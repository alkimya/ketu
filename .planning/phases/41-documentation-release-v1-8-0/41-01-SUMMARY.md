---
phase: 41-documentation-release-v1-8-0
plan: "01"
subsystem: documentation
tags: [docs, name-clean, changelog, api, concepts, upgrading, v1.8]
dependency_graph:
  requires: [40-03]
  provides: [DSPD-07-EN, D-01, D-02, D-03, D-04, D-05, D-06]
  affects: [docs/source/api.md, docs/source/concepts.md, CHANGELOG.md, UPGRADING.md, docs/source/changelog.md, ketu/]
tech_stack:
  added: []
  patterns: [name-clean-sweep, EN-first-docs, numpydoc-autodoc, changelog-keep-format]
key_files:
  created: []
  modified:
    - ketu/synastry/__init__.py
    - ketu/synastry/core.py
    - ketu/aspects/calculator.py
    - ketu/houses/core.py
    - ketu/charts/core.py
    - CHANGELOG.md
    - docs/source/changelog.md
    - UPGRADING.md
    - docs/source/api.md
    - docs/source/concepts.md
decisions:
  - "Generic 'downstream consumers' phrasing in all public artifacts — no private-project names (D-01)"
  - "Full legacy sweep including already-published changelog entries (D-02)"
  - "Docstring name-clean required because autodoc/numpydoc renders them into public API docs (D-03)"
  - "body_decl_speed documented at same depth as body_decl precedent in v1.5 (D-04)"
  - "Runnable example in api.md + concepts.md reading body_decl_speed / calling helper (D-05)"
  - "UPGRADING v1.7->v1.8 entry: generic phrasing, verify snippet, newest-first order (D-06)"
metrics:
  duration: "~35 min"
  completed: "2026-06-17"
  tasks_completed: 3
  tasks_total: 3
  files_modified: 10
---

# Phase 41 Plan 01: EN Documentation + Name-Clean Summary

EN documentation of the v1.8 declination-speed surface plus full name-clean sweep of all shipped/rendered artifacts. Zero private-project names remain; `body_decl_speed`, `DECL_STANDSTILL_EPS`, and `is_ascending_declination_chart` are fully documented in English; the dated `[1.8.0]` changelog and generic `v1.7 → v1.8` UPGRADING entry are in place; all six quality gates remain green.

## Tasks Completed

| Task | Name | Commit | Key Files |
|------|------|--------|-----------|
| 1 | Name-clean source docstrings (D-03) | c652576 | ketu/synastry/__init__.py, ketu/synastry/core.py, ketu/aspects/calculator.py, ketu/houses/core.py, ketu/charts/core.py |
| 2 | Name-clean EN changelogs + UPGRADING legacy + v1.7→v1.8 entry (D-02/D-06) | b5a6143 | CHANGELOG.md, docs/source/changelog.md, UPGRADING.md |
| 3 | Document v1.8 surface in api.md + concepts.md + [1.8.0] changelog (D-04/D-05/DSPD-07) | 6c4a414 | docs/source/api.md, docs/source/concepts.md, CHANGELOG.md, docs/source/changelog.md |

## What Was Done

### Task 1 — Source docstring name-clean (D-03)

Cleaned exactly 13 lines across 5 files (per the D-03 inventory):

- `ketu/synastry/__init__.py:47` — "Kala adapts to Ketu" → "downstream consumers adapt to Ketu"
- `ketu/synastry/core.py:21,46,105` — "Kala (the downstream ML consumer)" / "a Kala feature pipeline" / "Kala adapts to Ketu" → generic phrasing
- `ketu/aspects/calculator.py:168,299,423,460,536` — "preserve Kala contract" / "(e.g. Kala)" (×3) / "Kala's positional contract" → generic
- `ketu/houses/core.py:10` — "(Kala)" removed from dtype description
- `ketu/charts/core.py:20,97,102` — "Kala (the downstream ML consumer)" / "(Kala)" (×2) → generic

All six quality gates confirmed green after touching source docstrings: `make doc-gates` (interrogate 99.7%, numpydoc clean), `make doctest` (67 passed), `make mypy` (0 issues), `pytest` (1691 passed, 100% coverage).

### Task 2 — Legacy name-clean EN text docs + UPGRADING v1.7→v1.8 entry (D-02/D-06)

**CHANGELOG.md** (11 hits cleaned): "Kala guidance" → "Downstream impact", "BREAKING (Kala / downstream positional contract)" → "BREAKING (downstream positional contract)", "Kala Integration" section → "Downstream ML Integration", removed `KetuDataAdapter` brand name, etc.

**docs/source/changelog.md** (2 hits cleaned): same pattern as CHANGELOG.md.

**UPGRADING.md** (13 hits cleaned): "Kala guidance" headings → "Downstream guidance" (with version suffix on v1.6 to avoid MD024 duplicate), "Kala / downstream consumers" → "Downstream consumers", "Kala's KetuDataAdapter" → removed, "Sibling project Kala" → "Downstream consumers handle their own upgrade independently".

**UPGRADING.md — new v1.7→v1.8 section** added at top (newest-first, above "## v1.6 -> v1.7"): mirrors the v1.4→v1.5 `body_decl` template — states CHART_DTYPE grows to 16 fields (`body_decl_speed` at index 8), MINOR-not-patch rationale, named-access-safe/positional-must-adapt note, migration checklist, verify snippet asserting `chart["body_decl_speed"].shape == (14,)`, new API surface block.

### Task 3 — v1.8 EN documentation + [1.8.0] changelog (D-04/D-05/DSPD-07)

**docs/source/api.md**:
- CHART_DTYPE plain-text table: added `body_decl` row (was missing) AND `body_decl_speed` row (`float64[14]`, dδ/dt °/day, +ve = northward)
- New section `DECL_STANDSTILL_EPS`: value 0.001 °/day, purpose, scope note (applies to chart helper; scalar is_ascending_declination is a plain `> 0` with no threshold)
- New section `is_ascending_declination_chart(chart)`: int8 {+1,0,−1} per body, explicit comparison table vs v1.5 scalar (input/output/standstill columns), runnable example

**docs/source/concepts.md**:
- Legacy name-clean: 2 "Kala" hits → generic
- New section "CHART_DTYPE — body_decl_speed field (New in v1.8)": dδ/dt meaning, sign = montant/descendant, Δt=0.01 d FD rationale (package-wide idiom), standstill contract (DECL_STANDSTILL_EPS), library design principle (Ketu owns the astronomy; consumers read a field), additive-dtype note, full runnable example

**CHANGELOG.md + docs/source/changelog.md**: dated `[1.8.0] - 2026-06-17` entries added above `[1.7.0]` with Added (body_decl_speed, DECL_STANDSTILL_EPS, is_ascending_declination_chart) and Notes (MINOR-not-patch rationale, named-access-safe, positional-must-adapt).

All six quality gates confirmed green after all changes.

## Quality Gate Results

| Gate | Result |
|------|--------|
| `grep -rl 'Kala\|...' ketu/ --include='*.py'` | 0 files (clean) |
| `grep -c 'Rahu\|Ketu\|Lilith' ketu/core.py` | 7 (preserved) |
| `make doc-gates` (interrogate ≥95% + numpydoc) | PASSED (99.7%) |
| `make doctest` | 67 passed, 1 skipped |
| `make mypy` (--strict) | 0 issues, 72 files |
| `pytest tests/ -q` | 1691 passed, 2 skipped |
| `pytest --cov=ketu --cov-fail-under=100` | 100% coverage |

## Deviations from Plan

### Auto-fixed Issues

None — plan executed exactly as written, with one minor deviation:

**[Rule 2 - Minor] Merged Phase 40 commits before starting**

The worktree was forked from `7b200f6` (before Phase 40 ran). Phase 40's symbols (`body_decl_speed`, `DECL_STANDSTILL_EPS`, `is_ascending_declination_chart`) did not exist in the worktree. A `git merge ab26672` (fast-forward, no conflicts) brought in all Phase 40 changes before proceeding. This was necessary to have a working base for documentation — no functional changes introduced.

**[Cosmetic] MD024 duplicate-heading warnings in CHANGELOG.md and UPGRADING.md**

Pre-existing throughout the file (version-suffixed heading pattern "### Added 1.5.0" etc.). My new entries follow the same file convention. Not caused by this plan's edits; excluded from scope per deviation boundary rules.

## Known Stubs

None. All documented symbols (`body_decl_speed`, `DECL_STANDSTILL_EPS`, `is_ascending_declination_chart`) exist in the codebase and are fully implemented (shipped in Phase 40).

## Threat Flags

None. This plan edits documentation prose and source-code docstrings only. No runtime behaviour, parsing, I/O, or user-controlled input was introduced or modified.

## Self-Check: PASSED

All modified files exist on disk. All three task commits (c652576, b5a6143, 6c4a414) confirmed in git log.
