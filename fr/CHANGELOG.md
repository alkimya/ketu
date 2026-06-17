# Journal des modifications (version française)

> **Note :** Ce fichier est une traduction synthétisée du fichier
> [`../CHANGELOG.md`](../CHANGELOG.md) anglais, qui fait foi.
> Il n'est pas maintenu en parallèle : il est régénéré à chaque
> publication de version en même temps que la version anglaise.
> En cas de divergence, la version anglaise est la référence
> authoritative.

---

## [1.8.0] - 2026-06-17

### Ajouts

- **Champ `body_decl_speed` dans `CHART_DTYPE`** (`float64[14]`, index 8) :
  vitesse de déclinaison équatoriale dδ/dt en degrés/jour pour les 14 corps.
  Positif = vers le nord (montante), négatif = vers le sud (descendante).
  Calculé par différence finie vers l'avant à Δt = 0,01 jour (l'idiome FD
  global du paquet). Rempli automatiquement par `compute_chart` et
  `calculate_composite`. (Phase 40 — DSPD-01, DSPD-02, DSPD-03)

- **`DECL_STANDSTILL_EPS = 0.001` (°/jour)** : constante publique exportée
  depuis `ketu.calculations`. Définit le seuil en dessous duquel la vitesse
  de déclinaison d'un corps est classifiée comme station (|dδ/dt| ≤ EPS →
  neutre). Ketu définit cette frontière ; les consommateurs en aval la lisent
  directement. (DSPD-05)

- **`is_ascending_declination_chart(chart)` — auxiliaire de niveau thème** :
  retourne `int8` `{+1, 0, −1}` par corps (forme `(14,)` pour les thèmes
  scalaires, `(S, 14)` pour les lots). `+1` = montante (dδ/dt > EPS),
  `−1` = descendante (dδ/dt < −EPS), `0` = station (|dδ/dt| ≤ EPS).
  **Distinct du scalaire v1.5 `is_ascending_declination(jdate, body)` (bool,
  pas de seuil EPS).** (DSPD-06)

### Notes

- **Version MINEURE, pas un correctif** : la disposition octets de `CHART_DTYPE`
  s'agrandit (16 champs, était 15 — `body_decl_speed` ajouté à l'index 8).
  L'accès par nom de champ (`chart["body_lons"]`) n'est pas affecté. L'accès
  positionnel ou `.view()` sur `CHART_DTYPE` doit s'adapter. Voir
  [UPGRADING.md](../UPGRADING.md) → « v1.7 -> v1.8 ».

## [1.7.0] - 2026-06-15

### Modifications

- **Orbe de longitude Rahu / Ketu / Lilith : 0° → 2°** (`core.bodies`, source unique).
  Tous les consommateurs (`get_orb`, `calculate_aspects*`, synastrie, composite, CLI)
  héritent du changement sans aucune modification supplémentaire. Seuil de conjonction
  point à point : 2° ; moyenne point à planète : ex. Rahu-Soleil donne (2+12)/2 = 7°.
  Chiron (orbe = 4°) et toutes les autres planètes restent inchangés. (Phase 38 — ORB-01)
- **Opposition tautologique Rahu-Ketu supprimée** (`aspects/calculator.py`
  `_is_tautologique_node_opposition`) : le moteur supprime silencieusement
  l'Opposition Nœud Nord / Nœud Sud (toujours présente par définition, sans
  information astrologique). Tous les autres aspects de Rahu/Ketu restent
  détectés normalement. (Phase 38 — ORB-02)

### Notes

- **RUPTURE DE RÉSULTATS — version mineure, et non un correctif** : les résultats
  de détection d'aspects changent pour tous les consommateurs. Les aspects de
  nœuds/Lilith auparavant invisibles (orbe 0 → dans la limite des 2°) apparaissent
  désormais. Il s'agit d'un changement de comportement délibéré et contrôlé, livré
  en tant que version MINEURE selon le Versionnage Sémantique. Les consommateurs en aval
  (tout oracle/instantané qui énumère les aspects des nœuds ou de Lilith) **doivent
  traiter la mise à jour comme délibérée** — ne pas effectuer `pip install -U`
  comme un correctif neutre.
- **`CHART_DTYPE` et `core.aspects` sont octet-identiques** : aucune rupture du
  ratchet de dtype. Seuls les résultats de détection changent. (Phase 38)

## [1.6.0] - 2026-06-04

### Ajouts

- **Sous-paquet `ketu.declination` — aspects de déclinaison (parallèles &
  contre-parallèles)** : un NOUVEAU sous-paquet additif détectant les aspects
  parallèles (`P`) et contre-parallèles (`CP`) sur l'axe de déclinaison
  équatoriale (δ), indépendant de la longitude écliptique. (Phase 36)
- **`find_declination_aspects(body_decl)`** : détecteur scalaire/graphe unique.
  Prend le tableau signé-δ `chart["body_decl"]` de forme `(14,)` ; retourne un
  tableau structuré `DECLA_ASPECT_DTYPE` (paires triangle supérieur, triées,
  dédupliquées) ; `np.empty(0, …)` quand aucun aspect détecté (jamais `None`).
- **`declination_aspect_masks(body_decl)`** : chemin vectorisé en lot. Accepte
  `(S, 14)` ou `(14,)` (promu via `np.atleast_2d`) ; retourne un NamedTuple
  `DeclinationAspectMasks` de masques `(S, 91)` + vecteurs index/orbe `(91,)`.
  Diffusion pure, aucune boucle Python sur les corps.
- **NamedTuple `DeclinationAspectMasks`** (6 champs : `parallel`, `contra`,
  `gap`, `idx_i`, `idx_j`, `orb_pairs`).
- **`DECLA_ASPECT_DTYPE`** (5 champs : `body1`, `body2`, `kind` ∈ {"P","CP"},
  `gap`, `orb`).
- **`DECLA_COEF = 1/12` et `MIN_DECL_ORB = 0,5°`** : la formule d'orbe dérivée
  des corps `max((orb_b1 + orb_b2)/2 × DECLA_COEF, MIN_DECL_ORB)` → Soleil/Lune
  = 1,0°, corps à orbe zéro (Rahu/Ketu/Lilith) plancher à 0,5°.

### Notes

- **`CHART_DTYPE` inchangé — sous-paquet additif** : `ketu.declination` est un
  complément purement additif à l'infrastructure de déclinaison δ de la v1.5.
  Le champ `body_decl` (forme `(14,)`) livré en v1.5 est l'entrée unique ;
  `CHART_DTYPE` est octet-identique à la v1.5 (aucune rupture du ratchet). Les
  nouveaux noms sont accessibles uniquement via `ketu.declination.*` —
  `ketu.__all__` est inchangé.
- **Parallèle ≠ conjonction de longitude** : les aspects de déclinaison sont
  indépendants des aspects de longitude écliptique. La table `core.aspects`
  figée à 14 lignes est octet-identique à la v1.5.

## [1.5.0] - 2026-06-04

### Ajouts

- **`declination(jdate, body)` — déclinaison équatoriale δ** : retourne δ en degrés
  [−90, +90] (nord positif, sud négatif). Scalaire et vectorisé (tableau `jdate`
  via `calc_planet_position_batch`, sans boucle). Calculé via la chaîne
  écliptique → équatorial (`spherical_to_rectangular → ecliptic_to_equatorial →
  rectangular_to_spherical`), numériquement équivalent à Meeus éq. 13.4 à la
  précision machine. (Phase 33)
- **`declination_velocity(jdate, body)`** : dδ/dt en degrés/jour (positif = vers
  le nord). Différence finie avant, pas 0,01 jour — symétrique de l'idiome FD de
  `lat_velocity`. (Phase 33)
- **`is_ascending_declination(jdate, body)`** : `True` quand dδ/dt > 0 (Lune
  montante). Auxiliaire biodynamique montant/descendant. **Distinct de
  `is_ascending`** (trajectoire β) — les deux peuvent diverger pour le même corps
  à la même date. (Phase 33)
- **`is_out_of_bounds(jdate, body)`** : `True` quand |δ| > ε(jd). Le seuil OOB
  utilise l'obliquité vraie instantanée (non l'obliquité moyenne). La Lune peut
  dépasser ε lors des grandes stations lunaires (~cycle nodal 18,6 ans ; pic
  ~2024–2025). (Phase 33)
- **`CHART_DTYPE` — champ `body_decl` (additif)** : nouveau champ `float64[14]`
  contenant la déclinaison équatoriale δ pour les 14 corps. `compute_chart` et
  `calculate_composite` le remplissent tous deux via la chaîne de coordonnées.
  Le nombre de corps reste 14 ; c'est un changement de dtype additif. (Phase 33)
- **Surface CLI `--harmonics h<N>` pour les harmoniques dynamiques** : la commande
  `aspects` accepte `--harmonics h7` (et tout `h2`–`h64`) pour détecter les aspects
  harmoniques dynamiques aux côtés de l'ensemble statique, via le chemin moteur
  `dynamic_specs=`. (Phase 34)

### Modifié

- **Nommage `H{h}-{k}` promu en contrat d'API public** : les lignes d'harmoniques
  dynamiques sont nommées `H{h}-{k}` (harmonique `h`, multiple `k`), verrouillées
  par des tests et documentées comme stables. (Phase 34)
- **`find_aspect_timing` gagne le paramètre `dyn_coef=`** : l'orbe pour un aspect
  dynamique est dérivé de `(orb[b1] + orb[b2]) / 2 × dyn_coef`, correspondant au
  chemin de détection. (Phase 34)

### Corrigé

- **Vitesse moyenne des nœuds lunaires corrigée (−0,013 → −0,052954 °/jour)** :
  `core.bodies['speed']` pour Rahu et Ketu contenait une valeur ~4× trop faible.
  La véritable régression nodale est de 360° sur ~18,6 ans (≈ −0,052991 °/jour) ;
  le moteur produisait déjà −0,052954 °/jour pour les nœuds, la table est donc
  désormais cohérente avec le mouvement calculé. `calculate_speed_ratio` source
  désormais ses vitesses moyennes depuis `core.bodies['speed']` (source de vérité
  unique). (Phase 33)
- **Lignes de paires en double de `calculate_aspects_batch` éliminées** : avec des
  orbes qui se chevauchent (ex. le jeu EXTENDED), le chemin batch pouvait émettre
  plus d'une ligne pour la même paire `(body1, body2)` à une date unique,
  violant le contrat documenté « exactement une ligne par paire ».
  `calculate_aspects_vectorized` et `calculate_aspects_batch` partagent désormais
  un noyau de détection unique (`_detect_aspects_for_date`), imposant statique
  d'abord / dynamique ensuite, premier-trouvé-gagne par paire de façon identique.
  (Phase 33)

### Notes

- **`is_ascending` (β) inchangé** : l'existant `is_ascending` basé sur la latitude
  écliptique est octet-identique à la v1.4. Le nouveau `is_ascending_declination`
  est un auxiliaire indépendant et parallèle.
- **Impact en aval (additif, sans rupture pour l'accès par nom)** : `CHART_DTYPE`
  gagne `body_decl` comme champ additif. Le code utilisant l'accès par nom de
  champ (`chart["body_lons"]`) n'est pas affecté. Le code utilisant l'accès
  positionnel ou `.view()` sur le dtype brut doit être adapté. La correction de
  vitesse des nœuds modifie `core.bodies['speed'][10]` / `[11]` ; le code aval
  lisant ce champ verra la valeur corrigée.

## [1.4.0] - 2026-06-03

### Ajouts

- **`generate_harmonic_aspects(h)` — générateur d'harmoniques dynamiques** : construit
  des spécifications d'aspects à la volée pour tout harmonique entier `h` (2 ≤ h ≤ 64),
  en utilisant la convention plein-cercle 360° ramenée à 0–180° (`coef = k/h`). Retourne
  un tableau structuré compatible avec `core.aspects` ; à passer via l'argument
  `dynamic_specs=` à `calculate_aspects`, `find_aspects_between_dates` et
  `calculate_synastry`. La table figée `core.aspects` (14 lignes) et les empreintes de
  préréglages restent octet-identiques (chemin parallèle et additif). Disponible via
  `ketu.aspects.generate_harmonic_aspects` et
  `ketu.aspects.harmonics.generate_harmonic_aspects`. (Phase 28)
- **Plage de Chiron étendue à 1900–2100** : `ketu/data/chiron_coeffs.npz` régénéré
  (2283 segments Chebyshev, `jd_start=2415020.5`, `jd_end=2488069.5`, seg=32 j,
  degré=10) ; erreur max |Δλ| = 0,001214° sur la nouvelle plage. Moteur d'évaluation
  pur NumPy préservé ; `.npz` ~578 Ko (était 289,7 Ko). `calc_planet_position(jd, 13)`
  résout tout JD dans la nouvelle plage, y compris 1900–1949 et 2051–2100. (Phase 30)

### Modifié

- **Orbe de Chiron 0° → 4°** (parité Pluton) : `core.bodies['orb']` pour Chiron vaut
  désormais 4° ; Chiron forme maintenant des aspects scorés dans `calculate_aspects`,
  `compute_chart`, `calculate_synastry` et `find_aspects_between_dates`. Le code aval
  supposant zéro aspect Chiron doit être adapté ; voir
  [UPGRADING.md](../UPGRADING.md) → « v1.3 -> v1.4 ». (Phase 29)
- **Comportement hors-plage de Chiron bridé** : un JD en dehors de 1900–2100 passé à
  `calc_planet_position(jd, 13)` / `calc_planet_position_batch(jds, 13)` est désormais
  silencieusement bridé au segment le plus proche ; auparavant, une `ValueError` était
  levée. (Phase 30)
- **Documentation recentrée sur le défaut 180°** : les tables d'aspects de `concepts.md`
  n'affichent plus que CLASSICAL (5) et TRADITIONAL (7) ; les harmoniques mineurs
  plein-cercle (H5/H9/H10 / EXTENDED) restent disponibles dans le code mais sont retirés
  des tables récapitulatives. (Phase 31)

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

- **RUPTURE (contrat positionnel en aval) :** les tableaux du
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
  Précédemment inversé. Les consommateurs en aval doivent
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
