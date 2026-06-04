---
phase: 37-documentation-release-v1-6-0
plan: 01
subsystem: docs
tags: [sphinx, myst, i18n, gettext, declination-aspects, fr-translation]

# Dependency graph
requires:
  - phase: 36-declination-aspects-detection
    provides: ketu.declination subpackage (find_declination_aspects, DECLA_ASPECT_DTYPE, DECLA_COEF, MIN_DECL_ORB)
provides:
  - EN concepts.md "Declination Aspects — New in v1.6" feature section (5 DECLA-05 items)
  - EN api.md "Declination Aspects (ketu.declination) — New in v1.6" reference section
  - FR translations (concepts.po + api.po) for every new declination-aspects msgid
  - Recompiled concepts.mo + api.mo so FR docs render without English fallback
affects: [37-02, 37-03, ReadTheDocs v1.6 docs]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "MyST explicit-label cross-doc links use [text](#label) (bare hash), not [text](file.md#label) — clears myst.xref_missing in both EN and FR builds"

key-files:
  created:
    - .planning/phases/37-documentation-release-v1-6-0/37-01-SUMMARY.md
  modified:
    - docs/source/concepts.md
    - docs/source/api.md
    - docs/locale/fr/LC_MESSAGES/concepts.po
    - docs/locale/fr/LC_MESSAGES/api.po
    - docs/locale/fr/LC_MESSAGES/concepts.mo
    - docs/locale/fr/LC_MESSAGES/api.mo

key-decisions:
  - "Committed recompiled .mo files (concepts.mo, api.mo) — DEVIATION from the plan's premise that the repo commits zero .mo. Git history (5365c21, cdb72cd, fad7f64) shows .mo ARE tracked and recompiled every docs phase; .po-without-.mo would ship stale FR docs (English fallback), violating LOCKED project_fr_translations_before_release."
  - "Switched the two api.md concepts cross-links from concepts.md#anchor to the MyST explicit-label form #declination-aspects-new-in-v1-6 to clear the xref_missing warning the plan's clean-build verify required."
  - "Fixed multiple wrong sphinx-intl fuzzy auto-fills (the v1.6 heading seeded with the v1.5 string; '1.0°'→'10°'; 'Sun / Moon'→'Soleil, Lune'; 'DECLA_ASPECT_DTYPE'→'CHART_DTYPE'; 'orb_pairs'→'PARTS') that would have published mistranslations."
  - "Reverted changelog.po churn (stale POT-date refresh + pre-existing v1.5 fuzzy drift) — out of plan 37-01 scope (37-02 owns changelog)."

patterns-established:
  - "Table cells containing literal pipes (|δ₁−δ₂|) must escape them as \\|...\\| in GFM tables or MD056 breaks the column count."

requirements-completed: [DECLA-05]

# Metrics
duration: ~40min
completed: 2026-06-04
---

# Phase 37: Documentation & Release v1.6.0 — Plan 01 Summary

**Authored the complete v1.6 declination-aspects feature documentation in English and French — concepts prose + API reference + verified FR .mo recompile, no English fallback.**

## Performance

- **Duration:** ~40 min (initial worktree executor blocked on Bash permission at ~30%; finished inline by orchestrator)
- **Completed:** 2026-06-04
- **Tasks:** 3/3
- **Files modified:** 6 (2 source .md, 2 .po, 2 .mo)

## Accomplishments

### Task 1 — EN concepts.md section (commit 4ac05e4)
New `## Declination Aspects — New in v1.6` section (with explicit MyST label
`(declination-aspects-new-in-v1-6)=`) covering all five DECLA-05 items:
signed-δ parallel/contra-parallel definitions with the strict same-hemisphere
rule, the body-derived orb formula with the worked Sun/Moon = 1.0° example
(+ orb table), biodynamic framing (parallel ≈ conjunction / contra-parallel ≈
opposition on δ), the explicit parallel ≠ longitude-conjunction distinction, and
the `//` / `#` symbols with `P` / `CP` abbreviations. Plus the zero-sign trap and
OOB-interaction note, and a runnable `find_declination_aspects` example. The v1.5
Equatorial Declination section is intact.

### Task 2 — EN api.md reference (commit 4f34df9)
New `## Declination Aspects (ketu.declination) — New in v1.6` section documenting
`find_declination_aspects` (with the `np.empty(0)` empty-result contract),
`declination_aspect_masks`, `DeclinationAspectMasks` (6 fields),
`DECLA_ASPECT_DTYPE` (5 fields; `body1`/`body2` = `i1`, verified against the live
dtype), `DECLA_COEF` (1/12), `MIN_DECL_ORB` (0.5). Uses the correct
`from ketu.declination import` path (names NOT re-exported from top-level `ketu`).
Caught and fixed an MD056 table break from unescaped `|` pipes in `|δ₁−δ₂|` cells.

### Task 3 — FR translation + .mo recompile (commit ac7b295)
Ran `make gettext` + `make update-po`, translated every new declination-aspects
msgid in concepts.po and api.po, fixed several dangerous sphinx-intl fuzzy
auto-fills, and recompiled concepts.mo + api.mo. `make html` and `make html-fr`
both build with no declination xref/fuzzy warnings; the rendered FR pages contain
« contre-parallèle » (verified the .mo compile path end-to-end).

## Deviations

1. **`.mo` committed (plan premise was wrong).** The plan stated the repo commits
   zero `.mo` and to treat them as build artifacts. Git history disproves this —
   `.mo` are tracked and recompiled every docs phase. Committing `.po` without the
   matching `.mo` would leave published FR docs falling back to English, violating
   LOCKED `project_fr_translations_before_release`. Followed the repo convention.
2. **api.md cross-link form changed.** Used `[text](#declination-aspects-new-in-v1-6)`
   (MyST explicit-label) instead of `concepts.md#...` to satisfy the plan's
   no-xref-warning verify in both builds. Folded into the Task 3 commit since it
   was part of the i18n correctness work.
3. **changelog.po reverted** — out of 37-01 scope (owned by 37-02).

## Verification

- `grep` checks for all Task 1 + Task 2 verify criteria: PASS
- `make html` / `make html-fr`: build successfully, no declination `xref_missing`
  or fuzzy warnings on the new strings
- FR `.mo` content confirmed: `concepts.mo` → "Parallèle et contre-parallèle",
  `api.mo` → "Détecteur scalaire / thème unique."
- `pytest tests/ -q`: 1654 passed, 2 skipped, 100% coverage (unchanged — docs-only)
- No `ketu/` source, version, or changelog files touched by this plan
