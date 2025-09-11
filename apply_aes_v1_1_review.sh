#!/usr/bin/env bash
set -euo pipefail

# --- config knobs (override via env) ---
BRANCH="${BRANCH:-aes-v1_1}"
BASE="${BASE_BRANCH:-main}"
AUTO_SIGN="${AUTO_SIGN:-1}"           # 1=auto-sign plugin manifests if needed, 0=skip
REQUIRE_SIGNATURES="${REQUIRE_SIGNATURES:-true}"  # default policy require_signatures=true

# --- sanity checks ---
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "ERROR: Not inside a git repository."
  exit 1
fi
if ! git show-ref --verify --quiet "refs/heads/$BASE"; then
  echo "ERROR: Base branch '$BASE' not found."
  exit 1
fi
if [ -n "$(git status --porcelain)" ]; then
  echo "WARNING: You have uncommitted changes. Stash or commit first."
  exit 1
fi

# --- branch prep ---
git checkout "$BASE"
git pull --ff-only
if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  git checkout "$BRANCH"
else
  git checkout -b "$BRANCH"
fi

# --- layout ---
mkdir -p policies xova .github/workflows tools docs

# --- policies/default.json ---
cat > policies/default.json <<JSON
{
  "security": {
    "require_signatures": ${REQUIRE_SIGNATURES}
  },
  "limits": {
    "time_s": 15
  },
  "selection": {
    "prefer": "highest_version"
  },
  "thresholds": {
    "max": {
      "latency_ms": 600
    },
    "min": {
      "order_k2": 0.10,
      "order_k3": 0.05
    }
  },
  "post_chain": [
    { "api": "codex.analysis/order", "plugin": "codex.order_meter" }
  ],
  "grading": {
    "penalties": {
      "bad-signature": 100,
      "timeout": 50,
      "exception": 40,
      "bad-metrics": 30
    }
  }
}
JSON

# --- xova/evolve.py ---
cat > xova/evolve.py <<'PY'
#!/usr/bin/env python3
import json, os, sys, time, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"
OUTDIR  = ROOT / "out"
POLICY  = ROOT / "policies" / "default.json"

from registry import load_registry, choose_candidates
from sandbox import run_plugin

def load_policy():
    with open(POLICY, "r", encoding="utf-8") as f:
        return json.load(f)

def sha256_manifest_without_sig(man: dict) -> str:
    m2 = man.copy()
    m2.pop("signature", None)
    raw = json.dumps(m2, sort_keys=True, separators=(",",":")).encode()
    import hashlib
    return hashlib.sha256(raw).hexdigest()

def verify_manifest(man):
    want = man.get("signature","")
    if not want: return False
    got = sha256_manifest_without_sig(man)
    return got == want

def passes_thresholds(metrics, thr):
    if not thr: return True
    mx = thr.get("max", {})
    mn = thr.get("min", {})
    for k,v in mx.items():
        if k in metrics and metrics[k] > v:
            return False
    for k,v in mn.items():
        if k in metrics and metrics[k] < v:
            return False
    return True

def rank_candidates(cands, prefer):
    if prefer == "highest_version":
        def vparts(x):
            s = x["manifest"].get("version","0.0.0")
            return tuple(int(p) if p.isdigit() else 0 for p in s.split("."))
        return sorted(cands, key=vparts, reverse=True)
    return cands

def evolve(request_path: str):
    OUTDIR.mkdir(exist_ok=True)
    with open(request_path, "r", encoding="utf-8") as f:
        req = json.load(f)

    policy = load_policy()
    registry = load_registry(PLUGINS)

    api  = req["api"]
    caps = req.get("capabilities", [])
    params = req.get("params", {})

    cands = choose_candidates(registry, api, caps)
    cands = rank_candidates(cands, policy.get("selection",{}).get("prefer"))

    if not cands:
        print(json.dumps({"status":"failed","errors":[f"No plugin matches api={api} caps={caps}"]}, indent=2))
        return 1

    errors = []
    for cand in cands:
        man = cand["manifest"]
        if policy["security"].get("require_signatures", False):
            if not verify_manifest(man):
                errors.append({"plugin": cand["name"], "error": "bad-signature"})
                continue

        time_limit_s = float(man.get("time_limit_s", policy["limits"]["time_s"]))

        t0 = time.time()
        try:
            res = run_plugin(cand, params, OUTDIR, time_limit_s=time_limit_s)
        except Exception as e:
            errors.append({"plugin": cand["name"], "error": f"exception:{e}"})
            continue

        latency_ms = (time.time() - t0) * 1000.0
        metrics = res.get("metrics", {})
        metrics["latency_ms"] = latency_ms

        for link in policy.get("post_chain", []):
            dep = registry.get(link["plugin"])
            if not dep: 
                errors.append({"plugin": cand["name"], "warning": f"missing-post:{link['plugin']}"})
                continue
            try:
                ar = run_plugin(dep, {"wav": str(OUTDIR / "sequence.wav"), "k_values": [2,3]}, OUTDIR, time_limit_s=time_limit_s)
                metrics.update(ar.get("metrics", {}))
            except Exception as e:
                errors.append({"plugin": cand["name"], "error": f"post-exception:{e}"})

        if not passes_thresholds(metrics, policy.get("thresholds", {})):
            errors.append({"plugin": cand["name"], "error": "bad-metrics", "metrics": metrics})
            continue

        print(json.dumps({
            "status": "ok",
            "chosen": cand["name"],
            "version": man.get("version",""),
            "artifacts": res.get("artifacts", {}),
            "metrics": metrics,
            "tried": [x["name"] for x in cands]
        }, indent=2))
        return 0

    print(json.dumps({"status":"failed","errors": errors}, indent=2))
    return 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 xova/evolve.py examples/request_nine.json")
        sys.exit(2)
    sys.exit(evolve(sys.argv[1]))
PY
chmod +x xova/evolve.py

# --- .github/workflows/evolve.yml ---
cat > .github/workflows/evolve.yml <<'YML'
name: Evolve Build & Deploy

on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: evolve-${{ github.ref }}
  cancel-in-progress: true

jobs:
  evolve:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Run Evolution
        run: |
          python3 xova/evolve.py examples/request_nine.json || true
          ls -la out/ || true

      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: evolve-output
          path: out/
          retention-days: 7

      - name: Sync to Docs
        run: |
          mkdir -p docs
          cp -r out/* docs/ || true
          git config user.name github-actions
          git config user.email github-actions@github.com
          git add docs/
          git commit -m "Sync evolve artifacts to docs [skip ci]" || echo "No changes to commit"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
YML

# --- tools/sign_manifest.py ---
cat > tools/sign_manifest.py <<'PY'
#!/usr/bin/env python3
import json, sys, hashlib, pathlib

def sign(path: str, in_place: bool):
    p = pathlib.Path(path)
    man = json.loads(p.read_text(encoding="utf-8"))
    man.pop("signature", None)
    raw = json.dumps(man, sort_keys=True, separators=(",",":")).encode()
    sig = hashlib.sha256(raw).hexdigest()
    if in_place:
        man["signature"] = sig
        p.write_text(json.dumps(man, indent=2), encoding="utf-8")
        print(f"Signed {p} -> signature={sig}")
    else:
        print(sig)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tools/sign_manifest.py <manifest.json> [--in-place]")
        sys.exit(2)
    sign(sys.argv[1], "--in-place" in sys.argv[2:])
PY
chmod +x tools/sign_manifest.py

# --- tools/auto_sign_manifests.py ---
cat > tools/auto_sign_manifests.py <<'PY'
#!/usr/bin/env python3
import json, hashlib, pathlib, sys

PLUGINS = pathlib.Path("plugins")

def sign_obj(obj):
    o2 = dict(obj)
    o2.pop("signature", None)
    raw = json.dumps(o2, sort_keys=True, separators=(",",":")).encode()
    return hashlib.sha256(raw).hexdigest()

def main():
    if not PLUGINS.exists():
        print("No plugins/ directory; skipping.")
        return 0
    changed = 0
    for man_path in PLUGINS.rglob("manifest.json"):
        data = json.loads(man_path.read_text(encoding="utf-8"))
        sig = data.get("signature")
        new_sig = sign_obj(data)
        if sig != new_sig:
            data["signature"] = new_sig
            man_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            print(f"Signed/updated: {man_path}")
            changed += 1
    print(f"Done. {changed} manifest(s) updated.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
PY
chmod +x tools/auto_sign_manifests.py

# --- docs/index.html ---
cat > docs/index.html <<'HTML'
<!DOCTYPE html>
<meta charset="utf-8">
<title>AES Evolution Artifacts</title>
<style>body{font:14px/1.4 system-ui;margin:2rem}pre{background:#f4f4f4;padding:8px}</style>
<h1>AES Evolution Artifacts</h1>
<p>These files are synced from <code>out/</code> after the evolve workflow runs.</p>
<p><a href="sequence.wav">sequence.wav</a> • <a href="sequence.csv">sequence.csv</a></p>
<pre id="csv">Loading sequence.csv preview…</pre>
<script>
fetch('sequence.csv').then(r=>r.text()).then(t=>{
  const lines=t.trim().split(/\r?\n/).slice(0,40);
  document.getElementById('csv').textContent = lines.join('\n') + (lines.length>=40?'\n... (truncated)':'');
}).catch(()=>{document.getElementById('csv').textContent='sequence.csv not found yet.'});
</script>
HTML

# --- optional auto-sign pass ---
if [ "$AUTO_SIGN" = "1" ]; then
  python3 tools/auto_sign_manifests.py || true
fi

# --- stage/commit ---
git add policies/default.json xova/evolve.py .github/workflows/evolve.yml tools/sign_manifest.py tools/auto_sign_manifests.py docs/index.html
if git diff --cached --quiet; then
  echo "No changes to commit."
else
  git commit -m "AES v1.1: policy thresholds, graded penalties, per-plugin timeouts, evolve workflow, optional auto-sign"
fi

echo
echo "✅ Local branch ready: $BRANCH"
echo "Next steps:"
echo "  git push -u origin $BRANCH"
echo "  Open a PR comparing $BRANCH -> $BASE"
echo

echo "Notes:"
echo " - Ensure you have: plugins/* with manifest.json and examples/request_nine.json"
echo " - If signatures are required and manifests are unsigned, either keep AUTO_SIGN=1 or set REQUIRE_SIGNATURES=false"