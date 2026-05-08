# Phase 14 — Plan Review

**Verdict:** PASS WITH NOTES
**Date:** 2026-05-09
**Reviewer:** gsd-plan-checker (Sophie Chen)

---

## Goal coverage matrix

| Success criterion | Plan(s) responsible | Verification gate (concrete) | Status |
|---|---|---|---|
| **14.1** — `from ketu.charts import compute_chart, CHART_DTYPE, is_day_chart` résout cleanly ; `compute_chart(jd, lat, lon, system="placidus", aspects="classical")` retourne CHART_DTYPE complet (positions + ASC/MC/ARMC/Vertex + cusps + aspects) en un appel | 14-01 (skeleton + dtype + imports), 14-02 (positions + houses), 14-03 (aspects) | `14-01` Task 6 test #1 `test_public_imports_resolve` + 14-01 verification gate #7 smoke import + `14-02` Task 4 test #1 `test_compute_chart_returns_chart_dtype` + `14-03` Task 4 test #5 `test_aspect_matrix_consistent_with_calculate_aspects_vectorized_standalone` | OK |
| **14.2** — `compute_chart` accepte scalar AND array `jd` ; retourne CHART_DTYPE vectorisé ; pas de Python loop dans le hot path | 14-02 (broadcast + `_vectorised_body_properties` boucle bornée à 13 corps) | `14-02` Task 5 test suite complète `test_compute_chart_vectorisation.py` (6 tests : scalar, 1d, 2d, mixed broadcast, vectorised==scalar, hot-path latency proxy) + verification gate #5 sanity script Python | OK avec NOTE (cf. dimension Verification Derivation ci-dessous) |
| **14.3** — `is_day_chart(jd, lat, lon)` retourne True quand Sun ≥ ASC (sunrise inclusive), vectorisable, cohérent avec Sun longitude / ASC du CHART_DTYPE | 14-04 | `14-04` Task 3 test #9 `test_is_day_chart_consistency_with_compute_chart_asc_and_sun_lon` + tests #10 `_sunrise_inclusive_pragmatic_convention` + tests vectorisation #4-#6 | PASS WITH NOTE (D-13 sunrise-inclusive est implémenté de manière pragmatique et le test pin-le par injection synthétique, pas par recherche de jd réel — voir Findings W2) |
| **14.4** — Coverage sur `ketu/charts/` ≥95 % ; numpydoc validate clean | 14-05 (gate final), garanti dès 14-01 par discipline docstring | `14-05` Task 7 `make charts-coverage` (échec → exit code non-zero) + Task 8 `pytest --doctest-modules ketu/charts/` + `make doc-gates` | OK |
| **14.5** — CHART_DTYPE est named, frozen, shape-documented dans le module docstring avec section "Why structured array" | 14-01 (création + ratchet test), 14-05 (audit final) | `14-01` Task 6 test #10 `test_dtype_module_docstring_mentions_why_structured_array` (assertion sur `"Why a structured array" in ketu.charts.core.__doc__`) + `14-05` Task 2 audit visuel | OK |

**Bilan :** 5/5 success criteria ont au moins un plan responsable + une commande de vérification concrète qui les pinne. Aucun critère orphelin.

---

## Locked decisions traceability

| Décision | Plan | Task / endroit | Test pinning it | Status |
|---|---|---|---|---|
| **D-01** (positions layout 3 subarrays `body_lons/lats/speeds (f8, (13,))`) | 14-01 | Task 2 (CHART_DTYPE definition) | 14-01 Task 6 test #3 `test_dtype_subarray_shapes` | OK |
| **D-02** (lon/lat/speed only, retro derivable as `body_speeds < 0`) | 14-01, 14-02 | dtype + Task 4 test #6 | 14-02 test `test_compute_chart_body_speeds_negative_for_retrograde` | OK |
| **D-03** (houses inline, pas nested) | 14-01, 14-02 | dtype layout + assemblage | 14-02 test #4 `test_compute_chart_houses_inline_matches_calculate_houses` (paramétrisé sur 10 reference_charts × 3 systems) | OK |
| **D-04** (metadata jd/lat/lon/system inline) | 14-01, 14-02 | dtype + assemblage | 14-02 tests #2 + #3 (meta round-trip + lowercased system) | OK |
| **D-05** (aspect_matrix dense `(i1, (13,13))` + aspect_orbs `(f4, (13,13))`) | 14-01, 14-03 | dtype + builder | 14-01 test #3 (subarray shapes), 14-03 test #2 (symmetric) | OK |
| **D-06** (sentinel -1 / NaN, diagonale) | 14-01, 14-03 | dtype docstring + builder + tests | 14-01 tests #8-#9 (sentinel acceptance) + 14-03 test #4 `test_aspect_matrix_diagonal_sentinels` + #7 `test_aspect_matrix_caller_mask_pattern` | OK |
| **D-07** (default `aspects=None` ≡ CLASSICAL) | 14-03 | `_build_aspect_matrix` pass-through + docstring update | 14-03 test #1 `test_aspect_matrix_default_aspects_is_classical` | OK |
| **D-08** (body list FROZEN at 13) | 14-01, 14-02 | dtype docstring (axis (13,) frozen) + `_BODY_COUNT = 13` constant | 14-01 test #3 (shape `(13,)` pinned) — implicite via la rigidité du dtype | OK |
| **D-09** (vectorisation broadcast S, no Python hot loop) | 14-02 | `compute_chart` broadcast block | 14-02 vectorisation tests #1-#5 + #6 latency proxy | OK |
| **D-10** (AspectSetSpec contract pass-through) | 14-03 | `_build_aspect_matrix` accepte AspectSetSpec | 14-03 test #6 `test_aspect_matrix_handles_aspect_subset` | OK |
| **D-11** (polar_fallback pass-through) | 14-02 | `compute_chart` arg propagé à `calculate_houses` | 14-02 tests #8-#10 (polar default raise / porphyry substitutes / invalid value) | OK |
| **D-12** (is_day_chart standalone, PAS dans dtype) | 14-04 | helper standalone, dtype 14-01 ne contient PAS de field `is_day` | 14-01 test #2 `test_dtype_has_expected_field_names` (liste exacte des 14 champs, pas de `is_day`) | OK |
| **D-13** (sunrise inclusive, Sun ≥ ASC = day) | 14-04 | docstring + decision pragmatique | 14-04 test #10 `test_is_day_chart_sunrise_inclusive_pragmatic_convention` | OK avec NOTE — voir Warnings W2 |
| **D-14** (houses 7-12 = day, geometric) | 14-04 | `return sun_house >= 7` + docstring Notes section | 14-04 tests #2 + #3 (Paris J2000 noon = day, midnight = night) | OK |
| **D-15** (polar safety internal Porphyry) | 14-04 | `calculate_houses(polar_fallback="porphyry")` toujours forcé en interne | 14-04 tests #7 + #8 (lat=80, arctic circle paramétrisé sur lat 70-85) | OK |
| **D-16** (re-use calculate_aspects_vectorized + boucle Python sur S OK) | 14-03 | `_build_aspect_matrix` boucle `np.ndindex(jd_b.shape)` + commentaire `TODO(v1.3)` | 14-03 tests #5 (consistency standalone) + #8 (scalar-jd via empty tuple) + #9 (vectorised==per-element) | OK |
| **D-17** (symmetric mirror upper→lower triangle) | 14-03 | `matrix[idx + (i,j)] = matrix[idx + (j,i)] = i_asp` dans le builder | 14-03 tests #2 + #3 (symmetric matrix + symmetric orbs avec equal_nan=True) | OK |

**Bilan : 17/17 décisions LOCKED couvertes par au moins un task d'implémentation + un test de pinning.**

---

## Findings

### Blocking (FAIL — must fix before execute)

**Aucun.** Les plans couvrent goal, decisions, et cross-cutting constraints sans omission ni contradiction. La structure est propre, les tâches sont atomiques, les commandes de vérification sont concrètes.

### Warnings (PASS WITH NOTES — recommend fix, executor handles inline)

**W1 — `mypy --strict` peut buter sur l'import de `AspectSetSpec` depuis `ketu.aspects.presets`** (sévérité : warning)
- `pyproject.toml:144-153` carve-out `ketu.aspects.*` du strict checking ; il y a `disable_error_code = ["misc", "no-untyped-def", ..., "no-any-return", ...]`.
- Le plan 14-01 Task 3 importe `from ketu.aspects.presets import AspectSetSpec` dans `ketu/charts/api.py` (qui DOIT être strict-clean per CLAUDE.md cross-cutting v1.2).
- `AspectSetSpec = Union[None, str, Sequence[Union[str, int]], np.ndarray]` est typé proprement dans `presets.py` (vérifié in situ ligne 98), donc l'import en lui-même devrait passer mypy strict.
- **Risque résiduel** : si `calculate_aspects_vectorized` renvoie un type que mypy strict refuse (e.g. `Any` à cause du carve-out), le call site dans `_build_aspect_matrix` pourrait râler. Mitigation : un `cast(np.ndarray, records)` à l'appel sera probablement nécessaire en 14-03 Task 1. Le plan ne l'anticipe pas explicitement.
- **Fix recommandé pour l'executor** : si mypy strict râle au merge de 14-03, ajouter un `cast(np.ndarray, calculate_aspects_vectorized(...))` dans `_build_aspect_matrix` plutôt que d'élargir le carve-out à `ketu.charts.*` (qui violerait le contrat « charts/ strict-clean dès le départ »).

**W2 — D-13 sunrise-inclusive est implémenté de manière pragmatique mais le test pin la convention par injection, pas par cas réel** (sévérité : warning)
- Plan 14-04 Task 1 documente explicitement l'arbitrage Open Question 1 du RESEARCH (recommandation Sophie pragmatique : `return sun_house >= 7` sans branche `np.isclose(Sun, ASC)`).
- Plan 14-04 Task 3 test #10 valide la convention sur des deltas synthétiques `±0.01°` de l'ASC.
- **Subtilité non triviale** : avec la convention `house_of` actuelle (« cusps[i] BEGINS house i+1 », `houses/api.py:202-204`), un Sun *exactement* sur l'ASC est en maison 1 → `sun_house >= 7` retourne `False` → contradiction stricto-sensu avec D-13 (« Sun on ASC = day »).
- Le RESEARCH §4 Pitfall 4 reconnaît la subtilité ; le plan 14-04 documente que le cas mesure-zéro n'arrive pas en pratique numérique.
- **Risque résiduel** : si Phase 19 PARTS découvre un cas observé où l'égalité stricte se produit (ex : injection d'un chart synthétique pour tester un Lot of Fortune), le contrat D-13 sera violé silencieusement.
- **Fix recommandé pour l'executor** : ajouter en 14-04 un test additionnel `test_is_day_chart_sun_strictly_on_asc_synthetic` qui injecte un cas constructed (un jd où numériquement `sun_lon == asc` à la machine epsilon près via root-finding ou via un mock) et documente le comportement attendu actuel comme un known-deviation D-13. Si Phase 19 le remonte, switcher vers la branche `on_asc`.

**W3 — Plan 14-02 verification gate #5 (sanity vectorisation) ne re-vérifie pas la condition « no Python loop in hot path »** (sévérité : warning)
- Le test #6 `test_compute_chart_zero_python_loop_in_hot_path` du Plan 14-02 utilise un timeout de 5s comme proxy, marqué `@pytest.mark.slow` skippable.
- Le verification gate du plan 14-02 (commandes shell exit 0) n'inclut PAS l'exécution de ce test slow par défaut, donc le success criterion 14.2 « no Python loop in hot path » est vérifié indirectement seulement.
- **Fix recommandé pour l'executor** : ajouter une commande de vérification dans 14-02 verification gates : `python -m pytest tests/charts/test_compute_chart_vectorisation.py::test_compute_chart_zero_python_loop_in_hot_path -v` (ne pas la skipper). Sinon SC 14.2 reste vérifié uniquement par l'inspection de code, pas par un gate exécutable.

**W4 — Le commit message du plan 14-01 ne suit pas exactement la convention `git log` récente** (sévérité : warning, cosmétique)
- `git log --oneline -10` montre des commits comme `docs(13-05): summarize README + CHANGELOG positive-add reformulation` (préfixe `feat/docs/fix(NN-MM):`).
- Plan 14-01 utilise `feat(14-01): scaffold ketu.charts subpackage with CHART_DTYPE` → cohérent avec le pattern.
- Plan 14-02 / 14-03 / 14-04 / 14-05 idem → tous les 5 utilisent `feat(14-NN): ...` qui est le bon pattern.
- **Aucune action requise**, c'est juste une vérification que la convention est respectée.

**W5 — Plan 14-01 Task 6 test #11 `test_dtype_no_dataclass_chart_in_core` est formulé de manière trop large** (sévérité : warning)
- Le test rejette « any class » dans `ketu/charts/core.py` qui n'est pas un BaseException subclass.
- Risque : si 14-05 ou un futur plan ajoute un `class _ChartMetadata(NamedTuple)` ou `class ChartConfig(Protocol)` à `core.py` pour des raisons légitimes, ce test échouera spuriously.
- **Fix recommandé** : restreindre le test à l'interdiction explicite : `assert not hasattr(ketu.charts.core, "Chart")` (le nom de la dataclass anti-pattern serait `Chart`).

**W6 — Plan 14-02 Task 1 dépend d'un import cross-conftest non garanti** (sévérité : warning)
- `from tests.houses.conftest import (...)` est une stratégie risquée selon la collecte de fixtures pytest. Le RESEARCH §6 et le PLANS-OVERVIEW §Risques résiduels reconnaissent ce risque mais l'isolent en 14-02 sans plan de fallback dans le verification gate.
- **Fix recommandé** : si l'import cross-conftest casse au test, le plan 14-02 doit copier-coller les 10 entrées `reference_charts` dans `tests/charts/conftest.py`. Le verification gate du plan ne détecte pas explicitement ce cas. L'executor devra le gérer inline.

### Suggestions (optional polish, non-blocking)

**S1 — Le PLANS-OVERVIEW §Risques résiduels mentionne le risque W6 mais ne propose pas de gate de détection préventif**
- Idée : 14-02 Task 1 pourrait commencer par un check explicite `python -c "import sys; sys.path.insert(0, '.'); from tests.houses.conftest import reference_charts; print('OK')"`. Si exit non-zero, fallback automatique vers copier-coller. Pas un blocker, mais ça simplifie l'execute.

**S2 — Plan 14-05 Task 8 doctest `--doctest-modules` peut surprendre par les variations de repr numpy**
- Le plan documente la stratégie de mitigation (`+ELLIPSIS` ou `+SKIP`) mais ne préfère pas une option. Recommandation : adopter `+SKIP` par défaut sur les Examples vectorisés (la valeur de l'exemple est pédagogique, pas testable mécaniquement). Documenter ce choix une fois pour toutes en haut de chaque docstring concerné.

**S3 — Plan 14-03 Task 1 commentaire `TODO(v1.3)` pourrait être renforcé avec une référence d'issue ou de phase**
- Format suggéré : `# TODO(v1.3 / Phase 16 profiling): hoist resolve_aspect_set() above this loop if synastry batch profiling shows hot-path cost — see RESEARCH.md §Pitfall 3`. Pas blocking, juste tracé pour l'avenir.

**S4 — Aucun plan ne crée explicitement `tests/charts/fixtures/` directory pour les hand-validated charts**
- 14-03 Task 4 tests #10-#12 utilisent des charts hand-validated mais les coordonnées sont hardcodées dans les tests Python plutôt que stockées comme fichiers JSON dans `tests/charts/fixtures/` (pattern `tests/houses/fixtures/`). C'est acceptable pour 3 charts mais pas scalable. Pour Phase 14 c'est OK ; à reconsidérer si Phase 16 ajoute des dizaines de charts.

---

## Verification dimensions (résumé structuré)

| Dimension | Status | Notes |
|---|---|---|
| **1. Requirement coverage** | OK | CHART-01..05 tous mappés à au moins un plan + un test pinning. Vérifié via la table « Mapping requirements ↔ plans » de PLANS-OVERVIEW. |
| **2. Task completeness** | OK | Chaque PLAN.md a Files / Tasks / Verification gates / Done criteria / Atomic commit message / Rollback note. Tasks atomiques (≤7 par plan). |
| **3. Dependency correctness** | OK | Front-matter `depends_on: [N]` cohérent avec PLANS-OVERVIEW graphe. Aucun cycle. Wave 1 (14-01) → Wave 2 (14-02→14-03 séquentiel, 14-04 parallèle) → Wave 3 (14-05). |
| **4. Key links planned** | OK | `compute_chart` wire correctement `calculate_houses` + `calc_planet_position_batch` + `calculate_aspects_vectorized` (vérifié dans Tasks 2-3 du plan 14-02 et Task 1 du plan 14-03). `is_day_chart` wire `calculate_houses` + `calc_planet_position_batch` + `house_of` (vérifié 14-04 Task 1). |
| **5. Scope sanity** | OK | 14-01 = 7 tasks (haut, mais purement structural) ; 14-02 = 6 tasks ; 14-03 = 4 tasks ; 14-04 = 3 tasks ; 14-05 = 8 tasks (audit + Makefile, légèrement haut mais aucun nouveau code prod). Aucun plan > 8 tasks. Files modifiés : ~3 par plan max. Confortable. |
| **6. Verification derivation** | OK avec NOTE W3 | must_haves implicites présents (Done criteria mappent aux SC ROADMAP). Truths user-observable (« compute_chart returns CHART_DTYPE », « is_day_chart returns True at noon »). Un seul caveat : SC 14.2 « no Python loop in hot path » est vérifié par latency proxy `@pytest.mark.slow` qui peut être skippé. |
| **7. Context compliance** | OK | 17/17 D-XX honorés ; aucun test n'implémente de Deferred Idea (`is_day_chart(chart)` overload, Chiron, `compute_chart_aspects` standalone, `is_retrograde` field, top-level re-export, `dist` field). Aucune scope reduction détectée — pas de « v1 stub », pas de « simplified for now ». La décision pragmatique D-13 est explicitement encadrée par CONTEXT.md (le RESEARCH §4 documente l'arbitrage avant le plan). |
| **7b. Scope reduction** | OK | Recherche grep sur les 5 PLAN.md : aucun « v1 », « v2 », « simplified », « static for now », « hardcoded », « future enhancement », « placeholder », « basic version », « stub » sauf dans les contextes légitimes (14-01 documente que `compute_chart` et `is_day_chart` sont stubbed `NotImplementedError` jusqu'à 14-02/14-04 — c'est une stratégie d'incrémentation propre, pas une scope reduction du goal final). |
| **7c. Architectural tier compliance** | OK | RESEARCH.md a une « Architectural Responsibility Map » §Map (lignes 24-34). Tous les plans honorent : CHART_DTYPE en `core.py`, fonctions publiques en `api.py`, helpers privés `_build_aspect_matrix` / `_vectorised_body_properties` également en `api.py` (justifié par taille < 30 lignes), oracle test-only en `tests/charts/conftest.py`. Aucun mismatch tier. |
| **8. Nyquist compliance** | N/A | Pas de section « Validation Architecture » exigeant la sampling continuity au sens strict — RESEARCH §Validation Architecture présente une table « REQ → Behavior → Test type → Automated command » qui est respectée. Tous les tasks d'implémentation ont un automated verify : aucun « MISSING » non-couvert par Wave 0. |
| **9. Cross-plan data contracts** | OK | Le seul partage de données cross-plan est `aspect_matrix`/`aspect_orbs` initialisés en sentinelles par 14-02 puis remplis par 14-03. Le plan 14-02 documente explicitement « will be replaced by 14-03 » et 14-03 Task 3 transforme le test transition correspondant (renommage `test_compute_chart_aspect_matrix_sentinel_until_wave_03` → `test_compute_chart_aspect_matrix_diagonal_is_sentinel`). Pas de transformation conflictuelle. |
| **10. CLAUDE.md compliance** | OK | Tous les plans honorent : Sophie/français pour les PLAN.md narratifs (vérifié in situ), code/docstrings en anglais (pattern v1.1), `venv/` (pas `.venv/`, vérifié in situ aucune mention de `.venv`), NumPy structured arrays (pas de dataclass — anti-pattern PATTERNS §8.1 explicitement interdit par 14-01 test #11), pure-NumPy (pas d'ajout dans `[project.dependencies]`, vérifié), Python 3.10+ (`from __future__ import annotations` mandatoire PATTERNS §7.1), UTC-only (documenté `compute_chart` et `is_day_chart` docstrings). |
| **11. Research resolution** | OK | RESEARCH.md a une section `## Open Questions (à trancher au planning)` avec 3 questions. Toutes sont résolues dans les plans : (1) sunrise-inclusive pragmatic chez 14-04 Task 1 ; (2) cross-conftest import strategy chez 14-02 Task 1 + fallback ; (3) Sagan vs Einstein → Sagan adopté en 14-03 Task 4 test #12. Note : la section n'est PAS littéralement renommée `(RESOLVED)` dans RESEARCH.md, mais les résolutions sont documentées dans les plans. Recommandation cosmétique : renommer en `## Open Questions (RESOLVED — see plans)` pour respecter le contrat exact de la dimension 11. **Pas un blocker.** |
| **12. Pattern compliance** | OK | PATTERNS.md mappe chaque nouveau fichier à un analog v1.1 (`ketu/houses/{__init__,core,api}.py`, `tests/houses/{conftest,test_dtype,test_integration,test_polar_safety}.py`). Tous les plans citent l'analog dans leur Pre-flight reading + référencent les line numbers (e.g. `ketu/houses/api.py:107-114` pour le broadcast pattern). Shared patterns AGPL ratchet présent dans 14-01, 14-02, 14-04. Pattern numpy-avant-importorskip présent dans 14-02 Task 1. |

---

## Recommendation

**PASS WITH NOTES — proceed to execute.**

Les 5 plans sont d'une qualité élevée et constituent un set d'exécution cohérent. La stratégie de découpage (1 séquentiel + 2 parallèles + 1 final) est optimale, le mapping `success_criteria ↔ plans ↔ tests` est exhaustif, et les 17 décisions LOCKED sont toutes pinnées par au moins un test exécutable. La cohérence avec les patterns v1.1 (`ketu/houses/`) est rigoureuse — le PATTERNS.md identifie correctement la divergence subtile sur `pyproject.toml [tool.setuptools].packages` (liste explicite, pas find-packages) que CONTEXT.md avait sous-estimée.

Les 6 warnings ne bloquent pas l'exécution mais méritent attention de l'executor :
- **W1 (mypy strict + ketu.aspects carve-out)** est le plus probable de surface au merge — mitigation pré-pensée : `cast(np.ndarray, ...)` plutôt que carve-out.
- **W2 (D-13 sunrise pragmatique)** est une dette consciente, déjà documentée par RESEARCH ; mitigation : un test `_synthetic_strict_equality` additionnel pour traçabilité.
- **W3 (verification gate ne run pas le test slow vectorisation)** est un trou de gate facile à colmater : ajouter une ligne au gate du plan 14-02.
- **W4-W5-W6** sont cosmétiques ou concernent des cas edge déjà mitigés.

**Pas de re-planning nécessaire.** Lancer `/gsd-execute-phase 14` ; l'executor gérera les warnings inline avec les fix hints documentés ci-dessus. Les surfaces de test (~50 tests cumulés) et la discipline doc-gates (`interrogate ≥95 %`, `numpydoc lint`, `mypy --strict`, `make charts-coverage`) garantissent que toute régression sera capturée avant le commit final.

Phase 14 est prête à débloquer Phases 15 (parallèle), 16, 17, 18, 19 (consommateurs de CHART_DTYPE).

---

*Sophie Chen — gsd-plan-checker — 2026-05-09*
