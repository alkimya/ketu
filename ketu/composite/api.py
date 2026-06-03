"""
Public compute surface for the composite subpackage — :func:`calculate_composite`.

Composition-only module: consumes two :data:`ketu.charts.CHART_DTYPE` scalar
records (Phase 14 foundation) and produces a third scalar :data:`ketu.charts.CHART_DTYPE`
whose body longitudes, ASC, MC, ARMC, and Vertex are circular midpoints of the
two natals, and whose house cusps are derived from the composite ASC and MC via
Porphyry-style trisection inlined here (NOT recomputed from any partner's
geographic context — COMP-03 binding).

Locked design decisions (Plan 17-02 + 17-RESEARCH §"House Computation Strategy"):

- **Approach A (Porphyry trisection on composite ASC + composite MC).** House
  cusps are derived geometrically from the composite ASC and composite MC via
  the same trisection algebra as :func:`ketu.houses.porphyry.porphyry_cusps`
  lines 159–186, inlined here. :func:`ketu.houses.calculate_houses` is NEVER
  called from this module (Pitfall 3 ratchet — COMP-03 anti-regression).
- **``system=`` is accept-and-ignore.** Validated via
  :func:`ketu.houses.registry.get_system` (raises ``ValueError`` on unknown
  systems for API symmetry with :func:`ketu.charts.compute_chart`), then the
  returned function is discarded. The user's ``system`` string is stored in
  the output's ``system`` field for bookkeeping only — every requested system
  collapses to the same Porphyry-style trisection under the pure midpoint
  method.
- **``(jd, lat, lon)`` storage is bookkeeping.** ``jd`` and ``lat`` are linear
  midpoints of the two natals; ``lon`` is a circular midpoint (geographic
  longitude IS circular). Documented LOUDLY as "bookkeeping, NOT a
  moment-and-place" — Davison composites would not generally preserve these
  exact midpoint relations (Pitfall 2 ratchet).
- **Body speeds are linear averages.** Informational only — a composite has
  no canonical instantaneous motion. Documented in the function's Notes block;
  preserves the :data:`ketu.charts.CHART_DTYPE` ``body_speeds`` ``f8`` /
  ``(13,)`` contract.
- **ARMC and Vertex are circular midpoints** of the two natal values.
- **Inline aspect-matching loop.** :func:`ketu.aspects.calculator.calculate_aspects_vectorized`
  takes a ``jd`` and recomputes bodies internally; the composite has no
  canonical Julian Date so the existing signature does not fit. Phase 17 keeps
  the blast radius zero on the Phase 9 aspect engine by inlining an aspect-matching
  loop semantically identical to the ``triu`` matching loop at
  :mod:`ketu.aspects.calculator` lines 187–260, with composite ``body_lons``
  substituted for the recomputed positions. A future refactor (Phase 18/19 may
  want it) could expose a ``body_lons=`` kwarg on
  :func:`calculate_aspects_vectorized` — TODO not owned by Phase 17.

See Also
--------
ketu.composite.circular_midpoint : The short-arc midpoint helper underpinning
    every per-body and per-angle midpoint.
ketu.charts.compute_chart : Computes the per-partner CHART_DTYPE records
    consumed here (Phase 14 foundation).
ketu.houses.porphyry.porphyry_cusps : Source of the trisection algebra
    inlined here (lines 159–186 of porphyry.py).
ketu.synastry.calculate_synastry : The complementary pair-chart operation
    on the same CHART_DTYPE pair.

Notes
-----
**UTC-only contract — LOUD.** Both ``chart_a`` and ``chart_b`` MUST have been
computed with UTC Julian Dates. Time-zone conversion is the caller's
responsibility; mixing local-time charts will produce incorrect midpoints with
no error signal. This is the same loud invariant as the rest of Ketu.

**No Davison.** This module does NOT compute Davison composites (fresh natal
chart at the temporal + spatial midpoint of two births). Davison is deferred
to v1.3 per :mod:`ketu.composite` Notes. No ``davison=`` kwarg exists on
:func:`calculate_composite`.
"""
from __future__ import annotations

import numpy as np

from ketu.aspects.presets import resolve_aspect_set
from ketu.calculations import distance
from ketu.charts import CHART_DTYPE
from ketu.core import aspects as _ASPECTS, bodies as _BODIES
from ketu.ephemeris.coordinates import (
    ecliptic_to_equatorial,
    rectangular_to_spherical,
    spherical_to_rectangular,
    true_obliquity,
)
from ketu.houses.registry import get_system

from .core import circular_midpoint

_BODY_COUNT = 14  # D-08 body axis (Sun..Chiron), v1.3 ratchet lifted to 14


def calculate_composite(
    chart_a: np.ndarray,
    chart_b: np.ndarray,
    system: str = "placidus",
) -> np.ndarray:
    """
    Compute a midpoint composite chart from two natal charts.

    Returns a scalar :data:`ketu.charts.CHART_DTYPE` whose body
    longitudes, ASC, MC, ARMC, and Vertex are circular midpoints of
    the two natals, and whose house cusps are derived from the
    composite ASC and MC via Porphyry-style trisection (NOT recomputed
    from any partner's geographic context — COMP-03 binding).

    Parameters
    ----------
    chart_a : np.ndarray
        Scalar (0-d) structured array of :data:`ketu.charts.CHART_DTYPE`
        produced by :func:`ketu.charts.compute_chart`. MUST have been
        computed with a UTC Julian Date.
    chart_b : np.ndarray
        Scalar (0-d) structured array of :data:`ketu.charts.CHART_DTYPE`
        produced by :func:`ketu.charts.compute_chart`. MUST have been
        computed with a UTC Julian Date.
    system : str, default ``"placidus"``
        House system name. Validated against
        :data:`ketu.houses.registry.SYSTEMS` (raises ``ValueError``
        on unknown names, for API symmetry with
        :func:`ketu.charts.compute_chart`). **Stored in the output's
        ``system`` field for bookkeeping, but semantically a no-op
        under the pure midpoint method** — every requested system
        collapses to the same Porphyry-style trisection of (composite
        ASC, composite MC). If you need Placidus-flavoured composite
        cusps, use the reference-place method externally; it is not
        implemented in Phase 17.

    Returns
    -------
    np.ndarray
        Scalar (0-d) structured array of
        :data:`ketu.charts.CHART_DTYPE`.

    Raises
    ------
    ValueError
        If ``system`` is not a registered house system name.

    See Also
    --------
    ketu.composite.circular_midpoint : The short-arc midpoint helper.
    ketu.charts.compute_chart : Build the per-partner CHART_DTYPE
        inputs.
    ketu.charts.CHART_DTYPE : The frozen output dtype.
    ketu.synastry.calculate_synastry : The complementary pair-chart
        operation on the same CHART_DTYPE pair.

    Notes
    -----
    **Midpoint method only.** ``body_lons``, ``asc``, ``mc``, ``armc``,
    ``vertex``, and ``lon`` are circular midpoints of the two natals;
    ``body_lats``, ``body_speeds``, ``jd``, and ``lat`` are linear
    averages of the two natals. House cusps 2/3/5/6/8/9/11/12 are
    derived from the composite ASC and MC via Porphyry-style
    trisection inlined in this module (the algebra is the same as
    :func:`ketu.houses.porphyry.porphyry_cusps` lines 159–186 with
    composite ASC/MC substituted for the closed-form derivation).

    **(jd, lat, lon) on a composite are bookkeeping, NOT a
    moment-and-place.** They are stored as midpoints of the two
    natals for round-trip consistency. They have NO astronomical
    interpretation as "the moment-and-place of the composite" — that
    interpretation requires a Davison composite, which is out of
    scope for Phase 17 (deferred to v1.3 — see module docstring).

    **Body speeds.** ``body_speeds`` are linear averages of the two
    natal speeds and have no physical interpretation as "the
    composite's instantaneous longitude motion." They are stored for
    dtype contract compatibility (:data:`ketu.charts.CHART_DTYPE`
    ``body_speeds`` must be ``f8`` shape ``(13,)``); downstream
    consumers that need a physical speed should consult the
    per-partner natal speeds directly.

    **UTC-only contract — LOUD.** Both ``chart_a`` and ``chart_b``
    MUST have been computed with UTC Julian Dates. Mixing
    local-time charts produces incorrect midpoints with no error
    signal (same loud invariant as the rest of Ketu).

    **No Davison.** This function does NOT compute a Davison
    composite (time + space midpoint chart computed as a fresh
    natal). Davison is deferred to v1.3 — see module docstring's
    Notes section. No ``davison=`` kwarg exists; do not request one.

    **Aspect set.** The composite's intra-chart ``aspect_matrix`` /
    ``aspect_orbs`` are computed against the CLASSICAL aspect preset
    (5 majors: conjunction, sextile, square, trine, opposition). This
    matches the package-wide :data:`ketu.aspects.presets.CLASSICAL`
    default; the composite signature deliberately omits an
    ``aspects=`` parameter (COMP-01..04 do not mention it).

    **Accuracy vs Swiss Ephemeris.** Composite body longitudes are
    circular midpoints of two natal positions, each accurate to ±0.1°
    (inner planets) or ±0.5° (outer). The composite itself carries
    the same error budget plus up to ~0.1° of short-arc midpoint
    rounding (floating-point exact to ~1 ulp). House cusps are derived
    from composite ASC/MC via Porphyry trisection (±0.01°). Swiss-
    based composite tools may differ by similar amounts depending on
    their midpoint convention.

    **Supported date range.** Inherits the natal-chart constraint:
    1800–2200 CE for both partner charts. Accuracy degrades outside
    this range.

    **Edge cases.** If both partners' ASC values are exactly 180°
    apart, the composite ASC is defined as 0° by convention (see
    :func:`ketu.composite.circular_midpoint` antipodal pin). Geographic
    ``lon`` is the circular midpoint (e.g. 170°E and 170°W give 180°).

    Examples
    --------
    >>> import numpy as np
    >>> from ketu.charts import compute_chart
    >>> from ketu.composite import calculate_composite
    >>> chart_a = compute_chart(2451545.0, 48.86, 2.35)
    >>> chart_b = compute_chart(2451900.0, 40.71, -74.01)
    >>> comp = calculate_composite(chart_a, chart_b)
    >>> comp["body_lons"].shape
    (14,)
    >>> comp["cusps"].shape
    (12,)
    """
    # 1. Validate system= (raises ValueError on unknown); discard return
    #    value. Approach A no-op semantics — every system collapses to
    #    Porphyry-style trisection regardless of the user's request.
    get_system(system)  # validation only; ValueError on unknown name

    # 2. Allocate output as scalar CHART_DTYPE (shape () — 0-d structured
    #    array). NEVER call compute_chart here (Pitfall 2 anti-regression
    #    ratchet — a Davison implementation would).
    out = np.zeros((), dtype=CHART_DTYPE)

    # 3. Bookkeeping fields (linear / circular midpoints — documented as
    #    "NOT a moment-and-place" in the Notes block above).
    out["jd"] = (float(chart_a["jd"]) + float(chart_b["jd"])) / 2.0
    out["lat"] = (float(chart_a["lat"]) + float(chart_b["lat"])) / 2.0
    out["lon"] = float(
        circular_midpoint(float(chart_a["lon"]), float(chart_b["lon"]))
    )
    out["system"] = system  # bookkeeping; semantically a no-op (Approach A)

    # 4. Body axis — vectorised over the frozen (13,) axis. Pitfall 8
    #    ratchet via the shape itself; the index-0 = Sun convention is
    #    inherited from the natal CHART_DTYPE ``body_lons`` field.
    out["body_lons"] = circular_midpoint(
        chart_a["body_lons"], chart_b["body_lons"]
    )
    out["body_lats"] = (
        np.asarray(chart_a["body_lats"], dtype=np.float64)
        + np.asarray(chart_b["body_lats"], dtype=np.float64)
    ) / 2.0
    out["body_speeds"] = (
        np.asarray(chart_a["body_speeds"], dtype=np.float64)
        + np.asarray(chart_b["body_speeds"], dtype=np.float64)
    ) / 2.0
    # Derive body_decl from the composite λ,β that were just assigned — the
    # self-consistent derivation (δ of the composite midpoint chart, NOT a
    # midpoint of the parents' declinations). Open Question 1 resolved to
    # option (a): parallel to how body_lats is the midpoint of the ecliptic
    # latitudes, body_decl is derived via the full coordinates chain on the
    # composite λ,β. This is the same path used in compute_chart (Plan 02).
    _eps = true_obliquity(float(out["jd"]))  # scalar ε for composite jd
    _x, _y, _z = spherical_to_rectangular(
        np.asarray(out["body_lons"], dtype=np.float64),
        np.asarray(out["body_lats"], dtype=np.float64),
        1.0,
    )
    _xe, _ye, _ze = ecliptic_to_equatorial(_x, _y, _z, _eps)
    _, _decl, _ = rectangular_to_spherical(_xe, _ye, _ze)
    out["body_decl"] = _decl  # shape (14,) — δ ∈ [−90, +90]°, north positive

    # 5. Angles — circular midpoints. ARMC and Vertex stored for
    #    bookkeeping; ASC and MC drive the house-cusp trisection in
    #    step 6.
    composite_asc = float(
        circular_midpoint(float(chart_a["asc"]), float(chart_b["asc"]))
    )
    composite_mc = float(
        circular_midpoint(float(chart_a["mc"]), float(chart_b["mc"]))
    )
    out["armc"] = float(
        circular_midpoint(float(chart_a["armc"]), float(chart_b["armc"]))
    )
    out["vertex"] = float(
        circular_midpoint(float(chart_a["vertex"]), float(chart_b["vertex"]))
    )

    # 6. Porphyry-style trisection on (composite_asc, composite_mc).
    #    Verbatim algebra from ketu/houses/porphyry.py:159-186; polar
    #    ASC swap kept so high-latitude pairs don't produce a "wrong
    #    quadrant" ASC. NEVER call calculate_houses here (Pitfall 3
    #    anti-regression ratchet — COMP-03 binding).
    acmc_signed = ((composite_asc - composite_mc + 540.0) % 360.0) - 180.0
    if acmc_signed < 0.0:
        composite_asc = (composite_asc + 180.0) % 360.0
        acmc = acmc_signed + 180.0
    else:
        acmc = acmc_signed
    composite_ic = (composite_mc + 180.0) % 360.0
    composite_desc = (composite_asc + 180.0) % 360.0
    upper_step = acmc / 3.0
    lower_step = (180.0 - acmc) / 3.0
    cusp_11 = (composite_mc + upper_step) % 360.0
    cusp_12 = (composite_mc + 2.0 * upper_step) % 360.0
    cusp_2 = (composite_asc + lower_step) % 360.0
    cusp_3 = (composite_asc + 2.0 * lower_step) % 360.0
    cusp_5 = (cusp_11 + 180.0) % 360.0
    cusp_6 = (cusp_12 + 180.0) % 360.0
    cusp_8 = (cusp_2 + 180.0) % 360.0
    cusp_9 = (cusp_3 + 180.0) % 360.0
    out["cusps"] = np.array(
        [
            composite_asc, cusp_2, cusp_3, composite_ic,
            cusp_5, cusp_6, composite_desc, cusp_8,
            cusp_9, composite_mc, cusp_11, cusp_12,
        ],
        dtype=np.float64,
    )
    out["asc"] = composite_asc
    out["mc"] = composite_mc

    # 7. Aspect matrix — inline aspect-matching loop on composite
    #    body_lons. The existing intra-chart aspect engine
    #    (ketu.aspects.calculator) takes a Julian Date and recomputes
    #    bodies internally; the composite has no canonical jd, so we
    #    inline the matching algebra here. The inline loop is
    #    semantically identical to the engine's triu loop
    #    (calculator.py:187-260) with body positions substituted by the
    #    already-computed composite body_lons. We hardcode the
    #    CLASSICAL aspect preset (5 majors) because the composite
    #    signature deliberately omits an ``aspects=`` parameter
    #    (COMP-01..04 don't mention it; matches the package-wide
    #    default).
    composite_lons = out["body_lons"]
    aspect_matrix = np.full((_BODY_COUNT, _BODY_COUNT), -1, dtype=np.int8)
    aspect_orbs = np.full((_BODY_COUNT, _BODY_COUNT), np.nan, dtype=np.float32)
    body_orbs = _BODIES["orb"]  # shape (13,)
    aspect_angles = _ASPECTS["angle"]  # shape (14,)
    aspect_coefs = _ASPECTS["coef"]  # shape (14,)
    # Single source of truth for the classical mask (5 majors):
    # ketu.aspects.presets.resolve_aspect_set; imported at module top.
    classical_mask = resolve_aspect_set("classical")
    selected_indices = np.where(classical_mask)[0]

    for i in range(_BODY_COUNT):
        for j in range(i + 1, _BODY_COUNT):
            dist = float(distance(composite_lons[i], composite_lons[j]))
            for i_asp in selected_indices:
                aspect_angle = float(aspect_angles[i_asp])
                aspect_coef = float(aspect_coefs[i_asp])
                pair_orb = (
                    (float(body_orbs[i]) + float(body_orbs[j])) / 2.0
                    * aspect_coef
                )
                if i_asp == 0:  # Conjunction
                    if dist <= pair_orb:
                        # Sign convention: conjunction uses raw distance
                        # (calculator.py:223). Match-once-per-pair via break.
                        signed_orb = dist
                        aspect_matrix[i, j] = int(i_asp)
                        aspect_matrix[j, i] = int(i_asp)
                        aspect_orbs[i, j] = signed_orb
                        aspect_orbs[j, i] = signed_orb
                        break
                else:
                    if aspect_angle - pair_orb <= dist <= aspect_angle + pair_orb:
                        # Sign convention: non-conjunction uses
                        # ``aspect_angle - distance`` (calculator.py:229).
                        signed_orb = aspect_angle - dist
                        aspect_matrix[i, j] = int(i_asp)
                        aspect_matrix[j, i] = int(i_asp)
                        aspect_orbs[i, j] = signed_orb
                        aspect_orbs[j, i] = signed_orb
                        break

    out["aspect_matrix"] = aspect_matrix
    out["aspect_orbs"] = aspect_orbs

    return out


__all__ = [
    "calculate_composite",
]
