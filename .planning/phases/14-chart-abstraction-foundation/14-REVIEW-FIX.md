---
phase: 14
fixed_at: 2026-05-09T00:00:00Z
review_path: .planning/phases/14-chart-abstraction-foundation/14-REVIEW.md
iteration: 1
findings_in_scope: 8
fixed: 7
skipped: 1
status: partial
---

# Phase 14 — Code Review Fix Report

**Fixed at:** 2026-05-09
**Source review:** `.planning/phases/14-chart-abstraction-foundation/14-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 8 (3 Warnings + 5 Info, fix_scope=all)
- Fixed: 7
- Skipped: 1 (IN-05, explicitly out-of-scope per the review)
- Final test count: 858 (was 844; +14 net new ratchet tests)
- Final coverage: 98.08%
- mypy --strict: clean on `ketu/charts/`

## Fixed Issues

### WR-01: Convention D-13 `Sun == ASC = day` violée par le code (sunrise-inclusive incomplète)

**Files modified:** `ketu/charts/api.py`, `tests/charts/test_is_day_chart.py`
**Commit:** `40696eb`
**Applied fix:** Refactored `is_day_chart` to derive sect from a closed-form Ascendant (`compute_ascmc`) and apply the ASC-delta test `(asc - sun_lon) mod 360 < 180` instead of mapping the Sun through Placidus/Porphyry cusps and checking `sun_house >= 7`. The new formulation honours D-13 literally: a Sun exactly on the ASC (delta=0) resolves to **day** (sunrise-inclusive); a Sun exactly on the DESC (delta=180) resolves to **night** (sunset-exclusive). The `house_of(sun, cusps) >= 7` formulation was incorrect at the boundary because `house_of` maps `cusps[i] -> house i+1`, so Sun at ASC fell in house 1 and was classified as night. Imports adjusted accordingly (added `compute_ascmc`, dropped `house_of`). Updated the docstring "Sect convention", "Polar safety", and "Geometric definition" sections to reflect the new ASC-based, system-independent semantic.

**Note:** The reviewer's recommended formula `(sun_lon - asc) mod 360 < 180` was geometrically inverted (it would return night for Paris J2000 noon). Cross-checked the correct formula against the existing `test_is_day_chart_sunrise_inclusive_pragmatic_convention` test (Sun at `asc - 0.01` -> house 12 = day) and the Paris J2000 noon/midnight fixtures, confirming `(asc - sun_lon) mod 360 < 180` matches the diurnal-arc geometry where the rotating ASC sweeps eastward past a roughly-stationary Sun. **Status fixed: requires human verification** — the diurnal-arc reasoning is documented in the docstring and inline comments, and is pinned by the existing Paris noon/midnight/sunrise-inclusive test suite, but a fresh pair of eyes on the formula direction is recommended given the reviewer's note went the other way.

**Side effect (pre-existing test rewritten, not regression):** The polar consistency test `test_is_day_chart_consistency_polar_via_explicit_porphyry` was renamed to `test_is_day_chart_consistency_polar_via_asc_delta` and updated to ratchet the new system-independent ASC-delta semantic. The previous version asserted equivalence with `house_of(sun, polar_porphyry_cusps) >= 7`, which is broken at polar latitudes because Porphyry's polar fallback shifts `cusps[6] = ASC` (instead of `cusps[0] = ASC`). lat=80 N J2000 noon is now correctly reported as **night** (polar winter, Sun physically below horizon at declination ~-23°), where the previous coupling returned a spurious **day**.

### WR-02: Inconsistance cross-API silencieuse `is_day_chart` (Placidus hardcodé) vs `compute_chart`

**Files modified:** `tests/charts/test_is_day_chart.py`
**Commit:** `eea7bbb`
**Applied fix:** Added a parametrized cross-system consistency ratchet `test_is_day_chart_independent_of_caller_house_system` covering placidus / koch / porphyry × 4 non-polar fixtures (Paris, Sydney, New York, Tokyo). At non-polar latitudes the quadrant systems all satisfy `cusps[0] == ASC` and `cusps[6] == ASC + 180`, so `house_of(sun, cusps) >= 7` is mathematically equivalent to the ASC-delta sect formula; `is_day_chart` must agree with this equivalence for *every* registered system. When Phase 15 adds Whole Sign / Equal (where `cusps[6] != ASC + 180`), this ratchet will guard the contract: any regression making `is_day_chart` peek at the caller's house system will surface as a divergence. The implementation itself was already system-independent after WR-01 (uses `compute_ascmc` directly, never calls `calculate_houses`); this commit only adds the protective ratchet.

### WR-03: Tolérance `HOUSES_INLINE_TOL_DEG = 1e-9` plus laxiste que la docstring promise

**Files modified:** `tests/charts/test_compute_chart.py`
**Commit:** `c3b6600`
**Applied fix:** Removed the `HOUSES_INLINE_TOL_DEG = 1e-9` constant and replaced the tolerance-based comparison in `test_compute_chart_houses_inline_matches_calculate_houses` with strict bit-exact equality: `numpy.testing.assert_array_equal` for cusps and Python `==` for asc/mc/armc/vertex. This pins the D-03 "houses inline = bit-for-bit" contract literally rather than testing at micro-arcsecond tolerance. Updated the leading comment block to document the rationale (compute_chart calls calculate_houses once and copies fields directly; values are the same fp64 in memory). All 24 parametrized cases (placidus / koch / porphyry × 8 fixtures) pass with strict equality.

### IN-01: Stockage de `system.lower()` dans CHART_DTYPE crée un drift potentiel

**Files modified:** `ketu/charts/api.py`
**Commit:** `457e48e`
**Applied fix:** Replaced `out["system"] = system.lower()` with `out["system"] = houses["system"]` so `compute_chart` reads the canonical normalised system name back from `calculate_houses` rather than re-normalising locally. Single source-of-truth: any future change to `calculate_houses`' normalisation rule (alias resolution, kebab-case, etc.) auto-propagates. The existing `test_compute_chart_meta_fields_lowercased_system` stays green (calculate_houses lowercases too).

### IN-02: `aspect_orbs` peut contenir des valeurs négatives non documentées

**Files modified:** `ketu/charts/core.py`
**Commit:** `0d823f5`
**Applied fix:** Updated the `aspect_orbs` docstring entry in CHART_DTYPE to explicitly document the **signed** orb convention: `aspect_angle - distance` (positive when distance < aspect_angle, negative when distance > aspect_angle), inherited from `calculate_aspects_vectorized`. Added a recommendation to use `np.abs(chart["aspect_orbs"])` for absolute-orb filters. No code change — the signed-orb behaviour in `calculate_aspects_vectorized` is out-of-scope for Phase 14 and intentional.

### IN-03: `_BODY_COUNT = 13` constant mais pas dérivé de `ketu.core.bodies`

**Files modified:** `ketu/charts/api.py`, `tests/charts/test_dtype.py`
**Commit:** `9fbe507`
**Applied fix:** Replaced the magic literal `_BODY_COUNT: int = 13` with `_BODY_COUNT: int = len(_CANONICAL_BODIES)` (where `_CANONICAL_BODIES = ketu.core.bodies`). Added a runtime ratchet `test_body_count_frozen_at_thirteen` in `tests/charts/test_dtype.py` that pins the v1.2 D-08 freeze: if/when `ketu.core.bodies` grows (e.g. Chiron in v1.3), the test goes red and forces the human reviewer to walk through every CHART_DTYPE subarray shape (`body_lons` / `body_lats` / `body_speeds` / `aspect_matrix` / `aspect_orbs`) before lifting the freeze. CHART_DTYPE subarray literals stay as explicit `(13,)` / `(13, 13)` per IN-03 guidance — they are the documented contract surface.

### IN-04: Test `test_compute_chart_polar_fallback_invalid_raises_value_error` dépend d'un détail interne

**Files modified:** `tests/charts/test_compute_chart.py`
**Commit:** `21c19c5`
**Applied fix:** Parametrized the polar_fallback invalid-choice test over both a non-polar input (Paris, lat=48.86) and a polar input (lat=80, lon=0). Both trajectories are now pinned: a future refactor that moves `polar_fallback` validation into the polar branch only would break the non-polar case red here; a refactor that drops eager validation entirely would break the polar case red. Pure test-ratchet improvement; no production-code change.

## Skipped Issues

### IN-05: `RuntimeWarning: invalid value encountered in divide` dans `orbital.py:733` carry-over

**File:** `ketu/ephemeris/orbital.py:733`
**Reason:** Explicitly out-of-scope per the review. The finding itself states: "Out-of-scope phase 14 (carry-over pré-existant). [...] **Pour Phase 14 stricto sensu : aucune action**, c'est documenté correctement dans les SUMMARY." A dedicated ticket is suggested for `ketu/ephemeris/orbital.py:733` (handling `r -> 0` explicitly with `np.where(r == 0, np.nan, np.arcsin(z / r))` or a guard), to be addressed when Phase 19 (Arabic Parts) might surface NaN propagation through derived `lots`.
**Original issue:** `np.arcsin(z / r)` with `r = 0` produces `NaN` and emits `RuntimeWarning`. 61 warnings on charts tests trace back to this single line. Empirically no NaN escapes to `body_lons` / `body_lats` for the tested cases, but the safety is "by chance" rather than guaranteed.

---

_Fixed: 2026-05-09_
_Fixer: Claude (gsd-code-fixer) en persona Sophie Chen_
_Iteration: 1_
