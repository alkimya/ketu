---
phase: 10-houses-module
plan: 03
subsystem: houses
tags: [numpy, structured-array, registry-pattern, ascmc, vertex, swisseph-oracle]

# Dependency graph
requires:
  - phase: 10-01
    provides: apparent-GST sidereal_time (Meeus eq. 12.6) — ARMC computation depends on this
  - phase: 10-02
    provides: tests/houses/conftest.py with reference_charts + loaded_reference_snapshot fixtures (oracle JSON snapshot for 8 non-polar charts × 3 systems)
provides:
  - ketu.houses subpackage skeleton (HOU-02 + HOU-05)
  - HOUSES_DTYPE structured array (9 fields incl. cusps (12,) subarray)
  - HighLatitudeError exception (ValueError subclass with lat/system/polar_lat attrs)
  - SYSTEMS dict + register decorator (case-insensitive) + get_system dispatch
  - compute_ascmc / compute_armc (vectorized closed-form ASC/MC/ARMC/Vertex)
  - _ecliptic.py internal helpers (ra_to_lambda / lambda_to_ra / ascensional_difference)
  - calculate_houses / house_of public API stubs (NotImplementedError until Plan 10-06)
  - 28 new tests (5 dtype + 5 registry + 18 ascmc) — all passing at <1 arcmin oracle agreement on ASC/MC/ARMC
affects: [10-04 placidus-implementation, 10-05 koch-porphyry-polar, 10-06 integration-stub-removal]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Registry pattern for pluggable house systems: SYSTEMS dict + @register('name') decorator + get_system dispatch — new systems plug in without touching dispatch logic"
    - "Vectorized closed-form ASC/MC/ARMC/Vertex via np.arctan2 (Pitfall 2 avoided); broadcast over arbitrary leading shape; scalar in → 0-d out"
    - "Internal helpers prefixed with underscore (_ecliptic.py) to signal non-public API surface"
    - "Stub raise NotImplementedError pattern for public API entry points whose bodies land in later plans (calculate_houses, house_of in Plan 10-06)"

key-files:
  created:
    - "ketu/houses/__init__.py — public API surface (5 names + 2 stubbed funcs)"
    - "ketu/houses/core.py — HOUSES_DTYPE + HighLatitudeError"
    - "ketu/houses/registry.py — SYSTEMS dict + register/get_system"
    - "ketu/houses/_ecliptic.py — RA↔ecliptic-longitude helpers + ascensional_difference"
    - "ketu/houses/ascmc.py — compute_armc + compute_ascmc (vectorized closed-form)"
    - "tests/houses/test_dtype.py — 6 structural tests"
    - "tests/houses/test_registry.py — 5 dispatch/cleanup tests"
    - "tests/houses/test_ascmc.py — 17 oracle/shape/identity tests"
  modified:
    - "ketu/__init__.py — re-export 5 new public names (HOUSES_DTYPE, HighLatitudeError, HOUSE_SYSTEMS, calculate_houses, house_of)"
    - "pyproject.toml — add ketu.houses to [tool.setuptools].packages"

key-decisions:
  - "Vertex formula corrected to use anti-meridian (armc + 180) + co-latitude (90 - lat) — plan reference text omitted the anti-meridian shift; without it the result is the antivertex (off by ~168°). Empirical fix verified against pyswisseph oracle at J2000_Paris: 0.42 arcsec delta. Documented in ascmc.py docstring with cross-check note."
  - "compute_armc lifts scalar sidereal_time via list-comprehension over ravelled broadcast shape — pragmatic shim, microseconds for 1000 charts. Plan 10-06 may vectorize sidereal_time directly if profiling reveals a bottleneck."
  - "SYSTEMS aliased to HOUSE_SYSTEMS in ketu/__init__.py to avoid clobbering future SYSTEMS globals — consumers use ketu.HOUSE_SYSTEMS or import from ketu.houses directly."
  - "ASC/MC/ARMC tolerance held at 1 arcmin (HOU-01 spec); Vertex tolerance widened to 5 arcmin per Open Question 3 (advisory until proven tight at all latitudes). Worst-case Vertex delta observed: 15.5 arcsec at J2000_Tokyo — well inside the 300 arcsec advisory band."
  - "Internal helpers (_ecliptic.py) ship with both ra_to_lambda and the inverse lambda_to_ra even though Plan 10-03 only uses neither directly — they are the building blocks Plans 10-04 (Placidus) and 10-05 (Koch) will consume; landing them here keeps the surface stable across plan boundaries."

patterns-established:
  - "Houses-systems registry: @register('name') populates SYSTEMS dict; calculate_houses dispatches via get_system(name) — Plans 04/05 plug in without touching this module"
  - "ASC/MC/ARMC/Vertex closed-form via np.arctan2 broadcast — vectorized over (jd, lat, lon), 0-d out for scalar in, leading shape preserved for ndarray in"
  - "Stub-raise NotImplementedError for not-yet-wired public API; signature + docstring + .. note:: STUB header land in advance so consumers can read the contract before Plan 10-06"
  - "Mypy --strict explicit ndarray return casts: assign to typed local then return (`result: np.ndarray = ...`) — required because numpy ufunc % 360.0 path returns Any otherwise"

# Metrics
duration: 7m 48s
completed: 2026-05-07
---

# Phase 10 Plan 03: Registry / DTYPE / ASC-MC Summary

**ketu.houses subpackage scaffold — registry-pattern dispatch, HOUSES_DTYPE (9 fields incl. cusps (12,)), HighLatitudeError, and vectorized closed-form ASC/MC/ARMC/Vertex agreeing with pyswisseph oracle to <1 arcmin on 8/8 non-polar charts**

## Performance

- **Duration:** 7m 48s
- **Started:** 2026-05-07T07:23:48Z
- **Completed:** 2026-05-07T07:31:36Z
- **Tasks:** 3
- **Files modified:** 10 (8 created in ketu/houses/ and tests/houses/, 2 modified at top level)

## Accomplishments

- **HOU-02 (registry pattern) landed**: `SYSTEMS` dict + `@register("name")` decorator + `get_system` dispatch with case-insensitive lookup and helpful ValueError on unknown name. Plans 04/05 plug in without touching `calculate_houses`.
- **HOU-05 (structured array) landed**: `HOUSES_DTYPE` with 9 fields including the `cusps (12,)` subarray. Vectorized construction works (outer shape `(N,)` → `cusps` shape `(N, 12)`).
- **Closed-form ASC/MC/ARMC/Vertex implemented and oracle-verified**: All 8 non-polar reference charts agree with pyswisseph to <1 arcmin on ASC/MC/ARMC; Vertex agrees to <5 arcmin (advisory band per Open Question 3). Vectorized over `(jd, lat, lon)` of any broadcast shape via `np.arctan2`.
- **HighLatitudeError exception class**: ValueError subclass with `lat` / `system` / `polar_lat` attrs and a helpful message hinting at `polar_fallback="porphyry"`.
- **Public API surface declared**: `calculate_houses` and `house_of` stubs raise `NotImplementedError` with explicit "wired in Plan 10-06" message — signatures and docstrings are stable now.
- **538 tests pass**: previous 510 (incl. Plan 10-01 16, Plan 10-02 6) + 28 new from Plan 10-03; mypy --strict clean across 8 source/test files; no runtime swisseph imports in `ketu/houses/` (pure-NumPy contract preserved).

## Task Commits

Each task was committed atomically:

1. **Task 1: Create ketu/houses/ subpackage with registry, dtype, exception, and public API skeleton** — `71c30ce` (feat)
2. **Task 2: Implement vectorized closed-form ASC/MC/ARMC/Vertex** — `fb2a161` (feat)
3. **Task 3: Add tests for dtype, registry, and ASC/MC/Vertex oracle agreement** — `a5992dc` (test)

## Files Created/Modified

### Created (ketu/houses/)
- `ketu/houses/__init__.py` — public API: HOUSES_DTYPE, HighLatitudeError, SYSTEMS, calculate_houses (stub), house_of (stub).
- `ketu/houses/core.py` — HOUSES_DTYPE structured dtype + HighLatitudeError exception.
- `ketu/houses/registry.py` — SYSTEMS dict + register decorator + get_system dispatch.
- `ketu/houses/_ecliptic.py` — RA↔ecliptic-longitude helpers + ascensional_difference (NaN at polar boundary).
- `ketu/houses/ascmc.py` — compute_armc + compute_ascmc (vectorized closed-form via np.arctan2).

### Created (tests/houses/)
- `tests/houses/test_dtype.py` — 6 structural tests covering field names, cusps subarray (12,), N-shape construction, U10 system capacity, 0-d construction, HighLatitudeError attrs.
- `tests/houses/test_registry.py` — 5 tests: register insertion, lowercase normalization, case-insensitive lookup, ValueError-with-options, dict-ness invariant.
- `tests/houses/test_ascmc.py` — 17 tests: 8 oracle-arcmin parametrize × ASC/MC/ARMC + 5 vertex-5arcmin parametrize + vectorized-shape + 0-d-shape + ARMC-identity + Paris-sanity-band.

### Modified
- `ketu/__init__.py` — re-export 5 new public names (HOUSES_DTYPE, HighLatitudeError, HOUSE_SYSTEMS, calculate_houses, house_of) and append to `__all__`.
- `pyproject.toml` — add `"ketu.houses"` to `[tool.setuptools].packages`.

## HOUSES_DTYPE field-by-field breakdown

| Field    | NumPy dtype | Shape   | Purpose                                          |
| -------- | ----------- | ------- | ------------------------------------------------ |
| `jd`     | f8          | scalar  | Julian Date, UT                                  |
| `lat`    | f8          | scalar  | Geographic latitude, deg                         |
| `lon`    | f8          | scalar  | Geographic longitude (east-positive), deg        |
| `system` | U10         | scalar  | House system name (lowercase string)             |
| `cusps`  | f8          | (12,)   | 12 house cusps in deg [0, 360) — subarray field  |
| `asc`    | f8          | scalar  | Ascendant, deg [0, 360)                          |
| `mc`     | f8          | scalar  | Medium Coeli, deg [0, 360)                       |
| `armc`   | f8          | scalar  | Right Ascension of Medium Coeli, deg [0, 360)    |
| `vertex` | f8          | scalar  | Vertex, deg [0, 360)                             |

For an outer shape `(N,)` array, `arr["cusps"]` has shape `(N, 12)` — verified in `test_dtype_supports_vectorized_construction`.

## Oracle agreement (pyswisseph cross-check) — non-polar charts

All deltas in **arcseconds** (1 arcmin = 60 arcsec; HOU-01 spec for ASC/MC/ARMC = <60 arcsec; advisory for Vertex = <300 arcsec).

| Label             | ASC Δ″ | MC Δ″  | ARMC Δ″ | Vertex Δ″ |
| ----------------- | -----: | -----: | ------: | --------: |
| J2000_Greenwich   |  8.113 |  0.515 |   0.108 |     0.323 |
| J2000_Paris       |  7.438 |  0.604 |   0.108 |     0.420 |
| J2000_Sydney      |  4.071 |  0.600 |   0.108 |     0.736 |
| J2000_Tokyo       |  0.553 |  0.936 |   0.108 |    15.482 |
| J2000_BuenosAires |  1.089 |  1.151 |   0.108 |    12.570 |
| J2000_Equator     |  0.370 |  0.515 |   0.108 |     0.000 |
| 1900_NewYork      |  0.749 |  0.170 |   0.235 |     3.391 |
| 2050_Reykjavik    | 51.486 |  0.857 |   1.938 |     1.588 |

**Worst case ASC**: 51.5 arcsec @ 2050_Reykjavik (lat 64.1°N, near polar circle) — within HOU-01 60-arcsec spec but tight. Plan 10-05 (Koch + polar fallback) will need to monitor this band.

**Worst case Vertex**: 15.5 arcsec @ J2000_Tokyo — well inside the 300-arcsec advisory band.

## Decisions Made

- **Vertex formula corrected** (anti-meridian shift). Plan reference text in 10-RESEARCH.md described Vertex as "ASC formula with co-latitude (90 - lat) substituted for lat" — but empirically that yields the *antivertex*, off from the swisseph oracle by ~168°. The correct closed form evaluates the ASC formula at `armc + 180` (anti-meridian) with `90 - lat` (co-latitude). Documented in `ascmc.py` docstring with the cross-check delta (0.42 arcsec @ J2000_Paris). This is **deviation Rule 1 (auto-fix bug)** — the bug was in the plan's reference text, not in user-facing code, but the fix is the same: get the production formula right.
- **compute_armc list-comp shim**: `sidereal_time` is currently scalar-only. Rather than vectorize it as scope creep, `compute_armc` lifts via list comprehension over `np.broadcast_arrays(jd, lon).ravel()` then reshapes. Cost: microseconds for 1000 charts. Note for Plan 10-06 in the docstring.
- **HOUSE_SYSTEMS alias** in `ketu/__init__.py`: `from ketu.houses import SYSTEMS as HOUSE_SYSTEMS` — the bare name `SYSTEMS` is too generic for a top-level export; `HOUSE_SYSTEMS` reads as namespaced even at the package root. Within `ketu.houses` the name remains `SYSTEMS` (registry-internal convention).
- **Vertex tolerance at 5 arcmin (advisory)**, not 1 arcmin. Worst observed: 15.5 arcsec — comfortably below the advisory band but above the spec band, so the wider tolerance is honest. Open Question 3 will be revisited in Plan 10-06.
- **Internal helpers prefix `_ecliptic.py`**: ra_to_lambda / lambda_to_ra / ascensional_difference are building blocks for Plans 10-04 and 10-05; landing them with the underscore prefix at this plan boundary signals they are not part of the public API.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Vertex formula required anti-meridian shift**

- **Found during:** Task 2 (compute_ascmc empirical sanity check against pyswisseph snapshot)
- **Issue:** Plan reference Vertex formula was `atan2(cos(armc), -[sin(eps)*tan(90-lat) + cos(eps)*sin(armc)])`, which yields the antivertex (off by ~168° from the oracle). At J2000_Paris: my formula → 22.06°; oracle → 190.12°.
- **Fix:** Evaluate the ASC closed form at `armc + 180` (anti-meridian) with `90 - lat` (co-latitude). At J2000_Paris: corrected formula → 190.1196° vs oracle 190.1198° (Δ 0.42 arcsec).
- **Files modified:** `ketu/houses/ascmc.py` (docstring updated to record the correction; `armc_anti_rad = np.deg2rad((armc + 180) % 360)` substituted for `armc_rad` in the Vertex computation only).
- **Verification:** All 5 non-equator charts in `test_vertex_matches_swisseph_within_5_arcmin` pass; worst case 15.5 arcsec at J2000_Tokyo (well inside 300 arcsec advisory band).
- **Committed in:** `fb2a161` (Task 2 commit — initial implementation already had the fix; the deviation was in the plan reference text, not in the staged code).

**2. [Rule 3 - Blocking] Mypy --strict explicit ndarray return casts in `_ecliptic.py`**

- **Found during:** Task 1 verification (`python -m mypy --strict ketu/houses/`)
- **Issue:** mypy --strict reported `error: Returning Any from function declared to return "ndarray[...]"` on the three `_ecliptic.py` functions. Root cause: `np.rad2deg(...) % 360.0` returns `Any` from numpy's stubs (PEP 604 union narrowing not yet wired through ufunc returns).
- **Fix:** Assign result to a typed local before returning: `result: np.ndarray = np.rad2deg(lam) % 360.0; return result`. Same pattern applied to `lambda_to_ra` and `ascensional_difference`.
- **Files modified:** `ketu/houses/_ecliptic.py` (3 return statements).
- **Verification:** `python -m mypy --strict ketu/houses/` reports `Success: no issues found in 4 source files`. The same pattern was reused in `ascmc.py` proactively (no mypy errors there in the first place).
- **Committed in:** `71c30ce` (Task 1 commit — the typed-local pattern was inlined before the first commit).

---

**Total deviations:** 2 auto-fixed (1 Rule 1 bug fix, 1 Rule 3 blocking mypy issue)

**Impact on plan:** Both auto-fixes essential. The Vertex correction is a real production bug fix — without it `compute_ascmc` would have shipped a 168°-off Vertex; the test suite would have caught it (snapshot check), but the plan would have stalled on the test step. The mypy typed-local pattern is a recurring NumPy + mypy --strict friction point that future plans will reuse. No scope creep — both changes are tight to the affected functions.

## Issues Encountered

- **Plan dependency declared but Plan 10-02 hadn't published commits when this plan started.** Plan 10-02 had executed in parallel (Wave 2 strategy) and produced its untracked artifacts on disk (`tests/houses/conftest.py`, `tests/houses/fixtures/reference_charts.json`, `tests/houses/test_oracle_smoke.py`), but had not yet committed them. I consumed the on-disk fixtures rather than blocking. The `test_ascmc.py` file references `reference_charts` and `loaded_reference_snapshot` fixtures — those will resolve once Plan 10-02 commits. Plan 10-03 commits do **not** include any tests/houses/conftest.py or fixtures/ artifacts (those are 10-02's responsibility).

- **No swisseph fallback for ASC oracle tests.** If `swisseph` is uninstalled in some future env, the entire `tests/houses/` directory skips at collection (per the Plan 10-02 conftest's `pytest.importorskip`). This is intentional and matches the established Phase 8 dual-import + importorskip pattern.

## Verification

- `python -c "from ketu.houses import HOUSES_DTYPE, HighLatitudeError, SYSTEMS, calculate_houses, house_of; print(HOUSES_DTYPE.names, len(SYSTEMS))"` → prints all 9 field names and `0` (SYSTEMS empty at this plan boundary; Plans 04/05 will populate). ✅
- `pytest tests/houses/ -v` → 50 tests pass (16 from 10-01 LST + 6 from 10-02 oracle-smoke + 28 from 10-03). ✅
- `pytest tests/ -q` → 538 tests pass (510 baseline + 28 new); coverage 97.50%. ✅
- `mypy --strict ketu/houses/ tests/houses/test_dtype.py tests/houses/test_registry.py tests/houses/test_ascmc.py` → `Success: no issues found in 8 source files`. ✅
- `grep -nE "^(import|from).*swisseph" ketu/houses/*.py` → empty (no runtime swisseph imports). ✅
- `grep "ketu.houses" pyproject.toml` → matches the `[tool.setuptools].packages` line. ✅

## SYSTEMS dict at plan boundary

After Plan 10-03 lands, `SYSTEMS` is **empty** (`len(SYSTEMS) == 0`). Plans 10-04 (Placidus) and 10-05 (Koch + Porphyry) populate it with `placidus`, `koch`, and `porphyry` keys. Plan 10-06 wires the dispatch in `calculate_houses` and `house_of`.

## Next Phase Readiness

- **Plan 10-04 (Placidus)** can begin: registry signature `(armc, lat, eps) -> cusps[..., 12]` is documented; ASC/MC/ARMC available via `compute_ascmc`; `_ecliptic.ra_to_lambda` + `_ecliptic.ascensional_difference` available. Placidus iteration consumes ARMC and adds intermediate-cusp formulas.
- **Plan 10-05 (Koch + Porphyry)** can begin: same registry contract; HighLatitudeError exception ready for `polar_fallback="raise"` path; closed-form Porphyry computes cusps as 30°/60° splits between MC/IC and ASC/DSC, all of which are available from `compute_ascmc`.
- **Plan 10-06 (integration + stub removal)** can wire `calculate_houses` body: `eps, armc = compute_ascmc(...)["eps"], compute_ascmc(...)["armc"]; cusps = get_system(system)(armc, lat, eps); ...; result = np.empty(shape, dtype=HOUSES_DTYPE); ...`.
- **Reykjavik 51 arcsec ASC delta** is a yellow flag for high-latitude precision — within HOU-01 spec but tight. Plan 10-04 should add a regression fence at lat ≥ 60° and Plan 10-05 should ensure Porphyry-fallback kicks in well before 64°.

---
*Phase: 10-houses-module*
*Plan: 03 (registry-dtype-ascmc)*
*Completed: 2026-05-07*

## Self-Check: PASSED

- `ketu/houses/__init__.py` — FOUND
- `ketu/houses/core.py` — FOUND
- `ketu/houses/registry.py` — FOUND
- `ketu/houses/_ecliptic.py` — FOUND
- `ketu/houses/ascmc.py` — FOUND
- `tests/houses/test_dtype.py` — FOUND
- `tests/houses/test_registry.py` — FOUND
- `tests/houses/test_ascmc.py` — FOUND
- Commit `71c30ce` (Task 1) — FOUND
- Commit `fb2a161` (Task 2) — FOUND
- Commit `a5992dc` (Task 3) — FOUND
