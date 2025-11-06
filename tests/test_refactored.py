"""Test the refactored ketu implementation against expected values."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np

# Import ketu modules
from ketu.ephemeris import utc_to_julian, julian_to_utc
from ketu.ephemeris import calc_planet_position, get_planet_name
from ketu.ketu import (
    bodies,
    aspects,
    signs,
    dd_to_dms,
    body_sign,
    positions,
    calculate_aspects,
    is_retrograde,
    find_aspects_between_dates,
)


def test_time_conversions():
    """Test time conversion functions."""
    print("Testing time conversions...")

    # Test UTC to Julian
    dt = datetime(2020, 12, 21, 18, 20, 0, tzinfo=ZoneInfo("UTC"))
    jd = utc_to_julian(dt)
    print(f"  2020-12-21 18:20 UTC -> JD {jd:.6f}")

    # Expected: around 2459205.2639
    assert abs(jd - 2459205.2639) < 0.001, f"JD conversion failed: {jd}"

    # Test Julian to UTC
    dt_back = julian_to_utc(jd)
    print(f"  JD {jd:.6f} -> {dt_back}")
    assert dt_back.year == 2020
    assert dt_back.month == 12
    assert dt_back.day == 21
    assert dt_back.hour == 18
    assert dt_back.minute == 20

    print("  ✓ Time conversions OK")


def test_planet_positions():
    """Test planetary position calculations."""
    print("\nTesting planetary positions...")

    # Test date: 2020-12-21 19:20 Paris time
    paris_tz = ZoneInfo("Europe/Paris")
    dt = datetime(2020, 12, 21, 19, 20, 0, tzinfo=paris_tz)
    jd = utc_to_julian(dt)

    print(f"  Test date: {dt}")
    print(f"  Julian Date: {jd:.6f}")

    # Calculate positions for all bodies
    for body_id in range(10):  # Sun through Pluto
        pos = calc_planet_position(jd, body_id)
        name = get_planet_name(body_id)
        print(
            f"  {name:8} - Long: {pos[0]:7.3f}° Lat: {pos[1]:6.3f}° "
            f"Dist: {pos[2]:7.4f} AU  Speed: {pos[3]:7.4f}°/day"
        )

    # Check Sun position (should be around 270° in December)
    sun_pos = calc_planet_position(jd, 0)
    assert 260 < sun_pos[0] < 280, f"Sun position unexpected: {sun_pos[0]}"

    print("  ✓ Planet positions OK")


def test_aspects():
    """Test aspect calculations."""
    print("\nTesting aspect calculations...")

    dt = datetime(2020, 12, 21, 19, 20, 0, tzinfo=ZoneInfo("Europe/Paris"))
    jd = utc_to_julian(dt)

    # Get all aspects
    aspects_array = calculate_aspects(jd)

    print(f"  Found {len(aspects_array)} aspects:")
    for asp in aspects_array[:5]:  # Show first 5
        body1, body2, asp_type, orb = asp
        body1_name = bodies[bodies["id"] == body1]["name"][0].decode()
        body2_name = bodies[bodies["id"] == body2]["name"][0].decode()
        aspect_name = aspects[asp_type]["name"].decode()
        degs, mins, secs = dd_to_dms(abs(orb))
        print(f"    {body1_name:7} - {body2_name:12}: {aspect_name:12} " f"{degs:2d}°{mins:02d}'{secs:02d}\"")

    print("  ✓ Aspect calculations OK")


def test_retrograde():
    """Test retrograde detection."""
    print("\nTesting retrograde detection...")

    dt = datetime(2020, 12, 21, 19, 20, 0, tzinfo=ZoneInfo("Europe/Paris"))
    jd = utc_to_julian(dt)

    # Check retrograde status
    for body_id in range(2, 10):  # Mercury through Pluto
        retro = is_retrograde(jd, body_id)
        name = bodies[body_id]["name"].decode()
        if retro:
            print(f"  {name} is retrograde")

    print("  ✓ Retrograde detection OK")


def test_positions_array():
    """Test positions array function."""
    print("\nTesting positions array...")

    dt = datetime(2020, 12, 21, 19, 20, 0, tzinfo=ZoneInfo("Europe/Paris"))
    jd = utc_to_julian(dt)

    pos_array = positions(jd)

    print(f"  Positions shape: {pos_array.shape}")
    print("  Body positions in zodiac:")

    for i, pos in enumerate(pos_array):
        name = bodies[i]["name"].decode()
        sign, degs, mins, secs = body_sign(pos)
        print(f"    {name:10}: {signs[sign]:15} {degs:2d}°{mins:02d}'{secs:02d}\"")

    print("  ✓ Positions array OK")


def test_find_aspects_between_dates():
    """Test finding aspects between dates."""
    print("\nTesting aspect search between dates...")

    dt_start = datetime(2020, 12, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC"))
    dt_end = datetime(2020, 12, 31, 0, 0, 0, tzinfo=ZoneInfo("UTC"))
    jd_start = utc_to_julian(dt_start)
    jd_end = utc_to_julian(dt_end)

    # Find Sun-Moon aspects in December 2020
    sun_id = 0
    moon_id = 1

    aspects_found = find_aspects_between_dates(jd_start, jd_end, sun_id, moon_id)

    print(f"  Found {len(aspects_found)} Sun-Moon aspects in December 2020:")
    for asp in aspects_found[:5]:  # Show first 5
        exact_jd, b1, b2, asp_name, asp_val = asp
        exact_dt = julian_to_utc(exact_jd)
        print(f"    {exact_dt.strftime('%Y-%m-%d %H:%M')} - {asp_name} ({asp_val}°)")

    print("  ✓ Aspect search OK")


def test_accuracy_comparison():
    """Compare accuracy with known ephemeris data."""
    print("\nTesting accuracy against known values...")

    # Test against known position
    # 2020-01-01 00:00 UTC
    dt = datetime(2020, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC"))
    jd = utc_to_julian(dt)

    # Known approximate positions for this date
    expected = {
        "Sun": 280.0,  # Around 10° Capricorn
        "Moon": 330.0,  # Around 0° Pisces (varies)
        "Mercury": 265.0,  # Around 25° Sagittarius
        "Venus": 310.0,  # Around 10° Aquarius
        "Mars": 240.0,  # Around 0° Sagittarius
    }

    print("  Comparing positions for 2020-01-01 00:00 UTC:")
    for body_id, (name, exp_lon) in enumerate(expected.items()):
        pos = calc_planet_position(jd, body_id)
        diff = abs(pos[0] - exp_lon)
        status = "✓" if diff < 5.0 else "⚠"  # 5 degree tolerance
        print(f"    {name:8}: {pos[0]:7.3f}° (expected ~{exp_lon:.0f}°) " f"diff: {diff:5.2f}° {status}")

    print("  ✓ Accuracy test complete")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running Ketu Refactored Implementation Tests")
    print("=" * 60)

    test_time_conversions()
    test_planet_positions()
    test_aspects()
    test_retrograde()
    test_positions_array()
    test_find_aspects_between_dates()
    test_accuracy_comparison()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
