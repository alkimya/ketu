"""
Cycle state calculator for planetary pairs.

Calculates the instantaneous state of planetary cycles at given timestamps,
optimized for vectorized operations on large timestamp arrays.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Union, List, Optional, Tuple
import numpy as np

from ketu.core import bodies
from ketu.calculations import long, long_velocity, utc_to_julian, distance
from ketu.ephemeris.planets import calc_planet_position_batch
from ketu.complex import (
    degrees_to_complex,
    cycle_ratio_vectorized,
    complex_to_degrees
)

# Optional cache import
try:
    from ketu.cache import EphemerisCache, get_default_cache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    EphemerisCache = None
    get_default_cache = None


# Major aspects for proximity calculation (including waning phases)
MAJOR_ASPECTS = np.array([0, 60, 90, 120, 180, 240, 270, 300, 360], dtype=np.float32)
# Complex representation of major aspects
MAJOR_ASPECTS_Z = degrees_to_complex(MAJOR_ASPECTS)

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
    """
    Instantaneous state of a planetary cycle.

    Attributes
    ----------
    julian_day : float
        Julian date of calculation.
    body1_id : int
        First body ID.
    body2_id : int
        Second body ID.
    body1_lon : float
        Longitude of body 1 (0-360°).
    body2_lon : float
        Longitude of body 2 (0-360°).
    angular_separation : float
        Angular distance (0-360°, in direction of cycle).
    cycle_progress : float
        Normalized progress through cycle (0.0-1.0).
    cycle_phase : int
        1 for waxing (0→180°), -1 for waning (180→360°).
    body1_velocity : float
        Velocity of body 1 (deg/day).
    body2_velocity : float
        Velocity of body 2 (deg/day).
    relative_velocity : float
        Relative velocity (deg/day).
    body1_retro : bool
        Is body 1 retrograde.
    body2_retro : bool
        Is body 2 retrograde.
    nearest_aspect : float
        Nearest major aspect angle.
    aspect_distance : float
        Signed distance to nearest aspect.
    in_aspect : bool
        Whether currently within orb of an aspect.
    aspect_orb : float
        Current orb value if in aspect.
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
    """
    Convert body name or ID to ID."""
    if isinstance(body, int):
        return body
    body_idx = np.where(bodies["name"] == body.encode())[0]
    if len(body_idx) == 0:
        valid_bodies = ', '.join(bodies['name'].astype(str))
        raise ValueError(f"Unknown body: '{body}'. Valid bodies: {valid_bodies}")
    return int(bodies["id"][body_idx[0]])


def generate_cycle_series(
    body1: Union[str, int],
    body2: Union[str, int],
    timestamps: Union[np.ndarray, List[datetime]],
    include_aspects: bool = True,
    use_cache: bool = True,
    cache: Optional["EphemerisCache"] = None,
) -> np.ndarray:
    """
    Generate cycle state series for a planetary pair.

    Calculates the instantaneous state of the cycle between two bodies
    at each provided timestamp. Optimized for vectorized operations.

    Parameters
    ----------
    body1 : str or int
        First body (name or ID) - typically the faster body.
    body2 : str or int
        Second body (name or ID) - typically the slower body.
    timestamps : numpy.ndarray or list of datetime
        Array of timestamps (datetime or Julian dates).
    include_aspects : bool, optional
        Calculate aspect proximity info (default: True).
    use_cache : bool, optional
        Use EphemerisCache for faster lookups (default: True).
    cache : EphemerisCache, optional
        Optional EphemerisCache instance (uses default if None).

    Returns
    -------
    numpy.ndarray
        Structured numpy array with CYCLE_DTYPE.

    Examples
    --------
    >>> from datetime import datetime, timedelta
    >>> from ketu.cycles import generate_cycle_series
    >>> timestamps = [datetime(2025, 1, 1) + timedelta(days=i) for i in range(365)]
    >>> cycles = generate_cycle_series("Sun", "Mars", timestamps)
    >>> cycles.shape
    (365,)
    >>> cycles.dtype.names[:3]
    ('julian_day', 'body1_id', 'body2_id')
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
            raise ValueError(f"Unsupported timestamp dtype: {timestamps.dtype}. Expected datetime64 ('M') or float ('f')")
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
        (hasattr(timestamps, 'to_pydatetime') or
         (isinstance(timestamps, (list, np.ndarray)) and len(timestamps) > 0))
    )

    if use_ephemeris_cache and not isinstance(timestamps[0] if len(timestamps) > 0 else None, float):
        # Use cache for datetime-based timestamps
        if cache is None:
            cache = get_default_cache()

        # Convert timestamps to datetime if needed. The cache's vectorized
        # lookup reads .year/.month/... attributes, which numpy.datetime64
        # does not expose — so a datetime64 ndarray must be converted to
        # python datetime here (matching the jds path above), not passed raw.
        if hasattr(timestamps, 'to_pydatetime'):
            dts = list(timestamps.to_pydatetime())
        elif isinstance(timestamps, np.ndarray) and timestamps.dtype.kind == 'M':
            dts = list(timestamps.astype('datetime64[us]').astype(datetime))
        else:
            dts = list(timestamps)

        # Vectorized batch lookup from cache (10x faster than loop)
        pos1_lon, pos1_vel = cache.get_positions_vectorized(dts, body1_id)
        pos2_lon, pos2_vel = cache.get_positions_vectorized(dts, body2_id)

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

    # --- VECTORIZED COMPLEX NUMBER CALCULATION ---
    
    # 1. Calculate Cycle Ratio using Complex Numbers
    # z_ratio = z_slower / z_faster = e^(i(θ₂ - θ₁))
    z_ratios = cycle_ratio_vectorized(result['body1_lon'], result['body2_lon'])
    
    # 2. Extract angular separation (0-360) and Cycle Progress
    separation = complex_to_degrees(z_ratios)
    result['angular_separation'] = separation
    result['cycle_progress'] = separation / 360.0
    
    # 3. Cycle Phases
    # Waxing: 0 -> 180, Waning: 180 -> 360
    result['cycle_phase'] = np.where(separation < 180, 1, -1).astype(np.int8)
    
    # 4. Aspect Proximity (Vectorized Complex)
    if include_aspects:
        # Calculate angular distance to each aspect in radians
        # angle(z_ratio / z_aspect) gives signed distance in (-π, π]
        # MAJOR_ASPECTS_Z is broadcasted
        dist_matrix_rad = np.angle(z_ratios[:, np.newaxis] / MAJOR_ASPECTS_Z[np.newaxis, :])
        dist_matrix_deg = np.rad2deg(dist_matrix_rad)
        
        # Find index of aspect with minimum absolute distance
        nearest_indices = np.argmin(np.abs(dist_matrix_deg), axis=1)
        
        # Select the values
        nearest_aspects = MAJOR_ASPECTS[nearest_indices]
        result['nearest_aspect'] = np.where(nearest_aspects == 360, 0, nearest_aspects)
        
        # Signed distances corresponding to nearest aspects
        # Flattening index approach for performance
        n_samples = len(z_ratios)
        flat_indices = nearest_indices + np.arange(n_samples) * len(MAJOR_ASPECTS)
        result['aspect_distance'] = dist_matrix_deg.ravel()[flat_indices]
        
        # 5. Calculate Orbs Vectorized
        orb1 = float(bodies["orb"][body1_id])
        orb2 = float(bodies["orb"][body2_id])
        avg_orb = (orb1 + orb2) / 2
        
        # Coefficients based on MAJOR_ASPECTS indices
        # [0, 60, 90, 120, 180, 240, 270, 300, 360]
        #  C   S   Sq  As   Op   Wn   Wn   S    C
        #  1  .5  .75 .75   1   .75  .75  .5    1
        COEFFS = np.array([1.0, 0.5, 0.75, 0.75, 1.0, 0.75, 0.75, 0.5, 1.0], dtype=np.float32)
        orb_coeffs = COEFFS[nearest_indices]
        
        current_orbs = avg_orb * orb_coeffs
        
        # Check in_aspect
        in_aspect = np.abs(result['aspect_distance']) <= current_orbs
        result['in_aspect'] = in_aspect
        result['aspect_orb'] = np.where(in_aspect, current_orbs, 0.0)

    return result


def generate_multi_cycle_series(
    planet_pairs: List[Tuple[Union[str, int], Union[str, int]]],
    timestamps: Union[np.ndarray, List[datetime]],
    include_aspects: bool = True,
    use_cache: bool = True,
    cache: Optional["EphemerisCache"] = None,
) -> dict:
    """
    Generate cycle series for multiple planetary pairs.

    Parameters
    ----------
    planet_pairs : list of tuple
        List of (body1, body2) tuples.
    timestamps : numpy.ndarray or list of datetime
        Array of timestamps.
    include_aspects : bool, optional
        Calculate aspect proximity (default: True).
    use_cache : bool, optional
        Use EphemerisCache for faster lookups (default: True).
    cache : EphemerisCache, optional
        Optional EphemerisCache instance (uses default if None).

    Returns
    -------
    dict of {str: numpy.ndarray}
        Dict mapping pair names to structured arrays.

    Examples
    --------
    >>> from datetime import datetime, timedelta
    >>> pairs = [("Sun", "Moon"), ("Sun", "Mars"), ("Jupiter", "Saturn")]
    >>> timestamps = [datetime(2025, 1, 1) + timedelta(days=i) for i in range(365)]
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


# Default planet pairs for cycle analysis
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
