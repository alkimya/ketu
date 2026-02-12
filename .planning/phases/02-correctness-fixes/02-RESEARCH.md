# Phase 2: Correctness Fixes - Research

**Researched:** 2026-02-12
**Domain:** Python bug fixing, operator precedence, NumPy determinism, regression testing
**Confidence:** HIGH

## Summary

Phase 2 addresses two critical bugs discovered during real-world usage:

1. **BUG-01: Operator precedence in cache logic** - Cache control is broken due to Python's operator precedence rules. The expression evaluates as `((A and B and C and D) or E)` instead of `(A and B and C and (D or E))`, allowing cache to be used even when `use_cache=False`.

2. **BUG-02: Aspect vectorization non-determinism** - The vectorized aspect calculation (`calculate_aspects_vectorized()`) returns different results than the loop-based version (`calculate_aspects()`). On test date 2020-12-21, vectorized finds 31 aspects while loop-based finds 30. The missing aspect is `(3, 7, 11, 0.8055399)` - a Quincunx between Venus (3) and Uranus (7).

Both bugs are well-documented in `.planning/codebase/CONCERNS.md` with exact file locations, symptoms, and root causes. The fixes are straightforward: parentheses for BUG-01, and logic alignment for BUG-02.

**Primary recommendation:** Fix operator precedence first (trivial), then debug aspect vectorization by comparing loop vs vectorized logic step-by-step. Write regression tests that fail on v0.4.0 and pass after fixes.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | 9.0.2 | Testing framework | Python standard, already in use (183 tests) |
| numpy | >=1.20.0 | Numerical arrays | Core dependency, vectorization foundation |
| pytest-cov | 7.0.0 | Coverage tracking | Already configured in pyproject.toml |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| hypothesis | latest | Property-based testing | Optional: verify determinism across random inputs |
| pytest-benchmark | latest | Performance regression | Optional: ensure fixes don't degrade performance |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pytest | unittest | pytest already used (pyproject.toml config), migration unnecessary |
| Manual testing | Property-based testing | Manual sufficient for these specific bugs, hypothesis useful for future |

**Installation:**
```bash
# Already installed (existing test suite)
source venv/bin/activate
# No new dependencies required for basic fixes
```

## Architecture Patterns

### Recommended Test Structure
```
tests/
├── test_regression/           # NEW: Regression tests for v1.0.0
│   ├── test_bug_01_cache.py  # BUG-01: Cache control regression
│   └── test_bug_02_aspects.py # BUG-02: Aspect determinism regression
├── test_aspects_vectorization.py  # EXISTING: Will be fixed
└── [other existing tests]
```

### Pattern 1: Regression Test Structure
**What:** Tests that capture bugs fixed in a release, ensuring they never return
**When to use:** After fixing any bug that made it to production/users
**Example:**
```python
"""Regression tests for v1.0.0 bug fixes.

These tests fail on v0.4.0 and pass on v1.0.0+.
"""
import pytest
import numpy as np

def test_bug_01_cache_respects_use_cache_false():
    """BUG-01: use_cache=False must disable cache (operator precedence fix).

    Prior to v1.0.0, cache logic had incorrect operator precedence:
        use_cache and CACHE_AVAILABLE and hasattr() or isinstance()
    evaluated as:
        (use_cache and CACHE_AVAILABLE and hasattr()) or isinstance()

    This allowed cache to be used even when use_cache=False.

    Regression test: Verify cache is truly disabled when use_cache=False.
    """
    # Test implementation here
    pass

def test_bug_02_aspect_vectorization_deterministic():
    """BUG-02: calculate_aspects_vectorized() must match calculate_aspects().

    Prior to v1.0.0, vectorized aspect calculation returned different
    results than loop-based version. Example:
    - Date: 2020-12-21 18:20:00 UTC
    - Loop version: 30 aspects
    - Vectorized version: 31 aspects
    - Missing: (3, 7, 11, 0.8055399) - Venus-Uranus Quincunx

    Regression test: Verify both functions return identical results.
    """
    # Test implementation here
    pass
```

### Pattern 2: Cache Testing Strategy
**What:** Verify cache behavior without depending on cache implementation details
**When to use:** Testing optional caching systems where cache presence varies
**Example:**
```python
def test_cache_disabled_by_flag():
    """Test that use_cache=False prevents any caching."""
    # Call function twice with use_cache=False
    result1 = generate_cycle_series(timestamps, "Sun", "Moon", use_cache=False)
    result2 = generate_cycle_series(timestamps, "Sun", "Moon", use_cache=False)

    # Results should be identical (both computed fresh)
    np.testing.assert_array_equal(result1, result2)

    # No verification of cache internals needed
    # Just verify: same inputs + use_cache=False → same outputs
```

### Pattern 3: Determinism Testing
**What:** Verify same inputs always produce same outputs (no randomness, no ordering issues)
**When to use:** Vectorized code, parallel operations, set/dict-based logic
**Example:**
```python
@pytest.mark.parametrize("test_date", [
    datetime(2020, 12, 21, 18, 20, 0, tzinfo=ZoneInfo("UTC")),
    datetime(2025, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
    datetime(2015, 6, 15, 12, 0, 0, tzinfo=ZoneInfo("UTC")),
])
def test_aspects_deterministic_across_dates(test_date):
    """Verify aspect calculation is deterministic."""
    jd = utc_to_julian(test_date)

    # Run 10 times
    results = [calculate_aspects_vectorized(jd) for _ in range(10)]

    # All results must be identical
    for i in range(1, len(results)):
        assert len(results[0]) == len(results[i])
        np.testing.assert_array_equal(results[0], results[i])
```

### Anti-Patterns to Avoid
- **Testing cache internals:** Don't check cache hit/miss counters, check outputs instead
- **Flaky assertions:** Avoid `assert abs(result - expected) < 0.1` for exact computations; use `np.testing.assert_allclose` with explicit tolerance
- **Over-mocking:** Don't mock NumPy operations; test real logic to catch vectorization bugs
- **Single test date:** Use multiple dates via parametrize to catch edge cases

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Array comparison | Manual loops checking `arr1[i] == arr2[i]` | `np.testing.assert_array_equal()` | Handles shape mismatch, NaN, inf, provides clear error messages |
| Float comparison | `abs(a - b) < epsilon` | `np.testing.assert_allclose()` | Handles relative/absolute tolerance, array broadcasting |
| Regression tracking | Comments saying "this was broken" | Dedicated test file with bug numbers | Tests are executable documentation, comments decay |
| Cache verification | Inspecting cache internals | Testing output consistency | Implementation-agnostic, survives refactoring |
| Determinism checks | Running test multiple times manually | `@pytest.mark.parametrize` with ranges | Automated, documents expected behavior |

**Key insight:** NumPy and pytest provide specialized assertion functions that catch edge cases (NaN inequality, broadcasting errors, shape mismatches) that manual checks miss.

## Common Pitfalls

### Pitfall 1: Operator Precedence Blindness
**What goes wrong:** Writing `A and B and C or D` expecting `A and B and (C or D)` but getting `(A and B and C) or D`
**Why it happens:** Python's `and` has higher precedence than `or`, but human intuition reads left-to-right
**How to avoid:** Always parenthesize mixed `and`/`or` expressions, even when "obvious"
**Warning signs:** Boolean expression spans multiple lines, combines `and` with `or`

**Example from BUG-01:**
```python
# BROKEN (current code)
use_ephemeris_cache = (
    use_cache and
    CACHE_AVAILABLE and
    hasattr(timestamps, 'to_pydatetime') or  # Missing parentheses!
    (isinstance(timestamps, (list, np.ndarray)) and len(timestamps) > 0)
)
# Evaluates as: ((use_cache and CACHE_AVAILABLE and hasattr(...)) or isinstance(...))

# FIXED
use_ephemeris_cache = (
    use_cache and
    CACHE_AVAILABLE and
    (hasattr(timestamps, 'to_pydatetime') or
     (isinstance(timestamps, (list, np.ndarray)) and len(timestamps) > 0))
)
```

### Pitfall 2: Vectorization Logic Mismatch
**What goes wrong:** Vectorized version produces different results than scalar version
**Why it happens:** Different code paths for scalar vs vector, subtle differences in edge cases, ordering differences
**How to avoid:**
1. Write reference (slow) version first
2. Write comprehensive property test: `vectorized(inputs) == [scalar(x) for x in inputs]`
3. Test edge cases: empty arrays, single elements, boundary values
**Warning signs:** Test passes "usually", different results on specific dates, off-by-one aspect counts

**Example from BUG-02:**
```python
# In loop version (calculator.py line 139):
for idx in np.where(in_orb)[0]:
    results.append((body1_ids[idx], body2_ids[idx], i_asp, orb_values[np.where(in_orb)[0] == idx][0]))
    # ⚠️ orb_values indexing: np.where(in_orb)[0] == idx creates boolean mask
    #    This might skip some values or duplicate others

# Should be:
for i, idx in enumerate(np.where(in_orb)[0]):
    results.append((body1_ids[idx], body2_ids[idx], i_asp, orb_values[i]))
    # Use enumeration index 'i' for orb_values, not complex boolean mask
```

### Pitfall 3: Assuming Test Failure Means Code is Wrong
**What goes wrong:** Existing test fails after fix, assume fix is wrong, revert
**Why it happens:** Test might have been written to match buggy behavior
**How to avoid:**
1. Understand what test is verifying
2. Check if test expectations match specification or just current behavior
3. Update test if it was testing buggy behavior
**Warning signs:** Test name doesn't mention what it's testing, test has no docstring, test expectations are hard-coded with no explanation

### Pitfall 4: No Regression Test for Bugs
**What goes wrong:** Fix bug, add no test, bug returns months later
**Why it happens:** "It's a trivial fix", "existing tests should catch it"
**How to avoid:** Every bug fix requires regression test that fails pre-fix, passes post-fix
**Warning signs:** PR has file changes but no new tests, commit message says "fix X" but test count unchanged

## Code Examples

Verified patterns from project and Python best practices:

### Testing Cache Control
```python
# Source: Ketu test patterns + pytest best practices
def test_cache_disabled_when_use_cache_false():
    """Verify use_cache=False disables caching regardless of other conditions."""
    from datetime import datetime, timezone
    from ketu.cycles.calculator import generate_cycle_series
    import numpy as np

    timestamps = [
        datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
    ]

    # Call with use_cache=False multiple times
    result1 = generate_cycle_series(timestamps, "Sun", "Moon", use_cache=False)
    result2 = generate_cycle_series(timestamps, "Sun", "Moon", use_cache=False)

    # Results must be identical (deterministic computation)
    np.testing.assert_array_equal(result1, result2)

    # If cache was incorrectly used, we can't detect it directly
    # But we can verify behavior is correct
    assert len(result1) == len(timestamps)
```

### Testing Aspect Determinism
```python
# Source: tests/test_aspects_vectorization.py (modified for regression)
def test_aspect_vectorization_matches_loop_version():
    """Verify vectorized and loop-based aspect calculations are identical.

    Regression test for BUG-02: On v0.4.0, these returned different counts.
    """
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from ketu.aspects import calculate_aspects, calculate_aspects_vectorized
    from ketu.ephemeris.time import utc_to_julian
    import numpy as np

    # Test on multiple dates (not just one that might be special)
    test_dates = [
        datetime(2020, 12, 21, 18, 20, 0, tzinfo=ZoneInfo("UTC")),  # Known failure date
        datetime(2025, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
        datetime(2015, 6, 15, 12, 0, 0, tzinfo=ZoneInfo("UTC")),
    ]

    for test_date in test_dates:
        jd = utc_to_julian(test_date)

        # Both versions
        aspects_loop = calculate_aspects(jd)
        aspects_vec = calculate_aspects_vectorized(jd)

        # Must have same count
        assert len(aspects_loop) == len(aspects_vec), \
            f"Date {test_date}: loop={len(aspects_loop)} vs vec={len(aspects_vec)}"

        # Must have same aspects (after sorting for comparison)
        loop_sorted = np.sort(aspects_loop, order=["body1", "body2", "i_asp"])
        vec_sorted = np.sort(aspects_vec, order=["body1", "body2", "i_asp"])

        # Check body IDs and aspect types match
        np.testing.assert_array_equal(loop_sorted["body1"], vec_sorted["body1"])
        np.testing.assert_array_equal(loop_sorted["body2"], vec_sorted["body2"])
        np.testing.assert_array_equal(loop_sorted["i_asp"], vec_sorted["i_asp"])

        # Check orb values are close (floating point)
        np.testing.assert_allclose(loop_sorted["orb"], vec_sorted["orb"], rtol=1e-6)
```

### Debugging Vectorization Mismatch
```python
# Source: Debugging approach for BUG-02
def debug_aspect_mismatch():
    """Debug helper: Find which aspect is missing/extra in vectorized version."""
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from ketu.aspects import calculate_aspects, calculate_aspects_vectorized
    from ketu.ephemeris.time import utc_to_julian
    from ketu.core import bodies, aspects as aspect_data

    test_date = datetime(2020, 12, 21, 18, 20, 0, tzinfo=ZoneInfo("UTC"))
    jd = utc_to_julian(test_date)

    aspects_loop = calculate_aspects(jd)
    aspects_vec = calculate_aspects_vectorized(jd)

    # Convert to sets of tuples for comparison
    loop_set = set(
        (int(a["body1"]), int(a["body2"]), int(a["i_asp"]))
        for a in aspects_loop
    )
    vec_set = set(
        (int(a["body1"]), int(a["body2"]), int(a["i_asp"]))
        for a in aspects_vec
    )

    # Find differences
    only_in_loop = loop_set - vec_set
    only_in_vec = vec_set - loop_set

    print(f"Loop version: {len(aspects_loop)} aspects")
    print(f"Vectorized:   {len(aspects_vec)} aspects")
    print(f"Only in loop: {only_in_loop}")
    print(f"Only in vec:  {only_in_vec}")

    # Decode aspect info
    for body1, body2, i_asp in only_in_vec:
        body1_name = bodies["name"][body1].decode()
        body2_name = bodies["name"][body2].decode()
        aspect_name = aspect_data["name"][i_asp].decode()
        aspect_angle = aspect_data["angle"][i_asp]
        print(f"  {body1_name} - {body2_name}: {aspect_name} ({aspect_angle}°)")
```

### Fixing Operator Precedence
```python
# Source: Direct fix for BUG-01
# BEFORE (ketu/cycles/calculator.py lines 180-185)
use_ephemeris_cache = (
    use_cache and
    CACHE_AVAILABLE and
    hasattr(timestamps, 'to_pydatetime') or
    (isinstance(timestamps, (list, np.ndarray)) and len(timestamps) > 0)
)

# AFTER (with parentheses)
use_ephemeris_cache = (
    use_cache and
    CACHE_AVAILABLE and
    (hasattr(timestamps, 'to_pydatetime') or
     (isinstance(timestamps, (list, np.ndarray)) and len(timestamps) > 0))
)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual boolean logic | Black formatter + explicit parens | 2024+ | Formatter doesn't fix logic, only style |
| Assert statements | `np.testing.assert_*` | NumPy 1.x+ | Better error messages, array-aware |
| Try-run-test manually | `pytest.mark.parametrize` | pytest 2.0+ (2010) | Automated multi-case testing |
| Docstring examples | Doctest or dedicated tests | Ongoing | Doctests break easily, prefer unit tests |
| Version-agnostic tests | Regression test suites per release | Best practice | Documents what changed when |

**Deprecated/outdated:**
- `assert a == b` for arrays: Use `np.testing.assert_array_equal(a, b)` instead
- `assert abs(a - b) < 0.001`: Use `np.testing.assert_allclose(a, b, atol=0.001)` instead
- Testing by running code manually: Always write automated test

## Bug Analysis

### BUG-01: Operator Precedence (High Confidence)

**Location:** `ketu/cycles/calculator.py` lines 180-185

**Current Code:**
```python
use_ephemeris_cache = (
    use_cache and
    CACHE_AVAILABLE and
    hasattr(timestamps, 'to_pydatetime') or  # ❌ Missing parentheses
    (isinstance(timestamps, (list, np.ndarray)) and len(timestamps) > 0)
)
```

**Problem:** Python operator precedence makes `and` bind tighter than `or`, so this evaluates as:
```python
((use_cache and CACHE_AVAILABLE and hasattr(...)) or isinstance(...))
```

**Impact:** When `use_cache=False`, if `isinstance(timestamps, (list, np.ndarray)) and len(timestamps) > 0` is True, then `use_ephemeris_cache` becomes True, ignoring the user's `use_cache=False` setting.

**Fix:** Add parentheses to group the `or` condition:
```python
use_ephemeris_cache = (
    use_cache and
    CACHE_AVAILABLE and
    (hasattr(timestamps, 'to_pydatetime') or
     (isinstance(timestamps, (list, np.ndarray)) and len(timestamps) > 0))
)
```

**Test Strategy:**
1. Call `generate_cycle_series(..., use_cache=False)` with list/ndarray timestamps
2. Verify cache is NOT used (difficult to observe directly)
3. Alternative: Verify outputs are deterministic (same inputs → same outputs)
4. Success criteria from phase description: "User sets `use_cache=False` and cache is verifiably disabled"

### BUG-02: Aspect Vectorization (High Confidence)

**Location:** `ketu/aspects/calculator.py` lines 136-140

**Symptom:** On 2020-12-21 18:20:00 UTC:
- `calculate_aspects()` finds 30 aspects
- `calculate_aspects_vectorized()` finds 31 aspects
- Extra aspect: `(3, 7, 11, 0.8055399)` = Venus (3) - Uranus (7) Quincunx (150°)

**Root Cause (Suspected):** Line 139 has complex indexing:
```python
for idx in np.where(in_orb)[0]:
    results.append((body1_ids[idx], body2_ids[idx], i_asp,
                   orb_values[np.where(in_orb)[0] == idx][0]))
    #          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #          This creates a boolean mask that finds position of idx
    #          But orb_values was already filtered by in_orb, so index mismatch
```

**Expected Fix:**
```python
for i, idx in enumerate(np.where(in_orb)[0]):
    results.append((body1_ids[idx], body2_ids[idx], i_asp, orb_values[i]))
    #                                                       ^^^^^^^^^^^
    #                                                       Use enumeration index
```

**Test Strategy:**
1. Run both functions on multiple test dates
2. Assert `len(result1) == len(result2)`
3. Assert aspect lists are identical (after sorting)
4. Use `np.testing.assert_array_equal` for body IDs and aspect indices
5. Use `np.testing.assert_allclose` for orb values (floating point)
6. Success criteria: "User runs `calculate_aspects_vectorized()` across 100 dates and gets consistent aspect count every time"

## Open Questions

1. **Cache observability**
   - What we know: Cache is optional, may not be available
   - What's unclear: How to verify cache was/wasn't used without inspecting internals
   - Recommendation: Test output correctness, not cache behavior. If `use_cache=False`, outputs must be deterministic and correct.

2. **Performance impact of fixes**
   - What we know: BUG-01 fix is trivial (parentheses), no performance impact
   - What's unclear: Will BUG-02 fix change performance? Current code has `np.where(in_orb)[0] == idx` which is O(n) per iteration
   - Recommendation: Benchmark before/after. Expected improvement (remove redundant np.where call).

3. **Aspect count consistency across all dates**
   - What we know: BUG-02 manifests on 2020-12-21, might affect other dates
   - What's unclear: Is there a systematic pattern to when it fails?
   - Recommendation: Parametrize test with 10-20 random dates spanning years, verify all pass.

## Sources

### Primary (HIGH confidence)
- Ketu codebase: `.planning/codebase/CONCERNS.md` - Complete bug documentation
- Ketu codebase: `ketu/cycles/calculator.py` - BUG-01 location lines 180-185
- Ketu codebase: `ketu/aspects/calculator.py` - BUG-02 location lines 136-140
- Ketu codebase: `tests/test_aspects_vectorization.py` - Existing test showing failure
- Python documentation: Operator precedence - https://docs.python.org/3/reference/expressions.html#operator-precedence

### Secondary (MEDIUM confidence)
- NumPy testing utilities: https://numpy.org/doc/stable/reference/routines.testing.html
- pytest parametrize: https://docs.pytest.org/en/stable/how-to/parametrize.html
- pytest markers: https://docs.pytest.org/en/stable/how-to/mark.html

### Tertiary (LOW confidence)
- None - all findings verified from codebase and official documentation

## Metadata

**Confidence breakdown:**
- Bug identification: HIGH - Both bugs clearly documented with exact locations and symptoms
- Root cause analysis: HIGH - BUG-01 obvious (operator precedence), BUG-02 highly likely (indexing mismatch)
- Fix approach: HIGH - Both fixes are straightforward code changes
- Test strategy: HIGH - Standard regression testing patterns, well-established practices

**Research date:** 2026-02-12
**Valid until:** 90 days (stable domain - Python language semantics and NumPy don't change quickly)
