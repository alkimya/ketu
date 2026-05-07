# Phase 10: Houses Module - Research

**Researched:** 2026-05-07
**Domain:** Astrological house systems (Placidus, Koch, Porphyry) — coordinate conversion, iterative semi-arc trisection, vectorized NumPy
**Confidence:** HIGH (formulas, polar boundaries, dtype design, pyswisseph fixture API empirically verified)

> **Note on `<user_constraints>`:** No CONTEXT.md exists for this phase (`/gsd:discuss-phase` was not run). All requirements from ROADMAP.md (HOU-01 through HOU-10) are treated as locked specs.

---

## Summary

Phase 10 introduces a new `ketu/houses/` subpackage that computes Placidus and Koch house cusps over batched `(jd, lat, lon)` inputs, returning a `HOUSES_DTYPE` structured array. The math is well-documented (Meeus Ch.13, libephemeris reference, swisseph C source) and the iteration is short and convergent (≤10 iterations in practice for non-polar lats; the 50-iter cap from HOU-03 is a safety margin, not a typical value). The hardest engineering items are (a) **HOU-01 LST/obliquity precision audit** — empirically Ketu's GMST is ~12-16 arcsec off vs swisseph at J2000/1900, which propagates to **~25-32 arcsec ASC error** at mid-latitudes (still under 1-arcmin spec, but tight); (b) **HOU-08 vectorized iteration** — mask-based "compute only where not yet converged" pattern; (c) **HOU-06 polar safety** — `HighLatitudeError` default + Porphyry fallback as opt-in.

The cross-check oracle (`pyswisseph >= 2.10.3.6`, already wired test-only) returns **13-tuple cusps** (`cusps[0]=0.0` placeholder, `cusps[1..12]` are house cusps in degrees) and **8-tuple ascmc** (`ascmc[0]=ASC, [1]=MC, [2]=ARMC, [3]=Vertex, [4]=Equatorial Asc, [5]=Co-Asc Koch, [6]=Co-Asc Munkasey, [7]=Polar Asc`). Empirically, both Placidus 'P' and Koch 'K' raise `swisseph.Error` for lat > 66.56°; `houses_armc(armc, lat, eps, hsys)` is the right oracle if we want to isolate ARMC error from sidereal-time error during fixture authoring.

**Primary recommendation:** Phase 10 splits cleanly into 6 atomic plans driven by dependency order — (1) LST/obliquity audit & tighten, (2) pysweph oracle harness + fixture corpus, (3) registry + dtype + ASC/MC closed-form, (4) Placidus iteration vectorized, (5) Koch + Porphyry + polar safety, (6) integration & stub removal. Item (1) is the published blocker per state.md and must complete before (3).

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| numpy | >=1.20.0 (existing) | Structured arrays, vectorized iteration via boolean masks | The project's only runtime dep; HOU-08 vectorization is non-negotiable |
| pyswisseph (a.k.a. swisseph) | >=2.10.3.6 (existing test-only) | Cross-check oracle for HOU-09 reference fixtures | Already wired in `[project.optional-dependencies].test`; AGPL-safe (test-only); the de-facto authoritative implementation |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | (existing) | Test runner, fixtures, parametrization | Standard project tooling — extend `tests/houses/` |
| mypy --strict | (existing) | Type checking | Required gate; new `ketu/houses/*` listed in mypy overrides table when added |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Hand-rolled iteration in NumPy | scipy.optimize fixed-point | scipy is forbidden by the no-runtime-deps constraint; iteration here is trivially convergent in <10 steps without a heavyweight solver |
| Custom Placidus C extension | pure NumPy | Constraint says "no scipy/swisseph at runtime" — pure NumPy preserves the contract and is fast enough at chart-batch scale |
| `swisseph.houses_ex` for production | pure NumPy implementation | swisseph is AGPL — can only be a test oracle, never a runtime dep |

**Installation:** Already installed via existing `pip install -e ".[test]"`.

---

## Architecture Patterns

### Recommended Project Structure
```
ketu/houses/
├── __init__.py          # Public API: calculate_houses, house_of, HOUSES_DTYPE, HighLatitudeError, SYSTEMS
├── registry.py          # SYSTEMS dict + register() decorator + dispatch
├── core.py              # HOUSES_DTYPE definition, exception classes
├── ascmc.py             # ASC, MC, ARMC, Vertex closed-form (shared by all systems)
├── placidus.py          # Placidus iteration (vectorized, masked)
├── koch.py              # Koch iteration (vectorized, masked) - same shape as Placidus
├── porphyry.py          # Porphyry trisection (closed-form fallback)
└── _ecliptic.py         # RA <-> ecliptic-longitude helpers (shared math)

tests/houses/
├── __init__.py
├── conftest.py          # pyswisseph oracle helpers, parametrize fixtures
├── test_ascmc.py        # ASC/MC/ARMC/Vertex closed-form vs swe.houses_armc
├── test_placidus.py     # Reference fixtures + iteration cap behavior
├── test_koch.py
├── test_porphyry.py
├── test_registry.py     # Custom system registration test
├── test_polar_safety.py # HighLatitudeError + porphyry fallback + boundary at ±66.56°
├── test_dtype.py        # HOUSES_DTYPE shape semantics, vectorization
├── test_house_of.py     # house_of() for arbitrary planet_lon
└── fixtures/            # JSON or .npy reference fixtures (≥10 entries: city + polar lats 70°/80°)
```

### Pattern 1: Registry-based Dispatch (HOU-02)
**What:** Module-level `SYSTEMS` dict mapping single-letter code (lowercase) → callable returning cusps array.
**When to use:** Anytime you'd add an `if-elif` ladder for system names. Per HOU-02, dispatch must NOT live in `calculate_houses` — only in `SYSTEMS[system](...)`.

**Example:**
```python
# ketu/houses/registry.py
from typing import Callable, Dict
import numpy as np

# Signature: (armc: ndarray, lat: ndarray, eps: ndarray) -> ndarray of shape (..., 12)
HouseSystemFn = Callable[[np.ndarray, np.ndarray, np.ndarray], np.ndarray]

SYSTEMS: Dict[str, HouseSystemFn] = {}

def register(name: str) -> Callable[[HouseSystemFn], HouseSystemFn]:
    """Decorator to register a house system. New systems plug in without touching dispatch."""
    def _wrap(fn: HouseSystemFn) -> HouseSystemFn:
        SYSTEMS[name.lower()] = fn
        return fn
    return _wrap

# In ketu/houses/placidus.py:
# @register("placidus")
# def placidus_cusps(armc, lat, eps): ...
```

### Pattern 2: Vectorized Mask-Based Iteration (HOU-08)
**What:** Compute fixed-point updates only on elements that have not converged. Avoid `for jd in jds: while not converged:` (Python-loop antipattern).

**Example:** (Placidus diurnal-semi-arc fixed-point)
```python
def _placidus_cusp_iterate(
    armc: np.ndarray,        # shape (...,)
    lat: np.ndarray,          # shape (...,)
    eps: np.ndarray,          # shape (...,)
    H_target: float,          # 30 deg for cusp 11, 60 for cusp 12, etc.
    max_iter: int = 50,
    tol_deg: float = 1e-7,
) -> np.ndarray:
    """Vectorized Placidus cusp iteration. Returns RA of cusp (degrees)."""
    tan_lat = np.tan(np.deg2rad(lat))
    tan_eps = np.tan(np.deg2rad(eps))
    # initial guess: RA = ARMC + H_target (no AD correction)
    RA = (armc + H_target) % 360.0
    converged = np.zeros_like(RA, dtype=bool)
    for _ in range(max_iter):
        # 1. declination from RA on the ecliptic: tan(δ) = sin(RA) * tan(eps)
        sin_RA = np.sin(np.deg2rad(RA))
        tan_delta = sin_RA * tan_eps
        # 2. ascensional difference: AD = arcsin(tan(lat) * tan(delta))
        s = tan_lat * tan_delta
        # Polar guard: |s| > 1 means cusp does not exist at this lat
        polar_fail = np.abs(s) >= 1.0
        s_clipped = np.where(polar_fail, np.nan, s)
        AD = np.rad2deg(np.arcsin(s_clipped))
        # 3. update: RA_new = ARMC + H_scaled  (scaled by AD per cusp formula)
        RA_new = (armc + H_target * (1.0 + AD / 90.0)) % 360.0  # H formula varies by cusp; see Pitfalls
        delta = np.abs(((RA_new - RA + 180.0) % 360.0) - 180.0)
        newly_converged = delta < tol_deg
        # Only write back where not already converged AND not polar
        active = ~converged & ~polar_fail
        RA = np.where(active, RA_new, RA)
        converged = converged | newly_converged | polar_fail
        if converged.all():
            break
    # Mark non-converged + polar as NaN for caller to handle (HOU-06)
    not_done = ~converged
    RA = np.where(not_done, np.nan, RA)
    return RA
```

> ⚠ **The literal `H_target * (1.0 + AD / 90.0)` line is illustrative.** The actual per-cusp formulas are spelled out below in *Don't Hand-Roll → Placidus formula*. Do not paste this snippet verbatim.

### Pattern 3: Structured Array with Sub-array Fields (HOU-05)
**What:** Use NumPy's tuple-form `(name, dtype, shape)` to embed `cusps[12]` as a sub-array field. Field shape is appended to outer shape during access.

**Example:**
```python
# ketu/houses/core.py
import numpy as np

HOUSES_DTYPE = np.dtype([
    ("jd",      "f8"),               # input Julian date (UT)
    ("lat",     "f8"),               # geographic latitude (deg)
    ("lon",     "f8"),               # geographic longitude (deg)
    ("system",  "U10"),              # house system name (e.g. "placidus")
    ("cusps",   "f8", (12,)),        # 12 cusps in ecliptic longitude (deg, [0, 360))
    ("asc",     "f8"),               # Ascendant
    ("mc",      "f8"),               # Medium Coeli
    ("armc",    "f8"),               # Right Ascension of MC (= LST in degrees)
    ("vertex",  "f8"),               # Vertex (intersection of ecliptic & prime vertical)
])

# Vectorized: input shape (N,) → output shape (N,) with cusps field shape (N, 12)
# arr["cusps"][i, j] is house j+1 cusp for date i
# arr["cusps"].shape == (N, 12) for outer shape (N,)
```

### Anti-Patterns to Avoid
- **`if hsys == "placidus": ... elif hsys == "koch": ...` ladder.** HOU-02 requires registry dispatch; embedding `if/elif` in `calculate_houses` defeats the extensibility goal.
- **Python-level `for jd in jds:` loop around scalar Placidus.** Violates HOU-08 vectorization; Kala will batch over decades of dates.
- **Returning silent NaN at polar lats by default.** HOU-06 forbids this — default must `raise HighLatitudeError`.
- **`cusps[0] = ASC`** (1-indexed C convention from swisseph). For idiomatic NumPy, use 0-indexed: `cusps[0]` is house 1 cusp = ASC, `cusps[6]` is house 7 cusp = DESC. The pyswisseph 13-tuple oracle is 1-indexed; convert at the test boundary, not in the module.
- **Reusing `calc_planet_position`'s `lru_cache`.** House calculations are parameterized over (jd, lat, lon, system) — different cache key shape. Don't piggyback on the planet cache.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Reference fixture data | Hand-typed cusps from astro.com web UI | Programmatic `swe.houses_ex(jd, lat, lon, b'P')` calls in conftest, snapshot to JSON | Eliminates copy-paste errors; reproducible; lets the test re-snapshot on demand |
| ASC/MC formulas | Single-arg `arctan` with manual quadrant fix | `np.arctan2(sin_armc, cos_armc * cos_eps)` | atan2 places result in correct quadrant automatically; RadixPro warns the single-arg form needs `+180` bumps in 50% of cases |
| Polar boundary check | `if abs(lat) > 66.56` (literal) | `eps_today = mean_obliquity(jd); polar_lat = 90.0 - eps_today` | Obliquity drifts ~50″/yr; using current obliquity gives the *true* polar circle (e.g. 66.5604° in 2026 vs 66.5594° in 2050) |
| Convergence criterion | `abs(RA_new - RA) < tol` | `abs(((RA_new - RA + 180) % 360) - 180) < tol` | Plain subtraction breaks across the 359°→0° wrap; modular form handles the seam |
| Iteration termination | Track per-element iteration count manually | `for _ in range(max_iter): if converged.all(): break` + flag remaining as NaN | Idiomatic, single-pass, no per-element bookkeeping |

**Placidus formula (use, do not re-derive):**

For a target hour-angle fraction H (cusp 11: H=30°; cusp 12: H=60°; cusp 2: H=120°; cusp 3: H=150°), Placidus solves:
```
sin(RA - ARMC) * tan(lat) * tan(eps) * sin(RA)  =  sin(H * sign)
```
The libephemeris reference and Meeus Ch.13 give the canonical fixed-point form:
```
1. tan(δ) = sin(RA) * tan(eps)
2. AD = arcsin(tan(lat) * tan(δ))            ← Ascensional Difference
3. RA_new = ARMC + (H / (90° + AD))*90°       ← scaled trisection of semi-arc
4. iterate (2)-(3) until |Δ RA| < 1e-7°
```
Note: the per-cusp scaling factor differs for upper (cusps 11/12) vs lower (cusps 2/3) semi-arcs and for southern-hemisphere mirror. Use the libephemeris cusp-equation table verbatim:
- House 11: `RA_11 = ARMC + (90° + AD) / 3`
- House 12: `RA_12 = ARMC + 2(90° + AD) / 3`
- House 2 : `RA_2  = ARMC + 180° - 2(90° - AD) / 3`
- House 3 : `RA_3  = ARMC + 180° -  (90° - AD) / 3`

Cusps 1, 4, 7, 10 are closed-form (ASC, IC=ASC+180°, DESC=ASC+180°, MC) — do not iterate them. Cusps 5, 6, 8, 9 are derived as opposites: H5=H11+180°, H6=H12+180°, H8=H2+180°, H9=H3+180°.

**Koch formula:**

Same iteration shape as Placidus but trisects **oblique ascension** (OA = RA - AD) at the meridian rather than the semi-arc:
- OA_11 = OA_MC + (OA_Asc - OA_MC) / 3
- OA_12 = OA_MC + 2*(OA_Asc - OA_MC) / 3
- (similar for cusps 2, 3 from OA_Asc to OA_IC)

The fixed-point inversion `OA → RA` uses the same `AD = arcsin(tan(lat)*tan(δ))` step, then `λ = atan2(sin(RA), cos(RA)*cos(eps))`.

**Porphyry formula (closed-form, used as polar fallback):**
```
step_upper = ((asc - mc) mod 360) / 3
cusp_11 = mc + step_upper
cusp_12 = mc + 2 * step_upper
step_lower = ((ic - asc) mod 360) / 3      # ic = (mc + 180) mod 360
cusp_2 = asc + step_lower
cusp_3 = asc + 2 * step_lower
# cusps 5, 6, 8, 9 = opposites
```
No iteration, no polar failure mode (works at all latitudes including 90°).

**ASC closed-form:**
```python
# Robust atan2 form (RadixPro + swisseph C source agree)
asc_rad = np.arctan2(
    np.cos(np.deg2rad(armc)),
    -(np.sin(np.deg2rad(eps)) * np.tan(np.deg2rad(lat))
      + np.cos(np.deg2rad(eps)) * np.sin(np.deg2rad(armc)))
)
asc_deg = np.rad2deg(asc_rad) % 360.0
# Disambiguate hemisphere: ASC must be > MC by ~90° going east; if not, add 180.
# Robust check: use (asc - mc) mod 360 should be ~90° for non-polar charts.
```

**MC closed-form:**
```python
mc_rad = np.arctan2(
    np.sin(np.deg2rad(armc)),
    np.cos(np.deg2rad(armc)) * np.cos(np.deg2rad(eps))
)
mc_deg = np.rad2deg(mc_rad) % 360.0
# Quadrant disambiguation: if armc in [180, 360), mc should be in [180, 360).
mc_deg = np.where((armc >= 180.0) & (mc_deg < 180.0), mc_deg + 180.0, mc_deg) % 360.0
mc_deg = np.where((armc < 180.0) & (mc_deg >= 180.0), mc_deg - 180.0, mc_deg) % 360.0
```

**Key insight:** swisseph's `swehouse.c` (visible in pd-swisseph mirror) explicitly uses Porphyry as the in-process polar fallback for Koch (`strcpy(hsp->serr, "within polar circle, switched to Porphyry")`). At the Python binding level, however, **pyswisseph 2.10+ raises `swisseph.Error` rather than returning Porphyry data** — verified empirically (lat=75°, jd=J2000: both 'P' and 'K' raise). HOU-06's spec matches this: raise by default, opt in to Porphyry via `polar_fallback="porphyry"`.

---

## Common Pitfalls

### Pitfall 1: GMST Precision Mismatch (HOU-01)
**What goes wrong:** `ketu.ephemeris.time.sidereal_time()` uses the IAU 1982/USNO formula (constant 280.46061837). Empirically off by **+12.77 arcsec at J2000** and **−16.28 arcsec at 1900-01-01** vs `swe.sidtime`. ASC error is ~2× GMST error at lat ≈ 49° ⇒ ~25-32 arcsec ASC error from this source alone.
**Why it happens:** The current formula does not include the IAU 2000A precession-rate correction. Modern IERS/IAU 2006 GMST uses the polynomial `GMST(0h UT1) = 24110.54841 + 8640184.812866·T + ...` plus the equation of the equinoxes for GAST.
**How to avoid:**
- Tighten `sidereal_time` to the IAU 2006 form (see Meeus 2nd ed. eq. 12.4) **before** building Placidus/Koch on top of it.
- Provide a `tests/houses/test_lst_obliquity_precision.py` that asserts `<1 arcsec` agreement with `swe.sidtime` over the 1900-2100 range.
- Decouple: also expose `houses_armc(armc, lat, eps, system)` so fixture authoring can isolate ARMC source from algorithm bugs.
**Warning signs:** Hand-validated chart shows ASC drift of >30 arcsec from astro.com on a date >50 years from J2000.

### Pitfall 2: Single-arg `arctan` Quadrant Errors
**What goes wrong:** `arctan(y/x)` returns in `[-π/2, +π/2]`, missing the back-hemisphere half. RadixPro's tutorial explicitly warns "you will not always get a result in the correct quadrant; if required add or subtract 180°."
**Why it happens:** Wrap-around: ARMC=200° gives `tan(L) = sin(200)/[cos(200)·cos(eps)]` which has the same value as ARMC=20° but the answer must be in the third quadrant.
**How to avoid:** Always use `np.arctan2(y, x)`. For ASC, the canonical form is `atan2(cos(ARMC), -[sin(eps)·tan(lat) + cos(eps)·sin(ARMC)])`.
**Warning signs:** ASC sign-flips by 180° around ARMC=180° (passes-the-meridian test).

### Pitfall 3: Naive `RA_new − RA` Convergence Check
**What goes wrong:** When RA approaches 360°, the next iteration may land at 0.0001° — `abs(0.0001 - 359.9999) = 359.9998` flags as not-converged forever.
**Why it happens:** Modular arithmetic seam at 0°/360°.
**How to avoid:** `delta = abs(((RA_new - RA + 180) % 360) - 180)`. This maps the difference to `[0, 180]` correctly.
**Warning signs:** Test with `armc ≈ 359°` never converges; iteration count hits cap.

### Pitfall 4: Hard-coded Polar Boundary (66.56°)
**What goes wrong:** Obliquity drifts ~50″ per year. Using `if abs(lat) > 66.56` is wrong by up to ~1' over a 100-year span; failure modes include "ASC computes but quadrant is mis-assigned."
**Why it happens:** True polar circle = 90° − ε(jd), not a constant.
**How to avoid:** `polar_lat = 90.0 - mean_obliquity(jd)`; check `np.abs(lat) > polar_lat`. For HOU-09 fixtures specify both lat=70° (definitely polar) and lat=80° (deeply polar).
**Warning signs:** `pytest tests/houses/test_polar_safety.py` flickers (passes one day, fails another) — usually means using a `datetime.utcnow()`-derived obliquity in test setup.

### Pitfall 5: ARMC vs LST Confusion
**What goes wrong:** Some sources call this "RAMC", "ARMC", or "sidereal time in degrees" interchangeably. The unit is the same (degrees), but the *time system* matters.
**Why it happens:** ARMC = GMST + observer_longitude_east. The "ARMC" returned by `swe.houses_ex` is **already** corrected for observer longitude (it's local), while `swe.sidtime(jd)` returns Greenwich sidereal time in **hours**.
**How to avoid:**
- Internally name it `armc` (degrees, includes longitude).
- Document: `armc = (sidereal_time(jd, 0.0) + lon) % 360.0` where lon is east-positive.
- When using `swe.houses_armc` as oracle, feed your computed armc; when using `swe.houses_ex`, swisseph computes its own armc internally.
**Warning signs:** Tests pass at lon=0° but fail at lon=90°E.

### Pitfall 6: Placidus False-positive Convergence at Polar Edge
**What goes wrong:** Approaching ±66.56°, the iteration `tan(lat)·tan(δ)` flirts with 1.0. Iteration may "converge" to a degenerate root where AD ≈ 90°, meaning the cusp is at the meridian — physically wrong.
**Why it happens:** `arcsin` saturates to π/2 silently when its argument is just under 1.
**How to avoid:**
- Pre-check `tan_lat * tan_eps` and reject when `|s| ≥ 1` (clip to NaN, route to fallback).
- Cross-validate against swisseph's pol-circle behaviour at lat=66.56° vs 66.57° (last working / first failing in our empirical test).
**Warning signs:** Cusps 11 and 12 collapse to within 1° of MC at lat=66.5°.

### Pitfall 7: pyswisseph Tuple Indexing Surprise (HOU-09 fixture authoring)
**What goes wrong:** `swe.houses_ex(jd, lat, lon, b'P')` returns `(cusps, ascmc)`. **`cusps` is a 13-tuple where `cusps[0] = 0.0`** (placeholder; the C library uses 1-indexed houses). Iterating `for c in cusps` gives 13 values, not 12.
**Why it happens:** pyswisseph 2.10.3.4 changed the return format from 12-tuple to 13-tuple to match the C convention.
**How to avoid:** In conftest helpers, always slice: `cusps_swe = swe.houses_ex(...)[0][1:13]`. Treat this as a test-only conversion at the oracle boundary; the Ketu module exposes 0-indexed 12-element arrays.
**Warning signs:** Off-by-one ASC equality failures (test compares Ketu's house-1 cusp to swisseph's `cusps[0]=0.0`).

### Pitfall 8: hsys Bytes vs String Confusion (test fixtures)
**What goes wrong:** `swe.houses_ex(jd, lat, lon, "P")` (str) silently fails or raises in some pyswisseph versions; only `b"P"` (bytes) is universally accepted.
**Why it happens:** The C API takes `char` (1 byte), and the Python binding's PyArg parser is strict about bytes.
**How to avoid:** Use `b"P"`, `b"K"`, `b"O"` in fixture code. The Ketu public API takes str (`system="placidus"`) — only the test oracle layer uses bytes.

### Pitfall 9: Mypy --strict + np.ndarray Type Variance
**What goes wrong:** `def calculate_houses(jd: np.ndarray, ...)` passes scalar `float` and silently broadcasts. Mypy --strict (project-wide gate) flags this.
**Why it happens:** Project-wide pattern (used by `cycles`, `aspects`) is `Union[float, np.ndarray]` for inputs, with `np.atleast_1d()` normalization at entry.
**How to avoid:** Mirror the pattern in `aspects/calculator.py` — accept `Union[float, np.ndarray]`, normalize, preserve scalar-output for scalar-input.

---

## Code Examples

### Example 1: Public API surface (HOU-02, HOU-05, HOU-06, HOU-07)
```python
# ketu/houses/__init__.py
"""House system calculations.

>>> from ketu.houses import calculate_houses, house_of, HOUSES_DTYPE
>>> result = calculate_houses(2451545.0, 48.8566, 2.3522, system="placidus")
>>> result["asc"], result["mc"]
(26.77..., 281.78...)
>>> house_of(planet_lon=45.0, cusps=result["cusps"])
2  # 45° lies in house 2
"""

from .core import HOUSES_DTYPE, HighLatitudeError
from .registry import SYSTEMS
from .api import calculate_houses, house_of

__all__ = [
    "HOUSES_DTYPE",
    "HighLatitudeError",
    "SYSTEMS",
    "calculate_houses",
    "house_of",
]
```

```python
# ketu/houses/core.py
import numpy as np

HOUSES_DTYPE = np.dtype([
    ("jd", "f8"), ("lat", "f8"), ("lon", "f8"),
    ("system", "U10"),
    ("cusps", "f8", (12,)),
    ("asc", "f8"), ("mc", "f8"), ("armc", "f8"), ("vertex", "f8"),
])


class HighLatitudeError(ValueError):
    """Raised when |lat| exceeds the polar circle for the requested house system."""

    def __init__(self, lat: float, system: str, polar_lat: float):
        super().__init__(
            f"latitude {lat:.4f}° exceeds polar circle {polar_lat:.4f}° "
            f"for house system {system!r}; pass polar_fallback='porphyry' to fall back."
        )
        self.lat = lat
        self.system = system
        self.polar_lat = polar_lat
```

### Example 2: `house_of` helper (HOU-07)
```python
# ketu/houses/api.py (excerpt)
def house_of(planet_lon: np.ndarray, cusps: np.ndarray) -> np.ndarray:
    """Return the 1-indexed house number containing each planet longitude.

    Parameters
    ----------
    planet_lon : float or np.ndarray  (degrees, [0, 360))
    cusps : np.ndarray of shape (12,) or (..., 12)
        cusps[i] is the cusp of house (i+1).

    Returns
    -------
    np.ndarray of int (1..12), same broadcast shape as planet_lon.
    """
    planet_lon = np.asarray(planet_lon) % 360.0
    cusps = np.asarray(cusps)  # shape (..., 12)
    # For each planet_lon p, find largest i such that ((p - cusps[i]) mod 360) < 30 effective span.
    # Robust: compute mod-360 distance from each cusp; house i+1 spans [cusps[i], cusps[(i+1)%12]).
    # Equivalent vectorized form using broadcasting:
    diffs = (planet_lon[..., None] - cusps + 360.0) % 360.0  # shape (..., 12)
    next_cusp = np.roll(cusps, -1, axis=-1)
    spans = (next_cusp - cusps + 360.0) % 360.0  # shape (..., 12)
    # planet is in house i+1 iff diffs[..., i] < spans[..., i]
    in_house = diffs < spans  # shape (..., 12); exactly one True per row in non-degenerate cases
    house_idx = np.argmax(in_house, axis=-1)  # 0..11
    return (house_idx + 1).astype(np.int32)
```

### Example 3: pyswisseph oracle harness (HOU-09)
```python
# tests/houses/conftest.py
import json
from pathlib import Path
import pytest
import numpy as np

try:
    import swisseph as swe
    SWE_AVAILABLE = True
except ImportError:
    SWE_AVAILABLE = False


SYSTEM_BYTES = {"placidus": b"P", "koch": b"K", "porphyry": b"O"}


def swe_oracle(jd: float, lat: float, lon: float, system: str) -> dict:
    """Reference values from swisseph for cross-checking."""
    cusps_t, ascmc = swe.houses_ex(jd, lat, lon, SYSTEM_BYTES[system])
    return {
        "cusps": np.asarray(cusps_t[1:13]),  # convert 1-indexed → 0-indexed
        "asc": ascmc[0],
        "mc": ascmc[1],
        "armc": ascmc[2],
        "vertex": ascmc[3],
    }


@pytest.fixture(scope="session")
def reference_charts():
    """≥10 reference charts spanning normal & polar latitudes."""
    return [
        # (label, jd, lat, lon)
        ("J2000_Greenwich", 2451545.0, 51.4779, 0.0),
        ("J2000_Paris",     2451545.0, 48.8566, 2.3522),
        ("J2000_Sydney",    2451545.0, -33.8688, 151.2093),
        ("J2000_Tokyo",     2451545.0, 35.6762, 139.6503),
        ("J2000_Buenos_Aires", 2451545.0, -34.6037, -58.3816),
        ("1900_NewYork",    2415020.5, 40.7128, -74.0060),
        ("2050_Reykjavik",  2470204.0, 64.1466, -21.9426),
        ("J2000_Equator",   2451545.0, 0.0, 0.0),
        # Polar (HOU-09 explicit)
        ("J2000_lat70",     2451545.0, 70.0, 0.0),
        ("J2000_lat80",     2451545.0, 80.0, 0.0),
    ]


pytestmark_swe = pytest.mark.skipif(not SWE_AVAILABLE, reason="pyswisseph not installed")
```

### Example 4: Vectorized iteration with mask continuation (HOU-08)
```python
def _iterate_to_convergence(
    f_step,                      # callable(RA, *args) -> RA_new (vectorized)
    RA_init: np.ndarray,
    *args,
    max_iter: int = 50,
    tol_deg: float = 1e-7,
):
    """Generic mask-based fixed-point iteration. Returns (RA, converged_mask, iter_count)."""
    RA = RA_init.copy()
    converged = np.zeros_like(RA, dtype=bool)
    iter_used = np.zeros_like(RA, dtype=np.int32)
    for k in range(1, max_iter + 1):
        active = ~converged
        if not active.any():
            break
        RA_new = f_step(RA, *args)
        # Modular distance, handling 0/360 wrap
        delta = np.abs(((RA_new - RA + 180.0) % 360.0) - 180.0)
        # Update only active elements
        RA = np.where(active, RA_new, RA)
        # Newly converged
        newly_done = active & (delta < tol_deg)
        converged = converged | newly_done
        iter_used = np.where(newly_done, k, iter_used)
    return RA, converged, iter_used
```

### Example 5: Empirical baseline (HOU-01 audit reference values)
Run from `venv/bin/activate` Python:
```python
# Empirical: 2026-05-07 measurement
# Source: ketu sidereal_time vs swe.sidtime
#   J2000.0       :  +12.765 arcsec
#   2024-06-21 0h :   +3.326 arcsec
#   1900-01-01 0h :  -16.277 arcsec
#   2050-12-31 12h:   -8.827 arcsec
# Source: ketu mean_obliquity vs swe.calc_ut(SE_ECL_NUT)
#   All four dates: ±0.05 arcsec   ← already excellent, no tightening needed
#
# Sensitivity test (Paris lat=48.86, J2000):
#   GMST error +12.77″ → ASC error +24.96″
#   Multiplier: ~1.95x at this latitude (varies with lat, ~1/cos(lat) near equator)
#
# Spec target: <60″ ASC error (1 arcmin from HOU-01)
# Worst case ketu today: 16.28″ * ~2 ≈ 32.6″   ← inside spec at lat ~49°
# Polar lat=66°: multiplier ~2.5 → 16.28″ * 2.5 ≈ 40.7″   ← still inside spec
# Verdict: GMST tightening is RECOMMENDED but not strictly required to pass HOU-01.
#          Tightening to IAU 2006 polynomial (Meeus 12.4) drops error to <1″.
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `tan(L) = sin(ARMC) / (cos(ARMC) cos(eps))` w/ manual quadrant fix | `np.arctan2(...)` form | NumPy ≥1.0 (2006) | Eliminates 50%-of-the-time `+180°` correction; mandatory for vectorized code |
| 12-tuple `cusps` returned by `swe.houses_ex` | 13-tuple with `cusps[0]=0` placeholder | pyswisseph 2.10.3.4 (2024) | Test fixtures must slice `[1:13]`; Ketu internal arrays remain 0-indexed |
| Equal-house stub returning `(asc + i*30) % 360` | Real Placidus / Koch via registry | Phase 10 (this) | Removes the broken `calculate_house_cusps` from `ephemeris/planets.py` (HOU-10) |
| IAU 1976 obliquity (in current ketu code, formally) | IAU 2006 obliquity (Meeus 22.3) | IAU resolution 2006 | Sub-arcsecond precision; ketu's current formula is already IAU 2006-class (~0.05″ error) |
| IAU 1982 GMST (current ketu code: `280.46061837 + ...`) | IAU 2006 GMST (Meeus 12.4) | IERS conventions 2003/2010 | Ketu currently has up to 16″ GMST error at 1900; tighten to <1″ to comfortably exceed HOU-01 spec |

**Deprecated/outdated:**
- `cusps` returned as 12-tuple by pyswisseph: replaced by 13-tuple in 2.10.3.4. Ketu's pinned `>=2.10.3.6` is fine; just remember the [1:13] slice in fixtures.
- The single-argument `atan` formula in older pre-1990s astrology textbooks: superseded by `atan2` everywhere.

---

## Open Questions

1. **Is GMST tightening blocking, or "nice to have"?**
   - What we know: empirical worst case (1900) gives ~32 arcsec ASC error at lat=49°, well under the 1-arcmin spec.
   - What's unclear: At the polar boundary (lat=66°), multiplier rises and we may exceed spec for pre-1900 dates.
   - Recommendation: Treat HOU-01 as **a real audit task** — measure-then-decide. Tighten to IAU 2006 if any test fixture exceeds 30 arcsec ASC error vs swisseph; otherwise accept current precision and document. Plan 1 owns this decision.

2. **Should `house_of` accept a precomputed structured array or just the cusps field?**
   - What we know: HOU-07 spec is `house_of(planet_lon, cusps) -> int`.
   - What's unclear: Whether overload to also accept `HOUSES_DTYPE` row is desired.
   - Recommendation: Implement the spec literally (cusps array). Document a one-liner in the docstring: `house_of(p, result["cusps"])`. Don't overload.

3. **Vertex computation — closed-form or via swisseph cross-check only?**
   - What we know: Vertex = ecliptic point west of horizon at celestial equator's intersection with prime vertical. Closed form: `arctan2(cos(armc), -[sin(eps)*tan(complementary_lat) + cos(eps)*sin(armc)])` (i.e., ASC formula with `lat → 90° - lat`).
   - What's unclear: Whether Phase 10 needs Vertex precision to <1 arcmin like ASC, or whether it's a "best-effort" output field.
   - Recommendation: Implement closed-form, test against swisseph `ascmc[3]`. If it agrees to <1 arcmin, ship; otherwise document as "advisory" in dtype docstring.

4. **What does `polar_fallback="porphyry"` do at *exactly* lat=66.56°?**
   - What we know: Empirically pyswisseph works at 66.56° and fails at 66.57°. The math fails when `|tan(lat)*tan(eps)| ≥ 1` exactly.
   - What's unclear: Boundary handling — does `polar_fallback="porphyry"` ever trigger at 66.56°, or only strictly above?
   - Recommendation: Trigger fallback when `|s| > 1.0 - eps_tol` where `eps_tol=1e-9`, with `s = tan(lat)*tan(delta)`. Document the precise boundary in `HighLatitudeError.__doc__`.

5. **Cache key for `calculate_houses` — does it need one?**
   - What we know: The cache "configuration hashes" cross-cutting constraint mentions house system. There is no current `houses_cache.py`.
   - What's unclear: Whether the planner intends a houses cache or just notes the constraint for future work.
   - Recommendation: Don't build a cache in Phase 10. Document the cache-key shape `(jd, lat, lon, system)` in the plan and defer caching to a hypothetical Phase 12+ if profiling justifies it. Caching adds 200+ LoC and tests that aren't in the spec.

---

## Plan Decomposition Suggestions (planner reads, decides)

The following 6-plan decomposition follows dependency order and matches the 6-task convention used in Phase 9. Each plan is independently testable and gates the next.

| # | Plan | Owns | Depends on | Why this slice |
|---|------|------|-----------|----------------|
| 1 | **LST/obliquity audit & tighten** (HOU-01) | `ephemeris/time.py` GMST hardening, new `tests/houses/test_lst_obliquity_precision.py`, decision doc on whether tightening is needed | Nothing | **STATE.MD blocker** — must close before any Placidus work; landing it as Plan 1 unblocks all downstream |
| 2 | **Oracle harness + reference fixtures** (HOU-09 partial) | `tests/houses/conftest.py` with `swe_oracle()` helper, `reference_charts` fixture (≥10 entries incl. 70°/80°), JSON snapshot file | Plan 1 | Test infra must exist before TDD-style algorithm implementation; fixtures decouple algorithm from oracle availability |
| 3 | **Registry + dtype + ASC/MC closed-form** (HOU-02, HOU-05 partial) | `ketu/houses/{__init__,core,registry,ascmc}.py`, `tests/houses/test_ascmc.py`, `test_registry.py`, `test_dtype.py` | Plan 1, 2 | Closed-form ASC/MC has no iteration; provides scaffold (registry, dtype, exception class) for the iterative systems |
| 4 | **Placidus implementation + vectorized iteration** (HOU-03, HOU-08) | `ketu/houses/placidus.py`, `_ecliptic.py` helpers, `tests/houses/test_placidus.py` (incl. iteration cap & non-convergence test), parametrized over reference_charts (non-polar) | Plan 3 | Most complex algorithm; benefits from infra being solid |
| 5 | **Koch + Porphyry + polar safety** (HOU-04, HOU-06) | `ketu/houses/{koch,porphyry}.py`, `tests/houses/{test_koch,test_porphyry,test_polar_safety}.py`, `polar_fallback` param wiring | Plan 4 | Koch reuses Plan 4's iteration shape; Porphyry is the polar fallback so they ship together |
| 6 | **Stub removal + integration + house_of** (HOU-07, HOU-10) | Delete `calculate_house_cusps` from `ephemeris/planets.py`, update `ephemeris/__init__.py` exports, add `ketu/__init__.py` re-export, `house_of()` helper, `tests/houses/test_house_of.py`, `tests/houses/test_integration.py` end-to-end smoke, coverage gate verification (≥95%) | Plans 3, 4, 5 | Integration last; coverage check is the closing gate |

> **Note for planner:** Plan 4 + Plan 5 could merge if Koch + Porphyry feel small. Recommend keeping them split — Koch + polar-safety together is ~250 LoC of algorithm + tests, comfortable single-plan.

---

## Sources

### Primary (HIGH confidence)
- **pyswisseph 2.10+ Python binding** — empirical verification of API surface, 13-tuple cusps format, polar Error-raising behavior. Run from `venv/bin/activate`:
  - `swe.houses_ex(jd, lat, lon, b'P')` → `(cusps_13_tuple, ascmc_8_tuple)`
  - `swe.houses_armc(armc_deg, lat, eps_deg, b'P')` → same shape
  - `swe.sidtime(jd)` → GMST in **hours**
  - `swe.calc_ut(jd, swe.ECL_NUT)` → tuple with `coords[1] = mean obliquity in degrees`
- **swephR Section 13** (R wrapper, identical C API): https://rstub.github.io/swephR/reference/Section13.html — confirmed ascmc semantics: `[1]=ASC, [2]=MC, [3]=ARMC, [4]=Vertex, [5]=Equatorial Asc, [6]=Co-Asc Koch, [7]=Co-Asc Munkasey, [8]=Polar Asc`. (R is 1-indexed; Python equivalents are at index n-1.)
- **libephemeris house-systems reference**: https://github.com/g-battaglia/libephemeris/blob/main/docs/reference/house-systems.md — explicit per-cusp Placidus and Koch equations with iteration formula and convergence threshold (1e-7°).
- **pd-swisseph swehouse.c mirror** (canonical C source): https://github.com/jwmatthys/pd-swisseph/blob/master/swehouse.c — verified Koch's `if (fabs(fi) >= 90 - ekl)` polar test and Porphyry fallback `goto porphyry` (in C; Python binding raises instead).
- **NumPy 2.4 structured arrays**: https://numpy.org/doc/stable/user/basics.rec.html — confirmed `dtype([('cusps', 'f8', (12,))])` field-shape semantics: outer shape (N,) → field shape (N, 12).
- **Ketu v1.1 source** (this repo, gsd/v1.1-milestone branch):
  - `ketu/ephemeris/time.py:305-336` — current `sidereal_time()` (IAU 1982 form)
  - `ketu/ephemeris/coordinates.py:283-313` — current `mean_obliquity()` (IAU 2006 form, Meeus 22.3)
  - `ketu/ephemeris/planets.py:273-311` — broken `calculate_house_cusps()` stub to be removed (HOU-10)
  - `pyproject.toml:42-44` — `[project.optional-dependencies].test = ["pysweph>=2.10.3.6"]`
  - `tests/test_planets_coverage.py:186-269` — existing equal-house tests of the stub (will be removed in Plan 6)

### Secondary (MEDIUM confidence)
- **RadixPro - Ascendant**: https://radixpro.com/a4a-start/the-ascendant/ — confirms the Ascendant atan2 formula `atan2(cos ARMC, −[sin E·tan GL + cos E·sin ARMC])` with quadrant correction. Cites Dean & Mather (1977), Kampherbeek (1980).
- **RadixPro - Medium Coeli**: https://radixpro.com/a4a-start/medium-coeli/ — `atan2(sin ARMC, cos ARMC · cos E)`.
- **Skyscript - Placidus & Semi-Arc Method (Wackford)**: https://www.skyscript.co.uk/placido.html — historical context for the trisection-of-semi-arc principle; warns that intermediate cusps are not closed-form.
- **Astrodienst Astrowiki - Placidus**: https://www.astro.com/astrowiki/en/Placidus_House_System (placeholder content fetched; behavior consistent with other sources).
- **Astrodienst polar-region note**: https://www.astro.com/astrology/in_polar_asc_e.htm (referenced; full content blocked by browser-check page). Cross-confirmed via secondary search results: Placidus/Koch fail beyond polar circle; Porphyry/Whole Sign work everywhere.
- **Meeus *Astronomical Algorithms* 2nd ed.** (1998), Ch. 12 (sidereal time), Ch. 13 (house systems), Ch. 22 (obliquity) — referenced by libephemeris and skyscript; not directly fetched but multiple sources triangulate to the same formulas.

### Tertiary (LOW confidence — flagged for validation by planner/implementer)
- **Astrolog 7.80 sinusoidal house systems** (https://www.astrolog.org/astrolog/astsine.htm) — has alternative formulations not relevant to Phase 10 scope; mentioned only as reference for "what we are NOT implementing."
- **Various blog posts** (Cafe Astrology, AstroChartus, AstroSeek) — consumer-facing house-system explanations, used for narrative context only. Algorithms must come from libephemeris / Meeus / swisseph C source.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — pyswisseph already in `[test]` extras; numpy is the only runtime dep, no choice to make.
- Architecture: HIGH — registry + dtype + dispatch pattern verified against existing `ketu.aspects` registry-shape. Subarray field semantics empirically reproduced.
- Algorithm formulas (Placidus, Koch, Porphyry, ASC, MC): HIGH — libephemeris + pd-swisseph C source + RadixPro triangulate the same equations; pyswisseph oracle reproducible.
- Polar boundary: HIGH — verified empirically (66.56° works, 66.57° raises) at one date; the formula `90° − ε(jd)` is HIGH confidence (textbook); the exact tolerance for `polar_fallback="porphyry"` triggering is MEDIUM (Open Question 4).
- HOU-01 audit: MEDIUM — empirical numbers measured for 4 dates; whether tightening is *required* depends on the planner's spec interpretation. Recommendation given.
- Pitfalls: HIGH — most pitfalls reproduced empirically (tuple format, polar boundary, lat=75° error); `arctan2` quadrant trap is well-documented.

**Research date:** 2026-05-07
**Valid until:** 2026-08-07 (3 months — house-system math is centuries-stable; only pyswisseph API contract risks drift)
