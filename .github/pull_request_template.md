## Summary
<!-- What changed and why? -->

## Change type
- [ ] feat
- [ ] fix
- [ ] docs
- [ ] ci
- [ ] refactor
- [ ] test
- [ ] chore

## Quality checks
- [ ] `ruff check .`
- [ ] `black --check .`
- [ ] `flake8 .`
- [ ] `mypy scripts --ignore-missing-imports`
- [ ] `pytest -q`

## Reproducibility checks (if research/figure paths touched)
- [ ] `python scripts/validate_stats.py`
- [ ] `python scripts/generate_figures.py --theme light --format png --outdir paper/figures`
- [ ] `python scripts/figure_manifest.py write --dir paper/figures --out paper/figures/manifest.sha256`
- [ ] `python scripts/figure_manifest.py verify --dir paper/figures --manifest paper/figures/manifest.sha256`

## Security checklist
- [ ] No hardcoded secrets/API keys
- [ ] No weak crypto changes introduced
- [ ] Dependency changes reviewed

## Notes for reviewers
<!-- Risk areas, migration notes, rollout concerns -->
