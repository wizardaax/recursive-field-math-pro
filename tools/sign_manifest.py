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