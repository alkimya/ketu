# Chiron — the 14th Body

Ketu v1.3 adds **Chiron** as the 14th celestial body. Chiron is a small solar system body (a centaur) orbiting between Saturn and Uranus, carrying astrological significance as the "Wounded Healer". It is accessible through all standard Ketu calculation functions using `body_id=13`.

## Implementation Details

| Property | Value |
|---|---|
| `body_id` | 13 |
| Valid date range | 1900-01-01 to 2100-12-31 (Julian Days 2415020.5 to 2488069.5) — expanded in v1.4 |
| Position accuracy | max error 0.001214° (sub-arcminute, ~4 arcseconds) — improved in v1.4 |
| Evaluation method | Pure-NumPy Chebyshev polynomial evaluation |
| Runtime dependency | None — coefficients embedded in `ketu/data/chiron_coeffs.npz` |

The Chebyshev coefficients were generated offline using Swiss Ephemeris (build-only, AGPL-isolated). At runtime, Ketu uses pure NumPy — no `pyswisseph` dependency required.

## Accessing Chiron via Calculation Functions

Chiron uses the same API as any other body — just pass `body_id=13`.

```python
from ketu.calculations import long, lat

jd = 2451545.0   # J2000: 2000-01-01 12:00 UTC

chiron_lon = long(jd, 13)   # ~251.6125 degrees
chiron_lat = lat(jd, 13)

print(f"Chiron longitude: {chiron_lon:.4f} deg")
print(f"Chiron latitude:  {chiron_lat:.4f} deg")
```

You can also compute Chiron's properties alongside other bodies:

```python
from ketu.calculations import long, lat

jd = 2451545.0
body_ids = [0, 1, 13]   # Sun, Moon, Chiron
lons = [long(jd, b) for b in body_ids]
```

## Chiron in a Natal Chart

`compute_chart` returns a structured array with a `body_lons` field of shape `[14]`. Index 13 is Chiron.

```python
from ketu.charts import compute_chart

jd = 2451545.0
chart = compute_chart(jd, 48.8566, 2.3522)   # Paris, J2000

chiron_longitude = chart["body_lons"][13]
chiron_latitude  = chart["body_lats"][13]
chiron_speed     = chart["body_speeds"][13]   # degrees/day

print(f"Chiron at {chiron_longitude:.4f} deg")
```

All relational chart functions (synastry, composite, returns) inherit Chiron automatically — it appears at index 13 in every `body_lons`, `body_lats`, `body_speeds`, `aspect_matrix`, and `aspect_orbs` field.

## Date Range and Error Behaviour

Requesting Chiron outside 1950-2050 raises a `ValueError`:

```python
from ketu.calculations import long

# This raises ValueError: JD outside Chiron's supported range
chiron_lon = long(2300000.0, 13)
```

For dates inside the range, the positional error is guaranteed to be at most 0.005695° (about 20 arcseconds), well below the 0.01° target set during the Chebyshev spike (Phase 23).

## Breaking Change in v1.3 (D-08)

Prior to v1.3, `CHART_DTYPE` had a `body_lons[13]` field (indices 0–12). Adding Chiron expanded this to `body_lons[14]` (indices 0–13). Any code that hardcoded the body count (13) or accessed body arrays by fixed numeric index beyond 12 must be updated.

See [Migration Guide](migration.md) for the full upgrade path from v1.2 to v1.3.

## Next Steps

- [API reference](api.md) — full `ketu.calculations` signature list
- [Migration Guide](migration.md) — upgrading from v1.2, D-08 body-axis changes
