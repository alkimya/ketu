---
phase: 24-chiron
plan: 03
subsystem: ephemeris, charts, synastry, composite, cache, aspects, packaging
tags: [chiron, breaking-change, bodies-axis, 13-to-14, dtype, packaging, npz]

# Dependency graph
requires:
  - phase: 24-chiron/24-02
    provides: _chiron_scalar, _chiron_vec strategy functions (ketu/ephemeris/chiron.py)
  - phase: 24-chiron/24-01
    provides: ketu/data/chiron_coeffs.npz (1142 segments)

provides:
  - "calc_planet_position(jd, 13) returns Chiron via BODY_STRATEGIES['Chiron']"
  - "CHART_DTYPE with (14,) and (14,14) subarrays"
  - "ketu.data packaged (pyproject packages + package-data *.npz)"
  - "Full test suite green at 14 bodies (1361 passed, 100% coverage)"

affects:
  - 24-04 (accuracy regression uses calc_planet_position(jd, 13))
  - 24-05 (smoke tests exercise registered Chiron body)
  - 26 (CHANGELOG + UPGRADING 13→14 positional contract note)
  - Kala downstream (positional array contract 13→14 breaking change)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "BODY_STRATEGIES['Chiron'] = _BodyCalc(_chiron_scalar, _chiron_vec) — single per-body entry, no special-casing (CHIR-05)"
    - "SWE_IDS auto-range: range(len(SWE_IDS)) in transits.py auto-tracks body count"
    - "_BODY_ORBS_16 replaces _BODY_ORBS_15 (16 entries: 14 canonical + ASC + MC)"
    - "ketu.data in pyproject packages + package-data *.npz + MANIFEST.in recursive-include"

key-files:
  modified:
    - ketu/ephemeris/planets.py
    - ketu/core.py
    - ketu/charts/api.py
    - ketu/charts/core.py
    - ketu/composite/api.py
    - ketu/cache/ephemeris_cache.py
    - ketu/synastry/core.py
    - ketu/synastry/orbs.py
    - ketu/synastry/api.py
    - ketu/aspects/transits.py
    - pyproject.toml
    - MANIFEST.in
    - tests/test_ketu.py
    - tests/charts/test_dtype.py
    - tests/charts/test_compute_chart.py
    - tests/charts/test_compute_chart_vectorisation.py
    - tests/charts/test_aspect_matrix.py
    - tests/composite/test_dtype.py
    - tests/composite/test_calculate_composite.py
    - tests/synastry/test_dtype.py
    - tests/synastry/test_calculate_synastry.py
    - tests/synastry/test_applying.py
    - tests/synastry/test_modes_idempotent.py
    - tests/synastry/test_orbs.py
    - tests/synastry/test_oracle.py
    - tests/cli/test_synastry_cmd.py
    - tests/cli/fixtures/v1_1_reference_output.txt
    - tests/test_planets_coverage.py
    - tests/test_transits.py
    - tests/test_transits_coverage.py
    - tests/test_cache_ephemeris.py
    - tests/test_cache_coverage.py
    - tests/test_aspects_vectorization.py
    - tests/test_error_messages.py

key-decisions:
  - "Chiron wired via single BODY_STRATEGIES entry — no special-casing anywhere (CHIR-05 satisfied)"
  - "_BODY_ORBS_15 renamed to _BODY_ORBS_16 in source; _BODY_ORBS_15 alias preserved for test backward compat then removed"
  - "cli/fixtures/v1_1_reference_output.txt updated (not byte-frozen to pre-Chiron) — test re-pinned to post-v1.3 reference"
  - "Dense synastry mode: 15×15=225→16×16=256 rows; all dense-count tests updated"
  - "test_body_count_frozen_at_thirteen renamed to test_body_count_frozen_at_fourteen (ratchet advanced)"

# Metrics
duration: 18min
completed: 2026-05-29
---

# Phase 24 Plan 03: Bodies Axis 13→14 Breaking Change Summary

**Chiron wired at all 6 insertion points (BODY_INDICES/SWE_IDS/BODY_STRATEGIES/avg_speeds/core.bodies/docstrings); CHART_DTYPE/composite/cache/synastry/transits updated to 14 bodies; ketu.data packaged; 1361 tests green at 14 bodies, 100% coverage**

## Performance

- **Duration:** ~18 min
- **Started:** 2026-05-29T20:14:01Z
- **Completed:** 2026-05-29T20:31:40Z
- **Tasks:** 3/3
- **Source files modified:** 12
- **Test files modified:** 22

## Old→New Values Changed (for Phase 26 UPGRADING note)

### Source-side dtype/shape/count constants

| File | Constant / Field | Old | New |
|------|-----------------|-----|-----|
| `ketu/ephemeris/planets.py` | `BODY_INDICES` | no Chiron | `"Chiron": 13` |
| `ketu/ephemeris/planets.py` | `SWE_IDS` | no index 13 | `13: "Chiron"` |
| `ketu/ephemeris/planets.py` | `BODY_STRATEGIES` | 13 entries | `"Chiron": _BodyCalc(...)` |
| `ketu/ephemeris/planets.py` | `avg_speeds` | 12 (index) | `13: 0.01946` |
| `ketu/ephemeris/planets.py` | error msg / docstring | `0-12` | `0-13` |
| `ketu/core.py` | `bodies` array len | 13 | 14 |
| `ketu/core.py` | module docstring | "13 bodies", id 0-12 | "14 bodies", id 0-13 + Chiron |
| `ketu/charts/core.py` | `CHART_DTYPE body_lons/lats/speeds` | `(13,)` | `(14,)` |
| `ketu/charts/core.py` | `CHART_DTYPE aspect_matrix/orbs` | `(13,13)` | `(14,14)` |
| `ketu/composite/api.py` | `_BODY_COUNT` | `13` | `14` |
| `ketu/cache/ephemeris_cache.py` | `BODY_COUNT` | `13` | `14` |
| `ketu/cache/ephemeris_cache.py` | `BODY_IDS` | no Chiron | `"Chiron": 13` |
| `ketu/synastry/core.py` | `SYNASTRY_BODY_COUNT` | `15` | `16` |
| `ketu/synastry/orbs.py` | `_BODY_ORBS_15` → `_BODY_ORBS_16` | shape `(15,)` | shape `(16,)` |
| `ketu/aspects/transits.py` | `list(range(13))` | hardcoded | `list(range(len(SWE_IDS)))` |

### Synastry axis index shift (Chiron at 13 shifts ASC/MC)

| Element | Old index | New index |
|---------|-----------|-----------|
| ASC | 13 | 14 |
| MC  | 14 | 15 |
| Dense mode size | 15×15 = 225 | 16×16 = 256 |

### Packaging

| File | Addition |
|------|---------|
| `pyproject.toml` | `packages += "ketu.data"` |
| `pyproject.toml` | `[tool.setuptools.package-data] "ketu.data" = ["*.npz"]` |
| `MANIFEST.in` | `recursive-include ketu/data *.npz` |

## Task Commits

1. **Task 1: Wire Chiron at all 6 insertion points** — `74db466` (feat)
2. **Task 2: 13→14 bodies-axis ripple — dtype/shape/count + packaging** — `24fdad3` (feat)
3. **Task 3: Ratchet all test body-count/axis-index assertions to 14 bodies** — `66f13c8` (feat)

## Verification Results

- `pytest tests/ -q` : **1361 passed, 2 skipped, 0 failed, 100% coverage** (suite was 1358 before plan — +3 net)
- `grep -rn "import swisseph" ketu/` : vide (AGPL ratchet respecté)
- `grep -rn "frozen_at_thirteen" tests/` : vide (ratchet renommé → _fourteen)
- `grep -n "== 13\b" tests/charts/test_dtype.py` : seule la ligne Opposition (aspect index 169) — conforme
- `calc_planet_position(2451545.0, 13)` → lon `251.61°` (Chiron, J2000.0)
- `len(ketu.core.bodies)` → `14`
- `CHART_DTYPE['body_lons'].shape` → `(14,)`
- `CHART_DTYPE['aspect_matrix'].shape` → `(14, 14)`
- `SYNASTRY_BODY_COUNT` → `16`
- `BODY_COUNT` (cache) → `14`, `BODY_IDS['Chiron']` → `13`
- `tomllib.load(pyproject.toml)['tool']['setuptools']['packages']` contient `'ketu.data'`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Tests supplémentaires hors liste du plan avec assertions sur body count**
- **Found during:** Task 3 (first full test run — 50 tests failed, plan listed ~25)
- **Issue:** Le plan listait les principaux fichiers de tests mais pas tous. 25 autres tests dans `test_compute_chart_vectorisation.py`, `composite/test_dtype.py`, `cli/test_synastry_cmd.py`, `cli/fixtures/v1_1_reference_output.txt`, `test_aspects_vectorization.py`, `test_cache_ephemeris.py`, `test_cache_coverage.py`, `test_error_messages.py`, `synastry/test_oracle.py`, `synastry/test_modes_idempotent.py`, `synastry/test_applying.py` contenaient aussi des assertions sur l'ancien count.
- **Fix:** Correction de chaque assertion conformément à la même logique de ratchet (13→14, ASC/MC 13/14→14/15, dense 225→256).
- **Files modified:** (listés dans key-files ci-dessus)
- **Verification:** 1361 tests verts, 0 pragma, 100% coverage

**2. [Rule 1 - Bug] _BODY_ORBS_15 dans synastry/orbs.py et synastry/api.py**
- **Found during:** Task 3 (synastry/test_orbs.py failures)
- **Issue:** `_BODY_ORBS_15` était construit à partir de `_BODIES["orb"]` (shape 13) + 2 → shape (15,). Après l'ajout de Chiron, `_BODIES["orb"]` a shape 14 donc la table devient (16,). Tous les tests vérifiant shape (15,) et les indices ASC/MC [13]/[14] auraient échoué.
- **Fix:** Renommer `_build_body_orbs_15` → `_build_body_orbs_16`, `_BODY_ORBS_15` → `_BODY_ORBS_16` dans source + alias `_BODY_ORBS_15 = _BODY_ORBS_16` pour les imports existants. Mettre à jour synastry/api.py import + usage.
- **Files modified:** `ketu/synastry/orbs.py`, `ketu/synastry/api.py`
- **Committed in:** 66f13c8 (Task 3)

**3. [Rule 1 - Bug] CLI fixture v1_1_reference_output.txt byte-stable test**
- **Found during:** Task 3
- **Issue:** Le test `test_harmonics_all_byte_identical_to_v1_1_reference` compare stdout byte-for-byte avec une référence pre-Chiron. Avec Chiron dans les positions, la sortie diverge légitimement (ligne "Chiron : Sagittarius 11º36'45"" + aspects Saturn-Chiron + Pluto-Chiron).
- **Fix:** Régénérer le fichier fixture `tests/cli/fixtures/v1_1_reference_output.txt` avec la nouvelle sortie post-Chiron. Le test reste un "self-stable forward contract" (cf. son docstring).
- **Files modified:** `tests/cli/fixtures/v1_1_reference_output.txt`
- **Committed in:** 66f13c8 (Task 3)

---

**Total deviations:** 3 auto-fixed (Rule 1 — bugs / incomplete spec)
**Impact on plan:** Aucun dépassement de périmètre. Tous les fichiers modifiés sont la conséquence directe et attendue du breaking change 13→14.

## Self-Check: PASSED

### Files created/modified check

- `ketu/ephemeris/planets.py` — FOUND (modified)
- `ketu/core.py` — FOUND (modified)
- `ketu/charts/core.py` — FOUND (modified)
- `ketu/charts/api.py` — FOUND (modified)
- `ketu/composite/api.py` — FOUND (modified)
- `ketu/cache/ephemeris_cache.py` — FOUND (modified)
- `ketu/synastry/core.py` — FOUND (modified)
- `ketu/aspects/transits.py` — FOUND (modified)
- `pyproject.toml` — FOUND (modified)
- `MANIFEST.in` — FOUND (modified)

### Commits check

- `74db466` — Task 1 (feat(24-03): wire Chiron at all 6 insertion points)
- `24fdad3` — Task 2 (feat(24-03): 13→14 bodies-axis ripple)
- `66f13c8` — Task 3 (feat(24-03): ratchet all test body-count/axis-index assertions)

### Suite check

- 1361 passed, 2 skipped, 0 failed, 100% coverage ✓
- No swisseph import in ketu/ ✓
- frozen_at_thirteen → frozen_at_fourteen ✓

---
*Phase: 24-chiron*
*Completed: 2026-05-29*
