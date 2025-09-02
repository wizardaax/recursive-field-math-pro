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
    """
    Evaluate a chess game using stock evaluation and apply entropy pump analysis.
    Enhanced with comprehensive error handling.
    """
    try:
        # Parse PGN with error handling
        g = chess.pgn.read_game(io.StringIO(pgn_text))
        if g is None: 
            print(f"Warning: Failed to parse PGN for {tag}")
            return None
        
        # Initialize board and evaluation list
        b = g.board()
        evals = []
        move_count = 0
        
        # Process moves with error handling
        for mv in g.mainline_moves():
            try:
                if not b.is_legal(mv):
                    print(f"Warning: Illegal move {mv} in {tag} at position {move_count}")
                    continue
                b.push(mv)
                evals.append(stock_eval(b))
                move_count += 1
            except Exception as e:
                print(f"Warning: Error processing move {mv} in {tag}: {e}")
                continue
        
        # Validate minimum game length
        if len(evals) < 6: 
            print(f"Warning: Game {tag} too short ({len(evals)} moves), skipping analysis")
            return None
        
        # Apply entropy pump analysis with error handling
        try:
            res = codex_pump_from_series(np.array(evals), window=mid, n_index=PHI)
        except Exception as e:
            print(f"Error: Entropy pump analysis failed for {tag}: {e}")
            return {"tag": tag, "moves": len(evals), "ok": False, "reason": f"analysis_error: {e}"}
        
        # Generate plots with error handling
        try:
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
        except Exception as e:
            print(f"Warning: Plot generation failed for {tag}: {e}")
        
        return {"tag": tag, "moves": len(evals), **({} if not res["ok"] else res)}
        
    except Exception as e:
        print(f"Error: Failed to evaluate game {tag}: {e}")
        return {"tag": tag, "moves": 0, "ok": False, "reason": f"evaluation_error: {e}"}

def load_demo_pgns():
    # Three well-known games with valid PGN notation
    return [
        ("kasparov_topalov_1999",
         """[Event "Hoogovens A Tournament"] [Site "Wijk aan Zee NED"] [Date "1999.01.20"] [Round "4"] [White "Garry Kasparov"] [Black "Veselin Topalov"] [Result "1-0"]
1.e4 d6 2.d4 Nf6 3.Nc3 g6 4.Be3 Bg7 5.Qd2 c6 6.f3 b5 7.Nge2 Nbd7
8.Bh6 Bxh6 9.Qxh6 Bb7 10.a3 e5 11.O-O-O Qe7 12.Kb1 a6 13.Nc1 O-O-O
14.Nb3 exd4 15.Rxd4 c5 16.Rd1 Nb6 17.g3 Kb8 18.Na5 Ba8 19.Bh3 d5
20.Qf4+ Ka7 21.Rhe1 d4 22.Nd5 Nbxd5 23.exd5 Qd6 24.Rxd4 cxd4 25.Re7+ Kb6
26.Qxd4+ Kxa5 27.b4+ Ka4 28.Qc3 Qxd5 29.Ra7 Bb7 30.Rxb7 Qc4 31.Qxf6 Kxa3
32.Qxa6+ Kxb4 33.c3+ Kxc3 34.Qa1+ Kd2 35.Qb2+ Kd1 36.Bf1 Rd2 37.Rd7 Rxd7
38.Bxc4 bxc4 39.Qxh8 Rd3 40.Qa8 c3 41.Qa4+ Ke1 42.f4 f5 43.Kc1 Rd2
44.Qa7 1-0"""),
        ("fischer_byrne_1956",
         """[Event "Rosenwald Memorial"] [Site "New York, NY USA"] [Date "1956.10.17"] [Round "8"] [White "Donald Byrne"] [Black "Robert James Fischer"] [Result "0-1"]
1.Nf3 Nf6 2.c4 g6 3.Nc3 Bg7 4.d4 O-O 5.Bf4 d5 6.Qb3 dxc4 7.Qxc4 c6
8.e4 Nbd7 9.Rd1 Nb6 10.Qc5 Bg4 11.Bg5 Na4 12.Qa3 Nxc3 13.bxc3 Nxe4
14.Bxe7 Qb6 15.Bc4 Nxc3 16.Bc5 Rfe8+ 17.Kf1 Be6 18.Bxb6 Bxc4+ 19.Kg1 Ne2+
20.Kf1 Nxd4+ 21.Kg1 Ne2+ 22.Kf1 Nc3+ 23.Kg1 axb6 24.Qb4 Ra4 25.Qxb6 Nxd1
26.h3 Rxa2 27.Kh2 Nxf2 28.Re1 Rxe1 29.Qd8+ Bf8 30.Nxe1 Bd5 31.Nf3 Ne4
32.Qb8 b5 33.h4 h6 34.Ne5 Kg7 35.Kg1 Bc5+ 36.Kf1 Ng3+ 37.Ke1 Bb4+
38.Kd1 Bb3+ 39.Kc1 Ne2+ 40.Kb1 Nc3+ 41.Kc1 Rc2# 0-1"""),
        ("carlsen_caruana_2018_g12",
         """[Event "WCh 2018"] [Site "London ENG"] [Date "2018.11.28"] [Round "12"] [White "Magnus Carlsen"] [Black "Fabiano Caruana"] [Result "1/2-1/2"]
1.e4 c5 2.Nf3 Nc6 3.Bb5 g6 4.Bxc6 dxc6 5.d3 Bg7 6.h3 Nf6 7.Nc3 Nd7
8.Be3 e5 9.Qd2 h6 10.O-O Nf8 11.Nh2 Be6 12.f4 exf4 13.Bxf4 Ne6 14.Be3 Qd7
15.Rf2 O-O 16.Raf1 Ng5 17.Nd1 Ne6 18.Nf3 Ng5 19.Nf2 Ne6 20.Nh4 Ng5
21.Nhf3 Ne6 22.g3 Rad8 23.Kg2 Rfe8 24.Qc3 Bf8 25.a4 Bg7 26.Qd2 Bf8
27.b3 Bg7 28.Qc3 Bf8 29.h4 h5 30.Qd2 Bg7 31.Qc3 Bf8 32.Re2 Qd6
33.Ref2 Qd7 34.Re2 Qd6 35.Ref2 1/2-1/2""")
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