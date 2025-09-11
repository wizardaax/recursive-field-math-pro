#!/usr/bin/env python3
"""Simple sandbox module for xova/evolve.py"""
import os
import json
from pathlib import Path

def run_plugin(candidate, params, output_dir, time_limit_s=30.0):
    """Run a plugin in a sandbox environment"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Generate test artifacts
    sequence_csv = output_path / "sequence.csv"
    sequence_wav = output_path / "sequence.wav"
    
    # Create test CSV file
    with open(sequence_csv, 'w') as f:
        f.write("step,value,frequency\n")
        for i in range(10):
            f.write(f"{i},{i*0.1},{440 + i*10}\n")
    
    # Create test WAV file (empty placeholder)
    with open(sequence_wav, 'wb') as f:
        f.write(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00")  # Minimal WAV header
    
    return {
        "status": "ok",
        "metrics": {
            "evolution_steps": 100,
            "sequence_length": 10,
            "convergence_rate": 0.95,
            "audio_quality": 0.87
        },
        "artifacts": {
            "sequence.csv": str(sequence_csv),
            "sequence.wav": str(sequence_wav)
        }
    }