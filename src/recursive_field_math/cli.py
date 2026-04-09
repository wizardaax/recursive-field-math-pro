import argparse
import contextlib
import json
import os
import sys
from typing import Any

from .continued_fraction import lucas_ratio_cfrac
from .egyptian_fraction import egypt_4_7_11
from .fibonacci import F
from .field import r_theta
from .lucas import L
from .ratios import ratio, ratio_error_bounds
from .self_model import SelfModel
from .signatures import signature_summary


def main():
    # Ensure UTF-8 stdout so emoji in markdown output doesn't crash on Windows
    if hasattr(sys.stdout, "reconfigure"):
        with contextlib.suppress(Exception):
            sys.stdout.reconfigure(encoding="utf-8")

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
    sub.add_parser("cfrac", help="Continued fraction meta for L_{n+1}/L_n (n>=1)").add_argument(
        "n", type=int
    )

    # Self-model subcommand
    sp = sub.add_parser("self-model", help="Sentience seed self-model interface")
    sm_group = sp.add_mutually_exclusive_group(required=True)
    sm_group.add_argument("--observe", type=str, default=None, help="Observe an input pattern")
    sm_group.add_argument("--ask", action="store_true", default=False, help="Query for data needs")
    sm_group.add_argument(
        "--integrate", type=str, default=None, help="Integrate new data (JSON string)"
    )
    sm_group.add_argument("--state", action="store_true", default=False, help="Show current state")

    # Add entropy pump evaluation command
    sp = sub.add_parser("eval", help="Evaluate entropy pump results against acceptance rules")
    sp.add_argument("results_file", help="Path to entropy pump results JSON file")
    sp.add_argument(
        "--lucas-weights",
        nargs=3,
        type=int,
        default=[4, 7, 11],
        help="Lucas weights (default: 4 7 11)",
    )
    sp.add_argument("--markdown", action="store_true", help="Output as markdown (default: JSON)")

    args = p.parse_args()
    out: Any
    if args.cmd == "field":
        a, b = args.a, args.b
        out = {n: r_theta(n) for n in range(a, b + 1)}
    elif args.cmd == "lucas":
        a, b = args.a, args.b
        out = {n: L(n) for n in range(a, b + 1)}
    elif args.cmd == "fib":
        a, b = args.a, args.b
        out = {n: F(n) for n in range(a, b + 1)}
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
    elif args.cmd == "self-model":
        sm = SelfModel()
        if args.observe is not None:
            delta = sm.observe(args.observe)
            out = {"delta": delta, "state": sm.state()}
        elif args.ask:
            query = sm.ask()
            out = query if query is not None else {"query": None}
        elif args.integrate is not None:
            out = sm.integrate(args.integrate)
        elif args.state:
            out = sm.state()
        else:
            out = {"error": "self-model requires --observe, --ask, --integrate, or --state"}
    elif args.cmd == "eval":
        # Import here to avoid circular imports
        try:
            # Try to import from scripts package
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            sys.path.insert(0, project_root)
            from scripts.results_evaluator import evaluate_and_summarize_results
        except ImportError:
            print(
                "Error: Cannot import results evaluator. "
                "Make sure scripts/results_evaluator.py exists."
            )
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
                with open(args.results_file, encoding="utf-8") as f:
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
                        "skips": sum(1 for e in evaluations if e["verdict"] == "SKIP"),
                    },
                }
            except (FileNotFoundError, json.JSONDecodeError) as e:
                out = {"error": f"Cannot load results file: {e}"}
    else:
        out = {"error": "unknown command"}

    if args.cmd != "eval" or not args.markdown:
        print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
