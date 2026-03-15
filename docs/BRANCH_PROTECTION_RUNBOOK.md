# Branch Protection Runbook (Easy Mode)

This is the exact setup for `main` to enforce quality without killing velocity.

## 1) Enable protection for `main`
Settings → Branches → Add rule (or rulesets) for `main`.

## 2) Require pull requests
- ✅ Require a pull request before merging
- ✅ Require approvals: 1
- ✅ Dismiss stale approvals when new commits are pushed
- ✅ Require review from Code Owners

## 3) Require status checks to pass
Select these checks as **required**:
- `CI Quality Gate / Lint/Type/Test (ubuntu-latest / py3.11)`
- `CI Quality Gate / Reproducibility Figures + Manifest`
- `PR Reproducibility Check / repro-check`
- Coverage check (if present and stable name)

Also enable:
- ✅ Require branches to be up to date before merging

## 4) Protect history
- ✅ Restrict force pushes
- ✅ Do not allow deletions

## 5) Optional (recommended)
- ✅ Enable Merge Queue for `main`
- ✅ Auto-merge allowed for green PRs

## 6) Emergency bypass policy
Only repo admin may bypass, and must:
1. open issue documenting reason
2. include rollback plan
3. follow up with corrective PR within 24h
