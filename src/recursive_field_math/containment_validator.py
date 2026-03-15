"""
Containment Geometry Validator (SCE-88 style).

Accepts an architecture specification expressed as a nested dict (loaded from
YAML, JSON, or Markdown front-matter) and returns a *containment analysis*:

containment_score
    Scalar ∈ [0, 1].  Higher means the architecture is more tightly
    self-contained, with fewer potential escape paths.  Uses φ-weighted
    layer coupling.

weak_layer_map
    Dict mapping layer name → weakness score ∈ [0, 1].  Layers with high
    scores are candidates for hardening.

escape_path_candidates
    List of (from_layer, to_layer, severity) tuples identifying the most
    likely containment failures.

Design philosophy
~~~~~~~~~~~~~~~~~
This validator reasons about *structural geometry* (how layers reference each
other) and NOT about the runtime behaviour of the system.  A high containment
score means the declared architecture has few cross-layer couplings; it does
NOT prove that the running system is safe or secure.

Fail-closed
~~~~~~~~~~~
Returns ``ok=False`` with a ``reason`` when the spec is missing required keys
or has fewer than two layers.

Spec format
~~~~~~~~~~~
The minimal required spec is a dict with a ``"layers"`` key mapping layer
names to dicts that may contain:

    - ``"depends_on"``  – list of layer names this layer imports/calls
    - ``"weight"``      – optional float for importance (default 1.0)
    - ``"public_api"``  – optional bool (default True)

Example::

    >>> from recursive_field_math.containment_validator import validate
    >>> spec = {
    ...     "layers": {
    ...         "core":    {"depends_on": []},
    ...         "service": {"depends_on": ["core"]},
    ...         "api":     {"depends_on": ["service"]},
    ...     }
    ... }
    >>> result = validate(spec)
    >>> result["ok"]
    True
    >>> 0.0 <= result["containment_score"] <= 1.0
    True
"""

from __future__ import annotations

import math
from typing import Any

from .constants import PHI

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

MIN_LAYERS: int = 2

# A layer that depends on more than this fraction of all other layers is weak
COUPLING_THRESHOLD: float = 0.5

# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #


def _parse_layers(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Extract and normalise the 'layers' block from a spec dict."""
    raw = spec.get("layers", {})
    normalised: dict[str, dict[str, Any]] = {}
    for name, props in raw.items():
        if not isinstance(props, dict):
            props = {}
        normalised[name] = {
            "depends_on": list(props.get("depends_on", [])),
            "weight": float(props.get("weight", 1.0)),
            "public_api": bool(props.get("public_api", True)),
        }
    return normalised


def _coupling_matrix(layers: dict[str, dict[str, Any]]) -> dict[tuple[str, str], float]:
    """
    Build a directed coupling map {(from, to): φ-weighted coupling strength}.

    Each declared dependency contributes a coupling of ``1 / φ^depth`` where
    *depth* is estimated by topological distance from the entry layer.

    For simplicity here, depth is approximated as the position of the
    dependency in a sorted list (shortest path estimates require a full BFS
    but the φ-weighting already discounts distant dependencies).
    """
    layer_names = list(layers.keys())
    couplings: dict[tuple[str, str], float] = {}

    for name, props in layers.items():
        src_idx = layer_names.index(name)
        for dep in props["depends_on"]:
            if dep not in layers:
                continue  # dangling reference – treat as absent
            dep_idx = layer_names.index(dep)
            depth = abs(src_idx - dep_idx)
            strength = 1.0 / (PHI ** max(depth, 1))
            couplings[(name, dep)] = strength

    return couplings


def _weak_layer_scores(
    layers: dict[str, dict[str, Any]],
    couplings: dict[tuple[str, str], float],
) -> dict[str, float]:
    """
    Assign each layer a weakness score based on:
    1. Out-degree fraction (how many other layers it depends on).
    2. Total coupling strength normalised to the layer's own weight.
    """
    n = len(layers)
    scores: dict[str, float] = {}

    for name, props in layers.items():
        out_edges = [c for (src, _), c in couplings.items() if src == name]
        out_degree = len(out_edges)
        degree_fraction = out_degree / max(n - 1, 1)
        coupling_strength = sum(out_edges)
        weight = props["weight"]
        # Combine: high degree AND high coupling → high weakness
        weakness = (degree_fraction + coupling_strength / max(weight, 1e-9)) / 2.0
        scores[name] = min(1.0, weakness)

    return scores


def _escape_paths(
    couplings: dict[tuple[str, str], float],
    weak_scores: dict[str, float],
    *,
    top_k: int = 5,
) -> list[tuple[str, str, float]]:
    """
    Identify escape-path candidates: edges where *both* endpoints are weak.

    Returns a list of (from_layer, to_layer, severity) sorted by severity desc.
    Severity = geometric mean of the two weakness scores × coupling strength.
    """
    candidates: list[tuple[str, str, float]] = []
    for (src, dst), strength in couplings.items():
        src_weak = weak_scores.get(src, 0.0)
        dst_weak = weak_scores.get(dst, 0.0)
        severity = math.sqrt(src_weak * dst_weak) * strength
        if severity > 0:
            candidates.append((src, dst, severity))

    candidates.sort(key=lambda x: x[2], reverse=True)
    return candidates[:top_k]


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #


def validate(spec: dict[str, Any], *, top_k_escapes: int = 5) -> dict[str, Any]:
    """
    Validate an architecture spec and return containment geometry analysis.

    Parameters
    ----------
    spec:
        Architecture specification dict.  Must contain a ``"layers"`` key
        mapping layer names to their properties (see module docstring).
    top_k_escapes:
        Maximum number of escape-path candidates to report.

    Returns
    -------
    dict with keys:

    - ``ok``                     (bool)
    - ``containment_score``      (float) – ∈ [0, 1]; higher = better contained.
    - ``weak_layer_map``         (dict)  – layer → weakness score ∈ [0, 1].
    - ``escape_path_candidates`` (list)  – [(from, to, severity), …].
    - ``n_layers``               (int)
    - ``n_couplings``            (int)
    - ``reason``                 (str)   – explanation when ``ok`` is False.

    What the outputs mean and do NOT mean
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    - ``containment_score``: reflects the *declared* dependency topology.
      A score of 1.0 means no cross-layer couplings were declared; it does NOT
      mean the system is actually isolated at runtime.
    - ``weak_layer_map``: a static analysis score based on fan-out.  A weak
      layer is a structural concern, NOT necessarily a security vulnerability.
    - ``escape_path_candidates``: edges between structurally weak layers.  They
      are *candidates* for review, not confirmed vulnerabilities.

    Fail-closed
    ~~~~~~~~~~~
    Returns ``ok=False`` for specs with fewer than ``MIN_LAYERS`` layers, or
    if the ``"layers"`` key is absent.

    Examples
    --------
    >>> spec = {
    ...     "layers": {
    ...         "core":    {"depends_on": []},
    ...         "service": {"depends_on": ["core"]},
    ...         "api":     {"depends_on": ["service"]},
    ...     }
    ... }
    >>> result = validate(spec)
    >>> result["ok"]
    True
    >>> result["n_layers"]
    3
    >>> result = validate({})
    >>> result["ok"]
    False
    """
    if "layers" not in spec:
        return {
            "ok": False,
            "containment_score": 0.0,
            "weak_layer_map": {},
            "escape_path_candidates": [],
            "n_layers": 0,
            "n_couplings": 0,
            "reason": "spec missing required 'layers' key",
        }

    layers = _parse_layers(spec)
    n = len(layers)

    if n < MIN_LAYERS:
        return {
            "ok": False,
            "containment_score": 0.0,
            "weak_layer_map": {},
            "escape_path_candidates": [],
            "n_layers": n,
            "n_couplings": 0,
            "reason": f"spec has fewer than {MIN_LAYERS} layers (found {n})",
        }

    couplings = _coupling_matrix(layers)
    weak_scores = _weak_layer_scores(layers, couplings)
    escapes = _escape_paths(couplings, weak_scores, top_k=top_k_escapes)

    # Containment score: inverse of mean weakness, φ-weighted by layer count
    mean_weakness = sum(weak_scores.values()) / n
    # φ-weight: more layers → bonus for organised containment
    phi_weight = math.log(1 + n) / math.log(1 + n * PHI)
    containment_score = (1.0 - mean_weakness) * phi_weight
    containment_score = min(1.0, max(0.0, containment_score))

    return {
        "ok": True,
        "containment_score": containment_score,
        "weak_layer_map": weak_scores,
        "escape_path_candidates": escapes,
        "n_layers": n,
        "n_couplings": len(couplings),
        "reason": "",
    }
