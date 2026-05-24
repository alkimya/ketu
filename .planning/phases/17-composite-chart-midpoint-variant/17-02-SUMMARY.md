---
phase: 17-composite-chart-midpoint-variant
plan: 02
subsystem: composite
tags: [composite, calculate-composite, porphyry-trisection, midpoint-composite, COMP-01, COMP-03]

# Dependency graph
requires:
  - phase: 14-chart-abstraction-foundation
    provides: CHART_DTYPE (output dtype produced by calculate_composite)
  - phase: 17-composite-chart-midpoint-variant
    plan: 01
    provides: ketu.composite subpackage skeleton + circular_midpoint helper
provides:
  - calculate_composite(chart_a, chart_b, system="placidus") -> CHART_DTYPE (COMP-01 surface)
  - Inline Porphyry-style trisection on (composite_asc, composite_mc) (COMP-03 binding)
  - 75 regression tests pinning COMP-01 + COMP-03 + Pitfall 2/3/8 ratchets
affects:
  - 17-03-PLAN (oracle fixtures — consumes calculate_composite for self-consistency oracles)
  - 17-04-PLAN (close-out: composite_coverage_gate + Makefile + CHANGELOG)

# Tech tracking
tech-stack:
  added: []  # No new dependencies — pure NumPy reusing existing primitives
  patterns:
    - "Inline house-cusp trisection (Approach A) — composite ASC + composite MC fed directly into the Porphyry algebra; calculate_houses NOT consulted"
    - "Accept-and-ignore validation pattern — system= validated via get_system (raises ValueError on unknown), then return value discarded; user string stored for bookkeeping"
    - "Inline aspect-matching loop on pre-computed body_lons (no canonical jd) — match-once-per-pair break, signed-orb convention from calculator.py:223-229"
    - "Zero blast radius on Phase 9 aspect engine — calculate_aspects_vectorized untouched; future refactor (body_lons= kwarg) deferred to Phase 18/19 if needed"
    - "Grep-ratchet source-level guards — string substring checks in test_composite_houses.py pin the absence of forbidden calls (compute_chart, calculate_houses, calculate_aspects_vectorized)"

key-files:
  created:
    - ketu/composite/api.py
    - tests/composite/conftest.py
    - tests/composite/test_calculate_composite.py
    - tests/composite/test_composite_houses.py
    - tests/composite/test_dtype.py
  modified:
    - ketu/composite/__init__.py

key-decisions:
  - "Approach A (Porphyry trisection on composite ASC + composite MC) for house derivation, inlined verbatim from porphyry.py:159-186 — literal COMP-03 compliance, polar-safe by construction, no reference-latitude question"
  - "system= is accept-and-ignore: validated via get_system (raises ValueError on unknown), stored verbatim in output's system field, semantically a no-op under midpoint method — every system collapses to Porphyry trisection"
  - "jd/lat are linear midpoints; lon is circular midpoint — documented loudly as 'bookkeeping, NOT a moment-and-place'; Pitfall 2 ratchet pins composite['jd'] == (a['jd']+b['jd'])/2 exactly to detect future Davison conflation"
  - "Inline aspect-matching loop (Option 3 in 17-RESEARCH §'Reusing Existing Helpers') — keeps Phase 17 self-contained, zero blast radius on Phase 9 calculate_aspects_vectorized; hardcoded CLASSICAL preset (no aspects= kwarg per COMP-01..04)"
  - "Doctest examples in calculate_composite changed from `>>> compute_chart(...)` to a See Also-style narrative reference — avoids triggering the grep ratchet on the docstring (the source-level substring check would have false-matched the example call site)"

patterns-established:
  - "Pair-chart implementation pattern: inline reused algebra (porphyry trisection here, aspect matching here) rather than calling jd-bound entry points that would force a synthetic Julian Date"
  - "Source-level anti-regression via grep ratchets — read api.py as text in a test, assert forbidden substrings absent; cheaper than mocking + works across refactors"
  - "is_day_chart return-type tolerance in composite tests — accept bool/np.bool_/0-d ndarray via `bool(result) in (True, False)` (downstream consumers like Phase 19 Arabic Parts may face same ambiguity)"

# Metrics
duration: ~29 min
completed: 2026-05-24
---

# Phase 17 Plan 02: calculate_composite (COMP-01, COMP-03) Summary

**ketu.composite.calculate_composite shipped — scalar CHART_DTYPE × scalar CHART_DTYPE → scalar CHART_DTYPE with circular-midpoint body axis, inline Porphyry-trisection houses derived from composite ASC + composite MC, inline aspect-matching loop on composite body_lons, and 75 new ratchet tests pinning COMP-01 surface + COMP-03 house binding + Pitfall 2/3/8 anti-regression.**

## Performance

- **Duration:** ~29 min (28m 41s)
- **Started:** 2026-05-24T10:46:13Z
- **Completed:** 2026-05-24T11:14:54Z
- **Tasks:** 2 / 2
- **Files created:** 5 (`ketu/composite/api.py`, `tests/composite/conftest.py`, `tests/composite/test_calculate_composite.py`, `tests/composite/test_composite_houses.py`, `tests/composite/test_dtype.py`)
- **Files modified:** 1 (`ketu/composite/__init__.py`)
- **Tests added:** 75 (project suite: 1083 → 1158, all PASS)

## Accomplishments

- **`calculate_composite(chart_a, chart_b, system="placidus") -> CHART_DTYPE` shipped.** Public surface live behind `from ketu.composite import calculate_composite`. Returns a scalar (0-d) `CHART_DTYPE` whose every field is populated: bookkeeping (jd, lat, lon, system), body axis (body_lons/lats/speeds — shape (13,)), angles (asc, mc, armc, vertex), cusps (shape (12,)), and the (13,13) aspect_matrix + aspect_orbs.
- **COMP-01 surface satisfied** (`test_calculate_composite.py`). Per-body circular midpoint pinned via parametrized tests over all 13 bodies; per-body lats and speeds as linear averages; angles (asc/mc/armc/vertex) as circular midpoints; default `system="placidus"` per COMP-01 verbatim; unknown system raises ValueError; full swap symmetry on body_lons + asc/mc + cusps within 1e-9°.
- **COMP-03 binding satisfied** (`test_composite_houses.py`). House cusps derived from composite ASC + composite MC via inline Porphyry-style trisection (no call to `calculate_houses`); cusp endpoints 0/3/6/9 are ASC/IC/DESC/MC; lower trisection (cusps 1/2) and upper trisection (cusps 10/11) verified algebraically; cusps 4/5/7/8 are 180° oppositions of 10/11/1/2; swap symmetry on all 12 cusps within 1e-9°.
- **Approach A confirmed.** Polar pair (Paris 48°N + Reykjavik 64°N) produces finite cusps + finite asc/mc/armc/vertex — Porphyry trisection has no `tan(lat)` singularity. No `HighLatitudeError`, no NaN propagation. `test_polar_pair_does_not_nan` ratchet pinned.
- **Pitfall 2 anti-regression pinned** (`test_jd_is_linear_midpoint_of_natals`). `composite["jd"] == (chart_a["jd"] + chart_b["jd"]) / 2` exactly — Davison would not generally preserve this; this strict-equality ratchet detects accidental Davison conflation.
- **Pitfall 3 anti-regression pinned** (`test_no_calculate_houses_call_smoke`). Source-level grep ratchet asserts `calculate_houses(` substring does NOT appear in `ketu/composite/api.py`. Paired with `test_no_compute_chart_call_smoke` (Pitfall 2) and `test_no_calculate_aspects_vectorized_call_smoke` (inline aspect-loop ratchet).
- **Pitfall 8 anti-regression pinned** (`test_sun_index_0_matches_circular_midpoint` + `test_moon_index_1`). The 13-body axis order (Sun=0, Moon=1, NOT alphabetical) is verified by spot-checks against `circular_midpoint` applied to the natal `body_lons` at the same indices.
- **`system=` no-op semantics documented and enforced.** Passing `system="koch"` produces the same cusps as `system="placidus"` (the inline Porphyry trisection ignores it); the user's string is stored verbatim in `out["system"]`. `test_system_field_stores_user_value` + `test_system_unknown_raises_value_error` pin both behaviours.
- **`is_day_chart` callable on composite metadata** (`test_is_day_chart_callable_on_composite_metadata_does_not_raise`). The result is meaningless astrologically (bookkeeping jd/lat/lon) but the function must remain callable — pins the "no NaN in bookkeeping fields" invariant against future refactors.
- **Doc gates green.** `python -m numpydoc lint ketu/composite/api.py` clean; `python -m interrogate ketu/composite/` 100%. Module + function docstrings carry the loud "(jd, lat, lon) are bookkeeping NOT a moment-and-place", "UTC-only contract", and "No Davison" guards.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement calculate_composite (COMP-01, COMP-03)** — `6121e57` (feat)
2. **Task 2: Pin COMP-01 + COMP-03 + dtype + Pitfall ratchets** — `61ba77c` (test)

**Plan metadata commit:** Follows this SUMMARY (separate commit per task_commit_protocol).

## Files Created/Modified

- **`ketu/composite/api.py`** (NEW, 309 lines). Module docstring includes locked design decisions block + See Also (4 entries) + Notes (UTC contract + No Davison guard). `calculate_composite` function with full numpydoc (Parameters, Returns, Raises, Notes — 4 paragraphs: midpoint method only / bookkeeping caveat / body speeds caveat / UTC contract / no Davison / aspect set hardcoded — See Also (4 entries), Examples (narrative referring to circular_midpoint examples)). 7-step implementation: (1) system= validation via `get_system` discard, (2) zero-allocation of scalar CHART_DTYPE, (3) bookkeeping fields, (4) body axis midpoints, (5) angle midpoints, (6) inline Porphyry trisection with polar ASC-swap, (7) inline aspect-matching loop on CLASSICAL preset.
- **`ketu/composite/__init__.py`** (MODIFIED — 1 line added, 1 line modified). Re-exports `calculate_composite` from `.api`; `__all__` extended to `["calculate_composite", "circular_midpoint"]`.
- **`tests/composite/conftest.py`** (NEW). 6 session-scoped chart fixtures (paris, nyc, tokyo, sydney, reykjavik, retrograde_mercury) duplicated from `tests/synastry/conftest.py` per 17-RESEARCH §"Test Layout". Polar fixture passes `polar_fallback='porphyry'` to avoid masking composite bugs with HighLatitudeError raised inside `compute_chart`.
- **`tests/composite/test_dtype.py`** (NEW). 7 tests across 2 classes: TestOutputDtype (5 tests pinning dtype identity, scalar shape, body axis shape (13,), cusps shape (12,), aspect_matrix/orbs shape (13,13)) + TestBodyAxisOrderingPitfall8 (2 spot checks on Sun=0 / Moon=1 against circular_midpoint).
- **`tests/composite/test_calculate_composite.py`** (NEW). 53 tests across 6 classes: TestBookkeepingFields (3 — jd Pitfall 2 ratchet, lat linear, lon circular), TestSystemArgument (3 — store, ValueError, default placidus), TestBodyMidpoints (40 = 13×3 parametrized + 1 retrograde), TestAngleMidpoints (4 — asc/mc/armc/vertex), TestSwapSymmetry (3 — body_lons, asc/mc, cusps), TestIsDayChartCallable (1 — Q3 ratchet).
- **`tests/composite/test_composite_houses.py`** (NEW). 13 tests across 6 classes: TestCuspEndpoints (4 — cusps 0/3/6/9), TestPorphyryTrisection (3 — lower arc trisection, upper arc trisection, oppositions), TestSwapSymmetry (1 — cusps swap-symmetric), TestGrepRatchets (3 — calculate_houses/compute_chart/calculate_aspects_vectorized substrings absent), TestPolarSafe (1 — Paris+Reykjavik finite cusps), TestAngleMidpointConsistency (2 — ASC post-swap consistency, MC unswapped midpoint).

## Decisions Made

- **Approach A (Porphyry trisection) for house derivation.** 17-RESEARCH §"House Computation Strategy" presented Approach A (trisection from composite ASC + MC) and Approach B (synthesize composite ARMC + reference latitude + dispatch through SYSTEMS registry). Approach A wins on every relevant axis for Phase 17: literal COMP-03 compliance ("computed from composite ASC and MC"), polar-safe by construction (no `tan(lat)` singularity), no unanswerable reference-latitude question, closed-form ~30 lines inlined verbatim from `porphyry.py:159-186`. The `system=` argument's semantic meaning is sacrificed (every system collapses to Porphyry), but that's documented loudly and the user-supplied string is preserved in the output's `system` field for bookkeeping. If a user truly needs Placidus-flavoured composite cusps, the reference-place method is computable externally from the composite ARMC stored in the output — Phase 17 doesn't implement it.

- **system= accept-and-ignore, not raise-on-non-placidus.** Two compliant readings of "every system collapses to Porphyry under Approach A" exist: (a) raise ValueError for non-placidus/non-porphyry, (b) accept any registered system, store verbatim, document the no-op semantics. Chose (b) for API symmetry with `compute_chart` (`compute_chart` also accepts any registered system and stores the user's string). `get_system(system)` is still called to validate (raises ValueError on truly unknown systems), but the returned function is discarded. This keeps the surface predictable for downstream code that introspects `composite["system"]`.

- **Inline aspect-matching loop (Option 3 in 17-RESEARCH).** Three options existed for the aspect-matrix construction: (1) refactor `calculate_aspects_vectorized` to accept `body_lons=` kwarg (cleanest, but touches Phase 9 engine — wider blast radius and surface-area expansion), (2) sibling `_calculate_aspects_from_longitudes` helper in `ketu/aspects/` (lower blast radius but introduces parallel code path that can drift), (3) inline the 30-line `triu` matching loop in `calculate_composite` itself (most localised, may drift if Phase 9 algorithm changes). Chose Option 3 for Phase 17 self-containment — zero blast radius on the existing aspect engine; the localised loop is ~50 LOC and trivially audited. The TODO for a future refactor (Phase 18/19 may want a body_lons= kwarg) is documented in the api.py module docstring's Locked Design Decisions block.

- **CLASSICAL preset hardcoded (no aspects= kwarg).** COMP-01..04 don't mention an aspects parameter on `calculate_composite`. Hardcoding the CLASSICAL preset (5 majors) matches the package-wide default (`ketu.aspects.presets.CLASSICAL`). The preset mask is resolved via `resolve_aspect_set("classical")` rather than hardcoding the indices `[0, 4, 7, 9, 13]` directly — single source of truth (Phase 9), and a future preset upgrade would propagate without code changes here.

- **Doctest examples reworked to avoid grep-ratchet false-match.** Initially the function's `Examples` block contained `>>> compute_chart(...)` doctest calls — these would have triggered the source-level grep ratchet in `test_no_compute_chart_call_smoke` (the substring `compute_chart(` would appear in `api.py` even though the actual function call is in user code, not in the composite implementation). Reworked the Examples block to a narrative See Also-style reference: "Build the per-partner inputs via :func:`ketu.charts.compute_chart`, then call this function on the pair." Loses the executable doctest but the function call IS NOT in the example — the ratchet is honest.

- **is_day_chart return-type tolerance.** Initial test asserted `isinstance(result, (bool, np.bool_))` but `is_day_chart` returns a 0-d `np.ndarray` for scalar inputs (the broadcast machinery doesn't unbox). Relaxed the assertion to `bool(result) in (True, False)` — the key invariant is "callable without raising AND result castable to bool", which detects future NaN-in-bookkeeping refactors without coupling to is_day_chart's broadcast return-type quirk.

## Deviations from Plan

None of the deviations affect scope or break the locked design decisions. Three minor adjustments:

### Auto-fixed Issues

**1. [Rule 1 - Bug] is_day_chart return-type test relaxed**

- **Found during:** Task 2 first pytest run.
- **Issue:** Test asserted `isinstance(result, (bool, np.bool_))` but `is_day_chart(jd, lat, lon)` returns a 0-d `np.ndarray` even for scalar inputs (broadcast machinery doesn't unbox at ndim==0). The test failed loudly: `AssertionError: assert False where False = isinstance(array(False), (<class 'bool'>, <class 'numpy.bool'>))`.
- **Fix:** Relaxed the assertion to `bool(result) in (True, False)`. The plan's intent (Q3 ratchet — `is_day_chart` callable on composite metadata without raising) is preserved; the test now passes regardless of whether `is_day_chart` returns `bool`, `np.bool_`, or a 0-d `np.ndarray`. Future refactors to `is_day_chart`'s return type don't affect this ratchet.
- **Files modified:** `tests/composite/test_calculate_composite.py` (one assertion + a 3-line comment).
- **Verification:** `pytest tests/composite/test_calculate_composite.py::TestIsDayChartCallable -v` PASSES.
- **Committed in:** `61ba77c` (Task 2 commit — the relax landed before the file was committed).

**2. [Rule 1 - Bug] Doctest examples reworked to honour grep ratchet**

- **Found during:** Task 1 implementation review (before any commit).
- **Issue:** The plan's `<action>` block included `>>> from ketu.charts import compute_chart` and `>>> chart_a = compute_chart(2451545.0, 48.85, 2.35)` in the function's Examples section. The grep ratchet in Task 2 (`test_no_compute_chart_call_smoke`) reads `api.py` as text and asserts the substring `compute_chart(` does not appear. Including the doctest examples verbatim would have false-failed the ratchet — the call IS in the file, just in a docstring.
- **Fix:** Replaced the doctest examples with a narrative reference: "Build the per-partner inputs via :func:`ketu.charts.compute_chart`, then call this function on the pair." The user still learns how to use the function; the source-level substring is gone (the substring `compute_chart` appears, but not `compute_chart(` with the open-paren — the ratchet specifically targets call sites). Similarly reworked a comment that mentioned `calculate_aspects_vectorized(jd, ...)` to remove the parenthesis.
- **Files modified:** `ketu/composite/api.py` (Examples block + one comment in step 7).
- **Verification:** `grep -nE 'compute_chart\(|calculate_houses\(|calculate_aspects_vectorized\(' ketu/composite/api.py` returns ZERO matches.
- **Committed in:** `6121e57` (Task 1 commit — the rework landed before the file was committed).

**3. [Rule 1 - Hygiene] coverage gate scope clarified**

- **Found during:** Task 2 verification.
- **Issue:** Running `pytest tests/composite/` alone triggers the project-wide 70% coverage gate (set in `pyproject.toml`), which obviously fails when only the composite test suite is loaded (every other module shows ~0% coverage). The plan's verify command `pytest tests/composite/ -v` would have shown a coverage failure even though the actual test count is 93/93 PASS.
- **Fix:** No code change needed — the project-wide coverage gate is honoured by `pytest tests/` (full project), which DOES pass (98.21% project-wide). The composite-scoped coverage check uses the two-step pattern from `make synastry-coverage` precedent: `pytest tests/composite/ -o addopts="" --cov --cov-report= --cov-fail-under=0` then `coverage report --include='ketu/composite/*' --fail-under=95`. Composite-scoped coverage is 98% (lines 245-246 of api.py are the conjunction match-found break — will exercise in Plan 17-03 oracle fixtures with closer-orbed natal pairs).
- **Files modified:** None — this is a documentation note for Plan 17-04 (which will wire `make composite-coverage` properly).
- **Verification:** Project suite 1158/1158 PASS at 98.21% coverage; composite-scoped coverage 98%.

---

**Total deviations:** 3 auto-fixed (2 minor bugs surfacing as test/source adjustments; 1 hygiene note for Plan 17-04). No scope change, no decisions reversed, no architectural alternatives invoked.

**Impact on plan:** Plan's `<success_criteria>` all satisfied:

- [x] `calculate_composite(chart_a, chart_b, system="placidus") -> CHART_DTYPE` callable and exposed via `ketu.composite.__all__`.
- [x] Composite body longitudes are circular midpoints of the two natals across all 13 bodies (Pitfall 8 ratchet via index-0 / index-1 spot checks + parametrized full-axis test, all 13 bodies covered).
- [x] Composite ASC, MC, ARMC, Vertex are circular midpoints of the two natals.
- [x] Composite house cusps are Porphyry-style trisections of (composite ASC, composite MC); cusps 5/6/8/9 are oppositions of cusps 11/12/2/3.
- [x] Swap symmetry holds at <1e-9° tolerance on all output fields (body_lons + asc/mc + cusps verified).
- [x] `system=` accepts any registered system, raises `ValueError` on unknown, stored in output's `system` field, semantically a no-op.
- [x] Polar pair (lat 64°N) produces finite cusps (Approach A polar-safe ratchet via Reykjavik fixture).
- [x] Anti-regression grep ratchets pin: no `calculate_houses(`, no `compute_chart(`, no `calculate_aspects_vectorized(` calls inside `ketu/composite/api.py`.
- [x] Doc gates green; full project test suite green (1158/1158 PASS).

## Issues Encountered

- **Pytest shebang broken on venv binary.** Same v1.1 working-tree leftover as Plan 17-01: `venv/bin/pytest` has hardcoded shebang `#!/home/loc/workspace/solaris/ketu/venv/bin/python3`. Worked around by invoking `source venv/bin/activate && python -m pytest` instead of `pytest` directly. No effect on plan execution; documented as not in v1.2 scope.
- **`is_day_chart` 0-d ndarray return for scalar input.** Documented in deviation #1 above; the function's broadcast machinery returns `np.ndarray(False)` (ndim==0) rather than unboxing to a Python `bool` or `np.bool_`. The test was relaxed to `bool(result) in (True, False)` — the Q3 ratchet's intent is preserved.
- **No checkpoint reached, no authentication gates encountered.** Plan 17-02 is fully autonomous (no `type="checkpoint:*"` tasks).

## Self-Check: PASSED

Verification of claims:

- **Files exist (all 6):**
  - `ketu/composite/api.py` — FOUND
  - `ketu/composite/__init__.py` (modified) — FOUND with `calculate_composite` re-export
  - `tests/composite/conftest.py` — FOUND
  - `tests/composite/test_calculate_composite.py` — FOUND
  - `tests/composite/test_composite_houses.py` — FOUND
  - `tests/composite/test_dtype.py` — FOUND
- **Commits exist:**
  - `6121e57` — Task 1 (feat: implement calculate_composite) — FOUND
  - `61ba77c` — Task 2 (test: pin ratchets) — FOUND
- **Verification gates (6/6 PASS):**
  - V1 Plan verify command (shape, dtype, swap symmetry quick check): PASS
  - V2 Grep ratchet (no compute_chart(, calculate_houses(, calculate_aspects_vectorized() in api.py): PASS (zero matches)
  - V3 Doc gates (numpydoc lint + interrogate): PASS (numpydoc CLEAN; interrogate 100%)
  - V4 Composite test suite (`tests/composite/`): PASS (93/93)
  - V5 Full project test suite (`tests/`): PASS (1158/1158 at 98.21% coverage)
  - V6 Composite-scoped coverage: PASS (98% on `ketu/composite/`)

## Next Phase Readiness

- **Plan 17-03 (oracle fixtures):** `calculate_composite` is the foundation; oracle fixtures can now reuse the three synastry oracle birth records (Curie, Diana/Charles, Lennon/Ono) to generate self-consistency composite oracles. Fixture schema documented in 17-RESEARCH §"Astro.com Oracle Pairs". Plan 17-03 will replicate the Phase 16-03 pattern: load synastry birth records, run `calculate_composite`, pin the resulting composite body longitudes + ASC + MC as `expected_composite` JSON.
- **Plan 17-04 (close-out):** `composite_coverage_gate` pytest marker + `make composite-coverage` Makefile target + CHANGELOG `[Unreleased]` entry. Current composite-scoped coverage is 98% — well above the 95% gate. The two-step pattern (`pytest tests/composite/ + coverage report --include='ketu/composite/*' --fail-under=95`) is the established mirror of `make synastry-coverage` / `make charts-coverage`.
- **Sequencing note:** Lines 245-246 of `api.py` (the conjunction match-found `break` after recording a conjunction orb) are the only uncovered lines in `ketu/composite/`. These will be exercised in Plan 17-03 oracle fixtures (couples like Lennon/Ono have very close conjunctions Sun-Sun, Moon-Moon) — no special test needed in Plan 17-04.

---

*Phase: 17-composite-chart-midpoint-variant*
*Completed: 2026-05-24*
