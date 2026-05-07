---
phase: 11-cli-refactor-integration
plan: 06
subsystem: testing
tags: [cli, regression, subprocess, byte-identical, fixture, pytest, J2000, harmonics-all]

# Dependency graph
requires:
  - phase: 11-cli-refactor-integration
    provides: Plan 11-04 cmd_aspects + display.print_aspects single-source-of-truth for U+00BA `º` format string; Plan 11-05 ketu/__main__.py routing through SystemExit(main()) so subprocess result.returncode is meaningful
  - phase: 08-lilith-verification-and-fix
    provides: Lilith calibration that deliberately changed Lilith's longitude from v1.0's "Gemini 23º21'31\"" to v1.1's "Sagittarius 23º27'41\"" at J2000 UTC — the underlying astronomy that made v1.0 byte-identical infeasible
  - phase: 09-configurable-aspects
    provides: Default-aspect-set semantics + `# Aspect set: NAME` resolved-config header that is part of v1.1's stderr surface (not present in v1.0)
provides:
  - tests/cli/fixtures/v1_1_reference_output.txt: pinned v1.1 stdout for `python -m ketu --harmonics all aspects --date 2000-01-01T12:00:00Z` (2125 bytes, 52 lines, sha256 067fa67672d2e3c727a30612364e4b9bb1699401768f4a8fc4819a0e951785ed)
  - tests/cli/test_v1_1_reference_byte_stable.py: subprocess regression test (5 tests) asserting current `--harmonics all` stdout matches the pinned v1.1 fixture byte-for-byte; guards against future format drift, header leak to stdout, degree-symbol flip
  - CLI-03 reinterpretation: ORIGINAL contract was "byte-identical to v1.0 reference"; reinterpreted via Option A user decision as "self-stable forward contract" — pins v1.1 format going forward, NOT v1.0 backward compatibility (which Phases 8 + 9 deliberately broke)
affects: [12-release-preparation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Self-stable forward-contract regression: pin current output as the regression target (NOT a historical reference). Captures format drift after the consolidation point without claiming backward-compat to a version where the underlying domain logic deliberately changed."
    - "Subprocess-as-byte-surface: regression tests that pin user-visible byte output use `subprocess.run([sys.executable, '-m', package, ...])` + `result.stdout == FIXTURE.read_bytes()`. In-process tests via `capsys` would skip the entry-point and encoding layer."
    - "Encoding-pin via UTF-8 byte pattern: `data.count(b'\\xc2\\xba') > 20` and `data.count(b'\\xc2\\xb0') == 0` lock degree-symbol convention to U+00BA `º` MASCULINE ORDINAL INDICATOR (the v1.x display convention) and detect any future 'modernization' to U+00B0 `°` DEGREE SIGN."
    - "Stderr structural-cleanliness assertion: instead of asserting stderr is EMPTY (brittle when CLI-06 emits resolved-config header on stderr), assert every non-empty stderr line starts with `#` — flexible enough for diagnostic comments, strict enough to catch leaked print statements."
    - "Failure-message regeneration hint: when a byte-stable test fails on intentional drift, the assertion message includes `python -m ketu ... > FIXTURE` so the developer knows exactly how to update the fixture if the drift is approved."

key-files:
  created:
    - tests/cli/fixtures/v1_1_reference_output.txt
    - tests/cli/test_v1_1_reference_byte_stable.py
  modified: []

key-decisions:
  - "Option A pivot: re-pin fixture to current v1.1 output (NOT v1.0). The original plan's 'byte-identical to v1.0' contract was mathematically infeasible because Phase 8 (Lilith calibration) shifted Lilith's longitude (Gemini 23º21'31\" → Sagittarius 23º27'41\" at J2000 UTC) and Phase 9 (default CLASSICAL aspects) introduced the resolved-config header on stderr. Both were intentional v1.1 changes. The 'v1.0 contract' was already broken in reality; Option A formalizes that and reinterprets CLI-03 as a self-stable forward contract pinning future drift."
  - "Capture from CURRENT branch HEAD (gsd/v1.1-milestone), NOT from v1.0.0 git tag. No worktree dance needed — the original plan's `git worktree add /tmp/ketu-v1.0.0 v1.0.0` + venv-v1.0 + scripted-stdin-via-input() procedure was specific to capturing v1.0 bytes, which we are intentionally not doing under Option A."
  - "Fixture target renamed: `v1_1_reference_output.txt` (NOT `v1_0_legacy_output.txt`). Test target renamed: `test_v1_1_reference_byte_stable.py` (NOT `test_legacy_byte_identical.py`). Test class renamed: `TestV1_1ReferenceByteStable` (NOT `TestLegacyByteIdentical`). Naming honestly reflects what the contract actually pins (v1.1 forward) rather than what it was originally intended to pin (v1.0 backward)."
  - "Stderr policy: empty-stderr assertion replaced with structural-cleanliness assertion. Plan 11-04 pins the `# Ketu v1.1.0` + `# Aspect set: extended (...)` resolved-config header to stderr (CLI-06 contract). The byte-stable test's third sub-test `test_stderr_is_structurally_clean` asserts every non-empty stderr line starts with `#` — accommodates diagnostic headers, catches leaked `print()` statements that would silently corrupt downstream stderr consumers."
  - "Five-test breakdown: (1) fixture-exists-and-nonempty (sanity), (2) byte-identical-to-fixture (the main contract), (3) stderr-is-structurally-clean (no print leaks), (4) stderr-contains-aspect-set-header (CLI-06 belt-and-suspenders), (5) degree-symbol-locked-to-U+00BA (encoding-convention pin). The plan originally specified 3; added 2 (stderr-clean + degree-symbol) because the encoding+stderr surface is exactly what Phase 8 + Phase 9 changed and what the next breaking change is most likely to touch."
  - "No git worktree, no fresh venv, no input()-prompt strip. The Option A capture is a single-line redirect: `python -m ketu --harmonics all aspects --date 2000-01-01T12:00:00Z > FIXTURE 2> /tmp/v1_1_stderr.txt`. The argparse-based v1.1 CLI takes the date via flag (no input() prompts to strip)."

patterns-established:
  - "Forward-contract regression test naming: when pinning current output as a regression baseline (not a historical reference), name the fixture/test after the version being pinned forward (`v1_1_reference_*`), not the version-being-compared-against (`legacy_*`). Honest naming saves debugging time when a future contributor wonders 'what version is `legacy` referring to?'"
  - "Plan-Option-pivot documentation: when a plan's original premise becomes infeasible mid-execution, document the pivot in BOTH the SUMMARY frontmatter (`key-decisions`) AND the executable artifact's docstring (here: `test_v1_1_reference_byte_stable.py` module docstring). Future readers of the test file see the rationale without needing to dig through `.planning/`."
  - "Encoding regression detection via UTF-8 byte counts: `count(b'\\xc2\\xba') > N` patterns in test files lock encoding conventions without relying on language-aware string matching. Reads naturally to anyone familiar with UTF-8 and surfaces silent encoding flips that string-level assertions would miss."
  - "Failure-message helpfulness budget: byte-stable regressions that fire on intentional drift waste developer time if the message just says 'bytes differ at offset 1247'. The message should include (a) common drift causes, (b) regeneration command, (c) unified diff. Three lines of fail() boilerplate save 10 minutes of detective work per drift."

# Metrics
duration: ~15min
completed: 2026-05-07
---

# Phase 11 Plan 6: Byte-Identical Regression (Option A Pivot) Summary

**Self-stable forward contract for `--harmonics all`: 2125-byte v1.1 fixture pinned, 5-test subprocess regression added, original `byte-identical to v1.0` plan target abandoned because Phase 8 + Phase 9 deliberately diverged from v1.0 astronomy.**

## Performance

- **Duration:** ~15 min (incl. checkpoint pivot)
- **Started:** 2026-05-07T18:13:00Z (continuation agent spawn after Option A approval)
- **Completed:** 2026-05-07T18:28:11Z
- **Tasks:** 2 (fixture capture + regression test); checkpoint resolved out-of-band by user
- **Files modified:** 0; **files created:** 2

## Accomplishments

- **Phase 11 closed at 6/6 plans.** All v1.1 milestone CLI requirements covered: CLI-01 (Plan 11-05), CLI-02 (Plan 11-02 + 11-04), CLI-03 (this plan), CLI-04 (Plan 11-03), CLI-05 (Plan 11-04), CLI-06 (Plan 11-04).
- **v1.1 reference fixture pinned at 2125 bytes** (52 lines, sha256 `067fa67672d2e3c727a30612364e4b9bb1699401768f4a8fc4819a0e951785ed`, md5 `0e6a033c88eb88678187222af0fb7d46`) at `tests/cli/fixtures/v1_1_reference_output.txt`. Captured from `python -m ketu --harmonics all aspects --date 2000-01-01T12:00:00Z` on `gsd/v1.1-milestone` HEAD `0f2c43c`. Contains the three v1.0 structural blocks (Bodies Positions / Bodies Aspects / Aspect Timing Example) but with v1.1 astronomy (Lilith in Sagittarius 23º27'41" not Gemini 23º21'31"; Sun-Moon timing example shows Sextile/Square/Trine in v1.1's CLASSICAL+ window vs v1.0's Binovile/Decile/Trine). 41× U+00BA `º`, 0× U+00B0 `°`.
- **5-test subprocess regression test** at `tests/cli/test_v1_1_reference_byte_stable.py` (214 lines, mypy `--strict` clean): fixture-sanity, byte-identical, stderr-structurally-clean, stderr-contains-aspect-set-header, degree-symbol-locked-to-U+00BA. Plan specified 3; added 2 to lock encoding + stderr-cleanliness conventions that Phase 8 + Phase 9 most-recently changed.
- **Failure messages cite likely drift causes** + provide regeneration command for intentional bumps. The unified-diff output, list of common-cause hints, and one-liner regeneration recipe (`python -m ketu --harmonics all aspects --date {DATE} > {FIXTURE}`) make CI failures self-explanatory rather than requiring archaeology.
- **CLI-03 contract reinterpreted, NOT closed by silent acceptance.** Module docstring on the test file documents the Option A pivot transparently: original plan was "v1.0 byte-identical", Phase 8 + Phase 9 deliberately diverged, user chose to re-pin to v1.1 instead of revising the upstream phases. Future readers don't have to dig through `.planning/` to understand why the test is named `v1_1_reference` rather than `legacy`.
- **724 tests pass** (719 baseline from Plan 11-05 + 5 new); mypy `--strict` clean on the new test file.

## Task Commits

Each task was committed atomically:

1. **Task 1: Capture v1.1 reference fixture** — `2331fa8` (test)
2. **Task 2: Add v1.1 reference byte-stable subprocess regression** — `0f2c43c` (test)

**Plan metadata:** _committed by orchestrator at plan close_

## Files Created/Modified

- `tests/cli/fixtures/v1_1_reference_output.txt` (created) — pinned v1.1 reference stdout for `python -m ketu --harmonics all aspects --date 2000-01-01T12:00:00Z`. 2125 bytes, 52 lines. Forward-contract regression target.
- `tests/cli/test_v1_1_reference_byte_stable.py` (created) — 214-line subprocess regression test (5 tests). Module docstring documents the Option A pivot from v1.0 byte-identical to v1.1 self-stable forward contract.

## Decisions Made

- **Option A approved by user (single-most-important decision of this plan):** re-pin fixture to current v1.1 output instead of v1.0. Rationale: Phase 8 (Lilith calibration) and Phase 9 (default CLASSICAL aspects + resolved-config header) deliberately diverged from v1.0; the "v1.0 contract" was already broken in reality. Option A formalizes the divergence and reinterprets CLI-03 as a self-stable forward contract going forward.
- **No git worktree dance needed.** Option A captures from current HEAD via single redirect; the v1.0.0 worktree procedure (with fresh venv-v1.0, scripted-stdin via printf, input()-prompt strip) was specific to v1.0 capture and is not used here.
- **Stderr policy: structurally-clean, not empty.** Plan 11-04 pins the resolved-config header on stderr (CLI-06). Asserting "every non-empty stderr line starts with `#`" catches leaked `print()` calls without breaking the CLI-06 contract.
- **Two extra tests added (encoding + stderr-clean) beyond the plan-specified three.** Phase 8 + Phase 9 most-recently changed exactly these surfaces; locking them explicitly catches the most-likely future drift.
- **Failure-message regeneration hint included.** When the byte-stable test fires on intentional drift (e.g., a v2.0 format redesign), the message tells the developer exactly how to regenerate the fixture: `python -m ketu --harmonics all aspects --date {DATE} > {FIXTURE}`.

## Deviations from Plan

The Option A pivot is itself the dominant "deviation" — it is more accurately described as a **plan-target rewrite resolved at the human-verify checkpoint** than a Rule-1/2/3 auto-fix. The original plan body specified a v1.0 byte-identical contract; the user explicitly rejected that target after the prior executor surfaced the Phase 8 + Phase 9 divergence at the checkpoint. The continuation agent (this execution) operated under the rewritten target.

### Plan-target rewrite (resolved at checkpoint, NOT auto-fixed)

**1. Fixture target: `v1_1_reference_output.txt` (was: `v1_0_legacy_output.txt`)**
- **Found during:** Plan capture phase, by prior executor.
- **Issue:** Capturing v1.0.0 stdout would have produced a fixture that NO commit on `gsd/v1.1-milestone` could reproduce — Phase 8 (commit `e1c41b2` and follow-ups) shifted Lilith's longitude formula by design, so `python -m ketu --harmonics all aspects --date 2000-01-01T12:00:00Z` on v1.1 emits `Lilith    : Sagittarius    23º27'41"` while v1.0 emitted `Lilith    : Gemini         23º21'31"`. The "v1.0 byte-identical" contract was infeasible against the current branch.
- **Resolution (user decision Option A):** re-pin to current v1.1 output. Rename fixture, test file, and test class accordingly to honestly reflect the new contract.
- **Files:** `tests/cli/fixtures/v1_1_reference_output.txt` + `tests/cli/test_v1_1_reference_byte_stable.py`.
- **Verification:** byte-stable test passes against the freshly-captured fixture; full suite green (724 passed).

**2. Stale v1.0 fixture deleted (uncommitted leftover from prior executor)**
- **Found during:** Continuation-agent first action.
- **Issue:** Prior executor had captured `tests/cli/fixtures/v1_0_legacy_output.txt` and left it uncommitted on disk before hitting the checkpoint. Under Option A, that fixture is misleadingly-named (it pins v1.1 astronomy with a "v1.0 legacy" filename) and would confuse future readers.
- **Fix:** `rm tests/cli/fixtures/v1_0_legacy_output.txt` before captured fresh fixture under correct name.
- **Verification:** `ls tests/cli/fixtures/` after deletion shows empty directory; subsequent `python -m ketu ... > v1_1_reference_output.txt` captures fresh under correct name.

### Auto-fixed Issues (Rule 1/2/3)

None — all behaviour-affecting changes flowed from the Option A pivot resolved at the checkpoint, not from inline auto-fixes during task execution.

---

**Total deviations:** 1 plan-target rewrite (resolved at checkpoint by user); 1 housekeeping (stale fixture deletion); 0 Rule-1/2/3 auto-fixes.
**Impact on plan:** Major target rewrite (v1.0 → v1.1 pin) handled at checkpoint per Option A. CLI-03 contract is reinterpreted, not silently abandoned — the test file's module docstring documents the pivot transparently so future readers understand why the contract pins v1.1 forward rather than v1.0 backward. Plan deliverables (fixture file + subprocess regression test) are still produced; only their semantic interpretation changed.

## Issues Encountered

- **Pre-existing CLI-03 contract was infeasible.** Surfaced and resolved at the human-verify checkpoint by user decision Option A; documented above and in the test file's module docstring.
- **`xxd` not available in sandbox.** Plan body's verification recipe used `xxd ... | grep -c 'c2 ba'` for byte-pattern checks. Replaced with Python: `Path(p).read_bytes().count(b'\\xc2\\xba')`. Same semantic; works in any environment with Python available (which is required to run the tests anyway).

## User Setup Required

None. The fixture is committed; the test runs under standard `pytest tests/`. No environment variables, no external services, no manual configuration.

## Next Phase Readiness

- **Phase 11 closed: 6/6 plans complete.** All six CLI-* requirements covered (CLI-01 through CLI-06). Plan 11-06 was the last open Phase-11 plan.
- **Phase 12 (Release Preparation v1.1.0) unblocked.** Phase 11 deliverables ready for release: argparse CLI tree, `--harmonics` flag with preset + comma-list spec, `houses` subcommand, resolved-config header on stderr, introspection commands, byte-stable forward-contract regression test.
- **Phase 9 still awaits `/gsd:check-phase`** (independent track; not a Phase-12 blocker but should be closed before release notes are finalized).
- **Open follow-up (NOT a blocker):** the test file deliberately uses `subprocess.run([sys.executable, ...])` without a `cwd=` argument. Pytest's working directory at collection is the repo root; the test would also work under tox if invoked from the repo root. If a future CI configuration runs pytest from a different cwd (e.g., a sub-tree), the subprocess would still work because it invokes `python -m ketu` (module mode, not script path) — the installed `ketu` package is importable regardless of cwd. Surfaced here for completeness; no action needed.

---
*Phase: 11-cli-refactor-integration*
*Completed: 2026-05-07*

## Self-Check: PASSED

**Files verified:**
- FOUND: /home/loc/workspace/ketu/tests/cli/fixtures/v1_1_reference_output.txt (2125 bytes)
- FOUND: /home/loc/workspace/ketu/tests/cli/test_v1_1_reference_byte_stable.py
- MISSING (expected): /home/loc/workspace/ketu/tests/cli/fixtures/v1_0_legacy_output.txt (deleted as part of Option A pivot)

**Commits verified:**
- FOUND: 2331fa8 (test(11-06): capture v1.1 reference fixture for J2000 UTC)
- FOUND: 0f2c43c (test(11-06): add v1.1 reference byte-stable subprocess regression)

**Test status:**
- 724 tests pass (719 baseline + 5 new); mypy --strict clean on new file; full suite green.
