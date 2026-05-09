"""Smoke tests for the oracle harness in ``tests/houses/conftest.py``.

Pure-infra tests: NO dependencies on ``ketu.houses`` production code
(which doesn't exist until Plan 10-03 lands). The conftest's module-level
:func:`pytest.importorskip` gate handles the swisseph-missing case wholesale,
so these tests either all run (swisseph installed) or all skip (absent) —
never partially.

Coverage:

- ``test_reference_charts_has_at_least_ten_entries`` — HOU-09 floor of 10.
- ``test_reference_charts_includes_polar_latitudes`` — HOU-09 explicit
  70°/80° requirement.
- ``test_swe_oracle_returns_12_cusps_at_paris_j2000`` — happy-path shape
  check on the high-level helper.
- ``test_swe_oracle_polar_returns_error_marker`` — Placidus polar boundary
  raises :class:`swisseph.Error` and the helper translates it to
  ``{"error": ..., "polar": True}``.
- ``test_swe_oracle_armc_isolates_armc_from_sidereal_time`` — ARMC-direct
  helper accepts user-supplied ARMC (used by Plans 03/04/05 to factor out
  GST drift).
- ``test_loaded_reference_snapshot_matches_oracle`` — committed JSON matches
  live oracle within 1e-9 deg (deterministic swisseph; any drift signals
  an environmental issue).
"""

from __future__ import annotations

import numpy as np

from ketu.ephemeris.coordinates import mean_obliquity

from .conftest import swe_oracle, swe_oracle_armc


def test_reference_charts_has_at_least_ten_entries(reference_charts):
    assert len(reference_charts) >= 10, (
        f"HOU-09 requires ≥10 reference fixtures, got {len(reference_charts)}"
    )


def test_reference_charts_includes_polar_latitudes(reference_charts):
    lats = {abs(c["lat"]) for c in reference_charts}
    assert any(lat >= 70.0 for lat in lats), "HOU-09 requires lat=70°"
    assert any(lat >= 80.0 for lat in lats), "HOU-09 requires lat=80°"


def test_swe_oracle_returns_12_cusps_at_paris_j2000():
    result = swe_oracle(2451545.0, 48.8566, 2.3522, "placidus")
    assert result["cusps"].shape == (12,)
    assert 0.0 <= result["asc"] < 360.0
    assert 0.0 <= result["mc"] < 360.0


def test_swe_oracle_polar_returns_error_marker():
    # lat=80° is well beyond polar circle for Placidus — swisseph raises.
    result = swe_oracle(2451545.0, 80.0, 0.0, "placidus")
    assert "error" in result
    assert result.get("polar") is True


def test_swe_oracle_armc_isolates_armc_from_sidereal_time():
    """ARMC-direct API skips swe.sidtime — useful for Plans 03/04/05."""
    # mean_obliquity returns ``float | np.ndarray`` (vectorised); cast to
    # plain float for the scalar swe.houses_armc call.
    eps = float(mean_obliquity(2451545.0))
    result = swe_oracle_armc(0.0, 48.8566, eps, "placidus")  # armc=0 = meridian alignment
    assert result["cusps"].shape == (12,)


def test_loaded_reference_snapshot_matches_oracle(
    reference_charts, loaded_reference_snapshot
):
    """The committed JSON must match live oracle output within 1e-9 deg.

    swisseph is deterministic; any drift at this tolerance signals an
    environmental issue (e.g., a swisseph version or ephemeris-file change).
    """
    for chart in reference_charts:
        label = chart["label"]
        assert label in loaded_reference_snapshot["charts"], (
            f"Snapshot missing chart {label}"
        )
        for sys_name in (
            "placidus", "koch", "porphyry",
            "whole_sign", "equal", "regiomontanus",
        ):
            snap = loaded_reference_snapshot["charts"][label]["systems"][sys_name]
            live = swe_oracle(chart["jd"], chart["lat"], chart["lon"], sys_name)
            if "error" in snap:
                assert "error" in live, (
                    f"{label}/{sys_name}: snapshot has error but live does not"
                )
            else:
                np.testing.assert_allclose(
                    snap["cusps"],
                    live["cusps"],
                    atol=1e-9,
                    rtol=0,
                    err_msg=f"{label}/{sys_name} cusps drifted",
                )
                assert abs(snap["asc"] - live["asc"]) < 1e-9, (
                    f"{label}/{sys_name} asc drifted"
                )
                assert abs(snap["mc"] - live["mc"]) < 1e-9, (
                    f"{label}/{sys_name} mc drifted"
                )
