# API Reference

## Overview

```python
import ketu
```

Ketu's API is organized into several categories:

- **Data**: Structured arrays for bodies and aspects
- **Conversions**: Time and coordinates
- **Calculations**: Positions and aspects
- **Utilities**: Display and helpers

## Data

### `bodies`

```python
ketu.bodies: numpy.ndarray
```

Structured array containing celestial body information.

**Structure:**

- `name` (S12): Body name
- `id` (i4): Swiss Ephemeris identifier
- `orb` (f4): Orb in degrees
- `speed` (f4): Average speed in °/day

**Example:**

```python
>>> ketu.bodies["name"][:3]
array([b'Sun', b'Moon', b'Mercury'], dtype='|S12')

>>> ketu.bodies["orb"][:3]
array([12., 12., 8.], dtype=float32)
```

### `aspects`

```python
ketu.aspects: numpy.ndarray
```

Structured array of astrological aspects.

**Structure:**

- `name` (S12): Aspect name
- `value` (f4): Angle in degrees
- `coef` (f4): Coefficient for orb calculation

**Example:**

```python
>>> ketu.aspects["name"]
array([b'Conjunction', b'Semi-sextile', b'Sextile', ...])

>>> ketu.aspects["value"]
array([0., 30., 60., 90., 120., 150., 180.])
```

### `signs`

```python
ketu.signs: List[str]
```

List of zodiac signs.

```python
>>> ketu.signs[0]
'Aries'
>>> ketu.signs[11]
'Pisces'
```

## Time Conversions

### `local_to_utc()`

```python
def local_to_utc(dtime: datetime, zoneinfo: ZoneInfo = None) -> datetime
```

Converts a local datetime to UTC.

**Parameters:**

- `dtime`: datetime to convert
- `zoneinfo`: timezone (optional if dtime already has tzinfo)

**Returns:** datetime in UTC

**Example:**

```python
paris = ZoneInfo("Europe/Paris")
local = datetime(2024, 1, 1, 12, 0, tzinfo=paris)
utc = ketu.local_to_utc(local)
```

### `utc_to_julian()`

```python
def utc_to_julian(dtime: datetime) -> float
```

Converts a UTC datetime to Julian Day.

**Parameters:**

- `dtime`: datetime (UTC or with tzinfo)

**Returns:** Julian Day (float)

**Example:**

```python
dt = datetime(2024, 1, 1, 12, 0)
jday = ketu.utc_to_julian(dt)
# jday = 2460310.0
```

## Angular Conversions

### `decimal_degrees_to_dms()`

```python
def decimal_degrees_to_dms(deg: float) -> numpy.ndarray
```

Converts decimal degrees to degrees, minutes, seconds.

**Parameters:**

- `deg`: angle in decimal degrees

**Returns:** array [degrees, minutes, seconds]

**Example:**

```python

>>> ketu.decimal_degrees_to_dms(123.456)
array([123, 27, 21], dtype=int32)
```

### `distance()`

```python
def distance(pos1: float, pos2: float) -> float
```

Calculates the angular distance between two positions.

**Parameters:**

- `pos1`, `pos2`: positions in degrees

**Returns:** distance in degrees (0-180)

**Example:**

```python
>>> ketu.distance(10, 350)
20.0  # Shortest path
```

### `get_orb()`

```python
def get_orb(body1: int, body2: int, asp: int) -> float
```

Calculates the orb for an aspect between two bodies.

**Parameters:**

- `body1`, `body2`: body indices
- `asp`: aspect index

**Returns:** maximum orb in degrees

## Position Functions

### `body_properties()`

```python
@lru_cache
def body_properties(jday: float, body: int) -> numpy.ndarray
```

Calculates all properties of a body (cached function).

**Parameters:**

- `jday`: Julian Day
- `body`: Body ID

**Returns:** array [longitude, latitude, distance, vlong, vlat, vdist]

### `long()`, `lat()`, `dist_au()`

```python
def long(jday: float, body: int) -> float
def lat(jday: float, body: int) -> float
def dist_au(jday: float, body: int) -> float
```

Return respectively the longitude, latitude and distance of a body.

**Parameters:**

- `jday`: Julian Day
- `body`: Body ID (0=Sun, 1=Moon, etc.)

**Returns:** value in degrees or AU

### `vlong()`, `vlat()`, `vdist_au()`

```python
def vlong(jday: float, body: int) -> float
def vlat(jday: float, body: int) -> float
def vdist_au(jday: float, body: int) -> float
```

Movement speeds (degrees/day or AU/day).

## Analysis Functions

### `is_retrograde()`

```python
def is_retrograde(jday: float, body: int) -> bool
```

Checks if a body is retrograde.

**Example:**

```python
if ketu.is_retrograde(jday, 2):  # Mercury
    print("Mercury retrograde!")
```

### `is_ascending()`

```python
def is_ascending(jday: float, body: int) -> bool
```

Checks if a body's latitude is increasing.

### `body_sign()`

```python
def body_sign(b_long: float) -> numpy.ndarray
```

Determines the sign and exact position.

**Parameters:**

- `b_long`: longitude in degrees

**Returns:** array [sign, degrees, minutes, seconds]

`body_name()` and `body_id()`

```python
def body_name(body: int) -> str
def body_id(b_name: str) -> int
```

Conversion between ID and name of a body.

## Aspect Calculations

### `get_aspect()`

```python
def get_aspect(jday: float, body1: int, body2: int) -> Optional[Tuple]
```

Calculates the aspect between two bodies.

**Returns:** tuple (body1, body2, aspect_id, orb) or None

### `calculate_aspects()`

```python
def calculate_aspects(jday: float, l_bodies=bodies) -> numpy.ndarray
```

Calculates all aspects between bodies.

**Returns:** structured array of aspects

### `positions()`

```python
def positions(jday: float, l_bodies=bodies) -> numpy.ndarray
```

Calculates all body longitudes.

## Display Functions

### `print_positions()` and `print_aspects()`

```python
def print_positions(jday: float) -> None
def print_aspects(jday: float) -> None
```

Display formatted positions and aspects.

## Main Function

### `main()`

```python
def main() -> None
```

Entry point for the interactive CLI interface.

## Technical Notes

- Calculations use `@lru_cache` to optimize performance
- Body IDs follow the Swiss Ephemeris convention
- Angles are always in degrees (0-360)
- Time precision is approximately 1 second

## See Also

- [Concepts](concepts.md) for theory
- [Examples](examples.md) for more use cases
- [Swiss Ephemeris](https://www.astro.com/swisseph/) for technical details
