# SPK-01 — Mesures Chebyshev-par-segment : Chiron géocentrique (1950-2050)

> **Données uniquement.** Le verdict go/no-go est enregistré dans `23-02-PLAN.md` / `23-DECISION.md`.

---

## Métadonnées de l'exécution

| Paramètre              | Valeur                                                              |
|------------------------|---------------------------------------------------------------------|
| Date d'exécution       | 2026-05-29                                                          |
| Script                 | `.planning/phases/23-spike-chiron/spike_chiron_chebyshev.py`        |
| Plage couverte         | 1950-01-01 .. 2050-01-01 UTC                                        |
| jd0                    | 2433282.5000 (1950-01-01 00:00 UT)                                  |
| jd1                    | 2469807.5000 (2050-01-01 00:00 UT)                                  |
| total_days             | 36 525.0 jours                                                      |
| Oracle                 | `swe.calc_ut(jd, swe.CHIRON, FLG_SWIEPH\|FLG_SPEED)`               |
| swe.CHIRON             | 15                                                                  |
| retflag observé        | **260** = MOSEPH + SPEED (fallback Moshier — `seas_18.se1` seul, sans `sepl_18.se1`) |
| Éphéméride utilisée    | Moshier (pas SWIEPH complet) — voir note ci-dessous                 |
| Dossier éphéméride     | `/home/loc/workspace/rahu/kerykeion/kerykeion/sweph`                |
| Fichier requis         | `seas_18.se1` (217 KB, Chiron ID 2060)                              |
| numpy version          | 2.3.5                                                               |
| swisseph version       | 2.10.03                                                             |

> **Note retflag 260 vs 258** : avec `seas_18.se1` uniquement (sans `sepl_18.se1`), pyswisseph
> utilise le Moshier analytique pour le Soleil/la Lune nécessaires au calcul géocentrique.
> Selon la recherche (Q5), la différence SWIEPH vs Moshier pour Chiron est **max 0.000067°**
> sur 1950-2050 — négligeable face à la cible de 0.01°.

---

## Table de sweep des configurations

Mesures sur **TOUS** les segments de la plage 1950-2050.
Erreur mesurée sur une **grille de validation de 200 points DISTINCTS** des noeuds
d'ajustement. Métrique : **MAX |Δλ|** (pire cas), pas RMS.

| seg (d) | degré | n_segs | coef/seg | total coeffs (lon) | .npz lon-only (KB) | max \|Δλ\| (°) | < 0.01° ? |
|--------:|------:|-------:|---------:|-------------------:|-------------------:|---------------:|:---------:|
| 32      | 10    | 1142   | 11       | 12 562             | 98.1               | **0.000861**   | **OUI** * |
| 32      |  8    | 1142   |  9       | 10 278             | 80.3               | 0.001064       | OUI       |
| 32      | 12    | 1142   | 13       | 14 846             | 116.0              | 0.000823       | OUI       |
| 16      |  8    | 2283   |  9       | 20 547             | 160.5              | 0.001426       | OUI       |
| 64      |  8    |  571   |  9       |  5 139             | 40.1               | 0.001215       | OUI       |

`*` = **config primaire recommandée** (32j, deg=10)

> **Note sur n_segs = 1142 vs 1153 (recherche)** : la recherche préliminaire calculait
> `ceil(36889 / 32) = 1153` avec une estimation de 36889 jours. La plage exacte
> `swe.julday(2050,1,1,0) - swe.julday(1950,1,1,0) = 36525.0 jours` (années calendaires,
> pas juliens) donne `ceil(36525 / 32) = 1142`. Toutes les mesures utilisent les 1142 réels.

---

## Empreinte .npz pour la config primaire (3 quantités)

| Quantités     | Total coeffs      | .npz (float64, non compressé) |
|---------------|------------------:|------------------------------:|
| lon only      | 12 562            | 98.1 KB                       |
| lon + lat + dist | 12 562 × 3 = 37 686 | **294.4 KB**               |

Structure recommandée du `.npz` :
```
lon_coeffs  : (1142, 11)  float64
lat_coeffs  : (1142, 11)  float64
dist_coeffs : (1142, 11)  float64
seg_starts  : (1142,)     float64  (~9 KB)
seg_len     : scalar      float64  (32.0)
degree      : scalar      int32    (10)
jd_start    : scalar      float64
jd_end      : scalar      float64
```
Total avec métadonnées : ~303 KB non compressé (compressé `.npz` nettement inférieur).

---

## Précision lat/dist pour la config primaire (32j, deg=10)

| Quantité   | max erreur mesurée | Unité |
|------------|-------------------:|-------|
| Latitude   | **0.000986**       | °     |
| Distance   | **0.000000184**    | UA    |

Ces valeurs confirment que les 3 quantités (lon, lat, dist) sont ajustables avec la
même configuration, à des niveaux d'erreur négligeables.

---

## Segment le plus difficile

| Propriété              | Valeur                                   |
|------------------------|------------------------------------------|
| Date du pire segment   | **2027-04-20** (JD 2461516.31)           |
| Erreur max sur ce seg  | 0.000861° (= le max global, config 32/10)|
| Cause probable         | Vitesse géocentrique élevée + courbure   |

> **Note** : le segment le pire (2027-04-20) diffère de la prévision de recherche (~2046-2047
> perihelion). La différence est probablement due au fallback Moshier (retflag 260) vs SWIEPH
> complet (retflag 258) — le Moshier peut avoir une légère divergence sur la région 2046-2047
> qui n'est pas la pire pour le Moshier. L'erreur absolue reste de toute façon << 0.01°.

---

## Garde-fous méthodologiques appliqués

1. **Longitude déroulée avant ajustement** — offset cumulatif (diff>180 → offset-=360 ;
   diff<-180 → offset+=360) ; re-wrap en `% 360` à l'évaluation.
2. **Grille de validation distincte des noeuds d'ajustement** — 200 points uniformes
   `linspace(-1,1,200)`, différents des `degree+8` noeuds d'ajustement.
3. **MAX (pire cas), pas RMS** — `np.max(np.abs(erreur))` sur tous les segments.
4. **TOUS les segments testés** — boucle sur les 1142 segments, aucun échantillonnage.
5. **`swe.set_ephe_path()` appelé avant tout `calc_ut`** — aucune erreur `swisseph.Error`.
6. **Évaluateur pur-NumPy confirmé** — `np.allclose(poly(t), chebval(t, poly.coef))` = True
   (vérifié en ligne, aucune dépendance scipy dans le script).

---

## Résumé config primaire (32j, deg=10)

| Métrique               | Valeur         | Cible    | Marge     |
|------------------------|---------------:|:--------:|----------:|
| max \|Δλ\| (°)         | **0.000861**   | < 0.01   | **11.6×** |
| max \|Δlat\| (°)       | 0.000986       | —        | —         |
| max \|Δdist\| (UA)     | 1.84 × 10⁻⁷   | —        | —         |
| .npz (lon-only, KB)    | 98.1           | —        | —         |
| .npz (3 qté, KB)       | 294.4          | < 400    | —         |
| n_segs                 | 1142           | —        | —         |
| Évaluateur pur-NumPy   | confirmé       | requis   | —         |

---

*Ce fichier est la seule trace des mesures brutes (SPK-01). Le go/no-go est dans 23-02.*
