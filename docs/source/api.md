# API Reference

Ketu's API is organized into subpackages. All public functions use **submodule import paths** — the top-level `ketu` namespace re-exports only the items listed in the "Top-level exports" section below.

## Top-level exports

```python
import ketu

ketu.bodies          # structured array of celestial bodies
ketu.aspects         # structured array of astrological aspects
ketu.signs           # list of zodiac sign names
ketu.HOUSES_DTYPE    # NumPy dtype for house results
ketu.HighLatitudeError  # exception for polar house failures
ketu.HOUSE_SYSTEMS   # alias for ketu.houses.SYSTEMS
ketu.calculate_houses   # alias for ketu.houses.calculate_houses
ketu.house_of           # alias for ketu.houses.house_of
ketu.__version__        # package version string
```

## Calculations (`ketu.calculations`)

Core position and analysis functions. All work with Julian Day numbers (float).

```python
from ketu.calculations import (
    long,
    lat,
    dist_au,
    body_sign,
    is_retrograde,
    positions,
    body_name,
)
```

### `long(jday, body)` / `lat(jday, body)` / `dist_au(jday, body)`

Return the ecliptic longitude (degrees), latitude (degrees), and distance (AU) of a body.

**Parameters:**
- `jday` (`float`): Julian Day number
- `body` (`int`): body ID (0 = Sun … 13 = Chiron)

**Returns:** `float`

```python
from ketu.calculations import long, lat, dist_au

jd = 2451545.0  # J2000

sun_lon = long(jd, 0)   # Sun longitude
moon_lat = lat(jd, 1)   # Moon latitude
mars_au  = dist_au(jd, 4)  # Mars distance in AU

# Chiron (body_id=13, New in v1.3)
chiron_lon = long(jd, 13)   # e.g. 251.61°
chiron_lat = lat(jd, 13)
```

### `positions(jday, l_bodies=bodies)`

Return an array of longitudes for all bodies (or a subset).

**Returns:** `numpy.ndarray` of float64, shape `(N,)`

```python
from ketu.calculations import positions
import ketu

lons = positions(jd, ketu.bodies)
```

### `body_sign(b_long)`

Determine the zodiac sign and degree breakdown for a longitude.

**Parameters:** `b_long` (`float`): ecliptic longitude in degrees

**Returns:** `numpy.ndarray` of int32, fields `[sign_index, degrees, minutes, seconds]`

```python
from ketu.calculations import long, body_sign
import ketu

moon_lon  = long(jd, 1)
sign_data = body_sign(moon_lon)
print(f"Moon: {ketu.signs[sign_data[0]]} {sign_data[1]}° {sign_data[2]}'")
```

### `is_retrograde(jday, body)`

Return `True` if the body has negative longitudinal velocity (retrograde motion).

```python
from ketu.calculations import is_retrograde

if is_retrograde(jd, 2):   # Mercury
    print("Mercury retrograde")
```

### `is_ascending(jday, body)`

Return `True` if the body's **ecliptic latitude** (β) is increasing (positive β-velocity). This is the β-trajectory helper, unchanged since v1.0. It is **distinct** from `is_ascending_declination` — see [Equatorial Declination (New in v1.5)](#equatorial-declination-new-in-v1-5) for the β-vs-δ pitfall.

```python
from ketu.calculations import is_ascending

if is_ascending(jd, 1):   # Moon β rising
    print("Moon ascending in ecliptic latitude")
```

### `declination(jdate, body)` — New in v1.5

Return the equatorial declination δ of a body in degrees (north positive, south negative), range [−90, +90].

Computed via the ecliptic-to-equatorial chain: `spherical_to_rectangular(λ, β, 1) → ecliptic_to_equatorial(ε) → rectangular_to_spherical` — numerically equivalent to Meeus eq. 13.4. Scalar input uses the cached `long`/`lat` functions. Array input is vectorized loop-free via `calc_planet_position_batch`.

**Parameters:**
- `jdate` (`float` or `numpy.ndarray`): Julian Day number (scalar or 1-D array)
- `body` (`int`): body ID (0 = Sun … 13 = Chiron)

**Returns:** `float` (scalar) or `numpy.ndarray` (array input), same shape as *jdate*

```python
from ketu.calculations import declination
import numpy as np

jd = 2451545.0  # J2000

# Scalar
moon_decl = declination(jd, 1)   # e.g. −23.03°

# Vectorized
jds = np.array([2451545.0, 2451600.0, 2451650.0])
moon_decls = declination(jds, 1)  # shape (3,)
```

### `declination_velocity(jdate, body)` — New in v1.5

Return the rate of change of equatorial declination dδ/dt in degrees/day (positive = northward, negative = southward).

Computed via forward finite difference with step 0.01 day, mirroring the package-wide FD idiom used for `lat_velocity`.

**Parameters:**
- `jdate` (`float`): Julian Day number
- `body` (`int`): body ID (0 = Sun … 13 = Chiron)

**Returns:** `float`

```python
from ketu.calculations import declination_velocity

jd = 2451545.0

moon_vel = declination_velocity(jd, 1)   # e.g. +4.23 °/day
```

### `is_ascending_declination(jdate, body)` — New in v1.5

Return `True` when dδ/dt > 0 — the Moon (or any body) is **montante** (moving northward in declination).

**This is the biodynamic montant/descendant helper.** It is **not the same as `is_ascending`**, which tracks the ecliptic latitude β. See [Equatorial Declination (New in v1.5)](#equatorial-declination-new-in-v1-5) for the explicit β-vs-δ distinction.

**Parameters:**
- `jdate` (`float`): Julian Day number
- `body` (`int`): body ID (0 = Sun … 13 = Chiron)

**Returns:** `bool`

```python
from ketu.calculations import is_ascending_declination

jd = 2451545.0

if is_ascending_declination(jd, 1):   # Moon montante
    print("Moon montante (northward in declination)")
```

### `is_out_of_bounds(jdate, body)` — New in v1.5

Return `True` when |δ| > ε(jd) — the body's declination exceeds the instantaneous true obliquity of the ecliptic (out-of-bounds / hors limites).

The Moon can go OOB during major lunar standstill periods (~18.6-year nodal cycle; most recently around 2024–2025, with |δ| up to ~28.7°).

**Parameters:**
- `jdate` (`float`): Julian Day number
- `body` (`int`): body ID (0 = Sun … 13 = Chiron)

**Returns:** `bool`

```python
from ketu.calculations import is_out_of_bounds

jd = 2451545.0

if is_out_of_bounds(jd, 1):   # Moon OOB?
    print("Moon is out of bounds")
```

### `body_name(body)`

Return the string name for a body ID.

```python
from ketu.calculations import body_name

print(body_name(0))   # "Sun"
print(body_name(13))  # "Chiron"
```

---

## Time (`ketu.ephemeris.time`)

```python
from ketu.ephemeris.time import utc_to_julian, local_to_utc
```

### `utc_to_julian(dtime)`

Convert a UTC datetime to Julian Day number.

**Parameters:** `dtime` (`datetime`): UTC datetime (timezone-aware or naive UTC)

**Returns:** `float`

```python
from ketu.ephemeris.time import utc_to_julian
from datetime import datetime

jd = utc_to_julian(datetime(2000, 1, 1, 12, 0))
# jd == 2451545.0  (J2000.0)
```

### `local_to_utc(dtime, zoneinfo=None)`

Convert a local datetime to UTC.

**Parameters:**
- `dtime` (`datetime`): local datetime with or without tzinfo
- `zoneinfo` (`ZoneInfo`, optional): timezone if not embedded in dtime

**Returns:** `datetime` in UTC

```python
from ketu.ephemeris.time import local_to_utc, utc_to_julian
from datetime import datetime
from zoneinfo import ZoneInfo

paris = ZoneInfo("Europe/Paris")
dt_local = datetime(2020, 12, 21, 19, 20, tzinfo=paris)
dt_utc = local_to_utc(dt_local)
jd = utc_to_julian(dt_utc)
```

---

## Aspects (`ketu.aspects`)

Configurable aspect detection. New in v1.1: preset aspect sets.

```python
from ketu.aspects import (
    get_aspect,
    calculate_aspects,
    get_orb,
    CLASSICAL,
    TRADITIONAL,
    EXTENDED,
    AspectSetSpec,
    resolve_aspect_set,
)
```

### Preset Aspect Sets

| Name | Aspects included | Notes |
|------|------------------|-------|
| `TRADITIONAL` | Conjunction, Semi-sextile, Sextile, Square, Trine, Quincunx, Opposition (7 aspects) | **Library default** (v1.3+) |
| `CLASSICAL` | Conjunction, Sextile, Square, Trine, Opposition (5 aspects) | v1.2 and earlier default |
| `EXTENDED` | All 14 aspects | Includes full-circle minors (H5/H9/H10) |

All presets are `numpy.ndarray` boolean masks over the 14-aspect table.

`AspectSetSpec = Union[str, list, numpy.ndarray, None]` — any of these can be passed as the `aspects` argument to `calculate_aspects`.

### `aspects_for_harmonics(harmonics)`

Compose a custom aspect set from a list of harmonics. Returns a frozen length-14
`numpy.bool_` mask that can be used as `aspects=` argument to any Ketu function.

**Parameters:**
- `harmonics` (`Sequence[int]`): list of harmonic integers; valid values: `{1, 2, 3, 5, 6, 9, 10}`

**Returns:** frozen `numpy.ndarray` of `numpy.bool_`, shape `(14,)`

**Raises:** `ValueError` if any harmonic is not in the valid set or is not an integer.

```python
from ketu.aspects import aspects_for_harmonics

# The 7 half-circle aspects (= TRADITIONAL, the library default):
mask = aspects_for_harmonics([1, 2, 3, 6])

# Full-circle minor aspects (H5/H9/H10):
minors = aspects_for_harmonics([5, 9, 10])

# All 14 aspects (= EXTENDED):
all14 = aspects_for_harmonics([1, 2, 3, 5, 6, 9, 10])

# Just Sextile + Trine (harmonic 3, half-circle convention):
h3 = aspects_for_harmonics([3])

# Pass directly to calculate_aspects:
from ketu.aspects import calculate_aspects
result = calculate_aspects(jd, aspects=aspects_for_harmonics([1, 2, 3, 6]))
```

### `generate_harmonic_aspects(h)`

Generate aspect specs on the fly for **any** integer harmonic `h` — not just the named preset harmonics `{1, 2, 3, 5, 6, 9, 10}`. For each `k = 1 … h//2`, the function computes `angle = fold_to_0_180(k · 360 / h)` and `coef = k / h`, using the full-circle 360° convention folded to 0–180°.

**Parameters:**

- `h` (`int`): the harmonic, `2 ≤ h ≤ 64`. `h = 1` is rejected (degenerate, 0 rows); `h > 64` is rejected (impractically small orbs).

**Returns:** structured array with the **same dtype as `core.aspects`** (drop-in), shape `(h // 2,)`. Names are auto-generated (`b'H7-1'`, `b'H7-2'`, …). Pass the result as the `dynamic_specs=` argument to `calculate_aspects`, `find_aspects_between_dates`, and `calculate_synastry`.

**Raises:** `ValueError` if `h` is not an `int` or is outside `[2, 64]`.

```python
from ketu.aspects import generate_harmonic_aspects

# Harmonic 7: 3 unique folded angles (septile family)
specs = generate_harmonic_aspects(7)
print(len(specs))          # 3
print(specs['name'])       # [b'H7-1', b'H7-2', b'H7-3']
print(specs['angle'])      # [51.43, 102.86, 154.29]
print(specs['coef'])       # [0.1429, 0.2857, 0.4286]

# Pass to calculate_aspects via dynamic_specs:
from ketu.aspects import calculate_aspects
result = calculate_aspects(jd, dynamic_specs=generate_harmonic_aspects(7))
```

> **Note on orbs:** Dynamic harmonic orbs use `coef = k / h` (full-circle convention). For high harmonics this yields orbs roughly half the size of the equivalent half-circle aspect — accepted behaviour; the two conventions coexist without unification (see the v1.4 release notes).
>
> **Naming contract (v1.5+):** The emitted `name` bytes are **always** `b'H{h}-{k}'`
> (S16 dtype), for k = 1..h//2 in ascending order. This `(h, k) → (name, angle, coef)`
> mapping is **frozen** across v1.5+ minor and patch releases — no traditional-name
> substitution is ever performed by the generator. See
> {ref}`synthetic-harmonic-naming` in Concepts for the full GENERATOR vs. DETECTION
> channel explanation and the traditional-name reference table.

### `core.aspects` columns: `harmonic` and `symbol`

`core.aspects` is a 5-field structured array `(name, angle, coef, harmonic, symbol)`.
New in v1.3: the `harmonic` and `symbol` columns.

- **`harmonic` (`int32`):** the harmonic base for each aspect. Values: `[1, 6, 10, 9, 3, 5, 9, 2, 10, 3, 5, 6, 9, 1]` for aspects 0–13 in the canonical table order. `aspects_for_harmonics` uses this column internally (data-driven, no hardcoded indices).
- **`symbol` (`U4`):** Unicode glyph for the 7 half-circle aspects (☌ ⚺ ⚹ □ △ ⚻ ☍); blank (`""`) for the 7 full-circle minor aspects.
- **`coef` (`float32`):** orb coefficient. Conceptually referred to as `coefficient` in API documentation; the field name in the dtype is `coef` and was **not renamed** in v1.3.

```python
import ketu.core

# Access new columns:
harmonics = ketu.core.aspects["harmonic"]    # array([1, 6, 10, 9, 3, 5, 9, 2, 10, 3, 5, 6, 9, 1])
symbols   = ketu.core.aspects["symbol"]     # ['☌', '⚺', '', '', '⚹', '', '', '□', '', '△', '', '⚻', '', '☍']
coefs     = ketu.core.aspects["coef"]       # orb coefficients (field name: 'coef', not 'coefficient')
```

### `get_aspect(jday, body1, body2)`

Return the aspect between two bodies, or `None` if no in-orb aspect exists.

**Returns:** `tuple[int, int, int, float]` → `(body1, body2, aspect_id, orb)` or `None`

```python
from ketu.aspects import get_aspect

result = get_aspect(jd, 0, 1)   # Sun–Moon
if result:
    b1, b2, asp_id, orb = result
    print(f"aspect_id={asp_id}, orb={orb:.2f}°")
```

### `calculate_aspects(jdate, l_bodies=bodies, aspects=None)`

Compute all in-orb aspects for the given date.

**Parameters:**
- `jdate` (`float`): Julian Day
- `l_bodies`: body subset (default: all bodies)
- `aspects` (`AspectSetSpec`, optional): filter; `None` → TRADITIONAL (7 half-circle, v1.3+ default); `"classical"` → CLASSICAL (5); `"extended"` → EXTENDED (14); etc.

**Returns:** structured array with fields `(body1, body2, i_asp, orb)`

```python
from ketu.aspects import calculate_aspects, CLASSICAL

# Only classical aspects
classical = calculate_aspects(jd, aspects=CLASSICAL)

for row in classical:
    print(row["body1"], row["body2"], row["orb"])
```

### `get_orb(body1, body2, asp)`

Return the maximum allowed orb in degrees for an aspect pair.

### `find_aspect_timing(jdate, body1, body2, aspect_value, orb=None, dyn_coef=None)` — Updated in v1.5

Find the window (begin, exact, end) for an aspect between two bodies near a reference date.

**Parameters:**

- `jdate` (`float`): reference Julian Day
- `body1`, `body2` (`int`): body IDs (0 = Sun … 13 = Chiron)
- `aspect_value` (`float`): aspect angle in degrees
- `orb` (`float`, optional): explicit orb in degrees — escape hatch, skips all internal resolution. **When both `orb` and `dyn_coef` are given, explicit `orb` wins silently** (no error is raised).
- `dyn_coef` (`float`, optional): dynamic-orb coefficient — **new in v1.5 (HARM-04)**. When `orb` is `None` and `dyn_coef` is not `None`, the orb is derived as `(bodies['orb'][body1] + bodies['orb'][body2]) / 2 * dyn_coef`, mirroring the formula used by `calculate_aspects`. Pass the `coef` field from a `generate_harmonic_aspects` row directly — no pre-computation required.

**Orb resolution — three branches, checked in this order:**

1. `orb is not None` → explicit orb wins immediately (even if `dyn_coef` is also given).
2. `dyn_coef is not None` → orb derived as `(orb_b1 + orb_b2) / 2 * dyn_coef`.
3. Both `None` → static table lookup via `get_orb(body1, body2, asp_idx)`. Raises `ValueError` if `aspect_value` is not in the table.

**Returns:** `tuple[float, float, float]` — `(begin_jd, exact_jd, end_jd)`

**Raises:** `ValueError` when both `orb` and `dyn_coef` are `None` and `aspect_value` is not in the static aspect table.

```python
from ketu.aspects.calculator import find_aspect_timing
from ketu.aspects import generate_harmonic_aspects

jd = 2451545.0  # J2000

# Static path — trine (120°) found in the table, orb derived automatically:
begin, exact, end = find_aspect_timing(jd, 0, 1, 120.0)

# Dynamic path — H7-1 Sun-Moon timing via dyn_coef (no pre-computation):
begin, exact, end = find_aspect_timing(jd, 0, 1, 51.4286, dyn_coef=1/7)

# Explicit orb escape hatch (unchanged behaviour):
specs = generate_harmonic_aspects(7)
explicit_orb = (specs["coef"][0]) * 3.0   # custom orb
begin, exact, end = find_aspect_timing(jd, 0, 1, 51.4286, orb=explicit_orb)
```

---

## Houses (`ketu.houses`)

House system calculations. New in v1.1/v1.2.

```python
from ketu.houses import (
    calculate_houses,
    house_of,
    HOUSES_DTYPE,
    SYSTEMS,
    HighLatitudeError,
    register,
)
```

### `SYSTEMS`

Dictionary of supported house systems:

```python
SYSTEMS = {
    "placidus", "koch", "porphyry",
    "whole_sign", "equal", "regiomontanus"
}
```

### `HOUSES_DTYPE`

NumPy dtype for house result arrays:

```
jd         float64   Julian Day
lat        float64   geographic latitude (°)
lon        float64   geographic longitude (°)
system     U16       house system name
cusps      float64[12]  twelve house cusp longitudes
asc        float64   Ascendant longitude (°)
mc         float64   Midheaven longitude (°)
armc       float64   ARMC (right ascension of MC, °)
vertex     float64   Vertex longitude (°)
```

### `calculate_houses(jd, lat, lon, system="placidus", polar_fallback="raise")`

Compute house cusps and angles for a given moment and location.

**Parameters:**
- `jd` (`float`): Julian Day
- `lat` (`float`): geographic latitude in degrees
- `lon` (`float`): geographic longitude in degrees
- `system` (`str`): one of `SYSTEMS` keys
- `polar_fallback` (`str`): `"raise"` (default) or a fallback system name

**Returns:** scalar `numpy.ndarray` with `HOUSES_DTYPE` fields

```python
from ketu.houses import calculate_houses

jd = 2451545.0
lat, lon = 48.8566, 2.3522   # Paris

h = calculate_houses(jd, lat, lon, system="placidus")
print(f"ASC: {h['asc']:.2f}°")
print(f"MC:  {h['mc']:.2f}°")
print(f"House 1 cusp: {h['cusps'][0]:.2f}°")
```

### `house_of(planet_lon, cusps)`

Return the house number (1–12) for a given longitude.

**Parameters:**
- `planet_lon` (`float` or array): ecliptic longitude
- `cusps` (`float[12]`): house cusp array from `HOUSES_DTYPE`

**Returns:** `int` or array of int

```python
from ketu.houses import calculate_houses, house_of
from ketu.calculations import long

h = calculate_houses(jd, 48.8566, 2.3522)
sun_lon = long(jd, 0)
print(f"Sun in house {house_of(sun_lon, h['cusps'])}")
```

### `HighLatitudeError`

Raised by Placidus/Koch when house cusps cannot be computed above the polar circle. Catch it or use `polar_fallback`.

### `register`

Decorator/function to add a custom house system to the registry. See [Houses](houses.md) for advanced usage.

---

## Charts (`ketu.charts`)

Full natal chart computation. New in v1.2.

```python
from ketu.charts import compute_chart, is_day_chart, CHART_DTYPE
```

### `CHART_DTYPE`

NumPy dtype for a complete natal chart:

```
jd              float64      Julian Day
lat             float64      geographic latitude
lon             float64      geographic longitude
system          U16          house system
body_lons       float64[14]  ecliptic longitudes (index 13 = Chiron)
body_lats       float64[14]  ecliptic latitudes
body_speeds     float64[14]  longitudinal velocities (°/day)
cusps           float64[12]  house cusp longitudes
asc             float64      Ascendant
mc              float64      Midheaven
armc            float64      ARMC
vertex          float64      Vertex
aspect_matrix   float64[14,14]  aspect type for each pair (-1 = none)
aspect_orbs     float64[14,14]  orb in degrees for each pair
```

### `compute_chart(jd, lat, lon, system="placidus", aspects=None, polar_fallback="raise")`

Build a complete natal chart as a single structured array.

**Parameters:**
- `jd` (`float`): Julian Day
- `lat`, `lon` (`float`): geographic coordinates
- `system` (`str`): house system
- `aspects` (`AspectSetSpec`): aspect filter (default: TRADITIONAL — the 7 half-circle aspects, v1.3+)
- `polar_fallback` (`str`): high-latitude fallback

**Returns:** scalar `numpy.ndarray` with `CHART_DTYPE` fields

```python
from ketu.charts import compute_chart

jd = 2451545.0
lat, lon = 48.8566, 2.3522   # Paris

chart = compute_chart(jd, lat, lon, system="placidus")

print(f"ASC:    {chart['asc']:.2f}°")
print(f"Sun:    {chart['body_lons'][0]:.2f}°")
print(f"Moon:   {chart['body_lons'][1]:.2f}°")
print(f"Chiron: {chart['body_lons'][13]:.2f}°")   # body index 13 = Chiron
```

### `is_day_chart(jd, lat, lon)`

Return `True` if the Sun is above the horizon at the given moment and location (used for sect-aware Arabic Parts).

```python
from ketu.charts import is_day_chart

day = is_day_chart(2451545.0, 48.8566, 2.3522)
print("Day chart" if day else "Night chart")
```

See also: [Relational charts](relational_charts.md)

---

## Synastry (`ketu.synastry`)

Inter-chart aspect analysis. New in v1.2.

```python
from ketu.synastry import calculate_synastry, SYNASTRY_DTYPE
```

### `SYNASTRY_DTYPE`

```
body_a       int32     body index in chart A
body_b       int32     body index in chart B
lon_a        float64   longitude in chart A
lon_b        float64   longitude in chart B
aspect_type  int32     aspect index (-1 = none)
orb          float64   orb in degrees
applying     bool      True if applying
orb_limit    float64   maximum allowed orb
```

### `calculate_synastry(chart_a, chart_b, aspects="classical", orbs="synastry", mode="filtered")`

Compute all inter-chart aspects between two `CHART_DTYPE` arrays.

**Parameters:**
- `chart_a`, `chart_b`: scalar `CHART_DTYPE` arrays from `compute_chart`
- `aspects` (`AspectSetSpec`): aspect filter
- `orbs` (`str`): orb set (`"synastry"` applies reduced orbs)
- `mode` (`str`): `"filtered"` returns only in-orb pairs; `"full"` returns all pairs

**Returns:** structured array with `SYNASTRY_DTYPE` fields

```python
from ketu.charts import compute_chart
from ketu.synastry import calculate_synastry

chart_a = compute_chart(2451545.0, 48.8566, 2.3522)   # Paris J2000
chart_b = compute_chart(2451910.0, 51.5074, -0.1278)  # London ~1 year later

syn = calculate_synastry(chart_a, chart_b)

for row in syn:
    print(f"A body {row['body_a']} — B body {row['body_b']}: orb {row['orb']:.2f}°")
```

See also: [Relational charts](relational_charts.md)

---

## Composite (`ketu.composite`)

Midpoint composite chart computation. New in v1.2.

```python
from ketu.composite import calculate_composite, circular_midpoint
```

### `circular_midpoint(lon_a, lon_b)`

Compute the circular (shortest-arc) midpoint between two longitudes.

**Parameters:** `lon_a`, `lon_b` (`float` or array): ecliptic longitudes in degrees

**Returns:** `float` or array

```python
from ketu.composite import circular_midpoint

mid = circular_midpoint(10.0, 350.0)   # → 0.0° (shortest arc across 0°)
```

### `calculate_composite(chart_a, chart_b, system="placidus")`

Build a composite (midpoint) chart from two natal `CHART_DTYPE` arrays. The result is a new `CHART_DTYPE` array where each body position is the circular midpoint of the corresponding bodies in chart A and B.

**Returns:** scalar `numpy.ndarray` with `CHART_DTYPE` fields

```python
from ketu.charts import compute_chart
from ketu.composite import calculate_composite

chart_a = compute_chart(2451545.0, 48.8566, 2.3522)
chart_b = compute_chart(2451910.0, 48.8566, 2.3522)

composite = calculate_composite(chart_a, chart_b)
print(f"Composite Sun: {composite['body_lons'][0]:.2f}°")
```

See also: [Relational charts](relational_charts.md)

---

## Returns (`ketu.returns`)

Solar and lunar return charts. New in v1.2.

```python
from ketu.returns import solar_return, lunar_return
```

**Key asymmetry:** `solar_return` takes `target_year` as an `int`; `lunar_return` takes `target_jd` as a `float`.

### `solar_return(natal_jd, natal_lat, natal_lon, target_year, return_lat=None, return_lon=None, system="placidus")`

Find the exact Julian Day when the Sun returns to its natal longitude during `target_year`, then build the full chart at that moment.

**Parameters:**
- `natal_jd` (`float`): Julian Day of birth
- `natal_lat`, `natal_lon` (`float`): birth geographic coordinates
- `target_year` (`int`): Gregorian year for the return
- `return_lat`, `return_lon` (`float`, optional): relocated return location; `None` → natal location
- `system` (`str`): house system

**Returns:** scalar `CHART_DTYPE` array for the return chart

```python
from ketu.returns import solar_return

natal_jd = 2451545.0
sr = solar_return(natal_jd, 48.8566, 2.3522, target_year=2026)
print(f"Solar Return ASC: {sr['asc']:.2f}°")
```

### `lunar_return(natal_jd, natal_lat, natal_lon, target_jd, return_lat=None, return_lon=None, system="placidus")`

Find the next lunar return on or after `target_jd` (Moon returns to natal longitude), then build the chart.

**Parameters:**
- `natal_jd` (`float`): Julian Day of birth
- `natal_lat`, `natal_lon` (`float`): birth geographic coordinates
- `target_jd` (`float`): search starts from this Julian Day
- `return_lat`, `return_lon` (`float`, optional): relocated location
- `system` (`str`): house system

**Returns:** scalar `CHART_DTYPE` array

```python
from ketu.returns import lunar_return
from ketu.ephemeris.time import utc_to_julian
from datetime import datetime

natal_jd = 2451545.0
search_from = utc_to_julian(datetime(2026, 1, 1))

lr = lunar_return(natal_jd, 48.8566, 2.3522, target_jd=search_from)
print(f"Lunar Return Moon: {lr['body_lons'][1]:.2f}°")
```

See also: [Predictive charts](predictive_charts.md)

---

## Arabic Parts (`ketu.parts`)

Hermetic Lots / Arabic Parts. New in v1.2.

```python
from ketu.parts import (
    PARTS,
    calculate_part,
    calculate_all_parts,
    register,
    get_part,
    PartSpec,
)
```

### `PARTS`

Registry dictionary mapping part names to `PartSpec` objects. Built-in parts:

| Name | Sect-aware | Formula (day) |
|------|-----------|--------------|
| `"fortune"` | Yes | ASC + Moon − Sun |
| `"spirit"` | Yes | ASC + Sun − Moon |
| `"marriage"` | No (fixed) | ASC + Venus − Saturn |

`PartSpec` fields: `name`, `day_formula`, `night_formula`, `description`.

Formula signature: `(asc_lon, sun_lon, moon_lon, venus_lon) -> float`

### `calculate_part(part_name, chart)`

Compute the longitude of a named Arabic Part for a chart.

**Parameters:**
- `part_name` (`str`): key in `PARTS` registry
- `chart`: scalar `CHART_DTYPE` array (must include `asc`, `body_lons`)

**Returns:** `float` — ecliptic longitude of the Part (degrees)

Fortune and Spirit automatically invert their formulas for night charts (when Sun is below the horizon).

```python
from ketu.charts import compute_chart
from ketu.parts import calculate_part

jd = 2451545.0
chart = compute_chart(jd, 48.8566, 2.3522)

fortune = calculate_part("fortune", chart)
spirit  = calculate_part("spirit", chart)
marriage = calculate_part("marriage", chart)

print(f"Part of Fortune: {fortune:.2f}°")
print(f"Part of Spirit:  {spirit:.2f}°")
print(f"Part of Marriage: {marriage:.2f}°")
```

### `calculate_all_parts(chart, parts=None)`

Compute all registered parts (or a subset) at once.

**Parameters:**
- `chart`: scalar `CHART_DTYPE`
- `parts` (`list[str]`, optional): subset of `PARTS` keys; `None` → all

**Returns:** `dict[str, float]`

```python
from ketu.parts import calculate_all_parts

all_lots = calculate_all_parts(chart)
for name, lon in all_lots.items():
    print(f"{name}: {lon:.2f}°")
```

### `register(name, *, day_formula, night_formula, description="")`

Add a custom Arabic Part to the registry.

```python
from ketu.parts import register

def my_formula(asc, sun, moon, venus):
    return (asc + moon - venus) % 360

register("my_part", day_formula=my_formula, night_formula=my_formula, description="Custom part")
```

### `get_part(name)`

Retrieve a `PartSpec` from the registry.

See also: [Arabic Parts](arabic_parts.md)

---

## Display / CLI (`ketu.display`, `ketu.cli`)

```python
from ketu.display import print_positions, print_aspects
from ketu.cli import main
```

### `print_positions(jday)`

Print a formatted table of body positions for the given Julian Day.

### `print_aspects(jday)`

Print a formatted table of current in-orb aspects.

### `main()`

Entry point for the interactive CLI (`ketu` command).

### `parse_harmonics_spec(value)` and `HarmonicsSelection` — Updated in v1.5

`parse_harmonics_spec` is the argparse `type=` validator wired to the `--harmonics`
CLI argument. It returns a `HarmonicsSelection` NamedTuple `(mask, dynamic_specs)`.

**`HarmonicsSelection` fields:**

- `mask` (`np.ndarray[bool_]`, shape `(14,)`): length-14 boolean mask into `ketu.core.aspects`.
  All-False for `h<N>` tokens (only dynamic specs are used); populated for preset / index-list inputs.
- `dynamic_specs` (`DynamicAspectSpec | None`): structured array from
  `generate_harmonic_aspects` for `h<N>` tokens; `None` for preset and comma-separated-index inputs.

**Accepted spec forms:**

| Spec form | Returns | Notes |
|---|---|---|
| `"classical"` / `"traditional"` / `"extended"` / `"all"` | `HarmonicsSelection(mask=<preset>, dynamic_specs=None)` | `"all"` aliases `"extended"` |
| `"0,4,7,9,13"` | `HarmonicsSelection(mask=<computed>, dynamic_specs=None)` | Comma-separated indices into `core.aspects` |
| `"h7"` / `"H7"` | `HarmonicsSelection(mask=zeros(14), dynamic_specs=<array>)` | **New in v1.5** — arbitrary harmonic token `h<N>` |
| `"h7,h11"` / `"traditional,h7"` | **Rejected** (HARMF-01, deferred) | Multi-harmonic mixing not yet supported |

The `h<N>` form (case-insensitive, `N` in `[2, 64]`) selects only the `H{N}-{k}` dynamic
aspects via the `dynamic_specs=` channel. Preset / index-list inputs yield `dynamic_specs=None`.
See {ref}`harmonics-h7-cli-new-in-v1-5` in Concepts for the CLI usage, Tight-grammar
boundary, and a worked example.

---

(equatorial-declination-new-in-v1-5)=
## Equatorial Declination (`ketu.calculations`) — New in v1.5

Equatorial declination (δ) measures how far north or south of the celestial equator a body lies. It is **distinct from ecliptic latitude** (β):

| Quantity | Symbol | Reference plane | Ketu function |
|----------|--------|-----------------|---------------|
| Ecliptic latitude | β | Ecliptic plane | `lat`, `is_ascending` |
| Equatorial declination | δ | Celestial equator | `declination`, `is_ascending_declination` |

**β-vs-δ pitfall — "ascending Moon" is ambiguous:** `is_ascending` tracks the β-trajectory (ecliptic latitude rising); `is_ascending_declination` tracks the δ-trajectory (biodynamic montant/descendant). These two can disagree for the same body on the same date. Example: at 2025-03-07 (JD=2460742.0, Moon near a major standstill peak at δ≈+28.66°), `is_ascending_declination=True` (δ rising at +0.30°/day) while `is_ascending=False` (β descending).

**The Moon's δ cycle** completes in ≈27.21 days (draconic/nodal month). Montante = northward (dδ/dt > 0); descendante = southward (dδ/dt < 0). This is the cycle used in biodynamic agriculture (Loc's aspect-centric framing).

**Out-of-bounds (OOB):** the Moon's δ can exceed the obliquity ε during the **major lunar standstill** (~18.6-year nodal cycle). The threshold uses the instantaneous true obliquity ε(jd), not mean obliquity. During 2024–2025, the Moon reaches |δ| ≈ 28.7°.

```python
from ketu.calculations import (
    declination,
    declination_velocity,
    is_ascending_declination,
    is_out_of_bounds,
)

jd = 2451545.0  # J2000

# δ in degrees (north positive, south negative)
moon_decl = declination(jd, 1)
print(f"Moon δ: {moon_decl:.4f}°")

# dδ/dt in °/day
moon_vel = declination_velocity(jd, 1)
print(f"Moon dδ/dt: {moon_vel:.4f}°/day")

# Biodynamic montant/descendant
if is_ascending_declination(jd, 1):
    print("Moon montante (northward)")
else:
    print("Moon descendante (southward)")

# Out-of-bounds check
if is_out_of_bounds(jd, 1):
    print("Moon is out of bounds (|δ| > ε)")
```

---

## Declination Aspects (`ketu.declination`) — New in v1.6

Additive subpackage that detects **parallels** and **contra-parallels** on the
equatorial declination axis. It consumes `chart["body_decl"]` (the `(14,)` signed-δ
field shipped in v1.5); `CHART_DTYPE` is **unchanged**. These names are reachable
**only** via `ketu.declination.*` — they are NOT re-exported from top-level `ketu`
(`ketu.__all__` is unchanged, additive-only).

```python
from ketu.declination import (
    find_declination_aspects,
    declination_aspect_masks,
    DeclinationAspectMasks,
    DECLA_ASPECT_DTYPE,
    DECLA_COEF,
    MIN_DECL_ORB,
)
```

See the [Declination Aspects](concepts.md#declination-aspects-new-in-v1-6) concepts
page for the signed-δ definitions, the body-derived orb derivation, and the
biodynamic framing.

### `find_declination_aspects(body_decl)`

Scalar / single-chart detector.

- **Parameters:** `body_decl` (`ndarray`, shape `(14,)`) — signed declination δ in
  degrees, i.e. `chart["body_decl"]`.
- **Returns:** `ndarray[DECLA_ASPECT_DTYPE]` — upper-triangle pairs only
  (`body1 < body2`), no duplicates, sorted by `(body1, body2)`. Returns
  `np.empty(0, dtype=DECLA_ASPECT_DTYPE)` when nothing is detected — **never**
  `None`, never a tuple.

```python
import numpy as np
from ketu.declination import find_declination_aspects

decl = np.zeros(14)
decl[0] = 20.0   # Sun  δ = +20.0°
decl[1] = 20.5   # Moon δ = +20.5°  → same hemisphere, gap 0.5° ≤ 1.0° orb

aspects = find_declination_aspects(decl)
print(aspects)   # [(0, 1, 'P', 0.5, 1.0)] — Sun/Moon parallel
```

### `declination_aspect_masks(body_decl)`

Vectorized batch path. Accepts `(S, 14)` or `(14,)` (promoted via `np.atleast_2d`)
and returns a `DeclinationAspectMasks` NamedTuple. Pure NumPy broadcasting — no
Python body loop.

- **Parameters:** `body_decl` (`ndarray`, shape `(S, 14)` or `(14,)`).
- **Returns:** `DeclinationAspectMasks`.

### `DeclinationAspectMasks`

NamedTuple with six fields, in order:

| Field | Shape | Meaning |
|-------|-------|---------|
| `parallel` | `(S, 91)` | boolean parallel mask per chart per pair |
| `contra` | `(S, 91)` | boolean contra-parallel mask per chart per pair |
| `gap` | `(S, 91)` | `\|δ₁−δ₂\|` (parallel) / `\|δ₁+δ₂\|` (contra) per chart per pair |
| `idx_i` | `(91,)` | first body index of each pair |
| `idx_j` | `(91,)` | second body index of each pair |
| `orb_pairs` | `(91,)` | orb limit for each pair |

`91` is the upper-triangle pair count for 14 bodies (`14 × 13 / 2`).

### `DECLA_ASPECT_DTYPE`

The frozen 5-field row contract returned by `find_declination_aspects`:

| Field | Type | Meaning |
|-------|------|---------|
| `body1` | `i1` | first body index (`body1 < body2`) |
| `body2` | `i1` | second body index |
| `kind` | `U2` | `"P"` (parallel) or `"CP"` (contra-parallel) |
| `gap` | `f8` | `\|δ₁−δ₂\|` for P, `\|δ₁+δ₂\|` for CP |
| `orb` | `f8` | the orb limit used for that pair |

`body1` / `body2` are `i1` (signed 1-byte) in the live dtype.

### `DECLA_COEF` and `MIN_DECL_ORB`

- `DECLA_COEF = 1/12` (≈ 0.0833) — orb scaling on the declination axis.
- `MIN_DECL_ORB = 0.5` — floor (degrees) so zero-orb bodies stay detectable.

The per-pair orb is `max((orb_b1 + orb_b2) / 2 × DECLA_COEF, MIN_DECL_ORB)` →
Sun/Moon `1.0°`, Rahu/Lilith `0.5°` (floor). See the
[concepts page](concepts.md#declination-aspects-new-in-v1-6) for the full derivation.

---

## Chiron (body_id=13) — New in v1.3

Chiron is the 14th body added in v1.3. There is no separate Chiron module in the public API — it is accessed through the standard calculation functions using `body_id=13`.

**Key facts:**

- `ketu.bodies["name"][13] == b"Chiron"`
- Valid date range: 1900–2100 (expanded in v1.4; 2283 Chebyshev segments embedded in `ketu/data/chiron_coeffs.npz`). Out-of-range input is silently clamped to the nearest segment boundary.
- Accuracy: max error 0.001214° (sub-arcminute) over the 1900–2100 range
- `CHART_DTYPE` body arrays are 14-wide; index 13 always refers to Chiron

**Breaking change (v1.2 → v1.3):** The `CHART_DTYPE` body axis expanded from 13 to 14 bodies (D-08). Code that accessed bodies by fixed count or hardcoded index 12 as the last body must be updated. See [Migration](migration.md) for details.

```python
from ketu.calculations import long, lat

jd = 2451545.0   # J2000.0

chiron_lon = long(jd, 13)   # e.g. 251.61°
chiron_lat = lat(jd, 13)

print(f"Chiron at J2000: {chiron_lon:.2f}° ecliptic longitude")
```

```python
from ketu.charts import compute_chart

chart = compute_chart(jd, 48.8566, 2.3522)
chiron_lon = chart["body_lons"][13]   # body axis index 13
```

See also: [Chiron](chiron.md)
