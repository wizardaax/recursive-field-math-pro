"""
Tests for the RFF Evaluation API (eval_api.py).

Fixed-seed sequences are used throughout so results are reproducible.
"""

import math

import pytest

from recursive_field_math.eval_api import (
    MIN_LENGTH,
    PROFILE_NAME,
    calibration_report,
    score,
)

# ---------------------------------------------------------------------------
# Golden dataset: Fibonacci sequence (highly φ-coherent)
# ---------------------------------------------------------------------------
FIBONACCI = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
LUCAS = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123]

# Fixed-seed pseudo-random sequence (low φ-coherence expected)
import random as _random  # noqa: E402

_rng = _random.Random(42)
RANDOM_SEQ = [_rng.uniform(-10, 10) for _ in range(30)]


# ---------------------------------------------------------------------------
# Core success path tests
# ---------------------------------------------------------------------------


def test_score_fibonacci_ok():
    result = score(FIBONACCI, mode="numeric")
    assert result["ok"] is True
    assert result["profile"] == PROFILE_NAME
    assert result["mode"] == "numeric"
    assert result["n"] == len(FIBONACCI)
    assert 0.0 <= result["coherence"] <= 1.0
    assert 0.0 <= result["entropy"] <= 1.0
    assert 0.0 <= result["confidence"] <= 1.0


def test_score_lucas_ok():
    result = score(LUCAS, mode="numeric")
    assert result["ok"] is True
    assert result["n"] == len(LUCAS)


def test_score_tokens_mode():
    token_ids = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    result = score(token_ids, mode="tokens")
    assert result["ok"] is True
    assert result["mode"] == "tokens"


def test_score_actions_mode():
    actions = [0, 1, 0, 2, 1, 0, 3, 2, 1, 0, 3]
    result = score(actions, mode="actions")
    assert result["ok"] is True
    assert result["mode"] == "actions"


def test_score_profile_echoed():
    result = score(FIBONACCI, mode="numeric", profile=PROFILE_NAME)
    assert result["profile"] == PROFILE_NAME


# ---------------------------------------------------------------------------
# Fail-closed tests
# ---------------------------------------------------------------------------


def test_score_too_short_returns_not_ok():
    """Sequences shorter than MIN_LENGTH should be rejected."""
    short = [1, 2, 3]  # len < MIN_LENGTH (4)
    result = score(short)
    assert result["ok"] is False
    assert "too short" in result["reason"].lower()
    assert result["confidence"] == 0.0
    assert result["n"] == len(short)


def test_score_empty_returns_not_ok():
    result = score([])
    assert result["ok"] is False


def test_score_exactly_min_length():
    """MIN_LENGTH elements: may or may not pass depending on data, but must not crash."""
    seq = list(range(MIN_LENGTH))
    result = score(seq)
    # ok depends on confidence, but the call must always return a dict
    assert isinstance(result["ok"], bool)


def test_score_constant_sequence_low_confidence():
    """Constant sequences have no variance → confidence should be 0."""
    result = score([5, 5, 5, 5, 5, 5, 5, 5])
    assert result["ok"] is False
    assert result["confidence"] == 0.0


def test_score_invalid_profile():
    with pytest.raises(ValueError, match="Unknown profile"):
        score(FIBONACCI, profile="bad_profile")


def test_score_invalid_mode():
    with pytest.raises(ValueError, match="mode must be one of"):
        score(FIBONACCI, mode="invalid")


# ---------------------------------------------------------------------------
# Determinism test (fixed-seed reproducibility)
# ---------------------------------------------------------------------------


def test_score_is_deterministic():
    """Identical inputs must always produce identical outputs."""
    result_a = score(FIBONACCI, mode="numeric")
    result_b = score(FIBONACCI, mode="numeric")
    assert result_a == result_b


def test_random_seq_deterministic():
    r1 = score(RANDOM_SEQ, mode="numeric")
    r2 = score(RANDOM_SEQ, mode="numeric")
    assert r1 == r2


# ---------------------------------------------------------------------------
# φ-coherence direction test
# ---------------------------------------------------------------------------


def test_fibonacci_more_coherent_than_random():
    """Fibonacci sequence should have coherence >= that of white noise."""
    fib_result = score(FIBONACCI, mode="numeric")
    rnd_result = score(RANDOM_SEQ, mode="numeric")
    if fib_result["ok"] and rnd_result["ok"]:
        assert fib_result["coherence"] >= rnd_result["coherence"]


# ---------------------------------------------------------------------------
# calibration_report tests
# ---------------------------------------------------------------------------


def test_calibration_report_basic():
    sequences = [FIBONACCI, LUCAS, list(range(10, 25))]
    report = calibration_report(sequences)
    assert report["profile"] == PROFILE_NAME
    assert report["n_sequences"] == len(sequences)
    assert report["n_ok"] <= report["n_sequences"]
    assert "mean_coherence" in report
    assert "std_coherence" in report
    assert "mean_entropy" in report
    assert "mean_confidence" in report


def test_calibration_report_no_ok_sequences():
    """All short sequences → n_ok == 0, stats are NaN."""
    report = calibration_report([[1], [2], [1, 2]])
    assert report["n_ok"] == 0
    assert math.isnan(report["mean_coherence"])


def test_calibration_report_single_sequence():
    report = calibration_report([FIBONACCI])
    assert report["n_sequences"] == 1
