# Maintainer Quickstart (Daily Use)

## Local preflight
```bash
make quality
```

## Open PR with confidence
- Follow PR template
- Ensure required checks pass
- Ensure reproducibility files updated when touching research paths

## Release flow
1. Update CHANGELOG and RELEASE_NOTES
2. Bump version metadata if needed
3. Create tag (`vX.Y.Z-*`)
4. Verify Pages:
   - /research/latest/
   - /research/runs/

## If CI fails
- Lint/type failures: fix immediately
- Manifest mismatch: regenerate figures + update `paper/figures/manifest.sha256`
- Platform-specific failures: reproduce on Windows matrix locally or isolate path/encoding assumptions
