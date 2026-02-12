"""Lunar calendar generation based on aspect windows.

This module provides functions to generate lunar calendars showing all
major aspects during a lunar cycle (from new moon to new moon).
"""

from datetime import datetime, timedelta
from typing import Optional, Union, List, NamedTuple
from zoneinfo import ZoneInfo
import calendar

from .calculations import utc_to_julian, julian_to_utc
from ketu.aspects import find_aspect_window, AspectWindow

# Major aspect angles (conjunction, sextile, square, trine, opposition)
BIG_FIVE = [0, 60, 90, 120, 180]


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
    specified month, then generates a timeline of all Sun-Moon aspects during
    that cycle with their exact windows (begin, exact, end).

    Args:
        year: Year
        month: Month (1-12)
        aspects: List of aspect angles to track (default: BIG_FIVE = [0, 60, 90, 120, 180])
                 Examples: [0, 90, 180] for conjunction/square/opposition only
                          [0, 30, 60, 90, 120, 150, 180] for all major aspects
        timezone: Timezone for datetimes (default: UTC)

    Returns:
        LunarCalendar containing the cycle info and Sun-Moon aspect windows

    Example:
        >>> from ketu.lunar_calendar import generate_lunar_calendar
        >>>
        >>> # Full lunar calendar (all BIG_FIVE aspects)
        >>> calendar = generate_lunar_calendar(2024, 1, timezone="Europe/Paris")
        >>> print(f"Cycle: {calendar.cycle.start} to {calendar.cycle.end}")
        >>> print(f"Aspects found: {len(calendar.aspect_windows)}")
        >>>
        >>> # Only major aspects (New/Full/Quarters)
        >>> calendar = generate_lunar_calendar(2024, 1, aspects=[0, 90, 180])
        >>>
        >>> # All aspects including semi-sextile and quincunx
        >>> calendar = generate_lunar_calendar(2024, 1, aspects=[0, 30, 60, 90, 120, 150, 180])
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

    # Step 3: Generate Sun-Moon aspect windows for the entire cycle
    aspect_windows = []

    # If Conjunction (0°) is in the requested aspects, explicitly add the start and end new moons
    if 0 in aspects:
        try:
            # Add start new moon (conjunction)
            start_window = find_aspect_window(
                body1=0,  # Sun
                body2=1,  # Moon
                aspect=0,  # Conjunction
                around_date=cycle.start,
                search_days=2,
                detect_retrograde=False
            )
            if start_window is not None and len(start_window.moments) > 0:
                aspect_windows.append(start_window)

            # Add end new moon (conjunction)
            end_window = find_aspect_window(
                body1=0,  # Sun
                body2=1,  # Moon
                aspect=0,  # Conjunction
                around_date=cycle.end,
                search_days=2,
                detect_retrograde=False
            )
            if end_window is not None and len(end_window.moments) > 0:
                aspect_windows.append(end_window)
        except Exception:
            pass

    # Scan chronologically through the cycle for all other aspects
    # Start slightly after cycle start since we already handled the start conjunction
    current_date = cycle.start + timedelta(days=2)
    search_end = cycle.end - timedelta(days=2)  # End before cycle end since we handled end conjunction

    # Track found aspects to avoid duplicates - use dict for O(1) lookups
    found_aspects = {}  # aspect_angle -> list of exact times
    if 0 in aspects:
        found_aspects[0] = [cycle.start, cycle.end]

    while current_date < search_end:
        # Try to find each aspect type around current position
        for aspect_angle in aspects:
            if aspect_angle == 0:
                # Skip conjunction, already handled
                continue

            try:
                window = find_aspect_window(
                    body1=0,  # Sun
                    body2=1,  # Moon
                    aspect=aspect_angle,
                    around_date=current_date,
                    search_days=3.5,  # Search ±3.5 days (slightly reduced for speed)
                    detect_retrograde=False  # Moon doesn't retrograde
                )

                if window is not None and len(window.moments) > 0:
                    for moment in window.moments:
                        exact_time = moment.exact

                        # Check if this aspect falls within cycle (exclusive of exact boundaries)
                        if cycle.start < exact_time < cycle.end:
                            # Check if we already found this exact aspect (faster dict lookup)
                            is_duplicate = False
                            if aspect_angle in found_aspects:
                                for found_time in found_aspects[aspect_angle]:
                                    if abs((exact_time - found_time).total_seconds()) < 900:  # 15 min tolerance
                                        is_duplicate = True
                                        break

                            if not is_duplicate:
                                aspect_windows.append(window)
                                if aspect_angle not in found_aspects:
                                    found_aspects[aspect_angle] = []
                                found_aspects[aspect_angle].append(exact_time)

            except Exception:
                # If error finding this aspect, continue with next aspect
                continue

        # Move forward by 3 days (aspects happen roughly every 3-4 days in lunar cycle)
        current_date += timedelta(days=3)

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
