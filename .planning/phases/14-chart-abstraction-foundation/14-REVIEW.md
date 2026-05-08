---
phase: 14
phase_name: chart-abstraction-foundation
review_date: 2026-05-09
depth: standard
files_reviewed: 12
status: warnings
critical_count: 0
warning_count: 3
info_count: 5
---

# Phase 14 — Code Review Report

**Reviewé :** 2026-05-09
**Profondeur :** standard (per-file analysis)
**Fichiers reviewés :** 12 (3 prod + 7 tests + 2 config)
**Status :** warnings (aucun blocker, 3 warnings, 5 info)

## Summary

Travail solide et discipliné. Le sous-package `ketu/charts/` est essentiellement un copier-adapter du gabarit `ketu/houses/` v1.1, et ça se voit positivement : conventions respectées (`from __future__ import annotations` partout, `__all__` trié, type alias importé depuis presets et non redéfini, AGPL boundary verrouillée par ratchet test). Le contrat CHART_DTYPE est gelé proprement, la docstring "Why a structured array?" est présente, et les sentinelles D-06 (-1 / NaN) sont round-trippées par les tests structurels.

Les 844 tests passent, la couverture `ketu/charts/` est à 100 %, mypy --strict est clean, interrogate à 100 %, et numpydoc lint passe. Les Done criteria sont tous atteints.

Cela dit, l'analyse adversariale a remonté **trois warnings** méritent attention avant que les Phases 16/17/18/19 consomment ce contrat :

1. **Divergence subtile docstring/code sur D-13** : la convention sunrise-inclusive est documentée mais le code retourne `False` pour Sun exactement sur ASC (la docstring le reconnaît mais le justifie par "measure zero" — ce qui n'est pas un argument de correctness, c'est une dette).
2. **Inconsistance cross-API silencieuse** entre `is_day_chart` (Placidus hardcodé) et `compute_chart` (système caller-driven). En pratique invariant pour Placidus/Koch/Porphyry, mais Phase 15 ajoutera Whole Sign / Equal — où DESC ≠ ASC + 180.
3. **Précision houses inline cross-check** : la tolérance `HOUSES_INLINE_TOL_DEG = 1e-9` est plus laxiste que ce que la docstring promet ("bit-for-bit"). Cohérent avec ce que le code peut garantir, mais l'écart est sémantique.

Les 5 items Info sont des opportunités de polish, pas des défauts.

Aucun **BLOCKER** : pas de bug bloquant, pas de violation AGPL, pas de risque de data loss, pas de gap sécurité.

---

## Critical findings

Aucun.

---

## Warnings

### WR-01: Convention D-13 `Sun == ASC = day` violée par le code (sunrise-inclusive incomplète)

**Sévérité :** Warning
**Fichier :** `ketu/charts/api.py:392-403, 480`

**Issue :**
La décision D-13 (CONTEXT.md ligne 50) stipule explicitement : "Sect convention — sunrise-inclusive : `Sun >= ASC = day` (Hellenistic standard, matches Solar Fire / Astro.com / Robert Hand). Equality at the horizon resolves to **day**."

Le code retourne `np.asarray(sun_house >= 7)`. Or `house_of` applique la convention "cusps[i] BEGINS house i+1" : un Sun *exactement* sur l'ASC mappe vers la house 1, donc `sun_house >= 7` retourne `False` (night). Le code retourne donc **night** dans le cas-limite que D-13 exige être **day**.

La docstring de `is_day_chart` (ligne 392-403) reconnaît cette divergence et la justifie par "measure zero against real ephemeris data". C'est un argument de probabilité, pas de correctness contractuelle. Si jamais un caller construit une fixture de test (Phase 19 pourrait), ou si un caller passe un `sun_lon` synthétique (cf. le test `test_is_day_chart_sunrise_inclusive_pragmatic_convention` lui-même qui le fait à ±0.01), le contrat D-13 est violé silencieusement.

J'ai vérifié empiriquement à Paris J2000 :

```python
asc = 26.7757...
house_of(asc, cusps) → 1
is_day_chart(...with Sun==asc...) → False  # mais D-13 dit True
```

**Recommandation :**
Deux options propres :

1. **Corriger le code** pour matcher D-13 littéralement. Trois lignes :
   ```python
   sun_house = house_of(sun_lon, houses["cusps"])
   asc = houses["asc"]
   on_asc = np.isclose(sun_lon % 360.0, asc % 360.0, atol=1e-9)
   return np.asarray((sun_house >= 7) | on_asc)
   ```
   Coût : un broadcast supplémentaire, une comparaison NaN-safe à ajouter (Porphyry interne ne génère pas de NaN sur asc, donc OK).

2. **Adoucir D-13** dans CONTEXT.md pour reconnaître que la convention est "sunrise-inclusive *modulo numerical precision*", et documenter explicitement le comportement de bord. Cela aligne la spec sur le code mais demande un amendement de décision.

Sophie aimerait l'option 1 — la convention Hellenistic est documentée comme inclusive et c'est ce que les outils de référence (Solar Fire, Astro.com) implémentent. Le coût est marginal et la cohérence spec/code est récupérée. Si Phase 19 (Arabic Parts) construit un test "Lot of Fortune at sunrise = day", l'option 2 ne tiendra pas la promesse Hellenistic.

---

### WR-02: Inconsistance cross-API silencieuse `is_day_chart` (Placidus hardcodé) vs `compute_chart` (système caller)

**Sévérité :** Warning
**Fichier :** `ketu/charts/api.py:461-464`

**Issue :**
`is_day_chart` appelle `calculate_houses(jd_b, lat_b, lon_b, system="placidus", polar_fallback="porphyry")` avec **`"placidus"` hardcodé**. La docstring (ligne 459-460) justifie ce choix : "the day/night answer depends only on the Ascendant and the above-horizon hemisphere; Porphyry preserves both at every latitude, so the choice of system here is immaterial to the sect outcome".

L'argument tient pour Placidus / Koch / Porphyry : tous ont `cusp[6] (DESC) ≈ asc + 180`, donc `sun_house >= 7` ≡ `Sun ∈ [asc, asc+180)` (modulo 360). Mais :

1. **Phase 15 ajoutera Whole Sign et Equal** (CONTEXT.md ligne 21). Pour Whole Sign, `cusp[i] = floor(asc/30)*30 + i*30`, et `cusp[6]` (cusp 7) est à `cusp[0] + 180` MAIS `cusp[0]` n'est pas l'ASC — c'est le début du signe contenant l'ASC. Donc `sun_house >= 7` ne signifie plus "Sun above horizon" pour Whole Sign. Conséquence : si un caller fait `compute_chart(..., system="whole_sign")` puis `house_of(chart["body_lons"][0], chart["cusps"]) >= 7`, il obtient un résultat qui peut diverger de `is_day_chart(jd, lat, lon)`.

2. **Pas de test cross-API pour systèmes non-Placidus** : `test_is_day_chart_consistency_with_compute_chart_asc_and_sun_lon` n'utilise que `compute_chart(jd, lat, lon)` (Placidus par défaut). Aucun test ne vérifie cohérence avec Koch ou Porphyry.

3. **Le rationale de la docstring devient faux en v1.3** : si Phase 15 ajoute Whole Sign comme houses system documenté dans `compute_chart`, l'affirmation "the choice of system here is immaterial to the sect outcome" sera incorrecte sans modification.

**Recommandation :**

Option propre : **utiliser un calcul ASC-based, pas houses-based**, pour le sect. C'est ce que la définition Hellenistic dit littéralement :

```python
# Sect = Sun above horizon = Sun ∈ [ASC, ASC + 180) mod 360
asc = houses["asc"]
sun_lon_a = sun_lon % 360.0
asc_a = asc % 360.0
delta = (sun_lon_a - asc_a) % 360.0  # 0 inclus = day per D-13
return np.asarray(delta < 180.0)
```

Avantages :
- Indépendant du système de maison choisi (Whole Sign, Equal, Regiomontanus...)
- D-13 sunrise-inclusive automatiquement satisfait (delta=0 → day)
- Plus simple (pas besoin de `house_of`)
- Plus rapide (pas de calcul de cusps si Porphyry est juste pour l'ASC qui est déjà obtenu via `compute_ascmc` interne)

Si on garde l'implémentation actuelle, **a minima** :
- Ajouter un test qui exerce `compute_chart(..., system="koch")` et vérifie cohérence avec `is_day_chart` (ratchet pour quand Whole Sign arrive en Phase 15).
- Documenter explicitement dans la docstring que `is_day_chart` *ignore* le system du caller — une note "Notes" "We do NOT honor caller-side system choice; if you need sect by quadrant houses, derive it from your CHART_DTYPE directly".

---

### WR-03: Tolérance `HOUSES_INLINE_TOL_DEG = 1e-9` plus laxiste que la docstring promise

**Sévérité :** Warning
**Fichier :** `tests/charts/test_compute_chart.py:37, 100`

**Issue :**
La docstring de `test_compute_chart_houses_inline_matches_calculate_houses` dit : "D-03 ratchet: the houses block of CHART_DTYPE matches calculate_houses **bit-for-bit**." Le test compare avec `HOUSES_INLINE_TOL_DEG = 1e-9` (≈ 4 micro-arcsecondes).

`compute_chart` appelle `calculate_houses(jd_b, lat_b, lon_b, system, polar_fallback)` UNE fois et copie les fields directement. Ce sont les mêmes valeurs en mémoire — donc effectivement bit-exact (pas seulement 1e-9). La tolérance laxiste masquerait un bug subtil de copie (si jamais quelqu'un changeait le pipeline pour faire `chart["asc"] = float(houses["asc"])` au lieu d'une assignment broadcast, le f8→f8 reste bit-exact mais des conversions intermédiaires pourraient drifter).

Plus important : le SUMMARY 14-02 § Decisions Made #2 documente la tolérance pour les `body_lons` à `1e-12` (bit-exact). Pour les houses, la docstring dit "bit-for-bit" mais la tolérance numérique est `1e-9`. Inconsistance entre code et docstring.

**Recommandation :**
Renforcer la tolérance à `0.0` (égalité stricte) pour cusps + asc/mc/armc/vertex :
```python
np.testing.assert_array_equal(chart["cusps"], houses["cusps"])
for field in ("asc", "mc", "armc", "vertex"):
    assert chart[field] == houses[field], f"{system}/{label}: {field} drift"
```

Ça pin le contrat D-03 ("inline = bit-exact") proprement et catchera toute future régression introduisant un cast intermédiaire. Si jamais le test commence à fail, c'est un signal qu'un changement non-trivial a été introduit.

Si on veut être conservateur, descendre la tolérance à `1e-15` (garde une marge fp64 sans laisser passer des bugs).

---

## Info

### IN-01: Stockage de `system.lower()` dans CHART_DTYPE crée un drift potentiel avec `calculate_houses`

**Sévérité :** Info
**Fichier :** `ketu/charts/api.py:336`

**Issue :**
`compute_chart` fait `out["system"] = system.lower()` indépendamment de ce que `calculate_houses` stockerait dans son propre HOUSES_DTYPE. Aujourd'hui les deux lowercase identiquement, mais c'est une **double source-of-truth** : si jamais `calculate_houses` change sa normalisation (uppercase, kebab-case, alias resolution), `compute_chart` continuera de stocker `system.lower()` et les deux divergeront silencieusement.

**Recommandation :**
Lire la valeur depuis le retour de `calculate_houses` :
```python
out["system"] = houses["system"]
```
Single source-of-truth. Cohérent avec la philosophie "charts/ compose, ne ré-encapsule pas" (PATTERNS § 2 "Skip"). Ne change pas le test `test_compute_chart_meta_fields_lowercased_system` (qui passe toujours puisque `calculate_houses` lowercase aussi).

---

### IN-02: `aspect_orbs` peut contenir des valeurs négatives non documentées

**Sévérité :** Info
**Fichier :** `ketu/charts/core.py:67-69` (docstring CHART_DTYPE)

**Issue :**
La docstring dit : "`aspect_orbs` (f4, (13, 13)): orb in degrees; `NaN` means 'no orb'". Pas mention de signe.

`calculate_aspects_vectorized` (lignes 226-229) émet `orb = aspect_angle - distance` pour les non-Conjunctions, ce qui peut être **négatif** quand `distance > aspect_angle`. Le commentaire dans `calculator.py` le reconnaît : "This can produce negative values when distance > aspect_angle".

Donc un caller naïf qui fait `chart["aspect_orbs"][i, j] < 0.5` pour filtrer les "tight aspects" obtient des résultats inattendus pour les aspects où `distance > aspect_angle`.

**Recommandation :**
Documenter la convention de signe dans la docstring CHART_DTYPE :
```
- ``aspect_orbs`` (f4, (13, 13)): signed orb in degrees;
      ``aspect_angle - distance`` (positive when distance < aspect_angle,
      negative when distance > aspect_angle); ``NaN`` means "no orb".
      For absolute orb, use ``np.abs(chart["aspect_orbs"])``.
```
Ne pas changer le code (`calculate_aspects_vectorized` est out-of-scope phase 14), juste documenter le comportement existant.

---

### IN-03: `_BODY_COUNT = 13` constant mais pas dérivé de `ketu.core.bodies`

**Sévérité :** Info
**Fichier :** `ketu/charts/api.py:48`

**Issue :**
```python
_BODY_COUNT: int = 13
```
La docstring dit : "Mirrors `len(ketu.core.bodies)` and the subarray shapes pinned in `CHART_DTYPE`." Mais c'est un literal magique, pas dérivé. Si quelqu'un change `ketu.core.bodies` (acknowledged comme breaking v1.3 D-08), il faut chercher `_BODY_COUNT = 13` à la main et le mettre à jour, plus toutes les occurrences `(13,)` dans CHART_DTYPE et les `(13, 13)`.

Ce n'est pas un bug — c'est même intentionnel (le contrat est gelé par D-08), mais c'est une opportunité de DRY-ing.

**Recommandation :**
Optionnel pour v1.2 (D-08 gèle le 13). Pour v1.3 quand Chiron arrive :
```python
from ketu.core import bodies as _CANONICAL_BODIES
_BODY_COUNT: int = len(_CANONICAL_BODIES)  # FROZEN per D-08; 14 in v1.3
```
Pin runtime via test ratchet : `assert _BODY_COUNT == 13`. Ainsi si v1.3 grandit l'axe, le test rouge force la mise à jour explicite.

À ne PAS faire pour CHART_DTYPE (les subarray shapes doivent rester literals lisibles dans `core.py` — c'est le contrat documenté).

---

### IN-04: Test `test_compute_chart_polar_fallback_invalid_raises_value_error` dépend d'un détail interne de `calculate_houses`

**Sévérité :** Info
**Fichier :** `tests/charts/test_compute_chart.py:216-222`

**Issue :**
Le test passe `polar_fallback="invalid_choice"` à Paris (lat=48.86, non-polaire) et s'attend à `ValueError`. Cela fonctionne parce que `calculate_houses` valide `polar_fallback` *avant* le polar check (api.py:98-102).

Si jamais `calculate_houses` était refactoré pour valider `polar_fallback` *paresseusement* (seulement quand polaire), ce test casserait silencieusement la couverture de validation pour les inputs non-polaires. C'est un couplage implicite test/implémentation.

**Recommandation :**
Ajouter un test au cas polaire : `compute_chart(2451545.0, 80.0, 0.0, polar_fallback="invalid_choice")` doit ALSO raise ValueError. Couvre les deux trajectoires de validation.

Ou, mieux, ajouter un test équivalent à Paris ET au pôle dans une parametrize. Ça pin le contrat "ValueError peu importe la latitude".

---

### IN-05: `RuntimeWarning: invalid value encountered in divide` dans `orbital.py:733` carry-over

**Sévérité :** Info
**Fichier :** `ketu/ephemeris/orbital.py:733` (out-of-scope mais affecte `compute_chart`)

**Issue :**
Carry-over signalé par les SUMMARY 14-02, 14-04, 14-05. `np.arcsin(z / r)` avec `r = 0` produit `NaN`. Test SUMMARY 14-05 mentionne 61 warnings sur les tests charts.

J'ai vérifié empiriquement : `compute_chart(2451545.0, 48.86, 2.35)` produit le warning. Si jamais `r → 0` produit un `NaN` qui se propage à `body_lats[i]`, ça contamine `aspect_orbs` (pour ce body) et `body_lats` retournés par `compute_chart`.

J'ai vérifié : aucun NaN ne sort dans `body_lons` / `body_lats` pour le cas Paris J2000 ; donc le warning est probablement intercepté (ou produit un Inf qui se résoud avant `arcsin`). Mais c'est de la **chance**, pas une garantie.

**Recommandation :**
Out-of-scope phase 14 (carry-over pré-existant). Mais je note : si Phase 19 (Arabic Parts) commence à propager des NaN sur des `lots` dérivés de `body_lats`, ça pourrait surfacer comme un bug "fantôme" du chart. Suggérer un ticket dédié pour `ketu/ephemeris/orbital.py:733` (gérer le cas `r → 0` explicitement avec `np.where(r == 0, np.nan, np.arcsin(z / r))` ou un guard).

Pour Phase 14 stricto sensu : aucune action, c'est documenté correctement dans les SUMMARY.

---

## Compliments

Ce qui est notablement bien fait — Sophie félicite (sans complaisance) :

- **Discipline de gabarit `ketu/houses/` -> `ketu/charts/`** : copier-adapter exemplaire, sans dérive stylistique. `from __future__ import annotations` partout, `__all__` trié, type alias `AspectSetSpec` importé depuis presets et **non redéfini** (PATTERNS § 8.6 honoré).

- **Ratchets AGPL boundary** : trois tests indépendants (`test_no_runtime_swisseph_import` dans `test_dtype.py`, `test_compute_chart_no_runtime_swisseph_import` dans `test_compute_chart.py`, `test_no_runtime_swisseph_import_via_is_day_chart` dans `test_is_day_chart.py`). Le dernier déclenche une vraie call avant le check — catch les imports paresseux. **Plus strict que ce que PATTERNS § 8.5 demandait**. Bonne paranoïa.

- **Documentation D-06 sentinelles** : la docstring CHART_DTYPE (`core.py:71-73`) affiche le caller-mask one-liner inline (`mask = chart["aspect_matrix"] >= 0`). C'est ce que demandait CONTEXT.md ligne 142. Sophie aime quand la docstring ship le caller-pattern, pas juste la donnée.

- **Symétrie D-17 testée bidirectionnellement** : `test_aspect_matrix_symmetric` (matrix[i,j] == matrix[j,i]) ET `test_aspect_orbs_symmetric_with_nan_handling` (orbs avec equal_nan=True). Le second avec equal_nan est subtil — facile à oublier, ici fait correctement.

- **`np.ndindex(())` pinned par un test** : `test_aspect_matrix_scalar_jd_via_ndindex_empty_tuple`. Petit test, mais c'est exactement ce que RESEARCH §Assumption A1 demandait : pinner l'invariant numpy "scalar yields exactly one tuple". Si jamais NumPy change, le ratchet rouge prévient.

- **Bidirectional round-trip aspect-matrix** : `test_aspect_matrix_consistent_with_calculate_aspects_vectorized_standalone` vérifie forward (records → cells) ET reverse (populated cells → records). Pas juste un sens. C'est exactement ce qu'il faut pour pin le wrapper D-16.

- **Plan-data bug auto-fix** dans Plan 14-03 : le SUMMARY documente "Plan's incorrect aspect index for Trine (i_asp)" — Trine est 9, pas 7. L'agent a vérifié contre `ketu.core.aspects`, corrigé, et tracé la déviation Rule-1. C'est exactement le comportement adversarial qu'on veut. Pas de suiviste aveugle.

- **`np.asarray(sun_house >= 7)` wrap** dans `is_day_chart` : SUMMARY 14-04 documente que NumPy retourne `np.bool_` scalar pour les inputs scalaires, ce qui casse le contrat `np.ndarray` promis par la docstring. Le wrap `np.asarray(...)` upgrade vers 0-d ndarray. Petit détail, gros impact pour les callers qui font `.shape` ou `.dtype`.

- **Coverage 100 %** sur `ketu/charts/` (api.py 74/74, core.py 3/3, __init__.py 4/4). Pas de `# pragma: no cover`. Ratchet à 95 % comfortably exceeded. La discipline wave-by-wave (stubs first, full docstrings always green) a tenu sa promesse.

---

_Reviewed: 2026-05-09_
_Reviewer: Claude (gsd-code-reviewer) en persona Sophie Chen_
_Depth: standard (per-file analysis with cross-reference to CONTEXT.md decisions D-01..D-17)_
