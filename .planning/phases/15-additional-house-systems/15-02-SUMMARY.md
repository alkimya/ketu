---
phase: 15-additional-house-systems
plan: 02
subsystem: houses
tags: [numpy, swisseph, houses, whole-sign, equal, polar-safe, registry]

requires:
  - phase: 10-houses-module
    provides: SYSTEMS registry, @register decorator, HouseSystemFn signature, Porphyry-style closed-form ASC + polar swap pattern
  - phase: 14-chart-abstraction-foundation
    provides: doc gates (interrogate ≥95%, numpydoc validate), mypy --strict on ketu/houses/
  - phase: 15-additional-house-systems-plan-01
    provides: HOUSES_DTYPE U16 (already accommodates 'whole_sign'/'equal' which are < 16 chars but the bump was for regiomontanus), SYSTEM_BYTES extended with W/E/R, oracle ratchet covering 6 systems
provides:
  - "ketu.houses.whole_sign.whole_sign_cusps (closed-form sign-floor; polar-safe)"
  - "ketu.houses.equal.equal_cusps (closed-form ASC-anchored 30° spacing; polar-safe)"
  - "POLAR_SAFE_SYSTEMS frozenset in api.py = {porphyry, whole_sign, equal}"
  - "SYSTEMS registry now includes 'whole_sign' and 'equal' at import time"
  - "Algorithm-tier oracle bit-exact (1e-6°) for whole_sign + equal across 10 reference charts including polar (lat=70°/80°)"
  - "Convention-divergence ratchets: cusps[0]=floor(asc/30)*30 for whole_sign; cusps[9]=(asc+270)%360 for equal"
  - "Polar-safety ratchets: no NaN at lat=70°/80°/89° for both new systems"
affects: [15-03-regiomontanus, 15-04-cli-integration, 16-synastry, 17-composite, 18-solar-return]

tech-stack:
  added: []
  patterns:
    - "POLAR_SAFE_SYSTEMS frozenset at module-top of api.py — extensible polar gate carve-out (was hardcoded singular 'porphyry' string in v1.1)"
    - "Closed-form polar-safe house system pattern: copy Porphyry skeleton, replace stack with sign-floor / 30°-anchored offsets; reuse pre-floor polar ASC swap"
    - "numpydoc-canonical Notes section for narrative caveats (avoid custom 'Caveat ---' headers — numpydoc lint rejects unknown sections)"

key-files:
  created:
    - "ketu/houses/whole_sign.py"
    - "ketu/houses/equal.py"
    - "tests/houses/test_whole_sign.py"
    - "tests/houses/test_equal.py"
    - ".planning/phases/15-additional-house-systems/15-02-SUMMARY.md"
  modified:
    - "ketu/houses/__init__.py (append 2 trigger imports for whole_sign + equal)"
    - "ketu/houses/api.py (introduce POLAR_SAFE_SYSTEMS frozenset; replace singular 'porphyry' polar-gate carve-out)"
    - "tests/houses/test_polar_safety.py (append no-NaN tests for whole_sign + equal at polar latitudes)"

key-decisions:
  - "POLAR_SAFE_SYSTEMS as a module-top frozenset (not a hardcoded string list nor a sub-method check) — extensible by future systems (Campanus / Topocentric will add themselves) and trivially auditable"
  - "Both new modules mirror Porphyry's pre-floor polar ASC swap (acmc_signed < 0 → asc += 180°) BEFORE the sign-floor / 30°-spacing build (Pitfall 1: swap-before-floor preserves antipodal-quadrant agreement with swisseph at high latitudes)"
  - "Move the narrative 'Caveat ---' divergence sections in module docstrings under a numpydoc-canonical Notes header — keeps `numpydoc lint` clean while preserving the explanatory content (was emitting GL06/GL07 unknown-section warnings on first authoring)"
  - "Test files use np.asarray(..., dtype=np.float64) (NOT np.float64(...)) for scalar inputs to whole_sign_cusps/equal_cusps — the HouseSystemFn signature contract types its arguments as np.ndarray, which mypy --strict enforces. np.float64 is a numeric scalar, not an ndarray."

requirements-completed: [HOU2-01, HOU2-02]

duration: 8min
completed: 2026-05-09
---

# Phase 15 Plan 02: Whole Sign + Equal house systems Summary

**Deux house systems closed-form polar-safe livrés en parallèle dans un seul plan : Whole Sign (cusps[0] = début du signe contenant l'ASC) et Equal ASC-anchored (cusps[9] = (asc+270)%360 ≠ MC astronomique). Les deux partagent le même profil mathématique trivial (Porphyry skeleton + sign-floor / 30°-spacing), polar-safe par construction sans fallback. SYSTEMS registry passe de 3 à 5 entrées.**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-05-09T07:29:19Z
- **Completed:** 2026-05-09T07:37:27Z
- **Tasks:** 7 (4 implémentation + 3 tests, tous commités atomiquement)
- **Files modified:** 7 (4 créés, 3 modifiés)

## Accomplishments

- `ketu/houses/whole_sign.py` créé (115 lignes) : closed-form sign-floor via `floor(asc/30)*30`, mirror swisseph case `'W'` ; polar-safe par construction (aucune dépendance latitudinale dans le sign-floor au-delà de l'ASC closed-form).
- `ketu/houses/equal.py` créé (96 lignes) : closed-form ASC-anchored 30° spacing via `(asc + 30k) mod 360`, mirror swisseph case `'E'` ; polar-safe par construction. `cusps[9] = (asc+270)%360`, divergent de l'astro MC (HOU2-02 contract ASC-anchored vs `'D'` MC-anchored reporté v1.3).
- `ketu/houses/__init__.py` : 2 trigger imports ajoutés (`from . import whole_sign / equal`) ; `import ketu.houses` peuple désormais SYSTEMS avec 5 entrées (était 3).
- `ketu/houses/api.py` : nouveau `POLAR_SAFE_SYSTEMS = frozenset({"porphyry", "whole_sign", "equal"})` au module-top ; le polar gate `any_polar = polar_mask.any() and system_lower not in POLAR_SAFE_SYSTEMS` remplace la check singulière `system_lower != "porphyry"` de v1.1. `calculate_houses(jd, 80, 0, system="whole_sign")` ne lève plus `HighLatitudeError` (HOU2-01 contract).
- `tests/houses/test_whole_sign.py` créé (9 tests, 207 lignes) : algorithm-tier oracle vs `swe.houses_armc` à 1e-6° sur les 10 reference charts (incluant polar 70°/80°), polar safety, 30°-spacing, sign-floor convention, Pitfall 3 (ASC=0° boundary), registry, vectorisation, end-to-end via `calculate_houses`.
- `tests/houses/test_equal.py` créé (9 tests, 189 lignes) : algorithm-tier oracle, polar safety, 30°-spacing, `cusps[0]=asc` convention, **cusps[9]=(asc+270)%360 ≠ astro MC** (HOU2-02 ratchet, divergence > 1° à Paris J2000), registry, vectorisation, end-to-end.
- `tests/houses/test_polar_safety.py` étendu : 2 nouveaux tests no-NaN pour whole_sign et equal à lat=70°/80°/89° (était 8 tests, désormais 10).
- Régression complète : `pytest tests/houses/ -x` passe **176/176** (était 156 ; +20 nouveaux). `pytest tests/ -x` passe **878/878** (était 858 ; +20 nouveaux).
- mypy `--strict` clean sur les 3 fichiers Python prod modifiés (`whole_sign.py`, `equal.py`, `api.py`).
- `numpydoc lint` clean ; `interrogate` 100% sur les 2 nouveaux modules.

## Task Commits

Chaque tâche est commitée atomiquement :

1. **Task 1: ketu/houses/whole_sign.py** — `891c54e` (feat)
2. **Task 2: ketu/houses/equal.py** — `c656855` (feat)
3. **Task 3: __init__.py trigger imports whole_sign + equal** — `d06207b` (feat)
4. **Task 4: api.py POLAR_SAFE_SYSTEMS frozenset** — `e7852c4` (feat)
5. **Task 5: tests/houses/test_whole_sign.py** — `127a1bc` (test) — inclut un fix numpydoc-canonical Notes section dans whole_sign.py
6. **Task 6: tests/houses/test_equal.py** — `b4d1903` (test) — inclut un fix numpydoc-canonical Notes section dans equal.py
7. **Task 7: tests/houses/test_polar_safety.py extension** — `645eba3` (test)

## Files Created/Modified

### Created

- `ketu/houses/whole_sign.py` (115 lignes) — closed-form sign-floor via `floor(asc/30)*30` ; pre-floor polar ASC swap (Pitfall 1) ; polar-safe par construction.
- `ketu/houses/equal.py` (96 lignes) — closed-form ASC-anchored 30° spacing ; cusps[9]=(asc+270)%360 (HOU2-02 ratchet documenté).
- `tests/houses/test_whole_sign.py` (207 lignes, 9 tests) — algorithm-tier + polar safety + 30°-spacing + sign-floor convention + Pitfall 3 + registry + vectorisation + end-to-end.
- `tests/houses/test_equal.py` (189 lignes, 9 tests) — algorithm-tier + polar safety + 30°-spacing + ASC convention + MC divergence ratchet + registry + vectorisation + end-to-end.

### Modified

- `ketu/houses/__init__.py` — append `from . import whole_sign` et `from . import equal` après le porphyry trigger (2 lignes ajoutées).
- `ketu/houses/api.py` — introduction de `POLAR_SAFE_SYSTEMS: frozenset[str] = frozenset({"porphyry", "whole_sign", "equal"})` au module-top avec docstring détaillé ; substitution `system_lower != "porphyry"` → `system_lower not in POLAR_SAFE_SYSTEMS` ligne 145 ; commentaire explicatif refactoré pour référencer le set au lieu du singulier `'porphyry'`.
- `tests/houses/test_polar_safety.py` — append `test_whole_sign_does_not_yield_nan_above_polar_circle` et `test_equal_does_not_yield_nan_above_polar_circle` après le test porphyry existant.

## Decisions Made

- **`POLAR_SAFE_SYSTEMS` au module-top en frozenset** : l'extraction au top-level (suggestion finale du plan) plutôt qu'inline dans `calculate_houses` est plus propre stylistiquement et permet à des tests/scripts externes de l'introspecter (ex. `from ketu.houses.api import POLAR_SAFE_SYSTEMS`). Frozenset est canonique pour un set immutable de strings constantes.
- **Mirror du pre-floor polar ASC swap** : les deux nouveaux modules dupliquent intentionnellement le code de swap (`acmc_signed < 0 → asc += 180°`) plutôt que d'extraire un helper. Justification : l'extraction (e.g. `_polar_swapped_asc(armc, lat, eps)`) ajouterait une indirection peu lisible pour ~6 lignes ; chaque module reste self-contained et auto-documentant.
- **Les sections "Caveat" déplacées sous Notes** : `numpydoc lint` rejette les sections non-canoniques (GL06/GL07 warnings). Préserver le contenu narratif des caveats sous le header `Notes` standard plutôt que de désactiver le gate ou de le rendre custom.
- **Tests utilisent `np.asarray(..., dtype=np.float64)` pour les scalaires** : la signature `HouseSystemFn = Callable[[np.ndarray, np.ndarray, np.ndarray], np.ndarray]` typée ndarray-strict ; `np.float64(x)` est un scalaire numpy distinct, mypy `--strict` rejette le passage. `np.asarray(x, dtype=np.float64)` retourne un ndarray 0-D fonctionnellement équivalent et type-correct.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Le plan suggère `np.float64(...)` pour les inputs scalar des tests, ce qui viole `mypy --strict`**

- **Found during:** Task 5 (création de `test_whole_sign.py`)
- **Issue:** Le plan inclut littéralement `whole_sign_cusps(np.float64(armc), np.float64(chart["lat"]), np.float64(eps))`. Mypy `--strict` rejette ce code avec 9 erreurs `Argument N to "whole_sign_cusps" has incompatible type "float64"; expected "ndarray[tuple[Any, ...], dtype[Any]]"`. La signature `HouseSystemFn` typée ndarray l'exige.
- **Fix:** Substituer `np.float64(x)` → `np.asarray(x, dtype=np.float64)` à 3 emplacements dans `test_whole_sign.py` et 2 dans `test_equal.py` (rendu équivalent fonctionnellement, type-correct).
- **Files modified:** `tests/houses/test_whole_sign.py`, `tests/houses/test_equal.py`
- **Verification:** `mypy --strict` passe sur les 2 fichiers de test ; tests 9/9 verts dans chaque fichier.
- **Committed in:** `127a1bc` (Task 5) et `b4d1903` (Task 6).

**2. [Rule 1 - Bug] Section docstring "Caveat ---" custom rejetée par numpydoc lint**

- **Found during:** Task 5 (gate `numpydoc lint`)
- **Issue:** Les modules `whole_sign.py` et `equal.py` contenaient une section narrative `Caveat — ... -----` au top du module-docstring. `numpydoc lint` émet GL06 (`Found unknown section "Caveat — ..."`) + GL07 (sections wrong order) — viole le doc gate `numpydoc validate` Phase 13 que Plan 14 ratche pour `ketu/houses/`.
- **Fix:** Déplacer le contenu narratif Caveat sous un header `Notes` (section canonique numpydoc), en gardant l'inscription `Caveat — ...:` comme première ligne du paragraphe pour préserver la mise en valeur visuelle.
- **Files modified:** `ketu/houses/whole_sign.py`, `ketu/houses/equal.py`
- **Verification:** `numpydoc lint ketu/houses/whole_sign.py ketu/houses/equal.py` retourne 0 (output vide).
- **Committed in:** `127a1bc` (whole_sign fix) et `b4d1903` (equal fix).

**3. [Rule 2 - Critical] Docstring/comment de `calculate_houses` faisait référence à la check singulière 'porphyry' obsolète**

- **Found during:** Task 4 (extension polar-safe)
- **Issue:** Le commentaire ligne 137-142 de `api.py` parlait spécifiquement de "Porphyry is itself the polar fallback path" comme justification du carve-out. Après l'extension à `POLAR_SAFE_SYSTEMS`, ce commentaire est trompeur : whole_sign et equal ne sont PAS des fallbacks, mais des systèmes polar-safe par construction. Pas de bug fonctionnel mais documentation incohérente avec le code (Rule 2 critical fonctionnellement).
- **Fix:** Refactor du commentaire pour référencer `POLAR_SAFE_SYSTEMS` set + mention de l'historique Phase 15 (`extended the set from {'porphyry'} to {'porphyry', 'whole_sign', 'equal'}`).
- **Files modified:** `ketu/houses/api.py`
- **Verification:** Le commentaire reflète désormais correctement le nouveau set.
- **Committed in:** `e7852c4` (Task 4, intégré au commit principal).

---

**Total deviations:** 3 auto-fixed (2 bugs réels — mypy + numpydoc — plus 1 doc-coherence improvement). Aucune Rule 4 (architecturale) déclenchée.

**Impact on plan:** Aucun scope creep. Les fixes 1+2 sont des erreurs latentes du plan rendues visibles par les gates `mypy --strict` et `numpydoc lint` (Phase 13 doc gates). Le fix 3 est de la documentation cohérente avec le refactor.

## Issues Encountered

- **`pytest --cov-fail-under=95` global gate sur run partiel** : exactement le même faux-positif que dans 15-01 SUMMARY (le gate global de pyproject couvre l'ensemble du projet, pas le sous-ensemble couvert par les fichiers de test passés). Vérifié : `pytest tests/houses/test_whole_sign.py tests/houses/test_equal.py --cov=ketu.houses.whole_sign --cov=ketu.houses.equal` reporte 100% sur les 2 modules cibles ; le `FAIL Required test coverage of 95% not reached. Total coverage: 10.55%` est mesuré sur tout `ketu/`. Aucune action — la régression complète `pytest tests/ -x` (sans coverage) passe 878/878.
- **Venv shebang `pytest`** : connu (PROJECT.md mentionne `Venv shebangs hardcoded to /home/loc/workspace/solaris/ketu/venv/bin/python3`). Workaround `python -m pytest ...` documenté dans PROJECT.md, utilisé partout. Aucune action.

## Verification Gates Passed

Tous les 13 gates du plan sont au vert :

1. ✅ U16 capacity (depuis 15-01 ; pas de re-bump nécessaire pour whole_sign/equal qui sont < 16 chars)
2. ✅ `'whole_sign'` et `'equal'` enregistrés dans `SYSTEMS` (`['equal', 'koch', 'placidus', 'porphyry', 'whole_sign']`)
3. ✅ Algorithm-tier oracle bit-exact (1e-6°) — tests `test_whole_sign_algorithm_matches_oracle_armc_at_all_latitudes` et `test_equal_algorithm_matches_oracle_armc_at_all_latitudes` PASSED
4. ✅ End-to-end snapshot reste vert — `test_loaded_reference_snapshot_matches_oracle` PASSED (60 comparaisons, incluant whole_sign et equal)
5. ✅ Polar safety — `tests/houses/test_polar_safety.py` 10/10 PASSED ; `test_whole_sign_no_nan_at_polar_latitudes` et `test_equal_no_nan_at_polar_latitudes` PASSED
6. ✅ Convention divergences pinned — `test_whole_sign_cusp_1_is_start_of_rising_sign` PASSED ; `test_equal_cusp_10_is_asc_plus_270_not_astronomical_mc` PASSED (delta vs astro MC > 1°)
7. ✅ Pitfall 3 (ASC=0° boundary) — `test_whole_sign_asc_at_sign_boundary_yields_cusp_1_zero` PASSED
8. ✅ Polar gate étendu — `calculate_houses(jd, 80, 0, system="whole_sign")` et `system="equal"` ne lèvent plus `HighLatitudeError` (sans `polar_fallback="porphyry"`)
9. ✅ `pytest tests/houses/ -x` passe 176/176 (Plans 10-03..10-06 + 15-01 intacts)
10. ✅ Coverage 100% sur `ketu.houses.whole_sign` et `ketu.houses.equal` (gate ≥95% v1.2 strict)
11. ✅ `mypy --strict ketu/houses/whole_sign.py ketu/houses/equal.py ketu/houses/api.py` clean
12. ✅ Doc gates : `numpydoc lint` clean ; `interrogate ≥95%` PASSED (100.0%)
13. ✅ AGPL boundary preserved — `ketu.houses.whole_sign` et `ketu.houses.equal` n'exposent aucun symbole `swe*`

Régression complète : `pytest tests/ -x` → **878 passed** (était 858 sur 15-01 close).

## User Setup Required

Aucun — ce plan ne nécessite aucune configuration externe ni secret.

## Next Phase Readiness

- ✅ **Plan 15-03 (Regiomontanus) débloqué** : peut désormais ajouter sa propre ligne `from . import regiomontanus` à `ketu/houses/__init__.py` (append-only, ligne 6 sous les 5 actuelles), ses propres tests no-NaN-but-NaN-at-polar dans `test_polar_safety.py` (append après le test equal). Aucun conflit avec le scope de 15-02.
- ✅ **Plan 15-04 (CLI integration) débloqué** : `sorted(SYSTEMS.keys())` retourne désormais `['equal', 'koch', 'placidus', 'porphyry', 'whole_sign']` (5 entrées) ; après merge 15-03 ce sera 6. CLI `--list-house-systems` et `--system` choices fonctionneront dynamiquement.
- ✅ **Wave 2 progresse selon plan** : 15-02 livre 2 systèmes sur 3 ; 15-03 (Regiomontanus) reste à exécuter pour compléter HOU2-01..05 (HOU2-03 + HOU2-04 + HOU2-05 sont les 3 derniers requirements du milestone Phase 15).
- ✅ Aucun blocker. Phase 15 Wave 2 toujours OK pour exécution parallèle.

## Self-Check: PASSED

Vérification post-écriture :

- ✅ FOUND: `/home/loc/workspace/ketu/ketu/houses/whole_sign.py`
- ✅ FOUND: `/home/loc/workspace/ketu/ketu/houses/equal.py`
- ✅ FOUND: `/home/loc/workspace/ketu/tests/houses/test_whole_sign.py`
- ✅ FOUND: `/home/loc/workspace/ketu/tests/houses/test_equal.py`
- ✅ FOUND: `/home/loc/workspace/ketu/.planning/phases/15-additional-house-systems/15-02-SUMMARY.md` (ce fichier)
- ✅ FOUND: commit `891c54e` (Task 1)
- ✅ FOUND: commit `c656855` (Task 2)
- ✅ FOUND: commit `d06207b` (Task 3)
- ✅ FOUND: commit `e7852c4` (Task 4)
- ✅ FOUND: commit `127a1bc` (Task 5)
- ✅ FOUND: commit `b4d1903` (Task 6)
- ✅ FOUND: commit `645eba3` (Task 7)

---

*Phase: 15-additional-house-systems*
*Plan: 02-whole-sign-and-equal*
*Completed: 2026-05-09*
