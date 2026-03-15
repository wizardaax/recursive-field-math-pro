# `xdomain_bridge` — Cross-Domain Bridge

Provides a common **φ-harmonic latent geometry** and bidirectional domain
adapters.  Any supported domain sequence can be encoded into a normalised
`LatentVector` and decoded back, with a guaranteed round-trip error bound.

## Core guarantee

For every registered adapter the round-trip relative error is bounded:

```
|decode(encode(x)) - x| / rms(x)  ≤  ERROR_BOUND  (default 0.10)
```

If this bound would be exceeded, `encode` / `decode` raises `BridgeError`
rather than silently returning a degraded result (**fail-closed**).

## `LatentVector` schema

```python
{
    "values":   [float, …],  # N_LATENT (16) normalised φ-harmonic coefficients
    "norm":     float,       # original RMS — used for scale recovery on decode
    "domain":   str,         # source domain tag, e.g. "numeric"
    "profile":  str,         # always "xbridge_v1"
    "n_input":  int,         # original input length
}
```

## Quick start

### Encode and decode

```python
from recursive_field_math.xdomain_bridge import encode, decode

# Encode a numeric sequence into the latent space
lv = encode([1, 1, 2, 3, 5, 8, 13, 21], domain="numeric")
print(lv["domain"])    # "numeric"
print(lv["profile"])   # "xbridge_v1"
print(len(lv["values"]))  # 16

# Decode back to the original domain
reconstructed = decode(lv)
print(len(reconstructed))   # 8 — same length as the input
```

### Bridge two sequences together

```python
from recursive_field_math.xdomain_bridge import bridge

# Compare two sequences from different domains in shared latent space
similarity = bridge(
    [1, 1, 2, 3, 5, 8, 13, 21],   # numeric
    [0, 1, 1, 2, 3, 5, 8, 13],    # tokens
    domain_a="numeric",
    domain_b="tokens",
)
print(similarity["cosine_similarity"])   # latent-space cosine similarity
print(similarity["profile"])             # "xbridge_v1"
```

## Built-in domain adapters

| Domain tag | Input type | Adapter behaviour |
|-----------|-----------|------------------|
| `"numeric"` | `Sequence[float \| int]` | Values used as-is |
| `"tokens"` | `Sequence[int]` | Token IDs converted to ordinal ranks |
| `"actions"` | `Sequence[int]` | Same pipeline as `"tokens"` |

## Registering a custom adapter

```python
from recursive_field_math.xdomain_bridge import register_adapter, encode

def my_text_adapter(seq):
    """Convert a list of characters to float codepoints."""
    return [float(ord(c)) for c in seq]

register_adapter("text", my_text_adapter)

lv = encode(list("hello world"), domain="text")
print(lv["domain"])   # "text"
```

## Fail-closed examples

```python
from recursive_field_math.xdomain_bridge import encode, BridgeError

# Too short
try:
    encode([1, 2, 3], domain="numeric")   # need ≥ MIN_INPUT_LENGTH (4)
except BridgeError as e:
    print(e)

# Round-trip error exceeded (rare; indicates a very degenerate sequence)
try:
    lv = encode(degenerate_seq, domain="numeric")
except BridgeError as e:
    print(e)
```

## Key constants

```python
from recursive_field_math.xdomain_bridge import (
    N_LATENT,          # 16 — dimensionality of the latent vector
    MIN_INPUT_LENGTH,  # 4  — minimum input sequence length
    ERROR_BOUND,       # 0.10 — max allowable round-trip relative error
    BRIDGE_PROFILE,    # "xbridge_v1"
)
```

## Tips

* Use `bridge()` to compute latent-space similarity between sequences from
  different domains without manually managing encode/decode.
* The `"norm"` field in the `LatentVector` is essential for correct decoding —
  never discard it when storing a vector.
* Custom adapters must return a `list[float]` of length ≥ `MIN_INPUT_LENGTH`.
