---
phase: 12-release-preparation-v1-1-0
plan: 03
subsystem: docs
tags: [upgrading, migration, release-notes, cli, kala-adapter, houses, stderr]

# Dependency graph
requires:
  - phase: 09-configurable-aspects
    provides: "CLI default shift EXTENDED -> CLASSICAL (ASP-04) and resolved-config stderr header (CLI-06 surface)"
  - phase: 10-houses-module
    provides: "ketu.calculate_houses + house_of + HOUSES_DTYPE replacing the broken ketu.ephemeris.calculate_house_cusps placeholder (HOU-10)"
  - phase: 11-cli-refactor-integration
    provides: "shipped --harmonics, --list-aspect-sets, --list-house-systems flags + ketu houses subcommand (CLI-01..CLI-06)"
  - phase: 08-lilith-calibration
    provides: "Lilith formula re-fit (already documented byte-identical in UPGRADING.md pre-edit)"
provides:
  - "UPGRADING.md migration recipes for CLI default aspect shift (script users)"
  - "UPGRADING.md migration recipes for downstream-adapter Kala / KetuDataAdapter style consumers"
  - "UPGRADING.md migration recipes for the Houses Module (replacing removed ketu.ephemeris.calculate_house_cusps)"
  - "UPGRADING.md note about the new # Aspect set: / # House system: stderr header"
  - "Closure of REL-03 (UPGRADING completion) on the Phase 12 release-prep checklist"
affects: [12-04-release-publish, kala-downstream]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Migration recipes: paired CLI + Python API blocks for every breaking surface, never prose-only"
    - "Recipes verified against shipped code (parser.py, formatters.py, ketu/__init__.py exports) before authoring, not against RESEARCH-time sketches"

key-files:
  created:
    - ".planning/phases/12-release-preparation-v1-1-0/12-03-SUMMARY.md"
  modified:
    - "UPGRADING.md (+134 / -4 — replaced single misleading subsection with four substantive ones)"

key-decisions:
  - "Recipe authored against shipped reality, not RESEARCH speculation: registered house systems are placidus/koch/porphyry only (NOT equal/whole_sign), houses subcommand uses --date ISO (NOT --jd), and the stderr header includes aspect names + degrees (Conjunction 0°, …) NOT just bare angles"
  - "Lilith subsection content held byte-identical to pre-edit state per must_haves contract — only the trailing 'Other v1.0 -> v1.1 Changes' block was replaced"
  - "Atomic single-file commit (UPGRADING.md only) — pre-existing dirty state on STATE.md / config.json / earlier-phase PLAN.md files left untouched per plan scope"

patterns-established:
  - "Verify recipe APIs (CLI flags, Python imports, default values) against the live codebase via grep BEFORE writing migration prose"
  - "Always pair CLI recipe with Python API recipe so both audiences (shell scripters, library consumers) get a runnable snippet"

# Metrics
duration: 3min
completed: 2026-05-08
---

# Phase 12 Plan 03: UPGRADING Completion Summary

**Closes REL-03 by replacing the single misleading "backward-compatible" sentence with four substantive migration subsections (CLI default, Kala adapter, Houses Module, stderr header) — Lilith content held byte-identical.**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-05-07T22:36:06Z
- **Completed:** 2026-05-07T22:39:02Z
- **Tasks:** 2
- **Files modified:** 1 (`UPGRADING.md`)

## Accomplishments

- Removed the misleading sentence claiming "configurable aspects, houses module, CLI refactor is backward-compatible" (it was wrong — Phase 9 deliberately shifted CLI default from EXTENDED to CLASSICAL, which is ~64% fewer aspect rows per body pair).
- Added explicit migration recipe for CLI users: `ketu --harmonics extended aspects --date <ISO>` to restore v1.0 behavior, plus `ketu --list-aspect-sets` for discoverability and a `pip install 'ketu<1.1'` pin-not-migrate escape hatch.
- Added explicit Python API recipe: `from ketu.aspects.presets import EXTENDED; calculate_aspects(jd, bodies, aspects=EXTENDED)`.
- Added Kala / downstream adapter recipe (text-only — Kala is a sibling repo, not modified from here) using `calculate_aspects_batch(..., aspects=EXTENDED)`.
- Added Houses Module recipe replacing the removed v1.0 placeholder `ketu.ephemeris.calculate_house_cusps` with the new `ketu.calculate_houses` + `ketu houses` CLI subcommand.
- Added Resolved-Config stderr Header note documenting the new `# Ketu v1.1.0` / `# Aspect set: …` / `# House system: …` lines on stderr.

## Task Commits

Each task was committed atomically:

1. **Task 1+2: UPGRADING.md migration recipes** — `aaa706c` (`docs(12-03): add CLI / Kala / houses / stderr migration recipes to UPGRADING.md`)

_Note: Task 1 (Edit) and Task 2 (verify + commit) collapsed into a single atomic commit per the plan's `<action>` for Task 2 (Task 1 had no commit step — it staged the edit; Task 2 ran `git status` and committed)._ The verification gates from Task 1 were executed before the commit and all passed.

## Files Created/Modified

- `UPGRADING.md` — Replaced the three-line "Other v1.0 -> v1.1 Changes" subsection (the misleading "backward-compatible" claim) with four new H3 subsections totalling ~130 lines: "CLI Default Aspect Set", "Kala / Downstream Adapter Migration", "Houses Module", "Resolved-Config stderr Header". Lilith section held byte-identical.
- `.planning/phases/12-release-preparation-v1-1-0/12-03-SUMMARY.md` — This file.

## Decisions Made

- **Phase 11 CLI flag confirmed as `--harmonics` (not `--aspect-set`)** by grepping `ketu/cli/parser.py:64` — recipes use `--harmonics extended`, no aliases. The plan asked us to verify which flag was canonical; `--harmonics` is the only one defined.
- **Stderr header format updated to match shipped code.** Plan's draft recipe had `# Aspect set: classical (5 aspects: 0, 60, 90, 120, 180)`. Live code (`ketu/cli/formatters.py:50-53`) and a captured CLI invocation produce `# Aspect set: classical (5 aspects: Conjunction 0°, Sextile 60°, Square 90°, Trine 120°, Opposition 180°)`. Recipe was corrected to the shipped form so users diffing against actual stderr see a match.
- **Houses CLI recipe uses `--date ISO`, not `--jd`.** `ketu/cli/parser.py:113-117` defines `--date` (UTC ISO 8601) for the houses subcommand; there is no `--jd` flag. Recipe corrected from the plan's sketch (`--jd 2451545.0`) to `--date 2000-01-01T12:00:00Z`.
- **House systems list trimmed to shipped reality.** `ketu/houses/__init__.py:41-43` registers exactly `placidus`, `koch`, `porphyry`. Plan's draft listed `equal` and `whole_sign` — those are NOT registered in v1.1 (only mentioned in registry.py docstring as a generic example). Recipe corrected to list only the three actually-registered systems and added a parenthetical noting `equal` / `whole_sign` are not yet registered.
- **Lilith content not re-rendered.** Per `must_haves.truths`, the well-written Lilith section (per-date table, formula constants, post-fix accuracy bullets, action-required paragraph) must remain byte-identical. The Edit `old_string` deliberately scoped to just the trailing "Other v1.0 -> v1.1 Changes" subsection; nothing above it was touched. Sentinel-string greps (`MAX |delta| = 179.936579 deg`, `Recompute any cached Lilith values`, `0.002693 deg`) confirm preservation.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Stderr header format mismatch with shipped code**
- **Found during:** Task 1 (pre-write verification grep against `ketu/cli/formatters.py`)
- **Issue:** Plan's draft recipe showed `# Aspect set: classical (5 aspects: 0, 60, 90, 120, 180)` (bare angles). Shipped formatter produces `# Aspect set: classical (5 aspects: Conjunction 0°, Sextile 60°, Square 90°, Trine 120°, Opposition 180°)` (named aspects + degree symbols). A user diffing the recipe against actual CLI output would mismatch.
- **Fix:** Updated the example block in the "Resolved-Config stderr Header" subsection to use the shipped format verbatim.
- **Files modified:** `UPGRADING.md`
- **Verification:** Captured live stderr via `python -m ketu aspects --date 2026-05-07T12:00:00Z 2>&1 1>/dev/null` and matched against the recipe block.
- **Committed in:** `aaa706c`

**2. [Rule 1 - Bug] Houses CLI recipe used non-existent `--jd` flag**
- **Found during:** Task 1 (pre-write verification grep against `ketu/cli/parser.py`)
- **Issue:** Plan's draft recipe showed `ketu houses --jd 2451545.0 --lat 48.85 --lon 2.35 --system placidus`. The actual `p_houses` parser defines `--date ISO` (line 113-117), not `--jd`. The recipe would fail with `argparse: unrecognized arguments: --jd`.
- **Fix:** Changed `--jd 2451545.0` to `--date 2000-01-01T12:00:00Z` (same epoch, JD 2451545.0 ↔ J2000.0 noon UTC).
- **Files modified:** `UPGRADING.md`
- **Verification:** `grep -n "add_argument" ketu/cli/parser.py` confirmed `--date` is the only date-input flag for the houses subcommand; the recipe is now runnable as written.
- **Committed in:** `aaa706c`

**3. [Rule 1 - Bug] House systems list overstated v1.1 surface**
- **Found during:** Task 1 (verification grep over `ketu/houses/__init__.py` registrations)
- **Issue:** Plan's draft prose claimed available systems are `placidus, koch, porphyry, equal, whole_sign`. Only the first three are imported / registered in v1.1; `equal` and `whole_sign` appear only as docstring examples in `registry.py`. A user trying `--system equal` would hit `ValueError: unknown house system 'equal'`.
- **Fix:** Trimmed the list to the three actually-registered systems and added an explicit parenthetical: "the v1.0 broken `equal_fallback` placeholder is gone; `equal` and `whole_sign` are not yet registered". This both prevents user confusion and pre-empts a future doc bug-report.
- **Files modified:** `UPGRADING.md`
- **Verification:** `grep "register" ketu/houses/{placidus,koch,porphyry}.py` returned exactly three `@register("…")` matches.
- **Committed in:** `aaa706c`

---

**Total deviations:** 3 auto-fixed (3 doc-vs-code accuracy bugs, all caught at the recommended pre-write grep gate)
**Impact on plan:** All three deviations strictly improved recipe accuracy — none changed scope, all keep the plan's contract (four substantive subsections, no Lilith touch, atomic single-file commit). Without these fixes the recipes would have been runnable-but-wrong.

## Issues Encountered

- **MD036 lint warnings on emphasis-as-heading** (`**Migration recipe (CLI users)**` etc., lines 119/132/185/201). Intentional — these mirror the existing Lilith section's pattern (`**Root cause:**`, `**Fix:**`, `**Action required:**`) which the plan explicitly required to remain byte-identical. Promoting them to `####` headings would introduce inconsistency with the already-present Lilith style. Linter warnings left as-is; this is a stylistic preference for paragraph-leading emphasis labels, not a functional defect.
- **MD038 lint warning on `` `^# ` `` (trailing space inside code span)** at line 230. The trailing space is *load-bearing* — it's the literal grep regex pattern matching the resolved-config header lines (which all start with `"# "`, two characters). Removing the space would make the documented pattern semantically wrong. Left as-is.

## Verification Notes

- **Misleading sentence located at line 104 of pre-edit UPGRADING.md** ("is backward-compatible. See per-feature documentation…"). After the edit, `grep -q "is backward-compatible" UPGRADING.md` returns non-zero (phrase removed). Confirmed.
- **Phase 11 canonical CLI flag is `--harmonics`** (verified via `grep -nE "add_argument.*--harmonics|add_argument.*--aspect-set" ketu/cli/parser.py` → exactly one match for `--harmonics` at line 64-76, zero for `--aspect-set`). All four recipe blocks use `--harmonics`.
- **Diff stat:** 1 file changed, 134 insertions, 4 deletions (close to the plan's predicted ~110-130 / ~5-7; the extra ~10 insertions come from the three deviation-fix annotations: stderr header expansion to named aspects, `--date` vs `--jd` example correction, parenthetical on un-registered house systems).
- **Heading + code-fence balance** (Task 2 sub-step 2): h2=11, h3=13, h4=2; 34 fences (balanced). All assertions passed.
- **Single-file commit confirmed:** `git show --stat HEAD` lists exactly `UPGRADING.md`. The pre-existing dirty state (`.planning/config.json`, prior-phase `*-PLAN.md` edits, `CHANGELOG.md`) was deliberately NOT staged — it is outside this plan's scope.

## User Setup Required

None — documentation-only change.

## Next Phase Readiness

- **REL-03 closed.** UPGRADING.md now provides explicit migration recipes for all three breaking surfaces (Lilith already done pre-edit, CLI default + houses + stderr header newly added) plus downstream-adapter guidance for Kala and similar consumers.
- **Plan 12-04 (release-publish) unblocked.** UPGRADING.md is in a publishable state for the v1.1.0 release; CHANGELOG.md (Plan 12-02) and version sync (Plan 12-01) remain as the other two prerequisites. None of those overlap with this plan's scope.
- **No new blockers.** No Kala-side changes required from this repo (recipe is text-only guidance for the sibling project's maintainer to apply on their own schedule).

## Self-Check: PASSED

Verified after writing this SUMMARY.md:

- `UPGRADING.md` modified file: FOUND (134 insertions / 4 deletions confirmed via `git show --stat HEAD`)
- Commit `aaa706c`: FOUND (`git log --oneline -1` → `aaa706c docs(12-03): add CLI / Kala / houses / stderr migration recipes to UPGRADING.md`)
- All 13 phase-level verification grep checks pass (run after commit, see Bash output above)
- Lilith sentinel strings present (3/3): `MAX |delta| = 179.936579 deg`, `Recompute any cached Lilith values`, `0.002693 deg`
- Misleading phrase absent: `! grep -q "is backward-compatible" UPGRADING.md` returns 0

---
*Phase: 12-release-preparation-v1-1-0*
*Completed: 2026-05-08*
