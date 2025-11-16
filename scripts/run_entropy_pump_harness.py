"""
Parse PGNs, compute basic evals, apply Codex pump, write CSV + plots.
Artifacts land in ./out so your GitHub Action uploads them.
"""

import io
import json
import os
from datetime import datetime, timezone

import chess
import chess.pgn
import matplotlib.pyplot as plt
import numpy as np

from .codex_entropy_pump import PHI, codex_pump_from_series

OUT = "out"
os.makedirs(OUT, exist_ok=True)


def stock_eval(board: chess.Board) -> float:
    V = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}
    m = sum(
        (len(board.pieces(pt, chess.WHITE)) - len(board.pieces(pt, chess.BLACK)))
        * V[pt]
        for pt in V
    )
    mobility = len(list(board.legal_moves)) * 0.1
    # tiny king shield
    kW, kB = board.king(chess.WHITE), board.king(chess.BLACK)

    def shield(k, color, sgn):
        if k is None:
            return 0
        paw = chess.Piece(chess.PAWN, color)
        return sum(
            1
            for d in (7, 8, 9)
            if 0 <= k + sgn * d < 64 and board.piece_at(k + sgn * d) == paw
        )

    ks = (shield(kW, chess.WHITE, +1) - shield(kB, chess.BLACK, -1)) * 0.5
    return (m + mobility + ks) * 100.0  # cp


def eval_game(pgn_text: str, mid=(10, 30), tag="game"):
    g = chess.pgn.read_game(io.StringIO(pgn_text))
    if g is None:
        return None
    b = g.board()
    evals = []
    for mv in g.mainline_moves():
        b.push(mv)
        evals.append(stock_eval(b))
    if len(evals) < 6:
        return None
    res = codex_pump_from_series(np.array(evals), window=mid, n_index=PHI)
    # Plot curve
    x = np.arange(len(evals))
    plt.figure(figsize=(9, 4))
    plt.plot(x, evals, label="Stock (cp)")
    if res["ok"]:
        start, end = res["offset"], res["offset"] + res["window_len"]
        ycodex = evals.copy()
        ycodex[start:end] = res["series_codex"]
        plt.plot(x, ycodex, label="Codex (adjusted)")
        t = f"{tag}: ΔVar {res['variance_reduction_pct']:.1f}%, MAE +{res['mae_improvement_pct']:.1f}%"
    else:
        t = f"{tag}: Codex skip ({res['reason']})"
    plt.title(t)
    plt.xlabel("Move")
    plt.ylabel("Eval")
    plt.grid(True)
    plt.legend()
    path = os.path.join(OUT, f"{tag}_curve.png")
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()
    # Histogram of theta' (φ-clamp)
    if res["ok"]:
        edges, hist = res["theta_after_hist"]
        centers = 0.5 * (np.array(edges[1:]) + np.array(edges[:-1]))
        plt.figure(figsize=(7, 3))
        plt.bar(centers, hist, width=(edges[1] - edges[0]))
        plt.axvline(+res["phi_clamp_rad"], ls="--")
        plt.axvline(-res["phi_clamp_rad"], ls="--")
        plt.title(f"{tag}: φ-clamp at ±{res['phi_clamp_rad']:.3f} rad (~±38.2°)")
        plt.tight_layout()
        plt.savefig(os.path.join(OUT, f"{tag}_clamp.png"), dpi=160)
        plt.close()
    return {"tag": tag, "moves": len(evals), **({} if not res["ok"] else res)}


def load_demo_pgns():
    # Three compact classics (trimmed)
    return [
        (
            "kasparov_deepblue_1997_g2",
            """[Event "IBM Man-Machine"] [Date "1997.05.03"] [Result "1-0"]
         1.e4 c6 2.d4 d5 3.Nc3 dxe4 4.Nxe4 Nd7 5.Ng5 Ngf6 6.Bd3 e6 7.N1f3 h6
         8.Nxe6 Qe7 9.O-O fxe6 10.Bg6+ Kd8 11.Bf4 b5 12.Bd3 Bd6 13.Re1 c5 14.g3 c4
         15.Be4 Qd8 16.Bc1 Qc7 17.Nh4 g5 18.Ng2 Bb7 19.Bf5 Re8 20.Rxe6 Rxe6
         21.Bxe6 Nd5 22.Qf3 N7f6 23.Bxd5 Nxd5 24.Qxd5+ Bd6 25.Qf7 Qe7 26.Qxe7+ Bxe7
         27.Be3 Kd7 28.Kf1 a6 29.Ke2 Bd5 30.Kd3 Be4+ 31.Kc3 Bd5 32.Kd3 Be4+ 33.Kc3 Bd5 34.Kd3 1-0""",
        ),
        (
            "fischer_spassky_1972_g6",
            """[Event "WCh 1972"] [Date "1972.07.23"] [Result "1-0"]
         1.c4 e6 2.Nf3 d5 3.d4 Nf6 4.Nc3 Bb4 5.e3 O-O 6.Bd3 c5 7.O-O Nc6 8.a3 Ba5
         9.Ne2 dxc4 10.Bxc4 Bb6 11.dxc5 Qxd1 12.Rxd1 Bxc5 13.b4 Be7 14.Bb2 Rd8
         15.Rxd8+ Bxd8 16.Rd1 Be7 17.Ned4 Nxd4 18.Nxd4 Bd7 19.Nb5 Bxb5 20.Bxb5 Nxd5
         21.Bd3 Rd8 22.Be4 Nc3 23.Bxc3 Bxc3 24.Bc2 Rc8 25.Rd3 Bb2 26.h4 Kf8 27.Be4 Rc7
         28.Kh2 Ke7 29.Kg3 Kd6 30.Kf4 b6 31.g4 g6 32.h5 Rc4 33.Ke5 Kc7 34.Kd5 Kb7 35.Ke5 1-0""",
        ),
        (
            "carlsen_anand_2013_g9",
            """[Event "WCh 2013"] [Date "2013.11.21"] [Result "1/2-1/2"]
         1.d4 Nf6 2.c4 g6 3.Nc3 d5 4.cxd5 Nxd5 5.Bd2 Bg7 6.e4 Nxc3 7.Bxc3 O-O
         8.Qd2 Nc6 9.Nf3 Bg4 10.d5 Bxf3 11.Bxg7 Kxg7 12.Qf4 Qf6 13.Qxf6+ Qxf6
         14.Be2 Nd4 15.Qe3 Qxa1+ 16.Kd2 Qxh1 17.Qxd4+ e5 18.Qxe5+ f6 19.Qe7+ Kg8
         20.Qe6+ Kg7 21.Qe7+ Kg8 22.Qe6+ Kg7 23.Qe7+ Kg8 24.Qe6+ Kg7 25.Qe7+ Kg8 1/2-1/2""",
        ),
    ]


def main():
    mid = (10, 30)
    lucas_weights = (4, 7, 11)  # Default Lucas weights
    rows = []
    for tag, pgn in load_demo_pgns():
        r = eval_game(pgn, mid=mid, tag=tag)
        if r:
            rows.append(r)

    # Write summary JSON + CSV-like TSV
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    js = os.path.join(OUT, f"entropy_pump_summary_{ts}.json")
    with open(js, "w", encoding="utf-8") as f:
        f.write(json.dumps(rows, indent=2))
    tsv = os.path.join(OUT, f"entropy_pump_summary_{ts}.tsv")
    with open(tsv, "w", encoding="utf-8") as f:
        hdr = [
            "tag",
            "moves",
            "variance_reduction_pct",
            "compression",
            "mae_improvement_pct",
            "phi_clamp_rad",
        ]
        f.write("\t".join(hdr) + "\n")
        for r in rows:
            if not r.get("ok"):
                continue
            f.write("\t".join(str(r.get(k, "")) for k in hdr) + "\n")

    # Generate and display results summary
    from .results_evaluator import generate_summary_comment

    summary = generate_summary_comment(rows, lucas_weights)

    # Write summary to file
    summary_file = os.path.join(OUT, f"entropy_pump_summary_{ts}.md")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"OK — wrote {js} and {tsv} and plots in {OUT}/")
    print(f"Summary written to {summary_file}")
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(summary)


if __name__ == "__main__":
    main()
