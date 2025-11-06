"""Tests for Ketu library v0.1.0"""

import pytest
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo

from ketu import ketu


class TestData:
    """Test data structures"""

    def test_bodies_structure(self):
        """Test bodies array structure and content"""
        assert len(ketu.bodies) == 13
        assert ketu.bodies["id"][0] == 0  # Sun
        assert ketu.bodies["id"][1] == 1  # Moon
        assert ketu.bodies["name"][0] == b"Sun"
        assert ketu.bodies["orb"][0] == 12.0
        assert ketu.bodies["speed"][1] > 13.0  # Moon speed ~13°/day

    def test_aspects_structure(self):
        """Test aspects array structure and content"""
        assert len(ketu.aspects) == 7
        assert ketu.aspects["angle"][0] == 0  # Conjunction
        assert ketu.aspects["angle"][6] == 180  # Opposition
        assert ketu.aspects["name"][3] == b"Square"
        assert ketu.aspects["coef"][4] == 2 / 3  # Trine coefficient

    def test_signs_list(self):
        """Test zodiac signs list"""
        assert len(ketu.signs) == 12
        assert ketu.signs[0] == "Aries"
        assert ketu.signs[2] == "Gemini"
        assert ketu.signs[11] == "Pisces"


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
        utc_time = ketu.local_to_utc(self.test_date)
        assert utc_time.hour == 18  # Paris is UTC+1 in winter
        assert utc_time.minute == 20

    def test_utc_to_julian(self):
        """Test UTC to Julian Day conversion"""
        jday = ketu.utc_to_julian(self.test_date)
        assert isinstance(jday, float)
        assert jday > 2459000  # Approximate JD for 2020

        # Test epoch
        jday_epoch = ketu.utc_to_julian(self.day_one)
        assert jday_epoch == 1721425.5


class TestAngleConversions:
    """Test angle conversion functions"""

    def test_decimal_degrees_to_dms(self):
        """Test decimal degrees to DMS conversion"""
        result = ketu.decimal_degrees_to_dms(123.456)
        assert result[0] == 123  # degrees
        assert result[1] == 27  # minutes
        assert result[2] == 21  # seconds

        # Test with exact degrees
        result = ketu.decimal_degrees_to_dms(90.0)
        assert result[0] == 90
        assert result[1] == 0
        assert result[2] == 0

    def test_distance(self):
        """Test angular distance calculation"""
        # Simple cases
        assert ketu.distance(0, 90) == 90
        assert ketu.distance(0, 180) == 180
        assert ketu.distance(0, 270) == 90  # Shortest path

        # Wraparound
        assert ketu.distance(350, 10) == 20
        assert ketu.distance(10, 350) == 20

    def test_get_orb(self):
        """Test orb calculation for aspects"""
        # Sun-Moon conjunction
        orb = ketu.get_orb(0, 1, 0)  # bodies 0,1, aspect 0 (conjunction)
        assert orb == 12.0  # (12+12)/2 * 1

        # Mercury-Venus sextile
        orb = ketu.get_orb(2, 3, 2)  # bodies 2,3, aspect 2 (sextile)
        assert orb == 9.0 * (1 / 3)  # (10+8)/2 * 1/3


class TestBodyFunctions:
    """Test body-related functions"""

    def setup_method(self):
        """Setup test data"""
        self.test_date = datetime(2020, 12, 21, 19, 20, tzinfo=ZoneInfo("Europe/Paris"))
        self.jday = ketu.utc_to_julian(self.test_date)

    def test_body_name(self):
        """Test body name retrieval"""
        assert ketu.body_name(0) == "Sun"
        assert ketu.body_name(1) == "Moon"
        assert ketu.body_name(10) == "Rahu"
        assert ketu.body_name(12) == "Lilith"

    def test_body_id(self):
        """Test body ID retrieval by name"""
        assert ketu.body_id("Sun") == 0
        assert ketu.body_id("Moon") == 1
        assert ketu.body_id("Mars") == 4

    def test_body_properties(self):
        """Test body properties calculation"""
        props = ketu.body_properties(self.jday, 0)  # Sun
        assert isinstance(props, np.ndarray)
        assert len(props) == 6  # long, lat, dist, vlong, vlat, vdist
        assert 0 <= props[0] <= 360  # longitude in range

    def test_long_lat_dist(self):
        """Test individual position functions"""
        sun_long = ketu.long(self.jday, 0)
        sun_lat = ketu.lat(self.jday, 0)
        sun_dist = ketu.dist_au(self.jday, 0)

        assert 0 <= sun_long <= 360
        assert -90 <= sun_lat <= 90
        assert 0.98 <= sun_dist <= 1.02  # Sun distance ~1 AU

    def test_velocities(self):
        """Test velocity functions"""
        moon_vlong = ketu.vlong(self.jday, 1)
        assert 10 <= abs(moon_vlong) <= 16  # Moon moves 10-16°/day

        # Test retrograde detection
        mars_retro = ketu.is_retrograde(self.jday, 4)
        assert isinstance(mars_retro, bool)

    def test_is_ascending(self):
        """Test latitude ascending detection"""
        moon_ascending = ketu.is_ascending(self.jday, 1)
        assert isinstance(moon_ascending, bool)

    def test_body_sign(self):
        """Test zodiac sign calculation"""
        # Test Capricorn (270-300°)
        sign_data = ketu.body_sign(271.5)
        assert sign_data[0] == 9  # Capricorn index
        assert sign_data[1] == 1  # 1 degree
        assert sign_data[2] == 30  # 30 minutes

        # Test Aries (0-30°)
        sign_data = ketu.body_sign(15.25)
        assert sign_data[0] == 0  # Aries index
        assert sign_data[1] == 15  # 15 degrees
        assert sign_data[2] == 15  # 15 minutes

    def test_positions(self):
        """Test all positions calculation"""
        all_positions = ketu.positions(self.jday)
        assert isinstance(all_positions, np.ndarray)
        assert len(all_positions) == len(ketu.bodies)
        assert all(0 <= pos <= 360 for pos in all_positions)


class TestAspects:
    """Test aspect calculation functions"""

    def setup_method(self):
        """Setup test data"""
        self.test_date = datetime(2020, 12, 21, 19, 20, tzinfo=ZoneInfo("Europe/Paris"))
        self.jday = ketu.utc_to_julian(self.test_date)

    def test_get_aspect(self):
        """Test aspect detection between two bodies"""
        # Test Sun-Moon aspect
        aspect = ketu.get_aspect(self.jday, 0, 1)

        if aspect is not None:
            body1, body2, asp_type, orb = aspect
            assert body1 == 0  # Sun
            assert body2 == 1  # Moon
            assert 0 <= asp_type < 7  # Valid aspect type
            assert isinstance(orb, (float, np.floating))

    def test_calculate_aspects(self):
        """Test all aspects calculation"""
        aspects = ketu.calculate_aspects(self.jday)

        assert isinstance(aspects, np.ndarray)

        # Check structure if aspects exist
        if len(aspects) > 0:
            # Each aspect should have 4 fields
            assert aspects.dtype.names == ("body1", "body2", "i_asp", "orb")

            # Check first aspect
            first = aspects[0]
            assert 0 <= first["body1"] < len(ketu.bodies)
            assert 0 <= first["body2"] < len(ketu.bodies)
            assert 0 <= first["i_asp"] < len(ketu.aspects)


class TestDisplay:
    """Test display functions"""

    def setup_method(self):
        """Setup test data"""
        self.test_date = datetime(2020, 12, 21, 19, 20, tzinfo=ZoneInfo("Europe/Paris"))
        self.jday = ketu.utc_to_julian(self.test_date)

    def test_print_positions(self, capsys):
        """Test positions printing"""
        ketu.print_positions(self.jday)
        captured = capsys.readouterr()

        assert "Bodies Positions" in captured.out
        assert "Sun" in captured.out
        assert "Moon" in captured.out
        # Should show zodiac signs
        assert any(sign in captured.out for sign in ketu.signs)

    def test_print_aspects(self, capsys):
        """Test aspects printing"""
        ketu.print_aspects(self.jday)
        captured = capsys.readouterr()

        assert "Bodies Aspects" in captured.out
        # May or may not have aspects, but structure should be there


class TestMain:
    """Test main CLI function"""

    def test_main_invalid_input(self, monkeypatch, capsys):
        """Test main with invalid input"""
        inputs = iter(["invalid-date", ""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs, ""))

        ketu.main()
        captured = capsys.readouterr()

        assert "Error" in captured.out or "error" in captured.out


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_cache_clearing(self):
        """Test LRU cache functionality"""
        # Call function to populate cache
        jday = 2459000.0
        ketu.body_properties(jday, 0)

        # Cache info should be available
        cache_info = ketu.body_properties.cache_info()
        assert cache_info.hits >= 0
        assert cache_info.misses >= 0

        # Clear cache
        ketu.body_properties.cache_clear()
        cache_info = ketu.body_properties.cache_info()
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
            ketu.positions(jday)

        elapsed = time.time() - start
        assert elapsed < 1.0  # Should be under 1 second with cache

    def test_aspect_calculation_performance(self):
        """Test aspect calculation performance"""
        import time

        jday = 2459000.0
        start = time.time()

        # Calculate aspects 10 times
        for _ in range(10):
            ketu.calculate_aspects(jday)

        elapsed = time.time() - start
        assert elapsed < 0.5  # Should be fast


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
