"""
Inter-annotator agreement between Sam and Claude.

Computes:
  - Cohen's kappa (overall, per-section, per-obligation)
  - Confusion matrix (Sam vs Claude)
  - Per-document disagreement table (which obligations differ)

Usage:
    uv run python gold/agreement.py
"""
from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
SAM    = REPO / "gold" / "labels_sam.csv"
CLAUDE = REPO / "gold" / "labels_claude.csv"
OUT    = REPO / "thesis_ablation" / "agreement"


def load(path: Path) -> dict[tuple[str, str, str], int]:
    """Return {(doc, section, obligation): present} for filled rows only."""
    if not path.exists():
        return {}
    out: dict[tuple[str, str, str], int] = {}
    with path.open(encoding="utf-8-sig") as f:
        first = f.readline()
        if not first.lower().startswith("sep="):
            f.seek(0)
        if "\t" in first:
            delim = "\t"
        elif ";" in first and "," not in first.split(";")[0]:
            delim = ";"
        else:
            delim = ","
        reader = csv.DictReader(f, delimiter=delim)
        for row in reader:
            v = (row.get("present") or "").strip()
            if v not in ("0", "1"):
                continue
            out[(row["document"].strip(), row["dataset_section"].strip(),
                 row["obligation"].strip())] = int(v)
    return out


def cohen_kappa(a: list[int], b: list[int]) -> float:
    if not a or len(a) != len(b):
        return float("nan")
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    # marginals
    pa1 = sum(a) / n
    pb1 = sum(b) / n
    pe  = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    if pe == 1:
        return 1.0
    return (po - pe) / (1 - pe)


def main() -> None:
    sam, cl = load(SAM), load(CLAUDE)
    shared = sorted(set(sam) & set(cl))
    if not shared:
        print("No overlapping (doc, section, obligation) rows filled in both files.")
        print(f"  filled in sam:    {len(sam)}")
        print(f"  filled in claude: {len(cl)}")
        return

    OUT.mkdir(parents=True, exist_ok=True)

    s = [sam[k] for k in shared]
    c = [cl[k]  for k in shared]
    n = len(shared)
    agree = sum(x == y for x, y in zip(s, c))

    # Overall confusion
    tt = sum(1 for x, y in zip(s, c) if x == 1 and y == 1)
    tf = sum(1 for x, y in zip(s, c) if x == 1 and y == 0)
    ft = sum(1 for x, y in zip(s, c) if x == 0 and y == 1)
    ff = sum(1 for x, y in zip(s, c) if x == 0 and y == 0)

    overall_k = cohen_kappa(s, c)

    print(f"\n=== Overall agreement ({n} cells in both annotators) ===")
    print(f"  raw agreement : {agree}/{n} = {agree/n:.3f}")
    print(f"  Cohen's kappa : {overall_k:.3f}")
    # Landis & Koch (1977) thresholds
    interp = ("poor (<0)" if overall_k < 0
              else "slight (0.00-0.20)"   if overall_k <= 0.20
              else "fair (0.21-0.40)"     if overall_k <= 0.40
              else "moderate (0.41-0.60)" if overall_k <= 0.60
              else "substantial (0.61-0.80)" if overall_k <= 0.80
              else "almost perfect (>0.80)")
    print(f"  interpretation: {interp}")
    print()
    print("  Confusion matrix (rows=Sam, cols=Claude)")
    print(f"           Claude=0  Claude=1")
    print(f"  Sam=0    {ff:>8d}  {ft:>8d}")
    print(f"  Sam=1    {tf:>8d}  {tt:>8d}")

    # Per-section
    print("\n=== Per dataset section ===")
    rows = []
    for sec in ("training", "validation", "testing"):
        keys = [k for k in shared if k[1] == sec]
        if not keys: continue
        ss = [sam[k] for k in keys]
        cc = [cl[k]  for k in keys]
        ag = sum(x == y for x, y in zip(ss, cc)) / len(keys)
        k = cohen_kappa(ss, cc)
        rows.append({"section": sec, "n": len(keys), "agreement": round(ag, 3), "kappa": round(k, 3)})
    print(pd.DataFrame(rows).to_string(index=False))

    # Per-obligation
    print("\n=== Per obligation ===")
    rows = []
    by_ob: dict[str, tuple[list[int], list[int]]] = defaultdict(lambda: ([], []))
    for k in shared:
        by_ob[k[2]][0].append(sam[k])
        by_ob[k[2]][1].append(cl[k])
    for ob, (ss, cc) in sorted(by_ob.items()):
        ag = sum(x == y for x, y in zip(ss, cc)) / len(ss)
        rows.append({"obligation": ob, "n": len(ss),
                     "agreement": round(ag, 3), "kappa": round(cohen_kappa(ss, cc), 3)})
    df = pd.DataFrame(rows).sort_values("kappa")
    print(df.to_string(index=False))
    df.to_csv(OUT / "per_obligation.csv", index=False)

    # Per-document disagreement detail
    print("\n=== Disagreements per document ===")
    rows = []
    docs = sorted({k[0] for k in shared})
    for d in docs:
        d_keys = [k for k in shared if k[0] == d]
        diffs = [k for k in d_keys if sam[k] != cl[k]]
        rows.append({"document": d, "n_cells": len(d_keys),
                     "n_disagree": len(diffs), "pct": round(len(diffs) / len(d_keys) * 100, 1)})
    print(pd.DataFrame(rows).to_string(index=False))

    # Full disagreement listing
    diffs = [k for k in shared if sam[k] != cl[k]]
    if diffs:
        path = OUT / "disagreements.csv"
        with path.open("w", encoding="utf-8") as f:
            f.write("document,section,obligation,sam,claude\n")
            for k in diffs:
                f.write(f"{k[0]},{k[1]},{k[2]},{sam[k]},{cl[k]}\n")
        print(f"\n→ Full disagreement list: {path}  ({len(diffs)} rows)")


if __name__ == "__main__":
    main()
