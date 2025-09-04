#!/usr/bin/env bash
# Cross-platform friendly (bash) builder: build wheel+sdist, verify, checksums.
# Usage: bash scripts/build_artifacts.sh

set -euo pipefail

PKG_NAME="regen88_codex"
: "
# {PYTHON:=python}"

echo "==> Upgrading build toolchain"
$PYTHON -m pip install --upgrade pip build twine >/dev/null

echo "==> Building sdist + wheel"
$PYTHON -m build

echo "==> Verifying with twine"
$PYTHON -m twine check dist/*

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
