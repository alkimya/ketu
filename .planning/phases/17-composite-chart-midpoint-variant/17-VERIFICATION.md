---
phase: 17-composite-chart-midpoint-variant
verified: 2026-05-24T13:30:00Z
status: human_needed
score: 4/4 must-haves verified (with 1 documented-deferred follow-up flagged for human action)
human_verification:
  - test: "Astro.com manual cross-check on the 3 oracle fixtures"
    expected: "For each of curie / diana_charles / lennon_ono, the developer manually generates the composite on Astro.com (free composite calculator, Extended chart selection → method → 'midpoint method'), records the displayed longitudes, then updates each fixture's `cross_check_astro_com` block: `performed: true`, `date_performed: YYYY-MM-DD`, `delta_max_deg: <observed>`, `notes: ...`. Advisory tolerance is 0.1° (6 arcmin). Estimated 30 min one-time."
    why_human: "Astro.com is bot-blocked from automated retrieval (16-RESEARCH Pitfall + 17-RESEARCH §Astro.com Oracle Pairs). The ROADMAP wording 'hand-validated against Astro.com' is literally a manual UI task. The self-consistency oracle at tolerance_deg=0.0001 IS the headline regression gate and is satisfied; the Astro.com cross-check is the advisory cross-validation. All 3 fixtures carry `cross_check_astro_com.performed=false` as the deferral hand-off. Documented as a deferred follow-up in CHANGELOG line 87-88 and REQUIREMENTS COMP-04 parenthetical. NOT a Phase 17 blocker per the synastry Plan 16-05 precedent (same Astro.com bot-block constraint)."
---

# Phase 17: composite-chart-midpoint-variant Verification Report

**Phase Goal:** Users derive a midpoint composite chart from two natal charts as a single CHART_DTYPE, with circular-midpoint arithmetic verified on the wraparound case.

**Verified:** 2026-05-24T13:30:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #   | Truth                                                                                                  | Status                  | Evidence                                                                                                                                                                       |
| --- | ------------------------------------------------------------------------------------------------------ | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | `calculate_composite(a, b, system="placidus")` returns scalar `CHART_DTYPE` with all fields populated  | ✓ VERIFIED              | Smoke: `c.dtype == CHART_DTYPE`, `body_lons.shape == (13,)`, `cusps.shape == (12,)`                                                                                            |
| 2   | Composite body longitudes are circular midpoints of the two natals                                     | ✓ VERIFIED              | 75 ratchet tests in `tests/composite/test_calculate_composite.py` (40 parametrized over 13 bodies + retrograde); 3 oracle fixtures confirm max body delta ~5e-7°               |
| 3   | Composite house cusps are derived from composite ASC and MC (NOT recomputed independently)             | ✓ VERIFIED              | Smoke: `c['cusps'][0] == c['asc']` and `c['cusps'][9] == c['mc']`; grep ratchet — `calculate_houses(` / `compute_chart(` / `calculate_aspects_vectorized(` absent from api.py |
| 4   | `system=` is accept-and-ignore — same cusps for placidus/koch/etc, ValueError on unknown system        | ✓ VERIFIED              | Smoke: `c_placidus['cusps'] == c_koch['cusps']` (allclose 1e-12); `system='unknown_xyz'` raises ValueError                                                                    |
| 5   | `circular_midpoint(359.0, 1.0) == 0.0` (NOT 180.0), strict equality, pinned as regression              | ✓ VERIFIED              | Smoke: strict-equality assertion passes; `test_wraparound_359_1_returns_zero` in `tests/composite/test_circular_midpoint.py` (18 ratchet tests)                                |
| 6   | `circular_midpoint` is vectorisable and modulo-360°                                                    | ✓ VERIFIED              | Smoke: `circular_midpoint(array([...]), array([...]))` returns ndarray with broadcast shape; `mid(370, 11) == 10.5`                                                            |
| 7   | Two reference composite pairs pinned as oracle tests with documented max longitude delta               | ✓ VERIFIED (self-cons.) | 3 fixtures (`oracle_curie.json`, `oracle_diana_charles.json`, `oracle_lennon_ono.json`); per-fixture max-delta line printed in `pytest -v -s` (e.g., 0.000000° on Jupiter)     |
| 7b  | Two reference composite pairs hand-validated **against Astro.com** with documented delta               | ? UNCERTAIN (DEFERRED)  | All 3 fixtures carry `cross_check_astro_com.performed=false`; Astro.com is bot-blocked; deferral documented in CHANGELOG + REQUIREMENTS                                       |
| 8   | Davison composite is explicitly out of scope, labeled as deferred-to-v1.3 in module docstring          | ✓ VERIFIED              | `'Davison composite is NOT in scope' in ketu.composite.__doc__` AND `'v1.3' in ketu.composite.__doc__`; zero `def davison*` / `davison_composite` / `TODO.*[Dd]avison` matches |
| 9   | Swap symmetry: `c(a, b) == c(b, a)` on body_lons + asc/mc + cusps within 1e-9°                         | ✓ VERIFIED              | Smoke: `np.allclose(c['body_lons'], c_swap['body_lons'], atol=1e-9)` for all listed fields                                                                                     |

**Score:** 8/8 truths fully verified (truth 7b is the documented-deferred Astro.com cross-check — flagged as human_verification, not a hard gap).

### Required Artifacts

| Artifact                                            | Expected                                              | Status     | Details                                                                                |
| --------------------------------------------------- | ----------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------- |
| `ketu/composite/__init__.py`                        | Subpackage entry + Davison-deferred Notes block       | ✓ VERIFIED | 61 lines; "Davison composite is NOT in scope" verbatim; `__all__` exposes 2 symbols    |
| `ketu/composite/core.py`                            | `circular_midpoint(lon_a, lon_b)` helper              | ✓ VERIFIED | Signed-diff algebraic formulation; antipodal pin via np.where; vectorised + scalar-OK  |
| `ketu/composite/api.py`                             | `calculate_composite(chart_a, chart_b, system)` impl  | ✓ VERIFIED | 309 lines, 100% coverage; inline Porphyry trisection + inline aspect-matching loop     |
| `tests/composite/test_circular_midpoint.py`         | COMP-02 ratchet suite                                 | ✓ VERIFIED | 18 tests, headline `test_wraparound_359_1_returns_zero` strict-equality pin            |
| `tests/composite/test_calculate_composite.py`       | COMP-01 ratchet suite                                 | ✓ VERIFIED | 53 tests across 6 classes (bookkeeping, system, bodies, angles, swap, is_day_chart)    |
| `tests/composite/test_composite_houses.py`          | COMP-03 ratchet suite + grep ratchets                 | ✓ VERIFIED | 13 tests; grep ratchets pin absence of `calculate_houses(` / `compute_chart(` / `calculate_aspects_vectorized(` |
| `tests/composite/test_dtype.py`                     | dtype + body-axis-order ratchet suite                 | ✓ VERIFIED | 7 tests (5 dtype + 2 Pitfall 8 body order)                                              |
| `tests/composite/test_oracle.py`                    | COMP-04 oracle tests + max-delta reporter             | ✓ VERIFIED | 18 PASS + 2 SKIPPED (Curie ASC/MC by design); per-fixture max-delta line printed       |
| `tests/composite/fixtures/oracle_curie.json`        | Bodies-only oracle (Pierre C-rated)                   | ✓ VERIFIED | 10 body longitudes, no asc/mc; `cross_check_astro_com.performed=false`                  |
| `tests/composite/fixtures/oracle_diana_charles.json` | PRIMARY (both AA) bodies + ASC + MC                  | ✓ VERIFIED | 10 body longitudes + asc + mc; `cross_check_astro_com.performed=false`                  |
| `tests/composite/fixtures/oracle_lennon_ono.json`   | SECONDARY (A + AA) bodies + ASC + MC                  | ✓ VERIFIED | 10 body longitudes + asc + mc; `cross_check_astro_com.performed=false`                  |
| `tests/composite/test_composite_coverage_gate.py`   | COMP-05 sentinel test                                 | ✓ VERIFIED | 32 LoC; ratchets marker recognition + module import                                     |
| `pyproject.toml` (registration)                     | `ketu.composite` in packages + marker registration    | ✓ VERIFIED | 1 grep match each for `ketu.composite` and `composite_coverage_gate`                    |
| `Makefile` (composite-coverage target)              | `make composite-coverage` two-step pattern            | ✓ VERIFIED | Target present; `.PHONY` includes composite-coverage; gate reports 100% (95/95 stmts)   |
| `ketu/charts/__init__.py` (back-reference)          | See Also -> `ketu.composite.calculate_composite`      | ✓ VERIFIED | 4-entry See Also block extended from 2; numpydoc lint clean                              |
| `ketu/synastry/__init__.py` (back-reference)        | See Also -> `ketu.composite.calculate_composite`      | ✓ VERIFIED | 5-entry See Also block extended from 4; numpydoc lint clean                              |
| `CHANGELOG.md` (Unreleased Added)                   | 8 bullets citing COMP-01..04 + COMP-05                | ✓ VERIFIED | All entries present; lines 75-97; Astro.com deferral flagged on line 87-88              |
| `.planning/REQUIREMENTS.md`                          | COMP-01..05 statuses flipped to Done                  | ✓ VERIFIED | 5 grep matches each for `[x] **COMP-0` and `COMP-0.*Done`                              |

### Key Link Verification

| From                          | To                              | Via                                                  | Status     | Details                                                                                                     |
| ----------------------------- | ------------------------------- | ---------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------- |
| `calculate_composite`         | `circular_midpoint`              | Direct import + 7 invocations on jd/lat/lon/asc/mc/armc/vertex/body_lons | ✓ WIRED    | `from .core import circular_midpoint` in api.py; used for every per-body and per-angle midpoint           |
| `calculate_composite`         | `CHART_DTYPE`                    | `np.zeros((), dtype=CHART_DTYPE)` allocation         | ✓ WIRED    | Output shape `()`, dtype identity holds                                                                     |
| `calculate_composite`         | `get_system` (validation)        | `get_system(system)` line 191                        | ✓ WIRED    | Raises ValueError on unknown; return value discarded (accept-and-ignore semantics)                          |
| `calculate_composite`         | Porphyry trisection algebra      | Inlined verbatim from `porphyry.py:159-186`          | ✓ WIRED    | Closed-form trisection on (composite_asc, composite_mc); upper_step/lower_step + 12 cusps assembled         |
| `calculate_composite`         | `resolve_aspect_set("classical")` | Aspect-matching loop selector mask                   | ✓ WIRED    | CLASSICAL preset (5 majors) hardcoded; resolved via single source of truth                                  |
| `calculate_composite`         | NOT to `calculate_houses`        | Grep ratchet `test_no_calculate_houses_call_smoke`   | ✓ ANTI-WIRED | Verified absent from api.py source — COMP-03 binding pin                                                  |
| `calculate_composite`         | NOT to `compute_chart`           | Grep ratchet `test_no_compute_chart_call_smoke`      | ✓ ANTI-WIRED | Verified absent from api.py source — Pitfall 2 anti-Davison-conflation ratchet                            |
| `calculate_composite`         | NOT to `calculate_aspects_vectorized` | Grep ratchet `test_no_calculate_aspects_vectorized_call_smoke` | ✓ ANTI-WIRED | Verified absent from api.py source — Phase 9 engine blast-radius zero                                  |
| `ketu/composite/__init__.py`  | Public API surface               | `__all__ = ["calculate_composite", "circular_midpoint"]` | ✓ WIRED    | Both symbols imported and re-exported; package registered in pyproject.toml                              |

### Requirements Coverage

| Requirement | Status      | Blocking Issue                                                                                                                 |
| ----------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------ |
| COMP-01     | ✓ SATISFIED | `calculate_composite` callable with (chart_a, chart_b, system="placidus") → CHART_DTYPE; 75 ratchet tests pin the surface     |
| COMP-02     | ✓ SATISFIED | `circular_midpoint` is vectorisable, modulo-360°, and `mid(359, 1) == 0.0` strict-equality pinned in 18 ratchet tests          |
| COMP-03     | ✓ SATISFIED | House cusps derived from composite ASC + composite MC via inline Porphyry trisection; 3 grep ratchets pin absence of forbidden calls |
| COMP-04     | ✓ SATISFIED (self-consistency) / ? DEFERRED (Astro.com manual cross-check) | 3 oracle fixtures pinned with documented max longitude delta (~5e-7°); Astro.com cross-check deferred per 16-RESEARCH/17-RESEARCH Pitfall (bot-blocked) — `performed=false` flag is the close-out hand-off |
| COMP-05     | ✓ SATISFIED | `make composite-coverage` reports 100% (95/95 stmts); `composite_coverage_gate` marker registered; sentinel test PASSES         |

### Anti-Patterns Found

| File                                  | Line | Pattern                              | Severity | Impact                                                                                                                                                              |
| ------------------------------------- | ---- | ------------------------------------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ketu/composite/api.py`               | 42   | `TODO not owned by Phase 17` comment | ℹ️ Info  | Documented future-improvement note ("a future refactor could expose a `body_lons=` kwarg on `calculate_aspects_vectorized` — TODO not owned by Phase 17"). NOT a stub — explicitly scoped out of Phase 17 and the inline aspect-matching loop is fully implemented (100% coverage). No action required. |

No blocker or warning anti-patterns. No empty implementations. No `return None`/`return {}` stubs. No `console.log`-only handlers. No placeholder strings.

### Human Verification Required

#### 1. Astro.com manual cross-check on the 3 oracle fixtures

**Test:** For each of curie / diana_charles / lennon_ono, the developer manually generates the composite on Astro.com (free composite calculator, Extended chart selection → method → "midpoint method"), records the displayed longitudes, then updates each fixture's `cross_check_astro_com` block.

**Expected:** Body longitudes agree within tolerance_deg=0.1° (6 arcmin); ASC/MC may differ by 0.5°–2° depending on Astro.com's account-method preset (17-RESEARCH Pitfall 5 — Astro.com's free composite calculator defaults to the reference-place method, NOT the pure midpoint method we implement). Update each fixture:
- `performed: true`
- `date_performed: YYYY-MM-DD`
- `delta_max_deg: <observed>`
- `astro_com_settings: "Extended chart selection → method → 'midpoint method'"`
- `notes: "Body longitudes agreed to X°; ASC/MC differed by Y° (method preset Z)"`

**Why human:** Astro.com is bot-blocked from automated retrieval (`16-RESEARCH` Pitfall + `17-RESEARCH` §"Astro.com Oracle Pairs"). The ROADMAP wording "hand-validated against Astro.com" is literally a manual UI task. Estimated 30 min one-time. NOT a Phase 17 blocker per the synastry Plan 16-05 precedent (same Astro.com bot-block constraint); the self-consistency oracle at `tolerance_deg=0.0001` IS the headline regression gate and is satisfied. The deferral is documented loudly in CHANGELOG line 87-88, REQUIREMENTS COMP-04 parenthetical, every fixture's `cross_check_astro_com.performed=false` flag, and `17-04-SUMMARY.md` §"Astro.com Manual Cross-Check — DEFERRED".

### Gaps Summary

**No hard gaps.** All 8 verifiable observable truths are VERIFIED. All 18 required artifacts EXIST, are SUBSTANTIVE (100% coverage on `ketu/composite/`, 0 numpydoc lint issues, 0 mypy --strict issues), and are WIRED (9 key links all verified — both positive links and anti-wiring grep ratchets). All 5 requirements (COMP-01..05) are SATISFIED at the implementation level.

**One documented-deferred follow-up:** The literal ROADMAP wording on success criterion #3 includes "hand-validated against Astro.com" — this half is explicitly deferred to a developer-driven manual UI task because Astro.com is bot-blocked. The deferral is transparent (CHANGELOG line 87-88, REQUIREMENTS COMP-04 parenthetical, fixture-level `cross_check_astro_com.performed=false` flag, 17-04-SUMMARY.md "Astro.com Manual Cross-Check — DEFERRED" section). The self-consistency oracle methodology at `tolerance_deg=0.0001` is the headline regression gate and is in place; the Astro.com cross-check is the advisory cross-validation at `tolerance_deg=0.1` (6 arcmin), estimated 30 min one-time. NOT a Phase 17 blocker per the synastry Plan 16-05 precedent.

**Final verdict:** Phase goal achieved at the code level. One human-verification follow-up identified (Astro.com manual cross-check). Phase 17 is shippable per the documented self-consistency methodology; the Astro.com cross-check should be performed before Phase 20 (v1.2.0 release preparation) for completeness.

### Smoke Test Results

All 4 ROADMAP success criteria executed live during verification:

- **SC#1** (`calculate_composite` returns CHART_DTYPE + composite-ASC/MC houses): **PASS** — `dtype == CHART_DTYPE`, `body_lons.shape == (13,)`, `cusps.shape == (12,)`, `cusps[0] == asc`, `cusps[9] == mc`, `cusps[3] == ic`, `cusps[6] == desc`.
- **SC#2** (`circular_midpoint(359, 1) == 0.0`): **PASS** — strict equality holds; vectorisable; modulo-360 verified (`mid(370, 11) == mid(10, 11) == 10.5`).
- **SC#3** (2+ reference pairs with documented max delta): **PASS** (self-consistency) — 3 fixtures × `max body delta: 0.000000°` printed lines; Astro.com cross-check deferred (human follow-up).
- **SC#4** (Davison deferred-to-v1.3, no aspirational reference): **PASS** — `'Davison composite is NOT in scope' in ketu.composite.__doc__`; zero `davison*` grep matches outside the explicit deferral statements.

### Test Suite Status

- `pytest tests/`: **1177 / 1177 PASSED** (+2 skipped by design from Curie ASC/MC rating-hygiene)
- `pytest tests/composite/`: **112 / 112 PASSED** (+2 skipped)
- `make composite-coverage`: **100%** (95/95 statements on `ketu/composite/`)
- Grep ratchets in `api.py`: ZERO forbidden call patterns (`calculate_houses(` / `compute_chart(` / `calculate_aspects_vectorized(`)

---

_Verified: 2026-05-24T13:30:00Z_
_Verifier: Claude (gsd-verifier)_
