import argparse, json
from .field import r_theta
from .lucas import L
from .fibonacci import F
from .ratios import ratio, ratio_error_bounds
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
    else:
        out = {"error": "unknown command"}

    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
