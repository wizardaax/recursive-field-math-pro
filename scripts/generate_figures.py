#!/usr/bin/env python3
"""
Generate publication figures for RFF φ-modulation verification.

Outputs:
- nodes_vs_entropy.{png|pdf|svg}
- phi_scale_invariance.{png|pdf|svg}
- radar_metrics.{png|pdf|svg}
- coherence_scale.{png|pdf|svg}
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

WATERMARK = "RFF φ-Mod Verification — wizardaax"

CONFIGS = ["Baseline", "φ-mod", "Scheduler", "Combined"]
COLORS_LIGHT = ["#444444", "#008000", "#FFA500", "#1E90FF"]
COLORS_DARK = ["#888888", "#00FF00", "#FFA500", "#1E90FF"]

# Means from verification summary
NODES = np.array([232.2, 225.8, 231.2, 227.8])
COVERAGE_ENTROPY = np.array([1.1426, 1.2902, 1.1993, 1.1818])
BRANCHING = np.array([4.644, 4.516, 4.624, 4.556])
DEPTH = np.array([2.772, 2.676, 2.736, 2.744])
NODES_PER_SIM = np.array([4.644, 4.516, 4.624, 4.556])

# Standard deviations from summary (trial-level)
STD_NODES = np.array([3.1, 2.5, 3.0, 2.8])
STD_ENTROPY = np.array([0.021, 0.019, 0.022, 0.020])

# t-critical for 95% CI, df=4
T_CRIT_DF4_95 = 2.776
N_TRIALS = 5
CI_MULT = T_CRIT_DF4_95 / np.sqrt(N_TRIALS)


def apply_theme(theme: str) -> list[str]:
    if theme == "dark":
        plt.style.use("dark_background")
        return COLORS_DARK
    plt.style.use("default")
    return COLORS_LIGHT


def save(fig: plt.Figure, outdir: Path, name: str, fmt: str) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(outdir / f"{name}.{fmt}", dpi=300 if fmt == "png" else None)
    plt.close(fig)


def fig_nodes_vs_entropy(outdir: Path, fmt: str, colors: list[str]) -> None:
    fig = plt.figure(figsize=(7, 5))
    ax = fig.add_subplot(111)

    xerr = STD_NODES * CI_MULT
    yerr = STD_ENTROPY * CI_MULT

    for i, cfg in enumerate(CONFIGS):
        ax.errorbar(
            NODES[i],
            COVERAGE_ENTROPY[i],
            xerr=xerr[i],
            yerr=yerr[i],
            fmt="o",
            color=colors[i],
            capsize=5,
            label=cfg,
        )

    ax.set_xlabel("Nodes (mean)")
    ax.set_ylabel("Coverage Entropy (mean)")
    ax.set_title("Nodes vs Coverage Entropy (95% CI)")
    ax.grid(alpha=0.6, linestyle="--")
    ax.legend()

    ax.annotate(
        "φ-mod Optimal",
        xy=(NODES[1], COVERAGE_ENTROPY[1]),
        xytext=(NODES[1] + 2.2, COVERAGE_ENTROPY[1] + 0.02),
        arrowprops={"arrowstyle": "->", "lw": 2},
    )
    ax.text(
        0.5,
        -0.15,
        WATERMARK,
        fontsize=8,
        color="gray",
        ha="center",
        transform=ax.transAxes,
    )
    save(fig, outdir, "nodes_vs_entropy", fmt)


def fig_scale_invariance(outdir: Path, fmt: str) -> None:
    n_values = np.array([1e3, 1e4, 1e5, 1e6])
    collision_precise = np.zeros_like(n_values)
    collision_quantized = np.array([14.8, 58.3, 85.0, 99.59])

    fig = plt.figure(figsize=(7, 5))
    ax = fig.add_subplot(111)
    ax.plot(n_values, collision_precise, marker="o", color="green", label="Precise φ")
    ax.plot(
        n_values,
        collision_quantized,
        marker="s",
        color="red",
        label="Quantized φ ≈ 1.618",
    )
    ax.fill_between(
        n_values,
        collision_quantized,
        100,
        color="red",
        alpha=0.2,
        label="Catastrophic zone",
    )
    ax.set_xscale("log")
    ax.set_ylim(0, 105)
    ax.set_xlabel("Scale N (log)")
    ax.set_ylabel("Collision Rate (%)")
    ax.set_title("Scale Invariance: Fractional {nφ mod 1}")
    ax.grid(alpha=0.6, linestyle="--")
    ax.legend()
    ax.text(
        0.5,
        -0.15,
        WATERMARK,
        fontsize=8,
        color="gray",
        ha="center",
        transform=ax.transAxes,
    )
    save(fig, outdir, "phi_scale_invariance", fmt)


def normalize_for_radar() -> np.ndarray:
    arr = np.zeros((len(CONFIGS), 5))
    arr[:, 0] = (NODES.max() - NODES) / (NODES.max() - NODES.min())
    arr[:, 1] = (COVERAGE_ENTROPY - COVERAGE_ENTROPY.min()) / (
        COVERAGE_ENTROPY.max() - COVERAGE_ENTROPY.min()
    )
    arr[:, 2] = (BRANCHING.max() - BRANCHING) / (BRANCHING.max() - BRANCHING.min())
    arr[:, 3] = (DEPTH.max() - DEPTH) / (DEPTH.max() - DEPTH.min())
    arr[:, 4] = (NODES_PER_SIM.max() - NODES_PER_SIM) / (
        NODES_PER_SIM.max() - NODES_PER_SIM.min()
    )
    return arr


def fig_radar(outdir: Path, fmt: str, colors: list[str]) -> None:
    metrics = ["Nodes", "Coverage Entropy", "Branching", "Depth", "Nodes/Sim"]
    num_metrics = len(metrics)
    angles = np.linspace(0, 2 * np.pi, num_metrics, endpoint=False).tolist()
    angles += angles[:1]

    normalized = normalize_for_radar()

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, polar=True)

    for i, cfg in enumerate(CONFIGS):
        values = normalized[i].tolist()
        values += values[:1]
        ax.plot(angles, values, color=colors[i], linewidth=2, label=cfg)
        ax.fill(angles, values, color=colors[i], alpha=0.1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics)
    ax.set_yticklabels([])
    ax.set_title("Multi-Metric Radar (normalized)")
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    ax.text(
        0.5,
        -0.15,
        WATERMARK,
        fontsize=8,
        color="gray",
        ha="center",
        transform=ax.transAxes,
    )
    save(fig, outdir, "radar_metrics", fmt)


def fig_coherence(outdir: Path, fmt: str) -> None:
    labels = ["Random Noise", "Human Play", "Superhuman AI"]
    coherence = [0.9, 29.0, 42.0]
    colors = ["#888888", "#1E90FF", "#008000"]

    fig = plt.figure(figsize=(7, 5))
    ax = fig.add_subplot(111)
    ax.bar(labels, coherence, color=colors)
    ax.set_ylabel("Entropy Reduction (%)")
    ax.set_title("Coherence Scale")
    ax.set_ylim(0, 50)
    ax.grid(alpha=0.3, linestyle="--", axis="y")
    ax.text(
        0.5,
        -0.15,
        WATERMARK,
        fontsize=8,
        color="gray",
        ha="center",
        transform=ax.transAxes,
    )
    save(fig, outdir, "coherence_scale", fmt)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--theme", choices=["dark", "light"], default="light")
    p.add_argument("--format", choices=["png", "pdf", "svg"], default="png")
    p.add_argument("--outdir", type=Path, default=Path("paper/figures"))
    return p.parse_args()


def main() -> None:
    args = parse_args()
    colors = apply_theme(args.theme)
    fig_nodes_vs_entropy(args.outdir, args.format, colors)
    fig_scale_invariance(args.outdir, args.format)
    fig_radar(args.outdir, args.format, colors)
    fig_coherence(args.outdir, args.format)
    print(f"Generated figures in {args.outdir} as .{args.format} (theme={args.theme})")


if __name__ == "__main__":
    main()
