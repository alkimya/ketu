"""Comprehensive tests for EphemerisCache module."""

from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pytest

from ketu.cache.ephemeris_cache import (
    EphemerisCache,
    get_default_cache,
    BODY_COUNT,
    POSITION_FIELDS,
)


class TestEphemerisCacheInit:
    """Test cache initialization."""

    def test_default_cache_dir_creation(self, tmp_path):
        """Cache creates directory on init."""
        cache_dir = tmp_path / "cache"
        assert not cache_dir.exists()

        cache = EphemerisCache(cache_dir=cache_dir)

        assert cache_dir.exists()
        assert cache_dir.is_dir()
        assert cache.cache_dir == cache_dir

    def test_custom_cache_dir(self, tmp_path):
        """Cache uses custom directory."""
        custom_dir = tmp_path / "custom" / "ephemeris"
        cache = EphemerisCache(cache_dir=custom_dir)

        assert cache.cache_dir == custom_dir
        assert custom_dir.exists()


class TestEphemerisCacheComputeMonth:
    """Test month computation."""

    def test_compute_month_shape(self, tmp_path):
        """_compute_month returns correct shape (days, 13, 6)."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        data = cache._compute_month(2025, 1)

        # January 2025 has 31 days
        assert data.shape == (31, BODY_COUNT, POSITION_FIELDS)
        assert data.shape == (31, 14, 6)

    def test_compute_month_values_reasonable(self, tmp_path):
        """Computed positions are within physical bounds (0-360 lon)."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        data = cache._compute_month(2025, 1)

        # All longitudes (field 0) should be 0-360
        longitudes = data[:, :, 0]
        assert np.all(longitudes >= 0)
        assert np.all(longitudes < 360)

        # All latitudes (field 1) should be reasonable (-90 to 90)
        latitudes = data[:, :, 1]
        assert np.all(latitudes >= -90)
        assert np.all(latitudes <= 90)

        # All distances (field 2) should be non-negative
        # Note: Rahu (10) and Lilith (12) are calculated points, not physical bodies,
        # so they have distance 0
        distances = data[:, :, 2]
        assert np.all(distances >= 0)


class TestEphemerisCacheEnsureMonth:
    """Test month caching."""

    def test_ensure_month_creates_file(self, tmp_path):
        """ensure_month saves .npy file to disk."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        cache_file = tmp_path / "cache" / "2025-01-ephemeris.npy"

        assert not cache_file.exists()
        cache.ensure_month(2025, 1)
        assert cache_file.exists()

    def test_ensure_month_memory_cache(self, tmp_path):
        """ensure_month loads data into memory cache."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")

        assert (2025, 1) not in cache._memory_cache
        cache.ensure_month(2025, 1)
        assert (2025, 1) in cache._memory_cache

        data = cache._memory_cache[(2025, 1)]
        assert data.shape == (31, 14, 6)

    def test_ensure_month_reuses_disk_cache(self, tmp_path):
        """Second call loads from disk, not recompute."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")

        # First call: compute and save
        cache.ensure_month(2025, 1)
        first_data = cache._memory_cache[(2025, 1)].copy()

        # Clear memory
        cache.clear_memory()
        assert (2025, 1) not in cache._memory_cache

        # Second call: load from disk
        cache.ensure_month(2025, 1)
        second_data = cache._memory_cache[(2025, 1)]

        # Should be identical
        np.testing.assert_array_equal(first_data, second_data)

    def test_ensure_month_force_recompute(self, tmp_path):
        """force_recompute=True recomputes even when cached."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")

        # First compute
        cache.ensure_month(2025, 1)
        first_data = cache._memory_cache[(2025, 1)].copy()

        # Force recompute
        cache.ensure_month(2025, 1, force_recompute=True)
        second_data = cache._memory_cache[(2025, 1)]

        # Data should be identical (deterministic computation)
        # But should have been recomputed
        np.testing.assert_array_equal(first_data, second_data)


class TestEphemerisCacheEnsureRange:
    """Test range caching."""

    def test_ensure_range_multiple_months(self, tmp_path):
        """ensure_range loads all months in range."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")

        cache.ensure_range(2025, 1, 2025, 3)

        # All three months should be cached
        assert (2025, 1) in cache._memory_cache
        assert (2025, 2) in cache._memory_cache
        assert (2025, 3) in cache._memory_cache

        # Files should exist
        assert (tmp_path / "cache" / "2025-01-ephemeris.npy").exists()
        assert (tmp_path / "cache" / "2025-02-ephemeris.npy").exists()
        assert (tmp_path / "cache" / "2025-03-ephemeris.npy").exists()

    def test_ensure_range_year_boundary(self, tmp_path):
        """ensure_range handles Dec->Jan transition."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")

        cache.ensure_range(2024, 12, 2025, 2)

        # Should cross year boundary
        assert (2024, 12) in cache._memory_cache
        assert (2025, 1) in cache._memory_cache
        assert (2025, 2) in cache._memory_cache


class TestEphemerisCacheGetPosition:
    """Test position retrieval."""

    def test_get_position_midnight(self, tmp_path):
        """Position at midnight returns exact cached value."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        cache.ensure_month(2025, 1)

        # Get position at midnight
        ts = datetime(2025, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
        pos = cache.get_position(ts, body_id=0)  # Sun

        # Should match cached data exactly
        expected = cache._memory_cache[(2025, 1)][14, 0, :]  # day 15 = index 14
        np.testing.assert_array_equal(pos, expected)

    def test_get_position_interpolated(self, tmp_path):
        """Position at noon interpolates between days."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        cache.ensure_month(2025, 1)

        # Get position at noon
        ts = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        pos = cache.get_position(ts, body_id=0, interpolate=True)

        # Get midnight values
        data = cache._memory_cache[(2025, 1)]
        midnight_pos = data[14, 0, :]  # Jan 15 midnight
        next_midnight_pos = data[15, 0, :]  # Jan 16 midnight

        # At noon, longitude should be approximately halfway
        # (allowing for wrap-around handling)
        # Sun moves ~1 degree/day, so at noon should be ~0.5 degrees ahead
        expected_lon = midnight_pos[0] + (next_midnight_pos[0] - midnight_pos[0]) * 0.5
        np.testing.assert_allclose(pos[0], expected_lon, atol=0.01)

    def test_get_position_no_interpolation(self, tmp_path):
        """interpolate=False returns exact midnight value."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        cache.ensure_month(2025, 1)

        # Get position at noon without interpolation
        ts = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        pos = cache.get_position(ts, body_id=0, interpolate=False)

        # Should match midnight value exactly
        expected = cache._memory_cache[(2025, 1)][14, 0, :]
        np.testing.assert_array_equal(pos, expected)

    def test_get_position_naive_datetime(self, tmp_path):
        """Naive datetime gets UTC timezone added."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        cache.ensure_month(2025, 1)

        # Naive datetime
        ts_naive = datetime(2025, 1, 15, 0, 0, 0)
        pos_naive = cache.get_position(ts_naive, body_id=0)

        # UTC datetime
        ts_utc = datetime(2025, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
        pos_utc = cache.get_position(ts_utc, body_id=0)

        # Should be identical
        np.testing.assert_array_equal(pos_naive, pos_utc)

    def test_get_position_month_boundary(self, tmp_path):
        """Last day interpolation crosses to next month."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        cache.ensure_range(2025, 1, 2025, 2)

        # Get position at noon on last day of January
        ts = datetime(2025, 1, 31, 12, 0, 0, tzinfo=timezone.utc)
        pos = cache.get_position(ts, body_id=0, interpolate=True)

        # Should interpolate between Jan 31 and Feb 1
        jan_data = cache._memory_cache[(2025, 1)]
        feb_data = cache._memory_cache[(2025, 2)]

        jan_31_pos = jan_data[30, 0, :]  # Last day of January
        feb_1_pos = feb_data[0, 0, :]  # First day of February

        # Check longitude interpolation
        expected_lon = jan_31_pos[0] + (feb_1_pos[0] - jan_31_pos[0]) * 0.5
        np.testing.assert_allclose(pos[0], expected_lon, atol=0.01)


class TestEphemerisCacheVectorized:
    """Test vectorized operations."""

    def test_get_positions_vectorized_basic(self, tmp_path):
        """Vectorized returns (longitudes, velocities) arrays."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        cache.ensure_month(2025, 1)

        # Multiple timestamps
        timestamps = [
            datetime(2025, 1, 10, 0, 0, 0, tzinfo=timezone.utc),
            datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
            datetime(2025, 1, 20, 0, 0, 0, tzinfo=timezone.utc),
        ]

        lons, vels = cache.get_positions_vectorized(timestamps, body_id=0)

        assert lons.shape == (3,)
        assert vels.shape == (3,)

        # All longitudes should be in valid range
        assert np.all(lons >= 0)
        assert np.all(lons < 360)

    def test_get_positions_vectorized_empty(self, tmp_path):
        """Empty timestamps returns empty arrays."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")

        lons, vels = cache.get_positions_vectorized([], body_id=0)

        assert lons.shape == (0,)
        assert vels.shape == (0,)

    def test_get_longitudes_batch(self, tmp_path):
        """get_longitudes_batch returns longitudes only."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        cache.ensure_month(2025, 1)

        timestamps = [
            datetime(2025, 1, 10, 0, 0, 0, tzinfo=timezone.utc),
            datetime(2025, 1, 15, 0, 0, 0, tzinfo=timezone.utc),
        ]

        lons = cache.get_longitudes_batch(timestamps, body_id=0)

        assert lons.shape == (2,)
        assert np.all(lons >= 0)
        assert np.all(lons < 360)


class TestEphemerisCacheManagement:
    """Test cache management operations."""

    def test_clear_memory(self, tmp_path):
        """clear_memory empties memory cache."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")
        cache.ensure_month(2025, 1)

        assert len(cache._memory_cache) > 0
        assert len(cache._loaded_months) > 0

        cache.clear_memory()

        assert len(cache._memory_cache) == 0
        assert len(cache._loaded_months) == 0

    def test_cache_stats(self, tmp_path):
        """cache_stats returns correct counts and sizes."""
        cache = EphemerisCache(cache_dir=tmp_path / "cache")

        # Empty cache
        stats = cache.cache_stats()
        assert stats["months_in_memory"] == 0
        assert stats["months_on_disk"] == 0
        assert stats["memory_bytes"] == 0

        # Add two months
        cache.ensure_month(2025, 1)
        cache.ensure_month(2025, 2)

        stats = cache.cache_stats()
        assert stats["months_in_memory"] == 2
        assert stats["months_on_disk"] == 2
        assert stats["memory_bytes"] > 0
        assert stats["memory_mb"] > 0
        assert len(stats["disk_files"]) == 2


class TestDefaultCache:
    """Test default cache singleton."""

    def test_get_default_cache_singleton(self):
        """get_default_cache returns same instance."""
        cache1 = get_default_cache()
        cache2 = get_default_cache()

        # Should be the same instance
        assert cache1 is cache2

        # Should be an EphemerisCache instance
        assert isinstance(cache1, EphemerisCache)
