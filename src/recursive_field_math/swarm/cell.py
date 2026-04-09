"""
CellShard — independent execution unit for the cellular swarm.

Each shard owns:
- A deterministic hash-based router (input hash → worker slot)
- A local coherence gate backed by the SCE-88 containment validator
- Isolated per-shard metrics (uncertainty, violations, throughput)

Workers follow the *stateless* pattern: spawn → compute → return → terminate.
All persistent state is externalised to ``SwarmMemory``.

Zero new runtime dependencies.
"""

from __future__ import annotations

import hashlib
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Callable

from ..constants import PHI
from ..containment_validator import validate as sce88_validate
from .memory import SwarmMemory

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

_DEFAULT_SPEC: dict[str, Any] = {
    "layers": {
        "ingest": {"depends_on": []},
        "compute": {"depends_on": ["ingest"]},
        "validate": {"depends_on": ["compute"]},
        "output": {"depends_on": ["validate"]},
    }
}

_COHERENCE_FLOOR: float = 0.4  # minimum acceptable per-shard coherence


# --------------------------------------------------------------------------- #
# Deterministic routing
# --------------------------------------------------------------------------- #


def deterministic_route(input_data: str, num_shards: int) -> int:
    """Map *input_data* to a shard index via SHA-256, fully deterministic.

    Parameters
    ----------
    input_data:
        Arbitrary string payload.
    num_shards:
        Total number of shards (must be >= 1).

    Returns
    -------
    int
        Shard index in ``[0, num_shards)``.
    """
    if num_shards < 1:
        raise ValueError("num_shards must be >= 1")
    digest = hashlib.sha256(input_data.encode("utf-8")).hexdigest()
    return int(digest, 16) % num_shards


def deterministic_worker_slot(input_data: str, workers_per_shard: int) -> int:
    """Map *input_data* to a worker slot within a shard.

    Uses MD5 for a second independent hash (still deterministic).
    """
    if workers_per_shard < 1:
        raise ValueError("workers_per_shard must be >= 1")
    digest = hashlib.md5(input_data.encode("utf-8")).hexdigest()  # noqa: S324
    return int(digest, 16) % workers_per_shard


# --------------------------------------------------------------------------- #
# CellShard
# --------------------------------------------------------------------------- #


class CellShard:
    """Independent execution cell with local orchestrator and coherence gate.

    Parameters
    ----------
    shard_id:
        Unique identifier for this shard.
    workers_per_shard:
        Number of concurrent worker slots.
    memory:
        Shared ``SwarmMemory`` instance for externalised state.
    spec:
        SCE-88 architecture spec for coherence validation.
    """

    def __init__(
        self,
        shard_id: int,
        workers_per_shard: int = 4,
        memory: SwarmMemory | None = None,
        spec: dict[str, Any] | None = None,
    ) -> None:
        self._shard_id = shard_id
        self._workers_per_shard = max(1, workers_per_shard)
        self._memory = memory or SwarmMemory()
        self._spec = spec or _DEFAULT_SPEC
        self._lock = threading.Lock()

        # Local metrics
        self._tasks_completed: int = 0
        self._tasks_failed: int = 0
        self._constraint_violations: int = 0
        self._total_compute_time: float = 0.0
        self._coherence_score: float = 1.0
        self._isolated: bool = False

        # Thread pool for stateless workers
        self._pool: ThreadPoolExecutor | None = None

        # Validate initial coherence
        result = sce88_validate(self._spec)
        if result["ok"]:
            self._coherence_score = float(result["containment_score"])

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def shard_id(self) -> int:
        return self._shard_id

    @property
    def workers_per_shard(self) -> int:
        return self._workers_per_shard

    @property
    def isolated(self) -> bool:
        with self._lock:
            return self._isolated

    @property
    def coherence_score(self) -> float:
        with self._lock:
            return self._coherence_score

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #

    def start(self) -> None:
        """Activate the shard's worker pool."""
        with self._lock:
            if self._pool is None:
                self._pool = ThreadPoolExecutor(
                    max_workers=self._workers_per_shard,
                    thread_name_prefix=f"shard-{self._shard_id}",
                )

    def stop(self) -> None:
        """Shutdown the worker pool gracefully."""
        with self._lock:
            if self._pool is not None:
                self._pool.shutdown(wait=True)
                self._pool = None

    # ------------------------------------------------------------------ #
    # Execution
    # ------------------------------------------------------------------ #

    def submit(
        self,
        fn: Callable[..., Any],
        input_data: str,
        *args: Any,
        **kwargs: Any,
    ) -> Future[Any] | None:
        """Submit a stateless computation.

        The worker slot is determined by ``deterministic_worker_slot``.
        Returns a ``Future`` on success, or ``None`` if the shard is isolated.
        """
        with self._lock:
            if self._isolated:
                return None
            if self._pool is None:
                self._pool = ThreadPoolExecutor(
                    max_workers=self._workers_per_shard,
                    thread_name_prefix=f"shard-{self._shard_id}",
                )

        # Wrap with timing + coherence bookkeeping
        def _worker() -> Any:
            t0 = time.monotonic()
            try:
                result = fn(input_data, *args, **kwargs)
                elapsed = time.monotonic() - t0
                self._record_success(elapsed)
                return result
            except Exception as exc:
                elapsed = time.monotonic() - t0
                self._record_failure(elapsed)
                raise exc

        with self._lock:
            pool = self._pool
        if pool is None:
            return None
        return pool.submit(_worker)

    def execute_sync(
        self,
        fn: Callable[..., Any],
        input_data: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute a computation synchronously (blocking).

        Raises ``RuntimeError`` if the shard is isolated.
        """
        with self._lock:
            if self._isolated:
                raise RuntimeError(f"Shard {self._shard_id} is isolated — cannot execute")

        t0 = time.monotonic()
        try:
            result = fn(input_data, *args, **kwargs)
            elapsed = time.monotonic() - t0
            self._record_success(elapsed)
            return result
        except Exception as exc:
            elapsed = time.monotonic() - t0
            self._record_failure(elapsed)
            raise exc

    # ------------------------------------------------------------------ #
    # Coherence gate
    # ------------------------------------------------------------------ #

    def validate_coherence(self) -> bool:
        """Re-run SCE-88 validation and update local coherence score.

        If the score drops below ``_COHERENCE_FLOOR``, the shard self-isolates.
        Returns ``True`` if coherence is acceptable.
        """
        result = sce88_validate(self._spec)
        with self._lock:
            if result["ok"]:
                self._coherence_score = float(result["containment_score"])
            else:
                self._coherence_score = 0.0
                self._constraint_violations += 1

            if self._coherence_score < _COHERENCE_FLOOR:
                self._isolated = True
                return False
            return True

    def isolate(self) -> None:
        """Manually isolate this shard (drain traffic away)."""
        with self._lock:
            self._isolated = True

    def rejoin(self) -> bool:
        """Attempt to rejoin after isolation.

        Only succeeds if coherence is above the floor.
        """
        result = sce88_validate(self._spec)
        with self._lock:
            if result["ok"]:
                self._coherence_score = float(result["containment_score"])
            if self._coherence_score >= _COHERENCE_FLOOR:
                self._isolated = False
                return True
            return False

    # ------------------------------------------------------------------ #
    # Metrics
    # ------------------------------------------------------------------ #

    def metrics(self) -> dict[str, Any]:
        """Return a snapshot of per-shard metrics."""
        with self._lock:
            throughput = (
                self._tasks_completed / max(self._total_compute_time, 1e-9)
                if self._tasks_completed
                else 0.0
            )
            return {
                "shard_id": self._shard_id,
                "tasks_completed": self._tasks_completed,
                "tasks_failed": self._tasks_failed,
                "constraint_violations": self._constraint_violations,
                "coherence_score": round(self._coherence_score, 6),
                "throughput": round(throughput, 4),
                "isolated": self._isolated,
                "total_compute_time": round(self._total_compute_time, 6),
            }

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #

    def _record_success(self, elapsed: float) -> None:
        with self._lock:
            self._tasks_completed += 1
            self._total_compute_time += elapsed

    def _record_failure(self, elapsed: float) -> None:
        with self._lock:
            self._tasks_failed += 1
            self._total_compute_time += elapsed
            # φ-decay coherence on failure
            self._coherence_score = max(0.0, self._coherence_score * (1.0 / PHI))
            if self._coherence_score < _COHERENCE_FLOOR:
                self._isolated = True
                self._constraint_violations += 1

    def __repr__(self) -> str:
        return (
            f"CellShard(id={self._shard_id}, workers={self._workers_per_shard}, "
            f"isolated={self._isolated})"
        )
