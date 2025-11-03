"""
Enhanced entropy pump harness with Regen88 Codex support.
Parse PGNs, compute basic evals, apply Codex pump with Regen88 enhancements, write CSV + plots.
Artifacts land in ./out so your GitHub Action uploads them.
"""
import os, io, math, json, numpy as np, matplotlib.pyplot as plt
import chess, chess.pgn
from datetime import datetime, timezone
from .codex_entropy_pump import codex_pump_from_series, PHI
from .regen88_integration import Regen88Codex, regen88_analyze

OUT = "out"
os.makedirs(OUT, exist_ok=True)

def stock_eval(board: chess.Board) -> float:
    """Simple stock evaluation function for chess positions."""
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


def eval_game(pgn_text: str, mid=(10,30), tag="game", use_regen88=True):
    """
    Evaluate a chess game using entropy pump (with optional Regen88 enhancement).
    
    Args:
        pgn_text: PGN text of the game
        mid: Middle game window (start, end) moves
        tag: Game identifier tag
        use_regen88: Whether to use Regen88 enhanced processing
        
    Returns:
        Analysis results dict
    """
    g = chess.pgn.read_game(io.StringIO(pgn_text))
    if g is None: return None
    
    b = g.board()
    evals = []
    for mv in g.mainline_moves():
        b.push(mv)
        evals.append(stock_eval(b))
    
    if len(evals) < 6: return None
    
    # Choose processing method
    if use_regen88:
        # Use Regen88 enhanced processing
        res = regen88_analyze(np.array(evals), window=mid, tag=tag)
    else:
        # Use standard entropy pump
        res = codex_pump_from_series(np.array(evals), window=mid, n_index=PHI)
    
    # Generate plots
    x = np.arange(len(evals))
    
    # Main evaluation curve plot
    plt.figure(figsize=(10,5))
    plt.subplot(1, 2, 1)
    plt.plot(x, evals, label="Stock (cp)", alpha=0.7)
    
    if res["ok"]:
        # Plot windowed data if available
        if "series_raw" in res:
            series_raw = np.array(res["series_raw"])
            offset = res.get("offset", 0)
            x_window = x[offset:offset+len(series_raw)]
            plt.plot(x_window, series_raw, label="Window", linewidth=2)
        
        # Plot enhanced series if available (Regen88)
        if "series_codex" in res:
            series_codex = np.array(res["series_codex"])
            offset = res.get("offset", 0)
            x_codex = x[offset:offset+len(series_codex)]
            plt.plot(x_codex, series_codex, label="Codex φ-refined", linewidth=2)
        
        # Plot flame-corrected series if available
        if "theta_after_corrected" in res and use_regen88:
            # Convert theta back to approximate eval series for visualization
            corrected_theta = np.array(res["theta_after_corrected"])
            if len(corrected_theta) > 0 and "series_raw" in res:
                # Simple approximation for visualization
                base_series = np.array(res["series_raw"])
                offset = res.get("offset", 0)
                if len(base_series) >= len(corrected_theta):
                    corrected_approx = base_series[:len(corrected_theta)] * (1 + corrected_theta * 0.1)
                    x_corrected = x[offset:offset+len(corrected_approx)]
                    plt.plot(x_corrected, corrected_approx, 
                           label="Regen88 Enhanced", linewidth=2, linestyle='--')
    
    plt.title(f"{tag}: Evaluation Curves")
    plt.xlabel("Move"); plt.ylabel("Centipawns")
    plt.legend(); plt.grid(alpha=0.3)
    
    # Phi-clamp histogram plot
    plt.subplot(1, 2, 2)
    if res["ok"] and "theta_after_hist" in res:
        edges, hist = res["theta_after_hist"]
        centers = [(edges[i] + edges[i+1])/2 for i in range(len(hist))]
        plt.bar(centers, hist, width=0.05, alpha=0.7, label="θ′ distribution")
        
        # Mark phi-clamp lines
        phi_clamp = res.get("phi_clamp_rad", math.asin(1.0/PHI))
        plt.axvline(+phi_clamp, ls="--", color='red', label=f"φ-clamp ±{phi_clamp:.3f} rad")
        plt.axvline(-phi_clamp, ls="--", color='red')
        
        # Add Regen88 info if available
        if use_regen88 and "regen88_processed" in res:
            modules_info = []
            if res.get("flame_correction", {}).get("flames_corrected", 0) > 0:
                modules_info.append("Flame Corrected")
            if res.get("self_healing_applied", False):
                modules_info.append("Self-Healed")
            if "recursive_defense_multi_layer" in res:
                layers = res["recursive_defense_multi_layer"].get("layers_activated", 0)
                if layers > 0:
                    modules_info.append(f"Defense ({layers} layers)")
            
            if modules_info:
                plt.text(0.02, 0.98, "Regen88: " + ", ".join(modules_info), 
                        transform=plt.gca().transAxes, va='top', fontsize=8,
                        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    
    plt.title(f"{tag}: φ-clamp at ±{res.get('phi_clamp_rad', 0):.3f} rad (~±38.2°)" if res["ok"] else f"{tag}: Analysis Failed")
    plt.xlabel("Phase (rad)"); plt.ylabel("Count")
    plt.legend(); plt.grid(alpha=0.3)
    
    plt.tight_layout()
    plot_suffix = "_regen88" if use_regen88 else "_standard"
    plt.savefig(os.path.join(OUT, f"{tag}{plot_suffix}_analysis.png"), dpi=160)
    plt.close()
    
    # Create result summary
    result_summary = {"tag": tag, "moves": len(evals)}
    if res["ok"]:
        result_summary.update({
            k: res[k] for k in res 
            if k in ["variance_reduction_pct", "compression", "mae_improvement_pct", "phi_clamp_rad"]
        })
        
        # Add Regen88 specific metrics
        if use_regen88 and "regen88_processed" in res:
            result_summary["regen88_enhanced"] = True
            result_summary["regen88_modules"] = res["modules_enabled"]
            
            # Add improvement metrics
            if "improvement_metrics" in res:
                result_summary["regen88_improvement"] = res["improvement_metrics"]
            
            # Add flame correction stats
            if "flame_correction" in res:
                flame_info = res["flame_correction"]
                result_summary["flames_detected"] = flame_info.get("original_detection", {}).get("flame_detected", False)
                result_summary["flames_corrected"] = flame_info.get("flames_corrected", 0)
                result_summary["flame_effectiveness"] = flame_info.get("correction_effectiveness", 0.0)
            
            # Add self-healing stats
            if "self_healing" in res:
                healing_info = res["self_healing"]
                result_summary["healing_applied"] = healing_info.get("healing_result", {}).get("healing_applied", False)
                result_summary["healing_effectiveness"] = healing_info.get("healing_result", {}).get("healing_effectiveness", 0.0)
            
            # Add defense stats
            if "recursive_defense_multi_layer" in res:
                defense_info = res["recursive_defense_multi_layer"]
                result_summary["defense_layers_activated"] = defense_info.get("layers_activated", 0)
                result_summary["defense_effectiveness"] = defense_info.get("overall_effectiveness", 0.0)
    else:
        result_summary.update(res)
    
    return result_summary


def load_demo_pgns():
    """Load demonstration PGN games."""
    # Demo PGNs for testing
    pgns = [
        ("demo_tactical", """
[Event "Demo Tactical"]
[White "Player1"] [Black "Player2"]
1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 4.Ba4 Nf6 5.O-O Be7 6.Re1 b5 7.Bb3 d6 8.c3 O-O 
9.h3 Nb8 10.d4 Nbd7 11.c4 c6 12.cxb5 axb5 13.Nc3 Bb7 14.Bg5 b4 15.Nb1 h6 
16.Bh4 c5 17.dxe5 Nxe5 18.Nxe5 dxe5 19.Bxf6 Bxf6 20.Nd2 1-0
        """),
        
        ("demo_positional", """
[Event "Demo Positional"]
[White "Player1"] [Black "Player2"]
1.d4 d5 2.c4 e6 3.Nc3 Nf6 4.cxd5 exd5 5.Bg5 c6 6.e3 Bf5 7.Qf3 Bg6 8.Bxf6 Qxf6 
9.Qxf6 gxf6 10.Nf3 Nd7 11.Nh4 Bg7 12.Be2 O-O-O 13.Nxg6 hxg6 14.h4 Rde8 
15.O-O-O Rhf8 16.Rd2 f5 17.Rhd1 Nf6 18.f3 Ne4 19.Nxe4 fxe4 20.fxe4 f5 1/2-1/2
        """),
        
        ("demo_endgame", """
[Event "Demo Endgame"]
[White "Player1"] [Black "Player2"]
1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 a6 6.Be3 e6 7.f3 b5 8.Qd2 Bb7 
9.O-O-O Nbd7 10.h4 Qc7 11.Kb1 Rc8 12.g4 h6 13.Be2 Ne5 14.f4 Nfd7 15.fxe5 dxe5 
16.Nf3 Nc5 17.Bxc5 Qxc5 18.Nd5 Bxd5 19.exd5 e4 20.Ng1 Qxd5 21.Qxd5 exd5 
22.Rxd5 Ke7 23.Nf3 Rc1+ 24.Ka2 1-0
        """)
    ]
    return pgns


def main():
    """Main harness function with Regen88 support."""
    mid = (10, 30)
    lucas_weights = (4, 7, 11)
    
    # Process games with both standard and Regen88 modes for comparison
    standard_rows = []
    regen88_rows = []
    
    for tag, pgn in load_demo_pgns():
        # Standard processing
        standard_result = eval_game(pgn, mid=mid, tag=f"{tag}_std", use_regen88=False)
        if standard_result:
            standard_rows.append(standard_result)
        
        # Regen88 processing  
        regen88_result = eval_game(pgn, mid=mid, tag=f"{tag}_r88", use_regen88=True)
        if regen88_result:
            regen88_rows.append(regen88_result)
    
    # Write summary files
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    
    # Standard results
    standard_json = os.path.join(OUT, f"entropy_pump_standard_{ts}.json")
    with open(standard_json, "w", encoding="utf-8") as f:
        f.write(json.dumps(standard_rows, indent=2))
    
    # Regen88 results
    regen88_json = os.path.join(OUT, f"entropy_pump_regen88_{ts}.json")
    with open(regen88_json, "w", encoding="utf-8") as f:
        f.write(json.dumps(regen88_rows, indent=2))
    
    # Combined TSV for comparison
    tsv_file = os.path.join(OUT, f"entropy_pump_comparison_{ts}.tsv")
    with open(tsv_file, "w", encoding="utf-8") as f:
        header = ["mode", "tag", "moves", "variance_reduction_pct", "compression", "mae_improvement_pct", "phi_clamp_rad"]
        regen88_header = ["regen88_enhanced", "flames_corrected", "healing_applied", "defense_layers_activated"]
        f.write("\t".join(header + regen88_header) + "\n")
        
        # Write standard results
        for r in standard_rows:
            if not r.get("ok", True): continue
            row_data = ["standard"] + [str(r.get(k, "")) for k in header[1:]]
            row_data.extend(["False", "0", "False", "0"])  # No Regen88 features
            f.write("\t".join(row_data) + "\n")
        
        # Write Regen88 results
        for r in regen88_rows:
            if not r.get("ok", True): continue
            row_data = ["regen88"] + [str(r.get(k, "")) for k in header[1:]]
            # Add Regen88 specific data
            regen88_data = [
                str(r.get("regen88_enhanced", False)),
                str(r.get("flames_corrected", 0)),
                str(r.get("healing_applied", False)),
                str(r.get("defense_layers_activated", 0))
            ]
            row_data.extend(regen88_data)
            f.write("\t".join(row_data) + "\n")
    
    # Generate enhanced summary with both modes
    from .results_evaluator import generate_summary_comment
    
    # Generate summaries for both modes
    standard_summary = generate_summary_comment(standard_rows, lucas_weights)
    regen88_summary = generate_summary_comment(regen88_rows, lucas_weights)
    
    # Create comprehensive comparison summary
    comparison_summary = f"""# Entropy Pump Analysis - Standard vs Regen88 Comparison

## Standard Codex Results
{standard_summary}

## Regen88 Enhanced Results  
{regen88_summary}

## Comparison Summary
- **Standard Mode**: Classic entropy pump with golden refraction
- **Regen88 Mode**: Enhanced with flame correction, self-healing, and recursive defense
- **Lucas Weights**: {lucas_weights}
- **Analysis Window**: Moves {mid[0]}-{mid[1]}

### Enhancement Statistics
"""
    
    # Add enhancement statistics
    if regen88_rows:
        total_games = len(regen88_rows)
        flames_corrected = sum(1 for r in regen88_rows if r.get("flames_corrected", 0) > 0)
        healing_applied = sum(1 for r in regen88_rows if r.get("healing_applied", False))
        defense_activated = sum(1 for r in regen88_rows if r.get("defense_layers_activated", 0) > 0)
        
        comparison_summary += f"""
- **Flame Corrections**: {flames_corrected}/{total_games} games
- **Self-Healing Applied**: {healing_applied}/{total_games} games  
- **Defense Activated**: {defense_activated}/{total_games} games
"""
    
    # Write comprehensive summary
    summary_file = os.path.join(OUT, f"entropy_pump_comparison_{ts}.md")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(comparison_summary)
    
    print(f"✅ Analysis complete!")
    print(f"📊 Standard results: {standard_json}")
    print(f"🚀 Regen88 results: {regen88_json}")
    print(f"📈 Comparison TSV: {tsv_file}")
    print(f"📝 Summary: {summary_file}")
    print(f"🖼️  Plots saved in {OUT}/")
    
    print("\n" + "="*80)
    print("COMPARISON SUMMARY")
    print("="*80)
    print(comparison_summary)


if __name__ == "__main__":
    main()