# Phase 4: Test Coverage Hardening - Research

**Researched:** 2026-02-12
**Domain:** Python test coverage, pytest configuration, multi-version testing, NumPy testing patterns
**Confidence:** HIGH

## Summary

Phase 4 aims to harden Ketu's test coverage from the current 64% overall to 70%, with critical modules (cycles, cache, aspects) reaching 85%+ coverage. The project already has 196 passing tests with pytest 9.0.2 and coverage.py 7.13.1, providing a solid foundation. The main gaps are: cache module at 15% coverage (137 of 162 lines untested), cycles calculator at 72% (35 of 125 lines untested), and several deprecated export modules at 0% (can be ignored per Phase 1).

The phase requires five technical improvements: (1) comprehensive cache tests for file I/O, hit/miss paths, and interpolation; (2) cycles calculator tests for edge cases in pandas DatetimeIndex handling, datetime64 conversion, and cache integration paths; (3) standardized `numpy.testing.assert_allclose` usage with documented 1e-6 tolerance for all angle comparisons; (4) pytest marker registration to eliminate warnings; (5) re-enabling GitHub Actions CI for Python 3.10-3.13 testing (currently disabled).

**Primary recommendation:** Focus coverage efforts on cache module (15% → 85%) and cycles calculator (72% → 85%) as highest-impact targets. Aspects calculator already at 99% can be maintained. Use existing test patterns from `test_velocity_wrapping.py` as reference for NumPy testing best practices.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | 9.0.2 | Test framework | Industry standard, already integrated |
| pytest-cov | 7.0.0 | Coverage plugin | Official pytest coverage plugin, integrated with coverage.py |
| coverage.py | 7.13.1 | Coverage measurement | De facto standard for Python coverage, detailed reporting |
| NumPy | 2.3.5 | Testing utilities | `np.testing.assert_allclose` for floating-point comparisons |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| GitHub Actions | Latest | Multi-version CI | Testing Python 3.10, 3.11, 3.12, 3.13 |
| actions/setup-python | v5 | Python version matrix | Standard action for multi-version testing |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pytest-cov | coverage.py directly | pytest-cov provides better integration and reporting |
| numpy.testing.assert_allclose | pytest.approx | assert_allclose provides more control over absolute/relative tolerance |
| GitHub Actions | tox locally | CI ensures consistent cross-version testing |

**Installation:**
Already installed in venv. No new dependencies required.

## Architecture Patterns

### Current Test Structure
```
tests/
├── __init__.py
├── test_aspects_*.py          # Aspect calculations (well covered)
├── test_complex.py            # Complex math (well covered)
├── test_coverage_improvements.py  # Targeted coverage tests
├── test_ketu.py              # Legacy tests (includes @pytest.mark.slow)
├── test_velocity_wrapping.py # Example of NumPy testing best practices
├── test_regression/          # Bug regression tests
│   ├── test_bug_01_cache.py  # Cache operator precedence
│   └── test_bug_02_aspects.py # Aspect vectorization
└── benchmark*.py             # Performance tests (not in coverage)
```

### Pattern 1: NumPy Floating-Point Comparison

**What:** Use `numpy.testing.assert_allclose` with explicit tolerances for all angle comparisons.

**When to use:** When comparing angles, velocities, positions, or any floating-point astronomical calculations.

**Example:**
```python
# From test_velocity_wrapping.py - GOOD pattern
def test_scalar_and_vectorized_agree(self):
    """Scalar and vectorized Moon velocity must agree at boundary."""
    dt = datetime(2024, 1, 16, 5, 0, 0, tzinfo=timezone.utc)
    jd = utc_to_julian(dt)

    scalar_result = calc_planet_position(jd, MOON)
    batch_result = calc_planet_position_batch(np.array([jd]), MOON)

    np.testing.assert_allclose(
        scalar_result[3], batch_result[0, 3],
        atol=1e-6,
        err_msg="Scalar and vectorized Moon velocity must agree at 360/0 boundary"
    )
```

**Why this pattern:**
- Explicit tolerance (atol=1e-6) is documented and consistent
- Handles floating-point rounding errors properly
- Clear error messages for debugging
- NumPy native, no pytest dependency

### Pattern 2: Edge Case Testing for Angle Boundaries

**What:** Test angle wrapping at 0°/360° boundaries with known-failing dates.

**When to use:** For any function that performs angle arithmetic or velocity calculations.

**Example:**
```python
# From test_velocity_wrapping.py - boundary testing
class TestMoonVelocityWrapping:
    """Regression tests for BUG-03: Moon velocity wrapping."""

    def test_scalar_moon_velocity_at_boundary(self):
        """Scalar calc returns sane Moon velocity at 360/0 crossing."""
        # Known problematic date: Moon near 360 deg boundary
        dt = datetime(2024, 1, 16, 5, 0, 0, tzinfo=timezone.utc)
        jd = utc_to_julian(dt)

        result = calc_planet_position(jd, MOON)
        lon_speed = result[3]

        # Moon velocity is ~11-15 deg/day (prograde), never -36000
        assert 10 <= abs(lon_speed) <= 16, (
            f"Moon velocity at 360 deg crossing: {lon_speed} deg/day. "
            f"Expected ~14 deg/day. Wrapping bug if large negative."
        )
```

**Key elements:**
- Test with specific dates where wrapping occurs (documented)
- Assert reasonable physical bounds (Moon velocity 10-16 deg/day)
- Descriptive error messages with actual/expected values

### Pattern 3: Regression Test Structure

**What:** Isolated regression tests in `test_regression/` directory with bug documentation.

**When to use:** When fixing a bug, create a regression test that fails on old code, passes on new.

**Example:**
```python
"""Regression test for BUG-01: Cache operator precedence.

Prior to v1.0.0, the cache control logic had incorrect operator precedence:
    use_cache and CACHE_AVAILABLE and hasattr(...) or isinstance(...)

This evaluated as:
    ((use_cache and CACHE_AVAILABLE and hasattr(...)) or isinstance(...))

Result: use_cache=False was ignored when timestamps were list/ndarray.
"""

def test_use_cache_false_disables_cache_with_list_timestamps():
    """Test that use_cache=False is respected with list timestamps."""
    # Test implementation...
```

### Pattern 4: Cache Testing Strategy

**What:** Test cache module by covering file I/O paths, cache hits/misses, interpolation, and invalidation.

**Structure needed:**
```python
class TestEphemerisCacheFileIO:
    """Test cache file operations."""
    def test_compute_and_save_month(self, tmp_path):
        """Test computing and saving month to disk."""
    def test_load_existing_cache(self, tmp_path):
        """Test loading pre-existing cache files."""
    def test_force_recompute(self, tmp_path):
        """Test force_recompute flag."""

class TestEphemerisCacheHitMiss:
    """Test cache hit/miss logic."""
    def test_cache_hit_no_computation(self):
        """Verify no computation when cache hit."""
    def test_cache_miss_triggers_computation(self):
        """Verify computation when cache miss."""

class TestEphemerisCacheInterpolation:
    """Test intra-day interpolation."""
    def test_interpolate_midday_position(self):
        """Test interpolation between midnight samples."""
```

### Anti-Patterns to Avoid

- **BAD: Bare assertions for floats:** `assert angle1 == angle2` (fails due to float precision)
- **BAD: Missing tolerance documentation:** Using assert_allclose without documenting why tolerance is chosen
- **BAD: Unregistered markers:** `@pytest.mark.slow` without registration causes warnings
- **BAD: Testing export modules:** Don't add coverage for Phase 1 removed modules (chart, icalendar)

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Float comparison | Custom epsilon checks | `np.testing.assert_allclose` | Handles relative/absolute tolerance, edge cases (NaN, inf) |
| Temp directories | Manual cleanup | pytest `tmp_path` fixture | Automatic cleanup, isolation |
| Multi-version testing | Manual VM setup | GitHub Actions matrix | Parallelized, reproducible, free |
| Coverage collection | Custom instrumentation | pytest-cov plugin | Integrated, reports, branch coverage |
| Test parameterization | Copy-paste tests | `@pytest.mark.parametrize` | DRY, better reporting |

**Key insight:** Pytest and NumPy testing ecosystems are mature. Use built-in tools rather than custom solutions for standard testing problems.

## Common Pitfalls

### Pitfall 1: Not Registering Pytest Markers
**What goes wrong:** Warning appears: `PytestUnknownMarkWarning: Unknown pytest.mark.slow - is this a typo?`

**Why it happens:** Custom markers must be registered in `pyproject.toml` to be recognized.

**How to avoid:** Add markers to `[tool.pytest.ini_options]`:
```toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
]
```

**Warning signs:** Pytest warnings during test collection phase.

**Source:** [pytest official docs](https://docs.pytest.org/en/stable/how-to/mark.html)

### Pitfall 2: Incorrect Tolerance for Angle Comparisons
**What goes wrong:** Tests fail intermittently due to floating-point precision, or tests pass when they should fail.

**Why it happens:** Default tolerance (1e-7 relative) may be too tight or too loose for astronomical calculations.

**How to avoid:**
- Use explicit `atol=1e-6` for degrees (consistent with Ketu's documented precision)
- Document why tolerance is chosen (e.g., "1e-6 degrees = 0.0036 arcseconds, below ephemeris precision")
- Use relative tolerance (`rtol`) for large values, absolute (`atol`) for angles

**Warning signs:** Flaky tests that pass/fail randomly, or tests passing with obviously wrong values.

**Source:** [NumPy assert_allclose docs](https://numpy.org/doc/stable/reference/generated/numpy.testing.assert_allclose.html)

### Pitfall 3: Testing Against Removed Modules
**What goes wrong:** Wasting effort adding tests for `export/chart.py`, `export/icalendar.py`, etc.

**Why it happens:** Coverage report shows 0% for these modules.

**How to avoid:** These modules are removed in Phase 1. Exclude from coverage measurement:
```toml
[tool.coverage.run]
omit = [
    "*/tests/*",
    "ketu/export/*",
    "ketu/__main__.py",
    "ketu/resonance.py",
]
```

**Warning signs:** Coverage report includes modules that shouldn't be in v1.0.

### Pitfall 4: Not Testing Edge Cases at Boundaries
**What goes wrong:** Bugs appear in production at angle wrapping boundaries (0°/360°, ±180°).

**Why it happens:** Most random test data falls in the middle of ranges, not at edges.

**How to avoid:** Explicitly test known problematic values:
- 0°, 360° (angle wrapping)
- 180° (opposition, sign change)
- Values near 0 (division issues)
- Retrograde periods (negative velocities)

**Warning signs:** Bug reports about incorrect values at specific dates/angles.

**Source:** [Edge case testing guide](http://carpentries-incubator.github.io/python-testing/06-edges/index.html)

### Pitfall 5: Disabling CI for Local Development Convenience
**What goes wrong:** Tests pass locally on Python 3.13 but break on Python 3.10 in production.

**Why it happens:** `.github/workflows/tests.yml` has `on: workflow_dispatch:` instead of push/PR triggers.

**How to avoid:** Re-enable CI on push/PR:
```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
```

**Warning signs:** CI workflow never runs automatically, multi-version bugs slip through.

## Coverage Gaps Analysis

### Critical Module: cache/ephemeris_cache.py (15% → 85% target)

**Current state:** 25 of 162 lines covered (15.4%)

**Missing coverage areas:**
1. File I/O operations (lines 88-108, 154-163, 182-239)
   - `_compute_month()`: Computing full month of ephemeris data
   - `ensure_month()`: Cache file loading/saving logic
   - `ensure_range()`: Multi-month loading

2. Interpolation logic (lines 278-281, 300-387)
   - `get_position()`: Intra-day interpolation between midnight samples
   - `get_positions_vectorized()`: Batch interpolation

3. Cache management (lines 403-404, 408-409, 413-418, 434-436)
   - Cache clearing
   - Memory management
   - Default cache instance

**Test strategy:**
- Use pytest `tmp_path` fixture for isolated cache directories
- Test cache hit/miss paths separately
- Verify interpolation accuracy with known positions
- Test edge cases (month boundaries, year transitions)
- Verify vectorized batch operations match scalar

**Effort estimate:** 10-15 tests, ~200 lines of test code

### Critical Module: cycles/calculator.py (72% → 85% target)

**Current state:** 90 of 125 lines covered (72.0%)

**Missing coverage areas:**
1. Pandas DatetimeIndex conversion (lines 147-150)
2. NumPy datetime64 conversion (lines 154-155)
3. Cache integration paths (lines 184-200)
4. Edge cases in body ID resolution (lines 103, 106)

**Test strategy:**
- Test with pandas DatetimeIndex input (currently only 2 files use assert_allclose)
- Test with numpy datetime64 arrays
- Test cache-enabled vs cache-disabled paths
- Test invalid body names/IDs

**Effort estimate:** 5-8 tests, ~100 lines of test code

### Module: aspects/calculator.py (99% → maintain)

**Current state:** 144 of 145 lines covered (99.3%)

Only 1 line missing (line 292). This is excellent coverage; maintain during Phase 4.

### Modules to Exclude (0% coverage, removed in Phase 1)

Per ROADMAP.md Phase 1 completion:
- `ketu/export/` (all files)
- `ketu/__main__.py`
- `ketu/resonance.py` (to be refactored in Phase 5)
- `ketu/lunar_calendar.py` (low priority, not in critical path)

These should be added to coverage omit list.

## Code Examples

### Example 1: Cache File I/O Test with tmp_path

```python
# Source: pytest best practices
import pytest
from pathlib import Path
from datetime import datetime, timezone
from ketu.cache import EphemerisCache

class TestEphemerisCacheFileIO:
    """Test cache file operations."""

    def test_compute_and_save_month(self, tmp_path):
        """Test computing and saving month to disk."""
        cache = EphemerisCache(cache_dir=tmp_path)

        # Compute January 2025
        cache.ensure_month(2025, 1)

        # Verify cache file was created
        cache_file = tmp_path / "2025-01-ephemeris.npy"
        assert cache_file.exists()

        # Verify cache file has correct shape
        data = np.load(cache_file)
        assert data.shape == (31, 13, 6)  # 31 days, 13 bodies, 6 fields

    def test_cache_reused_on_second_call(self, tmp_path):
        """Test that cache file is reused, not recomputed."""
        cache = EphemerisCache(cache_dir=tmp_path)

        # First call: compute
        cache.ensure_month(2025, 1)
        cache_file = tmp_path / "2025-01-ephemeris.npy"
        first_mtime = cache_file.stat().st_mtime

        # Second call: should load from cache
        cache.ensure_month(2025, 1)
        second_mtime = cache_file.stat().st_mtime

        # File should not be modified
        assert first_mtime == second_mtime
```

### Example 2: Interpolation Accuracy Test

```python
def test_interpolate_sun_position_midday(self, tmp_path):
    """Test interpolation accuracy for Sun at midday."""
    cache = EphemerisCache(cache_dir=tmp_path)
    cache.ensure_month(2025, 1)

    # Get Sun position at noon (interpolated between midnight samples)
    noon_dt = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    pos = cache.get_position(noon_dt, body_id=0)  # Sun

    # Compute directly for comparison
    from ketu.ephemeris.planets import calc_planet_position
    from ketu.ephemeris.time import utc_to_julian
    jd = utc_to_julian(noon_dt)
    direct_pos = calc_planet_position(jd, 0)

    # Interpolation should be within 0.01 degrees (Sun moves ~1 deg/day)
    np.testing.assert_allclose(
        pos[0], direct_pos[0],  # longitude
        atol=0.01,
        err_msg="Interpolated Sun position should match direct computation"
    )
```

### Example 3: Parameterized Edge Case Test

```python
@pytest.mark.parametrize("angle,expected", [
    (0.0, 0.0),       # Zero boundary
    (360.0, 0.0),     # 360 wraps to 0
    (-30.0, 330.0),   # Negative wraps
    (720.0, 0.0),     # Multiple wraps
])
def test_angle_normalization(angle, expected):
    """Test angle normalization at boundaries."""
    from ketu.complex import degrees_to_complex, complex_to_degrees

    # Round-trip through complex representation
    z = degrees_to_complex(angle)
    normalized = complex_to_degrees(z)

    np.testing.assert_allclose(
        normalized, expected,
        atol=1e-6,
        err_msg=f"Angle {angle} should normalize to {expected}"
    )
```

### Example 4: Multi-Version CI Configuration

```yaml
# Source: GitHub Actions docs
# File: .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install pytest pytest-cov

    - name: Run tests with coverage
      run: |
        pytest tests/ -v --cov=ketu --cov-report=term-missing

    - name: Check coverage threshold
      run: |
        pytest tests/ --cov=ketu --cov-fail-under=70
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual float comparison | `np.testing.assert_allclose` | NumPy 1.5+ (2010) | Eliminated float precision bugs |
| tox for multi-version | GitHub Actions matrix | 2019+ | Free, parallel, integrated |
| pytest.approx | numpy.testing.assert_allclose | Scientific Python best practice | More control over tolerances |
| Coverage in separate run | pytest-cov integration | pytest-cov 1.0+ (2012) | Single command, better reporting |

**Deprecated/outdated:**
- Using `==` for float comparisons (always use assert_allclose)
- Running coverage.py manually (use pytest-cov plugin)
- Local tox for multi-version testing (use CI for definitive test)

## Open Questions

1. **Should lunar_calendar.py be included in coverage targets?**
   - What we know: Currently 17% coverage, not in critical path
   - What's unclear: Is this module actively used or planned for removal?
   - Recommendation: Exclude from Phase 4 scope, revisit in Phase 5

2. **What tolerance should be used for velocity comparisons?**
   - What we know: Angles use 1e-6 degrees
   - What's unclear: Appropriate tolerance for deg/day velocities
   - Recommendation: Use 1e-4 deg/day (Moon moves ~13 deg/day, so 1e-4 is 0.001% precision)

3. **Should benchmarks be included in test runs?**
   - What we know: benchmark*.py files exist but not in coverage
   - What's unclear: Performance regression testing strategy
   - Recommendation: Keep benchmarks separate, don't count in coverage

## Sources

### Primary (HIGH confidence)
- [pytest official documentation](https://docs.pytest.org/en/stable/) - Markers, fixtures, best practices
- [NumPy testing documentation](https://numpy.org/doc/stable/reference/routines.testing.html) - assert_allclose API
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/) - Coverage plugin usage
- [GitHub Actions Python docs](https://docs.github.com/en/actions/use-cases-and-examples/building-and-testing/building-and-testing-python) - Multi-version matrix testing
- Ketu source code - pyproject.toml, tests/, coverage.json

### Secondary (MEDIUM confidence)
- [Pytest Code Coverage Best Practices](https://pytest-with-eric.com/pytest-best-practices/pytest-code-coverage-reports/) - Coverage threshold guidance
- [Edge Case Testing Guide](http://carpentries-incubator.github.io/python-testing/06-edges/index.html) - Boundary testing patterns
- [NumPy Testing in Scientific Computing](https://cerfacs.fr/coop/pytest-allclose) - Tolerance selection for scientific code

### Tertiary (LOW confidence)
- None - all findings verified with authoritative sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All tools currently in use, versions verified
- Architecture: HIGH - Existing test patterns examined, coverage gaps measured
- Pitfalls: HIGH - Drawn from project history (ROADMAP, CONCERNS, existing bugs)
- Coverage targets: HIGH - Based on coverage.json analysis and success criteria

**Research date:** 2026-02-12
**Valid until:** 2026-06-12 (4 months - stable testing ecosystem)
