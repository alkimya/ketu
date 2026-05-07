"""HOU-01 precision regression tests for sidereal_time and mean_obliquity.

The asserted tolerances reflect the audit verdict in
``.planning/phases/10-houses-module/lst-audit-report.md`` (Verdict: TIGHTEN).

Test cases:

- ``test_sidereal_time_matches_swisseph_within_tolerance`` (5 dates) —
  apparent GST drift vs ``swe.sidtime(jd) * 15.0``; threshold
  :data:`TOL_GMST_ARCSEC`.
- ``test_mean_obliquity_matches_swisseph_within_tolerance`` (5 dates) —
  obliquity drift vs ``swe.calc_ut(jd, swe.ECL_NUT)[0][1]``; threshold
  :data:`TOL_OBLIQUITY_ARCSEC`.
- ``test_sidereal_time_longitude_offset_is_pure_addition`` (single, 3 longs) —
  cheap correctness invariant: LST = (GST + lon) % 360.
- ``test_asc_error_within_spec_at_polar_boundary`` (5 dates × lat=66.5°) —
  end-to-end ASC error fence at the Placidus polar boundary, isolated via
  ``swe.houses_armc``; threshold :data:`TOL_POLAR_ASC_ARCSEC` = 50″
  (10″ headroom vs HOU-01 60″ spec).

The module is **auto-skipped** when the optional ``pysweph`` test extra is
not installed: the top-level :func:`pytest.importorskip` gate raises
``pytest.skip.Exception`` at collection time so a bare ``pytest tests/``
reports the harness as SKIPPED rather than ERRORED.
"""

from __future__ import annotations

import math

import pytest

# Module-level skip-if-missing gate + named import for mypy --strict.
# Mypy honours [tool.mypy.overrides] module = ["swisseph.*"] / ignore_missing_imports
# for direct `import swisseph` statements only, not for `swe = importorskip(...)`
# bindings. Same dual-import pattern as ``tests/test_lilith_cross_check.py``.
pytest.importorskip("swisseph")
import swisseph as swe

_MIN_SWE_VERSION = "2.10"
if not str(swe.version).startswith(_MIN_SWE_VERSION):
    pytest.skip(
        f"swisseph C-library version {swe.version!r} below required "
        f"{_MIN_SWE_VERSION}.x (pyproject [test] pin: pysweph>=2.10.3.6)",
        allow_module_level=True,
    )

from ketu.ephemeris.coordinates import mean_obliquity
from ketu.ephemeris.time import sidereal_time

# ---------------------------------------------------------------------------
# Tolerances — see lst-audit-report.md §6-7 (Verdict: TIGHTEN)
# ---------------------------------------------------------------------------

# Verdict: TIGHTEN. Apparent-GST tightening (mean GMST + equation of
# equinoxes) yields max |drift| = 2.05 arcsec across 1900-2100 sample range
# (residual driven by the 4-term truncated nutation series in
# coordinates.nutation; full IAU 2000A is a v1.2 investment). 5.0 arcsec
# is 2.4× the achieved precision — fails CI if the mean-vs-apparent
# semantic regression returns, while leaving headroom for future nutation
# refinement that should TIGHTEN this number, never loosen it.
TOL_GMST_ARCSEC = 5.0

# coordinates.mean_obliquity is the IAU 2006 polynomial; empirical max
# drift = 0.063 arcsec across 1900-2100. 0.1 arcsec gives 1.6× headroom —
# guards future regressions without triggering on the current floor.
# DO NOT widen: <0.1 arcsec is a free precision win and any drift above
# would indicate an unintentional formula change.
TOL_OBLIQUITY_ARCSEC = 0.1

# Polar-boundary ASC fence: HOU-01 spec is <60 arcsec. We assert at 50″
# (10″ headroom) so any future regression triggers a test failure BEFORE
# we ship below spec. The 2024-06-21 lat=66.5° sample is a known Placidus
# polar singularity (dASC/dARMC ~70″/1″ near horizon-pole alignment);
# post-tightening the empirical max here is 8.7 arcsec, comfortably under
# the 50″ assertion.
TOL_POLAR_ASC_ARCSEC = 50.0

# ---------------------------------------------------------------------------
# Sample dates spanning the v1.1 valid range 1900-2050 plus margin
# ---------------------------------------------------------------------------

SAMPLE_DATES: list[tuple[str, float]] = [
    ("1900-01-01_12h_UT", 2415021.0),
    ("J2000_2000-01-01_12h_TT", 2451545.0),
    ("2024-06-21_0h_UT", 2460482.5),
    ("2050-12-31_12h_UT", 2470204.0),
    ("2100-01-01_12h_UT", 2488069.5),
]

POLAR_BOUNDARY_LAT_DEG = 66.5


def _signed_arcsec_delta(a_deg: float, b_deg: float) -> float:
    """Signed (a - b) wrapped to (-180, +180] degrees, expressed in arcseconds."""
    delta = ((a_deg - b_deg + 180.0) % 360.0) - 180.0
    return delta * 3600.0


# ---------------------------------------------------------------------------
# Test 1 — apparent GST drift vs swe.sidtime
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("label,jd", SAMPLE_DATES)
def test_sidereal_time_matches_swisseph_within_tolerance(label: str, jd: float) -> None:
    """ketu.sidereal_time matches swe.sidtime within TOL_GMST_ARCSEC.

    swe.sidtime returns apparent GST in hours; multiply by 15 to compare
    with sidereal_time which returns degrees. Both are apparent GST after
    the Plan 10-01 tightening.
    """
    ketu_gst_deg = sidereal_time(jd, 0.0)
    swe_gst_deg = swe.sidtime(jd) * 15.0
    delta_arcsec = abs(_signed_arcsec_delta(ketu_gst_deg, swe_gst_deg))
    assert delta_arcsec < TOL_GMST_ARCSEC, (
        f"{label}: GST drift = {delta_arcsec:.4f} arcsec ≥ {TOL_GMST_ARCSEC} "
        f"(ketu={ketu_gst_deg:.10f}, swe={swe_gst_deg:.10f})"
    )


# ---------------------------------------------------------------------------
# Test 2 — mean obliquity drift vs swe.calc_ut(ECL_NUT)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("label,jd", SAMPLE_DATES)
def test_mean_obliquity_matches_swisseph_within_tolerance(label: str, jd: float) -> None:
    """ketu.mean_obliquity matches swe within TOL_OBLIQUITY_ARCSEC.

    swe.calc_ut(jd, swe.ECL_NUT) returns ((eps_true, eps_mean, nut_lon,
    nut_obl, 0, 0), retflag, serr); mean obliquity is at index [0][1].
    Defensive index-based unpack matches Phase 8 cross-check pattern.
    """
    ketu_eps_deg = float(mean_obliquity(jd))
    ret = swe.calc_ut(jd, swe.ECL_NUT)
    swe_eps_deg = ret[0][1]  # mean obliquity
    delta_arcsec = abs(ketu_eps_deg - swe_eps_deg) * 3600.0
    assert delta_arcsec < TOL_OBLIQUITY_ARCSEC, (
        f"{label}: obliquity drift = {delta_arcsec:.6f} arcsec ≥ "
        f"{TOL_OBLIQUITY_ARCSEC} (ketu={ketu_eps_deg:.10f}, "
        f"swe={swe_eps_deg:.10f})"
    )


# ---------------------------------------------------------------------------
# Test 3 — longitude offset linearity
# ---------------------------------------------------------------------------


def test_sidereal_time_longitude_offset_is_pure_addition() -> None:
    """LST = (GST + longitude) % 360 to <1e-9 deg.

    Catches future bugs where longitude is swapped, signed wrong, or
    mis-applied in the formula. Cheap correctness check.
    """
    jd_j2000 = 2451545.0
    gst = sidereal_time(jd_j2000, 0.0)
    for lon in (0.0, 90.0, -45.0):
        lst = sidereal_time(jd_j2000, lon)
        expected = (gst + lon) % 360.0
        assert abs(lst - expected) < 1e-9, (
            f"lon={lon}: LST={lst} vs expected={expected} (delta={lst - expected})"
        )


# ---------------------------------------------------------------------------
# Test 4 — polar-boundary ASC regression fence (HOU-01 end-to-end)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("label,jd", SAMPLE_DATES)
def test_asc_error_within_spec_at_polar_boundary(label: str, jd: float) -> None:
    """End-to-end ASC fence at lat=66.5° (Arctic Circle / Placidus boundary).

    This is the **automatic regression fence** referenced in
    ``lst-audit-report.md`` §5. It propagates ketu's GST and mean
    obliquity through ``swe.houses_armc`` (Placidus) at the polar
    boundary and asserts the resulting ASC error stays under
    :data:`TOL_POLAR_ASC_ARCSEC` = 50″ (10″ headroom vs HOU-01 60″
    spec).

    ``swe.houses_armc(armc, lat, eps, hsys)`` accepts ARMC in **degrees**
    (NOT hours — Pitfall 7 from research). Both calls feed the same
    Placidus algorithm; the only inputs differing are ARMC and eps,
    so any delta is attributable purely to ketu primitive drift.
    """
    armc_ketu_deg = sidereal_time(jd, 0.0)
    eps_ketu_deg = float(mean_obliquity(jd))

    # Reference: swisseph's own GST + obliquity (mean, to match ketu's eps choice).
    armc_swe_deg = swe.sidtime(jd) * 15.0
    ret = swe.calc_ut(jd, swe.ECL_NUT)
    eps_swe_deg = ret[0][1]  # mean obliquity at index 1

    _, ascmc_ketu = swe.houses_armc(armc_ketu_deg, POLAR_BOUNDARY_LAT_DEG, eps_ketu_deg, b"P")
    asc_ketu = ascmc_ketu[0]

    _, ascmc_swe = swe.houses_armc(armc_swe_deg, POLAR_BOUNDARY_LAT_DEG, eps_swe_deg, b"P")
    asc_swe = ascmc_swe[0]

    delta_asc_arcsec = abs(_signed_arcsec_delta(asc_ketu, asc_swe))
    assert delta_asc_arcsec < TOL_POLAR_ASC_ARCSEC, (
        f"{label} lat={POLAR_BOUNDARY_LAT_DEG} ASC error "
        f"{delta_asc_arcsec:.3f} arcsec ≥ {TOL_POLAR_ASC_ARCSEC} "
        f"(spec: 60.0). asc_ketu={asc_ketu:.6f} asc_swe={asc_swe:.6f}"
    )
