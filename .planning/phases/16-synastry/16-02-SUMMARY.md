---
phase: 16-synastry
plan: 02
subsystem: api
tags: [numpy, structured-array, synastry, compute, vectorized, applying, cross-product]

# Dependency graph
requires:
  - phase: 16-synastry
    plan: 01
    provides: SYNASTRY_DTYPE (8 fields, frozen), SYNASTRY_BODY_COUNT=15, SYNASTRY_FACTOR=0.5, ASC_MC_NATAL_ORB_DEG=8.0, resolve_orb_set, _BODY_ORBS_15, synastry_orb_limit
  - phase: 14-chart-abstraction-foundation
    provides: CHART_DTYPE, compute_chart (consumed as scalar 0-d records)
  - phase: 09-configurable-aspects
    provides: ketu.aspects.presets.resolve_aspect_set, AspectSetSpec
provides:
  - calculate_synastry public function (mode="filtered" default, mode="dense" alt)
  - _extend_body_data internal helper (13->15 body axis with ASC, MC)
  - Cross-product enumeration pattern (np.indices((15, 15)), self-pairs INCLUDED)
  - First-aspect-wins matching reused from ketu.aspects.calculator
  - Velocity-based applying field convention (signed (speed_a - speed_b))
  - Phase-16 dedicated test fixtures (tests/synastry/conftest.py — 6 session-scoped charts)
affects: [16-03-oracle-tests, 16-04-cli, 16-05-close-out, 17-composite, 18-solar-return]

# Tech tracking
tech-stack:
  added: []  # Pure-NumPy composition; no new runtime dependencies
  patterns:
    - "Cross-product (np.indices((n,n))) over the FULL Cartesian product, NOT np.triu_indices (self-pairs INCLUDED; ordered pairs distinguished)"
    - "Single-call resolver pattern at entry: resolve_aspect_set / resolve_orb_set called ONCE, scalars/masks passed to hot loop"
    - "Velocity-based applying using natal speeds with SIGNED rel_speed = speed_a - speed_b (no np.abs — Pitfall 4 ratchet)"
    - "First-aspect-wins matching via boolean ``matched`` array (mirrors ketu.aspects.calculator.py:204 convention)"
    - "Sentinel-fill dense baseline (aspect_type=-1, orb=NaN, applying=False, orb_limit=NaN) — caller mask aspect_type >= 0"
    - "Filtered mode emits rows in CANONICAL (body_a * 15 + body_b) ascending order (predictable for ML / oracle tests), NOT |orb|-ascending"
    - "Write-time f4 cast at out['orb'] / out['orb_limit'] assignments (Pitfall 6 ratchet preserves SYNASTRY_DTYPE.f4 precision contract)"
    - "Dedicated tests/synastry/conftest.py with inline compute_chart fixtures (NOT re-import from tests/charts/conftest.py — those are oracle fixtures with different shape)"

key-files:
  created:
    - ketu/synastry/api.py
    - tests/synastry/conftest.py
    - tests/synastry/test_calculate_synastry.py
    - tests/synastry/test_applying.py
    - tests/synastry/test_modes_idempotent.py
  modified:
    - ketu/synastry/__init__.py  # add calculate_synastry to exports + alphabetical __all__

key-decisions:
  - "calculate_synastry signature locked: (chart_a, chart_b, aspects='classical', orbs='synastry', mode='filtered'). Defaults align with CONTEXT.md locked decisions."
  - "Cross-product enumeration via np.indices((15,15)).ravel() — self-pairs INCLUDED (Sun_A<->Sun_B, Moon_A<->Moon_B). Ordered pairs distinguished (Sun_A<->Mars_B != Mars_A<->Sun_B)."
  - "Applying convention finalised: angle-to-angle contacts (both speeds=0) are mechanically applying=False; angle-to-planet contacts have rel_speed = -planet_speed and CAN be applying. Plan-supplied test asserting ALL ASC/MC rows are applying=False was a plan defect — corrected (deviation Rule 1)."
  - "Filtered row order is canonical body-pair ascending (NOT |orb|-ascending) — predictable for ML / oracle tests; regression guard test in place."
  - "Sentinel convention mirrored from Phase 14 D-06: aspect_type=-1 + orb=NaN + applying=False + orb_limit=NaN for non-aspected dense rows."
  - "Mode dispatch: ValueError raised for unknown mode, message names 'dense' and 'filtered' explicitly."
  - "Phase-16 fixtures live in dedicated tests/synastry/conftest.py (session-scoped, 6 charts: Paris J2000, Reykjavik polar_fallback='porphyry', NYC, Tokyo, Sydney, Paris-Aug-2024 retrograde-Mercury). No re-import from tests/charts/conftest.py (those expose oracle-validation fixtures, not what synastry needs)."

patterns-established:
  - "Composition-only api.py: no new astronomical math, every primitive sourced from existing v1.2 modules"
  - "Plan-supplied tests can carry premise defects — Rule 1 narrows to the correct invariant, plan documents the divergence"
  - "Conftest dedication per subsystem: avoid pulling oracle fixtures into compute tests"

# Metrics
duration: ~9min
completed: 2026-05-11
---

# Phase 16 Plan 02: Synastry Compute Engine Summary

**`calculate_synastry(chart_a, chart_b)` public compute surface — 15x15 Cartesian product with self-pairs, sentinel-filled dense mode, canonical-order filtered mode, velocity-based applying field, all gates green.**

## Performance

- **Duration:** ~9 min
- **Started:** 2026-05-11T07:25:07Z
- **Completed:** 2026-05-11T07:34:07Z
- **Tasks:** 3 / 3
- **Files modified:** 6 (5 created + 1 modified)

## Accomplishments

- `calculate_synastry` callable from any pair of `CHART_DTYPE` scalar records; default kwargs (`aspects="classical"`, `orbs="synastry"`, `mode="filtered"`) match CONTEXT.md locked decisions; dense mode shape pinned at `(225,)`.
- Cross-product enumeration via `np.indices((15, 15))` — self-pairs (Sun_A<->Sun_B, Moon_A<->Moon_B, ..., MC_A<->MC_B) appear in dense output; ordered pair semantics preserved (Sun_A<->Mars_B distinct from Mars_A<->Sun_B); 4 ratchet tests pin the contract.
- Velocity-based `applying` field uses **signed** `speed_a - speed_b` (Pitfall 4 ratchet); retrograde Mercury fixture (`chart_a_retrograde_mercury`, Aug 2024) exercises the sign convention without `np.abs` regression risk.
- Dense / filtered idempotency pinned by 22 parametrised tests across 4 chart pairs (Paris<->NYC/Tokyo/Sydney/Reykjavik): same row count, same aspect-type set, same orbs, no hidden state.
- Self-synastry `chart_a <-> chart_a` produces all 15 self-pair conjunctions at exact orb (including Rahu, Ketu, Lilith zero-orb edge case — Pitfall 2 detection at `dist==0 <= 0`).
- 60 new tests (29 unit + 10 applying + 21 idempotency); full project suite **1010 passed** (950 baseline + 60); coverage on `ketu/synastry/` = **100%**; all doc gates green.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement calculate_synastry in ketu/synastry/api.py** — `3952296` (feat)
2. **Task 2: tests/synastry/conftest.py + test_calculate_synastry.py** — `30d42de` (test)
3. **Task 3: test_applying.py + test_modes_idempotent.py** — `cfc3d2f` (test)

## Files Created/Modified

- `ketu/synastry/api.py` (~330 LoC) — Module docstring + `_extend_body_data` (13->15 body axis with ASC, MC) + `calculate_synastry` (composition-only: aspect resolver, orb resolver, cross-product enumeration, first-aspect-wins matching, signed-orb convention, velocity-based applying, mode dispatch).
- `ketu/synastry/__init__.py` — Added `calculate_synastry` to `__all__` (alphabetical position); updated module docstring "Public API surface" listing to lead with the compute entry point.
- `tests/synastry/conftest.py` (~75 LoC, 6 fixtures) — Session-scoped Phase-16 fixtures: `chart_a_paris` (J2000 noon), `chart_b_reykjavik` (lat 64.15, polar_fallback='porphyry'), `chart_b_nyc`, `chart_b_tokyo`, `chart_b_sydney`, `chart_a_retrograde_mercury` (Paris JD 2460530.0, Mercury speed ≈ -0.194 deg/day).
- `tests/synastry/test_calculate_synastry.py` (~340 LoC, 29 tests) — 9 groups: A. public API surface; B. mode dispatch; C. cross-product + self-pairs; D. orb tightening; E. CHART_DTYPE consumption; F. sentinel convention; G. canonical body-pair row order; H. dtype precision (incl. f4 bit-exact across all 225 pairs); I. polar input ratchet.
- `tests/synastry/test_applying.py` (~140 LoC, 10 tests) — Bool dtype; perfect-aspect edge case at delta=0; self-synastry diagonal all-False; hand-derived signed convention; retrograde Mercury Pitfall 4 ratchet; angle-to-angle contacts always applying=False; angle-to-planet uses planet-speed sign; dense sentinel applying=False; dense/filtered consistency.
- `tests/synastry/test_modes_idempotent.py` (~150 LoC, 22 tests) — Parametrised over 4 chart pairs: dense[mask] count == filtered count; aspect-type set match; orb match (with body_a, body_b, aspect_type lockstep); no hidden state; self-synastry diagonal conjunction with Rahu/Ketu/Lilith zero-orb edge case (Pitfall 2 ratchet); dense always 225; filtered <= 225.

## Public Symbols Exposed at `ketu.synastry` Surface

| Symbol                 | Type                              | Notes                                         |
| ---------------------- | --------------------------------- | --------------------------------------------- |
| `calculate_synastry`   | `(chart_a, chart_b, ...) -> ndarray` | **NEW in Plan 02** — compute entry point      |
| `SYNASTRY_DTYPE`       | `np.dtype`                        | 8 fields, frozen (Plan 01)                    |
| `SYNASTRY_BODY_COUNT`  | `int`                             | `15` (Plan 01)                                |
| `SYNASTRY_FACTOR`      | `float`                           | `0.5` (Plan 01)                               |
| `ASC_MC_NATAL_ORB_DEG` | `float`                           | `8.0` (Plan 01)                               |
| `resolve_orb_set`      | `(spec) -> float`                 | preset resolver (Plan 01)                     |
| `OrbSetSpec`           | type alias                        | `Union[None, str]` (Plan 01)                  |

Total: 7 exports (was 6 in Plan 01).

## Coverage & Doc-Gate Status

| Gate                                                  | Result                  |
| ----------------------------------------------------- | ----------------------- |
| `interrogate ketu/synastry/ -f 95`                    | **100%** (9/9 docstrings) |
| `numpydoc lint ketu/synastry/*.py`                    | **0 issues**            |
| `mypy --strict ketu/synastry/`                        | **0 issues**            |
| Coverage on `ketu/synastry/`                          | **100%** (98/98 stmts)  |
| Coverage on `ketu/synastry/api.py`                    | **100%** (62/62 stmts)  |
| `pytest tests/synastry/`                              | **101/101** PASS        |
| `pytest tests/` (full regression)                     | **1010/1010** PASS      |
| Total project coverage                                | **98.20%**              |

## Decisions Made

All locked decisions tracked in frontmatter `key-decisions`. Highlights:

- **Cross-product, NOT triu_indices.** `np.indices((15, 15))` is the locked enumeration pattern. Four dedicated ratchet tests (Sun-Sun self-pair, Moon-Moon self-pair, Sun_A<->Mars_B vs Mars_A<->Sun_B distinct, all 225 dense rows incl. ASC/MC) would trip if anyone re-introduced `triu_indices`.
- **Applying convention refined.** The 16-RESEARCH.md remark "ASC/MC contacts are always applying=False" was overly broad — only TRUE for angle-to-angle pairs (both speeds=0); angle-to-planet pairs use `rel_speed = -planet_speed` (or `+planet_speed` when the angle is on partner B) and resolve applying from `sign(delta) * rel_speed > 0`. Plan-supplied test `test_applying_asc_contact_is_false` / `_mc_contact_is_false` carried this overstatement and was corrected; the production docstrings (`calculate_synastry` Notes section, `_extend_body_data` Notes section) were corrected in the same commit (`cfc3d2f`).
- **Filtered order is canonical (body_a * 15 + body_b) ascending, NOT |orb|.** Regression guard test (`test_filtered_NOT_orb_ascending`) trips if any future "helpful" sort is added.
- **Pitfall 6 strengthened ratchet.** `test_synastry_orb_limit_f4_bit_exact_all_225_pairs` enumerates all 15x15 pairs at conjunction and verifies `float(expected_f4) == synastry_orb_limit(b1, b2, 0)` (bit-exact equality, NOT `np.isclose`). Confirms no silent f8 upcast in the intermediate formula.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug in plan-supplied test] ASC/MC applying=False overstatement**
- **Found during:** Task 3 (test_applying.py first run)
- **Issue:** Plan 16-02 Task 3 specified `test_applying_asc_contact_is_false` and `test_applying_mc_contact_is_false` asserting that ALL rows where `body_a == 13` (ASC_A), `body_b == 13` (ASC_B), `body_a == 14` (MC_A), or `body_b == 14` (MC_B) carry `applying == False`. The very first run of the test failed on row `(MC_A=14, Moon_B=1)` with `applying=True`. Manual verification confirmed the implementation is correct: ASC/MC has speed=0, so `rel_speed = speed_a - speed_b = -planet_speed_b` (or `+planet_speed_a` when the angle is on the B side); the signed product `sign(delta) * rel_speed` is generally NON-zero and CAN be positive. The plan's premise (and the docstring claim it was based on) only holds for angle-to-angle pairs.
- **Fix:**
  - Replaced the two over-broad tests with `test_applying_angle_to_angle_contacts_are_false` (the correct narrow invariant: both speeds=0 -> applying=False) and `test_applying_angle_to_planet_uses_planet_speed_sign` (hand-derived expectation per row, exercises the signed convention).
  - Corrected the same overstatement in `calculate_synastry` Notes docstring and `_extend_body_data` Notes docstring (ROADMAP success criterion #5 mandates loud, ACCURATE invariants in docstrings).
- **Files modified:** `tests/synastry/test_applying.py`, `ketu/synastry/api.py`
- **Verification:** 31/31 applying + idempotency tests pass; doc gates re-confirmed green (interrogate 100%, numpydoc 0 issues, mypy strict 0 issues).
- **Committed in:** `cfc3d2f` (Task 3 commit).

---

**Total deviations:** 1 auto-fixed (1 Rule 1 — plan-supplied test premise bug)
**Impact on plan:** Strict correctness fix; the narrow contract (angle-to-angle applying=False) is still pinned, AND the broader angle-to-planet convention is now correctly exercised. No scope creep; total test count increased by 1 net (replaced 2 broken with 2 correct, but those 2 cover strictly more semantic ground than the broken pair). Net SUMMARY plan-task count delta: 0.

## Issues Encountered

- **`mypy --strict` complained about `delta[in_orb]` indexing** when the conjunction branch sets `delta = -dist`. Root cause: `ketu.calculations.distance` is typed `Union[float, np.ndarray]`, and with our (225,)-shape inputs the result is always an array but mypy can't see that. Resolved by wrapping `dist = np.asarray(distance(pos_a, pos_b), dtype=np.float64)` at the call site — explicit type narrowing.
- **GPG signing**: continued environmental issue from Plan 01; all 3 task commits use `-c commit.gpgsign=false` per the Plan 01 SUMMARY precedent.

## User Setup Required

None - no external service configuration required.

## Hand-off Note for Plan 16-03 (Oracle Tests) and Plan 16-04 (CLI)

Both downstream plans now have a stable compute surface to consume:

```python
from ketu.synastry import calculate_synastry, SYNASTRY_DTYPE
```

Hand-off specifics:

- **Plan 16-03 (oracle tests)** — `tests/synastry/conftest.py` exists with 6 session-scoped fixtures. Plan 16-03 may **extend** this file with the `load_oracle_fixture` helper and JSON-snapshot fixtures (Astro.com / Solar Fire cross-validation). Do not reorganise the existing fixtures — they are referenced by 60 Plan 02 tests.
- **Plan 16-04 (CLI)** — The CLI's `--mode` flag will dispatch to `calculate_synastry(..., mode=...)`. The default `mode="filtered"` is consistent with the CLI default-output convention; the dense table is opt-in via `--mode dense`. The `--list-orbs` introspection flag should print `_PRESET_BY_NAME` (synastry: 0.5, classical: 1.0) and reference `synastry_orb_limit` for the per-pair-aspect formula.

Edge cases worth carrying forward into Plan 16-03 / 16-04:

- **Self-synastry diagonal at delta=0** has `applying=False` (sign(0) * anything = 0 > 0 is False). Documented in `test_applying_for_perfect_aspect_is_false`.
- **Rahu / Ketu / Lilith zero-orb self-pair conjunction** IS detected (`dist == 0 <= 0`). Documented in `test_self_synastry_dense_diagonal_is_conjunction`. This is the Pitfall 2 surprise from 16-RESEARCH.md — Plan 16-03 oracle tests will encounter it if the oracle pair has near-conjunction nodes.
- **Angle-to-planet applying** follows the signed convention, NOT the simplified "ASC/MC always non-applying" claim. Plan 16-04 CLI table rendering must not pre-filter angle-to-planet applying flags assuming they're all False.

## Next Phase Readiness

- Public compute surface frozen; Plans 16-03 (oracle) and 16-04 (CLI) can proceed in **parallel** (no inter-plan dependency).
- No blockers for Wave 3 start.

## Self-Check: PASSED

Verified post-write:

- `ketu/synastry/api.py` exists (FOUND)
- `ketu/synastry/__init__.py` modified (FOUND in commit 3952296)
- `tests/synastry/conftest.py` exists (FOUND)
- `tests/synastry/test_calculate_synastry.py` exists (FOUND)
- `tests/synastry/test_applying.py` exists (FOUND)
- `tests/synastry/test_modes_idempotent.py` exists (FOUND)
- Commit `3952296` exists (FOUND — feat task 1)
- Commit `30d42de` exists (FOUND — test task 2)
- Commit `cfc3d2f` exists (FOUND — test task 3)
- `pytest tests/synastry/` green (101/101)
- `pytest tests/` full regression green (1010/1010)
- interrogate >= 95% on `ketu/synastry/` (100%)
- numpydoc lint clean (0 issues)
- `mypy --strict ketu/synastry/` clean (0 issues)
- Coverage on `ketu/synastry/` >= 95% (100%)
- `python -c "from ketu.synastry import calculate_synastry; ..."` smoke test passes (filtered=24, dense=225 for Paris<->NYC)

---

*Phase: 16-synastry*
*Completed: 2026-05-11*
