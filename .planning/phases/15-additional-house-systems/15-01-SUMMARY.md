---
phase: 15-additional-house-systems
plan: 01
subsystem: testing
tags: [numpy, swisseph, houses, snapshot, oracle, dtype, regiomontanus]

requires:
  - phase: 10-houses-module
    provides: SYSTEMS registry, _asc1 helper in koch.py, HOUSES_DTYPE U10, swe_oracle_armc oracle
  - phase: 14-chart-abstraction-foundation
    provides: doc gates ratchet (interrogate ≥95%, numpydoc), mypy --strict on ketu/houses/
provides:
  - HOUSES_DTYPE['system'] U16 capacity (fits 'regiomontanus' 13 chars)
  - _asc1 helper factorized in ketu/houses/_ecliptic.py (consumable by Koch + Regiomontanus)
  - SYSTEM_BYTES extended to 6 swisseph hsys codes (P/K/O/W/E/R)
  - scripts/snapshot_reference_charts.py (idempotent regen, --check drift detection)
  - tests/houses/fixtures/reference_charts.json v1.2-phase15-snapshot (10 charts × 6 systems = 60 blocks)
  - test_loaded_reference_snapshot_matches_oracle ratchets 6 systems (was 3)
  - test_dtype_string_field_capacity ratchets 6 system names (was 4)
affects: [15-02-whole-sign-equal, 15-03-regiomontanus, 15-04-cli-integration, 16-synastry, 17-composite, 18-solar-return]

tech-stack:
  added: []
  patterns:
    - "Idempotent JSON snapshot regen with sort_keys=True + trailing newline (deterministic byte-identical re-run)"
    - "Allow-listing in .gitignore for specific committed scripts under otherwise-ignored /scripts/ directory"
    - "Helper factorization to internal _ecliptic.py module (underscore-prefixed, consumed via from ._ecliptic import _asc1)"

key-files:
  created:
    - "scripts/snapshot_reference_charts.py"
    - ".planning/phases/15-additional-house-systems/15-01-SUMMARY.md"
  modified:
    - "ketu/houses/core.py (HOUSES_DTYPE U10→U16 + versionchanged docstring)"
    - "ketu/houses/_ecliptic.py (append _asc1 helper with extended docstring)"
    - "ketu/houses/koch.py (remove local _asc1 def, import from ._ecliptic)"
    - "tests/houses/conftest.py (extend SYSTEM_BYTES with W/E/R)"
    - "tests/houses/fixtures/reference_charts.json (regenerated 60 blocks, version v1.2-phase15-snapshot)"
    - "tests/houses/test_oracle_smoke.py (ratchet 3→6 systems in snapshot test)"
    - "tests/houses/test_dtype.py (ratchet 4→6 system names in capacity test)"
    - "CHANGELOG.md ([Unreleased] ### Changed entry on the U10→U16 bump)"
    - ".gitignore (allow-list scripts/snapshot_reference_charts.py)"

key-decisions:
  - "DTYPE bump U10→U16 chosen over rename to 'regio' (5 chars) — preserves canonical 'regiomontanus' name, non-breaking per NumPy implicit U10⇄U16 cast (D-01)"
  - "_asc1 extracted to ketu/houses/_ecliptic.py rather than duplicated — DRY win for Plan 15-03 (Regiomontanus reuses identical formula with pole-height parameter) (D-05)"
  - "scripts/snapshot_reference_charts.py committed (was aspirational reference in conftest.py:248-252) — paired .gitignore allow-list keeps the rest of /scripts/ ignored (D-06)"
  - "Snapshot uses sort_keys=True + trailing newline for byte-identical re-runs (idempotency invariant)"
  - "All 6 systems iterated on every regen (Pitfall 6 mitigation) — single SYSTEM_BYTES dict in script, no NEW_SYSTEMS / OLD_SYSTEMS partition"

patterns-established:
  - "Idempotent snapshot regen: deterministic JSON formatting + --check flag for CI drift detection"
  - "Internal helper factorization via _ecliptic.py: callers within ketu.houses import via 'from ._ecliptic import name'; underscore prefix signals 'do not depend on this from outside ketu.houses'"
  - "DTYPE bump with versionchanged docstring annotation + CHANGELOG [Unreleased] ### Changed entry"

requirements-completed: [HOU2-05]

duration: 6min
completed: 2026-05-09
---

# Phase 15 Plan 01: Foundation — DTYPE U16, _asc1 Extraction, Snapshot Regen Script Summary

**Foundation pour Phase 15 : DTYPE bump U10→U16, factorisation `_asc1`, et snapshot regen script idempotent — Wave 2 (Plans 02/03/04) peut désormais tester les 3 nouveaux systèmes contre le snapshot et réutiliser `_asc1` sans duplication.**

## Performance

- **Duration:** ~6 min
- **Started:** 2026-05-09T07:18:27Z
- **Completed:** 2026-05-09T07:24:24Z
- **Tasks:** 6 (5 implementation + 1 régression complète)
- **Files modified:** 9 (1 created, 8 modified)

## Accomplishments

- `HOUSES_DTYPE['system']` étendu de U10 à U16 — `"regiomontanus"` (13 chars) tient sans troncature, comparaisons par contenu inchangées (NumPy cast U10⇄U16 transparent).
- `_asc1` (helper de projection grand-cercle vers longitude écliptique) déplacé de `ketu/houses/koch.py` vers `ketu/houses/_ecliptic.py` ; `koch.py` consomme via `from ._ecliptic import _asc1`. Comportement identique : 22/22 tests Koch verts.
- `tests/houses/conftest.py:SYSTEM_BYTES` étendu avec `b"W"` / `b"E"` / `b"R"` (Whole Sign / Equal / Regiomontanus) — l'oracle swisseph supporte les 3 nouveaux systèmes avant même que Plans 15-02/03 ne livrent les implémentations Ketu.
- `scripts/snapshot_reference_charts.py` créé : régénération idempotente (sort_keys=True + trailing newline) de `tests/houses/fixtures/reference_charts.json`, support `--check` pour détecter la dérive sans écrire. Remplace la référence aspirationnelle de `conftest.py:248-252` jamais committée en v1.1.
- `tests/houses/fixtures/reference_charts.json` régénéré : 10 charts × 6 systèmes = 60 blocs, top-level `version: "v1.2-phase15-snapshot"`, format `{meta, systems}` par chart. 1241 lignes (était 641 lignes pour 30 blocs).
- `test_loaded_reference_snapshot_matches_oracle` itère les 6 systèmes (était 3) → 60 comparaisons à 1e-9° tolérance par run.
- `test_dtype_string_field_capacity` ratchet 6 noms (était 4) — incluant `"regiomontanus"` (13 chars) qui aurait été tronqué silencieusement avant le bump.

## Task Commits

Chaque tâche est commitée atomiquement :

1. **Task 1: DTYPE bump U10→U16 + CHANGELOG + test ratchet** — `f7eef3b` (feat)
2. **Task 2: Extraction _asc1 vers _ecliptic.py** — `9fe6f44` (refactor)
3. **Task 3: Extension SYSTEM_BYTES (W/E/R)** — `68e8590` (test)
4. **Tasks 4+5: Snapshot regen script + JSON regeneration + test ratchet 6 systèmes** — `57c0e76` (feat)

Task 6 (régression Phase 10 complète) ne produit pas de commit dédié — c'est une vérification : `pytest tests/houses/ -x` passe à 156/156, `pytest tests/ -x` passe à 858/858.

**Plan metadata:** [à venir au commit final]

## Files Created/Modified

### Created

- `scripts/snapshot_reference_charts.py` (255 lignes) — script de régénération du snapshot ; idempotent ; `--check` pour drift detection ; itère 10 charts × 6 systèmes via `swe.houses_ex`.

### Modified

- `ketu/houses/core.py` — `HOUSES_DTYPE['system']` U10→U16 ; ajout d'un bloc `versionchanged:: v1.2 (Phase 15)` au docstring.
- `ketu/houses/_ecliptic.py` — append de `_asc1(x, lat, sin_eps, cos_eps)` ; docstring étoffé pour expliciter la convention pole-height vs geographic-latitude (Pitfall 4 RESEARCH).
- `ketu/houses/koch.py` — suppression de la définition locale `_asc1` (lignes 44-89 de l'ancien fichier) ; ajout de `from ._ecliptic import _asc1` au top. 4 call sites inchangés.
- `tests/houses/conftest.py` — `SYSTEM_BYTES` étendu de 3 à 6 entrées (`whole_sign`/`equal`/`regiomontanus` → `W`/`E`/`R`) ; commentaire de table actualisé.
- `tests/houses/fixtures/reference_charts.json` — régénéré avec 60 blocs ; clé top-level `version` ajoutée ; sous-clé `meta` introduite par chart.
- `tests/houses/test_oracle_smoke.py` — ligne 84 : tuple `("placidus", "koch", "porphyry")` → `("placidus", "koch", "porphyry", "whole_sign", "equal", "regiomontanus")`.
- `tests/houses/test_dtype.py` — `test_dtype_string_field_capacity` ratchet les 6 noms ; docstring met à jour la promesse U10→U16.
- `CHANGELOG.md` — entrée sous `[Unreleased] ### Changed` documentant le bump U10→U16 avec disclaimer non-breaking.
- `.gitignore` — `/scripts/` → `/scripts/*` + `!/scripts/snapshot_reference_charts.py` (allow-list spécifique pour ne pas tracker tout `/scripts/`).

## Decisions Made

- **DTYPE bump U10→U16 plutôt que renommage `regiomontanus` → `regio`** : préserve le nom canonique communauté astro / swisseph ; le cast NumPy implicite U10⇄U16 garantit la rétrocompatibilité ; aucune surface API publique modifiée.
- **`_asc1` factorisé vers `_ecliptic.py`** : Koch et Regiomontanus partagent rigoureusement la même formule `arctan2(cos(x-90), -(tan(lat)·sin(eps) + cos(eps)·sin(x-90)))` ; dupliquer aurait été un piège pour la maintenance future. Le sous-cas Regiomontanus passe la pole-height au paramètre `lat` au lieu de la latitude géographique — documenté dans la docstring.
- **Allow-list `.gitignore` plutôt que désactivation globale** : seul `snapshot_reference_charts.py` est exempté ; `precompute_ephemeris.py` reste local au développeur. Décision fine pour ne pas tracker accidentellement des scripts d'expérimentation.
- **Format JSON `{meta, systems}` par chart au lieu de `{systems}` plat** : préparation pour Plan 15-02/03 où les tests pourraient lire `meta.lat`, `meta.jd`, etc. directement depuis le snapshot ; le test ratchet existant continue de marcher (lit seulement `charts[label]["systems"]`).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `.gitignore` ignorait globalement `/scripts/`**

- **Found during:** Task 4 (création de `scripts/snapshot_reference_charts.py`)
- **Issue:** Le `.gitignore` ligne 6 contenait `/scripts/`, ignorant tout le dossier. Le plan demande explicitement de committer `scripts/snapshot_reference_charts.py` — sans modification du `.gitignore`, `git add` aurait été silencieux et le fichier n'aurait jamais été tracké.
- **Fix:** Modifié `/scripts/` → `/scripts/*` avec allow-list `!/scripts/snapshot_reference_charts.py`. Approche minimaliste qui préserve l'ignore sur le reste du dossier (notamment `precompute_ephemeris.py` qui n'est pas dans le scope de Phase 15).
- **Files modified:** `.gitignore`
- **Verification:** `git status --short scripts/snapshot_reference_charts.py` retourne `??` (untracked, donc visible), puis `git add` succède.
- **Committed in:** `57c0e76` (commit Task 4+5)

---

**Total deviations:** 1 auto-fixed (1 blocking issue)
**Impact on plan:** Le fix `.gitignore` est strictement nécessaire pour satisfaire le success criteria du plan (« script committé »). Pas de scope creep — l'allow-list est volontairement minimaliste (un seul fichier exempté).

## Issues Encountered

- **Lint warning MD024 sur CHANGELOG.md** (« Multiple headings with the same content `### Changed` ») : warning IDE, non-bloquant. Le format Keep a Changelog autorise et encourage l'usage du même nom de section dans plusieurs releases — c'est volontaire. Aucune action.
- **Coverage gate à 6.15% lors du test isolé `test_dtype.py`** : faux positif lié au mode coverage de pytest qui mesure la couverture sur l'ensemble du code base alors qu'on ne lance qu'un seul fichier de test. Vérifié par la régression complète : `pytest tests/ -x` passe 858/858 sans gate de couverture (mode --no-cov absent dans le pyproject de la régression).

## Verification Gates Passed

Tous les 13 gates du plan sont au vert :

1. ✅ U16 itemsize ≥ 64 bytes (UCS-4 × 16 chars)
2. ✅ `_asc1` location : 0 def dans koch.py, 1 def dans _ecliptic.py, 1 import dans koch.py
3. ✅ `SYSTEM_BYTES` = 6 entrées exactes
4. ✅ Snapshot script idempotent (`--check` retourne 0 après run normal)
5. ✅ JSON contient les 6 systèmes par chart
6. ✅ `test_loaded_reference_snapshot_matches_oracle` passe (60 comparaisons à 1e-9°)
7. ✅ `test_dtype_string_field_capacity` passe avec 6 noms
8. ✅ `pytest tests/houses/test_koch.py -x -v` passe (22/22)
9. ✅ `pytest tests/houses/ -x` passe (156/156)
10. ✅ `CHANGELOG.md` mentionne le bump (`grep -c "U10.*U16\|U16.*regiomontanus"` = 2)
11. ✅ `mypy --strict ketu/houses/` clean (Success: no issues found in 9 source files)
12. ✅ `interrogate ketu/houses/ -f 95` PASSED (100.0%, minimum 95%)
13. ✅ `numpydoc lint ketu/houses/_ecliptic.py ketu/houses/core.py` clean (sortie vide)

Régression complète : `pytest tests/ -x` → **858 passed**.

## User Setup Required

Aucun — ce plan ne nécessite aucune configuration externe ni secret.

## Next Phase Readiness

- ✅ Wave 2 débloqué : Plans 15-02 (Whole Sign + Equal), 15-03 (Regiomontanus), 15-04 (CLI integration) peuvent désormais s'appuyer sur la fondation.
- ✅ Plan 15-03 peut directement consommer `_asc1` via `from ._ecliptic import _asc1` (réutilisera la même formule avec pole-height au lieu de geographic latitude).
- ✅ Plans 15-02/03 peuvent comparer leurs implémentations Ketu contre le snapshot étendu (60 blocs) et contre `swe_oracle_armc` (qui supporte désormais les 3 nouveaux systèmes via SYSTEM_BYTES).
- ✅ Plan 15-04 dispose de `HOUSES_DTYPE['system']` U16 pour stocker `"regiomontanus"` retourné par `calculate_houses`.

Aucun blocker. Phase 15 Wave 2 prête à exécuter en parallèle (3 plans indépendants : 15-02, 15-03, 15-04).

## Self-Check: PASSED

Vérification post-écriture :

- ✅ FOUND: `/home/loc/workspace/ketu/scripts/snapshot_reference_charts.py`
- ✅ FOUND: `/home/loc/workspace/ketu/.planning/phases/15-additional-house-systems/15-01-SUMMARY.md` (ce fichier)
- ✅ FOUND: commit `f7eef3b` (Task 1)
- ✅ FOUND: commit `9fe6f44` (Task 2)
- ✅ FOUND: commit `68e8590` (Task 3)
- ✅ FOUND: commit `57c0e76` (Task 4+5)

---

*Phase: 15-additional-house-systems*
*Plan: 01-foundation-snapshot-dtype-asc1*
*Completed: 2026-05-09*
