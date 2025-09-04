import math
from .utils import PHI

def shard_isolate(trace):
    cleaned = []
    for step in trace:
        if 'corrupt' in step:
            continue
        step['phase'] = (step['phase'] * PHI) % (2 * math.pi)
        cleaned.append(step)
    return cleaned
