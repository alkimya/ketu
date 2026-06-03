# Phase 33: Lunar Declination δ — Research

**Researched:** 2026-06-03
**Domain:** Equatorial declination δ of solar-system bodies in a pure-NumPy ephemeris; chart-dtype extension; finite-difference velocity; out-of-bounds gating.
**Confidence:** HIGH (every code anchor read from source and 2 claims re-verified numerically against the live package; astronomy reused verbatim from the pre-existing HIGH-confidence brief).

---

## Summary

This phase is almost entirely an **assembly + wiring** job over code that already exists and is already tested. The astronomy is settled: a project-level brief at `.planning/research/DECLINATION.md` (228 lines, HIGH) already verified that ketu's `coordinates.py` rectangular chain is numerically identical (Δ = 0 to machine precision) to Meeus eq. 13.4 `sin δ = sin β·cos ε + cos β·sin ε·sin λ`. **Do not redo that astronomy.** This RESEARCH.md adds the thing the brief lacked: the exact existing signatures, exact insertion points, and exact test/doc patterns the planner must mirror.

I re-verified two things against the live package (not just the brief): (1) the coordinate chain and the direct Meeus formula agree to `max|Δ| = 7.1e-15` when **vectorized over arrays**, confirming the hot path can be loop-free (DECL-02); and (2) **`true_obliquity(jd)` accepts arrays at runtime** even though its type hint says `jd: float -> float` — `nutation()` is pure-NumPy so it broadcasts. This resolves the only real open vectorization risk in the phase (OOB via `true_obliquity`).

The single largest finding for the planner is asymmetric downstream propagation of the new `body_decl` field (DECL-07): **Returns inherit it for free** (they call `compute_chart`), **Synastry does not need it** (it emits its own non-CHART dtype), but **Composite silently zero-fills it** (it allocates `np.zeros((), CHART_DTYPE)` and copies fields by name; an un-named `body_decl` becomes `0.0`, not garbage, but semantically wrong). The planner must explicitly decide composite's behaviour.

**Primary recommendation:** Add four functions to `ketu/calculations.py` (mirroring `lat`/`lat_velocity`/`is_ascending`), one `("body_decl", "f8", (14,))` field to `CHART_DTYPE` populated inside `compute_chart` from already-fetched `body_lats`/`body_lons` + `true_obliquity(jd_b)`, extend the existing `tests/charts/test_dtype.py` ratchets, and document en+fr — all additive, `is_ascending` (β) byte-for-byte unchanged.

---

## Reuse the Brief (do not duplicate the astronomy)

`/.planning/research/DECLINATION.md` is the authoritative astronomy source. Reuse, do not contradict:

| Brief section | Reusable conclusion | Status for this phase |
|---|---|---|
| §1 | δ = arcsin(sinβ·cosε + cosβ·sinε·sinλ) ≡ coordinates.py chain (Δ=0) | LOCKED — chain reuse mandated |
| §1 | Direct formula OR rectangular chain, both fine | LOCKED to **rectangular chain** (per STATE.md), with equivalence regression test (DECL-03) |
| §2 | montant = dδ/dt > 0; period = draconic/nodal month **27.21 d** (≈27.32 d tropical recurrence) | Reuse verbatim in docs (DECL-09) |
| §3 | OOB ⇔ \|δ\| > ε | LOCKED to **instantaneous ε(jd) via `true_obliquity`** (per STATE.md; brief D2 recommended `mean_obliquity`, OVERRIDDEN) |
| §4 | forward finite difference, step **0.01 d**, NO wraparound (δ bounded) | LOCKED — mirror `lat_velocity` |
| §5 D5 | name must not collide with `is_ascending` | LOCKED to `is_ascending_declination` |

**Two deliberate overrides of the brief's recommendations** (the brief flagged these as genuine forks; STATE.md picked the other branch):
- Brief D1/D2 recommended `mean_obliquity` for δ and OOB. **STATE.md locks `true_obliquity`** (instantaneous, nutation-corrected). Honor STATE.md. (Sub-arcminute difference; see Pitfall 6.)
- Brief D4 leaned toward the direct one-liner for `declination()`. **STATE.md locks the rectangular-chain reuse** with an equivalence regression test. Honor STATE.md.

---

## Resolved Code Anchors (the value-add)

All read from source on 2026-06-03. Format: `file:line` · signature/snippet · "planner uses for X".

### Anchor 1 — Coordinate chain (the δ math)
`ketu/ephemeris/coordinates.py`
- `spherical_to_rectangular(lon, lat, r) -> (x, y, z)` — line 12. Vectorized (uses `np.deg2rad`, elementwise). Accepts arrays.
- `ecliptic_to_equatorial(x, y, z, obliquity) -> (x_eq, y_eq, z_eq)` — line 94. Vectorized. `obliquity` in **degrees**.
- `rectangular_to_spherical(x, y, z) -> (lon, lat, r)` — line 48. Vectorized. **Returns `(lon, lat, r)` where `lat` IS the declination** when fed equatorial rectangulars. `lon` normalized to [0,360); `lat = rad2deg(arcsin(z/r))` ∈ [−90,+90] (line 86). Has a scalar `if r == 0: return 0,0,0` branch (line 78–80) and an array `np.where(r==0,1.0,r)` branch (line 83) — both array-safe.

**Planner uses for:** `declination()` body — `λ,β = long(jd,b), lat(jd,b)` → `spherical_to_rectangular(λ,β,1.0)` → `ecliptic_to_equatorial(...,true_obliquity(jd))` → `rectangular_to_spherical(...)`, **return the 2nd element** (lat = δ). VERIFIED vectorized end-to-end (`max|Δ|` vs Meeus = 7.1e-15).

### Anchor 2 — Obliquity (the OOB threshold + chain ε)
`ketu/ephemeris/coordinates.py`
- `mean_obliquity(jd) -> degrees` — line 290. IAU 2006. Explicitly vectorized (docstring + `T` arithmetic).
- `nutation(jd) -> (nut_lon, nut_obl)` degrees — line 324. Type-hinted `float` but pure-NumPy ops (broadcasts).
- `true_obliquity(jd) -> degrees` — line 379. `return mean_obliquity(jd) + nutation(jd)[1]`. **Type hint says `jd: float -> float` but it accepts arrays at runtime** (VERIFIED: `true_obliquity(np.linspace(...))` returns an array). Units: **degrees**.

**Planner uses for:** OOB threshold (DECL-06) and the chain's ε argument. Use `true_obliquity(jd)` per STATE.md. NOTE the misleading type hint — `declination_velocity`/OOB are vectorizable despite it; if mypy --strict complains, `ketu.calculations` is in the relaxed mypy override (Anchor 12) so it likely won't.

### Anchor 3 — Velocity idiom to mirror (`lat_velocity`)
`ketu/calculations.py`
- `lat_velocity(jdate, body) -> float` — line 329. Body: `return body_properties(jdate, body)[4]`. It does **NOT** finite-difference itself — it reads the precomputed `lat_speed` (index 4) out of the 6-tuple from `body_properties`. The actual forward difference (`(lat2-lat)/jd_delta`, `jd_delta = 0.01`) lives in `ketu/ephemeris/planets.py` lines 99–278 and `ketu/ephemeris/chiron.py:164`.
- `long_velocity` (line 300, index 3), `dist_velocity_au` (line 357, index 5) — same read-from-tuple pattern.

**Planner uses for:** `declination_velocity(jdate, body)` (DECL-04). **Decision point for planner:** `body_properties` does NOT carry a `decl_speed` field, so `declination_velocity` CANNOT read a precomputed value like `lat_velocity` does. It must compute the forward difference itself: `(declination(jd+0.01, body) - declination(jd, body)) / 0.01`. Step constant `0.01` must match the package-wide `jd_delta`. No wraparound (δ bounded — unlike `lon_speed` which needs the ±180 fix in planets.py).

### Anchor 4 — `is_ascending` (β) to parallel without collision
`ketu/calculations.py:413`
```python
def is_ascending(jdate: float, body: int) -> bool:
    """Check if a body's latitude is rising. ..."""
    return bool(lat_velocity(jdate, body) > 0)
```
**Planner uses for:** `is_ascending_declination(jdate, body) -> bool` is the faithful parallel: `return bool(declination_velocity(jdate, body) > 0)`. DISTINCT quantity (δ-rise vs β-rise). `is_ascending` stays byte-for-byte unchanged (do not touch lines 413–438). Both must coexist in `__all__` (Anchor 9).

### Anchor 5 — How (λ, β) are obtained for `(jdate, body)`
`ketu/calculations.py`
- `long(jdate, body) -> float` — line 210, `return body_properties(jdate, body)[0]`.
- `lat(jdate, body) -> float` — line 243, `return body_properties(jdate, body)[1]`.
- `body_properties(jdate, body) -> np.ndarray` — line 98, LRU-cached, returns `[lon, lat, dist, lon_speed, lat_speed, dist_speed]`.
- Vectorized batch path: `calc_planet_position_batch(jd_array, planet_id, flags=0) -> (n,6)` — `ketu/ephemeris/planets.py:608`. This is what `compute_chart` uses (Anchor 7), so chart-level δ can reuse already-fetched lon/lat.

**Planner uses for:** `declination(jdate, body)` plugs `long`/`lat` into the chain (scalar path). The scalar `body_properties` covers 0..13 incl. Chiron (all 14 bodies, DECL — Chiron via BODY_STRATEGIES). For the chart hot path, do NOT re-fetch positions — derive δ from `compute_chart`'s already-computed `body_lons`/`body_lats` (Anchor 7).

### Anchor 6 — `CHART_DTYPE`
`ketu/charts/core.py:87` (full def lines 87–102). Current 14 fields, in order:
`jd, lat, lon, system, body_lons(14,), body_lats(14,), body_speeds(14,), cusps(12,), asc, mc, armc, vertex, aspect_matrix(14,14), aspect_orbs(14,14)`.
`body_lats` sits at index 5 (line 93), shape `(14,)`, `f8`. The `#:` doc block (lines 48–86) enumerates every field and the body-axis order — must be updated when `body_decl` is added.

**Planner uses for:** Insert `("body_decl", "f8", (14,))` parallel to `body_lats`. **Placement recommendation:** append AFTER `body_speeds` (or immediately after `body_lats`) — see Pitfall 3 for why position is safe internally. Update the `#:` doc block to list the new field (numpydoc/interrogate gate, Anchor 12).

### Anchor 7 — `compute_chart` (chart wiring / the insertion point)
`ketu/charts/api.py`
- `_vectorised_body_properties(jd_b) -> (body_lons, body_lats, body_speeds)` — line 56. Loops over the 14 bodies (NOT over leading shape S); each body via `calc_planet_position_batch` (natively jd-vectorized). Returns arrays shaped `S + (14,)`.
- `compute_chart(jd, lat, lon, system, aspects, polar_fallback) -> CHART_DTYPE array` — line 196. Assembly block lines 360–379: `out = np.empty(leading_shape, dtype=CHART_DTYPE)` then `out["body_lats"] = body_lats` (line 371), `out["body_speeds"] = body_speeds` (line 372).
- `_BODY_COUNT = len(_CANONICAL_BODIES)` = 14 — line 53. Pinned by `test_body_count_frozen_at_fourteen`.

**Planner uses for:** Populate `body_decl` in step 5 (after line 372). Compute it from the already-fetched arrays + obliquity, e.g.:
```
eps_b = true_obliquity(jd_b)                      # shape S, array-safe (Anchor 2)
x, y, z = spherical_to_rectangular(body_lons, body_lats, 1.0)
xe, ye, ze = ecliptic_to_equatorial(x, y, z, eps_b[..., None])  # broadcast ε over the (14,) body axis
_, decl, _ = rectangular_to_spherical(xe, ye, ze)
out["body_decl"] = decl
```
`out = np.empty(...)` (line 361) means the field is UNINITIALIZED until assigned — the planner MUST assign it or it is garbage. (One verification step: assert `out["body_decl"]` matches the standalone `declination()` for a sample body.)

### Anchor 8 — Downstream consumers of CHART (the DECL-07 crux)
- **Returns** (`ketu/returns/solar.py:22, ~208` and `lunar.py`): call `compute_chart` directly and return its output. ⇒ **`body_decl` inherited for free, zero work.**
- **Synastry** (`ketu/synastry/api.py:98–102`): reads `chart["body_lons"]`, `chart["body_speeds"]` **by name**; emits its own grid dtype (`body_a/body_b/orb/...`), NOT a CHART_DTYPE. ⇒ **does not carry `body_decl`; no action needed** (declination aspects are out of scope).
- **Composite** (`ketu/composite/api.py:221`): `out = np.zeros((), dtype=CHART_DTYPE)` then copies fields **by name** (`out["body_lons"] = ...` line 235, `out["body_lats"] = (a+b)/2` line 238). ⇒ **`body_decl` is NOT named, so it stays `0.0` (zeros, not garbage)** — semantically wrong (a composite of two charts should have a meaningful declination, or an explicitly-documented "not computed" value).

**Planner DECISION (must make explicit):** for composite, either (a) compute `out["body_decl"]` as the declination derived from the composite `body_lons`/`body_lats` (consistent, recommended), or (b) midpoint of the two parents' `body_decl`, or (c) leave `0.0` with a documented caveat. **Recommendation: (a)** — derive from composite λ,β via the same chain, mirroring how composite already derives nothing-by-position. This keeps composite self-consistent and avoids a silent `0.0` trap. Verify all chart fields are read by-name (they are, per grep) so an appended field is safe.

### Anchor 9 — Public API export surface
- `ketu/calculations.py:508` — `__all__` lists `is_ascending`, `lat_velocity`, etc. **The four new functions (`declination`, `declination_velocity`, `is_ascending_declination`, `is_out_of_bounds`) must be added here.**
- `ketu/__init__.py:70` — top-level `__all__` does **NOT** re-export calculations functions (only core/houses symbols). So the public import path is `from ketu.calculations import declination` — matching the existing convention documented in `docs/source/api.md:3` ("All public functions use submodule import paths").

**Planner uses for:** Add 4 names to `ketu/calculations.py:__all__` only. Do NOT add to `ketu/__init__.py` (would break the documented convention; `is_ascending`/`lat_velocity` are themselves not top-level-exported).

### Anchor 10 — Docs structure (DECL-09 concrete targets)
- **EN source:** `docs/source/*.md` (MyST/Sphinx). Targets: `docs/source/api.md` (Calculations section starts line 21; `is_retrograde` documented at line 91 — add the 4 functions in the same style), `docs/source/concepts.md` (ecliptic-latitude concept at line 16 — add the δ / montant-descendant / OOB / β-vs-δ framing here), and `docs/source/changelog.md`.
- **FR translations:** `docs/locale/fr/LC_MESSAGES/*.po` (+ compiled `.mo`). `api.po` and `concepts.po` are the targets. Workflow: edit EN .md → `make gettext`/`sphinx-intl update` regenerates `.po` msgids → translate new msgstr → recompile `.mo`. (MEMORY note `project_fr_translations_before_release`: FR must be translated AND recompiled BEFORE the v1.5 PyPI release, not left English-fallback.)
- Docs Makefile: `docs/Makefile`, `docs/migrate_translations.py` exist for the i18n flow.

**Planner uses for:** DECL-09 deliverables — EN prose in `api.md` + `concepts.md`, FR in the matching `.po`, changelog entry. Framing must be aspect-centric (montant/descendant = Moon's own δ trajectory, draconic month ~27.21 d, OOB nodal cycle, explicit β-vs-δ distinction) — text reusable from brief §2/§3.

### Anchor 11 — Test layout
- δ/velocity unit tests belong in `tests/test_ketu.py` (where `is_ascending` is tested — `test_is_ascending` at line 335, imports at line 124) OR a new `tests/test_declination.py` mirroring it. The package uses a flat `tests/test_*.py` for calculations-level functions plus per-subpackage dirs (`tests/charts/`, `tests/composite/`, `tests/returns/`).
- Coordinate-chain equivalence test (DECL-03): mirror `tests/test_coordinates_coverage.py`.
- Chart-field + ratchet tests: `tests/charts/test_dtype.py` (Anchor 8 below). Composite propagation: `tests/composite/`. Returns inheritance: `tests/returns/`.

**Planner uses for:** placement of DECL-01..06 tests (calculations-level), DECL-03 equivalence (coordinates-level), DECL-07 propagation (charts/composite/returns), DECL-08 ratchet (charts/test_dtype.py).

### Anchor 8b — The dtype ratchet pattern to extend
`tests/charts/test_dtype.py`
- `test_dtype_has_expected_field_names()` — line 44: asserts `CHART_DTYPE.names == expected` (a hardcoded tuple incl. `body_lons, body_lats, body_speeds, ...`). **Add `"body_decl"` to the expected tuple.**
- field-shape tests — lines 60–65 (`("body_lats", (14,))` list) and 88–90 (kind/itemsize `("body_lats","f",8)`). **Add `("body_decl",(14,))` and `("body_decl","f",8)`.**
- subarray-shape tests — lines 118–136 (`arr["body_lats"].shape == (5,14)` and 0-d `(14,)`). **Add `body_decl` assertions.**
- `test_body_count_frozen_at_fourteen()` — line 218: the prior 13→14 ratchet (`_BODY_COUNT == 14`). This stays at 14 (body COUNT unchanged); the new ratchet is the FIELD-LIST one above. The docstring style (explaining the migration + "go red until reviewer confirms") is the template for documenting the additive `body_decl` bump.

**Planner uses for:** DECL-08 — extend the existing field-name/shape/itemsize assertions to include `body_decl`; add a docstring noting the v1.5 additive dtype-version bump (parallel to the v1.3 13→14 note) and that Kala's positional indexing impact is documented (Pitfall 3), not fixed here.

### Anchor 12 — Quality gates (BLOCKING — budget for these)
`pyproject.toml` + `Makefile`:
- **coverage** `fail_under = 100` (line 110) — every new line/branch needs a test. `exclude_lines` (111–130) lists allowed pragmas; new defensive branches need either a test or justification.
- **interrogate** `fail-under = 95`, `style = "sphinx"` (line 132–146) — all 4 functions + new dtype field doc need docstrings.
- **numpydoc** `checks = ["all", -EX01, -SA01, -ES01]` (line 148) — strict numpydoc on public functions (Parameters/Returns/etc. required; Examples optional). `make doc-gates`.
- **doctest** `make doctest` runs `--doctest-modules ketu/` with ELLIPSIS+NORMALIZE_WHITESPACE (line 87–90) — any `>>>` example in the new docstrings MUST execute correctly. Mirror the `lat`/`is_ascending` docstring example style (they have runnable `>>>` blocks).
- **mypy** `--strict` (line 166) BUT `ketu.calculations` is in the relaxed override (line 176–186, disables `no-untyped-def`, `arg-type`, `return-value`, etc.). So the misleading `true_obliquity` type hint (Anchor 2) is unlikely to fail mypy in calculations.py. `ketu.charts.*` is NOT in the relaxed list — chart wiring must be strictly typed.

---

## Common Pitfalls

### Pitfall 1: `is_ascending` (β) vs `is_ascending_declination` (δ) confusion
**What goes wrong:** A caller (or a future doc reader) assumes "ascending Moon" means the same thing in both. They are DIFFERENT physical quantities (ecliptic-latitude rise vs declination rise) that flip on different days.
**Why it happens:** Near-identical names; both are "ascending" Moon concepts in biodynamics.
**How to avoid:** Confirmed from source they are independent (`is_ascending` reads `lat_velocity` = β-speed; `is_ascending_declination` reads `declination_velocity` = δ-speed). Keep both in `__all__`; document the distinction explicitly in `concepts.md` (DECL-09 requires this). NEVER modify `is_ascending`.
**Warning sign:** any code path or doc that treats `is_ascending` as "the biodynamic ascending Moon" — that is the δ-trajectory's job now.

### Pitfall 2: Vectorization — a Python loop sneaking into the hot path (DECL-02)
**What goes wrong:** Implementing `declination` over an array by looping `body_properties` per date.
**Why it happens:** Scalar `body_properties` is the obvious building block but is LRU-cached/scalar.
**How to avoid:** VERIFIED the coordinate chain + `mean/true_obliquity` are array-safe end-to-end (`max|Δ| = 7.1e-15` vectorized). For array `jdate`, use the chain directly on arrays. For the chart hot path, reuse `compute_chart`'s already-vectorized `body_lons`/`body_lats` (Anchor 7) — no extra position fetch, no S-loop. The only acceptable loop is the existing 14-body loop in `_vectorised_body_properties` (constant in S).
**Warning sign:** `np.array([declination(jd, b) for jd in jds])` — forbidden in the hot path.

### Pitfall 3: `body_decl` dtype bump — is an appended field safe? (DECL-07/08 crux)
**What goes wrong:** Appending a CHART_DTYPE field shifts byte offsets; a consumer reading by byte-offset / `.view()` / positional `np.void` index would break.
**Why it happens:** STATE.md/MEMORY call CHART_DTYPE "frozen"; Kala indexes the body AXIS positionally.
**How to avoid:** VERIFIED via grep that ALL internal consumers (synastry, composite, returns) read chart fields **by NAME** (`chart["body_lons"]`, etc.), never by byte-offset or `.view()`. So an appended field is **safe inside ketu**. The body-axis positional contract (Kala) is about the `(14,)` index order, which is UNCHANGED (still 14 bodies). The ONLY external risk is a downstream consumer that does `chart.view(some_other_dtype)` or relies on `CHART_DTYPE.itemsize` — **the planner should document the additive bump for Kala (per DECL-08) and NOT attempt to fix Kala here.** Recommend the planner add a one-line caveat in the migration doc + changelog.
**Warning sign:** any `.view(`, `.itemsize`, or positional structured-array indexing in a consumer (none found in ketu).

### Pitfall 4: Composite silently zero-fills `body_decl`
**What goes wrong:** Composite allocates `np.zeros((), CHART_DTYPE)` and copies by name; `body_decl` is never assigned → it is `0.0` everywhere, looking valid but meaning "declination = 0" (on the equator) for every body.
**Why it happens:** `np.zeros` (not `np.empty`) hides the omission — no NaN, no crash.
**How to avoid:** Planner MUST explicitly populate `out["body_decl"]` in `composite/api.py` (recommendation: derive from the composite `body_lons`/`body_lats` via the chain). Add a composite test asserting `body_decl != 0` for an off-equator body.
**Warning sign:** a composite test that passes while `comp["body_decl"]` is all zeros.

### Pitfall 5: `np.empty` in `compute_chart` leaves `body_decl` as garbage until assigned
**What goes wrong:** `compute_chart` uses `np.empty(leading_shape, CHART_DTYPE)` (line 361). A new field not assigned in the step-5 block is uninitialized memory (NOT zero) → flaky, non-deterministic tests.
**How to avoid:** Assign `out["body_decl"] = decl` alongside `out["body_lats"]` (after line 372). Verify with a test comparing chart `body_decl` to standalone `declination()`.
**Warning sign:** intermittently-passing chart tests; non-reproducible `body_decl` values.

### Pitfall 6: true vs mean obliquity — honoring STATE.md over the brief
**What goes wrong:** The brief (D1/D2) recommends `mean_obliquity` for internal consistency. Following the brief would CONTRADICT STATE.md's locked `true_obliquity` decision.
**Why it happens:** Two HIGH-quality sources disagree (brief recommendation vs phase decision).
**How to avoid:** STATE.md wins — use `true_obliquity(jd)` for both `declination` (the chain's ε) and OOB threshold. Difference is sub-arcminute (≤~9″), below the Moon's ±0.01° ephemeris precision, so either is defensible; the LOCK is `true_obliquity`. The misleading `jd: float` type hint is not a blocker (Anchor 2 + 12).
**Warning sign:** a PR using `mean_obliquity` for δ "for consistency" — that's the brief's rec, not the phase's.

### Pitfall 7: Doc gates are BLOCKING (Anchor 12)
**What goes wrong:** A function ships without a numpydoc-clean docstring / runnable doctest / 100% line coverage → CI red.
**How to avoid:** Mirror `lat`/`is_ascending` docstrings exactly (they have Parameters/Returns/Examples with runnable `>>>`). Every branch tested (incl. the `arcsin`/sign paths). Update the CHART_DTYPE `#:` doc block (Anchor 6) so interrogate/numpydoc see the new field.
**Warning sign:** missing `Returns` section, `>>>` example that doesn't match `NORMALIZE_WHITESPACE` output, an untested branch.

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Ecliptic→equatorial δ | New trig from Meeus 13.4 | `coordinates.py` chain (Anchor 1) | STATE.md mandates reuse; VERIFIED Δ=0 vs Meeus; already tested |
| Obliquity ε(jd) | New IAU formula | `true_obliquity(jd)` (Anchor 2) | Exists, array-safe, nutation-corrected |
| δ velocity | New ODE / analytic derivative | Forward finite difference, step 0.01 (Anchor 3) | Mirrors `lat_velocity`; brief §4 says analytic "not worth it" |
| Position fetch in chart hot path | Re-call `calc_planet_position_batch` for δ | Reuse `compute_chart`'s `body_lons`/`body_lats` (Anchor 7) | Avoids double fetch + keeps it vectorized |
| Returns δ propagation | Manually copy `body_decl` | Nothing — Returns call `compute_chart` (Anchor 8) | Inherited for free |
| dtype ratchet | New test scaffold | Extend `tests/charts/test_dtype.py` (Anchor 8b) | Established pattern from the 13→14 ratchet |

**Key insight:** This phase introduces ZERO new astronomy and ZERO new dependencies (pure-NumPy contract holds; pyswisseph stays test/build-only). It is composition over existing, tested primitives.

---

## Suggested Implementation Sequence (NOT plans — the planner authors these)

A natural dependency order; the planner decides plan boundaries:

1. **Core functions** in `ketu/calculations.py` (DECL-01,02,04,05,06):
   `declination` (chain reuse) → `declination_velocity` (FD, step 0.01) → `is_ascending_declination` (mirror `is_ascending`) → `is_out_of_bounds` (`|δ| > true_obliquity(jd)`). Add all 4 to `__all__` (Anchor 9). Mirror docstring style of `lat`/`is_ascending` (doc gates).
2. **Equivalence regression test** (DECL-03): direct Meeus 13.4 == coordinates chain == `declination()`, machine precision. Place near `tests/test_coordinates_coverage.py` / `tests/test_ketu.py`.
3. **Unit + vectorization tests** (DECL-01,02,04,05,06) — scalar + array paths; OOB true/false cases; Moon montant/descendant sign; all 14 bodies incl. Chiron.
4. **dtype field** `("body_decl","f8",(14,))` in `CHART_DTYPE` (Anchor 6) + update the `#:` doc block.
5. **Chart wiring** in `compute_chart` (Anchor 7) — populate `out["body_decl"]` from existing arrays + `true_obliquity(jd_b)`; verify vs standalone `declination()`.
6. **Ratchet test** (DECL-08) — extend `tests/charts/test_dtype.py` field-name/shape/itemsize assertions; docstring notes the additive v1.5 bump + Kala-impact-documented-not-fixed.
7. **Downstream propagation** (DECL-07): Returns (verify inherited, add a test), Composite (DECIDE + populate `body_decl`, add test — Pitfall 4), Synastry (confirm no-op).
8. **Docs en + fr** (DECL-09): `api.md` (4 functions) + `concepts.md` (montant/descendant/OOB/β-vs-δ framing, draconic 27.21 d) + changelog; FR `.po` for `api`/`concepts` translated AND recompiled.
9. **Gate sweep:** `make test` (100% cov) + `make doctest` + `make doc-gates` + `make mypy` green.

---

## Open Questions

1. **Composite `body_decl` semantics** — derive from composite λ,β (recommended), midpoint of parents' δ, or documented `0.0`? *Recommendation: derive via the chain for self-consistency (Pitfall 4). Planner/UAT confirms.*
2. **Does Kala (`.view()` or positional CHART byte-offset read) break on the appended field?** No internal ketu consumer does; Kala is external. *Recommendation: document the additive bump (DECL-08), do NOT fix Kala here (MEMORY: Kala adapts post-milestone).* LOW confidence on Kala internals (not in this repo) — planner should flag for the Kala owner, not block.
3. **Should `body_decl_speeds` also be added to CHART_DTYPE?** The brief §5 D6 raised it as optional. Phase requirements (DECL-07) only mandate `body_decl`. *Recommendation: NO — out of the stated requirements; montant/descendant is exposed via the standalone `is_ascending_declination`, not a chart field. Adding it would be scope creep.*

---

## Sources

### Primary (HIGH confidence)
- `.planning/research/DECLINATION.md` — the project-level astronomy brief (Meeus 13.4, periods, OOB, velocity method). Reused, not re-derived.
- Ketu source, read 2026-06-03: `ketu/ephemeris/coordinates.py` (chain + obliquity), `ketu/calculations.py` (`long`/`lat`/`lat_velocity`/`is_ascending`/`__all__`), `ketu/charts/core.py` (CHART_DTYPE), `ketu/charts/api.py` (`compute_chart`/`_vectorised_body_properties`), `ketu/composite/api.py`, `ketu/synastry/api.py`, `ketu/returns/solar.py`+`lunar.py`, `ketu/ephemeris/planets.py` (`calc_planet_position_batch`, FD idiom), `tests/charts/test_dtype.py` (ratchets), `pyproject.toml`+`Makefile`+`docs/` (gates + doc targets).
- Live numerical re-verification (this research): chain vs Meeus 13.4 vectorized `max|Δ| = 7.1e-15`; `true_obliquity(array)` returns an array; vectorized OOB works.

### Secondary (MEDIUM confidence)
- Brief's §3 OOB astrological-meaning sources (Lunarium/Augurine/Evolving Door) — domain convention, already MEDIUM in the brief.

### Tertiary / unresolved (flagged)
- Kala-internal CHART consumption (external repo, not inspected) — Open Question 2.

---

## Metadata

**Confidence breakdown:**
- Code anchors (signatures, insertion points): HIGH — every one read from current source.
- Vectorization / `true_obliquity` array-safety: HIGH — verified at runtime against the live package.
- Downstream propagation (Returns free / Synastry n/a / Composite zero-fill): HIGH — grep + source confirmed.
- Kala external impact: LOW — external repo not in scope; flagged for documentation only.
- Astronomy (reused from brief): HIGH — brief verified numerically; re-confirmed here.

**Research date:** 2026-06-03
**Valid until:** ~30 days (stable internal codebase; no fast-moving external deps).
