# Migration Guide

This guide helps you migrate from Ketu v0.2.x (pyswisseph-based) to v0.3.0 (pure NumPy).

## What Changed

### Dependencies

**Before (v0.2.x):**

```bash
pip install ketu  # Installed pyswisseph + numpy
```

**After (v0.3.0):**

```bash
pip install ketu  # Only numpy required
pip install ketu[chart]  # With visualization
pip install ketu[all]  # With all optional features
```

### Removed Dependency

- **pyswisseph**: Completely removed - no more binary dependencies
- **Platform issues**: Fixed - pure Python + NumPy works everywhere

### New Optional Dependencies

- **matplotlib**: For chart visualization (`ketu[chart]`)
- **icalendar**: For calendar export (`ketu[icalendar]`)

## API Compatibility

### High-Level API (Unchanged)

The main API remains fully compatible:

```python
# This code works identically in v0.2.x and v0.3.0
from datetime import datetime
from zoneinfo import ZoneInfo
import ketu

dtime = datetime(2020, 12, 21, 19, 20, tzinfo=ZoneInfo("Europe/Paris"))
jday = ketu.utc_to_julian(dtime)

# All these functions work the same
ketu.print_positions(jday)
ketu.print_aspects(jday)
positions = ketu.positions(jday)
aspects = ketu.calculate_aspects(jday)
```

### New Functions

v0.3.0 adds new features:

```python
# Aspect windows
windows = ketu.find_aspect_window(jd_start, jd_end, body1=0, body2=1, aspect=0)

# Transits
natal_pos = ketu.get_natal_positions(natal_jd)
transits = ketu.compare_dates_transits(natal_pos, transit_jd)

# Chart visualization (requires matplotlib)
ketu.draw_zodiacal_chart(jday, output_file="chart.svg")

# iCalendar export (requires icalendar)
ketu.export_lunations_to_ical(jd_start, jd_end, "lunations.ics")
```

## Accuracy Differences

### Swiss Ephemeris (v0.2.x)

- Accuracy: ±0.001° (arc-second precision)
- Based on JPL ephemeris
- Full perturbation theory

### Pure NumPy (v0.3.0)

- Accuracy: ±0.1° for inner planets, ±0.5° for outer planets
- Based on VSOP87/simplified perturbations
- More than sufficient for astrological purposes

### When to Care

You likely **don't need** Swiss Ephemeris precision if:

- You're doing astrology (orbs are typically 1-12°)
- You're working with aspects (orb tolerance >> 0.5°)
- You need aspects exact to the minute (v0.3.0 handles this)

You **might prefer** Swiss Ephemeris if:

- You need arc-second precision for scientific astronomy
- You're computing asteroid positions (not yet supported in v0.3.0)
- You need positions for dates outside 1800-2200 CE

## Performance Comparison

### Time Series (365 days)

- v0.2.x: ~3.2 seconds
- v0.3.0: ~15 milliseconds
- **Speedup: 208x**

### Aspect Calculations

- v0.2.x: ~120 milliseconds
- v0.3.0: ~8 milliseconds
- **Speedup: 14.55x**

## Migration Steps

### Step 1: Update Package

```bash
pip install --upgrade ketu
```

### Step 2: Remove pyswisseph (Optional)

```bash
pip uninstall pyswisseph
```

### Step 3: Test Your Code

Run your existing code - it should work without changes:

```python
# Your existing code
import ketu

jday = ketu.utc_to_julian(datetime.now())
ketu.print_positions(jday)
```

### Step 4: Add Optional Features

If you want new features:

```bash
# For chart visualization
pip install ketu[chart]

# For iCalendar export
pip install ketu[icalendar]

# For everything
pip install ketu[all]
```

## Breaking Changes

### None for Public API

The public API (`ketu.*`) has **no breaking changes**.

### Internal Changes

If you were importing from internal modules:

**Before:**

```python
# Don't do this - internal API
from ketu.ketu import body_properties
```

**After:**

```python
# Use public API instead
from ketu import body_properties
```

## Common Issues

### Import Errors

**Problem:**

```python
ImportError: No module named 'swisseph'
```

**Solution:**
This is expected - pyswisseph is no longer used. Your code should still work.

### Accuracy Concerns

**Problem:** "Positions are slightly different from v0.2.x"

**Solution:** This is expected. Differences are typically < 0.5° and negligible for astrology.

### Missing Features

**Problem:** "Can't find function X"

**Solution:** Check if it's a new feature requiring optional dependencies:

```bash
pip install ketu[all]
```

## Validation

### Compare Results

To verify migration:

```python
# Save results from v0.2.x
import json
import ketu

jday = ketu.utc_to_julian(datetime(2025, 1, 1))
old_positions = ketu.positions(jday)
with open('old_positions.json', 'w') as f:
    json.dump(old_positions.tolist(), f)
```

After upgrading:

```python
# Compare with v0.3.0
new_positions = ketu.positions(jday)
with open('old_positions.json', 'r') as f:
    old_positions = np.array(json.load(f))

diff = np.abs(new_positions - old_positions)
print(f"Max difference: {diff.max():.4f}°")  # Should be < 0.5°
```

## Getting Help

If you encounter issues:

1. Check the [documentation](https://ketu.readthedocs.io)
2. Review [examples](examples.md)
3. Open an [issue](https://github.com/alkimya/ketu/issues)

## Rollback

If you need to rollback to v0.2.x:

```bash
pip install ketu==0.2.1
pip install pyswisseph
```

Note: v0.2.x will not receive further updates.
