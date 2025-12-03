"""Lunar calendar generation based on aspect windows.

This module provides functions to generate lunar calendars showing all
major aspects during a lunar cycle (from new moon to new moon).
"""

from datetime import datetime, timedelta
from typing import Optional, Union, List, NamedTuple
from zoneinfo import ZoneInfo
import calendar

from .calculations import utc_to_julian, julian_to_utc
from .aspect_windows import find_aspect_window, AspectWindow
from .export.constants import BIG_FIVE


class LunarCycle(NamedTuple):
    """Represents a lunar cycle from new moon to new moon.

    Attributes:
        start: Start of cycle (new moon datetime)
        end: End of cycle (next new moon datetime)
        start_jd: Start Julian Date
        end_jd: End Julian Date
        days_in_month: Number of days of this cycle in the target month
    """
    start: datetime
    end: datetime
    start_jd: float
    end_jd: float
    days_in_month: int


class LunarCalendar(NamedTuple):
    """Lunar calendar for a specific month.

    Attributes:
        year: Year
        month: Month (1-12)
        cycle: The selected lunar cycle
        aspect_windows: List of all aspect windows in the cycle
        timezone: Timezone used for datetimes
    """
    year: int
    month: int
    cycle: LunarCycle
    aspect_windows: List[AspectWindow]
    timezone: ZoneInfo


def find_new_moons_around_month(year: int, month: int,
                                 timezone: Optional[Union[str, ZoneInfo]] = None) -> List[datetime]:
    """Find all new moons around a given month (previous, during, and next).

    Searches for Sun-Moon conjunctions (0° aspect) in the period from 15 days
    before the month to 45 days after the start of the month.

    Args:
        year: Year
        month: Month (1-12)
        timezone: Timezone for results (default: UTC)

    Returns:
        List of new moon datetimes, sorted chronologically
    """
    if timezone is None:
        timezone = ZoneInfo("UTC")
    elif isinstance(timezone, str):
        timezone = ZoneInfo(timezone)

    # Search period: 15 days before month start to 45 days after
    # This ensures we catch the previous, current, and next new moon
    month_start = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone)
    search_start = month_start - timedelta(days=15)
    search_end = month_start + timedelta(days=45)

    # Convert to Julian dates
    jd_start = utc_to_julian(search_start)
    jd_end = utc_to_julian(search_end)

    # Find all Sun-Moon conjunctions (new moons)
    # Body 0 = Sun, Body 1 = Moon, Aspect 0 = Conjunction (0°)
    new_moons = []

    # Search for new moons using aspect windows
    # Scan in chunks, centering search around mid-points
    current_date = search_start + timedelta(days=15)  # Start 15 days into search period

    while current_date < search_end - timedelta(days=2):
        try:
            # Search for Sun-Moon conjunction (new moon) around this date
            window = find_aspect_window(
                body1=0,  # Sun
                body2=1,  # Moon
                aspect=0,  # Conjunction (0°)
                around_date=current_date,
                search_days=17,  # Search ±17 days (covers ~1 lunar cycle)
                detect_retrograde=False  # Moon doesn't retrograde
            )

            if window is not None and len(window.moments) > 0:
                # Found a new moon! Use the exact moment of the first occurrence
                first_moment = window.moments[0]
                new_moon_dt = first_moment.exact

                # Convert to target timezone
                if new_moon_dt.tzinfo != timezone:
                    new_moon_dt = new_moon_dt.astimezone(timezone)

                # Only add if not already in list (avoid duplicates)
                if not any(abs((nm - new_moon_dt).total_seconds()) < 3600 for nm in new_moons):
                    new_moons.append(new_moon_dt)

                # Jump to ~29.5 days after this new moon to find the next one
                current_date = first_moment.exact + timedelta(days=29.5)
            else:
                # No new moon found around this date, move forward
                current_date += timedelta(days=15)

        except Exception as e:
            # If error, move forward and continue searching
            current_date += timedelta(days=15)

    return sorted(new_moons)


def select_primary_lunar_cycle(year: int, month: int, new_moons: List[datetime]) -> LunarCycle:
    """Select the lunar cycle with the most days in the target month.

    Args:
        year: Year
        month: Month (1-12)
        new_moons: List of new moon datetimes (at least 2)

    Returns:
        LunarCycle with the most overlap with the target month
    """
    if len(new_moons) < 2:
        raise ValueError(f"Need at least 2 new moons to define cycles, got {len(new_moons)}")

    # Month boundaries
    month_start = datetime(year, month, 1, 0, 0, 0, tzinfo=new_moons[0].tzinfo)
    last_day = calendar.monthrange(year, month)[1]
    month_end = datetime(year, month, last_day, 23, 59, 59, tzinfo=new_moons[0].tzinfo)

    # Evaluate each cycle
    best_cycle = None
    max_days_in_month = 0

    for i in range(len(new_moons) - 1):
        cycle_start = new_moons[i]
        cycle_end = new_moons[i + 1]

        # Calculate overlap with target month
        overlap_start = max(cycle_start, month_start)
        overlap_end = min(cycle_end, month_end)

        if overlap_end > overlap_start:
            days_in_month = (overlap_end - overlap_start).days + 1

            if days_in_month > max_days_in_month:
                max_days_in_month = days_in_month
                best_cycle = LunarCycle(
                    start=cycle_start,
                    end=cycle_end,
                    start_jd=utc_to_julian(cycle_start),
                    end_jd=utc_to_julian(cycle_end),
                    days_in_month=days_in_month
                )

    if best_cycle is None:
        raise ValueError(f"No lunar cycle found overlapping with {year}-{month:02d}")

    return best_cycle


def generate_lunar_calendar(
    year: int,
    month: int,
    aspects: Optional[List] = None,
    timezone: Optional[Union[str, ZoneInfo]] = None
) -> LunarCalendar:
    """Generate a lunar calendar for a given month.

    Finds the lunar cycle (new moon to new moon) with the most days in the
    specified month, then generates a timeline of all major aspects during
    that cycle with their exact windows (begin, exact, end).

    Args:
        year: Year
        month: Month (1-12)
        aspects: List of aspect angles to track (default: BIG_FIVE = [0, 60, 90, 120, 180])
        timezone: Timezone for datetimes (default: UTC)

    Returns:
        LunarCalendar containing the cycle info and all aspect windows

    Example:
        >>> from ketu.lunar_calendar import generate_lunar_calendar
        >>> calendar = generate_lunar_calendar(2024, 1, timezone="Europe/Paris")
        >>> print(f"Cycle: {calendar.cycle.start} to {calendar.cycle.end}")
        >>> print(f"Aspects found: {len(calendar.aspect_windows)}")
        >>> for window in calendar.aspect_windows[:5]:
        ...     print(f"{window.body1_name} {window.aspect_name} {window.body2_name}")
        ...     print(f"  Begins: {window.begin}")
        ...     print(f"  Exact:  {window.exact}")
        ...     print(f"  Ends:   {window.end}")
    """
    # Default aspects: BIG_FIVE
    if aspects is None:
        aspects = BIG_FIVE

    # Default timezone: UTC
    if timezone is None:
        timezone = ZoneInfo("UTC")
    elif isinstance(timezone, str):
        timezone = ZoneInfo(timezone)

    # Step 1: Find all new moons around the target month
    new_moons = find_new_moons_around_month(year, month, timezone)

    if len(new_moons) < 2:
        raise ValueError(
            f"Could not find enough new moons around {year}-{month:02d}. "
            f"Found only {len(new_moons)} new moon(s)."
        )

    # Step 2: Select the primary lunar cycle
    cycle = select_primary_lunar_cycle(year, month, new_moons)

    # Step 3: Generate aspect windows for the entire cycle
    aspect_windows = []

    # For each aspect type
    for aspect_angle in aspects:
        # For all planetary pairs (excluding Rahu and Ketu for major aspects)
        # Use bodies 0-9 (Sun to Pluto) for BIG_FIVE aspects
        bodies_for_aspects = list(range(10))  # 0-9: classical + modern planets

        for i, body1 in enumerate(bodies_for_aspects):
            for body2 in bodies_for_aspects[i+1:]:
                try:
                    # Calculate mid-point of cycle and search range
                    cycle_midpoint = cycle.start + (cycle.end - cycle.start) / 2
                    cycle_duration_days = (cycle.end - cycle.start).days

                    # Find aspect window centered on cycle midpoint
                    window = find_aspect_window(
                        body1=body1,
                        body2=body2,
                        aspect=aspect_angle,
                        around_date=cycle_midpoint,
                        search_days=cycle_duration_days / 2 + 2,  # Search entire cycle + buffer
                        detect_retrograde=True
                    )

                    if window is not None and len(window.moments) > 0:
                        # Check if any moment falls within the cycle
                        for moment in window.moments:
                            if cycle.start <= moment.exact <= cycle.end:
                                aspect_windows.append(window)
                                break  # Only add the window once

                except Exception:
                    # If aspect not found or error, continue
                    continue

    # Sort by exact moment of first occurrence
    aspect_windows.sort(key=lambda w: w.moments[0].exact if w.moments else cycle.start)

    return LunarCalendar(
        year=year,
        month=month,
        cycle=cycle,
        aspect_windows=aspect_windows,
        timezone=timezone
    )


def print_lunar_calendar(calendar: LunarCalendar) -> None:
    """Pretty-print a lunar calendar.

    Args:
        calendar: LunarCalendar to display
    """
    print(f"\n{'='*70}")
    print(f"LUNAR CALENDAR - {calendar.year}-{calendar.month:02d}")
    print(f"{'='*70}\n")

    print(f"Lunar Cycle:")
    print(f"  New Moon (start): {calendar.cycle.start.strftime('%Y-%m-%d %H:%M %Z')}")
    print(f"  New Moon (end):   {calendar.cycle.end.strftime('%Y-%m-%d %H:%M %Z')}")
    print(f"  Days in month:    {calendar.cycle.days_in_month}")
    print(f"  Total duration:   {(calendar.cycle.end - calendar.cycle.start).days} days")
    print(f"\nAspects found: {len(calendar.aspect_windows)}\n")

    print(f"{'Date':12} {'Time':8} {'Event':40} {'Type':12}")
    print(f"{'-'*70}")

    for window in calendar.aspect_windows:
        # Format aspect name
        aspect_desc = f"{window.body1} {window.aspect} {window.body2}"

        # Show all moments (usually 1, but can be 3 with retrogrades)
        for moment in window.moments:
            # Show begin, exact, and end for this moment
            print(f"{moment.begin.strftime('%Y-%m-%d'):12} "
                  f"{moment.begin.strftime('%H:%M'):8} "
                  f"{aspect_desc:40} {'BEGIN':12}")

            print(f"{moment.exact.strftime('%Y-%m-%d'):12} "
                  f"{moment.exact.strftime('%H:%M'):8} "
                  f"{aspect_desc:40} {'EXACT':12}")

            print(f"{moment.end.strftime('%Y-%m-%d'):12} "
                  f"{moment.end.strftime('%H:%M'):8} "
                  f"{aspect_desc:40} {'END':12}")

            print()  # Blank line between moments


__all__ = [
    "LunarCycle",
    "LunarCalendar",
    "find_new_moons_around_month",
    "select_primary_lunar_cycle",
    "generate_lunar_calendar",
    "print_lunar_calendar",
]
