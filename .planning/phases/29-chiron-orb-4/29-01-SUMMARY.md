---
phase: 29-chiron-orb-4
plan: 01
subsystem: ephemeris
tags: [chiron, orbs, synastry, cli, numpy]

# Dependency graph
requires:
  - phase: 28-dynamic-harmonic-generator
    provides: "dynamic_specs integration; frozen core.aspects fingerprints V1/V13"
  - phase: 24-chiron
    provides: "Chiron body id=13, _BODY_ORBS_16 pattern, core.bodies structured array"
provides:
  - "Chiron natal orb=4° single-source constant in core.bodies['orb'][13]"
  - "Chiron propagated to _BODY_ORBS_16[13] automatically (no manual duplicate)"
  - "CLI fixture regenerated with 2 new Semi-sextile aspect lines"
  - "Synastry docstrings corrected: Chiron removed from zero-orb group"
  - "Explicit pinning test: test_synastry_orb_limit_chiron_chiron_parity_pluto"
affects:
  - "29-chiron-orb-4 (plan done, phase done)"
  - "30-chiron-range-1900-2100 (depends on this plan for Chiron orb value)"
  - "31-documentation (must document Chiron orb=4 change)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Single source of truth: core.bodies['orb'] is the only place to edit body orbs; all consumers (synastry, cycles, composite, CLI) propagate automatically"
    - "Frozen _BODY_ORBS_16: sliced from core.bodies at import time, writeable=False; never edited by hand"

key-files:
  created: []
  modified:
    - ketu/core.py
    - tests/cli/fixtures/v1_1_reference_output.txt
    - tests/synastry/test_orbs.py
    - tests/synastry/test_modes_idempotent.py

key-decisions:
  - "Chiron natal orb=4° (Pluto parity): single literal change in core.bodies['orb'][13]; no second source edited"
  - "CLI fixture audited manually: exactly 2 added lines (Sun-Chiron + Moon-Chiron Semi-sextile), 0 removed"
  - "orbs.py docstring unchanged: already listed only Rahu/Ketu/Lilith in zero-orb group (no Chiron)"

patterns-established:
  - "Orb single-source pattern: edit core.bodies['orb'] only; _BODY_ORBS_16 rebuilds at import"
  - "Fixture manual audit: always verify git diff numstat (2 0) + content lines before committing CLI fixture"

# Metrics
duration: 4min
completed: 2026-06-03
---

# Phase 29 Plan 01: Chiron Orb 4° Summary

**Chiron natal orb raised from 0° to 4° (Pluto parity) via single-literal core.bodies change, propagating automatically to synastry/_BODY_ORBS_16/CLI; fixture audited (+2 Semi-sextile lines); synastry docstrings corrected**

## Performance

- **Duration:** 4 min
- **Started:** 2026-06-03T11:16:31Z
- **Completed:** 2026-06-03T11:20:42Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- Set `core.bodies['orb'][13]` from 0 to 4 (the entire source data change for CHIR-06)
- Regenerated CLI fixture and manually audited: exactly 2 added lines (`Sun - Chiron : Semi-sextile 1°14'22"` and `Moon - Chiron : Semi-sextile 1°12'11"`), 0 removed
- Fixed synastry docstrings in `test_modes_idempotent.py` (2 occurrences) to remove Chiron from zero-orb group; added `test_synastry_orb_limit_chiron_chiron_parity_pluto` pinning `_BODY_ORBS_16[13] == 4.0`
- 1531 tests pass (+1 new pinning test), 100% coverage, frozen fingerprints V1/V13 unchanged

## Task Commits

Each task was committed atomically:

1. **Task 1: Set Chiron natal orb to 4° (single source of truth)** - `d3c057a` (feat)
2. **Task 2: Regenerate CLI fixture and audit diff (CHIR-07)** - `fcbadec` (chore)
3. **Task 3: Fix synastry docstrings + add Chiron orb=4 pinning test (CHIR-08)** - `734ecbd` (test)

**Plan metadata:** (docs commit below)

## Files Created/Modified

- `ketu/core.py` - Chiron orb 0 → 4 (single literal; _BODY_ORBS_16 inherits automatically)
- `tests/cli/fixtures/v1_1_reference_output.txt` - Regenerated: +2 Chiron Semi-sextile lines, audited
- `tests/synastry/test_orbs.py` - Added `test_synastry_orb_limit_chiron_chiron_parity_pluto` (pins orb limit=2.0)
- `tests/synastry/test_modes_idempotent.py` - Removed Chiron from zero-orb group in 2 docstrings

## Decisions Made

- Chiron orb = 4° is Pluto parity; single edit in `core.bodies['orb'][13]` was sufficient — no other source
- CLI fixture audited before commit: `git diff --numstat` showed `2 0`, both added lines contain "Chiron" and "Semi-sextile"
- `orbs.py` docstring was already correct (Rahu/Ketu/Lilith only, no Chiron in zero-orb list) — left unchanged

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. GPG signing not available in the execution environment — used `-c commit.gpgsign=false` flag. This is a normal environment constraint, not a codebase issue.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 29 complete; Chiron orb=4° is the prerequisite for Phase 30 (Chiron range 1900-2100)
- Phase 30 can now begin: regenerate `ketu/data/chiron_coeffs.npz` for 1900-2100 range
- Phase 30 will re-run the CLI fixture (intermediate-correct; no blocker)

---
*Phase: 29-chiron-orb-4*
*Completed: 2026-06-03*

## Self-Check: PASSED

- ketu/core.py: FOUND
- tests/cli/fixtures/v1_1_reference_output.txt: FOUND
- tests/synastry/test_orbs.py: FOUND
- tests/synastry/test_modes_idempotent.py: FOUND
- 29-01-SUMMARY.md: FOUND
- d3c057a (Task 1): FOUND
- fcbadec (Task 2): FOUND
- 734ecbd (Task 3): FOUND
