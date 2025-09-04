# Regen88 Codex v0.1.0

**First public release** of the Regen88 Codex — a small, well-tested, educational “Flame Correction Engine” designed to **detect/counter Null88-style collapse** and **stabilize recursion**.  
This version ships clean packaging, CI/CD, developer tooling, and a minimal, typed Python API.

---

## ✨ Highlights
- **Phi Drift Correction** — `phi_correct_drift()` realigns unstable phase series to the golden regime.
- **Pure Reseed (ZPE proxy)** — `clean_reseed()` purges a corrupted seed and derives a fresh 32-byte digest.
- **Harmonic Digest Balancing** — `harmonic_balance()` applies Lucas-based offsets (mod 256) across a digest series.
- **Fault Shard Isolation** — `shard_isolate()` filters “corrupt” steps and corrects the main path phases.
- **Typed, documented API** with simple, readable implementations suitable for learning and extension.
- **End-to-end automation**: CI, pre-commit, build/release scripts, and GitHub Releases workflow.

> ⚠️ **Educational notice**: This package is not a substitute for audited cryptography or production incident-response. It’s a teaching/experimentation toolkit.

---

## 📦 Install
```bash
# Editable dev install (includes tooling)
pip install -e ".[dev]"

# or normal install (runtime only)
pip install .
```

🧪 Quick Usage
```python
from regen88_codex import (
    phi_correct_drift,
    clean_reseed,
    harmonic_balance,
    shard_isolate,
)

# 1) Correct phases into [0, 2π) with golden stabilization
corr = phi_correct_drift([0.5, 7.0, -1.0])

# 2) Purge/reseed a corrupted blob
seed = clean_reseed(b"\xFF" * 64)  # -> 32 bytes

# 3) Rebalance digests with Lucas offsets
balanced = harmonic_balance([b"\x00"*8, b"\xFF"*8])

# 4) Isolate corrupt steps, keep corrected main path
main = shard_isolate([
    {"phase": 1.0},
    {"corrupt": True, "phase": 0.618},
    {"phase": 2.0},
])
```

✅ What’s Included

- **Source:** `regen88_codex/` (utils.py, flame_correct.py, reseed_pure.py, harmonic_balance.py, shard_isolate.py)
- **Tests:** `tests/test_regen88.py` (pytest; covers primary functions)
- **Packaging:** `pyproject.toml` (PEP 621), minimal `setup.py`
- **Docs:** `README.md`, `BUILD.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`
- **Tooling:**
  - Pre-commit hooks (`.pre-commit-config.yaml`)
  - Editor/format configs (`.editorconfig`, `.gitattributes`, `.vscode/settings.json`)
  - CI workflows: CI (lint/type/test), Pre-commit, Release (tag-triggered), optional Publish to PyPI
  - Release helpers: `scripts/*` (build_artifacts.sh, gh_release.sh, release_all.sh, etc.)
  - Version bumper: `tools/bump_version.py`

🛠️ Build Artifacts
Artifacts are attached to this release:

- regen88_codex-0.1.0-py3-none-any.whl
- regen88_codex-0.1.0.tar.gz

**Verify locally (optional):**
```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
# Checksums
sha256sum dist/*           # Linux
shasum -a 256 dist/*       # macOS
```

🔄 CI/CD & Release Flow

- On PR/Push: Lint (black/isort/flake8), type-check (mypy), tests (pytest).
- On tag v*: Build wheel+sdist and attach to GitHub Release automatically.
- On release published: Optional PyPI publish if PYPI_API_TOKEN secret is set.

🧭 Roadmap

- Optional numba/parallel paths for heavier analysis.
- Typer-based CLI convenience wrappers.
- Additional analysis modules & interactive plots (Plotly).
- Property-based tests expansion (Hypothesis) and fuzz inputs.

🔐 Security

This is educational software. Do not treat the reseed/correction heuristics as cryptographic guarantees.  
Report concerns privately (see SECURITY.md).

🙏 Thanks

Thanks to contributors and reviewers who helped shape the initial structure, automation, and tests.