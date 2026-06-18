"""
thesis_report.py — Focused, thesis-grade analysis of the Article 10 compliance pipeline.

Reuses parsers/loaders from analyse.py. Produces a small, publication-ready set:

  thesis/tables/
    headline_f1.csv / .tex     macro P/R/F1 per (mode, model)
    per_model.csv  / .tex      ranked F1 per model (averaged across modes)
    per_mode.csv   / .tex      ranked F1 per mode  (averaged across models)
    ground_truth.csv           SHACL verdict per (doc, model, mode) vs gold

  thesis/figures/
    mode_boxplot.pdf           per-doc F1 distribution per mode
    obligation_heatmap.pdf     F1 per obligation × mode (where ground truth exists)
    ground_truth_grid.pdf      verdict match grid for the 3 synthetic cards
    latency_vs_f1.pdf          runtime vs accuracy trade-off (graphrag only counts un-cached runs)

  thesis/REPORT.md             text summary with the headline numbers

Usage:
    uv run python thesis_report.py
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analyse import (
    GROUND_TRUTH,
    OBLIGATION_GROUND_TRUTH,
    _apply_thesis_style,
    analyse_compliance,
    compute_precision_recall,
    parse_ttl_name,
    run_shacl,
)

REPO_ROOT = Path(__file__).parent
SHAPES    = REPO_ROOT / "shapes" / "article10-shapes.ttl"
# Configured at runtime by main(); defaults below.
OUTPUTS   = REPO_ROOT / "outputs"
THESIS    = REPO_ROOT / "thesis"
TABLES    = THESIS / "tables"
FIGURES   = THESIS / "figures"

MODES_ORDER  = ["graphrag", "graphrag_stripped", "bypass", "zeroshot"]
MODE_COLORS  = {"graphrag": "#1f77b4", "graphrag_stripped": "#aec7e8", "bypass": "#ff7f0e", "zeroshot": "#2ca02c"}


# ── Data loading ─────────────────────────────────────────────────────────────

def load_records() -> tuple[list[dict], list[dict], list[dict]]:
    """Return (compliance, shacl, diagnostics) record lists for all .ttl outputs."""
    compliance, shacl, diagnostics = [], [], []
    for ttl in sorted(OUTPUTS.glob("*.ttl")):
        rec = analyse_compliance(ttl)
        if rec:
            compliance.append(rec)
        if SHAPES.exists():
            shacl.append(run_shacl(ttl, SHAPES))
        diag_path = ttl.with_name(ttl.stem + "__diagnostics.json")
        if diag_path.exists():
            d = json.loads(diag_path.read_text())
            doc, model, mode = parse_ttl_name(ttl)
            d["document"] = doc
            d["model"]    = model
            d["mode"]     = mode
            diagnostics.append(d)
    return compliance, shacl, diagnostics


# ── Headline tables ──────────────────────────────────────────────────────────

def headline_table(pr_df: pd.DataFrame) -> pd.DataFrame:
    """Macro P/R/F1 per (mode, model), averaged over docs with ground truth."""
    g = (pr_df.groupby(["mode", "model"])[["precision", "recall", "f1"]]
              .agg(["mean", "std"])
              .round(3))
    g.columns = [f"{m}_{s}" for m, s in g.columns]
    g = g.reset_index().sort_values(["mode", "f1_mean"], ascending=[True, False])
    return g


def per_model_summary(pr_df: pd.DataFrame) -> pd.DataFrame:
    s = pr_df.groupby("model")[["precision", "recall", "f1"]].mean().round(3)
    return s.sort_values("f1", ascending=False).reset_index()


def per_mode_summary(pr_df: pd.DataFrame) -> pd.DataFrame:
    s = pr_df.groupby("mode")[["precision", "recall", "f1"]].mean().round(3)
    s = s.reindex([m for m in MODES_ORDER if m in s.index])
    return s.reset_index()


def df_to_latex(df: pd.DataFrame, path: Path, caption: str, label: str) -> None:
    """Minimal hand-rolled LaTeX table (avoids jinja2 dependency)."""
    def cell(v):
        if isinstance(v, float):
            return f"{v:.3f}"
        return str(v).replace("_", r"\_").replace("&", r"\&").replace("%", r"\%")
    cols = list(df.columns)
    lines = [
        "\\begin{table}[ht]",
        "\\centering",
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}",
        "\\begin{tabular}{" + "l" * len(cols) + "}",
        "\\toprule",
        " & ".join(cell(c) for c in cols) + " \\\\",
        "\\midrule",
    ]
    for _, row in df.iterrows():
        lines.append(" & ".join(cell(row[c]) for c in cols) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    path.write_text("\n".join(lines))


# ── Ground-truth verdict table for synthetic cards ───────────────────────────

def ground_truth_table(shacl: list[dict]) -> pd.DataFrame:
    rows = []
    for r in shacl:
        if r["document"] not in GROUND_TRUTH:
            continue
        gold     = GROUND_TRUTH[r["document"]]
        verdict  = r["conforms"]
        rows.append({
            "document": r["document"],
            "model":    r["model"],
            "mode":     r.get("mode", "graphrag"),
            "gold":     "compliant" if gold else "non-compliant",
            "verdict":  "compliant" if verdict else "non-compliant",
            "correct":  bool(gold) == bool(verdict),
        })
    return pd.DataFrame(rows)


# ── Plots ────────────────────────────────────────────────────────────────────

def plot_mode_boxplot(pr_df: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    data, labels, colors = [], [], []
    for mode in MODES_ORDER:
        sub = pr_df[pr_df["mode"] == mode]["f1"].values
        if len(sub):
            data.append(sub)
            labels.append(mode)
            colors.append(MODE_COLORS[mode])
    bp = ax.boxplot(data, labels=labels, patch_artist=True, widths=0.55, showfliers=True)
    for patch, c in zip(bp["boxes"], colors):
        patch.set_facecolor(c); patch.set_alpha(0.7)
    ax.set_ylabel("Per-document F1")
    ax.set_ylim(-0.02, 1.02)
    ax.set_title("F1 distribution by pipeline mode")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_obligation_heatmap(pr_df: pd.DataFrame, out: Path) -> None:
    """Mean F1 per (obligation, mode) — requires per-obligation P/R/F1 input."""
    if "obligation" not in pr_df.columns:
        return
    pivot = (pr_df.groupby(["obligation", "mode"])["f1"]
                  .mean()
                  .unstack("mode")
                  .reindex(columns=[m for m in MODES_ORDER if m in pr_df["mode"].unique()]))
    fig, ax = plt.subplots(figsize=(5.5, 4.8))
    im = ax.imshow(pivot.values, cmap="viridis", vmin=0, vmax=1, aspect="auto")
    ax.set_yticks(range(len(pivot.index))); ax.set_yticklabels(pivot.index)
    ax.set_xticks(range(len(pivot.columns))); ax.set_xticklabels(pivot.columns)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            v = pivot.values[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                        color="white" if v < 0.5 else "black", fontsize=7)
    fig.colorbar(im, ax=ax, label="F1")
    ax.set_title("F1 per obligation × mode")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_ground_truth_grid(gt_df: pd.DataFrame, out: Path) -> None:
    if gt_df.empty:
        return
    docs   = sorted(gt_df["document"].unique())
    models = sorted(gt_df["model"].unique())
    fig, axes = plt.subplots(1, len(MODES_ORDER), figsize=(2.8 * len(MODES_ORDER), 0.55 * len(models) + 1.5),
                             sharey=True)
    if len(MODES_ORDER) == 1:
        axes = [axes]
    for ax, mode in zip(axes, MODES_ORDER):
        sub = gt_df[gt_df["mode"] == mode]
        if sub.empty:
            ax.set_visible(False); continue
        mat = np.full((len(models), len(docs)), np.nan)
        for _, r in sub.iterrows():
            i = models.index(r["model"]); j = docs.index(r["document"])
            mat[i, j] = 1.0 if r["correct"] else 0.0
        ax.imshow(mat, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
        ax.set_xticks(range(len(docs)))
        ax.set_xticklabels([d.replace("model_card_", "") for d in docs], rotation=30, ha="right")
        ax.set_yticks(range(len(models))); ax.set_yticklabels(models)
        ax.set_title(mode)
    fig.suptitle("SHACL verdict vs ground truth (green=correct, red=wrong)")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_latency_vs_f1(pr_df: pd.DataFrame, diagnostics: list[dict], out: Path) -> None:
    diag_df = pd.DataFrame(diagnostics)
    if diag_df.empty:
        return
    # Drop graphrag runs that used the cache (their duration is bogus).
    def is_real(row):
        if row.get("mode") != "graphrag":
            return True
        steps = row.get("steps")
        if not isinstance(steps, dict):
            return True
        extr = steps.get("extraction") or {}
        return not extr.get("from_cache", False)
    diag_df = diag_df[diag_df.apply(is_real, axis=1)]
    if diag_df.empty:
        return
    diag_df = diag_df.rename(columns={"total_duration_s": "duration_s"})
    merged = pr_df.merge(diag_df[["document", "model", "mode", "duration_s"]],
                         on=["document", "model", "mode"], how="left").dropna(subset=["duration_s"])
    if merged.empty:
        return
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    for mode in MODES_ORDER:
        sub = merged[merged["mode"] == mode]
        if sub.empty: continue
        ax.scatter(sub["duration_s"], sub["f1"], alpha=0.6, s=22,
                   label=mode, color=MODE_COLORS[mode])
    ax.set_xscale("log")
    ax.set_xlabel("Total runtime (s, log scale)")
    ax.set_ylabel("F1 per document")
    ax.set_title("Latency vs accuracy")
    ax.legend(loc="lower right")
    ax.set_ylim(-0.02, 1.02)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


# ── Per-obligation P/R/F1 (extended from analyse.compute_precision_recall) ───

def compute_per_obligation_pr(compliance_records: list[dict]) -> pd.DataFrame:
    """Per-obligation P/R/F1 aggregated across docs with ground truth."""
    rows = []
    for rec in compliance_records:
        doc = rec["document"]
        gt  = OBLIGATION_GROUND_TRUTH.get(doc)
        if not gt:
            continue
        for section, obligations in gt.items():
            actual_section = rec.get(section, {})
            for ob, expected in obligations.items():
                pred = bool(actual_section.get(ob, False))
                rows.append({
                    "document":    doc,
                    "model":       rec["model"],
                    "mode":        rec.get("mode", "graphrag"),
                    "section":     section,
                    "obligation":  ob,
                    "tp": int(pred and expected),
                    "fp": int(pred and not expected),
                    "fn": int((not pred) and expected),
                    "tn": int((not pred) and (not expected)),
                })
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    agg = (df.groupby(["obligation", "mode"])[["tp", "fp", "fn"]].sum().reset_index())
    agg["precision"] = agg.apply(lambda r: r.tp / (r.tp + r.fp) if (r.tp + r.fp) else 0.0, axis=1)
    agg["recall"]    = agg.apply(lambda r: r.tp / (r.tp + r.fn) if (r.tp + r.fn) else 0.0, axis=1)
    agg["f1"] = agg.apply(lambda r: (2 * r.precision * r.recall / (r.precision + r.recall))
                          if (r.precision + r.recall) else 0.0, axis=1)
    return agg.round(3)


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Thesis-grade analysis of compliance pipeline outputs")
    parser.add_argument("--outputs-dir", type=Path, default=REPO_ROOT / "outputs",
                        help="Directory with *.ttl + *__diagnostics.json (default: outputs/)")
    parser.add_argument("--thesis-dir", type=Path, default=REPO_ROOT / "thesis",
                        help="Where to write tables/ and figures/ (default: thesis/)")
    args = parser.parse_args()

    global OUTPUTS, THESIS, TABLES, FIGURES
    OUTPUTS = args.outputs_dir
    THESIS  = args.thesis_dir
    TABLES  = THESIS / "tables"
    FIGURES = THESIS / "figures"

    _apply_thesis_style()
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    compliance, shacl, diagnostics = load_records()
    if not compliance:
        print("No compliance records found in outputs/")
        return

    pr_df = compute_precision_recall(compliance)
    if pr_df.empty:
        print("No documents with ground truth in outputs/ — cannot compute P/R/F1.")
        return

    # 1. headline table
    headline = headline_table(pr_df)
    headline.to_csv(TABLES / "headline_f1.csv", index=False)
    df_to_latex(headline, TABLES / "headline_f1.tex",
                "Macro precision/recall/F1 per pipeline mode and model.",
                "tab:headline")

    # 2. per-model + per-mode
    pm = per_model_summary(pr_df)
    pm.to_csv(TABLES / "per_model.csv", index=False)
    df_to_latex(pm, TABLES / "per_model.tex",
                "Mean precision/recall/F1 per model (averaged across modes).",
                "tab:per_model")

    pmode = per_mode_summary(pr_df)
    pmode.to_csv(TABLES / "per_mode.csv", index=False)
    df_to_latex(pmode, TABLES / "per_mode.tex",
                "Mean precision/recall/F1 per pipeline mode (averaged across models).",
                "tab:per_mode")

    # 3. ground-truth verdict
    gt_df = ground_truth_table(shacl)
    gt_df.to_csv(TABLES / "ground_truth.csv", index=False)

    # 4. per-obligation
    per_ob = compute_per_obligation_pr(compliance)
    if not per_ob.empty:
        per_ob.to_csv(TABLES / "per_obligation.csv", index=False)

    # ── Figures ──────────────────────────────────────────────────────────────
    plot_mode_boxplot(pr_df, FIGURES / "mode_boxplot.pdf")
    if not per_ob.empty:
        plot_obligation_heatmap(per_ob, FIGURES / "obligation_heatmap.pdf")
    plot_ground_truth_grid(gt_df, FIGURES / "ground_truth_grid.pdf")
    plot_latency_vs_f1(pr_df, diagnostics, FIGURES / "latency_vs_f1.pdf")

    # ── Text summary ─────────────────────────────────────────────────────────
    lines = []
    lines.append("# Thesis report — Article 10 compliance pipeline\n")
    lines.append(f"- Documents scored against ground truth: **{pr_df['document'].nunique()}**")
    lines.append(f"- Models: **{pr_df['model'].nunique()}**  ({', '.join(sorted(pr_df['model'].unique()))})")
    lines.append(f"- Modes: **{pr_df['mode'].nunique()}**   ({', '.join(sorted(pr_df['mode'].unique()))})\n")
    lines.append("## Headline — macro F1 per (mode, model)\n")
    lines.append(headline.to_string(index=False))
    lines.append("\n## Per-mode (averaged over models)\n")
    lines.append(pmode.to_string(index=False))
    lines.append("\n## Per-model (averaged over modes)\n")
    lines.append(pm.to_string(index=False))
    if not gt_df.empty:
        acc = gt_df.groupby("mode")["correct"].mean().round(3)
        lines.append("\n## SHACL verdict accuracy on synthetic test cards\n")
        lines.append(acc.to_string())
    (THESIS / "REPORT.md").write_text("\n".join(lines))

    print(f"Wrote: {TABLES}/  {FIGURES}/  {THESIS}/REPORT.md")


if __name__ == "__main__":
    main()
