"""Cycle state calculator for planetary pairs.

Calculates the instantaneous state of planetary cycles at given timestamps,
optimized for vectorized operations on large timestamp arrays.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Union, List, Optional, Tuple
import numpy as np

from ketu.core import bodies
from ketu.calculations import long, vlong, utc_to_julian, distance
from ketu.ephemeris.planets import calc_planet_position_batch

# Optional cache import
try:
    from ketu.cache import EphemerisCache, get_default_cache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    EphemerisCache = None
    get_default_cache = None


# Major aspects for proximity calculation
MAJOR_ASPECTS = np.array([0, 60, 90, 120, 180, 240, 270, 300, 360], dtype=np.float32)

# Structured array dtype for cycle state
CYCLE_DTYPE = np.dtype([
    ('julian_day', 'f8'),           # Julian date
    ('body1_id', 'i2'),             # First body ID
    ('body2_id', 'i2'),             # Second body ID
    ('body1_lon', 'f4'),            # Body 1 longitude (0-360°)
    ('body2_lon', 'f4'),            # Body 2 longitude (0-360°)
    ('angular_separation', 'f4'),   # Separation (0-360°, always positive direction)
    ('cycle_progress', 'f4'),       # Normalized progress (0.0-1.0)
    ('cycle_phase', 'i1'),          # 1=waxing (0→180), -1=waning (180→360)
    ('body1_velocity', 'f4'),       # Body 1 velocity (deg/day)
    ('body2_velocity', 'f4'),       # Body 2 velocity (deg/day)
    ('relative_velocity', 'f4'),    # Relative velocity (deg/day)
    ('body1_retro', '?'),           # Body 1 retrograde
    ('body2_retro', '?'),           # Body 2 retrograde
    ('nearest_aspect', 'f4'),       # Nearest major aspect angle
    ('aspect_distance', 'f4'),      # Distance to nearest aspect (signed)
    ('in_aspect', '?'),             # Within orb of an aspect
    ('aspect_orb', 'f4'),           # Orb if in aspect, else 0
])


@dataclass
class CycleState:
    """Instantaneous state of a planetary cycle.

    Attributes:
        julian_day: Julian date of calculation
        body1_id: First body ID
        body2_id: Second body ID
        body1_lon: Longitude of body 1 (0-360°)
        body2_lon: Longitude of body 2 (0-360°)
        angular_separation: Angular distance (0-360°, in direction of cycle)
        cycle_progress: Normalized progress through cycle (0.0-1.0)
        cycle_phase: 1 for waxing (0→180°), -1 for waning (180→360°)
        body1_velocity: Velocity of body 1 (deg/day)
        body2_velocity: Velocity of body 2 (deg/day)
        relative_velocity: Relative velocity (deg/day)
        body1_retro: Is body 1 retrograde
        body2_retro: Is body 2 retrograde
        nearest_aspect: Nearest major aspect angle
        aspect_distance: Signed distance to nearest aspect
        in_aspect: Whether currently within orb of an aspect
        aspect_orb: Current orb value if in aspect
    """
    julian_day: float
    body1_id: int
    body2_id: int
    body1_lon: float
    body2_lon: float
    angular_separation: float
    cycle_progress: float
    cycle_phase: int
    body1_velocity: float
    body2_velocity: float
    relative_velocity: float
    body1_retro: bool
    body2_retro: bool
    nearest_aspect: float
    aspect_distance: float
    in_aspect: bool
    aspect_orb: float


def _get_body_id(body: Union[str, int]) -> int:
    """Convert body name or ID to ID."""
    if isinstance(body, int):
        return body
    body_idx = np.where(bodies["name"] == body.encode())[0]
    if len(body_idx) == 0:
        raise ValueError(f"Unknown body: {body}")
    return int(bodies["id"][body_idx[0]])


def _calculate_separation(lon1: float, lon2: float) -> float:
    """Calculate angular separation in cycle direction (0-360°).

    The separation is measured from body1 to body2 in the direction
    of the zodiac (counterclockwise). This gives a continuous 0-360° value
    representing position in the synodic cycle.

    Args:
        lon1: Longitude of body 1 (typically faster body)
        lon2: Longitude of body 2 (typically slower body)

    Returns:
        Separation in degrees (0-360°)
    """
    sep = (lon2 - lon1) % 360
    return sep


def _find_nearest_aspect(separation: Union[float, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
    """Find nearest major aspect and signed distance to it.

    Args:
        separation: Angular separation(s) in degrees

    Returns:
        Tuple of (nearest_aspect_angle, signed_distance)
    """
    sep = np.atleast_1d(separation)

    # Calculate distance to each major aspect
    distances = np.zeros((len(sep), len(MAJOR_ASPECTS)))
    for i, aspect in enumerate(MAJOR_ASPECTS):
        # Signed distance (negative = approaching, positive = separating)
        diff = sep - aspect
        # Normalize to -180 to 180
        diff = ((diff + 180) % 360) - 180
        distances[:, i] = diff

    # Find nearest (smallest absolute distance)
    abs_distances = np.abs(distances)
    nearest_idx = np.argmin(abs_distances, axis=1)

    nearest_aspect = MAJOR_ASPECTS[nearest_idx]
    signed_distance = distances[np.arange(len(sep)), nearest_idx]

    # Handle 360° = 0° case
    nearest_aspect = np.where(nearest_aspect == 360, 0, nearest_aspect)

    if len(sep) == 1:
        return float(nearest_aspect[0]), float(signed_distance[0])

    return nearest_aspect.astype(np.float32), signed_distance.astype(np.float32)


def _calculate_orb(body1_id: int, body2_id: int, aspect_angle: float) -> float:
    """Calculate orb tolerance for aspect.

    Uses traditional orb system based on planetary speeds.
    """
    # Get base orbs from bodies array
    orb1 = float(bodies["orb"][body1_id])
    orb2 = float(bodies["orb"][body2_id])

    # Average orb, scaled by aspect coefficient
    # Major aspects (0, 90, 120, 180) get larger orbs
    if aspect_angle in [0, 180]:
        coef = 1.0
    elif aspect_angle in [90, 120, 270, 240]:
        coef = 0.75
    elif aspect_angle in [60, 300]:
        coef = 0.5
    else:
        coef = 0.25

    return (orb1 + orb2) / 2 * coef


def generate_cycle_series(
    body1: Union[str, int],
    body2: Union[str, int],
    timestamps: Union[np.ndarray, List[datetime], "pd.DatetimeIndex"],
    include_aspects: bool = True,
    use_cache: bool = True,
    cache: Optional["EphemerisCache"] = None,
) -> np.ndarray:
    """Generate cycle state series for a planetary pair.

    Calculates the instantaneous state of the cycle between two bodies
    at each provided timestamp. Optimized for vectorized operations.

    Args:
        body1: First body (name or ID) - typically the faster body
        body2: Second body (name or ID) - typically the slower body
        timestamps: Array of timestamps (datetime or Julian dates)
        include_aspects: Calculate aspect proximity info (default: True)
        use_cache: Use EphemerisCache for faster lookups (default: True)
        cache: Optional EphemerisCache instance (uses default if None)

    Returns:
        Structured numpy array with CYCLE_DTYPE

    Example:
        >>> import pandas as pd
        >>> from ketu.cycles import generate_cycle_series
        >>>
        >>> timestamps = pd.date_range("2025-01-01", "2025-12-31", freq="1D")
        >>> cycles = generate_cycle_series("Sun", "Mars", timestamps)
        >>> print(cycles['angular_separation'][:5])
    """
    # Convert body names to IDs
    body1_id = _get_body_id(body1)
    body2_id = _get_body_id(body2)

    # Convert timestamps to Julian dates
    if hasattr(timestamps, 'to_pydatetime'):
        # pandas DatetimeIndex
        dts = timestamps.to_pydatetime()
        jds = np.array([utc_to_julian(dt) for dt in dts])
    elif isinstance(timestamps, np.ndarray):
        if timestamps.dtype.kind == 'M':  # datetime64
            # Convert numpy datetime64 to python datetime
            dts = timestamps.astype('datetime64[us]').astype(datetime)
            jds = np.array([utc_to_julian(dt) for dt in dts])
        elif timestamps.dtype.kind == 'f':  # float (Julian dates)
            jds = timestamps
        else:
            raise ValueError(f"Unsupported timestamp dtype: {timestamps.dtype}")
    else:
        # List of datetimes
        jds = np.array([utc_to_julian(dt) for dt in timestamps])

    n = len(jds)

    # Allocate result array
    result = np.zeros(n, dtype=CYCLE_DTYPE)

    # Fill basic info
    result['julian_day'] = jds
    result['body1_id'] = body1_id
    result['body2_id'] = body2_id

    # Determine if we should use cache
    use_ephemeris_cache = (
        use_cache and
        CACHE_AVAILABLE and
        hasattr(timestamps, 'to_pydatetime') or
        (isinstance(timestamps, (list, np.ndarray)) and len(timestamps) > 0)
    )

    if use_ephemeris_cache and not isinstance(timestamps[0] if len(timestamps) > 0 else None, float):
        # Use cache for datetime-based timestamps
        if cache is None:
            cache = get_default_cache()

        # Convert timestamps to datetime if needed
        if hasattr(timestamps, 'to_pydatetime'):
            dts = timestamps.to_pydatetime()
        else:
            dts = list(timestamps)

        # Batch lookup from cache (much faster than calc_planet_position_batch)
        pos1_lon = np.zeros(n, dtype=np.float32)
        pos1_vel = np.zeros(n, dtype=np.float32)
        pos2_lon = np.zeros(n, dtype=np.float32)
        pos2_vel = np.zeros(n, dtype=np.float32)

        for i, dt in enumerate(dts):
            # Get positions from cache (returns [lon, lat, dist, speed])
            p1 = cache.get_position(dt, body1_id)
            p2 = cache.get_position(dt, body2_id)
            pos1_lon[i] = p1[0]
            pos1_vel[i] = p1[3]
            pos2_lon[i] = p2[0]
            pos2_vel[i] = p2[3]

        result['body1_lon'] = pos1_lon
        result['body2_lon'] = pos2_lon
        result['body1_velocity'] = pos1_vel
        result['body2_velocity'] = pos2_vel
    else:
        # Fallback to direct calculation (for Julian dates or when cache unavailable)
        # calc_planet_position_batch returns shape (n, 6): [lon, lat, dist, lon_speed, lat_speed, dist_speed]
        pos1 = calc_planet_position_batch(jds, body1_id)
        pos2 = calc_planet_position_batch(jds, body2_id)

        # Extract longitudes (column 0) and velocities (column 3)
        result['body1_lon'] = pos1[:, 0]
        result['body2_lon'] = pos2[:, 0]
        result['body1_velocity'] = pos1[:, 3]
        result['body2_velocity'] = pos2[:, 3]

    result['relative_velocity'] = result['body2_velocity'] - result['body1_velocity']
    result['body1_retro'] = result['body1_velocity'] < 0
    result['body2_retro'] = result['body2_velocity'] < 0

    # Calculate separation (vectorized)
    result['angular_separation'] = _calculate_separation(
        result['body1_lon'],
        result['body2_lon']
    )

    # Cycle progress (0-1)
    result['cycle_progress'] = result['angular_separation'] / 360.0

    # Cycle phase: waxing (1) when 0-180°, waning (-1) when 180-360°
    result['cycle_phase'] = np.where(
        result['angular_separation'] <= 180, 1, -1
    ).astype(np.int8)

    # Aspect proximity
    if include_aspects:
        nearest, dist = _find_nearest_aspect(result['angular_separation'])
        result['nearest_aspect'] = nearest
        result['aspect_distance'] = dist

        # Check if in aspect (within orb)
        orb = _calculate_orb(body1_id, body2_id, 0)  # Base orb
        result['in_aspect'] = np.abs(dist) <= orb
        result['aspect_orb'] = np.where(result['in_aspect'], np.abs(dist), 0)

    return result


def generate_multi_cycle_series(
    planet_pairs: List[Tuple[Union[str, int], Union[str, int]]],
    timestamps: Union[np.ndarray, List[datetime], "pd.DatetimeIndex"],
    include_aspects: bool = True,
    use_cache: bool = True,
    cache: Optional["EphemerisCache"] = None,
) -> dict:
    """Generate cycle series for multiple planetary pairs.

    Args:
        planet_pairs: List of (body1, body2) tuples
        timestamps: Array of timestamps
        include_aspects: Calculate aspect proximity (default: True)
        use_cache: Use EphemerisCache for faster lookups (default: True)
        cache: Optional EphemerisCache instance (uses default if None)

    Returns:
        Dict mapping pair names to structured arrays

    Example:
        >>> pairs = [("Sun", "Moon"), ("Sun", "Mars"), ("Jupiter", "Saturn")]
        >>> timestamps = pd.date_range("2025-01-01", "2025-12-31", freq="1D")
        >>> cycles = generate_multi_cycle_series(pairs, timestamps)
        >>> sun_moon = cycles["Sun-Moon"]
    """
    result = {}

    # Get cache once for all pairs (efficiency)
    if use_cache and CACHE_AVAILABLE and cache is None:
        cache = get_default_cache()

    for body1, body2 in planet_pairs:
        # Create pair name
        if isinstance(body1, int):
            name1 = bodies["name"][body1].decode()
        else:
            name1 = body1

        if isinstance(body2, int):
            name2 = bodies["name"][body2].decode()
        else:
            name2 = body2

        pair_name = f"{name1}-{name2}"

        # Generate cycle series
        result[pair_name] = generate_cycle_series(
            body1, body2, timestamps, include_aspects,
            use_cache=use_cache, cache=cache
        )

    return result


# Default planet pairs for financial astrology
DEFAULT_PAIRS = [
    ("Sun", "Moon"),      # Lunation cycle (~29.5 days)
    ("Sun", "Mercury"),   # Mercury cycle (~116 days)
    ("Sun", "Venus"),     # Venus cycle (~584 days)
    ("Sun", "Mars"),      # Mars cycle (~780 days)
    ("Sun", "Jupiter"),   # Jupiter cycle (~399 days)
    ("Sun", "Saturn"),    # Saturn cycle (~378 days)
    ("Mars", "Jupiter"),  # Mars-Jupiter (~2.2 years)
    ("Mars", "Saturn"),   # Mars-Saturn (~2 years)
    ("Jupiter", "Saturn"), # Great conjunction (~20 years)
]


__all__ = [
    "generate_cycle_series",
    "generate_multi_cycle_series",
    "CycleState",
    "CYCLE_DTYPE",
    "MAJOR_ASPECTS",
    "DEFAULT_PAIRS",
]
