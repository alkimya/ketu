"""Zodiacal chart visualization module.

This module provides functions to create beautiful astrological charts
with planetary positions, aspects, and color-coded visual elements.
"""

from datetime import datetime, timedelta
from typing import Union, Optional, List, Tuple
from zoneinfo import ZoneInfo
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Wedge, FancyBboxPatch
from matplotlib.lines import Line2D
import matplotlib.patheffects as path_effects

from .core import bodies, aspects, signs
from .calculations import (
    positions,
    calculate_aspects,
    utc_to_julian,
    is_retrograde,
    long,
    vlong,
    distance,
)


# Zodiac symbols (Unicode)
ZODIAC_SYMBOLS = {
    0: "♈",   # Aries
    1: "♉",   # Taurus
    2: "♊",   # Gemini
    3: "♋",   # Cancer
    4: "♌",   # Leo
    5: "♍",   # Virgo
    6: "♎",   # Libra
    7: "♏",   # Scorpio
    8: "♐",   # Sagittarius
    9: "♑",   # Capricorn
    10: "♒",  # Aquarius
    11: "♓",  # Pisces
}

# Planet symbols (Unicode)
PLANET_SYMBOLS = {
    0: "☉",   # Sun
    1: "☽",   # Moon
    2: "☿",   # Mercury
    3: "♀",   # Venus
    4: "♂",   # Mars
    5: "♃",   # Jupiter
    6: "♄",   # Saturn
    7: "♅",   # Uranus
    8: "♆",   # Neptune
    9: "♇",   # Pluto
    10: "☊",  # North Node
    11: "☋",  # South Node
    12: "⚷",  # Chiron
}

# Aspect colors (distinctive colors for better visibility)
ASPECT_COLORS = {
    0: "#FFD700",   # Conjunction - Gold
    1: "#4169E1",   # Semi-Sextile - Royal Blue
    2: "#4169E1",   # Sextile - Royal Blue (swapped with Trine)
    3: "#FF0000",   # Square - Vivid Red
    4: "#32CD32",   # Trine - Lime Green (swapped with Sextile)
    5: "#FF1493",   # Quincunx - Deep Pink
    6: "#9400D3",   # Opposition - Dark Violet (more distinct)
}

# Aspect symbols (Unicode - using more compatible characters)
ASPECT_SYMBOLS = {
    0: "☌",   # Conjunction
    1: "⚹",   # Semi-Sextile (using sextile symbol)
    2: "*",   # Sextile (asterisk as fallback)
    3: "□",   # Square
    4: "△",   # Trine
    5: "Q",   # Quincunx (letter Q)
    6: "☍",   # Opposition
}

# Planet colors
PLANET_COLORS = {
    0: "#FFA500",   # Sun - Orange
    1: "#C0C0C0",   # Moon - Silver
    2: "#FFD700",   # Mercury - Gold
    3: "#FF69B4",   # Venus - Hot Pink
    4: "#FF0000",   # Mars - Red
    5: "#4169E1",   # Jupiter - Royal Blue
    6: "#8B4513",   # Saturn - Saddle Brown
    7: "#00CED1",   # Uranus - Dark Turquoise
    8: "#4169E1",   # Neptune - Royal Blue
    9: "#8B0000",   # Pluto - Dark Red
    10: "#9370DB",  # North Node - Medium Purple
    11: "#9370DB",  # South Node - Medium Purple
    12: "#FF8C00",  # Chiron - Dark Orange
}


def _is_aspect_applying(
    jd: float,
    body1_id: int,
    body2_id: int,
    aspect_angle: float,
    time_delta: float = 1.0,
) -> bool:
    """Check if aspect is applying (orb decreasing) or separating (orb increasing).

    Args:
        jd: Current Julian Date
        body1_id: First body ID
        body2_id: Second body ID
        aspect_angle: Aspect angle in degrees
        time_delta: Time delta in days to check (default: 1 day)

    Returns:
        True if applying (orb decreasing), False if separating (orb increasing)
    """
    # Calculate current orb
    pos1_now = long(jd, body1_id)
    pos2_now = long(jd, body2_id)
    dist_now = distance(pos1_now, pos2_now)
    orb_now = abs(dist_now - aspect_angle) if aspect_angle > 0 else dist_now

    # Calculate future orb
    pos1_future = long(jd + time_delta, body1_id)
    pos2_future = long(jd + time_delta, body2_id)
    dist_future = distance(pos1_future, pos2_future)
    orb_future = abs(dist_future - aspect_angle) if aspect_angle > 0 else dist_future

    # If orb is decreasing, aspect is applying
    return orb_future < orb_now


def draw_zodiacal_chart(
    date: Union[datetime, str, float],
    filename: str = "chart.svg",
    title: Optional[str] = None,
    timezone: Optional[Union[str, ZoneInfo]] = None,
    show_aspects: bool = True,
    show_legend: bool = True,
    show_aspect_table: bool = True,
    bodies_to_show: Optional[List[int]] = None,
    aspects_to_show: Optional[List[Union[str, int]]] = None,
    figsize: Tuple[float, float] = (16, 11),
    dpi: int = 150,
) -> None:
    """Draw a zodiacal chart with planetary positions and aspects.

    Creates a beautiful astrological chart showing:
    - Zodiac wheel with 12 signs
    - Planet positions marked on the wheel
    - Aspect lines between planets (color-coded by type and intensity by orb)
    - Applying aspects have a slight glow effect
    - Legend with planet symbols, positions, and aspect table

    The chart is oriented with 0° Aries at East (right), matching astronomical
    convention and showing seasonal alignment (Sun at top for summer solstice).

    Args:
        date: Date for the chart (datetime, ISO string, or Julian Date)
        filename: Output filename (supports .svg, .png, .pdf)
        title: Optional chart title (default: date)
        timezone: Timezone for display (str like 'Europe/Paris' or ZoneInfo object)
                  If None and date is string without tz, assumes UTC
                  If date is datetime with tzinfo, uses that timezone
        show_aspects: Draw aspect lines (default: True)
        show_legend: Show legend with planet info (default: True)
        show_aspect_table: Show aspect table (default: True)
        bodies_to_show: List of body IDs to show (default: 0-12, all)
        aspects_to_show: List of aspects to show by name or index
                         (default: ["Conjunction", "Sextile", "Square", "Trine", "Opposition"])
                         Excludes Semi-Sextile and Quincunx by default
        figsize: Figure size in inches (default: 14x10)
        dpi: Resolution for raster formats (default: 150)

    Examples:
        >>> # Summer solstice 2024 in Paris time
        >>> draw_zodiacal_chart("2024-06-20 22:51", "summer_solstice.svg",
        ...                      timezone="Europe/Paris")

        >>> # Chart without aspects
        >>> draw_zodiacal_chart("2024-01-01", "positions_only.svg", show_aspects=False)

        >>> # With datetime object
        >>> from datetime import datetime
        >>> from zoneinfo import ZoneInfo
        >>> dt = datetime(2024, 6, 20, 22, 51, tzinfo=ZoneInfo("Europe/Paris"))
        >>> draw_zodiacal_chart(dt, "chart.svg")
    """
    # Convert date to Julian Date and determine display timezone
    if isinstance(date, str):
        # Parse ISO string
        dt = datetime.fromisoformat(date)

        # If no timezone in string and timezone param provided, add it
        if dt.tzinfo is None and timezone is not None:
            if isinstance(timezone, str):
                tz = ZoneInfo(timezone)
            else:
                tz = timezone
            dt = dt.replace(tzinfo=tz)
        elif dt.tzinfo is None:
            # Assume UTC if no timezone specified
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))

        # Convert to UTC for calculations
        dt_utc = dt.astimezone(ZoneInfo("UTC"))
        jd = utc_to_julian(dt_utc)

        # Format for display in original timezone
        tz_name = dt.tzinfo.tzname(dt) if dt.tzinfo else "UTC"
        date_str = dt.strftime(f"%Y-%m-%d %H:%M {tz_name}")

    elif isinstance(date, datetime):
        # Use timezone from datetime or apply timezone param
        if date.tzinfo is None and timezone is not None:
            if isinstance(timezone, str):
                tz = ZoneInfo(timezone)
            else:
                tz = timezone
            dt = date.replace(tzinfo=tz)
        elif date.tzinfo is None:
            dt = date.replace(tzinfo=ZoneInfo("UTC"))
        else:
            dt = date

        # Convert to UTC for calculations
        dt_utc = dt.astimezone(ZoneInfo("UTC"))
        jd = utc_to_julian(dt_utc)

        # Format for display
        tz_name = dt.tzinfo.tzname(dt) if dt.tzinfo else "UTC"
        date_str = dt.strftime(f"%Y-%m-%d %H:%M {tz_name}")

    else:
        # Julian Date provided - convert to UTC datetime
        jd = float(date)
        from .calculations import julian_to_utc
        dt_utc = julian_to_utc(jd)

        # Apply timezone for display if provided
        if timezone is not None:
            if isinstance(timezone, str):
                tz = ZoneInfo(timezone)
            else:
                tz = timezone
            dt = dt_utc.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz)
            tz_name = dt.tzinfo.tzname(dt)
            date_str = dt.strftime(f"%Y-%m-%d %H:%M {tz_name}")
        else:
            date_str = dt_utc.strftime("%Y-%m-%d %H:%M UTC")

    # Default bodies to show (all)
    if bodies_to_show is None:
        bodies_to_show = list(range(13))  # 0-12

    # Default aspects to show (major aspects, excluding Semi-Sextile and Quincunx)
    if aspects_to_show is None:
        aspects_to_show = ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]

    # Convert aspect names to indices
    aspect_indices = []
    for aspect in aspects_to_show:
        if isinstance(aspect, str):
            idx = np.where(aspects["name"] == aspect.encode())[0]
            if len(idx) > 0:
                aspect_indices.append(int(idx[0]))
        else:
            aspect_indices.append(int(aspect))

    # Create figure
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.set_aspect('equal')
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.3, 1.3)
    ax.axis('off')

    # Title
    if title is None:
        title = f"Zodiacal Chart - {date_str}"
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)

    # Draw zodiac wheel
    _draw_zodiac_wheel(ax)

    # Get planetary positions
    planet_positions = {}
    for body_id in bodies_to_show:
        pos_data = positions(jd)
        if body_id < len(pos_data):
            longitude = pos_data[body_id]
            planet_positions[body_id] = longitude

    # Draw aspects first (so they're behind planets)
    if show_aspects:
        _draw_aspects(ax, jd, planet_positions, aspect_indices)

    # Draw planets
    _draw_planets(ax, jd, planet_positions)

    # Draw legend and aspect table
    if show_legend or show_aspect_table:
        _draw_legend_and_table(
            fig, ax, jd, planet_positions,
            aspect_indices,
            show_legend=show_legend,
            show_aspect_table=show_aspect_table
        )

    # Save figure
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', dpi=dpi)
    plt.close()

    print(f"Chart saved to: {filename}")


def _draw_zodiac_wheel(ax):
    """Draw the zodiac wheel with 12 signs."""
    # Outer circle
    outer_circle = Circle((0, 0), 1.0, fill=False, edgecolor='#2C3E50', linewidth=2)
    ax.add_patch(outer_circle)

    # Inner circle
    inner_circle = Circle((0, 0), 0.85, fill=False, edgecolor='#34495E', linewidth=1)
    ax.add_patch(inner_circle)

    # Zodiac background circle
    background = Circle((0, 0), 1.0, fill=True, facecolor='#F8F9FA', zorder=0)
    ax.add_patch(background)

    # Draw 12 zodiac segments
    colors = ['#FFE5E5', '#E5FFE5'] * 6  # Alternating light colors

    for i in range(12):
        # Each sign is 30 degrees
        # Start at 0° (Aries) on the right (East)
        theta1 = i * 30
        theta2 = (i + 1) * 30

        # Draw wedge
        wedge = Wedge(
            (0, 0), 0.85, theta1, theta2,
            facecolor=colors[i], edgecolor='none',
            zorder=1, alpha=0.3
        )
        ax.add_patch(wedge)

        # Draw division line
        angle_rad = np.radians(theta1)
        x1, y1 = 0.85 * np.cos(angle_rad), 0.85 * np.sin(angle_rad)
        x2, y2 = 1.0 * np.cos(angle_rad), 1.0 * np.sin(angle_rad)
        ax.plot([x1, x2], [y1, y2], color='#BDC3C7', linewidth=0.5, zorder=2)

        # Add zodiac symbol
        mid_angle = theta1 + 15
        angle_rad = np.radians(mid_angle)
        x = 0.925 * np.cos(angle_rad)
        y = 0.925 * np.sin(angle_rad)

        sign_name = signs[i]  # signs is a list
        symbol = ZODIAC_SYMBOLS.get(i, sign_name[:3])

        ax.text(
            x, y, symbol,
            ha='center', va='center',
            fontsize=16, fontweight='bold',
            color='#34495E', zorder=10
        )

    # Add cardinal points labels
    ax.text(1.15, 0, 'E\n0° ♈', ha='center', va='center', fontsize=10, color='#2C3E50', fontweight='bold')
    ax.text(0, 1.15, 'N\n90° ♋', ha='center', va='center', fontsize=10, color='#2C3E50', fontweight='bold')
    ax.text(-1.15, 0, 'W\n180° ♎', ha='center', va='center', fontsize=10, color='#2C3E50', fontweight='bold')
    ax.text(0, -1.15, 'S\n270° ♑', ha='center', va='center', fontsize=10, color='#2C3E50', fontweight='bold')


def _draw_planets(ax, jd: float, planet_positions: dict):
    """Draw planets on the zodiac wheel."""
    for body_id, longitude in planet_positions.items():
        # Convert longitude to angle (0° Aries = 0° on right)
        angle_deg = longitude
        angle_rad = np.radians(angle_deg)

        # Position on wheel (radius 0.925)
        x = 0.75 * np.cos(angle_rad)
        y = 0.75 * np.sin(angle_rad)

        # Get planet info
        body_name_str = bodies["name"][body_id].decode()
        symbol = PLANET_SYMBOLS.get(body_id, body_name_str[0])
        color = PLANET_COLORS.get(body_id, '#000000')

        # Check if retrograde
        retro = is_retrograde(jd, body_id)

        # Draw planet circle (increased size)
        planet_circle = Circle(
            (x, y), 0.055,
            facecolor=color, edgecolor='white',
            linewidth=2, zorder=20, alpha=0.9
        )
        ax.add_patch(planet_circle)

        # Draw symbol (increased font size)
        text = ax.text(
            x, y, symbol,
            ha='center', va='center',
            fontsize=16, fontweight='bold',
            color='white', zorder=21
        )
        text.set_path_effects([
            path_effects.Stroke(linewidth=2, foreground='black'),
            path_effects.Normal()
        ])

        # Add retrograde marker
        if retro:
            ax.text(
                x + 0.06, y + 0.06, 'R',
                ha='center', va='center',
                fontsize=8, fontweight='bold',
                color='red', zorder=22
            )


def _draw_aspects(ax, jd: float, planet_positions: dict, aspect_indices: list):
    """Draw aspect lines between planets."""
    # Calculate all aspects
    aspects_data = calculate_aspects(jd)

    for aspect_data in aspects_data:
        body1_id, body2_id, aspect_idx, orb_value = aspect_data

        # Only draw if aspect is in our filter list
        if aspect_idx not in aspect_indices:
            continue

        # Only draw if both bodies are in our planet list
        if body1_id not in planet_positions or body2_id not in planet_positions:
            continue

        # Get positions
        lon1 = planet_positions[body1_id]
        lon2 = planet_positions[body2_id]

        # Convert to coordinates
        angle1 = np.radians(lon1)
        angle2 = np.radians(lon2)

        x1, y1 = 0.75 * np.cos(angle1), 0.75 * np.sin(angle1)
        x2, y2 = 0.75 * np.cos(angle2), 0.75 * np.sin(angle2)

        # Get aspect info
        aspect_angle = float(aspects["angle"][aspect_idx])
        aspect_color = ASPECT_COLORS.get(aspect_idx, '#888888')

        # Calculate line intensity based on orb (closer = more intense)
        # Typical orbs are 0-10 degrees
        max_orb = 10.0
        intensity = 1.0 - min(abs(orb_value), max_orb) / max_orb
        alpha = 0.3 + 0.5 * intensity  # Alpha from 0.3 to 0.8

        # Check if applying or separating
        is_applying = _is_aspect_applying(jd, body1_id, body2_id, aspect_angle)

        # Line width based on intensity
        linewidth = 1.0 + 1.5 * intensity

        # Draw aspect line
        line = ax.plot(
            [x1, x2], [y1, y2],
            color=aspect_color, alpha=alpha,
            linewidth=linewidth, zorder=5,
            linestyle='-'
        )[0]

        # Add glow effect for applying aspects
        if is_applying:
            # Outer glow
            ax.plot(
                [x1, x2], [y1, y2],
                color=aspect_color, alpha=alpha * 0.3,
                linewidth=linewidth + 3, zorder=4,
                linestyle='-'
            )


def _draw_legend_and_table(fig, ax, jd: float, planet_positions: dict,
                           aspect_indices: list,
                           show_legend: bool = True, show_aspect_table: bool = True):
    """Draw legend with planet info and aspect table."""
    legend_x = 1.05
    legend_y_start = 0.98

    if show_legend:
        # Legend title (reduced spacing after)
        ax.text(
            legend_x, legend_y_start, "Planets",
            transform=ax.transAxes,
            fontsize=12, fontweight='bold',
            ha='left', va='top'
        )

        # Planet list
        y_offset = 1.5  # Reduced spacing from title
        for body_id in sorted(planet_positions.keys()):
            longitude = planet_positions[body_id]
            body_name_str = bodies["name"][body_id].decode()
            symbol = PLANET_SYMBOLS.get(body_id, body_name_str[0])
            color = PLANET_COLORS.get(body_id, '#000000')

            # Calculate sign and degree
            sign_idx = int(longitude / 30)
            degree_in_sign = longitude % 30
            sign_symbol = ZODIAC_SYMBOLS.get(sign_idx, "")
            sign_name = signs[sign_idx]

            retro = " R" if is_retrograde(jd, body_id) else ""

            y_pos = legend_y_start - y_offset * 0.045  # Reduced spacing

            # Planet symbol (colored, larger)
            ax.text(
                legend_x - 0.04, y_pos,
                symbol,
                transform=ax.transAxes,
                fontsize=16, fontweight='bold',
                color=color, ha='center', va='top'
            )

            # Planet name and longitude
            ax.text(
                legend_x, y_pos,
                f"{body_name_str:9} {degree_in_sign:5.1f}°{retro}",
                transform=ax.transAxes,
                fontsize=9, ha='left', va='top',
                family='monospace'
            )

            # Sign symbol (larger)
            ax.text(
                legend_x + 0.17, y_pos,
                sign_symbol,
                transform=ax.transAxes,
                fontsize=14, fontweight='bold',
                color='#34495E', ha='center', va='top'
            )

            # Sign name
            ax.text(
                legend_x + 0.2, y_pos,
                sign_name,
                transform=ax.transAxes,
                fontsize=8, ha='left', va='top',
                family='monospace'
            )

            y_offset += 1

    if show_aspect_table:
        # Aspect table (moved down to avoid overlap)
        table_y_start = legend_y_start - 0.75

        ax.text(
            legend_x, table_y_start, "Aspects",
            transform=ax.transAxes,
            fontsize=12, fontweight='bold',
            ha='left', va='top'
        )

        aspects_data = calculate_aspects(jd)

        # Filter and collect aspects
        filtered_aspects = []
        for aspect_data in aspects_data:
            body1_id, body2_id, aspect_idx, orb_value = aspect_data

            # Filter by aspect index
            if aspect_idx not in aspect_indices:
                continue

            if body1_id not in planet_positions or body2_id not in planet_positions:
                continue

            # Get body speeds to determine which is faster
            speed1 = abs(bodies["speed"][body1_id])
            speed2 = abs(bodies["speed"][body2_id])

            # Faster planet first (transiting planet)
            if speed1 >= speed2:
                fast_id, slow_id = body1_id, body2_id
            else:
                fast_id, slow_id = body2_id, body1_id

            filtered_aspects.append((fast_id, slow_id, aspect_idx, orb_value))

        # Display aspects (all of them, increase figure size if needed)
        y_offset = 1.5
        for fast_id, slow_id, aspect_idx, orb_value in filtered_aspects:
            fast_symbol = PLANET_SYMBOLS.get(fast_id, "?")
            slow_symbol = PLANET_SYMBOLS.get(slow_id, "?")
            aspect_symbol = ASPECT_SYMBOLS.get(aspect_idx, "?")
            aspect_angle = float(aspects["angle"][aspect_idx])
            aspect_color = ASPECT_COLORS.get(aspect_idx, '#888888')

            fast_color = PLANET_COLORS.get(fast_id, '#000000')
            slow_color = PLANET_COLORS.get(slow_id, '#000000')

            # Check if applying (orb decreasing)
            is_applying = _is_aspect_applying(jd, fast_id, slow_id, aspect_angle)
            applying_marker = "→" if is_applying else "←"

            y_pos = table_y_start - y_offset * 0.04

            # Fast planet symbol
            ax.text(
                legend_x, y_pos,
                fast_symbol,
                transform=ax.transAxes,
                fontsize=12, fontweight='bold',
                color=fast_color, ha='left', va='top'
            )

            # Aspect symbol
            ax.text(
                legend_x + 0.03, y_pos,
                aspect_symbol,
                transform=ax.transAxes,
                fontsize=11, fontweight='bold',
                color=aspect_color, ha='left', va='top'
            )

            # Slow planet symbol
            ax.text(
                legend_x + 0.055, y_pos,
                slow_symbol,
                transform=ax.transAxes,
                fontsize=12, fontweight='bold',
                color=slow_color, ha='left', va='top'
            )

            # Applying/separating marker
            ax.text(
                legend_x + 0.085, y_pos,
                applying_marker,
                transform=ax.transAxes,
                fontsize=10, ha='left', va='top',
                color='#555555'
            )

            # Orb
            ax.text(
                legend_x + 0.11, y_pos,
                f"{abs(orb_value):4.1f}°",
                transform=ax.transAxes,
                fontsize=8, ha='left', va='top',
                family='monospace'
            )

            y_offset += 1


__all__ = [
    "draw_zodiacal_chart",
]
