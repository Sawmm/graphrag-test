"""
l2_eval.py — Layer-2 (shape correctness) evaluation.

Builds gold-standard RDF from labels_sam.csv, runs pySHACL, and measures
whether the SHACL shapes correctly fire violations for absent obligations and
stay silent for present ones.

Usage:
    uv run python l2_eval.py
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, XSD
from pyshacl import validate as shacl_validate

REPO_ROOT = Path(__file__).parent
SHAPES    = REPO_ROOT / "shapes" / "article10-shapes.ttl"
LABELS    = REPO_ROOT / "gold" / "labels_sam.csv"

GAI  = Namespace("https://gelsi.com/gai-act#")
EX   = Namespace("https://gelsi.com/system#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCT  = Namespace("http://purl.org/dc/terms/")

PREDICATE_MAP = {
    "design_choices":             "hasDesignChoicesDoc",
    "provenance":                 "hasProvenanceDoc",
    "preprocessing":              "hasPreprocessingDoc",
    "assumptions":                "hasAssumptionsDoc",
    "suitability":                "hasSuitabilityDoc",
    "bias_examination":           "hasBiasExaminationDoc",
    "bias_mitigation":            "hasBiasMitigationDoc",
    "data_gap":                   "hasDataGapDoc",
    "relevance":                  "hasRelevanceDoc",
    "representativeness":         "hasRepresentativenessDoc",
    "statistical_props":          "hasStatisticalPropsDoc",
    "quality_metrics":            "hasQualityMetricsDoc",
    "contextual_characteristics": "hasContextualCharacteristicsDoc",
}

DATASET_CONFIG = {
    "training":   (EX.TrainingDataset,   GAI.hasTrainingDataset,   "Training Dataset"),
    "validation": (EX.ValidationDataset, GAI.hasValidationDataset, "Validation Dataset"),
    "testing":    (EX.TestingDataset,    GAI.hasTestingDataset,    "Testing Dataset"),
}

# Map resultPath URI fragment → obligation key
PATH_TO_OBLIGATION = {v: k for k, v in PREDICATE_MAP.items()}

# Map focusNode URI fragment → section key
FOCUS_TO_SECTION = {
    "TrainingDataset":   "training",
    "ValidationDataset": "validation",
    "TestingDataset":    "testing",
}


def load_labels() -> dict[str, dict[str, dict[str, bool]]]:
    """Return labels[doc][section][obligation] = bool(present)."""
    labels: dict = defaultdict(lambda: defaultdict(dict))
    with open(LABELS, newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            doc = row["document"]
            sec = row["dataset_section"]
            ob  = row["obligation"]
            labels[doc][sec][ob] = bool(int(row["present"]))
    return {d: dict(s) for d, s in labels.items()}


def build_gold_rdf(doc_labels: dict[str, dict[str, bool]]) -> Graph:
    """Build a gai-act RDF graph from per-section obligation labels."""
    g = Graph()
    g.bind("gai-act", GAI)
    g.bind("ex", EX)
    g.bind("dcat", DCAT)
    g.bind("dct", DCT)

    system = EX.TargetSystem
    g.add((system, RDF.type, GAI.HighRiskAISystem))
    g.add((system, GAI.usesTrainingTechniques,        Literal(True, datatype=XSD.boolean)))
    g.add((system, GAI.processesSensitiveDataForBias, Literal(False, datatype=XSD.boolean)))

    for sec, (ds_node, sys_pred, title) in DATASET_CONFIG.items():
        sec_labels = doc_labels.get(sec, {})
        # Always add all three dataset sections (all docs are Annex-IV normalised)
        g.add((system, sys_pred, ds_node))
        g.add((ds_node, RDF.type, DCAT.Dataset))
        g.add((ds_node, DCT.title, Literal(title)))
        for ob, pred in PREDICATE_MAP.items():
            if sec_labels.get(ob, False):
                bn = BNode()
                g.add((ds_node, GAI[pred], bn))
                g.add((bn, RDF.type, GAI.DocumentationNode))
    return g


def parse_violations(report_graph: Graph) -> dict[str, dict[str, bool]]:
    """
    Return predicted[section][obligation] = True (violation fired = absent).
    Only parse leaf per-obligation violations (focusNode is a dataset node).
    """
    SH = Namespace("http://www.w3.org/ns/shacl#")
    violations = list(report_graph.subjects(RDF.type, SH.ValidationResult))

    # predicted[section][obligation] = True means SHACL says "absent"
    absent: dict[str, dict[str, bool]] = defaultdict(lambda: defaultdict(bool))

    for v in violations:
        focus = str(report_graph.value(v, SH.focusNode) or "")
        path  = str(report_graph.value(v, SH.resultPath) or "")

        # Extract section from focusNode URI fragment
        section = None
        for frag, sec in FOCUS_TO_SECTION.items():
            if frag in focus:
                section = sec
                break
        if section is None:
            continue  # family-level or system-level shape — skip

        # Extract obligation from resultPath URI fragment
        obligation = None
        for frag, ob in PATH_TO_OBLIGATION.items():
            if frag in path:
                obligation = ob
                break
        if obligation is None:
            continue  # not a per-obligation path

        absent[section][obligation] = True

    return absent


def evaluate() -> None:
    labels = load_labels()
    documents = sorted(labels)

    tp = tn = fp = fn = 0
    per_ob: dict[str, dict[str, int]] = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0, "tn": 0})

    for doc in documents:
        doc_labels = labels[doc]
        g = build_gold_rdf(doc_labels)
        conforms, report_graph, _ = shacl_validate(
            g, shacl_graph=str(SHAPES), inference="none", abort_on_first=False
        )
        absent = parse_violations(report_graph)

        for sec in ("training", "validation", "testing"):
            for ob in PREDICATE_MAP:
                gold_present  = doc_labels.get(sec, {}).get(ob, False)
                shacl_present = not absent.get(sec, {}).get(ob, False)

                tp += int(gold_present and shacl_present)
                tn += int(not gold_present and not shacl_present)
                fp += int(not gold_present and shacl_present)
                fn += int(gold_present and not shacl_present)
                per_ob[ob]["tp"] += int(gold_present and shacl_present)
                per_ob[ob]["fp"] += int(not gold_present and shacl_present)
                per_ob[ob]["fn"] += int(gold_present and not shacl_present)
                per_ob[ob]["tn"] += int(not gold_present and not shacl_present)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall    = tp / (tp + fn) if (tp + fn) else 0.0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    accuracy  = (tp + tn) / (tp + tn + fp + fn)

    print("=== L2 Shape Correctness (gold RDF → pySHACL) ===")
    print(f"Documents: {len(documents)}")
    print(f"TP={tp}  FP={fp}  FN={fn}  TN={tn}")
    print(f"Precision : {precision:.3f}")
    print(f"Recall    : {recall:.3f}")
    print(f"F1        : {f1:.3f}")
    print(f"Accuracy  : {accuracy:.3f}")
    print()
    print("Per-obligation (sorted by FP+FN):")
    rows = []
    for ob, c in per_ob.items():
        p = c["tp"] / (c["tp"] + c["fp"]) if (c["tp"] + c["fp"]) else 0.0
        r = c["tp"] / (c["tp"] + c["fn"]) if (c["tp"] + c["fn"]) else 0.0
        f = 2*p*r/(p+r) if (p+r) else 0.0
        rows.append((ob, c["tp"], c["fp"], c["fn"], c["tn"], round(p,3), round(r,3), round(f,3)))
    rows.sort(key=lambda x: -(x[2]+x[3]))
    print(f"{'Obligation':<32} {'TP':>4} {'FP':>4} {'FN':>4} {'TN':>4}  {'P':>5} {'R':>5} {'F1':>5}")
    print("-" * 72)
    for ob, tp_, fp_, fn_, tn_, p, r, f in rows:
        print(f"{ob:<32} {tp_:>4} {fp_:>4} {fn_:>4} {tn_:>4}  {p:>5.3f} {r:>5.3f} {f:>5.3f}")


if __name__ == "__main__":
    evaluate()
