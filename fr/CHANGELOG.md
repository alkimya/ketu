# Journal des modifications (version française)

> **Note :** Ce fichier est une traduction synthétisée du fichier
> [`../CHANGELOG.md`](../CHANGELOG.md) anglais, qui fait foi.
> Il n'est pas maintenu en parallèle : il est régénéré à chaque
> publication de version en même temps que la version anglaise.
> En cas de divergence, la version anglaise est la référence
> authoritative.

---

## [1.3.0] - 2026-06-01

### Ajouts

- **Chiron en tant que 14e corps (body_id=13)** — évaluateur polynomial de
  Chebyshev embarqué (pur NumPy, zéro pyswisseph à l'exécution).
  `calc_planet_position(jd, 13)` et `calc_planet_position_batch(jds, 13)`
  résolvent la longitude de Chiron depuis `ketu/data/chiron_coeffs.npz`
  (289,7 Ko, Chebyshev seg=32j/deg=10). Max |Δλ| = 0,005695° sur
  1950–2050. Accessible via tous les chemins de calcul standard
  (`ketu.calculations`, `ketu.charts.compute_chart`, `ketu.synastry`, etc.).
  L'axe des corps du `CHART_DTYPE` est étendu : 13 corps → 14 corps
  (body_lons[14], body_speeds[14], aspects[14×14]). (Phase 24 / D-08)

- **`aspects_for_harmonics(harmonics)`** — compose un ensemble d'aspects
  à partir d'une liste d'harmoniques (ex. `[1, 2, 3, 6]`) et retourne un
  masque `numpy.bool_` figé de longueur 14. Harmoniques valides :
  `{1, 2, 3, 5, 6, 9, 10}` (données issues de `core.aspects`). Lève
  `ValueError` en cas d'entrée inconnue ou non entière.

- **Colonnes `harmonic` et `symbol` sur `core.aspects`** — `core.aspects`
  est maintenant un tableau structuré à 5 champs `(name, angle, coef,
  harmonic, symbol)`. La colonne `harmonic` porte la base harmonique entière
  de chaque aspect (ex. Sextile=3, Semi-sextile=6) ; `symbol` porte le
  glyphe Unicode des 7 aspects demi-cercle (☌ ⚺ ⚹ □ △ ⚻ ☍) ; les 7 aspects
  mineurs plein-cercle ont un symbole vide. Le champ `coef` est inchangé.

### Modifié

- **RUPTURE (contrat positionnel Kala / en aval) :** les tableaux du
  `CHART_DTYPE` sont étendus de la forme (13,) → (14,) et les aspects de
  (13,13) → (14,14). L'index positionnel 13 est Chiron. Tout code ayant
  codé en dur le nombre de corps à 13 ou adressant les tableaux de corps
  par index numérique fixe au-delà de 12 doit être mis à jour. Les tableaux
  `CHART_DTYPE` mis en cache avec v1.2 sont incompatibles — recalculer avec
  v1.3. L'axe des corps synastry passe de 15 à 16 (Soleil..Chiron + ASC +
  MC). Voir `UPGRADING.md → v1.2 -> v1.3`. (Phase 24 / D-08)

- **RUPTURE : ensemble d'aspects par défaut de l'API Python modifié de
  5 (CLASSICAL) à 7 (TRADITIONAL — les aspects demi-cercle).** L'appel à
  `calculate_aspects`, `compute_chart` ou toute fonction acceptant
  `aspects=None` produit désormais les **7 aspects demi-cercle**
  (harmoniques 1, 2, 3, 6) : Conjonction, Semi-sextile, Sextile, Carré,
  Trigone, Quinconce, Opposition. Auparavant, le défaut était les 5 aspects
  CLASSICAL majeurs. Les harmoniques mineurs plein-cercle (H5/H9/H10) restent
  opt-in. **Note CLI :** le défaut CLI `ketu ... --harmonics` reste
  **classical (5 aspects)** pour la compatibilité ascendante.
  Voir `UPGRADING.md → v1.2 -> v1.3`.

- **RUPTURE (convention de données interne).** `CYCLE_DTYPE.angular_separation`
  (et donc `cycle_progress` et `cycle_phase`) depuis
  `generate_cycle_series` / `generate_multi_cycle_series` suit désormais
  la direction documentée body1 → body2 : `(body2_lon - body1_lon) % 360`.
  Précédemment inversé. Les consommateurs en aval (ex. Kala) doivent
  ajuster : les valeurs sont maintenant `360 - ancien` de la conjonction
  sauf à 0°/180°.

### Corrigé

- `generate_cycle_series` accepte désormais un ndarray `numpy.datetime64`
  sur le chemin cache (`use_cache=True`) ; précédemment levait
  `AttributeError` car la recherche dans le cache lisait les attributs
  `.year`/`.month` que datetime64 n'expose pas.

---

## [1.2.0] - 2026-05-28

### Ajouts

- **Gates de qualité de la documentation CI** — `interrogate ≥95%`
  (bloquant) et `numpydoc validate` (bloquant depuis v1.2.0) sont
  désormais câblés dans `tests.yml`. `make doc-gates` lance la suite
  complète en local. (OPS-01, OPS-02)
- **Trois nouveaux systèmes de maisons** — Maisons Entières
  (`"whole_sign"`), Maisons Égales (`"equal"`) et Régiomontanus
  (`"regiomontanus"`) enregistrés dans `ketu.houses.SYSTEMS` via le
  décorateur `@register`. Accessibles via
  `calculate_houses(..., system=...)`, le CLI
  `ketu houses --system`, et `ketu --list-house-systems`. Le CLI
  retourne désormais six entrées :
  `equal, koch, placidus, porphyry, regiomontanus, whole_sign`.
  (HOU2-01..05 / Phase 15)
- **Sous-package `ketu.synastry`** — `calculate_synastry(chart_a,
  chart_b)` retourne un tableau structuré `SYNASTRY_DTYPE` (8 champs,
  produit croisé de 15 corps dont ASC/MC ; paires avec soi-même
  incluses). Mode `"filtered"` (défaut) et `"dense"` partagent le
  même schéma. Orbes synastry : facteur 0,5 (convention Astrodienst).
  Sous-commande CLI `ketu synastry`. Flag `ketu --list-orbs`.
  (SYN-01..05 / Phase 16)
- **Sous-package `ketu.composite`** — `calculate_composite(chart_a,
  chart_b, system="placidus") -> CHART_DTYPE` dérive un thème
  composite par la méthode des points médians. Helper
  `circular_midpoint(lon_a, lon_b)` vectorisable (ratchet pinné :
  `mid(359°, 1°) == 0°`). Maisons composites calculées depuis
  l'ASC composite + le MC composite via trisection Porphyre.
  Trois fixtures oracle auto-consistantes. (COMP-01..05 / Phase 17)
- **Sous-package `ketu.returns`** — retour solaire et retour lunaire
  avec support de la relocalisation.
  - `solar_return(natal_jd, natal_lat, natal_lon, target_year,
    return_lat=None, return_lon=None, system="placidus") -> CHART_DTYPE`
    — thème de retour solaire pour une année cible ;
    convergence à la seconde d'arc. (RET-01..06 / Phase 18)
  - `lunar_return(natal_jd, natal_lat, natal_lon, target_jd,
    return_lat=None, return_lon=None, system="placidus") -> CHART_DTYPE`
    — PREMIER retour lunaire >= `target_jd` (~27,32 j de période) ;
    convergence à la seconde d'arc. (LRET-01..05 / Phase 18)
  - **Asymétrie d'API :** `solar_return` prend un `target_year`
    entier ; `lunar_return` prend un `target_jd` en Jour Julien.
  - Racine commune pure-NumPy `_solve_return` partagée par les deux
    fonctions.
- **Sous-package `ketu.parts`** — framework extensible des Parts
  Arabes (analogue de `ketu.houses.SYSTEMS`).
  - `calculate_part(part_name, chart) -> float` — dispatch sect-aware
    via `is_day_chart`.
  - `calculate_all_parts(chart, parts=None) -> dict[str, float]` —
    retourne tous les parts du registre (ou un sous-ensemble nommé) ;
    ordre alphabétique déterministe.
  - Trois Parts intégrées : Fortune (sect-aware — `ASC + Lune − Soleil`
    jour / `ASC + Soleil − Lune` nuit), Esprit (miroir sect-aware de
    Fortune), Mariage (fixe, sect-invariant —
    `ASC + Descendant − Vénus`).
  - Flag CLI `ketu --list-parts` — liste tous les parts enregistrés
    avec la description de la formule et l'annotation de
    sect-awareness.
  - `make parts-coverage` : gate de couverture ≥95% sur
    `ketu/parts/` (mesuré à 100%). (PARTS-01..08 / Phase 19)

### Modifications

- `ketu.houses.HOUSES_DTYPE['system']` : largeur étendue de `U10` à
  `U16` pour accommoder `"regiomontanus"` (13 caractères) sans
  troncature. **Non-rompant** : la conversion NumPy U10⇄U16 est
  transparente à l'assignation. (Phase 15 / HOU2-05)

### Infrastructure

- **Rafraîchissement des workflows GitHub Actions** — `actions/checkout@v5`,
  `actions/setup-python@v6`, `actions/upload-artifact@v5` /
  `actions/download-artifact@v5` mis à jour vers les actions basées
  sur Node.js 24 ; tous les avertissements Node 20 supprimés des
  fichiers `tests.yml` et `publish.yml`. (OPS-03 / Phase 20)
- **Gate `numpydoc validate` désormais bloquant** — le gate CI
  (auparavant simple avertissement) est pleinement bloquant depuis
  v1.2.0 ; `make doc-gates` sort avec code non-nul à la moindre
  violation ; 214 violations GL01 préexistantes corrigées dans
  44 fichiers. (OPS-02 / Phase 20)

---

## [1.1.0] - 2026-05-08

Voir [CHANGELOG.md](../CHANGELOG.md#110---2026-05-08) pour la liste
complète des modifications de la version 1.1.0 (en anglais, version
de référence).

---

## [1.0.0] - 2026-02-12

Voir [CHANGELOG.md](../CHANGELOG.md#100---2026-02-12) pour la liste
complète des modifications de la version 1.0.0 (en anglais, version
de référence).

---

## Convention de versionnage

- **MAJEUR** : changements d'API incompatibles
- **MINEUR** : ajouts rétrocompatibles
- **CORRECTIF** : correctifs rétrocompatibles
