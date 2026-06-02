# Phase 28: Dynamic Harmonic Generator + Detection Integration - Research

**Researched:** 2026-06-03
**Domain:** NumPy structured arrays, aspect detection pipeline, Python harmonic geometry
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Generator form & API `generate_harmonic_aspects(h)`**
- Dtype de retour identique à `core.aspects` : `[name S16, angle f4, coef f4, harmonic i4, symbol U4]`. Drop-in : consommable partout où `core.aspects` l'est.
- Nommage synthétique `H{h}-{k}` dans `name` (ex. `H7-1`, `H7-2`, `H7-3`). Déterministe, sans collision.
- Symbole vide (`U4` blanc) pour toutes les lignes dynamiques — même convention que les minors actuels.
- Champ `harmonic` = h ; le rang `k` encodé dans `name` (pas de colonne `k` séparée).
- Convention 360° verrouillée : angles `fold_to_0_180(k·360/h)` pour `k=1..h//2`, `coef=k/h`, paires miroir dédupliquées, 0°/360° JAMAIS émis. Déterministe.
- Validation de `h` → Claude's Discretion (borne min/max).

**Intégration `dynamic_specs`**
- Nom de paramètre uniforme : `dynamic_specs` sur `calculate_aspects`, `calculate_aspects_vectorized`, `calculate_aspects_batch`, `find_aspects_between_dates`, `calculate_synastry`, et la chaîne cycles.
- Combinables en union : `aspects=` (preset/mask table) ET `dynamic_specs=` coexistent. Sortie = aspects table + aspects dynamiques.
- Ordre de détection : statique d'abord (table 0-13), puis dynamique (ordre du spec). First-match-wins préservé : une seule ligne par paire `(body1,body2)`.
- Orbe dynamique : `(orb_b1 + orb_b2) / 2 × coef`, `coef = k/h`. Orbes full-circle ~2× plus petits ACCEPTÉS (décision v1.4 verrouillée, pas d'unification).
- Sentinelle `i_asp = -2` pour toutes les lignes dynamiques dans la sortie de `calculate_aspects` (dtype de sortie `(body1, body2, i_asp, orb)` inchangé).

**Identité & ré-identification**
- Sortie `calculate_aspects` : `i_asp = -2` marque dynamique. Ré-identification via l'orbe signé recroisé avec ses propres `dynamic_specs`. Pas de nouveau champ.
- `find_aspects_between_dates` (tuples `(jdate, b1, b2, aspect_name, aspect_value)`) : pour un angle dynamique off-table, retourner le name synthétique du spec (`H7-1`), pas un crash.
- `find_aspect_timing` : ajouter un paramètre `coef`/orbe explicite optionnel pour les angles dynamiques. Si absent ET angle off-table → ValueError clair (jamais IndexError).
- Guards IndexError OBLIGATOIRES (ship cette phase) : `find_aspect_timing:427` et `find_aspects_between_dates:534` font `np.where(_CORE_ASPECTS["angle"] == …)[0]` et crashent sur un angle dynamique.

**Périmètre & ergonomie**
- API-seule — PAS de CLI. `dynamic_specs` exposé uniquement via l'API Python.
- Cycles : requis — `dynamic_specs` câblé dans `generate_cycle_series` / la chaîne cycles.
- Synastry : requis — `calculate_synastry` avec `dynamic_specs` retourne des lignes en `SYNASTRY_DTYPE`, orbe `_BODY_ORBS_16` × coef.
- Doctests : générateur + bout-en-bout, calibrés pour le gate doctest 100% sans fragilité float.

### Claude's Discretion
- Validation exacte de `h` (bornes min/max, h=1).
- Forme interne du paramètre orbe de `find_aspect_timing` (`coef` vs `orb` direct).
- Implémentation vectorisée précise du chemin dynamique (zéro boucle Python en hot path).
- Calibrage exact des doctests.

### Deferred Ideas (OUT OF SCOPE)
- Flag CLI `--harmonic N`.
- Champ `k` explicite / champ angle dans la sortie de `calculate_aspects`.
- Unification d'orbe full-circle (REJETÉ pour v1.4).
</user_constraints>

---

## Summary

Phase 28 adds a parallel dynamic aspect path alongside the frozen 14-row `core.aspects` table. The core challenge is not the generator itself (a few lines of NumPy arithmetic) but correct wiring through five distinct detection surfaces — `calculate_aspects` (scalar, vectorised, batch), `find_aspects_between_dates`, `find_aspect_timing`, `calculate_synastry`, and `generate_cycle_series` — each of which must apply first-match-wins ordering (static first, dynamic second) while keeping the dtype contracts Kala depends on intact.

Two existing functions contain literal `IndexError` traps on dynamic angles: `find_aspect_timing` at line 427 (bare `np.where(...)[0]` + `[0]` subscript) and `find_aspects_between_dates` at line 534 (same pattern). These must be guarded before dynamic angles can flow through the pipeline. All other integration points extend existing patterns cleanly, since the static path already does first-match-wins bookkeeping via `matched_pairs` sets.

The `core.aspects` table, its dtype, and both sha256 fingerprints (V1 `c5bd177...`, V13 `3258530...`) must remain bit-identical. `generate_harmonic_aspects(h)` produces a separate structured array with the same dtype shape — it is never concatenated into or mutated into `core.aspects`.

**Primary recommendation:** Implement `generate_harmonic_aspects(h)` in `ketu/aspects/presets.py` (or a new `ketu/aspects/harmonics.py`), expose `DynamicAspectSpec` (the type alias for the `dynamic_specs=` parameter), and thread it through all five surfaces following the exact same resolver-before-hot-loop pattern already used by `resolve_aspect_set`.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| numpy | ≥1.20.0 | Structured arrays, vectorised ops | Project-wide dependency; CYCLE_DTYPE / SYNASTRY_DTYPE already use it |

No new dependencies. The entire implementation is pure NumPy structured-array operations on the existing data model.

### Architecture Locations
| File | Role in Phase 28 |
|------|-----------------|
| `ketu/aspects/presets.py` (or new `ketu/aspects/harmonics.py`) | `generate_harmonic_aspects(h)`, `DynamicAspectSpec` type alias, `_fold_to_0_180` helper |
| `ketu/aspects/calculator.py` | Add `dynamic_specs=None` to `calculate_aspects`, `calculate_aspects_vectorized`, `calculate_aspects_batch`, `find_aspect_timing`, `find_aspects_between_dates` |
| `ketu/synastry/api.py` | Add `dynamic_specs=None` to `calculate_synastry` |
| `ketu/cycles/calculator.py` | Add `dynamic_specs=None` to `generate_cycle_series` (propagate to in_aspect / aspect_orb) |
| `ketu/aspects/__init__.py` | Export `generate_harmonic_aspects`, `DynamicAspectSpec` |
| `tests/test_dynamic_harmonics.py` | New test file; 100% coverage gate applies immediately |

---

## Architecture Patterns

### `generate_harmonic_aspects(h)` — the generator

**Geometry — fold_to_0_180:**
The convention `fold_to_0_180(angle)` means: `min(angle % 360, 360 - angle % 360)`. For `k·360/h` this reduces to `min(k*360/h, 360 - k*360/h)` which equals `k*360/h` when `k < h/2`, and `360 - k*360/h` when `k > h/2`. Mirror deduplication: since `fold_to_0_180(k*360/h) == fold_to_0_180((h-k)*360/h)`, only iterate `k = 1..h//2`. The 0° angle (k=0 or k=h) is never emitted because k starts at 1 and `h//2` stops before k=h.

Edge cases to verify:
- `h=2`: k=1 → angle=180°. The loop `k=1..1` produces only Opposition. Correct, but note `coef=1/2` differs from the static Opposition at `coef=1`. This is acceptable per the locked 360° convention (coef = k/h).
- `h=4`: k=1→90°, k=2→180°. Two rows. `coef=0.25` and `coef=0.5`.
- Even `h`: `k = h//2` gives angle=180°, which is valid (never 0°/360°).
- Odd `h` (e.g. h=7): k=1..3, angles ≈51.4°, 102.9°, 154.3°. Never hits 0° or 180° exactly.

```python
# Source: derived from ketu/core.py dtype and locked CONTEXT.md convention
import numpy as np

HARMONIC_DTYPE = np.dtype([
    ("name", "S16"), ("angle", "f4"), ("coef", "f4"), ("harmonic", "i4"), ("symbol", "U4")
])

def _fold_to_0_180(angle_deg: float) -> float:
    a = angle_deg % 360.0
    return a if a <= 180.0 else 360.0 - a

def generate_harmonic_aspects(h: int) -> np.ndarray:
    # validation: h must be int >= 2 (or >=3), see Claude's Discretion
    rows = []
    for k in range(1, h // 2 + 1):
        angle = _fold_to_0_180(k * 360.0 / h)
        coef = k / h
        name = f"H{h}-{k}".encode()  # S16 stores bytes
        rows.append((name, angle, coef, h, ""))
    return np.array(rows, dtype=HARMONIC_DTYPE)
```

**Confidence:** HIGH — the dtype is read directly from `ketu/core.py:113`; the S16/f4/f4/i4/U4 field order and types are exact.

### `calculate_aspects` (scalar) — dynamic path

The static path (lines 128-151, `ketu/aspects/calculator.py`) uses:
1. `resolve_aspect_set(aspects)` → 14-bool mask
2. Extract `selected_indices`, `selected_angles`, `selected_coefs`
3. `for b1, b2 in combs(bodies_id, 2)`: compute `dist`, then `for k, i_asp in enumerate(selected_indices)`: orb = `(orb[b1] + orb[b2]) / 2 * coef`, check distance, first-match-wins `break`.
4. Emit `(b1, b2, i_asp, orb)` with canonical `i_asp` 0-13.

**Dynamic extension:**
```python
# After the static inner loop (break or exhausted), if no break occurred:
if dynamic_specs is not None and pair_not_matched:
    for dyn_row in dynamic_specs:  # iterate numpy structured array rows
        dyn_angle = float(dyn_row["angle"])
        dyn_coef = float(dyn_row["coef"])
        dyn_orb = (orb_b1 + orb_b2) / 2 * dyn_coef
        if abs(dist - dyn_angle) <= dyn_orb:
            aspects_data.append((int(b1), int(b2), -2, float(dyn_angle - dist)))
            break  # first-match-wins on dynamic too
```

Sentinel `i_asp = -2` fits in `i4` dtype. The orb value convention mirrors the static path: `aspect_angle - dist` (signed, matches existing sign convention already documented in the code).

### `calculate_aspects_vectorized` — dynamic path

The vectorised path (lines 228-261) iterates `for k, i_asp_val in enumerate(selected_indices)` and uses a `matched_pairs` set to enforce first-match-wins. The dynamic extension runs AFTER the static loop completes:

```python
# After the for loop over selected_indices:
if dynamic_specs is not None:
    for dyn_row in dynamic_specs:  # outer loop over spec rows (NOT per-pair)
        dyn_angle = float(dyn_row["angle"])
        dyn_coef  = float(dyn_row["coef"])
        orbs = (orbs_body1 + orbs_body2) / 2 * dyn_coef  # shape (n_pairs,)
        in_orb = (
            (np.abs(all_distances - dyn_angle) <= orbs)
            & np.array([(body1_ids[i], body2_ids[i]) not in matched_pairs
                        for i in range(len(body1_ids))], dtype=bool)
        )
        # ... collect, emit i_asp = -2, update matched_pairs
```

**Important:** The `matched_pairs` set check cannot be vectorised as-is using pure NumPy without building an auxiliary boolean mask. The pattern above uses a list comprehension fallback for the matched_pairs check which is acceptable since the dynamic spec rows are few (h//2 max rows per harmonic, typically small h). For a zero-Python-loop-in-hot-path approach, an auxiliary boolean array `already_matched` (shape `n_pairs`) is preferable — update it alongside `matched_pairs` during the static loop.

**Refactor note:** The existing `matched_pairs` set is already used in the vectorised path at lines 255-261. Adding `already_matched = np.zeros(n_pairs, dtype=bool)` alongside it and updating both simultaneously is the cleanest approach to allow vectorised dynamic detection.

### `calculate_aspects_batch` — dynamic path

Analogous to the vectorised path. The per-date loop at line 367 must propagate `dynamic_specs` down into the inner aspect loop. Since `dynamic_specs` is date-independent (same spec rows for all dates), hoist dynamic coef/angle extraction above the per-date loop — matching the existing pattern for `selected_orbs_per_aspect` (line 363).

### `find_aspect_timing` — IndexError guard (MANDATORY)

**Current code (lines 427-430):**
```python
asp_idx = np.where(_CORE_ASPECTS["angle"] == aspect_value)[0]
if len(asp_idx) == 0:
    raise ValueError(f"unknown aspect value: {aspect_value}")
asp_idx = asp_idx[0]
orb = get_orb(body1, body2, asp_idx)
```

The guard `if len(asp_idx) == 0` raises ValueError — correct for truly unknown angles. But for a **dynamic angle** (which IS a valid angle, just off-table), this ValueError is wrong too.

**Fixed signature (locked: `coef` or `orb` explicit parameter):**
```python
def find_aspect_timing(
    jdate: float,
    body1: int,
    body2: int,
    aspect_value: float,
    orb: Optional[float] = None,
) -> Tuple[float, float, float]:
```

Logic:
- If `orb` is provided explicitly → use it directly (dynamic path, no table lookup needed).
- If `orb` is None → table lookup; if angle not in table → `ValueError` (same current behaviour for truly unknown static angles).

This avoids adding `coef` as a parameter (coef alone would require the body orbs to compute the actual orb value). Passing `orb` directly is simpler and already the right granularity.

### `find_aspects_between_dates` — IndexError guard (MANDATORY)

**Current crash site (line 534):**
```python
asp_idx = np.where(_CORE_ASPECTS["angle"] == aspect_angle)[0][0]  # IndexError if off-table
aspect_name_bytes = _CORE_ASPECTS["name"][asp_idx]
```

This code is reached when `find_all_aspects` returns `(exact_jd, aspect_angle)` tuples. For static aspects, `aspect_angle` is always in `_CORE_ASPECTS["angle"]`. For dynamic angles (passed via `dynamic_specs`), it is not.

**Required change:** The function needs a `dynamic_specs=None` parameter. When dynamic specs are present, `find_all_aspects` should be called with the union of static selected_angles + dynamic angles. Then the name-lookup at line 534 must:
1. First check `_CORE_ASPECTS["angle"] == aspect_angle` (static).
2. If not found, search `dynamic_specs["angle"] == aspect_angle` to retrieve the synthetic name.
3. Return the synthetic name (e.g. `"H7-1"`) instead of crashing.

```python
# Guard pattern:
asp_idx = np.where(_CORE_ASPECTS["angle"] == aspect_angle)[0]
if len(asp_idx) > 0:
    aspect_name = _CORE_ASPECTS["name"][asp_idx[0]].decode()
elif dynamic_specs is not None:
    dyn_idx = np.where(dynamic_specs["angle"] == aspect_angle)[0]
    if len(dyn_idx) > 0:
        aspect_name = dynamic_specs["name"][dyn_idx[0]].decode()
    else:
        aspect_name = f"{aspect_angle:.4f}°"  # fallback (should not happen)
else:
    aspect_name = f"{aspect_angle:.4f}°"  # unreachable if well-formed call
```

**Confidence:** HIGH — line numbers verified from reading `ketu/aspects/calculator.py`.

### `calculate_synastry` — dynamic path

**Current code (lines 286-329, `ketu/synastry/api.py`):** Iterates `for i_asp in selected_indices`, resolves `ang` and `coef` from `_ASPECTS`, computes per-pair `orbs_pair = (_BODY_ORBS_16[i_flat] + _BODY_ORBS_16[j_flat]) / 2.0 * coef * factor`, uses `in_orb` boolean mask, updates `matched` set.

**Dynamic extension:**
- After the static aspect loop, if `dynamic_specs is not None`, run a second loop over `dynamic_specs` rows.
- For each dynamic row: `dyn_ang = float(dyn_row["angle"])`, `dyn_coef = float(dyn_row["coef"])`, `orbs_pair = (_BODY_ORBS_16[i_flat] + _BODY_ORBS_16[j_flat]) / 2.0 * dyn_coef * factor`.
- `in_orb = (np.abs(dist - dyn_ang) <= orbs_pair) & (~matched)` (0° conjunction check may need special case if `dyn_ang == 0`, but per the generator convention 0° is never emitted).
- Emit with `aspect_type = -2` (dynamic sentinel) — note: `aspect_type` in SYNASTRY_DTYPE is `i1` (int8, range -128..127), so -2 fits.
- Update `out["aspect_type"]`, `out["orb"]`, `out["applying"]`, `out["orb_limit"]`, `matched |= in_orb`.

**Key difference from `calculate_aspects`:** The synastry path uses `aspect_type` field (not `i_asp`) and the dtype is `i1` not `i4`. `-2` fits in `i1`.

### `generate_cycle_series` — dynamic path

The cycles module uses a different aspect proximity mechanism (lines 282-318, `ketu/cycles/calculator.py`). It computes `nearest_aspect` and `in_aspect` against `MAJOR_ASPECTS = [0, 60, 90, 120, 180, 240, 270, 300, 360]` using complex number arithmetic — not the `_CORE_ASPECTS` table at all.

**Implication:** The cycles integration for dynamic aspects is NOT about reusing the same lookup. It means: when `dynamic_specs` is passed, add the dynamic aspect angles to the candidate list for `nearest_aspect` / `in_aspect` computation. The complex-distance matrix (`dist_matrix_deg` at line 285) already handles arbitrary angles — just extend `MAJOR_ASPECTS` / `MAJOR_ASPECTS_Z` with the dynamic angles for that call.

**Implementation sketch:**
```python
if dynamic_specs is not None:
    dyn_angles = dynamic_specs["angle"].astype(np.float32)  # shape (n_dyn,)
    effective_aspects = np.concatenate([MAJOR_ASPECTS, dyn_angles])
    # Recompute MAJOR_ASPECTS_Z-equivalent for the extended set
    effective_aspects_z = degrees_to_complex(effective_aspects)
    # Use effective_aspects* instead of MAJOR_ASPECTS* in the matrix
```

The `COEFFS` array (line 310) will need to be extended for dynamic angles — use `dyn_coef` values from `dynamic_specs["coef"]`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Angle folding to [0,180] | Custom modulo | `min(a % 360, 360 - a % 360)` — one-liner | Exact, no off-by-one at 180° |
| First-match-wins tracking | Custom visited dict | Extend existing `matched_pairs` set (scalar) or `already_matched` bool array (vectorised) | Already in the codebase |
| Orb computation for dynamic | Custom formula | Same formula as static: `(orb_b1 + orb_b2) / 2 * coef` | Single source of truth at `get_orb` |
| Dynamic name → bytes for S16 | Custom encoding | `f"H{h}-{k}".encode()` → stored in S16 field | Matches existing `S16` dtype |

---

## Common Pitfalls

### Pitfall 1: Mutating `core.aspects`
**What goes wrong:** Generator accidentally writes into or concatenates to `core.aspects`.
**Why it happens:** `np.concatenate([core.aspects, dynamic_array])` changes the object reference or the sha256 fingerprints.
**How to avoid:** `generate_harmonic_aspects(h)` returns a freshly allocated array. Never import and modify `core.aspects`. The sha256 test at `tests/test_ketu.py:189` will catch this.

### Pitfall 2: `i1` overflow in SYNASTRY_DTYPE
**What goes wrong:** Using `i_asp = -2` in synastry but forgetting `aspect_type` is `i1` (int8), not `i4`.
**Why it happens:** The dynamic sentinel in `calculate_aspects` output uses `i_asp = -2` in an `i4` field. The synastry output uses `aspect_type` in an `i1` field. Both -2 values fit in int8 (range -128..127). But if you accidentally write a larger sentinel (e.g. -100), no error is raised — silent truncation.
**How to avoid:** Consistently use -2 for the dynamic sentinel; document both sentinels (-1 = "no aspect" in synastry dense mode; -2 = "dynamic aspect" in both).

### Pitfall 3: `_VALID_HARMONICS` gate on dynamic path
**What goes wrong:** `generate_harmonic_aspects(h)` calling `aspects_for_harmonics([h])` which raises `ValueError` for h=7, h=11, etc.
**Why it happens:** `aspects_for_harmonics` validates against `_VALID_HARMONICS = frozenset({1, 2, 3, 5, 6, 9, 10})`. H7 is not in this set.
**How to avoid:** `generate_harmonic_aspects` must NOT call `aspects_for_harmonics`. It is an entirely independent function. `_VALID_HARMONICS` / `aspects_for_harmonics` remain untouched.

### Pitfall 4: Float equality in `find_aspects_between_dates` guard
**What goes wrong:** `np.where(dynamic_specs["angle"] == aspect_angle)[0]` finds no match because `f4` float from `find_all_aspects` result doesn't exactly equal the `f4` stored in `dynamic_specs`.
**Why it happens:** `find_all_aspects` returns `(exact_jd, aspect_angle)` where `aspect_angle` is the input value passed to `find_exact_aspect` — which came from `list(selected_angles + dynamic_angles)`. If that list was built from `np.float64` converted to Python float, and `dynamic_specs["angle"]` is `f4`, precision may differ.
**How to avoid:** Store dynamic angles as `f4` consistently; build the search list from `dynamic_specs["angle"].tolist()` (returns Python floats from the f4 array). Comparison: `np.isclose(dynamic_specs["angle"], aspect_angle, atol=1e-4)` as fallback, or use `f4` cast at call site.

### Pitfall 5: `compute_doctest` fragility on float repr
**What goes wrong:** A doctest like `>>> float(specs['angle'][0])` prints `51.42857360839844` instead of `51.42857142857143`.
**Why it happens:** `f4` float (32-bit) truncates precision. `f8` would give more digits.
**How to avoid:** Use `round()` in doctests: `>>> round(float(specs['angle'][0]), 2)` gives `51.43`. Or use `int(specs['angle'][0] * 100) / 100`. The gate doctest at `make doctest` uses `NORMALIZE_WHITESPACE + ELLIPSIS` options (verified in `pyproject.toml:88`).

### Pitfall 6: `already_matched` vs `matched_pairs` in vectorised path
**What goes wrong:** Switching from `matched_pairs` (a Python set of tuples) to `already_matched` (a NumPy bool array) for vectorised dynamic detection, but not keeping them in sync.
**Why it happens:** The static path uses `matched_pairs` set. Adding a parallel `already_matched` numpy array requires updating both at each match.
**How to avoid:** Either (a) keep `matched_pairs` only and use a list comprehension for the dynamic exclusion mask (simpler, acceptable for small dynamic specs), or (b) add `already_matched = np.zeros(n_pairs, dtype=bool)` and `already_matched[pair_indices] = True` whenever `matched_pairs.add(pair)` is called.

### Pitfall 7: Doctest gate breaks for `generate_cycle_series` with `dynamic_specs`
**What goes wrong:** The existing `generate_cycle_series` doctest asserts `cycles.dtype.names[:3]` — safe. But adding a new `dynamic_specs` parameter that changes `in_aspect` / `aspect_orb` calculations might break oracle-style tests.
**Why it happens:** `in_aspect` and `aspect_orb` in `CYCLE_DTYPE` are computed against `MAJOR_ASPECTS`. If dynamic angles alter these without test updates, existing tests fail.
**How to avoid:** When `dynamic_specs is None`, the computation is identical to the current implementation — no change. Dynamic path is purely additive.

---

## Code Examples

### `generate_harmonic_aspects(h)` — verified dtype

```python
# Source: ketu/core.py:113 — dtype exactly:
# dtype=[("name", "S16"), ("angle", "f4"), ("coef", "f4"), ("harmonic", "i4"), ("symbol", "U4")]
#
# For H7: k=1,2,3 → angles ≈ 51.43°, 102.86°, 154.29°; coef = 1/7, 2/7, 3/7
>>> specs = generate_harmonic_aspects(7)
>>> len(specs)
3
>>> specs.dtype.names
('name', 'angle', 'coef', 'harmonic', 'symbol')
>>> specs['name'][0]
b'H7-1'
>>> round(float(specs['angle'][0]), 2)
51.43
>>> round(float(specs['coef'][0]), 4)
0.1429
>>> int(specs['harmonic'][0])
7
>>> specs['symbol'][0]
''
```

### `calculate_aspects` with `dynamic_specs` — static-then-dynamic ordering

```python
# Source: ketu/aspects/calculator.py — existing loop structure
# Static loop: for k, i_asp in enumerate(selected_indices): ... break (first-match)
# Dynamic extension (after static exhausted for this pair):
# for dyn_row in dynamic_specs: check orb, emit (b1, b2, -2, orb_val), break

# Result dtype unchanged:
# np.dtype([("body1", "i4"), ("body2", "i4"), ("i_asp", "i4"), ("orb", "f4")])
# Dynamic rows have i_asp = -2.
```

### `calculate_synastry` — orb formula for dynamic specs

```python
# Source: ketu/synastry/api.py:294-298 — existing static formula:
# orbs_pair = (_BODY_ORBS_16[i_flat] + _BODY_ORBS_16[j_flat]) / 2.0 * coef * factor
# Dynamic formula: identical, coef = dyn_row["coef"], factor from resolve_orb_set
# SYNASTRY_DTYPE.aspect_type is i1; sentinel -2 fits (range -128..127).
```

### `find_aspect_timing` — guarded signature

```python
# Source: ketu/aspects/calculator.py:406-430 — current vulnerable code:
# asp_idx = np.where(_CORE_ASPECTS["angle"] == aspect_value)[0]
# if len(asp_idx) == 0: raise ValueError(...)
# asp_idx = asp_idx[0]
# orb = get_orb(body1, body2, asp_idx)
#
# Fixed: add optional `orb: Optional[float] = None` parameter.
# When orb is provided, skip the table lookup entirely.
# When orb is None and angle is off-table: raise ValueError (unchanged).
```

### `find_aspects_between_dates` — guarded name resolution

```python
# Source: ketu/aspects/calculator.py:530-538 — current vulnerable code:
# asp_idx = np.where(_CORE_ASPECTS["angle"] == aspect_angle)[0][0]  # IndexError
# aspect_name_bytes = _CORE_ASPECTS["name"][asp_idx]
#
# Fixed: check len(np.where(...)[0]) first; if 0 and dynamic_specs provided,
# search dynamic_specs["angle"] for the name.
```

### sha256 fingerprint protection — what NOT to do

```python
# Source: tests/test_ketu.py:189-213
# V1 fingerprint: sha256(aspects["name"].tobytes()
#                       + aspects["angle"].tobytes()
#                       + aspects["coef"].tobytes())
# V13 fingerprint: adds aspects["harmonic"].tobytes() + aspects["symbol"].tobytes()
#
# generate_harmonic_aspects() must NEVER modify ketu.core.aspects.
# The test will catch any mutation because bytes change.
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Direct `aspects["angle"]` table lookup | `resolve_aspect_set` resolver pattern | Phase 9 | Dynamic angles can bypass the resolver |
| 13-body array | 14-body array (Chiron at index 13) | Phase 24 | `_BODY_ORBS_16` already includes Chiron at index 13 |
| `aspects_for_harmonics` with `_VALID_HARMONICS` gate | Unchanged — NOT on dynamic path | Phase 26 | Dynamic generator is independent |

---

## Open Questions

1. **Validation bounds for `h` — Claude's Discretion**
   - What we know: `h=1` would produce no rows (loop `k=1..0` is empty). `h=2` produces 1 row (180°, same as Opposition but coef=0.5). `h >= 2` is the minimum sensible value. Upper bound: Python/NumPy can handle any h; the concern is usability (h=1000 produces 500 rows).
   - Recommendation: Validate `h >= 2` (h=1 is a degenerate case — the "unison" — produces no aspects). Set an upper bound of `h <= 64` or `h <= 128` as a practical limit. Raise `ValueError` with a clear message for out-of-range values.

2. **`dynamic_specs` type alias — what exactly is the expected type?**
   - What we know: Locked as "a structured array with the same dtype as `core.aspects`". `generate_harmonic_aspects(h)` returns exactly this.
   - What's unclear: Should `dynamic_specs` accept a list of such arrays (for combining multiple harmonics), or a single array only?
   - Recommendation: Accept either a single `np.ndarray` with the correct dtype or a list of such arrays (concatenate at the start of each consumer function). This matches how `aspects=` accepts various forms. Name the type alias `DynamicAspectSpec = Optional[Union[np.ndarray, List[np.ndarray]]]`.

3. **`find_aspects_between_dates` — float equality for dynamic angle name lookup**
   - What we know: `find_all_aspects` in `ketu/ephemeris/planets.py:519` receives a Python `list` of aspect angles, steps through time, and returns `(exact_jd, aspect_angle)` where `aspect_angle` is the original input value from the list.
   - What's unclear: If the list is built from `np.float64` but `dynamic_specs["angle"]` is `f4`, equality check may fail.
   - Recommendation: Build the `all_angles` list using `dynamic_specs["angle"].tolist()` (returns Python floats from f4 values). Then the round-trip through `find_all_aspects` preserves the same float value. Verify with an exact equality test.

4. **`generate_cycle_series` COEFFS extension for dynamic angles**
   - What we know: The current `COEFFS` array (line 310) is hardcoded for the 9 MAJOR_ASPECTS entries. Adding dynamic angles requires extending COEFFS.
   - Recommendation: Use `dyn_row["coef"]` from `dynamic_specs` directly as the orb coefficient for dynamic angles in the cycle proximity computation. Concatenate the coefficient array at call time when `dynamic_specs is not None`.

---

## Sources

### Primary (HIGH confidence)
- `ketu/core.py` — exact dtype of `core.aspects`: `[("name", "S16"), ("angle", "f4"), ("coef", "f4"), ("harmonic", "i4"), ("symbol", "U4")]`; all 14 rows with names, angles, coefs, harmonics, symbols
- `ketu/aspects/calculator.py` — exact signatures of `calculate_aspects`, `calculate_aspects_vectorized`, `calculate_aspects_batch`, `find_aspect_timing` (with the IndexError at line 427), `find_aspects_between_dates` (with the IndexError at line 534)
- `ketu/aspects/presets.py` — `_VALID_HARMONICS`, `aspects_for_harmonics`, `resolve_aspect_set`; confirmed that `_VALID_HARMONICS = frozenset({1, 2, 3, 5, 6, 9, 10})` and that H7/H11/H17 raise ValueError
- `ketu/synastry/api.py` — `calculate_synastry` full implementation; `_BODY_ORBS_16` usage; `SYNASTRY_DTYPE` with `aspect_type: i1` (confirmed -2 fits)
- `ketu/synastry/orbs.py` — `_BODY_ORBS_16`, `synastry_orb_limit` formula, `SYNASTRY_FACTOR = 0.5`
- `ketu/cycles/calculator.py` — `generate_cycle_series`, `MAJOR_ASPECTS`, `COEFFS` array; the complex-number path that computes `in_aspect` / `aspect_orb`
- `tests/test_ketu.py:189-213` — exact sha256 fingerprint test; V1 = `c5bd177...`, V13 = `3258530...`; hashes over `aspects["name"] + aspects["angle"] + aspects["coef"]` (V1) plus `harmonics + symbol` (V13)
- `pyproject.toml` — `fail_under = 100`, `doctest_optionflags = ["ELLIPSIS", "NORMALIZE_WHITESPACE"]`, `make doctest` target uses `--doctest-modules ketu/ --no-cov`

### Secondary (MEDIUM confidence)
- `ketu/ephemeris/planets.py:519` — `find_all_aspects` signature confirms the round-trip of `aspect_angle` through the function: accepts a list, returns the same values from the list (no recomputation of angle). This means the name-lookup float equality will hold if the list is built from `dynamic_specs["angle"].tolist()`.

---

## Metadata

**Confidence breakdown:**
- Generator geometry: HIGH — derived from ketu/core.py dtype and mathematical identity of fold_to_0_180
- Static path mechanics: HIGH — all four detection surfaces read directly from source
- IndexError sites: HIGH — exact line numbers and code verified by reading calculator.py
- Synastry orb formula: HIGH — read directly from synastry/api.py and orbs.py
- Cycles integration: HIGH — read directly from cycles/calculator.py
- sha256 fingerprints: HIGH — test code and constants read directly
- Coverage/doctest gate: HIGH — pyproject.toml and Makefile read directly

**Research date:** 2026-06-03
**Valid until:** 2026-07-03 (stable codebase, no external deps)
