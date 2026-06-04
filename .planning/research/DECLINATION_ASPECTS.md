# Declination Aspects Research Brief: Parallels & Contra-Parallels

**Project:** Ketu v1.6 — DECLA milestone  
**Researched:** 2026-06-04  
**Scope:** Parallel + contra-parallel detection only (natal chart integration, no synastry, no CLI)  
**Overall confidence:** HIGH for definitions/conventions; HIGH for orb formula; MEDIUM for OOB interaction specifics

---

## 1. Definitions

### 1.1 Parallel

A parallel exists when two bodies share the same equatorial declination (δ) **AND are on the same side of the celestial equator** — both north, or both south.

**Signed-δ condition:**

```
parallel: δ₁ and δ₂ have the same sign AND |δ₁ − δ₂| ≤ orb
```

Equivalently in code:

```python
same_side = np.sign(d1) == np.sign(d2)   # both > 0 or both < 0
close     = np.abs(d1 - d2) <= orb
is_parallel = same_side & close
```

**The same-hemisphere rule is STRICT and is the dominant convention across all surveyed sources** (Sepharial, Carter, Cafe Astrology, Lunarium, Kannon McAfee, Kerykeion, astro.com wiki). "Parallel = same side" is unambiguous.

No mainstream source counts |δ₁| ≈ |δ₂| regardless of sign as a parallel. That configuration is exclusively a contra-parallel. The fringe claim that "parallel happens regardless of north/south" (seen on one Kerykeion draft) contradicts the geometric definition and is an editorial error — the same page later defines it with the same-side rule correctly.

### 1.2 Contra-Parallel

A contra-parallel exists when two bodies have equal magnitude of declination but lie on **opposite sides** of the celestial equator.

**Signed-δ condition:**

```
contra-parallel: δ₁ and δ₂ have opposite signs AND |δ₁ + δ₂| ≤ orb
                 (i.e., |δ₁| ≈ |δ₂|, but sign(δ₁) ≠ sign(δ₂))
```

Equivalently in code:

```python
opposite_side = np.sign(d1) != np.sign(d2)
close_mirror  = np.abs(d1 + d2) <= orb   # sum → 0 when |d1|≈|d2| opposite sign
is_contra     = opposite_side & close_mirror
```

**Interpretive analogy (conventional, no implementation impact):**
- Parallel ≈ conjunction by declination
- Contra-parallel ≈ opposition by declination

Sources agree on this analogy (Sepharial: "they act as if they were in conjunction"; Carter couples parallel with conjunction). Boehrer and the Magi Society consider both aspects functionally similar to each other; the distinction is interpretive, not structural.

### 1.3 The Zero-Crossing Edge Case

When δ₁ and δ₂ are both near 0° (both bodies near the celestial equator), sign comparison becomes unstable. A body at +0.01° and one at −0.01° would be flagged as contra-parallel despite being essentially co-declinated. **Prevention:** treat δ = 0.0 as neither north nor south — use `np.sign` which returns 0 for zero, then the `same_side` and `opposite_side` checks both fail (neither parallel nor contra-parallel is triggered). This is the correct degenerate behavior: two bodies exactly on the equator have 0° separation and form neither aspect in the strict sense. In practice, this edge is astronomically rare and always within a conjunction by longitude as well.

---

## 2. Orb Conventions and Recommended Ketu Derivation Formula

### 2.1 Published Consensus

| Source | Natal Orb | Notes |
|--------|-----------|-------|
| Sepharial (early 20th c.) | ~1° implied | "same degree" = tight |
| Charles Carter | 1° | Stated major orbs should be ~5°, minors ~1° |
| Kt Boehrer (1994, *Declinations: The Other Dimension*) | 1°–1.5° | Luminaries may stretch to 1.5° |
| Kannon McAfee | 1°–1.5° for luminaries, 1° for others | Progressions: max 5' |
| Cafe Astrology | 1° (60') | Stated as explicit standard |
| Lunarium / astro-seek | 1° | "always the same, no matter which planets" |
| Magi Society | 1°12' | Slightly extended |
| Kerykeion | 1°–1°15' | Upper range for natal |
| astro.com | 1° | Used in Extended Chart aspectarian |

**Dominant consensus: 1° for natal, tight. 1°–1.5° is the permissive ceiling for luminaries. Progressions: ≤ 5'.**

One source (Lunarium) states the orb is "always the same regardless of planets," implying a fixed 1° with no body-pair variation. However, Kannon McAfee and Boehrer both distinguish luminary pairs as slightly wider, which aligns with Ketu's per-body orb table approach.

### 2.2 Why Standard Longitude Orbs Cannot Apply Directly

The total declination range is ±23.5° = 47° total. Longitude spans 360°. A 1° orb represents 1/47 ≈ 2.1% of the declination axis, versus 1/360 ≈ 0.3% for longitude. Declination aspects are "rarer" geometry — the proportional strictness demands much tighter orbs. This is the underlying rationale for the tight consensus.

### 2.3 Recommended Ketu Formula

Use the existing natal orb formula structure, with a dedicated declination coefficient:

```
δ_orb(b1, b2) = max(
    (bodies['orb'][b1] + bodies['orb'][b2]) / 2  *  DECLA_COEF,
    MIN_DECL_ORB
)
```

**Recommended constants:**

```python
DECLA_COEF    = 1 / 12   # ≈ 0.0833
MIN_DECL_ORB  = 0.5      # degrees — floor for zero-orb bodies (nodes, Lilith)
```

**Justification:**

The natal orb formula `(orb_b1 + orb_b2) / 2` produces a mean longitude orb. For Sun (orb=12°) + Moon (orb=12°): mean = 12°. Multiplying by `1/12` yields exactly **1.000°** — matching the tight published consensus precisely.

**Worked examples:**

| Pair | b1 orb | b2 orb | mean | × 1/12 | floor applied | final δ_orb |
|------|--------|--------|------|--------|---------------|-------------|
| Sun / Moon | 12° | 12° | 12.0° | 1.000° | no | **1.000°** |
| Sun / Mars | 12° | 8° | 10.0° | 0.833° | no | **0.833°** |
| Jupiter / Saturn | 10° | 10° | 10.0° | 0.833° | no | **0.833°** |
| Venus / Mars | 10° | 8° | 9.0° | 0.750° | no | **0.750°** |
| Uranus / Neptune | 6° | 6° | 6.0° | 0.500° | no | **0.500°** |
| Pluto / Chiron | 4° | 4° | 4.0° | 0.333° | → 0.500° | **0.500°** |
| Sun / Rahu | 12° | 0° | 6.0° | 0.500° | no | **0.500°** |
| Rahu / Lilith | 0° | 0° | 0.0° | 0.000° | → 0.500° | **0.500°** |

The floor of 0.5° ensures zero-orb bodies (Rahu id=10, Ketu id=11, Lilith id=12 — all have `core.bodies['orb'] = 0`) still receive a meaningful minimum orb rather than being undetectable.

The scale of resulting values (0.5°–1.0°) is fully within the published literature range for natal declination aspects across all source types.

**The coefficient `1/12` is a concrete, justified, exact fraction — not a magic number.** It equals the reciprocal of the maximum orb value in `core.bodies` (Sun/Moon both at 12°), which is the most natural normalization.

---

## 3. Detection Algorithm (NumPy-Vectorizable)

### 3.1 Scalar / Single Chart Detection

Given `body_decl` array of shape `(14,)` from a `CHART_DTYPE` record:

```python
import numpy as np
from ketu.core import bodies as _bodies

DECLA_COEF   = 1 / 12
MIN_DECL_ORB = 0.5  # degrees

def _decl_orb(i: int, j: int) -> float:
    """Compute the declination orb for body pair (i, j)."""
    raw = (_bodies["orb"][i] + _bodies["orb"][j]) / 2 * DECLA_COEF
    return float(max(raw, MIN_DECL_ORB))


def find_declination_aspects(
    body_decl: np.ndarray,   # shape (14,), signed degrees
) -> tuple[np.ndarray, np.ndarray]:
    """
    Detect all parallel and contra-parallel pairs in a natal chart.

    Parameters
    ----------
    body_decl : ndarray, shape (14,)
        Signed equatorial declination per body (degrees, -90 to +90).

    Returns
    -------
    parallels : ndarray, shape (N, 3) — columns: body_i, body_j, separation
    contras   : ndarray, shape (M, 3) — columns: body_i, body_j, |d_i + d_j|
    """
    n = len(body_decl)
    par_list, con_list = [], []
    for i in range(n):
        for j in range(i + 1, n):
            d1, d2 = body_decl[i], body_decl[j]
            orb = _decl_orb(i, j)
            sep = abs(d1 - d2)
            mir = abs(d1 + d2)
            s1, s2 = np.sign(d1), np.sign(d2)
            if s1 == s2 != 0 and sep <= orb:
                par_list.append((i, j, float(sep)))
            elif s1 != s2 and mir <= orb:
                con_list.append((i, j, float(mir)))
    dtype = [("body1", "i4"), ("body2", "i4"), ("gap", "f8")]
    par = np.array(par_list, dtype=dtype) if par_list else np.empty(0, dtype=dtype)
    con = np.array(con_list, dtype=dtype) if con_list else np.empty(0, dtype=dtype)
    return par, con
```

### 3.2 Vectorized Batch Detection (NumPy broadcast, no Python loops)

For large arrays of charts (shape `(S, 14)`), or to compute all 91 upper-triangle pairs at once:

```python
def find_declination_aspects_vectorized(
    body_decl: np.ndarray,  # shape (..., 14)
) -> dict:
    """
    Fully vectorized declination aspect detector.
    Returns boolean masks for the upper-triangle pair indices.
    """
    # Pre-build orb matrix (14×14), broadcast-safe
    orbs_vec = _bodies["orb"].astype(np.float64)           # shape (14,)
    orb_mat  = np.maximum(
        np.add.outer(orbs_vec, orbs_vec) / 2 * DECLA_COEF,
        MIN_DECL_ORB
    )  # shape (14, 14)

    # Upper triangle indices (91 pairs, i < j)
    idx_i, idx_j = np.triu_indices(14, k=1)                # each shape (91,)

    d = body_decl                                           # (..., 14)
    d1 = d[..., idx_i]                                     # (..., 91)
    d2 = d[..., idx_j]                                     # (..., 91)

    orb_pairs = orb_mat[idx_i, idx_j]                      # (91,)

    sep = np.abs(d1 - d2)
    mir = np.abs(d1 + d2)

    s1 = np.sign(d1)
    s2 = np.sign(d2)

    # Parallel: same non-zero sign, close in δ
    parallel = (s1 == s2) & (s1 != 0) & (sep <= orb_pairs)

    # Contra: opposite non-zero sign, |δ1 + δ2| within orb
    contra   = (s1 != s2) & (s1 != 0) & (s2 != 0) & (mir <= orb_pairs)

    return {
        "idx_i": idx_i,          # (91,) body index 1
        "idx_j": idx_j,          # (91,) body index 2
        "parallel": parallel,    # (..., 91) bool
        "contra": contra,        # (..., 91) bool
        "sep": sep,              # (..., 91) separation for parallels
        "mir": mir,              # (..., 91) mirror gap for contras
        "orb_pairs": orb_pairs,  # (91,) orb limit per pair
    }
```

The `orb_mat` computation is O(1) and can be module-level constant. The detection itself is pure NumPy broadcasting with no Python loops over bodies.

---

## 4. Minimum-Viable Scope vs. Optional Extensions

### 4.1 Recommended LIGHT scope for v1.6

**Implement:** in-orb boolean detection only.

For each ordered pair `(i, j)` with `i < j`:
- `is_parallel(i, j)`:   `sign(δᵢ) == sign(δⱼ) != 0  AND  |δᵢ − δⱼ| ≤ δ_orb(i,j)`
- `is_contra(i, j)`:     `sign(δᵢ) != sign(δⱼ)  AND  both != 0  AND  |δᵢ + δⱼ| ≤ δ_orb(i,j)`

This is sufficient for natal chart detection and matches what all surveyed software reports by default when displaying a "declination aspectarian" (Solar Fire, Astrodienst Extended Chart, Astro Gold).

**Return structure recommendation:** a dedicated dtype, e.g.:

```python
DECLA_ASPECT_DTYPE = np.dtype([
    ("body1",  "i4"),       # index into core.bodies (0-13)
    ("body2",  "i4"),
    ("kind",   "U2"),       # "P" or "CP"
    ("gap",    "f8"),       # |δ₁−δ₂| for P, |δ₁+δ₂| for CP, degrees
    ("orb",    "f8"),       # orb limit used for this pair
])
```

### 4.2 Optional Extensions (out of v1.6 scope, document for future)

**Applying/separating detection:** The analogue for longitude is whether the gap is shrinking over time. For declination:
- Parallel applying: `d/dt(|δ₁ − δ₂|) < 0`
- Contra applying: `d/dt(|δ₁ + δ₂|) < 0`

Both are computable via `declination_velocity(jdate, body)` already in v1.5. The velocity difference `v₁ − v₂` (for parallel) or `v₁ + v₂` (for contra) gives the rate of change of separation. Negative = applying.

**Verdict:** applying/separating is NOT commonly reported for declination aspects in mainstream practice. None of the surveyed sources (Carter, Boehrer, Cafe Astrology, Kannon McAfee, Kerykeion) discuss it. Progressions use a drastically tighter orb (≤ 5') instead. The community consensus is that in-orb detection is the complete output for natal work. Do not implement in v1.6.

**Timing (exact crossing date):** Similarly out of scope for v1.6. Achievable with the existing `aspect_windows.py` bisection pattern, but not expected by downstream consumers (Kala) at this milestone.

---

## 5. Out-of-Bounds Interaction and Edge Cases

### 5.1 OOB Bodies in Parallels

Bodies beyond ±23°26′ (already tracked via `is_out_of_bounds` in v1.5) **participate in parallel/contra-parallel detection mechanically identically** to in-bounds bodies. The detection formula does not change.

**Special significance (interpretive, no implementation impact):** When two OOB bodies form a parallel, some authors (Boehrer, McAfee) consider the aspect particularly intense because both bodies operate outside the solar declination range. This is a delineation note, not a detection flag — the implementer should not change detection logic. If the caller wants to annotate "both OOB" they can compose `is_out_of_bounds` results with the aspect output.

### 5.2 Near-Maximum Declination Edge Case

When two bodies are both near ±23.5° (near solstice points), the declination velocity is near zero (dδ/dt ≈ 0 — the turning point of the sine wave). A parallel between two near-maximum bodies can persist for days or even weeks. This is not a bug — it is astronomically correct. No special handling is needed.

### 5.3 The Codeclination (Boehrer) — Out of Scope

Boehrer defines a "codeclination" as a mirror declination across the 23°27' threshold (e.g., 23°30' has codeclination 23°24'). This is a separate interpretive technique, not a detection aspect. Do NOT implement in v1.6.

### 5.4 Zero-Orb Bodies (Rahu, Ketu, Lilith)

`core.bodies['orb']` is 0 for body indices 10, 11, 12. The `MIN_DECL_ORB = 0.5°` floor in the formula ensures these bodies can still form detectable declination aspects. In practice, the Moon's mean node (Rahu) and true node oscillate in declination and do form meaningful parallels with the Moon and Sun — these should not be invisible to the detector.

---

## 6. Symbols and Naming Conventions

### 6.1 Unicode (authoritative)

From David Faulks, "Extra Aspect Symbols for Astrology," Unicode proposal L2/16-174 (June 2016):

| Aspect | Unicode | Codepoint | Name |
|--------|---------|-----------|------|
| Parallel | `⫽` | U+2AFD | DOUBLE SOLIDUS OPERATOR (closest available, widely used as fallback) |
| Parallel | `‖` | U+2016 | DOUBLE VERTICAL LINE (common text fallback) |
| Parallel | `//` (proposed) | U+2BDD | PARALLEL ASPECT (proposal, not yet in Unicode) |
| Contra-parallel | `#` (proposed) | U+2BDE | CONTRA PARALLEL ASPECT (proposal, not yet in Unicode) |

The proposal (U+2BDD/U+2BDE) establishes `//` and `#` as the intended Unicode characters. As of 2026 these are not yet in the Unicode standard; the proposals are the authoritative reference for glyph intent.

### 6.2 Text Abbreviations (for docs, CLI output, dtype fields)

| Aspect | Abbrev | Notes |
|--------|--------|-------|
| Parallel | `P` | Most compact, used by Solar Fire and Astrodienst text output |
| Parallel | `Par` | Unambiguous in prose contexts |
| Contra-parallel | `CP` | Dominant in printed tables (Carter, Cafe Astrology, Solar Fire) |
| Contra-parallel | `Cntr` | Some software variants |
| Contra-parallel | `A` | Older notation (Magi Society); avoid for new code — confusing |

**Recommendation for Ketu:**
- `kind` field values: `"P"` and `"CP"` — short, unambiguous, matches Solar Fire convention.
- Symbol field (if needed): `"//"` and `"#"` — the intended Unicode glyphs per the proposal, universally recognizable as text.
- Documentation prose: "parallel" and "contra-parallel" (no hyphen variant "contraparallel" is also acceptable but less common in English-language sources).

---

## 7. Pitfalls and Test-Case Seeds

### Pitfall 1 (CRITICAL): Sign conflation — treating |δ₁| ≈ |δ₂| as parallel

**What goes wrong:** Using `abs(d1) - abs(d2)` as the separation metric for BOTH parallels and contra-parallels. This makes a body at +15° and one at −15° appear as a parallel with 0° separation — which is a contra-parallel.

**Prevention:** Always test sign separately. `parallel` requires `sign(d1) == sign(d2) != 0`.

**Test assertion:**
```python
# d1 = +15.0°, d2 = -15.0° → CONTRA-PARALLEL, NOT parallel
d = np.zeros(14); d[0] = 15.0; d[1] = -15.0
par, con = find_declination_aspects(d)
assert len(par) == 0, "Should not be a parallel"
assert len(con) == 1, "Should be a contra-parallel"
assert con[0]["gap"] < 0.001
```

### Pitfall 2 (CRITICAL): Confusing parallel with conjunction

**What goes wrong:** Treating a parallel as a longitude conjunction. They are independent — two bodies can be parallel without being conjunct (and vice versa). A "double whammy" (both conjunct AND parallel) is notably stronger, but the detection paths are separate.

**Test assertion:**
```python
# Two bodies at opposite longitudes (180° apart) but same declination → parallel, no longitude conjunction
# No code test here — architecture test: ensure find_declination_aspects takes body_decl only,
# does not access body longitudes.
```

### Pitfall 3: Orb inflation from longitude orb table

**What goes wrong:** Using the raw longitude orb `(orb_b1 + orb_b2) / 2` without the `DECLA_COEF` factor. For Sun/Moon this gives 12° — twelve times too wide, detecting spurious parallels for most of the year.

**Test assertion:**
```python
# Sun at +15°, Moon at +22° → gap = 7°; with raw orb 12° this is a false parallel
# With DECLA_COEF=1/12 → orb=1.0° → correctly NOT a parallel
d = np.zeros(14); d[0] = 15.0; d[1] = 22.0
par, _ = find_declination_aspects(d)
assert len(par) == 0, "7° gap must NOT be a parallel with 1° orb"
```

### Pitfall 4: Zero-sign trap at the celestial equator

**What goes wrong:** `np.sign(0.0) == 0`, so a body exactly at δ = 0° has sign = 0, and `sign(d1) == sign(d2)` is True (both 0), triggering a false parallel.

**Prevention:** The condition `s1 == s2 != 0` (i.e., `s1 == s2 and s1 != 0`) correctly rejects the zero case.

**Test assertion:**
```python
# Both bodies at δ = 0.0 → neither parallel nor contra
d = np.zeros(14)
d[0] = 0.0; d[1] = 0.0
par, con = find_declination_aspects(d)
assert len(par) == 0 and len(con) == 0

# One body at +0.01°, one at -0.01° → gap < orb but OPPOSITE signs → contra
d[0] = 0.01; d[1] = -0.01
par, con = find_declination_aspects(d)
assert len(par) == 0
# gap = 0.02° < MIN_DECL_ORB = 0.5° → contra is detected
assert len(con) == 1
```

### Pitfall 5: Moon Node / Lilith invisible with zero-orb formula

**What goes wrong:** Without `MIN_DECL_ORB`, `(0 + 0) / 2 * DECLA_COEF = 0.0`, so Rahu/Ketu/Lilith never form any declination aspect with each other. Even `Rahu/Sun` yields only 0.5° which is fine, but `Rahu/Chiron` would be 0.167° which is too tight for practical use.

**Prevention:** `MIN_DECL_ORB = 0.5°` floor in the formula.

**Test assertion:**
```python
# Rahu (idx 10, orb=0) and Lilith (idx 12, orb=0) at same declination
# Without floor: orb = 0.0 → no detection even at exact parallel
# With floor: orb = 0.5° → detects within 0.5°
d = np.zeros(14); d[10] = 12.5; d[12] = 12.4  # gap = 0.1° < 0.5° floor
par, _ = find_declination_aspects(d)
assert len(par) == 1, "Rahu/Lilith parallel should be detected with MIN_DECL_ORB floor"
```

### Pitfall 6: Applying `np.triu_indices` to a (14,) array then indexing a 14-element dtype field

**What goes wrong:** `body_decl` is a subarray field in `CHART_DTYPE` — accessing it from a scalar chart record returns shape `(14,)`, but from a batch record returns `(S, 14)`. Broadcasting the pair indices requires care.

**Test assertion (architecture):**
```python
# Scalar chart record
chart = compute_chart(jd, lat, lon, asc)
decl = chart["body_decl"]   # shape (14,)
assert decl.shape == (14,)
par, con = find_declination_aspects(decl)  # must not raise

# Batch
charts = compute_chart(jd_array, lat, lon, asc)
decl_batch = charts["body_decl"]  # shape (S, 14)
result = find_declination_aspects_vectorized(decl_batch)
assert result["parallel"].shape == (len(jd_array), 91)
```

### Known Test-Case Seeds (citable astronomical events)

**Summer solstice parallel:** Near June 21, the Sun's declination is ≈ +23.5°. Any inner planet also near its maximum northern declination forms a parallel with the Sun. Mercury and Venus frequently reach their maximum declination within 1° of the Sun's solstice value.

**Concrete seed (HIGH confidence, computable):**
```
Date: 2000-06-21 12:00 UTC
Sun δ ≈ +23.44°
Venus δ ≈ varies; check with ketu.calculations.declination(jd, 3)
```

**Annual contra-parallel seed:** Near equinoxes, the Sun crosses δ = 0°. Near winter solstice (Dec 21), Sun is at ≈ −23.44°, while any planet that was at +23.44° in June may be somewhere in between. The Moon reaches ≈ ±28° (OOB range) roughly every 2 weeks and will pass through declinations contra-parallel to most planets.

**Moon OOB seed:**
```python
# Moon is OOB roughly 10-15% of the time; check 2000-01-01 through 2000-12-31
# For a parallel detection unit test, find a date where Moon δ ≈ Sun δ within 1°
# Both bodies on same side → parallel; likely testable within the existing
# v1.5 declination oracle test infrastructure.
```

The implementer should derive concrete date/value seeds by running `ketu.calculations.declination` over a date range and finding natural exact-parallel events to use as regression fixtures — analogous to how v1.4 built Chebyshev oracle tests from Swiss Ephemeris ground truth.

---

## 8. Sources

| Source | Confidence | URL / Reference |
|--------|------------|-----------------|
| Kerykeion — Parallels and Contra-Parallels | HIGH | https://kerykeion.net/content/learn-astrology/advanced-aspects-parallels |
| Cafe Astrology — Synastry Parallels | HIGH | https://cafeastrology.com/declinations_parallels.html |
| Cafe Astrology — Natal Parallel Interpretations | HIGH | https://cafeastrology.com/natal/declinationsparallels.html |
| Starzology — Aspects of Declination | HIGH | https://www.starzology.com/aspects-of-declination/ |
| Kannon McAfee — Declinations | HIGH | https://kannonmcafee.wordpress.com/declinations/ |
| Lunarium — What Is Declination | HIGH | https://lunarium.co.uk/articles/declination/ |
| astro-seek — Parallels of Declination Calculator | MEDIUM | https://horoscopes.astro-seek.com/parallels-of-declination-astrology-aspects-online-calculator |
| Alabe / Solar Fire — Divining Declination in Solar Fire | MEDIUM | https://alabe.com/ProgramDocs/Divining_Declination_in_Solar_Fire.pdf |
| Astrologysoftware.com — Article 33 | MEDIUM | https://www.astrologysoftware.com/m/community/learn/articles/article_33.html |
| Kt Boehrer — *Declination: The Other Dimension* (1994) | HIGH (secondary) | ISBN 978-0-86690-669-2 (AbeBooks, Amazon) |
| Charles Carter — *The Astrological Aspects* | HIGH (secondary) | archive.org/details/astrologicalaspe0000cart |
| David Faulks — "Extra Aspect Symbols for Astrology" (Unicode L2/16-174, 2016) | HIGH | https://www.unicode.org/L2/L2016/16174-astrology-aspects.pdf |
| Symbolikon — Contra-Parallel Astrology Symbol | MEDIUM | https://symbolikon.com/downloads/contra-parallels-astrology/ |
| Astrodienst Astrowiki — Out-of-Bounds Planets | MEDIUM | https://www.astro.com/astrowiki/en/Out-of-Bounds_Planets |
| Ketu core.py / aspects/calculator.py — existing orb formula | HIGH (internal) | /home/loc/workspace/ketu/ketu/core.py, ketu/aspects/calculator.py |
