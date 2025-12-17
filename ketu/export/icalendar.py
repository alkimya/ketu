"""iCalendar export utilities for astronomical events.

This module provides functions to export lunations (new/full moons) and
transits to iCalendar (.ics) format for use in calendar applications.

Requires: icalendar library
Install with: pip install icalendar
"""

from datetime import datetime, timedelta
from typing import Optional, List, Union
import warnings

try:
    from icalendar import Calendar, Event, Alarm
    ICALENDAR_AVAILABLE = True
except ImportError:
    ICALENDAR_AVAILABLE = False
    warnings.warn(
        "icalendar library not available. "
        "Install with: pip install icalendar"
    )

from ..aspects import find_aspects_timeline, find_transits_to_position, get_natal_positions


def _check_icalendar():
    """Check if icalendar library is available."""
    if not ICALENDAR_AVAILABLE:
        raise ImportError(
            "icalendar library is required for export functions. "
            "Install with: pip install icalendar"
        )


def export_lunations_to_ical(
    year: int,
    filename: str,
    include_new_moon: bool = True,
    include_full_moon: bool = True,
    include_quarters: bool = False,
    event_duration_mode: str = "exact",  # "exact" or "orb"
    alert_before_minutes: Optional[int] = None,
) -> None:
    """Export lunar cycle events (new/full moons) to iCalendar file.

    Args:
        year: Year to export
        filename: Output .ics filename
        include_new_moon: Include new moons (Sun-Moon conjunction)
        include_full_moon: Include full moons (Sun-Moon opposition)
        include_quarters: Include first/last quarters (Sun-Moon squares)
        event_duration_mode: "exact" for point events, "orb" for duration events
        alert_before_minutes: Add alert N minutes before event (None = no alert)

    Example:
        >>> export_lunations_to_ical(
        ...     year=2024,
        ...     filename="lunar_calendar_2024.ics",
        ...     include_new_moon=True,
        ...     include_full_moon=True,
        ...     alert_before_minutes=60
        ... )
    """
    _check_icalendar()

    # Build aspects list
    aspects_list = []
    if include_new_moon:
        aspects_list.append("Conjunction")
    if include_full_moon:
        aspects_list.append("Opposition")
    if include_quarters:
        aspects_list.append("Square")

    if not aspects_list:
        raise ValueError("At least one lunation type must be included")

    # Find all lunations for the year
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    timeline = find_aspects_timeline(
        body1="Sun",
        body2="Moon",
        aspects_list=aspects_list,
        start_date=start_date,
        end_date=end_date,
    )

    # Create calendar
    cal = Calendar()
    cal.add("prodid", "-//Ketu Astrology//Lunar Calendar//EN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")
    cal.add("x-wr-calname", f"Calendrier Lunaire {year}")
    cal.add("x-wr-timezone", "UTC")
    cal.add("x-wr-caldesc", f"Nouvelles Lunes et Pleines Lunes pour {year}")

    # Add events
    for window in timeline:
        if not window.moments:
            continue

        moment = window.moments[0]

        # Determine event name and emoji
        if window.aspect == "Conjunction":
            event_name = "🌑 Nouvelle Lune"
            description = "Conjonction Soleil-Lune (Nouvelle Lune)"
        elif window.aspect == "Opposition":
            event_name = "🌕 Pleine Lune"
            description = "Opposition Soleil-Lune (Pleine Lune)"
        elif window.aspect == "Square":
            # Determine if first or last quarter based on time
            event_name = "🌓 Premier/Dernier Quartier"
            description = "Carré Soleil-Lune (Quartier)"
        else:
            continue

        # Create event
        event = Event()
        event.add("summary", event_name)
        event.add("description", description)

        # Set timing based on mode
        if event_duration_mode == "exact":
            # Point event at exact moment
            event.add("dtstart", moment.exact)
            event.add("dtend", moment.exact + timedelta(minutes=1))
        else:  # "orb"
            # Duration event spanning the orb
            event.add("dtstart", moment.begin)
            event.add("dtend", moment.end)

        event.add("dtstamp", datetime.now())
        event.add("uid", f"{moment.exact.isoformat()}-{window.aspect}@ketu")
        event.add("location", "")
        event.add("status", "CONFIRMED")
        event.add("transp", "TRANSPARENT")  # Free/busy: transparent

        # Add alert if requested
        if alert_before_minutes is not None:
            alarm = Alarm()
            alarm.add("action", "DISPLAY")
            alarm.add("description", f"Rappel: {event_name}")
            alarm.add("trigger", timedelta(minutes=-alert_before_minutes))
            event.add_component(alarm)

        cal.add_component(event)

    # Write to file
    with open(filename, "wb") as f:
        f.write(cal.to_ical())

    print(f"✓ Exported {len(timeline)} lunation events to {filename}")


def export_transits_to_ical(
    natal_date: Union[datetime, str, float],
    start_date: Union[datetime, str, float],
    end_date: Union[datetime, str, float],
    filename: str,
    transiting_bodies: Optional[List[str]] = None,
    natal_bodies: Optional[List[str]] = None,
    aspects_list: Optional[List[str]] = None,
    event_duration_mode: str = "exact",
    alert_before_minutes: Optional[int] = None,
) -> None:
    """Export planetary transits to iCalendar file.

    Args:
        natal_date: Natal/reference date
        start_date: Start date for transits
        end_date: End date for transits
        filename: Output .ics filename
        transiting_bodies: List of transiting bodies (default: outer planets)
        natal_bodies: List of natal bodies to check (default: Sun, Moon, ASC)
        aspects_list: List of aspects (default: major aspects)
        event_duration_mode: "exact" for point events, "orb" for duration events
        alert_before_minutes: Add alert N minutes before event

    Example:
        >>> export_transits_to_ical(
        ...     natal_date="1990-05-15 14:30",
        ...     start_date="2024-01-01",
        ...     end_date="2024-12-31",
        ...     filename="my_transits_2024.ics",
        ...     transiting_bodies=["Jupiter", "Saturn", "Uranus"],
        ...     alert_before_minutes=1440  # 24 hours before
        ... )
    """
    _check_icalendar()

    # Default transiting bodies (slow planets that matter most)
    if transiting_bodies is None:
        transiting_bodies = ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

    # Default natal bodies to check against
    if natal_bodies is None:
        natal_bodies = ["Sun", "Moon", "Mercury", "Venus", "Mars"]

    # Default aspects
    if aspects_list is None:
        aspects_list = ["Conjunction", "Square", "Trine", "Opposition"]

    # Get natal positions
    natal = get_natal_positions(natal_date, bodies_list=natal_bodies)

    # Create calendar
    cal = Calendar()
    cal.add("prodid", "-//Ketu Astrology//Transits Calendar//EN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")
    cal.add("x-wr-calname", "Transits Planétaires")
    cal.add("x-wr-timezone", "UTC")
    cal.add("x-wr-caldesc", "Transits des planètes lentes sur positions natales")

    event_count = 0

    # Find transits for each transiting body to each natal position
    for trans_body in transiting_bodies:
        for natal_body_name, natal_pos in natal.items():
            # Find transits
            transits = find_transits_to_position(
                transiting_body=trans_body,
                reference_longitude=natal_pos.longitude,
                aspects_list=aspects_list,
                start_date=start_date,
                end_date=end_date,
            )

            for window in transits:
                if not window.moments:
                    continue

                moment = window.moments[0]

                # Create event
                event_name = f"{trans_body} {window.aspect} natal {natal_body_name}"

                # Add symbols for aspects
                aspect_symbols = {
                    "Conjunction": "☌",
                    "Sextile": "⚹",
                    "Square": "□",
                    "Trine": "△",
                    "Opposition": "☍",
                }
                symbol = aspect_symbols.get(window.aspect, "")

                event_name_with_symbol = f"{trans_body} {symbol} natal {natal_body_name}"

                description = (
                    f"Transit: {trans_body} forme un {window.aspect} "
                    f"avec {natal_body_name} natal ({natal_pos.longitude:.2f}°)\n"
                    f"Orbe: {moment.orb_used:.1f}°\n"
                    f"Mouvement: {moment.motion}"
                )

                event = Event()
                event.add("summary", event_name_with_symbol)
                event.add("description", description)

                # Set timing based on mode
                if event_duration_mode == "exact":
                    event.add("dtstart", moment.exact)
                    event.add("dtend", moment.exact + timedelta(hours=1))
                else:  # "orb"
                    event.add("dtstart", moment.begin)
                    event.add("dtend", moment.end)

                event.add("dtstamp", datetime.now())
                event.add(
                    "uid",
                    f"{moment.exact.isoformat()}-{trans_body}-{natal_body_name}-{window.aspect}@ketu"
                )
                event.add("status", "CONFIRMED")
                event.add("transp", "TRANSPARENT")

                # Add alert if requested
                if alert_before_minutes is not None:
                    alarm = Alarm()
                    alarm.add("action", "DISPLAY")
                    alarm.add("description", f"Rappel: {event_name}")
                    alarm.add("trigger", timedelta(minutes=-alert_before_minutes))
                    event.add_component(alarm)

                cal.add_component(event)
                event_count += 1

    # Write to file
    with open(filename, "wb") as f:
        f.write(cal.to_ical())

    print(f"✓ Exported {event_count} transit events to {filename}")


def export_aspects_to_ical(
    body1: str,
    body2: str,
    start_date: Union[datetime, str, float],
    end_date: Union[datetime, str, float],
    filename: str,
    aspects_list: Optional[List[str]] = None,
    event_duration_mode: str = "exact",
    alert_before_minutes: Optional[int] = None,
) -> None:
    """Export aspects between two bodies to iCalendar file.

    Args:
        body1: First body name
        body2: Second body name
        start_date: Start date
        end_date: End date
        filename: Output .ics filename
        aspects_list: List of aspects (default: major aspects)
        event_duration_mode: "exact" for point events, "orb" for duration events
        alert_before_minutes: Add alert N minutes before event

    Example:
        >>> # Export all Venus-Mars aspects in 2024
        >>> export_aspects_to_ical(
        ...     body1="Venus",
        ...     body2="Mars",
        ...     start_date="2024-01-01",
        ...     end_date="2024-12-31",
        ...     filename="venus_mars_2024.ics"
        ... )
    """
    _check_icalendar()

    # Default aspects
    if aspects_list is None:
        aspects_list = ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]

    # Find aspects
    timeline = find_aspects_timeline(
        body1=body1,
        body2=body2,
        aspects_list=aspects_list,
        start_date=start_date,
        end_date=end_date,
    )

    # Create calendar
    cal = Calendar()
    cal.add("prodid", "-//Ketu Astrology//Aspects Calendar//EN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")
    cal.add("x-wr-calname", f"Aspects {body1}-{body2}")
    cal.add("x-wr-timezone", "UTC")

    # Add events
    for window in timeline:
        if not window.moments:
            continue

        moment = window.moments[0]

        # Event name with aspect symbol
        aspect_symbols = {
            "Conjunction": "☌",
            "Sextile": "⚹",
            "Square": "□",
            "Trine": "△",
            "Opposition": "☍",
        }
        symbol = aspect_symbols.get(window.aspect, "")
        event_name = f"{body1} {symbol} {body2} ({window.aspect})"

        description = f"{body1} forme un {window.aspect} avec {body2}"

        event = Event()
        event.add("summary", event_name)
        event.add("description", description)

        # Set timing
        if event_duration_mode == "exact":
            event.add("dtstart", moment.exact)
            event.add("dtend", moment.exact + timedelta(minutes=30))
        else:  # "orb"
            event.add("dtstart", moment.begin)
            event.add("dtend", moment.end)

        event.add("dtstamp", datetime.now())
        event.add("uid", f"{moment.exact.isoformat()}-{body1}-{body2}-{window.aspect}@ketu")
        event.add("status", "CONFIRMED")
        event.add("transp", "TRANSPARENT")

        # Add alert if requested
        if alert_before_minutes is not None:
            alarm = Alarm()
            alarm.add("action", "DISPLAY")
            alarm.add("description", f"Rappel: {event_name}")
            alarm.add("trigger", timedelta(minutes=-alert_before_minutes))
            event.add_component(alarm)

        cal.add_component(event)

    # Write to file
    with open(filename, "wb") as f:
        f.write(cal.to_ical())

    print(f"✓ Exported {len(timeline)} aspect events to {filename}")


__all__ = [
    "export_lunations_to_ical",
    "export_transits_to_ical",
    "export_aspects_to_ical",
]
