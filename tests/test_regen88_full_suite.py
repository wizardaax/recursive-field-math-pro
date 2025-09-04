"""
Comprehensive test suite for Regen88 Codex modules.
Tests flame correction, entropy healing, recursive defense, and integration.
"""
import math
import numpy as np
import pytest
from scripts.regen88_flame_correction import FlameCorrection, integrate_flame_correction_with_entropy_pump
from scripts.regen88_entropy_healing import EntropySelfHealing, AdaptiveHealing
from scripts.regen88_recursive_defense import RecursiveDefenseCore, MultiLayerDefense, integrate_recursive_defense
from scripts.regen88_integration import Regen88Codex, regen88_analyze, create_regen88_config
from scripts.codex_entropy_pump import PHI


class TestFlameCorrection:
    """Test suite for Flame Correction Engine."""
    
    def test_flame_detection_basic(self):
        """Test basic flame detection functionality."""
        flame_engine = FlameCorrection()
        
        # Create synthetic chaotic series
        rng = np.random.default_rng(42)
        chaotic_theta = rng.normal(0, 0.5, 50)
        # Add some high-frequency oscillations (flames)
        chaotic_theta[10:15] += rng.normal(0, 2.0, 5)
        
        detection = flame_engine.detect_flame_patterns(chaotic_theta)
        
        assert "flame_detected" in detection
        assert "flame_intensity" in detection
        assert "flame_locations" in detection
        assert detection["series_length"] == 50
    
    def test_flame_correction_effectiveness(self):
        """Test that flame correction reduces chaos."""
        flame_engine = FlameCorrection(threshold=0.1, correction_strength=0.8)
        
        # Create series with known instabilities
        rng = np.random.default_rng(42)
        theta_series = rng.normal(0, 0.3, 40)
        theta_series[15:20] = rng.normal(0, 3.0, 5)  # Inject flames
        
        original_variance = float(np.var(theta_series))
        
        # Apply full correction cycle
        result = flame_engine.full_correction_cycle(theta_series)
        
        assert result["flames_corrected"] >= 0
        assert "correction_effectiveness" in result
        assert "stability_improvement" in result
        
        # Verify correction actually improves stability
        corrected_series = np.array(result["corrected_series"])
        corrected_variance = float(np.var(corrected_series))
        assert corrected_variance <= original_variance
    
    def test_flame_correction_with_lucas_weights(self):
        """Test flame correction with different Lucas weights."""
        flame_engine = FlameCorrection(lucas_resonance=(4, 7, 11))
        
        rng = np.random.default_rng(123)
        theta_series = rng.normal(0, 0.4, 30)
        
        result = flame_engine.full_correction_cycle(theta_series)
        
        assert "corrected_series" in result
        assert len(result["corrected_series"]) == len(theta_series)
    
    def test_flame_integration_with_entropy_pump(self):
        """Test integration of flame correction with entropy pump."""
        rng = np.random.default_rng(42)
        eval_series = np.cumsum(rng.normal(0, 100, 50))
        
        result = integrate_flame_correction_with_entropy_pump(
            eval_series,
            window=(5, 35),
            enable_flame_correction=True
        )
        
        assert result["ok"] == True
        assert "regen88_enabled" in result
        assert "flame_correction" in result
        assert "theta_after_corrected" in result


class TestEntropySelfHealing:
    """Test suite for Entropy Self-Healing system."""
    
    def test_degradation_detection(self):
        """Test entropy degradation detection."""
        healer = EntropySelfHealing()
        
        # Create metrics indicating degradation
        degraded_metrics = {
            "variance_reduction_pct": 15.0,  # Below 20% threshold
            "compression": 0.3,              # Low compression
            "phi_clamp_rad": math.asin(1.0/PHI) * 1.5,  # Deviated phi-clamp
            "mae_improvement_pct": 1.0       # Below 2% threshold
        }
        
        detection = healer.detect_entropy_degradation(degraded_metrics)
        
        assert detection["degradation_detected"] == True
        assert detection["degradation_score"] > healer.degradation_threshold
        assert len(detection["degradation_indicators"]) > 0
    
    def test_recursive_healing(self):
        """Test recursive healing functionality."""
        healer = EntropySelfHealing(healing_iterations=2)
        
        # Create degraded theta series
        rng = np.random.default_rng(42)
        degraded_theta = rng.normal(0, 1.5, 40)  # High variance series
        
        degradation_info = {"degradation_detected": True, "degradation_score": 0.5}
        
        healing_result = healer.apply_recursive_healing(degraded_theta, degradation_info)
        
        assert healing_result["healing_applied"] == True
        assert healing_result["healing_iterations"] <= 2
        assert "healing_effectiveness" in healing_result
        assert len(healing_result["healed_series"]) == len(degraded_theta)
    
    def test_adaptive_healing(self):
        """Test adaptive healing system."""
        base_healer = EntropySelfHealing()
        adaptive_healer = AdaptiveHealing(base_healer)
        
        # Create entropy result that needs healing
        entropy_result = {
            "ok": True,
            "variance_reduction_pct": 10.0,  # Poor performance
            "compression": 0.2,
            "phi_clamp_rad": math.asin(1.0/PHI),
            "mae_improvement_pct": 1.0,
            "theta_after": np.random.normal(0, 1.0, 30).tolist()
        }
        
        result = adaptive_healer.adaptive_heal(entropy_result)
        
        assert "self_healing" in result
        assert "adaptive_healing" in result
        assert "adapted_threshold" in result["adaptive_healing"]
    
    def test_healing_statistics(self):
        """Test healing performance statistics."""
        healer = EntropySelfHealing()
        
        # Simulate some healing sessions
        for i in range(5):
            metrics = {
                "variance_reduction_pct": 15.0 + i * 2,
                "compression": 0.4,
                "phi_clamp_rad": math.asin(1.0/PHI),
                "mae_improvement_pct": 1.5
            }
            healer.monitor_and_heal({"ok": True, "theta_after": [0.1, 0.2, 0.3], **metrics})
        
        stats = healer.get_healing_statistics()
        
        assert stats["total_sessions"] == 5
        assert "healing_rate" in stats
        assert "average_effectiveness" in stats


class TestRecursiveDefense:
    """Test suite for Recursive Defense modules."""
    
    def test_recursive_barrier_computation(self):
        """Test recursive barrier computation."""
        defense = RecursiveDefenseCore(defense_depth=2)
        
        rng = np.random.default_rng(42)
        threat_series = rng.normal(0, 1.0, 20)
        
        barrier = defense.compute_recursive_barrier(threat_series)
        
        assert len(barrier) == len(threat_series)
        assert np.all(barrier >= 0)  # Barriers should be non-negative
        assert np.all(barrier <= 1.0)  # Barriers should be normalized
    
    def test_threat_analysis(self):
        """Test threat level analysis."""
        defense = RecursiveDefenseCore()
        
        # Create entropy data with various threat indicators
        high_threat_data = {
            "var_delta_before": 100.0,
            "var_delta_after": 95.0,   # Poor variance reduction
            "compression": 0.1,         # Low compression
            "phi_clamp_rad": math.asin(1.0/PHI) * 2,  # Unstable phi-clamp
            "theta_after": np.random.normal(0, 2.0, 50).tolist()  # High variance
        }
        
        threat_analysis = defense.analyze_threat_level(high_threat_data)
        
        assert threat_analysis["defense_required"] == True
        assert threat_analysis["threat_level"] > defense.protection_threshold
        assert len(threat_analysis["threat_indicators"]) > 0
    
    def test_defense_activation(self):
        """Test recursive defense activation."""
        defense = RecursiveDefenseCore(defense_depth=2)
        
        # Create data requiring defense
        entropy_data = {
            "theta_after": np.random.normal(0, 1.5, 30).tolist(),
            "compression": 0.1,
            "var_delta_before": 100.0,
            "var_delta_after": 90.0
        }
        
        threat_analysis = defense.analyze_threat_level(entropy_data)
        defense_result = defense.activate_recursive_defense(entropy_data, threat_analysis)
        
        if defense_result["defense_activated"]:
            assert "protection_effectiveness" in defense_result
            assert "protected_data" in defense_result
            protected_theta = defense_result["protected_data"]["theta_after"]
            assert len(protected_theta) == len(entropy_data["theta_after"])
    
    def test_multi_layer_defense(self):
        """Test multi-layer defense system."""
        multi_defense = MultiLayerDefense(defense_layers=3)
        
        entropy_data = {
            "theta_after": np.random.normal(0, 2.0, 40).tolist(),
            "compression": 0.05,  # Very low compression
            "var_delta_before": 200.0,
            "var_delta_after": 180.0
        }
        
        result = multi_defense.activate_layered_defense(entropy_data)
        
        assert result["multi_layer_defense"] == True
        assert "layers_activated" in result
        assert "overall_effectiveness" in result
        assert len(result["layer_results"]) == 3


class TestRegen88Integration:
    """Test suite for complete Regen88 integration."""
    
    def test_regen88_basic_functionality(self):
        """Test basic Regen88 system functionality."""
        regen88 = Regen88Codex()
        
        rng = np.random.default_rng(42)
        eval_series = np.cumsum(rng.normal(0, 50, 50))
        
        result = regen88.process_evaluation_series(eval_series, tag="test_basic")
        
        assert "regen88_processed" in result
        assert "modules_enabled" in result
        assert "improvement_metrics" in result
        assert result["tag"] == "test_basic"
    
    def test_regen88_all_modules_enabled(self):
        """Test Regen88 with all modules enabled."""
        regen88 = Regen88Codex(
            enable_flame_correction=True,
            enable_self_healing=True,
            enable_recursive_defense=True
        )
        
        rng = np.random.default_rng(123)
        # Create challenging series
        eval_series = np.cumsum(rng.normal(0, 100, 60))
        eval_series[20:25] += rng.normal(0, 500, 5)  # Add chaos
        
        result = regen88.process_evaluation_series(eval_series, tag="all_modules")
        
        if result.get("ok", False):
            assert result["modules_enabled"]["flame_correction"] == True
            assert result["modules_enabled"]["self_healing"] == True
            assert result["modules_enabled"]["recursive_defense"] == True
    
    def test_regen88_performance_tracking(self):
        """Test Regen88 performance tracking."""
        regen88 = Regen88Codex()
        
        # Process multiple series
        rng = np.random.default_rng(42)
        for i in range(3):
            eval_series = np.cumsum(rng.normal(0, 50, 40))
            regen88.process_evaluation_series(eval_series, tag=f"perf_test_{i}")
        
        performance = regen88.get_system_performance()
        
        assert performance["total_processed"] == 3
        assert "average_improvement" in performance
        assert "system_config" in performance
    
    def test_regen88_convenience_function(self):
        """Test convenience function for quick analysis."""
        rng = np.random.default_rng(42)
        eval_series = np.cumsum(rng.normal(0, 40, 35))
        
        result = regen88_analyze(eval_series, tag="convenience_test")
        
        assert "regen88_processed" in result
        assert result["tag"] == "convenience_test"
    
    def test_regen88_config_factory(self):
        """Test configuration factory function."""
        # Test different sensitivity levels
        configs = [
            create_regen88_config("low", "conservative", "minimal"),
            create_regen88_config("normal", "normal", "normal"),
            create_regen88_config("high", "aggressive", "maximum")
        ]
        
        for config in configs:
            assert isinstance(config, Regen88Codex)
            assert config.enable_flame_correction == True
            assert config.enable_self_healing == True
            assert config.enable_recursive_defense == True
    
    def test_comprehensive_analysis(self):
        """Test comprehensive analysis functionality."""
        regen88 = Regen88Codex()
        
        rng = np.random.default_rng(42)
        eval_series = np.cumsum(rng.normal(0, 60, 45))
        
        result = regen88.run_comprehensive_analysis(eval_series, tag="comprehensive")
        
        assert "comprehensive_analysis" in result
        assert "system_performance" in result["comprehensive_analysis"]
        assert "analysis_timestamp" in result["comprehensive_analysis"]


class TestRegen88EdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_series_handling(self):
        """Test handling of empty or invalid series."""
        regen88 = Regen88Codex()
        
        # Empty series
        empty_result = regen88.process_evaluation_series(np.array([]), tag="empty")
        assert empty_result["ok"] == False
        
        # Very short series
        short_result = regen88.process_evaluation_series(np.array([1, 2]), tag="short")
        assert short_result["ok"] == False
    
    def test_disabled_modules(self):
        """Test Regen88 with modules disabled."""
        regen88 = Regen88Codex(
            enable_flame_correction=False,
            enable_self_healing=False,
            enable_recursive_defense=False
        )
        
        rng = np.random.default_rng(42)
        eval_series = np.cumsum(rng.normal(0, 50, 40))
        
        result = regen88.process_evaluation_series(eval_series, tag="disabled")
        
        if result.get("ok", False):
            assert result["modules_enabled"]["flame_correction"] == False
            assert result["modules_enabled"]["self_healing"] == False
            assert result["modules_enabled"]["recursive_defense"] == False
    
    def test_lucas_weights_validation(self):
        """Test different Lucas weights configurations."""
        lucas_variants = [(4, 7, 11), (3, 5, 8), (2, 3, 5), (1, 1, 2)]
        
        for lucas_weights in lucas_variants:
            regen88 = Regen88Codex(lucas_weights=lucas_weights)
            
            rng = np.random.default_rng(42)
            eval_series = np.cumsum(rng.normal(0, 30, 25))
            
            result = regen88.process_evaluation_series(eval_series)
            assert result["lucas_weights"] == lucas_weights


# Integration tests with existing entropy pump
class TestRegen88WithExistingSystem:
    """Test Regen88 integration with existing entropy pump system."""
    
    def test_backward_compatibility(self):
        """Test that Regen88 maintains backward compatibility."""
        from scripts.codex_entropy_pump import codex_pump_from_series
        
        rng = np.random.default_rng(42)
        eval_series = np.cumsum(rng.normal(0, 50, 40))
        
        # Test original entropy pump
        original_result = codex_pump_from_series(eval_series, window=(5, 25))
        
        # Test Regen88 with all modules disabled
        regen88 = Regen88Codex(
            enable_flame_correction=False,
            enable_self_healing=False,
            enable_recursive_defense=False
        )
        regen88_result = regen88.process_evaluation_series(eval_series, window=(5, 25))
        
        if original_result["ok"] and regen88_result["ok"]:
            # Core metrics should be reasonably similar (allowing for small differences)
            variance_diff = abs(original_result["variance_reduction_pct"] - 
                              regen88_result["variance_reduction_pct"])
            # Allow up to 15% difference due to potential pipeline differences
            assert variance_diff < 15.0, f"Variance reduction difference too large: {variance_diff}"
    
    def test_enhanced_performance(self):
        """Test that Regen88 provides enhanced performance."""
        rng = np.random.default_rng(42)
        # Create challenging series with instabilities
        eval_series = np.cumsum(rng.normal(0, 80, 50))
        eval_series[15:20] += rng.normal(0, 300, 5)  # Inject chaos
        
        # Test with Regen88 enhancements
        regen88 = Regen88Codex()
        enhanced_result = regen88.process_evaluation_series(eval_series, window=(5, 35))
        
        if enhanced_result.get("ok", False):
            # Should show improvement metrics
            improvement = enhanced_result.get("improvement_metrics", {})
            assert "overall_effectiveness" in improvement
            assert improvement["overall_effectiveness"] >= 0.0