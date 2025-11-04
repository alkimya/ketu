# Vectorization and Performance Guide

This guide explains the vectorized functions in Ketu and how to use them for maximum performance.

## Overview

Ketu has been extensively optimized using pure NumPy vectorization, achieving **massive performance gains** without requiring JIT compilation or additional dependencies:

- **Time series (365 days)**: 208x faster
- **Aspect calculations (365 days)**: 14.55x faster
- **Single planet position**: 67x faster
- **Moon position**: 59x faster

All optimizations maintain **exact numerical compatibility** with the original implementations.

## Vectorized Functions

### 1. Planet Position Calculations

#### `calc_planet_position_batch(jd_array, planet_id, flags=0)`

Calculate planet positions for multiple dates efficiently.

**Location**: `ketu.ephemeris.planets`

**Performance**: ~15-67x faster than loop-based approach

**Example**:
```python
import numpy as np
from ketu.ephemeris.planets import calc_planet_position_batch
from ketu.ephemeris.time import utc_to_julian
from datetime import datetime, timedelta

# Calculate Sun positions for a year
start_date = datetime(2020, 1, 1)
dates = [start_date + timedelta(days=i) for i in range(365)]
jd_array = np.array([utc_to_julian(d) for d in dates])

# Vectorized calculation (super fast!)
results = calc_planet_position_batch(jd_array, 0)  # 0 = Sun

# Extract components
longitudes = results[:, 0]  # Ecliptic longitude
latitudes = results[:, 1]   # Ecliptic latitude
distances = results[:, 2]   # Distance in AU
lon_speeds = results[:, 3]  # Longitude velocity
```

**Planet IDs**:
- 0: Sun, 1: Moon, 2: Mercury, 3: Venus, 4: Mars
- 5: Jupiter, 6: Saturn, 7: Uranus, 8: Neptune, 9: Pluto
- 10: Rahu (mean node), 11: North Node (true node), 12: Lilith

**Returns**: 2D array of shape (n_dates, 6) with columns:
- [0] longitude (degrees)
- [1] latitude (degrees)
- [2] distance (AU)
- [3] longitude speed (degrees/day)
- [4] latitude speed (degrees/day)
- [5] distance speed (AU/day)

---

### 2. Aspect Calculations

#### `calculate_aspects_vectorized(jdate, l_bodies=bodies)`

Calculate all aspects for a single date using vectorized operations.

**Location**: `ketu.ketu_refactored`

**Performance**: 8.28x faster than loop-based approach

**Example**:
```python
from ketu import ketu_refactored
from ketu.ephemeris.time import utc_to_julian
from datetime import datetime

jd = utc_to_julian(datetime(2020, 12, 21, 18, 0))

# Vectorized aspect calculation
aspects = ketu_refactored.calculate_aspects_vectorized(jd)

# Process results
for aspect in aspects:
    body1_id = aspect['body1']
    body2_id = aspect['body2']
    aspect_type = aspect['i_asp']  # 0=conjunction, 1=semi-sextile, etc.
    orb = aspect['orb']            # Orb in degrees

    print(f"{body1_id}-{body2_id}: aspect {aspect_type}, orb {orb:.2f}°")
```

**Returns**: Structured NumPy array with fields:
- `body1` (int): First body ID
- `body2` (int): Second body ID
- `i_asp` (int): Aspect type index
- `orb` (float): Orb value in degrees

**Aspect indices**:
- 0: Conjunction (0°)
- 1: Semi-sextile (30°)
- 2: Sextile (60°)
- 3: Square (90°)
- 4: Trine (120°)
- 5: Quincunx (150°)
- 6: Opposition (180°)

---

#### `calculate_aspects_batch(jd_array, l_bodies=bodies)`

Calculate aspects for multiple dates efficiently.

**Location**: `ketu.ketu_refactored`

**Performance**: 14.55x faster for 365-day time series

**Example**:
```python
import numpy as np
from ketu import ketu_refactored
from ketu.ephemeris.time import utc_to_julian
from datetime import datetime, timedelta

# Create array of dates
start = datetime(2020, 1, 1)
dates = [start + timedelta(days=i) for i in range(365)]
jd_array = np.array([utc_to_julian(d) for d in dates])

# Batch aspect calculation
aspects_by_date = ketu_refactored.calculate_aspects_batch(jd_array)

# Process results
for i, aspects in enumerate(aspects_by_date):
    print(f"Day {i}: {len(aspects)} aspects")
    for aspect in aspects:
        # Same structure as calculate_aspects_vectorized
        pass
```

**Returns**: List of structured arrays, one per date

---

### 3. Low-Level Vectorized Functions

These functions are used internally but can also be called directly for advanced use cases.

#### `get_body_position_vectorized(body_id, jd_array)`

Calculate heliocentric positions for multiple dates.

**Location**: `ketu.ephemeris.orbital`

**Example**:
```python
from ketu.ephemeris.orbital import get_body_position_vectorized
import numpy as np

jd_array = np.array([2459205.0, 2459206.0, 2459207.0])

# Get Earth positions (for Sun geocentric calculation)
x, y, z, lon, lat, r = get_body_position_vectorized(0, jd_array)

print(f"Positions: {lon}")  # Array of longitudes
```

---

#### `get_moon_position_vectorized(jd_array)`

Calculate geocentric Moon positions for multiple dates.

**Location**: `ketu.ephemeris.orbital`

**Example**:
```python
from ketu.ephemeris.orbital import get_moon_position_vectorized
import numpy as np

jd_array = np.array([2459205.0, 2459206.0, 2459207.0])
lon, lat, dist = get_moon_position_vectorized(jd_array)

print(f"Moon longitudes: {lon}")
```

---

## Performance Benchmarks

Run the benchmark suite to see performance on your system:

```bash
python tests/benchmark.py
```

Example output:
```
BENCHMARK 5: Time Series (365 days of Sun positions)
======================================================================

Original (pyswisseph):
  365 Sun positions:
    Mean:   94.85 ms

Refactored (NumPy, VECTORIZED):
  365 Sun positions (vectorized):
    Mean:   454.20 µs
    Speedup: 208.83x faster
```

Run aspect-specific benchmarks:
```bash
python tests/test_aspects_vectorization.py
```

Run vectorization validation:
```bash
python tests/test_vectorization.py
```

---

## Migration Guide

### From Loop-Based to Vectorized

**Before** (slow):
```python
# Calculate Sun for 365 days (slow)
results = []
for i in range(365):
    jd = base_jd + i
    pos = ketu_refactored.calc_planet_position(jd, 0)
    results.append(pos[0])  # longitude
```

**After** (208x faster):
```python
# Calculate Sun for 365 days (fast)
jd_array = base_jd + np.arange(365)
results = calc_planet_position_batch(jd_array, 0)
longitudes = results[:, 0]
```

### Aspect Calculations

**Before** (slow):
```python
# Calculate aspects for 365 days (slow)
aspects_list = []
for i in range(365):
    jd = base_jd + i
    aspects = ketu_refactored.calculate_aspects(jd)
    aspects_list.append(aspects)
```

**After** (14.55x faster):
```python
# Calculate aspects for 365 days (fast)
jd_array = base_jd + np.arange(365)
aspects_list = ketu_refactored.calculate_aspects_batch(jd_array)
```

---

## Technical Details

### Vectorization Strategy

1. **Kepler Equation Solver**: Modified to accept array inputs via NumPy broadcasting
2. **Orbital Calculations**: All trigonometric and algebraic operations vectorized
3. **Coordinate Transformations**: `rectangular_to_spherical` handles arrays automatically
4. **Distance Function**: Vectorized using `np.where` for conditional logic
5. **Aspect Detection**: Pairwise distance matrix computed for all body pairs simultaneously

### Memory Efficiency

Vectorized functions use NumPy's efficient array operations:
- 19% less memory than pyswisseph
- Contiguous memory allocation
- Minimal Python object overhead

### Precision

All vectorized functions maintain numerical precision:
- Position calculations: < 1e-8 degrees difference
- Aspect calculations: exact match with original
- Validated against Swiss Ephemeris

---

## Best Practices

### When to Use Vectorized Functions

✅ **Use vectorized functions when**:
- Calculating positions for multiple dates (time series)
- Generating ephemeris tables
- Analyzing aspect patterns over time
- Performance is important

❌ **Use scalar functions when**:
- Calculating single positions interactively
- Performance doesn't matter
- Debugging specific calculations

### Optimization Tips

1. **Batch size**: Optimal batch size is typically 30-365 days
2. **Reuse arrays**: Pre-allocate Julian date arrays for repeated calculations
3. **Cache clearing**: Clear LRU caches if memory is constrained
4. **Aspect filtering**: Filter aspects by type to reduce processing

### Example: Optimized Research Workflow

```python
import numpy as np
from datetime import datetime, timedelta
from ketu.ephemeris.time import utc_to_julian
from ketu.ephemeris.planets import calc_planet_position_batch
from ketu.ketu_refactored import calculate_aspects_batch

# Setup: 10 years of daily data
start = datetime(2010, 1, 1)
n_days = 3650
dates = [start + timedelta(days=i) for i in range(n_days)]
jd_array = np.array([utc_to_julian(d) for d in dates])

# Calculate all planet positions (vectorized - very fast!)
planet_data = {}
for planet_id in range(10):
    planet_data[planet_id] = calc_planet_position_batch(jd_array, planet_id)

# Calculate all aspects (vectorized - very fast!)
all_aspects = calculate_aspects_batch(jd_array)

# Analysis: Find all Jupiter-Saturn conjunctions
for i, aspects in enumerate(all_aspects):
    for asp in aspects:
        if asp['body1'] == 5 and asp['body2'] == 6 and asp['i_asp'] == 0:
            print(f"Jupiter-Saturn conjunction on {dates[i]}: orb {asp['orb']:.2f}°")

# This entire analysis completes in ~1 second thanks to vectorization!
```

---

## Limitations

1. **Perturbations**: Not fully vectorized yet (minor performance impact for outer planets)
2. **Nodes and Lilith**: Use scalar calculations (relatively fast anyway)
3. **Aberration correction**: Applied per-date in batch mode (could be vectorized further)

---

## Future Enhancements

Possible future optimizations (not currently needed):

1. **Numba JIT compilation**: Could provide additional 2-5x speedup
2. **Multi-threading**: For independent planetary calculations
3. **GPU acceleration**: For very large datasets (>10,000 dates)

However, current pure NumPy vectorization already provides **excellent performance** for typical use cases.

---

## Support

For questions or issues with vectorized functions:
1. Check benchmark results: `python tests/benchmark.py`
2. Validate correctness: `python tests/test_vectorization.py`
3. Report issues: https://github.com/alkimya/ketu/issues

---

**Performance Summary**: Pure NumPy vectorization provides 15-208x speedup across all core operations, making Ketu suitable for large-scale ephemeris research without requiring additional dependencies or JIT compilation.
