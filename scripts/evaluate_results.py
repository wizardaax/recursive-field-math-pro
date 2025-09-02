#!/usr/bin/env python3
"""
CLI tool to evaluate Codex entropy-pump results.
"""
import argparse
import sys
import os

# Add the project root to path to import scripts module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from scripts.results_evaluator import evaluate_and_summarize_results
except ImportError:
    # If running from scripts directory
    from results_evaluator import evaluate_and_summarize_results


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate Codex entropy-pump results against acceptance rules"
    )
    parser.add_argument(
        "results_file", 
        help="Path to entropy pump results JSON file"
    )
    parser.add_argument(
        "--lucas-weights", 
        nargs=3, 
        type=int, 
        default=[4, 7, 11],
        help="Lucas weights tuple (default: 4 7 11)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file for summary (default: print to stdout)"
    )
    
    args = parser.parse_args()
    
    # Generate summary
    lucas_weights = tuple(args.lucas_weights)
    summary = evaluate_and_summarize_results(args.results_file, lucas_weights)
    
    # Output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary written to {args.output}")
    else:
        print(summary)


if __name__ == "__main__":
    main()