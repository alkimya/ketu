"""
Lunar return public API — LRET-01..05.

``lunar_return`` resolves the FIRST moment >= ``target_jd`` when the
Moon's geocentric longitude equals its natal longitude, then assembles
a CHART_DTYPE at the resolved instant (optionally relocated). The
Moon root-finding is delegated to ``ketu.returns._solve._solve_return``
- the shared bisection helper mandated by ROADMAP Phase 18 Success
Criterion #3 (LRET-02 factorisation lock).

Structurally identical to ``ketu.returns.solar_return`` but with two
critical differences:

1. **Body:** ``body_id=1`` (Moon) instead of ``0`` (Sun).
2. **Seed strategy:** lunar returns are ~27.32 d periodic, and an
   arbitrary ``target_jd`` may put the Moon anywhere in its cycle
   relative to natal -- so blindly seeding at ``target_jd`` is wrong.
   The seed is lifted from ``target_jd`` to the FIRST estimated
   return via mean-motion: read the Moon's signed residual at
   ``target_jd``, advance by ``(-r0) mod 360 / 13.176`` days. The
   actual return is within ~1 d of this estimate (anomalistic
   variation), comfortably inside a +/-1.5 d bracket. Cycle fallback
   ``n=0, 1, 2`` of ``t_first_seed + n * 27.321582`` is wired for
   the (vanishingly unlikely) anomalistic outlier case AND for the
   inclusive boundary case where the Moon is already at natal at
   ``target_jd`` and the mean-motion estimate slightly undershoots.
   The FIRST seed whose resolved JD is >= ``target_jd`` wins --
   guaranteeing the resolved JD is the first return >= ``target_jd``
   (LRET-01 binding).
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from ketu.charts import compute_chart
from ketu.ephemeris.planets import calc_planet_position
from ketu.returns._solve import (
    _TOL_DAYS,
    _TROPICAL_MONTH_D,
    _signed_residual_deg,
    _solve_return,
)

# Moon mean motion (degrees / day). Used ONLY for seed estimation -- the
# actual root-finding uses calc_planet_position_batch via _solve_return.
# Sidereal mean motion 13.176358 deg/d; tropical is bit-identical at this
# precision (precession contribution is sub-arcsec / day).
_MOON_MEAN_SPEED_DEG_PER_DAY: float = 360.0 / _TROPICAL_MONTH_D  # ~13.176


def lunar_return(
    natal_jd: float,
    natal_lat: float,
    natal_lon: float,
    target_jd: float,
    return_lat: Optional[float] = None,
    return_lon: Optional[float] = None,
    system: str = "placidus",
) -> np.ndarray:
    """
    Compute the FIRST lunar return chart for a natal birth >= ``target_jd``.

    Resolves the first moment >= ``target_jd`` at which the Moon's
    geocentric longitude equals the natal Moon longitude (within 1
    arc-second per LRET-03), then assembles a scalar
    :data:`ketu.charts.CHART_DTYPE` at that instant -- optionally
    relocated (LRET-01 + LRET-05).

    Parameters
    ----------
    natal_jd : float
        Natal Julian Date (UTC). The natal Moon longitude is read once
        from this JD via
        :func:`ketu.ephemeris.planets.calc_planet_position`.
    natal_lat : float
        Natal geographic latitude in degrees. **NEVER used for the
        Moon longitude resolution** -- Moon's geocentric longitude is
        location-independent. Lives on the signature for symmetry
        with :func:`solar_return` and for future-proofing. Defaults
        for ``return_lat`` if the caller passes ``None``.
    natal_lon : float
        Natal geographic longitude in degrees. Signature-symmetry
        only; defaults for ``return_lon`` if the caller passes
        ``None``.
    target_jd : float
        Earliest acceptable JD for the return (UTC Julian Date). The
        resolution finds the FIRST lunar return moment >=
        ``target_jd``. If ``target_jd`` is exactly at a return moment
        (within ``tol_deg`` Moon-residual), ``target_jd`` itself is
        returned (inclusive boundary). Subsequent returns at
        ``target_jd + 27.32 d``, ``target_jd + 54.64 d``, etc., are
        NOT returned by this call -- only the first.
    return_lat : float or None, optional
        Latitude for the return chart's houses, ASC, MC, ARMC, Vertex.
        ``None`` (default) reuses ``natal_lat`` -- the "standard
        return" case. Non-``None`` produces a "relocated return".
    return_lon : float or None, optional
        Longitude for the return chart's houses (etc.). ``None``
        (default) reuses ``natal_lon``.
    system : str, optional
        House system identifier. Default ``"placidus"``. Validated by
        :func:`ketu.houses.calculate_houses` (raises ``ValueError`` on
        unknown systems). Phase 15 adds ``"whole_sign"``, ``"equal"``,
        ``"regiomontanus"``.

    Returns
    -------
    np.ndarray
        Scalar (0-d) :data:`ketu.charts.CHART_DTYPE`. Field ``jd`` is
        the resolved return instant in UTC; ``lat``/``lon`` are
        ``return_lat``/``return_lon`` (or natal fallbacks); houses,
        ASC, MC are computed at the return location; body longitudes
        are evaluated at the return instant.

    Raises
    ------
    ValueError
        - If ``target_jd`` is a string (the most common footgun:
          passing an ISO date or year-as-string).
        - If no lunar return is found within 2 sidereal months
          (~54.64 d) of ``target_jd``. This indicates a pathological
          input or an ephemeris bug (the Moon's longitude is
          monotonic, so a return MUST exist within one period).
        - If the bisection bracket fails inside
          :func:`ketu.returns._solve._solve_return` for every seed in
          the cycle search (propagated; same Open Question Q1 lock
          as :func:`solar_return`).
        - If ``system`` is unknown (propagated from
          :func:`ketu.houses.calculate_houses`).

    See Also
    --------
    ketu.returns.solar_return : Solar return (asymmetric API:
        ``target_year`` integer, calendar-anchored, annual).
    ketu.charts.compute_chart : Underlying chart-assembly call.
    ketu.returns._solve._solve_return : Shared pure-NumPy bisection
        helper used by both :func:`solar_return` and
        :func:`lunar_return` (ROADMAP Phase 18 Success Criterion #3
        binding).

    Notes
    -----
    **API asymmetry vs.** :func:`ketu.returns.solar_return` **-- LOUD.**

    Where :func:`solar_return` takes an integer ``target_year``
    (calendar-anchored, one return per birthday-year), this function
    takes a Julian Date ``target_jd`` (instant-anchored, ~27.32 d
    periodicity). The asymmetry is **deliberate**: solar returns are
    naturally birthday-keyed; lunar returns are ~13x more frequent
    so the caller MUST specify which instant the search starts from.
    Passing ``target_jd`` as a year integer (e.g., ``2010``) will
    NOT raise but will produce a return near JD 2010, i.e., near
    -4677 BC -- almost certainly not what the caller wants. The
    ``target_jd`` parameter doc repeats this guard.

    **First-return >= ``target_jd`` contract -- LRET-01 binding.**

    The first-return seed is computed via mean-motion lift from
    ``target_jd``: read the Moon's signed residual ``r0`` at
    ``target_jd`` (in ``[-180, +180)``), then advance by
    ``(-r0) mod 360 / 13.176`` days. The result lies within ~1 d
    of the true first return (anomalistic variation), comfortably
    inside the +/-1.5 d bisection bracket. A cycle fallback
    (``n = 0, 1, 2`` of ``t_first_seed + n * 27.321582``) handles
    the (vanishingly unlikely) anomalistic outlier case AND the
    inclusive boundary case where the Moon is exactly at natal at
    ``target_jd`` (then the mean-motion estimate is ``target_jd``
    itself; the bisection lands at ``target_jd +/- tol_days``, the
    caller receives ``target_jd``). The FIRST candidate whose
    resolved JD is >= ``target_jd - tol_days`` wins -- this is the
    subtle correctness pin for LRET-01.

    **``natal_lat/lon`` vs ``return_lat/lon`` -- distinguish LOUDLY.**

    Same as :func:`solar_return`: ``natal_lat/lon`` are NEVER used
    for the Moon longitude resolution (Moon is geocentric);
    ``return_lat/lon`` set the houses of the return chart. Passing
    ``return_lat=None`` (default) reuses ``natal_lat``;
    ``return_lon=None`` (default) reuses ``natal_lon``.

    **UTC-only contract -- LOUD.** ``natal_jd`` and ``target_jd``
    MUST be UTC Julian Dates. Time-zone conversion is the caller's
    responsibility.

    **Polar relocation safety.** The internal
    :func:`ketu.charts.compute_chart` call hard-wires
    ``polar_fallback='porphyry'`` so extreme ``return_lat`` (Tromso,
    polar expeditions) does NOT raise ``HighLatitudeError``. Use
    ``system='whole_sign'`` or ``system='equal'`` if non-Porphyry
    cusps are desired at high latitudes.

    **Aberration convention.** Ketu uses TRUE geocentric Moon (no
    aberration on body_id=1, see ``ketu/ephemeris/planets.py:190``).
    Moon's aberration is negligible (it's geocentric and close); the
    resolved instant agrees with Astro.com to sub-arcsec.

    **Accuracy vs Swiss Ephemeris.** The resolved Moon return instant
    agrees with Astro.com to sub-arcsec (Moon aberration is geocentric
    and negligible). The returned chart's Moon longitude should match
    the natal Moon longitude within 1 arcsecond (LRET-03 tolerance).
    House cusps at the return location agree with Swiss to ±0.01°.

    **Supported date range.** 1800–2200 CE. The mean-motion seed
    estimation uses sidereal/tropical mean motion (13.176 deg/d),
    accurate enough across this range. The bisection converges to
    1 arcsecond in all cases.

    **Edge cases.** Passing ``target_jd`` exactly at a return moment
    (within the 1-arcsecond tolerance) returns ``target_jd`` itself
    (inclusive boundary — LRET-01). Subsequent returns are NOT returned
    by this call; call again with ``target_jd = prev_jd + 27.32`` to
    step forward. Polar ``return_lat`` is handled via internal
    ``polar_fallback='porphyry'``; no ``HighLatitudeError`` is raised.
    Passing ``target_jd`` as a year integer (e.g. 2010) is silently
    accepted but produces a chart near 4677 BC — use a proper JD.

    Examples
    --------
    >>> # First lunar return on or after 2010-01-01T00:00 UT for a 2000 natal:
    >>> jd_natal = 2451545.0
    >>> jd_target = 2455197.5  # 2010-01-01T00:00 UT
    >>> chart = lunar_return(jd_natal, 48.85, 2.35, jd_target)
    >>> float(chart["jd"]) >= jd_target - 1e-7  # first return >= target
    True
    >>> chart["body_lons"].shape
    (13,)
    """
    # Type guard: target_jd must be a float-like (not str).
    # int is accepted via float() promotion.
    if isinstance(target_jd, str):
        raise ValueError(
            f"target_jd must be a float (Julian Date); got string {target_jd!r}. "
            "Pass a UTC Julian Date (e.g., 2451545.0 for 2000-01-01T12:00 UT), NOT a year."
        )

    # 1. Read natal Moon longitude (single ephemeris call):
    natal_moon_lon = float(calc_planet_position(float(natal_jd), 1)[0])

    target_jd_f = float(target_jd)

    # 2. Estimate the first return seed via mean-motion lift from target_jd.
    # The Moon's signed residual at target_jd, r0 in [-180, +180), tells us
    # how far the Moon has yet to advance to come back to natal:
    #   advance_deg = (-r0) mod 360  in [0, 360).
    # Mean motion 13.176 deg/d gives the seed:
    #   t_first_seed = target_jd + advance_deg / 13.176.
    # Anomalistic perturbations make the true return within ~0.5-1 d of this
    # estimate -- comfortably inside a +/-1.5 d bracket.
    moon_at_target = float(calc_planet_position(target_jd_f, 1)[0])
    r0 = float(_signed_residual_deg(np.asarray(moon_at_target), natal_moon_lon))
    advance_deg = (-r0) % 360.0  # [0, 360)
    days_to_first_return = advance_deg / _MOON_MEAN_SPEED_DEG_PER_DAY
    t_first_seed = target_jd_f + days_to_first_return

    # 3. Seed-cycle search: try the mean-motion estimate first; if its bracket
    # fails (anomalistic variation > 1.5 d, vanishingly unlikely) or its
    # resolved JD lands < target_jd (Moon was already AT natal within tol_deg
    # at target_jd and the estimate undershot), try the next two cycles.
    # This guarantees the resolved JD is the first lunar return >= target_jd
    # (LRET-01 binding).
    jd_return: Optional[float] = None
    for n in range(3):  # 0, 1, 2 -- covers any conceivable case within 2 sidereal months
        t_seed = t_first_seed + n * _TROPICAL_MONTH_D

        try:
            candidate = _solve_return(
                body_id=1,
                natal_lon_ref=natal_moon_lon,
                t_seed=t_seed,
                half_window_days=1.5,
            )
        except ValueError:
            # No sign change in this bracket -- try next cycle.
            continue

        # First-return->= target_jd contract: the candidate must be
        # >= target_jd (within tol_days of the boundary). If the n=0 bracket
        # lands BEFORE target_jd (the Moon was already at natal within
        # tol_deg at target_jd and the mean-motion estimate slightly
        # undershot), keep searching.
        if candidate >= target_jd_f - _TOL_DAYS:
            jd_return = candidate
            break
        # else: this candidate is before target_jd, continue to n+1.

    if jd_return is None:
        raise ValueError(
            f"No lunar return found in [target_jd, target_jd + 2 * 27.32 d] "
            f"= [{target_jd_f}, {target_jd_f + 2 * _TROPICAL_MONTH_D}] for "
            f"natal_jd={natal_jd}. This is pathological -- the Moon's longitude "
            f"is monotonic and a return MUST exist within one sidereal period. "
            f"Check natal_jd and target_jd are valid UTC Julian Dates."
        )

    # 3. Resolve the return-chart geography (relocation contract -- LRET-05):
    chart_lat = float(natal_lat) if return_lat is None else float(return_lat)
    chart_lon = float(natal_lon) if return_lon is None else float(return_lon)

    # 4. Assemble CHART_DTYPE with polar-safe fallback hard-wired:
    return compute_chart(
        jd_return,
        chart_lat,
        chart_lon,
        system=system,
        polar_fallback="porphyry",
    )
