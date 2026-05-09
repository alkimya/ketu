---
phase: 15-additional-house-systems
plan: 03
subsystem: houses
tags: [numpy, swisseph, houses, regiomontanus, polar-fallback, registry, asc1]

requires:
  - phase: 10-houses-module
    provides: SYSTEMS registry, @register decorator, HouseSystemFn signature, polar_fallback machinery in calculate_houses, koch.py NaN-propagation pattern
  - phase: 14-chart-abstraction-foundation
    provides: doc gates (interrogate >=95%, numpydoc validate), mypy --strict on ketu/houses/
  - phase: 15-additional-house-systems-plan-01
    provides: HOUSES_DTYPE U16 capacity for "regiomontanus" (13 chars), _asc1 helper in _ecliptic.py (consumed via from ._ecliptic import _asc1), SYSTEM_BYTES extended with R, snapshot regen with regiomontanus block per chart
  - phase: 15-additional-house-systems-plan-02
    provides: __init__.py with whole_sign + equal trigger imports (regiomontanus appended below)
provides:
  - "ketu.houses.regiomontanus.regiomontanus_cusps (closed-form trig per swehouse.c case 'R'; NaN at polar boundary)"
  - "SYSTEMS registry now includes 'regiomontanus' at import time (6 systems total)"
  - "Algorithm-tier oracle bit-exact (1e-6) for regiomontanus across 8 non-polar reference charts"
  - "End-to-end snapshot match within 1 arcmin on 7 tight non-polar charts"
  - "Reykjavik tolerance pinned empirically at 1.0' (measured 0.86' on 2026-05-09)"
  - "Polar-safety ratchet: NaN at |lat| >= 90 - eps_mean(jd); polar_fallback='porphyry' routes correctly"
  - "Pitfall 4 ratchet: _asc1 callers explicitly named pole_height_outer_deg / pole_height_inner_deg"
affects: [15-04-cli-integration, 16-synastry, 17-composite, 18-solar-return]

tech-stack:
  added: []
  patterns:
    - "Pole-height naming convention (pole_height_outer / pole_height_inner) as visual ratchet against Pitfall 4 (geographic latitude vs pole height substitution)"
    - "Empirical Reykjavik tolerance pinning workflow: measure with -s flag, choose tolerance per decision-tree, document measurement date inline"
    - "Closed-form trig with polar-NaN propagation pattern reused from koch.py (mirror of structure: ASC/MC closed-form, polar mask, _asc1 calls, opposites 180, np.where masking)"

key-files:
  created:
    - "ketu/houses/regiomontanus.py (154 lignes)"
    - "tests/houses/test_regiomontanus.py (293 lignes)"
    - ".planning/phases/15-additional-house-systems/15-03-SUMMARY.md"
  modified:
    - "ketu/houses/__init__.py (append 1 trigger import for regiomontanus)"
    - "tests/houses/test_polar_safety.py (append regiomontanus polar-NaN ratchet)"
    - "tests/houses/test_integration.py (append 2 polar_fallback tests for regiomontanus)"

key-decisions:
  - "REYKJAVIK_REGIO_TOL_ARCMIN pinned at 1.0' rather than 1.5' (margin 0.5') because measured drift (0.86') falls in the < 1' bucket of the plan's decision-tree — Plan 15-03 strictly specifies 1.0' for this case"
  - "Pole-height variables named explicitly (pole_height_outer / pole_height_inner) and the grep ratchet 'grep _asc1 ketu/houses/regiomontanus.py | grep -v pole_height_(outer|inner)_deg' enforces no _asc1 call ever receives raw geographic latitude (Pitfall 4)"
  - "Regiomontanus follows Koch's NaN-propagation pattern at polar boundary (D-02 in 15-CONTEXT.md), NOT swisseph's MC<->IC swap — preserves v1.1 polar contract consistency across all NaN-emitting systems (placidus + koch + regiomontanus)"
  - "No api.py modification: existing polar_fallback machinery (api.py:147-167) routes Regiomontanus' NaN cusps to Porphyry automatically because is_polar/np.where logic is system-agnostic; verified by 2 dedicated integration tests"
  - "MAX_ITER=50 / TOL_DEG=1e-7 constants kept for API parity with Placidus tests even though Regio is closed-form (matches Koch's existing parity convention)"

requirements-completed: [HOU2-03]

duration: 7min
completed: 2026-05-09
---

# Phase 15 Plan 03: Regiomontanus House System Summary

**Closed-form trig Regiomontanus cusps (HOU2-03) per swisseph swehouse.c case 'R': 4 non-trivial cusps (11/12/2/3) via shared _asc1 helper with pole heights fh1=atan(tan(lat)/2) and fh2=atan(tan(lat)*cos(30°)); NaN at |lat|>=90-eps Koch-style; Reykjavik drift measured at 0.86' and pinned at 1.0'. SYSTEMS registry passes from 5 to 6 entries.**

## Performance

- **Duration:** ~7 min
- **Started:** 2026-05-09T07:43:11Z
- **Completed:** 2026-05-09T07:50:35Z
- **Tasks:** 6 (5 implementation + 1 régression complète)
- **Files modified:** 5 (2 créés, 3 modifiés)

## Accomplishments

- `ketu/houses/regiomontanus.py` créé (154 lignes) : closed-form trig per swisseph `swehouse.c` case `'R'`. Les 4 cusps non triviaux (11/12/2/3) sont calculés via `_asc1` partagé (Plan 15-01) avec pole heights nommés explicitement `pole_height_outer_deg` (cusps 11/3) et `pole_height_inner_deg` (cusps 12/2) — ratchet visuel anti-Pitfall 4. Cusps 5/6/8/9 dérivés par opposites 180. Polar mask `|lat| >= 90 - eps_mean(jd)` propage NaN Koch-style (D-02 verrouillé), JAMAIS de swap MC<->IC.
- `ketu/houses/__init__.py` : 1 trigger import ajouté (`from . import regiomontanus`) ; `import ketu.houses` peuple désormais SYSTEMS avec 6 entrées (était 5).
- `tests/houses/test_regiomontanus.py` créé (293 lignes, 16 tests) : algorithm-tier oracle vs `swe_oracle_armc` à `1e-6°` sur 8 charts non-polaires (Greenwich, Paris, Sydney, Tokyo, Buenos Aires, Equator, 1900 NewYork, Reykjavik), end-to-end snapshot à 1 arcmin sur 7 charts tight (parametrized), Reykjavik drift mesuré et pinné à 1.0' (mesure 0.86'), polar contract (NaN above polar circle, all-NaN at lat=80°, no silent NaN at mid-latitudes), cusps 5/6/8/9 = opposites 180° de 11/12/2/3, constants parity (MAX_ITER=50, TOL_DEG=1e-7), vectorisation (4 charts batch), registry registration (case-insensitive lookup).
- `tests/houses/test_polar_safety.py` étendu : test `test_regiomontanus_yields_nan_above_polar_circle_in_safety_suite` ajouté à côté de Whole Sign / Equal (Plan 15-02) — 11 tests désormais (était 10).
- `tests/houses/test_integration.py` étendu : 2 nouveaux tests polar_fallback dédiés à Regiomontanus (`test_polar_fallback_routes_regiomontanus_to_porphyry`, `test_polar_fallback_raise_for_regiomontanus`) qui vérifient que la machinery existante d'`api.py` (lignes 147-167) route automatiquement les NaN Regio vers Porphyry — aucune modification d'`api.py` requise pour HOU2-03.
- Régression complète : `pytest tests/houses/ -x` passe **195/195** (était 176 sur 15-02 ; +19 nouveaux). `pytest tests/ -x` passe **897/897** (était 878 ; +19 nouveaux).
- Coverage `regiomontanus.py` : **100%** (gate >=95% strict).
- mypy `--strict` clean sur `ketu/houses/` (12 source files Success).
- numpydoc lint clean sur `ketu/houses/regiomontanus.py` ; interrogate `ketu/houses/regiomontanus.py -f 95` PASSED 100%.
- Pitfall 4 grep ratchet : `grep _asc1 ketu/houses/regiomontanus.py | grep -v pole_height_(outer|inner)_deg` retourne 0 lignes (chaque appel `_asc1` reçoit explicitement un pole height nommé).

## Task Commits

Chaque tâche est commitée atomiquement :

1. **Task 1: ketu/houses/regiomontanus.py** — `b38317c` (feat)
2. **Task 2: __init__.py trigger import regiomontanus** — `fe84adf` (feat)
3. **Task 3: tests/houses/test_regiomontanus.py** — `9e1fbb2` (test)
4. **Task 4: extend test_polar_safety + test_integration** — `1395a4f` (test)
5. **Task 5: pin REYKJAVIK_REGIO_TOL_ARCMIN to 1.0' (measured 0.86')** — `e8a43b6` (test)

Task 6 (régression complète) ne produit pas de commit dédié — c'est une vérification : `pytest tests/houses/ -x` passe 195/195, `pytest tests/ -x` passe 897/897.

**Plan metadata:** [à venir au commit final]

## Files Created/Modified

### Created

- `ketu/houses/regiomontanus.py` (154 lignes) — closed-form trig per swisseph swehouse.c case 'R' ; pole-height variables nommés ; polar mask + np.where NaN propagation ; @register("regiomontanus") decorator ; MAX_ITER/TOL_DEG kept for parity.
- `tests/houses/test_regiomontanus.py` (293 lignes, 16 tests) — algorithm-tier oracle (1e-6°), end-to-end snapshot (1 arcmin × 7 charts, parametrized), Reykjavik drift measured (0.86', pinned 1.0'), polar contract (3 tests), cusp opposites 180, constants parity, vectorisation, registry.

### Modified

- `ketu/houses/__init__.py` — append `from . import regiomontanus  # noqa: F401  registers 'regiomontanus' in SYSTEMS` à la suite des 5 trigger imports existants (placidus, koch, porphyry, whole_sign, equal). 1 ligne ajoutée.
- `tests/houses/test_polar_safety.py` — append `test_regiomontanus_yields_nan_above_polar_circle_in_safety_suite` après le test `test_equal_does_not_yield_nan_above_polar_circle`.
- `tests/houses/test_integration.py` — append `test_polar_fallback_routes_regiomontanus_to_porphyry` et `test_polar_fallback_raise_for_regiomontanus` avant `test_calculate_houses_system_field_preserved_under_fallback`.

## Decisions Made

- **REYKJAVIK_REGIO_TOL_ARCMIN pinned at 1.0'** : la mesure empirique a donné 0.8581 arcmin (per-cusp max), bien sous l'estimation 15-RESEARCH §14.3 de 2-5 arcmin. Le plan stipule clairement « < 1 arcmin → Pinner = 1.0 * ARCMIN_DEG ». Marge de sûreté implicite : 0.14' contre dérive future. Si une régénération du snapshot pousse au-dessus de 1', une nouvelle mesure déterminera s'il faut tighten ou relax — interdit de blanket-relax sans mesure.
- **Pole-height naming as visual ratchet** : les variables `pole_height_outer_deg` et `pole_height_inner_deg` (au lieu de `fh1` / `fh2` ou un calcul inline) servent de marqueur visuel pour le grep gate : tout appel `_asc1` qui ne contiendrait pas l'un de ces deux noms serait flaggé comme bug. Cela protège contre la substitution accidentelle `_asc1(armc + 30, lat_b, ...)` (utilisation de la latitude géographique au lieu de la pole height — Pitfall 4 du 15-RESEARCH §11).
- **Koch-style NaN propagation, NOT swisseph swap** : à `|lat| >= 90 - eps`, le code retourne NaN sur les 12 cusps (mirror du pattern koch.py:128-131) ; le swap MC<->IC du C source de swisseph est explicitement écarté pour préserver la cohérence v1.1 (D-02 verrouillé en 15-CONTEXT.md). Le mécanisme `polar_fallback="porphyry"` d'`api.py:147-167` route ces NaN vers Porphyry sans aucune modification du code dispatch — vérifié par les 2 tests d'intégration ajoutés.
- **Aucune modification d'`api.py`** : la registry-based dispatch + le `np.where` polar_mask masking d'`api.py` sont system-agnostic. Ajouter Regiomontanus ne requiert aucune modification du dispatch — démontre la robustesse du pattern HOU-02 + HOU-06 mis en place en Phase 10.
- **MAX_ITER=50 / TOL_DEG=1e-7 constants kept for parity** : Regiomontanus est closed-form (pas d'itération) mais les constants sont préservées pour matcher le pattern Koch existant ; documenté dans le docstring comme « reserved for future iterative variants ». Test `test_regiomontanus_constants_unchanged` ratchet ces valeurs.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `np.float64(...)` violerait `mypy --strict` (même problème que Plan 15-02)**

- **Found during:** Task 3 (création de `test_regiomontanus.py`)
- **Issue:** Le plan inclut littéralement `regiomontanus_cusps(np.float64(armc), ...)` dans plusieurs tests. La signature `HouseSystemFn = Callable[[np.ndarray, np.ndarray, np.ndarray], np.ndarray]` typée ndarray-strict ; mypy `--strict` rejette `np.float64(x)` (scalaire numpy distinct du ndarray 0-D). Le même bug avait été corrigé en Plan 15-02 (cf 15-02-SUMMARY.md déviation #1).
- **Fix:** Substituer `np.float64(x)` → `np.asarray(x, dtype=np.float64)` à 7 emplacements dans `test_regiomontanus.py` (algorithm-tier oracle, snapshot tier, Reykjavik test, polar tests × 3, cusps opposites, vectorisation scalar inner loop). Approche identique à 15-02.
- **Files modified:** `tests/houses/test_regiomontanus.py`
- **Verification:** `mypy --strict ketu/houses/regiomontanus.py` PASSED ; tous les 16 tests verts.
- **Committed in:** `9e1fbb2` (Task 3 commit, intégré directement)

---

**Total deviations:** 1 auto-fixed (1 latent bug du plan rendu visible par le gate `mypy --strict` Phase 13). Aucune Rule 4 (architecturale) déclenchée.

**Impact on plan:** Aucun scope creep. Le fix est strictement nécessaire pour satisfaire le gate `mypy --strict ketu/houses/` (Phase 14 ratchet). Le plan suggérait littéralement le pattern `np.float64(...)` qui était une erreur héritée du Plan 15-02 — corrigée par la même substitution éprouvée.

## Issues Encountered

- **Stash pop accidentel pendant le diagnostic numpydoc** : pendant l'exécution du gate `numpydoc lint ketu/houses/__init__.py` (qui retournait un warning `GL07 Sections wrong order`), j'ai utilisé `git stash` pour vérifier que ce warning était pré-existant. Le `git stash` initial était vide (pas de changements à stasher), mais le `git stash pop` consécutif a démanqué le stash `stash@{0}: pre-release-merge: unrelated phase09/11 plan drift` (préexistant en STATE.md ligne 78, hors scope v1.2). Résultat : 8 fichiers en conflit `UU`/`DU` sur `.planning/phases/09-*` et `.planning/phases/11-*`. Résolution : `git rm` des 7 fichiers `DU` (déjà supprimés de HEAD) + `git checkout HEAD -- .planning/config.json` pour le seul `UU`. Vérifié post-résolution : `git diff --staged --stat` vide, fichiers Plan 15-03 intacts (vérifié via `grep "from . import" ketu/houses/__init__.py` qui retourne les 6 trigger imports attendus). **Aucun fichier Plan 15-03 affecté ; aucun commit perdu.**
- **Warning `GL07` numpydoc sur `ketu/houses/__init__.py`** : pré-existant (présent même avant Plan 15-03). C'est un warning sur l'ordre des sections du docstring du package (See Also / Notes / Examples). Hors scope Plan 15-03 — ni 15-01 ni 15-02 ne l'ont fixé. Si l'on souhaite y remédier, ce serait un plan dédié OPS-related (préférablement Phase 13 doc gates).
- **Coverage gate global `--cov-fail-under=70.0` faux-positif sur run partiel** : exactement comme 15-01 et 15-02 (cf SUMMARY.md), le coverage gate du pyproject mesure tout `ketu/` mais ne lance que `tests/houses/test_regiomontanus.py`. La coverage cible (regiomontanus.py = 100%) est respectée ; régression complète `pytest tests/ -x` passe 897/897 sans gate de coverage.

## Verification Gates Passed

Tous les 16 gates du plan sont au vert :

1. ✅ Plan 15-01 mergé : `_asc1` accessible via `from ._ecliptic import _asc1`
2. ✅ Regiomontanus enregistré : `'regiomontanus' in SYSTEMS` (6 entrées)
3. ✅ Algorithm-tier oracle bit-exact 1e-6° sur 8 charts non-polaires
4. ✅ End-to-end snapshot 1 arcmin sur 7 charts tight (parametrized 7/7 PASSED)
5. ✅ Reykjavik drift mesuré et pinned (0.8581' max, pinné à 1.0')
6. ✅ Polar contract : NaN above polar circle (`test_yields_nan_above_polar_circle`), all-NaN at lat=80° (`test_polar_lat_80_yields_all_nan`), no silent NaN at mid-latitudes (`test_no_silent_nan_at_mid_latitudes`)
7. ✅ Cusps 5/6/8/9 = opposites 180° de 11/12/2/3 (1e-9° tolérance)
8. ✅ polar_fallback integration : `test_polar_fallback_routes_regiomontanus_to_porphyry` + `test_polar_fallback_raise_for_regiomontanus` PASSED
9. ✅ Vectorisation : `test_regiomontanus_vectorised_matches_scalar_per_element` PASSED (4-batch matches 4 scalars)
10. ✅ Registry : `'regiomontanus' in SYSTEMS`, `get_system('REGIOMONTANUS')` retourne `regiomontanus_cusps`
11. ✅ Régression complète : `pytest tests/houses/ -x` passe 195/195 ; `pytest tests/ -x` passe 897/897
12. ✅ Coverage 100% sur `ketu/houses/regiomontanus.py` (gate >=95%)
13. ✅ mypy `--strict ketu/houses/` clean (12 source files, Success no issues found)
14. ✅ Doc gates : `numpydoc lint ketu/houses/regiomontanus.py` clean (sortie vide) ; `interrogate ketu/houses/regiomontanus.py -f 95` PASSED 100%
15. ✅ AGPL boundary : `ketu.houses.regiomontanus` n'expose aucun symbole `swe*`
16. ✅ Pitfall 4 grep ratchet : `grep _asc1 ketu/houses/regiomontanus.py | grep -v pole_height_(outer|inner)_deg` retourne 0 lignes

## User Setup Required

Aucun — ce plan ne nécessite aucune configuration externe ni secret.

## Next Phase Readiness

- ✅ **Plan 15-04 (CLI integration) débloqué** : `sorted(SYSTEMS.keys())` retourne désormais `['equal', 'koch', 'placidus', 'porphyry', 'regiomontanus', 'whole_sign']` (6 entrées). CLI `--list-house-systems` et `--system` choices fonctionneront dynamiquement avec la nouvelle entrée Regiomontanus. Le test legacy `tests/cli/test_houses_cmd.py:53-59` (qui assertait `--system regiomontanus` rejeté en v1.1) reste à inverser en Plan 15-04.
- ✅ **HOU2-01..03 complétés** : Whole Sign (15-02), Equal (15-02) et Regiomontanus (15-03) — les 3 nouveaux house systems requirements de Phase 15 sont livrés. HOU2-04 (CLI) et HOU2-05 (snapshot foundation, déjà partiellement en 15-01) restent pour Plan 15-04.
- ✅ **Phase 15 Wave 2 progresse** : 15-02 + 15-03 livrés en parallèle (no merge conflict — 15-02 a ajouté 2 trigger imports `whole_sign` + `equal`, 15-03 ajoute la 6e ligne `regiomontanus` à la suite ; append-only).
- ✅ **API contract v1.1 préservé** : aucune modification d'`api.py`, `core.py`, `registry.py`, `_ecliptic.py` ; les 3 nouveaux fichiers de Phase 15 (whole_sign.py, equal.py, regiomontanus.py) sont indépendants additifs.
- ✅ Aucun blocker. Phase 15 prête pour Plan 15-04 (CLI integration finale).

## Self-Check: PASSED

Vérification post-écriture :

- ✅ FOUND: `/home/loc/workspace/ketu/ketu/houses/regiomontanus.py`
- ✅ FOUND: `/home/loc/workspace/ketu/tests/houses/test_regiomontanus.py`
- ✅ FOUND: `/home/loc/workspace/ketu/.planning/phases/15-additional-house-systems/15-03-SUMMARY.md` (ce fichier)
- ✅ FOUND: commit `b38317c` (Task 1)
- ✅ FOUND: commit `fe84adf` (Task 2)
- ✅ FOUND: commit `9e1fbb2` (Task 3)
- ✅ FOUND: commit `1395a4f` (Task 4)
- ✅ FOUND: commit `e8a43b6` (Task 5)

---

*Phase: 15-additional-house-systems*
*Plan: 03-regiomontanus*
*Completed: 2026-05-09*
