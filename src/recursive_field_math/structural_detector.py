"""
Structural Pattern Detector.

Analyses an input sequence (text tokens, numeric ids, or raw floats) and
produces three diagnostics:

structural_signature
    A compact fingerprint of the sequence's repetition and interval structure,
    expressed as a normalised vector of φ-harmonic coefficients.

anomaly_index
    A scalar ∈ [0, 1] indicating how strongly the sequence deviates from an
    expected φ-coherent baseline.  Higher means more anomalous.

coherence_trace
    A list of per-window coherence values that lets callers inspect *where*
    within the sequence the structure holds or breaks.

Design philosophy
~~~~~~~~~~~~~~~~~
This module deliberately avoids claims about *meaning*.  It measures
observable structure (repetition, interval regularity, distributional
uniformity) and nothing more.  The caller is responsible for interpreting
whether high or low anomaly is good or bad for their domain.

Fail-closed
~~~~~~~~~~~
When the sequence is too short or degenerate, ``detect()`` returns
``ok=False`` with a descriptive ``reason`` field.  Never raises silently.

Examples::

    >>> from recursive_field_math.structural_detector import detect
    >>> result = detect([1, 1, 2, 3, 5, 8, 13, 21, 34, 55])
    >>> result["ok"]
    True
    >>> 0.0 <= result["anomaly_index"] <= 1.0
    True
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from .constants import PHI

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

MIN_LENGTH: int = 6
WINDOW_SIZE: int = 4  # minimum window for coherence trace
N_HARMONICS: int = 8  # number of φ-harmonic coefficients in signature
ANOMALY_THRESHOLD: float = 0.7  # above this the trace window is flagged

# Numerical stability floor and minimum internal sizes.
_EPS: float = 1e-12
_MIN_WINDOW_COHERENCE: int = 3
_MIN_DELTA_LEN: int = 2

# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #


def _to_floats(sequence: Sequence) -> list[float]:
    return [float(x) for x in sequence]


def _phi_harmonic_coefficients(values: list[float], n_harmonics: int = N_HARMONICS) -> list[float]:
    """
    Project *values* onto a basis of φ-harmonic sinusoids.

    The k-th basis frequency is  fₖ = φᵏ / len(values),  producing a
    naturally spaced set of frequencies that respects Lucas/Fibonacci packing.

    Returns a list of *normalised* coefficient magnitudes (each ∈ [0, 1]).
    """
    n = len(values)
    mean = sum(values) / n
    centred = [v - mean for v in values]

    coeffs: list[float] = []
    for k in range(1, n_harmonics + 1):
        freq = PHI**k / n
        cos_sum = sum(centred[i] * math.cos(2 * math.pi * freq * i) for i in range(n))
        sin_sum = sum(centred[i] * math.sin(2 * math.pi * freq * i) for i in range(n))
        magnitude = math.hypot(cos_sum, sin_sum) / max(n, 1)
        coeffs.append(magnitude)

    # Normalise to [0, 1] relative to the max coefficient
    max_c = max(coeffs) if coeffs else 1.0
    if max_c < _EPS:
        return [0.0] * n_harmonics
    return [c / max_c for c in coeffs]


def _window_coherence(window: list[float]) -> float:
    """
    Single-window φ-autocorrelation coherence (reuses logic from eval_api).

    Returns a value in [0, 1].
    """
    if len(window) < _MIN_WINDOW_COHERENCE:
        return 0.0

    deltas = [window[i + 1] - window[i] for i in range(len(window) - 1)]
    n = len(deltas)
    if n < _MIN_DELTA_LEN:
        return 0.0

    phi_inv = 1.0 / PHI
    shifted = [phi_inv * deltas[i] for i in range(n - 1)]
    original = deltas[: n - 1]

    mean_o = sum(original) / len(original)
    mean_s = sum(shifted) / len(shifted)
    cov = sum((o - mean_o) * (s - mean_s) for o, s in zip(original, shifted))
    var_o = sum((o - mean_o) ** 2 for o in original)
    var_s = sum((s - mean_s) ** 2 for s in shifted)

    denom = math.sqrt(var_o * var_s)
    if denom < _EPS:
        return 0.0

    return min(1.0, abs(cov / denom))


def _anomaly_index(coherence_trace: list[float]) -> float:
    """
    Compute anomaly index as the fraction of trace windows that fall *below*
    the expected coherence baseline.

    Expected baseline = mean of all windows.  Windows below the mean
    contribute to the anomaly score proportionally to their deficit.

    Returns a value in [0, 1].
    """
    if not coherence_trace:
        return 0.0

    mean_coh = sum(coherence_trace) / len(coherence_trace)
    deficits = [max(0.0, mean_coh - c) for c in coherence_trace]
    total_deficit = sum(deficits)
    max_possible = mean_coh * len(coherence_trace)  # if all windows had 0 coherence

    if max_possible < _EPS:
        return 0.0

    return min(1.0, total_deficit / max_possible)


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #


def detect(
    sequence: Sequence,
    *,
    window_size: int = WINDOW_SIZE,
    n_harmonics: int = N_HARMONICS,
) -> dict:
    """
    Analyse a sequence and return its structural signature, anomaly index, and
    coherence trace.

    Parameters
    ----------
    sequence:
        Any ordered sequence of numeric values (floats, ints, token ids, …).
    window_size:
        Sliding-window size for computing the coherence trace.  Must be ≥ 3.
    n_harmonics:
        Number of φ-harmonic coefficients in the structural signature.

    Returns
    -------
    dict with keys:

    - ``ok``                  (bool)
    - ``structural_signature``(list[float]) – φ-harmonic coefficient vector.
    - ``anomaly_index``       (float)       – deviation from φ-baseline ∈ [0, 1].
    - ``coherence_trace``     (list[float]) – per-window coherence values.
    - ``n``                   (int)         – sequence length.
    - ``reason``              (str)         – explanation when ``ok`` is False.

    What the outputs mean and do NOT mean
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    - ``structural_signature``: a *relative* fingerprint.  Two sequences with
      identical signatures have the same harmonic structure, but may differ in
      scale or offset.
    - ``anomaly_index``: a local deviation score.  It does NOT identify the
      type of anomaly or its cause.
    - ``coherence_trace``: a diagnostic window-by-window view.  Low coherence
      in a window means the local differences are NOT well-described by a
      φ-damped autocorrelation; it does NOT mean the data is incorrect.

    Fail-closed
    ~~~~~~~~~~~
    Returns ``ok=False`` for sequences shorter than ``MIN_LENGTH`` or with
    zero variance.

    Examples
    --------
    >>> result = detect([2, 1, 3, 4, 7, 11, 18, 29])
    >>> result["ok"]
    True
    >>> len(result["structural_signature"]) == 8
    True
    >>> result = detect([1, 2])
    >>> result["ok"]
    False
    """
    if window_size < _MIN_WINDOW_COHERENCE:
        raise ValueError(f"window_size must be >= {_MIN_WINDOW_COHERENCE}, got {window_size}")

    values = _to_floats(sequence)
    n = len(values)

    if n < MIN_LENGTH:
        return {
            "ok": False,
            "structural_signature": [],
            "anomaly_index": 0.0,
            "coherence_trace": [],
            "n": n,
            "reason": f"sequence too short (len={n}, minimum={MIN_LENGTH})",
        }

    # Check for zero variance
    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / n
    if variance < _EPS:
        return {
            "ok": False,
            "structural_signature": [0.0] * n_harmonics,
            "anomaly_index": 0.0,
            "coherence_trace": [],
            "n": n,
            "reason": "zero variance – constant sequence contains no structure",
        }

    # Structural signature via φ-harmonic projection
    signature = _phi_harmonic_coefficients(values, n_harmonics=n_harmonics)

    # Coherence trace via sliding window
    effective_window = max(window_size, WINDOW_SIZE)
    trace: list[float] = []
    for start in range(n - effective_window + 1):
        window = values[start : start + effective_window]
        trace.append(_window_coherence(window))

    # Anomaly index from trace
    anomaly = _anomaly_index(trace)

    return {
        "ok": True,
        "structural_signature": signature,
        "anomaly_index": anomaly,
        "coherence_trace": trace,
        "n": n,
        "reason": "",
    }
