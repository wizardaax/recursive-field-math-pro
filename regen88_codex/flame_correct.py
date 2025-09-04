import math
from .utils import PHI
from typing import List

def phi_correct_drift(phases: List[float]) -> List[float]:
    return [(p * PHI) % (2 * math.pi) for p in phases]
