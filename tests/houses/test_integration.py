"""End-to-end ``calculate_houses`` tests — dispatch, polar_fallback, dtype shape.

Covers HOU-02 (registry dispatch with no if/elif), HOU-05
(``HOUSES_DTYPE`` array), HOU-06 (``polar_fallback`` semantics) and HOU-09
(≥10 reference fixtures × 3 systems oracle agreement).

HOU-09 coverage gate command (run via Makefile target
``make houses-coverage``):

    pytest tests/houses/ --cov=ketu.houses --cov-fail-under=95 \
        --cov-report=term-missing
"""
from __future__ import annotations

import sys
from typing import Any

import numpy as np
import pytest

from ketu.houses import (
    HOUSES_DTYPE,
    SYSTEMS,
    HighLatitudeError,
    calculate_houses,
)


# Non-polar reference labels — the 8 charts where all 3 systems should
# agree with the swisseph oracle below 1 arcmin (the 2 polar charts at
# lat=70/80 are excluded since Placidus/Koch error there).
NON_POLAR_LABELS = [
    "J2000_Greenwich", "J2000_Paris", "J2000_Sydney",
    "J2000_Tokyo", "J2000_BuenosAires", "J2000_Equator",
    "1900_NewYork", "2050_Reykjavik",
]

# Per-system, per-chart cusp tolerance (arcmin). Matches Plans 10-04
# (Placidus) and 10-05 (Koch + Porphyry) inherited precision floors.
# The three systems differ in their sensitivity to the eps_mean vs
# eps_true mismatch in :func:`ketu.houses.ascmc.compute_ascmc`:
#
#   Placidus: ASC closed-form, then iterated cusps. Drift ~51″ at
#       Reykjavik (lat 64°N), under 10″ elsewhere.
#   Koch:     cos(lat) divisor amplifies eps drift to ~148″ at
#       Reykjavik. Pinned at 3 arcmin in Plan 10-05.
#   Porphyry: closed-form trisection. ASC is the ONLY input; drift
#       inherits from ASC drift (~51″ Reykjavik, < 10″ elsewhere).
#
# The 3-arcmin envelope absorbs all three at Reykjavik (the worst case).
# A future Plan 10-03 upgrade to eps_true would collapse all three to
# ~1″ everywhere — caught by the existing Plan 10-04/10-05 inherited-
# precision-floor regression tests.
NON_POLAR_TOL_ARCMIN = 3.0


def test_systems_has_placidus_koch_porphyry_at_import_time() -> None:
    """All 3 built-in systems are registered when ketu.houses is imported."""
    for name in ("placidus", "koch", "porphyry"):
        assert name in SYSTEMS, (
            f"{name} not in SYSTEMS={sorted(SYSTEMS.keys())}"
        )


def test_calculate_houses_returns_houses_dtype_array() -> None:
    """Scalar input returns 0-d HOUSES_DTYPE array with cusps shape (12,)."""
    r = calculate_houses(2451545.0, 48.8566, 2.3522, system="placidus")
    assert r.dtype == HOUSES_DTYPE
    assert r["cusps"].shape == (12,)
    assert 0.0 <= float(r["asc"]) < 360.0
    assert 0.0 <= float(r["mc"]) < 360.0
    assert 0.0 <= float(r["armc"]) < 360.0


def test_calculate_houses_meta_fields_populated() -> None:
    """``jd``, ``lat``, ``lon``, ``system`` round-trip with case normalisation."""
    r = calculate_houses(2451545.0, 48.8566, 2.3522, system="Placidus")
    assert float(r["jd"]) == 2451545.0
    assert float(r["lat"]) == 48.8566
    assert float(r["lon"]) == 2.3522
    # System field normalised to lowercase regardless of input case.
    assert str(r["system"]) == "placidus"


def test_calculate_houses_meta_fields_uppercase_input() -> None:
    """``system='PLACIDUS'`` (all-caps) also normalises to lowercase."""
    r = calculate_houses(2451545.0, 48.8566, 2.3522, system="PLACIDUS")
    assert str(r["system"]) == "placidus"


@pytest.mark.parametrize("system", ["placidus", "koch", "porphyry"])
@pytest.mark.parametrize("label", NON_POLAR_LABELS)
def test_calculate_houses_all_3_systems_match_oracle(
    system: str,
    label: str,
    reference_charts: list[dict[str, Any]],
    loaded_reference_snapshot: dict[str, Any],
) -> None:
    """All 3 systems agree with swisseph snapshot on every non-polar chart."""
    chart = next(c for c in reference_charts if c["label"] == label)
    chart_snap = loaded_reference_snapshot["charts"][label]
    snap_systems = chart_snap["systems"]
    if system not in snap_systems:
        pytest.skip(f"snapshot lacks {system} entry for {label}")
    snap_entry = snap_systems[system]
    if snap_entry.get("polar"):
        pytest.skip(f"{label} is polar for {system}; skipping")
    snap_cusps = np.asarray(snap_entry["cusps"], dtype=np.float64)

    r = calculate_houses(
        chart["jd"], chart["lat"], chart["lon"], system=system
    )
    cusps = np.asarray(r["cusps"], dtype=np.float64)
    # Modular signed difference, then take absolute value — handles 0/360 wrap.
    deltas = np.abs(((cusps - snap_cusps + 180.0) % 360.0) - 180.0)
    tol_deg = NON_POLAR_TOL_ARCMIN / 60.0
    for i in range(12):
        assert deltas[i] < tol_deg, (
            f"{system} {label} cusp {i+1} drift "
            f"{deltas[i] * 60.0:.3f} arcmin (tolerance "
            f"{NON_POLAR_TOL_ARCMIN} arcmin)"
        )


def test_calculate_houses_unknown_system_raises_value_error() -> None:
    """Unknown system surfaces via ``get_system`` ValueError."""
    with pytest.raises(ValueError, match="unknown house system"):
        calculate_houses(
            2451545.0, 48.8566, 2.3522, system="nonexistent_xyz",
        )


def test_calculate_houses_invalid_polar_fallback_raises_value_error() -> None:
    """Unknown polar_fallback value surfaces with informative error."""
    with pytest.raises(ValueError, match="polar_fallback"):
        calculate_houses(
            2451545.0, 48.8566, 2.3522,
            system="placidus",
            polar_fallback="invalid_choice",  # type: ignore[arg-type]
        )


def test_calculate_houses_polar_default_raises_high_latitude_error() -> None:
    """``polar_fallback='raise'`` (default) raises HighLatitudeError."""
    with pytest.raises(HighLatitudeError) as exc_info:
        calculate_houses(2451545.0, 80.0, 0.0, system="placidus")
    assert exc_info.value.lat == 80.0
    assert exc_info.value.system == "placidus"


def test_calculate_houses_polar_porphyry_substitutes_for_polar_only() -> None:
    """Vectorised: 1 mid-lat + 1 polar; mid → placidus, polar → porphyry; no NaN."""
    jds = np.array([2451545.0, 2451545.0])
    lats = np.array([48.8566, 80.0])
    lons = np.array([2.3522, 0.0])
    r = calculate_houses(
        jds, lats, lons,
        system="placidus", polar_fallback="porphyry",
    )
    assert r.shape == (2,)
    assert r["cusps"].shape == (2, 12)
    assert not np.isnan(r["cusps"]).any(), (
        "polar_fallback='porphyry' must produce no NaN"
    )


def test_calculate_houses_polar_porphyry_koch_no_nan() -> None:
    """Same fallback semantics for Koch: substitution at polar lat → no NaN."""
    jds = np.array([2451545.0, 2451545.0])
    lats = np.array([48.8566, 70.0])
    lons = np.array([2.3522, 0.0])
    r = calculate_houses(
        jds, lats, lons,
        system="koch", polar_fallback="porphyry",
    )
    assert not np.isnan(r["cusps"]).any()


def test_calculate_houses_polar_default_raise_for_koch() -> None:
    """Koch also raises by default at polar latitudes."""
    with pytest.raises(HighLatitudeError):
        calculate_houses(2451545.0, 70.0, 0.0, system="koch")


def test_calculate_houses_porphyry_at_polar_does_not_raise() -> None:
    """Porphyry alone at polar lat: no fallback needed; mathematically defined."""
    # Porphyry is the polar fallback path itself; calling it directly at
    # polar lat must succeed with finite cusps (no NaN, no error).
    r = calculate_houses(2451545.0, 80.0, 0.0, system="porphyry")
    assert not np.isnan(r["cusps"]).any()


def test_calculate_houses_vectorized_preserves_leading_shape() -> None:
    """N inputs → N-shape output."""
    n = 5
    jds = np.full(n, 2451545.0)
    lats = np.linspace(0.0, 50.0, n)
    lons = np.zeros(n)
    r = calculate_houses(jds, lats, lons, system="placidus")
    assert r.shape == (n,)
    assert r["cusps"].shape == (n, 12)


def test_calculate_houses_2d_input_shape_preserved() -> None:
    """``(2, 3)`` input shape → output shape ``(2, 3)``, cusps ``(2, 3, 12)``."""
    jds = np.full((2, 3), 2451545.0)
    lats = np.full((2, 3), 48.8566)
    lons = np.full((2, 3), 2.3522)
    r = calculate_houses(jds, lats, lons, system="placidus")
    assert r.shape == (2, 3)
    assert r["cusps"].shape == (2, 3, 12)


def test_calculate_houses_no_runtime_swisseph_import() -> None:
    """Sanity: ketu.houses must not import swisseph (test-only AGPL constraint).

    Ratchet test against accidental future "let me just import for a
    fixture" change. The swisseph oracle lives in
    :mod:`tests.houses.conftest` (test-only); production code under
    :mod:`ketu.houses` must remain swisseph-free.
    """
    # Re-import ketu.houses fresh-ish (already imported, but verify swisseph
    # isn't anywhere in its import surface).
    import ketu.houses  # noqa: F401
    import ketu.houses.api  # noqa: F401
    for mod_name, mod in list(sys.modules.items()):
        if mod_name.startswith("ketu.houses") and mod is not None:
            names = [
                n for n in dir(mod)
                if n.startswith("swe_") or n == "swisseph" or n == "swe"
            ]
            # Allow names like "swe_oracle" only in test files (this test
            # is in tests/); in ketu.houses.* nothing should match.
            assert not names, (
                f"{mod_name} unexpectedly exposes swisseph-related "
                f"names: {names}"
            )


def test_calculate_houses_polar_fallback_polar_cusps_match_porphyry_directly() -> None:
    """Cusps for polar element under fallback == direct Porphyry call.

    Validates that the fallback substitution doesn't accidentally mangle
    the cusp values during ``np.where`` element selection.
    """
    # 2 elements: one polar (80°N), one mid-lat. Under fallback='porphyry',
    # the polar element's cusps must equal direct calculate_houses(80, ...,
    # system='porphyry').
    jds = np.array([2451545.0, 2451545.0])
    lats = np.array([48.8566, 80.0])
    lons = np.array([2.3522, 0.0])
    r_fallback = calculate_houses(
        jds, lats, lons,
        system="placidus", polar_fallback="porphyry",
    )
    r_direct_polar = calculate_houses(
        2451545.0, 80.0, 0.0, system="porphyry",
    )
    polar_cusps_fallback = np.asarray(r_fallback["cusps"])[1]
    polar_cusps_direct = np.asarray(r_direct_polar["cusps"])
    deltas = np.abs(
        ((polar_cusps_fallback - polar_cusps_direct + 180.0) % 360.0) - 180.0
    )
    assert (deltas < 1e-9).all(), (
        f"polar fallback substitution mismatch: max delta={deltas.max():.3e}°"
    )


def test_calculate_houses_system_field_preserved_under_fallback() -> None:
    """``system`` field reflects user request, even when porphyry was substituted.

    Documents the contract: the cusps reflect the actual computation, but
    the ``system`` field reflects the user's request. Plan 11 (CLI) will
    rely on this.
    """
    r = calculate_houses(
        np.array([2451545.0, 2451545.0]),
        np.array([48.8566, 80.0]),
        np.array([2.3522, 0.0]),
        system="placidus", polar_fallback="porphyry",
    )
    # All elements report 'placidus' (user's request), even though the
    # 2nd element's cusps are Porphyry-computed.
    assert all(str(s) == "placidus" for s in r["system"])
