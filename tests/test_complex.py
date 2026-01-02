"""Tests for ketu.complex module - Complex number representation of cycles."""

import math
import pytest
import numpy as np

from ketu.complex import (
    ZodiacPoint,
    CycleRatio,
    Aspect,
    ASPECTS,
    ASPECTS_EXTENDED,
    circular_mean,
    circular_std,
    phase_locking_value,
    degrees_to_complex,
    radians_to_complex,
    complex_to_degrees,
    complex_to_radians,
    cycle_ratio_vectorized,
    nearest_aspect_vectorized,
    to_ml_features_vectorized,
)


class TestAspect:
    """Tests for Aspect class."""

    def test_aspect_from_degrees(self):
        """Test creating aspect from degrees."""
        conj = Aspect.from_degrees("conjunction", 0, orb=10.0)
        assert conj.name == "conjunction"
        assert conj.degrees == 0
        assert conj.radians == 0
        assert conj.z == complex(1, 0)
        assert conj.orb_default == 10.0

    def test_aspect_square(self):
        """Test square aspect (90°)."""
        square = ASPECTS["square"]
        assert square.degrees == 90
        assert abs(square.radians - math.pi / 2) < 1e-10
        # z should be approximately i
        assert abs(square.z.real) < 1e-10
        assert abs(square.z.imag - 1) < 1e-10

    def test_aspect_opposition(self):
        """Test opposition aspect (180°)."""
        opp = ASPECTS["opposition"]
        assert opp.degrees == 180
        assert abs(opp.radians - math.pi) < 1e-10
        # z should be -1
        assert abs(opp.z.real + 1) < 1e-10
        assert abs(opp.z.imag) < 1e-10

    def test_aspect_trine(self):
        """Test trine aspect (120°)."""
        trine = ASPECTS["trine"]
        assert trine.degrees == 120
        expected_z = complex(math.cos(math.radians(120)), math.sin(math.radians(120)))
        assert abs(trine.z - expected_z) < 1e-10

    def test_all_aspects_on_unit_circle(self):
        """All aspects should be on the unit circle."""
        for aspect in ASPECTS.values():
            assert abs(abs(aspect.z) - 1) < 1e-10

        for aspect in ASPECTS_EXTENDED.values():
            assert abs(abs(aspect.z) - 1) < 1e-10


class TestZodiacPoint:
    """Tests for ZodiacPoint class."""

    def test_from_degrees_basic(self):
        """Test creating point from degrees."""
        p = ZodiacPoint.from_degrees(90)
        assert abs(p.degrees - 90) < 1e-10
        assert abs(p.radians - math.pi / 2) < 1e-10
        assert abs(p.z.real) < 1e-10
        assert abs(p.z.imag - 1) < 1e-10

    def test_from_degrees_zero(self):
        """Test 0° point."""
        p = ZodiacPoint.from_degrees(0)
        assert abs(p.degrees) < 1e-10
        assert abs(p.z - 1) < 1e-10

    def test_from_degrees_normalization(self):
        """Test that degrees are normalized to [0, 360)."""
        p1 = ZodiacPoint.from_degrees(370)
        assert abs(p1.degrees - 10) < 1e-10

        p2 = ZodiacPoint.from_degrees(-30)
        assert abs(p2.degrees - 330) < 1e-10

    def test_from_radians(self):
        """Test creating point from radians."""
        p = ZodiacPoint.from_radians(math.pi)
        assert abs(p.degrees - 180) < 1e-10
        assert abs(p.z + 1) < 1e-10  # z = -1

    def test_from_complex(self):
        """Test creating point from complex number."""
        p = ZodiacPoint.from_complex(1j)
        assert abs(p.degrees - 90) < 1e-10

    def test_from_complex_normalization(self):
        """Test that non-unit complex numbers are normalized."""
        p = ZodiacPoint.from_complex(2 + 2j)  # |z| = 2√2
        assert abs(abs(p.z) - 1) < 1e-10
        assert abs(p.degrees - 45) < 1e-10

    def test_real_imag_properties(self):
        """Test real and imag properties."""
        p = ZodiacPoint.from_degrees(60)
        assert abs(p.real - 0.5) < 1e-10  # cos(60°) = 0.5
        assert abs(p.imag - math.sqrt(3) / 2) < 1e-10  # sin(60°)

    def test_division_creates_cycle_ratio(self):
        """Test that dividing points creates a CycleRatio."""
        p1 = ZodiacPoint.from_degrees(120)
        p2 = ZodiacPoint.from_degrees(90)
        ratio = p1 / p2
        assert isinstance(ratio, CycleRatio)
        assert abs(ratio.separation_degrees - 30) < 1e-10

    def test_multiplication(self):
        """Test that multiplying points adds angles."""
        p1 = ZodiacPoint.from_degrees(30)
        p2 = ZodiacPoint.from_degrees(45)
        result = p1 * p2
        assert abs(result.degrees - 75) < 1e-10

    def test_to_ml_features(self):
        """Test ML feature conversion."""
        p = ZodiacPoint.from_degrees(60)
        cos, sin = p.to_ml_features()
        assert abs(cos - 0.5) < 1e-10
        assert abs(sin - math.sqrt(3) / 2) < 1e-10

    def test_distance_to(self):
        """Test angular distance calculation."""
        p1 = ZodiacPoint.from_degrees(0)
        p2 = ZodiacPoint.from_degrees(90)
        assert abs(p1.distance_to(p2) - math.pi / 2) < 1e-10

        # Distance should be symmetric
        assert abs(p1.distance_to(p2) - p2.distance_to(p1)) < 1e-10

    def test_distance_to_opposition(self):
        """Test distance to opposite point."""
        p1 = ZodiacPoint.from_degrees(0)
        p2 = ZodiacPoint.from_degrees(180)
        assert abs(p1.distance_to(p2) - math.pi) < 1e-10


class TestCycleRatio:
    """Tests for CycleRatio class."""

    def test_basic_ratio(self):
        """Test basic cycle ratio calculation."""
        moon = ZodiacPoint.from_degrees(120)
        sun = ZodiacPoint.from_degrees(90)
        cycle = CycleRatio(moon, sun)

        assert abs(cycle.separation_degrees - 30) < 1e-10
        assert cycle.is_waxing

    def test_from_degrees(self):
        """Test creating ratio directly from degrees."""
        cycle = CycleRatio.from_degrees(90)
        assert abs(cycle.separation_degrees - 90) < 1e-10

    def test_from_radians(self):
        """Test creating ratio from radians."""
        cycle = CycleRatio.from_radians(math.pi / 2)
        assert abs(cycle.separation_degrees - 90) < 1e-10

    def test_waxing_waning(self):
        """Test waxing/waning detection."""
        waxing = CycleRatio.from_degrees(90)
        assert waxing.is_waxing
        assert not waxing.is_waning

        waning = CycleRatio.from_degrees(270)
        assert waning.is_waning
        assert not waning.is_waxing

    def test_cycle_progress(self):
        """Test cycle progress calculation."""
        cycle = CycleRatio.from_degrees(90)
        assert abs(cycle.cycle_progress - 0.25) < 1e-10

        cycle2 = CycleRatio.from_degrees(180)
        assert abs(cycle2.cycle_progress - 0.5) < 1e-10

    def test_distance_to_aspect_conjunction(self):
        """Test distance to conjunction."""
        # Exactly at conjunction
        cycle = CycleRatio.from_degrees(0)
        dist = cycle.distance_to_aspect("conjunction")
        assert abs(dist) < 1e-10

        # 10° past conjunction (separating)
        cycle2 = CycleRatio.from_degrees(10)
        dist2 = cycle2.distance_to_aspect("conjunction")
        assert dist2 > 0  # Positive = separating
        assert abs(dist2 - math.radians(10)) < 1e-10

        # 10° before conjunction (approaching from 350°)
        cycle3 = CycleRatio.from_degrees(350)
        dist3 = cycle3.distance_to_aspect("conjunction")
        assert dist3 < 0  # Negative = approaching
        assert abs(dist3 + math.radians(10)) < 1e-10

    def test_distance_to_aspect_square(self):
        """Test distance to square."""
        cycle = CycleRatio.from_degrees(90)
        dist = cycle.distance_to_aspect("square")
        assert abs(dist) < 1e-10

    def test_is_in_aspect(self):
        """Test aspect detection within orb."""
        # Exactly at trine
        cycle = CycleRatio.from_degrees(120)
        assert cycle.is_in_aspect("trine")

        # Within default orb (8°)
        cycle2 = CycleRatio.from_degrees(125)
        assert cycle2.is_in_aspect("trine")

        # Outside orb
        cycle3 = CycleRatio.from_degrees(110)
        assert not cycle3.is_in_aspect("trine")

        # Custom orb
        assert cycle3.is_in_aspect("trine", orb=15)

    def test_nearest_aspect(self):
        """Test finding nearest aspect."""
        # Near conjunction
        cycle = CycleRatio.from_degrees(5)
        aspect, dist = cycle.nearest_aspect
        assert aspect.name == "conjunction"
        assert abs(dist - math.radians(5)) < 1e-10

        # Near square
        cycle2 = CycleRatio.from_degrees(88)
        aspect2, dist2 = cycle2.nearest_aspect
        assert aspect2.name == "square"
        assert dist2 < 0  # Approaching

    def test_nearest_aspect_name(self):
        """Test nearest_aspect_name property."""
        cycle = CycleRatio.from_degrees(178)
        assert cycle.nearest_aspect_name == "opposition"

    def test_to_ml_features(self):
        """Test ML feature generation."""
        cycle = CycleRatio.from_degrees(90)
        features = cycle.to_ml_features()

        assert "cos_phase" in features
        assert "sin_phase" in features
        assert "cycle_progress" in features
        assert "is_waxing" in features
        assert "dist_conjunction" in features
        assert "dist_opposition" in features

        assert abs(features["cos_phase"]) < 1e-10  # cos(90°) = 0
        assert abs(features["sin_phase"] - 1) < 1e-10  # sin(90°) = 1
        assert abs(features["cycle_progress"] - 0.25) < 1e-10
        assert features["is_waxing"] == 1.0


class TestCircularStatistics:
    """Tests for circular statistics functions."""

    def test_circular_mean_single_point(self):
        """Test circular mean of single point."""
        p = ZodiacPoint.from_degrees(45)
        mean = circular_mean([p])
        assert abs(mean.degrees - 45) < 1e-10

    def test_circular_mean_two_points(self):
        """Test circular mean of two points."""
        p1 = ZodiacPoint.from_degrees(0)
        p2 = ZodiacPoint.from_degrees(90)
        mean = circular_mean([p1, p2])
        assert abs(mean.degrees - 45) < 1e-10

    def test_circular_mean_opposite_points(self):
        """Test circular mean of opposite points."""
        p1 = ZodiacPoint.from_degrees(0)
        p2 = ZodiacPoint.from_degrees(180)
        # Mean is undefined (resultant length = 0), but should not crash
        mean = circular_mean([p1, p2])
        # Result depends on implementation, just check it's valid
        assert 0 <= mean.degrees < 360

    def test_circular_mean_wrap_around(self):
        """Test circular mean handles wrap-around correctly."""
        p1 = ZodiacPoint.from_degrees(350)
        p2 = ZodiacPoint.from_degrees(10)
        mean = circular_mean([p1, p2])
        # Mean should be at 0° (or 360°)
        assert mean.degrees < 10 or mean.degrees > 350

    def test_circular_std_identical_points(self):
        """Test std of identical points is 0."""
        p = ZodiacPoint.from_degrees(45)
        std = circular_std([p, p, p])
        assert abs(std) < 1e-10

    def test_circular_std_spread_points(self):
        """Test std of spread points is positive."""
        points = [ZodiacPoint.from_degrees(d) for d in [0, 90, 180, 270]]
        std = circular_std(points)
        assert std > 0

    def test_circular_mean_empty_raises(self):
        """Test that empty sequence raises error."""
        with pytest.raises(ValueError):
            circular_mean([])

    def test_circular_std_empty_raises(self):
        """Test that empty sequence raises error."""
        with pytest.raises(ValueError):
            circular_std([])


class TestPhaseLockingValue:
    """Tests for phase_locking_value function."""

    def test_plv_perfect_sync(self):
        """Test PLV for perfectly synchronized series."""
        # Same phases = PLV = 1
        s1 = [ZodiacPoint.from_degrees(d) for d in [0, 30, 60, 90]]
        s2 = [ZodiacPoint.from_degrees(d) for d in [0, 30, 60, 90]]
        plv = phase_locking_value(s1, s2)
        assert abs(plv - 1.0) < 1e-10

    def test_plv_constant_offset(self):
        """Test PLV for constant phase offset."""
        # Constant 90° offset = PLV = 1
        s1 = [ZodiacPoint.from_degrees(d) for d in [0, 30, 60, 90]]
        s2 = [ZodiacPoint.from_degrees(d + 90) for d in [0, 30, 60, 90]]
        plv = phase_locking_value(s1, s2)
        assert abs(plv - 1.0) < 1e-10

    def test_plv_random_phases(self):
        """Test PLV for random phase differences."""
        # Random offsets = low PLV
        np.random.seed(42)
        offsets = np.random.uniform(0, 360, 100)
        s1 = [ZodiacPoint.from_degrees(d) for d in range(100)]
        s2 = [ZodiacPoint.from_degrees(d + off) for d, off in zip(range(100), offsets)]
        plv = phase_locking_value(s1, s2)
        assert plv < 0.5  # Should be low but not necessarily 0

    def test_plv_different_lengths_raises(self):
        """Test that different length series raises error."""
        s1 = [ZodiacPoint.from_degrees(0)]
        s2 = [ZodiacPoint.from_degrees(0), ZodiacPoint.from_degrees(90)]
        with pytest.raises(ValueError):
            phase_locking_value(s1, s2)


class TestVectorizedFunctions:
    """Tests for NumPy vectorized functions."""

    def test_degrees_to_complex(self):
        """Test vectorized degrees to complex conversion."""
        degrees = np.array([0, 90, 180, 270])
        z = degrees_to_complex(degrees)

        assert abs(z[0] - 1) < 1e-10
        assert abs(z[1] - 1j) < 1e-10
        assert abs(z[2] + 1) < 1e-10
        assert abs(z[3] + 1j) < 1e-10

    def test_radians_to_complex(self):
        """Test vectorized radians to complex conversion."""
        radians = np.array([0, np.pi / 2, np.pi])
        z = radians_to_complex(radians)

        assert abs(z[0] - 1) < 1e-10
        assert abs(z[1] - 1j) < 1e-10
        assert abs(z[2] + 1) < 1e-10

    def test_complex_to_degrees(self):
        """Test vectorized complex to degrees conversion."""
        z = np.array([1, 1j, -1, -1j])
        degrees = complex_to_degrees(z)

        assert abs(degrees[0] - 0) < 1e-10
        assert abs(degrees[1] - 90) < 1e-10
        assert abs(degrees[2] - 180) < 1e-10
        assert abs(degrees[3] - 270) < 1e-10

    def test_complex_to_radians(self):
        """Test vectorized complex to radians conversion."""
        z = np.array([1, 1j, -1])
        radians = complex_to_radians(z)

        assert abs(radians[0] - 0) < 1e-10
        assert abs(radians[1] - np.pi / 2) < 1e-10
        assert abs(radians[2] - np.pi) < 1e-10

    def test_cycle_ratio_vectorized(self):
        """Test vectorized cycle ratio calculation."""
        body1 = np.array([120, 90, 0])
        body2 = np.array([90, 90, 270])
        ratios = cycle_ratio_vectorized(body1, body2)

        # First: 120° - 90° = 30° separation
        sep1 = complex_to_degrees(np.array([ratios[0]]))[0]
        assert abs(sep1 - 30) < 1e-10

        # Second: 90° - 90° = 0° (conjunction)
        sep2 = complex_to_degrees(np.array([ratios[1]]))[0]
        assert abs(sep2) < 1e-10

    def test_nearest_aspect_vectorized(self):
        """Test vectorized nearest aspect finding."""
        z_ratios = degrees_to_complex(np.array([5, 88, 178, 122]))
        indices, angles, distances = nearest_aspect_vectorized(z_ratios)

        # 5° -> conjunction (0°)
        assert angles[0] == 0
        # 88° -> square (90°)
        assert angles[1] == 90
        # 178° -> opposition (180°)
        assert angles[2] == 180
        # 122° -> trine (120°)
        assert angles[3] == 120

    def test_to_ml_features_vectorized(self):
        """Test vectorized ML feature generation."""
        z_ratios = degrees_to_complex(np.array([0, 90, 180, 270]))
        features = to_ml_features_vectorized(z_ratios)

        assert features.shape == (4, 6)

        # Check cos_phase column (index 0)
        assert abs(features[0, 0] - 1) < 1e-10  # cos(0°) = 1
        assert abs(features[1, 0]) < 1e-10  # cos(90°) = 0
        assert abs(features[2, 0] + 1) < 1e-10  # cos(180°) = -1

        # Check sin_phase column (index 1)
        assert abs(features[0, 1]) < 1e-10  # sin(0°) = 0
        assert abs(features[1, 1] - 1) < 1e-10  # sin(90°) = 1

        # Check cycle_progress column (index 2)
        assert abs(features[0, 2] - 0) < 1e-10  # 0°
        assert abs(features[1, 2] - 0.25) < 1e-10  # 90°
        assert abs(features[2, 2] - 0.5) < 1e-10  # 180°

        # Check is_waxing column (index 3)
        assert features[0, 3] == 1.0  # 0° is waxing
        assert features[1, 3] == 1.0  # 90° is waxing
        assert features[2, 3] == 0.0  # 180° is waning (boundary)
        assert features[3, 3] == 0.0  # 270° is waning


class TestIntegrationWithCycles:
    """Integration tests with existing cycle data structures."""

    def test_convert_cycle_dtype_to_complex(self):
        """Test converting from CYCLE_DTYPE to complex representation."""
        # Simulate data from generate_cycle_series
        body1_lon = 120.0
        body2_lon = 90.0

        # Create ZodiacPoints
        p1 = ZodiacPoint.from_degrees(body1_lon)
        p2 = ZodiacPoint.from_degrees(body2_lon)
        cycle = p1 / p2

        # Verify it matches expected separation
        expected_sep = (body1_lon - body2_lon) % 360
        assert abs(cycle.separation_degrees - expected_sep) < 1e-10

    def test_batch_conversion(self):
        """Test batch conversion of cycle data."""
        # Simulate a year of daily data
        n_days = 365
        np.random.seed(42)

        # Simulated Moon-Sun positions
        moon_lons = np.cumsum(np.random.normal(13, 0.5, n_days)) % 360
        sun_lons = np.cumsum(np.random.normal(1, 0.1, n_days)) % 360

        # Convert to complex ratios
        z_ratios = cycle_ratio_vectorized(moon_lons, sun_lons)

        # Get ML features
        features = to_ml_features_vectorized(z_ratios)

        assert features.shape == (n_days, 6)
        assert np.all(features[:, 2] >= 0)  # cycle_progress >= 0
        assert np.all(features[:, 2] < 1)  # cycle_progress < 1
