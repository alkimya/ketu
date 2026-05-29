---
phase: 25-documentation
plan: 01
subsystem: docs
tags: [sphinx, myst-parser, restructuredtext, numpy, ketu]

requires:
  - phase: 24-chiron
    provides: "Chiron body_id=13, CHART_DTYPE 14-body axis, D-08 breaking change"
  - phase: 22-ephemeris-refactor
    provides: "BODY_STRATEGIES dispatch, _elements.py, _perturbations.py extraction"
  - phase: 21-quality
    provides: "100% coverage gate, 56 doctests, mypy strict"

provides:
  - "12 docs/source/*.md pages updated from v1.0 to v1.3 surface"
  - "conf.py version/release = 1.3.0"
  - "index.md: Chiron in body table, 5 new toctree slots, corrected Quick Example"
  - "api.md: hand-written 11-section reference for all v1.3 subpackages with correct import paths"
  - "quickstart.md: zero broken ketu.<fn>() calls, compute_chart snippet"
  - "concepts.md: 14 bodies, house systems section, sect subsection"
  - "changelog.md: v1.1.0 / v1.2.0 / v1.3.0 sections"
  - "migration.md: v1.0→v1.1→v1.2→v1.3 upgrade guide, 13→14 breaking change D-08"
  - "English Sphinx build: 1 real warning (display_version, pre-existing)"

affects:
  - "25-02 (new pages — toctree slots already wired)"
  - "25-03 (clean build gate — baseline established)"
  - "26-release (changelog/migration reviewed, conf.py version 1.3.0)"

tech-stack:
  added: []
  patterns:
    - "All doc examples use submodule imports (from ketu.X import ...) not top-level ketu.<fn>()"
    - "Emoji literals moved to prose, not inside Python code-block strings"
    - "MyST cross-refs to not-yet-created pages produce myst.xref_missing (expected, fixed in 25-02)"
    - "Build via python3 -m sphinx.cmd.build (broken venv shebang workaround)"

key-files:
  created: []
  modified:
    - docs/source/conf.py
    - docs/source/index.md
    - docs/source/api.md
    - docs/source/quickstart.md
    - docs/source/installation.md
    - docs/source/concepts.md
    - docs/source/examples.md
    - docs/source/architecture.md
    - docs/source/changelog.md
    - docs/source/migration.md
    - docs/source/performance.md
    - docs/source/contributing.md
    - docs/source/acknowledgments.md

key-decisions:
  - "api.md is hand-written (no autodoc): each subpackage documented manually with correct import paths"
  - "myst.xref_missing warnings for 25-02 pages (houses.md, relational_charts.md, predictive_charts.md, arabic_parts.md, chiron.md) are expected in this plan's isolated build — treated as non-failures per plan spec"
  - "conf.py bumped to 1.3.0; ketu/__init__.py and pyproject.toml left at 1.2.0 (Phase 26 owns the package version bump)"
  - "migration.md UPGRADING.md/CHANGELOG.md cross-refs replaced with in-docs changelog.md link (eliminated myst.xref_missing warnings)"
  - "Emoji moved out of Python code-block strings in examples.md to eliminate Sphinx highlight warnings"

patterns-established:
  - "Standard example date: jd = 2451545.0 (J2000), lat=48.8566 lon=2.3522 (Paris)"
  - "Code examples use backtick python blocks (not >>> prompts) — display-only, not pytest-collected"

duration: 10min
completed: 2026-05-29
---

# Phase 25 Plan 01: Documentation Update Summary

**12 frozen Sphinx pages lifted from v1.0 to v1.3 surface: all broken `ketu.<fn>()` imports fixed, Chiron documented, 8 new subpackages in api.md, changelog/migration complete, English build at 1 real warning (pre-existing)**

## Performance

- **Duration:** 10 min
- **Started:** 2026-05-29T22:25:58Z
- **Completed:** 2026-05-29T22:36:00Z
- **Tasks:** 3
- **Files modified:** 13

## Accomplishments

- Fixed all broken `ketu.long()` / `ketu.utc_to_julian()` style examples across 5 source files — zero broken top-level calls remain
- Rewrote `api.md` with 11 sections (39 correct `from ketu.` imports) covering the entire v1.1/v1.2/v1.3 surface: configurable aspects, houses, charts, synastry, composite, returns, Arabic Parts, Chiron body_id=13
- Updated 7 narrative pages (changelog, migration, architecture, contributing, examples, performance, acknowledgments) to v1.3 — including the D-08 13→14 breaking-change note and elimination of broken UPGRADING.md cross-references

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix broken imports + bump version + wire toctree** - `b094875` (feat)
2. **Task 2: Rewrite api.md for full v1.3 subpackage surface** - `3581306` (feat)
3. **Task 3: Update narrative pages + verify clean English build** - `e5f372a` (feat)

## Files Created/Modified

- `docs/source/conf.py` — version/release bumped to 1.3.0
- `docs/source/index.md` — Chiron in body table, 5 toctree slots, fixed Quick Example, updated overview
- `docs/source/quickstart.md` — all imports corrected, compute_chart snippet added
- `docs/source/installation.md` — version 1.3.0, pip install ketu[dev]
- `docs/source/concepts.md` — 14 bodies (Chiron body_id=13), house systems section, sect section
- `docs/source/api.md` — complete rewrite: 11-section hand-written API reference for v1.3
- `docs/source/examples.md` — imports fixed, emoji out of code strings, new synastry + solar_return examples
- `docs/source/architecture.md` — v1.3 module tree (13 subpackages), BODY_STRATEGIES, pure-NumPy note
- `docs/source/changelog.md` — v1.3.0 / v1.2.0 / v1.1.0 sections added
- `docs/source/migration.md` — v1.0→v1.1→v1.2→v1.3 upgrade guide, D-08 breaking change, broken xrefs fixed
- `docs/source/performance.md` — all module paths corrected
- `docs/source/contributing.md` — v1.3 architecture tree, 100% coverage gate, quality gates table, pyswisseph policy
- `docs/source/acknowledgments.md` — v1.1/v1.2/v1.3 milestone mention

## Decisions Made

- `api.md` is hand-written (no autodoc): each of the 11 subpackage sections was authored manually with correct import paths verified against RESEARCH.
- `conf.py` bumped to `1.3.0`; `ketu/__init__.py` and `pyproject.toml` left untouched at `1.2.0` — Phase 26 owns the package version bump.
- `myst.xref_missing` warnings for the 5 not-yet-created pages (houses.md, relational_charts.md, predictive_charts.md, arabic_parts.md, chiron.md) are expected and treated as non-failures per plan spec (Phase 25-02 creates those pages).
- Broken `UPGRADING.md` / `CHANGELOG.md` external cross-refs in `migration.md` replaced with in-tree `changelog.md` links — eliminates myst.xref_missing warnings that existed in the fr build baseline.
- Emoji moved from Python string literals in `examples.md` to surrounding prose — eliminates Sphinx highlight warnings.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

The build verification grep pattern in the plan used `"toctree"` to filter expected warnings, but the French-locale Sphinx produces `toc.not_readable` (not `"toctree"`) for missing-page warnings. Added `toc.not_readable` to the filter. Final count: 1 real warning (display_version, pre-existing), exactly as required.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Toctree slots for 5 new pages are wired in `index.md` — 25-02 can create them without touching `index.md`
- English build baseline: 1 real warning (display_version)
- All existing page content is at v1.3 surface — 25-02 new pages can cross-link freely
- 25-03 gettext pipeline ready to run after 25-02 pages exist

---
*Phase: 25-documentation*
*Completed: 2026-05-29*
