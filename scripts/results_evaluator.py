"""
Results evaluator for Codex entropy-pump output.
Applies acceptance rules and generates summary comments.
"""

import math
from typing import Any

import numpy as np

# Acceptance rule thresholds (from README)
VARIANCE_REDUCTION_THRESHOLD = 20.0  # percent: minimum variance reduction to pass
MAE_DELTA_THRESHOLD = 2.0  # percent: minimum MAE improvement to pass
PHI_CLAMP_TARGET_DEG = 38.2  # degrees: expected φ-clamp peak angle
PHI_CLAMP_TOLERANCE_DEG = 2.0  # degrees: allowed deviation from PHI_CLAMP_TARGET_DEG


def evaluate_acceptance_rules(result: dict[str, Any]) -> dict[str, Any]:
    """
    Apply acceptance rules to entropy pump result.

    Acceptance Rules (from README):
    - Variance reduction ≥ 20%
    - MAE delta ≥ 2%
    - φ-clamp peak within ±2° of 38.2°

    Args:
        result: Single entropy pump result dict

    Returns:
        Dict with evaluation details and verdict
    """
    if not result.get("ok", False):
        return {
            "verdict": "SKIP",
            "reason": result.get("reason", "unknown"),
            "variance_reduction_pass": False,
            "mae_delta_pass": False,
            "phi_clamp_peak_pass": False,
            "overall_pass": False,
        }

    # Rule 1: Variance reduction ≥ 20%
    variance_reduction = result.get("variance_reduction_pct", 0)
    variance_reduction_pass = variance_reduction >= VARIANCE_REDUCTION_THRESHOLD

    # Rule 2: MAE delta ≥ 2%
    mae_improvement = result.get("mae_improvement_pct", 0)
    mae_delta_pass = mae_improvement >= MAE_DELTA_THRESHOLD

    # Rule 3: φ-clamp peak within ±2° of 38.2°
    # Need to find the peak in the histogram and convert to degrees
    phi_clamp_peak_pass = False
    phi_clamp_peak_deg = None

    if "theta_after_hist" in result:
        edges, hist = result["theta_after_hist"]
        if hist and len(hist) > 0:
            # Find the bin with maximum count
            peak_bin_idx = np.argmax(hist)

            # Calculate the center of the peak bin
            if peak_bin_idx < len(edges) - 1:
                bin_center_rad = (edges[peak_bin_idx] + edges[peak_bin_idx + 1]) / 2
                phi_clamp_peak_deg = abs(math.degrees(bin_center_rad))

                # Check if within ±PHI_CLAMP_TOLERANCE_DEG of PHI_CLAMP_TARGET_DEG
                phi_clamp_peak_pass = (
                    abs(phi_clamp_peak_deg - PHI_CLAMP_TARGET_DEG) <= PHI_CLAMP_TOLERANCE_DEG
                )

    # Overall pass: all three rules must pass
    overall_pass = variance_reduction_pass and mae_delta_pass and phi_clamp_peak_pass
    verdict = "PASS" if overall_pass else "CHECK"

    return {
        "verdict": verdict,
        "variance_reduction_pct": variance_reduction,
        "variance_reduction_pass": variance_reduction_pass,
        "mae_improvement_pct": mae_improvement,
        "mae_delta_pass": mae_delta_pass,
        "phi_clamp_peak_deg": phi_clamp_peak_deg,
        "phi_clamp_peak_pass": phi_clamp_peak_pass,
        "overall_pass": overall_pass,
    }


def generate_summary_comment(
    results: list[dict[str, Any]], lucas_weights: tuple = (4, 7, 11)
) -> str:
    """
    Generate a formatted summary comment for GitHub issue.

    Args:
        results: List of entropy pump results with evaluations
        lucas_weights: Lucas weights tuple used

    Returns:
        Formatted markdown comment string
    """
    if not results:
        return "❌ **No valid results generated**"

    # Evaluate each result
    evaluations = []
    for result in results:
        eval_result = evaluate_acceptance_rules(result)
        eval_result["tag"] = result.get("tag", "unknown")
        eval_result["moves"] = result.get("moves", 0)
        evaluations.append(eval_result)

    # Count passes and checks
    passes = sum(1 for e in evaluations if e["verdict"] == "PASS")
    checks = sum(1 for e in evaluations if e["verdict"] == "CHECK")
    skips = sum(1 for e in evaluations if e["verdict"] == "SKIP")

    # Overall verdict
    if passes > 0 and checks == 0 and skips == 0:
        overall_verdict = "✅ **PASS**"
    elif passes > 0:
        overall_verdict = "⚠️ **MIXED**"
    else:
        overall_verdict = "⚠️ **CHECK**"

    # Build comment
    lines = [
        "## 🧮 Codex Entropy-Pump Results",
        "",
        f"**Lucas Weights:** {lucas_weights}",
        f"**Overall Verdict:** {overall_verdict}",
        "",
    ]

    # Summary table
    lines.extend(
        [
            "| Game | Moves | Variance Reduction | MAE Delta | φ-Clamp Peak | Verdict |",
            "|------|-------|-------------------|-----------|--------------|---------|",
        ]
    )

    for eval_result in evaluations:
        tag = eval_result["tag"]
        moves = eval_result["moves"]

        if eval_result["verdict"] == "SKIP":
            lines.append(f"| {tag} | {moves} | - | - | - | ⏭️ SKIP |")
            continue

        # Format metrics with pass/fail indicators
        var_red = eval_result["variance_reduction_pct"]
        var_indicator = "✅" if eval_result["variance_reduction_pass"] else "❌"

        mae = eval_result["mae_improvement_pct"]
        mae_indicator = "✅" if eval_result["mae_delta_pass"] else "❌"

        phi_peak = eval_result.get("phi_clamp_peak_deg")
        if phi_peak is not None:
            phi_indicator = "✅" if eval_result["phi_clamp_peak_pass"] else "❌"
            phi_text = f"{phi_peak:.1f}° {phi_indicator}"
        else:
            phi_text = "N/A ❌"

        verdict_emoji = "✅" if eval_result["verdict"] == "PASS" else "⚠️"
        verdict_text = f"{verdict_emoji} {eval_result['verdict']}"

        lines.append(
            f"| {tag} | {moves} | {var_red:.1f}% {var_indicator} | "
            f"{mae:.1f}% {mae_indicator} | {phi_text} | {verdict_text} |"
        )

    # Acceptance criteria reminder
    lines.extend(
        [
            "",
            "### Acceptance Rules",
            "- Variance reduction ≥ **20%**",
            "- MAE delta ≥ **2%**",
            "- φ-clamp peak within **±2° of 38.2°**",
        ]
    )

    return "\n".join(lines)


def evaluate_and_summarize_results(
    results_json_path: str, lucas_weights: tuple = (4, 7, 11)
) -> str:
    """
    Load results from JSON file, evaluate against rules, and generate summary.

    Args:
        results_json_path: Path to entropy pump results JSON file
        lucas_weights: Lucas weights used

    Returns:
        Formatted summary comment string
    """
    import json

    try:
        with open(results_json_path, encoding="utf-8") as f:
            results = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"❌ **Error loading results:** {e}"

    if not isinstance(results, list):
        return "❌ **Invalid results format: expected list**"

    return generate_summary_comment(results, lucas_weights)
