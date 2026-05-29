"""Additional tests for EphemerisCache to cover uncovered lines.

Targets lines: 134, 158-159, 213, 235, 240, 254-257, 283-286, 312-315, 372, 404-405.
"""

import calendar
from datetime import datetime, timezone
import numpy as np
import pytest

from ketu.cache.ephemeris_cache import EphemerisCache, BODY_COUNT, POSITION_FIELDS


class TestMemoryCacheHit:
    """Test memory cache hit path (line 134)."""

    def test_ensure_month_twice_hits_memory_cache(self, tmp_path):
        """Calling ensure_month twice without clearing memory hits line 134.

        The second call should return immediately from the memory cache check
        at line 133-134 without touching disk or recomputing.
        """
        cache = EphemerisCache(cache_dir=tmp_path / "cache")

        # First call: computes and stores in memory + disk
        cache.ensure_month(2025, 1)
        assert (2025, 1) in cache._memory_cache

        # Delete the disk file so we can verify the second call
        # does NOT try to load from disk (it returns from memory)
        disk_file = tmp_path / "cache" / "2025-01-ephemeris.npy"
        assert disk_file.exists()
        disk_file.unlink()

        # Second call: should hit memory cache (line 134) and return
        # If it tried disk, it would fail or recompute
        cache.ensure_month(2025, 1)

        # Data is still in memory
        assert (2025, 1) in cache._memory_cache
        # Disk file was NOT recreated (proving we returned early from memory)
        assert not disk_file.exists()

    def test_ensure_range_skips_already_loaded_months(self, tmp_path):
        """ensure_range with already-loaded months hits memory cache path."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")

        # Pre-load January
        cache.ensure_month(2025, 1)
        data_before = cache._memory_cache[(2025, 1)]

        # ensure_range includes January -- should hit memory cache for it
        cache.ensure_range(2025, 1, 2025, 2)

        # January data should be the exact same object (not reloaded)
        assert cache._memory_cache[(2025, 1)] is data_before
        # February should now also be loaded
        assert (2025, 2) in cache._memory_cache


class TestGetPositionAutoLoad:
    """Test auto-loading in get_position when month not in memory (line 213)."""

    def test_get_position_auto_loads_month(self, tmp_path):
        """get_position auto-loads month if not in memory (line 212-213)."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")

        # Do NOT call ensure_month first
        assert (2025, 1) not in cache._memory_cache

        # get_position should auto-load January 2025
        ts = datetime(2025, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
        pos = cache.get_position(ts, body_id=0)

        # Month should now be in memory
        assert (2025, 1) in cache._memory_cache

        # Position should be valid
        assert pos.shape == (POSITION_FIELDS,)
        assert 0 <= pos[0] < 360  # longitude in valid range


class TestNaiveDatetimeAutoLoad:
    """Test naive datetime handling combined with auto-load (lines 206, 213)."""

    def test_naive_datetime_triggers_auto_load(self, tmp_path):
        """Naive datetime with no pre-loaded month hits both lines 206 and 213."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")

        # Naive datetime, no month pre-loaded
        ts_naive = datetime(2025, 3, 10, 6, 0, 0)  # No tzinfo
        pos = cache.get_position(ts_naive, body_id=1)  # Moon

        # Should have auto-loaded March 2025
        assert (2025, 3) in cache._memory_cache
        assert pos.shape == (POSITION_FIELDS,)


class TestNoInterpolation:
    """Test interpolate=False path (line 218-219)."""

    def test_no_interpolation_returns_midnight_value(self, tmp_path):
        """interpolate=False returns exact cached midnight value (line 218-219)."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        cache.ensure_month(2025, 6)

        # Request position at 3pm with no interpolation
        ts = datetime(2025, 6, 20, 15, 30, 0, tzinfo=timezone.utc)
        pos = cache.get_position(ts, body_id=0, interpolate=False)

        # Should return exact midnight value for June 20 (index 19)
        expected = cache._memory_cache[(2025, 6)][19, 0, :]
        np.testing.assert_array_equal(pos, expected)

    def test_no_interpolation_at_midnight(self, tmp_path):
        """interpolate=False at midnight also returns exact value."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        cache.ensure_month(2025, 6)

        ts = datetime(2025, 6, 1, 0, 0, 0, tzinfo=timezone.utc)
        pos_no_interp = cache.get_position(ts, body_id=2, interpolate=False)
        pos_interp = cache.get_position(ts, body_id=2, interpolate=True)

        # At midnight, both should be identical
        np.testing.assert_array_equal(pos_no_interp, pos_interp)


class TestCrossMonthBoundary:
    """Test cross-month boundary interpolation (lines 232-242, 254-257)."""

    def test_cross_month_boundary_interpolation(self, tmp_path):
        """Interpolation at noon on last day of month uses next month data (lines 234-242)."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        cache.ensure_month(2025, 3)
        # Do NOT pre-load April -- let it be auto-loaded (line 240)

        # Noon on March 31 (last day of March)
        ts = datetime(2025, 3, 31, 12, 0, 0, tzinfo=timezone.utc)
        pos = cache.get_position(ts, body_id=0, interpolate=True)

        # April should have been auto-loaded
        assert (2025, 4) in cache._memory_cache

        # Verify interpolation is between March 31 and April 1
        mar_data = cache._memory_cache[(2025, 3)]
        apr_data = cache._memory_cache[(2025, 4)]
        mar_31 = mar_data[30, 0, :]  # Last day of March (index 30)
        apr_1 = apr_data[0, 0, :]    # First day of April

        # For non-longitude fields (lat, dist, speeds), check linear interpolation
        for i in range(1, POSITION_FIELDS):
            expected = mar_31[i] + (apr_1[i] - mar_31[i]) * 0.5
            np.testing.assert_allclose(pos[i], expected, atol=0.01,
                                       err_msg=f"Field {i} mismatch")

    def test_cross_year_boundary_december_to_january(self, tmp_path):
        """Interpolation on Dec 31 crosses to next year's January (line 235)."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        cache.ensure_month(2024, 12)
        # Do NOT pre-load January 2025 -- let auto-load trigger (line 240)

        # Noon on December 31
        ts = datetime(2024, 12, 31, 12, 0, 0, tzinfo=timezone.utc)
        pos = cache.get_position(ts, body_id=0, interpolate=True)

        # January 2025 should have been auto-loaded via line 235 path
        assert (2025, 1) in cache._memory_cache

        # Verify interpolation is between Dec 31 and Jan 1
        dec_data = cache._memory_cache[(2024, 12)]
        jan_data = cache._memory_cache[(2025, 1)]
        dec_31 = dec_data[30, 0, :]  # Dec 31 = index 30
        jan_1 = jan_data[0, 0, :]

        # Latitude (field 1) should be midpoint
        expected_lat = dec_31[1] + (jan_1[1] - dec_31[1]) * 0.5
        np.testing.assert_allclose(pos[1], expected_lat, atol=0.01)

    def test_cross_month_with_next_month_already_loaded(self, tmp_path):
        """Cross-month when next month is already in memory (skips line 240 ensure)."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        # Pre-load both months
        cache.ensure_range(2025, 6, 2025, 7)

        days_in_june = calendar.monthrange(2025, 6)[1]
        # Noon on last day of June
        ts = datetime(2025, 6, days_in_june, 18, 0, 0, tzinfo=timezone.utc)
        pos = cache.get_position(ts, body_id=1, interpolate=True)

        assert pos.shape == (POSITION_FIELDS,)
        assert 0 <= pos[0] < 360


class TestLongitudeWrapAround:
    """Test longitude 0/360 wrap-around handling (lines 254-257).

    This is hard to trigger with real astronomical data since the Sun moves
    smoothly. We use the Moon which moves faster, or we mock the data.
    """

    def test_longitude_wrap_around_forward(self, tmp_path):
        """Longitude wrap from ~350 to ~10 is handled correctly (lines 254-257)."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")

        # Create synthetic data with a wrap-around
        # 2 days of data, body 0 goes from 350 to 10 (crossing 360/0)
        data = np.zeros((2, BODY_COUNT, POSITION_FIELDS), dtype=np.float32)
        data[0, 0, 0] = 350.0  # Day 1 longitude
        data[1, 0, 0] = 10.0   # Day 2 longitude (crossed 360)
        # Set some velocity so it's realistic
        data[0, 0, 3] = 1.0
        data[1, 0, 3] = 1.0

        # Inject synthetic data into memory cache
        # Use a month with only 2 days? No, we need a real month.
        # Instead, use February which has 28 days and set our data in a custom way.
        # Actually, we can just directly set the cache for a fictitious purpose.
        # We'll create a 28-day array and set days 0 and 1.
        full_data = np.zeros((28, BODY_COUNT, POSITION_FIELDS), dtype=np.float32)
        full_data[0, 0, 0] = 350.0  # Feb 1
        full_data[1, 0, 0] = 10.0   # Feb 2 (wrapped past 360)
        full_data[0, 0, 3] = 1.0
        full_data[1, 0, 3] = 1.0

        cache._memory_cache[(2025, 2)] = full_data

        # Interpolate at noon on Feb 1 (fraction=0.5)
        ts = datetime(2025, 2, 1, 12, 0, 0, tzinfo=timezone.utc)
        pos = cache.get_position(ts, body_id=0, interpolate=True)

        # Expected: 350 + (370 - 350) * 0.5 = 360 -> 0 degrees (mod 360)
        # Since |10 - 350| = 340 > 180, wrap occurs:
        #   lon2 (10) < lon1 (350), so lon2 += 360 -> lon2 = 370
        # result = (350 + (370-350)*0.5) % 360 = 360 % 360 = 0
        assert np.isclose(pos[0], 0.0, atol=0.1) or np.isclose(pos[0], 360.0, atol=0.1)

    def test_longitude_wrap_around_backward(self, tmp_path):
        """Longitude wrap from ~10 to ~350 (retrograde) handled correctly."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")

        full_data = np.zeros((28, BODY_COUNT, POSITION_FIELDS), dtype=np.float32)
        full_data[0, 0, 0] = 10.0   # Feb 1
        full_data[1, 0, 0] = 350.0  # Feb 2 (retrograde, crossed 0)
        full_data[0, 0, 3] = -1.0
        full_data[1, 0, 3] = -1.0

        cache._memory_cache[(2025, 2)] = full_data

        # Interpolate at noon on Feb 1
        ts = datetime(2025, 2, 1, 12, 0, 0, tzinfo=timezone.utc)
        pos = cache.get_position(ts, body_id=0, interpolate=True)

        # |350 - 10| = 340 > 180, wrap occurs:
        #   lon2 (350) > lon1 (10), so lon1 += 360 -> lon1 = 370
        # result = (370 + (350-370)*0.5) % 360 = 360 % 360 = 0
        assert np.isclose(pos[0], 0.0, atol=0.1) or np.isclose(pos[0], 360.0, atol=0.1)


class TestGetAllPositions:
    """Test get_all_positions method (lines 283-286)."""

    def test_get_all_positions_returns_all_bodies(self, tmp_path):
        """get_all_positions returns (BODY_COUNT, POSITION_FIELDS) array."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        cache.ensure_month(2025, 1)

        ts = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = cache.get_all_positions(ts, interpolate=True)

        assert result.shape == (BODY_COUNT, POSITION_FIELDS)
        assert result.shape == (14, 6)

        # All longitudes should be in valid range
        for body_id in range(BODY_COUNT):
            assert 0 <= result[body_id, 0] < 360, \
                f"Body {body_id} longitude {result[body_id, 0]} out of range"

    def test_get_all_positions_matches_individual(self, tmp_path):
        """get_all_positions matches individual get_position calls."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        cache.ensure_month(2025, 1)

        ts = datetime(2025, 1, 10, 6, 0, 0, tzinfo=timezone.utc)
        all_pos = cache.get_all_positions(ts, interpolate=True)

        for body_id in range(BODY_COUNT):
            individual = cache.get_position(ts, body_id, interpolate=True)
            np.testing.assert_array_equal(
                all_pos[body_id, :], individual,
                err_msg=f"Body {body_id} mismatch"
            )

    def test_get_all_positions_no_interpolation(self, tmp_path):
        """get_all_positions with interpolate=False returns midnight values."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        cache.ensure_month(2025, 1)

        ts = datetime(2025, 1, 20, 15, 0, 0, tzinfo=timezone.utc)
        result = cache.get_all_positions(ts, interpolate=False)

        # Should match raw cached data for that day
        expected = cache._memory_cache[(2025, 1)][19, :, :]  # Day 20 = index 19
        np.testing.assert_array_equal(result, expected)


class TestGetPositionsBatch:
    """Test get_positions_batch method (lines 312-315)."""

    def test_get_positions_batch_multiple_timestamps(self, tmp_path):
        """get_positions_batch returns (n, POSITION_FIELDS) array."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        cache.ensure_month(2025, 1)

        timestamps = [
            datetime(2025, 1, 5, 0, 0, 0, tzinfo=timezone.utc),
            datetime(2025, 1, 10, 12, 0, 0, tzinfo=timezone.utc),
            datetime(2025, 1, 15, 6, 0, 0, tzinfo=timezone.utc),
            datetime(2025, 1, 20, 18, 0, 0, tzinfo=timezone.utc),
        ]

        result = cache.get_positions_batch(timestamps, body_id=0, interpolate=True)

        assert result.shape == (4, POSITION_FIELDS)

        # All longitudes in valid range
        assert np.all(result[:, 0] >= 0)
        assert np.all(result[:, 0] < 360)

    def test_get_positions_batch_matches_individual(self, tmp_path):
        """get_positions_batch matches individual get_position calls."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        cache.ensure_month(2025, 1)

        timestamps = [
            datetime(2025, 1, 3, 8, 0, 0, tzinfo=timezone.utc),
            datetime(2025, 1, 7, 16, 0, 0, tzinfo=timezone.utc),
            datetime(2025, 1, 25, 4, 0, 0, tzinfo=timezone.utc),
        ]

        batch_result = cache.get_positions_batch(timestamps, body_id=1, interpolate=True)

        for i, ts in enumerate(timestamps):
            individual = cache.get_position(ts, body_id=1, interpolate=True)
            np.testing.assert_array_equal(
                batch_result[i, :], individual,
                err_msg=f"Timestamp {i} mismatch"
            )

    def test_get_positions_batch_single_timestamp(self, tmp_path):
        """get_positions_batch works with single timestamp."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        cache.ensure_month(2025, 1)

        timestamps = [datetime(2025, 1, 15, 0, 0, 0, tzinfo=timezone.utc)]
        result = cache.get_positions_batch(timestamps, body_id=0)

        assert result.shape == (1, POSITION_FIELDS)

    def test_get_positions_batch_no_interpolation(self, tmp_path):
        """get_positions_batch with interpolate=False returns midnight values."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        cache.ensure_month(2025, 1)

        timestamps = [
            datetime(2025, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            datetime(2025, 1, 10, 18, 0, 0, tzinfo=timezone.utc),
        ]

        result = cache.get_positions_batch(timestamps, body_id=0, interpolate=False)

        # Should be exact midnight values regardless of time
        data = cache._memory_cache[(2025, 1)]
        np.testing.assert_array_equal(result[0, :], data[4, 0, :])   # Jan 5 = index 4
        np.testing.assert_array_equal(result[1, :], data[9, 0, :])   # Jan 10 = index 9


class TestVectorizedEdgeCases:
    """Test vectorized edge cases (lines 372, 404-405)."""

    def test_vectorized_empty_input(self, tmp_path):
        """Empty input returns empty arrays (line 340-341)."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")

        lons, vels = cache.get_positions_vectorized([], body_id=0)

        assert isinstance(lons, np.ndarray)
        assert isinstance(vels, np.ndarray)
        assert lons.shape == (0,)
        assert vels.shape == (0,)
        assert lons.dtype == np.float32
        assert vels.dtype == np.float32

    def test_vectorized_cross_month_boundary(self, tmp_path):
        """Vectorized handles timestamps on last day of month (lines 404-405).

        When timestamps include the last day of a month, the vectorized code
        must use next month's data for interpolation at the month boundary.
        """
        cache = EphemerisCache(cache_dir=tmp_path / "cache")

        # Include timestamps on the last day of January (day 31)
        # at various times to force cross-month interpolation
        timestamps = [
            datetime(2025, 1, 31, 6, 0, 0, tzinfo=timezone.utc),
            datetime(2025, 1, 31, 12, 0, 0, tzinfo=timezone.utc),
            datetime(2025, 1, 31, 18, 0, 0, tzinfo=timezone.utc),
        ]

        lons, vels = cache.get_positions_vectorized(timestamps, body_id=0)

        assert lons.shape == (3,)
        assert vels.shape == (3,)

        # All longitudes in valid range
        assert np.all(lons >= 0)
        assert np.all(lons < 360)

        # Longitudes should increase (Sun moves forward)
        # At different times on the same day, later times should have slightly larger lon
        assert lons[1] > lons[0] or abs(lons[1] - lons[0]) < 1.0
        assert lons[2] > lons[1] or abs(lons[2] - lons[1]) < 1.0

    def test_vectorized_cross_year_boundary(self, tmp_path):
        """Vectorized handles December 31 to January 1 boundary."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")

        timestamps = [
            datetime(2024, 12, 31, 12, 0, 0, tzinfo=timezone.utc),
            datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        ]

        lons, vels = cache.get_positions_vectorized(timestamps, body_id=0)

        assert lons.shape == (3,)
        assert vels.shape == (3,)
        assert np.all(lons >= 0)
        assert np.all(lons < 360)

    def test_vectorized_matches_scalar_get_position(self, tmp_path):
        """Vectorized results match scalar get_position for same timestamps."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")

        timestamps = [
            datetime(2025, 1, 5, 6, 0, 0, tzinfo=timezone.utc),
            datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
            datetime(2025, 1, 25, 18, 0, 0, tzinfo=timezone.utc),
        ]

        # Vectorized path
        lons_vec, vels_vec = cache.get_positions_vectorized(timestamps, body_id=0)

        # Scalar path
        for i, ts in enumerate(timestamps):
            pos = cache.get_position(ts, body_id=0, interpolate=True)
            np.testing.assert_allclose(
                lons_vec[i], pos[0], atol=0.01,
                err_msg=f"Longitude mismatch at timestamp {i}"
            )
            np.testing.assert_allclose(
                vels_vec[i], pos[3], atol=0.01,
                err_msg=f"Velocity mismatch at timestamp {i}"
            )

    def test_vectorized_multiple_months(self, tmp_path):
        """Vectorized with timestamps spanning multiple months."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")

        timestamps = [
            datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
            datetime(2025, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            datetime(2025, 3, 15, 12, 0, 0, tzinfo=timezone.utc),
        ]

        lons, vels = cache.get_positions_vectorized(timestamps, body_id=0)

        assert lons.shape == (3,)
        assert np.all(lons >= 0)
        assert np.all(lons < 360)


class TestStaleCacheBodyCountMismatch:
    """Test stale cache recompute path (lines 158-159).

    Covers the case where a `.npy` file on disk was built with a different
    body count (e.g. 13 bodies pre-Chiron vs. 14 post-Chiron).  The cache
    must silently recompute and overwrite rather than returning wrong data.
    """

    def test_stale_cache_body_count_triggers_recompute(self, tmp_path):
        """Stale .npy file with wrong body count is recomputed transparently.

        Notes
        -----
        Creates a fake ``2025-01-ephemeris.npy`` with shape ``(31, 13, 6)``
        (pre-Chiron body count).  ensure_month must detect the mismatch
        (``shape[1] != BODY_COUNT``), recompute, overwrite the file, and
        load the fresh ``(31, 14, 6)`` data into memory.
        """
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()

        # Write a stale .npy file with the old 13-body shape
        stale_data = np.zeros((31, 13, 6), dtype=np.float32)
        stale_path = cache_dir / "2025-01-ephemeris.npy"
        np.save(stale_path, stale_data)
        assert stale_path.exists()

        cache = EphemerisCache(cache_dir=cache_dir)

        # ensure_month must detect shape[1]==13 != BODY_COUNT==14 and recompute
        cache.ensure_month(2025, 1)

        # Memory cache now has fresh 14-body data
        data = cache._memory_cache[(2025, 1)]
        assert data.shape[1] == BODY_COUNT, (
            f"Expected body count {BODY_COUNT} after stale-cache recompute, "
            f"got {data.shape[1]}"
        )

        # Disk file was overwritten with fresh data
        fresh_data = np.load(stale_path)
        assert fresh_data.shape[1] == BODY_COUNT, (
            f"Disk file still has stale body count {fresh_data.shape[1]}"
        )
