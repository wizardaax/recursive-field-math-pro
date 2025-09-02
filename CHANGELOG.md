# Changelog

All notable changes to this project will be documented in this file.

The format loosely follows:
- Keep a Changelog (https://keepachangelog.com/en/1.1.0/)
- Conventional Commits categories (https://www.conventionalcommits.org/)

## [Unreleased]

### Features
- **Comprehensive plotting utilities**: Added `scripts/generate_plots.py` with CLI interface and utility functions for entropy pump analysis visualization
  - Variance reduction summary plots with threshold indicators
  - Phi-clamp distribution analysis across multiple games
  - Evaluation curve comparisons (before/after entropy pump)
  - Phase analysis plots showing rank-to-phase mapping and golden refraction
  - Comprehensive report generation combining all plot types
- **Enhanced demo PGNs**: Replaced problematic demo games with valid, well-known chess games (Kasparov-Topalov 1999, Fischer-Byrne 1956, Carlsen-Caruana 2018)
- **Improved error handling**: Enhanced `scripts/run_entropy_pump_harness.py` with comprehensive error handling for:
  - PGN parsing failures
  - Illegal move detection and recovery
  - Entropy pump analysis errors
  - Plot generation failures with graceful degradation

### Infrastructure
- **Expanded .gitignore**: Added rules to exclude plot artifacts and generated files:
  - Plot directories: `plots/`, `test_plots/`, `*_plots/`
  - Graphics file types: `*.png`, `*.jpg`, `*.pdf`, `*.svg`
  - Entropy pump artifacts: `entropy_pump_summary_*`

## [v0.1.1] - 2025-08-30

### Docs
- Clarify provenance of the “Hashing Extensions (Dual Hash Mode)” section and mark it with a conventional docs(gxsonic) commit for tooling traceability (commit 4d3250e8). (No functional changes.)

## [v0.1.0] - 2025-08-29
(Adjust this version/date if different in your repository.)

### Features
- Introduced Codex entropy-pump (golden ratio refraction) harness for chess PGN evaluation with variance reduction artifacts.
- Added dual-hash (BLAKE2b canonical + optional BLAKE3) documentation section describing:
  - Canonical hashing chain
  - Dual-hash opt-in fields (`audio_chunk_hashes`, `hash_extensions`)
  - Backward compatibility + downgrade behavior
  - Future extension ideas
  (Original docs landed in commit b5b6dbe8.)

### Docs
- Initial README detailing geometric field seed, Lucas/Fibonacci backbone, ratio laws, continued fractions, generating functions, CLI quickstart, agent hooks, and entropy-pump usage.

### Tooling / CI
- CI workflows: codex-agent, docs, docs-preview, release badges.

---

## Guidance

For the next release:
1. Add changes under Unreleased.
2. On release, promote them into a new version section with date.
3. Regenerate compare links.

## Compare Links
[Unreleased]: https://github.com/wizardaax/recursive-field-math-pro/compare/v0.1.1...HEAD
[v0.1.1]: https://github.com/wizardaax/recursive-field-math-pro/compare/v0.1.0...v0.1.1
[v0.1.0]: https://github.com/wizardaax/recursive-field-math-pro/releases/tag/v0.1.0
