#!/usr/bin/env python3
"""Bulk sign all plugin manifests."""

import json
import hashlib
from pathlib import Path


def sha256_manifest_without_sig(manifest: dict) -> str:
    """Calculate SHA-256 hash of manifest without signature field."""
    manifest_copy = manifest.copy()
    manifest_copy.pop("signature", None)
    canonical_json = json.dumps(manifest_copy, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode()).hexdigest()


def sign_all_manifests(plugins_dir: Path) -> int:
    """Sign all manifest.json files in plugins directory.
    
    Args:
        plugins_dir: Directory containing plugin subdirectories
        
    Returns:
        Number of manifests signed
    """
    signed_count = 0
    
    if not plugins_dir.exists():
        print(f"Plugins directory not found: {plugins_dir}")
        return 0
    
    for plugin_path in plugins_dir.iterdir():
        if not plugin_path.is_dir():
            continue
            
        manifest_path = plugin_path / "manifest.json"
        if not manifest_path.exists():
            print(f"Skipping {plugin_path.name}: no manifest.json found")
            continue
        
        try:
            # Load manifest
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            
            # Generate signature
            signature = sha256_manifest_without_sig(manifest)
            manifest["signature"] = signature
            
            # Save updated manifest
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)
            
            print(f"Signed: {plugin_path.name}")
            signed_count += 1
            
        except Exception as e:
            print(f"Error signing {plugin_path.name}: {e}")
            continue
    
    return signed_count


def main():
    """Main entry point."""
    # Find plugins directory relative to script location
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    plugins_dir = repo_root / "plugins"
    
    print(f"Looking for plugins in: {plugins_dir}")
    signed_count = sign_all_manifests(plugins_dir)
    
    if signed_count > 0:
        print(f"\nSigned {signed_count} manifest(s)")
    else:
        print("No manifests found to sign")
    
    return 0


if __name__ == "__main__":
    exit(main())