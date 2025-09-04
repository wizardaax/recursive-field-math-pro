"""
Regen88 Codex: Entropy Self-Healing System
Automatic detection and correction of entropy degradation with recursive healing.
"""
import math
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from scripts.codex_entropy_pump import PHI, golden_refraction, _rank_to_phase


class EntropySelfHealing:
    """
    Self-healing system for entropy pump degradation.
    
    Monitors entropy pump performance and automatically applies healing
    mechanisms when degradation is detected.
    """
    
    def __init__(self, 
                 degradation_threshold: float = 0.1,
                 healing_iterations: int = 3,
                 lucas_weights: Tuple[int, int, int] = (4, 7, 11)):
        """
        Initialize the entropy self-healing system.
        
        Args:
            degradation_threshold: Threshold for detecting entropy degradation
            healing_iterations: Maximum healing iterations to attempt
            lucas_weights: Lucas weights for healing resonance
        """
        self.degradation_threshold = degradation_threshold
        self.healing_iterations = healing_iterations
        self.lucas_weights = lucas_weights
        self.healing_history = []
        
    def detect_entropy_degradation(self, entropy_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect entropy degradation in pump metrics.
        
        Args:
            entropy_metrics: Current entropy pump metrics
            
        Returns:
            Degradation detection results
        """
        degradation_indicators = []
        degradation_score = 0.0
        
        # Check variance reduction effectiveness
        var_reduction = entropy_metrics.get("variance_reduction_pct", 0)
        if var_reduction < 20.0:  # Below acceptance threshold
            degradation_indicators.append("low_variance_reduction")
            degradation_score += (20.0 - var_reduction) / 20.0
        
        # Check compression coefficient
        compression = entropy_metrics.get("compression", 0)
        if compression < 0.5:  # Low compression indicates poor performance
            degradation_indicators.append("low_compression")
            degradation_score += (0.5 - compression) / 0.5
        
        # Check phi-clamp stability
        phi_clamp = entropy_metrics.get("phi_clamp_rad", 0)
        expected_phi_clamp = math.asin(1.0 / PHI)
        phi_deviation = abs(phi_clamp - expected_phi_clamp) / expected_phi_clamp
        if phi_deviation > 0.1:  # More than 10% deviation
            degradation_indicators.append("phi_clamp_deviation")
            degradation_score += phi_deviation
        
        # Check MAE improvement
        mae_improvement = entropy_metrics.get("mae_improvement_pct", 0)
        if mae_improvement < 2.0:  # Below acceptance threshold
            degradation_indicators.append("poor_mae_improvement")
            degradation_score += (2.0 - mae_improvement) / 2.0
        
        degradation_detected = degradation_score > self.degradation_threshold
        
        return {
            "degradation_detected": degradation_detected,
            "degradation_score": degradation_score,
            "degradation_indicators": degradation_indicators,
            "threshold": self.degradation_threshold
        }
    
    def apply_recursive_healing(self, 
                              theta_series: np.ndarray,
                              degradation_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply recursive healing to entropy series.
        
        Args:
            theta_series: Original theta series
            degradation_info: Degradation detection results
            
        Returns:
            Healing results with improved series
        """
        if not degradation_info["degradation_detected"]:
            return {
                "healing_applied": False,
                "healed_series": theta_series.tolist(),
                "healing_iterations": 0,
                "healing_effectiveness": 0.0
            }
        
        healed_series = theta_series.copy()
        original_variance = float(np.var(theta_series))
        
        healing_log = []
        
        for iteration in range(self.healing_iterations):
            # Apply Lucas-enhanced golden refraction
            a, b, c = self.lucas_weights
            lucas_factor = (a + b + c) / math.sqrt(a * b * c)
            enhanced_phi = PHI * lucas_factor
            
            # Recursive healing pass
            healed_series = self._recursive_healing_pass(healed_series, enhanced_phi, iteration)
            
            # Check improvement
            current_variance = float(np.var(healed_series))
            improvement = (original_variance - current_variance) / original_variance
            
            healing_log.append({
                "iteration": iteration + 1,
                "variance": current_variance,
                "improvement": improvement
            })
            
            # Stop if sufficient healing achieved
            if improvement > 0.3:  # 30% improvement threshold
                break
        
        final_variance = float(np.var(healed_series))
        healing_effectiveness = (original_variance - final_variance) / original_variance
        
        return {
            "healing_applied": True,
            "healed_series": healed_series.tolist(),
            "healing_iterations": len(healing_log),
            "healing_effectiveness": healing_effectiveness,
            "healing_log": healing_log,
            "original_variance": original_variance,
            "final_variance": final_variance
        }
    
    def _recursive_healing_pass(self, 
                               series: np.ndarray, 
                               enhanced_phi: float, 
                               iteration: int) -> np.ndarray:
        """
        Single recursive healing pass.
        
        Args:
            series: Series to heal
            enhanced_phi: Enhanced phi value for refraction
            iteration: Current iteration number
            
        Returns:
            Healed series after one pass
        """
        # Apply golden refraction with enhanced phi
        healed = golden_refraction(series, enhanced_phi)
        
        # Recursive stabilization based on iteration
        stabilization_factor = 1.0 / (PHI ** (iteration + 1))
        
        # Apply local smoothing for outliers
        for i in range(1, len(healed) - 1):
            local_mean = (healed[i-1] + healed[i+1]) / 2.0
            deviation = abs(healed[i] - local_mean)
            
            # If deviation is large, apply recursive correction
            if deviation > stabilization_factor:
                correction = local_mean * (1.0 / PHI)
                blend_factor = min(0.5, deviation / (2 * stabilization_factor))
                healed[i] = (1 - blend_factor) * healed[i] + blend_factor * correction
        
        return healed
    
    def monitor_and_heal(self, entropy_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete monitoring and healing cycle.
        
        Args:
            entropy_result: Entropy pump result to monitor and heal
            
        Returns:
            Enhanced result with self-healing applied
        """
        if not entropy_result.get("ok", False):
            return entropy_result
        
        # Detect degradation
        degradation = self.detect_entropy_degradation(entropy_result)
        
        # Apply healing if needed
        theta_series = np.array(entropy_result.get("theta_after", []))
        healing_result = self.apply_recursive_healing(theta_series, degradation)
        
        # Update healing history
        self.healing_history.append({
            "degradation_detected": degradation["degradation_detected"],
            "healing_applied": healing_result["healing_applied"],
            "effectiveness": healing_result["healing_effectiveness"]
        })
        
        # Enhanced result with self-healing data
        enhanced_result = entropy_result.copy()
        enhanced_result.update({
            "self_healing": {
                "degradation_detection": degradation,
                "healing_result": healing_result,
                "healing_history_length": len(self.healing_history)
            }
        })
        
        # Replace theta_after with healed version if healing was applied
        if healing_result["healing_applied"]:
            enhanced_result["theta_after"] = healing_result["healed_series"]
            enhanced_result["self_healing_applied"] = True
        else:
            enhanced_result["self_healing_applied"] = False
        
        return enhanced_result
    
    def get_healing_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about healing performance.
        
        Returns:
            Healing performance statistics
        """
        if not self.healing_history:
            return {
                "total_sessions": 0,
                "healing_rate": 0.0,
                "average_effectiveness": 0.0
            }
        
        total_sessions = len(self.healing_history)
        healing_sessions = sum(1 for h in self.healing_history if h["healing_applied"])
        degradation_sessions = sum(1 for h in self.healing_history if h["degradation_detected"])
        
        healing_rate = healing_sessions / max(1, degradation_sessions)
        
        effectiveness_values = [h["effectiveness"] for h in self.healing_history if h["healing_applied"]]
        average_effectiveness = np.mean(effectiveness_values) if effectiveness_values else 0.0
        
        return {
            "total_sessions": total_sessions,
            "degradation_sessions": degradation_sessions,
            "healing_sessions": healing_sessions,
            "healing_rate": healing_rate,
            "average_effectiveness": float(average_effectiveness),
            "max_effectiveness": float(max(effectiveness_values)) if effectiveness_values else 0.0
        }


class AdaptiveHealing:
    """
    Adaptive healing system that learns from healing patterns.
    """
    
    def __init__(self, base_healer: EntropySelfHealing):
        """
        Initialize adaptive healing wrapper.
        
        Args:
            base_healer: Base self-healing system
        """
        self.base_healer = base_healer
        self.adaptation_history = []
        
    def adaptive_heal(self, entropy_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply adaptive healing that learns from previous sessions.
        
        Args:
            entropy_result: Entropy result to heal
            
        Returns:
            Adaptively healed result
        """
        # Get healing statistics to adapt parameters
        stats = self.base_healer.get_healing_statistics()
        
        # Adapt threshold based on healing effectiveness
        if stats["average_effectiveness"] < 0.2:  # Low effectiveness
            self.base_healer.degradation_threshold *= 0.9  # Lower threshold (more sensitive)
        elif stats["average_effectiveness"] > 0.6:  # High effectiveness
            self.base_healer.degradation_threshold *= 1.1  # Raise threshold (less sensitive)
        
        # Ensure threshold stays in reasonable bounds
        self.base_healer.degradation_threshold = max(0.05, min(0.3, self.base_healer.degradation_threshold))
        
        # Apply healing with adapted parameters
        result = self.base_healer.monitor_and_heal(entropy_result)
        
        # Record adaptation
        self.adaptation_history.append({
            "threshold_used": self.base_healer.degradation_threshold,
            "effectiveness": stats.get("average_effectiveness", 0.0)
        })
        
        # Add adaptation info to result
        result["adaptive_healing"] = {
            "adapted_threshold": self.base_healer.degradation_threshold,
            "adaptation_count": len(self.adaptation_history)
        }
        
        return result