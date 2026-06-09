"""
Append empty annotation rows to gold/labels_sam.csv for any cards in
inputs/normalized/ that aren't yet present.

Idempotent — running twice is safe.

Usage:
    uv run python gold/append_normalized_template.py
"""
from __future__ import annotations

import csv
from pathlib import Path

REPO    = Path(__file__).resolve().parent.parent
INPUTS  = REPO / "inputs" / "normalized"
TARGET  = REPO / "gold" / "labels_sam.csv"

OBLIGATIONS = [
    "design_choices", "provenance", "preprocessing", "assumptions",
    "suitability", "bias_examination", "bias_mitigation", "data_gap",
    "relevance", "representativeness", "statistical_props",
    "quality_metrics", "contextual_characteristics",
]
SECTIONS = ["training", "validation", "testing"]


def main() -> None:
    existing_docs: set[str] = set()
    rows_existing: list[list[str]] = []
    header: list[str] | None = None
    bom_or_sep_line: str = ""

    if TARGET.exists():
        with TARGET.open(encoding="utf-8-sig") as f:
            first = f.readline()
            if first.lower().startswith("sep="):
                bom_or_sep_line = first
            else:
                # not a sep= line — that's actually the header, rewind
                f.seek(0)
            reader = csv.reader(f, delimiter=";")
            header = next(reader, None)
            for row in reader:
                rows_existing.append(row)
                if row:
                    existing_docs.add(row[0])

    cards = sorted(p.stem for p in INPUTS.iterdir()
                   if p.suffix.lower() in {".md", ".pdf"})
    to_add = [c for c in cards if c not in existing_docs]

    if not to_add:
        print("Nothing to add — labels_sam.csv already covers every normalized card.")
        return

    print(f"Adding {len(to_add)} cards × {len(SECTIONS)}×{len(OBLIGATIONS)} rows "
          f"= {len(to_add)*len(SECTIONS)*len(OBLIGATIONS)} new rows")
    for c in to_add:
        print(f"  + {c}")

    new_rows: list[list[str]] = []
    for card in to_add:
        for sec in SECTIONS:
            for ob in OBLIGATIONS:
                new_rows.append([card, sec, ob, "", "", "", ""])

    if header is None:
        header = ["document", "dataset_section", "obligation",
                  "present", "adequate", "notes", "annotator"]

    with TARGET.open("w", newline="", encoding="utf-8-sig") as f:
        if bom_or_sep_line:
            f.write(bom_or_sep_line)
        writer = csv.writer(f, delimiter=";")
        writer.writerow(header)
        writer.writerows(rows_existing + new_rows)

    print(f"\nWrote {len(rows_existing) + len(new_rows)} total rows → {TARGET}")


if __name__ == "__main__":
    main()
