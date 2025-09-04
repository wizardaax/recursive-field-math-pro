#!/usr/bin/env bash
# Tag and push: create git tag and push to trigger release workflow
# Usage: bash scripts/tag_and_push.sh v0.1.0 "Release description"

set -euo pipefail

if [ $# -ne 2 ]; then
    echo "Usage: bash scripts/tag_and_push.sh <tag> <description>"
    echo "Example: bash scripts/tag_and_push.sh v0.1.0 'Regen88 Codex v0.1.0'"
    exit 1
fi

TAG="$1"
DESCRIPTION="$2"

echo "==> Creating and pushing tag: $TAG"

# Verify we're on main/master branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    echo "Warning: You're on branch '$CURRENT_BRANCH', not main/master"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "Error: You have uncommitted changes. Please commit them first."
    exit 1
fi

# Create annotated tag
echo "==> Creating annotated tag"
git tag -a "$TAG" -m "$DESCRIPTION"

# Push tag
echo "==> Pushing tag to origin"
git push origin "$TAG"

echo "==> Tag $TAG pushed successfully!"
echo "This will trigger the release workflow in GitHub Actions."
echo "Check: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\).*/\1/' | sed 's/\.git$//')/actions"