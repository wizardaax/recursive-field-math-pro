"""
Coherence Governor — monitors coherence-per-compute and triggers consolidation.

The governor watches the ratio ``coherence_score / active_workers``.  When
this ratio drops below a configurable threshold it triggers *consolidation*
(reducing active shards/workers) rather than a hard global halt.

A global halt is only triggered when the *global* coherence score breaches
an absolute floor.

Zero new runtime dependencies.
"""

from __future__ import annotations

import threading
import time
from typing import Any

from ..constants import PHI
from ..containment_validator import validate as sce88_validate

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

DEFAULT_RATIO_THRESHOLD: float = 0.15
GLOBAL_COHERENCE_FLOOR: float = 0.2
DEFAULT_CHECK_INTERVAL: float = 1.0  # seconds

_GOVERNOR_SPEC: dict[str, Any] = {
    "layers": {
        "monitor": {"depends_on": []},
        "gate": {"depends_on": ["monitor"]},
        "consolidator": {"depends_on": ["gate"]},
        "reporter": {"depends_on": ["consolidator"]},
    }
}


# --------------------------------------------------------------------------- #
# CoherenceGovernor
# --------------------------------------------------------------------------- #


class CoherenceGovernor:
    """Monitors coherence/compute ratio and triggers consolidation or halt.

    Parameters
    ----------
    ratio_threshold:
        Minimum acceptable coherence / active-workers ratio.  When the
        ratio drops below this value, consolidation is triggered.
    global_floor:
        Absolute coherence score below which a global halt is raised.
    """

    def __init__(
        self,
        ratio_threshold: float = DEFAULT_RATIO_THRESHOLD,
        global_floor: float = GLOBAL_COHERENCE_FLOOR,
    ) -> None:
        self._ratio_threshold = ratio_threshold
        self._global_floor = global_floor
        self._lock = threading.Lock()

        # State
        self._global_coherence: float = 1.0
        self._active_workers: int = 0
        self._consolidation_count: int = 0
        self._halt_triggered: bool = False
        self._last_ratio: float = 1.0
        self._throttle_active: bool = False

        # History (bounded)
        self._history: list[dict[str, Any]] = []
        self._max_history: int = 100

        # Validate own spec
        result = sce88_validate(_GOVERNOR_SPEC)
        if result["ok"]:
            self._global_coherence = float(result["containment_score"])

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def halt_triggered(self) -> bool:
        with self._lock:
            return self._halt_triggered

    @property
    def throttle_active(self) -> bool:
        with self._lock:
            return self._throttle_active

    @property
    def coherence_compute_ratio(self) -> float:
        with self._lock:
            return self._last_ratio

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def update(
        self,
        coherence_score: float,
        active_workers: int,
    ) -> dict[str, Any]:
        """Feed new metrics and return an action recommendation.

        Returns
        -------
        dict with keys:
        - ``action``: ``"ok"`` | ``"consolidate"`` | ``"halt"``
        - ``ratio``: current coherence/compute ratio
        - ``coherence``: global coherence score
        - ``active_workers``: worker count
        """
        with self._lock:
            self._global_coherence = coherence_score
            self._active_workers = active_workers

            # Compute ratio (avoid division by zero)
            ratio = coherence_score / active_workers if active_workers > 0 else coherence_score
            self._last_ratio = ratio

            # Determine action
            action = "ok"
            if coherence_score < self._global_floor:
                action = "halt"
                self._halt_triggered = True
                self._throttle_active = True
            elif ratio < self._ratio_threshold:
                action = "consolidate"
                self._consolidation_count += 1
                self._throttle_active = True
            else:
                self._throttle_active = False

            entry = {
                "timestamp": time.monotonic(),
                "coherence": round(coherence_score, 6),
                "active_workers": active_workers,
                "ratio": round(ratio, 6),
                "action": action,
            }
            self._history.append(entry)
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history :]

            return {
                "action": action,
                "ratio": round(ratio, 6),
                "coherence": round(coherence_score, 6),
                "active_workers": active_workers,
            }

    def reset_halt(self) -> None:
        """Clear the halt flag (e.g. after manual intervention)."""
        with self._lock:
            self._halt_triggered = False
            self._throttle_active = False

    def metrics(self) -> dict[str, Any]:
        """Return governor diagnostics."""
        with self._lock:
            return {
                "global_coherence": round(self._global_coherence, 6),
                "active_workers": self._active_workers,
                "coherence_compute_ratio": round(self._last_ratio, 6),
                "ratio_threshold": self._ratio_threshold,
                "global_floor": self._global_floor,
                "consolidation_count": self._consolidation_count,
                "halt_triggered": self._halt_triggered,
                "throttle_active": self._throttle_active,
                "history_size": len(self._history),
            }

    def history(self) -> list[dict[str, Any]]:
        """Return a copy of the metrics history."""
        with self._lock:
            return list(self._history)

    def recommended_workers(self, current_workers: int) -> int:
        """Suggest the optimal worker count based on current coherence.

        Uses φ-weighted reduction: when consolidating, reduce by
        ``floor(current / φ)`` to keep the ratio above threshold.
        """
        with self._lock:
            if self._halt_triggered:
                return 0
            if not self._throttle_active:
                return current_workers
            # φ-weighted reduction
            reduced = max(1, int(current_workers / PHI))
            return reduced
