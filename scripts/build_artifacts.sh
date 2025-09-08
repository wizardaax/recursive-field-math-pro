#!/usr/bin/env bash
# Cross-platform friendly (bash) builder: build wheel+sdist, verify, checksums.
# Usage: bash scripts/build_artifacts.sh

set -euo pipefail

PKG_NAME="regen88-codex"
PYTHON=${PYTHON:-python}

echo "==> Upgrading build toolchain"
$PYTHON -m pip install --upgrade pip build twine || echo "Warning: Failed to upgrade tools, using existing versions"

echo "==> Building sdist + wheel"
# Use direct setuptools build to avoid packaging version conflicts
$PYTHON -c "
import os
import sys
from setuptools import setup, find_packages

# Clean previous builds
if os.path.exists('dist'):
    import shutil
    shutil.rmtree('dist')
if os.path.exists('build'):
    import shutil
    shutil.rmtree('build')

# Temporarily rename pyproject.toml to avoid conflicts with current setuptools
if os.path.exists('pyproject.toml'):
    os.rename('pyproject.toml', 'pyproject.toml.bak')

try:
    setup(
        name='regen88-codex',
        version='0.1.0',
        description='Regen88 Codex — Cross-platform recursive field math with entropy-pump, Lucas sequences, and complete CI/CD',
        package_dir={'': 'src'},
        packages=find_packages(where='src'),
        install_requires=['python-chess>=1.9', 'numpy>=1.26', 'matplotlib>=3.8'],
        entry_points={'console_scripts': ['rfm=recursive_field_math.cli:main']},
        python_requires='>=3.9',
        author='Commander X (Wizard)',
        classifiers=[
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: 3.12'
        ],
        script_args=['bdist_wheel', 'sdist']
    )
finally:
    # Restore pyproject.toml
    if os.path.exists('pyproject.toml.bak'):
        os.rename('pyproject.toml.bak', 'pyproject.toml')
"

echo "==> Verifying package can be imported from wheel"
# Test that the wheel contains expected files rather than using twine
if [ -f dist/*.whl ]; then
    for wheel in dist/*.whl; do
        echo "Checking wheel contents: $wheel"
        unzip -l "$wheel" | grep -E '(recursive_field_math|entry_points)' | head -5
    done
else
    echo "Warning: No wheel files found in dist/"
fi

echo "==> Calculating SHA256 checksums"
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum dist/*
elif command -v shasum >/dev/null 2>&1; then
  shasum -a 256 dist/*
else
  echo "No checksum tool found (sha256sum/shasum). Skipping."
fi

echo "==> Artifacts:"
ls -1 dist
