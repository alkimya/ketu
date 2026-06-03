# Quick Start Guide

## First Calculation

### Interactive Mode (CLI)

The simplest way to get started:

```bash
ketu
```

Follow the prompts:

1. Enter a date (ISO format): `2020-12-21`
2. Enter a time: `19:20`
3. Enter a timezone: `Europe/Paris`

### Programming Mode

```python
from datetime import datetime
from zoneinfo import ZoneInfo
from ketu.ephemeris.time import utc_to_julian
from ketu.display import print_positions, print_aspects

# Define the moment
paris = ZoneInfo("Europe/Paris")
dt = datetime(2020, 12, 21, 19, 20, tzinfo=paris)

# Convert to Julian day
jday = utc_to_julian(dt)

# Display positions
print_positions(jday)
```

### Basic Calculations

#### Planetary Positions

```python
from datetime import datetime
from ketu.ephemeris.time import utc_to_julian
from ketu.calculations import long, lat, dist_au

# Current date
dt = datetime.now()
jday = utc_to_julian(dt)

# Sun position (id=0)
sun_longitude = long(jday, 0)
sun_latitude = lat(jday, 0)
sun_distance = dist_au(jday, 0)

print(f"Sun: {sun_longitude:.2f}° longitude")
print(f"     {sun_latitude:.2f}° latitude")
print(f"     {sun_distance:.2f} AU")
```

#### Determine Zodiac Sign

```python
import ketu
from ketu.calculations import long, body_sign

# Moon position
moon_long = long(jday, 1)  # 1 = Moon

# Calculate sign
sign_data = body_sign(moon_long)
sign_index = sign_data[0]
degrees = sign_data[1]
minutes = sign_data[2]

print(f"Moon in {ketu.signs[sign_index]} {degrees}°{minutes}'")
```

#### Check Retrogradation

```python
from ketu.calculations import is_retrograde

# Mercury (id=2)
if is_retrograde(jday, 2):
    print("Mercury is retrograde")
else:
    print("Mercury is direct")
```

### Aspect Calculation

#### Aspects Between Two Planets

```python
from ketu.aspects import get_aspect
import ketu.core

# Sun-Moon aspect
aspect = get_aspect(jday, 0, 1)  # 0=Sun, 1=Moon

if aspect:
    body1, body2, asp_type, orb = aspect
    aspect_name = ketu.core.aspects["name"][asp_type].decode()
    print(f"Sun-Moon: {aspect_name} (orb: {orb:.2f}°)")
else:
    print("No Sun-Moon aspect")
```

```{note}
Use `ketu.core.aspects` (the aspect-type table) here, **not** `ketu.aspects`.
Because `ketu/aspects/` is a subpackage, `from ketu.aspects import ...`
binds the name `ketu.aspects` to that module — so `ketu.aspects["name"]`
would raise `TypeError: 'module' object is not subscriptable`. The
structured table always lives at `ketu.core.aspects`.
```

#### All Current Aspects

```python
from ketu.aspects import calculate_aspects
from ketu.calculations import body_name
import ketu.core

# Calculate all aspects
aspects_array = calculate_aspects(jday)

# Display
for aspect in aspects_array:
    b1, b2, asp_idx, orb = aspect
    name1 = body_name(b1)
    name2 = body_name(b2)
    asp_name = ketu.core.aspects["name"][asp_idx].decode()

    print(f"{name1} - {name2}: {asp_name} ({orb:.2f}°)")
```

### Complete Example: Natal Positions

```python
from datetime import datetime
from zoneinfo import ZoneInfo
import ketu
import ketu.core
from ketu.ephemeris.time import utc_to_julian, local_to_utc
from ketu.calculations import long, body_sign, is_retrograde, body_name, positions
from ketu.aspects import calculate_aspects

def natal_positions(year, month, day, hour, minute, timezone_str):
    """Calculate planetary positions for a birth moment"""

    # Create the date
    tz = ZoneInfo(timezone_str)
    dt = datetime(year, month, day, hour, minute, tzinfo=tz)
    jday = utc_to_julian(dt)

    print(f"\n{'='*50}")
    print(f"NATAL POSITIONS - {dt.strftime('%d/%m/%Y %H:%M')} {timezone_str}")
    print(f"{'='*50}\n")

    # Planetary positions
    print("PLANETARY POSITIONS:")
    print("-" * 30)

    for i, body in enumerate(ketu.bodies["name"]):
        if i > 9:  # Skip Rahu/Lilith to simplify
            break

        name = body.decode()
        longitude = long(jday, i)
        sign_data = body_sign(longitude)
        sign = ketu.signs[sign_data[0]]
        deg, min = sign_data[1], sign_data[2]

        # Check retrogradation
        retro = " R" if is_retrograde(jday, i) else ""

        print(f"{name:8} : {sign:12} {deg:2}°{min:02}'{retro}")

    # Major aspects
    print(f"\nMAJOR ASPECTS:")
    print("-" * 30)

    aspects = calculate_aspects(jday)
    for aspect in aspects:
        b1, b2, asp_idx, orb = aspect
        # Display only aspects with orb < 5°
        if abs(orb) < 5:
            name1 = body_name(b1)
            name2 = body_name(b2)
            asp_name = ketu.core.aspects["name"][asp_idx].decode()
            print(f"{name1:8} {asp_name:12} {name2:8} ({orb:+.2f}°)")

# Usage
natal_positions(1990, 5, 15, 14, 30, "Europe/Paris")
```

### Building a Full Natal Chart

New in v1.2: `compute_chart` returns a single structured array containing positions, house cusps, and aspect matrix.

```python
from ketu.ephemeris.time import utc_to_julian
from ketu.charts import compute_chart
from datetime import datetime

# Paris, J2000 epoch
jd = 2451545.0  # 2000-01-01 12:00 UTC
lat, lon = 48.8566, 2.3522  # Paris

chart = compute_chart(jd, lat, lon, system="placidus")

# Ascendant
print(f"ASC: {chart['asc']:.2f}°")

# Sun longitude (body index 0)
print(f"Sun: {chart['body_lons'][0]:.2f}°")

# Chiron longitude (body index 13, new in v1.3)
print(f"Chiron: {chart['body_lons'][13]:.2f}°")
```

### Tips and Tricks

#### Using the Cache

Position calculations use `@lru_cache` to optimize performance:

```python
from ketu.calculations import long, lat
from ketu.ephemeris.planets import body_properties

# These calls use the cache
long1 = long(jday, 0)
lat1 = lat(jday, 0)  # Uses body_properties cache

# To clear the cache
body_properties.cache_clear()
```

#### Working with NumPy

```python
import numpy as np
from ketu.calculations import long, body_sign

# Calculate positions for multiple days
days = np.arange(jday, jday + 30, 1)  # 30 days
sun_positions = [long(d, 0) for d in days]

# Find sign changes
signs = [body_sign(pos)[0] for pos in sun_positions]
changes = np.where(np.diff(signs))[0]
```

### Next Steps

- Explore [Advanced Examples](examples.md) for complex use cases
- See the [API Reference](api.md) for all details
- Learn about [Astrological Concepts](concepts.md) used in Ketu
- Discover [House Systems](houses.md) for complete chart calculation
