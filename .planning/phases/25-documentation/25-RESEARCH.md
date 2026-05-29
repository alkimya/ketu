# Phase 25: Documentation - Research

**Researched:** 2026-05-29
**Domain:** Sphinx + MyST-Parser + gettext i18n; Ketu public API surface audit
**Confidence:** HIGH (all findings are from direct codebase inspection and live tool runs)

---

## Summary

The Ketu documentation infrastructure is fully functional but frozen at v1.0 (2026-02-12). The 12 existing source pages cover the pre-v1.1 API (`ketu.long()`, `ketu.calculate_aspects()` etc.) which are no longer exported from the top-level `ketu` namespace. The eight feature areas shipped since v1.0 (configurable aspects, six house systems, `compute_chart`/`CHART_DTYPE`, synastry, midpoint composite, solar/lunar returns, Arabic Parts, Chiron) have zero documentation. Four brand-new pages are needed (relational charts, predictive/returns, Arabic Parts, Chiron), and eight existing pages need material updates.

The Sphinx + MyST-Parser + `sphinx-intl` stack is all installed in `venv/` and functional. The complete i18n command sequence is established. The critical gotcha: the `venv/bin/sphinx-intl` and `venv/bin/sphinx-build` scripts have a broken shebang (point to the non-existent `/home/loc/workspace/solaris/ketu/venv/bin/python3`). All Sphinx/sphinx-intl commands MUST be invoked via `python3 -m sphinx.cmd.build` and `python3 -c "from sphinx_intl.commands import main; ..."` or equivalently through the `Makefile` targets which use `$(SPHINXBUILD)` — because when run via `python3 -m`, the correct venv Python is found automatically.

Doc examples in Sphinx pages are display-only `code-block:: python` blocks, NOT tested by any CI gate. The doctest CI gate (`make doctest` / `--doctest-modules ketu/`) only covers `ketu/` module docstrings, not `docs/source/*.md`. New doc pages should use realistic `code-block:: python` examples — no `>>>` prompt needed unless they are actual docstring examples mirrored into the page. `sphinx.ext.doctest` is NOT loaded, so `.. doctest::` directives would be ignored anyway.

**Primary recommendation:** Three plans — (1) update the 12 existing pages to v1.3 API surface, (2) create 4 new pages for the major new feature areas, (3) run the gettext pipeline to create/update `.po` files and verify the fr build is clean. The shebang bug must be worked around by always using `python3 -m sphinx.cmd.build` and `python3 -m` equivalents.

---

## Standard Stack

### Core (all installed in venv at /home/loc/workspace/ketu/venv/)

| Library | Version | Purpose |
|---------|---------|---------|
| sphinx | 9.1.0 | HTML build engine |
| myst-parser | 5.0.0 | MyST Markdown parsing |
| sphinx-intl | 2.3.2 | gettext `.po` file management |
| sphinx-rtd-theme | installed | Read the Docs HTML theme |
| sphinx-copybutton | 0.5.2 | Copy buttons on code blocks |
| sphinx-autodoc-typehints | 3.6.2 | Type hint rendering |

### Gotcha: Broken Shebang

`venv/bin/sphinx-intl` and `venv/bin/sphinx-build` have shebang `#!/home/loc/workspace/solaris/ketu/venv/bin/python3` (old path, does not exist). Invoking these scripts directly raises `Exit code 127: can't execute: required file not found`.

**Workaround: always call via `python3 -m`:**
- Build HTML: `python3 -m sphinx.cmd.build -b html source build/html`
- Extract POT: `python3 -m sphinx.cmd.build -b gettext source build/gettext`
- Update PO: `python3 -c "from sphinx_intl.commands import main; import sys; sys.argv = ['sphinx-intl', 'update', '-p', 'build/gettext', '-l', 'fr', '-d', 'locale']; main()"`
- Build MO: `python3 -c "from sphinx_intl.commands import main; import sys; sys.argv = ['sphinx-intl', 'build', '-d', 'locale']; main()"`

Alternatively: `SPHINXBUILD="python3 -m sphinx.cmd.build" SPHINXINTL="python3 -c 'from sphinx_intl.commands import main; import sys; sys.argv[0]=...; main()'"` — but the `Makefile` already handles this if `python3` is the active venv python (verified: `which python3` → `venv/bin/python3`).

**Simplest approach from repo root:** Run everything via `make -C docs ...` targets after verifying `python3 -m sphinx.cmd.build --version` works. Alternatively, the Makefile's `$(SPHINXBUILD)` variable can be overridden: `make -C docs html SPHINXBUILD="python3 -m sphinx.cmd.build"`.

---

## Sphinx + MyST + gettext Mechanics (Repo-Specific)

### Command Sequence

All commands run from `docs/` directory:

**Step A — Build English HTML:**
```bash
cd docs
python3 -m sphinx.cmd.build -b html source build/html
# Or: make html SPHINXBUILD="python3 -m sphinx.cmd.build"
```
Currently produces: **1 warning** (`display_version` not supported by rtd theme — pre-existing, not new).

**Step B — Extract POT files (run after editing source):**
```bash
cd docs
python3 -m sphinx.cmd.build -b gettext source build/gettext
```
Produces one `.pot` file per `.md` source page in `build/gettext/`. A new `.md` page produces a new `.pot` file.

**Step C — Update PO files for French:**
```bash
cd docs
python3 -c "
from sphinx_intl.commands import main
import sys
sys.argv = ['sphinx-intl', 'update', '-p', 'build/gettext', '-l', 'fr', '-d', 'locale']
main()
"
```
For EXISTING pages: updates entries, marks obsolete strings (no fuzzy entries found in current PO files). For NEW pages: **creates new `.po` files** under `locale/fr/LC_MESSAGES/<pagename>.po` with all msgids untranslated (`msgstr ""`). Verified: `sphinx-intl update` creates new `.po` files automatically for new `.pot` files.

**Step D — Build MO files (binary compilation):**
```bash
cd docs
python3 -c "
from sphinx_intl.commands import main
import sys
sys.argv = ['sphinx-intl', 'build', '-d', 'locale']
main()
"
```

**Step E — Build French HTML:**
```bash
cd docs
python3 -m sphinx.cmd.build -b html -D language=fr source build/html-fr
# Or: make html-fr SPHINXBUILD="python3 -m sphinx.cmd.build"
```
Currently produces: **27 warnings** (26 from `examples.md` highlighting failures due to emoji in code strings — pre-existing, not new; 1 is the `display_version` warning, rest are `myst.xref_missing` for broken `UPGRADING.md` links).

**Important: untranslated strings fall back to English** — the French build does NOT fail on untranslated strings. It renders the English original. This means the new pages will build fine in fr even before translations are added (they just appear in English in the fr build).

### `docs/migrate_translations.py` — Role and Limitations

This is a one-time migration tool, NOT the ongoing translation workflow. It was written to port translations from an old `docs/fr/` directory structure to the gettext `.po` format. It:
- Reads English source `.md` files and old French `.md` files from `docs/fr/`
- Fuzzy-matches paragraphs using `difflib.SequenceMatcher`
- Populates `.po` files with matched translations

**For Phase 25: `migrate_translations.py` is NOT relevant.** There is no `docs/fr/` directory in the current repo. The ongoing translation pipeline is: edit English source → `make gettext` → `sphinx-intl update` → edit `.po` files → `sphinx-intl build` → `make html-fr`. The planner should NOT plan to use `migrate_translations.py` for Phase 25.

### toctree — How New Pages Are Registered

`docs/source/index.md` has two toctrees:
- User Guide: `installation`, `quickstart`, `concepts`, `examples`, `api`, `changelog`
- Developer Guide: `migration`, `architecture`, `performance`, `contributing`, `acknowledgments`

**New pages must be added to the toctree in `index.md`**. The new pages for DOC-11 (relational charts, predictive returns, Arabic Parts, Chiron) should go in the User Guide toctree, inserted before `api` and `changelog`.

Recommended toctree placement for new pages:
```
# User Guide toctree:
installation
quickstart
concepts
examples
houses          # new (house systems)
relational_charts   # new (synastry + composite)
predictive_charts   # new (returns)
arabic_parts       # new (Arabic Parts / Hermetic Lots)
chiron             # new (14th body)
API <api>
changelog
```

---

## Current State of the 12 Source Pages

### Pages Needing Major Updates

| Page | Current Coverage | v1.1/v1.2/v1.3 Content to Add |
|------|-----------------|-------------------------------|
| `index.md` | v1.0 feature table (12 bodies, no Chiron); toctree misses new pages | Add Chiron to body table; add new pages to toctree; update overview bullet list; bump version refs |
| `api.md` | Hand-written; covers ONLY v0.4-v1.0 functions — all via `ketu.long()`, `ketu.calculate_aspects()` etc (broken: these are NOT in `ketu.__all__`); misses all v1.1/v1.2/v1.3 APIs entirely | Fix import paths; add sections for `ketu.houses`, `ketu.charts`, `ketu.synastry`, `ketu.composite`, `ketu.returns`, `ketu.parts`; add Chiron body ID; add configurable aspects presets |
| `concepts.md` | v1.0 aspect list (14 aspects, good); v1.0 body count (13, no Chiron); no concept of house systems, no chart concept, no returns, no Arabic Parts | Add Chiron; add house systems concept; add sect concept for Arabic Parts |
| `quickstart.md` | All examples use `ketu.long()`, `ketu.calculate_aspects()` etc — these are NOT exported from `ketu` top-level (`__all__`). Examples are BROKEN relative to current API. | Fix to use `from ketu.calculations import long` etc; add a compute_chart quickstart snippet |
| `examples.md` | v1.0 examples only; emoji in code strings causing 4 syntax-highlight warnings | Fix emoji-in-strings warnings; add examples for new features |
| `architecture.md` | v0.3.0 module structure (mentions `ketu/__init__.py`, `core.py`, `calculations.py`, etc.); completely missing all new subpackages | Update module tree to v1.3; add new subpackage descriptions |
| `changelog.md` | Stops at v1.0.0 (2026-02-12); no v1.1, v1.2, v1.3 entries | Add v1.1.0, v1.2.0, v1.3.0 sections |
| `migration.md` | v0.4.0 → v1.0.0 only | Add v1.0.0 → v1.1.0, v1.1 → v1.2, v1.2 → v1.3 sections (breaking change: 13→14 bodies D-08) |

### Pages Needing Minor Updates

| Page | What to Update |
|------|---------------|
| `installation.md` | Update version number `1.0.0` → `1.3.0`; add `[dev]` extra mention |
| `performance.md` | Mostly OK; update module paths (e.g. `from ketu.aspects import...` not `ketu.calculate_aspects_batch`); verify examples still work |
| `contributing.md` | Update architecture tree; update coverage target to 100%; fix pyswisseph reference (now only in tests) |
| `acknowledgments.md` | Minor: add v1.3 GSD phase mentions if desired |

### `api.md` Is Hand-Written (Critical Finding)

`api.md` does NOT use `.. automodule::` or `.. autosummary::`. It is entirely hand-written prose. Every new subpackage must be manually documented with its function signatures and field layouts. This means adding sections for `ketu.houses`, `ketu.charts`, `ketu.synastry`, `ketu.composite`, `ketu.returns`, `ketu.parts`, and updating the body table for Chiron.

### `conf.py` Version Is Frozen

`docs/source/conf.py` line 12-13: `release = "1.0.0"` and `version = "1.0.0"`. These need updating to `1.3.0`.

---

## New Pages to Create (DOC-11)

Four new pages covering the major new feature areas. File paths under `docs/source/`.

### 1. `houses.md` — Six House Systems

Covers `ketu.houses` (v1.1/v1.2). Content:
- `SYSTEMS` dict: `placidus`, `koch`, `porphyry`, `whole_sign`, `equal`, `regiomontanus`
- `calculate_houses(jd, lat, lon, system, polar_fallback)` — scalar and batch
- `house_of(planet_lon, cusps)` — vectorised
- `HOUSES_DTYPE` fields: `jd`, `lat`, `lon`, `system`, `cusps`, `asc`, `mc`, `armc`, `vertex`
- `HighLatitudeError` + `polar_fallback` parameter
- Concept: why house systems differ
- Runnable example: Paris chart, batch, `house_of` for multiple planets

### 2. `relational_charts.md` — Synastry + Composite

Covers `ketu.charts`, `ketu.synastry`, `ketu.composite` (v1.2). Content:
- `compute_chart(jd, lat, lon, system, aspects, polar_fallback)` → `CHART_DTYPE`
- `CHART_DTYPE` fields: `jd`, `lat`, `lon`, `system`, `body_lons[14]`, `body_lats[14]`, `body_speeds[14]`, `cusps[12]`, `asc`, `mc`, `armc`, `vertex`, `aspect_matrix[14,14]`, `aspect_orbs[14,14]`
- `is_day_chart(jd, lat, lon)` — sect helper
- `calculate_synastry(chart_a, chart_b, aspects, orbs, mode)` → `SYNASTRY_DTYPE`
- `SYNASTRY_DTYPE` fields: `body_a`, `body_b`, `lon_a`, `lon_b`, `aspect_type`, `orb`, `applying`, `orb_limit`
- `calculate_composite(chart_a, chart_b, system)` → `CHART_DTYPE`
- `circular_midpoint(lon_a, lon_b)` — utility
- Runnable example: compute two charts, synastry between them, composite chart

### 3. `predictive_charts.md` — Solar + Lunar Returns

Covers `ketu.returns` (v1.2). Content:
- `solar_return(natal_jd, natal_lat, natal_lon, target_year, return_lat, return_lon, system)` → `CHART_DTYPE`
- `lunar_return(natal_jd, natal_lat, natal_lon, target_jd, return_lat, return_lon, system)` → `CHART_DTYPE`
- Key asymmetry: `solar_return` takes `target_year` (int), `lunar_return` takes `target_jd` (float)
- Relocation: `return_lat/lon=None` → natal location; non-None → relocated return
- UTC-only contract
- Runnable examples: solar return for 2026, lunar return search from current date

### 4. `arabic_parts.md` — Arabic Parts / Hermetic Lots

Covers `ketu.parts` (v1.2). Content:
- `PARTS` registry: `fortune`, `spirit`, `marriage` (built-in)
- `calculate_part(part_name, chart)` → `float` (longitude)
- `calculate_all_parts(chart, parts=None)` → `dict[str, float]`
- `register(name, day_formula, night_formula, description)` — extend the registry
- Sect-awareness: Fortune/Spirit invert day vs night; Marriage is fixed
- Formula signature: `(asc_lon, sun_lon, moon_lon, venus_lon) -> float`
- Runnable example: compute chart, calculate Fortune/Spirit/Marriage

### 5. `chiron.md` — Chiron (14th Body, v1.3)

Covers Chiron as body_id=13 (v1.3). Content:
- Body ID 13 = Chiron (confirmed: `bodies['name'][13] == b'Chiron'`)
- Range: 1950-2050 (Chebyshev `.npz` embedded in package)
- Accuracy: max error 0.005695° (sub-arcminute)
- Use `body_id=13` in all standard functions: `long(jd, 13)`, `lat(jd, 13)` etc.
- `compute_chart` returns `body_lons[14]` — index 13 is Chiron
- Breaking change note: CHART_DTYPE body axis expanded from 13→14 (D-08 in v1.3)
- Runnable example: Chiron longitude at J2000, Chiron in a chart

**Note on page naming:** "chiron" or "chiron_body" are both fine. The planner may consolidate pages differently, e.g. Chiron into a broader "bodies" page. The above is one reasonable breakdown.

---

## Real Public API Surface to Document

### `ketu` top-level (`ketu/__init__.py`)

Currently exports: `__version__` (1.2.0, needs bump to 1.3.0), `bodies`, `aspects`, `signs`, `HOUSES_DTYPE`, `HighLatitudeError`, `HOUSE_SYSTEMS`, `calculate_houses`, `house_of`.

**Functions documented in `api.md` as `ketu.long()`, `ketu.calculate_aspects()`, etc. are NOT in `ketu.__all__`** — they are accessible via submodule imports only:

| Documented as | Correct import path |
|--------------|-------------------|
| `ketu.long()` | `from ketu.calculations import long` |
| `ketu.lat()` | `from ketu.calculations import lat` |
| `ketu.body_sign()` | `from ketu.calculations import body_sign` |
| `ketu.is_retrograde()` | `from ketu.calculations import is_retrograde` |
| `ketu.positions()` | `from ketu.calculations import positions` |
| `ketu.body_name()` | `from ketu.calculations import body_name` |
| `ketu.utc_to_julian()` | `from ketu.ephemeris.time import utc_to_julian` |
| `ketu.local_to_utc()` | `from ketu.ephemeris.time import local_to_utc` |
| `ketu.get_aspect()` | `from ketu.aspects import get_aspect` |
| `ketu.calculate_aspects()` | `from ketu.aspects import calculate_aspects` |
| `ketu.get_orb()` | `from ketu.aspects import get_orb` |
| `ketu.print_positions()` | `from ketu.display import print_positions` |
| `ketu.print_aspects()` | `from ketu.display import print_aspects` |
| `ketu.main()` | `from ketu.cli import main` |

The updated `api.md` and `quickstart.md` must use these correct import paths, not `import ketu; ketu.long(...)`.

### `ketu.aspects` configurable aspects (v1.1)

```python
from ketu.aspects import (
    CLASSICAL,    # np.bool_ mask: [Conjunction, Sextile, Square, Trine, Opposition]
    TRADITIONAL,  # + Semi-sextile, Quincunx
    EXTENDED,     # all 14 aspects
    AspectSetSpec,  # Union[str, list, np.ndarray, None]
    resolve_aspect_set,  # (spec, default) -> np.ndarray
    calculate_aspects,   # (jdate, l_bodies, aspects=None) -> structured array
)
```

### `ketu.houses` (v1.1/v1.2)

```python
from ketu.houses import (
    calculate_houses,    # (jd, lat, lon, system="placidus", polar_fallback="raise") -> ndarray
    house_of,            # (planet_lon, cusps) -> int/array
    HOUSES_DTYPE,        # fields: jd, lat, lon, system, cusps[12], asc, mc, armc, vertex
    SYSTEMS,             # {'porphyry', 'placidus', 'koch', 'whole_sign', 'equal', 'regiomontanus'}
    HighLatitudeError,
    register,            # decorator to add new systems
)
```

### `ketu.charts` (v1.2)

```python
from ketu.charts import (
    compute_chart,   # (jd, lat, lon, system="placidus", aspects=None, polar_fallback="raise") -> ndarray
    is_day_chart,    # (jd, lat, lon) -> bool/array
    CHART_DTYPE,     # fields: jd, lat, lon, system, body_lons[14], body_lats[14],
                     #         body_speeds[14], cusps[12], asc, mc, armc, vertex,
                     #         aspect_matrix[14,14], aspect_orbs[14,14]
)
```

### `ketu.synastry` (v1.2)

```python
from ketu.synastry import (
    calculate_synastry,   # (chart_a, chart_b, aspects="classical", orbs="synastry", mode="filtered")
    SYNASTRY_DTYPE,       # fields: body_a, body_b, lon_a, lon_b, aspect_type, orb, applying, orb_limit
    SYNASTRY_BODY_COUNT,  # 16 (14 bodies + ASC + MC)
    SYNASTRY_FACTOR,      # 0.5
    ASC_MC_NATAL_ORB_DEG, # 8.0
    resolve_orb_set,
)
```

### `ketu.composite` (v1.2)

```python
from ketu.composite import (
    calculate_composite,  # (chart_a, chart_b, system="placidus") -> CHART_DTYPE scalar
    circular_midpoint,    # (lon_a, lon_b) -> float, vectorised
)
```

### `ketu.returns` (v1.2)

```python
from ketu.returns import (
    solar_return,  # (natal_jd, natal_lat, natal_lon, target_year, return_lat=None, return_lon=None, system="placidus") -> CHART_DTYPE
    lunar_return,  # (natal_jd, natal_lat, natal_lon, target_jd, return_lat=None, return_lon=None, system="placidus") -> CHART_DTYPE
)
```

### `ketu.parts` (v1.2)

```python
from ketu.parts import (
    PARTS,              # dict of PartSpec: 'fortune', 'spirit', 'marriage'
    calculate_part,     # (part_name, chart) -> float
    calculate_all_parts,# (chart, parts=None) -> dict[str, float]
    register,           # add new part
    get_part,           # retrieve PartSpec
    PartSpec,
)
```

### Chiron (v1.3) — body_id=13

No new module API — Chiron is accessed via existing calculation functions:
```python
from ketu.calculations import long, lat, dist_au, body_properties
jd = 2451545.0  # J2000
chiron_lon = long(jd, 13)   # → 251.61253866833982
chiron_lat = lat(jd, 13)
```

`ketu/ephemeris/chiron.py` contains private helpers (`_load_chiron_data`, `_chiron_scalar`, `_chiron_vec`) — NOT part of the public API. The `.npz` is in `ketu/data/chiron_coeffs.npz`, accessed via `importlib.resources`.

---

## How Examples Are Currently Expressed

### In `docs/source/*.md` files

All examples are ```` ```python ```` fenced code blocks (MyST/Markdown syntax). No `>>>` prompts. These are display-only — NOT run by any CI gate. The Sphinx `doctest` builder is NOT configured (`sphinx.ext.doctest` absent from `conf.py` extensions list).

### In `ketu/` module docstrings

NumPy-style docstrings with `Examples` section using `>>>` prompt. Run by CI gate: `python3 -m pytest --doctest-modules ketu/ --no-cov`. The `pyproject.toml` sets `doctest_optionflags = ["ELLIPSIS", "NORMALIZE_WHITESPACE"]`.

### Recommended style for new doc pages

Use ```` ```python ```` code blocks (NOT `>>>` prompts) in `.md` pages, consistent with existing pages. Examples should be realistic and correct (using the actual current import paths), but they don't need to be pytest-runnable since docs examples are not in the test suite.

**Exception:** If the planner wants to add `sphinx.ext.doctest` to `conf.py` and use `.. testsetup::` / `.. doctest::` directives, that is viable but changes the build and is a scope expansion beyond what exists. Recommend sticking to `code-block:: python` for consistency.

---

## gettext Gotchas

### How MyST Content Maps to msgids

Sphinx's gettext builder extracts translatable strings paragraph-by-paragraph. Each paragraph (separated by blank lines) becomes one msgid. Headings become their own msgid. Code blocks are NOT extracted — they appear verbatim in both languages (no translation needed for code).

### Fuzzy and Obsolete Entries

When you edit an English source paragraph, `sphinx-intl update` marks the old translation as `#, fuzzy` (the old msgstr is preserved but disabled). When a paragraph is removed, it becomes obsolete and is commented out with `#~`. Currently, there are **0 fuzzy entries** in any `.po` file — clean state. Running `update-po` after editing existing pages will add fuzzy entries for changed paragraphs, which must be reviewed and re-translated.

### New Pages Get New `.po` Files Automatically

When a new `pagename.md` is added and `make gettext` + `sphinx-intl update` is run, a new `locale/fr/LC_MESSAGES/pagename.po` is created with all msgids untranslated (`msgstr ""`). The French build succeeds (falls back to English). There is no need to manually create `.po` files.

### French Build Does NOT Fail on Untranslated Strings

Verified by live test: `sphinx-build -b html -D language=fr source build/html-fr` with 12 PO files containing many untranslated entries (`msgstr ""`) succeeds with 27 warnings, 0 errors. Untranslated strings appear in English in the French output. This is acceptable behavior; the phase success criterion is that the build completes clean (no hard failures), not that all strings are translated.

---

## What "Builds Clean" Means

### Current baseline (pre-Phase 25)

- English build: **1 warning** (`display_version` option not supported by rtd theme — pre-existing, theme-level)
- French build: **27 warnings** (4 from `examples.md` emoji-in-string highlighting failures; 4 from broken `UPGRADING.md`/`CHANGELOG.md` cross-references in `migration.md`; 1 `display_version` warning)

### Target state after Phase 25

- English build: 0 new warnings (the pre-existing 1 warning is acceptable)
- French build: 0 new warnings (the pre-existing broken xref warnings in `migration.md` can be fixed as a bonus; the emoji highlighting warnings in `examples.md` should be fixed when updating examples)
- No `-W` (warnings-as-errors) flag is currently used in `Makefile` or CI — this is not a requirement to add it

### Verification Commands for Plan Tasks

```bash
# Verify English build is clean (no new warnings):
python3 -m sphinx.cmd.build -b html docs/source docs/build/html 2>&1 | grep -c "WARNING"
# Expected: ≤ 1 (the pre-existing display_version warning)

# Verify French build is clean:
python3 -m sphinx.cmd.build -b html -D language=fr docs/source docs/build/html-fr 2>&1 | grep -c "WARNING"
# Expected: ≤ 5 (pre-existing warnings from migration.md xrefs + display_version)

# Verify MO files are up to date (non-empty):
ls -la docs/locale/fr/LC_MESSAGES/*.mo

# Verify all new pages appear in built index:
ls docs/build/html/*.html
```

### No Sphinx doc-build CI Job

The current CI (`tests.yml`) has NO job that runs `sphinx-build`. CI only runs: pytest coverage, type check, doc coverage (interrogate ≥95%), numpydoc lint, doctest-modules. The doc build verification is manual-only. Phase 25 can optionally add a CI step but this is NOT a stated requirement.

---

## Common Pitfalls

### Pitfall 1: Broken venv Shebangs

**What goes wrong:** `venv/bin/sphinx-intl` and `venv/bin/sphinx-build` scripts have shebang `#!/home/loc/workspace/solaris/ketu/venv/bin/python3` (old path). Running them directly fails with exit code 127.

**How to avoid:** Always use `python3 -m sphinx.cmd.build` and `python3 -c "from sphinx_intl.commands import main; ..."`.

### Pitfall 2: API Examples Using `ketu.long()` Style

**What goes wrong:** `api.md` and `quickstart.md` document functions as `ketu.long()`, `ketu.calculate_aspects()`, `ketu.utc_to_julian()` etc. These are NOT in `ketu.__all__` (verified: `hasattr(ketu, 'long') == False`). All examples using `import ketu; ketu.long(...)` are BROKEN.

**How to avoid:** All updated examples must use correct submodule imports: `from ketu.calculations import long`, `from ketu.aspects import calculate_aspects`, `from ketu.ephemeris.time import utc_to_julian`.

### Pitfall 3: `conf.py` Version Frozen at 1.0.0

`docs/source/conf.py` lines 12-13: `release = "1.0.0"`, `version = "1.0.0"`. Must be updated to `"1.3.0"`.

### Pitfall 4: New Pages NOT in toctree → Orphan Warning

If a new `.md` file is created but not added to any toctree in `index.md`, Sphinx raises `WARNING: document isn't included in any toctree`. The toctree in `index.md` must be updated for each new page.

### Pitfall 5: `migrate_translations.py` Is Not the Current Translation Tool

`migrate_translations.py` requires a `docs/fr/` directory (old structure, does not exist). It is a historical migration tool. The ongoing pipeline is `gettext → sphinx-intl update → edit .po → sphinx-intl build`.

### Pitfall 6: `examples.md` Emoji in Python Code Strings

`examples.md` has emoji literals inside Python strings (e.g. `"🌑 New Moon"`). Sphinx's Python lexer raises a highlighting warning for each. These are non-fatal but produce 4 warnings in the French build. When updating `examples.md`, avoid emoji in code block strings, or use `# noqa: highlighting` workarounds.

### Pitfall 7: `ketu.__version__` Is Frozen at 1.2.0

`ketu/__init__.py` line: `__version__ = "1.2.0"`. Pyproject.toml: `version = "1.2.0"`. Phase 26 (Release) will bump to 1.3.0, but the docs should say v1.3 for the features being documented. Use version references like "New in v1.3" rather than hard-coding the release number in prose.

---

## Architecture Patterns

### MyST Markdown Page Structure

Each page follows this pattern (consistent with existing pages):
```markdown
# Page Title

Brief intro paragraph.

## Section

### Subsection

```python
# Example code
from ketu.submodule import function
result = function(args)
```

## Next Steps
- Link to related pages
```

### MyST Extensions Available

`conf.py` enables: `colon_fence`, `deflist`, `dollarmath`, `html_admonition`, `html_image`, `replacements`, `smartquotes`, `substitution`, `tasklist`. All can be used in new pages.

Cross-references between pages: `[link text](pagename.md)` (MyST style, NOT rst `:doc:` roles).

### Runnable Examples Standard

For new pages, runnable examples should:
1. Import from the correct submodule path (see table above)
2. Use `jd = 2451545.0` (J2000.0 = 2000-01-01 12:00 UTC) as the standard test date
3. Use `lat=48.8566, lon=2.3522` (Paris) as the standard geographic location
4. Show both scalar and batch usage where applicable
5. Show the structured array field access pattern: `result["field_name"]`

---

## Open Questions

1. **Should `houses.md` be a new page or integrated into an updated `concepts.md`?**
   - What we know: `concepts.md` is 285 lines, already covers orbs, aspects, retrogradation
   - What's unclear: how much house-system theory is needed vs just API reference
   - Recommendation: create a separate `houses.md` as both concepts + API for house systems; keep `concepts.md` focused on celestial mechanics

2. **How many of the 56 module doctests reference old API patterns (`ketu.long` style)?**
   - What we know: `ketu.__init__.py` exports only `bodies`, `aspects`, `signs`, `HOUSES_DTYPE` etc.
   - What's unclear: whether the module-level doctests in `ketu/__init__.py` are affected
   - Recommendation: run `make doctest` before and after the update to verify the gate stays green

3. **Should the French translations for new pages contain substantive French content in Phase 25, or just leave them with empty `msgstr` (English fallback)?**
   - What we know: empty `msgstr` → English fallback in fr build; build does not fail
   - Recommendation: leave new pages' `.po` files with English fallback for now (Phase 25 scope is regeneration, not full translation); mark as "phase 26 or volunteer translation"

4. **Should `conf.py` `release`/`version` be bumped to 1.3.0 in Phase 25?**
   - What we know: currently frozen at `"1.0.0"` in `conf.py`; `ketu.__version__ = "1.2.0"` in `__init__.py`; pyproject.toml says `1.2.0`
   - Recommendation: bump `conf.py` to `"1.3.0"` as part of Phase 25 (the docs are documenting v1.3 features); leave pyproject.toml and `__init__.py` for Phase 26 release

---

## Sources

### Primary (HIGH confidence — all verified by direct file reads and live test runs)

- `/home/loc/workspace/ketu/docs/source/conf.py` — Sphinx configuration, extensions, i18n settings
- `/home/loc/workspace/ketu/docs/Makefile` — Build command sequence, sphinx-intl invocations
- `/home/loc/workspace/ketu/docs/migrate_translations.py` — Historical migration tool, role analysis
- `/home/loc/workspace/ketu/docs/source/*.md` (all 12 pages) — Current content audit
- `/home/loc/workspace/ketu/docs/locale/fr/LC_MESSAGES/*.po` — Translation state, fuzzy/untranslated counts
- `/home/loc/workspace/ketu/ketu/aspects/__init__.py` — configurable aspects public API
- `/home/loc/workspace/ketu/ketu/houses/__init__.py` — house systems public API
- `/home/loc/workspace/ketu/ketu/charts/__init__.py` — charts public API
- `/home/loc/workspace/ketu/ketu/synastry/__init__.py` — synastry public API
- `/home/loc/workspace/ketu/ketu/composite/__init__.py` — composite public API
- `/home/loc/workspace/ketu/ketu/returns/__init__.py` — returns public API
- `/home/loc/workspace/ketu/ketu/parts/__init__.py` — Arabic Parts public API
- `/home/loc/workspace/ketu/ketu/__init__.py` — top-level exports (verified `__all__`)
- `/home/loc/workspace/ketu/.github/workflows/tests.yml` — CI gates (no Sphinx build job)
- `/home/loc/workspace/ketu/pyproject.toml` — doctest options, interrogate config
- Live test: `python3 -m sphinx.cmd.build -b html` → 1 warning (English)
- Live test: `python3 -m sphinx.cmd.build -b html -D language=fr` → 27 warnings (French)
- Live test: `sphinx-intl update` → creates new PO files for new POT files

---

## Metadata

**Confidence breakdown:**
- Sphinx + gettext mechanics: HIGH — tested with live builds
- API surface: HIGH — verified via Python imports and inspect.signature
- Current page content: HIGH — full reads of all 12 pages
- Translation behavior (fallback to English): HIGH — verified by live fr build
- Pitfalls (shebang, broken API examples): HIGH — verified by direct testing

**Research date:** 2026-05-29
**Valid until:** Stable for this milestone (no external dependencies changing)
