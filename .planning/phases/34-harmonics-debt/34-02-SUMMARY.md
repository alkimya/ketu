---
phase: 34-harmonics-debt
plan: 02
subsystem: aspects
tags: [numpy, harmonics, find_aspect_timing, dyn_coef, orb, mypy, numpydoc, gettext, i18n]

requires:
  - phase: 34-01
    provides: H{h}-{k} naming contract stable; api.po/api.mo already updated (no file-conflict)

provides:
  - find_aspect_timing with dyn_coef= param (3-branch orb resolution, explicit-orb-first)
  - TestFindAspectTimingF3 (5 tests: derive, cross-check formula, static-unchanged, precedence, raise)
  - api.md find_aspect_timing section (dyn_coef + explicit-orb-wins precedence + code examples)
  - api.po/api.mo FR translations for all 13 new msgids (no fuzzy)

affects:
  - 34-03 (F1 CLI — uses find_aspect_timing under the hood; naming contract already stable)
  - 35-release (all HARM-04/05 requirements satisfied)

tech-stack:
  added: []
  patterns:
    - "3-branch orb resolution: explicit orb first (short-circuit), dyn_coef derived, static table"
    - "Orb formula dyn_coef mirrors calculate_aspects:215-216 — single canonical formula"
    - "Explicit orb wins silently over dyn_coef — no ValueError on combined call (HARM-05 locked)"

key-files:
  created:
    - tests/test_find_aspect_timing_f3.py
  modified:
    - ketu/aspects/calculator.py
    - docs/source/api.md
    - docs/locale/fr/LC_MESSAGES/api.po
    - docs/locale/fr/LC_MESSAGES/api.mo

key-decisions:
  - "Explicit orb wins silently when both orb= and dyn_coef= given — no ValueError raised (HARM-05)"
  - "dyn_coef formula mirrors calculate_aspects lines 215-216 exactly: (orb_b1+orb_b2)/2*dyn_coef"
  - "3-branch block: orb-not-None first, dyn_coef-not-None second, static-table last (code encodes precedence)"

duration: 12min
completed: 2026-06-03
---

# Phase 34 Plan 02: ASP-F3 find_aspect_timing dyn_coef= Summary

**`find_aspect_timing` gets `dyn_coef: Optional[float] = None` with 3-branch orb resolution (explicit-orb-first, dynamic-derive, static-table), plus 5-test suite and en+fr docs — HARM-04/05 satisfied**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-06-03T22:25:00Z
- **Completed:** 2026-06-03T22:37:00Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Added `dyn_coef: Optional[float] = None` to `find_aspect_timing` with a 3-branch orb-resolution block that encodes the locked precedence in code order: explicit `orb` first (silent win), `dyn_coef`-derived second, static-table third
- Wrote `TestFindAspectTimingF3` (5 tests): covers the new branch, cross-checks the formula against `calculate_aspects`, verifies byte-identical static path, proves silent precedence (NOT ValueError), confirms off-table-raises preserved
- Documented `find_aspect_timing` in `api.md` with the parameter table, 3-branch resolution list, and code examples; translated all 13 new msgids to French in `api.po` (no fuzzy entries); recompiled `api.mo`
- mypy --strict clean, numpydoc lint passes, `core.py` untouched (V1/V13 sha256 fingerprints stable), 100% coverage on `ketu/aspects/calculator.py`

## Task Commits

1. **Task 1: Add dyn_coef to find_aspect_timing** - `cfd4bfe` (feat)
2. **Task 2: TestFindAspectTimingF3** - `c542f63` (test)
3. **Task 3: Document dyn_coef en + fr** - `b63f446` (docs)

**Plan metadata:** (see final commit below)

## Files Created/Modified

- `ketu/aspects/calculator.py` — `find_aspect_timing` signature + 3-branch orb block + updated docstring
- `tests/test_find_aspect_timing_f3.py` — TestFindAspectTimingF3 (5 tests, HARM-04/05)
- `docs/source/api.md` — new `find_aspect_timing` section with dyn_coef docs
- `docs/locale/fr/LC_MESSAGES/api.po` — 13 new msgids translated, fuzzy flags cleared
- `docs/locale/fr/LC_MESSAGES/api.mo` — recompiled

## Decisions Made

- Explicit `orb` wins silently when both `orb=` and `dyn_coef=` are given (no ValueError) — this was a locked decision from the roadmap (HARM-05), overriding the brief's §4-C "raise" recommendation
- Orb formula `(orb_b1 + orb_b2) / 2 * dyn_coef` mirrors `calculate_aspects` lines 215-216 exactly — single canonical formula, no divergence
- The 3-branch if/elif/else block ordering encodes the precedence in the code itself (self-documenting)

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## Next Phase Readiness

- HARM-04 and HARM-05 satisfied; `find_aspect_timing` is now fully capable of accepting dynamic orb coefficients
- Plan 34-03 (ASP-F1 CLI `--harmonics h7`) can proceed — it does not depend on the timing function, only on the naming contract (stable since 34-01)

---
*Phase: 34-harmonics-debt*
*Completed: 2026-06-03*
