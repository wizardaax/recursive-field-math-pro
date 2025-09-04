# Contributing to Regen88 Codex

Thanks for your interest!

## Quick start
```bash
python -m pip install -e ".[dev]"
pre-commit install
pytest -q
```

### Style & checks
- Format with **black** (line length 100)
- Imports sorted by **isort** (profile black)
- Lint via **flake8** (+ bugbear)
- Types via **mypy** (target: `regen88_codex/`)
- Run:
  ```bash
  bash scripts/dev_check.sh
  ```

### Branch & PR
- Branch from `main`
- Conventional commits are appreciated
- Include tests for new features/fixes

---

## Maintainer Workflow: CI/Release/Tooling Setup

### 1) Create feature branch, commit, push, and open PR
```bash
git checkout -b regen88-ci-setup
git add -A
git commit -m "Add CI, release, pre-commit, and tooling for Regen88 Codex v0.1.0"
git push -u origin regen88-ci-setup
gh pr create --fill --title "Regen88 Codex v0.1.0 — CI/Release/Tooling" --body "Adds workflows, scripts, docs."
```

### 2) (Optional) Bootstrap dev environment and run checks locally
```bash
bash scripts/dev_bootstrap.sh
bash scripts/dev_check.sh
```

### 3) Build artifacts (wheel + sdist) and verify
```bash
bash scripts/build_artifacts.sh
bash scripts/check_artifacts.sh
```

### 4) Tag + push tag
```bash
bash scripts/tag_and_push.sh v0.1.0 "Regen88 Codex v0.1.0"
```

### 5) Create/Update GitHub Release and upload artifacts (requires gh auth login)
```bash
bash scripts/gh_release.sh v0.1.0 "Regen88 Codex v0.1.0"
```

#### Windows (PowerShell) equivalents
```powershell
git checkout -b regen88-ci-setup
git add -A
git commit -m "Add CI, release, pre-commit, and tooling for Regen88 Codex v0.1.0"
git push -u origin regen88-ci-setup
gh pr create --fill --title "Regen88 Codex v0.1.0 — CI/Release/Tooling" --body "Adds workflows, scripts, docs."

pwsh -f scripts/build_artifacts.ps1
pwsh -f scripts/release_all.ps1 v0.1.0 "Regen88 Codex v0.1.0"
```

#### (Optional) PyPI publish via workflow
Set a repo secret so release events auto-publish to PyPI:
```bash
gh secret set PYPI_API_TOKEN --body "<pypi-token-value>"
```