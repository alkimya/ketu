#!/usr/bin/env python
"""Benchmark cache performance for body_properties function."""

import time
import numpy as np
from functools import lru_cache, cache

# Import the uncached version
from ketu.ephemeris.planets import body_properties as _body_properties_uncached


# Version 1: No cache (original)
def body_properties_no_cache(jdate: float, body: int) -> np.ndarray:
    return _body_properties_uncached(jdate, body)


# Version 2: LRU cache with maxsize=1024
@lru_cache(maxsize=1024)
def body_properties_lru(jdate: float, body: int) -> np.ndarray:
    return _body_properties_uncached(jdate, body)


# Version 3: Unbounded cache (Python 3.9+)
@cache
def body_properties_cache(jdate: float, body: int) -> np.ndarray:
    return _body_properties_uncached(jdate, body)


def benchmark_function(func, name, jdates, bodies, iterations=3):
    """Benchmark a function with repeated calculations."""
    times = []

    for _ in range(iterations):
        # Clear cache if it exists
        if hasattr(func, 'cache_clear'):
            func.cache_clear()

        start = time.perf_counter()

        # Simulate real usage: calculate positions for multiple bodies and dates
        for jdate in jdates:
            for body in bodies:
                _ = func(jdate, body)

        elapsed = time.perf_counter() - start
        times.append(elapsed)

    avg_time = np.mean(times)
    std_time = np.std(times)

    print(f"{name:25s}: {avg_time*1000:7.2f} ms (±{std_time*1000:5.2f} ms)")

    # Show cache stats if available
    if hasattr(func, 'cache_info'):
        info = func.cache_info()
        print(f"{'':25s}  Cache: {info.hits} hits, {info.misses} misses, hit rate: {info.hits/(info.hits+info.misses)*100:.1f}%")

    return avg_time


def main():
    print("=" * 70)
    print("BENCHMARK: Cache Performance Comparison")
    print("=" * 70)

    # Test data: 10 different dates, all 13 bodies
    base_jdate = 2459000.0
    jdates = [base_jdate + i for i in range(10)]
    bodies = list(range(13))  # 0-12

    total_calls = len(jdates) * len(bodies)
    print(f"\nTest: {len(jdates)} dates × {len(bodies)} bodies = {total_calls} function calls")
    print(f"Repeated 3 times to get average\n")

    print("-" * 70)
    print("Scenario 1: COLD START (no cache reuse)")
    print("-" * 70)

    # For cold start, use different dates each time
    def benchmark_cold(func, name):
        times = []
        for i in range(3):
            if hasattr(func, 'cache_clear'):
                func.cache_clear()

            # Different dates each iteration (no cache benefit)
            jdates_unique = [base_jdate + 100*i + j for j in range(10)]

            start = time.perf_counter()
            for jdate in jdates_unique:
                for body in bodies:
                    _ = func(jdate, body)
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        avg_time = np.mean(times)
        print(f"{name:25s}: {avg_time*1000:7.2f} ms")
        return avg_time

    time_no_cache_cold = benchmark_cold(body_properties_no_cache, "No cache")
    time_lru_cold = benchmark_cold(body_properties_lru, "LRU cache (1024)")
    time_cache_cold = benchmark_cold(body_properties_cache, "Unbounded cache")

    print("\nCold start: All versions similar (no cache benefit)")
    print(f"  LRU vs No cache: {(time_lru_cold/time_no_cache_cold - 1)*100:+.1f}%")
    print(f"  Unbounded vs LRU: {(time_cache_cold/time_lru_cold - 1)*100:+.1f}%")

    print("\n" + "-" * 70)
    print("Scenario 2: HOT PATH (repeated calculations - typical use case)")
    print("-" * 70)

    # Realistic scenario: calculate aspects (requires multiple calls to same date/body)
    def benchmark_hot(func, name):
        times = []
        for _ in range(3):
            if hasattr(func, 'cache_clear'):
                func.cache_clear()

            start = time.perf_counter()

            # Realistic: calculate positions 100 times for same dates (like aspects calculation)
            for _ in range(100):
                for jdate in jdates[:3]:  # 3 dates
                    for body in bodies[:5]:  # 5 bodies
                        _ = func(jdate, body)

            elapsed = time.perf_counter() - start
            times.append(elapsed)

        avg_time = np.mean(times)
        print(f"{name:25s}: {avg_time*1000:7.2f} ms")

        if hasattr(func, 'cache_info'):
            info = func.cache_info()
            total = info.hits + info.misses
            print(f"{'':25s}  Cache: {info.hits} hits, {info.misses} misses, hit rate: {info.hits/total*100:.1f}%")

        return avg_time

    time_no_cache = benchmark_hot(body_properties_no_cache, "No cache")
    time_lru = benchmark_hot(body_properties_lru, "LRU cache (1024)")
    time_cache = benchmark_hot(body_properties_cache, "Unbounded cache")

    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    speedup_lru_vs_no = time_no_cache / time_lru
    speedup_cache_vs_lru = time_lru / time_cache
    speedup_cache_vs_no = time_no_cache / time_cache

    print(f"\nPhase 1 improvement (adding LRU cache):")
    print(f"  Speedup: {speedup_lru_vs_no:.1f}x faster")
    print(f"  Time reduction: {(1 - time_lru/time_no_cache)*100:.1f}%")

    print(f"\nPhase B4 improvement (LRU → unbounded cache):")
    print(f"  Speedup: {speedup_cache_vs_lru:.2f}x faster")
    print(f"  Time reduction: {(1 - time_cache/time_lru)*100:.1f}%")

    print(f"\nOverall (no cache → unbounded cache):")
    print(f"  Speedup: {speedup_cache_vs_no:.1f}x faster")
    print(f"  Time reduction: {(1 - time_cache/time_no_cache)*100:.1f}%")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
