"""
Core algorithms for aspect and transit calculations (internal module).

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
    """
    Convert body name or ID to integer ID.

    Parameters
    ----------
    body : str or int
        Body name (str) or ID (int).

    Returns
    -------
    int
        Body ID (0-12).
    """
    if isinstance(body, str):
        return _body_id_lookup(body)
    return body


def get_aspect_index(aspect: Union[str, int, float]) -> int:
    """
    Get aspect index from name, index, or angle.

    Parameters
    ----------
    aspect : str, int, or float
        Aspect name, index, or angle.

    Returns
    -------
    int
        Aspect index (0-13) - now includes harmonics 9 and 10.
    """
    if isinstance(aspect, str):
        idx = np.where(aspects["name"] == aspect.encode())[0]
        if len(idx) == 0:
            valid_aspects = ', '.join(a.decode() for a in aspects['name'])
            raise ValueError(f"unknown aspect name: '{aspect}'. Valid aspects: {valid_aspects}")
        return int(idx[0])
    elif isinstance(aspect, int) and aspect < len(aspects):
        return aspect
    else:
        idx = np.where(aspects["angle"] == aspect)[0]
        if len(idx) == 0:
            valid_angles = ', '.join(str(a) for a in aspects['angle'])
            raise ValueError(f"unknown aspect angle: {aspect}. Valid angles: {valid_angles}")
        return int(idx[0])


# ========== Position Calculation with Cache ==========

@lru_cache(maxsize=256)
def _cached_planet_position_batch(jd_tuple: tuple, planet_id: int) -> np.ndarray:
    """
    Cached version of calc_planet_position_batch.

    Note: jd_tuple must be a tuple (immutable) for caching to work.
    """
    jd_array = np.array(jd_tuple)
    return calc_planet_position_batch(jd_array, planet_id)


def get_cached_positions(jd_array: np.ndarray, planet_id: int) -> np.ndarray:
    """
    Get planet positions with caching.

    Caches results for repeated calculations on same time grid.

    Parameters
    ----------
    jd_array : np.ndarray
        Array of Julian Dates.
    planet_id : int
        Planet ID.

    Returns
    -------
    np.ndarray
        2D array of positions (n_dates, 6).
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
    """
    Refine exact moment using binary search (bisection method).

    Generic function that works for both aspects and transits.
    Uses a callback to calculate the distance/error at any given time.

    Parameters
    ----------
    distance_callback : callable
        Function that takes JD and returns distance error.
    jd_initial : float
        Initial guess for exact moment.
    max_iterations : int, optional
        Maximum iterations.
    tolerance : float, optional
        Convergence tolerance in days (~1 second = 1e-7 days).

    Returns
    -------
    float or None
        Refined Julian Date of exact moment.

    Examples
    --------
    For aspect between two bodies (convergence example):

    >>> # Callback returns 0.0 → immediately within tolerance → returns initial_jd
    >>> exact_jd = refine_exact_moment(lambda jd: 0.0, 2451545.0)
    >>> round(exact_jd, 1)
    2451545.0
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
    """
    Find orb entry and exit times using binary search.

    Generic function that works for both aspects and transits.
    Uses a callback to check if within orb at any given time.

    Parameters
    ----------
    is_within_orb_callback : callable
        Function that takes JD and returns bool.
    jd_exact : float
        Julian Date of exact moment.
    search_days : float, optional
        Maximum days to search in each direction.

    Returns
    -------
    tuple of (float or None, float or None)
        Tuple of (jd_begin, jd_end).

    Examples
    --------
    Always-within-orb callback → boundaries extend to search_days limits:

    >>> jd_begin, jd_end = find_orb_boundaries(lambda jd: True, 2451545.0, search_days=1.0)
    >>> jd_begin is not None
    True
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
    """
    Find indices of local minima in error array.

    A local minimum at index i means: error[i-1] > error[i] < error[i+1]

    Parameters
    ----------
    error_array : np.ndarray
        Array of errors/distances.
    threshold : float
        Only return minima below this threshold.

    Returns
    -------
    np.ndarray
        Array of indices where local minima occur.
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
    """
    Interpolate exact position of minimum using quadratic fit.

    Fits a parabola through 3 points to find the minimum.

    Parameters
    ----------
    error_before : float
        Error at idx-1.
    error_current : float
        Error at idx.
    error_after : float
        Error at idx+1.
    idx : int
        Current index.
    step_size : float
        Step size in the grid.

    Returns
    -------
    tuple of (float, float)
        Tuple of (offset_from_idx, interpolated_error).
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
    """
    Calculate adaptive step size based on body speeds.

    Faster bodies need finer sampling to avoid missing crossings.

    Parameters
    ----------
    body_speeds : list
        List of body speeds (degrees/day).
    orb : float
        Orb tolerance (degrees).
    min_step : float, optional
        Minimum step size (days).
    max_step : float, optional
        Maximum step size (days).
    points_per_orb : int, optional
        Desired number of sample points per orb width.

    Returns
    -------
    float
        Optimal step size (days).
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
    """
    Detect if motion is direct or retrograde.

    Parameters
    ----------
    velocity : float
        Longitude velocity (degrees/day).

    Returns
    -------
    str
        "retrograde" or "direct".
    """
    return "retrograde" if velocity < 0 else "direct"


def estimate_duration_hours(jd_begin: float, jd_end: float) -> float:
    """
    Estimate duration in hours between two Julian Dates.

    Parameters
    ----------
    jd_begin : float
        Start Julian Date.
    jd_end : float
        End Julian Date.

    Returns
    -------
    float
        Duration in hours.
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
