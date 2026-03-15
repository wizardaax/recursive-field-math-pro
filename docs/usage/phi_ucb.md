# `phi_ucb` — φ-UCB Tree Search

φ-UCB is a variant of the classic UCB1 exploration bonus that replaces the
square-root term with a φ-power term.  The result tends to favour nodes whose
visit counts sit at Fibonacci/Lucas resonance points.

## Formula

```
φ-UCB(node) = Q/N  +  α · φ^β · sqrt(ln(t) / N)
```

where:
- `Q` — cumulative reward for the node
- `N` — visit count (`+inf` when `N = 0`, guaranteeing full exploration)
- `t` — total parent visit count (or global step)
- `α` — exploration coefficient (default 1.0)
- `β` — φ-power exponent (default 0.5)
- `φ` — the golden ratio ≈ 1.618

## Quick start

### Score a single node

```python
from recursive_field_math.phi_ucb import phi_ucb_score

node = {"q": 12.5, "n": 25}   # q = cumulative reward, n = visit count
score = phi_ucb_score(node, t=200, alpha=1.0, beta=0.5)
print(score)   # e.g. 0.854…

# Unvisited node always gets +inf
unvisited = {"q": 0.0, "n": 0}
assert phi_ucb_score(unvisited, t=1) == float("inf")
```

### Select the best child

```python
from recursive_field_math.phi_ucb import select_best

children = [
    {"q": 5.0,  "n": 10},
    {"q": 12.0, "n": 25},
    {"q": 3.0,  "n": 3},   # low visits → high exploration bonus
]
best_index, best_score = select_best(children, t=100)
print(best_index, best_score)
```

### Benchmark against UCB1

```python
from recursive_field_math.phi_ucb import benchmark_phi_ucb_vs_ucb1

result = benchmark_phi_ucb_vs_ucb1(n_arms=5, n_steps=500, seed=42)
print(result["phi_ucb_cumulative_reward"])
print(result["ucb1_cumulative_reward"])
print(result["phi_ucb_regret"])   # vs the optimal arm
```

## Key parameters

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `alpha` | 1.0 | Overall exploration coefficient |
| `beta` | 0.5 | φ-power exponent; `β=0` → `φ^0 = 1` → reduces to pure UCB1 |

## Tips

* Set `beta=0` to fall back to standard UCB1 for A/B comparison.
* `select_best` returns `(index, score)` — use the index to identify which
  child to expand next.
* All inputs must satisfy `q >= 0` and `n >= 0`.  Negative values raise
  `ValueError`.
