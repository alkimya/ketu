"""Pure-NumPy bisection root-finder for Sun/Moon longitude returns.

This module is private (underscored). It exists to satisfy ROADMAP
Phase 18 Success Criterion #3: ``solar_return`` and ``lunar_return``
MUST share a single root-finder implementation. The factorisation is
non-negotiable per LRET-02.

Algorithm: bisection on the signed-short-arc residual
``((body_lon(t) - natal_lon_ref + 540) % 360) - 180``. Bisection is
chosen over Brent / Newton / secant for:

- **Curvature indifference** — Moon's parallactic+anomalistic
  perturbations cause d²θ/dt² inflections within a sidereal month;
  Newton's quadratic convergence would degrade and secant would
  stall near horizontal tangents. Bisection always converges in
  ``log2(bracket_width / tol)`` iterations regardless of curvature.
- **Pure-NumPy contract** — PROJECT.md / CLAUDE.md / REQUIREMENTS.md
  forbid scipy. Hand-rolled Brent is ~50 LOC of delicate code with
  ~3× iteration speedup; not worth the complexity at v1.2 call
  frequencies (~30 µs per return is comfortably below any budget).
- **Existing Ketu precedent** — ``find_exact_aspect``
  (``ketu/ephemeris/planets.py:273``) and ``refine_exact_moment``
  (``ketu/aspects/core.py:106``) both use bisection. This module
  stays consistent (and is the stricter cousin: tol_deg=1/3600
  vs. ``find_exact_aspect``'s 1e-3 days).

Wrap-around handling: ``_signed_residual_deg(lon, ref)`` lifts the
naive ``lon - ref`` (in [-360, +360]) to the signed short arc
[-180, +180). Same algebra as ``circular_midpoint`` in
``ketu/composite/core.py:79-81`` and ``porphyry_cusps`` in
``ketu/houses/porphyry.py:159``.

Retrograde safety: geocentric Sun is NEVER retrograde; geocentric
Moon is NEVER retrograde. The residual is monotonically increasing
over any bisection bracket for both Sun and Moon — guaranteeing
convergence in ``log2(bracket_width / tol)`` iterations.

Stopping criterion: dual threshold ``|residual| < tol_deg`` (1 arc-
second per RET-03 / LRET-03) OR ``bracket_width < tol_days`` (8.6 ms
FP-noise floor). The residual fires first in practice (~13 iter for
Sun, ~17 iter for Moon).

Module constants are exposed for testability; ``_solve_return``
itself is the sole public-from-the-package entry point.
"""
from __future__ import annotations

import numpy as np

from ketu.ephemeris.planets import calc_planet_position_batch

# Tolerances (RET-03 / LRET-03 binding):
_TOL_DEG: float = 1.0 / 3600.0  # 1 arc-second residual threshold (degrees)
_TOL_DAYS: float = 1e-7  # ~8.6 ms time-delta floor (overshoots arc-second per body's speed)

# Orbital periods used as initial-bracket seeds by Plans 18-02 (solar) and 18-03 (lunar):
_TROPICAL_YEAR_D: float = 365.24219  # Tropical year (equinox-to-equinox; Ketu's tropical-zodiac convention)
_TROPICAL_MONTH_D: float = 27.321582  # Tropical month (Moon returns to equinox-of-date longitude)


def _signed_residual_deg(lon: np.ndarray, ref: float) -> np.ndarray:
    """Signed short-arc residual in degrees, on ``[-180, +180)``.

    Same wrap-around algebra as ``circular_midpoint``
    (``ketu/composite/core.py:79-81``) and ``porphyry_cusps``
    (``ketu/houses/porphyry.py:159``). The antipodal case
    ``lon - ref == 180`` collapses to ``-180`` under
    ``((180 + 540) % 360) - 180 = -180`` (the interval is right-open).

    Parameters
    ----------
    lon : float or np.ndarray
        Body longitude(s) in degrees, normalised or not.
    ref : float
        Reference longitude in degrees.

    Returns
    -------
    np.ndarray
        Signed residual ``lon - ref`` lifted to ``[-180, +180)``.
        Scalar input returns a 0-d array.

    Notes
    -----
    Algebra: ``((lon - ref + 540) % 360) - 180``. The ``+ 540`` shift
    is the canonical Ketu wrap-around trick — adding 1.5 turns before
    the modulo guarantees the result lands in ``[-180, +180)`` for any
    input in ``[-360, +360]``. Bit-identical at the seam, no trig
    rounding, vectorisable.

    See Also
    --------
    ketu.composite.circular_midpoint : Same algebra applied to the
        midpoint computation (signed short-arc difference between two
        longitudes).

    Examples
    --------
    >>> import numpy as np
    >>> float(_signed_residual_deg(np.array(0.05), 359.95))
    0.10000000000002274
    >>> float(_signed_residual_deg(np.array(359.95), 0.05))
    -0.10000000000002274
    """
    return ((np.asarray(lon, dtype=np.float64) - ref + 540.0) % 360.0) - 180.0


def _solve_return(
    body_id: int,
    natal_lon_ref: float,
    t_seed: float,
    half_window_days: float,
    *,
    max_iter: int = 60,
    tol_deg: float = _TOL_DEG,
    tol_days: float = _TOL_DAYS,
) -> float:
    """Bisect on body-longitude residual to find the JD of a longitude return.

    Pure-NumPy bisection on the signed short-arc residual
    ``((body_lon(t) - natal_lon_ref + 540) % 360) - 180`` over the
    initial bracket ``[t_seed - half_window_days, t_seed + half_window_days]``.

    Parameters
    ----------
    body_id : int
        Pass-through to :func:`ketu.ephemeris.planets.calc_planet_position_batch`.
        ``0`` (Sun) or ``1`` (Moon) for Phase 18. Saturn/Jupiter returns
        in v1.3 would use ``5`` / ``6``.
    natal_lon_ref : float
        Natal longitude of ``body_id`` to return to, in degrees. Read
        once at the caller's public-API boundary; not recomputed per
        iteration.
    t_seed : float
        Initial guess JD near the expected return moment. Caller's
        responsibility to select correctly (Plan 18-02 uses
        ``natal_jd + (target_year - natal_year) * 365.24219`` for Sun;
        Plan 18-03 uses ``target_jd + n * 27.321582`` for Moon, with
        ``n`` chosen so the bracket contains a sign change).
    half_window_days : float
        Bracket half-width in days. Sun: ``1.5`` (±36 h). Moon: ``1.5``
        (±1.5 d). Both give ~6× safety margin over the body's expected
        drift at the seam.
    max_iter : int, optional
        Bisection iteration cap. Default ``60`` (overkill — Sun
        converges in ~13 iterations, Moon in ~17 from the recommended
        bracket widths). ``2**60`` halvings reach sub-attosecond
        time-delta precision; ``max_iter`` is a runaway guard, not the
        expected stop.
    tol_deg : float, optional
        Residual threshold. Default ``1/3600 = 2.778e-4°`` (1 arc-
        second per RET-03 / LRET-03). Bisection terminates as soon as
        ``|signed_residual(t_mid)| < tol_deg``.
    tol_days : float, optional
        Bracket-width floor. Default ``1e-7 d ≈ 8.6 ms``. Bisection
        terminates if the bracket shrinks below this regardless of
        residual (FP-noise protection).

    Returns
    -------
    float
        The JD at which the body's longitude crosses ``natal_lon_ref``
        to within ``tol_deg`` of the signed-short-arc residual (or to
        within ``tol_days`` of bracket width, whichever fires first).

    Raises
    ------
    ValueError
        If the initial bracket
        ``[t_seed - half_window_days, t_seed + half_window_days]``
        does NOT contain a sign change of the signed residual. This
        means the caller's seed was wrong — extend the search at the
        public-API level, do NOT auto-extend here (RESEARCH Open
        Question Q1: auto-extension would mask seed-selection bugs).

    Notes
    -----
    **Retrograde safety:** Geocentric Sun is NEVER retrograde;
    geocentric Moon is NEVER retrograde. The residual is monotonic
    over the bracket for both bodies; bisection always converges.
    Apparent retrograde motion is a phenomenon of geocentric
    Mercury/Venus/Mars/Jupiter/Saturn/Uranus/Neptune/Pluto only —
    NOT of Sun or Moon. Adding Saturn/Jupiter returns in v1.3 will
    require revisiting this — but Phase 18 is Sun + Moon only.

    **Vectorisation:** ``calc_planet_position_batch`` is natively
    vectorised. The bracket-endpoint pre-evaluation packs both into a
    single call (``np.array([t_lo, t_hi])``); the inner loop evaluates
    one midpoint per iteration (single-element array form for
    consistency).

    See Also
    --------
    ketu.ephemeris.planets.calc_planet_position_batch : Vectorised
        body-longitude evaluator called once per bracket endpoint and
        once per bisection iteration.

    Examples
    --------
    >>> # Solar return seed example (real call site lands in Plan 18-02
    >>> # ``solar_return``; here we only smoke the helper signature):
    >>> jd = _solve_return(0, 100.0, 2451910.24, 1.5)  # doctest: +SKIP
    >>> isinstance(jd, float)  # doctest: +SKIP
    True
    """
    t_lo: float = float(t_seed - half_window_days)
    t_hi: float = float(t_seed + half_window_days)

    lons = calc_planet_position_batch(np.array([t_lo, t_hi], dtype=np.float64), body_id)[:, 0]
    r_lo = float(_signed_residual_deg(lons[0], natal_lon_ref))
    r_hi = float(_signed_residual_deg(lons[1], natal_lon_ref))

    if r_lo * r_hi > 0.0:
        raise ValueError(
            f"No return in bracket [{t_lo}, {t_hi}] for body_id={body_id}: "
            f"residuals r_lo={r_lo}°, r_hi={r_hi}° have the same sign. "
            f"Caller seed (t_seed={t_seed}, half_window_days={half_window_days}) "
            f"does not bracket a zero of the signed-short-arc residual."
        )

    for _ in range(max_iter):
        t_mid = 0.5 * (t_lo + t_hi)
        lon_mid = float(
            calc_planet_position_batch(np.array([t_mid], dtype=np.float64), body_id)[0, 0]
        )
        r_mid = float(_signed_residual_deg(lon_mid, natal_lon_ref))

        if abs(r_mid) < tol_deg:
            return float(t_mid)
        if (t_hi - t_lo) < tol_days:
            return float(t_mid)

        if r_lo * r_mid < 0.0:
            t_hi, r_hi = t_mid, r_mid
        else:
            t_lo, r_lo = t_mid, r_mid

    return float(0.5 * (t_lo + t_hi))
