#!/usr/bin/env bash
set -euo pipefail

# publish_pypi.sh — Manual local PyPI publish using Twine.
#
# Usage:
#   TWINE_PASSWORD=<your-pypi-token> bash scripts/publish_pypi.sh
#
# Prerequisites:
# - dist/ directory must exist with built packages (.whl and .tar.gz)
# - TWINE_PASSWORD environment variable must be set to a valid PyPI API token
#
# This script checks for requirements and publishes to PyPI using Twine.

echo "==> PyPI Manual Publish"

# Check for dist/ directory
if [ ! -d "dist" ]; then
    echo "❌ Error: dist/ directory not found"
    echo "   Run: bash scripts/build_artifacts.sh"
    exit 1
fi

# Check for built packages
if [ -z "$(ls -A dist/*.whl 2>/dev/null)" ] && [ -z "$(ls -A dist/*.tar.gz 2>/dev/null)" ]; then
    echo "❌ Error: No packages found in dist/"
    echo "   Run: bash scripts/build_artifacts.sh"
    exit 1
fi

# Check for TWINE_PASSWORD
if [ -z "${TWINE_PASSWORD:-}" ]; then
    echo "❌ Error: TWINE_PASSWORD environment variable not set"
    echo "   Set your PyPI API token:"
    echo "   export TWINE_PASSWORD='pypi-...'"
    exit 1
fi

# Set TWINE_USERNAME (always __token__ for PyPI API tokens)
export TWINE_USERNAME=__token__

echo "==> Packages to publish:"
ls -lh dist/

echo ""
read -p "Proceed with publishing to PyPI? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo "==> Publishing to PyPI with Twine"
python -m twine upload dist/* --skip-existing

echo ""
echo "✅ Published to PyPI successfully!"
echo ""
echo "Verify at: https://pypi.org/project/regen88-codex/"
echo ""
