"""Regiomontanus house system implementation.

Regiomontanus divides the celestial equator into 12 equal 30° arcs, then
projects each arc into the ecliptic via great circles passing through the
north and south points of the local horizon (the prime vertical). The
result: each cusp is the ecliptic longitude where a specific great circle
crosses the ecliptic.

Per swisseph C source (``swehouse.c`` case ``'R'``):

    fh1 = atan(tan(lat) / 2)             # pole height for cusps 11/3
    fh2 = atan(tan(lat) * cos(30°))      # pole height for cusps 12/2

    cusp_11 = Asc1(ARMC + 30°,  fh1, sin_eps, cos_eps)
    cusp_12 = Asc1(ARMC + 60°,  fh2, sin_eps, cos_eps)
    cusp_2  = Asc1(ARMC + 120°, fh2, sin_eps, cos_eps)
    cusp_3  = Asc1(ARMC + 150°, fh1, sin_eps, cos_eps)

    cusps 5/6/8/9 = opposites of 11/12/2/3 (180°)
    cusps 1/4/7/10 = ASC, IC, DESC, MC (closed-form via arctan2)

Polar boundary at ``|lat| ≥ 90° − eps``: ``tan(lat)`` diverges,
``fh1``/``fh2`` lose precision, the formula breaks. We mirror Koch's
NaN propagation strategy: at polar latitudes, return ``NaN`` cusps so
:func:`ketu.houses.calculate_houses` can route via ``polar_fallback``
per HOU-06 (D-02 in 15-CONTEXT.md). NO swisseph-style MC↔IC swap (which
would be a digression from the v1.1 polar contract).

Notes
-----
Pitfall — pole height vs geographic latitude. The shared
:func:`_asc1` helper takes a parameter named ``lat`` for historical
reasons (Koch passes the geographic latitude there). For Regiomontanus,
the parameter is the great-circle **pole height**:
``fh1 = atan(tan(geo_lat) / 2)`` for cusps 11 and 3, and
``fh2 = atan(tan(geo_lat) * cos(30°))`` for cusps 12 and 2. Passing
``geo_lat`` instead would produce a uniform ~10° drift on all four
non-trivial cusps (Pitfall 4 from 15-RESEARCH §11). We name the
intermediate variables ``pole_height_outer`` and ``pole_height_inner``
to make the distinction visually obvious.
"""
from __future__ import annotations

import numpy as np

from ._ecliptic import _asc1
from .registry import register

#: Iteration cap kept for API parity with Placidus tests; Regiomontanus
#: is closed-form (no fixed-point solve), so the constant is unused in
#: the production code path. Reserved for future iterative variants.
MAX_ITER: int = 50

#: Convergence threshold (degrees) — same comment as :data:`MAX_ITER`.
TOL_DEG: float = 1e-7


@register("regiomontanus")
def regiomontanus_cusps(
    armc: np.ndarray,
    lat: np.ndarray,
    eps: np.ndarray,
) -> np.ndarray:
    """Compute the 12 Regiomontanus house cusps.

    Closed-form per swisseph ``swehouse.c`` case ``'R'``. At latitudes
    inside the polar circle (``|lat| ≥ 90° − eps``) the formula becomes
    degenerate; we return ``NaN`` cusps so
    :func:`ketu.houses.calculate_houses` can route via ``polar_fallback``
    per HOU-06.

    Parameters
    ----------
    armc : np.ndarray
        Right Ascension of Medium Coeli (degrees), broadcast-compatible
        with ``lat`` and ``eps``.
    lat : np.ndarray
        Geographic latitude (degrees).
    eps : np.ndarray
        Mean obliquity of the ecliptic (degrees).

    Returns
    -------
    np.ndarray
        Array of shape ``(..., 12)`` with cusp ordering
        ``[asc, c2, c3, ic, c5, c6, desc, c8, c9, mc, c11, c12]``. NaN
        elements where ``|lat| ≥ 90° − eps``.

    Notes
    -----
    The pole heights ``fh1`` and ``fh2`` are intermediate quantities,
    NOT geographic latitudes — see module docstring (Pitfall 4).
    """
    armc_b, lat_b, eps_b = np.broadcast_arrays(armc, lat, eps)
    armc_rad = np.deg2rad(armc_b)
    eps_rad = np.deg2rad(eps_b)
    lat_rad = np.deg2rad(lat_b)
    sin_eps = np.sin(eps_rad)
    cos_eps = np.cos(eps_rad)

    # Closed-form ASC and MC (mirror koch.py:81-91).
    mc = np.rad2deg(np.arctan2(
        np.sin(armc_rad),
        np.cos(armc_rad) * np.cos(eps_rad),
    )) % 360.0
    asc = np.rad2deg(np.arctan2(
        np.cos(armc_rad),
        -(np.sin(eps_rad) * np.tan(lat_rad)
          + np.cos(eps_rad) * np.sin(armc_rad)),
    )) % 360.0
    ic = (mc + 180.0) % 360.0
    desc = (asc + 180.0) % 360.0

    # Polar boundary: at |lat| ≥ 90 − eps the Regiomontanus formula
    # degenerates (tan(lat) diverges, fh1/fh2 lose precision). Mirror
    # Koch's NaN-propagation strategy — Plan 10-06's calculate_houses
    # routes via polar_fallback (D-02 in 15-CONTEXT.md). NO MC↔IC swap.
    polar_mask = np.abs(lat_b) >= (90.0 - eps_b)

    # Pole heights for the great circles defining cusps 11/12/2/3.
    # Named explicitly to ratchet against Pitfall 4 (15-RESEARCH §11):
    # NEVER pass geographic latitude to _asc1 in this file.
    cos_30 = np.cos(np.deg2rad(30.0))  # constant ~0.866025
    pole_height_outer = np.arctan(np.tan(lat_rad) / 2.0)        # cusps 11, 3
    pole_height_inner = np.arctan(np.tan(lat_rad) * cos_30)     # cusps 12, 2
    pole_height_outer_deg = np.rad2deg(pole_height_outer)
    pole_height_inner_deg = np.rad2deg(pole_height_inner)

    # 4 non-trivial cusps via _asc1 (per swisseph swehouse.c case 'R').
    # NOTE: each call passes a POLE HEIGHT, not a geographic latitude.
    cusp_11 = _asc1(armc_b + 30.0,  pole_height_outer_deg, sin_eps, cos_eps)
    cusp_12 = _asc1(armc_b + 60.0,  pole_height_inner_deg, sin_eps, cos_eps)
    cusp_2 = _asc1(armc_b + 120.0, pole_height_inner_deg, sin_eps, cos_eps)
    cusp_3 = _asc1(armc_b + 150.0, pole_height_outer_deg, sin_eps, cos_eps)

    # Cusps 5, 6, 8, 9 are opposites by construction (mirror koch.py:116-119).
    cusp_5 = (cusp_11 + 180.0) % 360.0
    cusp_6 = (cusp_12 + 180.0) % 360.0
    cusp_8 = (cusp_2 + 180.0) % 360.0
    cusp_9 = (cusp_3 + 180.0) % 360.0

    cusps = np.stack([
        asc, cusp_2, cusp_3, ic,
        cusp_5, cusp_6, desc, cusp_8,
        cusp_9, mc, cusp_11, cusp_12,
    ], axis=-1)

    # Apply polar mask: NaN out polar elements (mirror koch.py:128-131).
    if polar_mask.any():
        mask_b = np.broadcast_to(polar_mask[..., np.newaxis], cusps.shape)
        cusps = np.where(mask_b, np.nan, cusps)

    result: np.ndarray = cusps
    return result
