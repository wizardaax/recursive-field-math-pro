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