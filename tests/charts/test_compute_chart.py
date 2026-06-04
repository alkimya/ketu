"""Integration tests for :func:`ketu.charts.compute_chart` (positions + houses).

Plan 14-02 wires positions + inline houses + sentinel aspect block. Tests
cover:

- return dtype is :data:`CHART_DTYPE`,
- metadata round-trip (``jd``, ``lat``, ``lon``, ``system``),
- houses-inline equivalence vs :func:`ketu.houses.calculate_houses` (D-03),
- body positions cross-checked against the underlying vectorised
  primitive (``calc_planet_position_batch``),
- retrograde sign on :data:`body_speeds` (Mercury retrograde 2025-03-25),
- diagonal-sentinel ratchet on the populated aspect block,
- polar fallback pass-through (raise + porphyry, D-11),
- AGPL boundary ratchet (no swisseph in ``ketu.charts.*``).

The dense aspect block is wired by plan 14-03; off-diagonal contents
are exhaustively covered in :mod:`tests.charts.test_aspect_matrix`. The
diagonal-only ratchet here is the structural counterpart that keeps the
"a body has no aspect with itself" invariant pinned to ``compute_chart``
itself (D-06).
"""
from __future__ import annotations

import sys
import warnings
from typing import Any

import numpy as np
import pytest

from ketu.charts import CHART_DTYPE, compute_chart
from ketu.ephemeris.planets import calc_planet_position_batch
from ketu.houses import HighLatitudeError, calculate_houses

# Cross-checking ``compute_chart`` houses block against a direct
# ``calculate_houses`` call: same input pipeline, identical fp64 values
# in memory (compute_chart calls calculate_houses once and copies the
# fields directly), so the contract is bit-exact equality (D-03
# "houses inline = bit-for-bit"). We test with strict equality below
# (np.testing.assert_array_equal / `==`) rather than a numerical
# tolerance — any drift would be a regression introduced by an
# intermediate cast in the copy pipeline.

# Tolerance for cross-checking ``compute_chart["body_lons"]`` against the
# underlying ``calc_planet_position_batch`` primitive: identical
# computation, no precision loss expected (bit-exact in practice; we use
# 1e-12 deg for fp64 round-off headroom).
BODY_LONS_INLINE_TOL_DEG = 1e-12

# Mercury retrograde epoch verified at this date via
# calc_planet_position_batch (lon_speed ≈ -0.87 deg/day on 2025-03-25).
MERCURY_RETRO_JD = 2460759.5  # 2025-03-25T00:00:00 UTC


# ---------------------------------------------------------------------------
# Return dtype + metadata round-trip
# ---------------------------------------------------------------------------


def test_compute_chart_returns_chart_dtype() -> None:
    """Scalar input returns a 0-d :data:`CHART_DTYPE` element."""
    chart = compute_chart(2451545.0, 48.86, 2.35)
    assert chart.dtype == CHART_DTYPE
    assert chart.shape == ()
    assert chart["body_lons"].shape == (14,)
    assert chart["cusps"].shape == (12,)
    assert chart["aspect_matrix"].shape == (14, 14)
    assert chart["aspect_orbs"].shape == (14, 14)


def test_compute_chart_meta_fields_populated() -> None:
    """``jd``, ``lat``, ``lon``, ``system`` round-trip from inputs."""
    chart = compute_chart(2451545.0, 48.8566, 2.3522, system="placidus")
    assert float(chart["jd"]) == 2451545.0
    assert float(chart["lat"]) == 48.8566
    assert float(chart["lon"]) == 2.3522
    assert str(chart["system"]) == "placidus"


def test_compute_chart_meta_fields_lowercased_system() -> None:
    """``system='PLACIDUS'`` normalises to lowercase (mirrors calculate_houses)."""
    chart = compute_chart(2451545.0, 48.8566, 2.3522, system="PLACIDUS")
    assert str(chart["system"]) == "placidus"


# ---------------------------------------------------------------------------
# Houses inline equivalence (D-03)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("system", ["placidus", "koch", "porphyry"])
@pytest.mark.parametrize(
    "label",
    [
        "J2000_Greenwich", "J2000_Paris", "J2000_Sydney",
        "J2000_Tokyo", "J2000_BuenosAires", "J2000_Equator",
        "1900_NewYork", "2050_Reykjavik",
    ],
)
def test_compute_chart_houses_inline_matches_calculate_houses(
    system: str,
    label: str,
    reference_charts: list[dict[str, Any]],
) -> None:
    """D-03 ratchet: the houses block of CHART_DTYPE matches calculate_houses bit-for-bit."""
    chart_meta = next(c for c in reference_charts if c["label"] == label)
    jd, lat, lon = chart_meta["jd"], chart_meta["lat"], chart_meta["lon"]

    chart = compute_chart(jd, lat, lon, system=system)
    houses = calculate_houses(jd, lat, lon, system=system)

    # cusps (12,) — strict bit-for-bit equality.
    np.testing.assert_array_equal(
        np.asarray(chart["cusps"]),
        np.asarray(houses["cusps"]),
        err_msg=f"{system}/{label}: cusps not bit-exact (D-03 ratchet)",
    )
    # asc/mc/armc/vertex (scalar) — strict bit-for-bit equality.
    for field in ("asc", "mc", "armc", "vertex"):
        chart_val = float(chart[field])
        houses_val = float(houses[field])
        assert chart_val == houses_val, (
            f"{system}/{label}: {field} not bit-exact "
            f"(D-03 ratchet); chart={chart_val!r} vs houses={houses_val!r}"
        )


# ---------------------------------------------------------------------------
# Body positions wired to calc_planet_position_batch
# ---------------------------------------------------------------------------


def test_compute_chart_body_lons_match_underlying_primitive() -> None:
    """body_lons / lats / speeds reproduce ``calc_planet_position_batch`` for J2000_Paris."""
    jd, lat, lon = 2451545.0, 48.8566, 2.3522
    chart = compute_chart(jd, lat, lon)

    jd_arr = np.array([jd], dtype=np.float64)
    for body_id in range(14):
        batch = calc_planet_position_batch(jd_arr, body_id)
        # batch shape (1, 6); columns [lon, lat, dist, lon_speed, lat_speed, dist_speed]
        assert abs(
            float(chart["body_lons"][body_id]) - float(batch[0, 0])
        ) < BODY_LONS_INLINE_TOL_DEG, (
            f"body {body_id}: lon drift > {BODY_LONS_INLINE_TOL_DEG}"
        )
        assert abs(
            float(chart["body_lats"][body_id]) - float(batch[0, 1])
        ) < BODY_LONS_INLINE_TOL_DEG, (
            f"body {body_id}: lat drift > {BODY_LONS_INLINE_TOL_DEG}"
        )
        assert abs(
            float(chart["body_speeds"][body_id]) - float(batch[0, 3])
        ) < BODY_LONS_INLINE_TOL_DEG, (
            f"body {body_id}: speed drift > {BODY_LONS_INLINE_TOL_DEG}"
        )


def test_compute_chart_body_speeds_negative_for_retrograde() -> None:
    """D-02 ratchet: ``body_speeds < 0`` flags retrograde (Mercury 2025-03-25)."""
    chart = compute_chart(MERCURY_RETRO_JD, 48.8566, 2.3522)
    mercury_speed = float(chart["body_speeds"][2])  # body_id 2 == Mercury
    assert mercury_speed < 0.0, (
        f"Mercury was expected retrograde at JD {MERCURY_RETRO_JD} "
        f"(2025-03-25); got speed = {mercury_speed:+.4f} deg/day"
    )


# ---------------------------------------------------------------------------
# Aspect block diagonal ratchet (D-06)
# ---------------------------------------------------------------------------


def test_compute_chart_aspect_matrix_diagonal_is_sentinel() -> None:
    """D-06 ratchet: a body has no aspect with itself.

    The off-diagonal entries are now populated by ``_build_aspect_matrix``
    (plan 14-03) and exhaustively covered in
    :mod:`tests.charts.test_aspect_matrix`. This test pins the
    structural invariant on ``compute_chart`` itself: regardless of the
    aspect set requested, the diagonal of ``aspect_matrix`` must stay at
    ``-1`` and the diagonal of ``aspect_orbs`` must stay at ``NaN``.
    """
    chart = compute_chart(2451545.0, 48.8566, 2.3522)
    for i in range(14):
        assert int(chart["aspect_matrix"][i, i]) == -1, (
            f"aspect_matrix[{i}, {i}] expected -1 (sentinel); "
            f"got {int(chart['aspect_matrix'][i, i])}"
        )
        assert np.isnan(chart["aspect_orbs"][i, i]), (
            f"aspect_orbs[{i}, {i}] expected NaN (sentinel); "
            f"got {float(chart['aspect_orbs'][i, i])}"
        )


# ---------------------------------------------------------------------------
# Polar fallback pass-through (D-11)
# ---------------------------------------------------------------------------


def test_compute_chart_polar_default_raises() -> None:
    """D-11 ratchet: ``polar_fallback='raise'`` (default) propagates HighLatitudeError."""
    with pytest.raises(HighLatitudeError):
        compute_chart(2451545.0, 80.0, 0.0)


def test_compute_chart_polar_porphyry_substitutes() -> None:
    """``polar_fallback='porphyry'`` substitutes Porphyry cusps; system field unchanged."""
    chart = compute_chart(
        2451545.0, 80.0, 0.0,
        system="placidus", polar_fallback="porphyry",
    )
    # No NaN in cusps (Porphyry is mathematically defined at polar lat).
    assert not np.isnan(chart["cusps"]).any()
    # Requested system preserved (cusps reflect actual computation, but
    # ``system`` reflects the user's request; mirrors calculate_houses).
    assert str(chart["system"]) == "placidus"


@pytest.mark.parametrize(
    ("label", "lat", "lon"),
    [
        ("non_polar_paris", 48.8566, 2.3522),
        ("polar_lat_80",    80.0,    0.0),
    ],
)
def test_compute_chart_polar_fallback_invalid_raises_value_error(
    label: str, lat: float, lon: float,
) -> None:
    """Invalid ``polar_fallback`` propagates ValueError regardless of latitude.

    Pin both validation trajectories: at non-polar latitudes the error
    must surface (calculate_houses currently validates eagerly, before
    the polar check), AND at polar latitudes the error must surface
    (the polar branch is also reached). If a future refactor moves
    validation into the polar branch only, the non-polar case will go
    red here and force the regression to be addressed deliberately —
    this is the IN-04 ratchet.
    """
    del label  # only used for pytest IDs
    with pytest.raises(ValueError, match="polar_fallback"):
        compute_chart(
            2451545.0, lat, lon,
            polar_fallback="invalid_choice",  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# AGPL boundary ratchet — copy of tests/houses/test_integration.py:214-237
# (s/houses/charts/) per PATTERNS § 8.5.
# ---------------------------------------------------------------------------


def test_compute_chart_no_runtime_swisseph_import() -> None:
    """AGPL boundary ratchet: ``ketu.charts.*`` must not import swisseph.

    Test-only AGPL constraint: the swisseph oracle lives in
    :mod:`tests.charts.conftest` (which re-exports
    :mod:`tests.houses.conftest`); production code under
    :mod:`ketu.charts` must remain swisseph-free.
    """
    import ketu.charts  # noqa: F401
    import ketu.charts.api  # noqa: F401
    import ketu.charts.core  # noqa: F401
    for mod_name, mod in list(sys.modules.items()):
        if mod_name.startswith("ketu.charts") and mod is not None:
            names = [
                n for n in dir(mod)
                if n.startswith("swe_") or n == "swisseph" or n == "swe"
            ]
            assert not names, (
                f"{mod_name} unexpectedly exposes swisseph-related "
                f"names: {names}"
            )


# ---------------------------------------------------------------------------
# RuntimeWarning ratchet — observable-level guard for the heliocentric
# latitude div/0 (z/r when r→0 for the Sun). The source-level guard lives in
# tests/test_coverage_improvements.py
# (test_vectorized_path_r_zero_no_warning_no_nan_bounded, QAL-11
# np.maximum(r, 1e-10) floor); this is the integration counterpart asserting
# no RuntimeWarning ever reaches a `compute_chart` caller's REPL.
# ---------------------------------------------------------------------------


def test_compute_chart_emits_no_runtime_warning() -> None:
    """`compute_chart` must not emit any RuntimeWarning (div/0 ratchet).

    Promotes every RuntimeWarning to an error for the duration of the call
    so the pre-existing ``invalid value encountered in divide`` warning
    (heliocentric latitude ``z/r`` for the Sun, where ``r == 0``) can never
    silently return — the field is unused downstream but the warning used to
    pollute the REPL on every chart computation. Body ecliptic longitudes
    flow through a separate, correct path and stay finite.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("error", category=RuntimeWarning)
        chart = compute_chart(2451545.0, 48.8566, 2.3522)
    assert np.all(np.isfinite(chart["body_lons"])), chart["body_lons"]
