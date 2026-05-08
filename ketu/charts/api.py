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
This module ships as a STUB in plan 14-01: :data:`CHART_DTYPE` is final
but the function bodies raise :class:`NotImplementedError`. Plans 14-02
and 14-03 wire ``compute_chart`` (positions + houses, then aspect_matrix);
plan 14-04 wires ``is_day_chart``. The signatures and docstrings are
final from plan 14-01 onward so the doc gates (``interrogate >= 95%``,
``numpydoc validate``) stay green continuously while implementation
lands wave by wave.
"""
from __future__ import annotations

from typing import Literal, Union

import numpy as np

from ketu.aspects.presets import AspectSetSpec

ArrayLike = Union[float, np.ndarray]


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
        Aspect-set selector. ``None`` resolves to
        :data:`ketu.aspects.presets.CLASSICAL` (5 majors), aligned with
        the Phase 9 default (D-07). Accepts the same spec as
        :func:`ketu.aspects.calculator.calculate_aspects_vectorized` —
        preset name, sequence of names/indices, or a length-14 boolean
        mask.
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
    NotImplementedError
        Always, until plans 14-02 (positions + houses) and 14-03
        (aspect_matrix) wire the implementation.
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
    raise NotImplementedError(
        "compute_chart will be wired in plan 14-02 (positions + houses) "
        "and plan 14-03 (aspect_matrix)."
    )


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
