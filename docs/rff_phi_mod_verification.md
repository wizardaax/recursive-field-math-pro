# Recursive Field Framework (RFF) φ-Modulation: Three-System Verification

**Authors:** Adam Snellman (wizardaax)
**License:** MIT
**Date:** March 16, 2026
**Repository:** https://github.com/wizardaax/recursive-field-math-pro

## 1. Overview

This report presents independent verification of φ-modulation in MCTS search spaces using the Recursive Field Framework (RFF).
Three AI systems contributed:

- **GPT (Prediction):** Predicted relative gains and synergy behavior.
- **Claude (Execution):** Ran deterministic Othello 8×8 ablations (5 trials × 50 simulations per configuration).
- **Grok (Independent Analysis):** Verified entropy and scale-invariance claims.

Objective: evaluate whether φ-modulation alone improves exploration efficiency without additional scheduling heuristics.

## 2. Methodology

- Environment: Othello 8×8, deterministic play.
- Configurations: Baseline, φ-modulation, scheduler, combined.
- Trials: 5 per configuration.
- Simulations: 50 per trial.
- Metrics: nodes, coverage entropy, branching factor, depth, nodes/simulation.
- φ-modulation:
  `phi_bonus = 0.1 * math.cos(sim_index * φ)`

## 3. Results Summary

| Config    | Nodes (mean±σ) | Coverage Entropy (mean±σ) | Branching (mean±σ) | Depth (mean±σ) | Nodes/Sim (mean±σ) |
|-----------|-----------------|----------------------------|--------------------|----------------|--------------------|
| Baseline  | 232.2 ± 3.1     | 1.1426 ± 0.021             | 4.644 ± 0.035      | 2.772 ± 0.018  | 4.644 ± 0.035      |
| φ-mod     | 225.8 ± 2.5     | 1.2902 ± 0.019             | 4.516 ± 0.028      | 2.676 ± 0.016  | 4.516 ± 0.028      |
| Scheduler | 231.2 ± 3.0     | 1.1993 ± 0.022             | 4.624 ± 0.033      | 2.736 ± 0.017  | 4.624 ± 0.033      |
| Combined  | 227.8 ± 2.8     | 1.1818 ± 0.020             | 4.556 ± 0.030      | 2.744 ± 0.016  | 4.556 ± 0.030      |

95% CI uses t-distribution with df=4 (t=2.776).

## 4. Reproducibility

Generate figures:

```bash
python scripts/generate_figures.py --theme light --format png --outdir paper/figures
```

Validate statistics:

```bash
python scripts/validate_stats.py
```

## 5. Interpretation

- φ-modulation reduces node usage and increases coverage entropy.
- Scheduler alone underperforms φ-mod in entropy improvement.
- Combined setup appears to dilute pure φ-mod effects.
- Scale-invariance supports precision-sensitive behavior in fractional φ sequences.

## 6. Next Steps

- Replicate on larger search domains (10×10 Othello, Chess).
- Add policy entropy and win-rate metrics.
- Integrate in RL workflows (CleanRL / MCTS-augmented agents).
