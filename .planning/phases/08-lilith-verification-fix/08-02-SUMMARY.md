---
phase: 08-lilith-verification-fix
plan: 02
subsystem: infra
tags: [packaging, pyproject, optional-dependencies, pysweph, swisseph, agpl, pep621]

# Dependency graph
requires:
  - phase: 08-lilith-verification-fix
    provides: 08-01 sealed Mean Black Moon Lilith definition + acceptable error envelopes (no code dependency, but locks the contract that Plan 03 will cross-check)
provides:
  - "[project.optional-dependencies].test extra exposing pysweph>=2.10.3.6"
  - "Empirical proof that pysweph is unreachable from runtime install (AGPL non-contamination)"
  - "Empirical proof that `pip install -e .[test]` exposes `swisseph.MEAN_APOG == 12`"
affects: [08-03-cross-check-harness, 12-release-preparation, ci-test-matrix]

# Tech tracking
tech-stack:
  added: [pysweph (test-only, AGPL, optional extra)]
  patterns: [test-only optional extras via PEP 621 [project.optional-dependencies]]

key-files:
  created:
    - .planning/phases/08-lilith-verification-fix/08-02-SUMMARY.md
  modified:
    - pyproject.toml

key-decisions:
  - "pysweph (community fork) is test-only — never appears in [project].dependencies, so the published wheel stays MIT/pure-NumPy"
  - "Lower-bound only specifier (>=2.10.3.6) — no upper pin; aligns with REQUIREMENTS LIL-04 and STATE.md locked decision"
  - "AGPL non-contamination is verified empirically (two-venv test), not assumed from configuration alone"

patterns-established:
  - "Test-only optional dependency: AGPL/heavyweight libs go under [project.optional-dependencies], imported via pytest.importorskip in tests, never under runtime [project].dependencies"
  - "Two-venv verification protocol: any future test-only extra must be proven absent from runtime install AND present from `[extra]` install before merging"

# Metrics
duration: 2m 5s
completed: 2026-05-06
---

# Phase 8 Plan 2: Test-Only pysweph Dependency Summary

**Added `pysweph>=2.10.3.6` as a `[test]` extra in `pyproject.toml` and empirically proved via two-venv installs that the AGPL fork is reachable from `pip install -e .[test]` while staying invisible to `pip install -e .` — runtime wheel remains pure-NumPy.**

## Performance

- **Duration:** 2m 5s
- **Started:** 2026-05-06T17:22:36Z
- **Completed:** 2026-05-06T17:24:41Z
- **Tasks:** 2
- **Files modified:** 1 (`pyproject.toml`)

## Accomplishments

- Single-section insertion to `pyproject.toml`: `[project.optional-dependencies].test = ["pysweph>=2.10.3.6"]`.
- Top-level `[project].dependencies` byte-identical (`["numpy>=1.20.0"]`) — runtime contract preserved.
- Empirical AGPL-isolation proof captured (two clean venvs, full stdout transcripts below).
- Existing test suite green (410 passed) and `mypy --strict` clean (22 source files) under the new pyproject section.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add `[project.optional-dependencies].test = ["pysweph>=2.10.3.6"]`** — `d813ee4` (chore)
2. **Task 2: Empirically verify two-venv runtime isolation** — _no code commit_ (evidence-only task; transcripts captured in this SUMMARY)

**Plan metadata:** _(captured in final docs commit below)_

## Files Created/Modified

- `pyproject.toml` — inserted a 5-line `[project.optional-dependencies]` section between `[project].dependencies` and `[project.urls]`. No other lines touched.

### Exact diff applied

```diff
diff --git a/pyproject.toml b/pyproject.toml
index da67699..95685df 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -38,6 +38,11 @@ dependencies = [
     "numpy>=1.20.0",
 ]

+[project.optional-dependencies]
+test = [
+    "pysweph>=2.10.3.6",
+]
+
 [project.urls]
 Homepage = "https://github.com/alkimya/ketu"
 Documentation = "https://ketu.readthedocs.io"
```

## Empirical Two-Venv Evidence

The most important verification of this plan: AGPL non-contamination is proven, not assumed.

### Venv 1 — Runtime install (`pip install -e .`)

Command sequence:

```bash
python3 -m venv /tmp/ketu-runtime-check
/tmp/ketu-runtime-check/bin/pip install --upgrade pip
/tmp/ketu-runtime-check/bin/pip install -e /home/loc/workspace/ketu
/tmp/ketu-runtime-check/bin/python -c "import swisseph"
```

Captured stdout/stderr (`/tmp/ketu-runtime-check.out`):

```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import swisseph
ModuleNotFoundError: No module named 'swisseph'
OK: swisseph correctly absent from runtime install
```

**Outcome:** `swisseph` is unreachable. The runtime wheel does NOT pull `pysweph`. AGPL contamination guard PASSES.

### Venv 2 — Test install (`pip install -e .[test]`)

Command sequence:

```bash
python3 -m venv /tmp/ketu-test-check
/tmp/ketu-test-check/bin/pip install --upgrade pip
/tmp/ketu-test-check/bin/pip install -e "/home/loc/workspace/ketu[test]"
/tmp/ketu-test-check/bin/python -c "import swisseph; print(swisseph.MEAN_APOG)"
/tmp/ketu-test-check/bin/pip show pysweph | grep -E "^(Name|Version):"
```

Captured stdout (`/tmp/ketu-test-check.out`):

```
12
Name: pysweph
Version: 2.10.3.6
platform.machine=x86_64
platform.system=Linux
sys.version=3.13.5 (main, Jun 25 2025, 18:55:22) [GCC 14.2.0]
```

**Outcome:**
- `swisseph.MEAN_APOG == 12` — Swiss Ephemeris constant matches expected value (the body-id used by Plan 03's harness for Mean Black Moon).
- Installed package is **`pysweph`** (community fork), version **`2.10.3.6`** — matches the locked decision in STATE.md.
- Wheel availability confirmed for Linux x86_64 / CPython 3.13.

### Platform / Python record

| Field | Value |
|-------|-------|
| platform.machine | `x86_64` |
| platform.system | `Linux` |
| Python version | `3.13.5` |
| pysweph wheel | available |

## Decisions Made

- **Test-only extra named `test`** (not `dev` or `cross-check`) — keeps the install command minimal (`pip install -e .[test]`) and aligns with the broadest community convention. The pytest harness in Plan 03 will simply require the `[test]` extra in CI.
- **Lower-bound `>=2.10.3.6`, no upper pin** — locked by REQUIREMENTS LIL-04. Compatible release would risk silently skipping security/wheel updates from the fork; an upper cap would force premature CI churn.
- **No new mypy override needed** — the pre-existing `[[tool.mypy.overrides]] module = ["swisseph.*"]` continues to silence missing-imports for the runtime install where `pysweph` is absent.
- **No `extras_require` legacy block** — using PEP 621 `[project.optional-dependencies]` exclusively keeps `pyproject.toml` declarative and tool-agnostic (setuptools≥61, pip≥21.3 both honor it).

## Deviations from Plan

None — plan executed exactly as written. Both tasks completed on first attempt, all verification commands returned the expected outputs, and no auto-fix rules were triggered.

**Total deviations:** 0
**Impact on plan:** None.

## Issues Encountered

- The repository's `venv/bin/pytest` script has a stale absolute shebang from an earlier directory (`/home/loc/workspace/solaris/ketu/venv/...`), so `venv/bin/pytest` cannot be invoked directly. Worked around by calling `venv/bin/python -m pytest`, which is the canonical invocation anyway. Not a regression introduced by this plan; flagged as noise to clean up at venv re-creation time but out of scope here.

## User Setup Required

None — no external service configuration. The new optional extra is opt-in and only used in test/CI contexts.

## Next Phase Readiness

- **Plan 03 (cross-check harness) unblocked**: it can now `pytest.importorskip("swisseph")` against a CI job that runs `pip install -e .[test]`. With this extra installed, the harness will execute (not skip); without it, it will skip — exactly the dual mode the plan calls for.
- **Plan 12 (release preparation) note**: the published wheel is provably free of AGPL code. The two-venv evidence in this summary is the citation to use in the release notes when explaining why `pysweph` is not a runtime dependency.
- **CI matrix**: when CI is updated, add a job that installs `[test]` and runs the full suite, plus a smoke job that installs without extras and asserts `import ketu` works (i.e., that `ketu` itself never imports `swisseph` at runtime). The harness in Plan 03 should make this easy.

## Self-Check: PASSED

Verified post-write:

- File exists: `.planning/phases/08-lilith-verification-fix/08-02-SUMMARY.md` — FOUND
- File exists: `pyproject.toml` (modified) — FOUND
- Commit `d813ee4` (Task 1) — FOUND in `git log --oneline --all`
- `[project.optional-dependencies]` section grep — FOUND at line 41 of `pyproject.toml`
- `pysweph>=2.10.3.6` grep — FOUND at line 43 of `pyproject.toml`

---
*Phase: 08-lilith-verification-fix*
*Plan: 02*
*Completed: 2026-05-06*
