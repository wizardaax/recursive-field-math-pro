"""
Regen88 Codex: Recursive Defense Modules
Advanced defense mechanisms against entropy degradation using recursive algorithms.
"""
import math
import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Callable
from scripts.codex_entropy_pump import PHI, golden_refraction, _rank_to_phase


class RecursiveDefenseCore:
    """
    Core recursive defense system for protecting entropy pump stability.
    
    Uses recursive algorithms inspired by Lucas sequences and golden ratio
    mathematics to create defensive barriers against chaos.
    """
    
    def __init__(self, 
                 defense_depth: int = 3,
                 lucas_sequence: Tuple[int, int, int] = (4, 7, 11),
                 protection_threshold: float = 0.2):
        """
        Initialize the recursive defense core.
        
        Args:
            defense_depth: Recursive depth for defense algorithms
            lucas_sequence: Lucas sequence parameters for defense
            protection_threshold: Threshold for activating defenses
        """
        self.defense_depth = defense_depth
        self.lucas_sequence = lucas_sequence
        self.protection_threshold = protection_threshold
        self.defense_activations = []
        
    def compute_recursive_barrier(self, 
                                 threat_series: np.ndarray, 
                                 depth: int = None) -> np.ndarray:
        """
        Compute recursive barrier against entropy threats.
        
        Args:
            threat_series: Series representing entropy threats
            depth: Recursive depth (uses instance default if None)
            
        Returns:
            Barrier strength series
        """
        if depth is None:
            depth = self.defense_depth
            
        if depth == 0 or len(threat_series) < 2:
            return np.ones_like(threat_series) / PHI
        
        # Base case: simple golden ratio barrier
        if depth == 1:
            return self._golden_barrier(threat_series)
        
        # Recursive case: combine barriers at different scales
        # Split series for recursive processing
        mid = len(threat_series) // 2
        if mid < 1:
            return self._golden_barrier(threat_series)
        
        left_threats = threat_series[:mid]
        right_threats = threat_series[mid:]
        
        # Recursive barrier computation
        left_barrier = self.compute_recursive_barrier(left_threats, depth - 1)
        right_barrier = self.compute_recursive_barrier(right_threats, depth - 1)
        
        # Combine barriers with Lucas sequence weighting
        a, b, c = self.lucas_sequence
        lucas_weights = self._generate_lucas_weights(len(threat_series), a, b, c)
        
        combined_barrier = np.concatenate([left_barrier, right_barrier])
        enhanced_barrier = combined_barrier * lucas_weights
        
        # Apply golden ratio normalization
        max_barrier = np.max(enhanced_barrier)
        if max_barrier > 0:
            enhanced_barrier = enhanced_barrier * (1.0 / PHI) / max_barrier
        
        return enhanced_barrier
    
    def _golden_barrier(self, threat_series: np.ndarray) -> np.ndarray:
        """
        Create golden ratio based defensive barrier.
        
        Args:
            threat_series: Threat data
            
        Returns:
            Golden barrier strengths
        """
        # Map threats to phase space
        threat_phases = _rank_to_phase(threat_series)
        
        # Apply golden refraction for defense
        defended_phases = golden_refraction(threat_phases, PHI)
        
        # Convert back to barrier strengths (inverse of threat intensity)
        barrier_strengths = 1.0 / (1.0 + np.abs(defended_phases))
        
        return barrier_strengths
    
    def _generate_lucas_weights(self, length: int, a: int, b: int, c: int) -> np.ndarray:
        """
        Generate Lucas sequence based weights for defense.
        
        Args:
            length: Required length of weights
            a, b, c: Lucas sequence parameters
            
        Returns:
            Lucas weighted defense factors
        """
        if length <= 0:
            return np.array([])
        
        # Generate Lucas-like sequence
        weights = np.zeros(length)
        if length >= 1:
            weights[0] = a
        if length >= 2:
            weights[1] = b
        if length >= 3:
            weights[2] = c
        
        # Generate remaining weights using Lucas recurrence
        for i in range(3, length):
            weights[i] = weights[i-1] + weights[i-2] + weights[i-3]
        
        # Normalize with golden ratio
        if np.max(weights) > 0:
            weights = weights / np.max(weights) * (1.0 / PHI)
        
        return weights
    
    def analyze_threat_level(self, entropy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze threat level from entropy data.
        
        Args:
            entropy_data: Entropy pump data
            
        Returns:
            Threat analysis results
        """
        threat_indicators = []
        threat_score = 0.0
        
        # Analyze variance instability
        var_before = entropy_data.get("var_delta_before", 0)
        var_after = entropy_data.get("var_delta_after", 0)
        if var_before > 0:
            var_ratio = var_after / var_before
            if var_ratio > 0.8:  # Poor variance reduction
                threat_indicators.append("high_variance_threat")
                threat_score += (var_ratio - 0.5) / 0.5
        
        # Analyze compression degradation
        compression = entropy_data.get("compression", 0)
        if compression < 0.3:
            threat_indicators.append("compression_threat")
            threat_score += (0.3 - compression) / 0.3
        
        # Analyze phi-clamp instability
        phi_clamp = entropy_data.get("phi_clamp_rad", 0)
        expected_phi = math.asin(1.0 / PHI)
        phi_deviation = abs(phi_clamp - expected_phi) / expected_phi
        if phi_deviation > 0.15:
            threat_indicators.append("phi_instability_threat")
            threat_score += phi_deviation
        
        # Check for series anomalies
        theta_after = entropy_data.get("theta_after", [])
        if theta_after:
            theta_array = np.array(theta_after)
            theta_variance = float(np.var(theta_array))
            if theta_variance > 0.5:
                threat_indicators.append("theta_chaos_threat")
                threat_score += theta_variance
        
        threat_level = min(1.0, threat_score)
        defense_required = threat_level > self.protection_threshold
        
        return {
            "threat_level": threat_level,
            "defense_required": defense_required,
            "threat_indicators": threat_indicators,
            "threat_score": threat_score,
            "protection_threshold": self.protection_threshold
        }
    
    def activate_recursive_defense(self, 
                                 entropy_data: Dict[str, Any],
                                 threat_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Activate recursive defense mechanisms.
        
        Args:
            entropy_data: Entropy data to protect
            threat_analysis: Threat analysis results
            
        Returns:
            Defense activation results
        """
        if not threat_analysis["defense_required"]:
            return {
                "defense_activated": False,
                "reason": "no_threat_detected",
                "protected_data": entropy_data
            }
        
        # Extract threat series
        theta_after = np.array(entropy_data.get("theta_after", []))
        if len(theta_after) == 0:
            return {
                "defense_activated": False,
                "reason": "no_data_to_protect",
                "protected_data": entropy_data
            }
        
        # Compute recursive barrier
        barrier = self.compute_recursive_barrier(theta_after)
        
        # Apply defensive transformation
        protected_theta = self._apply_defensive_transform(theta_after, barrier)
        
        # Create protected entropy data
        protected_data = entropy_data.copy()
        protected_data["theta_after"] = protected_theta.tolist()
        protected_data["recursive_defense"] = {
            "barrier_strength": barrier.tolist(),
            "defense_depth": self.defense_depth,
            "lucas_sequence": self.lucas_sequence,
            "threat_level": threat_analysis["threat_level"]
        }
        
        # Record activation
        activation_record = {
            "threat_level": threat_analysis["threat_level"],
            "defense_depth": self.defense_depth,
            "protection_effectiveness": self._calculate_protection_effectiveness(theta_after, protected_theta)
        }
        self.defense_activations.append(activation_record)
        
        return {
            "defense_activated": True,
            "protection_effectiveness": activation_record["protection_effectiveness"],
            "barrier_strength": float(np.mean(barrier)),
            "protected_data": protected_data
        }
    
    def _apply_defensive_transform(self, 
                                 original_series: np.ndarray, 
                                 barrier: np.ndarray) -> np.ndarray:
        """
        Apply defensive transformation to protect series.
        
        Args:
            original_series: Original series to protect
            barrier: Defensive barrier strengths
            
        Returns:
            Protected series
        """
        # Ensure barrier and series have same length
        min_length = min(len(original_series), len(barrier))
        series = original_series[:min_length]
        barrier_strengths = barrier[:min_length]
        
        # Apply barrier protection
        protected = series.copy()
        for i in range(len(protected)):
            # Stronger barriers provide more stability
            stability_factor = barrier_strengths[i]
            
            # Apply golden ratio based protection
            if abs(series[i]) > stability_factor:
                protected[i] = series[i] * stability_factor * (1.0 / PHI)
            else:
                protected[i] = series[i] * (1.0 + stability_factor * (1.0 - 1.0/PHI))
        
        return protected
    
    def _calculate_protection_effectiveness(self, 
                                          original: np.ndarray, 
                                          protected: np.ndarray) -> float:
        """
        Calculate effectiveness of protection.
        
        Args:
            original: Original series
            protected: Protected series
            
        Returns:
            Protection effectiveness (0-1)
        """
        if len(original) == 0 or len(protected) == 0:
            return 0.0
        
        original_variance = float(np.var(original))
        protected_variance = float(np.var(protected))
        
        if original_variance == 0:
            return 1.0 if protected_variance == 0 else 0.0
        
        variance_reduction = (original_variance - protected_variance) / original_variance
        return max(0.0, min(1.0, variance_reduction))


class MultiLayerDefense:
    """
    Multi-layer recursive defense system with cascading protection.
    """
    
    def __init__(self, defense_layers: int = 3):
        """
        Initialize multi-layer defense.
        
        Args:
            defense_layers: Number of defense layers
        """
        self.defense_layers = defense_layers
        self.layers = []
        
        # Create defense layers with increasing depth and different Lucas parameters
        lucas_variants = [(4, 7, 11), (3, 5, 8), (2, 3, 5), (1, 1, 2)]
        for i in range(defense_layers):
            lucas_seq = lucas_variants[i % len(lucas_variants)]
            layer = RecursiveDefenseCore(
                defense_depth=i + 2,
                lucas_sequence=lucas_seq,
                protection_threshold=0.1 + i * 0.05
            )
            self.layers.append(layer)
    
    def activate_layered_defense(self, entropy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Activate all defense layers in sequence.
        
        Args:
            entropy_data: Data to protect
            
        Returns:
            Multi-layer defense results
        """
        current_data = entropy_data.copy()
        layer_results = []
        
        for i, layer in enumerate(self.layers):
            # Analyze threats for this layer
            threat_analysis = layer.analyze_threat_level(current_data)
            
            # Activate defense if needed
            defense_result = layer.activate_recursive_defense(current_data, threat_analysis)
            
            layer_results.append({
                "layer": i + 1,
                "threat_analysis": threat_analysis,
                "defense_result": defense_result
            })
            
            # Use protected data for next layer
            if defense_result["defense_activated"]:
                current_data = defense_result["protected_data"]
        
        # Calculate overall protection effectiveness
        original_theta = np.array(entropy_data.get("theta_after", []))
        final_theta = np.array(current_data.get("theta_after", []))
        
        overall_effectiveness = 0.0
        if len(original_theta) > 0 and len(final_theta) > 0:
            original_var = float(np.var(original_theta))
            final_var = float(np.var(final_theta))
            if original_var > 0:
                overall_effectiveness = max(0.0, (original_var - final_var) / original_var)
        
        return {
            "multi_layer_defense": True,
            "layers_activated": sum(1 for lr in layer_results if lr["defense_result"]["defense_activated"]),
            "layer_results": layer_results,
            "overall_effectiveness": overall_effectiveness,
            "final_protected_data": current_data
        }


def integrate_recursive_defense(entropy_result: Dict[str, Any],
                              defense_layers: int = 3,
                              enable_multi_layer: bool = True) -> Dict[str, Any]:
    """
    Integrate recursive defense with entropy pump results.
    
    Args:
        entropy_result: Entropy pump result to protect
        defense_layers: Number of defense layers
        enable_multi_layer: Whether to use multi-layer defense
        
    Returns:
        Enhanced result with recursive defense protection
    """
    if not entropy_result.get("ok", False):
        return entropy_result
    
    if enable_multi_layer:
        # Use multi-layer defense system
        defense_system = MultiLayerDefense(defense_layers)
        defense_result = defense_system.activate_layered_defense(entropy_result)
        
        # Merge results
        enhanced_result = defense_result["final_protected_data"].copy()
        enhanced_result["recursive_defense_multi_layer"] = defense_result
        
    else:
        # Use single layer defense
        defense_core = RecursiveDefenseCore()
        threat_analysis = defense_core.analyze_threat_level(entropy_result)
        defense_result = defense_core.activate_recursive_defense(entropy_result, threat_analysis)
        
        # Merge results
        enhanced_result = defense_result["protected_data"].copy()
        enhanced_result["recursive_defense_single"] = defense_result
    
    return enhanced_result