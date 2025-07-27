# ketu (v2.0) - Pure NumPy Implementation

A Python library to compute positions of astronomical bodies (Sun, Moon, planets and mean Node aka Rahu), generate time series and calendars based on planetary aspects.

## 🚀 What's New in v2.0

- **No more external dependencies!** Removed `pyswisseph` dependency
- **Pure NumPy implementation** - All calculations using NumPy
- **New features implemented:**
  - Find exact aspect timing (beginning, exact, end)
  - Find all aspects between two dates
  - Equation of time calculations
- **Improved architecture** with modular ephemeris package
- **Better performance** for bulk calculations
- **Fully transparent** and customizable calculations

## 📋 Requirements

- Python 3.9+
- NumPy: `pip install numpy`

That's it! No more binary dependencies or platform-specific installations.

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/alkimya/ketu.git
cd ketu

# Install dependencies
pip install numpy

# Run the interactive demo
python ketu/ketu_refactored.py
```

## 🌟 Features

### Core Functionality

- Calculate planetary positions for any date/time
- Detect planetary aspects with orbs
- Identify retrograde motion
- Convert between coordinate systems
- Support for tropical zodiac signs

### Celestial Bodies Supported

- ☉ Sun
- ☽ Moon  
- ☿ Mercury
- ♀ Venus
- ♂ Mars
- ♃ Jupiter
- ♄ Saturn
- ♅ Uranus
- ♆ Neptune
- ♇ Pluto
- ☊ Rahu (Mean Node)
- ☊ North Node (True Node)
- ⚸ Lilith (Mean Apogee)

### Aspects Detected

- Conjunction (0°)
- Semi-sextile (30°)
- Sextile (60°)
- Square (90°)
- Trine (120°)
- Quincunx (150°)
- Opposition (180°)

## 📖 Usage

### Basic Example

```python
from datetime import datetime
from zoneinfo import ZoneInfo
from ketu.ketu_refactored import (
    utc_to_julian, positions, calculate_aspects, 
    print_positions, print_aspects
)

# Create a timezone-aware datetime
paris_tz = ZoneInfo("Europe/Paris")
dt = datetime(2020, 12, 21, 19, 20, 0, tzinfo=paris_tz)

# Convert to Julian Date
jd = utc_to_julian(dt)

# Get all planetary positions
planet_positions = positions(jd)

# Calculate all aspects
aspects = calculate_aspects(jd)

# Pretty print results
print_positions(jd)
print_aspects(jd)
```

### Find Exact Aspect Timing

```python
from ketu.ketu_refactored import find_aspect_timing, body_id

# Find Sun-Moon conjunction timing
sun = body_id("Sun")
moon = body_id("Moon")

begin_jd, exact_jd, end_jd = find_aspect_timing(jd, sun, moon, 0.0)

# Convert to regular dates
from ketu.ephemeris import julian_to_utc
print(f"Aspect begins: {julian_to_utc(begin_jd)}")
print(f"Exact aspect: {julian_to_utc(exact_jd)}")
print(f"Aspect ends: {julian_to_utc(end_jd)}")
```

### Find Aspects Between Dates

```python
from ketu.ketu_refactored import find_aspects_between_dates

# Find all aspects in a month
start_date = datetime(2020, 12, 1, 0, 0, tzinfo=ZoneInfo("UTC"))
end_date = datetime(2020, 12, 31, 23, 59, tzinfo=ZoneInfo("UTC"))

jd_start = utc_to_julian(start_date)
jd_end = utc_to_julian(end_date)

# Find all Sun-Moon aspects
aspects = find_aspects_between_dates(jd_start, jd_end, sun, moon)

for exact_jd, body1, body2, aspect_name, angle in aspects:
    print(f"{julian_to_utc(exact_jd)}: {aspect_name} at {angle}°")
```

## 🏗️ Architecture

```
ketu/
├── ketu_refactored.py   # Main API (backward compatible)
├── ephemeris/           # Astronomical calculations
│   ├── __init__.py     
│   ├── time.py         # Time conversions & equation of time
│   ├── orbital.py      # Orbital mechanics & Kepler's equations
│   ├── coordinates.py  # Coordinate transformations
│   └── planets.py      # High-level planetary calculations
└── tests/
    └── test_refactored.py  # Validation tests
```

## 🔄 Migration from v1.x (pyswisseph)

If you're upgrading from the pyswisseph version:

1. The high-level API remains the same
2. Remove `pyswisseph` from requirements
3. Update imports to use `ketu_refactored`
4. See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for details

## 🎯 Accuracy

The pure NumPy implementation provides good accuracy for astrological purposes:

- **Planetary positions**: ±0.1° for inner planets, ±0.5° for outer planets  
- **Moon position**: ±0.5° (includes major perturbations)
- **Aspect timing**: ±2 minutes for exact aspects
- **Best accuracy range**: 1800-2200 CE

## 🚦 Running Tests

```bash
cd ketu
python tests/test_refactored.py
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional perturbation terms for higher accuracy
- More celestial bodies (asteroids, centaurs)
- Traditional astrology features (houses, lots)
- Performance optimizations
- Additional coordinate systems

## 📄 License

MIT License, see [LICENSE](LICENSE)

## 🙏 Acknowledgments

- Original orbital calculations based on Paul Schlyter's work
- Inspired by the accuracy and reliability of Swiss Ephemeris
- Built with the power of NumPy for scientific computing

## 📮 Contact

Loc Cosnier <loc.cosnier@pm.me>

---

*Note: This is a refactored version that removes the pyswisseph dependency. For the original version, see the v1.x branch.*
