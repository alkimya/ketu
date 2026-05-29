# Predictive Charts: Solar and Lunar Returns

Return charts mark the moment when a planet returns to the same ecliptic longitude it occupied at birth. Ketu provides two return functions — `solar_return` for the Sun's annual return, and `lunar_return` for the Moon's monthly return.

Both functions return a full `CHART_DTYPE` structured array (same as `compute_chart`), with the complete natal house system, body positions, and aspect matrix computed for the exact moment of return.

## Important API Asymmetry

| Function | Target parameter | Type | Meaning |
|---|---|---|---|
| `solar_return` | `target_year` | `int` | Calendar year in which to find the return |
| `lunar_return` | `target_jd` | `float` | Julian Day to start searching **from** |

This distinction matters: `solar_return(natal_jd, ..., target_year=2026)` finds the return that falls in the year 2026 (there is exactly one). `lunar_return(natal_jd, ..., target_jd=jd_now)` finds the next lunar return at or after `target_jd` (there are ~13 per year).

## solar_return

```python
solar_return(
    natal_jd,
    natal_lat,
    natal_lon,
    target_year,
    return_lat=None,
    return_lon=None,
    system="placidus",
)
```

**Parameters**

- `natal_jd` — Julian Day of the natal chart
- `natal_lat`, `natal_lon` — natal location (used as default return location)
- `target_year` — calendar year (int) in which to find the solar return
- `return_lat`, `return_lon` — relocation coordinates (see below); default `None` = natal location
- `system` — house system for the return chart (default `"placidus"`)

**Example — solar return for 2026, natal location**

```python
from ketu.returns import solar_return

natal_jd  = 2451545.0   # natal chart: J2000 (2000-01-01 12:00 UTC)
natal_lat = 48.8566     # Paris
natal_lon = 2.3522

sr = solar_return(natal_jd, natal_lat, natal_lon, target_year=2026)

print(f"Solar return JD:  {sr['jd']:.4f}")
print(f"Solar return ASC: {sr['asc']:.2f} deg")
print(f"Sun longitude:    {sr['body_lons'][0]:.4f} deg")  # Should match natal Sun
```

## lunar_return

```python
lunar_return(
    natal_jd,
    natal_lat,
    natal_lon,
    target_jd,
    return_lat=None,
    return_lon=None,
    system="placidus",
)
```

**Parameters**

- `natal_jd` — Julian Day of the natal chart
- `natal_lat`, `natal_lon` — natal location
- `target_jd` — Julian Day to start the search from (float); the function returns the first lunar return at or after this JD
- `return_lat`, `return_lon` — relocation coordinates; default `None` = natal location
- `system` — house system for the return chart

**Example — next lunar return from J2000**

```python
from ketu.returns import lunar_return

natal_jd  = 2451545.0   # natal chart: J2000
natal_lat = 48.8566     # Paris
natal_lon = 2.3522

# Find the lunar return starting from approximately the same date
lr = lunar_return(natal_jd, natal_lat, natal_lon, target_jd=natal_jd)

print(f"Lunar return JD:  {lr['jd']:.4f}")
print(f"Lunar return ASC: {lr['asc']:.2f} deg")
print(f"Moon longitude:   {lr['body_lons'][1]:.4f} deg")  # Should match natal Moon
```

## Relocation

Both functions accept optional `return_lat` / `return_lon` parameters. When provided, the house cusps and angles in the return chart are calculated for the relocation coordinates instead of the natal location. This is used in relocated return chart analysis.

```python
from ketu.returns import solar_return

natal_jd  = 2451545.0
natal_lat = 48.8566   # natal: Paris
natal_lon = 2.3522

# Relocated solar return: body positions are for the exact return moment,
# but houses are cast for New York
sr_relocated = solar_return(
    natal_jd, natal_lat, natal_lon,
    target_year=2026,
    return_lat=40.7128,   # New York
    return_lon=-74.0060,
)

print(f"Relocated ASC: {sr_relocated['asc']:.2f} deg")
```

When `return_lat=None` and `return_lon=None` (the defaults), the natal coordinates are used for both the return moment search and the house calculation.

## UTC Contract

All Julian Day values (`natal_jd`, `target_jd`) must be in UTC. The functions do not perform any timezone conversion internally.

```python
from ketu.ephemeris.time import utc_to_julian
from datetime import datetime, timezone

natal_dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
natal_jd = utc_to_julian(natal_dt)
```

## Next Steps

- [Relational charts](relational_charts.md) — synastry and composite charts
- [API reference](api.md) — full signatures for `ketu.returns`
