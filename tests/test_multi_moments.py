#!/usr/bin/env python3
"""Test if find_aspect_window can find multiple new moons in one call."""

from datetime import datetime
from zoneinfo import ZoneInfo

from ketu.aspect_windows import find_aspect_window


def test_multiple_new_moons():
    """Test finding multiple new moons in a wide search window."""
    print("\n" + "=" * 70)
    print("TEST: Multiple New Moons in Wide Search Window")
    print("=" * 70)

    # Search for new moons in January 2024
    # Should find: ~Dec 12, ~Jan 11, ~Feb 10
    test_date = datetime(2024, 1, 15, tzinfo=ZoneInfo("UTC"))

    print(f"\nSearching around: {test_date}")
    print("Search period: ±30 days (60 days total)")

    window = find_aspect_window(
        body1=0,  # Sun
        body2=1,  # Moon
        aspect=0,  # Conjunction (New Moon)
        around_date=test_date,
        search_days=30,  # ±30 days = 60 days total
        detect_retrograde=False,
    )

    print(f"\nFound {len(window.moments)} new moon(s):")
    for i, moment in enumerate(window.moments, 1):
        print(f"  {i}. {moment.exact.strftime('%Y-%m-%d %H:%M %Z')}")
        print(f"     Window: {moment.begin.strftime('%Y-%m-%d %H:%M')} → {moment.end.strftime('%Y-%m-%d %H:%M')}")

    # Expected: Should find 2-3 new moons
    if len(window.moments) >= 2:
        print(f"\n✓ SUCCESS: Found {len(window.moments)} new moons in single call")
        print("  This means we can optimize find_new_moons_around_month()")
    else:
        print(f"\n✗ ISSUE: Only found {len(window.moments)} new moon")
        print("  Wide search might not return all moments")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    test_multiple_new_moons()
