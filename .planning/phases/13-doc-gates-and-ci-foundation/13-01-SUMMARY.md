---
phase: 13-doc-gates-and-ci-foundation
plan: 01
subsystem: infra
tags:
  - ops
  - ci
  - docstrings
  - interrogate
  - numpydoc
  - pyproject

# Dependency graph
requires: []
provides:
  - "[project.optional-dependencies].dev group installs interrogate>=1.7.0 + numpydoc>=1.10.0"
  - "[tool.interrogate] config block (fail-under=95, lunar_calendar.py excluded, ignore-private/semiprivate=false)"
  - "4 one-line docstrings on _ra_formula_cusp_2/3/11/12 in ketu/houses/placidus.py"
  - "Local interrogate baseline at 100.0% (gate ready to wire to CI in Plan 02)"
affects:
  - 13-02 (interrogate CI step + Makefile target — already-green gate)
  - 13-03 (numpydoc config + source docstring fix-pass — same dev group)
  - 13-04 (numpydoc CI step — same dev group)
  - All later v1.2 phases (every new module is now subject to interrogate>=95% locally)

# Tech tracking
tech-stack:
  added:
    - "interrogate>=1.7.0 (docstring coverage tool, dev-only)"
    - "numpydoc>=1.10.0 (docstring style validator, dev-only — wired to CI in Plan 04)"
  patterns:
    - "AGPL-isolated dev group: [project.optional-dependencies].dev sibling of test (not colocated with pysweph) — D-01 boundary"
    - "Mirror [tool.coverage.run].omit shape in [tool.interrogate].exclude — single source of truth for legacy/unmaintained surface"
    - "ignore-private/semiprivate = false to enforce D-08 (fix gaps, don't paper them over)"

key-files:
  created: []
  modified:
    - "pyproject.toml — added [project.optional-dependencies].dev group + [tool.interrogate] block"
    - "ketu/houses/placidus.py — added 4 one-line docstrings on _ra_formula_cusp_2/3/11/12"

key-decisions:
  - "Pin floors (>=) not exact pins for interrogate / numpydoc — matches `pysweph>=2.10.3.6` convention in `test`"
  - "ignore-private = false / ignore-semiprivate = false — D-08 enforcement via 4 one-line docstrings, not suppression flags"
  - "verbose = 1 so the score appears in green-build logs as a positive signal (CONTEXT § Specifics)"
  - "One-line docstrings (not full Parameters/Returns numpydoc blocks) for the 4 trivial dispatched helpers — substantive math doc lives in module docstring + _CUSP_FORMULAS dispatch table per PATTERNS.md"

patterns-established:
  - "Dev-group separation: AGPL deps live in `test`, quality tooling lives in `dev` — preserves runtime/contamination boundary while making `pip install -e .[dev]` the canonical contributor command"
  - "Audit-then-wire principle (D-09 + RESEARCH plan sequence): land config + fix gaps locally first, wire CI only when the gate is already green — first impression matters in build logs"
  - "Per-cusp formula one-liner shape (`\"\"\"RA of Placidus cusp N: ``<formula>`` (mod 360).\"\"\"`) — reusable depth for trivial dispatched helpers where module docstring carries the substantive content"

requirements-completed:
  - OPS-01

# Metrics
duration: 3min
completed: 2026-05-08
---

# Phase 13 Plan 01: Doc-gate baseline (interrogate + dev extras) Summary

**Local `interrogate` gate now passes at 100.0% (>=95% threshold) via new `dev` extras group + `[tool.interrogate]` config + 4 one-line docstrings on placidus.py cusp helpers — gate ready for CI wiring in Plan 02.**

## Performance

- **Duration:** ~3 min active
- **Started:** 2026-05-08T11:24:47Z
- **Completed:** 2026-05-08T11:27:56Z
- **Tasks:** 2 / 2
- **Files modified:** 2

## Accomplishments

- `[project.optional-dependencies].dev = ["interrogate>=1.7.0", "numpydoc>=1.10.0"]` added as a sibling of the existing `test` group (D-01 — AGPL boundary preserved). `pip install -e ".[dev]"` resolves cleanly; both tools import (`interrogate 1.7.0`, `numpydoc 1.10.0`).
- `[tool.interrogate]` configuration block landed verbatim from PATTERNS.md: `fail-under = 95`, `verbose = 1`, exclusion mirroring `[tool.coverage.run].omit` (`ketu/lunar_calendar.py`, `tests`, `build`, `docs`), `ignore-init-method = true`, `ignore-magic = true`, `ignore-nested-functions = true`, `ignore-private = false`, `ignore-semiprivate = false`, `style = "sphinx"`.
- 4 one-line docstrings added to `_ra_formula_cusp_11/12/2/3` in `ketu/houses/placidus.py` — copied verbatim from PATTERNS.md, signatures unchanged.
- `python -m interrogate ketu/` now reports `RESULT: PASSED (minimum: 95.0%, actual: 100.0%)` — better than the predicted 98.2% baseline because all 4 known misses were patched.
- 724 existing tests still pass (`pytest tests/ -q --no-cov`); `mypy ketu/ --strict` reports `Success: no issues found in 40 source files`.
- Plan 02 readiness smoke confirmed: `grep 'interrogate' .github/workflows/tests.yml` returns zero hits — the workflow file was deliberately left untouched.

## Task Commits

Each task was committed atomically (worktree mode, `--no-verify` to avoid pre-commit hook contention):

1. **Task 1: Add `dev` optional-deps group + `[tool.interrogate]` config to pyproject.toml** — `65ccd74` (chore)
2. **Task 2: Add docstrings to 4 `_ra_formula_cusp_*` helpers in `ketu/houses/placidus.py`** — `33ea9a1` (docs)

_Note: no plan-metadata commit yet — this SUMMARY.md is committed at the end of the worktree run by the agent before handoff to the orchestrator._

## Files Created/Modified

- `pyproject.toml` — added `[project.optional-dependencies].dev` group (lines 45-48) and `[tool.interrogate]` block (after `[tool.coverage.report]`, before `[tool.mypy]`). +20 lines, 0 deletions.
- `ketu/houses/placidus.py` — added 4 one-line docstrings to `_ra_formula_cusp_11/12/2/3` (lines 82-95). +4 lines, 0 deletions. No signature, body, or import changes.

## Decisions Made

- **Plan was followed verbatim.** The blocks landed are byte-identical to the PATTERNS.md / RESEARCH.md spec. No design choices were re-opened during execution.
- **No CI changes** were made (deliberately — Plan 02 owns that). `grep 'interrogate' .github/workflows/tests.yml` confirms zero hits at end of plan, matching the plan's smoke check.

## Deviations from Plan

None — plan executed exactly as written.

The plan accurately predicted the post-fix interrogate score range (98.2% → 100.0%); the actual outcome is the upper bound (100.0%) because all 4 known misses were patched in Task 2.

## Issues Encountered

**Venv pip shebang drift (documented pre-existing issue, NOT new in this plan).**

`venv/bin/pip` has shebang `#!/home/loc/workspace/solaris/ketu/venv/bin/python3` — an obsolete path from before the repo was relocated from `solaris/ketu/` to `ketu/`. This is documented in `.planning/STATE.md` § "Working-tree leftovers" and `.planning/PROJECT.md` § "Known v1.2 ops debt" — the workaround (use `python -m pip` / invoke via `venv/bin/python -m <tool>`) is already the project convention.

Resolution: used `venv/bin/python -m pip install -e ".[dev]"` and `venv/bin/python -m interrogate ketu/` throughout this plan. No code change required; recording here for traceability.

## User Setup Required

None — no external service configuration required. Contributors who pull this commit should run `pip install -e ".[dev]"` (or `venv/bin/python -m pip install -e ".[dev]"` if their venv has the shebang drift) once to install the new optional-deps group locally.

## Next Plan Readiness

**Plan 02 (interrogate CI wiring + Makefile target — Wave 2) can proceed immediately.**

- Local gate is green at 100.0%; the first CI run on Plan 02 will pass on first push (no remediation cycle needed).
- The `pip install -e ".[dev]" || pip install -e .` install verb already in `tests.yml` line 28 starts succeeding immediately for the `dev` group (no workflow edit needed for the install step itself, per D-02).
- `make doc-gates` target referenced by Plan 02 will exit 0 because `interrogate ketu/` is already passing.

**Plan 03 (numpydoc fix-pass — Wave 2)** also benefits: `numpydoc` is already installed in the dev venv via this plan's `pip install -e ".[dev]"`, so audit-pre-flight invocations work without an extra install step.

## Self-Check: PASSED

Verified after writing SUMMARY:

- `pyproject.toml` exists and contains `[project.optional-dependencies].dev` + `[tool.interrogate]` blocks (greps returned 1 match each).
- `ketu/houses/placidus.py` exists; `grep -c '"""RA of Placidus cusp' ketu/houses/placidus.py` returns 4.
- Commit `65ccd74` exists in `git log`: chore(13-01) for the pyproject.toml edits.
- Commit `33ea9a1` exists in `git log`: docs(13-01) for the placidus docstrings.
- `python -m interrogate ketu/` exits 0 with score 100.0%.
- 724 tests pass; mypy --strict clean.
- `.github/workflows/tests.yml` was NOT modified (zero `interrogate` hits as required by plan's smoke check).

---
*Phase: 13-doc-gates-and-ci-foundation*
*Completed: 2026-05-08*
