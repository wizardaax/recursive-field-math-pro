# Codex Entropy-Pump (ϕ–Refraction)

**Goal:** tame midgame chaos by refracting eval-deltas through a golden-ratio index  
θ′ = arcsin(sin θ / ϕ), with θ = rank-phase of eval changes.

**Key metrics**
- Variance reduction in deltas (%)
- Compression coefficient `c = 1 − Var(θ′)/Var(θ)`
- MAE improvement (%; optional baseline)
- φ-clamp at ±arcsin(1/ϕ) ≈ ±0.666 rad (~±38.2°)

**Run locally**
```bash
python -m scripts.run_entropy_pump_harness
```

Artifacts land in `out/`: curves, clamp histograms, JSON/TSV summary.

---

### Requirements (if not already present)
Add lines to your `requirements.txt` (or they're already in your workflow install step):

```
python-chess>=1.9
numpy>=1.26
matplotlib>=3.8
```

---

## How to run it in your repo (fast)
1. **Paste the files** above into the matching paths.
2. **Commit** (web editor is fine):  
   `wire: add Codex entropy-pump harness (ϕ-clamp + metrics)`
3. **Trigger the agent:** open an issue "Entropy pump test" and comment:

```
/agent run
```
4. **See results:** Actions → latest run → artifact **codex-run** → open:
- `entropy_pump_summary_*.tsv/.json`
- `*_curve.png` (before/after eval)
- `*_clamp.png` (φ-clamp signature)

---

### What to look for
- Midgame window (moves 10–30) shows **~20–40% variance drop**.
- Clamp plot peaks near **±0.666 rad**.
- MAE improvement positive on most games (few %).

## Lucas Sweep Feature

The **Lucas sweep** compares different Lucas weight combinations to find optimal settings:

**Default combinations tested:**
- Baseline (no Lucas weights)
- (4,7,11) - Default Lucas sequence  
- (3,6,10) - Alternative comparison
- (2,5,8) - Smaller values
- (5,8,13) - Larger values

**New outputs:**
- `lucas_sweep_heatmap.png` - Comparative heatmap of variance reduction and compression
- `lucas_sweep_summary_*.json` - Detailed results for all combinations
- Individual plots for each combination: `*_lucas_X_Y_Z_curve.png` and `*_lucas_X_Y_Z_clamp.png`
- Enhanced TSV with `lucas_weights` column

**Usage:** The Lucas sweep runs automatically with the harness. Results show different combinations can achieve varying levels of variance reduction (from ~58% to ~92%) and compression performance.