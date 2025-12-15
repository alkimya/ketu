#!/usr/bin/env python3
"""Ketu → Kala Data Pipeline (Standalone Demo)

This demo shows how to generate Ketu data that Kala can consume for
pattern discovery and ML analysis. Run from Ketu directory.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
from itertools import combinations
import time

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: Pandas not available - some features disabled")

from ketu import generate_aspect_timeline


def generate_kala_ready_dataset(
    start_date: datetime,
    end_date: datetime,
    planets=None,
    output_format='pandas',
):
    """Generate aspect data in Kala-ready format.

    Args:
        start_date: Start of analysis period
        end_date: End of analysis period
        planets: List of planet names (default: Traditional 7)
        output_format: 'pandas', 'json', or 'csv'

    Returns:
        DataFrame or dict with all aspect data
    """
    if planets is None:
        planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

    print(f"\nGenerating Kala-ready dataset:")
    print(f"  Period: {start_date.date()} → {end_date.date()}")
    print(f"  Planets: {', '.join(planets)} ({len(planets)} bodies)")

    planet_pairs = list(combinations(planets, 2))
    print(f"  Planet pairs: {len(planet_pairs)}")

    start_time = time.perf_counter()

    # Collect all timelines
    all_events = []

    for i, (body1, body2) in enumerate(planet_pairs, 1):
        print(f"  [{i:2d}/{len(planet_pairs)}] {body1:10s} × {body2:10s} ... ", end="", flush=True)

        timeline = generate_aspect_timeline(
            body1=body1,
            body2=body2,
            start_date=start_date,
            end_date=end_date,
            detect_retrograde=True,
        )

        print(f"{len(timeline):3d} events")

        # Collect events
        for event in timeline.events:
            all_events.append({
                'timestamp': event.timestamp,
                'julian_day': event.julian_day,
                'body1': event.body1_name,
                'body2': event.body2_name,
                'planet_pair': f"{event.body1_name}-{event.body2_name}",
                'aspect_name': event.aspect_name,
                'aspect_angle': event.aspect_type,
                'orb': event.orb,
                'orb_tolerance': event.orb_tolerance,
                'aspect_strength': event.aspect_strength,
                'angular_separation': event.angular_separation,
                'phase': event.phase,
                'relative_velocity': event.relative_velocity,
                'days_to_exact': event.days_to_exact,
                'body1_retro': event.body1_retro,
                'body2_retro': event.body2_retro,
                'retro_intensity': event.retro_intensity,
                'window_begin': event.window_begin,
                'window_end': event.window_end,
                'duration_days': event.duration_days,
            })

    elapsed = time.perf_counter() - start_time

    print(f"\n  ✓ Generated {len(all_events)} total events in {elapsed*1000:.1f} ms")

    if output_format == 'pandas' and PANDAS_AVAILABLE:
        df = pd.DataFrame(all_events)
        df.set_index('timestamp', inplace=True)
        df = df.sort_index()

        # Add temporal features for Kala
        df['day_of_week'] = df.index.dayofweek
        df['day_of_month'] = df.index.day
        df['month'] = df.index.month
        df['day_of_year'] = df.index.dayofyear
        df['is_weekend'] = df['day_of_week'].isin([5, 6])

        # Add aspect quality
        harmonious = ['Conjunction', 'Sextile', 'Trine']
        challenging = ['Square', 'Opposition']
        df['aspect_quality'] = df['aspect_name'].apply(
            lambda x: 'harmonious' if x in harmonious else (
                'challenging' if x in challenging else 'neutral'
            )
        )

        # Add retrograde flags
        df['any_retrograde'] = df['body1_retro'] | df['body2_retro']
        df['both_retrograde'] = df['body1_retro'] & df['body2_retro']

        return df

    elif output_format == 'json':
        return {
            'metadata': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'planets': planets,
                'event_count': len(all_events),
                'generated_at': datetime.now().isoformat(),
            },
            'events': all_events,
        }

    else:
        return all_events


def discover_patterns(df):
    """Discover patterns in aspect data for Kala."""
    print("\n" + "=" * 70)
    print("PATTERN DISCOVERY")
    print("=" * 70)

    # 1. Aspect clusters
    print("\n1. ASPECT CLUSTERS")
    print("   Finding periods with multiple simultaneous aspects...")

    # Group by 24-hour windows
    df_sorted = df.sort_index()
    clusters = []

    i = 0
    while i < len(df_sorted):
        cluster_start = df_sorted.index[i]
        cluster_end = cluster_start + pd.Timedelta(hours=24)

        # Find all in window
        mask = (df_sorted.index >= cluster_start) & (df_sorted.index <= cluster_end)
        cluster_df = df_sorted[mask]

        if len(cluster_df) >= 3:  # Min 3 aspects
            clusters.append({
                'start': cluster_start,
                'count': len(cluster_df),
                'strength': cluster_df['aspect_strength'].mean(),
                'has_retro': cluster_df['any_retrograde'].any(),
            })
            i = df_sorted.index.get_loc(cluster_df.index[-1]) + 1
        else:
            i += 1

    print(f"   Found {len(clusters)} clusters (3+ aspects within 24h)")

    if len(clusters) > 0:
        # Top 3 clusters
        clusters_sorted = sorted(clusters, key=lambda x: x['strength'], reverse=True)
        print("\n   Top 3 strongest clusters:")
        for j, c in enumerate(clusters_sorted[:3], 1):
            print(f"   {j}. {c['start'].strftime('%Y-%m-%d')}: "
                  f"{c['count']} aspects, strength={c['strength']:.3f}")

    # 2. Retrograde patterns
    print("\n2. RETROGRADE PATTERNS")
    retro_events = df[df['any_retrograde']]
    print(f"   Retrograde aspects: {len(retro_events)} ({len(retro_events)/len(df)*100:.1f}%)")

    if len(retro_events) > 0:
        retro_by_pair = retro_events.groupby('planet_pair').size().sort_values(ascending=False)
        print(f"\n   Most retrograde-affected pairs:")
        for pair, count in retro_by_pair.head(3).items():
            print(f"     {pair}: {count} events")

    # 3. Aspect distribution
    print("\n3. ASPECT TYPE DISTRIBUTION")
    aspect_dist = df['aspect_name'].value_counts()
    for aspect, count in aspect_dist.items():
        print(f"   {aspect:12s}: {count:3d} ({count/len(df)*100:.1f}%)")

    # 4. Quality analysis
    print("\n4. ASPECT QUALITY")
    quality_dist = df['aspect_quality'].value_counts()
    for quality, count in quality_dist.items():
        print(f"   {quality.capitalize():12s}: {count:3d} ({count/len(df)*100:.1f}%)")

    # 5. Temporal patterns
    print("\n5. TEMPORAL PATTERNS")
    if 'day_of_week' in df.columns:
        dow_dist = df.groupby('day_of_week').size()
        weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        print("   Aspects by day of week:")
        for dow, count in dow_dist.items():
            print(f"     {weekdays[dow]}: {count:3d}")

    return clusters


def export_for_kala(df, filename='kala_aspect_data.csv'):
    """Export dataset for Kala consumption."""
    print("\n" + "=" * 70)
    print("EXPORT FOR KALA")
    print("=" * 70)

    # CSV export
    csv_file = f"/tmp/{filename}"
    df.to_csv(csv_file)
    print(f"\n✓ Exported to: {csv_file}")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {len(df.columns)}")

    # JSON export (convert numpy types to Python native types)
    json_file = f"/tmp/{filename.replace('.csv', '.json')}"
    df_json = df.reset_index()
    # Convert all numpy scalars to Python native types for JSON serialization
    for col in df_json.columns:
        if df_json[col].dtype in ['float64', 'int64', 'object']:
            df_json[col] = df_json[col].apply(
                lambda x: x.item() if hasattr(x, 'item') else x
            )
    df_json.to_json(json_file, orient='records', date_format='iso', indent=2)
    print(f"\n✓ Exported to: {json_file}")

    print("\nKala can now:")
    print("  1. Load this data with pd.read_csv() or pd.read_json()")
    print("  2. Correlate with price/market data")
    print("  3. Train ML models on patterns")
    print("  4. Backtest trading strategies")

    return csv_file, json_file


def main():
    """Main demo."""
    print("=" * 70)
    print("KETU → KALA DATA PIPELINE")
    print("Generate ML-Ready Aspect Data")
    print("=" * 70)

    # Demo: June 2025 lunar month
    start = datetime(2025, 6, 25, 10, 42, tzinfo=ZoneInfo("UTC"))
    end = datetime(2025, 7, 24, 19, 44, tzinfo=ZoneInfo("UTC"))

    # Generate dataset
    df = generate_kala_ready_dataset(
        start_date=start,
        end_date=end,
        planets=["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"],
        output_format='pandas',
    )

    if df is not None:
        print("\n" + "=" * 70)
        print("DATASET SUMMARY")
        print("=" * 70)
        print(f"\nShape: {df.shape}")
        print(f"Period: {df.index[0].date()} → {df.index[-1].date()}")
        print(f"\nColumns: {list(df.columns)}")

        print("\nFirst 5 events:")
        print(df[['body1', 'body2', 'aspect_name', 'aspect_strength', 'any_retrograde']].head())

        # Discover patterns
        clusters = discover_patterns(df)

        # Export
        if PANDAS_AVAILABLE:
            csv_file, json_file = export_for_kala(df)

            print("\n" + "=" * 70)
            print("PIPELINE COMPLETE!")
            print("=" * 70)
            print("\n✓ Ketu ephemeris calculations: DONE")
            print("✓ ML features enrichment: DONE")
            print("✓ Pattern discovery: DONE")
            print("✓ Export for Kala: DONE")
            print("\nNext: Load this data in Kala for correlation analysis!")

    else:
        print("\nPandas not available - install with: pip install pandas")


if __name__ == "__main__":
    main()
