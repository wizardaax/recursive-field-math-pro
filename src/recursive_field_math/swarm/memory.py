"""
Externalised state store for the cellular swarm.

Workers are stateless: they spawn, compute, return a result, and terminate.
All persistent state lives here in ``SwarmMemory``, which is thread-safe and
deterministic (insertion-ordered, no random eviction).

Zero new runtime dependencies — uses only stdlib collections + threading.
"""

from __future__ import annotations

import threading
from typing import Any


class SwarmMemory:
    """Thread-safe, deterministic key/value state store.

    Parameters
    ----------
    max_entries:
        Upper bound on stored entries.  When exceeded the *oldest* entry is
        evicted (FIFO), keeping behaviour deterministic.

    Examples
    --------
    >>> mem = SwarmMemory(max_entries=100)
    >>> mem.put("k1", {"value": 42})
    >>> mem.get("k1")
    {'value': 42}
    """

    def __init__(self, max_entries: int = 10_000) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be >= 1")
        self._max_entries = max_entries
        self._store: dict[str, Any] = {}
        self._insertion_order: list[str] = []
        self._lock = threading.Lock()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def put(self, key: str, value: Any) -> None:
        """Store *value* under *key*, evicting the oldest entry if full."""
        with self._lock:
            if key in self._store:
                self._store[key] = value
                return
            # Evict oldest if at capacity
            while len(self._store) >= self._max_entries:
                oldest = self._insertion_order.pop(0)
                del self._store[oldest]
            self._store[key] = value
            self._insertion_order.append(key)

    def get(self, key: str, default: Any = None) -> Any:
        """Return the value for *key*, or *default* if absent."""
        with self._lock:
            return self._store.get(key, default)

    def delete(self, key: str) -> bool:
        """Remove *key* and return ``True`` if it existed."""
        with self._lock:
            if key in self._store:
                del self._store[key]
                self._insertion_order.remove(key)
                return True
            return False

    def keys(self) -> list[str]:
        """Return a snapshot of all keys in insertion order."""
        with self._lock:
            return list(self._insertion_order)

    def size(self) -> int:
        """Return the number of stored entries."""
        with self._lock:
            return len(self._store)

    def clear(self) -> None:
        """Remove all entries."""
        with self._lock:
            self._store.clear()
            self._insertion_order.clear()

    def snapshot(self) -> dict[str, Any]:
        """Return a shallow copy of all stored data."""
        with self._lock:
            return dict(self._store)

    @property
    def max_entries(self) -> int:
        """Maximum capacity of this memory store."""
        return self._max_entries

    def stats(self) -> dict[str, Any]:
        """Return diagnostic statistics."""
        with self._lock:
            return {
                "size": len(self._store),
                "max_entries": self._max_entries,
                "utilisation": (
                    round(len(self._store) / self._max_entries, 6) if self._max_entries > 0 else 0.0
                ),
            }

    def get_or_put(self, key: str, default_factory: Any | None = None) -> Any:
        """Return value for *key* if present, otherwise store and return *default_factory()*.

        Parameters
        ----------
        key:
            The lookup key.
        default_factory:
            A callable returning the default value.  Called only when *key*
            is absent.
        """
        with self._lock:
            if key in self._store:
                return self._store[key]
        # Not found — compute outside lock, then store
        if default_factory is not None:
            value = default_factory() if callable(default_factory) else default_factory
        else:
            value = None
        self.put(key, value)
        return value
