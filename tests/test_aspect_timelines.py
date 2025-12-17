#!/usr/bin/env python3
"""Unit tests for aspect_timelines module (ML/research-ready planetary calendars)."""

import pytest
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np

from ketu.aspects import (
    AspectEvent,
    AspectTimeline,
    generate_aspect_timeline,
)


class TestAspectTimeline:
    """Test aspect timeline generation."""

    def test_mars_sun_timeline_2024(self):
        """Test Mars-Sun aspect timeline for 2024."""
        timeline = generate_aspect_timeline(
            body1="Sun",
            body2="Mars",
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        assert timeline.body1 == "Sun"
        assert timeline.body2 == "Mars"
        assert len(timeline) > 0
        assert all(isinstance(e, AspectEvent) for e in timeline.events)

        # Verify events are sorted chronologically
        timestamps = [e.timestamp for e in timeline.events]
        assert timestamps == sorted(timestamps)

    def test_venus_neptune_custom_aspects(self):
        """Test Venus-Neptune with custom aspect list."""
        timeline = generate_aspect_timeline(
            body1="Venus",
            body2="Neptune",
            start_date="2024-01-01",
            end_date="2024-06-30",
            aspects_list=["Conjunction", "Square", "Opposition"],
        )

        # All events should be one of the requested aspects
        for event in timeline.events:
            assert event.aspect_name in ["Conjunction", "Square", "Opposition"]

    def test_moon_sun_lunar_calendar(self):
        """Test Moon-Sun timeline (lunar calendar approach)."""
        timeline = generate_aspect_timeline(
            body1="Sun",
            body2="Moon",
            start_date="2024-01-01",
            end_date="2024-01-31",
            detect_retrograde=False,
        )

        # Should find lunar aspects in January
        assert len(timeline) >= 5  # At least a few major aspects

        # Moon never retrogrades
        for event in timeline.events:
            assert event.body2_retro == False  # Use == to handle np.bool_

    def test_jupiter_saturn_retrograde_detection(self):
        """Test retrograde detection with Jupiter-Saturn."""
        timeline = generate_aspect_timeline(
            body1="Jupiter",
            body2="Saturn",
            start_date="2024-01-01",
            end_date="2025-12-31",
            aspects_list=[0, 90, 180],
            detect_retrograde=True,
        )

        # Should have some events
        assert len(timeline) > 0

        # Check that retrograde flags are set correctly
        has_retrograde = any(e.body1_retro or e.body2_retro for e in timeline.events)
        # At least one planet should be retrograde at some point
        assert has_retrograde

    def test_event_enrichment(self):
        """Test that events contain all ML features."""
        timeline = generate_aspect_timeline(
            body1="Sun",
            body2="Mars",
            start_date="2024-07-01",
            end_date="2024-08-01",
        )

        if len(timeline) > 0:
            event = timeline.events[0]

            # Check all required fields exist
            assert hasattr(event, "timestamp")
            assert hasattr(event, "julian_day")
            assert hasattr(event, "body1_id")
            assert hasattr(event, "body2_id")
            assert hasattr(event, "aspect_type")
            assert hasattr(event, "aspect_name")
            assert hasattr(event, "orb")
            assert hasattr(event, "orb_tolerance")
            assert hasattr(event, "aspect_strength")

            # Cycle information
            assert hasattr(event, "angular_separation")
            assert hasattr(event, "phase")
            assert hasattr(event, "relative_velocity")
            assert hasattr(event, "days_to_exact")

            # Retrograde information
            assert hasattr(event, "body1_retro")
            assert hasattr(event, "body2_retro")
            assert hasattr(event, "retro_intensity")

            # Window timing
            assert hasattr(event, "window_begin")
            assert hasattr(event, "window_end")
            assert hasattr(event, "duration_days")

            # Validate ranges
            assert 0 <= event.aspect_strength <= 1.0
            assert event.orb >= 0
            assert event.duration_days > 0

    def test_timezone_handling(self):
        """Test timezone parameter."""
        tz = ZoneInfo("America/New_York")
        timeline = generate_aspect_timeline(
            body1="Sun",
            body2="Moon",
            start_date="2024-01-15",
            end_date="2024-01-20",
            timezone=tz,
        )

        assert timeline.timezone == tz


class TestExportFormats:
    """Test export methods for ML/research applications."""

    @pytest.fixture
    def sample_timeline(self):
        """Create a sample timeline for testing exports."""
        return generate_aspect_timeline(
            body1="Sun",
            body2="Mars",
            start_date="2024-07-01",
            end_date="2024-12-31",
        )

    def test_to_dict_list(self, sample_timeline):
        """Test conversion to dict list."""
        dict_list = sample_timeline.to_dict_list()

        assert isinstance(dict_list, list)
        assert len(dict_list) == len(sample_timeline)

        if len(dict_list) > 0:
            event_dict = dict_list[0]
            assert isinstance(event_dict, dict)

            # Check required keys
            required_keys = [
                "timestamp",
                "julian_day",
                "body1_id",
                "body2_id",
                "aspect_type",
                "aspect_name",
                "orb",
                "aspect_strength",
                "relative_velocity",
            ]
            for key in required_keys:
                assert key in event_dict

    def test_to_numpy(self, sample_timeline):
        """Test conversion to NumPy structured array."""
        np_array = sample_timeline.to_numpy()

        assert isinstance(np_array, np.ndarray)
        assert len(np_array) == len(sample_timeline)

        # Check dtype fields
        expected_fields = [
            "julian_day",
            "body1_id",
            "body2_id",
            "aspect_type",
            "orb",
            "aspect_strength",
            "phase",
            "relative_velocity",
        ]
        for field in expected_fields:
            assert field in np_array.dtype.names

        # Verify data types
        assert np_array["julian_day"].dtype == np.float64
        assert np_array["body1_id"].dtype == np.int32
        assert np_array["aspect_strength"].dtype == np.float32

    def test_to_pandas(self, sample_timeline):
        """Test conversion to Pandas DataFrame."""
        pytest.importorskip("pandas")  # Skip if pandas not installed

        df = sample_timeline.to_pandas()

        # Should have timestamp index
        assert df.index.name == "timestamp"
        assert len(df) == len(sample_timeline)

        # Check required columns
        required_columns = [
            "julian_day",
            "body1_name",
            "body2_name",
            "aspect_name",
            "orb",
            "aspect_strength",
            "relative_velocity",
            "body1_retro",
            "body2_retro",
        ]
        for col in required_columns:
            assert col in df.columns

    def test_to_json(self, sample_timeline):
        """Test conversion to JSON."""
        json_data = sample_timeline.to_json()

        assert isinstance(json_data, dict)
        assert "metadata" in json_data
        assert "events" in json_data

        metadata = json_data["metadata"]
        assert metadata["body1"] == "Sun"
        assert metadata["body2"] == "Mars"
        assert metadata["event_count"] == len(sample_timeline)
        assert isinstance(metadata["aspects_included"], list)
        assert isinstance(metadata["detect_retrograde"], bool)

        events = json_data["events"]
        assert isinstance(events, list)
        assert len(events) == len(sample_timeline)

    def test_empty_timeline_exports(self):
        """Test exports when no events found."""
        # Search in a narrow window where no aspects occur
        timeline = generate_aspect_timeline(
            body1="Jupiter",
            body2="Pluto",
            start_date="2024-01-01 00:00:00",
            end_date="2024-01-01 01:00:00",  # Very narrow, unlikely to have aspect
        )

        # Should handle empty timeline gracefully
        dict_list = timeline.to_dict_list()
        assert isinstance(dict_list, list)
        assert len(dict_list) == 0

        np_array = timeline.to_numpy()
        assert len(np_array) == 0

        json_data = timeline.to_json()
        assert json_data["metadata"]["event_count"] == 0
        assert len(json_data["events"]) == 0


class TestInputValidation:
    """Test input validation and error handling."""

    def test_body_by_name(self):
        """Test body specified by name."""
        timeline = generate_aspect_timeline(
            body1="Sun",
            body2="Moon",
            start_date="2024-01-15",
            end_date="2024-01-20",
        )
        assert timeline.body1 == "Sun"
        assert timeline.body2 == "Moon"

    def test_body_by_id(self):
        """Test body specified by ID."""
        timeline = generate_aspect_timeline(
            body1=0,  # Sun
            body2=1,  # Moon
            start_date="2024-01-15",
            end_date="2024-01-20",
        )
        assert timeline.body1 == "Sun"
        assert timeline.body2 == "Moon"

    def test_date_formats(self):
        """Test different date input formats."""
        # ISO string
        timeline1 = generate_aspect_timeline(
            body1="Sun",
            body2="Moon",
            start_date="2024-01-15",
            end_date="2024-01-20",
        )
        assert len(timeline1) > 0

        # Datetime object
        start = datetime(2024, 1, 15, tzinfo=ZoneInfo("UTC"))
        end = datetime(2024, 1, 20, tzinfo=ZoneInfo("UTC"))
        timeline2 = generate_aspect_timeline(
            body1="Sun",
            body2="Moon",
            start_date=start,
            end_date=end,
        )
        assert len(timeline2) > 0

    def test_invalid_body(self):
        """Test error handling for invalid body."""
        with pytest.raises(ValueError, match="Unknown body"):
            generate_aspect_timeline(
                body1="InvalidBody",
                body2="Moon",
                start_date="2024-01-15",
                end_date="2024-01-20",
            )

    def test_invalid_aspect(self):
        """Test error handling for invalid aspect."""
        with pytest.raises(ValueError, match="Unknown aspect"):
            generate_aspect_timeline(
                body1="Sun",
                body2="Moon",
                start_date="2024-01-15",
                end_date="2024-01-20",
                aspects_list=["InvalidAspect"],
            )


class TestPerformance:
    """Test performance characteristics."""

    def test_large_time_range(self):
        """Test performance with larger time range."""
        import time

        start = time.perf_counter()
        timeline = generate_aspect_timeline(
            body1="Sun",
            body2="Moon",
            start_date="2024-01-01",
            end_date="2024-12-31",
        )
        elapsed = time.perf_counter() - start

        # Should complete in reasonable time
        assert elapsed < 10.0  # Less than 10 seconds

        # Should find many lunar aspects in a year
        assert len(timeline) > 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
