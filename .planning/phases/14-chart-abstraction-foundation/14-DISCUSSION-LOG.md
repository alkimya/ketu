# Phase 14: Chart Abstraction Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-08
**Phase:** 14-chart-abstraction-foundation
**Areas discussed:** CHART_DTYPE shape, compute_chart signature, is_day_chart edge cases, Aspects intra-chart shape & filtering

---

## CHART_DTYPE shape

### Q1 — Empaquetage des positions des 13 bodies

| Option | Description | Selected |
|--------|-------------|----------|
| Subarray (13,) — comme HOUSES.cusps | Champs `body_lons (f8, (13,))`, `body_lats`, `body_speeds`. Indexation positionnelle. Mirror v1.1. | ✓ |
| Subarray + dtype imbriqué par body | Champ `bodies (BODY_DTYPE, (13,))` avec sous-dtype dédié. | |
| 13 champs scalaires nommés (sun_lon, moon_lon...) | Lisible mais perd la batchabilité. | |

**User's choice:** Subarray (13,) — mirror HOUSES_DTYPE precedent.
**Notes:** Cohérence avec v1.1 ; Kala-friendly indexation positionnelle.

### Q2 — Granularité des positions

| Option | Description | Selected |
|--------|-------------|----------|
| Lon seulement | Minimum viable. | |
| Lon + lat + speed | Speed → retrograde derivable; lat utile pour parallèles futurs. | ✓ |
| Lon + lat + speed + dist + retro flag | Tout body_properties() ; redondant. | |

**User's choice:** Lon + lat + speed.
**Notes:** Pas de dist (rarement utile hors déclinaison) ; retro = sign(speed).

### Q3 — Empaquetage des cusps + ASC/MC

| Option | Description | Selected |
|--------|-------------|----------|
| Répliquer les champs HOUSES inline | `cusps (12,)`, `asc`, `mc`, `armc`, `vertex` directement. Pas d'imbrication. | ✓ |
| Champ imbriqué `houses (HOUSES_DTYPE,)` | Single source-of-truth mais ajoute indirection. | |
| Subarray houses (HOUSES_DTYPE, (1,)) | Bizarre pour shape fixe. | |

**User's choice:** Répliquer inline.
**Notes:** Naturel pour ML, accès direct.

### Q4 — Métadonnées dans CHART_DTYPE

| Option | Description | Selected |
|--------|-------------|----------|
| Tous (jd, lat, lon, system) | Self-describing ; mirror HOUSES_DTYPE. | ✓ |
| Seulement jd | Compact mais perd self-description. | |
| Aucun | Anti-pattern pour SYN/COMP/RET. | |

**User's choice:** Tous.
**Notes:** Synastry/composite/return en ont besoin pour retracer le contexte.

### Q5 — Encodage des aspects intra-chart

| Option | Description | Selected |
|--------|-------------|----------|
| Matrice dense (13,13) of i_asp + (13,13) of orb | Shape fixe ; NumPy-first ; ML-friendly. 845 octets/chart. | ✓ |
| Pas d'aspects dans CHART_DTYPE — helper séparé | Casse le contrat ROADMAP "single call". | |
| Variable-length object field | Anti-pattern ML. | |
| Champ séparé retourné en tuple | Casse le contrat "single CHART_DTYPE return". | |

**User's choice:** Matrice dense (13,13).
**Notes:** Coût mémoire négligeable vs batchabilité.

### Q6 — AspectSet par défaut

| Option | Description | Selected |
|--------|-------------|----------|
| CLASSICAL (5 majors) — conforme v1.1 | Aligned sur Phase 9 default. Re-uses `resolve_aspect_set`. | ✓ |
| EXTENDED (14) | Inverse la décision v1.1. | |
| Aucun (forcer aspects=) | Friction inutile. | |

**User's choice:** CLASSICAL.
**Notes:** Une seule notion de "default aspect set" dans le projet.

---

## compute_chart signature

### Q7 — Liste de bodies configurable ?

| Option | Description | Selected |
|--------|-------------|----------|
| Figée à 13 | Shape fixe (13,) ; (13,13) aspect_matrix garanti ; v1.3 Chiron = BREAKING acceptable. | ✓ |
| Configurable via param `bodies=` | Casse le shape fixe de aspect_matrix. | |
| Figée mais filtre post-hoc | Sur-ingénierie. | |

**User's choice:** Figée à 13.
**Notes:** Le `(13,)` axis est partie du contrat CHART_DTYPE ; v1.3 grossira à 14 avec Chiron.

### Q8 — Vectorisation sur jd array

| Option | Description | Selected |
|--------|-------------|----------|
| Broadcast jd, lat, lon (mirror calculate_houses) | Cohérent avec v1.1 ; "mille charts en un appel" pour ML. | ✓ |
| Scalaire seul + boucle externe | Casse "no Python loop in hot path". | |
| Vectorisé sur jd seulement | Asymétrique avec calculate_houses. | |

**User's choice:** Broadcast (jd, lat, lon).
**Notes:** Même contrat que `calculate_houses`.

### Q9 — Param `aspects=`

| Option | Description | Selected |
|--------|-------------|----------|
| AspectSetSpec complet | Même contrat que calculate_aspects ; flexible mask Kala. | ✓ |
| Restreint aux noms de presets | Plus contraint, perd la flexibilité custom. | |

**User's choice:** AspectSetSpec complet.
**Notes:** Une seule API à apprendre.

### Q10 — Param `polar_fallback`

| Option | Description | Selected |
|--------|-------------|----------|
| Oui, même contrat que calculate_houses | Pass-through ; cohérence d'API. | ✓ |
| Non, fixé à 'raise' | Force le caller polar à contourner. | |
| Non, fixé à 'porphyry' | Silent fallback ; anti-pattern. | |

**User's choice:** Oui, même contrat.
**Notes:** Solar return relocated en Islande pourra l'utiliser.

---

## is_day_chart edge cases

### Q11 — Convention sect : Sun sur l'ASC (sunrise)

| Option | Description | Selected |
|--------|-------------|----------|
| Day inclusive (Sun >= ASC = day) | Hellenistic standard ; pro tools. | ✓ |
| Night inclusive (Sun > ASC strict) | Minoritaire. | |
| Sentinel 'twilight' | Over-engineering. | |

**User's choice:** Day inclusive.
**Notes:** Documenter dans la docstring.

### Q12 — Géométrie 'Sun above ASC'

| Option | Description | Selected |
|--------|-------------|----------|
| Sun longitude in houses 7-12 | Standard astrologique ; re-uses `house_of`. | ✓ |
| (sun_lon - asc) mod 360 in [180, 360] | False simplicity ; dépend du système. | |
| Sun altitude (h>0) via formule horizon | Over-engineering. | |

**User's choice:** Houses 7-12.
**Notes:** Re-utilise `house_of` ; pas de déclinaison nécessaire.

### Q13 — is_day_chart à lat polaire

| Option | Description | Selected |
|--------|-------------|----------|
| Propager NaN (tristate i1 -1) | Casse le contrat bool de la success criterion 14.3. | |
| polar_fallback='porphyry' interne | Porphyry défini partout ; pure-NumPy. | ✓ |
| Raise HighLatitudeError | Casse PARTS pour relocated returns en Islande. | |
| Retourner True par défaut | Silent default ; anti-pattern. | |

**User's choice:** Porphyry interne.
**Notes:** Documenter le rationnel dans la docstring.

### Q14 — Stocker is_day dans CHART_DTYPE ?

| Option | Description | Selected |
|--------|-------------|----------|
| Non, helper standalone seulement | Évite double source-of-truth ; PARTS appellera `(jd, lat, lon)` form. | ✓ |
| Oui, ajouter `is_day (bool)` dans CHART_DTYPE | Drift risk si qq'un modifie sun_lon ou asc. | |
| Surcharge (jd,lat,lon) ET (chart) | Adds API surface ; pick one en v1.2. | |

**User's choice:** Helper standalone seulement.
**Notes:** Overload `(chart)` deferred — surface en Phase 19 si friction.

---

## Aspects intra-chart: shape & filtering

### Q15 — Réutiliser calculate_aspects_vectorized ?

| Option | Description | Selected |
|--------|-------------|----------|
| Réutiliser, adapter pour leading shape | DRY ; one source-of-truth ; loop Python sur S acceptable v1.2. | ✓ |
| Réimplémenter pure-vectorisé | Plus rapide gros batches ; plus de code. | |
| Helper interne réutilisé puis vectorisé v1.3 | Pragmatique ; effectivement = option 1. | |

**User's choice:** Réutiliser.
**Notes:** Profile en Phase 16 si la boucle domine.

### Q16 — Symétrie de la matrice

| Option | Description | Selected |
|--------|-------------|----------|
| Triangulaire sup, diag = -1, lower mirror | Lookup intuitif quel que soit l'ordre. 2x mémoire négligeable. | ✓ |
| Triangulaire stricte, lower = -1 | Force i<j ; surprise consommation. | |
| Full matrix avec calcul redondant | 2x calcul. | |

**User's choice:** Triangulaire sup + lower mirror.
**Notes:** 845 octets/chart total.

### Q17 — Sentinel "pas d'aspect" dans aspect_matrix

| Option | Description | Selected |
|--------|-------------|----------|
| i_asp = -1 dans champ i1 | Lisible ; mask propre `>= 0`. | ✓ |
| Valeur 14 (hors range valide) | Arbitraire. | |
| Mask bool séparé | 2x champs à synchroniser. | |

**User's choice:** -1 dans i1.

### Q18 — Sentinel orb "absent"

| Option | Description | Selected |
|--------|-------------|----------|
| NaN | Idiome NumPy ; mask propre `~np.isnan`. | ✓ |
| Sentinel numérique spécial (-999) | Fragile (égalité float). | |
| 0.0 | Ambigu (conjunction exacte). | |

**User's choice:** NaN.

---

## Claude's Discretion

- Internal sub-module split inside `ketu/charts/` (api.py / sect.py / single api.py).
- Whether `is_day_chart` lives in `api.py`, `sect.py`, or `core.py`.
- Aspect-matrix builder as private helper or its own module.
- `[tool.coverage.run]` exclusion (likely none).
- Re-export `house_of` from `ketu.charts` for ergonomics — minor.
- Test fixture choices and oracle reference charts (re-use v1.1 patterns).

---

## Deferred Ideas

- `is_day_chart(chart)` overload accepting a CHART_DTYPE row — surface in Phase 19 only if needed.
- Chiron / additional bodies → v1.3 (acknowledged BREAKING).
- Pure-vectorised aspect-matrix (no Python loop) → profile in Phase 16, revisit v1.3 if dominant.
- `compute_chart_aspects(chart, aspects=...)` standalone re-derivation helper → v1.3 candidate.
- Bool subarray for `is_retrograde` → `chart_is_retrograde(chart)` ergonomic helper later.
- Top-level `from ketu import compute_chart, CHART_DTYPE` re-export → v1.3 once API stabilises.
- Per-body `dist` field → only if declination-based aspects surface as a feature.
