[![CI](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/ci.yml/badge.svg)](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/ci.yml)
[![Coverage](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/coverage.yml/badge.svg)](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/coverage.yml)
[![Pre-commit](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/pre-commit.yml)
[![Docs](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/docs.yml/badge.svg)](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/docs.yml)
[![Release](https://img.shields.io/github/v/release/wizardaax/recursive-field-math-pro?logo=github)](https://github.com/wizardaax/recursive-field-math-pro/releases)
[![License](https://img.shields.io/github/license/wizardaax/recursive-field-math-pro)](LICENSE)

---

# Xova Intelligence — Projex X1 (Recursive Field Math)

A research-grade library and CLI for recursive-field mathematics (Lucas 4–7–11), golden-ratio refraction, entropy-pump variance analysis, and agent-ready workflows. Includes a CLI (rfm), tests, CI/CD, and user-facing docs.

Table of contents
- TL;DR
- Quickstart
- Status & docs
- Usage examples
- Math reference
- Contributing

---

## TL;DR

A computational toolbox for Lucas/Fibonacci sequences, field geometry, and entropy-pump variance reduction (chess PGN analysis). Example: install, run a quick lucas sequence and run tests.

## Quickstart

Install and try the CLI:

```bash
pip install regen88-codex
rfm --help
# Quick examples
rfm lucas 0 10
rfm egypt
python -m pytest -q
```

Developer bootstrap:

```bash
bash scripts/dev_bootstrap.sh && bash scripts/dev_check.sh
```

---

## Status & docs

- Docs site (GitHub Pages): https://wizardaax.github.io/recursive-field-math-pro/
- CI: https://github.com/wizardaax/recursive-field-math-pro/actions
- Releases: https://github.com/wizardaax/recursive-field-math-pro/releases

Docs preview deployments are created for PRs via the docs-preview workflow.

---

## Usage highlights

- Core modules: src/recursive_field_math/ (fibonacci, lucas, field, ratios, continued_fraction, egyptian_fraction)
- CLI: `rfm` (see `src/recursive_field_math/cli.py`)
- Entropy-pump harness and PGN analysis: scripts/codex_entropy_pump.py and scripts/run_entropy_pump_harness

Run the entropy-pump harness (example):

```bash
python -m scripts.run_entropy_pump_harness
# artifacts: out/*_{curve,clamp}.png, *_summary.json
```

For full mathematical derivations and reference formulas, see docs/MATHEMATICS.md (moved from README for readability).

---

## Contributing

See RELEASE_NOTES/ and the docs/ directory for contribution and release guidance. Quick dev commands:

```bash
bash scripts/dev_bootstrap.sh
bash scripts/dev_check.sh
```

Please open issues or PRs for feature requests and bug reports.

---

## License

This project is licensed under the terms in LICENSE.