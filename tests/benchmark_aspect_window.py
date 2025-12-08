#!/usr/bin/env python3
"""Detailed benchmark for find_aspect_window() function."""

import time
from datetime import datetime
from zoneinfo import ZoneInfo

from ketu.aspect_windows import find_aspect_window


def benchmark_aspect_window():
    """Benchmark find_aspect_window with different scenarios."""
    print("\n" + "=" * 70)
    print("FIND_ASPECT_WINDOW PERFORMANCE BENCHMARK")
    print("=" * 70)

    # Test date
    test_date = datetime(2024, 1, 15, tzinfo=ZoneInfo("UTC"))

    # Benchmark 1: Fast bodies (Sun-Moon) - no retrograde
    print("\n1. Sun-Moon conjunction (fast bodies, no retrograde)")
    iterations = 100
    start = time.perf_counter()
    for _ in range(iterations):
        window = find_aspect_window(
            body1=0,  # Sun
            body2=1,  # Moon
            aspect=0,  # Conjunction
            around_date=test_date,
            search_days=3.5,
            detect_retrograde=False,
        )
    elapsed = time.perf_counter() - start
    avg_time = elapsed / iterations
    print(f"   Average time: {avg_time*1000:.2f} ms ({iterations} iterations)")

    # Benchmark 2: Same with retrograde detection (even though Moon doesn't retrograde)
    print("\n2. Sun-Moon conjunction (with retrograde detection)")
    start = time.perf_counter()
    for _ in range(iterations):
        window = find_aspect_window(
            body1=0,  # Sun
            body2=1,  # Moon
            aspect=0,  # Conjunction
            around_date=test_date,
            search_days=3.5,
            detect_retrograde=True,
        )
    elapsed = time.perf_counter() - start
    avg_time = elapsed / iterations
    print(f"   Average time: {avg_time*1000:.2f} ms ({iterations} iterations)")

    # Benchmark 3: Slower bodies (Mars-Jupiter)
    print("\n3. Mars-Jupiter square (slower bodies)")
    iterations = 50
    start = time.perf_counter()
    for _ in range(iterations):
        window = find_aspect_window(
            body1=4,  # Mars
            body2=5,  # Jupiter
            aspect=90,  # Square
            around_date=test_date,
            search_days=10,
            detect_retrograde=False,
        )
    elapsed = time.perf_counter() - start
    avg_time = elapsed / iterations
    print(f"   Average time: {avg_time*1000:.2f} ms ({iterations} iterations)")

    # Benchmark 4: Different aspects (BIG_FIVE)
    print("\n4. Sun-Moon BIG_FIVE aspects (5 different aspects)")
    aspects_to_test = [0, 60, 90, 120, 180]
    iterations = 20
    total_calls = iterations * len(aspects_to_test)

    start = time.perf_counter()
    for _ in range(iterations):
        for asp in aspects_to_test:
            window = find_aspect_window(
                body1=0,  # Sun
                body2=1,  # Moon
                aspect=asp,
                around_date=test_date,
                search_days=3.5,
                detect_retrograde=False,
            )
    elapsed = time.perf_counter() - start
    avg_time = elapsed / total_calls
    print(f"   Average time per call: {avg_time*1000:.2f} ms ({total_calls} calls)")
    print(f"   Total time for 5 aspects: {elapsed/iterations*1000:.2f} ms")

    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    benchmark_aspect_window()
