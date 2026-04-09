#!/usr/bin/env python3
"""
Deterministic SHA-256 manifest tool for research figure artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

CHUNK_SIZE_BYTES = 1024 * 1024  # 1 MB


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE_BYTES), b""):
            h.update(chunk)
    return h.hexdigest()


def list_files(fig_dir: Path) -> list[Path]:
    exts = {".png", ".svg", ".pdf"}
    files = [p for p in fig_dir.rglob("*") if p.is_file() and p.suffix.lower() in exts]
    return sorted(files)


def write_manifest(fig_dir: Path, out_file: Path) -> int:
    files = list_files(fig_dir)
    if not files:
        print(f"[ERROR] No figure files found under: {fig_dir}")
        return 2

    lines = []
    for path in files:
        digest = sha256_file(path)
        rel = path.relative_to(fig_dir).as_posix()
        lines.append(f"{digest}  {rel}")

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] Wrote {len(lines)} entries to {out_file}")
    return 0


def read_manifest(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        raw = raw.strip()
        if not raw:
            continue
        parts = raw.split("  ", 1)
        if len(parts) != 2:  # noqa: PLR2004
            raise ValueError(
                f'Invalid manifest format at line {lineno}: expected "<hash>  <path>", got: {raw!r}'
            )
        digest, rel = parts
        data[rel] = digest
    return data


def verify_manifest(fig_dir: Path, manifest: Path) -> int:
    if not manifest.exists():
        print(f"[ERROR] Missing manifest: {manifest}")
        return 2

    expected = read_manifest(manifest)
    files = list_files(fig_dir)
    actual: dict[str, str] = {}
    for path in files:
        rel = path.relative_to(fig_dir).as_posix()
        actual[rel] = sha256_file(path)

    failed = False

    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    if missing:
        failed = True
        print("[ERROR] Missing files from directory:")
        for rel in missing:
            print(f"  - {rel}")
    if extra:
        failed = True
        print("[ERROR] Extra files not present in manifest:")
        for rel in extra:
            print(f"  - {rel}")

    for rel, digest in expected.items():
        if rel in actual and actual[rel] != digest:
            failed = True
            print(f"[ERROR] Digest mismatch: {rel}")
            print(f"  expected: {digest}")
            print(f"  actual:   {actual[rel]}")

    if failed:
        return 1

    print(f"[OK] Manifest verified: {len(expected)} files")
    return 0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    w = sub.add_parser("write", help="write manifest from figure directory")
    w.add_argument("--dir", type=Path, required=True, dest="fig_dir")
    w.add_argument("--out", type=Path, required=True)

    v = sub.add_parser("verify", help="verify figure directory against manifest")
    v.add_argument("--dir", type=Path, required=True, dest="fig_dir")
    v.add_argument("--manifest", type=Path, required=True)

    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.cmd == "write":
        return write_manifest(args.fig_dir, args.out)
    if args.cmd == "verify":
        return verify_manifest(args.fig_dir, args.manifest)
    print("[ERROR] Unknown command")
    return 2


if __name__ == "__main__":
    sys.exit(main())
