"""Ketu - Astronomical cycle calculations.

A pure Python library for high-precision planetary ephemeris calculations,
cycle analysis, and aspect detection.

Submodules
----------
ketu.core
    Astronomical constants (bodies, aspects, signs)
ketu.calculations
    Position and velocity calculations for celestial bodies
ketu.aspects
    Aspect calculations, windows, timelines, and transits
ketu.cycles
    Planetary cycle time series generation
ketu.ephemeris
    Low-level ephemeris computations (time, planets, coordinates, orbital)
ketu.cache
    Ephemeris caching for fast lookups
ketu.complex
    Complex number representations for cycle features
ketu.lunar_calendar
    Lunar calendar generation
ketu.display
    CLI display functions

Precision Guarantees
--------------------
- Angular separation: ±1e-6° (0.0036 arcseconds)
- Planetary positions: ±0.1° for inner planets, ±0.5° for outer planets
- Lunar position: ±0.01° (36 arcseconds)
- Julian Date conversion: ±1 second
- Best accuracy: 1800-2200 CE

Coordinate Transformations
--------------------------
All coordinate transformations (ecliptic/equatorial, geocentric/heliocentric)
preserve ±1e-10° precision through careful numerical handling.

Body IDs
--------
0=Sun, 1=Moon, 2=Mercury, 3=Venus, 4=Mars, 5=Jupiter, 6=Saturn,
7=Uranus, 8=Neptune, 9=Pluto, 10=Rahu (North Node), 11=Ketu (South Node),
12=Lilith (Black Moon)

Examples
--------
>>> from ketu import bodies, aspects, signs
>>> print(bodies['name'][0].decode())  # First body
'Sun'
>>> print(aspects['angle'][0])  # First aspect angle
0.0
"""

__version__ = "0.4.0"
__author__ = "Loc Cosnier"
__license__ = "MIT"

from ketu.core import bodies, aspects, signs

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "bodies",
    "aspects",
    "signs",
]
