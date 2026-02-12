"""Tests for standardized error messages (QAL-01) and complex math integration (CPX-01)."""
import pytest
import numpy as np
from datetime import datetime, timezone, timedelta

from ketu.cycles.calculator import _get_body_id, generate_cycle_series, CYCLE_DTYPE
from ketu.ephemeris.planets import calc_planet_position
from ketu.aspects.core import get_aspect_index


class TestErrorMessages:
    """Verify error messages follow standardized format."""

    def test_unknown_body_in_cycle_calculator(self):
        """Test _get_body_id raises ValueError with standardized message for unknown body."""
        with pytest.raises(ValueError, match=r"[Uu]nknown body:.*InvalidPlanet.*Valid bodies"):
            _get_body_id("InvalidPlanet")

    def test_unknown_planet_id(self):
        """Test calc_planet_position raises ValueError with standardized message for invalid ID."""
        jd = 2451545.0  # J2000.0
        with pytest.raises(ValueError, match=r"unknown planet ID: 99.*Valid range: 0-12"):
            calc_planet_position(jd, 99)

    def test_unknown_aspect_name(self):
        """Test get_aspect_index raises ValueError with standardized message for unknown aspect."""
        with pytest.raises(ValueError, match=r"unknown aspect name: 'nonexistent'.*Valid aspects"):
            get_aspect_index("nonexistent")

    def test_unsupported_timestamp_dtype(self):
        """Test generate_cycle_series raises ValueError for unsupported dtype."""
        timestamps = np.array([1, 2, 3], dtype='i4')  # Integer dtype
        with pytest.raises(ValueError, match=r"[Uu]nsupported timestamp dtype.*Expected datetime64.*or float"):
            generate_cycle_series("Sun", "Moon", timestamps)


class TestComplexMathIntegration:
    """Verify CPX-01: complex math internal, degrees external."""

    def test_cycle_series_output_in_degrees(self):
        """Test that generate_cycle_series returns degree-valued fields in [0, 360)."""
        # Generate a week of timestamps
        start = datetime(2025, 1, 1, tzinfo=timezone.utc)
        timestamps = [start + timedelta(hours=i) for i in range(168)]  # 7 days

        # Generate cycle series
        cycles = generate_cycle_series("Sun", "Moon", timestamps)

        # Verify angular_separation is in [0, 360)
        assert np.all(cycles['angular_separation'] >= 0)
        assert np.all(cycles['angular_separation'] < 360)

        # Verify body longitudes are in [0, 360)
        assert np.all(cycles['body1_lon'] >= 0)
        assert np.all(cycles['body1_lon'] < 360)
        assert np.all(cycles['body2_lon'] >= 0)
        assert np.all(cycles['body2_lon'] < 360)

        # Verify cycle_progress is in [0, 1)
        assert np.all(cycles['cycle_progress'] >= 0)
        assert np.all(cycles['cycle_progress'] < 1)

        # Verify nearest_aspect is a valid aspect angle (0-360)
        assert np.all(cycles['nearest_aspect'] >= 0)
        assert np.all(cycles['nearest_aspect'] <= 360)

    def test_cycle_dtype_no_complex_fields(self):
        """Test that CYCLE_DTYPE has no complex-valued fields."""
        # Get all field types
        field_types = [CYCLE_DTYPE.fields[name][0].kind for name in CYCLE_DTYPE.names]

        # Valid numeric types (no complex 'c' type)
        valid_types = {'f', 'i', 'b', 'U', 'M'}  # float, int, bool, unicode, datetime

        for field_name, field_kind in zip(CYCLE_DTYPE.names, field_types):
            assert field_kind in valid_types, (
                f"Field '{field_name}' has complex or invalid type '{field_kind}'. "
                f"Expected one of {valid_types}"
            )

    def test_complex_functions_available_in_calculator(self):
        """Test that complex math functions are available in calculator module."""
        from ketu.cycles import calculator

        # Verify complex math functions exist
        assert hasattr(calculator, 'cycle_ratio_vectorized'), (
            "cycle_ratio_vectorized not found in calculator module"
        )
        assert hasattr(calculator, 'complex_to_degrees'), (
            "complex_to_degrees not found in calculator module"
        )

        # Verify they're used (imported from ketu.complex)
        from ketu.complex import cycle_ratio_vectorized, complex_to_degrees

        assert calculator.cycle_ratio_vectorized is cycle_ratio_vectorized
        assert calculator.complex_to_degrees is complex_to_degrees

    def test_cycle_progress_matches_separation(self):
        """Test that cycle_progress equals angular_separation / 360."""
        start = datetime(2025, 1, 1, tzinfo=timezone.utc)
        timestamps = [start + timedelta(days=i) for i in range(30)]

        cycles = generate_cycle_series("Sun", "Moon", timestamps)

        # cycle_progress should equal angular_separation / 360
        expected_progress = cycles['angular_separation'] / 360.0
        np.testing.assert_allclose(cycles['cycle_progress'], expected_progress, rtol=1e-6)

    def test_angular_separation_continuous(self):
        """Test that angular_separation changes smoothly (no discontinuities at 0/360 boundary)."""
        start = datetime(2025, 1, 20, tzinfo=timezone.utc)  # Near new moon
        timestamps = [start + timedelta(hours=i) for i in range(72)]  # 3 days

        cycles = generate_cycle_series("Sun", "Moon", timestamps)

        # Check for discontinuities (jumps > 30 degrees in 1 hour)
        diffs = np.diff(cycles['angular_separation'])

        # Handle 360->0 wrapping: if diff < -300, it's a wrap forward
        # if diff > 300, it's a wrap backward
        adjusted_diffs = np.where(diffs < -300, diffs + 360, diffs)
        adjusted_diffs = np.where(adjusted_diffs > 300, adjusted_diffs - 360, adjusted_diffs)

        # Moon moves ~0.5 degrees per hour relative to Sun
        # So max change in 1 hour should be < 1 degree
        assert np.all(np.abs(adjusted_diffs) < 1.0), (
            f"Found discontinuity in angular_separation. Max jump: {np.max(np.abs(adjusted_diffs))}"
        )
