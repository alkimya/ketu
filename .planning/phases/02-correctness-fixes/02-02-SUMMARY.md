---
phase: 02-correctness-fixes
plan: 02
subsystem: aspects
tags: [bugfix, vectorization, determinism, correctness]
dependency_graph:
  requires: []
  provides: [deterministic-aspect-calculation]
  affects: [ketu.aspects.calculator.calculate_aspects_vectorized]
tech_stack:
  added: []
  patterns: [enumerate-pattern, pair-deduplication]
key_files:
  created: []
  modified:
    - ketu/aspects/calculator.py
decisions:
  - "Use enumerate pattern to fix orb_values indexing in vectorized loop"
  - "Add matched_pairs set to prevent duplicate aspects per body pair"
  - "Match loop behavior: first aspect found for each pair wins (early return semantics)"
metrics:
  duration_seconds: 253
  duration_minutes: 4.2
  tasks_completed: 2
  tests_added: 0
  tests_fixed: 7
  files_modified: 1
  commits: 1
  completed_at: "2026-02-12T03:39:35Z"
---

# Phase 02 Plan 02: Fix Aspect Vectorization Non-determinism Summary

**One-liner:** Fixed vectorized aspect calculation to match loop version by correcting orb indexing and preventing duplicate pair matches.

## Problem

The `calculate_aspects_vectorized()` function returned different results than `calculate_aspects()`. On certain dates (e.g., 2015-06-15), the vectorized version found 31 aspects while the loop version found 28. Investigation revealed two bugs:

1. **Incorrect orb indexing:** Line 139 used `orb_values[np.where(in_orb)[0] == idx][0]` which creates a boolean mask against the full in_orb indices, causing wrong orb values or missing values
2. **Duplicate pair matching:** The vectorized version checked all aspect types for every body pair, finding multiple aspects per pair, while the loop version returns on the first aspect found

Example duplicate pairs on 2015-06-15:
- (0, 6): aspect 11 + aspect 12
- (1, 9): aspect 10 + aspect 11
- (5, 9): aspect 10 + aspect 11

## Solution

Applied two fixes to `ketu/aspects/calculator.py`:

1. **Enumerate pattern (lines 138-139):**
   ```python
   # Before:
   for idx in np.where(in_orb)[0]:
       results.append((..., orb_values[np.where(in_orb)[0] == idx][0]))

   # After:
   for i, idx in enumerate(np.where(in_orb)[0]):
       results.append((..., orb_values[i]))
   ```
   This matches the pattern already used in `calculate_aspects_batch()` at line 219.

2. **Pair deduplication (lines 117, 141-145):**
   ```python
   matched_pairs = set()

   for i_asp, aspect_angle in enumerate(aspects["angle"]):
       # ... aspect checking logic ...
       if np.any(in_orb):
           for i, idx in enumerate(np.where(in_orb)[0]):
               pair = (body1_ids[idx], body2_ids[idx])
               if pair not in matched_pairs:
                   results.append((body1_ids[idx], body2_ids[idx], i_asp, orb_values[i]))
                   matched_pairs.add(pair)
   ```
   This ensures only the first aspect found for each body pair is returned, matching the early-return semantics of `get_aspect()`.

## Verification

All regression tests pass:
- `test_vectorized_matches_loop_on_known_failure_date`: 2020-12-21 now matches (was 31 vs 30)
- `test_vectorized_matches_loop_across_dates`: All 5 parametrized dates match
- `test_vectorized_deterministic_repeated_calls`: Confirms deterministic behavior

Existing tests:
- `test_aspects_correctness`: Vectorization test now passes ✓
- Full suite: 192 tests pass, 0 failures

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking issue] Test file already exists**
- **Found during:** Task 1 start
- **Issue:** `tests/test_regression/test_bug_02_aspects.py` was already created in plan 02-01 (commit 56c2d5e)
- **Fix:** Skipped Task 1 test creation, proceeded directly to Task 2
- **Files modified:** None (file already existed)
- **Commit:** N/A (no action needed)

**2. [Rule 1 - Bug] Root cause was pair duplication, not just indexing**
- **Found during:** Task 2 execution
- **Issue:** Initial enumerate fix didn't resolve test failures. Investigation revealed vectorized version was finding multiple aspects per pair (e.g., 2015-06-15: 28 unique pairs but 31 total aspects)
- **Fix:** Added `matched_pairs` set to deduplicate, ensuring only first aspect per pair is returned
- **Files modified:** ketu/aspects/calculator.py (lines 117, 141-145)
- **Commit:** 468d7eb (included in main fix)

## Task Breakdown

| Task | Name | Commit | Duration |
|------|------|--------|----------|
| 1 | Write regression test (RED) | *skipped* | 0s |
| 2 | Fix vectorized aspect indexing (GREEN) | 468d7eb | 253s |

**Task 1 was skipped** because the test file was already created in plan 02-01. Task 2 included discovering and fixing the additional pair deduplication bug.

## Impact

**Before:** `calculate_aspects_vectorized()` returned inconsistent results, finding extra aspects due to:
- Wrong orb values from complex boolean mask indexing
- Multiple aspects per body pair (violating loop semantics)

**After:** Vectorized and loop versions produce identical results:
- Correct orb values using enumerate pattern
- One aspect per pair (first match wins)
- Deterministic across all test dates
- All 192 existing tests pass

## Files Modified

**ketu/aspects/calculator.py** (lines 117, 138-145):
- Added `matched_pairs` set for pair deduplication
- Changed loop from `for idx in np.where(in_orb)[0]:` to `for i, idx in enumerate(np.where(in_orb)[0]):`
- Changed orb indexing from `orb_values[np.where(in_orb)[0] == idx][0]` to `orb_values[i]`
- Added pair membership check before appending results

## Commits

- `468d7eb` - fix(02-02): fix vectorized aspect calculation non-determinism

## Self-Check: PASSED

All files exist and commits are present:

```bash
# File check
$ ls -la ketu/aspects/calculator.py
-rw-rw-r-- 1 loc loc 11819 Feb 12 04:39 ketu/aspects/calculator.py

# Commit check
$ git log --oneline | grep 468d7eb
468d7eb fix(02-02): fix vectorized aspect calculation non-determinism

# Test verification
$ pytest tests/test_regression/test_bug_02_aspects.py -v
========================= 7 passed in 0.52s =========================

$ pytest tests/ -v --tb=short
======================= 192 passed, 2 warnings in 7.72s ========================
```

All checks pass. BUG-02 is fully resolved.
