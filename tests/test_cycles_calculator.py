"""Comprehensive tests for ketu.cycles.calculator module.

Tests target all uncovered paths including:
- Body ID resolution (_get_body_id)
- Timestamp conversion paths (datetime, datetime64, Julian dates, pandas)
- Cache integration (enabled/disabled paths)
- Edge cases (0/360 degree boundaries, oppositions)
- Multi-cycle series generation
"""

from datetime import datetime, timezone, timedelta
import numpy as np
import pytest

from ketu.cycles.calculator import (
    generate_cycle_series,
    generate_multi_cycle_series,
    _get_body_id,
    CYCLE_DTYPE,
    DEFAULT_PAIRS,
)


class TestGetBodyId:
    """Test body ID resolution from names and integers."""

    def test_body_id_from_int(self):
        """Integer body ID passes through directly."""
        # Tests line 103
        body_id = _get_body_id(0)  # Sun
        assert body_id == 0

        body_id = _get_body_id(1)  # Moon
        assert body_id == 1

    def test_body_id_from_name(self):
        """String body name resolves to correct ID."""
        assert _get_body_id("Sun") == 0
        assert _get_body_id("Moon") == 1
        assert _get_body_id("Mercury") == 2
        assert _get_body_id("Venus") == 3
        assert _get_body_id("Mars") == 4
        assert _get_body_id("Jupiter") == 5
        assert _get_body_id("Saturn") == 6

    def test_body_id_unknown_raises(self):
        """Unknown body name raises ValueError."""
        # Tests line 106
        with pytest.raises(ValueError, match="Unknown body"):
            _get_body_id("InvalidName")

        with pytest.raises(ValueError, match="Unknown body"):
            _get_body_id("FakeBody")


class TestGenerateCycleSeriesTimestamps:
    """Test different timestamp input formats."""

    def test_datetime_list_input(self):
        """List of datetime objects works."""
        timestamps = [
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            datetime(2025, 1, 15, tzinfo=timezone.utc),
            datetime(2025, 2, 1, tzinfo=timezone.utc),
        ]

        result = generate_cycle_series("Sun", "Moon", timestamps, include_aspects=False)

        assert len(result) == 3
        assert result.dtype == CYCLE_DTYPE
        assert result['body1_id'][0] == 0  # Sun
        assert result['body2_id'][0] == 1  # Moon

    def test_julian_date_array_input(self):
        """Float array (Julian dates) works."""
        # Julian dates for 2025-01-01, 2025-01-15, 2025-02-01
        jds = np.array([2460676.5, 2460690.5, 2460707.5])

        result = generate_cycle_series("Sun", "Moon", jds, include_aspects=False)

        assert len(result) == 3
        assert result.dtype == CYCLE_DTYPE

    def test_numpy_datetime64_input(self):
        """numpy datetime64 array converts correctly."""
        # Tests lines 154-155
        timestamps = np.array(['2025-01-01', '2025-01-15', '2025-02-01'], dtype='datetime64[D]')

        # use_cache=False to force direct conversion path
        result = generate_cycle_series("Sun", "Moon", timestamps, include_aspects=False, use_cache=False)

        assert len(result) == 3
        assert result.dtype == CYCLE_DTYPE
        # Verify Julian dates are in reasonable range
        assert np.all(result['julian_day'] > 2460000)  # After 2024
        assert np.all(result['julian_day'] < 2470000)  # Before 2050

    def test_unsupported_dtype_raises(self):
        """Unsupported numpy dtype raises ValueError."""
        # Tests line 159
        timestamps = np.array([1, 2, 3], dtype='i4')  # Integer dtype

        with pytest.raises(ValueError, match="unsupported timestamp dtype"):
            generate_cycle_series("Sun", "Moon", timestamps)

    def test_pandas_datetimeindex_input(self):
        """pandas DatetimeIndex input works if pandas available."""
        # Tests lines 149-150
        try:
            import pandas as pd
        except ImportError:
            pytest.skip("pandas not available")

        # Create pandas DatetimeIndex
        timestamps = pd.date_range('2025-01-01', periods=3, freq='D', tz='UTC')

        result = generate_cycle_series("Sun", "Moon", timestamps, include_aspects=False, use_cache=False)

        assert len(result) == 3
        assert result.dtype == CYCLE_DTYPE


class TestGenerateCycleSeriesOutput:
    """Test output structure and value ranges."""

    def test_output_dtype_matches_cycle_dtype(self):
        """Output structured array has CYCLE_DTYPE."""
        timestamps = [
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            datetime(2025, 1, 15, tzinfo=timezone.utc),
        ]

        result = generate_cycle_series("Sun", "Moon", timestamps)

        assert result.dtype == CYCLE_DTYPE
        # Check all fields exist
        expected_fields = [
            'julian_day', 'body1_id', 'body2_id', 'body1_lon', 'body2_lon',
            'angular_separation', 'cycle_progress', 'cycle_phase',
            'body1_velocity', 'body2_velocity', 'relative_velocity',
            'body1_retro', 'body2_retro', 'nearest_aspect', 'aspect_distance',
            'in_aspect', 'aspect_orb'
        ]
        for field in expected_fields:
            assert field in result.dtype.names

    def test_angular_separation_range(self):
        """Angular separation always in 0-360 range."""
        timestamps = [datetime(2025, 1, 1, tzinfo=timezone.utc) + timedelta(days=i) for i in range(30)]

        result = generate_cycle_series("Sun", "Moon", timestamps, include_aspects=False)

        # Use assert_allclose for boundary checks
        np.testing.assert_array_less(-0.1, result['angular_separation'],
                                     err_msg="Angular separation should be >= 0")
        np.testing.assert_array_less(result['angular_separation'], 360.1,
                                     err_msg="Angular separation should be < 360")

    def test_cycle_progress_range(self):
        """Cycle progress always in 0-1 range."""
        timestamps = [datetime(2025, 1, 1, tzinfo=timezone.utc) + timedelta(days=i) for i in range(30)]

        result = generate_cycle_series("Sun", "Moon", timestamps, include_aspects=False)

        np.testing.assert_array_less(-0.001, result['cycle_progress'],
                                     err_msg="Cycle progress should be >= 0")
        np.testing.assert_array_less(result['cycle_progress'], 1.001,
                                     err_msg="Cycle progress should be <= 1")

    def test_aspect_proximity_calculated(self):
        """include_aspects=True fills aspect fields."""
        timestamps = [datetime(2025, 1, 1, tzinfo=timezone.utc)]

        result = generate_cycle_series("Sun", "Moon", timestamps, include_aspects=True)

        # Check that aspect fields are filled
        assert result['nearest_aspect'][0] >= 0
        assert result['nearest_aspect'][0] <= 360
        # aspect_distance should be in (-180, 180] typically
        assert abs(result['aspect_distance'][0]) <= 180

    def test_no_aspects_when_disabled(self):
        """include_aspects=False leaves aspect fields zero."""
        timestamps = [datetime(2025, 1, 1, tzinfo=timezone.utc)]

        result = generate_cycle_series("Sun", "Moon", timestamps, include_aspects=False)

        # Aspect fields should be zero when disabled
        np.testing.assert_allclose(result['nearest_aspect'], 0.0, atol=1e-6,
                                   err_msg="nearest_aspect should be 0 when aspects disabled")
        np.testing.assert_allclose(result['aspect_distance'], 0.0, atol=1e-6,
                                   err_msg="aspect_distance should be 0 when aspects disabled")
        assert not result['in_aspect'][0]
        np.testing.assert_allclose(result['aspect_orb'], 0.0, atol=1e-6,
                                   err_msg="aspect_orb should be 0 when aspects disabled")


class TestGenerateCycleSeriesCachePath:
    """Test cache-enabled and cache-disabled code paths."""

    def test_cache_disabled(self):
        """use_cache=False uses direct calculation."""
        # Tests fallback path (lines 201+)
        timestamps = [
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            datetime(2025, 1, 15, tzinfo=timezone.utc),
        ]

        result = generate_cycle_series("Sun", "Moon", timestamps, use_cache=False, include_aspects=False)

        assert len(result) == 2
        assert result['body1_id'][0] == 0
        assert result['body2_id'][0] == 1
        # Verify that longitudes are calculated
        assert result['body1_lon'][0] > 0
        assert result['body2_lon'][0] > 0

    def test_cache_enabled_with_datetimes(self, tmp_path):
        """use_cache=True with datetime list uses cache."""
        # Tests lines 184-200
        from ketu.cache import EphemerisCache

        cache_file = tmp_path / "test_cache.sqlite"
        cache = EphemerisCache(str(cache_file))

        timestamps = [
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            datetime(2025, 1, 15, tzinfo=timezone.utc),
        ]

        result = generate_cycle_series("Sun", "Moon", timestamps, use_cache=True, cache=cache, include_aspects=False)

        assert len(result) == 2
        # Verify positions were computed
        assert result['body1_lon'][0] > 0
        assert result['body2_lon'][0] > 0


class TestGenerateMultiCycleSeries:
    """Test multi-cycle series generation."""

    def test_multi_series_returns_dict(self):
        """Returns dict keyed by pair names."""
        # Tests lines 301-327
        pairs = [("Sun", "Moon"), ("Sun", "Mars")]
        timestamps = [
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            datetime(2025, 1, 15, tzinfo=timezone.utc),
        ]

        result = generate_multi_cycle_series(pairs, timestamps, include_aspects=False)

        assert isinstance(result, dict)
        assert len(result) == 2
        assert "Sun-Moon" in result
        assert "Sun-Mars" in result

    def test_multi_series_pair_names(self):
        """Pair names formatted as 'Body1-Body2'."""
        pairs = [("Sun", "Moon"), ("Jupiter", "Saturn")]
        timestamps = [datetime(2025, 1, 1, tzinfo=timezone.utc)]

        result = generate_multi_cycle_series(pairs, timestamps, include_aspects=False)

        assert "Sun-Moon" in result
        assert "Jupiter-Saturn" in result
        # Verify arrays are valid
        assert len(result["Sun-Moon"]) == 1
        assert len(result["Jupiter-Saturn"]) == 1

    def test_multi_series_with_int_body_ids(self):
        """Integer body IDs resolve to names in dict keys."""
        pairs = [(0, 1), (5, 6)]  # (Sun, Moon), (Jupiter, Saturn)
        timestamps = [datetime(2025, 1, 1, tzinfo=timezone.utc)]

        result = generate_multi_cycle_series(pairs, timestamps, include_aspects=False)

        assert "Sun-Moon" in result
        assert "Jupiter-Saturn" in result

    def test_multi_series_uses_default_pairs(self):
        """DEFAULT_PAIRS can be used with generate_multi_cycle_series."""
        timestamps = [datetime(2025, 1, 1, tzinfo=timezone.utc)]

        result = generate_multi_cycle_series(DEFAULT_PAIRS, timestamps, include_aspects=False)

        assert len(result) == len(DEFAULT_PAIRS)
        # Check a few expected pairs
        assert "Sun-Moon" in result
        assert "Sun-Mars" in result
        assert "Jupiter-Saturn" in result


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_degree_separation(self):
        """Conjunction (0 deg) handled correctly."""
        # New Moon on 2025-01-29 (Sun-Moon conjunction)
        timestamps = [datetime(2025, 1, 29, 12, 0, tzinfo=timezone.utc)]

        result = generate_cycle_series("Sun", "Moon", timestamps, include_aspects=False)

        # Angular separation should be close to 0 (within a few degrees)
        np.testing.assert_allclose(result['angular_separation'][0], 0.0, atol=15.0,
                                   err_msg="Conjunction should have angular separation near 0")
        # Cycle progress should be near 0 or 1
        assert result['cycle_progress'][0] < 0.05 or result['cycle_progress'][0] > 0.95

    def test_opposition_180_degrees(self):
        """Opposition (180 deg) boundary handled."""
        # Full Moon on 2025-02-12 (Sun-Moon opposition)
        timestamps = [datetime(2025, 2, 12, 12, 0, tzinfo=timezone.utc)]

        result = generate_cycle_series("Sun", "Moon", timestamps, include_aspects=False)

        # Angular separation should be close to 180 degrees
        np.testing.assert_allclose(result['angular_separation'][0], 180.0, atol=15.0,
                                   err_msg="Opposition should have angular separation near 180")
        # Cycle progress should be near 0.5
        np.testing.assert_allclose(result['cycle_progress'][0], 0.5, atol=0.05,
                                   err_msg="Opposition should have cycle progress near 0.5")

    def test_near_360_degree_separation(self):
        """Near-360 deg wraps correctly (not negative)."""
        # Use multiple timestamps around new moon
        timestamps = [
            datetime(2025, 1, 28, 12, 0, tzinfo=timezone.utc),  # Day before new moon
            datetime(2025, 1, 29, 12, 0, tzinfo=timezone.utc),  # New moon
            datetime(2025, 1, 30, 12, 0, tzinfo=timezone.utc),  # Day after new moon
        ]

        result = generate_cycle_series("Sun", "Moon", timestamps, include_aspects=False)

        # All angular separations should be positive (0-360 range)
        np.testing.assert_array_less(-0.1, result['angular_separation'],
                                     err_msg="Angular separation should never be negative")
        np.testing.assert_array_less(result['angular_separation'], 360.1,
                                     err_msg="Angular separation should not exceed 360")

    def test_cycle_phase_transitions(self):
        """Cycle phase correctly transitions at 180 degrees."""
        # Sample across a full lunation cycle
        timestamps = [datetime(2025, 1, 1, tzinfo=timezone.utc) + timedelta(days=i) for i in range(30)]

        result = generate_cycle_series("Sun", "Moon", timestamps, include_aspects=False)

        # cycle_phase should be 1 (waxing) when separation < 180
        waxing = result['angular_separation'] < 180
        waning = result['angular_separation'] >= 180

        np.testing.assert_array_equal(result['cycle_phase'][waxing], 1,
                                      err_msg="Phase should be 1 (waxing) when separation < 180")
        np.testing.assert_array_equal(result['cycle_phase'][waning], -1,
                                      err_msg="Phase should be -1 (waning) when separation >= 180")

    def test_velocity_calculations(self):
        """Body velocities and relative velocity calculated correctly."""
        timestamps = [datetime(2025, 1, 1, tzinfo=timezone.utc)]

        result = generate_cycle_series("Sun", "Moon", timestamps, include_aspects=False)

        # Sun velocity should be ~1 deg/day
        np.testing.assert_allclose(result['body1_velocity'][0], 1.0, atol=0.2,
                                   err_msg="Sun velocity should be ~1 deg/day")
        # Moon velocity should be ~12-15 deg/day
        assert 10 < result['body2_velocity'][0] < 16, "Moon velocity should be ~12-15 deg/day"
        # Relative velocity should be Moon - Sun
        np.testing.assert_allclose(result['relative_velocity'][0],
                                   result['body2_velocity'][0] - result['body1_velocity'][0],
                                   atol=1e-6,
                                   err_msg="Relative velocity should equal body2_velocity - body1_velocity")
