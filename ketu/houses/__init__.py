"""House system calculations.

Public API surface (HOU-02 + HOU-05 of v1.1 milestone):

- :func:`calculate_houses` — Compute house cusps for one or many charts.
- :func:`house_of` — Map a planetary longitude to its 1..12 house index.
- :data:`HOUSES_DTYPE` — Structured array layout for house results.
- :class:`HighLatitudeError` — Raised at polar latitudes (default behavior).
- :data:`SYSTEMS` — Dict of registered house-system implementations.

Plans 10-04 (Placidus) and 10-05 (Koch + Porphyry) register their
implementations into :data:`SYSTEMS`. Plan 10-06 wires the dispatch in
:func:`calculate_houses` and the lookup in :func:`house_of`. Until those
plans land, the public bodies stub-raise :class:`NotImplementedError`.

Examples
--------
>>> from ketu.houses import calculate_houses, house_of, HOUSES_DTYPE
>>> from ketu.houses import SYSTEMS, HighLatitudeError

See Also
--------
ketu.houses.registry.register : Decorator to add new systems.
ketu.houses.ascmc.compute_ascmc : Closed-form ASC/MC/ARMC/Vertex.
"""
from __future__ import annotations

from typing import Literal, Union

import numpy as np

from .core import HOUSES_DTYPE, HighLatitudeError
from .registry import SYSTEMS, get_system, register

__all__ = [
    "HOUSES_DTYPE",
    "HighLatitudeError",
    "SYSTEMS",
    "calculate_houses",
    "house_of",
]


def calculate_houses(
    jd: Union[float, np.ndarray],
    lat: Union[float, np.ndarray],
    lon: Union[float, np.ndarray],
    system: str = "placidus",
    polar_fallback: Literal["raise", "porphyry"] = "raise",
) -> np.ndarray:
    """Compute house cusps for one or many ``(jd, lat, lon)`` inputs.

    .. note::
        STUB IMPLEMENTATION — full body lands in Plan 10-06 (integration).
        Plans 10-04 (Placidus) and 10-05 (Koch + Porphyry) register their
        implementations into :data:`SYSTEMS`; Plan 10-06 wires this dispatch
        and ASC/MC/ARMC/Vertex glue from :mod:`ketu.houses.ascmc`.

    Parameters
    ----------
    jd : float or np.ndarray
        Julian Date, UT.
    lat : float or np.ndarray
        Geographic latitude (degrees).
    lon : float or np.ndarray
        Geographic longitude (degrees, east-positive).
    system : str, default "placidus"
        Registered house system name; case-insensitive.
    polar_fallback : {"raise", "porphyry"}, default "raise"
        Behavior when ``|lat|`` exceeds the polar circle for ``system``.
        ``"raise"`` raises :class:`HighLatitudeError`; ``"porphyry"`` falls
        back to the Porphyry algorithm (Plan 10-05).

    Returns
    -------
    np.ndarray
        Structured array of :data:`HOUSES_DTYPE`, leading shape preserved
        from broadcast of inputs.

    Raises
    ------
    NotImplementedError
        Always, until Plan 10-06 lands.
    """
    raise NotImplementedError(
        "calculate_houses is wired in Plan 10-06; "
        "use ketu.houses.SYSTEMS[system] directly until then "
        "(after Plans 10-04 / 10-05 register implementations)."
    )


def house_of(
    planet_lon: Union[float, np.ndarray],
    cusps: np.ndarray,
) -> np.ndarray:
    """Return the 1-indexed house containing each planetary longitude.

    .. note::
        STUB IMPLEMENTATION — full body lands in Plan 10-06.

    Parameters
    ----------
    planet_lon : float or np.ndarray
        Planetary ecliptic longitude(s) in degrees, ``[0, 360)``.
    cusps : np.ndarray
        12-element cusp array (or batched ``(N, 12)``) in degrees.

    Returns
    -------
    np.ndarray
        1-indexed house number(s) in ``{1, ..., 12}``.

    Raises
    ------
    NotImplementedError
        Always, until Plan 10-06 lands.
    """
    raise NotImplementedError(
        "house_of is wired in Plan 10-06."
    )
