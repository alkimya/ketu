# Arabic Parts (Hermetic Lots)

Arabic Parts — also called **Hermetic Lots** in classical astrology — are sensitive points derived from the longitudes of chart positions rather than from direct planetary observation. They were extensively used in Hellenistic and Medieval astrology and remain central to traditional practice.

Ketu provides a sect-aware registry of parts via the `ketu.parts` module.

## Built-in Parts

Three parts are registered by default:

| Name | Key | Sect-aware | Formula (day) | Formula (night) |
|---|---|---|---|---|
| Part of Fortune | `"fortune"` | Yes | ASC + Moon - Sun | ASC + Sun - Moon |
| Part of Spirit | `"spirit"` | Yes | ASC + Sun - Moon | ASC + Moon - Sun |
| Part of Marriage | `"marriage"` | No | ASC + Venus - Saturn | ASC + Venus - Saturn |

**Fortune and Spirit invert their formulas by sect:** in a day chart the standard formula applies; in a night chart the formula is reversed (Sun and Moon swap roles). Marriage is the same formula regardless of sect.

## Sect Detection

`ketu.parts` uses `is_day_chart` from `ketu.charts` internally. The chart passed to `calculate_part` carries its own `jd`, `lat`, and `lon` — Ketu determines sect automatically from those values.

## calculate_part

```python
calculate_part(part_name, chart) -> float
```

Computes a single part and returns its ecliptic longitude (0–360°).

```python
from ketu.charts import compute_chart
from ketu.parts import calculate_part

jd  = 2451545.0   # J2000: 2000-01-01 12:00 UTC
lat = 48.8566     # Paris
lon = 2.3522

chart = compute_chart(jd, lat, lon)

fortune  = calculate_part("fortune",  chart)
spirit   = calculate_part("spirit",   chart)
marriage = calculate_part("marriage", chart)

print(f"Fortune:  {fortune:.2f} deg")
print(f"Spirit:   {spirit:.2f} deg")
print(f"Marriage: {marriage:.2f} deg")
```

## calculate_all_parts

```python
calculate_all_parts(chart, parts=None) -> dict[str, float]
```

Computes all registered parts at once. The result is a plain Python dict mapping part name to longitude (float, degrees 0–360).

- `parts=None` computes every registered part.
- Pass a list of keys to restrict the calculation.

```python
from ketu.charts import compute_chart
from ketu.parts import calculate_all_parts

jd  = 2451545.0
lat = 48.8566
lon = 2.3522

chart = compute_chart(jd, lat, lon)

all_lots = calculate_all_parts(chart)
for name, lon_deg in sorted(all_lots.items()):
    print(f"{name:12s}  {lon_deg:.2f} deg")

# Selective calculation
select = calculate_all_parts(chart, parts=["fortune", "spirit"])
```

## Formula Signature

Every part formula (both day and night variants) must accept exactly four positional arguments:

```python
(asc_lon: float, sun_lon: float, moon_lon: float, venus_lon: float) -> float
```

Even if a formula does not use all four arguments, they are always passed in this order. Results are automatically normalised to [0°, 360°) by the registry.

## Registering Custom Parts

Use `register` to add a new part to the global registry:

```python
from ketu.parts import register, PARTS

# Part of Commerce: ASC + Mercury - Sun (same day and night)
def commerce_formula(asc_lon, sun_lon, moon_lon, venus_lon):
    from ketu.calculations import long
    return asc_lon  # simplified — real formula would use Mercury

register(
    name="commerce",
    day_formula=lambda asc, sun, moon, venus: asc + sun - moon,   # placeholder
    night_formula=lambda asc, sun, moon, venus: asc + sun - moon, # same (fixed)
    description="Part of Commerce (custom example)",
)

# Now 'commerce' is available everywhere
print(list(PARTS.keys()))
```

After registration, the new part is included in `calculate_all_parts(chart)` automatically.

## PartSpec and get_part

You can inspect any registered part:

```python
from ketu.parts import get_part, PartSpec

spec = get_part("fortune")
print(spec.description)      # "Part of Fortune"
print(spec.day_formula)      # callable
```

`PartSpec` is a named-tuple-like object with fields: `name`, `day_formula`, `night_formula`, `description`.

## Next Steps

- [Relational charts](relational_charts.md) — synastry and composite charts that can benefit from part analysis
- [API reference](api.md) — full `ketu.parts` signature list
