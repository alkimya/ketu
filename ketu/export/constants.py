"""Constants for chart visualization and export.

This module contains all visual constants used for rendering charts,
including symbols, colors, and default configurations.
"""

# Zodiac symbols (Unicode)
ZODIAC_SYMBOLS = {
    0: "♈",  # Aries
    1: "♉",  # Taurus
    2: "♊",  # Gemini
    3: "♋",  # Cancer
    4: "♌",  # Leo
    5: "♍",  # Virgo
    6: "♎",  # Libra
    7: "♏",  # Scorpio
    8: "♐",  # Sagittarius
    9: "♑",  # Capricorn
    10: "♒",  # Aquarius
    11: "♓",  # Pisces
}

# Planet symbols (Unicode)
PLANET_SYMBOLS = {
    0: "☉",  # Sun
    1: "☽",  # Moon
    2: "☿",  # Mercury
    3: "♀",  # Venus
    4: "♂",  # Mars
    5: "♃",  # Jupiter
    6: "♄",  # Saturn
    7: "♅",  # Uranus
    8: "♆",  # Neptune
    9: "♇",  # Pluto
    10: "☊",  # Rahu
    11: "☋",  # Ketu
    12: "⚸",  # Lilith
}

# Aspect colors (distinctive colors for better visibility)
ASPECT_COLORS = {
    0: "#FFD700",  # Conjunction - Gold
    1: "#4169E1",  # Semi-Sextile - Royal Blue
    2: "#4169E1",  # Sextile - Royal Blue (swapped with Trine)
    3: "#FF0000",  # Square - Vivid Red
    4: "#32CD32",  # Trine - Lime Green (swapped with Sextile)
    5: "#FF1493",  # Quincunx - Deep Pink
    6: "#9400D3",  # Opposition - Dark Violet (more distinct)
}

# Aspect symbols (Unicode - using more compatible characters)
ASPECT_SYMBOLS = {
    0: "☌",  # Conjunction
    1: "⚹",  # Semi-Sextile (using sextile symbol)
    2: "*",  # Sextile (asterisk as fallback)
    3: "□",  # Square
    4: "△",  # Trine
    5: "Q",  # Quincunx (letter Q)
    6: "☍",  # Opposition
}

# Planet colors
PLANET_COLORS = {
    0: "#FFA500",  # Sun - Orange
    1: "#C0C0C0",  # Moon - Silver
    2: "#FFD700",  # Mercury - Gold
    3: "#FF69B4",  # Venus - Hot Pink
    4: "#FF0000",  # Mars - Red
    5: "#4169E1",  # Jupiter - Royal Blue
    6: "#8B4513",  # Saturn - Saddle Brown
    7: "#00CED1",  # Uranus - Dark Turquoise
    8: "#4169E1",  # Neptune - Royal Blue
    9: "#8B0000",  # Pluto - Dark Red
    10: "#9370DB",  # Rahu - Medium Purple
    11: "#9370DB",  # Ketu - Medium Purple
    12: "#FF8C00",  # Lilith - Dark Orange
}

# Predefined lists for common use cases
PLANETS_DEFAULT = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]  # All planets
"""Default planet list: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn,
Uranus, Neptune, Pluto, Rahu (North Node), Ketu (South Node), Lilith"""

BIG_FIVE = [0, 60, 90, 120, 180]  # Conjunction, Sextile, Square, Trine, Opposition
"""Big Five aspects: Conjunction (0°), Sextile (60°), Square (90°), Trine (120°), Opposition (180°)"""

__all__ = [
    "ZODIAC_SYMBOLS",
    "PLANET_SYMBOLS",
    "ASPECT_COLORS",
    "ASPECT_SYMBOLS",
    "PLANET_COLORS",
    "PLANETS_DEFAULT",
    "BIG_FIVE",
]
