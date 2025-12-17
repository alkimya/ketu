#!/usr/bin/env python3
"""Example: Generate lunar calendar for a month.

This example demonstrates how to generate a lunar calendar showing
Sun-Moon aspects during the lunar cycle that overlaps most with a given month.

The lunar calendar tracks:
- New Moon (Conjunction 0°)
- First Quarter (Square 90°)
- Full Moon (Opposition 180°)
- Last Quarter (Square 90°)
- Plus optional intermediate aspects (Sextile 60°, Trine 120°, etc.)
"""

from ketu import generate_lunar_calendar, print_lunar_calendar


def main():
    """Generate and display lunar calendars for January 2024."""
    print("=" * 70)
    print("EXAMPLE: Lunar Calendar Generation")
    print("=" * 70)
    print()

    # Example 1: Full lunar calendar with all BIG_FIVE aspects
    print("\n" + "="*70)
    print("CALENDAR 1: All BIG_FIVE aspects (default)")
    print("="*70)
    calendar1 = generate_lunar_calendar(
        year=2024,
        month=1,
        timezone="Europe/Paris"
    )
    print(f"\nCycle: {calendar1.cycle.start.strftime('%Y-%m-%d %H:%M')} to "
          f"{calendar1.cycle.end.strftime('%Y-%m-%d %H:%M')}")
    print(f"Duration: {calendar1.cycle.days_in_month} days in January "
          f"(out of {(calendar1.cycle.end - calendar1.cycle.start).days} total)")
    print(f"\nSun-Moon aspects found: {len(calendar1.aspect_windows)}")
    for window in calendar1.aspect_windows:
        for moment in window.moments:
            phase_name = {
                "Conjunction": "🌑 New Moon",
                "Square": "🌓 Quarter",
                "Opposition": "🌕 Full Moon",
                "Sextile": "🌒 Sextile",
                "Trine": "🌔 Trine"
            }.get(window.aspect, window.aspect)
            print(f"  {moment.exact.strftime('%Y-%m-%d %H:%M %Z')} - {phase_name}")

    # Example 2: Only major phases (New, Quarters, Full)
    print("\n" + "="*70)
    print("CALENDAR 2: Major phases only (0°, 90°, 180°)")
    print("="*70)
    calendar2 = generate_lunar_calendar(
        year=2024,
        month=1,
        aspects=[0, 90, 180],  # Conjunction, Square, Opposition
        timezone="Europe/Paris"
    )
    print(f"\nMajor lunar phases: {len(calendar2.aspect_windows)}")
    for window in calendar2.aspect_windows:
        for moment in window.moments:
            phase_name = {
                "Conjunction": "🌑 New Moon",
                "Square": "🌓 Quarter",
                "Opposition": "🌕 Full Moon"
            }.get(window.aspect, window.aspect)
            print(f"  {moment.exact.strftime('%Y-%m-%d %H:%M %Z')} - {phase_name}")

    # Example 3: All seven major aspects
    print("\n" + "="*70)
    print("CALENDAR 3: All 7 major aspects")
    print("="*70)
    calendar3 = generate_lunar_calendar(
        year=2024,
        month=1,
        aspects=[0, 30, 60, 90, 120, 150, 180],  # All major aspects
        timezone="Europe/Paris"
    )
    print(f"\nAll Sun-Moon aspects: {len(calendar3.aspect_windows)}")
    for window in calendar3.aspect_windows:
        for moment in window.moments:
            print(f"  {moment.exact.strftime('%Y-%m-%d %H:%M %Z')} - {window.aspect}")


if __name__ == "__main__":
    main()
