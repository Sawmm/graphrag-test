"""
Generate an empty gold-standard label template from inputs/.

Output: gold/labels_template.csv

Annotator workflow:
    cp gold/labels_template.csv gold/labels_<your-initials>.csv
    Open in a spreadsheet. For each row fill:
        present   — 1 if any text in this section addresses this obligation,
                    else 0. Use the documentation-proxy definition: any
                    mention counts, even if the content is shallow.
        adequate  — 1 if a domain expert would say the documentation is
                    substantive (covers the obligation in spirit, not just
                    by name). Else 0. Leave blank when present=0.
        notes     — short free-text (line/quote reference) for audit.
        annotator — your initials.

Two annotators independently on ≥10 cards → compute Cohen's κ to confirm
the task is well-defined. <0.6 means the obligation definitions need
sharpening before running any model evaluation.
"""
from __future__ import annotations

import csv
from pathlib import Path

OBLIGATIONS: list[str] = [
    "design_choices",
    "provenance",
    "preprocessing",
    "assumptions",
    "suitability",
    "bias_examination",
    "bias_mitigation",
    "data_gap",
    "relevance",
    "representativeness",
    "statistical_props",
    "quality_metrics",
    "contextual_characteristics",
]

SECTIONS: list[str] = ["training", "validation", "testing"]

REPO    = Path(__file__).resolve().parent.parent
INPUTS  = REPO / "inputs"
OUT     = REPO / "gold" / "labels_template.csv"

FIELDS = ["document", "dataset_section", "obligation",
          "present", "adequate", "notes", "annotator"]


def main() -> None:
    cards = sorted(p.stem for p in INPUTS.iterdir()
                   if p.suffix.lower() in {".md", ".pdf"})

    rows = [
        {
            "document":         card,
            "dataset_section":  sec,
            "obligation":       ob,
            "present":          "",
            "adequate":         "",
            "notes":            "",
            "annotator":        "",
        }
        for card in cards
        for sec  in SECTIONS
        for ob   in OBLIGATIONS
    ]

    OUT.parent.mkdir(exist_ok=True)
    # utf-8-sig writes a BOM (required by Excel on Windows/Mac for non-ASCII)
    # and the leading "sep=," tells Excel to use comma even when the OS locale
    # default is semicolon (NL, DE, FR, ...). Pandas users read with
    # pd.read_csv(path, skiprows=1, encoding="utf-8-sig").
    with OUT.open("w", newline="", encoding="utf-8-sig") as f:
        f.write("sep=,\n")
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows ({len(cards)} cards × {len(SECTIONS)} sections × {len(OBLIGATIONS)} obligations)")
    print(f"  → {OUT}")


if __name__ == "__main__":
    main()
