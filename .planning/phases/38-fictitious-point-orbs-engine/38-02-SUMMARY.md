---
phase: 38-fictitious-point-orbs-engine
plan: "02"
subsystem: testing
tags: [orb, fictitious-points, rahu, ketu, lilith, synastry, oracles, regression-sweep, ORB-03]
dependency_graph:
  requires:
    - phase: 38-01
      provides: "Rahu/Ketu/Lilith orb 0→2° in ketu/core.py + _is_tautological_node_opposition filter"
  provides:
    - "tests/synastry/test_orbs.py: oracles rewritten 0.0→1.0 for Rahu/Ketu/Lilith self-pairs (D-07)"
    - "tests/synastry/test_modes_idempotent.py: stale zero-orb rationale refreshed (D-06)"
    - "tests/cli/fixtures/v1_1_reference_output.txt: re-pinned with 2 new Rahu aspects (ORB-03)"
  affects:
    - "ORB-03 requirement fully implemented — no silent oracle update"
tech_stack:
  added: []
  patterns:
    - "Deliberate oracle re-pinning: every changed detection documented with reason (new in-orb node aspect)"
    - "Fixture regeneration via live engine: python -m ketu ... 2>/dev/null > fixture"
key_files:
  created: []
  modified:
    - "tests/synastry/test_orbs.py (3 oracle rewrites + rename + docstrings)"
    - "tests/synastry/test_modes_idempotent.py (stale docstring refresh)"
    - "tests/cli/fixtures/v1_1_reference_output.txt (+2 new Rahu aspect lines)"
decisions:
  - "D-07 oracles renamed from *_zero_orb to *_two_degree_orb (rationale was false post-ORB-01)"
  - "Idempotent diagonal invariants unchanged — dist==0 on self-pair keeps emitted orb at 0.0 regardless of orb_limit"
  - "CLI snapshot v1_1_reference_output.txt re-pinned; harmonics_h7_reference_output.txt unchanged (no Rahu/Ketu aspects in septile family at this date)"
  - "mypy --strict has 225 pre-existing errors (baseline identical before and after these changes, all in ketu/cycles.*, ketu/calculations, and test stubs suppressed by pyproject.toml overrides)"
requirements-completed: [ORB-03]
duration: ~35min
completed: "2026-06-15"
---

# Phase 38 Plan 02: ORB-03 — Oracle Regression Sweep Summary

**Synastry orb-limit oracles rewritten 0.0→1.0 for Rahu/Ketu/Lilith self-pairs + CLI snapshot re-pinned with two new Rahu detections (Sun-Rahu Quincunx, Venus-Rahu Trine) that appear because Rahu orb 0→2°.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-06-15T19:00:00Z
- **Completed:** 2026-06-15T19:39:31Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Task 1 (D-07): Rewrote 3 synastry orb-limit oracles from `== 0.0` to `== 1.0`, renamed test functions from `*_zero_orb` to `*_two_degree_orb`, refreshed docstrings with ORB-01/phase-38 rationale, updated file docstring.
- Task 2 (D-06): Verified idempotent diagonal invariants still hold at 2° (all 16 self-pairs, `aspect_type==0`, `|orb|<1e-6` — unchanged); refreshed two stale docstrings that falsely stated "zero natal orbs" for Rahu/Ketu/Lilith.
- Task 3 (ORB-03 sweep): Full suite green at 1666 passed + 2 skipped, 100% coverage; CLI snapshot re-pinned with deliberate documentation of each new detection.

## Task Commits

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | D-07: rewrite synastry orb-limit oracles 0.0→1.0 | aa0d394 | tests/synastry/test_orbs.py |
| 2 | D-06: refresh stale zero-orb rationale in idempotent invariants | 5f64b51 | tests/synastry/test_modes_idempotent.py |
| 3 | ORB-03 regression sweep — re-pin CLI snapshot with 2° Rahu aspects | 0d59073 | tests/cli/fixtures/v1_1_reference_output.txt |

## Files Created/Modified

- `tests/synastry/test_orbs.py` — 3 functions renamed + assertions rewritten + docstrings corrected
- `tests/synastry/test_modes_idempotent.py` — module and test docstrings refreshed (assertions unchanged)
- `tests/cli/fixtures/v1_1_reference_output.txt` — 2 new lines added (new Rahu aspects)

## Oracle/Fixture Changes — Deliberate Re-Pin Register (ORB-03 Mandate)

| File | Change | Reason |
|------|--------|--------|
| `tests/synastry/test_orbs.py` | `synastry_orb_limit(10,10,0)`: `0.0 → 1.0` | **New orb**: Rahu natal orb 0→2°; math `(2+2)/2 × coef_conj(1) × 0.5 = 1.0` |
| `tests/synastry/test_orbs.py` | `synastry_orb_limit(11,11,0)`: `0.0 → 1.0` | **New orb**: Ketu natal orb 0→2°; same math |
| `tests/synastry/test_orbs.py` | `synastry_orb_limit(12,12,0)`: `0.0 → 1.0` | **New orb**: Lilith natal orb 0→2°; same math |
| `tests/cli/fixtures/v1_1_reference_output.txt` | Added line: `Sun - Rahu: Quincunx -6º45'18"` | **New in-orb aspect**: Rahu orb 0→2° brings Sun↔Rahu into Quincunx range at J2000 |
| `tests/cli/fixtures/v1_1_reference_output.txt` | Added line: `Venus - Rahu: Trine 3º33'33"` | **New in-orb aspect**: Rahu orb 0→2° brings Venus↔Rahu into Trine range at J2000 |

**No unexplained deltas found.** All changes are exclusively type (a): new in-orb node aspect appearing due to Rahu orb expansion. No (b) Rahu↔Ketu Opposition suppression in these files (D-05 — synastry is not filtered; natal filter from ORB-02 is covered in Plan 01's own tests).

## Already-present Rahu/Ketu detections (unchanged, for context)

The following aspects were already in `v1_1_reference_output.txt` before Plan 02 (were within old planetary orb range):
- `Mercury - Rahu: Quincunx 3º13'56"` — Mercury has orb=8, Rahu was 0 → already at (8+0)/2=4° limit
- `Jupiter - Ketu: Binovile -1º50'8"` — Jupiter orb=10; Ketu was 0 → (10+0)/2=5° limit
- `Neptune - Rahu: Opposition 1º56'32"` — Neptune orb=8 → 4° limit sufficient
- `Neptune - Ketu: Conjunction 1º55'54"` — same
- `Neptune - Lilith: Novile 0º16'33"` — same

These are NOT new detections from Plan 02 and are unchanged.

## Decisions Made

- **Rename over comment:** Renamed `test_*_zero_orb` to `test_*_two_degree_orb` because the old names would actively mislead — the rationale in the old docstrings was wrong. A docstring-only fix leaves misleading function names in git blame.
- **harmonics_h7_reference_output.txt untouched:** Verified via `diff` against HEAD; the septile-family subset produces no new Rahu/Ketu aspects at J2000. No change needed.
- **mypy --strict not resolved:** 225 pre-existing mypy errors (identical baseline before/after this plan's changes). These are suppressed in `pyproject.toml` overrides for `tests.*` and `ketu.calculations`/`ketu.cycles.*` modules. Scope boundary: these errors are not caused by this plan's changes, and fixing them would require ketu/ source edits prohibited by this plan.

## Deviations from Plan

None — plan executed exactly as written.

The regression sweep confirmed only the expected 2 CLI snapshot lines were stale (Plan 02's `files_modified` list was accurate). No additional oracle/fixture files required re-pinning beyond what the planner scoped.

## Issues Encountered

- **Worktree base mismatch at start:** The worktree HEAD was at pre-38-01 commit `4a08af9` (main was at `4d2ba9c` with Plan 01 merged). Required `git reset --hard main` to advance the worktree to the correct base. No work was lost (no local commits existed at that point). This is a worktree provisioning race condition where the orchestrator created the worktree before Plan 01's merge landed on `main`.

## Next Phase Readiness

- ORB-03 fully implemented: all test files referencing Rahu/Ketu/Lilith are green
- Full suite: 1666 passed, 2 skipped, 100% coverage, no regressions
- Phase 38 complete: ORB-01 (orb 0→2°) + ORB-02 (tautological filter) + ORB-03 (oracle sweep) all done
- v1.7.0 milestone readiness: the ORB-01/02/03 requirements are fully satisfied

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes. Test-only file changes. T-38-04 (silent oracle drift) mitigated: every changed detection documented above. T-38-05 (accidental ketu/ edit): git diff confirms only `tests/` files changed. T-38-06 (coverage erosion): 100% maintained, no new `# pragma: no cover`.

## Known Stubs

None.

## Self-Check: PASSED

- `tests/synastry/test_orbs.py` exists and contains `synastry_orb_limit(10, 10, 0) == 1.0`: FOUND
- `tests/synastry/test_modes_idempotent.py` exists and stale docstring updated: FOUND
- `tests/cli/fixtures/v1_1_reference_output.txt` contains `Sun     - Rahu        : Quincunx`: FOUND
- Commits aa0d394, 5f64b51, 0d59073: FOUND in git log
- `pytest tests/` exits 0, 1666 passed, 100% coverage: CONFIRMED
- git diff main..HEAD --name-only shows only tests/ files: CONFIRMED
