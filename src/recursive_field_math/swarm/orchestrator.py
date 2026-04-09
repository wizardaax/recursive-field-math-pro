"""
SwarmOrchestrator — hardware-aware orchestrator for the cellular swarm.

Manages a pool of ``CellShard`` instances, routes tasks via deterministic
hashing, and coordinates with the ``CoherenceGovernor`` for graceful
degradation.

Hardware-aware pool sizing
~~~~~~~~~~~~~~~~~~~~~~~~~~
``max_workers = min(cpu_cores * 2, available_RAM / worker_footprint)``

Graceful degradation
~~~~~~~~~~~~~~~~~~~~
Shards auto-isolate on violation; traffic drains to healthy shards.  A
global halt is triggered **only** when global coherence breaches the
governor's floor.

Zero new runtime dependencies.
"""

from __future__ import annotations

import os
import threading
from collections.abc import Sequence
from typing import Any, Callable

from ..containment_validator import validate as sce88_validate
from .cell import CellShard, deterministic_route
from .coherence_governor import CoherenceGovernor
from .memory import SwarmMemory
from .pipeline import Pipeline, PipelineStage

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

_DEFAULT_WORKER_FOOTPRINT_MB: int = 50  # estimated per-worker memory in MB
_FALLBACK_RAM_MB: int = 4096  # 4 GB assumed if detection fails


# --------------------------------------------------------------------------- #
# Hardware detection helpers
# --------------------------------------------------------------------------- #


def _detect_cpu_cores() -> int:
    """Return the number of usable CPU cores, minimum 1."""
    try:
        count = os.cpu_count()
        return max(1, count or 1)
    except Exception:
        return 1


def _detect_available_ram_mb() -> int:
    """Best-effort RAM detection (Linux /proc/meminfo, else fallback)."""
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable"):
                    kb = int(line.split()[1])
                    return max(1, kb // 1024)
    except Exception:
        pass
    return _FALLBACK_RAM_MB


def compute_max_workers(
    cpu_cores: int | None = None,
    available_ram_mb: int | None = None,
    worker_footprint_mb: int = _DEFAULT_WORKER_FOOTPRINT_MB,
) -> int:
    """Hardware-aware maximum worker count.

    ``max_workers = min(cpu_cores * 2, available_RAM / worker_footprint)``
    """
    cores = cpu_cores if cpu_cores is not None else _detect_cpu_cores()
    ram = available_ram_mb if available_ram_mb is not None else _detect_available_ram_mb()
    by_cpu = cores * 2
    by_ram = max(1, ram // max(1, worker_footprint_mb))
    return max(1, min(by_cpu, by_ram))


# --------------------------------------------------------------------------- #
# SwarmOrchestrator
# --------------------------------------------------------------------------- #


class SwarmOrchestrator:
    """Hardware-aware orchestrator managing shards, pipeline, and governor.

    Parameters
    ----------
    num_shards:
        Number of ``CellShard`` instances.
    workers_per_shard:
        Workers per shard (auto-capped by hardware limits).
    memory:
        Shared ``SwarmMemory`` instance.
    governor:
        ``CoherenceGovernor`` instance (created automatically if omitted).
    pipeline_batch_size:
        Batch size for pipeline stages.
    efficiency_mode:
        One of ``"balanced"``, ``"throughput"``, ``"coherence-strict"``.
    """

    def __init__(
        self,
        num_shards: int = 4,
        workers_per_shard: int = 4,
        memory: SwarmMemory | None = None,
        governor: CoherenceGovernor | None = None,
        pipeline_batch_size: int = 16,
        efficiency_mode: str = "balanced",
    ) -> None:
        self._lock = threading.Lock()
        self._memory = memory or SwarmMemory()
        self._governor = governor or CoherenceGovernor()
        self._efficiency_mode = efficiency_mode
        self._started = False

        # Hardware-aware limits
        hw_max = compute_max_workers()
        total_requested = num_shards * workers_per_shard
        if total_requested > hw_max:
            # Scale down workers_per_shard, keep num_shards
            workers_per_shard = max(1, hw_max // max(1, num_shards))

        self._num_shards = max(1, num_shards)
        self._workers_per_shard = max(1, workers_per_shard)

        # Create shards
        self._shards: list[CellShard] = [
            CellShard(
                shard_id=i,
                workers_per_shard=self._workers_per_shard,
                memory=self._memory,
            )
            for i in range(self._num_shards)
        ]

        # Build default pipeline: ingest → compute → validate → output
        self._pipeline = Pipeline(
            [
                PipelineStage("ingest", lambda x: x, batch_size=pipeline_batch_size),
                PipelineStage("compute", lambda x: x, batch_size=pipeline_batch_size),
                PipelineStage(
                    "validate",
                    self._validate_item,
                    batch_size=pipeline_batch_size,
                ),
                PipelineStage("output", lambda x: x, batch_size=pipeline_batch_size),
            ]
        )

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #

    def start(self) -> None:
        """Start all shards."""
        with self._lock:
            for shard in self._shards:
                shard.start()
            self._started = True

    def stop(self) -> None:
        """Shutdown all shards gracefully."""
        with self._lock:
            for shard in self._shards:
                shard.stop()
            self._started = False

    @property
    def started(self) -> bool:
        with self._lock:
            return self._started

    # ------------------------------------------------------------------ #
    # Routing & execution
    # ------------------------------------------------------------------ #

    def route(self, input_data: str) -> int:
        """Deterministic routing: input → shard index."""
        return deterministic_route(input_data, self._num_shards)

    def _find_healthy_shard(self, preferred: int) -> CellShard | None:
        """Return the preferred shard if healthy, else first healthy one."""
        shard = self._shards[preferred]
        if not shard.isolated:
            return shard
        # Drain to first healthy shard
        for s in self._shards:
            if not s.isolated:
                return s
        return None

    def execute(
        self,
        fn: Callable[..., Any],
        input_data: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Route input to the correct shard and execute synchronously.

        Raises ``RuntimeError`` if no healthy shards are available.
        """
        # Check governor
        if self._governor.halt_triggered:
            raise RuntimeError("Global halt — coherence breached floor")

        shard_idx = self.route(input_data)
        shard = self._find_healthy_shard(shard_idx)
        if shard is None:
            raise RuntimeError("No healthy shards available")

        result = shard.execute_sync(fn, input_data, *args, **kwargs)

        # Update governor with aggregated metrics
        self._update_governor()
        return result

    def execute_batch(
        self,
        fn: Callable[..., Any],
        inputs: Sequence[str],
    ) -> list[Any]:
        """Execute a batch of inputs, routing each deterministically."""
        results: list[Any] = []
        for inp in inputs:
            try:
                r = self.execute(fn, inp)
                results.append(r)
            except RuntimeError:
                results.append(None)
        self._update_governor()
        return results

    # ------------------------------------------------------------------ #
    # Pipeline integration
    # ------------------------------------------------------------------ #

    @property
    def pipeline(self) -> Pipeline:
        return self._pipeline

    def set_pipeline(self, pipeline: Pipeline) -> None:
        """Replace the default pipeline with a custom one."""
        with self._lock:
            self._pipeline = pipeline

    # ------------------------------------------------------------------ #
    # Scaling
    # ------------------------------------------------------------------ #

    def scale_auto(self) -> dict[str, Any]:
        """Auto-scale based on hardware and coherence governor feedback.

        Returns a summary of scaling actions taken.
        """
        hw_max = compute_max_workers()
        recommended = self._governor.recommended_workers(self._num_shards * self._workers_per_shard)
        actual_total = min(recommended, hw_max)
        new_wps = max(1, actual_total // max(1, self._num_shards))

        actions: list[str] = []
        if new_wps != self._workers_per_shard:
            actions.append(f"workers_per_shard: {self._workers_per_shard} → {new_wps}")
            self._workers_per_shard = new_wps

        return {
            "hw_max_workers": hw_max,
            "governor_recommended": recommended,
            "actual_total_workers": actual_total,
            "workers_per_shard": new_wps,
            "num_shards": self._num_shards,
            "actions": actions,
        }

    # ------------------------------------------------------------------ #
    # Status / metrics
    # ------------------------------------------------------------------ #

    def status(self) -> dict[str, Any]:
        """Return full orchestrator status."""
        shard_metrics = [s.metrics() for s in self._shards]
        healthy = sum(1 for s in self._shards if not s.isolated)
        total_completed = sum(m["tasks_completed"] for m in shard_metrics)
        total_failed = sum(m["tasks_failed"] for m in shard_metrics)

        # Aggregate coherence
        scores = [m["coherence_score"] for m in shard_metrics if not m["isolated"]]
        avg_coherence = sum(scores) / len(scores) if scores else 0.0

        governor_m = self._governor.metrics()

        return {
            "num_shards": self._num_shards,
            "healthy_shards": healthy,
            "workers_per_shard": self._workers_per_shard,
            "total_workers": self._num_shards * self._workers_per_shard,
            "tasks_completed": total_completed,
            "tasks_failed": total_failed,
            "avg_coherence": round(avg_coherence, 6),
            "coherence_compute_ratio": governor_m["coherence_compute_ratio"],
            "throttle_active": governor_m["throttle_active"],
            "halt_triggered": governor_m["halt_triggered"],
            "efficiency_mode": self._efficiency_mode,
            "shards": shard_metrics,
            "pipeline": self._pipeline.metrics(),
        }

    # ------------------------------------------------------------------ #
    # Governor
    # ------------------------------------------------------------------ #

    @property
    def governor(self) -> CoherenceGovernor:
        return self._governor

    @property
    def memory(self) -> SwarmMemory:
        return self._memory

    @property
    def shards(self) -> list[CellShard]:
        return list(self._shards)

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #

    def _update_governor(self) -> None:
        """Push aggregated shard metrics to the governor."""
        scores = [s.coherence_score for s in self._shards if not s.isolated]
        avg = sum(scores) / len(scores) if scores else 0.0
        active = sum(1 for s in self._shards if not s.isolated) * self._workers_per_shard
        self._governor.update(avg, active)

    @staticmethod
    def _validate_item(item: Any) -> Any:
        """Pipeline validate stage — runs SCE-88 containment check."""
        spec = {
            "layers": {
                "ingest": {"depends_on": []},
                "compute": {"depends_on": ["ingest"]},
                "validate": {"depends_on": ["compute"]},
                "output": {"depends_on": ["validate"]},
            }
        }
        result = sce88_validate(spec)
        if result.get("ok"):
            return item
        return None
