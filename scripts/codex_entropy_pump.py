# Codex entropy-pump: golden refraction + metrics
# Uses rank->phase mapping so it's scale-free and robust.
import math, numpy as np

PHI = (1 + 5**0.5) / 2

# Import flame correction engine
try:
    from .flame_correction import flame_correction_engine, apply_flame_correction_to_series
    FLAME_CORRECTION_AVAILABLE = True
except ImportError:
    FLAME_CORRECTION_AVAILABLE = False

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
                           lucas_weights: tuple[int,int,int] | None = None,
                           enable_flame_correction: bool = False,
                           flame_correction_params: dict | None = None) -> dict:
    """
    eval_series: per-move evaluations (cp-like). We operate on deltas.
    window: (start, end) moves to analyze; default = whole series.
    n_index: refraction index (default φ).
    lucas_weights: optional (a,b,c). Effective n becomes n_index / f_lucas
                   where f = (a+b+c)/sqrt(a*b*c).
    enable_flame_correction: whether to apply Regen88 flame correction engine.
    flame_correction_params: parameters for flame correction (optional).
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

    # Apply Regen88 Flame Correction Engine (optional)
    flame_correction_result = None
    if enable_flame_correction and FLAME_CORRECTION_AVAILABLE:
        # Set default flame correction parameters
        default_params = {
            "enable_flame_detection": True,
            "enable_regen88": True,
            "flame_threshold": 2.5,
            "regen_factor": 88.0,
            "iterations": 3
        }
        
        # Override with user-provided parameters
        if flame_correction_params:
            default_params.update(flame_correction_params)
        
        # Apply flame correction to the φ-refracted data
        flame_correction_result = apply_flame_correction_to_series(
            theta_p, deltas, xw[0], 0.0, **default_params
        )
        
        # Use flame-corrected theta for subsequent calculations
        theta_p_corrected = flame_correction_result["theta_corrected"]
        deltas_flame_corrected = flame_correction_result["deltas_corrected"]
        series_flame_corrected = flame_correction_result["series_corrected"]
    else:
        theta_p_corrected = theta_p
        deltas_flame_corrected = None
        series_flame_corrected = None

    # Compression coefficient (fraction removed) - use corrected theta if available
    var_before = float(np.var(theta))
    var_after  = float(np.var(theta_p_corrected))
    compression = 1.0 - (var_after / var_before)   # e.g., ~0.75

    # Reconstruct an adjusted delta stream by scaling
    # (keep mean, shrink swings by compression factor)
    # Use flame-corrected deltas if available, otherwise use standard compression
    if enable_flame_correction and deltas_flame_corrected is not None:
        deltas_adj = deltas_flame_corrected
        series_adj = series_flame_corrected
    else:
        shrink = compression
        deltas_adj = deltas * (1.0 - shrink)
        series_adj = np.concatenate([[xw[0]], xw[0] + np.cumsum(deltas_adj)])

    # φ-clamp angles for report (use corrected theta)
    phi_clamp = math.asin(1.0 / eff_n)          # ≈ 0.666 rad
    # Histogram (for peaks near ±phi_clamp) - use corrected theta
    hist_y, hist_edges = np.histogram(theta_p_corrected, bins=48, range=(-math.pi/2, math.pi/2))

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

    # Build result dictionary
    result = {
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
        "theta_after": theta_p_corrected.tolist(),
        "flame_correction_enabled": enable_flame_correction and FLAME_CORRECTION_AVAILABLE,
    }
    
    # Add flame correction specific data if applied
    if enable_flame_correction and flame_correction_result is not None:
        result.update({
            "flames_detected": flame_correction_result["flames_detected"],
            "flame_correction_strength": flame_correction_result["correction_strength"],
            "flame_variance_reduction_pct": flame_correction_result["variance_reduction_pct"],
            "regen88_applied": flame_correction_result["regen88_applied"],
            "theta_before_correction": theta_p.tolist(),
        })
    
    return result