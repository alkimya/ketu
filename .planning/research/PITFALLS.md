# Pitfalls Research: Python Library 1.0 Consolidation

**Domain:** Python scientific library (astronomical calculations)
**Researched:** 2026-02-12
**Confidence:** HIGH (based on codebase analysis + established Python packaging practices)

## Critical Pitfalls

### Pitfall 1: Breaking Public API Without Deprecation Path

**What goes wrong:**
Users upgrade from 0.4.0 to 1.0.0 and their code breaks immediately with ImportError or AttributeError. No warning, no migration guide, just broken imports.

**Why it happens:**
When removing export modules (chart, icalendar), the natural approach is to delete them and update `__all__`. But users importing `from ketu import draw_zodiacal_chart` will face hard failures.

**How to avoid:**
1. **Before removal**: Add deprecation warnings in 0.5.0 release
   ```python
   # ketu/__init__.py in 0.5.0
   try:
       from ketu.export import draw_zodiacal_chart
       import warnings
       warnings.warn(
           "draw_zodiacal_chart will be removed in ketu 1.0. "
           "Chart exports are deprecated.",
           DeprecationWarning,
           stacklevel=2
       )
   except ImportError:
       pass
   ```

2. **In 1.0**: Provide clear ImportError messages
   ```python
   # ketu/__init__.py in 1.0.0
   def draw_zodiacal_chart(*args, **kwargs):
       raise ImportError(
           "ketu.draw_zodiacal_chart was removed in 1.0.0. "
           "Chart rendering is no longer supported. "
           "Use ketu 0.4.x for chart exports."
       )
   ```

3. **Migration guide**: Document in CHANGELOG.md and GitHub release notes
   - What was removed
   - Why it was removed
   - Alternatives (stay on 0.4.x or use separate charting library)

**Warning signs:**
- No 0.5.0 deprecation release between 0.4.0 and 1.0.0
- CHANGELOG doesn't have "BREAKING CHANGES" section
- No migration guide in README or docs

**Phase to address:**
Phase 1 (Deprecation) + Phase 7 (Release Preparation)

---

### Pitfall 2: SemVer Confusion - Users Expect Stability After 1.0

**What goes wrong:**
After 1.0.0 release, users expect rock-solid stability. Any breaking change in 1.1.0 or bug that changes calculation results violates their trust. Scientific libraries are particularly sensitive because downstream users cache results and expect reproducibility.

**Why it happens:**
Pre-1.0 projects can break things freely. 1.0.0 signals "production ready" and "stable API." Breaking changes after 1.0 require major version bump (2.0). Teams underestimate this commitment.

**How to avoid:**
1. **Fix ALL known bugs before 1.0.0**
   - Operator precedence bug in cache logic (CONCERNS.md line 140-165)
   - Aspect non-determinism (30 vs 31 aspects, CONCERNS.md line 167-174)
   - These are correctness bugs — must be fixed, even if behavior changes

2. **Document behavior precisely**
   - Exact orb calculation formula (currently undocumented, CONCERNS.md line 268-274)
   - Aspect ordering guarantees (or explicitly "undefined order")
   - Numerical precision guarantees (e.g., "positions accurate to 0.001 degrees")

3. **Add "Correctness" section to CHANGELOG**
   ```markdown
   ## [1.0.0] - Breaking Changes

   ### Correctness Fixes (may change results from 0.4.0)
   - Fixed operator precedence bug in cache logic - cache now respects use_cache=False
   - Fixed aspect vectorization non-determinism - always returns same number of aspects
   - Orb calculations now documented and standardized

   **Impact**: If you relied on v0.4.0 results, recompute with v1.0.0 for correct values.
   ```

4. **Commit to semantic versioning strictly**
   - 1.x.y releases: bug fixes only (no behavior changes unless fixing incorrect behavior)
   - 1.x.0 releases: new features (backward compatible)
   - 2.0.0 release: breaking changes

**Warning signs:**
- Known bugs still present at 1.0.0 release
- No documentation of numerical precision guarantees
- No policy for handling correctness bugs post-1.0

**Phase to address:**
Phase 2 (Bug Fixes) — must complete before 1.0.0 release

---

### Pitfall 3: Hidden Dependencies Fail at Runtime

**What goes wrong:**
User installs `pip install ketu==1.0.0` successfully. Code runs fine until they call a function that imports Pandas, then:
```
ImportError: No module named 'pandas'
```

**Why it happens:**
Ketu has hidden Pandas dependency in `aspects/timelines.py` (CONCERNS.md line 119-125). Import is inside function, not at module level, so pip doesn't track it and installation succeeds. Failure happens at runtime.

**How to avoid:**
**Option A: Make Pandas required** (increases dependency burden)
```toml
# pyproject.toml
dependencies = [
    "numpy>=1.20.0",
    "pandas>=1.5.0",  # Now required
]
```

**Option B: Make aspect timelines optional** (preferred for pure NumPy goal)
```python
# ketu/__init__.py
try:
    from ketu.aspects.timelines import generate_aspect_timeline
    _TIMELINES_AVAILABLE = True
except ImportError:
    _TIMELINES_AVAILABLE = False
    def generate_aspect_timeline(*args, **kwargs):
        raise ImportError(
            "generate_aspect_timeline requires pandas. "
            "Install with: pip install pandas>=1.5.0"
        )
```

**Option C: Remove Pandas entirely** (best for 1.0 goal)
- Rewrite `aspects/timelines.py` to use structured NumPy arrays (CYCLE_DTYPE already exists)
- Remove DataFrame conversions, return structured arrays instead
- Breaking change but acceptable for 1.0

**Recommendation**: Option C — rewrite to pure NumPy, aligns with "NumPy only" constraint.

**Warning signs:**
- Import statements hidden inside functions
- Dependencies not in `pyproject.toml` but used in code
- No test that validates install in clean environment

**Phase to address:**
Phase 3 (Dependency Cleanup) — remove Pandas before 1.0.0

---

### Pitfall 4: Removing Modules from PyPI Package Without Proper Metadata

**What goes wrong:**
User has code: `from ketu.export.chart import draw_zodiacal_chart`. After upgrading to 1.0.0:
1. If `ketu.export` package is removed entirely → `ModuleNotFoundError`
2. If kept as stub → `ImportError` inside the module
3. Worst case: Old `.pyc` files from 0.4.0 remain, code "works" but uses stale bytecode

**Why it happens:**
Python package managers don't automatically remove old files when upgrading. If 0.4.0 installed `ketu/export/chart.py` and 1.0.0 removes it from `packages=[]`, the old file may persist.

**How to avoid:**
1. **Clean package list in pyproject.toml**
   ```toml
   # Current (0.4.0)
   packages = ["ketu", "ketu.ephemeris", "ketu.aspects", "ketu.cycles", "ketu.cache", "ketu.export"]

   # 1.0.0 - remove export
   packages = ["ketu", "ketu.ephemeris", "ketu.aspects", "ketu.cycles", "ketu.cache"]
   ```

2. **Use `find_packages()` carefully**
   If switching from explicit list to `find_packages()`, verify it doesn't accidentally include export:
   ```python
   # setup.py or pyproject.toml
   packages = find_packages(exclude=["tests", "benchmarks", "examples"])
   ```

3. **Test clean install** (critical step often skipped)
   ```bash
   # Create fresh venv
   python -m venv test_venv
   source test_venv/bin/activate

   # Install wheel directly (not editable)
   pip install dist/ketu-1.0.0-py3-none-any.whl

   # Verify removed modules don't import
   python -c "from ketu.export import draw_zodiacal_chart" # Should fail
   python -c "import ketu.export.chart" # Should fail
   ```

4. **Document upgrade path**
   ```markdown
   # UPGRADING.md
   ## From 0.4.x to 1.0.0

   If upgrading in existing environment:
   ```bash
   pip uninstall ketu
   pip install ketu==1.0.0
   ```

   This ensures old export modules are removed.
   ```

**Warning signs:**
- No clean install test in fresh venv
- `setup.py`/`pyproject.toml` has manual package list that doesn't match actual structure
- No `.pyc` cleanup in upgrade path

**Phase to address:**
Phase 7 (Release Preparation) — must test before PyPI publish

---

### Pitfall 5: Test Coverage Number Hides Critical Gaps

**What goes wrong:**
Project reaches 70% test coverage and releases 1.0.0. Users discover critical bugs in:
- Cache behavior (0% coverage, CONCERNS.md line 21-23)
- Cycle calculations (0% coverage, CONCERNS.md line 25-29)

Coverage metric is met but **wrong code** was tested.

**Why it happens:**
Coverage tools measure lines executed, not correctness. Easy to hit 70% by testing trivial functions (getters, formatters) while leaving core logic untested.

**How to avoid:**
1. **Coverage by module, not overall**
   ```bash
   pytest --cov=ketu --cov-report=term-missing

   # Check per-module coverage
   # CRITICAL: Cache, cycles, aspects must be >80%
   # ACCEPTABLE: Display, export (deprecated) can be lower
   ```

2. **Priority-based coverage targets**
   | Module | Priority | Target Coverage | Rationale |
   |--------|----------|-----------------|-----------|
   | `ketu/cycles/calculator.py` | CRITICAL | 90% | Core calculation engine |
   | `ketu/cache/ephemeris_cache.py` | CRITICAL | 85% | Data integrity risk |
   | `ketu/aspects/core.py` | HIGH | 85% | Affects all downstream |
   | `ketu/complex.py` | HIGH | 80% | Mathematical correctness |
   | `ketu/display.py` | LOW | 40% | UI only, not data |

3. **Write tests for failure modes**
   Current tests focus on happy path. Add:
   - Invalid inputs (negative JD, out-of-range bodies)
   - Edge cases (timestamp at exactly 0°, 360° wraparound)
   - Cache corruption scenarios
   - Non-determinism tests (run same calculation 100 times, verify identical results)

4. **Mutation testing** (advanced, optional)
   Tools like `mutmut` inject bugs into code to verify tests catch them:
   ```bash
   pip install mutmut
   mutmut run --paths-to-mutate ketu/cycles/
   # If mutation survives → test gap
   ```

**Warning signs:**
- High coverage in `display.py`, low in `cycles/calculator.py`
- No tests for error conditions
- Coverage jumps from 62% to 71% without testing critical modules

**Phase to address:**
Phase 4 (Test Coverage) — prioritize critical modules

---

### Pitfall 6: Complex Number Math - Precision Loss in Angle Wrapping

**What goes wrong:**
Cycle phase calculations lose precision during normalization. User calculates angle separation, gets 359.9999999997° instead of 0.0° due to floating point error compounded by trig functions.

**Why it happens:**
Complex number representation uses `e^(iθ) = cos(θ) + i·sin(θ)`. Chain of operations:
1. Degrees → Radians (first conversion)
2. Radians → Complex (sin/cos introduce error)
3. Complex division (compounds error)
4. Complex → Radians (atan2 introduces error)
5. Radians → Degrees (final conversion)

Each step loses ~1e-15 precision. After 5 steps, can accumulate to 1e-12, which becomes visible after wraparound.

**How to avoid:**
1. **Use modulo carefully**
   ```python
   # BAD: Can produce -0.0 or 360.0
   angle_deg = (angle_deg % 360)

   # GOOD: Guarantees [0, 360)
   angle_deg = angle_deg % 360.0
   if angle_deg < 0:
       angle_deg += 360.0
   ```

2. **Epsilon comparisons for aspect detection**
   ```python
   # BAD: Exact comparison fails due to precision
   if separation == 0.0:  # conjunction

   # GOOD: Tolerance-based comparison
   EPSILON = 1e-6  # ~0.0036 arcseconds
   if abs(separation - 0.0) < EPSILON:
   ```

3. **Test boundary cases**
   ```python
   def test_angle_wraparound():
       """Test precision at 0/360 boundary"""
       moon = ZodiacPoint.from_degrees(359.99999999)
       sun = ZodiacPoint.from_degrees(0.00000001)
       ratio = moon / sun

       # Should be near 0, not near 360
       assert ratio.aspect_degrees < 1.0 or ratio.aspect_degrees > 359.0
   ```

4. **Document precision limits**
   ```python
   # ketu/complex.py docstring
   """
   Precision: Angular calculations accurate to ~1e-6 degrees (~0.0036 arcseconds).
   This is sufficient for astrological purposes but not for astronomical ephemeris.

   Note: Angles near 0°/360° boundary may show small numerical artifacts (< 1e-6°).
   """
   ```

**Warning signs:**
- Tests don't cover angles near 0°, 360°
- No epsilon comparisons for floating point equality
- No documented precision guarantees

**Phase to address:**
Phase 4 (Test Coverage) + Phase 5 (Integration)

---

### Pitfall 7: Platform-Specific Floating Point Differences

**What goes wrong:**
Tests pass on Linux (dev machine) but fail on Windows or macOS. Same calculation produces:
- Linux: `120.50000000000001`
- Windows: `120.49999999999999`

Test expects exact match, fails on Windows.

**Why it happens:**
NumPy and Python math use platform-specific BLAS/LAPACK libraries. Different compilers (GCC vs MSVC) produce different floating point optimizations. Transcendental functions (sin, cos, atan2) are especially susceptible.

**How to avoid:**
1. **Use `numpy.testing.assert_allclose`**
   ```python
   # BAD: Exact comparison
   assert result == 120.5

   # GOOD: Tolerance-based
   np.testing.assert_allclose(result, 120.5, rtol=1e-7, atol=1e-9)
   # rtol = relative tolerance (1e-7 = 0.00001%)
   # atol = absolute tolerance (1e-9 = 0.000000001)
   ```

2. **Test on multiple platforms** (GitHub Actions)
   ```yaml
   # .github/workflows/test.yml
   strategy:
     matrix:
       os: [ubuntu-latest, windows-latest, macos-latest]
       python-version: ['3.10', '3.11', '3.12', '3.13']
   ```

3. **Document tested platforms**
   ```markdown
   # README.md
   ## Platform Support

   Ketu is tested on:
   - Linux (Ubuntu 20.04+)
   - macOS (12+)
   - Windows (10+)

   Numerical results may differ by <1e-7 degrees across platforms due to BLAS differences.
   ```

4. **Canonical test data** (for regression tests)
   Generate expected values on one platform, store as JSON:
   ```python
   # tests/fixtures/golden_data.json
   {
     "sun_moon_conjunction_2020_12_21": {
       "separation": 120.50000000000001,
       "tolerance": 1e-6  # Platform-safe tolerance
     }
   }
   ```

**Warning signs:**
- Tests use `==` for floating point comparisons
- CI only tests on one platform
- No tolerance documented for numerical accuracy

**Phase to address:**
Phase 4 (Test Coverage) — update test assertions

---

## Moderate Pitfalls

### Pitfall 8: Wheel vs Source Distribution Inconsistencies

**What goes wrong:**
User installs from source (`pip install ketu`) and it works. Another user installs from wheel (`pip install ketu --only-binary :all:`) and gets different behavior or missing files.

**Why it happens:**
`MANIFEST.in` controls source distribution (sdist), `pyproject.toml [tool.setuptools.package-data]` controls wheel. If they diverge, builds are inconsistent.

**How to avoid:**
1. **Test both build types**
   ```bash
   # Build both
   python -m build

   # Verify contents
   tar -tzf dist/ketu-1.0.0.tar.gz | grep -E '\.(py|typed)$'
   unzip -l dist/ketu-1.0.0-py3-none-any.whl

   # Install and test each
   pip install dist/ketu-1.0.0.tar.gz
   pytest
   pip uninstall ketu

   pip install dist/ketu-1.0.0-py3-none-any.whl
   pytest
   ```

2. **Keep MANIFEST.in minimal**
   ```
   # MANIFEST.in
   include README.md
   include LICENSE
   include CHANGELOG.md
   recursive-include ketu *.typed
   ```

3. **Use pyproject.toml for package data**
   ```toml
   [tool.setuptools.package-data]
   ketu = ["py.typed"]
   ```

**Phase to address:**
Phase 7 (Release Preparation)

---

### Pitfall 9: Type Hints Broken After Module Removal

**What goes wrong:**
Ketu has `py.typed` marker for type checking. After removing export modules, user's type checker fails:
```
error: Module 'ketu.export' has no attribute 'draw_zodiacal_chart'
```

Even though user doesn't import it, their type checker scans all exported symbols.

**How to avoid:**
1. **Update __init__.py carefully**
   Remove from `__all__` (already planned)

2. **Test with mypy in strict mode**
   ```bash
   pip install mypy
   mypy ketu/ --strict --no-implicit-optional
   ```

3. **Verify type stubs in wheel**
   ```bash
   unzip -l dist/ketu-1.0.0-py3-none-any.whl | grep typed
   # Should find: ketu/py.typed
   ```

**Phase to address:**
Phase 5 (Integration Testing)

---

### Pitfall 10: PyPI Metadata Doesn't Match Reality

**What goes wrong:**
User searches PyPI for "astronomical calculations", finds Ketu, but description says "chart rendering and visualization" (old copy). Downloads, finds no charts, feels misled.

**How to avoid:**
Update `pyproject.toml` metadata for 1.0.0:

```toml
[project]
name = "ketu"
version = "1.0.0"
description = "Pure NumPy astronomical calculations for planetary cycles and aspects"  # Updated
keywords = [
    "astronomy",
    "ephemeris",
    "aspects",
    "planets",
    "cycles",
    "numpy",
    # Removed: "astrology", "charts", "visualization"
]
classifiers = [
    "Development Status :: 5 - Production/Stable",  # Changed from Beta
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering :: Astronomy",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]

[project.optional-dependencies]
# Removed: chart, icalendar, all
# (No optional dependencies in 1.0 - pure NumPy only)
```

**Phase to address:**
Phase 7 (Release Preparation)

---

### Pitfall 11: Changelog Doesn't Follow Keep a Changelog Format

**What goes wrong:**
User reads CHANGELOG.md to understand upgrade impact. Sees:
```markdown
## [1.0.0] - 2026-02-20

- Removed exports
- Fixed bugs
- Updated tests
```

Vague. User doesn't know WHAT broke or WHY.

**How to avoid:**
Follow Keep a Changelog structure (already claimed in CHANGELOG.md line 7):

```markdown
## [1.0.0] - 2026-02-20

### BREAKING CHANGES

- **Removed export modules** (`ketu.export.chart`, `ketu.export.icalendar`)
  - Rationale: Pure calculation library, exports belong in separate GUI layer
  - Migration: Stay on 0.4.x if charts needed, or use matplotlib directly
  - Removed functions: `draw_zodiacal_chart`, `export_lunations_to_ical`, `export_transits_to_ical`, `export_aspects_to_ical`

- **Removed optional dependencies** (`matplotlib`, `icalendar`)
  - `pip install ketu[chart]` no longer valid
  - Core library is now NumPy-only

- **Removed CLI entry point** (`ketu` command)
  - Removed: `ketu.display.main()`
  - Rationale: Library focus, not CLI tool
  - Migration: Use as Python library or stay on 0.4.x

- **Removed Pandas dependency** from aspect timelines
  - `generate_aspect_timeline()` now returns structured NumPy array instead of DataFrame
  - Migration: Use `.to_records()` if DataFrame needed: `pd.DataFrame(result)`

### Fixed

- **Operator precedence bug** in cache logic (`cycles/calculator.py`)
  - IMPACT: Cache was sometimes used when `use_cache=False`
  - Now respects cache flag correctly

- **Aspect vectorization non-determinism**
  - IMPACT: `calculate_aspects_vectorized()` sometimes returned 30 instead of 31 aspects
  - Now deterministic across all dates

### Changed

- Integrated complex number representation into cycle engine
- Standardized error messages across modules
- Improved test coverage to 70%+ (focus on critical modules)

### Performance

- Vectorized ResonanceField calculations (1000x speedup for 8760 timestamps)
- Consolidated caching strategies

### Documentation

- Updated all docs for 1.0 API
- Removed chart/icalendar examples
- Added precision guarantees section
- Added platform compatibility matrix
```

**Phase to address:**
Phase 7 (Release Preparation)

---

### Pitfall 12: No Rollback Strategy if 1.0.0 Has Critical Bug

**What goes wrong:**
1.0.0 releases to PyPI. Users upgrade. Critical bug discovered (wrong aspect calculations). No way to "unpublish" from PyPI. Chaos.

**How to avoid:**
1. **Release candidate first**
   ```bash
   # Release 1.0.0rc1 to PyPI
   version = "1.0.0rc1"
   python -m build
   twine upload dist/*

   # Ask users to test
   # Wait 1-2 weeks

   # If stable, release 1.0.0
   version = "1.0.0"
   ```

2. **GitHub pre-release**
   Create GitHub release as "pre-release" before PyPI:
   - Upload wheel/sdist as artifacts
   - Tag as v1.0.0-rc1
   - Ask community to test
   - Wait for feedback

3. **Smoke tests before publish**
   ```python
   # tests/smoke_test.py
   """Critical calculations that must work"""
   def test_sun_moon_conjunction():
       """Known event: Dec 21, 2020 conjunction"""
       jd = utc_to_julian(datetime(2020, 12, 21, 18, 0))
       aspects = calculate_aspects(jd)
       conjunctions = [a for a in aspects if a['aspect'] == 'conjunction']
       assert len(conjunctions) > 0

   def test_cycle_series_basic():
       """Cycle series must not crash on common inputs"""
       timestamps = pd.date_range('2020-01-01', '2020-12-31', freq='D')
       cycles = generate_cycle_series(timestamps, "Sun", "Moon")
       assert len(cycles) == len(timestamps)
   ```

4. **Yanking strategy** (last resort)
   ```bash
   # If 1.0.0 is broken
   pip install twine
   twine upload --repository pypi dist/ketu-1.0.1-*  # Fixed version

   # Then yank broken version (marks as unavailable but doesn't delete)
   # Requires PyPI maintainer access
   # Only for critical bugs
   ```

**Phase to address:**
Phase 7 (Release Preparation) — release 1.0.0rc1 first

---

## Minor Pitfalls

### Pitfall 13: Version Number Not Updated in All Files

**What goes wrong:**
`pyproject.toml` says 1.0.0, but `ketu/__init__.py` still says `__version__ = "0.4.0"`. Users check version at runtime, see 0.4.0, confusion.

**How to avoid:**
Single source of truth:

```toml
# pyproject.toml
[project]
dynamic = ["version"]

[tool.setuptools.dynamic]
version = {attr = "ketu.__version__"}
```

```python
# ketu/__init__.py
__version__ = "1.0.0"
```

Pre-release checklist:
```bash
grep -r "0\.4\.0" ketu/ docs/ README.md
# Should find: 0 matches (except in CHANGELOG history)
```

**Phase to address:**
Phase 7 (Release Preparation)

---

### Pitfall 14: GitHub Release Tag Doesn't Match PyPI Version

**What goes wrong:**
PyPI has `ketu-1.0.0`, GitHub has tag `v1.0` (missing patch). URLs break, users confused.

**How to avoid:**
Consistent tagging:
```bash
# Git tag MUST match pyproject.toml version exactly
git tag v1.0.0  # NOT v1.0, NOT 1.0.0, NOT release-1.0.0
git push origin v1.0.0

# PyPI version must match
# pyproject.toml: version = "1.0.0"
python -m build
twine upload dist/ketu-1.0.0*
```

**Phase to address:**
Phase 7 (Release Preparation)

---

### Pitfall 15: No UPGRADING.md or Migration Guide

**What goes wrong:**
User reads CHANGELOG, sees "Removed export modules," has no idea how to update code.

**How to avoid:**
Create `UPGRADING.md`:

```markdown
# Upgrading to Ketu 1.0

## From 0.4.x to 1.0.0

### Removed: Chart rendering

**Before (0.4.x):**
```python
from ketu import draw_zodiacal_chart
draw_zodiacal_chart(jd, filename='chart.svg')
```

**After (1.0.0):**
Not supported. Options:
1. Stay on ketu==0.4.0 if charts are critical
2. Use matplotlib directly (we can provide example code)

### Removed: iCalendar export

**Before (0.4.x):**
```python
from ketu import export_lunations_to_ical
export_lunations_to_ical(start, end, filename='lunar.ics')
```

**After (1.0.0):**
Not supported. Stay on 0.4.x or use `icalendar` library directly.

### Changed: Aspect timelines return NumPy arrays

**Before (0.4.x):**
```python
timeline = generate_aspect_timeline(...)  # Returns DataFrame
timeline['separation'].mean()
```

**After (1.0.0):**
```python
timeline = generate_aspect_timeline(...)  # Returns structured array
timeline['separation'].mean()  # Still works!

# Or convert to DataFrame manually
import pandas as pd
df = pd.DataFrame(timeline)
```

### Fixed: Correctness bugs

If you relied on v0.4.0 results, recompute with v1.0.0:
- Cache behavior corrected (respects use_cache flag)
- Aspect vectorization now deterministic
```

**Phase to address:**
Phase 7 (Release Preparation)

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skip deprecation warnings | Faster 1.0 release | Angry users, support burden | Never - always deprecate first |
| Keep optional deps hidden | Cleaner dependency list | Runtime ImportErrors | Never - make explicit or remove |
| 70% coverage via trivial tests | Hit metric quickly | Critical bugs slip through | Never - prioritize by module risk |
| Skip platform testing | Faster CI | Windows/Mac failures in production | Never for 1.0 |
| Manual version updates | Simpler setup | Version drift across files | Never - automate with single source |
| No migration guide | Less writing | User confusion, GitHub issues | Never for breaking changes |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| NumPy arrays | Using `==` for float comparison | Use `np.testing.assert_allclose()` |
| PyPI publish | Upload without testing wheel install | Always test fresh venv install from wheel |
| GitHub Actions | Test only on Ubuntu | Matrix: [ubuntu, windows, macos] x [3.10, 3.11, 3.12, 3.13] |
| SemVer | Breaking change in 1.1.0 | Breaking changes require 2.0.0 after 1.0 |
| Package removal | Delete module, ship it | Test that old modules don't import after upgrade |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Python loops in ResonanceField | 1000x slower than vectorized | Use `calc_planet_position_batch()` | >1000 timestamps |
| Tuple conversion for cache | Conversion overhead on every call | Custom hash function or accept unhashable | High-frequency calls |
| Lunar calendar iteration | Slow for multi-year ranges | Batch find all new moons via aspect timeline | >5 years |
| Complex array broadcasting | Memory explosion for large arrays | Document limits, chunk if needed | >1M timestamps |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Cache dir default permissions (0o755) | On shared systems, other users read cache | Set to 0o700 (user-only) |
| No input validation on JD | Negative JD causes ephemeris errors | Validate JD range: `if jd < 0: raise ValueError` |
| Unpickling cache without verification | Malicious cache files execute code | Use JSON for cache, not pickle |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Silent cache failures | Results wrong, no error | Log cache hit/miss, warn on errors |
| Vague error messages | "ValueError: invalid input" | "ValueError: body_id must be 0-12, got 99" |
| No progress indicator | Users think code hung | Optional progress callback for long operations |
| Breaking API without migration guide | Users stuck, frustrated | Always provide UPGRADING.md with examples |

## "Looks Done But Isn't" Checklist

- [ ] **Module removal:** Verify old modules don't import in fresh venv wheel install
- [ ] **Version numbers:** Grep for old version in all files (code, docs, examples)
- [ ] **PyPI metadata:** Description/keywords match actual 1.0 functionality
- [ ] **Platform tests:** CI runs on Ubuntu, Windows, macOS for all supported Python versions
- [ ] **Float comparisons:** All tests use `assert_allclose`, not `==`
- [ ] **Coverage targets:** Critical modules (cycles, cache, aspects) >80%, not just overall 70%
- [ ] **Known bugs:** Operator precedence fixed, aspect non-determinism fixed
- [ ] **Deprecation path:** If skipping 0.5.0, clear migration guide in CHANGELOG and UPGRADING.md
- [ ] **Hidden dependencies:** No runtime ImportError for undeclared dependencies
- [ ] **Type checking:** `mypy ketu/ --strict` passes
- [ ] **Smoke tests:** Critical calculations tested against known-good results
- [ ] **Release candidate:** 1.0.0rc1 published and tested before 1.0.0 final

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Breaking API without deprecation | HIGH | 1. Release 1.0.1 with stubs that raise helpful errors<br>2. Publish detailed migration guide<br>3. Monitor GitHub issues, provide support |
| Hidden dependency breaks install | MEDIUM | 1. Release 1.0.1 with dependency added<br>2. Or remove feature entirely in 1.0.1<br>3. PyPI yank 1.0.0 if critical |
| Known bug shipped in 1.0.0 | HIGH | 1. Fix ASAP in 1.0.1<br>2. If correctness bug: document result changes<br>3. If critical: yank 1.0.0 (last resort) |
| Wrong PyPI metadata | LOW | 1. Update metadata, release 1.0.1<br>2. Edit PyPI description (can be done without release) |
| Platform test failures | MEDIUM | 1. Reproduce on affected platform<br>2. Fix float comparisons or platform-specific code<br>3. Release 1.0.1 |
| Incomplete module removal | MEDIUM | 1. Release 1.0.1 with proper package list<br>2. Test wheel install in clean venv |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Breaking API without deprecation | Phase 1 (Deprecation) + Phase 7 | Check CHANGELOG has BREAKING CHANGES section |
| SemVer confusion (bugs in 1.0) | Phase 2 (Bug Fixes) | All CONCERNS.md bugs resolved before release |
| Hidden Pandas dependency | Phase 3 (Dependency Cleanup) | `pip install ketu` in clean venv, import all functions |
| Module removal breaks imports | Phase 7 (Release Preparation) | Fresh venv wheel install, verify old modules fail to import |
| Coverage hiding critical gaps | Phase 4 (Test Coverage) | Per-module coverage: cycles >90%, cache >85% |
| Complex math precision loss | Phase 5 (Integration) | Tests include 0°/360° boundary cases |
| Platform float differences | Phase 4 (Test Coverage) | All tests use assert_allclose, CI tests 3 platforms |
| Wheel vs source differences | Phase 7 (Release Preparation) | Install both sdist and wheel, pytest each |
| Type hints broken | Phase 5 (Integration) | `mypy ketu/ --strict` passes |
| PyPI metadata outdated | Phase 7 (Release Preparation) | Review pyproject.toml classifiers/keywords/description |
| Changelog vague | Phase 7 (Release Preparation) | CHANGELOG follows Keep a Changelog format |
| No rollback plan | Phase 7 (Release Preparation) | Release 1.0.0rc1 first, wait for feedback |

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Phase 1: Deprecation | Skipping deprecation warnings to save time | Don't skip - either do 0.5.0 release with warnings, or provide extensive migration guide |
| Phase 2: Bug Fixes | Fixing bugs changes behavior, breaking tests | Document behavior changes in CHANGELOG "Correctness Fixes" section |
| Phase 3: Dependency Cleanup | Removing Pandas breaks aspect timelines | Rewrite to use NumPy structured arrays (CYCLE_DTYPE already exists) |
| Phase 4: Test Coverage | Hitting 70% without testing critical modules | Set per-module targets, prioritize cycles/cache/aspects |
| Phase 5: Integration | Assuming tests pass = code works | Add smoke tests for known calculations, test on 3 platforms |
| Phase 6: Documentation | Docs still reference removed features | Grep docs for "chart", "icalendar", "matplotlib" |
| Phase 7: Release Prep | Publishing to PyPI without testing wheel install | ALWAYS test fresh venv install from wheel before publish |

## Sources

**Codebase Analysis:**
- `/home/loc/workspace/solaris/ketu/.planning/codebase/CONCERNS.md` - Known bugs and gaps identified
- `/home/loc/workspace/solaris/ketu/pyproject.toml` - Current dependencies and metadata
- `/home/loc/workspace/solaris/ketu/ketu/__init__.py` - Export structure and optional deps
- `/home/loc/workspace/solaris/ketu/CHANGELOG.md` - Version history and SemVer claims

**Python Packaging Best Practices:**
- Python Packaging User Guide (packaging.python.org) - official PyPI packaging standards
- PEP 440 (Version Identification) - semantic versioning for Python
- Keep a Changelog (keepachangelog.com) - changelog format standard
- Semantic Versioning 2.0.0 (semver.org) - version bump rules

**Scientific Python Ecosystem:**
- NumPy Testing Guidelines - float comparison best practices
- SciPy Developer Guide - platform testing and numerical precision
- Astropy Coordination Committee - astronomical software standards (relevant for ephemeris libraries)

**Known Issues:**
- Operator precedence bug (CONCERNS.md line 140-165) - CRITICAL for Phase 2
- Aspect non-determinism (CONCERNS.md line 167-174) - CRITICAL for Phase 2
- Hidden Pandas dependency (CONCERNS.md line 119-125) - CRITICAL for Phase 3
- Untested cache module (CONCERNS.md line 21-23) - CRITICAL for Phase 4
- Untested cycles module (CONCERNS.md line 25-29) - CRITICAL for Phase 4

**Confidence Assessment:**
- HIGH for codebase-specific pitfalls (direct analysis of CONCERNS.md and code)
- HIGH for Python packaging pitfalls (established best practices, PEPs)
- HIGH for NumPy/scientific library pitfalls (documented standards)
- MEDIUM for complex number precision (domain-specific, based on general floating point knowledge)

---

*Pitfalls research for: Ketu 1.0 Python Library Consolidation*
*Researched: 2026-02-12*
*Confidence: HIGH (codebase analysis + established Python/scientific library practices)*
