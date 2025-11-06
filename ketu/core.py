"""Core data structures and constants for Ketu astrological calculations.

This module contains the fundamental astronomical and astrological data structures
used throughout the Ketu library, including planetary bodies, aspects, and zodiac signs.
"""

import numpy as np


# Structured array of astronomical bodies with same format as original
# Fields: name, id, orb (degrees), average speed (degrees/day)
# Orb values inspired by Abu Ma'shar (787-886) and Al-Biruni (973-1050)
bodies = np.array(
    [
        ("Sun", 0, 12, 0.986),
        ("Moon", 1, 12, 13.176),
        ("Mercury", 2, 8, 1.383),
        ("Venus", 3, 10, 1.2),
        ("Mars", 4, 8, 0.524),
        ("Jupiter", 5, 10, 0.083),
        ("Saturn", 6, 10, 0.034),
        ("Uranus", 7, 6, 0.012),
        ("Neptune", 8, 6, 0.007),
        ("Pluto", 9, 4, 0.004),
        ("Rahu", 10, 0, -0.013),  # Mean Node
        ("North Node", 11, 0, -0.013),  # True Node
        ("Lilith", 12, 0, 0.113),  # Mean Apogee
    ],
    dtype=[("name", "S12"), ("id", "i4"), ("orb", "f4"), ("speed", "f4")],
)

# Structured array of major aspects (harmonics 1, 2, 3, and 6)
# Fields: name, angle (degrees), coefficient for orb calculation
aspects = np.array(
    [
        ("Conjunction", 0, 1),
        ("Semi-sextile", 30, 1 / 6),
        ("Sextile", 60, 1 / 3),
        ("Square", 90, 1 / 2),
        ("Trine", 120, 2 / 3),
        ("Quincunx", 150, 5 / 6),
        ("Opposition", 180, 1),
    ],
    dtype=[("name", "S12"), ("angle", "f4"), ("coef", "f4")],
)

# Zodiac signs in order
signs = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


__all__ = [
    "bodies",
    "aspects",
    "signs",
]
