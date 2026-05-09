"""Whole Sign house system implementation.

In Whole Sign, each of the 12 houses corresponds to a complete zodiacal
sign of 30 degrees. House 1 begins at the **start of the sign containing
the Ascendant** — NOT at the Ascendant itself. This is the oldest
historical Western system (Hellenistic and Vedic traditions).

Per swisseph C source (``swehouse.c`` case ``'W'``):

    cusp_1 = floor(asc / 30) * 30        # start of rising sign
    cusp_k = (cusp_1 + 30 * (k - 1)) mod 360   # k = 2..12

The function is mathematically defined at all latitudes (it depends only
on the Ascendant, which is closed-form via :func:`compute_ascmc` for
``|lat| < 90°``). Polar-safe by construction — no NaN propagation, no
``HighLatitudeError`` path.

Notes
-----
Caveat — ``cusps[0]`` divergence:
For Placidus / Koch / Porphyry / Equal / Regiomontanus, ``cusps[0] == asc``.
For Whole Sign, ``cusps[0]`` is the start of the sign (Aries 0° if asc in
[0°, 30°), Taurus 0° if asc in [30°, 60°), etc.). The actual Ascendant is
preserved in ``out["asc"]`` (set by :func:`calculate_houses` via
:func:`compute_ascmc`). Callers needing the rising longitude must read
``out["asc"]``, NOT ``out["cusps"][0]``.

This divergence is verified by ``tests/houses/test_whole_sign.py``
(``test_whole_sign_cusp_1_is_start_of_rising_sign``).
"""
from __future__ import annotations

import numpy as np

from .registry import register


@register("whole_sign")
def whole_sign_cusps(
    armc: np.ndarray,
    lat: np.ndarray,
    eps: np.ndarray,
) -> np.ndarray:
    """Compute the 12 Whole Sign house cusps.

    Closed-form per swisseph ``swehouse.c`` case ``'W'``. Polar-safe by
    construction (no latitude-dependent singularity).

    Parameters
    ----------
    armc : np.ndarray
        Right Ascension of Medium Coeli (degrees), broadcast-compatible
        with ``lat`` and ``eps``.
    lat : np.ndarray
        Geographic latitude (degrees). Used only to compute the ASC; the
        sign-floor itself does not depend on latitude.
    eps : np.ndarray
        Mean obliquity of the ecliptic (degrees). Used only to compute
        the ASC and MC.

    Returns
    -------
    np.ndarray
        Array of shape ``(..., 12)`` with cusp ordering
        ``[cusp_1, cusp_2, ..., cusp_12]`` where ``cusp_1`` is the start
        of the sign containing the ASC (NOT the ASC itself; see module
        docstring). Indices 3, 6, 9 hold cusps 4 (IC equivalent), 7
        (DESC equivalent), and 10 (MC equivalent) by sign-floor symmetry,
        which generally diverge from the astronomical IC/DESC/MC.

    Notes
    -----
    The standard cusp ordering convention used elsewhere in
    ``ketu.houses`` (``[asc, c2, c3, ic, c5, c6, desc, c8, c9, mc, c11,
    c12]``) is preserved by index but loses its "asc/ic/desc/mc"
    interpretation: for Whole Sign these slots hold the sign-floor
    cusps, not the astronomical angles. Use ``out["asc"]``, ``out["mc"]``
    for the true ASC/MC.
    """
    armc_b, lat_b, eps_b = np.broadcast_arrays(armc, lat, eps)
    armc_rad = np.deg2rad(armc_b)
    eps_rad = np.deg2rad(eps_b)
    lat_rad = np.deg2rad(lat_b)

    # ASC closed-form (mirror porphyry.py:147-151). We need the ASC to
    # determine the rising sign; we discard MC since Whole Sign cusps
    # 4/7/10 are sign-floor opposites, not the astronomical IC/DESC/MC.
    asc = np.rad2deg(np.arctan2(
        np.cos(armc_rad),
        -(np.sin(eps_rad) * np.tan(lat_rad)
          + np.cos(eps_rad) * np.sin(armc_rad)),
    )) % 360.0

    # Polar ASC swap (mirror porphyry.py:153-162) — at high latitudes the
    # closed-form ASC may emerge in the antipodal quadrant; swisseph case
    # 'W' applies the same swap as case 'O' (Porphyry) before the
    # sign-floor. Pitfall 1 from 15-RESEARCH §11: do the swap BEFORE the
    # floor, not after.
    mc = np.rad2deg(np.arctan2(
        np.sin(armc_rad),
        np.cos(armc_rad) * np.cos(eps_rad),
    )) % 360.0
    acmc_signed = ((asc - mc + 540.0) % 360.0) - 180.0
    swap_mask = acmc_signed < 0.0
    asc = np.where(swap_mask, (asc + 180.0) % 360.0, asc)

    # Sign-floor: cusp_1 = start of the 30° sign containing ASC.
    cusp_1 = np.floor(asc / 30.0) * 30.0

    # Cusps 2..12: each 30° east of the previous one.
    # Build (..., 12) by adding [0, 30, 60, ..., 330] to cusp_1.
    offsets = np.arange(12, dtype=np.float64) * 30.0
    cusps = (cusp_1[..., np.newaxis] + offsets) % 360.0

    result: np.ndarray = cusps
    return result
