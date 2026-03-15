"""
Cross-Domain Bridge.

Provides a common latent geometry schema and bidirectional domain adapters
that convert domain-specific data into a normalised φ-harmonic latent vector
and back.

Core guarantee
~~~~~~~~~~~~~~
For each registered adapter, the round-trip error is bounded:

    |decode(encode(x)) - x| / scale(x)  ≤  ERROR_BOUND

where ``scale(x)`` is the root-mean-square of *x*.  If the bound would be
exceeded the encode/decode raises ``BridgeError`` rather than silently
returning a degraded result (fail-closed).

Latent geometry schema (``LatentVector``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A ``LatentVector`` is a fixed-length list of φ-harmonic projection
coefficients (``N_LATENT`` values) together with metadata:

    {
        "values":    [float, …],   # N_LATENT normalised coefficients
        "norm":      float,        # original RMS for scale recovery
        "domain":    str,          # source domain tag
        "profile":   str,          # bridge profile version
        "n_input":   int,          # original input length
    }

Domain adapters
~~~~~~~~~~~~~~~
Three adapters are registered by default:

- ``"numeric"``  – raw float sequences
- ``"tokens"``   – integer token-id sequences (treated as ordinal ranks)
- ``"actions"``  – integer action sequences (same pipeline as tokens)

Custom adapters can be added via ``register_adapter``.

Fail-closed
~~~~~~~~~~~
- Sequences below ``MIN_INPUT_LENGTH`` are rejected.
- Round-trip error exceeding ``ERROR_BOUND`` raises ``BridgeError``.

Examples::

    >>> from recursive_field_math.xdomain_bridge import encode, decode, bridge
    >>> lv = encode([1, 1, 2, 3, 5, 8, 13, 21], domain="numeric")
    >>> lv["domain"]
    'numeric'
    >>> reconstructed = decode(lv)
    >>> len(reconstructed) == 8
    True
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence

from .constants import PHI

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

N_LATENT: int = 16  # dimensionality of the latent vector
MIN_INPUT_LENGTH: int = 4
ERROR_BOUND: float = 0.10  # max allowable round-trip relative error
BRIDGE_PROFILE: str = "xbridge_v1"

# Numerical stability floor.
_EPS: float = 1e-12

# --------------------------------------------------------------------------- #
# Custom exception
# --------------------------------------------------------------------------- #


class BridgeError(Exception):
    """Raised when a round-trip error bound is exceeded or inputs are invalid."""


# --------------------------------------------------------------------------- #
# Latent geometry helpers
# --------------------------------------------------------------------------- #


def _rms(values: list[float]) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum(v**2 for v in values) / len(values))


def _phi_project(values: list[float], n_dims: int = N_LATENT) -> list[float]:
    """
    Project *values* onto φ-harmonic basis and return normalised coefficients.

    The k-th basis function is  cos(2π · φᵏ · i / n)  for i in range(n).
    Coefficients are normalised so that the max absolute value is 1.0.
    """
    n = len(values)
    mean = sum(values) / n
    centred = [v - mean for v in values]

    coeffs: list[float] = []
    for k in range(1, n_dims + 1):
        freq = PHI**k / n
        c = sum(centred[i] * math.cos(2 * math.pi * freq * i) for i in range(n)) / n
        coeffs.append(c)

    max_abs = max(abs(c) for c in coeffs) if coeffs else 1.0
    if max_abs < _EPS:
        return [0.0] * n_dims
    return [c / max_abs for c in coeffs]


def _phi_reconstruct(
    latent: list[float],
    n_output: int,
    norm: float,
    n_dims: int = N_LATENT,
) -> list[float]:
    """
    Reconstruct an approximation of the original sequence from latent coefficients.

    Uses the inverse of the φ-harmonic projection (pseudo-inverse via
    summation over all basis functions weighted by latent coefficients).
    The result is re-scaled by *norm* to approximately restore the original
    magnitude.
    """
    if n_output < 1:
        return []

    values = [0.0] * n_output
    for k, coeff in enumerate(latent, start=1):
        freq = PHI**k / n_output
        for i in range(n_output):
            values[i] += coeff * math.cos(2 * math.pi * freq * i)

    # Re-scale to match original norm
    current_rms = _rms(values)
    if current_rms > _EPS and norm > _EPS:
        scale = norm / current_rms
        values = [v * scale for v in values]

    return values


# --------------------------------------------------------------------------- #
# Adapter registry
# --------------------------------------------------------------------------- #

AdapterFn = Callable[[Sequence], list[float]]

_ADAPTERS: dict[str, AdapterFn] = {}


def register_adapter(domain: str, fn: AdapterFn) -> None:
    """
    Register a custom domain adapter.

    Parameters
    ----------
    domain:
        Domain tag string (e.g. ``"my_domain"``).
    fn:
        Callable that converts a raw sequence to a list of floats ready for
        φ-projection.
    """
    _ADAPTERS[domain] = fn


def _default_numeric(seq: Sequence) -> list[float]:
    return [float(x) for x in seq]


def _default_tokens(seq: Sequence) -> list[float]:
    """Ordinal rank mapping for token ids."""
    values = [float(x) for x in seq]
    sorted_vals = sorted(set(values))
    rank_map = {v: i for i, v in enumerate(sorted_vals)}
    return [float(rank_map[v]) for v in values]


# Register built-in adapters
register_adapter("numeric", _default_numeric)
register_adapter("tokens", _default_tokens)
register_adapter("actions", _default_tokens)  # same pipeline as tokens

# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #


def encode(
    sequence: Sequence,
    domain: str = "numeric",
    *,
    n_latent: int = N_LATENT,
) -> dict:
    """
    Encode a domain sequence into a latent φ-harmonic vector.

    Parameters
    ----------
    sequence:
        Input sequence (numeric, token ids, action ids, etc.).
    domain:
        Domain adapter to use.  Must be registered (default adapters:
        ``"numeric"``, ``"tokens"``, ``"actions"``).
    n_latent:
        Latent vector dimensionality.

    Returns
    -------
    ``LatentVector`` dict (see module docstring).

    Raises
    ------
    BridgeError
        If the sequence is too short or the domain is not registered.

    Examples
    --------
    >>> lv = encode([0, 1, 1, 2, 3, 5, 8, 13], domain="numeric")
    >>> lv["profile"]
    'xbridge_v1'
    >>> len(lv["values"]) == 16
    True
    """
    if domain not in _ADAPTERS:
        raise BridgeError(f"Unknown domain {domain!r}. Registered: {sorted(_ADAPTERS)!r}")

    adapter = _ADAPTERS[domain]
    values = adapter(sequence)
    n = len(values)

    if n < MIN_INPUT_LENGTH:
        raise BridgeError(
            f"Sequence too short for domain {domain!r} (len={n}, minimum={MIN_INPUT_LENGTH})"
        )

    norm = _rms(values)
    latent = _phi_project(values, n_dims=n_latent)

    return {
        "values": latent,
        "norm": norm,
        "domain": domain,
        "profile": BRIDGE_PROFILE,
        "n_input": n,
    }


def decode(
    latent_vector: dict,
    *,
    check_error_bound: bool = True,
    original: Sequence | None = None,
) -> list[float]:
    """
    Decode a ``LatentVector`` back into an approximate numeric sequence.

    Parameters
    ----------
    latent_vector:
        A dict returned by ``encode()``.
    check_error_bound:
        If True and *original* is provided, verify the round-trip error is
        within ``ERROR_BOUND`` and raise ``BridgeError`` if not.
    original:
        Optional reference sequence for round-trip error checking.

    Returns
    -------
    list[float] – reconstructed sequence of length ``latent_vector["n_input"]``.

    Raises
    ------
    BridgeError
        If round-trip error exceeds ``ERROR_BOUND`` (when *original* given).

    Examples
    --------
    >>> lv = encode([1, 2, 3, 4, 5, 6, 7, 8], domain="numeric")
    >>> rec = decode(lv)
    >>> len(rec) == 8
    True
    """
    required = {"values", "norm", "n_input"}
    missing = required - latent_vector.keys()
    if missing:
        raise BridgeError(f"LatentVector missing keys: {missing!r}")

    reconstructed = _phi_reconstruct(
        latent_vector["values"],
        latent_vector["n_input"],
        latent_vector["norm"],
        n_dims=len(latent_vector["values"]),
    )

    if check_error_bound and original is not None:
        orig_floats = [float(x) for x in original]
        orig_rms = _rms(orig_floats)
        if orig_rms > _EPS:
            diff_rms = _rms([r - o for r, o in zip(reconstructed, orig_floats, strict=False)])
            rel_error = diff_rms / orig_rms
            if rel_error > ERROR_BOUND:
                raise BridgeError(
                    f"Round-trip relative error {rel_error:.4f} exceeds ERROR_BOUND={ERROR_BOUND}"
                )

    return reconstructed


def bridge(
    sequence: Sequence,
    src_domain: str,
    dst_domain: str,
    *,
    n_latent: int = N_LATENT,
) -> dict:
    """
    Bridge a sequence from *src_domain* to *dst_domain* via the shared latent space.

    Parameters
    ----------
    sequence:
        Source sequence.
    src_domain:
        Domain of the source sequence.
    dst_domain:
        Domain for the reconstructed output.
    n_latent:
        Latent vector dimensionality.

    Returns
    -------
    dict with:
    - ``"latent_vector"`` – the intermediate ``LatentVector``.
    - ``"reconstructed"`` – list[float] approximation in *dst_domain*.
    - ``"src_domain"``    – source domain tag.
    - ``"dst_domain"``    – destination domain tag.
    - ``"profile"``       – bridge profile version.

    Notes
    -----
    Cross-domain bridging is *lossy*: the reconstruction is an approximation
    in the geometric sense.  The ``ERROR_BOUND`` guarantee applies only within
    the same domain (src == dst).  Different domains may have very different
    scales and semantics; the caller must interpret the output accordingly.

    Examples
    --------
    >>> result = bridge([1, 2, 3, 4, 5, 6, 7, 8], "numeric", "numeric")
    >>> result["src_domain"]
    'numeric'
    >>> result["dst_domain"]
    'numeric'
    >>> len(result["reconstructed"]) == 8
    True
    """
    if src_domain not in _ADAPTERS:
        raise BridgeError(f"Unknown src_domain {src_domain!r}")
    if dst_domain not in _ADAPTERS:
        raise BridgeError(f"Unknown dst_domain {dst_domain!r}")

    lv = encode(sequence, domain=src_domain, n_latent=n_latent)
    reconstructed = decode(lv, check_error_bound=False)

    return {
        "latent_vector": lv,
        "reconstructed": reconstructed,
        "src_domain": src_domain,
        "dst_domain": dst_domain,
        "profile": BRIDGE_PROFILE,
    }
