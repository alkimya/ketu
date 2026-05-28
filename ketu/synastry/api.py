"""
Public compute surface for the synastry subpackage — :func:`calculate_synastry`.

Composition-only module: consumes two :data:`ketu.charts.CHART_DTYPE`
scalar records (Phase 14 foundation) and produces a structured array of
:data:`ketu.synastry.SYNASTRY_DTYPE` rows. No new astronomical math is
introduced; every astronomical primitive is sourced from existing v1.2
modules (:mod:`ketu.charts`, :mod:`ketu.aspects.presets`,
:mod:`ketu.aspects.calculator`, :mod:`ketu.calculations`).

Locked design decisions (carried forward from Plan 16-01 + CONTEXT.md):

- **Cross-product enumeration over 15x15 = 225 ordered pairs (NOT
  :func:`numpy.triu_indices`); self-pairs INCLUDED per locked decision**
  — Sun_A<->Sun_B, Moon_A<->Moon_B are canonical synastry aspects (ego
  compatibility, emotional compatibility) and the row ``(Sun_A, Mars_B)``
  is semantically distinct from ``(Mars_A, Sun_B)`` because chart-of-origin
  is part of the identity.
- **Default ``orbs="synastry"`` tightens natal orbs by factor 0.5**
  (Astrodienst convention; cited in :data:`ketu.synastry.orbs.SYNASTRY_FACTOR`).
- **``applying`` field is velocity-based using NATAL speeds**
  (:data:`ketu.charts.CHART_DTYPE` ``body_speeds`` field) — both partner
  charts are static, the relative motion is ``speed_a - speed_b``.
- **Filtered-mode rows are canonically ordered by ``(body_a, body_b)``
  index ascending** — predictable for ML / oracle tests; callers may sort
  by ``|orb|`` post-hoc.
- **Dense mode uses ``aspect_type=-1`` and ``orb=NaN`` sentinels** for
  non-aspected pairs (mirrors Phase 14 :data:`ketu.charts.CHART_DTYPE`
  ``aspect_matrix`` convention).

See Also
--------
ketu.charts.compute_chart : Computes the per-partner CHART_DTYPE records
    consumed here (Phase 14 foundation).
ketu.synastry.orbs.resolve_orb_set : Preset resolver for the ``orbs=``
    parameter.
ketu.aspects.presets.resolve_aspect_set : Preset resolver for the
    ``aspects=`` parameter (re-used as-is).

Notes
-----
**UTC-only contract — LOUD.** Both ``chart_a`` and ``chart_b`` MUST have
been computed with UTC Julian Dates. Time-zone conversion is the caller's
responsibility; mixing local-time charts will produce incorrect aspects
with no error signal. This is the same loud invariant as the rest of Ketu
and is restated in the :func:`calculate_synastry` docstring per ROADMAP
success criterion #5.
"""
from __future__ import annotations

from typing import Literal, Tuple

import numpy as np

from ketu.aspects.presets import AspectSetSpec, resolve_aspect_set
from ketu.calculations import distance
from ketu.core import aspects as _ASPECTS

from .core import SYNASTRY_BODY_COUNT, SYNASTRY_DTYPE
from .orbs import OrbSetSpec, _BODY_ORBS_15, resolve_orb_set


def _extend_body_data(chart: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extend a CHART_DTYPE record's 13-body axis to the 15-body synastry axis.

    Concatenates the 13 canonical body longitudes and speeds from
    :data:`ketu.charts.CHART_DTYPE` with the scalar ``asc`` and ``mc``
    longitudes (indices 13 and 14), and zero speeds for ASC / MC.

    Parameters
    ----------
    chart : np.ndarray
        Scalar (0-d) structured array of :data:`ketu.charts.CHART_DTYPE`.

    Returns
    -------
    lons : np.ndarray
        Shape ``(15,)``, dtype ``float64``. Longitudes of the 13 canonical
        bodies followed by ASC and MC.
    speeds : np.ndarray
        Shape ``(15,)``, dtype ``float64``. Natal longitude speeds of the
        13 canonical bodies followed by ``0.0`` and ``0.0`` for ASC / MC.

    Notes
    -----
    ASC and MC have no per-day speed in the static natal-chart sense;
    assigning ``0.0`` propagates into the applying calculation as a
    zero contribution from the angle side. Angle-to-angle contacts
    (both sides ASC or MC) therefore have ``rel_speed = 0`` and are
    mechanically classified as ``applying=False``. An angle vs a planet
    has ``rel_speed = -planet_speed`` (or ``planet_speed`` when the
    angle is on partner B) and resolves applying/separating purely from
    the planet's natal motion sign and the signed ``delta``.
    """
    lons = np.concatenate([
        np.asarray(chart["body_lons"], dtype=np.float64),
        np.asarray([float(chart["asc"]), float(chart["mc"])], dtype=np.float64),
    ])
    speeds = np.concatenate([
        np.asarray(chart["body_speeds"], dtype=np.float64),
        np.zeros(2, dtype=np.float64),
    ])
    return lons, speeds


def calculate_synastry(
    chart_a: np.ndarray,
    chart_b: np.ndarray,
    aspects: AspectSetSpec = "classical",
    orbs: OrbSetSpec = "synastry",
    mode: Literal["dense", "filtered"] = "filtered",
) -> np.ndarray:
    """
    Compute inter-chart aspects between two natal charts.

    Returns a structured array of :data:`ketu.synastry.SYNASTRY_DTYPE`
    rows. In ``mode="filtered"`` (default), only aspected pairs appear,
    canonically ordered by ``(body_a, body_b)`` index ascending. In
    ``mode="dense"``, all 15 x 15 = 225 ordered pairs appear, with
    ``aspect_type=-1`` and ``orb=NaN`` (and ``orb_limit=NaN``,
    ``applying=False``) for non-aspected pairs.

    The Cartesian product is enumerated in full (NOT
    :func:`numpy.triu_indices`): self-pairs are INCLUDED per the locked
    CONTEXT.md decision because Sun_A<->Sun_B and Moon_A<->Moon_B are the
    canonical synastry aspects (ego and emotional compatibility), and
    ``(Sun_A, Mars_B)`` is semantically distinct from ``(Mars_A, Sun_B)``
    because chart-of-origin is part of the identity.

    Parameters
    ----------
    chart_a : np.ndarray
        Scalar (0-d) structured array of :data:`ketu.charts.CHART_DTYPE`
        for partner A (the "subject" chart in many synastry conventions).
    chart_b : np.ndarray
        Scalar (0-d) structured array of :data:`ketu.charts.CHART_DTYPE`
        for partner B.
    aspects : AspectSetSpec, optional
        Aspect-set spec passed through to
        :func:`ketu.aspects.presets.resolve_aspect_set`. Default
        ``"classical"`` (5 majors), aligned with the package-wide
        :data:`ketu.aspects.presets.CLASSICAL` default.
    orbs : OrbSetSpec, optional
        Orb tightening preset passed through to
        :func:`ketu.synastry.orbs.resolve_orb_set`. Default
        ``"synastry"`` applies factor 0.5 to the natal formula
        ``(orb_a + orb_b) / 2 * coef`` per Astrodienst convention
        (cited in :data:`ketu.synastry.orbs.SYNASTRY_FACTOR`).
        ``"classical"`` keeps the natal orbs unchanged for expert
        comparison views.
    mode : {"dense", "filtered"}, optional
        Output shape. ``"filtered"`` (default) returns only aspected
        rows; ``"dense"`` returns all 225 ordered pairs.

    Returns
    -------
    np.ndarray
        Structured array of :data:`ketu.synastry.SYNASTRY_DTYPE` rows.
        Filtered mode: shape ``(K,)`` with ``K <= 225``; dense mode:
        shape ``(225,)``.

    Raises
    ------
    ValueError
        If ``mode`` is not ``"dense"`` or ``"filtered"``; or if
        ``orbs`` / ``aspects`` is an unknown preset (propagated from
        :func:`ketu.synastry.orbs.resolve_orb_set` /
        :func:`ketu.aspects.presets.resolve_aspect_set`).

    See Also
    --------
    ketu.charts.compute_chart : Build CHART_DTYPE inputs.
    ketu.synastry.orbs.resolve_orb_set : Resolve the ``orbs=`` parameter.
    ketu.synastry.orbs.synastry_orb_limit : Per-pair orb formula (scalar
        form).
    ketu.aspects.presets.resolve_aspect_set : Resolve the ``aspects=``
        parameter.
    ketu.aspects.calculate_aspects_vectorized : Intra-chart aspect engine
        (single-chart counterpart).

    Notes
    -----
    **UTC ONLY.** Both ``chart_a`` and ``chart_b`` MUST have been
    computed with UTC Julian Dates. Time-zone conversion is the
    caller's responsibility; mixing local-time charts will produce
    incorrect aspects with no error signal.

    **Self-pairs INCLUDED.** The dense output contains all 225 ordered
    pairs ``(i, j)`` for ``i, j in [0, 15)``, including the 15 self-pairs
    where ``body_a == body_b`` (e.g. Sun_A<->Sun_B). These are the
    headline synastry aspects.

    **Body axis (15 bodies).** Indices 0..12 from :data:`ketu.core.bodies`
    (Sun, Moon, ..., Lilith), plus 13 = ASC and 14 = MC. The
    :data:`ketu.charts.CHART_DTYPE` ``cusps`` field (1..12) is **NOT**
    consulted (deferred to v1.3 if Phase 17 / 18 demand it).

    **Filtered row order.** Rows are sorted by ``(body_a * 15 + body_b)``
    ascending — canonical body-pair order, predictable for ML / oracle
    tests. Sort by ``|orb|`` post-hoc with
    ``result[np.argsort(np.abs(result["orb"]))]`` if needed.

    **Dense mode shape.** Always ``(225,)``. Non-aspected pairs carry
    ``aspect_type=-1``, ``orb=NaN``, ``orb_limit=NaN``,
    ``applying=False``.

    **Applying convention.** Velocity-based using
    :data:`ketu.charts.CHART_DTYPE` ``body_speeds``: the relative
    longitude motion is ``speed_a - speed_b`` and the aspect is
    applying when ``sign(delta) * (speed_a - speed_b) > 0``, where
    ``delta = aspect_angle - distance`` (signed; positive when the
    bodies are still approaching the exact aspect along the shorter arc).
    ASC and MC carry ``speed = 0`` by convention
    (see :func:`_extend_body_data`); angle-to-angle contacts
    (ASC <-> ASC, ASC <-> MC, MC <-> MC) therefore have ``rel_speed = 0``
    and are mechanically classified as ``applying=False``. An angle vs a
    planet (e.g. ASC_A <-> Moon_B) has ``rel_speed = -planet_speed`` and
    can be either applying or separating depending on ``sign(delta)``.

    Examples
    --------
    >>> from ketu.charts import compute_chart
    >>> from ketu.synastry import calculate_synastry
    >>> chart_a = compute_chart(2451545.0, 48.86, 2.35)  # doctest: +SKIP
    >>> chart_b = compute_chart(2451900.0, 40.71, -74.01)  # doctest: +SKIP
    >>> result = calculate_synastry(chart_a, chart_b)  # doctest: +SKIP
    >>> result.dtype.names[:3]  # doctest: +SKIP
    ('body_a', 'body_b', 'lon_a')
    """
    # 1. Resolve aspect mask + orb factor once at entry (single-call
    #    resolver pattern, mirrors ketu.aspects.calculator).
    mask = resolve_aspect_set(aspects)                 # length-14 bool
    factor = resolve_orb_set(orbs)                     # float scalar
    selected_indices = np.where(mask)[0]               # canonical aspect indices

    # 2. Extend both charts from 13 -> 15 body axis (add ASC, MC).
    lons_a, speeds_a = _extend_body_data(chart_a)      # (15,)
    lons_b, speeds_b = _extend_body_data(chart_b)      # (15,)

    # 3. Cross-product enumeration over the full Cartesian product
    #    (15 x 15 = 225 ordered pairs). NOT np.triu_indices — self-pairs
    #    and ordered pair semantics both matter (CONTEXT.md locked
    #    decision, RESEARCH.md Pitfall 1).
    n = SYNASTRY_BODY_COUNT
    i_idx, j_idx = np.indices((n, n))
    i_flat = i_idx.ravel()                             # shape (225,)
    j_flat = j_idx.ravel()                             # shape (225,)

    pos_a = lons_a[i_flat]
    pos_b = lons_b[j_flat]
    speed_a = speeds_a[i_flat]
    speed_b = speeds_b[j_flat]
    # ``distance`` is broadcast-typed Union[float, ndarray]; inputs are
    # shape (225,) so the result is always ``ndarray``. Cast explicitly
    # so the type checker can see the array branch.
    dist = np.asarray(distance(pos_a, pos_b), dtype=np.float64)  # (225,)

    # 4. Initialise the dense baseline with sentinels (-1 / NaN / False).
    out = np.empty(n * n, dtype=SYNASTRY_DTYPE)
    out["body_a"] = i_flat.astype(np.int8)
    out["body_b"] = j_flat.astype(np.int8)
    out["lon_a"] = pos_a
    out["lon_b"] = pos_b
    out["aspect_type"] = -1
    out["orb"] = np.nan
    out["applying"] = False
    out["orb_limit"] = np.nan

    # 5. First-aspect-wins matching, mirrors
    #    ketu.aspects.calculator:204 ``matched_pairs`` convention.
    matched = np.zeros(n * n, dtype=bool)

    for i_asp in selected_indices:
        i_asp_int = int(i_asp)
        ang = float(_ASPECTS["angle"][i_asp_int])
        coef = float(_ASPECTS["coef"][i_asp_int])

        # Per-pair orb limit (vectorised) with synastry factor applied.
        # Cast to float32 at write-time (out["orb_limit"] is f4) to keep
        # the SYNASTRY_DTYPE precision contract — Pitfall 6 ratchet.
        orbs_pair = (
            (_BODY_ORBS_15[i_flat] + _BODY_ORBS_15[j_flat]) / 2.0
            * coef
            * factor
        )

        if i_asp_int == 0:
            # Conjunction: in-orb iff distance is below the tolerance.
            # delta == -dist gives a signed orb whose sign matches the
            # "applying" convention (delta < 0 when separated past exact).
            in_orb = (dist <= orbs_pair) & (~matched)
            delta = -dist
        else:
            # Any other aspect: in-orb iff ``|dist - ang| <= orb_limit``.
            # delta = ang - dist matches the Phase 14 D-05 signed-orb
            # convention (positive when distance < aspect_angle).
            in_orb = (np.abs(dist - ang) <= orbs_pair) & (~matched)
            delta = ang - dist

        if not np.any(in_orb):
            continue

        # Applying: sign(delta) * relative_speed > 0.
        # Pitfall 4 ratchet: keep the SIGNED ``speed_a - speed_b`` form —
        # do NOT call np.abs on the speeds (that would silently flip
        # retrograde-body semantics).
        rel_speed = speed_a - speed_b
        applying = (np.sign(delta) * rel_speed) > 0

        out["aspect_type"][in_orb] = i_asp_int
        # f4 cast at write-time (Pitfall 6: SYNASTRY_DTYPE.orb is f4).
        out["orb"][in_orb] = delta[in_orb].astype(np.float32)
        out["applying"][in_orb] = applying[in_orb]
        # f4 cast at write-time (Pitfall 6: SYNASTRY_DTYPE.orb_limit is f4).
        out["orb_limit"][in_orb] = orbs_pair[in_orb].astype(np.float32)
        matched |= in_orb

    # 6. Mode dispatch.
    if mode == "dense":
        return out
    if mode == "filtered":
        return out[out["aspect_type"] >= 0]
    raise ValueError(
        f"unknown mode {mode!r}; expected 'dense' or 'filtered'"
    )


__all__ = [
    "calculate_synastry",
]
