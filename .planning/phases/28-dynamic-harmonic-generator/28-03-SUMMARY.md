---
phase: 28-dynamic-harmonic-generator
plan: "03"
subsystem: aspects
tags: [numpy, structured-arrays, synastry, cycles, harmonics, dynamic-aspects]

# Dependency graph
requires:
  - phase: 28-01
    provides: generate_harmonic_aspects, DynamicAspectSpec, HARMONIC_DTYPE

provides:
  - "calculate_synastry accepts dynamic_specs=, emits aspect_type=-2 dynamic rows"
  - "generate_cycle_series accepts dynamic_specs=, extends nearest-aspect candidate set"
  - "generate_multi_cycle_series forwards dynamic_specs to all pairs"
  - "tests/test_dynamic_synastry_cycles.py — 14 tests covering all new branches"

affects:
  - 28-02  # shares DynamicAspectSpec type alias
  - 31-documentation  # generate_harmonic_aspects, calculate_synastry, generate_cycle_series all need doc update
  - 32-release  # ASP-07 satisfied, part of Phase 28 delivery

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "static-first / dynamic-second detection via shared matched mask (synastry)"
    - "full-circle expansion of folded [0,180] angles for cycles detection (+ 360-theta mirror)"
    - "effective_aspects/effective_coeffs/effective_aspects_z built at call time, None path byte-identical"
    - "aspect_type=-2 sentinel for dynamic synastry rows (distinct from -1 = no-aspect)"
    - "filtered-mode predicate: aspect_type != -1 (keeps -2, drops -1)"

key-files:
  created:
    - "tests/test_dynamic_synastry_cycles.py — 14 tests: 6 synastry + 8 cycles"
  modified:
    - "ketu/synastry/api.py — dynamic_specs param + dynamic loop + filtered predicate fix"
    - "ketu/cycles/calculator.py — dynamic_specs param on generate_cycle_series + generate_multi_cycle_series"

key-decisions:
  - "aspect_type=-2 sentinel for dynamic synastry rows; fits int8 range [-128,127]; filtered predicate changed to != -1"
  - "Cycles full-circle expansion: generator emits folded [0,180]; mirror 360-theta added for waning detection (not 0/180 poles)"
  - "None path is byte-identical: effective_* variables take MAJOR_ASPECTS/COEFFS/MAJOR_ASPECTS_Z unchanged when dynamic_specs=None"
  - "Empty list [] falls back to static candidate set (no crash, no extension)"
  - "Neither consumer looks up core.aspects for dynamic angle/coef: both use dyn_row fields directly from spec"

patterns-established:
  - "DynamicAspectSpec normalisation at entry: list -> np.concatenate, None stays None"

# Metrics
duration: 11min
completed: "2026-06-03"
---

# Phase 28 Plan 03: Dynamic Synastry + Cycles Integration Summary

**`dynamic_specs` wired into `calculate_synastry` (aspect_type=-2 rows with `_BODY_ORBS_16 x dyn_coef x factor` orbs) and `generate_cycle_series` (nearest-aspect candidate set extended with full-circle H7/Hn angles), satisfying ASP-07**

## Performance

- **Duration:** ~11 min
- **Started:** 2026-06-03T10:29:41Z
- **Completed:** 2026-06-03T10:40:33Z
- **Tasks:** 2
- **Files modified:** 3 (2 sources + 1 new test file)

## Accomplishments

- `calculate_synastry` now accepts `dynamic_specs=None` as last parameter; when provided, a second detection loop runs after the static loop (static-first/dynamic-second, first-aspect-wins via shared `matched` mask); dynamic rows carry `aspect_type=-2`; filtered-mode predicate updated to `aspect_type != -1`
- `generate_cycle_series` and `generate_multi_cycle_series` accept `dynamic_specs=None`; when provided, the nearest-aspect candidate set is extended with dynamic angles (full-circle expansion: folded angle + waning mirror 360-theta); `None` path is byte-identical to the no-arg call
- 14 tests covering all new branches (6 synastry + 8 cycles), all passing; `ketu/synastry/api.py` and `ketu/cycles/calculator.py` both at 100% coverage in full suite

## Task Commits

1. **Task 1: dynamic_specs in calculate_synastry** - `c20958e` (feat)
2. **Task 2: dynamic_specs in generate_cycle_series/generate_multi_cycle_series** - `05991e4` (feat)

## Files Created/Modified

- `ketu/synastry/api.py` — `DynamicAspectSpec` import; `dynamic_specs=None` last param; normalise list; second dynamic loop after static loop; `aspect_type=-2` sentinel; filtered predicate `!= -1`; numpydoc updated
- `ketu/cycles/calculator.py` — `DynamicAspectSpec` import; `dynamic_specs=None` on `generate_cycle_series` + `generate_multi_cycle_series`; `effective_*` variables built at call time; full-circle expansion; numpydoc updated on both functions
- `tests/test_dynamic_synastry_cycles.py` — NEW: 14 tests (structural, existence, dtype, invariance, list-normalisation, empty-list fallback)

## Decisions Made

- **filtered-mode predicate `!= -1`**: the original predicate `>= 0` would have silently dropped all dynamic rows (`-2 < 0`). Changed to `!= -1` — keeps both static (`>= 0`) and dynamic (`== -2`), only drops non-aspected (`== -1`). Documented in numpydoc Notes.
- **Full-circle expansion in cycles**: the generator emits folded angles in `[0, 180]`; cycles already lists waning mirrors in `MAJOR_ASPECTS` (240/270/300). To keep the same semantics, each dynamic angle `theta` is expanded with `360 - theta` (unless `theta in {0, 180}`) so a separation on either side of the cycle is detectable.
- **Empty list fallback**: `dynamic_specs=[]` falls back silently to static (no error, no extension). Covered by test `test_cycles_empty_list_falls_back_to_static`.

## Deviations from Plan

None — plan executed exactly as written. The filtered-mode predicate change (`>= 0` → `!= -1`) was specified in the plan; it is not a deviation.

## Issues Encountered

None.

## Next Phase Readiness

- ASP-07 (dynamic aspects flow through cycles and synastry) is satisfied.
- Phase 28 Wave 2 is complete on this plan's side (28-02 runs in parallel on `ketu/aspects/calculator.py`).
- Phase 31 documentation should document: `calculate_synastry(dynamic_specs=)`, `generate_cycle_series(dynamic_specs=)`, `generate_multi_cycle_series(dynamic_specs=)`, and the `aspect_type=-2` / filtered-predicate semantics.

---
*Phase: 28-dynamic-harmonic-generator*
*Completed: 2026-06-03*
