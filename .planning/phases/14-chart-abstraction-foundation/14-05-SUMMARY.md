---
phase: 14-chart-abstraction-foundation
plan: 05
subsystem: charts
tags: [doc-gates, coverage-gate, makefile, pytest-marker, numpydoc, interrogate, mypy-strict, ratchet, ci-mirror]

# Dependency graph
requires:
  - phase: 14-chart-abstraction-foundation
    plan: 01
    provides: ketu/charts/ subpackage skeleton, CHART_DTYPE frozen layout
  - phase: 14-chart-abstraction-foundation
    plan: 02
    provides: compute_chart positions + houses pipeline (broadcast vectorised)
  - phase: 14-chart-abstraction-foundation
    plan: 03
    provides: dense (13, 13) aspect_matrix wired in compute_chart
  - phase: 14-chart-abstraction-foundation
    plan: 04
    provides: is_day_chart sect helper (polar-safe, sunrise-inclusive)
  - phase: 13-doc-gates-and-ci-foundation
    provides: interrogate >=95% gate, numpydoc validate, mypy --strict baseline
  - phase: 10-houses-module
    provides: make houses-coverage Makefile precedent (HOU-09 95% gate template)
provides:
  - make charts-coverage Makefile target (CHART-05 95% gate, CI-mirrored)
  - charts_coverage_gate pytest marker (symmetry with houses_coverage_gate)
  - See Also cross-references in compute_chart and is_day_chart docstrings
  - Confirmation that ketu/charts/ has zero carve-outs in mypy/coverage/interrogate
  - 100% coverage on ketu/charts/ (well above the 95% ratchet)
affects: [v1.2.0-release]

# Tech tracking
tech-stack:
  added: []  # No new runtime deps; pure Makefile + pyproject + docstring polish
  patterns:
    - "make charts-coverage mirrors make houses-coverage two-step pattern (avoids NumPy _NoValueType reload bug under coverage.py)"
    - "charts_coverage_gate marker follows houses_coverage_gate naming convention; non-blocking (no test currently uses it) but grep-able for the gate's CI provenance"
    - "See Also sections in compute_chart / is_day_chart cross-link the chart pipeline (compute_chart <-> calculate_houses + calculate_aspects_vectorized + is_day_chart ; is_day_chart <-> compute_chart + house_of)"

key-files:
  created:
    - .planning/phases/14-chart-abstraction-foundation/14-05-SUMMARY.md
  modified:
    - ketu/charts/api.py
    - Makefile
    - pyproject.toml

key-decisions:
  - "Followed plan exactly — no architectural changes, no production-code edits beyond docstring polish"
  - "compute_chart Examples block kept under # doctest: +SKIP (Plan 14-02 carry-over): the SKIP markers preserve readability of the vectorised example without flake on numpy version repr drift; doctests are still exercised via the is_day_chart Examples (3 doctests pass)"
  - "Tasks 4-5-6 (Makefile + marker + carve-out audit) committed together as a single chore: they form one infrastructure unit; splitting would leave a non-CI-runnable intermediate state"
  - "Task 6 audit confirmed: pyproject.toml has zero carve-outs for ketu.charts.* in [tool.mypy.overrides], [tool.coverage.run].omit, or [tool.interrogate].exclude (line 61 explicit packages list is the only mention, which is the correct setuptools registration)"
  - "Pre-existing RuntimeWarning in ketu/ephemeris/orbital.py:733 (invalid value in arcsin(z/r)) carried over from prior plans; out-of-scope per SCOPE BOUNDARY rule (not introduced by this plan)"

patterns-established:
  - "Plan-05 doc-gate ratchet template: any future v1.X subpackage can run a 4-task close-out (audit docstrings -> add See Also -> add coverage Makefile target -> add pytest marker) without touching production code"
  - "100% coverage benchmark on a wave-3 subpackage: ketu/charts/ ships at 100% line coverage, demonstrating that the wave-by-wave doc-gate-clean pattern (stubs first, full docstrings always green) yields zero defensive-branch debt"

requirements-completed: [CHART-05]

# Metrics
duration: ~4 min
completed: 2026-05-09
---

# Phase 14 Plan 5: Doc Gates Final + Coverage Ratchet + Makefile Target Summary

**CHART-05 coverage gate wired (`make charts-coverage` mirroring HOU-09), `charts_coverage_gate` pytest marker added, See Also cross-references polished into `compute_chart`/`is_day_chart` — final ratchet that closes Phase 14 with zero carve-outs and 100% coverage on `ketu/charts/`.**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-05-08T23:12:29Z
- **Completed:** 2026-05-09 (current session)
- **Tasks:** 8 (1 docstring polish + 1 core.py audit + 1 __init__.py audit + 1 Makefile + 1 marker + 1 carve-out audit + 1 coverage gate run + 1 final verification sweep)
- **Files created:** 1 (SUMMARY)
- **Files modified:** 3 (`ketu/charts/api.py`, `Makefile`, `pyproject.toml`)
- **New production code:** 0 lines (per plan: "Pas de nouveau code de production")
- **New tests:** 0 (per plan: "Pas de nouveaux tests fonctionnels")

## Accomplishments

- **`See Also` sections added** to `compute_chart` and `is_day_chart` docstrings:
  - `compute_chart` -> `calculate_houses` (D-11 pass-through), `calculate_aspects_vectorized` (D-05/D-17 projection), `is_day_chart` (D-12 standalone-helper rationale).
  - `is_day_chart` -> `compute_chart` (D-12 reverse cross-ref), `house_of` (D-14 internal).
- **`make charts-coverage` Makefile target** added, mirroring `make houses-coverage` exactly (same two-step pattern with the inline comment explaining the NumPy `_NoValueType` reload bug under `source=ketu.charts`).
- **`.PHONY` updated** to include `charts-coverage` between `houses-coverage` and `doc-gates`.
- **`charts_coverage_gate` pytest marker** added to `pyproject.toml` `markers` list (third entry, alphabetical after `houses_coverage_gate`). Non-blocking: no test currently carries the marker, but it documents the gate's existence for grep-ability and CI symmetry with houses.
- **Carve-out audit (Task 6) confirmed clean:** `[tool.mypy.overrides]` lines 144-153 do NOT mention `ketu.charts.*`; `[tool.coverage.run].omit` does NOT mention `ketu/charts/*`; `[tool.interrogate].exclude` does NOT mention `ketu/charts*`. The only `ketu.charts` reference is line 61 (`packages = [..., "ketu.charts", ...]`) which is the correct setuptools registration. **No `pyproject.toml` modifications beyond the marker.**
- **`ketu/charts/core.py` audit (Task 2) confirmed clean:** "Why a structured array?" section is present with 4 bullets, the 14 fields are documented via `#:` sphinx comments above `CHART_DTYPE`, the sentinel convention `chart["aspect_matrix"] >= 0` and the canonical 13-body order are both documented. **No modifications.**
- **`ketu/charts/__init__.py` audit (Task 3) confirmed clean:** vectorised example is present at module-docstring level (`>>> chart = compute_chart(np.array([...]), ...)`), `See Also` points to `calculate_houses` + `calculate_aspects_vectorized`, `__all__` is alphabetically sorted (`["CHART_DTYPE", "compute_chart", "is_day_chart"]`). **No modifications.**
- **No residual transition notes:** scanned `ketu/charts/api.py` for "currently ignored", "sentinel-only", "stub", "NotImplementedError" — zero matches. Plan 14-03 already cleaned the Plan-02 transitional aspect-block note.

## Verification Gates (Task 8)

All 8 gates from the plan §"Task 8 — Vérification finale" pass green:

| Gate                                                    | Result                                |
| ------------------------------------------------------- | ------------------------------------- |
| `pytest tests/charts/ -v -x`                            | 120 passed                            |
| `make doc-gates`                                        | exit 0 (interrogate + numpydoc lint)  |
| `make mypy`                                             | Success: no issues found in 43 files  |
| `make charts-coverage`                                  | 120 passed, **100% coverage**         |
| `pytest tests/ --no-cov -x`                             | 844 passed (zero regression)          |
| `pytest tests/ --cov=ketu --cov-fail-under=70`          | 844 passed, **98.07% project-wide**   |
| `pytest --doctest-modules ketu/charts/`                 | 3 doctests passed                     |
| Smoke import canary (`compute_chart` + `is_day_chart`)  | "Final smoke OK"                      |

### Coverage detail (Task 7)

```
Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
ketu/charts/__init__.py       4      0   100%
ketu/charts/api.py           74      0   100%
ketu/charts/core.py           3      0   100%
-------------------------------------------------------
TOTAL                        81      0   100%
Required test coverage of 95% reached.
```

100% line coverage on all 3 files of `ketu/charts/`. The 95% ratchet is exceeded by 5 percentage points; no `# pragma: no cover` markers were needed. **Strategy 1 from plan §Task 7 (add targeted test) was NOT triggered**; the wave-by-wave coverage discipline of Plans 14-01..04 already produced full coverage.

### interrogate detail (`interrogate ketu/`)

```
TOTAL: 100.0% (225/225 docstrings present)
RESULT: PASSED (minimum: 95.0%, actual: 100.0%)
```

`ketu/charts/` contributes 8 fully-documented public/private symbols.

### numpydoc lint detail

`numpydoc lint ketu/charts/*.py` -> clean (no output). Pre-existing warnings on `ketu/aspects/timelines.py` are out-of-scope (carry-over from before Phase 13; documented as deferred in `pyproject.toml` line 121: `"GL01"  # ignore during warning phase (Phase 13–19); fix and remove in Phase 20`).

## Task Commits

| Task         | Description                                                                                                       | Commit    | Type    |
| ------------ | ----------------------------------------------------------------------------------------------------------------- | --------- | ------- |
| Tasks 1-3    | Add `See Also` sections to `compute_chart` / `is_day_chart` docstrings; audit `core.py` + `__init__.py` (no mods) | `2154600` | docs    |
| Tasks 4-5-6  | Wire `make charts-coverage` Makefile target + `charts_coverage_gate` pytest marker; carve-out audit (no mods)     | `4fcb936` | chore   |
| Tasks 7-8    | Run coverage gate + 8-gate verification sweep (no code changes)                                                   | n/a       | n/a     |

Two atomic commits cover the work. Tasks 7-8 are pure verification (no code changes), so no commit was created — the verification results are reported in this Summary.

## Files Created/Modified

- `ketu/charts/api.py` — Added `See Also` section to `compute_chart` docstring (between `Raises` and `Notes`, cross-referencing `calculate_houses`, `calculate_aspects_vectorized`, `is_day_chart`); added `See Also` section to `is_day_chart` docstring (between `Returns` and `Notes`, cross-referencing `compute_chart`, `house_of`). +21 insertions, 0 deletions. mypy --strict still clean, numpydoc lint still clean, doctests still green.
- `Makefile` — Added `charts-coverage` to `.PHONY` line (one entry between `houses-coverage` and `doc-gates`); added the new target with the documented two-step pattern. +14 insertions, 1 deletion.
- `pyproject.toml` — Added `charts_coverage_gate` marker to `[tool.pytest.ini_options].markers` list. +1 insertion, 0 deletions.
- `.planning/phases/14-chart-abstraction-foundation/14-05-SUMMARY.md` — This file.

## Decisions Made

Followed the plan exactly. Three small in-scope adjustments documented as Rule-3 tweaks:

1. **Tasks 4-5-6 committed together as a single `chore` commit** rather than three separate commits. The plan describes them as separate tasks, but Task 6 is a pure audit (zero modifications), Task 5 (marker) is a 1-line edit, and Task 4 (Makefile target) is meaningless without the marker registration. Splitting would either (a) create a chore commit for Task 5 with a marker referring to a Makefile target that doesn't exist yet, or (b) create a Makefile commit referring to a marker that doesn't exist yet. The plan's "Atomic commit message" template combines all of CHART-05 into one feat; here we used `chore` since the Makefile + pyproject changes are infrastructure (no behavior change) — but the spirit (one commit per logical unit) is honored.
2. **`compute_chart` Examples block kept under `# doctest: +SKIP`** rather than rewriting to be doctest-executable. Rationale: the SKIP markers preserve the visual readability of the vectorised example (`>>> charts.shape, charts["body_lons"].shape, charts["aspect_matrix"].shape` -> `((2,), (2, 13), (2, 13, 13))`) without flake on numpy version repr drift; the success criterion 14.2 requirement ("vectorised example visible at the API surface") is met by the docstring text itself, not by doctest execution. Meanwhile the `is_day_chart` Examples are doctest-executable (3 doctests pass), so the doctest harness is exercised on the public API. This is the plan §Task 8 "Option 1 (préférée)" path; documented loudly in the docstring via the SKIP markers.
3. **Pre-existing `RuntimeWarning` in `ketu/ephemeris/orbital.py:733`** logged but NOT fixed. Out-of-scope per SCOPE BOUNDARY rule (carried over from before Phase 14; surfaces in 61 warnings during the charts test suite). Plans 14-02 and 14-04 also flagged this; tracking will continue independently of Phase 14 closure.

None of these adjustments alter the contract, the file count, or the verification gates. The plan's `done criteria` checklist is met one-for-one (see below).

## Deviations from Plan

**Plan executed exactly as written.** Three minor in-task adjustments listed above as Decisions. No architectural changes, no auth gates, no fix-attempt limit triggers, no out-of-scope discoveries.

## Issues Encountered

- **Pre-existing `RuntimeWarning` in `ketu/ephemeris/orbital.py:733`** (invalid value in `np.arcsin(z / r)`) — same warning logged in plans 14-02, 14-04. Visible in 61 charts-test warnings + 7 cache-test warnings. Out-of-scope per the SCOPE BOUNDARY rule. Tracked here for the verifier; if this becomes a CI gate later, a dedicated phase ticket should investigate `r -> 0` cases in the orbital.py spherical conversion.
- **Coverage gate noise on partial run** (carry-over from 14-01..04) — `pytest tests/charts/` without `--no-cov` still hits the project-wide `--cov=ketu` config; the project-wide threshold is 70% which is comfortably met (98.07%). Standard mitigation: use `--no-cov` for partial runs, full `pytest tests/` for the suite gate. Both green here. **Not a blocker.**

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

Phase 14 is **complete**. CHART-01..05 are all marked done:

- **CHART-01** (subpackage layout) — Plan 14-01 (committed)
- **CHART-02** (CHART_DTYPE) — Plan 14-01 (committed)
- **CHART-03** (compute_chart full pipeline) — Plans 14-02 + 14-03 (committed)
- **CHART-04** (is_day_chart) — Plan 14-04 (committed)
- **CHART-05** (>=95% coverage + Makefile gate) — **this plan** (committed)

Downstream consumers are unblocked:

- **Phase 16 (Synastry)** — will consume `aspect_matrix` cross-chart; the dense layout is the canonical interface, frozen by D-05/D-17.
- **Phase 17 (Composite)** — will compose two `CHART_DTYPE` instances; the body axis (13,) is frozen by D-08.
- **Phase 18 (Solar Return)** — will batch `compute_chart` calls; the broadcast contract is established by D-09 (S-leading vectorisation).
- **Phase 19 (Arabic Parts)** — will call `is_day_chart(jd, lat, lon)` directly per D-12; sect convention sunrise-inclusive (D-13) and polar safety (D-15) are pinned by Plan 14-04 tests.

The CI mirror is now complete: any PR that lands `ketu/charts/*.py` changes will have `make charts-coverage` enforce the 95% ratchet on a separate Makefile invocation (mirror of HOU-09).

No blockers. No carry-over technical debt from this plan.

## TDD Gate Compliance

This plan does not declare `type: tdd` in its frontmatter; the verification-only nature of the work (no production-code changes) makes RED/GREEN gates inapplicable. The two atomic commits are `docs` (See Also additions) and `chore` (Makefile + marker), neither of which represents a feature introduction. **TDD gates not required for this plan.**

## Threat Flags

None — this plan is purely doc/infrastructure/ratchet. No new endpoints, auth surfaces, file-access patterns, or schema changes. The Makefile target invokes `pytest` and `coverage report` only, both pre-existing tools with no new trust boundaries.

## Self-Check: PASSED

Files verified to exist:

- FOUND: ketu/charts/api.py (modified, +21 lines)
- FOUND: Makefile (modified, +14/-1)
- FOUND: pyproject.toml (modified, +1)
- FOUND: .planning/phases/14-chart-abstraction-foundation/14-05-SUMMARY.md

Commits verified to exist:

- FOUND: 2154600 (docs(14-05): add See Also sections to compute_chart and is_day_chart)
- FOUND: 4fcb936 (chore(14-05): wire CHART-05 coverage gate (Makefile + pytest marker))

Verification gates re-confirmed:

- pytest tests/charts/ -v -x --no-cov -> **120 passed**
- make doc-gates -> exit 0 (interrogate 100% + numpydoc lint clean)
- make mypy -> Success: no issues found in **43 source files**
- make charts-coverage -> 120 passed + **100% coverage on ketu/charts/** (Required: 95%)
- pytest tests/ --no-cov -x -> **844 passed** (zero regression vs baseline)
- pytest tests/ --cov=ketu --cov-fail-under=70 -> 844 passed, **98.07% project-wide**
- pytest --doctest-modules ketu/charts/ -> **3 doctests passed**
- Smoke canary -> "Final smoke OK"

---
*Phase: 14-chart-abstraction-foundation*
*Plan: 05-doc-gates-coverage-and-makefile*
*Completed: 2026-05-09*
