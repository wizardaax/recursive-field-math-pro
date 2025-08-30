# Changelog

All notable changes to this project will be documented in this file.

The format loosely follows:
- Keep a Changelog (https://keepachangelog.com/en/1.1.0/)
- Conventional Commits categories (https://www.conventionalcommits.org/)

## [Unreleased]

### (no changes yet)

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
