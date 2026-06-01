---
phase: 26-aspects-data-driven
plan: "02"
subsystem: aspects
tags: [numpy, structured-arrays, aspects, harmonics, presets, configurable-aspects, api, cli]

requires:
  - phase: 26-aspects-data-driven
    plan: "01"
    provides: "core.aspects 5-field dtype with harmonic (i4) column — aspects_for_harmonics reads harmonic column"

provides:
  - "aspects_for_harmonics(harmonics: Sequence[int]) -> frozen np.bool_[14] mask (data-driven from harmonic column)"
  - "TRADITIONAL redefined via aspects_for_harmonics([1,2,3,6]) — single source of truth"
  - "EXTENDED redefined via aspects_for_harmonics([1,2,3,5,6,9,10]) — single source of truth"
  - "Library default resolve_aspect_set(None) == TRADITIONAL (7 half-circle aspects)"
  - "CLI bare --harmonics stays classical (5) — v1.0/v1.1 byte-stable contract preserved"
  - "chart-layer D-07 ratchet re-pointed: compute_chart() default == aspects='traditional' (7)"
  - "Bug fix: calculate_aspects loop now iterates only selected aspects (was first-match-wins over ALL 14)"

affects:
  - "26-03: CHANGELOG/UPGRADING must document the library default shift (5->7) and aspects_for_harmonics API"
  - "27-release: ketu 1.3.0 ships with TRADITIONAL as default; API surface change documented"
  - "Kala downstream: no impact on aspect matrix output (they pass aspects= explicitly)"

tech-stack:
  added: []
  patterns:
    - "aspects_for_harmonics: data-driven mask composition from harmonic column — no hardcoded indices"
    - "Deliberate CLI/library divergence: CLI pins to classical(5) explicitly; library default is TRADITIONAL(7)"
    - "Rule 1 auto-fix pattern: loop vs vectorized divergence exposed by default shift, fixed at source"

key-files:
  created:
    - tests/cli/test_cli_default_divergence.py
  modified:
    - ketu/aspects/presets.py
    - ketu/aspects/__init__.py
    - ketu/aspects/calculator.py
    - ketu/charts/api.py
    - ketu/cli/aspects_cmd.py
    - tests/charts/test_aspect_matrix.py
    - tests/test_aspect_presets.py
    - tests/test_coverage_improvements.py

key-decisions:
  - "aspects_for_harmonics returns frozen length-14 np.bool_ mask — drop-in for any preset, no new type"
  - "Valid harmonics {1,2,3,5,6,9,10} derived data-driven from _ASPECTS['harmonic'] (not hardcoded)"
  - "CLASSICAL stays curated 5-index list — not harmonic-derivable (Sextile=H3 but drops Semi-sextile/Quincunx H6 — Pitfall 7)"
  - "CLI bare --harmonics None branch explicitly calls resolve_aspect_set('classical') — byte-stable contract"
  - "Aspect Timing Example in CLI pinned to aspects='classical' — v1.0 demo block stays byte-identical"
  - "chart-layer D-07 ratchet re-pointed to 'traditional' (not pinned back to classical)"
  - "calculate_aspects loop refactored to iterate only selected aspects (bug fix: was blocking Quincunx behind Biquintile)"
  - "H3 sextile/trine convention frozen: aspects_for_harmonics([3]) returns Sextile+Trine, NOT Semi-sextile/Quincunx (H6)"

patterns-established:
  - "Data-driven harmonic composition: aspects_for_harmonics reads _ASPECTS['harmonic'] column, never hardcodes"
  - "CLI divergence pattern: explicit preset name in CLI call instead of None-default to preserve byte-stability"
  - "First-match-wins per selected-set: calculate_aspects iterates mask-selected aspects only (no post-filter)"

duration: 21min
completed: 2026-06-01
---

# Phase 26 Plan 02: aspects_for_harmonics + library default flip 5->7 + CLI pin Summary

**aspects_for_harmonics data-driven API + TRADITIONAL/EXTENDED harmonic-derived redefinition + library default flipped to 7 half-circle aspects while CLI stays byte-stable at classical(5)**

## Performance

- **Duration:** 21 min
- **Started:** 2026-06-01T14:32:49Z
- **Completed:** 2026-06-01T14:54:34Z
- **Tasks:** 3
- **Files modified:** 8 (plus 1 file created)

## Accomplishments

- `aspects_for_harmonics([1,2,3,6])` = TRADITIONAL (7), `([5,9,10])` = 7 minors, `([1,2,3,5,6,9,10])` = EXTENDED (14); `([7])` raises ValueError; returns frozen mask
- TRADITIONAL/EXTENDED redefined on top of harmonic table (single source of truth); bit-identical to prior index-based definitions
- `resolve_aspect_set(None)` default flipped CLASSICAL(5) → TRADITIONAL(7); `ketu.cli.aspects_cmd` pinned to `"classical"` explicitly — all 139 CLI tests green unchanged
- chart-layer D-07 ratchet re-pointed: `test_aspect_matrix_default_aspects_is_traditional` asserts `compute_chart()` default == `aspects="traditional"` (7)
- Pre-existing bug fixed: `calculate_aspects` loop was blocking Quincunx(H6) behind Biquintile(H5) for pairs in both orbs; now iterates only selected aspects (matching vectorized)
- 1399 tests, 100% coverage, 57 doctests green, mypy --strict clean

## Task Commits

1. **Tasks 1+2 (atomic): aspects_for_harmonics + flip library default + pin CLI** — `ce01b22` (feat)
2. **Task 3: flip preset/default tests + aspects_for_harmonics coverage + bug fix** — `15cc462` (test)

**Plan metadata:** (final commit below)

## Files Created/Modified

- `/home/loc/workspace/ketu/ketu/aspects/presets.py` — `_VALID_HARMONICS` computed data-driven; `aspects_for_harmonics` function added; TRADITIONAL/EXTENDED redefined via `aspects_for_harmonics`; `resolve_aspect_set` default flipped to TRADITIONAL; docstrings updated; `aspects_for_harmonics` added to `__all__`
- `/home/loc/workspace/ketu/ketu/aspects/__init__.py` — `aspects_for_harmonics` added to import block and `__all__`
- `/home/loc/workspace/ketu/ketu/aspects/calculator.py` — 4 docstrings updated (CLASSICAL→7 half-circle); `calculate_aspects` loop refactored to iterate only selected aspects (bug fix)
- `/home/loc/workspace/ketu/ketu/charts/api.py` — 3 docstrings updated (CLASSICAL→TRADITIONAL default)
- `/home/loc/workspace/ketu/ketu/cli/aspects_cmd.py` — None branch changed to `resolve_aspect_set("classical")`; Aspect Timing Example pinned to `aspects="classical"`
- `/home/loc/workspace/ketu/tests/charts/test_aspect_matrix.py` — module docstring updated (D-07 comment); `_CLASSICAL_INDICES` comment updated; `test_aspect_matrix_default_aspects_is_traditional` (renamed+re-pointed)
- `/home/loc/workspace/ketu/tests/cli/test_cli_default_divergence.py` — NEW: 3 regression tests locking CLI(5)!=library(7) divergence
- `/home/loc/workspace/ketu/tests/test_aspect_presets.py` — 3 default tests flipped to TRADITIONAL; `aspects_for_harmonics` imported; `TestAspectsForHarmonics` class added (16 tests: 8 happy paths + 5 error paths + 3 structural)
- `/home/loc/workspace/ketu/tests/test_coverage_improvements.py` — 2 tests added for `get_aspect` conjunction path (line 79) and no-aspect path (line 82)

## aspects_for_harmonics Contract

```python
# Valid harmonics (data-driven from _ASPECTS["harmonic"]):
_VALID_HARMONICS = frozenset({1, 2, 3, 5, 6, 9, 10})

aspects_for_harmonics([1, 2, 3, 6])          # 7 half-circle == TRADITIONAL
aspects_for_harmonics([5, 9, 10])             # 7 minors (full-circle)
aspects_for_harmonics([1, 2, 3, 5, 6, 9, 10]) # 14 all == EXTENDED
aspects_for_harmonics([1])                    # Conjunction+Opposition (sum 2)
aspects_for_harmonics([3])                    # Sextile+Trine (H3, half-circle conv.)
aspects_for_harmonics([6])                    # Semi-sextile+Quincunx (H6)
aspects_for_harmonics([])                     # all-False mask (sum 0, valid)
aspects_for_harmonics([7])                    # raises ValueError (not in table)
aspects_for_harmonics([True])                 # raises ValueError (bool guard)
aspects_for_harmonics(["3"])                  # raises ValueError (non-int)
```

Return: frozen `np.bool_[14]` mask (writeable=False). Drop-in for any preset.

## Bit-Identity Proof (TRADITIONAL/EXTENDED)

| Preset | Old definition (indices) | New definition (harmonics) | Bit-identical |
|---|---|---|---|
| TRADITIONAL | `[0, 1, 4, 7, 9, 11, 13]` | `aspects_for_harmonics([1, 2, 3, 6])` | YES — isin selects same rows |
| EXTENDED | `np.arange(14)` | `aspects_for_harmonics([1,2,3,5,6,9,10])` | YES — all harmonics in table |

## CLI/Library Divergence (User Decision 1)

| Surface | Default | Mechanism | Byte-stable |
|---|---|---|---|
| Library (`resolve_aspect_set(None)`) | TRADITIONAL (7) | `default=TRADITIONAL` param | N/A (new contract) |
| CLI bare `--harmonics` | CLASSICAL (5) | `resolve_aspect_set("classical")` explicit | YES — fixture unchanged |

Regression test: `tests/cli/test_cli_default_divergence.py` locks `library_default(7) != cli_default(5)`.

## Chart-Layer D-07 Ratchet

- Old: `test_aspect_matrix_default_aspects_is_classical` — asserted `compute_chart()` default == `aspects="classical"` (5)
- New: `test_aspect_matrix_default_aspects_is_traditional` — asserts `compute_chart()` default == `aspects="traditional"` (7)
- Structural tests (symmetry, diagonal sentinels, scalar shape, batch shape) all hold for 5 OR 7 aspects — unchanged
- Audit: no other test in `tests/charts`, `tests/synastry`, `tests/composite` derives aspect CONTENT from the default; all use `aspects=` explicitly or check shape/structure only

## Decisions Made

- `aspects_for_harmonics` returns frozen `np.bool_[14]` — same type as presets, drop-in, no new type through hot loops
- CLASSICAL stays curated index list (Pitfall 7): keeps Sextile/H3 but drops Semi-sextile/Quincunx/H6, so not pure-harmonic
- Aspect Timing Example in CLI pinned to `aspects="classical"` explicitly — v1.0 demo block must stay byte-identical
- calculate_aspects refactored to iterate only selected aspects (same first-match-wins, but within the selected set)
- H3 Sextile/Trine frozen: `aspects_for_harmonics([3])` returns indices 4 (Sextile) + 9 (Trine), consistent with 26-01 half-circle convention

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] CLI Aspect Timing Example implicit default change**
- **Found during:** Task 2 (CLI pin to classical)
- **Issue:** The "Aspect Timing Example" block in `aspects_cmd.py` called `find_aspects_between_dates(jd-15, jd+15, sun_id, moon_id)` without explicit `aspects=`. Before the flip it used CLASSICAL(5); after the flip it used TRADITIONAL(7), finding Semi-sextile aspects instead of Sextile/Square — breaking `test_v1_1_reference_byte_stable.py`
- **Fix:** Added `aspects="classical"` explicitly to the `find_aspects_between_dates` call, with a comment explaining the intentional divergence
- **Files modified:** `ketu/cli/aspects_cmd.py`
- **Verification:** All 139 CLI tests green, including `test_v1_1_reference_byte_stable.py`
- **Committed in:** `ce01b22` (Task 1+2 atomic commit)

**2. [Rule 1 - Bug] calculate_aspects loop first-match-wins over ALL aspects, not selected set**
- **Found during:** Task 3 (test suite run)
- **Issue:** `calculate_aspects` used `get_aspect()` which iterates ALL 14 aspects first-match-wins, then post-filtered. With TRADITIONAL(7) as default, pairs where Biquintile/H5 (unselected) was in-orb before Quincunx/H6 (selected) got the Biquintile result silently discarded — pair absent from output. Vectorized correctly checked only selected aspects. 3 parametrized regression tests failed (loop found 20/26/22 aspects, vectorized found 22/27/23).
- **Fix:** Rewrote `calculate_aspects` inner loop to iterate only `selected_indices` (mask-filtered), same first-match-wins behavior but within the selected set
- **Files modified:** `ketu/aspects/calculator.py`
- **Verification:** All 7 regression tests in `test_bug_02_aspects.py` pass; loop==vectorized for TRADITIONAL default
- **Committed in:** `15cc462` (Task 3 commit)

**3. [Rule 1 - Bug] get_aspect coverage gaps (lines 79, 82) exposed by calculate_aspects refactor**
- **Found during:** Task 3 (100% coverage check)
- **Issue:** After removing `get_aspect` calls from `calculate_aspects`, lines 79 (`return body1, body2, i_asp, dist` — conjunction) and 82 (`return None` — no aspect) were no longer covered by the main flow. Coverage dropped to 99.91%.
- **Fix:** Added 2 targeted tests in `test_coverage_improvements.py`: `test_get_aspect_conjunction_return` (JD 2451550.0, Sun-Moon ~2.95° in-orb) and `test_get_aspect_no_aspect_returns_none` (Sun-Mars J2000, no aspect)
- **Files modified:** `tests/test_coverage_improvements.py`
- **Verification:** 100% coverage restored (1399 tests, 0 misses)
- **Committed in:** `15cc462` (Task 3 commit)

---

**Total deviations:** 3 auto-fixed (Rule 1 — all bugs exposed by the library default shift)
**Impact on plan:** All fixes necessary for correctness and gate compliance. No scope creep. The CLI byte-stable contract was preserved throughout; the calculate_aspects bug was pre-existing but only surfaced when the default moved from CLASSICAL(5) to TRADITIONAL(7).

## Issues Encountered

None additional. All issues resolved via auto-fix per deviation rules.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Phase 26 plan 03 (CHANGELOG/UPGRADING + concepts.md/api.md + fr gettext) can now document the full Phase 26 surface:
  - New `aspects_for_harmonics` API at `ketu.aspects.aspects_for_harmonics`
  - Library default shift 5→7 (BREAKING for callers relying on implicit default)
  - CLI byte-stable (no breaking change for CLI users)
  - chart-layer now defaults to TRADITIONAL (7 aspects in `aspect_matrix`)
  - CLASSICAL/TRADITIONAL/EXTENDED still available as named presets
- ketu/aspects/presets.py is the single source of truth for aspect set selection

## Self-Check: PASSED

- [x] `ketu/aspects/presets.py` exists with `aspects_for_harmonics` and `_VALID_HARMONICS`
- [x] `ketu/aspects/__init__.py` exports `aspects_for_harmonics`
- [x] `ketu/cli/aspects_cmd.py` has `resolve_aspect_set("classical")` (not None)
- [x] `tests/cli/test_cli_default_divergence.py` created with 3 tests
- [x] `tests/charts/test_aspect_matrix.py` has `test_aspect_matrix_default_aspects_is_traditional`
- [x] Commit `ce01b22` (feat Tasks 1+2) exists
- [x] Commit `15cc462` (test Task 3) exists
- [x] 1399 tests pass, 100% coverage, 57 doctests green, mypy --strict clean

---
*Phase: 26-aspects-data-driven*
*Completed: 2026-06-01*
