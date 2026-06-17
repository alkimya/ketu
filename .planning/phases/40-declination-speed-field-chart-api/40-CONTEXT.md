# Phase 40: Declination Speed Field & Chart API - Context

**Gathered:** 2026-06-17
**Status:** Ready for planning

<domain>
## Phase Boundary

`CHART_DTYPE` carries `body_decl_speed` (dδ/dt, deg/day) for all 14 bodies,
inherited across the full chart family (synastry / composite / returns), with a
public standstill threshold (`DECL_STANDSTILL_EPS`) defined IN Ketu and a
chart-level ascending-declination helper that Rahu can consume without computing
any astronomy.

**The scalar math already exists.** `ketu==1.6.0` ships
`declination_velocity(jd, body)` and `is_ascending_declination(jd, body)` in
`ketu.calculations` (delivered in v1.5, finite-difference step 0.01 d). This
phase **exposes the field in `CHART_DTYPE`** and adds the chart-level surface; it
does NOT reinvent the math.

**Boundary (non-negotiable):** Rahu computes no astronomy. The standstill
threshold lives in Ketu as a public contract so Rahu invents none. All display
decisions (raw value vs ↗/↘ sense, visual language) are Rahu's and live OUTSIDE
this engine.

**Requirements are pre-locked by `.planning/REQUIREMENTS.md` (DSPD-01..06).**
Downstream agents MUST read REQUIREMENTS.md — this CONTEXT.md only resolves the
gray areas the requirements left open.

</domain>

<decisions>
## Implementation Decisions

These decisions resolve the gray areas the requirements (DSPD-01..06) left open.
The requirements themselves remain the binding source for everything else
(field name/type, Δt=0.01 d verbatim, raw deg/day value, ratchet re-pin, MINOR
bump).

### Composite δ-speed derivation (resolves the DSPD-03 trap correctly)
- **D-01:** The composite `body_decl_speed` is computed by **finite difference on
  the composite's OWN frozen λ,β fields advanced by their midpoint velocities** —
  NOT by re-fetching real planetary positions at `jd_composite + 0.01`, and NOT by
  averaging the two parents' `body_decl_speed`.
- **Why:** The composite chart has **no canonical jd** (the code states this
  literally: `ketu/composite/api.py:36,156,321` — "the composite has no canonical
  jd"). `body_decl` (v1.5) worked via a static recompute because δ is a pure
  function of (λ, β). But dδ/dt is a *time-derivative* and needs two time points.
  Two rejected approaches:
  - ❌ **FD on jd_composite via the standard `declination` path** — re-fetches the
    *real* planetary positions at `jd_comp + 0.01` (jd_comp = mean of two birth
    dates, often decades from either parent). This measures the dδ/dt of a real
    body at a near-arbitrary jd, NOT the velocity of the frozen composite point.
    Physically meaningless and inconsistent with the composite's frozen λ,β. The
    user explicitly flagged and rejected this.
  - ❌ **Midpoint of the two parents' `body_decl_speed`** — the exact trap DSPD-03
    forbids (same trap as `body_decl` in v1.5).
- **How:** Advance the composite's frozen `body_lons`/`body_lats` by their stored
  midpoint velocities (`body_speeds` for λ; the dβ/dt midpoint for β) over Δt=0.01 d,
  recompute δ at both frozen points via the same coordinates chain
  (`spherical_to_rectangular → ecliptic_to_equatorial(ε) → rectangular_to_spherical`),
  and take the slope. **Self-consistent with the composite chart, derived from ITS
  OWN fields.** Faithful to the "derived from the composite chart" spirit of DSPD-03.
- **Note for planner:** the composite stores `body_speeds` (λ velocity midpoint)
  but does NOT currently store a β-velocity field. The β advance needs dβ/dt of the
  composite — the researcher/planner must determine how to obtain it (midpoint of
  the parents' β-velocities, or derive it) so the FD has a β-rate. This is the one
  open implementation detail under D-01.

### DECL_STANDSTILL_EPS value (deferred to research)
- **D-02:** The numeric value of `DECL_STANDSTILL_EPS` (deg/day) is **NOT pinned by
  the user** — the researcher/planner determines a justified, tested value.
- **Constraints for the research:** small enough not to mask real slow motion
  (outer planets have small but real dδ/dt), large enough to absorb FD noise near
  real standstills (Moon and Sun turning points at Δt=0.01 d). The Moon's dδ/dt
  reaches ~±5°/day; slow planets far less. The value must be tested and documented
  as a public contract (DSPD-05).

### Chart-level helper output encoding
- **D-03:** The chart-level ascending-declination helper returns a **`np.int8`
  array** with values `{-1, 0, +1}` per body: `+1` ascending (montant), `-1`
  descending (descendant), `0` neutral/standstill. Shape mirrors the body axis:
  `(14,)` for a scalar chart, `S + (14,)` for a vectorised chart.
- **Why:** Vectorised, ML-friendly, consistent with Ketu's structured-array idiom;
  the ↗/↘ sense reads off the sign just like `body_speeds`. Rejected: string array
  (less ML-friendly, heavier than int8, off-convention) and two-boolean-mask form
  (awkward for 3 states, neutral becomes implicit).
- **Classification rule (from DSPD-06):** ascending if
  `body_decl_speed > DECL_STANDSTILL_EPS`, descending if
  `body_decl_speed < −DECL_STANDSTILL_EPS`, neutral otherwise.
- **Distinctness:** this is the chart-level helper, distinct from — and consistent
  with — the v1.5 scalar `is_ascending_declination(jd, body)` (which returns a
  plain bool ↗/not). Naming/signature is the planner's call as long as the two are
  clearly distinguishable and the chart version reads the `body_decl_speed` field.

### Claude's Discretion (deferred to research/planning)
- **API namespace** — where `DECL_STANDSTILL_EPS` and the chart-level helper live
  is left to the **researcher** to settle by checking the real import graph
  (`calculations` ↔ `charts`). DSPD-05 allows "`ketu.calculations` or the
  appropriate public namespace". The known tension: `calculations.py` does NOT
  currently depend on `charts`, so a chart-reading helper placed in `calculations`
  risks an import cycle. The likely-clean split (constant near the v1.5 scalar in
  `ketu.calculations`; chart-level helper in `ketu.charts` alongside `is_day_chart`
  which already consumes `CHART_DTYPE`) is a strong candidate but the researcher
  confirms against the actual import graph and recommends; planner locks.
- **Composite β-velocity source** for D-01 (see D-01 note) — research determines.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap (binding)
- `.planning/REQUIREMENTS.md` — DSPD-01..07 + REL-01; the binding requirement
  contract. DSPD-01..06 are this phase. **Read first** — most decisions are locked
  here, not in this CONTEXT.md.
- `.planning/ROADMAP.md` § "Phase 40: Declination Speed Field & Chart API" — goal,
  depends-on, 6 success criteria (what must be TRUE).

### Domain gap doc (the why)
- `KETU-GAPS-declination.md` — the canonical gap analysis. Documents WHY this is
  Option B (Ketu patch, not Rahu finite-difference), the Ketu/Rahu boundary, the
  Δt=0.01 d idiom, the standstill-neutral requirement, and the "calculation already
  exists" framing. §"Décisions de cadrage (tranchées 2026-06-16)" is the locked
  scoping checklist.

### Implementation anchors (existing code to mirror)
- `ketu/charts/core.py:95-111` — `CHART_DTYPE` definition. `body_decl_speed` is
  appended additively after `body_decl` (line 103), `("body_decl_speed", "f8", (14,))`.
- `ketu/charts/api.py:379-394` — the `body_decl` derivation block in `compute_chart`;
  the closest analog. `body_decl_speed` mirrors this path but as a finite-difference
  slope (two evaluations).
- `ketu/calculations.py:495-524` — scalar `declination_velocity(jd, body)`; the
  FD step 0.01 d and `declination()` path to reuse verbatim. Lines 527-555:
  scalar `is_ascending_declination`. Line 656+: `__all__` export list.
- `ketu/composite/api.py:252-266` — how `body_decl` is self-consistently derived
  from composite λ,β (the v1.5 precedent for "derived from composite, not midpoint
  of parents"). D-01 extends this pattern to the velocity. Lines 248-251: composite
  `body_speeds` is the linear midpoint of parents' λ-velocities.
- `ketu/returns/lunar.py:37` — returns call `compute_chart` directly, so they
  inherit `body_decl_speed` for free (no change needed beyond the dtype/compute_chart
  work). Same for solar returns.
- `ketu/synastry/api.py:66-102` — synastry extends the body axis by concatenating
  partner `CHART_DTYPE` records; it inherits the new field automatically (verify the
  axis-extension helper carries `body_decl_speed`).
- `tests/charts/test_dtype.py` — the dtype ratchet. Lines 56-64 (`expected` field
  tuple), 67-85 (subarray shapes), 88-110 (kinds/itemsizes), 128-153 (construction
  shapes) all need `body_decl_speed` added. This ratchet breaks intentionally and is
  re-pinned (DSPD-04), mirroring how `body_decl` was added in v1.5.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`declination(jdate, body)`** (`calculations.py:440`) — array-vectorized δ via
  `calc_planet_position_batch` (loop-free). The `compute_chart` `body_decl` block
  already inlines this exact chain over `S + (14,)` in one pass; the speed field
  reuses it for two evaluations (jd and jd+0.01).
- **`declination_velocity(jdate, body)`** (`calculations.py:495`) — the scalar FD
  reference (`(δ(jd+0.01) − δ(jd)) / 0.01`). The chart field is its vectorised twin;
  numerical agreement against this scalar is success criterion 40.1 (DSPD-02).
- **`true_obliquity`, `spherical_to_rectangular`, `ecliptic_to_equatorial`,
  `rectangular_to_spherical`** (`ephemeris.coordinates`) — already imported in both
  `charts/api.py` and `composite/api.py`; the full δ chain. No new imports needed for
  the natal path.

### Established Patterns
- **Additive dtype-version bump** — `body_decl` (v1.5) is the exact precedent:
  append a `("...", "f8", (14,))` field, populate in `compute_chart`, break + re-pin
  the ratchet, document Kala positional impact. Follow it verbatim.
- **Vectorise over bodies, not over S** — `_vectorised_body_properties`
  (`charts/api.py:62`) loops 14 bodies; the δ block then computes over `S + (14,)`
  loop-free. The speed field stays in this pattern (two δ evaluations, still loop-free
  over S).
- **Composite never calls `compute_chart`** — it assembles the record field-by-field
  (`composite/api.py:227+`) and has an anti-regression ratchet against a Davison
  `compute_chart` call. D-01 must respect this: derive `body_decl_speed` inline from
  composite fields, not via a `compute_chart` re-entry.
- **`is_day_chart` lives in `ketu.charts` and reads `CHART_DTYPE`** — the precedent
  for a chart-level helper that consumes the dtype (candidate home for the chart-level
  declination helper; researcher confirms).

### Integration Points
- `CHART_DTYPE` (`charts/core.py`) — add the field.
- `compute_chart` (`charts/api.py`) — populate it (natal path; FD over S+(14,)).
- `composite/api.py` — populate it per D-01 (self-consistent FD on frozen λ,β).
- `synastry/api.py` — verify axis-extension carries it.
- returns (`returns/lunar.py`, solar) — inherit free via `compute_chart`; add a
  pinning test.
- `tests/charts/test_dtype.py` — re-pin the ratchet.
- `ketu.calculations.__all__` (and/or `ketu.charts`) — export `DECL_STANDSTILL_EPS`
  and the chart-level helper (namespace per research).

</code_context>

<specifics>
## Specific Ideas

- The user personally reviews the whole milestone before the release tag/publish
  (carried forward from `feedback_validation_review_before_release` — applies to
  Phase 41, not 40). Mark a go/no-go checkpoint before the irreversible publish.
- French + tutoiement in all user-facing messages, including during GSD
  orchestration (`feedback_sophie_orchestration`).
- The user confirmed "ok pour C" on the composite approach (Option C = FD on the
  composite's own frozen λ,β advanced by midpoint velocities) — D-01 is firmly his
  choice, not a default.

</specifics>

<deferred>
## Deferred Ideas

- **Rahu-side display logic** (raw value vs ↗/↘ sense, arrow/tint visual language,
  consistency with longitudinal ℞) — out of the engine entirely; Rahu's own repo.
  Listed in REQUIREMENTS.md "Out of Scope" and the gap doc's "Décisions restantes
  (côté Rahu)".
- **Declination *aspect* speed** (applying/separating parallels) — DECLA-F1, future
  release. This phase is the per-body δ-velocity field only.
- **Configurable Δt** — explicitly out of scope; reuse the package-wide 0.01 d idiom
  verbatim, no new API surface.
- **HARMF-01** (rich `--harmonics` CLI grammar) — unrelated future requirement.

None of these were in-scope creep during discussion — discussion stayed strictly
within the DSPD-01..06 boundary.

</deferred>

---

*Phase: 40-declination-speed-field-chart-api*
*Context gathered: 2026-06-17*
