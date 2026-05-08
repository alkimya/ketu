# Phase 14 — Plans Overview

**Planifié :** 2026-05-09 par Sophie Chen
**Phase :** 14-chart-abstraction-foundation
**Plans :** 5 (`14-01-PLAN.md` à `14-05-PLAN.md`)
**Vagues :** 2 (1 séquentielle prereq, 1 parallèle 3-way)
**Divergence vs RESEARCH §8 :** aucune — le découpage 5-plans est repris à l'identique parce qu'il est déjà optimal.

---

## Découpage retenu

### Vague 1 (séquentielle, fondation contractuelle)

| # | Plan | Scope (1 ligne) | Dépendances |
|---|------|------------------|-------------|
| 1 | **14-01-subpackage-skeleton-and-dtype** | Crée `ketu/charts/{__init__,core,api}.py` + `pyproject.toml` (`packages` list) + `tests/charts/test_dtype.py`. CHART_DTYPE complet (14 champs), section "Why structured array", stubs `NotImplementedError` + docstrings complets. Gates verts dès le commit 1. | — |

### Vague 2 (parallèle, implémentation)

Les Plans 14-02, 14-03 et 14-04 peuvent être exécutés en parallèle après merge de 14-01. **MAIS** : 14-03 (`aspect_matrix`) dépend de 14-02 (`compute_chart` skeleton) parce qu'il édite la même fonction. En pratique :

- **14-02 et 14-04 sont vraiment parallèles** (touchent des fonctions différentes : `compute_chart` vs `is_day_chart`).
- **14-03 séquentiel après 14-02** (modifie le corps de `compute_chart` que 14-02 a écrit).

| # | Plan | Scope (1 ligne) | Dépendances |
|---|------|------------------|-------------|
| 2 | **14-02-compute-chart-positions-and-houses** | `compute_chart` : broadcast `(jd, lat, lon)`, `_vectorised_body_properties` via `calc_planet_position_batch` (boucle sur 13 corps, pas sur S), `calculate_houses` inline, sentinelles `aspect_matrix=-1` / `aspect_orbs=NaN` (placeholder). Tests broadcast + houses-inline + polar fallback + AGPL ratchet. | 14-01 |
| 3 | **14-03-aspect-matrix-builder** | `_build_aspect_matrix` (boucle Python sur S per D-16, projection records → matrice dense (13,13), mirror upper→lower triangle per D-17, diagonale sentinel per D-06). Branche dans `compute_chart`. Tests symétrie + sentinelles + 3 charts hand-validated (J2000_Paris, 1900_NewYork, Sagan_NYC_1934). | 14-02 |
| 4 | **14-04-is-day-chart-helper** | `is_day_chart(jd, lat, lon)` : broadcast, `calculate_houses(polar_fallback="porphyry")` toujours (D-15), `house_of(sun_lon, cusps) >= 7` (D-14), convention sunrise-inclusive pragmatique (D-13). Tests sunrise edge ±0.01°, polar safety lat=80, vectorisation, cohérence cross-API vs CHART_DTYPE. | 14-01 |
| 5 | **14-05-doc-gates-coverage-and-makefile** | Polish docstrings (See Also, Examples vectorisés), cible `make charts-coverage` (mirror HOU-09), marker pytest `charts_coverage_gate`, audit final no-carve-out mypy/coverage/interrogate, validation `pytest --doctest-modules`. CHART-05 verrouillé. | 14-02, 14-03, 14-04 |

---

## Graphe de parallélisme

```
                     ┌────────────────────────┐
                     │ Wave 1                 │
                     │ ┌────────────────────┐ │
                     │ │ 14-01 (skeleton)   │ │
                     │ └─────────┬──────────┘ │
                     └───────────┼────────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            ▼                    ▼                    ▼
    ┌────────────────┐                       ┌────────────────┐
    │ Wave 2 — left  │                       │ Wave 2 — right │
    │ ┌────────────┐ │                       │ ┌────────────┐ │
    │ │ 14-02      │ │                       │ │ 14-04      │ │
    │ │ compute_   │ │                       │ │ is_day_    │ │
    │ │ chart      │ │                       │ │ chart      │ │
    │ │ positions  │ │                       │ │            │ │
    │ │ + houses   │ │                       │ │ (parallèle │ │
    │ └─────┬──────┘ │                       │  avec 14-02 │ │
    │       │        │                       │  et 14-03)  │ │
    │       ▼        │                       │            │ │
    │ ┌────────────┐ │                       │            │ │
    │ │ 14-03      │ │                       │            │ │
    │ │ aspect_    │ │                       │            │ │
    │ │ matrix     │ │                       │            │ │
    │ └─────┬──────┘ │                       └─────┬──────┘ │
    └───────┼────────┘                             │        │
            │                                      │        │
            └──────────────┬───────────────────────┘        │
                           ▼                                │
                  ┌──────────────────┐                      │
                  │ Wave 3           │◄─────────────────────┘
                  │ ┌──────────────┐ │
                  │ │ 14-05        │ │
                  │ │ doc gates +  │ │
                  │ │ coverage +   │ │
                  │ │ Makefile     │ │
                  │ └──────────────┘ │
                  └──────────────────┘
```

**Parallélisme effectif** :
- **Wave 1 séquentielle** : 14-01 seul. Indispensable parce que CHART_DTYPE est le contrat consommé par tous les autres plans.
- **Wave 2 parallèle 2-way** : `(14-02 → 14-03)` parallèle à `14-04`. Donc 2 worktrees Git (un sur la branche compute_chart, un sur la branche is_day_chart), merge dans n'importe quel ordre.
- **Wave 3 séquentielle** : 14-05 attend que les trois plans précédents aient atterri (il polish leurs docstrings et verrouille la couverture globale).

**Coût total séquentiel estimé** : 5 plans × ~30-45 min chacun = ~3 h (sans parallélisme).
**Coût avec parallélisme Wave 2** : ~2 h (14-02→14-03 dure ~75 min, 14-04 dure ~30 min en parallèle, puis 14-05 ~30 min).

---

## Mapping requirements ↔ plans ↔ success criteria

| REQ | Description courte | Plan(s) | Success Criteria couverts |
|-----|---------------------|---------|----------------------------|
| **CHART-01** | `ketu/charts/` subpackage avec `__init__.py` exposant l'API publique | **14-01** | 14.1 (imports résolvent) |
| **CHART-02** | `CHART_DTYPE` structured array (14 champs : metadata + bodies + houses inline + aspect matrix + orbs) ML-interop | **14-01** | 14.5 (named, frozen, shape-documented + "Why structured array" section) |
| **CHART-03** | `compute_chart(jd, lat, lon, system, aspects) → CHART_DTYPE` vectorisable | **14-02 + 14-03** | 14.1 (return shape + content), 14.2 (vectorisation no Python hot loop) |
| **CHART-04** | `is_day_chart(jd, lat, lon)` vectorisable, sunrise-inclusive | **14-04** | 14.3 (sunrise inclusive + cohérence cross-API CHART_DTYPE) |
| **CHART-05** | Couverture ≥95 % sur `ketu/charts/` + numpydoc clean | **14-05** | 14.4 (coverage ≥95 % + numpydoc validate clean) |

| Success Criterion (ROADMAP) | Phrase courte | Plan(s) qui le porte |
|------------------------------|----------------|------------------------|
| 14.1 | Imports résolvent + `compute_chart` retourne CHART_DTYPE complet | 14-01 (imports) + 14-02 + 14-03 (content) |
| 14.2 | `compute_chart` vectorisé broadcast (jd, lat, lon) → leading shape S, no Python hot loop | 14-02 (positions+houses), confirmé 14-03 (aspects) |
| 14.3 | `is_day_chart` sunrise-inclusive, vectorisé, cohérent vs CHART_DTYPE | 14-04 |
| 14.4 | Coverage ≥95 % + numpydoc clean | 14-05 (gate final) |
| 14.5 | CHART_DTYPE named, frozen, shape-documented + "Why structured array" section | 14-01 (création), 14-05 (audit final) |

**Vérification : aucun success criterion orphelin.** Tous les 5 SC ont au moins un plan responsable.

---

## Estimation de complexité par plan

| Plan | Complexité | # tasks | Risque cross-cutting | Justification |
|------|------------|---------|----------------------|----------------|
| **14-01** | **M** | 7 | Bas | Volume modéré (3 fichiers prod + 1 fichier test + 1 conf), purement structurel. Risque principal : pyproject.toml packages list (cf. PATTERNS §7.8 override CONTEXT.md). Tests pinning des sentinelles et anti-pattern dataclass. |
| **14-02** | **L** | 6 | Moyen | Le plan le plus dense : `_vectorised_body_properties` + `compute_chart` complet + 2 fichiers de tests d'intégration (17 tests cumulés). Risque : `calc_planet_position_batch` API non explicitement testée pour edge case shape. Mitigation : test #6 (vectorised==scalar) verrouille la cohérence. |
| **14-03** | **M** | 4 | Moyen | Volume modéré (1 helper + 1 fichier test 12 tests), MAIS la boucle Python sur S est une dette consciente (D-16) qui demande un commentaire `TODO(v1.3)` propre. Risque principal : 3 charts hand-validated demandent du temps de cross-check. |
| **14-04** | **S** | 3 | Bas | Plan le plus court : un helper compose `house_of`, broadcast, polar Porphyry interne, 12 tests. Décision pragmatique D-13 (pas de branche `on_asc`) simplifie le code. Risque mineur : tests sunrise pragmatiques ±0.01° demandent une construction synthétique correcte. |
| **14-05** | **S** | 8 | Bas | Pas de nouveau code de production. Audit + polish + Makefile + pyproject. Risque : si la couverture < 95 % à la première run, faut ajouter des tests ciblés. Mitigation : les Plans 02-04 ont prévu une couverture déjà saine. |

**Volume total** : ~28 tasks réparties sur 5 plans, ~50 tests cumulés. Aucun plan ne dépasse 7 tasks (sweet spot revertable atomique).

---

## Divergence vs recommandation RESEARCH.md §8

**Aucune divergence.** Le découpage 5-plans présenté en RESEARCH §8 est repris à l'identique. Justifications de cette adhésion :

1. **14-01 isolé** : pinner le contrat dtype en premier libère 14-02/03/04 du risque de redrift sur les noms/shapes.
2. **14-02 + 14-03 séquentiels** : `_build_aspect_matrix` modifie la même fonction `compute_chart` que 14-02 vient d'écrire. Les fusionner ferait un plan de 11+ tasks et ~25 tests, dépassant la zone confortable.
3. **14-04 indépendant** : `is_day_chart` ne touche pas `compute_chart`. Le sortir en plan séparé permet un parallélisme effectif.
4. **14-05 final** : sortir le sweep doc + coverage évite que chaque plan s'épuise sur interrogate/numpydoc — chacun écrit des docstrings « bonnes » et 14-05 garantit le « parfait ».

Les variantes acceptables mentionnées en RESEARCH §8 fin (fusionner 14-04 dans 14-01, fusionner 14-02/14-03, sortir un plan Makefile dédié) ont été examinées et rejetées :
- **Fusionner 14-04 dans 14-01** rendrait 14-01 trop hétérogène (skeleton + impl) et casserait la propriété « 14-01 verrouille le contrat ».
- **Fusionner 14-02 + 14-03** créerait un plan trop gros (cf. risque cité plus haut).
- **Sortir un plan Makefile dédié** est over-engineered pour une seule cible Make + un marker pytest ; intégré dans 14-05 c'est plus cohérent.

---

## Honneur des décisions verrouillées (D-01 à D-17)

Vérification croisée que chaque décision LOCKED apparaît dans au moins un plan :

| Décision | Plan(s) | Endroit |
|----------|---------|---------|
| D-01 (positions layout 3 subarrays) | 14-01 | CHART_DTYPE definition |
| D-02 (lon/lat/speed only, retro derivable) | 14-01, 14-02 | dtype + test retrograde |
| D-03 (houses inline, pas nested) | 14-01 | dtype layout |
| D-04 (metadata jd/lat/lon/system inline) | 14-01, 14-02 | dtype + test meta round-trip |
| D-05 (aspect_matrix dense (13,13)) | 14-01, 14-03 | dtype + builder |
| D-06 (sentinels -1 / NaN diagonale) | 14-01, 14-03 | dtype + test diagonal sentinel |
| D-07 (default CLASSICAL) | 14-03 | _build_aspect_matrix + test default classical |
| D-08 (body list FROZEN at 13) | 14-01, 14-02 | _BODY_COUNT constant + dtype docstring |
| D-09 (vectorisation broadcast S) | 14-02 | compute_chart broadcast block |
| D-10 (AspectSetSpec contract) | 14-03 | _build_aspect_matrix + test aspect subset |
| D-11 (polar_fallback pass-through) | 14-02 | compute_chart polar tests |
| D-12 (is_day_chart standalone, pas dans dtype) | 14-04 | helper standalone, pas de field is_day dans CHART_DTYPE |
| D-13 (sunrise inclusive) | 14-04 | docstring + test pragmatique ±0.01° |
| D-14 (houses 7-12 = day) | 14-04 | implementation + test consistency |
| D-15 (polar safety internal Porphyry) | 14-04 | always polar_fallback="porphyry" + test lat=80 |
| D-16 (re-use calculate_aspects_vectorized + Python loop S) | 14-03 | _build_aspect_matrix + commentaire TODO v1.3 |
| D-17 (symmetric mirror upper→lower) | 14-03 | mirror block + test symétrie |

**Verdict : 17/17 décisions couvertes par au moins un plan + un test pinné.**

---

## Cross-cutting constraints (v1.2) honnorés

| Contrainte | Plan(s) responsable(s) | Vérification |
|------------|-------------------------|---------------|
| Non-breaking minor strict | Tous (additif uniquement) | Aucun edit sur `ketu/houses/`, `ketu/aspects/`, `ketu/calculations.py`. |
| Pure-NumPy | Tous | `pyproject.toml` non modifié sur `dependencies`. Test ratchet AGPL `test_no_runtime_swisseph_import` dans 14-01, 14-02, 14-04. |
| Python 3.10+ | Tous | `from __future__ import annotations` partout (PATTERNS §7.1). |
| Vectorizable | 14-02, 14-04 | `np.broadcast_arrays` + test 0d/1d/2d/mixed-broadcast. |
| UTC-only | 14-02, 14-04 | Note loud dans docstrings de `compute_chart` et `is_day_chart`. |
| Coverage gates ≥95 % nouveau module | 14-05 | `make charts-coverage`. |
| Doc gates (interrogate ≥95 %, numpydoc validate) | 14-01 (dès le départ), 14-05 (audit final) | Verification commands explicites dans chaque plan. |
| Mypy `--strict` clean | Tous | Pas de carve-out `ketu.charts.*` dans pyproject.toml ; vérifié 14-05 Task 6. |
| AGPL non-contamination | 14-01, 14-02, 14-04 | Test ratchet `test_no_runtime_swisseph_import` (PATTERNS §8.5). |

---

## Risques résiduels et mitigations

| Risque | Probabilité | Impact | Mitigation prévue |
|--------|-------------|--------|---------------------|
| Import cross-conftest fixture (`from tests.houses.conftest import …`) ne propage pas correctement | Moyen | Bas | Fallback documenté dans 14-02 Task 1 : copier-coller les 10 reference_charts (10 lignes). |
| `np.ndindex(())` ne se comporte pas comme attendu | Faible (Assumption A1) | Moyen | Test pinné explicite dans 14-03 (`test_aspect_matrix_scalar_jd_via_ndindex_empty_tuple`). |
| `pytest --doctest-modules` échoue à cause de variation de repr numpy | Moyen | Bas | Stratégie documentée 14-05 Task 8 (option +ELLIPSIS ou +SKIP, ou réduire l'exemple à shape only). |
| Couverture < 95 % à la première run de `make charts-coverage` | Moyen | Bas | 14-05 Task 7 : ajouter tests ciblés OU `# pragma: no cover` parcimonieux ; **interdit** d'élargir omit. |
| `pyproject.toml [tool.setuptools].packages` oubli de `ketu.charts` | Élevé si copy-paste mécanique du CONTEXT.md | Élevé (pip install ne ship pas le subpackage) | 14-01 Task 1 le force explicitement + verification gate `python -c "import tomllib …"`. |
| Convention sunrise-inclusive testée par injection synthétique potentiellement non représentative | Faible | Bas | Test #10 de 14-04 documenté comme pragmatique ; un test « sun on real ASC via root-finding » pourrait être ajouté en v1.3 si Phase 19 (Parts) signale un cas observé. |

---

## Statut post-merge des 5 plans

Après merge propre des 5 plans, l'état du repo est :

- `ketu/charts/` complet et autonome.
- 5 fichiers de tests sous `tests/charts/` (~50 tests cumulés).
- `Makefile` augmenté de la cible `charts-coverage`.
- `pyproject.toml` augmenté de `ketu.charts` dans `packages` + marker `charts_coverage_gate`.
- ROADMAP Phase 14 complète avec **Plans : 5/5**.
- REQUIREMENTS Phase 14 : CHART-01..05 tous Done.

Phase 14 est alors prête pour `/gsd-verify-work` et l'unblocking des Phases 15 (parallèle), 16, 17, 18, 19 (consommatrices de CHART_DTYPE).

---

*Sophie Chen — Lead Technical Architect — 2026-05-09*
