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

| Name | Aspects included |
|------|-----------------|
| `CLASSICAL` | Conjunction, Sextile, Square, Trine, Opposition (5 aspects) |
| `TRADITIONAL` | CLASSICAL + Semi-sextile, Quincunx (7 aspects) |
| `EXTENDED` | All 14 aspects (default) |

All presets are `numpy.ndarray` boolean masks over the 14-aspect table.

`AspectSetSpec = Union[str, list, numpy.ndarray, None]` — any of these can be passed as the `aspects` argument to `calculate_aspects`.

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
- `aspects` (`AspectSetSpec`, optional): filter; `None` → EXTENDED; `"classical"` → CLASSICAL etc.

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
- `aspects` (`AspectSetSpec`): aspect filter (default: EXTENDED)
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

### `register(name, day_formula, night_formula, description)`

Add a custom Arabic Part to the registry.

```python
from ketu.parts import register

def my_formula(asc, sun, moon, venus):
    return (asc + moon - venus) % 360

register("my_part", my_formula, my_formula, "Custom part")
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

---

## Chiron (body_id=13) — New in v1.3

Chiron is the 14th body added in v1.3. There is no separate Chiron module in the public API — it is accessed through the standard calculation functions using `body_id=13`.

**Key facts:**

- `ketu.bodies["name"][13] == b"Chiron"`
- Valid date range: 1950–2050 (Chebyshev polynomial coefficients embedded in `ketu/data/chiron_coeffs.npz`)
- Accuracy: max error 0.005695° (sub-arcminute) over the 1950–2050 range
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
