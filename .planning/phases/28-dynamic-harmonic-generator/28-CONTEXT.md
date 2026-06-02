# Phase 28: Dynamic Harmonic Generator + Detection Integration - Context

**Gathered:** 2026-06-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Un utilisateur peut générer à la volée des aspects de premier ordre pour **n'importe quel
harmonique entier** `h` (H7, H11, H17…) via une nouvelle fonction publique
`generate_harmonic_aspects(h)`, et les faire détecter à travers toute la chaîne :
`calculate_aspects` (scalaire / vectorisé / batch), `find_aspects_between_dates`,
`find_aspect_timing`, `calculate_synastry`, et les cycles — **sans jamais muter** la table
figée `core.aspects` (14 lignes) ni ses empreintes sha256 (V1 `c5bd177…`, V13 `3258530…`).

Le chemin dynamique est **parallèle et additif**. `_VALID_HARMONICS` /
`aspects_for_harmonics` ne sont **jamais** consultés sur ce chemin (sinon ValueError sur
H7/H11/H17).

Cette phase clarifie le COMMENT. Le CLI, l'unification d'orbe, et toute nouvelle capacité
sortent du périmètre.

</domain>

<decisions>
## Implementation Decisions

### Forme & API du générateur (`generate_harmonic_aspects(h)`)
- **Dtype de retour identique à `core.aspects`** : `[name S16, angle f4, coef f4,
  harmonic i4, symbol U4]`. Drop-in : consommable partout où `core.aspects` l'est.
- **Nommage synthétique `H{h}-{k}`** dans le champ `name` (ex. `H7-1`, `H7-2`, `H7-3`).
  Déterministe, sans collision, indique l'harmonique et le rang `k`.
- **Symbole vide** (`U4` blanc) pour toutes les lignes dynamiques — même convention que
  les 7 minors actuels (Decile, Novile…). Pas de glyphe inventé ; l'identité passe par
  `name`.
- **Champ `harmonic` = h** ; le rang `k` est encodé dans `name` (pas de colonne `k`
  séparée, puisque le dtype reste celui de `core.aspects`).
- **Convention 360° verrouillée (spec ROADMAP exacte)** : angles
  `fold_to_0_180(k·360/h)` pour `k = 1..h//2`, `coef = k/h`, paires miroir
  **dédupliquées**, `0°/360°` **jamais émis**. Comportement déterministe.
- **Validation de `h` → Claude's Discretion** : le planner fixe la borne (h entier ≥ 1
  ou ≥ 2, borne haute éventuelle) selon la convention 360° et les contraintes d'orbe.
  ValueError clair sur entrée invalide.

### Intégration `dynamic_specs`
- **Nom de paramètre uniforme : `dynamic_specs`** sur `calculate_aspects`,
  `calculate_aspects_vectorized`, `calculate_aspects_batch`,
  `find_aspects_between_dates`, `calculate_synastry`, et la chaîne cycles. Conforme
  ROADMAP/STATE.
- **Combinables en union** : `aspects=` (preset/mask table) ET `dynamic_specs=` peuvent
  coexister. Sortie = aspects table sélectionnés **PLUS** aspects dynamiques.
- **Ordre de détection : statique d'abord** (ordre canonique table 0-13), **puis
  dynamique** (ordre de génération du spec). Une opposition/conjonction classique gagne
  sur un angle dynamique proche.
- **First-match-wins préservé** : une seule ligne par paire `(body1, body2)`, premier
  match dans l'ordre de détection ci-dessus. Contrat dtype/positionnel et invariant
  consommateur (Kala) intacts — pas de multi-lignes par paire.
- **Orbe dynamique** : `(orb_b1 + orb_b2) / 2 × coef` avec `coef = k/h` issu du spec.
  Les orbes full-circle ~2× plus petits que l'équivalent demi-cercle sont **ACCEPTÉS**
  (décision v1.4 déjà verrouillée — pas d'unification, pas de coef plancher).
- **Sentinelle `i_asp = -2`** pour toutes les lignes dynamiques dans la sortie de
  `calculate_aspects` (dtype de sortie `(body1, body2, i_asp, orb)` inchangé).

### Identité & ré-identification des lignes dynamiques
- **Sortie `calculate_aspects`** : `i_asp = -2` marque « dynamique ». L'utilisateur
  ré-identifie l'aspect précis via l'**orbe signé** (`angle - dist`) recroisé avec ses
  propres `dynamic_specs`. **Pas de nouveau champ** ; dtype de sortie inchangé.
- **`find_aspects_between_dates`** (tuples `(jdate, b1, b2, aspect_name, aspect_value)`) :
  pour un angle dynamique off-table, retourner le **name synthétique du spec** (`H7-1`),
  pas un crash. Cohérent avec le nommage du générateur.
- **`find_aspect_timing`** : ajouter un **paramètre `coef` (ou orbe) explicite optionnel**
  pour les angles dynamiques. Si absent ET angle off-table → `ValueError` clair (jamais
  d'IndexError). L'appelant fournit le `coef = k/h` de son spec.
- **Guards IndexError obligatoires (ship dans cette phase)** : `find_aspect_timing:427`
  et `find_aspects_between_dates:534` font tous deux
  `np.where(_CORE_ASPECTS["angle"] == …)[0]` et crashent sur un angle dynamique. Les deux
  guards atterrissent dans la même phase que `dynamic_specs`.

### Périmètre d'intégration & ergonomie
- **API-seule — PAS de CLI** : `dynamic_specs` exposé uniquement via l'API Python. Le CLI
  reste sur les presets nommés (`classical`/`traditional`/`extended`) → byte-stable,
  **aucun churn de fixture CLI** (évite de concurrencer les Phases 29/30).
- **Cycles : requis** (critère ROADMAP #3) — `dynamic_specs` câblé dans
  `generate_cycle_series` / la chaîne cycles ; les séries générées avec `dynamic_specs`
  incluent les détections dynamiques.
- **Synastry : requis** (critère ROADMAP #3) — `calculate_synastry` avec `dynamic_specs`
  retourne des lignes dynamiques en `SYNASTRY_DTYPE`, orbe dérivé de `_BODY_ORBS_16` ×
  coef dynamique.
- **Doctests : générateur + bout-en-bout** — (1) `generate_harmonic_aspects(7)` montre
  les 3 angles H7 + coefs ; (2) un mini end-to-end passant les specs à
  `calculate_aspects` et montrant une détection. Calibrés pour passer le gate doctest
  100% sans fragilité float.

### Claude's Discretion
- Validation exacte de `h` (bornes min/max, traitement de h=1).
- Forme interne du paramètre orbe de `find_aspect_timing` (`coef` vs `orb` direct) tant
  que l'IndexError est éliminé et la signature publique reste rétro-compatible si possible.
- Implémentation vectorisée précise du chemin dynamique (batchable, zéro boucle Python en
  hot path).
- Calibrage exact des doctests (valeurs float, tolérances).

</decisions>

<specifics>
## Specific Ideas

- Le `name` synthétique `H{h}-{k}` doit rester lisible à l'inspection brute : `H7-1`,
  `H7-2`, `H7-3` pour l'harmonique 7 (qui produit 3 angles distincts après dédup miroir).
- Cohérence visuelle avec l'existant : les lignes dynamiques ressemblent aux minors de la
  table (symbol vide), seule l'identité textuelle (`name`) et `i_asp=-2` les distinguent.
- La sortie de `calculate_aspects` reste volontairement minimale (`body1, body2, i_asp,
  orb`) — on ne l'enrichit PAS d'un champ angle pour préserver le contrat consommateur ;
  la ré-identification est la responsabilité de l'appelant qui détient ses `dynamic_specs`.

</specifics>

<deferred>
## Deferred Ideas

- **Flag CLI `--harmonic N`** — exposer le générateur dynamique en ligne de commande.
  Reporté : touche `display.py` + fixtures CLI, risque de churn byte concurrent aux
  Phases 29/30. Candidat pour une phase future si demande utilisateur.
- **Champ `k` explicite / champ angle dans la sortie de `calculate_aspects`** — enrichir
  le dtype de sortie pour ré-identification directe sans recroisement. Reporté : casse le
  contrat positionnel actuel (Kala). Reconsidérer si la ré-identification par orbe signé
  s'avère insuffisante en usage réel.
- **Unification d'orbe full-circle** — normaliser les orbes des hauts harmoniques pour
  qu'ils ne soient pas 2× plus petits. Explicitement REJETÉ pour v1.4 (décision
  verrouillée : orbes 2× plus petits acceptés, pas d'unification).

</deferred>

---

*Phase: 28-dynamic-harmonic-generator*
*Context gathered: 2026-06-02*
