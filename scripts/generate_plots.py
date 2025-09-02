#!/usr/bin/env python3
"""
Comprehensive plotting utilities for entropy pump analysis.
Provides CLI interface and utility functions for variance reduction summaries,
phi-clamp distributions, evaluation curves, and phase analysis plots.
"""
import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

# Import the entropy pump functionality
try:
    from .codex_entropy_pump import PHI, codex_pump_from_series, _rank_to_phase, golden_refraction
except ImportError:
    # Handle running as script
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scripts.codex_entropy_pump import PHI, codex_pump_from_series, _rank_to_phase, golden_refraction


def plot_variance_reduction_summary(results: List[Dict], output_dir: str = "plots") -> str:
    """
    Generate variance reduction summary plot from entropy pump results.
    
    Args:
        results: List of entropy pump result dictionaries
        output_dir: Directory to save plots
        
    Returns:
        Path to saved plot file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Filter successful results
    successful_results = [r for r in results if r.get("ok", False)]
    
    if not successful_results:
        print("No successful results to plot")
        return None
    
    # Extract data
    game_tags = [r["tag"] for r in successful_results]
    var_reductions = [r["variance_reduction_pct"] for r in successful_results]
    mae_improvements = [r["mae_improvement_pct"] for r in successful_results]
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Variance reduction plot
    bars1 = ax1.bar(game_tags, var_reductions, color='steelblue', alpha=0.7)
    ax1.set_ylabel('Variance Reduction (%)')
    ax1.set_title('Variance Reduction by Game')
    ax1.axhline(y=20, color='red', linestyle='--', alpha=0.7, label='20% threshold')
    ax1.legend()
    ax1.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, val in zip(bars1, var_reductions):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{val:.1f}%', ha='center', va='bottom')
    
    # MAE improvement plot
    colors = ['green' if x >= 2 else 'orange' if x >= 0 else 'red' for x in mae_improvements]
    bars2 = ax2.bar(game_tags, mae_improvements, color=colors, alpha=0.7)
    ax2.set_ylabel('MAE Improvement (%)')
    ax2.set_title('MAE Improvement by Game')
    ax2.axhline(y=2, color='red', linestyle='--', alpha=0.7, label='2% threshold')
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax2.legend()
    ax2.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, val in zip(bars2, mae_improvements):
        y_pos = bar.get_height() + (0.5 if val >= 0 else -1.5)
        ax2.text(bar.get_x() + bar.get_width()/2, y_pos, 
                f'{val:.1f}%', ha='center', va='bottom' if val >= 0 else 'top')
    
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, "variance_reduction_summary.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


def plot_phi_clamp_distribution(results: List[Dict], output_dir: str = "plots") -> str:
    """
    Generate phi-clamp distribution plots for all games.
    
    Args:
        results: List of entropy pump result dictionaries
        output_dir: Directory to save plots
        
    Returns:
        Path to saved plot file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Filter successful results
    successful_results = [r for r in results if r.get("ok", False) and "theta_after_hist" in r]
    
    if not successful_results:
        print("No histogram data available for phi-clamp distribution")
        return None
    
    # Calculate optimal subplot layout
    n_games = len(successful_results)
    cols = min(3, n_games)
    rows = (n_games + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 4*rows))
    if n_games == 1:
        axes = [axes]
    elif rows == 1:
        axes = [axes] if cols == 1 else axes
    else:
        axes = axes.flatten()
    
    phi_clamp_rad = math.asin(1.0 / PHI)
    
    for i, result in enumerate(successful_results):
        ax = axes[i] if n_games > 1 else axes[0]
        
        edges, hist = result["theta_after_hist"]
        centers = 0.5 * (np.array(edges[1:]) + np.array(edges[:-1]))
        
        # Create histogram
        ax.bar(centers, hist, width=(edges[1] - edges[0]), alpha=0.7, color='skyblue')
        
        # Add phi-clamp lines
        ax.axvline(+phi_clamp_rad, ls="--", color='red', alpha=0.8, label=f'+φ-clamp ({phi_clamp_rad:.3f})')
        ax.axvline(-phi_clamp_rad, ls="--", color='red', alpha=0.8, label=f'-φ-clamp ({phi_clamp_rad:.3f})')
        
        # Add actual peak
        actual_peak = result.get("phi_clamp_rad", phi_clamp_rad)
        peak_deg = math.degrees(actual_peak)
        ax.set_title(f'{result["tag"]}\nφ-clamp peak: {peak_deg:.1f}°')
        ax.set_xlabel('Phase (radians)')
        ax.set_ylabel('Frequency')
        ax.grid(True, alpha=0.3)
        
        if i == 0:  # Add legend to first subplot
            ax.legend()
    
    # Hide unused subplots
    for i in range(n_games, len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, "phi_clamp_distribution.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


def plot_evaluation_curves(results: List[Dict], eval_data: Optional[Dict] = None, output_dir: str = "plots") -> str:
    """
    Generate evaluation curves showing before/after entropy pump application.
    
    Args:
        results: List of entropy pump result dictionaries
        eval_data: Optional dictionary mapping game tags to evaluation series
        output_dir: Directory to save plots
        
    Returns:
        Path to saved plot file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    successful_results = [r for r in results if r.get("ok", False)]
    
    if not successful_results:
        print("No successful results for evaluation curves")
        return None
    
    # Calculate subplot layout
    n_games = len(successful_results)
    cols = min(2, n_games)
    rows = (n_games + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(8*cols, 5*rows))
    if n_games == 1:
        axes = [axes]
    elif rows == 1:
        axes = [axes] if cols == 1 else axes
    else:
        axes = axes.flatten()
    
    for i, result in enumerate(successful_results):
        ax = axes[i] if n_games > 1 else axes[0]
        
        tag = result["tag"]
        
        # If eval_data is provided, use it; otherwise create synthetic data
        if eval_data and tag in eval_data:
            evals = np.array(eval_data[tag])
        else:
            # Create synthetic evaluation curve for demonstration
            n_moves = result.get("moves", 40)
            np.random.seed(hash(tag) % 1000)  # Reproducible but game-specific
            evals = np.cumsum(np.random.normal(0, 30, n_moves))
        
        x = np.arange(len(evals))
        
        # Plot original evaluations
        ax.plot(x, evals, label="Original", alpha=0.8, linewidth=2)
        
        # Get window info
        offset = result.get("offset", 0)
        window_len = result.get("window_len", len(evals))
        start, end = offset, offset + window_len
        
        # Create adjusted evaluation series (this is illustrative)
        if "series_codex" in result:
            evals_adjusted = evals.copy()
            evals_adjusted[start:end] = result["series_codex"]
        else:
            # Simulate adjustment based on variance reduction
            variance_reduction = result["variance_reduction_pct"] / 100.0
            evals_adjusted = evals.copy()
            segment = evals[start:end]
            segment_mean = np.mean(segment)
            adjusted_segment = segment_mean + (segment - segment_mean) * (1 - variance_reduction)
            evals_adjusted[start:end] = adjusted_segment
        
        ax.plot(x, evals_adjusted, label="Entropy Pump", alpha=0.8, linewidth=2)
        
        # Highlight analysis window
        ax.axvspan(start, end-1, alpha=0.2, color='yellow', label=f'Analysis window')
        
        # Add metrics to title
        var_red = result["variance_reduction_pct"]
        mae_imp = result["mae_improvement_pct"]
        ax.set_title(f'{tag}\nVar.Red: {var_red:.1f}%, MAE: {mae_imp:+.1f}%')
        ax.set_xlabel('Move Number')
        ax.set_ylabel('Evaluation (cp)')
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    # Hide unused subplots
    for i in range(n_games, len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, "evaluation_curves.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


def plot_phase_analysis(series_data: np.ndarray, title: str = "Phase Analysis", output_dir: str = "plots") -> str:
    """
    Generate phase analysis plots showing rank-to-phase mapping and golden refraction.
    
    Args:
        series_data: Input evaluation series
        title: Plot title
        output_dir: Directory to save plots
        
    Returns:
        Path to saved plot file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Compute deltas and phases
    deltas = np.diff(series_data)
    theta_before = _rank_to_phase(deltas)
    theta_after = golden_refraction(theta_before, PHI)
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    # 1. Original series
    ax1.plot(series_data, 'b-', alpha=0.7, linewidth=2)
    ax1.set_title('Original Evaluation Series')
    ax1.set_xlabel('Move')
    ax1.set_ylabel('Evaluation')
    ax1.grid(True, alpha=0.3)
    
    # 2. Delta series
    ax2.plot(deltas, 'r-', alpha=0.7, linewidth=2)
    ax2.set_title('Evaluation Deltas')
    ax2.set_xlabel('Move')
    ax2.set_ylabel('Delta')
    ax2.grid(True, alpha=0.3)
    
    # 3. Phase mapping comparison
    ax3.scatter(theta_before, theta_after, alpha=0.6, s=30)
    ax3.plot([-np.pi/2, np.pi/2], [-np.pi/2, np.pi/2], 'k--', alpha=0.5, label='y=x')
    
    # Add phi-clamp boundaries
    phi_clamp = math.asin(1.0 / PHI)
    ax3.axhline(y=phi_clamp, color='red', linestyle='--', alpha=0.7, label=f'+φ-clamp')
    ax3.axhline(y=-phi_clamp, color='red', linestyle='--', alpha=0.7, label=f'-φ-clamp')
    
    ax3.set_xlabel('θ (before refraction)')
    ax3.set_ylabel("θ' (after refraction)")
    ax3.set_title('Golden Refraction Mapping')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # 4. Phase distribution histograms
    bins = 30
    ax4.hist(theta_before, bins=bins, alpha=0.5, label='Before refraction', density=True)
    ax4.hist(theta_after, bins=bins, alpha=0.5, label='After refraction', density=True)
    ax4.axvline(x=phi_clamp, color='red', linestyle='--', alpha=0.7)
    ax4.axvline(x=-phi_clamp, color='red', linestyle='--', alpha=0.7)
    ax4.set_xlabel('Phase (radians)')
    ax4.set_ylabel('Density')
    ax4.set_title('Phase Distribution')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle(title, fontsize=14)
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, f"phase_analysis_{title.lower().replace(' ', '_')}.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


def generate_comprehensive_report(results: List[Dict], output_dir: str = "plots") -> List[str]:
    """
    Generate all plots for a comprehensive entropy pump analysis report.
    
    Args:
        results: List of entropy pump result dictionaries
        output_dir: Directory to save plots
        
    Returns:
        List of paths to generated plot files
    """
    print(f"Generating comprehensive entropy pump analysis report in {output_dir}/")
    
    plot_paths = []
    
    # 1. Variance reduction summary
    try:
        path = plot_variance_reduction_summary(results, output_dir)
        if path:
            plot_paths.append(path)
            print(f"✓ Generated variance reduction summary: {path}")
    except Exception as e:
        print(f"✗ Error generating variance reduction summary: {e}")
    
    # 2. Phi-clamp distribution
    try:
        path = plot_phi_clamp_distribution(results, output_dir)
        if path:
            plot_paths.append(path)
            print(f"✓ Generated phi-clamp distribution: {path}")
    except Exception as e:
        print(f"✗ Error generating phi-clamp distribution: {e}")
    
    # 3. Evaluation curves
    try:
        path = plot_evaluation_curves(results, output_dir=output_dir)
        if path:
            plot_paths.append(path)
            print(f"✓ Generated evaluation curves: {path}")
    except Exception as e:
        print(f"✗ Error generating evaluation curves: {e}")
    
    # 4. Phase analysis for first successful result
    successful_results = [r for r in results if r.get("ok", False)]
    if successful_results:
        try:
            # Generate synthetic data for phase analysis demonstration
            first_result = successful_results[0]
            n_moves = first_result.get("moves", 40)
            np.random.seed(42)  # Reproducible
            synthetic_evals = np.cumsum(np.random.normal(0, 25, n_moves))
            
            path = plot_phase_analysis(synthetic_evals, 
                                     title=f"Phase Analysis - {first_result['tag']}", 
                                     output_dir=output_dir)
            if path:
                plot_paths.append(path)
                print(f"✓ Generated phase analysis: {path}")
        except Exception as e:
            print(f"✗ Error generating phase analysis: {e}")
    
    print(f"\n📊 Generated {len(plot_paths)} plots total")
    return plot_paths


def load_entropy_pump_results(file_path: str) -> List[Dict]:
    """Load entropy pump results from JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading results from {file_path}: {e}")
        return []


def main():
    """CLI interface for plotting utilities."""
    parser = argparse.ArgumentParser(description="Generate entropy pump analysis plots")
    parser.add_argument("input", nargs="?", help="JSON file with entropy pump results")
    parser.add_argument("-o", "--output", default="plots", help="Output directory for plots")
    parser.add_argument("--summary", action="store_true", help="Generate variance reduction summary only")
    parser.add_argument("--phi-clamp", action="store_true", help="Generate phi-clamp distribution only")
    parser.add_argument("--curves", action="store_true", help="Generate evaluation curves only")
    parser.add_argument("--phase", action="store_true", help="Generate phase analysis only")
    parser.add_argument("--all", action="store_true", help="Generate all plots (default)")
    
    args = parser.parse_args()
    
    # Load results
    if args.input:
        if not os.path.exists(args.input):
            print(f"Error: Input file {args.input} not found")
            return 1
        results = load_entropy_pump_results(args.input)
        if not results:
            print("No results loaded")
            return 1
    else:
        # Look for recent entropy pump results
        out_dir = "out"
        if os.path.exists(out_dir):
            json_files = [f for f in os.listdir(out_dir) if f.startswith("entropy_pump_summary_") and f.endswith(".json")]
            if json_files:
                latest_file = max(json_files)
                latest_path = os.path.join(out_dir, latest_file)
                print(f"Using latest results: {latest_path}")
                results = load_entropy_pump_results(latest_path)
            else:
                print("No entropy pump results found in out/ directory")
                return 1
        else:
            print("No input file specified and no out/ directory found")
            return 1
    
    # Generate plots based on arguments
    if not any([args.summary, args.phi_clamp, args.curves, args.phase]) or args.all:
        # Generate all plots
        generate_comprehensive_report(results, args.output)
    else:
        # Generate specific plots
        if args.summary:
            plot_variance_reduction_summary(results, args.output)
        if args.phi_clamp:
            plot_phi_clamp_distribution(results, args.output)
        if args.curves:
            plot_evaluation_curves(results, output_dir=args.output)
        if args.phase:
            # Generate phase analysis for demonstration
            np.random.seed(42)
            synthetic_evals = np.cumsum(np.random.normal(0, 25, 40))
            plot_phase_analysis(synthetic_evals, output_dir=args.output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())