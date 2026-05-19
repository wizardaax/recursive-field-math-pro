---
agent: agent_06 Lucas Analyst (Snell-Vern)
topic: doubling_formula
params: {"n": 18}
generated_at: 2026-05-19T04:59:08.724159+00:00
library: recursive_field_math
---

# Lucas doubling formula at n=18

## Claim

`L(2n) = L(n)² − 2·(−1)^n`

## At n=18

- L(36)       = **33385282**
- L(18)         = **5778**
- L(18)² − 2·(−1)^18 = **33385282**
- Equal? **True**

## Notes

This doubling identity is a corollary of L(m+n) = L(m)·L(n) − (−1)^n·L(m−n)
with m = n. It lets L(2n) be computed from L(n) in one multiply, making
a binary-doubling algorithm O(log n) instead of O(n).
