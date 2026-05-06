# Architecture Patterns

**Domain:** Python astronomical calculation library
**Researched:** 2026-02-12
**Context:** Brownfield consolidation - documenting clean API patterns for 1.0

## Recommended Architecture

Ketu should be a **pure calculation library** with three-layer architecture:

```
┌─────────────────────────────────────────┐
│   Public API (ketu/__init__.py)         │  ← Type-hinted, documented, stable
│   - Cycle calculations                   │
│   - Aspect calculations                  │
│   - Ephemeris queries                    │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│   Internal Modules (ketu/*/*)            │  ← Implementation details
│   - ketu.cycles.*                        │
│   - ketu.aspects.*                       │
│   - ketu.ephemeris.*                     │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│   External Dependencies                  │
│   - swisseph (calculations)              │
│   - numpy (data structures)              │
└─────────────────────────────────────────┘
```

### Component Boundaries

| Component | Responsibility | Communicates With | Public? |
|-----------|---------------|-------------------|---------|
| `ketu/__init__.py` | Public API surface, exports only | All internal modules | YES |
| `ketu.core` | Low-level swisseph wrappers | swisseph, numpy | NO (internal) |
| `ketu.cycles.*` | Cycle calculations, CYCLE_DTYPE | ketu.core, numpy | Partial (some functions) |
| `ketu.aspects.*` | Aspect finding, orbs, timelines | ketu.core, ketu.cycles | Partial (some functions) |
| `ketu.ephemeris.*` | Coordinate conversions, time utils | ketu.core, swisseph | Partial (some functions) |
| `ketu.cache.*` | Ephemeris caching | swisseph | NO (internal) |
| `ketu.complex` | Complex number cycle representation | ketu.cycles, numpy | YES (if integrated) |
| `ketu.resonance` | Resonance detection | ketu.cycles, ketu.complex | YES (if integrated) |
| `ketu.export.*` | Chart/iCalendar (REMOVE) | N/A | NO (deprecate) |

### Data Flow

All calculations follow the same pattern:

```
User Input (datetime, body names, parameters)
    ↓
Input Validation (check types, ranges, names)
    ↓
Normalize to NumPy arrays (np.atleast_1d)
    ↓
swisseph calculation (via ketu.core wrappers)
    ↓
Vectorized processing (NumPy operations)
    ↓
Structured Array Output (CYCLE_DTYPE or similar)
    ↓
User (pandas/polars/ML pipeline)
```

**No side effects** - Pure functions only:
- No global state modifications
- No file I/O (except swisseph ephemeris cache)
- No network calls
- Deterministic outputs for same inputs

## Patterns to Follow

### Pattern 1: Explicit Public API Surface

**What:** Only export intended public functions via `__all__`

**When:** Every module, especially `ketu/__init__.py`

**Example:**
```python
# ketu/__init__.py
from ketu.cycles.calculator import generate_cycle_series
from ketu.aspects.calculator import find_aspects
# ... other public functions ...

__all__ = [
    # Cycle functions
    "generate_cycle_series",
    "generate_multi_cycle_series",

    # Aspect functions
    "find_aspects",
    "aspect_timeline",

    # Ephemeris functions
    "planetary_position",

    # Constants
    "DEFAULT_PAIRS",
    "CYCLE_DTYPE",
]

# Version
__version__ = "1.0.0"
```

**Why:** API stability requires knowing what's public. Anything not in `__all__` can change.

### Pattern 2: Structured Array Returns

**What:** All calculation functions return NumPy structured arrays with named fields

**When:** Any function returning multiple related values

**Example:**
```python
import numpy as np
from typing import List
from datetime import datetime

# Define dtype
POSITION_DTYPE = np.dtype([
    ('timestamp', 'datetime64[s]'),
    ('body', 'U10'),
    ('longitude', 'f8'),
    ('latitude', 'f8'),
    ('distance', 'f8'),
])

def planetary_positions(
    timestamps: np.ndarray,  # datetime64[s]
    bodies: List[str],
) -> np.ndarray:  # POSITION_DTYPE
    """
    Calculate planetary positions.

    Parameters
    ----------
    timestamps : np.ndarray
        Array of UTC datetimes as datetime64[s]
    bodies : list of str
        Planet names (e.g., ['Sun', 'Moon', 'Mars'])

    Returns
    -------
    positions : np.ndarray
        Structured array with fields: timestamp, body, longitude, latitude, distance

    Examples
    --------
    >>> import numpy as np
    >>> from datetime import datetime, timezone
    >>> timestamps = np.array([datetime(2025, 1, 1, tzinfo=timezone.utc)], dtype='datetime64[s]')
    >>> positions = planetary_positions(timestamps, ['Sun', 'Moon'])
    >>> positions['longitude']  # Access by field name
    array([280.2, 305.7])
    """
    # Implementation...
    return result
```

**Why:**
- ML-ready (sklearn, xgboost expect NumPy arrays)
- Zero-copy to pandas: `pd.DataFrame(result)`
- Named access: `result['longitude']` more readable than `result[:, 2]`
- Type safety: dtype enforces structure

### Pattern 3: Scalar + Vector Polymorphism

**What:** Functions accept both scalar and array inputs, return matching shape

**When:** Any function that could reasonably be called with single or multiple values

**Example:**
```python
from typing import Union, overload
import numpy as np
from datetime import datetime

@overload
def cycle_phase(
    timestamp: datetime,
    body1: str,
    body2: str,
) -> float: ...

@overload
def cycle_phase(
    timestamp: np.ndarray,
    body1: str,
    body2: str,
) -> np.ndarray: ...

def cycle_phase(
    timestamp: Union[datetime, np.ndarray],
    body1: str,
    body2: str,
) -> Union[float, np.ndarray]:
    """
    Calculate cycle phase (0-360 degrees).

    Parameters
    ----------
    timestamp : datetime or np.ndarray
        Single datetime or array of datetimes
    body1 : str
        First body name
    body2 : str
        Second body name

    Returns
    -------
    phase : float or np.ndarray
        Phase in degrees (0-360). Scalar if input is scalar, array if input is array.
    """
    # Normalize to array
    timestamps = np.atleast_1d(timestamp)
    scalar_input = timestamps.shape == (1,)

    # Calculate (vectorized)
    phases = _calculate_phases(timestamps, body1, body2)

    # Return matching shape
    return float(phases[0]) if scalar_input else phases
```

**Why:**
- Natural for users (don't need separate functions)
- Enables REPL exploration (single dates) and production use (time series)
- Type hints with `@overload` give IDE support

### Pattern 4: Named Constants for Domain Values

**What:** Define constants for magic numbers and standard configurations

**When:** Aspect degrees, planetary names, configuration defaults

**Example:**
```python
# ketu/constants.py
from typing import Final, Literal

# Aspects
CONJUNCTION: Final = 0.0
SEXTILE: Final = 60.0
SQUARE: Final = 90.0
TRINE: Final = 120.0
OPPOSITION: Final = 180.0

# Default orbs (degrees)
DEFAULT_ORB: Final = 8.0
TIGHT_ORB: Final = 1.0

# Bodies
BodyName = Literal[
    "Sun", "Moon", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"
]

# Default cycle pairs for financial analysis
DEFAULT_PAIRS: Final = [
    ("Sun", "Moon"),
    ("Sun", "Mercury"),
    ("Sun", "Venus"),
    ("Sun", "Mars"),
    ("Sun", "Jupiter"),
    ("Sun", "Saturn"),
    ("Jupiter", "Saturn"),
    ("Mars", "Jupiter"),
    ("Venus", "Mars"),
]
```

**Why:**
- Self-documenting code
- Type safety with Literal types
- Easy to discover in IDE
- Centralizes domain knowledge

### Pattern 5: Explicit Validation with Context

**What:** Validate inputs early with helpful error messages

**When:** All public API functions

**Example:**
```python
def validate_body_name(body: str) -> None:
    """Validate planetary body name."""
    VALID_BODIES = {
        "Sun", "Moon", "Mercury", "Venus", "Mars",
        "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"
    }
    if body not in VALID_BODIES:
        raise ValueError(
            f"Unknown body '{body}'. Valid bodies are: {', '.join(sorted(VALID_BODIES))}"
        )

def validate_timestamp(timestamp: datetime) -> None:
    """Validate timestamp is in swisseph range."""
    # swisseph supports years -13200 to 16800
    if timestamp.year < -13200 or timestamp.year > 16800:
        raise ValueError(
            f"Date {timestamp} out of range. Swiss Ephemeris supports years "
            f"-13200 to 16800. For dates outside this range, consider using "
            f"JPL Horizons data."
        )

    if timestamp.tzinfo is None:
        raise ValueError(
            f"Timestamp {timestamp} must be timezone-aware. "
            f"Use datetime.now(timezone.utc) or timestamp.replace(tzinfo=timezone.utc)"
        )
```

**Why:**
- Fails fast with actionable messages
- Better than cryptic swisseph errors
- Guides users to solutions
- Documents constraints implicitly

## Anti-Patterns to Avoid

### Anti-Pattern 1: Object-Oriented Wrappers

**What goes wrong:** Creating classes for planets, aspects, cycles adds complexity without benefit

**Why it happens:** OOP feels natural, but astronomical calculations are inherently functional

**Consequences:**
- Harder to vectorize (objects don't play nice with NumPy)
- Stateful objects are harder to test
- Users just want numbers, not object graphs

**Instead:**
```python
# Bad: Objects
class Cycle:
    def __init__(self, body1, body2):
        self.body1 = body1
        self.body2 = body2

    def calculate(self, timestamp):
        # ...
        return self

# Good: Functions
def generate_cycle_series(timestamps, body1, body2) -> np.ndarray:
    # Returns structured array
    pass
```

### Anti-Pattern 2: Global Configuration State

**What goes wrong:** Module-level config (e.g., `ketu.set_orb(8.0)`) is hidden dependency

**Why it happens:** Seems convenient to set once, use everywhere

**Consequences:**
- Thread-unsafe
- Testing nightmares (state leaks between tests)
- Non-local behavior (function output depends on distant config call)

**Instead:**
```python
# Bad: Global state
_GLOBAL_ORB = 8.0

def set_orb(orb):
    global _GLOBAL_ORB
    _GLOBAL_ORB = orb

def find_aspects(timestamps, body1, body2):
    # Uses global _GLOBAL_ORB
    pass

# Good: Explicit parameters
def find_aspects(
    timestamps,
    body1,
    body2,
    orb_degrees: float = 8.0,
):
    # Explicit, local, pure
    pass
```

### Anti-Pattern 3: Mixed Return Types

**What goes wrong:** Sometimes return dict, sometimes array, sometimes custom object

**Why it happens:** Different use cases seem to need different types

**Consequences:**
- Users must check types before use
- Hard to compose functions
- IDE can't help

**Instead:**
```python
# Bad: Mixed types
def planetary_position(timestamp, body):
    if isinstance(timestamp, list):
        return np.array([...])  # Array
    else:
        return {'lon': ..., 'lat': ...}  # Dict

# Good: Consistent structured array
def planetary_position(timestamp, body):
    # Always returns structured array, even for single timestamp
    timestamps = np.atleast_1d(timestamp)
    result = np.zeros(len(timestamps), dtype=POSITION_DTYPE)
    # ...
    return result
```

### Anti-Pattern 4: Deep Module Hierarchies

**What goes wrong:** `ketu.aspects.core.calculator.find_aspects()` is too deep

**Why it happens:** Desire to organize code finely

**Consequences:**
- Hard to discover functionality
- Annoying to import
- Refactoring changes user code

**Instead:**
```python
# Bad: Deep nesting
from ketu.aspects.core.calculator import find_aspects

# Good: Flat public API
from ketu import find_aspects  # Re-exported in __init__.py
```

## Scalability Considerations

Ketu is a **calculation library**, not a service. Scalability is about:

1. **Large time series** (1M+ timestamps)
2. **Many bodies** (all planets simultaneously)
3. **Memory efficiency** (structured arrays, not objects)

| Concern | At 100 Timestamps | At 10K Timestamps | At 1M Timestamps |
|---------|-------------------|-------------------|------------------|
| **Memory** | NumPy arrays (~10KB) | NumPy arrays (~1MB) | NumPy arrays (~100MB), consider chunking |
| **Computation** | Instant | <1 second | ~10 seconds, document parallelization patterns |
| **Caching** | Ephemeris cache only | Same | Same (cache is per-body, not per-timestamp) |
| **Output** | Return full array | Return full array | Consider iterator pattern or chunked processing |

**Not Ketu's problem:**
- Distributed computation (users can parallelize with Dask/Ray)
- Database storage (users choose their storage)
- Real-time streaming (not a calculation library concern)

**Ketu's responsibility:**
- Vectorized calculations (avoid Python loops)
- Memory-efficient data structures (structured arrays)
- Document chunk-processing patterns for massive datasets

## Module Organization for 1.0

Recommended structure (remove anti-features):

```
ketu/
├── __init__.py          # Public API surface (__all__, version)
├── core.py              # Low-level swisseph wrappers (internal)
├── calculations.py      # Shared calculation utilities (internal)
├── constants.py         # Domain constants (partially public)
│
├── cycles/
│   ├── __init__.py      # Cycle exports
│   └── calculator.py    # Cycle calculations (CYCLE_DTYPE)
│
├── aspects/
│   ├── __init__.py      # Aspect exports
│   ├── core.py          # Aspect calculations
│   ├── windows.py       # Aspect timing windows
│   ├── timelines.py     # Aspect timelines
│   └── transits.py      # Transit detection
│
├── ephemeris/
│   ├── __init__.py      # Ephemeris exports
│   ├── planets.py       # Planetary positions
│   ├── coordinates.py   # Coordinate conversions
│   ├── time.py          # Time utilities
│   └── orbital.py       # Orbital elements
│
├── cache/
│   ├── __init__.py
│   └── ephemeris_cache.py  # Internal caching
│
├── complex.py           # Complex number representation (if integrated)
├── resonance.py         # Resonance detection (if integrated)
│
└── export/              # DEPRECATE & REMOVE in 1.0
    ├── chart.py         # Remove: visualization not calculation
    └── icalendar.py     # Remove: export not calculation
```

**Migration path for export/:**
1. Add `DeprecationWarning` in 1.0
2. Document migration in docs (use matplotlib/ics library directly)
3. Remove in 2.0

## Sources

**Confidence: HIGH**

Architecture patterns based on:
- NumPy API design (structured arrays, vectorization)
- SciPy module organization (flat public API, deep implementation)
- scikit-learn patterns (fit/transform separation, NumPy in/out)
- Functional programming principles (pure functions, no global state)
- Python packaging best practices (explicit exports, semantic versioning)

**Specific inspirations:**
- SciPy's public API design (scipy.__init__ exports)
- NumPy's structured arrays (best practice for tabular scientific data)
- Pandas' input flexibility (scalar or array inputs)
- scikit-learn's consistency (fit/transform pattern, but not applicable here)

**Not applicable to Ketu:**
- Microservices patterns (not a service)
- Database schema design (no persistence)
- API versioning strategies (package version is API version)
