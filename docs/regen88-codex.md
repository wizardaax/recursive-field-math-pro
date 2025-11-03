# Regen88 Codex: Enhanced Entropy Pump System

The Regen88 Codex is an advanced enhancement to the original Codex Entropy-Pump system, providing sophisticated error correction, self-healing capabilities, and recursive defense mechanisms.

## 🚀 New Features

### 1. Flame Correction Engine
- **Purpose**: Detects and corrects chaotic "flame" patterns in entropy data
- **Mechanism**: Uses Lucas-enhanced golden refraction to stabilize chaotic regions
- **Benefits**: Reduces entropy instabilities by up to 80% in detected flame regions

### 2. Entropy Self-Healing System
- **Purpose**: Automatically detects and corrects entropy degradation
- **Mechanism**: Recursive healing algorithms with adaptive threshold adjustment
- **Benefits**: Maintains system performance even under adverse conditions

### 3. Recursive Defense Modules
- **Purpose**: Provides multi-layer protection against entropy threats
- **Mechanism**: Recursive barrier algorithms using Lucas sequence mathematics
- **Benefits**: Proactive defense against entropy degradation patterns

## 🎯 Quick Start

### Basic Usage
```python
from scripts.regen88_integration import regen88_analyze
import numpy as np

# Your evaluation series
eval_series = np.array([...])  # Chess game evaluations, financial data, etc.

# Enhanced analysis with Regen88
result = regen88_analyze(eval_series, tag="my_analysis")

if result["ok"]:
    print(f"Variance reduction: {result['variance_reduction_pct']:.1f}%")
    print(f"Regen88 enhanced: {result.get('regen88_processed', False)}")
```

### Advanced Configuration
```python
from scripts.regen88_integration import Regen88Codex, create_regen88_config

# Create custom configuration
regen88 = create_regen88_config(
    flame_sensitivity="high",      # "low", "normal", "high"
    healing_aggressiveness="aggressive",  # "conservative", "normal", "aggressive"  
    defense_strength="maximum"     # "minimal", "normal", "maximum"
)

# Process with custom settings
result = regen88.process_evaluation_series(eval_series, tag="advanced")
```

## 📊 Enhanced Harness

Run comprehensive analysis with both standard and Regen88 modes:

```bash
python -m scripts.run_regen88_harness
```

This generates:
- **Comparison plots**: Standard vs Regen88 enhanced analysis
- **Performance metrics**: Detailed enhancement statistics
- **Summary reports**: Markdown summaries with acceptance rule evaluation

## 🔧 Module Details

### Flame Correction Engine

The Flame Correction Engine detects chaotic patterns ("flames") in entropy data and applies corrective measures:

```python
from scripts.regen88_flame_correction import FlameCorrection

flame_engine = FlameCorrection(
    threshold=0.15,              # Detection sensitivity
    correction_strength=0.8,     # Correction intensity
    lucas_resonance=(4, 7, 11)   # Lucas weights
)

# Detect and correct flames
result = flame_engine.full_correction_cycle(theta_series)
print(f"Flames corrected: {result['flames_corrected']}")
print(f"Correction effectiveness: {result['correction_effectiveness']:.1%}")
```

### Entropy Self-Healing

The self-healing system monitors entropy pump performance and applies corrective measures:

```python
from scripts.regen88_entropy_healing import EntropySelfHealing, AdaptiveHealing

# Create adaptive healing system
base_healer = EntropySelfHealing(
    degradation_threshold=0.1,   # Sensitivity to degradation
    healing_iterations=3,        # Max healing passes
    lucas_weights=(4, 7, 11)     # Lucas sequence parameters
)
adaptive_healer = AdaptiveHealing(base_healer)

# Apply healing to entropy results
enhanced_result = adaptive_healer.adaptive_heal(entropy_result)
```

### Recursive Defense

Multi-layer recursive defense against entropy threats:

```python
from scripts.regen88_recursive_defense import MultiLayerDefense

# Create defense system
defense = MultiLayerDefense(defense_layers=3)

# Apply protection
protected_result = defense.activate_layered_defense(entropy_data)
print(f"Defense layers activated: {protected_result['layers_activated']}")
```

## 📈 Performance Monitoring

The Regen88 system includes comprehensive performance tracking:

```python
# Get system performance statistics
regen88 = Regen88Codex()

# Process multiple series...
for series in data_series:
    result = regen88.process_evaluation_series(series)

# View performance statistics
stats = regen88.get_system_performance()
print(f"Total processed: {stats['total_processed']}")
print(f"Average improvement: {stats['average_improvement']:.1%}")
print(f"Flame correction rate: {stats['flame_correction_rate']:.1%}")
```

## 🎛️ Configuration Options

### Flame Correction
- **threshold**: Detection sensitivity (0.05-0.3, default: 0.15)
- **correction_strength**: Correction intensity (0.1-1.0, default: 0.8)
- **lucas_resonance**: Lucas weights tuple (default: (4, 7, 11))

### Self-Healing
- **degradation_threshold**: Degradation detection sensitivity (0.05-0.3, default: 0.1)
- **healing_iterations**: Maximum healing passes (1-5, default: 3)
- **lucas_weights**: Lucas sequence parameters (default: (4, 7, 11))

### Recursive Defense
- **defense_layers**: Number of protection layers (1-5, default: 3)
- **protection_threshold**: Defense activation threshold (0.1-0.5, default: 0.2)
- **lucas_sequence**: Lucas parameters for each layer

## 📋 Acceptance Rules

Regen88 maintains the same acceptance criteria as the original system:

- **Variance reduction** ≥ 20%
- **MAE improvement** ≥ 2%
- **φ-clamp peak** within ±2° of 38.2°

Enhanced with additional Regen88 metrics:
- **Flame correction effectiveness** ≥ 50%
- **Healing success rate** ≥ 70%
- **Defense activation accuracy** ≥ 80%

## 🧪 Testing

Comprehensive test suite covering all Regen88 modules:

```bash
# Run all tests
python -m pytest tests/ -v

# Run only Regen88 tests
python -m pytest tests/test_regen88_full_suite.py -v

# Run specific test categories
python -m pytest tests/test_regen88_full_suite.py::TestFlameCorrection -v
python -m pytest tests/test_regen88_full_suite.py::TestEntropySelfHealing -v
python -m pytest tests/test_regen88_full_suite.py::TestRecursiveDefense -v
```

## 🔀 Migration Guide

### From Original Codex to Regen88

1. **Replace function calls**:
   ```python
   # Old
   from scripts.codex_entropy_pump import codex_pump_from_series
   result = codex_pump_from_series(eval_series)
   
   # New
   from scripts.regen88_integration import regen88_analyze
   result = regen88_analyze(eval_series)
   ```

2. **Access enhanced features**:
   ```python
   if result.get("regen88_processed"):
       flame_info = result.get("flame_correction", {})
       healing_info = result.get("self_healing", {})
       defense_info = result.get("recursive_defense_multi_layer", {})
   ```

3. **Use new harness**:
   ```bash
   # Old
   python -m scripts.run_entropy_pump_harness
   
   # New (includes both modes)
   python -m scripts.run_regen88_harness
   ```

## 🎯 Use Cases

### 1. Financial Data Analysis
```python
# Analyze stock price volatility with Regen88
regen88 = create_regen88_config("high", "aggressive", "maximum")
result = regen88.process_evaluation_series(price_series, tag="AAPL_analysis")
```

### 2. Chess Game Analysis
```python
# Enhanced chess position evaluation
result = regen88_analyze(evaluation_series, window=(10, 30), tag="Kasparov_Fischer")
```

### 3. Scientific Data Processing
```python
# Process experimental data with self-healing
regen88 = Regen88Codex(enable_self_healing=True)
result = regen88.process_evaluation_series(sensor_data, tag="experiment_1")
```

## 📚 API Reference

### Core Classes
- `Regen88Codex`: Main integration class
- `FlameCorrection`: Flame detection and correction
- `EntropySelfHealing`: Self-healing system
- `AdaptiveHealing`: Adaptive healing wrapper
- `RecursiveDefenseCore`: Single-layer defense
- `MultiLayerDefense`: Multi-layer defense system

### Convenience Functions
- `regen88_analyze()`: Quick analysis with default settings
- `create_regen88_config()`: Configuration factory
- `integrate_flame_correction_with_entropy_pump()`: Flame correction integration
- `integrate_recursive_defense()`: Defense integration

### Result Structure
```python
{
    "ok": True,
    "regen88_processed": True,
    "regen88_version": "1.0.0",
    "modules_enabled": {...},
    "improvement_metrics": {...},
    "flame_correction": {...},      # If flame correction applied
    "self_healing": {...},          # If self-healing applied  
    "recursive_defense_multi_layer": {...}  # If defense applied
}
```