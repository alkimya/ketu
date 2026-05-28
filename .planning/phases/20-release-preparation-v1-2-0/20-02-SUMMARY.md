---
phase: 20-release-preparation-v1-2-0
plan: 02
subsystem: docs
tags: [numpydoc, docstrings, ci, makefile, pyproject]

# Dependency graph
requires:
  - phase: 20-release-preparation-v1-2-0
    provides: "Plan 20-01 — action version pins (tests.yml already at checkout@v5 etc.)"
provides:
  - "Zero numpydoc violations across all 61 linted ketu/*.py files"
  - "Blocking numpydoc CI gate in tests.yml (continue-on-error removed)"
  - "GL01 suppression removed from pyproject.toml"
  - "Makefile doc-gates fails on violations (|| true removed)"
affects: [phase-20-plan-03]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "NumPy docstring summary on line AFTER opening triple-quote (GL01 compliance)"
    - "All docstring summaries end with period (SS03 compliance)"
    - "See Also before Notes in numpydoc section order (GL07 compliance)"

key-files:
  created: []
  modified:
    - ketu/ephemeris/time.py
    - ketu/ephemeris/coordinates.py
    - ketu/ephemeris/orbital.py
    - ketu/ephemeris/planets.py
    - ketu/cache/ephemeris_cache.py
    - ketu/aspects/core.py
    - ketu/aspects/calculator.py
    - ketu/aspects/transits.py
    - ketu/aspects/timelines.py
    - ketu/aspects/windows.py
    - ketu/aspects/presets.py
    - .github/workflows/tests.yml
    - pyproject.toml
    - Makefile
    - "(44 additional files for GL01 mass-fix)"

key-decisions:
  - "GL01 suppression removal required fixing 214 pre-existing violations across 44 files — the plan's claim of zero GL01 violations was wrong (they were suppressed, not absent). All files use summary-on-opening-line style. Auto-fixed via Rule 1."
  - "GL07 section-order violations in composite/api.py, composite/core.py, returns/lunar.py, returns/solar.py, houses/api.py fixed by reordering See Also before Notes."
  - "GL02 violations (3 instances in introspection.py + 1 in ephemeris_cache.py) from single-line docstrings converted to multi-line — closing quotes moved to own line."

patterns-established:
  - "numpydoc gate is now fully blocking: CI fails, Makefile fails, no suppression"
  - "All future docstrings must put summary on line after opening triple-quote"

# Metrics
duration: 25min
completed: 2026-05-28
---

# Phase 20 Plan 02: numpydoc Fix and Gate Flip Summary

**All ~103 numpydoc violations fixed (SS03/PR09/RT01/RT05/PR08/PR01/GL08/GL06/GL07/GL01/GL02) and gate flipped to blocking in CI, pyproject.toml, and Makefile.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-05-28T20:23:15Z
- **Completed:** 2026-05-28T20:48:00Z
- **Tasks:** 2
- **Files modified:** 58 (11 target + 47 additional for GL01 mass-fix + 3 config)

## Accomplishments

- Fixed all 103 originally-catalogued violations (SS03 ×64, PR09 ×15, RT05 ×8, RT01 ×6, PR08 ×2, PR01 ×2, GL08 ×1, GL06+GL07 ×2) across 11 source files
- Fixed 214 pre-existing GL01 violations across 44 files (hidden by suppression) plus downstream GL02 (4) and GL07 (5) that appeared once GL01 parsing was restored
- Removed `continue-on-error: true` from tests.yml and Phase-20 TODO comment block; step renamed to "Doc style audit (numpydoc — blocking)"
- Removed `"GL01"` suppression from `pyproject.toml [tool.numpydoc_validation].checks`
- Removed `|| true` from Makefile `doc-gates` numpydoc lint line; echo updated to "Doc gates OK (interrogate + numpydoc both blocking)."
- `make doc-gates` exits 0 on clean tree; exits 2 on any violation (sanity-checked)
- 1284 tests pass, interrogate 100%, mypy pre-existing error unaffected

## Task Commits

1. **Task 1: Fix all numpydoc violations in the 11 source files** - `ffd054f` (fix)
2. **Task 2: Flip the gate to blocking + GL01 mass-fix** - `ae80c17` (chore)

## Files Created/Modified

### Task 1 — docstring fixes in 11 target files
- `ketu/ephemeris/time.py` — SS03 ×6, PR08 ×2, PR09 ×8, RT05 ×6 fixed
- `ketu/ephemeris/coordinates.py` — SS03 ×10 fixed
- `ketu/ephemeris/orbital.py` — SS03 ×9, PR01 ×1, RT01 ×1 fixed (normalize_angle gained full Parameters+Returns)
- `ketu/ephemeris/planets.py` — SS03 ×8, GL08 ×1 fixed (nested get_angle_diff got docstring)
- `ketu/cache/ephemeris_cache.py` — SS03 ×7, PR01 ×1, RT01 ×2 fixed
- `ketu/aspects/core.py` — SS03 ×10 fixed
- `ketu/aspects/calculator.py` — SS03 ×7 fixed
- `ketu/aspects/transits.py` — SS03 ×3 fixed
- `ketu/aspects/timelines.py` — RT01 ×3, SS03 ×1, PR09 ×7, RT05 ×1 fixed
- `ketu/aspects/windows.py` — SS03 ×2 fixed
- `ketu/aspects/presets.py` — GL06+GL07 ×2 fixed (non-standard sections absorbed into Notes)

### Task 2 — gate flip + GL01 mass-fix
- `.github/workflows/tests.yml` — continue-on-error removed, TODO comment removed, step renamed
- `pyproject.toml` — GL01 suppression entry removed
- `Makefile` — || true removed, echo updated
- `ketu/` (44 files) — GL01 mass-fix: summary moved to line after opening `"""`
- `ketu/composite/api.py` — GL07 fixed (See Also moved before Notes)
- `ketu/composite/core.py` — GL07 fixed (See Also moved before Notes)
- `ketu/returns/lunar.py` — GL07 fixed (See Also moved before Notes)
- `ketu/returns/solar.py` — GL07 fixed (See Also moved before Notes)
- `ketu/houses/api.py` — GL07 fixed (Notes moved before Examples)
- `ketu/cli/introspection.py` — GL02 ×3 fixed (closing quotes moved to own line)
- `ketu/cache/ephemeris_cache.py` — GL02 ×1 fixed (clear_memory docstring)

## Decisions Made

- GL01 suppression removal revealed 214 violations across 44 files (the plan claimed zero — they were suppressed, not absent). Auto-fixed via Rule 1 (bug in the plan's verification premise). Purely mechanical: moved docstring summary to the line after `"""`.
- GL07 section-order violations in 5 functions fixed by reordering (See Also must come before Notes in NumPy convention).
- GL02 violations (4 instances) from single-line docstrings that had closing `"""` on same line as text — fixed by putting closing quotes on their own line.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan's "zero GL01 violations" claim was incorrect — 214 violations across 44 files**
- **Found during:** Task 2 (flip gate)
- **Issue:** When GL01 suppression was removed from pyproject.toml, 214 violations appeared across 44 files. The plan stated "Verified: there are currently ZERO live GL01 violations, so removing the suppression is safe" — but this was verified while GL01 was still suppressed. The violations were hidden, not absent.
- **Fix:** Mass-fixed all 44 files by inserting newline after opening `"""` so summary is on its own line (GL01 compliant). Also fixed 4 GL02 violations (closing quotes on text line) and 5 GL07 violations (section order: Notes before See Also in 4 functions, Examples before Notes in 1 function) that were previously hidden by GL01 parse failures.
- **Files modified:** 44 source files + composite/api.py + composite/core.py + returns/lunar.py + returns/solar.py + houses/api.py + cli/introspection.py + cache/ephemeris_cache.py
- **Verification:** `python -m numpydoc lint $(find ketu ...)` exits 0; `make doc-gates` exits 0; `make doc-gates` exits 2 on intentionally-broken docstring (sanity check passed)
- **Committed in:** ae80c17 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — bug in plan's verification premise)
**Impact on plan:** The GL01 mass-fix was a prerequisite for the gate flip. All changes are purely docstring style, zero logic change. No scope creep — this is exactly what OPS-02 finalization required.

## Issues Encountered

None beyond the GL01 suppression discovery above (handled as Rule 1 auto-fix).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- OPS-02 finalized: numpydoc gate is fully blocking in CI, pyproject.toml, and Makefile
- Phase 20 Plan 03 (CHANGELOG + version bump) is the final remaining plan for v1.2.0 release
- 1284 tests green, interrogate 100%, mypy clean (one pre-existing error in returns/_solve.py unrelated to this plan)

---
*Phase: 20-release-preparation-v1-2-0*
*Completed: 2026-05-28*
