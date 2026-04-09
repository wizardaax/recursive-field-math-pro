"""
Cellular swarm architecture for recursive field math.

Provides a coherence-gated, hardware-aware swarm of independent execution
cells (shards) connected via a deterministic pipeline.  All routing is
hash-based and all workers are stateless, guaranteeing reproducibility at
any scale.

Public API
~~~~~~~~~~
- ``CellShard``          – independent execution unit with local coherence gate
- ``SwarmMemory``        – externalised state store shared across shards
- ``PipelineStage``      – ingest → compute → validate → output stage
- ``Pipeline``           – ordered chain of ``PipelineStage`` instances
- ``CoherenceGovernor``  – monitors coherence/compute ratio, triggers consolidation
- ``SwarmOrchestrator``  – hardware-aware orchestrator managing shards + pipeline
"""

from .cell import CellShard
from .coherence_governor import CoherenceGovernor
from .memory import SwarmMemory
from .orchestrator import SwarmOrchestrator
from .pipeline import Pipeline, PipelineStage

__all__ = [
    "CellShard",
    "CoherenceGovernor",
    "Pipeline",
    "PipelineStage",
    "SwarmMemory",
    "SwarmOrchestrator",
]
