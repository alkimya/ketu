# Ketu Documentation

**Ketu** is a Python library for calculating planetary positions and astrological aspects, based on `pyswisseph` and `numpy`.

The library was originally designed to produce biodynamic calendars and time series driven by astrological aspects, and it can serve as a foundation for building astrology software.

## Overview

Ketu allows you to:

- 🌟 Calculate precise positions of celestial bodies (Sun, Moon, planets, Nodes, Lilith)
- ⚡ Determine aspects between planets
- 📅 Convert between different time systems (UTC, Julian)
- 🔮 Identify retrogradations and zodiac signs
- 📊 Generate time series of aspects (coming soon)

## Navigation

```{toctree}
:maxdepth: 2
:caption: User Guide
installation
quickstart
concepts
examples
API <api>
changelog
contributing
```

## Main Features

### Supported Celestial Bodies

Body                |   Symbol  |   Orb     |   Average Speed
--------------------|-----------|-----------|-------------------
Sun                 |   ☉       |  12°      |  0.986°/day
Moon                |   ☽       |  12°      |  13.176°/day
Mercury             |   ☿       |  8°       |  1.383°/day
Venus               |   ♀       |  8°       |  1.2°/day
Mars                |   ♂       |  10°      |  0.524°/day
Jupiter             |   ♃       |  10°      |  0.083°/day
Saturn              |   ♄       |  10°      |  0.034°/day
Uranus              |   ♅       |  6°       |  0.012°/day
Neptune             |   ♆       |  6°       |  0.007°/day
Pluto               |   ♇       |  4°       |  0.004°/day
Rahu (Mean Node)    |   ☊       |  0º       |  -0.013°/day
Lilith (Black Moon) |   ⚸       |  0º       |  -0.113°/day

### Major Aspects

Aspect      |   Angle   |   Symbol     |   Harmonic
------------|-----------|--------------|-------------
Conjunction |   0°      |   ☌          |   1
Semi-sextile|   30°     |   ⚺          |   1/6
Sextile     |   60°     |   ⚹          |   1/3
Square      |   90°     |   □          |   1/2
Trine       |   120°    |   △          |   2/3
Quincunx    |   150°    |   ⚻          |   5/6
Opposition  |   180°    |   ☍          |   1

## Quick Example

```python
from datetime import datetime
from zoneinfo import ZoneInfo
import ketu

# Create a date
paris = ZoneInfo("Europe/Paris")
dt = datetime(2020, 12, 21, 19, 20, tzinfo=paris)

# Calculate and display
jday = ketu.utc_to_julian(dt)
ketu.print_positions(jday)
ketu.print_aspects(jday)
```

## Indices and Tables

{ref}`genindex`

{ref}`search`

## License

MIT License - Copyright (c) 2021-2025 Loc Cosnier

## Contact

- Author: Loc Cosnier
- Email: <loc.cosnier@pm.me>
- GitHub: alkimya/ketu
- PyPI: pypi.org/project/ketu
