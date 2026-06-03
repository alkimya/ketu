"""
Core data structures and constants for Ketu astrological calculations.

This module contains the fundamental astronomical and astrological data structures
used throughout the Ketu library, including planetary bodies, aspects, and zodiac signs.

Notes
-----
Orb values are inspired by medieval Islamic astronomers Abu Ma'shar (787-886)
and Al-Biruni (973-1050), adapted for modern precision calculations.

**Data Structures**

bodies : numpy.ndarray
    Structured array of 14 astronomical bodies with fields:

    - name (str): Body name (e.g., 'Sun', 'Moon', 'Mars').
    - id (int): Body identifier (0-13).
    - orb (float): Default orb in degrees for aspect calculations.
    - speed (float): Average daily motion in degrees/day.

    Body IDs:
    0=Sun, 1=Moon, 2=Mercury, 3=Venus, 4=Mars, 5=Jupiter, 6=Saturn,
    7=Uranus, 8=Neptune, 9=Pluto, 10=Rahu (Mean North Node),
    11=Ketu (Mean South Node), 12=Lilith (Mean Apogee/Black Moon),
    13=Chiron (Centaur).

aspects : numpy.ndarray
    Structured array of 14 major aspects with fields:

    - name (str): Aspect name (e.g., 'Conjunction', 'Trine').
    - angle (float): Aspect angle in degrees (0-180).
    - coef (float): Coefficient for orb calculation.
    - harmonic (int): Harmonic number (half-circle 1/2/3/6 divide 180°; full-circle 5/9/10 divide 360°).
    - symbol (str): Unicode astrological glyph (majors only; minors are blank).

    Aspect angles: 0° (conjunction), 30° (semi-sextile), 36° (decile),
    40° (novile), 60° (sextile), 72° (quintile), 80° (binovile),
    90° (square), 108° (tredecile), 120° (trine), 144° (biquintile),
    150° (quincunx), 160° (quadrinovile), 180° (opposition).

signs : list
    List of 12 zodiac sign names in order:
    Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio,
    Sagittarius, Capricorn, Aquarius, Pisces.

Examples
--------
>>> from ketu.core import bodies, aspects, signs
>>> # Access body data
>>> sun_id = bodies['id'][bodies['name'] == b'Sun'][0]
>>> print(sun_id)
0
>>> # Access aspect angles
>>> trine_angle = aspects['angle'][aspects['name'] == b'Trine'][0]
>>> print(trine_angle)
120.0
>>> # Access sign names
>>> print(signs[0])
Aries
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
        ("Rahu", 10, 0, -0.013),  # Mean North Node
        ("Ketu", 11, 0, -0.013),  # Mean South Node (opposite of Rahu)
        ("Lilith", 12, 0, 0.113),  # Mean Apogee (Black Moon)
        ("Chiron", 13, 4, 0.019),  # Centaur, Chebyshev-based position
    ],
    dtype=[("name", "S12"), ("id", "i4"), ("orb", "f4"), ("speed", "f4")],
)

# Structured array of major aspects (harmonics 1, 2, 3, 5, 6, 9, and 10)
# Fields: name, angle (degrees), coefficient for orb calculation, harmonic number, symbol glyph
# Harmonic convention: half-circle harmonics (1/2/3/6) divide 180°; full-circle (5/9/10) divide 360°.
# Frozen mapping: Sextile=H3, Trine=H3, Semi-sextile=H6, Quincunx=H6 (concepts.md).
# 7 major glyphs (Conjunction, Semi-sextile, Sextile, Square, Trine, Quincunx, Opposition);
# 7 minor aspects (Decile, Novile, Quintile, Binovile, Tredecile, Biquintile, Quadrinovile) get blank symbol.
aspects = np.array(
    [
        # Classical aspects (Harmonics 1, 2, 3, 6)
        ("Conjunction", 0, 1, 1, "☌"),        # H1, ☌
        ("Semi-sextile", 30, 1 / 6, 6, "⚺"),  # H6, ⚺
        ("Decile", 36, 1 / 10, 10, ""),             # H10, blank
        ("Novile", 40, 1 / 9, 9, ""),               # H9, blank
        ("Sextile", 60, 1 / 3, 3, "⚹"),        # H3, ⚹
        ("Quintile", 72, 1 / 5, 5, ""),             # H5, blank
        ("Binovile", 80, 2 / 9, 9, ""),             # H9, blank
        ("Square", 90, 1 / 2, 2, "□"),         # H2, □
        ("Tredecile", 108, 3 / 10, 10, ""),         # H10, blank
        ("Trine", 120, 2 / 3, 3, "△"),         # H3, △
        ("Biquintile", 144, 2 / 5, 5, ""),          # H5, blank
        ("Quincunx", 150, 5 / 6, 6, "⚻"),      # H6, ⚻
        ("Quadrinovile", 160, 4 / 9, 9, ""),        # H9, blank
        ("Opposition", 180, 1, 1, "☍"),        # H1, ☍
    ],
    dtype=[("name", "S16"), ("angle", "f4"), ("coef", "f4"), ("harmonic", "i4"), ("symbol", "U4")],
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
