"""Unit tests for transits module."""

import unittest
from datetime import datetime
from ketu.aspects import (
    find_transits_to_position,
    get_natal_positions,
    compare_dates_transits,
    TransitWindow,
    TransitMoment,
    NatalPosition,
    TransitAspect,
)


class TestTransitsToPosition(unittest.TestCase):
    """Test find_transits_to_position function."""

    def test_mars_transits_to_leo(self):
        """Test Mars transits to 120° (0° Leo) in 2024."""
        transits = find_transits_to_position(
            transiting_body="Mars",
            reference_longitude=120.0,
            aspects_list=["Conjunction", "Opposition"],
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        # Should find at least one transit
        self.assertGreater(len(transits), 0)

        # Check structure
        for window in transits:
            self.assertIsInstance(window, TransitWindow)
            self.assertEqual(window.transiting_body, "Mars")
            self.assertEqual(window.reference_longitude, 120.0)
            self.assertIn(window.aspect, ["Conjunction", "Opposition"])
            self.assertGreater(len(window.moments), 0)

            # Check moment structure
            moment = window.moments[0]
            self.assertIsInstance(moment, TransitMoment)
            self.assertLess(moment.begin, moment.exact)
            self.assertLess(moment.exact, moment.end)
            self.assertIn(moment.motion, ["direct", "retrograde"])

    def test_moon_quick_transits(self):
        """Test Moon transits (fast-moving body)."""
        # Moon should transit 0° Aries many times in a year
        transits = find_transits_to_position(
            transiting_body="Moon",
            reference_longitude=0.0,
            aspects_list=["Conjunction"],
            start_date="2024-01-01",
            end_date="2024-02-01",  # Just one month
        )

        # Moon completes ~13 cycles per year, so ~1 per month
        self.assertGreaterEqual(len(transits), 1)

        # Moon transits should be short (hours, not days)
        if transits:
            moment = transits[0].moments[0]
            duration_hours = (moment.end - moment.begin).total_seconds() / 3600
            self.assertLess(duration_hours, 48)  # Less than 2 days

    def test_pluto_slow_transit(self):
        """Test Pluto transit (slow-moving body)."""
        # Pluto moves very slowly, long durations
        transits = find_transits_to_position(
            transiting_body="Pluto",
            reference_longitude=270.0,  # 0° Capricorn
            aspects_list=["Conjunction"],
            start_date="2020-01-01",
            end_date="2025-12-31",  # 5 years
        )

        # May or may not find depending on Pluto's position
        # Just check it doesn't crash and returns proper structure
        for window in transits:
            self.assertIsInstance(window, TransitWindow)
            if window.moments:
                duration_days = (window.moments[0].end - window.moments[0].begin).total_seconds() / 86400
                # Pluto transits last very long
                self.assertGreater(duration_days, 30)

    def test_custom_orb(self):
        """Test custom orb parameter."""
        # Tight orb
        transits_tight = find_transits_to_position(
            transiting_body="Mars",
            reference_longitude=120.0,
            aspects_list=["Conjunction"],
            start_date="2024-10-01",
            end_date="2024-12-31",
            custom_orb=2.0,  # Very tight
        )

        # Wider orb
        transits_wide = find_transits_to_position(
            transiting_body="Mars",
            reference_longitude=120.0,
            aspects_list=["Conjunction"],
            start_date="2024-10-01",
            end_date="2024-12-31",
            custom_orb=10.0,  # Wide
        )

        # Wide orb should have longer duration
        if transits_tight and transits_wide:
            duration_tight = (transits_tight[0].moments[0].end - transits_tight[0].moments[0].begin).total_seconds()
            duration_wide = (transits_wide[0].moments[0].end - transits_wide[0].moments[0].begin).total_seconds()
            self.assertLess(duration_tight, duration_wide)

    def test_no_transits_in_range(self):
        """Test when no transits are found."""
        # Very narrow time range, unlikely to find anything
        transits = find_transits_to_position(
            transiting_body="Pluto",
            reference_longitude=0.0,
            aspects_list=["Conjunction"],
            start_date="2024-01-01",
            end_date="2024-01-02",  # Just 1 day
        )

        # Should return empty list (not crash)
        self.assertIsInstance(transits, list)

    def test_multiple_aspects(self):
        """Test finding multiple aspect types."""
        transits = find_transits_to_position(
            transiting_body="Mars",
            reference_longitude=120.0,
            aspects_list=["Conjunction", "Square", "Trine", "Opposition"],
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        # Should find multiple different aspects
        aspects_found = set(w.aspect for w in transits)
        self.assertGreater(len(aspects_found), 1)


class TestNatalPositions(unittest.TestCase):
    """Test get_natal_positions function."""

    def test_get_all_positions(self):
        """Test getting all natal positions."""
        natal = get_natal_positions("1990-05-15 14:30")

        # Should have 13 bodies (Sun through Lilith)
        self.assertEqual(len(natal), 13)

        # Check structure
        for body_name, pos in natal.items():
            self.assertIsInstance(pos, NatalPosition)
            self.assertEqual(pos.body, body_name)
            self.assertGreaterEqual(pos.longitude, 0)
            self.assertLess(pos.longitude, 360)

    def test_specific_bodies(self):
        """Test getting specific bodies only."""
        natal = get_natal_positions(
            "1990-05-15 14:30",
            bodies_list=["Sun", "Moon", "Mercury"]
        )

        self.assertEqual(len(natal), 3)
        self.assertIn("Sun", natal)
        self.assertIn("Moon", natal)
        self.assertIn("Mercury", natal)

    def test_datetime_input(self):
        """Test with datetime object input."""
        dt = datetime(1990, 5, 15, 14, 30)
        natal = get_natal_positions(dt)

        self.assertEqual(len(natal), 13)

    def test_sun_position(self):
        """Test Sun position on known date."""
        # May 15 → Sun should be in Taurus (30-60°)
        natal = get_natal_positions("1990-05-15 12:00")

        sun_lon = natal["Sun"].longitude
        self.assertGreater(sun_lon, 30)  # After Aries
        self.assertLess(sun_lon, 90)     # Before Gemini


class TestCompareDatesTransits(unittest.TestCase):
    """Test compare_dates_transits function."""

    def test_basic_comparison(self):
        """Test basic transit comparison."""
        transits = compare_dates_transits(
            natal_date="1990-05-15 14:30",
            transit_date="2024-11-21 12:00",
            aspects_list=["Conjunction", "Square", "Opposition"]
        )

        # Should find some transiting aspects
        self.assertIsInstance(transits, list)

        # Check structure
        for t in transits:
            self.assertIsInstance(t, TransitAspect)
            self.assertIsInstance(t.transiting_body, str)
            self.assertIsInstance(t.natal_body, str)
            self.assertIn(t.aspect, ["Conjunction", "Square", "Opposition"])
            self.assertIsInstance(t.exact_time, datetime)

    def test_same_date_comparison(self):
        """Test comparing a date with itself."""
        transits = compare_dates_transits(
            natal_date="2024-01-01 12:00",
            transit_date="2024-01-01 12:00",
            aspects_list=["Conjunction"]
        )

        # Should find exact conjunctions of all planets with themselves
        # But we skip same body, so should find no transits
        conjunction_count = sum(1 for t in transits if t.aspect == "Conjunction")
        # Each planet should NOT form conjunction with itself (filtered out)
        # But might form with other planets
        self.assertIsInstance(transits, list)

    def test_custom_orb(self):
        """Test custom orb in comparison."""
        # Tight orb
        transits_tight = compare_dates_transits(
            natal_date="1990-05-15 14:30",
            transit_date="2024-11-21 12:00",
            aspects_list=["Conjunction", "Square", "Opposition"],
            custom_orb=2.0
        )

        # Wide orb
        transits_wide = compare_dates_transits(
            natal_date="1990-05-15 14:30",
            transit_date="2024-11-21 12:00",
            aspects_list=["Conjunction", "Square", "Opposition"],
            custom_orb=10.0
        )

        # Wide orb should find more aspects
        self.assertGreaterEqual(len(transits_wide), len(transits_tight))

    def test_different_aspect_lists(self):
        """Test with different aspect lists."""
        # Only major aspects
        transits_major = compare_dates_transits(
            natal_date="1990-05-15 14:30",
            transit_date="2024-11-21 12:00",
            aspects_list=["Conjunction", "Square", "Trine", "Opposition"]
        )

        # Only conjunction
        transits_conj = compare_dates_transits(
            natal_date="1990-05-15 14:30",
            transit_date="2024-11-21 12:00",
            aspects_list=["Conjunction"]
        )

        # Major should find more
        self.assertGreaterEqual(len(transits_major), len(transits_conj))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_longitude_normalization(self):
        """Test that longitudes are properly normalized."""
        # Test with longitude > 360
        transits = find_transits_to_position(
            transiting_body="Mars",
            reference_longitude=480.0,  # Should normalize to 120.0
            aspects_list=["Conjunction"],
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        # Should work (normalized to 120°)
        for window in transits:
            self.assertEqual(window.reference_longitude, 120.0)

    def test_body_by_id(self):
        """Test specifying body by ID instead of name."""
        transits = find_transits_to_position(
            transiting_body=4,  # Mars
            reference_longitude=120.0,
            aspects_list=["Conjunction"],
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        for window in transits:
            self.assertEqual(window.transiting_body, "Mars")

    def test_aspect_by_angle(self):
        """Test specifying aspect by angle."""
        transits = find_transits_to_position(
            transiting_body="Mars",
            reference_longitude=120.0,
            aspects_list=[0, 180.0],  # Conjunction and Opposition
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        aspects_found = set(w.aspect for w in transits)
        if transits:
            self.assertTrue(
                "Conjunction" in aspects_found or "Opposition" in aspects_found
            )


if __name__ == "__main__":
    unittest.main()
