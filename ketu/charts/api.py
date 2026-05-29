"""
Public API for the charts subpackage: :func:`compute_chart` and :func:`is_day_chart`.

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
``compute_chart`` projects intra-chart aspects into a dense ``(14, 14)``
matrix via a Python loop over the leading shape ``S`` (D-16); each
``S``-element call to
:func:`ketu.aspects.calculator.calculate_aspects_vectorized` is itself
vectorised over the 91 body-pair upper-triangle, so the Python
overhead is constant in ``S``. ``is_day_chart`` exposes the
sunrise-inclusive sect helper required by Phase 19 (Arabic Parts) with
internal Porphyry polar fallback (D-15). Signatures and docstrings are
stable across waves so the doc gates (``interrogate >= 95%``,
``numpydoc validate``) remain green continuously.
"""
from __future__ import annotations

from typing import Literal, Union, cast

import numpy as np

from ketu.aspects.calculator import calculate_aspects_vectorized
from ketu.aspects.presets import AspectSetSpec
from ketu.core import bodies as _CANONICAL_BODIES
from ketu.ephemeris.planets import calc_planet_position_batch
from ketu.houses import calculate_houses
from ketu.houses.ascmc import compute_ascmc

from .core import CHART_DTYPE

ArrayLike = Union[float, np.ndarray]

#: Number of canonical bodies in the (14,) axis. Derived from
#: :data:`ketu.core.bodies` so a grow-the-axis change auto-propagates here.
#: Lifted to 14 by the v1.3 D-08 ratchet (Chiron added as body 13).
#: Pinned by ``test_body_count_frozen_at_fourteen`` (CHART_DTYPE subarray
#: shapes updated to (14,) / (14, 14) atomically with this change).
_BODY_COUNT: int = len(_CANONICAL_BODIES)


def _vectorised_body_properties(
    jd_b: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute per-body lon/lat/speed for a broadcast jd array.

    Loops over the 14 canonical bodies (NOT over the leading shape S).
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
        Shape ``S + (14,)``, dtype ``float64``. Ecliptic longitudes per
        body, degrees in ``[0, 360)``.
    body_lats : np.ndarray
        Shape ``S + (14,)``, dtype ``float64``. Ecliptic latitudes per
        body, degrees.
    body_speeds : np.ndarray
        Shape ``S + (14,)``, dtype ``float64``. Longitude speeds per
        body, ``deg/day`` (negative => retrograde).

    Notes
    -----
    The 14-body axis order follows :data:`ketu.core.bodies`
    (Sun=0, ..., Lilith=12, Chiron=13). Lifted to 14 by v1.3 D-08 ratchet.
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


def _build_aspect_matrix(
    jd_b: np.ndarray,
    aspects: AspectSetSpec,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Build the dense ``(13, 13)`` aspect matrix and orb matrix over leading shape ``S``.

    Loops over ``S`` in Python (per D-16); each ``S``-element call to
    :func:`ketu.aspects.calculator.calculate_aspects_vectorized` is
    natively vectorised over the 78 body-pair upper-triangle, so the
    Python overhead is constant in ``S``. The diagonal stays at the
    sentinel state (a body has no aspect with itself, D-06).

    Parameters
    ----------
    jd_b : np.ndarray
        Broadcast Julian Date array, leading shape ``S`` (any compatible
        shape — 0-d, 1-d, 2-d, etc.). Scalar-jd traverses the loop via
        ``np.ndindex(()) == [()]`` (RESEARCH Assumption A1).
    aspects : AspectSetSpec
        Pass-through to ``calculate_aspects_vectorized``. ``None``
        resolves to :data:`ketu.aspects.presets.CLASSICAL` (5 majors,
        per D-07). Accepts a preset name (``"classical"``,
        ``"traditional"``, ``"extended"``), a list of aspect names or
        canonical indices, or a length-14 boolean mask.

    Returns
    -------
    aspect_matrix : np.ndarray
        Shape ``S + (13, 13)``, dtype ``int8``. Each cell holds the
        canonical aspect index ``i_asp`` in ``[0, 13]`` (per
        :data:`ketu.core.aspects` ordering) when an aspect is in orb,
        or ``-1`` for "no aspect" (D-06). Symmetric per D-17:
        ``matrix[..., i, j] == matrix[..., j, i]``. Diagonal stays at
        ``-1``.
    aspect_orbs : np.ndarray
        Shape ``S + (13, 13)``, dtype ``float32``. Orb in degrees when
        an aspect is in orb, ``NaN`` for "no orb" (D-06). Symmetric per
        D-17. Diagonal stays at ``NaN``.

    Notes
    -----
    The Python loop over ``S`` is an explicit v1.2 trade-off (D-16):
    ``compute_chart`` is typically called for ML batches in the
    hundreds (synastry, composite, solar return), not 100k+. A
    pure-vectorised reimplementation can land in v1.3 if Phase 16
    profiling motivates it.
    """
    matrix = np.full(
        jd_b.shape + (_BODY_COUNT, _BODY_COUNT), -1, dtype=np.int8,
    )
    orbs = np.full(
        jd_b.shape + (_BODY_COUNT, _BODY_COUNT), np.nan, dtype=np.float32,
    )

    # ``np.ndindex(())`` yields exactly one tuple ``()`` for a 0-d shape,
    # so the scalar-jd case traverses this loop once with ``idx == ()``
    # naturally — no special-casing needed (RESEARCH Assumption A1, pinned
    # by ``test_aspect_matrix_scalar_jd_via_ndindex_empty_tuple``).
    #
    # TODO(v1.3): hoist ``resolve_aspect_set(aspects)`` above this loop if
    # profiling shows hot-path cost — see RESEARCH §Pitfall 3. For v1.2
    # the resolver runs at ~µs and ``S`` stays in the hundreds, so the
    # repeated call is acceptable.
    for idx in np.ndindex(jd_b.shape):
        jd_scalar = float(jd_b[idx])
        records = calculate_aspects_vectorized(jd_scalar, aspects=aspects)
        # ``records`` is a structured array with fields
        # ``(body1, body2, i_asp, orb)`` ; ``body1 < body2`` by
        # upper-triangle convention (calculator.py:187 ``triu_indices``).
        for rec in records:
            i = int(rec["body1"])
            j = int(rec["body2"])
            i_asp = int(rec["i_asp"])
            orb = float(rec["orb"])
            # D-17 mirror: write upper- AND lower-triangle so callers
            # can index either order without ceremony.
            matrix[idx + (i, j)] = i_asp
            matrix[idx + (j, i)] = i_asp
            orbs[idx + (i, j)] = orb
            orbs[idx + (j, i)] = orb

    return matrix, orbs


def compute_chart(
    jd: ArrayLike,
    lat: ArrayLike,
    lon: ArrayLike,
    system: str = "placidus",
    aspects: AspectSetSpec = None,
    polar_fallback: Literal["raise", "porphyry"] = "raise",
) -> np.ndarray:
    """
    Compute a fully-resolved natal chart in one vectorisable call.

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
        the package-wide default (D-07). Accepts a preset name
        (``"classical"``, ``"traditional"``, ``"extended"``), a list of
        aspect names or canonical indices, or a length-14 boolean mask
        (pass-through to
        :func:`ketu.aspects.calculator.calculate_aspects_vectorized`,
        D-10). The ``aspect_matrix`` field stores canonical 0-13 indices
        regardless of the selected subset; cells outside the subset stay
        at the sentinel ``-1``.
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

    See Also
    --------
    ketu.houses.calculate_houses : House cusps + ASC/MC/ARMC/Vertex
        engine called internally; ``polar_fallback`` is a pass-through
        per D-11.
    ketu.aspects.calculate_aspects_vectorized : Aspect engine whose
        records are projected into the dense ``(13, 13)``
        ``aspect_matrix`` / ``aspect_orbs`` block per D-05/D-17.
    ketu.charts.is_day_chart : Sect helper (sunrise-inclusive,
        polar-safe) used by Arabic Parts (Phase 19); standalone per
        D-12 (not stored in :data:`CHART_DTYPE`).

    Notes
    -----
    The body axis (the ``(13,)`` dimension of ``body_lons``,
    ``body_lats``, ``body_speeds`` and the leading axis of
    ``aspect_matrix`` / ``aspect_orbs``) is FROZEN per D-08. Indices
    follow :data:`ketu.core.bodies` order (Sun=0, ..., Lilith=12).
    Adding bodies is a v1.3 BREAKING change.

    The aspect matrix is built by a Python loop over the leading shape
    ``S`` (D-16). Each ``S``-element call to
    :func:`ketu.aspects.calculator.calculate_aspects_vectorized` is
    itself vectorised over the 78 body-pair upper-triangle, so the
    Python overhead is constant in ``S``. For ML batches in the
    hundreds (synastry, composite, solar return), this is comfortably
    below the bottleneck threshold; large-batch (>10k) callers should
    profile and report. ``aspects=None`` resolves to the ``CLASSICAL``
    preset (5 majors), aligned with the package-wide default (D-07).
    The matrix is symmetric (D-17): ``matrix[..., i, j] == matrix[..., j, i]``;
    the diagonal stays at the sentinel ``-1`` (a body has no aspect with
    itself, D-06).

    **Accuracy vs Swiss Ephemeris.** Body longitudes agree with Swiss
    Ephemeris to ±0.1° for inner planets (Mercury, Venus, Mars),
    ±0.5° for outer planets (Jupiter–Pluto), and ±0.01° for the Moon.
    House cusps (Placidus/Koch) agree with Swiss to ±0.01°. These
    differences are due to Ketu's pure-NumPy orbital model vs. the
    Swiss VSOP87/ELP2000 series. For research or astrological-software
    comparison, verify against Astro.com at your reference dates.

    **Supported date range.** 1800–2200 CE. Accuracy degrades outside
    this range as the mean-orbital-element series diverges from the
    true orbit.

    **Edge cases.** At polar latitudes (|lat| > ~66.56°), Placidus and
    Koch produce mathematically undefined cusps (the circumpolar Sun
    never crosses the needed horizon arcs). Pass ``polar_fallback=
    'porphyry'`` to substitute Porphyry cusps for polar elements, or
    use ``system='whole_sign'`` / ``system='equal'`` which are polar-safe.
    The body axis ``(13,)`` is frozen per D-08 — adding bodies is a
    v1.3 breaking change.

    Examples
    --------
    Scalar input (J2000 = 2000-01-01T12:00 UT, Paris):

    >>> import numpy as np
    >>> chart = compute_chart(2451545.0, 48.86, 2.35)
    >>> chart["body_lons"].shape
    (13,)
    >>> chart["aspect_matrix"].shape
    (13, 13)

    Vectorised over an array of (jd, lat, lon) triples:

    >>> jd = np.array([2451545.0, 2470204.0])
    >>> lat = np.array([48.86, 64.15])
    >>> lon = np.array([2.35, -21.94])
    >>> charts = compute_chart(jd, lat, lon, polar_fallback="porphyry")
    >>> charts.shape, charts["body_lons"].shape, charts["aspect_matrix"].shape
    ((2,), (2, 13), (2, 13, 13))
    """
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

    # 4. Aspect matrix: dense (13, 13) projection of intra-chart aspects
    #    (D-05, D-06, D-17). Python loop over S is a conscious v1.2
    #    trade-off (D-16); revisited in v1.3 if synastry profiling
    #    motivates a pure-vectorised reimplementation.
    aspect_matrix, aspect_orbs = _build_aspect_matrix(jd_b, aspects=aspects)

    # 5. Assemble structured output.
    out = np.empty(leading_shape, dtype=CHART_DTYPE)
    out["jd"] = jd_b
    out["lat"] = lat_b
    out["lon"] = lon_b
    # Single source-of-truth: read the canonical (lowercased) system
    # name back from calculate_houses' output rather than re-normalising
    # locally. Avoids drift if HOUSES_DTYPE['system'] ever changes its
    # normalisation rule (alias resolution, kebab-case, etc.).
    out["system"] = houses["system"]
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
    """
    Return True when the Sun is at or above the horizon (sunrise inclusive).

    Vectorised sect helper required by Arabic Parts (Phase 19). Each
    output element is ``True`` when the natal Sun lies in the
    above-horizon hemisphere (houses 7..12 of the natal cusps);
    ``False`` otherwise.

    Parameters
    ----------
    jd : float or np.ndarray
        Julian Date, UT. Time inputs are UTC only.
    lat : float or np.ndarray
        Geographic latitude (degrees). Polar latitudes (``|lat| >
        polar_circle(jd)``) are handled via internal Porphyry fallback
        — see Notes.
    lon : float or np.ndarray
        Geographic longitude (degrees, east-positive).

    Returns
    -------
    np.ndarray of bool
        Boolean array with shape ``np.broadcast_shapes(jd, lat, lon)``.
        ``True`` where the Sun is in houses 7..12 (above horizon = day),
        ``False`` otherwise (below horizon = night).

    See Also
    --------
    ketu.charts.compute_chart : Full natal-chart primitive; consumers
        that already have a :data:`CHART_DTYPE` can call
        ``is_day_chart`` separately rather than storing sect inside
        the chart (D-12 rationale: avoids double source-of-truth).
    ketu.houses.ascmc.compute_ascmc : Closed-form ASC/MC/ARMC/Vertex
        engine used internally for the system-independent ASC value.

    Notes
    -----
    **Sect convention (D-13).** Sunrise-inclusive: a Sun exactly on the
    Ascendant resolves to **day**. This matches the Hellenistic
    standard and is consistent with Solar Fire, Astro.com, and Robert
    Hand's published rules. The implementation honours D-13 literally
    via the diurnal-arc test ``(asc - sun_lon) mod 360 < 180`` — the
    Sun trails the rotating Ascendant by 0..180° while above the
    horizon. ``delta == 0`` (Sun exactly on the Ascendant) yields
    ``True`` (day, sunrise-inclusive); ``delta == 180`` (Sun exactly on
    the Descendant) yields ``False`` (night, sunset-exclusive).
    Synthetic deltas of +/-0.01 deg around the ASC are pinned by the
    test suite alongside the strict equality case.

    **Polar safety (D-15).** ``is_day_chart`` derives the Ascendant
    directly from :func:`ketu.houses.ascmc.compute_ascmc`, which is
    closed-form via :func:`numpy.arctan2` and mathematically defined
    at every latitude (including 80°+). High-latitude users
    (Reykjavik, Tromso, relocated Solar Return to polar latitudes,
    Arabic Parts at lat > 66.5 deg) always receive a bool answer
    instead of a :class:`ketu.houses.HighLatitudeError`. The
    user-facing :func:`compute_chart` does **not** impose this
    polar tolerance — ``is_day_chart`` does, by design, because the
    sect helper must always return a definitive bool.

    **Geometric definition (D-14).** The above-horizon hemisphere is
    the *trailing* semicircle of the rotating Ascendant: as the Earth
    rotates the ASC sweeps eastward through the zodiac while the Sun
    is roughly stationary, so an above-horizon Sun trails the ASC by
    ``0..180°`` of zodiacal longitude. Equivalently, the Sun is above
    the horizon when ``(asc - sun_lon) mod 360 < 180`` — i.e. when
    ``sun_lon`` lies in the half-open arc ``[ASC - 180, ASC]`` (mod
    360). This is system-independent — it depends only on the
    Ascendant, not on the chosen house system. Phase 15 will add
    Whole Sign and Equal house systems whose cusp 7 is **not** at
    ``ASC + 180``; the ASC-delta formulation here remains correct
    for those systems and matches the Hellenistic definition of sect.

    **Standalone helper (D-12).** ``is_day``-ness is **not** stored in
    :data:`ketu.charts.CHART_DTYPE`: storing it would create a double
    source-of-truth that drifts if a caller post-edits ``body_lons[0]``
    (Sun) or ``asc``. Phase 19 (Arabic Parts) calls this helper
    directly with ``(jd, lat, lon)``.

    Examples
    --------
    Scalar input (J2000 = 2000-01-01 12:00 UT at Paris, Sun near MC):

    >>> import numpy as np
    >>> bool(is_day_chart(2451545.0, 48.8566, 2.3522))
    True

    Vectorised input (J2000 midnight + noon at Paris):

    >>> jd = np.array([2451544.5, 2451545.0])
    >>> bool(is_day_chart(jd, 48.8566, 2.3522)[0])
    False
    >>> bool(is_day_chart(jd, 48.8566, 2.3522)[1])
    True

    Polar safety (Tromso, midsummer noon — Porphyry fallback prevents raise):

    >>> bool(is_day_chart(2451727.0, 69.65, 18.96))
    True
    """
    # 1. Broadcast (mirror compute_chart / calculate_houses).
    jd_a = np.asarray(jd, dtype=np.float64)
    lat_a = np.asarray(lat, dtype=np.float64)
    lon_a = np.asarray(lon, dtype=np.float64)
    jd_b, lat_b, lon_b = np.broadcast_arrays(jd_a, lat_a, lon_a)

    # 2. Closed-form Ascendant via compute_ascmc — system-independent and
    #    polar-safe (D-15). compute_ascmc is pure numpy.arctan2 math,
    #    mathematically defined at every latitude including 80°+, so we
    #    never raise HighLatitudeError. Crucially this also makes
    #    is_day_chart independent of any house system: Phase 15 will
    #    introduce Whole Sign / Equal where DESC != ASC + 180, but the
    #    Hellenistic sect definition is the eastward semicircle from the
    #    ASC (above-horizon hemisphere), which holds regardless of the
    #    house system.
    ascmc = compute_ascmc(jd_b, lat_b, lon_b)
    asc = np.asarray(ascmc["asc"], dtype=np.float64)

    # 3. Sun longitude per element. body_id=0 in calc_planet_position_batch
    #    is the Sun (PATTERNS § 3.2; mirrors _vectorised_body_properties
    #    body_id=0 column in compute_chart).
    sun_lon_flat = calc_planet_position_batch(jd_b.ravel(), 0)[:, 0]
    sun_lon = sun_lon_flat.reshape(jd_b.shape)

    # 4. Above-horizon test: a Sun whose ecliptic longitude is at or
    #    "behind" the Ascendant (within the preceding 180°) is above the
    #    horizon. The diurnal arc carries the Sun *backward* through the
    #    zodiac relative to the rotating ASC: at sunrise ``Sun == ASC``
    #    (delta = 0); just after sunrise the ASC has moved eastward of
    #    the Sun (Sun in house 12, ``asc - sun_lon`` slightly positive);
    #    at the MC the Sun trails the ASC by ~90°; at sunset it trails by
    #    180° (DESC). So sect is ``(asc - sun_lon) mod 360 < 180``:
    #    delta == 0 (Sun on ASC) -> day (D-13 sunrise-inclusive); delta
    #    == 180 (Sun on DESC) -> night (sunset-exclusive). This is
    #    system-independent: Whole Sign / Equal (Phase 15) leave this
    #    semicircle definition unchanged. Wrap in ``np.asarray`` so
    #    scalar inputs still yield a 0-d ``np.ndarray`` of dtype ``bool``
    #    rather than a bare ``np.bool_`` scalar — this keeps the public
    #    return contract (``np.ndarray``) uniform across scalar and
    #    vectorised call sites.
    delta = (asc - sun_lon) % 360.0
    return np.asarray(delta < 180.0)
