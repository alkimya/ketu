#!/usr/bin/env python3
"""Test direct calculation of new moons using positions."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import time

from ketu.calculations import long, vlong, utc_to_julian, julian_to_utc, distance
from ketu.aspects import find_aspect_window


def estimate_next_new_moon(jd: float) -> float:
    """Estimate next new moon from current Julian Date using actual velocities.

    Args:
        jd: Current Julian Date

    Returns:
        Estimated Julian Date of next new moon
    """
    # Get current Sun and Moon positions and velocities
    sun_pos = long(jd, 0)  # Sun
    moon_pos = long(jd, 1)  # Moon
    sun_vel = vlong(jd, 0)  # Sun velocity (degrees/day)
    moon_vel = vlong(jd, 1)  # Moon velocity (degrees/day)

    # Calculate signed angular distance (Moon - Sun)
    # Normalize to -180 to +180 range
    diff = (moon_pos - sun_pos) % 360
    if diff > 180:
        diff -= 360

    # If diff < 0, Moon is behind Sun and needs to catch up
    # If diff > 0, Moon is ahead and needs to complete the cycle

    # Relative velocity (how fast Moon catches up)
    relative_vel = moon_vel - sun_vel  # Typically ~12.2 deg/day

    # Calculate degrees until next conjunction
    if diff < 0:
        # Moon is behind Sun, catch up distance
        degrees_to_go = -diff
    else:
        # Moon is ahead, complete the cycle
        degrees_to_go = 360 - diff

    # Estimate days until conjunction
    if abs(relative_vel) > 0.1:  # Avoid division by zero
        days_to_conjunction = degrees_to_go / relative_vel
    else:
        # Fallback to average cycle
        days_to_conjunction = 29.53

    return jd + days_to_conjunction


def test_direct_calculation():
    """Test direct calculation vs search-based approach."""
    print("\n" + "=" * 70)
    print("TEST: Direct New Moon Calculation")
    print("=" * 70)

    test_date = datetime(2024, 1, 15, tzinfo=ZoneInfo("UTC"))
    jd_center = utc_to_julian(test_date)

    # Method 1: Search-based (current approach)
    print("\n1. Search-based approach (current)")
    start = time.perf_counter()
    window = find_aspect_window(
        body1=0, body2=1, aspect=0,
        around_date=test_date,
        search_days=17,
        detect_retrograde=False
    )
    time_search = time.perf_counter() - start
    found_jd = utc_to_julian(window.moments[0].exact) if window.moments else None
    print(f"   Time: {time_search*1000:.2f} ms")
    if found_jd:
        print(f"   Found: {julian_to_utc(found_jd).strftime('%Y-%m-%d %H:%M:%S')}")

    # Method 2: Direct calculation + refinement
    print("\n2. Direct calculation approach (new)")
    start = time.perf_counter()

    # Estimate next new moon
    estimated_jd = estimate_next_new_moon(jd_center)

    # Refine using narrow search window around estimate
    estimated_dt = julian_to_utc(estimated_jd)
    window2 = find_aspect_window(
        body1=0, body2=1, aspect=0,
        around_date=estimated_dt,
        search_days=2,  # Very narrow search
        detect_retrograde=False
    )
    time_direct = time.perf_counter() - start
    found_jd2 = utc_to_julian(window2.moments[0].exact) if window2.moments else None
    print(f"   Time: {time_direct*1000:.2f} ms")
    if found_jd2:
        print(f"   Found: {julian_to_utc(found_jd2).strftime('%Y-%m-%d %H:%M:%S')}")

    # Compare
    if found_jd and found_jd2:
        error_seconds = abs((found_jd - found_jd2) * 86400)
        print(f"\n   Error: {error_seconds:.1f} seconds")
        speedup = time_search / time_direct
        print(f"   Speedup: {speedup:.1f}x")

    # Test finding multiple new moons
    print("\n" + "=" * 70)
    print("TEST: Finding 3 New Moons Around January 2024")
    print("=" * 70)

    # Method 1: Current approach (multiple searches)
    print("\n1. Current approach (3 searches with wide windows)")
    start = time.perf_counter()

    search_dates = [
        test_date - timedelta(days=15),
        test_date,
        test_date + timedelta(days=15)
    ]

    new_moons_1 = []
    for date in search_dates:
        w = find_aspect_window(0, 1, 0, date, search_days=17, detect_retrograde=False)
        if w.moments:
            new_moons_1.append(w.moments[0].exact)

    time_current = time.perf_counter() - start
    print(f"   Time: {time_current*1000:.2f} ms")
    print(f"   Found: {len(set(new_moons_1))} unique new moons")

    # Method 2: Direct calculation (sequential)
    print("\n2. Direct approach (calculate positions once)")
    start = time.perf_counter()

    # Start from first estimate
    current_jd = estimate_next_new_moon(jd_center - 30)
    new_moons_2 = []

    for i in range(3):
        # Refine estimate with narrow search
        w = find_aspect_window(
            0, 1, 0,
            julian_to_utc(current_jd),
            search_days=3,  # Narrow search (±3 days)
            detect_retrograde=False
        )
        if w.moments:
            found_dt = w.moments[0].exact
            new_moons_2.append(found_dt)
            print(f"      {i+1}. {found_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            # Calculate next new moon from this one
            current_jd = utc_to_julian(found_dt) + 29.53
        else:
            print(f"      {i+1}. Not found around {julian_to_utc(current_jd).strftime('%Y-%m-%d')}")
            # Try advancing anyway
            current_jd += 29.53

    time_direct = time.perf_counter() - start
    print(f"   Time: {time_direct*1000:.2f} ms")
    print(f"   Found: {len(new_moons_2)} new moons")

    if len(new_moons_2) > 0:
        speedup = time_current / time_direct
        print(f"\n   Speedup: {speedup:.1f}x")
    else:
        print(f"\n   ERROR: Direct method failed to find moons")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    test_direct_calculation()
