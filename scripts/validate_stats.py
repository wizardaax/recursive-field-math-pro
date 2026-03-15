#!/usr/bin/env python3
"""
Validate and print summary statistics from ablation CSV.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

T_CRIT_DF4_95 = 2.776
N_TRIALS_EXPECTED = 5


def main() -> None:
    csv_path = Path("paper/data/ablation_metrics.csv")
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing input file: {csv_path}")

    df = pd.read_csv(csv_path)

    required = {
        "config",
        "trial",
        "nodes",
        "coverage_entropy",
        "branching",
        "depth",
        "nodes_per_sim",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    grouped = df.groupby("config", sort=False)
    print("Config statistics (mean ± std, 95% CI half-width):")
    print("--------------------------------------------------")

    for cfg, g in grouped:
        n = len(g)
        if n != N_TRIALS_EXPECTED:
            print(f"[WARN] {cfg}: expected {N_TRIALS_EXPECTED} trials, got {n}")

        print(f"\n[{cfg}]")
        for col in ["nodes", "coverage_entropy", "branching", "depth", "nodes_per_sim"]:
            mean = g[col].mean()
            std = g[col].std(ddof=1)
            ci = (T_CRIT_DF4_95 * std / np.sqrt(n)) if n > 1 else np.nan
            print(f"  {col:18s} mean={mean:.6f} std={std:.6f} ci95=±{ci:.6f}")


if __name__ == "__main__":
    main()
