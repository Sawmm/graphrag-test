"""
Side-by-side comparison of two thesis_report runs.

Outputs:
  thesis_ablation/headline_diff.csv   — F1 delta per (mode, model)
  thesis_ablation/per_mode_diff.csv   — F1 delta per mode (avg over models)

Usage:
    uv run python compare_ablation.py \
        --baseline thesis_normalized --variant thesis_noprune \
        --baseline-label pruned     --variant-label noprune
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def headline(thesis_dir: Path) -> pd.DataFrame:
    p = thesis_dir / "tables" / "headline_f1.csv"
    if not p.exists():
        raise FileNotFoundError(p)
    df = pd.read_csv(p)
    return df[["mode", "model", "precision_mean", "recall_mean", "f1_mean"]]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", type=Path, required=True)
    ap.add_argument("--variant",  type=Path, required=True)
    ap.add_argument("--baseline-label", default="baseline")
    ap.add_argument("--variant-label",  default="variant")
    ap.add_argument("--out", type=Path, default=Path("thesis_ablation"))
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    b = headline(args.baseline).rename(columns={
        "precision_mean": f"P_{args.baseline_label}",
        "recall_mean":    f"R_{args.baseline_label}",
        "f1_mean":        f"F1_{args.baseline_label}",
    })
    v = headline(args.variant).rename(columns={
        "precision_mean": f"P_{args.variant_label}",
        "recall_mean":    f"R_{args.variant_label}",
        "f1_mean":        f"F1_{args.variant_label}",
    })
    m = b.merge(v, on=["mode", "model"], how="outer")
    m["F1_delta"] = m[f"F1_{args.variant_label}"] - m[f"F1_{args.baseline_label}"]
    m = m.sort_values(["mode", "F1_delta"], ascending=[True, False]).round(3)
    m.to_csv(args.out / "headline_diff.csv", index=False)

    pm = (m.groupby("mode")[[f"F1_{args.baseline_label}", f"F1_{args.variant_label}", "F1_delta"]]
            .mean().round(3).reset_index())
    pm.to_csv(args.out / "per_mode_diff.csv", index=False)

    print("=== Per (mode, model) ===")
    print(m.to_string(index=False))
    print("\n=== Per mode (avg over models) ===")
    print(pm.to_string(index=False))
    print(f"\nSaved to {args.out}/")


if __name__ == "__main__":
    main()
