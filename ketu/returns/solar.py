"""
Solar return public API — RET-01..05.

``solar_return`` resolves the moment when the Sun's geocentric
longitude equals its natal longitude in a target year, then assembles
a CHART_DTYPE at the resolved instant (optionally relocated). The
Sun root-finding is delegated to ``ketu.returns._solve._solve_return``
— the shared bisection helper mandated by ROADMAP Phase 18 Success
Criterion #3 (LRET-02 factorisation lock).

The internal ``compute_chart`` call hard-wires
``polar_fallback='porphyry'`` so extreme ``return_lat`` does NOT
raise ``HighLatitudeError`` (RESEARCH Open Question Q5 — no
user-facing ``polar_fallback=`` kwarg).
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from ketu.charts import compute_chart
from ketu.ephemeris.planets import calc_planet_position
from ketu.ephemeris.time import julian_to_utc
from ketu.returns._solve import _TROPICAL_YEAR_D, _solve_return


def solar_return(
    natal_jd: float,
    natal_lat: float,
    natal_lon: float,
    target_year: int,
    return_lat: Optional[float] = None,
    return_lon: Optional[float] = None,
    system: str = "placidus",
) -> np.ndarray:
    """
    Compute the solar return chart for a natal birth and a target year.

    Resolves the moment in ``target_year`` at which the Sun's
    geocentric longitude equals the natal Sun longitude (within 1
    arc-second per RET-03), then assembles a scalar
    :data:`ketu.charts.CHART_DTYPE` at that instant — optionally
    relocated to ``return_lat``/``return_lon`` (RET-01 + RET-05).

    Parameters
    ----------
    natal_jd : float
        Natal Julian Date (UTC). The natal Sun longitude is read once
        from this JD via :func:`ketu.ephemeris.planets.calc_planet_position`.
    natal_lat : float
        Natal geographic latitude in degrees. **NEVER used for the Sun
        longitude resolution** — Sun's geocentric longitude is
        location-independent. Lives on the signature for symmetry /
        future-proofing. Defaults for ``return_lat`` if the caller
        passes ``None``.
    natal_lon : float
        Natal geographic longitude in degrees. Same as ``natal_lat``:
        signature-symmetry only; not used for resolution. Defaults
        for ``return_lon`` if the caller passes ``None``.
    target_year : int
        Calendar year (UTC) in which to find the return. The seed is
        computed as
        ``natal_jd + (target_year - natal_year) * 365.24219`` where
        ``natal_year`` is extracted from ``natal_jd`` via
        :func:`ketu.ephemeris.time.julian_to_utc`.
    return_lat : float or None, optional
        Latitude for the return chart's houses, ASC, MC, ARMC, Vertex.
        ``None`` (default) reuses ``natal_lat`` — the "standard return"
        case. Non-``None`` produces a "relocated return".
    return_lon : float or None, optional
        Longitude for the return chart's houses (etc.). ``None``
        (default) reuses ``natal_lon``.
    system : str, optional
        House system identifier (validated by
        :func:`ketu.houses.calculate_houses`; raises ``ValueError`` on
        unknown systems). Default ``"placidus"``. Phase 15 adds
        ``"whole_sign"``, ``"equal"``, ``"regiomontanus"``.

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
        If ``target_year`` is not an integer, if the initial ±36 h
        bracket around the seed JD does not contain a sign change of
        the Sun-longitude residual (propagated from
        :func:`ketu.returns._solve._solve_return`; indicates a
        seed-selection bug — the bracket is NOT auto-extended per
        RESEARCH Open Question Q1), or if ``system`` is unknown
        (propagated from :func:`ketu.houses.calculate_houses`).

    See Also
    --------
    ketu.charts.compute_chart : Underlying chart-assembly call.
    ketu.returns._solve._solve_return : Shared pure-NumPy bisection
        helper used by both :func:`solar_return` and the upcoming
        :func:`lunar_return` (Plan 18-03).

    Notes
    -----
    **``natal_lat/lon`` vs ``return_lat/lon`` — distinguish LOUDLY.**

    The Sun's geocentric longitude is location-independent — it
    depends only on the JD. Therefore ``natal_lat/lon`` are
    **NEVER** used to compute the resolved return JD; they appear on
    the signature for symmetry with the rest of Ketu's pair-chart
    APIs (where geographic context is meaningful) and for
    future-proofing if a v1.3 extension wants to derive sect or
    parallactic context from natal location. By contrast,
    ``return_lat/lon`` ARE used: they set the houses, ASC, MC, ARMC,
    Vertex of the return chart via the underlying
    :func:`ketu.charts.compute_chart` call. Passing ``return_lat=None``
    (the default) reuses ``natal_lat`` (giving the "standard return"
    case); passing non-``None`` produces a "relocated return".

    **API asymmetry vs.** :func:`ketu.returns.lunar_return` **— LOUD.**
    This function takes an integer ``target_year`` (calendar-anchored,
    one return per birthday-year). :func:`ketu.returns.lunar_return`
    takes a Julian Date ``target_jd`` (instant-anchored). The
    asymmetry is deliberate: solar returns are naturally birthday-
    keyed; lunar returns are ~27.32 d periodic, so the caller must
    specify which instant the search starts from.

    **UTC-only contract — LOUD.** ``natal_jd`` MUST be UTC. Time-zone
    conversion is the caller's responsibility.

    **Polar relocation safety.** The internal
    :func:`ketu.charts.compute_chart` call hard-wires
    ``polar_fallback='porphyry'`` so extreme ``return_lat`` (Tromso,
    polar expeditions) does NOT raise ``HighLatitudeError``. Use
    ``system='whole_sign'`` or ``system='equal'`` if non-Porphyry
    cusps are desired at high latitudes.

    **Aberration convention.** Ketu uses TRUE geocentric Sun (no
    aberration, see ``ketu/ephemeris/planets.py:190``). Astro.com
    uses APPARENT longitude (~20.5 arcsec aberration). The aberration
    cancels in the natal-to-return resolved-instant math (same
    convention both sides), so the resolved instant agrees with
    Astro.com to sub-second; the return Sun longitude in the output
    CHART_DTYPE differs from Astro.com's by ~20 arcsec systematically.

    **Leap-year Feb 29 natal.** A Feb 29 natal in a non-leap
    ``target_year`` resolves normally — the seed
    ``natal_jd + (target_year - natal_year) * 365.24219`` is a
    tropical-year offset, not calendar-anchored. The return falls in
    late Feb / early March of the target year (no special-casing
    needed).

    **Accuracy vs Swiss Ephemeris.** The resolved return instant agrees
    with Astro.com to sub-second (the natal/return Sun longitudes use
    the same convention — no aberration — so the residual cancels). The
    return Sun longitude in the output ``CHART_DTYPE`` differs from
    Astro.com's by ~20 arcsec systematically (aberration constant).
    House cusps at the return location agree with Swiss to ±0.01°.

    **Supported date range.** 1800–2200 CE. The tropical-year seed
    offset diverges modestly outside this range; the bisection still
    converges but the seed may require a wider bracket in extreme
    centuries.

    **Polar relocation.** Polar ``return_lat`` is handled via internal
    ``polar_fallback='porphyry'``; no ``HighLatitudeError`` is raised
    for relocated returns.

    Examples
    --------
    >>> # Standard solar return for 2000-01-01 natal in target year 2010:
    >>> jd_natal = 2451545.0  # 2000-01-01T12:00 UT
    >>> chart = solar_return(jd_natal, 48.85, 2.35, 2010)
    >>> chart.dtype.names[:3]
    ('jd', 'lat', 'lon')
    >>> chart["body_lons"].shape
    (13,)
    """
    if not isinstance(target_year, (int, np.integer)):
        raise ValueError(
            f"target_year must be an integer; got {type(target_year).__name__}={target_year!r}. "
            "Pass an int year (e.g., 2010), not a JD or a string."
        )

    # 1. Read natal Sun longitude (single ephemeris call):
    natal_sun_lon = float(calc_planet_position(float(natal_jd), 0)[0])

    # 2. Compute seed JD from target_year (tropical-year offset):
    natal_year = julian_to_utc(float(natal_jd)).year
    t_seed = float(natal_jd) + (int(target_year) - natal_year) * _TROPICAL_YEAR_D

    # 3. Bisect via the shared helper (ROADMAP Success Criterion #3 binding):
    jd_return = _solve_return(
        body_id=0,
        natal_lon_ref=natal_sun_lon,
        t_seed=t_seed,
        half_window_days=1.5,
    )

    # 4. Resolve the return-chart geography (relocation contract — RET-05):
    chart_lat = float(natal_lat) if return_lat is None else float(return_lat)
    chart_lon = float(natal_lon) if return_lon is None else float(return_lon)

    # 5. Assemble CHART_DTYPE with polar-safe fallback hard-wired:
    return compute_chart(
        jd_return,
        chart_lat,
        chart_lon,
        system=system,
        polar_fallback="porphyry",
    )
