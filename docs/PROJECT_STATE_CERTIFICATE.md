# Project State Certificate

> **Auditable summary of all branch protections, CI/CD workflows, and reproducibility
> guarantees active on the `main` branch of `wizardaax/recursive-field-math-pro`.**

---

## 1. Branch Protection Rules (`main`)

Applied via `.github/workflows/branch-protection.yml` (run with `ADMIN_TOKEN` PAT).

| Setting | Value |
|---|---|
| Require pull request before merging | ✅ |
| Required approving reviews | 1 |
| Require review from Code Owners | ✅ |
| Dismiss stale reviews on new commits | ✅ |
| Require branches to be up to date before merging | ✅ (`strict: true`) |
| Restrict force pushes | ✅ (`allow_force_pushes: false`) |
| Allow branch deletion | ❌ (`allow_deletions: false`) |
| Enforce rules on administrators | ✅ (`enforce_admins: true`) |
| Repository auto-merge | ✅ |

### Required status checks

All checks below must pass before a PR can merge:

| Check context (GitHub UI name) | Workflow file | Job |
|---|---|---|
| `CI Quality Gate / CI Gate` | `ci-quality-gate.yml` | `ci-gate` (stable fan-in; depends on matrix + repro jobs) |
| `PR Reproducibility Check / repro-check` | `pr-repro-check.yml` | `repro-check` |
| `Security (aeon-standards) / Security Scan (shared)` | `aeon-security.yml` | `security` (delegates to `wizardaax/aeon-standards` @v1) |

> **Note:** `ci-gate` is a non-matrix fan-in job whose name never changes
> regardless of OS/Python version matrix evolution.  This prevents required-check
> names from drifting when the matrix is updated.

---

## 2. CODEOWNERS

File: `.github/CODEOWNERS`

All files default to `@wizardaax`. Additional explicit owners are set for:

- `.github/workflows/*` — all CI/CD workflows
- `.github/CODEOWNERS`, `.github/labeler.yml`, `.github/dependabot.yml`,
  `.github/pull_request_template.md`
- `docs/QUALITY_GATES.md`, `CHANGELOG.md`, `RELEASE_NOTES.md`, `CITATION.cff`,
  `pyproject.toml`
- Reproducibility assets: `scripts/generate_figures.py`, `scripts/validate_stats.py`,
  `scripts/figure_manifest.py`, `paper/data/ablation_metrics.csv`,
  `paper/figures/manifest.sha256`, `paper/rff_phi_mod_verification.tex`,
  `docs/rff_phi_mod_verification.md`

---

## 3. CI/CD Workflows

| Workflow file | Trigger | Purpose |
|---|---|---|
| `aeon-python-ci.yml` | PR, push to `main`/`master`, `workflow_dispatch` | Shared Python CI (lint + type-check + test) delegated to `wizardaax/aeon-standards` @v1; plus repo-specific reproducibility figures |
| `aeon-security.yml` | PR, push to `main`/`master`, schedule, `workflow_dispatch` | Shared security scanning (pip-audit, npm audit, dep review) delegated to `wizardaax/aeon-standards` @v1 |
| `ci-quality-gate.yml` | PR to `main`, push to `main`, `workflow_dispatch` | Lint + type-check + test (matrix: ubuntu/windows × py3.10/3.11/3.12) + reproducibility figures & manifest |
| `pr-repro-check.yml` | PR to `main` (path-filtered) | Regenerate figures and diff against committed manifest |
| `ci.yml` | Push to `main`/`master`, PR, `workflow_dispatch` | Full Python/JS/shell lint and test matrix |
| `ci-python.yml` | — | Python-specific CI |
| `ci-node.yml` | — | Node.js-specific CI |
| `coverage.yml` | — | Coverage reporting |
| `branch-protection.yml` | `workflow_dispatch`; push to `main` (on self-change) | Applies all branch protection rules via GitHub API (requires `ADMIN_TOKEN` secret); auto-triggered when this file changes on `main` |
| `release.yml` / `publish.yml` | Tag push (`v*`) | Build, release, and publish |
| `publish-docker.yml` | — | Docker image publish |
| `publish-pypi.yml` | — | PyPI publish |
| `deploy-pages.yml` / `docs.yml` / `pages.yml` | — | Documentation / GitHub Pages |
| `codeql.yml` | — | CodeQL security scanning |
| `security.yml` | — | Dependency security scanning |
| `pre-commit.yml` | — | Pre-commit hook checks |
| `shellcheck.yml` | — | Shell script linting |
| `stale.yml` | — | Stale issue/PR management |
| `auto-label.yml` | — | Automatic PR labelling |
| `automerge-dependencies.yml` | — | Auto-merge Dependabot PRs |
| `release-drafter.yml` | — | Draft release notes |
| `tag-release.yml` | — | Tag-based release automation |
| `evolve.yml` | — | Repository evolution automation (includes infinite-loop guard) |
| `research-paper.yml` | — | Research paper generation |

---

## 4. Reproducibility Guarantees

| Guarantee | Mechanism |
|---|---|
| Figures are deterministic | `scripts/generate_figures.py` is seeded and deterministic |
| Figures are verified on every relevant PR | `PR Reproducibility Check / repro-check` regenerates figures and diffs against `paper/figures/manifest.sha256` |
| Manifest is committed alongside figures | `scripts/figure_manifest.py write` generates SHA-256 checksums; `verify` confirms them |
| Stats are validated before figure generation | `scripts/validate_stats.py` runs as a prerequisite step in the CI Quality Gate |
| Reproducibility assets are owner-gated | `@wizardaax` must review any change to `generate_figures.py`, `validate_stats.py`, `figure_manifest.py`, data CSVs, TeX sources, and the manifest file |

---

## 5. Policy-as-Code Workflow

The `.github/workflows/branch-protection.yml` workflow encodes branch protection as code:

```text
Trigger : workflow_dispatch (manual, one-time or re-applied as needed)
Secret  : ADMIN_TOKEN  — PAT with "repo" scope (classic) or
                         "administration: write" (fine-grained)
API     : github.rest.repos.updateBranchProtection (octokit/rest)
          github.rest.repos.update (auto-merge flag)
```

Re-running the workflow is idempotent — it is safe to run again after any settings
drift is detected.

### Post-run sanity checks

After running the workflow, verify:

- [ ] Direct push to `main` is blocked (except via approved PR)
- [ ] PRs require 1 approval + CODEOWNERS review
- [ ] Required status checks are enforced (see Section 1): `CI Quality Gate / CI Gate`, `PR Reproducibility Check / repro-check`, `Security (aeon-standards) / Security Scan (shared)`
- [ ] Force push to `main` is disabled
- [ ] Branch deletion for `main` is disabled
- [ ] Repository auto-merge is enabled

---

## 6. Emergency Bypass Policy

Only a repository administrator may bypass branch protection. Any bypass must:

1. Open an issue documenting the reason and scope.
2. Include a rollback plan.
3. Be followed by a corrective PR within 24 hours.

---

*Generated for `wizardaax/recursive-field-math-pro` — keep this file updated whenever
branch protection rules, required checks, or CODEOWNERS are modified.*
