# AGENTS.md - Developer Guidelines for Ketu

Ketu is a pure Python library for astronomical cycle calculations and planetary ephemeris.
- **Language**: Python 3.10+ | **Key dependency**: NumPy | **Venv**: `venv/` (NOT `.venv/)

---

## Development Environment

```bash
cd /home/loc/workspace/ketu
source venv/bin/activate
pip install -e ".[dev]"
```

---

## Running Tests

```bash
# Full suite with coverage
pytest tests/ -v --cov=ketu --cov-report=term-missing

# Single test file
pytest tests/test_ketu.py -v

# Single test function
pytest tests/test_ketu.py::TestData::test_bodies_structure -v

# Pattern matching
pytest tests/ -k "test_aspect" -v

# Skip slow tests
pytest tests/ -m "not slow" -v
```

---

## Type Checking

```bash
# mypy strict
mypy ketu/ --strict

# Full verification (mypy + pytest)
./verify_mypy.sh

# Some modules have relaxed type checking (see pyproject.toml)
# Run mypy on specific modules for faster feedback
mypy ketu/core.py ketu/display.py
```

### Coverage Requirements

- Minimum coverage: **70%** (configured in pyproject.toml)
- Run with: `pytest tests/ --cov=ketu --cov-report=term-missing`
- Coverage omits: `ketu/__main__.py`, `ketu/lunar_calendar.py`, and tests/

---

## External Dependencies

- **swisseph**: Optional C library for ephemeris calculations (type-checker ignores missing imports)

---

## Code Style Guidelines

### General Principles

- **PEP 8** compliant (Black defaults)
- **Type hints** required on all functions
- **Docstrings** on all public functions (Google style)
- **NumPy first**: Use structured arrays for ML interoperability
- **DateTime always UTC**: Never use naive datetime objects

### Imports Order

```python
# Standard library first
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional

# Third-party
import numpy as np

# Local application
from ketu.core import bodies, aspects, signs
from ketu.calculations import local_to_utc, utc_to_julian, body_name
```

### Naming Conventions

- **Variables/functions**: `snake_case` (e.g., `body_name`, `calculate_aspect`)
- **Classes**: `PascalCase` (e.g., `TestData`, `CycleState`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_PAIRS`, `MAJOR_ASPECTS`)
- **Modules**: `snake_case` (e.g., `ephemeris_cache.py`)

### Type Hints

```python
def calculate_aspect(jdate: float, body1: str, body2: str) -> tuple[int, int, int, float] | None:
    ...

def get_cycles(timestamps: np.ndarray) -> np.ndarray:
    """Return structured array with CYCLE_DTYPE."""
    ...
```

**Note**: Some modules (`ketu.calculations`, `ketu.complex`, `ketu.cycles.*`, `ketu.ephemeris.*`, `ketu.aspects.*`, `ketu.cache.ephemeris_cache`) have relaxed type checking per pyproject.toml. New code should still use full type hints when possible.

### NumPy Conventions

- Use structured arrays for tabular data
- Use `np.dtype` for type definitions
- Vectorize operations (avoid Python loops)
- Use `datetime64[s]` for timestamps

### Docstrings (Google Style)

```python
def utc_to_julian(dt: datetime, tz: ZoneInfo | None = None) -> float:
    """Convert datetime to Julian day number.

    Args:
        dt: UTC datetime to convert.
        tz: Optional timezone. If None, assumes UTC.

    Returns:
        Julian day number (fractional days).

    Raises:
        ValueError: If datetime is invalid.
    """
```

### Error Handling

- Use specific exception types
- Validate inputs early with clear error messages

```python
def body_id(name: str) -> int:
    if not isinstance(name, str):
        raise TypeError(f"Expected str, got {type(name).__name__}")
    idx = np.where(bodies['name'] == name.encode())[0]
    if len(idx) == 0:
        raise ValueError(f"Unknown body: {name}")
    return int(bodies['id'][idx[0]])
```

### Body IDs

`0=Sun, 1=Moon, 2=Mercury, 3=Venus, 4=Mars, 5=Jupiter, 6=Saturn, 7=Uranus, 8=Neptune, 9=Pluto, 10=Rahu, 11=Ketu, 12=Lilith`

---

## Commit Message Conventions

- `feat`: new feature
- `fix`: bug fix
- `docs`: documentation update
- `test`: tests only
- `refactor`: code changes that neither fix nor add a feature
- `chore`: maintenance, tooling

---

## Before Opening a PR

- [ ] Tests pass: `pytest tests/`
- [ ] Type checking passes: `mypy ketu/ --strict`
- [ ] Coverage maintained or improved
- [ ] Code follows PEP 8
- [ ] Docstrings updated
- [ ] CHANGELOG.md updated if applicable
