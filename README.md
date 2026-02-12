# Ketu

[![PyPI version](https://badge.fury.io/py/ketu.svg)](https://badge.fury.io/py/ketu)
[![Python Versions](https://img.shields.io/pypi/pyversions/ketu.svg)](https://pypi.org/project/ketu/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Ketu** is a pure NumPy library for astronomical calculations focused on planetary positions, aspects, and cycle analysis. With no dependencies beyond NumPy, Ketu provides fast, accurate calculations suitable for astrology, biodynamic calendars, and machine learning applications.

This library was originally designed to generate biodynamic calendars and time series based on astrological aspects. It can be used as a basis for building astrology software.

![Terminal screen](https://github.com/alkimya/ketu/blob/main/res/screen.png)

## What's New in v1.0.0

**Major release with breaking changes. See [UPGRADING.md](UPGRADING.md) and [CHANGELOG.md](CHANGELOG.md) for migration guide.**

- **Pure calculation library** - NumPy-only dependency, no visualization or export modules
- **Correctness fixes** - Cache operator precedence bug, aspect vectorization non-determinism, Moon velocity wrapping
- **Explicit API** - Velocity functions renamed (`vlong()` → `long_velocity()`), pandas dependency removed
- **Type hints everywhere** - mypy strict mode compliance
- **Comprehensive docstrings** - NumPy-style documentation with Examples sections
- **98% test coverage** - 408 tests across all modules
- **Performance improvements** - Vectorized batch ephemeris calculations

## Features

- **Planetary positions** for 13 bodies (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Rahu/Mean Node, True North Node, Lilith)
- **Detection of 14 major/minor aspects** (Conjunction, Opposition, Trine, Square, Sextile, Quintile, Novile, Decile, etc.)
- **Aspect windows** - Find when aspects begin, peak, and end
- **Transit calculations** - Track transits to natal positions
- **Retrogradation detection** and planet motion helpers
- **Time system conversions** (UTC, Julian Day)
- **Orb system** based on Abu Ma'shar (787-886) and Al-Biruni (973-1050)
- **Interactive CLI** for a non-programmatic workflow
- **Python API** that fits into your own tooling
- **Pure NumPy** - Single dependency for maximum portability and performance

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

## Advanced Examples

### Compute a planet position

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

### Check whether a planet is retrograde

```python
import ketu

# Mars (body id = 4)
if ketu.is_retrograde(jday, 4):
    print("Mars is retrograde")
else:
    print("Mars is direct")
```

### Find aspect windows

```python
from datetime import datetime, timedelta
import ketu

# Find Sun-Moon conjunction window
start = ketu.utc_to_julian(datetime(2025, 1, 1, tzinfo=ZoneInfo("UTC")))
end = ketu.utc_to_julian(datetime(2025, 12, 31, tzinfo=ZoneInfo("UTC")))

windows = ketu.find_aspect_window(start, end, body1=0, body2=1, aspect=0)

for window in windows:
    print(f"Conjunction from {ketu.julian_to_utc(window.begin_jd)} "
          f"to {ketu.julian_to_utc(window.end_jd)}")
    print(f"  Exact: {ketu.julian_to_utc(window.exact_jd)}")
```

### Calculate transits to natal positions

```python
import ketu

# Natal positions
natal_date = ketu.utc_to_julian(datetime(1990, 1, 15, 12, 0, tzinfo=ZoneInfo("UTC")))
natal_positions = ketu.get_natal_positions(natal_date)

# Find transits for a specific date
transit_date = ketu.utc_to_julian(datetime(2025, 11, 22, 12, 0, tzinfo=ZoneInfo("UTC")))
transits = ketu.compare_dates_transits(natal_positions, transit_date)

for transit in transits:
    print(f"{transit.transiting_body} {transit.aspect} natal {transit.natal_body}")
```

### Ephemeris Cache (v0.4.0)

For ML pipelines and high-frequency lookups, use the ephemeris cache for 1000x faster position lookups:

```python
from ketu.cache import EphemerisCache
from datetime import datetime, timezone

# Initialize cache (stores in ~/.ketu/ephemeris_cache/)
cache = EphemerisCache()

# Pre-compute a range of months (one-time operation)
# ~1-2 seconds per month, persisted to disk
for year in range(2020, 2026):
    for month in range(1, 13):
        cache.ensure_month(year, month)

# Fast O(1) lookups (0.006ms vs 10ms computation)
timestamp = datetime(2025, 6, 15, 14, 30, tzinfo=timezone.utc)

# Get single body position (lon, lat, distance, speed)
sun_pos = cache.get_position(timestamp, body_id=0)
print(f"Sun longitude: {sun_pos[0]:.2f}°")

# Get all 13 bodies at once
all_positions = cache.get_all_positions(timestamp)
# Returns dict: {body_id: (lon, lat, dist, speed), ...}
```

**CLI for pre-computing cache:**

```bash
# Pre-compute 2020-2030 (takes ~3-4 minutes)
python scripts/precompute_ephemeris.py --years 2020-2030

# Single year
python scripts/precompute_ephemeris.py --year 2025

# Force recompute
python scripts/precompute_ephemeris.py --year 2025 --force
```

**Performance:**

- Lookup: 0.006ms (with interpolation)
- Compute: 10ms
- Speedup: **1000x**
- Disk usage: ~50KB per month

## Documentation

The full documentation is hosted on [Read the Docs](https://ketu.readthedocs.io).

Included sections:

- **Installation**: detailed setup instructions
- **Quickstart**: guided tour of the basics
- **Concepts**: astrological and astronomical background
- **API Reference**: all functions documented
- **Examples**: advanced usage patterns
- **Developer Guide**: architecture and performance details

## Requirements

- Python 3.10 or higher
- `numpy` ≥ 1.20.0 — numerical routines and arrays

**That's it!** Ketu has no other dependencies.

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

## Performance

The pure NumPy implementation provides excellent performance:

- **Time series (365 days)**: 208x faster than loop-based approach
- **Aspect calculations**: 14.55x faster with vectorization
- **Single planet position**: 67x faster with optimized algorithms
- **Moon position**: 59x faster with custom perturbation calculations

See [docs/en/performance.md](docs/en/performance.md) for detailed benchmarks.

## Accuracy

The implementation provides good accuracy for astrological purposes:

- **Planetary positions**: ±0.1° for inner planets, ±0.5° for outer planets
- **Moon position**: ±0.5° (includes major perturbations)
- **Aspect timing**: ±2 minutes for exact aspects
- **Best accuracy range**: 1800-2200 CE

## Architecture

```text
ketu/
├── __init__.py          # Main API
├── core.py              # Data structures (bodies, aspects, signs)
├── calculations.py      # High-level calculation functions
├── display.py           # CLI and display utilities
├── aspect_windows.py    # Aspect timing calculations
├── transits.py          # Transit calculations
├── cache/               # High-performance ephemeris cache
│   ├── __init__.py
│   └── ephemeris_cache.py  # Monthly pre-computed positions
└── ephemeris/           # Astronomical calculations
    ├── time.py          # Time conversions
    ├── orbital.py       # Orbital mechanics
    ├── coordinates.py   # Coordinate transformations
    └── planets.py       # Planetary position calculations
```

## Roadmap

- [x] Removal of dependency on pyswisseph
- [x] Pure numpy implementation of planetary calculations
- [x] Search for exact aspects between two dates
- [x] Aspect windows and timing
- [x] Transit calculations
- [x] High-performance ephemeris cache
- [x] Complex number engine for cycle analysis

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

## Acknowledgments

- **[solarsystem](https://github.com/IoannisNasios/solarsystem)** by Ioannis Nasios — The pure Python astronomy library that inspired and served as the mathematical foundation for Ketu's NumPy ephemeris engine. Kepler's equation solver, perturbation terms, coordinate transformations, and Moon calculations all trace back to this elegant, dependency-free library. Thank you!
- **[Claude](https://claude.ai)** by Anthropic — The pure NumPy rewrite, from orbital mechanics to aspect detection, was developed in collaboration with Claude. Architecture, algorithms, tests, documentation were produced through extensive pair programming sessions.
- **[GSD (Get Shit Done)](https://github.com/gsd-build/get-shit-done)** — The project management workflow that structured the development of Ketu v1.0.0 into phases with research, planning, execution, and verification steps.
- Original orbital calculations based on Paul Schlyter's work
- Inspired by the accuracy and reliability of Swiss Ephemeris
- Built with the power of NumPy for scientific computing
