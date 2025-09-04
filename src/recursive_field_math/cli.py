import argparse
import json
import os
import sys
from .field import r_theta
from .lucas import L
from .fibonacci import F
from .ratios import ratio
from .ratios import ratio_error_bounds
from .continued_fraction import lucas_ratio_cfrac
from .egyptian_fraction import egypt_4_7_11
from .signatures import signature_summary


def main():
    p = argparse.ArgumentParser(prog="rfm", description="Recursive Field Math — Projex X1")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("field", help="r, theta for n in [a,b]")
    sp.add_argument("a", type=int)
    sp.add_argument("b", type=int)

    sp = sub.add_parser("lucas", help="Lucas numbers L_n for n in [a,b]")
    sp.add_argument("a", type=int)
    sp.add_argument("b", type=int)

    sp = sub.add_parser("fib", help="Fibonacci F_n for n in [a,b]")
    sp.add_argument("a", type=int)
    sp.add_argument("b", type=int)

    sp = sub.add_parser("ratio", help="L_{n+1}/L_n and error bounds")
    sp.add_argument("n", type=int)

    sub.add_parser("egypt", help="Egyptian fraction 1/4+1/7+1/11")
    sub.add_parser("sig", help="Signature triple summary")
    sub.add_parser("cfrac", help="Continued fraction meta for L_{n+1}/L_n (n>=1)").add_argument("n", type=int)
    
    # Add entropy pump evaluation command
    sp = sub.add_parser("eval", help="Evaluate entropy pump results against acceptance rules")
    sp.add_argument("results_file", help="Path to entropy pump results JSON file")
    sp.add_argument("--lucas-weights", nargs=3, type=int, default=[4, 7, 11],
                   help="Lucas weights (default: 4 7 11)")
    sp.add_argument("--markdown", action="store_true", 
                   help="Output as markdown (default: JSON)")
    
    # Add entropy pump harness with flame correction
    sp = sub.add_parser("entropy-pump", help="Run Codex entropy-pump harness on demo PGNs")
    sp.add_argument("--enable-flame-correction", action="store_true",
                   help="Enable Regen88 Codex Flame Correction Engine")
    sp.add_argument("--flame-threshold", type=float, default=2.5,
                   help="Flame detection threshold (std devs, default: 2.5)")
    sp.add_argument("--regen-factor", type=float, default=88.0,
                   help="Regen88 smoothing factor (default: 88.0)")
    sp.add_argument("--regen-iterations", type=int, default=3,
                   help="Number of Regen88 iterations (default: 3)")
    sp.add_argument("--output-dir", default="out", 
                   help="Output directory for results (default: out)")
    sp.add_argument("--quiet", action="store_true",
                   help="Suppress detailed output")

    args = p.parse_args()
    if args.cmd == "field":
        a, b = args.a, args.b
        out = {n: r_theta(n) for n in range(a, b+1)}
    elif args.cmd == "lucas":
        a, b = args.a, args.b
        out = {n: L(n) for n in range(a, b+1)}
    elif args.cmd == "fib":
        a, b = args.a, args.b
        out = {n: F(n) for n in range(a, b+1)}
    elif args.cmd == "ratio":
        n = args.n
        r = ratio(n)
        lo, hi = ratio_error_bounds(n)
        out = {"n": n, "ratio": r, "abs_error_bounds": [lo, hi]}
    elif args.cmd == "egypt":
        num, den = egypt_4_7_11()
        out = {"sum_1_4_7_11": {"num": num, "den": den}}
    elif args.cmd == "sig":
        out = signature_summary()
    elif args.cmd == "cfrac":
        n = args.n
        num, den, meta = lucas_ratio_cfrac(n)
        out = {"n": n, "ratio": [num, den], "cfrac_meta": meta}
    elif args.cmd == "eval":
        # Import here to avoid circular imports
        try:
            # Try to import from scripts package
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            sys.path.insert(0, project_root)
            from scripts.results_evaluator import evaluate_and_summarize_results
        except ImportError:
            print("Error: Cannot import results evaluator. Make sure scripts/results_evaluator.py exists.")
            sys.exit(1)
        
        lucas_weights = tuple(args.lucas_weights)
        
        if args.markdown:
            # Output markdown summary
            summary = evaluate_and_summarize_results(args.results_file, lucas_weights)
            print(summary)
            return
        else:
            # Output JSON evaluation data
            try:
                with open(args.results_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                
                from scripts.results_evaluator import evaluate_acceptance_rules
                evaluations = []
                for result in results:
                    eval_result = evaluate_acceptance_rules(result)
                    eval_result["tag"] = result.get("tag", "unknown")
                    eval_result["moves"] = result.get("moves", 0)
                    evaluations.append(eval_result)
                
                out = {
                    "lucas_weights": lucas_weights,
                    "evaluations": evaluations,
                    "summary": {
                        "total_games": len(evaluations),
                        "passes": sum(1 for e in evaluations if e["verdict"] == "PASS"),
                        "checks": sum(1 for e in evaluations if e["verdict"] == "CHECK"),
                        "skips": sum(1 for e in evaluations if e["verdict"] == "SKIP")
                    }
                }
            except (FileNotFoundError, json.JSONDecodeError) as e:
                out = {"error": f"Cannot load results file: {e}"}
    elif args.cmd == "entropy-pump":
        # Run entropy pump harness
        try:
            # Import and run harness
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            sys.path.insert(0, project_root)
            
            # Set up arguments for harness
            import argparse as harness_argparse
            harness_args = harness_argparse.Namespace()
            harness_args.enable_flame_correction = args.enable_flame_correction
            harness_args.flame_threshold = args.flame_threshold
            harness_args.regen_factor = args.regen_factor
            harness_args.regen_iterations = args.regen_iterations
            
            # Change to output directory
            original_cwd = os.getcwd()
            os.makedirs(args.output_dir, exist_ok=True)
            
            # Import and run harness with custom arguments
            from scripts.run_entropy_pump_harness import main as harness_main, eval_game, load_demo_pgns
            from datetime import datetime, timezone
            import json
            
            if not args.quiet:
                if args.enable_flame_correction:
                    print(f"🔥 Regen88 Flame Correction Engine enabled:")
                    print(f"   - Flame threshold: {args.flame_threshold} std devs")
                    print(f"   - Regen factor: {args.regen_factor}")
                    print(f"   - Iterations: {args.regen_iterations}")
                    print()
            
            # Run harness logic directly
            mid = (10, 30)
            lucas_weights = (4, 7, 11)
            
            flame_params = None
            if args.enable_flame_correction:
                flame_params = {
                    "flame_threshold": args.flame_threshold,
                    "regen_factor": args.regen_factor,
                    "iterations": args.regen_iterations
                }
            
            rows = []
            for tag, pgn in load_demo_pgns():
                r = eval_game(pgn, mid=mid, tag=tag, 
                             enable_flame_correction=args.enable_flame_correction,
                             flame_params=flame_params)
                if r: rows.append(r)
            
            # Write summary JSON
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            suffix = "_flame" if args.enable_flame_correction else ""
            js = os.path.join(args.output_dir, f"entropy_pump_summary_{ts}{suffix}.json")
            with open(js, "w", encoding="utf-8") as f:
                f.write(json.dumps(rows, indent=2))
            
            # Generate summary
            from scripts.results_evaluator import generate_summary_comment
            summary = generate_summary_comment(rows, lucas_weights)
            
            flame_status = " (🔥 Regen88 enabled)" if args.enable_flame_correction else ""
            
            if not args.quiet:
                print(f"Results written to {js}{flame_status}")
                print("\n" + "="*60)
                print(f"RESULTS SUMMARY{flame_status}")
                print("="*60)
                print(summary)
            
            out = {
                "status": "success",
                "results_file": js,
                "flame_correction_enabled": args.enable_flame_correction,
                "games_processed": len(rows),
                "summary": summary
            }
            
        except Exception as e:
            out = {"error": f"Failed to run entropy pump harness: {e}"}
    else:
        out = {"error": "unknown command"}

    if args.cmd not in ["eval", "entropy-pump"] or (args.cmd == "eval" and not args.markdown):
        print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
