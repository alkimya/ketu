# Architecture Research — Ketu v1.1 Integration

**Domain:** Astronomical/astrological calculation library (pure NumPy, PyPI-published)
**Researched:** 2026-05-06
**Confidence:** HIGH (based on direct code inspection of Ketu 1.0.0 source)
**Scope:** Integration of v1.1 features (configurable aspects, houses, Lilith fix) into existing Ketu architecture — *not* a green-field redesign.

---

## Executive Summary

The existing Ketu architecture is well-modularized with clean import boundaries. The v1.1 work is **additive** rather than transformative:

1. **Configurable aspects** = filter view over the existing 14-aspect master `core.aspects` array, exposed via a new `aspects/presets.py` module + a `selected_indices` parameter threaded through call sites. Backward compat is achieved by defaulting CLI to `classical` while leaving the master constant intact.
2. **Houses** = a fresh `ketu/houses/` submodule with a registry pattern (`SYSTEMS: dict[str, callable]`). The existing stub `calculate_house_cusps` in `ephemeris/planets.py` is a placeholder — it should be **deprecated and re-routed** through the new module, not extended.
3. **Lilith fix** = swap the formula inside `ephemeris/orbital.get_lilith_position()`. Public API (`body_id=12`) does not change. Optional Mean/True variants land as a parameter, not a new body slot, to avoid breaking `bodies` array indexing.

**Build order is dictated by dependencies:** Lilith fix is independent (lowest risk, ship first), aspects refactor must precede CLI flags (CLI consumes presets), houses can land in parallel with aspects since they share no code paths.

---

## Existing Architecture (As-Is, v1.0.0)

### Module Topology

```
ketu/
├── __init__.py                 # Re-exports: bodies, aspects, signs, __version__
├── core.py                     # bodies (np.ndarray, 13 rows), aspects (np.ndarray, 14 rows), signs (list)
├── calculations.py             # Position helpers: long(), lat(), positions(), body_id()
├── display.py                  # CLI entry: main(), print_positions(), print_aspects()
├── __main__.py                 # python -m ketu → display.main
├── complex.py                  # Complex-number ML feature extraction
├── lunar_calendar.py           # Lunar phase calendar
├── ephemeris/
│   ├── __init__.py             # Re-exports calculate_house_cusps (STUB)
│   ├── time.py                 # JD <-> UTC, sidereal_time
│   ├── orbital.py              # ORBITAL_ELEMENTS, get_*_position(), get_lilith_position() ← FIX TARGET
│   ├── coordinates.py          # ecliptic↔equatorial, mean_obliquity, true_obliquity
│   └── planets.py              # calc_planet_position(_batch), calculate_house_cusps (STUB) ← REPLACE
├── aspects/                    # Submodule (was a single file pre-1.0)
│   ├── __init__.py             # Public API (15 names)
│   ├── core.py                 # get_aspect_index(), get_cached_positions(), refine_exact_moment(), find_orb_boundaries()
│   ├── calculator.py           # get_orb(), calculate_aspects[_vectorized|_batch](), find_aspects_between_dates()
│   ├── windows.py              # AspectMoment, AspectWindow, find_aspect_window()
│   ├── timelines.py            # AspectEvent, AspectTimeline, generate_aspect_timeline()
│   └── transits.py             # TransitMoment, find_transits_to_position()
├── cycles/
│   ├── __init__.py             # CYCLE_DTYPE, generate_cycle_series, MAJOR_ASPECTS
│   └── calculator.py           # Has its OWN MAJOR_ASPECTS = [0,60,90,120,180,240,270,300,360] — not coupled to core.aspects
└── cache/
    ├── __init__.py
    └── ephemeris_cache.py      # EphemerisCache class (file-backed cache)
```

### How `core.aspects` is Used Today (Coupling Map)

| Site | File | Pattern | Coupling Strength |
|------|------|---------|-------------------|
| `aspects/calculator.py:14` | `from ketu.core import bodies, aspects` | Iterates `aspects["angle"]` in `get_aspect()`, `calculate_aspects_*()` | **STRONG** — must accept filter |
| `aspects/core.py:16` | `from ketu.core import bodies, aspects` | `get_aspect_index()` lookup | **MEDIUM** — only resolves names/angles |
| `aspects/windows.py:19` | `from ketu.core import bodies, aspects` | Aspect name decoding | **WEAK** — read-only |
| `aspects/timelines.py:25` | `from ketu.core import bodies, aspects` | Default `aspects_list` is hardcoded `["Conjunction", "Sextile", "Square", "Trine", "Opposition"]` (already 5 majors!) | **NONE for default** |
| `aspects/transits.py:26` | `from ketu.core import bodies, aspects` | Aspect lookups | **MEDIUM** |
| `display.py:12` | `from .core import signs, aspects` | Pretty-prints aspect names | **WEAK** |
| `cycles/calculator.py` | Defines own `MAJOR_ASPECTS` | **DECOUPLED** — does not import `core.aspects` | **NONE** |

**Critical finding:** The cycles module is already decoupled from `core.aspects` (uses its own `MAJOR_ASPECTS` array for proximity calculation). The aspects refactor only ripples through the `aspects/` submodule and `display.py`. **`cycles/` and `complex.py` are unaffected.**

**Second finding:** `generate_aspect_timeline()` already defaults to the 5 majors (Conjunction/Sextile/Square/Trine/Opposition) — it is *not* part of the v1.0 default-14 problem. The "default 14" problem lives in `calculate_aspects()`, `calculate_aspects_vectorized()`, and `calculate_aspects_batch()` only.

---

## Recommended v1.1 Structure

```
ketu/
├── core.py                       # MODIFIED: add ASPECT_PRESETS dict, keep `aspects` array intact (full 14)
├── aspects/
│   ├── presets.py                # NEW: name → np.ndarray mapping; resolve_preset(); get_default_indices()
│   ├── calculator.py             # MODIFIED: accept selected_indices param, default to preset
│   ├── core.py                   # MODIFIED: get_aspect_index() now scoped by preset
│   ├── windows.py                # MODIFIED: pass-through `selected_indices`
│   ├── timelines.py              # UNCHANGED (already 5-major default)
│   └── transits.py               # MODIFIED: pass-through `selected_indices`
├── houses/                       # NEW SUBMODULE
│   ├── __init__.py               # Public API: calculate_houses(), HOUSE_DTYPE, list_systems()
│   ├── _registry.py              # NEW: SYSTEMS = {"placidus": _placidus, "koch": _koch}
│   ├── _angles.py                # NEW: ramc(), obliquity_for_jd(), ascendant(), midheaven() — shared primitives
│   ├── placidus.py               # NEW: _placidus(jd_array, lat_array, lon_array) → vectorized cusps
│   ├── koch.py                   # NEW: _koch(jd_array, lat_array, lon_array) → vectorized cusps
│   └── assignment.py             # NEW: assign_planet_to_house(longitudes, cusps) — vectorized
├── ephemeris/
│   ├── orbital.py                # MODIFIED: get_lilith_position() uses verified formula; add get_lilith_position_true() optional
│   └── planets.py                # MODIFIED: deprecate calculate_house_cusps stub, route to ketu.houses
├── display.py                    # MODIFIED: argparse with subcommands; --harmonics flag; new `houses` subcommand
└── __init__.py                   # MODIFIED: export ASPECT_PRESETS, calculate_houses, HOUSE_DTYPE
```

### Structure Rationale

- **`aspects/presets.py` (new file, not in `core.py`):** Keeps `core.py` as pure data (NumPy structured arrays, list); presets are *behavior* (resolution logic, aliasing) which belongs adjacent to the consumers. Importing `from ketu.aspects.presets import CLASSICAL, TRADITIONAL, EXTENDED, ALL` mirrors how `cycles` exports `DEFAULT_PAIRS`.
- **`houses/` as a flat submodule (not `houses.py`):** Multiple house systems each warrant their own file (Placidus is ~80 lines of trig with iterative refinement; Koch is similar but with different spherical projection). The registry pattern (`_registry.py`) makes adding Whole Sign / Equal / Porphyry in v1.2 a 1-file change.
- **`_angles.py` separate:** ASC/MC/RAMC are shared primitives between every house system (Placidus and Koch both depend on them). Hoisting them prevents copy-paste between system files.
- **No new top-level `cli/` package:** The existing `display.py` is the natural CLI home. Refactoring it to argparse + subcommands keeps surface area small. Moving to a `cli/` package is over-engineering for ~3 subcommands.

---

## Architectural Patterns

### Pattern 1: Preset Filter as Index Array (configurable aspects)

**What:** Keep `core.aspects` as the immutable master list of 14 aspects. Presets are *index arrays* into that master list — not new aspect arrays.

**When to use:** Anywhere a function currently iterates `aspects["angle"]`, replace with iteration over `aspects[selected_indices]["angle"]`.

**Trade-offs:**
- (+) `core.aspects` API unchanged — existing code that does `from ketu.core import aspects` still works.
- (+) `selected_indices` is a NumPy array → vectorizes naturally.
- (+) Resolving a preset name to indices happens once at API boundary, not in hot loops.
- (−) Every public function that takes "which aspects" needs a new parameter (additive, defaults preserve behaviour).

**Example:**

```python
# ketu/aspects/presets.py
import numpy as np
from ketu.core import aspects

# Index arrays into the master `aspects` table (14 rows)
CLASSICAL  = np.array([0, 7, 9, 13, 4])           # Conj, Square, Trine, Opp, Sextile (5 majors)
TRADITIONAL = np.array([0, 7, 9, 13, 4, 1, 11])   # Classical + Semi-sextile + Quincunx (7)
EXTENDED   = np.arange(len(aspects))              # All 14 (legacy v1.0 default)

PRESETS: dict[str, np.ndarray] = {
    "classical":   CLASSICAL,
    "traditional": TRADITIONAL,
    "extended":    EXTENDED,
    "all":         EXTENDED,  # alias for CLI --harmonics all
}

def resolve_preset(spec: str | list | np.ndarray) -> np.ndarray:
    """Resolve a preset name OR list of harmonic numbers OR explicit indices to index array."""
    if isinstance(spec, str):
        if spec in PRESETS:
            return PRESETS[spec]
        # Parse "9,10,11" → indices for those harmonics
        return _harmonics_to_indices([int(h) for h in spec.split(",")])
    return np.asarray(spec, dtype=int)

DEFAULT_PRESET = "classical"  # ← v1.1 default; v1.0 was "extended"
```

```python
# ketu/aspects/calculator.py — modified signature
def calculate_aspects(
    jdate: float,
    l_bodies: np.ndarray = bodies,
    selected_indices: np.ndarray | None = None,  # NEW
) -> np.ndarray:
    if selected_indices is None:
        from ketu.aspects.presets import resolve_preset, DEFAULT_PRESET
        selected_indices = resolve_preset(DEFAULT_PRESET)
    # Loop becomes: for i_asp in selected_indices: aspect_angle = aspects["angle"][i_asp]
    ...
```

### Pattern 2: Registry for House Systems

**What:** A `dict[str, Callable]` maps system name → calculator function. Public `calculate_houses(system="placidus", ...)` dispatches.

**When to use:** Whenever multiple interchangeable algorithms share a signature. Standard in scientific Python (SciPy `minimize`, NumPy `linalg`).

**Trade-offs:**
- (+) Adding a new system = 1 file + 1 dict entry. No core changes.
- (+) Trivial introspection: `list_systems()` returns dict keys.
- (+) Each system's internals stay private (`_placidus`, `_koch`) — public API is the dispatcher.
- (−) Type checkers can't enforce that all callables have identical signatures without a `Protocol`. Mitigation: define `HouseCalculator` Protocol.

**Example:**

```python
# ketu/houses/__init__.py
import numpy as np
from typing import Protocol
from ketu.houses._registry import SYSTEMS

HOUSE_DTYPE = np.dtype([
    ("julian_day",     "f8"),
    ("geo_lat",        "f8"),
    ("geo_lon",        "f8"),
    ("system",         "U16"),
    ("cusps",          "f8", (12,)),   # 12 house cusps in degrees, House 1 = ASC
    ("ascendant",      "f8"),
    ("midheaven",      "f8"),
    ("vertex",         "f8"),
    ("equatorial_asc", "f8"),
])

class HouseCalculator(Protocol):
    def __call__(
        self, jd_array: np.ndarray, lat_array: np.ndarray, lon_array: np.ndarray
    ) -> np.ndarray: ...  # Returns structured array of HOUSE_DTYPE

def calculate_houses(
    jd: float | np.ndarray,
    geo_lat: float | np.ndarray,
    geo_lon: float | np.ndarray,
    system: str = "placidus",
) -> np.ndarray:
    """Vectorized house calculation. Returns structured array of shape (N,)."""
    if system not in SYSTEMS:
        raise ValueError(
            f"unknown house system: {system!r}. "
            f"Valid systems: {sorted(SYSTEMS.keys())}"
        )
    jd_arr  = np.atleast_1d(np.asarray(jd,      dtype="f8"))
    lat_arr = np.atleast_1d(np.asarray(geo_lat, dtype="f8"))
    lon_arr = np.atleast_1d(np.asarray(geo_lon, dtype="f8"))
    return SYSTEMS[system](jd_arr, lat_arr, lon_arr)

def list_systems() -> list[str]:
    return sorted(SYSTEMS.keys())
```

```python
# ketu/houses/_registry.py
from ketu.houses.placidus import _placidus
from ketu.houses.koch import _koch

SYSTEMS = {
    "placidus": _placidus,
    "koch":     _koch,
}
```

### Pattern 3: Vectorized Iterative Refinement (Placidus inner loop)

**What:** Placidus cusps require solving a transcendental equation (semi-arc proportion). Each cusp converges in 3-6 Newton-Raphson iterations. Vectorize across the *date axis*, accept Python iteration across the 6 intermediate cusps (II, III, V, VI, VIII, IX).

**When to use:** Algorithms with bounded iteration count (≤ ~10) where convergence per element is fast.

**Trade-offs:**
- (+) Same shape as `calc_planet_position_batch()` — `(n_dates, 6)` arrays in, structured array out.
- (+) Cusps I (ASC), IV (IC = MC+180°), VII (DSC = ASC+180°), X (MC) are closed-form, no iteration.
- (−) Circumpolar latitudes (>~66°) cause `arcsin` domain errors — must clamp or raise (Placidus is undefined there; Koch has the same restriction). Document the limitation.

**Example sketch:**

```python
# ketu/houses/placidus.py
def _placidus(jd_array, lat_array, lon_array):
    n = jd_array.shape[0]
    out = np.empty(n, dtype=HOUSE_DTYPE)
    out["julian_day"] = jd_array
    out["geo_lat"]    = lat_array
    out["geo_lon"]    = lon_array
    out["system"]     = "placidus"

    # Closed-form: ASC, MC (vectorized over n)
    eps = mean_obliquity(jd_array)               # (n,)
    ramc = sidereal_time(jd_array, lon_array)    # (n,)
    asc = ascendant(ramc, lat_array, eps)        # (n,)
    mc  = midheaven(ramc, eps)                   # (n,)

    out["ascendant"] = asc
    out["midheaven"] = mc
    out["cusps"][:, 0] = asc                     # House 1
    out["cusps"][:, 3] = (mc + 180.0) % 360.0    # House 4 (IC)
    out["cusps"][:, 6] = (asc + 180.0) % 360.0   # House 7 (DSC)
    out["cusps"][:, 9] = mc                      # House 10

    # Iterative: II, III, V, VI, VIII, IX (each is a fraction F of semi-arc)
    for house_idx, F in [(1, 1/3), (2, 2/3), (4, 2/3), (5, 1/3),
                         (7, 1/3), (8, 2/3)]:
        out["cusps"][:, house_idx] = _solve_placidus_cusp(
            ramc, lat_array, eps, F, sign=+1 if house_idx < 4 else -1
        )

    return out
```

---

## Data Flow

### CLI flow (v1.1)

```
$ ketu positions --date 2026-05-06 --harmonics classical
        │
        ▼
display.main() → argparse → subcommand="positions"
        │
        ▼
preset_indices = aspects.presets.resolve_preset("classical")  # → np.array([0,7,9,13,4])
        │
        ▼
print_positions(jd) ; print_aspects(jd, selected_indices=preset_indices)
        │
        ▼
calculate_aspects(jd, selected_indices=preset_indices)
        │
        ▼
for i_asp in selected_indices:               ← was: for i_asp in range(14)
    angle = aspects["angle"][i_asp]
    ...
```

```
$ ketu houses --date 2026-05-06 --time 12:00 --lat 48.85 --lon 2.35 --system placidus
        │
        ▼
display.main() → subcommand="houses"
        │
        ▼
jd = utc_to_julian(...)
result = ketu.houses.calculate_houses(jd, 48.85, 2.35, system="placidus")
        │
        ▼
print_houses(result)   ← new helper in display.py
```

### Library flow (Kala consumer)

```python
from ketu.aspects.presets import CLASSICAL, EXTENDED
from ketu.aspects import calculate_aspects_batch
from ketu.houses import calculate_houses

# Default 5 majors (new behaviour) — automatic
aspects_v11 = calculate_aspects_batch(jd_array)

# Explicit harmonics for ML feature engineering
aspects_ml  = calculate_aspects_batch(jd_array, selected_indices=EXTENDED)

# Houses for natal interpretation
houses = calculate_houses(jd, lat=48.85, lon=2.35, system="placidus")
```

---

## Integration Points (per feature)

### Feature A: Configurable Aspects

**Existing modules touched:**

| File | Modification | Risk |
|------|--------------|------|
| `ketu/aspects/calculator.py` | Add `selected_indices` param to `get_aspect`, `calculate_aspects`, `calculate_aspects_vectorized`, `calculate_aspects_batch`, `find_aspects_between_dates` | LOW (additive) |
| `ketu/aspects/windows.py` | Pass-through `selected_indices` in `find_aspect_window`, `find_aspects_timeline` | LOW |
| `ketu/aspects/transits.py` | Pass-through in `find_transits_to_position`, `compare_dates_transits` | LOW |
| `ketu/aspects/core.py` | `get_aspect_index()` accepts optional `valid_indices` for nicer error messages | LOW |
| `ketu/aspects/__init__.py` | Re-export presets | LOW |
| `ketu/__init__.py` | Re-export `ASPECT_PRESETS` | LOW |
| `ketu/display.py` | Resolve `--harmonics` flag → indices, pass through | MEDIUM (CLI semantics change) |

**New files:**
- `ketu/aspects/presets.py` — `PRESETS` dict, `resolve_preset()`, constants `CLASSICAL`, `TRADITIONAL`, `EXTENDED`.

**Backward compatibility:**
- `core.aspects` array stays at length 14 → `from ketu.core import aspects; len(aspects) == 14` still holds.
- Library callers that don't pass `selected_indices` get the new `classical` default → **breaking change** for the implicit count. Mitigation: documented in CHANGELOG + UPGRADING.md, override is `selected_indices=EXTENDED` (one-line fix).
- CLI `--harmonics all` reproduces v1.0 output exactly.
- `cycles/` is untouched (decoupled).

### Feature B: Houses Module

**Existing modules touched:**

| File | Modification | Risk |
|------|--------------|------|
| `ketu/ephemeris/planets.py` | `calculate_house_cusps()` deprecated; emit `DeprecationWarning` + delegate to `ketu.houses.calculate_houses()` | LOW (preserves existing import path) |
| `ketu/ephemeris/__init__.py` | Keep re-export for one cycle, add deprecation note | LOW |
| `ketu/__init__.py` | Add `from ketu.houses import calculate_houses, HOUSE_DTYPE` to `__all__` | LOW |
| `ketu/display.py` | New `houses` subcommand handler + `print_houses()` formatter | MEDIUM |

**New files (all in `ketu/houses/`):**
- `__init__.py` — public API (`calculate_houses`, `HOUSE_DTYPE`, `list_systems`, `assign_planet_to_house`)
- `_angles.py` — `ascendant()`, `midheaven()`, `ramc()` shared primitives (vectorized)
- `_registry.py` — `SYSTEMS` dict
- `placidus.py` — `_placidus()` calculator
- `koch.py` — `_koch()` calculator
- `assignment.py` — `assign_planet_to_house()`

**Reuse from existing code:**
- `ephemeris/time.py:sidereal_time()` — already exists, used as RAMC source.
- `ephemeris/coordinates.py:mean_obliquity()` / `true_obliquity()` — already exists.
- `np.atleast_1d` pattern from `calc_planet_position_batch` — same vectorization approach.

**Vectorization plan:**
Output dtype shape `(N,)` where N is the broadcast size of `(jd, lat, lon)`. ASC/MC are closed-form NumPy expressions. The 6 intermediate cusps run a fixed-iteration Newton solve where each iteration is a vectorized step over `(N,)`. Total: zero Python loops over the date axis; one Python loop of length 6 over the cusps; ≤8 inner iterations per cusp (also Python-level but bounded).

### Feature C: Lilith Fix

**Existing modules touched:**

| File | Modification | Risk |
|------|--------------|------|
| `ketu/ephemeris/orbital.py` | `get_lilith_position()` formula correction. Optionally add `get_lilith_position_true(jd)` for True Lilith. | MEDIUM (needs verification against Astro.com / Swiss Ephemeris reference values) |
| `ketu/ephemeris/planets.py` | If True Lilith is exposed, branch in `calc_planet_position()` (else: no change — body_id 12 still works). | LOW |
| `ketu/core.py` | If exposing True Lilith as separate body: extend `bodies` array. **Recommend: do NOT extend.** Keep id=12 for Mean Lilith, expose True via separate function. | — (decision: don't extend) |

**Reference verification approach:**
1. Pull Astro.com ephemeris values for J2000, 1900-01-01, 1950-01-01, 2000-01-01, 2025-01-01, 2050-01-01.
2. Compare against current `83.3532 + 0.1114040803 * d` formula.
3. The Chapront-Touz/Francou formula used by Swiss Ephemeris (per Astro.com docs) is the authoritative reference. Constants for J2000 epoch differ subtly; verify both intercept and rate.
4. Land regression test: `tests/ephemeris/test_lilith_reference.py` with 5 known dates ±0.01° tolerance.

**API decision: Mean vs True Lilith**
- **Recommended:** Body id=12 stays Mean (current). Add `get_lilith_position_true(jd)` as a separate function in `ephemeris/orbital.py`, NOT a separate body slot.
- **Why not extend `bodies` to 14 rows:** Many downstream consumers (Kala KetuAdapter, Surya) iterate `range(13)` or `bodies[:13]`. Adding a row breaks those. Sub-variants of a body via parameter is the safer additive path.
- **Future-proofing:** When other body variants land (e.g., True Node vs Mean Node already coexist via id 10/11 — but that's because they're geometrically distinct points), keep the rule: new body slot = new geometric point; new variant = parameter or function suffix.

### Feature D: CLI Refactor

**Existing modules touched:**

| File | Modification | Risk |
|------|--------------|------|
| `ketu/display.py` | Replace `input()`-based interactive flow with argparse subcommands. Keep `print_positions`, `print_aspects` as helpers. | MEDIUM-HIGH (only file users touch) |
| `ketu/__main__.py` | Unchanged (still calls `display.main`) | NONE |
| `pyproject.toml` | `[project.scripts]` entry should already point to `ketu.display:main` — verify. | LOW |

**Subcommand design:**

```
ketu                              # Backward-compat: launch interactive prompt (or replace with --help)
ketu positions DATE [TIME] [TZ]   # Print body positions
ketu aspects DATE [--harmonics SPEC]
ketu houses DATE TIME --lat LAT --lon LON [--system placidus|koch]
ketu transits DATE --to-date DATE [--harmonics SPEC]
```

**`--harmonics` parsing:** Delegate to `aspects.presets.resolve_preset()` which already accepts:
- preset names (`classical`, `traditional`, `extended`, `all`)
- comma-separated harmonic numbers (`9,10,11`)
- (future) explicit aspect names (`Conjunction,Square`)

**Backward compat note:** The existing v1.0 CLI is interactive (`input()` prompts). Argparse-with-no-args could either (a) preserve interactive flow when no subcommand is given, or (b) print `--help`. **Recommend (a) for one minor version, then deprecate.** This avoids breaking shell scripts that pipe input.

---

## Build Order (Recommended Phase Sequencing)

Build order is constrained by:
- CLI flags consume `aspects.presets` → presets must land first.
- Houses are independent of aspects → can run in parallel with aspects work.
- Lilith fix is independent of everything → ship anytime; lowest risk first is good morale.

| # | Feature | Depends On | Why This Order |
|---|---------|------------|----------------|
| 1 | **Lilith verification + fix** | Nothing | Independent; verification step gates the fix. Builds confidence + clears the "correctness" requirement before adding new surface area. |
| 2 | **Aspect presets** (`presets.py` + `selected_indices` threading) | Nothing | Foundation for CLI flags. Touches all `aspects/*.py` files; needs to settle before CLI changes. |
| 3 | **Houses module** (Placidus first, Koch second) | Nothing | Parallelizable with #2 if needed (different files). Placidus first because Koch shares the `_angles.py` primitives Placidus establishes. |
| 4 | **CLI refactor** (argparse + `--harmonics` + `houses` subcommand) | #2 (presets) AND #3 (houses) | CLI is the integration surface; both upstream features must exist. |
| 5 | **Docs + CHANGELOG + UPGRADING.md + version bump 1.1.0** | #1-4 | Standard release tail. |

**Critical dependency:** Phase #4 cannot start until #2 lands (CLI imports `resolve_preset`) and #3 lands (CLI calls `calculate_houses`). Phases #2 and #3 can run in parallel (different files, no shared symbols).

**Risk-ordered alternative (if Lilith verification reveals a non-trivial fix):**
1. Aspect presets → 2. Houses → 3. CLI → 4. Lilith (last, more time for verification) → 5. Release.
This swaps Lilith last if external reference comparison takes longer than expected.

---

## Scaling Considerations

This is a calculation library, not a service. "Scale" means **batch size of date arrays**.

| Scale (n_dates × n_pairs) | Architecture Adjustments |
|---------------------------|--------------------------|
| 100s of dates × 13 bodies | Vectorized NumPy is enough. LRU cache on `body_properties` already handles repeated lookups. |
| 10K dates × 13 bodies | Current `calc_planet_position_batch` already vectorizes per-body. Houses must follow the same shape (already in design). |
| 100K+ dates | LRU cache (size 1024) becomes a liability — use `EphemerisCache` (file-backed, already exists). For houses, cache per (jd, geo_lat, geo_lon) tuple; geo coordinates rarely change in practice. |
| 1M+ dates | Consider chunking (process 100K-row chunks). Memory budget for HOUSE_DTYPE: ~200 bytes/row × 1M = 200MB — manageable. |

### Performance Priorities

1. **First bottleneck:** `calculate_aspects_batch` already loops Python-level over dates because of the matched_pairs set. With aspect filtering, the inner aspect loop shrinks from 14 to 5 → ~3× speedup for the default case. Free win.
2. **Second bottleneck:** Placidus inner solver is the new hot path. Newton-Raphson with vectorized step should converge in ≤6 iterations at <1e-6° tolerance. Profile after first implementation.
3. **Third bottleneck:** Aberration correction in `calc_planet_position_batch` still has a Python loop (line 581-584). Pre-existing in v1.0; not a v1.1 concern.

---

## Anti-Patterns (Specific to v1.1)

### Anti-Pattern 1: Mutating `core.aspects` to filter

**What people do:** Replace the global `aspects` array with a filtered view based on a CLI flag at startup.
**Why it's wrong:** Breaks library users who imported `from ketu.core import aspects` expecting 14 rows. Globals + mutation = test pollution + import-order bugs.
**Do this instead:** Keep `core.aspects` immutable (it's a master constant). Pass `selected_indices` through call sites.

### Anti-Pattern 2: Houses as a flat `houses.py` file

**What people do:** Put Placidus + Koch + ASC/MC in a single 600-line `houses.py`.
**Why it's wrong:** Adding Whole Sign in v1.2 means editing the same file every system author touches. Merge conflicts. Also, each system has subtle edge cases (circumpolar latitudes for Placidus; different anchor for Koch); buried in one file they get tangled.
**Do this instead:** `houses/` package with one file per system + `_registry.py` dispatcher. Adding a system = 1 new file + 1 dict entry.

### Anti-Pattern 3: New body slot for Lilith variants

**What people do:** Add `body_id=13` for True Lilith, `body_id=14` for Lilith asteroid, etc.
**Why it's wrong:** Downstream code iterates `bodies['id']` or `range(13)`. Each new slot is a coordinated breaking change across Kala, Surya, and any external user.
**Do this instead:** One slot per geometrically distinct point. Variants of the same point (Mean vs True) are parameters or sister functions, not separate bodies.

### Anti-Pattern 4: Recompute ASC/MC inside every house system

**What people do:** Placidus reimplements ascendant; Koch reimplements ascendant; they drift apart over time.
**Why it's wrong:** Numerical drift between systems for cusps 1, 4, 7, 10 (which should be IDENTICAL across Placidus and Koch).
**Do this instead:** `_angles.py` defines `ascendant()`, `midheaven()`, `ramc()` once. Both system files import from there.

### Anti-Pattern 5: Defaulting CLI to "extended" silently

**What people do:** Ship v1.1 with default = 14 aspects to "preserve compat", document the preset system, and call it a day.
**Why it's wrong:** The whole point of v1.1 is the default change. Documenting `--harmonics classical` to opt INTO the new behaviour is the opposite of the requirement (PROJECT.md states the user's personal default is the 5 majors and v0.4 harmonics "leaked into the default").
**Do this instead:** Default IS classical. Document `--harmonics all` as the v1.0 compatibility flag. Bump minor (1.1.0) is sufficient for a documented default change in a pre-2.0 library.

---

## Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `ketu.aspects.presets` ↔ `ketu.core` | Import `aspects` array, build index arrays | One-way; presets depends on core |
| `ketu.aspects.calculator` ↔ `ketu.aspects.presets` | Default param resolution at call boundary | Lazy import to avoid module-load circularity |
| `ketu.houses` ↔ `ketu.ephemeris` | `houses` imports `sidereal_time`, `mean_obliquity` | Clean one-way dep |
| `ketu.houses` ↔ `ketu.calculations` | `houses` imports nothing from calculations | Houses are independent of body positions; planet→house assignment takes `longitudes` as input |
| `ketu.display` ↔ everything | Top of dependency tree, imports anything | Already true in v1.0 |
| `ketu.cycles` ↔ `ketu.aspects` | **None today, none in v1.1** | Cycles uses its own MAJOR_ASPECTS; aspect-preset change does not propagate |
| `ketu.complex` ↔ aspects/houses | None | Complex is leaf |

**No circular imports introduced.** Lazy imports inside `calculator.py` (for `presets`) match the existing `try: from ketu.cache import ...` pattern used in `cycles/calculator.py`.

---

## External Integration (Downstream Consumers)

| Consumer | What Breaks | Mitigation |
|----------|-------------|------------|
| Kala (KetuAdapter) | If it called `calculate_aspects_batch()` expecting 14-aspect rows, the v1.1 default returns 5-aspect rows | KetuAdapter must opt into `selected_indices=EXTENDED` (one-line); document in UPGRADING.md |
| Kala (KetuAdapter) | If it called `calculate_house_cusps` from `ketu.ephemeris.planets` (the stub) | Stub deprecated but kept for one minor cycle; emits warning. New code uses `ketu.houses.calculate_houses()` |
| Surya | Likely uses `positions()` and `body_properties()` — unchanged | None |
| Public PyPI users | `from ketu import bodies, aspects, signs` still works | None |

---

## Sources

- **Codebase inspection (HIGH confidence):**
  - `/home/loc/workspace/ketu/ketu/__init__.py` (public API surface)
  - `/home/loc/workspace/ketu/ketu/core.py` (master `aspects` array)
  - `/home/loc/workspace/ketu/ketu/aspects/{calculator,core,windows,timelines,transits}.py` (coupling sites)
  - `/home/loc/workspace/ketu/ketu/cycles/calculator.py` (decoupled MAJOR_ASPECTS — confirms no ripple)
  - `/home/loc/workspace/ketu/ketu/ephemeris/planets.py` (existing `calculate_house_cusps` stub at line 270; `get_lilith_position` formula at line 591)
  - `/home/loc/workspace/ketu/ketu/ephemeris/orbital.py` (Lilith formula `83.3532 + 0.1114040803 * d`)
  - `/home/loc/workspace/ketu/ketu/display.py` (existing CLI shape, `input()`-based)
  - `/home/loc/workspace/ketu/.planning/PROJECT.md` (v1.1 requirements, key decisions)
- **Placidus algorithm references (MEDIUM confidence — multiple sources agree):**
  - [Placidus House Equations (alt.astrology archives)](https://alt.astrology.moderated.narkive.com/jqcGiSkP/placidus-house-equations)
  - [Placidus cusp computation (Morinus Astrology)](https://morinus-astrology.com/placidus-cusps/)
  - [Astrology API: House Systems Comparison Guide 2026](https://astrology-api.io/blog/house-systems-comparison-guide)
  - [Swiss Ephemeris group: Placidus House Calculation discussion](https://groups.io/g/swisseph/topic/placidus_house_calculation/91265713)
- **Lilith reference formula (HIGH confidence — primary sources):**
  - [Astro.com Swiss Ephemeris documentation](https://www.astro.com/swisseph/swisseph.htm) — confirms Mean Apogee from Chapront/Chapront-Touz/Francou; deviation from Chapront's mean node = 0 at J2000, <20 arcseconds across 6000-year window
  - [Astrology Ephemeris for 9000+ years (Astro.com)](https://www.astro.com/swisseph/swepha_e.htm)
  - [Mean & True Black Moon Lilith (Serennu)](https://serennu.com/astrology/mean-true-black-moon.php) — confirms Mean = uniform rate, ~8.85 year cycle
  - [Lilith calculation variants (Kerykeion)](https://kerykeion.net/content/learn-astrology/foundation-lilith-variants)
  - [Cafe Astrology Lilith ephemeris](https://cafeastrology.com/black-moon-lilith-selena-sedna-ephemeris.html)

---

*Architecture research for: Ketu v1.1 (configurable aspects + houses + Lilith fix integration into existing v1.0.0 architecture)*
*Researched: 2026-05-06*
