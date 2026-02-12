#!/usr/bin/env python3
"""Demonstration of aspect timeline generation for ML/research applications.

This example shows how to use the aspect_timelines module to generate
planetary aspect calendars for various applications:
- Machine learning / deep learning
- Cycle research
- Time series analysis
"""

from datetime import datetime
from zoneinfo import ZoneInfo
import json

from ketu.aspects import generate_aspect_timeline


def demo_mars_sun_timeline():
    """Example 1: Mars-Sun aspects for 2024 (Martian calendar)."""
    print("=" * 70)
    print("EXAMPLE 1: Mars-Sun Aspect Timeline (Martian Calendar)")
    print("=" * 70)

    timeline = generate_aspect_timeline(
        body1="Sun",
        body2="Mars",
        start_date="2024-01-01",
        end_date="2024-12-31",
        timezone="UTC"
    )

    print(f"\nBody 1: {timeline.body1}")
    print(f"Body 2: {timeline.body2}")
    print(f"Period: {timeline.start_date.date()} to {timeline.end_date.date()}")
    print(f"Found {len(timeline)} aspect events\n")

    # Display first few events
    print("First 5 events:")
    for i, event in enumerate(timeline.events[:5], 1):
        print(f"{i}. {event.aspect_name:12} @ {event.timestamp.strftime('%Y-%m-%d %H:%M')} UTC")
        print(f"   Orb: {event.orb:.4f}° | Strength: {event.aspect_strength:.3f}")
        print(f"   Relative velocity: {event.relative_velocity:+.4f}°/day")
        if event.body1_retro or event.body2_retro:
            print(f"   RETROGRADE: Mars={event.body2_retro}, Retro intensity={event.retro_intensity:.4f}")
        print()

    return timeline


def demo_venus_neptune_timeline():
    """Example 2: Venus-Neptune aspects (slow planet interaction)."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Venus-Neptune Aspect Timeline")
    print("=" * 70)

    timeline = generate_aspect_timeline(
        body1="Venus",
        body2="Neptune",
        start_date="2024-01-01",
        end_date="2024-06-30",
        aspects_list=["Conjunction", "Square", "Trine", "Opposition"],
        timezone="America/New_York"
    )

    print(f"\nBody 1: {timeline.body1}")
    print(f"Body 2: {timeline.body2}")
    print(f"Aspects included: {timeline.aspects_included}")
    print(f"Found {len(timeline)} aspect events\n")

    # Display all events
    for event in timeline.events:
        retro_flag = " [RETRO]" if (event.body1_retro or event.body2_retro) else ""
        print(f"{event.aspect_name:12} @ {event.timestamp.strftime('%Y-%m-%d %H:%M')}{retro_flag}")
        print(f"   Duration: {event.duration_days:.1f} days | Strength: {event.aspect_strength:.3f}")

    return timeline


def demo_moon_sun_timeline():
    """Example 3: Moon-Sun aspects for one month (Lunar calendar)."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Moon-Sun Timeline for January 2024 (Lunar Calendar)")
    print("=" * 70)

    timeline = generate_aspect_timeline(
        body1="Sun",
        body2="Moon",
        start_date="2024-01-01",
        end_date="2024-01-31",
        detect_retrograde=False,  # Moon doesn't retrograde
    )

    print(f"\nFound {len(timeline)} lunar aspects in January 2024\n")

    # Group by aspect type
    by_aspect = {}
    for event in timeline.events:
        if event.aspect_name not in by_aspect:
            by_aspect[event.aspect_name] = []
        by_aspect[event.aspect_name].append(event)

    for aspect_name in ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]:
        if aspect_name in by_aspect:
            events = by_aspect[aspect_name]
            print(f"{aspect_name}: {len(events)} occurrence(s)")
            for event in events:
                print(f"   {event.timestamp.strftime('%Y-%m-%d %H:%M')} UTC")

    return timeline


def demo_export_formats(timeline):
    """Example 4: Export to different formats for ML/research."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Export to ML-Ready Formats")
    print("=" * 70)

    # Export to JSON
    print("\n1. Export to JSON:")
    json_data = timeline.to_json()
    print(f"   Metadata keys: {list(json_data['metadata'].keys())}")
    print(f"   Event count: {json_data['metadata']['event_count']}")
    print(f"   First event fields: {list(json_data['events'][0].keys())}")

    # Export to NumPy
    print("\n2. Export to NumPy structured array:")
    np_array = timeline.to_numpy()
    print(f"   Shape: {np_array.shape}")
    print(f"   Dtype: {np_array.dtype.names}")
    print(f"   Sample (first 3 rows):")
    print(f"   Julian Day | Body IDs | Aspect | Orb | Strength | Retro")
    for i in range(min(3, len(np_array))):
        row = np_array[i]
        print(f"   {row['julian_day']:.2f} | {row['body1_id']},{row['body2_id']} | "
              f"{row['aspect_type']:3.0f}° | {row['orb']:.4f}° | {row['aspect_strength']:.3f} | "
              f"{row['body1_retro']},{row['body2_retro']}")

    # Export to Pandas
    try:
        print("\n3. Export to Pandas DataFrame:")
        df = timeline.to_pandas()
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        print(f"\n   First 3 rows:")
        print(df.head(3)[['body1_name', 'body2_name', 'aspect_name', 'orb', 'aspect_strength']])

        # Demonstrate some Pandas operations
        print("\n   Group by aspect type:")
        aspect_counts = df.groupby('aspect_name').size()
        for aspect, count in aspect_counts.items():
            print(f"      {aspect}: {count}")

    except ImportError:
        print("\n3. Pandas not installed - skipping DataFrame demo")
        print("   Install with: pip install pandas")


def demo_custom_aspects():
    """Example 5: Custom aspect list with specific angles."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Custom Aspects (Only Major Angles)")
    print("=" * 70)

    timeline = generate_aspect_timeline(
        body1="Jupiter",
        body2="Saturn",
        start_date="2024-01-01",
        end_date="2025-12-31",
        aspects_list=[0, 90, 180],  # Only conjunction, square, opposition
        detect_retrograde=True
    )

    print(f"\nJupiter-Saturn major aspects (2024-2025)")
    print(f"Aspects: Conjunction (0°), Square (90°), Opposition (180°)")
    print(f"Found {len(timeline)} events\n")

    for event in timeline.events:
        retro_info = ""
        if event.body1_retro or event.body2_retro:
            retro_info = f" | Retro: J={event.body1_retro}, S={event.body2_retro}"
        print(f"{event.aspect_name:12} @ {event.timestamp.strftime('%Y-%m-%d')} | "
              f"Strength: {event.aspect_strength:.3f}{retro_info}")

    return timeline


if __name__ == "__main__":
    # Run all demonstrations
    print("\n" + "=" * 70)
    print("KETU ASPECT TIMELINE DEMONSTRATION")
    print("ML/Research-Ready Planetary Aspect Calendars")
    print("=" * 70)

    # Example 1: Mars-Sun
    mars_sun = demo_mars_sun_timeline()

    # Example 2: Venus-Neptune
    venus_neptune = demo_venus_neptune_timeline()

    # Example 3: Moon-Sun (Lunar calendar)
    moon_sun = demo_moon_sun_timeline()

    # Example 4: Export formats (using Mars-Sun timeline)
    demo_export_formats(mars_sun)

    # Example 5: Custom aspects
    jupiter_saturn = demo_custom_aspects()

    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nKey features demonstrated:")
    print("✓ Time window approach (aspects between dates)")
    print("✓ Multiple planet pairs (Mars-Sun, Venus-Neptune, etc.)")
    print("✓ Custom aspect lists")
    print("✓ Retrograde detection")
    print("✓ ML-ready exports (NumPy, Pandas, JSON)")
    print("✓ Full cycle information (phase, velocity, strength)")
    print("\nReady for: ML, deep learning, research!")
