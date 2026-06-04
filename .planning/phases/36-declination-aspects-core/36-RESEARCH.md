# Phase 36: Declination Aspects Core — Research

**Researched:** 2026-06-04
**Domain:** Pure-NumPy declination aspect detection sub-package (ketu/declination/)
**Confidence:** HIGH — all findings sourced from direct codebase reads

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- New sub-package `ketu/declination/` (core.py + api.py + `__init__.py`) mirroring `ketu/synastry/`.
- `DECLA_ASPECT_DTYPE`: `(body1 i1, body2 i1, kind U2 ∈ {"P","CP"}, gap f8, orb f8)`. `i1` for body indices (matches synastry `body_a`/`body_b`). Kind text `"P"`/`"CP"`. Keep both `gap` and `orb`. No symbol field.
- Scalar `find_declination_aspects(body_decl)` returns ONE unified structured array (P+CP mixed, `kind` field distinguishes), ordered by `(body1, body2)` ascending via `np.triu_indices`, empty = `np.empty(0, dtype=DECLA_ASPECT_DTYPE)`, never `None`. `body1 < body2` always.
- Batch: separate dedicated function, returns typed `NamedTuple` of bool masks `(S,91)` parallel + contra, `idx_i`/`idx_j` `(91,)`, `orb_pairs` `(91,)`, `gap` `(S,91)`. Precomputed 14×14 orb matrix, no Python body-loop.
- `core.py` = dtype + consts + orb matrix; `api.py` = scalar + batch; `__init__.py` = re-exports.
- Sub-module exposure only (`ketu.declination.find_declination_aspects`); top-level `ketu/__init__.py` `__all__` unchanged.
- `CHART_DTYPE` byte-identical; frozen 14-row `core.aspects` + V1/V13 sha256 fingerprints unchanged; 100% coverage + mypy `--strict` maintained.

### Claude's Discretion

- Exact `NamedTuple` field names/order for the batch return.
- Exact name of the batch function (e.g. `declination_aspect_masks`).
- Whether the 14×14 orb matrix is a module-level constant vs lazily built.
- Internal helper structure (`_decl_orb`, sign handling).

### Deferred Ideas (OUT OF SCOPE)

- Applying/separating detection on the δ axis (DECLA-F1).
- Exact-crossing timing for declination aspects (DECLA-F2).
- δ synastry (inter-chart parallels/contras, DECLA-F3).
- Dedicated CLI surface for declination aspects (DECLA-F4).
- `HARMF-01` (rich `--harmonics` grammar) — explicitly deferred out of v1.6.
- Codeclination (Boehrer's 23°27′ mirror).
- "Both OOB" annotation on parallels.
</user_constraints>

---

## Summary

Phase 36 adds `ketu/declination/` — a pure-NumPy companion that detects parallels and contra-parallels on the δ axis using `CHART_DTYPE["body_decl"]` (shipped v1.5). The math and orb formula are fully locked in `.planning/research/DECLINATION_ASPECTS.md`. This research anchors those decisions in the real codebase: exact file paths to mirror, exact existing types and constants to reuse, exact test names that must stay green, and concrete regression seeds with computed oracle values.

The closest existing analog is `ketu/synastry/` — a 3-file sub-package (`core.py` + `api.py` + `__init__.py`) that takes `CHART_DTYPE` records and emits structured arrays. Phase 36 mirrors this layout exactly. The 14-body axis is confirmed at `core.bodies` with `np.triu_indices(14, k=1)` → 91 upper-triangle pairs (14×13/2 = 91, verified).

**Primary recommendation:** Clone the synastry 3-file layout, declare `DECLA_ASPECT_DTYPE` in `core.py`, implement both functions in `api.py`, re-export from `__init__.py`. Do not touch `ketu/core.py`, `ketu/charts/core.py`, or `ketu/__init__.py`.

---

## Architecture Patterns

### New Sub-Package Layout to Create

```
ketu/declination/
├── __init__.py   # re-exports: DECLA_ASPECT_DTYPE, DECLA_COEF, MIN_DECL_ORB, find_declination_aspects, <batch_fn>
├── core.py       # DECLA_ASPECT_DTYPE, DECLA_COEF=1/12, MIN_DECL_ORB=0.5, _ORB_MAT (14×14 frozen)
└── api.py        # find_declination_aspects(body_decl) + batch function
```

Exact mirror of `/home/loc/workspace/ketu/ketu/synastry/` (3 files: `core.py`, `api.py`, `__init__.py`).

### Synastry Analog — Exact Layout

Reference: `/home/loc/workspace/ketu/ketu/synastry/`

| synastry file | purpose | declination analog |
|---|---|---|
| `core.py` | `SYNASTRY_DTYPE`, `SYNASTRY_BODY_COUNT` | `DECLA_ASPECT_DTYPE`, `DECLA_COEF`, `MIN_DECL_ORB`, orb matrix |
| `orbs.py` | orb formula, `_BODY_ORBS_16` | merged into `core.py` (simpler: no synastry factor, no ASC/MC) |
| `api.py` | `calculate_synastry(chart_a, chart_b)` | `find_declination_aspects(body_decl)` + batch |
| `__init__.py` | re-exports everything | same pattern |

Note: synastry has a 4th file (`orbs.py`). For declination the orb logic is simpler (one formula, no factor preset), so merge orb constants into `core.py` — no separate `orbs.py` needed.

### Import Patterns to Use in New Package

```python
# In ketu/declination/core.py
from __future__ import annotations
import numpy as np
from ketu.core import bodies as _BODIES

# In ketu/declination/api.py
from __future__ import annotations
from typing import NamedTuple
import numpy as np
from ketu.core import bodies as _BODIES        # same as synastry/orbs.py line 36
from .core import DECLA_ASPECT_DTYPE, DECLA_COEF, MIN_DECL_ORB  # or import _ORB_MAT directly
```

The `from ketu.core import bodies as _BODIES` pattern is confirmed in:
- `/home/loc/workspace/ketu/ketu/synastry/orbs.py` line 36: `from ketu.core import aspects as _ASPECTS, bodies as _BODIES`

### `DECLA_ASPECT_DTYPE` Declaration (verbatim from CONTEXT.md)

```python
DECLA_ASPECT_DTYPE: np.dtype = np.dtype([
    ("body1", "i1"),   # index into core.bodies (0-13), body1 < body2
    ("body2", "i1"),
    ("kind",  "U2"),   # "P" (parallel) or "CP" (contra-parallel)
    ("gap",   "f8"),   # |δ₁−δ₂| for P, |δ₁+δ₂| for CP, degrees
    ("orb",   "f8"),   # derived orb limit used for this pair, degrees
])
```

`i1` dtype mirrors synastry's `body_a`/`body_b` fields (confirmed: `/home/loc/workspace/ketu/ketu/synastry/core.py` lines 107-108).

### Orb Matrix Pattern

From synastry/orbs.py's `_build_body_orbs_16()` pattern (lines 59-86), the analogous pattern for the 14×14 declination orb matrix:

```python
def _build_orb_matrix() -> np.ndarray:
    orbs = _BODIES["orb"].astype(np.float64)  # shape (14,)
    mat = np.maximum(
        np.add.outer(orbs, orbs) / 2 * DECLA_COEF,
        MIN_DECL_ORB
    )  # shape (14, 14), f8
    mat.flags.writeable = False  # freeze — matches synastry _BODY_ORBS_16 convention
    return mat

_ORB_MAT: np.ndarray = _build_orb_matrix()  # module-level constant, computed once
```

`_BODIES["orb"]` is `f4` in `core.bodies` — cast to `f8` for the matrix to keep full precision (same `.astype(np.float64)` pattern used in brief §3.2 seed code).

### Scalar Function Pattern

```python
def find_declination_aspects(
    body_decl: np.ndarray,  # shape (14,), signed degrees
) -> np.ndarray:            # shape (K,) DECLA_ASPECT_DTYPE
    idx_i, idx_j = np.triu_indices(14, k=1)   # (91,) each
    d1 = body_decl[idx_i]                      # (91,)
    d2 = body_decl[idx_j]                      # (91,)
    orb_pairs = _ORB_MAT[idx_i, idx_j]         # (91,)
    gap_p  = np.abs(d1 - d2)
    gap_cp = np.abs(d1 + d2)
    s1, s2 = np.sign(d1), np.sign(d2)
    mask_p  = (s1 == s2) & (s1 != 0) & (gap_p  <= orb_pairs)
    mask_cp = (s1 != s2) & (s1 != 0) & (s2 != 0) & (gap_cp <= orb_pairs)
    # Build structured array...
    ...
    return result  # np.empty(0, dtype=DECLA_ASPECT_DTYPE) if no aspects
```

Note: the function is itself fully vectorized (no Python loop over bodies). The brief's §3.1 sketch used a Python loop; the CONTEXT.md locked a single structured array return — the implementation can vectorize internally even in the scalar function.

### Batch Function NamedTuple Pattern

```python
from typing import NamedTuple

class DeclinationAspectMasks(NamedTuple):
    parallel: np.ndarray    # shape (S, 91), bool
    contra: np.ndarray      # shape (S, 91), bool
    gap: np.ndarray         # shape (S, 91), f8 — min(gap_p, gap_cp) per pair
    idx_i: np.ndarray       # shape (91,), int — body index 1
    idx_j: np.ndarray       # shape (91,), int — body index 2
    orb_pairs: np.ndarray   # shape (91,), f8 — per-pair orb limit
```

NamedTuple usage in ketu is confirmed at `/home/loc/workspace/ketu/ketu/cli/harmonics_spec.py` line 65 (`class HarmonicsSelection(NamedTuple)`) and `/home/loc/workspace/ketu/ketu/ephemeris/planets.py` line 71 (`class _BodyCalc(NamedTuple)`). The `typing.NamedTuple` form is compatible with mypy `--strict`.

### `__init__.py` Pattern (mirror synastry)

```python
# ketu/declination/__init__.py
from __future__ import annotations
from .api import find_declination_aspects, <batch_fn_name>
from .core import DECLA_ASPECT_DTYPE, DECLA_COEF, MIN_DECL_ORB

__all__ = [
    "DECLA_ASPECT_DTYPE",
    "DECLA_COEF",
    "MIN_DECL_ORB",
    "find_declination_aspects",
    "<batch_fn_name>",
]
```

Reference: `/home/loc/workspace/ketu/ketu/synastry/__init__.py` lines 49-68.

---

## Codebase Anchors

### `CHART_DTYPE` — `body_decl` field

**File:** `/home/loc/workspace/ketu/ketu/charts/core.py`

```python
CHART_DTYPE: np.dtype = np.dtype([
    ...
    ("body_decl",     "f8", (14,)),   # line 103: δ per body, degrees [-90, +90], North positive
    ...
])
```

- Scalar chart record: `chart["body_decl"]` → shape `(14,)`
- Batch array `(S,)`: `charts["body_decl"]` → shape `(S, 14)`

This is the ONLY input to `find_declination_aspects`. The function takes the `(14,)` array directly, not the full `CHART_DTYPE` record (keeps it decoupled).

### `ketu.core.bodies` — 14-body axis

**File:** `/home/loc/workspace/ketu/ketu/core.py` lines 69-87

```python
bodies = np.array([
    ("Sun",     0, 12, 0.986),   # id=0,  orb=12
    ("Moon",    1, 12, 13.176),  # id=1,  orb=12
    ("Mercury", 2,  8, 1.383),   # id=2,  orb=8
    ("Venus",   3, 10, 1.2),     # id=3,  orb=10
    ("Mars",    4,  8, 0.524),   # id=4,  orb=8
    ("Jupiter", 5, 10, 0.083),   # id=5,  orb=10
    ("Saturn",  6, 10, 0.034),   # id=6,  orb=10
    ("Uranus",  7,  6, 0.012),   # id=7,  orb=6
    ("Neptune", 8,  6, 0.007),   # id=8,  orb=6
    ("Pluto",   9,  4, 0.004),   # id=9,  orb=4
    ("Rahu",   10,  0, -0.052954), # id=10, orb=0 (zero — MIN_DECL_ORB applies)
    ("Ketu",   11,  0, -0.052954), # id=11, orb=0
    ("Lilith", 12,  0, 0.113),   # id=12, orb=0
    ("Chiron", 13,  4, 0.019),   # id=13, orb=4
], dtype=[("name", "S12"), ("id", "i4"), ("orb", "f4"), ("speed", "f4")])
```

`_BODIES["orb"]` dtype is `f4`. The orb matrix builder must `.astype(np.float64)` before `np.add.outer`.

### Orb Formula Verification

Worked examples (confirmed from brief §2.3):

| Pair | orb formula result |
|---|---|
| Sun/Moon (0,1) | `max((12+12)/2 × 1/12, 0.5)` = **1.000°** |
| Sun/Venus (0,3) | `max((12+10)/2 × 1/12, 0.5)` = **0.917°** |
| Venus/Mars (3,4) | `max((10+8)/2 × 1/12, 0.5)` = **0.750°** |
| Rahu/Lilith (10,12) | `max((0+0)/2 × 1/12, 0.5)` = **0.500°** (floor) |
| Pluto/Chiron (9,13) | `max((4+4)/2 × 1/12, 0.5)` = **0.500°** (floor; 0.333 < floor) |

### `np.triu_indices(14, k=1)` — 91 pairs

```python
idx_i, idx_j = np.triu_indices(14, k=1)
# len(idx_i) == 91  (= 14*13/2, verified)
# idx_i[0]=0, idx_j[0]=1  (Sun, Moon)
# idx_i[-1]=12, idx_j[-1]=13  (Lilith, Chiron)
```

Confirmed in `/home/loc/workspace/ketu/ketu/aspects/calculator.py` line 382. The declination module uses the same pattern for upper-triangle enumeration.

---

## Tests That MUST Stay Green (Do Not Break)

### CHART_DTYPE Ratchets — `/home/loc/workspace/ketu/tests/charts/test_dtype.py`

| Test | What it pins | Why it breaks if violated |
|---|---|---|
| `test_dtype_has_expected_field_names` | 15 fields in exact order including `body_decl` | Any dtype change to `CHART_DTYPE` goes red |
| `test_dtype_subarray_shapes` (parametrized) | `body_decl` shape `(14,)` | Confirms v1.5 addition frozen |
| `test_body_count_frozen_at_fourteen` | `ketu.charts.api._BODY_COUNT == 14` | Confirms no new bodies added |
| `test_dtype_scalar_field_kinds` | All field kinds/itemsizes | Dtype width drift |
| `test_no_runtime_swisseph_import` | AGPL boundary | ketu.charts must not pull swisseph |

These tests must pass byte-for-byte. Phase 36 does NOT touch `ketu/charts/core.py` or `ketu/charts/api.py`.

### `core.aspects` V1/V13 sha256 Fingerprints — `/home/loc/workspace/ketu/tests/test_ketu.py`

| Test | Fingerprint constant | What it covers |
|---|---|---|
| `TestData.test_aspects_byte_fingerprint` (V1 path) | `EXPECTED_ASPECT_FINGERPRINT_V1 = "c5bd177316ce98d428bee011a5b0f17ae247d1dee1e478c2389af51d39afb359"` | `aspects["name"] + ["angle"] + ["coef"]` bytes frozen |
| `TestData.test_aspects_byte_fingerprint` (V13 path) | `EXPECTED_ASPECT_FINGERPRINT_V13 = "3258530818272989c27eb6de6a717947df1a2fccda10d9562aa15ef67b8f27d8"` | Extends V1 with `harmonic + symbol` bytes |

Phase 36 does NOT touch `ketu/core.py`. These must stay green.

### Additional Ratchets to Keep Green

- `/home/loc/workspace/ketu/tests/test_ketu.py::TestData::test_aspects_length` — `len(aspects) == 14`
- `/home/loc/workspace/ketu/tests/test_ketu.py::TestData::test_aspects_dtype_names` — 5-field schema frozen
- All 250+ existing tests — coverage gate `fail_under = 100` means ANY uncovered line in `ketu/` fails CI

---

## Quality Gates the New Package Must Satisfy

### 100% Coverage (`pyproject.toml` line 110)

`fail_under = 100` applies to the entire `ketu/` source tree. Every line in `ketu/declination/core.py`, `ketu/declination/api.py`, and `ketu/declination/__init__.py` must be reached by tests. No `# pragma: no cover` allowed (zero-pragma policy from Phase 21).

Confirmed exclude lines (safe to use): only the 7 patterns in `pyproject.toml` lines 111-129 (`pragma: no cover`, `def __repr__`, `raise NotImplementedError`, `if __name__ == "__main__":`, `if TYPE_CHECKING:`, the two post-modulo guards, the binary-search fallback). None of these are needed in the new sub-package.

### mypy `--strict` (`pyproject.toml` lines 166-186)

`[tool.mypy] strict = true`. The new `ketu/declination/` module is NOT listed in the `disable_error_code` override block (which only covers `ketu.calculations`, `ketu.complex`, `ketu.cycles.*`, etc.). Therefore the new package must satisfy full strict mypy.

Key implications:
- All functions need complete type annotations including return types.
- `np.ndarray` must be annotated carefully — use `np.ndarray` (mypy's numpy stubs handle it).
- `NamedTuple` fields need explicit type annotations: `parallel: np.ndarray`.
- `from __future__ import annotations` at top of every file (already the pattern across synastry, composite).
- No implicit `Any`; no untyped function parameters.

Reference: synastry/core.py uses `from __future__ import annotations` (line 57) and full annotations. api.py imports `from typing import Literal, Tuple, cast` (line 50).

### `pyproject.toml` Package Registration

**File:** `/home/loc/workspace/ketu/pyproject.toml` line 70

```toml
packages = ["ketu", "ketu.ephemeris", "ketu.aspects", "ketu.cycles", "ketu.cache",
            "ketu.houses", "ketu.charts", "ketu.cli", "ketu.synastry", "ketu.composite",
            "ketu.returns", "ketu.parts", "ketu.data"]
```

`ketu.declination` must be added to this list or the sub-package will not be installed.

---

## V1.5 Declination Infrastructure (Source of Oracle Fixtures)

### Functions Available

**File:** `/home/loc/workspace/ketu/ketu/calculations.py` lines 440-586

```python
def declination(jdate: Union[float, np.ndarray], body: int) -> Union[float, np.ndarray]:
    ...  # returns signed δ in degrees

def declination_velocity(jdate: float, body: int) -> float:
    ...  # dδ/dt in degrees/day

def is_ascending_declination(jdate: float, body: int) -> bool:
    ...  # dδ/dt > 0

def is_out_of_bounds(jdate: float, body: int) -> bool:
    ...  # |δ| > true_obliquity(jdate)
```

### Existing Test JDs (from `/home/loc/workspace/ketu/tests/test_declination.py`)

```python
JD_DESC = utc_to_julian(datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc))
# Moon δ ≈ +19.8956°, velocity ≈ -4.6051°/day (descending)

JD_ASC = 2460742.0
# Moon δ ≈ +28.6641°, velocity > 0 (ascending), OOB

JD_OOB = 2460676.5
# Moon δ ≈ -25.8853°, Sun δ ≈ -22.9982°, OOB (2025-01-01)

JD_INBOUNDS = utc_to_julian(datetime(2025, 6, 15, 12, 0, tzinfo=timezone.utc))
# Moon δ ≈ -19.72°, in-bounds
```

These JDs are available as fixtures to derive `body_decl` arrays for the new tests. Import `from ketu.calculations import declination` and compute `np.array([declination(jd, i) for i in range(14)])`.

---

## Regression Oracle Seeds (Computed, Citable)

### Seed 1: Summer Solstice 2000-06-21 (VERIFIED by running ketu)

**JD:** `2451717.0` (= 2000-06-21 12:00 UTC, `utc_to_julian(datetime(2000, 6, 21, 12, 0, tzinfo=timezone.utc))`)

**All 14 body declinations at JD 2451717.0:**

```python
# [Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Rahu, Ketu, Lilith, Chiron]
body_decl_solstice = np.array([
    +23.4373,  # 0 Sun
    -16.9561,  # 1 Moon
    +20.7104,  # 2 Mercury
    +23.8916,  # 3 Venus
    +24.2021,  # 4 Mars
    +18.9241,  # 5 Jupiter
    +17.2105,  # 6 Saturn
    -15.3320,  # 7 Uranus
    -18.5429,  # 8 Neptune
    -10.9362,  # 9 Pluto
    +20.9450,  # 10 Rahu
    -20.9431,  # 11 Ketu
    -22.8438,  # 12 Lilith
    -16.9228,  # 13 Chiron
])
```

**Expected parallels (P) at this date:**

| body1 | body2 | δ₁ | δ₂ | gap | orb |
|---|---|---|---|---|---|
| 0 Sun | 3 Venus | +23.4373 | +23.8916 | 0.4542° | 0.9167° |
| 0 Sun | 4 Mars | +23.4373 | +24.2021 | 0.7648° | 0.8333° |
| 1 Moon | 13 Chiron | -16.9561 | -16.9228 | 0.0333° | 0.6667° |
| 2 Mercury | 10 Rahu | +20.7104 | +20.9450 | 0.2346° | 0.5000° |
| 3 Venus | 4 Mars | +23.8916 | +24.2021 | 0.3105° | 0.7500° |

**Expected contra-parallels (CP) at this date:**

| body1 | body2 | δ₁ | δ₂ | mirror | orb |
|---|---|---|---|---|---|
| 1 Moon | 6 Saturn | -16.9561 | +17.2105 | 0.2544° | 0.9167° |
| 2 Mercury | 11 Ketu | +20.7104 | -20.9431 | 0.2327° | 0.5000° |
| 5 Jupiter | 8 Neptune | +18.9241 | -18.5429 | 0.3812° | 0.6667° |
| 6 Saturn | 13 Chiron | +17.2105 | -16.9228 | 0.2877° | 0.5833° |
| 10 Rahu | 11 Ketu | +20.9450 | -20.9431 | 0.0019° | 0.5000° |

**Total expected rows: 10** (5 P + 5 CP). This is a strong regression oracle.

### Seed 2: Moon OOB Near Parallel with Sun (JD_OOB from v1.5 oracle)

**JD:** `2460676.5` (= 2025-01-01 00:00 TT)

From `test_declination.py`: Moon δ ≈ -25.8853°, Sun δ ≈ -22.9982° at this date.

```python
# At JD_OOB = 2460676.5:
# Moon (body 1): δ ≈ -25.8853° (OOB: |δ| > ε ≈ 23.44°)
# Sun (body 0):  δ ≈ -22.9982°
# gap = |-25.8853 - (-22.9982)| = 2.887° > orb 1.0° → NOT a parallel
# This is a NEGATIVE test: Moon/Sun are NOT parallel despite being on same side
# because gap 2.887° > orb 1.0°
```

Use this as a regression fixture confirming the detector does NOT falsely trigger on large same-side gaps.

**How to derive other seeds:** Run `declination(jd, body)` over a date scan and find dates where `gap < 0.1°` for a known pair (tight parallel). The `JD_ASC = 2460742.0` (Moon δ ≈ +28.66°) combined with any planet near +28° would give an OOB parallel fixture.

---

## The Four Required Pitfall Tests (Exact Assertions)

All four must appear as explicit test cases in `tests/declination/`:

### Pitfall 1: Sign Conflation — +15/−15 is CP Not P

```python
d = np.zeros(14)
d[0] = +15.0   # Sun body 0
d[1] = -15.0   # Moon body 1
result = find_declination_aspects(d)
mask_p  = result["kind"] == "P"
mask_cp = result["kind"] == "CP"
p_sun_moon = result[(result["body1"] == 0) & (result["body2"] == 1) & mask_p]
cp_sun_moon = result[(result["body1"] == 0) & (result["body2"] == 1) & mask_cp]
assert len(p_sun_moon) == 0, "Sun +15 / Moon -15 must NOT be a parallel"
assert len(cp_sun_moon) == 1, "Sun +15 / Moon -15 MUST be a contra-parallel"
assert cp_sun_moon[0]["gap"] < 0.001
```

### Pitfall 2: Orb Inflation — 7° Sun/Moon Gap Not Parallel

```python
d = np.zeros(14)
d[0] = +15.0   # Sun
d[1] = +22.0   # Moon — gap = 7° > 1.0° orb
result = find_declination_aspects(d)
p_sun_moon = result[(result["body1"] == 0) & (result["body2"] == 1) & (result["kind"] == "P")]
assert len(p_sun_moon) == 0, "7° gap must NOT be a parallel (orb is 1.0° not 12°)"
```

### Pitfall 3: Zero-Sign Trap — Both δ=0 → No Aspect

```python
d = np.zeros(14)   # all bodies at δ=0
result = find_declination_aspects(d)
assert len(result) == 0, "All-zero declinations must produce no aspects"

# Also: near-zero opposite sign
d2 = np.zeros(14)
d2[0] = +0.01   # Sun just north
d2[1] = -0.01   # Moon just south
result2 = find_declination_aspects(d2)
p = result2[result2["kind"] == "P"]
cp = result2[result2["kind"] == "CP"]
assert len(p) == 0, "Near-zero opposite signs must NOT be parallel"
# gap = 0.02° < MIN_DECL_ORB 0.5° → IS a contra-parallel
assert len(cp) >= 1, "Near-zero opposite signs MUST be contra-parallel (within 0.5° floor)"
```

### Pitfall 4: MIN_DECL_ORB Floor — Rahu/Lilith Gap 0.1° → Parallel

```python
d = np.zeros(14)
d[10] = +12.5   # Rahu (orb=0)
d[12] = +12.4   # Lilith (orb=0) — gap = 0.1°, both orb=0
# Without floor: orb = max(0 × 1/12, 0) = 0.0° → no detection
# With floor:    orb = max(0, 0.5) = 0.5° → detects 0.1° < 0.5°
result = find_declination_aspects(d)
p_rahu_lilith = result[(result["body1"] == 10) & (result["body2"] == 12) & (result["kind"] == "P")]
assert len(p_rahu_lilith) == 1, "Rahu/Lilith parallel (gap 0.1°) must be detected via MIN_DECL_ORB floor"
```

---

## Test File Layout (Mirror synastry)

Create `tests/declination/` mirroring `tests/synastry/`:

```
tests/declination/
├── __init__.py
├── conftest.py              # shared fixtures (computed body_decl arrays)
├── test_dtype.py            # DECLA_ASPECT_DTYPE ratchets (field names, widths, itemsize)
├── test_find_aspects.py     # find_declination_aspects: pitfalls 1-4, oracle seed 1 + 2
├── test_batch.py            # batch function: shape (S,91), dtype, NamedTuple fields
└── test_declination_coverage_gate.py  # module import + marker sentinel
```

Reference test structure: `/home/loc/workspace/ketu/tests/synastry/` (6 files: `__init__.py`, `conftest.py`, `fixtures/`, `test_dtype.py`, `test_calculate_synastry.py`, `test_applying.py`, `test_modes_idempotent.py`, `test_oracle.py`, `test_orbs.py`, `test_synastry_coverage_gate.py`).

### `test_dtype.py` Must Cover

Following `tests/synastry/test_dtype.py` pattern:

- `test_public_imports_resolve` — `ketu.declination.DECLA_ASPECT_DTYPE` is `np.dtype`
- `test_dtype_field_count_five` — exactly 5 fields
- `test_dtype_field_names_canonical_order` — `("body1", "body2", "kind", "gap", "orb")`
- `test_dtype_body1_dtype_int8` — `"i1"`
- `test_dtype_body2_dtype_int8` — `"i1"`
- `test_dtype_kind_dtype_unicode2` — `np.dtype("U2")`
- `test_dtype_gap_dtype_float64` — `"f8"`
- `test_dtype_orb_dtype_float64` — `"f8"`
- `test_dtype_itemsize_pinned` — `1 + 1 + 8 + 8 + 8 = 26` bytes (check actual; `U2` = 2×4=8 bytes in NumPy UCS-4)
- `test_can_allocate_empty_array` — `np.empty(0, dtype=DECLA_ASPECT_DTYPE).shape == (0,)`

Note on U2 itemsize: NumPy stores Unicode as UCS-4. `U2` = 2 codepoints × 4 bytes = 8 bytes. Total: `1 + 1 + 8 + 8 + 8 = 26 bytes`. Verify with `DECLA_ASPECT_DTYPE.itemsize` and pin it.

### `conftest.py` Fixtures

```python
import numpy as np
import pytest
from ketu.calculations import declination

JD_SOLSTICE_2000 = 2451717.0  # 2000-06-21 12:00 UTC

@pytest.fixture
def body_decl_solstice() -> np.ndarray:
    """All 14 body declinations at 2000-06-21 12:00 UTC."""
    return np.array([declination(JD_SOLSTICE_2000, i) for i in range(14)])

@pytest.fixture
def body_decl_zeros() -> np.ndarray:
    return np.zeros(14)
```

---

## Anti-Patterns to Avoid

- **Python loop over 14 bodies in the hot path:** The batch function must use `np.triu_indices` + broadcasting. The scalar function can also be vectorized internally (no loop needed even there).
- **Returning `None` for empty result:** Always return `np.empty(0, dtype=DECLA_ASPECT_DTYPE)`.
- **Returning a tuple `(parallels, contras)` from `find_declination_aspects`:** Context.md locked a single unified array. The brief's §3.1 sketch (tuple return) is superseded.
- **Using `abs(d1) - abs(d2)` as separation metric for both P and CP:** This is Pitfall 1. Always compute `gap_p = abs(d1 - d2)` and `gap_cp = abs(d1 + d2)` separately.
- **Forgetting `np.sign(d) == 0` for δ=0 bodies:** Both `s1 == s2 != 0` and `s1 != s2 and s1 != 0 and s2 != 0` correctly handle this.
- **Touching `ketu/core.py`, `ketu/charts/core.py`, or `ketu/__init__.py`:** Phase 36 is additive only. No changes to existing files except `pyproject.toml` (add `ketu.declination` to `packages`).
- **Using f4 for `gap`/`orb` fields:** DECLA_ASPECT_DTYPE uses `f8` for both (unlike synastry's f4 `orb`/`orb_limit`). The declination range is small enough that f4 would be fine, but f8 is locked per CONTEXT.md.

---

## Open Questions

None for planning purposes. All decisions are locked.

The batch function name and NamedTuple field names are Claude's discretion. Suggested: `declination_aspect_masks` (function) and `DeclinationAspectMasks` (NamedTuple class).

---

## Sources

### Primary (HIGH confidence — direct codebase reads)

- `/home/loc/workspace/ketu/ketu/synastry/core.py` — exact `SYNASTRY_DTYPE` pattern to mirror
- `/home/loc/workspace/ketu/ketu/synastry/api.py` — exact `calculate_synastry` pattern, import style
- `/home/loc/workspace/ketu/ketu/synastry/orbs.py` — orb matrix build pattern, `_BODY_ORBS_16`, `_BODIES` import
- `/home/loc/workspace/ketu/ketu/synastry/__init__.py` — re-export pattern
- `/home/loc/workspace/ketu/ketu/core.py` — `bodies` array, 14 bodies, `orb` field values
- `/home/loc/workspace/ketu/ketu/charts/core.py` — `CHART_DTYPE`, `body_decl` field at line 103
- `/home/loc/workspace/ketu/tests/charts/test_dtype.py` — exact ratchet test names
- `/home/loc/workspace/ketu/tests/test_ketu.py` — V1/V13 sha256 fingerprints + test names
- `/home/loc/workspace/ketu/tests/test_declination.py` — JD oracle seeds
- `/home/loc/workspace/ketu/pyproject.toml` — `fail_under=100`, `mypy strict=true`, `packages` list
- `/home/loc/workspace/ketu/.planning/research/DECLINATION_ASPECTS.md` — math, orb formula, pitfalls (source of truth)
- Oracle computation: run `declination(2451717.0, i)` for all 14 bodies (verified above)

---

## RESEARCH COMPLETE

**Phase:** 36 — Declination Aspects Core
**Confidence:** HIGH

### Key Findings

1. **`ketu/synastry/` is the exact template**: 3-file layout (core.py + api.py + `__init__.py`), `i1` body indices, `from ketu.core import bodies as _BODIES`, `from __future__ import annotations`, `np.empty(0, dtype=...)` empty return, `__all__` re-export. Mirror this exactly.

2. **No existing file needs modification except `pyproject.toml`**: Add `ketu.declination` to the `packages` list (line 70). Everything else is purely additive.

3. **Concrete oracle: 10 aspects at JD 2451717.0 (2000-06-21)**: 5 parallels + 5 contra-parallels with exact expected `gap` and `orb` values (computed and tabulated above). Use as the primary regression fixture.

4. **Ratchets that must not break** (exact names):
   - `tests/charts/test_dtype.py::test_dtype_has_expected_field_names` (CHART_DTYPE byte-identical)
   - `tests/charts/test_dtype.py::test_body_count_frozen_at_fourteen` (_BODY_COUNT == 14)
   - `tests/test_ketu.py::TestData::test_aspects_byte_fingerprint` (V1 + V13 sha256)
   - `tests/test_ketu.py::TestData::test_aspects_length` (14 aspects)

5. **Quality gates**: `fail_under=100` (zero-pragma), `mypy --strict` (full, no override block for `ketu.declination`), `interrogate fail-under=95` (docstrings). The new sub-package must satisfy all three.

### File to be Created

`.planning/phases/36-declination-aspects-core/36-RESEARCH.md`

### Confidence Assessment

| Area | Level | Reason |
|---|---|---|
| Architecture / file layout | HIGH | Directly read synastry source |
| `DECLA_ASPECT_DTYPE` declaration | HIGH | Locked in CONTEXT.md, synastry pattern confirmed |
| Orb formula | HIGH | Computed and verified against brief §2.3 |
| Ratchet test names | HIGH | Directly read test files |
| Oracle seed values | HIGH | Computed by running ketu.calculations.declination |
| mypy/coverage gates | HIGH | Read pyproject.toml directly |

### Ready for Planning

Research complete. Planner can now write PLAN.md files.
