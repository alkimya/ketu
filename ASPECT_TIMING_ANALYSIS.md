# Aspect Timing Analysis: Mathematical Approaches

## Problem Statement

Find the beginning, exact moment, and end of an aspect between two celestial bodies.

**Mathematical formulation:**
```
We need to solve: |long₁(t) - long₂(t)| = aspect_angle ± orb
```

Where:
- `long₁(t)`, `long₂(t)` = ecliptic longitudes as functions of time
- `aspect_angle` = target angle (0°, 60°, 90°, 120°, 180°)
- `orb` = tolerance in degrees

**Complications:**
1. Non-linear functions (elliptical orbits + perturbations)
2. Retrograde motion (derivative changes sign)
3. Modulo 360° arithmetic (shortest angular distance)
4. Multiple solutions possible (planet can retrograde during aspect)

---

## Current Implementation

### Method: Linear Search + Binary Search

```python
# Step 1: Linear search backward/forward (0.25 day steps)
for _ in range(400):  # Max 100 days
    if abs(distance - aspect_angle) > orb:
        break

# Step 2: Binary search for exact moment
exact_jd = find_exact_aspect(jd_begin, jd_end, body1, body2, aspect_value)
```

**Performance:**
- Linear search: O(n) with n ≈ 400 iterations per direction
- Binary search: O(log n) ≈ 50 iterations
- Total: ~850 planetary position calculations per aspect

**Problems:**
- Slow for large time ranges
- Fixed step size misses fast-moving aspects
- Doesn't detect multiple solutions (retrograde cases)

---

## Proposed Approaches

### Approach 1: Analytical Solution (Ideal but Impractical)

**Theory:**
Solve the differential equation directly using Kepler's equation.

**Advantages:**
- Exact solution
- No iterations needed

**Disadvantages:**
- Extremely complex for geocentric positions
- Aberration, nutation, precession make it intractable
- Doesn't handle perturbations well
- Multiple planets = coupled equations

**Verdict:** ❌ Too complex for practical implementation

---

### Approach 2: Newton-Raphson Method (Fast & Accurate)

**Theory:**
Use derivative information to converge faster.

```python
def find_exact_aspect_newton(jd_initial: float, body1: int, body2: int, aspect_angle: float):
    """Find exact aspect using Newton-Raphson method."""

    def f(t):
        # Function: angular_distance(t) - aspect_angle
        pos1 = long(t, body1)
        pos2 = long(t, body2)
        return distance(pos1, pos2) - aspect_angle

    def f_prime(t):
        # Derivative: relative velocity
        v1 = vlong(t, body1)
        v2 = vlong(t, body2)
        return v1 - v2  # Simplified (needs sign correction)

    t = jd_initial
    for _ in range(20):  # Much fewer iterations than bisection
        t_new = t - f(t) / f_prime(t)
        if abs(t_new - t) < 0.0001:  # ~10 seconds precision
            return t_new
        t = t_new

    return None
```

**Advantages:**
- Quadratic convergence (much faster than bisection)
- Uses velocity data we already calculate
- Typically converges in 5-10 iterations

**Disadvantages:**
- Requires careful derivative handling
- Can diverge if initial guess is poor
- Derivative discontinuities at retrograde stations

**Performance:** ~20 calculations vs ~50 for bisection (2.5x faster)

---

### Approach 3: Velocity-Based Smart Search (Robust & Fast)

**Theory:**
Use relative velocity to predict aspect timing, then refine.

```python
def find_aspect_timing_smart(jdate: float, body1: int, body2: int, aspect_angle: float):
    """Smart aspect timing using velocity prediction."""

    # Get current state
    pos1, pos2 = long(jdate, body1), long(jdate, body2)
    vel1, vel2 = vlong(jdate, body1), vlong(jdate, body2)

    current_distance = distance(pos1, pos2)
    relative_velocity = vel1 - vel2  # degrees/day

    # Linear approximation for time to exact aspect
    angle_to_travel = aspect_angle - current_distance
    estimated_time = angle_to_travel / relative_velocity

    # Check for retrograde during aspect period
    if is_retrograde_crossing(jdate, jdate + estimated_time, body1, body2):
        # Handle special case: multiple solutions possible
        return find_multiple_solutions(...)

    # Refine with Newton-Raphson
    exact_time = newton_raphson_refine(jdate + estimated_time, ...)

    # Find orb boundaries using same technique
    orb_value = get_orb(body1, body2, aspect_index)
    begin_time = find_crossing(aspect_angle - orb_value, ...)
    end_time = find_crossing(aspect_angle + orb_value, ...)

    return begin_time, exact_time, end_time
```

**Advantages:**
- Fast initial estimation using linear approximation
- Detects retrograde crossings
- Handles multiple solutions
- Adaptive to planetary speeds

**Disadvantages:**
- More complex implementation
- Need to handle retrograde detection carefully

**Performance:** ~10-50 calculations (10-80x faster than current)

---

### Approach 4: Vectorized Grid Search + Interpolation (Modern)

**Theory:**
Pre-calculate positions on a dense grid, use NumPy to find crossings.

```python
def find_aspect_timing_vectorized(jd_start: float, jd_end: float, body1: int, body2: int):
    """Vectorized aspect finding using grid search."""

    # Create time grid (adaptive based on planetary speeds)
    avg_speed = (bodies["speed"][body1] + bodies["speed"][body2]) / 2
    time_resolution = 0.1 / avg_speed  # 0.1° resolution

    jd_array = np.arange(jd_start, jd_end, time_resolution)

    # Calculate all positions at once (vectorized!)
    positions1 = calc_planet_position_batch(jd_array, body1)[:, 0]
    positions2 = calc_planet_position_batch(jd_array, body2)[:, 0]

    # Calculate all angular distances
    distances = distance(positions1, positions2)

    # Find where distance crosses aspect_angle
    differences = distances - aspect_angle
    sign_changes = np.where(np.diff(np.sign(differences)))[0]

    # Refine each crossing with interpolation
    exact_times = []
    for idx in sign_changes:
        # Linear interpolation for sub-step precision
        t1, t2 = jd_array[idx], jd_array[idx+1]
        d1, d2 = differences[idx], differences[idx+1]
        exact_jd = t1 - d1 * (t2 - t1) / (d2 - d1)
        exact_times.append(exact_jd)

    return exact_times
```

**Advantages:**
- Leverages NumPy vectorization (very fast)
- Naturally finds all crossings (handles retrograde)
- Adaptive grid based on planetary speeds
- No iteration needed for search

**Disadvantages:**
- Memory usage for large time ranges
- Needs refinement step for high precision

**Performance:** 1000+ days analyzed in milliseconds

---

## Retrograde Motion Handling

### Problem

When a planet retrogrades during an aspect:

```
     approach → ← retreat → approach again
t0: |--------★========★--------|
         1st      2nd crossing
        exact    exact
```

There can be **3 exact moments** for a single aspect:
1. Approaching (direct)
2. Retreating (retrograde begins)
3. Approaching again (direct resumes)

### Detection Strategy

```python
def detect_retrograde_during_aspect(jd_start: float, jd_end: float, body: int) -> List[float]:
    """Find retrograde stations within time range."""

    # Find where vlong(t) = 0 (retrograde station)
    stations = []

    # Use derivative sign change detection
    step = 0.5  # Half-day steps
    jd = jd_start
    prev_retrograde = is_retrograde(jd, body)

    while jd < jd_end:
        jd += step
        curr_retrograde = is_retrograde(jd, body)

        if curr_retrograde != prev_retrograde:
            # Station detected, refine timing
            exact_station = find_station_exact(jd - step, jd, body)
            stations.append(exact_station)

        prev_retrograde = curr_retrograde

    return stations
```

---

## Recommendation

**Best approach: Hybrid (Approach 3 + 4)**

### Phase 1: Vectorized Detection
- Use vectorized grid search for initial detection
- Finds all crossings (handles retrograde automatically)
- Fast even for long time ranges

### Phase 2: Newton-Raphson Refinement
- Refine each crossing to high precision
- Uses velocity data for fast convergence
- Achieves second-level accuracy

### Implementation Plan

1. **New function:** `find_aspect_timing_hybrid()`
2. **Leverage existing:** `calc_planet_position_batch()` (already vectorized)
3. **Add:** Newton-Raphson refinement
4. **Test:** Compare with current method for accuracy
5. **Benchmark:** Measure speedup

### Expected Performance

- Current: ~850 calculations per aspect
- Hybrid: ~50-100 calculations per aspect
- **Speedup: 8-15x faster**
- **Bonus: Correctly handles retrograde cases**

---

## Questions for Discussion

1. **Precision requirements:** Is 0.001 days (~1.5 minutes) sufficient, or do we need second-level precision?

2. **Retrograde handling:** Should we return all 3 exact moments, or just the "strongest" (closest to perfect aspect)?

3. **API design:** Keep current signature `(begin, exact, end)` or return list of all crossings?

4. **Backward compatibility:** Replace current method or add new method alongside?

5. **Performance vs accuracy:** Is 10x speedup worth the added complexity?

---

## Next Steps

Please review and let me know:
- Which approach do you prefer?
- Should we handle retrograde with multiple solutions?
- Any specific use cases to optimize for?
