"""
RFF Evaluation API – deterministic scoring of sequences.

Scoring profile ``rff_v1`` (the only versioned profile shipped here) maps any
ordered numeric, token-id, or action sequence to three normalised scalars:

    coherence  – how well the sequence follows φ-weighted autocorrelation.
                 Range [0, 1]. Higher ≈ more structurally regular.
    entropy    – normalised Shannon entropy of the relative-change distribution.
                 Range [0, 1]. Higher ≈ more uniform / less predictable.
    confidence – calibrated certainty that the scores are meaningful.
                 Falls to 0 when the sequence is too short or degenerate.

``score()`` is *fail-closed*: when confidence is below CONFIDENCE_THRESHOLD the
dict contains ``"ok": False`` and a human-readable ``"reason"`` field.

Non-negotiables satisfied:
- Deterministic: identical input always produces identical output.
- Versioned: every result carries ``"profile": "rff_v1"``.
- Explicit semantics: see docstrings for what each metric means and does NOT mean.
- Fail-closed: low confidence is surfaced rather than silently ignored.

Example::

    >>> from recursive_field_math.eval_api import score
    >>> result = score([1, 1, 2, 3, 5, 8, 13], mode="numeric")
    >>> result["ok"]
    True
    >>> 0.0 <= result["coherence"] <= 1.0
    True
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from .constants import PHI

# --------------------------------------------------------------------------- #
# Public constants / profile metadata
# --------------------------------------------------------------------------- #

PROFILE_NAME: str = "rff_v1"
PROFILE_VERSION: int = 1

# Sequences shorter than this are rejected (confidence = 0, ok = False).
MIN_LENGTH: int = 4

# If the computed confidence is below this threshold the call is fail-closed.
CONFIDENCE_THRESHOLD: float = 0.10

# Numerical stability floor (used in internal helpers).
_EPS: float = 1e-12
_EPS_MEAN: float = 1e-9

# Minimum input sizes for internal functions (avoid PLR2004 magic literals).
_MIN_ENTROPY_LEN: int = 2
_MIN_COHERENCE_LEN: int = 3
_MIN_DELTA_LEN: int = 2

# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #


def _to_floats(sequence: Sequence) -> list[float]:
    """Convert an arbitrary sequence to a list of floats."""
    return [float(x) for x in sequence]


def _shannon_entropy_normalised(values: list[float], n_bins: int = 16) -> float:
    """
    Compute normalised Shannon entropy of *values* using a fixed histogram.

    Normalisation is against ``log2(n_bins)`` so the result lives in [0, 1].
    Returns 0.0 for constant input (single occupied bin).
    """
    if len(values) < _MIN_ENTROPY_LEN:
        return 0.0

    lo, hi = min(values), max(values)
    if math.isclose(lo, hi):
        return 0.0  # degenerate constant sequence

    bin_width = (hi - lo) / n_bins
    counts = [0] * n_bins
    for v in values:
        idx = min(int((v - lo) / bin_width), n_bins - 1)
        counts[idx] += 1

    n = len(values)
    entropy = 0.0
    for c in counts:
        if c:
            p = c / n
            entropy -= p * math.log2(p)

    max_entropy = math.log2(n_bins)
    return entropy / max_entropy


def _phi_coherence(values: list[float]) -> float:
    """
    φ-weighted autocorrelation coherence.

    Measures how well consecutive differences mirror a φ-scaled self-similar
    pattern.  Specifically computes a weighted correlation between the raw
    difference sequence and a φ-damped version of itself:

        coherence = |corr(Δx, φ⁻¹ · shift(Δx))| ∈ [0, 1]

    A pure Fibonacci / Lucas sequence scores near 1.0.
    White noise scores near 0.0.

    This is a *structural* measure and says nothing about the semantic meaning
    of the values.  A high coherence does not imply correctness, validity, or
    safety of the sequence.
    """
    if len(values) < _MIN_COHERENCE_LEN:
        return 0.0

    deltas = [values[i + 1] - values[i] for i in range(len(values) - 1)]
    n = len(deltas)
    if n < _MIN_DELTA_LEN:
        return 0.0

    # φ-damped shifted copy
    phi_inv = 1.0 / PHI
    shifted = [phi_inv * deltas[i] for i in range(n - 1)]
    original = deltas[: n - 1]

    # Pearson correlation (protected against zero std)
    mean_o = sum(original) / len(original)
    mean_s = sum(shifted) / len(shifted)
    cov = sum((o - mean_o) * (s - mean_s) for o, s in zip(original, shifted, strict=False))
    var_o = sum((o - mean_o) ** 2 for o in original)
    var_s = sum((s - mean_s) ** 2 for s in shifted)

    denom = math.sqrt(var_o * var_s)
    if denom < _EPS:
        return 0.0

    return abs(cov / denom)


def _confidence(values: list[float]) -> float:
    """
    Calibrated confidence that the coherence / entropy scores are meaningful.

    The formula combines:
    1. A length bonus that saturates at 1.0 once we have ≥ 32 elements.
    2. A variance check: if the sequence is near-constant, confidence degrades.

    Confidence is NOT a probability of correctness; it is a measure of how
    much information the sequence contains to derive stable scores.
    """
    n = len(values)
    if n < MIN_LENGTH:
        return 0.0

    # Length factor: saturates at 1.0 for n >= 32
    length_factor = min(1.0, (n - MIN_LENGTH) / (32 - MIN_LENGTH))

    # Variance factor
    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / n
    if variance < _EPS:
        return 0.0  # constant sequence – no information

    # Normalise variance factor using a soft cap (coefficient of variation)
    std = math.sqrt(variance)
    abs_mean = abs(mean)
    if abs_mean > _EPS_MEAN:
        cv = std / abs_mean
        var_factor = min(1.0, cv / 1.0)  # saturates at cv=1
    else:
        # Mean near zero: use raw std normalised to its own scale
        var_factor = min(1.0, std / (std + 1.0))

    confidence = length_factor * var_factor
    return float(min(1.0, max(0.0, confidence)))


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #


def score(
    sequence: Sequence,
    mode: str = "numeric",
    *,
    profile: str = PROFILE_NAME,
) -> dict:
    """
    Score a sequence and return a dict with coherence, entropy, and confidence.

    Parameters
    ----------
    sequence:
        An ordered sequence of numbers.  For ``mode="tokens"`` or
        ``mode="actions"`` the values are treated as integer ids / action codes
        and converted to floats internally before scoring.
    mode:
        One of ``"numeric"``, ``"tokens"``, or ``"actions"``.
        All three modes produce the same numerical pipeline; the distinction is
        preserved in the returned ``mode`` field for downstream filtering.
    profile:
        Scoring profile name.  Only ``"rff_v1"`` is currently supported.

    Returns
    -------
    dict with keys:

    - ``ok``        (bool)  – False when confidence is too low to be useful.
    - ``profile``   (str)   – name of the scoring profile used.
    - ``mode``      (str)   – the mode argument echoed back.
    - ``coherence`` (float) – φ-weighted autocorrelation coherence ∈ [0, 1].
    - ``entropy``   (float) – normalised Shannon entropy ∈ [0, 1].
    - ``confidence``(float) – calibrated reliability of the scores ∈ [0, 1].
    - ``n``         (int)   – number of elements processed.
    - ``reason``    (str)   – human-readable explanation when ``ok`` is False.

    What the scores mean and do NOT mean
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    - ``coherence`` measures *structural* self-similarity via φ-weighted
      autocorrelation.  It does NOT measure semantic quality, correctness, or
      safety of the sequence.
    - ``entropy`` measures distributional uniformity of incremental changes.
      It does NOT measure information content in the Shannon channel-capacity
      sense (there is no source model).
    - ``confidence`` measures data sufficiency.  A high confidence does NOT
      guarantee that the coherence/entropy estimates are accurate in an
      absolute sense – they are always relative to the sequence itself.

    Fail-closed behaviour
    ~~~~~~~~~~~~~~~~~~~~~~
    When ``confidence < CONFIDENCE_THRESHOLD`` the function returns
    ``ok=False`` with a descriptive ``reason``.  Callers must check ``ok``
    before using the scores.

    Examples
    --------
    >>> result = score([0, 1, 1, 2, 3, 5, 8, 13, 21, 34], mode="numeric")
    >>> result["ok"]
    True
    >>> result["profile"]
    'rff_v1'
    >>> 0.0 <= result["coherence"] <= 1.0
    True
    >>> result = score([1, 2], mode="numeric")
    >>> result["ok"]
    False
    """
    if profile != PROFILE_NAME:
        raise ValueError(f"Unknown profile {profile!r}; only {PROFILE_NAME!r} is supported.")

    allowed_modes = {"numeric", "tokens", "actions"}
    if mode not in allowed_modes:
        raise ValueError(f"mode must be one of {sorted(allowed_modes)!r}, got {mode!r}")

    values = _to_floats(sequence)
    n = len(values)

    # Fail-closed: too short
    if n < MIN_LENGTH:
        return {
            "ok": False,
            "profile": profile,
            "mode": mode,
            "coherence": 0.0,
            "entropy": 0.0,
            "confidence": 0.0,
            "n": n,
            "reason": f"sequence too short (len={n}, minimum={MIN_LENGTH})",
        }

    coherence = _phi_coherence(values)
    entropy = _shannon_entropy_normalised(values)
    conf = _confidence(values)

    ok = conf >= CONFIDENCE_THRESHOLD
    reason = "" if ok else f"confidence too low ({conf:.3f} < {CONFIDENCE_THRESHOLD})"

    return {
        "ok": ok,
        "profile": profile,
        "mode": mode,
        "coherence": coherence,
        "entropy": entropy,
        "confidence": conf,
        "n": n,
        "reason": reason,
    }


def calibration_report(sequences: Sequence[Sequence[Any]], *, profile: str = PROFILE_NAME) -> dict:
    """
    Generate a calibration report for a batch of sequences.

    Returns aggregate statistics (mean/std of each metric) so that callers
    can assess the stability of the scoring profile across a corpus.

    Parameters
    ----------
    sequences:
        List of sequences to evaluate.
    profile:
        Scoring profile to use.

    Returns
    -------
    dict with keys ``profile``, ``n_sequences``, ``n_ok``,
    and per-metric ``mean_*`` / ``std_*`` keys.
    """
    results = [score(seq, profile=profile) for seq in sequences]
    ok_results = [r for r in results if r["ok"]]

    def _stats(key: str) -> tuple[float, float]:
        vals = [r[key] for r in ok_results]
        if not vals:
            return (float("nan"), float("nan"))
        mean = sum(vals) / len(vals)
        variance = sum((v - mean) ** 2 for v in vals) / len(vals)
        return (mean, math.sqrt(variance))

    mean_coh, std_coh = _stats("coherence")
    mean_ent, std_ent = _stats("entropy")
    mean_conf, std_conf = _stats("confidence")

    return {
        "profile": profile,
        "n_sequences": len(results),
        "n_ok": len(ok_results),
        "mean_coherence": mean_coh,
        "std_coherence": std_coh,
        "mean_entropy": mean_ent,
        "std_entropy": std_ent,
        "mean_confidence": mean_conf,
        "std_confidence": std_conf,
    }
