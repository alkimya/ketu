---
phase: 14-chart-abstraction-foundation
plan: 01
subsystem: charts
tags: [numpy, structured-array, chart-dtype, subpackage-skeleton, mypy-strict, numpydoc, interrogate]

# Dependency graph
requires:
  - phase: 13-doc-gates-and-ci-foundation
    provides: interrogate ≥95% gate, numpydoc validate gate, mypy --strict cleanliness
  - phase: 10-houses-module
    provides: HOUSES_DTYPE precedent, calculate_houses signature, HighLatitudeError contract
  - phase: 09-configurable-aspects
    provides: AspectSetSpec type alias, calculate_aspects_vectorized canonical record format
provides:
  - ketu/charts/ subpackage skeleton (__init__.py, core.py, api.py)
  - CHART_DTYPE structured dtype (14 fields, frozen layout, body axis (13,) frozen per D-08)
  - compute_chart and is_day_chart public stubs with full numpydoc docstrings
  - tests/charts/test_dtype.py (32 structural ratchets)
  - pyproject.toml updated to ship ketu.charts in the explicit packages list
affects: [14-02-compute-chart, 14-03-aspect-matrix, 14-04-is-day-chart, 14-05-doc-gates-and-coverage, 16-synastry, 17-composite, 18-solar-return, 19-arabic-parts]

# Tech tracking
tech-stack:
  added: []  # No new runtime deps; pure NumPy on existing stack
  patterns:
    - "ketu/charts/ mirrors ketu/houses/ subpackage layout exactly (core.py + api.py + __init__.py re-exports)"
    - "CHART_DTYPE composes HOUSES_DTYPE inline (D-03) — flat scalar + short subarrays, no nesting"
    - "Aspect matrix sentinel convention: -1 (i1) for 'no aspect', NaN (f4) for 'no orb'"
    - "Stub functions ship with COMPLETE numpydoc docstrings (PR/RT/Notes/Examples) so doc gates stay green wave by wave"

key-files:
  created:
    - ketu/charts/__init__.py
    - ketu/charts/core.py
    - ketu/charts/api.py
    - tests/charts/__init__.py
    - tests/charts/test_dtype.py
    - .planning/phases/14-chart-abstraction-foundation/14-01-SUMMARY.md
  modified:
    - pyproject.toml

key-decisions:
  - "Followed plan exactly — CHART_DTYPE 14 fields in canonical metadata→bodies→houses→aspects order"
  - "Section 'Why a structured array?' lives in core.py (not __init__.py) per RESEARCH § 7"
  - "is_day_chart kept in api.py (no separate sect.py) per PATTERNS § 4 minimal-ship recommendation"
  - "32 tests in test_dtype.py (12 unique cases, parametrized expansion to 32)"
  - "Section ordering in __init__.py docstring fixed to numpydoc-canonical: See Also → Notes → Examples"

patterns-established:
  - "Stub-with-full-docstrings: compute_chart/is_day_chart raise NotImplementedError but expose final signatures + complete docstrings, keeping doc gates green continuously across the phase wave"
  - "AGPL-boundary ratchet: per-package test_no_runtime_swisseph_import to copy verbatim into every new ketu/* subpackage from now on"
  - "Anti-dataclass ratchet: explicit test asserting no `Chart` symbol in core.py, ratcheting against the cycles/ legacy double source-of-truth"

requirements-completed: [CHART-01, CHART-02]

# Metrics
duration: ~7 min
completed: 2026-05-08
---

# Phase 14 Plan 1: Subpackage Skeleton + CHART_DTYPE Summary

**ketu/charts/ subpackage scaffolded with frozen 14-field CHART_DTYPE, full numpydoc-clean stubs, and 32 structural ratchets — fondation contractuelle pour Plans 14-02..05.**

## Performance

- **Duration:** ~7 min
- **Started:** 2026-05-08T22:26:32Z
- **Completed:** 2026-05-08T22:33:39Z
- **Tasks:** 7 (1 pyproject + 3 prod files + 2 test files + 1 verification sweep)
- **Files created:** 6 (5 source + 1 SUMMARY)
- **Files modified:** 1 (pyproject.toml)

## Accomplishments

- `ketu/charts/` subpackage created with the full v1.1 houses/ template applied (subpackage layout, `__future__ annotations`, `__all__` discipline, mypy --strict cleanliness)
- `CHART_DTYPE` defined with 14 fields per D-01..D-06 (metadata + body subarrays + inline houses + aspect matrix + aspect orbs)
- `core.py` carries the **"Why a structured array?"** rationale section required by success criterion 14.5
- `compute_chart` and `is_day_chart` ship as stubs with COMPLETE numpydoc docstrings (Parameters/Returns/Raises/Notes/Examples) so plans 14-02/03/04 can wire bodies without churning the docstrings
- `pyproject.toml` updated to include `"ketu.charts"` in the explicit `[tool.setuptools] packages` list (required override of CONTEXT.md ligne 131; PATTERNS § 7.8 gotcha)
- `tests/charts/test_dtype.py` pins 32 assertions covering: public imports, field-name order, subarray shapes, scalar field kinds, vectorized + zero-dim construction, U10 capacity + truncation, sentinel round-trips (-1 / NaN), Why-structured-array docstring ratchet, anti-dataclass ratchet, AGPL no-swisseph ratchet, NotImplementedError stub guards
- All 7 verification gates pass clean: pytest tests/charts (32/32), interrogate 100%, numpydoc lint clean, mypy --strict clean, full pytest 756/756, pyproject check, smoke import

## Task Commits

Tasks were committed in two atomic commits (Task 1 isolated as a `chore`, Tasks 2–7 grouped as a `feat` per the plan's prescribed atomic-commit-message section):

1. **Task 1: Add ketu.charts to pyproject.toml** — `907dba9` (chore)
2. **Tasks 2–7: Scaffold ketu.charts subpackage with CHART_DTYPE** — `b52154e` (feat)

**Plan metadata:** _to be added by final docs commit after this SUMMARY lands_

## Files Created/Modified

- `ketu/charts/__init__.py` — Subpackage re-exports `CHART_DTYPE`, `compute_chart`, `is_day_chart`. Module docstring carries the public-API surface description, See Also / Notes / Examples sections (numpydoc-canonical order).
- `ketu/charts/core.py` — Defines `CHART_DTYPE` with the 14-field layout (D-01..D-06). Module docstring includes the "Why a structured array?" rationale (success criterion 14.5).
- `ketu/charts/api.py` — Stubs `compute_chart(jd, lat, lon, system, aspects, polar_fallback)` and `is_day_chart(jd, lat, lon)` with full numpydoc docstrings. Both raise `NotImplementedError` pending plans 14-02/03/04.
- `tests/charts/__init__.py` — Empty test-package marker.
- `tests/charts/test_dtype.py` — 12 test functions (32 cases via parametrization) covering structural invariants, ratchets, and stub guards.
- `pyproject.toml` — Added `"ketu.charts"` to the explicit `[tool.setuptools] packages` list between `"ketu.houses"` and `"ketu.cli"`.
- `.planning/phases/14-chart-abstraction-foundation/14-01-SUMMARY.md` — This file.

## Decisions Made

Followed the plan exactly. Three small adjustments documented as Rule-3 in-scope tweaks:

1. **Numpydoc section order in `__init__.py`** — Initial draft had Examples before See Also/Notes (mirroring RESEARCH § 1's snippet which places Examples second). Numpydoc lint flagged GL07 (Sections in wrong order). Fixed to the canonical See Also → Notes → Examples ordering. The plan's `__init__.py` snippet was a sketch; the gate is the authority.
2. **Test file consolidation (Tasks 6 + 7)** — Plan offered "discrétion" to put NotImplementedError stub tests either in `test_dtype.py` or a new `test_stubs.py`. Consolidated into `test_dtype.py` for now; the two stub tests are explicitly tagged with `# Stub test — to be removed in plan 14-0X` so plans 14-02 / 14-04 know exactly what to delete.
3. **Test count parametrization** — The plan asks for "12+ tests"; we shipped 12 unique test functions but parametrize 2 of them (subarray shapes × 6 fields, scalar kinds × 14 fields), producing 32 PASSED entries. The `done criteria` "12+ tests verts" is met (32 ≥ 12).

## Deviations from Plan

**Plan executed exactly as written.** Three minor in-task adjustments listed above as Decisions. None of them alter the contract, the file count, or the verification gates.

The pyproject.toml line is the deliberate override of CONTEXT.md ligne 131 that the plan explicitly calls out (PATTERNS § 7.8).

## Issues Encountered

- **Coverage gate noise on partial run** — `pytest tests/charts/` (no `--no-cov`) hits the project-wide `addopts = "-v --cov=ketu --cov-report=term-missing"` which then fails because charts-only coverage of `ketu/` totals 14%. This is the documented pyproject behavior (lines 71–75: "do NOT add --cov-fail-under to addopts"); the gate I followed is `pytest tests/charts/ -v -x --no-cov` for partial runs and the full `pytest tests/` for the suite gate. Both pass green. No action needed; documented here for next plan operators.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **Plan 14-02 ready** — `CHART_DTYPE` is contractual; `compute_chart` stub signature/docstring are final. Plan 14-02 will wire body positions + houses without touching the dtype or the docstring.
- **Plan 14-03 ready** — same as 14-02 for the aspect_matrix branch. The sentinels (-1 / NaN, diagonal initialisation) are pinned by tests 8 and 9 in `test_dtype.py`.
- **Plan 14-04 ready** — `is_day_chart` stub is parallelizable with 14-02/03 (no shared code path). Plan 14-04 will delete the stub-NotImplementedError test and add real sect tests.
- **Plan 14-05 ready** — doc-gate sweep already green at this checkpoint; Plan 14-05 just has to keep the gates green and add the `make charts-coverage` Makefile target.

No blockers. No carry-over technical debt. The Plans 14-02..05 wave can run with confidence that the contract surface is locked.

## Self-Check: PASSED

Files verified to exist:

- FOUND: ketu/charts/__init__.py
- FOUND: ketu/charts/core.py
- FOUND: ketu/charts/api.py
- FOUND: tests/charts/__init__.py
- FOUND: tests/charts/test_dtype.py
- FOUND: .planning/phases/14-chart-abstraction-foundation/14-01-SUMMARY.md

Commits verified to exist:

- FOUND: 907dba9 (chore: add ketu.charts to pyproject)
- FOUND: b52154e (feat: scaffold ketu.charts subpackage)

Verification gates re-confirmed:

- pytest tests/charts/ → 32 passed
- interrogate → 100.0% (PASSED, minimum 95.0%)
- numpydoc lint → clean (no output)
- mypy --strict ketu/charts/ → Success: no issues found in 3 source files
- pytest tests/ (full suite) → 756 passed
- pyproject check → ketu.charts present
- smoke import → CHART_DTYPE.names[:4] == ('jd','lat','lon','system')

---
*Phase: 14-chart-abstraction-foundation*
*Plan: 01-subpackage-skeleton-and-dtype*
*Completed: 2026-05-08*
