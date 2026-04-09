"""
Evolution engine for recursive self-improvement of the agent federation mesh.

Provides ``EvolutionEngine`` — a deterministic, thread-safe engine that
observes agent performance, proposes structural improvements, simulates
them in sandboxed isolation, and outputs versioned change sets with
provenance logging and human-gate flags.
"""

from .meta_engine import EvolutionEngine

__all__ = ["EvolutionEngine"]
