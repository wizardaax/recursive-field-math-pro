from .constants import PHI, PSI, ROOT_SCALE
from .containment_validator import validate as validate_containment
from .continued_fraction import lucas_ratio_cfrac
from .egyptian_fraction import egypt_4_7_11
from .eval_api import PROFILE_NAME as RFF_PROFILE
from .eval_api import calibration_report, score
from .fibonacci import F
from .field import r_theta
from .generating_functions import GF_F, GF_L
from .lucas import L
from .phi_ucb import benchmark_phi_ucb_vs_ucb1, phi_ucb_score, select_best
from .ratios import ratio, ratio_error_bounds
from .self_model import SelfModel
from .signatures import signature_summary
from .structural_detector import detect as detect_structure
from .swarm import (
    CellShard,
    CoherenceGovernor,
    Pipeline,
    PipelineStage,
    SwarmMemory,
    SwarmOrchestrator,
)
from .xdomain_bridge import BridgeError, bridge, decode, encode, register_adapter

__all__ = [
    # --- original symbols ---
    "PHI",
    "PSI",
    "ROOT_SCALE",
    "F",
    "L",
    "r_theta",
    "ratio",
    "ratio_error_bounds",
    "lucas_ratio_cfrac",
    "GF_F",
    "GF_L",
    "egypt_4_7_11",
    "signature_summary",
    # --- RFF Evaluation API ---
    "RFF_PROFILE",
    "score",
    "calibration_report",
    # --- φ-UCB Search ---
    "phi_ucb_score",
    "select_best",
    "benchmark_phi_ucb_vs_ucb1",
    # --- Structural Detector ---
    "detect_structure",
    # --- Self-Model ---
    "SelfModel",
    # --- Containment Geometry Validator ---
    "validate_containment",
    # --- Cross-Domain Bridge ---
    "encode",
    "decode",
    "bridge",
    "register_adapter",
    "BridgeError",
    # --- Cellular Swarm ---
    "CellShard",
    "CoherenceGovernor",
    "Pipeline",
    "PipelineStage",
    "SwarmMemory",
    "SwarmOrchestrator",
]
