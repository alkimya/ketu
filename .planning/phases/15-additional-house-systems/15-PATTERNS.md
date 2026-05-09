# Phase 15 : Additional House Systems — Pattern Map

**Mappé :** 2026-05-09 par Sophie Chen
**Fichiers analysés :** 4 nouveaux production + 3 nouveaux tests + 2 modifs registry/CLI
**Analogues identifiés :** 9 / 9 (100 % — la Phase 10 nous a donné le gabarit littéral, on l'applique en mode copier-adapter)

> **Note de cadrage Sophie.** On a une chance encore meilleure que Phase 14 : la
> Phase 15 est une **extension additive PURE** d'un sous-package qui possède
> déjà tous ses contrats (registry, polar fallback, oracle, dtype). Pour
> Whole Sign et Equal, le code production tient en ~30 lignes vectorisées et
> mappe trivialement (closed-form, jamais polaire). Regiomontanus est plus
> verbeux (~70 lignes) mais suit la même structure que `koch.py` : ASC/MC
> closed-form, formule trig per-cusp, mask polaire → NaN. Le job du planner
> est de copier le squelette de `porphyry.py` (closed-form non polaire) pour
> Whole Sign et Equal, et de copier `koch.py` (closed-form avec mask polaire)
> pour Regiomontanus. **Aucun nouveau pattern à inventer.**

---

## Vue d'ensemble : classification des fichiers

| Fichier nouveau / modifié | Rôle | Data flow | Analogue le plus proche | Match |
|---------------------------|------|-----------|--------------------------|-------|
| `ketu/houses/whole_sign.py` (new) | system implementation | scalar/vector reduction (closed-form, no polar) | `ketu/houses/porphyry.py` | exact |
| `ketu/houses/equal.py` (new) | system implementation | scalar/vector reduction (closed-form, no polar) | `ketu/houses/porphyry.py` | exact |
| `ketu/houses/regiomontanus.py` (new) | system implementation | scalar/vector reduction (closed-form, polar→NaN) | `ketu/houses/koch.py` | exact |
| `ketu/houses/__init__.py` (modify) | package re-export + registry trigger | n/a | self (lignes 41-43, append-only) | exact |
| `tests/houses/test_whole_sign.py` (new) | oracle + invariants | param + oracle | `tests/houses/test_porphyry.py` | exact |
| `tests/houses/test_equal.py` (new) | oracle + invariants | param + oracle | `tests/houses/test_porphyry.py` | exact |
| `tests/houses/test_regiomontanus.py` (new) | oracle + polar mask + invariants | param + oracle | `tests/houses/test_koch.py` | exact |
| `tests/houses/conftest.py` (modify) | oracle harness | test-only AGPL boundary | self (lignes 77-81, append-only) | exact |
| `tests/houses/fixtures/reference_charts.json` (regenerate) | oracle snapshot | JSON snapshot | self (existant) | exact |
| `ketu/cli/introspection.py` (modify) | CLI list output | n/a | self (lignes 22-26, append-only) | exact |

---

## 1. `ketu/houses/whole_sign.py` (new — closed-form, jamais polaire)

**Closest analog :** `ketu/houses/porphyry.py` (lignes 1-193, fichier complet).

**Pourquoi cet analogue :** Whole Sign est mathématiquement la plus simple des
trois. Cusp 1 = `floor(asc / 30) * 30` (début du signe contenant l'ASC), puis
cusp `i+1 = (cusp_1 + 30*i) mod 360`. Aucune itération, aucune dépendance à la
latitude, jamais de NaN polaire. Exactement le profil de Porphyry (closed-form,
finie partout) sauf que c'est encore **plus simple** : pas de trisection à
gérer, juste un floor + arithmétique modulaire sur 30°.

**Copy (à mirorer ligne-à-ligne) :**

- Header docstring (`porphyry.py:1-17`) — pattern « 1 ligne titre + paragraphe
  motivation + bloc formule en code-style ». Style Sophie : explique la
  mathématique d'abord, pas d'excuse.
- `from __future__ import annotations` + imports NumPy (`porphyry.py:18-23`).
- Signature `@register("whole_sign") def whole_sign_cusps(armc, lat, eps)`
  identique à `porphyry_cusps` (`porphyry.py:100-105`). **Le contrat
  `(armc, lat, eps) -> cusps[..., 12]` est imposé par la registry —
  voir `ketu/houses/registry.py:34`** ; même si Whole Sign n'utilise PAS
  `lat`, la signature reste fixe.
- Pattern broadcast (`porphyry.py:134-137`) :
  ```python
  armc_b, lat_b, eps_b = np.broadcast_arrays(armc, lat, eps)
  armc_rad = np.deg2rad(armc_b)
  eps_rad = np.deg2rad(eps_b)
  lat_rad = np.deg2rad(lat_b)
  ```
- Calcul ASC/MC inline (`porphyry.py:142-151`) — Whole Sign a besoin de l'ASC
  pour déterminer le signe d'origine. Copier mot-pour-mot.
- Pattern de stack final (`porphyry.py:188-193`) :
  ```python
  result: np.ndarray = np.stack([
      asc, cusp_2, cusp_3, ic,
      cusp_5, cusp_6, desc, cusp_8,
      cusp_9, mc, cusp_11, cusp_12,
  ], axis=-1)
  return result
  ```
  **ATTENTION ordre canonique :** index 0 = ASC, 3 = IC, 6 = DESC, 9 = MC. Pour
  Whole Sign, l'ASC reste l'ASC réel (pas le début du signe) **MAIS** le cusp 1
  (qui *définit* la maison 1) est le début du signe. Vérifier le contrat avec
  swisseph oracle : `swe.houses_ex(..., b'W')` met `cusps[1] = floor(asc/30)*30`
  et la valeur ASC dans `ascmc[0]`. Notre `cusps[0]` doit-il être l'ASC réel
  ou le début du signe ?

**Adapt — formule de cusp Whole Sign :**

```python
# Début du signe contenant l'ASC : cusp1 = floor(asc/30) * 30
cusp_1 = np.floor(asc / 30.0) * 30.0
# Maisons suivantes : 30° d'écart fixe
cusps_house_n = (cusp_1 + np.arange(12) * 30.0) % 360.0  # shape (..., 12)
```

**DÉCISION CRITIQUE — `cusps[0]` doit-il être ASC ou début-de-signe ?**

Vérification effectuée : `swisseph.houses_ex(2451545.0, 48.86, 2.35, b'W')`
retourne `cusps[1..12] = [0.0, 30.0, 60.0, ...]` (= début de signe pour
Capricorne, Verseau, etc.) tandis que `ascmc[0] = 26.7722` (ASC réel).
**Conclusion :** dans la convention Ketu (cusps[0] = "house 1 cusp"), nous
DEVONS retourner le début du signe, pas l'ASC. Cela diverge du pattern
Placidus/Koch/Porphyry où cusps[0] == asc, mais c'est correct pour Whole Sign.

→ Documenter cette divergence dans le docstring : « Note: for Whole Sign,
``cusps[0]`` is the start of the rising sign, NOT the Ascendant longitude.
``out['asc']`` (set by ``calculate_houses``) preserves the true ASC. »

→ Garder ASC/MC réels dans le calcul interne pour les besoins du caller
(via `compute_ascmc` dans `api.py`), mais cusps[0] = `cusp_1`, et cusps[3] =
`(cusp_1 + 90°) % 360`, etc.

**Skip :**
- Tout le bloc polar swap (`porphyry.py:153-162`) — Whole Sign n'en a pas
  besoin, le signe contenant l'ASC est défini de la même façon à toutes les
  latitudes.
- Les fonctions auxiliaires `polar_circle` / `is_polar` / `POLAR_EPS_TOL`
  (`porphyry.py:32-97`) — déjà disponibles via `from .porphyry import ...`,
  ne pas dupliquer.

**Why this analog :** Porphyry est le seul système ketu qui est (a) closed-form,
(b) jamais NaN polaire, (c) n'a pas de masque polaire à appliquer. Exactement
le profil de Whole Sign et Equal. Koch/Placidus introduisent des complications
(itération, mask polaire) inutiles ici.

---

## 2. `ketu/houses/equal.py` (new — closed-form, jamais polaire)

**Closest analog :** `ketu/houses/porphyry.py` (lignes 1-193, fichier complet).

**Pourquoi cet analogue :** Equal House est la version « ASC + 30°×N » sans
floor. Pas de dépendance latitude (l'ASC l'absorbe), pas de polaire au sens
strict — bien que l'ASC closed-form NaN à exactement lat=90° (cas extrême
non rencontré en pratique car bloqué par `is_polar` en amont quand l'utilisateur
le veut).

**Copy : identique à Whole Sign (§1)** — header, broadcast, ASC/MC inline, stack
final. Cf. `porphyry.py:1-193`.

**Adapt — formule de cusp Equal House :**

```python
# Cusps espacés de 30° à partir de l'ASC réel
cusp_offsets = np.arange(12) * 30.0  # shape (12,)
# Broadcast asc shape (...,) avec offsets shape (12,) -> shape (..., 12)
cusps_all = (asc[..., np.newaxis] + cusp_offsets) % 360.0
```

**Convention `cusps[0]` :** vérification effectuée :
`swe.houses_ex(2451545.0, 48.86, 2.35, b'E')` retourne
`cusps[1] = 26.7722° = ASC`. **Pour Equal, `cusps[0]` = ASC** (consistent avec
le contrat houses standard, pas de divergence à documenter).

**MC traité spécialement :** dans la convention swisseph Equal, `cusps[10]`
(maison 10) est `ASC + 270° = MC equal`, **PAS le MC astronomique réel**.
Le MC astronomique réel reste dans `out["mc"]` (rempli par `calculate_houses`
via `compute_ascmc`). Donc cusps[9] (= maison 10 cusp) = `(asc + 270) % 360`,
pas le MC réel — diverge du pattern Placidus/Koch/Porphyry où cusps[9] == mc.
Documenter dans le docstring.

→ Vérification recommandée pour le planner : tester avec swe oracle qu'à
Paris J2000, `cusps[9]` ≈ `26.77 + 270 = 296.77°`, pas `281.78°` (MC réel).

**Skip : identique à Whole Sign (§1).**

**Why this analog :** même raisons que Whole Sign — closed-form, finie partout,
profile Porphyry.

---

## 3. `ketu/houses/regiomontanus.py` (new — closed-form trig, polar→NaN)

**Closest analog :** `ketu/houses/koch.py` (lignes 1-181, fichier complet).

**Pourquoi cet analogue :** Regiomontanus utilise une projection trigonométrique
sur le cercle horaire (« great circle through poles, equally spaced 30°
sections of equator »). Plus complexe que Whole Sign/Equal (cos(lat) au
dénominateur, dégénère au polaire), mais closed-form (pas d'itération comme
Placidus). Profil mathématique identique à Koch :
- Calcul ASC/MC closed-form via `arctan2`.
- Une fonction auxiliaire trig per-cusp (Koch utilise `_asc1`, Regio aura un
  équivalent).
- Mask polaire `|lat| ≥ 90 - eps` → NaN propagé.
- Cusps 5/6/8/9 dérivés par symétrie 180°.

**Copy (à mirorer ligne-à-ligne depuis `koch.py`) :**

- Header docstring avec formule (`koch.py:1-28`) — Sophie convention : motivation
  mathématique en haut, référence swisseph (`swehouse.c` case `'R'`), explication
  du polar fallback.
- `MAX_ITER` / `TOL_DEG` constants (`koch.py:38-41`) — gardés pour parité API
  même si Regio est closed-form (cf commentaire Koch : « Reserved for future
  iterative variants »). Pattern à copier littéralement.
- Helper interne (`koch.py:44-89` — `_asc1`) : Regiomontanus aura sa propre
  version (tagger `_regio_cusp` ou similaire). Mirror le pattern :
  - Pre-computed `sin_eps` / `cos_eps` passés en paramètres pour éviter les
    recalculs.
  - `np.deg2rad` / `np.rad2deg` au front et au sortie.
  - Annotation type explicite `: np.ndarray` partout.
- Signature `@register("regiomontanus") def regiomontanus_cusps(armc, lat, eps)`
  (`koch.py:92-118`).
- Calcul ASC/MC inline (`koch.py:127-138`) — copier mot-pour-mot.
- Pattern polar mask (`koch.py:140-143`) :
  ```python
  polar_mask = np.abs(lat_b) >= (90.0 - eps_b)
  ```
- Pattern application du polar mask en fin de fonction (`koch.py:174-178`) :
  ```python
  if polar_mask.any():
      mask_b = np.broadcast_to(polar_mask[..., np.newaxis], cusps.shape)
      cusps = np.where(mask_b, np.nan, cusps)
  ```
- Pattern stack final (`koch.py:168-173`) — ordre canonique cusps[0..11].

**Adapt — formule per-cusp Regiomontanus :**

Per swisseph `swehouse.c` case `'R'` :
```
Pour cusp k = 11, 12, 2, 3 :
    H_k = ARMC + 30°*k_offset    # ARMC + 30, 60, 120, 150
    tan(λ_k) = sin(H_k) / (cos(H_k)*cos(eps) - sin(eps)*tan(lat))
    λ_k évalué via arctan2 pour quadrant safety (Pitfall 2 ketu)
Cusps 5, 6, 8, 9 = opposites 180° de 11, 12, 2, 3
Cusps 1, 4, 7, 10 = ASC, IC, DESC, MC
```

**Le planner DOIT cross-checker la formule** en lisant `swehouse.c` ou en
calant sur `swe.houses_armc(armc, lat, eps, b'R')` à plusieurs latitudes.

**Skip :**
- La logique d'itération de `placidus.py` — Regio est closed-form.
- La logique de polar swap de `porphyry.py:153-162` — pas de saut polaire à
  gérer (le mask NaN suffit).

**Why this analog :** Koch est le SEUL autre système ketu qui combine
(a) closed-form, (b) helper trig auxiliaire, (c) polar mask → NaN, (d) cusps
5/6/8/9 = opposites 180°. La structure de Regio est isomorphe.

---

## 4. `ketu/houses/__init__.py` (modify — registry trigger append)

**Closest analog :** lui-même, lignes 37-43 (existant, append-only).

**Action :** ajouter 3 lignes d'import après `from . import porphyry` :
```python
from . import whole_sign     # noqa: F401  registers 'whole_sign' in SYSTEMS
from . import equal          # noqa: F401  registers 'equal' in SYSTEMS
from . import regiomontanus  # noqa: F401  registers 'regiomontanus' in SYSTEMS
```

**Pattern à respecter :**
- Commentaire `# noqa: F401  registers 'NAME' in SYSTEMS` aligné en colonne
  (cf lignes 41-43 actuelles).
- **AUCUN ajout à `__all__`** : le re-export se fait via `SYSTEMS` (la registry
  exporte les clés), pas par import direct des fonctions cusps. Exactement
  comme `placidus_cusps`, `koch_cusps`, `porphyry_cusps` ne sont PAS dans
  `__all__` aujourd'hui (lignes 45-53).

**Why :** ces imports sont nécessaires car les décorateurs `@register("name")`
ne s'exécutent qu'à l'import du module. Sans ces 3 lignes,
`calculate_houses(system="whole_sign")` lèverait `ValueError("unknown house
system 'whole_sign'")`.

---

## 5. `tests/houses/conftest.py` (modify — SYSTEM_BYTES extend)

**Closest analog :** lui-même, lignes 77-81 (existant, append-only).

**Action :** étendre le dict `SYSTEM_BYTES` :
```python
SYSTEM_BYTES: dict[str, bytes] = {
    "placidus": b"P",
    "koch": b"K",
    "porphyry": b"O",
    "whole_sign": b"W",       # NEW — Phase 15
    "equal": b"E",            # NEW — Phase 15
    "regiomontanus": b"R",    # NEW — Phase 15
}
```

**Vérification empirique faite par Sophie ce 2026-05-09 :**
```bash
python3 -c "import swisseph as swe; ..."
# b'W': OK, asc=26.7722° → cusps[1]=0.0° (start of Capricorn)
# b'E': OK, asc=26.7722° → cusps[1]=26.7722° (= ASC)
# b'R': OK, asc=26.7722° → cusps[1]=26.7722°, cusp[2]=67.692°
```

→ Les 3 codes existent dans pyswisseph, OK pour la table.

**Pattern à respecter :**
- Commentaire de tag (`# Codes per the Astrodienst hsys table`) déjà présent
  ligne 72-76. Mettre à jour pour mentionner les 3 nouveaux codes.
- Aucune autre modif au fichier — `swe_oracle` et `swe_oracle_armc` (lignes
  95-188) sont génériques sur le `system` arg et fonctionnent telles quelles
  pour les 3 nouveaux systèmes.

---

## 6. `tests/houses/fixtures/reference_charts.json` (regenerate)

**Action :** le snapshot JSON actuel ne contient que `placidus / koch /
porphyry` pour chacune des 10 reference charts. Phase 15 doit le régénérer
pour inclure `whole_sign / equal / regiomontanus`.

**Closest analog :** structure existante du JSON.

**Pattern à respecter :**
```json
{
  "version": "v1.2-phase15-snapshot",   // BUMP version
  "charts": {
    "J2000_Paris": {
      "systems": {
        "placidus": {"cusps": [...], "asc": ..., ...},
        "koch": {...},
        "porphyry": {...},
        "whole_sign": {...},      // NEW
        "equal": {...},           // NEW
        "regiomontanus": {...}    // NEW
      }
    },
    ...
  }
}
```

**Question planner : où vit le script de regen ?**

`tests/houses/conftest.py:248-252` mentionne un fichier
`scripts/snapshot_reference_charts.py` qui n'existe pas dans le repo
(`find . -name "snapshot_reference_charts.py"` → nothing). **C'est une dette
documentaire.**

→ **Recommandation Sophie pour le planner :** créer un véritable
`scripts/snapshot_reference_charts.py` lors de la Phase 15. Pattern simple :
```python
# scripts/snapshot_reference_charts.py
import json
import swisseph as swe
from pathlib import Path

REFERENCE_CHARTS = [...]  # même 10 entrées que conftest.reference_charts
SYSTEMS = {"placidus": b"P", "koch": b"K", "porphyry": b"O",
           "whole_sign": b"W", "equal": b"E", "regiomontanus": b"R"}

def main() -> None:
    out = {"version": "v1.2-phase15-snapshot", "charts": {}}
    for chart in REFERENCE_CHARTS:
        out["charts"][chart["label"]] = {"systems": {}}
        for name, code in SYSTEMS.items():
            try:
                cusps_t, ascmc_t = swe.houses_ex(...)
                out["charts"][chart["label"]]["systems"][name] = {
                    "cusps": list(cusps_t[1:13]),
                    "asc": ascmc_t[0], ...
                }
            except swe.Error as e:
                out["charts"][chart["label"]]["systems"][name] = {
                    "error": str(e), "polar": True
                }
    Path("tests/houses/fixtures/reference_charts.json").write_text(
        json.dumps(out, indent=2)
    )

if __name__ == "__main__":
    main()
```

**Why this analog :** la structure JSON existante est notre seule référence ;
le script est une dette à payer pendant la phase qui en a besoin. Mieux vaut
créer le script proprement maintenant que de re-bricoler à chaque ajout de
système (qui arrivera : Campanus, Topocentric, Alcabitius...).

---

## 7. `tests/houses/test_whole_sign.py` (new)

**Closest analog :** `tests/houses/test_porphyry.py` (lignes 1-186, fichier
complet).

**Copy (mirorage de la structure du fichier) :**

- Header docstring (`test_porphyry.py:1`) — « <System> tests — closed-form +
  invariants ».
- Imports (`test_porphyry.py:2-15`) :
  ```python
  from ketu.houses.ascmc import compute_ascmc
  from ketu.houses.whole_sign import whole_sign_cusps
  ```
- **Test oracle bit-exact via `swe_oracle_armc`** (`test_porphyry.py:94-129`) —
  c'est LE test de référence Phase 15. Pattern :
  ```python
  def test_whole_sign_algorithm_matches_oracle_armc_at_all_latitudes(
      reference_charts: list[dict[str, Any]],
  ) -> None:
      from tests.houses.conftest import swe_oracle_armc
      for chart in reference_charts:
          ascmc = compute_ascmc(...)
          cusps = whole_sign_cusps(...)
          oracle = swe_oracle_armc(armc, lat, eps, "whole_sign")
          deltas = np.abs(((cusps - oracle["cusps"] + 180.0) % 360.0) - 180.0)
          assert deltas.max() < 1e-6
  ```
  **TOLERANCE :** `1e-6°` (3.6 marcsec) car Whole Sign est purement
  arithmétique (pas de trig sensible à eps_mean vs eps_true) → match
  bit-exact attendu, contrairement à Koch (tolérance 3 arcmin à Reykjavik).
- **Test « works at all latitudes »** (`test_porphyry.py:18-43`) — Whole Sign
  ne doit JAMAIS NaN, même à lat=89°. Pattern direct.
- **Test invariant 30° spacing** (analogue à `test_porphyry_trisection_invariant_*`,
  lignes 46-74) :
  ```python
  def test_whole_sign_cusps_evenly_spaced_30_deg() -> None:
      cusps = whole_sign_cusps(...)
      # cusps[i+1] - cusps[i] = 30 mod 360 pour tout i
      diffs = np.diff(cusps) % 360.0
      np.testing.assert_allclose(diffs, 30.0, atol=1e-9)
  ```
- **Test cusp1 = début du signe** (NOUVEAU — divergence vs autres systèmes) :
  ```python
  def test_whole_sign_cusp_1_is_start_of_rising_sign() -> None:
      ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
      cusps = whole_sign_cusps(...)
      asc = float(ascmc["asc"])
      expected_cusp_1 = np.floor(asc / 30.0) * 30.0
      assert abs(cusps[0] - expected_cusp_1) < 1e-9
  ```
- **Test registry registration** (`test_porphyry.py:163-168`) — pattern direct :
  ```python
  def test_whole_sign_registered_in_systems() -> None:
      from ketu.houses.registry import SYSTEMS, get_system
      assert "whole_sign" in SYSTEMS
      assert get_system("whole_sign") is whole_sign_cusps
      assert get_system("WHOLE_SIGN") is whole_sign_cusps
  ```
- **Test vectorized matches scalar per-element** (`test_porphyry.py:171-186`).

**Skip :**
- Les tests `polar_circle` / `is_polar` / `POLAR_EPS_TOL` (`test_porphyry.py:132-160`)
  — c'est l'API du module porphyry, pas applicable à whole_sign.
- Les tests de symétrie 180° (cusps 5/6/8/9 = opposites de 11/12/2/3) — vrai
  par construction pour Whole Sign mais redondant avec le test de spacing 30°.

**Why this analog :** test_porphyry.py est le plus court et le plus structuré
des trois (porphyry, koch, placidus), et son closed-form / pas-de-NaN-polaire
matche exactement Whole Sign.

---

## 8. `tests/houses/test_equal.py` (new)

**Closest analog :** `tests/houses/test_porphyry.py` (lignes 1-186).

**Copy : exactement comme §7 (Whole Sign).** Substituer `equal` partout.

**Adapt :**
- Test oracle : tolérance `1e-6°` (Equal est `asc + 30k`, arithmétique pure).
- Test invariant 30° spacing : identique à Whole Sign.
- Test cusp1 = ASC (PAS début du signe) :
  ```python
  def test_equal_cusp_1_equals_ascendant() -> None:
      ascmc = compute_ascmc(...)
      cusps = equal_cusps(...)
      assert abs(cusps[0] - float(ascmc["asc"])) < 1e-9
  ```
- Test cusp10 ≠ MC astronomique (la divergence Equal-vs-rest) :
  ```python
  def test_equal_cusp_10_is_asc_plus_270_not_astronomical_mc() -> None:
      ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
      cusps = equal_cusps(...)
      asc = float(ascmc["asc"])
      mc = float(ascmc["mc"])
      expected_equal_mc = (asc + 270.0) % 360.0
      assert abs(cusps[9] - expected_equal_mc) < 1e-9
      # Sanity: au moins 1° d'écart avec le MC astro à Paris J2000
      delta_to_astro_mc = abs(((cusps[9] - mc + 180) % 360) - 180)
      assert delta_to_astro_mc > 1.0, "Equal cusp 10 should diverge from MC"
  ```

**Why :** mêmes raisons qu'au §7.

---

## 9. `tests/houses/test_regiomontanus.py` (new)

**Closest analog :** `tests/houses/test_koch.py` (lignes 1-256, fichier complet).

**Pourquoi cet analogue :** Koch est le seul autre système ketu qui combine
(a) closed-form, (b) test oracle ARMC-direct bit-exact (`ALGO_TOL_DEG = 1e-6`),
(c) test snapshot end-to-end avec tolérance arcmin, (d) test polar mask NaN,
(e) test no-silent-NaN à mid-latitudes. Regiomontanus a exactement le même
profil : clos-form, sensible à eps_mean vs eps_true (cos(lat) au dénominateur
comme Koch).

**Copy (mirorage de la structure complète du fichier) :**

- Header docstring (`test_koch.py:1-19`) — copier la structure « Two-tier
  oracle strategy : algorithm tier (bit-exact) + end-to-end tier (arcmin) ».
- Imports (`test_koch.py:20-28`) — substituer `koch` par `regiomontanus`.
- Constants (`test_koch.py:30-32`) :
  ```python
  ARCMIN_DEG: float = 1.0 / 60.0
  CUSP_TOL_ARCMIN: float = 1.0 * ARCMIN_DEG
  ALGO_TOL_DEG: float = 1e-6
  ```
- `NON_POLAR_LABELS_TIGHT` / `NON_POLAR_LABELS` (`test_koch.py:36-46`).
- **Test algorithm-tier oracle ARMC-direct** (`test_koch.py:54-90`) — c'est
  LE test de référence pour Regiomontanus. Tolérance bit-exact `1e-6°`.
- **Test end-to-end snapshot** (`test_koch.py:99-128`) — pattern paramétré
  `@pytest.mark.parametrize("label", NON_POLAR_LABELS_TIGHT)` avec
  `loaded_reference_snapshot`.
- **Test inherited-precision-floor à Reykjavik** (`test_koch.py:131-167`) —
  Regio aura potentiellement aussi une dérive ~2-3 arcmin à Reykjavík à
  cause de eps_mean vs eps_true (cos(lat) au dénominateur). **Le planner DOIT
  mesurer empiriquement** la dérive max sur les 8 charts non polaires et
  pinner un `REYKJAVIK_REGIO_TOL_ARCMIN` réaliste (probablement entre 2 et 5
  arcmin). NE PAS deviner — mesurer.
- **Test invariants** (`test_koch.py:175-179`) — `MAX_ITER == 50`,
  `TOL_DEG == 1e-7` (constants gardées pour parité même si Regio est
  closed-form).
- **Test polar lat 80 yields NaN** (`test_koch.py:218-226`) — pattern direct.
- **Test no silent NaN at mid-latitudes** (`test_koch.py:229-247`) — pattern
  direct.
- **Test cusps 5/6/8/9 are opposites of 11/12/2/3** (`test_koch.py:199-215`) —
  pattern direct.
- **Test registered in systems** (`test_koch.py:250-255`).
- **Test vectorized matches scalar** (`test_koch.py:181-196`).

**Adapt :**
- Tous les `koch` / `koch_cusps` → `regiomontanus` / `regiomontanus_cusps`.
- Le commentaire « Koch's trisection (`Asc1` projection at high latitude with
  `cos(lat)` in the denominator of `sina`) amplifies this to ~2.5 arcmin »
  (`test_koch.py:140-141`) → adapter pour Regiomontanus (« Regio's projection
  at high latitude with `tan(lat)` in the formula amplifies eps drift to ~X
  arcmin » — X mesuré empiriquement).

**Skip :** rien de notable, le pattern Koch est complet pour Regio.

**Why this analog :** isomorphisme structurel parfait. Le seul fichier de
tests ketu qui couvre tous les angles dont Regiomontanus a besoin.

---

## 10. `ketu/cli/introspection.py` (modify — `_SYSTEM_DESCRIPTIONS` extend)

**Closest analog :** lui-même, lignes 22-26 (existant, dict additif).

**Action :** étendre `_SYSTEM_DESCRIPTIONS` :
```python
_SYSTEM_DESCRIPTIONS = {
    "placidus": "Time-based; iterative trisection of the diurnal/nocturnal arcs (v1.1)",
    "koch": "Birthplace-based; closed-form trisection of the oblique-ascension arc (v1.1)",
    "porphyry": "Space-based; equal trisection of the ARMC quadrants — works at all latitudes (v1.1, also the polar fallback)",
    "whole_sign": "Sign-based; cusp 1 = start of rising sign, then 30° spacing — oldest historical system (v1.2)",
    "equal": "Equal-house; cusp 1 = ASC, then 30° spacing — note cusp 10 ≠ astronomical MC (v1.2)",
    "regiomontanus": "Space-based; equal 30° divisions of the celestial equator projected through the poles (v1.2)",
}
```

**Why :** la fonction `cmd_list_house_systems()` (`introspection.py:48-57`)
itère déjà sur `sorted(_HOUSE_SYSTEMS.keys())`, donc l'ajout des 3 nouveaux
systèmes émerge automatiquement de la registry. **Aucun code change dans
`cmd_list_house_systems` lui-même.** Seul `_SYSTEM_DESCRIPTIONS` doit être
étendu pour fournir les bonnes descriptions (sinon le `(no description
available)` fallback ligne 53 est servi).

**Pattern à respecter :**
- Style descripteur cohérent : « <Catégorie>; <méthode> (<version>) ».
- Mentionner explicitement la divergence Equal cusp 10 ≠ MC (UX-relevant).
- Marquer `(v1.2)` pour distinguer des systèmes v1.1 dans le help output.

---

## 11. `tests/cli/test_introspection.py` (modify — extend assertions)

**Closest analog :** lui-même, lignes 20-31 (`TestListHouseSystems`).

**Action :** étendre la liste des noms attendus :
```python
def test_lists_registered_systems(self, invoke_main, capsys):
    rc = invoke_main(["--list-house-systems"])
    assert rc == 0
    out = capsys.readouterr().out
    for name in ("placidus", "koch", "porphyry",
                 "whole_sign", "equal", "regiomontanus"):  # NEW
        assert name in out
```

**Pas de nouveau test à créer** — le test existant ratchet la registry,
l'ajout de 3 entrées suffit.

---

## 12. Patterns transverses (cross-cutting)

### 12.1 Signature `(armc, lat, eps) -> cusps[..., 12]` — INVIOLABLE

**Source :** `ketu/houses/registry.py:30-34`, contrat `HouseSystemFn`.

**Règle Phase 15 :** les 3 nouvelles fonctions DOIVENT respecter cette
signature, **même si Whole Sign n'utilise pas `lat` ni `eps` mathématiquement
parlant**. Argument unused = OK pour mypy --strict avec `# noqa` si besoin,
mais ne PAS changer la signature ni utiliser `**kwargs`. Sinon
`calculate_houses` (qui appelle `sys_fn(armc, lat_b, eps)` ligne 141 de
`api.py`) casse silencieusement.

→ Convention pour Whole Sign : déclarer les 3 paramètres, les broadcast au
début comme dans Porphyry, mais ne les utiliser que pour calculer ASC/MC.

### 12.2 Cusps ordering canonique [asc, c2, c3, ic, c5, c6, desc, c8, c9, mc, c11, c12]

**Source :** `ketu/houses/porphyry.py:188-193`, `koch.py:168-173`,
`placidus.py:351-364`.

**Règle Phase 15 :** TOUS les `*_cusps` retournent un array shape `(..., 12)`
où l'index 0 = cusp 1 = ASC (ou son équivalent système-spécifique), index 9 =
cusp 10 = MC (ou son équivalent), etc.

**Divergences pré-établies (pas des bugs) :**
- Whole Sign : `cusps[0]` = début du signe, PAS l'ASC réel. `out["asc"]`
  préserve l'ASC réel.
- Equal : `cusps[9]` = `(asc + 270) % 360`, PAS le MC astronomique. `out["mc"]`
  préserve le MC réel.
- Regiomontanus : conventionnel (cusps[0] = ASC, cusps[9] = MC).

### 12.3 `from __future__ import annotations` — OBLIGATOIRE

**Source :** présent dans `ketu/houses/*.py` (8/8 fichiers vérifiés Phase 14).

**Règle Phase 15 :** TOUS les nouveaux fichiers `ketu/houses/*.py` ET
`tests/houses/test_*.py` commencent par `from __future__ import annotations`.

### 12.4 Anti-pattern : if/elif dispatch ladder

**Anti-pattern flag :** `ketu/houses/api.py:139-141` (« no inline if/elif
ladder anywhere — registry-based dispatch only »).

**Règle Phase 15 :** AUCUN `if system == "whole_sign": ... elif ...` nulle
part. Le dispatch est intégral via `SYSTEMS` (registry), donc l'ajout des 3
nouveaux systèmes ne touche PAS `api.py` (`calculate_houses` continue de
fonctionner sans modification — c'est tout l'intérêt du pattern HOU-02).

### 12.5 Anti-pattern : swisseph dans le runtime

**Anti-pattern catastrophique :** `import swisseph` dans `ketu/houses/*.py`.

**Ratchet test (`tests/houses/test_integration.py:214-237`) — `test_calculate_houses_no_runtime_swisseph_import`** : ce test scanne TOUS les modules `ketu.houses.*`
chargés et vérifie qu'aucun symbole `swe_*` / `swisseph` / `swe` n'est exposé.
**Ce test couvre les 3 nouveaux modules automatiquement** — pas besoin
d'ajouter de nouveau test ratchet.

→ Conséquence : `whole_sign.py`, `equal.py`, `regiomontanus.py` doivent
implémenter leurs formules en NumPy pur, **JAMAIS** appeler swisseph (même
pas pour vérifier — ça vit côté tests).

### 12.6 Tolérances oracle — barème par profil

| Profil | Tier algorithme (ARMC-direct) | Tier end-to-end (snapshot) | Pinning Reykjavik |
|--------|------------------------------|----------------------------|-------------------|
| Whole Sign | `1e-6°` (bit-exact, arithmétique) | `1e-6°` (bit-exact) | n/a (no high-lat sensitivity) |
| Equal | `1e-6°` | `1e-6°` | n/a |
| Regiomontanus | `1e-6°` | `1.0/60.0°` (1 arcmin) | mesurer empiriquement, ~2-5 arcmin |
| Placidus (rappel v1.1) | `1e-6°` | `1.0/60.0°` | ~51″ inherited eps drift |
| Koch (rappel v1.1) | `1e-6°` | `1.0/60.0°` | `3.0/60.0°` (~2.5 arcmin) |
| Porphyry (rappel v1.1) | `1e-6°` | `1.0/60.0°` | ~51″ inherited (via ASC) |

**Source :** `tests/houses/test_koch.py:30-33`, `test_placidus.py:29-30`.

**Règle Phase 15 :** Whole Sign et Equal sont purement arithmétiques (pas de
trig sur eps), donc leur tolérance end-to-end DOIT rester `1e-6°` même à
Reykjavik. Si le planner observe une dérive supérieure → bug, pas tolérance
à relâcher. Regiomontanus suit le profil Koch (eps-sensitive).

---

## 13. Récapitulatif pour le planner

| Action | Fichier | Source à imiter | Spec spécifique |
|--------|---------|-----------------|-----------------|
| Créer Whole Sign cusps | `ketu/houses/whole_sign.py` | `ketu/houses/porphyry.py:1-193` (closed-form, jamais polaire) | `cusps[0] = floor(asc/30)*30`, no `lat` dependency |
| Créer Equal cusps | `ketu/houses/equal.py` | `ketu/houses/porphyry.py:1-193` | `cusps = (asc + 30k) % 360` ; `cusps[9] ≠ MC astro` |
| Créer Regiomontanus cusps | `ketu/houses/regiomontanus.py` | `ketu/houses/koch.py:1-181` (closed-form trig + polar→NaN) | `tan(λ) = sin(H)/(cos(H)cos(eps) − sin(eps)tan(lat))` |
| Trigger registration | `ketu/houses/__init__.py:43+` | self (lignes 41-43) | append `from . import whole_sign / equal / regiomontanus` |
| Étendre oracle | `tests/houses/conftest.py:81+` | self (lignes 77-81) | ajouter `b'W'`, `b'E'`, `b'R'` à `SYSTEM_BYTES` |
| Test Whole Sign | `tests/houses/test_whole_sign.py` | `tests/houses/test_porphyry.py:1-186` | tolérance `1e-6°` end-to-end |
| Test Equal | `tests/houses/test_equal.py` | `tests/houses/test_porphyry.py:1-186` | tolérance `1e-6°` end-to-end + cusp10≠MC test |
| Test Regiomontanus | `tests/houses/test_regiomontanus.py` | `tests/houses/test_koch.py:1-256` | algo `1e-6°`, end-to-end 1 arcmin, Reykjavik mesuré |
| Régénérer snapshot JSON | `tests/houses/fixtures/reference_charts.json` | self (existant, structure inchangée) | bump `version` à `v1.2-phase15-snapshot`, ajouter 3 systèmes par chart |
| Créer regen script | `scripts/snapshot_reference_charts.py` | inexistant — dette à payer | wrapper `swe.houses_ex` sur les 10 charts × 6 systèmes |
| Étendre CLI descriptions | `ketu/cli/introspection.py:22-26` | self (existant) | ajouter 3 entrées dans `_SYSTEM_DESCRIPTIONS` |
| Étendre CLI test | `tests/cli/test_introspection.py:25` | self (lignes 20-31) | étendre la tuple de noms attendus dans `test_lists_registered_systems` |

**ZÉRO modification requise dans :**
- `ketu/houses/api.py` (`calculate_houses` est registry-driven)
- `ketu/houses/registry.py` (le mécanisme `register()` est inchangé)
- `ketu/houses/core.py` (HOUSES_DTYPE U10 system field accepte déjà
  `"whole_sign"`, `"equal"`, `"regiomontanus"` — vérifié par
  `test_dtype_string_field_capacity` qui mentionne déjà `whole_sign` ligne 43)
- `ketu/cli/parser.py` (le flag `--list-house-systems` existe déjà)
- `pyproject.toml` (pas de nouveau sous-package)

---

## 14. Risques et points d'attention pour le planner

### 14.1 Convention `cusps[0]` Whole Sign — divergence vs autres systèmes

**Problème :** dans Placidus/Koch/Porphyry/Equal/Regio, `cusps[0]` == ASC.
Pour Whole Sign, `cusps[0]` est le début du signe contenant l'ASC. Si le
planner copie aveuglément le pattern `cusps[0] = asc` de Porphyry, le test
oracle bit-exact contre swisseph (qui retourne `cusps[1] = 0.0` pour Paris
J2000 en `b'W'`) échouera.

**Mitigation :** test explicite §7
(`test_whole_sign_cusp_1_is_start_of_rising_sign`) ratchet la convention.
Documenter LOUDEMENT dans le docstring de `whole_sign_cusps`.

### 14.2 Convention `cusps[9]` Equal — divergence MC

**Problème :** `cusps[9]` Equal = `(asc + 270) % 360`, **PAS** le MC
astronomique. Mais `out["mc"]` (rempli par `calculate_houses` via
`compute_ascmc`) reste le MC astro. Donc l'utilisateur a 2 valeurs
différentes : `r["cusps"][9]` (cusp maison 10) et `r["mc"]` (MC réel).

**Mitigation :** test explicite §8
(`test_equal_cusp_10_is_asc_plus_270_not_astronomical_mc`) ratchet la
convention. Documenter dans `cmd_list_house_systems` description (« note
cusp 10 ≠ astronomical MC ») et dans le docstring d'`equal_cusps`.

### 14.3 Tolérance Reykjavik pour Regiomontanus — à mesurer

**Problème :** Reykjavik (lat 64.1°N, jd 2050) sort de la borne 1-arcmin
pour Koch (~2.5 arcmin) à cause de la dérive eps_mean vs eps_true. Regio
a la même topologie (cos(lat) au dénom). **Le planner DOIT mesurer
empiriquement** avant de pinner la tolérance, pas la deviner.

**Mitigation :** flow recommandé pour le planner :
1. Implémenter `regiomontanus_cusps`.
2. Lancer le test `test_regiomontanus_algorithm_matches_oracle_armc_*` (algo
   tier, tolérance `1e-6°`) — DOIT passer (pas eps-sensitive en algo tier).
3. Lancer le test `test_regiomontanus_cusps_match_oracle_at_arcmin` (end-to-end,
   tolérance 1 arcmin) sur 7 charts non-polar non-Reykjavik — DOIT passer.
4. Mesurer le delta max à Reykjavik. Pinner à `delta_max + 0.5 arcmin` (marge).
5. Si delta > 5 arcmin → BUG, pas tolérance. Investigate avant de pinner.

### 14.4 Polar boundary Regiomontanus — quelle formule de mask ?

**Problème :** Koch utilise `|lat| ≥ 90 - eps`. Regiomontanus a-t-il le même
boundary, ou un autre ? À vérifier dans `swehouse.c` case `'R'` : si la
formule contient `tan(lat)` directement (sans `cos(lat)` au dénom), le
boundary serait `|lat| = 90°` strict (i.e. jamais en pratique). Si elle
contient `cos(lat)` au dénom, boundary = `|lat| = 90°` aussi mais avec
dégénérescence numérique avant.

**Mitigation :** le planner DOIT lire `swehouse.c` case `'R'` pour
déterminer le boundary exact. À défaut, copier conservativement le mask
Koch (`|lat| ≥ 90 - eps`) — sera too-conservative mais safe (Porphyry
fallback sera invoqué un peu trop tôt, jamais incorrect).

### 14.5 `_SYSTEM_DESCRIPTIONS` ne valide plus — le hint Sophie

**Sophie remark :** `cmd_list_house_systems` (`introspection.py:53`) sert
`(no description available)` si une clé manque. Pas d'erreur, juste un UX
dégradé. Le test `test_mentions_polar_fallback_hint` ne vérifie que la
présence du mot « polar-fallback » ou « porphyry », pas que CHAQUE
système ait une description.

→ Recommandation Sophie : ajouter un test ratchet dans
`tests/cli/test_introspection.py` :
```python
def test_every_registered_system_has_description(self, invoke_main, capsys):
    invoke_main(["--list-house-systems"])
    out = capsys.readouterr().out
    assert "(no description available)" not in out, (
        "Every system in SYSTEMS must have a _SYSTEM_DESCRIPTIONS entry"
    )
```
**Optionnel mais cleaner** — laissé à la discrétion du planner.

---

## Métadonnées

**Scope d'analyse :** `ketu/houses/` (subpackage v1.1, gabarit complet),
`tests/houses/` (suite tests v1.1, gabarit complet), `ketu/cli/` (introspection
+ parser pour `--list-house-systems`), `pyproject.toml` (vérification packages
list, déjà OK).

**Fichiers scannés :** 8 fichiers prod (`ketu/houses/*.py`) + 11 fichiers
tests (`tests/houses/*.py` + `tests/cli/test_introspection.py`) + 2 fichiers
CLI (`introspection.py`, `parser.py`) + `pyproject.toml`.

**Vérifications empiriques effectuées :**
- `swe.houses_ex(jd, lat, lon, b'W' / b'E' / b'R')` — les 3 codes existent
  et retournent des valeurs cohérentes (`cusps[1]=0` pour W, `cusps[1]=asc`
  pour E, `cusps[2]=67.692°` pour R à Paris J2000).
- `HOUSES_DTYPE.system` est U10 et `test_dtype_string_field_capacity` ligne
  43 inclut déjà `"whole_sign"` parmi les valeurs testées — la dtype est
  prête sans modification.
- `pyproject.toml` ligne 61 contient déjà `"ketu.houses"` ; aucun nouveau
  sous-package à enregistrer.

**Date d'extraction :** 2026-05-09.

*— Sophie Chen, Lead Technical Architect*
