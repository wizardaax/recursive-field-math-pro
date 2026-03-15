# `eval_api` — RFF Evaluation API

Deterministic scoring of ordered sequences using the **`rff_v1`** profile.

## What it produces

| Field | Type | Range | Meaning |
|-------|------|-------|---------|
| `coherence` | float | [0, 1] | How well the sequence follows φ-weighted autocorrelation. Higher = more structurally regular. |
| `entropy` | float | [0, 1] | Normalised Shannon entropy of the relative-change distribution. Higher = more uniform / less predictable. |
| `confidence` | float | [0, 1] | Calibrated certainty that the scores are meaningful. Falls to 0 for short or degenerate sequences. |
| `ok` | bool | — | `True` when confidence ≥ threshold. `False` when the call is fail-closed. |
| `profile` | str | — | Always `"rff_v1"` — use this to version-gate downstream logic. |

The call is **fail-closed**: when `confidence` is below `CONFIDENCE_THRESHOLD`
(default 0.10) the returned dict has `"ok": False` and a human-readable
`"reason"` field instead of misleading scores.

## Quick start

```python
from recursive_field_math.eval_api import score

# --- Fibonacci-like sequence (high coherence) ---
result = score([1, 1, 2, 3, 5, 8, 13, 21], mode="numeric")
assert result["ok"] is True
print(result["coherence"])   # e.g. 0.82
print(result["entropy"])     # e.g. 0.61
print(result["profile"])     # "rff_v1"

# --- Token-id sequence ---
result = score([42, 17, 3, 99, 5, 2, 71, 8], mode="tokens")
print(result)

# --- Action sequence (game moves, API calls, …) ---
result = score([0, 1, 0, 2, 1, 0, 3, 1], mode="actions")
print(result)
```

## Fail-closed example

```python
result = score([1, 2, 3], mode="numeric")   # too short
assert result["ok"] is False
print(result["reason"])   # "sequence too short: need ≥ 4 values, got 3"
```

## Modes

| Mode | Input type | Description |
|------|-----------|-------------|
| `"numeric"` | `Sequence[float \| int]` | Raw numeric values; used as-is. |
| `"tokens"` | `Sequence[int]` | Integer token IDs converted to ordinal ranks before scoring. |
| `"actions"` | `Sequence[int]` | Same pipeline as `"tokens"`. |

## Key constants

```python
from recursive_field_math.eval_api import (
    PROFILE_NAME,          # "rff_v1"
    MIN_LENGTH,            # 4  — sequences shorter than this → ok=False
    CONFIDENCE_THRESHOLD,  # 0.10
)
```

## Tips

* All three scalars are always in **[0, 1]** when `ok` is `True`.
* The output is **deterministic**: the same input always yields the same dict.
* Use `result["profile"]` to version-gate downstream logic so future profile
  changes don't silently alter behaviour.
