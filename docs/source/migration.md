# Migration Guide

This guide helps you migrate from Ketu v0.4.0 to v1.0.0.

**This is a MAJOR version bump with breaking changes.** See [UPGRADING.md](../../UPGRADING.md) for detailed migration instructions.

## What Changed

### Removed: Export Modules

Ketu 1.0 is a pure calculation library. Visualization and calendar export features have been removed:

- **Removed modules**: `ketu.export.chart`, `ketu.export.icalendar`
- **Removed functions**: `draw_zodiacal_chart()`, `export_lunations_to_ical()`, `export_aspects_to_ical()`, `export_transits_to_ical()`
- **Why**: Ketu focuses on numerical calculations. Visualization belongs in application layers (GUI, web dashboards, etc.)

**Migration**: If you need these features, pin to `ketu==0.4.0` or implement visualization in your application layer using Ketu's calculation results.

### Removed: Pandas Dependency

- `generate_aspect_timeline()` now returns NumPy structured array (was DataFrame)
- `AspectTimeline.to_pandas()` removed
- **Migration**: Use `import pandas as pd; df = pd.DataFrame(timeline)` for manual conversion

### Renamed: Velocity Functions (Breaking)

- `vlong()` → `long_velocity()`
- `vlat()` → `lat_velocity()`
- `vdist_au()` → `dist_velocity_au()`
- **Why**: Explicit names prevent confusion. The old "v" prefix was ambiguous.

**Migration**: Use find-and-replace in your codebase:
```bash
sed -i 's/ketu\.vlong(/ketu.long_velocity(/g' *.py
sed -i 's/ketu\.vlat(/ketu.lat_velocity(/g' *.py
sed -i 's/ketu\.vdist_au(/ketu.dist_velocity_au(/g' *.py
```

### Changed: Public API Surface

- `ketu.__init__.py` exports only metadata + core constants
- Functions accessed via submodule imports: `from ketu.calculations import long`
- `ketu.__all__` explicitly lists public API

**Migration**: Most users won't notice this change. If you were importing from internal modules, switch to public API imports.

## Correctness Fixes

**IMPORTANT: These fixes change calculation results. Recompute cached 0.4.0 results.**

### Fixed Issues

1. **Cache operator precedence bug**: `use_cache=False` was ignored due to missing parentheses
2. **Aspect vectorization non-determinism**: `calculate_aspects_vectorized()` now returns consistent results
3. **Moon velocity wrapping**: Correct velocity at 360°/0° boundary (was showing ±360° spikes)

**Impact**: If you cached results from 0.4.0, recompute them with 1.0.0 for correctness.

## New Features

- **Type hints everywhere**: mypy strict mode compliance
- **NumPy-style docstrings**: Examples section in all public functions
- **Standardized error messages**: All `ValueError` messages include received value + valid options
- **Numerical precision guarantees**: ±1e-6° for angular separation (documented)

## Migration Steps

### Step 1: Review Breaking Changes

Read [UPGRADING.md](../../UPGRADING.md) for detailed migration instructions.

### Step 2: Update Package

```bash
pip install --upgrade ketu
```

### Step 3: Update Your Code

**Replace velocity function calls:**

```python
# Before (v0.4.0)
v = ketu.vlong(jday, body_id)

# After (v1.0.0)
v = ketu.long_velocity(jday, body_id)
```

**Replace pandas conversions:**

```python
# Before (v0.4.0)
timeline = ketu.generate_aspect_timeline(...)
df = timeline.to_pandas()

# After (v1.0.0)
import pandas as pd
timeline = ketu.generate_aspect_timeline(...)
df = pd.DataFrame(timeline)
```

**Remove chart/icalendar calls:**

```python
# Before (v0.4.0) - REMOVED
ketu.draw_zodiacal_chart(jday, output_file="chart.svg")
ketu.export_lunations_to_ical(start, end, "lunations.ics")

# After (v1.0.0) - No replacement
# Implement visualization in your application layer using ketu calculation results
```

### Step 4: Test Your Code

Run your test suite to catch any remaining issues.

### Step 5: Recompute Cached Results

If you cached calculation results from 0.4.0, recompute them for correctness.

## Rollback

If you need to rollback to v0.4.0:

```bash
pip install ketu==0.4.0
```

Note: v0.4.x will not receive further updates. v1.0.0 is the recommended version.

## Getting Help

If you encounter issues:

1. Check [UPGRADING.md](../../UPGRADING.md) for detailed migration guide
2. Review [CHANGELOG.md](../../CHANGELOG.md) for complete list of changes
3. Open an [issue](https://github.com/alkimya/ketu/issues)
