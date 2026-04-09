"""
Self-Model module for recursive field introspection.

Provides a deterministic, thread-safe self-model that wraps the SCE-88
containment geometry validator (``containment_validator.validate``) and uses
Lucas/φ mathematics to update internal state in response to observed input
patterns.

The model maintains four state variables:

- ``phase`` (int): monotonically increasing observation counter.
- ``coherence_score`` (float ∈ [0, 1]): containment score from the last
  successful constraint validation pass.
- ``uncertainty`` (float ∈ [0, 1]): starts at 1.0 and decays toward 0 as
  valid data is integrated.
- ``last_input_hash`` (str): deterministic hex digest of the last observed
  input, used for change detection.

Key behaviours
~~~~~~~~~~~~~~
- **observe** — hashes the input, computes a Lucas-weighted delta, and
  re-validates the internal architecture spec against SCE-88 constraints.
- **ask** — returns a JSON query dict when ``uncertainty > 0.3``; otherwise
  returns ``None``.
- **integrate** — validates new data against the constraint topology and, if
  valid, reduces uncertainty by a φ-weighted decay factor.

Thread safety
~~~~~~~~~~~~~
All mutable state access is guarded by a ``threading.Lock``.

Zero new dependencies
~~~~~~~~~~~~~~~~~~~~~
Uses only the stdlib and existing ``recursive_field_math`` internals.
"""

from __future__ import annotations

import hashlib
import json
import threading
from typing import Any

from .constants import PHI
from .containment_validator import validate
from .lucas import L

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

UNCERTAINTY_THRESHOLD: float = 0.3

# --------------------------------------------------------------------------- #
# Default architecture spec used for SCE-88 constraint validation
# --------------------------------------------------------------------------- #

_DEFAULT_SPEC: dict[str, Any] = {
    "layers": {
        "observer": {"depends_on": []},
        "integrator": {"depends_on": ["observer"]},
        "query_engine": {"depends_on": ["integrator"]},
        "constraint_gate": {"depends_on": ["integrator", "observer"]},
    }
}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _hash_input(data: str) -> str:
    """Return a deterministic hex digest for *data*."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _lucas_delta(phase: int) -> float:
    """
    Compute a φ-normalised delta from the Lucas sequence at *phase*.

    Uses L(phase mod 10) scaled by 1/φ² so the result stays in (0, 1).
    """
    idx = phase % 10
    return L(idx) / (PHI**2 + L(idx))


# --------------------------------------------------------------------------- #
# SelfModel
# --------------------------------------------------------------------------- #


class SelfModel:
    """Deterministic, thread-safe self-model wrapping SCE-88 constraints.

    Parameters
    ----------
    spec:
        Architecture specification dict passed to the containment validator.
        Defaults to a four-layer internal topology.

    Examples
    --------
    >>> sm = SelfModel()
    >>> delta = sm.observe("hello")
    >>> 0 <= delta <= 1
    True
    >>> sm.state()["phase"]
    1
    """

    def __init__(self, spec: dict[str, Any] | None = None) -> None:
        self._spec = spec if spec is not None else _DEFAULT_SPEC
        self._lock = threading.Lock()

        # Internal mutable state
        self._phase: int = 0
        self._coherence_score: float = 0.0
        self._uncertainty: float = 1.0
        self._last_input_hash: str = ""

        # Run initial constraint validation to seed coherence
        result = validate(self._spec)
        if result["ok"]:
            self._coherence_score = float(result["containment_score"])

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def state(self) -> dict[str, Any]:
        """Return a snapshot of the current internal state."""
        with self._lock:
            return {
                "phase": self._phase,
                "coherence_score": round(self._coherence_score, 6),
                "uncertainty": round(self._uncertainty, 6),
                "last_input_hash": self._last_input_hash,
            }

    def observe(self, input_pattern: str) -> float:
        """Observe *input_pattern*, update state, and return a delta ∈ [0, 1].

        The delta is derived from the Lucas sequence at the current phase,
        φ-normalised.  The containment validator is re-run to refresh the
        coherence score.

        Parameters
        ----------
        input_pattern:
            Arbitrary string (or JSON) to observe.

        Returns
        -------
        float
            The computed delta value ∈ [0, 1].
        """
        with self._lock:
            self._last_input_hash = _hash_input(input_pattern)
            self._phase += 1
            delta = _lucas_delta(self._phase)

            # Re-validate constraints
            result = validate(self._spec)
            if result["ok"]:
                self._coherence_score = float(result["containment_score"])

            return round(delta, 6)

    def ask(self) -> dict[str, Any] | None:
        """Return a query dict when uncertainty exceeds 0.3, else ``None``.

        The query includes the current state snapshot and a human-readable
        question field that downstream systems can act on.
        """
        with self._lock:
            if self._uncertainty <= UNCERTAINTY_THRESHOLD:
                return None
            return {
                "query": "Request additional data to reduce uncertainty.",
                "current_uncertainty": round(self._uncertainty, 6),
                "phase": self._phase,
                "coherence_score": round(self._coherence_score, 6),
            }

    def integrate(self, new_data: str) -> dict[str, Any]:
        """Validate *new_data* against the constraint topology and integrate.

        If the data passes validation the uncertainty is reduced by a
        φ-weighted decay factor: ``uncertainty *= 1/φ``.

        Parameters
        ----------
        new_data:
            JSON string representing new information to integrate.

        Returns
        -------
        dict
            ``{"ok": True/False, "state": <state snapshot>, ...}``
        """
        with self._lock:
            # Attempt to parse new_data as JSON for richer validation
            try:
                parsed = json.loads(new_data)
            except (json.JSONDecodeError, TypeError):
                parsed = {"raw": new_data}

            # Build a transient spec overlay if the data includes layers
            test_spec = parsed if isinstance(parsed, dict) and "layers" in parsed else self._spec

            result = validate(test_spec)
            if not result["ok"]:
                return {
                    "ok": False,
                    "reason": result.get("reason", "constraint validation failed"),
                    "state": self._snapshot_unlocked(),
                }

            # Decay uncertainty
            self._uncertainty = max(0.0, self._uncertainty * (1.0 / PHI))
            self._coherence_score = float(result["containment_score"])
            self._last_input_hash = _hash_input(new_data)

            return {
                "ok": True,
                "state": self._snapshot_unlocked(),
            }

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _snapshot_unlocked(self) -> dict[str, Any]:
        """Return state snapshot **without** acquiring the lock (caller holds it)."""
        return {
            "phase": self._phase,
            "coherence_score": round(self._coherence_score, 6),
            "uncertainty": round(self._uncertainty, 6),
            "last_input_hash": self._last_input_hash,
        }
