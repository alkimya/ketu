# Phase 22: Ephemeris Refactor — Research

**Researched:** 2026-05-29
**Domain:** Python refactoring — strategy pattern, module decomposition, pytest fixture consolidation
**Confidence:** HIGH (all findings from direct source reading)

---

## Summary

Phase 22 is a pure structural refactor across three independent concerns: (1) extract a per-body
dispatch strategy in `planets.py` to replace growing if-elif branches, (2) decompose the 859-LOC
`orbital.py` into focused sub-modules while preserving its public import surface, and (3) consolidate
four near-identical `conftest.py` natal fixture sets into a single `tests/conftest.py`. No behavior
change is permitted — the full 1346-test suite must remain byte-stable.

The source code has been read in full. All findings are HIGH confidence (direct file inspection).

**Primary recommendation:** Three independent plans, waved as REF-03 first (pure test infra, zero
production risk), then REF-01 + REF-02 in parallel (they touch disjoint files). REF-01 must handle
both `calc_planet_position` (scalar) and `calc_planet_position_batch` (vectorized) — they currently
duplicate the same if-elif and **one pre-existing bug exists in the batch path** (see Finding 1B
below).

---

## Finding 1: Per-Body Strategy in `planets.py` (REF-01)

### 1A — The scalar if-elif (`calc_planet_position`, lines 93–189)

`calc_planet_position(jd, planet_id, flags)` at `planets.py:70` dispatches via `planet_name`
obtained from `SWE_IDS.get(planet_id)`. Five distinct body "kinds":

| Branch | Condition | Body | Lines |
|--------|-----------|------|-------|
| SUN | `planet_name == "Sun"` | geocentric via Earth negation | 93–109 |
| MOON | `planet_name == "Moon"` | `get_moon_position` + wrapping lon_diff | 110–125 |
| RAHU | `planet_name == "Rahu"` | `get_lunar_nodes()[0]`, speed = -0.0529538083 | 127–136 |
| KETU | `planet_name == "Ketu"` | `get_lunar_nodes()[0] + 180`, same speed | 138–148 |
| LILITH | `planet_name == "Lilith"` | `get_lilith_position`, speed = `_LILITH_MEAN_RATE_DEG_PER_DAY` | 150–160 |
| ELSE | regular planets | heliocentric + geocentric conversion, speed by finite diff | 162–189 |

After the dispatch, line 192 applies `aberration_correction` for `planet_id >= 2` (not Sun or Moon).
This post-dispatch step must remain in the router, not inside each strategy.

### 1B — **PRE-EXISTING BUG in `calc_planet_position_batch` (lines 530)**

`calc_planet_position_batch` at `planets.py:453` mirrors the same logic but has **three branches**
only:

```python
if planet_name == "Sun": ...
elif planet_name == "Moon": ...
elif planet_name in ["Rahu", "NorthNode", "Lilith"]:  # line 530
    for i, jd in enumerate(jd_array):
        results[i] = calc_planet_position(jd, planet_id, flags)
else:
    # Regular planets (vectorized)
```

**`"Ketu"` is absent from the fallback list.** When `planet_id=11` (Ketu), the batch path falls
through to `else` and executes `body_idx = BODY_INDICES["Ketu"]` → tries to get a heliocentric
orbital position for it (wrong). The scalar `calc_planet_position` for Ketu is correct, but
the batch twin silently computes the wrong value for Ketu in vectorized time-series paths.

The strategy refactor **must fix this bug** by making the batch path share the same strategy
table as the scalar path, eliminating the divergence entirely.

### 1C — Recommended strategy structure

A `dict[str, Callable]` registry keyed by `planet_name`:

```python
# Per-body strategy: name → (scalar_fn, vectorized_fn)
# or a dataclass / namedtuple
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class BodyStrategy:
    scalar: Callable       # (jd: float) -> tuple[float, float, float, float, float, float]
    vectorized: Callable   # (jd_array: np.ndarray) -> tuple[arrays...]

BODY_STRATEGIES: dict[str, BodyStrategy] = {
    "Sun":    BodyStrategy(scalar=_calc_sun,    vectorized=_calc_sun_vec),
    "Moon":   BodyStrategy(scalar=_calc_moon,   vectorized=_calc_moon_vec),
    "Rahu":   BodyStrategy(scalar=_calc_rahu,   vectorized=_calc_rahu_vec),
    "Ketu":   BodyStrategy(scalar=_calc_ketu,   vectorized=_calc_ketu_vec),
    "Lilith": BodyStrategy(scalar=_calc_lilith, vectorized=_calc_lilith_vec),
    # Regular planets all share the same strategy wired with their body_idx:
    "Mercury": BodyStrategy(scalar=_make_planet_scalar(2), vectorized=_make_planet_vec(2)),
    ...
}
```

This is the pattern Phase 24 will use to add Chiron: `BODY_STRATEGIES["Chiron"] = BodyStrategy(...)`.

**Alternative (simpler):** Two separate dicts `SCALAR_STRATEGIES` and `VECTOR_STRATEGIES`, both
`dict[str, Callable]`. Lighter — no dataclass dependency, easy to understand.

**Recommendation:** Use two plain dicts (simpler, no new types). Regular planets can share a factory:
`_make_planet_body(body_idx)` returns a closure for both scalar and vectorized paths.

### 1D — Aberration post-processing

Line 192–195 applies `aberration_correction` for `planet_id >= 2`. After strategy dispatch, this
remains in `calc_planet_position` itself (not inside strategies). The strategy returns raw
`(lon, lat, dist, lon_speed, lat_speed, dist_speed)` before aberration. No change needed here.

### 1E — `get_planet_name` and `calculate_all_positions` insertion points for Phase 24

The roadmap notes six insertion points for Chiron in Phase 24:
1. `core.py` bodies array
2. `orbital.py` ORBITAL_ELEMENTS
3. `planets.py` BODY_INDICES
4. `planets.py` SWE_IDS
5. `planets.py` strategy table (this is what REF-01 creates)
6. `planets.py` `get_planet_name` dict (line 214)
7. `planets.py` `calculate_all_positions` iterates `range(13)` → must become `range(len(SWE_IDS))`

The range fix is needed in REF-01 as well to make Phase 24 trivial.

---

## Finding 2: Splitting `orbital.py` (REF-02)

### 2A — Natural seams

`orbital.py` (859 LOC) has these logical groups:

| Group | Lines | Functions | Natural module name |
|-------|-------|-----------|---------------------|
| Lilith constants | 1–54 | 5 private constants | stays in `orbital.py` or `_lilith.py` |
| ORBITAL_ELEMENTS | 67–208 | structured array data | stays in `orbital.py` or `_elements.py` |
| Angle utilities | 211–229 | `normalize_angle` | `_utils.py` or stays |
| Kepler solver | 231–269 | `solve_kepler_equation` | `_kepler.py` |
| Orbital mechanics | 272–356 | `orbital_elements_at_date`, `compute_position` | `_mechanics.py` |
| Perturbations | 359–472 | `apply_perturbations` (Jupiter/Saturn/Uranus if-elif) | `_perturbations.py` |
| Scalar getters | 475–691 | `get_body_position`, `get_moon_position`, `get_lunar_nodes`, `get_lilith_position` | `_body_getters.py` |
| Vectorized getters | 694–859 | `get_body_position_vectorized`, `get_moon_position_vectorized` | `_body_getters.py` (same file) or `_vectorized.py` |

### 2B — Import surface constraints

The following modules import directly from `ketu.ephemeris.orbital` (must not break):

**Production code:**
- `ketu/ephemeris/planets.py:13-22` imports: `ORBITAL_ELEMENTS`, `_LILITH_MEAN_RATE_DEG_PER_DAY`, `get_body_position`, `get_moon_position`, `get_lunar_nodes`, `get_lilith_position`, `get_body_position_vectorized`, `get_moon_position_vectorized`
- `ketu/ephemeris/__init__.py:18-29` imports: `ORBITAL_ELEMENTS`, `normalize_angle`, `solve_kepler_equation`, `orbital_elements_at_date`, `compute_position`, `apply_perturbations`, `get_body_position`, `get_moon_position`, `get_lunar_nodes`, `get_lilith_position`

**Test code:**
- `tests/test_vectorization.py:9-14` imports from `ketu.ephemeris.orbital`: `get_body_position`, `get_body_position_vectorized`, `get_moon_position`, `get_moon_position_vectorized`
- `tests/test_coverage_improvements.py:1086` imports: `ORBITAL_ELEMENTS`, `get_body_position_vectorized`
- `tests/test_coverage_improvements.py:1107` imports: `compute_position`
- `tests/test_lilith_cross_check.py:69` imports: `get_lilith_position`

### 2C — Re-export strategy (BINDING)

`orbital.py` must remain as the **re-export hub** for all public names. Move implementation to
focused private modules under `ketu/ephemeris/` (e.g. `_kepler.py`, `_mechanics.py`,
`_perturbations.py`, `_body_getters.py`), then re-export from `orbital.py`:

```python
# orbital.py after refactor — top portion (data + constants stay here)
# ... ORBITAL_ELEMENTS definition ...
# ... Lilith constants ...

# Re-export from focused sub-modules
from ._kepler import solve_kepler_equation, normalize_angle
from ._mechanics import orbital_elements_at_date, compute_position
from ._perturbations import apply_perturbations
from ._body_getters import (
    get_body_position, get_moon_position, get_lunar_nodes,
    get_lilith_position, get_body_position_vectorized,
    get_moon_position_vectorized,
)

__all__ = [...]
```

**This preserves all existing imports byte-identically.**

### 2D — `apply_perturbations` also has a per-body if-elif

`apply_perturbations` (line 359) has an if-elif for Jupiter/Saturn/Uranus. REF-01's strategy
pattern approach could also be applied here in a future phase (Phase 24 would add Chiron
perturbations). For Phase 22, it's acceptable to simply move the function to `_perturbations.py`
unchanged — the roadmap says "focused units", not necessarily "strategy-ified perturbations".
The Chiron perturbations are likely to be Chebyshev-based anyway (Phase 23 spike).

### 2E — Proposed split

```
ketu/ephemeris/
├── orbital.py          # Hub: ORBITAL_ELEMENTS, Lilith constants, re-exports all
├── _kepler.py          # normalize_angle, solve_kepler_equation (~60 LOC)
├── _mechanics.py       # orbital_elements_at_date, compute_position (~90 LOC)
├── _perturbations.py   # apply_perturbations (~115 LOC)
└── _body_getters.py    # get_body_position, get_moon_position, get_lunar_nodes,
                        # get_lilith_position, _vectorized twins (~390 LOC)
```

After the split, `orbital.py` would be ~250 LOC (data + re-exports), down from 859 LOC.
Each focused module is 60–390 LOC — all well under 500.

---

## Finding 3: Conftest Consolidation (REF-03)

### 3A — Four conftest.py files and their fixtures

| File | LOC | Fixtures | Nature |
|------|-----|----------|--------|
| `tests/charts/conftest.py` | 41 | `SYSTEM_BYTES`, `swe_oracle`, `reference_charts`, `loaded_reference_snapshot` (re-exported from `tests/houses/conftest.py`) | NO natal chart fixtures; just re-exports |
| `tests/synastry/conftest.py` | 133 | `chart_a_paris`, `chart_b_reykjavik`, `chart_b_nyc`, `chart_b_tokyo`, `chart_b_sydney`, `chart_a_retrograde_mercury`, `oracle_fixture` (+ `ORACLE_SLUGS`, `load_oracle_fixture`) | Full CHART_DTYPE fixtures |
| `tests/composite/conftest.py` | 134 | **Identical** `chart_a_paris`, `chart_b_reykjavik`, `chart_b_nyc`, `chart_b_tokyo`, `chart_b_sydney`, `chart_a_retrograde_mercury` + `oracle_fixture` (+ composite-specific `ORACLE_SLUGS`, `load_oracle_fixture`) | Byte-for-byte copy of synastry's chart fixtures |
| `tests/returns/conftest.py` | 115 | `natal_diana`, `natal_charles`, `natal_marie_curie`, `natal_pierre_curie`, `natal_lennon`, `natal_ono` | `dict[str, float]` triples only, NOT CHART_DTYPE |

### 3B — Exactly duplicated fixtures

Between `tests/synastry/conftest.py` and `tests/composite/conftest.py`, the following six fixtures
are **byte-for-byte identical** (same JDs, lat, lon, same `scope="session"`, same docstrings):

- `chart_a_paris()`  → `compute_chart(2451545.0, 48.86, 2.35)`
- `chart_b_reykjavik()` → `compute_chart(2470204.0, 64.15, -21.94, polar_fallback="porphyry")`
- `chart_b_nyc()` → `compute_chart(2451900.0, 40.71, -74.01)`
- `chart_b_tokyo()` → `compute_chart(2451545.0, 35.69, 139.69)`
- `chart_b_sydney()` → `compute_chart(2451545.0, -33.87, 151.21)`
- `chart_a_retrograde_mercury()` → `compute_chart(2460530.0, 48.86, 2.35)`

The `returns/conftest.py` also duplicates the six persona **JD/lat/lon** values (as raw `dict`
triples) that appear in `tests/returns/fixtures/_generate.py:44` comment and in the synastry/composite
JSON oracle fixtures.

### 3C — What to move to `tests/conftest.py`

**Create `tests/conftest.py`** containing:
1. The six `chart_*` CHART_DTYPE fixtures (`scope="session"`)
2. The six `natal_*` dict-triple fixtures (`scope="session"`)

Pytest fixture resolution: fixtures in `tests/conftest.py` are automatically available to ALL
subpackages under `tests/` without any import or `pytest_plugins` declaration.

**Keep subpackage-specific in their own conftests:**
- `tests/synastry/conftest.py` → keep `oracle_fixture`, `ORACLE_SLUGS`, `load_oracle_fixture`
  (synastry-specific)
- `tests/composite/conftest.py` → keep `oracle_fixture`, `ORACLE_SLUGS`, `load_oracle_fixture`
  (composite-specific, different JSON fixture files)
- `tests/charts/conftest.py` → keep as-is (re-exports from houses conftest; not part of REF-03
  scope)
- `tests/returns/conftest.py` → after moving natal_* to root conftest, this file becomes empty
  and can be removed (or kept as a stub with a module docstring)

### 3D — No fixture name conflicts

All six `chart_*` names appear only in `synastry/conftest.py` and `composite/conftest.py`.
All six `natal_*` names appear only in `returns/conftest.py`. No name collisions with
`tests/cli/conftest.py` (`invoke_main` only) or `tests/houses/conftest.py` (`SYSTEM_BYTES`,
`swe_oracle`, `swe_oracle_armc`, `reference_charts`, `loaded_reference_snapshot`).

### 3E — One behavioral difference to watch

`tests/composite/conftest.py` docstring explicitly says it duplicates synastry's conftest "per
17-RESEARCH §'Test Layout'" and notes "duplication preferred to cross-package pytest_plugins import".
Moving shared fixtures to `tests/conftest.py` is precisely what the roadmap calls for in REF-03;
this is the standard pytest approach and does NOT require `pytest_plugins` hacks.

---

## Finding 4: Byte-Stability Verification

### 4A — What counts as the "ephemeris regression suite"

There is **no dedicated golden-master / snapshot file** for planetary positions. Byte-stability is
verified by the existing test suite passing unchanged after the refactor. The relevant test files
pinning ephemeris behavior are:

| File | What it pins |
|------|-------------|
| `tests/test_ketu.py` (`TestPrecision`) | Sun ~270° (Dec 2020), Jupiter/Saturn ~300° (Dec 2020), Jupiter-Saturn separation <2°, Sun/Jupiter/Saturn tolerance 2–5° |
| `tests/test_refactored.py` | Sun position 260–280° (Dec 2020) |
| `tests/test_vectorization.py` | scalar vs vectorized agreement < 1e-10 (get_body_position), < 1e-10 (get_moon_position), < 1e-8 (calc_planet_position_batch vs scalar for Mars) |
| `tests/test_lilith_cross_check.py` | Lilith vs swisseph `MEAN_APOG` < 0.005° on 5 cross-check dates (1900–2050) |
| `tests/test_ketu.py` (`TestData`) | core.aspects sha256 fingerprint (`EXPECTED_ASPECT_FINGERPRINT_V1`) |

`tests/test_vectorization.py:47` is the strongest numerical regression: it asserts
`max_diff < 1e-10` between scalar and vectorized paths for `get_body_position`. After REF-02, this
test must still pass — confirming no float drift from the module decomposition.

### 4B — Strategy for proving byte-stability during REF-01

Before extracting strategies, capture reference outputs for all 13 body IDs at several JDs and
assert them in the refactored code. Alternatively, rely on `test_vectorization.py`'s 1e-8 / 1e-10
assertions and the precision tests in `test_ketu.py` as the regression harness. Adding a
before/after snapshot comparison test within REF-01's own plan provides extra insurance.

### 4C — `@lru_cache` on `calc_planet_position`

`calc_planet_position` is decorated with `@lru_cache(maxsize=128)` (line 69). The strategy
refactor must preserve this cache. The strategies themselves should be pure functions called from
within the cached wrapper — not decorated themselves.

---

## Finding 5: Coverage at 100% — Risks During Refactor

### 5A — Moved code that loses coverage

When functions move from `orbital.py` to `_kepler.py` / `_mechanics.py` etc., coverage.py tracks
by module. As long as the moved functions are imported back via `orbital.py` re-exports (and
`pyproject.toml` covers `source = ["ketu"]`), coverage is attributed to the original call paths.
No coverage risk if re-exports are in place before tests run.

### 5B — New `_private.py` modules

Private modules (`_kepler.py`, `_mechanics.py`, etc.) must be listed in `ketu/ephemeris/__init__.py`
or imported transitively so coverage.py tracks them. The re-export pattern in `orbital.py` ensures
this: `orbital.py` imports from `_kepler.py` → `_kepler.py` is always loaded → all lines covered.

### 5C — The `apply_perturbations` if-elif in `_perturbations.py`

`apply_perturbations` has three named branches (Jupiter, Saturn, Uranus) and an implicit
pass-through else. All four branches are currently covered by `tests/test_coverage_improvements.py`.
Moving the function to `_perturbations.py` changes nothing — the tests import via `ketu.ephemeris.orbital`
which re-exports, coverage tracks the real file.

### 5D — Strategy table dead entries

After the strategy refactor, if any strategy entry is never called in tests (e.g. a rarely-exercised
planet), that strategy function's body would be uncovered. Verify all 13 body IDs are exercised
by the existing suite. `test_planets_coverage.py:TestCalculateSpeedRatio.test_all_bodies_speed_ratio`
and `TestCalculateAllPositionsError.test_all_positions_returns_dict_with_arrays` exercise all 13
bodies — coverage should remain complete.

### 5E — Fixing the batch Ketu bug = coverage change

Fixing the `calc_planet_position_batch` bug (Ketu missing from fallback list) will change the
execution path for `planet_id=11` in batch mode. The new Ketu vectorized strategy function needs
its own test coverage. This is an incidental but necessary fix.

---

## Finding 6: Plan Ordering and Parallelism

### Dependency analysis

- **REF-03** (conftest consolidation) touches only `tests/` directory — zero production code.
  Fully independent of REF-01 and REF-02.
- **REF-01** (`planets.py` strategy) touches `ketu/ephemeris/planets.py` only. Independent of REF-02.
- **REF-02** (`orbital.py` split) touches `ketu/ephemeris/orbital.py` and creates new private
  modules. Independent of REF-01.

### Wave structure

```
Wave 1 (parallel): REF-01-PLAN + REF-02-PLAN + REF-03-PLAN
```

All three plans can execute in parallel. There are no shared files between them:
- REF-01 → `planets.py`
- REF-02 → `orbital.py`, new `_kepler.py`, `_mechanics.py`, `_perturbations.py`, `_body_getters.py`
- REF-03 → `tests/conftest.py` (new), `tests/synastry/conftest.py`, `tests/composite/conftest.py`, `tests/returns/conftest.py`

**Recommended:** Three-plan single wave. Each plan verifies `pytest tests/ -v` passes before
declaring done.

---

## Architecture Patterns

### Recommended Project Structure After Phase 22

```
ketu/ephemeris/
├── __init__.py          # unchanged public surface
├── planets.py           # strategy registry + cached wrappers (≤200 LOC)
├── orbital.py           # ORBITAL_ELEMENTS + Lilith constants + re-exports (≤250 LOC)
├── _kepler.py           # normalize_angle, solve_kepler_equation (≤70 LOC)
├── _mechanics.py        # orbital_elements_at_date, compute_position (≤100 LOC)
├── _perturbations.py    # apply_perturbations (≤120 LOC)
├── _body_getters.py     # get_body_position, get_moon_position, get_lunar_nodes,
│                        # get_lilith_position, vectorized twins (≤400 LOC)
├── coordinates.py       # unchanged
└── time.py              # unchanged

tests/
├── conftest.py          # NEW: 6 chart_* + 6 natal_* session-scoped fixtures
├── synastry/conftest.py # keeps oracle_fixture, ORACLE_SLUGS, load_oracle_fixture
├── composite/conftest.py# keeps oracle_fixture, ORACLE_SLUGS, load_oracle_fixture
├── returns/conftest.py  # stub (natal_* moved to root) or deleted
└── charts/conftest.py   # unchanged (re-exports from houses conftest)
```

### Anti-Patterns to Avoid

- **Don't use `pytest_plugins`** for fixture sharing — standard conftest.py discovery is sufficient
  and simpler.
- **Don't remove `orbital.py`** — it must remain as the re-export hub; all existing import paths
  must continue to work without any change in non-ephemeris code.
- **Don't break `@lru_cache`** — keep the cache on the outer `calc_planet_position` wrapper, not
  on strategy callables.
- **Don't create circular imports** — private `_*.py` modules must not import from `orbital.py`
  (they are imported by `orbital.py`, not the reverse).
- **Don't forget `calc_planet_position_batch`** — REF-01 must apply the strategy table to both
  the scalar and vectorized paths simultaneously, fixing the Ketu batch bug in the process.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Strategy dispatch | Complex metaclass or ABC | Plain `dict[str, Callable]` | No inheritance needed; dict lookup is O(1) and trivially extensible |
| Module re-exports | Custom import machinery | Standard `from ._module import ...` | Python's import system handles this natively |
| Fixture sharing | `pytest_plugins` declarations | Root `tests/conftest.py` | Pytest auto-discovers conftest.py at every directory level |

---

## Common Pitfalls

### Pitfall 1: `orbital.py` circular import
**What goes wrong:** `_body_getters.py` imports `solve_kepler_equation` from `_kepler.py`, which
is fine. But if `_body_getters.py` also imports `ORBITAL_ELEMENTS` from `orbital.py` (the hub),
and `orbital.py` imports from `_body_getters.py`, circular import.
**How to avoid:** `ORBITAL_ELEMENTS` and the Lilith constants STAY in `orbital.py`. Sub-modules
receive them as parameters or import them from each other (not from orbital.py). E.g.,
`_mechanics.py` imports `ORBITAL_ELEMENTS` from `orbital.py` only if `orbital.py` imports from
`_mechanics.py` AFTER defining `ORBITAL_ELEMENTS`. Python resolves this fine because `ORBITAL_ELEMENTS`
is defined at module level before the `from ._mechanics import` line — but test carefully.
**Safest approach:** Put `ORBITAL_ELEMENTS` in its own `_elements.py` module; everything imports
from `_elements.py`, and `orbital.py` re-exports from `_elements.py`.

### Pitfall 2: `@lru_cache` and strategy closures
**What goes wrong:** If `_make_planet_scalar(body_idx)` returns a closure, the closure captures
`body_idx` by reference. With a loop, all closures may capture the last value.
**How to avoid:** Use a default argument: `lambda body_idx=body_idx: ...` or a proper factory
function with an explicit parameter.

### Pitfall 3: `get_planet_name` dict vs SWE_IDS
`get_planet_name` (line 200) has its own hardcoded dict (lines 214–228) duplicating `SWE_IDS`.
This should be simplified to `return SWE_IDS.get(planet_id, f"Unknown({planet_id})")` in REF-01.

### Pitfall 4: `calculate_all_positions` hardcoded `range(13)`
Line 248: `for planet_id in range(13)`. After REF-01, this must be `range(len(SWE_IDS))` so
Phase 24 (Chiron as 14th body) works automatically.

### Pitfall 5: pytest fixture scope and session-scoped reuse
When `chart_a_paris` moves to `tests/conftest.py`, it is session-scoped and computed once per
test session. Both `synastry/` and `composite/` tests will share the SAME fixture instance.
This is correct and intended — it's already the case within each subpackage.
**Risk:** If any test mutates the returned numpy array, shared fixture causes interference.
Check: all six chart fixtures return structured arrays from `compute_chart`; tests call
`calculate_synastry(chart_a_paris, ...)` or `calculate_composite(...)` without mutating the input.
This is safe.

---

## Code Examples

### Strategy table for `planets.py` (recommended pattern)

```python
# Verified from reading planets.py + orbital.py source
from typing import Callable, NamedTuple

class _BodyCalc(NamedTuple):
    scalar: Callable      # (jd: float) -> tuple[6 floats]
    vectorized: Callable  # (jd_array: np.ndarray) -> tuple[6 arrays]

def _make_planet(body_idx: int) -> _BodyCalc:
    """Factory for regular heliocentric planets."""
    def _scalar(jd: float):
        x_e, y_e, z_e, *_ = get_body_position(BODY_INDICES["Sun"], jd)
        x_p, y_p, z_p, *_ = get_body_position(body_idx, jd)
        x_g, y_g, z_g = heliocentric_to_geocentric(x_p, y_p, z_p, x_e, y_e, z_e)
        lon, lat, dist = rectangular_to_spherical(x_g, y_g, z_g)
        jd2 = jd + 0.01
        x_e2, y_e2, z_e2, *_ = get_body_position(BODY_INDICES["Sun"], jd2)
        x_p2, y_p2, z_p2, *_ = get_body_position(body_idx, jd2)
        x_g2, y_g2, z_g2 = heliocentric_to_geocentric(x_p2, y_p2, z_p2, x_e2, y_e2, z_e2)
        lon2, lat2, dist2 = rectangular_to_spherical(x_g2, y_g2, z_g2)
        return lon, lat, dist, (lon2 - lon) / 0.01, (lat2 - lat) / 0.01, (dist2 - dist) / 0.01
    # ... vectorized twin similarly
    return _BodyCalc(scalar=_scalar, vectorized=_vec)

BODY_STRATEGIES: dict[str, _BodyCalc] = {
    "Sun":     _BodyCalc(scalar=_calc_sun_scalar,    vectorized=_calc_sun_vec),
    "Moon":    _BodyCalc(scalar=_calc_moon_scalar,   vectorized=_calc_moon_vec),
    "Rahu":    _BodyCalc(scalar=_calc_rahu_scalar,   vectorized=_calc_nodes_vec(0)),
    "Ketu":    _BodyCalc(scalar=_calc_ketu_scalar,   vectorized=_calc_nodes_vec(1)),  # BUG FIX
    "Lilith":  _BodyCalc(scalar=_calc_lilith_scalar, vectorized=_calc_lilith_vec),
    "Mercury": _make_planet(BODY_INDICES["Mercury"]),
    "Venus":   _make_planet(BODY_INDICES["Venus"]),
    "Mars":    _make_planet(BODY_INDICES["Mars"]),
    "Jupiter": _make_planet(BODY_INDICES["Jupiter"]),
    "Saturn":  _make_planet(BODY_INDICES["Saturn"]),
    "Uranus":  _make_planet(BODY_INDICES["Uranus"]),
    "Neptune": _make_planet(BODY_INDICES["Neptune"]),
    "Pluto":   _make_planet(BODY_INDICES["Pluto"]),
}
```

### Re-export pattern for `orbital.py`

```python
# orbital.py (hub after split)
# ... ORBITAL_ELEMENTS definition (stays here) ...
# ... Lilith constants (stay here) ...

from ._kepler import normalize_angle, solve_kepler_equation          # noqa: F401
from ._mechanics import orbital_elements_at_date, compute_position   # noqa: F401
from ._perturbations import apply_perturbations                      # noqa: F401
from ._body_getters import (                                          # noqa: F401
    get_body_position, get_moon_position, get_lunar_nodes,
    get_lilith_position, get_body_position_vectorized,
    get_moon_position_vectorized,
)
```

### Root conftest pattern

```python
# tests/conftest.py (new file)
"""Shared session-scoped fixtures available to all test subpackages."""
from __future__ import annotations
import numpy as np
import pytest
from ketu.charts import compute_chart

@pytest.fixture(scope="session")
def chart_a_paris() -> np.ndarray:
    """J2000 noon UTC chart for Paris (lat 48.86, lon 2.35)."""
    return compute_chart(2451545.0, 48.86, 2.35)

# ... other 5 chart_* fixtures (identical body to synastry/composite conftest) ...

@pytest.fixture(scope="session")
def natal_diana() -> dict[str, float]:
    """Princess Diana — JD 2437482.28125, lat 52.83, lon 0.50."""
    return {"jd": 2437482.28125, "lat": 52.83, "lon": 0.50}

# ... other 5 natal_* fixtures (identical to returns conftest) ...
```

---

## Open Questions

1. **Circular import with ORBITAL_ELEMENTS**
   - What we know: `orbital.py` defines `ORBITAL_ELEMENTS`, `_body_getters.py` will need it.
   - What's unclear: whether Python's module load order will handle a circular dependency
     (`orbital.py` → `_body_getters.py` → `orbital.py`) or if `ORBITAL_ELEMENTS` should be
     extracted to `_elements.py`.
   - Recommendation: Extract `ORBITAL_ELEMENTS` + Lilith constants to `_elements.py`; `orbital.py`
     re-exports from `_elements.py` too. Zero circular risk.

2. **`apply_perturbations` body-name coupling**
   - `apply_perturbations` uses `ORBITAL_ELEMENTS[body_id]["name"]` to dispatch. After the split,
     it will need `ORBITAL_ELEMENTS` available. Resolved by `_elements.py` approach above.

3. **`calc_planet_position_batch` Ketu fix scope**
   - This is a pre-existing correctness bug. Fixing it is the right thing to do in REF-01 since
     the strategy table eliminates the divergence. However, the batch Ketu path has never been
     tested (it silently ran the wrong code). The fix may change test output for batch Ketu calls.
     Verify no tests currently assert the (wrong) batch Ketu values.

---

## Sources

### Primary (HIGH confidence — direct source reading)
- `/home/loc/workspace/ketu/ketu/ephemeris/planets.py` — full read, lines 1–579
- `/home/loc/workspace/ketu/ketu/ephemeris/orbital.py` — full read, lines 1–860
- `/home/loc/workspace/ketu/tests/charts/conftest.py` — full read
- `/home/loc/workspace/ketu/tests/synastry/conftest.py` — full read
- `/home/loc/workspace/ketu/tests/composite/conftest.py` — full read
- `/home/loc/workspace/ketu/tests/returns/conftest.py` — full read
- `/home/loc/workspace/ketu/tests/test_vectorization.py` — full read
- `/home/loc/workspace/ketu/tests/test_ketu.py` — full read
- `/home/loc/workspace/ketu/tests/test_lilith_cross_check.py` — full read
- `/home/loc/workspace/ketu/tests/test_planets_coverage.py` — full read
- `/home/loc/workspace/ketu/ketu/ephemeris/__init__.py` — full read
- `/home/loc/workspace/ketu/pyproject.toml` — coverage config
- `/home/loc/workspace/ketu/.github/workflows/tests.yml` — CI coverage gate

---

## Metadata

**Confidence breakdown:**
- REF-01 strategy pattern: HIGH — code read in full, all branches documented
- REF-02 module split: HIGH — import surface mapped exhaustively
- REF-03 conftest consolidation: HIGH — all four conftest files read, fixtures catalogued
- Byte-stability verification: HIGH — regression test files identified and read
- Coverage risks: HIGH — exclude_lines and coverage config read

**Research date:** 2026-05-29
**Valid until:** Stable until source files are modified (no external dependencies)

---

## Appendix: Key File:Line References

| Concern | File | Lines |
|---------|------|-------|
| `calc_planet_position` if-elif | `ketu/ephemeris/planets.py` | 93–189 |
| `calc_planet_position_batch` if-elif | `ketu/ephemeris/planets.py` | 484–577 |
| **Ketu batch bug** | `ketu/ephemeris/planets.py` | **530** — `["Rahu", "NorthNode", "Lilith"]` missing `"Ketu"` |
| `@lru_cache` on scalar | `ketu/ephemeris/planets.py` | 69 |
| `BODY_INDICES` | `ketu/ephemeris/planets.py` | 35–49 |
| `SWE_IDS` | `ketu/ephemeris/planets.py` | 52–66 |
| `get_planet_name` duplicate dict | `ketu/ephemeris/planets.py` | 214–228 |
| `calculate_all_positions` hardcoded `range(13)` | `ketu/ephemeris/planets.py` | 248 |
| ORBITAL_ELEMENTS | `ketu/ephemeris/orbital.py` | 67–208 |
| Lilith constants | `ketu/ephemeris/orbital.py` | 49–53 |
| `normalize_angle` | `ketu/ephemeris/orbital.py` | 211–228 |
| `solve_kepler_equation` | `ketu/ephemeris/orbital.py` | 231–269 |
| `orbital_elements_at_date` | `ketu/ephemeris/orbital.py` | 272–302 |
| `compute_position` | `ketu/ephemeris/orbital.py` | 305–356 |
| `apply_perturbations` (Jupiter/Saturn/Uranus) | `ketu/ephemeris/orbital.py` | 359–472 |
| `get_body_position` | `ketu/ephemeris/orbital.py` | 475–507 |
| `get_moon_position` | `ketu/ephemeris/orbital.py` | 510–605 |
| `get_lunar_nodes` | `ketu/ephemeris/orbital.py` | 608–639 |
| `get_lilith_position` | `ketu/ephemeris/orbital.py` | 642–691 |
| `get_body_position_vectorized` | `ketu/ephemeris/orbital.py` | 694–760 |
| `get_moon_position_vectorized` | `ketu/ephemeris/orbital.py` | 763–859 |
| Synastry chart fixtures (to consolidate) | `tests/synastry/conftest.py` | 87–133 |
| Composite chart fixtures (to consolidate) | `tests/composite/conftest.py` | 88–134 |
| Returns natal triples (to consolidate) | `tests/returns/conftest.py` | 32–115 |
| Vectorization regression (1e-10 / 1e-8) | `tests/test_vectorization.py` | 47, 69, 88 |
| Precision regression (JPL Horizons) | `tests/test_ketu.py` | 381–488 |
| Lilith regression (swisseph, 0.005°) | `tests/test_lilith_cross_check.py` | 154–180 |
| `ketu/ephemeris/__init__.py` orbital imports | `ketu/ephemeris/__init__.py` | 18–29 |
