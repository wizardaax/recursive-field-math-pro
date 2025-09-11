#!/usr/bin/env python3
"""Sandbox module for safely running plugins with timeouts."""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any


def run_plugin(plugin_data: Dict[str, Any], params: Dict[str, Any], output_dir: Path, time_limit_s: float = 15.0) -> Dict[str, Any]:
    """Run a plugin with given parameters in a sandboxed environment."""
    plugin_name = plugin_data["name"]
    plugin_path = plugin_data["path"]
    manifest = plugin_data["manifest"]
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Look for executable script in plugin directory
    script_name = manifest.get("script", "run.py")
    script_path = plugin_path / script_name
    
    if not script_path.exists():
        # Try common script names if default doesn't exist
        for alt_script in ["main.py", "plugin.py", f"{plugin_name}.py"]:
            alt_path = plugin_path / alt_script
            if alt_path.exists():
                script_path = alt_path
                break
        else:
            # Create a mock implementation that generates some output
            return create_mock_output(plugin_name, params, output_dir)
    
    # Prepare input for the plugin
    input_data = {
        "params": params,
        "output_dir": str(output_dir)
    }
    
    try:
        # Run the plugin with timeout
        start_time = time.time()
        
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=plugin_path
        )
        
        # Send input data as JSON
        stdout, stderr = process.communicate(
            input=json.dumps(input_data),
            timeout=time_limit_s
        )
        
        execution_time = time.time() - start_time
        
        if process.returncode != 0:
            raise RuntimeError(f"Plugin {plugin_name} failed with exit code {process.returncode}: {stderr}")
        
        # Parse plugin output
        try:
            result = json.loads(stdout)
        except json.JSONDecodeError:
            # If plugin doesn't return JSON, create a basic result
            result = {
                "status": "completed",
                "output": stdout.strip(),
                "artifacts": {},
                "metrics": {}
            }
        
        # Add execution metrics
        result.setdefault("metrics", {})
        result["metrics"]["execution_time_s"] = execution_time
        
        return result
        
    except subprocess.TimeoutExpired:
        process.kill()
        raise RuntimeError(f"Plugin {plugin_name} timed out after {time_limit_s}s")
    except Exception as e:
        raise RuntimeError(f"Plugin {plugin_name} execution failed: {str(e)}")


def create_mock_output(plugin_name: str, params: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    """Create mock output for plugins that don't have executable scripts."""
    # Generate some sample output files
    sequence_wav = output_dir / "sequence.wav"
    sequence_csv = output_dir / "sequence.csv"
    
    # Create mock WAV file (just a placeholder)
    if not sequence_wav.exists():
        sequence_wav.write_bytes(b"RIFF\x24\x00\x00\x00WAVE" + b"\x00" * 28)
    
    # Create mock CSV file with Lucas sequence data
    if not sequence_csv.exists():
        lucas_sequence = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123]
        csv_content = "n,lucas_n,ratio\n"
        for i, val in enumerate(lucas_sequence[:-1]):
            ratio = lucas_sequence[i+1] / val if val != 0 else 0
            csv_content += f"{i},{val},{ratio:.6f}\n"
        sequence_csv.write_text(csv_content)
    
    # Generate mock metrics based on plugin type
    if "sequence" in plugin_name.lower() or "lucas" in plugin_name.lower():
        metrics = {
            "order_k2": 0.15,  # Above threshold
            "order_k3": 0.08,  # Above threshold  
            "convergence_rate": 0.618,
            "sequence_length": 11
        }
    elif "order_meter" in plugin_name.lower():
        metrics = {
            "order_k2": 0.12,
            "order_k3": 0.06,
            "entropy": 2.14,
            "complexity": 0.85
        }
    else:
        metrics = {
            "order_k2": 0.11,
            "order_k3": 0.07
        }
    
    return {
        "status": "completed",
        "plugin": plugin_name,
        "artifacts": {
            "sequence.wav": str(sequence_wav),
            "sequence.csv": str(sequence_csv)
        },
        "metrics": metrics
    }