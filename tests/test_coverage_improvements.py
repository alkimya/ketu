"""Tests to improve coverage for Ketu library.

This test file specifically targets previously uncovered code paths.
"""

import pytest
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo
from io import StringIO
import sys

from ketu import ketu


class TestVelocityFunctions:
    """Test velocity functions that weren't fully covered"""

    def setup_method(self):
        """Setup test data"""
        self.test_date = datetime(2020, 12, 21, 19, 20, tzinfo=ZoneInfo("Europe/Paris"))
        self.jday = ketu.utc_to_julian(self.test_date)

    def test_vdist_au(self):
        """Test distance velocity function"""
        # Test Sun distance velocity
        sun_vdist = ketu.vdist_au(self.jday, 0)
        assert isinstance(sun_vdist, (float, np.floating))
        # Sun's distance velocity should be relatively small
        assert abs(sun_vdist) < 0.1  # AU/day

        # Test Moon distance velocity
        moon_vdist = ketu.vdist_au(self.jday, 1)
        assert isinstance(moon_vdist, (float, np.floating))

    def test_vlat(self):
        """Test latitude velocity function"""
        # Test various bodies
        for body_id in [0, 1, 2, 3, 4]:
            vlat = ketu.vlat(self.jday, body_id)
            assert isinstance(vlat, (float, np.floating))


class TestAspectEdgeCases:
    """Test edge cases in aspect calculations"""

    def setup_method(self):
        """Setup test data"""
        self.test_date = datetime(2020, 12, 21, 19, 20, tzinfo=ZoneInfo("Europe/Paris"))
        self.jday = ketu.utc_to_julian(self.test_date)

    def test_get_aspect_reversed_bodies(self):
        """Test get_aspect with reversed body order (triggers line 274)"""
        # Call with body1 > body2 to trigger the swap
        aspect1 = ketu.get_aspect(self.jday, 1, 0)  # Moon, Sun (1 > 0)
        aspect2 = ketu.get_aspect(self.jday, 0, 1)  # Sun, Moon (normal order)

        # Both should return same result with normalized order
        if aspect1 is not None and aspect2 is not None:
            assert aspect1[0] == aspect2[0]  # Same body1
            assert aspect1[1] == aspect2[1]  # Same body2
            assert aspect1[2] == aspect2[2]  # Same aspect type

    def test_calculate_aspects_vectorized_empty(self):
        """Test vectorized aspect calculation with no matching aspects"""
        # Create a custom bodies array with just one body (no pairs possible)
        single_body = ketu.bodies[:1]

        # This should return empty array
        aspects = ketu.calculate_aspects_vectorized(self.jday, single_body)
        assert isinstance(aspects, np.ndarray)
        assert len(aspects) == 0

    def test_calculate_aspects_batch_empty(self):
        """Test batch aspect calculation with single body (no aspects)"""
        # Create date array
        jd_array = np.array([self.jday, self.jday + 1])

        # Use single body to get empty results
        single_body = ketu.bodies[:1]
        results = ketu.calculate_aspects_batch(jd_array, single_body)

        assert isinstance(results, list)
        assert len(results) == 2
        # Each result should be empty
        for result in results:
            assert len(result) == 0


class TestAspectTiming:
    """Test aspect timing functions"""

    def setup_method(self):
        """Setup test data"""
        self.test_date = datetime(2020, 12, 21, 19, 20, tzinfo=ZoneInfo("Europe/Paris"))
        self.jday = ketu.utc_to_julian(self.test_date)

    def test_find_aspect_timing(self):
        """Test finding beginning, exact, and end times for an aspect"""
        # Find a current aspect to test timing
        aspects = ketu.calculate_aspects(self.jday)

        if len(aspects) > 0:
            aspect = aspects[0]
            body1, body2 = aspect["body1"], aspect["body2"]
            asp_idx = aspect["i_asp"]
            aspect_value = ketu.aspects["angle"][asp_idx]

            # Find timing for this aspect
            begin_jd, exact_jd, end_jd = ketu.find_aspect_timing(
                self.jday, body1, body2, aspect_value
            )

            # Verify timing order
            assert begin_jd <= exact_jd <= end_jd

            # Verify times are reasonable (within ~100 days)
            assert abs(begin_jd - self.jday) < 100
            assert abs(end_jd - self.jday) < 100

    def test_find_aspect_timing_invalid_aspect(self):
        """Test find_aspect_timing with invalid aspect value"""
        with pytest.raises(ValueError):
            ketu.find_aspect_timing(self.jday, 0, 1, 999.0)

    def test_find_aspects_between_dates_both_bodies(self):
        """Test finding aspects between dates for specific body pair"""
        # Find aspects between Sun and Moon over 30 days
        sun_id = ketu.body_id("Sun")
        moon_id = ketu.body_id("Moon")

        aspects = ketu.find_aspects_between_dates(
            self.jday - 15,
            self.jday + 15,
            sun_id,
            moon_id
        )

        assert isinstance(aspects, list)
        # Should find at least one aspect in 30 days for Sun-Moon
        assert len(aspects) >= 1

        # Verify structure
        for aspect in aspects:
            exact_jd, b1, b2, asp_name, asp_val = aspect
            assert isinstance(exact_jd, (float, np.floating))
            assert b1 in [sun_id, moon_id]
            assert b2 in [sun_id, moon_id]
            assert isinstance(asp_name, str)
            assert isinstance(asp_val, (float, np.floating))

    def test_find_aspects_between_dates_one_body(self):
        """Test finding aspects with only body1 specified"""
        sun_id = ketu.body_id("Sun")

        # Find all aspects involving the Sun
        aspects = ketu.find_aspects_between_dates(
            self.jday - 5,
            self.jday + 5,
            body1=sun_id
        )

        assert isinstance(aspects, list)
        # All aspects should involve the Sun
        for aspect in aspects:
            exact_jd, b1, b2, asp_name, asp_val = aspect
            assert sun_id in [b1, b2]

    def test_find_aspects_between_dates_body2_only(self):
        """Test finding aspects with only body2 specified (covers line 536-537)"""
        moon_id = ketu.body_id("Moon")

        # Find all aspects involving the Moon as body2
        aspects = ketu.find_aspects_between_dates(
            self.jday - 5,
            self.jday + 5,
            body2=moon_id
        )

        assert isinstance(aspects, list)
        # All aspects should involve the Moon
        for aspect in aspects:
            exact_jd, b1, b2, asp_name, asp_val = aspect
            assert moon_id in [b1, b2]

    def test_find_aspects_between_dates_all_bodies(self):
        """Test finding all aspects between dates (covers line 538-539)"""
        # Find all aspects between all bodies (no body specified)
        aspects = ketu.find_aspects_between_dates(
            self.jday - 2,
            self.jday + 2
        )

        assert isinstance(aspects, list)
        # Should find many aspects with all bodies
        assert len(aspects) > 0

        # Results should be sorted by date
        dates = [asp[0] for asp in aspects]
        assert dates == sorted(dates)

    def test_find_aspects_between_dates_body_swap(self):
        """Test aspect finding with reversed body order (covers line 543-544)"""
        sun_id = ketu.body_id("Sun")
        moon_id = ketu.body_id("Moon")

        # Call with bodies in different orders
        aspects1 = ketu.find_aspects_between_dates(
            self.jday - 10,
            self.jday + 10,
            moon_id,  # body1 > body2
            sun_id
        )

        aspects2 = ketu.find_aspects_between_dates(
            self.jday - 10,
            self.jday + 10,
            sun_id,  # body1 < body2
            moon_id
        )

        # Should get same results regardless of order
        assert len(aspects1) == len(aspects2)


class TestMainCLI:
    """Test main CLI function with various inputs"""

    def test_main_valid_input(self, monkeypatch, capsys):
        """Test main with valid input"""
        inputs = iter([
            "2020-12-21",
            "19:20",
            "Europe/Paris"
        ])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        ketu.main()
        captured = capsys.readouterr()

        # Should show positions
        assert "Bodies Positions" in captured.out
        assert "Bodies Aspects" in captured.out
        assert "Aspect Timing Example" in captured.out

    def test_main_default_timezone(self, monkeypatch, capsys):
        """Test main with default timezone"""
        inputs = iter([
            "2020-12-21",
            "19:20",
            ""  # Empty string should use default
        ])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        ketu.main()
        captured = capsys.readouterr()

        # Should complete successfully with default timezone
        assert "Bodies Positions" in captured.out

    def test_main_invalid_date(self, monkeypatch, capsys):
        """Test main with invalid date format"""
        inputs = iter([
            "not-a-date",
            "invalid"
        ])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        ketu.main()
        captured = capsys.readouterr()

        assert "Error" in captured.out

    def test_main_invalid_time(self, monkeypatch, capsys):
        """Test main with invalid time format"""
        inputs = iter([
            "2020-12-21",
            "invalid-time"
        ])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        ketu.main()
        captured = capsys.readouterr()

        assert "Error" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
