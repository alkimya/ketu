"""COMP-04 / ROADMAP success criterion #3 — composite oracle tests.

Three reference composite pairs are pinned as regression fixtures with
documented per-body tolerances. Self-consistency is the primary
validation (machine-precision round-trip via :func:`ketu.charts.compute_chart`
+ :func:`ketu.composite.calculate_composite`). Cross-validation against
Astro.com is deferred to Plan 17-04 close-out — Astro.com is bot-blocked
from automated retrieval AND defaults to the reference-place method whose
ASC/MC differ from the pure midpoint method (17-RESEARCH §Pitfall 5).

The headline output of ``pytest -v -s`` is the max ``|delta|`` per
fixture — required by ROADMAP criterion #3 ("documented max longitude
delta"). Mirrors :mod:`tests.synastry.test_oracle`'s max-``|orb|``
reporter pattern (Plan 16-03 precedent).

Tests run OFFLINE — no network access; the three couples are the same
Curie / Diana-Charles / Lennon-Ono birth records used by the synastry
oracles, with zero new birth-data research required.
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.charts import compute_chart
from ketu.cli._dates import parse_iso_utc
from ketu.composite import calculate_composite

from .conftest import ORACLE_SLUGS, load_oracle_fixture

#: Frozen 13-body axis order (D-08). Same ordering as
#: :data:`ketu.core.bodies` and the synastry axis indices 0..12 (the
#: synastry test indexes ASC at 13 and MC at 14 because synastry extends
#: the body axis; composite stores ASC/MC as separate scalar fields on
#: the output CHART_DTYPE, not in the body axis).
BODY_NAMES = [
    "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
    "Uranus", "Neptune", "Pluto", "Rahu", "Ketu", "Lilith",
]
BODY_INDEX = {name: i for i, name in enumerate(BODY_NAMES)}


def _build_charts(fixture: dict) -> tuple[np.ndarray, np.ndarray]:
    """Construct ``(chart_a, chart_b)`` by replaying compute_chart on fixture data.

    Mirrors :func:`tests.synastry.test_oracle._build_charts` — uses
    :func:`ketu.cli._dates.parse_iso_utc` (the canonical CLI ISO-8601 → JD
    helper) to convert the fixture's ``iso_date`` string directly into a
    Julian Date. ``parse_iso_utc`` returns a JD float (no separate
    ``utc_to_julian`` step required).

    Parameters
    ----------
    fixture : dict
        Composite oracle fixture as returned by :func:`load_oracle_fixture`.

    Returns
    -------
    tuple of numpy.ndarray
        ``(chart_a, chart_b)`` scalar :data:`ketu.charts.CHART_DTYPE` records.
    """
    a = fixture["chart_a"]
    b = fixture["chart_b"]
    jd_a = parse_iso_utc(a["iso_date"])
    jd_b = parse_iso_utc(b["iso_date"])
    chart_a = compute_chart(jd_a, a["lat"], a["lon"])
    chart_b = compute_chart(jd_b, b["lat"], b["lon"])
    return chart_a, chart_b


def _circular_delta(actual: float, expected: float) -> float:
    """Compute the absolute short-arc delta between two longitudes in [0, 360).

    Returns ``min(|actual - expected|, 360 - |actual - expected|)`` so a
    body at 359° vs an expected 1° reports a delta of 2° (NOT 358°).

    Parameters
    ----------
    actual : float
        Computed composite longitude (degrees).
    expected : float
        Fixture's expected longitude (degrees).

    Returns
    -------
    float
        Absolute short-arc delta in degrees, in [0, 180].
    """
    raw = abs(actual - expected)
    return min(raw, 360.0 - raw)


class TestComposeOracleBodies:
    """Per-body composite longitudes match the fixture within ``tolerance_deg``.

    Parametrized over all three slugs; reports max ``|delta|`` per fixture
    in ``pytest -v -s`` output (ROADMAP success criterion #3).
    """

    def test_body_lons_match_oracle(
        self,
        oracle_fixture: dict,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Composite body longitudes equal the pinned expected values."""
        chart_a, chart_b = _build_charts(oracle_fixture)
        composite = calculate_composite(chart_a, chart_b)

        deltas: list[tuple[str, float, float]] = []
        for body_name, spec in oracle_fixture["expected_composite"]["body_lons"].items():
            idx = BODY_INDEX[body_name]
            expected = float(spec["deg"])
            tolerance = float(spec["tolerance_deg"])
            actual = float(composite["body_lons"][idx])

            delta = _circular_delta(actual, expected)
            deltas.append((body_name, delta, tolerance))

            assert delta <= tolerance, (
                f"{oracle_fixture['name']} {body_name}: expected {expected}°, "
                f"got {actual}°, delta {delta:.6f}° > tolerance {tolerance}°"
            )

        max_body, max_delta, max_tol = max(deltas, key=lambda x: x[1])
        # capsys.disabled() so the line surfaces in pytest -v -s output
        # (matches synastry Plan 16-03's reporting pattern).
        with capsys.disabled():
            print(
                f"\n[oracle:{oracle_fixture['name']}] max body delta: "
                f"{max_delta:.6f}° on {max_body} (tolerance {max_tol}°)"
            )


class TestComposeOracleAngles:
    """Composite ASC and MC match the fixture for AA-rated pairs only.

    For Curie (Pierre's birth time C-rated), ASC and MC are EXCLUDED from
    the fixture's ``expected_composite`` block — the corresponding tests
    skip with the documented Rodden-rating-hygiene reason.
    """

    def test_asc_matches_oracle_if_present(self, oracle_fixture: dict) -> None:
        """Composite ASC equals the pinned expected value (AA-rated pairs only)."""
        if "asc" not in oracle_fixture["expected_composite"]:
            pytest.skip(
                f"{oracle_fixture['name']}: asc excluded (Rodden rating "
                f"uncertainty — see fixture notes)"
            )
        chart_a, chart_b = _build_charts(oracle_fixture)
        composite = calculate_composite(chart_a, chart_b)
        spec = oracle_fixture["expected_composite"]["asc"]
        expected = float(spec["deg"])
        tolerance = float(spec["tolerance_deg"])
        actual = float(composite["asc"])
        delta = _circular_delta(actual, expected)
        assert delta <= tolerance, (
            f"{oracle_fixture['name']} asc: expected {expected}°, got "
            f"{actual}°, delta {delta:.6f}° > tolerance {tolerance}°"
        )

    def test_mc_matches_oracle_if_present(self, oracle_fixture: dict) -> None:
        """Composite MC equals the pinned expected value (AA-rated pairs only)."""
        if "mc" not in oracle_fixture["expected_composite"]:
            pytest.skip(
                f"{oracle_fixture['name']}: mc excluded (Rodden rating "
                f"uncertainty — see fixture notes)"
            )
        chart_a, chart_b = _build_charts(oracle_fixture)
        composite = calculate_composite(chart_a, chart_b)
        spec = oracle_fixture["expected_composite"]["mc"]
        expected = float(spec["deg"])
        tolerance = float(spec["tolerance_deg"])
        actual = float(composite["mc"])
        delta = _circular_delta(actual, expected)
        assert delta <= tolerance, (
            f"{oracle_fixture['name']} mc: expected {expected}°, got "
            f"{actual}°, delta {delta:.6f}° > tolerance {tolerance}°"
        )


class TestOracleSchemaIntegrity:
    """Fixture schema is stable; cross-check field documents deferred status."""

    def test_schema_version_is_1(self, oracle_fixture: dict) -> None:
        """Fixture carries the v1 schema marker."""
        assert oracle_fixture["schema_version"] == 1

    def test_validation_source_documents_self_consistency(
        self, oracle_fixture: dict,
    ) -> None:
        """``validation_source`` mentions the self-consistency methodology."""
        vs = oracle_fixture["validation_source"]
        assert "self-consistency" in vs.lower(), (
            f"{oracle_fixture['name']}: validation_source does not document "
            f"self-consistency methodology: {vs!r}"
        )

    def test_cross_check_astro_com_deferred(self, oracle_fixture: dict) -> None:
        """``cross_check_astro_com`` records deferred manual cross-check.

        Plan 17-03 ships with ``performed=false``; Plan 17-04 close-out
        may flip this to ``true`` once a manual Astro.com verification is
        run. The ``tolerance_deg`` is advisory (0.1° = 6 arcmin) and not
        the headline self-consistency gate.
        """
        cc = oracle_fixture["cross_check_astro_com"]
        assert "performed" in cc, (
            f"{oracle_fixture['name']}: cross_check_astro_com missing 'performed'"
        )
        assert "tolerance_deg" in cc, (
            f"{oracle_fixture['name']}: cross_check_astro_com missing 'tolerance_deg'"
        )
        assert cc["tolerance_deg"] == 0.1, (
            f"{oracle_fixture['name']}: cross_check_astro_com.tolerance_deg "
            f"{cc['tolerance_deg']} != 0.1 (advisory cross-check band)"
        )


class TestOracleSlugsExported:
    """:data:`ORACLE_SLUGS` covers the three couples (single-source-of-truth ratchet)."""

    def test_three_slugs(self) -> None:
        """Exactly three slugs are exported, alphabetically ordered."""
        assert ORACLE_SLUGS == ("curie", "diana_charles", "lennon_ono")

    def test_load_oracle_fixture_round_trip(self) -> None:
        """Each slug loads a fixture whose ``name`` matches the slug."""
        for slug in ORACLE_SLUGS:
            fixture = load_oracle_fixture(slug)
            assert fixture["name"] == slug, (
                f"slug {slug!r} loaded a fixture whose name is "
                f"{fixture['name']!r}"
            )
