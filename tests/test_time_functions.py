"""Tests for ephemeris time conversion functions.

Tests focus on improving coverage of ephemeris/time.py module.
"""

import pytest
import numpy as np
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from ketu.ephemeris.time import (
    utc_to_julian,
    coerce_to_jd,
    julian_to_utc,
    local_to_utc,
    delta_t,
    terrestrial_to_universal,
    universal_to_terrestrial,
    equation_of_time,
    sidereal_time,
)


class TestBasicTimeConversions:
    """Test basic UTC <-> Julian conversions."""

    def test_utc_to_julian_j2000(self):
        """Test J2000.0 epoch (2000-01-01 12:00 UTC = JD 2451545.0)."""
        dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        jd = utc_to_julian(dt)
        assert abs(jd - 2451545.0) < 0.01

    def test_julian_to_utc_j2000(self):
        """Test reverse conversion for J2000.0."""
        dt = julian_to_utc(2451545.0)
        assert dt.year == 2000
        assert dt.month == 1
        assert dt.day == 1
        assert dt.hour == 12

    def test_roundtrip_conversion(self):
        """Test UTC -> Julian -> UTC roundtrip."""
        dt_original = datetime(2024, 6, 15, 14, 30, 45, tzinfo=timezone.utc)
        jd = utc_to_julian(dt_original)
        dt_recovered = julian_to_utc(jd)

        # Allow 1 second tolerance
        delta = abs((dt_recovered - dt_original).total_seconds())
        assert delta < 2.0

    def test_utc_to_julian_with_timezone(self):
        """Test conversion with timezone-aware datetime."""
        # Paris time (UTC+2 in summer)
        dt_paris = datetime(2024, 6, 15, 14, 0, 0, tzinfo=ZoneInfo("Europe/Paris"))
        jd = utc_to_julian(dt_paris)

        # Should convert to UTC (12:00) before computing JD
        dt_utc = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        jd_utc = utc_to_julian(dt_utc)

        assert abs(jd - jd_utc) < 0.001

    def test_utc_to_julian_naive_datetime(self):
        """Test naive datetime (assumed UTC)."""
        dt_naive = datetime(2024, 1, 1, 0, 0, 0)
        jd = utc_to_julian(dt_naive)
        assert jd > 2451545.0  # After J2000

    def test_julian_calendar_dates(self):
        """Test dates before Gregorian calendar reform (1582-10-15)."""
        # Test a date in Julian calendar era
        dt = datetime(1500, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        jd = utc_to_julian(dt)
        assert 2269000 < jd < 2270000  # Approximate expected value

    def test_year_boundaries(self):
        """Test conversions at year boundaries."""
        # End of 1999
        dt = datetime(1999, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        jd = utc_to_julian(dt)
        dt_back = julian_to_utc(jd)
        assert dt_back.year == 1999

        # Start of 2000
        dt = datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        jd = utc_to_julian(dt)
        dt_back = julian_to_utc(jd)
        assert dt_back.year == 2000

    def test_february_dates(self):
        """Test February dates including leap years."""
        # Leap year
        dt = datetime(2020, 2, 29, 12, 0, 0, tzinfo=timezone.utc)
        jd = utc_to_julian(dt)
        dt_back = julian_to_utc(jd)
        assert dt_back.month == 2
        assert dt_back.day == 29

        # Non-leap year
        dt = datetime(2021, 2, 28, 12, 0, 0, tzinfo=timezone.utc)
        jd = utc_to_julian(dt)
        dt_back = julian_to_utc(jd)
        assert dt_back.month == 2
        assert dt_back.day == 28


class TestCoerceToJD:
    """Test coerce_to_jd accepts datetime, ISO string, and float identically."""

    def test_all_three_inputs_agree(self):
        dt = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        jd_from_dt = coerce_to_jd(dt)
        jd_from_str = coerce_to_jd("2025-01-01T12:00:00+00:00")
        jd_from_float = coerce_to_jd(jd_from_dt)
        assert jd_from_dt == jd_from_str == jd_from_float

    def test_datetime_matches_utc_to_julian(self):
        dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert coerce_to_jd(dt) == utc_to_julian(dt)

    def test_naive_string_assumed_utc(self):
        assert coerce_to_jd("2025-06-21T00:00:00") == utc_to_julian(
            datetime(2025, 6, 21, 0, 0, 0)
        )

    def test_float_passthrough(self):
        assert coerce_to_jd(2451545.0) == 2451545.0


class TestLocalToUTC:
    """Test local_to_utc function."""

    def test_timezone_aware_conversion(self):
        """Test conversion with timezone-aware datetime."""
        dt_paris = datetime(2024, 6, 21, 12, 0, 0, tzinfo=ZoneInfo("Europe/Paris"))
        dt_utc = local_to_utc(dt_paris)

        assert dt_utc.hour == 10  # Paris is UTC+2 in summer
        assert dt_utc.tzinfo == timezone.utc

    def test_naive_datetime(self):
        """Test naive datetime (assumed UTC)."""
        dt_naive = datetime(2024, 6, 21, 12, 0, 0)
        dt_utc = local_to_utc(dt_naive)

        assert dt_utc.hour == 12
        assert dt_utc.tzinfo == timezone.utc

    def test_various_timezones(self):
        """Test various timezone conversions."""
        timezones = [
            ("America/New_York", -5),  # Winter offset
            ("Asia/Tokyo", 9),
            ("Australia/Sydney", 11),  # Winter offset
        ]

        for tz_name, offset in timezones:
            dt_local = datetime(2024, 1, 15, 12, 0, 0, tzinfo=ZoneInfo(tz_name))
            dt_utc = local_to_utc(dt_local)
            assert dt_utc.tzinfo == timezone.utc


class TestDeltaT:
    """Test Delta T calculation."""

    def test_delta_t_year_2000(self):
        """Test Delta T for year 2000."""
        dt = delta_t(2000.0)
        # Expected value around 63.8 seconds
        assert 60 < dt < 70

    def test_delta_t_year_2024(self):
        """Test Delta T for year 2024."""
        dt = delta_t(2024.0)
        # Expected value around 69 seconds
        assert 65 < dt < 75

    def test_delta_t_historical(self):
        """Test Delta T for historical years."""
        # Year 1900
        dt = delta_t(1900.0)
        assert -5 < dt < 0

        # Year 1800
        dt = delta_t(1800.0)
        assert 10 < dt < 20

    def test_delta_t_ancient(self):
        """Test Delta T for ancient years."""
        # Year 0
        dt = delta_t(0.0)
        assert dt > 10000  # Large value for ancient times

        # Year -500
        dt = delta_t(-500.0)
        assert dt > 15000

    def test_delta_t_future(self):
        """Test Delta T for future years."""
        # Year 2100
        dt = delta_t(2100.0)
        assert dt > 80  # Extrapolated value

        # Year 2200
        dt = delta_t(2200.0)
        assert dt > 100


class TestTimeSystemConversions:
    """Test TT <-> UT conversions."""

    def test_universal_to_terrestrial(self):
        """Test UT to TT conversion."""
        jd_ut = 2451545.0  # J2000.0 in UT
        jd_tt = universal_to_terrestrial(jd_ut)

        # TT should be ahead of UT by Delta T
        assert jd_tt > jd_ut
        assert 0 < (jd_tt - jd_ut) * 86400 < 100  # Delta T in seconds

    def test_terrestrial_to_universal(self):
        """Test TT to UT conversion."""
        jd_tt = 2451545.0  # J2000.0 in TT
        jd_ut = terrestrial_to_universal(jd_tt)

        # UT should be behind TT
        assert jd_ut < jd_tt
        assert 0 < (jd_tt - jd_ut) * 86400 < 100

    def test_time_system_roundtrip(self):
        """Test UT -> TT -> UT roundtrip."""
        jd_ut_original = 2451545.0
        jd_tt = universal_to_terrestrial(jd_ut_original)
        jd_ut_recovered = terrestrial_to_universal(jd_tt)

        # Should recover original value within tolerance
        assert abs(jd_ut_recovered - jd_ut_original) < 0.0001




class TestSiderealTime:
    """Test sidereal time calculation."""

    def test_gmst_j2000(self):
        """Test Greenwich Mean Sidereal Time at J2000.0."""
        gmst = sidereal_time(2451545.0)

        # GMST at J2000.0 epoch should be near 280.46 degrees
        assert 280 < gmst < 281

    def test_gmst_range(self):
        """Test GMST is always in valid range."""
        jd_start = 2451545.0

        for day in range(0, 365, 10):
            jd = jd_start + day
            gmst = sidereal_time(jd)
            assert 0 <= gmst < 360

    def test_gmst_advances(self):
        """Test GMST advances correctly."""
        jd = 2451545.0
        gmst1 = sidereal_time(jd)
        gmst2 = sidereal_time(jd + 1.0)  # One day later

        # GMST advances by ~361 degrees per day (360 + ~1)
        # So after one day, it should be ~1 degree ahead
        advance = (gmst2 - gmst1) % 360
        assert 0.5 < advance < 1.5

    def test_local_sidereal_time(self):
        """Test Local Sidereal Time calculation."""
        jd = 2451545.0
        longitude = 45.0  # 45 degrees east

        gmst = sidereal_time(jd, longitude=0.0)
        lst = sidereal_time(jd, longitude=longitude)

        # LST should be GMST + longitude
        expected_lst = (gmst + longitude) % 360
        assert abs(lst - expected_lst) < 0.01

    def test_lst_west_longitude(self):
        """Test LST with west longitude (negative)."""
        jd = 2451545.0
        longitude = -75.0  # 75 degrees west

        gmst = sidereal_time(jd, longitude=0.0)
        lst = sidereal_time(jd, longitude=longitude)

        # LST should be GMST + longitude (longitude is negative)
        expected_lst = (gmst + longitude) % 360
        assert abs(lst - expected_lst) < 0.01


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_microseconds_in_conversion(self):
        """Test that microseconds are handled."""
        dt = datetime(2024, 1, 1, 12, 0, 0, 123456, tzinfo=timezone.utc)
        jd = utc_to_julian(dt)
        # Should complete without error
        assert jd > 2451545.0

    def test_very_old_dates(self):
        """Test very old dates."""
        dt = datetime(1000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        jd = utc_to_julian(dt)
        assert jd > 0  # Should be positive
        assert jd < 2451545.0  # Should be before J2000

    def test_future_dates(self):
        """Test future dates."""
        dt = datetime(2100, 12, 31, 12, 0, 0, tzinfo=timezone.utc)
        jd = utc_to_julian(dt)
        dt_back = julian_to_utc(jd)
        assert dt_back.year == 2100
        assert dt_back.month == 12

    def test_delta_t_all_ranges(self):
        """Test Delta T across all polynomial ranges."""
        test_years = [
            -1000, -500, -100, 0, 100, 500, 1000, 1500, 1600, 1650, 1700,
            1750, 1800, 1850, 1860, 1880, 1900, 1910, 1920, 1930, 1941,
            1950, 1961, 1970, 1986, 1990, 2005, 2010, 2024, 2050, 2100,
            2150, 2200, 3000
        ]

        for year in test_years:
            dt = delta_t(year)
            assert isinstance(dt, (int, float))
            # Delta T should be finite
            assert np.isfinite(dt)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
class TestEquationOfTime:
    """Test equation of time calculation."""

    def test_equation_of_time_returns_numeric(self):
        """Test equation of time returns a numeric value."""
        eot = equation_of_time(2451545.0)
        # Just verify it returns a number
        assert isinstance(eot, (int, float))
        assert np.isfinite(eot)

