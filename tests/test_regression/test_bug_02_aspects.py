"""Regression test for BUG-02: Aspect vectorization non-determinism.

Prior to v1.0.0, calculate_aspects_vectorized() returned different results
than calculate_aspects() due to incorrect indexing in the inner loop:

    for idx in np.where(in_orb)[0]:
        results.append((..., orb_values[np.where(in_orb)[0] == idx][0]))

The expression `orb_values[np.where(in_orb)[0] == idx][0]` creates a boolean
mask against the full in_orb indices, which can produce wrong values when
multiple indices match or miss values entirely.

Example: On 2020-12-21, loop found 30 aspects, vectorized found 31.
Extra: Venus-Uranus Quincunx (body1=3, body2=7, i_asp=11).
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pytest

from ketu.aspects.calculator import calculate_aspects, calculate_aspects_vectorized
from ketu.calculations import utc_to_julian


def test_vectorized_matches_loop_on_known_failure_date():
    """Test vectorization matches loop on the known failure date.

    On 2020-12-21 18:20:00 UTC, the vectorized function found 31 aspects
    while the loop version found 30 aspects. This test ensures both
    functions return identical results after the fix.
    """
    # Known failure date
    dt = datetime(2020, 12, 21, 18, 20, 0, tzinfo=ZoneInfo("UTC"))
    jd = utc_to_julian(dt)

    # Calculate aspects using both methods
    loop_result = calculate_aspects(jd)
    vec_result = calculate_aspects_vectorized(jd)

    # First check: same count
    assert len(loop_result) == len(vec_result), (
        f"Aspect count mismatch on 2020-12-21: "
        f"loop found {len(loop_result)}, vectorized found {len(vec_result)}"
    )

    # Sort both results by (body1, body2, i_asp) for comparison
    loop_sorted = np.sort(loop_result, order=["body1", "body2", "i_asp"])
    vec_sorted = np.sort(vec_result, order=["body1", "body2", "i_asp"])

    # Check body IDs and aspect types match exactly
    np.testing.assert_array_equal(
        loop_sorted["body1"], vec_sorted["body1"],
        err_msg="body1 IDs don't match"
    )
    np.testing.assert_array_equal(
        loop_sorted["body2"], vec_sorted["body2"],
        err_msg="body2 IDs don't match"
    )
    np.testing.assert_array_equal(
        loop_sorted["i_asp"], vec_sorted["i_asp"],
        err_msg="Aspect types don't match"
    )

    # Check orb values are close (allowing for floating point precision)
    np.testing.assert_allclose(
        loop_sorted["orb"], vec_sorted["orb"],
        rtol=1e-6,
        err_msg="Orb values don't match"
    )


@pytest.mark.parametrize("dt_str,expected_tz", [
    ("2020-12-21 18:20:00", "UTC"),  # Known failure date
    ("2025-01-01 00:00:00", "UTC"),
    ("2015-06-15 12:00:00", "UTC"),
    ("2010-03-20 00:00:00", "UTC"),  # Equinox
    ("2023-08-01 06:00:00", "UTC"),
])
def test_vectorized_matches_loop_across_dates(dt_str, expected_tz):
    """Test vectorization matches loop across multiple dates.

    This parametrized test ensures the fix works across various dates,
    not just the known failure case.
    """
    dt = datetime.fromisoformat(dt_str).replace(tzinfo=ZoneInfo(expected_tz))
    jd = utc_to_julian(dt)

    # Calculate aspects using both methods
    loop_result = calculate_aspects(jd)
    vec_result = calculate_aspects_vectorized(jd)

    # Assert same count
    assert len(loop_result) == len(vec_result), (
        f"Aspect count mismatch on {dt_str}: "
        f"loop found {len(loop_result)}, vectorized found {len(vec_result)}"
    )

    # Sort and compare
    loop_sorted = np.sort(loop_result, order=["body1", "body2", "i_asp"])
    vec_sorted = np.sort(vec_result, order=["body1", "body2", "i_asp"])

    # Check all fields match
    np.testing.assert_array_equal(loop_sorted["body1"], vec_sorted["body1"])
    np.testing.assert_array_equal(loop_sorted["body2"], vec_sorted["body2"])
    np.testing.assert_array_equal(loop_sorted["i_asp"], vec_sorted["i_asp"])
    np.testing.assert_allclose(loop_sorted["orb"], vec_sorted["orb"], rtol=1e-6)


def test_vectorized_deterministic_repeated_calls():
    """Test that vectorized calculation is deterministic.

    Multiple calls with the same input should always produce identical results.
    This ensures there are no random elements or state dependencies.
    """
    dt = datetime(2020, 12, 21, 18, 20, 0, tzinfo=ZoneInfo("UTC"))
    jd = utc_to_julian(dt)

    # Call vectorized function 10 times
    results = [calculate_aspects_vectorized(jd) for _ in range(10)]

    # All results should have the same length
    lengths = [len(r) for r in results]
    assert len(set(lengths)) == 1, f"Got different lengths: {lengths}"

    # All results should be identical to the first result
    first = results[0]
    for i, result in enumerate(results[1:], start=2):
        # Sort both for comparison
        first_sorted = np.sort(first, order=["body1", "body2", "i_asp"])
        result_sorted = np.sort(result, order=["body1", "body2", "i_asp"])

        np.testing.assert_array_equal(
            first_sorted, result_sorted,
            err_msg=f"Call {i} produced different results"
        )
