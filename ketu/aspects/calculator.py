"""Aspect calculations for Ketu.

This module contains functions for calculating astrological aspects between
astronomical bodies, including scalar and vectorized implementations.
"""

from functools import lru_cache
from itertools import combinations as combs
from typing import Tuple, Optional, List

import numpy as np
import numpy.typing as npt

# Import core data structures.
# The module-level ``aspects`` import is renamed to ``_CORE_ASPECTS`` to free
# the parameter name ``aspects=`` for the configurable aspect-set spec on the
# four public multi-aspect APIs (calculate_aspects, calculate_aspects_vectorized,
# calculate_aspects_batch, find_aspects_between_dates).
from ketu.core import bodies, aspects as _CORE_ASPECTS

# Import preset resolver (single-call entry-point that returns a length-14
# boolean mask into ``_CORE_ASPECTS``).
from ketu.aspects.presets import resolve_aspect_set, AspectSetSpec

# Import ephemeris functions
from ketu.ephemeris.planets import find_exact_aspect, find_all_aspects

# Import calculation utilities
from ketu.calculations import long, positions, distance


def get_orb(body1: int, body2: int, asp: int) -> float:
    """Calculate the orb tolerance for two bodies and an aspect

    Parameters
    ----------
    body1 : int
        First body ID (0-12).
    body2 : int
        Second body ID (0-12).
    asp : int
        Aspect index (0-6).

    Returns
    -------
    float
        Orb in degrees.
    """
    orbs, coef = bodies["orb"], _CORE_ASPECTS["coef"]
    return (orbs[body1] + orbs[body2]) / 2 * coef[asp]


def get_aspect(jdate: float, body1: int, body2: int) -> Optional[Tuple]:
    """Find aspect between two bodies at a given date

    Parameters
    ----------
    jdate : float
        Julian Date.
    body1 : int
        First body ID.
    body2 : int
        Second body ID.

    Returns
    -------
    tuple or None
        Tuple of (body1, body2, aspect_index, orb) or None if no aspect.
    """
    if body1 > body2:
        body1, body2 = body2, body1
    dist = distance(long(jdate, body1), long(jdate, body2))
    for i_asp, aspect in enumerate(_CORE_ASPECTS["angle"]):
        orb = get_orb(body1, body2, i_asp)
        if i_asp == 0 and dist <= orb:
            return body1, body2, i_asp, dist
        elif aspect - orb <= dist <= aspect + orb:
            return body1, body2, i_asp, aspect - dist
    return None


def calculate_aspects(
    jdate: float,
    l_bodies: np.ndarray = bodies,
    aspects: AspectSetSpec = None,
) -> np.ndarray:
    """Calculate all aspects between bodies at a given date

    Parameters
    ----------
    jdate : float
        Julian Date.
    l_bodies : np.ndarray, optional
        Bodies array (default: all bodies).
    aspects : AspectSetSpec, default None
        Aspect set to compute. ``None`` resolves to ``CLASSICAL`` (5 majors:
        Conjunction, Sextile, Square, Trine, Opposition). Accepts a preset
        name (``"classical"``, ``"traditional"``, ``"extended"``), a list of
        aspect names or indices, or a length-14 boolean mask. The result's
        ``i_asp`` field is always a canonical 0-13 index into
        ``ketu.core.aspects``, regardless of the selected subset.

    Returns
    -------
    np.ndarray
        Structured array with fields: body1, body2, i_asp, orb.

    Notes
    -----
    The ``i_asp`` field in the returned structured array is the canonical
    index into ``ketu.core.aspects`` (0-13), not a position within the
    selected subset. Downstream consumers (e.g. Kala) rely on this
    positional contract.
    """
    # Resolve aspect-set ONCE per API call, never inside per-pair loops.
    mask = resolve_aspect_set(aspects)
    selected_indices_set = set(int(i) for i in np.where(mask)[0].tolist())

    bodies_id = l_bodies["id"]
    # ``get_aspect`` is the low-level single-match scanner; out of scope per
    # ASP-07 (it does not accept ``aspects=``). We filter its emitted i_asp
    # against the resolved mask post-hoc to avoid leaking unselected aspects.
    aspects_data = [get_aspect(jdate, *comb) for comb in combs(bodies_id, 2)]
    aspects_data = [
        aspect
        for aspect in aspects_data
        if aspect is not None and int(aspect[2]) in selected_indices_set
    ]
    return np.array(
        aspects_data,
        dtype=[("body1", "i4"), ("body2", "i4"), ("i_asp", "i4"), ("orb", "f4")],
    )


def calculate_aspects_vectorized(
    jdate: float,
    l_bodies: np.ndarray = bodies,
    aspects: AspectSetSpec = None,
) -> np.ndarray:
    """Calculate all aspects using vectorized operations (faster)

    This function computes all planetary aspects in parallel using NumPy
    broadcasting, which is significantly faster than the loop-based approach.

    Parameters
    ----------
    jdate : float
        Julian Date.
    l_bodies : np.ndarray, optional
        Array of bodies (default: all bodies).
    aspects : AspectSetSpec, default None
        Aspect set to compute. ``None`` resolves to ``CLASSICAL`` (5 majors:
        Conjunction, Sextile, Square, Trine, Opposition). Accepts a preset
        name (``"classical"``, ``"traditional"``, ``"extended"``), a list of
        aspect names or indices, or a length-14 boolean mask. The result's
        ``i_asp`` field is always a canonical 0-13 index into
        ``ketu.core.aspects``, regardless of the selected subset.

    Returns
    -------
    np.ndarray
        Structured array of aspects with fields: body1, body2, i_asp, orb.

    Notes
    -----
    The ``i_asp`` field in the returned structured array is the canonical
    index into ``ketu.core.aspects`` (0-13), not a position within the
    selected subset. Downstream consumers (e.g. Kala) rely on this
    positional contract.
    """
    # Resolve aspect-set ONCE per API call (above the per-pair / per-aspect
    # work). The resolved mask, selected indices, and parallel angle/coef
    # slices feed the hot loop below.
    mask: npt.NDArray[np.bool_] = resolve_aspect_set(aspects)
    selected_indices: npt.NDArray[np.intp] = np.where(mask)[0]
    selected_angles: npt.NDArray[np.float64] = _CORE_ASPECTS["angle"][mask]
    selected_coefs: npt.NDArray[np.float64] = _CORE_ASPECTS["coef"][mask]

    bodies_id = l_bodies["id"]
    n_bodies = len(bodies_id)

    # Calculate all positions at once (vectorized)
    all_positions = positions(jdate, l_bodies)

    # Create pairwise combinations indices
    # Upper triangle indices (to avoid duplicates)
    i_indices, j_indices = np.triu_indices(n_bodies, k=1)

    # Get positions for all pairs (vectorized)
    pos1 = all_positions[i_indices]
    pos2 = all_positions[j_indices]

    # Calculate all distances at once (vectorized)
    all_distances = distance(pos1, pos2)  # type: ignore[arg-type]

    # Get body IDs for all pairs
    body1_ids = bodies_id[i_indices]
    body2_ids = bodies_id[j_indices]

    # Prepare to collect results
    results = []
    # Track which pairs have already been matched to an aspect
    # (to match loop behavior which returns on first aspect found)
    matched_pairs = set()

    # For each SELECTED aspect type, check all pairs at once (vectorized).
    # ``k`` is the position within the filtered subset (used for parallel
    # selected_angles/selected_coefs lookup); ``i_asp`` is the canonical
    # 0-13 index emitted to results — Kala's positional contract.
    for k, i_asp_val in enumerate(selected_indices):
        i_asp = int(i_asp_val)
        aspect_angle = float(selected_angles[k])
        aspect_coef = float(selected_coefs[k])

        # Calculate orbs for all pairs (vectorized)
        orbs_body1 = l_bodies["orb"][i_indices]
        orbs_body2 = l_bodies["orb"][j_indices]
        orbs = (orbs_body1 + orbs_body2) / 2 * aspect_coef

        if i_asp == 0:  # Conjunction (canonical index 0)
            # Check which pairs are in orb (vectorized)
            in_orb = all_distances <= orbs
            orb_values = all_distances[in_orb]  # type: ignore[index]
        else:
            # Check which pairs are in orb (vectorized)
            in_orb = (all_distances >= aspect_angle - orbs) & (all_distances <= aspect_angle + orbs)
            # Note: Using aspect_angle - distance (not abs) to match original behavior
            # This can produce negative values when distance > aspect_angle
            orb_values = aspect_angle - all_distances[in_orb]  # type: ignore[index]

        # Collect results for this aspect
        if np.any(in_orb):
            for i, idx in enumerate(np.where(in_orb)[0]):
                pair = (body1_ids[idx], body2_ids[idx])
                # Only add if this pair hasn't been matched yet
                # (matches loop behavior: first aspect found wins)
                if pair not in matched_pairs:
                    # Emit canonical i_asp (NOT k) to preserve Kala contract.
                    results.append((body1_ids[idx], body2_ids[idx], i_asp, orb_values[i]))
                    matched_pairs.add(pair)

    # Convert to structured array
    if len(results) == 0:
        return np.array([], dtype=[("body1", "i4"), ("body2", "i4"), ("i_asp", "i4"), ("orb", "f4")])

    return np.array(
        results,
        dtype=[("body1", "i4"), ("body2", "i4"), ("i_asp", "i4"), ("orb", "f4")],
    )


def calculate_aspects_batch(
    jd_array: np.ndarray,
    l_bodies: np.ndarray = bodies,
    aspects: AspectSetSpec = None,
) -> List[np.ndarray]:
    """Calculate aspects for multiple dates (batch processing)

    This function efficiently computes aspects for multiple dates by leveraging
    vectorized position calculations.

    Parameters
    ----------
    jd_array : np.ndarray
        Array of Julian Dates.
    l_bodies : np.ndarray, optional
        Array of bodies (default: all bodies).
    aspects : AspectSetSpec, default None
        Aspect set to compute. ``None`` resolves to ``CLASSICAL`` (5 majors:
        Conjunction, Sextile, Square, Trine, Opposition). Accepts a preset
        name (``"classical"``, ``"traditional"``, ``"extended"``), a list of
        aspect names or indices, or a length-14 boolean mask. The result's
        ``i_asp`` field is always a canonical 0-13 index into
        ``ketu.core.aspects``, regardless of the selected subset.

    Returns
    -------
    list of np.ndarray
        List of structured arrays, one for each date, containing aspects.

    Notes
    -----
    The ``i_asp`` field in the returned structured arrays is the canonical
    index into ``ketu.core.aspects`` (0-13), not a position within the
    selected subset. Downstream consumers (e.g. Kala) rely on this
    positional contract.
    """
    from ketu.ephemeris.planets import calc_planet_position_batch

    # PERFORMANCE-CRITICAL: resolve aspect-set ONCE per API call, ABOVE the
    # per-date loop. Re-resolving inside the date loop would re-run the
    # resolver n_dates times for the same input — the very anti-pattern the
    # research called out.
    mask: npt.NDArray[np.bool_] = resolve_aspect_set(aspects)
    selected_indices: npt.NDArray[np.intp] = np.where(mask)[0]
    selected_angles: npt.NDArray[np.float64] = _CORE_ASPECTS["angle"][mask]
    selected_coefs: npt.NDArray[np.float64] = _CORE_ASPECTS["coef"][mask]

    bodies_id = l_bodies["id"]
    n_bodies = len(bodies_id)
    n_dates = len(jd_array)

    # Calculate all positions for all bodies for all dates (vectorized!)
    # Shape: (n_bodies, n_dates, 6) where 6 = [lon, lat, dist, long_vel, lat_vel, dist_vel]
    all_body_positions = np.zeros((n_bodies, n_dates, 6))
    for i, body_id in enumerate(bodies_id):
        all_body_positions[i] = calc_planet_position_batch(jd_array, body_id)

    # Extract longitudes (shape: n_bodies x n_dates)
    all_longitudes = all_body_positions[:, :, 0]

    # Prepare pairwise combinations indices
    i_indices, j_indices = np.triu_indices(n_bodies, k=1)
    n_pairs = len(i_indices)

    # Calculate all distances for all pairs for all dates (vectorized!)
    # Shape: (n_pairs, n_dates)
    pos1_all = all_longitudes[i_indices, :]  # Shape: (n_pairs, n_dates)
    pos2_all = all_longitudes[j_indices, :]  # Shape: (n_pairs, n_dates)
    all_distances = distance(pos1_all, pos2_all)  # type: ignore[arg-type]

    # Pre-calculate orbs for all pairs for all aspects
    orbs_body1 = l_bodies["orb"][i_indices]  # Shape: (n_pairs,)
    orbs_body2 = l_bodies["orb"][j_indices]  # Shape: (n_pairs,)

    # Get body IDs for all pairs
    body1_ids = bodies_id[i_indices]
    body2_ids = bodies_id[j_indices]

    # Process each date
    results_by_date = []
    for date_idx in range(n_dates):
        date_results = []
        distances_this_date = all_distances[:, date_idx]  # All pair distances for this date

        # Check each SELECTED aspect type. ``k`` is the position within the
        # filtered subset (parallel to selected_angles / selected_coefs);
        # ``i_asp`` is the canonical 0-13 index emitted to results — Kala's
        # positional contract.
        for k, i_asp_val in enumerate(selected_indices):
            i_asp = int(i_asp_val)
            aspect_angle = float(selected_angles[k])
            aspect_coef = float(selected_coefs[k])
            orbs = (orbs_body1 + orbs_body2) / 2 * aspect_coef

            if i_asp == 0:  # Conjunction (canonical index 0)
                in_orb = distances_this_date <= orbs
                orb_values = distances_this_date[in_orb]  # type: ignore[index]
            else:
                in_orb = (distances_this_date >= aspect_angle - orbs) & (distances_this_date <= aspect_angle + orbs)
                # Note: Using aspect_angle - distance (not abs) to match original behavior
                orb_values = aspect_angle - distances_this_date[in_orb]  # type: ignore[index]

            # Collect results for this aspect
            if np.any(in_orb):
                indices_in_orb = np.where(in_orb)[0]
                for i, idx in enumerate(indices_in_orb):
                    # Emit canonical i_asp (NOT k) to preserve Kala contract.
                    date_results.append((body1_ids[idx], body2_ids[idx], i_asp, orb_values[i]))

        # Convert to structured array for this date
        if len(date_results) == 0:
            results_by_date.append(np.array([], dtype=[("body1", "i4"), ("body2", "i4"), ("i_asp", "i4"), ("orb", "f4")]))
        else:
            results_by_date.append(
                np.array(date_results, dtype=[("body1", "i4"), ("body2", "i4"), ("i_asp", "i4"), ("orb", "f4")])
            )

    return results_by_date


def find_aspect_timing(jdate: float, body1: int, body2: int, aspect_value: float) -> Tuple[float, float, float]:
    """Find beginning, exact, and end times for an aspect

    Parameters
    ----------
    jdate : float
        Reference Julian Date.
    body1 : int
        First body ID.
    body2 : int
        Second body ID.
    aspect_value : float
        Aspect angle in degrees.

    Returns
    -------
    tuple of (float, float, float)
        Tuple of (begin_jd, exact_jd, end_jd).
    """
    # Get the aspect index
    asp_idx = np.where(_CORE_ASPECTS["angle"] == aspect_value)[0]
    if len(asp_idx) == 0:
        raise ValueError(f"unknown aspect value: {aspect_value}")
    asp_idx = asp_idx[0]

    # Calculate orb
    orb = get_orb(body1, body2, asp_idx)

    # Search backward for beginning
    jd_begin = jdate
    step = -0.25  # Quarter day steps
    for _ in range(400):  # Max 100 days backward
        pos1 = long(jd_begin, body1)
        pos2 = long(jd_begin, body2)
        dist = distance(pos1, pos2)

        if abs(dist - aspect_value) > orb:
            jd_begin -= step
            break
        jd_begin += step

    # Search forward for end
    jd_end = jdate
    step = 0.25
    for _ in range(400):  # Max 100 days forward
        pos1 = long(jd_end, body1)
        pos2 = long(jd_end, body2)
        dist = distance(pos1, pos2)

        if abs(dist - aspect_value) > orb:
            jd_end -= step
            break
        jd_end += step

    # Find exact aspect
    exact_jd = find_exact_aspect(jd_begin, jd_end, body1, body2, aspect_value, orb)

    if exact_jd is None:
        exact_jd = jdate  # Fallback to reference date

    return jd_begin, exact_jd, jd_end


def find_aspects_between_dates(
    jdate_start: float,
    jdate_end: float,
    body1: Optional[int] = None,
    body2: Optional[int] = None,
    aspects: AspectSetSpec = None,
) -> List[Tuple]:
    """Find all aspects between two dates

    Parameters
    ----------
    jdate_start : float
        Start Julian Date.
    jdate_end : float
        End Julian Date.
    body1 : int, optional
        First body ID (optional, if None check all).
    body2 : int, optional
        Second body ID (optional, if None check all).
    aspects : AspectSetSpec, default None
        Aspect set to search for. ``None`` resolves to ``CLASSICAL`` (5
        majors). Accepts a preset name (``"classical"``, ``"traditional"``,
        ``"extended"``), a list of aspect names or indices, or a length-14
        boolean mask. The returned tuples contain canonical aspect names
        from ``ketu.core.aspects`` regardless of the selected subset.

    Returns
    -------
    list of tuple
        List of tuples (jdate, body1, body2, aspect_type, aspect_value).
    """
    # Resolve aspect-set ONCE per API call. The downstream
    # ``find_all_aspects`` call iterates over the angle list passed in;
    # passing only ``selected_angles`` confines its search to the selected
    # aspects (no leak of unselected aspect angles).
    mask: npt.NDArray[np.bool_] = resolve_aspect_set(aspects)
    selected_angles: npt.NDArray[np.float64] = _CORE_ASPECTS["angle"][mask]

    results = []

    # Determine which body pairs to check
    if body1 is not None and body2 is not None:
        pairs = [(body1, body2)]
    elif body1 is not None:
        pairs = [(body1, b) for b in bodies["id"] if b != body1]
    elif body2 is not None:
        pairs = [(b, body2) for b in bodies["id"] if b != body2]
    else:
        pairs = list(combs(bodies["id"], 2))

    # Check each pair
    for b1, b2 in pairs:
        if b1 > b2:
            b1, b2 = b2, b1

        # Find all aspects for this pair (filtered to selected aspect set)
        aspect_list = find_all_aspects(jdate_start, jdate_end, b1, b2, list(selected_angles))

        for exact_jd, aspect_angle in aspect_list:
            # Find aspect type — the ``np.where`` lookup against the FULL
            # core.aspects["angle"] yields a canonical 0-13 index, never a
            # filtered-subset position.
            asp_idx = np.where(_CORE_ASPECTS["angle"] == aspect_angle)[0][0]
            aspect_name_bytes = _CORE_ASPECTS["name"][asp_idx]
            aspect_name = aspect_name_bytes.decode() if isinstance(aspect_name_bytes, bytes) else str(aspect_name_bytes)

            results.append((exact_jd, b1, b2, aspect_name, aspect_angle))

    return sorted(results, key=lambda x: x[0])


__all__ = [
    "get_orb",
    "get_aspect",
    "calculate_aspects",
    "calculate_aspects_vectorized",
    "calculate_aspects_batch",
    "find_aspect_timing",
    "find_aspects_between_dates",
]
