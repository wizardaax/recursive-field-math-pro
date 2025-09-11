#!/usr/bin/env python3
"""Nine-based sequence generator plugin."""

import json
import sys
import numpy as np
import csv
from pathlib import Path


def generate_nine_sequence(steps: int, niner: bool = True) -> np.ndarray:
    """Generate a nine-based sequence."""
    sequence = []
    for i in range(steps):
        if niner:
            value = (i * 9 + 7) % 100  # Simple nine-based pattern
        else:
            value = (i * 7 + 9) % 100  # Alternative pattern
        sequence.append(value)
    return np.array(sequence)


def generate_audio_wave(sequence: np.ndarray, sample_rate: int = 44100, duration: float = 2.0) -> np.ndarray:
    """Generate audio waveform from sequence."""
    # Create a simple sine wave pattern based on sequence values
    t = np.linspace(0, duration, int(sample_rate * duration))
    wave = np.zeros_like(t)
    
    for i, freq_base in enumerate(sequence):
        freq = 220 + freq_base * 4  # Map to audio frequencies
        phase = (i / len(sequence)) * 2 * np.pi
        amplitude = 0.3 / len(sequence)
        wave += amplitude * np.sin(2 * np.pi * freq * t + phase)
    
    # Normalize
    if np.max(np.abs(wave)) > 0:
        wave = wave / np.max(np.abs(wave)) * 0.8
    
    return wave


def save_wav(wave: np.ndarray, filepath: Path, sample_rate: int = 44100):
    """Save wave as WAV file (simple 16-bit format)."""
    # Convert to 16-bit integers
    wave_int = (wave * 32767).astype(np.int16)
    
    # Write simple WAV file (minimal implementation)
    with open(filepath, 'wb') as f:
        # WAV header
        f.write(b'RIFF')
        f.write((36 + len(wave_int) * 2).to_bytes(4, 'little'))
        f.write(b'WAVE')
        f.write(b'fmt ')
        f.write((16).to_bytes(4, 'little'))
        f.write((1).to_bytes(2, 'little'))  # PCM
        f.write((1).to_bytes(2, 'little'))  # Mono
        f.write(sample_rate.to_bytes(4, 'little'))
        f.write((sample_rate * 2).to_bytes(4, 'little'))
        f.write((2).to_bytes(2, 'little'))
        f.write((16).to_bytes(2, 'little'))
        f.write(b'data')
        f.write((len(wave_int) * 2).to_bytes(4, 'little'))
        
        # Audio data
        for sample in wave_int:
            f.write(int(sample).to_bytes(2, 'little', signed=True))


def main():
    """Main plugin entry point."""
    # Read input from stdin
    input_data = json.load(sys.stdin)
    params = input_data.get("params", {})
    output_dir = Path(input_data.get("output_dir", "."))
    
    # Extract parameters
    steps = params.get("steps", 27)
    niner = params.get("niner", True)
    
    # Generate sequence
    sequence = generate_nine_sequence(steps, niner)
    
    # Generate audio
    wave = generate_audio_wave(sequence)
    
    # Save outputs
    output_dir.mkdir(exist_ok=True)
    
    # Save sequence as CSV
    csv_path = output_dir / "sequence.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["step", "value"])
        for i, value in enumerate(sequence):
            writer.writerow([i, value])
    
    # Save audio as WAV
    wav_path = output_dir / "sequence.wav"
    save_wav(wave, wav_path)
    
    # Calculate simple metrics
    metrics = {
        "sequence_length": len(sequence),
        "sequence_mean": float(np.mean(sequence)),
        "sequence_std": float(np.std(sequence)),
        "audio_duration_s": len(wave) / 44100,
        "audio_peak": float(np.max(np.abs(wave)))
    }
    
    # Return result
    result = {
        "status": "success",
        "artifacts": {
            "sequence.csv": str(csv_path),
            "sequence.wav": str(wav_path)
        },
        "metrics": metrics
    }
    
    print(json.dumps(result))


if __name__ == "__main__":
    main()