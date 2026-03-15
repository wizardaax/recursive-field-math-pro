# Quality Gates and Reproducibility Policy

## Purpose

Ensure mathematically advanced and research-critical outputs remain deterministic, validated, and release-safe.

## Required checks on PR to main

1. CI Quality Gate
2. PR Reproducibility Check

## Deterministic artifact policy

- Generated figure artifacts under `paper/figures/` must match `manifest.sha256`.
- Any intentional figure update must regenerate both figures and manifest in the same PR.

## Failure policy

- Any lint/type/test failure blocks merge.
- Any manifest mismatch blocks merge.
- Any missing reproducibility input files blocks merge.

## Recommended branch protection (repo settings)

- Require pull request before merging
- Require status checks to pass before merging:
  - `CI Quality Gate / Lint/Type/Test (ubuntu-latest / py3.11)` (and matrix peers)
  - `CI Quality Gate / Reproducibility Figures + Manifest`
  - `PR Reproducibility Check / repro-check`
- Require branches to be up to date before merging
- Restrict force pushes to `main`
