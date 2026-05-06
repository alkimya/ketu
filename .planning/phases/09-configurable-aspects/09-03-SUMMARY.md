---
phase: 09-configurable-aspects
plan: 03
subsystem: testing
tags: [pytest, sha256, invariant, numpy, structured-array]

# Dependency graph
requires:
  - phase: 09-configurable-aspects
    provides: "core.aspects v1.0 row order, dtype, and coefficients (length-14 append-only contract)"
provides:
  - "Strengthened invariant test for `core.aspects` (length 14, dtype.names, per-row name/angle/coef, sha256 byte fingerprint)"
  - "EXPECTED_ASPECT_FINGERPRINT_V1 constant pinning v1.0 byte layout"
  - "Surgical failure messages identifying drifted row index"
affects: [09-04a-calculator-refactor, 09-04b-default-migration, 09-05-integration-and-benchmark]

# Tech tracking
tech-stack:
  added: [hashlib (stdlib)]
  patterns: ["sha256-byte-fingerprint invariant for structured arrays", "per-row enumerate-with-pytest.approx for f4 fields"]

key-files:
  created: []
  modified: [tests/test_ketu.py]

key-decisions:
  - "Use sha256 over name.tobytes() + angle.tobytes() + coef.tobytes() — catches dtype/encoding drift that field-by-field tests miss"
  - "pytest.approx(abs=1e-6) for both angles and coefs — consistent and safe for f4 storage of fractions like 1/6, 1/9"
  - "Inline computation + write in single atomic task (no empty-files orchestration step) — Warning 5 fix"
  - "Pin fingerprint as file-scope constant `EXPECTED_ASPECT_FINGERPRINT_V1` for explicit update workflow on intentional changes"

patterns-established:
  - "Invariant test pattern: length + dtype.names + per-row checks + byte fingerprint = defense in depth"
  - "Mutation testing as plan verification step: swap rows, confirm test fails surgically, revert"

# Metrics
duration: ~3min
completed: 2026-05-06
---

# Phase 9 Plan 03: Invariant Test Summary

**Strengthened `core.aspects` invariant from 4 spot-checks to 4 dedicated tests (length, dtype.names, per-row name/angle/coef, sha256 byte fingerprint) with surgical failure messages and mutation-test-verified detection.**

## Performance

- **Duration:** ~1m 35s (commit timestamp delta)
- **Started:** 2026-05-06T19:09:19Z
- **Completed:** 2026-05-06T19:10:54Z
- **Tasks:** 1 (atomic compute-fingerprint + write-test)
- **Files modified:** 1 (`tests/test_ketu.py`)

## Accomplishments

- Pinned v1.0 byte-level fingerprint of `core.aspects` (sha256 over name + angle + coef tobytes)
- Replaced weak `test_aspects_structure` (4 of 42 fields spot-checked) with 4 strict invariant tests
- Mutation test verified: swap of rows 1 and 2 in `ketu/core.py` causes BOTH `test_aspects_structure` AND `test_aspects_byte_fingerprint` to fail with surgical messages identifying the drifted row
- All 423 tests in the full suite still green; no other test affected

## Task Commits

Each task was committed atomically:

1. **Task 1: Compute fingerprint inline AND write strengthened invariant tests** - `e5a529d` (test)

## Files Created/Modified

- `tests/test_ketu.py` - Added `import hashlib`; added EXPECTED_ASPECT_NAMES/ANGLES/COEFS tuples and EXPECTED_ASPECT_FINGERPRINT_V1 constant at module scope; replaced single weak test in `TestData` with 4 invariant tests (`test_aspects_length`, `test_aspects_dtype_names`, `test_aspects_structure`, `test_aspects_byte_fingerprint`). Net delta: +117 / -5 lines (7-line spot-check became ~50 lines of invariant block + ~70 lines of pinned expected data).

## Provenance Data (Step A — Captured Verbatim)

Captured by running `python -c "..."` against `ketu.core.aspects` at HEAD `34fe73d` (still v1.0-spec):

```text
FINGERPRINT: c5bd177316ce98d428bee011a5b0f17ae247d1dee1e478c2389af51d39afb359
LEN: 14
DTYPE_NAMES: ('name', 'angle', 'coef')
NAME_DTYPE: |S16
ANGLE_DTYPE: float32
COEF_DTYPE: float32
ROW 0: b'Conjunction' 0.0 1.0
ROW 1: b'Semi-sextile' 30.0 0.16666667
ROW 2: b'Decile' 36.0 0.1
ROW 3: b'Novile' 40.0 0.11111111
ROW 4: b'Sextile' 60.0 0.33333334
ROW 5: b'Quintile' 72.0 0.2
ROW 6: b'Binovile' 80.0 0.22222222
ROW 7: b'Square' 90.0 0.5
ROW 8: b'Tredecile' 108.0 0.3
ROW 9: b'Trine' 120.0 0.6666667
ROW 10: b'Biquintile' 144.0 0.4
ROW 11: b'Quincunx' 150.0 0.8333333
ROW 12: b'Quadrinovile' 160.0 0.44444445
ROW 13: b'Opposition' 180.0 1.0
```

Cross-checked against research file lines 367-371 (Conjunction, Semi-sextile, Decile, Novile, Sextile, Quintile, Binovile, Square, Tredecile, Trine, Biquintile, Quincunx, Quadrinovile, Opposition) — match.

The 14 rows correspond to harmonics 1, 2, 3, 6, 9, and 10 (per `ketu/core.py:82` comment). Coefficients verified arithmetically: 1, 1/6, 1/10, 1/9, 1/3, 1/5, 2/9, 1/2, 3/10, 2/3, 2/5, 5/6, 4/9, 1.

## Mutation Test Result (Step C)

**Procedure:** Swapped rows 1 and 2 in `ketu/core.py:88-89` (Semi-sextile <-> Decile). Ran `pytest tests/test_ketu.py::TestData::test_aspects_structure tests/test_ketu.py::TestData::test_aspects_byte_fingerprint -v`.

**Result:** BOTH tests failed as expected.

- `test_aspects_structure`: surgical message `row 1 name drifted: got np.bytes_(b'Decile'), expected b'Semi-sextile'`
- `test_aspects_byte_fingerprint`: full hash diff `got 1aa08ead...0b3a0b5; expected c5bd1773...9afb359`

**Revert:** `git checkout -- ketu/core.py`. Re-ran TestData class -> 6/6 PASSED. Full suite re-ran -> 423 passed, no regressions.

## Decisions Made

- Use 64-char lowercase hex for the pinned fingerprint and store as a parenthesized string literal across two lines for line-length conformance.
- Use `pytest.approx(abs=1e-6)` for BOTH angles (which happen to be exact in f4 because integer-valued) and coefficients (which are NOT exact, e.g. 1/6 stored as 0.16666667 in f4). Consistent treatment, safe tolerance.
- Keep tests inside the existing `TestData` class (not a new file or class) — this is the canonical home for core-data invariants.
- Plan referenced class name `TestCoreData`; actual class is `TestData`. Used existing class name (no rename) — the fix is in the test content, not the class structure.

## Deviations from Plan

### Naming clarification

**1. [No deviation - clarification only] Existing test class is `TestData`, not `TestCoreData`**
- **Found during:** Task 1 (initial file read)
- **Note:** Plan repeatedly refers to `TestCoreData::test_aspects_structure`; the actual class hosting the existing weak test in `tests/test_ketu.py` is `TestData` (line 31). Honored the plan's intent ("update/add within the existing class hosting `test_aspects_structure`") by editing `TestData`. No rename was performed (would have caused unnecessary churn).
- **Verification:** All 4 new tests run under `tests/test_ketu.py::TestData::test_aspects_*` and pass.
- **Committed in:** `e5a529d` (single task commit)

---

**Total deviations:** 0 (one naming clarification documented for future-plan reference)
**Impact on plan:** None — plan executed exactly as written, with class name corrected from `TestCoreData` to `TestData`.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- ASP-01 satisfied: invariant test pins length 14, dtype.names, per-row name/angle/coef (with `pytest.approx`), and sha256 byte fingerprint
- Plans 09-04a (calculator refactor) and 09-04b (default migration) can proceed knowing any drift in `core.aspects` rows 0-13 will be caught with surgical error messages
- Phase 9 invariant ("append-only, rows 0-13 frozen") is now machine-enforceable — adding a new row 14+ will fail `test_aspects_length` and `test_aspects_byte_fingerprint`, forcing intentional update of expected constants (the desired workflow)
- `core.aspects` itself UNCHANGED (`git diff ketu/core.py` empty); v1.0 contract preserved

## Self-Check: PASSED

**Files:**
- FOUND: `tests/test_ketu.py` (modified, +117/-5 lines per `git diff --stat`)
- FOUND: `.planning/phases/09-configurable-aspects/09-03-SUMMARY.md` (this file)

**Commits:**
- FOUND: `e5a529d` (test commit)

**Test verification:**
- FOUND: 4 new tests pass (`test_aspects_length`, `test_aspects_dtype_names`, `test_aspects_structure`, `test_aspects_byte_fingerprint`)
- FOUND: full suite 423 passed (no regressions)
- FOUND: mutation test fails surgically on row swap, reverts cleanly
- FOUND: `EXPECTED_ASPECT_FINGERPRINT_V1` is a real 64-char lowercase hex (NOT placeholder)

---
*Phase: 09-configurable-aspects*
*Completed: 2026-05-06*
