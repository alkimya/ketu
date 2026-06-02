# Feature Research: v1.4 Dynamic Harmonics + Chiron Orb

**Domain:** Astrological ephemeris library (pure-NumPy, financial-astrology focus)
**Researched:** 2026-06-02
**Confidence:** HIGH for math; MEDIUM for Chiron orb convention; HIGH for ephemeris range

---

## Summary

Three discrete v1.4 features researched: (1) an open-ended harmonic aspect generator,
(2) a Chiron orb fix from 0° to 4°, and (3) a Chiron ephemeris range extension from
1950-2050 to 1900-2100. All three are additive — none require breaking changes to the
frozen 14-row `core.aspects` table or existing presets.

The most design-sensitive finding is that the existing Ketu `harmonic` column uses a
**half-circle framing** (H1/H2/H3/H6 divide 180°) that is **incompatible** with the
standard astrological Nth-harmonic convention (divide 360°). The dynamic generator
must therefore use **only** the standard 360-division convention and be architecturally
independent of the fixed 14-row table. The two systems coexist without conflict.

---

## Feature 1: Open-ended Harmonic Aspect Generator

### Classification: TABLE STAKES

**Why table stakes:** Harmonic astrology practitioners expect any integer harmonic to be
usable (Addey tradition, Cochrane vibrational astrology). Ketu currently raises
`ValueError` for h=7, h=11, h=17, etc. — blocking a core use case that the ML consumer
(Kala) needs for exploratory harmonic feature engineering. Without this, H-exploration
requires re-releasing Ketu or monkey-patching `core.aspects`.

**Complexity:** LOW-MEDIUM. Pure math, no ephemeris dependency, no new data files.
Extends an existing public function (`aspects_for_harmonics`) or adds a parallel
`generate_harmonic_aspects(h)` returning a transient list rather than a fixed-table mask.

---

### 1a. Mathematical Definition of the Nth Harmonic

The standard definition (Addey 1976, confirmed by Cochrane vibrational astrology):

> For harmonic `h`, the aspect series divides the **360° circle** into `h` equal parts.
> The aspect angles are `k × 360° / h` for `k = 1, 2, …, h-1`.

Because the zodiac is symmetric — a separation of θ° and (360° - θ°) represent identical
closeness — every raw angle greater than 180° is folded:

```
raw_angle  = k × 360 / h
fold_angle = raw_angle  if raw_angle <= 180
           = 360 - raw_angle  if raw_angle > 180
```

The fold produces at most `floor(h/2)` **unique** angles (k = 1 .. h//2). This is the
correct range to iterate: for even h, k = h/2 yields 180° exactly; for odd h, the last
unique k is (h-1)//2.

**Verified against existing H5/H9/H10 entries in `core.aspects`:** the generator with
k=1..h//2 reproduces the H5 (72°, 144°) and partial H9/H10 entries exactly (the table
omits H9's 120° and H10's 72°/144°/180° because those angles belong to lower-harmonic
aspects in the deduplicated fixed table — an independent concern).

**Examples:**

| Harmonic | k | Raw (°) | Folded (°) | Traditional name |
|----------|---|---------|-----------|-----------------|
| H7 | 1 | 51.4286 | 51.4286 | Septile |
| H7 | 2 | 102.8571 | 102.8571 | Biseptile |
| H7 | 3 | 154.2857 | 154.2857 | Triseptile |
| H11 | 1 | 32.7273 | 32.7273 | Undecile |
| H11 | 2 | 65.4545 | 65.4545 | Biundecile |
| H11 | 3 | 98.1818 | 98.1818 | Triundecile |
| H11 | 4 | 130.9091 | 130.9091 | — (unnamed) |
| H11 | 5 | 163.6364 | 163.6364 | — (unnamed) |
| H17 | 1 | 21.1765 | 21.1765 | — (unnamed) |
| H17 | 2 | 42.3529 | 42.3529 | — (unnamed) |
| H17 | 8 | 169.4118 | 169.4118 | — (unnamed) |

---

### 1b. Orb Coefficient Formula

The existing Ketu orb formula is:

```
aspect_orb = (body1.orb + body2.orb) / 2  ×  aspect.coef
```

For the dynamic generator, `coef = k / h` (pre-fold k, i.e. k in 1..h//2).

**Verified:** this formula reproduces all `coef` values in the existing `core.aspects`
table for the **full-circle harmonics** (H5, H9, H10):
- H5 Quintile: k=1, coef=1/5=0.2 ✓
- H5 Biquintile: k=2, coef=2/5=0.4 ✓
- H9 Novile: k=1, coef=1/9≈0.111 ✓
- H9 Binovile: k=2, coef=2/9≈0.222 ✓
- H9 Quadrinovile: k=4, coef=4/9≈0.444 ✓
- H10 Decile: k=1, coef=1/10=0.1 ✓
- H10 Tredecile: k=3, coef=3/10=0.3 ✓

**Practical orb values for Sun-Mars pair (base orb = 10°):**

| Harmonic | k=1 coef | k=1 orb | largest coef | largest orb |
|----------|----------|---------|-------------|------------|
| H7 | 1/7≈0.143 | 1.43° | 3/7≈0.429 | 4.29° |
| H11 | 1/11≈0.091 | 0.91° | 5/11≈0.455 | 4.55° |
| H17 | 1/17≈0.059 | 0.59° | 8/17≈0.471 | 4.71° |

This is consistent with Cochrane's principle that "the orb allowed for any harmonic is
the orb for the conjunction divided by the harmonic number" (MEDIUM confidence; from
webSearch, not official docs). Ketu's per-body orb system achieves this automatically
via `coef = 1/h` for the smallest multiple.

---

### 1c. Naming Convention for High Harmonics

**Established names (HIGH confidence):**

| H | Named aspects (k=1, 2, …) |
|---|--------------------------|
| 7 | Septile, Biseptile, Triseptile |
| 8 | Semi-square (Octile), Sesquiquadrate |
| 11 | Undecile (1st only commonly named) |
| 12 | Semi-sextile (= H6 in standard, = H12 in 360-convention) |

**Naming convention beyond H12:** No established names exist. Cochrane's *The First 32
Harmonics* (2021, Cosmic Patterns Software) studies H1–H32 qualitatively but does not
assign individual aspect names within each harmonic series beyond the first multiple for
primes (septile, undecile, etc.).

**Recommendation:** for aspects with no traditional name, emit **blank symbol** (empty
string) and name them programmatically as `f"H{h}/{k}"` or leave name blank. This is
consistent with the existing Ketu convention: the 7 minor aspects in the fixed table
already use blank symbols. A caller can label them `H17k1`, `H17k2` … for display.

---

### 1d. Half-Circle vs Unified 360° — The Critical Architecture Question

**Finding: the two framings are INCOMPATIBLE and must remain separate systems.**

The existing `core.aspects` table mixes two conventions:
- **Half-circle harmonics (H1, H2, H3, H6):** divide 180°. `coef = angle / 180`.
  - H6 in Ketu = Semi-sextile (30°) + Quincunx (150°)
  - H3 in Ketu = Sextile (60°) + Trine (120°)
- **Full-circle harmonics (H5, H9, H10):** divide 360°. `coef = k/h`.

**A unified 360° generator cannot reproduce the half-circle aspects.** Verified by
exhaustive check:

| H (Ketu internal) | Expected angles (Ketu table) | Unified 360 generates | Missing |
|-------------------|-----------------------------|-----------------------|---------|
| H6 | 30°, 150° | 60°, 120°, 180° | 30°, 150° |
| H3 | 60°, 120° | 120° | 60° |
| H2 | 90° | 180° | 90° |
| H1 | 0°, 180° | 0° only | 180° |

**Consequence for the v1.4 generator:** it must use the **standard 360-division
convention** (the same convention Addey/Cochrane use and what external users mean when
they request "H17"). This generator operates on a **separate code path** from
`aspects_for_harmonics` and the fixed 14-row table. There is no conflict: the two
systems coexist, answer different questions, and the generator is not expected to
reproduce the table.

**Important naming note:** Ketu's `harmonic` column uses different numbering than
standard astrological convention. In standard astrology, Square = H4 (360/4=90°) and
Sextile = H6 (360/6=60°). In Ketu's internal column, Square = H2 and Sextile = H3
(half-circle framing). The dynamic generator should use **standard astrological
numbering** (360-based) to match user expectations, not Ketu's internal column values.

---

### 1e. Design Recommendation

```python
# New public API (separate from aspects_for_harmonics)
def generate_harmonic_aspects(h: int) -> list[dict]:
    """
    Generate aspect angles for harmonic h using standard 360-division convention.
    Returns list of dicts with keys: angle (float), k (int), coef (float), name (str), symbol (str).
    k=1..h//2 (unique angles only, pre-fold coefficient).
    """
```

Returns a **transient list** (not rows in `core.aspects`, not a bool mask). The consumer
(Kala) decides whether to deduplicate against the fixed 14-row table. This keeps the
generator stateless and independent.

**Not a breaking change.** The frozen 14-row table, presets, and `aspects_for_harmonics`
are untouched.

---

## Feature 2: Chiron Orb — 0° to 4°

### Classification: TABLE STAKES (bug fix framing)

**Current state:** `bodies['orb'][13] = 0.0` — Chiron has zero orb. This means Chiron
aspects are never triggered in practice (the orb window is literally zero). This is
effectively a defect introduced when Chiron was added in Phase 24: the body was inserted
with `orb=0` as a placeholder.

**Convention research:**

Astrologers assign Chiron varying orbs:
- Strictest modern approach (charts with 34+ factors): 0-1°
- Most common range: 2-4°
- Some practitioners: up to 5-8°
- Cochrane vibrational astrology: tight orbs (1-2° in harmonic charts)

The **3-5° range** is most frequently cited for natal aspects with Chiron. A **4° orb**
matching Pluto (the next-slowest body in the table) is the cleanest defensible default:

1. Pluto has the same orb (4°) in Ketu's table.
2. Chiron and Pluto have similar orbital characteristics (slow outer-body motion,
   similar astrological "weight" in modern practice).
3. 4° is within the mainstream range (2-5°); it is neither the widest nor strictest
   convention.
4. The user specifically requested parity with Pluto (4°), which has community backing.

**Sources conflict (LOW-MEDIUM confidence):** no single authoritative standard exists.
The range 2-5° is well-attested; 4° is defensible but not uniquely correct.

**Breaking change analysis:** changing `bodies['orb'][13]` from 0 to 4 is **NOT a
breaking change** in the semantic sense (no functionality removed, orb window expands).
However, it IS a value change in a constant that tests may assert directly.

**Tests requiring update:**
- `tests/synastry/test_modes_idempotent.py` — documents "Rahu/Ketu/Lilith/Chiron have
  zero natal orbs" as a test fixture. This test will need updating once orb changes.
- `tests/synastry/test_orbs.py` — mirrors `core.bodies['orb']` explicitly.
- Any snapshot tests comparing orb values numerically.

---

## Feature 3: Chiron Ephemeris Range — 1950-2050 to 1900-2100

### Classification: DIFFERENTIATOR

**Current state:** `ketu/data/chiron_coeffs.npz` covers JD 2433282.5–2469807.5
= **1950-01-01 to 2050-01-01** exactly (1142 segments of 32 days, degree-10 Chebyshev).
This was chosen in Phase 23 as the minimal viable range for the spike.

**Why extend:**
- Financial-astrology use cases need birth dates back to early 1900s for historical
  analysis (e.g., cycles of market crashes, birth charts of corporations, individuals
  born 1900-1950).
- Forward coverage to 2100 supports long-range forecasting typical in financial cycles.
- The Serennu ephemeris table covers 1920-2099; astro.com Swiss Ephemeris covers
  well beyond 2100. The 1900-2100 range is the standard for serious astrological software.

**Complexity:** MEDIUM.
- Requires running `tools/gen_chiron_coeffs.py` with extended `jd0/jd1` bounds.
- Requires `pyswisseph` + Swiss Ephemeris files (`seas_18.se1` etc.) covering 1900-2100.
- The `seas_18.se1` file covers 1800-2399 (well beyond needed range). HIGH confidence.
- Estimated additional segments: 1900-1950 adds ~50 years × 365.25/32 ≈ 571 segments;
  2050-2100 adds another ~571. Total ~2284 segments (was 1142), roughly doubles file
  size from ~297 KB to ~594 KB (lon+lat+dist). Acceptable.
- The generation script already exists and parameterizes `jd0/jd1`; this is an
  operational task, not a new algorithm.
- Must regenerate and commit the new NPZ; SemVer bump to v1.4.0 already warranted.

**Not a breaking change:** the evaluator (`ketu/ephemeris/planets.py` + cache) will
raise a bounds error for dates outside the current 1950-2050 range. Extending the range
turns those errors into valid positions — strictly additive.

---

## Feature Dependencies

```
Chiron orb fix (orb 0->4)
    └──requires──> Chiron ephemeris range extension (cannot usefully compute aspects
                   if many query dates fall outside 1950-2050 range; fix orb first,
                   extend range in same phase)
    └──required by──> Harmonic generator (to exercise Chiron aspects at H7/H11/etc.)

Harmonic generator
    └──builds on──> existing aspects/presets.py infrastructure (stateless, no dep)
    └──independent of──> frozen 14-row core.aspects table (parallel API)
```

---

## Anti-Features

| Anti-Feature | Why Requested | Why Problematic | Alternative |
|--------------|---------------|-----------------|-------------|
| Modify `core.aspects` to add H7/H11 rows | "Native" table integration | Breaks the Phase 9 frozen-14-row invariant; breaks all existing mask-indexed code; changes pickled numpy dtypes; requires SemVer major bump | Keep dynamic generator as a separate, transient API |
| Auto-deduplicate generator output against fixed table | Cleaner result | Generator loses its independence; must know about the fixed table; creates coupling | Let the caller decide; emit all k=1..h//2 angles |
| Expose Ketu internal harmonic numbering (H2=Square, H3=Sextile) in generator API | Consistent with internal column | Confuses users who expect H4=Square (standard convention); contradicts harmonic astrology literature | Use standard 360-based numbering in public API |
| Named aspects for H7/H11 as first-class `core.aspects` rows | Completeness | Blows up the frozen 14 invariant; minor aspects have no consensus naming or orb convention | Emit name/symbol as empty string or computed "H7k1" label from generator |

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Harmonic generator (H7, H11, H17 …) | HIGH | LOW | P1 — core v1.4 value |
| Chiron orb 0° → 4° | HIGH | VERY LOW (1 line + tests) | P1 — obvious fix |
| Chiron ephemeris 1900-2100 | MEDIUM | MEDIUM (build task + NPZ regen) | P2 — valuable but separable |

---

## Concrete Angles for QA Reference

Full 14 existing aspect angles (for regression testing the generator does not collide):
`0, 30, 36, 40, 60, 72, 80, 90, 108, 120, 144, 150, 160, 180`

Generator output for selected harmonics (angles in degrees, 6 decimal places):

**H7 (Septile series):** 51.428571, 102.857143, 154.285714
**H8 (Octile series):** 45.000000, 90.000000 (= Square), 135.000000
**H11 (Undecile series):** 32.727273, 65.454545, 98.181818, 130.909091, 163.636364
**H13:** 27.692308, 55.384615, 83.076923, 110.769231, 138.461538, 166.153846
**H17:** 21.176471, 42.352941, 63.529412, 84.705882, 105.882353, 127.058824, 148.235294, 169.411765

Note: H8 produces 90° (Square) — a generator must accept this overlap with the fixed
table without error. The consumer is responsible for deduplication if desired.

---

## Open Questions

1. **`aspects_for_harmonics` vs `generate_harmonic_aspects`:** Should v1.4 extend
   `aspects_for_harmonics` to accept arbitrary h (returning a dynamically-extended
   mask), or add a parallel `generate_harmonic_aspects(h)` returning a plain list?
   The latter is cleaner (no structural change to the mask API), but requires
   documentation that the two APIs coexist with different semantics. Recommendation:
   parallel function, but this is an API design decision for the roadmap phase.

2. **Chiron ephemeris build prerequisite:** extending to 1900-2100 requires
   `seas_18.se1` accessible at build time. The CI pipeline (or a developer with
   Swiss Ephemeris files) must run `gen_chiron_coeffs.py` and commit the new NPZ.
   This is an operational dependency, not a code dependency; needs a documented
   build step.

3. **Chiron orb: 4° or 2°?** Some practitioners argue Chiron warrants a tighter
   orb (2°) due to its minor-body status. The v1.3.1 scope note (in MEMORY.md)
   documents this unresolved. Research supports 4° as defensible; final choice is
   the user's preference.

---

## Sources

- John M. Addey, *Harmonics in Astrology* (1976/1977, Cambridge Circle) — foundational
  harmonic theory (via webSearch + Scribd reference; content not directly accessible)
- [Harmonics — Astro.com](https://www.astro.com/astrology/in_harmon_e.htm) — Addey
  overview; 360/h principle confirmed
- [Harmonic Charts Revisited — Halloran](https://www.halloran.com/harmonic.htm) —
  software implementation; "multiply radical positions by harmonic number"
- [Vibrational Astrology — David Cochrane](https://www.astrosoftware.com/harmonicfirst32.pdf) —
  orb = base_orb / h principle (Cochrane method; MEDIUM confidence, content not
  fully extractable)
- [Relocation Astrology — Vibrational Astrology Interlude](https://relocationastrologyguide.wordpress.com/2020/05/05/a-vibrational-astrology-interlude/) —
  angle multiplication mechanics confirmed
- [Astrological aspect — Wikipedia](https://en.wikipedia.org/wiki/Astrological_aspect) —
  aspect table, harmonic ratios
- [Aquarius Papers — Septile Series](https://aquariuspapers.substack.com/p/astrological-aspects-the-7th-harmonic) —
  H7 angles 51.4°/102.9°/154.3° confirmed
- [Chiron ephemeris 1920-2099 — Serennu](https://serennu.com/chironprint.html) —
  1920-2099 coverage confirming conventional range
- [Chiron orb conventions — saturnseason.com](https://saturnseason.com/aspects/what-the-hell-orb-should-i-use-and-when-and-why/) —
  2-4° most common for Chiron aspects
- Ketu codebase: `ketu/core.py`, `ketu/aspects/presets.py`, `ketu/data/chiron_coeffs.npz`,
  `tools/gen_chiron_coeffs.py`, `tests/synastry/test_modes_idempotent.py` — all
  verified by direct inspection (HIGH confidence)
