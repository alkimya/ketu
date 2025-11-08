"""Benchmark comparison: new aspect_windows vs old find_aspect_timing."""

import time
from datetime import datetime
from ketu.calculations import find_aspect_timing, utc_to_julian, julian_to_utc
from ketu.aspect_windows import find_aspect_window


def benchmark_old_method():
    """Benchmark old find_aspect_timing method."""
    dt = datetime(2024, 3, 25, 7, 0, 0)
    jd = utc_to_julian(dt)

    start = time.time()
    for _ in range(10):
        jd_begin, jd_exact, jd_end = find_aspect_timing(
            jdate=jd, body1=0, body2=1, aspect_value=180.0
        )
    elapsed = time.time() - start

    # Convert to datetime
    dt_begin = julian_to_utc(jd_begin)
    dt_exact = julian_to_utc(jd_exact)
    dt_end = julian_to_utc(jd_end)

    return elapsed / 10, dt_begin, dt_exact, dt_end


def benchmark_new_method():
    """Benchmark new find_aspect_window method."""
    start = time.time()
    for _ in range(10):
        result = find_aspect_window(
            body1="Sun",
            body2="Moon",
            aspect="Opposition",
            around_date="2024-03-25 07:00:00",
            search_days=2,
        )
    elapsed = time.time() - start

    moment = result.moments[0] if result.moments else None

    if moment:
        return elapsed / 10, moment.begin, moment.exact, moment.end
    return elapsed / 10, None, None, None


def main():
    print("=" * 80)
    print("ASPECT TIMING BENCHMARK: Old vs New Implementation")
    print("=" * 80)
    print()
    print("Test case: Sun-Moon Opposition (Full Moon) on March 25, 2024")
    print("Iterations: 10 times each, averaged")
    print()

    # Run old method
    print("🔄 Running old method (find_aspect_timing)...")
    time_old, begin_old, exact_old, end_old = benchmark_old_method()

    # Run new method
    print("🔄 Running new method (find_aspect_window)...")
    time_new, begin_new, exact_new, end_new = benchmark_new_method()

    # Results
    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()

    print("Old Method (find_aspect_timing):")
    print(f"  Average time:  {time_old * 1000:.2f} ms")
    print(f"  Begin:         {begin_old}")
    print(f"  Exact:         {exact_old}")
    print(f"  End:           {end_old}")
    print()

    print("New Method (find_aspect_window):")
    print(f"  Average time:  {time_new * 1000:.2f} ms")
    print(f"  Begin:         {begin_new}")
    print(f"  Exact:         {exact_new}")
    print(f"  End:           {end_new}")
    print()

    # Performance comparison
    if time_old > time_new:
        speedup = time_old / time_new
        print(f"✅ New method is {speedup:.2f}x FASTER")
    else:
        slowdown = time_new / time_old
        print(f"⚠️  New method is {slowdown:.2f}x SLOWER")

    # Accuracy comparison
    print()
    print("=" * 80)
    print("ACCURACY COMPARISON")
    print("=" * 80)
    print()

    if exact_old and exact_new:
        diff_exact = abs((exact_old - exact_new).total_seconds())
        diff_begin = abs((begin_old - begin_new).total_seconds())
        diff_end = abs((end_old - end_new).total_seconds())

        print(f"Difference in exact time:  {diff_exact:.2f} seconds")
        print(f"Difference in begin time:  {diff_begin:.2f} seconds")
        print(f"Difference in end time:    {diff_end:.2f} seconds")
        print()

        if diff_exact < 60:  # Less than 1 minute
            print("✅ Accuracy: Excellent agreement (< 1 minute)")
        elif diff_exact < 300:  # Less than 5 minutes
            print("✅ Accuracy: Good agreement (< 5 minutes)")
        else:
            print("⚠️  Accuracy: Significant difference")

    # Additional benchmarks
    print()
    print("=" * 80)
    print("ADDITIONAL BENCHMARKS")
    print("=" * 80)
    print()

    # Benchmark 1: Fast-moving bodies (Sun-Moon)
    print("Test 1: Fast-moving bodies (Sun-Moon Conjunction)")
    start = time.time()
    result = find_aspect_window(
        body1="Sun", body2="Moon", aspect="Conjunction", around_date="2024-04-08", search_days=2
    )
    time_fast = time.time() - start
    print(f"  Time: {time_fast * 1000:.2f} ms")

    # Benchmark 2: Slow-moving bodies (Jupiter-Saturn)
    print()
    print("Test 2: Slow-moving bodies (Jupiter-Saturn Conjunction)")
    start = time.time()
    result = find_aspect_window(
        body1="Jupiter", body2="Saturn", aspect="Conjunction", around_date="2020-12-21", search_days=60
    )
    time_slow = time.time() - start
    print(f"  Time: {time_slow * 1000:.2f} ms")

    # Benchmark 3: Multiple aspects (timeline)
    print()
    print("Test 3: Multiple aspects in one month (Sun-Moon timeline)")
    from ketu.aspect_windows import find_aspects_timeline

    start = time.time()
    timeline = find_aspects_timeline(
        body1="Sun",
        body2="Moon",
        aspects_list=["Conjunction", "Square", "Opposition"],
        start_date="2024-03-01",
        end_date="2024-03-31",
    )
    time_timeline = time.time() - start
    print(f"  Time: {time_timeline * 1000:.2f} ms")
    print(f"  Found {len(timeline)} aspects")

    print()
    print("=" * 80)
    print("BENCHMARK COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
