"""Public API for the charts subpackage: :func:`compute_chart` and :func:`is_day_chart`.

Two public functions, both vectorised over ``(jd, lat, lon)`` of any
broadcast-compatible shape:

- :func:`compute_chart` — Compute a fully-resolved natal chart (positions,
  ASC/MC/ARMC/Vertex, cusps, aspects) in one call. Returns a structured
  array of :data:`ketu.charts.CHART_DTYPE` with leading shape equal to the
  broadcast shape of the inputs.
- :func:`is_day_chart` — Sect helper. Returns ``True`` when the Sun is at
  or above the horizon (sunrise inclusive). Polar-safe via internal
  Porphyry fallback.

Both are pure NumPy. No swisseph runtime import — the swisseph oracle
lives only in :mod:`tests.charts.conftest` (test-only, AGPL boundary).

Notes
-----
Plan 14-02 wires ``compute_chart`` for positions + houses (with
``aspect_matrix`` / ``aspect_orbs`` sentinel-initialised to ``-1`` /
``NaN``); plan 14-03 will populate the dense aspect block; plan 14-04
will wire ``is_day_chart``. Signatures and docstrings stay stable wave
by wave so the doc gates (``interrogate >= 95%``, ``numpydoc validate``)
remain green continuously.
"""
from __future__ import annotations

from typing import Literal, Union, cast

import numpy as np

from ketu.aspects.presets import AspectSetSpec
from ketu.ephemeris.planets import calc_planet_position_batch
from ketu.houses import calculate_houses

from .core import CHART_DTYPE

ArrayLike = Union[float, np.ndarray]

#: Number of canonical bodies in the (13,) axis. Frozen per D-08 (Kala
#: positional contract). Mirrors ``len(ketu.core.bodies)`` and the
#: subarray shapes pinned in :data:`ketu.charts.CHART_DTYPE`.
_BODY_COUNT: int = 13


def _vectorised_body_properties(
    jd_b: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute per-body lon/lat/speed for a broadcast jd array.

    Loops over the 13 canonical bodies (NOT over the leading shape S).
    Each iteration calls :func:`ketu.ephemeris.planets.calc_planet_position_batch`,
    which is natively vectorised on jd; the total Python loop count is
    therefore constant in S (Pitfall 1 from RESEARCH §5).

    Parameters
    ----------
    jd_b : np.ndarray
        Broadcast Julian Date array, leading shape ``S`` (any compatible
        shape — 0-d, 1-d, 2-d, etc.).

    Returns
    -------
    body_lons : np.ndarray
        Shape ``S + (13,)``, dtype ``float64``. Ecliptic longitudes per
        body, degrees in ``[0, 360)``.
    body_lats : np.ndarray
        Shape ``S + (13,)``, dtype ``float64``. Ecliptic latitudes per
        body, degrees.
    body_speeds : np.ndarray
        Shape ``S + (13,)``, dtype ``float64``. Longitude speeds per
        body, ``deg/day`` (negative => retrograde).

    Notes
    -----
    The 13-body axis order follows :data:`ketu.core.bodies`
    (Sun=0, ..., Lilith=12) and is FROZEN per decision D-08.
    """
    jd_flat = np.asarray(jd_b, dtype=np.float64).ravel()  # shape (M,)
    n = jd_flat.size
    lons = np.empty((n, _BODY_COUNT), dtype=np.float64)
    lats = np.empty((n, _BODY_COUNT), dtype=np.float64)
    speeds = np.empty((n, _BODY_COUNT), dtype=np.float64)
    for body_id in range(_BODY_COUNT):
        # calc_planet_position_batch returns (n, 6):
        # [lon, lat, dist, lon_speed, lat_speed, dist_speed].
        batch = calc_planet_position_batch(jd_flat, body_id)
        lons[:, body_id] = batch[:, 0]
        lats[:, body_id] = batch[:, 1]
        speeds[:, body_id] = batch[:, 3]
    tail_shape = jd_b.shape + (_BODY_COUNT,)
    return (
        lons.reshape(tail_shape),
        lats.reshape(tail_shape),
        speeds.reshape(tail_shape),
    )


def compute_chart(
    jd: ArrayLike,
    lat: ArrayLike,
    lon: ArrayLike,
    system: str = "placidus",
    aspects: AspectSetSpec = None,
    polar_fallback: Literal["raise", "porphyry"] = "raise",
) -> np.ndarray:
    """Compute a fully-resolved natal chart in one vectorisable call.

    Returns a structured array of :data:`ketu.charts.CHART_DTYPE` carrying
    body positions, ASC/MC/ARMC/Vertex, the 12 house cusps, and a dense
    13x13 aspect matrix. ``(jd, lat, lon)`` broadcast to a common leading
    shape ``S``; the returned structured array has the same leading shape
    (success criterion 14.2).

    Parameters
    ----------
    jd : float or np.ndarray
        Julian Date, UT. Time inputs are UTC only — see the project
        constraints in PROJECT.md.
    lat : float or np.ndarray
        Geographic latitude (degrees).
    lon : float or np.ndarray
        Geographic longitude (degrees, east-positive).
    system : str, default "placidus"
        House system name. Any system registered via
        :func:`ketu.houses.registry.register` (currently
        ``"placidus"``, ``"koch"``, ``"porphyry"``). Case-insensitive.
    aspects : AspectSetSpec, default None
        Aspect-set selector. Accepted for API stability and reserved for
        plan 14-03 (D-10); currently ignored — see Notes. ``None``
        resolves to :data:`ketu.aspects.presets.CLASSICAL` (5 majors)
        once plan 14-03 wires the dense aspect computation (D-07).
    polar_fallback : {"raise", "porphyry"}, default "raise"
        Behaviour when ``|lat| > polar_circle(jd)`` (~ 66.56 deg). Passed
        through to :func:`ketu.houses.calculate_houses` (D-11). When
        ``"raise"``, polar inputs raise
        :class:`ketu.houses.HighLatitudeError`; when ``"porphyry"``,
        Porphyry cusps substitute for polar elements only.

    Returns
    -------
    np.ndarray
        Structured array of :data:`ketu.charts.CHART_DTYPE`, leading
        shape == ``np.broadcast_shapes(jd, lat, lon)``. The aspect
        matrix uses ``-1`` (i1) for "no aspect" and ``NaN`` (f4) for
        "no orb"; both are symmetric and have diagonal sentinels.

    Raises
    ------
    HighLatitudeError
        When ``polar_fallback='raise'`` and any input exceeds the polar
        circle (propagated from :func:`ketu.houses.calculate_houses`).
    ValueError
        When ``system`` is unknown or ``polar_fallback`` is invalid
        (propagated from :func:`ketu.houses.calculate_houses`).

    Notes
    -----
    The body axis (the ``(13,)`` dimension of ``body_lons``,
    ``body_lats``, ``body_speeds`` and the leading axis of
    ``aspect_matrix`` / ``aspect_orbs``) is FROZEN per D-08. Indices
    follow :data:`ketu.core.bodies` order (Sun=0, ..., Lilith=12).
    Adding bodies is a v1.3 BREAKING change.

    In this Plan-02 wiring, ``aspect_matrix`` and ``aspect_orbs`` are
    sentinel-initialised (``-1`` / ``NaN``) and the ``aspects`` parameter
    is accepted but not consumed. Plan 14-03 wires the dense aspect
    computation and removes this note.

    Examples
    --------
    Scalar input:

    >>> import numpy as np
    >>> chart = compute_chart(2451545.0, 48.86, 2.35)  # doctest: +SKIP
    >>> chart["body_lons"].shape  # doctest: +SKIP
    (13,)
    >>> chart["aspect_matrix"].shape  # doctest: +SKIP
    (13, 13)

    Vectorised over an array of (jd, lat, lon) triples (success
    criterion 14.2):

    >>> jd = np.array([2451545.0, 2470204.0])  # doctest: +SKIP
    >>> lat = np.array([48.86, 64.15])  # doctest: +SKIP
    >>> lon = np.array([2.35, -21.94])  # doctest: +SKIP
    >>> charts = compute_chart(jd, lat, lon, polar_fallback="porphyry")  # doctest: +SKIP
    >>> charts.shape, charts["body_lons"].shape, charts["aspect_matrix"].shape  # doctest: +SKIP
    ((2,), (2, 13), (2, 13, 13))
    """
    # ``aspects`` is accepted for API stability; plan 14-03 will consume it.
    del aspects

    # 1. Broadcast (mirror calculate_houses houses/api.py:107-114).
    jd_a = np.asarray(jd, dtype=np.float64)
    lat_a = np.asarray(lat, dtype=np.float64)
    lon_a = np.asarray(lon, dtype=np.float64)
    jd_b, lat_b, lon_b = np.broadcast_arrays(jd_a, lat_a, lon_a)
    leading_shape = jd_b.shape

    # 2. Houses (one call covers cusps + ASC/MC/ARMC/Vertex + polar dispatch).
    #    Validation of ``polar_fallback`` and ``system`` happens here too —
    #    not duplicated locally (PATTERNS § 3.1 "Skip" guidance).
    houses = calculate_houses(
        jd_b, lat_b, lon_b,
        system=system, polar_fallback=polar_fallback,
    )

    # 3. Body positions vectorised on S (loop bound to 13 bodies, constant
    #    in S; see _vectorised_body_properties docstring).
    body_lons, body_lats, body_speeds = _vectorised_body_properties(jd_b)

    # 4. Aspect matrix: sentinel-initialised for now; plan 14-03 will
    #    replace this with a real call to ``_build_aspect_matrix(...)``.
    aspect_matrix = np.full(
        leading_shape + (_BODY_COUNT, _BODY_COUNT),
        -1, dtype=np.int8,
    )
    aspect_orbs = np.full(
        leading_shape + (_BODY_COUNT, _BODY_COUNT),
        np.nan, dtype=np.float32,
    )

    # 5. Assemble structured output.
    out = np.empty(leading_shape, dtype=CHART_DTYPE)
    out["jd"] = jd_b
    out["lat"] = lat_b
    out["lon"] = lon_b
    out["system"] = system.lower()
    out["body_lons"] = body_lons
    out["body_lats"] = body_lats
    out["body_speeds"] = body_speeds
    out["cusps"] = houses["cusps"]
    out["asc"] = houses["asc"]
    out["mc"] = houses["mc"]
    out["armc"] = houses["armc"]
    out["vertex"] = houses["vertex"]
    out["aspect_matrix"] = aspect_matrix
    out["aspect_orbs"] = aspect_orbs

    return cast(np.ndarray, out)


def is_day_chart(
    jd: ArrayLike,
    lat: ArrayLike,
    lon: ArrayLike,
) -> np.ndarray:
    """Return True when the Sun is at or above the horizon (sunrise inclusive).

    Vectorised sect helper required by Arabic Parts (Phase 19). Each
    output element is ``True`` when the natal Sun is in the upper
    hemisphere (houses 7..12) or exactly on the Ascendant; ``False``
    otherwise.

    Parameters
    ----------
    jd : float or np.ndarray
        Julian Date, UT.
    lat : float or np.ndarray
        Geographic latitude (degrees).
    lon : float or np.ndarray
        Geographic longitude (degrees, east-positive).

    Returns
    -------
    np.ndarray of bool
        Broadcast shape over ``(jd, lat, lon)``. ``True`` = day chart,
        ``False`` = night chart.

    Raises
    ------
    NotImplementedError
        Always, until plan 14-04 wires the implementation.

    Notes
    -----
    Sunrise convention is **inclusive** (D-13): a Sun exactly on the
    Ascendant resolves to **day**. This matches the Hellenistic
    standard and is consistent with Solar Fire, Astro.com, and Robert
    Hand's published rules.

    Polar safety (D-15): ``is_day_chart`` computes its own ASC and
    cusps internally with ``polar_fallback="porphyry"`` so that
    high-latitude callers (Reykjavik, Tromso, Solar Return relocation
    to polar latitudes) never raise :class:`HighLatitudeError`.
    Porphyry cusps are mathematically defined at every latitude.

    The geometric definition (D-14) maps the Sun longitude to its
    house via :func:`ketu.houses.house_of` and tests house index
    >= 7 (above-horizon hemisphere). No declination math is required
    for v1.2 sect determination.

    Examples
    --------
    Scalar input:

    >>> is_day_chart(2451545.0, 48.86, 2.35)  # doctest: +SKIP
    array(True)

    Vectorised over an array of (jd, lat, lon) triples:

    >>> import numpy as np
    >>> jd = np.array([2451545.0, 2451545.0])  # doctest: +SKIP
    >>> lat = np.array([48.86, 80.0])  # doctest: +SKIP
    >>> lon = np.array([2.35, 0.0])  # doctest: +SKIP
    >>> is_day_chart(jd, lat, lon).shape  # doctest: +SKIP
    (2,)
    """
    raise NotImplementedError(
        "is_day_chart will be wired in plan 14-04."
    )
