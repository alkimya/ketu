---
phase: 25-documentation
plan: 03
subsystem: docs
tags: [sphinx, gettext, sphinx-intl, i18n, po-files, mo-files, french-translation]

requires:
  - phase: 25-01
    provides: "12 existing docs pages updated to v1.3 surface — final English source for gettext"
  - phase: 25-02
    provides: "5 new docs pages (houses, relational_charts, predictive_charts, arabic_parts, chiron) — new .pot targets"

provides:
  - "docs/locale/fr/LC_MESSAGES/houses.po: new French catalog (English-fallback, pipeline-created)"
  - "docs/locale/fr/LC_MESSAGES/relational_charts.po: new French catalog (English-fallback)"
  - "docs/locale/fr/LC_MESSAGES/predictive_charts.po: new French catalog (English-fallback)"
  - "docs/locale/fr/LC_MESSAGES/arabic_parts.po: new French catalog (English-fallback)"
  - "docs/locale/fr/LC_MESSAGES/chiron.po: new French catalog (English-fallback)"
  - "All 17 .po catalogs refreshed from final v1.3 source via gettext pipeline"
  - "Zero dangling #, fuzzy entries in any .po file (122 resolved)"
  - "17 compiled .mo files (all non-empty)"
  - "English build: 1 warning (display_version, pre-existing)"
  - "French build: 1 warning (display_version, pre-existing) — better than ≤5 target"
  - "DOC-12 satisfied"

affects:
  - "26-release (fr docs build clean, no i18n blockers for release)"

tech-stack:
  added: []
  patterns:
    - "gettext pipeline via python3 -m invocations only (broken venv shebang workaround)"
    - "New pages get English-fallback .po catalogs via sphinx-intl update (no manual creation)"
    - "Fuzzy resolution policy: all fuzzy → msgstr '' (English fallback) + remove flag (per DOC-12 decision)"
    - ".mo files compiled via python3 -c 'from sphinx_intl.commands import main; ...'"

key-files:
  created:
    - docs/locale/fr/LC_MESSAGES/houses.po
    - docs/locale/fr/LC_MESSAGES/relational_charts.po
    - docs/locale/fr/LC_MESSAGES/predictive_charts.po
    - docs/locale/fr/LC_MESSAGES/arabic_parts.po
    - docs/locale/fr/LC_MESSAGES/chiron.po
    - docs/locale/fr/LC_MESSAGES/houses.mo
    - docs/locale/fr/LC_MESSAGES/relational_charts.mo
    - docs/locale/fr/LC_MESSAGES/predictive_charts.mo
    - docs/locale/fr/LC_MESSAGES/arabic_parts.mo
    - docs/locale/fr/LC_MESSAGES/chiron.mo
  modified:
    - docs/locale/fr/LC_MESSAGES/api.po
    - docs/locale/fr/LC_MESSAGES/architecture.po
    - docs/locale/fr/LC_MESSAGES/concepts.po
    - docs/locale/fr/LC_MESSAGES/changelog.po
    - docs/locale/fr/LC_MESSAGES/migration.po
    - docs/locale/fr/LC_MESSAGES/contributing.po
    - docs/locale/fr/LC_MESSAGES/index.po
    - docs/locale/fr/LC_MESSAGES/acknowledgments.po
    - docs/locale/fr/LC_MESSAGES/examples.po
    - docs/locale/fr/LC_MESSAGES/quickstart.po
    - docs/locale/fr/LC_MESSAGES/installation.po
    - docs/locale/fr/LC_MESSAGES/performance.po
    - docs/locale/fr/LC_MESSAGES/installation.mo
    - docs/locale/fr/LC_MESSAGES/performance.mo
    - "(and all other 12 .mo files recompiled)"

key-decisions:
  - "New pages (.po catalogs) left with English-fallback (empty msgstr) — per recorded DOC-12 decision; substantive French translation deferred"
  - "All 122 fuzzy entries resolved via English fallback (msgstr '') + flag removal — no stale French text ships"
  - "Markdown heading markers (#, ##, ###) in msgstr fields are a pre-existing bug that cause myst.header warnings; stripped from performance.po and installation.po (Rule 1)"
  - "French build achieves 1 warning (better than ≤5 target) — only pre-existing display_version remains"

duration: 4min
completed: 2026-05-29
---

# Phase 25 Plan 03: French Translation Pipeline Summary

**gettext pipeline regenerated from final v1.3 source: 5 new .po catalogs created, 122 fuzzy entries resolved, 17 .mo files compiled, fr build at 1 warning (equal to the English baseline)**

## Performance

- **Duration:** 4 min
- **Started:** 2026-05-29T22:44:29Z
- **Completed:** 2026-05-29T22:49:22Z
- **Tasks:** 2
- **Files modified:** 27 (17 .po + 10 .mo)

## Accomplishments

- Ran `python3 -m sphinx.cmd.build -b gettext` → 17 .pot files extracted from final v1.3 English source (all 12 existing + 5 new pages from 25-02)
- Ran `sphinx-intl update` → 5 new .po files auto-created (houses, relational_charts, predictive_charts, arabic_parts, chiron) with English-fallback; 12 existing .po files refreshed
- Resolved all 122 `#, fuzzy` entries across 14 .po files: api.po(35), architecture.po(30), concepts.po(16), changelog.po(14), contributing.po(8), migration.po(8), index.po(3), acknowledgments.po(2), plus 1 each in 6 others — zero dangling fuzzy entries ship
- Auto-fixed pre-existing bug: Markdown heading markers (`#`, `##`, `###`) embedded in msgstr fields of `performance.po` and `installation.po` were causing 18 new `myst.header` warnings in the fr build; stripped all markers
- Compiled 17 .mo files; English build: 1 warning; French build: 1 warning (DOC-12 gate passed)

## Task Commits

Each task was committed atomically:

1. **Task 1: Extract POT + update fr .po catalogs** - `f52fecf` (feat)
2. **Task 2: Resolve fuzzy entries, compile .mo, verify builds** - `a9ff166` (feat)

**Plan metadata:** see below (docs commit)

## Files Created/Modified

**New .po files (English-fallback):**
- `docs/locale/fr/LC_MESSAGES/houses.po` — French catalog for house systems page
- `docs/locale/fr/LC_MESSAGES/relational_charts.po` — French catalog for relational charts page
- `docs/locale/fr/LC_MESSAGES/predictive_charts.po` — French catalog for predictive charts page
- `docs/locale/fr/LC_MESSAGES/arabic_parts.po` — French catalog for Arabic Parts page
- `docs/locale/fr/LC_MESSAGES/chiron.po` — French catalog for Chiron page

**Updated .po files (12 existing, refreshed from v1.3 source):**
- `docs/locale/fr/LC_MESSAGES/api.po` — 35 fuzzy resolved; 171 new msgids from v1.3 rewrite
- `docs/locale/fr/LC_MESSAGES/architecture.po` — 30 fuzzy resolved
- `docs/locale/fr/LC_MESSAGES/concepts.po` — 16 fuzzy resolved (Chiron, house systems, sect)
- `docs/locale/fr/LC_MESSAGES/changelog.po` — 14 fuzzy resolved (v1.1/1.2/1.3 entries)
- `docs/locale/fr/LC_MESSAGES/migration.po` — 8 fuzzy resolved (v1.0→v1.3 upgrade guide)
- `docs/locale/fr/LC_MESSAGES/contributing.po` — 8 fuzzy resolved
- `docs/locale/fr/LC_MESSAGES/installation.po` — 1 fuzzy resolved + heading markers stripped
- `docs/locale/fr/LC_MESSAGES/performance.po` — 0 fuzzy + heading markers stripped
- (+ examples, quickstart, index, acknowledgments — refreshed)

**Compiled .mo files:** all 17 (5 new + 12 existing recompiled)

## Decisions Made

- All fuzzy entries resolved with English fallback (empty msgstr) per the DOC-12 recorded decision — correctness over partial French coverage; no stale translations ship
- New pages left with English-fallback msgstr — substantive French translation deferred to a future volunteer/phase; fr build renders English for those pages (acceptable behavior, verified)
- `conf.py` version, `ketu/__init__.py`, and `pyproject.toml` left as-is — Phase 26 owns the package version bump

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Stripped Markdown heading markers from msgstr in performance.po and installation.po**
- **Found during:** Task 2 (fr build verification)
- **Issue:** `performance.po` contained msgstr values with `# `, `## `, `### ` prefixes (e.g., `msgstr "# Guide de Performance"`, `msgstr "## Benchmarks"`). `installation.po` had `msgstr "## Installation depuis les sources"`. These caused 18 new `myst.header` warnings in the fr build (`WARNING: Document headings start at H2/H3, not H1`), pushing the fr warning count to 19 (target: ≤5).
- **Fix:** Stripped all `#`, `##`, `###` heading prefixes from active msgstr fields in both files. Obsolete entries (`#~ msgstr "..."`) left untouched (they are not rendered).
- **Files modified:** `docs/locale/fr/LC_MESSAGES/performance.po`, `docs/locale/fr/LC_MESSAGES/installation.po`
- **Verification:** Rebuilt fr HTML → 1 warning (display_version only). Heading markers: zero remaining in active msgstr fields.
- **Committed in:** `a9ff166` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 Rule 1 bug)
**Impact on plan:** Fix required to meet the ≤5 warning gate; no scope creep; pre-existing catalog bug from original v1.0 translation.

## Issues Encountered

None beyond the auto-fixed heading-marker bug above.

## User Setup Required

None — no external service configuration required. The gettext pipeline is fully automated.

## Next Phase Readiness

- DOC-12 satisfied: pipeline regenerated, catalogs updated, both builds clean
- Phase 25 complete: DOC-10 (existing pages), DOC-11 (new pages), DOC-12 (fr pipeline) all satisfied
- Phase 26 (Release 1.3.0) can proceed: docs are at v1.3 surface, fr build is clean, no i18n blockers
- Future French translation volunteers can pick up the new pages' .po files (houses, relational_charts, predictive_charts, arabic_parts, chiron) — all have correct msgids from the v1.3 source

---
*Phase: 25-documentation*
*Completed: 2026-05-29*
