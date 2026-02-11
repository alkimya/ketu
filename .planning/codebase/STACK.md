# Technology Stack

**Analysis Date:** 2026-02-12

## Languages

**Primary:**
- Python 3.10+ - Core library (astronomical calculations, aspect analysis, cycles)
- Supported versions: 3.10, 3.11, 3.12, 3.13

## Runtime

**Environment:**
- CPython 3.10+
- Independent virtual environment: `ketu/venv/` (separate from Solaris workspace)

**Package Manager:**
- pip + setuptools
- Lockfile: No lock file; uses `pyproject.toml` (PEP 517/518)

## Frameworks & Core Libraries

**Core Scientific Computing:**
- NumPy >= 1.20.0 - Vectorized numerical operations, structured arrays, ephemeris calculations
  - Location: `ketu/ephemeris/` modules use NumPy exclusively
  - Performance: ~208x faster than legacy implementations

**Optional Visualization:**
- matplotlib >= 3.5.0 - Zodiacal chart SVG generation
  - Module: `ketu/export.py`
  - Installation: `pip install ketu[chart]`
  - Not a hard requirement; graceful fallback if missing

**Optional Calendar Export:**
- icalendar >= 5.0.0 - iCalendar (.ics) export for aspects/lunations
  - Module: `ketu/export.py`
  - Installation: `pip install ketu[icalendar]`
  - Not a hard requirement; graceful fallback if missing

**Testing & Quality:**
- pytest - Test runner
- pytest-cov - Code coverage reporting
- Coverage >= 7.13.1 - Coverage analysis (target tracking)

**Documentation:**
- Sphinx >= 7.0.0 - Documentation generation
- myst-parser >= 2.0.0 - Markdown support in Sphinx
- sphinx-rtd-theme >= 2.0.0 - ReadTheDocs Sphinx theme
- sphinx-autodoc-typehints >= 1.24.0 - Type hint documentation
- sphinx-copybutton >= 0.5.2 - Code block copy buttons
- sphinx-intl >= 2.1.0 - Internationalization (French documentation support)

**Development Tools:**
- setuptools >= 61.0 - Package building
- wheel - Distribution format
- build - PEP 517 build backend
- twine - PyPI upload tool

## Architecture Components

**Ephemeris (Pure NumPy Implementation):**
- Location: `ketu/ephemeris/` package
- Components:
  - `time.py` - UTC/Julian date conversions, sidereal time
  - `orbital.py` - Orbital element data, Kepler equation solver, planet position calculations
  - `coordinates.py` - Coordinate transformations (heliocentric→geocentric, ecliptic↔equatorial)
  - `planets.py` - High-level planetary position interface (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Rahu/Ketu, Lilith)
- **No external binary dependencies** (replaced pyswisseph in v0.3.0)
- Uses numpy for all mathematical operations

**Aspects & Cycles:**
- Location: `ketu/aspects/` package and `ketu/cycles/` package
- Components:
  - `aspects/core.py` - 14-aspect detection system (Conjunction, Opposition, Trine, Square, Sextile, Quintile, Novile, Decile, etc.)
  - `aspects/calculator.py` - Vectorized aspect calculation
  - `aspects/windows.py` - Precise aspect timing (beginning, exact, end)
  - `aspects/transits.py` - Transit calculations vs. natal positions
  - `cycles/calculator.py` - Vectorized cycle state calculation with complex number representation

**Complex Number Engine:**
- Location: `ketu/complex.py`
- Representation: `e^(iθ) = cos(θ) + i·sin(θ)` for zodiacal positions
- Provides: Phase-locking, circular statistics, ML-ready features
- Version: New in v0.4.0, fully vectorized with NumPy

**Lunar Calendar:**
- Location: `ketu/lunar_calendar.py`
- Generates lunar phase cycles (New Moon → Full Moon → New Moon)
- Structured arrays for batch processing

**Caching:**
- Location: `ketu/cache/ephemeris_cache.py`
- Storage: `.npy` (NumPy binary format) files in user's cache directory
- Performance: O(1) lookups (~0.01ms) vs. O(n) computation (~10ms)
- Scope: Pre-computes daily positions for all 13 bodies

**Export & Display:**
- Location: `ketu/export.py`, `ketu/display.py`
- CLI: `ketu` command (entry point in `ketu/display.py`)
- Optional chart generation (matplotlib)
- Optional iCalendar export (icalendar)

## Configuration Files

**Package Definition:**
- `pyproject.toml` - PEP 517 project metadata
  - Build system: setuptools + wheel
  - Dependencies: NumPy only (core)
  - Optional groups: `chart`, `icalendar`, `all`
  - Packages: `ketu`, `ketu.ephemeris`, `ketu.aspects`, `ketu.cycles`, `ketu.cache`, `ketu.export`

**Testing Configuration:**
- `pyproject.toml` [tool.pytest.ini_options]
  - Test paths: `tests/`
  - Test discovery: `test_*.py` files
  - Coverage: `--cov=ketu --cov-report=term-missing`
  - Exclude: `*/tests/*`

**Documentation Build:**
- `.readthedocs.yaml` - ReadTheDocs configuration
  - Build OS: ubuntu-22.04
  - Python: 3.12
  - Sphinx config: `docs/en/conf.py` (primary), `docs/fr/conf.py` (French)
  - Output formats: HTML, PDF, EPUB
  - Post-install: Build French docs alongside English

**CI/CD:**
- `.github/workflows/tests.yml` - Manual test workflow (disabled by default)
  - Runs: Python 3.10, 3.11, 3.12, 3.13
  - Coverage upload: Codecov (Python 3.12)
- `.github/workflows/publish.yml` - Manual PyPI publish workflow
  - Test PyPI for pre-release tags (rc, beta)
  - Production PyPI for stable tags

## Platform Requirements

**Development:**
- Python 3.10+ (tested 3.10-3.13)
- pip/setuptools
- ~500MB virtual environment (with test dependencies)

**Production:**
- Python 3.10+
- NumPy >= 1.20.0
- Optional: matplotlib, icalendar

**Documentation:**
- ReadTheDocs-compatible Sphinx setup
- Builds on Ubuntu 22.04 with Python 3.12

## Key Numerical Libraries

**NumPy Vectorization:**
- Structured arrays for batch ephemeris calculations
- Broadcasting for parallel aspect detection
- Complex number representation (1000x speedup vs. angle arithmetic)
- Example: `calc_planet_position_batch()` computes all 13 bodies for 10K timestamps in seconds

**Linear Algebra:**
- Rotation matrices for coordinate transformations (ecliptic→equatorial)
- Spherical→rectangular coordinate conversions

## Performance Characteristics

**Computation:**
- Single position: ~1ms (NumPy)
- Time series (10K timestamps, 1 body): ~10ms
- Time series (10K timestamps, 13 bodies): ~130ms
- Aspect detection (vectorized): 208x faster than legacy
- Cache lookup (1000 cached days): ~0.01ms per query

**Memory:**
- Cache per month: ~19 KB (13 bodies × 31 days × 6 floats)
- Cache per year: ~230 KB
- Structured array overhead: Minimal (binary format)

---

*Stack analysis: 2026-02-12*
