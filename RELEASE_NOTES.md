## v0.4.1-pages-integration

This release finalizes the RFF φ-modulation reproducibility and publishing pipeline.

### Included
- **PR #73** — Reproducibility bundle
  - figure generator CLI (`scripts/generate_figures.py`)
  - stats validator (`scripts/validate_stats.py`)
  - ablation dataset, LaTeX paper source, docs summary
  - CI workflow + Makefile/README updates

- **PR #74** — Initial GitHub Pages artifact publishing automation

- **PR #75** — Final Pages architecture fix
  - aligned publishing with active Pages source (`main/docs`)
  - versioned runs at `docs/research/runs/<run_number>/`
  - latest snapshot at `docs/research/latest/`
  - removed branch/source mismatch and retired redundant publisher flow

### Live artifact URLs
- Latest: https://wizardaax.github.io/recursive-field-math-pro/research/latest/
- All runs: https://wizardaax.github.io/recursive-field-math-pro/research/runs/
