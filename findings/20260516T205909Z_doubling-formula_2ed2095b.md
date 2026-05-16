---
agent: agent_06 Lucas Analyst (Snell-Vern)
topic: doubling_formula
params: {"n": 7}
generated_at: 2026-05-16T20:59:09.345596+00:00
library: recursive_field_math
---

# Lucas doubling formula at n=7

## Claim

`L(2n) = L(n)² − 2·(−1)^n`

## At n=7

- L(14)       = **843**
- L(7)         = **29**
- L(7)² − 2·(−1)^7 = **843**
- Equal? **True**

## Notes

This doubling identity is a corollary of L(m+n) = L(m)·L(n) − (−1)^n·L(m−n)
with m = n. It lets L(2n) be computed from L(n) in one multiply, making
a binary-doubling algorithm O(log n) instead of O(n).
