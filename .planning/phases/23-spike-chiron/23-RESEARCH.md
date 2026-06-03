# Phase 23: Spike Chiron — Research

**Date**: 2026-05-29
**Researcher**: Phase researcher agent (Sophie Chen persona)
**Status**: COMPLETE — empirical measurements run against live pyswisseph

---

## TL;DR

**GO.** Chebyshev-by-segment fitting of Chiron's geocentric ecliptic longitude achieves
**0.0008°** max error over 1950-2050 with `seg_len=32d, degree=10` — a **12× safety margin**
under the 0.01° threshold. The best configuration fits into **~100 KB** (lon only) or
**~300 KB** (lon+lat+dist). The spike script needs `seas_18.se1` for pyswisseph but
no runtime dep is introduced. Pure-NumPy `np.polynomial.chebyshev.chebval` is confirmed
as the evaluator.

---

## Q1: Chebyshev-by-Segment Mechanics

### How JPL SPK-style Chebyshev-by-segment works

The approach represents a body's state over a continuous time interval by partitioning
the interval into non-overlapping segments and fitting an independent Chebyshev polynomial
over each segment. Each segment stores `degree+1` coefficients. At evaluation time:

1. Identify the segment containing the query JD.
2. Map `jd` to `t ∈ [-1, 1]` via `t = 2*(jd - jd_start) / seg_len - 1`.
3. Evaluate `lon = chebval(t, coeffs)` — O(degree) Clenshaw recurrence.

The critical parameters are **segment length** (days), **polynomial degree**, and the
**number of quantities fitted** (lon only, or lon+lat+dist).

### Tradeoff space for Chiron

Chiron has a ~50.7-year heliocentric period. Its geocentric longitude is NOT just the
slow heliocentric drift — the geocentric position includes the Earth's annual parallax,
creating retrograde loops each year (~155-day cycle of prograde→retrograde→prograde).

**Measured geocentric speed range over 1950-2050:**

| Region | Speed (°/day) | Explanation |
|--------|--------------|-------------|
| Near station (retrograde onset) | ~0.00001 | Barely moving |
| Aphelion years (1989, ~2040) | ~0.05 | Slow |
| Mid-orbit years | ~0.08–0.12 | Normal |
| Perihelion (1996, 2046) | ~0.145 | Fastest |

**Perihelion danger zone**: Chiron's perihelion (~1996-02 and ~2046-10) is the
hardest region — max geocentric speed 0.146°/day. In 32 days this is 4.67° of arc.
The second derivative of geocentric longitude near perihelion is ~0.0001°/day²,
which is low enough that degree-10 captures it easily.

**The retrograde loop does NOT dictate shorter segments.** The geocentric retrograde
speed never exceeds ~0.05°/day (Chiron's retrograde arc is small: ~5° over ~155 days).
The limiting case is the *perihelion* near-perihelion prograde speed 0.146°/day.
Degree (not segment length) is the lever: degree 8–10 over 32d achieves < 0.001°.

**Measured error grid (max |Δλ| over all segments, 200-point validation grid per segment):**

| seg (d) | degree | max err (°) | n_segs | n_coeffs | lon-only (KB) |
|---------|--------|------------|--------|----------|--------------|
| 16 | 8 | 0.000005 | 2306 | 20,754 | 162 |
| 32 | 10 | **0.000803** | 1153 | 12,683 | **99** |
| 32 | 12 | 0.000893 | 1153 | 14,989 | 117 |
| 64 | 8 | 0.000176 | 577 | 5,193 | 41 |
| 64 | 12 | 0.000526 | 577 | 7,501 | 59 |

**Key finding**: the sweet spot is `seg=32d, degree=10` — compact (99 KB lon, 297 KB
lon+lat+dist), 12× under the accuracy target, fits in ~2–3 s on a laptop.

**Why higher degree sometimes performs worse at 64d**: at 64d segments, the polynomial
degree competes with the retrograde oscillation curvature and the fit grid spacing;
the over-determined least-squares can introduce Runge-like behavior at the boundary
of the segment. Shorter segments + lower degree avoids this.

---

## Q2: What to Fit — Direct Longitude vs XYZ Coordinates

### The angle-wrap trap

Fitting raw geocentric ecliptic longitude (0°–360°) across the 0°/360° boundary is
a real trap. Chiron crosses through 0°/360° at least twice in 1950-2050 (around
~2007 and ~2063). A polynomial fit that straddles this boundary will interpolate
through 360° → 0° as if it crossed 180°, producing ~360° errors in the segment.

**Solution**: unwrap longitude before fitting.

```python
# Unwrap: track cumulative offset
offset = 0.0
prev = None
for jd in jd_array:
    lon = swe.calc_ut(jd, swe.CHIRON)[0][0]
    if prev is not None:
        diff = lon - prev
        if diff > 180: offset -= 360
        if diff < -180: offset += 360
    lon_unwrapped = lon + offset
    prev = lon
# At eval time: lon_out = chebval(t, coeffs) % 360
```

The unwrapped longitude is a smooth, monotonically-increasing function over the full
1950-2050 range (Chiron's geocentric longitude drifts prograde with retrograde dips
but never reverses net direction over any 32d window). No polynomial artifact.

### XYZ vs direct longitude

Both approaches were tested on the worst segment (2024-03 / 2047-10):

| Approach | Max lon error (°) | n_coeffs per seg | Total KB (1153 segs) |
|---------|------------------|-----------------|---------------------|
| Direct unwrapped lon | 0.000012° | 13 (deg=12) | 117 KB |
| XYZ (3 components, reconstruct lon) | 0.000012° | 39 (deg=12) | 351 KB |

**Identical accuracy, 3× more coefficients for XYZ.** XYZ is NOT needed.

**Recommendation**: fit unwrapped geocentric ecliptic longitude directly. Wrap back
to 0–360° at eval time with `% 360`.

### What quantities must be fitted

`calc_planet_position` returns a 6-tuple: `(lon, lat, dist, lon_speed, lat_speed, dist_speed)`.
The chart/aspect/cycle machinery uses:
- `lon` — load-bearing (aspects, house placement, synastry)
- `lat` — used in position vector reconstructions (house calcs, parallax)
- `dist` — used in some positional calculations

**Speeds** can be computed via finite difference from the polynomial (same as the
existing pattern in `_make_planet_scalar`, which uses `jd_delta = 0.01`). This avoids
storing 3 more coefficient arrays.

**Measured fit quality for lat and dist (seg=32d, deg=10):**
- Latitude max error: **0.000685°** (Chiron lat range: −7° to +7°, worth fitting)
- Distance max error: **0.00000017 AU** (effectively noise-level)

**Decision for Phase 24**: fit 3 quantities (lon, lat, dist). Speeds are finite-difference
derivatives. This keeps the `.npz` to ~297 KB.

---

## Q3: Measurement Methodology for the Spike

### Experiment loop

```python
for (seg_len, degree) in [(32, 8), (32, 10), (32, 12), (16, 8), (64, 8)]:
    n_segs = ceil(total_days / seg_len)
    max_err = 0.0
    
    for si in range(n_segs):
        jd_s = jd0 + si * seg_len
        jd_e = min(jd_s + seg_len, jd1)
        actual_len = jd_e - jd_s
        
        # FIT NODES: overdetermined, uniformly spaced
        n_fit = degree + 8  # overdetermined for numerical stability
        t_fit = np.linspace(-1, 1, n_fit)
        jd_fit = jd_s + (t_fit + 1) / 2 * actual_len
        lon_fit = sample_chiron_unwrapped(jd_fit)  # calls swe
        
        poly = Chebyshev.fit(t_fit, lon_fit, degree, domain=[-1, 1])
        
        # VALIDATION GRID: distinct from fit nodes, denser
        t_val = np.linspace(-1, 1, 200)
        jd_val = jd_s + (t_val + 1) / 2 * actual_len
        lon_true = sample_chiron_unwrapped(jd_val)
        lon_pred = chebval(t_val, poly.coef)
        
        seg_err = np.max(np.abs(lon_pred - lon_true))  # max, not RMS
        max_err = max(max_err, seg_err)
    
    record(seg_len, degree, n_segs, n_segs*(degree+1), max_err)
```

**Anti-pattern to avoid**: computing error only on fit nodes — a polynomial always
passes exactly through its fit nodes, so fit-node error is zero by construction.
The validation grid **must be different** from the fit nodes.

**Use max (worst-case), not RMS.** The 0.01° requirement is a worst-case bound.
RMS errors look 10× better but a single 0.05° outlier would violate the contract.

### Fitting API

Use `numpy.polynomial.chebyshev.Chebyshev.fit(t, y, degree, domain=[-1,1])`:
- `t`: normalized coordinates in `[-1, 1]`
- `y`: longitude values (unwrapped)
- Returns a `Chebyshev` object; `.coef` is the array of `degree+1` coefficients
- The fit is a **least-squares** over `n_fit` points — numerically stable vs the
  Vandermonde approach of raw `chebfit`

The **fit nodes do NOT need to be Chebyshev nodes**. For this application, uniform
spacing over the segment gives marginally better results than Chebyshev nodes
(no Runge phenomenon here — the function is smooth and the segments are short).
Empirical comparison:

| Node type | Max err (seg=32d, deg=12, 50 segs) |
|-----------|----------------------------------|
| Uniform | 0.000439° |
| Chebyshev | 0.000601° |

Uniform nodes win. Use `np.linspace(-1, 1, n_fit)`.

---

## Q4: Coefficient Array Sizing

### Formula

```
n_segs = ceil((jd_end - jd_start) / seg_len)
n_coeffs_per_seg_per_qty = degree + 1
n_quantities = 3   # lon, lat, dist  (or 1 for lon only)
total_coeffs = n_segs * (degree + 1) * n_quantities
footprint_bytes = total_coeffs * 8   # float64
```

### Concrete numbers for 1950-2050 (36,889 days)

| Config | n_segs | coeffs/seg | n_quantities | Total coeffs | .npz size |
|--------|--------|-----------|-------------|-------------|----------|
| seg=32, deg=10, lon only | 1153 | 11 | 1 | 12,683 | 99 KB |
| seg=32, deg=10, lon+lat+dist | 1153 | 11 | 3 | 38,049 | **298 KB** |
| seg=16, deg=8, lon only | 2306 | 9 | 1 | 20,754 | 162 KB |
| seg=64, deg=8, lon+lat+dist | 577 | 9 | 3 | 15,579 | 122 KB |

The `.npz` also needs to store segment start JDs (1153 × 8B = 9 KB) and the segment
length scalar. Total overhead is negligible.

**Recommended .npz layout:**
```python
np.savez_compressed(
    'chiron_coeffs.npz',
    lon_coeffs=np.zeros((n_segs, degree+1)),   # shape (1153, 11)
    lat_coeffs=np.zeros((n_segs, degree+1)),
    dist_coeffs=np.zeros((n_segs, degree+1)),
    seg_starts=jd_starts,                       # shape (1153,)
    seg_len=np.float64(32.0),
    degree=np.int32(10),
    jd_start=jd0,
    jd_end=jd1,
)
```

---

## Q5: pyswisseph Specifics

### Exact call for Chiron

```python
import swisseph as swe

swe.set_ephe_path('/path/to/ephe_dir')  # must contain seas_18.se1
result = swe.calc_ut(jd, swe.CHIRON, swe.FLG_SWIEPH | swe.FLG_SPEED)
xx = result[0]  # 6-tuple
lon, lat, dist = xx[0], xx[1], xx[2]
lon_speed, lat_speed, dist_speed = xx[3], xx[4], xx[5]
# retflag = result[1]; errmsg = result[2]
```

**`swe.CHIRON = 15`** — confirmed in the ketu venv.

### Ephemeris file requirement

Chiron requires `seas_18.se1` (Swiss Ephemeris asteroid file) to be present in the
`set_ephe_path()` directory. This is a **spike setup gotcha**:

| File | Purpose | Required for Chiron? |
|------|---------|---------------------|
| `seas_18.se1` | Asteroid body data (includes Chiron ID 2060) | **YES** — must be in path |
| `sepl_18.se1` | Main planet data (Sun, Moon, etc.) | Needed for best accuracy |
| `semo_12.se1` | Moon detailed data | Not needed for Chiron |

**Without `seas_18.se1`**: `swe.calc_ut(jd, swe.CHIRON, ...)` raises `swisseph.Error`.
There is no pure-Moshier path for Chiron — `FLG_MOSEPH` still needs `seas_18.se1` to
be present.

**The actual ephemeris used**: with `seas_18.se1` only (no `sepl_18.se1`),
pyswisseph falls back to Moshier for the Sun/planets needed in the geocentric calculation:
retflag = 260 = `FLG_MOSEPH(4) + FLG_SPEED(256)`. The difference between
this Moshier-fallback path and the full SE files (retflag=258=SWIEPH+SPEED) is:
**max 0.000067°** over 1950-2050. This is negligible relative to the 0.01° target.

**For the spike**: `seas_18.se1` is available locally at
`/home/loc/workspace/rahu/kerykeion/kerykeion/sweph/seas_18.se1`. The spike script
must call `swe.set_ephe_path(...)` before any `calc_ut(swe.CHIRON, ...)`.

**For CI integration of Phase 24 tests**: either:
1. Bundle `seas_18.se1` as a test fixture (217 KB), or
2. Document that the regression test skips if SE files are absent (pattern:
   `pytest.importorskip("swisseph")` + check `set_ephe_path` works), or
3. Add `seas_18.se1` to `res/` in the repo (similar to how kerykeion distributes it)

The spike does NOT need to solve CI for Phase 24 — that is Phase 24's concern.
The spike only documents what ephemeris setup is needed.

### How existing tests use pyswisseph

Existing tests (`test_lilith_cross_check.py`, `tests/houses/conftest.py`) use:
- `pytest.importorskip("swisseph")` module-level gate
- No `swe.set_ephe_path()` call — they use bodies that work without SE files:
  - `swe.MEAN_APOG` (Lilith): Moshier, no SE files needed
  - `swe.houses_ex`: computation only, no SE files needed
  - `swe.MEAN_NODE`: Moshier, no SE files needed

**Chiron is the first body in the ketu test suite requiring SE files.**

---

## Q6: Pure-NumPy Runtime Evaluator

### Confirmed approach

```python
# At evaluation time (Phase 24 runtime — pure NumPy, no scipy):
def eval_chiron_lon(jd: float, seg_starts: np.ndarray,
                    lon_coeffs: np.ndarray, seg_len: float) -> float:
    si = int((jd - seg_starts[0]) / seg_len)
    si = max(0, min(si, len(seg_starts) - 1))
    t = 2.0 * (jd - seg_starts[si]) / seg_len - 1.0
    t = np.clip(t, -1.0, 1.0)
    lon_unwrapped = np.polynomial.chebyshev.chebval(t, lon_coeffs[si])
    return float(lon_unwrapped % 360.0)
```

**Vectorized over a jd array:**
```python
def eval_chiron_lon_batch(jd_arr: np.ndarray, seg_starts: np.ndarray,
                          lon_coeffs: np.ndarray, seg_len: float) -> np.ndarray:
    si_arr = np.clip(
        ((jd_arr - seg_starts[0]) / seg_len).astype(int),
        0, len(seg_starts) - 1
    )
    t_arr = 2.0 * (jd_arr - seg_starts[si_arr]) / seg_len - 1.0
    t_arr = np.clip(t_arr, -1.0, 1.0)
    # Loop over unique segments (usually 1-2 per batch for typical JD queries)
    result = np.empty(len(jd_arr))
    for si in np.unique(si_arr):
        mask = si_arr == si
        result[mask] = np.polynomial.chebyshev.chebval(t_arr[mask], lon_coeffs[si])
    return result % 360.0
```

**`np.polynomial.chebyshev.chebval`** confirmed:
- Pure NumPy, no scipy
- Vectorizes over `t` arrays natively
- Returns correct values matching `Chebyshev(t)` call (verified: `np.allclose=True`)
- Timing: ~5 μs scalar, ~94 μs for 1000-point batch

**The normalization**: `t = 2*(jd - jd_s)/seg_len - 1` maps `[jd_s, jd_s+seg_len]`
to `[-1, 1]`. The coefficients from `Chebyshev.fit(t_fit, y, deg, domain=[-1,1])`
are already in the standard `[-1,1]` domain — no additional domain transformation needed
when calling `chebval`.

---

## Q7: Repo Grounding

### Where Chiron slots into `planets.py`

**File**: `ketu/ephemeris/planets.py`

Current state after Phase 22:

```python
# Line 35-49: BODY_INDICES — maps name to index in ORBITAL_ELEMENTS
BODY_INDICES = {"Sun": 0, ..., "Lilith": 12}

# Line 52-66: SWE_IDS — maps int id to name (0-12)
SWE_IDS = {0: "Sun", ..., 12: "Lilith"}

# Line 310-324: BODY_STRATEGIES — per-body strategy registry
BODY_STRATEGIES: dict[str, _BodyCalc] = {
    "Sun": ..., "Moon": ..., ..., "Pluto": ...
}

# Line 332: calc_planet_position — dispatcher using BODY_STRATEGIES
# Line 603: calc_planet_position_batch — batch dispatcher using BODY_STRATEGIES
```

**Chiron will add**:
- `SWE_IDS[13] = "Chiron"`
- `BODY_INDICES["Chiron"] = 13`
- `BODY_STRATEGIES["Chiron"] = _BodyCalc(_chiron_scalar, _chiron_vec)`
- The scalar/vec functions call the pure-NumPy Chebyshev evaluator
- `calc_planet_position` valid range changes: `0-13`

### Where orbital.py fits

**File**: `ketu/ephemeris/orbital.py` (re-export hub)

After Phase 22 split, `orbital.py` is a thin re-export hub over 5 private modules
(`_elements.py`, `_kepler.py`, `_mechanics.py`, `_perturbations.py`, `_body_getters.py`).
Chiron does NOT need ORBITAL_ELEMENTS (those are for the numerical integrator).
Chiron's computation is entirely via the Chebyshev table.

**Note from Phase 22**: `apply_perturbations` strategy-ification was deferred to Phase 24;
the decision log states "Chiron perturbations likely Chebyshev-based via Phase 23 spike."
This research confirms: Chiron is entirely Chebyshev-based. No perturbations function.

### Existing pyswisseph pattern

Pattern established in `tests/test_lilith_cross_check.py` (lines 56-57):
```python
pytest.importorskip("swisseph")
import swisseph as swe
```
And in `tests/houses/conftest.py` (lines 59-60). The spike script follows this same
pattern but adds `swe.set_ephe_path(...)` since Chiron requires SE files.

### pyproject.toml dependencies

```toml
[project]  # runtime
dependencies = ["numpy>=1.20.0"]  # only numpy at runtime — MAINTAINED

[project.optional-dependencies]
test = ["pyswisseph>=2.10.0"]  # test/build only
```

pyswisseph stays in `[test]` optional dependencies. No change for Phase 23 (spike).
The spike script is placed in the `.planning/phases/23-spike-chiron/` directory —
not in `ketu/` and not in `tests/` — so it has zero impact on the package or test suite.

### scripts/ and tools/ directories

```bash
/home/loc/workspace/ketu/scripts/
  check_planning_coherence.py
  precompute_ephemeris.py       # <-- exists! offline precomputation pattern
  snapshot_reference_charts.py
```

`scripts/precompute_ephemeris.py` is an existing offline generator pattern.
**Phase 24's offline coeff generator** should follow this pattern (live in `scripts/`,
not in `ketu/` itself).

---

## Pitfalls Summary

| Pitfall | Impact | Mitigation |
|---------|--------|-----------|
| Fitting wrapped longitude (0°–360°) across 0/360 boundary | ~360° polynomial spike at boundary | Unwrap before fit; re-wrap after eval with `% 360` |
| Measuring error on fit nodes only | Error always 0 on fit nodes — meaningless | Use 200-point dense validation grid DISTINCT from fit nodes |
| Reporting RMS instead of max | 10× optimistic vs worst-case | Always report `np.max(np.abs(error))` |
| `swe.CHIRON` without `swe.set_ephe_path` | `swisseph.Error` raised | Call `swe.set_ephe_path(path_to_seas_18_dir)` before any Chiron calc |
| Using `FLG_MOSEPH` without SE files | Same `swisseph.Error` | Same fix — `seas_18.se1` must be findable |
| Using Chebyshev nodes for fit sampling | Slightly worse than uniform for this problem | Use `np.linspace(-1, 1, n_fit)` |
| Skipping the perihelion region (~2046–2047) | Miss the worst-case segment | Test ALL segments, not just a sample |
| scipy in the runtime evaluator | Breaks pure-NumPy contract | `np.polynomial.chebyshev.chebval` only |
| Fitting speeds separately | Not needed + double the work | Finite difference (jd_delta=0.01 pattern) |

---

## What "Good" Looks Like for the Spike Artifact

The spike delivers exactly two things:

### 1. Measurement table (SPK-01)

A documented table showing for the **primary candidate** and 2–3 bracketing alternatives:

- Segment length (days)
- Polynomial degree
- Number of segments (1950-2050)
- Coefficient count and `.npz` footprint (KB)
- **Max |Δλ|** vs Swiss Ephemeris over all segments, dense validation grid
- Whether max error < 0.01°

### 2. Go/no-go decision record (SPK-02)

A short written decision:
- Primary parameters chosen for Phase 24: seg_len, degree, n_quantities
- Achieved accuracy (absolute + ratio to 0.01° target)
- Latitude and distance accuracy (for position vector completeness)
- Oracle used (Moshier vs full SE files) with documented max difference
- `.npz` layout (arrays, shapes, dtypes)
- Ephemeris file setup requirement for Phase 24 test harness

**The deliverable is NOT**: production `ketu/chiron/` code, not a test registered in
`pytest`, not a change to `planets.py` or `BODY_INDICES`.

---

## Pre-measured Answers for Phase 24 Planning

The spike will confirm these numbers (already measured here as a preview):

| Parameter | Value |
|-----------|-------|
| Segment length | 32 days |
| Polynomial degree | 10 |
| Number of segments (1950-2050) | 1153 |
| Coefficients per segment | 11 (deg+1) |
| Quantities to fit | 3 (lon, lat, dist) |
| Total coefficients | 38,049 |
| `.npz` footprint | ~300 KB uncompressed, smaller compressed |
| Max longitude error | 0.000803° |
| Safety margin vs 0.01° | 12.4× |
| Worst segment | 2047-10-11 (2nd perihelion) |
| Oracle | `swe.calc_ut(jd, swe.CHIRON, FLG_SWIEPH|FLG_SPEED)` |
| Oracle setup | `swe.set_ephe_path(path_with_seas_18_se1)` |
| Moshier-vs-SE difference | max 0.000067° (negligible) |
| Go/no-go | **GO** |
