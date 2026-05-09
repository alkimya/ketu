---
phase: 15-additional-house-systems
review_type: pre-execution-plan-check
reviewer: gsd-plan-checker (Sophie Chen orchestration)
date: 2026-05-09
plans_reviewed: [15-01, 15-02, 15-03, 15-04]
verdict: PASS_WITH_MINOR_REVISIONS
revision_loop: 1/3
---

# Phase 15 — Plan Review (pre-execution)

**Goal-backward verification — méthodologie GSD plan-checker**

## Verdict global

**PASS avec révisions mineures recommandées (5 LOW, 2 MEDIUM, 0 HIGH).**

Les 4 plans, exécutés dans l'ordre Wave 1 → Wave 2 (15-01, puis 15-02 ‖ 15-03, puis 15-04), ferment **les 4 success criteria de Phase 15** et couvrent **les 5 requirements HOU2-01..05**. Toutes les 9 LOCKED DECISIONS sont implémentées au moins une fois. Les 7 pitfalls de RESEARCH §11 sont chacun adressés par au moins un test ou un garde-fou explicite. Pas de scope reduction, pas de contradiction CONTEXT.md, pas de circular dependency.

**Aucun blocker.** Les 7 issues identifiées sont des frictions ou hardenings, exécutables après un commit léger ou pendant l'exécution sans bloquer le workflow.

**Prêt à exécuter** : OUI, après application des 2 issues MEDIUM (M-01, M-02) qui demandent <5 minutes chacune. Les 5 LOW peuvent être traitées pendant l'exécution ou après.

---

## 1. Requirement coverage matrix

| REQ-ID | Description | Plan(s) couvrant | Tâches concrètes | Verdict |
|--------|-------------|------------------|------------------|---------|
| HOU2-01 | Whole Sign | 15-02 (Tasks 1, 5, 7) | Création `whole_sign.py`, test `test_whole_sign_*` (9 tests), polar safety extension | COUVERT |
| HOU2-02 | Equal | 15-02 (Tasks 2, 6, 7) | Création `equal.py`, test `test_equal_*` (9 tests dont divergence cusp[9]≠MC) | COUVERT |
| HOU2-03 | Regiomontanus | 15-03 (Tasks 1-5) | Création `regiomontanus.py`, test 2-tier (algo + end-to-end + Reykjavik), polar NaN, polar_fallback integration | COUVERT |
| HOU2-04 | CLI listing 6 systèmes | 15-04 (Tasks 1-3) | Dispatcher dynamique parser, `_SYSTEM_DESCRIPTIONS` étendu, tests introspection (3 tests dont alphabétique) | COUVERT |
| HOU2-05 | Validation Swiss Ephemeris | 15-01 (Tasks 4-5) + 15-02/03 (algo-tier) + 15-04 (Task 7) | Snapshot 60 blocs, `test_loaded_reference_snapshot_matches_oracle` étendu, max ASC delta documenté inline | COUVERT |

**5/5 requirements ont au moins un test ratchet automatisé.** Cross-check avec PROJECT.md (REQUIREMENTS.md) : aucun REQ Phase 15 silencieusement droppé ; aucun REQ d'autre phase silencieusement importé.

## 2. Phase 15 success criteria → plan trace

| Success criterion (ROADMAP §119-126) | Fermé par | Test/preuve concrète |
|--------------------------------------|-----------|----------------------|
| **1.** `calculate_houses(..., system="whole_sign"\|"equal"\|"regiomontanus")` retourne HOUSES_DTYPE valide ; W/E polar-safe (no NaN à lat=80°) | 15-02 + 15-03 | `test_calculate_houses_routes_whole_sign`, `test_calculate_houses_whole_sign_polar_safe_no_fallback_needed`, idem equal, `test_polar_fallback_routes_regiomontanus_to_porphyry` |
| **2.** `--list-house-systems` retourne 6 systèmes (placidus, koch, porphyry, whole_sign, equal, regiomontanus) | 15-04 | `test_lists_registered_systems` étendu + `test_systems_listed_in_alphabetical_order` (D-03) |
| **3.** Chaque nouveau système passe l'oracle 10-charts vs Swiss Ephemeris ; max ASC delta documenté | 15-01 + 15-02 + 15-03 | `test_loaded_reference_snapshot_matches_oracle` étendu (60 blocs) + `test_*_algorithm_matches_oracle_armc_*` à 1e-6° + Reykjavik mesure inline |
| **4.** `ketu houses --date 2025-06-21T12:00:00Z --lat 48.85 --lon 2.35 --system whole_sign` imprime 12 cusps via dispatch existant | 15-04 | Task 7 vérification inline + `TestHousesCmdMatchesPythonAPI::test_cli_cusps_match_python_api` paramétré 6 systèmes × 3 locations = 18 cas |

**Verdict success criteria : 4/4 fermés explicitement par les plans.**

## 3. Locked decisions trace (CONTEXT.md → plans)

| D-XX | Decision | Plan(s) appliquant | Vérifié dans |
|------|----------|--------------------|--------------|
| D-01 | HOUSES_DTYPE['system'] U10→U16 + CHANGELOG | 15-01 | Task 1, action explicite + CHANGELOG entry verbatim |
| D-02 | Polar Regiomontanus = NaN propagation Koch-style (PAS swap MC↔IC) | 15-03 | Task 1, polar_mask + np.where(NaN), commentaire ratchet "NO swisseph MC↔IC swap" |
| D-03 | CLI ordering = `sorted(SYSTEMS.keys())` alphabétique | 15-04 | Task 1, Task 3 (`test_systems_listed_in_alphabetical_order`) |
| D-04 | Module naming = `whole_sign.py` / `equal.py` / `regiomontanus.py` | 15-02, 15-03 | Files créés exactement à ces chemins |
| D-05 | `_asc1` factorisé vers `_ecliptic.py` | 15-01 (extraction), 15-03 (consommation) | Task 2 plan 15-01 + import dans regiomontanus.py |
| D-06 | Snapshot script `scripts/snapshot_reference_charts.py` créé | 15-01 | Task 4, code complet inline |
| D-07 | Parser `--system choices = sorted(SYSTEMS.keys())` dynamique | 15-04 | Task 1, action explicite |
| D-08 | Test legacy `tests/cli/test_houses_cmd.py:53-59` à inverser | 15-04 | Task 4, avant/après + `test_v12_systems_accepted` |
| D-09 | Helpers underscore-internal restent privés | 15-01, 15-03 | `_asc1` reste underscore-prefixed dans `_ecliptic.py`, Plan 15-02 docstring explicite "Le re-export se fait via SYSTEMS, pas par import direct" |

**Verdict locked decisions : 9/9 implémentées explicitement.** Aucun D-XX absent. Aucune contradiction.

## 4. Pitfalls trace (RESEARCH §11 → mitigations)

| Pitfall | Mitigation prévue | Plan |
|---------|-------------------|------|
| 1 — Polar swap order avant sign-floor (Whole Sign) | Code 15-02 Task 1 : swap explicitement avant `np.floor(asc/30)*30` ; commentaire "Pitfall 1" inline | 15-02 |
| 2 — Trigger import oublié dans `__init__.py` | 15-02 Task 3 + 15-03 Task 2, commentaire `# noqa: F401  registers 'NAME' in SYSTEMS`, garde-fou par tests `test_*_registered_in_systems` | 15-02, 15-03 |
| 3 — ASC = 0° boundary case (Whole Sign) | `test_whole_sign_asc_at_sign_boundary_yields_cusp_1_zero` | 15-02 |
| 4 — Pole height vs geographic latitude (Regiomontanus) | Variables nommées `pole_height_outer`/`pole_height_inner` ; grep ratchet dans verification gates ; `test_regiomontanus_no_silent_nan_at_mid_latitudes` | 15-03 |
| 5 — `_asc1` callers post-extraction (Koch) | 15-01 Task 2 grep final ratchet (`grep -c "def _asc1" koch.py == 0`) ; régression Phase 10 | 15-01 |
| 6 — Snapshot regen oublie systèmes existants | 15-01 Task 4 itère `SYSTEM_BYTES.items()` (6 entrées) — pas de hardcode ; commentaire "Pitfall 6" inline | 15-01 |
| 7 — Test legacy `test_invalid_system_rejected` (utilise `regiomontanus` comme invalide) | 15-04 Task 4 : substitué par `nonexistent_xyz` ; `test_v12_systems_accepted` ratchet positif | 15-04 |

**Verdict pitfalls : 7/7 explicitement adressés.**

## 5. Wave ordering & dependencies

```
Wave 1 (séquentiel bloquant)
  └── 15-01 (foundation: snapshot script, DTYPE U16, _asc1 extraction, SYSTEM_BYTES)

Wave 2 (parallèle puis convergent)
  ├── 15-02 (Whole Sign + Equal) ─┐
  ├── 15-03 (Regiomontanus)       ├──> 15-04 (CLI + closure)
  └─ depends_on: [15-01]          │
     parallelizable: 15-02 ‖ 15-03┘
```

**Vérification :**
- 15-01 `depends_on: []` ✓ (Wave 1)
- 15-02 `depends_on: [15-01]` ✓ (consomme `_asc1` ? Non, mais snapshot étendu OUI ; consomme U16 ? Non directement, mais c'est défensif)
- 15-03 `depends_on: [15-01]` ✓ (consomme `_asc1` via `from ._ecliptic import _asc1` — critique)
- 15-04 `depends_on: [15-02, 15-03]` ✓ (CLI doit voir les 6 systèmes enregistrés via `SYSTEMS.keys()`)
- Aucun cycle. Aucune référence à un plan inexistant. Aucune référence forward.

**File ownership** (No Conflict Map dans PLANS-OVERVIEW.md vérifié) : seul `ketu/houses/__init__.py` est touché par 15-02 ET 15-03 — append-only et disjoints (2 lignes vs 1 ligne distincte). Merge git trivial dans n'importe quel ordre.

## 6. Scope sanity

| Plan | Tasks | Files modifiés/créés | Estimated context | Verdict |
|------|-------|----------------------|-------------------|---------|
| 15-01 | 6 | 9 | ~45% | LIMITE — 6 tâches dépasse le target 2-3 mais chaque tâche est atomique (1 fichier, 1 action). Acceptable car c'est de la fondation ratchet, pas de la logique métier. **WARNING LOW** (L-01) |
| 15-02 | 7 | 7 | ~50% | LIMITE — 7 tâches couvre 2 systèmes très similaires en un plan (recommandation researcher §10 : "two-trivial-systems"). Acceptable. **WARNING LOW** (L-02) |
| 15-03 | 6 | 5 | ~45% | OK — Regiomontanus seul + tests + Reykjavik measurement |
| 15-04 | 7 | 4 | ~40% | LIMITE — 7 tâches dont 3 sont vérification/régression (gates Phase 13/15). Acceptable car post-merge plan. |

**Verdict scope : aucun plan ne dépasse 80% context, mais 3 plans sur 4 sont à la borne haute (6-7 tasks). Pas de blocker, friction LOW signalée.**

## 7. must_haves derivation

Chaque plan a un bloc `must_haves` complet avec :
- `truths` : 6-8 affirmations user-observable (✓ pas implementation-focused)
- `artifacts` : files créés avec `provides` + `min_lines`/`contains` (✓)
- `key_links` : wiring explicite avec `pattern` regex (✓)

**Spot-check 15-01 truth #2** : *"`HOUSES_DTYPE['system']` accepte la string `'regiomontanus'` (13 chars) sans troncature"* — testable, user-observable, traçable au D-01. ✓

**Spot-check 15-02 truth #6** : *"Equal cusps[9] = (asc + 270) mod 360 ≠ MC astronomique réel ; cette divergence est testée et documentée"* — testable via `test_equal_cusp_10_is_asc_plus_270_not_astronomical_mc`. ✓

**Verdict must_haves : tous les plans ont des truths user-observable et des artifacts/key_links cohérents.**

## 8. Cross-cutting v1.2 constraints

| Constraint | Vérifié dans plans | Verdict |
|------------|--------------------|---------|
| Non-breaking minor strict | DTYPE U10→U16 documenté CHANGELOG comme additive ; aucun défaut changé ; aucun export retiré | OK |
| Pure-NumPy (pas de scipy ; swisseph test-only) | 15-02/03 : "AGPL boundary preserved" gate (`assert not any(n.startswith('swe') for n in dir(m))`) ; 15-01 snapshot script vit sous `scripts/`, pas `ketu/` | OK |
| Vectorizable (pas de boucle Python sur S) | 15-02/03 : `np.broadcast_arrays`, stack-able cusps, test `test_*_vectorised_matches_scalar_per_element` | OK |
| Mypy `--strict` clean | Verification gate dans chaque plan | OK |
| Coverage ≥95% nouveaux modules | 15-02 Task gate `--cov-fail-under=95` ; 15-03 idem ; 15-04 gate project-wide | OK |
| Doc gates Phase 13 (numpydoc + interrogate ≥95%) | 15-04 Task 5 explicite ; 15-01/02/03 inclus dans gates | OK |

**Verdict v1.2 constraints : tous explicitement adressés.**

## 9. Issues identifiées (par sévérité)

### MEDIUM — à corriger avant exécution

#### M-01 — Help text de `--system` dans parser.py:57 et 137 mentionne uniquement les 3 systèmes v1.1

**Plan :** 15-04 Task 1
**Severity :** MEDIUM (UX-relevant, contradiction visible avec D-07)
**Description :** `parser.py:57` contient `"List available house systems (placidus, koch, porphyry) and exit."` (help du flag `--list-house-systems` au top-level). Le plan 15-04 Task 1 modifie correctement la ligne 137 (help du `--system` du subcommand `houses`) mais **ne mentionne pas** la mise à jour de la ligne 57. Une fois exécuté, l'utilisateur verra :

```
ketu --help
  --list-house-systems  List available house systems (placidus, koch, porphyry) and exit.
                        # ↑ MENT — affiche en réalité 6 systèmes
```

**Fix recommandé :** dans 15-04 Task 1, ajouter une 2e modification de `parser.py` :
- ligne 57 : changer le help string statique en dynamique (`f"List available house systems ({len(_HOUSE_SYSTEMS)}: {', '.join(sorted(_HOUSE_SYSTEMS))}) and exit."`) OU rendre générique (`"List all registered house systems and exit."`).

**Impact si non corrigé :** le test `test_lists_registered_systems` passe quand même (il vérifie l'output runtime, pas le help statique), mais la doc CLI est trompeuse — friction UX visible.

#### M-02 — Test `test_equal_cusp_1_equals_ascendant` (15-02 Task 6) ne teste pas vraiment l'égalité cusp[0]==asc

**Plan :** 15-02 Task 6
**Severity :** MEDIUM (test ratchet boguée, faux sens de sécurité)
**Description :** Le test rédigé ligne 671-689 contient :

```python
assert abs(float(cusps[0]) % 360.0 - float(cusps[0])) < 1e-9
```

Cette assertion est **trivialement vraie** pour tout `cusps[0] ∈ [0, 360)` — elle vérifie `x % 360 == x`, pas `cusps[0] == asc`. Il manque l'assertion réelle :

```python
asc = float(ascmc["asc"])
# Account for polar swap inside equal_cusps (may flip ASC by 180°)
assert abs(((float(cusps[0]) - asc + 180.0) % 360.0) - 180.0) < 1e-6  # short-arc
```

**Fix recommandé :** dans 15-02 Task 6, remplacer l'assertion noop par une vraie comparaison short-arc avec `ascmc["asc"]` (Paris J2000 n'a pas de swap polaire — ASC ≈ 26.77° devrait égaler cusps[0] à 1e-6° près).

**Impact si non corrigé :** le test passe mais ne ratchet RIEN. Si `equal_cusps` retournait `cusps[0] = 999.0 % 360 = 279.0` (bogue), le test passerait. Faux sens de sécurité.

### LOW — frictions, exécutables après ou pendant

#### L-01 — Plan 15-01 a 6 tasks (au-dessus du target 2-3)

**Plan :** 15-01
**Severity :** LOW
**Description :** 6 tâches dans un seul plan dépasse le target plan-checker. Toutes les 6 sont atomiques (1 fichier, 1 action) et le plan est de la fondation ratchet, pas de logique métier. Acceptable mais à surveiller pendant exécution — si le contexte d'exécution sature à 70%, splitter en 15-01a (DTYPE + CHANGELOG) et 15-01b (snapshot + `_asc1` + SYSTEM_BYTES).

**Fix recommandé :** ne rien faire pour l'instant ; surveiller `gsd-execute-phase` context usage sur 15-01.

#### L-02 — Plan 15-02 a 7 tasks (au-dessus du target 2-3)

**Plan :** 15-02
**Severity :** LOW
**Description :** Idem L-01 mais pour 15-02 (qui couvre 2 systèmes en un plan, recommandation researcher). Les 7 tâches sont : 2 modules prod, 1 init.py, 1 api.py, 2 tests, 1 polar_safety. Toutes atomiques. Si saturation, splitter en 15-02a (Whole Sign) et 15-02b (Equal).

#### L-03 — `tests/houses/test_dtype.py:43` actuel teste déjà `whole_sign` en U10

**Plan :** 15-01 Task 1
**Severity :** LOW (informationnel)
**Description :** Le fichier actuel `tests/houses/test_dtype.py:42-46` est déjà :

```python
"""system field is U10 — fits 'placidus', 'koch', 'porphyry', 'whole_sign'."""
for name in ("placidus", "koch", "porphyry", "whole_sign"):
```

C'est-à-dire que la convention `whole_sign` (10 chars) tient déjà en U10 — vérifié par les auteurs précédents. Le bump U10→U16 est donc **uniquement** nécessaire pour `regiomontanus` (13 chars), pas pour `whole_sign`. Le PATTERNS.md §metadata ligne 798 mentionne ce fait. Le plan 15-01 Task 1 le gère correctement (étend la tuple à 6 noms et bump à U16) — aucun bug, mais le commit message du plan pourrait clarifier que U10 marchait pour `whole_sign` mais pas pour `regiomontanus` (D-01 reste correct, juste le wording).

**Fix recommandé :** dans le commit message Task 1 (ligne 580), modifier `Bump HOUSES_DTYPE['system'] U10 -> U16 to fit "regiomontanus" (13 chars) without truncation` (déjà mentionné — précis). RAS, aucune action requise.

#### L-04 — `_asc1` dans `_ecliptic.py` (Plan 15-01 Task 2) — le commentaire docstring annonce "underscore-internal" mais le module est déjà documenté comme RA↔ecliptic helpers

**Plan :** 15-01 Task 2
**Severity :** LOW (cosmétique)
**Description :** Le module `_ecliptic.py` actuel a un docstring header (vérifié) qui parle de `ra_to_lambda` / `lambda_to_ra` (RA↔ecliptic). Ajouter `_asc1` (qui est ARMC + pole-height → ecliptic longitude via great circle) étend la portée du module. Le docstring header devrait être mis à jour pour mentionner `_asc1` aussi — sinon le module description et son contenu divergent. Le plan ne le mentionne pas explicitement.

**Fix recommandé :** dans 15-01 Task 2, ajouter une 3e action : "Update `_ecliptic.py` module docstring (lignes 1-9) pour mentionner `_asc1` aux côtés de `ra_to_lambda` / `lambda_to_ra`". Friction documentaire mineure.

#### L-05 — Plan 15-03 Task 5 (Reykjavik measurement) — placeholder `5.0 arcmin` dans test au moment du commit Wave 2

**Plan :** 15-03 Task 5
**Severity :** LOW (procédure manuelle bien encadrée mais à surveiller)
**Description :** Le constant `REYKJAVIK_REGIO_TOL_ARCMIN: float = 5.0 * ARCMIN_DEG` est rédigé comme placeholder dans le code de test (line 364). Task 5 demande à l'implémenteur de mesurer empiriquement et de remplacer la valeur. Si l'implémenteur oublie cette étape, le test passe avec une tolérance trop laxiste (5′) — perte de ratchet. Le decision-tree de Task 5 est correct mais ne contient pas de garde automatique.

**Fix recommandé :** ajouter dans Task 5 une dernière sous-étape : "Vérifier que la valeur finale dans `REYKJAVIK_REGIO_TOL_ARCMIN` n'est plus `5.0 * ARCMIN_DEG` (le placeholder) — si elle l'est, le commit est rejeté." Ratchet possible via grep dans verification gate :

```bash
grep -E "REYKJAVIK_REGIO_TOL_ARCMIN: float = 5\.0 \* ARCMIN_DEG  # initial" tests/houses/test_regiomontanus.py && echo "FAIL: Reykjavik tolerance still placeholder" && exit 1
```

**Impact si non corrigé :** drift Reykjavik réelle non ratchetée. Friction long terme (un futur regression de eps_mean serait masquée).

## 10. Architectural tier compliance

RESEARCH.md §"Architectural Responsibility Map" identifie clairement :
- `ketu/houses/*.py` (production tier) — algorithmes, registry, polar logic
- `tests/houses/*.py` (test tier) — oracle, AGPL boundary swisseph
- `ketu/cli/*.py` (CLI tier) — parser, introspection
- `scripts/*.py` (tooling tier) — snapshot regen (swisseph dépendance acceptable hors prod)

**Vérification plans :**
- Aucune logique métier algo dans `ketu/cli/*` (15-04 ne touche que parser/introspection — OK)
- Aucun import `swisseph` dans `ketu/houses/*` (15-01/02/03 vérifié par `test_calculate_houses_no_runtime_swisseph_import` ratchet existant)
- Snapshot script vit dans `scripts/` (pas `ketu/`) — AGPL boundary respecté

**Verdict tier compliance : aucune violation.**

## 11. Cross-plan data contracts

**Données partagées entre plans :**
- `_asc1` : produit par 15-01 (extraction), consommé par 15-03 (Regiomontanus). Contract : `(x, lat_or_pole_height, sin_eps, cos_eps) -> deg`. Vérifié par `test_koch.py` (régression 15-01) + `test_regiomontanus_*` (consommation 15-03). Pas de transformation incompatible.
- `SYSTEMS` registry : Wave 1 vide pour les nouveaux ; Wave 2 le peuple. CLI 15-04 lit après Wave 2 complete via `sorted(SYSTEMS.keys())` — séquencement explicite par dependencies graph.
- `reference_charts.json` snapshot : produit par 15-01 (60 blocs), consommé par 15-02/03 (`test_loaded_reference_snapshot_matches_oracle`). Format JSON identique à v1.1 (ajout de clés systems, pas de modification des champs existants). Pas de breaking change interne.
- `HOUSES_DTYPE` : 15-01 bump U10→U16 ; tous les plans Wave 2 lisent/écrivent `out["system"] = "regiomontanus"` qui ne tient qu'avec U16. Critique — vérifié par `test_dtype_string_field_capacity` étendu.

**Verdict cross-plan : aucun conflit, aucune transformation incompatible.**

## 12. CLAUDE.md compliance

`CLAUDE.md` impose :
- **Persona Sophie Chen / FR / tutoiement** : tous les plans rédigés en français avec persona ✓
- **Standalone Ketu** : aucune dépendance MarketStream/Kala dans plans ✓
- **Venv `venv/` (pas `.venv/`)** : non-applicable aux plans ✓
- **NumPy first / Structured arrays** : tous les algorithmes Wave 2 sont vectorisés via `np.broadcast_arrays` ; tests `test_*_vectorised_matches_scalar_per_element` ratchent la promesse ✓
- **Type hints partout** : signatures `(armc: np.ndarray, lat: np.ndarray, eps: np.ndarray) -> np.ndarray` dans 15-02/03 ✓
- **DateTime UTC** : non-applicable directement (les `jd` Julian Date UT sont déjà UTC par convention v1.1) ✓

**Verdict CLAUDE.md compliance : aucune violation.**

## 13. Research resolution

`15-RESEARCH.md` §14 (Risques) liste 5 points d'attention. Tous sont adressés :
- §14.1 (cusps[0] Whole Sign divergence) → test `test_whole_sign_cusp_1_is_start_of_rising_sign` (15-02)
- §14.2 (cusps[9] Equal divergence) → test `test_equal_cusp_10_is_asc_plus_270_not_astronomical_mc` (15-02)
- §14.3 (Reykjavik tolerance) → Task 5 measurement procedure (15-03)
- §14.4 (polar boundary Regio) → polar_mask `|lat| ≥ 90 - eps` (15-03 Task 1, identique à Koch — D-02)
- §14.5 (Sophie hint `_SYSTEM_DESCRIPTIONS`) → `test_every_registered_system_has_description` (15-04 Task 3)

`15-CONTEXT.md` `<deferred>` (Campanus, sidereal Whole Sign, MC-anchored Equal, JSON output, alias court) : aucun plan ne les implémente ✓ (vérification grep dans plans : pas de mention de "campanus", "sidereal", "MC-anchored", "json output", "alias regio" sauf en notes négatives).

**Verdict research resolution : toutes les questions/risques tranchés ; aucune deferred idea silencieusement importée.**

## 14. Pattern compliance

`15-PATTERNS.md` mappe 9 fichiers nouveaux à leurs analogues. Vérification spot-check :

| Fichier nouveau | Analogue PATTERNS | Plan applique l'analogue | Verdict |
|-----------------|-------------------|--------------------------|---------|
| `whole_sign.py` | `porphyry.py` (closed-form polar-safe) | 15-02 Task 1 mirror du squelette + adaptation `cusp_1 = floor(asc/30)*30` | OK |
| `equal.py` | `porphyry.py` | 15-02 Task 2 idem | OK |
| `regiomontanus.py` | `koch.py` (closed-form polar→NaN) | 15-03 Task 1 mirror + `_asc1` réutilisé via `_ecliptic.py` | OK |
| `__init__.py` modify | self lignes 41-43 | 15-02 Task 3 + 15-03 Task 2 append-only | OK |
| `test_whole_sign.py` | `test_porphyry.py` | 15-02 Task 5 mirror + sign-floor test | OK |
| `test_equal.py` | `test_porphyry.py` | 15-02 Task 6 mirror + cusp[9] divergence test | OK |
| `test_regiomontanus.py` | `test_koch.py` (two-tier oracle, Reykjavik pinned) | 15-03 Task 3 mirror complet + Reykjavik measurement | OK |
| `conftest.py:SYSTEM_BYTES` | self lignes 77-81 | 15-01 Task 3 append-only | OK |
| `introspection.py:_SYSTEM_DESCRIPTIONS` | self lignes 22-26 | 15-04 Task 2 append-only | OK |

**Verdict pattern compliance : 9/9 patterns explicitement consommés.**

## 15. Nyquist compliance (VALIDATION.md)

VALIDATION.md liste 14 tasks (15-01-01..15-04-04) avec `<automated>` commands. Vérification :
- Wave 0 requirements (5 stubs créés OU dépendances) : tous les MISSING tests référencent un plan créateur (15-01/02/03)
- Sampling rate : `pytest tests/houses/ -x -v` après chaque task ; `--cov` après chaque wave ; doc gates avant `gsd-verify-work` — feedback latency <30s/task
- Pas de watch-mode flags ; pas de E2E full suite > 30s

**Verdict nyquist : compliant. Le frontmatter `nyquist_compliant: false` actuel doit flipper à `true` après ce review.**

## 16. Récapitulatif des actions à prendre

### Avant exécution (MEDIUM, ~5 minutes)

1. **M-01** : 15-04 Task 1 — étendre la modif à `parser.py:57` (help du `--list-house-systems`).
2. **M-02** : 15-02 Task 6 — corriger l'assertion noop dans `test_equal_cusp_1_equals_ascendant`.

### Pendant ou après exécution (LOW)

3. **L-01/L-02** : surveillance contexte exécution sur 15-01 et 15-02 ; splitter si saturation.
4. **L-03** : RAS, juste informationnel.
5. **L-04** : 15-01 Task 2 — étendre le header docstring de `_ecliptic.py` pour inclure `_asc1`.
6. **L-05** : 15-03 Task 5 — ajouter grep ratchet pour interdire le placeholder Reykjavik.

### Aucune action immédiate requise

- Wave structure correcte
- Dependencies acycliques
- 5/5 REQs couverts
- 4/4 success criteria fermés
- 9/9 locked decisions implémentées
- 7/7 pitfalls adressés
- 12/14 plan-checker dimensions PASS, 2 SKIPPED (dimension 7c "Architectural Responsibility Map" couvert mais simple, et nyquist auto-pending)

---

## Verdict final

**STATUS : PASS_WITH_MINOR_REVISIONS**

**Décision : prêt à exécuter après application de M-01 et M-02 (~5 minutes).**

Les 5 LOW peuvent être traités pendant l'exécution ou consignés comme tickets de suivi. L'orchestrateur `gsd-execute-phase` peut démarrer Wave 1 (15-01) immédiatement après le micro-fix M-02 (qui touche Wave 2 plan 15-02 Task 6 — sans bloquer Wave 1).

**Configuration recommandée pour `/gsd-execute-phase 15` :**
- Exécuter Wave 1 (15-01) en séquentiel.
- Exécuter Wave 2 (15-02 ‖ 15-03) en parallèle deux agents.
- Exécuter 15-04 après merge des deux Wave 2.
- Surveiller le `_asc1` import dans 15-03 (dépendance critique sur 15-01 Task 2).
- Re-run `/gsd-plan-phase 15 --review` après corrections M-01/M-02 pour valider.

---

*Plan-checker review : Sophie Chen — gsd-plan-checker — 2026-05-09*
*Méthodologie : goal-backward verification (12 dimensions). Adversarial stance maintenue.*
*Aucun blocker identifié — phase prête à exécuter après corrections mineures.*
