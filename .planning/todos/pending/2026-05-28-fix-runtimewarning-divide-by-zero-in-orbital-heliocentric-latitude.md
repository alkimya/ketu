---
created: 2026-05-28T18:30:00.473Z
title: Fix RuntimeWarning divide-by-zero in orbital heliocentric latitude
area: general
files:
  - ketu/ephemeris/orbital.py:733
---

## Problem

`get_body_position_vectorized` calcule `lat = np.rad2deg(np.arcsin(z / r))` à
[ketu/ephemeris/orbital.py:733](ketu/ephemeris/orbital.py#L733). Quand `r == 0`
(le Soleil dans ce repère héliocentrique), `z / r = 0/0` produit un NaN et émet
`RuntimeWarning: invalid value encountered in divide`.

Cette latitude héliocentrique **n'est jamais utilisée** en aval : `calc_planet_position_batch`
([ketu/ephemeris/planets.py:520](ketu/ephemeris/planets.py#L520)) ne consomme que
x/y/z et ignore le retour `lat` (`_, _, _`). La longitude écliptique du chart
est calculée par un autre chemin et reste correcte.

**Impact :** purement cosmétique mais visible — le warning pollue le REPL à
**chaque** appel `compute_chart`, `solar_return`, `lunar_return`. Aucun NaN
n'apparaît dans les champs observables (`body_lons`, `cusps`, `asc`, `mc`
vérifiés propres).

**Provenance :** PRÉ-EXISTANT à Phase 18 (returns). `compute_chart` (Phase 14)
le déclenche déjà sur un appel direct. Découvert pendant l'UAT Phase 18
(test 1), journalisé comme observation hors-périmètre dans
`.planning/phases/18-solar-lunar-returns/18-UAT.md`.

## Solution

Garder la division contre `r == 0`. Options :
1. `np.divide(z, r, out=np.zeros_like(z), where=(r != 0))` puis `arcsin` — propre et vectorisé.
2. Court-circuiter complètement le calcul de `lat` si la valeur de retour n'est
   consommée nulle part (vérifier tous les call-sites de `get_body_position_vectorized` ;
   `calc_planet_position_batch` l'ignore déjà — confirmer qu'aucun autre appelant n'en a besoin
   avant de supprimer).

Ajouter un test qui exécute `compute_chart` sous `warnings.simplefilter("error", RuntimeWarning)`
pour ratcheter l'absence de warning (régression-guard). Vérifier que les latitudes
écliptiques des bodies restent inchangées après le fix.
