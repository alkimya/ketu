---
phase: 41-documentation-release-v1-8-0
plan: "02"
subsystem: documentation
tags: [fr-translation, gettext, po, mo, changelog, name-clean, v1.8]
dependency_graph:
  requires: [41-01]
  provides: [DSPD-07-FR, D-01-FR, D-02-FR]
  affects:
    - docs/locale/fr/LC_MESSAGES/api.po
    - docs/locale/fr/LC_MESSAGES/api.mo
    - docs/locale/fr/LC_MESSAGES/concepts.po
    - docs/locale/fr/LC_MESSAGES/concepts.mo
    - docs/locale/fr/LC_MESSAGES/changelog.po
    - docs/locale/fr/LC_MESSAGES/changelog.mo
    - fr/CHANGELOG.md
tech_stack:
  added: []
  patterns: [sphinx-gettext, sphinx-intl-update, msgfmt-recompile, fr-translation]
key_files:
  created: []
  modified:
    - docs/locale/fr/LC_MESSAGES/api.po
    - docs/locale/fr/LC_MESSAGES/api.mo
    - docs/locale/fr/LC_MESSAGES/concepts.po
    - docs/locale/fr/LC_MESSAGES/concepts.mo
    - docs/locale/fr/LC_MESSAGES/changelog.po
    - docs/locale/fr/LC_MESSAGES/changelog.mo
    - fr/CHANGELOG.md
decisions:
  - "Merged main (Phase 40 + 41-01) into worktree via fast-forward before starting (worktree was forked from pre-41-01 base)"
  - "Ran sphinx-intl update to add new msgids, then translated all v1.8 entries"
  - "4 EN warnings / 5 FR warnings = same as main repo baseline after 41-01 (no new warnings)"
metrics:
  duration: "~70 min"
  completed: "2026-06-17"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 7
---

# Phase 41 Plan 02: FR Translations + .mo Recompile + Docs Build Summary

French translations for all v1.8 EN msgids (api.po/concepts.po/changelog.po); name-clean of all private-project references in FR catalogs and fr/CHANGELOG.md; .mo binaries recompiled; dated [1.8.0] FR changelog entry; EN+FR Sphinx builds at the baseline with zero new warnings.

## Tasks Completed

| Task | Name | Commit | Key Files |
|------|------|--------|-----------|
| 1 | Extract new EN strings, translate to French, name-clean FR catalogs (D-02/D-07) | de95e98 | docs/locale/fr/LC_MESSAGES/api.po, concepts.po, changelog.po |
| 2 | Add [1.8.0] FR changelog, recompile .mo, build EN+FR docs at the baseline (D-07) | f593740 | fr/CHANGELOG.md, docs/locale/fr/LC_MESSAGES/*.mo |

## What Was Done

### Task 1 — Extract new EN msgids, translate v1.8 surface, name-clean (D-02/D-07)

**sphinx-intl update:** ran `make gettext` + `sphinx-intl update -p build/gettext -l fr` to inject the new v1.8 msgids into the three FR catalogs. Results: `api.po +27`, `changelog.po +34`, `concepts.po +9`.

**api.po — v1.8 translations (14 entries):**
- `DECL_STANDSTILL_EPS — New in v1.8` heading
- Standstill-constant description paragraph (Value/Purpose/Scope)
- `is_ascending_declination_chart(chart) — New in v1.8` heading
- Comparison table (Function/Input/Output/Standstill columns)
- Table rows: `is_ascending_declination(jdate, body)` / scalar jd + body id / `bool` / no (> 0 only)
- Table rows: `is_ascending_declination_chart(chart)` / CHART_DTYPE array / `int8[14]` / yes (EPS gate)
- Chart-level helper description paragraph + parameter + returns
- `+1` / `-1` / `0` classification lines
- See also note

**concepts.po — v1.8 translations (6 entries):**
- Section heading `CHART_DTYPE — body_decl_speed field (New in v1.8)`
- Field introduction (index 8, `float64[14]`, after `body_decl`)
- Sign meaning (positive = northward / negative = southward, mirrors `body_speeds`)
- FD rationale (Δt = 0.01 day, package-wide idiom, no new API surface)
- Standstill contract (DECL_STANDSTILL_EPS, `is_ascending_declination_chart` int8 contract)
- Library design principle (Ketu owns astronomy; downstream consumers read fields)
- Additive dtype change note (positional/.view() must adapt)

**concepts.po — name-clean:**
- 1 hit: "consommateurs tels que Kala" → "consommateurs en aval" (in the v1.7 Notes msgstr)
- 1 hit: "impact Kala documenté" → "impact documenté" (in the body_decl msgstr)

**changelog.po — v1.8 translations (5 entries):**
- `[1.8.0] - 2026-06-17` version header
- `Added 1.8.0` section heading
- `body_decl_speed` field description (FD idiom, auto-populated by compute_chart + calculate_composite)
- `DECL_STANDSTILL_EPS = 0.001` constant description
- `is_ascending_declination_chart` helper description (int8 contract, DSPD-06)
- `Notes 1.8.0` section heading
- Notes paragraph (MINEURE, named-access safe, positional/.view() must adapt)

**changelog.po — name-clean:**
- 2 hits: "Impact Kala (additif, pas de rupture)" → "Impact en aval (additif, pas de rupture)" (v1.5 Notes msgstr, twice)

### Task 2 — [1.8.0] FR changelog entry, .mo recompile, EN+FR docs build (D-07)

**fr/CHANGELOG.md — [1.8.0] entry added above [1.7.0]:**
- Dated `## [1.8.0] - 2026-06-17`
- `### Ajouts` section with 3 items: body_decl_speed field, DECL_STANDSTILL_EPS, is_ascending_declination_chart
- `### Notes` section: MINEURE-pas-correctif, named-access safe, positional/.view() must adapt, link to UPGRADING.md

**fr/CHANGELOG.md — 4 legacy Kala hits name-cleaned:**
- Line 33 (v1.7 Notes): "Le code aval (Kala et tout oracle/instantané)" → "Les consommateurs en aval (tout oracle/instantané)"
- Line 138 (v1.5 Notes): "Impact Kala (additif, sans rupture)" → "Impact en aval (additif, sans rupture)"
- Line 209 (v1.3 Breaking): "RUPTURE (contrat positionnel Kala / en aval)" → "RUPTURE (contrat positionnel en aval)"
- Line 233 (v1.3 Breaking): "Les consommateurs en aval (ex. Kala) doivent" → "Les consommateurs en aval doivent"

**.mo recompile:**
All FR .mo binaries recompiled via `sphinx-intl build -d locale` from the worktree's `docs/` directory. Confirmed: api.mo / concepts.mo / changelog.mo all newer than their .po (no English fallback).

**Docs builds:**
- EN: 4 warnings (display_version + duplicate-label equatorial-declination + 2× UPGRADING xref_missing) — identical to main repo baseline after 41-01
- FR: 5 warnings (same as EN + one extra duplicate-label in opposite direction) — identical to main repo baseline after 41-01
- Zero new warnings introduced by plan 02

## Quality Gate Results

| Gate | Result |
|------|--------|
| `grep -l 'Kala\|...' concepts.po changelog.po` | 0 files (clean) |
| `grep -l 'Kala\|...' fr/CHANGELOG.md` | 0 files (clean) |
| `grep -q 'body_decl_speed' concepts.po` | PASS |
| `grep -q 'consommateurs en aval' concepts.po` | PASS (2 occurrences) |
| `grep -q '[1.8.0]' fr/CHANGELOG.md` | PASS |
| api.mo newer than api.po | PASS |
| concepts.mo newer than concepts.po | PASS |
| changelog.mo newer than changelog.po | PASS |
| `make html` (EN) | PASS — 4 warnings (baseline) |
| `make html SPHINXOPTS="-D language=fr"` (FR) | PASS — 5 warnings (baseline) |

## Deviations from Plan

### Auto-fixed Issues

**[Rule 3 - Blocking] Merged main into worktree before starting**

The worktree was forked from `7b200f6` (before Phase 40 and Phase 41-01 ran). The `body_decl_speed` symbols and EN documentation introduced by those phases were absent, making translation impossible. A `git merge main` (fast-forward, no conflicts, 44 files) was run to bring in the Phase 40 + Phase 41-01 commits before proceeding. No functional changes — structural prerequisite to translation work.

**[Cosmetic] Sphinx warning count is 4/5 (not 1)**

The plan references "the 1-warning baseline" — that was the pre-Phase-41-01 baseline. Phase 41-01 introduced two new UPGRADING xref_missing warnings and a duplicate-label warning. These exist in the main repo too. Plan 02 introduces zero new warnings, which satisfies the "no NEW warnings" acceptance criterion.

## Known Stubs

None. All translated content maps directly to implemented symbols (`body_decl_speed` at CHART_DTYPE[8], `DECL_STANDSTILL_EPS`, `is_ascending_declination_chart`) shipped in Phase 40.

## Threat Flags

None. This plan modifies only gettext translation strings (.po), compiled binary catalogs (.mo), and a static markdown file (fr/CHANGELOG.md). No runtime behavior, parsing, I/O, or user-controlled input introduced.

## Self-Check: PASSED

All modified files confirmed on disk. Task commits de95e98 and f593740 in git log.
