---
phase: 23-spike-chiron
plan: 01
subsystem: ephemeris
tags: [chebyshev, chiron, pyswisseph, numpy, spike, measurements]

# Dependency graph
requires:
  - phase: 22-ephemeris-refactor
    provides: BODY_STRATEGIES registry + cleaned planets.py — Chiron slot is ready
provides:
  - "spike_chiron_chebyshev.py: runnable Chebyshev-by-segment fit + accuracy sweep vs swe oracle"
  - "23-MEASUREMENTS.md: SPK-01 measured table (n_segs, coeff counts, KB, max|Δλ|, lat/dist)"
affects:
  - 23-spike-chiron/23-02 (go/no-go decision consumes these numbers)
  - 24-chiron (config params: seg=32, deg=10, 3 quantities, npz layout)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Chebyshev-by-segment: unwrap lon before fit, re-wrap % 360 at eval, 200-pt distinct validation grid, MAX not RMS"
    - "pyswisseph oracle pattern: set_ephe_path before calc_ut(swe.CHIRON), handle retflag 258/260"
    - "Pure-NumPy eval: np.polynomial.chebyshev.chebval(t, coef) — no scipy"

key-files:
  created:
    - .planning/phases/23-spike-chiron/spike_chiron_chebyshev.py
    - .planning/phases/23-spike-chiron/23-MEASUREMENTS.md
  modified: []

key-decisions:
  - "Primary config confirmed: seg=32j, degree=10 — max|Δλ|=0.000861° (11.6× under 0.01° target)"
  - "retflag=260 (Moshier fallback) acceptable: max diff vs SWIEPH ≤0.000067° (negligible)"
  - "n_segs=1142 (not 1153): plage exacte 36525j via swe.julday, non 36889j estimés en recherche"
  - "Worst segment: 2027-04-20 (pas 2046-2047 perihelion) — effet probable du fallback Moshier"
  - "3 quantités (lon+lat+dist) = 294.4 KB .npz — lat max 0.000986°, dist max 1.84e-7 AU"

patterns-established:
  - "Spike in .planning/ dir: zero impact on ketu/, tests/, pyproject.toml, pytest collection"

# Metrics
duration: 5min
completed: 2026-05-29
---

# Phase 23 Plan 01: Spike Chiron Summary

**Chebyshev-by-segment sur Chiron 1950-2050 : max|Δλ|=0.000861° (11.6× sous la cible 0.01°) avec seg=32j/deg=10, 98 KB lon-only, confirmé pure-NumPy sans scipy**

## Performance

- **Duration:** ~5 min (dont ~4 min de sweep oracle pyswisseph)
- **Started:** 2026-05-29T19:04:37Z
- **Completed:** 2026-05-29T19:09:05Z
- **Tasks:** 2/2
- **Files created:** 2

## Accomplishments

- Script `spike_chiron_chebyshev.py` opérationnel : sweep complet 5 configs × 1142 segments chacune, sorties propres, exit 0
- Confirmation de la méthodologie complète : longitude déroulée, grille validation 200 pts distincte, MAX pas RMS, TOUS les segments
- `23-MEASUREMENTS.md` (SPK-01) avec vraies mesures mesurées, métadonnées oracle (retflag 260), lat/dist, pire segment, note sur n_segs réel vs estimé

## Task Commits

1. **Task 1: Write the spike fit-and-measure script** — `a80da5e` (feat)
2. **Task 2: Capture the measurement table in 23-MEASUREMENTS.md** — `c99d1f4` (feat)

## Files Created/Modified

- `.planning/phases/23-spike-chiron/spike_chiron_chebyshev.py` — script spike 446 lignes, runnable, non collecté par pytest
- `.planning/phases/23-spike-chiron/23-MEASUREMENTS.md` — table SPK-01 133 lignes, mesures réelles

## Decisions Made

- **Config primaire confirmée : seg=32j, degree=10** — max|Δλ|=0.000861°, 11.6× sous la cible, 98.1 KB lon-only, 294.4 KB lon+lat+dist
- **retflag=260 (Moshier fallback) noté et documenté** — `seas_18.se1` seul (sans `sepl_18.se1`) force le Moshier analytique pour Sun/Moon géocentrique. Différence max vs SWIEPH : 0.000067° selon Q5 research, négligeable
- **n_segs=1142** — plage exacte `swe.julday(2050,1,1)-swe.julday(1950,1,1)=36525j` (pas 36889j) ; `ceil(36525/32)=1142`
- **Pire segment 2027-04-20** (pas 2046-2047 perihelion comme prévu en recherche) — à documenter dans 23-DECISION.md ; peut être lié au Moshier sur la région 2046
- **3 quantités confirmées** : lat max 0.000986°, dist max 1.84×10⁻⁷ AU — les deux négligeables, config identique possible pour lat+dist

## Deviations from Plan

None — plan exécuté exactement comme écrit. Les écarts de valeurs par rapport aux prévisions de recherche (n_segs, pire segment) sont documentés comme données mesurées dans `23-MEASUREMENTS.md`.

## Issues Encountered

- **retflag=260 vs 258 attendu** : `seas_18.se1` présent mais pas `sepl_18.se1` → pyswisseph utilise Moshier pour les planètes nécessaires au géocentrique. Résolu : documenté dans les mesures ; la différence de 0.000067° est négligeable et le script continue normalement.
- **n_segs=1142 vs 1153 en recherche** : la recherche avait estimé 36889 jours (années juliennes). `swe.julday` exact donne 36525 jours (années grégoriennes calendaires 1950-2050). Aucun impact sur la validité.

## User Setup Required

None — spike dans `.planning/`, aucune configuration externe nécessaire pour le repo.

## Next Phase Readiness

- **23-02 (go/no-go)** : les mesures sont disponibles dans `23-MEASUREMENTS.md`. Config recommandée : seg=32, deg=10. Toutes les données nécessaires à la décision sont présentes.
- **Phase 24 (Chiron)** : paramètres confirmés — seg_len=32, degree=10, 3 quantités (lon+lat+dist), npz ~300 KB, évaluateur `np.polynomial.chebyshev.chebval`. Pour la CI Phase 24 : `seas_18.se1` requis (possiblement à bundler dans `tests/res/` ou skip conditionnel).

---
*Phase: 23-spike-chiron*
*Completed: 2026-05-29*
