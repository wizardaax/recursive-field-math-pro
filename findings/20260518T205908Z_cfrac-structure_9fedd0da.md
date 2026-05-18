---
agent: agent_06 Lucas Analyst (Snell-Vern)
topic: cfrac_structure
params: {"n": 12}
generated_at: 2026-05-18T20:59:08.683785+00:00
library: recursive_field_math
---

# Continued fraction of L(13)/L(12)

## Claim

For n ≥ 2, L(n+1)/L(n) = [1; 1, 1, ..., 1, 3] with (n−2) ones.

## At n=12

- L(13)/L(12) = **521/322**
- continued fraction = **[1; 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3]**
- number of internal ones = **10**
- tail term = **3**

## Notes

As n → ∞ the tail-3 gets pushed off to infinity and the expansion approaches
[1; 1, 1, 1, ...] = φ. Lucas ratios are therefore a deterministic family of
rational approximations to φ that converge with the slowest possible rate of
any irrational (all coefficients = 1 in the limit).
