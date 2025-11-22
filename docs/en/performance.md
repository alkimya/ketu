# Performance Guide

Ketu v0.3.0 uses pure NumPy vectorization to achieve massive performance improvements over the previous version.

## Benchmarks

### Time Series Calculations

For computing planetary positions over 365 days:

- **208x faster** than loop-based approach
- From ~3.2s to ~15ms for a full year

### Aspect Calculations

For detecting all aspects between planets:

- **14.55x faster** with vectorization
- From ~120ms to ~8ms per date

### Single Position Calculations

For computing individual planet positions:

- **67x faster** for outer planets
- **59x faster** for Moon calculations
- Optimized Kepler solver with Newton-Raphson method

## Vectorized Functions

### Batch Position Calculations

```python
import numpy as np
from ketu import utc_to_julian
from datetime import datetime, timedelta

# Calculate Sun positions for a year
dates = [datetime(2025, 1, 1) + timedelta(days=i) for i in range(365)]
jd_array = np.array([utc_to_julian(d) for d in dates])

# Use vectorized batch calculation
from ketu.ephemeris.planets import calc_planet_position_batch
positions = calc_planet_position_batch(jd_array, planet_id=0)  # Sun

# Extract components
longitudes = positions[:, 0]
latitudes = positions[:, 1]
distances = positions[:, 2]
```

### Vectorized Aspect Detection

```python
import ketu

# Calculate all aspects for multiple dates efficiently
aspects_batch = ketu.calculate_aspects_batch(jd_array)
```

## Optimization Techniques

### LRU Caching

The library uses `functools.lru_cache` with optimal cache sizes:

```python
from functools import lru_cache

@lru_cache(maxsize=1024)
def body_properties(jdate, body):
    # Cached for repeated calculations
    # 6.7x speedup vs no cache
    ...
```

### NumPy Broadcasting

All distance and angle calculations use NumPy broadcasting for efficient array operations:

```python
def distance(pos1, pos2):
    # Works with both scalars and arrays
    angle = np.abs(pos2 - pos1)
    return np.where(angle <= 180, angle, 360 - angle)
```

### Optimized Kepler Solver

The Kepler equation solver uses Newton-Raphson iteration with adaptive tolerance:

- Typical convergence in 3-5 iterations
- Adaptive epsilon based on eccentricity
- Vectorized for batch calculations

## Memory Efficiency

### Structured Arrays

Aspect results use structured NumPy arrays for efficient storage:

```python
# Compact storage with named fields
dtype = [('body1', 'i4'), ('body2', 'i4'),
         ('i_asp', 'i4'), ('orb', 'f8')]
aspects = np.zeros(num_aspects, dtype=dtype)
```

### In-Place Operations

Most calculations use in-place NumPy operations to minimize memory allocation.

## Best Practices

### Use Batch Functions

For time series analysis:

```python
# Good: Use batch functions
positions = calc_planet_position_batch(jd_array, planet_id)

# Avoid: Individual calls in a loop
positions = [calc_planet_position(jd, planet_id) for jd in jd_array]
```

### Pre-allocate Arrays

For large-scale calculations:

```python
import numpy as np

# Pre-allocate result array
results = np.zeros((len(dates), 6))

# Fill with batch calculation
results = calc_planet_position_batch(jd_array, planet_id)
```

### Cache Julian Day Conversions

```python
# Convert dates once
jd_array = np.array([utc_to_julian(d) for d in dates])

# Reuse for multiple calculations
sun_pos = calc_planet_position_batch(jd_array, 0)
moon_pos = calc_planet_position_batch(jd_array, 1)
```

## Performance Tips

1. **Use vectorized functions** for bulk operations
2. **Cache Julian dates** when computing multiple bodies
3. **Pre-allocate arrays** for large datasets
4. **Avoid Python loops** over dates - use NumPy arrays
5. **Reuse calculations** - leverage the LRU cache

## Profiling Your Code

To identify bottlenecks:

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your ketu code here
positions = ketu.positions(jday)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## Future Optimizations

Planned performance improvements:

- [ ] JIT compilation with Numba (optional)
- [ ] Parallel computation for independent bodies
- [ ] SIMD optimizations for coordinate transformations
- [ ] GPU acceleration for large-scale calculations (optional)
