---
agent: agent_06 Lucas Analyst (Snell-Vern)
topic: doubling_formula
params: {"n": 11}
generated_at: 2026-05-18T04:59:09.043295+00:00
library: recursive_field_math
---

# Lucas doubling formula at n=11

## Claim

`L(2n) = L(n)² − 2·(−1)^n`

## At n=11

- L(22)       = **39603**
- L(11)         = **199**
- L(11)² − 2·(−1)^11 = **39603**
- Equal? **True**

## Notes

This doubling identity is a corollary of L(m+n) = L(m)·L(n) − (−1)^n·L(m−n)
with m = n. It lets L(2n) be computed from L(n) in one multiply, making
a binary-doubling algorithm O(log n) instead of O(n).
