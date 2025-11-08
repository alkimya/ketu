"""Unit tests for aspect_windows module."""

import unittest
from datetime import datetime, timedelta
from ketu.aspect_windows import (
    find_aspect_window,
    find_aspects_timeline,
    AspectMoment,
    AspectWindow,
)
from ketu.calculations import utc_to_julian, long, distance


class TestAspectWindow(unittest.TestCase):
    """Test aspect window calculations."""

    def test_full_moon_march_2024(self):
        """Test Full Moon (Opposition) detection on March 25, 2024."""
        result = find_aspect_window(
            body1="Sun",
            body2="Moon",
            aspect="Opposition",
            around_date="2024-03-25",
            search_days=3,
        )

        self.assertEqual(result.body1, "Sun")
        self.assertEqual(result.body2, "Moon")
        self.assertEqual(result.aspect, "Opposition")
        self.assertEqual(len(result.moments), 1)
        self.assertEqual(result.retrograde_count, 0)

        moment = result.moments[0]
        self.assertIsInstance(moment, AspectMoment)
        self.assertEqual(moment.orb_used, 12.0)
        self.assertEqual(moment.motion, "direct")

        # Check timing is reasonable (exact should be around March 25, 2024)
        exact_date = moment.exact
        self.assertEqual(exact_date.year, 2024)
        self.assertEqual(exact_date.month, 3)
        self.assertEqual(exact_date.day, 25)

        # Check begin < exact < end
        self.assertLess(moment.begin, moment.exact)
        self.assertLess(moment.exact, moment.end)

        # Verify accuracy: at exact moment, distance should be very close to 180°
        jd_exact = utc_to_julian(moment.exact)
        sun_lon = long(jd_exact, 0)
        moon_lon = long(jd_exact, 1)
        dist = distance(sun_lon, moon_lon)
        self.assertAlmostEqual(dist, 180.0, delta=0.1)  # Within 0.1 degrees

    def test_new_moon_april_2024(self):
        """Test New Moon (Conjunction) detection on April 8, 2024."""
        result = find_aspect_window(
            body1="Sun",
            body2="Moon",
            aspect="Conjunction",
            around_date="2024-04-08",
            search_days=3,
        )

        self.assertEqual(len(result.moments), 1)
        moment = result.moments[0]

        # Check timing
        self.assertEqual(moment.exact.year, 2024)
        self.assertEqual(moment.exact.month, 4)
        self.assertEqual(moment.exact.day, 8)

        # Verify accuracy: at exact moment, distance should be close to 0°
        jd_exact = utc_to_julian(moment.exact)
        sun_lon = long(jd_exact, 0)
        moon_lon = long(jd_exact, 1)
        dist = distance(sun_lon, moon_lon)
        self.assertLess(dist, 0.5)  # Within 0.5 degrees of conjunction

    def test_custom_orb(self):
        """Test custom orb parameter."""
        # Default orb
        result_default = find_aspect_window(
            body1="Sun",
            body2="Moon",
            aspect="Opposition",
            around_date="2024-03-25",
            search_days=3,
        )

        # Tight orb
        result_tight = find_aspect_window(
            body1="Sun",
            body2="Moon",
            aspect="Opposition",
            around_date="2024-03-25",
            search_days=3,
            custom_orb=5.0,
        )

        self.assertEqual(result_default.moments[0].orb_used, 12.0)
        self.assertEqual(result_tight.moments[0].orb_used, 5.0)

        # Tight orb should have shorter duration
        duration_default = (
            result_default.moments[0].end - result_default.moments[0].begin
        ).total_seconds()
        duration_tight = (
            result_tight.moments[0].end - result_tight.moments[0].begin
        ).total_seconds()
        self.assertLess(duration_tight, duration_default)

    def test_no_aspect_found(self):
        """Test when no aspect is in range."""
        result = find_aspect_window(
            body1="Sun",
            body2="Moon",
            aspect="Opposition",
            around_date="2024-03-01",  # Far from full moon
            search_days=1,  # Very narrow search
        )

        self.assertEqual(len(result.moments), 0)
        self.assertEqual(result.retrograde_count, 0)

    def test_square_aspect(self):
        """Test square aspect detection."""
        result = find_aspect_window(
            body1="Sun",
            body2="Moon",
            aspect="Square",
            around_date="2024-03-17",
            search_days=2,
        )

        if result.moments:  # Square may exist
            moment = result.moments[0]

            # Verify it's actually a square
            jd_exact = utc_to_julian(moment.exact)
            sun_lon = long(jd_exact, 0)
            moon_lon = long(jd_exact, 1)
            dist = distance(sun_lon, moon_lon)
            self.assertAlmostEqual(dist, 90.0, delta=1.0)

    def test_trine_aspect(self):
        """Test trine aspect detection."""
        result = find_aspect_window(
            body1="Sun",
            body2="Moon",
            aspect="Trine",
            around_date="2024-03-01",
            search_days=2,
        )

        if result.moments:  # Trine may exist
            moment = result.moments[0]

            # Verify it's actually a trine
            jd_exact = utc_to_julian(moment.exact)
            sun_lon = long(jd_exact, 0)
            moon_lon = long(jd_exact, 1)
            dist = distance(sun_lon, moon_lon)
            self.assertAlmostEqual(dist, 120.0, delta=1.0)

    def test_aspects_timeline(self):
        """Test timeline of multiple aspects."""
        timeline = find_aspects_timeline(
            body1="Sun",
            body2="Moon",
            aspects_list=["Conjunction", "Opposition"],
            start_date="2024-03-01",
            end_date="2024-04-30",
        )

        # Should find at least one conjunction and one opposition
        self.assertGreater(len(timeline), 0)

        # Check chronological order
        for i in range(len(timeline) - 1):
            if timeline[i].moments and timeline[i + 1].moments:
                self.assertLessEqual(
                    timeline[i].moments[0].exact, timeline[i + 1].moments[0].exact
                )

    def test_jupiter_saturn_conjunction_2020(self):
        """Test Great Conjunction of Jupiter-Saturn (slow planets)."""
        result = find_aspect_window(
            body1="Jupiter",
            body2="Saturn",
            aspect="Conjunction",
            around_date="2020-12-21",
            search_days=60,
        )

        self.assertEqual(len(result.moments), 1)
        moment = result.moments[0]

        # Should be in December 2020
        self.assertEqual(moment.exact.year, 2020)
        self.assertEqual(moment.exact.month, 12)

        # Duration should be very long (months, not hours)
        duration_days = (moment.end - moment.begin).total_seconds() / 86400
        self.assertGreater(duration_days, 30)  # At least a month

    def test_namedtuple_structure(self):
        """Test that result structures are proper namedtuples."""
        result = find_aspect_window(
            body1="Sun",
            body2="Moon",
            aspect="Opposition",
            around_date="2024-03-25",
            search_days=3,
        )

        # Check AspectWindow fields
        self.assertTrue(hasattr(result, "body1"))
        self.assertTrue(hasattr(result, "body2"))
        self.assertTrue(hasattr(result, "aspect"))
        self.assertTrue(hasattr(result, "moments"))
        self.assertTrue(hasattr(result, "retrograde_count"))

        # Check AspectMoment fields
        moment = result.moments[0]
        self.assertTrue(hasattr(moment, "begin"))
        self.assertTrue(hasattr(moment, "exact"))
        self.assertTrue(hasattr(moment, "end"))
        self.assertTrue(hasattr(moment, "orb_used"))
        self.assertTrue(hasattr(moment, "motion"))

        # Check tuple indexing works
        self.assertEqual(result[0], "Sun")
        self.assertEqual(moment[0], moment.begin)

    def test_duration_varies_by_orb(self):
        """Test that duration varies correctly with orb size."""
        # Test with different orbs
        orbs = [3.0, 6.0, 12.0]
        durations = []

        for orb in orbs:
            result = find_aspect_window(
                body1="Sun",
                body2="Moon",
                aspect="Opposition",
                around_date="2024-03-25",
                search_days=3,
                custom_orb=orb,
            )
            if result.moments:
                duration = (
                    result.moments[0].end - result.moments[0].begin
                ).total_seconds()
                durations.append(duration)

        # Durations should increase with orb size
        self.assertEqual(len(durations), 3)
        self.assertLess(durations[0], durations[1])
        self.assertLess(durations[1], durations[2])

    def test_aspect_by_name_index_and_angle(self):
        """Test that aspects can be specified by name, index, or angle."""
        # By name
        result1 = find_aspect_window(
            body1="Sun",
            body2="Moon",
            aspect="Opposition",
            around_date="2024-03-25",
            search_days=3,
        )

        # By index (6 = Opposition)
        result2 = find_aspect_window(
            body1="Sun",
            body2="Moon",
            aspect=6,
            around_date="2024-03-25",
            search_days=3,
        )

        # By angle
        result3 = find_aspect_window(
            body1="Sun",
            body2="Moon",
            aspect=180.0,
            around_date="2024-03-25",
            search_days=3,
        )

        # All should find the same aspect
        if result1.moments and result2.moments and result3.moments:
            self.assertEqual(result1.moments[0].exact, result2.moments[0].exact)
            self.assertEqual(result2.moments[0].exact, result3.moments[0].exact)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_very_narrow_search(self):
        """Test with very narrow search range."""
        result = find_aspect_window(
            body1="Sun",
            body2="Moon",
            aspect="Opposition",
            around_date="2024-03-25",
            search_days=0.01,  # Very narrow: ~15 minutes
        )

        # May or may not find aspect depending on exact timing
        # Just check it doesn't crash
        self.assertIsInstance(result, AspectWindow)

    def test_very_wide_search(self):
        """Test with very wide search range."""
        result = find_aspect_window(
            body1="Jupiter",
            body2="Saturn",
            aspect="Conjunction",
            around_date="2020-12-21",
            search_days=180,  # Half a year
        )

        # Should find the conjunction
        self.assertGreater(len(result.moments), 0)

    def test_date_string_formats(self):
        """Test different date string formats."""
        # ISO format with time
        result1 = find_aspect_window(
            body1="Sun",
            body2="Moon",
            aspect="Opposition",
            around_date="2024-03-25 12:00:00",
            search_days=3,
        )

        # ISO format without time
        result2 = find_aspect_window(
            body1="Sun",
            body2="Moon",
            aspect="Opposition",
            around_date="2024-03-25",
            search_days=3,
        )

        # Both should find the same opposition
        if result1.moments and result2.moments:
            # Should be within a day of each other
            diff = abs((result1.moments[0].exact - result2.moments[0].exact).total_seconds())
            self.assertLess(diff, 86400)  # Less than 24 hours difference


if __name__ == "__main__":
    unittest.main()
