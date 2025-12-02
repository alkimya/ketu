"""Example: Zodiacal Chart Visualization

This example demonstrates how to create beautiful zodiacal charts
with planetary positions and aspects.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
from ketu.export.chart import draw_zodiacal_chart


def example_1_current_chart():
    """Example 1: Chart for current date."""
    print("=" * 70)
    print("Example 1: Zodiacal Chart for Current Date")
    print("=" * 70)

    draw_zodiacal_chart(
        date=datetime.now(),
        filename="chart_current.svg",
        title="Current Planetary Positions"
    )

    print("✓ Chart saved to: chart_current.svg\n")


def example_2_summer_solstice():
    """Example 2: Summer Solstice 2024 - Sun at top (90° Cancer) - Paris time."""
    print("=" * 70)
    print("Example 2: Summer Solstice 2024 (Paris Time)")
    print("=" * 70)

    draw_zodiacal_chart(
        date="2024-06-20 22:51",
        filename="chart_summer_solstice.svg",
        title="Summer Solstice 2024 - Sun at Zenith",
        timezone="Europe/Paris"
    )

    print("✓ Sun should be near top (90° Cancer)")
    print("✓ Displayed in Europe/Paris timezone (CEST)")
    print("✓ Chart saved to: chart_summer_solstice.svg\n")


def example_3_winter_solstice():
    """Example 3: Winter Solstice 2024 - Sun at bottom (270° Capricorn)."""
    print("=" * 70)
    print("Example 3: Winter Solstice 2024")
    print("=" * 70)

    draw_zodiacal_chart(
        date="2024-12-21 09:21",
        filename="chart_winter_solstice.svg",
        title="Winter Solstice 2024 - Sun at Nadir"
    )

    print("✓ Sun should be near bottom (270° Capricorn)")
    print("✓ Chart saved to: chart_winter_solstice.svg\n")


def example_4_spring_equinox():
    """Example 4: Spring Equinox 2024 - Sun at East (0° Aries)."""
    print("=" * 70)
    print("Example 4: Spring Equinox 2024")
    print("=" * 70)

    draw_zodiacal_chart(
        date="2024-03-20 03:06",
        filename="chart_spring_equinox.svg",
        title="Spring Equinox 2024 - Sun at East"
    )

    print("✓ Sun should be at East (0° Aries)")
    print("✓ Chart saved to: chart_spring_equinox.svg\n")


def example_5_autumn_equinox():
    """Example 5: Autumn Equinox 2024 - Sun at West (180° Libra)."""
    print("=" * 70)
    print("Example 5: Autumn Equinox 2024")
    print("=" * 70)

    draw_zodiacal_chart(
        date="2024-09-22 12:44",
        filename="chart_autumn_equinox.svg",
        title="Autumn Equinox 2024 - Sun at West"
    )

    print("✓ Sun should be at West (180° Libra)")
    print("✓ Chart saved to: chart_autumn_equinox.svg\n")


def example_6_full_moon():
    """Example 6: Full Moon - Strong Sun-Moon opposition aspect."""
    print("=" * 70)
    print("Example 6: Full Moon with Strong Opposition")
    print("=" * 70)

    draw_zodiacal_chart(
        date="2024-11-15 21:28",
        filename="chart_full_moon.svg",
        title="Full Moon - Sun ☍ Moon"
    )

    print("✓ Sun-Moon opposition should be visible")
    print("✓ Chart saved to: chart_full_moon.svg\n")


def example_7_positions_only():
    """Example 7: Chart without aspect lines."""
    print("=" * 70)
    print("Example 7: Positions Only (No Aspects)")
    print("=" * 70)

    draw_zodiacal_chart(
        date="2024-01-01 00:00",
        filename="chart_positions_only.svg",
        title="2024 New Year - Positions Only",
        show_aspects=False
    )

    print("✓ Chart with positions only (no aspect lines)")
    print("✓ Chart saved to: chart_positions_only.svg\n")


def example_8_datetime_with_timezone():
    """Example 8: Using datetime object with timezone."""
    print("=" * 70)
    print("Example 8: Datetime with Timezone (New York)")
    print("=" * 70)

    # Create datetime with timezone
    dt = datetime(2024, 11, 15, 16, 28, tzinfo=ZoneInfo("America/New_York"))

    draw_zodiacal_chart(
        date=dt,
        filename="chart_ny_timezone.svg",
        title="Full Moon - New York Time"
    )

    print("✓ Using datetime object with tzinfo")
    print("✓ Timezone automatically detected from datetime")
    print("✓ Chart saved to: chart_ny_timezone.svg\n")


def main():
    """Run all chart visualization examples."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 18 + "ZODIACAL CHART EXAMPLES" + " " * 27 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    # Run examples
    example_1_current_chart()
    example_2_summer_solstice()
    example_3_winter_solstice()
    example_4_spring_equinox()
    example_5_autumn_equinox()
    example_6_full_moon()
    example_7_positions_only()
    example_8_datetime_with_timezone()

    print("=" * 70)
    print("All charts generated successfully!")
    print("=" * 70)
    print()
    print("Charts created:")
    print("  • chart_current.svg - Current planetary positions")
    print("  • chart_summer_solstice.svg - Sun at top (Cancer) - Paris time")
    print("  • chart_winter_solstice.svg - Sun at bottom (Capricorn)")
    print("  • chart_spring_equinox.svg - Sun at East (Aries)")
    print("  • chart_autumn_equinox.svg - Sun at West (Libra)")
    print("  • chart_full_moon.svg - Full Moon opposition")
    print("  • chart_positions_only.svg - Positions without aspects")
    print("  • chart_ny_timezone.svg - Full Moon in New York time")
    print()
    print("Features:")
    print("  ✓ Zodiac wheel with 12 signs")
    print("  ✓ Planetary positions with Unicode symbols")
    print("  ✓ Color-coded aspect lines")
    print("  ✓ Intensity based on orb (closer = brighter)")
    print("  ✓ Glow effect for applying aspects")
    print("  ✓ Retrograde markers")
    print("  ✓ Timezone support (auto-detect or specify)")
    print("  ✓ Legend with positions and aspect table")
    print()


if __name__ == "__main__":
    main()
