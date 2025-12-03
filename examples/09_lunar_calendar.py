#!/usr/bin/env python3
"""Example: Generate lunar calendar for a month.

This example demonstrates how to generate a lunar calendar showing all
major aspects during the lunar cycle that overlaps most with a given month.
"""

from ketu import generate_lunar_calendar, print_lunar_calendar


def main():
    """Generate and display lunar calendar for January 2024."""
    print("=" * 70)
    print("EXAMPLE: Lunar Calendar Generation")
    print("=" * 70)
    print()

    # Generate lunar calendar for January 2024 in Paris timezone
    print("Generating lunar calendar for January 2024...")
    calendar = generate_lunar_calendar(
        year=2024,
        month=1,
        timezone="Europe/Paris"
    )

    # Display the calendar
    print_lunar_calendar(calendar)

    # Show some statistics
    print("\n" + "=" * 70)
    print("STATISTICS")
    print("=" * 70)
    print(f"\nTotal aspects found: {len(calendar.aspect_windows)}")

    # Count by aspect type
    aspect_counts = {}
    for window in calendar.aspect_windows:
        aspect_type = window.aspect
        aspect_counts[aspect_type] = aspect_counts.get(aspect_type, 0) + 1

    print("\nAspects by type:")
    for aspect_type, count in sorted(aspect_counts.items()):
        print(f"  {aspect_type}: {count}")

    # Find aspects with retrograde moments
    retrograde_aspects = [w for w in calendar.aspect_windows if w.retrograde_count > 0]
    if retrograde_aspects:
        print(f"\nAspects with retrograde motion: {len(retrograde_aspects)}")
        for window in retrograde_aspects:
            print(f"  {window.body1} {window.aspect} {window.body2} "
                  f"({len(window.moments)} exact moments)")


if __name__ == "__main__":
    main()
