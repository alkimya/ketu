---
phase: 33-lunar-declination
plan: 04
subsystem: docs
tags: [declination, documentation, sphinx, i18n, fr, po, concepts, api, changelog]

# Dependency graph
requires:
  - phase: 33-lunar-declination/33-01
    provides: 4 public declination functions in ketu.calculations (declination, declination_velocity, is_ascending_declination, is_out_of_bounds)
  - phase: 33-lunar-declination/33-02
    provides: body_decl field in CHART_DTYPE
  - phase: 33-lunar-declination/33-03
    provides: composite body_decl via coordinates chain

provides:
  - DECL-09: declination documented en + fr (api.md + concepts.md + changelog.md)
  - 4 functions documented in is_retrograde style in api.md
  - β-vs-δ pitfall explicit in both api.md (Equatorial Declination section) and concepts.md
  - montant/descendant biodynamic framing (~27.21d draconic cycle) in concepts.md
  - OOB nodal cycle (~18.6y) explained in concepts.md
  - v1.5 changelog entry with additive body_decl dtype note + Kala impact
  - FR api.po + concepts.po fully translated (no English-fallback for declination msgids)
  - FR changelog.po translated for v1.5 entry
  - .mo files recompiled; html-fr build renders "déclinaison"

affects:
  - 34-harmonics-debt (Phase 34 docs pattern)
  - 35-release-v15 (docs are release-ready for v1.5.0)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "EN source → make gettext → make update-po → manual msgstr fill → make build-mo → html-fr verify"
    - "MyST anchor (equatorial-declination-new-in-v1-5)= for cross-references between api.md sections"

key-files:
  created: []
  modified:
    - docs/source/api.md
    - docs/source/concepts.md
    - docs/source/changelog.md
    - docs/locale/fr/LC_MESSAGES/api.po
    - docs/locale/fr/LC_MESSAGES/api.mo
    - docs/locale/fr/LC_MESSAGES/concepts.po
    - docs/locale/fr/LC_MESSAGES/concepts.mo
    - docs/locale/fr/LC_MESSAGES/changelog.po
    - docs/locale/fr/LC_MESSAGES/changelog.mo

key-decisions:
  - "Equatorial Declination section added as a dedicated ## section in api.md (with MyST anchor) so function-level cross-links resolve"
  - "is_ascending(jday,body) documented explicitly in api.md to make β-vs-δ distinction discoverable at the function level"
  - "changelog.po fuzzy matches cleaned (v1.5 entry uses fresh msgstr, not fuzzy-inherited from 1.4)"

patterns-established:
  - "New feature docs: add standalone section with MyST anchor + document individual functions in Calculations section"
  - "FR .po workflow: gettext → update-po → fill msgstr → build-mo → html-fr smoke check grep 'déclinaison'"

# Metrics
duration: 7min
completed: 2026-06-03
---

# Phase 33 Plan 04: Documentation (EN + FR) Summary

**4 declination functions + β-vs-δ pitfall + biodynamic montant/descendant + OOB documented in api.md/concepts.md/changelog.md; FR .po fully translated and .mo recompiled (no English-fallback)**

## Performance

- **Duration:** 7 min
- **Started:** 2026-06-03T20:02:27Z
- **Completed:** 2026-06-03T20:09:47Z
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments

- EN docs: `api.md` documents `declination`, `declination_velocity`, `is_ascending_declination`, `is_out_of_bounds` in `is_retrograde` style; added dedicated Equatorial Declination section (MyST anchor) with β-vs-δ pitfall table, montant/descendant explanation, OOB nodal cycle
- EN docs: `concepts.md` has full Equatorial Declination section — δ vs β distinction, 27.21-day draconic cycle, OOB ~18.6y major standstill, body_decl additive CHART_DTYPE field
- EN docs: `changelog.md` has v1.5.0 entry covering all 4 functions + additive `body_decl` dtype bump + Kala additive-only impact note + `is_ascending` β unchanged
- FR: `api.po`, `concepts.po`, `changelog.po` fully translated (27 + 35 + 12 new msgids); `.mo` recompiled; html-fr renders "déclinaison" in all 3 pages
- Both `make html` and `make html-fr` build clean (2 pre-existing warnings only)

## Task Commits

1. **Task 1: EN docs — api.md + concepts.md + changelog.md** — `9b4b6e6` (docs)
2. **Task 2: FR translations — api.po/concepts.po/changelog.po + .mo recompiled** — `38ceb61` (docs)

**Plan metadata:** (this commit)

## Files Created/Modified

- `docs/source/api.md` — Added `is_ascending`, 4 declination functions (is_retrograde style), Equatorial Declination section with β-vs-δ table + montant/OOB prose
- `docs/source/concepts.md` — Added Equatorial Declination section (δ-vs-β, montant/descendant ~27.21d, OOB ~18.6y, body_decl CHART_DTYPE)
- `docs/source/changelog.md` — Added v1.5.0 entry (4 functions + additive body_decl + Kala note + is_ascending unchanged)
- `docs/locale/fr/LC_MESSAGES/api.po` — 35 new msgids translated (declination functions + section)
- `docs/locale/fr/LC_MESSAGES/api.mo` — recompiled
- `docs/locale/fr/LC_MESSAGES/concepts.po` — 27 new msgids translated (full Equatorial Declination section)
- `docs/locale/fr/LC_MESSAGES/concepts.mo` — recompiled
- `docs/locale/fr/LC_MESSAGES/changelog.po` — 12 new msgids translated (v1.5 entry)
- `docs/locale/fr/LC_MESSAGES/changelog.mo` — recompiled

## Decisions Made

- **MyST anchor on Equatorial Declination section**: added `(equatorial-declination-new-in-v1-5)=` above the `## Equatorial Declination` section in api.md so that function-level cross-links (`[Equatorial Declination (New in v1.5)](#equatorial-declination-new-in-v1-5)`) resolve at build time.
- **Explicit `is_ascending` doc in api.md**: documented `is_ascending(jday, body)` with a note that it is the β-trajectory helper and cross-references `is_ascending_declination` — making the β-vs-δ distinction discoverable at the function level, not only in the concepts section.
- **changelog.po fuzzy cleanup**: the `Added 1.5.0` msgid had a fuzzy match against `Added 1.4.0`; replaced with a clean, non-fuzzy translation.

## Deviations from Plan

None — plan executed exactly as written. The only discovery was that sphinx-intl inserted some duplicated entries due to line-number collisions with manually pre-translated msgids; these were cleaned up during the translation pass.

## Issues Encountered

None. Both EN and FR builds were clean on first run. The `update-po` step correctly identified 3 changed files (+35, +27, +12 msgids) matching the scope of the new content.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- DECL-09 satisfied: declination documented en + fr, 4 public functions, aspect-centric montant/descendant framing, β-vs-δ distinction explicit, FR translated + recompiled
- Phase 33 fully complete (Plans 01–04 done): foundation → chart wiring → composite wiring → docs en+fr
- Ready for Phase 34 (Harmonics Debt: ASP-F2 → ASP-F3 → ASP-F1) and eventually Phase 35 (Release v1.5.0)

---
*Phase: 33-lunar-declination*
*Completed: 2026-06-03*
