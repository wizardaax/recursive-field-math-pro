[![CI](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/ci.yml/badge.svg)](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/regen88-codex.svg)](https://pypi.org/project/regen88-codex/)
[![Release](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/release.yml/badge.svg)](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/release.yml)
---

# Projex X1 — Original Formula (Lucas 4–7–11)

## TL;DR

🚀 **Quick Start**: A mathematical research tool for recursive field computations using Lucas numbers and golden ratio formulas, with built-in CLI commands, chess game analysis via entropy pump, and agent-ready workflows.

**Key Features**: Lucas/Fibonacci sequences, field geometry, ratio calculations, Egyptian fractions, entropy-pump variance reduction for chess PGN analysis, and comprehensive CI/CD pipeline.

**In 30 seconds**: `pip install regen88-codex && rfm lucas 0 10 && rfm egypt && python -m pytest`

**Development**: `bash scripts/dev_bootstrap.sh && bash scripts/dev_check.sh`

---

> **Repo:** `wizardaax/recursive-field-math-pro`  
> **Focus:** Radial–angular recursive field + Lucas/Fibonacci backbone, with agent-ready CLI, tests, docs, data hooks, and CI.
> **Family name:** snellman
> **Given name:** adam a

## Status

[![Codex Agent](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/codex-agent.yml/badge.svg)](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/codex-agent.yml)
[![Docs](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/docs.yml/badge.svg)](https://wizardaax.github.io/recursive-field-math-pro/)
[![Docs Preview](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/docs-preview.yml/badge.svg)](https://github.com/wizardaax/recursive-field-math-pro/actions/workflows/docs-preview.yml)
[![Release](https://img.shields.io/github/v/release/wizardaax/recursive-field-math-pro?logo=github)](https://github.com/wizardaax/recursive-field-math-pro/releases)
[![License](https://img.shields.io/github/license/wizardaax/recursive-field-math-pro)](LICENSE)

- 📘 **Docs**: [GitHub Pages](https://wizardaax.github.io/recursive-field-math-pro/)
- 🚀 **Latest Release**: [Releases tab](https://github.com/wizardaax/recursive-field-math-pro/releases)
- ⚡ **CI/CD**: [Actions dashboard](https://github.com/wizardaax/recursive-field-math-pro/actions)

> **Docs Previews:** Open a PR against `main`. The **docs-preview** workflow deploys a temporary site and comments the preview URL on your PR automatically.

## Regen88 Codex — Development Workflow

🚀 **Complete cross-platform build, test, and release setup**

### Quick Setup
```bash
bash scripts/dev_bootstrap.sh    # Set up development environment  
bash scripts/dev_check.sh        # Run linting, type checking, and tests
bash scripts/build_artifacts.sh  # Build wheel and sdist packages
bash scripts/check_artifacts.sh  # Verify build artifacts
```

### Release Workflow  
```bash
# Tag and release (triggers GitHub Actions)
bash scripts/tag_and_push.sh v0.1.0 "Regen88 Codex v0.1.0"

# Or complete workflow with verification
bash scripts/release_all.sh v0.1.0 "Regen88 Codex v0.1.0"
```

### Features
- **CI/CD**: Multi-Python version testing (3.9-3.12) across Linux, Windows, macOS
- **Release Automation**: Tag-based releases with artifact uploads to GitHub
- **PyPI Publishing**: Optional auto-publish on release (requires `PYPI_API_TOKEN` secret)
- **Pre-commit Hooks**: Automated code quality checks with ruff, pytest
- **Development Scripts**: Bootstrap, check, build, verify, tag, and release workflows

### Artifacts  
- **Wheel**: `regen88_codex-*.whl` (installable via pip)
- **Source**: `regen88-codex-*.tar.gz` (source distribution)
- **Release**: Automated GitHub releases with checksums

## Geometric Field (Seed)
- Radial growth: \( r_n = 3\sqrt{n} \)  
- Angular phase: \( \theta_n = n\varphi \), where \( \varphi = \frac{1+\sqrt{5}}{2} \)  
- Base anchor: “Locked in root” at \( r=\sqrt{3} \)  
- Cycle cue: \( \pi \rightarrow 2\pi \rightarrow 3\pi \)

## Lucas Initialization
\((L_0,L_1,L_2,L_3,L_4,L_5) = (2,1,3,4,7,11), \quad L_{n+1} = L_n + L_{n-1}\)

## Backbone (Fibonacci/Lucas)
- \( F_n = \dfrac{\varphi^n - \psi^n}{\sqrt{5}},\quad L_n = \varphi^n + \psi^n,\quad \psi = 1-\varphi \)  
- Matrix form: \( L_n = \mathrm{tr}(Q^n),\quad Q=\begin{pmatrix}1&1\\1&0\end{pmatrix} \)  
- Fibonacci–Lucas link: \( L_n = F_{n-1} + F_{n+1} \)  
- Cassini (Lucas): \( L_n^2 - L_{n-1}L_{n+1} = 5(-1)^n \)  
- Pell-type norm: \( L_n^2 - 5F_n^2 = 4(-1)^n \)

## Signature Triple (4–7–11)
- \( L_3=4,\;L_4=7,\;L_5=11 \)  
- Egyptian fraction:  
  \( \frac{1}{4}+\frac{1}{7}+\frac{1}{11}=\frac{149}{308}=\frac{1}{2}-\frac{5}{308} \)  
- Products/sums: \( 4\cdot7\cdot11=308 \), \( 4\cdot7+4\cdot11+7\cdot11=149 \)  
- Frobenius (4,7): \( g(4,7)=4\cdot7-4-7=17 \)  
- Additive chain cue: \( 4+7=11 \)

## Ratio Law & Accuracy
\( \frac{L_{n+1}}{L_n} - \varphi = (-1)^{n+1}\frac{\sqrt{5}\,|\psi|^n}{L_n} \)  

Asymptotic law: \( \left|\frac{L_{n+1}}{L_n}-\varphi\right| \sim \frac{\sqrt{5}}{\varphi^{2n}} \)

Bounds:  
\( \frac{\sqrt{5}}{L_n(L_n+|\psi|^n)} < \Big|\tfrac{L_{n+1}}{L_n}-\varphi\Big| < \frac{\sqrt{5}}{L_n(L_n-|\psi|^n)} \)

## Continued Fraction / Semiconvergents
\( \frac{L_{n+1}}{L_n}=[1; \underbrace{1,\dots,1}_{n-2},3] \)  
Equivalently \( r_m=[1;1^m,3]=\frac{L_{m+3}}{L_{m+2}} \).

## Generating Functions
\( \sum_{n\ge0}F_n x^n=\frac{x}{1-x-x^2}, \quad \sum_{n\ge0}L_n x^n=\frac{2-x}{1-x-x^2} \)

---

## Quickstart

```bash
# [A] install (editable)
pip install -e .

# [B] run CLI examples
rfm field 1 10           # r, theta for n=1..10
rfm lucas 0 10           # L_n for n in [0,10]
rfm ratio 5              # L_{n+1}/L_n, error bounds
rfm egypt                # 1/4+1/7+1/11 decomposition check
rfm sig                  # signature triple summary
rfm eval results.json    # evaluate entropy pump results

# [C] tests
pytest -q
```

## Who is this for?

**🔬 Researchers & Mathematicians**: Explore Lucas number sequences, golden ratio properties, continued fractions, and recursive field mathematics with computational tools.

**🎓 Students & Educators**: Learn about Fibonacci/Lucas relationships, Egyptian fractions, and generating functions through interactive CLI examples and comprehensive documentation.

**💻 Developers & Engineers**: Integrate mathematical computations into applications, leverage agent-ready workflows, and utilize CI/CD-ready project structure.

**🤖 AI Agents & Automation**: Use keyword-based function routing (`my_recursive_ai.py`), standardized CLI interfaces, and structured output formats for programmatic analysis.

**♟️ Game Analysts**: Apply entropy-pump variance reduction techniques to chess PGN analysis with golden ratio refraction formulas.

**📊 Data Scientists**: Process numerical sequences, generate plots and visualizations, and validate mathematical models with built-in acceptance criteria.

## Agent Hooks
- Single command deploy: `scripts/deploy.sh` (edit `REMOTE=` to your GitHub SSH/HTTPS URL)
- CI: `.github/workflows/ci.yml` runs lint & tests on push
- `my_recursive_ai.py` provides keyword → function routing for agent mode

## Codex Entropy-Pump Feature

**Pull request:** [Add Codex entropy-pump feature with golden refraction for game analysis](https://github.com/wizardaax/recursive-field-math-pro/pull/2)  
**Status:** Merged by @wizardaax (2025-08-29)

### What’s Inside

- Golden ratio refraction formula for variance reduction in chess game evaluations
- Core implementation in `scripts/codex_entropy_pump.py`
- PGN analysis harness: processes chess games, generates plots, metrics, and summary artifacts
- Lucas weights for resonance adjustment
- Results: Up to ~92% variance reduction on classic games (Kasparov, Fischer, Carlsen)
- Artifacts: Curve plots, φ-clamp histograms, JSON/TSV summaries
- Comprehensive tests for invariants, edge cases, and Lucas weights

### Quick Usage

```bash
python -m scripts.run_entropy_pump_harness
# Artifacts appear in the out/ directory: *_curve.png, *_clamp.png, *.json, *.tsv, *.md
```

**New:** The harness now automatically evaluates results against acceptance rules and generates summary reports:

```bash
# Evaluate existing results
rfm eval out/entropy_pump_summary_*.json --markdown

# Or use the standalone tool
python scripts/evaluate_results.py out/entropy_pump_summary_*.json
```

### Quick Run (One-Click)
[⚡ Run Codex Agent](https://github.com/wizardaax/recursive-field-math-pro/issues/new?title=Entropy+pump+run+on+sample+PGNs&body=%2Fagent+run)

That link opens a new issue with the title prefilled (Entropy pump run on sample PGNs) and the comment body /agent run. You just hit Submit new issue and the workflow kicks off.

### What Happens
- The **codex-agent** workflow runs.
- It generates:
  - `entropy_pump_summary_*.json` / `.tsv`
  - Plots (`*_curve.png`, `*_clamp.png`)
- It posts a **summary comment** back on the issue:
  - Variance reduction %
  - MAE delta %
  - φ-clamp peak (target 38.2° ± 2°)
  - Lucas weights
- Verdict: ✅ PASS (meets thresholds) or ⚠️ CHECK

### Acceptance Rules
- Variance reduction ≥ **20%**
- MAE delta ≥ **2%**
- φ-clamp peak within **±2° of 38.2°**

## Layout
```
recursive-field-math-pro/
├─ src/recursive_field_math/
│  ├─ __init__.py
│  ├─ constants.py
│  ├─ fibonacci.py
│  ├─ lucas.py
│  ├─ field.py
│  ├─ ratios.py
│  ├─ continued_fraction.py
│  ├─ generating_functions.py
│  ├─ egyptian_fraction.py
│  ├─ signatures.py
│  └─ cli.py
├─ my_recursive_ai.py
├─ tests/
│  └─ test_core.py
├─ examples/
│  ├─ sample.json (CLI usage examples)
│  ├─ sample.md (quick demo guide)
│  └─ sample.ipynb (interactive notebook)
├─ data/
│  ├─ AEON-Gravyflyer.csv (placeholder)
│  └─ Enhanced_Zeta_Analysis.csv (placeholder)
├─ scripts/
│  └─ deploy.sh
├─ .github/workflows/ci.yml
├─ pyproject.toml
├─ LICENSE
└─ README.md
```

### 🔒 Hashing Extensions (Dual Hash Mode)

Canonical hashing (spec 0.1):
- Every glyph descriptor includes `audio_chunk_hash` (BLAKE2b-256 hex, 64 chars)
- The manifest’s `audio_merkle_root` is built from BLAKE2b (no alternative roots yet)
- Verification chain: raw audio bytes → BLAKE2b → descriptor → descriptor hash → Merkle inclusion

Why dual hash?
- BLAKE2b remains stable + widely available
- BLAKE3 offers speed + incremental benefits
- We expose BLAKE3 as an opt-in extension without altering canonical commitments

Enabling dual-hash:
```
pip install blake3
python -m gxsonic.cli --n-start 1 --n-end 2 --out out_dual --dual-hash
```

Descriptor (dual-hash mode) adds:
```
"audio_chunk_hash": "<blake2b>",
"audio_chunk_hashes": {
  "blake2b": "<blake2b>",
  "blake3": "<blake3>"
},
"hash_extensions": { "blake3": true }
```

Manifest adds (only when dual enabled):
```
"hash_extensions": { "blake3": true }
```

Backward compatibility:
- Older v0.1 readers parse `audio_chunk_hash` exactly as before
- Unknown fields (`audio_chunk_hashes`, `hash_extensions`) are ignored per typical permissive parsing
- Merkle root unchanged (BLAKE2b-only commitment)

Graceful downgrade:
- If `--dual-hash` is requested but `blake3` is missing:
  - CLI prints a warning
  - Output omits extension fields (pure canonical mode)
  - Exit code still 0 (non-fatal)

Quick smoke test:
```
pip install blake3
python -m gxsonic.cli --n-start 7 --n-end 8 --out test_dual --dual-hash
jq '.audio_chunk_hash,.audio_chunk_hashes.blake3' test_dual/descriptors/glyph_000007.json
```

Basic verifier sketch (Python):
```python
import json, hashlib, pathlib

d = json.loads(pathlib.Path("test_dual/descriptors/glyph_000007.json").read_text())
raw = pathlib.Path("test_dual/audio/glyph_000007.wav").read_bytes()
b2 = hashlib.blake2b(raw, digest_size=32).hexdigest()
assert b2 == d["audio_chunk_hash"]
if "audio_chunk_hashes" in d and "blake3" in d["audio_chunk_hashes"]:
    import blake3
    b3 = blake3.blake3(raw).hexdigest()
    assert b3 == d["audio_chunk_hashes"]["blake3"]
print("OK")
```

Future directions (non-breaking ideas):
- Optional `audio_merkle_root_blake3`
- Negotiated hash set in a future OFFER variant
- Streaming/incremental validation path using BLAKE3 chunk state

Security note:
Dual-hash is additive; it does not “mix” digests. Canonical authenticity still hinges on BLAKE2b + signatures (if present).

Note: This section was first introduced in commit b5b6dbe8 with a generic message; this clarifier adds conventional docs(gxsonic) traceability (no functional changes).