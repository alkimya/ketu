---
phase: 03-dependency-cleanup
plan: 01
subsystem: ketu-core
tags: [dependency-cleanup, pandas-removal, numpy-only]
dependency_graph:
  requires: []
  provides:
    - pandas-free-ketu-source
    - numpy-only-exports
    - migration-guide
  affects:
    - ketu.aspects.timelines
    - ketu.resonance
    - ketu.cycles
tech_stack:
  added: []
  removed:
    - pandas (optional dependency)
  patterns:
    - NumPy structured arrays for data export
    - Duck-typing for pandas DatetimeIndex support
key_files:
  created:
    - ketu/resonance.py
  modified:
    - ketu/aspects/timelines.py
    - ketu/cycles/calculator.py
    - ketu/cycles/__init__.py
    - tests/test_aspect_timelines.py
    - docs/aspect_timelines.md
    - ketu/aspects/README.md
    - UPGRADING.md
decisions:
  - title: Remove to_pandas entirely (no deprecation)
    rationale: Heading to 1.0.0, clean break justified; Ketu's contract is NumPy-only
    alternatives:
      - Deprecation period: Rejected - adds complexity for PyPI release
      - Keep as optional: Rejected - violates NumPy-only contract
  - title: Keep duck-typing for pandas DatetimeIndex
    rationale: Zero-cost interop, no pandas dependency required
    alternatives:
      - Remove duck-typing: Rejected - breaks user convenience for no benefit
  - title: User-side conversion pattern via pd.DataFrame()
    rationale: Users who need pandas can easily convert; pandas knows how to read NumPy structured arrays
    alternatives:
      - Provide helper function: Rejected - adds maintenance burden
metrics:
  duration_seconds: 370
  tasks_completed: 2
  files_modified: 8
  commits: 2
  tests_passing: 196
  completed_date: 2026-02-12
---

# Phase 03 Plan 01: Remove Pandas Dependency Summary

**One-liner:** Pure NumPy export system using structured arrays for AspectTimeline and ResonanceField, zero pandas imports in ketu source tree

## Objectives

Remove all pandas dependencies from Ketu, making it a pure NumPy library as per the original contract. Hidden pandas dependencies via `to_pandas()` in AspectTimeline and hard `import pandas` in resonance.py violated the NumPy-only contract.

## What Was Done

### Task 1: Remove Pandas from Source Code and Tests (Commit c9f0a1c)

**Files Modified:**
- `ketu/aspects/timelines.py`: Deleted `to_pandas()` and `_get_pandas_columns()` methods entirely
- `ketu/cycles/calculator.py`: Removed `pd.DatetimeIndex` from type hints, updated docstring examples to use `datetime + timedelta`
- `ketu/cycles/__init__.py`: Updated module docstring example from `pd.date_range` to list comprehension
- `ketu/resonance.py`: Removed `import pandas as pd`, changed return type from `pd.DataFrame` to `np.ndarray`
- `tests/test_aspect_timelines.py`: Deleted `test_to_pandas()`, added `test_no_pandas_import()`

**ResonanceField Changes:**
- Added `RESONANCE_DTYPE` at module level for structured array definition
- Replaced `pd.date_range()` with `np.arange()` using `np.datetime64` and `np.timedelta64`
- Replaced DataFrame construction with NumPy structured array creation
- Updated `compute_field()` docstring to reflect NumPy return type

**Type Hint Updates:**
- Removed `"pd.DatetimeIndex"` from `generate_cycle_series()` and `generate_multi_cycle_series()` type hints
- Preserved duck-typing via `hasattr(timestamps, 'to_pydatetime')` check (no dependency, just interop)

**Test Changes:**
- Removed `test_to_pandas` entirely (195 tests → 196 tests with new test)
- Added `test_no_pandas_import` to verify pandas is NOT imported as side effect

### Task 2: Update Documentation and Migration Guide (Commit 39a3f59)

**Files Modified:**
- `docs/aspect_timelines.md`: Replaced all `to_pandas()` examples with `to_numpy()` or user-side conversion patterns
- `ketu/aspects/README.md`: Changed "Timeline with export methods (NumPy, Pandas, JSON)" to "Timeline with export methods (NumPy, JSON)"
- `UPGRADING.md`: Added comprehensive pandas removal section with before/after examples

**Documentation Updates:**
- Added migration note to docs header warning about pandas removal
- Updated "ML-Ready Export Formats" from 3 formats (NumPy, Pandas, JSON) to 2 (NumPy, JSON)
- Replaced `df = timeline.to_pandas()` examples with `data = timeline.to_numpy()` throughout
- Updated multi-timeline example to show NumPy array concatenation or user-side pandas conversion
- Updated cycle phase classification example to use vectorized NumPy operations
- Updated time series resampling example to show user-side pandas conversion

**UPGRADING.md Migration Guide:**
- Added "Pandas Dependency" section under "Removed Features"
- Documented `AspectTimeline.to_pandas()` removal with 3 migration options:
  1. Use `to_numpy()` for ML workflows
  2. User-side conversion via `pd.DataFrame(timeline.to_dict_list())`
  3. User-side conversion via `pd.DataFrame(timeline.to_numpy())`
- Documented `ResonanceField.compute_field()` return type change
- Explained type hint changes and preserved duck-typing support
- Provided complete before/after code examples

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

All success criteria met:

1. ✅ Zero pandas imports in ketu/ source tree:
   ```bash
   $ grep -rn "import pandas" ketu/
   # (no output - zero matches)
   ```

2. ✅ Zero to_pandas() in .py files:
   ```bash
   $ grep -rn "to_pandas" ketu/*.py ketu/**/*.py
   # (no output - zero matches)
   ```

3. ✅ Only UPGRADING.md contains to_pandas in docs:
   ```bash
   $ grep -rn "to_pandas" docs/
   # (only UPGRADING.md migration examples)
   ```

4. ✅ AspectTimeline has no to_pandas method:
   ```python
   >>> from ketu.aspects.timelines import AspectTimeline
   >>> assert not hasattr(AspectTimeline, 'to_pandas')
   ```

5. ✅ ResonanceField doesn't import pandas:
   ```python
   >>> from ketu.resonance import ResonanceField
   >>> import sys
   >>> assert 'pandas' not in sys.modules
   ```

6. ✅ All 196 tests pass (test_to_pandas removed, test_no_pandas_import added)

## Key Technical Details

### NumPy Structured Array Implementation

**AspectTimeline** already used structured arrays via `_get_numpy_dtype()`, so no changes needed to the array structure - just removed the pandas export path.

**ResonanceField** required conversion from DataFrame to structured array:

```python
# Before (returned DataFrame)
df = pd.DataFrame(index=timestamps)
df['res_lon'] = res_lon
df['res_lat'] = res_lat
df['res_dec'] = res_dec
return df

# After (returns structured array)
RESONANCE_DTYPE = np.dtype([
    ('timestamp', 'datetime64[s]'),
    ('res_lon', 'f8'),
    ('res_lat', 'f8'),
    ('res_dec', 'f8'),
])
result = np.zeros(n_points, dtype=RESONANCE_DTYPE)
result['timestamp'] = timestamps
result['res_lon'] = res_lon
result['res_lat'] = res_lat
result['res_dec'] = res_dec
return result
```

### Timestamp Generation Without Pandas

Replaced `pd.date_range()` with NumPy datetime arithmetic:

```python
# Before
timestamps = pd.date_range(start_dt, end_dt, freq=f"{step_hours}h")

# After
start_naive = start_dt.replace(tzinfo=None) if start_dt.tzinfo else start_dt
end_naive = end_dt.replace(tzinfo=None) if end_dt.tzinfo else end_dt
timestamps = np.arange(
    np.datetime64(start_naive),
    np.datetime64(end_naive),
    np.timedelta64(step_hours, 'h')
)
```

### Duck-Typing Preservation

The plan correctly identified that duck-typing support for pandas DatetimeIndex should be PRESERVED, not removed:

```python
# This code remains unchanged (no pandas dependency)
if hasattr(timestamps, 'to_pydatetime'):
    # pandas DatetimeIndex (duck-typing, no import needed)
    dts = timestamps.to_pydatetime()
    jds = np.array([utc_to_julian(dt) for dt in dts])
```

This allows users to pass `pd.date_range()` output to ketu functions without ketu importing pandas.

## Impact Assessment

### For Users

**Breaking changes:**
- `AspectTimeline.to_pandas()` no longer available → use `to_numpy()` or user-side conversion
- `ResonanceField.compute_field()` returns `np.ndarray` instead of `pd.DataFrame` → access fields via `data['res_lon']` or convert to DataFrame

**User-side mitigation:**
```python
# Option 1: Use NumPy directly (recommended)
data = timeline.to_numpy()

# Option 2: Convert to pandas yourself
import pandas as pd
df = pd.DataFrame(timeline.to_dict_list())
df.set_index('timestamp', inplace=True)

# Option 3: Convert NumPy to pandas
df = pd.DataFrame(timeline.to_numpy())
```

**Zero impact:**
- Passing pandas DatetimeIndex to `generate_cycle_series()` still works (duck-typing preserved)
- All NumPy-based workflows unchanged

### For Ketu

**Benefits:**
- Pure NumPy contract enforced - no hidden dependencies
- Simpler dependency tree for PyPI package
- Smaller installation footprint
- Clearer API surface (NumPy-only exports)

**Maintenance:**
- One less dependency to track/update
- Clearer separation: ketu = calculations, user code = presentation

## Files Changed

**Source Code (5 files):**
- `ketu/aspects/timelines.py` (47 lines deleted: to_pandas + _get_pandas_columns)
- `ketu/cycles/calculator.py` (type hints + docstrings)
- `ketu/cycles/__init__.py` (docstring example)
- `ketu/resonance.py` (created: 201 lines, NumPy-only implementation)
- `tests/test_aspect_timelines.py` (test_to_pandas → test_no_pandas_import)

**Documentation (3 files):**
- `docs/aspect_timelines.md` (all examples updated)
- `ketu/aspects/README.md` (export methods list)
- `UPGRADING.md` (comprehensive migration guide)

**Total:** 8 files modified, 1 file created

## Commits

1. **c9f0a1c** - `refactor(03-01): remove pandas dependency from ketu source`
   - Removed to_pandas() from AspectTimeline
   - Converted ResonanceField to NumPy
   - Updated type hints and docstrings
   - Updated tests (195→196, removed test_to_pandas, added test_no_pandas_import)

2. **39a3f59** - `docs(03-01): update documentation for pandas removal`
   - Updated all documentation examples
   - Added migration guide to UPGRADING.md
   - Documented user-side conversion patterns

## Lessons Learned

1. **Duck-typing is good architecture** - Preserving `hasattr(timestamps, 'to_pydatetime')` allows pandas interop without pandas dependency
2. **NumPy structured arrays are sufficient** - No need for DataFrame wrapper in library code
3. **User-side conversion is cleaner** - Let users choose their presentation layer (pandas, polars, etc.)
4. **Clear migration guides matter** - Comprehensive before/after examples reduce user pain

## Next Steps

Phase 03 Plan 02 will address remaining dependency cleanup items per 03-RESEARCH.md findings.

---

## Self-Check: PASSED ✓

**Created Files:**
- ✓ ketu/resonance.py

**Modified Files:**
- ✓ ketu/aspects/timelines.py
- ✓ ketu/cycles/calculator.py
- ✓ ketu/cycles/__init__.py
- ✓ tests/test_aspect_timelines.py
- ✓ docs/aspect_timelines.md
- ✓ ketu/aspects/README.md
- ✓ UPGRADING.md

**Commits:**
- ✓ c9f0a1c (refactor pandas removal)
- ✓ 39a3f59 (docs update)

**Tests:**
- ✓ 196 tests collected and passing

---

**Phase 03 Plan 01 Complete** ✓
Duration: 6 minutes 10 seconds
Tests: 196/196 passing
Pandas imports in ketu/: 0
Status: Ready for 1.0.0 release
