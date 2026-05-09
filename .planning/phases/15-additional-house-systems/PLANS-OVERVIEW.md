# Phase 15 — Plans Overview

**Date :** 2026-05-09
**Phase :** Additional House Systems (Whole Sign + Equal + Regiomontanus)
**Plans :** 4 plans en 2 vagues (recommandation researcher §10 RESEARCH.md)
**Couverture :** HOU2-01..05 (5 requirements)

---

## Wave Structure

| Wave | Plan | Plan Name | Autonomous | Depends on | Parallelizable with |
|------|------|-----------|------------|------------|---------------------|
| **1** | 15-01 | foundation-snapshot-dtype-asc1 | yes | — | — |
| **2** | 15-02 | whole-sign-and-equal | yes | 15-01 | 15-03 |
| **2** | 15-03 | regiomontanus | yes | 15-01 | 15-02 |
| **2** | 15-04 | cli-integration-and-phase-gates | yes | 15-02, 15-03 | — |

**Vague 1 séquentielle (1 plan)** : pose la fondation (snapshot script, DTYPE bump, `_asc1` extraction, `SYSTEM_BYTES` étendu).

**Vague 2 (3 plans en pipeline + parallèle)** : Plans 15-02 et 15-03 parallèles ; Plan 15-04 finit après que les deux aient mergé.

```
                    Wave 1                          Wave 2
   ┌───────────────────────────────┐   ┌────────────────────────────────────┐
   │                               │   │                                    │
   │   15-01 (foundation)         ─┼───┼─►  15-02 (Whole Sign + Equal)  ────┼──┐
   │     • snapshot script         │   │                                    │  │
   │     • DTYPE U10 → U16         │   │                                    │  ▼
   │     • _asc1 → _ecliptic.py   ─┼───┼─►  15-03 (Regiomontanus)       ──► 15-04
   │     • SYSTEM_BYTES extend     │   │                                    │
   │                               │   │                                    │
   └───────────────────────────────┘   └────────────────────────────────────┘
                                                                          (CLI + gates,
                                                                           closes Phase 15)
```

---

## Plan Summaries

### Plan 15-01 — Foundation

**Wave :** 1 · **Tasks :** 6 · **Estimated context :** ~45%

**Requirements :** HOU2-05 (préparation snapshot pour gate end-to-end)

**Files modifiés :**
- `ketu/houses/core.py` (DTYPE U10 → U16)
- `ketu/houses/_ecliptic.py` (append `_asc1`)
- `ketu/houses/koch.py` (`from ._ecliptic import _asc1`)
- `tests/houses/conftest.py` (étendre `SYSTEM_BYTES`)
- `tests/houses/fixtures/reference_charts.json` (régénéré : 60 blocs)
- `scripts/snapshot_reference_charts.py` (nouveau)
- `tests/houses/test_oracle_smoke.py` (étendre 6 systèmes ligne 84)
- `tests/houses/test_dtype.py` (étendre `test_dtype_string_field_capacity`)
- `CHANGELOG.md` (entrée `[Unreleased] ### Changed`)

**Decisions verrouillées appliquées :**
- D-01 (DTYPE U10 → U16 + CHANGELOG)
- D-05 (extraction `_asc1`)
- D-06 (création `scripts/snapshot_reference_charts.py`)

**Ce que ce plan débloque :**
- Plan 15-02 et 15-03 peuvent tester end-to-end (snapshot étendu).
- Plan 15-03 peut importer `_asc1` depuis `_ecliptic.py`.
- Plan 15-04 peut afficher `regiomontanus` dans le CLI sans troncature de la string `system`.

---

### Plan 15-02 — Whole Sign + Equal

**Wave :** 2 · **Tasks :** 7 · **Estimated context :** ~50%

**Requirements :** HOU2-01 (Whole Sign), HOU2-02 (Equal)

**Files créés :**
- `ketu/houses/whole_sign.py` (~50 lignes prod + docstrings)
- `ketu/houses/equal.py` (~50 lignes prod + docstrings)
- `tests/houses/test_whole_sign.py` (~150 lignes ; 9 tests)
- `tests/houses/test_equal.py` (~140 lignes ; 9 tests)

**Files modifiés :**
- `ketu/houses/__init__.py` (append 2 trigger imports)
- `ketu/houses/api.py` (étendre `POLAR_SAFE_SYSTEMS`)
- `tests/houses/test_polar_safety.py` (append 2 tests no-NaN)

**Decisions verrouillées appliquées :**
- D-04 (un fichier par système)
- D-09 (helper internal naming non-breaking)

**Pitfalls couverts :**
- Pitfall 1 (polar swap order avant sign-floor)
- Pitfall 2 (trigger import `__init__.py`)
- Pitfall 3 (ASC = 0° boundary case)

**Divergences ratchet :**
- Whole Sign : `cusps[0]` = début du signe, NOT l'ASC
- Equal : `cusps[9]` = `(asc + 270) mod 360`, NOT l'astronomical MC

---

### Plan 15-03 — Regiomontanus

**Wave :** 2 · **Tasks :** 6 · **Estimated context :** ~45%

**Requirements :** HOU2-03 (Regiomontanus)

**Files créés :**
- `ketu/houses/regiomontanus.py` (~100 lignes prod + docstrings)
- `tests/houses/test_regiomontanus.py` (~210 lignes ; 12 tests)

**Files modifiés :**
- `ketu/houses/__init__.py` (append 1 trigger import)
- `tests/houses/test_polar_safety.py` (append 1 test ratchet polar NaN)
- `tests/houses/test_integration.py` (append 2 tests polar_fallback)

**Decisions verrouillées appliquées :**
- D-02 (polar Regio NaN style Koch, pas swap MC↔IC)
- D-04 (un fichier par système)
- D-05 (`_asc1` du Plan 15-01 réutilisé via `from ._ecliptic import _asc1`)

**Pitfalls couverts :**
- Pitfall 2 (trigger import)
- Pitfall 4 (pole height vs geographic latitude — variables explicitement nommées `pole_height_outer`/`pole_height_inner`)
- Pitfall 5 (`_asc1` callers OK via shared module)

**Tâche manuelle critique :** Task 5 (mesure empirique de la dérive Reykjavik et pinning de `REYKJAVIK_REGIO_TOL_ARCMIN`). Procédure inline dans le plan.

---

### Plan 15-04 — CLI integration et clôture des success criteria

**Wave :** 2 · **Tasks :** 7 · **Estimated context :** ~40%

**Requirements :** HOU2-04 (CLI listing), HOU2-05 (validation finale phase gates)

**Files modifiés :**
- `ketu/cli/parser.py` (`choices=sorted(SYSTEMS.keys())` dynamique)
- `ketu/cli/introspection.py` (3 entrées `_SYSTEM_DESCRIPTIONS`)
- `tests/cli/test_introspection.py` (étendre `TestListHouseSystems` + ratchet `every-system-has-description`)
- `tests/cli/test_houses_cmd.py` (inverser `test_invalid_system_rejected` ; étendre parametrize à 6 systèmes)

**Decisions verrouillées appliquées :**
- D-03 (CLI ordering alphabétique)
- D-07 (parser dispatcher dynamique)
- D-08 (inverser test legacy `test_invalid_system_rejected`)

**Pitfalls couverts :**
- Pitfall 7 (test legacy `test_invalid_system_rejected` — utiliser `nonexistent_xyz` au lieu de `regiomontanus`)

**Phase 15 success criteria fermés par ce plan :**

| Success criterion | Action |
|-------------------|--------|
| 1. Each system valid HOUSES_DTYPE; W/E polar-safe | Vérifié inline (Tasks 6-7) ; ratchet par tests Plans 15-02/03 |
| 2. CLI lists 6 systems alphabetically | Tasks 1-3 + ratchet `test_lists_registered_systems` |
| 3. 10-charts oracle gate per system | Régression de `test_loaded_reference_snapshot_matches_oracle` (Plan 15-01 étendu) + `test_*_algorithm_matches_oracle_armc` |
| 4. CLI prints 12 cusps for whole_sign | Task 7 vérification + `TestHousesCmdMatchesPythonAPI` parametré |

---

## Requirement Coverage Matrix

| Req ID | Plan(s) | Test ratchet |
|--------|---------|--------------|
| HOU2-01 (Whole Sign) | 15-02 | `test_whole_sign_*` (9 tests), `test_calculate_houses_routes_whole_sign` |
| HOU2-02 (Equal) | 15-02 | `test_equal_*` (9 tests), `test_calculate_houses_routes_equal` |
| HOU2-03 (Regiomontanus) | 15-03 | `test_regiomontanus_*` (12 tests), `test_polar_fallback_routes_regiomontanus_to_porphyry` |
| HOU2-04 (CLI 6 systems) | 15-04 | `TestListHouseSystems::test_lists_registered_systems` (étendu) |
| HOU2-05 (validation oracle) | 15-01 + 15-04 | `test_loaded_reference_snapshot_matches_oracle` (60 blocs) + `test_*_algorithm_matches_oracle_armc` (3 systèmes × 1e-6°) |

**Tous les 5 requirements ont au moins un test ratchet automatisé.**

---

## File Ownership (No Conflict Map)

| File | 15-01 | 15-02 | 15-03 | 15-04 |
|------|-------|-------|-------|-------|
| `ketu/houses/core.py` | ✏️ DTYPE | — | — | — |
| `ketu/houses/_ecliptic.py` | ✏️ append `_asc1` | — | — | — |
| `ketu/houses/koch.py` | ✏️ import `_asc1` | — | — | — |
| `ketu/houses/whole_sign.py` | — | 🆕 create | — | — |
| `ketu/houses/equal.py` | — | 🆕 create | — | — |
| `ketu/houses/regiomontanus.py` | — | — | 🆕 create | — |
| `ketu/houses/__init__.py` | — | ✏️ append 2 lines | ✏️ append 1 line | — |
| `ketu/houses/api.py` | — | ✏️ POLAR_SAFE | — | — |
| `ketu/cli/parser.py` | — | — | — | ✏️ dynamic choices |
| `ketu/cli/introspection.py` | — | — | — | ✏️ extend dict |
| `tests/houses/conftest.py` | ✏️ SYSTEM_BYTES | — | — | — |
| `tests/houses/fixtures/...json` | ✏️ regen | — | — | — |
| `tests/houses/test_dtype.py` | ✏️ extend | — | — | — |
| `tests/houses/test_oracle_smoke.py` | ✏️ extend | — | — | — |
| `tests/houses/test_polar_safety.py` | — | ✏️ append | ✏️ append | — |
| `tests/houses/test_integration.py` | — | — | ✏️ append | — |
| `tests/houses/test_whole_sign.py` | — | 🆕 create | — | — |
| `tests/houses/test_equal.py` | — | 🆕 create | — | — |
| `tests/houses/test_regiomontanus.py` | — | — | 🆕 create | — |
| `tests/cli/test_introspection.py` | — | — | — | ✏️ extend |
| `tests/cli/test_houses_cmd.py` | — | — | — | ✏️ extend |
| `scripts/snapshot_reference_charts.py` | 🆕 create | — | — | — |
| `CHANGELOG.md` | ✏️ append | — | — | — |

**Wave 2 conflit potentiel : `ketu/houses/__init__.py` est touché par Plans 15-02 ET 15-03.**

**Mitigation :** les modifications sont 100% append-only et disjointes (Plan 15-02 ajoute 2 lignes pour whole_sign/equal ; Plan 15-03 ajoute 1 ligne pour regiomontanus). Le merge git est trivial peu importe l'ordre. Aucun autre fichier n'est partagé entre les plans Wave 2.

---

## Validation Strategy (rappel VALIDATION.md)

- **Quick run** (per task) : `pytest tests/houses/ -x -v` (~30s)
- **Wave merge** : `pytest tests/ --cov=ketu.houses --cov-fail-under=95` (~90s)
- **Phase gate** : full suite + `numpydoc validate ketu/houses/` + `interrogate ketu/houses/ -f 95`

**Tolerance map (15-PATTERNS §12.6) :**
- Whole Sign / Equal : algorithm 1e-6° + end-to-end 1e-6° (arithmétique pure)
- Regiomontanus : algorithm 1e-6° + end-to-end 1 arcmin + Reykjavik pinned empirically
- Régression Phase 10 : Placidus/Koch/Porphyry inchangés à 1e-9° (snapshot v1.1 préservé)

---

## Sortie attendue post-Phase 15

- 6 systèmes enregistrés dans `SYSTEMS` registry au moment de `import ketu.houses`.
- 858+ tests verts (Phase 14 baseline 858 + nouveaux tests Phase 15 ~30).
- Coverage `ketu/houses/` ≥95 % project-wide.
- `ketu --list-house-systems` affiche les 6 noms triés alphabétiquement.
- `ketu houses --system <any-of-6>` calcule et formate les 12 cusps.
- Doc gates (OPS-01, OPS-02) verts.
- CHANGELOG `[Unreleased]` documente le DTYPE bump U10 → U16.
- Snapshot script `scripts/snapshot_reference_charts.py` réutilisable pour les futurs systèmes Campanus/Topocentric/Alcabitius (v1.3).

---

*— Sophie Chen, Lead Technical Architect*
*Plans rédigés 2026-05-09 — recommandation researcher §10 suivie*
