---
phase: 09-configurable-aspects
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - tests/benchmark_aspects_batch.py
  - .planning/phases/09-configurable-aspects/baseline-v1.0.json
autonomous: true
plan_id: "09-01"
requirements:
  - ASP-08

must_haves:
  truths:
    - "v1.0 baseline timings for calculate_aspects_batch are captured BEFORE any phase 9 code change"
    - "Baseline file is consumable by Wave 3 verification — JSON with mean/median/std/min/max in seconds for at least one batch size"
    - "Baseline is reproducible — running the script twice on unchanged code yields ≤2% drift between runs"
  artifacts:
    - path: "tests/benchmark_aspects_batch.py"
      provides: "Standalone benchmark script for calculate_aspects_batch using current API (not legacy ketu.ketu/ketu_refactored)"
      contains: "calculate_aspects_batch"
      min_lines: 60
    - path: ".planning/phases/09-configurable-aspects/baseline-v1.0.json"
      provides: "Frozen v1.0 timing baseline JSON"
      contains: "mean"
  key_links:
    - from: "tests/benchmark_aspects_batch.py"
      to: "ketu.aspects.calculator.calculate_aspects_batch"
      via: "direct import"
      pattern: "from ketu.aspects.* import calculate_aspects_batch|from ketu.aspects.calculator"
    - from: "tests/benchmark_aspects_batch.py"
      to: ".planning/phases/09-configurable-aspects/baseline-v1.0.json"
      via: "JSON dump on --capture flag"
      pattern: "json\\.dump"
---

<objective>
Capture the v1.0 performance baseline for `calculate_aspects_batch()` BEFORE any Phase 9 refactor begins. This baseline is the reference for ASP-08 (≤5% regression). Without it, Wave 3 cannot verify the regression budget.

Purpose: ASP-08 is a regression gate ("≤5% vs v1.0 baseline"). The phrase "v1.0 baseline" is meaningless without a captured number. The existing `tests/benchmark.py` is BROKEN — it imports `ketu.ketu` and `ketu.ketu_refactored` which no longer exist (verified by `ls ketu/*.py` — only `core.py`, `calculations.py`, `complex.py`, `display.py`, `lunar_calendar.py`, `__init__.py`, `__main__.py`). A new lean benchmark script is required.

Output:
- `tests/benchmark_aspects_batch.py` — standalone benchmark script using the actual public API
- `.planning/phases/09-configurable-aspects/baseline-v1.0.json` — frozen baseline JSON (this file is committed to git as part of the phase artifact, not gitignored)
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/REQUIREMENTS.md
@.planning/phases/09-configurable-aspects/09-RESEARCH.md

# Existing (broken) benchmark scaffolding for reference only — DO NOT import from it
@tests/benchmark.py
@tests/benchmark_aspect_window.py

# The API under benchmark
@ketu/aspects/calculator.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Write standalone benchmark script tests/benchmark_aspects_batch.py</name>
  <files>tests/benchmark_aspects_batch.py</files>
  <action>
    Create a NEW standalone benchmark script. Do NOT extend `tests/benchmark.py` — it has dead `from ketu import ketu` and `from ketu import ketu_refactored` imports referencing modules that no longer exist (verified by listing `ketu/*.py`: only core.py, calculations.py, complex.py, display.py, lunar_calendar.py, __init__.py, __main__.py).

    Required contents:
    1. Module docstring stating purpose: "Capture v1.0 baseline timings for calculate_aspects_batch() — reference point for ASP-08 ≤5% regression gate (Phase 9)."
    2. Imports: `import argparse, json, time, sys, os, statistics`; `from datetime import datetime, timedelta, timezone`; `import numpy as np`; `from ketu.calculations import utc_to_julian`; `from ketu.aspects.calculator import calculate_aspects_batch`.
    3. Define `BENCH_DATES_BATCH_SIZES = [30, 90, 365]` — small/medium/yearly. Use `datetime(2025, 1, 1, tzinfo=timezone.utc)` as anchor; build daily JD arrays via `np.array([utc_to_julian(anchor + timedelta(days=i)) for i in range(N)])`.
    4. Function `bench_one(jd_array: np.ndarray, iterations: int = 50) -> dict`. Inside: 5 warmup iterations (results discarded), then `iterations` measured iterations using `time.perf_counter()`. Return dict with keys: `n_dates` (int), `iterations` (int), `mean` (float, seconds), `median`, `std`, `min`, `max`. Use `statistics.mean/median/stdev` or numpy equivalents — be consistent.
    5. Function `main()`: argparse with two flags — `--capture PATH` (writes JSON to PATH) and `--compare PATH` (loads PATH, runs same benchmark, prints %-delta vs each batch size, exits non-zero if any batch size regresses >5%). Default behavior with no flags: print results to stdout (human-readable).
    6. JSON schema written by `--capture`: top-level object with keys `version` (string, "v1.0-baseline"), `git_sha` (string, from `git rev-parse HEAD` via subprocess — fall back to "unknown"), `captured_at` (ISO-8601 UTC), `python_version`, `numpy_version`, `bench` (dict mapping str(n_dates) -> result dict from `bench_one`).
    7. `if __name__ == "__main__": main()` guard.

    Anti-patterns to avoid:
    - Do NOT use pytest-benchmark (not in deps — verified `pyproject.toml`).
    - Do NOT import from `ketu.ketu` or `ketu.ketu_refactored` — those modules are gone (v1.0 cleanup removed them).
    - Do NOT measure inside the iteration loop the time to BUILD the JD array — only the call to `calculate_aspects_batch`.
    - Do NOT swallow benchmark exceptions — let them surface.

    The script must be runnable via:
        python tests/benchmark_aspects_batch.py --capture .planning/phases/09-configurable-aspects/baseline-v1.0.json
    and via:
        python tests/benchmark_aspects_batch.py --compare .planning/phases/09-configurable-aspects/baseline-v1.0.json

    Mypy strict: type-hint all functions; `dict` returns can use `dict[str, float]` / `dict[str, Any]` as appropriate.
  </action>
  <verify>
    `python tests/benchmark_aspects_batch.py` runs without import error and prints three batch-size result blocks (30/90/365) showing non-zero `mean`. Run `mypy --strict tests/benchmark_aspects_batch.py` — should pass (or be excluded by existing mypy config; check `pyproject.toml [tool.mypy]` files= or exclude=).
  </verify>
  <done>
    `tests/benchmark_aspects_batch.py` exists, imports succeed, `--capture` and `--compare` flags both functional, mypy strict passes (or file is properly excluded), no dependency on missing legacy modules.
  </done>
</task>

<task type="auto">
  <name>Task 2: Capture v1.0 baseline JSON before any code change</name>
  <files>.planning/phases/09-configurable-aspects/baseline-v1.0.json</files>
  <action>
    Run the script from Task 1 to capture the baseline:

        python tests/benchmark_aspects_batch.py --capture .planning/phases/09-configurable-aspects/baseline-v1.0.json

    CRITICAL CHECKS before considering this task done:
    1. The current HEAD must be on `gsd/v1.1-milestone` branch (or whatever branch is being used for v1.1) AND must NOT yet contain any Phase 9 code changes. Confirm via `git status` — only `.planning/` files should be modified. If any `ketu/aspects/*.py` files show modifications, STOP — capturing now would taint the baseline.
    2. Verify the captured JSON file:
       - `version` field equals `"v1.0-baseline"`
       - `git_sha` is a real 40-char hex (not "unknown")
       - `bench["365"]["mean"]` is a positive float in roughly the 1ms-1s range (sanity: 365 dates of cross-pair aspect calculation should not be sub-microsecond nor multi-second)
       - `bench["365"]["std"] / bench["365"]["mean"] < 0.30` (coefficient of variation under 30% — flag if not, suggests system noise too high; rerun on quieter machine)
    3. Run the script TWICE in succession; the second run via `--compare` should report drift <5% on every batch size. If drift exceeds 5%, the machine is too noisy for a reliable baseline — note in summary, but proceed (Wave 3 will use the same machine).
    4. Commit the JSON file alongside the script. The JSON is a planning artifact, not gitignored. Add to git: `git add .planning/phases/09-configurable-aspects/baseline-v1.0.json tests/benchmark_aspects_batch.py`.

    Do NOT regenerate this baseline later in the phase. Wave 3 reads it as-is. If the baseline is bad, fix it now and recapture; do not silently rerun mid-phase.
  </action>
  <verify>
    `cat .planning/phases/09-configurable-aspects/baseline-v1.0.json | python -c "import json,sys; d=json.load(sys.stdin); assert d['version']=='v1.0-baseline'; assert len(d['git_sha'])==40; assert d['bench']['365']['mean']>0; print('OK', d['bench']['365']['mean'])"` succeeds and prints mean.
  </verify>
  <done>
    `baseline-v1.0.json` exists, contains valid v1.0-baseline JSON with three batch-size entries (30, 90, 365), git_sha is real, mean values are sane (>0, <10s), reproducibility check passed (≤5% drift between two consecutive runs).
  </done>
</task>

</tasks>

<verification>
- `python tests/benchmark_aspects_batch.py --compare .planning/phases/09-configurable-aspects/baseline-v1.0.json` runs without crashing on the same HEAD it was captured on, with all batch sizes within ±5%.
- The JSON file is plain-text (not binary), git-tracked, contains `git_sha` matching the current HEAD or a recent ancestor (must be from BEFORE any Phase 9 ketu/aspects/ change).
- `tests/benchmark_aspects_batch.py` does NOT import `ketu.ketu`, `ketu.ketu_refactored`, or any module not in the current `ketu/` directory listing.
</verification>

<success_criteria>
- `baseline-v1.0.json` exists with three batch-size entries and is committed.
- `tests/benchmark_aspects_batch.py` is the standalone benchmark harness, runnable independently.
- ASP-08 verification in Wave 3 has a concrete reference point (this file).
- No phase 9 implementation code has been changed at the time the baseline was captured (verified by git log between baseline capture commit and any subsequent code change in `ketu/aspects/`).
</success_criteria>

<output>
After completion, create `.planning/phases/09-configurable-aspects/09-01-SUMMARY.md` documenting:
- Baseline machine info (Python version, NumPy version, OS)
- Captured timings (mean ± std for each batch size)
- Drift between two consecutive captures (reproducibility check)
- Confirmation that no `ketu/aspects/*.py` files were modified at capture time
</output>
