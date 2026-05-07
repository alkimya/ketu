---
phase: 12-release-preparation-v1-1-0
plan: 02
type: execute
wave: 1
depends_on: []
files_modified:
  - CHANGELOG.md
  - README.md

autonomous: true

must_haves:
  truths:
    - "CHANGELOG.md [1.1.0] section opens with a 'BREAKING / Numerical Behavior Changes (Summary)' rolled-up list naming all three breaking changes (CLI default, Lilith, houses)"
    - "Phase 9 CLI default change EXTENDED -> CLASSICAL is documented in CHANGELOG.md (was missing)"
    - "Phase 11 CLI refactor (new subcommands, new flags, stderr resolved-config header) is documented in CHANGELOG.md (was missing)"
    - "Existing CHANGELOG content for Lilith (Phase 8) and houses (Phase 10) is preserved unchanged"
    - "README.md 'What's New' section header references v1.1.0 (was v1.0.0) with 4-6 bullets pointing at the v1.1 highlights"
    - "[1.1.0] header still contains 'UNRELEASED' (date stamp is the LAST commit before tagging — that is Plan 12-04's job, NOT this plan)"
  artifacts:
    - path: "CHANGELOG.md"
      provides: "Release notes for v1.1.0 covering all three breaking behavior changes plus Phase 11 CLI refactor"
      contains: "BREAKING / Numerical Behavior Changes (Summary)"
    - path: "README.md"
      provides: "PyPI long_description (twine check validates this) with v1.1 banner"
      contains: "What's New in v1.1.0"
  key_links:
    - from: "CHANGELOG.md [1.1.0] BREAKING summary"
      to: "UPGRADING.md v1.0 -> v1.1 migration recipes"
      via: "Cross-reference text 'See UPGRADING.md ...'"
      pattern: "UPGRADING\\.md"
    - from: "CHANGELOG.md Phase 9 / Phase 11 entries"
      to: "ketu CLI behavior at runtime"
      via: "Documented flags --aspect-set, --harmonics, --list-aspect-sets, --list-house-systems and stderr '# Aspect set:' header"
      pattern: "--aspect-set|--harmonics|--list-aspect-sets|--list-house-systems"
---

<objective>
Close the two CHANGELOG.md gaps RESEARCH identified — Phase 9 (CLI default
change) and Phase 11 (CLI refactor) — and add a top-of-section rolled-up
"BREAKING / Numerical Behavior Changes (Summary)" list that satisfies
REL-02 success criterion 2 verbatim. Also do a small surgical update of
the README.md "What's New" section so the v1.1 PyPI page (long_description)
banners v1.1, not v1.0.

Purpose: Closes REL-02 and resolves RESEARCH.md Open Question 4 (README
touch-up). Without this plan, the v1.1.0 release ships a CHANGELOG that
silently omits the largest user-visible non-Lilith change (CLI default
EXTENDED -> CLASSICAL), and the PyPI page still announces v1.0.

Output: CHANGELOG.md `[1.1.0] - UNRELEASED` section gains a 3-bullet
top-of-section breaking summary, an `### Added` block listing Phase 11 CLI
refactor surface, and an updated `### Changed (BREAKING)` entry for the
CLI default. README.md "What's New" section is rewritten for v1.1.

The `UNRELEASED` placeholder is INTENTIONALLY KEPT in this plan; it is
replaced with the actual release date as the *last commit before tag* in
Plan 12-04 (RESEARCH.md Pitfall 2). Do NOT date-stamp here.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/12-release-preparation-v1-1-0/12-RESEARCH.md

@CHANGELOG.md
@README.md

# Phase 9 / 11 SUMMARYs only if needed for surface-area recall:
# @.planning/phases/09-configurable-aspects/09-05-SUMMARY.md
# @.planning/phases/11-cli-refactor-integration/11-05-SUMMARY.md
# @.planning/phases/11-cli-refactor-integration/11-06-SUMMARY.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Insert "BREAKING Summary" + Phase 9 CLI default + Phase 11 CLI refactor sections in CHANGELOG.md [1.1.0]</name>
  <files>CHANGELOG.md</files>
  <action>
The current `[1.1.0] - UNRELEASED` section already documents Lilith
(Phase 8) under `### Fixed (BREAKING - Numerical Behavior Change)` and
houses (Phase 10) under `### Removed (BREAKING)` + `### Added`. Two
gaps must be closed and one rolled-up summary must be added. Use the
Edit tool with surgical anchored replacements; do NOT rewrite the
file.

**Insertion 1 — rolled-up summary (top of [1.1.0] section)**

Anchor: line `## [1.1.0] - UNRELEASED`. Insert immediately after this
header line (and the blank line that follows), BEFORE the existing
`### Removed (BREAKING)` subsection:

```markdown
### BREAKING / Numerical Behavior Changes (Summary)

This release contains three user-visible behavior changes from v1.0.
Read each in detail in the dedicated sub-sections below and consult
`UPGRADING.md` for migration recipes.

1. **CLI default aspect set: EXTENDED (14) -> CLASSICAL (5).** The
   `ketu` CLI now emits 5 major aspects by default (Conjunction,
   Sextile, Square, Trine, Opposition). Restore v1.0 behavior with
   `ketu --harmonics extended`. (Phase 9 / ASP-04)
2. **Lilith (Mean Apogee) longitude formula corrected.** Values now
   match Swiss Ephemeris `SE_MEAN_APOG` to better than 0.01 deg. v1.0
   values were approximately 180 deg off on every date. Recompute
   any cached Lilith data. (Phase 8 / LIL-03)
3. **Houses module replaces broken `calculate_house_cusps`.** The v1.0
   `ketu.ephemeris.calculate_house_cusps` always returned an Equal
   House fallback regardless of system; it has been removed. Use the
   new `ketu.calculate_houses(...)` API or the `ketu houses` CLI
   subcommand. (Phase 10 / HOU-10)

```

(Note: this exact wording mirrors RESEARCH.md "Code Examples" >
"REL-02: CHANGELOG section template". Use `--harmonics extended` (not
`--aspect-set EXTENDED`) — the actual CLI flag wired in Phase 11 is
`--harmonics`; the parser accepts the preset name as a string. Confirm
by `grep -n "add_argument.*harmonics" ketu/cli/parser.py` before
writing the recipe.)

**Insertion 2 — Phase 9 CLI default change (BREAKING)**

The CHANGELOG today has no entry for the Phase 9 CLI default change.
Add a new top-level subsection `### Changed (BREAKING)` BETWEEN the
existing `### Removed (BREAKING)` and the existing `### Added` (the
houses one). Anchor to the line immediately before the houses
`### Added`:

```markdown
### Changed (BREAKING)

- **CLI default aspect set is now CLASSICAL (5 aspects) instead of
  the implicit EXTENDED (14 aspects) of v1.0.** The new default
  surfaces only the 5 major aspects (Conjunction, Opposition, Trine,
  Square, Sextile). v1.0 emitted all 14 harmonics by default; users
  who scraped CLI stdout will see approximately 64% fewer aspect
  rows per body pair. The `core.aspects` array remains length-14
  append-only (Kala positional indexing is unaffected — verified by
  the Phase 9 invariant test); only the *default selection* changed.
  Restore v1.0 behavior with `ketu --harmonics extended`. List
  available presets with `ketu --list-aspect-sets`. (Phase 9 /
  ASP-04, ASP-08)
```

**Insertion 3 — Phase 11 CLI refactor (Added)**

Today the CHANGELOG mentions the houses module under `### Added` but
not the broader CLI refactor. Append a NEW `### Added` block (Keep
a Changelog allows multiple `### Added` subsections inside a single
release) AFTER the existing Lilith-related `### Added` block (the
one that ends with the `pysweph>=2.10.3.6` bullet). Insert BEFORE
the `### Migration` subsection:

```markdown
### Added

- **CLI refactor (argparse-based)** — `ketu` is now an argparse
  multi-subcommand application:
  - `ketu aspects --date <ISO-UTC>` — aspect snapshot for a single
    instant (replaces the legacy interactive prompt).
  - `ketu houses --date <ISO-UTC> --lat <lat> --lon <lon>
    --system <name>` — house cusps for a single chart with optional
    `--polar-fallback {raise,porphyry}`.
  - `--harmonics {classical,traditional,extended,all,<comma-list>}` —
    select the aspect preset or pass an arbitrary comma-separated list
    of harmonic indices (e.g. `--harmonics 0,4,7,9,13`).
  - `--list-aspect-sets` — print available aspect presets with their
    angles, then exit. Works with or without a subcommand.
  - `--list-house-systems` — print available house systems with their
    polar-fallback hint, then exit. Works with or without a
    subcommand.
  - **Resolved-config stderr header** — every invocation emits a
    `# Ketu vX.Y.Z` line plus, when applicable, a `# Aspect set: <name>
    (N aspects: ...)` and/or `# House system: <name>` line to
    **stderr** (not stdout). Pipelines that consume stdout only are
    unaffected; pipelines that mix stdout and stderr should suppress
    with `2>/dev/null` or filter on `^# `.
- **Forward byte-stability regression** — new test
  `tests/cli/test_v1_1_reference_byte_stable.py` pins the v1.1
  default `ketu --harmonics all aspects --date 2000-01-01T12:00:00Z`
  output (sha256 `067fa67672d2e3c727a30612364e4b9bb1699401768f4a8fc4819a0e951785ed`,
  fixture at `tests/cli/fixtures/v1_1_reference_output.txt`) — catches
  unintended format/encoding/header drift in future releases.
  (Phase 11 / CLI-03)
```

**Verification BEFORE writing**

Before each Edit, run:
```bash
grep -n "^## \[1.1.0\] - UNRELEASED$" CHANGELOG.md   # must return one line
grep -n "^### Removed (BREAKING)$" CHANGELOG.md      # must return at least one (the houses one)
grep -n "^### Migration$" CHANGELOG.md               # must return one line in v1.1.0 block
```

Use the line numbers as anchors so the Edit tool's old_string is
unambiguous.

**DO NOT** in this task:
- Replace `UNRELEASED` with a date. That is Plan 12-04 Task 1.
- Reflow or reformat existing prose.
- Touch the v1.0.0 section or anything below it.
  </action>
  <verify>
After both edits:
```bash
# Rolled-up summary present
grep -q "^### BREAKING / Numerical Behavior Changes (Summary)$" CHANGELOG.md

# All three named items present in the summary
grep -q "EXTENDED (14) -> CLASSICAL (5)" CHANGELOG.md
grep -q "Lilith (Mean Apogee) longitude formula corrected" CHANGELOG.md
grep -q "Houses module replaces broken" CHANGELOG.md

# Phase 9 dedicated entry
grep -q "^### Changed (BREAKING)$" CHANGELOG.md
grep -q "ketu --harmonics extended" CHANGELOG.md
grep -q "ketu --list-aspect-sets" CHANGELOG.md

# Phase 11 dedicated entry
grep -q "^- \*\*CLI refactor (argparse-based)" CHANGELOG.md
grep -q "ketu --list-house-systems" CHANGELOG.md
grep -q "067fa67672d2e3c727a30612364e4b9bb1699401768f4a8fc4819a0e951785ed" CHANGELOG.md

# Lilith and houses content preserved (untouched anchors)
grep -q "approximately 180 deg on every date" CHANGELOG.md
grep -q "ketu\\.houses module" CHANGELOG.md

# UNRELEASED placeholder PRESERVED (do NOT date-stamp here)
grep -q "^## \[1.1.0\] - UNRELEASED$" CHANGELOG.md

# v1.0.0 section untouched (sanity)
grep -q "^## \[1.0.0\] - 2026-02-12$" CHANGELOG.md
```

All `grep -q` checks must succeed. If any fail, re-Edit with the
correct anchor and re-verify.
  </verify>
  <done>
CHANGELOG.md `[1.1.0]` section now contains: rolled-up BREAKING summary
at top, dedicated Phase 9 `### Changed (BREAKING)` entry, dedicated
Phase 11 `### Added` entry covering subcommands + flags + stderr header
+ byte-stability regression. UNRELEASED placeholder is intact (deferred
to 12-04). Existing Lilith and houses content is byte-identical to
pre-edit state outside the inserted blocks.
  </done>
</task>

<task type="auto">
  <name>Task 2: Update README.md "What's New" section to v1.1.0 (surgical)</name>
  <files>README.md</files>
  <action>
Anchor: line `## What's New in v1.0.0` (verified via grep:
research-confirmed it lives at line 13). Replace this section header
and the immediately-following bullet list with a v1.1.0 banner.

Strategy: leave the page badges (lines 3-4 — they read latest version
from PyPI dynamically, so they will auto-update once 1.1.0 is on PyPI),
leave the `## Features`, `## Installation`, etc. sections below
intact, ONLY rewrite the "What's New" section.

Read README.md first to find the exact bounding line of the existing
"What's New in v1.0.0" block (the section ends at the next `## ` heading
— likely `## Features`). Use Edit with old_string = the entire current
"What's New" block, new_string = the new v1.1.0 block:

```markdown
## What's New in v1.1.0

Ketu 1.1.0 is a feature release with **two breaking behavior changes**
from v1.0 (Lilith longitudes shift by approximately 180 deg, CLI
default emits 5 majors instead of 14 harmonics). Migration is
straightforward — see [UPGRADING.md](UPGRADING.md) for recipes.

- **Configurable aspects** — choose between `CLASSICAL` (5 majors,
  default), `TRADITIONAL` (7), `EXTENDED` (14), or `ALL`, via the
  `--harmonics` CLI flag or the `aspects=` parameter on the Python
  API. Discover presets with `ketu --list-aspect-sets`.
- **Houses module** — `ketu.calculate_houses(jd, lat, lon, system)`
  with Placidus, Koch, Porphyry, Equal, and Whole-Sign systems,
  vectorised over the broadcast of `(jd, lat, lon)`, with
  `polar_fallback` semantics for high-latitude charts. CLI:
  `ketu houses --system placidus --lat 48.85 --lon 2.35 --date
  2026-05-07T12:00:00Z`. List systems with `ketu --list-house-systems`.
- **Lilith fix** — Mean Apogee longitudes now match Swiss Ephemeris
  `SE_MEAN_APOG` to better than 0.01 deg (was approximately 180 deg
  off in v1.0). See [UPGRADING.md](UPGRADING.md) for the per-date
  shift table.
- **CLI refactor** — argparse-based, `ketu aspects` and `ketu houses`
  subcommands, resolved-config header on stderr, forward
  byte-stability regression test pinning v1.1 default output.
- **Test-only Swiss Ephemeris cross-check** —
  `pip install ketu[test]` pulls `pysweph>=2.10.3.6` for harness
  validation; runtime install (`pip install ketu`) stays pure-NumPy.

For the full list of changes see [CHANGELOG.md](CHANGELOG.md).

```

Note: keep the trailing blank line so the next section heading is
correctly delimited. Do NOT change any other line in README.md
(including the `## Features` heading and below).

If `## What's New in v1.0.0` is followed by content the planner
hasn't anticipated (e.g., a sub-bullet structure that differs
from the rough draft above), preserve the original spirit: the
new block should announce v1.1 highlights, link to CHANGELOG and
UPGRADING, and **not** mention v1.0 highlights at all.
  </action>
  <verify>
```bash
# New banner present
grep -q "^## What's New in v1.1.0$" README.md

# Old banner gone
! grep -q "^## What's New in v1.0.0$" README.md

# Anchor links present
grep -q "\[UPGRADING\.md\](UPGRADING\.md)" README.md
grep -q "\[CHANGELOG\.md\](CHANGELOG\.md)" README.md

# Mentions both BREAKING items at a glance
grep -q "180 deg" README.md
grep -q "5 majors instead of 14" README.md

# Sections below are untouched
grep -qE "^## (Features|Installation)" README.md
```
All checks pass.
  </verify>
  <done>
README.md "What's New in v1.0.0" section is replaced with a v1.1.0
banner that names the two breaking changes, lists 5 highlight bullets,
and links to CHANGELOG.md and UPGRADING.md. Sections below are
unchanged. PyPI long_description (via twine check in 12-04) will
render this v1.1 banner.
  </done>
</task>

<task type="auto">
  <name>Task 3: Validate, lint, and commit</name>
  <files>(no source edits; verification + git only)</files>
  <action>
1. Lint markdown rendering. The `publish.yml` workflow runs `twine
check dist/*` which validates README rendering on PyPI. Reproduce
locally with a quick render:
```bash
source venv/bin/activate
pip install --quiet readme_renderer  # if not already installed
python -c "
import readme_renderer.markdown
with open('README.md') as f:
    rendered = readme_renderer.markdown.render(f.read())
assert rendered is not None, 'README failed to render as markdown'
print('README OK')
"
```
If `readme_renderer` is not installable in the venv (e.g., offline),
skip this sub-step and rely on the `twine check` in Plan 12-04 — note
the skip in the SUMMARY.

2. Sanity check: no broken cross-references in the new sections.
```bash
# Files that the new sections link to must exist
test -f UPGRADING.md
test -f CHANGELOG.md
```

3. Diff review. Confirm only the intended files changed:
```bash
git status --porcelain
git diff --stat CHANGELOG.md README.md
```
Expect: 2 files modified, no other staged/unstaged changes.

4. Commit:
```bash
node ./.claude/get-shit-done/bin/gsd-tools.js commit \
  "docs(12-02): finish CHANGELOG v1.1.0 + update README What's New" \
  --files CHANGELOG.md README.md
```
GPG signing fallback per Plan 11-01 environmental note if needed.

5. Verify the commit:
```bash
git log -1 --oneline
git show --stat HEAD
```
  </action>
  <verify>
- `git log -1 --pretty=format:'%s'` shows
  `docs(12-02): finish CHANGELOG v1.1.0 + update README What's New`
  (or close).
- `git show --stat HEAD` lists exactly two files: `CHANGELOG.md`,
  `README.md`.
- `git status --porcelain` is empty.
- All `grep -q` checks from Tasks 1 and 2 still pass against the
  committed files (no last-minute drift).
- (If `readme_renderer` was available) `readme_renderer.markdown.render`
  returned non-None.
  </verify>
  <done>
CHANGELOG.md and README.md are updated and committed atomically on
`gsd/v1.1-milestone`. The CHANGELOG `[1.1.0]` section now satisfies
REL-02 success criterion 2 (rolled-up summary section + Phase 9 +
Phase 11 + existing Lilith + existing houses). The PyPI long_description
will banner v1.1.0 once `twine check` validates it in 12-04. The
`UNRELEASED` placeholder is intact for 12-04 to date-stamp at tag
time.
  </done>
</task>

</tasks>

<verification>
Phase-level verification of REL-02 after Plan 12-02:

```bash
# CHANGELOG covers all three named items in REL-02 success criterion 2
grep -q "^### BREAKING / Numerical Behavior Changes (Summary)$" CHANGELOG.md
grep -q "EXTENDED (14) -> CLASSICAL (5)" CHANGELOG.md       # CLI default change
grep -q "Lilith (Mean Apogee) longitude formula corrected" CHANGELOG.md  # Lilith
grep -q "Houses module replaces broken" CHANGELOG.md        # houses

# Phase 11 CLI refactor present (RESEARCH-identified gap closed)
grep -q "CLI refactor (argparse-based)" CHANGELOG.md
grep -q "067fa67672d2e3c727a30612364e4b9bb1699401768f4a8fc4819a0e951785ed" CHANGELOG.md

# README v1.1 banner active
grep -q "^## What's New in v1.1.0$" README.md
! grep -q "^## What's New in v1.0.0$" README.md

# Date stamp DEFERRED to 12-04 — UNRELEASED still present
grep -q "^## \[1.1.0\] - UNRELEASED$" CHANGELOG.md

# Two-file commit landed
git show --stat HEAD | grep -E "(CHANGELOG\.md|README\.md)"
```
</verification>

<success_criteria>
- CHANGELOG.md `[1.1.0]` rolled-up summary lists the 3 breaking changes
  named by REL-02 success criterion 2.
- Phase 9 (CLI default change) and Phase 11 (CLI refactor) sections
  added — both gaps from RESEARCH.md "What is MISSING" closed.
- README.md "What's New" advertises v1.1, not v1.0.
- `UNRELEASED` placeholder preserved (deferred to 12-04).
- Single commit on `gsd/v1.1-milestone` touching exactly two files.
- REL-02 closed.
</success_criteria>

<output>
After completion, create `.planning/phases/12-release-preparation-v1-1-0/12-02-SUMMARY.md`
including:
- Anchor lines used for each Edit insertion (so 12-04's date-stamp edit
  knows where the [1.1.0] header lives).
- Whether `readme_renderer` was available locally (informs 12-04
  about whether twine check is the first render gate).
- Commit hash.
- Any deviations (e.g., a Phase 11 surface-area fact that turned out
  different from RESEARCH and warranted a wording tweak).
</output>
