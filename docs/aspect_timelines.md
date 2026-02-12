# Aspect Timelines for ML/Research Applications

The `aspect_timelines` module provides a framework for generating planetary aspect calendars optimized for machine learning, deep learning, and research applications.

> **Migration Note**: As of v1.0, Ketu no longer provides `to_pandas()`. Use `to_numpy()` for ML workflows or `to_dict_list()` for dict-based workflows. See `UPGRADING.md` for conversion patterns.

## Overview

Unlike traditional astrological calendars that focus on complete cycles, aspect timelines use a **time window approach** - finding all aspects between two celestial bodies within a specified date range. This makes it ideal for:

- **Machine Learning**: Training data for predictive models
- **Deep Learning**: Time series analysis with rich feature sets
- **Research**: Statistical analysis of planetary patterns

## Key Features

### 1. Time Window Approach
Generate aspects between any two dates, not just complete cycles:
```python
from ketu import generate_aspect_timeline

timeline = generate_aspect_timeline(
    body1="Sun",
    body2="Mars",
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

### 2. Universal Planet Support
Works with ANY two celestial bodies:
- Fast planets (Sun-Moon, Sun-Mercury)
- Slow planets (Jupiter-Saturn, Saturn-Pluto)
- Mixed speeds (Mars-Neptune, Venus-Uranus)

### 3. Complete Cycle Information
Each event includes full metadata:
- **Timing**: Exact moment, entry/exit times, duration
- **Cycle data**: Angular separation, phase, quadrant, progress
- **Velocity**: Relative velocity, days to exact
- **Retrograde**: Detection and intensity for both bodies

### 4. ML-Ready Export Formats
Two export formats for different workflows:

#### NumPy (Dense Arrays)
```python
np_array = timeline.to_numpy()
# Structured array with all numerical features
# Perfect for scikit-learn, TensorFlow, PyTorch
```

#### JSON (Interoperability)
```python
json_data = timeline.to_json()
# Full metadata + events
# Perfect for web APIs, storage, sharing
```

## Usage Examples

### Example 1: Martian Calendar (Mars-Sun)

```python
from ketu import generate_aspect_timeline

# Generate Mars-Sun aspects for 2024
timeline = generate_aspect_timeline(
    body1="Sun",
    body2="Mars",
    start_date="2024-01-01",
    end_date="2024-12-31",
)

print(f"Found {len(timeline)} Mars-Sun aspects in 2024")

# Access events
for event in timeline.events:
    print(f"{event.aspect_name}: {event.timestamp}")
    print(f"  Strength: {event.aspect_strength:.3f}")
    print(f"  Duration: {event.duration_days:.1f} days")
```

### Example 2: Venus-Neptune with Custom Aspects

```python
# Only major aspects
timeline = generate_aspect_timeline(
    body1="Venus",
    body2="Neptune",
    start_date="2024-01-01",
    end_date="2024-12-31",
    aspects_list=["Conjunction", "Square", "Opposition"],
)

# Export to NumPy for analysis
data = timeline.to_numpy()
print(data[['aspect_type', 'orb', 'aspect_strength', 'duration_days']])
```

### Example 3: Lunar Calendar (Moon-Sun)

```python
# Traditional lunar calendar using the new framework
timeline = generate_aspect_timeline(
    body1="Sun",
    body2="Moon",
    start_date="2024-01-01",
    end_date="2024-01-31",
    detect_retrograde=False,  # Moon never retrogrades
)

# Group by aspect type
from collections import defaultdict
by_aspect = defaultdict(list)
for event in timeline.events:
    by_aspect[event.aspect_name].append(event.timestamp)

for aspect, times in by_aspect.items():
    print(f"{aspect}: {len(times)} occurrences")
```

### Example 4: Jupiter-Saturn Retrograde Analysis

```python
# Study Jupiter-Saturn major aspects with retrograde detection
timeline = generate_aspect_timeline(
    body1="Jupiter",
    body2="Saturn",
    start_date="2024-01-01",
    end_date="2025-12-31",
    aspects_list=[0, 90, 180],  # Conjunction, Square, Opposition
    detect_retrograde=True,
)

# Find retrograde events
retrograde_events = [
    e for e in timeline.events
    if e.body1_retro or e.body2_retro
]

print(f"Found {len(retrograde_events)} events during retrograde")
for event in retrograde_events:
    retro_bodies = []
    if event.body1_retro:
        retro_bodies.append("Jupiter")
    if event.body2_retro:
        retro_bodies.append("Saturn")
    print(f"{event.aspect_name}: {', '.join(retro_bodies)} retrograde")
    print(f"  Intensity: {event.retro_intensity:.4f}")
```

### Example 5: ML Feature Engineering

```python
# Generate training data for ML model
timeline = generate_aspect_timeline(
    body1="Sun",
    body2="Mars",
    start_date="2020-01-01",
    end_date="2024-12-31",
)

# Convert to NumPy for ML
data = timeline.to_numpy()

# Extract features
features = data[['aspect_type', 'aspect_strength', 'relative_velocity',
                 'body1_retro', 'body2_retro', 'duration_days']]

# For more complex analysis, convert to pandas if needed
import pandas as pd
df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['julian_day'], unit='D', origin='julian')
df.set_index('timestamp', inplace=True)

# Create derived features
df['is_retrograde'] = df['body1_retro'] | df['body2_retro']
df['strength_category'] = pd.cut(df['aspect_strength'], bins=[0, 0.7, 0.9, 1.0])
df['velocity_abs'] = df['relative_velocity'].abs()

# Time-based features
df['month'] = df.index.month
df['day_of_year'] = df.index.dayofyear

print(df.head())
```

## Data Structure Reference

### AspectEvent

Each event in the timeline contains:

```python
@dataclass
class AspectEvent:
    # Basic information
    timestamp: datetime          # UTC datetime of exact aspect
    julian_day: float           # Julian Date
    body1_id: int               # First body ID (0=Sun, 1=Moon, etc.)
    body2_id: int               # Second body ID
    body1_name: str             # First body name
    body2_name: str             # Second body name

    # Aspect information
    aspect_type: float          # Aspect angle (0, 60, 90, 120, 180)
    aspect_name: str            # Aspect name (Conjunction, etc.)
    orb: float                  # Orb in degrees (0 = exact)
    orb_tolerance: float        # Maximum orb allowed
    aspect_strength: float      # 1.0 at exact, 0.0 at orb edge

    # Cycle information
    angular_separation: float   # Angular distance (0-360°)
    phase: str                  # 'applying', 'exact', 'separating'
    relative_velocity: float    # Degrees/day
    days_to_exact: float        # Days until/since exact

    # Retrograde information
    body1_retro: bool           # Is body1 retrograde?
    body2_retro: bool           # Is body2 retrograde?
    retro_intensity: float      # Sum of velocities when retro

    # Window timing
    window_begin: datetime      # Entry into orb
    window_end: datetime        # Exit from orb
    duration_days: float        # Duration in days
```

### AspectTimeline

The timeline object contains:

```python
@dataclass
class AspectTimeline:
    body1: str                      # Name of first body
    body2: str                      # Name of second body
    start_date: datetime            # Timeline start
    end_date: datetime              # Timeline end
    timezone: ZoneInfo              # Timezone for display
    events: List[AspectEvent]       # List of events (sorted)
    aspects_included: List[float]   # Aspect angles included
    detect_retrograde: bool         # Retrograde detection enabled

    # Export methods
    def to_numpy() -> np.ndarray    # NumPy structured array
    def to_json() -> dict           # JSON-serializable dict
    def to_dict_list() -> list      # List of dicts
```

## ETL Workflow

The module follows Extract-Transform-Load principles:

### Extract
Calculate aspect events from ephemeris data using optimized algorithms:
- Adaptive grid search for candidate detection
- Binary search refinement for precision (±1 second)
- Vectorized operations for performance

### Transform
Enrich raw events with ML-ready features:
- Cycle information (phase, progress, quadrant)
- Velocity and acceleration metrics
- Retrograde detection and intensity
- Time-based features

### Load
Export to ML-friendly formats:
- **NumPy**: Dense numerical arrays for training
- **JSON**: Interoperable format for APIs/storage
- **Pandas**: (User-side conversion via `pd.DataFrame(timeline.to_numpy())`)

## Performance Characteristics

### Speed
- Fast bodies (Sun-Moon): ~0.1ms per aspect search
- Slow bodies (Jupiter-Saturn): ~0.13ms per aspect search
- Full year Sun-Moon timeline: ~1-2 seconds
- Retrograde detection: Minimal overhead

### Memory
- Structured NumPy arrays: Very compact
- Events stored as dataclasses: Minimal overhead
- Lazy evaluation: No computation until export

### Accuracy
- Exact aspect timing: ±1 second precision
- Orb calculations: 4+ decimal places
- Position accuracy: Swiss Ephemeris quality

## Comparison with Lunar Calendar

The new framework generalizes the lunar calendar concept:

| Feature | Lunar Calendar | Aspect Timelines |
|---------|---------------|------------------|
| Bodies | Sun-Moon only | Any 2 bodies |
| Approach | Complete cycle | Time window |
| Retrograde | N/A (Moon direct) | Full support |
| Export formats | Print only | NumPy, JSON |
| ML features | Limited | Complete |
| Use cases | Calendar display | ML/research |

You can recreate lunar calendar functionality:

```python
# Old way (lunar_calendar module)
from ketu import generate_lunar_calendar
calendar = generate_lunar_calendar(2024, 1)

# New way (aspect_timelines module)
from ketu import generate_aspect_timeline
timeline = generate_aspect_timeline(
    body1="Sun", body2="Moon",
    start_date="2024-01-01", end_date="2024-01-31",
    detect_retrograde=False
)
```

## Advanced Use Cases

### Multi-Planet Analysis

To analyze multiple planet pairs, generate separate timelines and merge:

```python
from ketu.aspects import generate_aspect_timeline
import numpy as np

# Generate multiple timelines
mars_sun = generate_aspect_timeline("Sun", "Mars", "2024-01-01", "2024-12-31")
venus_jupiter = generate_aspect_timeline("Venus", "Jupiter", "2024-01-01", "2024-12-31")
mercury_saturn = generate_aspect_timeline("Mercury", "Saturn", "2024-01-01", "2024-12-31")

# Get NumPy arrays
data_ms = mars_sun.to_numpy()
data_vj = venus_jupiter.to_numpy()
data_ms = mercury_saturn.to_numpy()

# Combine arrays (or convert to pandas if needed for complex merging)
import pandas as pd
df_list = [
    pd.DataFrame(mars_sun.to_numpy()).assign(pair="Mars-Sun"),
    pd.DataFrame(venus_jupiter.to_numpy()).assign(pair="Venus-Jupiter"),
    pd.DataFrame(mercury_saturn.to_numpy()).assign(pair="Mercury-Saturn"),
]
df_all = pd.concat(df_list).sort_values('julian_day')

print(f"Total events: {len(df_all)}")
print(df_all.groupby('pair').size())
```

### Cycle Phase Classification

Classify events by cycle phase:

```python
timeline = generate_aspect_timeline("Sun", "Mars", "2024-01-01", "2024-12-31")
data = timeline.to_numpy()

# Classify by aspect type (cycle phase)
def classify_phase(aspect_angle):
    if aspect_angle == 0:
        return "Conjunction (New)"
    elif aspect_angle == 90:
        return "Square (Challenge)"
    elif aspect_angle == 120:
        return "Trine (Harmony)"
    elif aspect_angle == 180:
        return "Opposition (Peak)"
    else:
        return "Other"

# Vectorized classification
import numpy as np
phases = np.vectorize(classify_phase)(data['aspect_type'])
unique, counts = np.unique(phases, return_counts=True)
for phase, count in zip(unique, counts):
    print(f"{phase}: {count}")
```

### Time Series Resampling

Create regular time series from irregular events:

```python
import pandas as pd
import numpy as np

timeline = generate_aspect_timeline("Sun", "Moon", "2024-01-01", "2024-12-31")
data = timeline.to_numpy()

# Convert to pandas for time series resampling
df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['julian_day'], unit='D', origin='julian')
df.set_index('timestamp', inplace=True)

# Create daily time series
daily_index = pd.date_range("2024-01-01", "2024-12-31", freq='D')
daily_df = pd.DataFrame(index=daily_index)

# Add aspect strength (max per day)
daily_df = daily_df.join(
    df.groupby(df.index.date)['aspect_strength'].max(),
    how='left'
)

# Fill missing days with 0 (no aspect)
daily_df = daily_df.fillna(0)

print(daily_df.head(10))
```

## API Reference

### generate_aspect_timeline()

```python
def generate_aspect_timeline(
    body1: Union[str, int],
    body2: Union[str, int],
    start_date: Union[datetime, str],
    end_date: Union[datetime, str],
    aspects_list: Optional[List[Union[str, int, float]]] = None,
    timezone: Optional[Union[str, ZoneInfo]] = None,
    detect_retrograde: bool = True,
) -> AspectTimeline
```

**Parameters:**

- `body1`: First body (name like "Sun" or ID like 0)
- `body2`: Second body (name like "Mars" or ID like 4)
- `start_date`: Start of timeline (datetime or ISO string)
- `end_date`: End of timeline (datetime or ISO string)
- `aspects_list`: List of aspects to include (default: BIG_FIVE)
- `timezone`: Timezone for display (default: UTC)
- `detect_retrograde`: Enable retrograde detection (default: True)

**Returns:** `AspectTimeline` object with events and export methods

**Available Aspects:**
- By name: "Conjunction", "Sextile", "Square", "Trine", "Opposition"
- By ID: 0, 1, 2, 3, 4
- By angle: 0.0, 60.0, 90.0, 120.0, 180.0
- Default: All BIG_FIVE aspects

**Available Bodies:**
- By name: "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "MeanNode"
- By ID: 0-10

## Future Extensions

The framework is designed to support:

1. **Multiple bodies** - Aspects between 3+ bodies simultaneously
2. **Custom orbs** - Per-aspect orb configuration
3. **Aspect patterns** - Grand trines, T-squares, etc.
4. **Harmonic analysis** - Non-traditional aspects
5. **Parallel processing** - Multi-core timeline generation
6. **Streaming API** - Event-by-event generation for very long periods

## See Also

- [examples/aspect_timeline_demo.py](../examples/aspect_timeline_demo.py) - Complete demonstration
- [tests/test_aspect_timelines.py](../tests/test_aspect_timelines.py) - Unit tests
- [aspect_windows module](../ketu/aspect_windows.py) - Low-level API
- [lunar_calendar module](../ketu/lunar_calendar.py) - Traditional lunar calendars
