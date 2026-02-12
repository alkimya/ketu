# Ketu Examples

This folder contains practical examples of how to use the Ketu library.

## List of examples

### 01 - Basic planetary positions

**File**: [`01_basic_positions.py`](01_basic_positions.py)

Fundamental calculations:

- Conversion of dates to Julian days
- Obtaining positions (longitude, latitude, distance)
- Determining zodiac signs
- Detecting retrogrades

```bash
python examples/01_basic_positions.py
```

### 02 - Astrological aspects

**File**: [`02_aspects.py`](02_aspects.py)

Aspect calculations:

- Aspect between two specific planets
- Calculation of all aspects at the moment
- Filtering by orb (close, exact)
- Detailed presentation

```bash
python examples/02_aspects.py
```

### 03 - Time series

**File**: [`04_time_series.py`](04_time_series.py)

Calculations over several days:

- Evolution of planetary positions
- Detection of sign changes
- Retrogradation periods
- Statistics (min, max, average speed)

```bash
python examples/04_time_series.py
```

## Usage

### Prerequisites

```bash
pip install ketu
# or from source:
pip install -e .
```

### Execution

All examples are standalone Python scripts:

```bash
# From the project root
python examples/01_basic_positions.py
python examples/02_aspects.py
# etc.

# Or make them executable
chmod +x examples/*.py
./examples/01_basic_positions.py
```

## Complete documentation

For more details, see the documentation:

- [Quick start guide](../docs/source/quickstart.md)
- [API Reference](../docs/source/api.md)
- [Astrological Concepts](../docs/source/concepts.md)
- [Online Documentation](https://ketu.readthedocs.io)

## Use Cases

### Transit Analysis

```python
# See example 04 - Time series
detect_sign_changes(start_date, 365, 0)  # Sun over 1 year
```

### Search for tight aspects

```python
# See example 02 - Aspects
tight_aspects = [asp for asp in aspects if abs(asp[3]) < 1]
```

## Tips

### Performance

Calculations use an automatic LRU cache. For loops on many dates:

```python
# Clears the cache if necessary
ketu.body_properties.cache_clear()
```

---

For any questions: <https://github.com/alkimya/ketu/issues>
