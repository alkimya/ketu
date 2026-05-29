# Relational Charts: Synastry and Composite

Relational charts analyse two people's charts together rather than in isolation. Ketu provides three modules for this: `ketu.charts` builds the individual charts, `ketu.synastry` compares them aspect by aspect, and `ketu.composite` derives a midpoint chart that represents the relationship itself.

## Building Charts with compute_chart

`compute_chart` is the central function for natal chart calculation. It calculates all 14 body positions, twelve house cusps, the four angles, and the full aspect matrix in a single call, returning a `CHART_DTYPE` structured array.

```python
compute_chart(jd, lat, lon, system="placidus", aspects=None, polar_fallback="raise")
```

**Parameters**

- `jd` — Julian Day (float, UTC)
- `lat` / `lon` — geographic latitude and longitude in degrees
- `system` — house system (default `"placidus"`)
- `aspects` — aspect set spec (`None` uses the default classical set)
- `polar_fallback` — high-latitude fallback behaviour (see [House Systems](houses.md))

**Example — two charts**

```python
from ketu.charts import compute_chart

jd_a = 2451545.0          # 2000-01-01 12:00 UTC (J2000), Paris
jd_b = 2451910.0          # 2000-12-31 12:00 UTC, New York

chart_a = compute_chart(jd_a, 48.8566, 2.3522)      # Paris
chart_b = compute_chart(jd_b, 40.7128, -74.0060)    # New York

print(chart_a["asc"])                  # Ascendant of chart A
print(chart_b["body_lons"][0])         # Sun longitude of chart B
```

### CHART_DTYPE Fields

| Field | Shape | Description |
|---|---|---|
| `jd` | scalar | Julian Day |
| `lat` | scalar | Geographic latitude |
| `lon` | scalar | Geographic longitude |
| `system` | scalar | House system name |
| `body_lons` | [14] | Ecliptic longitudes for bodies 0–13 |
| `body_lats` | [14] | Ecliptic latitudes for bodies 0–13 |
| `body_speeds` | [14] | Daily motion in degrees for bodies 0–13 |
| `cusps` | [12] | House cusp longitudes |
| `asc` | scalar | Ascendant longitude |
| `mc` | scalar | Midheaven longitude |
| `armc` | scalar | ARMC (sidereal time angle) |
| `vertex` | scalar | Vertex longitude |
| `aspect_matrix` | [14, 14] | Aspect type between each body pair (0 = none) |
| `aspect_orbs` | [14, 14] | Orb in degrees for each active aspect |

Body index 13 is Chiron (see [Chiron](chiron.md)).

### Sect Helper

```python
from ketu.charts import is_day_chart

# Returns True if the Sun is above the horizon (day chart)
is_day = is_day_chart(jd_a, 48.8566, 2.3522)
```

This is used internally by Arabic Parts to select sect-aware formulas.

## Synastry

Synastry overlays two charts and finds aspects formed between the planets of one person and the planets of the other.

```python
from ketu.synastry import calculate_synastry, SYNASTRY_DTYPE

calculate_synastry(chart_a, chart_b, aspects="classical", orbs="synastry", mode="filtered")
```

**Parameters**

- `chart_a`, `chart_b` — `CHART_DTYPE` structured arrays from `compute_chart`
- `aspects` — aspect set: `"classical"` (default), `"traditional"`, `"extended"`, or a list/mask
- `orbs` — orb set: `"synastry"` applies the standard synastry orb reduction factor
- `mode` — `"filtered"` returns only active aspects; `"all"` returns every body pair

**Example**

```python
from ketu.charts import compute_chart
from ketu.synastry import calculate_synastry

jd_a = 2451545.0
jd_b = 2451910.0

chart_a = compute_chart(jd_a, 48.8566, 2.3522)
chart_b = compute_chart(jd_b, 40.7128, -74.0060)

aspects = calculate_synastry(chart_a, chart_b)

for row in aspects:
    print(
        f"Body {row['body_a']} ({row['lon_a']:.1f} deg)"
        f" {row['aspect_type']}"
        f" Body {row['body_b']} ({row['lon_b']:.1f} deg)"
        f"  orb={row['orb']:.2f} deg"
        f"  applying={row['applying']}"
    )
```

### SYNASTRY_DTYPE Fields

| Field | Type | Description |
|---|---|---|
| `body_a` | int | Body index from chart A (0–15; 14=ASC, 15=MC) |
| `body_b` | int | Body index from chart B (0–15) |
| `lon_a` | float64 | Ecliptic longitude of body A |
| `lon_b` | float64 | Ecliptic longitude of body B |
| `aspect_type` | int | Aspect type code |
| `orb` | float64 | Orb in degrees |
| `applying` | bool | True if the aspect is applying |
| `orb_limit` | float64 | Maximum allowed orb for this aspect |

Synastry includes ASC and MC from both charts, giving up to 16 points per chart.

## Composite Charts

A composite chart is constructed from the midpoints of each pair of planets, houses, and angles between two natal charts. It represents the energy of the relationship rather than either individual.

```python
from ketu.composite import calculate_composite, circular_midpoint

calculate_composite(chart_a, chart_b, system="placidus")
```

Returns a single `CHART_DTYPE` structured array. The house system is re-calculated from the composite Ascendant and Midheaven.

```python
from ketu.charts import compute_chart
from ketu.composite import calculate_composite, circular_midpoint

jd_a = 2451545.0
jd_b = 2451910.0

chart_a = compute_chart(jd_a, 48.8566, 2.3522)
chart_b = compute_chart(jd_b, 40.7128, -74.0060)

composite = calculate_composite(chart_a, chart_b)

print(composite["asc"])            # Composite Ascendant
print(composite["body_lons"][0])   # Composite Sun
```

### circular_midpoint

`circular_midpoint` computes the shortest-arc midpoint between two ecliptic longitudes, handling the 0°/360° wraparound correctly.

```python
from ketu.composite import circular_midpoint

# Midpoint of 350° and 10° crosses the 0°-point: result is 0°
mid = circular_midpoint(350.0, 10.0)
print(mid)   # 0.0

# Standard midpoint
mid2 = circular_midpoint(30.0, 90.0)
print(mid2)  # 60.0
```

## Next Steps

- [Predictive charts](predictive_charts.md) — solar and lunar return charts
- [Arabic Parts](arabic_parts.md) — Fortune, Spirit, and custom lots
- [API reference](api.md) — full signatures for `ketu.charts`, `ketu.synastry`, `ketu.composite`
