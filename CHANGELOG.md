# Changelog

All notable changes to this project will be documented in this file.

The format loosely follows:
- Keep a Changelog (https://keepachangelog.com/en/1.1.0/)
- Conventional Commits categories (https://www.conventionalcommits.org/)

## [Unreleased]

### Added
- Release workflow publishes to PyPI on tags if `PYPI_API_TOKEN` secret is set
- `scripts/demo_loom.sh`: One-click demo artifact generation for 60s Loom recording
- `scripts/publish_pypi.sh`: Manual local PyPI publish helper using Twine
- Marketing kit in `marketing/` directory:
  - `x_thread.md`: X/Twitter thread (12 posts) on ternary cognition and φ-refraction
  - `blog_ternary_agents.md`: 800-word blog post on Xova Intelligence and Lucas 4–7–11 resonance
  - `pitch_deck.md`: Concise one-pager for problem/solution/traction/roadmap
  - `hn_post.md`: Hacker News announcement with reproducibility steps
  - `reddit_ml_post.md`: r/MachineLearning community post
  - `vc_dm_templates.md`: Short and long investor outreach templates
- README brand header for "Xova Intelligence — Ternary Field Agents" (soft brand, no breaking changes)

### Changed
- Standardized release notes body in `.github/workflows/release.yml` with install/verify snippet at top
- Release workflow now includes PyPI publishing step (conditional on `PYPI_API_TOKEN` secret)

### Fixed
- Improved secret check in release workflow to use proper GitHub Actions syntax
- Enhanced file existence check in `scripts/publish_pypi.sh` to avoid glob expansion issues

## [v0.2.0] - 2025-01-27

### Features
- **Onboarding Enhancements**: Added comprehensive onboarding improvements for better user experience
  - TL;DR block at the top of README for instant comprehension
  - "Who is this for?" audience section clarifying intended users (researchers, students, developers, AI agents, game analysts, data scientists)
  - `examples/` directory with ready-to-run demo files:
    - `sample.json`: CLI usage examples and expected outputs
    - `sample.md`: Quick demo guide with mathematical background
    - `sample.ipynb`: Interactive Jupyter notebook for hands-on exploration

### Docs
- Enhanced README structure with improved navigation and clarity
- Updated directory layout documentation to include examples/
- Version bump to v0.2.0 across applicable files

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
[Unreleased]: https://github.com/wizardaax/recursive-field-math-pro/compare/v0.2.0...HEAD
[v0.2.0]: https://github.com/wizardaax/recursive-field-math-pro/compare/v0.1.1...v0.2.0
[v0.1.1]: https://github.com/wizardaax/recursive-field-math-pro/compare/v0.1.0...v0.1.1
[v0.1.0]: https://github.com/wizardaax/recursive-field-math-pro/releases/tag/v0.1.0
