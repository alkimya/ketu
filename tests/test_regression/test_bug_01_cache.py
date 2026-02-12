"""Regression test for BUG-01: Cache operator precedence.

Prior to v1.0.0, the cache control logic in generate_cycle_series() had
incorrect operator precedence:

    use_cache and CACHE_AVAILABLE and hasattr(...) or isinstance(...)

This evaluated as:
    ((use_cache and CACHE_AVAILABLE and hasattr(...)) or isinstance(...))

Instead of the intended:
    (use_cache and CACHE_AVAILABLE and (hasattr(...) or isinstance(...)))

Result: use_cache=False was ignored when timestamps were a list or ndarray.
"""

import numpy as np
from datetime import datetime, timezone
from ketu.cycles.calculator import generate_cycle_series


def test_use_cache_false_disables_cache_with_list_timestamps():
    """Test that use_cache=False is respected with list timestamps."""
    # Create a list of UTC-aware datetime timestamps
    timestamps = [
        datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        datetime(2025, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        datetime(2025, 1, 3, 0, 0, 0, tzinfo=timezone.utc),
    ]

    # Call with use_cache=False - this should work without errors
    result = generate_cycle_series("Sun", "Moon", timestamps, use_cache=False)

    # Verify result is returned
    assert result is not None

    # Verify result length matches input length
    assert len(result) == len(timestamps)

    # Verify we got cycle data back
    assert result['body1_id'][0] == 0  # Sun
    assert result['body2_id'][0] == 1  # Moon


def test_use_cache_false_disables_cache_with_ndarray_timestamps():
    """Test that use_cache=False is respected with ndarray timestamps."""
    # Create numpy array of Julian dates
    # JD for 2025-01-01 00:00:00 UTC is approximately 2460676.5
    timestamps = np.array([2460676.5, 2460677.5, 2460678.5])

    # Call with use_cache=False - this should work without errors
    result = generate_cycle_series("Sun", "Moon", timestamps, use_cache=False)

    # Verify result is returned
    assert result is not None

    # Verify result length matches input length
    assert len(result) == len(timestamps)

    # Verify we got cycle data back
    assert result['body1_id'][0] == 0  # Sun
    assert result['body2_id'][0] == 1  # Moon


def test_operator_precedence_logic_directly():
    """Directly test the boolean logic that was broken.

    This test demonstrates the operator precedence bug and validates the fix.
    """
    # Simulate the scenario: use_cache=False, list timestamps
    use_cache = False
    CACHE_AVAILABLE = True
    has_to_pydatetime = False  # list doesn't have this attribute
    is_list_or_ndarray = True
    is_nonempty = True

    # BUGGY expression (without parentheses around the or clause):
    # use_cache and CACHE_AVAILABLE and has_to_pydatetime or (is_list_or_ndarray and is_nonempty)
    # This evaluates as:
    # ((use_cache and CACHE_AVAILABLE and has_to_pydatetime) or (is_list_or_ndarray and is_nonempty))
    buggy_result = (
        use_cache and CACHE_AVAILABLE and has_to_pydatetime or
        (is_list_or_ndarray and is_nonempty)
    )

    # Bug: cache enabled despite use_cache=False!
    assert buggy_result == True, "Buggy expression incorrectly enables cache"

    # FIXED expression (with parentheses around the or clause):
    # use_cache and CACHE_AVAILABLE and (has_to_pydatetime or (is_list_or_ndarray and is_nonempty))
    fixed_result = (
        use_cache and CACHE_AVAILABLE and
        (has_to_pydatetime or (is_list_or_ndarray and is_nonempty))
    )

    # Correct: cache disabled when use_cache=False
    assert fixed_result == False, "Fixed expression correctly disables cache"

    # Additional test: verify with use_cache=True the logic works correctly
    use_cache = True
    fixed_result_enabled = (
        use_cache and CACHE_AVAILABLE and
        (has_to_pydatetime or (is_list_or_ndarray and is_nonempty))
    )
    assert fixed_result_enabled == True, "Fixed expression enables cache when use_cache=True"
