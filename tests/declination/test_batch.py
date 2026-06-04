"""Batch-path tests for :func:`ketu.declination.declination_aspect_masks`.

Covers:

- NamedTuple field contract (:class:`DeclinationAspectMasks` fields/order).
- Shape and dtype guarantees for ``(S, 14)`` input.
- ``idx_i`` / ``idx_j`` alignment with ``np.triu_indices(14, k=1)``.
- ``(14,)`` single-chart promotion via :func:`numpy.atleast_2d`.
- Vectorization contract: no Python ``for`` loop in the batch hot path.
- Row-for-row consistency oracle between batch masks and scalar
  :func:`find_declination_aspects` on the JD 2451717.0 solstice chart.
- Multi-chart independence: row 0 (solstice, 5P+5CP) and row 1 (all zeros,
  0P+0CP) are independent.
- ``gap`` field equals ``min(|δ₁−δ₂|, |δ₁+δ₂|)`` element-wise.
"""
from __future__ import annotations

import inspect

import numpy as np
import pytest

from ketu.declination import (
    DeclinationAspectMasks,
    declination_aspect_masks,
    find_declination_aspects,
)
from ketu.declination.core import _ORB_MAT


def test_namedtuple_fields() -> None:
    """DeclinationAspectMasks has exactly the 6 fields in the specified order."""
    expected = ("parallel", "contra", "gap", "idx_i", "idx_j", "orb_pairs")
    assert DeclinationAspectMasks._fields == expected


def test_batch_shapes_and_dtypes() -> None:
    """Batch on (5, 14) zeros: parallel/contra are (5,91) bool, gap (5,91) f8, idx_i/idx_j (91,) int, orb_pairs (91,) f8."""
    d = np.zeros((5, 14))
    r = declination_aspect_masks(d)

    # parallel and contra: (5, 91) bool
    assert r.parallel.shape == (5, 91), f"parallel shape {r.parallel.shape}"
    assert r.contra.shape == (5, 91), f"contra shape {r.contra.shape}"
    assert r.parallel.dtype == np.dtype("bool"), f"parallel dtype {r.parallel.dtype}"
    assert r.contra.dtype == np.dtype("bool"), f"contra dtype {r.contra.dtype}"

    # gap: (5, 91) float64
    assert r.gap.shape == (5, 91), f"gap shape {r.gap.shape}"
    assert r.gap.dtype == np.dtype("f8"), f"gap dtype {r.gap.dtype}"

    # idx_i, idx_j: (91,) integer
    assert r.idx_i.shape == (91,), f"idx_i shape {r.idx_i.shape}"
    assert r.idx_j.shape == (91,), f"idx_j shape {r.idx_j.shape}"
    assert np.issubdtype(r.idx_i.dtype, np.integer), f"idx_i dtype {r.idx_i.dtype}"
    assert np.issubdtype(r.idx_j.dtype, np.integer), f"idx_j dtype {r.idx_j.dtype}"

    # orb_pairs: (91,) float64
    assert r.orb_pairs.shape == (91,), f"orb_pairs shape {r.orb_pairs.shape}"
    assert r.orb_pairs.dtype == np.dtype("f8"), f"orb_pairs dtype {r.orb_pairs.dtype}"


def test_idx_matches_triu() -> None:
    """idx_i/idx_j equal np.triu_indices(14, k=1); orb_pairs equals _ORB_MAT[idx_i, idx_j]."""
    d = np.zeros((2, 14))
    r = declination_aspect_masks(d)
    expected_i, expected_j = np.triu_indices(14, k=1)
    assert (r.idx_i == expected_i).all(), "idx_i mismatch with triu_indices"
    assert (r.idx_j == expected_j).all(), "idx_j mismatch with triu_indices"
    expected_orbs = _ORB_MAT[expected_i, expected_j]
    np.testing.assert_array_equal(r.orb_pairs, expected_orbs)


def test_single_chart_via_atleast_2d() -> None:
    """A (14,) input is promoted to (1, 91) parallel/contra/gap masks."""
    d = np.zeros(14)
    r = declination_aspect_masks(d)
    assert r.parallel.shape == (1, 91), f"parallel shape {r.parallel.shape}"
    assert r.contra.shape == (1, 91), f"contra shape {r.contra.shape}"
    assert r.gap.shape == (1, 91), f"gap shape {r.gap.shape}"


def test_no_python_body_loop() -> None:
    """The hot path of declination_aspect_masks contains no Python for-loop.

    Reads the source via inspect.getsource, strips the docstring, and asserts
    that the remaining code lines contain no ``for `` token — guards the
    vectorization contract.
    """
    src = inspect.getsource(declination_aspect_masks)
    # Strip the docstring: find the closing triple-quote after the opening one
    # (the docstring ends at the last ``"""`` before the actual code lines).
    lines = src.splitlines()
    # Scan past the opening def line and the docstring block
    in_docstring = False
    code_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not in_docstring and (stripped.startswith('"""') or stripped.startswith("'''")):
            in_docstring = True
            # Single-line docstring ends on the same line (if closing quote present)
            rest = stripped[3:]
            if rest.endswith('"""') or rest.endswith("'''"):
                in_docstring = False
            continue
        if in_docstring:
            if '"""' in stripped or "'''" in stripped:
                in_docstring = False
            continue
        code_lines.append(line)
    code_body = "\n".join(code_lines)
    assert "for " not in code_body, (
        "declination_aspect_masks must not contain a Python for-loop in the "
        "code body; use pure NumPy broadcasting instead.\n"
        f"Code body:\n{code_body}"
    )


def test_batch_matches_scalar_solstice(body_decl_solstice: np.ndarray) -> None:
    """Batch masks on JD 2451717.0 chart match scalar find_declination_aspects row-for-row.

    The oracle expects exactly 5 parallels + 5 contra-parallels for the solstice chart.
    Reconstructs the set of (idx_i[p], idx_j[p], kind) tuples from both paths
    and asserts equality.
    """
    d = body_decl_solstice
    r = declination_aspect_masks(d)  # promotes (14,) -> (1, 91)

    # Reconstruct set from batch result (row 0)
    batch_set: set[tuple[int, int, str]] = set()
    for p in np.where(r.parallel[0])[0]:
        batch_set.add((int(r.idx_i[p]), int(r.idx_j[p]), "P"))
    for p in np.where(r.contra[0])[0]:
        batch_set.add((int(r.idx_i[p]), int(r.idx_j[p]), "CP"))

    # Reconstruct set from scalar result
    scalar_result = find_declination_aspects(d)
    scalar_set: set[tuple[int, int, str]] = set()
    for row in scalar_result:
        scalar_set.add((int(row["body1"]), int(row["body2"]), str(row["kind"])))

    assert batch_set == scalar_set, (
        f"batch and scalar disagree:\n  batch={batch_set}\n  scalar={scalar_set}"
    )
    # Oracle: exactly 10 detections (5 P + 5 CP)
    assert len(batch_set) == 10, f"expected 10 detections, got {len(batch_set)}"
    n_p = int(np.count_nonzero(r.parallel[0]))
    n_cp = int(np.count_nonzero(r.contra[0]))
    assert n_p == 5, f"expected 5 parallels, got {n_p}"
    assert n_cp == 5, f"expected 5 contra-parallels, got {n_cp}"


def test_batch_multi_chart(
    body_decl_solstice: np.ndarray,
    body_decl_zeros: np.ndarray,
) -> None:
    """Multi-chart (2, 14) batch: row 0 = 5P+5CP, row 1 (zeros) = 0P+0CP."""
    batch = np.stack([body_decl_solstice, body_decl_zeros], axis=0)  # (2, 14)
    r = declination_aspect_masks(batch)

    # Row 0: solstice — 5 parallels + 5 contra-parallels
    n_p0 = int(np.count_nonzero(r.parallel[0]))
    n_cp0 = int(np.count_nonzero(r.contra[0]))
    assert n_p0 == 5, f"row 0: expected 5 parallels, got {n_p0}"
    assert n_cp0 == 5, f"row 0: expected 5 contras, got {n_cp0}"

    # Row 1: all zeros — zero-sign trap means no aspects
    n_p1 = int(np.count_nonzero(r.parallel[1]))
    n_cp1 = int(np.count_nonzero(r.contra[1]))
    assert n_p1 == 0, f"row 1: expected 0 parallels, got {n_p1}"
    assert n_cp1 == 0, f"row 1: expected 0 contras, got {n_cp1}"


def test_batch_gap_is_min() -> None:
    """gap field equals min(|δ₁−δ₂|, |δ₁+δ₂|) element-wise.

    Uses a hand-built single chart to verify the gap formula on the first pair
    (Sun=body 0, Moon=body 1 → pair index 0 in triu_indices(14, k=1)).
    """
    # Build a chart with known declinations for Sun and Moon
    d = np.zeros(14)
    d[0] = 10.0   # Sun: +10°
    d[1] = 12.0   # Moon: +12°
    # gap_p  = |10 - 12| = 2.0
    # gap_cp = |10 + 12| = 22.0
    # expected gap = min(2.0, 22.0) = 2.0
    r = declination_aspect_masks(d)
    idx_i, idx_j = np.triu_indices(14, k=1)
    # Find the (Sun=0, Moon=1) pair
    pair_idx = int(np.where((idx_i == 0) & (idx_j == 1))[0][0])
    d1 = d[idx_i]
    d2 = d[idx_j]
    expected_gap_p  = np.abs(d1 - d2)
    expected_gap_cp = np.abs(d1 + d2)
    expected_gap = np.minimum(expected_gap_p, expected_gap_cp)
    np.testing.assert_allclose(
        r.gap[0, pair_idx],
        expected_gap[pair_idx],
        err_msg="gap[0, Sun-Moon pair] != min(|d1-d2|, |d1+d2|)",
    )
    # Verify the full gap row matches element-wise
    np.testing.assert_allclose(
        r.gap[0],
        expected_gap,
        err_msg="gap[0] row does not match min(|d1-d2|, |d1+d2|) element-wise",
    )
