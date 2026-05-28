---
phase: 18-solar-lunar-returns
verified: 2026-05-28T16:53:40Z
status: passed
score: 6/6 ROADMAP criteria verified (+ pure-NumPy contract verified)
human_verification:
  - test: "Astro.com manual cross-check of the 6 oracle resolved instants"
    expected: "Resolved Sun/Moon return JDs agree with Astro.com to sub-second (Sun) / sub-arcsec (Moon) after convention alignment"
    why_human: "Astro.com UI is bot-blocked (Phase 16/17 precedent); deferred 30-min manual task. NOT a Phase 18 blocker — pyswisseph CI cross-check is the runnable substitute (strictly stronger than Phase 17 which had only Astro.com deferred)."
notes:
  - severity: warning
    item: "pyproject.toml [project.optional-dependencies].test lists `pysweph>=2.10.3.6` — likely a typo of `pyswisseph`. The runtime module is `swisseph` (from the PyPI `pyswisseph` package) and IS installed/imported by the oracle test. The contract (swisseph NOT in [project.dependencies]) is satisfied, but `pip install ketu[test]` would fail to install the correct cross-check dependency."
  - severity: info
    item: "pyswisseph cross-check tolerance was relaxed from the planned 0.001° (3.6\") to per-body 0.01° (solar) / 0.75° (lunar). This is explicitly anticipated by the contract ('per-body tolerance relaxed for documented physical reasons') and pinned with measured ephemeris-theory deltas (Ketu bespoke Sun / truncated-Meeus Moon vs pyswisseph Moshier ELP) in each fixture's cross_check_rationale + 18-04-NOTES.md. The PRIMARY gate remains self-consistency at tolerance_deg=0.0001."
---

# Phase 18: Solar + Lunar Returns (Standard + Relocated) Verification Report

**Phase Goal:** Users compute the solar return chart for any natal birth and any target year AND the lunar return chart for any natal birth and any target date (>=27.32-day periodicity), optionally relocating either return chart to a different lat/lon, with arc-second convergence on both resolved return times — Solar and Lunar share a single pure-NumPy `_solve_return` core.

**Verified:** 2026-05-28T16:53:40Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (6 ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | `solar_return(natal_jd, natal_lat, natal_lon, target_year, return_lat=None, return_lon=None, system="placidus")` returns CHART_DTYPE; relocation via return_lat/lon, None→natal | ✓ VERIFIED | `ketu/returns/solar.py:27-195` exact signature; `compute_chart(...)` returns CHART_DTYPE; `chart_lat = natal_lat if return_lat is None else return_lat` (L185-186). Tests: `test_relocation_changes_houses_not_bodies`, `test_returns_chart_dtype`. 16 solar tests pass. |
| 2 | `lunar_return(...target_jd...)` returns CHART_DTYPE for FIRST Moon return >= target_jd; same relocation; API asymmetry documented LOUDLY | ✓ VERIFIED | `ketu/returns/lunar.py:52-284` exact signature; first-return contract enforced via seed-cycle search `if candidate >= target_jd_f - _TOL_DAYS` (L259). Docstring "API asymmetry vs solar_return -- LOUD" (L133). Tests: `test_resolved_jd_is_at_or_after_target`, `test_resolved_jd_is_within_one_period_of_target`. 23 lunar tests pass. |
| 3 | Single internal `_solve_return(...)`; BOTH solar+lunar call it (NO inline bisection); wrap-around centralised + pinned on Sun AND Moon | ✓ VERIFIED | `ketu/returns/_solve.py:108` is the sole bisection. solar.py L177 + lunar.py L244 both call `_solve_return`. NO `while`/bisection loop in solar.py/lunar.py (only `for n in range(3)` cycle-seed search in lunar). `_signed_residual_deg` (L61) centralises wrap. Helper tests: `TestSolveReturnSunWrapAround` + `TestSolveReturnMoonWrapAround`. |
| 4 | Both returns converge to <1 arc-second of target body longitude, reported as test verdict | ✓ VERIFIED | `_TOL_DEG = 1.0/3600.0` (L53); `if abs(r_mid) < tol_deg: return` (L228). Tests `test_residual_under_one_arcsecond` (solar+lunar) assert resolved residual < 1″. Convergence ratchet: `test_sun_converges_in_under_30_iterations`, `test_moon_converges_in_under_30_iterations`. |
| 5 | 3 solar + 3 lunar oracles (each incl. wrap-around); lunar incl. day-after-target | ✓ VERIFIED | 6 fixtures present: `oracle_solar_{diana_1980,curie_1900,aries_seam_1970}.json` + `oracle_lunar_{diana_2000,curie_day_after,pisces_seam_1990}.json`. `test_day_after_target_calendar_pin` asserts `resolved_date > target_date`. Wrap-around: `test_wrap_around_natal_near_seam` over both seam fixtures. 15 oracle tests pass. |
| 6 | Both docstrings distinguish LOUDLY natal_lat/lon (body ref) vs return_lat/lon (houses) | ✓ VERIFIED | solar.py L100 + lunar.py L163: "`natal_lat/lon` vs `return_lat/lon` -- distinguish LOUDLY". Sentinel tests `test_natal_lat_does_not_affect_jd` (both) assert identical JD across natal_lat values. |

**Score:** 6/6 truths verified

### Additional Contract: PURE-NumPy runtime + test-only pyswisseph

| Truth | Status | Evidence |
| --- | --- | --- |
| `ketu/returns/` has NO swisseph import | ✓ VERIFIED | `grep -rn "swisseph" ketu/returns/` → 0 matches. `ketu.returns` imports + public API resolve with `sys.modules['swisseph']=None`. |
| No swisseph in [project.dependencies] | ✓ VERIFIED | `[project].dependencies = ["numpy>=1.20.0"]` only (pyproject.toml:37-39). All `swisseph` strings in `ketu/` runtime are comments/docstrings, not imports. |
| pyswisseph is test-only | ⚠️ VERIFIED w/ WARNING | Listed under `[project.optional-dependencies].test` (pyproject.toml:42-44), NOT runtime — BUT name is `pysweph` (typo of `pyswisseph`). Oracle test imports correct module `swisseph as swe` with graceful `pytest.skip` fallback. |
| Self-consistency (tolerance_deg=0.0001) is PRIMARY gate | ✓ VERIFIED | `test_self_consistency` (oracle L268) asserts API reproduces resolved JD to `tolerance_deg`=0.0001. |
| pyswisseph cross-check = test-only external validation, per-body tolerance relaxed for documented physical reasons | ✓ VERIFIED | `test_pyswisseph_cross_check` runs (NOT skipped, swisseph 2.10.03 installed). Per-body tolerances solar 0.01° / lunar 0.75° documented with measured ephemeris-theory deltas (oracle L340-366). |

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `ketu/returns/_solve.py` | Shared `_solve_return` + `_signed_residual_deg` + constants | ✓ VERIFIED | 239 lines, substantive bisection; 100% coverage. |
| `ketu/returns/solar.py` | `solar_return` delegating to helper | ✓ VERIFIED | 196 lines; delegates L177; 100% coverage. |
| `ketu/returns/lunar.py` | `lunar_return` delegating to helper, n=0,1,2 seed search | ✓ VERIFIED | 285 lines; delegates L244; seed-cycle `for n in range(3)`; 100% coverage. |
| `ketu/returns/__init__.py` | Re-exports + `__all__` + LOUD Notes | ✓ VERIFIED | `__all__ = ["lunar_return", "solar_return"]`; 100% coverage. |
| `tests/returns/` suite | RET/LRET surface + oracle + helper tests | ✓ VERIFIED | 76 tests pass (solve 16, solar 16, lunar 23, oracle 15, gate 1, paths 5). |
| 6 oracle fixtures | 3 solar + 3 lunar | ✓ VERIFIED | All present; day-after + 2 seam fixtures included. |
| `pyproject.toml` | `ketu.returns` package + `returns_coverage_gate` marker | ✓ VERIFIED | Package listed (L61); marker alphabetical between houses & synastry (L82). |
| `Makefile` | `returns-coverage` target + `.PHONY` | ✓ VERIFIED | Target L92-94; in `.PHONY` L11; `make returns-coverage` exits 0 at 100%. |
| `CHANGELOG.md` | `## [Unreleased] ### Added` returns surface | ✓ VERIFIED | Entries L99-144; additive only. |
| `.planning/REQUIREMENTS.md` | RET-01..06 + LRET-01..05 → Done | ✓ VERIFIED | All 11 checkboxes `[x]`; status table all "Phase 18 | Done". |
| Back-references (charts/composite/synastry `__init__`) | See Also → ketu.returns | ✓ VERIFIED | All three reference `ketu.returns.solar_return` + `lunar_return`. |
| `18-04-NOTES.md` | pyswisseph/Astro-Seek/Astro.com probe results | ✓ VERIFIED | Present (12.5 KB). |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| solar.py | `_solve_return` | delegated bisection body_id=0 | ✓ WIRED | L177 `_solve_return(body_id=0, ...)` |
| lunar.py | `_solve_return` | delegated bisection body_id=1 | ✓ WIRED | L244 `_solve_return(body_id=1, ...)` |
| solar/lunar.py | `calc_planet_position` | read natal body lon | ✓ WIRED | solar L170 `(natal_jd), 0`; lunar L215 `(natal_jd), 1` |
| solar/lunar.py | `compute_chart` | assemble CHART_DTYPE + hard-wired polar_fallback | ✓ WIRED | Both call `compute_chart(..., polar_fallback="porphyry")` |
| `_solve_return` | `calc_planet_position_batch` | vectorised per-iter eval | ✓ WIRED | _solve.py L209, L224 |
| `_signed_residual_deg` | composite/porphyry wrap convention | `((x - ref + 540) % 360) - 180` | ✓ WIRED | _solve.py L105 verbatim match |
| oracle test | `solar_return` + `lunar_return` | imports + invokes both | ✓ WIRED | oracle L49 import; both invoked in self-consistency + cross-check |
| oracle test | swisseph (test-only) | cross-check bisection | ✓ WIRED | imports `swisseph as swe` with skip fallback; cross-check PASSED (not skipped) |

### Requirements Coverage

| Requirement | Status | Notes |
| --- | --- | --- |
| RET-01 (solar_return signature + relocation) | ✓ SATISFIED | Truth #1 |
| RET-02 (pure-NumPy root-finding + wrap-around) | ✓ SATISFIED | Truth #3 |
| RET-03 (<1 arcsec convergence) | ✓ SATISFIED | Truth #4 |
| RET-04 (3+ solar oracles incl wrap-around) | ✓ SATISFIED | Truth #5 |
| RET-05 (natal vs return lat/lon docstring) | ✓ SATISFIED | Truth #6 |
| RET-06 (>=95% coverage gate) | ✓ SATISFIED | 100% on ketu/returns/; `make returns-coverage` exit 0 |
| LRET-01 (lunar_return first-return >= target_jd) | ✓ SATISFIED | Truth #2 |
| LRET-02 (shared _solve_return factorisation) | ✓ SATISFIED | Truth #3 |
| LRET-03 (<1 arcsec convergence) | ✓ SATISFIED | Truth #4 |
| LRET-04 (3+ lunar oracles incl wrap + day-after) | ✓ SATISFIED | Truth #5 |
| LRET-05 (target_jd semantics + lat/lon docstring) | ✓ SATISFIED | Truth #6 |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| (none in ketu/returns/) | — | — | — | TODO/FIXME/stub scan clean; only `...` is in a docstring example (solar.py:161) |
| pyproject.toml | 43 | `pysweph` (typo of `pyswisseph`) | ⚠️ Warning | `pip install ketu[test]` installs wrong/nonexistent cross-check dep; does NOT affect runtime purity contract |

### Human Verification Required

1. **Astro.com manual cross-check** of the 6 oracle resolved instants.
   - Expected: resolved Sun/Moon return JDs agree with Astro.com to sub-second (Sun) / sub-arcsec (Moon) after convention alignment.
   - Why human: Astro.com UI is bot-blocked (Phase 16/17 precedent). Deferred 30-min manual task; documented in 18-04-NOTES.md + 18-05-SUMMARY.md. NOT a Phase 18 blocker — the pyswisseph CI cross-check is the runnable substitute (strictly stronger than Phase 17).

### Gaps Summary

No goal-blocking gaps. All 6 ROADMAP success criteria are achieved in the actual codebase, the pure-NumPy runtime contract holds (zero swisseph imports in `ketu/`, numpy-only `[project.dependencies]`), and the full project suite passes (1253 passed, 2 pre-existing Phase-17 skips). The shared `_solve_return` core is genuinely factored — both public APIs delegate, with no inline bisection. Coverage on `ketu/returns/` is 100% and `make returns-coverage` exits 0.

Two non-blocking items remain:

- **WARNING:** `pyproject.toml` test-extra names the cross-check dependency `pysweph` rather than `pyswisseph`. The runtime purity contract is unaffected (it is NOT in `[project.dependencies]`), and the installed environment already has `swisseph` 2.10.03 so the cross-check actually runs and passes. But `pip install ketu[test]` from a clean environment would fail to provision the intended dependency. Recommend correcting `pysweph` → `pyswisseph`.
- **INFO:** The pyswisseph cross-check tolerance was relaxed from the planned 0.001° to per-body 0.01° (solar) / 0.75° (lunar). This is explicitly permitted by the contract ("per-body tolerance relaxed for documented physical reasons") and pinned with measured ephemeris-theory deltas in fixtures + 18-04-NOTES.md. The primary regression gate is the self-consistency oracle at tolerance_deg=0.0001, which is machine-precision-tight.

---

_Verified: 2026-05-28T16:53:40Z_
_Verifier: Claude (gsd-verifier)_
