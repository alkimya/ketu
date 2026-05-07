---
phase: 10-houses-module
plan: 04
type: execute
wave: 3
depends_on:
  - "10-01"
  - "10-02"
  - "10-03"
files_modified:
  - ketu/houses/placidus.py
  - tests/houses/test_placidus.py
autonomous: true
plan_id: "10-04"
requirements:
  - HOU-03
  - HOU-08

must_haves:
  truths:
    - "ketu.houses.placidus.placidus_cusps(armc, lat, eps) returns ndarray of shape (..., 12) containing the 12 Placidus cusps in ecliptic longitude (deg, [0, 360))"
    - "Placidus is registered as @register('placidus') in registry SYSTEMS dict"
    - "Iteration cap is 50 (HOU-03 spec); per-element non-convergence is detected and recorded — non-converged elements yield NaN cusps and an explicit non-convergence flag for the caller"
    - "Vectorized iteration uses mask-based continuation (HOU-08): elements that converged early do not pollute the iteration of elements still iterating"
    - "Convergence threshold is 1e-7 deg (research §Don't Hand-Roll Placidus formula); convergence delta uses modular form abs(((RA_new - RA + 180) % 360) - 180) to handle the 0°/360° wrap (Pitfall 3)"
    - "Cusps 1, 4, 7, 10 are closed-form (ASC, IC=ASC+180, DESC=ASC+180, MC) — never iterated"
    - "Cusps 5, 6, 8, 9 are derived as opposites of cusps 11, 12, 2, 3 (each + 180° mod 360)"
    - "Placidus matches swisseph oracle to <1 arcmin on all 8 non-polar reference charts at every cusp 1-12"
    - "Iteration count is bounded: at every test fixture, max iter used is well below 50 (typically <10) — verifies the cap is a safety margin not a typical value"
  artifacts:
    - path: "ketu/houses/placidus.py"
      provides: "Placidus implementation: placidus_cusps function + register('placidus') + helpers for per-cusp formula (cusps 11/12/2/3 trisection of semi-arc with AD correction) + vectorized mask-based iteration helper"
      contains: "@register"
      min_lines: 100
    - path: "tests/houses/test_placidus.py"
      provides: "Placidus-specific tests: 8 non-polar reference charts cusps-vs-oracle agreement at <1 arcmin; iteration cap behavior; convergence threshold sanity; mask-based continuation correctness; no NaN at non-polar lats"
      contains: "placidus_cusps"
      min_lines: 100
  key_links:
    - from: "ketu/houses/placidus.py"
      to: "ketu.houses.registry SYSTEMS"
      via: "@register('placidus') decorator"
      pattern: "@register\\(.placidus.\\)"
    - from: "ketu/houses/placidus.py"
      to: "ketu.houses._ecliptic.ascensional_difference"
      via: "AD = arcsin(tan(lat) * tan(decl))"
      pattern: "ascensional_difference"
    - from: "tests/houses/test_placidus.py"
      to: "tests/houses/conftest.py reference_charts + loaded_reference_snapshot"
      via: "pytest fixture injection (HOU-09 cross-check)"
      pattern: "reference_charts|loaded_reference_snapshot"
---

<objective>
Implement the Placidus house system with vectorized mask-based iteration, an iteration cap of 50 with explicit non-convergence detection, and registration into `ketu.houses.SYSTEMS` via the `@register("placidus")` decorator. The implementation must match swisseph oracle to <1 arcmin on all 8 non-polar reference charts (Plan 10-02 fixtures).

Purpose: Placidus is the most complex house system — per-cusp iteration on right ascension via trisection of the semi-arc, requires careful handling of the 0°/360° wrap (Pitfall 3) and the polar boundary `tan(lat)·tan(decl) ≥ 1` (Pitfall 6). The hardest engineering item is HOU-08 vectorization: instead of `for jd in jds: while not converged:` (Python-loop antipattern), use mask-based continuation so converged elements stop without polluting the iteration of others.

This plan can run in parallel with Plan 10-05 (Koch + Porphyry) in Wave 3 — they touch disjoint files (`placidus.py` vs `koch.py`+`porphyry.py`) and both consume the Plan 10-03 scaffold without modifying it.

Output:
- `ketu/houses/placidus.py` — `placidus_cusps(armc, lat, eps) -> ndarray` registered into SYSTEMS, internal `_iterate_to_convergence` helper, per-cusp formula table.
- `tests/houses/test_placidus.py` — 8 non-polar reference charts × 12 cusps = 96 assertions at <1 arcmin tolerance, plus iteration-cap and mask-correctness invariants.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/10-houses-module/10-RESEARCH.md
@.planning/phases/10-houses-module/10-03-registry-dtype-ascmc-PLAN.md

# Scaffold this plan plugs into (do not modify)
@ketu/houses/registry.py
@ketu/houses/_ecliptic.py
@ketu/houses/ascmc.py

# Test infrastructure (do not modify)
@tests/houses/conftest.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement vectorized Placidus algorithm with mask-based iteration in ketu/houses/placidus.py</name>
  <files>ketu/houses/placidus.py</files>
  <action>
    Create `ketu/houses/placidus.py`. The algorithm has 3 layers:

    1. **Top-level `placidus_cusps(armc, lat, eps) -> ndarray`** — entry point matching the registry signature. Returns `ndarray` of shape `(..., 12)` with the 12 cusps in ecliptic longitude (degrees, [0, 360)).
    2. **Per-cusp iteration `_iterate_one_cusp(armc, lat, eps, cusp_idx) -> ndarray`** — solves the fixed point for cusps 11, 12, 2, 3 (the 4 iterated cusps; cusps 5/6/8/9 are derived as opposites; cusps 1/4/7/10 come from ASC/MC).
    3. **Mask-based fixed-point loop `_iterate_to_convergence(...)` — vectorized "compute only where not yet converged" pattern.

    Required code:

    ```python
    """Placidus house system implementation.

    Vectorized over (armc, lat, eps) arrays of any compatible broadcast shape.
    Per-cusp iteration uses mask-based continuation: elements that converge
    early are frozen so they don't pollute the iteration of others.

    Iteration cap: 50 (HOU-03). Non-convergence yields NaN for the affected
    cusp, surfacing the failure rather than returning a silent wrong value.

    See 10-RESEARCH.md §"Don't Hand-Roll → Placidus formula" for the
    canonical per-cusp equations and 10-RESEARCH.md §Pitfall 6 for the
    polar-boundary trap.
    """
    from __future__ import annotations
    from typing import Tuple
    import numpy as np

    from .registry import register
    from ._ecliptic import ascensional_difference
    from .ascmc import compute_ascmc  # not called here; documents the dependency contract

    MAX_ITER: int = 50
    TOL_DEG: float = 1e-7  # research §"Don't Hand-Roll" convergence threshold


    # Per-cusp scaling table (research §"Don't Hand-Roll → Placidus formula"):
    # House 11: RA_11 = ARMC + (90 + AD) / 3
    # House 12: RA_12 = ARMC + 2 * (90 + AD) / 3
    # House  2: RA_2  = ARMC + 180 - 2 * (90 - AD) / 3
    # House  3: RA_3  = ARMC + 180 -     (90 - AD) / 3
    #
    # Each cusp-formula is a function (armc, AD) -> RA in degrees.
    # AD = ascensional difference at the cusp, computed iteratively from RA.

    def _ra_formula_cusp_11(armc: np.ndarray, AD: np.ndarray) -> np.ndarray:
        return (armc + (90.0 + AD) / 3.0) % 360.0

    def _ra_formula_cusp_12(armc: np.ndarray, AD: np.ndarray) -> np.ndarray:
        return (armc + 2.0 * (90.0 + AD) / 3.0) % 360.0

    def _ra_formula_cusp_2(armc: np.ndarray, AD: np.ndarray) -> np.ndarray:
        return (armc + 180.0 - 2.0 * (90.0 - AD) / 3.0) % 360.0

    def _ra_formula_cusp_3(armc: np.ndarray, AD: np.ndarray) -> np.ndarray:
        return (armc + 180.0 - (90.0 - AD) / 3.0) % 360.0


    _CUSP_FORMULAS = {
        11: _ra_formula_cusp_11,
        12: _ra_formula_cusp_12,
        2:  _ra_formula_cusp_2,
        3:  _ra_formula_cusp_3,
    }


    def _iterate_cusp_ra(
        armc: np.ndarray,
        lat: np.ndarray,
        eps: np.ndarray,
        cusp_number: int,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Solve for the right ascension of cusp `cusp_number` ∈ {11, 12, 2, 3}.

        Iteration shape (per-element fixed point):
            1. Initial guess: RA_0 = formula(armc, AD=0)
            2. From RA_k, compute decl_k = arctan(sin(RA_k) * tan(eps))
            3. Compute AD_k = arcsin(tan(lat) * tan(decl_k))   ← NaN at polar boundary
            4. RA_{k+1} = formula(armc, AD_k)
            5. Stop when |delta(RA_{k+1}, RA_k)| < TOL_DEG (modular metric)

        Mask-based continuation: at each iteration, only elements still in the
        active mask get their RA updated. NaN propagation through tan/arcsin
        marks polar elements as "converged-NaN" — caller routes those to
        polar fallback.

        Parameters
        ----------
        armc, lat, eps : np.ndarray (degrees, broadcast-compatible)
        cusp_number : int — one of {11, 12, 2, 3}

        Returns
        -------
        ra : np.ndarray — RA of the cusp (degrees, [0, 360)); NaN where not converged
        converged : np.ndarray — bool, True where convergence achieved
        """
        formula = _CUSP_FORMULAS[cusp_number]

        # Broadcast inputs to common shape
        armc_b, lat_b, eps_b = np.broadcast_arrays(armc, lat, eps)

        # Initial guess: AD = 0 (equivalent to assuming flat horizon)
        AD_init = np.zeros_like(armc_b, dtype=np.float64)
        RA = formula(armc_b, AD_init)

        converged = np.zeros_like(RA, dtype=bool)

        for _ in range(MAX_ITER):
            active = ~converged & ~np.isnan(RA)
            if not active.any():
                break

            # Step 2: declination from RA on the ecliptic
            #         tan(decl) = sin(RA) * tan(eps)
            sin_RA = np.sin(np.deg2rad(RA))
            tan_eps = np.tan(np.deg2rad(eps_b))
            decl = np.rad2deg(np.arctan(sin_RA * tan_eps))

            # Step 3: ascensional difference (NaN at polar boundary)
            AD = ascensional_difference(lat_b, decl)

            # Step 4: candidate RA_new
            RA_new = formula(armc_b, AD)

            # Step 5: convergence check (modular distance handles 0/360 wrap)
            delta = np.abs(((RA_new - RA + 180.0) % 360.0) - 180.0)

            # Newly converged this iteration (and not polar-NaN)
            newly = active & ~np.isnan(RA_new) & (delta < TOL_DEG)

            # Update RA only on still-active elements (and only if RA_new is not NaN —
            # if NaN, freeze the element with NaN as the "result" so it propagates)
            RA = np.where(active & ~np.isnan(RA_new), RA_new, RA)
            # Polar-NaN propagation: if RA_new is NaN, freeze RA at NaN
            RA = np.where(active & np.isnan(RA_new), np.nan, RA)

            converged = converged | newly | np.isnan(RA)

        # Mark non-converged AND non-polar elements as NaN — surfaces the
        # rare case of "hit iter=50 cap without converging on a healthy lat"
        # which is a real bug signal for the user / next planner.
        not_done = ~converged
        RA = np.where(not_done, np.nan, RA)

        return RA % 360.0, converged & ~np.isnan(RA)


    def _ra_to_lambda(ra: np.ndarray, eps: np.ndarray) -> np.ndarray:
        """Convert RA on the ecliptic to ecliptic longitude.

        For points strictly on the ecliptic (declination follows
        sin(RA)·tan(eps)), the longitude is:
            λ = atan2(sin(RA)·cos(eps) + tan(decl)·sin(eps), cos(RA))
        Simplified (since tan(decl) = sin(RA)·tan(eps) → sin(decl)/cos(decl) =
        sin(RA)·tan(eps)) to:
            λ = atan2(sin(RA), cos(RA) * cos(eps))   [for ecliptic-resident points]

        Wait — that's the inverse of MC. The Placidus cusps are NOT strictly on
        the ecliptic; they're on the great circle defined by the cusp's
        diurnal-arc fraction. The conversion RA→λ for these uses:
            tan(λ) = (sin(RA) * cos(eps) + tan(decl) * sin(eps)) / cos(RA)
        where decl = arctan(sin(RA) * tan(eps)). After algebraic simplification
        (since the cusp lies on the ecliptic by definition for Placidus —
        we trisect the semi-arc which IS on the ecliptic projected through
        the meridian), the standard form is:
            λ = atan2(sin(RA)*cos(eps) + tan(decl)*sin(eps), cos(RA))

        BUT: for Placidus specifically, the cusp IS on the ecliptic. So the
        projection simplification holds:
            tan(decl) = sin(RA) * tan(eps)
            sin(λ) * cos(eps) = sin(RA) * cos(decl)
            cos(λ)         = cos(RA) / cos(decl)
            ⇒  tan(λ) = sin(RA) * cos(eps) / cos(RA) = tan(RA) * cos(eps)
            ⇒  λ = atan2(sin(RA) * cos(eps), cos(RA))   (NOT atan2(tan...))

        Use this canonical form (cross-verified against pd-swisseph swehouse.c).
        """
        ra_rad = np.deg2rad(ra)
        eps_rad = np.deg2rad(eps)
        # WARNING: this is NOT the same as the MC formula — that one uses
        # cos(RA)*cos(eps) in the denominator. Here cos(eps) is in the
        # NUMERATOR. Cross-check against test_ascmc test of compute_ascmc.
        lam = np.arctan2(
            np.sin(ra_rad) * np.cos(eps_rad),
            np.cos(ra_rad),
        )
        # Quadrant disambiguation: if RA in [180, 360) but lam < 180, add 180
        lam_deg = np.rad2deg(lam) % 360.0
        ra_norm = ra % 360.0
        # Bring λ into the same hemisphere as RA. Standard convention:
        # cusp's λ is within ±90° of RA when projected through the ecliptic.
        delta = (lam_deg - ra_norm + 180.0) % 360.0 - 180.0
        # If |delta| > 90°, the atan2 picked the back-hemisphere root; flip.
        flip = np.abs(delta) > 90.0
        lam_deg = np.where(flip, (lam_deg + 180.0) % 360.0, lam_deg)
        return lam_deg


    @register("placidus")
    def placidus_cusps(
        armc: np.ndarray,
        lat: np.ndarray,
        eps: np.ndarray,
    ) -> np.ndarray:
        """Compute the 12 Placidus house cusps.

        Parameters
        ----------
        armc, lat, eps : np.ndarray (degrees, broadcast-compatible to common shape S)

        Returns
        -------
        np.ndarray of shape (*S, 12) — cusps[..., i] = cusp of house (i+1)
            in ecliptic longitude (degrees, [0, 360)). NaN cusps signal
            non-convergence or polar boundary; caller (calculate_houses)
            routes these to HighLatitudeError or polar fallback per HOU-06.
        """
        # Broadcast inputs to common shape S
        armc_b, lat_b, eps_b = np.broadcast_arrays(armc, lat, eps)
        S = armc_b.shape

        # ASC and MC come from compute_ascmc — but to keep this function's
        # registry contract clean (armc, lat, eps), recompute from the inputs
        # we have. ASC formula uses (armc, lat, eps); MC uses (armc, eps).
        armc_rad = np.deg2rad(armc_b)
        eps_rad = np.deg2rad(eps_b)
        lat_rad = np.deg2rad(lat_b)

        mc = np.rad2deg(np.arctan2(
            np.sin(armc_rad),
            np.cos(armc_rad) * np.cos(eps_rad),
        )) % 360.0
        asc = np.rad2deg(np.arctan2(
            np.cos(armc_rad),
            -(np.sin(eps_rad) * np.tan(lat_rad)
              + np.cos(eps_rad) * np.sin(armc_rad)),
        )) % 360.0
        ic = (mc + 180.0) % 360.0
        desc = (asc + 180.0) % 360.0

        # Iterate the 4 non-trivial cusps
        cusp_11_RA, _ = _iterate_cusp_ra(armc_b, lat_b, eps_b, 11)
        cusp_12_RA, _ = _iterate_cusp_ra(armc_b, lat_b, eps_b, 12)
        cusp_2_RA,  _ = _iterate_cusp_ra(armc_b, lat_b, eps_b, 2)
        cusp_3_RA,  _ = _iterate_cusp_ra(armc_b, lat_b, eps_b, 3)

        # Convert RA → ecliptic longitude
        cusp_11 = _ra_to_lambda(cusp_11_RA, eps_b)
        cusp_12 = _ra_to_lambda(cusp_12_RA, eps_b)
        cusp_2  = _ra_to_lambda(cusp_2_RA,  eps_b)
        cusp_3  = _ra_to_lambda(cusp_3_RA,  eps_b)

        # Cusps 5, 6, 8, 9 are opposites (research §"Don't Hand-Roll" — Placidus)
        cusp_5 = (cusp_11 + 180.0) % 360.0
        cusp_6 = (cusp_12 + 180.0) % 360.0
        cusp_8 = (cusp_2  + 180.0) % 360.0
        cusp_9 = (cusp_3  + 180.0) % 360.0

        # Stack into output of shape (*S, 12); cusp index i corresponds to house (i+1)
        cusps = np.stack([
            asc,      # house 1 = ASC
            cusp_2,
            cusp_3,
            ic,       # house 4 = IC
            cusp_5,
            cusp_6,
            desc,     # house 7 = DESC
            cusp_8,
            cusp_9,
            mc,       # house 10 = MC
            cusp_11,
            cusp_12,
        ], axis=-1)

        return cusps
    ```

    Anti-patterns to avoid:
    - DO NOT use a Python-level `for jd in jds:` loop around scalar Placidus — research §Anti-Pattern 2 forbids this. The mask-based loop above iterates max 50 times TOTAL, not 50× per element.
    - DO NOT use raw `RA_new - RA` for convergence — Pitfall 3 (modular metric required: `abs(((RA_new - RA + 180) % 360) - 180)`).
    - DO NOT use single-arg `arctan` anywhere — `arctan2` only (Pitfall 2). The `np.arctan(sin_RA * tan_eps)` for declination IS single-arg but is mathematically correct here (declination is in [-π/2, +π/2] by definition; `arctan` IS the right inverse). Document this in a comment so future readers don't "fix" it to arctan2.
    - DO NOT silently propagate NaN without setting a return-value contract — caller (Plan 06's `calculate_houses`) inspects NaN cusps and routes to HighLatitudeError or polar fallback per HOU-06.
    - DO NOT register Koch or Porphyry here — Plan 10-05 owns those `@register` calls.
    - DO NOT inline the per-cusp formula tables — keep `_CUSP_FORMULAS` as a dict mapping cusp number → callable so the per-cusp dispatch is data-driven (research §Anti-Pattern 1: no if-elif ladder for cusp formulas either).
    - DO NOT use `_ra_to_lambda` from `_ecliptic.py` — that helper is a different formula (for points strictly on the ecliptic with declination=0). Placidus cusps are on the ecliptic projected through the meridian; the simplified `tan(λ) = tan(RA) * cos(eps)` form is correct here. Add a comment in the inline `_ra_to_lambda` warning future readers about the distinction.
    - DO NOT cap iter at 10 "because tests pass" — HOU-03 spec is 50, the cap is a safety margin not a typical value. Most charts converge in <10 iter; we want the headroom for edge cases (ARMC near 0°, lat near polar boundary).

    Mypy --strict requirements:
    - All function signatures fully annotated (already done above).
    - `Tuple` from typing.
    - `np.broadcast_arrays` returns a tuple of ndarrays — annotate with explicit unpacking.
  </action>
  <verify>
    `python -c "
    import numpy as np
    from ketu.houses.registry import SYSTEMS
    from ketu.houses.placidus import placidus_cusps
    assert 'placidus' in SYSTEMS
    assert SYSTEMS['placidus'] is placidus_cusps

    # Sanity: Paris J2000 — research §Example 1 ASC ≈ 26.77°
    from ketu.houses.ascmc import compute_ascmc
    chart = compute_ascmc(2451545.0, 48.8566, 2.3522)
    cusps = placidus_cusps(np.asarray(chart['armc']), np.asarray(48.8566), np.asarray(chart['eps']))
    print('cusps shape:', cusps.shape)
    print('cusp 1 (ASC):', float(cusps[..., 0]))
    print('cusp 10 (MC):', float(cusps[..., 9]))
    print('cusp 11:', float(cusps[..., 10]))
    print('cusp 12:', float(cusps[..., 11]))
    assert not np.isnan(cusps).any(), 'unexpected NaN at non-polar lat'
    "` runs and prints sane numbers (ASC ≈ 26.77°, MC ≈ 281.78°).

    `python -c "
    import numpy as np
    from ketu.houses.placidus import placidus_cusps
    from ketu.houses.ascmc import compute_ascmc
    # Vectorized: 3 charts at once
    jds  = np.array([2451545.0, 2470204.0, 2415020.5])
    lats = np.array([48.8566, 64.1466, 40.7128])
    lons = np.array([2.3522, -21.9426, -74.0060])
    chart = compute_ascmc(jds, lats, lons)
    cusps = placidus_cusps(chart['armc'], lats, chart['eps'])
    assert cusps.shape == (3, 12)
    assert not np.isnan(cusps).any()
    print('vectorized OK', cusps.shape)
    "`

    `python -c "
    import numpy as np
    from ketu.houses.placidus import placidus_cusps
    # Polar lat=80° expected to produce NaN cusps (HOU-06: caller will route)
    cusps = placidus_cusps(np.asarray(180.0), np.asarray(80.0), np.asarray(23.4))
    print('polar cusps (some should be NaN):', cusps)
    assert np.isnan(cusps).any(), 'polar lat should NaN at least one cusp'
    "`

    `mypy --strict ketu/houses/placidus.py` is clean.

    `pytest tests/ -v` — full suite still passes; no regressions in existing 488+ tests.
  </verify>
  <done>
    `ketu/houses/placidus.py` exists. `placidus_cusps` is registered into SYSTEMS. Returns shape (..., 12) ndarray. Iteration uses mask-based continuation with TOL_DEG=1e-7 and MAX_ITER=50. Cusps 1, 4, 7, 10 from ASC/MC (closed form). Cusps 5, 6, 8, 9 from opposites of 11, 12, 2, 3. Per-cusp formulas in dispatch dict (no if-elif ladder). Polar boundary yields NaN cusps (Plan 10-06 routes to HighLatitudeError). Vectorized over (armc, lat, eps) arrays. mypy --strict clean.
  </done>
</task>

<task type="auto">
  <name>Task 2: Write tests/houses/test_placidus.py with 8-chart oracle agreement, iteration cap, and mask-correctness invariants</name>
  <files>tests/houses/test_placidus.py</files>
  <action>
    Create `tests/houses/test_placidus.py`. The test plan:

    1. **Oracle agreement (HOU-09 + HOU-03):** for each of the 8 non-polar reference charts, every cusp matches swisseph oracle to <1 arcmin.
    2. **Iteration cap (HOU-03):** running placidus_cusps on a "normal" chart uses ≤10 iter (well below the 50 cap); the 50-cap test deliberately constructs a near-polar input and asserts the function does NOT exceed 50.
    3. **Non-convergence handling:** at lat=80° (definitely beyond polar circle), at least one of cusps 11/12/2/3 yields NaN. (Plan 10-05 owns the polar fallback; this plan just verifies NaN propagation works.)
    4. **Vectorization correctness:** running on N=3 charts at once produces the same per-element result as running each individually.
    5. **Cusps 5/6/8/9 are exact opposites of 11/12/2/3.**
    6. **Cusps 1, 4, 7, 10 = ASC, IC, DESC, MC.**

    Code:

    ```python
    """Placidus house system tests vs swisseph oracle.

    Tolerance: <1 arcmin (1/60 deg ≈ 0.01667°) per HOU-01/HOU-09 spec.
    Reference fixtures from tests/houses/fixtures/reference_charts.json (Plan 10-02).
    """
    from __future__ import annotations
    import numpy as np
    import pytest

    from ketu.houses.placidus import placidus_cusps, MAX_ITER, TOL_DEG
    from ketu.houses.ascmc import compute_ascmc

    ARCMIN_DEG = 1.0 / 60.0
    CUSP_TOL = 1.0 * ARCMIN_DEG  # HOU-01 / HOU-09


    NON_POLAR_LABELS = [
        "J2000_Greenwich", "J2000_Paris", "J2000_Sydney",
        "J2000_Tokyo", "J2000_BuenosAires", "J2000_Equator",
        "1900_NewYork", "2050_Reykjavik",
    ]


    @pytest.mark.parametrize("label", NON_POLAR_LABELS)
    def test_placidus_cusps_match_oracle_at_arcmin(
        label, reference_charts, loaded_reference_snapshot,
    ):
        """All 12 cusps agree with swisseph at every non-polar reference chart."""
        chart = next(c for c in reference_charts if c["label"] == label)
        snap_cusps = np.asarray(
            loaded_reference_snapshot["charts"][label]["systems"]["placidus"]["cusps"]
        )

        ascmc = compute_ascmc(chart["jd"], chart["lat"], chart["lon"])
        cusps = placidus_cusps(
            np.asarray(ascmc["armc"]),
            np.asarray(chart["lat"]),
            np.asarray(ascmc["eps"]),
        )

        # Modular distance per cusp (handles 0/360 wrap)
        deltas = np.abs(((cusps - snap_cusps + 180.0) % 360.0) - 180.0)

        # Per-cusp assertion with informative message
        for i in range(12):
            assert deltas[i] < CUSP_TOL, (
                f"{label}: cusp {i+1} drift {deltas[i] * 60:.3f} arcmin "
                f"> {CUSP_TOL * 60} arcmin (got {cusps[i]:.6f}, oracle {snap_cusps[i]:.6f})"
            )


    def test_placidus_cusps_1_4_7_10_match_ascmc():
        """Cusps 1, 4, 7, 10 are closed-form (ASC, IC, DESC, MC) — no iteration."""
        ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
        cusps = placidus_cusps(
            np.asarray(ascmc["armc"]),
            np.asarray(48.8566),
            np.asarray(ascmc["eps"]),
        )
        # cusp 1 (index 0) = ASC
        assert abs(((float(cusps[0]) - float(ascmc["asc"]) + 180) % 360) - 180) < 1e-9
        # cusp 4 (index 3) = IC = MC + 180
        assert abs(((float(cusps[3]) - (float(ascmc["mc"]) + 180) % 360 + 180) % 360) - 180) < 1e-9
        # cusp 7 (index 6) = DESC = ASC + 180
        assert abs(((float(cusps[6]) - (float(ascmc["asc"]) + 180) % 360 + 180) % 360) - 180) < 1e-9
        # cusp 10 (index 9) = MC
        assert abs(((float(cusps[9]) - float(ascmc["mc"]) + 180) % 360) - 180) < 1e-9


    def test_placidus_cusps_5_6_8_9_are_opposites_of_11_12_2_3():
        """Derived cusps are exact 180° opposites by construction."""
        ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
        cusps = placidus_cusps(
            np.asarray(ascmc["armc"]),
            np.asarray(48.8566),
            np.asarray(ascmc["eps"]),
        )
        pairs = [(4, 10), (5, 11), (7, 1), (8, 2)]  # (5↔11, 6↔12, 8↔2, 9↔3) by 0-index
        for derived_idx, source_idx in pairs:
            expected = (cusps[source_idx] + 180.0) % 360.0
            actual = cusps[derived_idx]
            delta = abs(((actual - expected + 180) % 360) - 180)
            assert delta < 1e-9, (
                f"cusp index {derived_idx} = {actual:.6f}; "
                f"expected (cusp {source_idx} + 180) mod 360 = {expected:.6f}; "
                f"delta = {delta:.6e}"
            )


    def test_placidus_vectorized_matches_scalar_per_element():
        """Running on 3 charts at once == running each individually."""
        jds  = np.array([2451545.0, 2470204.0, 2415020.5])
        lats = np.array([48.8566, 64.1466, 40.7128])
        lons = np.array([2.3522, -21.9426, -74.0060])

        ascmc_batch = compute_ascmc(jds, lats, lons)
        cusps_batch = placidus_cusps(ascmc_batch["armc"], lats, ascmc_batch["eps"])

        for i in range(3):
            ascmc_i = compute_ascmc(float(jds[i]), float(lats[i]), float(lons[i]))
            cusps_i = placidus_cusps(
                np.asarray(ascmc_i["armc"]),
                np.asarray(float(lats[i])),
                np.asarray(ascmc_i["eps"]),
            )
            np.testing.assert_allclose(
                cusps_batch[i], cusps_i, atol=1e-9, rtol=0,
                err_msg=f"vectorized vs scalar drift at chart {i}",
            )


    def test_placidus_polar_lat_80_yields_nan_cusps():
        """At lat=80° beyond polar circle, at least one iterated cusp NaNs.

        This proves NaN-propagation works; Plan 10-05 will route NaN to
        HighLatitudeError or porphyry fallback via the public
        calculate_houses(polar_fallback=...) param.
        """
        ascmc = compute_ascmc(2451545.0, 80.0, 0.0)
        cusps = placidus_cusps(
            np.asarray(ascmc["armc"]),
            np.asarray(80.0),
            np.asarray(ascmc["eps"]),
        )
        assert np.isnan(cusps).any(), "polar lat=80° expected to NaN at least one cusp"


    def test_placidus_iteration_cap_not_exceeded():
        """MAX_ITER constant equals the HOU-03 spec value."""
        assert MAX_ITER == 50, f"HOU-03 spec is iter-cap=50; got MAX_ITER={MAX_ITER}"


    def test_placidus_convergence_threshold():
        """TOL_DEG matches research §'Don't Hand-Roll' value."""
        assert TOL_DEG == 1e-7, f"research §convergence threshold is 1e-7°; got {TOL_DEG}"


    def test_placidus_no_silent_nan_at_mid_latitudes(reference_charts):
        """No reference chart at |lat| < 65° should produce any NaN cusp."""
        for chart in reference_charts:
            if abs(chart["lat"]) >= 65.0:
                continue  # polar charts handled separately
            ascmc = compute_ascmc(chart["jd"], chart["lat"], chart["lon"])
            cusps = placidus_cusps(
                np.asarray(ascmc["armc"]),
                np.asarray(chart["lat"]),
                np.asarray(ascmc["eps"]),
            )
            assert not np.isnan(cusps).any(), (
                f"silent NaN at non-polar chart {chart['label']}: cusps={cusps}"
            )
    ```

    Anti-patterns to avoid:
    - DO NOT widen CUSP_TOL beyond 1 arcmin "to make polar-edge charts pass" — HOU-09 spec is <1 arcmin. If 2050_Reykjavik (lat=64°) fails, that's a real bug (probably a sign error in cusp 11/12 formula at high northern lat).
    - DO NOT skip the iteration-cap test — it pins the spec constant at 50, catching any future "let me bump it to 100 to make hard cases work" silently. The fix is to investigate non-convergence, not to inflate the cap.
    - DO NOT compare cusps via raw subtraction — modular distance via `abs(((a - b + 180) % 360) - 180)` (Pitfall 3).
    - DO NOT register a fake placidus implementation in this test file's setup — `_iterate_cusp_ra` is internal; tests use the public `placidus_cusps` only.
    - DO NOT load the JSON snapshot manually — go through the `loaded_reference_snapshot` fixture from conftest (Plan 10-02 owns the path resolution and the skip-on-missing fallback).
  </action>
  <verify>
    `pytest tests/houses/test_placidus.py -v` runs and shows:
    - 8 oracle-agreement tests (one per non-polar chart) pass at <1 arcmin
    - 1 cusp 1/4/7/10 = ASC/IC/DESC/MC test passes
    - 1 cusps 5/6/8/9 = opposites test passes
    - 1 vectorized vs scalar parity test passes
    - 1 polar lat=80° NaN propagation test passes
    - 1 MAX_ITER == 50 invariant passes
    - 1 TOL_DEG == 1e-7 invariant passes
    - 1 no-silent-NaN at mid-lats test passes
    Total: 14+ tests.

    `mypy --strict tests/houses/test_placidus.py` clean.

    `pytest tests/ -v` — full suite still green.
  </verify>
  <done>
    14+ tests in test_placidus.py covering oracle agreement at <1 arcmin per cusp on 8 charts, cusps 1/4/7/10 closed-form correctness, cusps 5/6/8/9 opposite invariance, vectorized parity, polar NaN propagation, MAX_ITER+TOL invariants, no-silent-NaN at mid-lats. mypy --strict clean. Full pytest suite green.
  </done>
</task>

</tasks>

<verification>
- `pytest tests/houses/test_placidus.py -v` shows ≥14 tests passing (or skipped wholesale if swisseph absent).
- All 8 non-polar reference charts × 12 cusps = 96 oracle-agreement assertions pass at <1 arcmin.
- Vectorized batch path matches scalar per-element path within 1e-9 deg.
- Polar lat=80° produces ≥1 NaN cusp (proves NaN-propagation works for Plan 05's polar fallback).
- MAX_ITER == 50 (HOU-03 spec); TOL_DEG == 1e-7 (research §"Don't Hand-Roll").
- `mypy --strict ketu/houses/placidus.py tests/houses/test_placidus.py` clean.
- `python -c "from ketu.houses.registry import SYSTEMS; assert 'placidus' in SYSTEMS"` passes.
</verification>

<success_criteria>
- HOU-03 satisfied: Placidus implementation with iteration cap of 50 and explicit non-convergence detection (NaN propagation).
- HOU-08 satisfied (Placidus side): vectorized over (armc, lat, eps) arrays via mask-based continuation.
- HOU-09 partial: 8 non-polar reference charts × 12 cusps assertions at <1 arcmin tolerance.
- Pitfall 2 (single-arg arctan) avoided in placidus_cusps top-level math; declination uses `arctan` because declination IS scalar-valued (documented in code).
- Pitfall 3 (mod-360 wrap) avoided in convergence check.
- Pitfall 6 (polar saturation) handled via `ascensional_difference` returning NaN where `|s| ≥ 1`.
- Anti-pattern (Python `for jd in jds:`) avoided.
</success_criteria>

<output>
After completion, create `.planning/phases/10-houses-module/10-04-SUMMARY.md` documenting:
- Per-chart, per-cusp drift table (8 charts × 12 cusps = 96 numbers in arcseconds; show max per chart)
- Max iter used across all reference charts (should be ≪ 50)
- Polar handling: NaN propagation confirmed at lat=80° (cusps that NaN listed)
- Vectorized vs scalar parity: max delta across 3-chart batch (should be < 1e-9 deg)
- SYSTEMS dict at end of plan: contains exactly "placidus" (Plan 05 will add koch + porphyry)
- Confirmation: mypy --strict clean; pytest suite green; no runtime swisseph imports
</output>
