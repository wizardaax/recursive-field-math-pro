#!/usr/bin/env python3
"""Simple registry module for xova/evolve.py"""

import json
import os
from pathlib import Path

# Default location AES auto-evolve looks for plugin manifests when no
# explicit plugins_dir is passed. Adam's machine: C:\Xova\plugins. The
# AGI stack documents Xova's plugin host living there. Override via
# the XOVA_PLUGINS_DIR environment variable if needed.
DEFAULT_PLUGINS_DIR = os.environ.get("XOVA_PLUGINS_DIR", r"C:\Xova\plugins")


def load_registry(plugins_dir=None):
    """Load plugin registry from plugins directory.

    plugins_dir defaults to ``DEFAULT_PLUGINS_DIR`` (C:\\Xova\\plugins or the
    XOVA_PLUGINS_DIR env override). This closes the gap surfaced by the
    2026-05-02 federation audit — auto-evolve had nothing to rank/sandbox
    when callers omitted the arg.
    """
    if plugins_dir is None:
        plugins_dir = DEFAULT_PLUGINS_DIR
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
