# Upgrading

This guide collects migration notes between Ketu releases. Sections are
ordered newest-first.

## v1.0 -> v1.1

Ketu v1.1 is a backward-compatible feature release (configurable
aspects, houses module, CLI refactor) with **one breaking numerical
fix**: the Mean Apogee Lilith longitude formula. All other body
positions, cycles, harmonics, and aspect calculations involving
non-Lilith bodies are **unchanged** between v1.0 and v1.1.

### Lilith (Black Moon) Calculation

The Mean Apogee Lilith formula has been **corrected** in v1.1 to match
Swiss Ephemeris's `SE_MEAN_APOG`. Values returned by
`get_lilith_position(jd)` and `calc_planet_position(jd, 12)` differ
from v1.0 by approximately **180 deg** on essentially every date in
the 1900-2050 range.

**Root cause:** the v1.0 formula `83.3532 + 0.1114040803 * d` was
actually computing the lunar mean *perigee* longitude (the apogee plus
180 deg, mod 360), not the apogee. The formula was never externally
verified against an independent reference implementation. v1.1's Plan
03 cross-check harness (`tests/test_lilith_cross_check.py`) measured
`MAX |delta| = 179.936579 deg` against `swe.calc_ut(jd, swe.MEAN_APOG)`
on five dates spanning 1900-2050.

**Fix:** v1.1 ships a re-fitted formula:

```text
lilith_lon = (E + R * d + A * sin(omega * d + phi)) mod 360 deg
where d = JD_UT - 2451545.0
  E     = 263.3521188770 deg     (mean longitude at J2000.0)
  R     = 0.1114036699  deg/day  (mean motion)
  A     = 0.1156754590  deg      (perturbation amplitude)
  omega = 0.3287143373  deg/day  (perturbation rate, period ~1095 days)
  phi   = 96.6084061482 deg      (perturbation phase at J2000.0)
```

Note: this is a deliberate deviation from a pure Chapront secular
linear formula. v1.1 ships **linear secular term + one sin()
perturbation**, not a raw ELP-2000 polynomial. The single perturbation
term absorbs a residual sinusoidal component (period approximately
1095 days, amplitude approximately 0.116 deg) that a pure linear
correction could not reduce below the 0.01 deg tolerance. All five
parameters were jointly nonlinear-least-squares-fitted against
`swe.calc_ut(jd, swe.MEAN_APOG)` over 55K daily samples 1900-2050.

**Post-fix accuracy** (vs. Swiss Ephemeris `SE_MEAN_APOG`):

- Max |delta| over the five Plan 03 cross-check dates: **0.002693 deg**
- Max |delta| over 55K daily samples 1900-2050:        **0.007815 deg**

Both well below the **0.01 deg** user-facing tolerance documented in
`docs/LILITH_DEFINITION.md`.

**Concrete v1.0 -> v1.1 examples** (the `Delta v1.1 - v1.0` column is
the user-visible shift in Ketu output, computed as
`signed_circular_diff(v1_1, v1_0)` in degrees, NOT the Ketu-vs-swe
residual):

| Date                   | v1.0 Lilith (deg) | v1.1 Lilith (deg) | Delta v1.1 - v1.0 (deg) |
|------------------------|-------------------|-------------------|-------------------------|
| 1900-06-15 12:00:00 UT |        352.812244 |        172.874759 |             -179.937486 |
| 1950-03-21 18:30:00 UT |        217.722980 |         37.629503 |             +179.906523 |
| 2000-01-01 12:00:00 UT |         83.353200 |        263.467026 |             -179.886174 |
| 2025-09-23 06:00:00 UT |         50.189492 |        230.090328 |             +179.900836 |
| 2050-12-21 00:00:00 UT |        357.307261 |        177.413556 |             -179.893705 |

(v1.0 column reproduces the legacy formula
`(83.3532 + 0.1114040803 * (jd - 2451545.0)) mod 360`; v1.1 column is
the live `get_lilith_position` output. Deltas are wrapped into
`(-180, +180]`. The signs alternate because both v1.0 and v1.1 wrap
around 360 deg at slightly different rates -- the user-visible
magnitude is approximately 180 deg on every date.)

**Action required:** Recompute any cached Lilith values produced by
v1.0. If you stored Ketu output (lunation timing arrays for the lunar
apogee, ML feature columns including Lilith longitude or its
derivatives, aspect-window catalogues for Lilith, natal/transit
charts) for downstream consumption, regenerate them with v1.1.

**Downstream consumers (Kala, etc.):** Lilith body index `12` is
unchanged. Positional arrays remain length-14 (no schema break). Only
the longitude returned for a given JD shifts by approximately 180 deg.
Any pipeline that re-runs Ketu calls is automatically migrated;
pipelines that consume cached v1.0 outputs without recomputation will
silently retain the v1.0 (incorrect) values.

**See also:**

- `docs/LILITH_DEFINITION.md` -- full definition, formula, reference
  frame, source theory, tolerance derivation, and v1.0 -> v1.1
  History.
- `tests/test_lilith_cross_check.py` -- the cross-check harness (run
  via `pip install -e .[test] && pytest tests/test_lilith_cross_check.py`).
- `CHANGELOG.md` v1.1.0 entry -- short release-notes summary.

### Other v1.0 -> v1.1 Changes

Other v1.1 work (configurable aspects, houses module, CLI refactor)
is backward-compatible. See per-feature documentation and the
`CHANGELOG.md` v1.1.0 entry for non-Lilith additions.

---

## v0.4.x -> v1.0.0

Ketu 1.0.0 is a breaking release focused on API cleanup and simplification. This guide will help you migrate your code from version 0.4.x to 1.0.0.

## Overview

Version 1.0.0 removes visualization and export functionality, making Ketu a pure astronomical calculation library. All functions are now accessed via explicit submodule imports, creating a cleaner and more maintainable API surface.

## Removed Features

### Pandas Dependency

**Status:** Removed

Ketu 1.0.0 is a pure NumPy library. The pandas dependency has been removed, and all methods that returned pandas DataFrames have been eliminated.

#### AspectTimeline.to_pandas() Removed

```python
# v0.4.x (NO LONGER WORKS)
from ketu.aspects import generate_aspect_timeline
timeline = generate_aspect_timeline("Sun", "Mars", "2024-01-01", "2024-12-31")
df = timeline.to_pandas()  # NO LONGER EXISTS

# v1.0.0 - Option 1: Use to_numpy() for ML workflows
timeline = generate_aspect_timeline("Sun", "Mars", "2024-01-01", "2024-12-31")
data = timeline.to_numpy()  # NumPy structured array

# v1.0.0 - Option 2: User-side conversion via dict (preserves string fields)
import pandas as pd
df = pd.DataFrame(timeline.to_dict_list())
df.set_index('timestamp', inplace=True)

# v1.0.0 - Option 3: User-side conversion via NumPy (numeric fields)
df = pd.DataFrame(timeline.to_numpy())
```

#### Type Hints No Longer Reference pandas

Type hints for `timestamps` parameters no longer include `pd.DatetimeIndex`. However, duck-typing support is preserved — you can still pass pandas DatetimeIndex objects, and they will be handled correctly via `hasattr(timestamps, 'to_pydatetime')`.

```python
# v0.4.x type hint
def generate_cycle_series(
    timestamps: Union[np.ndarray, List[datetime], "pd.DatetimeIndex"]
) -> np.ndarray: ...

# v1.0.0 type hint (pandas removed from signature)
def generate_cycle_series(
    timestamps: Union[np.ndarray, List[datetime]]
) -> np.ndarray: ...

# But pandas DatetimeIndex still works via duck-typing!
import pandas as pd
timestamps = pd.date_range("2025-01-01", "2025-12-31", freq="1D")
cycles = generate_cycle_series("Sun", "Mars", timestamps)  # Works fine
```

### Chart Visualization

**Status:** Removed

The `ketu.export.chart` module and all chart visualization features have been removed. This includes `draw_zodiacal_chart()` and related matplotlib-based visualization functions.

```python
# v0.4.x (NO LONGER WORKS)
from ketu.export import draw_zodiacal_chart
draw_zodiacal_chart(positions, aspects)

# v1.0.0 (NO REPLACEMENT)
# Chart functionality removed from ketu
```

**Migration tip:** If you need chart visualization, copy the `chart.py` file from v0.4.0 into your own project, or use a dedicated astrology visualization package.

### iCalendar Export

**Status:** Removed

The `ketu.export.icalendar` module has been removed along with the icalendar dependency.

```python
# v0.4.x (NO LONGER WORKS)
from ketu.export import export_to_icalendar

# v1.0.0 (NO REPLACEMENT)
# iCalendar export removed from ketu
```

**Migration tip:** If you need iCalendar export, copy the relevant code from v0.4.0 or implement it in your application layer.

### Optional Dependencies

**Status:** Removed

Optional dependency installation via pip extras is no longer supported. All optional dependencies have been removed.

```bash
# v0.4.x (NO LONGER WORKS)
pip install ketu[chart]
pip install ketu[icalendar]
pip install ketu[all]

# v1.0.0 (ONLY NUMPY REQUIRED)
pip install ketu
```

## Import Changes

### New Import Pattern

All functions must now be imported from their respective submodules. Top-level imports of functions are no longer supported.

```python
# v0.4.x (NO LONGER WORKS)
from ketu import utc_to_julian, long, positions
from ketu import calculate_aspects, find_aspect_timing
from ketu import generate_cycle_series

# v1.0.0 (REQUIRED)
from ketu.calculations import utc_to_julian, long, positions
from ketu.aspects import calculate_aspects, find_aspect_timing
from ketu.cycles import generate_cycle_series
```

### What Still Works

Core constants and metadata remain accessible at the top level:

```python
# v1.0.0 (UNCHANGED)
from ketu import bodies, aspects, signs
from ketu import __version__, __author__, __license__

print(bodies)   # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
print(aspects)  # [0, 60, 90, 120, 180]
print(signs)    # ['Ari', 'Tau', 'Gem', 'Can', 'Leo', 'Vir', ...]
```

## Submodule Reference

Quick reference for migrating common imports:

| Old import (v0.4.x) | New import (v1.0.0) |
|---------------------|---------------------|
| `from ketu import utc_to_julian` | `from ketu.calculations import utc_to_julian` |
| `from ketu import long` | `from ketu.calculations import long` |
| `from ketu import positions` | `from ketu.calculations import positions` |
| `from ketu import body_properties` | `from ketu.calculations import body_properties` |
| `from ketu import vlong` | `from ketu.calculations import long_velocity` |
| `from ketu import vlat` | `from ketu.calculations import lat_velocity` |
| `from ketu import vdist_au` | `from ketu.calculations import dist_velocity_au` |
| `from ketu import calculate_aspects` | `from ketu.aspects import calculate_aspects` |
| `from ketu import find_aspect_timing` | `from ketu.aspects import find_aspect_timing` |
| `from ketu import find_aspect_window` | `from ketu.aspects import find_aspect_window` |
| `from ketu import generate_cycle_series` | `from ketu.cycles import generate_cycle_series` |
| `from ketu import generate_multi_cycle_series` | `from ketu.cycles import generate_multi_cycle_series` |

### Available Submodules

- `ketu.calculations` - Position and velocity calculations
- `ketu.aspects` - Aspect calculations, windows, timelines, transits
- `ketu.cycles` - Planetary cycle time series generation
- `ketu.ephemeris` - Low-level ephemeris computations
- `ketu.cache` - Ephemeris caching for fast lookups
- `ketu.complex` - Complex number representations for ML
- `ketu.lunar_calendar` - Lunar calendar generation
- `ketu.display` - CLI display functions

## Renamed Functions

### Velocity Functions

The ambiguous `vlong()`, `vlat()`, and `vdist_au()` functions have been renamed to explicit names that clearly indicate they return velocity (speed) values, not position values.

| Old name (v0.4.x) | New name (v1.0.0) | Returns |
|--------------------|-------------------|---------|
| `vlong(jd, body)` | `long_velocity(jd, body)` | Longitude speed (deg/day) |
| `vlat(jd, body)` | `lat_velocity(jd, body)` | Latitude speed (deg/day) |
| `vdist_au(jd, body)` | `dist_velocity_au(jd, body)` | Distance speed (AU/day) |

```python
# v0.4.x (NO LONGER WORKS)
from ketu.calculations import vlong, vlat, vdist_au
moon_speed = vlong(jd, 1)

# v1.0.0 (REQUIRED)
from ketu.calculations import long_velocity, lat_velocity, dist_velocity_au
moon_speed = long_velocity(jd, 1)
```

**Why the rename:** The "v" prefix was ambiguous — it could mean "value" or "velocity." The new names make it explicit that these functions return speed/velocity, not position values.

## Installation

```bash
# Install ketu 1.0.0 (only numpy required)
pip install ketu==1.0.0
```

## Quick Migration Checklist

- [ ] Search your codebase for `from ketu import` (functions)
- [ ] Update all function imports to use submodule paths
- [ ] Update imports of `bodies`, `aspects`, `signs` (these still work from top level)
- [ ] Rename `vlong()` → `long_velocity()`, `vlat()` → `lat_velocity()`, `vdist_au()` → `dist_velocity_au()`
- [ ] Remove `ketu[chart]`, `ketu[icalendar]`, or `ketu[all]` from requirements files
- [ ] Remove any usage of `ketu.export.chart` or `ketu.export.icalendar`
- [ ] Test your code in a clean virtual environment
- [ ] Run your test suite to verify all imports work

## Example Migration

Here's a complete example showing the migration process:

```python
# v0.4.x code
from ketu import utc_to_julian, positions, calculate_aspects
from ketu import bodies
from datetime import datetime, timezone

now = datetime.now(timezone.utc)
jd = utc_to_julian(now)
pos = positions(jd, bodies)
asp = calculate_aspects(jd, bodies)

# v1.0.0 code (migrated)
from ketu.calculations import utc_to_julian, positions
from ketu.aspects import calculate_aspects
from ketu import bodies
from datetime import datetime, timezone

now = datetime.now(timezone.utc)
jd = utc_to_julian(now)
pos = positions(jd, bodies)
asp = calculate_aspects(jd, bodies)
```

## Getting Help

If you encounter issues during migration:

- Check the [documentation](https://ketu.readthedocs.io) for detailed API reference
- Open an issue on [GitHub](https://github.com/alkimya/ketu/issues)
- Review the source code for available functions in each submodule
