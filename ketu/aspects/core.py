"""Core algorithms for aspect and transit calculations (internal module).

This module contains shared algorithms used by both aspect_windows and transits modules.
It should not be imported directly by users.

Performance optimizations:
- LRU cache for position calculations
- Vectorized grid search
- Binary search refinement
"""

from functools import lru_cache
from typing import Union, Optional, Tuple, Callable
import numpy as np

from ketu.core import bodies, aspects
from ketu.calculations import body_id as _body_id_lookup, long, distance
from ketu.ephemeris.planets import calc_planet_position_batch


# ========== Input Validation ==========

def get_body_id(body: Union[str, int]) -> int:
    """Convert body name or ID to integer ID.

    Args:
        body: Body name (str) or ID (int)

    Returns:
        Body ID (0-12)
    """
    if isinstance(body, str):
        return _body_id_lookup(body)
    return body


def get_aspect_index(aspect: Union[str, int, float]) -> int:
    """Get aspect index from name, index, or angle.

    Args:
        aspect: Aspect name, index, or angle

    Returns:
        Aspect index (0-6)
    """
    if isinstance(aspect, str):
        idx = np.where(aspects["name"] == aspect.encode())[0]
        if len(idx) == 0:
            raise ValueError(f"Unknown aspect name: {aspect}")
        return int(idx[0])
    elif isinstance(aspect, int) and aspect < 7:
        return aspect
    else:
        idx = np.where(aspects["angle"] == aspect)[0]
        if len(idx) == 0:
            raise ValueError(f"Unknown aspect angle: {aspect}")
        return int(idx[0])


# ========== Position Calculation with Cache ==========

@lru_cache(maxsize=256)
def _cached_planet_position_batch(jd_tuple: tuple, planet_id: int) -> np.ndarray:
    """Cached version of calc_planet_position_batch.

    Note: jd_tuple must be a tuple (immutable) for caching to work.
    """
    jd_array = np.array(jd_tuple)
    return calc_planet_position_batch(jd_array, planet_id)


def get_cached_positions(jd_array: np.ndarray, planet_id: int) -> np.ndarray:
    """Get planet positions with caching.

    Caches results for repeated calculations on same time grid.

    Args:
        jd_array: Array of Julian Dates
        planet_id: Planet ID

    Returns:
        2D array of positions (n_dates, 6)
    """
    # Convert to tuple for caching (numpy arrays are not hashable)
    jd_tuple = tuple(jd_array.tolist())
    return _cached_planet_position_batch(jd_tuple, planet_id)


# ========== Core Algorithm: Binary Search Refinement ==========

def refine_exact_moment(
    distance_callback: Callable[[float], float],
    jd_initial: float,
    max_iterations: int = 50,
    tolerance: float = 1e-7,
) -> Optional[float]:
    """Refine exact moment using binary search (bisection method).

    Generic function that works for both aspects and transits.
    Uses a callback to calculate the distance/error at any given time.

    Args:
        distance_callback: Function that takes JD and returns distance error
        jd_initial: Initial guess for exact moment
        max_iterations: Maximum iterations
        tolerance: Convergence tolerance in days (~1 second = 1e-7 days)

    Returns:
        Refined Julian Date of exact moment

    Example:
        >>> # For aspect between two bodies:
        >>> def callback(jd):
        ...     pos1 = long(jd, body1_id)
        ...     pos2 = long(jd, body2_id)
        ...     return distance(pos1, pos2) - aspect_angle
        >>> exact_jd = refine_exact_moment(callback, initial_jd)
    """
    error_initial = distance_callback(jd_initial)

    if abs(error_initial) < 0.001:
        return jd_initial

    # Search window
    search_window = 0.5
    jd_left = jd_initial - search_window
    jd_right = jd_initial + search_window

    best_jd = jd_initial
    best_error = abs(error_initial)

    for _ in range(max_iterations):
        jd_mid = (jd_left + jd_right) / 2
        error_mid = distance_callback(jd_mid)

        if abs(error_mid) < best_error:
            best_error = abs(error_mid)
            best_jd = jd_mid

        if abs(error_mid) < 0.001:
            return jd_mid

        if abs(jd_right - jd_left) < tolerance:
            return best_jd

        # Binary search
        error_left_mid = distance_callback((jd_left + jd_mid) / 2)
        error_mid_right = distance_callback((jd_mid + jd_right) / 2)

        if abs(error_left_mid) < abs(error_mid_right):
            jd_right = jd_mid
        else:
            jd_left = jd_mid

    return best_jd


# ========== Core Algorithm: Orb Boundary Search ==========

def find_orb_boundaries(
    is_within_orb_callback: Callable[[float], bool],
    jd_exact: float,
    search_days: float = 30,
) -> Tuple[Optional[float], Optional[float]]:
    """Find orb entry and exit times using binary search.

    Generic function that works for both aspects and transits.
    Uses a callback to check if within orb at any given time.

    Args:
        is_within_orb_callback: Function that takes JD and returns bool
        jd_exact: Julian Date of exact moment
        search_days: Maximum days to search in each direction

    Returns:
        Tuple of (jd_begin, jd_end)

    Example:
        >>> # For aspect with specific orb:
        >>> def callback(jd):
        ...     pos1 = long(jd, body1_id)
        ...     pos2 = long(jd, body2_id)
        ...     dist = distance(pos1, pos2)
        ...     return abs(dist - aspect_angle) <= orb
        >>> jd_begin, jd_end = find_orb_boundaries(callback, exact_jd)
    """
    # Binary search for beginning
    jd_begin = None
    left = jd_exact - search_days
    right = jd_exact

    for _ in range(20):  # ~1 minute precision
        mid = (left + right) / 2

        if is_within_orb_callback(mid):
            jd_begin = mid
            right = mid
        else:
            left = mid

        if abs(right - left) < 1e-5:
            break

    # Binary search for end
    jd_end = None
    left = jd_exact
    right = jd_exact + search_days

    for _ in range(20):
        mid = (left + right) / 2

        if is_within_orb_callback(mid):
            jd_end = mid
            left = mid
        else:
            right = mid

        if abs(right - left) < 1e-5:
            break

    return jd_begin, jd_end


# ========== Core Algorithm: Local Minima Detection ==========

def find_local_minima(error_array: np.ndarray, threshold: float) -> np.ndarray:
    """Find indices of local minima in error array.

    A local minimum at index i means: error[i-1] > error[i] < error[i+1]

    Args:
        error_array: Array of errors/distances
        threshold: Only return minima below this threshold

    Returns:
        Array of indices where local minima occur
    """
    n = len(error_array)
    if n < 3:
        return np.array([], dtype=int)

    # Find where error[i] < error[i-1] and error[i] < error[i+1]
    is_local_min = np.zeros(n, dtype=bool)

    for i in range(1, n - 1):
        if (error_array[i] < error_array[i - 1] and
            error_array[i] < error_array[i + 1] and
            error_array[i] <= threshold):
            is_local_min[i] = True

    return np.where(is_local_min)[0]


def interpolate_minimum(
    error_before: float,
    error_current: float,
    error_after: float,
    idx: int,
    step_size: float,
) -> Tuple[float, float]:
    """Interpolate exact position of minimum using quadratic fit.

    Fits a parabola through 3 points to find the minimum.

    Args:
        error_before: Error at idx-1
        error_current: Error at idx
        error_after: Error at idx+1
        idx: Current index
        step_size: Step size in the grid

    Returns:
        Tuple of (offset_from_idx, interpolated_error)
    """
    # Quadratic interpolation formula
    denominator = 2 * (error_before - 2 * error_current + error_after)

    if abs(denominator) > 1e-10:
        offset = (error_before - error_after) / denominator
        offset = np.clip(offset, -0.5, 0.5)  # Keep it local
    else:
        offset = 0.0

    return offset, error_current


# ========== Adaptive Grid Parameters ==========

def calculate_adaptive_step(
    body_speeds: list,
    orb: float,
    min_step: float = 0.01,
    max_step: float = 1.0,
    points_per_orb: int = 10,
) -> float:
    """Calculate adaptive step size based on body speeds.

    Faster bodies need finer sampling to avoid missing crossings.

    Args:
        body_speeds: List of body speeds (degrees/day)
        orb: Orb tolerance (degrees)
        min_step: Minimum step size (days)
        max_step: Maximum step size (days)
        points_per_orb: Desired number of sample points per orb width

    Returns:
        Optimal step size (days)
    """
    # Calculate relative speed
    if len(body_speeds) == 1:
        relative_speed = abs(body_speeds[0])
    else:
        relative_speed = abs(body_speeds[0] - body_speeds[1])

    if relative_speed < 0.001:
        relative_speed = 0.001  # Minimum to avoid division by zero

    # Calculate step: we want ~points_per_orb samples across the orb width
    days_per_orb = orb / relative_speed
    step_days = days_per_orb / points_per_orb

    # Clamp to reasonable range
    step_days = min(step_days, max_step)
    step_days = max(step_days, min_step)

    return step_days


# ========== Utility Functions ==========

def detect_retrograde_motion(velocity: float) -> str:
    """Detect if motion is direct or retrograde.

    Args:
        velocity: Longitude velocity (degrees/day)

    Returns:
        "retrograde" or "direct"
    """
    return "retrograde" if velocity < 0 else "direct"


def estimate_duration_hours(jd_begin: float, jd_end: float) -> float:
    """Estimate duration in hours between two Julian Dates.

    Args:
        jd_begin: Start Julian Date
        jd_end: End Julian Date

    Returns:
        Duration in hours
    """
    return (jd_end - jd_begin) * 24.0


__all__ = [
    "get_body_id",
    "get_aspect_index",
    "get_cached_positions",
    "refine_exact_moment",
    "find_orb_boundaries",
    "find_local_minima",
    "interpolate_minimum",
    "calculate_adaptive_step",
    "detect_retrograde_motion",
    "estimate_duration_hours",
]
