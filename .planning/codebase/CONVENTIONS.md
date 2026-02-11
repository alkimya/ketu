# Coding Conventions

**Analysis Date:** 2026-02-12

## Naming Patterns

**Files:**
- Lowercase with underscores: `calculations.py`, `lunar_calendar.py`
- Package directories: lowercase plural or singular: `ketu/ephemeris/`, `ketu/aspects/`, `ketu/cycles/`
- Test files: `test_*.py` prefix pattern (e.g., `test_ketu.py`, `test_complex.py`)

**Functions:**
- snake_case for all functions: `utc_to_julian()`, `calculate_aspects()`, `find_aspect_window()`
- Descriptive verb prefixes: `calculate_*`, `find_*`, `get_*`, `is_*`, `generate_*`, `to_*`
- Private/internal functions: prefix with underscore: `_get_body_id()`, `_body_properties_uncached()`

**Variables:**
- snake_case: `jdate`, `jd_array`, `aspect_angle`, `body1_lon`
- Boolean prefixes: `is_retrograde`, `in_aspect`, `in_orb`, `CACHE_AVAILABLE`
- Structured array fields: snake_case in dtype definitions: `angular_separation`, `cycle_progress`, `aspect_distance`
- Constants: UPPERCASE: `DEFAULT_PAIRS`, `CYCLE_DTYPE`, `MAJOR_ASPECTS`

**Types/Classes:**
- PascalCase: `ZodiacPoint`, `CycleRatio`, `Aspect`, `LunarCycle`, `LunarCalendar`, `AspectWindow`
- NamedTuple classes: PascalCase: `AspectMoment`, `TransitMoment`, `NatalPosition`, `AspectEvent`, `TransitAspect`
- Exceptions: PascalCase with Error suffix (implied or explicit): `ValueError`, `ImportError`

## Code Style

**Formatting:**
- No external formatter configured; follows PEP 8
- Line length: Implicit but generally 100-120 characters based on code samples
- Imports grouped logically (see Import Organization below)

**Linting:**
- pytest with coverage enabled via pyproject.toml configuration
- No explicit linter config (no .flake8, .pylintrc)
- Type hints expected throughout (see Type Hints section)

## Type Hints

**Required:**
- All function parameters must have type hints: `jdate: float`, `body: int`, `timestamps: Union[np.ndarray, List[datetime]]`
- All function return types must be specified: `-> float`, `-> np.ndarray`, `-> Optional[Tuple]`
- Union types with `Optional` for nullable returns: `-> Optional[Tuple]`, `-> Union[float, np.ndarray]`

**Patterns:**
- NumPy arrays: `np.ndarray` with description of shape/dtype in docstring
- Lists/collections: `List[datetime]`, `Sequence[Union[str, int]]`
- Callable: `Optional[Union[str, ZoneInfo]]` for flexible parameter types

**Example from `cycles/calculator.py`:**
```python
def generate_cycle_series(
    body1: Union[str, int],
    body2: Union[str, int],
    timestamps: Union[np.ndarray, List[datetime], "pd.DatetimeIndex"],
    include_aspects: bool = True,
    use_cache: bool = True,
) -> np.ndarray:
```

## Import Organization

**Order (enforced in practice):**
1. Standard library (future imports, then standard): `from __future__ import annotations`, `from functools import lru_cache`, `from datetime import datetime`
2. Third-party libraries: `import numpy as np`, `import pytest`
3. Local package imports: `from ketu.core import bodies, aspects`, `from .calculations import positions`

**Path Aliases:**
- Relative imports within package: `from .core import bodies`, `from .ephemeris.time import utc_to_julian`
- Absolute imports for ketu submodules: `from ketu.core import bodies`, `from ketu.complex import degrees_to_complex`
- Optional dependency imports wrapped in try/except:
  ```python
  try:
      from ketu.cache import EphemerisCache, get_default_cache
      CACHE_AVAILABLE = True
  except ImportError:
      CACHE_AVAILABLE = False
  ```

**Barrel Files (used for API):**
- `ketu/__init__.py`: Comprehensive re-export of all public APIs with `__all__` list
- `ketu/aspects/__init__.py`: Imports from submodules (calculator, windows, timelines, transits)
- `ketu/export/__init__.py`: Conditional exports based on optional dependency availability

## Error Handling

**Patterns:**
- Explicit exceptions with informative messages: `raise ValueError(f"Unknown body: {body}")`
- Type validation at function entry: Check parameter types before use
- Missing optional dependencies: Wrap in try/except at import time and raise ImportError with install instructions at function call

**Examples:**
```python
# From ephemeris/planets.py
planet_name = SWE_IDS.get(planet_id)
if planet_name is None:
    raise ValueError(f"Unknown planet ID: {planet_id}")

# From export/icalendar.py
if not ICALENDAR_AVAILABLE:
    raise ImportError(
        "icalendar library is required for export functions. "
        "Install with: pip install icalendar"
    )
```

**No custom exceptions:** Use standard library exceptions (ValueError, ImportError, etc.)

## Comments

**When to Comment:**
- Complex calculations: Explain the mathematical rationale
- Non-obvious algorithms: Document the approach
- Important caveats: "NumPy implementation uses Gregorian proleptic calendar"
- Inline comments for structured array field meanings

**Style:**
- Inline comments after code: `return (orbs[body1] + orbs[body2]) / 2 * coef[asp]  # Orb tolerance`
- Block comments above logical sections: Separate with blank lines
- Comments end with period: `# Moon speed ~13°/day.`

**No Over-Commenting:**
- Don't duplicate code in comments
- Self-documenting code preferred: Clear function/variable names
- Comments that contradict code are worse than no comments

## Docstrings

**Required:**
- All public functions: Must have docstring
- All classes: Must have docstring with Attributes section
- All methods: Must have docstring

**Format:** Google-style docstrings with sections:
```python
def get_aspect(jdate: float, body1: int, body2: int) -> Optional[Tuple]:
    """Find aspect between two bodies at a given date.

    Args:
        jdate: Julian Date
        body1: First body ID
        body2: Second body ID

    Returns:
        Tuple of (body1, body2, aspect_index, orb) or None if no aspect
    """
```

**Sections used:**
- Args: Parameter descriptions (type + description)
- Returns: Return value type and description
- Raises: Exception types (not always used; not needed if no exceptions)
- Example: Usage examples for complex functions (sometimes used)

**Module docstrings:**
- Required at top of every .py file
- Describe purpose and sometimes list submodules/exports
- Example from `calculations.py`:
  ```python
  """Astronomical and astrological calculations for Ketu.

  This module contains position, velocity, and time conversion calculations
  for planetary bodies. For aspect calculations, see the aspects module.
  """
  ```

## Function Design

**Size:**
- Functions typically 10-50 lines
- Vectorized functions larger (50-150 lines) with heavy NumPy operations: `calculate_aspects_batch()`

**Parameters:**
- Positional parameters for required values: `jdate`, `body1`, `body2`
- Keyword-only parameters for optional behavior: `include_aspects: bool = True`, `use_cache: bool = True`
- Union types for flexible input: `body: Union[str, int]`, `timestamps: Union[np.ndarray, List[datetime]]`

**Return Values:**
- Scalar numpy types or native Python: `float`, `int`, `bool`
- NumPy arrays for bulk data: `np.ndarray` (dtype specified in docstring)
- NamedTuple or dataclass for structured results: `AspectWindow`, `CycleState`
- List of structured results: `List[np.ndarray]`, `List[TransitWindow]`
- None for optional returns: `Optional[Tuple]`, `-> Optional[int]`

**Example from `aspects/calculator.py`:**
```python
def get_orb(body1: int, body2: int, asp: int) -> float:
    """Calculate the orb tolerance for two bodies and an aspect.

    Args:
        body1: First body ID (0-12)
        body2: Second body ID (0-12)
        asp: Aspect index (0-6)

    Returns:
        Orb in degrees
    """
    orbs, coef = bodies["orb"], aspects["coef"]
    return (orbs[body1] + orbs[body2]) / 2 * coef[asp]
```

## Module Design

**Exports:**
- `__all__` list in every module with public API: See `ketu/__init__.py` (246 lines)
- Public functions/classes: No underscore prefix
- Private/internal: Underscore prefix (`_get_body_id`)

**Structured Arrays:**
- Heavily used as primary data structure for performance (ML-ready)
- Defined as module-level constants: `CYCLE_DTYPE`, `MAJOR_ASPECTS_Z`
- Fields documented in both dtype and docstring:
  ```python
  CYCLE_DTYPE = np.dtype([
      ('julian_day', 'f8'),           # Julian date
      ('body1_id', 'i2'),             # First body ID
      # ... more fields
  ])
  ```

**Example Package Structure (from `ketu/aspects/`):**
- `__init__.py`: Re-exports from submodules + `__all__`
- `calculator.py`: Core aspect calculations (get_aspect, calculate_aspects, calculate_aspects_batch)
- `windows.py`: Aspect timing detection (AspectWindow, find_aspect_window)
- `timelines.py`: ML-ready time series (AspectTimeline, generate_aspect_timeline)
- `transits.py`: Transit calculations (find_transits_to_position, compare_dates_transits)

**No barrel files for internal use:** Import directly from source modules in implementation code

## Vectorization Patterns

**NumPy-first philosophy:**
- Single calculations via scalar functions: `get_orb(body1, body2, asp) -> float`
- Multiple calculations via broadcasting: Use NumPy arrays and vectorized operations
- Batch operations with explicit names: `calculate_aspects_batch()`, `calc_planet_position_batch()`

**Example from `aspects/calculator.py`:**
```python
# Vectorized distance calculation
pos1 = all_positions[i_indices]
pos2 = all_positions[j_indices]
all_distances = distance(pos1, pos2)  # type: ignore[arg-type]

# Vectorized orb checking
in_orb = (all_distances >= aspect_angle - orbs) & (all_distances <= aspect_angle + orbs)
```

---

*Convention analysis: 2026-02-12*
