"""
Regen88 Codex: Flame Correction Engine
Advanced error correction and stability enhancement for entropy pump systems.
"""
import math
import numpy as np
from typing import Dict, Any, Tuple, Optional
from scripts.codex_entropy_pump import PHI, golden_refraction, _rank_to_phase


class FlameCorrection:
    """
    Flame Correction Engine for detecting and correcting entropy instabilities.
    
    The "flame" represents chaotic fluctuations that can destabilize the entropy pump.
    This engine detects these patterns and applies corrective measures.
    """
    
    def __init__(self, 
                 threshold: float = 0.15,
                 correction_strength: float = 0.8,
                 lucas_resonance: Tuple[int, int, int] = (4, 7, 11)):
        """
        Initialize the Flame Correction Engine.
        
        Args:
            threshold: Flame detection threshold (0-1)
            correction_strength: Strength of correction applied (0-1)
            lucas_resonance: Lucas weights for resonance correction
        """
        self.threshold = threshold
        self.correction_strength = correction_strength
        self.lucas_resonance = lucas_resonance
        
    def detect_flame_patterns(self, theta_series: np.ndarray) -> Dict[str, Any]:
        """
        Detect chaotic flame patterns in phase series.
        
        Args:
            theta_series: Phase series from entropy pump
            
        Returns:
            Detection results with flame locations and intensity
        """
        if len(theta_series) < 8:
            return {"flame_detected": False, "reason": "series too short"}
        
        # Calculate second-order differences to detect rapid oscillations
        deltas = np.diff(theta_series)
        second_deltas = np.diff(deltas)
        
        # Detect flame intensity using variance of second-order differences
        flame_intensity = float(np.var(second_deltas))
        flame_detected = flame_intensity > self.threshold
        
        # Find flame locations (high variance regions)
        window_size = min(8, len(second_deltas) // 4)
        flame_locations = []
        
        if window_size > 0:
            for i in range(len(second_deltas) - window_size + 1):
                window_var = float(np.var(second_deltas[i:i + window_size]))
                if window_var > self.threshold * 1.5:
                    flame_locations.append(i)
        
        return {
            "flame_detected": flame_detected,
            "flame_intensity": flame_intensity,
            "flame_locations": flame_locations,
            "detection_threshold": self.threshold,
            "series_length": len(theta_series)
        }
    
    def apply_flame_correction(self, 
                             theta_series: np.ndarray,
                             detection_results: Dict[str, Any]) -> np.ndarray:
        """
        Apply flame correction to stabilize chaotic regions.
        
        Args:
            theta_series: Original phase series
            detection_results: Results from flame detection
            
        Returns:
            Corrected phase series
        """
        if not detection_results["flame_detected"]:
            return theta_series.copy()
        
        corrected = theta_series.copy()
        flame_locations = detection_results["flame_locations"]
        
        # Apply Lucas resonance correction at flame locations
        a, b, c = self.lucas_resonance
        lucas_factor = (a + b + c) / math.sqrt(a * b * c)
        
        for loc in flame_locations:
            # Define correction window around flame location
            window_start = max(0, loc - 2)
            window_end = min(len(corrected), loc + 6)
            
            if window_end > window_start:
                window = corrected[window_start:window_end]
                
                # Apply golden ratio smoothing with Lucas enhancement
                smoothed = self._apply_golden_smoothing(window, lucas_factor)
                
                # Blend original and corrected based on correction strength
                blend_factor = self.correction_strength
                corrected[window_start:window_end] = (
                    blend_factor * smoothed + 
                    (1 - blend_factor) * window
                )
        
        return corrected
    
    def _apply_golden_smoothing(self, 
                               window: np.ndarray, 
                               lucas_factor: float) -> np.ndarray:
        """
        Apply golden ratio based smoothing to a window of phase values.
        
        Args:
            window: Phase values to smooth
            lucas_factor: Lucas resonance factor
            
        Returns:
            Smoothed phase values
        """
        if len(window) < 3:
            return window.copy()
        
        # Enhanced golden refraction with Lucas resonance
        enhanced_phi = PHI / lucas_factor
        
        # Apply enhanced refraction
        smoothed = golden_refraction(window, enhanced_phi)
        
        # Apply recursive smoothing for extreme values
        for i in range(1, len(smoothed) - 1):
            if abs(smoothed[i]) > abs(smoothed[i-1]) * 1.5 and abs(smoothed[i]) > abs(smoothed[i+1]) * 1.5:
                # Recursive correction for outliers
                smoothed[i] = (smoothed[i-1] + smoothed[i+1]) / 2.0 * (1.0 / PHI)
        
        return smoothed
    
    def full_correction_cycle(self, theta_series: np.ndarray) -> Dict[str, Any]:
        """
        Perform complete flame detection and correction cycle.
        
        Args:
            theta_series: Input phase series
            
        Returns:
            Complete correction results
        """
        # Initial detection
        detection = self.detect_flame_patterns(theta_series)
        
        # Apply correction if needed
        corrected_series = self.apply_flame_correction(theta_series, detection)
        
        # Verify correction effectiveness
        post_detection = self.detect_flame_patterns(corrected_series)
        
        # Calculate correction metrics
        correction_effectiveness = 0.0
        if detection["flame_detected"]:
            reduction = detection["flame_intensity"] - post_detection["flame_intensity"]
            correction_effectiveness = max(0.0, reduction / detection["flame_intensity"])
        
        return {
            "original_detection": detection,
            "corrected_series": corrected_series.tolist(),
            "post_correction_detection": post_detection,
            "correction_effectiveness": correction_effectiveness,
            "flames_corrected": len(detection["flame_locations"]),
            "stability_improvement": float(np.var(theta_series) - np.var(corrected_series))
        }


def integrate_flame_correction_with_entropy_pump(eval_series: np.ndarray,
                                               window: Optional[Tuple[int, int]] = None,
                                               n_index: float = PHI,
                                               lucas_weights: Optional[Tuple[int, int, int]] = None,
                                               enable_flame_correction: bool = True,
                                               flame_threshold: float = 0.15) -> Dict[str, Any]:
    """
    Enhanced entropy pump with integrated flame correction.
    
    Args:
        eval_series: Evaluation series
        window: Analysis window
        n_index: Refraction index
        lucas_weights: Lucas weights
        enable_flame_correction: Whether to enable flame correction
        flame_threshold: Flame detection threshold
        
    Returns:
        Enhanced entropy pump results with flame correction data
    """
    from scripts.codex_entropy_pump import codex_pump_from_series
    
    # Run standard entropy pump first
    base_result = codex_pump_from_series(eval_series, window, n_index, lucas_weights)
    
    if not base_result["ok"] or not enable_flame_correction:
        return base_result
    
    # Extract theta series for flame correction
    theta_series = np.array(base_result["theta_after"])
    
    # Initialize flame correction engine
    flame_engine = FlameCorrection(
        threshold=flame_threshold,
        correction_strength=0.8,
        lucas_resonance=lucas_weights or (4, 7, 11)
    )
    
    # Apply flame correction
    flame_results = flame_engine.full_correction_cycle(theta_series)
    
    # Enhance the base result with flame correction data
    enhanced_result = base_result.copy()
    enhanced_result.update({
        "regen88_enabled": True,
        "flame_correction": flame_results,
        "theta_after_corrected": flame_results["corrected_series"],
        "flame_stability_improvement": flame_results["stability_improvement"],
        "correction_effectiveness": flame_results["correction_effectiveness"]
    })
    
    return enhanced_result