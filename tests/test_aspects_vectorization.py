"""Test and benchmark vectorized aspect calculations."""

import numpy as np
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from ketu.aspects import calculate_aspects, calculate_aspects_vectorized, calculate_aspects_batch
from ketu.calculations import positions, distance
from ketu.core import bodies
from ketu.ephemeris.time import utc_to_julian


# Test date
TEST_DATE = datetime(2020, 12, 21, 18, 20, 0, tzinfo=ZoneInfo("UTC"))
TEST_JD = utc_to_julian(TEST_DATE)


def test_aspects_correctness():
    """Test that vectorized aspect functions produce consistent results."""
    print("\n" + "=" * 70)
    print("CORRECTNESS TESTS: Vectorized Aspects")
    print("=" * 70)

    # Test 1: Single date aspects
    print("\nTest 1: calculate_aspects_vectorized vs calculate_aspects")

    # Original version
    aspects_orig = calculate_aspects(TEST_JD)

    # Vectorized version
    aspects_vec = calculate_aspects_vectorized(TEST_JD)

    # Compare results
    assert len(aspects_orig) == len(aspects_vec), f"Different number of aspects: {len(aspects_orig)} vs {len(aspects_vec)}"

    # Sort both by body1, body2, aspect for comparison
    if len(aspects_orig) > 0:
        orig_sorted = np.sort(aspects_orig, order=["body1", "body2", "i_asp"])
        vec_sorted = np.sort(aspects_vec, order=["body1", "body2", "i_asp"])

        # Check all fields match
        for field in ["body1", "body2", "i_asp"]:
            assert np.all(orig_sorted[field] == vec_sorted[field]), f"Mismatch in {field}"

        # Check orb values are close
        orb_diff = np.max(np.abs(orig_sorted["orb"] - vec_sorted["orb"]))
        assert orb_diff < 1e-6, f"Orb difference too large: {orb_diff}"

    print(f"  ✓ {len(aspects_orig)} aspects match perfectly")

    # Test 2: Batch aspects consistency
    print("\nTest 2: calculate_aspects_batch consistency")

    jd_array = np.array([TEST_JD, TEST_JD + 1, TEST_JD + 2])

    # Batch version
    aspects_batch = calculate_aspects_batch(jd_array)

    # Verify that batch returns correct number of dates
    assert len(aspects_batch) == len(jd_array), \
        f"Batch should return {len(jd_array)} results, got {len(aspects_batch)}"

    # Verify each result is a valid structured array
    for i, aspects in enumerate(aspects_batch):
        assert isinstance(aspects, np.ndarray), f"Date {i}: result should be ndarray"
        assert aspects.dtype.names == ('body1', 'body2', 'i_asp', 'orb'), \
            f"Date {i}: invalid dtype"

        # Verify all body IDs are valid (0-13)
        if len(aspects) > 0:
            assert np.all(aspects['body1'] >= 0) and np.all(aspects['body1'] <= 13), \
                f"Date {i}: invalid body1 IDs"
            assert np.all(aspects['body2'] >= 0) and np.all(aspects['body2'] <= 13), \
                f"Date {i}: invalid body2 IDs"
            assert np.all(aspects['i_asp'] >= 0) and np.all(aspects['i_asp'] <= 13), \
                f"Date {i}: invalid aspect IDs"

    print(f"  ✓ All {len(jd_array)} dates have valid structured arrays")
    print(f"  ✓ Found {[len(a) for a in aspects_batch]} aspects for each date")


def benchmark_aspects_performance():
    """Benchmark vectorized aspect calculations."""
    print("\n" + "=" * 70)
    print("PERFORMANCE BENCHMARKS: Vectorized Aspects")
    print("=" * 70)

    # Benchmark 1: Single date aspects
    print("\nBenchmark 1: Single date aspect calculation")

    iterations = 100

    # Original version
    start = time.perf_counter()
    for _ in range(iterations):
        _ = calculate_aspects(TEST_JD)
    time_orig = time.perf_counter() - start

    # Vectorized version
    start = time.perf_counter()
    for _ in range(iterations):
        _ = calculate_aspects_vectorized(TEST_JD)
    time_vec = time.perf_counter() - start

    speedup = time_orig / time_vec
    print(f"  Original:   {time_orig/iterations*1000:.3f} ms per call")
    print(f"  Vectorized: {time_vec/iterations*1000:.3f} ms per call")
    print(f"  Speedup:    {speedup:.2f}x")

    # Benchmark 2: Batch aspects (30 days)
    print("\nBenchmark 2: Aspect calculation for 30 days")

    jd_array = TEST_JD + np.arange(30)

    # Scalar loop version
    start = time.perf_counter()
    _ = [calculate_aspects(jd) for jd in jd_array]
    time_scalar = time.perf_counter() - start

    # Batch version
    start = time.perf_counter()
    _ = calculate_aspects_batch(jd_array)
    time_batch = time.perf_counter() - start

    speedup = time_scalar / time_batch
    print(f"  Scalar loop: {time_scalar*1000:.2f} ms")
    print(f"  Batch:       {time_batch*1000:.2f} ms")
    print(f"  Speedup:     {speedup:.2f}x")

    # Benchmark 3: Batch aspects (365 days)
    print("\nBenchmark 3: Aspect calculation for 365 days")

    jd_array = TEST_JD + np.arange(365)

    # Scalar loop version
    start = time.perf_counter()
    _ = [calculate_aspects(jd) for jd in jd_array]
    time_scalar = time.perf_counter() - start

    # Batch version
    start = time.perf_counter()
    _ = calculate_aspects_batch(jd_array)
    time_batch = time.perf_counter() - start

    speedup = time_scalar / time_batch
    print(f"  Scalar loop: {time_scalar:.3f} s")
    print(f"  Batch:       {time_batch:.3f} s")
    print(f"  Speedup:     {speedup:.2f}x")


def benchmark_distance_vectorization():
    """Benchmark vectorized distance function."""
    print("\n" + "=" * 70)
    print("PERFORMANCE: Vectorized Distance Function")
    print("=" * 70)

    # Test with arrays
    n = 1000
    pos1 = np.random.uniform(0, 360, n)
    pos2 = np.random.uniform(0, 360, n)

    # Vectorized version (new)
    start = time.perf_counter()
    for _ in range(100):
        _ = distance(pos1, pos2)
    time_vec = (time.perf_counter() - start) / 100

    print(f"\n  Vectorized distance for {n} pairs: {time_vec*1000:.3f} ms")
    print(f"  Per distance: {time_vec/n*1e6:.3f} µs")


if __name__ == "__main__":
    print("=" * 70)
    print("ASPECT VECTORIZATION TEST SUITE")
    print("=" * 70)

    # Run correctness tests
    test_aspects_correctness()

    # Run performance benchmarks
    benchmark_aspects_performance()
    benchmark_distance_vectorization()

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED!")
    print("=" * 70)
