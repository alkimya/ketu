# Codebase Structure

**Analysis Date:** 2026-02-12

## Directory Layout

```
ketu/
├── ketu/                           # Main package source
│   ├── __init__.py                 # Public API exports (~60+ functions/classes)
│   ├── __main__.py                 # Module entry point
│   ├── core.py                     # Core data structures (bodies, aspects, signs)
│   ├── calculations.py             # Position/velocity calculations (cached)
│   ├── display.py                  # CLI and formatted output functions
│   ├── lunar_calendar.py           # Lunar cycle calendar generation
│   ├── complex.py                  # Complex number representation (ML features)
│   ├── resonance.py                # Resonance field calculations
│   │
│   ├── ephemeris/                  # Low-level ephemeris calculations
│   │   ├── __init__.py
│   │   ├── time.py                 # Julian day conversions, delta-T
│   │   ├── orbital.py              # Orbital elements, Kepler equation, perturbations
│   │   ├── planets.py              # Body position calculations, batch operations
│   │   └── coordinates.py          # Coordinate transformations
│   │
│   ├── aspects/                    # Aspect event detection and analysis
│   │   ├── __init__.py             # Module exports
│   │   ├── core.py                 # Low-level algorithms (binary search, caching)
│   │   ├── calculator.py           # High-level aspect API
│   │   ├── windows.py              # Aspect window detection (entry/exit/exact)
│   │   ├── timelines.py            # ML-ready aspect timelines
│   │   └── transits.py             # Transit calculations (transit to natal)
│   │
│   ├── cycles/                     # Continuous cycle state calculations
│   │   ├── __init__.py             # Module exports
│   │   └── calculator.py           # CycleState, CYCLE_DTYPE, generate_cycle_series
│   │
│   ├── cache/                      # Optional ephemeris caching layer
│   │   ├── __init__.py
│   │   └── ephemeris_cache.py      # EphemerisCache, pre-computed daily positions
│   │
│   └── export/                     # Optional output formats (matplotlib, iCal)
│       ├── __init__.py             # Graceful degradation for optional deps
│       ├── chart.py                # SVG/matplotlib chart generation
│       ├── icalendar.py            # iCalendar export
│       └── constants.py            # BIG_FIVE, display constants
│
├── tests/                          # 16 test modules, 176 tests passing
│   ├── test_ketu.py                # Core data structures, time, positions, aspects
│   ├── test_complex.py             # Complex number representation
│   ├── test_vectorization.py       # Vectorized operations
│   ├── test_aspects_vectorization.py # Aspect vectorization
│   ├── test_aspect_windows.py      # Aspect window detection
│   ├── test_aspect_timelines.py    # ML-ready aspect timelines
│   ├── test_transits.py            # Transit calculations
│   ├── test_lunar_calendar_performance.py # Lunar calendar generation
│   ├── test_time_functions.py      # Time conversion edge cases
│   ├── test_coverage_improvements.py # Coverage expansion tests
│   ├── test_refactored.py          # Refactored code validation
│   ├── test_direct_new_moon.py     # Direct new moon detection
│   ├── test_multi_moments.py       # Multiple aspect moments
│   ├── benchmark.py                # Performance benchmarks
│   ├── benchmark_aspect_window.py  # Aspect window benchmarks
│   └── __init__.py
│
├── docs/                           # Documentation
│   ├── source/                     # Sphinx documentation source
│   │   ├── conf.py
│   │   ├── api.md
│   │   ├── concepts.md
│   │   └── ...
│   └── ...
│
├── examples/                       # Usage examples
│   └── ...
│
├── benchmarks/                     # Benchmark scripts
│   └── ...
│
├── res/                            # Resources (icons, etc)
├── scripts/                        # Development scripts
├── fr/                             # French documentation
│
├── pyproject.toml                  # Project metadata, dependencies, entry point
├── CLAUDE.md                       # Ketu-specific developer instructions
├── CHANGELOG.md                    # Version history
├── CONTRIBUTING.md                # Contribution guidelines
├── LICENSE                         # MIT license
├── MANIFEST.in                     # Package manifest
├── README.md                       # Project overview
├── .readthedocs.yaml              # ReadTheDocs configuration
├── .github/                        # GitHub CI/workflows
├── .pytest_cache/                  # pytest cache
├── .coverage                       # coverage.py data
├── venv/                           # Independent virtual environment (separate from Solaris)
└── .git/                           # Git repository
```

## Directory Purposes

**ketu/**
- Purpose: Main source package with modular subpackages
- Contains: 28 Python modules across 7 subpackages
- Key files: `__init__.py` (public API), `core.py` (constants), `calculations.py` (main API)

**ketu/ephemeris/**
- Purpose: Low-level astronomical computations independent of swisseph
- Contains: Time conversion, orbital mechanics, coordinate transformations
- Key files: `planets.py` (calc_planet_position), `time.py` (Julian day conversion)
- Generated: No; hand-written pure Python/NumPy
- Committed: Yes; core to library functionality

**ketu/aspects/**
- Purpose: Discrete aspect event detection (exact moments, windows, timelines)
- Contains: 6 modules with specialized algorithms
- Key files: `calculator.py` (public API), `core.py` (shared algorithms), `windows.py` (precise timing)
- Generated: No
- Committed: Yes; extensive test coverage in tests/test_aspect*.py

**ketu/cycles/**
- Purpose: Continuous cycle state generation for time series analysis
- Contains: CYCLE_DTYPE (structured array), generate_cycle_series (vectorized)
- Key files: `calculator.py` (CycleState, generate functions)
- Generated: No
- Committed: Yes; designed for Kala/Solaris integration

**ketu/cache/**
- Purpose: Optional caching layer for 100x speedup on repeated queries
- Contains: EphemerisCache class, daily position pre-computation
- Key files: `ephemeris_cache.py`
- Generated: No; cache files are generated at runtime
- Committed: No (cache files in .gitignore)

**ketu/export/**
- Purpose: Optional output formats with graceful degradation
- Contains: Chart visualization (matplotlib), iCalendar export
- Key files: `chart.py`, `icalendar.py`, `constants.py`
- Generated: No
- Committed: Yes; optional but included for reference

**tests/**
- Purpose: Test suite (176 passing tests)
- Contains: 16 test modules covering all public APIs
- Key files: `test_ketu.py` (core), `test_complex.py` (ML features), `test_aspect_windows.py` (windows)
- Generated: No
- Committed: Yes; pytest config in pyproject.toml

**docs/**
- Purpose: Sphinx documentation and API reference
- Contains: API docs (markdown/RST), concepts, architecture
- Key files: `source/api.md`, `source/concepts.md`
- Generated: Partially (built Sphinx outputs)
- Committed: Source files yes, built docs no

## Key File Locations

**Entry Points:**
- `ketu/__init__.py`: Main public API (imports all user-facing functions)
- `ketu/display.py::main()`: CLI entry point (`ketu` command)
- `ketu/__main__.py`: Module entry point (`python -m ketu`)
- `ketu/cycles/__init__.py`: Cycles module entry point (generate_cycle_series)

**Configuration:**
- `pyproject.toml`: Project metadata, dependencies, entry point definition
- `CLAUDE.md`: Ketu-specific developer instructions (rules, architecture, versions)
- `.readthedocs.yaml`: ReadTheDocs build configuration
- `.pytest_cache/`: pytest configuration (in pyproject.toml under [tool.pytest])

**Core Logic:**
- `ketu/core.py`: bodies/aspects/signs arrays (constants, canonical reference)
- `ketu/calculations.py`: Main calculation API (position, velocity, sign, retrograde)
- `ketu/ephemeris/planets.py`: calc_planet_position, calc_planet_position_batch (kernel)
- `ketu/aspects/calculator.py`: get_aspect, calculate_aspects (user API)
- `ketu/cycles/calculator.py`: generate_cycle_series, CYCLE_DTYPE (ML integration point)

**Testing:**
- `tests/test_ketu.py`: Core functionality (time, positions, aspects)
- `tests/test_complex.py`: Complex representation and ML features
- `tests/test_aspect_windows.py`: Precise aspect event timing
- `tests/test_lunar_calendar_performance.py`: Lunar calendar generation
- All tests use pytest; run with `pytest tests/ -v`

## Naming Conventions

**Files:**
- Modules: lowercase_with_underscores.py (e.g., `ephemeris_cache.py`)
- Packages: lowercase (e.g., `ephemeris/`, `aspects/`)
- Test files: `test_<module>.py` or `test_<feature>.py`
- Benchmarks: `benchmark*.py` in tests/ directory
- Docs: `*.md` (markdown) or `*.rst` (reStructuredText)

**Directories:**
- Source: `ketu/` for main package, `tests/` for tests, `docs/` for documentation
- Subpackages: Use single lowercase name with multiple modules inside (e.g., `ephemeris/`, `aspects/`)
- Config: Hidden directories like `.github/`, `.pytest_cache/`, `.git/`
- Resources: `res/`, `examples/`, `fr/` (French docs), `benchmarks/`, `scripts/`

**Functions/Classes:**
- Public API: CamelCase for classes (ZodiacPoint, CycleState, AspectWindow), snake_case for functions (generate_cycle_series, find_aspect_window)
- Private: Prefix with underscore (e.g., _get_body_id, _cached_planet_position_batch)
- Constants: UPPERCASE_WITH_UNDERSCORES (CYCLE_DTYPE, MAJOR_ASPECTS, DEFAULT_PAIRS)
- Data types: Structured arrays in core.py named with descriptors (bodies, aspects, signs)

**Type Hints:**
- Used throughout library (all public functions have type hints)
- Complex types: Union[str, int], Optional[...], Tuple[...], List[...], np.ndarray
- Imports: `from typing import ...` at module level
- Backward compatibility: Also provide untyped aliases (e.g., longitude() and long() both available)

## Where to Add New Code

**New Feature (e.g., Harmonic Aspects):**
- Primary code: Create new module in `ketu/aspects/` (e.g., `harmonics.py`)
- Public API: Export from `ketu/aspects/__init__.py`
- Core functionality: Add to `ketu/core.py` if adding body/aspect/sign constants
- Tests: `tests/test_<feature>.py`
- Docs: `docs/source/<feature>.md`

**New Component/Module (e.g., Sidereal Time Calculator):**
- Implementation: Add to appropriate subpackage
  - If ephemeris: `ketu/ephemeris/<component>.py`
  - If aspects: `ketu/aspects/<component>.py`
  - If export: `ketu/export/<component>.py`
- Integration: Export from subpackage __init__.py
- Public API: Export from main `ketu/__init__.py` if user-facing
- Tests: `tests/test_<component>.py`

**Utilities/Helpers:**
- Shared within subpackage: Add to existing module (e.g., normalize_angle in ephemeris/orbital.py)
- Cross-package: Create new utility module in appropriate subpackage
  - Calculation utilities: `ketu/calculations.py`
  - Ephemeris utilities: `ketu/ephemeris/<utility>.py`
  - Aspect utilities: `ketu/aspects/core.py`

**Tests:**
- Location: `tests/test_<module_or_feature>.py`
- Structure: Class-based (TestXxx) with setup_method/teardown_method, or function-based with fixtures
- Coverage: Aim for >90% line coverage (enforce via --cov-report=term-missing in pyproject.toml)
- Mocking: Use pytest fixtures; avoid external dependencies in tests

**Documentation:**
- API docs: `docs/source/api.md` (auto-generated or hand-written)
- Concepts: `docs/source/concepts.md` (explanations of algorithms)
- Examples: `examples/<feature>.py` (runnable scripts)
- French docs: `fr/<topic>.md`

## Special Directories

**venv/**
- Purpose: Independent Python environment for Ketu (separate from Solaris workspace)
- Generated: Yes (created by `python -m venv venv/`)
- Committed: No (.gitignore)
- Setup: `source venv/bin/activate && pip install -e .`

**.github/**
- Purpose: GitHub Actions CI/CD workflows
- Contains: Workflow definitions for testing, linting, documentation builds
- Generated: No (hand-written)
- Committed: Yes

**.planning/codebase/**
- Purpose: GSD mapping output (codebase analysis documents)
- Contains: ARCHITECTURE.md, STRUCTURE.md, CONVENTIONS.md, TESTING.md, CONCERNS.md
- Generated: Yes (by /gsd:map-codebase)
- Committed: No (temporary, generated per session)

**.coverage**
- Purpose: Coverage.py database for code coverage analysis
- Generated: Yes (created by pytest --cov)
- Committed: No (.gitignore)

**.readthedocs.yaml**
- Purpose: ReadTheDocs build configuration
- Specifies: Python version, build requirements, documentation source path
- Committed: Yes

**docs/source/**
- Purpose: Sphinx source for documentation
- Contains: conf.py (Sphinx config), markdown/RST files for API/concepts
- Generated: Partially (Sphinx builds output)
- Committed: Source yes, built docs no

---

*Structure analysis: 2026-02-12*
