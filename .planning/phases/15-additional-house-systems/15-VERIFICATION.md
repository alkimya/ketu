---
phase: 15-additional-house-systems
verified: 2026-05-09T08:27:19Z
status: passed
score: 13/13 must-haves verified
overrides_applied: 0
gaps: []
warnings:
  - description: "REQUIREMENTS.md ligne 24 indique HOU2-04 comme `[ ]` (incomplet) et ligne 116 indique `Pending`, mais le code, les tests et le SUMMARY 15-04 montrent que HOU2-04 est livré et vert. Cohérence documentaire à corriger (pas de régression code)."
    location: ".planning/REQUIREMENTS.md:24, :116"
    severity: doc
    fix: "Mettre à jour REQUIREMENTS.md : HOU2-04 → `[x]` ligne 24 et `Complete` ligne 116."
---

# Phase 15: Additional House Systems Verification Report

**Phase Goal:** Users select Whole Sign, Equal, or Regiomontanus through the existing SYSTEMS registry — proving the v1.1 extensibility claim — with each system validated against Swiss Ephemeris.

**Verified:** 2026-05-09T08:27:19Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| #  | Truth | Status | Evidence |
|----|-------|--------|----------|
| SC1 | `calculate_houses(jd, lat, lon, system='whole_sign'/'equal'/'regiomontanus')` retourne un `HOUSES_DTYPE` valide ; Whole Sign et Equal sont polar-safe (no NaN à lat=80°) | VERIFIED | Spot-check Python : les 3 systèmes retournent `cusps.shape=(12,)`, `system` field correct ; lat=80° produces no NaN pour whole_sign et equal (cusps[:3]=[330., 0., 30.] et [352.36, 22.36, 52.36]). Tests `test_calculate_houses_routes_whole_sign`, `test_calculate_houses_whole_sign_polar_safe_no_fallback_needed`, `test_calculate_houses_routes_equal`, `test_calculate_houses_equal_polar_safe_no_fallback_needed` PASSED. |
| SC2 | `ketu houses --list-house-systems` liste exactement 6 systèmes : placidus, koch, porphyry, whole_sign, equal, regiomontanus | VERIFIED | `python -m ketu --list-house-systems` retourne les 6 entrées triées alphabétiquement avec descriptions complètes (no `(no description available)` fallback). `test_lists_registered_systems`, `test_systems_listed_in_alphabetical_order`, `test_every_registered_system_has_description` PASSED. |
| SC3 | Chaque nouveau système passe la 10-reference-charts oracle suite vs Swiss Ephemeris | VERIFIED | `test_loaded_reference_snapshot_matches_oracle` PASSED (60 comparaisons à 1e-9° = 10 charts × 6 systèmes). Algorithm-tier oracle (1e-6°) PASSED pour whole_sign/equal/regiomontanus. Reykjavik drift mesuré empiriquement (0.86 arcmin) et pinned à 1.0' dans `REYKJAVIK_REGIO_TOL_ARCMIN`. |
| SC4 | `ketu houses --date ... --system whole_sign` (et equal/regiomontanus) imprime 12 cusps depuis le CLI sans code path additionnel | VERIFIED | Exécution réelle CLI confirmée : les 3 commandes produisent 12 House Cusps + ASC + MC formatés avec degrés/signes/minutes/secondes. Dispatcher dynamique via `choices=sorted(_HOUSE_SYSTEMS.keys())` ligne 135 de `parser.py` (pas de liste hardcodée). |

**Score:** 4/4 success criteria roadmap verified

### Must-Haves Across Plans

| #  | Must-Have | Plan | Status | Evidence |
|----|-----------|------|--------|----------|
| MH1 | `HOUSES_DTYPE['system']` = U16 (fits "regiomontanus") | 15-01 | VERIFIED | `core.py:46` `("system", "U16")`, itemsize=64 (UCS-4 × 16). |
| MH2 | `_asc1` factorisé dans `_ecliptic.py`, koch.py importe via `from ._ecliptic import _asc1` | 15-01 | VERIFIED | `_ecliptic.py:103 def _asc1`, `koch.py:33 from ._ecliptic import _asc1`. Aucune définition locale dans koch.py. |
| MH3 | Snapshot JSON contient 6 systèmes × 10 charts = 60 blocs avec version `v1.2-phase15-snapshot` | 15-01 | VERIFIED | JSON 33840 bytes, `version: v1.2-phase15-snapshot`, 10 charts, 60 system blocks total. Idempotency confirmé (`--check` retourne exit 0). |
| MH4 | `SYSTEM_BYTES` = 6 entrées swisseph (P/K/O/W/E/R) | 15-01 | VERIFIED | `conftest.py:80` dict avec les 6 paires correctes. |
| MH5 | whole_sign : cusps[0] = floor(asc/30)*30 ≠ asc | 15-02 | VERIFIED | Test `test_whole_sign_cusp_1_is_start_of_rising_sign` PASSED ; CLI output : ASC=181.6673° → cusps[0]=180.0° (sign floor Libra). |
| MH6 | equal : cusps[9] = (asc+270) mod 360 ≠ astro MC | 15-02 | VERIFIED | Test `test_equal_cusp_10_is_asc_plus_270_not_astronomical_mc` PASSED ; divergence > 1° à Paris J2000 (cusps[9]=91.67°, astro MC=92.10°, mais à 2025-06-21 Paris : equal cusps[9]=91.67° vs astro MC=92.10°, écart > 0). |
| MH7 | Regiomontanus polar-NaN à `|lat| ≥ 90 - eps`, `polar_fallback='porphyry'` route correctement | 15-03 | VERIFIED | Tests `test_regiomontanus_polar_lat_80_yields_all_nan`, `test_polar_fallback_routes_regiomontanus_to_porphyry`, `test_polar_fallback_raise_for_regiomontanus` PASSED. |
| MH8 | Pitfall 4 ratchet : `_asc1` dans regiomontanus.py reçoit pole heights, pas geo lat | 15-03 | VERIFIED | grep `_asc1\(` dans regiomontanus.py : 4 appels, tous reçoivent `pole_height_outer_deg` ou `pole_height_inner_deg` (lignes 131-134). |
| MH9 | Reykjavik drift mesuré empiriquement et pinné | 15-03 | VERIFIED | `REYKJAVIK_REGIO_TOL_ARCMIN = 1.0 * ARCMIN_DEG` ; mesure réelle 0.8581 arcmin imprimée par `test_regiomontanus_reykjavik_drift_measured_and_pinned`. |
| MH10 | Parser dispatcher dynamique : `choices=sorted(SYSTEMS.keys())` | 15-04 | VERIFIED | `parser.py:135 choices=sorted(_HOUSE_SYSTEMS.keys())`. Test runtime : `system choices: ['equal', 'koch', 'placidus', 'porphyry', 'regiomontanus', 'whole_sign']`. |
| MH11 | `_SYSTEM_DESCRIPTIONS` couvre les 6 systèmes (no fallback affiché) | 15-04 | VERIFIED | `introspection.py:22-29` 6 entrées. CLI output : aucun `(no description available)`. Test `test_every_registered_system_has_description` PASSED. |
| MH12 | `test_invalid_system_rejected` inversé : utilise `nonexistent_xyz` | 15-04 | VERIFIED | Confirmé par exécution `--system nonexistent_xyz` → exit 2 + message "invalid choice: 'nonexistent_xyz' (choose from equal, koch, placidus, porphyry, regiomontanus, whole_sign)". |
| MH13 | Test parametré 6 systèmes × 3 locations = 18 cases CLI matchent l'API Python | 15-04 | VERIFIED | `tests/cli/test_houses_cmd.py::TestHousesCmdMatchesPythonAPI::test_cli_cusps_match_python_api` parametré sur 6 systèmes (constaté dans l'exécution `298 passed` houses+cli). |

**Score:** 13/13 must-haves verified (sur l'agrégat des 4 plans)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `ketu/houses/whole_sign.py` | @register("whole_sign"), closed-form sign-floor | VERIFIED | 116 lignes, contient `@register("whole_sign")` ligne 38, formule sign-floor `np.floor(asc/30.0)*30.0` ligne 108. |
| `ketu/houses/equal.py` | @register("equal"), ASC-anchored 30° spacing | VERIFIED | 97 lignes, contient `@register("equal")` ligne 39, formule `(asc + 30k) mod 360` via offsets ligne 93. |
| `ketu/houses/regiomontanus.py` | @register("regiomontanus"), closed-form trig + polar NaN | VERIFIED | 154 lignes, contient `@register("regiomontanus")` ligne 58, pole_height_outer/inner explicit, polar mask ligne 118, NaN propagation lignes 149-151. |
| `ketu/houses/_ecliptic.py:_asc1` | Helper extracted from koch.py | VERIFIED | `def _asc1` ligne 103 ; consommé par koch.py:33 et regiomontanus.py:46. |
| `ketu/houses/__init__.py` | trigger imports placidus + koch + porphyry + whole_sign + equal + regiomontanus | VERIFIED | 6 trigger imports lignes 41-46. SYSTEMS = 6 entries au runtime. |
| `ketu/houses/api.py` | POLAR_SAFE_SYSTEMS frozenset = {porphyry, whole_sign, equal} | VERIFIED | `api.py:42-44` `POLAR_SAFE_SYSTEMS = frozenset({"porphyry", "whole_sign", "equal"})`. Polar gate utilise `not in POLAR_SAFE_SYSTEMS` ligne 147. |
| `ketu/houses/core.py:HOUSES_DTYPE` | system field U16 | VERIFIED | `("system", "U16")` ligne 46. |
| `ketu/cli/parser.py` | `choices=sorted(SYSTEMS.keys())` dynamique | VERIFIED | Ligne 135. Import ligne 17 `from ketu.houses import SYSTEMS as _HOUSE_SYSTEMS`. |
| `ketu/cli/introspection.py` | `_SYSTEM_DESCRIPTIONS` 6 entries | VERIFIED | Lignes 22-29. |
| `scripts/snapshot_reference_charts.py` | Idempotent regen | VERIFIED | Existe, --check retourne exit 0 ("matches live oracle output"). |
| `tests/houses/fixtures/reference_charts.json` | 10 charts × 6 systems = 60 blocs, version v1.2-phase15-snapshot | VERIFIED | Validé via `json.load` : version correcte, 60 blocks. |
| `tests/houses/test_whole_sign.py` | Algorithm-tier oracle 1e-6° + invariants + sign-floor + registry | VERIFIED | 9 tests PASSED (test_whole_sign.py exécuté). |
| `tests/houses/test_equal.py` | Algorithm-tier 1e-6° + 30°-spacing + cusp10≠MC + registry | VERIFIED | 9 tests PASSED. |
| `tests/houses/test_regiomontanus.py` | Two-tier oracle + Reykjavik pinned + polar contract | VERIFIED | 16 tests PASSED, Reykjavik drift = 0.8581' affiché. |
| `tests/cli/test_houses_cmd.py` | test_invalid inverted, test_v12_systems_accepted, parametrized 6×3 | VERIFIED | 25 tests PASSED. |
| `tests/cli/test_introspection.py` | TestListHouseSystems étendu (4 tests) | VERIFIED | 8 tests PASSED. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `ketu/cli/parser.py` | `ketu.houses.SYSTEMS` | `from ketu.houses import SYSTEMS as _HOUSE_SYSTEMS` ligne 17 + `choices=sorted(_HOUSE_SYSTEMS.keys())` ligne 135 | WIRED | Runtime check : choices= 6 systèmes triés. |
| `ketu/houses/__init__.py` | `whole_sign`/`equal`/`regiomontanus` modules | trigger imports ligne 44-46 | WIRED | `import ketu.houses` peuple SYSTEMS avec 6 entrées (vérifié via `len(SYSTEMS)==6`). |
| `ketu/houses/regiomontanus.py` | `ketu/houses/_ecliptic.py:_asc1` | `from ._ecliptic import _asc1` ligne 46 | WIRED | 4 appels `_asc1(...)` à lignes 131-134. |
| `ketu/houses/koch.py` | `ketu/houses/_ecliptic.py:_asc1` | `from ._ecliptic import _asc1` ligne 33 | WIRED | 4 appels à lignes 110-113 ; régression Phase 10 verte (22 tests koch). |
| `ketu/houses/api.py:147` polar gate | `POLAR_SAFE_SYSTEMS` frozenset | `not in POLAR_SAFE_SYSTEMS` substituant la check `!= "porphyry"` v1.1 | WIRED | `calculate_houses(jd, 80, 0, system="whole_sign")` ne lève plus HighLatitudeError. |
| `tests/houses/conftest.py:SYSTEM_BYTES` | swisseph hsys table | dict mapping 6 systèmes vers `b"P/K/O/W/E/R"` | WIRED | `swe_oracle_armc` consomme le mapping correctement (algorithm-tier tests verts). |
| `scripts/snapshot_reference_charts.py` | `tests/houses/fixtures/reference_charts.json` | `swe.houses_ex` itère 6 systèmes × 10 charts | WIRED | Idempotency `--check` exit 0. |
| `ketu/cli/introspection.py:cmd_list_house_systems` | `_SYSTEM_DESCRIPTIONS` | `_SYSTEM_DESCRIPTIONS.get(name, "(no description available)")` itère `sorted(_HOUSE_SYSTEMS.keys())` | WIRED | CLI output liste 6 systèmes avec descriptions, aucun fallback affiché. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `whole_sign_cusps` output | `cusps` array (..., 12) | `np.broadcast_arrays(armc, lat, eps)` + sign-floor closed-form | Yes (12 valeurs distinctes par chart) | FLOWING |
| `equal_cusps` output | `cusps` array | broadcast + (asc + 30k) mod 360 | Yes (12 valeurs ASC-anchored) | FLOWING |
| `regiomontanus_cusps` output | `cusps` array via `_asc1` calls × 4 + opposites | `_asc1` from `_ecliptic.py` (closed-form trig per swehouse case 'R') | Yes (4 cusps non-trivial + 4 opposites + 4 angles) ; NaN propagation au polar | FLOWING |
| CLI `--list-house-systems` output | listing dict | `sorted(_HOUSE_SYSTEMS.keys())` itère SYSTEMS registry réel | Yes (6 systèmes triés alphabétiquement) | FLOWING |
| CLI `houses --system X` cusps | cusps formatés | `calculate_houses(...)` → `cmd_houses` formatage | Yes (12 cusps + ASC + MC affichés en deg/sign/min/sec) | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Module imports + SYSTEMS registry | `python -c "from ketu.houses import SYSTEMS; print(sorted(SYSTEMS.keys()))"` | `['equal', 'koch', 'placidus', 'porphyry', 'regiomontanus', 'whole_sign']` | PASS |
| HOUSES_DTYPE U16 | `python -c "from ketu.houses import HOUSES_DTYPE; print(HOUSES_DTYPE.fields['system'][0].itemsize)"` | `64` (UCS-4 × 16 chars) | PASS |
| Whole Sign at lat=80° (polar-safe) | `calculate_houses(2451545.0, 80.0, 0.0, system='whole_sign')` | cusps finite, no NaN | PASS |
| Equal at lat=80° (polar-safe) | `calculate_houses(2451545.0, 80.0, 0.0, system='equal')` | cusps finite, no NaN | PASS |
| Regiomontanus + polar_fallback | `calculate_houses(2451545.0, 80.0, 0.0, system='regiomontanus', polar_fallback='porphyry')` | cusps finite via Porphyry substitution | PASS |
| CLI --list-house-systems | `python -m ketu --list-house-systems` | 6 systèmes triés alphabétiquement, descriptions complètes | PASS |
| CLI houses --system whole_sign | `python -m ketu houses --date 2025-06-21T12:00:00Z --lat 48.85 --lon 2.35 --system whole_sign` | 12 cusps + ASC + MC formatés (sign-floor Libra→Virgo, multiples de 30°) | PASS |
| CLI houses --system equal | idem `--system equal` | 12 cusps + ASC + MC (cusps[0]=ASC=181.67°, écart 30°) | PASS |
| CLI houses --system regiomontanus | idem `--system regiomontanus` | 12 cusps + ASC + MC (cusps non-trivial via _asc1) | PASS |
| CLI invalid system rejected | `python -m ketu houses ... --system nonexistent_xyz` | exit 2, "invalid choice: 'nonexistent_xyz' (choose from equal, koch, placidus, porphyry, regiomontanus, whole_sign)" | PASS |
| Snapshot idempotency | `python scripts/snapshot_reference_charts.py --check` | exit 0, "matches live oracle output" | PASS |
| Reykjavik drift measured | `pytest test_regiomontanus_reykjavik_drift_measured_and_pinned -s` | "Reykjavik Regiomontanus drift: max=0.8581'" | PASS |
| Full test suite | `pytest tests/ --no-cov` | 909 passed, 113 warnings, 15.71s | PASS |
| Houses + CLI test subset | `pytest tests/houses/ tests/cli/ --no-cov` | 298 passed (incluant 16 regiomontanus, 9 whole_sign, 9 equal, 25 houses_cmd, 8 introspection) | PASS |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|----------------|-------------|--------|----------|
| HOU2-01 | 15-02 | Whole Sign houses — chaque maison = un signe, démarrant au signe de l'ASC ; polar-safe ; enregistré dans SYSTEMS | SATISFIED | Module `whole_sign.py` avec `@register("whole_sign")`, 9 tests verts, polar-safe à lat=80° confirmé. |
| HOU2-02 | 15-02 | Equal houses — cusps espacés de 30° depuis l'ASC ; polar-safe ; enregistré dans SYSTEMS | SATISFIED | Module `equal.py` avec `@register("equal")`, 9 tests verts, polar-safe à lat=80° confirmé. |
| HOU2-03 | 15-03 | Regiomontanus houses — division de l'équateur céleste projetée via le prime vertical ; enregistré dans SYSTEMS | SATISFIED | Module `regiomontanus.py` avec `@register("regiomontanus")`, 16 tests verts, NaN polar + polar_fallback intégration validés, Reykjavik drift pinné à 1.0' (0.86' mesuré). |
| HOU2-04 | 15-04 | `--list-house-systems` retourne désormais placidus, koch, porphyry, whole_sign, equal, regiomontanus (5+ systèmes) | SATISFIED | Code, CLI runtime et tests confirment 6 systèmes affichés alphabétiquement. **NOTE doc-only**: REQUIREMENTS.md ligne 24 et 116 indiquent encore `[ ]`/`Pending` — incohérence documentaire à corriger (warning, pas blocker). |
| HOU2-05 | 15-01, 15-02, 15-03, 15-04 | Chaque nouveau système validé contre Swiss Ephemeris sur les 10 reference charts ; max ASC delta documenté | SATISFIED | Snapshot 10 charts × 6 systèmes ratcheté à 1e-9° (`test_loaded_reference_snapshot_matches_oracle`). Algorithm-tier oracle bit-exact 1e-6° pour les 3 nouveaux systèmes. Reykjavik drift max documenté inline (0.8581'). |

**Toutes les requirements IDs sont SATISFIED.** Aucune orpheline.

### Anti-Patterns Found

Scan ciblé sur les fichiers Phase 15 (`whole_sign.py`, `equal.py`, `regiomontanus.py`, `_ecliptic.py:_asc1`, `parser.py`, `introspection.py`, `snapshot_reference_charts.py`).

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | — | — | — | Aucun TODO/FIXME/PLACEHOLDER laissé dans le code production Phase 15. Aucun `return null/return []/return {}` non justifié. Aucun handler `onSubmit={(e)=>e.preventDefault()}` (pas de surface UI ici). Stub patterns absents. |

Note : `MAX_ITER` et `TOL_DEG` dans `regiomontanus.py:52,55` sont des constants documentés "reserved for future iterative variants" pour parité API avec Placidus — ce n'est pas du code mort, c'est une convention. Test `test_regiomontanus_constants_unchanged` ratchet ces valeurs.

### Human Verification Required

Aucun item nécessitant une vérification humaine. Tous les success criteria sont vérifiables programmatiquement (CLI execution, oracle suite, dtype shape, NaN absence) et tous ont été validés par exécution directe.

### Gaps Summary

**Aucun gap bloquant.** Phase 15 est complète et la goal du roadmap est atteinte :

- Les 3 nouveaux house systems (Whole Sign, Equal, Regiomontanus) sont implémentés, enregistrés dans `SYSTEMS`, et accessibles via l'API Python ET le CLI Ketu sans aucun code dispatch additionnel.
- L'extensibilité v1.1 est démontrée : le parser `--system` apprend dynamiquement via `choices=sorted(SYSTEMS.keys())` ; le test ratchet `test_every_registered_system_has_description` empêche la régression sur la cohérence registry↔descriptions.
- Validation Swiss Ephemeris : les 6 systèmes passent la suite oracle 10-charts à 1e-9° (snapshot ratchet) ; algorithm-tier bit-exact 1e-6° pour les 3 nouveaux ; Reykjavik drift mesuré empiriquement (0.8581 arcmin) et pinné conservativement à 1.0 arcmin.
- 909/909 tests verts (était 858 avant Phase 15 → +51 nouveaux tests).
- Documentation gates Phase 13 verts (interrogate 100%, numpydoc lint clean) ; mypy --strict clean sur ketu/houses/ et ketu/cli/.

### Warning (non-blocker)

**REQUIREMENTS.md incohérence documentaire** : HOU2-04 est marqué `[ ]` ligne 24 et `Pending` ligne 116, alors que le code/tests/SUMMARY 15-04 confirment l'achèvement. À corriger en mettant à jour les deux lignes (`[x]` et `Complete`). Aucun impact sur le code livré ; le ROADMAP.md ligne 241 a déjà été mis à jour ("Phase 15 complete (4/4 plans, HOU2-01..05 satisfied, 909 tests, 6 systems registered)").

---

_Verified: 2026-05-09T08:27:19Z_
_Verifier: Claude (gsd-verifier, persona Sophie Chen)_
