#!/usr/bin/env python3
import hashlib
import json
import os
import sys
import time
from pathlib import Path

from registry import choose_candidates, load_registry
from sandbox import run_plugin

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"
OUTDIR = ROOT / "out"
POLICY = ROOT / "policies" / "default.json"


def load_policy():
    with open(POLICY, encoding="utf-8") as f:
        return json.load(f)


def sha256_manifest_without_sig(man: dict) -> str:
    m2 = man.copy()
    m2.pop("signature", None)
    raw = json.dumps(m2, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def verify_manifest(man):
    want = man.get("signature", "")
    if not want:
        return False
    got = sha256_manifest_without_sig(man)
    return got == want


def passes_thresholds(metrics, thr):
    if not thr:
        return True
    mx = thr.get("max", {})
    mn = thr.get("min", {})
    for k, v in mx.items():
        if k in metrics and metrics[k] > v:
            return False
    return all(not (k in metrics and metrics[k] < v) for k, v in mn.items())


def rank_candidates(cands, prefer):
    if prefer == "highest_version":

        def vparts(x):
            s = x["manifest"].get("version", "0.0.0")
            return tuple(int(p) if p.isdigit() else 0 for p in s.split("."))

        return sorted(cands, key=vparts, reverse=True)
    return cands


def _write_summaries(chosen_name, man, metrics, api):
    """S/B add-on: persist run metadata for dashboards/badges."""
    OUTDIR.mkdir(exist_ok=True)
    summary = {
        "chosen": chosen_name,
        "version": man.get("version", ""),
        "metrics": metrics,
        "timestamp": time.time(),
        "request_api": api,
        "commit": os.environ.get("GITHUB_SHA", ""),
    }
    (OUTDIR / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    (OUTDIR / "metrics.json").write_text(
        json.dumps(metrics, separators=(",", ":")), encoding="utf-8"
    )


def evolve(request_path: str):
    OUTDIR.mkdir(exist_ok=True)
    with open(request_path, encoding="utf-8") as f:
        req = json.load(f)

    policy = load_policy()
    registry = load_registry(PLUGINS)

    api = req["api"]
    caps = req.get("capabilities", [])
    params = req.get("params", {})

    cands = choose_candidates(registry, api, caps)
    cands = rank_candidates(cands, policy.get("selection", {}).get("prefer"))

    if not cands:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "errors": [f"No plugin matches api={api} caps={caps}"],
                },
                indent=2,
            )
        )
        return 1

    errors = []
    for cand in cands:
        man = cand["manifest"]
        if policy["security"].get("require_signatures", False) and not verify_manifest(man):
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
        metrics = res.get("metrics", {}) or {}
        metrics["latency_ms"] = latency_ms

        for link in policy.get("post_chain", []):
            dep = registry.get(link["plugin"])
            if not dep:
                errors.append(
                    {
                        "plugin": cand["name"],
                        "warning": f"missing-post:{link['plugin']}",
                    }
                )
                continue
            try:
                ar = run_plugin(
                    dep,
                    {"wav": str(OUTDIR / "sequence.wav"), "k_values": [2, 3]},
                    OUTDIR,
                    time_limit_s=time_limit_s,
                )
                metrics.update(ar.get("metrics", {}) or {})
            except Exception as e:
                errors.append({"plugin": cand["name"], "error": f"post-exception:{e}"})

        if not passes_thresholds(metrics, policy.get("thresholds", {})):
            errors.append(
                {"plugin": cand["name"], "error": "bad-metrics", "metrics": metrics}
            )
            continue

        _write_summaries(cand["name"], man, metrics, api)

        print(
            json.dumps(
                {
                    "status": "ok",
                    "chosen": cand["name"],
                    "version": man.get("version", ""),
                    "artifacts": res.get("artifacts", {}),
                    "metrics": metrics,
                    "tried": [x["name"] for x in cands],
                },
                indent=2,
            )
        )
        return 0

    print(json.dumps({"status": "failed", "errors": errors}, indent=2))
    return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 xova/evolve.py examples/request_nine.json")
        sys.exit(2)
    sys.exit(evolve(sys.argv[1]))
