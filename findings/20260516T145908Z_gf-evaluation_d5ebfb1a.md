---
agent: agent_06 Lucas Analyst (Snell-Vern)
topic: gf_evaluation
params: {"x_recip": 4}
generated_at: 2026-05-16T14:59:08.489372+00:00
library: recursive_field_math
---

# Fibonacci generating function at x = 1/4

## Claim

`G_F(x) = x / (1 − x − x²) = Σ_{n≥0} F(n) x^n` converges for |x| < 1/φ ≈ 0.618.

## At x = 1/4 = 0.2500000000

- Closed form `x/(1−x−x²)` = **0.363636363636**
- Partial sum Σ_{n=0..40} F(n)·x^n = **0.363636363636**
- |closed − partial| = **5.551e-17**
- |x| < 1/φ ≈ 0.6180 ? **True**

## Notes

Singularities at x = 1/φ and x = 1/ψ control growth: F(n) ~ φⁿ/√5. The
truncated sum's residual error after N terms is bounded by |x|^(N+1)·φ^(N+1)/√5,
which is why convergence is fast for x < 0.5 and slow near the singularity.
