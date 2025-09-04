#!/usr/bin/env bash
# Development bootstrap: set up dev environment with all required tools
# Usage: bash scripts/dev_bootstrap.sh

set -euo pipefail

echo "==> Bootstrapping development environment"

# Update package management
echo "==> Upgrading pip and build tools"
python -m pip install --upgrade pip setuptools wheel || echo "Warning: Failed to upgrade tools, using existing versions"

# Install package in editable mode
echo "==> Installing package in editable mode"
python -m pip install -e . || echo "Warning: Failed to install package in editable mode"

# Install development dependencies
echo "==> Installing development dependencies"
python -m pip install pytest ruff pre-commit build twine || echo "Warning: Some development dependencies may not be available"

# Install pre-commit hooks
echo "==> Setting up pre-commit hooks"
if [ -f .pre-commit-config.yaml ]; then
    pre-commit install
    echo "Pre-commit hooks installed"
else
    echo "Warning: .pre-commit-config.yaml not found, skipping pre-commit setup"
fi

echo "==> Development environment ready!"
echo ""
echo "Available commands:"
echo "  bash scripts/dev_check.sh         - Run linting and tests"
echo "  bash scripts/build_artifacts.sh   - Build distribution packages"
echo "  bash scripts/check_artifacts.sh   - Verify build artifacts"
echo "  bash scripts/tag_and_push.sh      - Tag and push release"
echo "  bash scripts/release_all.sh       - Full release workflow"