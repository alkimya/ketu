# House Systems

House systems divide the celestial sphere into twelve segments, called **houses**, starting from the Ascendant (the eastern horizon at the moment of birth). Each system uses a different mathematical projection to do this division, which is why the same chart can look markedly different depending on which system you choose. Ketu ships six systems and lets you register additional ones.

## Supported Systems

The six built-in systems are exposed in the `SYSTEMS` dict:

| Key | Name | Description |
|---|---|---|
| `placidus` | Placidus | Time-based; most common in modern western practice |
| `koch` | Koch | Birthplace system; similar to Placidus at mid-latitudes |
| `porphyry` | Porphyry | Divides quadrants into thirds; works at high latitudes |
| `whole_sign` | Whole Sign | Each house = one full sign; oldest recorded system |
| `equal` | Equal | Houses of 30° each, starting from the Ascendant |
| `regiomontanus` | Regiomontanus | Space-based; common in horary astrology |

```python
from ketu.houses import SYSTEMS

print(list(SYSTEMS.keys()))
# ['placidus', 'koch', 'porphyry', 'whole_sign', 'equal', 'regiomontanus']
```

## calculate_houses

```python
calculate_houses(jd, lat, lon, system="placidus", polar_fallback="raise")
```

Computes the twelve house cusps and the angles (Ascendant, Midheaven, ARMC, Vertex) for a given moment and location. Returns a NumPy structured array of `HOUSES_DTYPE`.

**Parameters**

- `jd` — Julian Day (float, UTC)
- `lat` — geographic latitude in degrees (+N / -S)
- `lon` — geographic longitude in degrees (+E / -W)
- `system` — one of the six keys above (default `"placidus"`)
- `polar_fallback` — behaviour above the Arctic/Antarctic circles (see below)

**Example — Paris chart at J2000**

```python
from ketu.houses import calculate_houses, house_of, SYSTEMS, HOUSES_DTYPE, HighLatitudeError

jd = 2451545.0       # J2000: 2000-01-01 12:00 UTC
lat = 48.8566        # Paris latitude
lon = 2.3522         # Paris longitude

h = calculate_houses(jd, lat, lon, system="placidus")

print(h["asc"])      # Ascendant longitude (degrees)
print(h["mc"])       # Midheaven longitude (degrees)
print(h["cusps"])    # Array of 12 cusp longitudes
```

**Switching systems**

```python
for system in SYSTEMS:
    h = calculate_houses(jd, lat, lon, system=system)
    print(f"{system:16s}  ASC={h['asc']:.2f}  MC={h['mc']:.2f}")
```

## house_of

```python
house_of(planet_lon, cusps)
```

Places one or more planet longitudes into a house number (1–12), vectorised over an array of longitudes.

```python
from ketu.houses import calculate_houses, house_of

jd = 2451545.0
h = calculate_houses(jd, 48.8566, 2.3522)
cusps = h["cusps"]

# Single planet
sun_lon = 280.5
print(house_of(sun_lon, cusps))   # e.g. 10

# Multiple planets at once
import numpy as np
planet_lons = np.array([280.5, 45.3, 123.7, 198.2])
houses = house_of(planet_lons, cusps)
print(houses)   # array of house numbers 1–12
```

## HOUSES_DTYPE

The structured array returned by `calculate_houses` has the following fields:

| Field | Type | Description |
|---|---|---|
| `jd` | float64 | Julian Day of the calculation |
| `lat` | float64 | Geographic latitude |
| `lon` | float64 | Geographic longitude |
| `system` | U20 | House system name |
| `cusps` | float64[12] | Twelve house cusp longitudes (degrees) |
| `asc` | float64 | Ascendant longitude (degrees) |
| `mc` | float64 | Midheaven longitude (degrees) |
| `armc` | float64 | ARMC (sidereal time angle) |
| `vertex` | float64 | Vertex longitude (degrees) |

## High-Latitude Handling

Projection-based systems (Placidus, Koch) break down at extreme latitudes (roughly above 66° N or below 66° S) because the ecliptic can fail to intersect the prime vertical.

**`polar_fallback="raise"` (default)** — raises `HighLatitudeError` when the calculation is geometrically impossible.

**Alternative fallback** — pass the name of another system to use as a fallback:

```python
from ketu.houses import calculate_houses, HighLatitudeError

# Attempt Placidus; fall back to Porphyry at high latitudes
try:
    h = calculate_houses(jd, 70.0, 25.0, system="placidus", polar_fallback="porphyry")
except HighLatitudeError:
    # polar_fallback="raise" and the location is beyond the polar circle
    pass
```

Whole Sign and Equal never raise `HighLatitudeError` — they work everywhere.

## Registering Custom Systems

```python
from ketu.houses import register

@register("my_system")
def my_system_calculator(jd, lat, lon):
    # Returns (cusps_array[12], asc, mc, armc, vertex)
    ...
```

After registration, `"my_system"` is available as a `system=` argument to `calculate_houses`.

## Next Steps

- [Relational charts](relational_charts.md) — synastry and composite charts using house cusps
- [API reference](api.md) — full `ketu.houses` signature list
