# Phase 14: Chart Abstraction Foundation - Context

**Gathered:** 2026-05-08
**Status:** Ready for planning

<domain>
## Phase Boundary

A new `ketu/charts/` subpackage that publishes a single primitive — `compute_chart(jd, lat, lon, system, aspects, polar_fallback)` — returning a fully-resolved `CHART_DTYPE` structured array combining body positions + ASC/MC/ARMC/Vertex + cusps + intra-chart aspects in one vectorisable call. Plus an `is_day_chart(jd, lat, lon)` helper required by Arabic Parts (Phase 19). Keystone upstream of Synastry (16), Composite (17), Solar Return (18), and Parts (19).

**In scope:**
- `ketu/charts/` subpackage (`__init__.py`, `core.py`, `api.py`) following the v1.1 `ketu/houses/` shape.
- `CHART_DTYPE` defined in `ketu/charts/core.py` — frozen, named, fully shape-documented in the module docstring with a "Why structured array" rationale block.
- `compute_chart(jd, lat, lon, system="placidus", aspects=None, polar_fallback="raise") → CHART_DTYPE` in `ketu/charts/api.py`, vectorised over broadcast `(jd, lat, lon)` of any compatible shape.
- `is_day_chart(jd, lat, lon) → bool` (or vector of bool) helper, vectorisable, sunrise-inclusive, polar-safe via internal Porphyry fallback.
- Coverage ≥95 % on `ketu/charts/` (mirrors v1.1 houses gate); `numpydoc validate` clean; `interrogate ≥95%` clean.

**Out of scope:**
- Synastry (Phase 16), Composite (Phase 17), Solar Return (Phase 18), Parts (Phase 19) — they CONSUME `CHART_DTYPE`; their plans land later.
- New house systems Whole Sign / Equal / Regiomontanus (Phase 15) — independent of CHART; parallelizable.
- Chiron / additional bodies — deferred to v1.3 (changing the `(13,)` body axis is a v1.3 BREAKING acknowledged here).
- `is_day_chart(chart)` overload that takes a CHART_DTYPE row — Phase 14 ships only the `(jd, lat, lon)` form (the form Parts needs); overload deferred unless surfaced.
- Storing `is_day` inside CHART_DTYPE — explicitly rejected (D-12 below).

</domain>

<decisions>
## Implementation Decisions

### CHART_DTYPE shape (positions + houses + aspects + metadata)

- **D-01:** **Positions layout** — three subarray fields mirror `HOUSES_DTYPE.cusps (12,)` precedent: `body_lons (f8, (13,))`, `body_lats (f8, (13,))`, `body_speeds (f8, (13,))`. Indexation positionnelle stable par body ID (Kala-friendly). The `(13,)` axis follows the canonical `ketu.core.bodies` order (Sun=0..Lilith=12). No nested per-body sub-dtype (rejected: adds maintenance surface for no batch-friendliness gain).
- **D-02:** **Position granularity** — lon + lat + speed only. `dist` excluded (rarely needed in astrology outside declination); `is_retrograde` derivable as `body_speeds < 0` by the caller (no separate retro field). Speed in degrees/day.
- **D-03:** **Houses layout** — replicate the HOUSES_DTYPE fields **inline** in CHART_DTYPE: `cusps (f8, (12,))`, `asc (f8)`, `mc (f8)`, `armc (f8)`, `vertex (f8)`. NOT a nested `houses (HOUSES_DTYPE,)` field (rejected: adds an indirection level that hurts ML interop; the values are scalars/short subarrays anyway).
- **D-04:** **Metadata** — `jd (f8)`, `lat (f8)`, `lon (f8)`, `system (U10)` stored inline. Self-describing chart (mirror HOUSES_DTYPE). Synastry / composite / return need this context preserved on every chart they consume.
- **D-05:** **Aspects layout** — dense matrix of canonical aspect indices: `aspect_matrix (i1, (13, 13))` and `aspect_orbs (f4, (13, 13))`. Upper-triangle is computed; lower-triangle mirrors (i,j → j,i) for symmetric lookup convenience. Diagonal = `-1` / `NaN` (a body has no aspect with itself). Cost: 13×13×(1+4) = 845 bytes per chart — negligible vs ML batchability.
- **D-06:** **Aspect "no-aspect" sentinels** — `aspect_matrix[i,j] == -1` (i1 supports negatives; canonical i_asp ∈ [0,13] so -1 is unambiguous). `aspect_orbs[i,j] == NaN` (f4 supports NaN; idiomatic NumPy "absent"). Caller mask: `chart["aspect_matrix"] >= 0` or `~np.isnan(chart["aspect_orbs"])`.
- **D-07:** **Default aspect set** — `aspects=None` resolves to `CLASSICAL` (5 majors), aligned with the Phase 9 default. One canonical "default aspect set" across the package — no Phase-14-specific divergence.

### compute_chart signature

- **D-08:** **Body list is FROZEN at 13** — no `bodies=` parameter. The `(13,)` axis is part of the CHART_DTYPE contract; varying it would require variable-shape `aspect_matrix (N,N)` and break Kala's positional indexing. Adding Chiron in v1.3 will grow the axis to 14 and is an acknowledged BREAKING for v1.3.
- **D-09:** **Vectorisation** — broadcasts `(jd, lat, lon)` to a common leading shape S (mirror `calculate_houses`). Returns CHART_DTYPE with that leading shape. No Python loop in the hot path (success criterion 14.2).
- **D-10:** **AspectSetSpec contract** — `aspects: AspectSetSpec = None` accepts the same spec as `calculate_aspects_vectorized` (preset name, list of names/indices, length-14 boolean mask). Re-uses `resolve_aspect_set`. One AspectSetSpec contract across the project.
- **D-11:** **Polar handling** — `polar_fallback: Literal["raise", "porphyry"] = "raise"` is pass-through to `calculate_houses` internal. Same contract as v1.1 houses; "one call" stays unified for polar callers (especially relocated solar returns in Phase 18).

### is_day_chart helper

- **D-12:** **Standalone helper, NOT stored in CHART_DTYPE** — `is_day_chart(jd, lat, lon)` is the canonical sect entry point. Phase 14 ships only the `(jd, lat, lon)` form; an overload taking a CHART_DTYPE row is deferred (Phase 19 PARTS will call the standalone form internally — equally cheap). Storing `is_day` inside the chart would create a double source-of-truth that drifts if anyone post-edits `body_lons[0]` (Sun) or `asc`.
- **D-13:** **Sect convention** — sunrise-inclusive: `Sun >= ASC = day` (Hellenistic standard, matches Solar Fire / Astro.com / Robert Hand). Equality at the horizon resolves to **day**. Documented loudly in the docstring.
- **D-14:** **Geometric definition** — "Sun above horizon" = Sun longitude is in houses 7–12 of the natal cusps (above-horizon hemisphere). Re-uses `house_of(sun_lon, cusps)`; vectorised by composition. Avoids declination math (no need for it in v1.2).
- **D-15:** **Polar safety** — `is_day_chart` computes its own ASC + cusps internally with `polar_fallback="porphyry"` so high-latitude Parts calls don't fail silently or raise. Porphyry is mathematically defined at every latitude. Documented as the rationale in the docstring.

### Aspects intra-chart implementation

- **D-16:** **Re-use existing `calculate_aspects_vectorized`** rather than reimplement — one source-of-truth for orb math + AspectSetSpec resolution. Phase 14 wraps it: call once per leading-shape element, project the returned (body1, body2, i_asp, orb) records into the (13,13) dense matrix. If `jd` is array-shaped (S,), the wrapper loops over S in Python — acceptable for v1.2 (`compute_chart` is not a hot-path tightloop; ML callers batch S to ~100s, not 100k+). A pure-vectorised reimplementation can land in v1.3 if profiling motivates.
- **D-17:** **Symmetric mirror** — after computing the upper-triangle matches, the wrapper reflects them to the lower-triangle (`aspect_matrix[j,i] = aspect_matrix[i,j]`). Both lookup orders work without caller ceremony.

### Claude's Discretion

- Internal sub-module split inside `ketu/charts/` (e.g. whether `is_day_chart` lives in `api.py`, `sect.py`, or `core.py`) — planner decides; the v1.1 houses split (`core.py` for dtype, `api.py` for public funcs, internal modules for math) is the recommended template.
- Whether the aspect-matrix builder is a private helper (`_build_aspect_matrix`) inside `api.py` or its own module — planner decides.
- Exact `[tool.coverage.run]` exclusion (if any) for `ketu/charts/` — likely none needed (new module written cleanly to ≥95%).
- Whether to expose `house_of` re-export from `ketu/charts` for ergonomics or rely on `from ketu.houses import house_of` — minor; planner picks.
- Test fixture choices and oracle reference charts — researcher/planner pick from the existing `tests/houses/conftest.py` + swisseph oracle pattern.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` § "Phase 14: Chart Abstraction Foundation" — goal, depends-on, success criteria 1–5.
- `.planning/REQUIREMENTS.md` § CHART-01..05 — the five locked requirements (subpackage, dtype, compute_chart, is_day_chart, ≥95% coverage).
- `.planning/PROJECT.md` § "Chart abstraction (Option A)" — the locked Option-A choice: structured array, not dataclass, not flat.
- `.planning/STATE.md` § "v1.2 roadmap structure" — Phase 14 as the keystone; SYN/COMP/RET/PARTS depend on its dtype.

### v1.2 framing constraints (apply to every phase, including this one)
- `.planning/ROADMAP.md` § "Cross-Cutting Constraints (v1.2)" — non-breaking minor strict, pure-NumPy, Python 3.10+, mypy --strict, ≥95% on new modules, doc gates from Phase 13 onward.
- `CLAUDE.md` § "Règles importantes" — no runtime dep additions; venv = `venv/`; NumPy structured arrays for ML interop.

### Pre-resolved architecture decisions (input to Phase 14)
- `.planning/research/v1.2-OPEN_QUESTIONS.md` § Q1 — Option A (CHART_DTYPE) chosen over dataclass / flat. Settled.
- `.planning/research/v1.2-OPEN_QUESTIONS.md` § AR-Q1, AR-Q2 — `ketu/charts/` subpackage location confirmed.
- `.planning/research/v1.2-OPEN_QUESTIONS.md` § PR-Q3 — sunrise-inclusive sect convention confirmed.
- `.planning/research/v1.2-SCOPE.md` § "Cross-cutting design challenge: the Chart abstraction" — original framing of the architectural question.

### Phase 13 doc gates (apply to ketu/charts/)
- `.planning/phases/13-doc-gates-and-ci-foundation/13-CONTEXT.md` § "numpydoc validate posture" + "interrogate scope" — `ketu/charts/` is in-scope for both gates from day one.
- `pyproject.toml` § `[tool.interrogate]`, `[tool.numpydoc_validation]` — config to satisfy.

### Existing patterns to mirror
- `ketu/houses/core.py` — `HOUSES_DTYPE` is the canonical structured-array precedent. Subarray field shape `cusps (f8, (12,))`, `HighLatitudeError(ValueError)` pattern.
- `ketu/houses/api.py` — `calculate_houses` broadcast pattern (`np.broadcast_arrays`, leading shape S). Direct template for `compute_chart`.
- `ketu/houses/__init__.py` — public re-export pattern (`__all__` + module docstring with usage examples).
- `ketu/houses/ascmc.py` — `compute_ascmc(jd, lat, lon)` returns ASC/MC/ARMC/Vertex/eps; `compute_chart` calls it via `calculate_houses` (already does internally).
- `ketu/aspects/calculator.py` — `calculate_aspects_vectorized(jdate, l_bodies, aspects)` returns the structured pair-record array that `compute_chart` projects into `aspect_matrix`.
- `ketu/aspects/presets.py` — `resolve_aspect_set(AspectSetSpec)` and `AspectSetSpec` type alias; `compute_chart`'s `aspects=` param goes through it unchanged.
- `ketu/cycles/calculator.py` § `CYCLE_DTYPE` — alternative structured-array precedent (flat, time-series-oriented). Useful contrast to confirm CHART is per-instant + subarray-heavy, not per-row.
- `ketu/calculations.py` — `positions(jdate, l_bodies)` for body lons; `body_properties(jdate, body)` returns lat/speed/dist already (re-use in batch).

### Test patterns to mirror
- `tests/houses/conftest.py` — swisseph oracle pattern (test-only AGPL boundary). New `tests/charts/conftest.py` follows the same shape.
- `tests/houses/test_calculate_houses.py` — broadcast / vectorisation testing pattern.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`calculate_houses`** (`ketu/houses/api.py`): `compute_chart` calls it directly with `(jd, lat, lon, system, polar_fallback)` to obtain the houses portion of CHART_DTYPE. No re-derivation of ASC/MC/cusps math. Single round-trip.
- **`positions`** + **`body_properties`** (`ketu/calculations.py`): per-body lon / lat / speed lookups. Composable for the `body_lons`, `body_lats`, `body_speeds` subarrays. Today scalar-jd; Phase 14 adds the broadcast wrapper.
- **`calculate_aspects_vectorized`** (`ketu/aspects/calculator.py`): emits canonical `(body1_id, body2_id, i_asp, orb)` records. `compute_chart` projects these into the dense (13,13) matrix; reuses `resolve_aspect_set` indirectly.
- **`resolve_aspect_set` + `AspectSetSpec`** (`ketu/aspects/presets.py`): single source-of-truth for aspect-set resolution. `compute_chart(aspects=...)` is a pass-through.
- **`house_of`** (`ketu/houses/api.py`): vectorised body-to-house mapping. `is_day_chart` calls it on the Sun longitude to decide above/below horizon.
- **`HOUSES_DTYPE` shape** (`ketu/houses/core.py`): direct precedent for the houses sub-block in CHART_DTYPE (D-03 inlines those fields).

### Established Patterns
- **Subpackage layout**: v1.1 settled on `core.py` (dtypes + exceptions), `api.py` (public functions), per-system math modules. `ketu/charts/` mirrors: `core.py` (CHART_DTYPE), `api.py` (compute_chart, is_day_chart). Plan whether `is_day_chart` lives in `api.py` or a `sect.py` sibling — both work.
- **`np.broadcast_arrays(jd, lat, lon)` then build structured output of leading shape S** — established in `calculate_houses` and the canonical broadcast template for Phase 14.
- **Subarray fields for fixed-length axes** (`cusps (f8, (12,))` in HOUSES). CHART_DTYPE follows: `body_lons (f8, (13,))`, `aspect_matrix (i1, (13,13))`. NumPy-first; Kala consumes via positional indexing.
- **Per-module mypy / coverage / numpydoc overrides via pyproject** — keep defaults; only override if a specific gap surfaces. Don't pre-emptively add carve-outs.
- **AGPL non-contamination** — `pysweph` lives only in `tests/`. `ketu/charts/` runtime imports must not pull it in. Tests for the chart module use the existing test-only swisseph oracle.

### Integration Points
- **New subpackage `ketu/charts/`** with `__init__.py` re-exporting `CHART_DTYPE`, `compute_chart`, `is_day_chart`. Top-level `ketu/__init__.py` does **not** re-export these in v1.2 (additive — callers `from ketu.charts import ...` per the success criterion 14.1 wording); revisit in v1.3 if convention shifts.
- **No edits to `ketu/houses/`, `ketu/aspects/`, `ketu/calculations.py`** — Phase 14 is composition only. If a tiny helper is missing (e.g. a vectorised `positions(jd_array, ...)`), surface it during planning; the bias is "wrap externally, do not edit upstream modules in this phase".
- **`pyproject.toml`** — no new entries required (`ketu/charts/` is auto-discovered by the existing setuptools find-packages config). Doc-gate configs are global; they pick up the new module automatically.
- **`tests/charts/`** — new test directory mirroring `tests/houses/` (conftest with swisseph oracle, per-feature test files, 10-reference-charts oracle pattern).

</code_context>

<specifics>
## Specific Ideas

- The CHART_DTYPE module docstring MUST include a **"Why structured array"** section pointing to the ML-interop / Kala positional-contract rationale (success criterion 14.5). Sophie's voice: explain, don't apologise.
- `is_day_chart`'s docstring MUST loudly call out the polar-safety design choice (Porphyry internal fallback) — high-latitude users will read this and need to trust it.
- `compute_chart`'s docstring MUST include a vectorised example (`jd_array, lat_array, lon_array → CHART_DTYPE shape (S,)`), mirroring `calculate_houses`'s docstring example, so success criterion 14.2 is visible at the API surface.
- The aspect-matrix sentinel convention (`-1` for "no aspect", `NaN` for "no orb") MUST be documented in the CHART_DTYPE module docstring with the canonical caller mask one-liner (`chart["aspect_matrix"] >= 0`).
- Test fixtures: re-use the 10-reference-charts oracle from `tests/houses/` for the houses portion of CHART_DTYPE; add 2–3 hand-validated full-chart fixtures (with intra-chart aspects) for the aspect_matrix portion. Hand-validation source: the existing v1.1 reference-charts pinned values.

</specifics>

<deferred>
## Deferred Ideas

- **`is_day_chart(chart)` overload** — accepts a CHART_DTYPE row and reads sun_lon + cusps from it. Equally cheap but adds API surface; PARTS (Phase 19) doesn't strictly need it (it can call the `(jd, lat, lon)` form). Surface only if PARTS implementation reveals friction.
- **Chiron / additional bodies in CHART_DTYPE** — grows the `(13,)` axis to `(14,)` and is an acknowledged BREAKING for v1.3. Out of v1.2 scope (PROJECT.md § "Explicitly DEFERRED to v1.3").
- **Pure-vectorised aspect-matrix computation** (no Python loop over leading shape S) — D-16 chooses re-use over reimplementation. Profile in Phase 16 (synastry batches charts) and revisit in v1.3 if the loop dominates.
- **`compute_chart_aspects(chart, aspects=...)` standalone helper** — re-derive aspects from a stored chart with a different aspect set than the one originally computed. Useful but not required by ROADMAP. v1.3 candidate.
- **Storing `is_retrograde` as a bool subarray** — derivable as `body_speeds < 0`; ergonomic helper `chart_is_retrograde(chart)` could land later.
- **Top-level `from ketu import compute_chart, CHART_DTYPE` re-export** — convenience; revisit in v1.3 once the API stabilises across SYN/COMP/RET/PARTS.
- **Per-body `dist` field in CHART_DTYPE** — rejected for v1.2 (D-02). If declination-based aspects (parallels / contre-parallels) surface as a feature, the dtype evolves with that phase.

</deferred>

---

*Phase: 14-chart-abstraction-foundation*
*Context gathered: 2026-05-08*
