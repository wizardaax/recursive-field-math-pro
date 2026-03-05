import math

import numpy as np

from scripts.codex_entropy_pump import (
    PHI,
    _rank_to_phase,
    codex_pump_from_series,
    golden_refraction,
)


def test_phi_clamp_invariant():
    rng = np.random.default_rng(7)
    x = rng.normal(size=5000)  # synthetic chaos
    th = _rank_to_phase(x)
    thp = golden_refraction(th, PHI)
    clamp = math.asin(1.0 / PHI)
    # histogram peak near ±clamp (~0.666 rad)
    hist, _ = np.histogram(thp, bins=60, range=(-math.pi / 2, math.pi / 2))
    peak = np.argmax(hist)
    centers = np.linspace(-math.pi / 2, math.pi / 2, 60, endpoint=False) + (math.pi / 60)
    assert abs(abs(centers[peak]) - clamp) < 0.1


def test_codex_pump_basic():
    # Test with synthetic evaluation series
    rng = np.random.default_rng(42)
    evals = np.cumsum(rng.normal(0, 50, 50))  # random walk evaluation

    result = codex_pump_from_series(evals, window=(5, 25))

    assert result["ok"]
    assert "variance_reduction_pct" in result
    assert "compression" in result
    assert "phi_clamp_rad" in result
    assert abs(result["phi_clamp_rad"] - math.asin(1.0 / PHI)) < 1e-10


def test_codex_pump_edge_cases():
    # Test too short series
    short_series = np.array([1, 2, 3])
    result = codex_pump_from_series(short_series)
    assert not result["ok"]
    assert result["reason"] == "too short"

    # Test zero variance
    zero_var = np.array([5, 5, 5, 5, 5])
    result = codex_pump_from_series(zero_var)
    assert not result["ok"]
    assert result["reason"] == "zero variance"


def test_lucas_weights():
    # Test Lucas weights functionality
    rng = np.random.default_rng(42)
    evals = np.cumsum(rng.normal(0, 50, 50))

    # Test with (4,7,11) Lucas weights as mentioned in the problem
    result_lucas = codex_pump_from_series(evals, window=(5, 25), lucas_weights=(4, 7, 11))
    result_normal = codex_pump_from_series(evals, window=(5, 25))

    assert result_lucas["ok"]
    assert result_normal["ok"]

    # The compression and variance reduction should be different with Lucas weights
    assert result_lucas["compression"] != result_normal["compression"]
    assert result_lucas["variance_reduction_pct"] != result_normal["variance_reduction_pct"]
