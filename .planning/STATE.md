---
gsd_state_version: 1.0
milestone: v1.2
milestone_name: Astrologie relationnelle et prédictive
status: executing
last_updated: "2026-05-11T09:50:00Z"
last_activity: 2026-05-11
progress:
  total_phases: 8
  completed_phases: 3
  total_plans: 19
  completed_plans: 17
  percent: 89
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-05-08 — v1.2 milestone initialized)

**Core value:** Cycle calculations must be correct, tested, and performant.
**Current focus:** Phase 16 — synastry

## Current Position

Phase: 16 (synastry) — IN PROGRESS
Plan: 4 of 5 (Plans 01, 02, 03 complete; Plan 04 already advanced in parallel — see commits 9c81a86 + b788da3; Plan 05 close-out remains)
Status: Plan 16-03 oracle tests closed (SYN-05 satisfied — 3 hand-validated oracle pairs pinned, 21 parametrized tests green, max |orb| reported per couple); Wave 3 oracle leg COMPLETE
Progress: [████████▉░] 89%
Last activity: 2026-05-11
Resume file: .planning/phases/16-synastry/16-04-PLAN.md (if still pending close-out) or 16-05-PLAN.md (close-out)

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
| Phase 16-synastry P02 | ~9min | 3 tasks | 6 files |
| Phase 16-synastry P03 | ~5min | 2 tasks | 5 files |

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
- [Phase 16-02]: calculate_synastry signature locked: (chart_a, chart_b, aspects='classical', orbs='synastry', mode='filtered'); defaults align with CONTEXT.md decisions; cross-product via np.indices((15,15)) NOT triu_indices; self-pairs INCLUDED.
- [Phase 16-02]: Applying convention refined (Rule 1 deviation): plan-supplied claim 'ALL ASC/MC contacts applying=False' was incorrect — only angle-to-angle pairs (both speeds=0) are mechanically applying=False; angle-to-planet uses signed rel_speed = -planet_speed. Docstrings + tests corrected in commit cfc3d2f.
- [Phase 16-02]: Filtered row order is canonical body-pair (body_a*15 + body_b) ascending, NOT |orb|-ascending — predictable for ML/oracle tests; regression-guard test in place. Pitfall 6 f4 bit-exact ratchet across all 225 pairs at conjunction.
- [Phase 16-03]: Self-consistency oracle is PRIMARY methodology — fixtures generated from compute_chart + calculate_synastry, lowest-|orb| aspects pinned as regression contracts; Astro.com cross-validation deferred to Plan 05 manual follow-up (anti-bot per 16-RESEARCH.md). Each fixture documents this loudly in validation_source.
- [Phase 16-03]: Rating-uncertainty hygiene enforced — Curie pair (Pierre = C, noon LMT) and Lennon/Ono pair (Lennon = A, ±15min) EXCLUDE ASC/MC from expected_aspects; Diana/Charles (both AA) INCLUDE 3 ASC contacts. Schema v1 frozen with mandatory keys (schema_version, name, rodden_a, rodden_b, chart_a, chart_b, expected_aspects, validation_source, tolerance_deg).
- [Phase 16-03]: Permissive orb_max_deg=5.0 (presence ceiling) decoupled from tighter tolerance_deg=0.1 (cross-validation quality bar for Plan 05). Max |orb| recorded per couple in pytest -v -s output: curie 2.27°, diana_charles 2.03°, lennon_ono 2.13° — comfortably under the 5.0° ceiling (ROADMAP success criterion #4 satisfied).

## Session Continuity

v1.2 roadmap written 2026-05-08. Phase 15 close : 15-01..04 tous complétés (HOU2-01..05 satisfaits, 909 tests verts, 6 systèmes registrés). Phase 16 (Synastry) démarrée 2026-05-11 — Plan 16-01 foundation closed: ketu/synastry/ subpackage skeleton + SYNASTRY_DTYPE (8 fields, frozen) + SYNASTRY_BODY_COUNT=15 + orb formula module (SYNASTRY_FACTOR=0.5, ASC_MC_NATAL_ORB_DEG=8.0, resolve_orb_set resolver) livrés. **Plan 16-02 compute API closed (2026-05-11T07:34Z)**: `calculate_synastry(chart_a, chart_b, aspects, orbs, mode)` livré dans `ketu/synastry/api.py` (composition-only — cross-product 15x15, self-pairs INCLUDED, sentinel-fill dense, canonical-order filtered, velocity-based signed-applying); 60 nouveaux tests (29 unit + 10 applying + 21 idempotency); suite totale 1010 verts (950 + 60); coverage 100% sur ketu/synastry/; doc gates verts. **Plan 16-03 oracle tests closed (2026-05-11T09:50Z)**: 3 hand-validated celebrity synastry oracle fixtures (Curie AA/C, Diana/Charles AA/AA, Lennon/Ono A/AA) livrés comme JSON dans `tests/synastry/fixtures/oracle_*.json` (schema v1, Rodden ratings, AstroDatabank URLs, self-consistency validation_source). `tests/synastry/conftest.py` étendu (NON écrasé) avec `load_oracle_fixture` + `ORACLE_SLUGS` + `oracle_fixture` parametrized fixture. `tests/synastry/test_oracle.py` ajouté — 7 tests × 3 fixtures = 21 tests paramétrisés, tous verts. Max |orb| reporté par couple (ROADMAP critère #4): curie 2.27°, diana_charles 2.03°, lennon_ono 2.13° (largement sous le plafond permissif de 5.0°). Tests run OFFLINE — pas de fetch Astro.com (anti-bot per 16-RESEARCH.md Pitfall); cross-validation Astro.com déférée à Plan 05 manual follow-up. Suite synastry: 122/122 verts. Suite projet: **1058/1058 verts** (1037 baseline post-Plan-04 commits + 21 oracle). Coverage `ketu/synastry/` toujours 100%; interrogate 100%, numpydoc 0 issues, mypy --strict 0 issues. Aucune déviation (plan exécuté tel qu'écrit). Last session: Sophie + executor agent, stopped at: Plan 16-03 complete. Next: Plan 16-04 (CLI) déjà partiellement avancé en parallèle (commits 9c81a86 + b788da3) — vérifier statut + Plan 16-05 (close-out) ensuite.
