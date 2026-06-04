"""
bypass.py — Direct LLM compliance assessment for EU AI Act Article 10.

Provides an alternative to the full GraphRAG pipeline: sends the model card
to the LLM in a single prompt and asks it to judge each Article 10 obligation
as present (true) or absent (false).  The result is an RDF graph in the same
gai-act format as the GraphRAG pipeline, so the same SHACL shapes apply.

Use with:  uv run python run.py --input model_card.md --model qwen2.5:7b --bypass

This is the "judge" baseline for thesis comparison:
  - GraphRAG pipeline: chunk → KG extraction → kg_to_rdf → SHACL
  - Bypass pipeline:   full text → single LLM prompt → judgments_to_rdf → SHACL

Key difference: the bypass reads the whole document in one context window, so
it can reason across sections.  The GraphRAG pipeline reads one chunk at a time
and relies on the extraction schema to guide what nodes are created.
"""

from __future__ import annotations

import json
import logging
import re

import json_repair
from neo4j_graphrag.llm.ollama_llm import OllamaLLM
from neo4j_graphrag.types import LLMMessage
from rdflib import BNode, Graph, Literal, Namespace
from rdflib.namespace import RDF

log = logging.getLogger(__name__)

GAI  = Namespace("https://gelsi.com/gai-act#")
EX   = Namespace("https://gelsi.com/system#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCT  = Namespace("http://purl.org/dc/terms/")


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
/no_think
You are an EU AI Act Article 10 compliance assessor.

Read the model card below and judge each of the Article 10 obligations for \
each dataset type (training, validation, testing).

Rules:
- Answer true ONLY when substantive documentation is present in the text.
- A statement that something was NOT done, was not completed, or is absent \
counts as false.
- If no testing dataset is mentioned at all, set has_testing_dataset to false \
and all testing obligations to false.

Return ONLY valid JSON — no prose before or after. Use this exact structure:

{
  "has_training_dataset": true,
  "has_validation_dataset": true,
  "has_testing_dataset": false,
  "training": {
    "design_choices": true,
    "provenance": true,
    "preprocessing": true,
    "assumptions": true,
    "suitability": true,
    "bias_examination": false,
    "bias_mitigation": false,
    "data_gaps": false,
    "relevance": true,
    "representativeness": false,
    "statistical_props": true,
    "quality_metrics": true,
    "contextual_characteristics": true
  },
  "validation": { "<same 13 keys as training>" },
  "testing":    { "<same 13 keys as training>" }
}

Obligation definitions:
  design_choices             Art. 10(2)(a) — why and how datasets were collected or split
  provenance                 Art. 10(2)(b) — data origin, sources, collection method, consent
  preprocessing              Art. 10(2)(c) — data cleaning, filtering, annotation, normalisation
  assumptions                Art. 10(2)(d) — what the data represents and its stated limitations
  suitability                Art. 10(2)(e) — fitness for intended purpose, size and coverage
  bias_examination           Art. 10(2)(f) — bias audit, fairness analysis, protected attributes examined
  bias_mitigation            Art. 10(2)(g) — debiasing measures or documented decision not to apply them
  data_gaps                  Art. 10(2)(h) — known gaps, missing subgroups, acknowledged shortcomings
  relevance                  Art. 10(3)    — data is relevant to the intended task
  representativeness         Art. 10(3)    — demographic or subgroup coverage, population representation
  statistical_props          Art. 10(3)    — class distributions, dataset sizes, label prevalence
  quality_metrics            Art. 10(3)    — accuracy, error rates, annotation quality, completeness
  contextual_characteristics Art. 10(4)    — deployment geography, domain, equipment or clinical context
"""

_OBLIGATION_KEYS = [
    "design_choices", "provenance", "preprocessing", "assumptions",
    "suitability", "bias_examination", "bias_mitigation", "data_gaps",
    "relevance", "representativeness", "statistical_props",
    "quality_metrics", "contextual_characteristics",
]

_PREDICATE_MAP = {
    "design_choices":            "hasDesignChoicesDoc",
    "provenance":                "hasProvenanceDoc",
    "preprocessing":             "hasPreprocessingDoc",
    "assumptions":               "hasAssumptionsDoc",
    "suitability":               "hasSuitabilityDoc",
    "bias_examination":          "hasBiasExaminationDoc",
    "bias_mitigation":           "hasBiasMitigationDoc",
    "data_gaps":                 "hasDataGapDoc",
    "relevance":                 "hasRelevanceDoc",
    "representativeness":        "hasRepresentativenessDoc",
    "statistical_props":         "hasStatisticalPropsDoc",
    "quality_metrics":           "hasQualityMetricsDoc",
    "contextual_characteristics":"hasContextualCharacteristicsDoc",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _parse_judgment(raw: str, label: str) -> dict:
    """Parse LLM output into a judgment dict, handling fences, lists, junk."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)
    # Extract first {...} block if model added prose around it
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if m:
        raw = m.group(0)
    repaired = json_repair.repair_json(raw)
    parsed = json.loads(repaired) if repaired else {}
    # Sometimes models return [ {...} ] — unwrap
    if isinstance(parsed, list):
        parsed = next((x for x in parsed if isinstance(x, dict)), {})
    if not isinstance(parsed, dict):
        raise ValueError(f"{label} returned non-dict JSON: {type(parsed).__name__}; raw: {raw[:300]}")
    return parsed


def _fill_defaults(judgments: dict) -> dict:
    for ds in ("training", "validation", "testing"):
        v = judgments.get(ds)
        if not isinstance(v, dict):
            v = {}
        for key in _OBLIGATION_KEYS:
            v.setdefault(key, False)
        judgments[ds] = v
    for key in ("has_training_dataset", "has_validation_dataset", "has_testing_dataset"):
        judgments.setdefault(key, False)
    return judgments


async def _invoke_with_retry(messages, llm: OllamaLLM, label: str, retries: int = 1) -> dict:
    last_raw = ""
    for attempt in range(retries + 1):
        result = await llm.ainvoke(messages)
        last_raw = result.content
        try:
            return _parse_judgment(last_raw, label)
        except (json.JSONDecodeError, ValueError) as e:
            log.warning("%s parse failed (attempt %d/%d): %s", label, attempt + 1, retries + 1, e)
            if attempt == retries:
                raise ValueError(
                    f"{label} returned unparseable JSON after {retries + 1} attempts: {e}\n"
                    f"Raw: {last_raw[:500]}"
                ) from e
            # Retry with a reminder appended
            messages = messages + [
                LLMMessage(role="user", content="Your previous reply was not valid JSON. Reply with ONLY the JSON object, no prose, no markdown fences."),
            ]
    raise RuntimeError("unreachable")


async def bypass_judge(text: str, llm: OllamaLLM) -> dict:
    """
    Send the full document to the LLM and return a structured compliance dict.

    Returns a dict with keys:
      has_training_dataset, has_validation_dataset, has_testing_dataset  (bool)
      training, validation, testing  (dict of obligation_key → bool)
    """
    messages = [
        LLMMessage(role="system", content=_SYSTEM_PROMPT),
        LLMMessage(role="user", content=f"Model card:\n\n{text}"),
    ]
    log.info("Bypass: sending document to LLM (%d chars)", len(text))
    judgments = await _invoke_with_retry(messages, llm, "Bypass judge")
    judgments = _fill_defaults(judgments)
    log.info(
        "Bypass judgment — training: %s  validation: %s  testing: %s",
        judgments["has_training_dataset"],
        judgments["has_validation_dataset"],
        judgments["has_testing_dataset"],
    )
    return judgments


def judgments_to_rdf(judgments: dict) -> Graph:
    """Build a gai-act RDF graph from bypass-mode boolean judgments."""
    g = Graph()
    g.bind("gai-act", GAI)
    g.bind("ex",      EX)
    g.bind("dcat",    DCAT)
    g.bind("dct",     DCT)

    system_node = EX.TargetSystem
    g.add((system_node, RDF.type, GAI.HighRiskAISystem))

    dataset_config = {
        "training":   (EX.TrainingDataset,   GAI.hasTrainingDataset,   "Training Dataset"),
        "validation": (EX.ValidationDataset, GAI.hasValidationDataset, "Validation Dataset"),
        "testing":    (EX.TestingDataset,    GAI.hasTestingDataset,    "Testing Dataset"),
    }

    n_datasets = n_docs = 0
    for ds_key, (ds_rdf_node, sys_pred, title) in dataset_config.items():
        if not judgments.get(f"has_{ds_key}_dataset", False):
            continue

        g.add((system_node, sys_pred, ds_rdf_node))
        g.add((ds_rdf_node, RDF.type, DCAT.Dataset))
        g.add((ds_rdf_node, DCT.title, Literal(title)))
        n_datasets += 1

        ds_judgments = judgments.get(ds_key, {})
        for obligation, pred in _PREDICATE_MAP.items():
            if ds_judgments.get(obligation, False):
                doc_node = BNode()
                g.add((ds_rdf_node, GAI[pred], doc_node))
                g.add((doc_node, RDF.type, GAI.DocumentationNode))
                n_docs += 1

    log.info("RDF built from bypass: %d dataset(s), %d documentation node(s)", n_datasets, n_docs)
    return g
