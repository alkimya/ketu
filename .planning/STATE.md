---
gsd_state_version: 1.0
milestone: v1.2
milestone_name: Astrologie relationnelle et prédictive
status: executing
last_updated: "2026-05-24T10:24:21Z"
last_activity: 2026-05-24
progress:
  total_phases: 8
  completed_phases: 4
  total_plans: 23
  completed_plans: 20
  percent: 87
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-05-08 — v1.2 milestone initialized)

**Core value:** Cycle calculations must be correct, tested, and performant.
**Current focus:** Phase 17 — composite chart (midpoint variant)

## Current Position

Phase: 17 (composite-chart-midpoint-variant) — IN PROGRESS (1 of 4 plans complete)
Plan: 1 of 4 (Plan 01 complete; 02, 03, 04 pending)
Status: Plan 17-01 foundation shipped (COMP-02 + COMP-04 satisfied — `circular_midpoint` helper with signed-diff algebraic formulation; `ketu.composite` subpackage registered in `pyproject.toml`; Davison-deferred Notes block in `__init__.py` docstring; 18 ratchet tests pinning `mid(359°, 1°) == 0.0` + antipodal + vectorisation + NaN propagation + defensive normalisation; project suite 1083/1083 PASS, doc gates clean). Plan 17-02 next: `calculate_composite(chart_a, chart_b, system='placidus') -> CHART_DTYPE`.
Progress: [████████▌·] 87%
Last activity: 2026-05-24
Resume file: ready for /gsd:execute-phase 17 plan 02 (calculate_composite implementation)

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
| Phase 16-synastry P04 | ~30min (2 sessions) | 3 tasks | 5 files |
| Phase 16-synastry P05 | ~36min | 3 tasks | 7 files |
| Phase 16 P05 | ~36min | 3 tasks | 7 files |
| Phase 17 P01 | 7min | 3 tasks | 5 files |

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
- [Phase 16-04]: Suffixed argument-group order LOCKED (chart-A bundle → chart-B bundle → mode → system → polar-fallback → json) for `ketu synastry`; pattern reusable for Plans 17/18 two-chart sub-commands (composite, bi-wheel). `--mode dense` is meaningful via `--json` only — ASCII table view silently filters to aspect_type ≥ 0 to avoid 225-line NaN noise.
- [Phase 16-04]: STDERR diagnostics LAYERED on top of `emit_resolved_config` — 2 synastry-specific lines (`# Synastry mode: <mode>`, `# Orbs: synastry (factor 0.5 — astro.com convention)`) pin the orbs preset citation in EVERY invocation (ROADMAP success criterion #3 satisfied per-call, not just in docs).
- [Phase 16-04]: First-wins early-return ladder in `main()` is INTENTIONAL (Pitfall 8 from 16-RESEARCH.md), ratchet pinned by `test_list_flags_collision_first_wins` (XOR assertion between `--list-orbs` and `--list-house-systems` branches when both flags passed). Production code comment in parser.main() documents the contract; ladder order is NOT alphabetical, it's the source-declaration order (list_aspect_sets → list_house_systems → list_orbs).
- [Phase 16-04]: M-5 ratchet re-confirmed by import path: `ketu/cli/introspection.py:13-17` imports `_PRESET_BY_NAME` (singular, matching `ketu/aspects/presets.py:91`). Data-driven CLI output iterates `sorted(_ORB_PRESETS.keys())`, so v1.3 in-place dict extension surfaces automatically. JSON output adds 3 label fields (body_a_name, body_b_name, aspect_name) on top of the 8 SYNASTRY_DTYPE fields — consumers get human-readable rows without re-joining core dtype tables.
- [Phase 16-05]: Markers registered in `pyproject.toml [tool.pytest.ini_options].markers` (NOT in a `tests/conftest.py` — that file does not exist in this project; H-1 ratchet). `synastry_coverage_gate` joins `houses_coverage_gate` and `charts_coverage_gate`; pattern is now established for Plans 17/18/19 close-outs.
- [Phase 16-05]: Makefile target uses the two-step pattern (`pytest tests/synastry/ + coverage report --include='ketu/synastry/*' --fail-under=95`) inherited from Phase 14 `charts-coverage` and Phase 10 `houses-coverage` — avoids the NumPy `_NoValueType` reload bug from sub-package source narrowing. Single-step `--cov=ketu/synastry --cov-fail-under=95` was REJECTED for this reason.
- [Phase 16-05]: See Also entries follow the importable-Python-path convention across all 4 synastry source files (Phase 13 BLOCKER lesson: numpydoc's See Also parser crashes the lint when given slash-style file paths). 11 new See Also entries added; all numpydoc lint clean; all references smoke-imported before commit.
- [Phase 16-05]: CHANGELOG entry is additive-only (7 new bullets under `## [Unreleased]` `### Added`). No `### Changed` / `### Deprecated` / `### Removed` sections touched. v1.2 framing is non-breaking minor strict; the `[1.2.0]` release heading is owned by Phase 20.
- [Phase 16-05]: 5 ROADMAP Phase 16 success criteria smoke-tested PASS with output excerpts captured in `.planning/phases/16-synastry/16-05-SUMMARY.md`. SC#1 (SYNASTRY_DTYPE + 5 mandatory fields): 25 aspects, schema match. SC#2 (dense + filtered same schema): dense=(225,), filtered=(25,). SC#3 (tighter orbs + Astrodienst citation): Sun-Moon synastry=6.0°, classical=12.0°, citation rendered in help(). SC#4 (3 oracle couples): curie 2.27°, diana_charles 2.03°, lennon_ono 2.13° under 5.0° ceiling. SC#5 (coverage 100% on ketu/synastry/; UTC restated): 100% coverage, "UTC ONLY" loud in Notes section.
- [Phase 17]: [Phase 17-01]: circular_midpoint formulation switched from complex-exponential (~1 ulp drift on representable means) to signed-diff algebraic — float-exact for mid(10°,20°)==15°, preserves all documented properties (wraparound, antipodal pin, NaN propagation, vectorisation). Listed in 17-RESEARCH.md §Alternative formulation; Rule 1 auto-fix.
- [Phase 17]: [Phase 17-01]: Antipodal pin convention (|delta|==180° collapses to 0.0) implemented via explicit np.isclose+np.where guard rather than relying on np.angle(0+0j) coincidence; tripwire test test_antipodal_pinned_convention fails loudly if convention changes.
- [Phase 17]: [Phase 17-01]: Davison defer in __init__.py Notes block (loudest visibility); zero runtime API surface for Davison (no NotImplementedError stub, no TODO comment, no See Also entry); IDE autocomplete consumers see nothing about Davison — Phase 17 standard for COMP-04.

## Session Continuity

v1.2 roadmap written 2026-05-08. **Phase 17 (Composite Chart, midpoint variant) démarrée 2026-05-24** — Plan 17-01 foundation shipped (2026-05-24T10:24Z, ~7min, 3 tasks, 5 files): `ketu/composite/` subpackage skeleton (`__init__.py` avec module docstring incluant Davison-deferred Notes block — COMP-04 binding satisfait, **zero runtime API surface pour Davison**: pas de stub, pas de TODO, pas de See Also entry) + `circular_midpoint(lon_a, lon_b)` helper dans `core.py` (formulation signed-diff algébrique, float-exact pour mid(10°,20°)==15°; antipodal pin via np.isclose+np.where guard returning 0.0; defensive `% 360.0` normalisation; vectorisable, scalar→0-d ndarray) + suite 18 tests COMP-02 dans `tests/composite/test_circular_midpoint.py` (Wraparound, Vectorisation, DefensiveNormalisation, NanPropagation classes; headline ratchet `test_wraparound_359_1_returns_zero` strict-equality pinning `mid(359°, 1°) == 0.0`) + `pyproject.toml` mis à jour (`"ketu.composite"` ajouté en fin de `[tool.setuptools].packages` list, synastry precedent). **Suite projet: 1083/1083 verts** (1065 baseline + 18 nouveaux). Doc gates verts (numpydoc lint clean sur les 2 nouveaux modules; interrogate 100% sur `ketu/composite/`). **Déviation** (Rule 1 - bug): formulation `circular_midpoint` switchée de complex-exponential (recommandé par le plan, mais ~1 ulp drift via deg2rad/rad2deg round-trip) vers signed-diff algébrique (alternative documentée dans 17-RESEARCH.md §Alternative formulation) — float-exact pour les means représentables, préserve toutes les propriétés documentées; verify command Task 1 strict `assert == 15.0` PASS. Workflow incident notable: `venv/bin/pytest` a un shebang hardcodé vers `/home/loc/workspace/solaris/ketu/venv/bin/python3` (v1.1 working-tree leftover documenté dans STATE.md, NOT in v1.2 scope); workaround = `python -m pytest`. Plans 17-02 (calculate_composite implementation, COMP-01 + COMP-03), 17-03 (oracle fixtures réutilisant les 3 couples synastry), 17-04 (close-out: composite_coverage_gate + Makefile + CHANGELOG) à suivre. Last session: Sophie + executor agent, stopped at: Plan 17-01 complete — **ready for /gsd:execute-phase 17 plan 02 (calculate_composite)**.

---

**Historical context (pre-Phase 17):**

v1.2 roadmap written 2026-05-08. Phase 15 close : 15-01..04 tous complétés (HOU2-01..05 satisfaits, 909 tests verts, 6 systèmes registrés). Phase 16 (Synastry) démarrée 2026-05-11 — Plan 16-01 foundation closed: ketu/synastry/ subpackage skeleton + SYNASTRY_DTYPE (8 fields, frozen) + SYNASTRY_BODY_COUNT=15 + orb formula module (SYNASTRY_FACTOR=0.5, ASC_MC_NATAL_ORB_DEG=8.0, resolve_orb_set resolver) livrés. **Plan 16-02 compute API closed (2026-05-11T07:34Z)**: `calculate_synastry(chart_a, chart_b, aspects, orbs, mode)` livré dans `ketu/synastry/api.py` (composition-only — cross-product 15x15, self-pairs INCLUDED, sentinel-fill dense, canonical-order filtered, velocity-based signed-applying); 60 nouveaux tests (29 unit + 10 applying + 21 idempotency); suite totale 1010 verts (950 + 60); coverage 100% sur ketu/synastry/; doc gates verts. **Plan 16-03 oracle tests closed (2026-05-11T09:50Z)**: 3 hand-validated celebrity synastry oracle fixtures (Curie AA/C, Diana/Charles AA/AA, Lennon/Ono A/AA) livrés comme JSON dans `tests/synastry/fixtures/oracle_*.json` (schema v1, Rodden ratings, AstroDatabank URLs, self-consistency validation_source). `tests/synastry/conftest.py` étendu (NON écrasé) avec `load_oracle_fixture` + `ORACLE_SLUGS` + `oracle_fixture` parametrized fixture. `tests/synastry/test_oracle.py` ajouté — 7 tests × 3 fixtures = 21 tests paramétrisés, tous verts. Max |orb| reporté par couple (ROADMAP critère #4): curie 2.27°, diana_charles 2.03°, lennon_ono 2.13° (largement sous le plafond permissif de 5.0°). Tests run OFFLINE — pas de fetch Astro.com (anti-bot per 16-RESEARCH.md Pitfall); cross-validation Astro.com déférée à Plan 05 manual follow-up. Suite synastry: 122/122 verts. Suite projet: **1058/1058 verts**. **Plan 16-04 CLI closed (2026-05-11T09:11Z)** : `ketu synastry` sub-command shipped (9 args) avec aligned ASCII table par défaut + JSON list-of-dicts opt-in (11 keys par dict). `ketu --list-orbs` introspection flag wired. STDERR diagnostics layered. M-1 first-wins early-return ladder ratchet pinned. M-5 `_PRESET_BY_NAME` singular import re-confirmed. **32 nouveaux tests CLI**. Suite projet : 1064/1064 verts. Coverage `ketu/cli/synastry_cmd.py` 98%; `ketu/synastry/` toujours 100%. Doc gates verts. Aucune déviation. **Plan 16-05 close-out shipped (2026-05-11T10:00Z)** : `make synastry-coverage` Makefile target (mirror de `make charts-coverage` et `make houses-coverage`, two-step pattern, ≥95% gate sur `ketu/synastry/`, mesuré à 100%). `synastry_coverage_gate` pytest marker enregistré dans `pyproject.toml [tool.pytest.ini_options].markers` (mirror de `houses_coverage_gate`, `charts_coverage_gate`; H-1 ratchet honoré — pas de `tests/conftest.py` créé, ce fichier n'existe pas dans le projet). Sentinel test `tests/synastry/test_synastry_coverage_gate.py` ajouté (ratchet marker recognition + module import, PASS sous `-W error::pytest.PytestUnknownMarkWarning`). See Also cross-references étendues sur les 4 fichiers source synastry (`__init__.py` 4 entries, `api.py` 5 entries dans `calculate_synastry`, `orbs.py` 2 nouveaux blocs de 3 entries sur `synastry_orb_limit` + `resolve_orb_set`); 11 entries total, toutes references importables Python paths (Phase 13 lesson honoré), numpydoc lint clean sur tous les fichiers synastry. CHANGELOG `## [Unreleased]` `### Added` étendu avec 7 nouveaux bullets citant SYN-01..05 (subpackage, orbs module, CLI sub-command, --list-orbs flag, oracle fixtures, Makefile target, pytest marker); additive-only, aucune section Changed/Deprecated/Removed touchée. **5 ROADMAP Phase 16 success criteria smoke-tested PASS** avec output excerpts capturés dans `16-05-SUMMARY.md`: SC#1 (SYNASTRY_DTYPE + 5 mandatory fields, 25 aspects), SC#2 (dense=(225,), filtered=(25,), schemas match), SC#3 (Sun-Moon synastry=6.0° < classical=12.0°, Astrodienst citation présente dans help()), SC#4 (3 couples curie/diana_charles/lennon_ono, max |orb| 2.27/2.03/2.13°), SC#5 (coverage 100% sur ketu/synastry/, "UTC ONLY" loud dans Notes section). **Suite projet : 1065/1065 verts** (1064 baseline + 1 nouveau sentinel). Doc gates verts (interrogate 100% project-wide, numpydoc 0 issues sur synastry, mypy --strict 0 issues sur 51 fichiers). Aucune déviation (plan exécuté tel qu'écrit; cf. SUMMARY 16-05). Incident mineur de process : `git stash pop` essayé pendant Task 3 verification a déclenché un conflit avec une stash pré-existante (`stash@{0}: pre-release-merge: unrelated phase09/11 plan drift`) à cause d'artéfacts non-suivis dans le working tree (`.claude/`, `.opencode/`); résolu proprement en acceptant les versions HEAD; commits Tasks 1+2 vérifiés intacts; counter-measure noté dans SUMMARY (éviter `git stash` quand le working tree contient des artéfacts non-suivis). Last session: Sophie + executor agent, stopped at: Plan 16-05 complete — **Phase 16 close à 100% — ready for /gsd:verify-phase 16** ou démarrage Phase 17 (Composite Chart).
