"""Benchmark script for Ketu ephemeris calculations.

This script measures the performance of various ephemeris calculations to establish
baseline metrics for optimization work. It compares the pyswisseph-based implementation
(ketu.py) with the pure NumPy implementation (ketu_refactored.py).
"""

import sys
import os
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import original implementation
from ketu import ketu

# Import refactored implementation
from ketu import ketu_refactored

# Test date
TEST_DATE = datetime(2020, 12, 21, 18, 20, 0, tzinfo=ZoneInfo("UTC"))
TEST_JD = ketu.utc_to_julian(TEST_DATE)


def benchmark_function(func, *args, iterations=100, **kwargs):
    """Benchmark a function with multiple iterations."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        times.append(end - start)

    times = np.array(times)
    return {
        'mean': np.mean(times),
        'std': np.std(times),
        'min': np.min(times),
        'max': np.max(times),
        'median': np.median(times),
        'result': result
    }


def format_time(seconds):
    """Format time in appropriate units."""
    if seconds < 1e-6:
        return f"{seconds * 1e9:.2f} ns"
    elif seconds < 1e-3:
        return f"{seconds * 1e6:.2f} µs"
    elif seconds < 1:
        return f"{seconds * 1e3:.2f} ms"
    else:
        return f"{seconds:.3f} s"


def print_benchmark_result(name, stats, baseline=None):
    """Print benchmark results in a formatted way."""
    print(f"\n  {name}:")
    print(f"    Mean:   {format_time(stats['mean'])} ± {format_time(stats['std'])}")
    print(f"    Median: {format_time(stats['median'])}")
    print(f"    Min:    {format_time(stats['min'])}")
    print(f"    Max:    {format_time(stats['max'])}")

    if baseline is not None:
        speedup = baseline['mean'] / stats['mean']
        if speedup > 1:
            print(f"    Speedup: {speedup:.2f}x faster")
        else:
            print(f"    Speedup: {1/speedup:.2f}x slower")


def benchmark_single_planet():
    """Benchmark calculation of a single planet position."""
    print("\n" + "=" * 70)
    print("BENCHMARK 1: Single Planet Position")
    print("=" * 70)

    # Original implementation
    print("\nOriginal (pyswisseph):")
    stats_orig = benchmark_function(ketu.body_properties, TEST_JD, 0, iterations=1000)
    print_benchmark_result("Sun position", stats_orig)

    # Refactored implementation
    print("\nRefactored (NumPy):")
    stats_refac = benchmark_function(
        ketu_refactored.calc_planet_position, TEST_JD, 0, iterations=1000
    )
    print_benchmark_result("Sun position", stats_refac, baseline=stats_orig)


def benchmark_all_planets():
    """Benchmark calculation of all planet positions."""
    print("\n" + "=" * 70)
    print("BENCHMARK 2: All Planets Positions")
    print("=" * 70)

    # Original implementation
    print("\nOriginal (pyswisseph):")

    def calc_all_orig(jd):
        return np.array([ketu.body_properties(jd, i) for i in range(10)])

    stats_orig = benchmark_function(calc_all_orig, TEST_JD, iterations=100)
    print_benchmark_result("All 10 planets", stats_orig)

    # Refactored implementation
    print("\nRefactored (NumPy):")
    stats_refac = benchmark_function(ketu_refactored.positions, TEST_JD, iterations=100)
    print_benchmark_result("All 10 planets", stats_refac, baseline=stats_orig)


def benchmark_aspects():
    """Benchmark aspect calculations."""
    print("\n" + "=" * 70)
    print("BENCHMARK 3: Aspect Calculations")
    print("=" * 70)

    # Original implementation
    print("\nOriginal (pyswisseph):")
    stats_orig = benchmark_function(ketu.calculate_aspects, TEST_JD, iterations=100)
    print_benchmark_result("All aspects", stats_orig)

    # Refactored implementation
    print("\nRefactored (NumPy):")
    stats_refac = benchmark_function(
        ketu_refactored.calculate_aspects, TEST_JD, iterations=100
    )
    print_benchmark_result("All aspects", stats_refac, baseline=stats_orig)


def benchmark_retrograde():
    """Benchmark retrograde detection."""
    print("\n" + "=" * 70)
    print("BENCHMARK 4: Retrograde Detection")
    print("=" * 70)

    # Original implementation
    print("\nOriginal (pyswisseph):")
    stats_orig = benchmark_function(ketu.is_retrograde, TEST_JD, 1, iterations=1000)
    print_benchmark_result("Single planet retrograde", stats_orig)

    # Refactored implementation
    print("\nRefactored (NumPy):")
    stats_refac = benchmark_function(
        ketu_refactored.is_retrograde, TEST_JD, 1, iterations=1000
    )
    print_benchmark_result("Single planet retrograde", stats_refac, baseline=stats_orig)


def benchmark_time_series():
    """Benchmark time series generation (365 days of positions)."""
    print("\n" + "=" * 70)
    print("BENCHMARK 5: Time Series (365 days of Sun positions)")
    print("=" * 70)

    # Generate Julian dates for 365 days
    jd_array = np.array([TEST_JD + i for i in range(365)])

    # Original implementation
    print("\nOriginal (pyswisseph):")

    def calc_series_orig(jd_arr):
        return np.array([ketu.body_properties(jd, 0)[0] for jd in jd_arr])

    stats_orig = benchmark_function(calc_series_orig, jd_array, iterations=10)
    print_benchmark_result("365 Sun positions", stats_orig)

    # Refactored implementation (non-vectorized, for fair comparison)
    print("\nRefactored (NumPy, non-vectorized):")

    def calc_series_refac(jd_arr):
        return np.array([ketu_refactored.calc_planet_position(jd, 0)[0] for jd in jd_arr])

    stats_refac = benchmark_function(calc_series_refac, jd_array, iterations=10)
    print_benchmark_result("365 Sun positions", stats_refac, baseline=stats_orig)


def benchmark_find_aspects():
    """Benchmark finding aspects between dates."""
    print("\n" + "=" * 70)
    print("BENCHMARK 6: Find Aspects Between Dates (30 days)")
    print("=" * 70)

    jd_start = TEST_JD
    jd_end = TEST_JD + 30

    # Only refactored version has this function
    print("\nRefactored (NumPy only):")
    stats = benchmark_function(
        ketu_refactored.find_aspects_between_dates,
        jd_start, jd_end, 0, 1,  # Sun-Moon aspects
        iterations=10
    )
    print_benchmark_result("Sun-Moon aspects in 30 days", stats)


def benchmark_memory_usage():
    """Compare memory usage patterns."""
    print("\n" + "=" * 70)
    print("MEMORY USAGE ANALYSIS")
    print("=" * 70)

    import tracemalloc

    # Original implementation
    tracemalloc.start()
    for i in range(100):
        _ = ketu.body_properties(TEST_JD + i, 0)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"\nOriginal (100 planet calculations):")
    print(f"  Current: {current / 1024:.2f} KB")
    print(f"  Peak:    {peak / 1024:.2f} KB")

    # Refactored implementation
    tracemalloc.start()
    for i in range(100):
        _ = ketu_refactored.calc_planet_position(TEST_JD + i, 0)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"\nRefactored (100 planet calculations):")
    print(f"  Current: {current / 1024:.2f} KB")
    print(f"  Peak:    {peak / 1024:.2f} KB")


def benchmark_cache_performance():
    """Benchmark LRU cache performance."""
    print("\n" + "=" * 70)
    print("BENCHMARK 7: Cache Performance")
    print("=" * 70)

    # Refactored implementation uses LRU cache
    # First call (cache miss)
    print("\nRefactored (NumPy with LRU cache):")

    # Clear cache by creating new dates
    test_dates = [TEST_JD + i * 100 for i in range(10)]

    # Cold cache
    cold_times = []
    for jd in test_dates:
        start = time.perf_counter()
        _ = ketu_refactored.calc_planet_position(jd, 0)
        cold_times.append(time.perf_counter() - start)

    print(f"  Cold cache (first call): {format_time(np.mean(cold_times))}")

    # Warm cache (repeat same dates)
    warm_times = []
    for jd in test_dates:
        start = time.perf_counter()
        _ = ketu_refactored.calc_planet_position(jd, 0)
        warm_times.append(time.perf_counter() - start)

    print(f"  Warm cache (repeat call): {format_time(np.mean(warm_times))}")
    print(f"  Cache speedup: {np.mean(cold_times) / np.mean(warm_times):.2f}x")


def run_all_benchmarks():
    """Run all benchmark tests."""
    print("=" * 70)
    print("KETU EPHEMERIS PERFORMANCE BENCHMARK")
    print("=" * 70)
    print(f"\nTest configuration:")
    print(f"  Date: {TEST_DATE}")
    print(f"  Julian Date: {TEST_JD:.6f}")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  NumPy: {np.__version__}")

    try:
        import swisseph
        print(f"  Swiss Ephemeris: {swisseph.__version__}")
    except:
        print(f"  Swiss Ephemeris: Not available")

    # Run benchmarks
    benchmark_single_planet()
    benchmark_all_planets()
    benchmark_aspects()
    benchmark_retrograde()
    benchmark_time_series()
    benchmark_find_aspects()
    benchmark_cache_performance()
    benchmark_memory_usage()

    # Summary
    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)
    print("\nThese baseline metrics can be used to evaluate future optimizations.")
    print("\nPotential optimization areas:")
    print("  1. Vectorize time series calculations")
    print("  2. Vectorize all-planets calculations")
    print("  3. Optimize Kepler equation solver")
    print("  4. Batch aspect calculations")
    print("  5. Use numba JIT compilation for hot loops")
    print("=" * 70)


if __name__ == "__main__":
    run_all_benchmarks()
