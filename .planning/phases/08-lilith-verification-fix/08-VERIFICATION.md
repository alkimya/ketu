---
phase: 08-lilith-verification-fix
verified: 2026-05-06T18:03:08Z
status: passed
score: 5/5 must-haves verified
re_verification: false
---

# Phase 8: Lilith Verification & Fix — Verification Report

**Phase Goal:** Lilith longitude is provably correct against Swiss Ephemeris over 1900-2050, with the formula's definition documented before any code change.
**Verified:** 2026-05-06T18:03:08Z
**Status:** PASSED
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `docs/LILITH_DEFINITION.md` exists with Mean Apogee definition, tropical longitude convention, and Chapront-Touze/Francou citation, committed before formula changes | VERIFIED | File at 263 lines; commit `596da4c` predates formula fix `39e3a71`; grep confirms SE_MEAN_APOG, Chapront, tropical, 83.3532 (legacy), 0.01 deg tolerance with arithmetic derivation |
| 2 | Cross-check harness runs 5+ dates spanning 1900-2050 and passes within documented tolerance | VERIFIED | `pytest tests/test_lilith_cross_check.py -v` reports 10 passed (5 user-tolerance at 0.01 deg + 5 regression-baseline at 0.005 deg); dates are 1900-06-15, 1950-03-21, 2000-01-01, 2025-09-23, 2050-12-21 |
| 3 | Empirical error was >0.01 deg, so corrected formula landed with regression tests pinning new values | VERIFIED | Pre-fix MAX delta = 179.936579 deg (Plan 03); formula corrected in `39e3a71`; regression baseline `REGRESSION_TOLERANCE_DEG = 0.005` in test file; post-fix max delta = 0.002693 deg (5 dates) / 0.007815 deg (55K samples) |
| 4 | `ketu[test]` install pulls `pysweph>=2.10.3.6`; runtime wheel does NOT | VERIFIED | `pyproject.toml` lines 41-44: pysweph only under `[project.optional-dependencies].test`; runtime `dependencies` is `["numpy>=1.20.0"]` only; no `import swisseph` in any `ketu/` module |
| 5 | CHANGELOG and UPGRADING document Lilith value changes with explicit magnitude | VERIFIED | CHANGELOG.md `[1.1.0]` entry cites 179.936579 deg (pre-fix), 0.002693 deg and 0.007815 deg (post-fix); UPGRADING.md `v1.0 -> v1.1` section has 5-row per-date table showing ~180 deg shift; all three magnitudes consistent across CHANGELOG, UPGRADING, and LILITH_DEFINITION.md |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `docs/LILITH_DEFINITION.md` | Definition doc with formula, frame, source, tolerance, history | VERIFIED | 263 lines; 9 sections present; History filled in by Plan 04 (no `[TO BE FILLED]` sentinel); intro prose at line 8 retains stale forward-reference phrase but History section body is complete |
| `tests/test_lilith_cross_check.py` | 5-date parametrized harness vs `swe.MEAN_APOG`, `TOLERANCE_DEG = 0.01`, importorskip gate | VERIFIED | 180 lines; `TOLERANCE_DEG = 0.01`, `REGRESSION_TOLERANCE_DEG = 0.005`, `pytest.importorskip("swisseph")` module-level gate, 5 dates spanning 1900-2050 |
| `pyproject.toml` `[project.optional-dependencies].test` | `pysweph>=2.10.3.6` as test-only dep | VERIFIED | Lines 41-44 confirmed; runtime `dependencies` unchanged at `["numpy>=1.20.0"]` |
| `ketu/ephemeris/orbital.py` (formula + constants) | v1.1 formula with 5 private named constants; old literal removed from live code | VERIFIED | `_LILITH_MEAN_EPOCH_DEG = 263.3521188770`, `_LILITH_MEAN_RATE_DEG_PER_DAY = 0.1114036699`, 3 perturbation constants; old literals `83.3532`/`0.1114040803` appear only in comments |
| `ketu/ephemeris/planets.py` (wiring) | Imports `_LILITH_MEAN_RATE_DEG_PER_DAY` and uses it at `lon_speed` and `avg_speeds[12]` | VERIFIED | Import confirmed at line 14; `lon_speed = _LILITH_MEAN_RATE_DEG_PER_DAY` at line 156; `avg_speeds[12] = round(_LILITH_MEAN_RATE_DEG_PER_DAY, 6)` at line 461 |
| `CHANGELOG.md` | v1.1.0 entry with explicit Lilith magnitude | VERIFIED | `## [1.1.0] - UNRELEASED` section present; 179.936579 deg, 0.002693 deg, 0.007815 deg all cited; deviation from pure Chapront linear disclosed explicitly |
| `UPGRADING.md` | v1.0 -> v1.1 section with per-date table and migration recipe | VERIFIED | `## v1.0 -> v1.1` section with 5-row per-date table (live-computed values); action required, downstream consumer notes, deviation transparency |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `docs/LILITH_DEFINITION.md` | `ketu/ephemeris/orbital.py` (formula) | Formula section with `263.3521188770` and `0.1114036699` plus perturbation constants | WIRED | Definition doc quotes v1.1 formula verbatim; orbital.py constants match exactly |
| `docs/LILITH_DEFINITION.md` | Swiss Ephemeris `SE_MEAN_APOG` (constant 12) | Named correspondence section | WIRED | `SE_MEAN_APOG` appears at lines 17, 19, 144 of definition doc |
| `tests/test_lilith_cross_check.py` | `ketu.ephemeris.orbital.get_lilith_position` | Direct call in test functions | WIRED | `from ketu.ephemeris.orbital import get_lilith_position` + `swe.calc_ut(jd, swe.MEAN_APOG)` both in test |
| `ketu/ephemeris/planets.py` | `ketu/ephemeris/orbital.py` | `from .orbital import _LILITH_MEAN_RATE_DEG_PER_DAY` | WIRED | Import confirmed; used at `lon_speed` and `avg_speeds[12]` |
| `UPGRADING.md` | Lilith magnitude (v1.0 -> v1.1 shift) | Per-date table with `signed_circular_diff(v1.1, v1.0)` | WIRED | 5-row table with concrete values (e.g. 1900: v1.0=352.812244, v1.1=172.874759, delta=-179.937486) |

### Wave 3 Deviation Assessment

The SUMMARY context notes that Plan 04 added one `sin()` perturbation term beyond a pure Chapront secular linear formula to meet the <0.01 deg goal. Post-fix max delta = 0.002693 deg on the 5 plan dates / 0.007815 deg over 55K daily samples.

**Does this deviation impact goal achievement?** No. The phase goal is "Lilith longitude is provably correct against Swiss Ephemeris over 1900-2050." The standard is agreement with `swe.MEAN_APOG` within the documented tolerance, not adherence to a particular derivation method. The deviation is:

1. **Documented** — CHANGELOG, UPGRADING, and LILITH_DEFINITION all explicitly state "linear secular term + 1 sin() perturbation, not a raw ELP-2000 polynomial."
2. **Within tolerance** — 0.007815 deg < 0.01 deg over the full 1900-2050 window.
3. **Honest** — the perturbation fits an actual residual in the swe.MEAN_APOG reference, not an arbitrary fudge.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `docs/LILITH_DEFINITION.md` | 8 | Stale intro prose says "History section closes with a placeholder filled in by Plan 04" — but the History section IS complete | Info | None — the History section body is fully populated; only the intro description is stale |
| `ketu/ephemeris/planets.py` | 300 | `# Simple equal house system as placeholder` | Info | Pre-existing, unrelated to Phase 8; house system stub is out of scope |

No blockers. No unfilled sentinel strings (`[TO BE FILLED]`, `A.AAAAAA`, etc.) found in any Phase 8 artifact.

### Human Verification Required

None. All acceptance criteria are mechanically verifiable:

- Harness runs and passes: confirmed by live `pytest` execution (10 passed).
- Tolerance numeric: 0.002693 deg and 0.007815 deg are both < 0.01 deg (arithmetic).
- AGPL isolation: confirmed by pyproject.toml structure and absence of `import swisseph` in `ketu/` modules.
- Documentation content: confirmed by targeted grep.

### Commits (All Verified Present)

| Commit | Description | Plan |
|--------|-------------|------|
| `596da4c` | docs(08-01): document Mean Apogee definition and Chapront citation | 01 |
| `d813ee4` | chore(08-02): add pysweph as test-only optional dependency | 02 |
| `2ff8c92` | test(08-03): add Lilith cross-check harness vs Swiss Ephemeris MEAN_APOG | 03 |
| `143072a` | fix(08-03): adapt cross-check harness to pysweph 2.10.3.6 ABI | 03 |
| `39e3a71` | fix(08-04): correct Lilith mean apogee formula across 4 plumbing sites | 04 |
| `8af6085` | test(08-04): add regression-baseline harness pinning v1.1 Lilith fit | 04 |
| `2bce430` | docs(08-04): update LILITH_DEFINITION.md Formula and History for v1.1 fix | 04 |
| `3b18290` | docs(08-05): add v1.1.0 Lilith correction entry to CHANGELOG | 05 |
| `1907af6` | docs(08-05): add v1.0 -> v1.1 Lilith migration section to UPGRADING | 05 |

All 9 commits present in `git log --all`.

---

_Verified: 2026-05-06T18:03:08Z_
_Verifier: Claude (gsd-verifier)_
