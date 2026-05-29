"""Oracle synastry tests — 3 hand-validated celebrity couples.

Loads ``tests/synastry/fixtures/oracle_*.json`` fixtures (curated in
Plan 16-03 Task 1) and asserts that :func:`ketu.synastry.calculate_synastry`
reproduces every documented expected aspect within the per-aspect
``orb_max_deg`` tolerance. Satisfies ROADMAP success criterion #4
(SYN-05): 3+ hand-validated synastry oracle couples.

Methodology (PRIMARY): self-consistency — both natal charts are
re-computed via :func:`ketu.charts.compute_chart` from the fixture's
ISO-UTC birth data, and :func:`ketu.synastry.calculate_synastry` is
re-run; the resulting filtered output MUST contain every expected
aspect within ``orb_max_deg``. Astro.com cross-validation is deferred
to Plan 16-05 manual follow-up (per fixture ``validation_source``).

Tests run OFFLINE — no network access (Astro.com anti-bot per
``16-RESEARCH.md`` Pitfall).
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import pytest

from ketu.charts import compute_chart
from ketu.cli._dates import parse_iso_utc
from ketu.core import aspects as ASPECTS
from ketu.synastry import calculate_synastry


# Body name -> 0..15 index in the synastry axis (14 canonical bodies + ASC + MC).
# Source: ketu.synastry.api._extend_body_data — indices 0..13 mirror
# ketu.core.bodies (incl. Chiron=13); 14 = ASC, 15 = MC.
_BODY_NAME_TO_INDEX = {
    "Sun": 0, "Moon": 1, "Mercury": 2, "Venus": 3, "Mars": 4,
    "Jupiter": 5, "Saturn": 6, "Uranus": 7, "Neptune": 8, "Pluto": 9,
    "Rahu": 10, "Ketu": 11, "Lilith": 12, "Chiron": 13, "ASC": 14, "MC": 15,
}

# Aspect name -> 0..13 canonical index (ketu.core.aspects).
_ASPECT_NAME_TO_INDEX = {
    name.decode(): idx for idx, name in enumerate(ASPECTS["name"])
}

# Mandatory fixture schema keys (validated per fixture).
_MANDATORY_KEYS = {
    "schema_version", "name", "rodden_a", "rodden_b",
    "chart_a", "chart_b", "expected_aspects",
    "validation_source", "tolerance_deg",
}

# Mandatory chart_a / chart_b sub-keys.
_MANDATORY_CHART_KEYS = {"subject_name", "iso_date", "lat", "lon", "source"}


def _build_charts(fixture: dict) -> tuple[np.ndarray, np.ndarray]:
    """Re-compute both natal charts from an oracle fixture's birth data.

    Uses ``polar_fallback='porphyry'`` defensively (none of the 3
    fixtures sit at extreme latitudes, but the flag guards against
    a future fixture addition at high latitude masking a synastry
    regression behind a :class:`ketu.houses.HighLatitudeError`).
    """
    jd_a = parse_iso_utc(fixture["chart_a"]["iso_date"])
    jd_b = parse_iso_utc(fixture["chart_b"]["iso_date"])
    chart_a = compute_chart(
        jd_a,
        fixture["chart_a"]["lat"],
        fixture["chart_a"]["lon"],
        polar_fallback="porphyry",
    )
    chart_b = compute_chart(
        jd_b,
        fixture["chart_b"]["lat"],
        fixture["chart_b"]["lon"],
        polar_fallback="porphyry",
    )
    return chart_a, chart_b


def _find_match(
    result: np.ndarray, body_a_idx: int, body_b_idx: int, aspect_idx: int,
) -> Optional[np.ndarray]:
    """Find the synastry row matching ``(body_a, body_b, aspect_type)``.

    Returns ``None`` if no matching row exists (test asserts presence).
    """
    mask = (
        (result["body_a"] == body_a_idx)
        & (result["body_b"] == body_b_idx)
        & (result["aspect_type"] == aspect_idx)
    )
    matches = result[mask]
    if len(matches) == 0:
        return None
    # First-aspect-wins guarantees at most one row per (a, b) — return scalar.
    return matches[0]


def test_oracle_fixture_schema_valid(oracle_fixture: dict) -> None:
    """Each oracle fixture carries every mandatory schema key."""
    missing = _MANDATORY_KEYS - set(oracle_fixture.keys())
    assert not missing, (
        f"fixture {oracle_fixture.get('name', '?')!r} missing keys: {missing}"
    )
    for side in ("chart_a", "chart_b"):
        chart = oracle_fixture[side]
        missing_chart = _MANDATORY_CHART_KEYS - set(chart.keys())
        assert not missing_chart, (
            f"fixture {oracle_fixture['name']!r} {side} missing keys: "
            f"{missing_chart}"
        )
    assert oracle_fixture["schema_version"] == 1, (
        f"fixture {oracle_fixture['name']!r}: schema_version != 1"
    )
    assert len(oracle_fixture["expected_aspects"]) >= 3, (
        f"fixture {oracle_fixture['name']!r}: needs >= 3 expected_aspects"
    )


def test_oracle_chart_compute_succeeds(oracle_fixture: dict) -> None:
    """compute_chart returns a valid CHART_DTYPE record for both partners."""
    chart_a, chart_b = _build_charts(oracle_fixture)
    # Both charts must be scalar 0-d structured arrays (Phase 14 contract).
    assert chart_a.shape == (), (
        f"fixture {oracle_fixture['name']!r}: chart_a shape "
        f"{chart_a.shape!r} != ()"
    )
    assert chart_b.shape == (), (
        f"fixture {oracle_fixture['name']!r}: chart_b shape "
        f"{chart_b.shape!r} != ()"
    )
    # Body longitudes finite (no NaN propagation upstream).
    assert np.all(np.isfinite(chart_a["body_lons"])), (
        f"fixture {oracle_fixture['name']!r}: chart_a body_lons has NaN"
    )
    assert np.all(np.isfinite(chart_b["body_lons"])), (
        f"fixture {oracle_fixture['name']!r}: chart_b body_lons has NaN"
    )


def test_oracle_synastry_runs_default_args(oracle_fixture: dict) -> None:
    """calculate_synastry with default args yields a non-empty SYNASTRY result."""
    chart_a, chart_b = _build_charts(oracle_fixture)
    result = calculate_synastry(chart_a, chart_b)
    assert result.dtype.names is not None
    assert "body_a" in result.dtype.names
    assert "aspect_type" in result.dtype.names
    assert len(result) > 0, (
        f"fixture {oracle_fixture['name']!r}: filtered synastry returned 0 rows"
    )


def test_oracle_expected_aspects_all_present(oracle_fixture: dict) -> None:
    """Every expected_aspects entry appears in the filtered synastry within orb_max_deg."""
    chart_a, chart_b = _build_charts(oracle_fixture)
    result = calculate_synastry(chart_a, chart_b, mode="filtered")
    missing: list[str] = []
    over_orb: list[str] = []
    for expected in oracle_fixture["expected_aspects"]:
        body_a_idx = _BODY_NAME_TO_INDEX[expected["body_a"]]
        body_b_idx = _BODY_NAME_TO_INDEX[expected["body_b"]]
        aspect_idx = _ASPECT_NAME_TO_INDEX[expected["aspect"]]
        match = _find_match(result, body_a_idx, body_b_idx, aspect_idx)
        if match is None:
            missing.append(
                f"{expected['body_a']}_A <-> {expected['body_b']}_B "
                f"({expected['aspect']})"
            )
            continue
        orb_abs = abs(float(match["orb"]))
        if orb_abs > expected["orb_max_deg"]:
            over_orb.append(
                f"{expected['body_a']}_A <-> {expected['body_b']}_B "
                f"({expected['aspect']}): |orb|={orb_abs:.4f} > "
                f"orb_max_deg={expected['orb_max_deg']}"
            )
    assert not missing, (
        f"fixture {oracle_fixture['name']!r}: missing expected aspects: "
        + "; ".join(missing)
    )
    assert not over_orb, (
        f"fixture {oracle_fixture['name']!r}: aspects present but over orb: "
        + "; ".join(over_orb)
    )


def test_oracle_max_orb_delta_reported(
    oracle_fixture: dict, capsys: pytest.CaptureFixture[str],
) -> None:
    """Print and assert max |orb| on expected aspects — ROADMAP success criterion #4."""
    chart_a, chart_b = _build_charts(oracle_fixture)
    result = calculate_synastry(chart_a, chart_b, mode="filtered")
    orbs: list[float] = []
    for expected in oracle_fixture["expected_aspects"]:
        body_a_idx = _BODY_NAME_TO_INDEX[expected["body_a"]]
        body_b_idx = _BODY_NAME_TO_INDEX[expected["body_b"]]
        aspect_idx = _ASPECT_NAME_TO_INDEX[expected["aspect"]]
        match = _find_match(result, body_a_idx, body_b_idx, aspect_idx)
        assert match is not None, (
            f"fixture {oracle_fixture['name']!r}: expected aspect "
            f"{expected['body_a']}<->{expected['body_b']} "
            f"({expected['aspect']}) missing from filtered result"
        )
        orbs.append(abs(float(match["orb"])))
    max_orb = max(orbs)
    # IMPORTANT: print() at module level so pytest -v -s captures the line.
    print(
        f"[{oracle_fixture['name']}] max |orb| on expected aspects: "
        f"{max_orb:.4f} deg (over {len(orbs)} aspects)"
    )
    assert max_orb <= 5.0, (
        f"fixture {oracle_fixture['name']!r}: max |orb| {max_orb:.4f} "
        f"exceeds permissive 5.0 deg ceiling"
    )


def test_oracle_tolerance_band_documented(oracle_fixture: dict) -> None:
    """Fixture's tolerance_deg sits in the documented (0, 1] band."""
    tol = float(oracle_fixture["tolerance_deg"])
    assert 0.0 < tol <= 1.0, (
        f"fixture {oracle_fixture['name']!r}: tolerance_deg {tol} "
        f"outside (0.0, 1.0] - update fixture or revise band"
    )


def test_oracle_dense_mode_consistent(oracle_fixture: dict) -> None:
    """dense[mask] equals filtered (idempotency invariant carried over to oracles)."""
    chart_a, chart_b = _build_charts(oracle_fixture)
    dense = calculate_synastry(chart_a, chart_b, mode="dense")
    filtered = calculate_synastry(chart_a, chart_b, mode="filtered")
    dense_masked = dense[dense["aspect_type"] >= 0]
    assert len(dense_masked) == len(filtered), (
        f"fixture {oracle_fixture['name']!r}: dense[mask] count "
        f"{len(dense_masked)} != filtered count {len(filtered)}"
    )
    # Aspect-type set match (canonical body-pair order ensures identity).
    assert np.array_equal(
        dense_masked["aspect_type"], filtered["aspect_type"]
    ), (
        f"fixture {oracle_fixture['name']!r}: dense[mask].aspect_type "
        f"!= filtered.aspect_type"
    )
