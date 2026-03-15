# Engineering Standards (wizardaax repos)

> **Single source of truth:** All shared standards, reusable workflows, and
> policy templates live in the central control repository:
> [`wizardaax/aeon-standards`](https://github.com/wizardaax/aeon-standards)
>
> **Pinned ref:** `wizardaax/aeon-standards@main`
> *(update this line to a specific commit SHA once the control repo is tagged,
> e.g. `wizardaax/aeon-standards@a1b2c3d`)*
>
> This file is a **local summary**. The authoritative version is
> [`wizardaax/aeon-standards/docs/ENGINEERING_STANDARDS.md`](https://github.com/wizardaax/aeon-standards/blob/main/docs/ENGINEERING_STANDARDS.md).

---

## Required for merge to main
- Pull request + at least 1 approval
- Required status checks pass
- No force-push to `main`
- No direct commits to `main` (except admin emergency policy)

## CI baseline
- Lint + format + tests on every PR
- Dependency update automation (Dependabot)
- Stale issue/PR hygiene automation
- Shared reusable CI via `wizardaax/aeon-standards/.github/workflows/python-ci.yml`
- Shared security scanning via `wizardaax/aeon-standards/.github/workflows/security.yml`

## Release baseline
- Update CHANGELOG/RELEASE_NOTES for release-impacting changes
- Tag with semantic version (e.g., `v0.4.3-*`)
- Verify docs/pages links after release
- Consult [COMPATIBILITY_MATRIX.md](./COMPATIBILITY_MATRIX.md) before releasing
  breaking changes

## Research/repro policy (for research repos)
For repos with deterministic artifacts:
- Regenerate artifacts in CI
- Maintain hash manifest
- Block merge on manifest drift

## Cross-repo health
See [HEALTH_DASHBOARD.md](./HEALTH_DASHBOARD.md) for live CI, coverage, release,
and security status across all wizardaax repos.
