# Architecture: v1.4 Feature Integration into Ketu

**Project:** Ketu v1.4
**Researched:** 2026-06-02
**Scope:** Dynamic harmonics + Chiron orb 4° + Chiron range 1900-2100

---

## Summary

Two independent feature groups. Group A is architecturally novel (new data representation, detection-loop seam). Group B is a constant change that propagates automatically through the existing orb formula plumbing, but breaks several pinned-value tests.

**Group A — Dynamic harmonic aspects:** The frozen 14-row `core.aspects` table and its bool[14] mask system cannot represent arbitrary harmonics (H7, H11, H13, H17, etc.) because those angles are not rows in the table. The detection loop in `calculate_aspects` / `calculate_aspects_vectorized` / `calculate_aspects_batch` already iterates over `(angle, coef)` tuples extracted from the table — the natural seam is to allow that same loop to accept externally-supplied `(angle, coef)` tuples that were never in the table. The mask path and the dynamic path both lower into the same internal `list[tuple[float, float]]` (angle, coef) representation, which the hot loop already operates on.

**Group B — Chiron orb 4° + range 1900-2100:** The orb value in `core.bodies['orb'][13]` is read by `get_orb` (via `bodies["orb"]`) and by `synastry/orbs.py:_build_body_orbs_16` (via `_BODIES["orb"]`). Changing the constant in `core.py` propagates automatically. The four bodies with zero natal orb (Rahu, Ketu, Lilith, Chiron) are documented and tested; Chiron will leave that group. The range extension to 1900-2100 is an offline `gen_chiron_coeffs.py` re-run with new `jd0`/`jd1` arguments and a re-validation that `max|Δλ| < 0.01°` still holds.

---

## 1. Dynamic Harmonic Representation

### The Constraint

`aspects_for_harmonics` in `ketu/aspects/presets.py` (line 174) hard-rejects any harmonic not in `_VALID_HARMONICS = frozenset({1,2,3,5,6,9,10})`. That function returns a bool[14] mask. A bool[14] mask can only select rows that already exist in the frozen 14-row table. For H7 (angles: 360/7≈51.4°, 720/7≈102.9°, 1080/7≈154.3°), none of those angles appear as table rows, so a mask-based approach is physically impossible for arbitrary harmonics.

The dynamic path needs its own representation: a list of (angle, coef) pairs generated from the harmonic formula, independent of the table.

### Proposed Data Structure: `HarmonicSpec`

A small structured array (or named tuple list) of aspect specs generated for harmonic `h`:

```python
HARMONIC_SPEC_DTYPE = np.dtype([
    ("angle", "f4"),    # fold_to_0_180(k * 360 / h), degrees
    ("coef",  "f4"),    # k / h  (360° convention, accepted by user)
    ("k",     "i2"),    # multiplier index (1 .. h//2)
])
```

Generator function (new, in `ketu/aspects/presets.py` or a new `ketu/aspects/harmonics.py`):

```python
def generate_harmonic_aspects(h: int) -> npt.NDArray:
    """
    Generate aspect specs for harmonic h using the 360° unified convention.

    For harmonic h, angles = fold_to_0_180(k * 360 / h) for k = 1 .. h//2.
    Coefficient = k / h.  Does NOT consult the frozen core.aspects table.
    Returns a structured array of HARMONIC_SPEC_DTYPE, shape (n_angles,).
    """
```

`fold_to_0_180(angle)` is `180 - abs(angle % 360 - 180)` — maps any angle to [0, 180] by reflecting through 180°. For h=2: k=1 → 180°, coef=0.5. For h=3: k=1 → 120°, coef=1/3; k=1 also gives k=h//2=1 so one angle. For h=7: k=1 → 51.4°, k=2 → 102.9°, k=3 → 154.3°, all with coefs 1/7, 2/7, 3/7.

The user has explicitly accepted that these coefs (~2× smaller than table coefs for comparable angles at lower harmonics) are intentional and correct.

**No `i_asp` field exists on `HARMONIC_SPEC_DTYPE`.** Dynamic aspects have no canonical index in `core.aspects`. The output dtype from detection functions must signal this: use `i_asp = -2` as the sentinel for dynamic aspects (distinct from `-1` which means "no aspect" in dense synastry mode). Alternatively, extend the output dtype to carry `(angle, coef)` directly alongside a nullable `i_asp`. See section 3 for the decision.

---

## 2. Detection-Loop Seam: Unified (angle, coef) Internal List

### Where the Seam Goes

Currently, in `calculate_aspects` (lines 121-124), `calculate_aspects_vectorized` (lines 195-198), and `calculate_aspects_batch` (lines 317-326), the hot-loop setup looks like:

```python
mask = resolve_aspect_set(aspects)
selected_indices = np.where(mask)[0]        # canonical 0-13 indices
selected_angles  = _CORE_ASPECTS["angle"][mask]
selected_coefs   = _CORE_ASPECTS["coef"][mask]
```

The loop then iterates `for k, i_asp in enumerate(selected_indices)` using `selected_angles[k]` and `selected_coefs[k]`.

**The seam is at the point where `selected_angles` / `selected_coefs` are assembled.** Both the mask path and the dynamic path need to produce entries in a unified `list[tuple[int, float, float]]` = `(i_asp, angle, coef)` where `i_asp` is:
- `0..13` for table-derived aspects (canonical index, preserved for Kala contract)
- `-2` for dynamic aspects (sentinel, no table row)

Proposed internal representation after the seam:

```python
# AspectSpec = (i_asp: int, angle: float, coef: float)
# i_asp == -2 signals "dynamic, no table row"
_AspectSpec = tuple[int, float, float]
```

The function signature change is minimal: the `aspects` parameter on all four public multi-aspect functions (`calculate_aspects`, `calculate_aspects_vectorized`, `calculate_aspects_batch`, `find_aspects_between_dates`) gains an additional optional `dynamic_specs` parameter:

```python
def calculate_aspects(
    jdate: float,
    l_bodies: np.ndarray = bodies,
    aspects: AspectSetSpec = None,
    dynamic_specs: npt.NDArray | None = None,  # HARMONIC_SPEC_DTYPE array
) -> np.ndarray:
```

The resolver block becomes:

```python
# Table path (existing)
mask = resolve_aspect_set(aspects)
selected_indices = np.where(mask)[0]
spec_list: list[_AspectSpec] = [
    (int(i), float(_CORE_ASPECTS["angle"][i]), float(_CORE_ASPECTS["coef"][i]))
    for i in selected_indices
]

# Dynamic path (additive, runs after table path)
if dynamic_specs is not None:
    for row in dynamic_specs:
        spec_list.append((-2, float(row["angle"]), float(row["coef"])))
```

The hot loop body changes from reading `selected_angles[k]` and `selected_coefs[k]` to reading `i_asp, angle, coef = spec_list[k]`. The conjunction guard `if i_asp == 0` becomes `if i_asp == 0` (still correct for the table conjunction) and `if angle == 0.0` or better `if i_asp == 0 or (i_asp == -2 and angle < 0.001)` for dynamic H1 which includes 0° from folding. In practice H1 is a degenerate case; for all h >= 2, fold_to_0_180(k*360/h) with k in 1..h//2 never equals exactly 0° unless h=1. A safe guard: `if angle < 0.01` (conjunction-like treatment for any near-zero angle).

### What Changes in the Output dtype

The `i_asp` field in the returned structured array currently holds 0-13. For dynamic aspects it holds -2. Consumers that do `_CORE_ASPECTS["name"][result["i_asp"]]` will crash on -2. Two options:

**Option A (minimal):** Leave `i_asp` as-is but document that -2 = dynamic. Consumers must gate on `i_asp >= 0` before table lookup. Kala's positional contract is preserved for i_asp >= 0. The `aspect_orb` field in `CYCLE_DTYPE` and the synastry `aspect_type` field need the same sentinel awareness.

**Option B (additive fields):** Add `dyn_angle: f4` and `dyn_coef: f4` to the output dtype, populated only when `i_asp == -2`, NaN otherwise. This is richer but breaks any code asserting the exact output dtype fields.

**Recommended: Option A.** The downstream consumer (Kala) already gates on `i_asp >= 0` (synastry uses `aspect_type >= 0` as the "aspected" mask). A single additional gate on the natal aspects output is the least intrusive change. No dtype shape change, no field addition.

---

## 3. Integration Points: file:function Table

### New Components

| Component | Location | What It Does |
|-----------|----------|--------------|
| `generate_harmonic_aspects` | `ketu/aspects/presets.py` OR new `ketu/aspects/harmonics.py` | Generates `HARMONIC_SPEC_DTYPE` array for harmonic h. No table lookup. |
| `HARMONIC_SPEC_DTYPE` | same module as above | Structured dtype `(angle:f4, coef:f4, k:i2)`. |

### Modified Components

| File | Function | Change |
|------|----------|--------|
| `ketu/aspects/calculator.py` | `calculate_aspects` | Add `dynamic_specs` param; assemble unified `spec_list`; loop over spec_list instead of parallel arrays; emit `i_asp=-2` for dynamic rows. |
| `ketu/aspects/calculator.py` | `calculate_aspects_vectorized` | Same `dynamic_specs` param + unified spec_list. The inner per-aspect broadcast loop changes from index-based to spec_list iteration. |
| `ketu/aspects/calculator.py` | `calculate_aspects_batch` | Same param + spec_list. The hoisted `selected_iasp_ints / selected_angles_f / selected_coefs_f` lists become a single `spec_list` assembled once above the date loop. |
| `ketu/aspects/calculator.py` | `find_aspects_between_dates` | Add `dynamic_specs` param; append dynamic angles to `selected_angles` before passing to `find_all_aspects`; after the inner loop, reverse-lookup by angle may fail for dynamic angles (no table row at that angle) — emit `("dynamic_H{h}_k{k}", angle)` as aspect_name instead of table name. |
| `ketu/aspects/calculator.py` | `get_aspect` | Low-priority: this function hard-iterates `_CORE_ASPECTS["angle"]` and is not used in the main hot paths post-Phase 26. If exposed to dynamic aspects, add a `dynamic_specs` param following the same pattern. Can be deferred. |
| `ketu/aspects/calculator.py` | `find_aspect_timing` | Line 427: `asp_idx = np.where(_CORE_ASPECTS["angle"] == aspect_value)[0]` will fail for dynamic angles not in the table. This function is aspect-value-based (caller passes an angle), so no `i_asp` lookup is strictly needed — refactor to accept `orb` directly instead of re-deriving it from the table index. |
| `ketu/synastry/api.py` | `calculate_synastry` | Add `dynamic_specs` param; extend `spec_list` assembly (lines 286-290 of the loop setup) to include dynamic rows with `i_asp_int = -2`; the `aspect_type` field in `SYNASTRY_DTYPE` is `i1` with range [-128, 127] — -2 fits. The loop body already reads `ang` and `coef` from the table by index; for dynamic rows it reads from the spec directly. |
| `ketu/synastry/orbs.py` | `synastry_orb_limit` | No change needed. The `asp` parameter is used only to look up `_ASPECTS["coef"][asp]`. For dynamic paths the caller should NOT call `synastry_orb_limit` with `asp=-2`; the dynamic path computes `(orb_a + orb_b) / 2 * dynamic_coef * factor` inline (the same formula, just with `dynamic_coef` from the spec). |
| `ketu/cycles/calculator.py` | `generate_cycle_series` | The cycle engine uses its own `MAJOR_ASPECTS` array (lines 33-35: `[0, 60, 90, 120, 180, 240, 270, 300, 360]`) and `COEFFS` (line 310) for the `aspect_orb` field — these are independent of `core.aspects` and do not need a dynamic aspects param for the `aspect_orb` cycle field. However, if a caller wants dynamic-aspect-aware cycle aspect detection, a future extension could add a `dynamic_aspects` param to `generate_cycle_series`. For v1.4 scope this is likely out of scope; the cycle engine is self-contained and the `aspect_orb` field measures proximity to the 9 major cycle angles, not to an arbitrary harmonic. **No change required for v1.4 unless explicitly scoped.**|
| `ketu/aspects/presets.py` | `aspects_for_harmonics` | No change to existing function (it keeps hard-rejecting unknown harmonics). The new `generate_harmonic_aspects` function is additive and separate. |
| `ketu/cli/harmonics_spec.py` | `parse_harmonics_spec` | Currently accepts preset names and comma-separated indices into core.aspects. To support `--harmonics 7` or `--harmonics h7` on the CLI, extend to detect a `h<N>` or `harmonic:<N>` token and return a (mask=all-False, dynamic_specs=generate_harmonic_aspects(N)) pair — or change the return type. This is a CLI surface decision; may be deferred to a separate plan. |

### Functions with Hard Table-Index Assumptions (Breakage Risk)

These functions index `_CORE_ASPECTS` by position (0-13) and will fail or produce wrong results if given `i_asp = -2` without a guard:

| File | Line | Assumption | Fix |
|------|------|------------|-----|
| `calculator.py:427` | `find_aspect_timing` | `np.where(_CORE_ASPECTS["angle"] == aspect_value)[0]` → crashes if `aspect_value` not in table | Accept `orb` directly, skip table lookup |
| `calculator.py:534` | `find_aspects_between_dates` inner loop | `asp_idx = np.where(_CORE_ASPECTS["angle"] == aspect_angle)[0][0]` → IndexError for dynamic angles | Guard: if `len(idx) == 0`, use `f"H{h}k{k}"` as name |
| `aspects/core.py:get_aspect_index` | line 57-70 | Looks up `aspects["name"]` or `aspects["angle"]` — valid for table aspects only | No change needed if dynamic path never calls this function with dynamic angles |
| `aspects/core.py:get_aspect_index` | line 63 | `aspect < len(aspects)` guard — -2 would pass `isinstance(int)` but `aspects[-2]` wraps to `aspects[12]` (Quadrinovile) | Add explicit `if aspect < 0: raise ValueError` guard |

---

## 4. Synastry / Cycles Propagation

### Dynamic coef flows through orb correctly

In `calculate_synastry` (`synastry/api.py` lines 291-299), the orb is computed as:

```python
orbs_pair = (_BODY_ORBS_16[i_flat] + _BODY_ORBS_16[j_flat]) / 2.0 * coef * factor
```

`coef` comes from `float(_ASPECTS["coef"][i_asp_int])` for table aspects. For a dynamic spec the coef is `k/h` from the spec row. The formula is identical — `coef` is just a scalar multiplier. Dynamic path substitutes `dynamic_coef` for `coef` at the same point in the loop. No structural change to the orb formula.

### `synastry_orb_limit` is not called on the hot path

`synastry_orb_limit` (`synastry/orbs.py` line 148) is a scalar helper for testing and one-off calculations. The `calculate_synastry` hot path computes the same formula inline (line 294). For dynamic aspects, the inline path uses `dynamic_coef` directly. `synastry_orb_limit` should document that `asp` must be a valid table index (0-13); callers wanting dynamic orb limits should compute `(orb_a + orb_b) / 2.0 * dynamic_coef * factor` directly.

### `_BODY_ORBS_16` propagation for Chiron orb change

`_BODY_ORBS_16` is built at import time by `_build_body_orbs_16` (`synastry/orbs.py` line 59-75):

```python
arr = np.concatenate([
    _BODIES["orb"].astype(np.float32),  # entries 0..13 from core.bodies
    np.array([ASC_MC_NATAL_ORB_DEG] * 2, dtype=np.float32),
])
```

Because it reads `_BODIES["orb"]` (= `ketu.core.bodies["orb"]`) at import time, changing `core.bodies["orb"][13]` from `0` to `4.0` in `core.py` will automatically propagate into `_BODY_ORBS_16[13]` at the next import. No code change in `synastry/orbs.py`.

### CYCLE_DTYPE aspect_orb field

`generate_cycle_series` computes `aspect_orb` using a hardcoded `COEFFS` array over `MAJOR_ASPECTS = [0, 60, 90, 120, 180, 240, 270, 300, 360]` (lines 310-313 of `cycles/calculator.py`). This is completely independent of the `core.aspects` table and of any dynamic harmonic spec. The Chiron orb change does not affect cycle detection logic (the cycle engine uses its own orb formula based on `bodies["orb"]` directly at lines 302-303). After the Chiron orb change, `avg_orb` for a Sun-Chiron cycle pair will become `(12 + 4) / 2 = 8.0` instead of `(12 + 0) / 2 = 6.0`. This is automatic.

### No table-index positional assumptions in synastry hot loop

`calculate_synastry` iterates `for i_asp in selected_indices` and reads `_ASPECTS["angle"][i_asp_int]` and `_ASPECTS["coef"][i_asp_int]`. For dynamic specs the `i_asp_int` sentinel `-2` must be branched: `ang = spec_angle` and `coef = spec_coef` from the dynamic spec row rather than a table lookup. The `aspect_type` field written to `SYNASTRY_DTYPE` will be `-2` for dynamic rows. Downstream consumers gate on `aspect_type >= 0` already.

---

## 5. Chiron Orb 0° → 4°: Propagation Audit

### One-line change in `core.py`

```python
# Before:
("Chiron", 13, 0, 0.019),
# After:
("Chiron", 13, 4, 0.019),
```

### Automatic propagation (no code changes needed)

| Module | Path | Effect |
|--------|------|--------|
| `ketu/aspects/calculator.py` | `get_orb(b1, b2, asp)` reads `bodies["orb"]` | Chiron orb becomes 4 automatically |
| `ketu/aspects/calculator.py` | `calculate_aspects` inner loop reads `l_bodies["orb"]` (line 139) | Automatic |
| `ketu/aspects/calculator.py` | `calculate_aspects_vectorized` reads `l_bodies["orb"]` (line 237) | Automatic |
| `ketu/aspects/calculator.py` | `calculate_aspects_batch` reads `l_bodies["orb"]` (line 352) | Automatic |
| `ketu/synastry/orbs.py` | `_build_body_orbs_16` reads `_BODIES["orb"]` at import time (line 71) | `_BODY_ORBS_16[13]` becomes 4.0 automatically |
| `ketu/cycles/calculator.py` | reads `bodies["orb"][body_id]` at lines 302-303 | Automatic for any body pair including Chiron |

### Test artifacts pinning the old 0° orb (must be updated)

1. **`tests/synastry/test_modes_idempotent.py` (lines 7, 112-131)**
   The docstring and test body explicitly state: "Rahu / Ketu / Lilith / **Chiron** have zero natal orbs". After the change Chiron leaves the zero-orb group. The `test_self_synastry_dense_diagonal_is_conjunction` test (line 107) passes for zero-orb bodies because `dist <= orbs_pair` holds with `orbs_pair == 0` and `dist == 0`. After the change Chiron's self-pair synastry orb becomes `(4 + 4) / 2 * 1 * 0.5 = 2.0` — the test still passes (dist=0 <= 2.0), but the docstring wording is wrong and must be updated to remove Chiron from the "zero-orb" list.

2. **`tests/synastry/test_orbs.py` (no explicit Chiron-specific orb-value assertion)**
   `test_body_orbs_15_canonical_entries_match_bodies` (line 52) asserts `_BODY_ORBS_16[:14] == _BODIES["orb"]` — this is a structural equality test, not pinned to a specific Chiron value. It will continue to pass after the change (the assertion is still true; it just compares against the new value). No change needed.
   There is no explicit `synastry_orb_limit(13, 13, 0) == 0.0` assertion (unlike the explicit Rahu/Ketu/Lilith zero-orb tests at lines 96-106). Chiron is not tested individually for its orb value. However, the docstring and list in `test_modes_idempotent.py` must change.

3. **`tests/cli/fixtures/v1_1_reference_output.txt`**
   Lines present Chiron aspects:
   - `Saturn  - Chiron      : Quincunx      1º11' 2"`
   - `Pluto   - Chiron      : Conjunction   0º 9'48"`
   At the 2000-01-01 date Chiron is near Sagittarius 11°. With orb=0 it only appears when very close to an exact aspect. With orb=4 the aspect detection window widens; the fixture may gain additional Chiron aspect lines or the existing aspect orb values will not change (orb values are differences, not the tolerance). The fixture will need re-recording. The test `test_v1_1_reference_byte_stable.py` runs `--harmonics all` which includes all 14 aspects. With Chiron orb=0 currently, only very tight Chiron aspects appear. With orb=4, more Chiron aspects will appear. **This fixture will change and must be re-recorded after the orb change is applied.**

4. **`tests/synastry/test_modes_idempotent.py` docstring (lines 7, 112)** — wording change only, no assertion logic change.

5. **No assertion in `test_orbs.py` pins Chiron's orb to 0.** The `test_synastry_orb_limit_rahu_rahu_zero_orb`, `_ketu_ketu_zero_orb`, `_lilith_lilith_zero_orb` tests (lines 90-106) do not have a Chiron equivalent — there is no `test_synastry_orb_limit_chiron_chiron_zero_orb` to delete. Only the docstrings that mention Chiron as "zero-orb" must be updated.

---

## 6. Chiron Range 1900-2100: Integration

### What changes

In `tools/gen_chiron_coeffs.py` lines 110-111:
```python
jd0 = swe.julday(1950, 1, 1, 0.0)   # → swe.julday(1900, 1, 1, 0.0)
jd1 = swe.julday(2050, 1, 1, 0.0)   # → swe.julday(2100, 1, 1, 0.0)
```

The `_REF_JDS` list (lines 61-69) should be extended to include dates in the 1900-1950 and 2050-2100 wings for the `--dump-refs` validation output.

The segment count `n_segs = ceil(total_days / 32)` scales proportionally: 200 years ≈ 73050 days → ~2283 segments vs. current 1142.

The `.npz` arrays `lon_coeffs`, `lat_coeffs`, `dist_coeffs`, `seg_starts` all have shape `(n_segs, 11)` or `(n_segs,)` — they grow in proportion to the new range.

### What does NOT change

- `ketu/ephemeris/chiron.py:_load_chiron_data` loads whatever `.npz` is bundled — no code change.
- `_eval_chiron_qty` uses `jd_end` from the data for last-segment length calculation — reads from `.npz`, no code change.
- `ketu/data/chiron_coeffs.npz` is replaced in-place.

### Validation contract

The existing regression test `tests/ephemeris/test_chiron_regression.py` pins 7 reference JDs across 1950-2050. After regeneration it must be extended with reference JDs in the 1900-1950 and 2050-2100 wings (at least one per wing), with pyswisseph-oracle-derived reference longitudes, to demonstrate the 0.01° accuracy target holds over the full new range. The max|Δλ| from the spike (0.000861°) applies only to 1950-2050; the extended range may have slightly different accuracy characteristics that must be measured and documented.

---

## 7. Suggested Build Order

### Phase A: Dynamic Harmonic Generator + Detection-Chain Integration

**Deliverables:**
- `generate_harmonic_aspects(h: int) -> ndarray` in `ketu/aspects/presets.py` (or new `ketu/aspects/harmonics.py`)
- `HARMONIC_SPEC_DTYPE` constant
- `dynamic_specs` parameter on `calculate_aspects`, `calculate_aspects_vectorized`, `calculate_aspects_batch`, `find_aspects_between_dates`, `calculate_synastry`
- Unified spec_list assembly inside each function
- Guard in `aspects/core.py:get_aspect_index` for negative indices
- Guard in `calculator.py:find_aspects_between_dates` for angle lookup failure
- Tests covering H7, H11, H17 detection through the full chain
- Docs: new API surface + convention note (360° unified, ~2× smaller orbs than table convention)

**Dependencies:** None (fully additive, does not touch core.aspects or core.bodies).

**Can parallelize with:** Phase B (no shared files, no shared constants).

### Phase B: Chiron Orb 4° + Test/Fixture Updates

**Deliverables:**
- `core.py` line 84: `("Chiron", 13, 4, 0.019)` (single constant)
- Update `tests/synastry/test_modes_idempotent.py` docstrings (remove Chiron from "zero-orb" group)
- Re-record `tests/cli/fixtures/v1_1_reference_output.txt` (Chiron aspects will change)
- Update any other test docstrings that describe Chiron as zero-orb

**Dependencies:** None relative to Phase A.

**Can parallelize with:** Phase A (no shared files). Cannot parallelize with Phase C (both touch Chiron behaviour; run B first so the orb change is final before re-recording fixtures, and the range extension is then validated against the new orb).

### Phase C: Chiron Range 1900-2100 Regeneration + Validation

**Deliverables:**
- Modify `tools/gen_chiron_coeffs.py` jd0/jd1 and `_REF_JDS`
- Run offline generator (requires pyswisseph + seas_18.se1)
- Replace `ketu/data/chiron_coeffs.npz`
- Extend `tests/ephemeris/test_chiron_regression.py` with 1900-1950 and 2050-2100 reference pins
- Document max|Δλ| for the extended range in the test module

**Dependencies:**
- Phase B should complete first (orb constant final before regeneration, avoids double fixture churn)
- Requires build environment with pyswisseph (offline step, not in CI by default)

**Cannot parallelize with:** Phase B (sequential for clean fixture re-recording).

### Phase D: Documentation

**Deliverables:**
- `docs/` updates: dynamic harmonic API, Chiron orb rationale, range extension
- Changelog entry for v1.4

**Dependencies:** Phases A + B + C must be final (doc last rule — API surface must be stable).

### Phase E: Release v1.4.0

**Deliverables:**
- pyproject.toml version bump
- Changelog finalization
- PyPI publish (OIDC)
- git tag + push

**Dependencies:** Phase D complete.

### Dependency Graph

```
A (dynamic harmonics) ─────────────────────────────────────────────── D (docs) ─── E (release)
B (Chiron orb 4°) ─── C (Chiron range 1900-2100, after B is final) ──┘
```

A and B are fully independent and can be built in parallel or in either order. C must follow B. D must follow A, B, C. E must follow D.

---

## 8. Open Questions

1. **CLI surface for dynamic harmonics.** `parse_harmonics_spec` in `ketu/cli/harmonics_spec.py` currently returns a bool[14] mask. If `--harmonics h7` should work on the CLI, the return type must change (mask + optional dynamic_specs). This is a CLI contract change with byte-stability implications for `v1_1_reference_output.txt`. Recommend scoping this to a separate plan within Phase A or a follow-on Phase A.1.

2. **`find_aspects_between_dates` dynamic name.** When a dynamic angle matches, there is no table name for the aspect. Current code at line 534 does `_CORE_ASPECTS["name"][asp_idx]` which will fail with IndexError for angles not in the table. The proposed fix (emit `"H{h}k{k}"` or `"dynamic_51.4"`) is functional but the caller gets a string that does not match any `ketu.core.aspects` name. Downstream code that expects `name in [a.decode() for a in _CORE_ASPECTS["name"]]` will break. This is acceptable (dynamic aspects are by definition not in the table) but must be documented clearly.

3. **`find_aspect_timing` signature.** This function takes `aspect_value: float` and internally derives the orb by looking up the table index. For dynamic aspects the orb derivation changes: the caller knows the harmonic (and therefore the coef), but this function does not accept coef. Either add a `coef` parameter or deprecate the table-lookup path. No urgent need unless `find_aspect_timing` is called on dynamic angles.

4. **Accuracy of 1900-2100 range.** The spike (Phase 23) validated max|Δλ|=0.000861° for 1950-2050 with seg_len=32/degree=10. Chiron's orbital parameters change slowly but the eccentricity is high (0.38). The accuracy over the extended wings should be measured offline before committing the regenerated `.npz`. If accuracy exceeds 0.01° anywhere, the degree parameter may need to be raised from 10 to 12 for the extended segments.

5. **`SYNASTRY_DTYPE.aspect_type` range.** Currently `i1` (int8), range [-128, 127]. `-2` fits. If future harmonics introduce more sentinels, the range remains safe (a harmonic number up to 127 could be used as a positive sentinel, though that is a different design). No change needed for v1.4.
