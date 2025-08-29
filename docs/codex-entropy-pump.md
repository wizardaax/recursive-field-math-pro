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

If you want the **Lucas sweep** (e.g., compare (4,7,11) vs (3,6,10)), I'll add a small loop and a summary heatmap next.