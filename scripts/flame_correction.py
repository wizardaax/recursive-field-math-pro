# Regen88 Codex Flame Correction Engine
# Provides outlier correction and regenerative smoothing for φ-refracted data
import math
import numpy as np
from typing import Optional, Dict, Any

# Regen88 constants
REGEN88_FACTOR = 88.0  # Regenerative smoothing factor
FLAME_THRESHOLD = 2.5  # Standard deviations for flame detection
REGEN_ITERATIONS = 3   # Number of regenerative correction cycles


def detect_flames(theta_data: np.ndarray, threshold: float = FLAME_THRESHOLD) -> np.ndarray:
    """
    Detect 'flames' (outliers) in the φ-refracted angle data.
    
    Args:
        theta_data: Array of φ-refracted angles
        threshold: Number of standard deviations to consider as flame
        
    Returns:
        Boolean array marking flame positions
    """
    if len(theta_data) < 3:
        return np.zeros(len(theta_data), dtype=bool)
    
    # Use robust statistics for flame detection
    median = np.median(theta_data)
    mad = np.median(np.abs(theta_data - median))  # Median Absolute Deviation
    
    # Convert MAD to standard deviation equivalent
    sigma_equiv = mad * 1.4826  # MAD to std conversion factor
    
    if sigma_equiv == 0:
        return np.zeros(len(theta_data), dtype=bool)
    
    # Mark points that are more than threshold standard deviations from median
    z_scores = np.abs(theta_data - median) / sigma_equiv
    return z_scores > threshold


def regen88_smooth(data: np.ndarray, factor: float = REGEN88_FACTOR) -> np.ndarray:
    """
    Apply Regen88 regenerative smoothing algorithm.
    
    The algorithm uses a weighted regenerative filter that reduces
    high-frequency noise while preserving the underlying signal structure.
    
    Args:
        data: Input data array
        factor: Regenerative factor (higher = more smoothing)
        
    Returns:
        Smoothed data array
    """
    if len(data) < 2:
        return data.copy()
    
    smoothed = data.copy()
    alpha = 1.0 / (1.0 + factor / 88.0)  # Adaptive smoothing parameter
    
    # Forward pass
    for i in range(1, len(smoothed)):
        smoothed[i] = alpha * smoothed[i] + (1 - alpha) * smoothed[i-1]
    
    # Backward pass for symmetry
    for i in range(len(smoothed) - 2, -1, -1):
        smoothed[i] = alpha * smoothed[i] + (1 - alpha) * smoothed[i+1]
    
    return smoothed


def flame_correction_engine(theta_refracted: np.ndarray,
                          enable_flame_detection: bool = True,
                          enable_regen88: bool = True,
                          flame_threshold: float = FLAME_THRESHOLD,
                          regen_factor: float = REGEN88_FACTOR,
                          iterations: int = REGEN_ITERATIONS) -> Dict[str, Any]:
    """
    Apply Regen88 Codex Flame Correction Engine to φ-refracted data.
    
    Args:
        theta_refracted: φ-refracted angle data from entropy pump
        enable_flame_detection: Whether to detect and correct flames
        enable_regen88: Whether to apply regenerative smoothing
        flame_threshold: Threshold for flame detection (std devs)
        regen_factor: Regenerative smoothing factor
        iterations: Number of correction iterations
        
    Returns:
        Dict containing corrected data and correction metrics
    """
    if len(theta_refracted) == 0:
        return {
            "theta_corrected": theta_refracted.copy(),
            "flames_detected": 0,
            "correction_strength": 0.0,
            "variance_reduction_pct": 0.0,
            "regen88_applied": False,
            "flame_detection_applied": False
        }
    
    theta_corrected = theta_refracted.copy()
    total_flames = 0
    original_variance = float(np.var(theta_refracted))
    
    # Apply iterative correction
    for iteration in range(iterations):
        if enable_flame_detection:
            # Detect flames in current data
            flame_mask = detect_flames(theta_corrected, flame_threshold)
            flames_in_iteration = np.sum(flame_mask)
            total_flames += flames_in_iteration
            
            # Correct flames using interpolation
            if flames_in_iteration > 0:
                # Create corrected version by interpolating flame points
                corrected_iter = theta_corrected.copy()
                flame_indices = np.where(flame_mask)[0]
                
                for idx in flame_indices:
                    # Find nearest non-flame neighbors for interpolation
                    left_idx = idx - 1
                    right_idx = idx + 1
                    
                    # Find valid left neighbor
                    while left_idx >= 0 and flame_mask[left_idx]:
                        left_idx -= 1
                    
                    # Find valid right neighbor  
                    while right_idx < len(flame_mask) and flame_mask[right_idx]:
                        right_idx += 1
                    
                    # Interpolate flame value
                    if left_idx >= 0 and right_idx < len(theta_corrected):
                        # Linear interpolation between neighbors
                        weight = (idx - left_idx) / (right_idx - left_idx)
                        corrected_iter[idx] = (1 - weight) * theta_corrected[left_idx] + \
                                            weight * theta_corrected[right_idx]
                    elif left_idx >= 0:
                        # Use left neighbor
                        corrected_iter[idx] = theta_corrected[left_idx]
                    elif right_idx < len(theta_corrected):
                        # Use right neighbor
                        corrected_iter[idx] = theta_corrected[right_idx]
                    # If no valid neighbors, keep original value
                
                theta_corrected = corrected_iter
        
        # Apply Regen88 smoothing
        if enable_regen88:
            theta_corrected = regen88_smooth(theta_corrected, regen_factor)
    
    # Calculate correction metrics
    final_variance = float(np.var(theta_corrected))
    variance_reduction = 0.0
    if original_variance > 0:
        variance_reduction = 100.0 * (1.0 - final_variance / original_variance)
    
    # Correction strength metric (RMS difference from original)
    correction_strength = float(np.sqrt(np.mean((theta_corrected - theta_refracted) ** 2)))
    
    return {
        "theta_corrected": theta_corrected,
        "flames_detected": int(total_flames),
        "correction_strength": correction_strength,
        "variance_reduction_pct": variance_reduction,
        "regen88_applied": enable_regen88,
        "flame_detection_applied": enable_flame_detection,
        "original_variance": original_variance,
        "corrected_variance": final_variance
    }


def apply_flame_correction_to_series(theta_refracted: np.ndarray,
                                   deltas_original: np.ndarray,
                                   series_baseline: float,
                                   compression_factor: float,
                                   **correction_kwargs) -> Dict[str, Any]:
    """
    Apply flame correction and reconstruct the corrected evaluation series.
    
    This function integrates with the entropy pump output to provide
    a corrected evaluation series based on flame-corrected θ values.
    
    Args:
        theta_refracted: φ-refracted angles from entropy pump
        deltas_original: Original delta series
        series_baseline: Baseline value for series reconstruction  
        compression_factor: Compression factor from entropy pump
        **correction_kwargs: Arguments for flame_correction_engine
        
    Returns:
        Dict with corrected series and metrics
    """
    # Apply flame correction to the refracted angles
    correction_result = flame_correction_engine(theta_refracted, **correction_kwargs)
    theta_corrected = correction_result["theta_corrected"]
    
    # Reconstruct corrected delta series
    # Map corrected angles back to delta space using inverse rank mapping
    if len(theta_corrected) > 1 and len(deltas_original) > 0:
        # Note: theta_corrected typically has one more element than deltas_original
        # because it represents angles for each delta point
        # We need to map the corrected angles back to delta magnitudes
        
        # Calculate correction scale factor based on variance reduction
        original_theta_var = np.var(theta_refracted) if len(theta_refracted) > 1 else 1.0
        corrected_theta_var = np.var(theta_corrected) if len(theta_corrected) > 1 else 1.0
        
        if original_theta_var > 0:
            theta_correction_factor = np.sqrt(corrected_theta_var / original_theta_var)
        else:
            theta_correction_factor = 1.0
        
        # Apply flame correction scaling to original deltas along with compression
        total_correction = (1.0 - compression_factor) * theta_correction_factor
        deltas_corrected = deltas_original * total_correction
        
        # Reconstruct series
        series_corrected = np.concatenate([[series_baseline], 
                                         series_baseline + np.cumsum(deltas_corrected)])
    else:
        deltas_corrected = deltas_original.copy() if len(deltas_original) > 0 else np.array([])
        series_corrected = np.array([series_baseline])
    
    # Combine results
    result = correction_result.copy()
    result.update({
        "deltas_corrected": deltas_corrected,
        "series_corrected": series_corrected,
        "delta_variance_reduction_pct": 0.0
    })
    
    # Calculate delta variance reduction
    if len(deltas_original) > 0 and len(deltas_corrected) > 0:
        orig_delta_var = np.var(deltas_original)
        corr_delta_var = np.var(deltas_corrected)
        if orig_delta_var > 0:
            result["delta_variance_reduction_pct"] = 100.0 * (1.0 - corr_delta_var / orig_delta_var)
    
    return result