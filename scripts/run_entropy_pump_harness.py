"""
Parse PGNs, compute basic evals, apply Codex pump, write CSV + plots.
Artifacts land in ./out so your GitHub Action uploads them.
"""
import os, io, math, json, numpy as np, matplotlib.pyplot as plt
import chess, chess.pgn
from datetime import datetime, timezone
from .codex_entropy_pump import codex_pump_from_series, PHI

OUT = "out"
os.makedirs(OUT, exist_ok=True)

def stock_eval(board: chess.Board) -> float:
    V = {chess.PAWN:1, chess.KNIGHT:3, chess.BISHOP:3, chess.ROOK:5, chess.QUEEN:9}
    m = sum((len(board.pieces(pt, chess.WHITE))-len(board.pieces(pt, chess.BLACK)))*V[pt] for pt in V)
    mobility = len(list(board.legal_moves))*0.1
    # tiny king shield
    kW, kB = board.king(chess.WHITE), board.king(chess.BLACK)
    def shield(k, color, sgn): 
        if k is None: return 0
        paw = chess.Piece(chess.PAWN, color)
        return sum(1 for d in (7,8,9) if 0 <= k+sgn*d < 64 and board.piece_at(k+sgn*d)==paw)
    ks = (shield(kW, chess.WHITE, +1) - shield(kB, chess.BLACK, -1))*0.5
    return (m + mobility + ks) * 100.0  # cp

def eval_game(pgn_text: str, mid=(10,30), tag="game"):
    try:
        g = chess.pgn.read_game(io.StringIO(pgn_text))
        if g is None: 
            print(f"Warning: Could not parse PGN for {tag}")
            return None
        
        b = g.board()
        evals = []
        
        for i, mv in enumerate(g.mainline_moves()):
            try:
                b.push(mv)
                evals.append(stock_eval(b))
            except chess.IllegalMoveError as e:
                print(f"Warning: Illegal move in {tag} at move {i+1}: {mv} - {e}")
                # Try to continue with what we have
                break
        
        if len(evals) < 6: 
            print(f"Warning: Too few moves ({len(evals)}) in {tag} for analysis")
            return None
            
    except Exception as e:
        print(f"Warning: Error processing {tag}: {e}")
        return None
        
    res = codex_pump_from_series(np.array(evals), window=mid, n_index=PHI)
    
    # Plot curve
    x = np.arange(len(evals))
    plt.figure(figsize=(9,4))
    plt.plot(x, evals, label="Stock (cp)")
    if res["ok"]:
        start, end = res["offset"], res["offset"]+res["window_len"]
        ycodex = evals.copy()
        ycodex[start:end] = res["series_codex"]
        plt.plot(x, ycodex, label="Codex (adjusted)")
        t = f"{tag}: ΔVar {res['variance_reduction_pct']:.1f}%, MAE +{res['mae_improvement_pct']:.1f}%"
    else:
        t = f"{tag}: Codex skip ({res['reason']})"
    plt.title(t); plt.xlabel("Move"); plt.ylabel("Eval"); plt.grid(True); plt.legend()
    path = os.path.join(OUT, f"{tag}_curve.png"); plt.tight_layout(); plt.savefig(path, dpi=160); plt.close()
    
    # Histogram of theta' (φ-clamp)
    if res["ok"]:
        edges, hist = res["theta_after_hist"]
        centers = 0.5*(np.array(edges[1:])+np.array(edges[:-1]))
        plt.figure(figsize=(7,3))
        plt.bar(centers, hist, width=(edges[1]-edges[0]))
        plt.axvline(+res["phi_clamp_rad"], ls="--"); plt.axvline(-res["phi_clamp_rad"], ls="--")
        plt.title(f"{tag}: φ-clamp at ±{res['phi_clamp_rad']:.3f} rad (~±38.2°)")
        plt.tight_layout(); plt.savefig(os.path.join(OUT, f"{tag}_clamp.png"), dpi=160); plt.close()
    
    return {"tag": tag, "moves": len(evals), **({} if not res["ok"] else res)}

def load_demo_pgns():
    # Simple, completely valid demonstration games for entropy pump testing
    return [
        ("italian_game_demo",
         """[Event "Demo Game"] [Date "2024.01.01"] [Result "1-0"]
1.e4 e5 2.Nf3 Nc6 3.Bc4 Bc5 4.c3 Nf6 5.d4 exd4 6.cxd4 Bb4+ 7.Bd2 Bxd2+
8.Nbxd2 d5 9.exd5 Nxd5 10.Qb3 Nce7 11.O-O c6 12.Rfe1 O-O 13.Re4 Nf6
14.Re1 Ned5 15.Ne4 Nxe4 16.Rxe4 Be6 17.Bxd5 Bxd5 18.Qb4 Re8 19.Re5 Rxe5
20.dxe5 Qe7 21.Qxe7 Nxe7 22.Re1 Nc8 23.f4 Nb6 24.g3 Nd7 25.Re3 Nxe5
26.fxe5 Re8 27.Kf2 Rxe5 28.Ra3 a6 29.b4 Re2+ 30.Kf3 Rxh2 31.a4 1-0"""),
        ("french_defense_demo",
         """[Event "Demo Game"] [Date "2024.01.01"] [Result "0-1"]
1.e4 e6 2.d4 d5 3.Nc3 Bb4 4.e5 c5 5.a3 Bxc3+ 6.bxc3 Ne7 7.Qg4 Qc7
8.Qxg7 Rg8 9.Qxh7 cxd4 10.Ne2 Nbc6 11.f4 Bd7 12.Qd3 dxc3 13.Qxc3 d4
14.Qb3 Nxe5 15.fxe5 Qxe5 16.Bf4 Qf5 17.Qxb7 Rc8 18.Qxa7 Ng6 19.Bg3 Ne5
20.Qa5 Nc4 21.Qa4 Qf1+ 22.Kd2 Ne3 23.Rc1 Qf2 24.Qxd4 Qxg2 25.Qh4 Rc2+
26.Kd3 Nf1 27.Qf4 Nxg3 28.hxg3 Qf1 29.Rc3 Rxc3+ 30.Nxc3 Qf5+ 31.Kd2 Be8 0-1"""),
        ("kings_indian_demo", 
         """[Event "Demo Game"] [Date "2024.01.01"] [Result "1/2-1/2"]
1.d4 Nf6 2.c4 g6 3.Nc3 Bg7 4.e4 d6 5.Nf3 O-O 6.Be2 e5 7.O-O Nc6
8.d5 Ne7 9.Ne1 Nd7 10.Be3 f5 11.f3 f4 12.Bf2 g5 13.c5 Ng6 14.cxd6 cxd6
15.Rc1 Nf6 16.Nd3 g4 17.fxg4 Nxg4 18.Bxg4 Bxg4 19.Qd2 Qh4 20.h3 Be6
21.Rf3 Nh4 22.Rg3+ Kh8 23.Bxh4 Qxh4 24.Rg4 Qh6 25.Qxh6 Bxh6 26.Rc7 Rab8
27.Nf2 Rg8 28.Rg6 Bg7 29.Nfe4 Rxg6 30.Nxg6+ Kg8 31.Nxf8 Bxf8 32.Rxb7 1/2-1/2""")
    ]

def main():
    mid = (10, 30)
    lucas_weights = (4, 7, 11)  # Default Lucas weights
    rows = []
    for tag, pgn in load_demo_pgns():
        r = eval_game(pgn, mid=mid, tag=tag)
        if r: rows.append(r)
    
    # Write summary JSON + CSV-like TSV
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    js = os.path.join(OUT, f"entropy_pump_summary_{ts}.json")
    with open(js, "w", encoding="utf-8") as f: f.write(json.dumps(rows, indent=2))
    tsv = os.path.join(OUT, f"entropy_pump_summary_{ts}.tsv")
    with open(tsv, "w", encoding="utf-8") as f:
        hdr = ["tag","moves","variance_reduction_pct","compression","mae_improvement_pct","phi_clamp_rad"]
        f.write("\t".join(hdr)+"\n")
        for r in rows:
            if not r.get("ok"): continue
            f.write("\t".join(str(r.get(k,"")) for k in hdr)+"\n")
    
    # Generate and display results summary
    from .results_evaluator import generate_summary_comment
    summary = generate_summary_comment(rows, lucas_weights)
    
    # Write summary to file
    summary_file = os.path.join(OUT, f"entropy_pump_summary_{ts}.md")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary)
    
    print(f"OK — wrote {js} and {tsv} and plots in {OUT}/")
    print(f"Summary written to {summary_file}")
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    print(summary)

if __name__ == "__main__":
    main()