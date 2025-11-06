"""Display and CLI functions for Ketu.

This module provides functions to format and print astronomical calculations,
as well as the main command-line interface.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np

from .core import signs, aspects
from .calculations import (
    body_name,
    body_id,
    body_sign,
    positions,
    calculate_aspects,
    is_retrograde,
    dd_to_dms,
    utc_to_julian,
    julian_to_utc,
    find_aspects_between_dates,
)


def print_positions(jdate: float):
    """Function to format and print positions of the bodies for a date"""
    print("\n")
    print("------------- Bodies Positions -------------")
    for index, pos in np.ndenumerate(positions(jdate)):
        sign, degs, mins, secs = body_sign(pos)
        retro = ", R" if is_retrograde(jdate, *index) else ""
        print(f"{body_name(*index):10}: " f"{signs[sign]:15}{degs:>2}º{mins:>2}'{secs:>2}\"{retro}")


def print_aspects(jdate: float):
    """Function to format and print aspects between the bodies for a date"""
    print("\n")
    print("------------- Bodies Aspects -------------")
    for aspect in calculate_aspects(jdate):
        body1, body2, i_asp, orb = aspect
        degs, mins, secs = dd_to_dms(orb)
        print(
            f"{body_name(body1):7} - {body_name(body2):12}: "
            f"{aspects['name'][i_asp].decode():12} "
            f"{degs:>2}º{mins:>2}'{secs:>2}\""
        )


def main():
    """Entry point of the program"""
    try:
        year, month, day = map(int, input("Give a date with ISO format, ex: 2020-12-21\n").split("-"))
        hour, minute = map(int, input("Give a time (hour, minute), with ISO format, ex: 19:20\n").split(":"))
        tzinfo = input("Give the Time Zone, ex: 'Europe/Paris' for France: ") or "Europe/Paris"
        zoneinfo = ZoneInfo(tzinfo)
        dtime = datetime(year, month, day, hour, minute, tzinfo=zoneinfo)
        jday = utc_to_julian(dtime)
        print_positions(jday)
        print_aspects(jday)

        # Demo of new features
        print("\n------------- Aspect Timing Example -------------")
        # Example: Find timing for Sun-Moon conjunction
        sun_id = body_id("Sun")
        moon_id = body_id("Moon")

        aspects_found = find_aspects_between_dates(jday - 15, jday + 15, sun_id, moon_id)
        for asp in aspects_found[:3]:  # Show first 3
            exact_jd, b1, b2, asp_name, asp_val = asp
            exact_dt = julian_to_utc(exact_jd)
            print(f"{body_name(b1)} {asp_name} {body_name(b2)} at {exact_dt}")

    except ValueError as e:
        print(f"Error : {e}")
        print("Please enter a valid date and time with ISO format")


__all__ = [
    "print_positions",
    "print_aspects",
    "main",
]
