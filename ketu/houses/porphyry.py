"""
Porphyry house system — closed-form trisection.

Used as the polar fallback for Placidus and Koch (HOU-06). Mathematically
defined at all latitudes including 90° because it depends only on ASC/MC,
not on declination-dependent ascensional difference.

Trisection (research §"Don't Hand-Roll → Porphyry formula"):

    upper_step = ((asc - mc) mod 360) / 3
    cusp_11 = mc + upper_step
    cusp_12 = mc + 2 * upper_step
    lower_step = ((ic - asc) mod 360) / 3   where ic = (mc + 180) mod 360
    cusp_2  = asc + lower_step
    cusp_3  = asc + 2 * lower_step
    cusps 5/6/8/9 = opposites of 11/12/2/3
    cusps 1/4/7/10 = ASC/IC/DESC/MC
"""
from __future__ import annotations

from typing import Union

import numpy as np

from ketu.ephemeris.coordinates import mean_obliquity

from .registry import register

#: Margin used by :func:`is_polar` to trigger the polar fallback strictly
#: before the formal boundary, avoiding false-positive convergence at the
#: exact polar circle (research §Open Question 4 — "trigger fallback when
#: |s| > 1 - eps_tol").
POLAR_EPS_TOL: float = 1e-9


def polar_circle(jd: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Return the polar circle latitude (degrees) at the given Julian date.

    ``polar_circle = 90° − mean_obliquity(jd)``.

    At J2000 ε ≈ 23.4393° → polar_circle ≈ 66.5607°. The obliquity drifts
    ~50″ per century (Pitfall 4 from 10-RESEARCH.md); using the time-varying
    value is what keeps the polar boundary correct over centuries.

    Vectorised via :func:`ketu.ephemeris.coordinates.mean_obliquity`.

    Parameters
    ----------
    jd : float or np.ndarray
        Julian Date, UT.

    Returns
    -------
    float or np.ndarray
        Polar-circle latitude (degrees). Same shape as ``jd``.
    """
    return 90.0 - mean_obliquity(jd)


def is_polar(
    lat: Union[float, np.ndarray],
    jd: Union[float, np.ndarray],
) -> Union[bool, np.ndarray]:
    """
    Return ``True`` where ``|lat| > polar_circle(jd) − POLAR_EPS_TOL``.

    Used by the public ``calculate_houses`` (Plan 10-06) to route polar
    elements to either :class:`HighLatitudeError` or
    :func:`porphyry_cusps` based on the ``polar_fallback`` parameter
    (HOU-06).

    Parameters
    ----------
    lat : float or np.ndarray
        Geographic latitude (degrees), broadcast-compatible with ``jd``.
    jd : float or np.ndarray
        Julian Date, UT.

    Returns
    -------
    bool or np.ndarray
        ``True`` for elements above the polar circle. Returns a Python
        ``bool`` for purely scalar input, an ``np.ndarray`` of bool
        otherwise.

    Notes
    -----
    The boundary is computed as ``90° − mean_obliquity(jd) − POLAR_EPS_TOL``;
    do NOT hardcode 66.56° here (Pitfall 4). The ``POLAR_EPS_TOL`` margin
    avoids false-positive convergence at the formal boundary (Pitfall 6 from
    10-RESEARCH.md and Open Question 4).
    """
    boundary = polar_circle(jd)
    lat_arr = np.asarray(lat, dtype=np.float64)
    boundary_arr = np.asarray(boundary, dtype=np.float64)
    result = np.abs(lat_arr) > boundary_arr - POLAR_EPS_TOL
    if result.ndim == 0:
        return bool(result)
    return result


@register("porphyry")
def porphyry_cusps(
    armc: np.ndarray,
    lat: np.ndarray,
    eps: np.ndarray,
) -> np.ndarray:
    """
    Compute the 12 Porphyry house cusps.

    Closed-form (no iteration). Works at all latitudes including 89° —
    Porphyry is the polar fallback path for Placidus and Koch.

    Parameters
    ----------
    armc : np.ndarray
        Right Ascension of Medium Coeli (degrees), broadcast-compatible.
    lat : np.ndarray
        Geographic latitude (degrees).
    eps : np.ndarray
        Mean obliquity of the ecliptic (degrees).

    Returns
    -------
    np.ndarray
        Array of shape ``(..., 12)``: 12 house cusps in ecliptic longitude
        (degrees, ``[0, 360)``). Cusp ordering is 1-indexed at element 0:
        ``[asc, c2, c3, ic, c5, c6, desc, c8, c9, mc, c11, c12]``.

    Notes
    -----
    At exactly ``lat = 90°`` the ASC formula diverges (``tan(lat)`` → inf).
    In practice :func:`is_polar` triggers the polar fallback for
    ``|lat| > polar_circle(jd)`` long before that limit, so this corner is
    not reached during normal calculate_houses dispatch.
    """
    armc_b, lat_b, eps_b = np.broadcast_arrays(armc, lat, eps)
    armc_rad = np.deg2rad(armc_b)
    eps_rad = np.deg2rad(eps_b)
    lat_rad = np.deg2rad(lat_b)

    # ASC and MC closed-form (same as ketu.houses.ascmc.compute_ascmc,
    # inlined here so porphyry remains self-contained — Porphyry is the
    # polar fallback and must work even when the standard ascmc machinery
    # might NaN.
    mc = np.rad2deg(np.arctan2(
        np.sin(armc_rad),
        np.cos(armc_rad) * np.cos(eps_rad),
    )) % 360.0
    asc = np.rad2deg(np.arctan2(
        np.cos(armc_rad),
        -(np.sin(eps_rad) * np.tan(lat_rad)
          + np.cos(eps_rad) * np.sin(armc_rad)),
    )) % 360.0

    # Polar ASC swap: at high latitudes the closed-form ASC may emerge in
    # the "wrong" quadrant relative to MC (ASC behind MC by short-arc
    # signed difference < 0). Swisseph's Porphyry path swaps ASC by 180°
    # in that case (``swehouse.c`` case ``'O'``). Mirror that so polar
    # Porphyry agrees with the oracle even when ``compute_ascmc`` returns
    # the "antiASC" branch.
    acmc_signed = ((asc - mc + 540.0) % 360.0) - 180.0  # short-arc signed (-180, +180]
    swap_mask = acmc_signed < 0.0
    asc = np.where(swap_mask, (asc + 180.0) % 360.0, asc)
    acmc = np.where(swap_mask, acmc_signed + 180.0, acmc_signed)

    ic = (mc + 180.0) % 360.0
    desc = (asc + 180.0) % 360.0

    # Upper trisection: from MC eastward to ASC over the (now positive)
    # short arc ``acmc``.
    upper_step = acmc / 3.0

    # Lower trisection: from ASC eastward to IC; since ``ic = mc + 180``
    # and ``asc = mc + acmc``, the IC-eastward arc from ASC is
    # ``(180 - acmc) mod 360``. At ``acmc <= 180`` this is just
    # ``180 - acmc``.
    lower_step = (180.0 - acmc) / 3.0

    cusp_11 = (mc + upper_step) % 360.0
    cusp_12 = (mc + 2.0 * upper_step) % 360.0
    cusp_2 = (asc + lower_step) % 360.0
    cusp_3 = (asc + 2.0 * lower_step) % 360.0

    # Cusps 5, 6, 8, 9 are opposites by construction.
    cusp_5 = (cusp_11 + 180.0) % 360.0
    cusp_6 = (cusp_12 + 180.0) % 360.0
    cusp_8 = (cusp_2 + 180.0) % 360.0
    cusp_9 = (cusp_3 + 180.0) % 360.0

    result: np.ndarray = np.stack([
        asc, cusp_2, cusp_3, ic,
        cusp_5, cusp_6, desc, cusp_8,
        cusp_9, mc, cusp_11, cusp_12,
    ], axis=-1)
    return result
