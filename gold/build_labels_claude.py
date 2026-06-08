"""
Extract Annotator-1 / "Status" columns embedded in each input model card
and write gold/labels_claude.csv (same format as labels_sam.csv).

Decision rule (matches build_template.py documentation-proxy definition):
    satisfied | partial | yes  → present = 1
    not_satisfied | no | n/a   → present = 0
Rows skipped if no annotation table is found in the card.

Usage:
    uv run python gold/build_labels_claude.py
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

REPO    = Path(__file__).resolve().parent.parent
INPUTS  = REPO / "inputs"
OUT     = REPO / "gold" / "labels_claude.csv"

OBLIGATIONS: list[str] = [
    "design_choices", "provenance", "preprocessing", "assumptions",
    "suitability", "bias_examination", "bias_mitigation", "data_gap",
    "relevance", "representativeness", "statistical_props",
    "quality_metrics", "contextual_characteristics",
]
SECTIONS: list[str] = ["training", "validation", "testing"]

# Cards use "data_gaps" in some tables, "data_gap" in others — normalise.
KEY_ALIASES = {"data_gaps": "data_gap"}

POSITIVE = {"satisfied", "partial", "yes", "true", "1"}
NEGATIVE = {"not_satisfied", "not satisfied", "no", "false", "0", "n/a", "na"}


def parse_section_table(card_text: str, section: str) -> dict[str, int]:
    """Find the obligation table for the given dataset section and return key->1/0."""
    # Locate the section header in the Compliance Annotation block.
    header_pat = re.compile(rf"###\s+{section}\s+dataset\s+obligations", re.IGNORECASE)
    m = header_pat.search(card_text)
    if not m:
        return {}
    # Grab text until the next ### header.
    tail = card_text[m.end():]
    end = re.search(r"\n###\s", tail)
    block = tail[: end.start() if end else len(tail)]

    out: dict[str, int] = {}
    # Detect a "no testing dataset" catch-all row.
    if re.search(r"\(all\).+not[\s_]*satisfied.+no\s+testing\s+dataset", block, re.IGNORECASE):
        return {ob: 0 for ob in OBLIGATIONS}

    for line in block.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        ob_raw = cells[0].lower().replace(" ", "_")
        ob = KEY_ALIASES.get(ob_raw, ob_raw)
        if ob not in OBLIGATIONS:
            continue
        # Annotator-1 (real cards) is column index 2; "Status" (synthetic cards) is index 2.
        verdict_full = cells[2].lower().strip()
        # Drop trailing annotations like "satisfied [ADDED]" or "not_satisfied — reason".
        verdict = re.split(r"[\s\[\(—–-]", verdict_full, maxsplit=1)[0]
        v_under = verdict_full.replace(" ", "_")
        v_space = verdict_full.replace("_", " ")
        first_two = "_".join(verdict_full.replace("_", " ").split()[:2])
        if verdict in POSITIVE or v_under.startswith("satisfied") or v_space.startswith("satisfied") or v_under.startswith("partial"):
            out[ob] = 1
        elif (verdict in NEGATIVE or v_under.startswith("not_satisfied")
              or v_space.startswith("not satisfied") or first_two in NEGATIVE):
            out[ob] = 0
    return out


def main() -> None:
    # Fallback for cards without embedded annotation tables (e.g. compliant_one_out)
    try:
        import sys
        sys.path.insert(0, str(REPO))
        from analyse import OBLIGATION_GROUND_TRUTH  # type: ignore
    except Exception:
        OBLIGATION_GROUND_TRUTH = {}

    cards = sorted(p.stem for p in INPUTS.iterdir()
                   if p.suffix.lower() in {".md", ".pdf"})
    rows: list[dict] = []
    for stem in cards:
        path = INPUTS / f"{stem}.md"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        any_table = False
        for section in SECTIONS:
            verdicts = parse_section_table(text, section)
            if verdicts:
                any_table = True
            for ob in OBLIGATIONS:
                if ob not in verdicts:
                    continue
                rows.append({
                    "document":        stem,
                    "dataset_section": section,
                    "obligation":      ob,
                    "present":         verdicts[ob],
                    "adequate":        "",
                    "notes":           "",
                    "annotator":       "claude",
                })
        if not any_table and stem in OBLIGATION_GROUND_TRUTH:
            gt = OBLIGATION_GROUND_TRUTH[stem]
            for section in SECTIONS:
                for ob in OBLIGATIONS:
                    if ob in gt.get(section, {}):
                        rows.append({
                            "document":        stem,
                            "dataset_section": section,
                            "obligation":      ob,
                            "present":         int(bool(gt[section][ob])),
                            "adequate":        "",
                            "notes":           "fallback: analyse.OBLIGATION_GROUND_TRUTH",
                            "annotator":       "claude",
                        })

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8-sig") as f:
        f.write("sep=,\n")
        writer = csv.DictWriter(f, fieldnames=["document", "dataset_section",
                                               "obligation", "present", "adequate",
                                               "notes", "annotator"])
        writer.writeheader()
        writer.writerows(rows)

    docs = sorted({r["document"] for r in rows})
    print(f"Wrote {len(rows)} annotated rows from {len(docs)} cards")
    print(f"  → {OUT}")
    for d in docs:
        n = sum(1 for r in rows if r["document"] == d)
        print(f"  {d}: {n} rows")


if __name__ == "__main__":
    main()
