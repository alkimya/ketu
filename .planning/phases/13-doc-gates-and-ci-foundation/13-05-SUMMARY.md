---
phase: 13-doc-gates-and-ci-foundation
plan: 05
subsystem: docs
tags:
  - ops
  - docs
  - changelog
  - readme

# Dependency graph
requires:
  - 13-02
  - 13-04
provides:
  - "README.md `### Documentation Quality Gates` section under `## Documentation` describing the live CI gates (interrogate blocking + numpydoc warning, blocking from v1.2.0) and `make doc-gates` for local execution"
  - "CHANGELOG.md `## [Unreleased]` heading + `### Added` entry citing OPS-01 + OPS-02, mentioning the new `dev` extras group, the `make doc-gates` target, and the warning-blocking-from-v1.2.0 posture"
  - "OPS-01 / OPS-02 traceability fully closed in public docs — every claim is now factually backed by code that shipped in Plans 01–04 (D-13 enforced)"
affects:
  - "Phase 13 acceptance gate (closes the 13.3 ROADMAP success criterion: aspirational refs reformulated)"
  - "Phase 20 plan author (rename `## [Unreleased]` to `## [1.2.0] - YYYY-MM-DD` when flipping numpydoc to blocking; bump pyproject + ketu/__init__.py; remove `continue-on-error: true` and `\"GL01\"` suppression; fix the deferred ~59 GL01 + 100 SS03/PR09/RT05 hits)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Positive-add reformulation pattern: when the aspirational-refs sweep returns ZERO hits pre-edit, the 'reformulation pass' becomes a positive-add of qualified-from-day-one claims rather than a rewrite. PATTERNS.md § 'CHANGELOG.md and README.md — positive-add of \"enforced by CI\" wording' provided the byte-identical text blocks landed."
    - "Keep-a-Changelog `## [Unreleased]` convention: project preamble explicitly cites Keep-a-Changelog; in-flight v1.2 work goes under `## [Unreleased]` until release; Phase 20 will rename to `## [1.2.0] - YYYY-MM-DD`."
    - "Qualification-by-context pattern for doc-quality claims: every mention of `interrogate ≥95%` / `numpydoc validate` is now in proximity to `(blocking)`, `(warning, blocking from v1.2.0)`, or `enforced by CI` wording — never bare. Final sweep verifies this invariant."

key-files:
  created: []
  modified:
    - "README.md — +9 / -0. New `### Documentation Quality Gates` sub-section inserted under `## Documentation`, BEFORE `## Requirements`. Top-level section ordering preserved (Documentation → Requirements → Supported bodies → ...). Verbatim from PATTERNS.md."
    - "CHANGELOG.md — +10 / -0. New `## [Unreleased]` heading + `### Added` entry inserted BEFORE `## [1.1.0] - 2026-05-08`. Preamble (lines 1-8) intact. Existing `## [1.1.0]` and earlier entries unchanged. Verbatim from PATTERNS.md."

key-decisions:
  - "Plan executed verbatim — both blocks are byte-identical to PATTERNS.md § 'CHANGELOG.md and README.md — positive-add of \"enforced by CI\" wording'. No design decisions re-opened during execution."
  - "README placement: `### Documentation Quality Gates` as a sub-section UNDER the existing `## Documentation` heading (NOT a new top-level `## Documentation Quality Gates` section). Reasoning: the gates are conceptually about Ketu's documentation; using `###` preserves the README's existing top-level structure."
  - "CHANGELOG `## [Unreleased]` heading created from scratch — it didn't exist (the file started with `## [1.1.0] - 2026-05-08` per pre-edit live read). Per Keep-a-Changelog convention (which the project's preamble explicitly cites), in-flight v1.2 work goes under `## [Unreleased]`."
  - "fr/CHANGELOG.md left UNTOUCHED (Phase 20 / OPS-04 territory per CONTEXT § Deferred Ideas). The English `> Consultez la version française dans fr/CHANGELOG.md` blockquote in the preamble is also OPS-04 territory and was not modified."

patterns-established:
  - "Aspirational-refs audit-then-positive-add pattern: when the pre-edit sweep returns ZERO hits, skip the rewrite scope and execute as positive-add only — saves the verifier from chasing rewrites that don't exist. The post-edit sweep should return all-qualified hits in proximity to `(blocking)` / `(warning, ...)` / `enforced by CI` / `make doc-gates` wording."
  - "Phase boundary respect: a Phase 13 plan touches PUBLIC docs only (README, CHANGELOG); `.planning/` files (STATE, MILESTONES, PROJECT) update through the orchestrator's `update_state` flow, NOT as part of the per-plan reformulation pass (D-12 enforcement). Verified via `git diff --stat HEAD~2..HEAD -- '.planning/'` returning empty."

requirements-completed:
  - OPS-01
  - OPS-02

# Metrics
duration: "~3min"
completed: 2026-05-08
---

# Phase 13 Plan 05: README + CHANGELOG positive-add reformulation Summary

**Closes OPS-01 / OPS-02 traceability in public docs via a positive-add (NOT a rewrite): the pre-edit aspirational-refs sweep returned ZERO hits across `CHANGELOG.md`, `README.md`, `CONTRIBUTING.md`, `UPGRADING.md`, `docs/source/`, so this plan only adds new qualified claims (`(blocking)`, `(warning, blocking from v1.2.0)`, `enforced by CI`). Lands the README `### Documentation Quality Gates` sub-section + the CHANGELOG `## [Unreleased] / ### Added` entry citing `(OPS-01, OPS-02)`. Phase 13 acceptance gate is now ready for `/gsd-verify-work 13`.**

## Performance

- **Duration:** ~3 min active (2 tasks, both byte-identical to PATTERNS.md spec)
- **Started:** 2026-05-08T17:52:56Z
- **Completed:** 2026-05-08T17:55:42Z
- **Tasks:** 2 / 2
- **Files modified:** 2

## Accomplishments

### Task 1 — README `### Documentation Quality Gates` positive-add

Pre-edit sweep verified empty (zero hits across all five public-doc paths), so the action ran as a positive-add. New sub-section landed under the existing `## Documentation` heading, BEFORE `## Requirements`:

```markdown
### Documentation Quality Gates

Documentation quality is enforced by CI on every push:

- **`interrogate ≥95%`** (blocking) — every public function, class, and module has a docstring.
- **`numpydoc validate`** (warning, blocking from v1.2.0) — docstrings follow the NumPy convention.

Run both locally before pushing: `make doc-gates`.
```

- **`(blocking)`** qualifier on interrogate: backed by Plan 02's CI step (commit `f262eff`) — `Doc coverage gate (interrogate ≥95%)` runs on Python 3.13 with no `continue-on-error`, so a sub-95% score fails the build.
- **`(warning, blocking from v1.2.0)`** qualifier on numpydoc: backed by Plan 04's CI step (commit `1ec5ce5`) — `Doc style audit (numpydoc — warning only, blocking from v1.2.0)` runs with `continue-on-error: true`. The Phase 20 forward-note YAML comment Plan 04 landed makes the flip-target explicit.
- **`make doc-gates`**: backed by Plan 02's Makefile target (commit `8be808d`) — runs interrogate (blocking) + numpydoc (warning, `|| true`) on the same exclusion list as the CI steps.
- **Top-level section ordering preserved:** `grep -n "^## " README.md` shows the same 17 top-level sections in the same order (Documentation → Requirements → Supported bodies → ... → Roadmap → ...). The new section is `###` (sub-section), not `##` (top-level), so the README's high-level table-of-contents is unchanged.

### Task 2 — CHANGELOG `## [Unreleased] / ### Added` entry

The pre-edit CHANGELOG had no `## [Unreleased]` heading — the file started directly with `## [1.1.0] - 2026-05-08`. Plan 05 created the heading and added a single `### Added` bullet under it:

```markdown
## [Unreleased]

### Added

- **CI doc-quality gates** — `interrogate ≥95%` (blocking) and
  `numpydoc validate` (warnings, blocking from v1.2.0) are now wired
  into `tests.yml`. New `[project.optional-dependencies].dev` group
  installs both tools (`pip install -e .[dev]`); `make doc-gates`
  runs the full suite locally. (OPS-01, OPS-02)
```

- **`(OPS-01, OPS-02)` parenthetical** matches the existing entry-shape convention used throughout `## [1.1.0]` (e.g. `(HOU-02 .. HOU-10)` line 69, `(Phase 9 / ASP-04)` line 21, `(Phase 11 / CLI-03)` line 153).
- **`## [Unreleased]` heading** follows Keep-a-Changelog (project preamble explicitly cites it). Phase 20 will rename to `## [1.2.0] - YYYY-MM-DD` at release time — captured in the forward note below.
- **Preamble (lines 1-8) untouched:** `# Changelog` + `> Consultez la version française dans fr/CHANGELOG.md` + the "All notable changes…" paragraph + the Keep-a-Changelog reference paragraph all intact.
- **Existing `## [1.1.0]` block untouched:** `git diff CHANGELOG.md | grep -E "^[+-].*\[1\.1\.0\]"` shows zero modifications inside the [1.1.0] section. The diff is **+10 / -0**.

### Final aspirational-refs sweep (post-edit)

Re-ran the same sweep across all five public-doc paths after both edits landed:

```
CHANGELOG.md:14:- **CI doc-quality gates** — `interrogate ≥95%` (blocking) and
CHANGELOG.md:15:  `numpydoc validate` (warnings, blocking from v1.2.0) are now wired
README.md:243:- **`interrogate ≥95%`** (blocking) — every public function, class, and module has a docstring.
README.md:244:- **`numpydoc validate`** (warning, blocking from v1.2.0) — docstrings follow the NumPy convention.
```

- **4 hits, all qualified.** Each match is in proximity to `(blocking)`, `(warning, blocking from v1.2.0)`, `(warnings, blocking from v1.2.0)`, OR is part of the new "Documentation quality is enforced by CI on every push:" lead paragraph in README. **Zero bare aspirational claims.**
- `CONTRIBUTING.md`, `UPGRADING.md`, `docs/source/` — zero hits (unchanged from pre-edit, as expected since Plan 05 only modifies README + CHANGELOG).

### Runtime sanity gates (post-edit)

- `python -m interrogate ketu/` — exit 0, score **100.0%** (≥95% threshold).
- `python -m pytest tests/ -q --no-cov` — **724 tests pass** (40 expected RuntimeWarnings on `np.divide`, all pre-existing).
- `python -m mypy ketu/ --strict` — `Success: no issues found in 40 source files`.
- `make doc-gates` — exit 0. Numpydoc surfaces ~100 warnings (deferred from Plan 04 to Phase 20 per its SUMMARY); the `|| true` intercepts them and the final `@echo` confirms the warning-only posture.

## Task Commits

Each task was committed atomically (worktree mode, `--no-verify` per parallel-executor protocol):

1. **Task 1: add Documentation Quality Gates section to README** — `f90408a` (docs)
2. **Task 2: add Unreleased CI doc-quality gates entry to CHANGELOG** — `6c144e1` (docs)

This SUMMARY.md is committed as a separate metadata commit by this agent before handoff.

## Files Created/Modified

| File | Lines added | Lines removed | Nature |
| --- | --- | --- | --- |
| `README.md` | +9 | 0 | New `### Documentation Quality Gates` sub-section under `## Documentation` |
| `CHANGELOG.md` | +10 | 0 | New `## [Unreleased] / ### Added` entry citing `(OPS-01, OPS-02)` |

**Diff scope sanity check:**
- `git diff --stat HEAD~2..HEAD` returns exactly two entries (CHANGELOG.md +10, README.md +9) — total `+19 / -0`.
- `git diff --stat HEAD~2..HEAD -- '.planning/'` returns empty (D-12 enforced).
- `git diff --stat HEAD~2..HEAD -- 'fr/'` returns empty (Phase 20 / OPS-04 boundary respected).
- `git diff --stat HEAD~2..HEAD -- 'ketu/'` returns empty (no source changes — Plans 01-04 own all source edits).

## Decisions Made

- **Plan executed verbatim — zero design decisions re-opened.** Both PATTERNS.md text blocks landed byte-for-byte. The plan's `<action>` sections specified placement, exact wording, and constraints — execution applied them mechanically.
- **README sub-section (`###`), not top-level (`##`).** The plan's Step 2 was explicit on this: `### Documentation Quality Gates` is conceptually a sub-topic under `## Documentation`, and using `###` preserves the README's top-level outline. Verified via `grep -n "^## " README.md` — same 17 top-level sections in the same order before and after.
- **`## [Unreleased]` rather than `## [1.2.0] - YYYY-MM-DD`.** Phase 13 is mid-milestone (Phase 20 is release prep); pinning a date now would be wrong. Keep-a-Changelog `## [Unreleased]` is the canonical staging heading. Phase 20 plan author renames it at release.
- **`fr/CHANGELOG.md` and the `> Consultez la version française` blockquote left untouched.** Both are OPS-04 (Phase 20) territory per CONTEXT § Deferred Ideas. Mixing OPS-04 work into a Phase 13 plan would have re-opened a closed scope.
- **`.planning/config.json` was already modified in the worktree before Plan 05 started** (a `granularity` key reorder, unrelated to my work). I did not stage it. D-12 strict enforcement means Plan 05 only writes to README, CHANGELOG, and this SUMMARY.md — never to other `.planning/` files.

## Deviations from Plan

None — plan executed exactly as written.

The IDE flagged an MD024/no-duplicate-heading lint warning at line 69 of CHANGELOG.md after Task 2. This is a pre-existing artifact of Keep-a-Changelog convention: the existing `## [1.1.0]` block already contains multiple `### Added` headings (Plans 1.1 staged its work as 4 separate `### Added` sub-blocks). My new `### Added` under `## [Unreleased]` follows the same documented pattern and is structurally correct. No action taken — the warning is a textual lint artifact, not a structural defect, and matches the project's existing convention.

## Issues Encountered

None. The pre-edit sweep returning empty (the planning team had already verified this live 2026-05-08) meant the entire plan executed as positive-add — no rewrite scope expansion was needed.

## Forward note for Phase 20 plan author

When Phase 20 lands the v1.2.0 release-prep tasks, the planner MUST coordinate the following atomic flips:

1. **Rename `## [Unreleased]` to `## [1.2.0] - YYYY-MM-DD`** in `CHANGELOG.md`. The single `### Added` entry under it is already correctly formed and traceable (`OPS-01, OPS-02`); no content edits needed. Add additional `### Added / ### Changed / ### Fixed` blocks to capture Phases 14-19 work as those phases land.
2. **Bump version** in `pyproject.toml` (`[project].version`) and `ketu/__init__.py` (`__version__`) to `1.2.0`.
3. **Remove `continue-on-error: true`** from the `Doc style audit (numpydoc — warning only, blocking from v1.2.0)` step in `.github/workflows/tests.yml` (and rename the step to drop "warning only" — suggested: `Doc style audit (numpydoc — blocking)`). Remove the leading 3-line YAML comment block (its job is done once the flip is committed).
4. **Remove `"GL01"`** from `[tool.numpydoc_validation].checks` in `pyproject.toml`.
5. **Run a mechanical fix-pass** on the deferred work documented in Plan 03 / Plan 04 SUMMARYs: ~59 GL01 hits (from Plan 03 D-14) + 100 SS03/PR09/RT05/RT01/PR01/PR08 hits (from Plan 04 deferred-issues table) + 2 GL06/GL07 in `ketu/aspects/presets.py` + 1 GL08 in `ketu/ephemeris/planets.py:302`. After the fix-pass, `python -m numpydoc lint $(find ketu -name "*.py" ! -path "*/__pycache__/*" ! -name "lunar_calendar.py" ! -name "_*.py")` MUST produce zero output.
6. **`fr/CHANGELOG.md` reformulation pass (OPS-04)** — remove or update the `> Consultez la version française dans fr/CHANGELOG.md` blockquote in `CHANGELOG.md` based on the OPS-04 decision; mirror the v1.2 `### Added` entry into `fr/CHANGELOG.md` if the file is kept. This Phase 13 plan deliberately did NOT touch either file (Deferred Idea per CONTEXT).

## Path Forward for Phase 13 Verifier

**Phase 13 acceptance gate is now ready for `/gsd-verify-work 13`.** The four ROADMAP success criteria all map to landed work:

- **13.1 (interrogate ≥95% blocking):** Plan 02 wired the CI step (commit `f262eff`); Plan 01 brought the codebase to 100% baseline. Plan 05's README `(blocking)` qualifier is now factual.
- **13.2 (numpydoc validate warning-only):** Plan 04 wired the CI step (commit `1ec5ce5`) with `continue-on-error: true` and the Phase 20 flip-target YAML comment. Plan 05's README `(warning, blocking from v1.2.0)` qualifier is now factual.
- **13.3 (aspirational refs reformulated):** Plan 05 — pre-edit sweep returned empty; positive-add of qualified claims landed in README + CHANGELOG; post-edit sweep confirms all 4 matches are qualified. **Closed by this plan.**
- **13.4 (gates produce a clean baseline on v1.1):** Plan 01 fixed the 4 placidus interrogate gaps; Plan 03 fixed ~115 numpydoc gaps in its declared 9-file scope. `python -m interrogate ketu/` now reports 100.0%; `python -m pytest tests/ -q --no-cov` passes 724/724.

The verifier should also confirm:
- `git diff --stat HEAD~5..HEAD -- '.planning/'` returns empty across all five Plan 13 commits (D-12).
- `git diff --stat HEAD~5..HEAD -- 'fr/'` returns empty (Phase 20 / OPS-04 boundary).
- `make doc-gates` exits 0 locally with the warning posture working as designed (numpydoc warnings printed, build green).

## Self-Check: PASSED

Verified after writing SUMMARY:

- `README.md` contains the new section: `grep -c "^### Documentation Quality Gates$" README.md` returns `1`.
- `grep -A8 "^### Documentation Quality Gates$" README.md` contains all five required substrings: `interrogate ≥95%`, `(blocking)`, `numpydoc validate`, `(warning, blocking from v1.2.0)`, `make doc-gates`.
- README top-level ordering preserved: `Documentation` (line 226) → `Requirements` (line 248) → `Supported bodies` (line 255) → ... — same as pre-edit.
- `CHANGELOG.md` contains the new heading: `grep -c "^## \[Unreleased\]$" CHANGELOG.md` returns `1`.
- `grep -A8 "^## \[Unreleased\]$" CHANGELOG.md` contains all four required substrings: `CI doc-quality gates`, `interrogate ≥95%`, `numpydoc validate`, `(OPS-01, OPS-02)`.
- CHANGELOG ordering: `awk '/^## \[/{print NR": "$0}' CHANGELOG.md | head -3` shows `Unreleased` (line 10) → `[1.1.0]` (line 20) → `[1.0.0]` (line 172) — correct chronological order.
- CHANGELOG preamble unchanged: `head -8 CHANGELOG.md` is byte-identical to the pre-edit version.
- Commit `f90408a` (Task 1, docs) present in `git log`.
- Commit `6c144e1` (Task 2, docs) present in `git log`.
- D-12 enforcement: `git diff --stat HEAD~2..HEAD -- '.planning/'` returns empty.
- Phase 20 / OPS-04 boundary: `git diff --stat HEAD~2..HEAD -- 'fr/'` returns empty.
- Final aspirational sweep: 4 matches across CHANGELOG + README, ALL qualified (in proximity to `(blocking)`, `(warning, ...)`, or `enforced by CI` wording). Zero bare claims.
- Runtime sanity: `interrogate` 100.0% (≥95%); 724 pytest tests pass; `mypy --strict` clean; `make doc-gates` exit 0.

---
*Phase: 13-doc-gates-and-ci-foundation*
*Completed: 2026-05-08*
