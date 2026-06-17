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


_RESULT_DTYPE = [("body1", "i4"), ("body2", "i4"), ("i_asp", "i4"), ("orb", "f4")]

# Module-level constants for the tautological-node-opposition guard.
# Using named constants avoids magic numbers and makes the intent auditable.
_RAHU_ID = 10
_KETU_ID = 11
_OPPOSITION_IASP = 13  # Canonical index into core.aspects (last row)


def _is_tautological_node_opposition(body1: int, body2: int, i_asp: int) -> bool:
    """
    Return True iff this aspect is the intra-chart Rahu↔Ketu Opposition.

    Rahu and Ketu are always ~180° apart by astronomical definition (Ketu is
    the Mean South Node, exactly opposite the Mean North Node Rahu). Emitting
    this Opposition adds no information and pollutes downstream consumers.
    The helper is order-insensitive so it works regardless of which body ID
    is passed as ``body1``.

    Parameters
    ----------
    body1 : int
        First body ID (may be a ``np.int32`` from ``body1_ids[idx]``).
    body2 : int
        Second body ID (may be a ``np.int32``).
    i_asp : int
        Canonical aspect index into ``ketu.core.aspects`` (0-13). Dynamic
        rows carry ``i_asp = -2`` and are structurally exempt (returns False).

    Returns
    -------
    bool
        ``True`` only for ``(Rahu, Ketu)`` or ``(Ketu, Rahu)`` paired with
        the Opposition aspect (``i_asp == 13``).
    """
    if i_asp != _OPPOSITION_IASP:
        return False
    pair = (int(body1), int(body2))
    return pair == (_RAHU_ID, _KETU_ID) or pair == (_KETU_ID, _RAHU_ID)


def _detect_aspects_for_date(
    distances: np.ndarray,
    body1_ids: np.ndarray,
    body2_ids: np.ndarray,
    static_iasp: list,
    static_angles: list,
    static_orbs: list,
    dyn_angles: list,
    dyn_orbs: list,
) -> list:
    """
    Detect aspects for a single date's pairwise distances.

    Shared detection core used by both :func:`calculate_aspects_vectorized`
    (one call) and :func:`calculate_aspects_batch` (one call per date). It
    enforces the documented contract — **exactly one row per ``(body1, body2)``
    pair**, static-first then dynamic, first-match-wins — so the two public
    APIs cannot drift apart.

    Parameters
    ----------
    distances : np.ndarray
        Angular separations for every pair, shape ``(n_pairs,)``.
    body1_ids, body2_ids : np.ndarray
        Canonical body IDs for each pair, shape ``(n_pairs,)``.
    static_iasp : list of int
        Canonical 0-13 aspect index for each selected static aspect.
    static_angles : list of float
        Exact angle (degrees) for each selected static aspect.
    static_orbs : list of np.ndarray
        Per-pair orb tolerance arrays (shape ``(n_pairs,)``) for each selected
        static aspect, already scaled by the aspect coefficient.
    dyn_angles : list of float
        Exact angle for each dynamic aspect row (empty when none).
    dyn_orbs : list of np.ndarray
        Per-pair orb tolerance arrays for each dynamic aspect row.

    Returns
    -------
    list of tuple
        ``(body1, body2, i_asp, orb)`` rows; at most one per pair. Dynamic
        rows carry ``i_asp = -2``.
    """
    results = []
    matched_pairs: set = set()

    # Static aspects first (first-match-wins per pair).
    for k, i_asp in enumerate(static_iasp):
        aspect_angle = static_angles[k]
        orbs = static_orbs[k]

        if i_asp == 0:  # Conjunction (canonical index 0)
            in_orb = distances <= orbs
            orb_values = distances[in_orb]
        else:
            in_orb = (distances >= aspect_angle - orbs) & (distances <= aspect_angle + orbs)
            # aspect_angle - distance (not abs) to match original behavior;
            # this can be negative when distance > aspect_angle.
            orb_values = aspect_angle - distances[in_orb]

        if np.any(in_orb):
            for i, idx in enumerate(np.where(in_orb)[0]):
                pair = (body1_ids[idx], body2_ids[idx])
                if pair not in matched_pairs:
                    # Emit canonical i_asp (NOT k) to preserve the downstream contract.
                    # Suppress the tautological intra-chart Rahu↔Ketu Opposition.
                    # The pair is still added to matched_pairs so no later aspect re-emits
                    # for it (first-match-wins contract: Opposition is i_asp 13, the last
                    # static row, so no other static aspect competes; suppressing the emit
                    # while still marking the pair consumed is the safest placement).
                    if not _is_tautological_node_opposition(
                        int(body1_ids[idx]), int(body2_ids[idx]), i_asp
                    ):
                        results.append((body1_ids[idx], body2_ids[idx], i_asp, orb_values[i]))
                    matched_pairs.add(pair)

    # Dynamic aspects second — only pairs not matched by a static aspect.
    for di, dyn_angle in enumerate(dyn_angles):
        orbs = dyn_orbs[di]
        in_orb = np.abs(distances - dyn_angle) <= orbs
        if np.any(in_orb):
            for idx in np.where(in_orb)[0]:
                pair = (body1_ids[idx], body2_ids[idx])
                if pair not in matched_pairs:
                    # Dynamic rows carry i_asp = -2; helper returns False (structurally exempt).
                    # Guard is present for uniformity (D-01 single-source rule).
                    if not _is_tautological_node_opposition(
                        int(body1_ids[idx]), int(body2_ids[idx]), -2
                    ):
                        results.append((body1_ids[idx], body2_ids[idx], -2, dyn_angle - distances[idx]))
                    matched_pairs.add(pair)

    return results


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
            # Suppress the tautological intra-chart Rahu↔Ketu Opposition.
            # Helper is order-insensitive; body1/body2 are already in canonical
            # ascending order after the swap above.
            if _is_tautological_node_opposition(body1, body2, i_asp):
                return None
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
    selected subset. Downstream consumers rely on this positional contract.
    Dynamic rows carry ``i_asp = -2``.

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
                    # Conjunction: tautological node opposition guard returns False
                    # for i_asp=0 (conjunction is never suppressed). Guard present
                    # for D-01 single-source consistency.
                    if not _is_tautological_node_opposition(int(b1), int(b2), i_asp):
                        aspects_data.append((int(b1), int(b2), i_asp, float(dist)))
                    matched = True
                    break
            elif aspect_angle - orb <= dist <= aspect_angle + orb:
                # Suppress the tautological intra-chart Rahu↔Ketu Opposition.
                # Dynamic rows carry i_asp=-2 and are structurally exempt.
                if not _is_tautological_node_opposition(int(b1), int(b2), i_asp):
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
    selected subset. Downstream consumers rely on this positional contract.
    Dynamic rows carry ``i_asp = -2``.
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

    # Pre-compute per-pair orb sums once (independent of aspect type), then
    # scale by each aspect's coefficient. ``i_asp`` is the canonical 0-13 index
    # emitted to results — the downstream positional contract.
    pair_orb_sums = (l_bodies["orb"][i_indices] + l_bodies["orb"][j_indices]) / 2
    static_iasp = [int(v) for v in selected_indices]
    static_angles = [float(v) for v in selected_angles]
    static_orbs = [pair_orb_sums * float(c) for c in selected_coefs]

    dyn_angles: list = []
    dyn_orbs: list = []
    if dyn is not None:
        dyn_angles = [float(r["angle"]) for r in dyn]
        dyn_orbs = [pair_orb_sums * float(r["coef"]) for r in dyn]

    results = _detect_aspects_for_date(
        all_distances,
        body1_ids,
        body2_ids,
        static_iasp,
        static_angles,
        static_orbs,
        dyn_angles,
        dyn_orbs,
    )

    # Convert to structured array
    if len(results) == 0:
        return np.array([], dtype=_RESULT_DTYPE)

    return np.array(results, dtype=_RESULT_DTYPE)


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
    selected subset. Downstream consumers rely on this positional contract.
    Dynamic rows carry ``i_asp = -2``.
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

    # Process each date through the shared detection core, so batch and
    # vectorized cannot drift apart (one row per pair, static-first/dynamic-second).
    results_by_date = []
    for date_idx in range(n_dates):
        distances_this_date = all_distances[:, date_idx]  # All pair distances for this date

        date_results = _detect_aspects_for_date(
            distances_this_date,
            body1_ids,
            body2_ids,
            selected_iasp_ints,
            selected_angles_f,
            selected_orbs_per_aspect,
            dyn_angles_f,
            dyn_orbs_per_row,
        )

        # Convert to structured array for this date
        if len(date_results) == 0:
            results_by_date.append(np.array([], dtype=_RESULT_DTYPE))
        else:
            results_by_date.append(np.array(date_results, dtype=_RESULT_DTYPE))

    return results_by_date


def find_aspect_timing(
    jdate: float,
    body1: int,
    body2: int,
    aspect_value: float,
    orb: Optional[float] = None,
    dyn_coef: Optional[float] = None,
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
        Explicit orb in degrees.  When provided, orb resolution
        short-circuits immediately — **this escape hatch wins even when
        ``dyn_coef`` is also given** (HARM-05 locked precedence: explicit
        ``orb`` wins silently, no :exc:`ValueError` is raised).  Use this for
        one-off calls where you have already computed the orb.
    dyn_coef : float, optional
        Dynamic-orb coefficient.  When ``orb`` is ``None`` and
        ``dyn_coef`` is not ``None``, the orb is derived as
        ``(bodies['orb'][body1] + bodies['orb'][body2]) / 2 * dyn_coef``,
        mirroring the formula used by ``calculate_aspects`` (lines 215-216).
        This removes the need for callers to pre-compute the orb for
        off-table harmonic angles — pass the ``coef`` field from a
        ``generate_harmonic_aspects`` row directly.  When both ``orb`` and
        ``dyn_coef`` are given, **explicit ``orb`` wins silently** (HARM-05).

        When both ``orb`` and ``dyn_coef`` are ``None`` (default static path),
        the orb is resolved from the ``_CORE_ASPECTS`` table via
        ``get_orb(body1, body2, asp_idx)``.  If ``aspect_value`` is not found
        in the table a clear :exc:`ValueError` is raised (never
        :exc:`IndexError`).

    Returns
    -------
    tuple of (float, float, float)
        Tuple of (begin_jd, exact_jd, end_jd).

    Raises
    ------
    ValueError
        If both ``orb`` and ``dyn_coef`` are ``None`` and ``aspect_value``
        is not found in the ``_CORE_ASPECTS`` table.

    Examples
    --------
    >>> from ketu.aspects.calculator import find_aspect_timing
    >>> jd = 2451545.0
    >>> # Dynamic orb derived from coefficient — no pre-computation needed (HARM-04):
    >>> result = find_aspect_timing(jd, 0, 1, 51.4286, dyn_coef=1/7)
    >>> len(result) == 3
    True
    """
    if orb is not None:
        # Explicit orb wins silently — escape hatch short-circuits, even when
        # dyn_coef is also provided (HARM-05 locked precedence: explicit orb
        # wins, NOT raise).
        pass
    elif dyn_coef is not None:
        # Dynamic path — derive orb from the coefficient.  Mirrors the formula
        # in calculate_aspects (calculator.py:215-216):
        #   (orb_b1 + orb_b2) / 2 * dyn_coef
        orb = (
            float(bodies["orb"][body1]) + float(bodies["orb"][body2])
        ) / 2 * dyn_coef
    else:
        # Static path — frozen-table lookup (UNCHANGED behaviour).
        asp_idx = np.where(_CORE_ASPECTS["angle"] == aspect_value)[0]
        if len(asp_idx) == 0:
            raise ValueError(f"unknown aspect value: {aspect_value}")
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
