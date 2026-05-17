---
agent: agent_06 Lucas Analyst (Snell-Vern)
topic: cfrac_structure
params: {"n": 8}
generated_at: 2026-05-17T20:59:08.578410+00:00
library: recursive_field_math
---

# Continued fraction of L(9)/L(8)

## Claim

For n ≥ 2, L(n+1)/L(n) = [1; 1, 1, ..., 1, 3] with (n−2) ones.

## At n=8

- L(9)/L(8) = **76/47**
- continued fraction = **[1; 1, 1, 1, 1, 1, 1, 3]**
- number of internal ones = **6**
- tail term = **3**

## Notes

As n → ∞ the tail-3 gets pushed off to infinity and the expansion approaches
[1; 1, 1, 1, ...] = φ. Lucas ratios are therefore a deterministic family of
rational approximations to φ that converge with the slowest possible rate of
any irrational (all coefficients = 1 in the limit).
