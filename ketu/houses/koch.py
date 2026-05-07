"""Koch house system implementation.

Koch's "Geburtsorthäuser" trisects the ascensional difference of the MC
on the equator, then projects each trisected angle into the ecliptic via
the same Asc1 formula used for the Ascendant. Per swisseph C source
(``swehouse.c`` case ``'K'``) and Knappich's original derivation:

    sina  = sin(MC) * sin(eps) / cos(lat)        (clipped to [-1, +1])
    cosa  = sqrt(1 - sina²)
    c     = arctan(tan(lat) / cosa)
    ad3   = arcsin(sin(c) * sina) / 3
    cusp_11 = Asc1(ARMC + 30  − 2·ad3, lat, eps)
    cusp_12 = Asc1(ARMC + 60  − ad3,    lat, eps)
    cusp_2  = Asc1(ARMC + 120 + ad3,    lat, eps)
    cusp_3  = Asc1(ARMC + 150 + 2·ad3,  lat, eps)

Where ``Asc1(x, lat, eps)`` is the ASC formula evaluated with ``x − 90``
as the equator angle: it returns the ecliptic longitude where a great
circle of pole height ``lat`` and equatorial RA ``x − 90`` crosses the
ecliptic.

Polar boundary at ``|lat| ≥ 90° − eps`` causes the formula to break (``sina``
saturates and intermediate quantities lose precision); swisseph itself
falls back to Porphyry there (``goto porphyry`` in the C source). We mirror
that: at polar latitudes, :func:`koch_cusps` returns ``NaN`` cusps so
Plan 10-06's ``calculate_houses`` can route via ``polar_fallback`` per
HOU-06.
"""
from __future__ import annotations

import numpy as np

from .registry import register

#: Iteration cap kept for API parity with Placidus tests; Koch is closed-form
#: in this implementation (no fixed-point solve), so the constant is unused
#: in the production code path. Reserved for future iterative variants.
MAX_ITER: int = 50

#: Convergence threshold (degrees) — same comment as :data:`MAX_ITER`.
TOL_DEG: float = 1e-7


def _asc1(
    x: np.ndarray,
    lat: np.ndarray,
    sin_eps: np.ndarray,
    cos_eps: np.ndarray,
) -> np.ndarray:
    """Return the ecliptic longitude crossed by a great circle.

    Mirrors swisseph's ``Asc1(x, f, sine, cose)`` (``swehouse.c`` line
    2056). For ``x = ARMC + 90`` and ``f = lat`` this collapses to the
    standard Ascendant formula::

        asc = atan2(cos(armc), -(tan(lat)·sin(eps) + cos(eps)·sin(armc)))

    Parameters
    ----------
    x : np.ndarray
        Angle (degrees) — for cusp ``k`` this is ``ARMC + offset_k``.
    lat : np.ndarray
        Geographic latitude (degrees).
    sin_eps, cos_eps : np.ndarray
        Pre-computed ``sin``/``cos`` of the obliquity (radians) — passed
        in to avoid repeating the trig inside the per-cusp loop.

    Returns
    -------
    np.ndarray
        Ecliptic longitude (degrees, ``[0, 360)``).
    """
    x_norm = x % 360.0
    x_rad = np.deg2rad(x_norm)
    lat_rad = np.deg2rad(lat)
    # The classical asc-style formula evaluated at the shifted argument:
    #   tan(λ) = sin(x − 90 + 90) / (−tan(lat)·sin(eps) + cos(eps)·cos(x − 90 + 90))
    # which equals
    #   tan(λ) = cos(x − 90) / (−tan(lat)·sin(eps) − cos(eps)·sin(x − 90))
    # Using x directly (without the −90 shift) corresponds to evaluating Asc1
    # whose argument is ``ARMC + offset`` — when offset=90 we get the ASC.
    # Swisseph's Asc1(x) implements the same identity via a quadrant-folded
    # recursion using Asc2; the ``arctan2`` below is the closed-form
    # equivalent.
    num = np.cos(x_rad - np.pi / 2.0)
    den = -(np.tan(lat_rad) * sin_eps + cos_eps * np.sin(x_rad - np.pi / 2.0))
    lam = np.arctan2(num, den)
    result: np.ndarray = np.rad2deg(lam) % 360.0
    return result


@register("koch")
def koch_cusps(
    armc: np.ndarray,
    lat: np.ndarray,
    eps: np.ndarray,
) -> np.ndarray:
    """Compute the 12 Koch house cusps.

    Closed-form per swisseph ``swehouse.c`` (case ``'K'``). At latitudes
    inside the polar circle (``|lat| ≥ 90° − eps``) the formula becomes
    degenerate; we return ``NaN`` cusps so Plan 10-06's ``calculate_houses``
    can route via ``polar_fallback`` per HOU-06.

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
        Array of shape ``(..., 12)`` with cusp ordering
        ``[asc, c2, c3, ic, c5, c6, desc, c8, c9, mc, c11, c12]``.
    """
    armc_b, lat_b, eps_b = np.broadcast_arrays(armc, lat, eps)
    armc_rad = np.deg2rad(armc_b)
    eps_rad = np.deg2rad(eps_b)
    lat_rad = np.deg2rad(lat_b)
    sin_eps = np.sin(eps_rad)
    cos_eps = np.cos(eps_rad)

    # Closed-form ASC and MC.
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

    # Polar boundary: at |lat| ≥ 90 − eps the Koch formula degenerates.
    # Mirror swisseph's behaviour (``goto porphyry`` in C source) by
    # propagating NaN — Plan 10-06 routes via polar_fallback.
    polar_mask = np.abs(lat_b) >= (90.0 - eps_b)

    # Koch's "ad3" trisection of the equator's ascensional difference.
    sina = np.sin(np.deg2rad(mc)) * sin_eps / np.cos(lat_rad)
    sina = np.clip(sina, -1.0, 1.0)
    cosa = np.sqrt(1.0 - sina * sina)
    # Guard cosa > 0 (the C source promises "always >> 0"; clip to avoid
    # divide-by-zero from numerical error in extreme cases).
    cosa = np.where(cosa > 1e-15, cosa, np.nan)
    c_rad = np.arctan(np.tan(lat_rad) / cosa)
    ad3_rad = np.arcsin(np.sin(c_rad) * sina) / 3.0
    ad3 = np.rad2deg(ad3_rad)

    # Per swisseph swehouse.c case 'K':
    cusp_11 = _asc1(armc_b + 30.0 - 2.0 * ad3, lat_b, sin_eps, cos_eps)
    cusp_12 = _asc1(armc_b + 60.0 - ad3,       lat_b, sin_eps, cos_eps)
    cusp_2  = _asc1(armc_b + 120.0 + ad3,      lat_b, sin_eps, cos_eps)
    cusp_3  = _asc1(armc_b + 150.0 + 2.0 * ad3, lat_b, sin_eps, cos_eps)

    # Cusps 5, 6, 8, 9 are opposites by construction.
    cusp_5 = (cusp_11 + 180.0) % 360.0
    cusp_6 = (cusp_12 + 180.0) % 360.0
    cusp_8 = (cusp_2 + 180.0) % 360.0
    cusp_9 = (cusp_3 + 180.0) % 360.0

    cusps = np.stack([
        asc, cusp_2, cusp_3, ic,
        cusp_5, cusp_6, desc, cusp_8,
        cusp_9, mc, cusp_11, cusp_12,
    ], axis=-1)

    # Apply polar mask: NaN out polar elements.
    if polar_mask.any():
        # Broadcast polar_mask over the trailing cusps axis.
        mask_b = np.broadcast_to(polar_mask[..., np.newaxis], cusps.shape)
        cusps = np.where(mask_b, np.nan, cusps)

    result: np.ndarray = cusps
    return result
