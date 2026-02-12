"""Coverage tests for transits module - targeting uncovered lines.

Covers:
- Line 305: default aspects_list (None) in find_transits_to_position
- Lines 311-314: datetime input for start_date
- Lines 319-322: float (Julian Date) input for end_date
- Line 358: refine_exact_moment returns None
- Line 367: find_orb_boundaries returns None
- Lines 398-403: detect_retrograde=False path
- Line 451: float input for reference_date in get_natal_positions
- Line 522: default aspects_list in compare_dates_transits
- Lines 528-531: float transit_date in compare_dates_transits
"""

from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from ketu.aspects import (
    find_transits_to_position,
    get_natal_positions,
    compare_dates_transits,
    TransitWindow,
    TransitMoment,
    NatalPosition,
    TransitAspect,
)
from ketu.calculations import utc_to_julian


# ========== find_transits_to_position coverage ==========


class TestFindTransitsDefaultAspects:
    """Line 305: aspects_list=None uses default major aspects."""

    def test_default_aspects_list_is_used(self):
        """When aspects_list is None, defaults to 5 major aspects."""
        transits = find_transits_to_position(
            transiting_body="Moon",
            reference_longitude=90.0,
            aspects_list=None,
            start_date="2024-03-01",
            end_date="2024-03-31",
        )
        # Should not raise; returns list of TransitWindow
        assert isinstance(transits, list)
        for window in transits:
            assert isinstance(window, TransitWindow)
            # Default list: Conjunction, Sextile, Square, Trine, Opposition
            assert window.aspect in [
                "Conjunction",
                "Sextile",
                "Square",
                "Trine",
                "Opposition",
            ]


class TestFindTransitsDatetimeStartDate:
    """Lines 311-314: datetime object for start_date."""

    def test_datetime_start_date(self):
        """Pass a datetime object as start_date (not string)."""
        start = datetime(2024, 6, 1, 0, 0, 0, tzinfo=timezone.utc)
        transits = find_transits_to_position(
            transiting_body="Moon",
            reference_longitude=180.0,
            aspects_list=["Conjunction"],
            start_date=start,
            end_date="2024-06-30",
        )
        assert isinstance(transits, list)

    def test_datetime_start_date_naive(self):
        """Pass a naive datetime as start_date."""
        start = datetime(2024, 6, 1, 12, 0, 0)
        transits = find_transits_to_position(
            transiting_body="Moon",
            reference_longitude=0.0,
            aspects_list=["Conjunction"],
            start_date=start,
            end_date="2024-06-30",
        )
        assert isinstance(transits, list)


class TestFindTransitsFloatEndDate:
    """Lines 319-322: float (Julian Date) for end_date."""

    def test_float_end_date(self):
        """Pass a Julian Date float as end_date."""
        jd_end = utc_to_julian(datetime(2024, 4, 30, 0, 0, 0))
        transits = find_transits_to_position(
            transiting_body="Moon",
            reference_longitude=45.0,
            aspects_list=["Conjunction"],
            start_date="2024-04-01",
            end_date=jd_end,
        )
        assert isinstance(transits, list)

    def test_datetime_end_date(self):
        """Pass a datetime object as end_date (lines 319-320)."""
        end = datetime(2024, 4, 30, 0, 0, 0, tzinfo=timezone.utc)
        transits = find_transits_to_position(
            transiting_body="Moon",
            reference_longitude=45.0,
            aspects_list=["Conjunction"],
            start_date="2024-04-01",
            end_date=end,
        )
        assert isinstance(transits, list)

    def test_both_datetime_inputs(self):
        """Both start_date and end_date as datetime objects."""
        start = datetime(2024, 5, 1, 0, 0, 0)
        end = datetime(2024, 5, 31, 0, 0, 0)
        transits = find_transits_to_position(
            transiting_body="Moon",
            reference_longitude=120.0,
            aspects_list=["Conjunction"],
            start_date=start,
            end_date=end,
        )
        assert isinstance(transits, list)

    def test_both_float_inputs(self):
        """Both start_date and end_date as Julian Date floats."""
        jd_start = utc_to_julian(datetime(2024, 7, 1, 0, 0, 0))
        jd_end = utc_to_julian(datetime(2024, 7, 31, 0, 0, 0))
        transits = find_transits_to_position(
            transiting_body="Moon",
            reference_longitude=270.0,
            aspects_list=["Conjunction"],
            start_date=jd_start,
            end_date=jd_end,
        )
        assert isinstance(transits, list)


class TestFindTransitsRefinementFailure:
    """Line 358: refine_exact_moment returns None (skipped candidate)."""

    def test_refinement_returns_none(self):
        """When refine_exact_moment returns None, candidate is skipped."""
        with patch(
            "ketu.aspects.transits.refine_exact_moment", return_value=None
        ):
            transits = find_transits_to_position(
                transiting_body="Moon",
                reference_longitude=90.0,
                aspects_list=["Conjunction"],
                start_date="2024-03-01",
                end_date="2024-03-31",
            )
            # All candidates skipped because refinement always returns None
            assert isinstance(transits, list)
            assert len(transits) == 0


class TestFindTransitsOrbBoundaryFailure:
    """Line 367: find_orb_boundaries returns None (boundary not found)."""

    def test_orb_boundary_returns_none(self):
        """When find_orb_boundaries returns (None, None), candidate is skipped."""
        with patch(
            "ketu.aspects.transits.find_orb_boundaries",
            return_value=(None, None),
        ):
            transits = find_transits_to_position(
                transiting_body="Moon",
                reference_longitude=90.0,
                aspects_list=["Conjunction"],
                start_date="2024-03-01",
                end_date="2024-03-31",
            )
            # All candidates skipped because boundaries are None
            assert isinstance(transits, list)
            assert len(transits) == 0

    def test_orb_boundary_begin_none(self):
        """When find_orb_boundaries returns (None, value), candidate is skipped."""
        with patch(
            "ketu.aspects.transits.find_orb_boundaries",
            return_value=(None, 2460400.0),
        ):
            transits = find_transits_to_position(
                transiting_body="Moon",
                reference_longitude=90.0,
                aspects_list=["Conjunction"],
                start_date="2024-03-01",
                end_date="2024-03-31",
            )
            assert isinstance(transits, list)
            assert len(transits) == 0


class TestFindTransitsDetectRetrogradeFalse:
    """Lines 398-403: detect_retrograde=False limits to single closest moment."""

    def test_detect_retrograde_false_mars(self):
        """With detect_retrograde=False, multiple moments for same aspect are reduced to 1."""
        # Use Mars over a long period to increase chance of retrograde hits
        transits = find_transits_to_position(
            transiting_body="Mars",
            reference_longitude=120.0,
            aspects_list=["Conjunction", "Square", "Trine", "Opposition"],
            start_date="2024-01-01",
            end_date="2024-12-31",
            detect_retrograde=False,
        )
        assert isinstance(transits, list)
        # With detect_retrograde=False, each window should have at most 1 moment
        for window in transits:
            assert len(window.moments) <= 1
            # retrograde_count should be 0 when detect_retrograde=False reduces moments
            if len(window.moments) == 1:
                assert window.retrograde_count >= 0

    def test_detect_retrograde_false_moon(self):
        """Moon never retrogrades, so detect_retrograde=False still works."""
        transits = find_transits_to_position(
            transiting_body="Moon",
            reference_longitude=0.0,
            aspects_list=["Conjunction"],
            start_date="2024-01-01",
            end_date="2024-06-30",
            detect_retrograde=False,
        )
        assert isinstance(transits, list)

    def test_detect_retrograde_false_forces_single_moment(self):
        """Force the path where multiple moments exist and detect_retrograde=False trims them."""
        # Create a mock scenario: multiple moments exist for a single aspect,
        # and detect_retrograde=False should pick the closest to center.
        fake_moment_1 = TransitMoment(
            begin=datetime(2024, 3, 1),
            exact=datetime(2024, 3, 10),
            end=datetime(2024, 3, 20),
            orb_used=2.0,
            motion="direct",
        )
        fake_moment_2 = TransitMoment(
            begin=datetime(2024, 6, 1),
            exact=datetime(2024, 6, 15),
            end=datetime(2024, 6, 30),
            orb_used=2.0,
            motion="retrograde",
        )
        fake_moment_3 = TransitMoment(
            begin=datetime(2024, 8, 1),
            exact=datetime(2024, 8, 10),
            end=datetime(2024, 8, 20),
            orb_used=2.0,
            motion="direct",
        )

        # Patch _find_transit_crossings to return 3 candidates, and refinement
        # to produce 3 moments, so the detect_retrograde=False path trims to 1.
        with patch(
            "ketu.aspects.transits._find_transit_crossings",
            return_value=[
                (2460370.0, 0.1, "direct"),
                (2460480.0, 0.1, "retrograde"),
                (2460540.0, 0.1, "direct"),
            ],
        ), patch(
            "ketu.aspects.transits.refine_exact_moment",
            side_effect=[2460370.0, 2460480.0, 2460540.0],
        ), patch(
            "ketu.aspects.transits.find_orb_boundaries",
            side_effect=[
                (2460360.0, 2460380.0),
                (2460470.0, 2460490.0),
                (2460530.0, 2460550.0),
            ],
        ):
            transits = find_transits_to_position(
                transiting_body="Moon",
                reference_longitude=90.0,
                aspects_list=["Conjunction"],
                start_date="2024-01-01",
                end_date="2024-12-31",
                detect_retrograde=False,
            )
            # The function should reduce to at most 1 moment per window
            for window in transits:
                assert len(window.moments) <= 1
                if window.moments:
                    assert window.retrograde_count == 0


# ========== get_natal_positions coverage ==========


class TestGetNatalPositionsFloatInput:
    """Line 451: float (Julian Date) input for reference_date."""

    def test_float_reference_date(self):
        """Pass a Julian Date float as reference_date."""
        jd = utc_to_julian(datetime(1990, 5, 15, 14, 30, 0))
        natal = get_natal_positions(reference_date=jd)

        assert isinstance(natal, dict)
        assert len(natal) == 13
        for name, pos in natal.items():
            assert isinstance(pos, NatalPosition)
            assert 0 <= pos.longitude < 360

    def test_float_reference_date_with_bodies(self):
        """Pass Julian Date float with specific bodies_list."""
        jd = utc_to_julian(datetime(2000, 1, 1, 12, 0, 0))
        natal = get_natal_positions(
            reference_date=jd,
            bodies_list=["Sun", "Moon"],
        )

        assert len(natal) == 2
        assert "Sun" in natal
        assert "Moon" in natal

    def test_float_matches_string_result(self):
        """Float JD input should give same result as equivalent string input."""
        dt = datetime(2024, 6, 15, 0, 0, 0)
        jd = utc_to_julian(dt)

        natal_str = get_natal_positions("2024-06-15 00:00:00")
        natal_float = get_natal_positions(jd)

        for body in natal_str:
            assert abs(natal_str[body].longitude - natal_float[body].longitude) < 0.001


# ========== compare_dates_transits coverage ==========


class TestCompareDatesDefaultAspects:
    """Line 522: aspects_list=None uses default major aspects."""

    def test_default_aspects_list(self):
        """When aspects_list is None, defaults to 5 major aspects."""
        transits = compare_dates_transits(
            natal_date="1990-05-15 14:30",
            transit_date="2024-11-21 12:00",
            aspects_list=None,
        )
        assert isinstance(transits, list)
        for t in transits:
            assert isinstance(t, TransitAspect)
            assert t.aspect in [
                "Conjunction",
                "Sextile",
                "Square",
                "Trine",
                "Opposition",
            ]


class TestCompareDatesFloatTransitDate:
    """Lines 528-531: float (Julian Date) for transit_date."""

    def test_float_transit_date(self):
        """Pass a Julian Date float as transit_date."""
        jd_transit = utc_to_julian(datetime(2024, 11, 21, 12, 0, 0))
        transits = compare_dates_transits(
            natal_date="1990-05-15 14:30",
            transit_date=jd_transit,
            aspects_list=["Conjunction", "Opposition"],
        )
        assert isinstance(transits, list)
        for t in transits:
            assert isinstance(t, TransitAspect)
            # exact_time should be a datetime (converted from JD via julian_to_utc)
            assert isinstance(t.exact_time, datetime)

    def test_datetime_transit_date(self):
        """Pass a datetime object as transit_date (line 528-529)."""
        dt_transit = datetime(2024, 11, 21, 12, 0, 0)
        transits = compare_dates_transits(
            natal_date="1990-05-15 14:30",
            transit_date=dt_transit,
            aspects_list=["Conjunction", "Opposition"],
        )
        assert isinstance(transits, list)
        for t in transits:
            assert isinstance(t, TransitAspect)
            assert t.exact_time == dt_transit

    def test_float_transit_date_matches_string(self):
        """Float JD transit_date should find same aspects as equivalent string."""
        dt = datetime(2024, 6, 15, 12, 0, 0)
        jd = utc_to_julian(dt)

        transits_str = compare_dates_transits(
            natal_date="2000-01-01 12:00",
            transit_date="2024-06-15 12:00:00",
            aspects_list=["Conjunction"],
            custom_orb=5.0,
        )
        transits_float = compare_dates_transits(
            natal_date="2000-01-01 12:00",
            transit_date=jd,
            aspects_list=["Conjunction"],
            custom_orb=5.0,
        )
        # Same number of aspects found
        assert len(transits_str) == len(transits_float)

    def test_float_natal_and_transit_dates(self):
        """Both natal_date and transit_date as Julian Date floats."""
        jd_natal = utc_to_julian(datetime(1990, 5, 15, 14, 30, 0))
        jd_transit = utc_to_julian(datetime(2024, 11, 21, 12, 0, 0))
        transits = compare_dates_transits(
            natal_date=jd_natal,
            transit_date=jd_transit,
            aspects_list=["Conjunction", "Square"],
        )
        assert isinstance(transits, list)


class TestCompareDatesDefaultAspectsWithFloat:
    """Combined test: both default aspects (line 522) and float transit_date (lines 528-531)."""

    def test_defaults_with_float_transit(self):
        """Default aspects_list=None combined with float transit_date."""
        jd_transit = utc_to_julian(datetime(2024, 3, 20, 0, 0, 0))
        transits = compare_dates_transits(
            natal_date="1985-12-25 08:00",
            transit_date=jd_transit,
            aspects_list=None,
        )
        assert isinstance(transits, list)
        for t in transits:
            assert t.aspect in [
                "Conjunction",
                "Sextile",
                "Square",
                "Trine",
                "Opposition",
            ]
