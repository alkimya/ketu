---
phase: 24-chiron
plan: 01
subsystem: ephemeris
tags: [chiron, chebyshev, numpy, pyswisseph, npz, build-tools]

# Dependency graph
requires:
  - phase: 23-spike-chiron
    provides: locked params (seg=32j, deg=10, n_segs=1142), .npz layout, seas_18.se1 path

provides:
  - "tools/gen_chiron_coeffs.py: offline Chebyshev coefficient generator (pyswisseph build-only)"
  - "ketu/data/__init__.py: package marker making ketu.data a Python package"
  - "ketu/data/chiron_coeffs.npz: 1142-segment Chebyshev coefficients for Chiron 1950-2050 (lon/lat/dist)"
  - "7 pinned reference (jd, lon) tuples for plan 24-04 accuracy regression test"

affects:
  - 24-02 (needs .npz to test the loader and chiron.py evaluator)
  - 24-03 (needs ketu.data package for pyproject.toml wiring)
  - 24-04 (needs reference longitudes captured here)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Offline build-only generator in tools/ (outside ketu/ and tests/) — one-time artifact producer"
    - "np.savez_compressed with 8 named arrays (locked layout per 23-DECISION §4)"
    - "Pure-NumPy validation gate using chebval before writing .npz — aborts on max|Δλ| >= 0.01°"
    - "swisseph imported only inside function bodies, never at module top-level (AGPL isolation)"

key-files:
  created:
    - tools/gen_chiron_coeffs.py
    - ketu/data/__init__.py
    - ketu/data/chiron_coeffs.npz
  modified: []

key-decisions:
  - "Generator placed in tools/ (not scripts/) — one-time build artifact producer, not operational script"
  - "retflag=260 (Moshier fallback) confirmed acceptable — max diff vs SWIEPH ≤ 0.000067° (negligible)"
  - "Validation gate uses pur-NumPy chebval (not Chebyshev object) — matches the runtime evaluator exactly"
  - "7 reference longitudes pinned via --dump-refs for plan 24-04 regression test (no pyswisseph at test time)"

patterns-established:
  - "tools/ directory: build-only scripts that must never be imported by ketu/ or collected by pytest"
  - "ketu/data/ package: binary artifacts shipped inside the wheel via setuptools package-data"

# Metrics
duration: 7min
completed: 2026-05-29
---

# Phase 24 Plan 01: Chiron Coefficient Generator Summary

**Offline Chebyshev generator (pyswisseph + seas_18.se1) produces ketu/data/chiron_coeffs.npz (289.7 KB, 1142 segments, max|Δλ|=0.000861°, 11.6× under 0.01° target)**

## Performance

- **Duration:** ~7 min (dominated by 1142 × 3-quantity fit + 1142 × 200-point validation)
- **Started:** 2026-05-29T19:57:42Z
- **Completed:** 2026-05-29T22:01:00Z
- **Tasks:** 2/2
- **Files created:** 3

## Accomplishments

- `tools/gen_chiron_coeffs.py` (659 lignes) — générateur hardened du spike SPK-01 avec argparse `--output`/`--dump-refs`, gate de validation pur-NumPy (sys.exit(1) si max|Δλ| >= 0.01°), numpydoc complet, swisseph uniquement dans les corps de fonctions
- `ketu/data/chiron_coeffs.npz` — 1142 segments × 3 quantités (lon/lat/dist), 289.7 KB compressé, gate passé : max|Δλ|=0.000861° (11.6× sous cible), max|Δlat|=0.000986°, max|Δdist|=1.84e-7 UA
- 7 longitudes de référence capturées via `--dump-refs` pour le test de régression plan 24-04

## Task Commits

1. **Task 1: Write the offline generator tools/gen_chiron_coeffs.py** — `dc7636d` (feat)
2. **Task 2: Create ketu/data package and generate + commit the .npz** — `0f220a4` (feat)

## Files Created/Modified

- `/home/loc/workspace/ketu/tools/gen_chiron_coeffs.py` — Générateur offline Chebyshev (659 lignes), argparse `--output`/`--dump-refs`, gate max|Δλ| < 0.01°, build-only (jamais importé par ketu/)
- `/home/loc/workspace/ketu/ketu/data/__init__.py` — Marqueur de package vide (setuptools requis)
- `/home/loc/workspace/ketu/ketu/data/chiron_coeffs.npz` — Artefact Chebyshev 1950-2050 (289.7 KB, 8 tableaux nommés)

## Decisions Made

- Generator placé dans `tools/` (pas `scripts/`) — distinction claire : `scripts/` = scripts opérationnels, `tools/` = outils build-only
- retflag=260 (Moshier fallback) confirmé acceptable — mesuré max 0.000067° vs SWIEPH, négligeable
- Gate de validation utilise `np.polynomial.chebyshev.chebval` (pur-NumPy, pas l'objet Chebyshev) — cohérent avec l'évaluateur runtime de plan 24-02

## Longitudes de référence Chiron (pour plan 24-04)

Capturées avec `tools/gen_chiron_coeffs.py --dump-refs` (oracle pyswisseph + seas_18.se1, retflag=260) :

```python
_CHIRON_REFS: list[tuple[float, float]] = [
    (2433282.5, 255.777223),  # 1950-01-01  retflag=260
    (2440587.5, 2.520351),    # 1970-01-01  retflag=260
    (2447892.5, 103.847482),  # 1990-01-01  retflag=260
    (2451545.0, 251.617624),  # J2000.0     retflag=260
    (2455197.5, 323.115304),  # 2010-01-01  retflag=260
    (2462501.5, 38.042056),   # 2030-01-01  retflag=260
    (2469807.5, 246.587706),  # 2050-01-01  retflag=260
]
TOLERANCE_DEG = 0.01  # spike-validated max|Δλ|=0.000861°, soit 11.6× looser
```

## Deviations from Plan

None - plan exécuté exactement tel qu'écrit.

## Issues Encountered

None — pyswisseph disponible dans le venv, `seas_18.se1` au chemin prévu (`/home/loc/workspace/rahu/kerykeion/kerykeion/sweph/`), generator a tourné sans erreur.

## Verification Results

- `pytest --collect-only 2>&1 | grep "tools/"` : vide (generator non collecté)
- `grep -rn "import swisseph" ketu/` : vide (ratchet AGPL respecté)
- `.npz` chargeable en pur-NumPy : `OK ['degree', 'dist_coeffs', 'jd_end', 'jd_start', 'lat_coeffs', 'lon_coeffs', 'seg_len', 'seg_starts']`
- `ls -la ketu/data/chiron_coeffs.npz` : 296611 bytes (289.7 KB, < 303 KB limit)

## Self-Check: PASSED

## Next Phase Readiness

- Plan 24-02 peut démarrer : `ketu/data/chiron_coeffs.npz` est committéet loadable
- Plan 24-03 peut suivre : `ketu/data/__init__.py` est en place pour le wiring pyproject.toml
- Plan 24-04 a ses 7 longitudes de référence (verbatim ci-dessus)

---
*Phase: 24-chiron*
*Completed: 2026-05-29*
