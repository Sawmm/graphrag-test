"""
run.py — EU AI Act Article 10 compliance checker using neo4j-graphrag + SHACL.

This script checks whether an AI system's documentation (e.g. a model card)
complies with EU AI Act Article 10 data governance requirements.

Pipeline overview
-----------------
Step 1 — Document ingestion
    Read a PDF or Markdown file and split it into overlapping text chunks.

Step 2 — Knowledge graph extraction (compliance-aware schema)
    Use neo4j-graphrag's LLMEntityRelationExtractor with a constrained
    schema where each Article 10 obligation has its own node type
    (DesignChoicesDoc, ProvenanceDoc, ...). The LLM creates an obligation
    node whenever it finds the matching documentation in a chunk.

Step 3 — Schema pruning
    Run GraphPruning to strip any off-schema labels the LLM hallucinated
    (small models often ignore additional_node_types=False). Without this
    step, off-schema nodes survive into the cache and silently break the
    RDF mapping in Step 5.

Step 4 — Persistence
    Cache the pruned graph as JSON next to the input so subsequent runs
    skip the LLM entirely. Also write to Neo4j for browser exploration.

Step 5 — RDF graph construction
    Deterministically map the pruned KG to gai-act RDF. Each obligation
    node in the KG produces one DocumentationNode triple — the
    "documentation proxy principle": SHACL checks whether documentation
    exists, not whether the content is adequate.

Step 6 — SHACL validation
    Validate the RDF graph against the Article 10 SHACL shapes. Each
    missing DocumentationNode fires a violation. Print the results.

Scope
-----
This pipeline validates Article 10 SHACL families 1–4 only:
    §10(1) Dataset existence
    §10(2) Data governance documentation
    §10(3) Dataset quality documentation
    §10(4) Contextual characteristics documentation

Families 5 (§10(5) sensitive-data processing) and 6 (§10(6) non-training
systems) are out of scope. Their SHACL shapes are conditional on the
processesSensitiveDataForBias / usesTrainingTechniques triples, which
this pipeline does not emit. Adding them would require either extending
the extraction schema with declaration nodes or a separate boolean-judge
LLM call. See README / thesis for justification.

Usage
-----
    # Basic run (Neo4j + Ollama must be running)
    uv run python run.py --input model_card.md --model qwen2.5:7b

    # Re-extract from scratch (ignore cached graph)
    uv run python run.py --input model_card.md --model qwen2.5:7b --force

    # Custom shapes file
    uv run python run.py --input model_card.md --model qwen2.5:7b \\
        --shapes /path/to/article10-shapes.ttl

    # Custom Neo4j connection
    uv run python run.py --input model_card.md --model qwen2.5:7b \\
        --neo4j-uri bolt://localhost:7687 --neo4j-user neo4j --neo4j-password secret

Dependencies
------------
    uv add "neo4j-graphrag[ollama]" ollama neo4j pyshacl rdflib pypdf

External services required
--------------------------
    - Ollama running at http://localhost:11434 with your chosen model pulled
    - Neo4j running at bolt://localhost:7687 with APOC plugin enabled
      (start with Docker: see README or use --neo4j-* flags for remote)
"""

from __future__ import annotations

import argparse
import asyncio
import datetime
import json
import logging
import textwrap
import time
from collections import defaultdict
from pathlib import Path
import re

from neo4j import GraphDatabase
from neo4j_graphrag.experimental.components.entity_relation_extractor import LLMEntityRelationExtractor
from neo4j_graphrag.experimental.components.graph_pruning import GraphPruning
from neo4j_graphrag.experimental.components.kg_writer import Neo4jWriter
from neo4j_graphrag.experimental.components.schema import GraphSchema
from neo4j_graphrag.experimental.components.text_splitters.fixed_size_splitter import FixedSizeSplitter
from neo4j_graphrag.experimental.components.types import TextChunk, TextChunks
from neo4j_graphrag.llm.ollama_llm import OllamaLLM
from pyshacl import validate as shacl_validate
from rdflib import BNode, Graph, Literal, Namespace
from rdflib.namespace import RDF

from bypass import bypass_judge, judgments_to_rdf
from zeroshot import zeroshot_judge

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Model options — edit these to tune LLM behaviour
# See https://github.com/ollama/ollama/blob/main/docs/modelfile.md#valid-parameters-and-values
# ---------------------------------------------------------------------------

MODEL_OPTIONS: dict = {
    "options": {"temperature": 0, "num_ctx": 32768},
}

# Per-model overrides for models that crash with large num_ctx.
# Gemma 3n / Gemma 4 hits a llama.cpp GGML_SCHED_MAX_SPLIT_INPUTS assert at 32k.
MODEL_OPTIONS_OVERRIDES: dict[str, dict] = {
    "gemma4:e4b":   {"options": {"temperature": 0, "num_ctx": 8192}},
    "gemma4:e2b":   {"options": {"temperature": 0, "num_ctx": 8192}},
    "gemma3n:e4b":  {"options": {"temperature": 0, "num_ctx": 8192}},
    "gemma3n:e2b":  {"options": {"temperature": 0, "num_ctx": 8192}},
}


def _model_options(model: str) -> dict:
    return MODEL_OPTIONS_OVERRIDES.get(model, MODEL_OPTIONS)


# ---------------------------------------------------------------------------
# RDF namespaces
#
# gai-act: custom ontology aligned to the EU AI Act (hosted at gelsi.com)
# ex:      instance namespace for the specific system being evaluated
# dcat:    W3C dataset vocabulary
# dct:     Dublin Core terms (used for dataset titles)
# ---------------------------------------------------------------------------

GAI  = Namespace("https://gelsi.com/gai-act#")
EX   = Namespace("https://gelsi.com/system#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCT  = Namespace("http://purl.org/dc/terms/")




# ---------------------------------------------------------------------------
# EU AI Act Article 10 extraction schema for neo4j-graphrag
#
# Each node type corresponds to one Article 10 obligation.  The LLM is asked
# to create a node of that type whenever it finds documentation satisfying
# the obligation, and to link it to the relevant dataset node.
#
# This means the extracted KG IS the compliance evidence — no separate judge
# call is needed.  kg_to_rdf() below maps these nodes directly to gai-act RDF
# triples, which SHACL then validates.
# ---------------------------------------------------------------------------

# Obligation node types: label → (relationship from dataset, gai-act predicate)
_OBLIGATION_NODES: dict[str, tuple[str, str]] = {
    "DesignChoicesDoc":             ("HAS_DESIGN_CHOICES_DOC",         "hasDesignChoicesDoc"),
    "ProvenanceDoc":                ("HAS_PROVENANCE_DOC",             "hasProvenanceDoc"),
    "PreprocessingDoc":             ("HAS_PREPROCESSING_DOC",          "hasPreprocessingDoc"),
    "AssumptionsDoc":               ("HAS_ASSUMPTIONS_DOC",            "hasAssumptionsDoc"),
    "SuitabilityDoc":               ("HAS_SUITABILITY_DOC",            "hasSuitabilityDoc"),
    "BiasExaminationDoc":           ("HAS_BIAS_EXAMINATION_DOC",       "hasBiasExaminationDoc"),
    "BiasMitigationDoc":            ("HAS_BIAS_MITIGATION_DOC",        "hasBiasMitigationDoc"),
    "DataGapDoc":                   ("HAS_DATA_GAP_DOC",               "hasDataGapDoc"),
    "RelevanceDoc":                 ("HAS_RELEVANCE_DOC",              "hasRelevanceDoc"),
    "RepresentativenessDoc":        ("HAS_REPRESENTATIVENESS_DOC",     "hasRepresentativenessDoc"),
    "StatisticalPropsDoc":          ("HAS_STATISTICAL_PROPS_DOC",      "hasStatisticalPropsDoc"),
    "QualityMetricsDoc":            ("HAS_QUALITY_METRICS_DOC",        "hasQualityMetricsDoc"),
    "ContextualCharacteristicsDoc": ("HAS_CONTEXTUAL_CHARACTERISTICS_DOC", "hasContextualCharacteristicsDoc"),
}

_NODE_PROPS = [{"name": "name", "type": "STRING"}]

EXTRACTION_SCHEMA = {
    "node_types": [
        {"label": "AISystem",          "description": "The AI system being documented",                                                               "properties": _NODE_PROPS},
        {"label": "TrainingDataset",   "description": "The dataset used to train the AI system",                                                      "properties": _NODE_PROPS},
        {"label": "ValidationDataset", "description": "The dataset used to tune or validate the AI system during development",                        "properties": _NODE_PROPS},
        {"label": "TestingDataset",    "description": "The held-out dataset used only for final evaluation",                                          "properties": _NODE_PROPS},
        # One node type per Article 10 obligation — create when the documentation is present
        {"label": "DesignChoicesDoc",             "description": "Documents why and how datasets were collected or split (Art. 10(2)(a))",            "properties": _NODE_PROPS},
        {"label": "ProvenanceDoc",                "description": "Documents data origin, sources, collection method, consent (Art. 10(2)(b))",        "properties": _NODE_PROPS},
        {"label": "PreprocessingDoc",             "description": "Documents data cleaning, filtering, annotation, normalisation (Art. 10(2)(c))",     "properties": _NODE_PROPS},
        {"label": "AssumptionsDoc",               "description": "Documents what the data represents and its stated limitations (Art. 10(2)(d))",     "properties": _NODE_PROPS},
        {"label": "SuitabilityDoc",               "description": "Documents fitness for intended purpose, size and coverage assessment (Art. 10(2)(e))", "properties": _NODE_PROPS},
        {"label": "BiasExaminationDoc",           "description": "Documents bias audit, fairness analysis, protected attributes examined (Art. 10(2)(f))", "properties": _NODE_PROPS},
        {"label": "BiasMitigationDoc",            "description": "Documents debiasing measures or a deliberate decision not to apply them (Art. 10(2)(g))", "properties": _NODE_PROPS},
        {"label": "DataGapDoc",                   "description": "Documents known gaps, missing subgroups, acknowledged shortcomings (Art. 10(2)(h))", "properties": _NODE_PROPS},
        {"label": "RelevanceDoc",                 "description": "Documents that data is relevant to the intended task or use case (Art. 10(3))",     "properties": _NODE_PROPS},
        {"label": "RepresentativenessDoc",        "description": "Documents demographic or subgroup coverage, population representation (Art. 10(3))", "properties": _NODE_PROPS},
        {"label": "StatisticalPropsDoc",          "description": "Documents class distributions, dataset sizes, label prevalence (Art. 10(3))",       "properties": _NODE_PROPS},
        {"label": "QualityMetricsDoc",            "description": "Documents accuracy, error rates, annotation quality, completeness (Art. 10(3))",    "properties": _NODE_PROPS},
        {"label": "ContextualCharacteristicsDoc", "description": "Documents deployment geography, domain, equipment or clinical context (Art. 10(4))", "properties": _NODE_PROPS},
    ],
    "relationship_types": [
        {"label": "HAS_TRAINING_DATASET",   "description": "AI system uses this as its training dataset"},
        {"label": "HAS_VALIDATION_DATASET", "description": "AI system uses this as its validation dataset"},
        {"label": "HAS_TESTING_DATASET",    "description": "AI system uses this as its testing dataset"},
        *[
            {"label": rel, "description": f"Dataset has this documentation node"}
            for rel, _ in _OBLIGATION_NODES.values()
        ],
    ],
    "patterns": [
        ("AISystem", "HAS_TRAINING_DATASET",   "TrainingDataset"),
        ("AISystem", "HAS_VALIDATION_DATASET", "ValidationDataset"),
        ("AISystem", "HAS_TESTING_DATASET",    "TestingDataset"),
        *[
            (ds, rel, label)
            for label, (rel, _) in _OBLIGATION_NODES.items()
            for ds in ("TrainingDataset", "ValidationDataset", "TestingDataset")
        ],
    ],
    "additional_node_types": False,
    "additional_relationship_types": False,
}


# ---------------------------------------------------------------------------
# Step 1 helpers: caching the extracted graph
#
# Extraction is the slowest step (one LLM call per chunk). We cache the
# result as a JSON file next to the input document so subsequent runs skip
# the LLM entirely and reload from disk.
#
# Cache filename: <input_stem>__<model_slug>__graph.json
# Use --force to delete the cache and re-extract from scratch.
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).parent


def _cache_path(input_path: Path, model: str, strip_headers: bool = False,
                cache_root: Path | None = None) -> Path:
    """Return the path of the JSON cache file for this input + model pair."""
    slug = model.replace(":", "-").replace("/", "_")[:30]
    suffix = "_stripped" if strip_headers else ""
    cache_dir = cache_root or (_REPO_ROOT / "cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{input_path.stem}__{slug}__graph{suffix}.json"


def _save_cache(path: Path, nodes: list, relationships: list) -> None:
    """Serialise extracted nodes and relationships to JSON."""

    def _serialise(obj):
        props = getattr(obj, "properties", {}) or {}
        return {
            "id":            getattr(obj, "id", None) or getattr(obj, "element_id", None),
            "label":         getattr(obj, "label", None),
            "labels":        getattr(obj, "labels", None),
            # Only keep JSON-safe property values; skip embeddings/vectors
            "properties":    {k: v for k, v in props.items()
                              if isinstance(v, (str, int, float, bool, type(None)))},
            "type":          getattr(obj, "type", None),
            "start_node_id": getattr(obj, "start_node_id", None),
            "end_node_id":   getattr(obj, "end_node_id", None),
        }

    payload = {
        "nodes":         [_serialise(n) for n in nodes],
        "relationships": [_serialise(r) for r in relationships],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    log.info("Graph cached to %s", path)


def _load_cache(path: Path) -> tuple[list, list]:
    """Load a previously cached graph from JSON."""

    data = json.loads(path.read_text(encoding="utf-8"))

    # Recreate lightweight objects that behave like the originals
    class _Node:
        def __init__(self, d): self.__dict__.update(d)

    class _Rel:
        def __init__(self, d): self.__dict__.update(d)

    nodes = [_Node(d) for d in data["nodes"]]
    rels  = [_Rel(d)  for d in data["relationships"]]
    log.info("Loaded cached graph: %d nodes, %d relationships", len(nodes), len(rels))
    return nodes, rels


# ---------------------------------------------------------------------------
# Markdown-aware splitter
#
# Compliance docs use ### headers per obligation (### Bias examination, ...).
# A pure character splitter cuts those sections in half, so the chunk holding
# "### Bias examination" may not contain the bias-examination evidence — the
# LLM then fails to emit a BiasExaminationDoc node.
#
# This splitter splits on heading lines (## or deeper) so each section is its
# own chunk. Oversize sections fall back to FixedSizeSplitter. Non-markdown
# input (e.g. PDF text) without ## headings degrades to plain FixedSizeSplitter
# behaviour.
# ---------------------------------------------------------------------------

# Split positions: BEFORE any `## ` (level-2) and any `### ` (level-3+).
# Used in two passes so we can keep level-2 context as a prefix on level-3 chunks.
_L2_SPLIT_RE = re.compile(r"(?m)^(?=## [^#])")
_L3_SPLIT_RE = re.compile(r"(?m)^(?=### )")


class MarkdownSectionSplitter:
    """Section-aware splitter that respects markdown heading boundaries.

    Each `### ` subsection becomes its own chunk, prefixed with the parent
    `## ` heading so the LLM can resolve which dataset (training/validation/
    testing) the subsection refers to. Sections that exceed max_chunk_size
    are subdivided with FixedSizeSplitter. Plain text without ## headings
    falls back to FixedSizeSplitter wholesale.
    """

    def __init__(
        self,
        max_chunk_size: int = 1500,
        chunk_overlap: int = 250,
        strip_headers: bool = False,
    ) -> None:
        self.max_chunk_size = max_chunk_size
        self.strip_headers = strip_headers
        self._fallback = FixedSizeSplitter(
            chunk_size=max_chunk_size,
            chunk_overlap=chunk_overlap,
        )

    @staticmethod
    def _strip_md_headers(text: str) -> str:
        # Turn "## Training Dataset" / "### Bias Examination" into plain text
        # so the LLM sees content without markdown heading cues.
        return re.sub(r"(?m)^#{1,6}\s+", "", text)

    async def run(self, text: str) -> TextChunks:
        level2 = [s for s in _L2_SPLIT_RE.split(text) if s.strip()]
        if not level2:
            result = await self._fallback.run(text)
            if self.strip_headers:
                result = TextChunks(chunks=[
                    TextChunk(text=self._strip_md_headers(c.text), index=c.index)
                    for c in result.chunks
                ])
            return result

        chunks: list[TextChunk] = []
        for section in level2:
            heading = section.split("\n", 1)[0] if section.startswith("## ") else ""
            sub_sections = _L3_SPLIT_RE.split(section)

            for i, sub in enumerate(sub_sections):
                sub = sub.strip()
                if not sub:
                    continue
                # Prepend the parent ## heading to every ### chunk so the
                # LLM knows which dataset context it belongs to.
                if i > 0 and heading and not sub.startswith(heading):
                    sub = f"{heading}\n\n{sub}"

                if self.strip_headers:
                    sub = self._strip_md_headers(sub)

                if len(sub) <= self.max_chunk_size:
                    chunks.append(TextChunk(text=sub, index=len(chunks)))
                else:
                    fb = await self._fallback.run(sub)
                    for sc in fb.chunks:
                        text_out = self._strip_md_headers(sc.text) if self.strip_headers else sc.text
                        chunks.append(TextChunk(text=text_out, index=len(chunks)))

        return TextChunks(chunks=chunks)


# ---------------------------------------------------------------------------
# Step 1: Extract knowledge graph from document, write to Neo4j
# ---------------------------------------------------------------------------

async def extract_and_store(
    text: str,
    input_path: Path,
    model: str,
    llm: OllamaLLM,
    driver,
    neo4j_database: str,
    force: bool = False,
    strip_headers: bool = False,
    cache_root: Path | None = None,
) -> tuple[list, list, dict]:
    """
    Split the document, extract a knowledge graph with the LLM, prune off-schema
    nodes, and write it to Neo4j. Returns (nodes, relationships, metrics).

    On subsequent runs the cached JSON is used instead of re-extracting,
    unless force=True is passed.
    """
    cache = _cache_path(input_path, model, strip_headers=strip_headers, cache_root=cache_root)

    if cache.exists() and not force:
        log.info("Cache hit — skipping extraction. Use --force to re-extract.")
        nodes, rels = _load_cache(cache)
        return nodes, rels, {"from_cache": True, "duration_s": 0.0}

    t0 = time.perf_counter()

    splitter = MarkdownSectionSplitter(
        max_chunk_size=1500,
        chunk_overlap=250,
        strip_headers=strip_headers,
    )

    # on_error="IGNORE" skips chunks where the LLM returns malformed output
    # rather than crashing the whole run.
    extractor = LLMEntityRelationExtractor(
        llm=llm,
        on_error="IGNORE",
        create_lexical_graph=True,  # also creates Chunk nodes with raw text
    )

    # Schema enforcement: extractor only passes the schema into the prompt.
    # GraphPruning is what actually filters labels not in node_types / patterns.
    # Without this step, small models emit off-schema labels that break the
    # KG→RDF mapping silently.
    pruner = GraphPruning()

    # driver is None when --no-neo4j is set (cluster runs). Neo4j is only used
    # for browser exploration; the KG cache, RDF and SHACL all work without it.
    writer = Neo4jWriter(driver=driver, neo4j_database=neo4j_database) if driver is not None else None

    chunks_result = await splitter.run(text=text)
    n_chunks = len(chunks_result.chunks)
    log.info("Split into %d chunks", n_chunks)

    graph_schema = GraphSchema.model_validate(EXTRACTION_SCHEMA)
    raw_graph    = await extractor.run(chunks=chunks_result, document_info=None, schema=graph_schema)
    log.info("Extracted %d nodes, %d relationships (raw)",
             len(raw_graph.nodes), len(raw_graph.relationships))

    pruning_result = await pruner.run(graph=raw_graph, schema=graph_schema)
    graph_result   = pruning_result.graph
    stats          = pruning_result.pruning_stats
    nodes          = graph_result.nodes
    relationships  = graph_result.relationships
    log.info("After pruning: %d nodes, %d relationships (pruned %d nodes, %d rels)",
             len(nodes), len(relationships),
             len(stats.pruned_nodes), len(stats.pruned_relationships))

    if writer is not None:
        await writer.run(graph=graph_result)
        log.info("Graph written to Neo4j")
    else:
        log.info("Skipping Neo4j write (--no-neo4j)")

    duration = round(time.perf_counter() - t0, 3)
    _save_cache(cache, nodes, relationships)
    metrics = {
        "from_cache":         False,
        "duration_s":         duration,
        "chunks":             n_chunks,
        "nodes_raw":          len(raw_graph.nodes),
        "relationships_raw":  len(raw_graph.relationships),
        "nodes":              len(nodes),
        "relationships":      len(relationships),
        "pruned_nodes":       len(stats.pruned_nodes),
        "pruned_relationships": len(stats.pruned_relationships),
    }
    return nodes, relationships, metrics


# ---------------------------------------------------------------------------
# Step 2: Map extracted KG directly to gai-act RDF (no judge needed)
#
# The extraction schema is compliance-aware: each obligation has its own node
# type. The LLM creates those nodes during extraction when it finds the
# relevant documentation in the source text.
#
# This function is fully deterministic — it reads the KG structure and emits
# the corresponding RDF triples. SHACL then validates the result.
# ---------------------------------------------------------------------------

def kg_to_rdf(nodes: list, relationships: list) -> Graph:
    """
    Convert the extracted KG to a gai-act RDF graph for SHACL validation.

    Mapping rules:
      AISystem node          → ex:TargetSystem  a gai-act:HighRiskAISystem
      TrainingDataset node   → ex:TrainingDataset   a dcat:Dataset
      ValidationDataset node → ex:ValidationDataset a dcat:Dataset
      TestingDataset node    → ex:TestingDataset    a dcat:Dataset
      Dataset HAS_X_DOC DocNode → dataset gai-act:hasXDoc _:bnode
    """

    def _label(node) -> str:
        lbl = getattr(node, "label", None) or getattr(node, "labels", "")
        return lbl if isinstance(lbl, str) else (list(lbl)[0] if lbl else "")

    def _id(node):
        return getattr(node, "id", None) or getattr(node, "element_id", None)

    # Outgoing relationship index: node_id -> [(rel_type, target_id)]
    rels_from: dict = defaultdict(list)
    for rel in relationships:
        start = getattr(rel, "start_node_id", None)
        end   = getattr(rel, "end_node_id", None)
        rtype = getattr(rel, "type", "")
        if start is not None and end is not None:
            rels_from[start].append((rtype, end))

    # Group nodes by label (skip Chunk nodes)
    by_label: dict[str, list] = defaultdict(list)
    for node in nodes:
        lbl = _label(node)
        if lbl and lbl != "Chunk":
            by_label[lbl].append(node)

    # Reverse map: KG relationship type → gai-act predicate name
    rel_to_predicate: dict[str, str] = {
        rel: pred for _, (rel, pred) in _OBLIGATION_NODES.items()
    }

    # Dataset KG label → (RDF node, system predicate, display title)
    dataset_config = {
        "TrainingDataset":   (EX.TrainingDataset,   GAI.hasTrainingDataset,   "Training Dataset"),
        "ValidationDataset": (EX.ValidationDataset, GAI.hasValidationDataset, "Validation Dataset"),
        "TestingDataset":    (EX.TestingDataset,    GAI.hasTestingDataset,    "Testing Dataset"),
    }

    g = Graph()
    g.bind("gai-act", GAI)
    g.bind("ex",      EX)
    g.bind("dcat",    DCAT)
    g.bind("dct",     DCT)

    system_node = EX.TargetSystem
    g.add((system_node, RDF.type, GAI.HighRiskAISystem))

    # Collect all doc types found across ALL dataset nodes (union approach).
    # Model cards often document things once for the whole system; a chunk
    # boundary mid-section can cause the LLM to attribute docs to TrainingDataset
    # even when the text is about testing.  If any dataset node has a doc type,
    # treat it as documented for the system as a whole.
    global_doc_rels: set[str] = set()
    for ds_label in dataset_config:
        for ds_node in by_label.get(ds_label, []):
            for rel_type, _ in rels_from.get(_id(ds_node), []):
                if rel_type in rel_to_predicate:
                    global_doc_rels.add(rel_type)

    n_datasets = n_docs = 0
    for ds_label, (ds_rdf_node, sys_pred, title) in dataset_config.items():
        if not by_label.get(ds_label):
            log.debug("No %s nodes found — SHACL will flag missing dataset", ds_label)
            continue

        g.add((system_node, sys_pred, ds_rdf_node))
        g.add((ds_rdf_node, RDF.type, DCAT.Dataset))
        g.add((ds_rdf_node, DCT.title, Literal(title)))
        n_datasets += 1

        # Emit dataset-specific docs, then fill in any globally-found ones
        emitted: set[str] = set()
        for ds_node in by_label[ds_label]:
            for rel_type, _ in rels_from.get(_id(ds_node), []):
                pred = rel_to_predicate.get(rel_type)
                if pred and rel_type not in emitted:
                    doc_node = BNode()
                    g.add((ds_rdf_node, GAI[pred], doc_node))
                    g.add((doc_node, RDF.type, GAI.DocumentationNode))
                    emitted.add(rel_type)
                    n_docs += 1

        for rel_type in global_doc_rels - emitted:
            pred = rel_to_predicate.get(rel_type)
            if pred:
                doc_node = BNode()
                g.add((ds_rdf_node, GAI[pred], doc_node))
                g.add((doc_node, RDF.type, GAI.DocumentationNode))
                n_docs += 1

    log.info("RDF built: %d dataset(s), %d documentation node(s)", n_datasets, n_docs)
    return g


# ---------------------------------------------------------------------------
# Step 5: SHACL validation and reporting
# ---------------------------------------------------------------------------

def validate_and_report(g: Graph, shapes_path: Path) -> bool:
    """
    Validate the RDF graph against the Article 10 SHACL shapes and print a
    human-readable report. Returns True if the system is compliant.
    """
    conforms, report_graph, _ = shacl_validate(
        g,
        shacl_graph=str(shapes_path),
        inference="none",
        abort_on_first=False,
    )

    SH = Namespace("http://www.w3.org/ns/shacl#")
    violations = list(report_graph.subjects(RDF.type, SH.ValidationResult))

    print()
    print("=" * 60)
    print("  EU AI Act Article 10 Compliance Report")
    print("=" * 60)
    print(f"  Result:     {'COMPLIANT ✓' if conforms else 'NON-COMPLIANT ✗'}")
    print(f"  Violations: {len(violations)}")
    print("=" * 60)

    if violations:
        print()
        for v in violations:
            message = report_graph.value(v, SH.resultMessage)
            print(f"  • {message or '(no message)'}")
    else:
        print()
        print("  No violations found.")

    print()
    return conforms


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

# Default shapes path: in-repo shapes/ dir, fall back to sibling thesis repo
DEFAULT_SHAPES_PATH = Path(__file__).parent / "shapes" / "article10-shapes.ttl"
if not DEFAULT_SHAPES_PATH.exists():
    DEFAULT_SHAPES_PATH = (
        Path(__file__).parent.parent
        / "thesis" / "shacl-modelling" / "ontologies" / "article10-shapes.ttl"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check EU AI Act Article 10 compliance using neo4j-graphrag + SHACL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              uv run python run.py --input model_card.md --model qwen2.5:7b
              uv run python run.py --input model_card.pdf --model llama3.2 --force
        """),
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        type=Path,
        help="Path to the document to check (PDF or Markdown/text)",
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Ollama model name, e.g. qwen2.5:7b or llama3.2",
    )
    parser.add_argument(
        "--ollama-url",
        default="http://localhost:11434",
        help="Ollama base URL (default: http://localhost:11434)",
    )
    parser.add_argument(
        "--neo4j-uri",
        default="bolt://localhost:7687",
        help="Neo4j Bolt URI (default: bolt://localhost:7687)",
    )
    parser.add_argument(
        "--neo4j-user",
        default="neo4j",
        help="Neo4j username (default: neo4j)",
    )
    parser.add_argument(
        "--neo4j-password",
        default="password",
        help="Neo4j password (default: password)",
    )
    parser.add_argument(
        "--neo4j-database",
        default="neo4j",
        help="Neo4j database name (default: neo4j)",
    )
    parser.add_argument(
        "--shapes",
        type=Path,
        default=DEFAULT_SHAPES_PATH,
        help=f"Path to article10-shapes.ttl (default: {DEFAULT_SHAPES_PATH})",
    )
    parser.add_argument(
        "--outputs-dir",
        type=Path,
        default=_REPO_ROOT / "outputs",
        help="Where to write TTL and diagnostics (default: outputs/)",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=_REPO_ROOT / "cache",
        help="Where to read/write KG cache JSON (default: cache/)",
    )
    parser.add_argument(
        "--bypass",
        action="store_true",
        help=(
            "Skip GraphRAG; send the full document to the LLM directly and ask it "
            "to judge each Article 10 obligation (no Neo4j required, much faster)"
        ),
    )
    parser.add_argument(
        "--zeroshot",
        action="store_true",
        help=(
            "Zero-shot baseline: minimal prompt with no obligation definitions. "
            "Tests whether the model inherently knows Article 10."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-extract the knowledge graph even if a cache file already exists (graphrag mode only)",
    )
    parser.add_argument(
        "--no-neo4j",
        action="store_true",
        help=(
            "Skip writing the KG to Neo4j (graphrag mode). The JSON cache, RDF "
            "and SHACL validation still run normally — Neo4j is only used for "
            "browser exploration. Use this on clusters with no Neo4j available."
        ),
    )
    parser.add_argument(
        "--judge",
        action="store_true",
        help=(
            "After GraphRAG extraction, replace kg_to_rdf with a bypass-style "
            "LLM judgment pass on the full document. KG still built (for "
            "visualisation/metrics) but final RDF comes from per-obligation "
            "boolean judgment, not raw KG presence. Mitigates KG extraction "
            "false positives where headings cause spurious doc nodes."
        ),
    )
    parser.add_argument(
        "--strip-headers",
        action="store_true",
        help=(
            "Strip markdown header markers (#, ##, ###) from chunk text before "
            "sending to the LLM. Tests whether GraphRAG's format sensitivity to "
            "headings causes false-positive documentation node extraction."
        ),
    )

    args = parser.parse_args()

    # Validate paths before doing any work
    if not args.input.exists():
        parser.error(f"Input file not found: {args.input}")
    if not args.shapes.exists():
        parser.error(
            f"SHACL shapes file not found: {args.shapes}\n"
            "Pass --shapes <path> to specify the location of article10-shapes.ttl"
        )

    # Read the input document
    if args.input.suffix.lower() == ".pdf":
        from pypdf import PdfReader
        text = "\n".join(
            page.extract_text() or "" for page in PdfReader(str(args.input)).pages
        )
    else:
        text = args.input.read_text(encoding="utf-8")

    llm = OllamaLLM(model_name=args.model, host=args.ollama_url, model_params=_model_options(args.model))

    outputs_dir = args.outputs_dir
    outputs_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace(":", "-").replace("/", "_")[:30]
    if args.zeroshot:
        mode_tag = "zeroshot"
    elif args.bypass:
        mode_tag = "bypass"
    else:
        mode_tag = "graphrag"
    if args.strip_headers and mode_tag == "graphrag":
        mode_tag = f"{mode_tag}_stripped"
    if args.judge and mode_tag == "graphrag":
        mode_tag = f"{mode_tag}_judge"

    run_start = time.perf_counter()

    if args.zeroshot:
        # ── Zero-shot mode: minimal prompt, no schema, no Neo4j ──────────
        t0 = time.perf_counter()
        judgments = asyncio.run(zeroshot_judge(text, llm))
        judge_duration = round(time.perf_counter() - t0, 3)

        t0 = time.perf_counter()
        rdf_graph = judgments_to_rdf(judgments)
        rdf_duration = round(time.perf_counter() - t0, 3)

        extraction_metrics: dict = {"mode": "zeroshot", "duration_s": judge_duration}

    elif args.bypass:
        # ── Bypass mode: one LLM call, no Neo4j ──────────────────────────
        t0 = time.perf_counter()
        judgments = asyncio.run(bypass_judge(text, llm))
        judge_duration = round(time.perf_counter() - t0, 3)

        t0 = time.perf_counter()
        rdf_graph = judgments_to_rdf(judgments)
        rdf_duration = round(time.perf_counter() - t0, 3)

        extraction_metrics: dict = {"mode": "bypass", "duration_s": judge_duration}

    else:
        # ── GraphRAG mode: chunk → KG → RDF ──────────────────────────────
        driver = None if args.no_neo4j else GraphDatabase.driver(
            args.neo4j_uri,
            auth=(args.neo4j_user, args.neo4j_password),
        )
        t0 = time.perf_counter()
        nodes, relationships, extraction_metrics = asyncio.run(
            extract_and_store(
                text=text,
                input_path=args.input,
                model=args.model,
                llm=llm,
                driver=driver,
                neo4j_database=args.neo4j_database,
                force=args.force,
                strip_headers=args.strip_headers,
                cache_root=args.cache_dir,
            )
        )
        if driver is not None:
            driver.close()
        extraction_metrics.setdefault("duration_s", round(time.perf_counter() - t0, 3))

        t0 = time.perf_counter()
        if args.judge:
            judgments = asyncio.run(bypass_judge(text, llm))
            rdf_graph = judgments_to_rdf(judgments)
        else:
            rdf_graph = kg_to_rdf(nodes, relationships)
        rdf_duration = round(time.perf_counter() - t0, 3)

    # ── Save Turtle output ────────────────────────────────────────────────
    turtle_path = outputs_dir / f"{args.input.stem}__{slug}__{mode_tag}.ttl"
    turtle_path.write_text(rdf_graph.serialize(format="turtle"), encoding="utf-8")
    log.info("RDF graph saved to %s", turtle_path)

    # ── SHACL validation ─────────────────────────────────────────────────
    t0 = time.perf_counter()
    validate_and_report(rdf_graph, args.shapes)
    shacl_duration = round(time.perf_counter() - t0, 3)

    total_duration = round(time.perf_counter() - run_start, 3)

    # ── Diagnostics ───────────────────────────────────────────────────────
    diagnostics = {
        "document":   args.input.stem,
        "model":      args.model,
        "mode":       mode_tag,
        "timestamp":  datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "steps": {
            "extraction": extraction_metrics,
            "rdf_build":  {"duration_s": rdf_duration},
            "shacl":      {"duration_s": shacl_duration},
        },
        "total_duration_s": total_duration,
    }
    diag_path = outputs_dir / f"{args.input.stem}__{slug}__{mode_tag}__diagnostics.json"
    diag_path.write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    log.info("Diagnostics saved to %s", diag_path)

    # ── Timing summary ────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("  Timing Summary")
    print("=" * 60)
    if args.bypass:
        print(f"  LLM judge        : {extraction_metrics['duration_s']:7.1f}s")
    else:
        cache_note = " (cached)" if extraction_metrics.get("from_cache") else ""
        print(f"  Extraction{cache_note:9s}: {extraction_metrics['duration_s']:7.1f}s")
    print(f"  RDF build        : {rdf_duration:7.3f}s")
    print(f"  SHACL validation : {shacl_duration:7.3f}s")
    print(f"  ─────────────────────────────")
    print(f"  Total            : {total_duration:7.1f}s")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
