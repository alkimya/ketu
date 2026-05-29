# SPK-02 — Décision go/no-go : Chiron par Chebyshev-par-segment

**Rédigé par** : Sophie Chen (Lead Technical Architect)
**Date** : 2026-05-29
**Consomme** : `23-MEASUREMENTS.md` (SPK-01, mesures empiriques)
**Pour** : Phase 24 — Chiron

---

## VERDICT

> # GO

Le spike confirme sans ambiguïté la viabilité technique de l'approche Chebyshev-par-segment
pour Chiron géocentrique 1950-2050. La configuration primaire `seg=32j, deg=10` atteint
**max|Δλ|=0.000861°**, soit **11.6× sous la cible de 0.01°**. La Phase 24 peut démarrer.

---

## 1. Paramètres Phase 24 — Configuration verrouillée

| Paramètre          | Valeur choisie                            | Justification                             |
|--------------------|-----------------------------------------|------------------------------------------|
| Longueur de segment | **32 jours**                            | Sweet spot : compact + précis            |
| Degré polynomial   | **10**                                  | 11 coefficients/seg, marge 11.6×         |
| Quantités ajustées | **3** : lon, lat, dist                  | Complet pour le vecteur position          |
| Vitesses           | **Différence finie** `jd_delta=0.01`    | Pattern existant `_make_planet_scalar`    |
| n_segments         | **1142** (plage 36 525 j = jd0..jd1)   | `ceil(36525/32)`, calculé par `swe.julday` |
| Total coefficients | **37 686** (1142 × 11 × 3)              | lon + lat + dist                         |
| Empreinte .npz     | **~294 KB** non compressé               | Bien sous la limite opérationnelle        |

**Remarque n_segs** : la recherche estimait 1153 segs (36 889 j); la plage exacte
`swe.julday(2050,1,1) − swe.julday(1950,1,1) = 36 525 j` (années calendaires, pas
juliens) donne `ceil(36525/32) = 1142`. Toutes les mesures utilisent ce chiffre réel.

---

## 2. Précision atteinte

### 2.1 Tableau de comparaison — config primaire vs cible

| Métrique               | Valeur mesurée       | Cible    | Résultat          |
|------------------------|---------------------:|:--------:|:-----------------:|
| max \|Δλ\| (°)        | **0.000861**         | < 0.01°  | **ATTEINT**       |
| Ratio / cible          | **0.0861** (11.6×)   | < 1.0    | **ATTEINT**       |
| max \|Δlat\| (°)      | 0.000986             | —        | acceptable        |
| max \|Δdist\| (AU)     | 1.84 × 10⁻⁷         | —        | acceptable        |

**La contrainte < 0.01° est ATTEINTE sur l'intégralité de la plage 1950-2050.**

### 2.2 Segment le plus difficile

| Propriété              | Valeur                                   |
|------------------------|------------------------------------------|
| Date du pire segment   | **2027-04-20** (JD 2461516.31)           |
| Erreur max sur ce seg  | **0.000861°** (= le max global)          |
| Cause probable         | Vitesse géocentrique élevée + courbure locale |

Note : le pire segment attendu en recherche était la zone périhélie 2046-2047. L'écart
est attribué au fallback Moshier (retflag 260) — légère divergence dans la zone 2046-2047
qui n'est pas la pire pour Moshier. L'erreur absolue reste << 0.01° dans les deux cas.

### 2.3 Table de sweep complète (toutes configs testées)

| seg (j) | degré | n_segs | coef/seg | .npz lon-only (KB) | max \|Δλ\| (°) | < 0.01° |
|--------:|------:|-------:|---------:|-------------------:|---------------:|:-------:|
| 32      | 10    | 1142   | 11       | 98.1               | **0.000861**   | OUI *   |
| 32      |  8    | 1142   |  9       | 80.3               | 0.001064       | OUI     |
| 32      | 12    | 1142   | 13       | 116.0              | 0.000823       | OUI     |
| 16      |  8    | 2283   |  9       | 160.5              | 0.001426       | OUI     |
| 64      |  8    |  571   |  9       | 40.1               | 0.001215       | OUI     |

`*` = **config primaire retenue**

---

## 3. Provenance oracle et éphéméride

### 3.1 Appel oracle exact

```python
import swisseph as swe

swe.set_ephe_path('/chemin/vers/dossier_contenant_seas_18.se1')

result = swe.calc_ut(jd, swe.CHIRON, swe.FLG_SWIEPH | swe.FLG_SPEED)
xx     = result[0]   # 6-uplet
lon, lat, dist             = xx[0], xx[1], xx[2]
lon_speed, lat_speed, dist_speed = xx[3], xx[4], xx[5]
# retflag = result[1]  →  260 observé (MOSEPH + SPEED)
# errmsg  = result[2]
```

`swe.CHIRON = 15` — confirmé dans le venv ketu.

### 3.2 retflag observé vs attendu

| retflag | Signification                  | Observé dans le spike |
|---------|-------------------------------|----------------------|
| 258     | SWIEPH + SPEED                 | Non (sepl_18.se1 absent) |
| **260** | **MOSEPH + SPEED**             | **Oui** (seas_18.se1 seul) |

Avec `seas_18.se1` uniquement (sans `sepl_18.se1`), pyswisseph utilise le Moshier
analytique pour le Soleil/la Lune nécessaires au calcul géocentrique.
Différence max SWIEPH vs Moshier : **≤ 0.000067°** sur 1950-2050 (source : Q5 recherche).
Négligeable face à la cible 0.01°. Les coefficients produits avec Moshier sont acceptables.

### 3.3 Exigence de configuration éphéméride (Phase 24)

**`seas_18.se1` DOIT être présent dans le répertoire `set_ephe_path()`.**

Sans ce fichier, `swe.calc_ut(jd, swe.CHIRON, ...)` lève `swisseph.Error`.
Il n'existe pas de chemin Moshier pur pour Chiron — même `FLG_MOSEPH` exige `seas_18.se1`.

Localisation dans le spike : `/home/loc/workspace/rahu/kerykeion/kerykeion/sweph/seas_18.se1`
Taille : **217 KB** (fichier de données astéroïdes, contient Chiron ID 2060).

**Options CI pour Phase 24 (décision différée à Phase 24)** :
1. Bundler `seas_18.se1` comme fixture de test (répertoire `tests/res/`).
2. Pattern `pytest.importorskip("swisseph")` + skip conditionnel si le fichier est absent.
3. Ajouter `seas_18.se1` dans `res/` du dépôt (identique à la distribution kerykeion).

Phase 23 ne décide pas de l'approche CI — c'est la responsabilité de Phase 24.

---

## 4. Layout .npz pour Phase 24

Structure des tableaux, formes et dtypes :

```python
np.savez_compressed(
    'ketu/data/chiron_coeffs.npz',
    lon_coeffs  = np.zeros((1142, 11), dtype=np.float64),  # shape (1142, 11)
    lat_coeffs  = np.zeros((1142, 11), dtype=np.float64),  # shape (1142, 11)
    dist_coeffs = np.zeros((1142, 11), dtype=np.float64),  # shape (1142, 11)
    seg_starts  = jd_starts,                                # shape (1142,)  f64
    seg_len     = np.float64(32.0),                         # scalar f64
    degree      = np.int32(10),                             # scalar i32
    jd_start    = np.float64(2433282.5),                    # scalar f64  (1950-01-01)
    jd_end      = np.float64(2469807.5),                    # scalar f64  (2050-01-01)
)
```

| Tableau      | Forme        | Dtype   | Taille (non compressé) |
|--------------|:------------:|:-------:|----------------------:|
| lon_coeffs   | (1142, 11)   | float64 | 98.1 KB               |
| lat_coeffs   | (1142, 11)   | float64 | 98.1 KB               |
| dist_coeffs  | (1142, 11)   | float64 | 98.1 KB               |
| seg_starts   | (1142,)      | float64 | 8.9 KB                |
| seg_len      | scalaire     | float64 | < 1 KB                |
| degree       | scalaire     | int32   | < 1 KB                |
| jd_start     | scalaire     | float64 | < 1 KB                |
| jd_end       | scalaire     | float64 | < 1 KB                |
| **TOTAL**    |              |         | **~303 KB**           |

Le `.npz` compressé (`savez_compressed`) sera nettement inférieur à 303 KB.

---

## 5. Évaluateur runtime (confirmé, NON livré cette phase)

L'évaluateur runtime est **pur NumPy, zéro scipy** :

```python
import numpy as np

def eval_chiron(jd: float, data: dict) -> tuple[float, float, float,
                                                  float, float, float]:
    """Retourne (lon, lat, dist, lon_speed, lat_speed, dist_speed)."""
    seg_starts = data['seg_starts']
    seg_len    = float(data['seg_len'])
    jd_delta   = 0.01  # pattern _make_planet_scalar existant

    def _eval_qty(jd_: float, coeffs: np.ndarray) -> float:
        si = int((jd_ - seg_starts[0]) / seg_len)
        si = max(0, min(si, len(seg_starts) - 1))
        t  = 2.0 * (jd_ - seg_starts[si]) / seg_len - 1.0
        t  = float(np.clip(t, -1.0, 1.0))
        return float(np.polynomial.chebyshev.chebval(t, coeffs[si]))

    lon  = _eval_qty(jd, data['lon_coeffs']) % 360.0
    lat  = _eval_qty(jd, data['lat_coeffs'])
    dist = _eval_qty(jd, data['dist_coeffs'])

    # Vitesses par différence finie (même pattern que _make_planet_scalar)
    lon1  = _eval_qty(jd + jd_delta, data['lon_coeffs']) % 360.0
    lat1  = _eval_qty(jd + jd_delta, data['lat_coeffs'])
    dist1 = _eval_qty(jd + jd_delta, data['dist_coeffs'])
    # Correction wrap 360° pour la vitesse de longitude
    dlon  = lon1 - lon
    if dlon > 180.0:  dlon -= 360.0
    if dlon < -180.0: dlon += 360.0
    lon_speed  = dlon / jd_delta
    lat_speed  = (lat1 - lat) / jd_delta
    dist_speed = (dist1 - dist) / jd_delta

    return lon, lat, dist, lon_speed, lat_speed, dist_speed
```

Points confirmés par le spike :
- `np.polynomial.chebyshev.chebval(t, coef)` matche exactement `Chebyshev(t)` : `np.allclose = True`.
- Performance : ~5 µs scalaire, ~94 µs pour 1000 points en batch.
- Normalisation : `t = 2*(jd − jd_s)/seg_len − 1` mappe `[jd_s, jd_s+seg_len]` → `[-1,1]`.
  Les coefficients de `Chebyshev.fit(..., domain=[-1,1])` sont déjà dans le domaine standard.
- Longitude déroulée avant ajustement, re-wrap `% 360` à l'évaluation.

---

## 6. Points d'insertion Phase 24 (référence — non modifiés ici)

Phase 24 modifiera les éléments suivants dans `ketu/ephemeris/planets.py` :

### 6.1 BODY_INDICES (~L35-49)
```python
# Ajouter :
BODY_INDICES["Chiron"] = 13
```

### 6.2 SWE_IDS (~L52-66)
```python
# Ajouter :
SWE_IDS[13] = "Chiron"
```

### 6.3 BODY_STRATEGIES (~L310-324)
```python
# Ajouter :
BODY_STRATEGIES["Chiron"] = _BodyCalc(_chiron_scalar, _chiron_vec)
```

### 6.4 calc_planet_position — plage valide
La plage valide passe de **0-12** à **0-13** après l'ajout de Chiron.

### 6.5 Ratchet 13→14 corps (rupture contrôlée)

Phase 24 met à jour les assertions corps-count suivantes :
- `tests/test_ketu.py:110` — `test_body_count_frozen_at_thirteen` → rebaptiser + passer à 14.
- Assertions synastry / transits / charts corps-count — audit complet en Phase 24.
- Note dans UPGRADING.md (Phase 26) : contrat positionnel interne `Ketu↔Kala` change de 13 à 14 corps.

**Aucun de ces fichiers n'a été modifié par les phases 23-01 ou 23-02.**

---

## 7. Garde-fous de périmètre (SPK-02)

Ce spike (Phases 23-01 + 23-02) livre **données + décision uniquement** :

| Garde-fou                              | Statut                          |
|----------------------------------------|---------------------------------|
| Aucun code de production sous `ketu/`  | **RESPECTÉ** — zéro fichier ketu modifié |
| Aucun nouveau test enregistré par pytest | **RESPECTÉ** — `spike_chiron_chebyshev.py` hors de `tests/` et hors de `ketu/` |
| Suite de tests inchangée (1 351 tests) | **RESPECTÉ** — suite entièrement verte |
| Gate de couverture 100% inchangé       | **RESPECTÉ** — aucune ligne ketu touchée |
| Aucune dépendance runtime ajoutée      | **RESPECTÉ** — pyswisseph reste en `[test]` optional uniquement |
| pyproject.toml non modifié             | **RESPECTÉ** — zéro changement |

Vérification rapide :
```bash
git status --porcelain ketu tests pyproject.toml
# Attendu : sortie vide
```

---

## Prochaine étape

Phase 24 — Chiron : intégration des coefficients Chebyshev dans `ketu/` avec l'évaluateur
pur-NumPy, mise à jour des 6 points d'insertion (`BODY_INDICES`, `SWE_IDS`,
`BODY_STRATEGIES`, `calc_planet_position`, `core.py` bodies, `orbital.py`), ratchet
13→14, et tests de régression de précision couvrant la plage 1950-2050.

---

*Source des mesures : `.planning/phases/23-spike-chiron/23-MEASUREMENTS.md` (SPK-01)*
*Décision rédigée par Sophie Chen — Phase 23 Plan 02 — 2026-05-29*
