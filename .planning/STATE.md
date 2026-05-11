---
gsd_state_version: 1.0
milestone: v1.2
milestone_name: Astrologie relationnelle et prédictive
status: executing
last_updated: "2026-05-11T07:21:26Z"
last_activity: 2026-05-11
progress:
  total_phases: 8
  completed_phases: 3
  total_plans: 19
  completed_plans: 15
  percent: 79
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-05-08 — v1.2 milestone initialized)

**Core value:** Cycle calculations must be correct, tested, and performant.
**Current focus:** Phase 16 — synastry

## Current Position

Phase: 16 (synastry) — IN PROGRESS
Plan: 2 of 5 (Plan 01 complete; Plan 02 ready to start)
Status: Plan 16-01 foundation closed (SYN-01 satisfied)
Progress: [████████░░] 79%
Last activity: 2026-05-11
Resume file: .planning/phases/16-synastry/16-02-PLAN.md

## Performance Metrics

**Velocity totals:**

- v1.0: 16 plans / 7 phases (one decimal phase 2.1 inserted)
- v1.1: 27 plans / 5 phases (no decimal phases inserted)

**v1.1 phase breakdown (active time):**

| Phase                          | Plans | Active                                          | Avg/Plan      |
| ------------------------------ | ----- | ----------------------------------------------- | ------------- |
| 8. Lilith Verification & Fix   | 5     | ~22m 18s                                        | ~4m 28s       |
| 9. Configurable Aspects        | 6     | ~44m 58s                                        | ~7m 30s       |
| 10. Houses Module              | 6     | ~58m 10s                                        | ~9m 42s       |
| 11. CLI Refactor & Integration | 6     | ~34m 52s                                        | ~5m 49s       |
| 12. Release Preparation v1.1.0 | 4     | ~20m 26s active (~3h elapsed incl. checkpoints) | ~5m 6s active |
| Phase 15 P01 | 6 | 5 tasks | 9 files |
| Phase 15 P02 | 8min | 7 tasks | 7 files |
| Phase 15 P03 | 7min | 5 tasks | 5 files |
| Phase 15 P04 | 7min | 7 tasks | 5 files |
| Phase 16 P01 | ~6min | 3 tasks | 7 files |

## Accumulated Context

**Open blockers:** None.

**v1.2 roadmap structure:**

- Phase 13: Doc Gates & CI Foundation (OPS-01, OPS-02) — early ops debt; gates apply to all subsequent v1.2 code
- Phase 14: Chart Abstraction Foundation (CHART-01..05) — keystone upstream of SYN/COMP/RET
- Phase 15: Additional House Systems (HOU2-01..05) — independent of CHART; extends `SYSTEMS` registry
- Phase 16: Synastry (SYN-01..05) — depends on Phase 14
- Phase 17: Composite Chart Midpoint (COMP-01..04) — depends on Phase 14
- Phase 18: Solar Return Standard + Relocated (RET-01..05) — depends on Phase 14
- Phase 19: Arabic Parts Framework + 8 Parts (PARTS-01..08) — depends on Phase 14 (`is_day_chart`)
- Phase 20: Release Preparation v1.2.0 (OPS-03, OPS-04, OPS-05) — late ops debt + PyPI publish

**v1.2 ops debt (will close during this milestone):**

- `interrogate ≥95%` not installed/wired into CI — Phase 13 (OPS-01)
- `numpydoc validate` not wired into CI — Phase 13 (OPS-02)
- Node.js 20 deprecation warnings on every workflow step — Phase 20 (OPS-03)
- `fr/CHANGELOG.md` aspirational reference — Phase 20 (OPS-04, decision)
- Venv shebangs hardcoded to `/home/loc/workspace/solaris/ketu/venv/bin/python3` — workaround documented; not in v1.2 scope

**Working-tree leftovers (NOT v1.2 scope):**

- Stash `pre-release-merge: unrelated phase09/11 plan drift` left as-is

**Downstream impact (carried over from v1.1 BREAKING):**

- Kala (`solaris/kala`) — KetuAdapter must explicitly request `aspects=EXTENDED` for v1.0 behavior parity (documented in UPGRADING.md)
- Lilith consumers — recompute any cached values; ~180° shift on every date

**v1.2 framing constraints:**

- Non-breaking minor strict — all new APIs additive; no defaults changed; no exports removed
- Pure-NumPy contract preserved (no scipy / no swisseph runtime)
- Coverage gates: ≥90% project / ≥85% per module / ≥95% on new modules (`ketu/charts/`, `ketu/parts/`)

## Decisions

- Plan 15-03: REYKJAVIK_REGIO_TOL_ARCMIN pinned at 1.0' (measured 0.86' on 2026-05-09) — decision-tree case <1' bucket per Plan 15-03 Task 5.
- Plan 15-03: Pole-height naming convention (`pole_height_outer_deg` / `pole_height_inner_deg`) as visual ratchet against Pitfall 4 (geographic latitude vs pole height); grep gate enforces no `_asc1` call receives raw geographic latitude in `regiomontanus.py`.
- Plan 15-03: Regiomontanus follows Koch-style NaN propagation at polar boundary (D-02 verrouillé in 15-CONTEXT.md), NOT swisseph `MC<->IC` swap; existing `api.py` `polar_fallback` machinery routes NaN to Porphyry without modification (verified by 2 dedicated integration tests).
- Plan 15-04: Parser dispatcher dynamique via `choices=sorted(SYSTEMS.keys())` (D-07 verrouillé) — future-proof, Campanus/Topocentric/Alcabitius en v1.3 ne nécessiteront aucune modification du parser.
- Plan 15-04: Top-level `--list-house-systems` help rendu statique générique (`"List all registered house systems and exit."`) — évite la dette de maintenance ; détails dans le subcommand `--system` help.
- Plan 15-04: Pitfall 7 affecte 2 emplacements (test_houses_cmd.py ET test_parser.py) — auto-fix Rule 1 sur le second emplacement non identifié dans le plan ; substitution `regiomontanus` → `nonexistent_xyz` ratchet la sémantique CLI sans dépendance à la blacklist.
- Plan 16-01: SYNASTRY_DTYPE record-style verrouillé (anti-axis-style ratchet test) — un schéma unique pour dense + filtered modes via sentinelles `aspect_type=-1` / `orb=NaN`.
- Plan 16-01: 8 fields locked as floor — 5 ROADMAP-mandatory + 3 metadata (lon_a, lon_b, orb_limit) rendent les rows auto-suffisants, pas de re-join CHART_DTYPE downstream.
- Plan 16-01: SYNASTRY_FACTOR = 0.5 single-source-of-truth (cité astro.com FAQ "Partner horoscopes") — no parallel hardcoded orb table, multiplicatif uniquement sur la formule natale `(orb_a + orb_b)/2 * coef`.
- Plan 16-01: ASC_MC_NATAL_ORB_DEG = 8.0 (mid-tier, matches Mercury/Mars/Uranus/Neptune in ketu.core.bodies) — donne 4° sur ASC-planète conjunction après factor 0.5, conforme à la pratique astro.com.
- Plan 16-01: `_PRESET_BY_NAME` singulier (matches `ketu/aspects/presets.py:91`) — ratchet test en place contre la dérive pluralisée.
- Plan 16-01: `OrbSetSpec = Union[None, str]` (no dict/callable/Sequence en v1.2) — surface narrow MVP.
- Plan 16-01: `calculate_synastry` deferred to Plan 02 — foundation surface frozen first; `__init__.py` exports 6 names actuellement (SYNASTRY_DTYPE, SYNASTRY_BODY_COUNT, SYNASTRY_FACTOR, ASC_MC_NATAL_ORB_DEG, resolve_orb_set, OrbSetSpec).

## Session Continuity

v1.2 roadmap written 2026-05-08. Phase 15 close : 15-01..04 tous complétés (HOU2-01..05 satisfaits, 909 tests verts, 6 systèmes registrés). Phase 16 (Synastry) démarrée 2026-05-11 — Plan 16-01 foundation closed: ketu/synastry/ subpackage skeleton + SYNASTRY_DTYPE (8 fields, frozen) + SYNASTRY_BODY_COUNT=15 + orb formula module (SYNASTRY_FACTOR=0.5, ASC_MC_NATAL_ORB_DEG=8.0, resolve_orb_set resolver) livrés. Tests: 41 new (18 dtype + 23 orbs); suite totale 950 verts (909 baseline + 41); coverage 100% sur ketu/synastry/; doc gates green (interrogate 100%, numpydoc 0 issues, mypy --strict 0 issues). Last session: Sophie + executor agent, stopped at: Plan 16-01 complete. Next: Plan 16-02 (compute API — calculate_synastry).
