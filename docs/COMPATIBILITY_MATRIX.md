# Cross-Repo Compatibility Matrix

This document tracks which versions of `recursive-field-math-pro` are compatible
with other `wizardaax` repositories and their key dependencies.

> **Governed by:** [`wizardaax/aeon-standards`](https://github.com/wizardaax/aeon-standards) — see the
> [release coherence policy](https://github.com/wizardaax/aeon-standards/blob/main/docs/ENGINEERING_STANDARDS.md#release-baseline)
> for guidance on coordinated releases.

---

## Package: `regen88-codex` (repo: `recursive-field-math-pro`)

> `regen88-codex` is the **PyPI package name** published from this repository
> (`recursive-field-math-pro`).  Both names refer to the same codebase.

| `recursive-field-math-pro` version | PyPI: `regen88-codex` | Python | `glyph_phase_engine` | `aeon-standards` workflows | Notes |
|---|---|---|---|---|---|
| `v0.5.x` | `0.5.x` | `>=3.9, <3.14` | `>=0.1.0` (TBD) | `@main` / `@v1` (pending) | Current stable |
| `v0.4.x` | `0.4.x` | `>=3.9, <3.13` | N/A | N/A | Legacy |

---

## Dependency pins

```
# Core runtime (pyproject.toml)
python-chess  >=1.9
numpy         >=1.26
matplotlib    >=3.8
```

---

## aeon-standards workflow compatibility

| aeon-standards ref | Reusable workflow | Min caller version | Status |
|---|---|---|---|
| `@main` | `python-ci.yml` | GitHub Actions runner `ubuntu-latest` | ⏳ Pending bootstrap |
| `@main` | `security.yml` | GitHub Actions runner `ubuntu-latest` | ⏳ Pending bootstrap |
| `@v1` | `python-ci.yml` | GitHub Actions runner `ubuntu-latest` | ⏳ Pending tag |
| `@v1` | `security.yml` | GitHub Actions runner `ubuntu-latest` | ⏳ Pending tag |

> Once `wizardaax/aeon-standards` is bootstrapped and tagged `v1`, update the
> `uses:` lines in `.github/workflows/aeon-python-ci.yml` and
> `.github/workflows/aeon-security.yml` from `@main` to `@v1`.

---

## Update policy

- This file **must** be updated whenever a release changes a public API or
  raises/lowers a minimum dependency version.
- Incompatible changes (breaking API, major dep bumps) require a major version
  bump and a dedicated entry in [CHANGELOG.md](../CHANGELOG.md).
- For cross-repo coordinated releases, open an issue in
  [`wizardaax/aeon-standards`](https://github.com/wizardaax/aeon-standards/issues)
  referencing both repos.
