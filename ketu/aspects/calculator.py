"""Aspect calculations for Ketu.

This module contains functions for calculating astrological aspects between
astronomical bodies, including scalar and vectorized implementations.
"""

from functools import lru_cache
from itertools import combinations as combs
from typing import Tuple, Optional, List

import numpy as np

# Import core data structures
from ketu.core import bodies, aspects

# Import ephemeris functions
from ketu.ephemeris.planets import find_exact_aspect, find_all_aspects

# Import calculation utilities
from ketu.calculations import long, positions, distance


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


def get_aspect(jdate: float, body1: int, body2: int) -> Optional[Tuple]:
    """Find aspect between two bodies at a given date.

    Args:
        jdate: Julian Date
        body1: First body ID
        body2: Second body ID

    Returns:
        Tuple of (body1, body2, aspect_index, orb) or None if no aspect
    """
    if body1 > body2:
        body1, body2 = body2, body1
    dist = distance(long(jdate, body1), long(jdate, body2))
    for i_asp, aspect in enumerate(aspects["angle"]):
        orb = get_orb(body1, body2, i_asp)
        if i_asp == 0 and dist <= orb:
            return body1, body2, i_asp, dist
        elif aspect - orb <= dist <= aspect + orb:
            return body1, body2, i_asp, aspect - dist
    return None


def calculate_aspects(jdate: float, l_bodies=bodies) -> np.ndarray:
    """Calculate all aspects between bodies at a given date.

    Args:
        jdate: Julian Date
        l_bodies: Bodies array (default: all bodies)

    Returns:
        Structured array with fields: body1, body2, i_asp, orb
    """
    bodies_id = l_bodies["id"]
    aspects_data = [get_aspect(jdate, *comb) for comb in combs(bodies_id, 2)]
    aspects_data = [aspect for aspect in aspects_data if aspect is not None]
    return np.array(
        aspects_data,
        dtype=[("body1", "i4"), ("body2", "i4"), ("i_asp", "i4"), ("orb", "f4")],
    )


def calculate_aspects_vectorized(jdate: float, l_bodies=bodies) -> np.ndarray:
    """Calculate all aspects using vectorized operations (faster).

    This function computes all planetary aspects in parallel using NumPy
    broadcasting, which is significantly faster than the loop-based approach.

    Args:
        jdate: Julian Date
        l_bodies: Array of bodies (default: all bodies)

    Returns:
        Structured array of aspects with fields: body1, body2, i_asp, orb
    """
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

    # For each aspect type, check all pairs at once (vectorized)
    for i_asp, aspect_angle in enumerate(aspects["angle"]):
        # Calculate orbs for all pairs (vectorized)
        orbs_body1 = l_bodies["orb"][i_indices]
        orbs_body2 = l_bodies["orb"][j_indices]
        aspect_coef = aspects["coef"][i_asp]
        orbs = (orbs_body1 + orbs_body2) / 2 * aspect_coef

        if i_asp == 0:  # Conjunction
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
                    results.append((body1_ids[idx], body2_ids[idx], i_asp, orb_values[i]))
                    matched_pairs.add(pair)

    # Convert to structured array
    if len(results) == 0:
        return np.array([], dtype=[("body1", "i4"), ("body2", "i4"), ("i_asp", "i4"), ("orb", "f4")])

    return np.array(
        results,
        dtype=[("body1", "i4"), ("body2", "i4"), ("i_asp", "i4"), ("orb", "f4")],
    )


def calculate_aspects_batch(jd_array: np.ndarray, l_bodies=bodies) -> List[np.ndarray]:
    """Calculate aspects for multiple dates (batch processing).

    This function efficiently computes aspects for multiple dates by leveraging
    vectorized position calculations.

    Args:
        jd_array: Array of Julian Dates
        l_bodies: Array of bodies (default: all bodies)

    Returns:
        List of structured arrays, one for each date, containing aspects
    """
    from ketu.ephemeris.planets import calc_planet_position_batch

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

        # Check each aspect type
        for i_asp, aspect_angle in enumerate(aspects["angle"]):
            aspect_coef = aspects["coef"][i_asp]
            orbs = (orbs_body1 + orbs_body2) / 2 * aspect_coef

            if i_asp == 0:  # Conjunction
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
    """Find beginning, exact, and end times for an aspect.

    Args:
        jdate: Reference Julian Date
        body1: First body ID
        body2: Second body ID
        aspect_value: Aspect angle in degrees

    Returns:
        Tuple of (begin_jd, exact_jd, end_jd)
    """
    # Get the aspect index
    asp_idx = np.where(aspects["angle"] == aspect_value)[0]
    if len(asp_idx) == 0:
        raise ValueError(f"Unknown aspect value: {aspect_value}")
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
    jdate_start: float, jdate_end: float, body1: Optional[int] = None, body2: Optional[int] = None
) -> List[Tuple]:
    """Find all aspects between two dates.

    Args:
        jdate_start: Start Julian Date
        jdate_end: End Julian Date
        body1: First body ID (optional, if None check all)
        body2: Second body ID (optional, if None check all)

    Returns:
        List of tuples (jdate, body1, body2, aspect_type, aspect_value)
    """
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

        # Find all aspects for this pair
        aspect_list = find_all_aspects(jdate_start, jdate_end, b1, b2, list(aspects["angle"]))

        for exact_jd, aspect_angle in aspect_list:
            # Find aspect type
            asp_idx = np.where(aspects["angle"] == aspect_angle)[0][0]
            aspect_name_bytes = aspects["name"][asp_idx]
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
