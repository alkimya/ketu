# Journal des modifications (version française)

> **Note :** Ce fichier est une traduction synthétisée du fichier
> [`../CHANGELOG.md`](../CHANGELOG.md) anglais, qui fait foi.
> Il n'est pas maintenu en parallèle : il est régénéré à chaque
> publication de version en même temps que la version anglaise.
> En cas de divergence, la version anglaise est la référence
> authoritative.

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
