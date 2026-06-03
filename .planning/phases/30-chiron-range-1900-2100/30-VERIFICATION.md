---
phase: 30-chiron-range-1900-2100
verified: 2026-06-03T13:05:22Z
status: passed
score: 3/3 must-haves verified
re_verification: false
---

# Phase 30: Chiron Range 1900-2100 Verification Report

**Phase Goal:** Chiron's embedded Chebyshev coefficients span 1900-2100, validated to < 0.01° against Swiss Ephemeris (including the ~1895-1896 perihelion region near the lower bound), so callers with early-20th-century dates receive accurate Chiron positions without a runtime error.

**Verified:** 2026-06-03T13:05:22Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Blocking spike ran BEFORE .npz commit; max|Δλ| measured over 1900-2100 including perihelion edge; degree=10 kept; verdict recorded in PROJECT.md + STATE.md; spike-only (no source/test/pyproject committed) | VERIFIED | Commit 6fab1c0 modifies only `.planning/PROJECT.md` and `.planning/STATE.md`; git log confirms no tools/ketu/tests changes; PROJECT.md line 198 contains `[Phase 30-01]` row with `max delta-lon=0.001214 deg < 0.01 deg`; STATE.md line 84 contains full decision entry |
| 2 | ketu/data/chiron_coeffs.npz regenerated with jd_start=2415020.5 / jd_end=2488069.5 / shape (2283,11); Phase 24-04 actual_len fix preserved; pure-NumPy runtime (zero swisseph import) | VERIFIED | `np.load` output: shape (2283, 11), degree=10, jd_start=2415020.5, jd_end=2488069.5; chiron.py line 113 reads `actual_len = min(seg_starts[si] + seg_len, jd_end) - seg_starts[si]`; `grep -nE "^\s*(import\|from)\s+(swisseph\|swe)"` chiron.py returns empty |
| 3 | Regression tests re-pinned to span 1900-2100: pre-1950 wing (JD 2422324.5, 1920-01-01) + post-2050 wing (JD 2480764.5, 2080-01-01) pinned; 4 bounds clamp tests; full suite 1537 passed, 2 skipped, 100% coverage | VERIFIED | `_CHIRON_REFS` contains 9 entries (7 original + 2 wings); 4 bounds tests in regression file; `pytest tests/ -q` output: 1537 passed, 2 skipped, 100.00% coverage |

**Score:** 3/3 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.planning/PROJECT.md` | Key Decisions row `[Phase 30-01]` with measured max|Δλ| | VERIFIED | Line 198 confirmed present |
| `.planning/STATE.md` | Decision log entry `[Phase 30-01]` with spike verdict | VERIFIED | Line 84 confirmed present |
| `tools/gen_chiron_coeffs.py` | setup_oracle range 1900-2100; _REF_JDS includes 1920 + 2080 wings | VERIFIED | Lines 113-114: `swe.julday(1900,1,1,0.0)` and `swe.julday(2100,1,1,0.0)`; _REF_JDS contains JD 2422324.5 (1920) and 2480764.5 (2080) |
| `ketu/data/chiron_coeffs.npz` | (2283, 11), degree=10, jd_start=2415020.5, jd_end=2488069.5 | VERIFIED | Direct `np.load` confirms all four values |
| `ketu/ephemeris/chiron.py` | actual_len fix at line 113; zero swisseph import; docstrings 1900/2100 | VERIFIED | Line 113 intact; grep for swisseph import empty; no stale 1950/2050 references found |
| `tests/ephemeris/test_chiron_unit.py` | Shape assertions (2283, 11) and (2283,) | VERIFIED | Lines 55-58 confirmed |
| `tests/ephemeris/test_chiron_regression.py` | 9 refs spanning 1920-2080; 4 bounds tests | VERIFIED | `_CHIRON_REFS` has 9 entries (JD 2422324.5 through 2480764.5); 4 bound test functions confirmed |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| Spike (commit 6fab1c0) | `.planning` decision log only | Spike ephemeral in /tmp; only planning files modified | WIRED | Commit touches only `.planning/PROJECT.md` and `.planning/STATE.md` |
| `tools/gen_chiron_coeffs.py setup_oracle` | `ketu/data/chiron_coeffs.npz` | `generate_all_coefficients(jd0,jd1)` over 1900-2100 | WIRED | `swe.julday(2100,...)` present; .npz reflects 2283 segs/jd_end=2488069.5 |
| `chiron.py _eval_chiron_qty` line 113 | `data['jd_end']` = 2488069.5 | `actual_len = min(...)` reads jd_end from .npz | WIRED | Line 113 intact; reads `jd_end` parameter which comes from loaded .npz |
| `gen_chiron_coeffs.py --dump-refs` | `test_chiron_regression.py _CHIRON_REFS` | Oracle longitudes captured and pinned | WIRED | 1920 ref (2.609080°) and 2080 ref (36.885249°) match Summary capture table |

---

### Requirements Coverage

| Requirement | Status | Notes |
|-------------|--------|-------|
| CHIR-09: 1900 lower bound | SATISFIED | jd_start=2415020.5 confirmed; bounds test at jd_start passes |
| CHIR-10: .npz regenerated 1900-2100 | SATISFIED | (2283, 11), degree=10, both JD bounds confirmed |
| CHIR-11: regression tests span 1900-2100 | SATISFIED | 9 refs from 1920-2080; gate 0.001214° < 0.01° |

---

### Anti-Patterns Found

None. No TODO/FIXME/PLACEHOLDER markers found in the 4 phase files. No stale 1950/2050 references remain in chiron.py. No stub implementations.

---

### Human Verification Required

None. All goal criteria are verifiable programmatically and all automated checks passed.

---

### Git History Verification

Commit sequence confirms spike-before-regeneration ordering:
- `6fab1c0` (spike verdict): only `.planning/PROJECT.md` and `.planning/STATE.md`
- `55cf95b` (30-01 SUMMARY): only `.planning/` files
- `9bb30ce` (30-02 Task 1): `tools/gen_chiron_coeffs.py` + `ketu/data/chiron_coeffs.npz`
- `6503f9b` (30-02 Task 2): `ketu/ephemeris/chiron.py` + `tests/ephemeris/test_chiron_unit.py`
- `ebdfe8d` (30-02 Task 3): `tests/ephemeris/test_chiron_regression.py`

All 5 declared source/test/data files land in 30-02 commits, after the spike-only 30-01 commits. Zero leftover spike artifacts under the repo tree.

---

_Verified: 2026-06-03T13:05:22Z_
_Verifier: Claude (gsd-verifier)_
