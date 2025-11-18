import json
import math
import os
import tempfile

from scripts.results_evaluator import (
    evaluate_acceptance_rules,
    evaluate_and_summarize_results,
    generate_summary_comment,
)


def test_evaluate_acceptance_rules_pass():
    """Test evaluation with all rules passing."""
    # Create a result that should pass all rules
    result = {
        "ok": True,
        "tag": "test_game",
        "moves": 20,
        "variance_reduction_pct": 85.5,  # ≥ 20% ✓
        "mae_improvement_pct": 5.2,  # ≥ 2% ✓
        # φ-clamp peak near 38.2° (0.666 rad)
        "theta_after_hist": (
            [-0.7, -0.6, -0.5, 0.5, 0.6, 0.65, 0.68, 0.7],  # edges
            [0, 0, 1, 1, 2, 5, 2, 0],  # hist - peak at 0.65 rad ≈ 37.2°
        ),
    }

    evaluation = evaluate_acceptance_rules(result)

    assert evaluation["verdict"] == "PASS"
    assert evaluation["variance_reduction_pass"] is True
    assert evaluation["mae_delta_pass"] is True
    assert evaluation["phi_clamp_peak_pass"] is True
    assert evaluation["overall_pass"] is True
    assert evaluation["variance_reduction_pct"] == 85.5
    assert evaluation["mae_improvement_pct"] == 5.2
    assert abs(evaluation["phi_clamp_peak_deg"] - 37.2) < 1.0  # approximately


def test_evaluate_acceptance_rules_check():
    """Test evaluation with some rules failing."""
    result = {
        "ok": True,
        "tag": "test_game",
        "moves": 20,
        "variance_reduction_pct": 15.0,  # < 20% ✗
        "mae_improvement_pct": 1.5,  # < 2% ✗
        "theta_after_hist": (
            [-0.7, -0.6, -0.5, 0.5, 0.6, 0.65, 0.68, 0.7],
            [0, 0, 1, 1, 2, 5, 2, 0],  # peak around 37.2° - this should pass
        ),
    }

    evaluation = evaluate_acceptance_rules(result)

    assert evaluation["verdict"] == "CHECK"
    assert evaluation["variance_reduction_pass"] is False
    assert evaluation["mae_delta_pass"] is False
    assert evaluation["phi_clamp_peak_pass"] is True
    assert evaluation["overall_pass"] is False


def test_evaluate_acceptance_rules_skip():
    """Test evaluation with failed result."""
    result = {"ok": False, "reason": "too short", "tag": "test_game"}

    evaluation = evaluate_acceptance_rules(result)

    assert evaluation["verdict"] == "SKIP"
    assert evaluation["reason"] == "too short"
    assert evaluation["overall_pass"] is False


def test_phi_clamp_peak_calculation():
    """Test φ-clamp peak degree calculation."""
    # Peak at exactly 0.666 rad should be ~38.2°
    result = {
        "ok": True,
        "variance_reduction_pct": 25.0,
        "mae_improvement_pct": 3.0,
        "theta_after_hist": (
            [0.6, 0.65, 0.67, 0.68, 0.7],  # edges
            [1, 2, 10, 2],  # hist - peak at bin centered on ~0.675 rad
        ),
    }

    evaluation = evaluate_acceptance_rules(result)

    # Peak bin center: (0.67 + 0.68) / 2 = 0.675 rad ≈ 38.7°
    expected_deg = math.degrees(0.675)
    assert abs(evaluation["phi_clamp_peak_deg"] - expected_deg) < 0.1
    # Should pass since 38.7° is within ±2° of 38.2°
    assert evaluation["phi_clamp_peak_pass"] is True


def test_generate_summary_comment():
    """Test summary comment generation."""
    results = [
        {
            "ok": True,
            "tag": "game_pass",
            "moves": 25,
            "variance_reduction_pct": 85.0,
            "mae_improvement_pct": 5.0,
            "theta_after_hist": ([0.6, 0.65, 0.67, 0.68, 0.7], [1, 2, 10, 2]),
        },
        {
            "ok": True,
            "tag": "game_check",
            "moves": 30,
            "variance_reduction_pct": 15.0,  # Fails
            "mae_improvement_pct": 1.0,  # Fails
            "theta_after_hist": ([0.6, 0.65, 0.67, 0.68, 0.7], [1, 2, 10, 2]),
        },
        {"ok": False, "reason": "too short", "tag": "game_skip", "moves": 5},
    ]

    summary = generate_summary_comment(results, lucas_weights=(4, 7, 11))

    # Check for key components
    assert "Codex Entropy-Pump Results" in summary
    assert "Lucas Weights:** (4, 7, 11)" in summary
    assert "**Overall Verdict:** ⚠️ **MIXED**" in summary
    assert "game_pass" in summary
    assert "game_check" in summary
    assert "game_skip" in summary
    assert "✅ PASS" in summary
    assert "⚠️ CHECK" in summary
    assert "⏭️ SKIP" in summary
    assert "Acceptance Rules" in summary


def test_generate_summary_comment_all_pass():
    """Test summary with all games passing."""
    results = [
        {
            "ok": True,
            "tag": "game1",
            "moves": 25,
            "variance_reduction_pct": 85.0,
            "mae_improvement_pct": 5.0,
            "theta_after_hist": ([0.6, 0.65, 0.67, 0.68, 0.7], [1, 2, 10, 2]),
        }
    ]

    summary = generate_summary_comment(results)

    assert "**Overall Verdict:** ✅ **PASS**" in summary


def test_evaluate_and_summarize_results():
    """Test loading results from JSON file and generating summary."""
    results = [
        {
            "ok": True,
            "tag": "test_game",
            "moves": 25,
            "variance_reduction_pct": 85.0,
            "mae_improvement_pct": 5.0,
            "theta_after_hist": ([0.6, 0.65, 0.67, 0.68, 0.7], [1, 2, 10, 2]),
        }
    ]

    # Create temporary JSON file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(results, f)
        temp_path = f.name

    try:
        summary = evaluate_and_summarize_results(temp_path, lucas_weights=(4, 7, 11))

        assert "Codex Entropy-Pump Results" in summary
        assert "Lucas Weights:** (4, 7, 11)" in summary
        assert "test_game" in summary

    finally:
        os.unlink(temp_path)


def test_evaluate_and_summarize_results_file_not_found():
    """Test handling of missing JSON file."""
    summary = evaluate_and_summarize_results("/nonexistent/file.json")

    assert "Error loading results" in summary
    assert "❌" in summary
