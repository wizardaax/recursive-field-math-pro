#!/usr/bin/env python3
"""Registry module for loading and managing plugin candidates."""

import json
from pathlib import Path
from typing import Dict, List, Any


def load_registry(plugins_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Load all plugins from the plugins directory into a registry."""
    registry = {}
    
    if not plugins_dir.exists():
        return registry
    
    for plugin_dir in plugins_dir.iterdir():
        if not plugin_dir.is_dir():
            continue
            
        manifest_path = plugin_dir / "manifest.json"
        if not manifest_path.exists():
            continue
            
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            
            plugin_data = {
                "name": plugin_dir.name,
                "path": plugin_dir,
                "manifest": manifest
            }
            registry[plugin_dir.name] = plugin_data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load plugin {plugin_dir.name}: {e}")
            continue
    
    return registry


def choose_candidates(registry: Dict[str, Dict[str, Any]], api: str, capabilities: List[str] = None) -> List[Dict[str, Any]]:
    """Choose plugin candidates that match the API and capabilities."""
    candidates = []
    capabilities = capabilities or []
    
    for plugin_name, plugin_data in registry.items():
        manifest = plugin_data["manifest"]
        
        # Check if plugin supports the required API
        supported_apis = manifest.get("apis", [])
        if api not in supported_apis:
            continue
        
        # Check if plugin supports all required capabilities
        plugin_caps = set(manifest.get("capabilities", []))
        required_caps = set(capabilities)
        
        if not required_caps.issubset(plugin_caps):
            continue
        
        candidates.append(plugin_data)
    
    return candidates