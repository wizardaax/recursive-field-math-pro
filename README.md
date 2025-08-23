# Projex X1 — Original Formula (Lucas 4–7–11)

> **Repo:** `wizardaax/recursive-field-math-pro`  
> **Focus:** Radial–angular recursive field + Lucas/Fibonacci backbone, with agent-ready CLI, tests, docs, data hooks, and CI.

## Geometric Field (Seed)
- Radial growth: \( r_n = 3\sqrt{n} \)  
- Angular phase: \( \theta_n = n\varphi \), where \( \varphi = \frac{1+\sqrt{5}}{2} \)  
- Base anchor: “Locked in root” at \( r=\sqrt{3} \)  
- Cycle cue: \( \pi \rightarrow 2\pi \rightarrow 3\pi \)

## Lucas Initialization
\((L_0,L_1,L_2,L_3,L_4,L_5) = (2,1,3,4,7,11), \quad L_{n+1} = L_n + L_{n-1}\)

## Backbone (Fibonacci/Lucas)
- \( F_n = \dfrac{\varphi^n - \psi^n}{\sqrt{5}},\quad L_n = \varphi^n + \psi^n,\quad \psi = 1-\varphi \)  
- Matrix form: \( L_n = \mathrm{tr}(Q^n),\quad Q=\begin{pmatrix}1&1\\1&0\end{pmatrix} \)  
- Fibonacci–Lucas link: \( L_n = F_{n-1} + F_{n+1} \)  
- Cassini (Lucas): \( L_n^2 - L_{n-1}L_{n+1} = 5(-1)^n \)  
- Pell-type norm: \( L_n^2 - 5F_n^2 = 4(-1)^n \)

## Signature Triple (4–7–11)
- \( L_3=4,\;L_4=7,\;L_5=11 \)  
- Egyptian fraction:  
  \( \frac{1}{4}+\frac{1}{7}+\frac{1}{11}=\frac{149}{308}=\frac{1}{2}-\frac{5}{308} \)  
- Products/sums: \( 4\cdot7\cdot11=308 \), \( 4\cdot7+4\cdot11+7\cdot11=149 \)  
- Frobenius (4,7): \( g(4,7)=4\cdot7-4-7=17 \)  
- Additive chain cue: \( 4+7=11 \)

## Ratio Law & Accuracy
\( \frac{L_{n+1}}{L_n} - \varphi = (-1)^{n+1}\frac{\sqrt{5}\,|\psi|^n}{L_n} \)  

Asymptotic law: \( \left|\frac{L_{n+1}}{L_n}-\varphi\right| \sim \frac{\sqrt{5}}{\varphi^{2n}} \)

Bounds:  
\( \frac{\sqrt{5}}{L_n(L_n+|\psi|^n)} < \Big|\tfrac{L_{n+1}}{L_n}-\varphi\Big| < \frac{\sqrt{5}}{L_n(L_n-|\psi|^n)} \)

## Continued Fraction / Semiconvergents
\( \frac{L_{n+1}}{L_n}=[1; \underbrace{1,\dots,1}_{n-2},3] \)  
Equivalently \( r_m=[1;1^m,3]=\frac{L_{m+3}}{L_{m+2}} \).

## Generating Functions
\( \sum_{n\ge0}F_n x^n=\frac{x}{1-x-x^2}, \quad \sum_{n\ge0}L_n x^n=\frac{2-x}{1-x-x^2} \)

---

## Quickstart

```bash
# [A] install (editable)
pip install -e .

# [B] run CLI examples
rfm field 1 10           # r, theta for n=1..10
rfm lucas 0 10           # L_n for n in [0,10]
rfm ratio 5              # L_{n+1}/L_n, error bounds
rfm egypt                # 1/4+1/7+1/11 decomposition check
rfm sig                  # signature triple summary

# [C] tests
pytest -q
```

## Agent Hooks
- Single command deploy: `scripts/deploy.sh` (edit `REMOTE=` to your GitHub SSH/HTTPS URL)
- CI: `.github/workflows/ci.yml` runs lint & tests on push
- `my_recursive_ai.py` provides keyword → function routing for agent mode

## Layout
```
recursive-field-math-pro/
├─ src/recursive_field_math/
│  ├─ __init__.py
│  ├─ constants.py
│  ├─ fibonacci.py
│  ├─ lucas.py
│  ├─ field.py
│  ├─ ratios.py
│  ├─ continued_fraction.py
│  ├─ generating_functions.py
│  ├─ egyptian_fraction.py
│  ├─ signatures.py
│  └─ cli.py
├─ my_recursive_ai.py
├─ tests/
│  └─ test_core.py
├─ data/
│  ├─ AEON-Gravyflyer.csv (placeholder)
│  └─ Enhanced_Zeta_Analysis.csv (placeholder)
├─ scripts/
│  └─ deploy.sh
├─ .github/workflows/ci.yml
├─ pyproject.toml
├─ LICENSE
└─ README.md
```
