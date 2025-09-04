#!/usr/bin/env bash
# Development check: run all linting, type checking, and tests
# Usage: bash scripts/dev_check.sh

set -euo pipefail

echo "==> Running development checks"

# Lint with ruff (warnings only for now)
echo "==> Linting with ruff"
python -m ruff check . || echo "⚠️  Linting issues found (not blocking)"

# Run tests with pytest
echo "==> Running tests with pytest"
python -m pytest -v

# Check if package can be imported
echo "==> Testing package import"
python -c "import recursive_field_math; print('✓ Package imports successfully')"

# Test CLI command
echo "==> Testing CLI command"
python -c "
import subprocess
result = subprocess.run(['rfm', '--help'], capture_output=True, text=True)
if result.returncode == 0:
    print('✓ CLI command works')
else:
    print('✗ CLI command failed')
    print(result.stderr)
    exit(1)
"

# Test scripts can be imported
echo "==> Testing script imports"
python -c "
try:
    from scripts.codex_entropy_pump import PHI
    from scripts.results_evaluator import evaluate_acceptance_rules
    print('✓ Script imports work')
except ImportError as e:
    print(f'✗ Script import failed: {e}')
    exit(1)
"

echo "==> All checks passed! ✓"