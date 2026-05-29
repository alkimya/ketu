---
phase: 22-ephemeris-refactor
verified: 2026-05-29T17:51:33Z
status: passed
score: 3/3 must-haves verified
---

# Phase 22: Ephemeris Refactor Verification Report

**Phase Goal:** The ephemeris engine is restructured so a new body is a registered per-body strategy (not another if-elif branch) and orbital.py decomposes into focused units — behavior byte-stable — making Chiron a clean addition rather than aggravated debt.
**Verified:** 2026-05-29T17:51:33Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #  | Truth                                                                                                          | Status     | Evidence                                                                                  |
|----|----------------------------------------------------------------------------------------------------------------|------------|-------------------------------------------------------------------------------------------|
| 1  | Adding a new body requires registering one BODY_STRATEGIES entry, not adding an if-elif branch                 | VERIFIED   | `BODY_STRATEGIES` dict at planets.py:310 covers all 13 bodies; both scalar and batch dispatch through it; no if-elif on planet name remains |
| 2  | orbital.py decomposes from ~859 LOC into focused units each under 500 LOC; regression suite byte-identical     | VERIFIED   | orbital.py = 70 LOC (hub); _elements.py 209, _kepler.py 69, _mechanics.py 99, _perturbations.py 131, _body_getters.py 415; all under 500 LOC |
| 3  | Duplicated natal/chart fixtures consolidated into root tests/conftest.py; full suite stays green               | VERIFIED   | tests/conftest.py holds 12 fixtures; grep of subpackage conftests returns 0 `def chart_*`/`def natal_*`; 1351 passed, 2 skipped, 100% coverage |

**Score:** 3/3 truths verified

### Required Artifacts

| Artifact                              | Provides                                                           | Status      | Details                                                     |
|---------------------------------------|--------------------------------------------------------------------|-------------|-------------------------------------------------------------|
| `ketu/ephemeris/planets.py`           | BODY_STRATEGIES registry; `@lru_cache` on calc_planet_position     | VERIFIED    | BODY_STRATEGIES at line 310; `@lru_cache(maxsize=128)` at line 331; batch dispatch at line 633 |
| `tests/test_planets_coverage.py`      | TestBatchKetuFix, TestScalarBatchAgreementAllBodies, TestBodyStrategiesRegistry | VERIFIED | All 5 new test methods present and imported BODY_STRATEGIES |
| `ketu/ephemeris/_elements.py`         | ORBITAL_ELEMENTS + five _LILITH_* constants                        | VERIFIED    | 209 LOC; no ketu imports (zero circular-import risk)        |
| `ketu/ephemeris/_kepler.py`           | normalize_angle, solve_kepler_equation                             | VERIFIED    | 69 LOC; imports numpy only                                  |
| `ketu/ephemeris/_mechanics.py`        | orbital_elements_at_date, compute_position                         | VERIFIED    | 99 LOC; imports from _elements, _kepler                     |
| `ketu/ephemeris/_perturbations.py`    | apply_perturbations (Jupiter/Saturn/Uranus branches unchanged)     | VERIFIED    | 131 LOC; imports from _elements                             |
| `ketu/ephemeris/_body_getters.py`     | get_body_position, get_moon_position, get_lunar_nodes, get_lilith_position + vectorized twins | VERIFIED | 415 LOC; imports from _elements, _kepler, _mechanics, _perturbations — never from orbital.py |
| `ketu/ephemeris/orbital.py`           | Re-export hub; all prior public names importable                   | VERIFIED    | 70 LOC; re-exports via `from ._body_getters import` and siblings; `__all__` defined       |
| `tests/conftest.py`                   | 6 chart_* CHART_DTYPE fixtures + 6 natal_* dict-triple fixtures    | VERIFIED    | All 12 fixtures present; chart_a_paris sourced from tests/conftest.py:41 per fixture list |
| `tests/synastry/conftest.py`          | Only synastry-specific: oracle_fixture (chart_* removed)           | VERIFIED    | grep returns 0 `def chart_*`; oracle_fixture present        |
| `tests/composite/conftest.py`         | Only composite-specific: oracle_fixture (chart_* removed)          | VERIFIED    | grep returns 0 `def chart_*`; oracle_fixture present        |
| `tests/returns/conftest.py`           | Documented stub (natal_* moved to root)                            | VERIFIED    | 9 LOC stub with docstring explaining REF-03 migration        |

### Key Link Verification

| From                          | To                                          | Via                              | Status  | Details                                                         |
|-------------------------------|---------------------------------------------|----------------------------------|---------|-----------------------------------------------------------------|
| `calc_planet_position`        | `BODY_STRATEGIES[name].scalar`              | dict lookup inside @lru_cache    | WIRED   | planets.py:354 `BODY_STRATEGIES[planet_name].scalar(jd)`       |
| `calc_planet_position_batch`  | `BODY_STRATEGIES[name].vectorized`          | dict lookup replacing old if-elif| WIRED   | planets.py:633 `BODY_STRATEGIES[planet_name].vectorized(jd_array)` |
| `ketu/ephemeris/orbital.py`   | `ketu/ephemeris/_body_getters.py`           | `from ._body_getters import`     | WIRED   | orbital.py:38-45                                                |
| `ketu/ephemeris/_body_getters.py` | `ketu/ephemeris/_elements.py`           | `from ._elements import`         | WIRED   | _body_getters.py:18-25                                          |
| `tests/synastry/test_*.py`    | `tests/conftest.py chart_* fixtures`        | pytest conftest auto-discovery   | WIRED   | pytest --fixtures confirms chart_a_paris at tests/conftest.py:41 |
| `tests/returns/test_*.py`     | `tests/conftest.py natal_* fixtures`        | pytest conftest auto-discovery   | WIRED   | returns subpackage: 311 passed using shared fixtures            |

### Requirements Coverage

| Requirement | Status    | Notes                                                                 |
|-------------|-----------|-----------------------------------------------------------------------|
| REF-01      | SATISFIED | Per-body strategy registry replaces if-elif; scalar+batch unified     |
| REF-02      | SATISFIED | orbital.py 859→70 LOC hub; 5 focused sub-modules created             |
| REF-03      | SATISFIED | 12 fixtures consolidated to root tests/conftest.py; no pytest_plugins |

### Anti-Patterns Found

None blocking. The only `["Rahu", "NorthNode", "Lilith"]` occurrence in planets.py is inside a docstring comment (line 290) explaining the pre-existing bug that was fixed — not executable code.

### Human Verification Required

None. All phase goals are verifiable programmatically.

## Summary

Phase 22 goal is fully achieved:

- **REF-01 (Strategy pattern):** `BODY_STRATEGIES` dict at planets.py:310 covers all 13 bodies. Both `calc_planet_position` (scalar, @lru_cache preserved) and `calc_planet_position_batch` dispatch through the same table — a new body like Chiron requires one `BODY_STRATEGIES["Chiron"] = _BodyCalc(...)` entry, not editing two parallel if-elif chains. The pre-existing Ketu batch bug (body fell through to heliocentric branch, ~170° error) is fixed. `TestBodyStrategiesRegistry` structurally guards against half-added bodies.

- **REF-02 (Orbital split):** The 859-LOC monolith decomposes into five focused modules (orbital.py hub 70 LOC; _body_getters.py 415; _elements.py 209; _perturbations.py 131; _mechanics.py 99; _kepler.py 69). Dependency direction is strictly `_elements ← leaf modules ← orbital.py`; no sub-module imports from orbital.py. All historical `from ketu.ephemeris.orbital import X` names resolve byte-identically. test_vectorization.py (< 1e-10) and test_lilith_cross_check.py (< 0.005°) confirm zero float drift.

- **REF-03 (Conftest consolidation):** 12 session-scoped fixtures (6 `chart_*` CHART_DTYPE arrays + 6 `natal_*` dict triples) live once in tests/conftest.py. Subpackage conftests retain only their oracle-specific helpers. Standard pytest auto-discovery — no `pytest_plugins`. `chart_b_reykjavik` retains `polar_fallback="porphyry"` (Pitfall 3 ratchet).

Full suite: **1351 passed, 2 skipped, 100% coverage**.

---
_Verified: 2026-05-29T17:51:33Z_
_Verifier: Claude (gsd-verifier)_
