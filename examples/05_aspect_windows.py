"""Example: Finding aspect windows with begin, exact, and end times.

This example demonstrates the new aspect window API that provides
precise timing for aspect events including:
- Entry into orb (begin)
- Exact aspect moment
- Exit from orb (end)
- Retrograde motion detection
"""

from datetime import datetime
from ketu.aspect_windows import find_aspect_window, find_aspects_timeline


def example_1_full_moon():
    """Example 1: Finding a Full Moon (Sun-Moon Opposition)."""
    print("=" * 70)
    print("Example 1: Full Moon (Sun-Moon Opposition)")
    print("=" * 70)

    result = find_aspect_window(
        body1="Sun",
        body2="Moon",
        aspect="Opposition",
        around_date="2024-03-25",
        search_days=3,
    )

    if result.moments:
        moment = result.moments[0]
        print(f"\nFull Moon Details:")
        print(f"  Begin (enters orb): {moment.begin}")
        print(f"  Exact opposition:   {moment.exact}")
        print(f"  End (exits orb):    {moment.end}")
        print(f"  Orb used:          {moment.orb_used}°")
        print(f"  Motion:            {moment.motion}")

        # Calculate duration
        duration_hours = (moment.end - moment.begin).total_seconds() / 3600
        print(f"  Total duration:    {duration_hours:.1f} hours")
    else:
        print("No opposition found in search range")


def example_2_new_moon():
    """Example 2: Finding a New Moon (Sun-Moon Conjunction)."""
    print("\n" + "=" * 70)
    print("Example 2: New Moon (Sun-Moon Conjunction)")
    print("=" * 70)

    result = find_aspect_window(
        body1="Sun",
        body2="Moon",
        aspect="Conjunction",
        around_date="2024-04-08",
        search_days=3,
    )

    if result.moments:
        moment = result.moments[0]
        print(f"\nNew Moon Details:")
        print(f"  Begin: {moment.begin}")
        print(f"  Exact: {moment.exact}")
        print(f"  End:   {moment.end}")

        # Time to exact from begin
        time_to_exact = (moment.exact - moment.begin).total_seconds() / 3600
        print(f"  Time to exactitude: {time_to_exact:.1f} hours")
    else:
        print("No conjunction found in search range")


def example_3_monthly_lunation_cycle():
    """Example 3: Timeline of all Sun-Moon aspects in a month."""
    print("\n" + "=" * 70)
    print("Example 3: Monthly Lunation Cycle (March 2024)")
    print("=" * 70)

    timeline = find_aspects_timeline(
        body1="Sun",
        body2="Moon",
        aspects_list=["Conjunction", "Sextile", "Square", "Trine", "Opposition"],
        start_date="2024-03-01",
        end_date="2024-03-31",
    )

    print(f"\nFound {len(timeline)} lunation aspects:")
    for i, window in enumerate(timeline, 1):
        if window.moments:
            moment = window.moments[0]
            print(f"\n{i}. {window.aspect} ({window.body1}-{window.body2})")
            print(f"   Exact: {moment.exact.strftime('%Y-%m-%d %H:%M UTC')}")
            print(f"   Duration: {(moment.end - moment.begin).total_seconds() / 3600:.1f}h")


def example_4_custom_orb():
    """Example 4: Using a custom orb."""
    print("\n" + "=" * 70)
    print("Example 4: Custom Orb (Tight orb for precision work)")
    print("=" * 70)

    # Compare default orb vs tight orb
    print("\nWith default orb (12°):")
    result_default = find_aspect_window(
        body1="Sun",
        body2="Moon",
        aspect="Opposition",
        around_date="2024-03-25",
        search_days=3,
    )
    if result_default.moments:
        m = result_default.moments[0]
        duration_default = (m.end - m.begin).total_seconds() / 3600
        print(f"  Duration: {duration_default:.1f} hours")

    print("\nWith tight orb (5°):")
    result_tight = find_aspect_window(
        body1="Sun",
        body2="Moon",
        aspect="Opposition",
        around_date="2024-03-25",
        search_days=3,
        custom_orb=5.0,
    )
    if result_tight.moments:
        m = result_tight.moments[0]
        duration_tight = (m.end - m.begin).total_seconds() / 3600
        print(f"  Duration: {duration_tight:.1f} hours")
        print(f"  Reduction: {duration_default - duration_tight:.1f} hours")


def example_5_slow_planets():
    """Example 5: Slower moving planets (Jupiter-Saturn)."""
    print("\n" + "=" * 70)
    print("Example 5: Jupiter-Saturn Conjunction")
    print("=" * 70)

    # The Great Conjunction of December 2020
    result = find_aspect_window(
        body1="Jupiter",
        body2="Saturn",
        aspect="Conjunction",
        around_date="2020-12-21",
        search_days=60,  # Need wider search for slow planets
    )

    if result.moments:
        moment = result.moments[0]
        print(f"\nGreat Conjunction Details:")
        print(f"  Begin: {moment.begin.strftime('%Y-%m-%d')}")
        print(f"  Exact: {moment.exact.strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"  End:   {moment.end.strftime('%Y-%m-%d')}")
        print(f"  Orb:   {moment.orb_used}°")

        duration_days = (moment.end - moment.begin).total_seconds() / 86400
        print(f"  Duration: {duration_days:.1f} days")
    else:
        print("No conjunction found (may need wider search range)")


def example_6_year_timeline():
    """Example 6: Full year timeline for two bodies."""
    print("\n" + "=" * 70)
    print("Example 6: Venus-Mars Aspects in 2024")
    print("=" * 70)

    timeline = find_aspects_timeline(
        body1="Venus",
        body2="Mars",
        aspects_list=["Conjunction", "Square", "Trine", "Opposition"],
        start_date="2024-01-01",
        end_date="2024-12-31",
    )

    if timeline:
        print(f"\nFound {len(timeline)} Venus-Mars aspects in 2024:")
        for window in timeline:
            if window.moments:
                moment = window.moments[0]
                print(f"  {window.aspect:12s}: {moment.exact.strftime('%Y-%m-%d %H:%M UTC')}")
    else:
        print("\nNo aspects found in 2024")


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "ASPECT WINDOWS EXAMPLES" + " " * 30 + "║")
    print("╚" + "═" * 68 + "╝")

    # Run all examples
    example_1_full_moon()
    example_2_new_moon()
    example_3_monthly_lunation_cycle()
    example_4_custom_orb()
    example_5_slow_planets()
    example_6_year_timeline()

    print("\n" + "=" * 70)
    print("Examples completed successfully!")
    print("=" * 70 + "\n")
