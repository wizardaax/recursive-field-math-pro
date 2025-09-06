#!/usr/bin/env bash
# Release helper for regen88-codex
# Usage:
#   tools/release.sh [VERSION] [BRANCH]
# Examples:
#   tools/release.sh v0.2.0a1 v0.2.0a1-full-release
#   tools/release.sh v0.2.0 main
#
# Env toggles:
#   FORCE=1   # re-tag if tag already exists (delete/recreate locally and on origin)
#   DRY_RUN=1 # print actions without executing pushes/gh release

set -euo pipefail

VERSION="${1:-v0.2.0a1}"              # Tag to create (e.g., v0.2.0a1 or v0.2.0)
BRANCH="${2:-v0.2.0a1-full-release}"  # Target commit/branch for the tag
TAG="$VERSION"

log() { printf "\033[1;34m==>\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33m[warn]\033[0m %s\n" "$*" >&2; }
err() { printf "\033[1;31m[err]\033[0m %s\n" "$*" >&2; exit 1; }

run() {
  if [[ "${DRY_RUN:-0}" != "0" ]]; then
    echo "+ $*"
  else
    eval "$@"
  fi
}

# --- sanity & setup ---------------------------------------------------------
log "Fetching remotes and switching to ${BRANCH}"
run "git fetch --all --prune"
run "git switch '${BRANCH}'"

log "Top commit:"
run "git log -1 --oneline"

# Optional dependency sanity (PEP 621)
if ! grep -qE '^dependencies\s*=\s*\[.*"numpy>=' pyproject.toml; then
  warn "numpy runtime dependency not found in [project].dependencies"
fi

# --- tag handling -----------------------------------------------------------
remote_has_tag=0
if git ls-remote --exit-code --tags origin "${TAG}" >/dev/null 2>&1; then
  remote_has_tag=1
fi

if git rev-parse -q --verify "refs/tags/${TAG}" >/dev/null 2>&1 || [[ $remote_has_tag -eq 1 ]]; then
  if [[ "${FORCE:-0}" == "1" ]]; then
    warn "Tag ${TAG} exists; FORCE=1 set, re-tagging..."
    run "git tag -d '${TAG}'" || true
    if [[ $remote_has_tag -eq 1 ]]; then
      run "git push --delete origin '${TAG}'"
    fi
  else
    err "Tag ${TAG} already exists. Re-run with FORCE=1 to re-tag."
  fi
fi

log "Creating annotated tag ${TAG}"
run "git tag -a '${TAG}' -m 'regen88-codex ${VERSION}'"

log "Pushing tag ${TAG} to origin"
run "git push origin '${TAG}'"

# --- GitHub release ---------------------------------------------------------
if command -v gh >/dev/null 2>&1; then
  if gh auth status >/dev/null 2>&1; then
    NOTES_FILE="CHANGELOG.md"
    log "Creating GitHub release ${TAG} (target=${BRANCH})"
    if [[ -f "${NOTES_FILE}" ]]; then
      run "gh release create '${TAG}' --target '${BRANCH}' --title 'regen88-codex ${VERSION}' --notes-file '${NOTES_FILE}'"
    else
      warn "CHANGELOG.md not found; creating release with generic notes"
      run "gh release create '${TAG}' --target '${BRANCH}' --title 'regen88-codex ${VERSION}' --notes 'Release ${VERSION}'"
    fi
  else
    warn "gh CLI not authenticated; skipping GitHub release creation"
  fi
else
  warn "gh CLI not found; skipping GitHub release creation"
fi

log "Done. CI/Trusted Publisher should build & publish to PyPI if configured."
log "Tip: to verify post-publish, run:"
echo "  pip install --no-cache-dir 'regen88-codex==${VERSION#v}' && regen88 wormhole-sim --n 256 --start 64 --width 64 --op phase_flip"