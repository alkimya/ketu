#!/usr/bin/env python3
"""Performance benchmark for lunar calendar generation."""

import time
from datetime import datetime
from zoneinfo import ZoneInfo

from ketu.lunar_calendar import generate_lunar_calendar


def benchmark_lunar_calendar():
    """Benchmark lunar calendar generation."""
    print("\n" + "=" * 70)
    print("LUNAR CALENDAR PERFORMANCE BENCHMARK")
    print("=" * 70)

    # Test configuration
    year = 2024
    month = 1
    timezone = ZoneInfo("UTC")

    # Benchmark 1: BIG_FIVE aspects (default)
    print("\n1. BIG_FIVE aspects (default - 5 aspect types)")
    iterations = 10
    start = time.perf_counter()
    for _ in range(iterations):
        calendar = generate_lunar_calendar(year, month, timezone=timezone)
    elapsed = time.perf_counter() - start
    avg_time = elapsed / iterations
    print(f"   Average time: {avg_time*1000:.1f} ms ({iterations} iterations)")
    print(f"   Found {len(calendar.aspect_windows)} aspects")

    # Benchmark 2: Major phases only (3 aspect types)
    print("\n2. Major phases only (3 aspect types: 0°, 90°, 180°)")
    start = time.perf_counter()
    for _ in range(iterations):
        calendar = generate_lunar_calendar(
            year, month, aspects=[0, 90, 180], timezone=timezone
        )
    elapsed = time.perf_counter() - start
    avg_time = elapsed / iterations
    print(f"   Average time: {avg_time*1000:.1f} ms ({iterations} iterations)")
    print(f"   Found {len(calendar.aspect_windows)} aspects")

    # Benchmark 3: All 7 major aspects
    print("\n3. All 7 major aspects")
    start = time.perf_counter()
    for _ in range(iterations):
        calendar = generate_lunar_calendar(
            year, month, aspects=[0, 30, 60, 90, 120, 150, 180], timezone=timezone
        )
    elapsed = time.perf_counter() - start
    avg_time = elapsed / iterations
    print(f"   Average time: {avg_time*1000:.1f} ms ({iterations} iterations)")
    print(f"   Found {len(calendar.aspect_windows)} aspects")

    # Benchmark 4: Generate calendars for entire year (12 months)
    print("\n4. Generate calendars for entire year (12 months)")
    start = time.perf_counter()
    calendars = []
    for month in range(1, 13):
        cal = generate_lunar_calendar(year, month, timezone=timezone)
        calendars.append(cal)
    elapsed = time.perf_counter() - start
    total_aspects = sum(len(cal.aspect_windows) for cal in calendars)
    print(f"   Total time: {elapsed:.2f} s")
    print(f"   Average per month: {elapsed/12*1000:.1f} ms")
    print(f"   Total aspects found: {total_aspects}")

    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    benchmark_lunar_calendar()
