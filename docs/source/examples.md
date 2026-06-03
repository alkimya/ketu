# Examples

## Moon Phases with Pattern Matching

The example below uses emoji labels in *prose* — not inside Python strings — to avoid syntax-highlight warnings.

```python
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from ketu.ephemeris.time import utc_to_julian
from ketu.calculations import long

def lunar_phase(jday):
    """Return (phase_name, elongation, description) for the given Julian Day."""

    # Calculate the Sun-Moon angle
    sun_long = long(jday, 0)
    moon_long = long(jday, 1)

    # Elongation of the Moon relative to the Sun
    elongation = (moon_long - sun_long) % 360

    # Phase matching on elongation range
    match elongation:
        case e if 0 <= e < 22.5:
            return "New Moon", e, "Conjunction"
        case e if 22.5 <= e < 67.5:
            return "Waxing Crescent", e, "Waxing"
        case e if 67.5 <= e < 112.5:
            return "First Quarter", e, "Waxing Quarter"
        case e if 112.5 <= e < 157.5:
            return "Waxing Gibbous", e, "Gibbous"
        case e if 157.5 <= e < 202.5:
            return "Full Moon", e, "Opposition"
        case e if 202.5 <= e < 247.5:
            return "Waning Gibbous", e, "Gibbous"
        case e if 247.5 <= e < 292.5:
            return "Last Quarter", e, "Waning Square"
        case e if 292.5 <= e < 337.5:
            return "Waning Crescent", e, "Balsamic"
        case _:
            return "New Moon", e, "Conjunction"


def lunar_calendar(year, month):
    """Generate a lunar phase calendar for a month."""

    print(f"\n{'='*50}")
    print(f"LUNAR CALENDAR - {month:02d}/{year}")
    print(f"{'='*50}\n")

    tz = ZoneInfo("UTC")

    for day in range(1, 32):
        try:
            dt = datetime(year, month, day, 12, 0, tzinfo=tz)
            jday = utc_to_julian(dt)

            phase, elongation, description = lunar_phase(jday)

            if any(key in phase for key in ["New", "First Quarter",
                                            "Full", "Last Quarter"]):
                print(f"{day:02d}/{month:02d}: {phase} ({elongation:.1f}°)")

        except ValueError:
            break  # End of month


# Example of use
lunar_calendar(2024, 1)
```

## Planetary Transits

```python
from datetime import datetime, timedelta
from dataclasses import dataclass
from zoneinfo import ZoneInfo
from ketu.ephemeris.time import utc_to_julian
from ketu.calculations import long, body_name
from ketu.aspects import get_orb
import ketu.core


@dataclass
class Transit:
    """Represents a planetary transit."""
    planet: str
    aspect: str
    natal_planet: str
    date: datetime
    orb: float
    exact: bool = False


def search_transits(natal_date, transit_date, planets_to_follow=None):
    """Search for transits to natal positions."""

    if planets_to_follow is None:
        planets_to_follow = [0, 1, 2, 3, 4, 5, 6]  # Sun to Saturn

    natal_jday = utc_to_julian(natal_date)
    natal_positions = {i: long(natal_jday, i) for i in planets_to_follow}

    transit_jday = utc_to_julian(transit_date)
    transits = []

    for i_transit in planets_to_follow:
        transit_pos = long(transit_jday, i_transit)

        for natal_i, natal_pos in natal_positions.items():
            diff = abs(transit_pos - natal_pos) % 360
            if diff > 180:
                diff = 360 - diff

            for j, angle in enumerate(ketu.core.aspects["angle"]):
                max_orb = get_orb(i_transit, natal_i, j)
                orb = abs(diff - angle)

                if orb <= max_orb:
                    transit = Transit(
                        planet=body_name(i_transit),
                        aspect=ketu.core.aspects["name"][j].decode(),
                        natal_planet=body_name(natal_i),
                        date=transit_date,
                        orb=orb,
                        exact=(orb < 1.0)
                    )
                    transits.append(transit)

    return transits


# Example
natal = datetime(1990, 5, 15, 14, 30, tzinfo=ZoneInfo("Europe/Paris"))
transit = datetime.now(ZoneInfo("Europe/Paris"))

transits = search_transits(natal, transit)
for t in transits:
    exact = " EXACT!" if t.exact else ''
    print(f"{t.planet} {t.aspect} {t.natal_planet} natal "
          f"(orb: {t.orb:.2f}°){exact}")
```

## Period Analysis

```python
from datetime import datetime, timedelta
from ketu.ephemeris.time import utc_to_julian
from ketu.calculations import long, body_sign, is_retrograde, body_name
from ketu.aspects import calculate_aspects
import ketu
import ketu.core


def analyze_period(start_date, end_date, step_days=1):
    """Analyze aspects over a period."""

    results = {
        "exact_aspects": [],
        "sign_changes": [],
        "retrogrades": [],
        "statistics": {}
    }

    current = start_date
    prev_signs = None
    prev_retros = None

    while current <= end_date:
        jday = utc_to_julian(current)

        signs = [body_sign(long(jday, i))[0] for i in range(10)]
        retros = [is_retrograde(jday, i) for i in range(10)]

        if prev_signs is not None:
            for i, (s1, s2) in enumerate(zip(prev_signs, signs)):
                if s1 != s2:
                    results["sign_changes"].append({
                        "date": current,
                        "planet": body_name(i),
                        "old_sign": ketu.signs[s1],
                        "new_sign": ketu.signs[s2]
                    })

        if prev_retros is not None:
            for i, (r1, r2) in enumerate(zip(prev_retros, retros)):
                if r1 != r2:
                    results["retrogrades"].append({
                        "date": current,
                        "planet": body_name(i),
                        "status": 'Retrograde' if r2 else "Direct"
                    })

        aspects = calculate_aspects(jday)
        for asp in aspects:
            if abs(asp[3]) < 0.5:
                results["exact_aspects"].append({
                    "date": current,
                    "aspect": ketu.core.aspects["name"][asp[2]].decode(),
                    "planet1": body_name(asp[0]),
                    "planet2": body_name(asp[1]),
                    "orb": asp[3]
                })

        prev_signs = signs
        prev_retros = retros
        current += timedelta(days=step_days)

    return results


# Analyze the current month
start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

analysis = analyze_period(start, end)
print(f"Sign changes: {len(analysis['sign_changes'])}")
print(f"Direction changes: {len(analysis['retrogrades'])}")
print(f"Exact aspects: {len(analysis['exact_aspects'])}")
```

## Full Chart with Synastry (New in v1.2)

```python
from ketu.ephemeris.time import utc_to_julian
from ketu.charts import compute_chart
from ketu.synastry import calculate_synastry
from ketu.calculations import body_name
from datetime import datetime

# Person A: Paris, J2000
jd_a = 2451545.0
chart_a = compute_chart(jd_a, 48.8566, 2.3522, system="placidus")

# Person B: London, one year later
jd_b = 2451910.0
chart_b = compute_chart(jd_b, 51.5074, -0.1278, system="placidus")

print(f"Person A — ASC: {chart_a['asc']:.2f}°  Sun: {chart_a['body_lons'][0]:.2f}°")
print(f"Person B — ASC: {chart_b['asc']:.2f}°  Sun: {chart_b['body_lons'][0]:.2f}°")

# Compute synastry aspects between the two charts
syn = calculate_synastry(chart_a, chart_b)

print(f"\nSynastry aspects ({len(syn)} in orb):")

# calculate_synastry extends the 14-body axis with two angles:
# index 14 = ASC, index 15 = MC. body_name() only knows 0–13, so map the angles.
ANGLE_LABEL = {14: "ASC", 15: "MC"}

def synastry_label(idx):
    return ANGLE_LABEL.get(idx, body_name(idx))

for row in syn[:5]:   # Show first 5
    name_a = synastry_label(int(row["body_a"]))
    name_b = synastry_label(int(row["body_b"]))
    print(f"  {name_a} (A) — {name_b} (B): orb {row['orb']:.2f}°")
```

## Solar Return (New in v1.2)

```python
from ketu.ephemeris.time import utc_to_julian
from ketu.returns import solar_return
from datetime import datetime

# Natal data
natal_jd = 2451545.0       # J2000 — birth Julian Day
natal_lat, natal_lon = 48.8566, 2.3522   # Paris

# Solar return for 2026 at the natal location
sr = solar_return(natal_jd, natal_lat, natal_lon, target_year=2026)

print(f"Solar Return 2026:")
print(f"  ASC:  {sr['asc']:.2f}°")
print(f"  MC:   {sr['mc']:.2f}°")
print(f"  Sun:  {sr['body_lons'][0]:.2f}°")

# Relocated solar return (e.g. London)
sr_london = solar_return(
    natal_jd, natal_lat, natal_lon,
    target_year=2026,
    return_lat=51.5074, return_lon=-0.1278
)
print(f"\nRelocated to London — ASC: {sr_london['asc']:.2f}°")
```

## Next steps

- Check out the [Concepts](concepts.md) to understand the theory
- Refer to the [API](api.md) for technical details
- Explore [Relational Charts](relational_charts.md) for synastry and composite
- Contribute to the project on [GitHub](https://github.com/alkimya/ketu)
