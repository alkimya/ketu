# Architecture

This page describes the internal architecture of Ketu v1.3.

## Module Structure

```text
ketu/
├── __init__.py          # Public re-exports: bodies, aspects, signs, HOUSES_DTYPE,
│                        #   HighLatitudeError, HOUSE_SYSTEMS, calculate_houses,
│                        #   house_of, __version__
├── core.py              # Fundamental data structures: bodies (14), aspects, signs
├── calculations.py      # High-level API: long, lat, dist_au, body_sign,
│                        #   is_retrograde, positions, body_name, body_properties
├── display.py           # CLI display: print_positions, print_aspects, main
├── aspect_windows.py    # Aspect timing: AspectMoment, AspectWindow,
│                        #   find_aspect_window, find_aspects_timeline
├── transits.py          # Transit calculations: NatalPosition, TransitAspect,
│                        #   get_natal_positions, find_transits_to_position
│
├── aspects/             # Configurable aspect sets (New in v1.1)
│   └── __init__.py      # CLASSICAL, TRADITIONAL, EXTENDED, AspectSetSpec,
│                        #   resolve_aspect_set, calculate_aspects, get_aspect, get_orb
│
├── houses/              # House system calculations (New in v1.1/v1.2)
│   └── __init__.py      # calculate_houses, house_of, HOUSES_DTYPE, SYSTEMS,
│                        #   HighLatitudeError, register (6 systems)
│
├── charts/              # Full natal chart (New in v1.2)
│   └── __init__.py      # compute_chart, is_day_chart, CHART_DTYPE
│
├── synastry/            # Inter-chart aspects (New in v1.2)
│   └── __init__.py      # calculate_synastry, SYNASTRY_DTYPE
│
├── composite/           # Midpoint composite charts (New in v1.2)
│   └── __init__.py      # calculate_composite, circular_midpoint
│
├── returns/             # Solar and lunar returns (New in v1.2)
│   └── __init__.py      # solar_return, lunar_return
│
├── parts/               # Arabic Parts / Hermetic Lots (New in v1.2)
│   └── __init__.py      # PARTS, calculate_part, calculate_all_parts,
│                        #   register, get_part, PartSpec
│
├── cache/               # High-performance ephemeris cache
│   └── ephemeris_cache.py  # Monthly pre-computed positions (O(1) lookups)
│
├── data/                # Embedded coefficient data (New in v1.3)
│   └── chiron_coeffs.npz   # Chebyshev polynomial coefficients for Chiron,
│                           #   1900–2100, seg=32 days, degree=10
│
└── ephemeris/           # Low-level astronomical calculations (pure NumPy)
    ├── __init__.py      # Ephemeris package API
    ├── time.py          # Time conversions: utc_to_julian, local_to_utc,
    │                    #   sidereal time, Delta T
    ├── orbital.py       # Orbital mechanics: Kepler solver, orbital elements,
    │                    #   perturbations (re-export hub; elements in _elements.py)
    ├── _elements.py     # ORBITAL_ELEMENTS + Lilith constants (extracted in v1.2)
    ├── _perturbations.py # apply_perturbations strategy (extracted in v1.2)
    ├── coordinates.py   # Coordinate transformations: ecliptic↔equatorial,
    │                    #   heliocentric↔geocentric, nutation, aberration
    ├── planets.py       # Planetary position dispatch: BODY_STRATEGIES dict,
    │                    #   calc_planet_position, get_body_position, body_properties
    └── chiron.py        # Chiron Chebyshev evaluator (New in v1.3): private helpers
                         #   _load_chiron_data, _chiron_scalar, _chiron_vec
```

## Runtime Dependencies

Ketu is a **pure NumPy library at runtime**. The only runtime dependency is NumPy.

`pyswisseph` is used **only** in the offline build tool (`tools/gen_chiron_coeffs.py`) to generate the Chiron Chebyshev coefficients. It is never imported at runtime, which maintains AGPL isolation.

## Core Components

### Data Structures (`core.py`)

Defines fundamental structured arrays:

- **`bodies`**: 14-element structured array (`name`, `id`, `orb`, `speed`). Index 13 = Chiron (New in v1.3).
- **`aspects`**: 14-element array (`name`, `value`, `coef`) for all supported aspect angles.
- **`signs`**: list of 12 zodiac sign names.

### Calculations (`calculations.py`)

High-level API wrapping ephemeris functions with LRU caching:

- `positions()` — all planetary longitudes
- `long/lat/dist_au()` — single-body position components
- `body_sign()` — zodiac sign + degree breakdown
- `is_retrograde()` — retrograde detection
- `body_name()` — body ID to string

### Aspects (`ketu/aspects/`)

Configurable aspect detection (New in v1.1):

- `CLASSICAL / TRADITIONAL / EXTENDED` — boolean masks for preset sets
- `calculate_aspects(jdate, l_bodies, aspects=None)` — accepts any `AspectSetSpec`
- `get_aspect(jdate, body1, body2)` — single pair
- `get_orb(body1, body2, asp)` — orb for pair + aspect

### House Systems (`ketu/houses/`)

Six house systems (New in v1.1/v1.2):

- Placidus, Koch, Porphyry, Whole Sign, Equal, Regiomontanus
- `calculate_houses(jd, lat, lon, system, polar_fallback)` → `HOUSES_DTYPE`
- `house_of(planet_lon, cusps)` — vectorised house assignment
- `register` — extend with custom systems
- `HighLatitudeError` — raised when Placidus/Koch fail near poles

### Charts (`ketu/charts/`)

Full natal chart (New in v1.2):

- `compute_chart(jd, lat, lon, system, aspects, polar_fallback)` → `CHART_DTYPE`
- `is_day_chart(jd, lat, lon)` — sect helper (Sun above horizon)
- `CHART_DTYPE` — unified structured array: 14 body positions, 12 cusps, angles, 14×14 aspect matrix

### Relational Charts (`ketu/synastry/`, `ketu/composite/`)

Inter-chart analysis (New in v1.2):

- `calculate_synastry(chart_a, chart_b, aspects, orbs, mode)` → `SYNASTRY_DTYPE`
- `calculate_composite(chart_a, chart_b, system)` → `CHART_DTYPE`
- `circular_midpoint(lon_a, lon_b)` — shortest-arc midpoint utility

### Predictive Charts (`ketu/returns/`)

Solar and lunar returns (New in v1.2):

- `solar_return(natal_jd, …, target_year)` — exact Sun return to natal position
- `lunar_return(natal_jd, …, target_jd)` — next Moon return after target date
- Both return `CHART_DTYPE` for the return chart
- Support relocation via `return_lat/return_lon` parameters

### Arabic Parts (`ketu/parts/`)

Hermetic Lots (New in v1.2):

- `PARTS` registry: `fortune`, `spirit`, `marriage`
- `calculate_part(part_name, chart)` — sect-aware for Fortune/Spirit
- `calculate_all_parts(chart, parts=None)` → `dict[str, float]`
- Custom parts via `register(name, day_formula, night_formula, description)`

## Ephemeris Package

### Time Conversions (`ephemeris/time.py`)

- UTC ↔ Julian Day conversions
- Equation of time calculations
- Sidereal time calculations
- Delta T corrections for historical dates

Uses purely mathematical formulas — no external dependencies.

### Orbital Mechanics (`ephemeris/orbital.py`)

Re-export hub delegating to:

- `_elements.py`: `ORBITAL_ELEMENTS` + Lilith constants (extracted in v1.2 to eliminate circular import risk)
- `_perturbations.py`: `apply_perturbations` strategy

Core functions:

- Kepler solver (Newton-Raphson)
- Position from orbital elements
- Major planetary perturbations

### Coordinate Transformations (`ephemeris/coordinates.py`)

- Ecliptic ↔ Equatorial coordinates
- Heliocentric ↔ Geocentric positions
- Rectangular ↔ Spherical coordinates
- Nutation + aberration corrections (applied inside body-vec functions)

### Planetary Calculations (`ephemeris/planets.py`)

Strategy-based dispatch (refactored in v1.2):

- `BODY_STRATEGIES` — dict mapping body_id → computation function; Chiron strategy added at index 13 (v1.3)
- `calc_planet_position(jday, body)` — dispatches via strategy dict
- `get_body_position / get_body_position_vectorized` — scalar and batch entry points
- `body_properties(jd, body)` — full 6-component vector (lon, lat, dist, velocities), LRU-cached

### Chiron Evaluator (`ephemeris/chiron.py`)

New in v1.3. Private helpers — not part of the public API:

- `_load_chiron_data()` — loads `ketu/data/chiron_coeffs.npz` via `importlib.resources`
- `_chiron_scalar(jd)` — evaluates Chebyshev polynomial for a single JD
- `_chiron_vec(jd_array)` — vectorised batch evaluation

Coefficients: 2283 segments, 32-day width, degree 10, three quantities (lon, lat, dist). Max error: 0.001214° over 1900–2100.

## Design Principles

### Separation of Concerns

- `ephemeris/`: pure astronomical calculations (no astrological interpretation)
- `calculations.py`: astrological interpretation layer
- `display.py`: user interface only
- Subpackages: each feature area is self-contained

### Vectorization First

All core functions support both scalar and array inputs via NumPy broadcasting.

### No Global State

All functions are pure — same inputs always produce same outputs. LRU cache is the only shared state (clearable via `body_properties.cache_clear()`).

### Pure NumPy Runtime

Only NumPy is imported at runtime. pyswisseph is a test/build-only dependency (AGPL isolation).

### 100% Test Coverage

All branches are covered by the test suite (1373+ tests). The `fail_under=100` gate is enforced in CI via pytest-cov.

## Data Flow

### Position Calculation Flow

```text
from ketu.calculations import long
long(jd, body)
       |
       v
ephemeris/planets.py — body_properties(jd, body)
       |
       v
BODY_STRATEGIES[body](jd)   ← strategy dispatch
       |
   body < 13: calc_planet_position (orbital mechanics)
   body == 13: _chiron_vec / _chiron_scalar (Chebyshev)
       |
       v
Returns: [lon, lat, dist, lon_speed, lat_speed, dist_speed]
```

### Chart Calculation Flow

```text
from ketu.charts import compute_chart
compute_chart(jd, lat, lon, system)
       |
       v
1. get_body_position_vectorized  → body_lons[14], body_lats[14], body_speeds[14]
2. calculate_houses(jd, lat, lon, system)  → cusps[12], asc, mc, armc, vertex
3. calculate_aspects(jd, ...)   → aspect_matrix[14,14], aspect_orbs[14,14]
       |
       v
Returns: scalar CHART_DTYPE array
```

## Testing Strategy

### Unit Tests

- Individual functions in `ephemeris/`
- Isolated calculations
- Edge cases and boundary conditions

### Integration Tests

- Full chart computation
- Aspect detection
- Time conversions
- Chiron accuracy pins (reference longitudes spanning 1900–2100)

### Quality Gates (CI)

- **pytest**: 1373+ tests, all must pass
- **Coverage**: 100% (`fail_under=100`, zero pragma, `exclude_lines` for proven dead branches)
- **mypy strict**: zero errors across all subpackages
- **numpydoc**: all public docstrings validated
- **doctests**: 56+ inline examples verified via `pytest --doctest-modules ketu/`
