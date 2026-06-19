# Requirements: Ketu — v1.8 Declination Speed

**Defined:** 2026-06-17
**Core Value:** Cycle calculations must be correct, tested, and performant. If the math is wrong, nothing downstream matters.

## Milestone Intent

Expose declination velocity dδ/dt as a `body_decl_speed` field in `CHART_DTYPE` — the one real gap that blocks the Rahu UI from showing montant/descendant in declination without computing astronomy in the front-end.

**The calculation already exists.** `ketu==1.6.0` ships `declination_velocity(jd, body)` and `is_ascending_declination(jd, body)` in `ketu.calculations` (delivered in v1.5, finite-difference step 0.01 d). The gap is NOT that Ketu cannot compute dδ/dt — it can, scalar-wise. The gap is that dδ/dt is **not in `CHART_DTYPE`**, the structured chart Rahu consumes. `body_decl` (δ) is there; `body_decl_speed` (dδ/dt) is not. This milestone exposes the field; it does not reinvent the math.

**Boundary (non-negotiable):** Rahu computes no astronomy. All display decisions (show the dδ/dt value vs only the ↗/↘ sense; visual language vs longitudinal ℞) are Rahu's and live OUTSIDE this engine. The standstill threshold is defined IN Ketu as a public contract so Rahu invents none.

**Framing:** MINOR-not-patch (1.8.0). The dtype layout grows (like `body_decl` in v1.5) → Kala re-pins PyPI; the dtype ratchet test is updated. It is a derivative of an existing field (δ), not a new body/house/part — in the spirit of "Ketu ~complete".

## v1.8 Requirements

Requirements for the v1.8 release. Each maps to roadmap phases (numbering continues from 40).

### Declination Speed Field

- [x] **DSPD-01**: `CHART_DTYPE` gains an additive field `("body_decl_speed", "f8", (14,))` (layout grows like `body_decl` in v1.5), populated by `compute_chart` (scalar + array `jd`) via the vectorized `declination_velocity` path; raw deg/day value (mirrors `body_speeds` for longitude — the ↗/↘ sense reads off the sign).
- [x] **DSPD-02**: Δt = 0.01 day reused verbatim from the existing `declination_velocity` finite-difference step (no new API surface, not configurable); numerical agreement verified against scalar `declination_velocity(jd, body)` (Δ = 0, or a documented FD tolerance).
- [x] **DSPD-03**: `body_decl_speed` inherited by synastry / composite / returns; the composite δ-speed is **derived from the composite chart** (recomputed on composite λ,β via the same path), never the midpoint of the parents' `body_decl_speed` (same trap as `body_decl` in v1.5).
- [x] **DSPD-04**: the `CHART_DTYPE` layout ratchet test is updated for the new field — the ratchet breaks intentionally and is re-pinned (as for `body_decl` in v1.5); Kala positional impact documented.

### Standstill & Chart-Level API

- [x] **DSPD-05**: a public, tested constant `DECL_STANDSTILL_EPS` (deg/day) defined IN Ketu and documented as a contract — Rahu invents no astronomical threshold; `|dδ/dt| ≤ DECL_STANDSTILL_EPS` ⇒ standstill (neutral).
- [x] **DSPD-06**: a chart-level `is_ascending_declination` helper reading the sign of `body_decl_speed` + the standstill threshold (ascending if `> DECL_STANDSTILL_EPS`, descending if `< −DECL_STANDSTILL_EPS`, neutral otherwise), distinct from — and consistent with — the v1.5 scalar version.

### Documentation & Release

- [x] **DSPD-07**: documentation en + fr of the `body_decl_speed` field, the Δt 0.01 d step, the `DECL_STANDSTILL_EPS` threshold, the chart-level helper, and the Ketu/Rahu boundary (Rahu computes nothing); FR `.po` translated + `.mo` recompiled (no English fallback).
- [x] **REL-01**: `ketu==1.8.0` shipped to PyPI via OIDC (push main + tag); MINOR-not-patch bump in all three source-of-truth files; dated `[1.8.0]` changelog (EN+FR) + UPGRADING v1.7→v1.8 with explicit Kala re-pin guidance (dtype layout grows); human go/no-go honoured; post-publish fresh-venv smoke FROM PyPI confirms `body_decl_speed` is present in `CHART_DTYPE`, populated non-trivially, no `pyswisseph` at runtime.

## Future Requirements

Deferred to a later release. Tracked but not in the current roadmap.

### CLI / Harmonics

- **HARMF-01**: Rich `--harmonics` CLI grammar — multi-harmonic (`h7,h11`) and preset+harmonic mixing (`traditional,h7`). v1.5 shipped only the Tight single-token form; v1.6/v1.7/v1.8 stay off it.

### Declination follow-ups

- **DECLA-F1**: Declination synastry / applying-timing / dedicated CLI surface. v1.6 shipped in-orb detection only; natural follow-ups if demand surfaces.

## Out of Scope

Explicitly excluded for v1.8. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Rahu-side display logic (value vs ↗/↘ sense, arrow/tint visual language) | Display is the front-end's responsibility; the Ketu field gives both the value and the sign. Out of the engine entirely. |
| Rahu computing dδ/dt itself (Option A from the gap doc) | The Ketu/Rahu boundary is non-negotiable: Rahu does no astronomy, even a finite difference. Decided 2026-06-16. |
| Configurable Δt (per-call FD step) | Reuse the package-wide 0.01 d idiom verbatim; a tunable step is a new API surface with no demand. |
| Declination *aspect* speed (applying/separating parallels) | This milestone is the per-body δ-velocity field only; declination-aspect dynamics remain DECLA-F1, out of scope. |
| New bodies / houses / Arabic parts | Ketu is ~feature-complete as an engine; v1.8 is a derivative of an existing field (δ), not a new entity. |
| `pyswisseph` as a runtime dependency | Test-only only; AGPL + NumPy-only brand promise hold. |
| Changing `body_speeds` / `body_decl` semantics | `body_decl_speed` is purely additive; existing fields stay byte-compatible in value. |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DSPD-01 | Phase 40 | Complete |
| DSPD-02 | Phase 40 | Complete |
| DSPD-03 | Phase 40 | Complete |
| DSPD-04 | Phase 40 | Complete |
| DSPD-05 | Phase 40 | Complete |
| DSPD-06 | Phase 40 | Complete |
| DSPD-07 | Phase 41 | Complete |
| REL-01 | Phase 41 | Complete |

**Coverage:**

- v1.8 requirements: 8 total
- Mapped to phases: 8/8
- Unmapped: 0 ✓

---
*Requirements defined: 2026-06-17*
*Last updated: 2026-06-17 — traceability filled by roadmapper (Phases 40-41)*
