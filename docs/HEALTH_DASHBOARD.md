# Cross-Repo Health Dashboard

Live status for all `wizardaax` repositories governed by
[`aeon-standards`](https://github.com/wizardaax/aeon-standards).

> **Refresh cadence:** CI badges auto-update on each workflow run.
> Coverage numbers and release versions are pulled from GitHub Shields.
> Security alert counts must be updated manually or via automation.

---

## recursive-field-math-pro

| Metric | Status |
|---|---|
| CI | [![CI](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/ci.yml/badge.svg)](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/ci.yml) |
| Quality Gate | [![CI Quality Gate](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/ci-quality-gate.yml/badge.svg)](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/ci-quality-gate.yml) |
| Security | [![Security](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/security.yml/badge.svg)](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/security.yml) |
| Pre-commit | [![Pre-commit](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/pre-commit.yml) |
| Coverage | [![Coverage](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/coverage.yml/badge.svg)](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/coverage.yml) |
| Last Release | [![Release](https://img.shields.io/github/v/release/wizardaax/recursive-field-math-pro?logo=github)](https://github.com/wizardaax/recursive-field-math-pro/releases) |
| Branch protection | ✅ enforced (see [branch-protection.yml](../.github/workflows/branch-protection.yml)) |
| aeon-standards wired | ✅ `@v1` ([aeon-python-ci.yml](../.github/workflows/aeon-python-ci.yml), [aeon-security.yml](../.github/workflows/aeon-security.yml)) |

---

## aeon-standards (control repo)

| Metric | Status |
|---|---|
| Repo | [![aeon-standards](https://img.shields.io/badge/repo-aeon--standards-6A0DAD?logo=github)](https://github.com/wizardaax/aeon-standards) |
| Status | ✅ bootstrapped — tagged `v1` |
| CI | [![CI](https://github.com/wizardaax/aeon-standards/actions/workflows/python-ci.yml/badge.svg)](https://github.com/wizardaax/aeon-standards/actions/workflows/python-ci.yml) |
| Security | [![Security](https://github.com/wizardaax/aeon-standards/actions/workflows/security.yml/badge.svg)](https://github.com/wizardaax/aeon-standards/actions/workflows/security.yml) |

---

## Policy checklist (per repo)

| Repo | Branch protection | Dependabot | Stale bot | Reusable CI wired | Security scanning |
|---|---|---|---|---|---|
| `recursive-field-math-pro` | ✅ | ✅ | ✅ | ✅ `@v1` | ✅ |
| `aeon-standards` | ✅ | ✅ | ✅ | N/A (source) | ✅ |

---

## How to update this dashboard

1. **CI badges** — update the workflow file name in the shield URL if a workflow is renamed.
2. **Coverage numbers** — the `coverage.yml` workflow uploads an HTML report artifact.
   Once Codecov is wired, replace the workflow badge with a Codecov badge.
3. **Branch protection state** — run the
   [Enforce Branch Protection](../../../actions/workflows/branch-protection.yml)
   workflow manually after any policy change, then update the checkmark in the table.
4. **aeon-standards bootstrap** — the control repo is live and tagged `v1`; all
   ⏳ entries have been flipped to ✅.
