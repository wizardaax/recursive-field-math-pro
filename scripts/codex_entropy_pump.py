# Codex entropy-pump: golden refraction + metrics
# Uses rank->phase mapping so it's scale-free and robust.
import math, numpy as np

PHI = (1 + 5**0.5) / 2

def _rank_to_phase(x: np.ndarray) -> np.ndarray:
    """Map real series -> phases in (-pi/2, pi/2) by ranks (no SciPy)."""
    n = len(x)
    order = np.argsort(x)
    ranks = np.empty(n, dtype=float)
    ranks[order] = np.arange(1, n + 1)
    u = ranks / (n + 1)                  # (0,1)
    return np.pi * (u - 0.5)             # (-pi/2, pi/2)

def golden_refraction(theta: np.ndarray, n: float = PHI) -> np.ndarray:
    s = np.sin(theta) / float(n)
    s = np.clip(s, -1.0, 1.0)
    return np.arcsin(s)

def codex_pump_from_series(eval_series: np.ndarray,
                           window: tuple[int,int] | None = None,
                           n_index: float = PHI,
                           lucas_weights: tuple[int,int,int] | None = None) -> dict:
    """
    eval_series: per-move evaluations (cp-like). We operate on deltas.
    window: (start, end) moves to analyze; default = whole series.
    n_index: refraction index (default φ).
    lucas_weights: optional (a,b,c). Effective n becomes n_index / f_lucas
                   where f = (a+b+c)/sqrt(a*b*c).
    Returns dict with metrics + arrays for plotting.
    """
    x = np.asarray(eval_series, dtype=float)
    if window:
        s, e = window
        xw = x[s:e].copy()
        offset = s
    else:
        xw = x.copy()
        offset = 0

    if len(xw) < 4:
        return {"ok": False, "reason": "too short"}

    deltas = np.diff(xw)                         # chaos lives here
    if np.allclose(np.var(deltas), 0.0):
        return {"ok": False, "reason": "zero variance"}

    theta = _rank_to_phase(deltas)

    # Lucas resonance (optional)
    if lucas_weights:
        a,b,c = lucas_weights
        f = (a + b + c) / math.sqrt(a*b*c)
        eff_n = n_index / f
    else:
        eff_n = n_index

    theta_p = golden_refraction(theta, eff_n)

    # Compression coefficient (fraction removed)
    var_before = float(np.var(theta))
    var_after  = float(np.var(theta_p))
    compression = 1.0 - (var_after / var_before)   # e.g., ~0.75

    # Reconstruct an adjusted delta stream by scaling
    # (keep mean, shrink swings by compression factor)
    shrink = compression
    deltas_adj = deltas * (1.0 - shrink)
    series_adj = np.concatenate([[xw[0]], xw[0] + np.cumsum(deltas_adj)])

    # φ-clamp angles for report
    phi_clamp = math.asin(1.0 / n_index)          # ≈ 0.666 rad
    # Histogram (for peaks near ±phi_clamp)
    hist_y, hist_edges = np.histogram(theta_p, bins=48, range=(-math.pi/2, math.pi/2))

    # Simple "baseline smoother" to compute MAE improvement (optional)
    def ma(x, k=5):
        if len(x) < k+1: return x
        kernel = np.ones(k)/k
        pad = np.concatenate([np.repeat(x[0], k-1), x])
        sm = np.convolve(pad, kernel, mode="valid")
        return sm[:len(x)]
    base_series = ma(xw, 5)
    mae_base = float(np.mean(np.abs(xw - base_series)))
    mae_codex = float(np.mean(np.abs(xw - series_adj)))
    mae_improve = 0.0 if mae_base == 0 else 100.0 * (mae_base - mae_codex) / mae_base

    return {
        "ok": True,
        "offset": offset,
        "window_len": len(xw),
        "var_delta_before": float(np.var(deltas)),
        "var_delta_after":  float(np.var(deltas_adj)),
        "variance_reduction_pct": 100.0 * (1.0 - np.var(deltas_adj)/np.var(deltas)),
        "compression": compression,
        "phi_clamp_rad": phi_clamp,
        "theta_after_hist": (hist_edges.tolist(), hist_y.tolist()),
        "mae_improvement_pct": mae_improve,
        "series_raw": xw.tolist(),
        "series_codex": series_adj.tolist(),
        "theta_after": theta_p.tolist(),
    }