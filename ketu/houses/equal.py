"""Equal house system implementation (ASC-anchored).

In Equal house, each cusp is exactly 30° east of the previous, starting
from the Ascendant. This is the simplest possible house system — used as
a teaching system and occasionally for natal charts where the user wants
sign-aligned spacing without the sign-floor.

Per swisseph C source (``swehouse.c`` case ``'E'``):

    cusp_k = (asc + 30 * (k - 1)) mod 360   # k = 1..12

The function is mathematically defined at all latitudes (it depends only
on the Ascendant). Polar-safe by construction — no NaN propagation.

Notes
-----
Caveat — ``cusps[9]`` is NOT the astronomical MC:
For Placidus / Koch / Porphyry / Regiomontanus, ``cusps[9] == mc`` (the
astronomical Medium Coeli, computed via :func:`compute_ascmc`). For
Equal house, ``cusps[9] = (asc + 270) mod 360``, which only coincides
with the astronomical MC at the equator (where ASC and MC are
exactly 90° apart). At any other latitude, ``cusps[9]`` and ``out["mc"]``
diverge by up to ~10° (mid-latitudes) or more (near polar). This is
intentional — HOU2-02 specifies ASC-anchored Equal, not MC-anchored
Equal (swisseph case ``'D'``, deferred to v1.3).

Callers needing the astronomical MC must read ``out["mc"]``, NOT
``out["cusps"][9]``. This divergence is verified by
``tests/houses/test_equal.py``
(``test_equal_cusp_10_is_asc_plus_270_not_astronomical_mc``).
"""
from __future__ import annotations

import numpy as np

from .registry import register


@register("equal")
def equal_cusps(
    armc: np.ndarray,
    lat: np.ndarray,
    eps: np.ndarray,
) -> np.ndarray:
    """Compute the 12 Equal house cusps (ASC-anchored).

    Closed-form per swisseph ``swehouse.c`` case ``'E'``. Polar-safe.

    Parameters
    ----------
    armc : np.ndarray
        Right Ascension of Medium Coeli (degrees), broadcast-compatible
        with ``lat`` and ``eps``.
    lat : np.ndarray
        Geographic latitude (degrees). Used only to compute the ASC.
    eps : np.ndarray
        Mean obliquity of the ecliptic (degrees). Used only to compute
        the ASC.

    Returns
    -------
    np.ndarray
        Array of shape ``(..., 12)``: ``cusps[k] = (asc + 30k) mod 360``.
        ``cusps[0] == asc`` (consistent with Placidus/Koch/Porphyry);
        ``cusps[9]`` is ``(asc + 270) mod 360``, which generally diverges
        from the astronomical MC stored in ``out["mc"]`` (see module
        docstring).
    """
    armc_b, lat_b, eps_b = np.broadcast_arrays(armc, lat, eps)
    armc_rad = np.deg2rad(armc_b)
    eps_rad = np.deg2rad(eps_b)
    lat_rad = np.deg2rad(lat_b)

    # ASC closed-form (mirror porphyry.py:147-151).
    asc = np.rad2deg(np.arctan2(
        np.cos(armc_rad),
        -(np.sin(eps_rad) * np.tan(lat_rad)
          + np.cos(eps_rad) * np.sin(armc_rad)),
    )) % 360.0

    # Polar ASC swap (mirror porphyry.py:153-162). The MC computed here
    # is used ONLY to determine the swap; it is NOT stacked into the
    # output (Equal cusps[9] = asc+270, not the astronomical MC).
    mc = np.rad2deg(np.arctan2(
        np.sin(armc_rad),
        np.cos(armc_rad) * np.cos(eps_rad),
    )) % 360.0
    acmc_signed = ((asc - mc + 540.0) % 360.0) - 180.0
    swap_mask = acmc_signed < 0.0
    asc = np.where(swap_mask, (asc + 180.0) % 360.0, asc)

    # Equal cusps: each 30° east of the ASC.
    offsets = np.arange(12, dtype=np.float64) * 30.0
    cusps = (asc[..., np.newaxis] + offsets) % 360.0

    result: np.ndarray = cusps
    return result
