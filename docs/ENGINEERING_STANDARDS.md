# Engineering Standards (wizardaax repos)

## Required for merge to main
- Pull request + at least 1 approval
- Required status checks pass
- No force-push to `main`
- No direct commits to `main` (except admin emergency policy)

## CI baseline
- Lint + format + tests on every PR
- Dependency update automation (Dependabot)
- Stale issue/PR hygiene automation

## Release baseline
- Update CHANGELOG/RELEASE_NOTES for release-impacting changes
- Tag with semantic version (e.g., `v0.4.3-*`)
- Verify docs/pages links after release

## Research/repro policy (for research repos)
For repos with deterministic artifacts:
- Regenerate artifacts in CI
- Maintain hash manifest
- Block merge on manifest drift
