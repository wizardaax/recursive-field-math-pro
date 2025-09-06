#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-v0.2.0a1}"            # pass v0.2.0a1 or v0.2.0 etc.
BRANCH="${2:-v0.2.0a1-full-release}" # or main if you've merged
TAG="${VERSION}"

echo "==> Verifying branch/commit"
git fetch --all --prune
git switch "$BRANCH"
git log -1 --oneline

echo "==> Quick sanity: pyproject deps should include numpy"
grep -n 'dependencies = \["numpy>=' pyproject.toml >/dev/null

echo "==> Tagging $TAG"
git tag -a "$TAG" -m "regen88-codex $VERSION"
git push origin "$TAG"

echo "==> Creating GitHub release (requires gh CLI & repo permissions)"
if ! command -v gh >/dev/null; then
  echo "gh CLI not found; skipping GitHub release creation."; exit 0
fi

NOTES_FILE="CHANGELOG.md"
if [ -f "$NOTES_FILE" ]; then
  gh release create "$TAG" --target "$BRANCH" \
    --title "regen88-codex $VERSION" \
    --notes-file "$NOTES_FILE"
else
  gh release create "$TAG" --target "$BRANCH" \
    --title "regen88-codex $VERSION" \
    --notes "Release $VERSION"
fi

echo "==> Done. CI should build & publish to PyPI via Trusted Publisher."

# Usage:
# chmod +x tools/release.sh
# tools/release.sh v0.2.0a1 v0.2.0a1-full-release
# # later (stable):
# # tools/release.sh v0.2.0 main
