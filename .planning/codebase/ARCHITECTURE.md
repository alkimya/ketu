# Architecture

**Analysis Date:** 2026-02-12

## Pattern Overview

**Overall:** Layered astronomical library with specialized modules for ephemeris calculations, aspect detection, and cycle analysis.

**Key Characteristics:**
- NumPy-first design for vectorized operations and ML compatibility
- Modular separation of concerns: ephemeris (raw calculations) → aspects (events) → cycles (time series)
- LRU caching for repeated calculations
- Structured arrays (CYCLE_DTYPE, ASPECT_DTYPE) for direct ML/Pandas interop
- Optional dependencies (matplotlib, icalendar) with graceful degradation
- Pure Python with numpy only as core dependency; independent of swisseph

## Layers

**Ephemeris Layer (Core Astronomical Calculations):**
- Purpose: Compute raw planetary positions, velocities, and coordinates at any Julian date
- Location: `ketu/ephemeris/`
- Contains:
  - `time.py`: Julian day conversions, delta-T, terrestrial/universal time
  - `orbital.py`: Kepler equation solving, orbital element interpolation, perturbation corrections
  - `planets.py`: Body position calculations, batch operations, speed ratios
  - `coordinates.py`: Spherical/rectangular conversion, ecliptic/equatorial transformation
- Depends on: numpy only
- Used by: calculations layer, cycles layer, aspects layer

**Calculations Layer (High-Level Position API):**
- Purpose: Expose user-friendly position and velocity functions with caching
- Location: `ketu/calculations.py`
- Contains:
  - Position functions: `long()`, `latitude()`, `dist_au()`
  - Velocity functions: `vlong()` (velocity, not position)
  - Analysis: `is_retrograde()`, `is_ascending()`, `body_sign()`
  - Utilities: `distance()` (angular), `body_properties()` (cached)
  - Time conversion wrappers
- Depends on: ephemeris layer, core data structures (bodies, aspects, signs)
- Used by: aspects layer, cycles layer, display module

**Aspects Layer (Discrete Event Detection):**
- Purpose: Find planetary aspect events (exact moments, windows, timelines)
- Location: `ketu/aspects/`
- Contains:
  - `core.py`: Low-level algorithms (binary search refinement, LRU caching, position grids)
  - `calculator.py`: High-level API (get_aspect, calculate_aspects, vectorized variants)
  - `windows.py`: Aspect window detection (entry/exact/exit moments with precise timing)
  - `timelines.py`: ML-ready aspect timelines (discrete events as structured arrays)
  - `transits.py`: Transit calculations (planetary transit to natal position)
- Depends on: calculations layer, core data structures, ephemeris (batch positions)
- Used by: lunar_calendar, display module, client code

**Cycles Layer (Continuous Time Series):**
- Purpose: Generate cycle state at each timestamp (phase, separation, velocity, aspect proximity)
- Location: `ketu/cycles/`
- Contains:
  - `calculator.py`: CycleState dataclass, CYCLE_DTYPE, generate_cycle_series, generate_multi_cycle_series
  - Structured array format optimized for correlation with OHLCV price data
- Depends on: calculations layer, complex representation, ephemeris (batch positions), optional cache
- Used by: client code (Kala, Solaris), resonance field

**Complex Representation Layer (ML Features):**
- Purpose: Convert degrees to complex numbers for circular statistics and ML features
- Location: `ketu/complex.py`
- Contains:
  - ZodiacPoint, CycleRatio dataclasses
  - Aspect definitions (roots of unity)
  - Circular mean/std, phase locking value
  - degrees_to_complex, cycle_ratio_vectorized, to_ml_features_vectorized
- Depends on: numpy
- Used by: cycles layer, resonance field, client ML code

**Resonance Field Layer (Continuous Pressure Fields):**
- Purpose: Transform discrete planetary positions into continuous Gaussian pressure fields
- Location: `ketu/resonance.py`
- Contains: ResonanceField class with compute_field for harmonic/declination/latitude resonance
- Depends on: ephemeris, complex representation
- Used by: Surya agent framework

**Export Layer (Optional Outputs):**
- Purpose: Generate charts (matplotlib) and iCalendar exports (optional dependencies)
- Location: `ketu/export/`
- Contains:
  - `chart.py`: SVG zodiacal charts (requires matplotlib)
  - `icalendar.py`: iCal export for lunations/transits/aspects (requires icalendar)
  - `constants.py`: BIG_FIVE and other display constants
- Depends on: calculations layer, aspects layer
- Used by: display module, client code

**Display/CLI Layer:**
- Purpose: User-facing CLI and formatted output functions
- Location: `ketu/display.py`
- Contains: print_positions(), print_aspects(), main() CLI entry point
- Depends on: calculations, aspects, core data structures
- Used by: CLI users, scripts

**Lunar Calendar Layer:**
- Purpose: Generate lunar calendars with aspect windows aligned to lunar cycles
- Location: `ketu/lunar_calendar.py`
- Contains: LunarCycle, LunarCalendar dataclasses, generate_lunar_calendar()
- Depends on: calculations, aspects (find_aspect_window), export constants
- Used by: client code needing lunar-aligned timings

**Core Data Structures:**
- Purpose: Define canonical bodies, aspects, signs used throughout library
- Location: `ketu/core.py`
- Contains:
  - bodies: numpy structured array [name, id, orb, speed]
  - aspects: numpy structured array [name, angle, coef]
  - signs: list of zodiac sign names
- Depends on: numpy
- Used by: All layers

## Data Flow

**Computational Path (Ephemeris → Cycles):**

1. **Input:** Timestamps (datetime or Julian dates) + body pairs (names or IDs)
2. **Ephemeris computation:** `calc_planet_position_batch()` (vectorized, with optional caching)
3. **Position extraction:** Body longitudes, latitudes, velocities (degrees, degrees/day)
4. **Cycle calculation:** Angular separation, cycle progress (0-360°, 0-1.0), relative velocity
5. **Aspect proximity:** Distance to nearest major aspect (signed orb)
6. **Output:** CYCLE_DTYPE structured array for direct Pandas/NumPy operations

**Aspect Event Detection Path:**

1. **Input:** Two bodies + aspect type + date range
2. **Coarse search:** Grid search over date range (daily steps by default)
3. **Fine detection:** Binary search around candidate grid points
4. **Refinement:** Bisection to find exact moment (1e-7 tolerance)
5. **Window calculation:** Entry time (approaching), exact time (orb = 0), exit time (separating)
6. **Output:** AspectMoment/AspectWindow objects with precise timestamps

**ML Feature Path:**

1. **Input:** CYCLE_DTYPE structured array from cycles layer
2. **Transformation:** Complex representation (degrees → e^iθ)
3. **Normalization:** Circular statistics (mean, std, PLV)
4. **Feature extraction:** (cos(θ), sin(θ)) for linear ML models
5. **Output:** ML-ready feature matrix

## Key Abstractions

**CYCLE_DTYPE (Cycle State Snapshot):**
- Purpose: Immutable structured array format for cycle state at one timestamp
- Location: `ketu/cycles/calculator.py`
- Fields: julian_day, body1_lon, body2_lon, angular_separation, cycle_progress, cycle_phase, relative_velocity, nearest_aspect, aspect_distance, in_aspect
- Used for: Direct serialization to Pandas, correlation analysis, time series alignment with OHLCV

**CycleState (Cycle State Dataclass):**
- Purpose: Type-safe Python object representation of cycle state
- Contains: Same fields as CYCLE_DTYPE but as dataclass attributes
- Used for: Python API, single-point calculations, type hints

**AspectWindow/AspectMoment:**
- Purpose: Discrete event representation with precise timing
- Location: `ketu/aspects/windows.py`
- Contains: entry_time, exact_time, exit_time, orb, aspect_name, bodies, applying/separating
- Used for: Lunar calendar generation, transit tables, event-based analysis

**ZodiacPoint/CycleRatio:**
- Purpose: Complex number representation on unit circle
- Location: `ketu/complex.py`
- Properties: Angle in degrees/radians, complex form, nearest aspect, cycle phase
- Used for: Circular statistics, ML feature engineering, aspect proximity

**ResonanceField:**
- Purpose: Continuous harmonic pressure field over time
- Contains: Method compute_field() that returns DataFrame with harmonic/declination/latitude resonance scores
- Used for: Surya agent input, continuous signal generation

## Entry Points

**Public API (ketu/__init__.py):**
- Location: `ketu/__init__.py`
- Exports: ~60+ functions and classes
- Triggers: Client code importing from ketu
- Responsibilities:
  - Time conversion: utc_to_julian, julian_to_utc, local_to_utc
  - Positions: longitude, latitude, positions, velocities
  - Aspects: calculate_aspects, find_aspect_timing, find_aspects_between_dates
  - Advanced: generate_aspect_timeline, generate_cycle_series, ResonanceField
  - Display: print_positions, print_aspects

**CLI Entry Point:**
- Location: `ketu/display.py::main()`
- Command: `ketu` (installed as script via setuptools)
- Triggers: User runs `ketu` command
- Responsibilities: Interactive date/time input, compute positions and aspects, display results

**Module Entry Points:**
- Cycles: `generate_cycle_series(body1, body2, timestamps)` in `ketu/cycles/__init__.py`
- Aspects: `find_aspect_window(body1, body2, aspect, around_date)` in `ketu/aspects/`
- Lunar: `generate_lunar_calendar(year, month)` in `ketu/lunar_calendar.py`
- Resonance: `ResonanceField(bodies, harmonics).compute_field(start, end)` in `ketu/resonance.py`

## Error Handling

**Strategy:** Raise informative exceptions for invalid inputs; use optional dependencies with graceful degradation

**Patterns:**

1. **Body/Aspect validation:** ValueError with message "Unknown body: {name}" or "Unknown aspect: {name}"
   - Examples: `_get_body_id()` in cycles/calculator.py, `get_aspect_index()` in aspects/core.py

2. **Optional dependencies:** Try/except ImportError with _AVAILABLE flags
   - Example: Export module conditionally loads matplotlib/icalendar; __init__.py extends __all__ only if available

3. **Time computations:** Use numpy for vectorization; propagate NaN for missing values (by default)

4. **Aspect/Transit searches:** Return None if no aspect found within search window

## Cross-Cutting Concerns

**Logging:** Not implemented (no logging framework dependency); uses print() for debug/display functions

**Validation:**
- Time: Must be datetime with timezone (tzinfo) or float (Julian date)
- Bodies: By name (string) or ID (int, 0-12)
- Aspects: By name (string), index (int, 0-13), or angle (float degrees)
- Timestamps: Must be convertible to Julian dates (datetime or numeric array)

**Authentication:** Not applicable (library has no external service calls)

**Caching Strategy:**
- **Ephemeris calculations:** LRU cache (256 entries) in `aspects/core.py::_cached_planet_position_batch()`
- **Body properties:** LRU cache (1024 entries) in `calculations.py::body_properties()`
- **Cycle calculations:** Optional EphemerisCache for pre-computed daily positions (100x speedup for repeated queries)

**Thread Safety:** Not guaranteed; LRU caches are thread-safe but calculations themselves are not explicitly protected

## Key Dependencies

- **numpy (required):** Structured arrays, vectorized operations, broadcasting
- **matplotlib (optional):** Chart visualization
- **icalendar (optional):** Calendar export
- **swisseph (removed in v0.4.0):** Replaced with pure Python ephemeris calculations

---

*Architecture analysis: 2026-02-12*
