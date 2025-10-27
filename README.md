# Ketu

[![PyPI version](https://badge.fury.io/py/ketu.svg)](https://badge.fury.io/py/ketu)
[![Python Versions](https://img.shields.io/pypi/pyversions/ketu.svg)](https://pypi.org/project/ketu/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Vous préférez le français ? [Consultez README.md](fr/README.md)

**Ketu** is a lightweight Python library for computing the positions of astronomical bodies (Sun, Moon, planets, and the mean Node a.k.a. Rahu) and generating calendars driven by astrological aspects.

This library was originally designed to generate biodynamic calendars and time series based on astrological aspects. It can be used as a basis for building astrology software.

![Terminal screen](https://github.com/alkimya/ketu/blob/main/res/screen.png)

## Features

- **Planetary positions** for 13 bodies (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Rahu/Mean Node, True North Node, Lilith)
- **Detection of the 7 major aspects** (Conjunction, Semi-sextile, Sextile, Square, Trine, Quincunx, Opposition)
- **Retrogradation detection** and planet motion helpers
- **Time system conversions** (UTC, Julian Day)
- **Orb system** based on Abu Ma'shar (787-886) and Al-Biruni (973-1050)
- **Interactive CLI** for a non-programmatic workflow
- **Python API** that fits into your own tooling

## Installation

### From PyPI (recommended)

```bash
pip install ketu
```

### From source

```bash
git clone https://github.com/alkimya/ketu.git
cd ketu
pip install -e .
```

## Quick Start

### Interactive mode (CLI)

Run the command below and answer the prompts:

```bash
ketu
```

You will be asked for:

- A date (ISO format: `2020-12-21`)
- A time (ISO format: `19:20`)
- A timezone (for example `Europe/Paris`)

The program prints:

- Positions of every celestial body with zodiac signs
- All inter-planet aspects with their orbs

### Programmatic usage

```python
from datetime import datetime
from zoneinfo import ZoneInfo
import ketu

# Define a datetime
dtime = datetime(2020, 12, 21, 19, 20, tzinfo=ZoneInfo("Europe/Paris"))
jday = ketu.utc_to_julian(dtime)

# Display planetary positions
ketu.print_positions(jday)

# Display aspects
ketu.print_aspects(jday)
```

### Additional examples

#### Compute a planet position

```python
from datetime import datetime
from zoneinfo import ZoneInfo
import ketu

dtime = datetime(2024, 10, 26, 12, 0, tzinfo=ZoneInfo("UTC"))
jday = ketu.utc_to_julian(dtime)

sun_long = ketu.long(jday, 0)
print(f"Sun longitude: {sun_long:.2f}°")

sign, deg, mins, secs = ketu.body_sign(sun_long)
print(f"Position: {ketu.signs[sign]} {deg}°{mins}'{secs}\"")
```

#### Check whether a planet is retrograde

```python
import ketu

# Mars (body id = 4)
if ketu.is_retrograde(jday, 4):
    print("Mars is retrograde")
else:
    print("Mars is direct")
```

#### Calculate all aspects for a given day

```python
import ketu

aspects_data = ketu.calculate_aspects(jday)

for aspect in aspects_data:
    body1, body2, i_asp, orb = aspect
    print(f"{ketu.body_name(body1)} - {ketu.body_name(body2)}: "
          f"{ketu.aspects['name'][i_asp].decode()} (orb: {orb:.2f}°)")
```

## Documentation

The full documentation is hosted on [Read the Docs](https://ketu.readthedocs.io) (French by default, English via the language toggle).

Included sections:

- **Installation**: detailed setup instructions
- **Quickstart**: guided tour of the basics
- **Concepts**: astrological and astronomical background
- **API Reference**: all functions documented
- **Examples**: advanced usage patterns

## Requirements

- Python 3.10 or higher
- `numpy` ≥ 1.20.0 — numerical routines and arrays
- `pyswisseph` ≥ 2.10.0 — Swiss Ephemeris bindings

> The dependency on `pyswisseph` is scheduled for removal in a future release, replaced by pure NumPy implementation.

## Supported bodies

| Body | ID | Orb | Average speed (°/day) |
|------|----|-----|-----------------------|
| Sun | 0 | 12° | 0.986 |
| Moon | 1 | 12° | 13.176 |
| Mercury | 2 | 8° | 1.383 |
| Venus | 3 | 10° | 1.200 |
| Mars | 4 | 8° | 0.524 |
| Jupiter | 5 | 10° | 0.083 |
| Saturn | 6 | 10° | 0.034 |
| Uranus | 7 | 6° | 0.012 |
| Neptune | 8 | 6° | 0.007 |
| Pluto | 9 | 4° | 0.004 |
| Rahu (Mean Node) | 10 | 0° | -0.013 |
| True North Node | 11 | 0° | -0.013 |
| Lilith (Black Moon) | 12 | 0° | -0.113 |

## Supported aspects

| Aspect | Angle | Orb coefficient |
|--------|-------|-------------------|
| Conjunction | 0° | 1 |
| Semi-sextile | 30° | 1/6 |
| Sextile | 60° | 1/3 |
| Square | 90° | 1/2 |
| Trine | 120° | 2/3 |
| Quincunx | 150° | 5/6 |
| Opposition | 180° | 1 |

## Roadmap

- [ ] Removal of dependency on pyswisseph
- [ ] Pure numpy implementation of planetary calculations
- [ ] Search for exact aspects between two dates
- [ ] Generation of aspect calendars
- [ ] API for progressions and directions
- [ ] Support for more celestial bodies (asteroids, etc.)

## Contribution

Contributions are welcome! Feel free to:

- Open an issue to report a bug or suggest a feature
- Submit a pull request
- Improve the documentation

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## License

This project is licensed under MIT. See the [LICENSE](LICENSE) file for more details.

## Contact

Loc Cosnier - [@alkimya](https://github.com/alkimya)

Project: [https://github.com/alkimya/ketu](https://github.com/alkimya/ketu)
