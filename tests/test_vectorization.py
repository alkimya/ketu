"""Test and benchmark vectorized ephemeris functions."""

import numpy as np
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from ketu.ephemeris.planets import calc_planet_position, calc_planet_position_batch
from ketu.ephemeris.orbital import (
    get_body_position,
    get_body_position_vectorized,
    get_moon_position,
    get_moon_position_vectorized,
)
from ketu.ephemeris.time import utc_to_julian


# Test date
TEST_DATE = datetime(2020, 12, 21, 18, 20, 0, tzinfo=ZoneInfo("UTC"))
TEST_JD = utc_to_julian(TEST_DATE)


def test_vectorized_correctness():
    """Test that vectorized functions produce same results as scalar versions."""
    print("\n" + "=" * 70)
    print("CORRECTNESS TESTS: Vectorized vs Scalar")
    print("=" * 70)

    # Test get_body_position_vectorized for Sun (Earth orbit)
    print("\nTest 1: get_body_position_vectorized (Sun/Earth)")
    jd_array = np.array([TEST_JD, TEST_JD + 1, TEST_JD + 2])

    # Scalar version
    results_scalar = []
    for jd in jd_array:
        results_scalar.append(get_body_position(0, jd))

    # Vectorized version
    results_vec = get_body_position_vectorized(0, jd_array)

    # Compare
    for i, jd in enumerate(jd_array):
        scalar = results_scalar[i]
        vec = [results_vec[0][i], results_vec[1][i], results_vec[2][i],
               results_vec[3][i], results_vec[4][i], results_vec[5][i]]

        max_diff = max(abs(s - v) for s, v in zip(scalar, vec))
        assert max_diff < 1e-10, f"Mismatch at JD {jd}: {max_diff}"

    print("  ✓ Results match (max diff < 1e-10)")

    # Test get_moon_position_vectorized
    print("\nTest 2: get_moon_position_vectorized")

    # Scalar version
    moon_scalar = []
    for jd in jd_array:
        moon_scalar.append(get_moon_position(jd))

    # Vectorized version
    moon_vec = get_moon_position_vectorized(jd_array)

    # Compare
    for i, jd in enumerate(jd_array):
        scalar = moon_scalar[i]
        vec = (moon_vec[0][i], moon_vec[1][i], moon_vec[2][i])

        max_diff = max(abs(s - v) for s, v in zip(scalar, vec))
        assert max_diff < 1e-10, f"Mismatch at JD {jd}: {max_diff}"

    print("  ✓ Results match (max diff < 1e-10)")

    # Test calc_planet_position_batch
    print("\nTest 3: calc_planet_position_batch (Mars)")

    # Scalar version
    mars_scalar = []
    for jd in jd_array:
        mars_scalar.append(calc_planet_position(jd, 4))  # Mars

    # Batch version
    mars_batch = calc_planet_position_batch(jd_array, 4)

    # Compare
    for i, jd in enumerate(jd_array):
        scalar = mars_scalar[i]
        batch = mars_batch[i]

        max_diff = max(abs(s - b) for s, b in zip(scalar, batch))
        assert max_diff < 1e-8, f"Mismatch at JD {jd}: {max_diff}"

    print("  ✓ Results match (max diff < 1e-8)")


def benchmark_vectorized_performance():
    """Benchmark vectorized functions against scalar versions."""
    print("\n" + "=" * 70)
    print("PERFORMANCE BENCHMARKS: Vectorized vs Scalar")
    print("=" * 70)

    # Benchmark 1: Time series of 365 Sun positions
    print("\nBenchmark 1: Sun positions for 365 days")
    jd_array = TEST_JD + np.arange(365)

    # Scalar version
    start = time.perf_counter()
    for jd in jd_array:
        _ = get_body_position(0, jd)
    time_scalar = time.perf_counter() - start

    # Vectorized version
    start = time.perf_counter()
    _ = get_body_position_vectorized(0, jd_array)
    time_vec = time.perf_counter() - start

    speedup = time_scalar / time_vec
    print(f"  Scalar:     {time_scalar*1000:.2f} ms")
    print(f"  Vectorized: {time_vec*1000:.2f} ms")
    print(f"  Speedup:    {speedup:.2f}x")

    # Benchmark 2: Moon positions for 365 days
    print("\nBenchmark 2: Moon positions for 365 days")

    # Scalar version
    start = time.perf_counter()
    for jd in jd_array:
        _ = get_moon_position(jd)
    time_scalar = time.perf_counter() - start

    # Vectorized version
    start = time.perf_counter()
    _ = get_moon_position_vectorized(jd_array)
    time_vec = time.perf_counter() - start

    speedup = time_scalar / time_vec
    print(f"  Scalar:     {time_scalar*1000:.2f} ms")
    print(f"  Vectorized: {time_vec*1000:.2f} ms")
    print(f"  Speedup:    {speedup:.2f}x")

    # Benchmark 3: Mars positions for 365 days (via calc_planet_position)
    print("\nBenchmark 3: Mars positions for 365 days")

    # Scalar version (without cache)
    calc_planet_position.cache_clear()
    start = time.perf_counter()
    for jd in jd_array:
        _ = calc_planet_position(jd, 4)
    time_scalar = time.perf_counter() - start

    # Batch version
    start = time.perf_counter()
    _ = calc_planet_position_batch(jd_array, 4)
    time_vec = time.perf_counter() - start

    speedup = time_scalar / time_vec
    print(f"  Scalar:     {time_scalar*1000:.2f} ms")
    print(f"  Batch:      {time_vec*1000:.2f} ms")
    print(f"  Speedup:    {speedup:.2f}x")

    # Benchmark 4: Multiple planets time series
    print("\nBenchmark 4: All 10 planets for 365 days")

    # Scalar version
    calc_planet_position.cache_clear()
    start = time.perf_counter()
    for planet_id in range(10):
        for jd in jd_array:
            _ = calc_planet_position(jd, planet_id)
    time_scalar = time.perf_counter() - start

    # Batch version
    start = time.perf_counter()
    for planet_id in range(10):
        _ = calc_planet_position_batch(jd_array, planet_id)
    time_batch = time.perf_counter() - start

    speedup = time_scalar / time_batch
    print(f"  Scalar:     {time_scalar:.3f} s")
    print(f"  Batch:      {time_batch:.3f} s")
    print(f"  Speedup:    {speedup:.2f}x")


if __name__ == "__main__":
    print("=" * 70)
    print("VECTORIZATION VALIDATION AND BENCHMARK SUITE")
    print("=" * 70)

    # Run correctness tests
    test_vectorized_correctness()

    # Run performance benchmarks
    benchmark_vectorized_performance()

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED!")
    print("=" * 70)
