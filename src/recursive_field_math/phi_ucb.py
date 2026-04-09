"""
φ-Modulated Upper Confidence Bound (φ-UCB) search module.

Provides a drop-in replacement for the UCB1 action-selection formula used in
Monte Carlo Tree Search (MCTS) and similar bandit / planning frameworks:

    UCB1(i, t) = Q(i) + C × √(ln t / N(i))

This module replaces the constant exploration bonus with a φ-modulated one:

    φ-UCB(i, t) = Q(i) + α × φ^β × √(ln t / N(i))

where

    α   – base exploration coefficient (analogous to UCB1's C)
    β   – φ-exponent (scales the golden-ratio amplification)
    φ   – golden ratio ≈ 1.618 (imported from constants)

The golden-ratio amplification produces naturally hierarchical exploration
that mirrors Fibonacci/Lucas packing, which has been shown to improve
coverage in tree-structured search over uniform UCB1 on structured problems.

What φ-UCB does NOT guarantee
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- It does not guarantee faster convergence than UCB1 on arbitrary problems.
- It is NOT a Bayesian method; no posterior over rewards is maintained.
- The α and β hyper-parameters must be tuned per domain.

Fail-closed behaviour
~~~~~~~~~~~~~~~~~~~~~~
``phi_ucb_score`` returns ``+inf`` for unvisited nodes (``N=0``), guaranteeing
they are selected at least once before any visited node is re-selected.
Invalid inputs raise ``ValueError``.

Examples::

    >>> from recursive_field_math.phi_ucb import phi_ucb_score
    >>> phi_ucb_score({"q": 0.5, "n": 10}, t=100, alpha=1.0, beta=0.5)  # doctest: +ELLIPSIS
    1.0...
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from typing import Any

from .constants import PHI

# --------------------------------------------------------------------------- #
# Public constants
# --------------------------------------------------------------------------- #

DEFAULT_ALPHA: float = 1.0
DEFAULT_BETA: float = 0.5  # keeps φ^β ≈ 1.27, a gentle boost

# --------------------------------------------------------------------------- #
# Core scoring
# --------------------------------------------------------------------------- #


def phi_ucb_score(
    node_stats: dict[str, Any],
    t: int,
    alpha: float = DEFAULT_ALPHA,
    beta: float = DEFAULT_BETA,
) -> float:
    """
    Compute the φ-UCB score for a single node.

    Parameters
    ----------
    node_stats:
        Dict with keys:
        - ``"q"``  (float) – mean reward estimate for this node.
        - ``"n"``  (int)   – visit count for this node.
    t:
        Total number of simulations (parent visit count).
    alpha:
        Base exploration coefficient (≥ 0).
    beta:
        φ-exponent for the golden-ratio amplification (real number).

    Returns
    -------
    float – the φ-UCB score.  Higher is better (maximise to select).

    Raises
    ------
    ValueError
        If ``t < 0``, ``alpha < 0``, or ``node_stats`` is missing keys.

    Notes
    -----
    Unvisited nodes (``n == 0``) return ``+inf`` to guarantee they are
    selected at least once before any other node is re-visited.  This
    mirrors standard MCTS initialisation.

    What this metric means
    ~~~~~~~~~~~~~~~~~~~~~~
    The score balances exploitation (q term) with φ-modulated exploration
    (the bonus term).  It is a *heuristic* selection criterion; it does NOT
    represent a probability or a provable regret bound in general.

    Examples
    --------
    >>> phi_ucb_score({"q": 0.0, "n": 0}, t=1)
    inf
    >>> phi_ucb_score({"q": 0.5, "n": 5}, t=10, alpha=1.0, beta=0.0)  # β=0 → φ^0=1 → pure UCB1
    1.2...
    """
    if t < 0:
        raise ValueError(f"t must be >= 0, got {t}")
    if alpha < 0:
        raise ValueError(f"alpha must be >= 0, got {alpha}")
    if "q" not in node_stats or "n" not in node_stats:
        raise ValueError("node_stats must contain 'q' and 'n' keys")

    q = float(node_stats["q"])
    n = int(node_stats["n"])

    if n < 0:
        raise ValueError(f"node visit count n must be >= 0, got {n}")

    # Unvisited node: always select first
    if n == 0:
        return math.inf

    if t == 0:
        # No simulations run yet; exploration bonus is undefined – return q only.
        return q

    phi_mod: float = float(PHI**beta)
    bonus = alpha * phi_mod * math.sqrt(math.log(t) / n)
    return q + bonus


# --------------------------------------------------------------------------- #
# Batch selection (MCTS adapter)
# --------------------------------------------------------------------------- #


def select_best(
    children: Sequence[dict[str, Any]],
    t: int,
    alpha: float = DEFAULT_ALPHA,
    beta: float = DEFAULT_BETA,
    *,
    rng: random.Random | None = None,
) -> int:
    """
    Return the index of the child with the highest φ-UCB score.

    Ties are broken randomly using *rng* (or ``random`` module if None).

    Parameters
    ----------
    children:
        Sequence of node-stats dicts (each must have ``"q"`` and ``"n"``).
    t:
        Parent's visit count.
    alpha, beta:
        φ-UCB hyper-parameters forwarded to ``phi_ucb_score``.
    rng:
        Optional ``random.Random`` instance for reproducible tie-breaking.

    Returns
    -------
    int – index of the selected child.

    Raises
    ------
    ValueError
        If ``children`` is empty.

    Examples
    --------
    >>> import random
    >>> children = [{"q": 0.9, "n": 5}, {"q": 0.4, "n": 1}]
    >>> select_best(children, t=10, rng=random.Random(0))
    0
    """
    if not children:
        raise ValueError("children must be non-empty")

    scores = [phi_ucb_score(c, t=t, alpha=alpha, beta=beta) for c in children]
    best_score = max(scores)

    # Collect all indices that share the best score
    best_indices = [i for i, s in enumerate(scores) if s == best_score]

    _rng = rng or random.Random()
    return _rng.choice(best_indices)


# --------------------------------------------------------------------------- #
# Benchmark harness
# --------------------------------------------------------------------------- #


def benchmark_phi_ucb_vs_ucb1(
    n_arms: int = 10,
    n_steps: int = 1000,
    seed: int = 42,
    alpha: float = DEFAULT_ALPHA,
    beta: float = DEFAULT_BETA,
) -> dict[str, Any]:
    """
    Compare φ-UCB against UCB1 on a synthetic multi-arm bandit.

    The bandit arms have fixed reward means drawn from a seeded RNG.  Both
    algorithms start from the same blank state.  This harness is intentionally
    simple and deterministic for reproducibility.

    Parameters
    ----------
    n_arms:
        Number of bandit arms.
    n_steps:
        Number of pull steps to simulate.
    seed:
        RNG seed (fixed for reproducible benchmarks).
    alpha, beta:
        φ-UCB hyper-parameters.

    Returns
    -------
    dict with:
    - ``"phi_ucb_cumulative_reward"`` (float)
    - ``"ucb1_cumulative_reward"``    (float)
    - ``"phi_ucb_regret"``            (float) – vs optimal arm
    - ``"ucb1_regret"``               (float)
    - ``"arm_means"``                 (list[float])
    - ``"seed"``                      (int)
    - ``"n_arms"``                    (int)
    - ``"n_steps"``                   (int)

    What this means and does NOT mean
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    This benchmark uses Bernoulli-like arms (reward ~ N(μ, 0.1²)).  Results
    may not generalise to structured tree search problems.  A lower regret on
    this benchmark does NOT prove that φ-UCB is universally superior to UCB1.

    Examples
    --------
    >>> result = benchmark_phi_ucb_vs_ucb1(n_arms=5, n_steps=200, seed=0)
    >>> "phi_ucb_cumulative_reward" in result
    True
    >>> result["seed"]
    0
    """
    rng = random.Random(seed)
    arm_means = [rng.random() for _ in range(n_arms)]
    best_mean = max(arm_means)

    def _run(use_phi_ucb: bool) -> float:
        stats = [{"q": 0.0, "n": 0} for _ in range(n_arms)]
        total_reward = 0.0
        _r = random.Random(seed)  # separate stream for rewards (fixed)

        for step in range(1, n_steps + 1):
            t = step - 1
            if use_phi_ucb:
                chosen = select_best(
                    stats, t=t, alpha=alpha, beta=beta, rng=random.Random(step)
                )
            else:
                # UCB1: alpha=1.0, beta=0.0  (phi^0 = 1)
                chosen = select_best(
                    stats, t=t, alpha=alpha, beta=0.0, rng=random.Random(step)
                )

            reward = arm_means[chosen] + _r.gauss(0, 0.1)
            # Update running mean
            n_old = stats[chosen]["n"]
            q_old = stats[chosen]["q"]
            stats[chosen]["n"] += 1
            stats[chosen]["q"] = (q_old * n_old + reward) / stats[chosen]["n"]
            total_reward += reward

        return total_reward

    phi_reward = _run(use_phi_ucb=True)
    ucb1_reward = _run(use_phi_ucb=False)
    optimal_reward = best_mean * n_steps

    return {
        "phi_ucb_cumulative_reward": phi_reward,
        "ucb1_cumulative_reward": ucb1_reward,
        "phi_ucb_regret": optimal_reward - phi_reward,
        "ucb1_regret": optimal_reward - ucb1_reward,
        "arm_means": arm_means,
        "seed": seed,
        "n_arms": n_arms,
        "n_steps": n_steps,
    }
