# Phase 17: Composite Chart (Midpoint Variant) — Research

**Researched:** 2026-05-11
**Domain:** Midpoint composite chart derivation from two `CHART_DTYPE` records (circular-arithmetic, ASC/MC midpoint + house-cusp derivation, scalar pair-chart API mirroring `ketu.synastry`).
**Confidence:** HIGH (composition only — every astronomical primitive exists in Ketu v1.0/v1.1/v1.2; novelty is the circular-midpoint helper, the house-derivation strategy, and the new module/dtype surface).

---

## User Constraints (no CONTEXT.md — ROADMAP success criteria are binding)

No `/gsd:discuss-phase` was run for this phase. Per the orchestrator brief, the four ROADMAP success criteria for Phase 17 are treated as **LOCKED decisions**:

### Locked Decisions (from ROADMAP success criteria + REQUIREMENTS COMP-01..04)

1. **`calculate_composite(chart_a, chart_b, system="placidus")` returns a `CHART_DTYPE`** whose body longitudes are circular midpoints of the two natals, and whose houses are **computed from the composite ASC and MC** (NOT recomputed independently from `(jd, lat, lon)` of either partner).
2. **`circular_midpoint(lon_a, lon_b)` is vectorisable, modulo-360°**, and `circular_midpoint(359.0, 1.0) == 0.0` (NOT 180.0) is pinned as a regression test.
3. **Two reference composite pairs (hand-validated against Astro.com) are pinned as oracle tests** with documented max longitude delta.
4. **Davison composite is explicitly out of scope** and labeled as deferred-to-v1.3 in the module docstring (no aspirational reference).

### Claude's Discretion (planner's freedom areas)

- Module path: `ketu/composite/` (new package) vs `ketu/charts/composite.py` (single-file) — recommendation below in §Module Layout.
- Internal helper names (`_circular_midpoint_scalar`, `_compose_houses_from_angles`, etc.).
- Whether to derive composite cusps via **Porphyry-style trisection from composite ASC + composite MC** (Approach A, recommended below) or **call the existing house-system dispatch with composite ARMC + reference latitude** (Approach B). See §House Computation Strategy.
- Coverage gate marker: include `composite_coverage_gate` from the start (recommended) or defer to a close-out plan.
- Reference latitude convention (only relevant if Approach B is chosen). The mathematically purest "no recomputation" reading of COMP-03 is Approach A.
- Public `__all__` set; CLI sub-command (NOT required by COMP-01..04 — keep out of scope for this phase unless added in a follow-up plan).

### Deferred Ideas (OUT OF SCOPE for Phase 17)

- **Davison composite** (time + space midpoint chart) — v1.3 per REQUIREMENTS §"Deferred to v1.3" and ROADMAP §Phase 17 success criterion #4. Module docstring MUST label this as deferred (no aspirational pointer / TODO / placeholder function).
- Batch composite (N×M pairs in one call). Phase 17 only handles **scalar `CHART_DTYPE` × scalar `CHART_DTYPE` → scalar `CHART_DTYPE`** (mirrors synastry's scalar contract).
- Composite chart CLI sub-command (`ketu composite ...`). Not in COMP-01..04. Add only via a separate close-out plan if desired.
- Composite aspects to natal (transits-to-composite). Different concern, no requirement.
- Multi-composite (>2 charts). Astrodienst feature, not in v1.2 scope.
- Reference-place method (Astrodienst's alternative composite calculation). Phase 17 implements the **pure midpoint method** only.
- Composite Vertex / ARMC interpretive fields beyond what `CHART_DTYPE` already holds.

---

## Summary

Phase 17 is **composition over invention** — same pattern as Phase 14 (charts) and Phase 16 (synastry). The astronomical math is trivial: a midpoint composite chart is the structured-array containing (a) circular midpoints of the 13 body longitudes/latitudes of the two natals, (b) circular midpoints of the two ASC and MC values, (c) house cusps **derived from those composite ASC and MC** rather than recomputed via the standard `(jd, lat, lon) → ARMC → cusps` pipeline. The single tricky bit is choosing the **short-arc midpoint** on the circle: `circular_midpoint(359°, 1°) == 0°`, not `180°`. The whole phase is ~300 LOC behind a single public function.

The non-trivial decisions are architectural, not astronomical:

1. **House derivation strategy.** Each Ketu house system today is a function `(armc, lat, eps) → cusps[12]`. COMP-03 forbids recomputing houses from a partner's `(jd, lat, lon)`. Two compliant strategies exist: **(A) Porphyry-trisection from composite ASC + composite MC alone** (mathematically cleanest, polar-safe by construction, ignores `system="placidus"` semantically — every system collapses to Porphyry for composites), or **(B) compose a synthetic `(composite_armc, reference_lat, composite_eps)` and dispatch through the existing registry** (preserves the `system=` argument's user-facing meaning, requires a chosen reference latitude). Recommendation: **Approach A** (see §House Computation Strategy for justification — it matches COMP-03's literal reading and avoids the "reference latitude" decision which has no canonical answer in the pure midpoint convention).

2. **Module layout.** Mirror `ketu/synastry/` as `ketu/composite/` — a new top-level subpackage with `api.py`, `core.py`, `__init__.py`. Both phases share the same shape ("pair-chart compute": `CHART_DTYPE × CHART_DTYPE → output`), so the layout symmetry is strong. Single-file `ketu/charts/composite.py` would conflate two distinct concerns (chart construction vs pair derivation).

3. **API naming.** ROADMAP/REQUIREMENTS spec `calculate_composite(...)` matches synastry's `calculate_synastry(...)` precedent; the chart-building primitive is `compute_chart(...)`. Keep the spec name verbatim — the precedent is `compute_*` for fresh-from-`(jd, lat, lon)` chart construction and `calculate_*` for derived/multi-chart operations. `calculate_composite` fits the latter convention.

**Primary recommendation:** Implement `ketu/composite/` as a new subpackage with `calculate_composite(chart_a, chart_b, system="placidus") → CHART_DTYPE` + `circular_midpoint(lon_a, lon_b)` helper. Use Porphyry trisection from composite ASC + composite MC for house cusps (Approach A). Ignore `system=` semantically (accept but document that all systems collapse to the same composite cusps under the midpoint method) OR raise on non-Porphyry/non-default `system=` (see §Open Questions). Pin two Astro.com oracle pairs with `<0.1°` tolerance per body, mirror the `synastry_coverage_gate` pattern as `composite_coverage_gate` (≥95%), and ratchet `mid(359°, 1°) == 0°` as the headline regression test.

---

## Codebase Landmarks

| File | Why it matters for Phase 17 |
|------|-----------------------------|
| [`ketu/charts/core.py`](../../../ketu/charts/core.py) | `CHART_DTYPE` definition (14 fields, ordered metadata → bodies → houses → aspects). The composite output dtype IS `CHART_DTYPE` — Phase 17 produces this layout, does not introduce a new one. |
| [`ketu/charts/api.py`](../../../ketu/charts/api.py) | `compute_chart(jd, lat, lon, system, aspects, polar_fallback)` — the canonical CHART_DTYPE construction path (lines 311–357). Composite assembly mirrors this: fill `jd`/`lat`/`lon`/`system`/`body_lons`/`body_lats`/`body_speeds`/`cusps`/`asc`/`mc`/`armc`/`vertex`/`aspect_matrix`/`aspect_orbs`. The `is_day_chart` function (line 360) is a standalone helper, NOT a `CHART_DTYPE` field — no composite-specific sect logic needed. |
| [`ketu/synastry/api.py`](../../../ketu/synastry/api.py) | `calculate_synastry(chart_a, chart_b, ...)` — the precedent for "scalar `CHART_DTYPE` × scalar `CHART_DTYPE`" pair operations. Composite mirrors the public signature, the docstring style, the `__all__` export shape, and the locked-decisions docstring block. |
| [`ketu/synastry/__init__.py`](../../../ketu/synastry/__init__.py) | Subpackage `__init__.py` precedent: re-export the public function + the dtype constant + helper resolvers from `api.py` / `core.py` / `orbs.py`. Composite gets a smaller surface — `calculate_composite` + `circular_midpoint`. |
| [`ketu/houses/api.py`](../../../ketu/houses/api.py) | `calculate_houses(jd, lat, lon, system, polar_fallback)` — the high-level house entry. **NOT directly reusable for composite** because its first step is `compute_ascmc(jd, lat, lon)` which we are explicitly bypassing (COMP-03). We DO reuse the registry-dispatch idea below. |
| [`ketu/houses/registry.py`](../../../ketu/houses/registry.py) | `SYSTEMS` dict + `get_system(name)` lookup. If Approach B is chosen, `get_system(system)(armc, lat, eps)` is called with synthetic composite ARMC/lat/eps. If Approach A is chosen, `SYSTEMS` is not touched directly — Phase 17 inlines a Porphyry-style trisection. |
| [`ketu/houses/porphyry.py`](../../../ketu/houses/porphyry.py) | `porphyry_cusps(armc, lat, eps)` (line 100) — the closed-form trisection that constructs all 12 cusps from ASC + MC + IC + DESC. **The actual cusp formulas** at lines 167–186 (`upper_step = ((asc - mc) mod 360) / 3`, etc.) are what Phase 17 reuses verbatim, just substituting `(composite_asc, composite_mc)` for the closed-form ASC/MC the function would normally compute itself. This is the single most important reference for Approach A. |
| [`ketu/houses/ascmc.py`](../../../ketu/houses/ascmc.py) | `compute_ascmc` + `compute_armc` — useful only if Approach B is chosen and a synthetic composite ARMC needs to be constructed. Approach A does not consume this. |
| [`ketu/aspects/calculator.py`](../../../ketu/aspects/calculator.py) | `calculate_aspects_vectorized(jd, aspects=...)` — the aspect engine consumed by `compute_chart`'s `_build_aspect_matrix`. **Composite needs aspects too** (the output is a full `CHART_DTYPE` including `aspect_matrix`/`aspect_orbs`), but the existing function takes `jd` and recomputes bodies. We will need a small adapter that takes pre-computed composite body longitudes and runs the same body-pair aspect-matching loop. See §Reusing Helpers. |
| [`ketu/calculations.py`](../../../ketu/calculations.py) | `distance(...)` — circular-distance utility consumed by synastry. Useful as a NumPy-vectorised primitive when implementing the aspect-matching adapter for composite. |
| [`pyproject.toml`](../../../pyproject.toml) (lines 77–82) | `markers = [...]` registration site for `composite_coverage_gate`. Add alphabetically between `charts_coverage_gate` and `houses_coverage_gate`. |
| [`Makefile`](../../../Makefile) (lines 50–66) | Precedent for `make composite-coverage` target — three-line copy of the `charts-coverage` / `synastry-coverage` block (`pytest tests/composite/` + `coverage report --include='ketu/composite/*' --fail-under=95`). |
| [`tests/synastry/conftest.py`](../../../tests/synastry/conftest.py) | Fixture pattern: session-scoped `compute_chart(...)` calls for reusable chart pairs (`chart_a_paris`, `chart_b_nyc`, etc.). Composite test fixtures should mirror exactly. |
| [`tests/synastry/test_oracle.py`](../../../tests/synastry/test_oracle.py) + [`tests/synastry/fixtures/oracle_*.json`](../../../tests/synastry/fixtures/) | Oracle test pattern: JSON fixtures with subject birth data + expected outputs + `tolerance_deg`. Composite uses the same JSON-driven layout; the `expected_aspects` array is replaced by `expected_bodies` (Sun/Moon/Mercury/.../Pluto composite longitudes) + `expected_asc`/`expected_mc`. |
| [`tests/synastry/test_synastry_coverage_gate.py`](../../../tests/synastry/test_synastry_coverage_gate.py) | Sentinel test for the coverage-gate marker. Composite gets the exact same file at `tests/composite/test_composite_coverage_gate.py`. |
| [`.planning/phases/16-synastry/16-RESEARCH.md`](../16-synastry/16-RESEARCH.md) | Stylistic precedent for the RESEARCH document — section headings, confidence calibration, the locked-decisions / discretion / deferred-ideas trichotomy. |

---

## Domain Primer: Midpoint Composite (vs Davison)

A **composite chart** is a third "relationship chart" derived from two natal charts. Two principal conventions exist in the literature:

| Convention | What is averaged | What's needed | v1.2 scope? |
|------------|------------------|---------------|-------------|
| **Midpoint composite** | Each planet's longitude is the midpoint of the two natal longitudes; ASC and MC similarly. | Only the two natal `CHART_DTYPE` records. | **YES** (COMP-01..04) |
| **Davison composite** | A real chart computed at the temporal midpoint (mid-Julian-Date) and spatial midpoint (geographic great-circle midpoint) of the two births. | Birth dates + locations for both partners; a fresh ephemeris call. | **NO** (deferred to v1.3) |

The two conventions answer the same astrological question ("what is the third entity that is the relationship?") with different mathematical machinery. The midpoint method is **algebraic** (averaging existing angles); Davison is **physical** (a real moment in real space). Their outputs are similar near the equator and for partners born close together; they diverge for partners with large geographic or temporal separation.

**Two sub-variants of the midpoint method** appear in commercial software (Solar Fire, Astro.com):

- **Pure midpoint method (what Phase 17 implements):** Composite Sun = midpoint of two natal Suns, composite Moon = midpoint of two natal Moons, ..., composite ASC = midpoint of two natal ASCs, composite MC = midpoint of two natal MCs. House cusps 2/3/5/6/8/9/11/12 are then **derived geometrically from composite ASC + composite MC** (Porphyry trisection) — this is COMP-03's literal reading.
- **Reference-place method (Astrodienst's documented preference, NOT what we implement):** Composite MC is the midpoint of the two natal MCs; composite ASC is then *back-computed* from that MC plus a **reference geographic latitude** (typically the latitude midpoint, sometimes the user's chosen "where the relationship happens"); then the full house system runs at `(composite_armc, reference_lat, composite_eps)`. This requires a "reference latitude" decision that has no canonical answer, which is why Phase 17 skips it.

The Astrodienst FAQ ([Composite charts](https://www.astro.com/faq/fq_fh_compo_e.htm), [Composite Chart wiki](https://www.astro.com/astrowiki/en/Composite_Chart)) documents both methods. The Astrolabe / Solar Fire convention and Robert Hand's *Planets in Composite* (1975, the canonical reference cited in REQUIREMENTS commentary) use the pure midpoint method. Phase 17 follows that lineage.

**Confidence:** HIGH on the math (both conventions are extensively documented in mainstream astrology references); MEDIUM on Astrodienst's exact convention because their primary pages are bot-blocked from WebFetch (cross-verified via secondary sources cited in §Sources).

---

## Circular Midpoint Math

### The two midpoints on a circle

For two longitudes `a` and `b` on the unit circle, there are always **two midpoints** exactly 180° apart: the **short-arc midpoint** (on the shorter arc between `a` and `b`, length `<= 90°` from each endpoint) and the **antipodal midpoint** (on the longer arc, length `>= 90°` from each endpoint). Naïve arithmetic `(a + b) / 2` picks the wrong one whenever `|a - b| > 180°` (the wraparound case).

### Wraparound proof: `mid(359°, 1°)`

- **Linear average** `(359 + 1) / 2 = 180°` — this is the **antipodal** midpoint. **WRONG.**
- **Geometric truth:** `359°` and `1°` are 2° apart on the short arc through `0°`. The midpoint of that short arc is `0°` (equivalently, `360°` mod 360 = `0°`). The antipodal midpoint at `180°` lies 178° from each endpoint — astronomically nonsense for a "composite Sun" interpretation.
- **Pinned regression test (COMP-02):** `circular_midpoint(359.0, 1.0) == 0.0`. Tolerance: exact equality (this is a closed-form rational computation; no float error introduced if implemented correctly).

### Vectorised NumPy expression (recommended)

The canonical short-arc midpoint formula uses complex-number averaging on the unit circle, then `np.angle()`:

```python
import numpy as np

def circular_midpoint(lon_a: ArrayLike, lon_b: ArrayLike) -> np.ndarray:
    """Short-arc midpoint on the unit circle, modulo 360°.

    Vectorised. ``circular_midpoint(359.0, 1.0) == 0.0`` (NOT 180.0).
    """
    a_rad = np.deg2rad(np.asarray(lon_a, dtype=np.float64))
    b_rad = np.deg2rad(np.asarray(lon_b, dtype=np.float64))
    # Sum of two unit vectors -> bisector along the shorter arc.
    bisector = np.exp(1j * a_rad) + np.exp(1j * b_rad)
    return np.rad2deg(np.angle(bisector)) % 360.0
```

**Why this works:** Adding the two unit complex numbers `exp(i*a)` and `exp(i*b)` yields a vector pointing along the **short-arc bisector** (the sum vector lies on the angle bisector by parallelogram-law symmetry, and the short arc is always the one selected because both addends point "outward" from the bisector). `np.angle()` returns this bisector's argument in `(-π, π]`; the `% 360.0` normalises to `[0, 360)`.

**Edge cases:**

- `a == b`: bisector = `2 * exp(i*a)`, angle = `a`. Correct.
- `a == b + 180° (antipodal)`: bisector = `0`, `np.angle(0)` returns `0`. **Ambiguous case** — both midpoints are equally valid. Document the convention (return `0` or NaN); composite charts never legitimately need the midpoint of two antipodal bodies (would only occur for two partners with exactly opposing Suns, geometrically possible but astrologically degenerate). **Recommended:** Pin `circular_midpoint(0.0, 180.0)` behaviour explicitly in tests so future refactors don't silently change it. NumPy's `np.angle(0+0j) == 0.0`, so the function returns `0.0` for `(0, 180)` — pin this.
- **NaN inputs:** propagate naturally through `np.exp` / `np.angle`. No special handling.

### Alternative formulation (algebraically equivalent)

```python
diff = ((lon_b - lon_a + 180.0) % 360.0) - 180.0    # signed short-arc diff in (-180, +180]
midpoint = (lon_a + diff / 2.0) % 360.0
```

This is the same result by a different route (compute the short-arc signed offset, then add half). Marginally faster (no trig calls), but the complex-exponential form is **more obviously correct** at a glance and vectorises identically. Either is acceptable; the planner should pick one and pin both implementations against each other for cross-validation if there's any doubt.

**Confidence:** HIGH (the complex-exponential midpoint is the textbook circular-statistics formula; the wraparound case is a one-line proof).

---

## House Computation Strategy

This is the **single architectural decision** of the phase, and it deserves careful treatment because COMP-03 is precise about what's forbidden.

### What COMP-03 says

> Composite houses calculated from composite ASC + composite MC (NOT re-computed independently)

Operationally, "NOT re-computed independently" means we MUST NOT call `calculate_houses(jd_a, lat_a, lon_a, ...)` or `calculate_houses(jd_b, lat_b, lon_b, ...)` or any variant that uses one partner's geographic context to produce composite cusps. The composite ASC and composite MC are the **inputs** to the house computation, not its outputs.

### Approach A (RECOMMENDED): Porphyry trisection from composite ASC + composite MC

Take the composite ASC and composite MC as given (computed via `circular_midpoint` on the two natal ASCs and MCs), then derive cusps 2/3/5/6/8/9/11/12 by the same trisection algebra Porphyry uses ([`ketu/houses/porphyry.py`](../../../ketu/houses/porphyry.py) lines 167–186):

```python
# composite_asc, composite_mc = circular_midpoint(...) of partner ASCs / MCs
# Polar-ASC swap (mirror porphyry.py:159-161): keep the short-arc form ACMC > 0.
acmc_signed = ((composite_asc - composite_mc + 540.0) % 360.0) - 180.0
swap_mask = acmc_signed < 0.0
composite_asc = np.where(swap_mask, (composite_asc + 180.0) % 360.0, composite_asc)
acmc = np.where(swap_mask, acmc_signed + 180.0, acmc_signed)

composite_ic = (composite_mc + 180.0) % 360.0
composite_desc = (composite_asc + 180.0) % 360.0

upper_step = acmc / 3.0
lower_step = (180.0 - acmc) / 3.0

cusp_11 = (composite_mc + upper_step) % 360.0
cusp_12 = (composite_mc + 2.0 * upper_step) % 360.0
cusp_2 = (composite_asc + lower_step) % 360.0
cusp_3 = (composite_asc + 2.0 * lower_step) % 360.0
cusp_5 = (cusp_11 + 180.0) % 360.0
cusp_6 = (cusp_12 + 180.0) % 360.0
cusp_8 = (cusp_2 + 180.0) % 360.0
cusp_9 = (cusp_3 + 180.0) % 360.0

cusps = np.stack([
    composite_asc, cusp_2, cusp_3, composite_ic,
    cusp_5, cusp_6, composite_desc, cusp_8,
    cusp_9, composite_mc, cusp_11, cusp_12,
], axis=-1)
```

**Pros:**
- **Literal COMP-03 compliance.** Composite ASC + composite MC are the only inputs.
- **Polar-safe by construction.** Porphyry trisection works at every latitude (no `tan(lat)` singularity, no `HighLatitudeError` path).
- **No "reference latitude" decision.** The geographic-latitude question is sidestepped entirely.
- **Closed-form, vectorisable, ~10 lines of code** (we already have the reference in `porphyry.py`).
- **Robert Hand's documented composite-house convention** in *Planets in Composite* effectively reduces to this for midpoint composites (the book's worked examples use a trisection-style derivation).

**Cons:**
- The `system="placidus"` argument is **semantically a no-op** in this approach — every requested house system collapses to a Porphyry-like trisection. Either accept this and document it, or raise `ValueError` for systems other than `"placidus"` / `"porphyry"`. (See §Open Questions.)
- Phase 15's six house systems do not differentiate the composite chart in any way under Approach A. This is **fine** because the midpoint convention has no meaningful sense of "Placidus-style declination scaling" on a chart with no real-time-and-place; but it's a documentation surface.

### Approach B (NOT RECOMMENDED): Synthesise composite ARMC and dispatch through `SYSTEMS`

Take the midpoint of the two natal ARMC values (`circular_midpoint(armc_a, armc_b)`), the average of the two epsilons (linear average is fine — eps drifts by ~50″/century, so the two values are within ~0.00001° for any realistic partner pair), pick a **reference latitude** (midpoint of the two natal latitudes? linear average is fine for small separations, geographic great-circle midpoint for large ones), then call `SYSTEMS[system](composite_armc, ref_lat, composite_eps)`.

This is what the [pyswisseph programmer's manual](https://github.com/astrorigin/pyswisseph/blob/master/docs/programmers_manual/house_cusp_calculation.rst) recommends for composites in the SwissEph C API.

**Pros:**
- The `system="placidus"` argument has real semantic meaning — Placidus composites differ from Porphyry composites differ from Koch composites, just as in natal charts.
- Aligns with Astrodienst's "reference place method" if the reference latitude is interpreted as the user's chosen "where the relationship happens" coordinate.

**Cons:**
- Requires a **reference latitude** decision. The literature has no canonical answer; the linear midpoint `(lat_a + lat_b) / 2` is the simplest plausible choice but is not the great-circle geographic midpoint (the great-circle midpoint requires `lon` too, and bringing geographic context back in feels like a backdoor violation of COMP-03's spirit).
- The composite ASC produced by this path is NOT the midpoint of the two natal ASCs (it's the ASC computed at `composite_armc` for `ref_lat` and `composite_eps`). This **contradicts COMP-01's "body longitudes are circular midpoints of the two natals"** if you read ASC as a "body" in the structural sense (it is one of the `CHART_DTYPE` fields).
- Polar-fallback machinery becomes relevant again (Placidus at high reference latitudes can NaN out).

### Recommendation

**Approach A.** It matches the literal COMP-03 wording ("computed from the composite ASC and MC"), avoids the unanswerable reference-latitude question, is polar-safe, and reduces the implementation to ~10 lines of straightforward NumPy. The `system="placidus"` argument is preserved in the function signature for API symmetry with `compute_chart` and is **stored in the output `CHART_DTYPE`'s `system` field** to record the user's stated intent — but documented as semantically a no-op for midpoint composites. The `CHART_DTYPE["armc"]` field stores `circular_midpoint(armc_a, armc_b)` for completeness (so downstream consumers can rebuild Approach B externally if they want), and `CHART_DTYPE["vertex"]` stores `circular_midpoint(vertex_a, vertex_b)` by the same logic.

**Confidence:** HIGH on Approach A's correctness (the algebra is the existing Porphyry path, reused verbatim); MEDIUM on the recommendation over Approach B (some users will reasonably prefer Approach B for `system=` semantic meaning — the planner may want to surface this as an explicit design question if there's appetite for a `/gsd:discuss-phase` round).

---

## Body Coverage

`CHART_DTYPE` carries 13 bodies on a frozen axis (D-08): Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Rahu, Ketu, Lilith. **All 13 must be midpointed.** The `body_lons` / `body_lats` / `body_speeds` arrays of the composite output have the same `(13,)` shape; each element is the circular midpoint (for lon) or arithmetic mean (for lat — latitudes are not circular in `[0, 360)`, they live in `[-90, +90]`) of the two natal values.

**Speeds.** Natal speeds are degrees/day at the moment of the natal chart. The "composite speed" is a meaningless quantity — there is no moment of time for a midpoint composite. Two reasonable conventions:

1. **Linear average of the two natal speeds:** `composite_speed = (speed_a + speed_b) / 2`. This is what most commercial software stores, if it stores anything. Cheap, vectorisable, signed-preserving (a body retrograde in both natals stays retrograde in the composite).
2. **Sentinel NaN:** Acknowledge the metaphysical incoherence by storing NaN.

**Recommendation:** Use (1). NaN propagates into every downstream consumer (`is_day_chart`, aspect calculation, etc.) in ways that surface as bugs rather than informative errors. Linear average is the conservative default — it preserves the array's `f8` dtype contract and matches commercial software behaviour. **Document explicitly** in the function docstring that `body_speeds` on a composite is the linear average of natal speeds and has no physical interpretation as "the composite's instantaneous longitude motion."

**Latitudes.** Linear average is correct: ecliptic latitude `[-90, +90]` is not circular at the equator; planets stay within ~7° of the ecliptic; no wraparound concern; arithmetic mean is geometrically sound.

**Confidence:** HIGH (the 13-body axis is frozen by D-08; speeds and latitudes are documented; linear-average vs NaN is a documentation choice with low blast radius).

---

## `is_day_chart` for Composites

`is_day_chart` is a **standalone helper** (D-12), not a `CHART_DTYPE` field. It takes `(jd, lat, lon)` and answers "is the Sun above the horizon at this moment-and-place?". For a midpoint composite, the inputs `(jd, lat, lon)` are **ambiguous** — the composite has no canonical Julian Date and no canonical location.

**Recommendation:** Phase 17 does NOT extend `is_day_chart` to composites. The COMP-01..04 spec does not mention sect, day/night, or `is_day_chart`. Callers who legitimately want a "composite sect" can post-hoc compute `(composite_asc - composite_sun_lon) % 360 < 180` themselves (the same diurnal-arc test `is_day_chart` uses internally), but Phase 17 does not bake that into a public API. The `CHART_DTYPE` does NOT carry an `is_day` field today (D-12 deliberately keeps sect out of the dtype to avoid double source-of-truth), so the composite output naturally inherits that absence.

Phase 19 (Arabic Parts) is the consumer that needs `is_day_chart`; the Parts spec will decide whether composite Arabic Parts are even in scope (they're a separate ROADMAP phase). Phase 17 owes no contract here.

**Confidence:** HIGH (D-12 keeps sect out of `CHART_DTYPE`; COMP-01..04 doesn't mention it).

---

## Module Layout

**Recommendation:** `ketu/composite/` as a new subpackage, mirroring `ketu/synastry/`.

```
ketu/
└── composite/
    ├── __init__.py          # Re-export calculate_composite + circular_midpoint
    ├── api.py               # def calculate_composite(chart_a, chart_b, system="placidus") -> np.ndarray
    └── core.py              # circular_midpoint helper; any internal constants
                             # (no new dtype — output IS ketu.charts.CHART_DTYPE)
```

**Why a new subpackage, not `ketu/charts/composite.py`:**

- Phase 16 (`ketu/synastry/`) established the precedent: pair-chart computations get their own top-level subpackage. Single-file siblings inside `ketu/charts/` would mix two concerns — **building** a chart (`compute_chart` from `(jd, lat, lon)`) vs **deriving** a chart from existing ones (`calculate_composite` from two `CHART_DTYPE`s).
- Future Phase 18 (Solar Return) and Phase 19 (Arabic Parts) may want their own subpackages by the same logic.
- The `__init__.py` boundary lets the planner ratchet a `composite_coverage_gate` cleanly via `--include='ketu/composite/*'` in the Makefile (mirroring `synastry-coverage` at lines 64–66).
- `tests/composite/` parallels `tests/synastry/` exactly — easier to navigate for contributors.

`pyproject.toml` `[tool.setuptools] packages` (line 61) must include `"ketu.composite"`.

**Confidence:** HIGH (direct synastry precedent; symmetric naming; no contraindications).

---

## Public API Surface

```python
def calculate_composite(
    chart_a: np.ndarray,         # scalar CHART_DTYPE
    chart_b: np.ndarray,         # scalar CHART_DTYPE
    system: str = "placidus",    # stored in out["system"]; see Approach A discussion
) -> np.ndarray:                 # scalar CHART_DTYPE
    """Compute a midpoint composite chart from two natal charts.
    ...
    """
```

**Default `system=` value.** Spec says `system="placidus"` (COMP-01 verbatim). Match the spec. Note that under Approach A, the value of `system` is recorded in the output's `system` field but does not change the cusps produced — document this loudly.

**Output `jd` / `lat` / `lon`.** These are `CHART_DTYPE` fields whose composite values are conventionally NaN or ambiguous. Two conventions:

1. **NaN sentinels.** Honest. `out["jd"] = np.nan`, `out["lat"] = np.nan`, `out["lon"] = np.nan`.
2. **Linear midpoints.** `out["jd"] = (jd_a + jd_b) / 2`, `out["lat"] = (lat_a + lat_b) / 2`, `out["lon"] = circular_midpoint(lon_a, lon_b)`. These have **no astronomical meaning** for a midpoint composite but are useful for round-trip testing and they're what some software stores.

**Recommendation:** Use **(2) linear midpoints** for `jd` and `lat` (these are not circular quantities; linear average is fine) and **circular midpoint** for `lon` (geographic longitude IS circular). This matches the "every CHART_DTYPE field is a midpoint" mental model of COMP-01 and avoids NaN propagation through downstream consumers. Document explicitly that `(jd, lat, lon)` on a composite are bookkeeping, NOT a real moment-and-place — emphatically NOT a Davison-style time-and-space midpoint. This is the most likely source of user confusion and must be guarded.

**Composite ARMC / Vertex.** Similarly midpointed (`circular_midpoint(armc_a, armc_b)`, `circular_midpoint(vertex_a, vertex_b)`).

**Composite aspect_matrix / aspect_orbs.** Required by `CHART_DTYPE`. Compute the intra-chart aspects of the composite using the composite body longitudes — same algorithm as `_build_aspect_matrix` in [`ketu/charts/api.py`](../../../ketu/charts/api.py) lines 109–190, but instead of calling `calculate_aspects_vectorized(jd_scalar, ...)` (which recomputes bodies from `jd`), pass the already-derived composite longitudes directly. See §Reusing Helpers below — this requires either a small adapter or refactoring `calculate_aspects_vectorized` to accept pre-computed body longitudes.

---

## Reusing Existing Helpers

### What we reuse

| Helper | Source | How composite uses it |
|--------|--------|------------------------|
| `np.deg2rad`, `np.rad2deg`, `np.angle`, `np.exp` | NumPy | Vectorised `circular_midpoint` implementation. |
| Porphyry trisection algebra | [`ketu/houses/porphyry.py`](../../../ketu/houses/porphyry.py) lines 153–186 | House cusps 2/3/5/6/8/9/11/12 from composite ASC + composite MC (Approach A). |
| `CHART_DTYPE` | [`ketu/charts/core.py`](../../../ketu/charts/core.py) line 85 | The output dtype (no new dtype introduced). |
| `bodies`, aspect coefficients, aspect set resolver | [`ketu/core.py`](../../../ketu/core.py), [`ketu/aspects/presets.py`](../../../ketu/aspects/presets.py) | Used by the aspect-matrix construction. |
| `distance` | [`ketu/calculations.py`](../../../ketu/calculations.py) | Pair-distance computation for aspect matching. |

### What we may need to add or refactor

**Aspect-matrix from pre-computed longitudes.** `calculate_aspects_vectorized` currently takes `jd` and recomputes bodies internally — it does NOT accept a pre-computed `(13,)` longitudes array. For composite, we have composite longitudes but no canonical `jd`, so this signature doesn't fit.

Three options:

1. **Refactor `calculate_aspects_vectorized`** to optionally accept `body_lons=None` (default: compute from `jd`) and skip the body computation when `body_lons` is provided. Cleanest, but touches the Phase 9 aspect engine — wider blast radius.
2. **Add a sibling `_calculate_aspects_from_longitudes(body_lons, aspects=...)`** in `ketu/aspects/` or `ketu/composite/`. Lower blast radius, but introduces a parallel code path that can drift from `calculate_aspects_vectorized`.
3. **Inline the body-pair aspect-matching loop in `calculate_composite`** (~30 lines borrowed from `calculate_aspects_vectorized`'s `triu_indices` loop). Most localised; risk of drift if Phase 9 aspect algorithm changes.

**Recommendation:** Option 1 (refactor `calculate_aspects_vectorized` to accept `body_lons` as an optional kwarg). The refactor is small (gate the body-recompute behind an `if body_lons is None:` early-return) and benefits Phase 18 (Solar Return) and Phase 19 (Arabic Parts) which face the same pattern. The planner should sequence this as a precursor task (e.g., Plan 17-01: refactor aspect engine to accept `body_lons` kwarg) before Plan 17-02 (composite implementation).

**No existing `circular_midpoint` / `circular_mean` / `circular_average` utility** exists anywhere in `ketu/`. Confirmed via `grep -rn "circular" ketu/` and `grep -rn "midpoint" ketu/` — only doc references to "midpoint" appear, no implementation. Phase 17 introduces this helper. It should live in `ketu/composite/core.py` (not in `ketu/calculations.py`) because (a) it is consumed exclusively by composite, (b) future use cases (mean Black Moon Lilith osculating-vs-mean midpoints, etc.) are speculative, (c) `ketu/calculations.py` is becoming a god module and we should avoid pile-on.

**Confidence:** HIGH on what we reuse; MEDIUM on the recommendation to refactor `calculate_aspects_vectorized` (it could go either way; the planner has discretion).

---

## Astro.com Oracle Pairs

COMP-04 / ROADMAP criterion #3 requires **2+ hand-validated composite charts** as pinned oracle tests with documented max longitude delta.

### Approach to oracle generation

Phase 16's synastry oracles use **self-consistency** (`tests/synastry/test_oracle.py` `validation_source`: "Self-consistency oracle — generated from compute_chart + calculate_synastry") because Astro.com is anti-bot for automated scraping (per 16-RESEARCH Pitfall) AND because the two relevant outputs (synastry aspect rows; composite longitudes) can be re-derived deterministically from the natal inputs. **Composite faces the same constraint**: Astro.com is bot-blocked from our WebFetch attempts (confirmed in §Sources below), so manual cross-validation by a human is the only way to get true Astro.com numbers.

Three viable paths for the planner:

1. **Self-consistency only** (synastry's choice). Generate `calculate_composite` on the same two natal pairs that synastry uses (Curie, Diana/Charles, Lennon/Ono — three existing fixtures), pin the resulting composite longitudes as expected values with `tolerance_deg=0.0001` (machine-precision regression). Honest about what's validated (the function's stability, not its agreement with Astro.com). Mark `validation_source` accordingly.
2. **Self-consistency + manual cross-check** (synastry Plan 16-05's deferred follow-up). Same as (1), plus a manual one-time validation against Astro.com by the developer that's recorded in a `cross_check_*.md` note alongside the fixture. Astro.com numbers are pinned with `cross_check_tolerance_deg=0.1` in the JSON fixture, and a single test asserts agreement at that broader tolerance. **Recommended.**
3. **Astro.com-first oracle** (would require live Astro.com numbers up-front, NOT achievable from this research session — bot-blocked).

### Recommended fixture pairs

Use the **three existing synastry fixtures** for composite oracles too (zero new fixture data needed; same birth records; just a new test file):

| Pair | Slug | Use for composite? | Notes |
|------|------|--------------------|-------|
| Marie & Pierre Curie | `curie` | YES | Pierre's birth time is C-rated (uncertain) — composite ASC/MC are unreliable for this pair; pin **bodies only**, exclude ASC/MC from oracle. |
| Diana & Charles | `diana_charles` | YES | Both birth times AA-rated (Astro.com Databank) — pin **bodies + ASC + MC**. **Primary oracle.** |
| John Lennon & Yoko Ono | `lennon_ono` | YES | Both AA-rated — pin **bodies + ASC + MC**. **Secondary oracle.** |

This gives 2+ reliable composite ASC/MC oracles (Diana/Charles + Lennon/Ono) plus a bodies-only oracle (Curie) for additional coverage, **with zero new birth-data research required**.

### Expected fixture schema (extend the existing `oracle_*.json` shape)

```json
{
  "schema_version": 2,
  "name": "diana_charles",
  "rodden_a": "AA",
  "rodden_b": "AA",
  "chart_a": { "subject_name": "Diana", "iso_date": "1961-07-01T18:45:00Z", "lat": 52.83, "lon": 0.51, "source": "..." },
  "chart_b": { "subject_name": "Charles", "iso_date": "1948-11-14T21:14:00Z", "lat": 51.50, "lon": -0.13, "source": "..." },
  "expected_composite": {
    "body_lons": {
      "Sun":     {"deg": <to-be-computed>, "tolerance_deg": 0.0001},
      "Moon":    {"deg": <to-be-computed>, "tolerance_deg": 0.0001},
      "...":     "...",
      "Pluto":   {"deg": <to-be-computed>, "tolerance_deg": 0.0001}
    },
    "asc": {"deg": <to-be-computed>, "tolerance_deg": 0.0001},
    "mc":  {"deg": <to-be-computed>, "tolerance_deg": 0.0001}
  },
  "validation_source": "Self-consistency oracle - generated from compute_chart + calculate_composite on <date> using ketu v1.2. Cross-validation against Astro.com is an optional manual follow-up.",
  "cross_check_astro_com": {
    "performed": false,
    "tolerance_deg": 0.1,
    "notes": "Deferred to close-out plan; bot-blocked from automated retrieval."
  }
}
```

**Expected tolerance ranges:**

- **Self-consistency:** `<1e-4°` (~0.36 arcsec, machine precision for the IEEE-754 / NumPy-NumPy round-trip). This is the headline gate.
- **Cross-Astro.com (if performed manually):** `<0.1°` (6 arcmin) — accounts for (a) Astro.com's display precision (typically 1 arcmin), (b) potential ephemeris-version differences (Astro.com uses Swiss Ephemeris; we use cached/Swisseph too, so they should agree closely), (c) potential method differences (Astro.com may default to reference-place method depending on user settings).
- **Phase 14 baseline:** Natal `body_lons` agreement vs swisseph oracle is `<0.01°` (1-arcmin spec, ~0.36 arcmin actual in Phase 14 tests). Composite tolerance should be similar; `0.1°` for cross-Astro is generous.

### Sample numbers (placeholders for the planner)

I **deliberately did not pre-compute** the expected composite longitudes from the existing fixtures in this research session — that's a Plan 17-XX task (generate fixtures via the new `calculate_composite` function once it exists, then commit the JSON values as the regression pin). Pre-computing them now would create a circular oracle (we'd be validating the function against its own output before the function exists).

**Planner action:** Sequence "Plan 17-XX: generate composite oracle fixtures via the implemented function and pin the results" as a task AFTER the implementation but BEFORE the close-out, mirroring how synastry Plan 16-03 generated its oracle JSONs after Plan 16-02 finished the implementation.

**Confidence:** HIGH on the fixture-generation pattern (synastry precedent is clean); MEDIUM on the cross-Astro.com numbers (they will be hand-validated post-implementation, not pre-).

---

## Davison Guard (Module Docstring)

COMP-04 / ROADMAP criterion #4 requires the module docstring to label Davison as deferred-to-v1.3, with **no aspirational reference** (no `# TODO: davison`, no `def davison_composite(...): raise NotImplementedError`, no stub).

### Recommended docstring text (drop into `ketu/composite/__init__.py`)

```python
"""Composite chart subpackage — midpoint composite from two natal charts.

Public API surface (COMP-01..04 of the v1.2 milestone):

- :func:`calculate_composite` — Derive a midpoint composite chart from two
  :data:`ketu.charts.CHART_DTYPE` scalar records. Returns a scalar
  :data:`ketu.charts.CHART_DTYPE` whose body longitudes, ASC, MC, ARMC, and
  Vertex are circular midpoints of the two natals, and whose house cusps are
  derived from the composite ASC and MC via Porphyry-style trisection (NOT
  recomputed from any partner's geographic context).
- :func:`circular_midpoint` — Short-arc midpoint on the unit circle, modulo
  360°. Vectorised. ``circular_midpoint(359.0, 1.0) == 0.0`` (NOT 180.0).

See Also
--------
ketu.charts.compute_chart : Build the per-partner CHART_DTYPE inputs.
ketu.synastry.calculate_synastry : Inter-chart aspect computation (the
    complementary pair-chart operation on the same CHART_DTYPE pair).

Notes
-----
**Midpoint method only.** Phase 17 implements the pure midpoint composite
(every CHART_DTYPE field is a circular midpoint of the two natals; house
cusps are derived geometrically from composite ASC + composite MC). The
'reference place method' documented by Astrodienst, which back-computes
the composite ASC and houses from a chosen reference latitude, is NOT
implemented — users requiring that convention should compute it externally
from the composite ARMC stored in the output.

**Davison composite is NOT in scope.** Davison composites — built at the
temporal midpoint (mid-Julian-Date) and spatial midpoint (geographic
great-circle midpoint) of two births, then computed as a fresh natal — are
deferred to v1.2 release follow-up (tracked separately in the v1.3 roadmap).
The midpoint method implemented here is algebraically distinct from
Davison and the two conventions are not interchangeable.

**Composite (jd, lat, lon) are bookkeeping, NOT a moment-and-place.** The
``jd``, ``lat``, and ``lon`` fields on the output CHART_DTYPE are stored
as linear (jd, lat) and circular (lon) midpoints of the two natals for
round-trip consistency. They have NO astronomical interpretation as
"the moment-and-place of the composite" — that interpretation requires
Davison, which is out of scope.
"""
```

### Style precedent in the codebase

The `ketu/synastry/__init__.py` docstring (lines 1–40) uses the same trichotomy: public surface bullets, See Also, Notes with caveats. The Davison guard sits in **Notes** (loudest visibility, no NotImplementedError stub anywhere). Phase 16's `ketu/synastry/api.py` uses the inline-prose "deferred to v1.3 if Phase 17 / 18 demand it" pattern (line 194); Phase 17 should be more explicit because Davison is a **named alternative method**, not a feature-gap.

**Confidence:** HIGH (style precedent is established; ROADMAP language is precise).

---

## Test Layout

Mirror `tests/synastry/` exactly:

```
tests/
└── composite/
    ├── __init__.py
    ├── conftest.py                            # Reusable composite chart pairs (session-scoped)
    ├── fixtures/
    │   ├── oracle_curie.json                  # Body-only oracle (Pierre's birth time C-rated)
    │   ├── oracle_diana_charles.json          # Primary oracle (both AA-rated)
    │   └── oracle_lennon_ono.json             # Secondary oracle (both AA-rated)
    ├── test_circular_midpoint.py              # COMP-02 ratchet (mid(359,1)==0, wraparound suite,
    │                                          #   antipodal edge case, vectorisation, NaN propagation)
    ├── test_calculate_composite.py            # COMP-01 surface tests (shape, dtype, fields populated)
    ├── test_composite_houses.py               # COMP-03 ratchet (houses derived from composite ASC/MC;
    │                                          #   trisection-style cusps; NOT recomputed from partner jd/lat/lon)
    ├── test_dtype.py                          # Output is CHART_DTYPE (no schema regression)
    ├── test_oracle.py                         # COMP-04 ratchet (2+ pinned reference pairs)
    └── test_composite_coverage_gate.py        # Sentinel for the composite_coverage_gate marker
```

**Session-scoped fixtures** to reuse: every fixture from `tests/synastry/conftest.py` is reusable for composite (`chart_a_paris`, `chart_b_nyc`, `chart_b_tokyo`, `chart_b_sydney`, `chart_b_reykjavik`, `chart_a_retrograde_mercury`). The planner can either **import them across packages** (uncommon but supported via `pytest_plugins`) or **duplicate them** in `tests/composite/conftest.py` (simpler; small DRY tax; matches Phase 16's choice to not import from `tests/charts/conftest.py`).

**Recommendation:** Duplicate — six tiny `compute_chart(...)` calls cost nothing to repeat and the test packages stay self-contained.

**Confidence:** HIGH (direct synastry precedent; no contraindications).

---

## Coverage Gate

Phase 16's pattern is fully established and should be replicated for Phase 17:

### `pyproject.toml` (line 77–82) — add alphabetically

```toml
markers = [
    "slow: ...",
    "charts_coverage_gate: CHART-05 95% coverage gate for ketu.charts (run via Makefile target `make charts-coverage`)",
    "composite_coverage_gate: COMP-XX 95% coverage gate for ketu.composite (run via Makefile target `make composite-coverage`)",
    "houses_coverage_gate: ...",
    "synastry_coverage_gate: ...",
]
```

The COMP-XX identifier should be assigned by the planner — there's no existing COMP-05 in REQUIREMENTS for a coverage gate, so this is a Phase 17 close-out addition. Recommend `COMP-05: ketu.composite ≥95% line coverage gate` as a new acceptance criterion mirroring SYN-05 / CHART-05 / HOU-09.

### `Makefile` — add `composite-coverage` target

```makefile
## composite-coverage: Run the COMP-05 ≥95% coverage gate scoped to ketu.composite.
##
## Mirror of synastry-coverage. Two-step pattern to avoid the NumPy
## `_NoValueType` reload bug triggered when coverage.py uses
## `source=ketu.composite` (sub-package). With `source=ketu` (full package)
## coverage works cleanly.
composite-coverage:
	$(PYTHON) -m pytest tests/composite/ -o addopts="" --cov --cov-report= --cov-fail-under=0
	$(PYTHON) -m coverage report --include='ketu/composite/*' --fail-under=95 -m
```

Add `composite-coverage` to the `.PHONY` line.

### Should this land in Phase 17 or close-out?

**Recommendation: land in Phase 17 from the start.** Phase 16 deferred the gate to Plan 16-04 (after the implementation was complete) but the gate was scoped from Plan 16-01's research. Phase 17 should bake the gate into the early plans so coverage is monitored throughout implementation, not retrofitted. The marker registration + Makefile target are zero-cost up-front and prevent the "we hit 80%, now what?" surprise.

**Confidence:** HIGH (synastry precedent; coverage gate is a 6-line change).

---

## Risks & Pitfalls (ranked by likelihood × blast radius)

### Pitfall 1 (HIGH × HIGH): Circular-midpoint sign error producing `180°` for `mid(359°, 1°)`

**What goes wrong:** Naïve `(a + b) / 2 % 360.0` returns `180.0` for `(359, 1)` — the **antipodal** midpoint, geometrically wrong. Composite Sun/Moon/etc. ends up on the opposite side of the chart from where it should be.

**Why it happens:** `a` and `b` are positive floats in `[0, 360)`; their arithmetic mean equals the short-arc midpoint only when `|a - b| <= 180°`. The wraparound at 0°/360° silently breaks the equivalence.

**How to avoid:** Use the complex-exponential formulation (or the equivalent signed-diff form). Pin `circular_midpoint(359.0, 1.0) == 0.0` as a regression test (COMP-02). Add a parametrized wraparound suite covering: `(359, 1)`, `(0, 358)`, `(180, 0)` (antipodal — pin behaviour explicitly), `(270, 90)` (90° apart spanning the wrap), `(45, 315)` (90° apart not spanning the wrap).

**Warning signs:** Oracle test failures with composite body longitudes off by exactly `180°` from expected.

### Pitfall 2 (HIGH × HIGH): Conflating composite midpoint with Davison time-midpoint

**What goes wrong:** A future contributor (or this phase's executor under deadline pressure) implements `calculate_composite` by computing the mid-Julian-Date and calling `compute_chart(mid_jd, mid_lat, mid_lon)` — a **Davison composite**, not a midpoint composite. Users get Davison numbers while the docstring claims midpoint.

**Why it happens:** Davison is conceptually simpler ("just compute a chart at the midpoint of time and space"); the implementation may feel cleaner; the two methods agree closely for partners born near each other in time and place, hiding the bug for the common case.

**How to avoid:**
- Write a **ratchet test that fails if the implementation accidentally calls `compute_chart`** — assert that `composite["jd"]` equals `(chart_a["jd"] + chart_b["jd"]) / 2` for arbitrary natal inputs (Davison would NOT preserve this trivially; it would store the mid-JD it actually used). Pair with a test asserting `composite["body_lons"][0]` equals `circular_midpoint(chart_a["body_lons"][0], chart_b["body_lons"][0])` exactly — a Davison Sun is NOT this midpoint in general.
- Module docstring guard (see §Davison Guard).
- Reviewer checklist: "Does this implementation call `compute_chart` anywhere? It must not."

**Warning signs:** Composite bodies that "feel like real ephemeris values" but disagree with hand-computed midpoints for any partner pair spanning >1 year of birth dates.

### Pitfall 3 (HIGH × MEDIUM): House recomputation drift — calling `calculate_houses(jd_a, lat_a, lon_a, ...)`

**What goes wrong:** Implementation falls back to "use partner A's geographic context for the composite houses" because that's the path of least resistance — call `calculate_houses` with one partner's `(jd, lat, lon)`. Composite cusps end up biased toward partner A's natal frame. Silent COMP-03 violation.

**Why it happens:** The existing `calculate_houses(jd, lat, lon)` signature is the canonical house-cusp entry point in Ketu, and the obvious thing to do is "just call it with one partner's coordinates." There is no public function today that accepts `(asc, mc)` directly.

**How to avoid:**
- Implement Approach A inline (don't call `calculate_houses` at all from `calculate_composite`). Reuse the trisection algebra by copying lines 167–186 of `porphyry.py` into the composite module.
- Add an **anti-regression ratchet test**: assert that swapping `chart_a` and `chart_b` produces the same composite cusps (modulo numerical noise). If the implementation accidentally privileges one partner, this test fails because swap symmetry breaks. Document in the test docstring exactly why this is a COMP-03 ratchet.
- Code review: search for `calculate_houses` calls in `ketu/composite/` — there should be **zero**.

**Warning signs:** Composite cusps that drift when you swap partner A and partner B; cusps that exhibit polar-fallback behaviour at extreme latitudes (Approach A is polar-safe by construction; if the implementation suddenly cares about latitude, something is wrong).

### Pitfall 4 (MEDIUM × HIGH): NumPy modulo on negative angles

**What goes wrong:** Implementer uses Python's `%` on negative-valued intermediate computations and assumes mathematical modulo semantics; depending on NumPy version and dtype, signed-vs-unsigned wraparound behaviour can flip subtly.

**Why it happens:** Python's `%` IS mathematical modulo for floats (`-1.0 % 360.0 == 359.0`), but if anyone accidentally uses C-style `math.fmod` or a NumPy operation that delegates differently, sign can leak through.

**How to avoid:** Stick to `np.mod(x, 360.0)` or `x % 360.0` (NumPy preserves Python-modulo semantics for `np.float64` and `np.float32`). Pin a test like `circular_midpoint(-1.0, 1.0) == 0.0` (negative input that should normalize to the same answer as `(359, 1)`) — though spec inputs are always non-negative, defensive normalization at the top of `circular_midpoint` (`a = np.asarray(a) % 360.0`) costs one line and rules out the whole class.

**Warning signs:** Off-by-360° errors that disappear when inputs are pre-normalized but reappear for raw inputs.

### Pitfall 5 (MEDIUM × MEDIUM): Astro.com oracle mismatch due to convention difference

**What goes wrong:** Manual cross-validation against Astro.com produces a `0.5° to 2°` disagreement on ASC/MC even though the bodies agree exactly. This is because Astro.com defaults to the **reference-place method** (not the pure midpoint method), and the user's account settings determined the reference latitude.

**Why it happens:** Astro.com's free composite calculator has BOTH methods exposed and the default depends on the user's chart-form preset. Without knowing exactly which setting was used, "Astro.com agrees" is ill-defined for ASC/MC.

**How to avoid:**
- Document in the `validation_source` JSON field which Astro.com option was used: typically "Extended chart selection → method → 'midpoint method'" needs to be explicit. Cross-check the partner's account didn't override.
- Use **pure-self-consistency as the headline gate** (`tolerance_deg=0.0001`); treat Astro.com cross-check as an **advisory tolerance** (`tolerance_deg=0.1`) with a note explaining the method ambiguity.
- For the body longitudes (not ASC/MC), Astro.com agreement should be tight regardless of method — bodies are method-invariant. Pin those tightly.

**Warning signs:** A pair where bodies agree to `0.01°` but ASC/MC differ by `1.5°` — that's the reference-place vs midpoint signature.

### Pitfall 6 (MEDIUM × LOW): `system="placidus"` semantic confusion

**What goes wrong:** A user calls `calculate_composite(a, b, system="koch")` expecting Koch-style cusps and receives Porphyry-trisection cusps because of Approach A's "all systems collapse to Porphyry" reality. They interpret the bug as "Phase 17 is broken" rather than "the spec is ambiguous."

**Why it happens:** The `system=` argument's API symmetry with `compute_chart` invites users to assume it has the same semantic meaning. Under Approach A, it doesn't.

**How to avoid:**
- **Loudest possible docstring warning** on `calculate_composite`'s `system` parameter: "For the pure midpoint composite, the `system=` value is stored in the output's `system` field for bookkeeping but does NOT change the cusp computation — all systems collapse to a Porphyry-style trisection of (composite ASC, composite MC). If you need Placidus-flavored composite cusps, use the reference-place method externally; that path is not implemented in Phase 17."
- **Optional ratchet:** raise `ValueError` for `system not in {"placidus", "porphyry"}` and accept only those two (with `"placidus"` documented as "synonym for porphyry under the pure midpoint method"). This is more user-hostile but eliminates the confusion vector. Recommend NOT doing this — match Approach A's "accept any system, record it, compute the same cusps" behaviour and let the docstring carry the load. Discuss with stakeholders if there's a real demand for Placidus-flavored composites.

**Warning signs:** GitHub issues asking "why does `system='koch'` produce the same result as `system='placidus'` for composite?"

### Pitfall 7 (LOW × HIGH): Antipodal-bodies edge case (`a == b + 180°`)

**What goes wrong:** When the two natal Suns (or any body pair) are exactly antipodal, `circular_midpoint` faces an ambiguous answer — both midpoints are equally valid. The complex-exponential formula returns `np.angle(0+0j) == 0.0`, which is one of the two answers but NOT the geometrically "shorter arc" answer (there is no shorter arc).

**Why it happens:** Two unit vectors `exp(i*a)` and `exp(i*-a)` sum to zero; `np.angle(0)` returns `0` by convention; the "true" answer is ill-defined.

**How to avoid:**
- Pin `circular_midpoint(0.0, 180.0) == 0.0` (or `90.0`, depending on whichever the implementation returns — pin what you get, document why it's ambiguous). The test is a tripwire, not an assertion of correctness.
- In practice, two partners with exactly antipodal Suns are astronomically possible but vanishingly rare; warn in the docstring but don't add special-case logic.

**Warning signs:** Composite output where one body is exactly `0.0` despite both natals having that body far from `0.0`/`180.0` — sniff for antipodal-pair regression.

### Pitfall 8 (LOW × MEDIUM): Body axis ordering drift

**What goes wrong:** The `(13,)` body axis is FROZEN by D-08 and ordered `[Sun, Moon, ..., Lilith]`. If the composite implementation hand-rolls the body loop in a different order (e.g., alphabetical), the composite output has body indices that disagree with the input charts.

**Why it happens:** The 13-body axis ordering is a project-wide invariant but easy to violate by hand-rolling `for body_name in sorted(BODIES.keys())`.

**How to avoid:**
- Use NumPy elementwise array operations on the `(13,)` axis: `composite_body_lons = circular_midpoint(chart_a["body_lons"], chart_b["body_lons"])`. No loop, no order question.
- Add a ratchet test: `assert composite["body_lons"].shape == (13,)` and `composite["body_lons"][0] == circular_midpoint(chart_a["body_lons"][0], chart_b["body_lons"][0])` (index 0 is Sun by D-08).

**Warning signs:** Composite Sun longitude matching expected composite Moon (off-by-one), or any obviously-wrong body assignment.

---

## Open Questions for the Planner

These are decisions the research could not resolve without stakeholder input. Flagged for the planner to either decide explicitly or escalate via a `/gsd:discuss-phase` round before locking the plan.

### Q1: Approach A vs Approach B for house computation

- **What we know:** Both are compliant with COMP-03's literal text; A is mathematically purer and polar-safe; B preserves `system=` semantic meaning at the cost of a reference-latitude decision.
- **What's unclear:** Whether the user explicitly wants `system="koch"` etc. to produce different composite cusps. Robert Hand's *Planets in Composite* (1975) uses what amounts to Approach A; Astro.com's interface offers both via the "reference place method" toggle.
- **Recommendation:** Pick A; flag in plan; if implementation reveals a strong reason to switch (e.g., oracle tests don't match Astro.com defaults at tight tolerance), revisit. Plan must explicitly document the choice in `17-CONTEXT.md` if one is generated later.

### Q2: `system=` argument behaviour under Approach A — accept-and-ignore vs raise

- **What we know:** Under Approach A, any `system` value produces the same Porphyry-trisection cusps.
- **What's unclear:** Whether to accept any string (lenient) or raise `ValueError` for `system not in {"placidus", "porphyry"}` (strict).
- **Recommendation:** Accept any registered house system name (call `get_system(system)` for validation, then ignore the function it returns). Store the user's stated `system` in the output for bookkeeping. Document the no-op semantics loudly. This matches `calculate_houses`'s laxity (it raises only on **unknown** systems, not on "I asked for X but you gave me Y").

### Q3: `jd`/`lat`/`lon` storage convention — midpoints vs NaN

- **What we know:** A midpoint composite has no canonical `(jd, lat, lon)`. Linear midpoints have no physical meaning but provide round-trip stability. NaN is honest but propagates through downstream consumers.
- **What's unclear:** Whether any downstream consumer (Phase 18, 19, ML adapters) would mis-interpret midpoint `(jd, lat, lon)` as "a real moment" and feed them back into `compute_chart` or `is_day_chart`.
- **Recommendation:** Linear midpoints with a LOUD docstring guard. Add a Phase 17 ratchet that explicitly tests `is_day_chart(composite["jd"], composite["lat"], composite["lon"])` produces "garbage but doesn't raise" — i.e., the function is callable on composite metadata but the result is meaningless. This pins behaviour without endorsing it.

### Q4: Speed convention — linear average vs NaN

- **What we know:** Composite speeds have no physical interpretation; linear average is conservative and dtype-preserving; NaN is honest but propagates.
- **What's unclear:** Whether `applying`-style synastry tests downstream of composite (if any) would mis-interpret composite speeds.
- **Recommendation:** Linear average. Pin the convention in tests. Document in the function docstring that composite `body_speeds` are not physically meaningful (mirror of the `jd`/`lat`/`lon` guard).

### Q5: Composite ARMC convention — circular midpoint vs derived from composite MC

- **What we know:** Two reasonable choices: (a) `circular_midpoint(armc_a, armc_b)`, (b) re-derive from composite MC via the inverse `compute_ascmc`. Choice (a) is cheaper and consistent with "everything is a midpoint"; choice (b) keeps ARMC algebraically tied to the stored MC.
- **What's unclear:** Whether downstream consumers (Phase 18 Solar Return likely) consume composite ARMC at all.
- **Recommendation:** Choice (a) — `circular_midpoint(armc_a, armc_b)`. Test that the relationship `MC ≈ atan2(sin(ARMC), cos(ARMC) * cos(eps))` is **approximately** preserved (it won't be exact because `circular_midpoint(armc_a, armc_b)` doesn't generally map to the same MC as `circular_midpoint(mc_a, mc_b)` — that's a real mathematical consequence of midpointing two non-linear quantities independently). Document the small discrepancy if it shows up in tests; it's not a bug.

### Q6: Test fixture cross-validation against Astro.com — required at v1.2 release or deferrable?

- **What we know:** Astro.com is bot-blocked from automated fetching; manual cross-validation requires a developer to manually generate composites for the three pairs and record numbers.
- **What's unclear:** Whether ROADMAP's "hand-validated against Astro.com" wording requires that hand validation to happen INSIDE Phase 17 vs in a close-out follow-up (synastry's pattern, Plan 16-05).
- **Recommendation:** Generate the oracle fixtures via self-consistency in the Phase 17 implementation plans; defer the manual Astro.com cross-check to a Plan 17-XX close-out task that updates `cross_check_astro_com.performed = true` once a developer has done it. This mirrors synastry Plan 16-05's pattern verbatim and unblocks the implementation phase from a manual UI task.

---

## Out-of-Scope Reminders (Davison)

**Davison composite chart is OUT OF SCOPE for Phase 17.** Specifically:

- ❌ Do NOT add a `davison=False` kwarg to `calculate_composite`.
- ❌ Do NOT add a `def calculate_davison(...): raise NotImplementedError` stub.
- ❌ Do NOT add a `# TODO: Davison in v1.3` comment in the implementation source.
- ❌ Do NOT add a `Davison` reference under "See Also" in any docstring.
- ✅ DO label Davison as deferred-to-v1.3 in the module docstring's **Notes** section (LOUD).
- ✅ DO ensure no code path inside `calculate_composite` accidentally implements Davison (Pitfall 2).

The label-and-walk-away pattern matches REQUIREMENTS §"Deferred to v1.3" and ROADMAP §Phase 17 success criterion #4 verbatim: "no aspirational reference".

---

## Sources

### Primary (HIGH confidence)

- [`ketu/charts/core.py`](../../../ketu/charts/core.py) — `CHART_DTYPE` definition and rationale.
- [`ketu/charts/api.py`](../../../ketu/charts/api.py) — `compute_chart` construction path; aspect-matrix loop.
- [`ketu/synastry/api.py`](../../../ketu/synastry/api.py) — pair-chart computation precedent.
- [`ketu/synastry/__init__.py`](../../../ketu/synastry/__init__.py) — subpackage docstring + `__all__` pattern.
- [`ketu/houses/api.py`](../../../ketu/houses/api.py) — `calculate_houses(jd, lat, lon, system, polar_fallback)` entry point (line 47); `SYSTEMS` dispatch (line 162).
- [`ketu/houses/porphyry.py`](../../../ketu/houses/porphyry.py) — `porphyry_cusps(armc, lat, eps)` (line 100); **trisection algebra at lines 167–186 is the canonical reference for Approach A**.
- [`ketu/houses/ascmc.py`](../../../ketu/houses/ascmc.py) — `compute_ascmc` / `compute_armc` closed-form formulas.
- [`ketu/houses/registry.py`](../../../ketu/houses/registry.py) — `SYSTEMS` dict + `get_system(name)` lookup.
- [`tests/synastry/conftest.py`](../../../tests/synastry/conftest.py) — fixture pattern.
- [`tests/synastry/test_oracle.py`](../../../tests/synastry/test_oracle.py) — oracle test pattern.
- [`tests/synastry/test_synastry_coverage_gate.py`](../../../tests/synastry/test_synastry_coverage_gate.py) — coverage-gate sentinel pattern.
- [`pyproject.toml`](../../../pyproject.toml) lines 60–82 — marker registration + setuptools packages list.
- [`Makefile`](../../../Makefile) lines 50–66 — coverage-gate Makefile target template.
- [`.planning/REQUIREMENTS.md`](../../REQUIREMENTS.md) — COMP-01..04 verbatim, Davison v1.3 deferral.
- [`.planning/ROADMAP.md`](../../ROADMAP.md) — Phase 17 success criteria 1–4.
- [`.planning/phases/16-synastry/16-RESEARCH.md`](../16-synastry/16-RESEARCH.md) — research-document style precedent.

### Secondary (MEDIUM confidence, multi-source corroboration)

- [pyswisseph programmer's manual — house cusp calculation](https://github.com/astrorigin/pyswisseph/blob/master/docs/programmers_manual/house_cusp_calculation.rst) — composite ARMC + averaged epsilon convention (SwissEph C API guidance). **Authoritative for the reference-place method;** corroborates Approach B mechanically but does not endorse it over Approach A.
- WebSearch [composite chart midpoint method ASC MC](https://www.google.com/search?q=%22composite+chart%22+midpoint+method+ASC+MC) — multiple sources (Astro-Seek, Cafe Astrology, Astrohelpers, LUNA Astrology, Starzology, Robert Hand commentary) describe the two-method dichotomy (midpoint vs reference-place); pure-midpoint definition matches Approach A.
- [Astro.com Composite Chart wiki](https://www.astro.com/astrowiki/en/Composite_Chart) (bot-blocked from WebFetch; cited via secondary commentary) — Astrodienst's documented preference is the reference-place method, but the pure midpoint method is supported and is what Robert Hand's *Planets in Composite* (1975) describes.

### Tertiary (LOW confidence, flagged for manual validation)

- Robert Hand, *Planets in Composite* (1975) — cited indirectly through secondary commentary; I did not retrieve the primary text in this research session. The recommendation to use Approach A rests partly on the secondary characterisation of Hand's method. **Planner should verify** if a copy of the book is available, especially for the exact house-cusp derivation Hand specifies.
- Exact Astro.com numerical outputs for the three oracle pairs (Curie, Diana/Charles, Lennon/Ono) — bot-blocked; **manual one-time validation by a developer is required** for the cross-check assertion to be meaningful. Plan 17-XX close-out task.

---

## Confidence Breakdown

| Area | Level | Reason |
|------|-------|--------|
| Standard stack (NumPy + existing Ketu primitives) | HIGH | All needed primitives exist in v1.0/v1.1/v1.2 codebase; verified by direct file reads. |
| Architecture (`ketu/composite/` subpackage layout) | HIGH | Direct synastry precedent; symmetric naming; pyproject + Makefile pattern is established. |
| Circular-midpoint math | HIGH | Textbook circular-statistics formula; vectorised in NumPy; wraparound case is a one-line proof. |
| House computation strategy (Approach A) | MEDIUM-HIGH | Mathematically correct and COMP-03 compliant; recommendation over Approach B rests partly on stylistic preference (the planner may legitimately disagree). |
| Body coverage (13 bodies, frozen axis) | HIGH | D-08 freeze; latitudes/speeds conventions documented; trivial implementation. |
| `is_day_chart` for composite | HIGH | D-12 keeps sect out of CHART_DTYPE; COMP-01..04 doesn't mention it; no action needed. |
| Module layout (`ketu/composite/`) | HIGH | Synastry precedent is unambiguous. |
| Public API (`calculate_composite`, `circular_midpoint`) | HIGH | Spec names locked by COMP-01/COMP-02. |
| Astro.com oracle pattern (self-consistency primary + manual cross-check deferred) | MEDIUM | Pattern matches synastry; bot-block forces self-consistency as primary; manual cross-check is an honest follow-up. |
| Test layout (`tests/composite/`) | HIGH | Direct synastry mirror. |
| Coverage gate (`composite_coverage_gate`) | HIGH | Synastry / charts / houses precedent; 6 lines of config. |
| Pitfalls 1–8 | HIGH-MEDIUM | Pitfalls 1–4 are direct consequences of the math; 5–8 are secondary edges with smaller blast radius. |
| Davison guard wording | HIGH | Style precedent in `ketu/synastry/__init__.py` Notes; ROADMAP wording is precise. |

**Research date:** 2026-05-11
**Valid until:** 2026-06-11 (30 days; the v1.2 milestone is stable; no upstream library churn expected in this window)
