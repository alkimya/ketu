# Phase 14 : Chart Abstraction Foundation — Pattern Map

**Mappé :** 2026-05-08 par Sophie Chen
**Fichiers analysés :** 6 nouveaux (3 prod + 3+ tests) + patterns transverses
**Analogues identifiés :** 6 / 6 (100 % — la subpackage `ketu/houses/` v1.1 est le gabarit littéral)

> **Note de cadrage Sophie.** La Phase 14 a une chance qu'on n'a presque
> jamais : un précédent direct (`ketu/houses/`) qui répond à toutes les
> questions de forme (subpackage, dtype subarray, broadcast, polar fallback,
> oracle test-only). Le job du planner est essentiellement un **copier‑adapter**
> discipliné. Là où je signale une divergence (cycles vs houses, dataclass vs
> dtype-only), c'est une dette antérieure — on ne la propage PAS dans charts/.

---

## Vue d'ensemble : classification des fichiers

| Fichier nouveau | Rôle | Data flow | Analogue le plus proche | Match |
|-----------------|------|-----------|--------------------------|-------|
| `ketu/charts/__init__.py` | package re-export | n/a | `ketu/houses/__init__.py` | exact |
| `ketu/charts/core.py` | dtype + exceptions | structured-array spec | `ketu/houses/core.py` | exact |
| `ketu/charts/api.py` | public API (compute_chart, is_day_chart) | broadcast → structured array | `ketu/houses/api.py` | exact |
| `ketu/charts/sect.py` *(optionnel)* | helper math interne | scalar/vector reduction | `ketu/houses/porphyry.py` (split-pattern) | role-match |
| `tests/charts/conftest.py` | test infra (oracle swisseph) | test-only AGPL boundary | `tests/houses/conftest.py` | exact |
| `tests/charts/test_*.py` | tests dtype/oracle/polaire | param + oracle | `tests/houses/test_dtype.py` + `test_integration.py` + `test_polar_safety.py` | exact |

---

## 1. `ketu/charts/__init__.py`

**Closest analog :** `ketu/houses/__init__.py` (lignes 1-53, fichier complet).

**Copy (à mirorer ligne-à-ligne) :**
- En-tête avec docstring de module (`ketu/houses/__init__.py:1-30`) :
  - 1 ligne de résumé
  - Section "Public API surface" listant chaque export avec `:func:` / `:data:` / `:class:` cross-refs
  - Section `Examples` avec `>>> from ketu.charts import compute_chart, is_day_chart, CHART_DTYPE`
  - Section `See Also` pointant vers les modules internes
- `from __future__ import annotations` (ligne 31) — convention obligatoire dans tout `ketu/charts/`
- Pattern d'imports alphabétiques par module local (`from .api import ...` / `from .core import ...`) — `ketu/houses/__init__.py:33-35`
- `__all__` strictement trié alphabétiquement, contenant seulement la surface publique — `ketu/houses/__init__.py:45-53`

**Adapt :**
- `__all__` cible : `["CHART_DTYPE", "compute_chart", "is_day_chart"]` (3 entrées si pas de re-export `house_of` ; 4 sinon — voir Discrétion D du CONTEXT).
- L'exemple du docstring DOIT inclure le cas vectorisé (success criterion 14.2 visible dès l'`__init__`) :
  ```
  >>> r = compute_chart(np.array([2451545.0, 2470204.0]),
  ...                   np.array([48.86, 64.15]),
  ...                   np.array([2.35, -21.94]))
  >>> r.shape, r["body_lons"].shape, r["aspect_matrix"].shape
  ((2,), (2, 13), (2, 13, 13))
  ```

**Skip :**
- Le bloc registry-trigger (`ketu/houses/__init__.py:37-43` : `from . import placidus  # noqa: F401`). **Pas de registry dans charts/** — `compute_chart` dispatche `system=` directement vers `calculate_houses` qui possède déjà sa propre registry. Ne pas dupliquer.

**Why this analog :** identique en intention (re-export d'une subpackage avec dtype + 1-3 fonctions publiques). C'est le seul gabarit dans le repo qui mélange « dtype + fonctions vectorisées + exception » comme charts/ va le faire.

---

## 2. `ketu/charts/core.py`

**Closest analog :** `ketu/houses/core.py` (lignes 1-80, fichier complet).

**Copy (à mirorer) :**
- Module docstring (`ketu/houses/core.py:1-15`) — pattern « définit X et Y » + paragraphe de motivation ML/Kala. **EXTENSION OBLIGATOIRE pour CHART_DTYPE :** ajouter un bloc explicite **"Why structured array"** (CONTEXT.md § Specifics ligne 139, success criterion 14.5). Ton : Sophie explique, ne s'excuse pas. Référencer Kala positional indexing.
- `from __future__ import annotations` + `import numpy as np` (lignes 16-18) — exact même header.
- Définition du dtype avec **commentaires `#:` sphinx** au-dessus (`ketu/houses/core.py:20-34` documente chaque champ) — **OBLIGATOIRE** : la doc des champs doit être lisible dans le docstring sphinx + accessible via `help(CHART_DTYPE)`.
- Pattern de subarray `("cusps", "f8", (12,))` (ligne 40) → CHART_DTYPE le réutilise pour `body_lons (f8, (13,))`, `body_lats (f8, (13,))`, `body_speeds (f8, (13,))`, `cusps (f8, (12,))`, `aspect_matrix (i1, (13, 13))`, `aspect_orbs (f4, (13, 13))`.
- Annotation explicite `HOUSES_DTYPE: np.dtype = np.dtype([...])` (ligne 35) — typage explicite obligatoire (mypy --strict).

**Adapt :**
- Liste des champs de CHART_DTYPE selon CONTEXT.md D-01 à D-06 :
  ```python
  CHART_DTYPE: np.dtype = np.dtype([
      # Metadata (D-04, mirror HOUSES_DTYPE inline)
      ("jd",            "f8"),
      ("lat",           "f8"),
      ("lon",           "f8"),
      ("system",        "U10"),
      # Body positions (D-01, D-02 ; (13,) axis = ketu.core.bodies order)
      ("body_lons",     "f8", (13,)),
      ("body_lats",     "f8", (13,)),
      ("body_speeds",   "f8", (13,)),
      # Houses inline (D-03 ; PAS de nested HOUSES_DTYPE)
      ("cusps",         "f8", (12,)),
      ("asc",           "f8"),
      ("mc",            "f8"),
      ("armc",          "f8"),
      ("vertex",        "f8"),
      # Aspects matrix (D-05, D-06)
      ("aspect_matrix", "i1", (13, 13)),
      ("aspect_orbs",   "f4", (13, 13)),
  ])
  ```
- Le docstring DOIT documenter les sentinelles `aspect_matrix == -1` (no aspect) et `aspect_orbs == NaN` (no orb), avec le one-liner caller : `chart["aspect_matrix"] >= 0` (CONTEXT.md § Specifics ligne 142).
- Le docstring DOIT documenter l'ordre canonique des 13 corps (Sun=0..Lilith=12) en référençant `ketu.core.bodies`.

**Skip :**
- **PAS de `HighLatitudeError` propre à charts/.** L'erreur polaire remonte naturellement via `calculate_houses` (D-11 : `polar_fallback` est un pass-through). Ré-importer `HighLatitudeError` depuis `ketu.houses` UNIQUEMENT si on l'expose dans `__all__` — sinon, laisser propager. Décision recommandée : **ne pas le re-exporter**, garder `from ketu.houses import HighLatitudeError` côté caller. C'est cohérent avec le principe « charts/ compose, ne ré-encapsule pas ».
- **PAS de dataclass `@dataclass class Chart:` parallèle au dtype.** C'est l'anti-pattern du module `ketu/cycles/calculator.py:58-115` (`CycleState` dataclass + `CYCLE_DTYPE` dtype redondants). Le projet a tranché Option A en faveur du dtype-seul (CONTEXT.md ligne 86, PROJECT.md). `core.py` ne contient QUE `CHART_DTYPE`.

**Why this analog :** `HOUSES_DTYPE` est le seul dtype ketu qui combine `(metadata scalaire + subarray field + champs scalaires d'angles)` dans la forme exacte que CHART_DTYPE va étendre. CYCLE_DTYPE est plat et orienté time-series — **n'est pas l'analogue de référence pour charts/**.

---

## 3. `ketu/charts/api.py`

**Closest analog :** `ketu/houses/api.py` (lignes 1-230, fichier complet).

### 3.1 Pattern broadcast + structured-output (gabarit `compute_chart`)

**Copy (à mirorer) — `ketu/houses/api.py:14-26` (header) :**
```python
from __future__ import annotations
from typing import Literal, Union, cast
import numpy as np
ArrayLike = Union[float, np.ndarray]
```
Le `from __future__ import annotations` est NON-NÉGOCIABLE pour numpydoc + mypy --strict.

**Copy — `ketu/houses/api.py:107-114` (broadcast pattern) :**
```python
jd_a = np.asarray(jd, dtype=np.float64)
lat_a = np.asarray(lat, dtype=np.float64)
lon_a = np.asarray(lon, dtype=np.float64)
jd_b, lat_b, lon_b = np.broadcast_arrays(jd_a, lat_a, lon_a)
# leading shape S = jd_b.shape
```
C'est le template canonique « broadcast → leading shape S » (CONTEXT.md ligne 123).

**Copy — `ketu/houses/api.py:153-165` (assemblage structured array de leading shape S) :**
```python
out = np.empty(jd_b.shape, dtype=HOUSES_DTYPE)
out["jd"] = jd_b
out["lat"] = lat_b
# ... etc
return out
```
Mirroir littéral pour CHART_DTYPE — `np.empty(jd_b.shape, dtype=CHART_DTYPE)` puis remplissage champ par champ.

**Copy — pattern `polar_fallback` validation (`ketu/houses/api.py:98-102`) :**
```python
if polar_fallback not in ("raise", "porphyry"):
    raise ValueError(
        f"polar_fallback must be 'raise' or 'porphyry'; "
        f"got {polar_fallback!r}"
    )
```

**Copy — pattern docstring numpydoc (`ketu/houses/api.py:35-97`) :**
- Sections Parameters / Returns / Raises / Notes / Examples dans cet ordre.
- Examples DOIT contenir un exemple scalaire ET un exemple vectorisé (`ketu/houses/api.py:84-96`) — c'est le contrat de visibilité de SC 14.2.
- Cast de retour : `return cast(np.ndarray, out)` si mypy --strict râle (cf `ketu/houses/api.py:230`).

**Adapt :**
- Signature : `compute_chart(jd, lat, lon, system="placidus", aspects=None, polar_fallback="raise")` (D-08 : pas de `bodies=`).
- Type alias importé : `from ketu.aspects.presets import AspectSetSpec` (D-10).
- Pipeline interne :
  1. broadcast `(jd, lat, lon)` → leading shape S (mirror `calculate_houses`).
  2. appel `calculate_houses(jd, lat, lon, system, polar_fallback)` (D-11, pass-through). Récupère cusps/asc/mc/armc/vertex en une passe.
  3. positions des 13 corps : pour chaque jd dans `jd_b.ravel()`, appeler `positions(jd)` (`ketu/calculations.py:461-489`) — **boucle Python sur S acceptée pour v1.2** (D-16). Documenter la dette dans une note interne `# TODO(v1.3): vectoriser positions sur jd_array — voir D-16`.
  4. lat/speed par corps : `body_properties(jd, body)` (`ketu/calculations.py:94-136`, déjà LRU-cached) — même boucle Python sur (S, 13).
  5. aspects : appeler `calculate_aspects_vectorized(jd, bodies, aspects)` une fois par élément de S, projeter chaque enregistrement `(body1, body2, i_asp, orb)` dans `aspect_matrix[i,j]` et son miroir `[j,i]` (D-17). Diagonale = `-1` / `NaN`.
  6. assemblage structured array (mirror `ketu/houses/api.py:153-165`).
- Pas de fallback `polar_fallback='porphyry'` à gérer EN LOCAL : `calculate_houses` le fait. Charts/ se contente de passer.

**Skip :**
- Le bloc `is_polar / polar_mask / np.where` (`ketu/houses/api.py:118-151`) — c'est le boulot de `calculate_houses`, pas de `compute_chart`. Charts/ n'y touche pas.
- Le `get_system(system)` direct (ligne 104) — déléguer à `calculate_houses` qui le fait pour nous.

**Why this analog :** `calculate_houses` est l'archétype « broadcast `(jd, lat, lon)` → structured array de shape S ». La signature de `compute_chart` est une sur-ensemble de celle de `calculate_houses` (mêmes 3 entrées spatio-temporelles + `aspects`).

### 3.2 Pattern `house_of` réutilisé pour `is_day_chart`

**Closest analog :** `ketu/houses/api.py:168-230` (`house_of`).

**Copy :**
- Annotation de retour castée : `return cast(np.ndarray, ...)` (ligne 230) — mypy --strict.
- Pattern broadcast `planet_lon` shape `(...,)` → `(..., 1)` puis comparaison vectorisée (lignes 217-225).
- Docstring numpydoc avec section Notes mathématique en code-block (lignes 200-215) — Sophie aime les preuves visibles.

**Adapt pour `is_day_chart` :**
- Signature : `is_day_chart(jd, lat, lon) -> np.ndarray` (bool ou bool scalar).
- Implémentation D-14, D-15 : compute Sun longitude via `long(jd, 0)` (`ketu/calculations.py:204-233`), compute cusps via `calculate_houses(jd, lat, lon, polar_fallback="porphyry")` (Porphyry interne forcé pour polar safety — D-15), appliquer `house_of(sun_lon, cusps)`. Sun en houses 7-12 = day (D-14).
- Convention sunrise-inclusive (D-13) : Sun >= ASC = day. Documenter LOUDEMENT dans le docstring (CONTEXT.md ligne 140).
- Polar safety : le docstring DOIT contenir un paragraphe explicatif sur le `polar_fallback="porphyry"` interne — les utilisateurs haute-latitude (Reykjavík, Tromsø) doivent comprendre pourquoi ils n'ont pas d'erreur (CONTEXT.md ligne 140).

**Skip :**
- L'argmax pattern de `house_of` (ligne 229) — pas applicable à `is_day_chart` ; on REUTILISE `house_of` directement, on ne le réimplémente pas.

**Why this analog :** `is_day_chart` est mathématiquement « compose `house_of(sun_lon, cusps)` puis test ∈ {7..12} ». Tout le pattern broadcast est déjà chez `house_of`.

---

## 4. Décision : `is_day_chart` dans `api.py` OU dans `sect.py` séparé ?

**Recommandation Sophie : `is_day_chart` reste dans `api.py`.**

**Évidence dans `ketu/houses/` :**
- `ketu/houses/api.py` mesure 8757 octets, contient 2 fonctions publiques (`calculate_houses` + `house_of`).
- Les modules math séparés (`ascmc.py` 5607o, `placidus.py` 14127o, `koch.py` 6758o, `porphyry.py` 6674o, `_ecliptic.py` 3390o) sont split parce qu'ils contiennent **plusieurs centaines de lignes de math complexe** chacun.
- `is_day_chart` fait ~30 lignes de glue (compose `long` + `calculate_houses` + `house_of`). C'est exactement le profil d'une fonction publique-glue qui appartient à `api.py`.

**Si toutefois la fonction grossit au-delà de ~50 lignes** (ex : ajout d'overload `is_day_chart(chart)` plus tard), alors split en `ketu/charts/sect.py` avec le pattern de `ketu/houses/porphyry.py:1-30` :
- Module docstring expliquant pourquoi le module existe en propre.
- `from __future__ import annotations`.
- Re-export depuis `ketu/charts/__init__.py`.

**Discrétion planner :** OK pour split en `sect.py` si le planner sent que ça aide la lisibilité — c'est explicitement délégué à sa discrétion (CONTEXT.md ligne 61). Pour Phase 14 ship minimal, **garder dans `api.py`**.

---

## 5. `tests/charts/conftest.py`

**Closest analog :** `tests/houses/conftest.py` (lignes 1-255, fichier complet).

**Copy (mirorage littéral, c'est le meilleur conftest du repo) :**
- En-tête avec docstring expliquant la frontière AGPL test-only (`tests/houses/conftest.py:1-30`). Pour charts/, mentionner que le swisseph oracle compose ASC/MC/cusps + positions de corps + aspects pour cross-checker `compute_chart`.
- **Pattern d'import critique** (`tests/houses/conftest.py:32-60`) — le `import numpy AVANT importorskip swisseph` n'est PAS facultatif (commentaire ligne 36-43 explique le `_NoValueType` bug coverage.py). À copier MOT POUR MOT :
  ```python
  from __future__ import annotations
  import numpy as np
  import pytest
  import json  # noqa: E402
  from pathlib import Path  # noqa: E402
  from typing import Any  # noqa: E402

  pytest.importorskip("swisseph")
  import swisseph as swe  # noqa: E402
  ```
- `SYSTEM_BYTES` dict (lignes 77-81) — ré-importer ou ré-déclarer (préférable : `from tests.houses.conftest import SYSTEM_BYTES` pour DRY).
- `swe_oracle(jd, lat, lon, system)` helper (lignes 95-147) — utilisé pour la portion houses du chart.
- Pattern fixture `reference_charts` session-scoped (lignes 196-231) — ré-utiliser les MÊMES 10 charts de `tests/houses/conftest.py:219-231` (CONTEXT.md ligne 143).
- Pattern fixture `loaded_reference_snapshot` (lignes 234-254) avec skip-si-absent.

**Adapt — additions spécifiques à charts/ :**
- Nouvel oracle helper `swe_chart_oracle(jd, lat, lon, system)` qui combine :
  - `swe_oracle(jd, lat, lon, system)` pour cusps/asc/mc/armc/vertex
  - `swe.calc_ut(jd, body_id)` pour les 13 corps (ou réutiliser un helper existant — vérifier si `tests/test_lilith_cross_check.py` en a un).
  - Optionnel : aspects calculés par la lib elle-même (les aspects sont un détail d'implémentation interne, pas un calcul swisseph).
- Nouvelle fixture `chart_reference_fixtures` : 2-3 charts hand-validés AVEC aspect_matrix attendu (CONTEXT.md ligne 143). Format suggéré :
  ```python
  {
      "label": "J2000_Paris_full_chart",
      "jd": 2451545.0, "lat": 48.8566, "lon": 2.3522, "system": "placidus",
      "expected_body_lons": np.array([...13 valeurs...]),
      "expected_aspect_pairs": [(0, 1, 13, 4.5), ...],  # (body1, body2, i_asp, orb)
  }
  ```
- Si un fichier `tests/charts/fixtures/reference_charts.json` est régénéré, mirror le pattern `FIXTURES_DIR = Path(__file__).parent / "fixtures"` (`tests/houses/conftest.py:86`).

**Skip :**
- `swe_oracle_armc` (lignes 150-188) — c'est un helper Plan 03/04/05 spécifique au split ARMC du houses. Charts/ ne split pas le calcul ARMC ; pas besoin.

**Why this analog :** identique en intention (oracle test-only AGPL, fixtures session-scoped, ≥10 charts dont polaires). Le pattern d'import numpy-avant-importorskip est un **bug-killer** déjà débogué pour Phase 10 — ne le redécouvre pas à la dure.

---

## 6. `tests/charts/test_*.py` — décomposition recommandée

**Closest analogs :** `tests/houses/test_dtype.py`, `test_integration.py`, `test_polar_safety.py`, `test_oracle_smoke.py`.

### Fichier 1 : `tests/charts/test_dtype.py`

**Analog :** `tests/houses/test_dtype.py:1-68`.

**Copy :**
- Pattern `test_dtype_field_names_match_spec()` (`test_dtype.py:13-18`) — assertion stricte de l'ordre des 14 champs.
- Pattern `test_dtype_cusps_is_subarray_of_length_12()` (`test_dtype.py:21-29`) — vérifier `.shape` du field dtype. Adapter pour `body_lons (13,)`, `aspect_matrix (13, 13)`, etc.
- Pattern `test_dtype_supports_vectorized_construction()` (`test_dtype.py:32-38`) — `np.zeros(N, dtype=CHART_DTYPE)` + assignment round-trip.
- Pattern `test_dtype_string_field_capacity()` (`test_dtype.py:41-46`) — U10 fits "placidus", "porphyry", etc.
- Pattern `test_dtype_scalar_zero_dim_construction()` (`test_dtype.py:49-54`).

**Adapt :**
- Tests sentinelles aspect_matrix : vérifier que `i1` accepte `-1`, que `f4` accepte `NaN`, que la diagonale est correctement initialisée.
- Test ordre canonique : `body_lons[0]` correspond à Sun (cross-check via `ketu.core.bodies`).

**Skip :** test `test_high_latitude_error_is_value_error_subclass` — pas de HighLatitudeError propre à charts/.

### Fichier 2 : `tests/charts/test_compute_chart.py`

**Analog :** `tests/houses/test_integration.py:1-285`.

**Copy :**
- Pattern `test_calculate_houses_returns_houses_dtype_array()` (`test_integration.py:65-72`) → adapter pour `compute_chart`.
- Pattern `test_calculate_houses_meta_fields_populated()` (`test_integration.py:75-82`) — round-trip jd/lat/lon/system.
- Pattern `@pytest.mark.parametrize @ pytest.mark.parametrize` croisé (system × label) (`test_integration.py:91-122`) — vérifier `compute_chart["cusps"]` matche le snapshot houses.
- Pattern `test_calculate_houses_vectorized_preserves_leading_shape()` (`test_integration.py:193-201`) — leading shape S préservé.
- Pattern `test_calculate_houses_2d_input_shape_preserved()` (`test_integration.py:204-211`) — shape `(2, 3)` → output `(2, 3)`, subarray `(2, 3, 13)`.
- Pattern `test_calculate_houses_no_runtime_swisseph_import()` (`test_integration.py:214-237`) — **CRITIQUE pour la frontière AGPL**. Adapter pour `ketu.charts.*` au lieu de `ketu.houses.*`. Catch-all que personne n'importe swisseph dans le runtime.

**Adapt :**
- Tests body_lons cross-checked avec swisseph oracle (boucle sur les 13 corps).
- Tests aspect_matrix : vérifier symétrie (`aspect_matrix[i,j] == aspect_matrix[j,i]` D-17), vérifier diagonale = -1, vérifier qu'un aspect connu (Sun-Moon trine en 2026-01-01 par ex.) est présent au bon index.
- Test `aspects=None` → CLASSICAL (D-07).
- Test `aspects=["Conjunction", "Trine"]` → seuls ces aspects apparaissent dans aspect_matrix.

**Skip :** sections koch-spécifiques, porphyry-spécifiques (calculate_houses gère déjà).

### Fichier 3 : `tests/charts/test_polar_safety.py`

**Analog :** `tests/houses/test_polar_safety.py:1-158`.

**Copy :**
- Pattern `test_calculate_houses_polar_default_raises_high_latitude_error` — `compute_chart(jd, 80, 0, polar_fallback="raise")` doit raise HighLatitudeError (propagé depuis calculate_houses).
- Pattern `test_calculate_houses_polar_porphyry_substitutes_for_polar_only` (`test_integration.py:151-164`) — vectorisé 1 mid-lat + 1 polar, no NaN dans `cusps`.

**Adapt :**
- Vérifier que `compute_chart["body_lons"]` n'est PAS affecté par le polar_fallback (les positions de corps n'en dépendent pas — sanity).
- Vérifier `aspect_matrix` reste valide en cas de polar_fallback="porphyry" (les aspects sont entre corps, pas entre cusps).

### Fichier 4 : `tests/charts/test_is_day_chart.py`

**Analog :** combinaison `tests/houses/test_house_of.py` (compose pattern) + nouvelle logique sect.

**Copy :**
- Pattern fixture `paris_j2000_cusps` (`test_house_of.py:19-24`) — adapter pour Paris J2000 chart complet.
- Pattern broadcast test `test_house_of_vectorized_over_planet_lons` (`test_house_of.py:49-55`) — pour `is_day_chart(jd_array, lat_array, lon_array)`.

**Adapt :**
- Cas hand-validés : J2000 Paris à midi UTC = day. J2000 Paris à minuit UTC = night.
- Test edge case D-13 : Sun exactement sur ASC → day (sunrise-inclusive).
- Test polar safety D-15 : `is_day_chart(2451545.0, 80.0, 0.0)` doit retourner un bool **sans raise** (Porphyry interne).
- Test convention D-14 : Sun en house 7-12 = day, Sun en house 1-6 = night.

### Fichier 5 (optionnel) : `tests/charts/test_oracle_smoke.py`

**Analog :** `tests/houses/test_oracle_smoke.py:1-105`.

**Copy :**
- Pattern `test_reference_charts_has_at_least_ten_entries` + `test_reference_charts_includes_polar_latitudes`.
- Pattern `test_loaded_reference_snapshot_matches_oracle` — si un snapshot chart-level est introduit.

**Adapt :** seulement si la fixture `chart_reference_fixtures` introduit une logique JSON snapshot. Sinon, skip ce fichier.

---

## 7. Patterns transverses (cross-cutting)

### 7.1 `from __future__ import annotations` — OBLIGATOIRE

**Présent dans tous les modules récents :**
- `ketu/houses/*.py` (8/8 fichiers vérifiés)
- `ketu/aspects/presets.py`
- `tests/houses/conftest.py`, `tests/houses/test_*.py`

**ABSENT (legacy, ne pas imiter) :**
- `ketu/cycles/calculator.py:1-10` — pas de `__future__ annotations`. Hérité de v1.0, anti-pattern.
- `ketu/aspects/calculator.py:1-12` — idem, legacy.

**Règle Phase 14 :** TOUS les fichiers `ketu/charts/*.py` ET `tests/charts/*.py` commencent par `from __future__ import annotations`. Pas d'exception.

### 7.2 Type alias naming

- `ArrayLike = Union[float, np.ndarray]` (`ketu/houses/api.py:25`, `ketu/houses/ascmc.py:27`) — pattern à réutiliser dans `ketu/charts/api.py`.
- `AspectSetSpec = Union[None, str, Sequence[Union[str, int]], np.ndarray]` (`ketu/aspects/presets.py:98`) — importer depuis presets, ne PAS redéfinir.

### 7.3 `__all__` discipline

- Strictement trié alphabétiquement (`ketu/houses/__init__.py:45-53`).
- Contient SEULEMENT les entrées effectivement re-exportées.
- Un par fichier prod (même les modules internes ont leur `__all__` — cf `ketu/aspects/calculator.py:517-525`).

### 7.4 Position des Examples dans les docstrings

- **Module-level** : exemples d'usage dans le docstring du `__init__.py` (`ketu/houses/__init__.py:13-16`).
- **Function-level** : exemples spécifiques à la fonction (`ketu/houses/api.py:84-96`).
- Pour `compute_chart`, les DEUX positions doivent contenir un exemple vectorisé (success criterion 14.2 visible à l'`__init__` ET à la fonction).

### 7.5 Docstring numpydoc — sections obligatoires

Configuration `[tool.numpydoc_validation]` (`pyproject.toml:115-131`) :
- `EX01` ignoré → Examples optionnels pour les internes, **mais OBLIGATOIRE pour les fonctions publiques exportées** (par convention Sophie).
- `SA01`, `ES01`, `GL01` ignorés.
- Tous les autres checks actifs : Parameters, Returns, Raises, Notes doivent être numpydoc-clean.

Pour Phase 14, `compute_chart` et `is_day_chart` exportent → Examples obligatoires.

### 7.6 Coverage

Configuration `[tool.coverage.run]` (`pyproject.toml:82-88`) :
- `source = ["ketu"]`
- `omit` ne mentionne PAS `ketu/charts/` → auto-inclus dès création.
- `[tool.coverage.report] fail_under = 70` global ; le gate ≥95 % sur `ketu/charts/` (success criterion 14.5) est à appliquer **via Makefile target `make charts-coverage`** (mirror `houses-coverage` mentionné dans `tests/houses/test_house_of.py:9`).

### 7.7 Mypy --strict

Configuration `[[tool.mypy.overrides]]` (`pyproject.toml:144-154`) :
- Carve-outs existants pour `ketu.aspects.*`, `ketu.cycles.*`, `ketu.calculations`, etc. → **NE PAS étendre à `ketu.charts.*`**. Phase 14 doit être strict-clean dès le jour 1 (CLAUDE.md § Cross-cutting v1.2 : « mypy --strict »).
- Donc : `cast(np.ndarray, ...)` aux retours, annotations explicites partout, `npt.NDArray[np.float64]` quand le dtype compte.

### 7.8 Setuptools packages

Configuration `[tool.setuptools]` (`pyproject.toml:60-61`) :
```toml
packages = ["ketu", "ketu.ephemeris", "ketu.aspects", "ketu.cycles", "ketu.cache", "ketu.houses", "ketu.cli"]
```
**ATTENTION :** ce n'est PAS un find-packages auto ; c'est une liste explicite. Phase 14 DOIT ajouter `"ketu.charts"` à cette liste pour que la subpackage soit installée.

> **Divergence vs CONTEXT.md ligne 131 :** le contexte dit « pyproject.toml — no new entries required (`ketu/charts/` is auto-discovered by the existing setuptools find-packages config) ». **C'est faux** — la config est explicite, pas auto. Le planner DOIT ajouter `"ketu.charts"` à la liste `packages`. Une seule ligne, mais sinon `pip install ketu` n'inclura pas le sous-package.

---

## 8. Anti-patterns à NE PAS reproduire

### 8.1 Dataclass + dtype redondants

**Source de l'anti-pattern :** `ketu/cycles/calculator.py:58-115` définit `@dataclass class CycleState` PUIS `CYCLE_DTYPE = np.dtype([...])` avec les MÊMES champs. Double source-of-truth, dette de maintenance, ML interop ambiguë.

**Règle Phase 14 :** `core.py` contient UNIQUEMENT `CHART_DTYPE`. Pas de `@dataclass class Chart:`. Option A est tranchée (PROJECT.md, CONTEXT.md ligne 86).

### 8.2 Imports directs depuis sous-modules

**Anti-pattern :** `from ketu.aspects.calculator import calculate_aspects_vectorized` est OK pour le runtime interne de `ketu/charts/api.py`, mais les **callers externes** doivent passer par `from ketu.aspects import calculate_aspects_vectorized` (l'`__init__.py` re-exporte).

**Règle :** dans `ketu/charts/api.py`, importer DEPUIS le sous-module (`from ketu.aspects.calculator import calculate_aspects_vectorized`) pour minimiser la surface d'import et éviter les imports circulaires potentiels. Mais PAS depuis l'`__init__.py` de aspects (qui charge tout).

### 8.3 Dispatch if/elif

**Anti-pattern flag (`ketu/houses/api.py:140-141`) :** « no inline if/elif ladder anywhere — registry-based dispatch only ».

**Règle Phase 14 :** `compute_chart` ne dispatche PAS sur `system=` — il passe à `calculate_houses` qui a déjà sa registry. Pas de `if system == "placidus": ... elif system == "koch": ...` dans charts/.

### 8.4 Polar circle hardcoded

**Anti-pattern flag (`tests/houses/test_polar_safety.py:98-112`) :** `polar_circle` est time-varying (90 - ε(jd)), pas une constante 66.5616°. Le test `test_polar_circle_is_time_varying_not_hardcoded` est un ratchet.

**Règle Phase 14 :** `is_day_chart` ne hardcode PAS de seuil polaire. Il appelle `calculate_houses(..., polar_fallback="porphyry")` qui gère via `polar_circle(jd)`.

### 8.5 Swisseph dans le runtime

**Anti-pattern catastrophique :** `import swisseph` dans `ketu/charts/*.py`. Violation AGPL acquise par contamination du package MIT.

**Ratchet test à copier (`tests/houses/test_integration.py:214-237`)** : `test_compute_chart_no_runtime_swisseph_import` vérifie que `dir(ketu.charts.*)` ne contient AUCUN nom commençant par `swe_`, ni `swisseph`, ni `swe`. À copier mot-pour-mot, juste s/houses/charts/.

### 8.6 Re-définir `AspectSetSpec`

**Anti-pattern :** définir un nouveau type alias ChartsAspectSpec ou similaire dans `ketu/charts/`.

**Règle :** TOUJOURS importer depuis presets : `from ketu.aspects.presets import AspectSetSpec`. Une seule source-of-truth (D-10 ; CONTEXT.md ligne 116).

---

## 9. Récapitulatif pour le planner

| Action | Fichier | Source à imiter |
|--------|---------|------------------|
| Créer subpackage layout | `ketu/charts/{__init__,core,api}.py` | `ketu/houses/{__init__,core,api}.py` |
| Définir CHART_DTYPE | `ketu/charts/core.py` | `ketu/houses/core.py:35-45` (pattern subarray) |
| Implémenter compute_chart | `ketu/charts/api.py` | `ketu/houses/api.py:28-165` (broadcast + assemble) |
| Implémenter is_day_chart | `ketu/charts/api.py` | `ketu/houses/api.py:168-230` (compose `house_of`) |
| Tests dtype structurel | `tests/charts/test_dtype.py` | `tests/houses/test_dtype.py:1-68` |
| Tests intégration | `tests/charts/test_compute_chart.py` | `tests/houses/test_integration.py:65-285` |
| Tests polar safety | `tests/charts/test_polar_safety.py` | `tests/houses/test_polar_safety.py:1-158` |
| Tests sect | `tests/charts/test_is_day_chart.py` | combinaison `test_house_of.py` + logique nouvelle |
| Conftest oracle | `tests/charts/conftest.py` | `tests/houses/conftest.py:1-255` |
| Ajouter au pyproject | `pyproject.toml:61` | ajout `"ketu.charts"` à la liste explicite |

---

## Métadonnées

**Scope d'analyse :** `ketu/houses/` (subpackage v1.1, gabarit principal), `ketu/aspects/` (calculator + presets, dépendances downstream), `ketu/cycles/` (anti-pattern dataclass à éviter), `ketu/calculations.py` (positions/body_properties à composer), `tests/houses/` (gabarit tests), `pyproject.toml` (gates doc/coverage/mypy).

**Fichiers scannés :** 14 fichiers prod + 8 fichiers tests + pyproject.

**Date d'extraction :** 2026-05-08.

*— Sophie Chen, Lead Technical Architect*
