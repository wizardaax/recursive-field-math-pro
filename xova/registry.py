#!/usr/bin/env python3
"""Simple registry module for xova/evolve.py"""

import json
from pathlib import Path


def load_registry(plugins_dir):
    """Load plugin registry from plugins directory"""
    registry = {}
    plugins_path = Path(plugins_dir)
    if plugins_path.exists():
        for plugin_file in plugins_path.glob("*.json"):
            try:
                with open(plugin_file) as f:
                    plugin_data = json.load(f)
                    registry[plugin_file.stem] = plugin_data
            except Exception:
                pass
    return registry


def choose_candidates(registry, api, capabilities):
    """Choose plugin candidates based on API and capabilities"""
    candidates = []
    for name, plugin_data in registry.items():
        manifest = plugin_data.get("manifest", {})
        if manifest.get("api") == api:
            plugin_caps = set(manifest.get("capabilities", []))
            required_caps = set(capabilities)
            if required_caps.issubset(plugin_caps):
                candidates.append({"name": name, "manifest": manifest})
    return candidates
