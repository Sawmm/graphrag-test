"""
Derive gold labels from the clean, verbatim-restructured cards in
inputs/normalized/*_annex_iv.md and write gold/labels_normalized.csv.

These normalized cards contain NO compliance verdict table — they only
restructure the raw card text into the Annex IV skeleton, writing the literal
string "not provided" wherever the raw card says nothing about an obligation.

Decision rule (documentation-proxy, matches build_template.py):
    field has substantive text   → present = 1
    field is "not provided"/empty → present = 0

This is deterministic given the normalized cards, and is uncontaminated by any
satisfied/partial/not_satisfied judgment (those never appear in these files).

Output is loaded by analyse.py alongside the other gold/labels_*.csv. Because
"labels_normalized.csv" sorts after "labels_claude.csv", its values win over the
old (contaminated) claude rows for the same (document, section, obligation),
while synthetic-card rows that exist only in labels_claude.csv are preserved.

Usage:
    uv run python gold/build_labels_normalized.py
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

REPO       = Path(__file__).resolve().parent.parent
NORMALIZED = REPO / "inputs" / "normalized"
OUT        = REPO / "gold" / "labels_normalized.csv"

OBLIGATIONS: list[str] = [
    "design_choices", "provenance", "preprocessing", "assumptions",
    "suitability", "bias_examination", "bias_mitigation", "data_gap",
    "relevance", "representativeness", "statistical_props",
    "quality_metrics", "contextual_characteristics",
]
FIELDS = ["document", "dataset_section", "obligation",
          "present", "adequate", "notes", "annotator"]

# Section header number → dataset_section name. Section 1 (overview) and
# Section 5 (sensitive data) carry no per-obligation rows and are skipped.
SECTION_NUM = {"2": "training", "3": "validation", "4": "testing"}

EMPTY_VALUES = {"", "not provided", "n/a", "na", "tbd"}

_SECTION_RE = re.compile(r"^##\s+Section\s+(\d+)\b")
_OBLIG_RE   = re.compile(r"^###\s+\d+\.(\d+)\b")
_HR_RE      = re.compile(r"^-{3,}\s*$")  # markdown horizontal rule / section divider


def parse_card(text: str) -> dict[str, dict[str, int]]:
    """Return {section_name: {obligation_key: 1|0}} for one normalized card."""
    out: dict[str, dict[str, int]] = {}
    current_section: str | None = None
    current_ob: str | None = None
    buf: list[str] = []

    def flush() -> None:
        if current_section and current_ob is not None:
            body = "\n".join(buf).strip().lower()
            present = 0 if body in EMPTY_VALUES else 1
            out.setdefault(current_section, {})[current_ob] = present

    for line in text.splitlines():
        sec_m = _SECTION_RE.match(line)
        if sec_m:
            flush()
            current_section = SECTION_NUM.get(sec_m.group(1))
            current_ob, buf = None, []
            continue
        ob_m = _OBLIG_RE.match(line)
        if ob_m and current_section:
            flush()
            idx = int(ob_m.group(1)) - 1
            current_ob = OBLIGATIONS[idx] if 0 <= idx < len(OBLIGATIONS) else None
            buf = []
            continue
        if current_ob is not None and not _HR_RE.match(line):
            buf.append(line)
    flush()
    return out


def main() -> None:
    if not NORMALIZED.exists():
        raise SystemExit(f"missing dir: {NORMALIZED}")

    rows: list[dict] = []
    cards = sorted(NORMALIZED.glob("*_annex_iv.md"))
    for path in cards:
        doc = path.stem
        parsed = parse_card(path.read_text(encoding="utf-8"))
        for section in ("training", "validation", "testing"):
            verdicts = parsed.get(section, {})
            for ob in OBLIGATIONS:
                if ob not in verdicts:
                    continue
                rows.append({
                    "document":        doc,
                    "dataset_section": section,
                    "obligation":      ob,
                    "present":         verdicts[ob],
                    "adequate":        "",
                    "notes":           "",
                    "annotator":       "claude_normalized",
                })

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8-sig") as f:
        f.write("sep=,\n")
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows from {len(cards)} normalized cards")
    print(f"  → {OUT}")
    for path in cards:
        doc = path.stem
        n_present = sum(1 for r in rows if r["document"] == doc and r["present"] == 1)
        n_total   = sum(1 for r in rows if r["document"] == doc)
        print(f"  {doc}: {n_present}/{n_total} present")


if __name__ == "__main__":
    main()
