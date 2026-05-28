---
status: complete
phase: 18-solar-lunar-returns
source: [18-01-SUMMARY.md, 18-02-SUMMARY.md, 18-03-SUMMARY.md, 18-04-SUMMARY.md, 18-05-SUMMARY.md]
started: 2026-05-28T00:00:00Z
updated: 2026-05-28T00:01:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Solar return — standard + relocated
expected: `solar_return(natal_jd, natal_lat, natal_lon, target_year)` retourne un CHART_DTYPE pour le moment de retour solaire résolu. `return_lat/lon` non-None → chart relocalisé (cusps changent, bodies non); None → lat/lon natals.
result: pass
note: "Fonctionnalité OK (CHART_DTYPE retourné, zéro NaN dans body_lons/cusps/asc/mc, relocation correcte). Un RuntimeWarning 'invalid value encountered in divide' (orbital.py:733, latitude héliocentrique inutilisée du Soleil à r=0) pollue le REPL mais est PRÉ-EXISTANT à Phase 18 — compute_chart (Phase 14) le déclenche déjà directement. Logged as cosmetic gap, hors périmètre Phase 18."

### 2. Lunar return — first return ≥ target_jd
expected: `lunar_return(natal_jd, natal_lat, natal_lon, target_jd)` retourne un CHART_DTYPE pour le PREMIER retour lunaire ≥ target_jd (période ~27.32 j). Le JD résolu est ≥ target_jd. Même contrat de relocation que solar_return.
result: pass

### 3. API asymmetry documented loudly
expected: `help(solar_return)` et `help(lunar_return)` distinguent clairement solar (target_year, calendar-anchored) vs lunar (target_jd, instant-anchored). Le mot-clé "asymmetry" apparaît dans au moins une docstring.
result: pass

### 4. Shared _solve_return — no inline bisection
expected: `solar_return` ET `lunar_return` délèguent au helper unique `ketu.returns._solve._solve_return`. Aucune boucle de bisection inline dans solar.py/lunar.py (Success Criterion #3).
result: pass

### 5. Arc-second convergence + natal/return lat-lon distinction
expected: La longitude du corps au moment résolu est à <1 arc-seconde de la cible natale (Sun ~1e-4°, Moon ~3e-4°). Les docstrings distinguent loudly natal_lat/lon (référence du corps natal) vs return_lat/lon (houses du retour).
result: pass

### 6. Oracle suite + pure-NumPy contract
expected: `make returns-coverage` passe à 100% (≥95% gate). 6 oracle fixtures (3 solar + 3 lunar incl. wrap-around + day-after-target). pyswisseph reste test-only; `ketu/returns/` n'importe jamais swisseph — Ketu runtime pur NumPy.
result: pass
note: "make returns-coverage passe à 100% (≥95% gate) LORSQUE le venv est activé. 6 fixtures présentes (solar: curie_1900, diana_1980, aries_seam_1970 wrap-around; lunar: diana_2000, pisces_seam_1990 wrap-around, curie_day_after). ketu/returns/ sans aucun import swisseph (pur NumPy ✓). L'échec initial `python: not found` venait de `make` lancé SANS venv activé — convention pré-existante Makefile:9 `PYTHON ?= python` (toutes les cibles), pas un défaut Phase 18; CLAUDE.md prescrit `source venv/bin/activate`."

## Summary

total: 6
passed: 6
issues: 0
pending: 0
skipped: 0

## Gaps

[no Phase 18 issues — all 6 tests passed]

## Out-of-scope observations (NOT Phase 18 gaps)

- truth: "Les appels solar_return/lunar_return n'émettent pas de RuntimeWarning au REPL"
  status: pre-existing
  reason: "RuntimeWarning 'invalid value encountered in divide' à orbital.py:733 (arcsin(z/r) avec r=0 pour le Soleil → latitude héliocentrique NaN, jamais utilisée). PRÉ-EXISTANT à Phase 18 : compute_chart (Phase 14) le déclenche déjà sur appel direct. Résultat correct (zéro NaN dans body_lons/cusps/asc/mc). Candidat nettoyage couche éphéméride, hors périmètre Phase 18."
  severity: cosmetic
  test: 1
- truth: "make returns-coverage tourne sans venv activé"
  status: by-design
  reason: "Échec `python: not found` quand make lancé hors venv. Convention pré-existante Makefile:9 `PYTHON ?= python` partagée par TOUTES les cibles coverage (composite/synastry/charts/houses). Avec venv activé, passe à 100%. CLAUDE.md prescrit `source venv/bin/activate`. Pas un défaut Phase 18."
  severity: minor
  test: 6
