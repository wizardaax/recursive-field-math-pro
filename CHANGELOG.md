# Changelog

All notable changes to this project will be documented in this file.

The format loosely follows:
- Keep a Changelog (https://keepachangelog.com/en/1.1.0/)
- Conventional Commits categories (https://www.conventionalcommits.org/)

## [Unreleased]

### Docs
- Clarify provenance of the “Hashing Extensions (Dual Hash Mode)” section and mark it with a conventional docs(gxsonic) commit for tooling traceability (commit 4d3250e8).

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

When you cut the next release:
1. Update the Unreleased section into a new version block with date.
2. Add a fresh Unreleased placeholder above it.

Example:
## [v0.1.1] - 2025-09-02
### Docs
- Clarify README dual-hash section placement (4d3250e8)

Then reset Unreleased.

## Compare Links (optional to add once tags exist)
You can append links like:
[v0.1.0]: https://github.com/wizardaax/recursive-field-math-pro/releases/tag/v0.1.0
[Unreleased]: https://github.com/wizardaax/recursive-field-math-pro/compare/v0.1.0...HEAD