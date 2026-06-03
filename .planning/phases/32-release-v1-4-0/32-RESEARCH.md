# Phase 32: Release v1.4.0 — Research

**Researched:** 2026-06-03
**Domain:** Python package release engineering — version bump, CHANGELOG authoring, UPGRADING,
PyPI OIDC publish ceremony (reuses v1.3.0 infra proven in Phase 27)
**Confidence:** HIGH (all claims verified against live repo files and live venv)

---

## Summary

Phase 32 is the FINAL phase of milestone v1.4 (Dynamic Harmonics & Chiron Range). All four
predecessor phases (28–31) are complete. The release infrastructure is proven from Phase 20
(v1.2.0) and Phase 27 (v1.3.0): `publish.yml` is wired, OIDC trusted publishing is configured
on PyPI, and the pre-flight pattern is documented.

This phase is MECHANICAL. There are no new features and no tooling changes. The two tasks the
roadmap stubs — 32-01 (version bump + CHANGELOG + UPGRADING + fr/CHANGELOG) and 32-02
(pre-flight + publish + smoke test) — map directly to REL-12 and REL-13.

**Gold-standard precedent:** Phase 27 (v1.3.0 release). This RESEARCH.md is structured
identically and flags every v1.4-specific delta from that precedent.

**Three concrete deltas from Phase 27 that make v1.4 non-trivial:**

1. **CHANGELOG must be authored fresh.** Unlike v1.3 (which merged two existing Unreleased
   sections), the root `CHANGELOG.md` has NO `[1.4.0]` section and NO `[Unreleased]` section.
   The `[1.4.0]` section must be written from scratch. The content source is
   `docs/source/changelog.md` which has a `## [1.4.0] - 2026-06-XX` block already written in
   Phase 31 — but with a date placeholder (`2026-06-XX`) that must be date-stamped at release.
   The root CHANGELOG and the docs changelog use **different formats** (root uses `### Added` /
   `### Changed`; docs uses `### Added 1.4.0` / `### Changed 1.4.0`).

2. **UPGRADING.md needs a `## v1.3 -> v1.4` section.** v1.4 has two behavioural changes that
   affect downstream consumers (Kala): Chiron orb 0°→4° (Chiron now forms scored aspects in
   all aspect-detection paths, so downstream aspect counts and scores can change), and
   Chiron out-of-range clamping instead of `ValueError` (silent behaviour change). Both warrant
   migration notes. The dynamic generator is purely additive and needs only a brief mention.

3. **Fresh-venv smoke test has three new v1.4 assertions** on top of the v1.3 ones:
   (a) `generate_harmonic_aspects(7)` returns 3 rows with correct H7 angles,
   (b) `core.bodies['orb']` for Chiron is 4.0,
   (c) `calc_planet_position(2422324.5, 13)` (JD for 1920-01-01, OUTSIDE the old 1950–2050
   range) returns a finite longitude — proving the new 1900–2100 range is active.

**Locked user constraint (feedback_validation_review_before_release):** The user personally
reviews the entire milestone BEFORE any irreversible action. Plan 32-02 MUST contain a
`type="checkpoint:human-verify" gate="blocking"` task BEFORE the tag push and PyPI publish.
An auto-publish flow is NOT acceptable.

**Primary recommendation:** Two sequential plans mirroring Phase 27:
- **32-01** (wave 1, autonomous): version bump + author root CHANGELOG.md `[1.4.0]` +
  sync fr/CHANGELOG.md + add UPGRADING `v1.3 -> v1.4` + update README `## What's New` +
  date-stamp the docs/source/changelog.md placeholder.
- **32-02** (wave 2, human-gated): full harmonics+Chiron-aware local pre-flight (HARD GATES)
  → BLOCKING human go/no-go → tag v1.4.0 + push tag + push origin/main + GitHub release
  (sdist+wheel) → post-publish fresh-venv smoke from PyPI.

---

## Version Bump Locations (ALL Files to Change)

Verified 2026-06-03 by reading all files directly.

| File | Line | Current value | Target value | Notes |
|------|------|---------------|--------------|-------|
| `pyproject.toml` | 7 | `version = "1.3.0"` | `version = "1.4.0"` | Build system source of truth |
| `ketu/__init__.py` | 57 | `__version__ = "1.3.0"` | `__version__ = "1.4.0"` | Runtime source of truth |
| `docs/source/conf.py` | 14–15 | Already `"1.4.0"` | **No change needed** | Pre-bumped in Phase 31 |

**Total files to edit: 2** (`pyproject.toml` + `ketu/__init__.py`). `docs/source/conf.py`
is already at 1.4.0 — do NOT touch it (same Pitfall 8 as v1.3, see Pitfalls below).

Gate: `pip install -e . -q && pytest tests/test_version.py -v`

---

## CHANGELOG.md Current State and Required Delta

**Verified 2026-06-03 by reading CHANGELOG.md directly.**

### Current structure (confirmed)

```
## [1.3.0] - 2026-06-01    ← line 10 (already dated, no Unreleased)
## [1.2.0] - 2026-05-28    ← (further down)
```

**There is NO `[Unreleased]` section and NO `[1.4.0]` section.** The `[1.4.0]` block must
be authored fresh and inserted ABOVE `## [1.3.0] - 2026-06-01`.

### Content source

`docs/source/changelog.md` has a `## [1.4.0] - 2026-06-XX` block (written Phase 31):

```
### Added 1.4.0
- generate_harmonic_aspects(h) dynamic generator
- Chiron range expanded to 1900–2100 (2283 Chebyshev segments)

### Changed 1.4.0
- Chiron orb 0° → 4° (Pluto parity)
- Chiron out-of-range behaviour: silently clamped (was ValueError)
- Documentation recentred on 180°-division default
```

The docs changelog uses its own format (`### Added 1.4.0` etc.) — the root CHANGELOG uses the
**Keep a Changelog** format (`### Added`, `### Changed`). Do NOT copy the docs format
verbatim — adapt to root format.

### Root CHANGELOG.md [1.4.0] section to author

Place immediately after line 9 (the blank line before `## [1.3.0]`). Use today's UTC date.

```markdown
## [1.4.0] - YYYY-MM-DD

### Added

- **`generate_harmonic_aspects(h)` — dynamic harmonic generator**: builds aspect specs on
  the fly for any integer harmonic `h` (2 ≤ h ≤ 64), using the full-circle 360° convention
  folded to 0–180° (`coef = k/h`). Returns a structured array compatible with `core.aspects`;
  pass as `dynamic_specs=` argument to `calculate_aspects`, `find_aspects_between_dates`, and
  `calculate_synastry`. The frozen 14-row `core.aspects` table and preset fingerprints are
  byte-identical (parallel code path, no interference). Available at
  `ketu.aspects.generate_harmonic_aspects` and `ketu.aspects.harmonics.generate_harmonic_aspects`.
  (Phase 28)
- **Chiron range expanded to 1900–2100**: `ketu/data/chiron_coeffs.npz` regenerated with 2283
  Chebyshev segments (`jd_start=2415020.5` / `jd_end=2488069.5`, seg=32 days, degree=10).
  Max |Δλ| = 0.001214° over the full 1900–2100 range. Pure-NumPy runtime preserved; file
  size increased from 289.7 KB to ~578 KB. `calc_planet_position(jd, 13)` resolves Chiron
  for any JD in the new range including 1900–1949 and 2051–2100. (Phase 30)

### Changed

- **Chiron orb 0° → 4°** (Pluto parity): `core.bodies['orb']` for Chiron is now 4°.
  Chiron now forms scored aspects in all aspect-detection paths (`calculate_aspects`,
  `compute_chart`, `calculate_synastry`, `find_aspects_between_dates`). Downstream code
  that expected Chiron to produce zero aspects (old orb=0) must adapt; Chiron aspect
  counts and scores change accordingly. See UPGRADING.md → "v1.3 -> v1.4". (Phase 29)
- **Chiron out-of-range clamping**: input JD outside the 1900–2100 range is now silently
  clamped to the nearest segment boundary; previously raised `ValueError`. (Phase 30)
- **Documentation recentred on 180°-division default**: `concepts.md` aspect tables show
  CLASSICAL (5) and TRADITIONAL (7) only; full-circle minor harmonics (H5/H9/H10 /
  EXTENDED) remain available in code but are removed from the summary tables. (Phase 31)
```

### Required action in Plan 32-01

1. Read CHANGELOG.md to confirm current state (no Unreleased, no [1.4.0]).
2. Insert the `## [1.4.0] - YYYY-MM-DD` block above `## [1.3.0] - 2026-06-01`.
3. Use the real release date (today's UTC date).
4. Leave `## [1.3.0] - 2026-06-01` and everything below untouched.

---

## fr/CHANGELOG.md Required Delta

**Verified 2026-06-03 by reading fr/CHANGELOG.md directly.**

`fr/CHANGELOG.md` currently has `## [1.3.0] - 2026-06-01` as the latest section. A matching
French `## [1.4.0] - YYYY-MM-DD` section must be added above it (same date as root CHANGELOG).

```markdown
## [1.4.0] - YYYY-MM-DD

### Ajouts

- **`generate_harmonic_aspects(h)` — générateur d'harmoniques dynamiques**: construit des
  spécifications d'aspects à la volée pour tout harmonique entier `h` (2 ≤ h ≤ 64), en
  utilisant la convention plein-cercle 360° ramenée à 0–180° (`coef = k/h`). Retourne un
  tableau structuré compatible avec `core.aspects` ; passez-le comme argument `dynamic_specs=`
  à `calculate_aspects`, `find_aspects_between_dates` et `calculate_synastry`. La table figée
  de 14 lignes `core.aspects` et les empreintes des préréglages sont identiques octet par octet
  (chemin de code parallèle). (Phase 28)
- **Plage Chiron étendue à 1900–2100** : `ketu/data/chiron_coeffs.npz` régénéré avec 2283
  segments Chebyshev (`jd_start=2415020.5` / `jd_end=2488069.5`, seg=32j, deg=10). Max
  |Δλ| = 0,001214° sur la plage complète 1900–2100. Exécution pur NumPy préservée ; taille
  du fichier passée de 289,7 Ko à ~578 Ko. (Phase 30)

### Modifié

- **Orbe Chiron 0° → 4°** (parité Pluton) : `core.bodies['orb']` pour Chiron est maintenant
  4°. Chiron forme désormais des aspects scorés dans tous les chemins de détection
  (`calculate_aspects`, `compute_chart`, `calculate_synastry`, `find_aspects_between_dates`).
  Le code en aval qui attendait zéro aspect de Chiron (ancien orbe=0) doit s'adapter.
  Voir `UPGRADING.md → v1.3 -> v1.4`. (Phase 29)
- **Comportement hors-plage Chiron** : un JD d'entrée hors de la plage 1900–2100 est
  maintenant silencieusement bridé à la borne de segment la plus proche ; auparavant levait
  `ValueError`. (Phase 30)
- **Documentation recentrée sur le défaut à 180°** : les tableaux d'aspects de `concepts.md`
  montrent uniquement CLASSICAL (5) et TRADITIONAL (7) ; les harmoniques mineurs plein-cercle
  (H5/H9/H10 / EXTENDED) restent disponibles dans le code mais sont retirés des tableaux
  récapitulatifs. (Phase 31)
```

---

## docs/source/changelog.md Date Placeholder

**Verified 2026-06-03.** `docs/source/changelog.md` line 9 reads:

```
## [1.4.0] - 2026-06-XX
```

The `2026-06-XX` placeholder must be replaced with the real release date as part of Plan
32-01. This edit is part of the same commit as the root CHANGELOG authoring. After this edit,
the docs changelog and the root CHANGELOG carry the same date.

**Note:** `docs/source/changelog.md` also has `## [1.3.0] - 2026-06-XX` on its v1.3 section
(line ~46). That placeholder was left from Phase 25/27. If it is still `2026-06-XX`, also
date-stamp it to `2026-06-01` (the actual v1.3.0 release date from root CHANGELOG.md). Verify
by reading the file before editing.

---

## UPGRADING.md Required Delta

**Verified 2026-06-03 by reading UPGRADING.md directly.**

`UPGRADING.md` currently has `## v1.2 -> v1.3` as the topmost section (line 6). There is NO
`## v1.3 -> v1.4` section. It must be added as the **new first section**, before `## v1.2 -> v1.3`.

### Rationale for UPGRADING entry

v1.4 has two behavioural changes relevant to downstream consumers (primarily Kala):

1. **Chiron orb 0° → 4°** is a **behavioural breaking change**: any code that queries aspects
   for charts containing Chiron will now receive results it previously did not (Chiron aspects
   are newly scored). This can change aspect counts, aspect type fields, and synastry output.

2. **Chiron out-of-range clamping** (was `ValueError`): code that expected an exception for
   out-of-range JD will now silently succeed (clamped). This is a silently-breaking behaviour
   change for any code that relied on the exception for bounds checking.

3. **Dynamic generator** is purely additive (no existing behaviour changes).

### `## v1.3 -> v1.4` content to add

```markdown
## v1.3 -> v1.4

### Chiron orb changed from 0° to 4° — Chiron now forms aspects

In v1.4.0, `core.bodies['orb']` for Chiron is **4°** (previously 0°). This means:

- `calculate_aspects`, `compute_chart`, `calculate_synastry`, and
  `find_aspects_between_dates` will now detect and score Chiron aspects.
- Downstream code that assumed Chiron produces **zero aspects** must be updated.
  Chiron aspect counts, scores, and aspect_type fields change accordingly.
- The `CHART_DTYPE` body axis is **unchanged** from v1.3 (still 14 bodies / indices 0–13).
  Only the orb scalar changes.

**Kala / downstream adapter guidance:** If you filter or count aspects by body index,
results for body_id=13 (Chiron) will now be non-empty. Recompute any Chiron-related
aspect tallies or downstream models after upgrading.

### Chiron out-of-range behaviour: ValueError → silent clamp

In v1.4.0, passing a JD outside the 1900–2100 range to `calc_planet_position(jd, 13)`
or `calc_planet_position_batch(jds, 13)` is **silently clamped** to the nearest segment
boundary. Previously this raised `ValueError`.

- Code that relied on the `ValueError` for bounds checking must add explicit range
  validation if that contract is needed.
- The valid range expanded from 1950–2050 to **1900–2100** (see below).

### Chiron range expanded: 1950–2050 → 1900–2100

`calc_planet_position(jd, 13)` now resolves Chiron for any JD in **1900–2100**
(previously 1950–2050 only). The embedded `.npz` was regenerated; no code changes needed.

Verify the new range is active:

```python
from ketu.ephemeris.planets import calc_planet_position
import math

# JD 2422324.5 ≈ 1920-01-01 — outside the old 1950–2050 range
pos = calc_planet_position(2422324.5, 13)
lon = float(pos[0])
assert math.isfinite(lon) and 0.0 <= lon < 360.0
```

### Dynamic harmonic generator — additive, no migration needed

`ketu.aspects.generate_harmonic_aspects(h)` is a new pure-additive API. No existing
imports or callers change. Opt in by passing `dynamic_specs=generate_harmonic_aspects(h)`
to `calculate_aspects`, `find_aspects_between_dates`, or `calculate_synastry`.
```

---

## README.md Required Delta

**Verified 2026-06-03.** README currently has `## What's New in v1.3.0` at line 13.
There is **no** `## What's New in v1.4.0` section.

A `## What's New in v1.4.0` section must be added as a NEW section between lines 12
(the `---` separator at the end of the v1.3 section) and line 13 (the current
`## What's New in v1.3.0` header). Actually the structure is:

```
[project preamble]
## What's New in v1.3.0    ← line 13 (becomes second section)
...v1.3 content...
---                         ← separator
## What's New in v1.2.0    ← line 40
```

The new section should be inserted BEFORE `## What's New in v1.3.0` to keep newest-first:

```markdown
## What's New in v1.4.0

Ketu v1.4.0 adds a dynamic harmonic aspect generator and expands the Chiron range to
1900–2100. The public API is purely additive; the two behavioural changes are the Chiron
orb (0°→4°, Chiron now forms aspects) and the silenced out-of-range clamping.
See [UPGRADING.md](UPGRADING.md) for migration notes and [CHANGELOG.md](CHANGELOG.md)
for the full list.

- **Dynamic harmonic generator** — `generate_harmonic_aspects(h)` produces aspect specs
  on the fly for any harmonic 2–64 in the full-circle 360° convention. Pass as
  `dynamic_specs=` to `calculate_aspects`, `calculate_synastry`, or
  `find_aspects_between_dates`. The frozen 14-aspect `core.aspects` table is unchanged.
- **Chiron range 1900–2100** — the embedded Chebyshev `.npz` was regenerated with 2283
  segments covering JD 2415020.5–2488069.5 (1900-01-01 to 2100-01-01). Max error 0.001214°.
  Pure-NumPy runtime preserved.
- **Chiron orb 4°** — Chiron now participates in aspect detection like any other body.
  Downstream consumers (Kala) that expect zero Chiron aspects must adapt.

---
```

---

## PyPI and Git Tag State

**Verified 2026-06-03 against live repo and PyPI.**

| Item | State |
|------|-------|
| Current PyPI live version | 1.3.0 |
| `v1.4.0` tag | Does NOT yet exist |
| `v1.3.0` tag | Exists on main |
| PyPI slot `ketu==1.4.0` | Available (confirmed via JSON API) |
| OIDC trusted publisher | Configured from Phase 20 — Owner:alkimya, Repo:ketu, Workflow:publish.yml, Environment:pypi — no changes needed |

---

## Publish Workflow (publish.yml)

**Verified 2026-06-03 by reading `.github/workflows/publish.yml` directly.**

```yaml
on:
  push:
    tags:
      - 'v*.*.*'          # trigger: push v1.4.0 tag
jobs:
  build:                   # Python 3.11, python -m build --sdist --wheel, twine check
  publish-to-pypi:         # needs build, environment: pypi, id-token: write
                           # uses: pypa/gh-action-pypi-publish@release/v1
```

**No changes to publish.yml are needed for v1.4.0.** Actions versions (Node 24 from Phase 20):
- `actions/checkout@v5`
- `actions/setup-python@v6`
- `actions/upload-artifact@v5` / `actions/download-artifact@v5`
- `pypa/gh-action-pypi-publish@release/v1`

**CRITICAL (from project memory):** Push BOTH the tag AND `origin/main`:
```bash
git push origin v1.4.0     # triggers publish.yml → PyPI
git push origin main        # RTD follows main, not the tag
```
Pushing only the tag leaves RTD docs frozen (feedback_push_main_not_just_tag_on_release).

---

## Packaging of ketu/data (chiron_coeffs.npz)

**Verified 2026-06-03.** `pyproject.toml` includes:

```toml
[tool.setuptools]
packages = ["ketu", ..., "ketu.data"]   # ketu.data is explicitly listed

[tool.setuptools.package-data]
"ketu.data" = ["*.npz"]                  # *.npz included in wheel + sdist
```

The regenerated `ketu/data/chiron_coeffs.npz` is now **~578 KB** (was 289.7 KB at v1.3).
2283 Chebyshev segments, jd_start=2415020.5, jd_end=2488069.5.

**Smoke test must verify the .npz ships (new size note):**
```bash
python -m zipfile -l dist/ketu-1.4.0-py3-none-any.whl | grep "chiron_coeffs.npz"
# Expected: ketu/data/chiron_coeffs.npz (present; size ~578KB)
```

---

## Quality Gates Status (as of 2026-06-03)

**Verified live in venv.**

| Gate | Status | Notes |
|------|--------|-------|
| `pytest tests/ -q` | PASS | **1537 passed, 2 skipped** (up from 1399 at v1.3) |
| `python -m interrogate ketu/` | PASS | 99.7% (minimum 95%) |
| `python -m numpydoc lint $(...)` | PASS | Zero violations (excluding `lunar_calendar.py` and `_*.py`) |
| `python -m mypy --strict ketu/` | **FAIL** | 1 error: `ketu/synastry/api.py:392` `no-any-return` |

**The mypy error MUST be fixed before tagging.** The error is in `calculate_synastry`
at line 392: `return out[out["aspect_type"] != -1]` returns `Any` from a function
typed to return `np.ndarray`. This requires a cast or type annotation. This must be
resolved in Plan 32-02 Task 1 (pre-flight) or as a preliminary fix before 32-02 runs.

**Recommendation:** Fix the mypy error in Plan 32-01 as an additional Task, or as a
pre-task in 32-02. The fix is a one-liner: add `cast(np.ndarray, ...)` or adjust the
return annotation. Since it is a source change (not documentation), it belongs in a
separate commit before the version-bump commit, or bundled with the version-bump commit.

---

## Fresh-Venv Smoke Test (REL-13) — v1.4.0 Assertions

The v1.4.0 smoke test adds **three new assertions** on top of the v1.3 assertions:

1. `generate_harmonic_aspects(7)` → 3 rows, angles ≈ [51.4286, 102.8571, 154.2857]
2. `core.bodies['orb']` for Chiron is 4.0
3. `calc_planet_position(2422324.5, 13)` (JD for 1920-01-01, outside old 1950–2050 range)
   returns a finite longitude in [0, 360)

**The jd_1920 smoke JD:** `2422324.5` = 1920-01-01 00:00:00 UTC. This JD is below
the old lower bound `2433282.5` (1950-01-01), so if the old (1950–2050) `.npz` were
present, this would fail with ValueError. It resolving correctly proves the 1900–2100
range is active.

**Complete Fresh-Venv Smoke Test for Plan 32-02:**

```bash
#!/usr/bin/env bash
set -euo pipefail
VERSION="1.4.0"
JD_1920="2422324.5"   # 1920-01-01 — outside old 1950-2050 range

# 1. Verify wheel exists and is pure-Python
ls dist/ketu-${VERSION}-py3-none-any.whl || { echo "FAIL: wheel not found (check for platform tag)"; exit 1; }

# 2. Verify .npz ships in wheel (~578 KB in v1.4)
python -m zipfile -l dist/ketu-${VERSION}-py3-none-any.whl | grep -q "ketu/data/chiron_coeffs.npz" \
  || { echo "FAIL: chiron_coeffs.npz missing from wheel"; exit 1; }
echo "OK: chiron_coeffs.npz present in wheel"

# 3. Fresh venv
TMP=$(mktemp -d)
trap "rm -rf '$TMP'" EXIT
python -m venv "$TMP"

# 4. Install ONLY the wheel (no .[test] extras → no pyswisseph)
"$TMP/bin/pip" install --quiet "dist/ketu-${VERSION}-py3-none-any.whl"

# 5. Version check
"$TMP/bin/python" -c "
import ketu, importlib.metadata as m
assert ketu.__version__ == '${VERSION}', f'Bad __version__: {ketu.__version__}'
assert m.version('ketu') == '${VERSION}', f'Bad metadata: {m.version(\"ketu\")}'
print('version OK:', ketu.__version__)
"

# 6. All subpackage imports (including v1.4 generate_harmonic_aspects)
"$TMP/bin/python" -c "
from ketu.core import bodies, aspects, signs
from ketu.calculations import long
from ketu.aspects import calculate_aspects, aspects_for_harmonics, generate_harmonic_aspects
from ketu.cycles import generate_cycle_series
from ketu.cache import EphemerisCache
from ketu.houses import calculate_houses
from ketu.charts import compute_chart
from ketu.synastry import calculate_synastry
from ketu.composite import calculate_composite
from ketu.returns import solar_return
from ketu.parts import calculate_part
from ketu.ephemeris.planets import calc_planet_position
print('all subpackage imports OK')
"

# 7. v1.4 NEW: generate_harmonic_aspects(7) — correct H7 angles
"$TMP/bin/python" -c "
from ketu.aspects import generate_harmonic_aspects
h7 = generate_harmonic_aspects(7)
assert len(h7) == 3, f'Expected 3 H7 rows, got {len(h7)}'
angles = [float(a) for a in h7['angle']]
expected = [360/7, 720/7, 1080/7]
for a, e in zip(angles, expected):
    assert abs(a - e) < 0.01, f'H7 angle off: {a} vs {e}'
print(f'H7 angles OK: {[round(a,4) for a in angles]}')
"

# 8. v1.4 NEW: Chiron orb is 4.0
"$TMP/bin/python" -c "
import numpy as np
from ketu.core import bodies
idx = np.where(bodies['name'] == b'Chiron')[0][0]
orb = float(bodies['orb'][idx])
assert orb == 4.0, f'Expected Chiron orb=4.0, got {orb}'
print(f'Chiron orb OK: {orb}°')
"

# 9. v1.4 NEW: Chiron resolves at JD 2422324.5 (1920-01-01 — outside old 1950-2050 range)
"$TMP/bin/python" -c "
import math
from ketu.ephemeris.planets import calc_planet_position
jd = ${JD_1920}  # 1920-01-01, was out-of-range under v1.3
pos = calc_planet_position(jd, 13)
lon = float(pos[0])
assert math.isfinite(lon), f'Chiron longitude not finite at 1920: {lon}'
assert 0.0 <= lon < 360.0, f'Chiron longitude out of range at 1920: {lon}'
print(f'Chiron 1920 OK: lon={lon:.4f}° (proves 1900-2100 range active)')
"

# 10. v1.3 preserved: Chiron resolves at J2000.0
"$TMP/bin/python" -c "
import math
from ketu.ephemeris.planets import calc_planet_position
pos = calc_planet_position(2451545.0, 13)   # J2000.0
lon = float(pos[0])
assert math.isfinite(lon) and 0.0 <= lon < 360.0, f'Chiron J2000 bad: {lon}'
print(f'Chiron J2000 OK: lon={lon:.4f}°')
"

# 11. pyswisseph NOT installed (AGPL isolation)
"$TMP/bin/python" -c "
import importlib.util
spec = importlib.util.find_spec('swisseph')
assert spec is None, 'FAIL: pyswisseph is importable in runtime venv'
print('pyswisseph NOT in runtime venv: OK')
"

echo "All smoke tests PASSED for ketu==${VERSION}"
```

---

## Pre-flight Script (v1.4.0)

Complete script for Plan 32-02, Task 1:

```bash
#!/usr/bin/env bash
set -euo pipefail
VERSION="1.4.0"

echo "=== Pre-flight: ketu ${VERSION} ==="

# 1. Clean working tree on main
test -z "$(git status --porcelain)" || { echo "FAIL: Dirty working tree"; exit 1; }
git branch --show-current | grep -q "^main$" || { echo "FAIL: Not on main branch"; exit 1; }
echo "OK: clean tree on main"

# 2. Version sync
grep -q "version = \"${VERSION}\"" pyproject.toml || { echo "FAIL: pyproject.toml not bumped"; exit 1; }
grep -q "__version__ = \"${VERSION}\"" ketu/__init__.py || { echo "FAIL: __init__.py not bumped"; exit 1; }
pip install -e . -q
pytest tests/test_version.py -v
echo "OK: version synced to ${VERSION}"

# 3. CHANGELOG [1.4.0] dated (not a placeholder)
grep -q "^## \[${VERSION}\] - 20" CHANGELOG.md || { echo "FAIL: [${VERSION}] not dated in CHANGELOG"; exit 1; }
! grep -q "^## \[${VERSION}\] - 2026-06-XX" CHANGELOG.md || { echo "FAIL: CHANGELOG still has XX placeholder"; exit 1; }
! grep -q "^## \[Unreleased\]" CHANGELOG.md || { echo "FAIL: [Unreleased] section present"; exit 1; }
echo "OK: CHANGELOG dated and no Unreleased or XX placeholder"

# 4. fr/CHANGELOG has matching [1.4.0] section
grep -q "^## \[${VERSION}\] - 20" fr/CHANGELOG.md || { echo "FAIL: fr/CHANGELOG.md missing [${VERSION}]"; exit 1; }
echo "OK: fr/CHANGELOG.md has dated [${VERSION}]"

# 5. UPGRADING has v1.3 -> v1.4 section
grep -q "v1\.3 -> v1\.4" UPGRADING.md || { echo "FAIL: UPGRADING missing v1.3 -> v1.4 section"; exit 1; }
echo "OK: UPGRADING.md has v1.3 -> v1.4 section"

# 6. docs/source/changelog.md placeholder replaced
! grep -q "\[${VERSION}\] - 2026-06-XX" docs/source/changelog.md || { echo "FAIL: docs/source/changelog.md still has XX placeholder"; exit 1; }
echo "OK: docs/source/changelog.md date placeholder resolved"

# 7. Quality gates (all must pass before tag)
FILES=$(find ketu -name "*.py" ! -path "*/__pycache__/*" ! -name "lunar_calendar.py" ! -name "_*.py")
python -m numpydoc lint $FILES || { echo "FAIL: numpydoc violations"; exit 1; }
python -m interrogate ketu/ || { echo "FAIL: interrogate < 95%"; exit 1; }
pytest tests/ -q
python -m mypy --strict ketu/
echo "OK: all quality gates pass"

# 8. Build
rm -rf dist/ build/ ketu.egg-info/
python -m build --sdist --wheel
ls dist/ketu-${VERSION}-py3-none-any.whl || { echo "FAIL: wheel has unexpected platform tag"; exit 1; }
echo "OK: built dist/"

# 9. twine check
pip install --quiet twine
python -m twine check dist/*
echo "OK: twine check"

# 10. Verify .npz ships in wheel (v1.4: ~578 KB)
python -m zipfile -l dist/ketu-${VERSION}-py3-none-any.whl | grep -q "ketu/data/chiron_coeffs.npz" \
  || { echo "FAIL: chiron_coeffs.npz missing from wheel"; exit 1; }
echo "OK: chiron_coeffs.npz present in wheel"

# 11. sdist ships fr/CHANGELOG.md
tar -tzf dist/ketu-${VERSION}.tar.gz | grep -q "fr/CHANGELOG.md" \
  || { echo "FAIL: fr/CHANGELOG.md missing from sdist"; exit 1; }
echo "OK: fr/CHANGELOG.md in sdist"

# 12. Full fresh-venv smoke test (local wheel)
TMP=$(mktemp -d)
trap "rm -rf '$TMP'" EXIT
python -m venv "$TMP"
"$TMP/bin/pip" install --quiet "dist/ketu-${VERSION}-py3-none-any.whl"

"$TMP/bin/python" -c "
import ketu, importlib.metadata as m
assert ketu.__version__ == '${VERSION}' == m.version('ketu'), f'version mismatch: {ketu.__version__}'
print('version OK')
"

"$TMP/bin/python" -c "
from ketu.core import bodies, aspects, signs
from ketu.calculations import long
from ketu.aspects import calculate_aspects, aspects_for_harmonics, generate_harmonic_aspects
from ketu.cycles import generate_cycle_series
from ketu.cache import EphemerisCache
from ketu.houses import calculate_houses
from ketu.charts import compute_chart
from ketu.synastry import calculate_synastry
from ketu.composite import calculate_composite
from ketu.returns import solar_return
from ketu.parts import calculate_part
from ketu.ephemeris.planets import calc_planet_position
print('all imports OK')
"

# v1.4 new: H7 angles
"$TMP/bin/python" -c "
from ketu.aspects import generate_harmonic_aspects
h7 = generate_harmonic_aspects(7)
assert len(h7) == 3
angles = [float(a) for a in h7['angle']]
assert all(abs(a - e) < 0.01 for a, e in zip(angles, [360/7, 720/7, 1080/7]))
print(f'H7 OK: {[round(a,4) for a in angles]}')
"

# v1.4 new: Chiron orb=4
"$TMP/bin/python" -c "
import numpy as np; from ketu.core import bodies
idx = np.where(bodies['name'] == b'Chiron')[0][0]
assert float(bodies['orb'][idx]) == 4.0
print('Chiron orb=4.0 OK')
"

# v1.4 new: Chiron resolves at 1920 (outside old 1950-2050)
"$TMP/bin/python" -c "
import math; from ketu.ephemeris.planets import calc_planet_position
lon = float(calc_planet_position(2422324.5, 13)[0])  # 1920-01-01
assert math.isfinite(lon) and 0.0 <= lon < 360.0
print(f'Chiron 1920 OK: {lon:.4f}°')
"

# v1.3 preserved: Chiron at J2000
"$TMP/bin/python" -c "
import math; from ketu.ephemeris.planets import calc_planet_position
lon = float(calc_planet_position(2451545.0, 13)[0])
assert math.isfinite(lon) and 0.0 <= lon < 360.0
print(f'Chiron J2000 OK: {lon:.4f}°')
"

# AGPL isolation
"$TMP/bin/python" -c "
import importlib.util
assert importlib.util.find_spec('swisseph') is None, 'pyswisseph LEAKED into runtime wheel!'
print('pyswisseph absent: OK')
"

echo "OK: fresh-venv smoke tests PASSED"

# 13. PyPI slot clear
python3 -c "
import urllib.request, json
data = json.loads(urllib.request.urlopen('https://pypi.org/pypi/ketu/json').read())
versions = list(data['releases'].keys())
assert '${VERSION}' not in versions, f'PyPI already has ${VERSION}!'
print(f'PyPI clear. Latest: {sorted(versions)[-1]}')
"

echo ""
echo "=== Pre-flight PASSED ==="
echo "Safe to: git tag -a v${VERSION} -m 'Release ${VERSION}' && git push origin v${VERSION} && git push origin main"
```

---

## GitHub Release Body (v1.4.0)

Ready-to-use body for `gh release create v1.4.0`:

```
Ketu v1.4.0 — Dynamic Harmonic Generator + Chiron Range 1900–2100

**New in v1.4.0:**
- `generate_harmonic_aspects(h)` — dynamic aspect generator for any harmonic 2–64 in full-circle convention. Pass as `dynamic_specs=` to `calculate_aspects`, `calculate_synastry`, `find_aspects_between_dates`. Frozen `core.aspects` table is unchanged.
- Chiron range expanded to **1900–2100** (was 1950–2050): `ketu/data/chiron_coeffs.npz` regenerated with 2283 Chebyshev segments, max error 0.001214°. Pure-NumPy runtime preserved.

**Changed in v1.4.0:**
- Chiron orb **0° → 4°** (Pluto parity): Chiron now forms scored aspects in all detection paths.
- Chiron out-of-range input is now **silently clamped** (was `ValueError`).
- Documentation recentred: aspect tables show CLASSICAL (5) and TRADITIONAL (7) only; EXTENDED remains in code.

**Migration:** see [UPGRADING.md → v1.3 -> v1.4](https://github.com/alkimya/ketu/blob/main/UPGRADING.md#v13---v14) — primarily for Chiron orb change (downstream aspect counts change).

- [CHANGELOG](https://github.com/alkimya/ketu/blob/main/CHANGELOG.md)
- `pip install ketu==1.4.0`

1537 tests, mypy --strict, 100% coverage.
```

Command:

```bash
gh release create v1.4.0 \
  --title "Ketu 1.4.0 — Dynamic Harmonic Generator + Chiron Range 1900–2100" \
  --notes "$(cat <<'EOF'
Ketu v1.4.0 adds a dynamic harmonic aspect generator and expands the Chiron ephemeris to
the full 1900–2100 range. The frozen aspect table and all existing imports are unchanged.

**New in v1.4.0:**
- `generate_harmonic_aspects(h)` — build aspect specs on the fly for any harmonic 2–64.
  Pass as `dynamic_specs=` to `calculate_aspects`, `calculate_synastry`, `find_aspects_between_dates`.
  The frozen 14-row `core.aspects` and preset fingerprints are byte-identical.
- Chiron range expanded to **1900–2100** (was 1950–2050): 2283 Chebyshev segments,
  max error 0.001214°, pure-NumPy runtime, ~578 KB `.npz`.

**Changed in v1.4.0:**
- Chiron orb **0° → 4°** (Pluto parity): Chiron now forms scored aspects in all detection paths
  (`calculate_aspects`, `compute_chart`, `calculate_synastry`, `find_aspects_between_dates`).
- Chiron out-of-range input is now **silently clamped** to the nearest boundary (was `ValueError`).
- Documentation recentred: summary tables show CLASSICAL (5) and TRADITIONAL (7) only;
  EXTENDED / full-circle minors remain available in code.

**Migration (see UPGRADING.md → v1.3 → v1.4):**
- Downstream code expecting **zero Chiron aspects** (old orb=0) must adapt — aspect counts
  and scores for body_id=13 will now be non-empty.
- Code relying on `ValueError` for out-of-range JD must add explicit bounds checking.

- 📋 [CHANGELOG](https://github.com/alkimya/ketu/blob/main/CHANGELOG.md)
- 🔄 [UPGRADING](https://github.com/alkimya/ketu/blob/main/UPGRADING.md#v13---v14)
- 📦 `pip install ketu==1.4.0`

1537 tests, mypy --strict, 100% coverage.
EOF
)" \
  dist/ketu-1.4.0-py3-none-any.whl dist/ketu-1.4.0.tar.gz
```

---

## Plan Decomposition

```
.planning/phases/32-release-v1-4-0/
├── 32-01-version-bump-changelog-upgrading-PLAN.md   # REL-12 (docs-only, wave 1)
└── 32-02-pypi-publish-smoke-test-PLAN.md            # REL-13 (human-gated, wave 2)
```

### Plan 32-01 task list

1. **Fix the mypy error** in `ketu/synastry/api.py:392` (`no-any-return`) before bumping
   version — this is a source change that must be committed before the version bump commit.
   (If the planner decides to bundle it with the version bump commit, that is also acceptable
   since it is a pre-existing quality gate failure.)
2. Bump version: `pyproject.toml` + `ketu/__init__.py` → `"1.4.0"`. Do NOT touch
   `docs/source/conf.py` (already at 1.4.0 — Pitfall 8).
3. Run `pytest tests/test_version.py -v` to verify the sync gate.
4. Author the root `CHANGELOG.md` `[1.4.0]` section (fresh — no merge needed).
5. Date-stamp `docs/source/changelog.md` `[1.4.0] - 2026-06-XX` → real date.
   Also check and fix `docs/source/changelog.md` `[1.3.0] - 2026-06-XX` placeholder if
   still present (replace with `2026-06-01`).
6. Add `## v1.3 -> v1.4` section to `UPGRADING.md` (new first section).
7. Add `## [1.4.0]` section to `fr/CHANGELOG.md`.
8. Add `## What's New in v1.4.0` to `README.md` above the existing v1.3.0 section.
9. Commit all doc + version changes in one atomic commit.
10. Run full suite: `pytest tests/ -q` to confirm nothing broken.

### Plan 32-02 task list

1. Date-stamp check: confirm both CHANGELOG.md and fr/CHANGELOG.md carry today's release date.
2. Full pre-flight (the script above) — HARD GATES, stop on first failure.
3. **BLOCKING human go/no-go checkpoint** (present pre-flight results; wait for "approved").
4. `git tag -a v1.4.0 -m "Release 1.4.0 — Dynamic Harmonic Generator + Chiron Range 1900–2100"`
5. `git push origin v1.4.0` — triggers publish.yml.
6. `git push origin main` — RTD follows main (feedback_push_main_not_just_tag_on_release).
7. Watch `publish.yml` to completion via `gh run watch`.
8. `gh release create v1.4.0` with sdist + wheel, using the release body above.
9. Post-publish verification: fresh venv `pip install ketu==1.4.0` from PyPI, run full
   smoke assertions (all four v1.4 checks + all-imports + no-swisseph).
10. Clean local build artifacts: `rm -rf dist build ketu.egg-info`.

---

## Numbered Pitfalls (v1.4-specific adaptations of v1.3 list)

### Pitfall 1: Authoring CHANGELOG from scratch (different from v1.3 merge)

**What goes wrong:** Plan writer tries to find an `[Unreleased]` section to merge (v1.3
pattern) — there is none. The `[1.4.0]` block must be authored fresh. The content source is
`docs/source/changelog.md`, not the root CHANGELOG.

**How to avoid:** Read root CHANGELOG.md first. Confirm current state: `## [1.3.0] - 2026-06-01`
is the top section. Write the `[1.4.0]` block from the bullets in this RESEARCH.md.

### Pitfall 2: docs/source/changelog.md date placeholder left as 2026-06-XX

**What goes wrong:** The docs changelog has `## [1.4.0] - 2026-06-XX`. If not replaced,
RTD will show a placeholder date after the release.

**How to avoid:** Plan 32-01 Task 5 explicitly replaces `2026-06-XX` with the real date.
Pre-flight step 6 asserts the placeholder is gone: `! grep -q "\[1.4.0\] - 2026-06-XX" docs/source/changelog.md`.

### Pitfall 3: docs/source/changelog.md v1.3 placeholder still 2026-06-XX

**What goes wrong:** The v1.3 section in docs/source/changelog.md may still read
`## [1.3.0] - 2026-06-XX` (a leftover from Phase 25/27). Not a blocker for PyPI publish, but
cosmetically wrong in RTD.

**How to avoid:** When editing docs/source/changelog.md for the v1.4 date, also check the
v1.3 section and replace its placeholder with `2026-06-01` (the actual v1.3.0 release date).

### Pitfall 4: mypy strict fails (ketu/synastry/api.py:392 no-any-return)

**What goes wrong:** `python -m mypy --strict ketu/` reports 1 error at `synastry/api.py:392`.
The pre-flight STOPS on this gate failure before the tag is pushed.

**How to avoid:** Fix the error in Plan 32-01. The fix: add a cast —
`return cast(np.ndarray, out[out["aspect_type"] != -1])` — or tighten the return type.
Run `python -m mypy --strict ketu/` after the fix to confirm zero errors.

### Pitfall 5: conf.py re-bumped unnecessarily (same as v1.3 Pitfall 8)

**What goes wrong:** Plan edits `docs/source/conf.py` to "1.4.0" — but it is already at
1.4.0 (pre-bumped in Phase 31). Creates a spurious no-op diff in the bump commit.

**How to avoid:** Read conf.py lines 14–15 before any edit. Current state: `release = "1.4.0"`,
`version = "1.4.0"`. Do NOT touch it.

### Pitfall 6: Push tag but forget to push main (RTD docs freeze)

**What goes wrong:** `git push origin v1.4.0` fires publish.yml and PyPI gets the new version.
But `origin/main` is not pushed. RTD follows main, so the docs on readthedocs.io remain frozen
at v1.3 content even though PyPI has v1.4.0.

**How to avoid:** Plan 32-02 Task 6 explicitly includes `git push origin main` as a separate
step AFTER the tag push. This is a first-class step, not optional (feedback_push_main_not_just_tag_on_release).

### Pitfall 7: chiron_coeffs.npz missing from wheel (larger file in v1.4)

**What goes wrong:** The v1.4 `.npz` is ~578 KB (was 289.7 KB). Any file-size gate or
packaging check tuned to the v1.3 size might appear wrong. More importantly, if `ketu.data`
were dropped from `packages`, the larger file would silently not ship.

**How to avoid:** Pre-flight step 10 asserts `ketu/data/chiron_coeffs.npz` is present in
the wheel using `python -m zipfile -l`. The presence check is binary — size is irrelevant.

### Pitfall 8: Smoke JD inside old 1950-2050 range proves nothing for the range expansion

**What goes wrong:** Smoke test uses `jd=2451545.0` (J2000.0 = year 2000) to check Chiron.
This JD was valid under v1.3 too, so it does not prove the 1900–2100 range is active.
The v1.3 and v1.4 `.npz` both cover J2000.0.

**How to avoid:** Smoke assertion #3 uses `jd=2422324.5` (1920-01-01), which is BELOW the
old v1.3 lower bound of 2433282.5 (1950-01-01). If the old `.npz` were present, this would
fail or clamp to wrong data.

### Pitfall 9: pyswisseph appears in fresh-venv (misleading dev venv result)

**What goes wrong:** In the dev venv, `swisseph` IS importable (it is under `.[test]` extras).
Running the pyswisseph absence check against the dev venv always passes, which gives false
confidence. The check must run inside the fresh venv that installed ONLY the wheel.

**How to avoid:** The smoke test always installs `dist/ketu-1.4.0-py3-none-any.whl` without
`.[test]` extras, and runs the `find_spec('swisseph') is None` check against THAT venv.

### Pitfall 10: Version bumped in only one file

**What goes wrong:** `pyproject.toml = "1.4.0"` but `ketu/__init__.py = "1.3.0"` (or vice
versa). `test_version_matches_metadata` fails.

**How to avoid:** Bump both in the same commit. Run `pytest tests/test_version.py -v`
immediately after.

### Pitfall 11: Tag not on main

**What goes wrong:** Tag pushed from a non-main branch. `publish.yml` runs but the resulting
wheel's commit is not on main's history.

**How to avoid:** Pre-flight step 1 confirms `git branch --show-current == main`. Confirm
before tagging.

### Pitfall 12: Wheel has a platform-specific name

**What goes wrong:** Smoke test looks for `ketu-1.4.0-py3-none-any.whl` but wheel was built
with a platform tag.

**How to avoid:** Pre-flight step 8 asserts `ls dist/ketu-${VERSION}-py3-none-any.whl`
succeeds. The `.npz` is pure data; the package is pure Python — `python -m build` always
produces `py3-none-any`.

### Pitfall 13: UPGRADING missing v1.3 -> v1.4 (Chiron orb is a behavioural break)

**What goes wrong:** Plan 32-01 omits the UPGRADING section because v1.4 "has no dtype
breaks like v1.3". But the Chiron orb change IS a behavioural breaking change for any
downstream code that expected zero Chiron aspects.

**How to avoid:** Plan 32-01 explicitly adds `## v1.3 -> v1.4` to UPGRADING.md with the
orb-change migration note. Pre-flight step 5 asserts `grep -q "v1\.3 -> v1\.4" UPGRADING.md`.

---

## Exact File/Line Targets for Every Edit (Plan 32-01)

| File | Edit | Location | Action |
|------|------|----------|--------|
| `ketu/synastry/api.py` | Fix mypy `no-any-return` | line 392 | Add `cast(np.ndarray, ...)` or adjust return type |
| `pyproject.toml` | Version bump | line 7 | `"1.3.0"` → `"1.4.0"` |
| `ketu/__init__.py` | Version bump | line 57 | `"1.3.0"` → `"1.4.0"` |
| `docs/source/conf.py` | **No change** | lines 14–15 | Already `"1.4.0"` — do NOT touch |
| `CHANGELOG.md` | Author `[1.4.0]` section | After line 9 (before `## [1.3.0]`) | Insert fresh `## [1.4.0] - YYYY-MM-DD` block |
| `docs/source/changelog.md` | Date-stamp `[1.4.0]` | line 9 | `2026-06-XX` → real date |
| `docs/source/changelog.md` | Date-stamp `[1.3.0]` if still XX | ~line 46 | `2026-06-XX` → `2026-06-01` |
| `UPGRADING.md` | Add `v1.3 -> v1.4` | line 1 (new first section) | Insert before `## v1.2 -> v1.3` |
| `fr/CHANGELOG.md` | Add `[1.4.0]` section | Before `## [1.3.0] - 2026-06-01` | Insert `## [1.4.0] - YYYY-MM-DD` in French |
| `README.md` | Add `## What's New in v1.4.0` | line 13 (before current v1.3 section) | Insert v1.4 What's New section |

---

## Subpackages for Smoke Import Table (v1.4 additions bolded)

| Package | Import | v1.4 note |
|---------|--------|-----------|
| `ketu` | `import ketu` | `__version__` check |
| `ketu.core` | `from ketu.core import bodies, aspects, signs` | |
| `ketu.calculations` | `from ketu.calculations import long` | |
| `ketu.aspects` | `from ketu.aspects import calculate_aspects, aspects_for_harmonics, generate_harmonic_aspects` | **`generate_harmonic_aspects` is new in v1.4** |
| `ketu.cycles` | `from ketu.cycles import generate_cycle_series` | |
| `ketu.cache` | `from ketu.cache import EphemerisCache` | |
| `ketu.houses` | `from ketu.houses import calculate_houses` | |
| `ketu.charts` | `from ketu.charts import compute_chart` | |
| `ketu.synastry` | `from ketu.synastry import calculate_synastry` | |
| `ketu.composite` | `from ketu.composite import calculate_composite` | |
| `ketu.returns` | `from ketu.returns import solar_return` | |
| `ketu.parts` | `from ketu.parts import calculate_part` | |
| `ketu.ephemeris.planets` | `from ketu.ephemeris.planets import calc_planet_position` | |

---

## State of the Art

| Item | v1.3.0 | v1.4.0 | Notes |
|------|--------|--------|-------|
| Body count | 14 (body_id 0–13) | 14 (unchanged) | No structural change |
| Chiron orb | 0° | **4°** | Chiron now forms scored aspects |
| Chiron valid range | 1950–2050 | **1900–2100** | 2283 segments, ~578 KB .npz |
| chiron_coeffs.npz size | 289.7 KB | **~578 KB** | Larger but same format |
| chiron_coeffs.npz segments | 1142 | **2283** | |
| Chiron max |Δλ| | 0.005695° | **0.001214°** | Better accuracy with more segments |
| Chiron out-of-range | ValueError | **silent clamp** | Behavioural change |
| Dynamic generator | Not available | **`generate_harmonic_aspects(h)`** | ketu.aspects + ketu.aspects.harmonics |
| HARMONIC_DTYPE | Not available | **new dtype** in ketu.aspects | |
| Test count | 1399 (Phase 26) | **1537** (2 skipped) | 100% coverage |
| mypy --strict | PASS | **1 error (must fix)** | synastry/api.py:392 |
| docs/source/conf.py | 1.3.0 | **Already 1.4.0** | Pre-bumped Phase 31, do not touch |
| docs/source/changelog.md | Has [1.4.0] stub | **Has date placeholder XX** | Must be date-stamped |
| README What's New | v1.3.0 section | **No v1.4.0 section yet** | Must add |
| UPGRADING | v1.2 → v1.3 only | **No v1.3 → v1.4 section** | Must add |
| fr/CHANGELOG | [1.3.0] is latest | **No [1.4.0] section** | Must add |
| PyPI slot 1.4.0 | N/A | **Available** (confirmed) | |
| v1.4.0 git tag | Does not exist | **Must create** | |

---

## Open Questions

1. **mypy fix strategy:** The `no-any-return` error in `ketu/synastry/api.py:392` needs a
   fix before tagging. Two options: (a) fix in a separate commit before Plan 32-01's version
   bump commit, (b) bundle it in the version bump commit. The planner should make this
   explicit in Plan 32-01 Task 1. Either is acceptable; what matters is that `mypy --strict`
   is clean before Plan 32-02 runs.

2. **docs/source/changelog.md v1.3 placeholder:** Read the file at `## [1.3.0]` to confirm
   whether it still says `2026-06-XX` or was already date-stamped. The research could not
   confirm the exact current state of that specific line. Plan 32-01 should read the file and
   conditionally fix it.

3. **README v1.4 What's New position:** Should `## What's New in v1.4.0` be inserted BEFORE
   or AFTER the existing `## What's New in v1.3.0`? Newest-first is the convention (v1.3 section
   was at line 13, above the v1.2 section at line 40). Insert v1.4 section before v1.3 section,
   making it the new first feature section under the project preamble.

---

## Sources

### Primary (HIGH confidence — verified against live repo files 2026-06-03)

- `pyproject.toml` (read directly) — `version = "1.3.0"` at line 7; `ketu.data` package + `*.npz` package-data confirmed; `pyswisseph` under `[test]` extras only
- `ketu/__init__.py` (read directly) — `__version__ = "1.3.0"` at line 57
- `docs/source/conf.py` (read directly) — `release = "1.4.0"`, `version = "1.4.0"` at lines 14–15 (pre-bumped Phase 31)
- `CHANGELOG.md` (read directly) — `## [1.3.0] - 2026-06-01` is the current top section; no Unreleased; no [1.4.0]
- `fr/CHANGELOG.md` (read directly) — `## [1.3.0] - 2026-06-01` is the current top section
- `docs/source/changelog.md` (read directly) — `## [1.4.0] - 2026-06-XX` block confirmed; content matches Phase 31 deliverables
- `UPGRADING.md` (read directly) — `## v1.2 -> v1.3` is the topmost section; no `## v1.3 -> v1.4` section exists
- `README.md` (read directly) — `## What's New in v1.3.0` at line 13; no v1.4 section
- `.github/workflows/publish.yml` (read directly) — tag-push trigger, OIDC, Node 24 actions confirmed; no changes needed
- `ketu/data/chiron_coeffs.npz` (read directly) — 578 KB, 2283 segments, jd_start=2415020.5, jd_end=2488069.5 (1900–2100)
- `git tag -l` output — `v1.3.0` exists, `v1.4.0` does not
- PyPI JSON API — 1.4.0 slot confirmed available; latest is 1.3.0
- `generate_harmonic_aspects(7)` (executed live) — 3 rows, angles [51.4286, 102.8571, 154.2857]
- `core.bodies` Chiron orb (executed live) — 4.0
- `calc_planet_position(2422324.5, 13)` (executed live) — 2.608478° (finite, in [0,360))
- `pytest tests/ -q` (executed live) — 1537 passed, 2 skipped
- `python -m mypy --strict ketu/` (executed live) — 1 error at synastry/api.py:392
- `python -m interrogate ketu/` (executed live) — 99.7% PASS
- `python -m numpydoc lint` (executed live, excluding lunar_calendar.py and _*.py) — zero violations

### Secondary (MEDIUM confidence)
- Phase 27 RESEARCH.md + PLAN files (read directly) — pre-flight pattern, ceremony pattern, pitfalls adapted for v1.4
- MEMORY.md entries for project feedback — feedback_push_main_not_just_tag_on_release, feedback_validation_review_before_release, project_v14_scope_intent confirmed

---

## Metadata

**Confidence breakdown:**
- Version bump locations: HIGH — read all files directly; exactly 2 files need editing
- CHANGELOG state: HIGH — read directly; no Unreleased, no [1.4.0]; fresh authoring required
- UPGRADING gap: HIGH — read directly; no v1.3 → v1.4 section
- docs/source/changelog.md placeholder: HIGH — `2026-06-XX` confirmed
- publish.yml trigger/OIDC: HIGH — read directly; no changes needed
- packaging (.npz in wheel): HIGH — pyproject.toml package-data confirmed; .npz is 578 KB
- Smoke test assertions: HIGH — all executed live; H7 angles, Chiron orb=4.0, 1920 JD finite
- mypy failure: HIGH — executed live; 1 error confirmed at synastry/api.py:392
- PyPI state: HIGH — JSON API confirmed; 1.4.0 slot free

**Research date:** 2026-06-03
**Valid until:** 30 days (stable domain; re-check PyPI slot just before publish)
