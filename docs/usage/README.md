# Usage Guides — v0.5.0-substrate

Per-module guides for the five substrate modules shipped in v0.5.0.

| Guide | Module | Key public API |
|-------|--------|---------------|
| [eval_api.md](eval_api.md) | `recursive_field_math.eval_api` | `score()` |
| [phi_ucb.md](phi_ucb.md) | `recursive_field_math.phi_ucb` | `phi_ucb_score()`, `select_best()`, `benchmark_phi_ucb_vs_ucb1()` |
| [structural_detector.md](structural_detector.md) | `recursive_field_math.structural_detector` | `detect()` |
| [containment_validator.md](containment_validator.md) | `recursive_field_math.containment_validator` | `validate()` |
| [xdomain_bridge.md](xdomain_bridge.md) | `recursive_field_math.xdomain_bridge` | `encode()`, `decode()`, `bridge()`, `register_adapter()` |

## Common patterns

### All modules are fail-closed

Every public function returns (or raises, for `xdomain_bridge`) a structured
error when input is degenerate, rather than silently returning meaningless
results.  Always check `result["ok"]` before using scores:

```python
result = score(my_sequence)
if not result["ok"]:
    print(result["reason"])
else:
    print(result["coherence"])
```

### Profile / version fields

Every result dict carries a `"profile"` key so downstream logic can be
version-gated:

```python
assert result["profile"] == "rff_v1"   # eval_api
assert lv["profile"] == "xbridge_v1"   # xdomain_bridge
```

## Installation

```bash
pip install regen88-codex==0.5.0
```

```python
import recursive_field_math
from recursive_field_math.eval_api            import score
from recursive_field_math.phi_ucb             import phi_ucb_score, select_best
from recursive_field_math.structural_detector import detect
from recursive_field_math.containment_validator import validate
from recursive_field_math.xdomain_bridge      import encode, decode, bridge
```
