"""Regression: datetime64 ndarray must work on the cache path.

generate_cycle_series advertises ``Union[np.ndarray, List[datetime]]`` for its
timestamps argument, and the Julian-date path already converts datetime64 to
python datetime. The cache path, however, passed the array straight to
``EphemerisCache.get_positions_vectorized``, which reads ``.year``/``.month``/…
attributes that ``numpy.datetime64`` does not expose, raising::

    AttributeError: 'numpy.datetime64' object has no attribute 'year'

The existing ``test_numpy_datetime64_input`` only exercised ``use_cache=False``,
so this path was untested. These tests pin both halves: the cache path accepts a
datetime64 ndarray, and it produces results identical to the equivalent
python-datetime list.
"""

from datetime import datetime, timedelta

import numpy as np

from ketu.cycles import generate_cycle_series


def _week_datetimes():
    """Seven consecutive daily UTC datetimes (python datetime list)."""
    return [datetime(2025, 6, 1) + timedelta(days=i) for i in range(7)]


def _week_datetime64():
    """Same seven days as a numpy datetime64 ndarray."""
    return np.arange(
        "2025-06-01", "2025-06-08", dtype="datetime64[D]"
    ).astype("datetime64[s]")


def test_datetime64_ndarray_accepted_via_cache():
    """A datetime64 ndarray must succeed on the cache path (use_cache=True)."""
    result = generate_cycle_series(
        "Sun", "Moon", _week_datetime64(), use_cache=True
    )
    assert result.shape == (7,)
    assert np.all(np.isfinite(result["angular_separation"]))
    assert np.all(result["angular_separation"] >= 0)
    assert np.all(result["angular_separation"] < 360)


def test_datetime64_matches_datetime_list_via_cache():
    """datetime64 ndarray and equivalent datetime list yield identical results."""
    cyc_list = generate_cycle_series("Sun", "Moon", _week_datetimes(), use_cache=True)
    cyc_arr = generate_cycle_series("Sun", "Moon", _week_datetime64(), use_cache=True)
    np.testing.assert_allclose(
        cyc_arr["angular_separation"],
        cyc_list["angular_separation"],
        atol=1e-4,
    )
