---
phase: 23-spike-chiron
verified: 2026-05-29T19:17:07Z
status: passed
score: 3/3 must-haves verified
---

# Phase 23: Spike Chiron Verification Report

**Phase Goal:** A measured go/no-go on Chebyshev-by-segment for Chiron — segment size, polynomial degree, coefficient array size, and achieved longitude accuracy vs Swiss Ephemeris are documented before any production code is planned.
**Verified:** 2026-05-29T19:17:07Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| #   | Truth                                                                                                                                   | Status     | Evidence                                                                                                                   |
| --- | --------------------------------------------------------------------------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------- |
| 1   | Chebyshev-by-segment fit run on real measurements; seg size, degree, coeff array size, and accuracy vs Swiss Ephemeris documented       | VERIFIED   | 23-MEASUREMENTS.md: 5-config sweep, primary (32j/deg=10), n_segs=1142, 11 coeffs/seg, 98.1 KB lon-only, max\|Δλ\|=0.000861° |
| 2   | Achievable accuracy < 0.01° documented OR real boundary + tuning documented; written go/no-go decision exists                           | VERIFIED   | 23-DECISION.md: explicit "GO" at line 12; "ATTEINT" at line 44; 11.6× margin over 1950-2050; worst segment 2027-04-20      |
| 3   | Spike artifact captured in phase directory; deliverable is data + decision, NOT production runtime code; ketu/tests/pyproject.toml untouched | VERIFIED   | `git diff --name-only 38ae4f1..HEAD -- ketu/ tests/ pyproject.toml` = empty; spike script is outside all three; pytest collection unchanged (1353 collected pre and post) |

**Score:** 3/3 truths verified

---

### Required Artifacts

| Artifact                                                              | Expected                                              | Status    | Details                                              |
| --------------------------------------------------------------------- | ----------------------------------------------------- | --------- | ---------------------------------------------------- |
| `.planning/phases/23-spike-chiron/spike_chiron_chebyshev.py`          | Runnable spike: fit + accuracy measurement vs swe     | VERIFIED  | 446 lines; contains `set_ephe_path`, unwrap logic, 200-pt grid, all-segments loop, 5 configs |
| `.planning/phases/23-spike-chiron/23-MEASUREMENTS.md`                 | SPK-01 measurement table with run metadata            | VERIFIED  | 133 lines; full sweep table, lat/dist errors, worst segment, retflag, methodology guards |
| `.planning/phases/23-spike-chiron/23-DECISION.md`                     | SPK-02 go/no-go decision record                       | VERIFIED  | 277 lines; explicit GO, locked Phase 24 params, .npz layout, insertion points, scope guardrail |

---

### Key Link Verification

| From                              | To                                    | Via                                                        | Status  | Details                                                              |
| --------------------------------- | ------------------------------------- | ---------------------------------------------------------- | ------- | -------------------------------------------------------------------- |
| `spike_chiron_chebyshev.py`       | `swisseph (swe.CHIRON oracle)`        | `swe.set_ephe_path()` then `swe.calc_ut(jd, swe.CHIRON, FLG_SWIEPH|FLG_SPEED)` | WIRED   | `set_ephe_path` at line 43; `swe.FLG_SWIEPH | swe.FLG_SPEED` at line 49, 111, 132, 143 |
| `spike_chiron_chebyshev.py`       | `numpy.polynomial.chebyshev`          | `Chebyshev.fit` for fit; `chebval` for dense-grid eval     | WIRED   | `from numpy.polynomial.chebyshev import Chebyshev, chebval` at line 28; used in `fit_and_measure_segment` |
| `23-MEASUREMENTS.md`              | spike script output                   | table transcribed from script printed results              | WIRED   | `0.000861` appears in table; methodology guards section matches script logic exactly |
| `23-DECISION.md`                  | `23-MEASUREMENTS.md`                  | accuracy numbers + chosen config from measurement table    | WIRED   | `0.000861` and `11.6×` consistent across both files; DECISION.md header cites MEASUREMENTS.md |
| `23-DECISION.md`                  | `ketu/ephemeris/planets.py` (Phase 24 insertion points) | references BODY_INDICES / SWE_IDS / BODY_STRATEGIES | WIRED   | Sections 6.1–6.4 in DECISION.md reference each insertion point with line numbers |

---

### Requirements Coverage

| Requirement | Status    | Blocking Issue |
| ----------- | --------- | -------------- |
| SPK-01      | SATISFIED | Spike script + 23-MEASUREMENTS.md deliver the measured table with n_segs, coeff counts, .npz sizing, max\|Δλ\|, lat/dist error, worst segment, methodology guards |
| SPK-02      | SATISFIED | 23-DECISION.md delivers the explicit GO verdict derived from measured accuracy (0.000861° < 0.01°), locked Phase 24 parameters, .npz layout, seas_18.se1 setup requirement, and scope guardrail |

---

### Critical Constraint: No Production Code Added

| Check                                               | Result                    | Evidence                                                                      |
| --------------------------------------------------- | ------------------------- | ----------------------------------------------------------------------------- |
| No new files under `ketu/`                          | CLEAN                     | `git diff --name-only --diff-filter=A 38ae4f1..HEAD -- ketu/` = empty        |
| No new files under `tests/`                         | CLEAN                     | `git diff --name-only --diff-filter=A 38ae4f1..HEAD -- tests/` = empty       |
| No modifications to `pyproject.toml`                | CLEAN                     | `git diff --name-only 38ae4f1..HEAD -- pyproject.toml` = empty               |
| Spike script not collected by pytest                | CONFIRMED                 | `pytest --collect-only -q` output contains no `chiron`; script lives in `.planning/` |
| Test suite count unchanged                          | CONFIRMED                 | 1353 collected (1351 passed + 2 skipped) both before and after phase 23 — matches phase 22 VERIFICATION baseline |

Note: the plan text says "1351 tests" and the SUMMARY says "1 351 tests" — both refer to the *passed* count, not the collected count (1353). This is consistent with the phase 22 VERIFICATION baseline which reported "1351 passed, 2 skipped." No discrepancy.

---

### Anti-Patterns Found

None. The spike script contains no `TODO`/`FIXME` markers, no empty implementations, and no stubs. It is explicitly a throwaway script (documented as such in the module docstring) and is never imported by ketu/ code.

---

### Human Verification Required

None required for this phase. All deliverables are documentation + a throwaway script; no runtime behavior, UI, or external service integration needs human testing. The measurement numbers in 23-MEASUREMENTS.md are the ground truth — the script was run and its output transcribed.

---

## Summary

Phase 23 achieves its goal. The spike delivers:

1. A runnable Chebyshev-by-segment fit script (`spike_chiron_chebyshev.py`, 446 lines) that runs against live pyswisseph with correct methodology: longitude unwrapped before fit, 200-point distinct validation grid, MAX (not RMS) error metric, all 1142 segments over 1950-2050 tested.

2. A measurement record (`23-MEASUREMENTS.md`, 133 lines) capturing the 5-config sweep with concrete numbers, run metadata (retflag=260, Moshier fallback, numpy/swisseph versions), lat/dist accuracy, and worst-segment identification.

3. A go/no-go decision (`23-DECISION.md`, 277 lines) with an explicit GO verdict (max|Δλ|=0.000861°, 11.6× safety margin under 0.01°), locked Phase 24 parameters (seg=32j, degree=10, 3 quantities), .npz layout, ephemeris-file setup requirement, Phase 24 insertion-point references, and an explicit scope guardrail.

The critical constraint is fully satisfied: zero files added or modified under `ketu/`, `tests/`, or `pyproject.toml`. The 1353-test suite and 100% coverage gate are untouched.

---

_Verified: 2026-05-29T19:17:07Z_
_Verifier: Claude (gsd-verifier)_
