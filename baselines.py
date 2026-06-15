"""
baselines.py — non-LLM-extraction baselines for Article 10 obligation detection.

Each baseline produces a dict mapping "{section}.{obligation}" → bool, then
serialises that dict to the same gai-act TTL format as run.py so the existing
analyse.py pipeline can score it without changes.

Baselines:
    keyword   — regex per obligation, scoped to each dataset section (working).
    embedding — Ollama embedding similarity (stub, see TODO).
    judge     — whole-document LLM yes/no judge (stub, see TODO).

Output filenames mirror run.py:
    outputs/{card_stem}__baseline-keyword.ttl
    outputs/{card_stem}__baseline-keyword__diagnostics.json

Usage:
    uv run python baselines.py --baseline keyword
    uv run python baselines.py --baseline keyword --input inputs/model_card_compliant.md
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import time
from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace
from rdflib.namespace import RDF


# ── Constants ────────────────────────────────────────────────────────────────

OBLIGATIONS: list[str] = [
    "design_choices", "provenance", "preprocessing", "assumptions",
    "suitability", "bias_examination", "bias_mitigation", "data_gap",
    "relevance", "representativeness", "statistical_props",
    "quality_metrics", "contextual_characteristics",
]

SECTIONS: list[str] = ["training", "validation", "testing"]

# Map obligation key → gai-act predicate (mirrors run.py:_OBLIGATION_NODES)
OBLIGATION_PREDICATES: dict[str, str] = {
    "design_choices":              "hasDesignChoicesDoc",
    "provenance":                  "hasProvenanceDoc",
    "preprocessing":               "hasPreprocessingDoc",
    "assumptions":                 "hasAssumptionsDoc",
    "suitability":                 "hasSuitabilityDoc",
    "bias_examination":            "hasBiasExaminationDoc",
    "bias_mitigation":             "hasBiasMitigationDoc",
    "data_gap":                    "hasDataGapDoc",
    "relevance":                   "hasRelevanceDoc",
    "representativeness":          "hasRepresentativenessDoc",
    "statistical_props":           "hasStatisticalPropsDoc",
    "quality_metrics":             "hasQualityMetricsDoc",
    "contextual_characteristics":  "hasContextualCharacteristicsDoc",
}

GAI  = Namespace("https://gelsi.com/gai-act#")
EX   = Namespace("https://gelsi.com/system#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCT  = Namespace("http://purl.org/dc/terms/")


# ── Section extractor ────────────────────────────────────────────────────────
#
# Cards follow `## Section N — <DatasetType>` (e.g. "## Section 2 — Training
# Dataset"). The regex is permissive: it matches "Training", "Validation",
# "Testing" anywhere in a level-2 heading, then captures everything up to
# the next level-2 heading.
# ----------------------------------------------------------------------------

_SECTION_KEYWORDS = {
    "training":   r"training",
    "validation": r"validation",
    "testing":    r"testing|test\b",
}


def section_text(text: str, section: str) -> str:
    """Return the text under the level-2 heading for the given dataset type."""
    pattern = re.compile(
        rf"(?im)^##\s+[^\n]*\b({_SECTION_KEYWORDS[section]})\b[^\n]*$",
    )
    m = pattern.search(text)
    if not m:
        return ""
    start = m.end()
    rest  = text[start:]
    # Stop at the next level-2 heading
    nxt   = re.search(r"(?m)^##\s+[^#]", rest)
    end   = nxt.start() if nxt else len(rest)
    return rest[:end]


# ── Baseline 1: keyword regex ────────────────────────────────────────────────
#
# Each obligation has a list of regex patterns. If any pattern matches inside
# the section text, the obligation is reported as detected.
# ----------------------------------------------------------------------------

KEYWORD_PATTERNS: dict[str, list[str]] = {
    "design_choices":             [r"design\s+choice", r"sampling\s+strateg", r"split\b", r"data\s+selection"],
    "provenance":                 [r"provenan", r"collected\s+from", r"source\s*:", r"IRB", r"consent", r"data.*collection"],
    "preprocessing":              [r"preprocess", r"cleaning", r"normali[sz]", r"tokeni[sz]", r"annotation\s+pipeline"],
    "assumptions":                [r"\bassum\w+"],
    "suitability":                [r"suitabilit", r"\bsufficient\b", r"power\s+analysis", r"sample\s+size\s+(was|is)"],
    "bias_examination":           [r"bias\s+(audit|examin|analys|assess)", r"fairness\s+(audit|analys)", r"protected\s+attribute"],
    "bias_mitigation":            [r"\bmitigat\w+", r"debias", r"oversampl", r"reweight", r"importance\s+weight"],
    "data_gap":                   [r"\bgap\w*\b", r"missing\s+subgroup", r"underrepresent", r"shortcoming"],
    "relevance":                  [r"\brelevan\w+"],
    "representativeness":         [r"representativ", r"stratif", r"demographic\s+coverage"],
    "statistical_props":          [r"distribution", r"class\s+(balance|imbalance|prevalen)", r"\bvariance\b"],
    "quality_metrics":            [r"quality\s+(metric|check|review)", r"completeness", r"error\s+rate", r"annotation\s+error"],
    "contextual_characteristics": [r"context", r"deployment\s+(environment|setting)", r"clinical\s+(setting|workflow)", r"geograph"],
}


def baseline_keyword(text: str) -> dict[str, bool]:
    """Detect obligations by regex match within each dataset section."""
    result: dict[str, bool] = {}
    for sec in SECTIONS:
        sec_text = section_text(text, sec)
        for ob in OBLIGATIONS:
            patterns = KEYWORD_PATTERNS[ob]
            present  = bool(sec_text) and any(
                re.search(p, sec_text, re.I) for p in patterns
            )
            result[f"{sec}.{ob}"] = present
    return result


# ── Baseline 2: embedding similarity ─────────────────────────────────────────
# TODO: embed each obligation description (from EXTRACTION_SCHEMA in run.py)
#       and each chunk under a dataset section. Detect obligation if cosine
#       similarity ≥ threshold. Sweep threshold on a held-out card set.
# ----------------------------------------------------------------------------

def baseline_embedding(text: str, *, embed_model: str = "nomic-embed-text",
                       ollama_url: str = "http://localhost:11434",
                       threshold: float = 0.6) -> dict[str, bool]:
    raise NotImplementedError(
        "Embedding baseline not implemented yet. See module docstring for plan."
    )


# ── Baseline 3: whole-document LLM judge ─────────────────────────────────────
# TODO: single prompt: "For dataset section S, is obligation O documented?
#       Return JSON {section.obligation: bool}." Run via OllamaLLM with
#       MODEL_OPTIONS (temp=0, seed=42).
# ----------------------------------------------------------------------------

def baseline_judge(text: str, *, model: str = "qwen2.5:14b",
                   ollama_url: str = "http://localhost:11434") -> dict[str, bool]:
    raise NotImplementedError(
        "LLM-judge baseline not implemented yet. See module docstring for plan."
    )


# ── Dict-of-bools → gai-act TTL ──────────────────────────────────────────────
#
# Mirrors run.py:kg_to_rdf output so the resulting TTL can be scored by
# analyse.py and validated by the same SHACL shapes file as the main pipeline.
# Only emits a dataset node if at least one obligation in that section is True.
# ----------------------------------------------------------------------------

_DATASET_CONFIG = {
    "training":   (EX.TrainingDataset,   GAI.hasTrainingDataset,   "Training Dataset"),
    "validation": (EX.ValidationDataset, GAI.hasValidationDataset, "Validation Dataset"),
    "testing":    (EX.TestingDataset,    GAI.hasTestingDataset,    "Testing Dataset"),
}


def bools_to_rdf(bools: dict[str, bool]) -> Graph:
    g = Graph()
    g.bind("gai-act", GAI)
    g.bind("ex",      EX)
    g.bind("dcat",    DCAT)
    g.bind("dct",     DCT)

    system_node = EX.TargetSystem
    g.add((system_node, RDF.type, GAI.HighRiskAISystem))

    for sec, (ds_node, sys_pred, title) in _DATASET_CONFIG.items():
        has_any = any(bools.get(f"{sec}.{ob}", False) for ob in OBLIGATIONS)
        if not has_any:
            continue
        g.add((system_node, sys_pred, ds_node))
        g.add((ds_node, RDF.type, DCAT.Dataset))
        g.add((ds_node, DCT.title, Literal(title)))
        for ob in OBLIGATIONS:
            if bools.get(f"{sec}.{ob}", False):
                doc = BNode()
                g.add((ds_node, GAI[OBLIGATION_PREDICATES[ob]], doc))
                g.add((doc, RDF.type, GAI.DocumentationNode))
    return g


# ── Runner ───────────────────────────────────────────────────────────────────

_BASELINES: dict[str, callable] = {
    "keyword":   baseline_keyword,
    "embedding": baseline_embedding,
    "judge":     baseline_judge,
}

_REPO        = Path(__file__).parent
_INPUTS_DIR  = _REPO / "inputs" / "normalized"
_OUTPUTS_DIR = _REPO / "outputs"


def _read(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader
        return "\n".join(p.extract_text() or "" for p in PdfReader(str(path)).pages)
    return path.read_text(encoding="utf-8")


def run_one(input_path: Path, baseline_name: str) -> dict:
    fn   = _BASELINES[baseline_name]
    text = _read(input_path)

    t0    = time.perf_counter()
    bools = fn(text)
    g     = bools_to_rdf(bools)
    dur   = round(time.perf_counter() - t0, 4)

    slug = f"baseline-{baseline_name}"
    ttl_path  = _OUTPUTS_DIR / f"{input_path.stem}__{slug}.ttl"
    diag_path = _OUTPUTS_DIR / f"{input_path.stem}__{slug}__diagnostics.json"

    _OUTPUTS_DIR.mkdir(exist_ok=True)
    ttl_path.write_text(g.serialize(format="turtle"), encoding="utf-8")
    diagnostics = {
        "document":         input_path.stem,
        "model":            slug,
        "baseline":         baseline_name,
        "timestamp":        datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_duration_s": dur,
        "detected":         sum(bools.values()),
        "possible":         len(bools),
    }
    diag_path.write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    return diagnostics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--baseline", choices=list(_BASELINES), default="keyword")
    parser.add_argument("--input", type=Path, default=None,
                        help="Single input file. If omitted, runs on every file in inputs/normalized/.")
    args = parser.parse_args()

    targets = (
        [args.input]
        if args.input
        else sorted(p for p in _INPUTS_DIR.iterdir()
                    if p.suffix.lower() in {".md", ".pdf"})
    )

    print(f"Running baseline={args.baseline} on {len(targets)} card(s)")
    print(f"{'Document':50s}  {'Detected':>8s}  {'Time(s)':>8s}")
    print("-" * 72)
    for path in targets:
        d = run_one(path, args.baseline)
        print(f"{d['document']:50s}  {d['detected']:3d}/{d['possible']:<4d}  {d['total_duration_s']:8.3f}")


if __name__ == "__main__":
    main()
