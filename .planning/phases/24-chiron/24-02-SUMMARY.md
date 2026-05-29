---
phase: 24-chiron
plan: 02
subsystem: ephemeris
tags: [chiron, chebyshev, numpy, importlib-resources, lru_cache, aberration, coverage]

# Dependency graph
requires:
  - phase: 24-chiron/24-01
    provides: ketu/data/chiron_coeffs.npz (1142 segments, deg=10, 3 quantities)

provides:
  - "ketu/ephemeris/chiron.py: _load_chiron_data, _eval_chiron_qty, _chiron_scalar, _chiron_vec"
  - "tests/ephemeris/__init__.py: new test subpackage marker"
  - "tests/ephemeris/test_chiron_unit.py: 7 unit tests at 100% chiron.py coverage"

affects:
  - 24-03 (imports _chiron_scalar, _chiron_vec to register in BODY_STRATEGIES)
  - 24-04 (accuracy regression uses _chiron_scalar via calc_planet_position)
  - 24-05 (smoke tests exercise the registered Chiron body)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "importlib.resources.files('ketu.data').joinpath('chiron_coeffs.npz').open('rb') — zipimport-safe .npz loader"
    - "@lru_cache(maxsize=1) on _load_chiron_data — .npz loaded once per interpreter session"
    - "jd_delta=0.01 finite-difference velocities — matches _make_planet_scalar pattern"
    - "aberration applied inside _chiron_vec — matches _make_planet_vec pattern for batch consistency"
    - "patch.object(_chiron_mod, '_eval_chiron_qty') mock to exercise unreachable 360° wrap branches"

key-files:
  created:
    - ketu/ephemeris/chiron.py
    - tests/ephemeris/__init__.py
    - tests/ephemeris/test_chiron_unit.py
  modified: []

key-decisions:
  - "aberration applied inside _chiron_vec (not left to caller) — matches _make_planet_vec byte-stability convention"
  - "dlon < -180 branch tested via mock, not via natural JDs — no natural 1950-2050 JD produces dlon<-180 in 0.01 days at Chiron speed"
  - "test_chiron_scalar_dlon_wrap_corrections uses patch.object to exercise both 360° wrap branches — avoids exclude_lines addition"

patterns-established:
  - "tests/ephemeris/ subpackage: future ephemeris-level unit tests go here"
  - "Defensive wrap branches in slow-body evaluators require mock-based coverage (no natural trigger in orbit data)"

# Metrics
duration: 5min
completed: 2026-05-29
---

# Phase 24 Plan 02: Chiron Evaluator Module Summary

**Pure-NumPy Chiron evaluator (importlib.resources + lru_cache + finite-diff velocities + per-element aberration) with 100% coverage via 7 unit tests including mock-based 360° wrap branch coverage**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-05-29T20:04:40Z
- **Completed:** 2026-05-29T20:10:00Z
- **Tasks:** 2/2
- **Files created:** 3

## Accomplishments

- `ketu/ephemeris/chiron.py` (235 lignes) — évaluateur pur-NumPy zéro-swisseph avec numpydoc complet
  - `_load_chiron_data()` : `@lru_cache(maxsize=1)` + `importlib.resources.files("ketu.data")` — AGPL-safe, zipimport-safe
  - `_eval_chiron_qty()` : évaluateur Chebyshev segment avec clamp JD hors-plage (max/min guards)
  - `_chiron_scalar()` : 6-tuple (lon,lat,dist,speeds) par différence finie `jd_delta=0.01`, wrap 360° correct
  - `_chiron_vec()` : boucle scalaire + aberration par élément (pattern `_make_planet_vec`)
- `tests/ephemeris/__init__.py` + `tests/ephemeris/test_chiron_unit.py` — 7 tests, chiron.py à 100% de couverture
- Suite complète : **1358 passed, 2 skipped, 100% total coverage** (inchangé depuis 24-01)

## Strategy Functions Exported (for plan 24-03)

```python
from ketu.ephemeris.chiron import _chiron_scalar, _chiron_vec

# Signatures (for BODY_STRATEGIES registration in planets.py):
# _chiron_scalar(jd: float) -> tuple[float, float, float, float, float, float]
#   Returns (lon, lat, dist, lon_speed, lat_speed, dist_speed)
#   lon in [0, 360), velocities in units/day
#   NO aberration applied (consistent with other scalar strategies)
#
# _chiron_vec(jd_array: np.ndarray) -> tuple[np.ndarray, ...]
#   Returns 6 arrays, aberration ALREADY APPLIED internally
#   (matches _make_planet_vec convention)
```

## Task Commits

1. **Task 1: Write ketu/ephemeris/chiron.py evaluator module** — `3e68b99` (feat)
2. **Task 2: Write unit tests for the evaluator** — `7ce12c7` (feat)

## Files Created/Modified

- `/home/loc/workspace/ketu/ketu/ephemeris/chiron.py` — Évaluateur pur-NumPy, 4 fonctions publiques, numpydoc complet, zero swisseph
- `/home/loc/workspace/ketu/tests/ephemeris/__init__.py` — Marqueur de sous-package vide
- `/home/loc/workspace/ketu/tests/ephemeris/test_chiron_unit.py` — 7 tests couvrant loader, éval, clamp ×2, vec/scalar consistency, wrap branches ×2, ratchet AGPL

## Decisions Made

- **Aberration dans `_chiron_vec`** : appliquée en interne pour matcher le pattern `_make_planet_vec` — sans ça, le chemin batch différerait du chemin scalaire de ~20 arcsec (dans le budget 0.01° mais incohérent).
- **Branche `dlon < -180` testée par mock** : aucun JD naturel 1950-2050 ne produit ce cas (Chiron trop lent). Évite d'ajouter cette branche aux `exclude_lines` — préférable de la tester explicitement.
- **`inspect.getsource` + filtre lignes import** : le test AGPL ratchet vérifie uniquement les lignes `import`/`from`, pas les docstrings — évite les faux positifs sur les mentions documentaires de "pyswisseph".

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] test_no_swisseph_import initial failure — docstring mentions**
- **Found during:** Task 2 (test execution)
- **Issue:** `inspect.getsource` returns le module entier incluant les docstrings. Les docstrings mentionnent "pyswisseph" comme référence documentaire, déclenchant l'assertion.
- **Fix:** Filtrer les lignes source pour ne vérifier que les lignes commençant par `import` ou `from`.
- **Files modified:** tests/ephemeris/test_chiron_unit.py
- **Verification:** test_no_swisseph_import PASSED
- **Committed in:** `7ce12c7` (Task 2 commit)

**2. [Rule 2 - Missing Coverage] Branches dlon wrap non couvertes par JDs naturels**
- **Found during:** Task 2 (coverage report — 96% sur chiron.py, lignes 162, 164 manquantes)
- **Issue:** Les branches `dlon > 180` et `dlon < -180` ne sont déclenchées par aucun JD naturel 1950-2050 à `jd_delta=0.01` (Chiron trop lent). Le gate 100% coverage aurait échoué.
- **Fix:** Ajout d'un test `test_chiron_scalar_dlon_wrap_corrections` avec `patch.object` sur `_eval_chiron_qty` pour injecter des valeurs synthétiques (lon≈0°/lon1≈360° et vice versa).
- **Files modified:** tests/ephemeris/test_chiron_unit.py
- **Verification:** chiron.py 100% (49 Stmts, 0 Miss). Full suite 1358 passed, 100% total.
- **Committed in:** `7ce12c7` (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (1 bug / false positive, 1 missing coverage)
**Impact on plan:** Les deux corrections nécessaires pour la corectude des tests et le gate 100%. Aucun dépassement de périmètre.

## Issues Encountered

None — les deux deviations ont été détectées et corrigées inline pendant Task 2.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 24-03 peut démarrer : `_chiron_scalar` et `_chiron_vec` sont les strategy functions à enregistrer dans `BODY_STRATEGIES["Chiron"]` de `planets.py`
- Aucun test existant cassé (Chiron pas encore enregistré — body count inchangé à 13)
- Gate de couverture 100% maintenu : 1358 tests, 0 pragma

---
*Phase: 24-chiron*
*Completed: 2026-05-29*
