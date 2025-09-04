import pytest
import numpy as np
import math
from scripts.flame_correction import (
    detect_flames, 
    regen88_smooth, 
    flame_correction_engine,
    apply_flame_correction_to_series
)


class TestFlameDetection:
    """Test flame detection functionality."""
    
    def test_detect_flames_basic(self):
        """Test basic flame detection with outliers."""
        # Create data with clear outliers
        data = np.array([0.1, 0.2, 0.15, 5.0, 0.18, 0.12, -4.0, 0.2])
        flames = detect_flames(data, threshold=2.0)
        
        # Should detect the outliers at indices 3 and 6
        assert flames[3] == True  # 5.0 is an outlier
        assert flames[6] == True  # -4.0 is an outlier
        assert np.sum(flames) == 2
    
    def test_detect_flames_no_outliers(self):
        """Test flame detection with normal data."""
        data = np.array([0.1, 0.2, 0.15, 0.18, 0.12, 0.22, 0.16])
        flames = detect_flames(data, threshold=2.0)
        
        # Should detect no flames in normal data
        assert np.sum(flames) == 0
    
    def test_detect_flames_empty_array(self):
        """Test flame detection with empty array."""
        data = np.array([])
        flames = detect_flames(data)
        
        assert len(flames) == 0
    
    def test_detect_flames_constant_data(self):
        """Test flame detection with constant data."""
        data = np.array([1.0, 1.0, 1.0, 1.0])
        flames = detect_flames(data)
        
        # Should detect no flames in constant data
        assert np.sum(flames) == 0


class TestRegen88Smoothing:
    """Test Regen88 regenerative smoothing."""
    
    def test_regen88_smooth_basic(self):
        """Test basic smoothing functionality."""
        # Create noisy data
        data = np.array([1.0, 3.0, 1.5, 4.0, 2.0])
        smoothed = regen88_smooth(data, factor=88.0)
        
        # Smoothed data should be less noisy
        assert len(smoothed) == len(data)
        original_variance = np.var(data)
        smoothed_variance = np.var(smoothed)
        assert smoothed_variance <= original_variance
    
    def test_regen88_smooth_preserves_trends(self):
        """Test that smoothing preserves overall trends."""
        # Create trending data with noise
        trend = np.linspace(0, 10, 20)
        noise = np.random.normal(0, 0.5, 20)
        data = trend + noise
        
        smoothed = regen88_smooth(data, factor=50.0)
        
        # Should preserve general upward trend
        assert smoothed[-1] > smoothed[0]
        assert np.corrcoef(trend, smoothed)[0, 1] > 0.8  # High correlation with trend
    
    def test_regen88_smooth_empty_array(self):
        """Test smoothing with empty array."""
        data = np.array([])
        smoothed = regen88_smooth(data)
        
        assert len(smoothed) == 0
    
    def test_regen88_smooth_single_element(self):
        """Test smoothing with single element."""
        data = np.array([5.0])
        smoothed = regen88_smooth(data)
        
        assert len(smoothed) == 1
        assert smoothed[0] == data[0]


class TestFlameCorrection:
    """Test complete flame correction engine."""
    
    def test_flame_correction_basic(self):
        """Test basic flame correction functionality."""
        # Create θ-refracted data with outliers
        theta_data = np.array([0.1, 0.2, 2.0, 0.15, 0.18, -1.8, 0.12])  # outliers at 2.0, -1.8
        
        result = flame_correction_engine(
            theta_data,
            enable_flame_detection=True,
            enable_regen88=True,
            flame_threshold=1.5
        )
        
        assert "theta_corrected" in result
        assert "flames_detected" in result
        assert result["flames_detected"] > 0  # Should detect some flames
        assert result["regen88_applied"] is True
        assert result["flame_detection_applied"] is True
    
    def test_flame_correction_disabled(self):
        """Test flame correction with both features disabled."""
        theta_data = np.array([0.1, 0.2, 2.0, 0.15, 0.18])
        
        result = flame_correction_engine(
            theta_data,
            enable_flame_detection=False,
            enable_regen88=False
        )
        
        # Should return original data unchanged
        np.testing.assert_array_equal(result["theta_corrected"], theta_data)
        assert result["flames_detected"] == 0
        assert result["regen88_applied"] is False
        assert result["flame_detection_applied"] is False
    
    def test_flame_correction_reduces_variance(self):
        """Test that flame correction reduces variance."""
        # Create highly variable data with outliers
        np.random.seed(42)
        base_data = np.random.normal(0, 0.3, 50)
        # Add some extreme outliers
        outlier_positions = [10, 25, 40]
        for pos in outlier_positions:
            base_data[pos] = np.random.choice([-3.0, 3.0])
        
        result = flame_correction_engine(
            base_data,
            enable_flame_detection=True,
            enable_regen88=True
        )
        
        original_var = np.var(base_data)
        corrected_var = np.var(result["theta_corrected"])
        
        # Variance should be reduced
        assert corrected_var < original_var
        assert result["variance_reduction_pct"] > 0
    
    def test_flame_correction_empty_data(self):
        """Test flame correction with empty data."""
        result = flame_correction_engine(np.array([]))
        
        assert len(result["theta_corrected"]) == 0
        assert result["flames_detected"] == 0
        assert result["variance_reduction_pct"] == 0.0


class TestFlameCommissionSeries:
    """Test flame correction integration with series reconstruction."""
    
    def test_apply_flame_correction_to_series(self):
        """Test integration with series reconstruction."""
        # Create mock entropy pump output
        theta_refracted = np.array([0.5, -0.3, 1.2, 0.2, -0.1, 0.8])  # outlier at 1.2, 0.8
        deltas_original = np.array([10, -5, 15, -8, 3])
        series_baseline = 100.0
        compression_factor = 0.3
        
        result = apply_flame_correction_to_series(
            theta_refracted, 
            deltas_original, 
            series_baseline, 
            compression_factor,
            enable_flame_detection=True,
            enable_regen88=True
        )
        
        assert "theta_corrected" in result
        assert "deltas_corrected" in result  
        assert "series_corrected" in result
        assert len(result["deltas_corrected"]) == len(deltas_original)
        assert len(result["series_corrected"]) == len(deltas_original) + 1
        assert result["series_corrected"][0] == series_baseline
    
    def test_flame_correction_preserves_series_structure(self):
        """Test that flame correction preserves series structure."""
        theta_refracted = np.linspace(-0.5, 0.5, 10)
        deltas_original = np.random.normal(0, 5, 9)
        series_baseline = 50.0
        compression_factor = 0.2
        
        result = apply_flame_correction_to_series(
            theta_refracted,
            deltas_original,
            series_baseline, 
            compression_factor
        )
        
        # Series should start with baseline
        assert result["series_corrected"][0] == series_baseline
        
        # Series should be reconstructed from deltas
        reconstructed = series_baseline + np.cumsum(result["deltas_corrected"])
        np.testing.assert_array_almost_equal(
            result["series_corrected"][1:], 
            reconstructed,
            decimal=10
        )


class TestFlameCommissionIntegration:
    """Test integration with existing entropy pump system."""
    
    def test_integration_with_entropy_pump(self):
        """Test that flame correction integrates properly with entropy pump."""
        # This test would require importing codex_entropy_pump
        # For now, test the core flame correction functionality
        
        # Simulate typical entropy pump θ output
        phi = (1 + np.sqrt(5)) / 2
        theta_data = np.array([
            np.arcsin(np.sin(0.3) / phi),
            np.arcsin(np.sin(-0.2) / phi), 
            np.arcsin(np.sin(0.8) / phi),  # potential outlier
            np.arcsin(np.sin(0.1) / phi),
            np.arcsin(np.sin(-0.4) / phi)
        ])
        
        result = flame_correction_engine(theta_data)
        
        # Should produce reasonable corrected output
        assert len(result["theta_corrected"]) == len(theta_data)
        assert not np.any(np.isnan(result["theta_corrected"]))
        assert np.all(np.abs(result["theta_corrected"]) <= np.pi/2)  # Valid θ range


if __name__ == "__main__":
    pytest.main([__file__])