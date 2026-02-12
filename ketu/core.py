"""Core data structures and constants for Ketu astrological calculations.

This module contains the fundamental astronomical and astrological data structures
used throughout the Ketu library, including planetary bodies, aspects, and zodiac signs.

Data Structures
---------------
bodies : numpy.ndarray
    Structured array of 13 astronomical bodies with fields:
    - name (str): Body name (e.g., 'Sun', 'Moon', 'Mars')
    - id (int): Body identifier (0-12)
    - orb (float): Default orb in degrees for aspect calculations
    - speed (float): Average daily motion in degrees/day

    Body IDs:
    0=Sun, 1=Moon, 2=Mercury, 3=Venus, 4=Mars, 5=Jupiter, 6=Saturn,
    7=Uranus, 8=Neptune, 9=Pluto, 10=Rahu (Mean North Node),
    11=Ketu (Mean South Node), 12=Lilith (Mean Apogee/Black Moon)

aspects : numpy.ndarray
    Structured array of 14 major aspects with fields:
    - name (str): Aspect name (e.g., 'Conjunction', 'Trine')
    - angle (float): Aspect angle in degrees (0-180)
    - coef (float): Coefficient for orb calculation

    Aspect angles: 0° (conjunction), 30° (semi-sextile), 36° (decile),
    40° (novile), 60° (sextile), 72° (quintile), 80° (binovile),
    90° (square), 108° (tredecile), 120° (trine), 144° (biquintile),
    150° (quincunx), 160° (quadrinovile), 180° (opposition)

signs : list
    List of 12 zodiac sign names in order:
    Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio,
    Sagittarius, Capricorn, Aquarius, Pisces

Notes
-----
Orb values are inspired by medieval Islamic astronomers Abu Ma'shar (787-886)
and Al-Biruni (973-1050), adapted for modern precision calculations.

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
    ],
    dtype=[("name", "S12"), ("id", "i4"), ("orb", "f4"), ("speed", "f4")],
)

# Structured array of major aspects (harmonics 1, 2, 3, 6, 9, and 10)
# Fields: name, angle (degrees), coefficient for orb calculation
aspects = np.array(
    [
        # Classical aspects (Harmonics 1, 2, 3, 6)
        ("Conjunction", 0, 1),
        ("Semi-sextile", 30, 1 / 6),
        ("Decile", 36, 1 / 10),  # H10 - Semi-quintile
        ("Novile", 40, 1 / 9),  # H9 - Nonagone
        ("Sextile", 60, 1 / 3),
        ("Quintile", 72, 1 / 5),  # H5 (sub-harmonic of H10)
        ("Binovile", 80, 2 / 9),  # H9
        ("Square", 90, 1 / 2),
        ("Tredecile", 108, 3 / 10),  # H10 - Tri-decile
        ("Trine", 120, 2 / 3),
        ("Biquintile", 144, 2 / 5),  # H5 (sub-harmonic of H10)
        ("Quincunx", 150, 5 / 6),
        ("Quadrinovile", 160, 4 / 9),  # H9
        ("Opposition", 180, 1),
    ],
    dtype=[("name", "S16"), ("angle", "f4"), ("coef", "f4")],
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
