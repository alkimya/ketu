---
phase: 09-configurable-aspects
verified: 2026-05-07T00:10:00Z
status: passed
score: 5/5 must-haves verified
re_verification: false
---

# Phase 09: Configurable Aspects Verification Report

**Phase Goal:** User can select an aspect set (5 majors default, 7 traditional, 14 extended) via Python API or named preset, with `core.aspects` remaining length-14 append-only and Kala's positional indexing preserved.
**Verified:** 2026-05-07T00:10:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `core.aspects` is length 14, dtype ('name','angle','coef'), byte-fingerprint unchanged from v1.0; invariant test fails on any reorder/deletion | VERIFIED | `len(ketu.core.aspects)==14`; sha256 matches `c5bd177316ce98d428bee011a5b0f17ae247d1dee1e478c2389af51d39afb359`; 4 invariant tests in `TestData` all pass |
| 2 | `from ketu.aspects.presets import CLASSICAL, TRADITIONAL, EXTENDED` resolves to 5, 7, 14 active aspects respectively; frozen (mutation raises) | VERIFIED | `.sum()` returns 5/7/14; `flags.writeable=False`; mutation raises `ValueError: assignment destination is read-only` |
| 3 | `calculate_aspects(...)` and both variants called with `aspects=CLASSICAL` emit zero non-classical i_asp codes (only `{0,4,7,9,13}`) | VERIFIED | 9 integration tests in `TestAspectPresetsIntegration` all pass; live check confirms `i_asp codes == [0,4,7,9,13]` |
| 4 | `aspects=None` on any of the four public APIs defaults to CLASSICAL (5 majors); downstream must opt into EXTENDED | VERIFIED | All four signatures have `aspects: AspectSetSpec = None`; `resolve_aspect_set(None)` returns CLASSICAL; `test_default_equals_classical` and `test_find_aspects_between_dates_default_equals_classical` pass |
| 5 | `calculate_aspects_batch` with `aspects=extended` shows ≤5% regression vs v1.0 baseline; LRU caches do not key on aspect set | VERIFIED | `benchmark-comparison.json` records `asp08_overall_pass=true`, largest EXTENDED delta = -10.10% (10% faster); both LRU caches (`body_properties`, `_cached_planet_position_batch`) key only on `(jd, body)`, never on aspect set |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `ketu/aspects/presets.py` | CLASSICAL/TRADITIONAL/EXTENDED frozen masks; `resolve_aspect_set` resolver; `AspectSetSpec` type | VERIFIED | 229 lines, 100% coverage, frozen arrays, resolver with 6 dispatch branches |
| `ketu/aspects/__init__.py` | Re-exports CLASSICAL, TRADITIONAL, EXTENDED, AspectSetSpec, resolve_aspect_set | VERIFIED | `from ketu.aspects import CLASSICAL, TRADITIONAL, EXTENDED, AspectSetSpec, resolve_aspect_set` succeeds |
| `ketu/aspects/calculator.py` | Four public APIs accept `aspects: AspectSetSpec = None`; hot loops enumerate `selected_indices`; `_CORE_ASPECTS` rename; resolver called once above per-date loop | VERIFIED | All four functions have `aspects=None`; `selected_iasp_ints` pre-computed above loop; `selected_orbs_per_aspect` hoisted; `_CORE_ASPECTS` throughout |
| `ketu/aspects/windows.py` | `find_aspects_timeline` default from CLASSICAL preset | VERIFIED | `_CLASSICAL_NAMES` derived from CLASSICAL mask at module level; `aspects_list = list(_CLASSICAL_NAMES)` on default path |
| `ketu/aspects/timelines.py` | `generate_aspect_timeline` default from CLASSICAL preset | VERIFIED | Same pattern |
| `ketu/aspects/transits.py` | `find_transits_to_position` + `compare_dates_transits` defaults from CLASSICAL preset | VERIFIED | Two default-block sites both migrated |
| `tests/test_ketu.py` (TestData) | 4 invariant tests: length, dtype.names, per-row name/angle/coef, sha256 fingerprint | VERIFIED | `test_aspects_length`, `test_aspects_dtype_names`, `test_aspects_structure`, `test_aspects_byte_fingerprint` — all pass |
| `tests/test_aspect_presets.py` | 56 unit tests + 9 integration tests | VERIFIED | 65 tests total; all pass |
| `tests/benchmark_aspects_batch.py` | Standalone benchmark with `--aspect-set` and `--compare` flags | VERIFIED | Script exists with argparse for `--aspect-set {classical,traditional,extended}` and `--compare` |
| `.planning/phases/09-configurable-aspects/baseline-v1.0.json` | Frozen v1.0 timing baseline | VERIFIED | File present; not modified post-capture |
| `.planning/phases/09-configurable-aspects/benchmark-comparison.json` | Phase 9 comparison result; `asp08_overall_pass=true` | VERIFIED | JSON present; `asp08_overall_pass: true`; all three batch sizes pass |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `calculator.py` APIs | `presets.py` resolver | `resolve_aspect_set(aspects)` called once at entry | WIRED | Lines 116, 174, 294, 481 in calculator.py |
| `windows.py` / `timelines.py` / `transits.py` | `presets.py` CLASSICAL | `_CLASSICAL_NAMES` module-level derivation | WIRED | 3 import blocks confirmed; 4 default sites confirmed |
| `test_aspect_presets.py` integration | `calculator.py` APIs | Direct import and call with `aspects=CLASSICAL/EXTENDED` | WIRED | 9 tests pass end-to-end |
| `benchmark_aspects_batch.py` | `calculator.py` `calculate_aspects_batch` | `_call_with_aspect_set` wrapper | WIRED | Script passes `aspects=aspect_set` to the function |
| LRU caches | aspect set independence | Cache keys contain only `(jd, body)` — no aspect parameter | WIRED | `_cached_planet_position_batch(jd_tuple, planet_id)`, `body_properties(jdate, body)` — confirmed |

### Requirements Coverage

| Requirement | Status | Notes |
|-------------|--------|-------|
| ASP-01 (core.aspects append-only, length-14 invariant) | SATISFIED | sha256 fingerprint test + length + per-row name/angle/coef |
| ASP-02 (CLASSICAL/TRADITIONAL/EXTENDED presets) | SATISFIED | 5/7/14 sums; frozen; subpackage re-exports |
| ASP-03 (calculate_aspects family accepts aspects=) | SATISFIED | All 4 signatures; `aspects: AspectSetSpec = None` |
| ASP-04 (aspects=None defaults to CLASSICAL) | SATISFIED | Confirmed on all 4 APIs + 2 integration tests |
| ASP-05 (resolver called once, above hot loops) | SATISFIED | `selected_iasp_ints` / `selected_orbs_per_aspect` hoisted above per-date loop |
| ASP-06 (LRU caches must include mask hash if aspect-set-dependent) | SATISFIED (forward-looking) | No cache materializes aspect output; rule documented in presets.py docstring |
| ASP-07 (CLASSICAL result contains zero non-classical aspects) | SATISFIED | 9 integration tests, including 3 covering all calculator variants + find_aspects_between_dates |
| ASP-08 (≤5% regression on extended vs baseline) | SATISFIED | -10.10% to -15.62% on all batch sizes (faster, not slower) |

### Anti-Patterns Found

None detected. No TODOs, FIXMEs, empty implementations, or console.log-only stubs in any of the key files.

### Human Verification Required

None. All acceptance criteria are programmable assertions covered by the test suite. The benchmark regression gate is enforced by `benchmark-comparison.json` with `asp08_overall_pass=true`.

### Summary

Phase 09 fully achieves its goal. The five observable truths are all verified against the actual codebase:

1. `core.aspects` is frozen at 14 rows with byte-level fingerprint unchanged from v1.0; the invariant test suite catches any reorder, deletion, or shape change.
2. The three preset constants (CLASSICAL=5, TRADITIONAL=7, EXTENDED=14) are frozen `np.bool_` arrays accessible from `ketu.aspects.presets` and re-exported from `ketu.aspects`.
3. All four public aspect calculation APIs (`calculate_aspects`, `_vectorized`, `_batch`, `find_aspects_between_dates`) accept `aspects: AspectSetSpec = None`; CLASSICAL results contain only canonical i_asp codes from `{0,4,7,9,13}`, preserving Kala's positional contract.
4. `aspects=None` explicitly resolves to CLASSICAL (5 majors) — the default change is observable and tested; downstream consumers must pass `aspects=EXTENDED` to get v1.0 behavior.
5. `calculate_aspects_batch` with `aspects=EXTENDED` is 10-16% faster than the v1.0 baseline (HARD GATE passed with significant margin); CLASSICAL is 33-41% faster; LRU caches do not key on the aspect set.

Total tests: 488 passing (0 failing). Full test suite runs clean.

---

_Verified: 2026-05-07T00:10:00Z_
_Verifier: Claude (gsd-verifier)_
