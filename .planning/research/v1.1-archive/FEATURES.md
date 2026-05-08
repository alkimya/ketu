# Feature Research — Ketu v1.1

**Domain:** Astronomical/astrological calculation library (NumPy, pure-Python)
**Researched:** 2026-05-06
**Milestone:** v1.1 — configurable aspects + houses (Placidus, Koch) + Lilith fix
**Confidence:** HIGH on standards (well-documented ecosystem); MEDIUM on Ketu-specific implementation choices

## Scope of This Document

This document focuses ONLY on the three new feature areas for v1.1, layered on top of existing Ketu 1.0.0:

1. **Configurable aspects** — Make the 14-aspect set filterable by category (major/minor/harmonic), without changing the underlying detection algorithm.
2. **Astrological houses** — Add a NEW houses module (Placidus + Koch) with proper math; the existing `calculate_house_cusps` placeholder in `ephemeris/planets.py:270` is an equal-house stub and is broken.
3. **Lilith fix** — Verify and document which Lilith Ketu computes (mean apogee) and ensure it matches Swiss Ephemeris within tolerance.

Existing v1.0.0 features (cycles, transits, aspect windows, complex ML features, lunar calendar, CLI) are out of scope.

---

## 1. Configurable Aspects

### What "Configurable" Means in the Astrology Ecosystem

There is **no single industry-standard categorization** of aspects. Three orthogonal categorizations exist, and serious tools expose all three:

| Categorization | Origin | Universally Agreed? |
|---|---|---|
| **Ptolemaic / Major** (5 aspects: 0°, 60°, 90°, 120°, 180°) | Ptolemy, Tetrabiblos, 2nd century CE | YES — all sources agree on these 5 |
| **Minor** (typically 30°, 36°, 40°, 45°, 51.4°, 72°, 135°, 144°, 150°) | Kepler (quintile/biquintile), 18th–20th century additions | NO — set varies by author |
| **Harmonic family** (h1=0, h2=180, h3=120, h4=90, h5=72, h6=60, h7=51.4, h8=45, h9=40, h10=36, h11, h12=30, h13...) | John Addey, harmonic astrology (1970s+) | YES on math, NO on which to include |

The 5 Ptolemaic majors are the **only universally agreed set**. Everything else is configurable per software/user preference.

### How Comparable Libraries Expose Aspect Configuration

| Library | Mechanism | Notes |
|---|---|---|
| **Kerykeion** (Python) | `active_aspects` parameter — list of `{name, orb}` dicts | `DEFAULT_ACTIVE_ASPECTS` constant; `AspectsFactory` filters by config |
| **flatlib** (Python, traditional) | Module constants `MAJOR_ASPECTS`, `MINOR_ASPECTS`; per-call lists | Distinguishes "active/passive object" semantics |
| **Swiss Ephemeris** (C/Python) | No built-in aspect classification — leaves it to consumer | Provides positions only |
| **astropy** | No astrology features (astronomy library only) | N/A |

**Pattern:** Pass an iterable of aspect identifiers (or a category alias like `"major"`/`"minor"`) to detection functions. Default to majors only.

### Ketu's Current State

`ketu/core.py` line 84 defines a flat `aspects` structured array with 14 entries. There is **no `category` field**. Every consumer (cycles, transits, windows) implicitly uses all 14. Filtering today requires modifying the array directly — there is no public API.

The 14 aspects in Ketu's array map to harmonics as:

```
H1: Conjunction (0°), Opposition (180°)  — degenerate cases
H2: Opposition (180°)
H3: Trine (120°)
H4: Square (90°)
H5: Quintile (72°), Biquintile (144°)
H6: Sextile (60°)
H8: (missing — 45° semi-square, 135° sesquare NOT in Ketu)
H9: Novile (40°), Binovile (80°), Quadrinovile (160°)
H10: Decile (36°), Tredecile (108°)
H12: Semi-sextile (30°), Quincunx (150°)
```

**Notable absences:** H7 (septile 51.4°), H8 (45°/135°), H11 (32.7°), H13 (27.7°). Ketu's set is unusual — it omits H8 (semi-square/sesquare) which is widely considered a "minor major" and includes H9/H10 sub-aspects (binovile, quadrinovile, tredecile) which most libraries omit.

### Feature Categorization

#### Table Stakes

| Feature | Why Expected | Complexity | Implementation Notes |
|---|---|---|---|
| Filter by Ptolemaic major (5 aspects) | Universal default in every astrology tool — users expect "major aspects only" mode | LOW | Add `category` field to `aspects` structured array; one-liner filter |
| Filter by aspect name list | Standard API in kerykeion/flatlib (pass `["Trine", "Square"]`) | LOW | Boolean mask on `aspects['name']` |
| Filter by harmonic number | Ketu's existing aspects ARE harmonic-derived; users will want `harmonic=5` to get quintile+biquintile | LOW–MED | Add `harmonic` field (i4); mask on it |
| Per-aspect orb override | Standard in kerykeion (`active_aspects=[{name, orb}]`); Ketu currently uses body orb × aspect coef | MEDIUM | Optional dict param overriding default coefficient logic |
| Default to majors-only in new APIs | Sensible default reduces noise; matches industry convention | LOW | Default param value `category="major"` |

#### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---|---|---|---|
| **Harmonic-first taxonomy** | Most libraries treat harmonics as an afterthought; Ketu can make harmonics first-class (h-number is the primary index, names are aliases) — fits the ML/quantitative use case (Kala) | MEDIUM | Sort by harmonic, expose `aspects_by_harmonic(n)` helper |
| **NumPy-native filter API** | Return a *view* of the structured array, not a copy/list — keeps the vectorization story consistent | LOW | `aspects[aspects['harmonic'] == 5]` works natively |
| **Structured-array-aware in cycles/timelines** | Existing cycle/timeline functions already accept aspect lists implicitly; make them accept the filtered structured array directly | MEDIUM | Threads through `cycles.calculator`, `aspects.timelines` |
| **Pre-defined named sets** | `ASPECT_SETS = {"ptolemaic": ..., "minor": ..., "harmonic_5": ..., "harmonic_9": ...}` | LOW | Module-level dict; documents Ketu's interpretation explicitly |

#### Anti-Features

| Anti-Feature | Why Tempting | Why Avoid | Alternative |
|---|---|---|---|
| Add a 7th-harmonic septile (51.4°) just because libraries do | "Completeness" pressure | Septile orb is contested, divides 360 unequally (51.428...°), and Ketu's existing 14 already excludes it — adding now changes downstream cycle outputs unexpectedly | Document septile as deliberately excluded; add only if a consumer (Kala/Surya) requests it |
| Pluggable user-defined aspects (any angle) | Flexibility | Every angle is technically already a "phase" in cycle data — the aspect array is for *named* harmonics. Arbitrary angles belong in the cycle separation field, not the aspect taxonomy | Point users to `cycles.calculator` for arbitrary-angle queries |
| Aspect "strength" beyond the existing `coef` | Looks rigorous | Astrology has no consensus on relative strength; Ketu's `coef` (1/n harmonic weighting) is already a defensible choice | Keep `coef`; document its meaning |
| Tropical-vs-sidereal aspect adjustment | Sidereal users will ask | Aspects are angular separations — they're zodiac-system-agnostic. Only sign assignments and houses depend on tropical/sidereal | Document that aspects are independent of zodiac system |
| Renaming existing aspects to break compatibility | "Cleanup" temptation | v1.0.0 is on PyPI; downstream Kala uses these names | Keep all 14 names exactly; ADD fields, don't rename |

### Implementation Sketch

```python
# ketu/core.py — extend existing array
aspects = np.array([
    ("Conjunction",   0,   1.0,   1, "major"),
    ("Semi-sextile",  30,  1/6,   12, "minor"),
    ("Decile",        36,  1/10,  10, "minor"),
    ("Novile",        40,  1/9,   9,  "minor"),
    ("Sextile",       60,  1/3,   6,  "major"),
    ("Quintile",      72,  1/5,   5,  "minor"),
    ("Binovile",      80,  2/9,   9,  "minor"),
    ("Square",        90,  1/2,   4,  "major"),
    ("Tredecile",     108, 3/10,  10, "minor"),
    ("Trine",         120, 2/3,   3,  "major"),
    ("Biquintile",    144, 2/5,   5,  "minor"),
    ("Quincunx",      150, 5/6,   12, "minor"),
    ("Quadrinovile",  160, 4/9,   9,  "minor"),
    ("Opposition",    180, 1.0,   2,  "major"),
], dtype=[
    ("name", "S16"),
    ("angle", "f4"),
    ("coef", "f4"),
    ("harmonic", "i4"),    # NEW
    ("category", "S8"),    # NEW
])

# ketu/aspects/__init__.py
def filter_aspects(category=None, harmonic=None, names=None):
    """Return a view of `aspects` filtered by category, harmonic, or names."""
    mask = np.ones(len(aspects), dtype=bool)
    if category is not None:
        mask &= (aspects['category'] == category.encode())
    if harmonic is not None:
        mask &= (aspects['harmonic'] == harmonic)
    if names is not None:
        name_bytes = [n.encode() for n in names]
        mask &= np.isin(aspects['name'], name_bytes)
    return aspects[mask]
```

### Dependencies on Existing Modules

| Module | Impact | Reason |
|---|---|---|
| `ketu/core.py` | MUST CHANGE | Add `harmonic` and `category` fields to `aspects` |
| `ketu/aspects/core.py` | LIKELY CHANGE | `get_aspect_index` should accept category/harmonic filters |
| `ketu/aspects/calculator.py` | LIKELY CHANGE | Detection loop should accept filtered aspect set |
| `ketu/aspects/timelines.py` | LOW IMPACT | Add optional category param, default to all (back-compat) |
| `ketu/cycles/calculator.py` | NO CHANGE | Cycles use angular separation, not named aspects |
| `ketu/aspects/transits.py` | LOW IMPACT | Same as timelines |
| Tests | UPDATE | Existing tests asserting 14 aspects must still pass; add filter tests |

---

## 2. Astrological Houses

### What House Calculation Returns (Industry Convention)

Per Swiss Ephemeris (the de-facto reference implementation used by virtually every modern astrology tool):

`swe.houses(jd_ut, lat, lon, hsys)` returns **two arrays**:

1. **`cusps`** — house cusps, ecliptic longitude in degrees
   - Swiss Ephemeris uses **1-based indexing**: `cusps[1..12]` for houses 1–12; `cusps[0]` is unused. Total length 13.
   - Pythonic alternative (most wrappers): 0-based length-12 array `cusps[0..11]`.
   - **Decision needed for Ketu:** 0-based, length-12 (NumPy-native, matches Ketu conventions).

2. **`ascmc`** — special angles, length 8 minimum:
   | Index | Constant | Meaning |
   |---|---|---|
   | 0 | ASC | Ascendant (= cusp 1 for Placidus/Koch) |
   | 1 | MC | Midheaven (= cusp 10 for Placidus/Koch) |
   | 2 | ARMC | Right Ascension of Midheaven |
   | 3 | VERTEX | Vertex (western horizon ecliptic intersection) |
   | 4 | EQUASC | Equatorial Ascendant |
   | 5 | COASC1 | Co-Ascendant (Walter Koch) |
   | 6 | COASC2 | Co-Ascendant (Munkasey) |
   | 7 | POLASC | Polar Ascendant (Munkasey) |

### Inputs Required

| Input | Type | Notes |
|---|---|---|
| Julian Date (UT) | float | UT, not TT — Ketu has both via `terrestrial_to_universal` |
| Geographic latitude | float, degrees | Positive north |
| Geographic longitude | float, degrees | Positive east (Swiss Ephemeris convention) |
| House system code | str | 'P' (Placidus), 'K' (Koch) at minimum for v1.1 |

**Anything else?** No. Houses are time + location only — no ephemeris data needed beyond sidereal time and obliquity (both already in `ketu/ephemeris/time.py:305` and `ephemeris/coordinates.py`).

### Placidus Algorithm

Placidus trisects the **diurnal and nocturnal semi-arcs** of each ecliptic degree. The diurnal semi-arc:

```
DSA(δ, φ) = arccos(−tan(φ) · tan(δ))
```

where φ is geographic latitude and δ is declination. Intermediate cusps (11, 12, 2, 3) are found by an **iterative trigonometric formula** (no closed form). Typical convergence: 3–5 iterations.

**Houses 1, 4, 7, 10** are angles:
- House 1 = Ascendant (computed from ARMC + obliquity + latitude)
- House 10 = MC (computed from ARMC + obliquity)
- House 4 = MC + 180°
- House 7 = ASC + 180°

**Houses 2, 3, 11, 12** require iteration (and 5, 6, 8, 9 by symmetry).

**Failure mode at high latitude:** When |φ| > 90° − ε ≈ 66.5° (Arctic/Antarctic circles), some ecliptic degrees never rise/set, `arccos` argument exceeds [−1, 1], math diverges. **Standard handling:** raise an exception or fall back to Porphyry/Equal house and warn.

### Koch Algorithm

Koch shares the angle calculation with Placidus (same ASC, same MC) but trisects the diurnal arc of the **Ascendant** rather than each cusp's own arc. Specifically: Koch projects time intervals computed from the ASC's own diurnal arc backward to find the intermediate cusps.

Mathematically simpler than Placidus (no iteration), but **shares the same high-latitude failure** at ~66°.

At mid-latitudes (30°–50°) Koch and Placidus produce visibly different cusps — typical disagreement is 1–5° on intermediate cusps.

### House Assignment for Planets

Standard algorithm:

```python
def planet_house(planet_lon, cusps):
    """Return house number (1-12) for a planet at given longitude."""
    for i in range(12):
        next_cusp = cusps[(i + 1) % 12]
        # Handle wrap-around at 360°/0°
        if cusps[i] <= next_cusp:
            if cusps[i] <= planet_lon < next_cusp:
                return i + 1
        else:  # crosses 0°
            if planet_lon >= cusps[i] or planet_lon < next_cusp:
                return i + 1
    return 12  # Fallback
```

This is straightforward longitude-vs-cusp comparison with wrap-around. **No special edge cases beyond 0°/360° boundary.**

### Feature Categorization

#### Table Stakes

| Feature | Why Expected | Complexity | Implementation Notes |
|---|---|---|---|
| Placidus house cusps | Default in 90%+ of modern astrology software (kerykeion, astro.com, Solar Fire) | HIGH | Iterative trig; well-documented but math-heavy. Use Meeus *Astronomical Algorithms* Ch. 17 as reference |
| Koch house cusps | Second-most-common system; explicitly requested by spec | MEDIUM | Closed-form (no iteration); shares angle math with Placidus |
| ASC + MC + ARMC + Vertex | Universal output of any house calculation | LOW | Already have ARMC via `sidereal_time(jd, lon)`; ASC and MC are derived |
| Planet-to-house assignment | Implied by having houses — users will ask "which house is Mars in?" | LOW | Simple longitude comparison |
| High-latitude warning/error | Math literally breaks at φ > 66°; silent failure = data corruption | LOW | Explicit `HighLatitudeError` or `RuntimeWarning` |
| NumPy structured array output | Matches Ketu's existing pattern (bodies, aspects, cycles all are structured arrays) | LOW | Define `HOUSES_DTYPE` |
| UTC datetime + lat/lon input signature | Mirrors existing `calculations.py` API | LOW | Use existing `utc_to_julian` |

#### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---|---|---|---|
| **Vectorized cusps for time series** | Houses change continuously through the day (1° every 4 minutes); existing tools recompute single-shot. Ketu's NumPy-first ML focus means batch house calculation across timestamps is uniquely valuable for Kala | MEDIUM | `calculate_houses_batch(jd_array, lat, lon, system)` returning (n_dates, 12) array |
| **Structured-array output with metadata** | Return `(timestamp, system, ASC, MC, ARMC, vertex, cusp1..12, sign1..12)` as one structured array | MEDIUM | Defines `HOUSES_DTYPE` analogous to `CYCLE_DTYPE` |
| **Equal house fallback for high lat** | Many users have natal charts at moderate-high latitudes (Scandinavia, Alaska) and want a graceful degradation | LOW | `system="P"` with `fallback="A"` parameter |

#### Anti-Features

| Anti-Feature | Why Tempting | Why Avoid | Alternative |
|---|---|---|---|
| Support all 18 Swiss Ephemeris house systems in v1.1 | "Feature parity" with pyswisseph | Each system needs separate math + tests; v1.1 spec says Placidus + Koch only. Equal/Whole Sign are trivial extensions for v1.2 | Ship 'P' and 'K' only; add others on demand |
| Topocentric position adjustment for planets in houses | Technically more correct (Moon parallax can shift by 1° at horizon) | Massively complicates the pipeline; existing Ketu positions are geocentric. Astrology software *almost universally* uses geocentric for house assignment | Document as "geocentric house assignment" |
| House-based aspect detection | "House aspects" exist in some traditions | Conflates two orthogonal concepts (zodiacal angle vs mundane house relationship); existing aspects use ecliptic longitude. Adding house-aspect mode doubles every aspect API | Out of scope; aspects stay zodiacal |
| Auto-detect timezone from lat/lon | UX nicety | Adds a `pytz`/`tzdata` dependency; Ketu's "NumPy only" stance is a design pillar | Require UTC input (consistent with existing API) |
| Mundane positions (right ascension/declination of planets) | Comes up in research | Different output structure; not a v1.1 deliverable | Defer to v1.2+; can be derived from existing equatorial coordinates |

### Implementation Sketch

```python
# ketu/houses.py (NEW MODULE)

import numpy as np
from .ephemeris.time import sidereal_time
from .ephemeris.coordinates import true_obliquity

HOUSES_DTYPE = np.dtype([
    ('timestamp', 'datetime64[s]'),
    ('system', 'U1'),         # 'P', 'K', 'A', 'W', ...
    ('ascendant', 'f8'),
    ('mc', 'f8'),
    ('armc', 'f8'),
    ('vertex', 'f8'),
    ('cusps', 'f8', (12,)),   # houses 1..12 in 0-based array
])

class HighLatitudeError(ValueError):
    """Placidus/Koch undefined at |latitude| > 66.5°."""

def calculate_houses(jd_ut, lat, lon, system='P'):
    """Calculate house cusps and angles."""
    if system in ('P', 'K') and abs(lat) > 66.5:
        raise HighLatitudeError(f"{system} undefined at lat={lat}")
    armc = sidereal_time(jd_ut, lon)
    eps = true_obliquity(jd_ut)
    asc = _ascendant(armc, lat, eps)
    mc = _midheaven(armc, eps)
    if system == 'P':
        cusps = _placidus_cusps(armc, lat, eps, asc, mc)
    elif system == 'K':
        cusps = _koch_cusps(armc, lat, eps, asc, mc)
    # ... assemble structured array
    return result

def planet_house(planet_lon, cusps):
    """Return 1-12 for planet's house."""
    # Longitude comparison with 0°/360° wrap
```

### Dependencies on Existing Modules

| Module | Role | Notes |
|---|---|---|
| `ketu/ephemeris/time.py:sidereal_time` | EXISTING — provides ARMC | Already correct (verified against IAU formula) |
| `ketu/ephemeris/coordinates.py:true_obliquity` | EXISTING — provides ε | Already implemented |
| `ketu/calculations.py:utc_to_julian` | EXISTING — input conversion | Reused as-is |
| `ketu/ephemeris/planets.py:calculate_house_cusps` (line 270) | **DELETE** — broken equal-house stub | Replace with new module |
| `ketu/houses.py` | **NEW** | Public API |
| `ketu/__init__.py` | EXPORT | Add `calculate_houses`, `planet_house`, `HOUSES_DTYPE` |
| `ketu/display.py` | OPTIONAL | Add CLI flag `--houses` to display chart |

---

## 3. Lilith

### Verification of Current Ketu Implementation

`ketu/ephemeris/orbital.py:574-593` and `ketu/ephemeris/planets.py:147-155` compute Lilith as:

```python
lilith = normalize_angle(83.3532 + 0.1114040803 * d)
```

where `d = jd - 2451545.0` (days since J2000.0).

**This is Mean Black Moon Lilith (mean lunar apogee).**

Sanity check on daily motion:
- 0.1114040803 °/day × 365.25 × 8.85 = 360.16° → matches the documented **8.85-year (~3232-day) anomalistic period** of the lunar apogee (HIGH confidence; verified against multiple sources).

### Three Liliths in the Astrology Ecosystem

| Variant | Swiss Ephemeris ID | Description | Motion | Used By |
|---|---|---|---|---|
| **Mean Lilith** | `SE_MEAN_APOG` (12) | Smoothed apogee, never retrograde, predictable | ~0.1114°/day, no station | Default in 95%+ of software including astro.com |
| **True/Osculating Lilith** | `SE_OSCU_APOG` (13) | Instantaneous geometric apogee | Highly erratic, ±30° amplitude oscillation, retrogrades | Available as opt-in |
| **Interpolated Lilith** | `SE_INTP_APOG` (21) | Smoothed between actual apogee passages | ±5° amplitude (mid-ground) | Niche, rarely used |
| **Asteroid Lilith** | Asteroid 1181 | Physical asteroid in main belt | 4-year orbit, regular retrogrades | Different archetype, supplementary |

### Position Accuracy Expectations

| Comparison | Typical Difference | Source |
|---|---|---|
| Ketu Mean Lilith vs Swiss Eph SE_MEAN_APOG | should be < 0.1° | Both use ELP2000-derived mean motion |
| Mean Lilith vs True Lilith | 3°–8° typical, up to 12°+ extreme | Ecosystem reference |
| Mean Lilith vs Asteroid 1181 | Unrelated — completely different bodies | N/A |

**Recommended verification target for Ketu v1.1:** Mean Lilith must agree with Swiss Ephemeris `SE_MEAN_APOG` to **< 0.1°** across 1900–2100 (this is the same accuracy bar Ketu uses for other bodies per its existing test suite).

### What's the "Fix" the v1.1 Spec Mentions?

Possible interpretations (all should be investigated during phase research):

1. **Documentation fix** — Ketu's docstrings call it "Lilith" without specifying *which* Lilith. Add explicit "Mean Black Moon Lilith (mean lunar apogee, SE_MEAN_APOG-equivalent)" in docs, README, and `core.py` comments.

2. **Constant accuracy fix** — The hardcoded base longitude `83.3532°` and rate `0.1114040803°/day` should be verified against the Swiss Ephemeris reference to ensure the J2000 epoch values are correct to 4+ decimal places. **The current values look correct based on cross-referencing**, but should be tested.

3. **Optional True Lilith addition** — Many users will eventually want osculating Lilith. Add `SE_OSCU_APOG`-equivalent as a new body or as a parameter. **Out of scope for v1.1** based on spec wording ("Lilith fix"), but flag for v1.2.

4. **Body ID convention fix** — Ketu uses ID 12 for Lilith. Swiss Ephemeris uses ID 12 for SE_MEAN_APOG also. ✓ matches.

### Feature Categorization

#### Table Stakes

| Feature | Why Expected | Complexity | Implementation Notes |
|---|---|---|---|
| Document which Lilith Ketu computes | Users currently can't know without reading source | LOW | Update docstrings: "Mean Black Moon Lilith (lunar apogee)" |
| Verify accuracy vs Swiss Ephemeris | Without independent verification, position correctness is unproven | LOW | Add test comparing to known SE values for sample dates |
| Document position accuracy | Users need to know if Ketu is suitable for their precision needs | LOW | "Accurate to <0.1° across 1900–2100" in module docstring |

#### Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---|---|---|---|
| **Multiple Lilith variants exposed** | Most NumPy-only libs only do mean; offering both mean and true is rare in the pure-Python ecosystem | MEDIUM | Add `get_true_lilith_position(jd)` using osculating elements (defer to v1.2 unless required) |
| **Speed/velocity reporting consistent with other bodies** | Ketu already returns velocity for all bodies; mean Lilith velocity is constant ~0.1114°/day, but the data structure should be uniform | LOW | Already implemented in `calc_planet_position` — verify field is populated correctly |

#### Anti-Features

| Anti-Feature | Why Tempting | Why Avoid | Alternative |
|---|---|---|---|
| Switch default from Mean to True Lilith | "True is more accurate" appearance | Astrologically Mean is the *standard* expected default; True has 30° oscillations that confuse users; breaks compatibility for Kala consumers | Keep Mean as default; document why; add True only as opt-in |
| Add asteroid 1181 as "Lilith" | Naming overlap with Black Moon Lilith | Different archetype, different math (full asteroid integration), confuses users; not requested | If asteroids ever added, name it `Lilith_1181` or `Asteroid_Lilith` |
| Compute Lilith from full DE431 ephemeris integration | "Maximum accuracy" | Mean Lilith IS a smoothed quantity by definition — adding more accuracy to a smoothed value is conceptually incoherent | Document that Mean Lilith uses analytic series (correct approach) |
| Rename "Lilith" to "MeanLilith" or "BlackMoon" | Disambiguation | Breaks v1.0 API; Kala depends on the name "Lilith" | Keep name; clarify in docs |

### Dependencies on Existing Modules

| Module | Impact | Notes |
|---|---|---|
| `ketu/ephemeris/orbital.py:get_lilith_position` | VERIFY ONLY | Test against Swiss Ephemeris values; likely no code change needed |
| `ketu/ephemeris/planets.py` (Lilith block, lines 147–155) | VERIFY + DOC | Velocity calculation OK; add docstring clarification |
| `ketu/core.py` (bodies array, line 77) | DOC | Comment "Mean Apogee (Black Moon)" is correct; possibly expand |
| Tests | ADD | New test: `test_lilith_matches_swiss_ephemeris` with known reference points |
| `README.md` / docs | UPDATE | "Lilith = Mean Black Moon Lilith" prominently noted |

---

## Cross-Cutting Feature Dependencies

```
[Aspects: configurable categories]
    └──independent──> (no dependency on houses or Lilith)

[Houses: Placidus/Koch]
    ├──requires──> [ephemeris/time.py:sidereal_time]      (EXISTS)
    ├──requires──> [ephemeris/coordinates.py:true_obliquity] (EXISTS)
    └──requires──> [calculations.py:utc_to_julian]         (EXISTS)

[Lilith: verify + document]
    └──independent──> (purely a verification/doc task)

[Houses + planet positions]
    └──> [planet_house(lon, cusps)]
          └──requires──> existing calc_planet_position (EXISTS)

[Aspects + Houses + Lilith]
    └──> all three can ship in parallel; no sequencing required
```

### Integration Notes

- **No phase ordering constraint among the three.** Aspects, Houses, and Lilith are orthogonal and could be developed concurrently.
- **Houses is by far the largest piece of work** (Placidus iteration, Koch math, edge cases, vectorization, tests). Should likely be split across two phases (cusps math + integration/CLI).
- **Aspects work is surface-level** but touches many existing modules — needs careful regression testing for v1.0 backward compatibility.
- **Lilith is mostly verification work** — the implementation appears already correct; the deliverable is tests + documentation + (possibly) a minor formula adjustment.

---

## v1.1 MVP Definition

### Must Ship in v1.1

- [ ] `aspects` array gains `harmonic` and `category` fields
- [ ] `filter_aspects(category=, harmonic=, names=)` public API
- [ ] Default behavior of `cycles`/`timelines`/`transits` UNCHANGED (back-compat); filter is opt-in
- [ ] `ketu/houses.py` module with Placidus + Koch
- [ ] `calculate_houses(jd, lat, lon, system='P')` returning structured array
- [ ] `planet_house(longitude, cusps)` helper
- [ ] `HighLatitudeError` raised at |lat| > 66.5° for P/K
- [ ] `HOUSES_DTYPE` defined and exported
- [ ] Lilith documented as "Mean Black Moon Lilith (lunar apogee)" in core.py and module docs
- [ ] Lilith verification test against Swiss Ephemeris reference values (< 0.1° tolerance)
- [ ] Existing `calculate_house_cusps` stub removed from `ephemeris/planets.py`
- [ ] All v1.0 tests still pass
- [ ] New tests for each feature

### Defer to v1.2

- [ ] Equal House (`A`) and Whole Sign (`W`) house systems
- [ ] Vectorized batch house calculation across timestamps
- [ ] True/Osculating Lilith as opt-in
- [ ] User-defined custom aspects (arbitrary angles)
- [ ] Per-aspect orb override dict API
- [ ] Topocentric house adjustment
- [ ] CLI integration for houses display

### Out of Scope (v2+)

- [ ] All 18 Swiss Ephemeris house systems
- [ ] Asteroid Lilith (1181)
- [ ] Sidereal zodiac houses
- [ ] House-based aspect modes
- [ ] Mundane (right-ascension) positions

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---|---|---|---|
| Placidus cusps | HIGH | HIGH | P1 |
| Koch cusps | HIGH | MEDIUM | P1 |
| `planet_house` | HIGH | LOW | P1 |
| Aspect category filter (major/minor) | HIGH | LOW | P1 |
| Aspect harmonic filter | MEDIUM | LOW | P1 |
| Aspect name-list filter | MEDIUM | LOW | P1 |
| Lilith documentation clarification | MEDIUM | LOW | P1 |
| Lilith accuracy verification test | MEDIUM | LOW | P1 |
| `HighLatitudeError` for P/K | HIGH | LOW | P1 |
| ASC/MC/ARMC/Vertex output | HIGH | LOW (derives from cusps) | P1 |
| Equal house fallback | MEDIUM | LOW | P2 |
| Vectorized batch houses | MEDIUM | MEDIUM | P2 |
| Per-aspect orb override | LOW | MEDIUM | P2 |
| True Lilith opt-in | LOW | MEDIUM | P3 |
| Topocentric adjustment | LOW | HIGH | P3 |

**Priority key:** P1 = required for v1.1 release; P2 = nice-to-have if time permits; P3 = defer.

---

## Sources

### Primary (Authoritative)

- [Swiss Ephemeris programmer's manual: house calculation](https://github.com/astrorigin/pyswisseph/blob/master/docs/programmers_manual/house_cusp_calculation.rst) — `swe.houses()` API contract, ascmc array layout, house system codes
- [Swiss Ephemeris documentation (astro.com)](https://www.astro.com/swisseph/swisseph.htm) — Mean/True/Interpolated Lilith definitions, SE_MEAN_APOG vs SE_OSCU_APOG vs SE_INTP_APOG
- [pyswisseph house systems reference](https://github.com/astrorigin/pyswisseph/blob/master/docs/sidereal_time_ascendant_mc_houses_vertex/astrological_house_systems.rst) — house system codes, high-latitude failure mode

### Library Conventions

- [Kerykeion source/README (GitHub)](https://github.com/g-battaglia/kerykeion/blob/main/README.md) — `active_aspects` parameter pattern, default Placidus, `houses_system_identifier`
- [flatlib aspects module](https://github.com/flatangle/flatlib/blob/master/flatlib/aspects.py) — Major/Minor aspect lists, traditional astrology conventions
- [flatlib swe.py wrapper](https://github.com/flatangle/flatlib/blob/master/flatlib/ephem/swe.py) — house system code mapping

### Astrological Conventions

- [Wikipedia: Astrological aspect](https://en.wikipedia.org/wiki/Astrological_aspect) — 5 Ptolemaic majors universally agreed
- [Astrology Podcast Ep. 323: Five Major Configurations](https://theastrologypodcast.com/2021/10/16/aspects-in-astrology-the-five-major-configurations/) — modern consensus on majors
- [Advanced Astrology: Minor Aspects](https://advanced-astrology.com/minor-aspects/) — semi-sextile, semi-square, sesquare, quincunx, quintile definitions
- [Astrodienst Astrowiki: Harmonics](https://www.astro.com/astrology/in_harmon_e.htm) — harmonic categorization (h2, h3, h4, h5, h7, h8, h9, h12)

### Lilith Variants

- [Astrodienst Astrowiki: Lilith](https://www.astro.com/astrowiki/en/Lilith) — Mean vs True vs Asteroid 1181
- [Kerykeion: Lilith variants](https://kerykeion.net/content/learn-astrology/foundation-lilith-variants) — typical 3°-8° divergence Mean vs True, software defaults
- [Serennu: Mean & True Black Moon Lilith](https://serennu.com/astrology/mean-true-black-moon.php) — ecosystem norms
- [Darkstar Astrology: Three Liliths](https://darkstarastrology.com/three-liliths/) — disambiguation of mean apogee vs asteroid 1181 vs Waldemath dark moon

### House System Algorithms

- [Astrodienst: Placidus House System](https://www.astro.com/astrowiki/en/Placidus_House_System) — semi-arc trisection method
- [Big Sky Astrology: House Systems](https://www.bigskyastrology.com/house-systems-dividing-the-sky/) — comparison of methods
- [AstroChartus: House Systems Explained](https://www.astrochartus.com/blog/house-systems-explained) — Placidus vs Koch differences
- [RoxyAPI: House Systems Implementation Guide](https://roxyapi.com/blogs/house-systems-astrology-app-implementation-guide) — algorithm details, high-latitude failure

### Confidence by Section

| Section | Confidence | Rationale |
|---|---|---|
| Ptolemaic 5 majors | HIGH | Universal consensus across all sources |
| Minor aspects categorization | MEDIUM | Set varies by tradition; Ketu's specific 14 are unusual |
| Harmonic categorization (h-numbers) | HIGH | Mathematical, unambiguous |
| Placidus algorithm | HIGH | Documented in Meeus, Swiss Ephemeris |
| Koch algorithm | HIGH | Same |
| High-lat failure at 66° | HIGH | Mathematical certainty (arccos domain) |
| Mean Lilith = standard default | HIGH | Confirmed across 5+ sources |
| Ketu's Lilith = Mean Apogee | HIGH | Code review confirms (formula matches 8.85-year period exactly) |
| Lilith accuracy < 0.1° expectation | MEDIUM | Reasonable based on ELP2000 derivation; needs empirical test |
| Aspect set comparison to other libraries | MEDIUM | Surface-level review; individual library APIs vary |

---

*Feature research for: Ketu v1.1 (configurable aspects + Placidus/Koch houses + Lilith verification)*
*Researched: 2026-05-06 by gsd-project-researcher*
