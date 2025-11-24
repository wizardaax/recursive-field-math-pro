"""
Regen88 Codex: Complete Integration Module
Unified interface for the enhanced entropy pump with flame correction,
self-healing, and recursive defense capabilities.
"""
import math
import numpy as np
from typing import Dict, Any, Tuple, Optional
from scripts.codex_entropy_pump import codex_pump_from_series, PHI
from scripts.regen88_flame_correction import integrate_flame_correction_with_entropy_pump, FlameCorrection
from scripts.regen88_entropy_healing import EntropySelfHealing, AdaptiveHealing
from scripts.regen88_recursive_defense import integrate_recursive_defense, MultiLayerDefense


class Regen88Codex:
    """
    Complete Regen88 Codex system integrating all enhancement modules.
    
    This is the main interface for the enhanced entropy pump with:
    - Flame Correction Engine
    - Entropy Self-Healing
    - Recursive Defense Modules
    - Comprehensive monitoring and reporting
    """
    
    def __init__(self, 
                 enable_flame_correction: bool = True,
                 enable_self_healing: bool = True,
                 enable_recursive_defense: bool = True,
                 flame_threshold: float = 0.15,
                 healing_threshold: float = 0.1,
                 defense_layers: int = 3,
                 lucas_weights: Tuple[int, int, int] = (4, 7, 11)):
        """
        Initialize the complete Regen88 Codex system.
        
        Args:
            enable_flame_correction: Enable flame correction engine
            enable_self_healing: Enable entropy self-healing
            enable_recursive_defense: Enable recursive defense modules
            flame_threshold: Threshold for flame detection
            healing_threshold: Threshold for healing activation
            defense_layers: Number of recursive defense layers
            lucas_weights: Lucas weights for all modules
        """
        self.enable_flame_correction = enable_flame_correction
        self.enable_self_healing = enable_self_healing
        self.enable_recursive_defense = enable_recursive_defense
        self.lucas_weights = lucas_weights
        
        # Initialize subsystems
        self.flame_engine = FlameCorrection(
            threshold=flame_threshold,
            correction_strength=0.8,
            lucas_resonance=lucas_weights
        ) if enable_flame_correction else None
        
        self.healing_system = AdaptiveHealing(
            EntropySelfHealing(
                degradation_threshold=healing_threshold,
                healing_iterations=3,
                lucas_weights=lucas_weights
            )
        ) if enable_self_healing else None
        
        self.defense_system = MultiLayerDefense(
            defense_layers=defense_layers
        ) if enable_recursive_defense else None
        
        # Monitoring and statistics
        self.processing_history = []
        self.performance_metrics = {
            "total_processed": 0,
            "flame_corrections": 0,
            "healing_sessions": 0,
            "defense_activations": 0,
            "overall_improvements": []
        }
    
    def process_evaluation_series(self, 
                                eval_series: np.ndarray,
                                window: Optional[Tuple[int, int]] = None,
                                n_index: float = PHI,
                                tag: str = "regen88_analysis") -> Dict[str, Any]:
        """
        Process evaluation series through complete Regen88 pipeline.
        
        Args:
            eval_series: Evaluation series to process
            window: Analysis window
            n_index: Refraction index
            tag: Analysis tag for tracking
            
        Returns:
            Complete Regen88 analysis results
        """
        # Stage 1: Base entropy pump with optional flame correction
        if self.enable_flame_correction:
            base_result = integrate_flame_correction_with_entropy_pump(
                eval_series=eval_series,
                window=window,
                n_index=n_index,
                lucas_weights=self.lucas_weights,
                enable_flame_correction=True,
                flame_threshold=self.flame_engine.threshold
            )
            if base_result.get("flame_correction", {}).get("flames_corrected", 0) > 0:
                self.performance_metrics["flame_corrections"] += 1
        else:
            base_result = codex_pump_from_series(
                eval_series=eval_series,
                window=window,
                n_index=n_index,
                lucas_weights=self.lucas_weights
            )
        
        if not base_result.get("ok", False):
            return self._create_failure_result(base_result, tag)
        
        # Stage 2: Self-healing
        if self.enable_self_healing:
            healed_result = self.healing_system.adaptive_heal(base_result)
            if healed_result.get("self_healing_applied", False):
                self.performance_metrics["healing_sessions"] += 1
        else:
            healed_result = base_result
        
        # Stage 3: Recursive defense
        if self.enable_recursive_defense:
            defended_result = integrate_recursive_defense(
                entropy_result=healed_result,
                defense_layers=self.defense_system.defense_layers,
                enable_multi_layer=True
            )
            defense_info = defended_result.get("recursive_defense_multi_layer", {})
            if defense_info.get("layers_activated", 0) > 0:
                self.performance_metrics["defense_activations"] += 1
        else:
            defended_result = healed_result
        
        # Stage 4: Final analysis and metrics
        final_result = self._finalize_regen88_result(
            original_series=eval_series,
            final_result=defended_result,
            tag=tag
        )
        
        # Update performance tracking
        self._update_performance_metrics(final_result)
        
        return final_result
    
    def _create_failure_result(self, base_result: Dict[str, Any], tag: str) -> Dict[str, Any]:
        """Create failure result for tracking."""
        return {
            "ok": False,
            "regen88_processed": True,
            "tag": tag,
            "reason": base_result.get("reason", "unknown"),
            "base_result": base_result,
            "modules_enabled": {
                "flame_correction": self.enable_flame_correction,
                "self_healing": self.enable_self_healing,
                "recursive_defense": self.enable_recursive_defense
            }
        }
    
    def _finalize_regen88_result(self, 
                               original_series: np.ndarray,
                               final_result: Dict[str, Any],
                               tag: str) -> Dict[str, Any]:
        """
        Finalize Regen88 processing with comprehensive metrics.
        
        Args:
            original_series: Original evaluation series
            final_result: Final processed result
            tag: Analysis tag
            
        Returns:
            Complete Regen88 result with metrics
        """
        # Calculate overall improvement metrics
        original_theta = np.array(final_result.get("theta_after", []))
        
        # Check if we have flame-corrected or defense-protected theta
        if "theta_after_corrected" in final_result:
            processed_theta = np.array(final_result["theta_after_corrected"])
        elif "recursive_defense_multi_layer" in final_result:
            defense_data = final_result["recursive_defense_multi_layer"]["final_protected_data"]
            processed_theta = np.array(defense_data.get("theta_after", []))
        else:
            processed_theta = original_theta
        
        # Calculate comprehensive improvement metrics
        improvement_metrics = self._calculate_improvement_metrics(
            original_series, original_theta, processed_theta
        )
        
        # Create comprehensive result
        regen88_result = final_result.copy()
        regen88_result.update({
            "regen88_processed": True,
            "regen88_version": "1.0.0",
            "tag": tag,
            "modules_enabled": {
                "flame_correction": self.enable_flame_correction,
                "self_healing": self.enable_self_healing,
                "recursive_defense": self.enable_recursive_defense
            },
            "lucas_weights": self.lucas_weights,
            "improvement_metrics": improvement_metrics,
            "processing_timestamp": self._get_timestamp()
        })
        
        return regen88_result
    
    def _calculate_improvement_metrics(self, 
                                     original_series: np.ndarray,
                                     original_theta: np.ndarray,
                                     processed_theta: np.ndarray) -> Dict[str, Any]:
        """Calculate comprehensive improvement metrics."""
        metrics = {}
        
        # Basic variance improvements
        if len(original_theta) > 0 and len(processed_theta) > 0:
            orig_var = float(np.var(original_theta))
            proc_var = float(np.var(processed_theta))
            
            metrics["theta_variance_reduction"] = (
                (orig_var - proc_var) / orig_var if orig_var > 0 else 0.0
            )
            metrics["theta_stability_improvement"] = max(0.0, metrics["theta_variance_reduction"])
        else:
            metrics["theta_variance_reduction"] = 0.0
            metrics["theta_stability_improvement"] = 0.0
        
        # Series stability metrics
        if len(original_series) > 1:
            orig_deltas = np.diff(original_series)
            orig_chaos = float(np.var(orig_deltas))
            
            # Estimate final series stability (if available)
            if len(processed_theta) > 1:
                proc_deltas = np.diff(processed_theta)
                proc_chaos = float(np.var(proc_deltas))
                metrics["chaos_reduction"] = (
                    (orig_chaos - proc_chaos) / orig_chaos if orig_chaos > 0 else 0.0
                )
            else:
                metrics["chaos_reduction"] = 0.0
        else:
            metrics["chaos_reduction"] = 0.0
        
        # Overall effectiveness score
        effectiveness_components = [
            metrics.get("theta_stability_improvement", 0.0),
            metrics.get("chaos_reduction", 0.0)
        ]
        metrics["overall_effectiveness"] = float(np.mean([max(0.0, c) for c in effectiveness_components]))
        
        return metrics
    
    def _update_performance_metrics(self, result: Dict[str, Any]):
        """Update system performance tracking."""
        self.performance_metrics["total_processed"] += 1
        
        improvement = result.get("improvement_metrics", {}).get("overall_effectiveness", 0.0)
        self.performance_metrics["overall_improvements"].append(improvement)
        
        # Record processing session
        session_record = {
            "tag": result.get("tag", "unknown"),
            "success": result.get("ok", False),
            "improvement": improvement,
            "modules_used": {
                "flame": "flame_correction" in result,
                "healing": "self_healing" in result,
                "defense": "recursive_defense_multi_layer" in result or "recursive_defense_single" in result
            }
        }
        self.processing_history.append(session_record)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
    
    def get_system_performance(self) -> Dict[str, Any]:
        """
        Get comprehensive system performance statistics.
        
        Returns:
            Performance statistics for the Regen88 system
        """
        improvements = self.performance_metrics["overall_improvements"]
        
        stats = {
            "total_processed": self.performance_metrics["total_processed"],
            "flame_corrections": self.performance_metrics["flame_corrections"],
            "healing_sessions": self.performance_metrics["healing_sessions"],
            "defense_activations": self.performance_metrics["defense_activations"],
            "average_improvement": float(np.mean(improvements)) if improvements else 0.0,
            "max_improvement": float(np.max(improvements)) if improvements else 0.0,
            "improvement_std": float(np.std(improvements)) if len(improvements) > 1 else 0.0,
            "system_config": {
                "flame_correction_enabled": self.enable_flame_correction,
                "self_healing_enabled": self.enable_self_healing,
                "recursive_defense_enabled": self.enable_recursive_defense,
                "lucas_weights": self.lucas_weights
            }
        }
        
        # Calculate success rates
        if self.performance_metrics["total_processed"] > 0:
            stats["flame_correction_rate"] = (
                self.performance_metrics["flame_corrections"] / 
                self.performance_metrics["total_processed"]
            )
            stats["healing_activation_rate"] = (
                self.performance_metrics["healing_sessions"] / 
                self.performance_metrics["total_processed"]
            )
            stats["defense_activation_rate"] = (
                self.performance_metrics["defense_activations"] / 
                self.performance_metrics["total_processed"]
            )
        
        return stats
    
    def run_comprehensive_analysis(self, 
                                 eval_series: np.ndarray,
                                 tag: str = "comprehensive") -> Dict[str, Any]:
        """
        Run comprehensive analysis with detailed reporting.
        
        Args:
            eval_series: Series to analyze
            tag: Analysis tag
            
        Returns:
            Detailed analysis results
        """
        # Process with Regen88
        result = self.process_evaluation_series(eval_series, tag=tag)
        
        # Add comprehensive analysis
        result["comprehensive_analysis"] = {
            "system_performance": self.get_system_performance(),
            "processing_history_length": len(self.processing_history),
            "analysis_timestamp": self._get_timestamp()
        }
        
        return result


# Convenience function for quick Regen88 processing
def regen88_analyze(eval_series: np.ndarray,
                   window: Optional[Tuple[int, int]] = None,
                   lucas_weights: Tuple[int, int, int] = (4, 7, 11),
                   tag: str = "regen88") -> Dict[str, Any]:
    """
    Quick analysis using default Regen88 configuration.
    
    Args:
        eval_series: Evaluation series
        window: Analysis window
        lucas_weights: Lucas weights
        tag: Analysis tag
        
    Returns:
        Regen88 analysis results
    """
    regen88 = Regen88Codex(lucas_weights=lucas_weights)
    return regen88.process_evaluation_series(eval_series, window=window, tag=tag)


# Factory function for custom Regen88 configurations
def create_regen88_config(flame_sensitivity: str = "normal",
                         healing_aggressiveness: str = "normal", 
                         defense_strength: str = "normal") -> Regen88Codex:
    """
    Create Regen88 configuration with preset sensitivity levels.
    
    Args:
        flame_sensitivity: "low", "normal", "high"
        healing_aggressiveness: "conservative", "normal", "aggressive"
        defense_strength: "minimal", "normal", "maximum"
        
    Returns:
        Configured Regen88 system
    """
    # Flame correction thresholds
    flame_thresholds = {"low": 0.25, "normal": 0.15, "high": 0.08}
    flame_threshold = flame_thresholds.get(flame_sensitivity, 0.15)
    
    # Healing thresholds
    healing_thresholds = {"conservative": 0.2, "normal": 0.1, "aggressive": 0.05}
    healing_threshold = healing_thresholds.get(healing_aggressiveness, 0.1)
    
    # Defense layers
    defense_layers_map = {"minimal": 1, "normal": 3, "maximum": 5}
    defense_layers = defense_layers_map.get(defense_strength, 3)
    
    return Regen88Codex(
        flame_threshold=flame_threshold,
        healing_threshold=healing_threshold,
        defense_layers=defense_layers
    )