# Upgrading

This guide collects migration notes between Ketu releases. Sections are
ordered newest-first.

## v1.1 -> v1.2

Ketu v1.2 is a fully backward-compatible feature release. All v1.1 code
continues to work unchanged — there are no breaking changes, no default
value changes, and no removed exports. This section is purely
informational: opt in to the new APIs when you are ready.

### New APIs

#### Synastry

```python
from ketu.synastry import calculate_synastry

# chart_a and chart_b are CHART_DTYPE records from compute_chart()
aspects = calculate_synastry(chart_a, chart_b)
# Returns a SYNASTRY_DTYPE structured array (filtered mode, default)
# Use mode="dense" for the full 225-row cross-product matrix.
```

#### Composite chart (midpoint variant)

```python
from ketu.composite import calculate_composite, circular_midpoint

composite = calculate_composite(chart_a, chart_b)
# Returns CHART_DTYPE — bodies, houses, and aspects derived from
# circular midpoints of the two natal charts.

mid = circular_midpoint(359.0, 1.0)  # == 0.0 (short-arc midpoint)
```

#### Solar and Lunar Returns

```python
from ketu.returns import solar_return, lunar_return

# Solar return for a target calendar year
sr = solar_return(natal_jd, natal_lat, natal_lon, target_year=2026)
# target_year must be an integer (e.g. 2026), NOT a Julian Date.

# Lunar return for the first return >= a target Julian Date
lr = lunar_return(natal_jd, natal_lat, natal_lon, target_jd=2461000.0)
# target_jd must be a float Julian Date (e.g. 2461000.0),
# NOT a year integer. Passing 2026 would resolve a return near
# JD 2026 (4677 BC) — always pass a real JD.

# API asymmetry: solar_return takes target_year (int, calendar-anchored),
# lunar_return takes target_jd (float, instant-anchored, ~27.32 d period).

# Relocation: pass return_lat/return_lon to compute the chart for a
# different location while keeping the resolved return instant.
sr_relocated = solar_return(
    natal_jd, natal_lat, natal_lon,
    target_year=2026,
    return_lat=40.71,   # New York
    return_lon=-74.01,
)
```

#### Arabic Parts framework

```python
from ketu.parts import calculate_part, calculate_all_parts

# Single part — sect-aware (Fortune / Spirit dispatch on is_day_chart)
fortune = calculate_part("fortune", chart)     # -> float longitude
spirit  = calculate_part("spirit", chart)      # -> float longitude
marriage = calculate_part("marriage", chart)   # -> float (fixed, no sect)

# All registered parts at once (alphabetical key order)
parts_dict = calculate_all_parts(chart)
# {"fortune": <lon>, "marriage": <lon>, "spirit": <lon>}

# Named subset
subset = calculate_all_parts(chart, parts=["fortune", "spirit"])

# CLI introspection
# ketu --list-parts
```

#### Three new house systems

```python
from ketu import calculate_houses

# Available from v1.2: whole_sign, equal, regiomontanus
houses = calculate_houses(jd, lat, lon, system="whole_sign")
houses = calculate_houses(jd, lat, lon, system="equal")
houses = calculate_houses(jd, lat, lon, system="regiomontanus")

# CLI
# ketu houses --system whole_sign --lat 48.85 --lon 2.35 --date 2026-05-28T12:00:00Z
```

> **Note:** The v1.0 -> v1.1 section below stated that `equal` and
> `whole_sign` were "not yet registered". They are now fully registered
> in v1.2 — this section supersedes that caveat.

### Nothing to change for existing code

If your code was correct under v1.1, it remains correct under v1.2
without modification. There are no numerical behavior changes, no
default argument changes, and no removed symbols. The new subpackages
(`ketu.synastry`, `ketu.composite`, `ketu.returns`, `ketu.parts`) and
house systems are purely additive.

---

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

### CLI Default Aspect Set (Phase 9 / ASP-04)

In v1.0, the `ketu` CLI emitted **14 aspects per body pair** by
default (the EXTENDED preset: conjunction, opposition, trine, square,
sextile, quincunx, semisextile, semisquare, sesquisquare, quintile,
biquintile, novile, septile, decile).

In v1.1, the CLI default is **CLASSICAL: the 5 major aspects only**
(conjunction, opposition, trine, square, sextile). Scripts that
parsed v1.0 CLI output will receive approximately 64% fewer aspect
rows per body pair.

The `core.aspects` array is **unchanged** (length-14, append-only —
verified by the Phase 9 invariant test in
`tests/test_aspects_invariants.py`). Positional indexing into the
array still works. Only the *default selection* the CLI applies on
top of the array changed.

**Migration recipe (CLI users)**

```bash
# Restore v1.0 default behavior (14 aspects):
ketu --harmonics extended aspects --date 2026-05-07T12:00:00Z

# Discover available presets:
ketu --list-aspect-sets

# Pin to v1.0 instead of migrating:
pip install 'ketu<1.1'
```

**Migration recipe (Python API users)**

```python
# v1.0 implicit: calculate_aspects emitted all 14 harmonics
from ketu.aspects import calculate_aspects
result = calculate_aspects(jd, bodies)  # got 14 aspects

# v1.1 default: 5 majors only. Restore v1.0 behavior explicitly:
from ketu.aspects import calculate_aspects
from ketu.aspects.presets import EXTENDED
result = calculate_aspects(jd, bodies, aspects=EXTENDED)  # 14 aspects
```

### Kala / Downstream Adapter Migration (Phase 9 / ASP-04)

If you maintain a downstream adapter that consumes Ketu's aspect
output (Kala's `KetuDataAdapter`, custom scripts, ML feature
pipelines), check whether your code depends on the **count** of
aspect rows or on a specific *named* aspect (quincunx, semisextile,
etc.) that only EXTENDED includes.

In v1.0, downstream consumers received EXTENDED implicitly. In v1.1,
they receive CLASSICAL by default — silently losing 9 rows per body
pair without any error.

**Recipe** — request EXTENDED explicitly at the API boundary:

```python
# In your adapter's Ketu call site:
from ketu.aspects.presets import EXTENDED
from ketu.aspects import calculate_aspects_batch

aspects = calculate_aspects_batch(jds, bodies, aspects=EXTENDED)
```

The `core.aspects` array remains length-14 and append-only (Kala
positional indexing unaffected). Cache keys include the aspect-set
configuration hash, so explicit `aspects=EXTENDED` produces a fresh
cache entry rather than serving stale CLASSICAL data.

> **Note:** This guidance is for *downstream maintainers* of adapters
> that depend on Ketu's CLI or Python API. It does not require any
> change inside `ketu` itself. Sibling project Kala (separate
> repository) handles its own upgrade independently.

### Houses Module (Phase 10 / HOU-10)

The v1.0 placeholder `ketu.ephemeris.calculate_house_cusps` was
**removed** because it was broken: it returned an Equal House
fallback regardless of the requested `house_system` argument and
exposed an inconsistent return shape. The replacement is the new
`ketu.houses` module.

**Migration recipe (Python API)**

```python
# v1.0 (BROKEN, now removed - ImportError in v1.1):
from ketu.ephemeris import calculate_house_cusps  # ImportError

# v1.1:
from ketu import calculate_houses, house_of, HOUSES_DTYPE
houses = calculate_houses(jd, lat, lon, system='placidus')
# houses is a HOUSES_DTYPE structured array with 12 cusps + ASC/MC/ARMC/Vertex,
# vectorised over the broadcast of (jd, lat, lon).
ascendant = houses['cusps'][..., 0]      # cusp 1 = ASC
midheaven = houses['cusps'][..., 9]      # cusp 10 = MC
which_house = house_of(planet_lon=200.0, cusps=houses['cusps'][0])  # 1..12
```

**Migration recipe (CLI)**

```bash
# Single-chart house cusps (UTC ISO 8601 date, not raw JD):
ketu houses --date 2000-01-01T12:00:00Z --lat 48.85 --lon 2.35 --system placidus

# Discover available house systems and polar-fallback hints:
ketu --list-house-systems
```

Available systems in v1.1: `placidus`, `koch`, `porphyry` (the v1.0
broken `equal_fallback` placeholder is gone; `equal` and `whole_sign`
are not yet registered). High-latitude charts (|lat| > polar_circle(jd))
raise `HighLatitudeError` by default; pass `--polar-fallback porphyry`
(CLI) or `polar_fallback="porphyry"` (Python API) to fall back to
Porphyry houses instead.

### Resolved-Config stderr Header (Phase 11 / CLI-06)

The v1.1 CLI prints a resolved-config header to **stderr** (not
stdout) on every invocation. Example:

```text
# Ketu v1.1.0
# Aspect set: classical (5 aspects: Conjunction 0°, Sextile 60°, Square 90°, Trine 120°, Opposition 180°)
```

Pipelines that read stdout only (`ketu ... | parser`) are
**unaffected**. Pipelines that mix stdout and stderr (`ketu ... 2>&1`)
will see two extra leading lines and may need to filter on `^# `.
Suppress entirely with `2>/dev/null` if your pipeline cannot tolerate
stderr output.

For the houses subcommand, the second line is `# House system: <name>`
instead of `# Aspect set: ...`.

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
