"""
Standalone plotting utilities for Codex entropy-pump results.
Generate visualizations from JSON result files or raw data.
"""
import os
import json
import math
import argparse
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Tuple


def load_results_from_json(json_path: str) -> List[Dict[str, Any]]:
    """Load entropy pump results from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        results = json.load(f)
    if not isinstance(results, list):
        raise ValueError(f"Expected list of results, got {type(results)}")
    return results


def plot_variance_reduction_summary(results: List[Dict[str, Any]], 
                                  output_path: Optional[str] = None) -> None:
    """Create summary bar chart of variance reduction across all games."""
    valid_results = [r for r in results if r.get("ok", False)]
    if not valid_results:
        print("No valid results to plot")
        return
    
    tags = [r["tag"] for r in valid_results]
    variance_reductions = [r["variance_reduction_pct"] for r in valid_results]
    mae_improvements = [r["mae_improvement_pct"] for r in valid_results]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Variance reduction plot
    bars1 = ax1.bar(tags, variance_reductions, color='steelblue', alpha=0.8)
    ax1.axhline(20.0, color='red', linestyle='--', alpha=0.7, label='Acceptance threshold (20%)')
    ax1.set_ylabel('Variance Reduction (%)')
    ax1.set_title('Codex Entropy-Pump: Variance Reduction by Game')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, val in zip(bars1, variance_reductions):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # MAE improvement plot
    bars2 = ax2.bar(tags, mae_improvements, color='orange', alpha=0.8)
    ax2.axhline(2.0, color='red', linestyle='--', alpha=0.7, label='Acceptance threshold (2%)')
    ax2.axhline(0.0, color='gray', linestyle='-', alpha=0.5)
    ax2.set_ylabel('MAE Improvement (%)')
    ax2.set_xlabel('Game')
    ax2.set_title('Codex Entropy-Pump: MAE Improvement by Game')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, val in zip(bars2, mae_improvements):
        height = bar.get_height()
        y_pos = height + 0.5 if height >= 0 else height - 1
        ax2.text(bar.get_x() + bar.get_width()/2, y_pos, 
                f'{val:.1f}%', ha='center', va='bottom' if height >= 0 else 'top', 
                fontweight='bold')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved variance reduction summary to {output_path}")
    else:
        plt.show()
    plt.close()


def plot_phi_clamp_distribution(results: List[Dict[str, Any]], 
                               output_path: Optional[str] = None) -> None:
    """Create combined φ-clamp distribution plot for all games."""
    valid_results = [r for r in results if r.get("ok", False)]
    if not valid_results:
        print("No valid results to plot")
        return
    
    phi_clamp_target = 38.2  # degrees
    tolerance = 2.0  # degrees
    
    fig, axes = plt.subplots(len(valid_results), 1, figsize=(10, 3 * len(valid_results)))
    if len(valid_results) == 1:
        axes = [axes]
    
    for i, result in enumerate(valid_results):
        ax = axes[i]
        
        # Extract histogram data
        edges, hist = result["theta_after_hist"]
        centers = np.array([(edges[j] + edges[j+1]) / 2 for j in range(len(edges)-1)])
        centers_deg = np.degrees(np.abs(centers))  # Convert to degrees and take absolute value
        
        # Plot histogram
        ax.bar(centers_deg, hist, width=np.degrees(edges[1] - edges[0]), 
               alpha=0.7, color='skyblue', edgecolor='navy')
        
        # Mark φ-clamp target and tolerance
        ax.axvline(phi_clamp_target, color='red', linestyle='--', linewidth=2, 
                  label=f'φ-clamp target ({phi_clamp_target}°)')
        ax.axvspan(phi_clamp_target - tolerance, phi_clamp_target + tolerance, 
                  alpha=0.2, color='red', label=f'±{tolerance}° tolerance')
        
        # Find actual peak
        if hist:
            peak_idx = np.argmax(hist)
            peak_deg = centers_deg[peak_idx]
            ax.axvline(peak_deg, color='green', linestyle='-', linewidth=2, 
                      label=f'Actual peak ({peak_deg:.1f}°)')
        
        ax.set_title(f'{result["tag"]}: φ-Clamp Distribution')
        ax.set_xlabel('|θ′| (degrees)')
        ax.set_ylabel('Frequency')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 90)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved φ-clamp distribution to {output_path}")
    else:
        plt.show()
    plt.close()


def plot_evaluation_curves(results: List[Dict[str, Any]], 
                          output_path: Optional[str] = None) -> None:
    """Create evaluation curve plots showing before/after entropy pump."""
    valid_results = [r for r in results if r.get("ok", False)]
    if not valid_results:
        print("No valid results to plot")
        return
    
    fig, axes = plt.subplots(len(valid_results), 1, figsize=(12, 4 * len(valid_results)))
    if len(valid_results) == 1:
        axes = [axes]
    
    for i, result in enumerate(valid_results):
        ax = axes[i]
        
        # Get full evaluation series (reconstruct from raw + codex data)
        offset = result["offset"]
        window_len = result["window_len"]
        
        # Create x-axis for moves
        total_moves = result["moves"]
        x = np.arange(total_moves)
        
        # Create full evaluation series (assuming stock eval outside window)
        # This is simplified - in real case you'd need the full original series
        series_raw = result["series_raw"]
        series_codex = result["series_codex"]
        
        # Plot the windowed data we have
        x_window = np.arange(offset, offset + window_len)
        
        ax.plot(x_window, series_raw, 'o-', label='Original (stock eval)', 
               color='blue', alpha=0.8, linewidth=2)
        ax.plot(x_window, series_codex, 's-', label='Codex adjusted', 
               color='red', alpha=0.8, linewidth=2)
        
        # Highlight the analysis window
        ax.axvspan(offset, offset + window_len - 1, alpha=0.1, color='gray', 
                  label=f'Analysis window ({offset}-{offset + window_len - 1})')
        
        # Add metrics to title
        var_reduction = result["variance_reduction_pct"]
        mae_improvement = result["mae_improvement_pct"]
        title = (f'{result["tag"]}: Variance ↓{var_reduction:.1f}%, '
                f'MAE {"↑" if mae_improvement >= 0 else "↓"}{abs(mae_improvement):.1f}%')
        
        ax.set_title(title)
        ax.set_xlabel('Move Number')
        ax.set_ylabel('Evaluation (centipawns)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved evaluation curves to {output_path}")
    else:
        plt.show()
    plt.close()


def plot_theta_phase_analysis(results: List[Dict[str, Any]], 
                             output_path: Optional[str] = None) -> None:
    """Create phase analysis plots showing θ → θ′ transformation."""
    valid_results = [r for r in results if r.get("ok", False)]
    if not valid_results:
        print("No valid results to plot")
        return
    
    fig, axes = plt.subplots(len(valid_results), 2, figsize=(15, 4 * len(valid_results)))
    if len(valid_results) == 1:
        axes = axes.reshape(1, -1)
    
    for i, result in enumerate(valid_results):
        ax1, ax2 = axes[i]
        
        # Get phase data
        theta_after = np.array(result["theta_after"])
        
        # Create synthetic θ (before refraction) for demonstration
        # In practice, this would be stored in the results
        phi = (1 + np.sqrt(5)) / 2
        theta_before = np.arcsin(np.sin(theta_after) * phi)
        
        # Phase scatter plot
        ax1.scatter(theta_before, theta_after, alpha=0.7, s=50)
        ax1.plot([-np.pi/2, np.pi/2], [-np.pi/2, np.pi/2], 'r--', alpha=0.5, label='y=x')
        ax1.set_xlabel('θ (original phase)')
        ax1.set_ylabel('θ′ (refracted phase)')
        ax1.set_title(f'{result["tag"]}: Phase Refraction θ → θ′')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_xlim(-np.pi/2, np.pi/2)
        ax1.set_ylim(-np.pi/2, np.pi/2)
        
        # Compression visualization
        var_before = np.var(theta_before)
        var_after = np.var(theta_after)
        compression = result["compression"]
        
        ax2.hist(theta_before, bins=20, alpha=0.5, label=f'Before (σ²={var_before:.3f})', 
                density=True, color='blue')
        ax2.hist(theta_after, bins=20, alpha=0.5, label=f'After (σ²={var_after:.3f})', 
                density=True, color='red')
        ax2.set_xlabel('Phase (radians)')
        ax2.set_ylabel('Density')
        ax2.set_title(f'{result["tag"]}: Phase Compression ({compression:.1%})')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved phase analysis to {output_path}")
    else:
        plt.show()
    plt.close()


def create_comprehensive_report(results: List[Dict[str, Any]], 
                               output_dir: str = "plots") -> None:
    """Generate a comprehensive set of plots for entropy pump analysis."""
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Generating comprehensive entropy pump plots in {output_dir}/...")
    
    # Generate all plot types
    plot_variance_reduction_summary(results, 
                                  os.path.join(output_dir, "variance_reduction_summary.png"))
    
    plot_phi_clamp_distribution(results, 
                               os.path.join(output_dir, "phi_clamp_distribution.png"))
    
    plot_evaluation_curves(results, 
                          os.path.join(output_dir, "evaluation_curves.png"))
    
    plot_theta_phase_analysis(results, 
                             os.path.join(output_dir, "phase_analysis.png"))
    
    print(f"All plots generated successfully in {output_dir}/")


def main():
    """Command-line interface for generating entropy pump plots."""
    parser = argparse.ArgumentParser(
        description="Generate plots from Codex entropy-pump results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m scripts.generate_plots out/entropy_pump_summary_*.json
  python -m scripts.generate_plots results.json --plot-type variance
  python -m scripts.generate_plots results.json --output-dir my_plots
        """)
    
    parser.add_argument("json_file", help="Path to entropy pump results JSON file")
    parser.add_argument("--plot-type", 
                       choices=["all", "variance", "phi-clamp", "curves", "phase"],
                       default="all",
                       help="Type of plot to generate (default: all)")
    parser.add_argument("--output-dir", default="plots",
                       help="Output directory for plots (default: plots)")
    parser.add_argument("--show", action="store_true",
                       help="Show plots interactively instead of saving")
    
    args = parser.parse_args()
    
    # Load results
    try:
        results = load_results_from_json(args.json_file)
        print(f"Loaded {len(results)} results from {args.json_file}")
    except Exception as e:
        print(f"Error loading results: {e}")
        return 1
    
    # Generate plots based on type
    output_path = None if args.show else args.output_dir
    
    if args.plot_type == "all":
        if args.show:
            print("Showing all plots interactively...")
            plot_variance_reduction_summary(results)
            plot_phi_clamp_distribution(results)
            plot_evaluation_curves(results)
            plot_theta_phase_analysis(results)
        else:
            create_comprehensive_report(results, args.output_dir)
    
    elif args.plot_type == "variance":
        if not args.show:
            os.makedirs(args.output_dir, exist_ok=True)
        plot_variance_reduction_summary(results, 
            None if args.show else os.path.join(args.output_dir, "variance_reduction.png"))
    
    elif args.plot_type == "phi-clamp":
        if not args.show:
            os.makedirs(args.output_dir, exist_ok=True)
        plot_phi_clamp_distribution(results,
            None if args.show else os.path.join(args.output_dir, "phi_clamp.png"))
    
    elif args.plot_type == "curves":
        if not args.show:
            os.makedirs(args.output_dir, exist_ok=True)
        plot_evaluation_curves(results,
            None if args.show else os.path.join(args.output_dir, "evaluation_curves.png"))
    
    elif args.plot_type == "phase":
        if not args.show:
            os.makedirs(args.output_dir, exist_ok=True)
        plot_theta_phase_analysis(results,
            None if args.show else os.path.join(args.output_dir, "phase_analysis.png"))
    
    return 0


if __name__ == "__main__":
    exit(main())