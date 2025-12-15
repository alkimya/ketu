#!/usr/bin/env python3
"""Generate complete planetary calendar with all aspects between all planets.

This example shows how to efficiently generate a full planetary calendar
for a lunar month (new moon to new moon) with all BIG_FIVE aspects between
all planet pairs.
"""

import time
from datetime import datetime
from zoneinfo import ZoneInfo
from itertools import combinations

from ketu import generate_aspect_timeline
from ketu.aspects import find_aspect_window
from ketu.calculations import utc_to_julian


# Traditional planets (excluding modern outer planets for speed)
TRADITIONAL_PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

# All planets including modern
ALL_PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
               "Uranus", "Neptune", "Pluto"]


def find_lunar_month_bounds(year: int, month: int, timezone="UTC"):
    """Find new moon bounds for a given month.

    Args:
        year: Year
        month: Month (1-12)
        timezone: Timezone string

    Returns:
        Tuple of (start_new_moon_datetime, end_new_moon_datetime)
    """
    # Search around the middle of the month
    search_date = datetime(year, month, 15, tzinfo=ZoneInfo(timezone))

    # Find new moon in this month
    window = find_aspect_window(
        body1="Sun",
        body2="Moon",
        aspect=0,  # Conjunction = New Moon
        around_date=search_date,
        search_days=17,  # ±17 days to cover the month
        detect_retrograde=False,
    )

    if not window.moments:
        raise ValueError(f"No new moon found around {year}-{month:02d}")

    new_moon_1 = window.moments[0].exact

    # Find next new moon (approximately 29.53 days later)
    next_search = datetime(
        new_moon_1.year,
        new_moon_1.month,
        new_moon_1.day,
        tzinfo=ZoneInfo(timezone)
    )

    # Add 29 days and search
    jd_next = utc_to_julian(next_search) + 29.53
    from ketu.calculations import julian_to_utc
    next_search_dt = julian_to_utc(jd_next)

    window2 = find_aspect_window(
        body1="Sun",
        body2="Moon",
        aspect=0,
        around_date=next_search_dt,
        search_days=3,  # Narrow search
        detect_retrograde=False,
    )

    if not window2.moments:
        raise ValueError(f"No next new moon found after {new_moon_1}")

    new_moon_2 = window2.moments[0].exact

    return new_moon_1, new_moon_2


def generate_full_planetary_calendar(
    start_date,
    end_date,
    planets=None,
    aspects_list=None,
    detect_retrograde=True,
    timezone="UTC",
):
    """Generate complete planetary calendar with all aspects between all planets.

    Args:
        start_date: Start datetime or string
        end_date: End datetime or string
        planets: List of planet names (default: TRADITIONAL_PLANETS)
        aspects_list: List of aspects (default: BIG_FIVE)
        detect_retrograde: Enable retrograde detection
        timezone: Timezone string

    Returns:
        Dictionary with:
            - 'timelines': Dict of {(planet1, planet2): AspectTimeline}
            - 'all_events': List of all events sorted chronologically
            - 'stats': Statistics about the calendar
    """
    if planets is None:
        planets = TRADITIONAL_PLANETS

    if aspects_list is None:
        aspects_list = ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]

    print(f"\nGenerating planetary calendar:")
    print(f"  Period: {start_date} → {end_date}")
    print(f"  Planets: {', '.join(planets)} ({len(planets)} bodies)")
    print(f"  Aspects: {', '.join(aspects_list)}")

    # Generate all planet pairs
    planet_pairs = list(combinations(planets, 2))
    print(f"  Planet pairs: {len(planet_pairs)}")
    print()

    start_time = time.perf_counter()

    # Generate timeline for each pair
    timelines = {}
    all_events = []

    for i, (body1, body2) in enumerate(planet_pairs, 1):
        print(f"  [{i:2d}/{len(planet_pairs)}] {body1:10s} × {body2:10s} ... ", end="", flush=True)

        pair_start = time.perf_counter()

        timeline = generate_aspect_timeline(
            body1=body1,
            body2=body2,
            start_date=start_date,
            end_date=end_date,
            aspects_list=aspects_list,
            detect_retrograde=detect_retrograde,
            timezone=timezone,
        )

        pair_time = time.perf_counter() - pair_start

        timelines[(body1, body2)] = timeline
        all_events.extend(timeline.events)

        print(f"{len(timeline):3d} events ({pair_time*1000:5.1f} ms)")

    # Sort all events chronologically
    all_events.sort(key=lambda e: e.timestamp)

    total_time = time.perf_counter() - start_time

    # Calculate statistics
    stats = {
        'total_pairs': len(planet_pairs),
        'total_events': len(all_events),
        'total_time_ms': total_time * 1000,
        'avg_time_per_pair_ms': (total_time / len(planet_pairs)) * 1000,
        'events_per_day': len(all_events) / ((end_date - start_date).total_seconds() / 86400),
    }

    print(f"\n  ✓ Generated {stats['total_events']} total events in {stats['total_time_ms']:.1f} ms")
    print(f"    Average: {stats['avg_time_per_pair_ms']:.1f} ms per pair")

    return {
        'timelines': timelines,
        'all_events': all_events,
        'stats': stats,
        'start_date': start_date,
        'end_date': end_date,
        'planets': planets,
    }


def print_calendar_summary(calendar):
    """Print summary of generated calendar."""
    print("\n" + "=" * 70)
    print("PLANETARY CALENDAR SUMMARY")
    print("=" * 70)

    stats = calendar['stats']
    all_events = calendar['all_events']

    print(f"\nPeriod: {calendar['start_date']} → {calendar['end_date']}")
    print(f"Planets: {', '.join(calendar['planets'])}")
    print(f"\nTotal events: {stats['total_events']}")
    print(f"Planet pairs: {stats['total_pairs']}")
    print(f"Generation time: {stats['total_time_ms']:.1f} ms")
    print(f"Events per day: {stats['events_per_day']:.1f}")

    # Group by aspect type
    from collections import defaultdict
    by_aspect = defaultdict(int)
    by_planet_pair = defaultdict(int)
    retrograde_count = 0

    for event in all_events:
        by_aspect[event.aspect_name] += 1
        pair_key = f"{event.body1_name}-{event.body2_name}"
        by_planet_pair[pair_key] += 1
        if event.body1_retro or event.body2_retro:
            retrograde_count += 1

    print(f"\nBy aspect type:")
    for aspect in ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]:
        if aspect in by_aspect:
            print(f"  {aspect:12s}: {by_aspect[aspect]:3d}")

    print(f"\nRetrograde events: {retrograde_count} ({retrograde_count/len(all_events)*100:.1f}%)")

    print(f"\nMost active pairs:")
    top_pairs = sorted(by_planet_pair.items(), key=lambda x: x[1], reverse=True)[:5]
    for pair, count in top_pairs:
        print(f"  {pair:20s}: {count:3d} events")


def export_to_pandas(calendar):
    """Export complete calendar to single Pandas DataFrame."""
    try:
        import pandas as pd
    except ImportError:
        print("Pandas not installed - skipping DataFrame export")
        return None

    # Collect all events into single DataFrame
    all_data = []

    for event in calendar['all_events']:
        all_data.append({
            'timestamp': event.timestamp,
            'body1': event.body1_name,
            'body2': event.body2_name,
            'pair': f"{event.body1_name}-{event.body2_name}",
            'aspect': event.aspect_name,
            'aspect_angle': event.aspect_type,
            'orb': event.orb,
            'strength': event.aspect_strength,
            'separation': event.angular_separation,
            'velocity': event.relative_velocity,
            'body1_retro': event.body1_retro,
            'body2_retro': event.body2_retro,
            'retro_intensity': event.retro_intensity,
            'duration_days': event.duration_days,
        })

    df = pd.DataFrame(all_data)
    df.set_index('timestamp', inplace=True)

    return df


def demo_june_2025_lunar_month():
    """Demo: Complete planetary calendar for June 2025 lunar month."""
    print("\n" + "=" * 70)
    print("DEMO: Complete Planetary Calendar for June 2025 Lunar Month")
    print("=" * 70)

    # Find new moon bounds for June 2025
    print("\nFinding lunar month bounds...")
    new_moon_1, new_moon_2 = find_lunar_month_bounds(2025, 6, timezone="UTC")

    print(f"  New Moon 1: {new_moon_1.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"  New Moon 2: {new_moon_2.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    duration = (new_moon_2 - new_moon_1).total_seconds() / 86400
    print(f"  Duration: {duration:.2f} days")

    # Generate complete planetary calendar
    calendar = generate_full_planetary_calendar(
        start_date=new_moon_1,
        end_date=new_moon_2,
        planets=TRADITIONAL_PLANETS,  # 7 planets = 21 pairs
        detect_retrograde=True,
    )

    # Print summary
    print_calendar_summary(calendar)

    # Show first 10 events
    print("\n" + "=" * 70)
    print("FIRST 10 EVENTS")
    print("=" * 70)
    print()

    for i, event in enumerate(calendar['all_events'][:10], 1):
        retro = ""
        if event.body1_retro or event.body2_retro:
            retro_bodies = []
            if event.body1_retro:
                retro_bodies.append(event.body1_name)
            if event.body2_retro:
                retro_bodies.append(event.body2_name)
            retro = f" [RETRO: {', '.join(retro_bodies)}]"

        print(f"{i:2d}. {event.timestamp.strftime('%Y-%m-%d %H:%M')} | "
              f"{event.body1_name:8s} {event.aspect_name:12s} {event.body2_name:8s} | "
              f"Strength: {event.aspect_strength:.3f}{retro}")

    # Export to Pandas
    print("\n" + "=" * 70)
    print("EXPORT TO PANDAS")
    print("=" * 70)

    df = export_to_pandas(calendar)
    if df is not None:
        print(f"\nDataFrame shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst 5 rows:")
        print(df.head()[['body1', 'body2', 'aspect', 'strength', 'body1_retro', 'body2_retro']])

        # Some analysis
        print("\nAspect distribution:")
        print(df['aspect'].value_counts())

        print("\nMost active planet pairs:")
        print(df['pair'].value_counts().head(5))

        print("\nRetrograde analysis:")
        retro_mask = df['body1_retro'] | df['body2_retro']
        print(f"  Total retrograde events: {retro_mask.sum()} / {len(df)} ({retro_mask.sum()/len(df)*100:.1f}%)")

    return calendar, df


def demo_all_planets_comparison():
    """Demo: Compare traditional vs all planets for a shorter period."""
    print("\n" + "=" * 70)
    print("DEMO: Traditional vs All Planets (1 week comparison)")
    print("=" * 70)

    start = datetime(2025, 6, 1, tzinfo=ZoneInfo("UTC"))
    end = datetime(2025, 6, 8, tzinfo=ZoneInfo("UTC"))

    print("\n1. Traditional planets (7 bodies, 21 pairs)")
    cal_trad = generate_full_planetary_calendar(
        start_date=start,
        end_date=end,
        planets=TRADITIONAL_PLANETS,
        detect_retrograde=True,
    )

    print("\n2. All planets including modern (10 bodies, 45 pairs)")
    cal_all = generate_full_planetary_calendar(
        start_date=start,
        end_date=end,
        planets=ALL_PLANETS,
        detect_retrograde=True,
    )

    print("\n" + "=" * 70)
    print("COMPARISON")
    print("=" * 70)
    print(f"\nTraditional: {cal_trad['stats']['total_events']} events in {cal_trad['stats']['total_time_ms']:.1f} ms")
    print(f"All planets: {cal_all['stats']['total_events']} events in {cal_all['stats']['total_time_ms']:.1f} ms")
    print(f"\nSpeedup factor: {cal_all['stats']['total_time_ms'] / cal_trad['stats']['total_time_ms']:.1f}x slower")
    print(f"Additional events: {cal_all['stats']['total_events'] - cal_trad['stats']['total_events']}")


if __name__ == "__main__":
    # Main demo: June 2025 lunar month
    calendar, df = demo_june_2025_lunar_month()

    # Comparison demo
    print("\n" * 2)
    demo_all_planets_comparison()

    print("\n" + "=" * 70)
    print("DEMOS COMPLETE")
    print("=" * 70)
    print("\n✓ Complete planetary calendars generated quickly!")
    print("✓ All aspects between all planets")
    print("✓ ML-ready Pandas DataFrames")
    print("✓ Optimized performance")
