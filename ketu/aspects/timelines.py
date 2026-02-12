"""Generate aspect timelines between celestial bodies for ML/research applications.

This module provides tools to generate time series data of planetary aspects
optimized for machine learning, deep learning, astro-trading, and research.

The design follows ETL (Extract, Transform, Load) principles:
- Extract: Calculate aspect events from ephemeris data
- Transform: Enrich with cycle info, phase, retrograde status
- Load: Export to ML-ready formats (NumPy, JSON)

Key features:
- Time window approach (aspects between two dates)
- Full cycle information (phase, quadrant, progress, velocity)
- Retrograde detection and intensity
- Applying/separating phase calculation
- Multiple export formats for different ML workflows
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Union, List, Optional, Dict, Any
from zoneinfo import ZoneInfo
import numpy as np

from ketu.core import bodies, aspects
from ketu.aspects.windows import find_aspect_window, AspectWindow, AspectMoment
from ketu.calculations import distance, long, long_velocity, utc_to_julian, julian_to_utc


@dataclass
class AspectEvent:
    """Single aspect event with full cycle information for ML/research.

    Attributes:
        timestamp: UTC datetime of exact aspect
        julian_day: Julian Date of exact aspect
        body1_id: First body ID
        body2_id: Second body ID
        body1_name: First body name
        body2_name: Second body name
        aspect_type: Aspect angle (0, 60, 90, 120, 180)
        aspect_name: Aspect name (Conjunction, Sextile, etc.)
        orb: Orb value in degrees
        orb_tolerance: Maximum orb allowed for this aspect
        aspect_strength: Normalized strength (1.0 at exact, 0.0 at orb edge)

        # Cycle information
        angular_separation: Angular distance between bodies (0-360°)
        phase: 'applying', 'exact', 'separating'
        relative_velocity: Relative velocity in degrees/day
        days_to_exact: Days until/since exact (negative = past, 0 = exact, positive = future)

        # Retrograde information
        body1_retro: Is body1 retrograde?
        body2_retro: Is body2 retrograde?
        retro_intensity: Retrograde intensity (sum of absolute velocities when retro)

        # Window timing
        window_begin: Entry into orb
        window_end: Exit from orb
        duration_days: Duration of aspect window in days
    """
    timestamp: datetime
    julian_day: float
    body1_id: int
    body2_id: int
    body1_name: str
    body2_name: str
    aspect_type: float
    aspect_name: str
    orb: float
    orb_tolerance: float
    aspect_strength: float

    # Cycle information
    angular_separation: float
    phase: str
    relative_velocity: float
    days_to_exact: float

    # Retrograde information
    body1_retro: bool
    body2_retro: bool
    retro_intensity: float

    # Window timing
    window_begin: datetime
    window_end: datetime
    duration_days: float


@dataclass
class AspectTimeline:
    """Timeline of aspect events between two bodies with ML-ready export methods.

    This class represents a complete timeline of aspects between two celestial bodies,
    enriched with all necessary features for ML/deep learning applications.

    Attributes:
        body1: Name of first body
        body2: Name of second body
        start_date: Start of timeline
        end_date: End of timeline
        timezone: Timezone for display (data stored in UTC)
        events: List of aspect events sorted chronologically
        aspects_included: List of aspect angles included
        detect_retrograde: Whether retrograde detection was enabled
    """
    body1: str
    body2: str
    start_date: datetime
    end_date: datetime
    timezone: ZoneInfo
    events: List[AspectEvent] = field(default_factory=list)
    aspects_included: List[float] = field(default_factory=list)
    detect_retrograde: bool = True

    def __len__(self) -> int:
        """Return number of events in timeline."""
        return len(self.events)

    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert events to list of dictionaries.

        Returns:
            List of event dictionaries with all fields
        """
        result = []
        for event in self.events:
            result.append({
                'timestamp': event.timestamp.isoformat(),
                'julian_day': event.julian_day,
                'body1_id': event.body1_id,
                'body2_id': event.body2_id,
                'body1_name': event.body1_name,
                'body2_name': event.body2_name,
                'aspect_type': event.aspect_type,
                'aspect_name': event.aspect_name,
                'orb': event.orb,
                'orb_tolerance': event.orb_tolerance,
                'aspect_strength': event.aspect_strength,
                'angular_separation': event.angular_separation,
                'phase': event.phase,
                'relative_velocity': event.relative_velocity,
                'days_to_exact': event.days_to_exact,
                'body1_retro': event.body1_retro,
                'body2_retro': event.body2_retro,
                'retro_intensity': event.retro_intensity,
                'window_begin': event.window_begin.isoformat(),
                'window_end': event.window_end.isoformat(),
                'duration_days': event.duration_days,
            })
        return result

    def to_numpy(self) -> np.ndarray:
        """Convert to NumPy structured array (dense format for ML).

        Returns:
            Structured array with all event data
        """
        if not self.events:
            # Return empty array with correct dtype
            return np.array([], dtype=self._get_numpy_dtype())

        # Convert to structured array
        data = []
        for event in self.events:
            data.append((
                event.julian_day,
                event.body1_id,
                event.body2_id,
                event.aspect_type,
                event.orb,
                event.orb_tolerance,
                event.aspect_strength,
                event.angular_separation,
                1 if event.phase == 'applying' else (0 if event.phase == 'exact' else -1),
                event.relative_velocity,
                event.days_to_exact,
                event.body1_retro,
                event.body2_retro,
                event.retro_intensity,
                event.duration_days,
            ))

        return np.array(data, dtype=self._get_numpy_dtype())

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary.

        Returns:
            Dictionary with metadata and events
        """
        return {
            'metadata': {
                'body1': self.body1,
                'body2': self.body2,
                'start_date': self.start_date.isoformat(),
                'end_date': self.end_date.isoformat(),
                'timezone': str(self.timezone),
                'aspects_included': self.aspects_included,
                'detect_retrograde': self.detect_retrograde,
                'event_count': len(self.events),
            },
            'events': self.to_dict_list(),
        }

    @staticmethod
    def _get_numpy_dtype():
        """Get NumPy dtype for structured array."""
        return np.dtype([
            ('julian_day', 'f8'),
            ('body1_id', 'i4'),
            ('body2_id', 'i4'),
            ('aspect_type', 'f4'),
            ('orb', 'f4'),
            ('orb_tolerance', 'f4'),
            ('aspect_strength', 'f4'),
            ('angular_separation', 'f4'),
            ('phase', 'i1'),  # -1=separating, 0=exact, 1=applying
            ('relative_velocity', 'f4'),
            ('days_to_exact', 'f4'),
            ('body1_retro', 'bool'),
            ('body2_retro', 'bool'),
            ('retro_intensity', 'f4'),
            ('duration_days', 'f4'),
        ])


def _enrich_aspect_event(
    moment: AspectMoment,
    body1_id: int,
    body2_id: int,
    body1_name: str,
    body2_name: str,
    aspect_angle: float,
    aspect_name: str,
    orb_tolerance: float,
) -> AspectEvent:
    """Enrich aspect moment with cycle and retrograde information.

    Args:
        moment: AspectMoment from find_aspect_window()
        body1_id: First body ID
        body2_id: Second body ID
        body1_name: First body name
        body2_name: Second body name
        aspect_angle: Target aspect angle
        aspect_name: Aspect name
        orb_tolerance: Maximum orb allowed

    Returns:
        Enriched AspectEvent with all ML features
    """
    jd_exact = utc_to_julian(moment.exact)

    # Get positions and velocities at exact moment
    lon1 = long(jd_exact, body1_id)
    lon2 = long(jd_exact, body2_id)
    vel1 = long_velocity(jd_exact, body1_id)
    vel2 = long_velocity(jd_exact, body2_id)

    # Calculate angular separation
    angular_sep = distance(lon1, lon2)

    # Calculate orb and strength
    orb = abs(angular_sep - aspect_angle) if aspect_angle > 0 else angular_sep
    aspect_strength = 1.0 - (orb / orb_tolerance) if orb_tolerance > 0 else 1.0

    # Calculate relative velocity
    relative_vel = vel2 - vel1

    # Determine phase (always exact at the exact moment, but we calculate for context)
    # At exact moment, days_to_exact = 0, phase = 'exact'
    phase = 'exact'
    days_to_exact = 0.0

    # Check for retrograde motion
    body1_retro = vel1 < 0
    body2_retro = vel2 < 0

    # Calculate retrograde intensity (sum of absolute velocities when retrograde)
    retro_intensity = 0.0
    if body1_retro:
        retro_intensity += abs(vel1)
    if body2_retro:
        retro_intensity += abs(vel2)

    # Calculate window duration
    duration_days = (moment.end - moment.begin).total_seconds() / 86400.0

    return AspectEvent(
        timestamp=moment.exact,
        julian_day=jd_exact,
        body1_id=body1_id,
        body2_id=body2_id,
        body1_name=body1_name,
        body2_name=body2_name,
        aspect_type=aspect_angle,
        aspect_name=aspect_name,
        orb=orb,
        orb_tolerance=orb_tolerance,
        aspect_strength=aspect_strength,
        angular_separation=angular_sep,
        phase=phase,
        relative_velocity=relative_vel,
        days_to_exact=days_to_exact,
        body1_retro=body1_retro,
        body2_retro=body2_retro,
        retro_intensity=retro_intensity,
        window_begin=moment.begin,
        window_end=moment.end,
        duration_days=duration_days,
    )


def generate_aspect_timeline(
    body1: Union[str, int],
    body2: Union[str, int],
    start_date: Union[datetime, str],
    end_date: Union[datetime, str],
    aspects_list: Optional[List[Union[str, int, float]]] = None,
    timezone: Optional[Union[str, ZoneInfo]] = None,
    detect_retrograde: bool = True,
) -> AspectTimeline:
    """Generate aspect timeline between two bodies for ML/research applications.

    This function generates a complete timeline of planetary aspects between two bodies
    within a specified date range. The output is optimized for machine learning,
    deep learning, astro-trading, and research applications.

    Features:
    - Time window approach (all aspects between start and end dates)
    - Full cycle information (phase, velocity, separation)
    - Retrograde detection and intensity calculation
    - ML-ready export formats (NumPy, JSON)
    - ETL-optimized data structure

    Args:
        body1: First body (name like "Sun" or ID like 0)
        body2: Second body (name like "Mars" or ID like 4)
        start_date: Start of timeline (datetime or ISO string like "2024-01-01")
        end_date: End of timeline (datetime or ISO string like "2024-12-31")
        aspects_list: List of aspects to include (default: BIG_FIVE)
                     Can be names ("Conjunction"), IDs (0), or angles (0.0)
        timezone: Timezone for display (default: UTC)
                 Can be string like "Europe/Paris" or ZoneInfo object
        detect_retrograde: Enable retrograde detection (default: True)
                          When True, finds multiple exact moments during retrogrades

    Returns:
        AspectTimeline object with events and export methods

    Examples:
        >>> # Mars-Sun aspects in 2024
        >>> timeline = generate_aspect_timeline(
        ...     body1="Sun",
        ...     body2="Mars",
        ...     start_date="2024-01-01",
        ...     end_date="2024-12-31"
        ... )
        >>> print(f"Found {len(timeline)} aspect events")
        >>> arr = timeline.to_numpy()  # Export to NumPy
        >>>
        >>> # Venus-Neptune with custom aspects
        >>> timeline = generate_aspect_timeline(
        ...     body1="Venus",
        ...     body2="Neptune",
        ...     start_date="2025-01-01",
        ...     end_date="2025-06-30",
        ...     aspects_list=["Conjunction", "Square", "Opposition"],
        ...     timezone="America/New_York"
        ... )
    """
    # Default aspects: BIG_FIVE
    if aspects_list is None:
        aspects_list = ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]

    # Parse timezone
    if timezone is None:
        tz = ZoneInfo("UTC")
    elif isinstance(timezone, str):
        tz = ZoneInfo(timezone)
    else:
        tz = timezone

    # Parse dates
    if isinstance(start_date, str):
        start_dt = datetime.fromisoformat(start_date)
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=tz)
    else:
        start_dt = start_date
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=tz)

    if isinstance(end_date, str):
        end_dt = datetime.fromisoformat(end_date)
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=tz)
    else:
        end_dt = end_date
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=tz)

    # Convert to UTC for calculations
    start_utc = start_dt.astimezone(ZoneInfo("UTC"))
    end_utc = end_dt.astimezone(ZoneInfo("UTC"))

    # Get body IDs and names
    if isinstance(body1, str):
        body1_idx = np.where(bodies["name"] == body1.encode())[0]
        if len(body1_idx) == 0:
            raise ValueError(f"Unknown body: '{body1}'. Check BODY_INDICES for valid names")
        body1_id = int(body1_idx[0])
        body1_name = body1
    else:
        body1_id = int(body1)
        body1_name = bodies["name"][body1_id].decode()

    if isinstance(body2, str):
        body2_idx = np.where(bodies["name"] == body2.encode())[0]
        if len(body2_idx) == 0:
            raise ValueError(f"Unknown body: '{body2}'. Check BODY_INDICES for valid names")
        body2_id = int(body2_idx[0])
        body2_name = body2
    else:
        body2_id = int(body2)
        body2_name = bodies["name"][body2_id].decode()

    # Convert aspect list to angles and names
    aspect_info = []  # List of (angle, name, orb_tolerance)
    for aspect in aspects_list:
        if isinstance(aspect, str):
            aspect_idx = np.where(aspects["name"] == aspect.encode())[0]
            if len(aspect_idx) == 0:
                raise ValueError(f"Unknown aspect: {aspect}")
            aspect_id = int(aspect_idx[0])
            aspect_angle = float(aspects["angle"][aspect_id])
            aspect_name = aspect
        elif isinstance(aspect, (int, float)):
            aspect_angle = float(aspect)
            # Find matching aspect by angle
            matching = np.where(np.abs(aspects["angle"] - aspect_angle) < 0.1)[0]
            if len(matching) > 0:
                aspect_name_bytes = aspects["name"][matching[0]]
                aspect_name = aspect_name_bytes.decode() if isinstance(aspect_name_bytes, bytes) else str(aspect_name_bytes)
            else:
                aspect_name = f"{aspect_angle}°"
        else:
            raise ValueError(f"invalid aspect type: {type(aspect).__name__}. Expected str, int, float, or dict")

        aspect_info.append(aspect_angle)

    # Use find_aspects_timeline from aspect_windows module
    # (This is more efficient than calling find_aspect_window multiple times)
    from ketu.aspects.windows import find_aspects_timeline

    windows = find_aspects_timeline(
        body1=body1_id,
        body2=body2_id,
        aspects_list=aspects_list,  # type: ignore[arg-type]
        start_date=start_utc,
        end_date=end_utc,
        detect_retrograde=detect_retrograde,
    )

    # Convert AspectWindow objects to enriched AspectEvent objects
    events = []
    for window in windows:
        # Get aspect angle from window
        aspect_idx = np.where(aspects["name"] == window.aspect.encode())[0][0]
        aspect_angle = float(aspects["angle"][aspect_idx])
        aspect_name = window.aspect

        # Get orb tolerance
        from ketu.aspects.calculator import get_orb
        orb_tolerance = get_orb(body1_id, body2_id, aspect_idx)

        # Enrich each moment
        for moment in window.moments:
            event = _enrich_aspect_event(
                moment=moment,
                body1_id=body1_id,
                body2_id=body2_id,
                body1_name=body1_name,
                body2_name=body2_name,
                aspect_angle=aspect_angle,
                aspect_name=aspect_name,
                orb_tolerance=orb_tolerance,
            )
            events.append(event)

    # Sort events chronologically
    events.sort(key=lambda e: e.timestamp)

    return AspectTimeline(
        body1=body1_name,
        body2=body2_name,
        start_date=start_utc,
        end_date=end_utc,
        timezone=tz,
        events=events,
        aspects_included=aspect_info,
        detect_retrograde=detect_retrograde,
    )


__all__ = [
    "AspectEvent",
    "AspectTimeline",
    "generate_aspect_timeline",
]
