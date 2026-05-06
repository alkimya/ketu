---
phase: 09-configurable-aspects
plan: 05
subsystem: testing
tags: [aspect-presets, integration-test, benchmark, regression-gate, asp-07, asp-08]

# Dependency graph
requires:
  - phase: 09-01-baseline-capture
    provides: baseline-v1.0.json + tests/benchmark_aspects_batch.py with --aspect-set + --compare flags
  - phase: 09-02-presets-module
    provides: ketu/aspects/presets.py (CLASSICAL/TRADITIONAL/EXTENDED + resolve_aspect_set) and tests/test_aspect_presets.py (unit tests)
  - phase: 09-04a-calculator-refactor
    provides: ketu/aspects/calculator.py — 4 public APIs accept aspects=AspectSetSpec=None (default CLASSICAL)
provides:
  - ASP-07 verified: integration tests covering all 4 public aspect APIs with CLASSICAL/TRADITIONAL/EXTENDED presets
  - ASP-08 verified: benchmark-comparison.json — Phase 9 EXTENDED is FASTER than v1.0 baseline on every batch size
  - Hot-loop perf fix in calculate_aspects_batch (per-aspect work hoisted above per-date loop)
affects: [09-CHECK, 10-houses-module, 11-cli-refactor, kala-integration]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Performance contract gating via captured baseline JSON + percent-delta verdict (HARD GATE, no CONDITIONAL band)"
    - "Hoist per-aspect Python-scalar conversions above per-date loop (avoid n_dates × n_aspects cast cost)"
    - "Pre-compute orb arrays per aspect ONCE outside per-date loop (orbs depend only on coef, not date)"
    - "Integration tests for default-flip behavior — assert aspects=None == aspects=CLASSICAL on all default-bearing APIs"

key-files:
  created:
    - .planning/phases/09-configurable-aspects/benchmark-comparison.json
  modified:
    - tests/test_aspect_presets.py
    - ketu/aspects/calculator.py

key-decisions:
  - "ASP-08 baseline-comparison HARD GATE: any batch size >5% regression on aspect_set=extended = FAIL = blocks phase exit. No CONDITIONAL <10% band (Warning 8 fix locked in)."
  - "Plan 09-04a's calculator refactor introduced a +6-7% mean-time regression on aspect_set=extended at 200 iterations — root cause: per-aspect Python-scalar casts AND orb-array recomputation inside the per-date loop. Fixed by hoisting in commit b847176."
  - "Use 200 iterations (not the 50 default) for compare runs to keep sampling variance below the 5% gate width — the 50-iter compare runs were noise-dominated and produced flaky verdicts."
  - "Hoisted per-aspect work means the resolver-overhead per call is fully amortized over both the per-date AND per-aspect axes; CLASSICAL is now -33% to -41% faster than v1.0 (5/14 inner-loop work + zero cast overhead)."

patterns-established:
  - "When a refactor wraps a hot loop (with cast / lookup overhead), benchmark BEFORE merging the per-date loop change — the regression won't show in single-call timing tests but compounds at n_dates=365."
  - "Capture baseline at higher iteration count than 50 for noise-resilient comparisons; alternatively use median-of-runs across 5+ compare invocations."

# Metrics
duration: 19m 21s
completed: 2026-05-07
---

# Phase 9 Plan 05: Integration & Benchmark Summary

**ASP-07 + ASP-08 verified: 9 integration tests across all 4 public aspect APIs pass; calculate_aspects_batch is now 8-15% FASTER than v1.0 baseline on every batch size after hoisting per-aspect work out of the per-date loop.**

## Performance

- **Duration:** 19m 21s
- **Started:** 2026-05-06T23:10:38Z
- **Completed:** 2026-05-06T23:30:00Z (approx)
- **Tasks:** 2 (Task 1: integration tests, Task 2: benchmark capture)
- **Files modified:** 2 (`tests/test_aspect_presets.py`, `ketu/aspects/calculator.py`)
- **Files created:** 1 (`.planning/phases/09-configurable-aspects/benchmark-comparison.json`)

## Accomplishments

### ASP-07 — Integration tests (PASS, 9/9)

Added `TestAspectPresetsIntegration` class to `tests/test_aspect_presets.py`. Each test asserts a single property on a single public API; one-line summaries:

1. `test_calculate_aspects_classical_no_leak` — `calculate_aspects(jd, aspects=CLASSICAL)` emits no row with `i_asp` outside `{0,4,7,9,13}`.
2. `test_calculate_aspects_vectorized_classical_no_leak` — same property on `calculate_aspects_vectorized`.
3. `test_calculate_aspects_batch_classical_no_leak` — same property on `calculate_aspects_batch`, asserted across all dates in the batch.
4. `test_find_aspects_between_dates_classical_no_leak` — `find_aspects_between_dates(..., aspects=CLASSICAL)` emits no row whose `aspect_name` is outside `{Conjunction, Sextile, Square, Trine, Opposition}`.
5. `test_find_aspects_between_dates_default_equals_classical` — `aspects=None` default produces identical row list to explicit `aspects=CLASSICAL` on `find_aspects_between_dates`.
6. `test_find_aspects_between_dates_extended_superset` — `aspects=EXTENDED` returns a SUPERSET of `aspects=CLASSICAL` rows (every CLASSICAL row also appears in EXTENDED).
7. `test_default_equals_classical` — `aspects=None` default produces identical sorted output to `aspects=CLASSICAL` on `calculate_aspects`.
8. `test_traditional_no_leak` — `calculate_aspects_vectorized(jd, aspects=TRADITIONAL)` emits no row outside `{0,1,4,7,9,11,13}`.
9. `test_classical_results_use_canonical_iasp` — emitted `i_asp` is canonical 0-13 index (subset of `{0,4,7,9,13}`), NOT a renumbered position 0-4 in the filtered subset (Pitfall 1 / Kala positional contract).

488 tests pass total (was 479 before; +9 integration). Coverage 98.31% project-wide; `presets.py` 100%, `calculator.py` 99% (both exceed gates).

### ASP-08 — Benchmark comparison (PASS, max delta on EXTENDED = -10.10%)

Captured `benchmark-comparison.json`: Phase 9 EXTENDED + Phase 9 CLASSICAL vs v1.0 baseline at 200 iterations per batch size (4× the 50-iter baseline, to dampen sampling variance below the 5% gate width).

| Batch size | Baseline mean (ms) | Phase 9 EXTENDED mean (ms) | Delta (EXT)   | Phase 9 CLASSICAL mean (ms) | Delta (CLS)   |
| ---------: | -----------------: | -------------------------: | ------------: | --------------------------: | ------------: |
|         30 |              19.32 |                      17.36 |    **-10.10%** |                       12.90 |    **-33.19%** |
|         90 |              54.37 |                      45.88 |    **-15.62%** |                       32.81 |    **-39.65%** |
|        365 |             200.87 |                     173.80 |    **-13.48%** |                      119.26 |    **-40.63%** |

`asp08_overall_pass = true`. Largest regression on EXTENDED: **-10.10%** (i.e. 10% FASTER than v1.0). HARD GATE PASSED with significant margin.

CLASSICAL speedup observed across all sizes: **-33% to -41%** of inner-loop time. Matches research line 500's 30-65% speedup prediction (5/14 active aspects + hoisted casts).

### Verification artifacts

- `git diff tests/benchmark_aspects_batch.py` — empty (script unmodified per Blocker 2 fix).
- `git diff .planning/phases/09-configurable-aspects/baseline-v1.0.json` — empty (baseline frozen).
- `pytest tests/ -x` — 488 passed.
- `mypy --strict ketu/aspects/calculator.py` — clean.

## Task Commits

1. **Task 1: TestAspectPresetsIntegration class** — `3499b28` (test)
2. **Perf fix (deviation Rule 1):** hoist per-aspect work above per-date loop — `b847176` (perf)
3. **Task 2: benchmark-comparison.json** — `c974322` (chore)

## Files Created/Modified

- `tests/test_aspect_presets.py` — added 9 integration test methods + datetime/aspects/utc_to_julian imports + 4 module-level constant sets (CLASSICAL/TRADITIONAL/NON_CLASSICAL/NON_TRADITIONAL indices + CLASSICAL_NAMES). Now 65 tests total (56 unit + 9 integration).
- `ketu/aspects/calculator.py` — `calculate_aspects_batch` hot-loop fix: hoisted per-aspect Python-scalar casts (`int(i_asp)`, `float(angle)`, `float(coef)`) and orb-array computation `(orbs_body1 + orbs_body2)/2 * coef` ABOVE the per-date loop. The per-date loop now consumes pre-computed lists.
- `.planning/phases/09-configurable-aspects/benchmark-comparison.json` — created. Schema: `version`, `captured_at`, `git_sha`, `baseline_ref`, `baseline_git_sha`, `baseline_aspect_set`, `iterations`, `comparisons` (per-batch-size), `asp08_overall_pass`, `asp08_largest_regression_extended`, `notes`.

## Decisions Made

- **HARD GATE enforced exactly as plan specifies.** No CONDITIONAL band; ASP-08 is binary PASS/FAIL.
- **Iteration count raised to 200 for compare runs.** With 50 iterations the 365-batch standard deviation was ~5-15% of the mean (driven by GC pauses, scheduler jitter, cache misses), making single-run verdicts flaky. 200 iterations brings std/mean below 4% across all batch sizes.
- **Hot-loop fix landed in this plan, not deferred.** Plan 09-04a's refactor was correct semantically (canonical i_asp, single resolver call) but introduced per-date Python-overhead. Plan 09-05's verdict logic explicitly authorizes calculator.py fixes for hot-loop regressions; deferring would have left the phase blocked.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — Performance Bug] Hot-loop regression in `calculate_aspects_batch`**
- **Found during:** Task 2 (initial benchmark compare runs at 50 and 200 iterations consistently showed +5-7% regression on `aspect_set=extended`).
- **Issue:** Plan 09-04a moved per-aspect work into the per-date loop:
  - `int(i_asp_val)`, `float(selected_angles[k])`, `float(selected_coefs[k])` — paid `n_dates × n_aspects` times instead of `n_aspects` times.
  - `orbs = (orbs_body1 + orbs_body2) / 2 * aspect_coef` — recomputed `n_dates × n_aspects` times despite depending only on `aspect_coef`.
- **Fix:** Hoisted all per-aspect work ABOVE the per-date loop:
  - `selected_iasp_ints` / `selected_angles_f` / `selected_coefs_f` — pre-cast lists.
  - `pair_orb_sums = (orbs_body1 + orbs_body2) / 2` (date-independent).
  - `selected_orbs_per_aspect = [pair_orb_sums * c for c in selected_coefs_f]` (per-aspect, date-independent — list of pre-multiplied arrays).
  - The per-date loop now indexes `selected_orbs_per_aspect[k]` directly, no arithmetic inside.
- **Files modified:** `ketu/aspects/calculator.py`
- **Verification:** All 488 tests still pass; mypy --strict clean; benchmark comparison goes from +6-7% regression to -8% to -15% **improvement** on every batch size.
- **Committed in:** `b847176`

---

**Total deviations:** 1 auto-fixed (1 performance bug — Rule 1)
**Impact on plan:** The fix was both necessary (HARD GATE failure without it) and explicitly authorized by Plan 09-05 Step 4. No scope creep; surgical edit confined to the per-date loop body and its hoist preamble.

## Issues Encountered

- **Sampling-variance noise at 50-iter default.** First compare runs were noise-dominated: same code produced verdicts ranging from -1% to +14% on the 365 batch across 5 consecutive compare invocations. Resolution: bumped to 200 iterations and used the script's own `--iterations 200` flag (no script mutation).

## LRU-cache Audit (Final Check Before Phase Exit)

Per Plan 09-05 Warning-7 belt-and-braces:

```
ketu/calculations.py:94:@lru_cache(maxsize=1024)         (planet position cache, scalar JD)
ketu/aspects/core.py:72:@lru_cache(maxsize=256)          (single-aspect scanner)
```

| Site | Function | Cache key | Materializes filtered aspect output? | Verdict |
| --- | --- | --- | --- | --- |
| `ketu/calculations.py:94` | `_cached_planet_position` | `(jd, body_id)` | No — returns body position only, no aspect-set involvement | **SAFE** |
| `ketu/aspects/core.py:72` | scalar aspect scanner | `(jd_start, jd_end, b1, b2, angle)` | No — keyed per-angle, never per-set | **SAFE** |

Cross-reference Plan 09-04a SUMMARY's audit: same 2 sites + `body_properties` cache; same verdicts. Consistency confirmed. **No cache currently materializes filtered aspect output**, so adding ASP-06's `mask.tobytes()` key suffix remains a forward-looking rule (no live cache to fix). 

## Phase 9 Acceptance Criteria Status (1-5 from ROADMAP)

1. **`core.aspects` length 14, append-only invariant** — covered by Plan 09-03 invariant test (sha256 byte fingerprint + per-row identity). PASSING.
2. **CLASSICAL/TRADITIONAL/EXTENDED resolve to 5/7/14 active aspects** — covered by Plan 09-02 unit tests (56 tests). PASSING.
3. **CLASSICAL leak = zero across all four public aspect APIs (ASP-07)** — covered by this plan's `TestAspectPresetsIntegration` (3 calculator-family + 3 find_aspects_between_dates + TRADITIONAL + canonical-i_asp + default-flip = 9 tests). PASSING.
4. **`aspects=None` == `CLASSICAL` on `calculate_aspects` AND `find_aspects_between_dates` (ASP-04)** — covered by `test_default_equals_classical` and `test_find_aspects_between_dates_default_equals_classical`. PASSING.
5. **≤5% regression vs baseline (HARD GATE) AND CLASSICAL faster (ASP-08)** — covered by `benchmark-comparison.json`. EXTENDED -10% to -15% (faster); CLASSICAL -33% to -41% (faster). PASSING with margin.

All five Phase 9 acceptance criteria GREEN.

## Next Phase Readiness

- **Phase 9 (Configurable Aspects) ready for `/gsd:check-phase`.** All 6 plans complete (09-01, 09-02, 09-03, 09-04a, 09-04b, 09-05).
- **Cross-repo blocker REMAINS:** "Kala aspect-count dependency unverified" — confirm with Kala maintainer that `KetuAdapter` either tolerates `EXTENDED` opt-in or is updated before Phase 9 merge. This plan does NOT resolve the cross-repo blocker; it's a pre-merge action item per STATE.md.
- **Performance regression risk for future hot-loop refactors:** any future refactor of `calculate_aspects_batch` MUST be benchmarked at ≥200 iterations against baseline-v1.0.json before merging. The 50-iter default produces noise-dominated verdicts at the 5% gate.

## Self-Check: PASSED

Verified at `2026-05-06T23:30Z`:

- `tests/test_aspect_presets.py` exists and contains `TestAspectPresetsIntegration` with 9 test methods — FOUND.
- `.planning/phases/09-configurable-aspects/benchmark-comparison.json` exists — FOUND.
- `ketu/aspects/calculator.py` perf fix lands at line ~298 (hoisted casts) and line ~330 (selected_orbs_per_aspect) — FOUND.
- Commits exist: `3499b28` (test), `b847176` (perf), `c974322` (chore) — all FOUND in `git log --oneline`.
- `git diff tests/benchmark_aspects_batch.py` empty — VERIFIED.
- `git diff .planning/phases/09-configurable-aspects/baseline-v1.0.json` empty — VERIFIED.

---
*Phase: 09-configurable-aspects*
*Completed: 2026-05-07*
