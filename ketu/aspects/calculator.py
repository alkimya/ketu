"""
Aspect calculations for Ketu.

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

# Import dynamic aspect spec type alias and helper
from ketu.aspects.harmonics import DynamicAspectSpec

# Import ephemeris functions
from ketu.ephemeris.planets import find_exact_aspect, find_all_aspects

# Import calculation utilities
from ketu.calculations import long, positions, distance


def _normalize_dynamic_specs(
    dynamic_specs: DynamicAspectSpec,
) -> Optional[np.ndarray]:
    """
    Normalise *dynamic_specs* into a single structured array or ``None``.

    Parameters
    ----------
    dynamic_specs : DynamicAspectSpec
        A single ``generate_harmonic_aspects`` array, a list of such arrays,
        or ``None``.

    Returns
    -------
    np.ndarray or None
        Concatenated structured array when *dynamic_specs* is non-empty,
        ``None`` when it is ``None`` or an empty list.
    """
    if dynamic_specs is None:
        return None
    if isinstance(dynamic_specs, list):
        if len(dynamic_specs) == 0:
            return None
        return np.concatenate(dynamic_specs)
    return dynamic_specs


def get_orb(body1: int, body2: int, asp: int) -> float:
    """
    Calculate the orb tolerance for two bodies and an aspect.

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
    """
    Find aspect between two bodies at a given date.

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
    dynamic_specs: DynamicAspectSpec = None,
) -> np.ndarray:
    """
    Calculate all aspects between bodies at a given date.

    Parameters
    ----------
    jdate : float
        Julian Date.
    l_bodies : np.ndarray, optional
        Bodies array (default: all bodies).
    aspects : AspectSetSpec, default None
        Aspect set to compute. ``None`` resolves to the default 7 half-circle
        aspects (harmonics 1,2,3,6 — Conjunction, Semi-sextile, Sextile,
        Square, Trine, Quincunx, Opposition). Accepts a preset name
        (``"classical"``, ``"traditional"``, ``"extended"``), a list of
        aspect names or indices, or a length-14 boolean mask. The result's
        ``i_asp`` field is always a canonical 0-13 index into
        ``ketu.core.aspects``, regardless of the selected subset.
    dynamic_specs : DynamicAspectSpec, default None
        Optional dynamic aspect specs as returned by
        :func:`~ketu.aspects.harmonics.generate_harmonic_aspects`, or a list
        of such arrays (they are concatenated internally).  When provided,
        dynamic aspects are detected **after** the static set (static-first,
        dynamic-second, first-match-wins per pair).  Dynamic rows carry
        ``i_asp = -2`` sentinel.  The orb is derived from
        ``(core.bodies['orb'][b1] + core.bodies['orb'][b2]) / 2 × dyn_coef``.
        Output dtype is UNCHANGED: ``(body1 i4, body2 i4, i_asp i4, orb f4)``;
        exactly one row per ``(body1, body2)`` pair.

    Returns
    -------
    np.ndarray
        Structured array with fields: body1, body2, i_asp, orb.

    Notes
    -----
    The ``i_asp`` field in the returned structured array is the canonical
    index into ``ketu.core.aspects`` (0-13), not a position within the
    selected subset. Downstream consumers (e.g. Kala) rely on this
    positional contract. Dynamic rows carry ``i_asp = -2``.

    Examples
    --------
    >>> import numpy as np
    >>> from ketu.aspects.calculator import calculate_aspects
    >>> from ketu.aspects.harmonics import generate_harmonic_aspects
    >>> jd = 2451545.0
    >>> specs = generate_harmonic_aspects(7)
    >>> result = calculate_aspects(jd, dynamic_specs=specs)
    >>> result.dtype.names == ('body1', 'body2', 'i_asp', 'orb')
    True
    >>> any(r['i_asp'] == -2 for r in result)  # at least one dynamic row detected
    True
    """
    # Resolve aspect-set ONCE per API call, never inside per-pair loops.
    mask = resolve_aspect_set(aspects)
    selected_indices: list[int] = [int(i) for i in np.where(mask)[0].tolist()]
    selected_angles: npt.NDArray[np.float64] = _CORE_ASPECTS["angle"][mask]
    selected_coefs: npt.NDArray[np.float64] = _CORE_ASPECTS["coef"][mask]

    # Normalise dynamic_specs once (None / single array / list → array or None).
    dyn = _normalize_dynamic_specs(dynamic_specs)

    bodies_id = l_bodies["id"]
    aspects_data = []
    for b1, b2 in combs(bodies_id, 2):
        # combs() always yields pairs in iteration order (body IDs 0-13 ascending),
        # so b1 < b2 is guaranteed here. No swap needed.
        dist = distance(long(jdate, int(b1)), long(jdate, int(b2)))
        # Iterate ONLY selected aspects (first-match-wins within the selected set).
        # This matches the vectorized behavior: unselected aspects are not
        # considered at all, so a pair "blocked" by an unselected first-match
        # in get_aspect is now correctly checked against the selected set.
        matched = False
        for k, i_asp in enumerate(selected_indices):
            aspect_angle = float(selected_angles[k])
            aspect_coef = float(selected_coefs[k])
            orb = (l_bodies["orb"][np.where(l_bodies["id"] == b1)[0][0]] +
                   l_bodies["orb"][np.where(l_bodies["id"] == b2)[0][0]]) / 2 * aspect_coef
            if i_asp == 0:
                if dist <= orb:
                    aspects_data.append((int(b1), int(b2), i_asp, float(dist)))
                    matched = True
                    break
            elif aspect_angle - orb <= dist <= aspect_angle + orb:
                aspects_data.append((int(b1), int(b2), i_asp, float(aspect_angle - dist)))
                matched = True
                break

        # Dynamic path — only when the static loop did NOT match this pair.
        if dyn is not None and not matched:
            orb_b1 = float(l_bodies["orb"][np.where(l_bodies["id"] == b1)[0][0]])
            orb_b2 = float(l_bodies["orb"][np.where(l_bodies["id"] == b2)[0][0]])
            for dyn_row in dyn:
                dyn_angle = float(dyn_row["angle"])
                dyn_coef = float(dyn_row["coef"])
                dyn_orb = (orb_b1 + orb_b2) / 2 * dyn_coef
                if abs(dist - dyn_angle) <= dyn_orb:
                    aspects_data.append(
                        (int(b1), int(b2), -2, float(dyn_angle - dist))
                    )
                    break

    return np.array(
        aspects_data,
        dtype=[("body1", "i4"), ("body2", "i4"), ("i_asp", "i4"), ("orb", "f4")],
    )


def calculate_aspects_vectorized(
    jdate: float,
    l_bodies: np.ndarray = bodies,
    aspects: AspectSetSpec = None,
    dynamic_specs: DynamicAspectSpec = None,
) -> np.ndarray:
    """
    Calculate all aspects using vectorized operations (faster).

    This function computes all planetary aspects in parallel using NumPy
    broadcasting, which is significantly faster than the loop-based approach.

    Parameters
    ----------
    jdate : float
        Julian Date.
    l_bodies : np.ndarray, optional
        Array of bodies (default: all bodies).
    aspects : AspectSetSpec, default None
        Aspect set to compute. ``None`` resolves to the default 7 half-circle
        aspects (harmonics 1,2,3,6 — Conjunction, Semi-sextile, Sextile,
        Square, Trine, Quincunx, Opposition). Accepts a preset name
        (``"classical"``, ``"traditional"``, ``"extended"``), a list of
        aspect names or indices, or a length-14 boolean mask. The result's
        ``i_asp`` field is always a canonical 0-13 index into
        ``ketu.core.aspects``, regardless of the selected subset.
    dynamic_specs : DynamicAspectSpec, default None
        Optional dynamic aspect specs as returned by
        :func:`~ketu.aspects.harmonics.generate_harmonic_aspects`, or a list
        of such arrays (they are concatenated internally).  Dynamic aspects
        are detected **after** the static set (static-first, dynamic-second,
        first-match-wins per pair).  Dynamic rows carry ``i_asp = -2``
        sentinel.  The orb is derived from
        ``(core.bodies['orb'][b1] + core.bodies['orb'][b2]) / 2 × dyn_coef``.
        Output dtype is UNCHANGED: ``(body1 i4, body2 i4, i_asp i4, orb f4)``;
        exactly one row per ``(body1, body2)`` pair.

    Returns
    -------
    np.ndarray
        Structured array of aspects with fields: body1, body2, i_asp, orb.

    Notes
    -----
    The ``i_asp`` field in the returned structured array is the canonical
    index into ``ketu.core.aspects`` (0-13), not a position within the
    selected subset. Downstream consumers (e.g. Kala) rely on this
    positional contract. Dynamic rows carry ``i_asp = -2``.
    """
    # Resolve aspect-set ONCE per API call (above the per-pair / per-aspect
    # work). The resolved mask, selected indices, and parallel angle/coef
    # slices feed the hot loop below.
    mask: npt.NDArray[np.bool_] = resolve_aspect_set(aspects)
    selected_indices: npt.NDArray[np.intp] = np.where(mask)[0]
    selected_angles: npt.NDArray[np.float64] = _CORE_ASPECTS["angle"][mask]
    selected_coefs: npt.NDArray[np.float64] = _CORE_ASPECTS["coef"][mask]

    # Normalise dynamic_specs once.
    dyn = _normalize_dynamic_specs(dynamic_specs)

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

    # Pre-compute orb arrays once (independent of aspect type).
    orbs_body1 = l_bodies["orb"][i_indices]
    orbs_body2 = l_bodies["orb"][j_indices]

    # For each SELECTED aspect type, check all pairs at once (vectorized).
    # ``k`` is the position within the filtered subset (used for parallel
    # selected_angles/selected_coefs lookup); ``i_asp`` is the canonical
    # 0-13 index emitted to results — Kala's positional contract.
    for k, i_asp_val in enumerate(selected_indices):
        i_asp = int(i_asp_val)
        aspect_angle = float(selected_angles[k])
        aspect_coef = float(selected_coefs[k])

        # Calculate orbs for all pairs (vectorized)
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

    # Dynamic path — runs after all static aspects (static-first/dynamic-second).
    # Only pairs not yet matched by a static aspect are eligible.
    if dyn is not None:
        for dyn_row in dyn:
            dyn_angle = float(dyn_row["angle"])
            dyn_coef = float(dyn_row["coef"])
            orbs = (orbs_body1 + orbs_body2) / 2 * dyn_coef
            in_orb = np.abs(all_distances - dyn_angle) <= orbs
            if np.any(in_orb):
                for idx in np.where(in_orb)[0]:
                    pair = (body1_ids[idx], body2_ids[idx])
                    if pair not in matched_pairs:
                        results.append(
                            (
                                body1_ids[idx],
                                body2_ids[idx],
                                -2,
                                dyn_angle - all_distances[idx],
                            )
                        )
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
    dynamic_specs: DynamicAspectSpec = None,
) -> List[np.ndarray]:
    """
    Calculate aspects for multiple dates (batch processing).

    This function efficiently computes aspects for multiple dates by leveraging
    vectorized position calculations.

    Parameters
    ----------
    jd_array : np.ndarray
        Array of Julian Dates.
    l_bodies : np.ndarray, optional
        Array of bodies (default: all bodies).
    aspects : AspectSetSpec, default None
        Aspect set to compute. ``None`` resolves to the default 7 half-circle
        aspects (harmonics 1,2,3,6 — Conjunction, Semi-sextile, Sextile,
        Square, Trine, Quincunx, Opposition). Accepts a preset name
        (``"classical"``, ``"traditional"``, ``"extended"``), a list of
        aspect names or indices, or a length-14 boolean mask. The result's
        ``i_asp`` field is always a canonical 0-13 index into
        ``ketu.core.aspects``, regardless of the selected subset.
    dynamic_specs : DynamicAspectSpec, default None
        Optional dynamic aspect specs as returned by
        :func:`~ketu.aspects.harmonics.generate_harmonic_aspects`, or a list
        of such arrays (they are concatenated internally).  Dynamic aspects
        are detected **after** the static set for each date
        (static-first, dynamic-second, first-match-wins per pair).  Dynamic
        rows carry ``i_asp = -2`` sentinel.  The orb is derived from
        ``(core.bodies['orb'][b1] + core.bodies['orb'][b2]) / 2 × dyn_coef``.
        Output dtype is UNCHANGED: ``(body1 i4, body2 i4, i_asp i4, orb f4)``;
        exactly one row per ``(body1, body2)`` pair per date.

    Returns
    -------
    list of np.ndarray
        List of structured arrays, one for each date, containing aspects.

    Notes
    -----
    The ``i_asp`` field in the returned structured arrays is the canonical
    index into ``ketu.core.aspects`` (0-13), not a position within the
    selected subset. Downstream consumers (e.g. Kala) rely on this
    positional contract. Dynamic rows carry ``i_asp = -2``.
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
    # Hoist per-aspect Python-scalar conversions ABOVE the per-date loop so we
    # pay the cast cost ``len(selected_indices)`` times total instead of
    # ``n_dates × len(selected_indices)`` (ASP-08 hot-loop fix).
    selected_iasp_ints: list[int] = [int(v) for v in selected_indices]
    selected_angles_f: list[float] = [float(v) for v in selected_angles]
    selected_coefs_f: list[float] = [float(v) for v in selected_coefs]

    # Normalise dynamic_specs once (date-independent).
    dyn = _normalize_dynamic_specs(dynamic_specs)

    # Hoist dynamic angle/coef extractions ABOVE the per-date loop
    # (dyn specs are date-independent — mirror the existing hoisting of
    # selected_orbs_per_aspect below).
    dyn_angles_f: list[float] = []
    dyn_coefs_f: list[float] = []
    if dyn is not None:
        dyn_angles_f = [float(r["angle"]) for r in dyn]
        dyn_coefs_f = [float(r["coef"]) for r in dyn]

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

    # Pre-compute per-aspect orb arrays ONCE (independent of date) — the
    # only per-aspect input is ``aspect_coef``, so this work is hoisted out
    # of the per-date loop entirely.
    pair_orb_sums = (orbs_body1 + orbs_body2) / 2  # Shape: (n_pairs,)
    selected_orbs_per_aspect = [pair_orb_sums * c for c in selected_coefs_f]

    # Pre-compute dynamic orb arrays per spec row (also date-independent).
    dyn_orbs_per_row: list[np.ndarray] = []
    if dyn is not None:
        dyn_orbs_per_row = [pair_orb_sums * c for c in dyn_coefs_f]

    # Process each date
    results_by_date = []
    for date_idx in range(n_dates):
        date_results = []
        distances_this_date = all_distances[:, date_idx]  # All pair distances for this date

        # Check each SELECTED aspect type. ``k`` is the position within the
        # filtered subset (parallel to selected_angles / selected_coefs);
        # ``i_asp`` is the canonical 0-13 index emitted to results — Kala's
        # positional contract.
        # Build matched_pairs for the date to support static-first/dynamic-second.
        matched_pairs: set = set()
        for k in range(len(selected_iasp_ints)):
            i_asp = selected_iasp_ints[k]
            aspect_angle = selected_angles_f[k]
            orbs = selected_orbs_per_aspect[k]

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
                    matched_pairs.add((body1_ids[idx], body2_ids[idx]))

        # Dynamic path — runs after all static aspects for this date.
        if dyn is not None:
            for di, dyn_angle in enumerate(dyn_angles_f):
                orbs = dyn_orbs_per_row[di]
                in_orb = np.abs(distances_this_date - dyn_angle) <= orbs
                if np.any(in_orb):
                    for idx in np.where(in_orb)[0]:
                        pair = (body1_ids[idx], body2_ids[idx])
                        if pair not in matched_pairs:
                            date_results.append(
                                (
                                    body1_ids[idx],
                                    body2_ids[idx],
                                    -2,
                                    dyn_angle - distances_this_date[idx],
                                )
                            )
                            matched_pairs.add(pair)

        # Convert to structured array for this date
        if len(date_results) == 0:
            results_by_date.append(np.array([], dtype=[("body1", "i4"), ("body2", "i4"), ("i_asp", "i4"), ("orb", "f4")]))
        else:
            results_by_date.append(
                np.array(date_results, dtype=[("body1", "i4"), ("body2", "i4"), ("i_asp", "i4"), ("orb", "f4")])
            )

    return results_by_date


def find_aspect_timing(
    jdate: float,
    body1: int,
    body2: int,
    aspect_value: float,
    orb: Optional[float] = None,
) -> Tuple[float, float, float]:
    """
    Find beginning, exact, and end times for an aspect.

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
    orb : float, optional
        Explicit orb in degrees.  When provided, the ``_CORE_ASPECTS`` table
        lookup is skipped entirely — this is the **dynamic path** for
        off-table angles (e.g. ``51.4286`` for H7-1).  Pass the orb derived
        from your ``dynamic_specs`` row, e.g.
        ``(bodies['orb'][b1] + bodies['orb'][b2]) / 2 * dyn_coef``.

        When ``orb`` is ``None`` (default), the orb is resolved from the
        ``_CORE_ASPECTS`` table using ``get_orb(body1, body2, asp_idx)``.
        If ``aspect_value`` is not found in the table a clear
        :exc:`ValueError` is raised (never :exc:`IndexError`).

    Returns
    -------
    tuple of (float, float, float)
        Tuple of (begin_jd, exact_jd, end_jd).

    Raises
    ------
    ValueError
        If ``orb`` is ``None`` and ``aspect_value`` is not found in the
        ``_CORE_ASPECTS`` table.
    """
    if orb is None:
        # Static path — look up the aspect in the frozen table.
        asp_idx = np.where(_CORE_ASPECTS["angle"] == aspect_value)[0]
        if len(asp_idx) == 0:
            raise ValueError(f"unknown aspect value: {aspect_value}")
        # Calculate orb from the table.
        orb = get_orb(body1, body2, int(asp_idx[0]))

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
    dynamic_specs: DynamicAspectSpec = None,
) -> List[Tuple]:
    """
    Find all aspects between two dates.

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
        Aspect set to search for. ``None`` resolves to the default 7
        half-circle aspects (harmonics 1,2,3,6). Accepts a preset name
        (``"classical"``, ``"traditional"``, ``"extended"``), a list of
        aspect names or indices, or a length-14 boolean mask. The returned
        tuples contain canonical aspect names from ``ketu.core.aspects``
        regardless of the selected subset.
    dynamic_specs : DynamicAspectSpec, default None
        Optional dynamic aspect specs as returned by
        :func:`~ketu.aspects.harmonics.generate_harmonic_aspects`, or a list
        of such arrays.  When provided, the angles in the specs are added to
        the search angles passed to ``find_all_aspects`` (union of static and
        dynamic angles).  Returned tuples with a dynamic angle carry the
        **synthetic name** from the spec (e.g. ``"H7-1"``) instead of
        crashing with :exc:`IndexError`.

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

    # Normalise dynamic_specs and build the union angle list.
    dyn = _normalize_dynamic_specs(dynamic_specs)
    if dyn is not None:
        # Use Python floats from f4 array so round-trip through find_all_aspects
        # preserves exact equality on the name-lookup comparison below.
        dyn_angles_list: list[float] = [float(a) for a in dyn["angle"].tolist()]
        search_angles: list[float] = list(selected_angles) + dyn_angles_list
    else:
        search_angles = list(selected_angles)

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

        # Find all aspects for this pair (filtered to selected aspect set + dynamic angles)
        aspect_list = find_all_aspects(jdate_start, jdate_end, b1, b2, search_angles)

        for exact_jd, aspect_angle in aspect_list:
            # Len-checked name resolution — never crashes with IndexError on
            # dynamic off-table angles (ASP-09 guard).
            static_idx = np.where(_CORE_ASPECTS["angle"] == aspect_angle)[0]
            if len(static_idx) > 0:
                aspect_name_bytes = _CORE_ASPECTS["name"][static_idx[0]]
                aspect_name = (
                    aspect_name_bytes.decode()
                    if isinstance(aspect_name_bytes, bytes)
                    else str(aspect_name_bytes)
                )
            elif dyn is not None:
                # Dynamic angle — look up synthetic name from spec.
                dyn_idx = np.where(dyn["angle"] == aspect_angle)[0]
                if len(dyn_idx) == 0:  # pragma: no cover
                    # Fallback: close-match in case f4 round-trip introduces tiny drift.
                    # Unreachable in practice: dyn_angles_list uses Python floats from f4
                    # values and find_all_aspects returns those exact values, so the
                    # exact-equality lookup above always succeeds.
                    dyn_idx = np.where(np.isclose(dyn["angle"], aspect_angle, atol=1e-4))[0]
                if len(dyn_idx) > 0:
                    raw_name = dyn["name"][dyn_idx[0]]
                    aspect_name = (
                        raw_name.decode()
                        if isinstance(raw_name, bytes)
                        else str(raw_name)
                    )
                else:  # pragma: no cover
                    # Defensive fallback — unreachable: find_all_aspects only returns
                    # angles from search_angles, which includes all dyn angles; isclose
                    # covers any f4 round-trip drift, so this branch cannot be triggered
                    # by well-formed calls.
                    aspect_name = f"{aspect_angle:.4f}"
            else:  # pragma: no cover
                # Defensive fallback — unreachable: when dyn is None, search_angles
                # contains only static angles; find_all_aspects can only return one of
                # those, so the static_idx lookup above always succeeds.
                aspect_name = f"{aspect_angle:.4f}"

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
