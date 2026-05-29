---
phase: 21-quality
plan: "01"
subsystem: testing
tags: [coverage, pytest, numpy, house-systems, aspects, cycles, ephemeris, cli]

requires:
  - phase: 21-quality-research
    provides: "Gap inventory: 66 missed lines across 20 files at 97.90% baseline"

provides:
  - "62 new targeted tests in tests/test_coverage_improvements.py covering all documented non-orbital-guard gaps"
  - "ketu/houses/_ecliptic.py at 100% via known-value + round-trip tests"
  - "ketu/houses/api.py at 100% (polar_fallback ValueError + house_of direct coverage)"
  - "ketu/aspects/core.py, timelines.py, windows.py all at 100%"
  - "ketu/cache/ephemeris_cache.py at 100%"
  - "ketu/cli/ all modules at 100% (harmonics_spec, aspects_cmd, houses_cmd, synastry_cmd)"
  - "ketu/complex.py at 100%"
  - "ketu/cycles/calculator.py at 100% including CACHE_AVAILABLE=False branch"
  - "Overall coverage lifted from 97.90% to 99% (66 → 44 missed lines)"
  - "Rule 1 fix: test_composite_houses.py ratchet updated to exclude doctest lines"

affects: [21-02, 21-03, 21-04]

tech-stack:
  added: []
  patterns:
    - "Defensive-branch coverage via unittest.mock.patch.object to inject fault conditions"
    - "Round-trip identity tests for RA<->lambda converters (ra_to_lambda(lambda_to_ra(x)) == x)"
    - "importlib.reload under sys.modules=None to cover ImportError fallback branches"
    - "Bisection exhaustion via alternating-sign mock to cover the after-loop return"
    - "builtins.set patching to inject phantom entries into vectorized loop unique_months"

key-files:
  created:
    - "tests/test_coverage_improvements.py (rewritten — 62 tests, 19 test classes)"
  modified:
    - "tests/composite/test_composite_houses.py (Rule 1: ratchet grep excludes doctest lines)"

key-decisions:
  - "Branches inaccessibles documentées sans pragma: orbital.py:227, time.py:369, planets.py:362+448 sont des gardes défensives après modulo/dict — jamais atteignables à l'exécution Python normale; traitement déféré à 21-04 exclude_lines"
  - "body_name aliases (true Node / mean Apogee) couverts via patch.object car get_planet_name ne retourne plus ces valeurs (noms internes renommés en Ketu/Lilith)"
  - "CACHE_AVAILABLE=False via importlib.reload avec sys.modules[ketu.cache]=None; always-restore via finally block pour isolation des tests"
  - "Test ratchet test_no_compute_chart_call_smoke corrigé: filtrer les lignes doctest (>>>) pour permettre les exemples dans docstrings sans déclencher la garde anti-Davison"

patterns-established:
  - "Patch pattern pour branches défensives inaccessibles: utiliser unittest.mock.patch.object ou patch(builtins.set) pour injecter des états impossibles"
  - "Bisection test pattern: mock calc_planet_position avec alternance de signe pour exhaustion des itérations"
  - "Cache test pattern: tempfile.TemporaryDirectory() pour isolation complète du cache"

duration: 24min
completed: "2026-05-29"
---

# Phase 21 Plan 01: Coverage Gaps Quality Summary

**62 targeted tests closing all non-orbital-guard coverage gaps; _ecliptic.py and houses/api.py reach 100%; overall coverage from 97.90% to 99% with 4 unreachable defensive branches documented for 21-04 exclude_lines.**

## Performance

- **Duration:** 24 min
- **Started:** 2026-05-29T01:34:21Z
- **Completed:** 2026-05-29T01:58:00Z
- **Tasks:** 3 (committed together as one atomic commit)
- **Files modified:** 2

## Accomplishments

- _ecliptic.py (was 64%) now at 100%: known-value asserts at equinoxes (0°/180°), non-trivial angles (30°/45°), and full ra_to_lambda(lambda_to_ra(x)) == x round-trip over 12 lambdas
- houses/api.py (was 84%) now at 100%: polar_fallback ValueError + house_of() direct coverage with 1..12 range assertion
- All aspects, CLI, cache, complex, and cycles modules reach 100%
- CACHE_AVAILABLE=False branch covered via importlib.reload under sys.modules injection
- Pre-existing regression fixed: test ratchet now correctly excludes docstring `>>>` lines

## Task Commits

1. **Tasks 1+2+3: All coverage gaps** - `94bc3d9` (test)
   *Note: All three tasks are in one file (tests/test_coverage_improvements.py); committed atomically.*

## Files Created/Modified

- `tests/test_coverage_improvements.py` — Rewritten with 62 tests across 19 test classes targeting all documented gaps
- `tests/composite/test_composite_houses.py` — Rule 1 fix: grep ratchet filters doctest lines

## Decisions Made

- **Defensive branches inaccessibles**: `orbital.py:227` (`angle += 360.0` after `% 360.0`), `time.py:369` (`gst += 360.0` after `% 360.0`), `planets.py:362` (after 50 bisection iterations) and `planets.py:448` (`avg_speed == 0` impossible via dict) are all proven dead code paths in Python. These 4 lines are not in the original RESEARCH gap list and will be handled by 21-04's `exclude_lines` additions alongside `display.py:28`.
- **body_name aliases**: The aliases "true Node" / "mean Apogee" in `calculations.py:170-174` are only reachable if `get_planet_name` returns those values — but the current implementation maps indices 11/12 to "Ketu"/"Lilith". Covered via `patch.object(calc_mod, "get_planet_name")`.
- **test ratchet fix**: The grep ratchet in `test_composite_houses.py` was checking `"compute_chart(" not in source` but 21-03 added docstring Examples with `>>> compute_chart(2451545.0, ...)`. Fix: filter lines starting with `>>>` before the grep.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] test_no_compute_chart_call_smoke regression from plan 21-03**
- **Found during:** Task 2 (full test suite verification)
- **Issue:** The plan 21-03 docstring work added `>>> compute_chart(...)` in the Examples section of `ketu/composite/api.py`. This caused the pre-existing grep ratchet test to fail because `"compute_chart(" in source` matches doctest lines.
- **Fix:** Updated the ratchet to filter lines starting with `>>>` before checking for `compute_chart(`. The anti-Davison guard still catches any genuine runtime call.
- **Files modified:** `tests/composite/test_composite_houses.py`
- **Verification:** All 3 ratchet tests pass; runtime call detection still works
- **Committed in:** `94bc3d9`

---

**Total deviations:** 1 auto-fixed (Rule 1 — bug)
**Impact on plan:** Minimal; kept test suite green without touching source files.

## Issues Encountered

- `ra_to_lambda(90°)` returns exactly 90° (not a solstice "shift") because `atan2(sin(90°), cos(90°)·cos(eps)) = atan2(1, 0) = 90°`. Tests updated to use 30°/45° where obliquity produces a measurable non-trivial difference.
- `CACHE_AVAILABLE=False` reload: `importlib.reload(ketu.cycles.calculator)` triggers a fresh import; `sys.modules["ketu.cache"] = None` causes the `except ImportError` to fire. Always restored in `finally` to prevent state leakage.
- `find_exact_aspect:362` (after-loop return): proven unreachable because after 50 bisection iterations on any initial range, `abs(right-left) = initial_range / 2^50` always falls below tolerance=0.001, triggering line 354 first. The alternating-mock test covers the function thoroughly but line 362 remains in the missing list (dead code).

## Next Phase Readiness

- 21-02 (orbital.py div/0 guards) can proceed on clean baseline: 99% coverage, all aspect/house/cache modules at 100%
- 21-04 will need to add `exclude_lines` entries for: `orbital.py:227`, `time.py:369`, `planets.py:362`, `planets.py:448`, and `display.py:28` — all proven dead defensive branches
- No pragmas added anywhere in the codebase (zero pragma policy maintained)

---
*Phase: 21-quality*
*Completed: 2026-05-29*
