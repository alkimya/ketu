# Phase 9: Configurable Aspects — Research

**Researched:** 2026-05-06
**Domain:** NumPy structured-array filtering, public API evolution, LRU cache invalidation, Python preset module design
**Confidence:** HIGH (codebase-grounded; cross-repo Kala contract is MEDIUM)

## Summary

Phase 9 is a pure-Python refactor inside an already-vectorized library. The existing `core.aspects` 14-row structured array (`ketu/core.py:84-103`) becomes an immutable, append-only registry whose row order is the canonical aspect index. Three named subsets (CLASSICAL=5, TRADITIONAL=7, EXTENDED=14) live in a new module `ketu/aspects/presets.py` as constants that resolve to `np.bool_` masks (length 14). Every public aspect API (`get_aspect`, `calculate_aspects`, `calculate_aspects_vectorized`, `calculate_aspects_batch`, plus `find_aspect_window`, `find_aspects_timeline`, `find_aspects_between_dates`, `find_transits_to_position`, `compare_dates_transits`, `generate_aspect_timeline`) gains an `aspects=` parameter that resolves once at entry into a single boolean mask and is passed down. Hot loops (`calculator.py:143`, `calculator.py:239`) iterate the masked indices only — they never re-resolve names. The `i_asp` field emitted in result rows continues to carry the canonical 0-13 index — that is precisely what preserves Kala's positional `aspects['name'][i_asp]` lookup.

The default semantic flips: `aspects=None` now means CLASSICAL (5), not "all 14". This is the one user-facing breaking change for Python API consumers; Kala must opt into `EXTENDED` (or pass an explicit list) to keep v1.0 behavior. There are exactly two LRU-cached functions in scope (`ketu/calculations.py:94` `body_properties` and `ketu/aspects/core.py:72` `_cached_planet_position_batch`), and **neither computes aspect filtering** — they only fetch positions. Filtering happens *after* the cache, which means cache keys do NOT need to include `aspect_set`. ASP-06 is satisfied trivially as long as no new cache is added that materializes filtered aspect arrays. (If we add such a cache for `calculate_aspects_batch`, the key MUST include the resolved-mask hash; see Pitfall 4.)

**Primary recommendation:** Add `ketu/aspects/presets.py` with three frozen `np.ndarray[bool]` masks of length 14 plus a single resolver `resolve_aspect_set(aspects, default=CLASSICAL) -> np.ndarray[bool]`. Add `aspects=None` parameter to all public aspect APIs. In each API, call the resolver exactly once at the top, then pass the boolean mask (or `mask.nonzero()[0]` index list) to the existing hot-loop sites — replace `enumerate(aspects["angle"])` with `enumerate(aspects["angle"][mask])` or pre-filter the angle/coef vectors. Pin row order with a hash-based invariant test plus per-row name-equality assertions. No new runtime dependencies, no `core.aspects` mutation, no changes to result `dtype`.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| numpy | >=1.20.0 (already pinned in `pyproject.toml:38`) | Boolean-mask filtering of structured arrays, `triu_indices`, `np.bool_` | Already the only runtime dep; "pure NumPy contract preserved" is a project decision |
| functools.lru_cache | stdlib | Existing cache pattern in `body_properties` and `_cached_planet_position_batch` | Already in use; do not introduce `cachetools` |
| hashlib (sha256) | stdlib | Stable hashing of an `np.ndarray[bool]` mask for invariant fingerprint test | Pure-stdlib; deterministic; resists ordering bugs better than `tuple(...)` of names which can drift in Python repr |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| typing | stdlib | `Union[str, Sequence[str], np.ndarray, None]` for the `aspects=` parameter | Public API typed surface |
| collections.abc.Sequence | stdlib | Runtime isinstance check on user-supplied lists/tuples | Resolver dispatch |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Boolean mask of length 14 | Tuple of indices `(0, 4, 7, 9, 13)` | Mask is faster for `numpy` filter (`arr[mask]` vs fancy indexing), allows `mask.sum()` for early-exit, hashes cheaply via `mask.tobytes()`. Indices win only if we needed sparse iteration over many positions (we don't — 14 is tiny). Pick mask. |
| New module `ketu/aspects/presets.py` | Add constants to `ketu/core.py` | `core.py` is already documented as "constants only; no logic". Presets *do* contain a resolver function, so they belong with calculator code, not core data. Subpackage promotes locality of aspect logic. Pick separate module. |
| Hash-based invariant test | Per-row equality test alone | Hash detects re-encoding of bytes (e.g. `S16` -> `U16`); per-row catches semantic drift. Use BOTH (defense in depth) — see Pitfall 6. |

**Installation:**
No new packages. NumPy already a dep.

## Architecture Patterns

### Recommended Project Structure

```
ketu/
├── core.py                       # UNCHANGED: aspects, bodies, signs constants
├── aspects/
│   ├── __init__.py               # MODIFIED: re-export CLASSICAL/TRADITIONAL/EXTENDED + resolver
│   ├── presets.py                # NEW: aspect-set constants + resolver
│   ├── core.py                   # UNCHANGED: shared algorithms (no aspect-set awareness)
│   ├── calculator.py             # MODIFIED: aspects= parameter on get_aspect, calculate_aspects, _vectorized, _batch, find_aspect_timing, find_aspects_between_dates
│   ├── windows.py                # MODIFIED: aspects= parameter on find_aspect_window (single-aspect API — already accepts one name; keep that, but add to find_aspects_timeline)
│   ├── timelines.py              # MODIFIED: aspects_list= already exists; default flip to CLASSICAL preset; respect resolver
│   └── transits.py               # MODIFIED: aspects_list= parameter on find_transits_to_position, compare_dates_transits — already exists; default flip to CLASSICAL
└── tests/
    └── test_aspect_presets.py    # NEW: invariant + preset + integration tests
```

**Key design decisions:**

1. **`core.aspects` is the registry, presets reference it by index.** The presets are NOT redefinitions of aspect angles; they are masks/index-arrays selecting rows from `core.aspects`. This guarantees the orb coefficients in `core.aspects['coef']` (indices 0-13) remain the single source of truth.

2. **`presets.py` imports from `ketu.core`, not vice versa.** Avoids circular imports. `presets.py` is a sibling of `calculator.py`, both depending on `ketu.core`.

3. **Resolver runs once per API call, outside hot loops.** Pattern below.

### Pattern 1: Preset module shape

```python
# ketu/aspects/presets.py
"""Aspect set presets and resolver for configurable aspect filtering.

Three named presets select subsets of the 14 aspects in ketu.core.aspects:
- CLASSICAL: 5 majors (conjunction, sextile, square, trine, opposition)
- TRADITIONAL: 7 (CLASSICAL + semi-sextile, quincunx)
- EXTENDED: 14 (legacy v1.0 default — all aspects)

Each preset is a length-14 np.bool_ array indexable into core.aspects.
"""
from __future__ import annotations
from typing import Sequence, Union

import numpy as np

from ketu.core import aspects as _ASPECTS

# Sanity-check that core.aspects has length 14 (defensive; the invariant test
# also enforces this).
assert len(_ASPECTS) == 14, (
    f"core.aspects length changed to {len(_ASPECTS)}; aspect presets are pinned to 14"
)

# Preset masks: length-14 np.bool_ arrays selecting rows of core.aspects
# Indices follow core.py:84-103 row order:
# 0=Conjunction, 1=Semi-sextile, 2=Decile, 3=Novile, 4=Sextile,
# 5=Quintile, 6=Binovile, 7=Square, 8=Tredecile, 9=Trine,
# 10=Biquintile, 11=Quincunx, 12=Quadrinovile, 13=Opposition

_CLASSICAL_INDICES = np.array([0, 4, 7, 9, 13], dtype=np.intp)
_TRADITIONAL_INDICES = np.array([0, 1, 4, 7, 9, 11, 13], dtype=np.intp)
_EXTENDED_INDICES = np.arange(14, dtype=np.intp)

def _indices_to_mask(indices: np.ndarray) -> np.ndarray:
    mask = np.zeros(14, dtype=np.bool_)
    mask[indices] = True
    mask.flags.writeable = False  # Frozen
    return mask

CLASSICAL: np.ndarray = _indices_to_mask(_CLASSICAL_INDICES)
TRADITIONAL: np.ndarray = _indices_to_mask(_TRADITIONAL_INDICES)
EXTENDED: np.ndarray = _indices_to_mask(_EXTENDED_INDICES)

_PRESET_BY_NAME = {
    "classical": CLASSICAL,
    "traditional": TRADITIONAL,
    "extended": EXTENDED,
}

AspectSetSpec = Union[None, str, Sequence[Union[str, int]], np.ndarray]

def resolve_aspect_set(
    spec: AspectSetSpec,
    default: np.ndarray = CLASSICAL,
) -> np.ndarray:
    """Resolve aspect-set spec into a length-14 boolean mask.

    Parameters
    ----------
    spec : None, str, Sequence[str|int], or np.ndarray
        - None: use `default` (CLASSICAL by default)
        - str: preset name ("classical", "traditional", "extended") — case-insensitive
        - Sequence of str: aspect names ("Conjunction", "Trine", ...) matched against core.aspects['name']
        - Sequence of int: aspect indices (0-13)
        - np.ndarray of bool, length 14: used as-is
        - np.ndarray of int: indices, converted to mask

    Returns
    -------
    np.ndarray of bool, length 14
        Mask selecting rows from core.aspects.

    Raises
    ------
    ValueError
        On unknown preset name, unknown aspect name, out-of-range index,
        or wrong-length boolean array.
    """
    if spec is None:
        return default
    if isinstance(spec, str):
        key = spec.lower()
        if key not in _PRESET_BY_NAME:
            valid = ", ".join(_PRESET_BY_NAME)
            raise ValueError(
                f"unknown aspect preset: '{spec}'. Valid presets: {valid}"
            )
        return _PRESET_BY_NAME[key]
    if isinstance(spec, np.ndarray):
        if spec.dtype == np.bool_:
            if spec.shape != (14,):
                raise ValueError(
                    f"boolean aspect mask must have shape (14,), got {spec.shape}"
                )
            return spec
        # int array → indices
        return _indices_to_mask(np.asarray(spec, dtype=np.intp))
    # Sequence (list/tuple) of strings or ints
    indices: list[int] = []
    for item in spec:
        if isinstance(item, str):
            idx = np.where(_ASPECTS["name"] == item.encode())[0]
            if len(idx) == 0:
                valid = ", ".join(a.decode() for a in _ASPECTS["name"])
                raise ValueError(
                    f"unknown aspect name: '{item}'. Valid aspects: {valid}"
                )
            indices.append(int(idx[0]))
        elif isinstance(item, (int, np.integer)):
            i = int(item)
            if not 0 <= i < 14:
                raise ValueError(
                    f"aspect index out of range: {i} (valid: 0-13)"
                )
            indices.append(i)
        else:
            raise ValueError(
                f"invalid aspect spec item: {item!r} (expected str or int)"
            )
    return _indices_to_mask(np.array(indices, dtype=np.intp))


__all__ = [
    "CLASSICAL",
    "TRADITIONAL",
    "EXTENDED",
    "AspectSetSpec",
    "resolve_aspect_set",
]
```

### Pattern 2: Resolve mask once at API entry, filter once before hot loop

**Current hot loop** (`ketu/aspects/calculator.py:143-178`):

```python
for i_asp, aspect_angle in enumerate(aspects["angle"]):
    aspect_coef = aspects["coef"][i_asp]
    orbs = (orbs_body1 + orbs_body2) / 2 * aspect_coef
    ...  # in_orb mask, append to results
```

**Refactored hot loop** (resolve once outside, filter angle/coef once, iterate filtered arrays — but EMIT canonical `i_asp` for Kala compatibility):

```python
# At API entry — resolve_aspect_set is the ONLY new call:
from ketu.aspects.presets import resolve_aspect_set
mask = resolve_aspect_set(aspects)             # length-14 bool, runs once
selected_indices = np.where(mask)[0]            # canonical 0-13 indices
selected_angles = _CORE_ASPECTS["angle"][mask]  # filtered, parallel to selected_indices
selected_coefs = _CORE_ASPECTS["coef"][mask]

# Hot loop iterates only the active subset:
for k, i_asp in enumerate(selected_indices):
    aspect_angle = selected_angles[k]
    aspect_coef = selected_coefs[k]
    orbs = (orbs_body1 + orbs_body2) / 2 * aspect_coef
    ...
    # CRITICAL: emit i_asp (the canonical 0-13 index from core.aspects),
    # NOT k (the position within the filtered subset). This preserves
    # Kala's positional `aspects['name'][i_asp]` contract.
    results.append((body1_ids[idx], body2_ids[idx], int(i_asp), orb_values[i]))
```

This keeps result row dtype identical (`("i_asp", "i4")` continues to mean "index into `core.aspects`") and skips work for filtered-out aspects entirely. Performance impact is **positive** for CLASSICAL (5/14 of inner-loop work) and zero for EXTENDED.

### Anti-Patterns to Avoid

- **Filtering inside the per-pair loop.** `calculator.py:143` already has the right structure (loop over aspects is outer); do NOT add `if i_asp in selected_indices:` inside — that's the "filter inside hot loop" anti-pattern ASP-05 explicitly bans. Solution: pre-filter `selected_angles`/`selected_coefs` *once*, iterate the filtered arrays.
- **Mutating `core.aspects`.** Never `aspects = aspects[mask]` reassignment at module level. Each public function gets its own filtered local. The module-level `core.aspects` stays length-14, append-only, frozen.
- **Renumbering `i_asp` to be 0..N-1 within the selected set.** Tempting (cleaner output) but breaks Kala's positional lookup. The `i_asp` field is a canonical index into `core.aspects`, not a row-number-in-results. Document this explicitly in the docstring.
- **Putting the resolver call in the per-date loop of `calculate_aspects_batch`** (`calculator.py:234`). It's already efficient because the per-aspect-type loop is INSIDE the per-date loop — but the resolver itself must execute once per API call (above the date loop), not per date.
- **Adding aspect-set state to module-level globals** (e.g. `_DEFAULT_ASPECT_SET = CLASSICAL` mutable). Thread-unsafe and hides config changes. Each API call resolves explicitly from its parameter.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Aspect-name -> index lookup | New dict | `np.where(_ASPECTS["name"] == name.encode())[0]` (already used at `aspects/core.py:55`, `aspects/timelines.py:457`) | Already idiomatic in this codebase; avoids redundant data structures that can drift |
| Mask hashing for invariant test | `tuple(aspects['name'])` | `hashlib.sha256(aspects['name'].tobytes() + aspects['angle'].tobytes() + aspects['coef'].tobytes()).hexdigest()` | bytes-level fingerprint catches dtype drift (S16→U16, f4→f8) that tuple-equality misses |
| Per-call mask cloning to avoid mutation | `mask.copy()` everywhere | Set `mask.flags.writeable = False` once at module load (see `_indices_to_mask`) | NumPy native frozen arrays; zero-cost; user accidentally writing raises `ValueError` |
| Custom test fixture for "all aspect APIs" | Hand-listed call list | Pytest `parametrize` over `(api_callable, kwargs)` tuples | Standard pytest pattern; test_ketu.py already uses class-based parametrize via `setup_method` |
| New benchmark harness | pytest-benchmark | Existing `tests/benchmark.py` + `tests/benchmark_aspect_window.py` (raw `time.perf_counter`) | pytest-benchmark NOT in deps (verified `pyproject.toml:42-44`); v1.0 baseline is whatever the existing scripts measured. Pattern: capture v1.0 baseline timings into a JSON fixture before refactor, then assert ≤5% regression in the same script |

**Key insight:** Every primitive needed already exists in this codebase. The phase is composition, not invention. Resist adding any new helper class; the resolver function + three numpy arrays is the entire surface area.

## Common Pitfalls

### Pitfall 1: Breaking Kala by changing `i_asp` semantics
**What goes wrong:** Refactor renumbers `i_asp` from "canonical index in core.aspects (0-13)" to "position in selected subset (0-N-1)". Kala's `aspects['name'][i_asp]` then dereferences the wrong row.
**Why it happens:** During hot-loop refactor, it's "natural" to use `enumerate(filtered_array)`'s loop variable as the index.
**How to avoid:** Use `selected_indices = np.where(mask)[0]` and emit `selected_indices[k]` (or unpack `for k, i_asp in enumerate(selected_indices)` — see Pattern 2). Add an explicit test that `result['i_asp']` values are valid indices into the unfiltered length-14 `core.aspects` (i.e. `0 <= i_asp < 14`, NOT `< len(selected)`).
**Warning signs:** `result['i_asp'].max() < 14` for EXTENDED (correct) but `result['i_asp'].max() < 5` for CLASSICAL (WRONG — should be 13 since Opposition is index 13 and is in CLASSICAL).

### Pitfall 2: Default-value silent breakage
**What goes wrong:** User upgrades Ketu, calls `calculate_aspects(jd)` (no kwargs), suddenly gets 5 aspects instead of 14. They don't notice in tests; harmonics 9/10 disappear from ML features in production.
**Why it happens:** Default change is invisible at call site.
**How to avoid:** (a) CHANGELOG entry in BREAKING section per REL-02 (already on roadmap), (b) UPGRADING.md migration recipe per REL-03 (already on roadmap), (c) the integration test from ASP-07 must explicitly assert "calling `calculate_aspects(jd)` with no args returns no row whose `i_asp` is in `{1,2,3,5,6,8,10,12}` (the 9 non-classical indices)".
**Warning signs:** Existing tests that count `len(result) == 14` or check for `Quintile`-by-name will fail without `aspects=EXTENDED`. Sweep tests for hardcoded counts BEFORE flipping the default.

### Pitfall 3: `np.where(aspects['name'] == 'Trine')` failing on str vs bytes
**What goes wrong:** User passes `["Trine", "Square"]`, resolver does `np.where(_ASPECTS["name"] == "Trine")` → empty array because `_ASPECTS["name"]` is `S16` (bytes) but `"Trine"` is `str`.
**Why it happens:** Existing `core.aspects` uses `S16` dtype (`core.py:103`). Other modules already paper over this with `.encode()` (e.g. `aspects/core.py:55`, `aspects/timelines.py:457`).
**How to avoid:** Always `name.encode()` in the resolver before comparison. Add a test case `resolve_aspect_set(["Trine"])` returning a mask where index 9 is True.
**Warning signs:** Resolver silently returns all-False mask; downstream returns 0 aspects; no error raised. Mitigation: in resolver, raise `ValueError` if `len(idx) == 0` after `np.where` (mirror `aspects/core.py:56-58`).

### Pitfall 4: Adding a new LRU cache later that ignores `aspect_set`
**What goes wrong:** Phase 9 ships fine (no new caches added). Phase 11 or later adds `@lru_cache` over `calculate_aspects_batch` keyed on `(jd_array_tuple, body_set)`. Two callers with different `aspect_set` get the same cached result — stale.
**Why it happens:** ASP-06 says "LRU cache keys include `aspect_set` hash where applicable". The "where applicable" is a future-proofing clause; if no current cache materializes filtered aspects, the requirement is vacuously satisfied.
**How to avoid:** Document in `presets.py` docstring: "If a future cache materializes filtered aspect output, its key MUST include `mask.tobytes()` or `int.from_bytes(mask.tobytes(), 'little')`." Add a comment in `calculator.py` near `calculate_aspects_batch` referencing this. ASP-06 verification step: grep `@lru_cache` in aspect modules; assert each one's key tuple is independent of aspect filtering OR includes a mask hash.
**Warning signs:** During code review, see `@lru_cache` decorating any function whose return value depends on `aspect_set`.

### Pitfall 5: Mutable default trap on the `aspects` parameter
**What goes wrong:** `def calculate_aspects(jd, aspects=CLASSICAL)`. CLASSICAL is a frozen ndarray (`flags.writeable = False`), but it's still a *shared object* — any `aspects[0] = False` style accident inside the function would either raise (good) or be missed in code review (bad).
**Why it happens:** Python mutable-default-argument anti-pattern.
**How to avoid:** Default to `None` in the signature, resolve inside: `def calculate_aspects(jd, aspects=None): mask = resolve_aspect_set(aspects)`. The resolver supplies CLASSICAL when input is None. This matches the existing `aspects_list=None` pattern in `windows.py:430`, `timelines.py:398`, `transits.py:304`.
**Warning signs:** Function signature shows `aspects=CLASSICAL` directly. Refactor to `aspects=None` + resolver.

### Pitfall 6: Invariant test that's too weak (or too strong)
**What goes wrong:**
- Too weak: `assert len(aspects) == 14` only — passes if someone reorders rows or changes coefficients.
- Too strong: golden-file byte comparison of the entire `core.aspects` ndarray — fails on numpy version upgrade if internal padding changes.
**Why it happens:** Existing test `test_ketu.py:43-49` is an example of "too weak" — it spot-checks 4 fields out of 42 (14 rows × 3 fields).
**How to avoid:** Defense in depth. (a) Length: `len(aspects) == 14`. (b) Per-row name: assert each `aspects['name'][i].decode() == EXPECTED_NAMES[i]` for the full 14-row list. (c) Per-row angle: `aspects['angle'][i] == EXPECTED_ANGLES[i]` (exact equality is fine — these are integer-valued floats stored as f4). (d) Per-row coef: `aspects['coef'][i] == pytest.approx(EXPECTED_COEFS[i], abs=1e-6)` (1/6, 1/9 etc. are not exact in f4). (e) Hash fingerprint: `sha256(aspects['name'].tobytes() + aspects['angle'].tobytes() + aspects['coef'].tobytes()).hexdigest() == EXPECTED_HASH`. (f) dtype names: `aspects.dtype.names == ('name', 'angle', 'coef')`. The hash is the "fast canary" — if anything changes it screams. The per-row tests give surgical error messages.
**Warning signs:** Test passes when you mutate one row. Mutation-test it: temporarily swap rows 1 and 2 in `core.py` and confirm the test fails.

### Pitfall 7: Forgetting to update `find_aspect_window` (single-aspect API)
**What goes wrong:** ASP-03 lists three calculator APIs explicitly. But `find_aspect_window` (`windows.py:220`) takes a single aspect and `find_aspects_timeline` (`windows.py:380`) takes `aspects_list`. The latter has a hardcoded default `["Conjunction", "Sextile", "Square", "Trine", "Opposition"]` (BIG_FIVE). If we don't migrate it, the default-flip is applied inconsistently — `find_aspects_timeline` already returns CLASSICAL, but for the wrong reason (hardcoded list, not preset).
**Why it happens:** ASP-03 is scoped to the three batch APIs; the broader audit is implicit in ASP-07 ("integration test, all public aspect APIs").
**How to avoid:** Replace each hardcoded `["Conjunction", "Sextile", ...]` with `CLASSICAL` preset in: `windows.py:431-437`, `timelines.py:398-399`, `transits.py:304-305`, `transits.py:521-522`, `calculator.py` (no hardcoded list — uses `aspects['angle']` directly, fix via the new `aspects=` parameter). Also update lunar_calendar.py `BIG_FIVE = [0, 60, 90, 120, 180]` (`lunar_calendar.py:16`) to import from presets — but verify it actually uses angles, not preset masks. If kept as raw angles, document the parallelism.
**Warning signs:** Grep for `"Conjunction", "Sextile"` literal lists across the package; each match is a candidate site.

## Code Examples

Verified patterns from this codebase:

### Existing per-aspect loop (calculator.py:143-178)
```python
# Source: ketu/aspects/calculator.py:143-178 (current v1.0 implementation)
for i_asp, aspect_angle in enumerate(aspects["angle"]):
    orbs_body1 = l_bodies["orb"][i_indices]
    orbs_body2 = l_bodies["orb"][j_indices]
    aspect_coef = aspects["coef"][i_asp]
    orbs = (orbs_body1 + orbs_body2) / 2 * aspect_coef

    if i_asp == 0:  # Conjunction
        in_orb = all_distances <= orbs
        orb_values = all_distances[in_orb]
    else:
        in_orb = (all_distances >= aspect_angle - orbs) & (all_distances <= aspect_angle + orbs)
        orb_values = aspect_angle - all_distances[in_orb]

    if np.any(in_orb):
        for i, idx in enumerate(np.where(in_orb)[0]):
            pair = (body1_ids[idx], body2_ids[idx])
            if pair not in matched_pairs:
                results.append((body1_ids[idx], body2_ids[idx], i_asp, orb_values[i]))
                matched_pairs.add(pair)
```

### Refactored per-aspect loop with mask filter

```python
# Source: proposed Phase 9 refactor of ketu/aspects/calculator.py
from ketu.aspects.presets import resolve_aspect_set

def calculate_aspects_vectorized(
    jdate: float,
    l_bodies=bodies,
    aspects=None,  # NEW
) -> np.ndarray:
    mask = resolve_aspect_set(aspects)               # resolve once
    selected_idx = np.where(mask)[0]                  # canonical indices, ints
    selected_angles = _ASPECTS_DATA["angle"][mask]    # filtered, len = mask.sum()
    selected_coefs = _ASPECTS_DATA["coef"][mask]

    # ... (existing position calculation, unchanged) ...

    for k, i_asp in enumerate(selected_idx):
        aspect_angle = float(selected_angles[k])
        aspect_coef = float(selected_coefs[k])
        orbs = (orbs_body1 + orbs_body2) / 2 * aspect_coef
        # ... (unchanged in_orb logic) ...
        # Emit canonical i_asp (int 0-13), NOT k:
        results.append((body1_ids[idx], body2_ids[idx], int(i_asp), orb_values[i]))
```

### Append-only invariant test (proposed)

```python
# Source: proposed tests/test_aspect_presets.py — invariant section
import hashlib
import numpy as np
import pytest

from ketu.core import aspects

EXPECTED_NAMES = [
    b"Conjunction", b"Semi-sextile", b"Decile", b"Novile", b"Sextile",
    b"Quintile", b"Binovile", b"Square", b"Tredecile", b"Trine",
    b"Biquintile", b"Quincunx", b"Quadrinovile", b"Opposition",
]
EXPECTED_ANGLES = [0.0, 30.0, 36.0, 40.0, 60.0, 72.0, 80.0, 90.0,
                   108.0, 120.0, 144.0, 150.0, 160.0, 180.0]
EXPECTED_COEFS = [1.0, 1/6, 1/10, 1/9, 1/3, 1/5, 2/9, 1/2,
                  3/10, 2/3, 2/5, 5/6, 4/9, 1.0]

def test_aspects_length():
    assert len(aspects) == 14, "core.aspects must remain length 14 (append-only)"

def test_aspects_dtype_names():
    assert aspects.dtype.names == ("name", "angle", "coef")

def test_aspects_row_order_names():
    for i, expected in enumerate(EXPECTED_NAMES):
        assert aspects["name"][i] == expected, (
            f"row {i} name drifted: got {aspects['name'][i]!r}, expected {expected!r}"
        )

def test_aspects_row_order_angles():
    np.testing.assert_array_equal(aspects["angle"], np.array(EXPECTED_ANGLES, dtype="f4"))

def test_aspects_row_order_coefs():
    np.testing.assert_allclose(aspects["coef"], np.array(EXPECTED_COEFS, dtype="f4"), atol=1e-6)

def test_aspects_byte_fingerprint():
    """Hash fingerprint catches dtype/encoding drift that field-by-field tests miss."""
    h = hashlib.sha256()
    h.update(aspects["name"].tobytes())
    h.update(aspects["angle"].tobytes())
    h.update(aspects["coef"].tobytes())
    fingerprint = h.hexdigest()
    # NOTE: capture the actual fingerprint at the time of writing this test,
    # then pin it. If anyone changes core.aspects this test fails loudly.
    EXPECTED_FINGERPRINT = "<COMPUTED-AT-TEST-WRITE-TIME>"
    assert fingerprint == EXPECTED_FINGERPRINT, (
        "core.aspects bytes changed; update fingerprint AND verify the change is "
        "an APPEND (rows 0-13 unchanged) per Phase 9 invariant"
    )
```

The fingerprint should be computed once during planning/implementation and frozen. Note: the test will need to be updated if/when row 14+ is appended in the future — the planner should call this out.

### Resolver dispatch test pattern

```python
# Source: proposed tests/test_aspect_presets.py — resolver section
import pytest
import numpy as np
from ketu.aspects.presets import (
    CLASSICAL, TRADITIONAL, EXTENDED, resolve_aspect_set,
)

def test_resolve_none_returns_classical():
    np.testing.assert_array_equal(resolve_aspect_set(None), CLASSICAL)

def test_resolve_classical_string():
    np.testing.assert_array_equal(resolve_aspect_set("classical"), CLASSICAL)

def test_resolve_traditional_string():
    np.testing.assert_array_equal(resolve_aspect_set("traditional"), TRADITIONAL)

def test_resolve_extended_string():
    np.testing.assert_array_equal(resolve_aspect_set("extended"), EXTENDED)

def test_resolve_unknown_preset_raises():
    with pytest.raises(ValueError, match="unknown aspect preset"):
        resolve_aspect_set("invalid")

@pytest.mark.parametrize("names,expected_indices", [
    (["Conjunction"], [0]),
    (["Trine", "Square"], [7, 9]),
    (["Conjunction", "Sextile", "Square", "Trine", "Opposition"], [0, 4, 7, 9, 13]),
])
def test_resolve_name_list(names, expected_indices):
    mask = resolve_aspect_set(names)
    np.testing.assert_array_equal(np.where(mask)[0], expected_indices)

def test_resolve_index_list():
    mask = resolve_aspect_set([0, 4, 7, 9, 13])
    np.testing.assert_array_equal(mask, CLASSICAL)

def test_resolve_bool_mask_passthrough():
    custom = np.zeros(14, dtype=np.bool_)
    custom[[0, 7]] = True
    result = resolve_aspect_set(custom)
    np.testing.assert_array_equal(result, custom)

def test_resolve_wrong_length_mask_raises():
    with pytest.raises(ValueError, match="shape"):
        resolve_aspect_set(np.zeros(13, dtype=np.bool_))

def test_resolve_unknown_name_raises():
    with pytest.raises(ValueError, match="unknown aspect name"):
        resolve_aspect_set(["NotAnAspect"])

def test_resolve_out_of_range_index_raises():
    with pytest.raises(ValueError, match="out of range"):
        resolve_aspect_set([14])

def test_classical_is_frozen():
    """Defense against accidental mutation."""
    with pytest.raises(ValueError):
        CLASSICAL[0] = False
```

### Integration test pattern (ASP-07)

```python
# Source: proposed tests/test_aspect_presets.py — integration section
NON_CLASSICAL_INDICES = {1, 2, 3, 5, 6, 8, 10, 11, 12}  # Everything NOT in CLASSICAL

def test_calculate_aspects_classical_excludes_non_classical():
    from ketu.aspects import calculate_aspects
    from ketu.calculations import utc_to_julian
    from datetime import datetime, timezone
    jd = utc_to_julian(datetime(2025, 1, 1, tzinfo=timezone.utc))
    result = calculate_aspects(jd, aspects="classical")
    # Note: result["i_asp"] are canonical 0-13 indices; assert none is non-classical
    assert not any(int(i) in NON_CLASSICAL_INDICES for i in result["i_asp"])

# Repeat for calculate_aspects_vectorized, calculate_aspects_batch, etc.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Default = all 14 aspects (v0.4 → v1.0) | Default = CLASSICAL 5 (v1.1) | Phase 9 / v1.1.0 | Python API breaking change; CHANGELOG/UPGRADING.md must call out |
| Hardcoded `BIG_FIVE = [0, 60, 90, 120, 180]` (lunar_calendar.py:16) and `["Conjunction", ...]` lists (windows.py, timelines.py, transits.py) | Single source of truth: `CLASSICAL` preset | Phase 9 | Eliminates 4+ duplicated default lists; consistency guaranteed |
| `enumerate(aspects["angle"])` (loops 14 every time) | `enumerate(selected_indices)` after pre-filter | Phase 9 | ≥5% performance gain on CLASSICAL (5/14 ≈ 64% less inner-loop work); no impact on EXTENDED |

**Deprecated/outdated:**
- The phase brief mentions `ketu/aspect_windows.py` and `ketu/transits.py` as top-level modules. They DO NOT EXIST at those paths. The actual files are `ketu/aspects/windows.py` and `ketu/aspects/transits.py` (verified by `ls`). The CLAUDE.md project doc also still references the old paths (CLAUDE.md). This is a doc drift the planner should note but NOT fix as part of Phase 9 unless trivially in-scope.

## Open Questions

1. **Does Kala actually rely on `len(core.aspects) == 14`, or only on the row-order of names 0-13?**
   - What we know: STATE.md:53 and ROADMAP.md:33 say "Kala uses positional indexing"; the agreed contract is "append-only" (so future row 14, 15... are fine, but 0-13 are pinned). The blocker note STATE.md:87 explicitly flags "Kala aspect-count dependency unverified".
   - What's unclear: Does Kala do `aspects['name'][i_asp]` (only indexing, length-agnostic) or `aspects['name'][:14]` (count-pinned)?
   - Recommendation: Phase 9 should NOT lengthen `core.aspects`, only refactor around it. The append-only invariant is documented; future appends need a separate decision. The `KetuAdapter` audit is the user's pre-merge action item, not blocking research. The integration test (ASP-07) operationally confirms "Kala can opt into EXTENDED and get the same 14 aspects".

2. **Should `find_aspect_window` (single-aspect API) gain `aspects=` parameter?**
   - What we know: `find_aspect_window(body1, body2, aspect=...)` already takes a single aspect by name/index/angle (`windows.py:223`). It does NOT need an `aspects=` set parameter.
   - What's unclear: Whether ASP-03's "calculate_aspects(...) and friends" includes the windows/transits APIs. The literal text scopes ASP-03 to three calculator functions. ASP-07 ("all public aspect APIs") is broader.
   - Recommendation: Add `aspects=` (set) parameter to APIs that return MULTIPLE aspect types (`find_aspects_timeline`, `find_aspects_between_dates`, `find_transits_to_position`, `compare_dates_transits`, `generate_aspect_timeline`). Leave `find_aspect_window` single-aspect (it's a different shape). The planner can split this into two tasks if desired.

3. **Is the existing `tests/benchmark.py` reliable enough to define the v1.0 baseline?**
   - What we know: Raw `time.perf_counter` over 100 iterations with mean/std/median (`tests/benchmark.py:32-49`). pytest-benchmark NOT installed (verified `pyproject.toml:42-44`). Existing benchmark structure in `tests/test_aspects_vectorization.py:83+` runs benchmark functions via plain `pytest` (not skipped).
   - What's unclear: Is "v1.0 baseline" captured anywhere as numbers? The roadmap text "≤5% regression vs the v1.0 baseline" implies a baseline exists.
   - Recommendation: Capture the baseline AT THE START of Phase 9 implementation (run `tests/benchmark.py` and `tests/benchmark_aspect_window.py` on the v1.0 tag, save output to `.planning/phases/09-configurable-aspects/baseline-v1.0.json`). Compare end-of-phase. Or add a pytest test that runs both branches (with `aspects=EXTENDED`, the new code path should match v1.0 ±5%; with `aspects=CLASSICAL`, it should be FASTER). Adding pytest-benchmark is out-of-scope (no new dev deps requested).

4. **Where do the lunar_calendar `BIG_FIVE` integer-angle list and the new presets meet?**
   - What we know: `lunar_calendar.py:16` defines `BIG_FIVE = [0, 60, 90, 120, 180]` as ANGLES (not aspect names or indices). It's passed through to `find_aspect_window` per-angle in a loop (`lunar_calendar.py:309-336`).
   - What's unclear: Whether to delete `BIG_FIVE` and replace with `CLASSICAL` mask (semantically equivalent but different shape — angles vs. mask). The lunar_calendar consumer expects a list of angles.
   - Recommendation: Keep `BIG_FIVE` as-is (it's a list of integer angles for a different API style); document it as "equivalent to CLASSICAL preset" in a comment. Migration to preset is a separate cleanup, not in scope. Coverage gate (≥85%/module) is currently set on `coverage.run.omit` to skip `lunar_calendar.py` (`pyproject.toml:77`), so `BIG_FIVE` isn't on the critical path.

## Sources

### Primary (HIGH confidence)
- `ketu/core.py:84-103` — current `aspects` 14-row structured array; row order is the canonical aspect-index reference
- `ketu/aspects/calculator.py:73-265` — current `calculate_aspects`, `calculate_aspects_vectorized`, `calculate_aspects_batch` signatures and hot-loop structure (`calculator.py:143`, `calculator.py:239`)
- `ketu/aspects/core.py:41-67` — existing `get_aspect_index` resolver (str/int/float dispatch); pattern to extend
- `ketu/aspects/core.py:72-102` — existing LRU cache (`_cached_planet_position_batch`); does NOT depend on aspect_set, so cache key is unaffected
- `ketu/calculations.py:94-135` — existing `body_properties` LRU cache; same conclusion
- `ketu/aspects/windows.py:430-437` — hardcoded BIG_FIVE-equivalent default in `find_aspects_timeline`
- `ketu/aspects/timelines.py:398-399` — same pattern in `generate_aspect_timeline`
- `ketu/aspects/transits.py:304-305`, `transits.py:521-522` — same pattern in transit APIs
- `ketu/lunar_calendar.py:16` — `BIG_FIVE` integer-angle list (parallel namespace)
- `ketu/__init__.py:55-68` — top-level package exports (`bodies`, `aspects`, `signs`)
- `ketu/aspects/__init__.py:1-86` — subpackage exports; CLASSICAL/TRADITIONAL/EXTENDED must be added here per ASP-02 conventional placement
- `pyproject.toml:38-44` — runtime/test dependencies; no new deps allowed
- `pyproject.toml:90-110` — mypy strict configuration; new module must conform
- `tests/test_ketu.py:43-49` — existing aspects structure test (currently weak — see Pitfall 6)
- `tests/test_aspects_vectorization.py:8-80` — existing correctness test patterns to extend
- `tests/benchmark.py`, `tests/benchmark_aspect_window.py` — existing benchmark infrastructure (raw `time.perf_counter`)
- `.planning/REQUIREMENTS.md:11-20` — ASP-01 through ASP-08 verbatim
- `.planning/STATE.md:53,87` — append-only invariant + Kala blocker note
- `.planning/PROJECT.md:83` — h12 = "traditional 7" = CLASSICAL + semi-sextile + quincunx (canonical mapping confirmed)
- `.planning/ROADMAP.md:62-92` — phase 9 goal and success criteria

### Secondary (MEDIUM confidence)
- `.planning/codebase/INTEGRATIONS.md:134-138` — Kala consumes Ketu, no bidirectional comm; cross-repo contract is documented but Kala source not visible from this repo
- CLAUDE.md project file — references `aspect_windows.py` and `transits.py` at top-level; OUTDATED (verified files are in `ketu/aspects/`). Doc drift; not blocking.

### Tertiary (LOW confidence)
- None — phase is fully grounded in existing codebase. No external library research required (no new deps).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — pure NumPy + stdlib, all primitives already in repo
- Architecture: HIGH — pattern is clean composition of existing primitives; `presets.py` is a new sibling module of established structure
- Pitfalls: HIGH — 7 codebase-grounded pitfalls, each with specific file:line warning signs
- Cross-repo (Kala) contract: MEDIUM — confirmed by planning docs but Kala source not in this repo. Mitigated by integration test ASP-07 ("test from Ketu's side that EXTENDED behaves like v1.0").
- Benchmark methodology: MEDIUM — existing scripts work but pytest-benchmark not installed; baseline capture is a one-shot manual step, not a CI fixture.

**Research date:** 2026-05-06
**Valid until:** 2026-06-06 (30 days; codebase is stable, no fast-moving deps)

---

## RESEARCH COMPLETE

**Phase:** 9 - Configurable Aspects
**Confidence:** HIGH

### Key Findings
- `ketu/aspects/` subpackage already exists; add `presets.py` as a sibling of `calculator.py`/`windows.py`/`timelines.py`/`transits.py`. No need to relocate `core.aspects`.
- CLASSICAL/TRADITIONAL/EXTENDED canonical mapping = indices `[0,4,7,9,13]` / `[0,1,4,7,9,11,13]` / `[0..13]` of `core.aspects` (verified from `core.py:84-103`).
- Only TWO LRU caches exist (`calculations.py:94`, `aspects/core.py:72`); neither depends on aspect filtering, so ASP-06 is satisfied without modifying any cache key today. Document the rule for future caches.
- `i_asp` field in result dtypes is the load-bearing Kala contract: it must remain a canonical 0-13 index into `core.aspects`, NOT a position-within-filtered-subset. Hot-loop refactor must emit `selected_indices[k]`, not `k`.
- Hardcoded `["Conjunction", "Sextile", "Square", "Trine", "Opposition"]` lists exist in 4+ places (`windows.py:431`, `timelines.py:398`, `transits.py:304`, `transits.py:521`) and `BIG_FIVE = [0, 60, 90, 120, 180]` in `lunar_calendar.py:16` — at minimum the four in the `aspects/` package should migrate to `CLASSICAL`; `lunar_calendar.py` is coverage-omitted and can stay as-is.
- pytest-benchmark is NOT a dependency. Benchmark methodology = capture v1.0 baseline manually via existing `tests/benchmark*.py` scripts before refactor begins; assert ≤5% regression at end of phase.

### File Created
`/home/loc/workspace/ketu/.planning/phases/09-configurable-aspects/09-RESEARCH.md`

### Confidence Assessment
| Area | Level | Reason |
|------|-------|--------|
| Standard Stack | HIGH | Pure NumPy + stdlib; nothing new |
| Architecture | HIGH | Composition of established codebase primitives, single new file |
| Pitfalls | HIGH | 7 pitfalls, each with file:line evidence and warning-sign tests |
| Kala contract | MEDIUM | Confirmed in planning docs; Kala source not in-repo. Mitigated by ASP-07 integration test from Ketu's side |
| Benchmark methodology | MEDIUM | Existing scripts adequate; baseline-capture is manual, one-shot |

### Open Questions
1. Does Kala depend on `len(core.aspects) == 14` or only row-order 0-13? (Append-only invariant resolves either way; user has the Kala-maintainer ping as pre-merge action.)
2. Should `find_aspect_window` (single-aspect API) gain `aspects=` set parameter? Recommendation: NO — it's per-aspect, not per-set.
3. Where is the v1.0 baseline captured? Recommendation: capture at start of phase via existing `tests/benchmark*.py`, save to `baseline-v1.0.json` in phase dir.
4. Migrate `lunar_calendar.BIG_FIVE` to `CLASSICAL`? Recommendation: NO (coverage-omitted, separate concern).

### Ready for Planning
Research complete. Planner can now create PLAN.md files with confidence in stack, file layout, hot-loop refactor pattern, invariant test design, and integration-test scope.
