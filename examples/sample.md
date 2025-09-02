# Quick Demo: Lucas Numbers and Golden Ratio

This example demonstrates the core functionality of the recursive field math library.

## Basic Usage

### 1. Generate Lucas Numbers
```bash
rfm lucas 0 10
```
Expected output: Lucas sequence L₀ through L₁₀

### 2. Analyze Ratios
```bash
rfm ratio 5
```
Shows L₆/L₅ ratio and convergence to golden ratio φ

### 3. Egyptian Fraction Check
```bash
rfm egypt
```
Verifies the decomposition: 1/4 + 1/7 + 1/11 = 149/308

## Mathematical Background

The Lucas numbers follow the recurrence relation:
- L₀ = 2, L₁ = 1
- Lₙ = Lₙ₋₁ + Lₙ₋₂ for n ≥ 2

Key properties:
- **Golden Ratio**: lim(n→∞) Lₙ₊₁/Lₙ = φ = (1+√5)/2
- **Signature Triple**: L₃=4, L₄=7, L₅=11 (forms the basis for entropy pump analysis)
- **Egyptian Fraction**: Special relationship between signature triple fractions

## Next Steps

1. Explore field geometry: `rfm field 1 10`
2. Run entropy pump analysis: `python -m scripts.run_entropy_pump_harness`
3. Analyze chess games with variance reduction techniques
4. Integrate with your own mathematical research workflows

## Agent Integration

For programmatic use:
```python
from recursive_field_math import lucas, ratios
result = lucas.generate_sequence(0, 10)
ratio_analysis = ratios.analyze_convergence(5)
```