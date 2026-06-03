# Phase 29: Chiron Orb 4° - Research

**Researched:** 2026-06-03
**Domain:** Codebase constant change + test artifact propagation
**Confidence:** HIGH (all findings from direct code inspection)

---

## Summary

Phase 29 is a single-constant change: `ketu/core.py` line 84, Chiron's `orb` field goes from `0` to `4`. Every downstream consumer reads `bodies["orb"]` dynamically at runtime, so propagation is automatic — no second source of truth exists that must be manually patched. The one exception is `_BODY_ORBS_16` in `ketu/synastry/orbs.py`, which is built at module import time by slicing `_BODIES["orb"]`, so it also propagates automatically after the one-line change.

The only artifacts that require **active regeneration or correction** are:

1. `tests/cli/fixtures/v1_1_reference_output.txt` — the byte-stable CLI fixture will gain 2 new aspect lines (Sun-Chiron and Moon-Chiron Semi-sextile) because widening Chiron's orb from 0→4 crosses the threshold for those pairs on the reference date 2000-01-01T12:00:00Z.
2. Two synastry test files (`test_modes_idempotent.py`, `test_orbs.py`) that group Chiron with the zero-orb bodies (Rahu/Ketu/Lilith) — those descriptions/asserts become factually wrong.

The frozen `core.aspects` fingerprints (`EXPECTED_ASPECT_FINGERPRINT_V1`, `V13`) hash `core.aspects` only — `core.bodies` bytes are not included — so changing a body orb cannot affect them. Confirmed at `tests/test_ketu.py:191-212`.

**Primary recommendation:** Change one literal in `core.py` line 84, regenerate the CLI fixture with the one-liner from `test_v1_1_reference_byte_stable.py`, manually diff to confirm only the expected 2 new lines appear, then fix the 2 synastry test files.

---

## 1. The Single Source of Truth

**File:** `ketu/core.py`  
**Line:** 84  
**Current value:**
```python
("Chiron", 13, 0, 0.019),  # Centaur, Chebyshev-based position
```
**Change to:**
```python
("Chiron", 13, 4, 0.019),  # Centaur, Chebyshev-based position
```

**Pluto's orb (parity target) — `core.py` line 80:**
```python
("Pluto", 9, 4, 0.004),
```
Pluto orb = 4.0 confirmed via runtime check. Chiron current = 0.0 confirmed.

---

## 2. Propagation Paths — All Automatic After the One Change

| Consumer | File:Line | How it reads Chiron orb | Manual update? |
|---|---|---|---|
| `get_orb()` natal formula | `ketu/aspects/calculator.py:81` | `bodies["orb"]` direct array read | NO — automatic |
| `calculate_aspects()` | `ketu/aspects/calculator.py:197-198` | `l_bodies["orb"][...]` | NO — automatic |
| `calculate_aspects_vectorized()` | `ketu/aspects/calculator.py:317-318` | `l_bodies["orb"][i_indices]` | NO — automatic |
| `calculate_aspects_batch()` | `ketu/aspects/calculator.py:487-488` | `l_bodies["orb"][i_indices]` | NO — automatic |
| `synastry._BODY_ORBS_16` | `ketu/synastry/orbs.py:70-75` | `_BODIES["orb"].astype(np.float32)` at import | NO — automatic |
| `cycles calculator` | `ketu/cycles/calculator.py:366-368` | `bodies["orb"][body1_id]` | NO — automatic |
| `composite/api.py` | `ketu/composite/api.py:312` | `_BODIES["orb"]` direct | NO — automatic |

**Key finding:** `_BODY_ORBS_16` is NOT a hardcoded duplicate. It is built dynamically at module import via `_build_body_orbs_16()` (`ketu/synastry/orbs.py:59-75`) which concatenates `_BODIES["orb"].astype(np.float32)` + 2 ASC/MC entries. So `_BODY_ORBS_16[13]` becomes 4.0 automatically once `core.py` is changed.

The test `test_body_orbs_15_canonical_entries_match_bodies` (`tests/synastry/test_orbs.py:51-54`) verifies this mirror relationship — it will PASS after the change (the test mirrors `core.bodies['orb']`, so it adapts automatically).

---

## 3. The CLI Fixture

**File:** `tests/cli/fixtures/v1_1_reference_output.txt`  
**Current size:** 2259 bytes / 55 lines  
**Reference date / command:**
```bash
python -m ketu --harmonics all aspects --date 2000-01-01T12:00:00Z > tests/cli/fixtures/v1_1_reference_output.txt
```
(Exact command is embedded in `tests/cli/test_v1_1_reference_byte_stable.py:148-149`.)

**Current Chiron lines in fixture (lines 17, 46, 50):**
- Line 17: `Chiron    : Sagittarius    11º36'45"` (position, unchanged)
- Line 46: `Saturn  - Chiron      : Quincunx      1º11' 2"` (already present — Saturn orb=10 → avg=(10+0)/2=5, so this worked even at Chiron orb=0)
- Line 50: `Pluto   - Chiron      : Conjunction   0º 9'48"` (already present — Pluto orb=4 → avg=(4+0)/2=2)

**New aspects that WILL APPEAR after orb=4 (verified by calculation):**
- `Sun   - Chiron : Semi-sextile   1º14'22"` (approx) — Sun orb=12, Chiron=4 → avg=8, coef=1/6 → orb tolerance=1.333°; distance from 30° = 1.240° < 1.333° ✓
- `Moon  - Chiron : Semi-sextile   1º12'11"` (approx) — Moon orb=12, Chiron=4 → same 1.333°; distance from 30° = 1.203° < 1.333° ✓

**No other new aspects** on this date — checked exhaustively across all 14 aspect types for all 13 other bodies.

**Manual audit requirement (CHIR-07):** After regenerating, run `git diff tests/cli/fixtures/v1_1_reference_output.txt` and confirm:
1. Only 2 new aspect lines (Sun-Chiron and Moon-Chiron Semi-sextile) are added.
2. No lines are removed, no format changes, no other pairs affected.
3. The size assertion in the test (`> 1500` bytes) still holds (fixture will grow ~100 bytes).

**NOTE:** The byte-count comment in the test (`v1.1 reference is ~2125 bytes`) will be stale after regeneration but the `> 1500` threshold still passes — no code change needed in the test file itself beyond the fixture regeneration.

---

## 4. Synastry Tests to Fix

### `tests/synastry/test_modes_idempotent.py`

**Module docstring (line 7):**
```
zero-orb-body edge case for Rahu / Ketu / Lilith / Chiron.
```

**Test docstring (`test_self_synastry_dense_diagonal_is_conjunction`, lines 112-118):**
```python
"""...
Rahu / Ketu / Lilith / Chiron have zero natal orbs (in
:data:`ketu.core.bodies`), so the synastry orb tolerance for these
self-pairs is ``0``. The conjunction is detected because the
in-orb test uses ``dist <= orbs_pair`` (non-strict), and self-synastry
gives ``dist == 0`` exactly. This edge case pre-empts the
"zero-orb body conjunction not detected" surprise documented in
16-RESEARCH.md (Pitfall 2 / Rahu zero-orb conjunction edge case).
"""
```

**Required changes:**
- Module docstring: remove "Chiron" from the zero-orb list.
- Test docstring: change `Rahu / Ketu / Lilith / Chiron` to `Rahu / Ketu / Lilith`. The zero-orb self-pair behaviour documented here no longer applies to Chiron — Chiron now has orb=4, so `synastry_orb_limit(13, 13, 0) = (4+4)/2 * 1 * 0.5 = 2.0` ≠ 0.
- Note: the test assertion (`len(diag) == 16`, `diag["aspect_type"] == 0`) remains correct — self-synastry diagonal conjunctions are always detected via the non-strict `<=` even for non-zero orbs. Only the docstring explanation changes.

### `tests/synastry/test_orbs.py`

**Tests grouping Chiron with zero-orb points (implicit — via the `test_body_orbs_15_canonical_entries_match_bodies` mirror test):**

Line 51-54 — this test will PASS automatically (no change needed):
```python
def test_body_orbs_15_canonical_entries_match_bodies() -> None:
    """Entries 0..13 mirror ketu.core.bodies['orb'] (14 canonical incl. Chiron)."""
    expected = _BODIES["orb"].astype(np.float32)
    np.testing.assert_array_equal(_BODY_ORBS_16[:14], expected)
```

**There is NO explicit `test_synastry_orb_limit_chiron_chiron_zero_orb` test** (confirmed by grep). This is the gap CHIR-08 requires filling.

**Required new test to add to `test_orbs.py`:**
```python
def test_synastry_orb_limit_chiron_chiron_parity_pluto() -> None:
    """Chiron-Chiron conjunction == 2.0 deg (orb=4 × factor=0.5, Pluto parity).

    Pins Chiron natal orb = 4° in synastry (_BODY_ORBS_16[13] == 4.0).
    Chiron (id=13) is no longer in the zero-orb group (Rahu/Ketu/Lilith).
    """
    # Chiron-Chiron: (4+4)/2 * coef_conj * factor = 4 * 1 * 0.5 = 2.0
    assert synastry_orb_limit(13, 13, 0) == pytest.approx(2.0, abs=1e-5)
```

Add this after the existing Lilith-Lilith zero-orb test (line 106). Pattern follows `test_synastry_orb_limit_rahu_rahu_zero_orb` at lines 90-96.

Also update the `synastry_orb_limit` docstring in `ketu/synastry/orbs.py:129-130`:
```python
# Current:
# Zero when either body has a zero natal orb (Rahu, Ketu, Lilith in :data:`ketu.core.bodies`).
# After change: Chiron is removed from this list.
```

---

## 5. Frozen-Table Safety

**Confirmed:** `test_aspects_byte_fingerprint` (`tests/test_ketu.py:189-212`) hashes ONLY `core.aspects` fields:
```python
h1.update(aspects_data["name"].tobytes())
h1.update(aspects_data["angle"].tobytes())
h1.update(aspects_data["coef"].tobytes())
```
and the v1.3 extension:
```python
h13.update(aspects_data["harmonic"].tobytes())
h13.update(aspects_data["symbol"].tobytes())
```

`core.bodies` bytes are NEVER hashed. Changing `bodies["orb"][13]` from 0→4 does not affect `EXPECTED_ASPECT_FINGERPRINT_V1` (`c5bd177...`) or `EXPECTED_ASPECT_FINGERPRINT_V13` (`3258530...`). Both fingerprint tests PASS unchanged.

**No other fingerprint/byte-hash test touches `core.bodies`.** Confirmed via grep of entire test suite.

---

## 6. Complete List of Files That Change

### Source (1 file, 1 line):
| File | Change |
|------|--------|
| `ketu/core.py:84` | `("Chiron", 13, 0, 0.019)` → `("Chiron", 13, 4, 0.019)` |

### Side-effect docstring fix (1 source file):
| File | Change |
|------|--------|
| `ketu/synastry/orbs.py:129-130` | Remove Chiron from zero-orb list in `synastry_orb_limit` docstring |

### Fixture (1 file, regenerated):
| File | Change |
|------|--------|
| `tests/cli/fixtures/v1_1_reference_output.txt` | +2 new aspect lines (Sun-Chiron Semi-sextile, Moon-Chiron Semi-sextile) |

### Tests (2 files modified, 1 new test added):
| File | Change |
|------|--------|
| `tests/synastry/test_modes_idempotent.py` | Module docstring + `test_self_synastry_dense_diagonal_is_conjunction` docstring: remove "Chiron" from zero-orb list |
| `tests/synastry/test_orbs.py` | Add `test_synastry_orb_limit_chiron_chiron_parity_pluto()` after line 106 |

### Tests that PASS unchanged (no action needed):
| File | Why it passes automatically |
|------|-----|
| `tests/synastry/test_orbs.py:51-54` (`test_body_orbs_15_canonical_entries_match_bodies`) | Mirrors `core.bodies['orb']` — adapts automatically |
| `tests/test_ketu.py:189-212` (`test_aspects_byte_fingerprint`) | Hashes `core.aspects` only — bodies unchanged |
| `tests/synastry/test_orbs.py:90-106` (Rahu/Ketu/Lilith zero-orb tests) | Still correct — those bodies remain at orb=0 |

---

## 7. Gotchas

### Gotcha 1: `_BODY_ORBS_16` frozen array
`_BODY_ORBS_16.flags.writeable = False` — the array is frozen. However, it is rebuilt fresh at each module import, so the fix in `core.py` propagates automatically on the next process start. No runtime mutation is needed.

### Gotcha 2: `composite/api.py:312` has stale comment
```python
body_orbs = _BODIES["orb"]  # shape (13,)
```
This comment says 13 but since Phase 24 it's actually shape (14,). Not this phase's responsibility to fix — it was stale before Phase 29 — but the planner should be aware. The actual computation at lines 320-327 uses `_BODY_COUNT = 14` correctly.

### Gotcha 3: CLI fixture test size assertion
`tests/cli/test_v1_1_reference_byte_stable.py:93-95` asserts `FIXTURE.stat().st_size > 1500`. The fixture will grow from 2259 to ~2360 bytes after regeneration — still > 1500. The inline comment `v1.1 reference is ~2125 bytes` will be stale but is just a comment, not an assertion.

### Gotcha 4: Existing Chiron aspects in fixture are NOT new
The fixture already has `Saturn-Chiron Quincunx` and `Pluto-Chiron Conjunction` even at orb=0. This is because `get_orb` uses the **average** of both bodies' orbs. Saturn orb=10 → avg=(10+0)/2=5.0; Pluto orb=4 → avg=(4+0)/2=2.0. These two aspects are not affected by this change. The change ONLY adds new pairs where the Chiron side of the average matters enough to cross threshold.

### Gotcha 5: `ketu/synastry/orbs.py` docstring (non-test file)
The `synastry_orb_limit` docstring at line 129 says `"Zero when either body has a zero natal orb (Rahu, Ketu, Lilith in :data:`ketu.core.bodies`)"`. This is a numpydoc-gated public API docstring. The numpydoc gate is BLOCKING CI. After adding Chiron to orb=4, the docstring must be updated to remove Chiron from the zero-orb list. The `Returns` section currently lists only Rahu/Ketu/Lilith — no change needed there, Chiron was never listed. The body of the `Returns` description at line 129-130 is the one to fix.

### Gotcha 6: 100% coverage gate
The new test `test_synastry_orb_limit_chiron_chiron_parity_pluto` calls `synastry_orb_limit(13, 13, 0)`. This hits the already-covered branch; no new branches are introduced by the constant change. Coverage gate will remain at 100%.

### Gotcha 7: Phase 30 dependency
Phase 30 (Chiron Range 1900-2100) will regen the `.npz` ephemeris and may trigger another CLI fixture update. The Phase 30 planner must re-run `python -m ketu --harmonics all aspects --date 2000-01-01T12:00:00Z` after the `.npz` change and commit the updated fixture then. The fixture committed in Phase 29 is intermediate-correct, not final.

---

## Sources

All findings from direct code inspection of the ketu codebase. Confidence HIGH throughout — no external sources required for this phase (it is a pure constant change with known propagation pattern).

| File inspected | Purpose |
|---|---|
| `ketu/core.py:69-87` | Single source of truth for body orbs |
| `ketu/aspects/calculator.py:63-82` | `get_orb` formula |
| `ketu/synastry/orbs.py:59-89` | `_BODY_ORBS_16` derivation |
| `ketu/cycles/calculator.py:365-377` | Cycles orb path |
| `ketu/composite/api.py:305-330` | Composite orb path |
| `tests/test_ketu.py:100-212` | Fingerprint tests (aspects only) |
| `tests/synastry/test_orbs.py` | Synastry orb pinning tests |
| `tests/synastry/test_modes_idempotent.py` | Zero-orb edge case docstrings |
| `tests/cli/test_v1_1_reference_byte_stable.py` | Fixture test and regen command |
| `tests/cli/fixtures/v1_1_reference_output.txt` | Current fixture content |

**Runtime verification:** Computed new aspects on 2000-01-01T12:00:00Z with simulated orb=4; confirmed exactly 2 new pairs cross threshold (Sun-Chiron Semi-sextile, Moon-Chiron Semi-sextile). No other pairs affected.

---

## Metadata

**Confidence breakdown:**
- Source change: HIGH — single literal, confirmed by code + runtime check
- Propagation: HIGH — all paths read `bodies["orb"]` dynamically; `_BODY_ORBS_16` confirmed derived
- Fixture diff: HIGH — exact 2 new lines computed and verified
- Test changes: HIGH — exact docstrings quoted, exact new test pattern specified
- Frozen fingerprints: HIGH — confirmed by reading hash code; bodies bytes not hashed

**Research date:** 2026-06-03
**Valid until:** Until Phase 30 modifies ephemeris data (which may re-trigger fixture churn)
