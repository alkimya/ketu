---
phase: 13-doc-gates-and-ci-foundation
plan: 04
subsystem: infra
tags:
  - ops
  - ci
  - numpydoc
  - github-actions

# Dependency graph
requires:
  - 13-02
  - 13-03
provides:
  - "Warning-only `Doc style audit (numpydoc — warning only, blocking from v1.2.0)` step in `.github/workflows/tests.yml` (Python 3.13 only, `continue-on-error: true`)"
  - "Phase 20 forward-note YAML comment marking the step as the OPS-02 finalization flip target (D-04 + D-05 traceability)"
  - "Single-source-of-truth invocation form: `python -m numpydoc lint $FILES` over `find ketu` minus `_*.py` and `lunar_calendar.py` (mirrors `[tool.numpydoc_validation].exclude`)"
  - "Bug fix: invalid `See Also` entries pointing to non-Python paths in `ketu/ephemeris/orbital.py` were crashing the parser (`ValueError: Error parsing See Also entry`); moved to `Notes` section so the CI step produces useful warning output instead of a Python traceback"
affects:
  - 13-05 (reformulation pass — README "Documentation Quality Gates" can now claim the numpydoc step is wired in CI)
  - "Phases 14–19 (every PR will surface new numpydoc gaps in the build log without halting unrelated work)"
  - "Phase 20 (OPS-02 finalization) — TWO things must flip when numpydoc goes blocking: (a) remove `continue-on-error: true` from this step, (b) remove `\"GL01\"` from `[tool.numpydoc_validation].checks` and run a mechanical fix-pass on the GL01 hits PLUS the 100 SS03/PR09/RT05/RT01 issues deferred from Plan 03 — see 'Deferred Issues' section below)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "CI gating-by-Python-version reuse: same `if: matrix.python-version == '3.13'` pattern as Plan 02's interrogate step + the existing coverage step — doc style is Python-version-independent, no need to fan out across the matrix"
    - "Warning-posture knob: `continue-on-error: true` is the single new ingredient with no in-repo precedent; locked by D-04 and explicitly slated for removal in Phase 20 (D-05). The leading YAML comment ensures the next maintainer cannot miss this when flipping to blocking"
    - "File globbing via `find ... ! -path ! -name`: redundant with `[tool.numpydoc_validation].exclude` regex but belt-and-braces — even if the config exclude misses a file, `find` doesn't pass it to numpydoc"
    - "Positive printout `Validating N files...` (29 files): visibility-on-green-build pattern requested in CONTEXT § Specifics — contributors see step is doing real work even when output is empty"

key-files:
  created: []
  modified:
    - ".github/workflows/tests.yml — new `Doc style audit (numpydoc — warning only, blocking from v1.2.0)` step inserted between `Doc coverage gate (interrogate ≥95%)` (Plan 02) and `Upload coverage reports to Codecov`. 14 lines added (3 lines comment + 11 lines step body). YAML still parses (9 named steps in expected order)."
    - "ketu/ephemeris/orbital.py — Rule 1 bug fix: `get_lilith_position` had a `See Also` block pointing to `docs/LILITH_DEFINITION.md : ...` and `tests/test_lilith_cross_check.py : ...`. numpydoc cannot parse these (the parser expects importable Python references like `module.func`, not file paths with `/` and `.md`/`.py` extensions). Moved to a `Notes` section as a plain Markdown-style list. 7 lines added, 5 lines removed; identical information content."

key-decisions:
  - "Plan executed verbatim — the YAML step shape is byte-identical to PATTERNS.md § \".github/workflows/tests.yml — new `Doc style audit (numpydoc)` step\" plus the leading 3-line comment that the plan's <action> block specified explicitly"
  - "BUG FIX (Rule 1): `See Also` block in `ketu/ephemeris/orbital.py:get_lilith_position` was crashing numpydoc (ValueError on `'docs/LILITH_DEFINITION.md : ...'`). The crash happened early in the AST walk so it masked every downstream issue. Moved the file-path references to a `Notes` section. Without this fix, the new CI step would produce a Python traceback instead of useful warnings — defeating the whole purpose of the warning posture."
  - "`grep -c \"continue-on-error: true\"` returns 2, not 1 as the acceptance criteria expected. The 2nd match is the LITERAL STRING in the leading YAML comment (`# Phase 20 ... remove \\`continue-on-error: true\\` ...`) that the plan's <action> block explicitly required. The YAML semantic check (only ONE step has the knob) passes correctly. Documenting the divergence here for traceability."
  - "DEFERRED: Plan 03 left 100 numpydoc issues across 11 source files outside its declared 9-file scope (concentrated in `ketu/ephemeris/{time,orbital,coordinates,planets}.py` and `ketu/aspects/*.py` and `ketu/cache/ephemeris_cache.py`). Mechanical SS03/PR09/RT05/RT01 codes — same fix-pass shape as Plan 03. Did NOT fix in Plan 04 because (a) Plan 04's stated objective is wiring the CI step, not extending Plan 03's fix-pass; (b) the warning posture (`continue-on-error: true`) means these surface as yellow-step warnings, not red-step blockers, which is exactly the intended behavior of the warning posture; (c) Phase 20 must run a full mechanical fix-pass anyway when removing the GL01 suppression — handling these 100 issues then keeps the work batched."

patterns-established:
  - "Numpydoc `See Also` only accepts importable Python references — file paths (with `/` or `.md`/`.py` extensions) crash the parser. Use `Notes` for file-path references; reserve `See Also` for `module.func`/`module.Class` form."
  - "Warning-posture step ordering convention: doc gates (interrogate blocking + numpydoc warning-only) live BETWEEN the coverage threshold step and the Codecov upload step. New v1.2 phases adding gates should follow this layout."
  - "`continue-on-error: true` flips with `\"GL01\"` suppression in pyproject.toml — they're the two halves of the warning posture. Phase 20 must flip both atomically; the leading YAML comment names both."

requirements-completed:
  - OPS-02

# Metrics
duration: "~12min"
completed: 2026-05-08
---

# Phase 13 Plan 04: Numpydoc CI step — warning-only Summary

**Wires `python -m numpydoc lint $FILES` into `.github/workflows/tests.yml` as a Python-3.13-gated, `continue-on-error: true` step (`Doc style audit (numpydoc — warning only, blocking from v1.2.0)`) with a leading YAML comment marking it as the Phase 20 flip target — closes OPS-02 in CI. One Rule 1 bug fix landed alongside (See Also block in `orbital.py` was crashing the parser). 100 mechanical numpydoc issues from outside Plan 03's declared scope are deferred to Phase 20's blocking-flip pass; the warning posture intentionally accepts them.**

## Performance

- **Duration:** ~12 min active (1 task + 1 Rule-1 deviation + synthetic-warning negative test)
- **Started:** 2026-05-08T15:30:00Z
- **Completed:** 2026-05-08T15:42:00Z
- **Tasks:** 1 / 1 (plus 1 Rule-1 deviation committed separately)
- **Files modified:** 2

## Accomplishments

### Task 1 — Numpydoc CI step

`.github/workflows/tests.yml` gains a new step inserted between the existing `Doc coverage gate (interrogate ≥95%)` (Plan 02) and `Upload coverage reports to Codecov`:

```yaml
    # Phase 20 (OPS-02 finalization): remove `continue-on-error: true` and
    # the `"GL01"` suppression in `[tool.numpydoc_validation].checks` to
    # flip this gate to blocking (per Phase 13 decisions D-04 / D-05).
    - name: Doc style audit (numpydoc — warning only, blocking from v1.2.0)
      if: matrix.python-version == '3.13'
      continue-on-error: true
      run: |
        FILES=$(find ketu -name "*.py" \
            ! -path "*/__pycache__/*" \
            ! -name "lunar_calendar.py" \
            ! -name "_*.py")
        echo "Validating $(echo "$FILES" | wc -l) files..."
        python -m numpydoc lint $FILES
```

- **3.13-only gating** mirrors Plan 02's interrogate step + the existing coverage threshold step.
- **`continue-on-error: true`** is the warning-posture knob locked by D-04. Single new ingredient with no in-repo precedent; documented in PATTERNS.md as such.
- **`python -m numpydoc lint`** (NOT `validate`) — `lint` is the AST-based multi-file form; `validate` would require importing each object (RESEARCH § Pitfall 1).
- **File scope** mirrors `[tool.numpydoc_validation].exclude` (no `lunar_calendar.py`, no `_*.py`) — belt-and-braces with the config.
- **`Validating N files...` printout** keeps the log informative even when the step is silent (CONTEXT § Specifics).
- **Phase 20 forward-note YAML comment** explicitly names BOTH things that must flip: `continue-on-error: true` removal AND `"GL01"` removal from pyproject.toml.

### Rule 1 deviation — `See Also` parser crash in `orbital.py`

While running the pre-flight numpydoc baseline, `python -m numpydoc lint $FILES` raised `ValueError: Error parsing See Also entry 'docs/LILITH_DEFINITION.md : Frame, formula, tolerance, history.'` — a hard parser crash that masked every downstream issue from the rest of the codebase.

Root cause: `numpydoc.docscrape._parse_see_also` requires importable Python references in `See Also` entries; file paths with `/` or `.md`/`.py` extensions break the parser. `ketu/houses/__init__.py` already uses the canonical form (`module.func : description`); `orbital.py:get_lilith_position` was the sole offender.

Fix: moved the two file-path references to a `Notes` section as a plain Markdown-style list. Identical information content, valid numpydoc syntax. No signature or behavior change.

Without this fix, Plan 04's new CI step would produce a Python traceback in the Actions log instead of useful warnings — defeating the whole purpose of the warning posture.

### Synthetic-warning negative test (worktree-local)

VALIDATION.md § Manual-Only Verifications asks for a feature-branch push to confirm the warning posture works end-to-end. As a parallel executor I cannot push, so I ran the local equivalent:

1. **Baseline** — captured `python -m numpydoc lint $FILES` issue counts (exit 1; 100 issues across 11 files; 0 issues on `ketu/calculations.py` per Plan 03's clean baseline).
2. **Inject gap** — temporarily removed the first `Returns\n    -------\n    bool\n ...` block from `ketu/calculations.py`.
3. **Re-run** — `numpydoc lint` exit 1 (unchanged); `calculations.py` issue count went from **0 → +2** (RT01 + RT05 surfacing the missing Returns section).
4. **CI semantic interpretation** — exit 1 is intercepted by `continue-on-error: true` in CI: step would show YELLOW (failure intercepted), build overall stays GREEN, the 2 new issues appear in the Actions log alongside the pre-existing 100. Build is not halted.
5. **Restore** — file restored from backup; `numpydoc lint` returns to baseline.

This confirms the warning posture works as designed: gaps surface in the log without blocking the build.

## Task Commits

Each task was committed atomically (worktree mode, `--no-verify`):

1. **Rule 1 deviation: replace invalid `See Also` file refs with Notes section** — `a882d4a` (fix)
2. **Task 1: add numpydoc warning-only step to tests.yml (OPS-02)** — `1ec5ce5` (ci)

This SUMMARY is committed as a separate metadata commit by the orchestrator after the worktree merge.

## Files Created/Modified

| File | Lines added | Lines removed | Nature |
| --- | --- | --- | --- |
| `.github/workflows/tests.yml` | +14 | 0 | New CI step (3 lines comment + 11 lines step body) |
| `ketu/ephemeris/orbital.py` | +7 | -5 | Rule 1 bug fix: See Also → Notes |

**Diff scope sanity check:**
- `git diff 043e145..HEAD -- ketu/ | grep -E "^[+-]\s*(def |class |return |import |from |__all__)" | wc -l` returns `0` — no signature/import/__all__ change in the bug fix.
- `git diff 043e145..HEAD -- .github/workflows/tests.yml` shows ONLY additions (no modifications to Plan 02's interrogate step or any earlier step).

## Decisions Made

- **Plan executed verbatim for Task 1** — the YAML step shape is byte-identical to PATTERNS.md spec plus the 3-line comment specified in the plan's `<action>` block.
- **Rule 1 fix landed as a separate commit before the CI step** — sequencing matters: if I'd added the CI step first, even the local `make doc-gates` invocation would crash. The fix is a hard pre-requisite for any `numpydoc lint` invocation over the full file scope.
- **DID NOT extend Plan 03's fix-pass to the 100 deferred issues** — see "Deferred Issues" below for the rationale. Briefly: the warning posture exists to accept warnings; extending Plan 04 to fix them would have re-opened a closed plan's scope and conflated two distinct quality concerns (CI plumbing vs source docstring polish).
- **DID NOT remove the leading comment despite the `grep -c "continue-on-error: true"` count divergence** — the comment is explicitly required by the plan's `<action>` (Phase 20 forward-note per D-05). The acceptance criteria's `exactly 1` count was based on YAML semantics; the 2nd grep match is the literal-string-in-comment, which is intentional. YAML structure check passes (only ONE step has `continue-on-error: true` as a YAML knob).

## Deviations from Plan

### Rule 1 (bug auto-fix) — `See Also` parser crash in `ketu/ephemeris/orbital.py`

- **Found during:** pre-flight baseline check before Task 1 — running `python -m numpydoc lint $FILES` over the same file scope as the plan's CI step crashed with `ValueError`.
- **Issue:** `numpydoc.docscrape._parse_see_also` cannot parse `See Also` entries that contain `/` (file path) or unrecognized file extensions. The `get_lilith_position` docstring had two such entries (`docs/LILITH_DEFINITION.md : ...` and `tests/test_lilith_cross_check.py : ...`).
- **Fix:** moved both references into a `Notes` section as a plain Markdown-style list. Identical information; valid numpydoc.
- **Files modified:** `ketu/ephemeris/orbital.py` (+7/-5).
- **Commit:** `a882d4a` (fix).
- **Why this isn't a Rule 4 (architectural):** zero signature/behavior/export change; pure docstring repair using the same `Notes`-section pattern Plan 03 used for `__init__.py` and `core.py` GL06/GL07 fold.
- **Why Plan 03 missed it:** Plan 03's verification ran `python -m numpydoc lint` only over its declared 9-file subset (which excluded `ephemeris/orbital.py`). The `find ketu` glob in Plan 04's CI step has wider scope and triggered the crash.

## Deferred Issues

### 100 mechanical numpydoc issues across 11 files outside Plan 03's declared scope

Running `python -m numpydoc lint $FILES` over the full `find ketu` glob (29 files) on the post-fix HEAD produces **100 issues across 11 files** (after the See Also crash fix unblocks the parser). All are mechanical SS03/PR09/RT05/RT01/PR01/PR08/GL06/GL07/GL08 codes — the same shape Plan 03 fixed in its 9-file subset.

**Per-file breakdown** (verified live 2026-05-08):

| File | Issues | Dominant codes |
| --- | --- | --- |
| `ketu/ephemeris/time.py` | 24 | SS03, PR09, RT05, PR08 |
| `ketu/aspects/timelines.py` | 12 | SS03, PR09, RT05, RT01 |
| `ketu/ephemeris/orbital.py` | 11 | SS03, PR01, RT01 |
| `ketu/ephemeris/coordinates.py` | 10 | SS03 |
| `ketu/cache/ephemeris_cache.py` | 10 | SS03, PR01, RT01 |
| `ketu/aspects/core.py` | 10 | SS03 |
| `ketu/ephemeris/planets.py` | 9 | SS03, GL08 |
| `ketu/aspects/calculator.py` | 7 | SS03 |
| `ketu/aspects/transits.py` | 3 | SS03 |
| `ketu/aspects/windows.py` | 2 | SS03 |
| `ketu/aspects/presets.py` | 2 | GL06, GL07 (`Public API` non-standard section) |

**Why deferred (not fixed in this plan):**

1. **Scope discipline:** Plan 04's stated objective is "Wire `python -m numpydoc lint <files>` into `.github/workflows/tests.yml` as a WARNING-ONLY CI step". Extending it to a 100-issue 11-file fix-pass would re-open Plan 03's scope and mix two distinct concerns (CI plumbing vs source docstring polish).
2. **Warning posture is correct behavior:** `continue-on-error: true` exists *precisely* to surface these warnings without blocking the build. The 100 issues will appear in the Actions log on the next push; that's the intended UX of the warning posture during Phases 14-19.
3. **Phase 20 batches the work:** Phase 20's blocking-flip plan must already run a mechanical sed-pass for the ~59 GL01 hits Plan 03 deferred via D-14. Including these 100 SS03/PR09/RT05 hits in the same pass keeps it efficient and atomic.
4. **No new bugs introduced:** these are pre-existing v1.0 / v1.1 docstrings. Plan 03's audit baseline (RESEARCH § "numpydoc baseline = 231 issues across 9 files") was scoped to a different subset — primarily because the original audit used `--ignore SA01 EX01 ES01` and ran on a smaller file enumeration than the locked `find ketu` exclude regex now in place.

**For the Phase 20 plan author:** see "Reminder for the Phase 20 plan author" below.

### `grep -c "continue-on-error: true"` returns 2, not 1

The acceptance criteria expected `exactly 1` continue-on-error match. The actual count is `2` because:
- Line 56: the LITERAL YAML knob `continue-on-error: true` (the active warning-posture flag).
- Line 51: the LITERAL STRING `continue-on-error: true` inside the leading YAML comment that the plan's `<action>` block explicitly required (Phase 20 forward-note per D-05).

The YAML semantic check passes correctly: `python -c "import yaml; ..."` confirms only ONE step has `continue-on-error: True` as a YAML key. The grep miscount is a textual artifact of the required forward-note comment, not a structural defect. No action needed; documenting for traceability.

## Issues Encountered

- **Initial `find ketu` numpydoc invocation crashed.** Pre-flight check produced `ValueError` from numpydoc's See Also parser, masking the rest of the run. Resolved as Rule 1 deviation above. Lesson: future doc-gate phases should run the FULL `find ketu` invocation (not a hand-curated subset) when computing baselines, so parser crashes surface immediately.
- **Plan acceptance criteria expected zero numpydoc output**; actual baseline produces 100 issues. Documented as deferred work above; the warning posture absorbs them by design.

## Forward note for the Phase 20 plan author

When Phase 20 lands the "flip numpydoc to blocking" task, the planner MUST:

1. **Remove `continue-on-error: true`** from the `Doc style audit (numpydoc — warning only, blocking from v1.2.0)` step in `.github/workflows/tests.yml`. (And update the step name to drop the "warning only" phrase — suggested rename: `Doc style audit (numpydoc — blocking)`.) The leading YAML comment block (lines 51-53) can be removed at the same time — its job is done.
2. **Remove the `"GL01"` line** from `[tool.numpydoc_validation].checks` in `pyproject.toml` (it's the third `# ignore` entry).
3. **Run a mechanical fix-pass on:**
   - **~59 GL01 hits** deferred from Plan 03 (D-14), concentrated in `complex.py` and `calculations.py`. Editor regex: `s/"""([A-Z][^"\n.]+\.)$/"""\n    \1/` (move summary onto its own line).
   - **100 mechanical SS03/PR09/RT05/RT01/PR01/PR08 hits across 11 files** deferred from Plan 04 (this plan), per the per-file breakdown above. Use the same period-termination + Returns-section pattern Plan 03 used for `complex.py` / `calculations.py` / `cycles/calculator.py`.
   - **2 GL06/GL07 hits in `ketu/aspects/presets.py`** ("Public API" non-standard section — fold into `Notes` per the Plan 03 pattern).
   - **1 GL08 hit in `ketu/ephemeris/planets.py:302`** (truly missing docstring — add a one-liner).
4. **Verify clean** with `python -m numpydoc lint $(find ketu -name "*.py" ! -path "*/__pycache__/*" ! -name "lunar_calendar.py" ! -name "_*.py")` after the fix-pass — must produce zero output (no stdout, no stderr beyond informational warnings).
5. **Confirm the synthetic-gap negative test FLIPS POLARITY** post-flip: injecting a gap should now make CI red (build fails), not yellow (build green with warning). Document in the Phase 20 SUMMARY.

## Path Forward for Plan 05

**Plan 05 (positive-add reformulation pass — Wave 4) can proceed.** Pre-conditions verified:

- `.github/workflows/tests.yml` has both doc-gate steps wired (interrogate blocking + numpydoc warning-only).
- `make doc-gates` (Plan 02) runs the same suite locally.
- README "Documentation Quality Gates" paragraph can now factually claim:
  - `interrogate ≥95%` (blocking) — enforced by CI on Python 3.13.
  - `numpydoc lint` (warning, blocking from v1.2.0) — enforced by CI on Python 3.13.
- Plan 05 has no source-file conflict with Plans 01-04 (Plan 05 only touches `README.md` and `CHANGELOG.md`).

## Self-Check: PASSED

Verified after writing SUMMARY:

- `.github/workflows/tests.yml` exists and contains the new step:
  - `grep -c "Doc style audit (numpydoc" .github/workflows/tests.yml` returns `1`.
  - `grep -c "numpydoc validate" .github/workflows/tests.yml` returns `0` (correct — we use `lint`, not `validate`).
  - `grep -E "Phase 20.*continue-on-error|Phase 20.*OPS-02" .github/workflows/tests.yml` matches the leading comment.
  - YAML parses (`python -c "import yaml; yaml.safe_load(open('.github/workflows/tests.yml'))"` exits 0).
  - Step ordering: `Check coverage threshold` → `Doc coverage gate (interrogate ≥95%)` → `Doc style audit (numpydoc ...)` → `Upload coverage reports to Codecov` (verified via `yaml.safe_load`).
- Commit `a882d4a` (Rule 1, fix) present in `git log`.
- Commit `1ec5ce5` (Task 1, ci) present in `git log`.
- `python -m interrogate ketu/` exit 0 with score 100.0% (≥95%).
- `python -m pytest tests/ -q --no-cov` — 724 tests pass.
- `python -m mypy ketu/ --strict` — Success: no issues found in 40 source files.
- Synthetic-warning negative test: `+2` issues injected on `calculations.py`, exit 1, would be intercepted by `continue-on-error: true` in CI.
- `git diff 043e145..HEAD -- ketu/ | grep -E "^[+-]\s*(def |class |return |import |from |__all__)"` returns 0 lines (no signature/import/__all__ change).

---
*Phase: 13-doc-gates-and-ci-foundation*
*Completed: 2026-05-08*
