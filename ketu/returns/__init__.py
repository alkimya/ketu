"""Returns subpackage — Solar and Lunar returns (standard + relocated).

Public API surface (RET-01..05 + LRET-01..05 of the v1.2 milestone):

- :func:`solar_return` — Resolve the moment when the Sun returns to its
  natal longitude in a given target year; assemble a CHART_DTYPE at
  the resolved instant (relocated to ``return_lat/lon`` if provided).
  Phase 18 Plan 02.
- :func:`lunar_return` — Resolve the FIRST moment ≥ ``target_jd`` when
  the Moon returns to its natal longitude (sidereal/tropical period
  ~27.32 d); assemble a CHART_DTYPE at the resolved instant.
  Phase 18 Plan 03.

Both functions share a single internal pure-NumPy bisection root-finder
(``ketu.returns._solve._solve_return``) — ROADMAP Phase 18 Success
Criterion #3 mandates this factorisation. Wrap-around 360°→0° is
handled centrally inside the helper via the signed-short-arc
residual ``((body_lon - natal_lon + 540) % 360) - 180`` (same
algebra as :func:`ketu.composite.circular_midpoint` and
``ketu.houses.porphyry``).

See Also
--------
ketu.charts.compute_chart : Assemble the CHART_DTYPE at the resolved
    return instant — both public functions call this under the hood.
ketu.composite.calculate_composite : Complementary pair-chart
    operation (midpoint composite of two natals).
ketu.synastry.calculate_synastry : Inter-chart aspect computation
    on the same CHART_DTYPE pair.

Notes
-----
**API asymmetry — LOUD.** :func:`solar_return` takes an integer
``target_year`` (calendar-anchored, one return per birthday-year).
:func:`lunar_return` takes a Julian Date ``target_jd`` (instant-
anchored) and returns the FIRST lunar return ≥ ``target_jd``. The
asymmetry is deliberate: solar returns are naturally birthday-keyed,
lunar returns are ~27.32 d-periodic so the caller must specify which
instant the search starts from. Both docstrings repeat this guard.

**UTC-only contract — LOUD.** ``natal_jd`` (and ``target_jd`` for
lunar) MUST be UTC Julian Dates. Time-zone conversion is the caller's
responsibility; mixing local-time JDs will produce incorrect returns
with no error signal.

**``natal_lat/lon`` vs ``return_lat/lon`` — distinguish LOUDLY.**

- ``natal_lat/lon`` are NEVER used for the root-finding: Sun and Moon
  geocentric longitudes are location-independent. They live on the
  signatures for symmetry / future-proofing only.
- ``return_lat/lon`` ARE used: they set the houses, ASC, MC, ARMC,
  Vertex of the return chart via
  ``compute_chart(jd_return, return_lat, return_lon, system)``.
  Passing ``return_lat=None`` (default) reuses ``natal_lat``;
  ``return_lon=None`` (default) reuses ``natal_lon``. This is the
  "standard return" case; non-None values produce a "relocated return".

**Polar relocation safety.** Both public functions call
``compute_chart`` with ``polar_fallback='porphyry'`` hard-wired. This
means extreme ``return_lat`` (Tromso, polar expeditions) does NOT
raise ``HighLatitudeError``. Use ``system='whole_sign'`` or
``system='equal'`` if you want non-Porphyry cusps at high latitudes.

**Aberration convention.** Ketu uses TRUE geocentric Sun/Moon
longitude (no aberration on body_ids 0/1, see
``ketu/ephemeris/planets.py:190``). Astro.com uses APPARENT longitude
(~20.5 arcsec aberration for Sun). The ~20 arcsec offset cancels in
the natal-to-return resolved-instant math (both sides use the same
convention), so the resolved instant agrees with Astro.com to
sub-second. Cross-tool deltas on individual body longitudes in the
return chart are within ~20 arcsec for Sun, sub-arcsec for Moon.
"""
from __future__ import annotations

__all__: list[str] = []  # solar_return and lunar_return land in Plans 18-02 and 18-03
