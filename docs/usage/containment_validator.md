# `containment_validator` — Containment Geometry Validator

Audits a layered-architecture specification (expressed as a plain Python dict,
JSON, or YAML) and returns a structural containment analysis.

> **Important scope note:** this validator reasons about *structural geometry*
> (how layers declare dependencies on each other) and **not** about runtime
> behaviour.  A high containment score means the declared architecture has few
> cross-layer couplings; it does **not** prove that the running system is safe
> or secure.

## What it produces

| Field | Type | Range | Meaning |
|-------|------|-------|---------|
| `containment_score` | float | [0, 1] | Higher = architecture is more tightly self-contained (fewer escape paths). Uses φ-weighted layer coupling. |
| `weak_layer_map` | dict[str, float] | values ∈ [0, 1] | Per-layer weakness score. High scores indicate candidates for hardening. |
| `escape_path_candidates` | list[tuple] | — | `(from_layer, to_layer, severity)` tuples for the most likely containment failures. |
| `ok` | bool | — | `False` when the spec is invalid or has fewer than two layers. |

## Spec format

```python
spec = {
    "layers": {
        "<layer_name>": {
            "depends_on": ["<other_layer>", …],  # optional
            "weight":     1.0,                    # optional importance weight
            "public_api": True,                   # optional
        },
        …
    }
}
```

The only required key is `"layers"` with at least two entries.

## Quick start

```python
from recursive_field_math.containment_validator import validate

spec = {
    "layers": {
        "core":    {"depends_on": []},
        "service": {"depends_on": ["core"]},
        "api":     {"depends_on": ["service"]},
    }
}

result = validate(spec)
assert result["ok"] is True
print(result["containment_score"])        # e.g. 0.87 — well-contained
print(result["weak_layer_map"])           # {"core": 0.0, "service": 0.2, "api": 0.3}
print(result["escape_path_candidates"])   # [] — no escape paths found
```

## Detecting coupling problems

```python
leaky_spec = {
    "layers": {
        "core":    {"depends_on": []},
        "service": {"depends_on": ["core", "api"]},   # back-dependency!
        "api":     {"depends_on": ["service", "core"]},
    }
}

result = validate(leaky_spec)
print(result["containment_score"])        # lower score
print(result["escape_path_candidates"])   # lists problematic edges
```

## Top-k escape paths

```python
result = validate(spec, top_k_escapes=10)   # surface up to 10 candidates
for from_l, to_l, severity in result["escape_path_candidates"]:
    print(f"{from_l} → {to_l}: severity={severity:.3f}")
```

## Fail-closed example

```python
result = validate({"layers": {"only_one": {}}})   # need ≥ 2 layers
assert result["ok"] is False
print(result["reason"])
```

## Tips

* Start by addressing the highest-severity entries in `escape_path_candidates`.
* Layers with `weight > 1.0` amplify their coupling impact; use this to flag
  security-critical layers.
* The score is φ-weighted: layers at higher topological depth contribute more
  to the overall containment measure.
