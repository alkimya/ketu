# Aspects Package

This package contains all aspect-related calculations and analysis tools for Ketu.

## Modules

### `core.py`
Low-level aspect calculation algorithms (internal use).
- Cached position calculations
- Binary search refinement
- Retrograde detection
- Adaptive grid search

### `calculator.py`
High-level aspect finding functions.
- `get_aspect()`: Find aspect between two bodies at a moment
- `calculate_aspects()`: Calculate all aspects at a moment
- `find_aspect_timing()`: Find when aspect becomes exact
- `find_aspects_between_dates()`: Find aspects in date range

### `windows.py`
Aspect window detection with precise timing.
- `find_aspect_window()`: Find entry/exit times and exact moments
- `find_aspects_timeline()`: Find multiple aspects efficiently
- `AspectWindow`: Structured aspect window data
- `AspectMoment`: Exact aspect timing data

### `timelines.py`
ML-ready aspect timeline generation.
- `generate_aspect_timeline()`: Generate complete aspect timeline
- `AspectTimeline`: Timeline with export methods (NumPy, Pandas, JSON)
- `AspectEvent`: Rich event data with cycle information
- Perfect for machine learning and research

### `transits.py`
Transit calculations to natal positions.
- `find_transits_to_position()`: Find transits to a specific position
- `get_natal_positions()`: Get all natal positions
- `compare_dates_transits()`: Compare transits between dates
- `TransitWindow`: Structured transit data

## Usage

All functions are exported through `ketu.aspects` and `ketu` main package:

```python
from ketu import generate_aspect_timeline
from ketu.aspects import find_aspect_window, calculate_aspects

# Generate ML-ready timeline
timeline = generate_aspect_timeline(
    body1="Sun",
    body2="Mars",
    start_date="2024-01-01",
    end_date="2024-12-31",
)

# Export to Pandas
df = timeline.to_pandas()
```

## Architecture

```
aspects/
├── core.py           # Low-level algorithms
├── calculator.py     # High-level aspect finding
├── windows.py        # Precise timing windows
├── timelines.py      # ML-ready timelines
└── transits.py       # Transit calculations
```

All modules use absolute imports (`ketu.X`) for clarity and maintainability.

## See Also

- Main documentation: `/docs/aspect_timelines.md`
- Examples: `/examples/aspect_timeline_demo.py`
- Tests: `/tests/test_aspect_*.py`
