# Phase 24: Chiron — Research

**Researched:** 2026-05-29
**Domain:** Python packaging (importlib.resources), ephemeris integration, body-count ratchet audit
**Confidence:** HIGH

---

## Summary

Phase 23 locked all algorithmic parameters (see `23-DECISION.md` — do NOT re-research). This document covers ONLY the six open implementation/integration gaps deferred to Phase 24: .npz packaging, offline generator placement, CI strategy for the pyswisseph oracle, Chiron's insertion points (Chebyshev-only, no Keplerian row), the authoritative body-count assertion audit, and downstream dtype/shape ripple.

The core insight for the body-count work: `_BODY_COUNT` in `ketu/charts/api.py` is `len(ketu.core.bodies)`, so adding the Chiron row to `ketu/core.py` **automatically propagates** to `charts`, `composite/api.py` has a hardcoded `_BODY_COUNT = 13` that must be updated, and `CHART_DTYPE` in `ketu/charts/core.py` has hardcoded `(13,)` and `(13, 13)` subarray shapes that must be manually changed. `SYNASTRY_BODY_COUNT` goes 15 → 16, and `ketu/cache/ephemeris_cache.py:BODY_COUNT = 13` must go to 14.

**Primary recommendation:** Ship `chiron_coeffs.npz` in `ketu/data/` as a package; use `importlib.resources.files("ketu.data").joinpath("chiron_coeffs.npz")` as the loader idiom; put the generator at `tools/gen_chiron_coeffs.py`; pin hardcoded reference longitudes for the regression test (no pyswisseph at test time).

---

## Gap 1 — .npz packaging inside the wheel

### Decision

Use a new `ketu/data/` package directory. This is the cleanest path.

### pyproject.toml changes

```toml
[tool.setuptools]
packages = [
    "ketu", "ketu.ephemeris", "ketu.aspects", "ketu.cycles",
    "ketu.cache", "ketu.houses", "ketu.charts", "ketu.cli",
    "ketu.synastry", "ketu.composite", "ketu.returns", "ketu.parts",
    "ketu.data",          # NEW
]

[tool.setuptools.package-data]
ketu = ["py.typed"]
"ketu.data" = ["*.npz"]  # NEW: ships chiron_coeffs.npz into the wheel
```

### MANIFEST.in

A `MANIFEST.in` already exists (`/home/loc/workspace/ketu/MANIFEST.in`). It does NOT cover `ketu/data/*.npz` — add one line:

```
recursive-include ketu/data *.npz
```

This is required for sdist correctness (without it `pip install` from a tarball would silently omit the .npz). Pyproject-only builds (PEP 517) still need MANIFEST.in for sdist source inclusion when using setuptools.

### Loader idiom (works 3.10-3.13)

```python
# ketu/ephemeris/chiron.py (the new Chebyshev evaluator module)
from importlib.resources import files
import numpy as np

def _load_chiron_data() -> dict[str, np.ndarray]:
    """Load Chiron Chebyshev coefficients from the installed package data."""
    ref = files("ketu.data").joinpath("chiron_coeffs.npz")
    with ref.open("rb") as fh:
        npz = np.load(fh)
        return {k: npz[k] for k in npz.files}
```

`importlib.resources.files()` is the stable API since Python 3.9 (PEP 451). It returns a `Traversable` object that works for editable installs, wheel installs, and zipimport. No fallback to `pkg_resources` needed.

**`ketu/data/__init__.py`** — create an empty file; setuptools requires it for the directory to be recognised as a package.

### Confidence: HIGH

`importlib.resources.files()` is the documented approach for Python ≥ 3.9 and is what setuptools `package-data` targets internally.

---

## Gap 2 — Offline generator placement and invocation

### Decision

Place the generator at `tools/gen_chiron_coeffs.py` at the repo root. Rationale:

- The repo already has `scripts/` (contains `precompute_ephemeris.py`, `snapshot_reference_charts.py`, `check_planning_coherence.py`) — these are operational scripts that run against the installed package.
- The Chiron generator is a **one-time build artifact producer**, not operational. It belongs in `tools/` alongside other build-time tooling.
- A `tools/` directory is OUTSIDE `ketu/` (never imported by the package) and OUTSIDE `tests/` (never collected by pytest). This satisfies CHIR-01's constraint exactly.

### Invocation

```bash
# Run once with pyswisseph [test] extra installed and seas_18.se1 available:
SE_EPHE_PATH=/path/to/dir/containing/seas_18.se1 \
  python tools/gen_chiron_coeffs.py --output ketu/data/chiron_coeffs.npz

# After running, commit the .npz:
git add ketu/data/chiron_coeffs.npz
git commit -m "feat(24): generate Chiron Chebyshev coefficients (seg=32j, deg=10)"
```

### Generator content

The generator is a hardened version of `spike_chiron_chebyshev.py` (`.planning/phases/23-spike-chiron/spike_chiron_chebyshev.py`). Key differences from the spike:

1. Accepts `--output` path argument; writes to `ketu/data/chiron_coeffs.npz` by default.
2. Uses `np.savez_compressed` (not `savez`) — spike confirmed layout.
3. Validates output by running the evaluator and checking `max|Δλ| < 0.01°` before saving.
4. Has a docstring + argparse `--help`.
5. Does NOT produce lat/dist sweeps — runs all 3 quantities in one pass.

### pytest collection guard

The `pyproject.toml` `[tool.pytest.ini_options]` sets `testpaths = ["tests"]`. Since `tools/` is not under `tests/`, pytest never collects it. No additional guard needed. Confirm with:

```bash
pytest --collect-only 2>&1 | grep "tools/"  # Expected: empty
```

### Confidence: HIGH

The `scripts/` precedent exists in the repo and the `tools/` approach is standard.

---

## Gap 3 — CI / seas_18.se1 strategy for CHIR-03 accuracy regression test

### Recommendation: hardcoded pinned reference longitudes (no pyswisseph at test time)

This is the established Ketu pattern. Evidence:

- `tests/composite/test_oracle.py` — three reference composite pairs pinned as regression fixtures (JSON), compared by self-consistency; pyswisseph cross-check is deferred to human review.
- `tests/test_lilith_cross_check.py` — pyswisseph cross-check runs only when `pyswisseph` is installed (`pytest.importorskip("swisseph")`); the PRIMARY regression gate is pinned constants.
- `tests/returns/test_returns_oracle.py` — fixtures pinned as JSON; pyswisseph cross-check is `pytest.importorskip`-gated (skipped if absent) and does NOT require `seas_18.se1` (standard planetary bodies only).

For Chiron, the situation is HARDER than returns/composite: the oracle (`swe.calc_ut(jd, swe.CHIRON, ...)`) requires `seas_18.se1` which is NOT bundled with pyswisseph. CI would need the file committed or downloaded. This is unique complexity.

**Recommended approach:** Capture reference longitudes ONCE during the generator run (using the spike's oracle), store them as a Python dict in the test file, and test that `_chiron_scalar(jd)` agrees within `< 0.01°`. No pyswisseph, no `seas_18.se1` in CI.

```python
# tests/ephemeris/test_chiron_regression.py

# Reference longitudes captured 2026-05-29 using pyswisseph + seas_18.se1.
# Dates span Chiron's ~50.7yr period: one per ~10yr.
# Tolerance: 0.01° (spike-validated max|Δλ| = 0.000861°; tolerance is 11.6x looser).
_CHIRON_REFS: list[tuple[float, float]] = [
    # (jd, expected_lon_deg)
    (2433282.5, <lon_at_1950-01-01>),   # 1950-01-01
    (2440587.5, <lon_at_1970-01-01>),   # 1970-01-01
    (2447892.5, <lon_at_1990-01-01>),   # 1990-01-01
    (2451545.0, <lon_at_2000-01-15>),   # J2000.0
    (2455197.5, <lon_at_2010-01-01>),   # 2010-01-01
    (2462501.5, <lon_at_2030-01-01>),   # 2030-01-01 (future)
    (2469807.5, <lon_at_2050-01-01>),   # 2050-01-01
]
TOLERANCE_DEG = 0.01

@pytest.mark.parametrize("jd, expected_lon", _CHIRON_REFS)
def test_chiron_regression(jd: float, expected_lon: float) -> None:
    """CHIR-03: Chiron longitude within spike-validated 0.01° bound."""
    from ketu.ephemeris.planets import calc_planet_position
    pos = calc_planet_position(jd, 13)
    delta = abs(pos[0] - expected_lon)
    if delta > 180.0:
        delta = 360.0 - delta
    assert delta < TOLERANCE_DEG, (
        f"Chiron lon={pos[0]:.6f}° differs from ref {expected_lon:.6f}° "
        f"by {delta:.6f}° (>{TOLERANCE_DEG}°)"
    )
```

Reference values are captured by running `tools/gen_chiron_coeffs.py --dump-refs` (the generator can print them) or by running the spike one final time before committing.

**Why not `importorskip` + seas_18.se1?** The `test_lilith_cross_check.py` pattern would work for `pyswisseph` (auto-skip if absent), but `seas_18.se1` is not installed with pyswisseph — it would need to be committed into the repo (`tests/res/` option from 23-DECISION §3.3). At 217 KB, committing it is not absurd, but it adds binary blob churn to git history whenever the generator reruns. The pinned-constant approach is zero-dependency and matches the composite/oracle precedent more closely.

### Confidence: HIGH

Pattern directly matches `tests/composite/test_oracle.py` and Ketu's existing convention.

---

## Gap 4 — Chiron as a non-Keplerian body: ORBITAL_ELEMENTS insertion point

### Decision: Chiron does NOT get an ORBITAL_ELEMENTS row

Key finding from reading the code:

`ORBITAL_ELEMENTS` (in `ketu/ephemeris/_elements.py`) is a structured NumPy array consumed by `_body_getters.py` (`get_body_position`, `get_body_position_vectorized`) and `_mechanics.py` (`orbital_elements_at_date`, `compute_position`). These Keplerian mechanics functions are called by `_make_planet_scalar` and `_make_planet_vec` factories in `planets.py`.

Rahu, Ketu (the node), and Lilith do have rows in `ORBITAL_ELEMENTS` (for dtype/shape completeness and historical reasons), BUT their actual computation in `planets.py` uses `_scalar_loop_vec` via `get_lunar_nodes` and `get_lilith_position` — the ORBITAL_ELEMENTS rows for those bodies are never accessed by their planet strategy functions.

However, Chiron is DIFFERENT: the ORBITAL_ELEMENTS rows for Rahu/Ketu/Lilith exist because `BODY_INDICES` maps them into the array by name and some legacy paths use the array. For Chiron, there is no Keplerian formula — the evaluator is purely Chebyshev.

**Authoritative mapping of the 6 CHIR-02 insertion points:**

| Insertion point | File | What to do |
|---|---|---|
| 1. `BODY_INDICES` | `ketu/ephemeris/planets.py:L35-49` | `BODY_INDICES["Chiron"] = 13` |
| 2. `SWE_IDS` | `ketu/ephemeris/planets.py:L52-66` | `SWE_IDS[13] = "Chiron"` |
| 3. `BODY_STRATEGIES` | `ketu/ephemeris/planets.py:L310-324` | `BODY_STRATEGIES["Chiron"] = _BodyCalc(_chiron_scalar, _chiron_vec)` |
| 4. `calc_planet_position` error msg | `planets.py:L352` | Change `"Valid range: 0-12"` to `"Valid range: 0-13"` |
| 5. `core.py bodies` array | `ketu/core.py:L66-83` | Append Chiron row |
| 6. `ORBITAL_ELEMENTS` | `ketu/ephemeris/_elements.py` | **DO NOT ADD** — see below |

**Why no ORBITAL_ELEMENTS row:** The 23-DECISION §6 description of "6 insertion points" listed `orbital.py ORBITAL_ELEMENTS` but this is incorrect for a Chebyshev body. `ORBITAL_ELEMENTS` is only consumed by `_body_getters.py` and `_mechanics.py` for Keplerian heliocentric position; Chiron's strategy (`_chiron_scalar`, `_chiron_vec`) bypasses all of that, calling `np.polynomial.chebyshev.chebval` directly on the loaded .npz data. No code path from `BODY_STRATEGIES["Chiron"]` ever touches `ORBITAL_ELEMENTS`.

The actual 6th insertion point is: **`calculate_speed_ratio` `avg_speeds` dict** in `planets.py:L579-592`. This dict is keyed by `body_id` integer and currently covers 0-12. Chiron (body_id=13) needs an entry or the function falls back to `avg_speed = 1.0` (not a crash, but an inaccurate ratio). Chiron's mean motion is approximately `360° / (50.7 yr × 365.25 d/yr) ≈ 0.01946°/day`. Add `13: 0.01946` to the dict.

**New Chiron strategy functions** (`ketu/ephemeris/chiron.py` new module):

```python
# ketu/ephemeris/chiron.py
import numpy as np
from importlib.resources import files
from functools import lru_cache

@lru_cache(maxsize=1)
def _load_chiron_data() -> dict[str, np.ndarray]:
    ref = files("ketu.data").joinpath("chiron_coeffs.npz")
    with ref.open("rb") as fh:
        npz = np.load(fh)
        return {k: npz[k] for k in npz.files}

def _eval_chiron_qty(jd: float, coeffs: np.ndarray,
                     seg_starts: np.ndarray, seg_len: float) -> float:
    si = int((jd - seg_starts[0]) / seg_len)
    si = max(0, min(si, len(seg_starts) - 1))
    t = float(np.clip(2.0 * (jd - seg_starts[si]) / seg_len - 1.0, -1.0, 1.0))
    return float(np.polynomial.chebyshev.chebval(t, coeffs[si]))

def _chiron_scalar(jd: float) -> tuple[float, float, float, float, float, float]:
    data = _load_chiron_data()
    seg_starts: np.ndarray = data["seg_starts"]
    seg_len = float(data["seg_len"])
    jd_delta = 0.01

    lon  = _eval_chiron_qty(jd, data["lon_coeffs"], seg_starts, seg_len) % 360.0
    lat  = _eval_chiron_qty(jd, data["lat_coeffs"], seg_starts, seg_len)
    dist = _eval_chiron_qty(jd, data["dist_coeffs"], seg_starts, seg_len)

    lon1  = _eval_chiron_qty(jd + jd_delta, data["lon_coeffs"], seg_starts, seg_len) % 360.0
    lat1  = _eval_chiron_qty(jd + jd_delta, data["lat_coeffs"], seg_starts, seg_len)
    dist1 = _eval_chiron_qty(jd + jd_delta, data["dist_coeffs"], seg_starts, seg_len)

    dlon = lon1 - lon
    if dlon > 180.0:   dlon -= 360.0
    if dlon < -180.0:  dlon += 360.0
    return lon, lat, dist, dlon / jd_delta, (lat1 - lat) / jd_delta, (dist1 - dist) / jd_delta

def _chiron_vec(jd_array: np.ndarray) -> tuple[...]:
    # Vectorized via scalar loop (same pattern as _scalar_loop_vec for Rahu/Ketu)
    # Import here to avoid circular; _scalar_loop_vec in planets.py wraps calc_planet_position
    # which already handles planet_id=13 once wired.
    # Implementation: loop over jd_array calling _chiron_scalar, stack results.
    n = len(jd_array)
    out = np.zeros((n, 6))
    for i, jd in enumerate(jd_array):
        out[i] = _chiron_scalar(float(jd))
    return (out[:, 0], out[:, 1], out[:, 2], out[:, 3], out[:, 4], out[:, 5])
```

**Note on `_chiron_vec` and aberration:** `_make_planet_vec` applies aberration INSIDE the vectorized function (by design, to match the original batch else-branch). `_scalar_loop_vec` does NOT apply aberration inside — it calls `calc_planet_position` which applies aberration at the router level for planet_id >= 2. Since Chiron (body_id=13 >= 2), the router already applies aberration after calling `BODY_STRATEGIES["Chiron"].scalar(jd)`. For the vectorized path (`calc_planet_position_batch`), the batch router calls `BODY_STRATEGIES[name].vectorized(jd_array)` and does NOT apply aberration (that was only done inside `_make_planet_vec`). If Chiron should have aberration in the batch path, `_chiron_vec` must apply it internally — matching `_make_planet_vec` pattern. Given Chiron's slow movement (~0.019°/day), aberration (~20 arcsec) is within the 0.01° accuracy budget but at the margin. **Recommendation:** Apply aberration in `_chiron_vec` for consistency with other planets. Add the same aberration loop as in `_make_planet_vec` (lines 269-273 of `planets.py`).

### Confidence: HIGH

Code path verified by reading `_body_getters.py`, `_mechanics.py`, and the BODY_STRATEGIES pattern.

---

## Gap 5 — Authoritative body-count assertion audit

### Authoritative table

**Legend:** AXIS-INDEX = synastry ASC/MC axes (must NOT change); BODY-COUNT = actual count of bodies (must update 13→14); ASPECT-COUNT = count of aspect types (unrelated, must stay 14).

| File | Line(s) | Value | Classification | Phase 24 action |
|------|---------|-------|----------------|-----------------|
| `tests/test_ketu.py` | 110 | `len(bodies) == 13` | BODY-COUNT | Change to 14 + rename test to `test_body_count_frozen_at_fourteen` |
| `tests/charts/test_dtype.py` | 218-235 | `_BODY_COUNT == 13` | BODY-COUNT | Change assertion to 14; update docstring |
| `tests/charts/test_dtype.py` | 60-74 | `("body_lons", (13,))` etc. | BODY-COUNT (subarray shape) | Change all `(13,)` to `(14,)`, `(13, 13)` to `(14, 14)` |
| `tests/charts/test_dtype.py` | 116-129 | `arr["body_lons"].shape == (5, 13)` | BODY-COUNT | Change to `(5, 14)`, etc. |
| `tests/charts/test_dtype.py` | 132-139 | `elem["body_lons"].shape == (13,)` | BODY-COUNT | Change to `(14,)` |
| `tests/charts/test_dtype.py` | 169 | `arr["aspect_matrix"][0, 0, 1] == 13` | ASPECT-COUNT (aspect index 13 = Opposition) | KEEP — this is the aspect type index, not a body count |
| `tests/test_planets_coverage.py` | 178 | `len(positions) == 13` | BODY-COUNT | Change to 14 |
| `tests/test_planets_coverage.py` | 375 | `range(13)` | BODY-COUNT | Change to `range(14)` |
| `tests/test_planets_coverage.py` | 531 | `range(13)` | BODY-COUNT | Change to `range(14)` |
| `tests/test_transits.py` | 152, 178 | `len(natal) == 13` | BODY-COUNT | Change to 14 |
| `tests/test_transits_coverage.py` | 307 | `len(natal) == 13` | BODY-COUNT | Change to 14 |
| `tests/composite/test_calculate_composite.py` | 27 | `list(range(13))` | BODY-COUNT | Change to `range(14)`; also update `_BODY_NAMES` list |
| `tests/charts/test_compute_chart.py` | 138 | `range(13)` | BODY-COUNT | Change to `range(14)` |
| `tests/charts/test_compute_chart.py` | 184 | `range(13)` | BODY-COUNT (aspect matrix diagonal loop) | Change to `range(14)` |
| `tests/charts/test_aspect_matrix.py` | 123, 173, 344, 368 | `range(13)` / `combinations(range(13), 2)` | BODY-COUNT | Change to `range(14)` |
| `tests/synastry/test_dtype.py` | 122-127 | `SYNASTRY_BODY_COUNT == 15` | BODY-COUNT (15 = 13 canonical + ASC + MC) | Change to 16 (14 canonical + ASC + MC) |
| `tests/synastry/test_calculate_synastry.py` | 140-141 | `body_a == 13` (ASC_A) / `body_a == 14` (MC_A) | AXIS-INDEX (ASC=13, MC=14 in OLD scheme) | After 14 canonical bodies: ASC becomes 14, MC becomes 15. All these must be updated. |
| `tests/synastry/test_calculate_synastry.py` | 225, 227, 235, 237 | `body_a == 13` (ASC), `body_a == 14` (MC) | AXIS-INDEX | Change to 14 (ASC), 15 (MC) |
| `tests/synastry/test_calculate_synastry.py` | 384 | `body_b == 13` or `body_b == 14` | AXIS-INDEX | Change to 14, 15 |
| `tests/synastry/test_applying.py` | 135-136, 167-168 | `== 13` (ASC), `== 14` (MC) | AXIS-INDEX | Change to 14, 15 |
| `tests/test_aspect_presets.py` | 46-47, 67, 80, 89, 209 | `range(14)`, `sum() == 14` | ASPECT-COUNT (14 aspect types, not bodies) | KEEP — refers to core.aspects length |
| `tests/synastry/test_dtype.py` | 172 | `aspect_type == 13` | ASPECT-COUNT (index of Opposition) | KEEP |

**Synastry axis-index shift** is the most complex change: currently `SYNASTRY_BODY_COUNT = 15` (indices 0..12 = bodies, 13 = ASC, 14 = MC). After adding Chiron as body_id=13, the scheme becomes: 0..13 = bodies, 14 = ASC, 15 = MC. `SYNASTRY_BODY_COUNT` becomes 16. All synastry tests that hardcode `== 13` (ASC) or `== 14` (MC) must become `== 14` and `== 15`.

### Source code body-count locations (ketu/ not tests/)

| File | Location | What to change |
|------|----------|----------------|
| `ketu/core.py` | `bodies` array, docstring | Append Chiron row; update docstring counts |
| `ketu/charts/core.py` | `CHART_DTYPE` subarray shapes | `(13,)` → `(14,)`, `(13, 13)` → `(14, 14)` |
| `ketu/charts/api.py` | `_BODY_COUNT = len(_CANONICAL_BODIES)` | Auto-propagates from `ketu.core.bodies` — no manual change needed (derived) |
| `ketu/composite/api.py` | `_BODY_COUNT = 13` (line 80) | Change to `14` (or derive: `_BODY_COUNT = len(_BODIES)`) |
| `ketu/cache/ephemeris_cache.py` | `BODY_COUNT = 13` (line 29), `BODY_IDS` dict | Change to 14; add `"Chiron": 13` to `BODY_IDS` |
| `ketu/synastry/core.py` | `SYNASTRY_BODY_COUNT: int = 15` | Change to 16 |
| `ketu/aspects/transits.py` | `list(range(13))` (line 480) | Change to `list(range(len(SWE_IDS)))` or `range(14)` |
| `ketu/ephemeris/planets.py` | error msg `"Valid range: 0-12"`, `avg_speeds` dict | Update range msg; add `13: 0.01946` to avg_speeds |
| `ketu/ephemeris/planets.py` | docstring for `calc_planet_position` | Update `planet_id: int — Planet ID (0-12)` to 0-13 |
| `ketu/core.py` | module docstring lines 14-25 | Update "13 astronomical bodies" to 14; add Chiron to body ID list |
| `ketu/charts/api.py` | `_vectorised_body_properties` docstring | "Loops over the 13 canonical bodies" → 14 |

### Confidence: HIGH

Every file read directly; classification based on context.

---

## Gap 6 — Downstream dtype/shape ripple

### CHART_DTYPE subarrays: MUST be manually updated

`CHART_DTYPE` in `ketu/charts/core.py` is a hardcoded `np.dtype([..., ("body_lons", "f8", (13,)), ..., ("aspect_matrix", "i1", (13, 13)), ...])`. Adding Chiron to `ketu.core.bodies` does NOT auto-propagate here. The planner must explicitly update every `(13,)` to `(14,)` and both `(13, 13)` to `(14, 14)`.

Fields affected in `CHART_DTYPE`:
- `body_lons`: `(13,)` → `(14,)`
- `body_lats`: `(13,)` → `(14,)`
- `body_speeds`: `(13,)` → `(14,)`
- `aspect_matrix`: `(13, 13)` → `(14, 14)`
- `aspect_orbs`: `(13, 13)` → `(14, 14)`

### Auto-propagating locations (no manual change needed)

- `ketu/charts/api.py:_BODY_COUNT = len(_CANONICAL_BODIES)` — derives from `ketu.core.bodies`, auto-propagates once Chiron row is appended.
- `calculate_all_positions` in `planets.py` — `for planet_id in range(len(SWE_IDS))` — auto-propagates once `SWE_IDS[13] = "Chiron"` is added.

### Cache impact

`ketu/cache/ephemeris_cache.py` allocates `(days_in_month, BODY_COUNT, POSITION_FIELDS)` arrays. `BODY_COUNT = 13` is a hardcoded constant — must be changed to 14. The cache stores positions for all bodies; Chiron at body_id=13 will be correctly stored once the constant is updated and `BODY_IDS["Chiron"] = 13` is added.

### Synastry shape

`SYNASTRY_DTYPE` is a record-style dtype (no subarrays sized by body count — verified from `tests/synastry/test_dtype.py:149-156`). Changing `SYNASTRY_BODY_COUNT` from 15 to 16 propagates to `synastry/api.py:n = SYNASTRY_BODY_COUNT` which controls dense-mode allocation. No dtype field shapes to update in synastry.

### Composite shape

`composite/api.py:_BODY_COUNT = 13` controls aspect matrix allocation (`(13, 13)` → `(14, 14)` arrays). Must be updated to 14 (or derived).

### Returns

`ketu/returns/solar.py` and `ketu/returns/lunar.py` call `compute_chart` internally and return a `CHART_DTYPE` array. Since they delegate to `compute_chart`, they auto-propagate once `CHART_DTYPE` is updated. No manual changes needed in `returns/`.

### Parts

`ketu/parts/` — no hardcoded body counts found. Works on named bodies via the registry. Auto-propagates.

### Confidence: HIGH

All files read directly.

---

## Architecture Patterns

### New file: `ketu/ephemeris/chiron.py`

This is the recommended layout:

```
ketu/ephemeris/chiron.py     # _chiron_scalar, _chiron_vec, _load_chiron_data
ketu/data/__init__.py        # empty, makes ketu.data a package
ketu/data/chiron_coeffs.npz  # generated by tools/gen_chiron_coeffs.py
tools/gen_chiron_coeffs.py   # offline generator (pyswisseph + seas_18.se1 required)
tests/ephemeris/__init__.py  # already exists or create
tests/ephemeris/test_chiron_regression.py  # CHIR-03 pinned reference test
tests/ephemeris/test_chiron_unit.py        # CHIR-01/02 unit tests
```

### Import chain for Chiron

```
ketu/ephemeris/chiron.py
  ← imported by ketu/ephemeris/planets.py
    (adds _chiron_scalar, _chiron_vec to BODY_STRATEGIES["Chiron"])
  ← calls importlib.resources.files("ketu.data") at load time
  ← lru_cache(maxsize=1) to load .npz once
```

### Anti-patterns to avoid

- **Do NOT add a Chiron row to ORBITAL_ELEMENTS.** There is no Keplerian formula for it; the row would be dead code and mislead future readers.
- **Do NOT use `pkg_resources`.** It is deprecated since setuptools 67; `importlib.resources.files()` is the replacement.
- **Do NOT use `np.load(str(path))` with a raw string path** constructed by `__file__` manipulation — this breaks zipimport and editable installs. Use `importlib.resources.files("ketu.data").joinpath("chiron_coeffs.npz").open("rb")`.
- **Do NOT import `swisseph` at module level** in any file under `ketu/` — the AGPL boundary ratchet (`test_no_runtime_swisseph_import`) will fail.

---

## Common Pitfalls

### Pitfall 1: CHART_DTYPE not auto-propagating

`CHART_DTYPE` subarrays are hardcoded literals, not derived from `len(ketu.core.bodies)`. Forgetting to update them will cause shape mismatches at runtime (silent wrong shapes) and test failures in `test_dtype_subarray_shapes`.

### Pitfall 2: Synastry axis-index shift breaks ASC/MC tests

After adding Chiron as body_id=13, the synastry ASC axis shifts from 13 to 14, and MC from 14 to 15. Tests in `tests/synastry/test_calculate_synastry.py` and `tests/synastry/test_applying.py` that check `body_a == 13` (ASC) or `body_a == 14` (MC) will all fail. These are AXIS-INDEX changes, not body-count changes — the planner must treat them carefully.

### Pitfall 3: aberration in `_chiron_vec`

`calc_planet_position_batch` calls `BODY_STRATEGIES[name].vectorized(jd_array)` and does NOT apply aberration (the aberration was applied inside `_make_planet_vec` for historical byte-stability reasons). If `_chiron_vec` does not apply aberration, Chiron positions from the batch path will differ by ~20 arcsec from the scalar path. This is within the 0.01° budget but inconsistent. Apply aberration in `_chiron_vec` matching the `_make_planet_vec` loop pattern.

### Pitfall 4: `lru_cache` on `calc_planet_position` eviction

`calc_planet_position` has `@lru_cache(maxsize=128)`. Tests that call `calc_planet_position.cache_clear()` between tests will continue to work. The `.npz` load via `_load_chiron_data()` has its own `@lru_cache(maxsize=1)` — it is NOT cleared between tests. This is correct (the data does not change), but ensure `_chiron_scalar` is called through `calc_planet_position` (which IS cache-cleared in tests) rather than directly.

### Pitfall 5: coverage gate on `chiron.py` out-of-range JD guard

The `_eval_chiron_qty` function clamps `si` to `[0, n_segs-1]`. The clamping for out-of-range JD is a defensive branch (JD < 1950 or JD > 2050). For 100% coverage these branches must either be tested (with JDs outside the range) or added to `exclude_lines` in `[tool.coverage.report]`. Recommend testing them — the evaluator should return the nearest segment's extrapolation rather than crash.

---

## Suggested Plan Breakdown

### Wave structure

**Wave 1 (foundation — no breakage):**
- Plan 24-01: `tools/gen_chiron_coeffs.py` — offline generator (hardened spike script). Pyswisseph + seas_18.se1 required. Produces `ketu/data/chiron_coeffs.npz`. Commits the .npz to the repo.
- Plan 24-02: `ketu/data/__init__.py` + `ketu/ephemeris/chiron.py` — new module with `_load_chiron_data`, `_chiron_scalar`, `_chiron_vec`. Unit tests for loader and evaluator. No changes to body counts yet; does not break any existing test.

**Wave 2 (wire insertion points — the ratchet):**
- Plan 24-03: Wire all 6 CHIR-02 insertion points in `ketu/`:
  - `ketu/core.py` bodies append Chiron row + docstring
  - `ketu/ephemeris/planets.py` BODY_INDICES + SWE_IDS + BODY_STRATEGIES + avg_speeds + error msg
  - `ketu/ephemeris/chiron.py` imported by `planets.py`
  - `ketu/charts/core.py` CHART_DTYPE subarray shapes (13→14)
  - `ketu/composite/api.py` _BODY_COUNT 13→14
  - `ketu/cache/ephemeris_cache.py` BODY_COUNT 13→14
  - `ketu/synastry/core.py` SYNASTRY_BODY_COUNT 15→16
  - `ketu/aspects/transits.py` range(13) → range(len(SWE_IDS))
  - `pyproject.toml` packages + package-data + MANIFEST.in
  - All test body-count assertions (from Gap 5 table)

**Wave 3 (accuracy regression + docs):**
- Plan 24-04: CHIR-03 regression test file (`tests/ephemeris/test_chiron_regression.py`) with pinned reference longitudes covering 7 dates across 1950-2050. Run generator to capture reference values, pin them, commit.
- Plan 24-05: CHIR-05 smoke tests — `compute_chart` includes Chiron; aspect detection works; `generate_cycle_series` with Chiron pairs. Docstring and numpydoc updates. Update `ketu/core.py` module docstring. Verify coverage gate remains at 100%.

**Gating:** Plan 24-01 must complete before 24-02 (needs the .npz to test the loader). Plans 24-01 and 24-02 can be developed independently from each other in terms of logic, but 24-02 depends on 24-01's .npz being committed. Plan 24-03 depends on 24-02. Plans 24-04 and 24-05 depend on 24-03.

---

## Sources

### Primary (HIGH confidence)
- Direct code reading: `ketu/ephemeris/planets.py`, `ketu/ephemeris/_elements.py`, `ketu/core.py`, `pyproject.toml`, `MANIFEST.in`
- Direct test reading: all files cited in Gap 5 table
- `.planning/phases/23-spike-chiron/23-DECISION.md` — binding decisions and locked parameters
- `.planning/phases/23-spike-chiron/spike_chiron_chebyshev.py` — prototype evaluator code

### Secondary (MEDIUM confidence)
- Python 3.11 docs: `importlib.resources.files()` — standard since 3.9, stable API through 3.13

---

## Metadata

**Confidence breakdown:**
- Gap 1 (.npz packaging): HIGH — pattern verified against existing MANIFEST.in + pyproject.toml
- Gap 2 (generator placement): HIGH — `scripts/` precedent exists; `tools/` is standard convention
- Gap 3 (CI strategy): HIGH — matches composite/oracle pattern exactly
- Gap 4 (insertion points): HIGH — ORBITAL_ELEMENTS non-insertion confirmed by code path tracing
- Gap 5 (body-count audit): HIGH — every file read, every line classified
- Gap 6 (dtype ripple): HIGH — auto-propagation vs hardcoded distinguished by direct reading

**Research date:** 2026-05-29
**Valid until:** 2026-07-15 (stable codebase, no fast-moving dependencies)
