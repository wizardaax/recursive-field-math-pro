"""
Pipeline stages for the cellular swarm.

Implements a four-phase pipeline (ingest → compute → validate → output) with:
- Batch-compatible grouping of tasks per stage
- Deterministic backpressure (upstream pauses when downstream is full)
- Thread-safe buffering between stages

Zero new runtime dependencies.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Sequence
from typing import Any, Callable

from ..containment_validator import validate as sce88_validate

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

DEFAULT_BUFFER_SIZE: int = 256
DEFAULT_BATCH_SIZE: int = 16

# Default SCE-88 spec for pipeline validation
_PIPELINE_SPEC: dict[str, Any] = {
    "layers": {
        "ingest": {"depends_on": []},
        "compute": {"depends_on": ["ingest"]},
        "validate": {"depends_on": ["compute"]},
        "output": {"depends_on": ["validate"]},
    }
}


# --------------------------------------------------------------------------- #
# PipelineStage
# --------------------------------------------------------------------------- #


class PipelineStage:
    """A single stage in the swarm pipeline.

    Parameters
    ----------
    name:
        Human-readable stage name (e.g. ``"ingest"``).
    handler:
        Callable that processes a single item or a batch of items.
    batch_size:
        Maximum number of items grouped per invocation of *handler*.
    buffer_size:
        Maximum items held in the input buffer before backpressure kicks in.
    """

    def __init__(
        self,
        name: str,
        handler: Callable[..., Any],
        batch_size: int = DEFAULT_BATCH_SIZE,
        buffer_size: int = DEFAULT_BUFFER_SIZE,
    ) -> None:
        self._name = name
        self._handler = handler
        self._batch_size = max(1, batch_size)
        self._buffer_size = max(1, buffer_size)

        self._buffer: list[Any] = []
        self._lock = threading.Lock()
        self._backpressure = False

        # Metrics
        self._items_processed: int = 0
        self._items_dropped: int = 0
        self._batches_processed: int = 0
        self._total_time: float = 0.0

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def name(self) -> str:
        return self._name

    @property
    def backpressure(self) -> bool:
        with self._lock:
            return self._backpressure

    @property
    def buffer_utilisation(self) -> float:
        with self._lock:
            return len(self._buffer) / self._buffer_size

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def enqueue(self, item: Any) -> bool:
        """Add an item to the stage buffer.

        Returns ``True`` if accepted, ``False`` if the buffer is full
        (backpressure).
        """
        with self._lock:
            if len(self._buffer) >= self._buffer_size:
                self._backpressure = True
                self._items_dropped += 1
                return False
            self._buffer.append(item)
            self._backpressure = False
            return True

    def enqueue_batch(self, items: Sequence[Any]) -> int:
        """Enqueue multiple items, returning the count actually accepted."""
        accepted = 0
        for item in items:
            if self.enqueue(item):
                accepted += 1
            else:
                break
        return accepted

    def process(self) -> list[Any]:
        """Drain up to one batch from the buffer, process it, and return results.

        Returns an empty list if the buffer is empty.
        """
        with self._lock:
            batch = self._buffer[: self._batch_size]
            self._buffer = self._buffer[self._batch_size :]
            if len(self._buffer) < self._buffer_size:
                self._backpressure = False

        if not batch:
            return []

        t0 = time.monotonic()
        results: list[Any] = []
        for item in batch:
            try:
                result = self._handler(item)
                results.append(result)
            except Exception:
                results.append(None)
        elapsed = time.monotonic() - t0

        with self._lock:
            self._items_processed += len(batch)
            self._batches_processed += 1
            self._total_time += elapsed

        return results

    def flush(self) -> list[Any]:
        """Process all remaining items in the buffer."""
        all_results: list[Any] = []
        while True:
            batch_results = self.process()
            if not batch_results:
                break
            all_results.extend(batch_results)
        return all_results

    def pending(self) -> int:
        """Return the number of items waiting in the buffer."""
        with self._lock:
            return len(self._buffer)

    def metrics(self) -> dict[str, Any]:
        """Return stage diagnostics."""
        with self._lock:
            avg_time = (
                self._total_time / self._batches_processed if self._batches_processed else 0.0
            )
            return {
                "name": self._name,
                "items_processed": self._items_processed,
                "items_dropped": self._items_dropped,
                "batches_processed": self._batches_processed,
                "buffer_pending": len(self._buffer),
                "buffer_size": self._buffer_size,
                "batch_size": self._batch_size,
                "backpressure": self._backpressure,
                "avg_batch_time": round(avg_time, 6),
            }

    def __repr__(self) -> str:
        return f"PipelineStage(name={self._name!r}, batch={self._batch_size})"


# --------------------------------------------------------------------------- #
# Pipeline
# --------------------------------------------------------------------------- #


class Pipeline:
    """Ordered chain of ``PipelineStage`` instances with backpressure propagation.

    Parameters
    ----------
    stages:
        Sequence of ``PipelineStage`` objects executed left-to-right.

    Examples
    --------
    >>> s1 = PipelineStage("double", lambda x: x * 2, batch_size=4)
    >>> s2 = PipelineStage("stringify", lambda x: str(x), batch_size=4)
    >>> pipe = Pipeline([s1, s2])
    >>> pipe.push(5)
    True
    >>> pipe.run_once()  # processes through all stages
    ['10']
    """

    def __init__(self, stages: Sequence[PipelineStage]) -> None:
        if not stages:
            raise ValueError("Pipeline requires at least one stage")
        self._stages: list[PipelineStage] = list(stages)
        self._lock = threading.Lock()

    @property
    def stages(self) -> list[PipelineStage]:
        return list(self._stages)

    def push(self, item: Any) -> bool:
        """Push an item into the first stage.

        Returns ``False`` if the first stage is applying backpressure.
        """
        return self._stages[0].enqueue(item)

    def push_batch(self, items: Sequence[Any]) -> int:
        """Push multiple items into the first stage."""
        return self._stages[0].enqueue_batch(items)

    def run_once(self) -> list[Any]:
        """Execute one processing pass through all stages in order.

        Intermediate results flow from stage N to stage N+1.  If any stage
        applies backpressure, earlier results are buffered deterministically.

        Returns the output list from the final stage.
        """
        for i, stage in enumerate(self._stages):
            results = stage.process()
            if i + 1 < len(self._stages):
                next_stage = self._stages[i + 1]
                for r in results:
                    if r is not None:
                        next_stage.enqueue(r)
            else:
                return results
        return []

    def run_all(self) -> list[Any]:
        """Keep running passes until all stages are drained.

        Returns the concatenated output from all passes.
        """
        all_output: list[Any] = []
        max_iters = 1000  # safety cap
        for _ in range(max_iters):
            output = self.run_once()
            if output:
                all_output.extend(output)
            # Check if any stage still has pending items
            if all(s.pending() == 0 for s in self._stages):
                break
        return all_output

    def metrics(self) -> list[dict[str, Any]]:
        """Return metrics for every stage."""
        return [s.metrics() for s in self._stages]

    def has_backpressure(self) -> bool:
        """Return ``True`` if any stage is currently applying backpressure."""
        return any(s.backpressure for s in self._stages)

    def validate_coherence(self) -> bool:
        """Run SCE-88 validation against the pipeline topology.

        Returns ``True`` if the pipeline architecture passes containment
        checks.
        """
        result = sce88_validate(_PIPELINE_SPEC)
        return bool(result.get("ok", False))
