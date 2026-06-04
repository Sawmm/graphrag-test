"""report.py — Generate a quick HTML overview of analysis results."""

from pathlib import Path
import pandas as pd
import json

ANALYSIS_DIR = Path(__file__).parent / "analysis"
OUT_FILE = ANALYSIS_DIR / "overview.html"

OBLIGATIONS = [
    "design_choices", "provenance", "preprocessing", "assumptions",
    "suitability", "bias_examination", "bias_mitigation", "data_gap",
    "relevance", "representativeness", "statistical_props",
    "quality_metrics", "contextual_characteristics",
]
SECTIONS = ["training", "validation", "testing"]


def load(name: str) -> pd.DataFrame:
    p = ANALYSIS_DIR / f"{name}.csv"
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


def badge(conforms: bool) -> str:
    if conforms:
        return '<span style="color:#27ae60;font-weight:bold">COMPLIANT ✓</span>'
    return '<span style="color:#c0392b;font-weight:bold">NON-COMPLIANT ✗</span>'


def cell(val: bool) -> str:
    color = "#27ae60" if val else "#e74c3c"
    symbol = "✓" if val else "✗"
    return f'<td style="text-align:center;background:{color};color:white;padding:4px 6px">{symbol}</td>'


def pct(v: float) -> str:
    color = "#27ae60" if v >= 90 else "#e67e22" if v >= 60 else "#c0392b"
    return f'<span style="color:{color};font-weight:bold">{v:.1f}%</span>'


def section_header(title: str) -> str:
    return f'<h2 style="margin-top:2em;border-bottom:2px solid #2c3e50;padding-bottom:6px;color:#2c3e50">{title}</h2>'


def build_html() -> str:
    shacl   = load("shacl_results")
    comp    = load("compliance_matrix")
    pr      = load("precision_recall")
    gt      = load("ground_truth_accuracy")
    missed  = load("missed_obligations")
    kg      = load("kg_metrics")

    parts = []
    parts.append("""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Compliance Pipeline Results</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 1200px; margin: 40px auto; padding: 0 20px; color: #2c3e50; }
  table { border-collapse: collapse; width: 100%; margin-bottom: 1.5em; font-size: 13px; }
  th { background: #2c3e50; color: white; padding: 6px 10px; text-align: left; }
  td { padding: 5px 10px; border-bottom: 1px solid #ddd; }
  tr:hover { background: #f8f9fa; }
  .run-label { font-size: 11px; color: #666; }
  h1 { color: #2c3e50; }
</style>
</head><body>
<h1>Compliance Pipeline — Results Overview</h1>
""")

    # ── 1. SHACL Verdicts ────────────────────────────────────────────────────
    parts.append(section_header("1. SHACL Verdicts"))
    if not shacl.empty:
        parts.append("<table><tr><th>Document</th><th>Model</th><th>Mode</th><th>Verdict</th><th>Violations</th></tr>")
        for _, r in shacl.iterrows():
            parts.append(
                f"<tr><td>{r['document']}</td><td>{r['model']}</td>"
                f"<td>{r.get('mode','graphrag')}</td>"
                f"<td>{badge(r['conforms'])}</td>"
                f"<td>{int(r['violation_count'])}</td></tr>"
            )
        parts.append("</table>")

    # ── 2. Precision / Recall / F1 ───────────────────────────────────────────
    parts.append(section_header("2. Obligation-Level Precision / Recall / F1"))
    if not pr.empty:
        parts.append("<table><tr><th>Document</th><th>Model</th><th>Mode</th>"
                     "<th>Precision</th><th>Recall</th><th>F1</th>"
                     "<th>TP</th><th>TN</th><th>FP</th><th>FN</th></tr>")
        for _, r in pr.iterrows():
            parts.append(
                f"<tr><td>{r['document']}</td><td>{r['model']}</td><td>{r['mode']}</td>"
                f"<td>{pct(r['precision']*100)}</td>"
                f"<td>{pct(r['recall']*100)}</td>"
                f"<td>{pct(r['f1']*100)}</td>"
                f"<td>{int(r['tp'])}</td><td>{int(r['tn'])}</td>"
                f"<td>{int(r['fp'])}</td><td>{int(r['fn'])}</td></tr>"
            )
        macro = pr[["precision","recall","f1"]].mean()
        parts.append(
            f"<tr style='font-weight:bold;background:#ecf0f1'>"
            f"<td colspan='3'>Macro average</td>"
            f"<td>{pct(macro['precision']*100)}</td>"
            f"<td>{pct(macro['recall']*100)}</td>"
            f"<td>{pct(macro['f1']*100)}</td>"
            f"<td colspan='4'></td></tr>"
        )
        parts.append("</table>")

    # ── 3. Per-obligation detection heatmap ──────────────────────────────────
    parts.append(section_header("3. Per-Obligation Detection Matrix"))
    if not comp.empty:
        ob_cols = [f"{s}.{o}" for s in SECTIONS for o in OBLIGATIONS if f"{s}.{o}" in comp.columns]
        parts.append("<div style='overflow-x:auto'><table>")
        parts.append("<tr><th>Document</th><th>Model</th><th>Mode</th>")
        for col in ob_cols:
            sec, ob = col.split(".", 1)
            parts.append(f'<th style="font-size:9px;writing-mode:vertical-rl;min-width:18px">{sec[:3]}.{ob[:6]}</th>')
        parts.append("<th>Rate</th></tr>")
        for _, r in comp.iterrows():
            parts.append(f"<tr><td>{r['document']}</td><td>{r['model']}</td><td>{r.get('mode','graphrag')}</td>")
            for col in ob_cols:
                parts.append(cell(bool(r.get(col, 0))))
            parts.append(f"<td>{pct(r['detection_rate_pct'])}</td></tr>")
        parts.append("</table></div>")

    # ── 4. Ground truth accuracy ─────────────────────────────────────────────
    parts.append(section_header("4. Ground Truth Verdict Accuracy"))
    if not gt.empty:
        summary = gt.groupby("model")[["correct","tp","tn","fp","fn"]].sum()
        summary["accuracy_%"] = (summary["correct"] / gt.groupby("model").size() * 100).round(1)
        parts.append("<table><tr><th>Model</th><th>Correct</th><th>TP</th><th>TN</th><th>FP</th><th>FN</th><th>Accuracy</th></tr>")
        for model, r in summary.iterrows():
            parts.append(
                f"<tr><td>{model}</td><td>{int(r['correct'])}</td>"
                f"<td>{int(r['tp'])}</td><td>{int(r['tn'])}</td>"
                f"<td>{int(r['fp'])}</td><td>{int(r['fn'])}</td>"
                f"<td>{pct(r['accuracy_%'])}</td></tr>"
            )
        parts.append("</table>")

    # ── 5. Most missed obligations ───────────────────────────────────────────
    parts.append(section_header("5. Most Frequently Missed Obligations (top 10)"))
    if not missed.empty:
        top = missed.head(10)
        parts.append("<table><tr><th>Obligation</th><th>Missed</th><th>Total runs</th><th>Miss rate</th></tr>")
        for _, r in top.iterrows():
            parts.append(
                f"<tr><td>{r['obligation']}</td><td>{int(r['missed'])}</td>"
                f"<td>{int(r['total_runs'])}</td><td>{pct(r['miss_rate_pct'])}</td></tr>"
            )
        parts.append("</table>")

    # ── 6. KG Quality ────────────────────────────────────────────────────────
    parts.append(section_header("6. Knowledge Graph Quality"))
    if not kg.empty:
        parts.append("<table><tr><th>Document</th><th>Model</th><th>Entity Nodes</th>"
                     "<th>Schema Nodes</th><th>Schema %</th><th>Content Rels</th></tr>")
        for _, r in kg.iterrows():
            parts.append(
                f"<tr><td>{r['document']}</td><td>{r['model']}</td>"
                f"<td>{int(r['entity_nodes'])}</td><td>{int(r['schema_nodes'])}</td>"
                f"<td>{pct(r['schema_compliance_pct'])}</td>"
                f"<td>{int(r['content_rels'])}</td></tr>"
            )
        parts.append("</table>")

    parts.append("</body></html>")
    return "\n".join(parts)


if __name__ == "__main__":
    html = build_html()
    OUT_FILE.write_text(html, encoding="utf-8")
    print(f"Saved: {OUT_FILE}")
