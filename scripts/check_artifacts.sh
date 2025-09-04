#!/usr/bin/env bash
# Check build artifacts: verify distributions are valid and contain expected files
# Usage: bash scripts/check_artifacts.sh

set -euo pipefail

PKG_NAME="regen88-codex"
PYTHON=${PYTHON:-python}

echo "==> Checking build artifacts"

if [ ! -d "dist" ]; then
    echo "Error: dist/ directory not found. Run 'bash scripts/build_artifacts.sh' first."
    exit 1
fi

# Count expected files
WHEELS=$(ls dist/*.whl 2>/dev/null | wc -l)
SDISTS=$(ls dist/*.tar.gz 2>/dev/null | wc -l)

echo "Found $WHEELS wheel(s) and $SDISTS source distribution(s)"

if [ "$WHEELS" -eq 0 ] || [ "$SDISTS" -eq 0 ]; then
    echo "Error: Expected at least 1 wheel and 1 sdist"
    exit 1
fi

# Verify with twine
echo "==> Verifying distributions with twine"
$PYTHON -m twine check dist/*

# Check wheel contents
echo "==> Checking wheel contents"
for wheel in dist/*.whl; do
    echo "Checking $wheel:"
    unzip -l "$wheel" | grep -E '\.(py|toml|txt|md)$' | head -10
done

# Check sdist contents
echo "==> Checking sdist contents"
for sdist in dist/*.tar.gz; do
    echo "Checking $sdist:"
    tar -tzf "$sdist" | grep -E '\.(py|toml|txt|md)$' | head -10
done

# Verify package can be installed and imported
echo "==> Testing package installation in temporary environment"
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

# Create virtual environment
$PYTHON -m venv "$TMP_DIR/venv"
source "$TMP_DIR/venv/bin/activate"

# Install from wheel
WHEEL=$(ls dist/*.whl | head -1)
pip install "$WHEEL"

# Test import
python -c "import recursive_field_math; print('✓ Package imports correctly from wheel')"

# Test CLI
python -c "
import subprocess
result = subprocess.run(['rfm', '--help'], capture_output=True, text=True)
if result.returncode == 0:
    print('✓ CLI works from installed package')
else:
    print('✗ CLI failed from installed package')
    exit(1)
"

deactivate

echo "==> All artifact checks passed! ✓"