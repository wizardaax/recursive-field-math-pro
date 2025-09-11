#!/usr/bin/env python3
"""Plugin registry loader for Xova evolution system."""

import json
from pathlib import Path
from typing import Dict, List, Any


def load_registry(plugins_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Load plugin registry from plugins directory.
    
    Args:
        plugins_dir: Directory containing plugin subdirectories
        
    Returns:
        Dictionary mapping plugin names to plugin info
    """
    registry = {}
    
    if not plugins_dir.exists():
        return registry
        
    for plugin_path in plugins_dir.iterdir():
        if not plugin_path.is_dir():
            continue
            
        manifest_path = plugin_path / "manifest.json"
        if not manifest_path.exists():
            continue
            
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
                
            plugin_info = {
                "name": plugin_path.name,
                "path": plugin_path,
                "manifest": manifest
            }
            registry[plugin_path.name] = plugin_info
            
        except (json.JSONDecodeError, OSError):
            # Skip invalid manifests
            continue
            
    return registry


def choose_candidates(registry: Dict[str, Dict[str, Any]], 
                     api: str, 
                     capabilities: List[str]) -> List[Dict[str, Any]]:
    """Choose plugin candidates that match API and capabilities.
    
    Args:
        registry: Plugin registry dictionary
        api: Required API string
        capabilities: List of required capabilities
        
    Returns:
        List of matching plugin candidates
    """
    candidates = []
    
    for plugin_name, plugin_info in registry.items():
        manifest = plugin_info["manifest"]
        
        # Check if plugin supports the required API
        plugin_apis = manifest.get("apis", [])
        if api not in plugin_apis:
            continue
            
        # Check if plugin has all required capabilities
        plugin_caps = set(manifest.get("capabilities", []))
        required_caps = set(capabilities)
        if not required_caps.issubset(plugin_caps):
            continue
            
        candidates.append(plugin_info)
        
    return candidates