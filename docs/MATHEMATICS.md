# Mathematical Reference (moved from README)

This document contains the mathematical derivations and reference material moved from README.md for improved readability.

## Geometric Field (Seed)
- Radial growth: r_n = 3\sqrt{n}
- Angular phase: θ_n = nφ, where φ = (1+√5)/2
- Base anchor: “Locked in root” at r=√3
- Cycle cue: π → 2π → 3π

## Lucas Initialization
(L_0,L_1,L_2,L_3,L_4,L_5) = (2,1,3,4,7,11),  L_{n+1} = L_n + L_{n-1}

## Backbone (Fibonacci/Lucas)
- F_n = (φ^n - ψ^n)/√5,  L_n = φ^n + ψ^n,  ψ = 1-φ
- Matrix form: L_n = tr(Q^n), Q = [[1,1],[1,0]]
- Fibonacci–Lucas link: L_n = F_{n-1} + F_{n+1}
- Cassini (Lucas): L_n^2 - L_{n-1}L_{n+1} = 5(-1)^n
- Pell-type norm: L_n^2 - 5F_n^2 = 4(-1)^n

## Signature Triple (4–7–11)
- L_3=4, L_4=7, L_5=11
- Egyptian fraction:
  1/4 + 1/7 + 1/11 = 149/308 = 1/2 - 5/308
- Products/sums: 4*7*11 = 308, 4*7 + 4*11 + 7*11 = 149
- Frobenius (4,7): g(4,7) = 4*7 - 4 - 7 = 17
- Additive chain cue: 4 + 7 = 11

## Ratio Law & Accuracy
(L_{n+1}/L_n) - φ = (-1)^{n+1} (√5 |ψ|^n) / L_n

Asymptotic law: |L_{n+1}/L_n - φ| ~ √5 / φ^{2n}

Bounds:
√5 / (L_n(L_n + |ψ|^n)) < |L_{n+1}/L_n - φ| < √5 / (L_n(L_n - |ψ|^n))

## Continued Fraction / Semiconvergents
L_{n+1}/L_n = [1; 1, ..., 1, 3]  (n-2 ones)
Equivalently r_m = [1; 1^m, 3] = L_{m+3} / L_{m+2}

## Generating Functions
sum_{n>=0} F_n x^n = x / (1 - x - x^2)

sum_{n>=0} L_n x^n = (2 - x) / (1 - x - x^2)
