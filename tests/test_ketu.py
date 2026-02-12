"""Tests for Ketu library v0.1.0"""

import pytest
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo

import ketu
from ketu.core import bodies, aspects as aspects_data, signs
from ketu.calculations import (
    local_to_utc,
    utc_to_julian,
    body_name,
    body_id,
    body_properties,
    long,
    longitude,
    lat,
    dist_au,
    vlong,
    longitude_velocity,
    is_retrograde,
    is_ascending,
    body_sign,
    positions,
    decimal_degrees_to_dms,
    distance,
)
from ketu.aspects import get_aspect, calculate_aspects, get_orb
from ketu.display import print_positions, print_aspects, main


class TestData:
    """Test data structures"""

    def test_bodies_structure(self):
        """Test bodies array structure and content"""
        assert len(bodies) == 13
        assert bodies["id"][0] == 0  # Sun
        assert bodies["id"][1] == 1  # Moon
        assert bodies["name"][0] == b"Sun"
        assert bodies["orb"][0] == 12.0
        assert bodies["speed"][1] > 13.0  # Moon speed ~13°/day

    def test_aspects_structure(self):
        """Test aspects array structure and content"""
        assert len(aspects_data) == 14
        assert aspects_data["angle"][0] == 0  # Conjunction
        assert aspects_data["angle"][13] == 180  # Opposition
        assert aspects_data["name"][7] == b"Square"
        assert aspects_data["coef"][9] == 2 / 3  # Trine coefficient

    def test_signs_list(self):
        """Test zodiac signs list"""
        assert len(signs) == 12
        assert signs[0] == "Aries"
        assert signs[2] == "Gemini"
        assert signs[11] == "Pisces"


class TestTimeConversions:
    """Test time conversion functions"""

    def setup_method(self):
        """Setup test data"""
        self.paris_tz = ZoneInfo("Europe/Paris")
        self.utc_tz = ZoneInfo("UTC")
        self.test_date = datetime(2020, 12, 21, 19, 20, 0, tzinfo=self.paris_tz)
        self.day_one = datetime(1, 1, 1)

    def test_local_to_utc(self):
        """Test local to UTC conversion"""
        utc_time = local_to_utc(self.test_date)
        assert utc_time.hour == 18  # Paris is UTC+1 in winter
        assert utc_time.minute == 20

    def test_utc_to_julian(self):
        """Test UTC to Julian Day conversion"""
        jday = utc_to_julian(self.test_date)
        assert isinstance(jday, float)
        assert jday > 2459000  # Approximate JD for 2020

        # Test epoch (NumPy implementation uses Gregorian proleptic calendar)
        jday_epoch = utc_to_julian(self.day_one)
        assert jday_epoch == 1721423.5


class TestAngleConversions:
    """Test angle conversion functions"""

    def test_decimal_degrees_to_dms(self):
        """Test decimal degrees to DMS conversion"""
        result = decimal_degrees_to_dms(123.456)
        assert result[0] == 123  # degrees
        assert result[1] == 27  # minutes
        assert result[2] == 21  # seconds

        # Test with exact degrees
        result = decimal_degrees_to_dms(90.0)
        assert result[0] == 90
        assert result[1] == 0
        assert result[2] == 0

    def test_distance(self):
        """Test angular distance calculation"""
        # Simple cases
        assert distance(0, 90) == 90
        assert distance(0, 180) == 180
        assert distance(0, 270) == 90  # Shortest path

        # Wraparound
        assert distance(350, 10) == 20
        assert distance(10, 350) == 20

    def test_get_orb(self):
        """Test orb calculation for aspects"""
        # Sun-Moon conjunction
        orb = get_orb(0, 1, 0)  # bodies 0,1, aspect 0 (conjunction)
        assert orb == 12.0  # (12+12)/2 * 1

        # Mercury-Venus sextile
        orb = get_orb(2, 3, 4)  # bodies 2,3, aspect 4 (sextile)
        assert orb == 9.0 * (1 / 3)  # (10+8)/2 * 1/3


class TestBodyFunctions:
    """Test body-related functions"""

    def setup_method(self):
        """Setup test data"""
        self.test_date = datetime(2020, 12, 21, 19, 20, tzinfo=ZoneInfo("Europe/Paris"))
        self.jday = utc_to_julian(self.test_date)

    def test_body_name(self):
        """Test body name retrieval"""
        assert body_name(0) == "Sun"
        assert body_name(1) == "Moon"
        assert body_name(10) == "Rahu"
        assert body_name(12) == "Lilith"

    def test_body_id(self):
        """Test body ID retrieval by name"""
        assert body_id("Sun") == 0
        assert body_id("Moon") == 1
        assert body_id("Mars") == 4

    def test_body_properties(self):
        """Test body properties calculation"""
        props = body_properties(self.jday, 0)  # Sun
        assert isinstance(props, np.ndarray)
        assert len(props) == 6  # long, lat, dist, vlong, vlat, vdist
        assert 0 <= props[0] <= 360  # longitude in range

    def test_long_lat_dist(self):
        """Test individual position functions"""
        sun_long = long(self.jday, 0)
        sun_lat = lat(self.jday, 0)
        sun_dist = dist_au(self.jday, 0)

        assert 0 <= sun_long <= 360
        assert -90 <= sun_lat <= 90
        assert 0.98 <= sun_dist <= 1.02  # Sun distance ~1 AU

    def test_velocities(self):
        """Test velocity functions"""
        moon_vlong = vlong(self.jday, 1)
        assert 10 <= abs(moon_vlong) <= 16  # Moon moves 10-16°/day

        # Test retrograde detection
        mars_retro = is_retrograde(self.jday, 4)
        assert isinstance(mars_retro, bool)

    def test_is_ascending(self):
        """Test latitude ascending detection"""
        moon_ascending = is_ascending(self.jday, 1)
        assert isinstance(moon_ascending, bool)

    def test_body_sign(self):
        """Test zodiac sign calculation"""
        # Test Capricorn (270-300°)
        sign_data = body_sign(271.5)
        assert sign_data[0] == 9  # Capricorn index
        assert sign_data[1] == 1  # 1 degree
        assert sign_data[2] == 30  # 30 minutes

        # Test Aries (0-30°)
        sign_data = body_sign(15.25)
        assert sign_data[0] == 0  # Aries index
        assert sign_data[1] == 15  # 15 degrees
        assert sign_data[2] == 15  # 15 minutes

    def test_positions(self):
        """Test all positions calculation"""
        all_positions = positions(self.jday)
        assert isinstance(all_positions, np.ndarray)
        assert len(all_positions) == len(bodies)
        assert all(0 <= pos <= 360 for pos in all_positions)


class TestAspects:
    """Test aspect calculation functions"""

    def setup_method(self):
        """Setup test data"""
        self.test_date = datetime(2020, 12, 21, 19, 20, tzinfo=ZoneInfo("Europe/Paris"))
        self.jday = utc_to_julian(self.test_date)

    def test_get_aspect(self):
        """Test aspect detection between two bodies"""
        # Test Sun-Moon aspect
        aspect = get_aspect(self.jday, 0, 1)

        if aspect is not None:
            body1, body2, asp_type, orb = aspect
            assert body1 == 0  # Sun
            assert body2 == 1  # Moon
            assert 0 <= asp_type < 14  # Valid aspect type
            assert isinstance(orb, (float, np.floating))

    def test_calculate_aspects(self):
        """Test all aspects calculation"""
        aspects = calculate_aspects(self.jday)

        assert isinstance(aspects, np.ndarray)

        # Check structure if aspects exist
        if len(aspects) > 0:
            # Each aspect should have 4 fields
            assert aspects.dtype.names == ("body1", "body2", "i_asp", "orb")

            # Check first aspect
            first = aspects[0]
            assert 0 <= first["body1"] < len(bodies)
            assert 0 <= first["body2"] < len(bodies)
            assert 0 <= first["i_asp"] < len(aspects_data)


class TestDisplay:
    """Test display functions"""

    def setup_method(self):
        """Setup test data"""
        self.test_date = datetime(2020, 12, 21, 19, 20, tzinfo=ZoneInfo("Europe/Paris"))
        self.jday = utc_to_julian(self.test_date)

    def test_print_positions(self, capsys):
        """Test positions printing"""
        print_positions(self.jday)
        captured = capsys.readouterr()

        assert "Bodies Positions" in captured.out
        assert "Sun" in captured.out
        assert "Moon" in captured.out
        # Should show zodiac signs
        assert any(sign in captured.out for sign in signs)

    def test_print_aspects(self, capsys):
        """Test aspects printing"""
        print_aspects(self.jday)
        captured = capsys.readouterr()

        assert "Bodies Aspects" in captured.out
        # May or may not have aspects, but structure should be there


class TestMain:
    """Test main CLI function"""

    def test_main_invalid_input(self, monkeypatch, capsys):
        """Test main with invalid input"""
        inputs = iter(["invalid-date", ""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs, ""))

        main()
        captured = capsys.readouterr()

        assert "Error" in captured.out or "error" in captured.out


class TestPrecision:
    """Test astronomical precision against known reference values.

    Reference values sourced from JPL Horizons and validated ephemeris.
    These tests ensure Ketu returns POSITIONS (not velocities) with reasonable accuracy.
    """

    def setup_method(self):
        """Setup test data with known reference positions."""
        from datetime import timezone

        # Reference date: 21 Dec 2020 18:20 UTC (Jupiter-Saturn conjunction)
        self.ref_date = datetime(2020, 12, 21, 18, 20, 0, tzinfo=timezone.utc)
        self.ref_jday = utc_to_julian(self.ref_date)

        # Reference positions from JPL Horizons (approximate, ~1° tolerance)
        # Source: https://ssd.jpl.nasa.gov/horizons/
        self.ref_positions = {
            0: 270.0,   # Sun: ~0° Capricorn (270°)
            1: 340.0,   # Moon: ~10° Pisces (340°) - approximate, moves fast
            5: 300.0,   # Jupiter: ~0° Aquarius (300°)
            6: 300.5,   # Saturn: ~0.5° Aquarius (300.5°) - conjunction!
        }

        # Reference date 2: 23 Jan 2026 12:00 UTC
        self.ref_date_2 = datetime(2026, 1, 23, 12, 0, 0, tzinfo=timezone.utc)
        self.ref_jday_2 = utc_to_julian(self.ref_date_2)

        # Reference positions for 23 Jan 2026 (approximate)
        self.ref_positions_2 = {
            0: 303.0,   # Sun: ~3° Aquarius
            5: 108.0,   # Jupiter: ~18° Cancer
            6: 357.0,   # Saturn: ~27° Pisces
        }

    def test_long_returns_position_not_velocity(self):
        """CRITICAL: Verify long() returns position (0-360°), not velocity (~0-15°/day).

        This test catches the bug where vlong (velocity) was used instead of long (position).
        Velocities are typically 0-15°/day, positions are 0-360°.
        """
        # Jupiter and Saturn should be around 300° (Aquarius) on 21 Dec 2020
        jupiter_long = long(self.ref_jday, 5)  # Jupiter
        saturn_long = long(self.ref_jday, 6)   # Saturn

        # These MUST be large values (position), not small values (velocity)
        assert jupiter_long > 200, f"Jupiter longitude {jupiter_long}° is too small - possibly returning velocity instead of position!"
        assert saturn_long > 200, f"Saturn longitude {saturn_long}° is too small - possibly returning velocity instead of position!"

        # Check they're in the expected range (near 300° Aquarius)
        assert 290 <= jupiter_long <= 310, f"Jupiter should be near 300° (Aquarius), got {jupiter_long}°"
        assert 290 <= saturn_long <= 310, f"Saturn should be near 300° (Aquarius), got {saturn_long}°"

    def test_vlong_returns_velocity_not_position(self):
        """Verify vlong() returns velocity (°/day), not position.

        Velocities are typically:
        - Sun: ~1°/day
        - Moon: ~13°/day
        - Jupiter: ~0.08°/day
        - Saturn: ~0.03°/day
        """
        sun_vlong = vlong(self.ref_jday, 0)
        moon_vlong = vlong(self.ref_jday, 1)
        jupiter_vlong = vlong(self.ref_jday, 5)
        saturn_vlong = vlong(self.ref_jday, 6)

        # Sun velocity ~1°/day
        assert 0.9 <= abs(sun_vlong) <= 1.1, f"Sun velocity should be ~1°/day, got {sun_vlong}°/day"

        # Moon velocity ~13°/day
        assert 10 <= abs(moon_vlong) <= 16, f"Moon velocity should be ~13°/day, got {moon_vlong}°/day"

        # Outer planets are slow
        assert abs(jupiter_vlong) < 0.5, f"Jupiter velocity should be <0.5°/day, got {jupiter_vlong}°/day"
        assert abs(saturn_vlong) < 0.2, f"Saturn velocity should be <0.2°/day, got {saturn_vlong}°/day"

    def test_alias_consistency(self):
        """Test that longitude() and long() return identical values."""
        assert longitude(self.ref_jday, 0) == long(self.ref_jday, 0)
        assert longitude(self.ref_jday, 5) == long(self.ref_jday, 5)

        assert longitude_velocity(self.ref_jday, 0) == vlong(self.ref_jday, 0)
        assert longitude_velocity(self.ref_jday, 5) == vlong(self.ref_jday, 5)

    def test_jupiter_saturn_conjunction_2020(self):
        """Test positions during the famous Jupiter-Saturn conjunction of Dec 2020.

        On 21 Dec 2020, Jupiter and Saturn were in conjunction at ~0° Aquarius (300°).
        This is a well-documented astronomical event.
        """
        jupiter_long = long(self.ref_jday, 5)
        saturn_long = long(self.ref_jday, 6)

        # They should be very close (within 1°)
        separation = abs(jupiter_long - saturn_long)
        assert separation < 2.0, f"Jupiter-Saturn separation should be <2° during conjunction, got {separation}°"

    def test_sun_position_accuracy(self):
        """Test Sun position accuracy across different dates."""
        # 21 Dec 2020: Sun at ~0° Capricorn (270°)
        sun_long = long(self.ref_jday, 0)
        assert abs(sun_long - self.ref_positions[0]) < 2.0, \
            f"Sun position error too large: expected ~{self.ref_positions[0]}°, got {sun_long}°"

        # 23 Jan 2026: Sun at ~3° Aquarius (303°)
        sun_long_2 = long(self.ref_jday_2, 0)
        assert abs(sun_long_2 - self.ref_positions_2[0]) < 2.0, \
            f"Sun position error too large: expected ~{self.ref_positions_2[0]}°, got {sun_long_2}°"

    def test_outer_planets_accuracy(self):
        """Test outer planet positions (Jupiter, Saturn) with wider tolerance."""
        # Outer planets move slowly, so positions should be fairly stable
        jupiter_long = long(self.ref_jday_2, 5)
        saturn_long = long(self.ref_jday_2, 6)

        # Allow 5° tolerance for orbital element calculations
        assert abs(jupiter_long - self.ref_positions_2[5]) < 5.0, \
            f"Jupiter position error too large: expected ~{self.ref_positions_2[5]}°, got {jupiter_long}°"
        assert abs(saturn_long - self.ref_positions_2[6]) < 5.0, \
            f"Saturn position error too large: expected ~{self.ref_positions_2[6]}°, got {saturn_long}°"


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_cache_clearing(self):
        """Test LRU cache functionality"""
        # Call function to populate cache
        jday = 2459000.0
        body_properties(jday, 0)

        # Cache info should be available
        cache_info = body_properties.cache_info()
        assert cache_info.hits >= 0
        assert cache_info.misses >= 0

        # Clear cache
        body_properties.cache_clear()
        cache_info = body_properties.cache_info()
        assert cache_info.currsize == 0


# Performance tests (optional, marked slow)
@pytest.mark.slow
class TestPerformance:
    """Performance tests"""

    def test_multiple_calculations(self):
        """Test performance with multiple calculations"""
        import time

        jday = 2459000.0
        start = time.time()

        # Calculate 100 positions
        for _ in range(100):
            positions(jday)

        elapsed = time.time() - start
        assert elapsed < 1.0  # Should be under 1 second with cache

    def test_aspect_calculation_performance(self):
        """Test aspect calculation performance"""
        import time

        jday = 2459000.0
        start = time.time()

        # Calculate aspects 10 times
        for _ in range(10):
            calculate_aspects(jday)

        elapsed = time.time() - start
        assert elapsed < 0.5  # Should be fast


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
