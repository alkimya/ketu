# Phase 15: Additional House Systems — Context

**Gathered:** 2026-05-09
**Status:** Ready for planning
**Source:** Inline orchestrator capture (post-research, pre-plan)

<domain>
## Phase Boundary

Ajouter trois nouveaux house systems (Whole Sign, Equal, Regiomontanus) au registry `SYSTEMS` existant (Phase 10), validés contre Swiss Ephemeris sur les 10 reference charts. Phase **indépendante de Phase 14** : pas de changement à `compute_chart` ni à `CHART_DTYPE`. Extension par registre pur, additive.

</domain>

<decisions>
## Implementation Decisions

### Naming & dtype capacity
- **`HOUSES_DTYPE['system']` étendu de `U10` → `U16`** pour accommoder `"regiomontanus"` (13 chars).
  - Documenté dans CHANGELOG `[Unreleased]` `### Changed` avec disclaimer non-breaking : valeurs comparables par contenu, cast U10⇄U16 transparent en NumPy.
  - Pas d'alias court (`regio`) — on garde le nom canonique communauté astro / swisseph.
- Trois nouveaux modules : `ketu/houses/whole_sign.py`, `equal.py`, `regiomontanus.py` (un fichier par système, mimétisme `koch.py` / `porphyry.py`).

### Polar safety
- **Whole Sign / Equal** : polar-safe par construction (n'utilisent que ASC qui est closed-form à toute lat<90°). Pas de NaN, pas de `HighLatitudeError`.
- **Regiomontanus** : NaN-propagation Koch-style à `|lat| ≥ 90 - eps_mean(jd)`. Cohérence avec HOU-06 — `polar_fallback="porphyry"` route automatiquement, `polar_fallback="raise"` lève `HighLatitudeError`. Pas de swisseph-style swap MC↔IC.

### Helper factorization
- **Extraire `_asc1` de `koch.py` vers un module interne** (e.g. `_ecliptic.py`) pour le réutiliser dans `regiomontanus.py`. Préserve DRY ; underscore-prefixé reste internal-only (non-breaking, non exporté).

### CLI integration
- **`--list-house-systems` ordering : alphabétique déterministe** via `sorted(SYSTEMS.keys())`. L'ordre HOU2-04 dans REQUIREMENTS est narratif, pas un contrat.
  - Output attendu : `equal, koch, placidus, porphyry, regiomontanus, whole_sign`.
- **Parser `--system` choices : dynamique** via `sorted(SYSTEMS.keys())` (au lieu du hardcode `["placidus","koch","porphyry"]` de v1.1).
- **`_SYSTEM_DESCRIPTIONS`** dans `ketu/cli/introspection.py` étendu avec les 3 nouvelles descriptions (FR + EN selon convention v1.1).

### Test à inverser
- `tests/cli/test_houses_cmd.py:53-59` (qui assert `--system regiomontanus` rejeté en v1.1) **doit être inversé** : c'est désormais un input valide. Le researcher l'a flaggé comme legacy-incompatible. Update, ne pas déprécier.

### Snapshot regeneration
- `scripts/snapshot_reference_charts.py` **n'existe pas** (référence aspirationnelle dans `tests/houses/conftest.py:248`). Il **doit être créé** dans Phase 15 (utile pour Campanus/Topocentric futurs aussi).
- Étendre `tests/houses/fixtures/reference_charts.json` avec 3 systèmes × 10 charts = 30 nouveaux blocs.

### Oracle gates
- Pattern v1.1 two-tier preservé :
  - **Tier 1 (algorithm)** : `swe_oracle_armc(armc, lat, eps, system)` vs implémentation Ketu, tolérance `1e-6°` (machine precision sur 8 charts non-polaires).
  - **Tier 2 (end-to-end snapshot)** : tolérance `1 arcmin` sur les 7 charts non-polaires "tight" ; Reykjavik attendu drift 2-5 arcmin pour Regio (pinned exception).
- Polar safety tests étendus : Whole Sign/Equal asser no-NaN à 70°/80°/89°, Regio asser NaN à `|lat| ≥ 90 - eps_mean(jd)`.

### Claude's Discretion (Phase 15)
- Découpage exact des plans (4 vs 5 vs 6) : laissé au planner, mais le researcher recommande 4 plans en 2 vagues (W1: registry+dtype+_asc1+snapshot, W2: 3 systèmes + CLI en parallèle).
- Naming des fichiers de test (`test_whole_sign.py` vs `test_houses_whole_sign.py`) : suivre la convention v1.1 — `tests/houses/test_<system>.py`.
- Structure du DTYPE bump (Plan 15-01 ou plan dédié) : laissé au planner.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 15 RESEARCH + PATTERNS
- `.planning/phases/15-additional-house-systems/15-RESEARCH.md` — Formules canoniques (swisseph C cases W/E/R), 7 pitfalls, validation architecture, 4-plan découpage proposé
- `.planning/phases/15-additional-house-systems/15-PATTERNS.md` — Mapping file:line des analogues (`koch.py`/`porphyry.py` pour les algos, two-tier oracle pour les tests)

### Roadmap & requirements
- `.planning/ROADMAP.md` (lignes 108-126) — Phase 15 success criteria
- `.planning/REQUIREMENTS.md` (HOU2-01..05, lignes 19-26)

### Code à modifier / référencer
- `ketu/houses/registry.py` — décorateur `@register`, contrat `HouseSystemFn`
- `ketu/houses/core.py:35-45` — `HOUSES_DTYPE` (à bump U10→U16 sur le champ `system`)
- `ketu/houses/api.py:126` — liste polar-safe à étendre `{"porphyry", "whole_sign", "equal"}`
- `ketu/houses/koch.py` — pattern Regio (closed-form NaN polar) + helper `_asc1` à factoriser
- `ketu/houses/porphyry.py` — pattern Whole Sign/Equal (closed-form polar-safe)
- `ketu/houses/__init__.py:41-43` — trigger imports à étendre
- `ketu/cli/parser.py:135` — `choices` à passer dynamique via `sorted(SYSTEMS.keys())`
- `ketu/cli/introspection.py:_SYSTEM_DESCRIPTIONS` — étendre avec 3 entrées
- `tests/houses/conftest.py:SYSTEM_BYTES` — ajouter `b"W"`, `b"E"`, `b"R"`
- `tests/houses/fixtures/reference_charts.json` — régénérer (snapshot)
- `tests/cli/test_houses_cmd.py:53-59` — inverser le test legacy

### v1.1 milestone (oracle pattern)
- `.planning/milestones/v1.1-ROADMAP.md` — Phase 10 Houses Module (oracle pattern, polar fallback, HighLatitudeError contract)

### Cross-cutting v1.2 constraints
- Non-breaking minor strict (additive only, aucun défaut changé, aucun export retiré)
- Pure-NumPy (pas de scipy, swisseph reste test-only AGPL)
- Vectorizable (pas de boucle Python sur la shape S dans le hot path)
- Coverage ≥95% sur le code nouveau, ≥85% par module
- Doc gates Phase 13 : numpydoc validate clean, interrogate ≥95%
- Mypy --strict clean

</canonical_refs>

<specifics>
## Specific Ideas

- **Whole Sign formule** : `cusp[k] = (floor(asc/30)*30 + 30*k) mod 360` — alignement sur le signe de l'ASC (pas l'ASC lui-même comme cusp[0]).
- **Equal formule** : `cusp[k] = (asc + 30*k) mod 360`. `cusps[9]` = `(asc+270) mod 360` ≠ MC astronomique — divergence intentionnelle, à documenter dans la docstring.
- **Regiomontanus** : `fh1 = atan(tan(lat)/2)`, `fh2 = atan(tan(lat) * cos(30°))`, puis 4 appels à `_asc1(armc + offset_k, fh_k, sin_eps, cos_eps)`. Stack-able vectorisable en une passe. Cf. swisseph `swehouse.c` case `'R'`.
- **DTYPE bump U10→U16** : `np.dtype([..., ("system", "U16"), ...])`. Vérifier `tests/houses/test_dtype.py` (s'il pin la capacité U10) — adapter.
- **Snapshot script** : créer `scripts/snapshot_reference_charts.py` qui itère 10 charts × 6 systèmes via `swe.houses_ex()` et écrit `tests/houses/fixtures/reference_charts.json`. Idempotent ; `python scripts/snapshot_reference_charts.py --check` pour valider sans réécrire.

</specifics>

<deferred>
## Deferred Ideas

- **Campanus, Topocentric, Alcabitius** — registry les supportera mais pas livrés v1.2 (REQUIREMENTS « Out of Scope »). Le snapshot script doit être conçu pour les accommoder au moment voulu (v1.3+).
- **Sidereal Whole Sign / ayanamsha** — Phase 15 = tropical only. Branche sidereal de swisseph case `'W'` non implémentée.
- **MC-anchored Equal (système 'D' swisseph)** — HOU2-02 explicitement ASC-anchored. Variante reportée.
- **JSON output pour `--list-house-systems`** — pas dans le scope HOU2-04.
- **Alias court `regio`** — décision : on garde le nom canonique long.

</deferred>

---

*Phase: 15-additional-house-systems*
*Context capturé: 2026-05-09 inline post-research (4 questions ouvertes du researcher tranchées : DTYPE U10→U16, polar Regio NaN-style Koch, CLI alphabétique, pas d'alias)*
