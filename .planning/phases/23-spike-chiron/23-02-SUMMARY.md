---
phase: 23-spike-chiron
plan: 02
subsystem: ephemeris
tags: [chiron, chebyshev, decision, go-no-go, spike, measurements]

# Dependency graph
requires:
  - phase: 23-01
    provides: "23-MEASUREMENTS.md (SPK-01) — valeurs mesurées max|Δλ|, n_segs, lat/dist, pire segment"
provides:
  - "23-DECISION.md: verdict GO explicite + paramètres Phase 24 verrouillés (SPK-02)"
affects:
  - 24-chiron (paramètres seg=32j/deg=10/3 quantités, layout .npz, points d'insertion)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Décision go/no-go consommant des mesures empiriques (SPK-01 → SPK-02 pipeline)"

key-files:
  created:
    - .planning/phases/23-spike-chiron/23-DECISION.md
  modified: []

key-decisions:
  - "GO pour Phase 24 : max|Δλ|=0.000861° (11.6× sous 0.01°) — cible ATTEINTE sur 1950-2050"
  - "Config verrouillée : seg=32j, deg=10, 3 quantités (lon+lat+dist), vitesses par différence finie jd_delta=0.01"
  - "Layout .npz : lon_coeffs/lat_coeffs/dist_coeffs shape (1142,11) f64 + seg_starts (1142,) f64 + scalaires"
  - "seas_18.se1 requis pour Phase 24 : séparation CI différée (3 options documentées, décision Phase 24)"
  - "Points d'insertion référencés (non modifiés) : BODY_INDICES[Chiron]=13, SWE_IDS[13], BODY_STRATEGIES, plage 0-13"

# Metrics
duration: 2min
completed: 2026-05-29
---

# Phase 23 Plan 02: SPK-02 Go/No-Go Decision Summary

**Décision GO explicite pour Phase 24 Chiron : max|Δλ|=0.000861° (11.6× sous la cible 0.01°), config verrouillée seg=32j/deg=10/3-quantités, layout .npz et points d'insertion documentés**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-05-29T19:11:34Z
- **Completed:** 2026-05-29T19:13:16Z
- **Tasks:** 1/1
- **Files created:** 1

## Accomplishments

- `23-DECISION.md` rédigé (277 lignes) en consommant les valeurs mesurées de `23-MEASUREMENTS.md`
- Verdict **GO** posé en tête de document, clairement lisible
- Config Phase 24 verrouillée : seg=32j, deg=10, 3 quantités (lon+lat+dist), vitesses par différence finie `jd_delta=0.01`
- Précision documentée : max|Δλ|=0.000861° (11.6× sous 0.01°), max|Δlat|=0.000986°, max|Δdist|=1.84×10⁻⁷ AU
- Pire segment documenté : 2027-04-20, erreur=0.000861°
- Comparaison < 0.01° explicitement notée **ATTEINT**
- Layout .npz complet (8 tableaux, formes, dtypes)
- Exigence `seas_18.se1` + `set_ephe_path` documentée avec 3 options CI pour Phase 24
- Points d'insertion Phase 24 référencés : `BODY_INDICES`, `SWE_IDS`, `BODY_STRATEGIES`, `calc_planet_position` plage 0-13, ratchet 13→14
- Évaluateur pur-NumPy `np.polynomial.chebyshev.chebval` documenté avec pattern exact
- Garde-fous de périmètre explicites : aucun ketu/, aucun pytest, aucune dépendance runtime

## Task Commits

1. **Task 1: Write the go/no-go decision record (23-DECISION.md)** — `69b899e` (feat)

## Files Created/Modified

- `.planning/phases/23-spike-chiron/23-DECISION.md` — décision SPK-02, 277 lignes

## Decisions Made

- **GO pour Phase 24 Chiron** — max|Δλ|=0.000861° sur 1950-2050, 11.6× sous la cible. Aucune condition de blocage.
- **Config verrouillée : seg=32j, deg=10, 3 quantités** — sweet spot confirmé : compact (294 KB), précis (11.6× marge), évaluateur pur-NumPy.
- **Vitesses par différence finie (jd_delta=0.01)** — pattern `_make_planet_scalar` existant, pas de coefficients supplémentaires stockés.
- **Layout .npz documenté** : 8 entrées, shapes (1142,11) × 3 quantités + (1142,) seg_starts + 4 scalaires.
- **Options CI seas_18.se1 différées à Phase 24** — 3 options listées (bundle fixture / importorskip+skip / res/), Phase 23 ne décide pas.

## Deviations from Plan

None — plan exécuté exactement comme écrit. Les valeurs mesurées (n_segs=1142, pire segment
2027-04-20) avaient déjà été documentées dans 23-MEASUREMENTS.md en 23-01 ; 23-DECISION.md
les transcrit fidèlement.

## Phase 23 — Clôture du spike

Les deux objectifs du spike sont livrés :
- **SPK-01** (23-01) : `spike_chiron_chebyshev.py` + `23-MEASUREMENTS.md` — mesures empiriques
- **SPK-02** (23-02) : `23-DECISION.md` — verdict GO + paramètres Phase 24 verrouillés

Suite de tests : **1 351 tests, 100% couverture** — inchangés.

## Next Phase Readiness

- **Phase 24 (Chiron)** peut démarrer sur des bases solides :
  - Paramètres confirmés : `seg_len=32`, `degree=10`, `n_quantities=3`
  - Layout .npz documenté (shapes, dtypes)
  - Points d'insertion identifiés (6 fichiers)
  - Évaluateur pur-NumPy confirmé
  - Exigence `seas_18.se1` documentée avec options CI
  - Ratchet 13→14 planifié

---
*Phase: 23-spike-chiron*
*Completed: 2026-05-29*
