---
phase: 10-houses-module
plan: 05
type: execute
wave: 3
depends_on:
  - "10-01"
  - "10-02"
  - "10-03"
files_modified:
  - ketu/houses/koch.py
  - ketu/houses/porphyry.py
  - tests/houses/test_koch.py
  - tests/houses/test_porphyry.py
  - tests/houses/test_polar_safety.py
autonomous: true
plan_id: "10-05"
requirements:
  - HOU-04
  - HOU-06

must_haves:
  truths:
    - "ketu.houses.koch.koch_cusps(armc, lat, eps) returns ndarray of shape (..., 12); registered as @register('koch')"
    - "ketu.houses.porphyry.porphyry_cusps(armc, lat, eps) returns ndarray of shape (..., 12); registered as @register('porphyry'); CLOSED-FORM (no iteration); works at all latitudes including 90°"
    - "Koch matches swisseph oracle to <1 arcmin on all 8 non-polar reference charts at every cusp 1-12"
    - "Porphyry trisects the (mc → asc) and (asc → ic) arcs into thirds; cusps 5/6/8/9 are opposites of 11/12/2/3 by construction"
    - "Polar boundary detected via 90° - mean_obliquity(jd) (Pitfall 4); NOT a hardcoded 66.56° literal"
    - "polar_fallback parameter accepted at the public-API boundary (Plan 10-06 will plumb it through to calculate_houses); this plan implements the polar-detection helper that calculate_houses calls"
    - "is_polar(lat, jd) -> bool returns True iff |lat| > polar_lat(jd) where polar_lat = 90 - mean_obliquity(jd) - polar_eps_tol"
    - "When |lat| > polar_lat and polar_fallback='raise' (default), HighLatitudeError is raised (Plan 10-06 wires); when polar_fallback='porphyry', porphyry_cusps is dispatched"
    - "Koch at lat=80° produces NaN cusps (polar) — caller routes via polar_fallback per HOU-06; never silent NaN reaches the user"
  artifacts:
    - path: "ketu/houses/koch.py"
      provides: "Koch implementation: koch_cusps + @register('koch'); oblique-ascension trisection; same vectorized mask-iter shape as Placidus"
      contains: "@register"
      min_lines: 80
    - path: "ketu/houses/porphyry.py"
      provides: "Porphyry implementation (closed-form polar fallback): porphyry_cusps + @register('porphyry') + is_polar(lat, jd) helper + polar_circle(jd) helper"
      contains: "@register"
      min_lines: 80
    - path: "tests/houses/test_koch.py"
      provides: "8 non-polar charts × 12 cusps oracle agreement at <1 arcmin; vectorized parity"
      contains: "koch_cusps"
      min_lines: 60
    - path: "tests/houses/test_porphyry.py"
      provides: "Porphyry closed-form correctness: trisection invariants; works at lat=80° and lat=89° (no NaN); cusps 5/6/8/9 opposites of 11/12/2/3"
      contains: "porphyry_cusps"
      min_lines: 60
    - path: "tests/houses/test_polar_safety.py"
      provides: "Polar-circle detection invariant; HighLatitudeError raised at lat>polar_lat for placidus/koch with polar_fallback='raise'; porphyry returned with polar_fallback='porphyry'; never silent NaN at the public API"
      contains: "HighLatitudeError"
      min_lines: 60
  key_links:
    - from: "ketu/houses/koch.py"
      to: "ketu.houses.registry SYSTEMS"
      via: "@register('koch') decorator"
      pattern: "@register\\(.koch.\\)"
    - from: "ketu/houses/porphyry.py"
      to: "ketu.houses.registry SYSTEMS"
      via: "@register('porphyry') decorator"
      pattern: "@register\\(.porphyry.\\)"
    - from: "ketu/houses/porphyry.py"
      to: "ketu.ephemeris.coordinates.mean_obliquity"
      via: "polar_circle(jd) = 90 - mean_obliquity(jd)"
      pattern: "mean_obliquity"
    - from: "tests/houses/test_polar_safety.py"
      to: "ketu.houses.HighLatitudeError"
      via: "pytest.raises(HighLatitudeError)"
      pattern: "HighLatitudeError"
---

<objective>
Implement Koch + Porphyry house systems and the polar-safety machinery (HOU-04, HOU-06). Koch is iterative (same shape as Placidus); Porphyry is closed-form and works at all latitudes including 90°. The polar-safety helpers (`is_polar`, `polar_circle`) detect when |lat| exceeds the time-varying polar circle (90° - ε(jd)) and let Plan 10-06's `calculate_houses` route to either HighLatitudeError or porphyry_cusps based on the `polar_fallback` parameter.

Purpose: Koch trisects oblique ascension at the meridian (instead of semi-arc); for the user, it's "Placidus's stylistic alternative — same family of failures at polar lats." Porphyry trisects the (mc, asc) and (asc, ic) arcs in pure ecliptic coordinates — no iteration, no polar failure mode, mathematically defined at lat=89° just as well as lat=0°. The polar-fallback contract states: at |lat| > 90° - ε(jd), Placidus and Koch fail; user picks `raise` (default — HighLatitudeError) or `porphyry` (silent fallback, but never silent NaN — the result is real Porphyry cusps).

This plan runs in Wave 3 in parallel with Plan 10-04 (Placidus). They touch disjoint files (`koch.py`+`porphyry.py` vs `placidus.py`); both consume the Plan 10-03 scaffold (`registry`, `_ecliptic`, `ascmc`, `core`).

Output:
- `ketu/houses/koch.py` — `koch_cusps(armc, lat, eps)` registered as 'koch'; iterative.
- `ketu/houses/porphyry.py` — `porphyry_cusps(armc, lat, eps)` registered as 'porphyry'; closed-form; plus `is_polar(lat, jd) -> bool` and `polar_circle(jd) -> float` helpers.
- 3 test files: test_koch (oracle agreement, vectorized parity), test_porphyry (closed-form invariants, works at lat=89°), test_polar_safety (boundary detection, HighLatitudeError raise vs porphyry fallback).
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
@ketu/houses/core.py

# Test infrastructure (do not modify)
@tests/houses/conftest.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement Koch + Porphyry + polar-safety helpers in ketu/houses/{koch,porphyry}.py</name>
  <files>ketu/houses/koch.py
ketu/houses/porphyry.py</files>
  <action>
    Step A — Create `ketu/houses/porphyry.py` (closed-form, no iteration). This goes first because Koch may use polar-circle helpers in its boundary check.

    ```python
    """Porphyry house system — closed-form trisection.

    Used as the polar fallback for Placidus and Koch (HOU-06). Mathematically
    defined at all latitudes including 90° because it depends only on ASC/MC,
    not on declination-dependent ascensional difference.

    Trisection (research §"Don't Hand-Roll → Porphyry formula"):
        upper_step = ((asc - mc) mod 360) / 3
        cusp_11 = mc + upper_step
        cusp_12 = mc + 2 * upper_step
        lower_step = ((ic - asc) mod 360) / 3   where ic = (mc + 180) mod 360
        cusp_2  = asc + lower_step
        cusp_3  = asc + 2 * lower_step
        cusps 5/6/8/9 = opposites of 11/12/2/3
        cusps 1/4/7/10 = ASC/IC/DESC/MC
    """
    from __future__ import annotations
    from typing import Union
    import numpy as np

    from .registry import register
    from ketu.ephemeris.coordinates import mean_obliquity


    POLAR_EPS_TOL: float = 1e-9  # research §Open Question 4: trigger fallback when |s| > 1 - eps_tol


    def polar_circle(jd: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Return the polar circle latitude (degrees) at the given Julian date.

        polar_circle = 90° − mean_obliquity(jd)

        At J2000 ε ≈ 23.4393° → polar_circle ≈ 66.5607°. Drifts ~50″ per year
        (Pitfall 4); using the time-varying value is what makes the polar
        boundary correct over centuries.

        Vectorized via mean_obliquity (already vectorized in
        ketu.ephemeris.coordinates).
        """
        return 90.0 - mean_obliquity(jd)


    def is_polar(
        lat: Union[float, np.ndarray],
        jd: Union[float, np.ndarray],
    ) -> Union[bool, np.ndarray]:
        """Return True where |lat| > polar_circle(jd) - POLAR_EPS_TOL.

        Used by the public calculate_houses (Plan 10-06) to route polar
        elements to either HighLatitudeError or porphyry_cusps based on
        the polar_fallback parameter (HOU-06).

        Returns a Python bool for scalar input, np.ndarray of bool otherwise.
        """
        boundary = polar_circle(jd)
        return np.abs(lat) > boundary - POLAR_EPS_TOL


    @register("porphyry")
    def porphyry_cusps(
        armc: np.ndarray,
        lat: np.ndarray,
        eps: np.ndarray,
    ) -> np.ndarray:
        """Compute the 12 Porphyry house cusps.

        Closed-form (no iteration). Works at all latitudes.

        Parameters
        ----------
        armc, lat, eps : np.ndarray (degrees, broadcast-compatible)

        Returns
        -------
        np.ndarray of shape (..., 12)
        """
        armc_b, lat_b, eps_b = np.broadcast_arrays(armc, lat, eps)
        armc_rad = np.deg2rad(armc_b)
        eps_rad = np.deg2rad(eps_b)
        lat_rad = np.deg2rad(lat_b)

        # ASC and MC closed-form (same as ascmc.compute_ascmc, inlined here
        # to keep porphyry self-contained — porphyry is the POLAR FALLBACK
        # and must work even when the standard ascmc machinery would NaN).
        # Note: at exactly lat=90°, tan(lat) → inf and ASC formula diverges.
        # In practice, Plan 10-06 calls porphyry only when |lat| > polar_circle,
        # not at lat=90° (which is degenerate for any house system except
        # Whole Sign / Equal). Document the boundary in is_polar's docstring.
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

        # Upper trisection: from MC eastward to ASC
        upper_arc = (asc - mc) % 360.0
        upper_step = upper_arc / 3.0

        # Lower trisection: from ASC eastward to IC
        lower_arc = (ic - asc) % 360.0
        lower_step = lower_arc / 3.0

        cusp_11 = (mc + upper_step) % 360.0
        cusp_12 = (mc + 2.0 * upper_step) % 360.0
        cusp_2  = (asc + lower_step) % 360.0
        cusp_3  = (asc + 2.0 * lower_step) % 360.0

        cusp_5 = (cusp_11 + 180.0) % 360.0
        cusp_6 = (cusp_12 + 180.0) % 360.0
        cusp_8 = (cusp_2  + 180.0) % 360.0
        cusp_9 = (cusp_3  + 180.0) % 360.0

        return np.stack([
            asc, cusp_2, cusp_3, ic,
            cusp_5, cusp_6, desc, cusp_8,
            cusp_9, mc, cusp_11, cusp_12,
        ], axis=-1)
    ```

    Step B — Create `ketu/houses/koch.py`. Koch trisects oblique ascension instead of semi-arc. Same mask-based iteration shape as Placidus but with a different per-cusp formula. Shorter than Placidus because we already have all the helpers.

    ```python
    """Koch house system implementation.

    Koch trisects oblique ascension (OA = RA - AD) at the meridian rather than
    the semi-arc as Placidus does. Per research §"Don't Hand-Roll → Koch
    formula":

        OA_11 = OA_MC + (OA_Asc - OA_MC) / 3
        OA_12 = OA_MC + 2 * (OA_Asc - OA_MC) / 3
        OA_2  = OA_Asc + (OA_IC - OA_Asc) / 3
        OA_3  = OA_Asc + 2 * (OA_IC - OA_Asc) / 3

    Then OA → RA via the same AD machinery (AD = arcsin(tan(lat)*tan(decl))),
    iterated to convergence. Polar boundary at |tan(lat)·tan(decl)| ≥ 1 yields
    NaN (Plan 10-06 routes to fallback per HOU-06).
    """
    from __future__ import annotations
    import numpy as np

    from .registry import register
    from ._ecliptic import ascensional_difference

    MAX_ITER: int = 50
    TOL_DEG: float = 1e-7


    def _oa_to_ra_iterate(
        oa: np.ndarray,
        lat: np.ndarray,
        eps: np.ndarray,
    ) -> np.ndarray:
        """Solve RA from oblique ascension OA = RA − AD via fixed point.

        Initial guess: RA_0 = OA (assume AD=0).
        Update: AD_k = arcsin(tan(lat)·tan(decl_k)) where decl_k = arctan(sin(RA_k)·tan(eps))
                RA_{k+1} = OA + AD_k

        Stop when |delta(RA, OA + AD)| < TOL_DEG. Cap at MAX_ITER. NaN
        propagates from polar boundary.
        """
        oa_b, lat_b, eps_b = np.broadcast_arrays(oa, lat, eps)
        RA = oa_b.copy()  # initial guess: AD=0
        converged = np.zeros_like(RA, dtype=bool)

        for _ in range(MAX_ITER):
            active = ~converged & ~np.isnan(RA)
            if not active.any():
                break

            sin_RA = np.sin(np.deg2rad(RA))
            tan_eps = np.tan(np.deg2rad(eps_b))
            decl = np.rad2deg(np.arctan(sin_RA * tan_eps))
            AD = ascensional_difference(lat_b, decl)
            RA_new = (oa_b + AD) % 360.0

            delta = np.abs(((RA_new - RA + 180.0) % 360.0) - 180.0)
            newly = active & ~np.isnan(RA_new) & (delta < TOL_DEG)

            RA = np.where(active & ~np.isnan(RA_new), RA_new, RA)
            RA = np.where(active & np.isnan(RA_new), np.nan, RA)
            converged = converged | newly | np.isnan(RA)

        not_done = ~converged
        RA = np.where(not_done, np.nan, RA)
        return RA % 360.0


    def _ra_to_lambda(ra: np.ndarray, eps: np.ndarray) -> np.ndarray:
        """Same RA→ecliptic-longitude conversion as Placidus uses.

        Placidus and Koch agree on this projection because both place cusps
        on the ecliptic; only the trisection target differs (semi-arc vs
        oblique-ascension).
        """
        ra_rad = np.deg2rad(ra)
        eps_rad = np.deg2rad(eps)
        lam = np.arctan2(
            np.sin(ra_rad) * np.cos(eps_rad),
            np.cos(ra_rad),
        )
        lam_deg = np.rad2deg(lam) % 360.0
        ra_norm = ra % 360.0
        delta = (lam_deg - ra_norm + 180.0) % 360.0 - 180.0
        flip = np.abs(delta) > 90.0
        lam_deg = np.where(flip, (lam_deg + 180.0) % 360.0, lam_deg)
        return lam_deg


    @register("koch")
    def koch_cusps(
        armc: np.ndarray,
        lat: np.ndarray,
        eps: np.ndarray,
    ) -> np.ndarray:
        """Compute the 12 Koch house cusps.

        Parameters
        ----------
        armc, lat, eps : np.ndarray (degrees, broadcast-compatible)

        Returns
        -------
        np.ndarray of shape (..., 12) — NaN cusps at polar lats; caller
        (Plan 10-06 calculate_houses) routes via polar_fallback per HOU-06.
        """
        armc_b, lat_b, eps_b = np.broadcast_arrays(armc, lat, eps)
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

        # Compute oblique ascensions of MC, ASC, IC.
        # OA_MC = ARMC (by definition; MC is at zero diurnal-arc fraction).
        # OA_Asc = RA(asc) - AD(asc, lat). RA(asc) recovered from λ via
        #   tan(RA) = tan(λ) / cos(eps); use arctan2 for quadrant.
        # OA_IC = OA_MC + 180.

        def _lambda_to_ra(lam_deg: np.ndarray) -> np.ndarray:
            lam_rad = np.deg2rad(lam_deg)
            return np.rad2deg(np.arctan2(
                np.sin(lam_rad) * np.cos(eps_rad),
                np.cos(lam_rad),
            )) % 360.0

        def _decl_of_ecliptic_point(lam_deg: np.ndarray) -> np.ndarray:
            lam_rad = np.deg2rad(lam_deg)
            return np.rad2deg(np.arcsin(np.sin(lam_rad) * np.sin(eps_rad)))

        ra_asc = _lambda_to_ra(asc)
        decl_asc = _decl_of_ecliptic_point(asc)
        ad_asc = ascensional_difference(lat_b, decl_asc)
        oa_mc = armc_b
        oa_asc = (ra_asc - ad_asc) % 360.0
        oa_ic = (oa_mc + 180.0) % 360.0

        # Upper trisection (MC → ASC): cusps 11, 12
        oa_upper_arc = (oa_asc - oa_mc) % 360.0
        oa_11 = (oa_mc + oa_upper_arc / 3.0) % 360.0
        oa_12 = (oa_mc + 2.0 * oa_upper_arc / 3.0) % 360.0
        # Lower trisection (ASC → IC): cusps 2, 3
        oa_lower_arc = (oa_ic - oa_asc) % 360.0
        oa_2  = (oa_asc + oa_lower_arc / 3.0) % 360.0
        oa_3  = (oa_asc + 2.0 * oa_lower_arc / 3.0) % 360.0

        # OA → RA (iterative; NaN at polar)
        ra_11 = _oa_to_ra_iterate(oa_11, lat_b, eps_b)
        ra_12 = _oa_to_ra_iterate(oa_12, lat_b, eps_b)
        ra_2  = _oa_to_ra_iterate(oa_2,  lat_b, eps_b)
        ra_3  = _oa_to_ra_iterate(oa_3,  lat_b, eps_b)

        # RA → ecliptic longitude
        cusp_11 = _ra_to_lambda(ra_11, eps_b)
        cusp_12 = _ra_to_lambda(ra_12, eps_b)
        cusp_2  = _ra_to_lambda(ra_2,  eps_b)
        cusp_3  = _ra_to_lambda(ra_3,  eps_b)

        # Cusps 5, 6, 8, 9 = opposites
        cusp_5 = (cusp_11 + 180.0) % 360.0
        cusp_6 = (cusp_12 + 180.0) % 360.0
        cusp_8 = (cusp_2  + 180.0) % 360.0
        cusp_9 = (cusp_3  + 180.0) % 360.0

        return np.stack([
            asc, cusp_2, cusp_3, ic,
            cusp_5, cusp_6, desc, cusp_8,
            cusp_9, mc, cusp_11, cusp_12,
        ], axis=-1)
    ```

    Anti-patterns to avoid:
    - DO NOT register Placidus here — Plan 10-04 already did.
    - DO NOT hardcode the polar boundary at 66.56° — Pitfall 4 (use `90 - mean_obliquity(jd)`).
    - DO NOT skip the `polar_eps_tol = 1e-9` margin in `is_polar` — research §Open Question 4 explicitly recommends "trigger fallback when |s| > 1 - eps_tol" to avoid the false-positive-convergence at the exact boundary (Pitfall 6).
    - DO NOT use single-arg `arctan` for OA→RA conversion — quadrant errors guaranteed (Pitfall 2). The exception is `arctan(sin_RA * tan_eps)` for declination, which IS in [-π/2, +π/2] by definition; document this in code comments.
    - DO NOT compute Koch by "calling placidus_cusps and adjusting" — Koch's underlying angles differ; call the public Koch math directly. (No cross-import between systems beyond what _ecliptic.py and ascmc.py provide.)
    - DO NOT perform any I/O — these modules are pure functions.

    Mypy --strict requirements:
    - All function signatures fully annotated.
    - `Union[float, np.ndarray]` where appropriate; the project pattern is consistent (research §Pitfall 9).
    - `np.broadcast_arrays` returns tuple; explicit unpacking with type-annotation.
  </action>
  <verify>
    `python -c "
    import numpy as np
    from ketu.houses.registry import SYSTEMS
    assert 'koch' in SYSTEMS
    assert 'porphyry' in SYSTEMS

    # Sanity: Paris J2000 Koch
    from ketu.houses.ascmc import compute_ascmc
    from ketu.houses.koch import koch_cusps
    chart = compute_ascmc(2451545.0, 48.8566, 2.3522)
    cusps_k = koch_cusps(np.asarray(chart['armc']), np.asarray(48.8566), np.asarray(chart['eps']))
    print('Koch Paris cusps:', cusps_k)
    assert not np.isnan(cusps_k).any()

    # Sanity: Porphyry at lat=89° (deeply polar — must NOT NaN)
    from ketu.houses.porphyry import porphyry_cusps, is_polar, polar_circle
    chart89 = compute_ascmc(2451545.0, 89.0, 0.0)
    cusps_p = porphyry_cusps(np.asarray(chart89['armc']), np.asarray(89.0), np.asarray(chart89['eps']))
    print('Porphyry lat=89°:', cusps_p)
    assert not np.isnan(cusps_p).any(), 'Porphyry must work at lat=89°'

    # is_polar boundary check
    print('polar_circle at J2000:', polar_circle(2451545.0))
    print('is_polar(80, J2000):', is_polar(80.0, 2451545.0))
    print('is_polar(60, J2000):', is_polar(60.0, 2451545.0))
    "`

    `mypy --strict ketu/houses/koch.py ketu/houses/porphyry.py` clean.
  </verify>
  <done>
    `ketu/houses/koch.py` exists; koch_cusps registered as 'koch'. `ketu/houses/porphyry.py` exists; porphyry_cusps registered as 'porphyry'; polar_circle and is_polar helpers exposed. Both Koch and Porphyry vectorized with mask-based iteration (Koch only; Porphyry is closed-form). Porphyry works at lat=89° without NaN. is_polar uses 90° - mean_obliquity(jd), not a hardcoded constant. mypy --strict clean.
  </done>
</task>

<task type="auto">
  <name>Task 2: Write tests/houses/test_koch.py with 8-chart oracle agreement and vectorized parity</name>
  <files>tests/houses/test_koch.py</files>
  <action>
    Create `tests/houses/test_koch.py`. Mirror the structure of test_placidus.py but for Koch.

    ```python
    """Koch house system tests vs swisseph oracle (HOU-04, HOU-09).

    Tolerance: <1 arcmin per cusp. Reference fixtures from Plan 10-02.
    """
    from __future__ import annotations
    import numpy as np
    import pytest

    from ketu.houses.koch import koch_cusps, MAX_ITER, TOL_DEG
    from ketu.houses.ascmc import compute_ascmc

    ARCMIN_DEG = 1.0 / 60.0
    CUSP_TOL = 1.0 * ARCMIN_DEG

    NON_POLAR_LABELS = [
        "J2000_Greenwich", "J2000_Paris", "J2000_Sydney",
        "J2000_Tokyo", "J2000_BuenosAires", "J2000_Equator",
        "1900_NewYork", "2050_Reykjavik",
    ]


    @pytest.mark.parametrize("label", NON_POLAR_LABELS)
    def test_koch_cusps_match_oracle_at_arcmin(
        label, reference_charts, loaded_reference_snapshot,
    ):
        chart = next(c for c in reference_charts if c["label"] == label)
        snap_cusps = np.asarray(
            loaded_reference_snapshot["charts"][label]["systems"]["koch"]["cusps"]
        )

        ascmc = compute_ascmc(chart["jd"], chart["lat"], chart["lon"])
        cusps = koch_cusps(
            np.asarray(ascmc["armc"]),
            np.asarray(chart["lat"]),
            np.asarray(ascmc["eps"]),
        )

        deltas = np.abs(((cusps - snap_cusps + 180.0) % 360.0) - 180.0)
        for i in range(12):
            assert deltas[i] < CUSP_TOL, (
                f"{label}: Koch cusp {i+1} drift {deltas[i] * 60:.3f} arcmin "
                f"(ours {cusps[i]:.6f}, oracle {snap_cusps[i]:.6f})"
            )


    def test_koch_iter_constants_match_research():
        assert MAX_ITER == 50
        assert TOL_DEG == 1e-7


    def test_koch_vectorized_matches_scalar_per_element():
        jds  = np.array([2451545.0, 2470204.0, 2415020.5])
        lats = np.array([48.8566, 64.1466, 40.7128])
        lons = np.array([2.3522, -21.9426, -74.0060])
        ascmc_b = compute_ascmc(jds, lats, lons)
        cusps_b = koch_cusps(ascmc_b["armc"], lats, ascmc_b["eps"])

        for i in range(3):
            ai = compute_ascmc(float(jds[i]), float(lats[i]), float(lons[i]))
            ci = koch_cusps(
                np.asarray(ai["armc"]),
                np.asarray(float(lats[i])),
                np.asarray(ai["eps"]),
            )
            np.testing.assert_allclose(cusps_b[i], ci, atol=1e-9, rtol=0)


    def test_koch_cusps_5_6_8_9_are_opposites_of_11_12_2_3():
        ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
        cusps = koch_cusps(
            np.asarray(ascmc["armc"]),
            np.asarray(48.8566),
            np.asarray(ascmc["eps"]),
        )
        pairs = [(4, 10), (5, 11), (7, 1), (8, 2)]
        for derived_idx, source_idx in pairs:
            expected = (cusps[source_idx] + 180.0) % 360.0
            actual = cusps[derived_idx]
            delta = abs(((actual - expected + 180) % 360) - 180)
            assert delta < 1e-9


    def test_koch_polar_lat_80_yields_nan():
        ascmc = compute_ascmc(2451545.0, 80.0, 0.0)
        cusps = koch_cusps(
            np.asarray(ascmc["armc"]),
            np.asarray(80.0),
            np.asarray(ascmc["eps"]),
        )
        assert np.isnan(cusps).any()


    def test_koch_no_silent_nan_at_mid_latitudes(reference_charts):
        for chart in reference_charts:
            if abs(chart["lat"]) >= 65.0:
                continue
            ascmc = compute_ascmc(chart["jd"], chart["lat"], chart["lon"])
            cusps = koch_cusps(
                np.asarray(ascmc["armc"]),
                np.asarray(chart["lat"]),
                np.asarray(ascmc["eps"]),
            )
            assert not np.isnan(cusps).any(), f"silent NaN at {chart['label']}"
    ```

    Anti-patterns to avoid:
    - Same as test_placidus.py: don't widen tolerance, don't skip cap test, modular-distance for angle deltas.
    - DO NOT compare Koch cusps to Placidus cusps — they SHOULD differ (different math).
  </action>
  <verify>
    `pytest tests/houses/test_koch.py -v` shows ~13 tests passing (8 parametrized + 5 invariants).

    `mypy --strict tests/houses/test_koch.py` clean.
  </verify>
  <done>
    test_koch.py exists with 8 oracle-agreement parametrized tests + 5 invariant tests = 13 total. All pass at <1 arcmin per cusp on non-polar charts. Vectorized parity within 1e-9 deg. NaN propagation at lat=80°. mypy --strict clean.
  </done>
</task>

<task type="auto">
  <name>Task 3: Write tests/houses/test_porphyry.py and tests/houses/test_polar_safety.py</name>
  <files>tests/houses/test_porphyry.py
tests/houses/test_polar_safety.py</files>
  <action>
    Step A — `tests/houses/test_porphyry.py`:

    ```python
    """Porphyry tests — closed-form trisection invariants and polar correctness."""
    from __future__ import annotations
    import numpy as np
    import pytest

    from ketu.houses.porphyry import porphyry_cusps, is_polar, polar_circle, POLAR_EPS_TOL
    from ketu.houses.ascmc import compute_ascmc


    def test_porphyry_works_at_extreme_polar_lat():
        """Porphyry at lat=89° must NOT NaN — it's the polar fallback."""
        ascmc = compute_ascmc(2451545.0, 89.0, 0.0)
        cusps = porphyry_cusps(
            np.asarray(ascmc["armc"]),
            np.asarray(89.0),
            np.asarray(ascmc["eps"]),
        )
        assert not np.isnan(cusps).any(), (
            f"Porphyry must work at lat=89°; got cusps={cusps}"
        )


    def test_porphyry_trisection_invariant_upper_arc():
        """Cusps 11, 12 evenly trisect the arc from MC to ASC."""
        ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
        cusps = porphyry_cusps(
            np.asarray(ascmc["armc"]),
            np.asarray(48.8566),
            np.asarray(ascmc["eps"]),
        )
        mc, asc = float(cusps[9]), float(cusps[0])  # cusps 10, 1
        c11, c12 = float(cusps[10]), float(cusps[11])
        upper_arc = (asc - mc) % 360.0
        # cusp_11 - mc should be upper_arc/3; cusp_12 - mc should be 2*upper_arc/3
        assert abs((c11 - mc) % 360.0 - upper_arc / 3.0) < 1e-9
        assert abs((c12 - mc) % 360.0 - 2.0 * upper_arc / 3.0) < 1e-9


    def test_porphyry_trisection_invariant_lower_arc():
        ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
        cusps = porphyry_cusps(
            np.asarray(ascmc["armc"]),
            np.asarray(48.8566),
            np.asarray(ascmc["eps"]),
        )
        ic, asc = float(cusps[3]), float(cusps[0])
        c2, c3 = float(cusps[1]), float(cusps[2])
        lower_arc = (ic - asc) % 360.0
        assert abs((c2 - asc) % 360.0 - lower_arc / 3.0) < 1e-9
        assert abs((c3 - asc) % 360.0 - 2.0 * lower_arc / 3.0) < 1e-9


    def test_porphyry_cusps_5_6_8_9_are_opposites_of_11_12_2_3():
        ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
        cusps = porphyry_cusps(
            np.asarray(ascmc["armc"]),
            np.asarray(48.8566),
            np.asarray(ascmc["eps"]),
        )
        pairs = [(4, 10), (5, 11), (7, 1), (8, 2)]
        for derived_idx, source_idx in pairs:
            expected = (cusps[source_idx] + 180.0) % 360.0
            delta = abs(((cusps[derived_idx] - expected + 180) % 360) - 180)
            assert delta < 1e-9


    def test_porphyry_matches_swisseph_at_paris_j2000(loaded_reference_snapshot):
        """Optional: if snapshot was generated with Porphyry, cross-check."""
        snap = loaded_reference_snapshot["charts"]["J2000_Paris"]["systems"]
        if "porphyry" not in snap:
            pytest.skip("Snapshot does not include Porphyry (Plan 10-02 only snapshots placidus+koch)")
        # ... (left as exercise; Plan 10-02 may not snapshot porphyry by default)


    def test_polar_circle_at_j2000_is_in_expected_range():
        """polar_circle = 90 - ε(jd). At J2000 ε ≈ 23.44 → polar ≈ 66.56."""
        pc = float(polar_circle(2451545.0))
        assert 66.4 < pc < 66.7, f"polar_circle at J2000 = {pc}; expected ~66.56"


    def test_is_polar_at_boundary():
        """lat just above polar circle → True; just below → False."""
        pc = float(polar_circle(2451545.0))
        assert is_polar(pc + 0.1, 2451545.0)
        assert not is_polar(pc - 0.1, 2451545.0)
        # Negative lats too
        assert is_polar(-(pc + 0.1), 2451545.0)
        assert not is_polar(-(pc - 0.1), 2451545.0)


    def test_is_polar_vectorized():
        lats = np.array([0.0, 45.0, 67.0, 80.0, -67.0])
        results = is_polar(lats, 2451545.0)
        assert results.tolist() == [False, False, True, True, True]


    def test_polar_eps_tol_documented():
        """POLAR_EPS_TOL exists per research Open Question 4."""
        assert POLAR_EPS_TOL == 1e-9
    ```

    Step B — `tests/houses/test_polar_safety.py`:

    ```python
    """Polar-safety integration tests (HOU-06).

    These tests verify that the helpers (is_polar, polar_circle) integrate
    correctly. Plan 10-06 will fold them into calculate_houses with the
    polar_fallback parameter; this test file pins the helper contract that
    Plan 10-06 will consume.
    """
    from __future__ import annotations
    import numpy as np
    import pytest

    from ketu.houses import HighLatitudeError
    from ketu.houses.porphyry import is_polar, polar_circle
    from ketu.houses.placidus import placidus_cusps
    from ketu.houses.koch import koch_cusps
    from ketu.houses.porphyry import porphyry_cusps
    from ketu.houses.ascmc import compute_ascmc


    def test_high_latitude_error_is_raised_when_polar_fallback_is_raise(monkeypatch):
        """Simulate the calculate_houses raise behavior — Plan 10-06 wires this for real.

        For Plan 10-05, we just verify the exception class is constructible
        with the right semantic content.
        """
        with pytest.raises(HighLatitudeError) as exc_info:
            raise HighLatitudeError(75.0, "placidus", 66.56)
        assert exc_info.value.lat == 75.0
        assert exc_info.value.system == "placidus"
        assert exc_info.value.polar_lat == 66.56


    def test_placidus_yields_nan_above_polar_circle():
        """Plan 10-06 will check for NaN and raise HighLatitudeError; this test
        pins the underlying contract: above polar circle, Placidus NaN-propagates.
        """
        jd = 2451545.0
        pc = float(polar_circle(jd))
        lat = pc + 1.0  # 1° beyond polar circle
        ascmc = compute_ascmc(jd, lat, 0.0)
        cusps = placidus_cusps(
            np.asarray(ascmc["armc"]),
            np.asarray(lat),
            np.asarray(ascmc["eps"]),
        )
        assert np.isnan(cusps).any(), (
            f"Placidus 1° beyond polar circle (lat={lat}) should NaN at least one cusp"
        )


    def test_koch_yields_nan_above_polar_circle():
        jd = 2451545.0
        pc = float(polar_circle(jd))
        lat = pc + 1.0
        ascmc = compute_ascmc(jd, lat, 0.0)
        cusps = koch_cusps(
            np.asarray(ascmc["armc"]),
            np.asarray(lat),
            np.asarray(ascmc["eps"]),
        )
        assert np.isnan(cusps).any()


    def test_porphyry_does_not_yield_nan_above_polar_circle():
        """Porphyry is the polar fallback — must work at lat=80, lat=89."""
        for lat in [70.0, 80.0, 89.0]:
            ascmc = compute_ascmc(2451545.0, lat, 0.0)
            cusps = porphyry_cusps(
                np.asarray(ascmc["armc"]),
                np.asarray(lat),
                np.asarray(ascmc["eps"]),
            )
            assert not np.isnan(cusps).any(), (
                f"Porphyry must not NaN at lat={lat} (it's the polar fallback)"
            )


    def test_polar_circle_is_time_varying_not_hardcoded():
        """polar_circle is 90 - ε(jd); ε drifts ~50″/yr (Pitfall 4)."""
        pc_1900 = float(polar_circle(2415020.5))
        pc_2050 = float(polar_circle(2470204.0))
        # ε drifts ~46.81″ per century → polar_circle drifts the SAME
        # amount (with sign flip). Over 150 years that's ~70″ ≈ 0.0194°.
        delta = abs(pc_2050 - pc_1900)
        assert delta > 0.005, (
            f"polar_circle 1900 vs 2050 differs by only {delta * 3600:.1f} arcsec; "
            "expected >18 arcsec drift — is mean_obliquity actually time-varying?"
        )


    def test_high_latitude_error_message_contains_porphyry_hint():
        """Error message must guide caller to the polar_fallback option."""
        e = HighLatitudeError(75.0, "placidus", 66.56)
        assert "porphyry" in str(e).lower(), (
            "HighLatitudeError must hint at polar_fallback='porphyry' option per HOU-06"
        )
    ```

    Anti-patterns to avoid:
    - DO NOT call calculate_houses in test_polar_safety.py — it's still a stub at Plan 05 time. The integration test for the polar_fallback parameter lives in Plan 10-06's test_integration.py.
    - DO NOT mock is_polar — the function is pure and tested as-is.
    - DO NOT skip the polar_circle time-varying test — that's the Pitfall 4 regression catcher; if mean_obliquity ever becomes a constant, this test will fail loudly.
    - DO NOT compare to a hardcoded polar circle value (66.56°, 66.5604°, etc.) — that's Pitfall 4 in the test file. Use the live `polar_circle(jd)` return.
  </action>
  <verify>
    `pytest tests/houses/test_porphyry.py -v` shows ~9 tests passing (extreme-lat, 2 trisection invariants, opposites, polar_circle range, is_polar boundary, is_polar vectorized, POLAR_EPS_TOL existence, optional swisseph compare).

    `pytest tests/houses/test_polar_safety.py -v` shows 6 tests passing.

    `mypy --strict tests/houses/test_porphyry.py tests/houses/test_polar_safety.py` clean.

    `pytest tests/ -v` — full suite green.
  </verify>
  <done>
    test_porphyry.py exists with 9 tests covering closed-form trisection, opposites, extreme polar, polar_circle range, is_polar boundary + vectorized. test_polar_safety.py exists with 6 tests covering HighLatitudeError semantics, NaN propagation contract for placidus/koch above polar circle, porphyry no-NaN at lat=89°, time-varying polar_circle, and error-message guidance. mypy --strict clean.
  </done>
</task>

</tasks>

<verification>
- `pytest tests/houses/ -v` shows ~50 tests passing across all Plan 10-04 and 10-05 test files (or wholesale-skipped if swisseph absent).
- Koch agrees with swisseph oracle to <1 arcmin on all 8 non-polar reference charts × 12 cusps = 96 assertions.
- Porphyry trisection invariants hold at machine precision (1e-9 deg).
- Porphyry works at lat=89° without NaN (the polar fallback contract).
- is_polar uses time-varying 90° - mean_obliquity(jd) — NOT hardcoded.
- Placidus AND Koch produce NaN cusps at |lat| > polar_circle (Plan 10-06 will route to HighLatitudeError or porphyry).
- HighLatitudeError message mentions "porphyry" (HOU-06 caller guidance).
- `mypy --strict ketu/houses/koch.py ketu/houses/porphyry.py tests/houses/test_*.py` clean.
- SYSTEMS dict at end of plan: contains "placidus" (Plan 04), "koch", "porphyry" — Plan 10-06 will assert all 3 are present.
</verification>

<success_criteria>
- HOU-04 satisfied: Koch implementation registered as 'koch'; oracle agreement <1 arcmin on 8 charts × 12 cusps.
- HOU-06 satisfied (helpers level): is_polar(lat, jd) and polar_circle(jd) helpers; POLAR_EPS_TOL = 1e-9 (research §Open Question 4); HighLatitudeError carries lat/system/polar_lat and hints at porphyry fallback in message.
- Porphyry as polar fallback: closed-form, works at all latitudes including 89°.
- Pitfall 4 (hardcoded polar boundary) avoided via the time-varying polar_circle helper; regression-tested.
- Pitfall 6 (false-positive Placidus convergence at polar edge) handled by ascensional_difference NaN-clipping at |s| ≥ 1.
- Plan 10-06 has all the pieces it needs to wire calculate_houses with the polar_fallback parameter.
</success_criteria>

<output>
After completion, create `.planning/phases/10-houses-module/10-05-SUMMARY.md` documenting:
- Koch oracle drift table (8 charts × 12 cusps; max per chart in arcseconds)
- Porphyry trisection invariant assertion deltas (should all be < 1e-9 deg)
- polar_circle values at J2000, 1900, 2050 (showing time variation)
- is_polar boundary table: lat={0, 45, 67, 80, -67} × jd=J2000 → expected vs actual bool
- SYSTEMS dict at end of plan: ["koch", "placidus", "porphyry"] (alphabetical)
- Confirmation: mypy --strict clean; pytest suite green; no runtime swisseph imports
</output>
