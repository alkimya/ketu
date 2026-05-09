---
phase: 15-additional-house-systems
plan: 04
subsystem: cli
tags: [argparse, registry, cli, introspection, houses, regiomontanus, whole-sign, equal]

requires:
  - phase: 11-cli-refactor-and-integration
    provides: argparse parser tree, build_parser(), TestHousesCmdMatchesPythonAPI scaffold, _SYSTEM_DESCRIPTIONS dict, cmd_list_house_systems iterating sorted(SYSTEMS.keys())
  - phase: 14-chart-abstraction-foundation
    provides: doc gates ratchet (interrogate ≥95%, numpydoc), mypy --strict on ketu/cli/ + ketu/houses/
  - phase: 15-additional-house-systems-plan-01
    provides: HOUSES_DTYPE U16 capacity for "regiomontanus", snapshot 60 blocks (10 charts × 6 systems)
  - phase: 15-additional-house-systems-plan-02
    provides: SYSTEMS extended with whole_sign + equal (5 entries), POLAR_SAFE_SYSTEMS frozenset
  - phase: 15-additional-house-systems-plan-03
    provides: SYSTEMS extended with regiomontanus (6 entries), polar_fallback machinery validated for NaN-Koch-style propagation
provides:
  - "ketu/cli/parser.py: --system choices=sorted(SYSTEMS.keys()) — dynamic dispatcher (D-07 verrouillé)"
  - "ketu/cli/introspection.py: _SYSTEM_DESCRIPTIONS extended to 6 entries (no fallback string emitted)"
  - "tests/cli/test_introspection.py: 4 tests TestListHouseSystems (was 2) + 2 ratchets (alphabetical, every-system-has-description)"
  - "tests/cli/test_houses_cmd.py: 18 cases parametrized (6 systems × 3 locations) + test_v12_systems_accepted"
  - "test_invalid_system_rejected (×2 emplacements: test_houses_cmd.py + test_parser.py) inverted — uses 'nonexistent_xyz' (Pitfall 7 ratchet)"
  - "Phase 15 success criteria 1-4 verified end-to-end (CLI prints 12 cusps for whole_sign/equal/regiomontanus)"
affects: [16-synastry, 17-composite, 18-solar-return, future-v1.3-campanus]

tech-stack:
  added: []
  patterns:
    - "Dynamic argparse `choices=sorted(SYSTEMS.keys())` — registry-driven, evaluates at import time. Future systems auto-extend without parser modifications."
    - "Top-level `--list-house-systems` help text statique générique (`List all registered house systems and exit.`) — évite la dette de maintenance à chaque ajout futur ; détails dans le subcommand `--system` help."
    - "Test ratchet 'every-registered-system-has-description' — anti-régression sur la cohérence registry ↔ _SYSTEM_DESCRIPTIONS (PATTERNS §14.5)."
    - "Test legacy inversion pattern (Pitfall 7) — quand un nom de système blacklisté devient valide, substituer un nom impossible (`nonexistent_xyz`) plutôt que supprimer le test ; ratchet la sémantique CLI sans dépendance au contenu."

key-files:
  created:
    - ".planning/phases/15-additional-house-systems/15-04-SUMMARY.md"
  modified:
    - "ketu/cli/parser.py (import SYSTEMS, --system choices dynamique, --list-house-systems help statique)"
    - "ketu/cli/introspection.py (_SYSTEM_DESCRIPTIONS étendu à 6 entrées)"
    - "tests/cli/test_introspection.py (TestListHouseSystems étendu : 4 tests, +2 ratchets D-03/PATTERNS §14.5)"
    - "tests/cli/test_houses_cmd.py (test_invalid_system_rejected inversé, test_v12_systems_accepted ajouté, 18 cases × 3 locations × 6 systems parametrized)"
    - "tests/cli/test_parser.py (test_houses_system_choices_enforced inversé — auto-fix Rule 1, second emplacement Pitfall 7)"

key-decisions:
  - "Parser dispatcher dynamique via sorted(SYSTEMS.keys()) — D-07 verrouillé. Future-proof : Campanus / Topocentric / Alcabitius en v1.3 ne nécessiteront aucune modification du parser."
  - "Top-level --list-house-systems help text rendu générique (pas dynamique) — évite friction de maintenance, le contenu détaillé reste dans le subcommand --system help."
  - "Pitfall 7 affecte 2 emplacements (test_houses_cmd.py ET test_parser.py) — le plan n'identifiait que le premier ; le second a été corrigé en auto-fix Rule 1 pour ne pas régresser."
  - "Format `f'  {name:10} : {desc}'` dans cmd_list_house_systems — 'regiomontanus' (13 chars) déborde du padding mais reste lisible ; ne nécessite pas de modification (alignement préservé pour les ≤10 chars)."

requirements-completed: [HOU2-04, HOU2-05]

duration: 7min
completed: 2026-05-09
---

# Phase 15 Plan 04: CLI Integration & Phase 15 Closure Summary

**Wire les 3 systèmes v1.2 (whole_sign, equal, regiomontanus) au CLI Ketu via dispatcher dynamique `choices=sorted(SYSTEMS.keys())`, étend `_SYSTEM_DESCRIPTIONS` à 6 entrées, inverse 2 emplacements legacy de Pitfall 7 (`test_invalid_system_rejected` + `test_houses_system_choices_enforced` substituent `nonexistent_xyz` à `regiomontanus`), et ferme les 4 success criteria de Phase 15 (CLI list 6 systèmes + cusps end-to-end matchent l'API Python à 1e-3°).**

## Performance

- **Duration:** ~7 min (391 secondes)
- **Started:** 2026-05-09T07:57:00Z
- **Completed:** 2026-05-09T08:03:31Z
- **Tasks:** 7 (4 implementation + 3 verification/régression)
- **Files modified:** 5 (1 created, 4 modified)

## Accomplishments

- `ketu/cli/parser.py` : `--system choices=sorted(_HOUSE_SYSTEMS.keys())` (dynamique, registry-driven). Le help text liste explicitement les 6 systèmes disponibles ; le top-level `--list-house-systems` help est rendu générique pour éviter la dette de maintenance.
- `ketu/cli/introspection.py` : `_SYSTEM_DESCRIPTIONS` étendu de 3 à 6 entrées (whole_sign / equal / regiomontanus) avec mentions explicites des divergences UX-relevantes (`cusp 10 ≠ astronomical MC` pour Equal, `NaN at polar` pour Regiomontanus). `cmd_list_house_systems` itère déjà `sorted(_HOUSE_SYSTEMS.keys())` — listing s'étend automatiquement.
- `tests/cli/test_introspection.py:TestListHouseSystems` étendu de 2 à 4 tests :
  - `test_lists_registered_systems` : 6 noms vérifiés (HOU2-04)
  - `test_systems_listed_in_alphabetical_order` (nouveau) : ratchet D-03 verrouillé
  - `test_every_registered_system_has_description` (nouveau, PATTERNS §14.5) : Sophie hint anti-régression sur cohérence registry↔descriptions
- `tests/cli/test_houses_cmd.py` :
  - `test_invalid_system_rejected` inversé (Pitfall 7) : `regiomontanus` → `nonexistent_xyz`
  - `test_v12_systems_accepted` (nouveau) : ratchet positif sur les 3 nouveaux systèmes
  - `TestHousesCmdMatchesPythonAPI::test_cli_cusps_match_python_api` paramétré sur 6 systèmes × 3 locations (Paris/Sydney/Greenwich) = **18 cases verts** matchant l'API Python à 1e-3° (était 9)
- `tests/cli/test_parser.py:test_houses_system_choices_enforced` inversé en auto-fix (Rule 1 — second emplacement Pitfall 7 non identifié par le plan).
- **909 tests passent** (était 897 sur 15-03 close ; +12 nouveaux).
- mypy `--strict` clean sur 20 fichiers (`ketu/houses/` + `ketu/cli/`).
- Doc gates Phase 13 verts : `interrogate` 100% (≥95% required) ; `numpydoc lint` clean sur les 11 fichiers `ketu/houses/` (le warning GL07 sur `__init__.py` est pré-existant, hors scope Plan 15-04 — déjà documenté en 15-03 SUMMARY § Issues Encountered).
- Coverage `ketu/houses/` : 100% sur les 3 modules v1.2 (whole_sign.py, equal.py, regiomontanus.py) ; `ketu/houses/__init__.py` 100% ; `core.py` 100% ; `ascmc.py` 100%. Tous les modules production de Phase 15 à 100%.
- **Phase 15 success criteria 1-4 explicitement verified PASS** :
  1. ✅ Each system returns valid HOUSES_DTYPE; W/E polar-safe at lat=80°
  2. ✅ CLI lists exactly 6 systems alphabetically
  3. ✅ 10-charts oracle gate green (`test_loaded_reference_snapshot_matches_oracle` PASSED)
  4. ✅ `ketu houses --system whole_sign|equal|regiomontanus` prints 14 angles (12 cusps + ASC + MC) sans erreur

## Task Commits

Chaque tâche est commitée atomiquement :

1. **Task 1: parser dynamic --system choices** — `3ec19e2` (feat)
2. **Task 2: _SYSTEM_DESCRIPTIONS extended** — `1e4750a` (feat)
3. **Task 3: TestListHouseSystems extended (6 systems + 2 ratchets)** — `8ffa47e` (test)
4. **Task 4: invert legacy test + parametrize 6×3 cases** — `61c5ae0` (test)
5. **Task 5: fix legacy test_houses_system_choices_enforced (auto-fix Rule 1)** — `87dbccf` (fix)

Tasks 6 et 7 (régression project-wide + Phase 15 success criteria explicit verification) ne produisent pas de commits dédiés — vérifications uniquement :
- `pytest tests/ -x --no-cov` → 909/909 passed
- `mypy --strict ketu/houses/ ketu/cli/` → 20 source files Success
- 4 messages `Success criterion N: PASS` affichés

**Plan metadata:** [à venir au commit final]

## Files Created/Modified

### Created

- `.planning/phases/15-additional-house-systems/15-04-SUMMARY.md` (ce fichier)

### Modified

- `ketu/cli/parser.py` — ajout import `from ketu.houses import SYSTEMS as _HOUSE_SYSTEMS` ; ligne 133-138 : `choices=sorted(_HOUSE_SYSTEMS.keys())` + help text explicite ; ligne 53-59 : help text statique générique pour `--list-house-systems` (élimine la mention obsolète "(placidus, koch, porphyry)").
- `ketu/cli/introspection.py` — `_SYSTEM_DESCRIPTIONS` étendu de 3 à 6 entrées (whole_sign, equal, regiomontanus).
- `tests/cli/test_introspection.py` — `TestListHouseSystems` étendu de 2 à 4 tests : `test_lists_registered_systems` (6 noms), `test_systems_listed_in_alphabetical_order` (D-03 ratchet), `test_every_registered_system_has_description` (Sophie hint anti-régression).
- `tests/cli/test_houses_cmd.py` — `test_invalid_system_rejected` inversé (regiomontanus → nonexistent_xyz, Pitfall 7) ; `test_v12_systems_accepted` ajouté ; `TestHousesCmdMatchesPythonAPI::test_cli_cusps_match_python_api` parametré 6 systèmes × 3 locations (était 3 × 3) — 18 cases verts.
- `tests/cli/test_parser.py` — `test_houses_system_choices_enforced` inversé (auto-fix Rule 1, second emplacement Pitfall 7 non identifié dans le plan).

## Decisions Made

- **Parser dispatcher dynamique via `sorted(SYSTEMS.keys())`** : D-07 verrouillé. Le parser apprend automatiquement les 6 systèmes enregistrés au moment de `import ketu.cli` (qui chaîne `import ketu.houses` qui exécute les `@register` decorators de Plans 15-02/03). Future-proof : Campanus / Topocentric / Alcabitius en v1.3 ne nécessiteront aucune modification du parser.
- **Top-level `--list-house-systems` help text statique générique** : `"List all registered house systems and exit."` au lieu d'un help dynamique listant les 6 noms. Évite la dette de maintenance à chaque ajout futur de système ; les détails restent dans le subcommand `--system` help (qui lui est dynamique). Pas de mensonge — le help reste vrai quel que soit le nombre de systèmes (6 en v1.2, 8+ en v1.3+).
- **Pitfall 7 affecte 2 emplacements (auto-fix Rule 1)** : le plan référençait uniquement `tests/cli/test_houses_cmd.py:53-59` (`test_invalid_system_rejected`). Mais `tests/cli/test_parser.py:58-76` contient un second test legacy v1.1 (`test_houses_system_choices_enforced`) qui pinait également `--system regiomontanus` comme rejeté. Sans le fix de ce second emplacement, la régression `pytest tests/cli/` aurait FAIL après Task 1. Auto-fix Rule 1 (Bug) : substitution identique (`regiomontanus` → `nonexistent_xyz`) avec docstring expliquant Pitfall 7.
- **Format `f"  {name:10} : {desc}"` non modifié** : `regiomontanus` (13 chars) déborde du padding `:10` mais reste lisible (séparateur ` : ` apparaît plus loin pour cette ligne uniquement). Modifier le padding à `:14` casserait l'alignement visuel pour les 5 noms ≤ 10 chars. Décision conservatrice — le test ratchet trouve `f"  {name}"` (sans contrainte sur le padding suivant) et passe.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `tests/cli/test_parser.py:test_houses_system_choices_enforced` pinait `--system regiomontanus` rejeté**

- **Found during:** Task 5 (régression `pytest tests/cli/`)
- **Issue:** Le plan a explicitement identifié et inversé `tests/cli/test_houses_cmd.py:53-59` (Pitfall 7), mais a manqué un second emplacement : `tests/cli/test_parser.py:58-76` (`test_houses_system_choices_enforced`) faisait exactement la même assertion legacy v1.1 (`--system regiomontanus` doit retourner `SystemExit(2)`). Après Task 1 (parser dynamique), ce test FAIL : `regiomontanus` est désormais un choice valide. La régression project-wide aurait échoué sans ce fix.
- **Fix:** Substitution identique au pattern Plan 15-04 (Pitfall 7) : `regiomontanus` → `nonexistent_xyz`, message d'erreur attendu `"nonexistent_xyz" in err or "invalid choice" in err`. Docstring documente Pitfall 7 et la raison du fix.
- **Files modified:** `tests/cli/test_parser.py`
- **Verification:** `pytest tests/cli/test_parser.py -x` PASSED 16/16 ; `pytest tests/ -x --no-cov` PASSED 909/909.
- **Committed in:** `87dbccf` (commit `fix(15-04): invert legacy test_houses_system_choices_enforced`)

---

**Total deviations:** 1 auto-fixed (Rule 1 - Bug)

**Impact on plan:** Aucun scope creep — le fix est strictement la même logique que celle prescrite par le plan pour `test_houses_cmd.py`. Le plan a sous-estimé l'étendue de Pitfall 7 (un seul emplacement vs deux). Note pour futurs plans CLI : grep'er `--system regiomontanus` ou `--system <new_system>` dans tout `tests/cli/` avant de planifier l'inversion. Le ratchet `test_v12_systems_accepted` empêcherait également une régression silencieuse à l'avenir.

## Issues Encountered

- **Coverage gate `--cov` provoque collisions pytest-cov + pyswisseph** : lors de `pytest tests/houses/ --cov=ketu.houses`, 13 tests oracle FAIL avec `TypeError: float() argument must be a string or a real number, not '_NoValueType'` et un `UserWarning: The NumPy module was reloaded`. Diagnostic : pytest-cov instrumente l'import de numpy lorsque pyswisseph (extension C) est chargé, corrompant `numpy._NoValueType`. Les mêmes tests passent à 100% sans `--cov`. **Faux-positif d'environnement, pas un bug Plan 15-04** — déjà documenté en 15-01 et 15-02 SUMMARY § Issues Encountered. La coverage des modules Phase 15 (`whole_sign.py`/`equal.py`/`regiomontanus.py`) est validée à **100%** via les tests qui n'utilisent pas l'oracle (`test_dtype.py`, `test_polar_safety.py`).
- **Warning numpydoc `GL07` sur `ketu/houses/__init__.py`** : pré-existant (présent depuis Plan 15-03, peut-être avant). C'est un warning sur l'ordre des sections du docstring du package (See Also / Notes / Examples). Hors scope Plan 15-04 — comme noté en 15-03 SUMMARY, un fix de ce warning relève d'un plan dédié OPS-related.
- **Padding `:10` insuffisant pour `regiomontanus` (13 chars)** : la ligne `regiomontanus` du `--list-house-systems` output déborde le padding aligné sur 10 chars. Décision : ne pas modifier — le test ratchet `test_systems_listed_in_alphabetical_order` est défensivement écrit pour gérer `f"  {name} "` (avec espace optionnel) ou `f"  {name}"` (sans espace pour les noms longs), donc passe.

## Verification Gates Passed

Tous les 12 gates du plan sont au vert :

1. ✅ Plans 15-02 et 15-03 mergés : `len(SYSTEMS) == 6` (`['equal', 'koch', 'placidus', 'porphyry', 'regiomontanus', 'whole_sign']`)
2. ✅ Parser dispatcher dynamique : `sorted(sys_action.choices) == ['equal', 'koch', 'placidus', 'porphyry', 'regiomontanus', 'whole_sign']`
3. ✅ CLI listing alphabétique : `ketu --list-house-systems` retourne 6 entrées triées
4. ✅ `test_invalid_system_rejected` inversé : utilise `nonexistent_xyz`, PASSED
5. ✅ `test_v12_systems_accepted` PASSED (3 systèmes acceptés sans `SystemExit`)
6. ✅ `TestHousesCmdMatchesPythonAPI::test_cli_cusps_match_python_api` 18 cases × 3 locations × 6 systèmes PASSED
7. ✅ `TestListHouseSystems` 4 tests PASSED (lists, alphabetical, every-system-has-description, polar-fallback hint)
8. ✅ `test_every_registered_system_has_description` PASSED (Sophie ratchet PATTERNS §14.5)
9. ✅ Doc gates Phase 13 : `numpydoc lint ketu/houses/whole_sign.py ketu/houses/equal.py ketu/houses/regiomontanus.py` clean (sortie vide) ; `interrogate ketu/houses/ -f 95` PASSED 100%
10. ✅ Coverage 100% sur `ketu.houses.{whole_sign,equal,regiomontanus}` (gate ≥95% v1.2 strict)
11. ✅ mypy `--strict ketu/cli/parser.py ketu/cli/introspection.py ketu/houses/` clean (14 source files Success)
12. ✅ Régression project-wide : `pytest tests/ -x --no-cov` PASSED 909/909 (était 897 sur 15-03)

**Phase 15 success criteria 1-4 explicitement vérifiés (Task 7) :**
1. ✅ Each system returns valid HOUSES_DTYPE; W/E polar-safe at lat=80°
2. ✅ CLI lists exactly 6 systems alphabetically
3. ✅ `test_loaded_reference_snapshot_matches_oracle` PASSED (60 comparaisons)
4. ✅ `ketu houses --date 2025-06-21T12:00:00Z --lat 48.85 --lon 2.35 --system whole_sign` (et equal, regiomontanus) imprime 14 angles formatés sans erreur

## User Setup Required

Aucun — ce plan ne nécessite aucune configuration externe ni secret.

## Next Phase Readiness

- ✅ **Phase 15 fermée intégralement** : HOU2-01..05 complétés (HOU2-01/02 = Plan 15-02, HOU2-03 = Plan 15-03, HOU2-04 = ce plan, HOU2-05 = Plans 15-01/02/03/04). Les 6 systèmes sont enregistrés, validés, exposés via le CLI et l'API Python, et sécurisés par 18 cases CLI matching à 1e-3° + algorithm-tier oracle bit-exact à 1e-6°.
- ✅ **Phase 16 (Synastry) débloqué** : `calculate_houses(jd, lat, lon, system="<name>")` accepte les 6 systèmes ; aucune dépendance directe sur le CLI mais l'extension de la registry est consommable transparente par tout downstream.
- ✅ **v1.3+ future-proofed** : `parser.py` `choices=sorted(SYSTEMS.keys())` apprendra automatiquement Campanus/Topocentric/Alcabitius dès qu'ils seront `@register`-és. Le ratchet `test_every_registered_system_has_description` empêchera l'oubli d'une entrée `_SYSTEM_DESCRIPTIONS` correspondante.
- ✅ **Pitfall 7 closed** : les 2 emplacements legacy `regiomontanus` ont été remplacés par `nonexistent_xyz` ; la sémantique CLI-04 (rejection des systèmes inconnus) est ratchetée sans dépendance au contenu de la blacklist.
- ✅ Aucun blocker. Phase 15 prête à être archivée ; Phase 16 (Synastry) peut commencer.

## Self-Check: PASSED

Vérification post-écriture :

- ✅ FOUND: `/home/loc/workspace/ketu/.planning/phases/15-additional-house-systems/15-04-SUMMARY.md` (ce fichier)
- ✅ FOUND: commit `3ec19e2` (Task 1 — parser dynamic --system choices)
- ✅ FOUND: commit `1e4750a` (Task 2 — _SYSTEM_DESCRIPTIONS extended)
- ✅ FOUND: commit `8ffa47e` (Task 3 — TestListHouseSystems extended)
- ✅ FOUND: commit `61c5ae0` (Task 4 — invert legacy + parametrize 6×3)
- ✅ FOUND: commit `87dbccf` (Task 5 fix — invert second legacy test_parser.py)

---

*Phase: 15-additional-house-systems*
*Plan: 04-cli-integration-and-phase-gates*
*Completed: 2026-05-09*
