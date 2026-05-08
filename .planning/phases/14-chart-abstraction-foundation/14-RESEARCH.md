# Phase 14: Chart Abstraction Foundation — Research

**Recherche :** 2026-05-08
**Domaine :** API d'agrégation NumPy structured-array (positions + houses + aspects) sur stack pure-NumPy 2.x
**Confiance globale :** HIGH (tous les patterns ciblés existent déjà en v1.1 sous forme exploitable)

---

## Résumé exécutif

Phase 14 est de la **composition pure**, pas de l'invention. Les trois briques (`positions`/`body_properties`, `calculate_houses`, `calculate_aspects_vectorized`) existent toutes et sont matures. Le travail consiste à :

1. Définir un nouveau `CHART_DTYPE` qui *inline* HOUSES_DTYPE (D-03) + ajoute les positions des 13 corps en subarrays (D-01) + ajoute la matrice d'aspects dense (13,13) (D-05).
2. Écrire `compute_chart` comme un wrapper qui broadcast `(jd, lat, lon)` vers une shape S, appelle `calculate_houses` une fois, vectorise les positions sur S, puis projette les records d'aspects dans la matrice dense (boucle Python sur S autorisée par D-16).
3. Écrire `is_day_chart` comme un wrapper auto-suffisant qui calcule ses propres ASC + cusps en interne avec `polar_fallback="porphyry"` (D-15), puis applique `house_of(sun_lon, cusps) ∈ {7..12}` (D-14).
4. Couvrir le tout à ≥95 % et passer interrogate + numpydoc validate (gates Phase 13).

**Recommandation principale :** mimer **strictement** la structure `ketu/houses/` — `core.py` (dtype + module docstring "Why structured array") + `api.py` (compute_chart + is_day_chart, les deux dans le même fichier puisque is_day_chart est trivial et factorisable autour des mêmes imports). Pas de `sect.py` séparé : il créerait un fichier de 30 lignes dont la seule logique est un appel à `calculate_houses` + `house_of`.

**Plan recommandé :** 5 plans atomiques (voir §8 pour le détail), exécutables en deux vagues (skeleton+dtype seul puis compute_chart + is_day_chart + tests + doc-gates en parallèle).

---

## Architectural Responsibility Map

| Capability | Tier primaire | Tier secondaire | Rationale |
|---|---|---|---|
| Définition `CHART_DTYPE` | `ketu/charts/core.py` | — | Pattern HOUSES_DTYPE (`ketu/houses/core.py:35`) : dtype + exception(s) + module docstring vivent dans `core.py`. |
| `compute_chart` (broadcast + assemblage) | `ketu/charts/api.py` | — | Pattern `calculate_houses` (`ketu/houses/api.py:28`) : public function dans `api.py`, dispatche vers les modules internes. |
| `is_day_chart` (sect helper) | `ketu/charts/api.py` | — | Helper factorisable autour des mêmes imports que `compute_chart` ; un fichier `sect.py` séparé n'apporte rien (cf. §1). |
| Construction matrice d'aspects | `_build_aspect_matrix` (privé dans `api.py`) | — | Fonction interne ; pas de surface publique. Le pattern v1.1 ne sort un module dédié que quand il y a 50+ lignes de math (cf. `houses/porphyry.py`, `houses/placidus.py`). Ici < 30 lignes. |
| Re-export public | `ketu/charts/__init__.py` | — | Pattern `ketu/houses/__init__.py:33-53` : `from .core import …` puis `from .api import …` puis `__all__`. |
| Test oracles (swisseph) | `tests/charts/conftest.py` | `tests/houses/conftest.py` (ré-utilisable) | Pattern test-only AGPL ; le swisseph oracle de `tests/houses/conftest.py` est ré-utilisable verbatim pour valider la portion houses de CHART_DTYPE. |

---

## 1. Squelette du subpackage `ketu/charts/`

### Recommandation concrète

```
ketu/charts/
├── __init__.py        # re-exports : CHART_DTYPE, compute_chart, is_day_chart
├── core.py            # CHART_DTYPE + module docstring "Why structured array"
└── api.py             # compute_chart + is_day_chart + _build_aspect_matrix (privé)
```

**Pas de `sect.py` séparé.** `is_day_chart` fait ~15 lignes utiles (broadcast + appel `calculate_houses` + appel `house_of` + comparaison hémisphère). Le sortir dans son propre fichier crée une indirection sans bénéfice. Le pattern v1.1 sort un module séparé uniquement quand il porte une responsabilité math autonome (placidus.py, koch.py, porphyry.py, ascmc.py — tous ≥ 80 lignes de logique). `is_day_chart` n'est pas dans cette catégorie.

**Pas de module séparé pour `_build_aspect_matrix` non plus.** ~20 lignes ; reste fonction privée dans `api.py`. À sortir dans son propre fichier UNIQUEMENT si la Phase 16 (synastry) en réclame une variante cross-chart — auquel cas le refactor sera trivial et appartiendra à Phase 16, pas à 14.

### Divergences vs `ketu/houses/`

| Aspect | `ketu/houses/` | `ketu/charts/` proposé | Justification |
|---|---|---|---|
| `core.py` | dtype + `HighLatitudeError` | dtype seul | Pas d'exception spécifique à charts ; on délègue les `HighLatitudeError` à `calculate_houses` qu'on appelle. |
| Modules math | `placidus.py`, `koch.py`, `porphyry.py`, `ascmc.py`, `registry.py` | aucun | Phase 14 ne fait pas de math nouvelle. Tout est composition. |
| `__init__.py` registry trigger imports | `from . import placidus  # noqa: F401` etc. | aucun trigger import | Pas de pattern registre dans charts (D-08 : body list FROZEN, pas de dispatch). |

Les imports déclencheurs de la registry `houses/__init__.py:41-43` n'ont **pas** d'équivalent ici — c'est un piège classique de copy-paste à éviter.

### Re-export package (`ketu/charts/__init__.py`)

```python
"""Chart abstraction subpackage — fully-resolved natal charts in one call."""
from __future__ import annotations

from .api import compute_chart, is_day_chart
from .core import CHART_DTYPE

__all__ = [
    "CHART_DTYPE",
    "compute_chart",
    "is_day_chart",
]
```

**Top-level `ketu/__init__.py` n'est PAS modifié en v1.2** (cf. CONTEXT § Integration Points : « callers `from ketu.charts import …` per the success criterion 14.1 wording »). Revisité v1.3.

---

## 2. Définition de `CHART_DTYPE`

### Snippet concret (à mettre dans `ketu/charts/core.py`)

```python
import numpy as np

#: Structured dtype for a fully-resolved natal chart.
#:
#: Fields (12 total):
#:     - ``jd`` (f8): Julian Date, UT.
#:     - ``lat`` (f8): Geographic latitude, degrees.
#:     - ``lon`` (f8): Geographic longitude (east-positive), degrees.
#:     - ``system`` (U10): House system requested (e.g. "placidus").
#:     - ``body_lons`` (f8, (13,)): Ecliptic longitudes per body, degrees [0, 360).
#:     - ``body_lats`` (f8, (13,)): Ecliptic latitudes per body, degrees.
#:     - ``body_speeds`` (f8, (13,)): Longitude speeds per body, deg/day.
#:                                      Negative => retrograde.
#:     - ``cusps`` (f8, (12,)): 12 house cusps, degrees [0, 360).
#:     - ``asc`` (f8): Ascendant, degrees [0, 360).
#:     - ``mc`` (f8): Medium Coeli, degrees [0, 360).
#:     - ``armc`` (f8): Right Ascension of MC, degrees [0, 360).
#:     - ``vertex`` (f8): Vertex, degrees [0, 360).
#:     - ``aspect_matrix`` (i1, (13, 13)): canonical aspect index in
#:           [0, 13]; -1 means "no aspect"; symmetric (matrix[i,j]==matrix[j,i]);
#:           diagonal == -1.
#:     - ``aspect_orbs`` (f4, (13, 13)): orb in degrees; NaN means "no orb"
#:           (matches aspect_matrix == -1); symmetric; diagonal == NaN.
CHART_DTYPE: np.dtype = np.dtype([
    ("jd",            "f8"),
    ("lat",           "f8"),
    ("lon",           "f8"),
    ("system",        "U10"),
    ("body_lons",     "f8", (13,)),
    ("body_lats",     "f8", (13,)),
    ("body_speeds",   "f8", (13,)),
    ("cusps",         "f8", (12,)),
    ("asc",           "f8"),
    ("mc",            "f8"),
    ("armc",          "f8"),
    ("vertex",        "f8"),
    ("aspect_matrix", "i1", (13, 13)),
    ("aspect_orbs",   "f4", (13, 13)),
])
```

**Note d'ordre :** je mets les champs dans l'ordre logique (méta → bodies → houses → aspects) plutôt que l'ordre exact d'HOUSES_DTYPE. C'est lisible à l'œil et n'a pas d'impact perf (NumPy ne ré-ordonne pas les structured fields). Le planner peut adopter un autre ordre s'il préfère ; ce qui compte c'est que les **noms de champs** des houses correspondent **verbatim** à HOUSES_DTYPE pour faciliter le copy-write `out["asc"] = houses["asc"]` etc.

### Sentinelles (D-06)

- `aspect_matrix` : `i1` (signed int8, range -128..127). « Pas d'aspect » = `-1`. Indices canoniques d'aspects ∈ [0, 13] (cf. `ketu/aspects/presets.py:10-14`), donc -1 est sans ambiguïté.
- `aspect_orbs` : `f4`. « Pas d'orb » = `np.nan`. Idiomatique NumPy.
- Diagonale : `-1` / `NaN` (un corps n'a pas d'aspect avec lui-même).

**Caller mask documenté dans la docstring :** `chart["aspect_matrix"] >= 0` ou équivalent `~np.isnan(chart["aspect_orbs"])`.

### Estimation taille mémoire (un chart scalaire)

| Champ | Bytes |
|---|---|
| jd, lat, lon (3 × f8) | 24 |
| system (U10 = 10 × 4 bytes UCS-4) | 40 |
| body_lons, body_lats, body_speeds (3 × 13 × f8) | 312 |
| cusps (12 × f8) | 96 |
| asc, mc, armc, vertex (4 × f8) | 32 |
| aspect_matrix (13 × 13 × i1) | 169 |
| aspect_orbs (13 × 13 × f4) | 676 |
| **Total** | **~1349 bytes** |

`np.zeros(1, dtype=CHART_DTYPE).itemsize` confirmera (NumPy peut padder). Pour S=1000 charts batchés : ~1.35 MB. Négligeable face au gain ML-batchabilité.

### Module docstring "Why structured array" (success criterion 14.5)

À écrire dans `ketu/charts/core.py` en tête de fichier. Section dédiée nommée `"Why a structured array?"` qui explique :

1. **ML-interop NumPy-first :** Kala consomme via indexation positionnelle (`chart["body_lons"][i]` pour le body i, garanti stable par D-08).
2. **Batchabilité :** un seul `np.empty(S, dtype=CHART_DTYPE)` au lieu de S dataclasses Python — typique 100× plus rapide à construire et nativement `np.save`/`np.load`-friendly.
3. **Self-describing :** chaque chart porte son propre `(jd, lat, lon, system)` (D-04), évitant à synastry/composite/return de transporter le contexte séparément.
4. **Inline houses, pas nested (D-03) :** suppression d'un niveau d'indirection ; toutes les valeurs houses sont des scalaires ou subarrays courts, le nesting n'apporterait rien.

Ton Sophie : explicatif et pragmatique, pas défensif. Le ton de `ketu/houses/core.py:1-15` est le bon registre.

---

## 3. Stratégie d'implémentation `compute_chart`

### Squelette (api.py)

```python
def compute_chart(
    jd: ArrayLike,
    lat: ArrayLike,
    lon: ArrayLike,
    system: str = "placidus",
    aspects: AspectSetSpec = None,
    polar_fallback: Literal["raise", "porphyry"] = "raise",
) -> np.ndarray:
    # 1. Broadcast — exact mirror of calculate_houses (houses/api.py:108-111)
    jd_a  = np.asarray(jd,  dtype=np.float64)
    lat_a = np.asarray(lat, dtype=np.float64)
    lon_a = np.asarray(lon, dtype=np.float64)
    jd_b, lat_b, lon_b = np.broadcast_arrays(jd_a, lat_a, lon_a)
    S = jd_b.shape  # leading shape

    # 2. Houses (one call covers cusps + ASC/MC/ARMC/Vertex + polar dispatch)
    houses = calculate_houses(jd_b, lat_b, lon_b, system=system,
                              polar_fallback=polar_fallback)
    # houses is a structured array of HOUSES_DTYPE, leading shape S.

    # 3. Body positions vectorised on S (see §5 for the wrapper choice)
    body_lons, body_lats, body_speeds = _vectorised_body_properties(jd_b)
    # Each: shape S + (13,)  i.e.  (*S, 13)

    # 4. Aspect matrix per element — Python loop over S (D-16)
    aspect_matrix, aspect_orbs = _build_aspect_matrix(
        jd_b, body_lons, aspects=aspects
    )
    # aspect_matrix: shape (*S, 13, 13) i1
    # aspect_orbs:   shape (*S, 13, 13) f4

    # 5. Assemble structured output
    out = np.empty(S, dtype=CHART_DTYPE)
    out["jd"]            = jd_b
    out["lat"]           = lat_b
    out["lon"]           = lon_b
    out["system"]        = system.lower()
    out["body_lons"]     = body_lons
    out["body_lats"]     = body_lats
    out["body_speeds"]   = body_speeds
    out["cusps"]         = houses["cusps"]
    out["asc"]           = houses["asc"]
    out["mc"]            = houses["mc"]
    out["armc"]          = houses["armc"]
    out["vertex"]        = houses["vertex"]
    out["aspect_matrix"] = aspect_matrix
    out["aspect_orbs"]   = aspect_orbs
    return out
```

### Helper privé `_vectorised_body_properties`

Trois options pour construire `body_lons / lats / speeds` de shape `(*S, 13)` :

- **Option A (recommandée) — exploiter `calc_planet_position_batch`** (`ketu/ephemeris/planets.py:431`). Cette fonction prend déjà `jd_array: np.ndarray` et un `planet_id` scalaire, retourne `(n_dates, 6)` avec les colonnes `[lon, lat, dist, lon_speed, lat_speed, dist_speed]`. C'est exactement la primitive vectorisée qu'il nous faut.

  ```python
  def _vectorised_body_properties(jd_b: np.ndarray):
      # Flatten to 1-D for batch call, then reshape back to S + (13,)
      jd_flat = jd_b.ravel()                      # shape (M,)
      n = jd_flat.size
      lons   = np.empty((n, 13), dtype=np.float64)
      lats   = np.empty((n, 13), dtype=np.float64)
      speeds = np.empty((n, 13), dtype=np.float64)
      for body_id in range(13):
          batch = calc_planet_position_batch(jd_flat, body_id)  # (n, 6)
          lons[:,   body_id] = batch[:, 0]
          lats[:,   body_id] = batch[:, 1]
          speeds[:, body_id] = batch[:, 3]
      tail_shape = jd_b.shape + (13,)
      return (lons.reshape(tail_shape),
              lats.reshape(tail_shape),
              speeds.reshape(tail_shape))
  ```

  Boucle Python sur **13** (le nb de corps), pas sur S. Le coût est `O(13)` indépendant de la taille du batch. C'est l'approche la plus rapide possible sans toucher à `ephemeris/planets.py`.

- **Option B (rejetée) — boucler sur S avec `body_properties` scalaire** : 13 × S appels Python au lieu de 13. Inutilement lent dès que S > 10.

- **Option C (rejetée) — refactor `body_properties` pour accepter array-jd nativement** : touche `ketu/calculations.py` et `ketu/ephemeris/planets.py:255`, hors scope (CONTEXT § Integration Points : « bias is "wrap externally, do not edit upstream modules in this phase" »).

**Verdict :** Option A. Pas de refactor upstream, pas de boucle Python sur S pour les positions.

### Helper privé `_build_aspect_matrix` (D-16, D-17)

```python
def _build_aspect_matrix(
    jd_b: np.ndarray,
    body_lons: np.ndarray,        # shape (*S, 13)
    aspects: AspectSetSpec,
) -> tuple[np.ndarray, np.ndarray]:
    S = jd_b.shape
    matrix = np.full(S + (13, 13), -1,     dtype=np.int8)
    orbs   = np.full(S + (13, 13), np.nan, dtype=np.float32)

    # Diagonal stays at sentinel; init done.

    # Python loop over leading shape S (D-16 explicitly accepts this).
    for idx in np.ndindex(S):
        jd_scalar = float(jd_b[idx])
        records = calculate_aspects_vectorized(jd_scalar, aspects=aspects)
        # records: structured array with fields body1, body2, i_asp, orb
        for rec in records:
            i, j = int(rec["body1"]), int(rec["body2"])
            i_asp = int(rec["i_asp"])
            orb   = float(rec["orb"])
            # Upper triangle from calculator (i < j by convention,
            # cf. aspects/calculator.py:187 triu_indices)
            matrix[idx + (i, j)] = i_asp
            matrix[idx + (j, i)] = i_asp           # D-17 mirror
            orbs[  idx + (i, j)] = orb
            orbs[  idx + (j, i)] = orb

    return matrix, orbs
```

**Pourquoi la boucle est OK pour v1.2 (D-16) :** `compute_chart` est appelé pour des batchs ML de l'ordre de la centaine de charts (synastry/composite/solar return), pas du million de timestamps. Sur S=100, la boucle Python sur S coûte ~100 appels à `calculate_aspects_vectorized` qui est déjà vectorisé sur les 78 paires de corps (`triu_indices(13, k=1)` → 78 paires). Profilage Phase 16 décidera si v1.3 doit ré-implémenter en pur-vector.

**Cas limite à pinner en test :** `np.ndindex(()) → [()]` une fois, donc le scalar-jd traverse correctement la même boucle (idx vide). À tester.

---

## 4. Stratégie d'implémentation `is_day_chart`

### Pseudocode complet

```python
def is_day_chart(
    jd: ArrayLike,
    lat: ArrayLike,
    lon: ArrayLike,
) -> np.ndarray:
    """Return True if the Sun is at or above the horizon (sunrise inclusive)."""
    # 1. Broadcast (mirror compute_chart)
    jd_b, lat_b, lon_b = np.broadcast_arrays(
        np.asarray(jd,  dtype=np.float64),
        np.asarray(lat, dtype=np.float64),
        np.asarray(lon, dtype=np.float64),
    )

    # 2. Compute houses with Porphyry polar fallback (D-15)
    houses = calculate_houses(
        jd_b, lat_b, lon_b,
        system="placidus", polar_fallback="porphyry",
    )

    # 3. Sun longitude per element — single-body batch call
    sun_lon = calc_planet_position_batch(jd_b.ravel(), 0)[:, 0].reshape(jd_b.shape)

    # 4. Map Sun to its house (D-14)
    sun_house = house_of(sun_lon, houses["cusps"])  # shape == jd_b.shape

    # 5. Above-horizon hemisphere = houses 7..12 (D-14)
    # Sunrise inclusive: Sun ON the ASC (==house 1 boundary) goes to day.
    # Sun in house 7..12 = above horizon = day.
    # house_of returns 1..12 ; we want True for {7, 8, 9, 10, 11, 12}.
    return sun_house >= 7
```

### Points clés à documenter dans la docstring

- **D-13 sunrise-inclusive loudly :** « Equality at the horizon (Sun exactly on ASC) resolves to **day** ». Hellenistic standard (Solar Fire / Astro.com / Robert Hand). C'est exactement ce que produit la formule géométrique : un Sun à `cusps[0] = ASC` est en maison 1 par convention `house_of` (`ketu/houses/api.py:202-204` : « A planet at exactly cusps[0] (the ASC) is in house 1 »), donc `sun_house >= 7` est `False`, donc... attend.

  **Subtilité importante :** la convention "sunrise inclusive = day" implique que Sun ON the ASC = day. Mais Sun en maison 1 (juste sous l'horizon, après l'ASC vers la maison 2) = nuit. Donc le **point exact** de l'ASC est ambigu : la définition "Sun in {7..12} = day" ne couvre pas l'égalité stricte. Solution : utiliser une comparaison "Sun >= ASC en distance angulaire éclipt vers l'ouest" plutôt que "Sun in upper hemisphere".

  **À clarifier dans le plan :** la formulation D-14 ("houses 7-12 = above horizon") est correcte modulo l'ambiguïté du strict-equality à l'ASC. Une implémentation propre :
  ```python
  # Distance Sun→ASC mesurée vers l'ouest (sens des maisons)
  # Si Sun est exactement sur l'ASC, dist = 0 ; on veut day.
  # Si Sun est juste après l'ASC en maison 1, dist > 0 mais petit ; on veut night.
  # Si Sun est en maison 7 (DESC), dist = 180° ; on veut day.
  dist_west = (sun_lon - houses["asc"]) % 360.0
  # Day si Sun est sur la moitié occidentale [0, 0] ∪ [180, 360]…
  # NON : c'est compliqué. La règle "houses 7..12" + traitement explicite de
  # l'égalité Sun==ASC est plus claire :
  on_asc = np.isclose(sun_lon % 360.0, houses["asc"] % 360.0, atol=1e-9)
  return (sun_house >= 7) | on_asc
  ```

  **Note pour le planner :** ce détail d'égalité-à-l'ASC est probablement irrelevant en pratique (probabilité 0 sur des données réelles), mais doit être pinné par un test pour le contrat sunrise-inclusive (D-13). Pas besoin d'être maladroit dans la prod : la branche `on_asc` est le cas dégénéré pédagogique. Discutable de le simplifier en `sun_house >= 7` tout court et de documenter "égalité-stricte ne survient jamais en pratique numérique" — laisser le planner trancher en fonction du test fixture qu'il choisira.

- **D-15 Porphyry polar safety loudly :** « `is_day_chart` calculates its own ASC + cusps internally with `polar_fallback='porphyry'` so high-latitude callers (Arabic Parts at lat > 66.5°) don't fail silently or raise. Porphyry is mathematically defined at all latitudes. » Le ton de `ketu/houses/api.py:74-83` (Notes section pour les cas-limites) est le bon registre.

- **Vectorisation :** docstring exemple avec `is_day_chart(np.array([…]), np.array([…]), np.array([…]))` retournant un array de bool de même shape — symétrique à `compute_chart`'s docstring.

---

## 5. Vectorisation : gotchas pour le planner

### `positions` / `body_properties` — état actuel

| Fonction | Fichier:ligne | Accepte array-jd ? | Solution Phase 14 |
|---|---|---|---|
| `body_properties(jd, body_id)` | `ketu/calculations.py:95` | ❌ `lru_cache(maxsize=1024)`, scalar-jd seulement | N'utilise PAS pour Phase 14. |
| `positions(jdate, l_bodies)` | `ketu/calculations.py:461` | ❌ Boucle Python `[long(jdate, body) for body in bodies_id]` | N'utilise PAS pour Phase 14. |
| `calc_planet_position_batch(jd_array, planet_id)` | `ketu/ephemeris/planets.py:431` | ✅ accepte `np.ndarray` de jd, retourne `(n, 6)` | **Brique de base de `_vectorised_body_properties`.** |

**Verdict :** ne PAS toucher `body_properties` ni `positions`. Bâtir directement sur `calc_planet_position_batch`. La seule boucle Python qu'on s'autorise pour les positions est sur les **13 corps**, pas sur S. Cf. §3 Option A.

### `compute_ascmc` broadcast-ready ?

Oui (`ketu/houses/ascmc.py:73`) — vu dans le code, `compute_ascmc` accepte des arrays via `np.broadcast_arrays`. La vectorisation interne lifte `sidereal_time` (scalar-only) via list-comprehension (`ascmc.py:65-68`) — coût négligeable. **Donc `calculate_houses` est nativement vectorisé sur (jd, lat, lon).** Pas de wrapper nécessaire pour la portion houses.

### Contrat de leading-shape HOUSES_DTYPE

`calculate_houses(jd_array, lat_array, lon_array, …)` retourne une structured array de HOUSES_DTYPE de leading shape == `np.broadcast_shapes(jd, lat, lon)` (cf. `houses/api.py:154 : out = np.empty(jd_b.shape, dtype=HOUSES_DTYPE)`). Pour S=(N,) on a `houses["cusps"].shape == (N, 12)`, `houses["asc"].shape == (N,)`. Exactement ce que CHART_DTYPE attend pour ses champs houses inline (D-03). Affectation directe sans reshape.

### Points pratiques

- **`np.broadcast_arrays` ne copie pas** : il retourne des vues. `np.empty(S, dtype=CHART_DTYPE)` puis `out["jd"] = jd_b` matérialise. C'est le pattern de `houses/api.py:154-163`, à ré-utiliser tel quel.
- **`np.ndindex(())` itère une fois sur le tuple vide** : la boucle de `_build_aspect_matrix` traite le cas scalaire correctement sans branche spéciale. À pinner par test.
- **Type hints :** `ArrayLike = Union[float, np.ndarray]` — alias déjà défini dans `houses/api.py:25`. Réutiliser ce pattern (l'importer si on veut, mais le re-déclarer localement est aussi OK et plus self-contained).
- **`mypy --strict` :** `_vectorised_body_properties` doit retourner `tuple[np.ndarray, np.ndarray, np.ndarray]` avec annotations explicites. Pattern dans `houses/ascmc.py:30, 73`.

---

## 6. Stratégie de tests

### Fichiers de test (sous `tests/charts/`)

| Fichier | Couvre | Réutilisation |
|---|---|---|
| `tests/charts/__init__.py` | (vide) | Convention pytest. |
| `tests/charts/conftest.py` | Oracle swisseph + reference charts | **Importe** depuis `tests/houses/conftest.py` les helpers `swe_oracle`, `SYSTEM_BYTES`, `reference_charts`, `loaded_reference_snapshot` ; ajoute des fixtures spécifiques aspects. |
| `tests/charts/test_dtype.py` | Structure CHART_DTYPE (noms, shapes, sentinelles) | Pattern verbatim de `tests/houses/test_dtype.py`. Pas de swisseph. |
| `tests/charts/test_compute_chart.py` | API publique : scalaire, batch, dispatch system, polar_fallback, leading-shape, équivalence vs `calculate_houses` standalone | Pattern de `tests/houses/test_integration.py`. |
| `tests/charts/test_compute_chart_vectorisation.py` | Vectorisation explicite (success criterion 14.2) — shapes 0-d, 1-d, 2-d ; round-trip houses | Mirror du pattern broadcast de `houses/test_integration.py`. |
| `tests/charts/test_aspect_matrix.py` | Matrice dense, symétrie, sentinelles (-1 / NaN), diagonale, default CLASSICAL, AspectSetSpec pass-through, 2-3 charts hand-validated | Nouveau ; consomme `calculate_aspects_vectorized` standalone comme oracle interne (déjà testé Phase 9). |
| `tests/charts/test_is_day_chart.py` | Sect, sunrise-inclusive, polar safety (Porphyry), vectorisation, cohérence vs CHART_DTYPE | Nouveau ; pas de swisseph (pure logique géométrique). |

### Réutilisation `tests/houses/conftest.py`

L'oracle swisseph + le reference_charts fixture sont **trivialement ré-utilisables** pour valider la portion houses de CHART_DTYPE. Au lieu de dupliquer, deux options :

- **Option recommandée :** dans `tests/charts/conftest.py`, faire un `from tests.houses.conftest import swe_oracle, reference_charts, loaded_reference_snapshot`. Pytest fait le bon truc avec les fixtures importées (vérifier sur un cas simple ; il peut falloir les re-décorer `@pytest.fixture(scope="session")` localement).
- **Option fallback si l'import direct casse :** définir un `conftest.py` à `tests/conftest.py` qui expose ces fixtures globalement, ou copier-coller la liste (10 entrées, pas la mer à boire). À trancher par le planner au moment de l'écriture du test.

### Charts hand-validated pour `aspect_matrix` (CONTEXT § Specifics)

CONTEXT recommande 2-3 charts full-validated. Ma recommandation :

1. **`J2000_Paris`** (déjà dans `reference_charts`) — case de référence évidente, faciliter la cohérence cross-test.
2. **`1900_NewYork`** (déjà dans `reference_charts`) — diversité d'époque (positions planétaires assez différentes du J2000, plus de chance de capter un bug).
3. **Un chart natal "célèbre"** — au choix du planner. Recommandation : naissance de Carl Sagan (1934-11-09T05:05Z, lat=40.6943, lon=-73.9249, NYC), parce que l'ascendant Scorpio donne une distribution non-triviale de bodies à travers les maisons et les aspects sont riches (J/S/U conjonction triple intéressante). Alternative équivalente : Albert Einstein (1879-03-14T11:30 LMT Ulm).

Pour chaque chart, la validation des aspects se fait soit :

- **Par cross-validation interne :** appeler `calculate_aspects_vectorized(jd, aspects="classical")` standalone, vérifier que sa sortie remplit la matrice de la même façon que `_build_aspect_matrix`. Garantit la cohérence du wrapping, pas la correctness des aspects en absolu (mais celle-ci est déjà gardée par les tests Phase 9).
- **Par swisseph oracle :** `swe.swe_calc_ut` pour les positions de chaque corps puis recalcul manuel d'orbs. Plus robuste mais plus de boilerplate. À envisager pour les 2-3 charts hand-validated uniquement.

**Verdict :** cross-validation interne pour la majorité (cohérence wrapper/standalone), swisseph oracle pour les 2-3 hand-validated charts (correctness end-to-end). Le planner décide du dosage final.

### Coverage gate

`pytest tests/charts/ --cov=ketu.charts --cov-fail-under=95 --cov-report=term-missing` — pattern HOU-09. Documenter dans le Makefile (cf. `pyproject.toml:78-80` qui mentionne `make houses-coverage`) une cible `make charts-coverage`. CONTEXT § Integration Points le mentionne implicitement.

---

## 7. Doc gates checklist (Phase 13 → Phase 14)

Phase 13 a wiré `interrogate ≥95%` (BLOCKING) et `numpydoc validate` (warning, blocking flip Phase 20). Phase 14 est le premier nouveau module à devoir atterrir GREEN.

### Pour `interrogate ≥95%`

`pyproject.toml:99-113` config actuelle :
```toml
[tool.interrogate]
fail-under = 95
exclude = ["ketu/lunar_calendar.py", "tests", "build", "docs"]
```

`ketu/charts/` sera **automatiquement scanné** (pas dans exclude). Donc :

- [ ] **Toutes les fonctions publiques** ont une docstring : `compute_chart`, `is_day_chart`, `_build_aspect_matrix` (semi-private, mais `ignore-private = false` cf. config), `_vectorised_body_properties`.
- [ ] **Module docstrings** présents : `ketu/charts/__init__.py`, `ketu/charts/core.py`, `ketu/charts/api.py`.
- [ ] **`CHART_DTYPE`** a un docstring `#:` au-dessus (pattern `houses/core.py:35`).
- [ ] `__init__` méthodes : pas concerné (pas de classe en Phase 14).

### Pour `numpydoc validate`

`pyproject.toml:115-131` checks complets sauf EX01/SA01/ES01/GL01 (warnings ignorés). Donc le planner doit garantir :

- [ ] **Summary line** présent (PR01) — phrase impérative courte.
- [ ] **Parameters section** complète et bien typée (PR02-PR10).
- [ ] **Returns section** présente (RT01-RT05).
- [ ] **Raises section** si la fonction lève — `compute_chart` peut propager `HighLatitudeError` via `calculate_houses`.
- [ ] Pas d'EX01/SA01/ES01/GL01 à régler (whitelistés).

**Référence à mimer :** `ketu/houses/api.py:35-97` (calculate_houses docstring) — c'est le standard de qualité v1.1 et il passe les deux gates. Le copier-paste structurel + adapter au contenu de `compute_chart` est la voie sûre.

### Section "Why structured array" (success criterion 14.5)

Va dans le **module docstring de `ketu/charts/core.py`**, section dédiée nommée `"Why a structured array?"`. Pas dans `__init__.py` (qui re-exporte juste), pas dans `api.py` (qui héberge les functions). Dans `core.py` aux côtés de la définition de CHART_DTYPE — c'est le bon endroit logique.

Si on veut être ceinture+bretelles : ajouter un pointeur depuis le `__init__.py` (`See Also` section) vers `core.py`. Mais le contenu canonique vit en un seul endroit (DRY).

---

## 8. Recommandation de découpage en plans

5 plans atomiques, exécutables en 2 vagues :

### Vague 1 (séquentielle — fondation)

| # | Plan | Scope (1 ligne) | Dépendances | Couverture REQ |
|---|---|---|---|---|
| 1 | **`14-01-skeleton-and-dtype.md`** | Crée `ketu/charts/` (`__init__.py`, `core.py` vide d'API mais avec module docstring "Why structured array" + `CHART_DTYPE`, `api.py` stub avec signatures), + `tests/charts/test_dtype.py` qui pinne field names / shapes / sentinelles. | — | CHART-01, CHART-02 (partiel : structure) |

### Vague 2 (parallèle — implémentation)

| # | Plan | Scope (1 ligne) | Dépendances | Couverture REQ |
|---|---|---|---|---|
| 2 | **`14-02-compute-chart.md`** | Implémente `compute_chart` : broadcast, `_vectorised_body_properties` (basé sur `calc_planet_position_batch`), assemblage des champs houses + bodies + métadonnées dans CHART_DTYPE. NE FAIT PAS encore aspect_matrix (champs initialisés à -1/NaN). Tests : `test_compute_chart.py` + `test_compute_chart_vectorisation.py`. | Plan 1 | CHART-03 (sans aspects) |
| 3 | **`14-03-aspect-matrix.md`** | Ajoute `_build_aspect_matrix` (boucle Python sur S + `calculate_aspects_vectorized` + projection dense + mirror D-17), branche dans `compute_chart`, gère `aspects=` AspectSetSpec pass-through. Tests : `test_aspect_matrix.py` (incluant 2-3 hand-validated charts). | Plan 2 | CHART-03 (volet aspects) |
| 4 | **`14-04-is-day-chart.md`** | Implémente `is_day_chart` (broadcast + `calculate_houses` polar Porphyry interne + `house_of` + sect logic D-13/14). Tests : `test_is_day_chart.py` (sunrise-inclusive, polar safety, vectorisation, cohérence avec CHART_DTYPE.asc + body_lons[0]). | Plan 1 (pour CHART_DTYPE et la place dans api.py ; **PAS** Plan 2/3 — `is_day_chart` est indépendant de `compute_chart`) | CHART-04 |
| 5 | **`14-05-doc-gates-and-coverage.md`** | Pass complet `interrogate` + `numpydoc validate` sur `ketu/charts/` ; ajoute `make charts-coverage` Makefile target ; vérifie ≥95 % coverage gate ; nettoie les docstrings finales (Notes, Raises, Examples vectorisés). | Plans 2+3+4 | CHART-05 |

### Justification du découpage

- **Plan 1 isolé :** la définition de CHART_DTYPE est le contrat de toute la phase. Le pinner par tests structurels en premier permet aux Plans 2-4 de se développer en parallèle sans redrift sur les noms/shapes de champs.
- **Plans 2 et 3 séquentiels :** `_build_aspect_matrix` consomme `body_lons` que `compute_chart` produit. Découper évite un PLAN.md géant qui mélange broadcast/houses/positions ET la logique aspect-matrix.
- **Plan 4 indépendant de 2/3 :** `is_day_chart` ne touche pas à `compute_chart`. Parallélisable avec Plans 2 et 3 si l'orchestrateur supporte le branchement.
- **Plan 5 final :** le sweep doc + coverage est le finishing touch. Le sortir évite que chaque plan d'implémentation se distrait avec interrogate/numpydoc — chacun écrit des docstrings « bonnes » et le Plan 5 garantit le « parfait ».

### Variantes acceptables (au planner de trancher)

- Fusionner Plan 4 dans Plan 1 (skeleton + dtype + is_day_chart) si on veut que la Vague 2 soit purement compute_chart-centrée. Trade-off : Plan 1 grossit légèrement (~ +50 lignes) mais Plan 4 disparaît.
- Fusionner Plans 2 et 3 (compute_chart complet en un seul plan) si le planner juge le scope d'un plan « compute_chart sans aspects » trop artificiel. Trade-off : un seul gros plan vs deux petits ; le test step est plus lourd.
- Sortir un Plan dédié « Makefile + Phase-13 doc-gate verification » au lieu de l'intégrer dans Plan 5. Surcoût : un plan trivial supplémentaire ; bénéfice : isolation du change pyproject/Makefile vis-à-vis du code.

---

## Phase Requirements

| ID | Description (REQUIREMENTS.md) | Plans qui la couvrent |
|---|---|---|
| CHART-01 | `ketu/charts/` subpackage avec `__init__.py` exposant l'API publique | Plan 1 |
| CHART-02 | `CHART_DTYPE` structured array (positions par body + ASC/MC/ARMC/Vertex + cusps + aspects) ML-interop | Plan 1 |
| CHART-03 | `compute_chart(jd, lat, lon, system, aspects) → CHART_DTYPE` un appel, vectorisable | Plans 2 + 3 |
| CHART-04 | `is_day_chart(jd, lat, lon) → bool` vectorisable, sunrise-inclusive | Plan 4 |
| CHART-05 | Couverture ≥95 % sur `ketu/charts/` (gate identique houses v1.1) | Plan 5 (validation finale) |

---

## Project Constraints (from CLAUDE.md + ROADMAP cross-cutting)

Le planner **DOIT** vérifier que tous les plans honorent :

- **Persona :** Sophie Chen, français + tutoiement dans tous les artefacts conversationnels (PLAN.md narratifs OK en français, code/docstrings restent en anglais — précédent v1.1).
- **Standalone :** aucune dépendance sur MarketStream / Kala / autre projet Solaris.
- **Venv :** `venv/` (pas `.venv/`).
- **NumPy first :** structured arrays, pas de dataclass, pas de dict de scalaires.
- **Non-breaking minor strict (v1.2) :** Phase 14 est **purement additive**. Aucun champ existant modifié, aucun export retiré, aucun défaut changé sur une API existante. `ketu/houses/`, `ketu/aspects/`, `ketu/calculations.py` intouchés.
- **Pure-NumPy contract :** zéro nouvelle dépendance runtime. `pysweph` reste test-only.
- **Python 3.10+ :** type hints `from __future__ import annotations` + `Literal` etc.
- **Mypy `--strict` clean** sur `ketu/charts/` dès le départ (pas dans la liste des modules carve-out de `pyproject.toml:144-153`).
- **UTC-only :** comme partout. Documenter dans la docstring `compute_chart` que `jd` est un Julian Date UT.
- **Doc gates depuis Phase 13 :** `interrogate ≥95 %` + `numpydoc validate` doivent rester verts. Phase 14 ajoute du code couvert dès le départ.
- **AGPL boundary :** runtime imports de `ketu/charts/` ne doivent **pas** introduire `swisseph`. Tests-only.

---

## Test Framework

| Property | Value |
|---|---|
| Framework | pytest (déjà installé, `pyproject.toml:66-80`) |
| Config file | `pyproject.toml [tool.pytest.ini_options]` |
| Quick run command (pendant dev d'un plan) | `pytest tests/charts/ -x -v` |
| Full suite command | `pytest tests/ --cov=ketu --cov-report=term-missing` |
| Charts coverage gate | `pytest tests/charts/ --cov=ketu.charts --cov-fail-under=95 --cov-report=term-missing` (à wirer dans `Makefile` Plan 5) |

### Wave 0 Gaps (à créer avant de commencer Plan 2)

- [ ] `tests/charts/__init__.py` (vide)
- [ ] `tests/charts/conftest.py` (oracle imports + fixtures locales)
- [ ] Pas d'install supplémentaire requis : pytest, numpy, pysweph (test-only) sont déjà dans `[project.optional-dependencies].test`.

---

## Pitfalls communs identifiés

### Pitfall 1 — Boucle Python sur S pour les positions

**Erreur :** appeler `body_properties(jd, body_id)` (cached, scalar-only) dans une boucle sur S × 13.
**Pourquoi ça arrive :** `body_properties` est l'API publique « naturelle » qu'on voit dans `calculations.py`.
**Comment l'éviter :** utiliser `calc_planet_position_batch(jd_array, body_id)` (`ephemeris/planets.py:431`) qui est nativement vectorisé sur jd. Boucle Python sur les **13 corps**, pas sur **S**.
**Signe précurseur :** `compute_chart` qui scale linéairement avec S au lieu d'asymptotiquement constant en Python overhead.

### Pitfall 2 — Re-déclencher la registry des houses

**Erreur :** copier-coller `from . import placidus  # noqa: F401` etc. de `ketu/houses/__init__.py:41-43` dans `ketu/charts/__init__.py` par mimétisme.
**Pourquoi ça arrive :** copier-paste mécanique du pattern v1.1.
**Comment l'éviter :** `ketu/charts/` n'a **pas** de registry. Pas de submodules à déclencher. `__init__.py` reste minimal (re-export `core` + `api`).
**Signe précurseur :** `ImportError` sur `ketu.charts.placidus` (qui n'existe pas).

### Pitfall 3 — Confusion AspectSetSpec strings vs masks

**Erreur :** passer `aspects="classical"` à `_build_aspect_matrix` puis le re-passer à `calculate_aspects_vectorized` qui ré-appelle `resolve_aspect_set` à chaque itération de S.
**Pourquoi ça arrive :** `calculate_aspects_vectorized` accepte AspectSetSpec, on est tenté de pass-through naïf.
**Comment l'éviter :** appeler `resolve_aspect_set(aspects)` **UNE SEULE FOIS** au-dessus de la boucle S, passer le **bool mask** résolu à `calculate_aspects_vectorized` à chaque itération. Pattern de `calculator.py:294` (batch resolves once above its date loop).
**Signe précurseur :** profiling montre `resolve_aspect_set` appelé S fois.

### Pitfall 4 — Convention "sunrise inclusive" mal appliquée

**Erreur :** retourner `sun_house >= 7` sans traiter le cas `sun_lon == asc` strict.
**Pourquoi ça arrive :** la formulation D-14 ("houses 7-12 = above horizon") suggère une comparaison simple, mais D-13 force "Sun on ASC = day", or `house_of` met un Sun ON the ASC en maison 1.
**Comment l'éviter :** soit ajouter une branche `np.isclose(sun_lon, asc) → True`, soit utiliser une formulation géométrique distance-angle directement, et **pinner le cas par un test** quoi qu'il en soit.
**Signe précurseur :** test "Sun exactement sur l'ASC" retourne `False` au lieu de `True`.

### Pitfall 5 — Symétrie aspect_matrix oubliée

**Erreur :** remplir uniquement `matrix[i,j]` (upper triangle, comme `triu_indices` le fournit) sans miroir D-17.
**Pourquoi ça arrive :** `calculate_aspects_vectorized` retourne déjà `body1 < body2` (upper triangle), on est tenté de copier directement.
**Comment l'éviter :** TOUJOURS écrire `matrix[i,j] = matrix[j,i] = i_asp` et `orbs[i,j] = orbs[j,i] = orb`. Test pinné : `np.array_equal(matrix, matrix.T)` modulo le sentinel pattern.
**Signe précurseur :** caller code écrit `chart["aspect_matrix"][3,5]` retourne -1 alors que `chart["aspect_matrix"][5,3]` retourne 7.

### Pitfall 6 — Float comparison dans diagonale

**Erreur :** initialiser `aspect_orbs` à `0.0` au lieu de `np.nan` pour la diagonale.
**Pourquoi ça arrive :** `np.empty` puis remplissage, on oublie d'init la diagonale ; ou on pense que `0.0` est suffisant comme sentinel.
**Comment l'éviter :** `np.full(S + (13, 13), np.nan, dtype=np.float32)` au lieu de `np.empty`. Diagonale reste `NaN` naturellement (jamais écrite). Test pinné : `assert np.isnan(chart["aspect_orbs"][..., i, i]).all() for i in range(13)`.
**Signe précurseur :** `chart["aspect_orbs"] == 0` matche la diagonale ET les rares cases `i_asp == 0` (conjonction exacte avec orb 0).

---

## Architecture — diagramme de flux

```
                  compute_chart(jd, lat, lon, system, aspects, polar_fallback)
                                   │
                ┌──────────────────┼─────────────────────────┐
                │                  │                         │
                ▼                  ▼                         ▼
      np.broadcast_arrays    calculate_houses    _vectorised_body_properties
      (jd, lat, lon)         (HOUSES_DTYPE        (loop sur 13 bodies →
       → leading shape S      → cusps, asc,        calc_planet_position_batch)
                              mc, armc, vertex)    → body_lons, lats, speeds
                │                  │                         │
                │                  │                         │
                │                  ▼                         ▼
                │          ┌───────────────────────────────────────┐
                │          │  _build_aspect_matrix                 │
                │          │   for idx in np.ndindex(S):           │
                │          │     calculate_aspects_vectorized      │
                │          │       (jd, mask) → records            │
                │          │     project records → matrix[idx]     │
                │          │       (upper + mirror lower D-17)     │
                │          └───────────────────────────────────────┘
                │                              │
                ▼                              ▼
           ┌───────────────────────────────────────────────┐
           │  Assemble CHART_DTYPE :                       │
           │   out["jd"]=jd_b ; out["asc"]=houses["asc"]   │
           │   out["body_lons"]=body_lons ; etc.           │
           │   out["aspect_matrix"]=matrix ;               │
           │   out["aspect_orbs"]=orbs                     │
           └───────────────────────────────────────────────┘
                              │
                              ▼
                       CHART_DTYPE array
                       leading shape S


            is_day_chart(jd, lat, lon)
                     │
                     ▼
        np.broadcast_arrays(jd, lat, lon) → S
                     │
       ┌─────────────┼──────────────────────┐
       ▼             ▼                      ▼
 calculate_houses  calc_planet_position    house_of(sun_lon, cusps)
 (system="placidus", _batch(jd_flat, 0)    → sun_house ∈ {1..12}
  polar_fallback="porphyry")                       │
       │              │                            │
       │              ▼                            │
       │           sun_lon                         │
       └──────────────┼────────────────────────────┘
                      ▼
              return (sun_house >= 7)
              [+ on_asc edge case if planner keeps it]
              shape == S, dtype == bool
```

---

## Sources

### Primary (HIGH confidence — code vérifié in situ)

- `ketu/houses/core.py:35-45` — HOUSES_DTYPE structure (D-01/D-03 mirror précis).
- `ketu/houses/api.py:28-165` — calculate_houses broadcast pattern (template direct pour compute_chart).
- `ketu/houses/api.py:168-230` — house_of (consommé par is_day_chart, retourne 1..12, convention « cusps[i] BEGINS house i+1 »).
- `ketu/houses/ascmc.py:73-161` — compute_ascmc (déjà vectorisé, appelé en interne par calculate_houses).
- `ketu/aspects/calculator.py:135-249` — calculate_aspects_vectorized (returns structured array body1/body2/i_asp/orb ; emits canonical 0-13 i_asp ; upper-triangle uniquement).
- `ketu/aspects/calculator.py:294-303` — pattern « resolve aspect-set ONCE above hot loop » (à appliquer dans `_build_aspect_matrix`).
- `ketu/aspects/presets.py:84-220` — CLASSICAL preset + AspectSetSpec + resolve_aspect_set (D-07, D-10).
- `ketu/calculations.py:95-136` — body_properties (lru_cache, scalar-only — à NE PAS utiliser dans Phase 14).
- `ketu/calculations.py:461-489` — positions (boucle Python — à NE PAS utiliser dans Phase 14).
- `ketu/ephemeris/planets.py:431-518` — calc_planet_position_batch (vectorisé sur jd, retourne (n, 6) — **brique clé**).
- `ketu/cycles/calculator.py:37-55` — CYCLE_DTYPE (alternative structured-array precedent ; flat per-row, contraste utile pour confirmer que CHART est subarray-heavy).
- `tests/houses/conftest.py:1-255` — swisseph oracle pattern complet, ré-utilisable pour CHART_DTYPE.
- `tests/houses/test_dtype.py:1-67` — pattern de test structurel CHART_DTYPE.
- `tests/houses/test_integration.py:1-120` — pattern de test broadcast/oracle pour calculate_houses.
- `pyproject.toml:99-131` — config interrogate + numpydoc à respecter dès Plan 1.

### Secondary (HIGH — documents de planification internes)

- `.planning/phases/14-chart-abstraction-foundation/14-CONTEXT.md` — D-01..D-17 LOCKED.
- `.planning/ROADMAP.md` § Phase 14 — 5 success criteria.
- `.planning/REQUIREMENTS.md` § CHART-01..05.
- `.planning/phases/13-doc-gates-and-ci-foundation/13-CONTEXT.md` — D-06/D-07/D-14 (scope numpydoc + interrogate).

### Tertiary (LOW — knowledge background non vérifié dans cette session)

- Convention sunrise-inclusive sect (Hellenistic standard, Solar Fire / Astro.com / Robert Hand) — `[CITED: CONTEXT.md D-13]` qui le déclare déjà résolu. Pas re-vérifié contre source externe (LOCKED).
- Marriage de la formule "houses 7..12 = above horizon" avec la convention sunrise-inclusive — `[ASSUMED]` que les deux sont co-cohérentes modulo le cas-limite Sun==ASC analysé en §4. À pinner par test.

### Versions vérifiées

- `numpy 2.3.5` (installé localement dans `venv/`, vérifié via `python -c "import numpy; print(numpy.__version__)"`). Le code Phase 14 cible `numpy>=1.20` (cf. `pyproject.toml:38`) ; aucun usage de feature numpy 2.x exclusive prévu.
- `pyswisseph` test-only, version pinnée `>=2.10.3.6` (`pyproject.toml:43`).

---

## Assumptions Log

| # | Claim | Section | Risk si faux |
|---|---|---|---|
| A1 | `np.ndindex(())` itère exactement une fois sur `()` (donc le scalar-jd traverse correctement la boucle de `_build_aspect_matrix`) | §3, §5 | Moyen — si faux, scalar-jd casserait. Mitigation : test pinné explicite « scalar-jd compute_chart works ». **À vérifier au moment de l'implémentation par un quick `python -c "import numpy as np; list(np.ndindex(()))"` — devrait imprimer `[()]`.** |
| A2 | Importer fixtures depuis `tests/houses/conftest.py` dans `tests/charts/conftest.py` fonctionne sans re-décorer | §6 | Bas — si faux, fallback est de copier-coller la liste des 10 reference_charts (10 lignes). Pas bloquant. |
| A3 | Le cas-limite « Sun exactement sur l'ASC » n'arrive jamais en données réelles (probabilité 0 numérique) | §4 | Bas — c'est le cas-test pédagogique. Si on simplifie en `sun_house >= 7` tout court, on viole D-13 stricto sensu mais en pratique zéro impact. **Demande arbitrage planner** : implémentation pédagogique avec branche `on_asc` ou implémentation pragmatique sans. |
| A4 | `i1` (signed int8) est suffisant pour aspect_matrix sentinel `-1` + indices ∈ [0, 13] | §2 | Aucun — `i1` couvre [-128, 127], aspects canoniques ∈ [0, 13]. Verified. |
| A5 | `f4` (NaN-capable) est suffisant pour aspect_orbs (orbs ≤ 12° en pratique) | §2 | Aucun — orbs maximaux ~24° (cf. `ketu/core.py:67-79`, max body orb 12°, max sum 24°), `f4` couvre largement avec NaN distinct de 0. Verified. |

**Ces 5 assumptions sont les seules dans tout le RESEARCH.md.** Le reste est tracé à du code lu en session ou à CONTEXT/ROADMAP/REQUIREMENTS.

---

## Open Questions (à trancher au planning)

1. **Branche `on_asc` dans `is_day_chart` : pédagogique ou pragmatique ?** (cf. A3 ci-dessus, §4 Pitfall 4)
   - Pédagogique : ajouter `on_asc = np.isclose(sun_lon, asc) ; return (sun_house >= 7) | on_asc` + test pinné dédié.
   - Pragmatique : `return sun_house >= 7` tout court + commentaire « strict equality at ASC has measure-zero in practice ; documented as day per D-13 ».
   - **Recommandation Sophie :** pragmatique. Le test pinné peut quand même valider la convention sur un cas de calculs synthétique (Sun à 0.01° before/after ASC) sans avoir à coder la branche dans la prod.

2. **`tests/charts/conftest.py` : import depuis `tests/houses/conftest.py` ou copier-coller ?** (cf. A2 ci-dessus, §6)
   - À tester en dev. Si l'import marche → DRY win. Si non → copy-paste les 10 lignes du fixture, c'est trivial.

3. **Reference chart hand-validated #3 (Sagan ou Einstein) ?** (cf. §6)
   - Choix purement esthétique. Sagan = scorpion ascendant + triple conjonction Jupiter/Saturn/Uranus dans les Poissons (riche en aspects). Einstein = ascendant Cancer, distribution plus calme. Recommandation : **Sagan**, plus de signal pour un test d'aspect_matrix.

---

## Validation Architecture

### Test Framework

| Property | Value |
|---|---|
| Framework | pytest 8.x (déjà installé, cf. `pyproject.toml`) |
| Config file | `pyproject.toml [tool.pytest.ini_options]` |
| Quick run command | `pytest tests/charts/ -x -v` |
| Full suite command | `pytest tests/ -v --cov=ketu --cov-report=term-missing` |

### Phase Requirements → Test Map

| REQ | Behavior | Test type | Automated command | File status |
|---|---|---|---|---|
| CHART-01 | `from ketu.charts import …` resolves | unit | `pytest tests/charts/test_dtype.py::test_public_imports -x` | ❌ Wave 0 / Plan 1 |
| CHART-02 | CHART_DTYPE has 14 fields, correct shapes | unit (structural) | `pytest tests/charts/test_dtype.py -x` | ❌ Wave 0 / Plan 1 |
| CHART-03 (positions) | compute_chart vectorise body_lons sur S | integration | `pytest tests/charts/test_compute_chart.py -x` | ❌ Plan 2 |
| CHART-03 (houses) | compute_chart copie cusps/asc/mc/armc/vertex de calculate_houses | integration | `pytest tests/charts/test_compute_chart.py::test_houses_inline -x` | ❌ Plan 2 |
| CHART-03 (aspects) | aspect_matrix dense + symétrique + sentinelles | integration | `pytest tests/charts/test_aspect_matrix.py -x` | ❌ Plan 3 |
| CHART-03 (vectorisation) | scalar/1-d/2-d (jd, lat, lon) shapes round-trip | integration | `pytest tests/charts/test_compute_chart_vectorisation.py -x` | ❌ Plan 2 |
| CHART-04 | is_day_chart vectorisé + sunrise inclusive + polar safe | unit + integration | `pytest tests/charts/test_is_day_chart.py -x` | ❌ Plan 4 |
| CHART-05 | ≥95 % coverage `ketu/charts/` | gate | `pytest tests/charts/ --cov=ketu.charts --cov-fail-under=95` | gate command, validated Plan 5 |

### Sampling Rate

- **Per task commit** (pendant développement d'un plan) : `pytest tests/charts/ -x -v`
- **Per wave merge** : `pytest tests/ -v --cov=ketu --cov-report=term-missing`
- **Phase gate** (avant `/gsd-verify-work`) : full suite green + coverage gate `make charts-coverage` (à créer Plan 5).

### Wave 0 Gaps

- [ ] `tests/charts/__init__.py` — empty marker (Plan 1)
- [ ] `tests/charts/conftest.py` — oracle imports + local fixtures (Plan 1)
- [ ] Aucun framework install supplémentaire requis : pytest, numpy, pyswisseph déjà disponibles.

---

## Metadata

**Confidence breakdown :**

- Squelette subpackage : **HIGH** — pattern v1.1 (`ketu/houses/`) directement applicable, lu in situ.
- CHART_DTYPE definition : **HIGH** — D-01..D-07 LOCKED, snippet vérifié syntaxiquement contre HOUSES_DTYPE pattern.
- compute_chart strategy : **HIGH** — toutes les briques (`calculate_houses`, `calc_planet_position_batch`, `calculate_aspects_vectorized`) sont implémentées et lues en session.
- is_day_chart strategy : **MEDIUM-HIGH** — conviction sur la stratégie (broadcast + Porphyry + house_of), mais le détail "sunrise inclusive vs house_of convention 1..12" demande arbitrage planner (cf. Open Question 1).
- Vectorisation gotchas : **HIGH** — lu directement dans calculator.py et ephemeris/planets.py.
- Test strategy : **HIGH** — pattern `tests/houses/` directement applicable, lu in situ.
- Doc gates checklist : **HIGH** — config `pyproject.toml` lu in situ, scope Phase 13 confirmé.
- Plan breakdown : **MEDIUM-HIGH** — 5-plan partition est solide, mais variantes acceptables (cf. §8 fin) — laissé à arbitrage planner.

**Recherche date :** 2026-05-08
**Valid until :** ~2026-06-08 (30 jours — codebase v1.1 stable, faible churn attendu).
