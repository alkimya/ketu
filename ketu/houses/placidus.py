"""Placidus house system implementation.

Vectorized over ``(armc, lat, eps)`` arrays of any compatible broadcast
shape. Per-cusp iteration uses mask-based continuation: elements that
converge early are frozen so they don't pollute the iteration of others
(HOU-08 anti-pattern: never wrap scalar Placidus in a Python ``for jd in
jds:`` loop).

Iteration cap: 50 (HOU-03). Non-convergence yields ``NaN`` for the affected
cusp, surfacing the failure rather than returning a silent wrong value.
The polar boundary ``|tan(lat) * tan(decl)| >= 1`` is detected via
:func:`ketu.houses._ecliptic.ascensional_difference` returning ``NaN`` and
that ``NaN`` is propagated through the iteration to the output cusps. The
caller (``calculate_houses`` in Plan 10-06) inspects ``NaN`` cusps and
routes them to ``HighLatitudeError`` or polar fallback per HOU-06.

Algorithm (per-cusp fixed point on right ascension):

1. Initial guess: ``RA_0 = formula(armc, AD=0)`` (flat-horizon limit).
2. From ``RA_k`` derive ``decl_k = arctan(sin(RA_k) * tan(eps))``.
3. ``AD_k = arcsin(tan(lat) * tan(decl_k))`` — ``NaN`` at polar boundary.
4. ``RA_{k+1} = formula(armc, AD_k)``.
5. Stop when ``|delta(RA_{k+1}, RA_k)| < TOL_DEG`` using the modular
   metric ``abs(((RA_new - RA + 180) % 360) - 180)`` (Pitfall 3: the
   plain difference fails near the 0°/360° wrap).

Per-cusp scaling table (research §"Don't Hand-Roll" → Placidus formula):

- House 11: ``RA_11 = ARMC + (90 + AD) / 3``
- House 12: ``RA_12 = ARMC + 2 * (90 + AD) / 3``
- House  2: ``RA_2  = ARMC + 180 - 2 * (90 - AD) / 3``
- House  3: ``RA_3  = ARMC + 180 -     (90 - AD) / 3``

Cusps 5, 6, 8, 9 are exact 180° opposites of cusps 11, 12, 2, 3. Cusps
1, 4, 7, 10 are closed-form (ASC, IC = MC + 180, DESC = ASC + 180, MC)
and are never iterated.

References
----------
- 10-RESEARCH.md §"Don't Hand-Roll → Placidus formula" — canonical
  per-cusp equations, convergence threshold (1e-7°), iteration cap
  guidance, and Pitfall 6 (polar saturation) discussion.
- pd-swisseph ``swehouse.c`` — cross-checked RA→λ projection form.
- HOU-03 spec: iter cap = 50, explicit non-convergence detection.
- HOU-08 spec: vectorized over batches via mask-based continuation.
"""
from __future__ import annotations

from typing import Tuple

import numpy as np

from ._ecliptic import ascensional_difference
from .registry import register

#: Maximum number of fixed-point iterations per cusp (HOU-03).
#:
#: Most charts converge in well under 10 iterations; the 50 cap is a
#: safety margin for ARMC/lat combinations close to the polar boundary
#: where convergence is slow but not impossible. Inflating this cap to
#: "make hard cases work" hides bugs — the correct response to
#: non-convergence at iter=50 is to investigate, not to bump the cap.
MAX_ITER: int = 50

#: Convergence threshold in degrees (research §"Don't Hand-Roll").
#:
#: 1e-7° ≈ 0.36 marcsec — well below the HOU-01 / HOU-09 1-arcmin
#: agreement spec, so any solution within ``TOL_DEG`` is more than
#: precise enough at the user-facing tolerance.
TOL_DEG: float = 1e-7


# ---------------------------------------------------------------------------
# Per-cusp RA formulas (research §"Don't Hand-Roll" → Placidus formula)
# ---------------------------------------------------------------------------
#
# Each formula maps (armc, AD) -> RA in degrees, where AD is the ascensional
# difference at the current iterate's declination. AD itself is computed
# iteratively via _iterate_cusp_ra below.


def _ra_formula_cusp_11(armc: np.ndarray, AD: np.ndarray) -> np.ndarray:
    return (armc + (90.0 + AD) / 3.0) % 360.0


def _ra_formula_cusp_12(armc: np.ndarray, AD: np.ndarray) -> np.ndarray:
    return (armc + 2.0 * (90.0 + AD) / 3.0) % 360.0


def _ra_formula_cusp_2(armc: np.ndarray, AD: np.ndarray) -> np.ndarray:
    return (armc + 180.0 - 2.0 * (90.0 - AD) / 3.0) % 360.0


def _ra_formula_cusp_3(armc: np.ndarray, AD: np.ndarray) -> np.ndarray:
    return (armc + 180.0 - (90.0 - AD) / 3.0) % 360.0


#: Dispatch table: cusp number -> RA formula. Data-driven dispatch avoids the
#: if-elif ladder anti-pattern (research §Anti-Pattern 1).
_CUSP_FORMULAS: dict[int, "_RAFormula"] = {
    11: _ra_formula_cusp_11,
    12: _ra_formula_cusp_12,
    2:  _ra_formula_cusp_2,
    3:  _ra_formula_cusp_3,
}


# Type alias for the per-cusp formula callable shape (mypy-strict compatible).
from typing import Callable

_RAFormula = Callable[[np.ndarray, np.ndarray], np.ndarray]


def _iterate_cusp_ra(
    armc: np.ndarray,
    lat: np.ndarray,
    eps: np.ndarray,
    cusp_number: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """Solve for the right ascension of a Placidus iterated cusp.

    Mask-based fixed-point iteration: at each step, only elements that
    have not yet converged AND have non-``NaN`` RA are updated. Elements
    that hit the polar boundary (``|tan(lat) * tan(decl)| >= 1``) yield
    ``NaN`` from :func:`ascensional_difference`; that ``NaN`` is frozen
    into ``RA`` so it propagates to the output and signals "this element
    has no Placidus cusp at this lat / ARMC / eps".

    Parameters
    ----------
    armc : np.ndarray
        Right Ascension of the Medium Coeli, degrees.
    lat : np.ndarray
        Geographic latitude, degrees.
    eps : np.ndarray
        Mean (or true) obliquity of the ecliptic, degrees.
    cusp_number : int
        One of ``{11, 12, 2, 3}``. The other Placidus cusps are derived
        (1/4/7/10 closed-form; 5/6/8/9 opposites).

    Returns
    -------
    ra : np.ndarray
        Right ascension of the cusp, degrees, ``[0, 360)``. ``NaN`` where
        the iteration did not converge or the polar boundary was hit.
    converged : np.ndarray
        Boolean mask, ``True`` where convergence was achieved (``NaN``
        elements have ``converged == False`` so callers can distinguish
        the two failure modes).
    """
    formula = _CUSP_FORMULAS[cusp_number]

    # Broadcast inputs to a common shape so element-wise masks line up.
    armc_b, lat_b, eps_b = np.broadcast_arrays(armc, lat, eps)

    # Initial guess: AD = 0 (flat-horizon limit). Same shape as the broadcast.
    AD_init = np.zeros_like(armc_b, dtype=np.float64)
    RA: np.ndarray = formula(armc_b.astype(np.float64), AD_init)

    converged = np.zeros(RA.shape, dtype=bool)

    for _ in range(MAX_ITER):
        active = ~converged & ~np.isnan(RA)
        if not active.any():
            break

        # Step 2: declination from RA on the ecliptic.
        # tan(decl) = sin(RA) * tan(eps). decl is in [-pi/2, +pi/2] by
        # definition of declination, so single-arg arctan IS the correct
        # inverse here (Pitfall 2 applies to RA / longitude — angles that
        # span the full circle — not to declination).
        sin_RA = np.sin(np.deg2rad(RA))
        tan_eps = np.tan(np.deg2rad(eps_b))
        decl = np.rad2deg(np.arctan(sin_RA * tan_eps))

        # Step 3: ascensional difference (NaN at polar boundary, Pitfall 6).
        AD = ascensional_difference(lat_b, decl)

        # Step 4: candidate next RA.
        RA_new = formula(armc_b.astype(np.float64), AD)

        # Step 5: convergence check via modular distance (Pitfall 3).
        delta = np.abs(((RA_new - RA + 180.0) % 360.0) - 180.0)

        # Newly converged this iteration (active, non-NaN, within tolerance).
        newly = active & ~np.isnan(RA_new) & (delta < TOL_DEG)

        # Update RA only on still-active, non-NaN-RA_new elements.
        RA = np.where(active & ~np.isnan(RA_new), RA_new, RA)
        # Polar-NaN propagation: if RA_new is NaN, freeze RA at NaN.
        RA = np.where(active & np.isnan(RA_new), np.nan, RA)

        converged = converged | newly

    # Mark elements that hit MAX_ITER without converging (and weren't already
    # NaN-frozen) as NaN — this surfaces the rare "healthy lat but didn't
    # converge in 50 iter" case as a real bug signal rather than silently
    # returning the last iterate.
    not_done = ~converged & ~np.isnan(RA)
    RA = np.where(not_done, np.nan, RA)

    final_ra: np.ndarray = np.where(np.isnan(RA), np.nan, RA % 360.0)
    return final_ra, converged & ~np.isnan(final_ra)


def _ra_to_lambda_placidus(ra: np.ndarray, eps: np.ndarray) -> np.ndarray:
    """Convert RA of a Placidus cusp to ecliptic longitude.

    A Placidus cusp lies on the ecliptic by construction (we trisect the
    diurnal semi-arc on the ecliptic). For an ecliptic-resident point
    (``β = 0``) the standard transformation is

    ``tan(λ) = sin(RA) / (cos(RA) · cos(ε))``

    evaluated quadrant-safely via :func:`numpy.arctan2` as

    ``λ = atan2(sin(RA), cos(RA) · cos(ε))``.

    This is the inverse of :func:`ketu.houses._ecliptic.lambda_to_ra` and
    matches :func:`ketu.houses._ecliptic.ra_to_lambda`. It is **not** the
    Placidus-MC closed form (that one is identical, but applied to ARMC
    rather than to the per-cusp iterated RA — see
    :func:`ketu.houses.ascmc.compute_ascmc`).

    Quadrant disambiguation: :func:`numpy.arctan2` returns a result in
    ``[-180°, +180°)``; we wrap to ``[0°, 360°)`` and then flip to the
    correct hemisphere if the result falls more than ±90° away from
    ``RA``. This handles the case where ``arctan2`` selects the
    back-hemisphere root (e.g. a cusp at λ ≈ 332° has RA ≈ 334°; raw
    ``arctan2`` may return ≈ 152° when the negative-cosine branch is hit).

    Parameters
    ----------
    ra : np.ndarray
        Right ascension of the cusp, degrees. ``NaN`` propagates through.
    eps : np.ndarray
        Obliquity, degrees, broadcast-compatible with ``ra``.

    Returns
    -------
    np.ndarray
        Ecliptic longitude in degrees, ``[0, 360)``; ``NaN`` where ``ra``
        is ``NaN``.
    """
    ra_rad = np.deg2rad(ra)
    eps_rad = np.deg2rad(eps)
    lam = np.arctan2(
        np.sin(ra_rad),
        np.cos(ra_rad) * np.cos(eps_rad),
    )
    lam_deg = np.rad2deg(lam) % 360.0
    ra_norm = ra % 360.0

    # Quadrant flip if the picked root is in the back hemisphere.
    delta = (lam_deg - ra_norm + 180.0) % 360.0 - 180.0
    flip = np.abs(delta) > 90.0
    lam_deg = np.where(flip, (lam_deg + 180.0) % 360.0, lam_deg)
    result: np.ndarray = lam_deg
    return result


@register("placidus")
def placidus_cusps(
    armc: np.ndarray,
    lat: np.ndarray,
    eps: np.ndarray,
) -> np.ndarray:
    """Compute the 12 Placidus house cusps.

    Vectorized over ``(armc, lat, eps)`` arrays of any compatible broadcast
    shape. The output's leading dimensions equal the broadcast of the
    inputs; the final dimension has length 12 (cusp index ``i`` corresponds
    to house ``i + 1``).

    Parameters
    ----------
    armc : np.ndarray
        Right Ascension of the Medium Coeli, degrees.
    lat : np.ndarray
        Geographic latitude, degrees.
    eps : np.ndarray
        Mean obliquity of the ecliptic, degrees.

    Returns
    -------
    np.ndarray
        Shape ``(*broadcast_shape, 12)``. Cusps in ecliptic longitude
        (degrees, ``[0, 360)``). ``NaN`` cusps signal non-convergence or
        polar boundary; the caller (:func:`ketu.houses.calculate_houses`,
        Plan 10-06) inspects ``NaN`` cusps and routes them to
        :class:`HighLatitudeError` or the polar fallback per HOU-06.

    Notes
    -----
    Cusps 1, 4, 7, 10 are closed-form (ASC, IC, DESC, MC). Cusps 11, 12,
    2, 3 are iterated (mask-based fixed point on RA). Cusps 5, 6, 8, 9 are
    exact 180° opposites of 11, 12, 2, 3.

    Implementation re-derives ASC/MC inline from ``(armc, lat, eps)``
    rather than calling :func:`ketu.houses.ascmc.compute_ascmc` —
    :func:`compute_ascmc` takes ``(jd, lat, lon)`` and would re-compute
    ARMC and ε; we already have those, so re-deriving inline keeps the
    registry contract clean and avoids redundant work.
    """
    # Broadcast inputs to a common shape S.
    armc_b, lat_b, eps_b = np.broadcast_arrays(armc, lat, eps)
    armc_b = armc_b.astype(np.float64)
    lat_b = lat_b.astype(np.float64)
    eps_b = eps_b.astype(np.float64)

    armc_rad = np.deg2rad(armc_b)
    eps_rad = np.deg2rad(eps_b)
    lat_rad = np.deg2rad(lat_b)

    # ASC and MC closed-form (matches :func:`ketu.houses.ascmc.compute_ascmc`).
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

    # Iterate the 4 non-trivial cusps.
    cusp_11_RA, _ = _iterate_cusp_ra(armc_b, lat_b, eps_b, 11)
    cusp_12_RA, _ = _iterate_cusp_ra(armc_b, lat_b, eps_b, 12)
    cusp_2_RA,  _ = _iterate_cusp_ra(armc_b, lat_b, eps_b, 2)
    cusp_3_RA,  _ = _iterate_cusp_ra(armc_b, lat_b, eps_b, 3)

    # RA -> ecliptic longitude (Placidus-specific projection).
    cusp_11 = _ra_to_lambda_placidus(cusp_11_RA, eps_b)
    cusp_12 = _ra_to_lambda_placidus(cusp_12_RA, eps_b)
    cusp_2  = _ra_to_lambda_placidus(cusp_2_RA,  eps_b)
    cusp_3  = _ra_to_lambda_placidus(cusp_3_RA,  eps_b)

    # Cusps 5/6/8/9 are exact 180° opposites of 11/12/2/3.
    cusp_5 = (cusp_11 + 180.0) % 360.0
    cusp_6 = (cusp_12 + 180.0) % 360.0
    cusp_8 = (cusp_2  + 180.0) % 360.0
    cusp_9 = (cusp_3  + 180.0) % 360.0

    # Stack into output of shape (*S, 12); cusp index i = house (i+1).
    cusps: np.ndarray = np.stack([
        asc,      # house 1 = ASC
        cusp_2,
        cusp_3,
        ic,       # house 4 = IC
        cusp_5,
        cusp_6,
        desc,     # house 7 = DESC
        cusp_8,
        cusp_9,
        mc,       # house 10 = MC
        cusp_11,
        cusp_12,
    ], axis=-1)

    return cusps
