"""
Tests for the φ-UCB Search module (phi_ucb.py).

Uses fixed seeds throughout for reproducibility.
"""

import math
import random

import pytest

from recursive_field_math.phi_ucb import (
    benchmark_phi_ucb_vs_ucb1,
    phi_ucb_score,
    select_best,
)

# ---------------------------------------------------------------------------
# phi_ucb_score core tests
# ---------------------------------------------------------------------------


def test_unvisited_node_returns_inf():
    """Unvisited nodes must always return +inf to guarantee exploration."""
    result = phi_ucb_score({"q": 0.0, "n": 0}, t=100)
    assert result == math.inf


def test_zero_t_returns_q():
    """When t==0 there are no simulations yet; score should equal q."""
    result = phi_ucb_score({"q": 0.75, "n": 5}, t=0)
    assert result == pytest.approx(0.75)


def test_basic_score_positive_bonus():
    """With n>0 and t>0, the bonus should be > 0 so score > q."""
    q = 0.5
    result = phi_ucb_score({"q": q, "n": 10}, t=100)
    assert result > q


def test_beta_zero_equals_ucb1():
    """With beta=0, phi^0 = 1 so phi_ucb should equal UCB1."""
    node = {"q": 0.5, "n": 10}
    t = 100
    alpha = 1.0
    phi_score = phi_ucb_score(node, t=t, alpha=alpha, beta=0.0)
    # UCB1 score = q + alpha * sqrt(ln(t)/n)
    ucb1_score = 0.5 + alpha * math.sqrt(math.log(100) / 10)
    assert phi_score == pytest.approx(ucb1_score, rel=1e-9)


def test_higher_beta_gives_higher_score():
    """A larger beta amplifies the exploration bonus."""
    node = {"q": 0.0, "n": 5}
    t = 50
    score_low_beta = phi_ucb_score(node, t=t, alpha=1.0, beta=0.0)
    score_high_beta = phi_ucb_score(node, t=t, alpha=1.0, beta=1.0)
    assert score_high_beta > score_low_beta


def test_invalid_t_raises():
    with pytest.raises(ValueError, match="t must be >= 0"):
        phi_ucb_score({"q": 0.0, "n": 1}, t=-1)


def test_invalid_alpha_raises():
    with pytest.raises(ValueError, match="alpha must be >= 0"):
        phi_ucb_score({"q": 0.0, "n": 1}, t=1, alpha=-0.1)


def test_missing_keys_raises():
    with pytest.raises(ValueError, match="'q' and 'n'"):
        phi_ucb_score({"q": 0.5}, t=10)


def test_negative_n_raises():
    with pytest.raises(ValueError, match="n must be >= 0"):
        phi_ucb_score({"q": 0.0, "n": -1}, t=10)


# ---------------------------------------------------------------------------
# select_best tests
# ---------------------------------------------------------------------------


def test_select_best_picks_highest_score():
    """The best node (highest q, adequate visits) should be selected."""
    children = [
        {"q": 0.9, "n": 5},
        {"q": 0.1, "n": 5},
        {"q": 0.5, "n": 5},
    ]
    idx = select_best(children, t=15, rng=random.Random(0))
    assert idx == 0  # first child has highest q


def test_select_best_prefers_unvisited():
    """Unvisited children (n=0) must always be selected over visited ones."""
    children = [
        {"q": 0.9, "n": 10},
        {"q": 0.0, "n": 0},  # unvisited → +inf
    ]
    idx = select_best(children, t=10, rng=random.Random(0))
    assert idx == 1


def test_select_best_empty_raises():
    with pytest.raises(ValueError, match="non-empty"):
        select_best([], t=10)


def test_select_best_tie_breaking_deterministic():
    """Ties should be broken by the supplied rng (deterministic)."""
    children = [{"q": 0.5, "n": 10}, {"q": 0.5, "n": 10}]
    idx_a = select_best(children, t=20, rng=random.Random(7))
    idx_b = select_best(children, t=20, rng=random.Random(7))
    assert idx_a == idx_b  # same seed → same choice


# ---------------------------------------------------------------------------
# benchmark_phi_ucb_vs_ucb1 tests
# ---------------------------------------------------------------------------


def test_benchmark_runs_and_returns_dict():
    result = benchmark_phi_ucb_vs_ucb1(n_arms=5, n_steps=50, seed=0)
    assert "phi_ucb_cumulative_reward" in result
    assert "ucb1_cumulative_reward" in result
    assert "phi_ucb_regret" in result
    assert "ucb1_regret" in result
    assert result["seed"] == 0
    assert result["n_arms"] == 5  # noqa: PLR2004
    assert result["n_steps"] == 50  # noqa: PLR2004


def test_benchmark_is_deterministic():
    r1 = benchmark_phi_ucb_vs_ucb1(n_arms=5, n_steps=100, seed=42)
    r2 = benchmark_phi_ucb_vs_ucb1(n_arms=5, n_steps=100, seed=42)
    assert r1["phi_ucb_cumulative_reward"] == r2["phi_ucb_cumulative_reward"]
    assert r1["ucb1_cumulative_reward"] == r2["ucb1_cumulative_reward"]


def test_benchmark_arm_means_count():
    result = benchmark_phi_ucb_vs_ucb1(n_arms=8, n_steps=20, seed=1)
    assert len(result["arm_means"]) == 8  # noqa: PLR2004


def test_benchmark_different_seeds_differ():
    r1 = benchmark_phi_ucb_vs_ucb1(n_arms=5, n_steps=100, seed=1)
    r2 = benchmark_phi_ucb_vs_ucb1(n_arms=5, n_steps=100, seed=2)
    # Different seeds should yield different arm means
    assert r1["arm_means"] != r2["arm_means"]
