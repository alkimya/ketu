# Phase 5: Complex Math Integration - Research

**Researched:** 2026-02-12
**Domain:** NumPy Complex Number Vectorization, Caching Strategies, Error Standardization
**Confidence:** HIGH

## Summary

Phase 5 unifies complex number mathematics into Ketu's cycle calculation engine while maintaining a degrees-based external API. The codebase already has strong foundations: `complex.py` provides ZodiacPoint and CycleRatio classes with vectorized NumPy functions, and `cycles/calculator.py` already uses complex math in lines 217-230. The challenge is threefold: (1) ensure all cycle calculations use complex arithmetic internally while outputting degrees, (2) vectorize the remaining Python loops in `ResonanceField._get_trace()`, and (3) consolidate the dual caching system (LRU cache decorators on individual calculations vs EphemerisCache for batch lookups).

Research reveals that NumPy complex operations provide 10-100x speedup over Python loops, making them ideal for astronomical calculations. The existing `complex.py` module demonstrates best practices with `np.exp(1j * radians)` for complex representation and `np.angle()` for conversion back to degrees. The dual caching strategy is appropriate: LRU cache for single-point ephemeris calls (pure functions with no side effects) and EphemerisCache for batch operations (structured data with disk persistence). These serve different use cases and should coexist.

**Primary recommendation:** Extend existing complex math usage from `cycles/calculator.py` to `resonance.py` using vectorized batch functions, standardize error messages with f-string context patterns, and document the intentional dual-cache architecture.

## Standard Stack

### Core Libraries

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| NumPy | 1.24+ (2.x preferred) | Complex number arrays, vectorization | Industry standard for numerical computing, 10-100x faster than Python loops |
| functools | stdlib | LRU caching decorator | Built-in, thread-safe, optimal for pure function memoization |
| Python | 3.10-3.13 | Language runtime | Project already tests across these versions (Phase 4) |

### Supporting Tools

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | current | Testing framework | Already in use, 241 tests passing |
| coverage.py | current | Test coverage | Phase 4 achieved 91.48% coverage |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| NumPy complex | Python complex | Python complex good for single values, NumPy essential for arrays |
| LRU cache | cachetools | cachetools adds TTL/LFU but adds dependency, stdlib sufficient here |
| Custom vectorization | Plain loops | Loops are 10-100x slower, vectorization is already demonstrated in codebase |

**Installation:**
No new dependencies required. All core libraries already in use.

## Architecture Patterns

### Pattern 1: Complex Numbers for Angular Arithmetic

**What:** Represent zodiac positions as points on the unit circle (z = e^(iθ)) for discontinuity-free calculation

**When to use:** Any angular separation, cycle phase, or aspect calculation

**Example from `ketu/complex.py`:**
```python
def degrees_to_complex(degrees: np.ndarray) -> np.ndarray:
    """Convert array of degrees to complex numbers on unit circle."""
    radians = np.deg2rad(degrees)
    return np.exp(1j * radians)

def cycle_ratio_vectorized(
    body1_degrees: np.ndarray,
    body2_degrees: np.ndarray
) -> np.ndarray:
    """Compute cycle ratios for arrays of positions."""
    z1 = degrees_to_complex(body1_degrees)
    z2 = degrees_to_complex(body2_degrees)
    return z1 / z2  # Angular separation via complex division
```

**Why it works:**
- No discontinuity at 0°/360° boundary
- Angular separation is complex division: z₁/z₂ = e^(i(θ₁-θ₂))
- Vectorized operations on entire arrays
- ML-friendly features (real, imag parts are continuous)

### Pattern 2: Batch Vectorization for Performance

**What:** Process entire timestamp arrays in vectorized operations instead of Python loops

**When to use:** Any operation over multiple timestamps (>10 points)

**Example from `ketu/cycles/calculator.py`:**
```python
# GOOD: Vectorized batch calculation (lines 217-230)
z_ratios = cycle_ratio_vectorized(result['body1_lon'], result['body2_lon'])
separation = complex_to_degrees(z_ratios)
result['angular_separation'] = separation
result['cycle_progress'] = separation / 360.0

# BAD: Python loop (from resonance.py lines 186-199)
for k, jd in enumerate(jds):
    res = calc_planet_position(jd, pid)  # Single call per iteration
    lon, lat, dist = res[0], res[1], res[2]
    # ... coordinate transformations ...
    _lons[k] = lon
```

**Migration path:**
Replace `calc_planet_position` loop with `calc_planet_position_batch`:
```python
# From ephemeris/planets.py line 24
from ketu.ephemeris.planets import calc_planet_position_batch

# Vectorized: all positions at once
positions = calc_planet_position_batch(jds, pid)  # Shape: (n, 6)
lons = positions[:, 0]  # Longitude column
lats = positions[:, 1]  # Latitude column
```

### Pattern 3: Dual Caching Strategy

**What:** Use LRU cache for single-point pure functions, EphemerisCache for batch operations with persistence

**When to use:**
- LRU cache: Pure functions with hashable arguments, called repeatedly with same inputs
- EphemerisCache: Batch timestamp arrays, cross-session persistence needed

**Example:**
```python
# LRU: Single-point ephemeris calculation (planets.py line 67)
@lru_cache(maxsize=128)
def calc_planet_position(jd: float, planet_id: int, flags: int = 0) -> np.ndarray:
    """Thread-safe memoization for repeated single JD lookups."""
    # Pure function: same inputs always return same output
    ...

# EphemerisCache: Batch operations with disk persistence
cache = EphemerisCache()  # ~/.ketu/ephemeris_cache/
cache.ensure_range(2025, 1, 2025, 12)  # Pre-compute and save to disk
lons, vels = cache.get_positions_vectorized(timestamps, body_id)  # 10x faster
```

**Why both:**
- LRU cache: ~0.01ms hit latency, no disk I/O, thread-safe decorator
- EphemerisCache: Pre-computed monthly files, cross-session persistence, vectorized batch API
- Different use cases: single-point vs batch, in-memory vs persistent

### Pattern 4: Error Messages with Context

**What:** Standardized error format with specific information for debugging

**When to use:** All ValueError and TypeError raises

**Current patterns from codebase:**
```python
# GOOD: Specific context (complex.py line 337)
raise ValueError(f"Unknown aspect: {aspect}")

# GOOD: Clear boundaries (lunar_calendar.py line 230)
raise ValueError(f"Need at least 2 new moons to define cycles, got {len(new_moons)}")

# INCOMPLETE: Missing what was received (cycles/calculator.py line 106)
raise ValueError(f"Unknown body: {body}")
# Better: f"Unknown body: {body}. Valid bodies: {list(BODY_INDICES.keys())}"
```

**Standardized template:**
```python
# For invalid arguments
raise ValueError(
    f"Invalid {parameter_name}: {received_value}. "
    f"Expected {constraint}. Valid options: {valid_values}"
)

# For type errors
raise TypeError(
    f"{parameter_name} must be {expected_type}, got {type(value).__name__}"
)
```

### Anti-Patterns to Avoid

- **Complex numbers in public API:** Users should see degrees (0-360), not complex numbers
- **Mixing cache strategies:** Don't use LRU cache for disk-backed data or EphemerisCache for single points
- **Python loops for batch operations:** Always prefer vectorized NumPy operations
- **Vague error messages:** Include received value, expected constraint, and valid options

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Complex angle arithmetic | Custom modulo 360 logic with discontinuities | `np.exp(1j * radians)` and `np.angle()` | No 0°/360° edge cases, vectorized, mathematically sound |
| Function memoization | Manual dict-based cache | `@lru_cache` decorator | Thread-safe, bounded size, zero-overhead syntax |
| Batch ephemeris | Loop over single-point API | `calc_planet_position_batch` | 10-100x faster, already implemented |
| Angle normalization | Manual if/else wrapping | `np.deg2rad()` → `np.angle()` → `np.rad2deg()` | Handles all edge cases, vectorized |

**Key insight:** NumPy's complex dtype and universal functions (ufuncs) handle all the edge cases and performance optimization. The existing `complex.py` module demonstrates these patterns correctly.

## Common Pitfalls

### Pitfall 1: Forgetting Complex-to-Degrees Conversion at API Boundary

**What goes wrong:** Internal complex numbers leak into user-facing output

**Why it happens:** Complex math is convenient internally, easy to forget conversion

**How to avoid:** All public functions return degrees/structured arrays, complex is strictly internal

**Warning signs:**
```python
# BAD: Returns complex array
def get_separation(lon1, lon2):
    z1 = degrees_to_complex(lon1)
    z2 = degrees_to_complex(lon2)
    return z1 / z2  # ⚠️ Complex output

# GOOD: Convert back to degrees
def get_separation(lon1, lon2):
    z1 = degrees_to_complex(lon1)
    z2 = degrees_to_complex(lon2)
    z_ratio = z1 / z2
    return complex_to_degrees(z_ratio)  # ✓ Degrees output
```

**Detection:** Type hints catch this - return type should be `np.ndarray[np.float64]` not `np.ndarray[np.complex128]`

### Pitfall 2: Using Wrong Cache for Use Case

**What goes wrong:** Performance degradation or incorrect behavior

**Why it happens:** Both caches exist, unclear when to use each

**How to avoid:** Decision matrix:

| Scenario | Use | Reason |
|----------|-----|--------|
| Single JD, pure calculation | LRU cache | In-memory, thread-safe, auto-managed |
| Array of timestamps | EphemerisCache | Vectorized batch API, 10x faster |
| Need cross-session persistence | EphemerisCache | Disk-backed monthly files |
| Function with side effects | Neither | Caching requires pure functions |

**Warning signs:**
- LRU cache with list/array arguments → Use batch API instead
- EphemerisCache for single timestamp → Use cached single-point function
- Cache miss rate >50% → Wrong cache strategy for access pattern

### Pitfall 3: Vectorization Breaking on Coordinate Transformations

**What goes wrong:** `resonance.py._get_trace()` uses loop for coordinate transforms (lines 186-199)

**Why it happens:** Coordinate functions (`ecliptic_to_equatorial`) not vectorized yet

**How to avoid:** Check if coordinate functions support arrays:

```python
# Current state (line 192-195)
for k, jd in enumerate(jds):
    x, y, z = spherical_to_rectangular(lon, lat, dist)
    obl = mean_obliquity(jd)
    xe, ye, ze = ecliptic_to_equatorial(x, y, z, obl)

# Need to verify: Can these functions take arrays?
# If yes: vectorize the entire block
# If no: Keep loop OR vectorize the coordinate functions first
```

**Detection:** Performance profiling shows loop dominates execution time

### Pitfall 4: Inconsistent Error Message Formats

**What goes wrong:** Users see different error styles across modules

**Why it happens:** Multiple developers, no documented standard

**How to avoid:** Enforce template in code review:

```python
# Inconsistent (current state)
raise ValueError(f"Unknown body: {body}")  # No suggestions
raise ValueError(f"Unknown planet ID: {planet_id}")  # Different wording
raise ValueError(f"Unknown aspect: {aspect}")  # No constraint info

# Standardized (target state)
raise ValueError(
    f"Unknown body: '{body}'. "
    f"Valid bodies: {', '.join(BODY_INDICES.keys())}"
)
raise ValueError(
    f"Unknown planet ID: {planet_id}. "
    f"Valid range: 0-12. See BODY_INDICES for mapping."
)
raise ValueError(
    f"Unknown aspect: '{aspect}'. "
    f"Valid aspects: {', '.join(ASPECTS.keys())}"
)
```

**Warning signs:** Error messages without context, inconsistent capitalization/punctuation

## Code Examples

Verified patterns from codebase:

### Example 1: Complex Number Cycle Calculation (Already Implemented)

From `ketu/cycles/calculator.py` lines 217-230:
```python
# 1. Calculate Cycle Ratio using Complex Numbers
# z_ratio = z_slower / z_faster = e^(i(θ₂ - θ₁))
z_ratios = cycle_ratio_vectorized(result['body1_lon'], result['body2_lon'])

# 2. Extract angular separation (0-360) and Cycle Progress
separation = complex_to_degrees(z_ratios)
result['angular_separation'] = separation
result['cycle_progress'] = separation / 360.0

# 3. Cycle Phases
# Waxing: 0 -> 180, Waning: 180 -> 360
result['cycle_phase'] = np.where(separation < 180, 1, -1).astype(np.int8)

# 4. Aspect Proximity (Vectorized Complex)
# Calculate angular distance to each aspect in radians
dist_matrix_rad = np.angle(z_ratios[:, np.newaxis] / MAJOR_ASPECTS_Z[np.newaxis, :])
```

**Status:** ✓ Already correctly implemented, serves as reference

### Example 2: Vectorized Batch Ephemeris Lookup

From `ketu/cache/ephemeris_cache.py` lines 283-387:
```python
def get_positions_vectorized(
    self,
    timestamps: list,
    body_id: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """Get longitude and velocity for a body across timestamps (vectorized).

    This is the fast path - uses numpy vectorized operations instead of
    Python loops. ~10x faster than get_positions_batch for large arrays.
    """
    n = len(timestamps)

    # Convert timestamps to components for vectorized processing
    years = np.array([ts.year for ts in timestamps], dtype=np.int32)
    months = np.array([ts.month for ts in timestamps], dtype=np.int32)
    days = np.array([ts.day for ts in timestamps], dtype=np.int32)
    fractions = np.array([
        (ts.hour + ts.minute / 60 + ts.second / 3600) / 24.0
        for ts in timestamps
    ], dtype=np.float32)

    # Process each unique month in batch
    for (year, month) in unique_months:
        mask = (years == year) & (months == month)
        # ... vectorized interpolation ...

    return longitudes, velocities
```

**Status:** ✓ Already implemented, should be used in `resonance.py`

### Example 3: Target Pattern for ResonanceField Vectorization

Migrate `resonance.py._get_trace()` from lines 186-199:
```python
# BEFORE: Python loop (slow)
def _get_trace(self, pid: int, jds: np.ndarray):
    n = len(jds)
    _lons = np.zeros(n)
    _lats = np.zeros(n)
    _decs = np.zeros(n)

    for k, jd in enumerate(jds):
        res = calc_planet_position(jd, pid)  # Single call
        lon, lat, dist = res[0], res[1], res[2]

        # Coordinate transformation (scalar)
        x, y, z = spherical_to_rectangular(lon, lat, dist)
        obl = mean_obliquity(jd)
        xe, ye, ze = ecliptic_to_equatorial(x, y, z, obl)
        ra, dec, _ = rectangular_to_spherical(xe, ye, ze)

        _lons[k] = lon
        _lats[k] = lat
        _decs[k] = dec

    return _lons, _lats, _decs

# AFTER: Vectorized batch (fast)
def _get_trace(self, pid: int, jds: np.ndarray):
    """Calculate 3D trace for a single body over many JDs (vectorized)."""
    # Batch ephemeris calculation
    positions = calc_planet_position_batch(jds, pid)  # Shape: (n, 6)
    lons = positions[:, 0]
    lats = positions[:, 1]
    dists = positions[:, 2]

    # Vectorized coordinate transformations
    # TODO: Verify if coordinate functions support array inputs
    # If not, these may need to remain in a loop temporarily
    obliquities = np.array([mean_obliquity(jd) for jd in jds])

    # Option A: If functions are vectorized
    xs, ys, zs = spherical_to_rectangular(lons, lats, dists)
    xes, yes, zes = ecliptic_to_equatorial(xs, ys, zs, obliquities)
    ras, decs, _ = rectangular_to_spherical(xes, yes, zes)

    # Option B: If functions are not vectorized, vectorize them first
    # OR accept the coordinate transformation loop as acceptable
    # since the ephemeris batch call is the primary bottleneck

    return lons, lats, decs
```

**Status:** Target implementation for Phase 5

### Example 4: Standardized Error Messages

Pattern from Phase 5 requirement QAL-01:
```python
# Template for ValueError with context
def _get_body_id(body: Union[str, int]) -> int:
    """Convert body name or ID to ID."""
    if isinstance(body, int):
        if not 0 <= body <= 12:
            raise ValueError(
                f"Body ID must be in range 0-12, got {body}. "
                f"See BODY_INDICES for valid mappings."
            )
        return body

    body_idx = np.where(bodies["name"] == body.encode())[0]
    if len(body_idx) == 0:
        valid_bodies = [b.decode() for b in bodies["name"]]
        raise ValueError(
            f"Unknown body: '{body}'. "
            f"Valid bodies: {', '.join(valid_bodies)}"
        )
    return int(bodies["id"][body_idx[0]])

# Template for TypeError with received type
def generate_cycle_series(timestamps: Union[np.ndarray, List[datetime]], ...):
    if not isinstance(timestamps, (np.ndarray, list)):
        raise TypeError(
            f"timestamps must be numpy array or list, "
            f"got {type(timestamps).__name__}"
        )
```

**Status:** Template to apply across all modules

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Modulo 360° arithmetic | Complex unit circle (z = e^(iθ)) | v0.4.0 (complex.py added) | No 0°/360° discontinuities, vectorization-friendly |
| Python loops for batch | NumPy vectorized operations | v0.4.0 (partial) | 10-100x speedup where applied |
| Single cache strategy | Dual cache (LRU + EphemerisCache) | v0.4.0 | Optimized for both single-point and batch access patterns |
| Ad-hoc error messages | Standardized context format | Phase 5 target | Better debugging, consistent UX |

**Deprecated/outdated:**
- Manual angle wrapping with `if angle > 360: angle -= 360` → Use `complex_to_degrees(degrees_to_complex(angle))`
- `calc_planet_position` in loops → Use `calc_planet_position_batch` for arrays
- Generic error messages → Include context with f-strings

**NumPy version transition:**
- NumPy 1.x reached EOL September 2025
- NumPy 2.x recommended for security patches and performance improvements
- Ketu should specify `numpy>=1.24,<3.0` for compatibility

## Open Questions

1. **Are coordinate transformation functions vectorized?**
   - What we know: `spherical_to_rectangular`, `ecliptic_to_equatorial`, etc. exist in `ephemeris/coordinates.py`
   - What's unclear: Do they accept NumPy arrays or only scalars?
   - Recommendation: Test with array inputs; if not vectorized, decide between (a) vectorizing them first or (b) accepting coordinate loop as acceptable since ephemeris batch is the main bottleneck

2. **Should we remove LRU cache in favor of EphemerisCache only?**
   - What we know: Both caches serve different use cases, both are used in codebase
   - What's unclear: CPX-03 requirement says "single coherent caching strategy"
   - Recommendation: Interpret "coherent" as "documented and intentional" not "single implementation". Keep both, document when to use each (Pattern 3 above)

3. **What is the error message capitalization standard?**
   - What we know: Python convention is lowercase start, no period
   - What's unclear: Current codebase has mixed patterns
   - Recommendation: Follow Python convention: lowercase start, no period, specific context

4. **Should complex numbers be exposed in structured array dtypes?**
   - What we know: CYCLE_DTYPE uses float fields, complex math is internal only
   - What's unclear: Any benefit to adding complex field to structured array?
   - Recommendation: Keep degrees in structured arrays (user-facing), complex purely internal (computation-facing)

## Sources

### Primary (HIGH confidence)

- Ketu codebase analysis:
  - `/home/loc/workspace/solaris/ketu/ketu/complex.py` - Complex number implementation
  - `/home/loc/workspace/solaris/ketu/ketu/cycles/calculator.py` - Already uses complex math (lines 217-230)
  - `/home/loc/workspace/solaris/ketu/ketu/cache/ephemeris_cache.py` - Vectorized batch API
  - `/home/loc/workspace/solaris/ketu/ketu/resonance.py` - Target for vectorization
  - `/home/loc/workspace/solaris/ketu/.planning/REQUIREMENTS.md` - Phase 5 requirements
  - Test coverage: 241 tests passing, 91.48% coverage (Phase 4 complete)

### Secondary (MEDIUM confidence)

- [NumPy Structured Arrays Documentation](https://numpy.org/doc/stable/user/basics.rec.html) - Official NumPy docs on structured arrays
- [Python functools.lru_cache Documentation](https://docs.python.org/3/library/functools.html) - Official Python docs on LRU caching
- [Real Python: LRU Cache Strategy](https://realpython.com/lru-cache-python/) - Best practices for function memoization
- [NumPy Vectorization Guide](https://www.geeksforgeeks.org/numpy/vectorized-operations-in-numpy/) - Performance benefits of vectorization
- [Python Exception Handling Best Practices](https://realpython.com/python-raise-exception/) - Error message conventions

### Tertiary (LOW confidence, marked for validation)

- [Towards Data Science: NumPy Vectorization Speedup](https://towardsdatascience.com/how-to-speedup-data-processing-with-numpy-vectorization-12acac71cfca/) - Claims 10-100x speedup (validated against actual Ketu codebase comments)
- [Python Error Types Guide](https://middleware.io/blog/python-error-types/) - General error handling patterns

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries already in use, versions verified in pyproject.toml
- Architecture patterns: HIGH - Patterns extracted from working codebase (complex.py, cycles/calculator.py)
- Common pitfalls: HIGH - Identified from actual code patterns and Phase 4 test coverage work
- Vectorization benefits: MEDIUM-HIGH - NumPy documentation + verified in codebase comments ("10x faster")
- Error message conventions: MEDIUM - Python docs confirm, but existing codebase has mixed patterns

**Research date:** 2026-02-12
**Valid until:** 2026-05-12 (90 days - NumPy/Python stdlib are stable)

**Key finding:** Phase 5 is not a full rewrite but surgical integration. The complex math infrastructure already exists and is partially integrated. Main tasks are:
1. Extend complex math usage to resonance.py (vectorize `_get_trace`)
2. Document and clarify the dual-cache architecture (not remove one)
3. Standardize error messages with f-string context template
4. Update type hints to reflect degrees output from complex-math internals
