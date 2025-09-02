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

def eval_game(pgn_text: str, mid=(10,30), tag="game", lucas_weights=None):
    g = chess.pgn.read_game(io.StringIO(pgn_text))
    if g is None: return None
    b = g.board()
    evals = []
    for mv in g.mainline_moves():
        b.push(mv)
        evals.append(stock_eval(b))
    if len(evals) < 6: return None
    res = codex_pump_from_series(np.array(evals), window=mid, n_index=PHI, lucas_weights=lucas_weights)
    
    # Create tag suffix for Lucas weights
    tag_suffix = f"_lucas_{'_'.join(map(str, lucas_weights))}" if lucas_weights else ""
    plot_tag = f"{tag}{tag_suffix}"
    
    # Plot curve
    x = np.arange(len(evals))
    plt.figure(figsize=(9,4))
    plt.plot(x, evals, label="Stock (cp)")
    if res["ok"]:
        start, end = res["offset"], res["offset"]+res["window_len"]
        ycodex = evals.copy()
        ycodex[start:end] = res["series_codex"]
        plt.plot(x, ycodex, label="Codex (adjusted)")
        lucas_info = f" Lucas({','.join(map(str, lucas_weights))})" if lucas_weights else ""
        t = f"{tag}: ΔVar {res['variance_reduction_pct']:.1f}%, MAE +{res['mae_improvement_pct']:.1f}%{lucas_info}"
    else:
        t = f"{tag}: Codex skip ({res['reason']})"
    plt.title(t); plt.xlabel("Move"); plt.ylabel("Eval"); plt.grid(True); plt.legend()
    path = os.path.join(OUT, f"{plot_tag}_curve.png"); plt.tight_layout(); plt.savefig(path, dpi=160); plt.close()
    # Histogram of theta' (φ-clamp)
    if res["ok"]:
        edges, hist = res["theta_after_hist"]
        centers = 0.5*(np.array(edges[1:])+np.array(edges[:-1]))
        plt.figure(figsize=(7,3))
        plt.bar(centers, hist, width=(edges[1]-edges[0]))
        plt.axvline(+res["phi_clamp_rad"], ls="--"); plt.axvline(-res["phi_clamp_rad"], ls="--")
        lucas_info = f" Lucas({','.join(map(str, lucas_weights))})" if lucas_weights else ""
        plt.title(f"{tag}: φ-clamp at ±{res['phi_clamp_rad']:.3f} rad (~±38.2°){lucas_info}")
        plt.tight_layout(); plt.savefig(os.path.join(OUT, f"{plot_tag}_clamp.png"), dpi=160); plt.close()
    
    result = {"tag": tag, "moves": len(evals), **({} if not res["ok"] else res)}
    if lucas_weights:
        result["lucas_weights"] = lucas_weights
    return result

def load_demo_pgns():
    # Three compact classics (trimmed)
    return [
        ("kasparov_deepblue_1997_g2",
         """[Event "IBM Man-Machine"] [Date "1997.05.03"] [Result "1-0"]
         1.e4 c6 2.d4 d5 3.Nc3 dxe4 4.Nxe4 Nd7 5.Ng5 Ngf6 6.Bd3 e6 7.N1f3 h6
         8.Nxe6 Qe7 9.O-O fxe6 10.Bg6+ Kd8 11.Bf4 b5 12.Bd3 Bd6 13.Re1 c5 14.g3 c4
         15.Be4 Qd8 16.Bc1 Qc7 17.Nh4 g5 18.Ng2 Bb7 19.Bf5 Re8 20.Rxe6 Rxe6
         21.Bxe6 Nd5 22.Qf3 N7f6 23.Bxd5 Nxd5 24.Qxd5+ Bd6 25.Qf7 Qe7 26.Qxe7+ Bxe7
         27.Be3 Kd7 28.Kf1 a6 29.Ke2 Bd5 30.Kd3 Be4+ 31.Kc3 Bd5 32.Kd3 Be4+ 33.Kc3 Bd5 34.Kd3 1-0"""),
        ("fischer_spassky_1972_g6",
         """[Event "WCh 1972"] [Date "1972.07.23"] [Result "1-0"]
         1.c4 e6 2.Nf3 d5 3.d4 Nf6 4.Nc3 Bb4 5.e3 O-O 6.Bd3 c5 7.O-O Nc6 8.a3 Ba5
         9.Ne2 dxc4 10.Bxc4 Bb6 11.dxc5 Qxd1 12.Rxd1 Bxc5 13.b4 Be7 14.Bb2 Rd8
         15.Rxd8+ Bxd8 16.Rd1 Be7 17.Ned4 Nxd4 18.Nxd4 Bd7 19.Nb5 Bxb5 20.Bxb5 Nxd5
         21.Bd3 Rd8 22.Be4 Nc3 23.Bxc3 Bxc3 24.Bc2 Rc8 25.Rd3 Bb2 26.h4 Kf8 27.Be4 Rc7
         28.Kh2 Ke7 29.Kg3 Kd6 30.Kf4 b6 31.g4 g6 32.h5 Rc4 33.Ke5 Kc7 34.Kd5 Kb7 35.Ke5 1-0"""),
        ("carlsen_anand_2013_g9",
         """[Event "WCh 2013"] [Date "2013.11.21"] [Result "1/2-1/2"]
         1.d4 Nf6 2.c4 g6 3.Nc3 d5 4.cxd5 Nxd5 5.Bd2 Bg7 6.e4 Nxc3 7.Bxc3 O-O
         8.Qd2 Nc6 9.Nf3 Bg4 10.d5 Bxf3 11.Bxg7 Kxg7 12.Qf4 Qf6 13.Qxf6+ Qxf6
         14.Be2 Nd4 15.Qe3 Qxa1+ 16.Kd2 Qxh1 17.Qxd4+ e5 18.Qxe5+ f6 19.Qe7+ Kg8
         20.Qe6+ Kg7 21.Qe7+ Kg8 22.Qe6+ Kg7 23.Qe7+ Kg8 24.Qe6+ Kg7 25.Qe7+ Kg8 1/2-1/2""")
    ]

def lucas_sweep_analysis(pgns, mid=(10,30), lucas_combinations=None):
    """Run Lucas sweep comparing different weight combinations."""
    if lucas_combinations is None:
        lucas_combinations = [
            None,  # baseline (no Lucas weights)
            (4, 7, 11),  # default Lucas sequence
            (3, 6, 10),  # alternative comparison
            (2, 5, 8),   # smaller values
            (5, 8, 13),  # larger values
        ]
    
    all_results = []
    
    for lucas_weights in lucas_combinations:
        print(f"Running analysis with Lucas weights: {lucas_weights}")
        for tag, pgn in pgns:
            r = eval_game(pgn, mid=mid, tag=tag, lucas_weights=lucas_weights)
            if r: 
                all_results.append(r)
    
    return all_results

def create_lucas_heatmap(results):
    """Create a heatmap comparing Lucas weight performance."""
    # Group results by game and Lucas weights
    games = set(r["tag"] for r in results if r.get("ok"))
    lucas_combos = []
    for r in results:
        if r.get("ok"):
            lw = r.get("lucas_weights")
            if lw not in lucas_combos:
                lucas_combos.append(lw)
    
    # Create data matrix for heatmap
    variance_matrix = []
    compression_matrix = []
    
    combo_labels = []
    for combo in lucas_combos:
        if combo is None:
            combo_labels.append("Baseline")
        else:
            combo_labels.append(f"({','.join(map(str, combo))})")
    
    for combo in lucas_combos:
        var_row = []
        comp_row = []
        for game in sorted(games):
            # Find result for this game/combo combination
            game_result = None
            for r in results:
                if r["tag"] == game and r.get("lucas_weights") == combo and r.get("ok"):
                    game_result = r
                    break
            
            if game_result:
                var_row.append(game_result["variance_reduction_pct"])
                comp_row.append(game_result["compression"])
            else:
                var_row.append(0)  # fallback
                comp_row.append(0)
        
        variance_matrix.append(var_row)
        compression_matrix.append(comp_row)
    
    # Create heatmap plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Variance reduction heatmap
    im1 = ax1.imshow(variance_matrix, cmap='YlOrRd', aspect='auto')
    ax1.set_title('Variance Reduction % (Lucas Sweep)')
    ax1.set_xlabel('Games')
    ax1.set_ylabel('Lucas Weight Combinations')
    ax1.set_xticks(range(len(games)))
    ax1.set_xticklabels(sorted(games), rotation=45, ha='right')
    ax1.set_yticks(range(len(combo_labels)))
    ax1.set_yticklabels(combo_labels)
    
    # Add text annotations
    for i in range(len(combo_labels)):
        for j in range(len(games)):
            text = ax1.text(j, i, f'{variance_matrix[i][j]:.1f}', 
                           ha="center", va="center", color="black", fontsize=10)
    
    plt.colorbar(im1, ax=ax1, label='Variance Reduction %')
    
    # Compression heatmap
    im2 = ax2.imshow(compression_matrix, cmap='Blues', aspect='auto')
    ax2.set_title('Compression Coefficient (Lucas Sweep)')
    ax2.set_xlabel('Games')
    ax2.set_ylabel('Lucas Weight Combinations')
    ax2.set_xticks(range(len(games)))
    ax2.set_xticklabels(sorted(games), rotation=45, ha='right')
    ax2.set_yticks(range(len(combo_labels)))
    ax2.set_yticklabels(combo_labels)
    
    # Add text annotations
    for i in range(len(combo_labels)):
        for j in range(len(games)):
            text = ax2.text(j, i, f'{compression_matrix[i][j]:.3f}', 
                           ha="center", va="center", color="black", fontsize=10)
    
    plt.colorbar(im2, ax=ax2, label='Compression Coefficient')
    
    plt.tight_layout()
    heatmap_path = os.path.join(OUT, "lucas_sweep_heatmap.png")
    plt.savefig(heatmap_path, dpi=160, bbox_inches='tight')
    plt.close()
    
    return heatmap_path

def main():
    mid = (10, 30)
    
    # Load demo games
    demo_pgns = load_demo_pgns()
    
    # Run Lucas sweep analysis
    print("Running Lucas sweep analysis...")
    lucas_results = lucas_sweep_analysis(demo_pgns, mid=mid)
    
    # Run baseline analysis for backward compatibility
    print("Running baseline analysis...")
    rows = []
    for tag, pgn in demo_pgns:
        r = eval_game(pgn, mid=mid, tag=tag)
        if r: rows.append(r)
    
    # Combine all results
    all_rows = rows + lucas_results
    
    # Write summary JSON + CSV-like TSV
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    js = os.path.join(OUT, f"entropy_pump_summary_{ts}.json")
    with open(js, "w", encoding="utf-8") as f: f.write(json.dumps(all_rows, indent=2))
    
    # Write TSV with Lucas weights column
    tsv = os.path.join(OUT, f"entropy_pump_summary_{ts}.tsv")
    with open(tsv, "w", encoding="utf-8") as f:
        hdr = ["tag","moves","variance_reduction_pct","compression","mae_improvement_pct","phi_clamp_rad","lucas_weights"]
        f.write("\t".join(hdr)+"\n")
        for r in all_rows:
            if not r.get("ok"): continue
            # Format lucas_weights for TSV
            lw_str = str(r.get("lucas_weights", "")).replace("(", "").replace(")", "").replace(" ", "") if r.get("lucas_weights") else ""
            row_data = [
                r.get("tag", ""),
                r.get("moves", ""),
                r.get("variance_reduction_pct", ""),
                r.get("compression", ""),
                r.get("mae_improvement_pct", ""),
                r.get("phi_clamp_rad", ""),
                lw_str
            ]
            f.write("\t".join(str(x) for x in row_data)+"\n")
    
    # Create Lucas sweep heatmap
    print("Creating Lucas sweep heatmap...")
    heatmap_path = create_lucas_heatmap(lucas_results)
    
    # Write Lucas sweep summary
    lucas_summary_path = os.path.join(OUT, f"lucas_sweep_summary_{ts}.json")
    with open(lucas_summary_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(lucas_results, indent=2))
    
    print(f"OK — wrote {js} and {tsv} and plots in {OUT}/")
    print(f"Lucas sweep results in {lucas_summary_path}")
    print(f"Lucas sweep heatmap: {heatmap_path}")

if __name__ == "__main__":
    main()