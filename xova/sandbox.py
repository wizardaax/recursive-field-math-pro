#!/usr/bin/env python3
"""Plugin execution sandbox for Xova evolution system."""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any


def run_plugin(plugin_info: Dict[str, Any], 
               params: Dict[str, Any], 
               output_dir: Path,
               time_limit_s: float = 15.0) -> Dict[str, Any]:
    """Run a plugin in a sandboxed environment.
    
    Args:
        plugin_info: Plugin information from registry
        params: Parameters to pass to plugin
        output_dir: Directory for plugin output
        time_limit_s: Maximum execution time in seconds
        
    Returns:
        Plugin execution result dictionary
    """
    plugin_path = plugin_info["path"]
    manifest = plugin_info["manifest"]
    
    # Find the main script
    main_script = plugin_path / manifest.get("main", "main.py")
    if not main_script.exists():
        raise FileNotFoundError(f"Plugin main script not found: {main_script}")
    
    # Prepare input for plugin
    input_data = {
        "params": params,
        "output_dir": str(output_dir),
        "manifest": manifest
    }
    
    # Run plugin as subprocess
    try:
        process = subprocess.Popen(
            [sys.executable, str(main_script)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(plugin_path)
        )
        
        start_time = time.time()
        input_json = json.dumps(input_data)
        
        try:
            stdout, stderr = process.communicate(input=input_json, timeout=time_limit_s)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            raise TimeoutError(f"Plugin exceeded time limit of {time_limit_s}s")
        
        execution_time = time.time() - start_time
        
        if process.returncode != 0:
            raise RuntimeError(f"Plugin failed with code {process.returncode}: {stderr}")
        
        # Parse plugin output
        try:
            result = json.loads(stdout)
        except json.JSONDecodeError:
            result = {"output": stdout, "stderr": stderr}
        
        # Add execution metadata
        result.setdefault("metadata", {}).update({
            "execution_time_s": execution_time,
            "plugin_name": plugin_info["name"],
            "plugin_version": manifest.get("version", "unknown")
        })
        
        return result
        
    except (OSError, subprocess.SubprocessError) as e:
        raise RuntimeError(f"Failed to execute plugin: {e}")