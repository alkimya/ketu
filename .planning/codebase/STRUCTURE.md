# Codebase Structure

**Analysis Date:** 2026-05-29

## Directory Layout

```
ketu/
├── __init__.py                  # Public API surface (bodies, aspects, signs, HOUSES_DTYPE, house functions)
├── __main__.py                  # Entry point for `python -m ketu`
├── core.py                      # Core data structures (bodies, aspects, signs structured arrays)
├── calculations.py              # Utility functions (distance, dd_to_dms, body_properties, positions)
├── display.py                   # CLI formatters (print_positions, print_aspects)
├── complex.py                   # Complex representations for zodiac points (e^(iθ))
├── lunar_calendar.py            # Lunar calendar generation (find_new_moons_around_month, LunarCalendar)
│
├── aspects/                     # Aspect detection and analysis
│   ├── __init__.py              # Public exports (get_aspect, calculate_aspects, windows, timelines, transits)
│   ├── core.py                  # Low-level aspect calcs (orb computation, aspect matching)
│   ├── calculator.py            # High-level API (calculate_aspects_vectorized, calculate_aspects_batch)
│   ├── windows.py               # Aspect window detection with precise timing (AspectWindow, AspectMoment)
│   ├── timelines.py             # ML-ready time series (AspectTimeline, AspectEvent, generate_aspect_timeline)
│   ├── transits.py              # Transit calculations (TransitAspect, find_transits_to_position)
│   └── presets.py               # Aspect set presets (CLASSICAL, TRADITIONAL, EXTENDED, resolve_aspect_set)
│
├── charts/                      # Unified natal chart assembly
│   ├── __init__.py              # Public API (compute_chart, is_day_chart, CHART_DTYPE)
│   ├── core.py                  # CHART_DTYPE definition (14 fields: metadata, bodies, houses, aspects)
│   └── api.py                   # compute_chart, is_day_chart, _vectorised_body_properties, _build_aspect_matrix
│
├── houses/                      # House system calculations and registry
│   ├── __init__.py              # Public API (calculate_houses, house_of, HOUSES_DTYPE, SYSTEMS, HighLatitudeError)
│   ├── core.py                  # HOUSES_DTYPE definition (9 fields), HighLatitudeError exception
│   ├── api.py                   # calculate_houses dispatcher, house_of mapper
│   ├── registry.py              # SYSTEMS dict, register decorator, get_system resolver
│   ├── ascmc.py                 # compute_ascmc, Porphyry fallback for polar latitudes
│   ├── _ecliptic.py             # Ecliptic coordinate frame helper
│   ├── placidus.py              # @register('placidus') — semi-arc method
│   ├── koch.py                  # @register('koch') — semi-arc variant
│   ├── porphyry.py              # @register('porphyry') — equal cusp trisection (polar-safe fallback)
│   ├── whole_sign.py            # @register('whole_sign') — sign-based
│   ├── equal.py                 # @register('equal') — equal cusps from ASC
│   └── regiomontanus.py         # @register('regiomontanus') — variant of Placidus
│
├── synastry/                    # Inter-chart aspect calculations
│   ├── __init__.py              # Public API (calculate_synastry, SYNASTRY_DTYPE, SYNASTRY_BODY_COUNT, orb presets)
│   ├── core.py                  # SYNASTRY_DTYPE definition (8 fields), SYNASTRY_BODY_COUNT constant
│   ├── api.py                   # calculate_synastry dispatcher, dense/filtered modes
│   └── orbs.py                  # Synastry orb presets, SYNASTRY_FACTOR (0.5), resolve_orb_set
│
├── composite/                   # Midpoint composite chart
│   ├── __init__.py              # Public API (calculate_composite, circular_midpoint)
│   ├── core.py                  # circular_midpoint helper (signed short-arc midpoint)
│   └── api.py                   # calculate_composite dispatcher, Porphyry cusp derivation
│
├── returns/                     # Solar and Lunar returns
│   ├── __init__.py              # Public API (solar_return, lunar_return)
│   ├── solar.py                 # solar_return(natal_jd, target_year, return_lat=None, return_lon=None)
│   ├── lunar.py                 # lunar_return(natal_jd, target_jd, natal_lat, natal_lon)
│   └── _solve.py                # _solve_return (shared bisection core), _signed_residual_deg
│
├── parts/                       # Arabic Parts (Hermetic Lots) registry
│   ├── __init__.py              # Public API, trigger-import of built-in parts (fortune, spirit, marriage)
│   ├── api.py                   # calculate_part, calculate_all_parts dispatchers
│   └── registry.py              # PARTS dict, PartSpec dataclass, register function, get_part resolver
│
├── cycles/                      # Planetary cycle time series
│   ├── __init__.py              # Public API (generate_cycle_series, generate_multi_cycle_series, CYCLE_DTYPE)
│   └── calculator.py            # CYCLE_DTYPE, CycleState dataclass, cycle generation logic
│
├── ephemeris/                   # Low-level astronomical calculations
│   ├── __init__.py              # Public exports (time, orbital, coordinates, planets functions)
│   ├── time.py                  # utc_to_julian, julian_to_utc, local_to_utc, delta_t, sidereal_time
│   ├── orbital.py               # Kepler equation solver, ORBITAL_ELEMENTS, body position calculations
│   ├── coordinates.py           # Transform functions (ecliptic↔equatorial, heliocentric↔geocentric)
│   └── planets.py               # calc_planet_position, calc_planet_position_batch, body_properties
│
├── cache/                       # Two-layer caching strategy
│   ├── __init__.py              # Public API (EphemerisCache, BODY_COUNT, get_default_cache)
│   └── ephemeris_cache.py       # EphemerisCache class (monthly pre-computation with interpolation)
│
└── cli/                         # Command-line interface
    ├── __init__.py              # Public API (main)
    ├── parser.py                # build_parser, main dispatch logic
    ├── aspects_cmd.py           # cmd_aspects subcommand
    ├── houses_cmd.py            # cmd_houses subcommand
    ├── synastry_cmd.py          # cmd_synastry subcommand
    ├── introspection.py         # cmd_list_{aspect_sets,house_systems,orbs,parts}
    ├── harmonics_spec.py        # parse_harmonics_spec (CLI aspect set parser)
    ├── formatters.py            # Output formatting helpers
    └── _dates.py                # Date parsing utilities
```

## Directory Purposes

**ketu/ (Root Package):**
- Purpose: Ketu library package root; public API surface and core data
- Contains: __init__.py, core.py, calculations.py, display.py, complex.py, lunar_calendar.py
- Key files: `core.py` (bodies, aspects, signs), `__init__.py` (public exports)

**ketu/aspects/:**
- Purpose: Aspect calculations, detection, and analysis
- Contains: Vectorised aspect finding, window/timeline extraction, transit detection, preset masks
- Key files: `calculator.py` (high-level API), `core.py` (low-level orb logic), `presets.py` (CLASSICAL/TRADITIONAL/EXTENDED)

**ketu/charts/:**
- Purpose: Unified natal chart assembly (positions + houses + aspects in one call)
- Contains: compute_chart entry point, is_day_chart sect helper, CHART_DTYPE schema
- Key files: `api.py` (compute_chart, _vectorised_body_properties, _build_aspect_matrix), `core.py` (CHART_DTYPE)

**ketu/houses/:**
- Purpose: House system calculations via extensible registry
- Contains: 6 house systems (placidus, koch, porphyry, whole_sign, equal, regiomontanus), HOUSES_DTYPE, HighLatitudeError
- Key files: `api.py` (calculate_houses, house_of), `registry.py` (SYSTEMS dict, register decorator), system files (placidus.py, koch.py, etc.)

**ketu/synastry/:**
- Purpose: Inter-chart aspect calculations between two natal charts
- Contains: calculate_synastry dispatcher, SYNASTRY_DTYPE schema, 15-body axis (13 canonical + ASC + MC), orb presets
- Key files: `api.py` (calculate_synastry, filtered/dense modes), `core.py` (SYNASTRY_DTYPE), `orbs.py` (SYNASTRY_FACTOR, presets)

**ketu/composite/:**
- Purpose: Midpoint composite chart derivation from two natals
- Contains: calculate_composite, circular_midpoint helper
- Key files: `api.py` (calculate_composite), `core.py` (circular_midpoint)

**ketu/returns/:**
- Purpose: Solar and Lunar return chart computation
- Contains: solar_return (year-anchored), lunar_return (instant-anchored), _solve_return (shared bisection core)
- Key files: `solar.py`, `lunar.py`, `_solve.py` (_solve_return, _signed_residual_deg)

**ketu/parts/:**
- Purpose: Arabic Parts / Hermetic Lots registry and dispatch
- Contains: PARTS dict, PartSpec dataclass, 3 built-in parts (fortune, spirit, marriage)
- Key files: `registry.py` (PARTS, PartSpec, register, get_part), `api.py` (calculate_part, calculate_all_parts)

**ketu/cycles/:**
- Purpose: Planetary cycle time series generation
- Contains: CYCLE_DTYPE, generate_cycle_series, generate_multi_cycle_series, CycleState dataclass
- Key files: `calculator.py` (cycle generation logic)

**ketu/ephemeris/:**
- Purpose: Low-level astronomical calculations (not exposed to end users directly)
- Contains: Julian Date conversions, Kepler equation solver, coordinate transforms, planetary position calculations
- Key files: `time.py`, `orbital.py`, `coordinates.py`, `planets.py`

**ketu/cache/:**
- Purpose: Optional high-performance caching (Layer 1 = LRU, Layer 2 = monthly pre-computation)
- Contains: EphemerisCache class for batch operations
- Key files: `ephemeris_cache.py` (EphemerisCache implementation)

**ketu/cli/:**
- Purpose: Command-line interface entry point and subcommand dispatchers
- Contains: Argparse tree, subcommand handlers (aspects, houses, synastry), introspection flags
- Key files: `parser.py` (build_parser, main), `aspects_cmd.py`, `houses_cmd.py`, `synastry_cmd.py`, `introspection.py`

## Key File Locations

**Entry Points:**
- `ketu/__main__.py` — CLI entry point for `python -m ketu`
- `ketu/cli/parser.py:main()` — Argparse dispatcher
- `ketu/charts/api.py:compute_chart()` — Primary Python API for natal charts
- `ketu/__init__.py` — Public package exports

**Configuration:**
- `ketu/core.py` — Astronomical constants (bodies, aspects, signs structured arrays)
- `pyproject.toml` — Project metadata, dependencies (numpy >= 1.20.0)

**Core Logic:**
- `ketu/charts/api.py` — Chart assembly (_vectorised_body_properties, _build_aspect_matrix)
- `ketu/aspects/calculator.py` — Vectorised aspect detection
- `ketu/returns/_solve.py` — Bisection root-finder for returns
- `ketu/ephemeris/planets.py` — Planetary position calculations (pure NumPy)

**Testing:**
- `tests/test_ketu.py` — Core data structure contracts and invariants
- `tests/test_*.py` — Feature-specific tests (aspects, transits, coordinates, etc.)
- `tests/conftest.py` — Pytest fixtures (if present)

## Naming Conventions

**Files:**
- Module files: `lowercase_with_underscores.py` (e.g., `aspect_windows.py`, `ephemeris_cache.py`)
- Private modules: Prefix with `_` (e.g., `_solve.py`, `_ecliptic.py`)
- Subpackage __init__.py: Exports public API; may trigger registrations via side-effect imports

**Directories:**
- Subpackages: `lowercase` (e.g., `aspects`, `houses`, `returns`)
- Package group: Alphabetically ordered by purpose (data → calculation → chart → derived)

**Functions:**
- Public API: `snake_case` (e.g., `calculate_aspects_vectorized`, `compute_chart`, `solar_return`)
- Internal helpers: Prefix with `_` (e.g., `_vectorised_body_properties`, `_solve_return`)
- Registry callables: Named with purpose (e.g., `register`, `get_system`, `get_part`)

**Classes:**
- Public: `PascalCase` (e.g., `HighLatitudeError`, `AspectWindow`, `PartSpec`)
- Exception subclasses: Suffix with `Error` or inherit from ValueError
- Dataclasses: Frozen where possible (PartSpec, Aspect)

**Constants:**
- Structured arrays: `UPPERCASE` (e.g., `CHART_DTYPE`, `CYCLE_DTYPE`, `HOUSES_DTYPE`)
- Registries: `UPPERCASE` (e.g., `SYSTEMS`, `PARTS`, `CLASSICAL`, `TRADITIONAL`, `EXTENDED`)
- Immutable sequences: `UPPERCASE` (e.g., `DEFAULT_PAIRS`, `MAJOR_ASPECTS`)
- Internal constants: `_UPPERCASE` (e.g., `_TOL_DEG`, `_TROPICAL_YEAR_D`)

## Where to Add New Code

**New House System:**
1. Create `ketu/houses/mysystem.py` with `@register('mysystem')` decorator
2. Implement house calculation function matching `HouseSystemFn` signature
3. Import the module in `ketu/houses/__init__.py` to trigger registration
4. Add tests in `tests/test_houses_*.py`

**New Arabic Part:**
1. Call `register(name='mypart', day_formula=..., night_formula=..., description=...)` in `ketu/parts/__init__.py`
2. Use signature `(asc, sun, moon, venus) -> float` for both formulas
3. Add tests in `tests/test_parts_*.py`

**New Aspect Calculation / Feature:**
1. Primary code: `ketu/aspects/newfeature.py`
2. Export from `ketu/aspects/__init__.py`
3. Tests: `tests/test_aspect_newfeature.py`

**New Cycle Analysis:**
1. Primary code: `ketu/cycles/newanalysis.py`
2. Leverage CYCLE_DTYPE or create specialized dtype (follow CHART_DTYPE/SYNASTRY_DTYPE pattern)
3. Tests: `tests/test_cycles_newanalysis.py`

**New CLI Subcommand:**
1. Create `ketu/cli/mycommand_cmd.py` with `cmd_mycommand(args)` dispatcher
2. Add subparser in `ketu/cli/parser.py:build_parser()` with `set_defaults(func=cmd_mycommand)`
3. Tests: `tests/test_cli_mycommand.py`

**Bug Fix or Refactor:**
1. If fixing a calculation: modify source file directly (e.g., `ketu/ephemeris/planets.py`)
2. If refactoring a dtype: update ARCH.md and STRUCTURE.md; coordinate with Kala consumer
3. Add regression test in appropriate `tests/test_*.py` file
4. Commit with message "fix: description" or "refactor: description"

## Special Directories

**ketu/__pycache__/:**
- Purpose: Python bytecode cache (auto-generated)
- Generated: Yes
- Committed: No (.gitignore)

**tests/__pycache__/:**
- Purpose: Pytest bytecode cache (auto-generated)
- Generated: Yes
- Committed: No (.gitignore)

**tests/:**
- Purpose: All test files (mirroring ketu/ structure and extending with integration tests)
- Contains: test_ketu.py (core invariants), test_aspects.py, test_houses.py, test_transits.py, test_coordinates_coverage.py, etc.
- Committed: Yes
- Run: `pytest tests/ -v`

**ketu/cache/ (optional user activation):**
- Purpose: High-performance batch pre-computation (user explicitly creates EphemerisCache instance)
- Generated: No (code only)
- Committed: Yes

**docs/ and examples/ (if present):**
- Purpose: Documentation and usage examples
- Committed: Yes

---

*Structure analysis: 2026-05-29*
