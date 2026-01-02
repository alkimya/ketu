# Complex Number Representation for Planetary Cycles

This module provides a mathematical representation of planetary positions and cycles using complex numbers on the unit circle.

## Mathematical Foundation

A longitude θ (in radians) is represented as a point on the unit circle:

```
z = e^(iθ) = cos(θ) + i·sin(θ)
```

This representation offers several advantages:

| Operation | Classical (degrees) | Complex |
|-----------|---------------------|---------|
| Aspect between bodies | `(lon2 - lon1) % 360` | `angle(z2/z1)` |
| Circular mean | Complex formula | `angle(Σzᵢ)` |
| Angular distance | `min(abs(a-b), 360-abs(a-b))` | `abs(angle(z1/z2))` |
| ML features | Sin/cos encoding needed | `(Re(z), Im(z))` natively linear |
| No discontinuity | 0°/360° wrap issues | Continuous on circle |

## Core Classes

### ZodiacPoint

Represents a single position on the zodiac circle.

```python
from ketu.complex import ZodiacPoint

# Create from degrees (user input)
moon = ZodiacPoint.from_degrees(120)  # Moon at 120° (0° Cancer)

# Create from radians (internal calculations)
sun = ZodiacPoint.from_radians(np.pi / 2)  # Sun at 90°

# Properties
print(moon.degrees)    # 120.0
print(moon.radians)    # 2.094...
print(moon.z)          # (-0.5+0.866j)
print(moon.real)       # -0.5 (cos)
print(moon.imag)       # 0.866 (sin)

# ML features (no discontinuity at 0°/360°)
cos_val, sin_val = moon.to_ml_features()
```

### CycleRatio

Represents the phase relationship between two bodies.

```python
from ketu.complex import ZodiacPoint, CycleRatio

# Create from two points
moon = ZodiacPoint.from_degrees(120)
sun = ZodiacPoint.from_degrees(90)

# Division creates a CycleRatio
cycle = moon / sun  # Equivalent to: CycleRatio(moon, sun)

# Properties
print(cycle.separation_degrees)  # 30.0
print(cycle.is_waxing)           # True (0-180°)
print(cycle.cycle_progress)      # 0.083... (30/360)

# Aspect detection
print(cycle.nearest_aspect_name)         # "conjunction" or "sextile"
print(cycle.is_in_aspect("sextile"))     # True (within orb)
print(cycle.distance_to_aspect("sextile"))  # Distance in radians

# ML features
features = cycle.to_ml_features()
# Returns: {
#   'cos_phase': ...,
#   'sin_phase': ...,
#   'cycle_progress': ...,
#   'is_waxing': ...,
#   'dist_conjunction': ...,
#   'dist_opposition': ...
# }
```

### Aspects

Major aspects are represented as roots of unity:

```python
from ketu.complex import ASPECTS, Aspect

# Pre-defined major aspects
conj = ASPECTS["conjunction"]  # 0° = 1+0j
sextile = ASPECTS["sextile"]   # 60° = e^(iπ/3)
square = ASPECTS["square"]     # 90° = 0+1j (= i)
trine = ASPECTS["trine"]       # 120° = e^(i2π/3)
opp = ASPECTS["opposition"]    # 180° = -1+0j

# Each aspect has:
print(square.degrees)      # 90.0
print(square.radians)      # 1.5707...
print(square.z)            # (0+1j)
print(square.orb_default)  # 8.0
```

## Circular Statistics

### Circular Mean

```python
from ketu.complex import ZodiacPoint, circular_mean

# Correctly handles wrap-around at 0°/360°
points = [
    ZodiacPoint.from_degrees(350),
    ZodiacPoint.from_degrees(10)
]
mean = circular_mean(points)
print(mean.degrees)  # ~0° (not 180°!)
```

### Circular Standard Deviation

```python
from ketu.complex import circular_std

std = circular_std(points)  # Returns radians
```

### Phase Locking Value (PLV)

Measures synchronization between two time series:

```python
from ketu.complex import phase_locking_value

# PLV = 1: Perfect sync (constant phase difference)
# PLV = 0: No sync (random phase difference)

plv = phase_locking_value(moon_series, sun_series)
```

## Vectorized Operations (NumPy)

For performance with large datasets:

```python
import numpy as np
from ketu.complex import (
    degrees_to_complex,
    cycle_ratio_vectorized,
    nearest_aspect_vectorized,
    to_ml_features_vectorized,
)

# Convert arrays of positions
moon_lons = np.array([120, 150, 180, 210])  # Degrees
sun_lons = np.array([90, 95, 100, 105])

# Compute cycle ratios
z_ratios = cycle_ratio_vectorized(moon_lons, sun_lons)

# Find nearest aspects
indices, angles, distances = nearest_aspect_vectorized(z_ratios)

# Generate ML features (shape: n x 6)
features = to_ml_features_vectorized(z_ratios)
```

## Integration with generate_cycle_series

```python
import pandas as pd
from ketu.cycles import generate_cycle_series
from ketu.complex import degrees_to_complex, to_ml_features_vectorized

# Generate cycle data
timestamps = pd.date_range("2025-01-01", "2025-12-31", freq="1D")
cycles = generate_cycle_series("Sun", "Moon", timestamps)

# Convert to complex representation
z_ratios = degrees_to_complex(cycles['angular_separation'])

# Get ML-ready features
features = to_ml_features_vectorized(z_ratios)
# features[:, 0] = cos_phase
# features[:, 1] = sin_phase
# features[:, 2] = cycle_progress
# features[:, 3] = is_waxing
# features[:, 4] = dist_conjunction
# features[:, 5] = dist_opposition
```

## Use Cases

### 1. Correlation Analysis

```python
import numpy as np
from scipy import stats
from ketu.complex import cycle_ratio_vectorized

# Cycle data
z_cycles = cycle_ratio_vectorized(moon_lons, sun_lons)

# Price returns
returns = np.diff(prices) / prices[:-1]

# Correlate with cos/sin of cycle phase
cos_corr, _ = stats.spearmanr(z_cycles.real[:-1], returns)
sin_corr, _ = stats.spearmanr(z_cycles.imag[:-1], returns)
```

### 2. Feature Engineering for ML

```python
from ketu.complex import to_ml_features_vectorized

# Get features without 0°/360° discontinuity
features = to_ml_features_vectorized(z_ratios)

# Add to DataFrame for model training
df['cos_moon_sun'] = features[:, 0]
df['sin_moon_sun'] = features[:, 1]
df['moon_sun_progress'] = features[:, 2]
```

### 3. Phase Synchronization Analysis

```python
from ketu.complex import phase_locking_value, ZodiacPoint

# Compare volatility cycles with planetary cycles
vol_phases = [ZodiacPoint.from_radians(p) for p in volatility_phases]
planet_phases = [ZodiacPoint.from_degrees(d) for d in planet_longitudes]

plv = phase_locking_value(vol_phases, planet_phases)
print(f"Phase synchronization: {plv:.3f}")
```

## Convention Notes

- **Internal**: All calculations use **radians**
- **User-facing**: Degrees for input/output when convenient
- **Complex numbers**: Always normalized to unit circle (|z| = 1)
- **Separation direction**: Measured counterclockwise (positive direction on zodiac)

## References

- Fisher, N. I. (1993). *Statistical Analysis of Circular Data*
- Mardia, K. V., & Jupp, P. E. (2000). *Directional Statistics*
- Lachaux, J. P., et al. (1999). "Measuring phase synchrony in brain signals"
