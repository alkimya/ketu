"""Internal helpers shared by house-system implementations.

Provides RA <-> ecliptic-longitude conversions used by Placidus
(Plan 10-04) and Koch (Plan 10-05). All angles in degrees; all functions
vectorized via NumPy ufuncs.

The leading underscore in the module name signals "internal API"; consumers
should import from :mod:`ketu.houses` (public surface), not from here.
"""
from __future__ import annotations

import numpy as np


def ra_to_lambda(ra: np.ndarray, eps: np.ndarray) -> np.ndarray:
    """Convert right ascension on the ecliptic to ecliptic longitude.

    For a point on the ecliptic (declination = 0) with right ascension
    ``ra``, compute its ecliptic longitude ``lam`` via the closed-form
    quadrant-safe identity ``tan(lam) = tan(ra) / cos(eps)`` evaluated
    through :func:`numpy.arctan2`.

    Parameters
    ----------
    ra : np.ndarray
        Right ascension, degrees, broadcast-compatible with ``eps``.
    eps : np.ndarray
        Mean obliquity of the ecliptic, degrees.

    Returns
    -------
    np.ndarray
        Ecliptic longitude in degrees, normalized to ``[0, 360)``.

    Notes
    -----
    Strictly valid for points on the ecliptic (declination = 0). For
    off-ecliptic points used by Placidus intermediate-cusp formulas
    (Plan 10-04), the more general formula
    ``atan2(sin(ra), cos(ra)*cos(eps) - sin(decl)*sin(eps))`` should be
    used; we keep this simpler form as a building block.
    """
    ra_rad = np.deg2rad(ra)
    eps_rad = np.deg2rad(eps)
    lam = np.arctan2(np.sin(ra_rad), np.cos(ra_rad) * np.cos(eps_rad))
    result: np.ndarray = np.rad2deg(lam) % 360.0
    return result


def lambda_to_ra(lam: np.ndarray, eps: np.ndarray) -> np.ndarray:
    """Convert ecliptic longitude to right ascension on the ecliptic.

    Inverse of :func:`ra_to_lambda` for points on the ecliptic. Uses
    ``tan(ra) = tan(lam) * cos(eps)`` evaluated through
    :func:`numpy.arctan2` for quadrant correctness.

    Parameters
    ----------
    lam : np.ndarray
        Ecliptic longitude, degrees, broadcast-compatible with ``eps``.
    eps : np.ndarray
        Mean obliquity of the ecliptic, degrees.

    Returns
    -------
    np.ndarray
        Right ascension in degrees, normalized to ``[0, 360)``.
    """
    lam_rad = np.deg2rad(lam)
    eps_rad = np.deg2rad(eps)
    ra = np.arctan2(np.sin(lam_rad) * np.cos(eps_rad), np.cos(lam_rad))
    result: np.ndarray = np.rad2deg(ra) % 360.0
    return result


def ascensional_difference(lat: np.ndarray, decl: np.ndarray) -> np.ndarray:
    """Compute the ascensional difference ``AD = arcsin(tan(lat) * tan(decl))``.

    Returns ``NaN`` where ``|tan(lat) * tan(decl)| >= 1`` — i.e. where the
    cusp does not exist (polar boundary; see Pitfall 6 in 10-RESEARCH.md).
    Caller is responsible for routing ``NaN`` to the polar-fallback path
    (Porphyry, per Plan 10-05).

    Parameters
    ----------
    lat : np.ndarray
        Geographic latitude, degrees, broadcast-compatible with ``decl``.
    decl : np.ndarray
        Declination, degrees.

    Returns
    -------
    np.ndarray
        Ascensional difference in degrees, ``NaN`` where the formula does
        not exist.
    """
    s = np.tan(np.deg2rad(lat)) * np.tan(np.deg2rad(decl))
    s_safe = np.where(np.abs(s) < 1.0, s, np.nan)
    result: np.ndarray = np.rad2deg(np.arcsin(s_safe))
    return result
