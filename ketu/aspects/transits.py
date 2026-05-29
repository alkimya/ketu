"""
Transit calculations - planetary movements relative to fixed reference positions.

This module provides APIs for calculating transits, which occur when moving planets
form aspects with fixed reference positions (e.g., natal chart positions).

A transit is different from an aspect:
- Aspect: Two moving bodies forming an angle
- Transit: One moving body forming an angle with a fixed position

Example:
    >>> from ketu.aspects.transits import find_transits_to_position
    >>> transits = find_transits_to_position(
    ...     transiting_body="Mars",
    ...     reference_longitude=120.0,
    ...     aspects_list=["Conjunction", "Trine", "Opposition"],
    ...     start_date="2024-01-01",
    ...     end_date="2024-12-31"
    ... )
    >>> isinstance(transits, list)
    True
"""

from collections import namedtuple
from datetime import datetime
from typing import Union, List, Optional, Dict, Tuple
import numpy as np

from ketu.core import bodies, aspects
from ketu.calculations import (
    distance,
    body_id,
    long,
    long_velocity,
    utc_to_julian,
    julian_to_utc,
    positions,
)
from ketu.aspects.calculator import get_orb
from ketu.ephemeris.planets import calc_planet_position_batch

# Import shared algorithms from refactored core module
from ketu.aspects.core import (
    get_body_id as _get_body_id,
    get_aspect_index as _get_aspect_index,
    get_cached_positions,
    refine_exact_moment,
    find_orb_boundaries,
    find_local_minima,
    interpolate_minimum,
    calculate_adaptive_step,
)

# Default aspect set sourced from presets module (Phase 9, ASP-04).
# Replaces previously-hardcoded ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]
# lists. Single source of truth: when CLASSICAL changes, all call sites in this
# module pick up the change automatically.
from ketu.aspects.presets import CLASSICAL as _CLASSICAL_MASK
_CLASSICAL_NAMES = tuple(
    aspects["name"][i].decode()
    for i in np.where(_CLASSICAL_MASK)[0]
)


# ========== Data Structures ==========

TransitMoment = namedtuple(
    "TransitMoment",
    ["begin", "exact", "end", "orb_used", "motion"],
    defaults=[None, None, None, None, "direct"],
)
"""
Named tuple representing a single transit moment.

Attributes:
    begin (datetime): Entry into orb (transit begins)
    exact (datetime): Exact transit moment
    end (datetime): Exit from orb (transit ends)
    orb_used (float): Orb tolerance used (degrees)
    motion (str): 'direct' or 'retrograde'
"""


TransitWindow = namedtuple(
    "TransitWindow",
    ["transiting_body", "reference_longitude", "aspect", "moments", "retrograde_count"],
    defaults=[None, None, None, [], 0],
)
"""
Named tuple representing complete transit window information.

Attributes:
    transiting_body (str): Name of transiting body
    reference_longitude (float): Fixed reference position (degrees)
    aspect (str): Aspect name
    moments (List[TransitMoment]): List of transit moments (1-3 for retrograde)
    retrograde_count (int): Number of retrograde events during transit
"""


NatalPosition = namedtuple(
    "NatalPosition",
    ["body", "longitude", "latitude", "distance"],
)
"""
Named tuple for natal/reference planetary position.

Attributes:
    body (str): Body name
    longitude (float): Ecliptic longitude (degrees)
    latitude (float): Ecliptic latitude (degrees)
    distance (float): Distance from Earth (AU)
"""


TransitAspect = namedtuple(
    "TransitAspect",
    ["transiting_body", "natal_body", "aspect", "exact_time", "orb_used"],
)
"""
Named tuple for a transit aspect between two positions.

Attributes:
    transiting_body (str): Name of transiting body
    natal_body (str): Name of natal/reference body
    aspect (str): Aspect name
    exact_time (datetime): Exact aspect moment
    orb_used (float): Orb tolerance used (degrees)
"""


# ========== Helper Functions ==========
# Note: _get_body_id and _get_aspect_index are now imported from _aspect_core

def _find_transit_crossings(
    body_id: int,
    reference_lon: float,
    aspect_angle: float,
    orb: float,
    jd_start: float,
    jd_end: float,
) -> List[Tuple[float, float, str]]:
    """
    Find all transit crossing candidates using vectorized search

    Similar to _adaptive_grid_search but for transits (one moving body vs fixed position).

    Parameters
    ----------
    body_id : int
        Transiting body ID.
    reference_lon : float
        Reference longitude (degrees).
    aspect_angle : float
        Target aspect angle (degrees).
    orb : float
        Orb tolerance (degrees).
    jd_start : float
        Start Julian Date.
    jd_end : float
        End Julian Date.

    Returns
    -------
    list of tuple
        List of (jd_crossing, error, motion) tuples.
    """
    # Calculate adaptive step size using refactored function
    avg_speed = bodies["speed"][body_id]
    step_days = calculate_adaptive_step([avg_speed], orb)

    # Create time grid
    n_steps = int((jd_end - jd_start) / step_days) + 1
    jd_grid = np.linspace(jd_start, jd_end, n_steps)

    # Vectorized position calculation with caching
    pos_data = get_cached_positions(jd_grid, body_id)

    # Extract longitudes and velocities
    lon = pos_data[:, 0]
    vlon = pos_data[:, 3]

    # Calculate angular distances from reference (vectorized)
    dists = distance(lon, reference_lon)  # type: ignore[arg-type]

    # Calculate absolute error from target aspect angle
    aspect_error = np.abs(dists - aspect_angle)

    # Find local minima using refactored function
    minima_indices = find_local_minima(aspect_error, orb)

    candidates = []

    # Process each local minimum
    for idx in minima_indices:
        error_before = aspect_error[idx - 1]
        error_current = aspect_error[idx]
        error_after = aspect_error[idx + 1]

        # Use quadratic interpolation from refactored function
        offset, _ = interpolate_minimum(error_before, error_current, error_after, idx, step_days)
        jd_approx = jd_grid[idx] + offset * step_days

        # Determine motion (retrograde or direct)
        is_retro = vlon[idx] < 0
        motion_type = "retrograde" if is_retro else "direct"

        candidates.append((jd_approx, error_current, motion_type))

    return candidates


def _make_transit_distance_callback(body_id: int, reference_lon: float, aspect_angle: float):
    """
    Create callback for transit distance calculation (for refinement)

    Parameters
    ----------
    body_id : int
        Transiting body ID.
    reference_lon : float
        Reference longitude.
    aspect_angle : float
        Target aspect angle.

    Returns
    -------
    callable
        Callback function that takes JD and returns distance error.
    """
    def callback(jd: float) -> float:
        pos = long(jd, body_id)
        dist = distance(pos, reference_lon)
        return dist - aspect_angle
    return callback


def _make_transit_orb_callback(body_id: int, reference_lon: float, aspect_angle: float, orb: float):
    """
    Create callback to check if within orb (for boundary finding)

    Parameters
    ----------
    body_id : int
        Transiting body ID.
    reference_lon : float
        Reference longitude.
    aspect_angle : float
        Target aspect angle.
    orb : float
        Orb tolerance.

    Returns
    -------
    callable
        Callback function that takes JD and returns bool (within orb?).
    """
    def callback(jd: float) -> bool:
        pos = long(jd, body_id)
        dist = distance(pos, reference_lon)
        error = abs(dist - aspect_angle) if aspect_angle > 0 else dist
        return error <= orb
    return callback


# ========== Public API ==========

def find_transits_to_position(
    transiting_body: Union[str, int],
    reference_longitude: float,
    aspects_list: Optional[List[Union[str, int]]] = None,
    start_date: Optional[Union[datetime, str, float]] = None,
    end_date: Optional[Union[datetime, str, float]] = None,
    custom_orb: Optional[float] = None,
    detect_retrograde: bool = True,
) -> List[TransitWindow]:
    """
    Find transits of a moving body to a fixed longitude.

    This function finds when a transiting planet forms aspects with a fixed
    reference position (e.g., natal planet position).

    Parameters
    ----------
    transiting_body : str or int
        Moving body (name or ID).
    reference_longitude : float
        Fixed reference position (0-360 degrees).
    aspects_list : list of (str or int), optional
        List of aspects to find (default: major aspects).
    start_date : datetime, str, or float, optional
        Start date (datetime, ISO string, or Julian Date).
    end_date : datetime, str, or float, optional
        End date (datetime, ISO string, or Julian Date).
    custom_orb : float, optional
        Custom orb in degrees (default: use calculated orb).
    detect_retrograde : bool, optional
        Enable multi-pass retrograde detection.

    Returns
    -------
    list of TransitWindow
        List of TransitWindow objects sorted by exact time.

    Examples
    --------
    When does Mars transit 120° (0° Leo)?

    >>> transits = find_transits_to_position(
    ...     transiting_body="Mars",
    ...     reference_longitude=120.0,
    ...     aspects_list=["Conjunction", "Square", "Trine", "Opposition"],
    ...     start_date="2024-01-01",
    ...     end_date="2024-12-31"
    ... )
    """
    # Convert inputs
    body_id_val = _get_body_id(transiting_body)
    body_name = bodies["name"][body_id_val].decode()

    # Normalize longitude to 0-360
    reference_longitude = reference_longitude % 360

    # Default aspects: CLASSICAL preset (Phase 9 ASP-04)
    if aspects_list is None:
        aspects_list = list(_CLASSICAL_NAMES)

    # Convert dates
    if isinstance(start_date, str):
        start_dt = datetime.fromisoformat(start_date)
        jd_start = utc_to_julian(start_dt)
    elif isinstance(start_date, datetime):
        jd_start = utc_to_julian(start_date)
    else:
        jd_start = float(start_date)

    if isinstance(end_date, str):
        end_dt = datetime.fromisoformat(end_date)
        jd_end = utc_to_julian(end_dt)
    elif isinstance(end_date, datetime):
        jd_end = utc_to_julian(end_date)
    else:
        jd_end = float(end_date)

    all_windows = []

    # Find each aspect
    for aspect in aspects_list:
        aspect_idx = _get_aspect_index(aspect)
        aspect_name = aspects["name"][aspect_idx].decode()
        aspect_angle = float(aspects["angle"][aspect_idx])

        # Calculate orb (use Sun's orb as reference for the fixed position)
        if custom_orb is not None:
            orb = custom_orb
        else:
            # Orb between transiting body and Sun (as proxy for natal position)
            orb = get_orb(body_id_val, 0, aspect_idx)

        # Find transit crossings
        candidates = _find_transit_crossings(
            body_id_val, reference_longitude, aspect_angle, orb, jd_start, jd_end
        )

        if not candidates:
            continue

        # Refine each candidate using generic algorithms from _aspect_core
        refined_moments = []

        for jd_approx, _, motion in candidates:
            # Refine exact moment using generic refinement with callback
            distance_callback = _make_transit_distance_callback(
                body_id_val, reference_longitude, aspect_angle
            )
            jd_exact = refine_exact_moment(distance_callback, jd_approx)

            if jd_exact is None:
                continue

            # Find orb boundaries using generic boundary finding with callback
            orb_callback = _make_transit_orb_callback(
                body_id_val, reference_longitude, aspect_angle, orb
            )
            jd_begin, jd_end_orb = find_orb_boundaries(orb_callback, jd_exact, 30)

            if jd_begin is None or jd_end_orb is None:
                continue

            # Convert to datetime
            dt_begin = julian_to_utc(jd_begin)
            dt_exact = julian_to_utc(jd_exact)
            dt_end = julian_to_utc(jd_end_orb)

            # Check retrograde
            vel = long_velocity(jd_exact, body_id_val)
            is_retro = vel < 0
            motion_type = "retrograde" if is_retro else "direct"

            refined_moments.append(
                TransitMoment(
                    begin=dt_begin,
                    exact=dt_exact,
                    end=dt_end,
                    orb_used=orb,
                    motion=motion_type,
                )
            )

        if refined_moments:
            # Sort by exact time
            refined_moments.sort(key=lambda m: m.exact)

            # Count retrogrades
            retrograde_count = sum(1 for m in refined_moments if m.motion == "retrograde")

            # Limit to single moment if retrograde detection disabled
            if not detect_retrograde and len(refined_moments) > 1:
                jd_center = (jd_start + jd_end) / 2
                refined_moments = sorted(
                    refined_moments,
                    key=lambda m: abs(utc_to_julian(m.exact) - jd_center)
                )[:1]
                retrograde_count = 0

            all_windows.append(
                TransitWindow(
                    transiting_body=body_name,
                    reference_longitude=reference_longitude,
                    aspect=aspect_name,
                    moments=refined_moments,
                    retrograde_count=retrograde_count,
                )
            )

    # Sort all windows chronologically
    all_windows.sort(key=lambda w: w.moments[0].exact if w.moments else datetime.max)

    return all_windows


def get_natal_positions(
    reference_date: Union[datetime, str, float],
    bodies_list: Optional[List[Union[str, int]]] = None,
) -> Dict[str, NatalPosition]:
    """
    Get planetary positions at a reference date (e.g., natal chart).

    Parameters
    ----------
    reference_date : datetime, str, or float
        Reference date (datetime, ISO string, or Julian Date).
    bodies_list : list of (str or int), optional
        List of bodies (default: all planets).

    Returns
    -------
    dict of {str: NatalPosition}
        Dictionary mapping body names to NatalPosition objects.

    Examples
    --------
    >>> natal = get_natal_positions("1990-05-15 14:30")
    >>> "Sun" in natal
    True
    >>> bool(0.0 <= natal["Sun"].longitude < 360.0)
    True
    """
    # Convert date
    if isinstance(reference_date, str):
        dt = datetime.fromisoformat(reference_date)
        jd = utc_to_julian(dt)
    elif isinstance(reference_date, datetime):
        jd = utc_to_julian(reference_date)
    else:
        jd = float(reference_date)

    # Default to all bodies
    if bodies_list is None:
        bodies_list = list(range(13))  # 0-12

    natal_positions = {}

    for body in bodies_list:
        body_id_val = _get_body_id(body)
        body_name = bodies["name"][body_id_val].decode()

        from ketu.calculations import body_properties
        props = body_properties(jd, body_id_val)

        natal_positions[body_name] = NatalPosition(
            body=body_name,
            longitude=props[0],
            latitude=props[1],
            distance=props[2],
        )

    return natal_positions


def compare_dates_transits(
    natal_date: Union[datetime, str, float],
    transit_date: Union[datetime, str, float],
    aspects_list: Optional[List[Union[str, int]]] = None,
    custom_orb: Optional[float] = None,
) -> List[TransitAspect]:
    """
    Compare two dates and find all transiting aspects.

    This function compares all planetary positions at two different dates
    and finds which transiting planets are forming aspects with natal positions.

    Parameters
    ----------
    natal_date : datetime, str, or float
        Natal/reference date.
    transit_date : datetime, str, or float
        Transit/current date.
    aspects_list : list of (str or int), optional
        List of aspects to check (default: major aspects).
    custom_orb : float, optional
        Custom orb in degrees.

    Returns
    -------
    list of TransitAspect
        List of TransitAspect objects.

    Examples
    --------
    Compare birth chart with current transits:

    >>> transits = compare_dates_transits(
    ...     natal_date="1990-05-15 14:30",
    ...     transit_date="2024-11-21"
    ... )
    >>> isinstance(transits, list)
    True
    """
    # Get natal positions
    natal_positions = get_natal_positions(natal_date)

    # Get transit positions
    transit_positions = get_natal_positions(transit_date)

    # Default aspects: CLASSICAL preset (Phase 9 ASP-04)
    if aspects_list is None:
        aspects_list = list(_CLASSICAL_NAMES)

    # Convert transit date
    if isinstance(transit_date, str):
        dt = datetime.fromisoformat(transit_date)
        transit_dt = dt
    elif isinstance(transit_date, datetime):
        transit_dt = transit_date
    else:
        transit_dt = julian_to_utc(float(transit_date))

    transit_aspects = []

    # Check each transiting body against each natal body
    for trans_name, trans_pos in transit_positions.items():
        trans_body_id = _get_body_id(trans_name)

        for natal_name, natal_pos in natal_positions.items():
            # Skip same body
            if trans_name == natal_name:
                continue

            natal_body_id = _get_body_id(natal_name)

            # Calculate distance
            dist = distance(trans_pos.longitude, natal_pos.longitude)

            # Check each aspect
            for aspect in aspects_list:
                aspect_idx = _get_aspect_index(aspect)
                aspect_name = aspects["name"][aspect_idx].decode()
                aspect_angle = float(aspects["angle"][aspect_idx])

                # Calculate orb
                if custom_orb is not None:
                    orb = custom_orb
                else:
                    orb = get_orb(trans_body_id, natal_body_id, aspect_idx)

                # Check if within orb
                if aspect_angle == 0:
                    # Conjunction
                    if dist <= orb:
                        transit_aspects.append(
                            TransitAspect(
                                transiting_body=trans_name,
                                natal_body=natal_name,
                                aspect=aspect_name,
                                exact_time=transit_dt,
                                orb_used=orb,
                            )
                        )
                else:
                    # Other aspects
                    if abs(dist - aspect_angle) <= orb:
                        transit_aspects.append(
                            TransitAspect(
                                transiting_body=trans_name,
                                natal_body=natal_name,
                                aspect=aspect_name,
                                exact_time=transit_dt,
                                orb_used=orb,
                            )
                        )

    return transit_aspects


__all__ = [
    "TransitMoment",
    "TransitWindow",
    "NatalPosition",
    "TransitAspect",
    "find_transits_to_position",
    "get_natal_positions",
    "compare_dates_transits",
]
