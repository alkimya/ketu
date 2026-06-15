# Ketu Documentation

**Ketu** is a Python library for calculating planetary positions and planetary aspects using pure NumPy.

The library was originally designed to produce biodynamic calendars and time series driven by planetary aspects, and it can serve as a foundation for building astrology software.

## Overview

Ketu allows you to:

- Calculate precise positions of celestial bodies (Sun, Moon, planets, Nodes, Lilith, Chiron)
- Determine aspects between planets with configurable aspect sets (Classical, Traditional, Extended)
- Convert between different time systems (UTC, Julian)
- Identify retrogradations and zodiac signs
- Calculate astrological house systems (Placidus, Koch, Porphyry, Whole Sign, Equal, Regiomontanus)
- Compute full natal charts as structured NumPy arrays (CHART_DTYPE)
- Analyse synastry and composite (midpoint) charts between two individuals
- Calculate solar and lunar returns for predictive astrology
- Compute Arabic Parts / Hermetic Lots (Fortune, Spirit, Marriage)
- Generate time series of aspects

## Navigation

```{toctree}
:maxdepth: 2
:caption: User Guide
installation
quickstart
concepts
examples
houses
relational_charts
predictive_charts
arabic_parts
chiron
API <api>
changelog
```

```{toctree}
:maxdepth: 2
:caption: Developer Guide
migration
architecture
performance
contributing
acknowledgments
```

## Main Features

### Supported Celestial Bodies

Body                   | Symbol | Orb | Average Speed
-----------------------|--------|-----|---------------
Sun                    | ☉      | 12° | 0.986°/day
Moon                   | ☽      | 12° | 13.176°/day
Mercury                | ☿      | 8°  | 1.383°/day
Venus                  | ♀      | 10° | 1.2°/day
Mars                   | ♂      | 8°  | 0.524°/day
Jupiter                | ♃      | 10° | 0.083°/day
Saturn                 | ♄      | 10° | 0.034°/day
Uranus                 | ♅      | 6°  | 0.012°/day
Neptune                | ♆      | 6°  | 0.007°/day
Pluto                  | ♇      | 4°  | 0.004°/day
Rahu (Mean Node)       | ☊      | 2°  | -0.052954°/day
Ketu (Mean South Node) | ☋      | 2°  | -0.052954°/day
Lilith (Black Moon)    | ⚸      | 2°  | 0.113°/day
Chiron                 | ⚷      | 4°  | ~0.018°/day

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
from ketu.ephemeris.time import utc_to_julian
from ketu.display import print_positions, print_aspects

# Create a date
paris = ZoneInfo("Europe/Paris")
dt = datetime(2020, 12, 21, 19, 20, tzinfo=paris)

# Calculate and display
jday = utc_to_julian(dt)
print_positions(jday)
print_aspects(jday)
```

## Indices and Tables

{ref}`genindex`

{ref}`search`

## License

MIT License - Copyright (c) 2021-2026 Loc Cosnier

## Contact

- Author: Loc Cosnier
- Email: <loc.cosnier@pm.me>
- GitHub: alkimya/ketu
- PyPI: pypi.org/project/ketu
