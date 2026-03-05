#!/usr/bin/env bash
# Release all: complete release workflow with verification
# Usage: bash scripts/release_all.sh v0.1.0 "Release description"

set -euo pipefail

if [ $# -ne 2 ]; then
    echo "Usage: bash scripts/release_all.sh <tag> <description>"
    echo "Example: bash scripts/release_all.sh v0.1.0 'Regen88 Codex v0.1.0'"
    exit 1
fi

TAG="$1"
DESCRIPTION="$2"

echo "==> Starting complete release workflow for $TAG"

# Run development checks
echo "==> Step 1: Running development checks"
bash scripts/dev_check.sh

# Build artifacts
echo "==> Step 2: Building artifacts"
bash scripts/build_artifacts.sh

# Check artifacts
echo "==> Step 3: Checking artifacts"
bash scripts/check_artifacts.sh

# Confirm release
echo ""
echo "==> Release ready for $TAG"
echo "Description: $DESCRIPTION"
echo "Artifacts built and verified in dist/"
echo ""
read -p "Proceed with tagging and pushing? (y/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Release cancelled."
    exit 1
fi

# Tag and push
echo "==> Step 4: Tagging and pushing"
bash scripts/tag_and_push.sh "$TAG" "$DESCRIPTION"

echo ""
echo "==> Release workflow complete! ✓"
echo ""
echo "Next steps:"
echo "1. Monitor GitHub Actions for build completion"
echo "2. Check GitHub Releases page for the new release"
echo "3. If PyPI auto-publish is configured, verify package on PyPI"
echo ""
echo "GitHub Actions: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\).*/\1/' | sed 's/\.git$//')/actions"
echo "Releases: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\).*/\1/' | sed 's/\.git$//')/releases"