---
phase: 12-release-preparation-v1-1-0
plan: 02
subsystem: docs
tags: [changelog, release-notes, readme, pypi, v1.1.0]

# Dependency graph
requires:
  - phase: 08-lilith-verification-and-fix
    provides: Lilith Mean Apogee correction (already documented in CHANGELOG before this plan)
  - phase: 09-configurable-aspects
    provides: CLI default flip EXTENDED -> CLASSICAL (newly documented here)
  - phase: 10-houses-module
    provides: ketu.houses module + HOU-10 removal (already documented in CHANGELOG before this plan)
  - phase: 11-cli-refactor-integration
    provides: argparse CLI, subcommands, --harmonics, --list-* introspection, stderr config header, byte-stability fixture (newly documented here)
provides:
  - CHANGELOG.md [1.1.0] BREAKING / Numerical Behavior Changes (Summary) section enumerating the 3 user-visible breaks
  - CHANGELOG.md [1.1.0] dedicated `### Changed (BREAKING)` entry for Phase 9 CLI default flip
  - CHANGELOG.md [1.1.0] dedicated `### Added` entry for Phase 11 CLI refactor (subcommands + flags + stderr header + byte-stability regression)
  - README.md "What's New in v1.1.0" banner replacing the v1.0.0 banner
affects: [12-03-upgrading-completion, 12-04-release-publish]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Anchored Edit insertions on Markdown headings preserve unchanged prose byte-for-byte"
    - "Surgical README banner replacement leaves dynamic PyPI badges + structural sections (Features, Installation, ...) untouched"

key-files:
  created: []
  modified:
    - "CHANGELOG.md (3 insertion blocks in [1.1.0] section: BREAKING summary, Phase 9 Changed (BREAKING), Phase 11 Added)"
    - "README.md (lines 13-24 replaced with v1.1.0 banner; rest untouched)"

key-decisions:
  - "Used `ketu --harmonics extended` as the v1.0-restore recipe (matches actual Phase 11 CLI flag wired in ketu/cli/parser.py line 65)"
  - "Phase 11 CLI surface area placed in a SECOND `### Added` block (Keep a Changelog allows multiple ### Added subsections per release) rather than merging with the existing Lilith-related `### Added`"
  - "Replaced README block-quote `## Houses module — ... Equal, and Whole-Sign systems` with `Placidus, Koch, and Porphyry systems` — the plan's reference text overstated v1.1 surface; Phase 10 only shipped 3 systems"
  - "Replaced trailing `^# ` code-span filter (lint MD038 violation: trailing space in inline code) with prose `lines starting with #` — semantically equivalent"

patterns-established:
  - "Anchor lines for [1.1.0] header (`## [1.1.0] - UNRELEASED`) at line 10 — Plan 12-04 date-stamp Edit will target this exact string"
  - "Multi-block ### Added per release section is valid Keep-a-Changelog and used here"

# Metrics
duration: 3m 42s
completed: 2026-05-08
---

# Phase 12 Plan 02: Changelog Completion Summary

**CHANGELOG.md `[1.1.0]` gains a 3-bullet rolled-up BREAKING summary, a Phase 9 `### Changed (BREAKING)` entry, and a Phase 11 `### Added` entry covering the argparse CLI refactor; README.md "What's New" banner flips to v1.1.0.**

## Performance

- **Duration:** 3m 42s
- **Started:** 2026-05-07T22:36:19Z
- **Completed:** 2026-05-07T22:40:01Z
- **Tasks:** 3 (Task 1 CHANGELOG, Task 2 README, Task 3 validate+commit)
- **Files modified:** 2 (CHANGELOG.md, README.md)

## Accomplishments

- **Closed REL-02 success criterion 2 verbatim** — `### BREAKING / Numerical Behavior Changes (Summary)` section names all 3 v1.0 -> v1.1 user-visible behavior changes (CLI default, Lilith, houses) with cross-references to UPGRADING.md.
- **Closed RESEARCH.md "What is MISSING" gap 1** — Phase 9 CLI default flip (EXTENDED -> CLASSICAL) now has its own `### Changed (BREAKING)` entry with restore recipe `ketu --harmonics extended` and discovery flag `ketu --list-aspect-sets`.
- **Closed RESEARCH.md "What is MISSING" gap 2** — Phase 11 CLI refactor surface documented: `ketu aspects` / `ketu houses` subcommands, `--harmonics`, `--list-aspect-sets`, `--list-house-systems`, resolved-config stderr header, byte-stability regression test (sha256 `067fa67672d2e3c727a30612364e4b9bb1699401768f4a8fc4819a0e951785ed`).
- **Closed RESEARCH.md Open Question 4** — README.md "What's New" banner now advertises v1.1.0; PyPI long_description (rendered via `twine check` in 12-04) banners v1.1, not v1.0.
- **`UNRELEASED` placeholder INTACT** — `## [1.1.0] - UNRELEASED` at line 10 of CHANGELOG.md is unchanged; date stamp deferred to Plan 12-04 Task 1 per RESEARCH.md Pitfall 2.

## Task Commits

All three tasks were combined into a single atomic commit per Task 3's plan-specified protocol (`docs(12-02): finish CHANGELOG v1.1.0 + update README What's New`).

1. **Task 1: Insert CHANGELOG sections** — folded into the unified commit
2. **Task 2: Update README "What's New"** — folded into the unified commit
3. **Task 3: Validate, lint, and commit** — `cd16bcf` (docs)

**Single commit:** `cd16bcf` — touches exactly `CHANGELOG.md` + `README.md` (94 insertions, 11 deletions).

## Files Created/Modified

- `CHANGELOG.md` — 65 net insertions in `[1.1.0]` section:
  - **Insertion 1** (lines 12-30): `### BREAKING / Numerical Behavior Changes (Summary)` rolled-up 3-bullet list
  - **Insertion 2** (lines 45-57): `### Changed (BREAKING)` Phase 9 CLI default flip entry, between existing `### Removed (BREAKING)` (HOU-10) and existing `### Added` (ketu.houses module)
  - **Insertion 3** (lines 124-153): `### Added` Phase 11 CLI refactor entry, between existing Lilith-related `### Added` (ending with pysweph bullet) and `### Migration`
  - All Lilith (Phase 8) and houses (Phase 10) prose preserved byte-for-byte outside the inserted blocks
- `README.md` — 40 lines inserted, 11 lines deleted; only the "What's New" block (lines 13-24 of original) was replaced; PyPI badges (lines 3-5), screenshot (line 11), `## Features` and below entirely untouched

## Anchor Lines (for Plan 12-04 date stamp)

After this plan, the following anchor lines exist in `CHANGELOG.md`:

| Line | Content                                                  | Purpose                                                                  |
| ---- | -------------------------------------------------------- | ------------------------------------------------------------------------ |
| 10   | `## [1.1.0] - UNRELEASED`                                | **Plan 12-04 Task 1 anchor** — replace `UNRELEASED` with release date    |
| 12   | `### BREAKING / Numerical Behavior Changes (Summary)`    | Roll-up summary (Plan 12-02 Insertion 1)                                 |
| 32   | `### Removed (BREAKING)`                                 | HOU-10 (pre-existing, unchanged)                                         |
| 45   | `### Changed (BREAKING)`                                 | Phase 9 CLI default flip (Plan 12-02 Insertion 2)                        |
| 59   | `### Added`                                              | ketu.houses module (pre-existing, unchanged)                             |
| 102  | `### Added`                                              | Lilith definition + harness + pysweph (pre-existing, unchanged)          |
| 124  | `### Added`                                              | Phase 11 CLI refactor (Plan 12-02 Insertion 3)                           |
| 155  | `### Migration`                                          | Pre-existing, unchanged                                                  |
| 162  | `## [1.0.0] - 2026-02-12`                                | Sentinel — Plan 12-04 must NOT touch anything below this line            |

`README.md` anchors:

| Line | Content                                | Purpose                                                                |
| ---- | -------------------------------------- | ---------------------------------------------------------------------- |
| 13   | `## What's New in v1.1.0`              | Replaced from `## What's New in v1.0.0` (Plan 12-02 Task 2)            |
| 43   | `## Features`                          | Sentinel — sections below untouched                                    |

## Local Render Gate

`readme_renderer[md]` was **available locally** after `python -m pip install --quiet 'readme_renderer[md]'` in the venv (the bare `readme_renderer` package was already present, but lacks markdown support without the `[md]` extra — installation took ~2s). README rendered cleanly: 27,454 chars HTML output, no warnings, no errors.

**Implication for Plan 12-04:** `twine check dist/*` is **NOT the first render gate** — Plan 12-02 already validated the markdown locally. `twine check` in 12-04 is a redundant safety net catching any post-build packaging issues, not a first-time validation.

## Decisions Made

- **`ketu --harmonics extended` (not `--aspect-set EXTENDED`)** as the v1.0-restore recipe. Verified via `grep -n "add_argument.*harmonics" ketu/cli/parser.py` returning line 65 + `parse_harmonics_spec` (line 18) which accepts `"classical" | "traditional" | "extended" | "all"` (case-insensitive) AND comma-separated indices. The parser does NOT expose a `--aspect-set` flag; the public CLI flag is `--harmonics` exclusively.
- **Phase 11 entry in a SECOND `### Added` block** rather than merging with the existing Lilith-related `### Added` (lines 102-122). Keep a Changelog 1.0.0 spec allows multiple `### Added` subsections per release; this preserves the existing pre-Plan-12-02 Lilith block byte-for-byte and groups the Phase 11 surface area under its own heading.
- **Replaced inline code-span trailing-space filter** (`` `^# ` ``) with prose ("lines starting with `#`"). The trailing space in the original draft triggered MD038/no-space-in-code lint warning at line 146. Semantically equivalent — both refer to the resolved-config header pattern.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan reference text for README "Houses module" bullet listed 5 systems; Phase 10 only shipped 3**

- **Found during:** Task 2 (README "What's New" rewrite)
- **Issue:** Plan reference text said `with Placidus, Koch, Porphyry, Equal, and Whole-Sign systems`; Phase 10 SUMMARY (`10-06-SUMMARY.md`) and `ketu/houses/__init__.py` only register 3 systems via `from . import placidus, koch, porphyry`. Equal House and Whole-Sign systems are NOT in the v1.1 codebase. Shipping the 5-system claim in the README would have created a documentation lie.
- **Fix:** Replaced with `with Placidus, Koch, and Porphyry systems` — matches reality, matches CHANGELOG.md `### Added` block at line 59 (which correctly says "Placidus, Koch, and Porphyry house systems").
- **Files modified:** `README.md` (one bullet, ~6 chars net delta)
- **Verification:** `grep -E '^from \. import' ketu/houses/__init__.py` returns the 3 registration imports; CHANGELOG and README now agree.
- **Committed in:** `cd16bcf` (Task 3 atomic commit)

**2. [Rule 1 - Bug] Plan reference draft contained MD038 lint violation (trailing space inside code span)**

- **Found during:** Task 1 Insertion 3 (Phase 11 `### Added` block)
- **Issue:** Plan reference text had `` filter on `^# `. `` — the trailing space inside the inline code span violates Markdown lint MD038 (no-space-in-code). The space is semantically meaningful (the resolved-config header pattern is `# Aspect set: ...`, with a space after `#`), but inline code spans should not have leading or trailing whitespace.
- **Fix:** Replaced with prose `filter lines starting with `#`.` — semantically equivalent and lint-clean.
- **Files modified:** `CHANGELOG.md` (one line, line 146)
- **Verification:** Editor diagnostic cleared; manual readback confirms meaning preserved.
- **Committed in:** `cd16bcf` (Task 3 atomic commit)

**3. [Rule 3 - Blocking] `readme_renderer` was installed without the `[md]` extra**

- **Found during:** Task 3 step 1 (local render gate)
- **Issue:** `python -c "import readme_renderer.markdown; ..."` emitted `UserWarning: Markdown renderers are not available. Install 'readme_renderer[md]' to enable Markdown rendering.` and returned `None`, failing the assertion. Without this fix, the local render gate would have been skipped and the SUMMARY would have had to note "skipped — relying on twine check in 12-04" per the plan's contingency clause.
- **Fix:** `python -m pip install --quiet 'readme_renderer[md]'` (the bare `pip` shim in venv was broken with `ne peut exécuter`, so used `python -m pip` invocation per the standard Python pattern).
- **Files modified:** None — this is venv state, not codebase state.
- **Verification:** Re-ran the same `python -c` snippet — got `OK: README rendered (27454 chars)` with zero warnings.
- **Committed in:** N/A (venv-state change, no commit)

---

**Total deviations:** 3 auto-fixed (2 Rule 1 - Bug, 1 Rule 3 - Blocking)
**Impact on plan:** All three deviations are corrections to plan reference text or environment, not scope changes. The shipped CHANGELOG and README correctly describe the v1.1 software as actually built in Phases 8/9/10/11.

## Authentication Gates

None — this plan was pure documentation editing.

## Issues Encountered

- **Plan verify-grep on `"ketu\.houses module"`** — failed because the existing pre-Plan-12-02 prose has `` **`ketu.houses` module** `` (backticks between, NOT adjacent prose). The grep pattern in the plan's verify block was already wrong against the un-modified CHANGELOG, so this is a plan-text bug, not a deviation from the executed work. The substantive "preserve unchanged" criterion (Lilith and houses content byte-identical outside inserted blocks) IS satisfied — `git diff CHANGELOG.md` shows only insertions in the `[1.1.0]` section, zero deletions or modifications elsewhere. Documented here for transparency; no code action required.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **Plan 12-03 (UPGRADING.md completion)** is unblocked. The CHANGELOG cross-references `UPGRADING.md` from the new BREAKING summary; Plan 12-03 must add the v1.0 -> v1.1 migration recipes for the 3 named breaks (CLI default, Lilith, houses).
- **Plan 12-04 (release publish)** is unblocked. The `## [1.1.0] - UNRELEASED` anchor at line 10 is intact for Plan 12-04 Task 1's date-stamp Edit. The local `readme_renderer[md]` render gate has already validated the README, so `twine check` in Plan 12-04 will be a redundant safety net rather than the first render check.
- **REL-02 closed.** All three Phase 12 RESEARCH-identified CHANGELOG gaps (Phase 9, Phase 11, README banner) are filled. Single atomic commit `cd16bcf` on `gsd/v1.1-milestone`.

---

## Self-Check: PASSED

Verified post-commit:

- `CHANGELOG.md` exists and contains all 13 plan-specified anchor strings (`### BREAKING / Numerical Behavior Changes (Summary)`, `EXTENDED (14) -> CLASSICAL (5)`, `Lilith (Mean Apogee) longitude formula corrected`, `Houses module replaces broken`, `### Changed (BREAKING)`, `ketu --harmonics extended`, `ketu --list-aspect-sets`, `CLI refactor (argparse-based)`, `ketu --list-house-systems`, `067fa67672d2e3c727a30612364e4b9bb1699401768f4a8fc4819a0e951785ed`, `## [1.1.0] - UNRELEASED`, `## [1.0.0] - 2026-02-12`, `approximately 180 deg on every date`).
- `README.md` exists and contains `## What's New in v1.1.0`; does NOT contain `## What's New in v1.0.0`; both `[UPGRADING.md](UPGRADING.md)` and `[CHANGELOG.md](CHANGELOG.md)` links present; `## Features` heading at line 43 untouched.
- Commit `cd16bcf` exists in `git log`, message is `docs(12-02): finish CHANGELOG v1.1.0 + update README What's New`, touches exactly `CHANGELOG.md` + `README.md` (2 files), 94 insertions, 11 deletions.

---
*Phase: 12-release-preparation-v1-1-0*
*Completed: 2026-05-08*
