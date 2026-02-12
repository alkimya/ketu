# Phase 3: Dependency Cleanup - Research

**Researched:** 2026-02-12
**Domain:** Python dependency management, NumPy structured arrays, API design
**Confidence:** HIGH

## Summary

Phase 3 removes the hidden Pandas dependency from Ketu, ensuring the library remains pure NumPy as documented. The primary issue is `generate_aspect_timeline()` currently returns an `AspectTimeline` object with a `to_pandas()` method that imports pandas at runtime. While the import is lazy (only when called), this creates a "soft dependency" that users may expect to work.

The solution is straightforward: remove the `to_pandas()` method entirely, document the breaking change, and rely on users to convert NumPy structured arrays to Pandas DataFrames themselves if needed (it's a one-liner). The `to_numpy()` method already exists and returns proper NumPy structured arrays, which is the contract Ketu promises.

**Primary recommendation:** Remove `AspectTimeline.to_pandas()` method entirely, update tests to use `to_numpy()`, document conversion pattern for users who need Pandas.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| NumPy | >=1.20.0 | Structured arrays for tabular data | Already core dependency, no additional deps, C-speed performance |
| pytest | Latest | Test framework | Already in dev dependencies, will use `importorskip` pattern |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| N/A | N/A | No supporting libraries needed | Pure refactoring task |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Remove method | Keep with optional dependency | Keeping creates maintenance burden, violates NumPy-only contract |
| Remove method | Deprecate first, remove in v0.5.0 | Unnecessary delay - v0.4.0 → v0.5.0 is already a major bump |

**Installation:**
No new dependencies required. This is a removal task.

## Architecture Patterns

### Current State (BEFORE)
```
ketu/aspects/timelines.py
├── AspectTimeline.to_numpy()      ✓ Pure NumPy
├── AspectTimeline.to_pandas()     ✗ Lazy pandas import
└── AspectTimeline.to_dict_list()  ✓ Pure Python
```

### Target State (AFTER)
```
ketu/aspects/timelines.py
├── AspectTimeline.to_numpy()      ✓ Pure NumPy (PRIMARY)
├── AspectTimeline.to_dict_list()  ✓ Pure Python
└── [to_pandas removed]
```

### Pattern 1: NumPy Structured Arrays for Tabular Data

**What:** Use NumPy structured arrays with named dtypes for columnar data instead of Pandas DataFrames.

**When to use:** When building libraries that need to avoid heavy dependencies, when data is numeric/homogeneous, when interfacing with C code, when performance matters more than convenience.

**Example:**
```python
# Current implementation (KEEP)
def to_numpy(self) -> np.ndarray:
    """Convert to NumPy structured array (dense format for ML).

    Returns:
        Structured array with all event data
    """
    if not self.events:
        return np.array([], dtype=self._get_numpy_dtype())

    data = []
    for event in self.events:
        data.append((
            event.julian_day,
            event.body1_id,
            event.body2_id,
            event.aspect_type,
            # ... etc
        ))

    return np.array(data, dtype=self._get_numpy_dtype())

@staticmethod
def _get_numpy_dtype():
    """Get NumPy dtype for structured array."""
    return np.dtype([
        ('julian_day', 'f8'),
        ('body1_id', 'i4'),
        ('body2_id', 'i4'),
        ('aspect_type', 'f4'),
        # ... etc
    ])
```

### Pattern 2: Lazy Optional Imports (ANTI-PATTERN for this project)

**What:** Import optional dependencies only when methods are called.

**Why it's wrong here:** Violates Ketu's NumPy-only contract. Users installing fresh see "ketu" works without pandas, assume it's pure NumPy, then hit runtime ImportError when calling methods. Creates confusion.

**What to do instead:** Remove optional methods entirely. If users need Pandas, they can convert themselves (documented in migration guide).

### Pattern 3: User-Side Conversion Pattern (RECOMMENDED)

**What:** Provide clear documentation for users to convert NumPy structured arrays to Pandas if needed.

**Example:**
```python
# User code after migration
from ketu.aspects import generate_aspect_timeline
import pandas as pd

timeline = generate_aspect_timeline("Sun", "Mars", "2024-01-01", "2024-12-31")

# Option 1: Get NumPy structured array
np_data = timeline.to_numpy()

# Option 2: Convert to Pandas yourself (one-liner)
df = pd.DataFrame(timeline.to_dict_list())
df.set_index('timestamp', inplace=True)

# Or even simpler
df = pd.DataFrame(timeline.to_numpy())
```

### Anti-Patterns to Avoid

- **Soft dependencies with lazy imports:** Creates confusing user experience where library "sometimes" works depending on what methods you call
- **extras_require for core functionality:** `to_pandas()` is listed as export method alongside `to_numpy()`, implies they're equally supported
- **Deprecation before removal in major bumps:** v0.4.0 → v0.5.0 is already breaking changes OK, no need for deprecation cycle

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Structured array type definitions | Custom dtype builders | np.dtype() with list of tuples | Official NumPy API, well-tested, standard |
| Array field access | Custom accessor methods | Direct field indexing `arr['field']` | NumPy native, faster, no overhead |
| Optional dependency management | Custom import wrappers | Remove entirely for this use case | Ketu's contract is NumPy-only |

**Key insight:** NumPy structured arrays already provide everything needed. Don't build abstractions over them - use them directly.

## Common Pitfalls

### Pitfall 1: Thinking Pandas is "required" for ML/data work
**What goes wrong:** Developer assumes removing `to_pandas()` breaks ML workflows because "everyone uses pandas."

**Why it happens:** Pandas is dominant in data science, creates assumption it's mandatory.

**How to avoid:** Recognize that:
- NumPy structured arrays work with sklearn, PyTorch, TensorFlow directly
- `to_dict_list()` still exists for JSON serialization
- Users who want Pandas can convert in 1-2 lines (well-documented)

**Warning signs:** Temptation to keep method "for convenience" despite breaking contract.

### Pitfall 2: Leaving import statement at module level
**What goes wrong:** Even though `to_pandas()` method will be removed, resonance.py has `import pandas as pd` at the top level, creating hard dependency.

**Why it happens:** resonance.py uses pandas for date_range and DataFrame creation.

**How to avoid:**
- Check ALL files that import pandas (already found: cycles/calculator.py type hints, resonance.py hard import)
- Remove type hints that reference `pd.DatetimeIndex`
- Either remove resonance.py features or refactor to use NumPy

**Warning signs:** Tests fail with `ModuleNotFoundError: No module named 'pandas'` in unexpected files.

### Pitfall 3: Breaking tests that use pytest.importorskip
**What goes wrong:** Test `test_to_pandas` currently uses `pytest.importorskip("pandas")` to skip if pandas not installed. After removal, need to delete the entire test, not just change the skip.

**Why it happens:** Mechanical refactoring - search/replace without understanding test intent.

**How to avoid:**
- Delete entire `test_to_pandas` test class/method
- Keep `test_to_numpy` and verify it works
- Add test verifying pandas NOT imported: `assert 'pandas' not in sys.modules` after running test suite

**Warning signs:** Test file still mentions pandas anywhere.

### Pitfall 4: Leaving pandas in docstring examples
**What goes wrong:** Code examples in docstrings/docs still show `df = timeline.to_pandas()`.

**Why it happens:** Documentation updated separately from code, gets forgotten.

**How to avoid:**
- Search ALL files for "to_pandas", "pd.DataFrame", "pandas" in comments/docstrings
- Update examples to show `to_numpy()` as primary export
- Add migration guide showing how users convert themselves if needed

**Warning signs:** `grep -r "to_pandas" ketu/` returns anything.

### Pitfall 5: Not testing fresh install
**What goes wrong:** Tests pass in dev environment (which has pandas installed), but fail for users installing fresh.

**Why it happens:** Development environment accumulates dependencies, masks missing dependencies.

**How to avoid:**
- Test in fresh venv: `python -m venv /tmp/test_ketu && /tmp/test_ketu/bin/pip install .`
- Run: `/tmp/test_ketu/bin/python -c "import ketu; import sys; assert 'pandas' not in sys.modules"`
- Verify with `pip show ketu` that pandas is not in "Requires" line

**Warning signs:** CI passes but user reports ImportError.

## Code Examples

### Example 1: Accessing NumPy Structured Array Fields

```python
# Source: https://numpy.org/doc/stable/user/basics.rec.html
# After getting NumPy array from to_numpy()
timeline = generate_aspect_timeline("Sun", "Mars", "2024-01-01", "2024-12-31")
data = timeline.to_numpy()

# Access individual columns
julian_days = data['julian_day']
aspect_types = data['aspect_type']
orbs = data['orb']

# Boolean indexing
exact_aspects = data[data['aspect_orb'] > 0]

# Multiple field selection (NumPy 1.16+)
subset = data[['julian_day', 'aspect_type', 'orb']]
```

### Example 2: User-Side Pandas Conversion (for migration docs)

```python
# Source: Migration guide to be written
# Users who need Pandas can convert themselves
from ketu.aspects import generate_aspect_timeline

timeline = generate_aspect_timeline("Sun", "Mars", "2024-01-01", "2024-12-31")

# Method 1: Via dict (preserves all string fields)
import pandas as pd
df = pd.DataFrame(timeline.to_dict_list())
df.set_index('timestamp', inplace=True)

# Method 2: Via NumPy structured array (numeric fields only)
df = pd.DataFrame(timeline.to_numpy())

# Method 3: Custom conversion for specific fields
data = timeline.to_numpy()
df = pd.DataFrame({
    'julian_day': data['julian_day'],
    'aspect_type': data['aspect_type'],
    'orb': data['orb'],
})
```

### Example 3: Removing resonance.py Pandas Dependency

```python
# Source: Current implementation analysis
# BEFORE: resonance.py uses pandas
import pandas as pd

timestamps = pd.date_range(start_dt, end_dt, freq=f"{step_hours}h")
df = pd.DataFrame(index=timestamps)
df['res_lon'] = res_lon
return df

# AFTER: Option 1 - Return NumPy structured array
timestamps = np.arange(
    np.datetime64(start_dt),
    np.datetime64(end_dt),
    np.timedelta64(step_hours, 'h')
)
dtype = np.dtype([
    ('timestamp', 'datetime64[s]'),
    ('res_lon', 'f8'),
    ('res_lat', 'f8'),
    ('res_dec', 'f8'),
])
data = np.zeros(len(timestamps), dtype=dtype)
data['timestamp'] = timestamps
data['res_lon'] = res_lon
data['res_lat'] = res_lat
data['res_dec'] = res_dec
return data

# AFTER: Option 2 - Mark resonance as experimental/deprecated
# Add deprecation warning, plan to remove or refactor in v0.6.0
```

### Example 4: Type Hint Updates

```python
# BEFORE: cycles/calculator.py line 113
timestamps: Union[np.ndarray, List[datetime], "pd.DatetimeIndex"]

# AFTER: Remove pandas reference
timestamps: Union[np.ndarray, List[datetime]]

# Note: Keep duck-typing support via hasattr checks
if hasattr(timestamps, 'to_pydatetime'):  # Still works for pandas users
    dts = timestamps.to_pydatetime()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pandas for all tabular data | NumPy structured arrays for numeric libraries | 2020s trend | Lighter deps, faster installs |
| extras_require for optional features | Clear hard dependencies only | PEP 735 (2023) | Better dependency hygiene |
| Soft dependencies via lazy import | Remove or make hard dependency | Best practice shift | Clearer user expectations |
| Deprecate → remove cycle | Direct removal in major version | Modern Python packaging | Faster iteration |

**Deprecated/outdated:**
- **pandas.np alias**: Removed in pandas 1.0 (2020), never use `pd.np`
- **setup.py for configs**: Modern tools use pyproject.toml
- **Long deprecation cycles for libraries**: v0.x libraries can break in major bumps

## Open Questions

1. **What to do with resonance.py?**
   - What we know: It has hard pandas import (`import pandas as pd` at line 14), uses `pd.date_range` and `pd.DataFrame`
   - What's unclear: Is resonance module core to ketu or experimental? Is it documented/tested?
   - Recommendation: Check test coverage. If resonance is experimental/undocumented, mark with deprecation warning. If it's core, refactor to NumPy arrays as part of this phase.

2. **Should we keep duck-typing for pandas DatetimeIndex?**
   - What we know: `cycles/calculator.py` checks `hasattr(timestamps, 'to_pydatetime')` to support pandas
   - What's unclear: Does this still create soft dependency? Will users expect it to work?
   - Recommendation: KEEP the duck-typing - it doesn't require pandas to be installed, just handles it gracefully if user passes it. This is good interop, not a dependency.

3. **Version bump: v0.4.0 → v0.5.0 or v1.0.0?**
   - What we know: Breaking change (removing public method), semantic versioning says major bump
   - What's unclear: Is ketu ready for v1.0.0 stability commitment?
   - Recommendation: v0.5.0 (next minor in 0.x series). Reserve v1.0.0 for when API is truly stable.

## Sources

### Primary (HIGH confidence)
- NumPy Structured Arrays Official Docs: https://numpy.org/doc/stable/user/basics.rec.html
- Ketu codebase: `/home/loc/workspace/solaris/ketu/ketu/aspects/timelines.py` (read directly)
- Ketu codebase: `/home/loc/workspace/solaris/ketu/pyproject.toml` (read directly)
- Ketu tests: `/home/loc/workspace/solaris/ketu/tests/test_aspect_timelines.py` (read directly)

### Secondary (MEDIUM confidence)
- [NumPy Arrays vs Pandas DataFrames Comparison](https://www.c-sharpcorner.com/article/numpy-arrays-vs-pandas-dataframes-key-differences-explained/)
- [Memory-Efficient Time Series in Python](https://krbnite.github.io/Memory-Efficient-Windowing-of-Time-Series-Data-in-Python-2-NumPy-Arrays-vs-Pandas-DataFrames/)
- [Python Optional Dependencies Best Practices](https://www.pyopensci.org/python-package-guide/package-structure-code/declare-dependencies.html)
- [setuptools dependency management](https://setuptools.pypa.io/en/latest/userguide/dependency_management.html)
- [PEP 735 – Dependency Groups](https://peps.python.org/pep-0735/)

### Tertiary (LOW confidence)
- [Jake VanderPlas - Structured Data NumPy](https://jakevdp.github.io/PythonDataScienceHandbook/02.09-structured-data-numpy.html) - older resource but good fundamentals
- Various Stack Overflow discussions on NumPy vs Pandas (informational background only)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - NumPy already core dependency, removal task has no new dependencies
- Architecture: HIGH - Code already has `to_numpy()` implemented correctly, pattern is proven
- Pitfalls: HIGH - Based on direct codebase analysis + common Python packaging issues
- Open questions: MEDIUM - Need to verify resonance.py usage and test coverage

**Research date:** 2026-02-12
**Valid until:** 2026-04-12 (60 days - stable domain, NumPy patterns don't change rapidly)
