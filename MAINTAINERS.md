# MAINTAINERS — Regen88 Codex

## One-shot local release (Linux/macOS)
```bash
bash scripts/release_all.sh v0.1.0 "Regen88 Codex v0.1.0"
```

## One-shot local release (Windows PowerShell)
```powershell
pwsh -f scripts/release_all.ps1 v0.1.0 "Regen88 Codex v0.1.0"
```

## Manual steps (advanced)
1. Dev checks:
   ```bash
   bash scripts/dev_check.sh
   ```
2. Build & verify:
   ```bash
   bash scripts/build_artifacts.sh
   bash scripts/check_artifacts.sh
   ```
3. Tag & push:
   ```bash
   bash scripts/tag_and_push.sh v0.1.0 "Regen88 Codex v0.1.0"
   ```
4. GitHub Release:
   ```bash
   bash scripts/gh_release.sh v0.1.0 "Regen88 Codex v0.1.0"
   ```

## Automation
- **CI**: `.github/workflows/ci.yml`
- **Release on tag**: `.github/workflows/release.yml`
- **PyPI on published release**: `.github/workflows/publish-pypi.yml` (needs `PYPI_API_TOKEN` secret)