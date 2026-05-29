"""
Évaluateur Chiron pur-NumPy — zéro pyswisseph, zéro scipy.

Charge ``ketu/data/chiron_coeffs.npz`` (coefficients Chebyshev par segment,
générés hors-ligne par ``tools/gen_chiron_coeffs.py``) via
``importlib.resources`` et calcule positions + vitesses par différence finie.

Strategy functions (``_chiron_scalar``, ``_chiron_vec``) sont enregistrées dans
``BODY_STRATEGIES`` par le plan 24-03 (``planets.py``).
"""

from __future__ import annotations

from functools import lru_cache
from importlib.resources import files

import numpy as np

from .coordinates import aberration_correction


@lru_cache(maxsize=1)
def _load_chiron_data() -> dict[str, np.ndarray]:
    """Load Chiron Chebyshev coefficient data from the installed package data.

    Uses ``importlib.resources.files`` (Python ≥ 3.9, PEP 451) to locate the
    ``.npz`` inside the installed wheel or editable install — no ``__file__``
    path manipulation, no ``pkg_resources``.

    Returns
    -------
    dict of {str: np.ndarray}
        Dictionary mapping array names to arrays.  Keys: ``lon_coeffs``,
        ``lat_coeffs``, ``dist_coeffs`` (shape ``(1142, 11)``), ``seg_starts``
        (shape ``(1142,)``), ``seg_len`` (scalar float64), ``degree`` (scalar
        int32), ``jd_start``, ``jd_end``.

    Notes
    -----
    The result is cached by ``lru_cache(maxsize=1)`` — the ``.npz`` is read
    from disk only once per interpreter session.

    Examples
    --------
    >>> data = _load_chiron_data()
    >>> data["lon_coeffs"].shape
    (1142, 11)
    """
    ref = files("ketu.data").joinpath("chiron_coeffs.npz")
    with ref.open("rb") as fh:
        npz = np.load(fh)
        return {k: npz[k] for k in npz.files}


def _eval_chiron_qty(
    jd: float,
    coeffs: np.ndarray,
    seg_starts: np.ndarray,
    seg_len: float,
    jd_end: float,
) -> float:
    """Evaluate a single Chebyshev quantity for Chiron at a given Julian Date.

    Parameters
    ----------
    jd : float
        Julian Date at which to evaluate.
    coeffs : np.ndarray
        Chebyshev coefficients array of shape ``(n_segs, degree+1)``.
    seg_starts : np.ndarray
        Start JD of each segment, shape ``(n_segs,)``.
    seg_len : float
        Nominal length of each segment in days (32.0).
    jd_end : float
        JD of the last valid date (2469807.5 for the 1950-2050 range).  Used
        to compute the actual length of the last (possibly truncated) segment.

    Returns
    -------
    float
        Evaluated Chebyshev polynomial value at ``jd``.

    Notes
    -----
    Out-of-range JDs (before 1950 or after 2050) are clamped to the nearest
    segment boundary — the function never raises on out-of-range input.

    The normalised ``t`` coordinate is also clipped to ``[-1, 1]`` to guard
    against floating-point edge effects at segment boundaries.

    The last segment may be shorter than ``seg_len`` when the total range is
    not an exact multiple of 32 days.  The generator fits the polynomial over
    the actual (shorter) segment length, so the evaluator must use that same
    length for ``t`` normalisation — otherwise the mapping of physical JD to
    ``t ∈ [-1, 1]`` would be wrong and accuracy would degrade significantly.

    Examples
    --------
    >>> data = _load_chiron_data()
    >>> val = _eval_chiron_qty(
    ...     2451545.0,
    ...     data["lon_coeffs"],
    ...     data["seg_starts"],
    ...     float(data["seg_len"]),
    ...     float(data["jd_end"]),
    ... )
    >>> 0.0 <= val % 360.0 < 360.0
    True
    """
    si = int((jd - seg_starts[0]) / seg_len)
    si = max(0, min(si, len(seg_starts) - 1))
    # Use the actual segment length (last segment may be truncated).
    actual_len = min(seg_starts[si] + seg_len, jd_end) - seg_starts[si]
    t = float(np.clip(2.0 * (jd - seg_starts[si]) / actual_len - 1.0, -1.0, 1.0))
    return float(np.polynomial.chebyshev.chebval(t, coeffs[si]))


def _chiron_scalar(jd: float) -> tuple[float, float, float, float, float, float]:
    """Compute geocentric Chiron position and velocity at a Julian Date.

    Pure-NumPy implementation using embedded Chebyshev segments.  Velocities
    are estimated by finite difference (``jd_delta = 0.01`` day, matching the
    ``_make_planet_scalar`` pattern in ``planets.py``).

    Parameters
    ----------
    jd : float
        Julian Date (TT/ET).

    Returns
    -------
    tuple of float
        Six-element tuple ``(lon, lat, dist, lon_speed, lat_speed, dist_speed)``
        where:

        * ``lon`` — ecliptic longitude in degrees ``[0, 360)``,
        * ``lat`` — ecliptic latitude in degrees,
        * ``dist`` — geocentric distance in AU,
        * ``lon_speed`` — longitude rate in °/day,
        * ``lat_speed`` — latitude rate in °/day,
        * ``dist_speed`` — distance rate in AU/day.

    Notes
    -----
    The 360° wrap correction on ``dlon`` (the ``> 180 / < -180`` branches) is
    needed because ``% 360`` of two nearby longitudes can straddle 0°/360°.

    Out-of-range JD input is silently clamped (see ``_eval_chiron_qty``).

    Examples
    --------
    >>> result = _chiron_scalar(2451545.0)
    >>> len(result)
    6
    >>> 0.0 <= result[0] < 360.0
    True
    >>> result[2] > 0.0  # distance must be positive
    True
    """
    data = _load_chiron_data()
    seg_starts: np.ndarray = data["seg_starts"]
    seg_len = float(data["seg_len"])
    jd_end = float(data["jd_end"])
    jd_delta = 0.01

    lon = _eval_chiron_qty(jd, data["lon_coeffs"], seg_starts, seg_len, jd_end) % 360.0
    lat = _eval_chiron_qty(jd, data["lat_coeffs"], seg_starts, seg_len, jd_end)
    dist = _eval_chiron_qty(jd, data["dist_coeffs"], seg_starts, seg_len, jd_end)

    lon1 = _eval_chiron_qty(jd + jd_delta, data["lon_coeffs"], seg_starts, seg_len, jd_end) % 360.0
    lat1 = _eval_chiron_qty(jd + jd_delta, data["lat_coeffs"], seg_starts, seg_len, jd_end)
    dist1 = _eval_chiron_qty(jd + jd_delta, data["dist_coeffs"], seg_starts, seg_len, jd_end)

    dlon = lon1 - lon
    if dlon > 180.0:
        dlon -= 360.0
    if dlon < -180.0:
        dlon += 360.0

    return (
        lon,
        lat,
        dist,
        dlon / jd_delta,
        (lat1 - lat) / jd_delta,
        (dist1 - dist) / jd_delta,
    )


def _chiron_vec(
    jd_array: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Compute Chiron position and velocity for an array of Julian Dates.

    Loops over ``jd_array`` calling ``_chiron_scalar``, then applies
    aberration correction per element — matching the ``_make_planet_vec``
    pattern in ``planets.py`` (lines 269-273) so that scalar and batch paths
    agree to within floating-point precision.

    Parameters
    ----------
    jd_array : np.ndarray
        1-D array of Julian Dates (TT/ET).

    Returns
    -------
    tuple of np.ndarray
        Six arrays ``(lon, lat, dist, lon_speed, lat_speed, dist_speed)``,
        each of shape ``(n,)`` where ``n = len(jd_array)``.  Aberration is
        applied to ``lon`` and ``lat`` internally (same convention as
        ``_make_planet_vec`` for regular planets).

    Notes
    -----
    ``_make_planet_vec`` applies aberration inside the vectorised function for
    byte-stability with the original batch path.  ``_chiron_vec`` follows the
    same convention: aberration is applied here so the batch router
    (``calc_planet_position_batch``) does not need to apply it a second time.

    Examples
    --------
    >>> import numpy as np
    >>> jds = np.array([2451545.0, 2451575.0])
    >>> lons, lats, dists, ls, bs, ds = _chiron_vec(jds)
    >>> lons.shape
    (2,)
    >>> all(0.0 <= l < 360.0 for l in lons)
    True
    """
    n = len(jd_array)
    out = np.zeros((n, 6))

    for i, jd in enumerate(jd_array):
        out[i] = _chiron_scalar(float(jd))

    lon = out[:, 0]
    lat = out[:, 1]
    dist = out[:, 2]
    lon_speed = out[:, 3]
    lat_speed = out[:, 4]
    dist_speed = out[:, 5]

    # Apply aberration correction per element — matches _make_planet_vec pattern
    for i in range(n):
        dlon, dlat = aberration_correction(lon[i], lat[i], jd_array[i])
        lon[i] += dlon
        lat[i] += dlat

    return lon, lat, dist, lon_speed, lat_speed, dist_speed
