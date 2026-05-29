"""Property tests for the dense-vs-filtered idempotency invariant.

Pins ``calculate_synastry(a, b, mode='dense')[mask] == calculate_synastry(a, b, mode='filtered')``
modulo row order across multiple chart pairs (parametrised). Also pins
the self-synastry diagonal-conjunction sanity (a chart synastry'd with
itself shows all 16 self-pair conjunctions at exact orb), including the
zero-orb-body edge case for Rahu / Ketu / Lilith / Chiron.

Fixtures live in :mod:`tests.synastry.conftest` (auto-discovered).
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.synastry import calculate_synastry


CHART_PAIRS = [
    ("paris_nyc", "chart_a_paris", "chart_b_nyc"),
    ("paris_tokyo", "chart_a_paris", "chart_b_tokyo"),
    ("paris_sydney", "chart_a_paris", "chart_b_sydney"),
    ("paris_reykjavik", "chart_a_paris", "chart_b_reykjavik"),
]


@pytest.mark.parametrize(
    "label, fixture_a, fixture_b",
    CHART_PAIRS,
    ids=[case[0] for case in CHART_PAIRS],
)
def test_dense_mask_filtered_equals_filtered_mode(
    label: str,
    fixture_a: str,
    fixture_b: str,
    request: pytest.FixtureRequest,
) -> None:
    """``dense[mask]`` row count equals ``filtered`` row count for each chart pair."""
    a = request.getfixturevalue(fixture_a)
    b = request.getfixturevalue(fixture_b)
    dense = calculate_synastry(a, b, mode="dense")
    filtered = calculate_synastry(a, b, mode="filtered")
    assert len(dense[dense["aspect_type"] >= 0]) == len(filtered)


@pytest.mark.parametrize(
    "label, fixture_a, fixture_b",
    CHART_PAIRS,
    ids=[case[0] for case in CHART_PAIRS],
)
def test_dense_filtered_same_aspect_type_set(
    label: str,
    fixture_a: str,
    fixture_b: str,
    request: pytest.FixtureRequest,
) -> None:
    """Sorted set of aspect types in ``dense[mask]`` matches the set in ``filtered``."""
    a = request.getfixturevalue(fixture_a)
    b = request.getfixturevalue(fixture_b)
    dense = calculate_synastry(a, b, mode="dense")
    filtered = calculate_synastry(a, b, mode="filtered")
    assert sorted(dense[dense["aspect_type"] >= 0]["aspect_type"].tolist()) == sorted(
        filtered["aspect_type"].tolist(),
    )


@pytest.mark.parametrize(
    "label, fixture_a, fixture_b",
    CHART_PAIRS,
    ids=[case[0] for case in CHART_PAIRS],
)
def test_dense_filtered_same_orb_values(
    label: str,
    fixture_a: str,
    fixture_b: str,
    request: pytest.FixtureRequest,
) -> None:
    """For each aspected (body_a, body_b, aspect_type) triple, orb matches across modes."""
    a = request.getfixturevalue(fixture_a)
    b = request.getfixturevalue(fixture_b)
    dense = calculate_synastry(a, b, mode="dense")
    filtered = calculate_synastry(a, b, mode="filtered")
    # Both arrays are emitted in canonical body-pair ascending order.
    dense_subset = dense[dense["aspect_type"] >= 0]
    assert np.array_equal(dense_subset["orb"], filtered["orb"])
    assert np.array_equal(
        dense_subset["aspect_type"], filtered["aspect_type"],
    )
    assert np.array_equal(dense_subset["body_a"], filtered["body_a"])
    assert np.array_equal(dense_subset["body_b"], filtered["body_b"])


def test_dense_filtered_no_hidden_state(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Calling ``calculate_synastry`` twice returns equal arrays (idempotency / no caching state)."""
    r1 = calculate_synastry(chart_a_paris, chart_b_nyc)
    r2 = calculate_synastry(chart_a_paris, chart_b_nyc)
    for field in r1.dtype.names:
        a, b = r1[field], r2[field]
        if np.issubdtype(a.dtype, np.floating):
            assert np.array_equal(a, b, equal_nan=True)
        else:
            assert np.array_equal(a, b)


def test_self_synastry_dense_diagonal_is_conjunction(
    chart_a_paris: np.ndarray,
) -> None:
    """``calculate_synastry(a, a, mode='dense')`` shows all 16 self-pair conjunctions at exact orb.

    Rahu / Ketu / Lilith / Chiron have zero natal orbs (in
    :data:`ketu.core.bodies`), so the synastry orb tolerance for these
    self-pairs is ``0``. The conjunction is detected because the
    in-orb test uses ``dist <= orbs_pair`` (non-strict), and self-synastry
    gives ``dist == 0`` exactly. This edge case pre-empts the
    "zero-orb body conjunction not detected" surprise documented in
    16-RESEARCH.md (Pitfall 2 / Rahu zero-orb conjunction edge case).
    """
    self_syn = calculate_synastry(
        chart_a_paris, chart_a_paris, mode="dense",
    )
    diag = self_syn[self_syn["body_a"] == self_syn["body_b"]]
    assert len(diag) == 16, "must have 16 self-pair rows (one per body in axis)"
    # Every diagonal row is a conjunction (aspect_type == 0).
    assert (diag["aspect_type"] == 0).all(), (
        f"diagonal must be conjunctions, got {diag['aspect_type'].tolist()}"
    )
    # Every orb is exactly zero (delta = -dist with dist=0 -> orb = 0.0).
    # Account for float32 / signed-zero artefact: assert |orb| < 1e-6.
    assert (np.abs(diag["orb"]) < 1e-6).all()


@pytest.mark.parametrize(
    "label, fixture_a, fixture_b",
    CHART_PAIRS,
    ids=[case[0] for case in CHART_PAIRS],
)
def test_dense_count_always_256(
    label: str,
    fixture_a: str,
    fixture_b: str,
    request: pytest.FixtureRequest,
) -> None:
    """``mode='dense'`` always returns exactly 256 rows for any chart pair."""
    a = request.getfixturevalue(fixture_a)
    b = request.getfixturevalue(fixture_b)
    dense = calculate_synastry(a, b, mode="dense")
    assert len(dense) == 256


@pytest.mark.parametrize(
    "label, fixture_a, fixture_b",
    CHART_PAIRS,
    ids=[case[0] for case in CHART_PAIRS],
)
def test_filtered_count_le_256(
    label: str,
    fixture_a: str,
    fixture_b: str,
    request: pytest.FixtureRequest,
) -> None:
    """``mode='filtered'`` returns at most 256 rows for any chart pair."""
    a = request.getfixturevalue(fixture_a)
    b = request.getfixturevalue(fixture_b)
    filtered = calculate_synastry(a, b, mode="filtered")
    assert len(filtered) <= 256
