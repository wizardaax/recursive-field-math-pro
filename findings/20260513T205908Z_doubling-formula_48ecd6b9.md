---
agent: agent_06 Lucas Analyst (Snell-Vern)
topic: doubling_formula
params: {"n": 4}
generated_at: 2026-05-13T20:59:08.646537+00:00
library: recursive_field_math
---

# Lucas doubling formula at n=4

## Claim

`L(2n) = L(n)² − 2·(−1)^n`

## At n=4

- L(8)       = **47**
- L(4)         = **7**
- L(4)² − 2·(−1)^4 = **47**
- Equal? **True**

## Notes

This doubling identity is a corollary of L(m+n) = L(m)·L(n) − (−1)^n·L(m−n)
with m = n. It lets L(2n) be computed from L(n) in one multiply, making
a binary-doubling algorithm O(log n) instead of O(n).
