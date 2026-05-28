"""
Core types for the houses subpackage.

Defines :data:`HOUSES_DTYPE` (structured array layout for house cusp results)
and :class:`HighLatitudeError` (raised when latitude exceeds the polar circle
for the requested house system).

The dtype is a structured ``numpy.dtype`` with 9 fields including a
12-element subarray field ``cusps``. This matches the v1.1 milestone
contract HOU-05: a single dtype that downstream consumers (Kala) can
index positionally for ML pipelines.

The exception is a :class:`ValueError` subclass so callers can catch
``ValueError`` generically when the distinction between "bad input" and
"polar latitude" doesn't matter.
"""
from __future__ import annotations

import numpy as np

#: Structured dtype for house cusp results.
#:
#: Fields:
#:     - ``jd`` (f8): Julian Date, UT.
#:     - ``lat`` (f8): Geographic latitude, degrees.
#:     - ``lon`` (f8): Geographic longitude (east-positive), degrees.
#:     - ``system`` (U16): House system name (e.g. "placidus", "regiomontanus").
#:     - ``cusps`` (f8, (12,)): 12 house cusps in degrees [0, 360).
#:     - ``asc`` (f8): Ascendant, degrees [0, 360).
#:     - ``mc`` (f8): Medium Coeli, degrees [0, 360).
#:     - ``armc`` (f8): Right Ascension of Medium Coeli, degrees [0, 360).
#:     - ``vertex`` (f8): Vertex, degrees [0, 360).
#:
#: The ``cusps`` field is a subarray. For an outer shape ``(N,)`` array,
#: ``arr["cusps"]`` has shape ``(N, 12)``.
#:
#: .. versionchanged:: v1.2 (Phase 15)
#:     ``system`` field width bumped from U10 to U16 to accommodate
#:     ``"regiomontanus"`` (13 chars) without truncation. Read paths
#:     remain compatible (NumPy implicit U10⇄U16 cast on assignment;
#:     equality comparisons by content are unchanged). No public API
#:     change — additive only per v1.2 non-breaking-minor contract.
HOUSES_DTYPE: np.dtype = np.dtype([
    ("jd",      "f8"),
    ("lat",     "f8"),
    ("lon",     "f8"),
    ("system",  "U16"),
    ("cusps",   "f8", (12,)),  # subarray field; outer shape (N,) -> cusps shape (N, 12)
    ("asc",     "f8"),
    ("mc",      "f8"),
    ("armc",    "f8"),
    ("vertex",  "f8"),
])


class HighLatitudeError(ValueError):
    """
    Raised when ``|lat|`` exceeds the polar circle for the requested house system.

    Carries the latitude, the system name, and the actual polar circle
    (90 deg - mean_obliquity(jd)) for caller diagnostics. Subclass of
    :class:`ValueError` so callers can catch ``ValueError`` generically
    when desired.

    Parameters
    ----------
    lat : float
        Geographic latitude (degrees) that triggered the error.
    system : str
        House system name (e.g. "placidus") that does not support this latitude.
    polar_lat : float
        Polar circle for the epoch (degrees), typically ``90 - eps_mean(jd)``.

    Attributes
    ----------
    lat : float
    system : str
    polar_lat : float
    """

    def __init__(self, lat: float, system: str, polar_lat: float) -> None:
        super().__init__(
            f"latitude {lat:.4f}° exceeds polar circle {polar_lat:.4f}° "
            f"for house system {system!r}; pass polar_fallback='porphyry' to fall back."
        )
        self.lat: float = lat
        self.system: str = system
        self.polar_lat: float = polar_lat
