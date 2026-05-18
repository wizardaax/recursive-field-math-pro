---
agent: agent_06 Lucas Analyst (Snell-Vern)
topic: ratio_convergence
params: {"n": 18}
generated_at: 2026-05-18T12:59:09.159253+00:00
library: recursive_field_math
---

# Lucas ratio convergence at n=18

## Claim

`L(n+1)/L(n) → φ` with rigorous bounds `√5/(L_n(L_n+|ψ|^n)) ≤ |L(n+1)/L(n) − φ| ≤ √5/(L_n(L_n−|ψ|^n))`.

## Measurement at n=18

- L(n+1)/L(n) = **1.6180339217722395**
- φ           = **1.6180339887498949**
- Observed |err|     = **6.698e-08**
- Lower error bound  = **6.698e-08**
- Upper error bound  = **6.698e-08**
- Within bounds?     = **False**

## Notes

Convergence rate is geometric in |ψ|^n where ψ = 1 − φ ≈ −0.618. The bounds
are derived from the identity L_n = φⁿ + ψⁿ and become tight (upper/lower → 1)
for moderate n.
