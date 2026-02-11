# Codebase Concerns

**Analysis Date:** 2026-02-12

## Test Coverage Gaps

### Failing Test in Aspect Vectorization

**Area:** Aspect calculations
- **Issue:** `test_aspects_correctness` in `tests/test_aspects_vectorization.py` fails intermittently with mismatched aspect count (30 vs 31 aspects)
- **Files:** `ketu/aspects/calculator.py`, `ketu/aspects/core.py`, `tests/test_aspects_vectorization.py`
- **What's missing:** Non-deterministic aspect filtering or ordering issue in vectorized path - one aspect is sometimes excluded
- **Risk:** Aspects may be dropped silently depending on calculation path, affecting trading signals or analysis
- **Priority:** High
- **Fix approach:** Investigate the vectorized aspect calculation logic in `ketu/aspects/core.py` and `ketu/aspects/calculator.py`. The issue likely lies in how aspects are filtered or deduplicated between `calculate_aspects` and `calculate_aspects_vectorized`. Need to ensure both code paths produce identical results.

### Untested Modules

**Areas with 0% or <20% coverage:**
- `ketu/cache/ephemeris_cache.py` - 0% coverage (436 lines)
  - Caching system for ephemeris lookups
  - No tests exist for cache hit/miss behavior, file I/O, or interpolation
  - Risk: Cache corruption, memory leaks, or stale data silently used

- `ketu/cycles/calculator.py` - 0% coverage (363 lines)
  - Core cycle series generation with vectorized complex math
  - Despite being heavily used, has no unit tests
  - Risk: Silent failures in cycle calculations affecting all downstream analysis

- `ketu/lunar_calendar.py` - 17% coverage (383 lines)
  - Large untested sections in lunar calendar generation (lines 138-174, 215-325, 340-373)
  - Risk: Lunar calendar exports may be incorrect without test verification

- `ketu/export/chart.py` - 9% coverage (654 lines)
  - Chart rendering logic almost entirely untested

- `ketu/export/icalendar.py` - 8% coverage (415 lines)
  - iCalendar export logic almost entirely untested

**Impact:** 38% of codebase untested. These are critical systems (caching, cycles, exports).

## Performance Bottlenecks

### Resonance Field Loop-Based Calculation

**Area:** 3D resonance field computation
- **Files:** `ketu/resonance.py` (lines 155-186)
- **Problem:** `_get_trace()` method uses explicit Python loop for time series calculation instead of vectorization
  ```python
  for k, jd in enumerate(jds):
      res = calc_planet_position(jd, pid)  # Single JD at a time
  ```
- **Impact:** For hourly calculation over 1 year (8,760 points), this is ~1000x slower than vectorized approach
- **Cause:** Comment at line 168-169 states "Let's stick to the loop for safety unless slow" - was a temporary choice
- **Fix approach:** Use `calc_planet_position_batch()` (available in `ketu/ephemeris/planets.py`) to vectorize position calculations for all JDs at once

### Cache Conversion Overhead

**Area:** Cycle calculation with caching
- **Files:** `ketu/cycles/calculator.py` (line 183-185)
- **Problem:** Converting numpy arrays to tuples for LRU caching
  ```python
  jd_tuple = tuple(jd_array.tolist())  # Converts array -> list -> tuple
  ```
- **Impact:** Conversion overhead for every cache lookup, even when timestamps are identical
- **Better approach:** Use custom cache key function or hashable array representation

## Architectural Fragility

### Velocity vs Position Function Names

**Area:** Function naming ambiguity
- **Files:** `ketu/__init__.py` (lines 46, 168), `ketu/calculations.py` (lines 168, 188)
- **Issue:** Functions `vlong()`, `vlat()`, `vdist_au()` return SPEED in degrees/day, not position, but the "v" prefix is ambiguous
- **Risk:** High likelihood of user confusion - "v" commonly means "velocity" but is used here for velocity magnitude
- **Current mitigation:** Explicit aliases exist (`longitude_velocity`, `latitude_velocity`) with docstring warnings
- **Concern:** Legacy code in the codebase might still use short names incorrectly
- **Fix approach:** Consider deprecating short names in next major version, encourage use of explicit aliases

### Complex Number Representation Not Fully Integrated

**Area:** Dual cycle representation systems
- **Files:** `ketu/complex.py` (632 lines), `ketu/cycles/calculator.py` (uses complex math), `ketu/resonance.py` (not using complex)
- **Issue:** Two different representations of cycles exist:
  1. Traditional angular separation (0-360°) - used in cycles/calculator.py
  2. Complex number representation (unit circle) - used in complex.py
  3. ResonanceField does not use complex math despite available tools
- **Impact:** Code duplication and confusion about which representation to use. ResonanceField recalculates harmonics manually (lines 110-117) when complex number tools could simplify it
- **Fix approach:** Consolidate to use complex representation consistently, or document when to use each approach

### Cache Optional But Untested

**Area:** Ephemeris caching system
- **Files:** `ketu/cache/ephemeris_cache.py`, `ketu/cycles/calculator.py` (lines 27-33, 179-185)
- **Issue:** Cache is optional (try/except ImportError), conditions for using cache are complex:
  ```python
  use_ephemeris_cache = (
      use_cache and
      CACHE_AVAILABLE and
      hasattr(timestamps, 'to_pydatetime') or  # BUG: operator precedence issue!
      (isinstance(timestamps, (list, np.ndarray)) and len(timestamps) > 0)
  )
  ```
- **Risk:** Due to operator precedence, this may evaluate incorrectly. Parentheses needed: `... and (hasattr(...) or ...)`
- **Impact:** Cache might not be used when intended or vice versa, with no visibility into what happened
- **Fix approach:** Fix operator precedence, add logging to show which path was taken, ensure cache tests exist

## Dependencies at Risk

### Optional Export Dependencies

**Area:** Optional features with silent degradation
- **Files:** `ketu/__init__.py` (lines 109-118), `ketu/export/__init__.py`
- **Issue:** Chart rendering (`svgwrite`) and iCalendar (`icalendar`) are optional but imported silently
- **Current state:** `_EXPORT_AVAILABLE` flag set but not checked before use
- **Risk:** If user forgets to install optional deps, calling export functions fails at runtime rather than at import time
- **Fix approach:** Either require optional deps in setup.py as extras (`pip install ketu[export]`), or check `_EXPORT_AVAILABLE` before function calls and raise helpful error

### Pandas Dependency in Timelines

**Area:** Hidden dependency
- **Files:** `ketu/aspects/timelines.py` (lines 197-200)
- **Issue:** Pandas is imported only inside `generate_aspect_timeline()`, not listed as optional dependency
- **Risk:** Function fails at runtime if pandas not installed, no early warning
- **Fix approach:** Either add pandas to required deps or document as optional with early ImportError

## Security Considerations

### File System Cache Permissions

**Area:** Local cache storage
- **Files:** `ketu/cache/ephemeris_cache.py` (lines 62-65)
- **Issue:** Cache directory created at `~/.ketu/ephemeris_cache/` with default permissions
- **Risk:** On shared systems, other users can read cached ephemeris data (low risk but inconsistent with security practices)
- **Mitigation:** Could set directory to mode 0o700 (user-only)

## Known Bugs

### Operator Precedence in Cache Logic

**File:** `ketu/cycles/calculator.py` (lines 183-185)
- **Code:**
  ```python
  use_ephemeris_cache = (
      use_cache and
      CACHE_AVAILABLE and
      hasattr(timestamps, 'to_pydatetime') or  # Missing parentheses!
      (isinstance(timestamps, (list, np.ndarray)) and len(timestamps) > 0)
  )
  ```
- **Problem:** Due to Python operator precedence, this evaluates as:
  ```python
  ((A and B and C and D) or E)  # NOT  (A and B and C and (D or E))
  ```
- **Impact:** Cache can be used even when `use_cache=False` if the second condition is true
- **Workaround:** Currently works because conditions rarely conflict, but behavior is non-obvious
- **Fix:** Add parentheses:
  ```python
  use_ephemeris_cache = (
      use_cache and
      CACHE_AVAILABLE and
      (hasattr(timestamps, 'to_pydatetime') or
       (isinstance(timestamps, (list, np.ndarray)) and len(timestamps) > 0))
  )
  ```

### Aspect Vectorization Non-Determinism

**File:** `tests/test_aspects_vectorization.py` (line 41)
- **Symptom:** Test fails with "Different number of aspects: 30 vs 31"
- **Trigger:** Call `calculate_aspects_vectorized()` on certain dates
- **Status:** 1 failure in 183 tests, suggesting intermittent issue
- **Root cause:** Not yet identified - likely in aspect filtering logic
- **Workaround:** None (aspects cannot be relied upon in certain cases)

## Missing Critical Features

### No Aspect Persistence

**Area:** Aspect calculations
- **Files:** All aspect modules
- **Problem:** No way to save/load computed aspects between sessions
- **Impact:** Users must recompute aspects for every analysis session
- **Blocks:** Building production trading systems that need consistent aspect history

### ResonanceField Performance Not Optimized

**Area:** 3D resonance computation
- **Files:** `ketu/resonance.py`
- **Problem:** Method calculates harmonics manually in tight loop (lines 105-117) instead of using pre-computed complex aspects from `complex.py`
- **Impact:** Slower than necessary, code duplication
- **Blocks:** Real-time resonance field updates for high-frequency analysis

## Test Configuration Issues

**File:** `tests/test_ketu.py`
- **Issue:** `@pytest.mark.slow` decorator used (line 403) but marker not registered in `pytest.ini` or `pyproject.toml`
- **Symptom:** PytestUnknownMarkWarning on every test run
- **Fix:** Register marker in pytest config:
  ```ini
  [pytest]
  markers =
      slow: marks tests as slow (deselect with '-m "not slow"')
  ```

## Code Duplication Concerns

### Aspect Filtering Logic

**Files:** `ketu/aspects/calculator.py`, `ketu/aspects/core.py`, `ketu/aspects/windows.py`
- **Issue:** Similar aspect filtering/comparison logic appears in multiple places
- **Risk:** Bugs fixed in one place may not propagate to others
- **Suggestion:** Extract aspect comparison to single utility function

### Position Calculation Caching

**Files:** `ketu/calculations.py` (LRU cache via decorator), `ketu/aspects/core.py` (tuple-based caching)
- **Issue:** Two different caching strategies for ephemeris lookups
- **Consolidation opportunity:** Use EphemerisCache consistently across modules

## Scaling Limits

### Lunar Calendar Generation Scalability

**File:** `ketu/lunar_calendar.py` (lines 85-124, 241-325)
- **Current approach:** Searches for new moons by iterating forward in 15-day chunks, calling `find_aspect_window()` repeatedly
- **Limitation:** For historical analysis (many years), this becomes slow
- **Better approach:** Use aspect timeline to batch-find all new moons in date range at once
- **Impact:** Generating lunar calendars for 10+ years is noticeably slow

### Complex Array Broadcasting

**File:** `ketu/cycles/calculator.py` (lines 238-256)
- **Current:** Vectorized aspect proximity calculation with complex numbers works efficiently
- **Scaling:** Works well for <100k timestamps; memory usage scales as O(n * n_aspects) for distance matrix
- **Limit:** For very large arrays (>1M timestamps), distance matrix allocation could exceed available memory
- **Mitigation:** Currently not needed for trading applications, but document if used for research

## Code Quality Observations

### Inconsistent Error Messages

**Files:** Various aspect/transit modules
- **Issue:** Error messages vary in style and detail
  - Some raise `ValueError`, others `TypeError`, some `RuntimeError`
  - Some messages include context (body IDs), others don't
- **Impact:** Harder for users to debug issues
- **Suggestion:** Standardize error messages with consistent context information

### Missing Type Hints in Some Functions

**File:** `ketu/resonance.py`
- **Issue:** Type hints present but incomplete in some methods
- **Example:** `_get_trace()` returns tuple but doesn't declare return type
- **Impact:** Type checking tools can't verify correct usage

## Documentation Gaps

### No Guidance on Cache Management

**Files:** `ketu/cache/ephemeris_cache.py`
- **Issue:** Module exists but no user-facing documentation on:
  - When to use cache vs direct calculation
  - How much disk space cache uses
  - Cache invalidation strategy
  - Thread safety

### Aspect Orb Calculation Undocumented

**Files:** `ketu/cycles/calculator.py` (lines 259-271)
- **Issue:** Orb coefficients are hard-coded: `[1.0, 0.5, 0.75, 0.75, 1.0, 0.75, 0.75, 0.5, 1.0]`
- **Concern:** No explanation of why these specific values were chosen
- **Impact:** Users cannot adjust orb behavior without editing core code

---

*Concerns audit: 2026-02-12*
