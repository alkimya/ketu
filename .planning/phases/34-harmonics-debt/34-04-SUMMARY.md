---
phase: 34-harmonics-debt
plan: "04"
subsystem: testing, docs, cli
tags: [harmonics, h7, byte-stability, septile, cli, sphinx, gettext, fr-translation]

requires:
  - phase: 34-harmonics-debt/34-03
    provides: "--harmonics h7 end-to-end CLI producing correct H7-k output (Quadrinovile bug fixed)"

provides:
  - "harmonics_h7_reference_output.txt: pinned byte-stability fixture for --harmonics h7"
  - "TestHarmonicsH7ByteStable: 6-test sibling class enforcing h7 forward contract"
  - "--harmonics h7 CLI surface documented in concepts.md + api.md (Tight-grammar boundary, worked example)"
  - "concepts.po / api.po: full French translations with no English fallback"
  - "concepts.mo / api.mo: compiled binaries"
  - "HARM-08 + HARM-09 satisfied — F1 (ASP-F1) harmonics debt complete"

affects: [35-release-v1-5, kala-adapter]

tech-stack:
  added: []
  patterns:
    - "Ketu fixture ritual: generate → audit each expectation explicitly → pin (never blind regenerate)"
    - "Sibling test class pattern: additive TestHarmonicsH7ByteStable alongside existing TestV1_1ReferenceByteStable"
    - "Tight-grammar boundary documentation: table of supported vs. deferred forms (HARMF-01)"

key-files:
  created:
    - tests/cli/fixtures/harmonics_h7_reference_output.txt
  modified:
    - tests/cli/test_v1_1_reference_byte_stable.py
    - docs/source/concepts.md
    - docs/source/api.md
    - docs/locale/fr/LC_MESSAGES/concepts.po
    - docs/locale/fr/LC_MESSAGES/concepts.mo
    - docs/locale/fr/LC_MESSAGES/api.po
    - docs/locale/fr/LC_MESSAGES/api.mo

key-decisions:
  - "Fixture audited explicitly before pinning: H7-1/H7-2/H7-3 names confirmed, Quadrinovile=0, timing block byte-identical to v1.1, U+00BA degree symbol (20 occurrences), stderr header on stderr not stdout"
  - "TestHarmonicsH7ByteStable is purely additive: existing TestV1_1ReferenceByteStable class + v1_1_reference_output.txt are byte-identical (verified via md5sum)"
  - "MyST anchor (harmonics-h7-cli-new-in-v1-5) added to concepts.md for cross-reference from api.md"
  - "Tight-grammar boundary documented as table: h<N> alone supported; h7,h11 and traditional,h7 deferred to HARMF-01"

patterns-established:
  - "Byte-stability ritual: generate with 2>/tmp/h7.err, audit 5 criteria, pin — documented in SUMMARY audit findings"
  - "Sibling class: new harmonics get their own TestHarmonics{X}ByteStable class (additive-only, no modification of existing classes)"

duration: 8min
completed: 2026-06-03
---

# Phase 34 Plan 04: H7 Byte-Stability + Docs (F1) Summary

**`--harmonics h7` byte-stability fixture pinned (audited, not blind-regenerated) and CLI surface documented en + fr — HARM-08 + HARM-09 satisfied, F1 (ASP-F1) harmonics debt complete**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-06-03T20:50:34Z
- **Completed:** 2026-06-03T20:58:54Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- Fixture `harmonics_h7_reference_output.txt` generated and manually audited (5 criteria, all pass) before pinning
- `TestHarmonicsH7ByteStable` sibling class with 6 tests enforces the h7 forward contract; existing class + fixture byte-identical
- `concepts.md` gains a `--harmonics h7` subsection (syntax, semantics, Tight-grammar boundary table, worked example); `api.md` gains `parse_harmonics_spec` / `HarmonicsSelection` reference — both with MyST cross-link
- French PO files fully translated (no English fallback); `.mo` files recompiled via `make build-mo`
- Full suite: 1623 tests pass, 100% coverage, 0 pragma

## Audit Findings (Fixture Ritual)

Generated: `python -m ketu --harmonics h7 aspects --date 2000-01-01T12:00:00Z`

| Criterion | Result |
|---|---|
| H7-k names present (H7-1, H7-2, H7-3) | 6 rows found |
| Quadrinovile absent | 0 occurrences |
| Septile angles consistent (~51.43°/~102.86°/~154.29°) | Orbs match base angles |
| Timing block present and byte-identical to v1.1 | Identical (md5 diff confirmed) |
| Degree symbol U+00BA (not U+00B0) | 20 × `\xc2\xba`, 0 × `\xc2\xb0` |
| `# Aspect set: h7` on stderr (not stdout) | Confirmed via `grep /tmp/h7.err` |

## Task Commits

1. **Task 1: Generate + MANUALLY AUDIT the h7 fixture** — `e64cabe` (chore)
2. **Task 2: Add TestHarmonicsH7ByteStable sibling class** — `ee88b09` (test)
3. **Task 3: Document the --harmonics h7 CLI surface (en + fr)** — `0f20569` (docs)

## Files Created/Modified

- `tests/cli/fixtures/harmonics_h7_reference_output.txt` — pinned stdout of `--harmonics h7 aspects --date 2000-01-01T12:00:00Z`
- `tests/cli/test_v1_1_reference_byte_stable.py` — +156 lines additive: FIXTURE_H7, REFERENCE_ARGV_H7, TestHarmonicsH7ByteStable (6 tests)
- `docs/source/concepts.md` — `--harmonics h7` subsection with MyST anchor, Tight-grammar table, worked example
- `docs/source/api.md` — `parse_harmonics_spec` / `HarmonicsSelection` section with h<N> form, accepted specs table
- `docs/locale/fr/LC_MESSAGES/concepts.po` — +23 msgids fully translated
- `docs/locale/fr/LC_MESSAGES/concepts.mo` — recompiled
- `docs/locale/fr/LC_MESSAGES/api.po` — +21 msgids fully translated
- `docs/locale/fr/LC_MESSAGES/api.mo` — recompiled

## Decisions Made

- Fixture audited explicitly against 5 criteria before pinning (never blind regenerate — the ketu ritual)
- `TestHarmonicsH7ByteStable` is purely additive: existing `TestV1_1ReferenceByteStable` class and `v1_1_reference_output.txt` are byte-identical post-edit
- MyST anchor `(harmonics-h7-cli-new-in-v1-5)=` enables `{ref}` cross-link from api.md
- Tight-grammar boundary documented as a table (h<N> alone supported; mixing deferred to HARMF-01)
- FR translations complete with no English fallback for the new section

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## Next Phase Readiness

- HARM-08 (byte-stability fixture + test) and HARM-09 (CLI docs en + fr) satisfied
- F1 (ASP-F1) harmonics debt is complete; Phase 34 (Harmonics Debt) fully closed
- Ready for Phase 35: Release v1.5.0 (quality gates, version bump, PyPI OIDC, post-publish smoke)
- User checkpoint required before Phase 35 (per relecture-validation decision)

## Self-Check: PASSED

All required files exist on disk. All 3 task commits (`e64cabe`, `ee88b09`, `0f20569`) confirmed in git log.

---
*Phase: 34-harmonics-debt*
*Completed: 2026-06-03*
