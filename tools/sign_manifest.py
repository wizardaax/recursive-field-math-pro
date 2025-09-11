#!/usr/bin/env python3
"""Sign a single plugin manifest file."""

import json
import hashlib
import argparse
from pathlib import Path


def sha256_manifest_without_sig(manifest: dict) -> str:
    """Calculate SHA-256 hash of manifest without signature field."""
    manifest_copy = manifest.copy()
    manifest_copy.pop("signature", None)
    canonical_json = json.dumps(manifest_copy, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode()).hexdigest()


def sign_manifest(manifest_path: Path, in_place: bool = False) -> dict:
    """Sign a manifest file.
    
    Args:
        manifest_path: Path to manifest.json file
        in_place: If True, update the file in place
        
    Returns:
        Signed manifest dictionary
    """
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    # Generate signature
    signature = sha256_manifest_without_sig(manifest)
    manifest["signature"] = signature
    
    if in_place:
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
    
    return manifest


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Sign a plugin manifest file")
    parser.add_argument("manifest", help="Path to manifest.json file")
    parser.add_argument("--in-place", action="store_true", 
                       help="Update the file in place")
    
    args = parser.parse_args()
    
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"Error: Manifest file not found: {manifest_path}")
        return 1
    
    try:
        signed_manifest = sign_manifest(manifest_path, args.in_place)
        
        if args.in_place:
            print(f"Signed manifest updated: {manifest_path}")
        else:
            print(json.dumps(signed_manifest, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"Error signing manifest: {e}")
        return 1


if __name__ == "__main__":
    exit(main())