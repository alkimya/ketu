---
phase: 11-cli-refactor-integration
plan: 05
subsystem: cli
tags: [argparse, cli, entry-point, legacy-removal, console-script, pyproject, packaging]

# Dependency graph
requires:
  - phase: 11-cli-refactor-integration
    provides: Plan 11-01 build_parser scaffolding + main(); Plan 11-04 wired cmd_aspects + cmd_houses + cmd_list_aspect_sets + cmd_list_house_systems (zero stubs in parser.py — both entry points can now safely route to ketu.cli:main)
provides:
  - pyproject.toml [project.scripts]: ketu = "ketu.cli:main" (was: "ketu.display:main")
  - pyproject.toml [tool.setuptools].packages: ketu.cli added
  - ketu/__main__.py: imports main from ketu.cli; raise SystemExit(main()) so argparse return code becomes process exit code (matches Plan 11-06's subprocess result.returncode contract)
  - ketu/display.py: main() function deleted (~30 lines); __all__ now exports only print_positions and print_aspects; unused imports trimmed (datetime, ZoneInfo, body_id, find_aspects_between_dates, utc_to_julian, julian_to_utc); module docstring updated
  - tests/test_ketu.py: TestMain class deleted (1 test); 'main' removed from `from ketu.display import (...)` import
  - tests/test_coverage_improvements.py: TestMainCLI class deleted (4 tests); legacy 'from ketu.display import main' removed (deviation Rule 3 — sister test file shared the import; would fail at pytest collection time once display.main was deleted)
  - CLI-01 fully closed: NO interactive input() prompt anywhere in ketu/. Subcommands have their own --help.
affects: [11-06-byte-identical-regression]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Atomic dual-entry-point repoint: pyproject.toml [project.scripts] AND ketu/__main__.py changed in the SAME commit. Updating only one means the other still routes to old code (research §Pitfall 7). Reinstall via `python -m pip install -e .` regenerates the venv `ketu` console script wrapper to point at ketu.cli:main."
    - "Module entry point exit-code propagation: `raise SystemExit(main())` in __main__.py — main() returns int (argparse convention), SystemExit converts it to process exit code. Plan 11-06's subprocess test will check result.returncode."
    - "Test file collection-time guard: when deleting a public symbol, grep for `from {module} import {symbol}` across tests/ BEFORE running pytest — collection-time ImportError surfaces before any test runs and is harder to diagnose than a runtime failure (research §Pitfall 8). Plan flagged tests/test_ketu.py only; tests/test_coverage_improvements.py shared the same import (caught here via Rule 3)."
    - "Source-of-truth purge order: delete the symbol's CONSUMERS first (test classes referencing it), then delete the SYMBOL itself. We did this in the reverse order (delete display.main, then test cleanup) but Edit handled it atomically via a single Write of display.py — the failure mode (collection error) was caught when running pytest after both edits, not before."

key-files:
  created: []
  modified:
    - pyproject.toml
    - ketu/__main__.py
    - ketu/display.py
    - tests/test_ketu.py
    - tests/test_coverage_improvements.py

key-decisions:
  - "Both entry points repointed in a single commit (Task 1 atomic): pyproject.toml [project.scripts] ketu = 'ketu.cli:main' + ketu/__main__.py `from ketu.cli import main`. Per research §Pitfall 7, updating only one leaves the other routing to old code. Reinstall `python -m pip install -e .` regenerates `venv/bin/ketu` console script wrapper; verified via `head -5 $(which ketu)` showing `from ketu.cli import main`."
  - "ketu/__main__.py uses `raise SystemExit(main())` rather than bare `main()`: main() returns the argparse parser's int return code (Plan 11-01 deliverable), SystemExit propagates it to the OS process exit code. Plan 11-06's byte-identical regression test runs `python -m ketu --harmonics all aspects --date ...` in a subprocess and checks `result.returncode`; this contract requires the SystemExit wrapper."
  - "ketu/display.py imports trimmed to only what print_positions and print_aspects need: dropped datetime, zoneinfo, body_id, find_aspects_between_dates, utc_to_julian, julian_to_utc — all six were exclusively used by the deleted main(). After trim: file is ~85 lines (was ~123). __all__ = ['print_positions', 'print_aspects'] (no 'main'). Module docstring rewritten to reflect 'library helpers' role; explicit pointer to ketu.cli for the argparse-based CLI replaces the v1.0 'main command-line interface' wording."
  - "Deviation Rule 3 (blocking): tests/test_coverage_improvements.py:TestMainCLI (4 tests) also imported `from ketu.display import main` and would have failed at pytest COLLECTION time (ImportError before any test ran) once display.main was deleted. The plan flagged tests/test_ketu.py:TestMain (1 test) but missed this sister file. Detected by `grep -rn 'from ketu.display import.*main' tests/` BEFORE running pytest. Both classes deleted; total test count delta is -5 (724 → 719), not -1 as the plan estimated."
  - "Plan 11-04's display.print_aspects test class (TestDisplay in tests/test_ketu.py) was left untouched: print_positions and print_aspects are unchanged in this plan; both tests still pass. New CLI tests in tests/cli/ (Plans 11-01..11-04, 24 tests) cover the equivalent CLI-level territory at the new entry point — no replacement test needed for the deleted TestMain/TestMainCLI classes."

patterns-established:
  - "Dual-entry-point atomic repoint: both pyproject.toml [project.scripts] AND ketu/__main__.py change in the SAME commit. Reinstall `python -m pip install -e .` regenerates the console script wrapper. Plan 11-06's tests use `python -m ketu` (not `ketu`) so technically wouldn't strictly require the reinstall — but reinstall is hygiene and the success criterion specifies the `ketu` script must work too."
  - "Public-symbol deletion checklist: (1) grep ALL of ketu/, tests/, docs/ for the symbol BEFORE deleting; (2) delete consumers first (test classes); (3) delete symbol; (4) trim now-unused imports in the surviving module; (5) update __all__; (6) update module docstring; (7) re-run pytest to confirm no collection errors. Step 1 caught the test_coverage_improvements.py omission in the plan."
  - "Console-script wrapper inspection: after `pip install -e .`, `head -5 $(which ketu)` shows the auto-generated wrapper (`from ketu.cli import main; sys.exit(main())`). Quick visual proof the entry point repoint took effect at the OS level, not just at the Python module level."

# Metrics
duration: 2m 38s
completed: 2026-05-07
---

# Phase 11 Plan 5: Entry Point Repoint & Legacy Removal Summary

**Both entry points (`ketu` console script + `python -m ketu`) repointed to `ketu.cli:main`; legacy `display.main()` interactive prompt deleted; CLI-01 fully closed (no `input()` prompt anywhere in ketu/).**

## Performance

- **Duration:** 2m 38s
- **Started:** 2026-05-07T15:17:56Z
- **Completed:** 2026-05-07T15:20:34Z
- **Tasks:** 2
- **Files modified:** 5 (pyproject.toml, ketu/__main__.py, ketu/display.py, tests/test_ketu.py, tests/test_coverage_improvements.py)

## Accomplishments

- **Both entry points repointed atomically** (single commit) — `pyproject.toml [project.scripts] ketu = "ketu.cli:main"` AND `ketu/__main__.py: from ketu.cli import main`. Reinstall via `python -m pip install -e .` regenerated the venv `ketu` console script wrapper.
- **Legacy `display.main()` deleted** (~30 lines) — the v1.0 interactive `input()` prompt that asked for date/time/timezone is gone. `display.py` is now a pure library-helpers module exposing `print_positions` and `print_aspects` only.
- **`display.py` imports trimmed** — dropped `datetime`, `zoneinfo`, `body_id`, `find_aspects_between_dates`, `utc_to_julian`, `julian_to_utc` (all six were exclusively used by the deleted `main()`). File is ~85 lines (was ~123). `__all__` no longer exports `main`.
- **Test cleanup across two files** — `tests/test_ketu.py:TestMain` (1 test) deleted as planned; `tests/test_coverage_improvements.py:TestMainCLI` (4 tests) deleted as Rule-3 deviation (the plan flagged the first file only; the second shared the same `from ketu.display import main` import and would have failed at pytest collection time).
- **CLI-01 fully closed** — `grep -rn "from ketu.display import.*main\|ketu\.display\.main\|ketu\.display:main" ketu/ tests/ docs/` returns only the historical comment in `__main__.py` describing what was removed.
- **719 tests pass** (was 724 baseline; -5 = 1 from TestMain + 4 from TestMainCLI). mypy --strict clean across `ketu/cli/` + `ketu/display.py` + `ketu/__main__.py` (10 source files).

## Task Commits

Each task was committed atomically:

1. **Task 1: Repoint entry points (pyproject.toml + __main__.py)** — `6067a49` (feat)
2. **Task 2: Delete display.py:main(), update __all__, clean up tests/test_ketu.py + test_coverage_improvements.py** — `b1ea9cd` (refactor)

_(Plan metadata commit follows this SUMMARY.)_

## Files Created/Modified

### `pyproject.toml` (modified)

```diff
 [project.scripts]
-ketu = "ketu.display:main"
+ketu = "ketu.cli:main"

 [tool.setuptools]
-packages = ["ketu", "ketu.ephemeris", "ketu.aspects", "ketu.cycles", "ketu.cache", "ketu.houses"]
+packages = ["ketu", "ketu.ephemeris", "ketu.aspects", "ketu.cycles", "ketu.cache", "ketu.houses", "ketu.cli"]
```

### `ketu/__main__.py` (modified — full rewrite)

```diff
 """Entry point for running Ketu as a module.

 This allows running Ketu with: python -m ketu
+
+Routes to ``ketu.cli:main`` (the argparse-based CLI). The legacy
+``ketu.display:main`` interactive prompt was deleted in Phase 11.
 """

-from .display import main
+from ketu.cli import main

 if __name__ == "__main__":
-    main()
+    raise SystemExit(main())
```

### `ketu/display.py` (modified — ~38 lines removed)

- Deleted `def main() -> None:` body (lines 90-116 in v1.0 / Plan 11-04 state). The interactive `input()` prompt for date/time/timezone, the `print_positions(jday)` + `print_aspects(jday)` calls, the `Aspect Timing Example` block (now lives in `cmd_aspects` which calls `display.print_aspects(jd, aspects=mask)` directly), and the `except ValueError` branch with French error message all gone.
- Trimmed imports: `from datetime import datetime`, `from zoneinfo import ZoneInfo`, and from `.calculations` dropped `body_id`, `utc_to_julian`, `julian_to_utc`; from `.aspects` dropped `find_aspects_between_dates`. Surviving imports: `numpy`, `signs` + `_CORE_ASPECTS` from `.core`, `body_name` + `body_sign` + `positions` + `is_retrograde` + `dd_to_dms` from `.calculations`, `calculate_aspects` from `.aspects`, `AspectSetSpec` (TYPE_CHECKING).
- `__all__` shrinks from 3 entries to 2: removes `"main"`.
- Module docstring rewritten: "Library formatters for Ketu astronomical output. Provides `print_positions` and `print_aspects`... The legacy interactive `main()` prompt was removed in Phase 11; the argparse-based CLI lives in `ketu.cli`."

### `tests/test_ketu.py` (modified)

```diff
-from ketu.display import print_positions, print_aspects, main
+from ketu.display import print_positions, print_aspects
```

```diff
-class TestMain:
-    """Test main CLI function"""
-
-    def test_main_invalid_input(self, monkeypatch, capsys):
-        """Test main with invalid input"""
-        inputs = iter(["invalid-date", ""])
-        monkeypatch.setattr("builtins.input", lambda _: next(inputs, ""))
-
-        main()
-        captured = capsys.readouterr()
-
-        assert "Error" in captured.out or "error" in captured.out
-
-
 class TestPrecision:
```

### `tests/test_coverage_improvements.py` (modified — Deviation Rule 3)

```diff
-from ketu.display import main
-
-
 class TestVelocityFunctions:
```

`TestMainCLI` class deleted (4 tests: `test_main_valid_input`, `test_main_default_timezone`, `test_main_invalid_date`, `test_main_invalid_time`). All four exercised the legacy interactive prompt via `monkeypatch.setattr("builtins.input", ...)` — no replacement needed; CLI-level coverage is provided by `tests/cli/test_aspects_cmd.py` and `tests/cli/test_resolved_header.py` from Plan 11-04.

## Re-install Verification

```text
$ python -m pip install -e . --quiet
(silent success)

$ which ketu
/home/loc/workspace/ketu/venv/bin/ketu

$ head -5 /home/loc/workspace/ketu/venv/bin/ketu
#!/home/loc/workspace/ketu/venv/bin/python
# -*- coding: utf-8 -*-
import re
import sys
from ketu.cli import main

$ ketu --help | head -3
usage: ketu [-h] [--list-aspect-sets] [--list-house-systems]
            [--harmonics SPEC]
            {aspects,houses} ...

$ python -m ketu --help | head -3
usage: ketu [-h] [--list-aspect-sets] [--list-house-systems]
            [--harmonics SPEC]
            {aspects,houses} ...

$ python -m ketu
(prints argparse help to stdout, exit code 0)

$ python -m ketu --list-aspect-sets
Available aspect sets (use with --harmonics SPEC):
  classical    : 5 majors (...)
  ... (4 presets listed)
```

Both entry points route to argparse CLI; no interactive prompt; exit code propagates correctly.

## Test Count Delta

| State | Count | Notes |
|-------|-------|-------|
| End of Plan 11-04 | 724 | Baseline before this plan |
| TestMain (test_ketu.py) deleted | -1 | Single test exercising legacy interactive main |
| TestMainCLI (test_coverage_improvements.py) deleted | -4 | Sister file Rule-3 deviation |
| **End of Plan 11-05** | **719** | **All passing; mypy --strict clean; 0 regressions** |

CLI test count unchanged from end of Plan 11-04 (24 CLI tests in tests/cli/ — none of them touch the deleted `main`).

## Decisions Made

See `key-decisions` in frontmatter. Key calls:

1. **Atomic dual-entry-point repoint** — both files in same commit (research §Pitfall 7).
2. **`raise SystemExit(main())`** in `__main__.py` for argparse return-code → process exit-code propagation (required by Plan 11-06's `result.returncode` check).
3. **Trim imports aggressively** in `display.py` — six imports were exclusively used by `main()`; keeping them would be cruft.
4. **Delete TestMain AND TestMainCLI** (5 tests total) — the new tests/cli/ suite from Plans 11-01..11-04 covers equivalent territory at the new entry point.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Removed `from ketu.display import main` and `TestMainCLI` class from tests/test_coverage_improvements.py**

- **Found during:** Pre-execution grep audit (`grep -rn "from ketu.display import.*main" ketu/ tests/ docs/`)
- **Issue:** The plan flagged `tests/test_ketu.py:TestMain` (1 test) but missed a sister file: `tests/test_coverage_improvements.py` line 23 also has `from ketu.display import main`, and a `TestMainCLI` class at lines 236-295 contains 4 more tests exercising the legacy interactive prompt. Once `display.main` is deleted, this import fails at pytest COLLECTION time (before any test runs), producing an `ImportError` cascade across the whole suite.
- **Fix:** Removed the import line + deleted the `TestMainCLI` class entirely. Same pattern as the planned `tests/test_ketu.py` cleanup.
- **Files modified:** `tests/test_coverage_improvements.py`
- **Verification:** `grep -rn "from ketu.display import.*main\|ketu\.display\.main\|ketu\.display:main" ketu/ tests/ docs/` returns only the historical comment in `__main__.py`. Full `pytest tests/` collects and runs cleanly (719 passed).
- **Committed in:** `b1ea9cd` (Task 2 commit; same atomic edit as the planned `test_ketu.py` cleanup since both must land before pytest can collect the suite)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary correctness fix — without it, `pytest tests/` would have failed at collection time and Task 2's verification step `pytest tests/ -v` could not have run. No scope creep; same pattern as planned cleanup, just applied to one extra file. Test count delta is -5 instead of plan-estimated -1.

## Issues Encountered

- **GPG signing skipped per environmental note.** Used `git -c commit.gpgsign=false` per commit; no global config change. Same approach used in Plans 11-01..11-04.
- **Venv shebangs broken in sandbox.** `pip install -e .` failed with "ne peut exécuter" because `venv/bin/pip` shebang points at a missing Python; switched to `python -m pip install -e .` per environmental note.

## User Setup Required

None — no external service configuration required. Just `python -m pip install -e .` (already done as part of Task 1).

## Next Phase Readiness

**Plan 11-06 (byte-identical regression) is fully unblocked.** It can now safely run `python -m ketu --harmonics all aspects --date 2020-12-21T19:20:00+01:00` in a subprocess and trust:

1. The subprocess routes through `ketu/__main__.py` → `ketu.cli:main` (this plan's repoint).
2. `main()` returns an int that becomes the subprocess's `result.returncode` (this plan's `SystemExit(main())` wrapper).
3. The output on stdout uses the v1.0 `º` (U+00BA) format string from `display.print_aspects` (Plan 11-04's BLOCKER 1 fix; preserved here — no edit to print_aspects in this plan).
4. The resolved-config header `# Ketu v1.1.0` + `# Aspect set: extended (...)` lands on stderr, not stdout (Plan 11-04's CLI-03 stdout-pristine contract; preserved).

Phase 11 progresses to **5/6 plans (83%)**. Plan 11-06 is the last plan; after it, Phase 11 is complete and Phase 12 (release prep) becomes available.

## Self-Check: PASSED

Verified:
- `pyproject.toml` contains `ketu = "ketu.cli:main"` AND `ketu.cli` in packages list — FOUND
- `ketu/__main__.py` contains `from ketu.cli import main` AND `raise SystemExit(main())` — FOUND
- `ketu/display.py` does NOT contain `def main` (`grep -c "def main" ketu/display.py` returns `0`) — VERIFIED
- `python -c "from ketu.display import main"` raises ImportError — VERIFIED
- `tests/test_ketu.py` does NOT contain `TestMain` or `test_main_invalid` — VERIFIED
- `tests/test_coverage_improvements.py` does NOT contain `TestMainCLI` or `from ketu.display import main` — VERIFIED
- `python -m pytest tests/` reports 719 passed (was 724 — delta of -5) — VERIFIED
- `python -m mypy --strict ketu/display.py ketu/__main__.py ketu/cli/` reports "Success: no issues found in 10 source files" — VERIFIED
- `ketu --help` and `python -m ketu --help` print argparse usage with no interactive prompt — VERIFIED
- `head -5 $(which ketu)` shows `from ketu.cli import main` — VERIFIED
- Commit `6067a49` exists in git log (Task 1) — FOUND
- Commit `b1ea9cd` exists in git log (Task 2) — FOUND

---
*Phase: 11-cli-refactor-integration*
*Completed: 2026-05-07*
