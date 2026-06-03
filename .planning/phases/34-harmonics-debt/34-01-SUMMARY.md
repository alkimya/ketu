---
phase: 34-harmonics-debt
plan: 01
subsystem: aspects
tags: [harmonics, naming-contract, documentation, testing, i18n, numpydoc]

requires:
  - phase: 28-dynamic-harmonics
    provides: generate_harmonic_aspects with correct H{h}-{k} naming (already implemented)

provides:
  - TestNamingContractF2 pinning class (5 tests, h7/h2/even-h/all-h/collision)
  - generate_harmonic_aspects "Public API contract" paragraph in docstring
  - Two-channel GENERATOR vs DETECTION distinction in concepts.md + api.md
  - Traditional-name reference table (quintile/septile/novile) in concepts.md
  - FR translations for all new doc paragraphs (concepts.po/mo + api.po/mo)

affects:
  - 34-02 (ASP-F3 timing orb — depends on naming contract being stable)
  - 34-03 (ASP-F1 CLI --harmonics — depends on F2 contract)
  - 35-release-v15

tech-stack:
  added: []
  patterns:
    - "Two-channel naming: GENERATOR always H{h}-{k}, DETECTION prefers static table name on collision"
    - "MyST {ref} role for cross-file anchor references"
    - "TestNamingContractF2 pattern: regex sweep over all h in [2..64] for full contract coverage"

key-files:
  created: []
  modified:
    - tests/test_dynamic_harmonics.py
    - ketu/aspects/harmonics.py
    - docs/source/concepts.md
    - docs/source/api.md
    - docs/locale/fr/LC_MESSAGES/concepts.po
    - docs/locale/fr/LC_MESSAGES/concepts.mo
    - docs/locale/fr/LC_MESSAGES/api.po
    - docs/locale/fr/LC_MESSAGES/api.mo

key-decisions:
  - "Generator naming ALWAYS b'H{h}-{k}': no traditional-name substitution ever — locked decision, not reopened"
  - "Detection channel static-first: 120° always Trine (i_asp=9), not H3-1 (i_asp=-2)"
  - "Cross-file MyST anchor reference uses {ref} role, not path-based concepts.md#anchor"
  - "Table style in concepts.md: no-leading-pipe to match pre-existing conventions"

patterns-established:
  - "Explicit MyST target (anchor-name)= placed directly before heading for cross-file {ref} links"

duration: 15min
completed: 2026-06-03
---

# Phase 34 Plan 01: Naming Contract F2 Summary

**H{h}-{k} generator naming pinned as public API contract: 5-test class covers h=2..64 regex sweep + collision static-first semantics; docstring promoted; two-channel distinction + traditional-name table documented in en+fr**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-06-03T20:17:17Z
- **Completed:** 2026-06-03T20:40Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- `TestNamingContractF2` (5 tests) pins the H{h}-{k} contract for h=7 exact, h=2 boundary, even-h last-row-180°, all h in [2..64] via regex sweep, and collision semantics (120° → Trine i_asp=9, not H3-1 i_asp=-2)
- `generate_harmonic_aspects` docstring gains an explicit "Public API contract (frozen, v1.5+)" paragraph — numpydoc lint, interrogate 100%, mypy --strict, doctests all pass
- `concepts.md` gains `(synthetic-harmonic-naming)=` subsection with GENERATOR/DETECTION channel distinction and traditional-name reference table (quintile, septile, novile, biquintile, binovile, quadnovile)
- `api.md` gains Naming contract note cross-referencing the concepts section via `{ref}` MyST role (no Sphinx xref_missing warning)
- FR translations complete for all 14 new concepts.po msgids and 1 api.po msgid; both .mo recompiled; html-fr build clean

## Task Commits

1. **Task 1: Pin the H{h}-{k} naming contract with TestNamingContractF2** — `3d06108` (test)
2. **Task 2: Promote the naming contract to the generator docstring** — `12b22b3` (docs)
3. **Task 3: Document two-channel distinction + traditional-name table (en + fr)** — `ec2d412` (docs)

## Files Created/Modified

- `tests/test_dynamic_harmonics.py` — Added `TestNamingContractF2` class with 5 pinning tests (118 lines)
- `ketu/aspects/harmonics.py` — Added "Public API contract" paragraph to `generate_harmonic_aspects` Notes section (docstring-only)
- `docs/source/concepts.md` — Added `(synthetic-harmonic-naming)=` subsection with two-channel distinction and traditional-name table
- `docs/source/api.md` — Added Naming contract note to `generate_harmonic_aspects(h)` section
- `docs/locale/fr/LC_MESSAGES/concepts.po` — 14 new msgids translated (FR)
- `docs/locale/fr/LC_MESSAGES/concepts.mo` — Recompiled
- `docs/locale/fr/LC_MESSAGES/api.po` — 1 new msgid translated (FR)
- `docs/locale/fr/LC_MESSAGES/api.mo` — Recompiled

## Decisions Made

- Generator naming is ALWAYS `b'H{h}-{k}'` (locked decision, not reopened per plan).
- Detection channel is static-first: a 120° collision is Trine (i_asp=9), never H3-1 (i_asp=-2).
- Cross-file MyST anchor reference uses `{ref}` role (not path-based `concepts.md#anchor`) — the path-based form triggers `myst.xref_missing` even in HTML builds.
- Table style uses no-leading-pipe format to match pre-existing conventions in concepts.md.

## Deviations from Plan

None — plan executed exactly as written. No executable code changed (generator behaviour was already correct). The only deviation was choosing `{ref}` role over the path-based link specified in the plan, which was necessary to avoid a Sphinx build warning.

## Issues Encountered

- MyST cross-file path links (`concepts.md#anchor`) don't resolve MyST explicit target names during Sphinx build — triggers `myst.xref_missing`. Fixed by switching to `{ref}` role, which is the idiomatic MyST/Sphinx approach.
- Linter false-positive MD022 for MyST anchor lines (pre-existing pattern — same warning existed for `(equatorial-declination-new-in-v1-5)=` before this plan).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- HARM-01, HARM-02, HARM-03 satisfied.
- Plan 34-02 (ASP-F3: `find_aspect_timing` `dyn_coef=` orb derivation) can proceed.
- core.aspects V1/V13 sha256 fingerprints unchanged (no core.py modification).
- Full suite: 1593 tests pass, 100% coverage, all gates green.

---
*Phase: 34-harmonics-debt*
*Completed: 2026-06-03*
