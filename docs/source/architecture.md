# Architecture

This page describes the internal architecture of Ketu v0.3.0.

## Module Structure

```
ketu/
├── __init__.py          # Public API and imports
├── core.py              # Data structures (bodies, aspects, signs)
├── calculations.py      # High-level calculation functions
├── display.py           # CLI and display utilities
├── aspect_windows.py    # Aspect timing calculations
├── transits.py          # Transit calculations
├── chart.py             # Zodiacal chart visualization
├── icalendar_export.py  # iCalendar export utilities
└── ephemeris/           # Low-level astronomical calculations
    ├── __init__.py      # Ephemeris package API
    ├── time.py          # Time conversions and equation of time
    ├── orbital.py       # Orbital mechanics and Kepler solver
    ├── coordinates.py   # Coordinate transformations
    └── planets.py       # Planetary position calculations
```

## Core Components

### Data Structures (core.py)

Defines the fundamental data structures:

- **bodies**: Dictionary with planet names, IDs, symbols, orbs, speeds
- **aspects**: Dictionary with aspect names, angles, coefficients, symbols
- **signs**: List of zodiac sign names

These are implemented as NumPy structured arrays for efficient access.

### Calculations (calculations.py)

High-level API wrapping ephemeris functions:

- `positions()` - Get all planetary positions
- `calculate_aspects()` - Detect all aspects
- `find_aspect_timing()` - Find exact aspect moments
- `is_retrograde()` - Check retrograde motion

### Display (display.py)

User-facing display functions:

- `print_positions()` - Formatted position table
- `print_aspects()` - Formatted aspect table
- `main()` - Interactive CLI entry point

## Ephemeris Package

### Time Conversions (ephemeris/time.py)

Handles all time-related calculations:

- **UTC ↔ Julian Day** conversions
- **Equation of time** calculations
- **Sidereal time** calculations
- **Delta T** corrections for historical dates

Uses purely mathematical formulas - no external dependencies.

### Orbital Mechanics (ephemeris/orbital.py)

Core astronomical calculations:

- **Kepler solver** - Solves Kepler's equation using Newton-Raphson
- **Orbital elements** - Planetary orbital parameters
- **Perturbations** - Major planetary perturbations
- **Position from elements** - Convert orbital elements to position

### Coordinate Transformations (ephemeris/coordinates.py)

Coordinate system conversions:

- **Ecliptic ↔ Equatorial** coordinates
- **Heliocentric ↔ Geocentric** positions
- **Rectangular ↔ Spherical** coordinates
- **Nutation** corrections
- **Aberration** corrections

### Planetary Calculations (ephemeris/planets.py)

High-level planetary position functions:

- `calc_planet_position()` - Single date calculation
- `calc_planet_position_batch()` - Vectorized batch calculation
- `find_exact_aspect()` - Binary search for exact aspects
- `body_properties()` - Get full position + velocity

## Advanced Features

### Aspect Windows (aspect_windows.py)

Temporal tracking of aspects:

- **AspectMoment** - Instant when aspect is exact
- **AspectWindow** - Duration from begin to end of aspect
- `find_aspect_window()` - Find all windows in date range
- `find_aspects_timeline()` - Complete aspect timeline

Uses binary search and gradient descent for precision.

### Transits (transits.py)

Natal chart and transit calculations:

- **NatalPosition** - Stores natal planet position
- **TransitAspect** - Describes transit-to-natal aspect
- `get_natal_positions()` - Extract natal positions
- `find_transits_to_position()` - Find transits to a point
- `compare_dates_transits()` - Full transit comparison

### Chart Visualization (chart.py)

Matplotlib-based zodiacal charts:

- Circular zodiac with 12 signs
- Planet glyphs at correct positions
- Aspect lines between planets
- Customizable colors and styles
- SVG/PNG/PDF output

Requires optional `matplotlib` dependency.

### iCalendar Export (icalendar_export.py)

Export aspects to calendar format:

- `export_lunations_to_ical()` - New/Full Moon events
- `export_aspects_to_ical()` - All aspects as events
- `export_transits_to_ical()` - Transit events

Requires optional `icalendar` dependency.

## Design Principles

### Separation of Concerns

- **ephemeris/**: Pure astronomical calculations
- **calculations.py**: Astrological interpretations
- **display.py**: User interface
- **Advanced modules**: Optional features

### Vectorization First

All core functions support both scalar and array inputs via NumPy broadcasting.

### No Global State

All functions are pure - same inputs always produce same outputs.

### Optional Dependencies

Advanced features (charts, iCalendar) are optional extras:

```python
# Optional import with graceful degradation
try:
    from ketu.chart import draw_zodiacal_chart
    _CHART_AVAILABLE = True
except ImportError:
    _CHART_AVAILABLE = False
```

### Backward Compatibility

The public API maintains compatibility with previous versions where possible.

## Data Flow

### Position Calculation Flow

```
User calls: ketu.long(jday, body)
           ↓
calculations.long(jday, body)
           ↓
ephemeris.planets.calc_planet_position(jday, body)
           ↓
ephemeris.orbital.calc_planet_pos_from_elements(jday, elements)
           ↓
ephemeris.orbital.solve_kepler(M, e)
           ↓
Returns: [lon, lat, dist, lon_speed, lat_speed, dist_speed]
```

### Aspect Calculation Flow

```
User calls: ketu.calculate_aspects(jday)
           ↓
calculations.calculate_aspects(jday)
           ↓
1. Get all planet positions
2. Generate all body pairs
3. For each pair:
   - Calculate angular distance
   - Check against aspect angles
   - Compute orb
   - Filter by orb tolerance
           ↓
Returns: Structured array of aspects
```

## Testing Strategy

### Unit Tests

- Individual functions in `ephemeris/`
- Isolated calculations
- Edge cases and boundary conditions

### Integration Tests

- Full position calculations
- Aspect detection
- Time conversions

### Validation Tests

- Compare against known ephemeris data
- Cross-check with historical observations
- Verify retrograde periods

### Benchmark Tests

- Performance regression detection
- Memory usage monitoring
- Optimization validation

## Extension Points

To add new features:

1. **New celestial bodies**: Add to `core.bodies`
2. **New aspects**: Add to `core.aspects`
3. **New calculations**: Extend `calculations.py`
4. **New ephemeris functions**: Add to `ephemeris/`
5. **New export formats**: Follow `icalendar_export.py` pattern
