---
phase: 09-configurable-aspects
plan: 05
type: execute
wave: 3
depends_on:
  - "09-01"
  - "09-04"
files_modified:
  - tests/test_aspect_presets.py
  - .planning/phases/09-configurable-aspects/benchmark-comparison.json
autonomous: true
plan_id: "09-05"
requirements:
  - ASP-07
  - ASP-08

must_haves:
  truths:
    - "Integration test: calling each public aspect API with aspects=CLASSICAL returns zero rows with i_asp outside {0, 4, 7, 9, 13} — across calculate_aspects, calculate_aspects_vectorized, calculate_aspects_batch"
    - "Integration test: aspects=None default produces identical output to aspects=CLASSICAL (default-flip observable)"
    - "Integration test: aspects=EXTENDED produces output equivalent to v1.0 14-aspect behavior (legacy escape hatch verified)"
    - "Integration test: aspects=TRADITIONAL returns zero rows with i_asp outside {0, 1, 4, 7, 9, 11, 13}"
    - "Benchmark comparison: tests/benchmark_aspects_batch.py --compare baseline-v1.0.json reports ≤5% regression on calculate_aspects_batch for at least one batch size with aspects=EXTENDED (apples-to-apples comparison vs v1.0 default which was effectively EXTENDED)"
    - "Benchmark observation: aspects=CLASSICAL is FASTER than aspects=EXTENDED on calculate_aspects_batch (5/14 inner-loop work)"
  artifacts:
    - path: "tests/test_aspect_presets.py"
      provides: "Integration tests for all public batch aspect APIs (extends Plan 09-02 test file with new test class TestAspectPresetsIntegration)"
      contains: "TestAspectPresetsIntegration"
    - path: ".planning/phases/09-configurable-aspects/benchmark-comparison.json"
      provides: "Captured comparison: v1.0 baseline vs Phase 9 EXTENDED vs Phase 9 CLASSICAL timings for each batch size"
      contains: "regression_pct"
  key_links:
    - from: "tests/test_aspect_presets.py TestAspectPresetsIntegration"
      to: "ketu.aspects.{calculate_aspects, calculate_aspects_vectorized, calculate_aspects_batch}"
      via: "direct call with aspects= parameter"
      pattern: "calculate_aspects\\(.*aspects=|calculate_aspects_vectorized\\(.*aspects=|calculate_aspects_batch\\(.*aspects="
    - from: ".planning/phases/09-configurable-aspects/benchmark-comparison.json"
      to: ".planning/phases/09-configurable-aspects/baseline-v1.0.json"
      via: "tests/benchmark_aspects_batch.py --compare"
      pattern: "regression_pct"
---

<objective>
Verify Phase 9 acceptance criteria ASP-07 (integration test across all public batch APIs with CLASSICAL preset) and ASP-08 (≤5% regression on `calculate_aspects_batch` vs v1.0 baseline). Both verifications run AFTER the Wave 2 refactor lands, so depends_on covers Plans 09-01 (baseline) and 09-04 (refactor).

Purpose: ASP-07 — "Integration test: configure CLASSICAL, call all public aspect APIs, assert no result contains a non-classical aspect". ASP-08 — "Benchmark: `calculate_aspects_batch()` regresses by no more than 5% vs v1.0 baseline". Without this plan the success criteria #3 and #5 of the phase are unverified.

Output:
- Extended `tests/test_aspect_presets.py` with a new `TestAspectPresetsIntegration` test class (~6 test functions) covering CLASSICAL/TRADITIONAL/EXTENDED/None across all three batch APIs.
- New file `.planning/phases/09-configurable-aspects/benchmark-comparison.json` — captured Phase 9 timings + regression-pct vs baseline.
- Documented decision: PASS / DOCUMENTED-DEVIATION (with magnitude + rationale) for the ASP-08 5% gate.
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
@.planning/phases/09-configurable-aspects/09-01-SUMMARY.md
@.planning/phases/09-configurable-aspects/09-02-SUMMARY.md
@.planning/phases/09-configurable-aspects/09-04-SUMMARY.md

# The benchmark script (created in Plan 09-01)
@tests/benchmark_aspects_batch.py

# The baseline JSON (captured in Plan 09-01)
@.planning/phases/09-configurable-aspects/baseline-v1.0.json

# The refactored APIs (modified in Plan 09-04)
@ketu/aspects/calculator.py

# The existing test file to extend (created in Plan 09-02)
@tests/test_aspect_presets.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add TestAspectPresetsIntegration class to tests/test_aspect_presets.py (ASP-07)</name>
  <files>tests/test_aspect_presets.py</files>
  <action>
    EXTEND `tests/test_aspect_presets.py` (created in Plan 09-02) with a new test class for integration coverage. The Plan 09-02 file contains resolver/constants unit tests; this task adds end-to-end tests that call the actual aspect calculation APIs.

    Add at the top of the file (alongside existing imports):

        from datetime import datetime, timezone, timedelta
        import numpy as np
        from ketu.calculations import utc_to_julian
        from ketu.aspects import (
            calculate_aspects,
            calculate_aspects_vectorized,
            calculate_aspects_batch,
            CLASSICAL,
            TRADITIONAL,
            EXTENDED,
        )

        # Canonical 0-13 index sets per preset (per ketu.core.aspects row order)
        CLASSICAL_INDICES = {0, 4, 7, 9, 13}                    # 5 majors
        TRADITIONAL_INDICES = {0, 1, 4, 7, 9, 11, 13}            # 7
        NON_CLASSICAL_INDICES = set(range(14)) - CLASSICAL_INDICES   # 9 non-classical (1,2,3,5,6,8,10,11,12)
        NON_TRADITIONAL_INDICES = set(range(14)) - TRADITIONAL_INDICES  # 7 non-traditional

    Add a new test class:

        class TestAspectPresetsIntegration:
            """ASP-07: integration tests verify CLASSICAL/TRADITIONAL/EXTENDED defaults
            propagate correctly through all public batch aspect APIs and never leak
            non-set aspects into results."""

            def setup_method(self):
                self.jd = utc_to_julian(datetime(2025, 1, 1, tzinfo=timezone.utc))
                self.jd_array = np.array([
                    utc_to_julian(datetime(2025, 1, 1, tzinfo=timezone.utc) + timedelta(days=i))
                    for i in range(7)
                ])

            def test_calculate_aspects_classical_no_leak(self):
                """ASP-07: calculate_aspects(jd, aspects=CLASSICAL) returns no row with non-classical i_asp."""
                result = calculate_aspects(self.jd, aspects=CLASSICAL)
                leaked = set(int(x) for x in result["i_asp"]) & NON_CLASSICAL_INDICES
                assert not leaked, f"CLASSICAL preset leaked non-classical i_asp: {leaked}"

            def test_calculate_aspects_vectorized_classical_no_leak(self):
                """ASP-07: calculate_aspects_vectorized(jd, aspects=CLASSICAL) returns no non-classical i_asp."""
                result = calculate_aspects_vectorized(self.jd, aspects=CLASSICAL)
                leaked = set(int(x) for x in result["i_asp"]) & NON_CLASSICAL_INDICES
                assert not leaked, f"CLASSICAL preset leaked non-classical i_asp: {leaked}"

            def test_calculate_aspects_batch_classical_no_leak(self):
                """ASP-07: calculate_aspects_batch(jd_array, aspects=CLASSICAL) returns no non-classical i_asp on any date."""
                results_per_date = calculate_aspects_batch(self.jd_array, aspects=CLASSICAL)
                all_leaked = set()
                for date_idx, result in enumerate(results_per_date):
                    if len(result):
                        leaked = set(int(x) for x in result["i_asp"]) & NON_CLASSICAL_INDICES
                        if leaked:
                            all_leaked |= leaked
                assert not all_leaked, f"CLASSICAL leaked non-classical i_asp across batch: {all_leaked}"

            def test_default_equals_classical(self):
                """ASP-04: aspects=None default behaves identically to aspects=CLASSICAL."""
                r_default = calculate_aspects(self.jd)
                r_classical = calculate_aspects(self.jd, aspects=CLASSICAL)
                # Sort by (body1, body2, i_asp) tuple for stable comparison
                def keyed(arr):
                    return sorted(
                        (int(r["body1"]), int(r["body2"]), int(r["i_asp"]), float(r["orb"]))
                        for r in arr
                    )
                assert keyed(r_default) == keyed(r_classical), (
                    "default (aspects=None) result diverges from explicit aspects=CLASSICAL"
                )

            def test_traditional_no_leak(self):
                """ASP-07: TRADITIONAL preset returns no row outside {0,1,4,7,9,11,13}."""
                result = calculate_aspects_vectorized(self.jd, aspects=TRADITIONAL)
                leaked = set(int(x) for x in result["i_asp"]) & NON_TRADITIONAL_INDICES
                assert not leaked, f"TRADITIONAL preset leaked: {leaked}"

            def test_extended_includes_non_classical(self):
                """Sanity: EXTENDED preset CAN return harmonic aspects (e.g. Quintile, Quincunx).
                On any astronomical date there is some pair-aspect coverage; we don't pin a
                specific aspect, but verify EXTENDED returns ≥ as many distinct i_asp values
                as CLASSICAL on the same date (legacy v1.0 behavior preserved)."""
                r_classical = calculate_aspects_vectorized(self.jd, aspects=CLASSICAL)
                r_extended = calculate_aspects_vectorized(self.jd, aspects=EXTENDED)
                cl_codes = set(int(x) for x in r_classical["i_asp"])
                ext_codes = set(int(x) for x in r_extended["i_asp"])
                # EXTENDED uses the matched_pairs first-aspect-wins semantic, so a CLASSICAL
                # aspect MAY be eclipsed by a closer harmonic. The correct invariant is:
                # every i_asp produced is a valid 0-13 canonical index.
                assert all(0 <= int(x) < 14 for x in r_extended["i_asp"]), "EXTENDED produced invalid i_asp"
                assert all(0 <= int(x) < 14 for x in r_classical["i_asp"]), "CLASSICAL produced invalid i_asp"

            def test_classical_results_use_canonical_iasp(self):
                """ASP-05/Pitfall 1: i_asp emitted under CLASSICAL is the canonical 0-13 index,
                NOT a position 0..4 within the filtered subset. Verifies Kala contract."""
                result = calculate_aspects_vectorized(self.jd, aspects=CLASSICAL)
                if len(result):
                    # All emitted i_asp must be in CLASSICAL_INDICES (subset of {0,4,7,9,13}).
                    # If renumbered to subset positions, we'd see {0,1,2,3,4} instead.
                    emitted = set(int(x) for x in result["i_asp"])
                    assert emitted <= CLASSICAL_INDICES, (
                        f"i_asp not canonical — got {emitted}, "
                        f"expected subset of {CLASSICAL_INDICES} (0,4,7,9,13). "
                        f"Renumbering bug per RESEARCH.md Pitfall 1."
                    )
                    # Also assert max i_asp can be 13 (Opposition is in CLASSICAL); if it's
                    # never above 4, that's a smoking gun for the renumbering bug.
                    # (We don't ASSERT max==13 because Opposition may not occur on this date,
                    # but we DO assert it's not bounded by the filtered-subset length.)

    The test count for the new class: 7 functions. Combined with the resolver tests from Plan 09-02 (≥21 functions), the file has ≥28 test functions.

    **Anti-patterns to avoid:**
    - Do NOT pass dates that have ZERO aspects of any type (would cause vacuously-true assertions). The chosen 2025-01-01 is fine — at any random date, multi-body cross-pair aspect coverage is non-empty for EXTENDED. If empty for CLASSICAL on a specific date, that's a normal data property, not a bug.
    - Do NOT compare result equality across `calculate_aspects` vs `calculate_aspects_vectorized` — they have slightly different first-match-wins semantics (per existing test patterns). Compare ONLY same-function with different `aspects=` values.
    - Do NOT add a benchmark assertion to this test class — Task 2 handles benchmark.
  </action>
  <verify>
    Run: `pytest tests/test_aspect_presets.py -v -k Integration` — all 7 integration tests pass.
    Run: `pytest tests/test_aspect_presets.py -v` — all tests (resolver + integration, ≥28 functions) pass.
    Run: `pytest tests/ -x` — full suite passes.
  </verify>
  <done>
    `tests/test_aspect_presets.py` contains `TestAspectPresetsIntegration` with 7 integration test methods; all pass; no test in the wider suite breaks. ASP-07 acceptance criteria satisfied (CLASSICAL leak = zero) verified across all three batch APIs.
  </done>
</task>

<task type="auto">
  <name>Task 2: Run benchmark comparison and capture .planning/.../benchmark-comparison.json (ASP-08)</name>
  <files>.planning/phases/09-configurable-aspects/benchmark-comparison.json</files>
  <action>
    Run the benchmark from Plan 09-01 in `--compare` mode and capture the result.

    Step 1: Verify Plan 09-04 has landed and the current HEAD has the refactored APIs:

        git log --oneline -5
        grep -n "resolve_aspect_set" ketu/aspects/calculator.py | head -3

    The grep should show the resolver imported and called.

    Step 2: Run the comparison script (apples-to-apples — Phase 9 with `aspects=EXTENDED` matches v1.0's effective default of all 14 aspects):

    Modify `tests/benchmark_aspects_batch.py` slightly if needed to support an `--aspect-set` flag for `--compare` mode. Specifically: when `--compare` is used, the script should benchmark with `aspects=EXTENDED` (to compare apples-to-apples with v1.0). This may already be the default if the script was written without `aspects=` passed (which would resolve to CLASSICAL — NOT comparable to v1.0's all-14 baseline).

    EXPLICIT update to `tests/benchmark_aspects_batch.py` (extending Plan 09-01's script):

        # Add CLI flag:
        parser.add_argument("--aspect-set", choices=["classical", "traditional", "extended"],
                            default="extended",
                            help="Which aspect preset to benchmark (default: extended for v1.0 apples-to-apples)")

        # In bench_one or main, when calling calculate_aspects_batch:
        from ketu.aspects import calculate_aspects_batch
        # ...
        result = calculate_aspects_batch(jd_array, aspects=args.aspect_set)

    Then run:

        # Phase 9 timing with EXTENDED (apples-to-apples vs v1.0 baseline):
        python tests/benchmark_aspects_batch.py --compare .planning/phases/09-configurable-aspects/baseline-v1.0.json --aspect-set extended > /tmp/cmp-extended.txt 2>&1

        # Phase 9 timing with CLASSICAL (expected SPEEDUP from 5/14 inner-loop work):
        python tests/benchmark_aspects_batch.py --capture /tmp/phase9-classical.json --aspect-set classical
        python tests/benchmark_aspects_batch.py --capture /tmp/phase9-extended.json --aspect-set extended

    Step 3: Build the comparison JSON manually using these inputs. Create `.planning/phases/09-configurable-aspects/benchmark-comparison.json`:

        {
          "version": "phase9-comparison",
          "captured_at": "<ISO-8601>",
          "git_sha": "<HEAD>",
          "baseline_ref": ".planning/phases/09-configurable-aspects/baseline-v1.0.json",
          "baseline_git_sha": "<from baseline-v1.0.json>",
          "comparisons": {
            "30":  {"baseline_mean": <s>, "phase9_extended_mean": <s>, "phase9_classical_mean": <s>,
                    "regression_pct_extended": <float>, "regression_pct_classical": <float>,
                    "asp08_pass": <bool>},
            "90":  {...},
            "365": {...}
          },
          "asp08_overall_pass": <bool>,
          "notes": "ASP-08 gate: regression_pct_extended ≤ 5% on at least one batch size constitutes pass."
        }

    `regression_pct = (phase9 - baseline) / baseline * 100`. Positive = regression. Negative = improvement.

    Step 4: Verdict logic:

    - **PASS**: every batch size's `regression_pct_extended ≤ 5.0`. Set `asp08_overall_pass = true`.
    - **CONDITIONAL PASS**: at least one batch size passes; one or more fail by a small margin (< 10%). Document magnitudes in SUMMARY.md and flag for /gsd:check-phase.
    - **FAIL**: any batch size regresses > 10%, OR all batch sizes regress > 5%. Set `asp08_overall_pass = false`. Investigate before proceeding to /gsd:check-phase. Common causes:
      * Hot loop refactor introduced an extra `np.where` per date → fix by hoisting.
      * Mask resolution moved inside per-date loop → audit `resolve_aspect_set` call sites.
      * Type-cast (`int(i_asp)`, `float(selected_angles[k])`) introduced overhead → these are necessary for the structured-array `.append`, accept the cost.

    Step 5: Always also report the CLASSICAL timing for context — Phase 9 should make CLASSICAL FASTER than v1.0 baseline (since v1.0 effectively iterated all 14 aspects, Phase 9 with CLASSICAL only iterates 5). A CLASSICAL improvement of 30-65% on inner-loop time is expected per research line 500.

    **Constraints (per quality_gate):**
    - Run benchmarks on the SAME machine that captured the baseline in Plan 09-01.
    - Do NOT run with `pytest-benchmark` (not in deps).
    - Do NOT pin the regression threshold below 5% — that's the ASP-08 contract.
    - Document any deviation from PASS in SUMMARY.md with magnitude.
  </action>
  <verify>
    `cat .planning/phases/09-configurable-aspects/benchmark-comparison.json | python -c "import json,sys; d=json.load(sys.stdin); assert 'comparisons' in d; assert all('regression_pct_extended' in v for v in d['comparisons'].values()); print('asp08_overall_pass=', d['asp08_overall_pass']); print('largest_regression=', max(v['regression_pct_extended'] for v in d['comparisons'].values()))"`
    Output shows `asp08_overall_pass=True` and largest regression ≤ 5.0. (Or if FAIL/CONDITIONAL, summary documents magnitude.)
  </verify>
  <done>
    `benchmark-comparison.json` exists with the three batch-size entries; the ASP-08 verdict (PASS / CONDITIONAL / FAIL) is recorded; if FAIL, root cause is documented in SUMMARY.md (and a follow-up gap closure is recommended via /gsd:check-phase if needed). CLASSICAL timing is captured alongside EXTENDED for context.
  </done>
</task>

</tasks>

<verification>
- `pytest tests/test_aspect_presets.py -v` — all unit + integration tests pass.
- `pytest tests/ -x` — full suite passes.
- `.planning/phases/09-configurable-aspects/benchmark-comparison.json` exists with three batch-size entries (30, 90, 365), each with `regression_pct_extended` and `regression_pct_classical` floats.
- `asp08_overall_pass` is `true` (PASS), or magnitude of any failure is documented in `09-05-SUMMARY.md`.
- The file `baseline-v1.0.json` is UNCHANGED since Plan 09-01 captured it (`git diff .planning/phases/09-configurable-aspects/baseline-v1.0.json` empty).
- Coverage check: `pytest --cov=ketu/aspects/presets --cov=ketu/aspects/calculator --cov-report=term-missing` — `presets.py` ≥95%, `calculator.py` ≥85% (project gate).
</verification>

<success_criteria>
- ASP-07 satisfied: integration test `TestAspectPresetsIntegration` covers `calculate_aspects`, `calculate_aspects_vectorized`, `calculate_aspects_batch` with CLASSICAL preset; asserts no leak of non-classical i_asp in any result; passes.
- ASP-08 satisfied: benchmark comparison run on same machine as baseline; `regression_pct_extended ≤ 5%` recorded for each batch size, or any deviation documented with magnitude in SUMMARY.md.
- Default-flip observed (`aspects=None == aspects=CLASSICAL`).
- Kala contract verified end-to-end (`test_classical_results_use_canonical_iasp`).
- TRADITIONAL preset works correctly (no leak of non-traditional indices).
- benchmark-comparison.json is committed alongside baseline-v1.0.json.
</success_criteria>

<output>
After completion, create `.planning/phases/09-configurable-aspects/09-05-SUMMARY.md` documenting:
- ASP-07 verdict: PASS (all 7 integration tests pass) — list each test and its assertion in 1 line each.
- ASP-08 verdict: PASS / CONDITIONAL / FAIL with the largest regression_pct_extended.
- CLASSICAL speedup observed (negative regression_pct_classical) on all three batch sizes — quantify (e.g. "-32% to -64% inner-loop time").
- Coverage delta: `presets.py` and `calculator.py` percentages.
- Phase 9 success criteria status (1-5 from ROADMAP):
  1. core.aspects length 14 ✓ (Plan 09-03 invariant test)
  2. CLASSICAL/TRADITIONAL/EXTENDED resolve to 5/7/14 ✓ (Plan 09-02 unit tests)
  3. CLASSICAL leak = zero ✓ (this plan)
  4. aspects=None == CLASSICAL ✓ (this plan)
  5. ≤5% regression vs baseline + CLASSICAL faster ✓/conditional (this plan)
- Phase 9 blocker note: "Kala aspect-count dependency unverified" — this plan does NOT resolve the cross-repo blocker; it's a pre-merge action item per STATE.md.
</output>
