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
import ketu

# Define the moment
paris = ZoneInfo("Europe/Paris")
dt = datetime(2020, 12, 21, 19, 20, tzinfo=paris)

# Convert to Julian day
jday = ketu.utc_to_julian(dt)

# Display positions
ketu.print_positions(jday)
```

### Basic Calculations

#### Planetary Positions

```python
import ketu
from datetime import datetime

# Current date
dt = datetime.now()
jday = ketu.utc_to_julian(dt)

# Sun position (id=0)
sun_longitude = ketu.long(jday, 0)
sun_latitude = ketu.lat(jday, 0)
sun_distance = ketu.dist_au(jday, 0)

print(f"Sun: {sun_longitude:.2f}° longitude")
print(f"     {sun_latitude:.2f}° latitude")
print(f"     {sun_distance:.2f} AU")
```

#### Determine Zodiac Sign

```python
# Moon position
moon_long = ketu.long(jday, 1)  # 1 = Moon

# Calculate sign
sign_data = ketu.body_sign(moon_long)
sign_index = sign_data[0]
degrees = sign_data[1]
minutes = sign_data[2]

print(f"Moon in {ketu.signs[sign_index]} {degrees}°{minutes}'")
```

#### Check Retrogradation

```python
# Mercury (id=2)
if ketu.is_retrograde(jday, 2):
    print("Mercury is retrograde")
else:
    print("Mercury is direct")
```

### Aspect Calculation

#### Aspects Between Two Planets

```python
# Sun-Moon aspect
aspect = ketu.get_aspect(jday, 0, 1)  # 0=Sun, 1=Moon

if aspect:
    body1, body2, asp_type, orb = aspect
    aspect_name = ketu.aspects["name"][asp_type].decode()
    print(f"Sun-Moon: {aspect_name} (orb: {orb:.2f}°)")
else:
    print("No Sun-Moon aspect")
```

#### All Current Aspects

```python
# Calculate all aspects
aspects_array = ketu.calculate_aspects(jday)

# Display
for aspect in aspects_array:
    b1, b2, asp_idx, orb = aspect
    name1 = ketu.body_name(b1)
    name2 = ketu.body_name(b2)
    asp_name = ketu.aspects["name"][asp_idx].decode()

    print(f"{name1} - {name2}: {asp_name} ({orb:.2f}°)")
```

### Complete Example: Natal Chart

```python
import ketu
from datetime import datetime
from zoneinfo import ZoneInfo

def natal_chart(year, month, day, hour, minute, timezone_str):
    """Calculate a simple natal chart"""

    # Create the date
    tz = ZoneInfo(timezone_str)
    dt = datetime(year, month, day, hour, minute, tzinfo=tz)
    jday = ketu.utc_to_julian(dt)

    print(f"\n{'='*50}")
    print(f"NATAL CHART - {dt.strftime('%d/%m/%Y %H:%M')} {timezone_str}")
    print(f"{'='*50}\n")

    # Planetary positions
    print("PLANETARY POSITIONS:")
    print("-" * 30)

    for i, body in enumerate(ketu.bodies["name"]):
        if i > 9:  # Skip Rahu/Lilith to simplify
            break

        name = body.decode()
        longitude = ketu.long(jday, i)
        sign_data = ketu.body_sign(longitude)
        sign = ketu.signs[sign_data[0]]
        deg, min = sign_data[1], sign_data[2]

        # Check retrogradation
        retro = " ℞" if ketu.is_retrograde(jday, i) else ""

        print(f"{name:8} : {sign:12} {deg:2}°{min:02}'{retro}")

    # Major aspects
    print(f"\nMAJOR ASPECTS:")
    print("-" * 30)

    aspects = ketu.calculate_aspects(jday)
    for aspect in aspects:
        b1, b2, asp_idx, orb = aspect
        # Display only aspects with orb < 5°
        if abs(orb) < 5:
            name1 = ketu.body_name(b1)
            name2 = ketu.body_name(b2)
            asp_name = ketu.aspects["name"][asp_idx].decode()
            print(f"{name1:8} {asp_name:12} {name2:8} ({orb:+.2f}°)")

# Usage
natal_chart(1990, 5, 15, 14, 30, "Europe/Paris")
```

### Tips and Tricks

#### Using the Cache

Position calculations use `@lru_cache` to optimize performance:

```python

# These calls use the cache
long1 = ketu.long(jday, 0)
lat1 = ketu.lat(jday, 0)  # Uses body_properties cache

# To clear the cache
ketu.body_properties.cache_clear()
```

#### Working with NumPy

```python
import numpy as np

# Calculate positions for multiple days
days = np.arange(jday, jday + 30, 1)  # 30 days
sun_positions = [ketu.long(d, 0) for d in days]

# Find sign changes
signs = [ketu.body_sign(pos)[0] for pos in sun_positions]
changes = np.where(np.diff(signs))[0]
```

#### Customizing Orbs

```python
# Temporarily modify orbs
original_orbs = ketu.bodies["orb"].copy()

# Tighter orbs
ketu.bodies["orb"] = ketu.bodies["orb"] * 0.5

# Calculate with new orbs
aspects = ketu.calculate_aspects(jday)

# Restore
ketu.bodies["orb"] = original_orbs
```

### Next Steps

- Explore [Advanced Examples](examples.md) for complex use cases
- See the [API Reference](api.md) for all details
- Learn about [Astrological Concepts](concepts.md) used in Ketu
