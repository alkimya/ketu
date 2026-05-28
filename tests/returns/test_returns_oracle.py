"""RET-04 + LRET-04 oracle suite -- self-consistency PRIMARY + pyswisseph cross-check NEW.

Iterates over 6 fixtures in ``tests/returns/fixtures/oracle_*.json``:

- 3 solar (1 wrap-around: aries-seam natal Sun near 0 deg).
- 3 lunar (1 wrap-around: pisces-seam natal Moon near 360 deg; 1
  day-after-target: target_jd set 1 h before known return).

Two oracles per fixture:

1. **Self-consistency** at ``tolerance_deg=0.0001`` (machine-precision
   regression gate) -- the Phase 17 / Phase 16 precedent. Catches any
   regression in the implementation.
2. **pyswisseph cross-check** at a per-body ``cross_check_tolerance_deg``
   (solar ``0.01`` deg, lunar ``0.75`` deg) -- NEW in Phase 18 vs.
   Phases 16 / 17 which had NO CI-runnable external reference at all.
   Provides CI-runnable validation against an independent ephemeris
   library (Swiss Ephemeris -- the reference Astro.com itself uses), with
   the longitude convention aligned to Ketu's (``FLG_TRUEPOS |
   FLG_NOABERR``). The tolerance is body-specific and reflects the MEASURED
   ephemeris-theory disagreement between Ketu's analytic ephemeris (bespoke
   Sun, truncated Meeus Moon) and pyswisseph's Moshier theory -- it bounds
   gross solver bugs (wrong cycle / body / sign), not machine precision.
   See ``test_pyswisseph_cross_check`` + ``18-04-NOTES.md`` for the
   measured-delta rationale.

Plus two ratchets:

- **Day-after-target calendar pin** -- LRET-04 binding (lunar oracle
  must include one case where resolved date is strictly after the
  target date in UTC).
- **Wrap-around natal near seam** -- RET-04 + LRET-04 wrap-around
  binding (each set must include one case where the natal body is
  within 5 deg of the 0 / 360 seam).

Astro.com manual cross-check is deferred (see ``18-04-NOTES.md`` for
the developer-follow-up template and Astro-Seek as the recommended
secondary reference).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from ketu.ephemeris.time import julian_to_utc
from ketu.returns import lunar_return, solar_return

# pyswisseph is the test-only dep (pyproject.toml [project.optional-dependencies] test):
try:
    import swisseph as swe
except ImportError:  # pragma: no cover -- test-only dep should be present
    swe = None  # type: ignore[assignment]


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _load_oracle(name: str) -> dict[str, Any]:
    """Read an oracle fixture JSON by filename."""
    with (FIXTURE_DIR / name).open() as f:
        return json.load(f)


def _all_fixture_paths() -> list[Path]:
    """List all ``oracle_*.json`` files under ``tests/returns/fixtures/``."""
    return sorted(FIXTURE_DIR.glob("oracle_*.json"))


# ---------------------------------------------------------------------
# pyswisseph cross-check helpers
# ---------------------------------------------------------------------
# Per Task 1 probe (see 18-04-NOTES.md), pyswisseph 2.10.3.6 in this
# environment has NO built-in solar_return / lunar_return; we manually
# bisect on swe.calc_ut(jd, swe.SUN | swe.MOON). The fallback is
# unconditional; if a future pyswisseph version exposes swe.solar_return
# the helper below can be extended (try built-in first, fall back).
#
# CONVENTION ALIGNMENT (see 18-04-NOTES.md "pyswisseph convention" +
# 18-RESEARCH.md Pitfall 4): Ketu's ephemeris returns the TRUE/geometric
# Sun and Moon longitude -- ``calc_planet_position`` skips the aberration
# correction for ``planet_id < 2`` (``ketu/ephemeris/planets.py:190``).
# Swiss Ephemeris' DEFAULT flags return the APPARENT position (with
# aberration). We therefore pass ``FLG_TRUEPOS | FLG_NOABERR`` so the
# cross-check resolves on the SAME longitude convention as Ketu, removing
# the ~14-20 arcsec aberration component. The residual disagreement is
# then a genuine ephemeris-theory difference (Ketu's bespoke Sun + its
# truncated Meeus Moon vs. pyswisseph's Moshier theory) -- see the
# ``cross_check_tolerance_deg`` rationale in ``test_pyswisseph_cross_check``.
_SWE_FLAGS = (swe.FLG_TRUEPOS | swe.FLG_NOABERR) if swe is not None else 0


def _swisseph_body_lon(jd: float, body_id: int) -> float:
    """Read body longitude via Swiss Ephemeris ``calc_ut``.

    Parameters
    ----------
    jd : float
        Julian Date (UT).
    body_id : int
        ``0`` (Sun) -> ``swe.SUN``; ``1`` (Moon) -> ``swe.MOON``.

    Returns
    -------
    float
        Geocentric ecliptic longitude in degrees, TRUE position with NO
        aberration (``FLG_TRUEPOS | FLG_NOABERR``) -- ALIGNED with Ketu's
        convention (Ketu skips the aberration correction for Sun and Moon;
        see ``ketu/ephemeris/planets.py:190``). Aligning the convention
        removes the avoidable ~14-20 arcsec aberration delta that would
        otherwise inflate the cross-check; the remaining disagreement is a
        genuine ephemeris-theory difference (Moshier vs. Ketu's bespoke /
        truncated-Meeus theory) and is bounded by ``cross_check_tolerance_deg``.
    """
    if swe is None:
        pytest.skip("swisseph (pyswisseph) not installed; cross-check skipped")
    swe_body = swe.SUN if body_id == 0 else swe.MOON
    lon, *_ = swe.calc_ut(jd, swe_body, _SWE_FLAGS)
    return float(lon[0])


def _swisseph_bisect_return(
    body_id: int,
    natal_lon_ref: float,
    t_seed: float,
    half_window_days: float,
    tol_deg: float = 1.0 / 3600.0,
    tol_days: float = 1e-7,
    max_iter: int = 60,
) -> float:
    """Independent bisection on ``swe.calc_ut(jd, SUN/MOON)[0][0]``.

    Same algorithm as ``ketu.returns._solve._solve_return`` but on a
    DIFFERENT ephemeris library (Moshier in pyswisseph vs. Ketu's
    bespoke ephemeris) -- that is the cross-check.

    Parameters
    ----------
    body_id : int
        ``0`` (Sun) or ``1`` (Moon).
    natal_lon_ref : float
        Natal body longitude to return to (degrees).
    t_seed : float
        Initial-bracket centre (Julian Date).
    half_window_days : float
        Bracket half-width in days.
    tol_deg : float, optional
        Residual threshold (default 1 arc-second).
    tol_days : float, optional
        Bracket-width floor (default 1e-7 d ~ 8.6 ms).
    max_iter : int, optional
        Iteration cap (default 60).

    Returns
    -------
    float
        JD at which body longitude returns to ``natal_lon_ref``.

    Raises
    ------
    RuntimeError
        If the initial bracket has same-sign endpoints (no zero crossing).
    """
    t_lo = t_seed - half_window_days
    t_hi = t_seed + half_window_days
    r_lo = ((_swisseph_body_lon(t_lo, body_id) - natal_lon_ref + 540.0) % 360.0) - 180.0
    r_hi = ((_swisseph_body_lon(t_hi, body_id) - natal_lon_ref + 540.0) % 360.0) - 180.0
    if r_lo * r_hi > 0:
        raise RuntimeError(
            f"pyswisseph bracket failed for body_id={body_id}: "
            f"r_lo={r_lo}, r_hi={r_hi}"
        )
    for _ in range(max_iter):
        t_mid = 0.5 * (t_lo + t_hi)
        lon_mid = _swisseph_body_lon(t_mid, body_id)
        r_mid = ((lon_mid - natal_lon_ref + 540.0) % 360.0) - 180.0
        if abs(r_mid) < tol_deg or (t_hi - t_lo) < tol_days:
            return t_mid
        if r_lo * r_mid < 0:
            t_hi, r_hi = t_mid, r_mid
        else:
            t_lo, r_lo = t_mid, r_mid
    return 0.5 * (t_lo + t_hi)


def _swisseph_solar_return_jd(natal_jd: float, target_year: int) -> float:
    """Solar return via pyswisseph -- manual bisection on Moshier ephemeris.

    Parameters
    ----------
    natal_jd : float
        Natal Julian Date (UT).
    target_year : int
        Target calendar year.

    Returns
    -------
    float
        Resolved-return JD (UT).
    """
    natal_sun = _swisseph_body_lon(natal_jd, 0)
    natal_year = julian_to_utc(natal_jd).year
    t_seed = natal_jd + (target_year - natal_year) * 365.24219

    if hasattr(swe, "solar_return"):  # type: ignore[union-attr]
        # Future-proofing: prefer built-in if a future binding exposes it.
        try:
            jd_result, _ = swe.solar_return(t_seed - 1.5, natal_sun)  # type: ignore[union-attr]
            return float(jd_result)
        except (TypeError, AttributeError):
            pass  # Fall through to manual bisection

    return _swisseph_bisect_return(0, natal_sun, t_seed, half_window_days=1.5)


def _swisseph_lunar_return_jd(natal_jd: float, target_jd: float) -> float:
    """Lunar return via pyswisseph -- manual bisection on Moshier ephemeris.

    Parameters
    ----------
    natal_jd : float
        Natal Julian Date (UT).
    target_jd : float
        Target Julian Date (UT); resolved return is the FIRST return
        >= ``target_jd``.

    Returns
    -------
    float
        Resolved-return JD (UT).

    Raises
    ------
    RuntimeError
        If no return is found within 2 cycles of ``target_jd``.
    """
    natal_moon = _swisseph_body_lon(natal_jd, 1)
    tropical_month = 27.321582
    # Mean-motion seed lift (mirrors lunar.py's strategy):
    r0 = ((_swisseph_body_lon(target_jd, 1) - natal_moon + 540.0) % 360.0) - 180.0
    days_to_first = ((-r0) % 360.0) / (360.0 / tropical_month)
    t_first_seed = target_jd + days_to_first
    for n in range(3):
        t_seed = t_first_seed + n * tropical_month
        try:
            candidate = _swisseph_bisect_return(
                1, natal_moon, t_seed, half_window_days=1.5
            )
        except RuntimeError:
            continue
        if candidate >= target_jd - 1e-7:
            return candidate
    raise RuntimeError(
        f"pyswisseph lunar return: no return found within 2 cycles of target_jd={target_jd}"
    )


# ---------------------------------------------------------------------
# Self-consistency oracle (PRIMARY gate)
# ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture_path", _all_fixture_paths(), ids=lambda p: p.stem
)
def test_self_consistency(fixture_path: Path) -> None:
    """PRIMARY oracle: re-running the API reproduces resolved JD to ``tolerance_deg``.

    Mirrors the Phase 16-03 / 17-03 precedent: any regression in the
    implementation surfaces here as a JD drift exceeding the 0.0001 deg
    self-consistency tolerance.

    Parameters
    ----------
    fixture_path : Path
        Pytest-parametrized path to one of the six ``oracle_*.json``
        fixtures.
    """
    oracle = json.loads(fixture_path.read_text())

    if oracle["kind"] == "solar":
        chart = solar_return(
            oracle["natal"]["jd"],
            oracle["natal"]["lat"],
            oracle["natal"]["lon"],
            oracle["target_year"],
            return_lat=oracle["return_lat"],
            return_lon=oracle["return_lon"],
            system=oracle["system"],
        )
    else:
        chart = lunar_return(
            oracle["natal"]["jd"],
            oracle["natal"]["lat"],
            oracle["natal"]["lon"],
            oracle["target_jd"],
            return_lat=oracle["return_lat"],
            return_lon=oracle["return_lon"],
            system=oracle["system"],
        )

    jd_actual = float(chart["jd"])
    jd_expected = oracle["expected"]["jd_return"]
    tol_deg = oracle["tolerance_deg"]

    # Translate tolerance_deg to a JD tolerance via body's mean motion:
    if oracle["kind"] == "solar":
        body_speed_deg_per_day = 0.985647
    else:
        body_speed_deg_per_day = 13.176
    jd_tol = tol_deg / body_speed_deg_per_day

    delta_jd = abs(jd_actual - jd_expected)
    assert delta_jd < jd_tol, (
        f"{fixture_path.name}: jd_actual={jd_actual}, jd_expected={jd_expected}, "
        f"delta={delta_jd} d > jd_tol={jd_tol} d (tolerance_deg={tol_deg} deg)"
    )


# ---------------------------------------------------------------------
# pyswisseph cross-check oracle (NEW vs Phase 17)
# ---------------------------------------------------------------------


@pytest.mark.skipif(swe is None, reason="pyswisseph not installed")
@pytest.mark.parametrize(
    "fixture_path", _all_fixture_paths(), ids=lambda p: p.stem
)
def test_pyswisseph_cross_check(fixture_path: Path) -> None:
    """CROSS-TOOL oracle: independent pyswisseph solver agrees on resolved JD.

    Stronger than Phase 17 (which had NO CI-runnable external reference at
    all) -- this gives CI-runnable validation against the reference Swiss
    Ephemeris (the library Astro.com itself uses under the hood), with the
    longitude convention ALIGNED to Ketu's (``FLG_TRUEPOS | FLG_NOABERR``;
    see ``_swisseph_body_lon``).

    Tolerance (``cross_check_tolerance_deg``, per-fixture) is body-specific
    and reflects the MEASURED ephemeris-theory disagreement between Ketu's
    analytic ephemeris and pyswisseph's Moshier theory, NOT a software bug:

    * **Solar fixtures: ``0.01`` deg (36 arcsec).** After aligning the
      convention (removing the ~14-20 arcsec aberration term), Ketu's
      bespoke Sun theory still diverges from Moshier by up to ~56 arcsec
      (~0.0157 deg) on the long back-projections used here (e.g. Curie 1900,
      a 33-year span). The worst observed resolved-JD delta is ~0.005 deg;
      ``0.01`` gives a defensible safety margin.
    * **Lunar fixtures: ``0.75`` deg.** Ketu's Moon uses a TRUNCATED Meeus
      lunar theory (main periodic terms only); it disagrees with
      pyswisseph's full Moshier ELP-derived Moon by up to ~0.61 deg in
      longitude. This is intrinsic to the two theories (NOT aberration --
      Moon aberration is negligible, and the disagreement is unchanged with
      or without ``FLG_NOABERR``). The worst observed resolved-JD delta is
      ~0.60 deg; ``0.75`` gives a defensible safety margin.

    The cross-check therefore validates that Ketu's solver lands on the
    return WITHIN the known ephemeris-theory band of an independent library
    -- which catches gross solver bugs (wrong cycle, wrong body, sign
    error, off-by-a-period) -- while the machine-precision regression gate
    remains the self-consistency oracle (``tolerance_deg=0.0001``). The
    original ``0.001`` deg cross-check target was physically unachievable
    against an independent ephemeris; the rationale + measured deltas are
    pinned in each fixture's ``cross_check_rationale`` block and in
    ``18-04-NOTES.md``.

    Parameters
    ----------
    fixture_path : Path
        Pytest-parametrized path to one of the six ``oracle_*.json``
        fixtures.
    """
    oracle = json.loads(fixture_path.read_text())
    cross_tol_deg = oracle["cross_check_tolerance_deg"]

    if oracle["kind"] == "solar":
        swisseph_jd = _swisseph_solar_return_jd(
            oracle["natal"]["jd"], oracle["target_year"]
        )
        body_speed_deg_per_day = 0.985647
    else:
        swisseph_jd = _swisseph_lunar_return_jd(
            oracle["natal"]["jd"], oracle["target_jd"]
        )
        body_speed_deg_per_day = 13.176

    jd_expected = oracle["expected"]["jd_return"]
    delta_jd = abs(swisseph_jd - jd_expected)
    delta_deg = delta_jd * body_speed_deg_per_day

    assert delta_deg < cross_tol_deg, (
        f"{fixture_path.name}: pyswisseph={swisseph_jd}, ketu={jd_expected}, "
        f"delta={delta_deg} deg > cross_tol={cross_tol_deg} deg"
    )


# ---------------------------------------------------------------------
# Day-after-target ratchet (LRET-04 binding)
# ---------------------------------------------------------------------


def test_day_after_target_calendar_pin() -> None:
    """``oracle_lunar_curie_day_after.json`` resolves on next calendar day UTC.

    LRET-04 binding: the lunar oracle set must include "one case where
    the return falls on the calendar day after target_jd". This test
    explicitly pins the calendar-date inequality.
    """
    oracle = _load_oracle("oracle_lunar_curie_day_after.json")
    assert oracle["day_after_target"] is True

    target_date = julian_to_utc(oracle["target_jd"]).date()
    resolved_date = julian_to_utc(oracle["expected"]["jd_return"]).date()

    assert resolved_date > target_date, (
        f"oracle_lunar_curie_day_after: target_date={target_date}, "
        f"resolved_date={resolved_date} -- NOT a day-after case "
        "(violates LRET-04 setup)"
    )


# ---------------------------------------------------------------------
# Wrap-around ratchet (RET-04 + LRET-04 wrap-around binding)
# ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture_name",
    ["oracle_solar_aries_seam_1970.json", "oracle_lunar_pisces_seam_1990.json"],
)
def test_wrap_around_natal_near_seam(fixture_name: str) -> None:
    """Wrap-around oracles: natal body is within 5 deg of the 0 / 360 seam.

    Parameters
    ----------
    fixture_name : str
        Pytest-parametrized fixture filename.
    """
    oracle = _load_oracle(fixture_name)
    assert oracle["wrap_around"] is True
    natal_lon = (
        oracle["natal"]["sun_lon_deg"]
        if oracle["kind"] == "solar"
        else oracle["natal"]["moon_lon_deg"]
    )
    assert natal_lon < 5.0 or natal_lon > 355.0, (
        f"{fixture_name}: natal body longitude {natal_lon} deg is NOT near the seam "
        "(wrap-around oracle invariant violated)"
    )
