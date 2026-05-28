"""
Closed-form ASC, MC, ARMC, and Vertex computation.

Shared by all registered house systems (Plans 10-04 Placidus and 10-05 Koch
consume these as inputs to their per-cusp algorithms). Pure NumPy;
vectorized over ``(jd, lat, lon)`` arrays of any compatible broadcast shape.

All angles in degrees, normalized to ``[0, 360)``. Inputs may be scalar or
ndarray; output preserves leading shape.

References
----------
- Meeus, *Astronomical Algorithms* (2nd ed.), chapter 12 (sidereal time)
  and chapter 13 (transformations).
- Astrodienst pd-swisseph C source — ASC/MC closed-form (cross-checked).
- 10-RESEARCH.md §"Don't Hand-Roll" — derivation notes and Pitfall 2
  (always use ``np.arctan2``, never single-arg ``np.arctan``).
"""
from __future__ import annotations

from typing import Union

import numpy as np

from ketu.ephemeris.coordinates import mean_obliquity
from ketu.ephemeris.time import sidereal_time

ArrayLike = Union[float, np.ndarray]


def compute_armc(
    jd: ArrayLike,
    lon: ArrayLike,
) -> np.ndarray:
    """
    Compute the Right Ascension of the Medium Coeli (= local sidereal time).

    ``ARMC = (GMST(jd) + lon_east) mod 360`` (Pitfall 5: explicit
    decomposition that mirrors the swisseph C source, not a hidden
    ``sidereal_time(jd, lon)`` call).

    Parameters
    ----------
    jd : float or np.ndarray
        Julian Date, UT.
    lon : float or np.ndarray
        Geographic longitude, east-positive, degrees.

    Returns
    -------
    np.ndarray
        ARMC in degrees, ``[0, 360)``. Output shape is the broadcast of
        ``jd`` and ``lon``. Scalar inputs return a 0-d ndarray.

    Notes
    -----
    :func:`ketu.ephemeris.time.sidereal_time` is currently scalar-only; we
    lift it via a list-comprehension over the ravelled broadcast shape. The
    cost is negligible (microseconds for 1000 charts). Plan 10-06 may
    replace this with a vectorized ``sidereal_time`` if profiling reveals
    a bottleneck.
    """
    jd_arr = np.asarray(jd, dtype=np.float64)
    lon_arr = np.asarray(lon, dtype=np.float64)
    jd_b, lon_b = np.broadcast_arrays(jd_arr, lon_arr)
    # sidereal_time is scalar-only; lift via list comprehension.
    flat = np.array(
        [sidereal_time(float(jd_v), 0.0) for jd_v in jd_b.ravel()],
        dtype=np.float64,
    ).reshape(jd_b.shape)
    result: np.ndarray = (flat + lon_b) % 360.0
    return result


def compute_ascmc(
    jd: ArrayLike,
    lat: ArrayLike,
    lon: ArrayLike,
) -> dict[str, np.ndarray]:
    """
    Compute ASC, MC, ARMC, Vertex, and obliquity for one or many charts.

    Closed-form via :func:`numpy.arctan2` — never single-arg
    :func:`numpy.arctan` (Pitfall 2 from research).

    Parameters
    ----------
    jd : float or np.ndarray
        Julian Date, UT.
    lat : float or np.ndarray
        Geographic latitude, degrees.
    lon : float or np.ndarray
        Geographic longitude, east-positive, degrees.

    Returns
    -------
    dict[str, np.ndarray]
        Keys: ``"asc"``, ``"mc"``, ``"armc"``, ``"vertex"``, ``"eps"``.
        Each value is an ndarray of the broadcast shape of
        ``(jd, lat, lon)``. Scalar input returns 0-d ndarrays.

    Notes
    -----
    Formulas, all evaluated via :func:`numpy.arctan2` for quadrant
    correctness:

    - **MC**: ``mc = atan2(sin(armc), cos(armc) * cos(eps))``
    - **ASC**: ``asc = atan2(cos(armc), -[sin(eps) * tan(lat)
      + cos(eps) * sin(armc)])``
    - **Vertex**: ASC formula evaluated at the anti-meridian
      (``armc + 180``) with co-latitude (``90 - lat``) substituted for
      ``lat``. The anti-meridian shift is essential — without it the
      formula yields the antivertex (research §"Don't Hand-Roll" reference
      text was incomplete; cross-checked against pyswisseph at
      J2000 / lat=48.86° / lon=2.35°: Vertex 190.1196° vs oracle 190.1198°,
      delta 0.4 arcsec). Open Question 3 retains the advisory 5-arcmin
      tolerance for cross-latitude robustness.
    """
    jd_a = np.asarray(jd, dtype=np.float64)
    lat_a = np.asarray(lat, dtype=np.float64)
    lon_a = np.asarray(lon, dtype=np.float64)

    # Broadcast inputs to a common shape so the output dict has consistent shape.
    jd_b, lat_b, lon_b = np.broadcast_arrays(jd_a, lat_a, lon_a)

    armc = compute_armc(jd_b, lon_b)  # shape == jd_b.shape
    eps_raw = mean_obliquity(jd_b)
    eps: np.ndarray = np.asarray(eps_raw, dtype=np.float64)

    armc_rad = np.deg2rad(armc)
    eps_rad = np.deg2rad(eps)
    lat_rad = np.deg2rad(lat_b)

    # MC: atan2(sin(armc), cos(armc) * cos(eps))
    mc: np.ndarray = np.rad2deg(np.arctan2(
        np.sin(armc_rad),
        np.cos(armc_rad) * np.cos(eps_rad),
    )) % 360.0

    # ASC: atan2(cos(armc), -[sin(eps) * tan(lat) + cos(eps) * sin(armc)])
    asc: np.ndarray = np.rad2deg(np.arctan2(
        np.cos(armc_rad),
        -(np.sin(eps_rad) * np.tan(lat_rad)
          + np.cos(eps_rad) * np.sin(armc_rad)),
    )) % 360.0

    # Vertex: ASC formula at the anti-meridian (armc + 180) with co-latitude
    # (90 - lat) substituted for lat. The anti-meridian shift is required —
    # see docstring; without it the result is the antivertex, off by ~168°.
    armc_anti_rad = np.deg2rad((armc + 180.0) % 360.0)
    co_lat_rad = np.deg2rad(90.0 - lat_b)
    vertex: np.ndarray = np.rad2deg(np.arctan2(
        np.cos(armc_anti_rad),
        -(np.sin(eps_rad) * np.tan(co_lat_rad)
          + np.cos(eps_rad) * np.sin(armc_anti_rad)),
    )) % 360.0

    return {
        "asc": asc,
        "mc": mc,
        "armc": armc,
        "vertex": vertex,
        "eps": eps,
    }
