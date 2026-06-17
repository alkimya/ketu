# Phase 40: Declination Speed Field & Chart API - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-17
**Phase:** 40-declination-speed-field-chart-api
**Areas discussed:** Composite δ-speed derivation, DECL_STANDSTILL_EPS value, chart-level helper encoding, API namespace

---

## Composite δ-speed derivation (DSPD-03 trap)

First pass:

| Option | Description | Selected |
|--------|-------------|----------|
| FD sur jd composite moyen | Differentiate δ at jd_composite and jd_composite+0.01 on frozen composite λ,β via the declination_velocity path | ✓ (first pass) |
| Midpoint des dδ/dt parents | Average the two parents' body_decl_speed — the trap DSPD-03 forbids | |
| FD sur les λ,β composite figés | Advance composite λ,β by their midpoint velocities over 0.01d, recompute δ at both points, take slope | |

Claude flagged a technical reservation: the standard `declination(jd_comp+0.01)`
path RE-FETCHES real planetary positions at a near-arbitrary jd (mean of two
births), measuring a real body's velocity rather than the frozen composite point's
— physically inconsistent with the composite's frozen λ,β. Re-asked with the
nuance.

Second pass (precision):

| Option | Description | Selected |
|--------|-------------|----------|
| FD sur λ,β composite avancés | Advance composite λ,β by their midpoint velocities over 0.01d, recompute δ, take slope — self-consistent with the composite's own fields | ✓ |
| Garder FD sur jd composite | Accept the re-fetch behaviour, document it explicitly | |
| Laisser le researcher trancher | Researcher analyses both numerically | |

**User's choice:** FD on the composite's own frozen λ,β advanced by midpoint
velocities (Option C). Confirmed verbatim: "ok pour C".
**Notes:** The composite has no canonical jd (literal code comment at
`composite/api.py:36,156,321`). Velocity needs two time points; the only
self-consistent derivation advances the composite's OWN frozen fields. Open
implementation detail: the composite stores λ-velocity (`body_speeds`) but not a
β-velocity field — research must determine the β-rate source for the FD.

---

## DECL_STANDSTILL_EPS value

| Option | Description | Selected |
|--------|-------------|----------|
| Je te laisse rechercher | Researcher/planner determines a justified, tested value by numerical analysis | ✓ |
| Très petit (~0.001°/j) | Quasi-zero; neutralises only true turning points; risks FD-noise sign flips | |
| Modéré (~0.01–0.05°/j) | Wider dead zone; more robust to noise but masks real slow motion | |

**User's choice:** Defer to research.
**Notes:** Constraints recorded in CONTEXT.md D-02 — small enough not to mask real
slow motion (outer planets), large enough to absorb FD noise near real standstills
(Moon/Sun turning points). Must be tested + documented as a public contract (DSPD-05).

---

## Chart-level helper output encoding

| Option | Description | Selected |
|--------|-------------|----------|
| Array int8 {-1,0,+1} | +1 ascending, -1 descending, 0 neutral; vectorised, ML-friendly, sign reads like body_speeds | ✓ |
| Array de chaînes | U10 'ascending'/'descending'/'neutral'; readable but off-convention and heavier | |
| Deux masques booléens | (is_ascending, is_neutral); awkward for 3 states, neutral implicit | |

**User's choice:** int8 array {-1, 0, +1}, shape (14,) / S+(14,).
**Notes:** Classification rule from DSPD-06 — ascending if speed >
DECL_STANDSTILL_EPS, descending if < −EPS, neutral otherwise. Distinct from the
v1.5 scalar `is_ascending_declination` (plain bool).

---

## API namespace (DECL_STANDSTILL_EPS + chart-level helper)

| Option | Description | Selected |
|--------|-------------|----------|
| ketu.calculations (les deux) | Both in calculations alongside the v1.5 scalar; risks import cycle (calculations doesn't depend on charts) | |
| Constante calculations, helper charts | Constant near the scalar; helper in charts (consumes CHART_DTYPE, like is_day_chart) | |
| Laisser le researcher trancher | Researcher verifies the real import graph and recommends | ✓ |

**User's choice:** Defer to research.
**Notes:** Known tension recorded — `calculations.py` does not currently import
`charts`, so a chart-reading helper in `calculations` risks a cycle. Likely-clean
split (constant in calculations, helper in charts) is a strong candidate; researcher
confirms against the actual import graph.

---

## Claude's Discretion

- API namespace for `DECL_STANDSTILL_EPS` and the chart-level helper — deferred to
  the researcher (import-graph check).
- Composite β-velocity source for the D-01 finite difference — deferred to research.
- DECL_STANDSTILL_EPS numeric value — deferred to research within the documented
  constraints.
- Naming/signature of the chart-level helper (as long as clearly distinct from the
  v1.5 scalar and reading the `body_decl_speed` field) — planner's call.

## Deferred Ideas

- Rahu-side display logic (raw value vs ↗/↘ sense, visual language) — out of engine.
- Declination *aspect* speed (DECLA-F1) — future release.
- Configurable Δt — out of scope; reuse 0.01 d verbatim.
- HARMF-01 (rich `--harmonics` CLI grammar) — unrelated future requirement.
