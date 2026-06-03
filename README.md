# Ketu

[![PyPI version](https://badge.fury.io/py/ketu.svg)](https://badge.fury.io/py/ketu)
[![Python Versions](https://img.shields.io/pypi/pyversions/ketu.svg)](https://pypi.org/project/ketu/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Ketu** is a pure NumPy library for astronomical calculations focused on planetary positions, aspects, and cycle analysis. With no dependencies beyond NumPy, Ketu provides fast, accurate calculations suitable for astrology, biodynamic calendars, and machine learning applications.

This library was originally designed to generate biodynamic calendars and time series based on astrological aspects. It can be used as a basis for building astrology software.

![Terminal screen](https://github.com/alkimya/ketu/blob/main/res/screen.png)

## What's New in v1.4.0

Ketu v1.4.0 introduces a dynamic harmonic aspect generator and expands the Chiron
ephemeris to 1900–2100. There are two behavioural changes: Chiron now forms scored
aspects (orb raised from 0° to 4°) and out-of-range Chiron inputs are silently clamped
instead of raising `ValueError`. See [UPGRADING.md](UPGRADING.md) for migration recipes
and [CHANGELOG.md](CHANGELOG.md) for the full list of changes.

- **Dynamic harmonic generator** — `ketu.aspects.generate_harmonic_aspects(h)` builds
  aspect specs on the fly for any integer harmonic 2 ≤ h ≤ 64 (full-circle 360°
  folded to 0–180°, `coef = k/h`). Pass the result as `dynamic_specs=` to
  `calculate_aspects`, `find_aspects_between_dates`, or `calculate_synastry`. The
  frozen 14-row `core.aspects` table and preset fingerprints are byte-identical.
- **Chiron range 1900–2100** — `ketu/data/chiron_coeffs.npz` regenerated (2283
  Chebyshev segments, max error 0.001214°, ~578 KB). `calc_planet_position(jd, 13)`
  now resolves any JD in the expanded range with no code changes required.
- **Chiron orb 4°** — `core.bodies['orb']` for Chiron is now 4° (Pluto parity).
  Chiron forms scored aspects in all detection functions. Downstream code that assumed
  zero Chiron aspects must adapt (see UPGRADING.md → "v1.3 -> v1.4").

---

## What's New in v1.3.0

Ketu v1.3.0 adds Chiron as the 14th body and makes the aspect engine
data-driven. The public API is additive; the one breaking change is the
internal positional-array contract (the bodies axis goes 13 → 14) and the
aspect default/coefficient/preset surface. See [UPGRADING.md](UPGRADING.md)
for migration recipes and [CHANGELOG.md](CHANGELOG.md) for the full list.

- **Chiron** — the 14th body (`body_id = 13`), evaluated from embedded
  Chebyshev-by-segment coefficients in **pure NumPy** (no `pyswisseph`,
  no SciPy, no new runtime dependency). `ketu.calc_planet_position(jd, 13)`
  returns Chiron's longitude within ~0.006° of Swiss Ephemeris across
  1950–2050. Chiron participates in `compute_chart`, aspect detection,
  and the cycle machinery like any other body.
- **Data-driven aspect engine** — aspects now live in a single declarative
  table (`name, angle, coef, harmonic, symbol`); the detection logic
  iterates over it with no per-aspect hardcoding. Compose a set from
  harmonics with `aspects_for_harmonics([1, 2, 3, 6])`, or use the
  `CLASSICAL` / `TRADITIONAL` / `EXTENDED` presets.
- **New default aspect set (breaking)** — the library default is now the
  7 half-circle harmonics (H1/H2/H3/H6: Conjunction, Semi-sextile, Sextile,
  Square, Trine, Quincunx, Opposition). The full-circle minors
  (quintile, novile, decile, and friends — H5/H9/H10) are opt-in. The CLI
  stays pinned to the classical 5 for byte-stable output.
- **Full French documentation** — every Sphinx page is now fully
  translated to French through the gettext pipeline.

## What's New in v1.2.0

Ketu v1.2.0 is a non-breaking feature release — all v1.1 code works
unchanged. See [UPGRADING.md](UPGRADING.md) for opt-in migration recipes
and [CHANGELOG.md](CHANGELOG.md) for the full list of changes.

- **Synastry** — `ketu.synastry.calculate_synastry(chart_a, chart_b)`
  returns a `SYNASTRY_DTYPE` cross-product of inter-chart aspects (15
  bodies × 15 bodies = 225 pairs; `filtered` and `dense` modes).
  Astrodienst-style orbs (0.5× tightening). CLI `ketu synastry`;
  `ketu --list-orbs`.
- **Composite charts** — `ketu.composite.calculate_composite(chart_a,
  chart_b)` returns a `CHART_DTYPE` midpoint composite. Helper
  `circular_midpoint(lon_a, lon_b)` with pinned regression
  `mid(359°, 1°) == 0°`.
- **Solar and Lunar Returns** — `ketu.returns.solar_return(...,
  target_year=<int>)` and `ketu.returns.lunar_return(...,
  target_jd=<float>)` with arc-second convergence and optional
  relocation (`return_lat`/`return_lon`). API asymmetry: solar takes
  an integer year, lunar takes a Julian Date.
- **Arabic Parts** — `ketu.parts.calculate_part(name, chart)` with
  sect-aware dispatch (Fortune / Spirit) and fixed Marriage formula;
  `calculate_all_parts(chart)` dict; `ketu --list-parts`.
- **Three new house systems** — Whole Sign (`"whole_sign"`), Equal
  (`"equal"`), Regiomontanus (`"regiomontanus"`) registered in
  `ketu.houses.SYSTEMS`. `ketu --list-house-systems` now returns
  six entries.
- **CI doc gates hardened** — `interrogate ≥95%` and `numpydoc
  validate` are both fully blocking; `make doc-gates` runs them
  locally. 214 pre-existing GL01 violations fixed.
- **GitHub Actions workflow refresh** — Node.js 24 actions
  (`checkout@v5`, `setup-python@v6`, `upload-artifact@v5`); all
  Node 20 deprecation warnings eliminated.

For the full list of changes see [CHANGELOG.md](CHANGELOG.md).

## Features

- **Planetary positions** for 14 bodies (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Rahu/Mean Node, True North Node, Lilith, Chiron)
- **Data-driven aspect engine** — a declarative table of 14 major/minor aspects (Conjunction, Opposition, Trine, Square, Sextile, Quincunx, ... through Quintile, Novile, Decile); harmonic-based selection via `aspects_for_harmonics([...])`. The default set is the 7 half-circle aspects; full-circle minors are opt-in.
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

# Get all 14 bodies at once
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

### Documentation Quality Gates

Documentation quality is enforced by CI on every push:

- **`interrogate ≥95%`** (blocking) — every public function, class, and module has a docstring.
- **`numpydoc validate`** (warning, blocking from v1.2.0) — docstrings follow the NumPy convention.

Run both locally before pushing: `make doc-gates`.

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
| Chiron | 13 | 0° | 0.019 |

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

These 7 half-circle aspects (harmonics 1, 2, 3, 6) are the library default.
The full table also carries 7 full-circle minor aspects (Quintile, Decile,
Novile, Binovile, Quadrinovile, Biquintile, Tredecile — harmonics 5, 9, 10),
which are opt-in via `aspects_for_harmonics([...])` or the `EXTENDED` preset.

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
├── complex.py           # Complex-number engine for cycle analysis
├── display.py           # Display utilities
├── lunar_calendar.py    # Biodynamic / lunar calendar helpers
├── aspects/             # Data-driven aspect engine (presets, harmonics)
├── charts/              # compute_chart / CHART_DTYPE abstraction
├── houses/              # Six house systems (Placidus, Whole Sign, ...)
├── synastry/            # Inter-chart aspect cross-products
├── composite/           # Midpoint composite charts
├── returns/             # Solar and lunar returns
├── parts/               # Arabic Parts framework
├── cycles/              # Planetary cycle series (NumPy structured arrays)
├── cli/                 # Interactive command-line interface
├── cache/               # High-performance ephemeris cache
├── data/                # Embedded Chiron Chebyshev coefficients (.npz)
└── ephemeris/           # Astronomical calculations
    ├── time.py          # Time conversions
    ├── orbital.py       # Orbital mechanics (re-export hub)
    ├── coordinates.py   # Coordinate transformations
    ├── planets.py       # Planetary position calculations (per-body strategies)
    └── chiron.py        # Pure-NumPy Chiron Chebyshev evaluator
```

## Roadmap

- [x] Removal of dependency on pyswisseph
- [x] Pure numpy implementation of planetary calculations
- [x] Search for exact aspects between two dates
- [x] Aspect windows and timing
- [x] Transit calculations
- [x] High-performance ephemeris cache
- [x] Complex number engine for cycle analysis
- [x] Configurable aspects and six house systems
- [x] Chart abstraction (`compute_chart` / `CHART_DTYPE`)
- [x] Relational charts (synastry, midpoint composite)
- [x] Predictive charts (solar and lunar returns)
- [x] Arabic Parts framework
- [x] Chiron as the 14th body (pure-NumPy Chebyshev evaluation)
- [x] Data-driven aspect engine with harmonic-based selection

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
