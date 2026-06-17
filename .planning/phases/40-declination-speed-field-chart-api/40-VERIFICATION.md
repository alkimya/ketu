---
phase: 40-declination-speed-field-chart-api
verified: 2026-06-17T16:13:37Z
status: passed
score: 6/6 must-haves verified
overrides_applied: 0
re_verification: false
---

# Phase 40: Declination Speed Field & Chart API — Verification Report

**Phase Goal:** `CHART_DTYPE` carries `body_decl_speed` (dδ/dt, deg/day) for all 14 bodies, inherited across the full chart family, with a public standstill threshold and a chart-level ascending-declination helper that Rahu can consume without computing any astronomy.
**Verified:** 2026-06-17T16:13:37Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #  | Truth | Status | Evidence |
|----|-------|--------|----------|
| 1  | `np.dtype(CHART_DTYPE).names` includes `body_decl_speed`; `compute_chart` populates it with non-zero finite float64 values; exact match with scalar `declination_velocity(jd, body)` (Δ = 0) | VERIFIED | `CHART_DTYPE.names[8] == 'body_decl_speed'`, 16 fields; Moon: chart=−3.6107, scalar=−3.6107, delta=0.0; `all(isfinite)=True`, `not all_zero=True` |
| 2  | `compute_chart` over array `jd` produces `body_decl_speed.shape == (N, 14)`, Δt = 0.01 day verbatim, no new parameter | VERIFIED | `compute_chart(jds_3, ...)["body_decl_speed"].shape == (3, 14)`; literal `0.01` in `api.py:402,411`; no parameter added |
| 3  | Synastry, composite, and returns all inherit `body_decl_speed`; composite speed differs from naïve parent midpoint | VERIFIED | `solar_return(...)['"body_decl_speed"]` finite non-zero; synastry CHART_DTYPE inputs carry field (SYNASTRY_DTYPE does not, by design); composite Moon: comp=−5.583, naïve_midpoint=−3.229, `not allclose=True` |
| 4  | Dtype ratchet test updated and passes at 16 fields (old 15-field fingerprint replaced, intentional break documented) | VERIFIED | All 5 ratchet locations in `tests/charts/test_dtype.py` updated; pytest green; `ketu/charts/core.py` comment documents v1.8 break + Kala re-pin requirement |
| 5  | `DECL_STANDSTILL_EPS` importable from `ketu.calculations`, value tested, `|dδ/dt| ≤ EPS` classifies standstill | VERIFIED | `from ketu.calculations import DECL_STANDSTILL_EPS` succeeds; `== 0.001`; in `__all__`; Sun at solstice classifies neutral; Jupiter in motion not masked |
| 6  | Chart-level `is_ascending_declination_chart` returns int8 {-1,0,+1} per body; consistent with v1.5 scalar; 100% coverage | VERIFIED | Returns `np.int8`, shape `(14,)` scalar / `(N,14)` vectorised; all three branches verified (EPS×0.5→0, EPS×2→+1, −EPS×2→−1); Sun ascending matches `is_ascending_declination(jd,0)=True`; `100.00%` coverage |

**Score:** 6/6 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `ketu/charts/core.py` | `body_decl_speed` field in `CHART_DTYPE` at index 8 (16 fields) | VERIFIED | `("body_decl_speed", "f8", (14,))` at position 8; `#:` docstring updated; Kala impact documented |
| `ketu/calculations.py` | `DECL_STANDSTILL_EPS = 0.001` exported from `__all__` | VERIFIED | Present at line 509; `#:` numpydoc docstring with empirical table; in `__all__` at line 692 |
| `ketu/charts/api.py` | FD population of `body_decl_speed` in `compute_chart` + `is_ascending_declination_chart` | VERIFIED | FD block at lines 396–411; helper at line 572; `DECL_STANDSTILL_EPS` imported at line 39 |
| `ketu/charts/__init__.py` | `is_ascending_declination_chart` exported | VERIFIED | In `from .api import ...` line 48 and `__all__` line 54 |
| `ketu/composite/api.py` | Composite `body_decl_speed` from frozen λ,β + midpoint velocities (D-01) | VERIFIED | FD block at lines 269–308; `calc_planet_position_batch` imported at line 82; `compute_chart` NOT called from composite |
| `tests/charts/test_dtype.py` | 5-location ratchet re-pinned at 16 fields | VERIFIED | All 5 locations carry `body_decl_speed`; pytest green |
| `tests/charts/test_compute_chart.py` | `TestBodyDeclSpeed` class (4 tests) | VERIFIED | present/not-zero/scalar-match/vectorised-shape/finite |
| `tests/charts/test_chart_helpers.py` | `is_ascending_declination_chart` tests (8 tests; all 3 branches) | VERIFIED | Created; import gate + dtype + shape + consistency + neutral + all-branches |
| `tests/composite/test_calculate_composite.py` | `TestBodyDeclSpeed` (4 tests incl. anti-averaging ratchet) | VERIFIED | shape/not-zero/finite/not-parent-midpoint |
| `tests/synastry/test_calculate_synastry.py` | Synastry inheritance pinning (no source edit) | VERIFIED | New test confirms CHART_DTYPE inputs carry field; SYNASTRY_DTYPE does not |
| `tests/returns/test_solar_return.py` | Returns inheritance (solar_return body_decl_speed finite+non-zero) | VERIFIED | `TestSolarReturnBodyDeclSpeedInherited` class appended |
| `tests/test_declination.py` | `TestDeclStandstillEps` (5 tests) | VERIFIED | import/value/__all__/sun-solstice-neutral/jupiter-not-masked |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `ketu/charts/api.py` | `ketu.calculations.DECL_STANDSTILL_EPS` | `from ketu.calculations import DECL_STANDSTILL_EPS` | VERIFIED | One-way import; no cycle |
| `ketu/charts/api.py compute_chart` | `_vectorised_body_properties` | Second call at `jd_b + 0.01` | VERIFIED | `_vectorised_body_properties(_jd_b1)` at line 403 |
| `ketu/composite/api.py` | `ketu.ephemeris.planets.calc_planet_position_batch` | `from ketu.ephemeris.planets import calc_planet_position_batch` | VERIFIED | Imported at line 82; used for dβ/dt midpoints |
| `ketu/composite/api.py` composite FD | `out["body_decl"] / out["body_lons"] / out["body_speeds"]` | FD on composite's frozen fields | VERIFIED | `_decl` reused as δ₀; `out["body_lons"]` + `out["body_speeds"]` advanced; `out["body_decl_speed"]` assigned |
| `tests/charts/test_dtype.py` | `ketu.charts.core.CHART_DTYPE` | field-name / shape / kind assertions | VERIFIED | 5 ratchet locations all green |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| `compute_chart` | `out["body_decl_speed"]` | `_vectorised_body_properties(jd_b + 0.01)` → coordinate chain → FD slope | Yes — FD on real ephemeris positions; Moon=-3.61 deg/day at JD 2460690 | FLOWING |
| `calculate_composite` | `out["body_decl_speed"]` | Frozen composite (λ,β) advanced by midpoint velocities from `calc_planet_position_batch` | Yes — composite Moon=-5.58 vs naïve midpoint=-3.23, ratchet confirms non-trivial | FLOWING |
| `is_ascending_declination_chart` | `speeds = chart["body_decl_speed"]` | Reads populated `body_decl_speed` from CHART_DTYPE | Yes — produces int8 {-1,0,+1}; all 3 branches reachable | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `CHART_DTYPE` has 16 fields with `body_decl_speed` at index 8 | `python -c "from ketu.charts import CHART_DTYPE; n=CHART_DTYPE.names; assert n[8]=='body_decl_speed'; assert len(n)==16"` | Assertion passes | PASS |
| `DECL_STANDSTILL_EPS == 0.001` importable | `python -c "from ketu.calculations import DECL_STANDSTILL_EPS; assert DECL_STANDSTILL_EPS == 0.001"` | Assertion passes | PASS |
| `compute_chart` populates `body_decl_speed` non-zero, matches scalar (Δ=0) | `python -c "..."` (Moon at JD 2460690) | chart=-3.6107, scalar=-3.6107, delta=0.0 | PASS |
| Vectorised `compute_chart` produces shape `(N, 14)` | `compute_chart(jds_3, ...)["body_decl_speed"].shape == (3, 14)` | Shape confirmed | PASS |
| Composite differs from naïve parent midpoint | Moon comp=-5.583, midpoint=-3.229 | `not allclose` confirmed | PASS |
| `is_ascending_declination_chart` returns int8 {-1,0,+1} | All three branch values tested | +1/−1/0 all reachable | PASS |
| Full suite green + 100% coverage | `pytest tests/ -q` | 1691 passed, 2 skipped, 100.00% | PASS |

### Probe Execution

Step 7c: SKIPPED — no probe scripts declared in phase plans or in `scripts/*/tests/probe-*.sh`.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| DSPD-01 | 40-01, 40-02 | `CHART_DTYPE` gains `body_decl_speed` field; `compute_chart` populates it | SATISFIED | `CHART_DTYPE.names[8]=='body_decl_speed'`; FD block in `api.py:396–411`; anti-zero-fill test green |
| DSPD-02 | 40-01, 40-02 | Δt = 0.01 d verbatim; agreement with scalar `declination_velocity` (Δ=0) | SATISFIED | Literal `0.01` in `api.py`; `test_body_decl_speed_matches_scalar_declination_velocity_exactly` asserts delta==0.0 |
| DSPD-03 | 40-03 | `body_decl_speed` inherited by synastry/composite/returns; composite derived from composite's own frozen λ,β | SATISFIED | Solar return and synastry inputs carry field; composite anti-averaging ratchet green (Moon: −5.58 vs −3.23) |
| DSPD-04 | 40-01 | Dtype ratchet test updated for new field; break intentional, re-pinned | SATISFIED | 5 ratchet locations in `test_dtype.py` updated; Kala positional impact documented in `core.py` |
| DSPD-05 | 40-01 | `DECL_STANDSTILL_EPS = 0.001` public, tested, in `__all__` | SATISFIED | Importable; in `__all__`; Sun at solstice → neutral; Jupiter in motion → not masked |
| DSPD-06 | 40-02 | Chart-level `is_ascending_declination_chart` helper; int8 {-1,0,+1}; consistent with v1.5 scalar | SATISFIED | Exported from `ketu.charts`; all 3 branches verified; consistency confirmed for Sun/Moon/Mercury |
| DSPD-07 | Phase 41 | Documentation en+fr | DEFERRED | Phase 41 requirement — not in scope for Phase 40 |
| REL-01 | Phase 41 | `ketu==1.8.0` shipped to PyPI | DEFERRED | Phase 41 requirement — not in scope for Phase 40 |

### Deferred Items

Items not yet met but explicitly addressed in later milestone phases.

| # | Item | Addressed In | Evidence |
|---|------|-------------|----------|
| 1 | DSPD-07: Documentation en+fr of `body_decl_speed`, Δt step, `DECL_STANDSTILL_EPS`, helper, Ketu/Rahu boundary | Phase 41 | REQUIREMENTS.md traceability: `DSPD-07 | Phase 41 | Pending` |
| 2 | REL-01: `ketu==1.8.0` shipped to PyPI via OIDC | Phase 41 | REQUIREMENTS.md traceability: `REL-01 | Phase 41 | Pending` |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `ketu/charts/api.py` | 402, 411 | `0.01` magic number (3 independent sites) | Warning (WR-01 from review) | Future edit risk: if one site is tuned the others diverge and the exact-match test breaks far from the edit. No functional issue today. |
| `ketu/charts/api.py` | 615–619 | NaN silently classified as neutral (0) | Warning (WR-02 from review) | `is_ascending_declination_chart` does not guard against non-finite inputs; NaN → 0 with no signal. `compute_chart` guarantees finite output today; the risk is with hand-built charts. |
| `ketu/composite/api.py` | 383–412 | Inline aspect loop omits Rahu↔Ketu tautological opposition suppression | Warning (WR-03 from review) | Pre-existing defect (predates v1.7); file was edited this phase for `body_decl_speed` only; out of scope for DSPD requirements. No regression introduced by this phase. |
| `ketu/charts/core.py` | 22 | `"the canonical 13-body axis"` (stale; actual axis is 14) | Info (WR-04 from review) | Doc-only contradiction; stale from before v1.3 Chiron addition. Several sites across `core.py`, `api.py`, `composite/api.py`. |

No `TBD`, `FIXME`, or `XXX` debt markers found in the files modified by this phase.

### Human Verification Required

None. All success criteria are programmatically verifiable. The WR-01/WR-02/WR-04 findings from the code review are robustness and documentation improvements, not functional regressions, and carry no human-verification requirement for the phase goal.

### Gaps Summary

No gaps. All 6 must-haves are VERIFIED against the codebase. The full test suite passes (1691 tests, 100% coverage). DSPD-07 and REL-01 are explicitly assigned to Phase 41 and are deferred, not gaps.

The four code-review findings (WR-01 magic number, WR-02 NaN silent neutral, WR-03 pre-existing composite aspect loop, WR-04 stale `(13,)` docstrings) are non-blocking observations carried forward. WR-03 in particular is pre-existing and out of scope for Phase 40's DSPD requirements. None of these findings prevent the phase goal from being achieved.

---

_Verified: 2026-06-17T16:13:37Z_
_Verifier: Claude (gsd-verifier)_
