"""
analyse.py — Thesis results analysis for the EU AI Act Article 10 compliance pipeline.

Compares knowledge graph quality and compliance detection across models and documents.
Produces console tables, CSV exports, and PDF plots in analysis/.

Usage:
    uv run python analyse.py
    uv run python analyse.py --shapes /path/to/article10-shapes.ttl
    uv run python analyse.py --output-dir results/
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF
from pyshacl import validate as shacl_validate

REPO_ROOT  = Path(__file__).parent
CACHE_DIR  = REPO_ROOT / "cache"
OUTPUT_DIR = REPO_ROOT / "outputs"

# ── Schema constants (keep in sync with run.py:EXTRACTION_SCHEMA) ────────────

SCHEMA_NODE_LABELS = {
    "AISystem", "TrainingDataset", "ValidationDataset", "TestingDataset",
    "DesignChoicesDoc", "ProvenanceDoc", "PreprocessingDoc", "AssumptionsDoc",
    "SuitabilityDoc", "BiasExaminationDoc", "BiasMitigationDoc", "DataGapDoc",
    "RelevanceDoc", "RepresentativenessDoc", "StatisticalPropsDoc",
    "QualityMetricsDoc", "ContextualCharacteristicsDoc",
}
STRUCTURAL_RELS    = {"FROM_CHUNK", "NEXT_CHUNK"}

DATASET_PROPS: dict[str, str] = {
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

DATASET_SECTIONS = {
    "training":   "https://gelsi.com/system#TrainingDataset",
    "validation": "https://gelsi.com/system#ValidationDataset",
    "testing":    "https://gelsi.com/system#TestingDataset",
}

GAI  = Namespace("https://gelsi.com/gai-act#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")

# ── Ground truth: expected SHACL compliance verdict per document stem ────────
GROUND_TRUTH: dict[str, bool] = {
    "model_card_compliant":      True,
    "model_card_compliant_copy": True,
    "model_card_noncompliant":   False,
    "model_card_compliant_one_out": False,
}

# ── Ground truth: per-obligation presence for precision/recall ───────────────
# Structure: doc → section → obligation_key → bool (True = should be present)
# Only populated for synthetic cards where ground truth is known exactly.
_ALL_TRUE = {k: True for k in [
    "design_choices", "provenance", "preprocessing", "assumptions",
    "suitability", "bias_examination", "bias_mitigation", "data_gap",
    "relevance", "representativeness", "statistical_props",
    "quality_metrics", "contextual_characteristics",
]}

OBLIGATION_GROUND_TRUTH: dict[str, dict[str, dict[str, bool]]] = {
    "model_card_compliant": {
        "training":   _ALL_TRUE.copy(),
        "validation": _ALL_TRUE.copy(),
        "testing":    _ALL_TRUE.copy(),
    },
    "model_card_compliant_one_out": {
        "training":   {**_ALL_TRUE, "statistical_props": False},
        "validation": _ALL_TRUE.copy(),
        "testing":    _ALL_TRUE.copy(),
    },
    "model_card_noncompliant": {
        "training": {**_ALL_TRUE,
            "bias_examination": False, "bias_mitigation": False,
            "data_gap": False, "representativeness": False,
        },
        "validation": {**_ALL_TRUE,
            "bias_examination": False, "bias_mitigation": False,
            "data_gap": False, "representativeness": False,
            "statistical_props": False, "quality_metrics": False,
        },
        "testing": {k: False for k in _ALL_TRUE},
    },
}


def _load_gold_csv() -> None:
    """Merge filled rows from gold/labels_*.csv into OBLIGATION_GROUND_TRUTH.

    Only rows with a 1/0 in 'present' are loaded. Real cards in the CSV win
    over hardcoded entries; synthetic cards stay hardcoded.
    """
    import csv
    gold_dir = Path(__file__).parent / "gold"
    if not gold_dir.exists():
        return
    for csv_path in sorted(gold_dir.glob("labels_*.csv")):
        if csv_path.name == "labels_template.csv":
            continue
        with csv_path.open(encoding="utf-8-sig") as f:
            first = f.readline()
            if not first.lower().startswith("sep="):
                f.seek(0)
            reader = csv.DictReader(f, delimiter=";" if ";" in first and "," not in first.split(";")[0] else ",")
            for row in reader:
                present = (row.get("present") or "").strip()
                if present not in ("0", "1"):
                    continue
                doc = row["document"].strip()
                sec = row["dataset_section"].strip()
                ob  = row["obligation"].strip()
                OBLIGATION_GROUND_TRUTH.setdefault(doc, {}).setdefault(sec, {})[ob] = (present == "1")


_load_gold_csv()

# ── Matplotlib style for LaTeX-compatible PDF output ────────────────────────

def _apply_thesis_style() -> None:
    """Configure matplotlib for thesis-quality PDF output."""
    plt.rcParams.update({
        "font.family":       "serif",
        "font.size":         10,
        "axes.titlesize":    11,
        "axes.labelsize":    10,
        "xtick.labelsize":   8,
        "ytick.labelsize":   8,
        "legend.fontsize":   9,
        "figure.dpi":        150,
        "savefig.dpi":       300,
        "savefig.format":    "pdf",
        "pdf.fonttype":      42,   # embed fonts as Type 42 (TrueType) — no missing-font issues
        "ps.fonttype":       42,
        "axes.spines.top":   False,
        "axes.spines.right": False,
    })


# ── Filename parsing ─────────────────────────────────────────────────────────

def parse_cache_name(path: Path) -> tuple[str, str] | None:
    m = re.match(r"^(.+)__(.+)__graph\.json$", path.name)
    return (m.group(1), m.group(2)) if m else None


def parse_ttl_name(path: Path) -> tuple[str, str, str]:
    """Return (document, model_slug, mode).

    Handles both legacy two-part names (doc__model) and the current three-part
    names (doc__model__mode).  Mode defaults to 'graphrag' for legacy files.
    """
    stem = path.stem
    parts = stem.split("__")
    if len(parts) >= 3 and parts[-1] in ("graphrag", "bypass", "zeroshot"):
        mode  = parts[-1]
        model = parts[-2]
        doc   = "__".join(parts[:-2])
    elif len(parts) >= 2:
        mode  = "graphrag"
        model = parts[-1]
        doc   = "__".join(parts[:-1])
    else:
        return (stem, "unknown", "graphrag")
    return (doc, model, mode)


# ── KG analysis ──────────────────────────────────────────────────────────────

def analyse_kg(cache_path: Path) -> dict | None:
    parsed = parse_cache_name(cache_path)
    if not parsed:
        return None
    doc, model = parsed
    data  = json.loads(cache_path.read_text())
    nodes = data["nodes"]
    rels  = data["relationships"]

    def node_label(n: dict) -> str:
        lbl = n.get("label") or (n.get("labels") or ["?"])[0]
        return lbl if isinstance(lbl, str) else (list(lbl)[0] if lbl else "?")

    all_labels       = [node_label(n) for n in nodes]
    non_chunk_labels = [l for l in all_labels if l != "Chunk"]
    schema_labels    = [l for l in non_chunk_labels if l in SCHEMA_NODE_LABELS]
    rel_types        = [r.get("type", "?") for r in rels]
    content_rels     = [t for t in rel_types if t not in STRUCTURAL_RELS]

    return {
        "document":              doc,
        "model":                 model,
        "total_nodes":           len(nodes),
        "chunk_nodes":           all_labels.count("Chunk"),
        "entity_nodes":          len(non_chunk_labels),
        "schema_nodes":          len(schema_labels),
        "schema_compliance_pct": round(len(schema_labels) / len(non_chunk_labels) * 100, 1) if non_chunk_labels else 0.0,
        "unique_entity_types":   len(set(non_chunk_labels)),
        "total_rels":            len(rels),
        "content_rels":          len(content_rels),
        "unique_rel_types":      len(set(content_rels)),
        "label_dist":            dict(Counter(non_chunk_labels).most_common()),
        "rel_type_dist":         dict(Counter(content_rels).most_common()),
    }


# ── Compliance analysis ──────────────────────────────────────────────────────

def analyse_compliance(ttl_path: Path) -> dict | None:
    doc, model, mode = parse_ttl_name(ttl_path)
    g = Graph()
    try:
        g.parse(str(ttl_path), format="turtle")
    except Exception as e:
        print(f"  WARNING: could not parse {ttl_path.name}: {e}")
        return None

    result: dict = {"document": doc, "model": model, "mode": mode}
    total_detected = total_possible = 0

    for section_key, dataset_uri in DATASET_SECTIONS.items():
        dataset_node = URIRef(dataset_uri)
        present_preds = set(g.predicates(dataset_node, None))
        section: dict[str, bool] = {}
        for obligation_key, rdf_pred in DATASET_PROPS.items():
            detected = GAI[rdf_pred] in present_preds
            section[obligation_key] = detected
            total_detected += int(detected)
            total_possible += 1
        result[section_key] = section

    result["total_detected"]     = total_detected
    result["total_possible"]     = total_possible
    result["detection_rate_pct"] = round(total_detected / total_possible * 100, 1) if total_possible else 0.0
    return result


# ── SHACL validation ─────────────────────────────────────────────────────────

def run_shacl(ttl_path: Path, shapes_path: Path) -> dict:
    doc, model, mode = parse_ttl_name(ttl_path)
    g = Graph()
    g.parse(str(ttl_path), format="turtle")
    conforms, report_graph, _ = shacl_validate(
        g, shacl_graph=str(shapes_path), inference="none", abort_on_first=False,
    )
    SH = Namespace("http://www.w3.org/ns/shacl#")
    violations = list(report_graph.subjects(RDF.type, SH.ValidationResult))
    messages   = [str(report_graph.value(v, SH.resultMessage) or "") for v in violations]
    return {
        "document":        doc,
        "model":           model,
        "mode":            mode,
        "conforms":        conforms,
        "violation_count": len(violations),
        "violations":      messages,
    }


# ── Cross-model agreement ─────────────────────────────────────────────────────

def compute_agreement(compliance_records: list[dict]) -> pd.DataFrame:
    by_doc: dict[str, dict[str, dict[str, bool]]] = defaultdict(dict)
    for rec in compliance_records:
        flat: dict[str, bool] = {}
        for sec in ("training", "validation", "testing"):
            for k, v in rec.get(sec, {}).items():
                flat[f"{sec}.{k}"] = v
        by_doc[rec["document"]][rec["model"]] = flat

    rows = []
    for doc, models in by_doc.items():
        model_list = list(models.keys())
        for i in range(len(model_list)):
            for j in range(i + 1, len(model_list)):
                m1, m2 = model_list[i], model_list[j]
                keys = set(models[m1]) & set(models[m2])
                if not keys:
                    continue
                agree = sum(models[m1][k] == models[m2][k] for k in keys)
                disagreed_keys = [k for k in keys if models[m1][k] != models[m2][k]]
                rows.append({
                    "document":       doc,
                    "model_a":        m1,
                    "model_b":        m2,
                    "n_keys":         len(keys),
                    "n_agree":        agree,
                    "agreement_pct":  round(agree / len(keys) * 100, 1),
                    "disagreed_keys": ", ".join(sorted(disagreed_keys)),
                })
    return pd.DataFrame(rows)


# ── Ground truth accuracy ─────────────────────────────────────────────────────

def compute_ground_truth_accuracy(shacl_records: list[dict]) -> pd.DataFrame:
    """Compare SHACL verdicts against ground truth where known."""
    rows = []
    for r in shacl_records:
        expected = GROUND_TRUTH.get(r["document"])
        if expected is None:
            continue
        predicted = r["conforms"]
        rows.append({
            "document":  r["document"],
            "model":     r["model"],
            "expected":  expected,
            "predicted": predicted,
            "correct":   predicted == expected,
            "tp": int(expected and predicted),
            "tn": int(not expected and not predicted),
            "fp": int(not expected and predicted),
            "fn": int(expected and not predicted),
        })
    return pd.DataFrame(rows)


# ── Precision / Recall / F1 at obligation level ──────────────────────────────

def compute_precision_recall(compliance_records: list[dict]) -> pd.DataFrame:
    """Per-run precision, recall, F1 at the obligation level against ground truth."""
    rows = []
    for rec in compliance_records:
        gt = OBLIGATION_GROUND_TRUTH.get(rec["document"])
        if gt is None:
            continue
        tp = tn = fp = fn = 0
        for sec in ("training", "validation", "testing"):
            for obligation, predicted in rec.get(sec, {}).items():
                expected = gt.get(sec, {}).get(obligation)
                if expected is None:
                    continue
                tp += int(predicted and expected)
                tn += int(not predicted and not expected)
                fp += int(predicted and not expected)
                fn += int(not predicted and expected)
        total = tp + tn + fp + fn
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1        = (2 * precision * recall / (precision + recall)
                     if (precision + recall) > 0 else 0.0)
        rows.append({
            "document":  rec["document"],
            "model":     rec["model"],
            "mode":      rec.get("mode", "graphrag"),
            "tp": tp, "tn": tn, "fp": fp, "fn": fn,
            "precision": round(precision, 3),
            "recall":    round(recall, 3),
            "f1":        round(f1, 3),
            "accuracy":  round((tp + tn) / total, 3) if total else 0.0,
        })
    return pd.DataFrame(rows)


# ── Per-obligation present-class metrics + support ──────────────────────────

# Minimum gold positives ("present") needed before a per-obligation recall is
# trustworthy. Real medical cards are ~80% "not provided", so many obligations
# have too few positives to estimate recall from — those are flagged, not used
# for capability claims.
SUPPORT_THRESHOLD = 5


def compute_per_obligation_metrics(
    compliance_records: list[dict], by_section: bool = False
) -> pd.DataFrame:
    """Present-class precision/recall/F1 per obligation, pooled across all runs
    that have ground truth, plus the gold support (# expected-present).

    'present' is the positive class: tp = predicted present AND expected present.
    """
    agg: dict[tuple, dict[str, int]] = defaultdict(
        lambda: {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "n_eval": 0}
    )
    # support = number of DISTINCT (document, section) gold positives for the
    # obligation, counted once regardless of how many model×mode runs touched
    # that card. This reflects how many real examples exist to estimate recall
    # from — pooling across repeated runs of the same card would inflate it.
    support_docs: dict[tuple, set[tuple]] = defaultdict(set)
    for rec in compliance_records:
        gt = OBLIGATION_GROUND_TRUTH.get(rec["document"])
        if gt is None:
            continue
        for sec in ("training", "validation", "testing"):
            for ob, predicted in rec.get(sec, {}).items():
                expected = gt.get(sec, {}).get(ob)
                if expected is None:
                    continue
                key = (ob, sec) if by_section else (ob,)
                a = agg[key]
                a["tp"] += int(predicted and expected)
                a["fp"] += int(predicted and not expected)
                a["fn"] += int(not predicted and expected)
                a["tn"] += int(not predicted and not expected)
                a["n_eval"] += 1
                if expected:
                    support_docs[key].add((rec["document"], sec))

    rows = []
    for key, a in agg.items():
        tp, fp, fn = a["tp"], a["fp"], a["fn"]
        support = len(support_docs[key])
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall    = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (2 * precision * recall / (precision + recall)
              if (precision + recall) else 0.0)
        row = {"obligation": key[0]}
        if by_section:
            row["section"] = key[1]
        row.update({
            "support":            support,
            "n_eval":             a["n_eval"],
            "tp": tp, "fp": fp, "fn": fn,
            "precision":          round(precision, 3),
            "recall":             round(recall, 3),
            "f1":                 round(f1, 3),
            "sufficient_support": support >= SUPPORT_THRESHOLD,
        })
        rows.append(row)

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("support", ascending=False).reset_index(drop=True)
    return df


def plot_per_obligation_f1(per_ob_df: pd.DataFrame, out_dir: Path) -> str:
    """Horizontal F1 bars per obligation; low-support obligations greyed out."""
    if per_ob_df.empty:
        return ""
    df = per_ob_df.sort_values("f1").reset_index(drop=True)
    colours = ["#27ae60" if s else "#bbbbbb" for s in df["sufficient_support"]]
    labels  = [f"{o}  (n+={s})" for o, s in zip(df["obligation"], df["support"])]

    fig, ax = plt.subplots(figsize=(9, max(3, len(df) * 0.4)))
    bars = ax.barh(range(len(df)), df["f1"], color=colours, edgecolor="white")
    ax.bar_label(bars, labels=[f"{v:.2f}" for v in df["f1"]], padding=3, fontsize=7)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlim(0, 1.1)
    ax.set_xlabel("Present-class F1")
    ax.set_title(f"Per-Obligation Detection F1  "
                 f"(grey = support < {SUPPORT_THRESHOLD}, recall unreliable)")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    return _savefig(fig, out_dir, "per_obligation_f1")


def plot_precision_recall(pr_df: pd.DataFrame, out_dir: Path) -> str:
    if pr_df.empty:
        return ""
    pr_df = pr_df.copy()
    pr_df["run"] = pr_df.apply(
        lambda r: f"{_short(r['document'], 18)}\n({r['model']}, {r['mode']})", axis=1
    )
    x = np.arange(len(pr_df))
    w = 0.25
    fig, ax = plt.subplots(figsize=(max(6, len(pr_df) * 1.4), 4))
    ax.bar(x - w, pr_df["precision"], w, label="Precision", color="steelblue",   edgecolor="white")
    ax.bar(x,     pr_df["recall"],    w, label="Recall",    color="seagreen",    edgecolor="white")
    ax.bar(x + w, pr_df["f1"],        w, label="F1",        color="darkorange",  edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(pr_df["run"], rotation=35, ha="right", fontsize=7)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Score")
    ax.set_title("Obligation-Level Precision / Recall / F1 per Run")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return _savefig(fig, out_dir, "precision_recall")


# ── Frequently missed obligations ────────────────────────────────────────────

def compute_missed_obligations(compliance_records: list[dict]) -> pd.DataFrame:
    """For each obligation key, count how often it was NOT detected across all runs."""
    counts: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "missed": 0})
    for rec in compliance_records:
        for sec in ("training", "validation", "testing"):
            for k, v in rec.get(sec, {}).items():
                key = f"{sec[:5]}.{k}"
                counts[key]["total"] += 1
                counts[key]["missed"] += int(not v)
    rows = [
        {
            "obligation":   k,
            "total_runs":   v["total"],
            "missed":       v["missed"],
            "miss_rate_pct": round(v["missed"] / v["total"] * 100, 1) if v["total"] else 0.0,
        }
        for k, v in counts.items()
    ]
    return pd.DataFrame(rows).sort_values("miss_rate_pct", ascending=False)


# ── GraphRAG vs bypass mode comparison ──────────────────────────────────────

def compute_mode_comparison(compliance_records: list[dict]) -> pd.DataFrame:
    """Per-obligation agreement between graphrag and bypass for the same (doc, model) pair."""
    # Index by (doc, model, mode) → flat obligation dict
    index: dict[tuple, dict[str, bool]] = {}
    for rec in compliance_records:
        key = (rec["document"], rec["model"], rec.get("mode", "graphrag"))
        flat: dict[str, bool] = {}
        for sec in ("training", "validation", "testing"):
            for k, v in rec.get(sec, {}).items():
                flat[f"{sec[:5]}.{k}"] = v
        index[key] = flat

    rows = []
    seen = set()
    for (doc, model, mode), flat in index.items():
        if mode != "graphrag":
            continue
        bypass_key = (doc, model, "bypass")
        if bypass_key not in index:
            continue
        pair_id = (doc, model)
        if pair_id in seen:
            continue
        seen.add(pair_id)
        bypass_flat = index[bypass_key]
        obligation_keys = sorted(set(flat) | set(bypass_flat))
        for ok in obligation_keys:
            gr = flat.get(ok, False)
            bp = bypass_flat.get(ok, False)
            rows.append({
                "document":   doc,
                "model":      model,
                "obligation": ok,
                "graphrag":   int(gr),
                "bypass":     int(bp),
                "agree":      int(gr == bp),
            })
    return pd.DataFrame(rows)


def plot_mode_comparison(
    compliance_records: list[dict],
    shacl_records: list[dict],
    out_dir: Path,
) -> list[str]:
    """
    Two plots:
      1. Per-obligation detection rate: graphrag vs bypass side-by-side bars.
      2. SHACL verdict comparison: graphrag vs bypass per (doc, model).
    """
    saved: list[str] = []

    # ── 1. Per-obligation detection rate comparison ───────────────────────────
    by_mode: dict[str, dict[str, list[int]]] = {"graphrag": {}, "bypass": {}}
    for rec in compliance_records:
        mode = rec.get("mode", "graphrag")
        if mode not in by_mode:
            continue
        for sec in ("training", "validation", "testing"):
            for k, v in rec.get(sec, {}).items():
                key = f"{sec[:5]}.{k}"
                by_mode[mode].setdefault(key, []).append(int(v))

    if by_mode["graphrag"] and by_mode["bypass"]:
        all_keys = sorted(set(by_mode["graphrag"]) | set(by_mode["bypass"]))
        gr_rates = [np.mean(by_mode["graphrag"].get(k, [0])) * 100 for k in all_keys]
        bp_rates = [np.mean(by_mode["bypass"].get(k, [0])) * 100 for k in all_keys]

        x = np.arange(len(all_keys))
        w = 0.38
        fig, ax = plt.subplots(figsize=(14, max(4, len(all_keys) * 0.32)))
        ax.barh(x - w / 2, gr_rates, w, label="GraphRAG", color="steelblue",  edgecolor="white")
        ax.barh(x + w / 2, bp_rates, w, label="Bypass",   color="darkorange", edgecolor="white")
        ax.set_yticks(x)
        ax.set_yticklabels(all_keys, fontsize=7)
        ax.set_xlim(0, 115)
        ax.xaxis.set_major_formatter(mtick.PercentFormatter())
        ax.set_xlabel("Detection rate (%)")
        ax.set_title("Obligation Detection Rate: GraphRAG vs Bypass")
        ax.legend()
        ax.grid(axis="x", alpha=0.3)
        ax.invert_yaxis()
        fig.tight_layout()
        saved.append(_savefig(fig, out_dir, "mode_obligation_comparison"))

    # ── 2. SHACL verdict comparison ───────────────────────────────────────────
    if shacl_records:
        verdict_by_key: dict[tuple, dict[str, bool]] = {}
        for r in shacl_records:
            key = (r["document"], r["model"])
            verdict_by_key.setdefault(key, {})[r.get("mode", "graphrag")] = r["conforms"]

        paired = [(doc, mdl, v.get("graphrag"), v.get("bypass"))
                  for (doc, mdl), v in verdict_by_key.items()
                  if "graphrag" in v and "bypass" in v]

        if paired:
            labels = [f"{_short(d, 20)}\n({m})" for d, m, _, _ in paired]
            gr_vals = [int(g) for _, _, g, _ in paired]
            bp_vals = [int(b) for _, _, _, b in paired]
            x = np.arange(len(paired))
            w = 0.38

            fig, ax = plt.subplots(figsize=(max(5, len(paired) * 1.4), 4))
            ax.bar(x - w / 2, gr_vals, w, label="GraphRAG", color="steelblue",  edgecolor="white")
            ax.bar(x + w / 2, bp_vals, w, label="Bypass",   color="darkorange", edgecolor="white")
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=30, ha="right")
            ax.set_yticks([0, 1])
            ax.set_yticklabels(["NON-COMPLIANT", "COMPLIANT"])
            ax.set_title("SHACL Verdict: GraphRAG vs Bypass")
            ax.legend()
            ax.grid(axis="y", alpha=0.3)
            fig.tight_layout()
            saved.append(_savefig(fig, out_dir, "mode_verdict_comparison"))

    return [s for s in saved if s]


# ── Entity type schema adherence detail ──────────────────────────────────────

def compute_entity_type_summary(kg_records: list[dict]) -> pd.DataFrame:
    rows = []
    for rec in kg_records:
        for label, count in rec.get("label_dist", {}).items():
            rows.append({
                "document": rec["document"],
                "model":    rec["model"],
                "entity_type": label,
                "count":    count,
                "schema_compliant": label in SCHEMA_NODE_LABELS,
            })
    return pd.DataFrame(rows)


# ── Plotting helpers ──────────────────────────────────────────────────────────

def _short(s: str, n: int = 20) -> str:
    return (s[:n] + "…") if len(s) > n else s


def _run_label(doc: str, model: str) -> str:
    return f"{_short(doc, 18)}\n({model})"


def _savefig(fig: plt.Figure, out_dir: Path, name: str) -> str:
    """Save figure as PDF and return filename."""
    path = out_dir / f"{name}.pdf"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path.name


# ── Plots ─────────────────────────────────────────────────────────────────────

def plot_kg_quality(kg_df: pd.DataFrame, out_dir: Path) -> str:
    metrics = [
        ("entity_nodes",          "Entity Nodes\n(non-Chunk)",  "steelblue"),
        ("schema_compliance_pct", "Schema\nCompliance (%)",     "seagreen"),
        ("unique_entity_types",   "Unique\nEntity Types",       "coral"),
        ("content_rels",          "Content\nRelationships",     "mediumpurple"),
        ("unique_rel_types",      "Unique\nRel. Types",         "darkorange"),
    ]
    fig, axes = plt.subplots(1, len(metrics), figsize=(3.2 * len(metrics), 4))
    fig.suptitle("Knowledge Graph Quality by Run", y=1.01)

    labels = [_run_label(r.document, r.model) for r in kg_df.itertuples()]
    x = range(len(kg_df))

    for ax, (col, title, colour) in zip(axes, metrics):
        ax.bar(x, kg_df[col], color=colour, edgecolor="white", linewidth=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=40, ha="right")
        ax.set_title(title)
        if col == "schema_compliance_pct":
            ax.set_ylim(0, 108)
            ax.yaxis.set_major_formatter(mtick.PercentFormatter())
        ax.grid(axis="y", alpha=0.3, linewidth=0.5)

    fig.tight_layout()
    return _savefig(fig, out_dir, "kg_quality")


def plot_entity_types(entity_df: pd.DataFrame, out_dir: Path) -> str:
    if entity_df.empty:
        return ""
    runs = entity_df.groupby(["document", "model"])
    schema_counts, offschema_counts, run_labels = [], [], []
    for (doc, model), grp in runs:
        schema_counts.append(grp[grp.schema_compliant]["count"].sum())
        offschema_counts.append(grp[~grp.schema_compliant]["count"].sum())
        run_labels.append(_run_label(doc, model))

    x = range(len(run_labels))
    fig, ax = plt.subplots(figsize=(max(5, len(run_labels) * 1.2), 4))
    ax.bar(x, schema_counts,    label="Schema-expected",  color="seagreen",  edgecolor="white")
    ax.bar(x, offschema_counts, bottom=schema_counts, label="Off-schema", color="tomato", edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(run_labels, rotation=35, ha="right")
    ax.set_ylabel("Entity node count")
    ax.set_title("Entity Type Schema Adherence per Run")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return _savefig(fig, out_dir, "entity_schema_adherence")


def plot_compliance_heatmap(compliance_records: list[dict], out_dir: Path) -> str:
    rows = []
    for rec in compliance_records:
        run_label = f"{_short(rec['document'], 20)} ({rec['model']})"
        for sec in ("training", "validation", "testing"):
            for k, v in rec.get(sec, {}).items():
                rows.append({"run": run_label, "key": f"{sec[:5]}.{k}", "detected": int(v)})

    if not rows:
        return ""

    df_m  = pd.DataFrame(rows)
    pivot = df_m.pivot_table(index="run", columns="key", values="detected", fill_value=0)

    fig_w = max(12, len(pivot.columns) * 0.6)
    fig_h = max(3,  len(pivot)        * 0.5 + 1.5)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    im = ax.imshow(pivot.values, aspect="auto", cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=55, ha="right", fontsize=7)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_title("Obligation Detection Matrix  (green = detected, red = missing)")
    plt.colorbar(im, ax=ax, fraction=0.012, pad=0.02, label="Detected")

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            ax.text(j, i, "✓" if pivot.values[i, j] else "✗",
                    ha="center", va="center", fontsize=7,
                    color="black" if pivot.values[i, j] else "#888")

    fig.tight_layout()
    return _savefig(fig, out_dir, "compliance_heatmap")


def plot_detection_rates(compliance_records: list[dict], out_dir: Path) -> str:
    if not compliance_records:
        return ""
    per_section = []
    for rec in compliance_records:
        run = f"{_short(rec['document'], 18)} ({rec['model']})"
        for sec in ("training", "validation", "testing"):
            section = rec.get(sec, {})
            if section:
                rate = sum(section.values()) / len(section) * 100
                per_section.append({"run": run, "section": sec, "rate": rate})

    df_s  = pd.DataFrame(per_section)
    pivot = df_s.pivot_table(index="run", columns="section", values="rate", aggfunc="mean").fillna(0)

    x       = range(len(pivot))
    width   = 0.25
    colours = {"training": "steelblue", "validation": "seagreen", "testing": "darkorange"}

    fig, ax = plt.subplots(figsize=(max(6, len(pivot) * 1.2), 4))
    for i, sec in enumerate(("training", "validation", "testing")):
        if sec in pivot.columns:
            ax.bar([xi + i * width for xi in x], pivot[sec], width=width,
                   label=sec.capitalize(), color=colours[sec], edgecolor="white")

    ax.set_xticks([xi + width for xi in x])
    ax.set_xticklabels(pivot.index, rotation=35, ha="right")
    ax.set_ylim(0, 108)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_ylabel("Obligation detection rate (%)")
    ax.set_title("Per-Dataset-Section Obligation Detection Rate")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return _savefig(fig, out_dir, "detection_rates")


def plot_per_card_model_comparison(compliance_records: list[dict], out_dir: Path) -> str:
    """
    For each document card, compare detection rates across all models that ran on it.
    One subplot per card, grouped bars per model coloured by dataset section.
    """
    if not compliance_records:
        return ""

    # Group records by document
    by_doc: dict[str, list[dict]] = defaultdict(list)
    for rec in compliance_records:
        by_doc[rec["document"]].append(rec)

    # Only include docs with more than one model OR all docs (single-model still useful)
    docs = sorted(by_doc.keys())
    n_docs = len(docs)
    if n_docs == 0:
        return ""

    cols = min(n_docs, 3)
    rows = (n_docs + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4.5, rows * 3.8), squeeze=False)
    fig.suptitle("Per-Card Obligation Detection Rate by Model", y=1.01)

    sec_colours = {"training": "steelblue", "validation": "seagreen", "testing": "darkorange"}
    sections    = ["training", "validation", "testing"]

    for idx, doc in enumerate(docs):
        ax    = axes[idx // cols][idx % cols]
        recs  = by_doc[doc]
        models = [r["model"] for r in recs]
        n_models = len(models)

        x     = np.arange(n_models)
        width = 0.25

        for si, sec in enumerate(sections):
            rates = []
            for rec in recs:
                section = rec.get(sec, {})
                rate = sum(section.values()) / len(section) * 100 if section else 0.0
                rates.append(rate)
            bars = ax.bar(x + si * width, rates, width, label=sec.capitalize(),
                          color=sec_colours[sec], edgecolor="white")
            # Annotate bars with value
            for bar, val in zip(bars, rates):
                if val > 0:
                    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                            f"{val:.0f}%", ha="center", va="bottom", fontsize=6)

        ax.set_title(_short(doc, 28), fontsize=9)
        ax.set_xticks(x + width)
        ax.set_xticklabels(models, rotation=20, ha="right", fontsize=7)
        ax.set_ylim(0, 115)
        ax.yaxis.set_major_formatter(mtick.PercentFormatter())
        ax.set_ylabel("Detection rate (%)")
        ax.grid(axis="y", alpha=0.3)
        if idx == 0:
            ax.legend(fontsize=7, loc="upper right")

    # Hide unused subplots
    for idx in range(n_docs, rows * cols):
        axes[idx // cols][idx % cols].set_visible(False)

    fig.tight_layout()
    return _savefig(fig, out_dir, "per_card_model_comparison")


def plot_missed_obligations(missed_df: pd.DataFrame, out_dir: Path) -> str:
    """Bar chart of miss rate per obligation key, sorted descending."""
    if missed_df.empty:
        return ""

    fig, ax = plt.subplots(figsize=(10, max(3, len(missed_df) * 0.28)))
    colours = ["#c0392b" if r >= 50 else "#e67e22" if r >= 20 else "#27ae60"
               for r in missed_df["miss_rate_pct"]]
    bars = ax.barh(missed_df["obligation"], missed_df["miss_rate_pct"],
                   color=colours, edgecolor="white")
    ax.bar_label(bars, labels=[f"{v:.0f}%" for v in missed_df["miss_rate_pct"]],
                 padding=3, fontsize=7)
    ax.set_xlim(0, 115)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_xlabel("Miss rate across all runs (%)")
    ax.set_title("Obligation Miss Rate  (red ≥ 50%, orange ≥ 20%, green < 20%)")
    ax.grid(axis="x", alpha=0.3)
    ax.invert_yaxis()
    fig.tight_layout()
    return _savefig(fig, out_dir, "missed_obligations")


def plot_shacl(shacl_records: list[dict], out_dir: Path) -> str:
    if not shacl_records:
        return ""
    labels = [_run_label(r["document"], r["model"]) for r in shacl_records]
    counts = [r["violation_count"] for r in shacl_records]
    colors = ["#c0392b" if c > 0 else "#27ae60" for c in counts]

    fig, ax = plt.subplots(figsize=(max(5, len(labels) * 1.2), 4))
    bars = ax.bar(range(len(labels)), counts, color=colors, edgecolor="white")
    ax.bar_label(bars, padding=3)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylabel("SHACL Violations")
    ax.set_title("SHACL Validation: Violation Count per Run\n(green = compliant)")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return _savefig(fig, out_dir, "shacl_violations")


def plot_ground_truth_accuracy(gt_df: pd.DataFrame, out_dir: Path) -> str:
    """Confusion-style stacked bar per model showing TP/TN/FP/FN counts."""
    if gt_df.empty:
        return ""

    by_model = gt_df.groupby("model")[["tp", "tn", "fp", "fn"]].sum().reset_index()
    models   = by_model["model"].tolist()
    x        = np.arange(len(models))
    width    = 0.5

    fig, ax = plt.subplots(figsize=(max(4, len(models) * 1.4), 4))
    bottom = np.zeros(len(models))
    colours = {"tp": "#27ae60", "tn": "#2980b9", "fp": "#e74c3c", "fn": "#e67e22"}
    labels  = {"tp": "True Positive (correct compliant)",
                "tn": "True Negative (correct non-compliant)",
                "fp": "False Positive (incorrectly compliant)",
                "fn": "False Negative (missed non-compliance)"}

    for key in ("tp", "tn", "fp", "fn"):
        vals = by_model[key].values.astype(float)
        ax.bar(x, vals, width, bottom=bottom, label=labels[key],
               color=colours[key], edgecolor="white")
        for xi, (v, b) in enumerate(zip(vals, bottom)):
            if v > 0:
                ax.text(xi, b + v / 2, str(int(v)), ha="center", va="center",
                        fontsize=8, color="white", fontweight="bold")
        bottom += vals

    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=15, ha="right")
    ax.set_ylabel("Number of documents")
    ax.set_title("Compliance Verdict Accuracy vs Ground Truth")
    ax.legend(fontsize=7, bbox_to_anchor=(1.01, 1), loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return _savefig(fig, out_dir, "ground_truth_accuracy")


def plot_agreement(agree_df: pd.DataFrame, out_dir: Path) -> str:
    if agree_df.empty:
        return ""
    labels = [
        f"{_short(r.document, 14)}\n{_short(r.model_a, 12)} vs\n{_short(r.model_b, 12)}"
        for r in agree_df.itertuples()
    ]
    fig, ax = plt.subplots(figsize=(max(5, len(agree_df) * 1.5), 4))
    bars = ax.bar(range(len(agree_df)), agree_df["agreement_pct"],
                  color="mediumpurple", edgecolor="white")
    ax.bar_label(bars, labels=[f"{v:.1f}%" for v in agree_df["agreement_pct"]], padding=3)
    ax.set_xticks(range(len(agree_df)))
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 115)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.axhline(100, color="seagreen", linestyle="--", alpha=0.6, label="Perfect agreement")
    ax.set_title("Cross-model Agreement on Obligation Detection (%)")
    ax.set_ylabel("Agreement (%)")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return _savefig(fig, out_dir, "cross_model_agreement")


# ── Console report ────────────────────────────────────────────────────────────

def _section(title: str) -> None:
    print(f"\n{'=' * 72}\n  {title}\n{'=' * 72}")


def render_report(
    kg_df: pd.DataFrame,
    compliance_records: list[dict],
    shacl_records: list[dict],
    agree_df: pd.DataFrame,
    entity_df: pd.DataFrame,
    gt_df: pd.DataFrame,
    missed_df: pd.DataFrame,
    mode_comparison_df: pd.DataFrame,
    pr_df: pd.DataFrame,
    per_ob_df: pd.DataFrame,
    out_dir: Path,
) -> None:
    report_lines: list[str] = []

    def rline(s: str = "") -> None:
        report_lines.append(s)

    # ── 1. KG Quality ────────────────────────────────────────────────────────
    _section("1. Knowledge Graph Quality")
    if not kg_df.empty:
        display = kg_df[[
            "document", "model",
            "entity_nodes", "schema_nodes", "schema_compliance_pct",
            "unique_entity_types", "content_rels", "unique_rel_types",
        ]].copy()
        display.columns = [
            "Document", "Model",
            "Entity Nodes", "Schema Nodes", "Schema %",
            "Node Types", "Content Rels", "Rel Types",
        ]
        out = display.to_string(index=False)
        print(out)
        rline("=== 1. KG Quality ===")
        rline(out)
    else:
        print("  No cache files found.")

    # ── 2. Entity type inventory per model ───────────────────────────────────
    _section("2. Entity Type Inventory (non-Chunk nodes)")
    if not entity_df.empty:
        for (doc, model), grp in entity_df.groupby(["document", "model"]):
            print(f"\n  {doc}  |  {model}")
            for _, row in grp.sort_values("count", ascending=False).iterrows():
                tag = "✓" if row.schema_compliant else "✗"
                print(f"    {tag} {row.entity_type:<35s} {row['count']:>3d}")

    # ── 3. Compliance detection summary ──────────────────────────────────────
    _section("3. Compliance Detection Summary")
    if compliance_records:
        comp_rows = [
            {
                "Document":  r["document"],
                "Model":     r["model"],
                "Mode":      r.get("mode", "graphrag"),
                "Detected":  r["total_detected"],
                "Possible":  r["total_possible"],
                "Rate %":    r["detection_rate_pct"],
            }
            for r in compliance_records
        ]
        out = pd.DataFrame(comp_rows).to_string(index=False)
        print(out)
        rline("\n=== 3. Compliance Summary ===")
        rline(out)
    else:
        print("  No TTL outputs found.")

    # ── 4. Per-section obligation breakdown ───────────────────────────────────
    _section("4. Per-Section Obligation Coverage")
    for rec in compliance_records:
        mode_tag = f"  [{rec.get('mode', 'graphrag')}]"
        print(f"\n  {rec['document']}  |  {rec['model']}{mode_tag}")
        for sec in ("training", "validation", "testing"):
            section = rec.get(sec, {})
            detected = sum(section.values())
            total    = len(section)
            missing  = [k for k, v in section.items() if not v]
            print(f"    {sec:12s}: {detected:2d}/{total}", end="")
            if missing:
                print(f"  missing: {', '.join(missing)}")
            else:
                print("  ✓ all obligations present")

    # ── 5. Frequently missed obligations ─────────────────────────────────────
    _section("5. Frequently Missed Obligations")
    if not missed_df.empty:
        out = missed_df.to_string(index=False)
        print(out)
        rline("\n=== 5. Missed Obligations ===")
        rline(out)

    # ── 6. SHACL ──────────────────────────────────────────────────────────────
    _section("6. SHACL Validation Results")
    if shacl_records:
        for r in shacl_records:
            status = "COMPLIANT" if r["conforms"] else f"NON-COMPLIANT  ({r['violation_count']} violations)"
            print(f"  {r['document']:45s}  {r['model']:20s}  {status}")
            for msg in r["violations"]:
                print(f"    • {msg}")
        rline("\n=== 6. SHACL ===")
        for r in shacl_records:
            rline(f"  {r['document']}  |  {r['model']}  conforms={r['conforms']}  violations={r['violation_count']}")
    else:
        print("  (no --shapes provided — SHACL skipped)")

    # ── 7. Ground truth accuracy ──────────────────────────────────────────────
    _section("7. Ground Truth Accuracy")
    if not gt_df.empty:
        summary = gt_df.groupby("model")[["correct", "tp", "tn", "fp", "fn"]].sum()
        summary["accuracy_%"] = (summary["correct"] / gt_df.groupby("model").size() * 100).round(1)
        out = summary.to_string()
        print(out)
        rline("\n=== 7. Ground Truth Accuracy ===")
        rline(out)
    else:
        print("  No ground truth entries matched (add to GROUND_TRUTH dict or provide --shapes).")

    # ── 8. Cross-model agreement ──────────────────────────────────────────────
    _section("8. Cross-model Agreement on Obligation Detection")
    if not agree_df.empty:
        cols = ["document", "model_a", "model_b", "n_keys", "n_agree", "agreement_pct", "disagreed_keys"]
        out = agree_df[cols].to_string(index=False)
        print(out)
        rline("\n=== 8. Cross-model Agreement ===")
        rline(out)
    else:
        print("  No document has results from multiple models.")

    # ── 9. GraphRAG vs bypass mode comparison ─────────────────────────────────
    _section("9. GraphRAG vs Bypass Mode Comparison")
    if not mode_comparison_df.empty:
        summary = (
            mode_comparison_df
            .groupby("obligation")[["graphrag", "bypass", "agree"]]
            .mean()
            .mul(100)
            .round(1)
            .rename(columns={"graphrag": "GraphRAG %", "bypass": "Bypass %", "agree": "Agree %"})
            .sort_values("Agree %")
        )
        out = summary.to_string()
        print(out)
        rline("\n=== 9. GraphRAG vs Bypass ===")
        rline(out)

        overall_agree = mode_comparison_df["agree"].mean() * 100
        print(f"\n  Overall per-obligation agreement: {overall_agree:.1f}%")
        rline(f"\n  Overall per-obligation agreement: {overall_agree:.1f}%")

        # Show pairs that have both modes
        pairs = mode_comparison_df[["document", "model"]].drop_duplicates()
        print(f"\n  Pairs with both modes ({len(pairs)}):")
        for _, row in pairs.iterrows():
            print(f"    {row['document']}  |  {row['model']}")
    else:
        print("  No (doc, model) pairs found with both graphrag and bypass outputs.")

    # ── 10. Obligation-level precision / recall / F1 ──────────────────────────
    _section("10. Obligation-Level Precision / Recall / F1")
    if not pr_df.empty:
        out = pr_df[["document", "model", "mode", "precision", "recall", "f1",
                      "tp", "tn", "fp", "fn"]].to_string(index=False)
        print(out)
        rline("\n=== 10. Precision / Recall / F1 ===")
        rline(out)
        avg = pr_df[["precision", "recall", "f1"]].mean().round(3)
        print(f"\n  Macro averages — P: {avg['precision']}  R: {avg['recall']}  F1: {avg['f1']}")
        rline(f"\n  Macro averages — P: {avg['precision']}  R: {avg['recall']}  F1: {avg['f1']}")
    else:
        print("  No documents with per-obligation ground truth found.")

    # ── 11. Per-obligation present-class detection + support ──────────────────
    _section("11. Per-Obligation Present-Class Detection (with gold support)")
    if not per_ob_df.empty:
        show = per_ob_df[["obligation", "support", "n_eval", "tp", "fp", "fn",
                          "precision", "recall", "f1", "sufficient_support"]]
        out = show.to_string(index=False)
        print(out)
        rline("\n=== 11. Per-Obligation Detection ===")
        rline(out)

        # Pooled (micro) present-class metrics across all obligations.
        tp = int(per_ob_df["tp"].sum()); fp = int(per_ob_df["fp"].sum()); fn = int(per_ob_df["fn"].sum())
        micro_p = tp / (tp + fp) if (tp + fp) else 0.0
        micro_r = tp / (tp + fn) if (tp + fn) else 0.0
        micro_f1 = (2 * micro_p * micro_r / (micro_p + micro_r)) if (micro_p + micro_r) else 0.0

        # Macro over obligations with enough gold positives to trust recall.
        ok = per_ob_df[per_ob_df["sufficient_support"]]
        macro_f1 = round(ok["f1"].mean(), 3) if not ok.empty else float("nan")
        n_low = int((~per_ob_df["sufficient_support"]).sum())

        summary = (
            f"\n  Present-class micro — P: {micro_p:.3f}  R: {micro_r:.3f}  F1: {micro_f1:.3f}"
            f"\n  Macro F1 over {len(ok)} sufficiently-supported obligations "
            f"(support ≥ {SUPPORT_THRESHOLD}): {macro_f1}"
            f"\n  {n_low} obligation(s) below support threshold — recall unreliable, "
            f"excluded from macro."
        )
        print(summary)
        rline(summary)
    else:
        print("  No per-obligation ground truth to evaluate against.")

    # ── Save text report ──────────────────────────────────────────────────────
    report_path = out_dir / "report.txt"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyse EU AI Act compliance pipeline results for thesis",
    )
    parser.add_argument(
        "--shapes", type=Path, default=None,
        help="Path to article10-shapes.ttl for SHACL validation (optional)",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=REPO_ROOT / "analysis",
        help="Directory for CSVs, plots, and report (default: analysis/)",
    )
    args = parser.parse_args()

    _apply_thesis_style()

    out_dir = args.output_dir
    out_dir.mkdir(exist_ok=True)

    # ── Discover and analyse
    kg_records = [
        r for path in sorted(CACHE_DIR.glob("*__graph.json"))
        if (r := analyse_kg(path)) is not None
    ]
    compliance_records = [
        r for path in sorted(OUTPUT_DIR.glob("*.ttl"))
        if (r := analyse_compliance(path)) is not None
    ]
    shacl_records: list[dict] = []
    if args.shapes:
        if args.shapes.exists():
            shacl_records = [run_shacl(p, args.shapes) for p in sorted(OUTPUT_DIR.glob("*.ttl"))]
        else:
            print(f"WARNING: shapes file not found: {args.shapes}")

    kg_df              = pd.DataFrame(kg_records)
    entity_df          = compute_entity_type_summary(kg_records)
    agree_df           = compute_agreement(compliance_records) if compliance_records else pd.DataFrame()
    gt_df              = compute_ground_truth_accuracy(shacl_records) if shacl_records else pd.DataFrame()
    missed_df          = compute_missed_obligations(compliance_records) if compliance_records else pd.DataFrame()
    mode_comparison_df = compute_mode_comparison(compliance_records) if compliance_records else pd.DataFrame()
    pr_df              = compute_precision_recall(compliance_records) if compliance_records else pd.DataFrame()
    per_ob_df          = compute_per_obligation_metrics(compliance_records) if compliance_records else pd.DataFrame()

    # ── Save CSVs
    if not kg_df.empty:
        kg_df.drop(columns=["label_dist", "rel_type_dist"], errors="ignore").to_csv(
            out_dir / "kg_metrics.csv", index=False,
        )
    if compliance_records:
        flat_rows = []
        for rec in compliance_records:
            row: dict = {
                "document": rec["document"], "model": rec["model"],
                "mode": rec.get("mode", "graphrag"),
                "total_detected": rec["total_detected"],
                "detection_rate_pct": rec["detection_rate_pct"],
            }
            for sec in ("training", "validation", "testing"):
                for k, v in rec.get(sec, {}).items():
                    row[f"{sec}.{k}"] = int(v)
            flat_rows.append(row)
        pd.DataFrame(flat_rows).to_csv(out_dir / "compliance_matrix.csv", index=False)
    if shacl_records:
        pd.DataFrame([{k: v for k, v in r.items() if k != "violations"} for r in shacl_records]).to_csv(
            out_dir / "shacl_results.csv", index=False,
        )
    if not agree_df.empty:
        agree_df.to_csv(out_dir / "cross_model_agreement.csv", index=False)
    if not entity_df.empty:
        entity_df.to_csv(out_dir / "entity_type_inventory.csv", index=False)
    if not gt_df.empty:
        gt_df.to_csv(out_dir / "ground_truth_accuracy.csv", index=False)
    if not missed_df.empty:
        missed_df.to_csv(out_dir / "missed_obligations.csv", index=False)
    if not mode_comparison_df.empty:
        mode_comparison_df.to_csv(out_dir / "mode_comparison.csv", index=False)
    if not pr_df.empty:
        pr_df.to_csv(out_dir / "precision_recall.csv", index=False)
    if not per_ob_df.empty:
        per_ob_df.to_csv(out_dir / "per_obligation_metrics.csv", index=False)

    # ── Generate plots (all saved as PDF)
    plots_generated: list[str] = []
    if not kg_df.empty:
        plots_generated.append(plot_kg_quality(kg_df, out_dir))
        plots_generated.append(plot_entity_types(entity_df, out_dir))
    if compliance_records:
        plots_generated.append(plot_compliance_heatmap(compliance_records, out_dir))
        plots_generated.append(plot_detection_rates(compliance_records, out_dir))
        plots_generated.append(plot_per_card_model_comparison(compliance_records, out_dir))
        plots_generated.append(plot_missed_obligations(missed_df, out_dir))
    if shacl_records:
        plots_generated.append(plot_shacl(shacl_records, out_dir))
        if not gt_df.empty:
            plots_generated.append(plot_ground_truth_accuracy(gt_df, out_dir))
    if not agree_df.empty:
        plots_generated.append(plot_agreement(agree_df, out_dir))
    if not mode_comparison_df.empty or shacl_records:
        plots_generated.extend(plot_mode_comparison(compliance_records, shacl_records, out_dir))
    if not pr_df.empty:
        plots_generated.append(plot_precision_recall(pr_df, out_dir))
    if not per_ob_df.empty:
        plots_generated.append(plot_per_obligation_f1(per_ob_df, out_dir))

    # ── Console + text report
    render_report(kg_df, compliance_records, shacl_records, agree_df, entity_df,
                  gt_df, missed_df, mode_comparison_df, pr_df, per_ob_df, out_dir)

    print(f"\n{'─' * 72}")
    print(f"  Outputs saved to: {out_dir}/")
    for name in filter(None, plots_generated):
        print(f"    {name}")
    for csv in sorted(out_dir.glob("*.csv")):
        print(f"    {csv.name}")
    print(f"    report.txt")
    print(f"{'─' * 72}\n")


if __name__ == "__main__":
    main()
