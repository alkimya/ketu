# Declination δ — Technical Brief (Ketu v1.5)

**Researched:** 2026-06-03
**Scope:** Pure astronomical definition of equatorial declination δ and its rate of change, for a pure-NumPy `ketu` feature. NOT zodiacal/Thun/constellation work — this is angular/equatorial mechanics of a single body (the Moon especially).
**Overall confidence:** HIGH (formulas verified numerically against ketu's own coordinate chain; period/standstill facts cross-checked against Meeus + Wikipedia + multiple references).

---

## 1. Declination δ — definition, formula, computation path

### Definition

Declination δ is the angular distance of a body north (+) or south (−) of the **celestial equator**, the equatorial-coordinate analogue of ecliptic latitude β. It is bounded `δ ∈ [−90°, +90°]`. Its companion is right ascension α (the equatorial analogue of ecliptic longitude λ). North is positive, south negative — the universal convention; ketu should follow it.

### Exact spherical-trig formula (Meeus, *Astronomical Algorithms* 2nd ed., Ch. 13, eq. 13.4)

Given ecliptic longitude λ, ecliptic latitude β, and obliquity of the ecliptic ε:

```
sin δ = sin β · cos ε + cos β · sin ε · sin λ              (Meeus 13.4)

tan α = (sin λ · cos ε − tan β · sin ε) / cos λ            (Meeus 13.3)
```

- δ is recovered with `arcsin` (no quadrant ambiguity, since δ ∈ [−90°,+90°]).
- α must use `arctan2(numerator, denominator)` to land in the correct quadrant, then normalize to [0°,360°). (ketu's `rectangular_to_spherical` already does exactly this.)

**The question's stated formula `sin δ = sin β cos ε + cos β sin ε sin λ` is CONFIRMED correct** (HIGH — it is Meeus eq. 13.4 verbatim, and verified numerically below).

### Equivalence with the existing `coordinates.py` chain — VERIFIED

The rectangular path already present in ketu is:

```
spherical_to_rectangular(λ, β, r)   →  (x, y, z)        ecliptic rectangular
ecliptic_to_equatorial(x, y, z, ε)  →  (xₑ, yₑ, zₑ)     equatorial rectangular
rectangular_to_spherical(xₑ,yₑ,zₑ)  →  (α, δ, r)        α = lon, δ = lat
```

I numerically compared this chain against the direct Meeus 13.4/13.3 formulas (ε = 23.4392911°) across λ ∈ {0,45,90,120,200,270,310}, β ∈ {0,±2.1,±3.5,±4.8,±5.14}:

| λ | β | δ direct | δ chain | Δδ | α direct | α chain | Δα |
|---|---|----------|---------|-----|----------|---------|-----|
| 45 | 3.5 | 19.67943 | 19.67943 | 0 | 41.44694 | 41.44694 | 0 |
| 90 | 5.14 | 28.57929 | 28.57929 | 0 | 90.00000 | 90.00000 | 0 |
| 270 | −5.14 | −28.57929 | −28.57929 | 0 | 270.00000 | 270.00000 | 0 |
| 310 | −4.8 | −22.35965 | −22.35965 | 0 | 313.83688 | 313.83688 | ~3e-14 |

**Δ is zero to machine precision.** The two are mathematically identical (the rectangular rotation about the x-axis is exactly the matrix form of eqs. 13.3/13.4). **Reusing the existing `coordinates.py` chain is correct and produces the canonical declination.** No new trig code is strictly required — only an assembly function.

Note the diagnostic row λ=90°, β=5.14° → δ = 28.579° = ε + β: the Moon at its orbital-inclination peak, sitting at the solstitial longitude, reaches `ε + i` (the major-standstill geometry, §2/§3).

### Recommended computation path for `declination(jdate, body)`

Two equivalent implementation styles; pick one (§5 design decision):

1. **Reuse rectangular chain** (DRY, leans on tested code):
   `λ, β = long(jd,body), lat(jd,body)` → `spherical_to_rectangular(λ,β,1.0)` → `ecliptic_to_equatorial(...,ε(jd))` → `rectangular_to_spherical(...)`, return the latitude component.
2. **Direct formula** (one-liner, slightly faster, self-documenting as δ):
   `δ = arcsin( sinβ·cosε + cosβ·sinε·sinλ )`.

Both are fully vectorizable over date arrays with `np.deg2rad`/`np.arcsin`. Recommendation: **direct formula** for the public `declination()` (clarity, it literally is "the declination"), with a unit test asserting equality to the rectangular chain to lock the equivalence in regression.

### Which obliquity — `true_obliquity` or `mean_obliquity`?

Numerically (at J2000): mean ε = 23.439291°, true ε = 23.437691°, difference 5.76″. The induced declination error from using mean vs true ε peaks where `∂δ/∂ε` is largest (near λ=90°/270°): **~5.8″ at J2000, up to ~9″ at maximum nutation** (nutation-in-obliquity amplitude ≈ ±9.2″ over the 18.6-yr cycle, per ketu's own `nutation()` leading term `9.20·cos Ω`). 9″ = 0.15 arcmin.

**At daily resolution this is negligible; at arcminute reporting it is below the 1′ tick but not zero.** This is a genuine design choice — see §5.

**Sources:** Meeus eqs. 13.3, 13.4 (Ch. 13 "Transformation of Coordinates"); numerical verification against ketu `coordinates.py` (this brief). Confidence HIGH.

---

## 2. Montant / Descendant — declination trajectory

### Definition (aspect-centric, single-body state)

This is a property of the **Moon alone**, not relative to any constellation:

- **Montante (ascending in declination):** `dδ/dt > 0` — the Moon is climbing toward the celestial equator's north / toward its northern declination extreme.
- **Descendante (descending in declination):** `dδ/dt < 0` — the Moon is sinking toward / past the equator southward.

This is the *equatorial* analogue of ketu's existing `is_ascending()`, which tests **ecliptic-latitude** velocity (`lat_velocity > 0`). The two are different physical quantities — β-rising vs δ-rising — and will not flip on the same days. The new helper should be named to avoid confusion with `is_ascending` (e.g. `is_declination_ascending` / `is_montante`).

> Design caution worth flagging to the user: the memory note `project_future_lunar_declination` records that for biodynamics, *latitude* `is_ascending` was deemed "sufficient at daily resolution." The δ-trajectory (montant/descendant) is the **true biodynamic ascending/descending Moon** in the astronomical (Kolisko/declination) sense, distinct from β. Confirm which one the v1.5 feature targets. This brief assumes the genuine δ-trajectory.

### Period that governs the δ cycle — the DRACONIC (nodal) month

The Moon's declination completes one full oscillation (max δ → min δ → max δ) once per **node-to-node passage**. Precise periods:

| Month type | Reference frame | Days |
|------------|-----------------|------|
| Synodic (new→new) | Sun | 29.530589 |
| Anomalistic (perigee→perigee) | apse | 27.554550 |
| Sidereal (vs stars) | fixed stars | 27.321662 |
| Tropical (vs equinox) | vernal equinox | 27.321582 |
| **Draconic / nodal (node→node)** | **lunar nodes** | **27.212221** |

**Why the draconic/nodal month, not sidereal or synodic:** declination is fixed by the body's *position relative to the celestial equator*. The Moon's path crosses the equator where its orbit's relation to the equatorial plane changes sign — and the Moon's orbital plane is anchored by its **nodes** (the line where the lunar orbit meets the ecliptic). The Moon reaches maximum |δ| a quarter-orbit from the ascending node and crosses δ≈0 near the nodes. Because the nodes regress (~19.3°/yr, full circle in 18.6 yr), the node-to-node return — the **draconic month** — is the period over which the declination geometry exactly repeats. The synodic month (Sun) is irrelevant to δ; the sidereal month (stars) and tropical month (equinox) are close but anchored to the wrong reference for the node-governed swing.

**Nuance (do not over-claim):** Sources sometimes state the declination "completes a cycle once every tropical month of 27.3 d" (e.g. Wikipedia). Both are defensible: the *extreme-to-extreme recurrence* tracks the tropical month (~27.32 d) because the solstitial longitudes are equinox-anchored, while the *node-to-node geometry* that sets the amplitude is the draconic month (~27.21 d). They differ by only ~0.11 d (~2.6 h). **For requirements: state the period as the draconic/nodal month ≈ 27.21 d as the physically-correct driver of the δ swing, and note the ~27.32 d tropical figure as the near-equal extreme-recurrence value.** At daily resolution they are indistinguishable; this distinction is a documentation precision point, not an implementation fork.

### Turning points (max/min δ)

- The Moon's instantaneous declination extreme each month is approximately `±(ε + β_node)` where β_node is the Moon's ecliptic latitude contribution at the solstitial longitude; the *envelope* of these monthly extremes is `±(ε ± i)`, i = 5.14° lunar orbital inclination.
- **Max possible:** `ε + i ≈ 23.44 + 5.14 ≈ 28.6°` (major standstill).
- **Min of the envelope:** `ε − i ≈ 23.44 − 5.14 ≈ 18.3°` (minor standstill).
- At a turning point `dδ/dt = 0` (sign change of velocity) — these are the monthly "lunistices."

**Sources:** Meeus Ch. 13/47; period values standard (USNO/Meeus); Wikipedia "Lunar standstill"; numerical check (this brief). Confidence HIGH for periods and envelope; the tropical-vs-draconic nuance is MEDIUM (sources phrase it both ways — surfaced honestly above).

---

## 3. Out-of-Bounds (OOB) — definition, threshold, nodal cycle, meaning

### Definition

A body is **out-of-bounds** when its declination exceeds the **Sun's maximum declination**, i.e. when

```
|δ| > ε        (ε = obliquity of the ecliptic, currently ≈ 23°26′ ≈ 23.44°)
```

The Sun's δ never exceeds ε (the Sun rides the ecliptic, β=0, so |δ_Sun|_max = ε exactly). Any body beyond that band is "outside the boundaries the Sun ever reaches" — hence out-of-bounds. For the Moon, OOB occurs whenever its β (up to ±5.14°) pushes δ past ε; possible only when the monthly declination envelope `ε ± i` exceeds ε, i.e. during the major-standstill half of the nodal cycle.

### The 18.6-year nodal cycle

The lunar nodes regress once per **18.6 years** (≈6798 d). Because the node line sets whether the 5.14° inclination *adds to* or *subtracts from* ε:

- **Major standstill** (nodes at the equinoxes, i adds): monthly |δ|_max ≈ **28.6°** → Moon goes OOB for an extended stretch each month, for a span of years around the standstill.
- **Minor standstill** (~9.3 yr later, i subtracts): monthly |δ|_max ≈ **18.3°** → Moon never reaches ε, so the Moon is **never OOB** during the minor-standstill years.

So OOB for the Moon is not a fixed monthly event — it switches on/off across the 18.6-yr cycle. (The most recent major lunar standstill was 2024–2025.)

### Threshold decision — fixed 23°26′ vs instantaneous ε(jd)

This is a real design choice (§5). Astronomically the correct boundary is the **Sun's actual maximum declination at that epoch**, which equals the obliquity ε(jd) — and ε(jd) drifts (mean obliquity decreases ≈ 47″/century; eq. in `mean_obliquity`). Over ketu's supported 1900–2100 range, ε ranges roughly 23.452° (1900) → 23.426° (2100), a span of ~0.026° ≈ 1.6′. A planet sitting within ~1.6′ of the boundary could be classified differently by a fixed vs instantaneous threshold. **Recommendation: instantaneous ε(jd)** (it is the physically-meaningful, self-consistent boundary and costs nothing — ketu already computes ε per date). True-vs-mean ε for the threshold is the same sub-arcminute question as §1.

### Practical / astrological meaning

In modern Western astrology, an out-of-bounds body (most discussed for the **Moon**) is read as operating "outside the normal rules / off the leash" — heightened, unconventional, extreme expression of that body. It is a recognized, widely-tooled concept (declination-based astrology). For ketu's biodynamic/financial cycle framing, OOB is simply a flaggable extreme-declination state of the Moon, cyclically gated by the 18.6-yr nodal cycle — useful as a regime marker. (Meaning is domain convention, not physics: MEDIUM, multiple concordant astrology references.)

**Sources:** Wikipedia "Lunar standstill"; Lunarium / Augurine / Evolving Door Astrology (OOB definition `|δ| > Sun's max ≈ 23°26′`, standstill range 18.3°–28.6°, 18.6-yr cycle) — all concordant. Obliquity drift from ketu `mean_obliquity` (IAU 2006). Confidence: definition HIGH, meaning MEDIUM.

---

## 4. Velocity of δ — recommended method, time step, edge cases

### ketu's existing idiom (verified)

`ketu/ephemeris/planets.py` computes ALL speeds (lon_speed, **lat_speed**, dist_speed) by **forward finite difference** with a fixed step `jd_delta = 0.01` days (≈14.4 min), e.g. `lat_speed = (lat2 - lat) / jd_delta`. This is the pattern behind `lat_velocity()` and hence `is_ascending()`. **dδ/dt MUST mirror this idiom** for consistency, testability, and zero new machinery.

### Recommended method

**Forward (or central) finite difference of δ, step 0.01 d**, fully vectorized:

```
δ1 = declination(jd,        body)
δ2 = declination(jd + 0.01, body)
dδ_dt = (δ2 - δ1) / 0.01            # °/day, mirrors lat_speed exactly
is_montante = dδ_dt > 0
```

- Forward difference matches the existing house style precisely (recommended for drop-in consistency).
- **Central difference** `(δ(jd+h) − δ(jd−h)) / (2h)` is O(h²) accurate vs forward's O(h) and centers the estimate on `jd` — preferable *if* turning-point precision matters (it removes the half-step bias near `dδ/dt = 0`). This is a minor design choice (§5).
- **No δ wraparound handling needed** (see §5): unlike `lon_speed`, which needs the `±180`/`±360` correction in planets.py, δ ∈ [−90,+90] is monotone and bounded — the latitude-style plain subtraction `(δ2 − δ1)` is always correct. This *simplifies* the velocity vs the longitude case.

### Time-step stability

For the Moon (fastest body), the declination rate peaks near the equator crossings at roughly **±3–4°/day**. A step of 0.01 d resolves this with negligible truncation error and is the value ketu already trusts for the (faster-changing) longitude. **0.01 d is stable and recommended** — do not shrink it (ketu's Moon ephemeris precision is ±0.01° in λ, so a smaller step would amplify ephemeris noise without real gain). Analytic differentiation is possible (differentiate eq. 13.4, feeding in `dλ/dt = lon_speed` and `dβ/dt = lat_speed`) but adds code and depends on the speed fields' own finite-difference accuracy — **not worth it**; finite difference of δ is cleaner and idiomatic.

### Edge cases

- **Near turning points (lunistices):** `dδ/dt → 0` and changes sign. `is_montante`/`is_descendante` flip here. A forward difference reports the *average* slope over the next 0.01 d, so the flip is detected ~half a step late (~7 min) — irrelevant at daily resolution; central difference removes even this.
- **At the equator (δ=0):** nothing special — δ is smooth through zero, velocity is maximal there, sign of δ flips but velocity does not.
- **Poles / |δ|→90°:** physically unreachable for any solar-system body (`|δ| ≤ ε+i ≈ 28.6°` for the Moon, less for others except Pluto/Chiron which have higher β); `arcsin` is well-conditioned far from ±90°. No clamping needed in the supported range.
- **Hemisphere convention:** north +, south − (matches β sign convention already used in ketu). Confirm in docstring.

**Sources:** ketu `planets.py` lines 99–278 (finite-difference idiom, step 0.01 d); standard numerical differentiation. Confidence HIGH.

---

## 5. Design decisions for the user

Each is a genuine fork — established fact vs choice is labeled.

### D1 — True vs Mean obliquity ε for δ (and the OOB threshold)
- **Fact:** they differ by ≤ ~9″ (≤0.15′) in resulting δ; nutation-driven, peaks near λ=90°/270°.
- **Recommendation: use `mean_obliquity(jd)`** for δ and OOB, for consistency with the rest of ketu's geometry layer (houses use mean obliquity; `_ecliptic.py` takes "mean obliquity") and because the sub-arcminute nutation term is below the Moon's own ±0.01° ephemeris precision. Offer `true_obliquity` only if the user explicitly wants arcsecond-faithful declination.
- **Why it's a choice:** purists computing apparent (nutation-corrected) place would pick true ε. Default mean keeps the library internally uniform.

### D2 — OOB threshold: fixed 23°26′ vs instantaneous ε(jd)
- **Fact:** ε drifts ~1.6′ across 1900–2100; the Sun's true max declination = ε(jd), not a constant.
- **Recommendation: instantaneous ε(jd)** — physically correct, already computed per date, free. A body within ~1.6′ of the band could be misclassified by a hardcoded 23°26′.
- **Why it's a choice:** some astrology software hardcodes 23°26′ for reproducibility against published tables. If matching such a table is a requirement, fixed wins; otherwise instantaneous.

### D3 — Velocity: forward vs central finite difference
- **Fact:** both O(h)/O(h²) accurate; forward matches the existing `lat_speed` idiom exactly.
- **Recommendation: forward difference, step 0.01 d**, for drop-in consistency with `lat_velocity`. Switch to central only if turning-point timing (lunistice detection) becomes a first-class feature.
- **Why it's a choice:** central is marginally more accurate at the turning points; consistency vs precision tradeoff.

### D4 — Implementation path: reuse rectangular chain vs direct Meeus 13.4
- **Fact:** numerically identical (Δ = 0 to machine precision).
- **Recommendation: direct formula** for `declination()` (clearest, self-documenting, slightly faster), guarded by a regression test asserting equality with the `coordinates.py` chain.

### D5 — Naming / semantic clash with existing `is_ascending` (β-velocity)
- **Fact:** `is_ascending(jd, body)` already exists and tests **ecliptic-latitude** rise, NOT declination. They are different quantities.
- **Recommendation:** name the δ-trajectory helper distinctly (`is_declination_ascending`, or domain term `is_montante`) and document the distinction. Decide whether v1.5's "montant/descendant" means the genuine δ-trajectory (this brief's assumption) or the existing β-based `is_ascending` (per the `project_future_lunar_declination` memo). This is the single most important framing decision for requirements.

### D6 — `CHART_DTYPE` extension (`body_decl`)
- **Fact:** `CHART_DTYPE` has `body_lons`, `body_lats`, `body_speeds` (each `(14,)`), no `body_decl`. Adding a field is a frozen-layout change (the dtype is documented as "frozen" and consumed by synastry/composite/parts; the 13→14 body change previously broke the freeze and Kala adapted).
- **Recommendation:** add `("body_decl", "f8", (14,))` (parallel to `body_lats`) and, if the montant/OOB features need it, `("body_decl_speeds", "f8", (14,))`. Treat as a deliberate dtype-version bump with a ratchet test (mirror the prior `test_dtype.py` 13→14 pattern). Flag to downstream (Kala) as a layout change.

---

## 6. Sources

- **Meeus, Jean. *Astronomical Algorithms*, 2nd ed.** — Ch. 13 "Transformation of Coordinates," **eq. 13.3** (right ascension) and **eq. 13.4** (declination): `sin δ = sin β cos ε + cos β sin ε sin λ`. (HIGH — primary reference; ketu already uses Meeus for sidereal time eq. 12.6 and Moon theory.)
- **ketu source (verified in this brief):** `ketu/ephemeris/coordinates.py` (`spherical_to_rectangular`, `ecliptic_to_equatorial`, `rectangular_to_spherical`, `mean_obliquity` [IAU 2006], `true_obliquity`, `nutation`); `ketu/ephemeris/planets.py` lines 99–278 (finite-difference speed idiom, `jd_delta = 0.01`); `ketu/calculations.py` (`lat`, `lat_velocity`, `is_ascending`); `ketu/charts/core.py` line 87 (`CHART_DTYPE`). Numerical equivalence of formula vs chain and nutation magnitude computed here. (HIGH.)
- **Wikipedia, "Lunar standstill"** — declination range `(ε−i)`…`(ε+i)`, minor ≈±18.3°, major ≈±28.6°, i=5.14°, 18.6-yr nodal precession, monthly declination cycle. https://en.wikipedia.org/wiki/Lunar_standstill (MEDIUM, cross-checked).
- **Lunarium ("Out-of-Bounds Planets"), Augurine ("Lunar Standstill and the 18.6-Year Cycle"), Evolving Door Astrology ("Out of Bounds")** — OOB definition `|δ| > Sun's max declination ≈ 23°26′`, astrological meaning, standstill OOB gating. (MEDIUM, three concordant sources.) https://lunarium.co.uk/articles/out-of-bounds/ · https://www.augurine.com/learn/declination/lunar-standstill · https://www.evolvingdoorastro.com/glossary/terms/declination/out-of-bounds
- **Month-length values** (synodic 29.530589 d, sidereal 27.321662 d, tropical 27.321582 d, anomalistic 27.554550 d, **draconic 27.212221 d**) — standard USNO/Meeus constants. (HIGH.)

---

## NOT covered (out of scope by design)

Thun biodynamic constellation calendar, sidereal/zodiacal sign conventions, "Moon in front of constellation X" — explicitly excluded per milestone framing. This brief is pure equatorial/angular mechanics of declination.
