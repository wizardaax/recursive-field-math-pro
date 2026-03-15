# `structural_detector` — Structural Pattern Detector

Analyses an input sequence and produces three diagnostics about its internal
structure.  The module deliberately avoids claims about *meaning*: it measures
observable patterns (repetition, interval regularity, distributional uniformity)
and nothing more.

## What it produces

| Field | Type | Range | Meaning |
|-------|------|-------|---------|
| `structural_signature` | list[float] | each ∈ [0, 1] | φ-harmonic coefficient vector (8 values by default). A compact fingerprint of the sequence's repetition and interval structure. |
| `anomaly_index` | float | [0, 1] | How strongly the sequence deviates from a φ-coherent baseline. Higher = more anomalous. |
| `coherence_trace` | list[float] | each ∈ [0, 1] | Per-window coherence values. Inspect *where* structure holds or breaks. |
| `ok` | bool | — | `False` when the sequence is too short or degenerate. |

## Quick start

```python
from recursive_field_math.structural_detector import detect

# Fibonacci sequence — high coherence, low anomaly
result = detect([1, 1, 2, 3, 5, 8, 13, 21, 34, 55])
assert result["ok"] is True
print(result["anomaly_index"])          # e.g. 0.12 (low)
print(result["structural_signature"])   # 8 normalised φ-harmonic coefficients
print(result["coherence_trace"])        # per-window coherence

# Random noise — high anomaly
import random
random.seed(0)
noisy = [random.gauss(0, 1) for _ in range(20)]
result = detect(noisy)
print(result["anomaly_index"])   # typically high
```

## Fail-closed example

```python
result = detect([1, 2, 3])   # too short (need ≥ 6)
assert result["ok"] is False
print(result["reason"])
```

## Working with the coherence trace

The `coherence_trace` has one value per sliding window.  Use it to pinpoint
exactly where structure breaks down:

```python
result = detect(my_sequence)
for i, c in enumerate(result["coherence_trace"]):
    if c < 0.3:
        print(f"Window {i}: low coherence ({c:.3f})")
```

## Key constants

```python
from recursive_field_math.structural_detector import (
    MIN_LENGTH,        # 6  — minimum sequence length
    WINDOW_SIZE,       # 4  — sliding window width for coherence trace
    N_HARMONICS,       # 8  — number of φ-harmonic coefficients in signature
    ANOMALY_THRESHOLD, # 0.7 — above this a window is flagged as anomalous
)
```

## Tips

* The `structural_signature` can be used as a feature vector for downstream
  classifiers or similarity comparisons.
* `anomaly_index` is derived from the fraction of windows above
  `ANOMALY_THRESHOLD`.  An index near 1.0 means nearly every window is anomalous.
* The module accepts any sequence of numbers or hashable tokens; non-float
  values are cast to float internally.
