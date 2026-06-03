# Phase 31: Documentation (en + fr) — Research

**Researched:** 2026-06-03
**Domain:** Sphinx (MyST-Markdown) documentation editing + gettext i18n cycle
**Confidence:** HIGH — all findings verified by reading actual files and running live builds

---

## Summary

Phase 31 is a pure documentation editing phase. All v1.4 features (generate_harmonic_aspects, Chiron orb 4°, Chiron range 1900-2100) are fully implemented in source code but completely absent from the docs. No doc source `.md` file was modified during Phases 28-30. The French gettext catalogs (17 `.po` files) are currently 100% translated and clean (verified via babel), but will accumulate fuzzies/empty entries the moment any English source `.md` is edited — requiring a full re-extract → update → translate → compile cycle for every touched page.

The Sphinx toolchain is stable and well-understood from Phase 26.1. The single accepted build warning is `display_version n'est pas supportée pour ce thème` (confirmed via live build). The planner's primary task is identifying the exact surgical string replacements per file, then wiring the gettext cycle as a follow-on wave.

**Primary recommendation:** Plan English edits in Wave 1 (independent per file), gettext cycle in Wave 2 (must follow all Wave 1 edits since extraction reads the modified source), and final build verification as the last step.

---

## 1. Docs Layout and Toolchain

### Source Format

All docs are **MyST Markdown** (`.md` files) in `docs/source/`. Sphinx is configured via `docs/source/conf.py`. The extension list includes `myst_parser` with all standard MyST extensions enabled.

**Source files relevant to Phase 31:**

| File | Primary Requirements |
|------|---------------------|
| `docs/source/concepts.md` | DOC-14, DOC-16 |
| `docs/source/migration.md` | DOC-15 |
| `docs/source/relational_charts.md` | DOC-15 |
| `docs/source/api.md` | DOC-15, DOC-16 |
| `docs/source/chiron.md` | DOC-16 |
| `docs/source/changelog.md` | DOC-15, DOC-16 (v1.4 section + fix stale 1.1 entry) |
| `docs/source/conf.py` | version bump to `1.4.0` |

### Build Commands (exact, copy-pasteable)

All commands run from repo root (not `docs/`). The Makefile VENVBIN uses `../venv/bin/` so it's relative-path sensitive — use the full python3 forms from repo root:

```bash
# English build
/home/loc/workspace/ketu/venv/bin/python -m sphinx \
  -b html docs/source docs/build/html 2>&1 | grep -E "WARNING|avertissement|réussi"

# French build
/home/loc/workspace/ketu/venv/bin/python -m sphinx \
  -b html -D language=fr docs/source docs/build/html-fr 2>&1 | grep -E "WARNING|avertissement|réussi"

# Extract POT files
cd /home/loc/workspace/ketu/docs && /home/loc/workspace/ketu/venv/bin/sphinx-build \
  -b gettext source build/gettext 2>&1

# Update .po files from new POT (merges new strings, marks changed as fuzzy)
cd /home/loc/workspace/ketu/docs && /home/loc/workspace/ketu/venv/bin/sphinx-intl \
  update -p build/gettext -l fr

# Compile .mo files from .po files
cd /home/loc/workspace/ketu/docs && /home/loc/workspace/ketu/venv/bin/sphinx-intl \
  build -d locale
```

Alternatively, `make html`, `make gettext`, `make update-po`, `make build-mo`, `make html-fr` all work from `docs/` (Makefile uses `VENVBIN = ../venv/bin`).

### Full French i18n Cycle (Phase 26.1 established workflow)

```bash
# Step 1: Edit docs/source/*.md (Wave 1 English edits)

# Step 2: Re-extract POTs
cd /home/loc/workspace/ketu/docs && make gettext
# Produces: docs/build/gettext/*.pot

# Step 3: Update .po files (marks changed strings as fuzzy, adds new strings as empty)
cd /home/loc/workspace/ketu/docs && make update-po
# Updates: docs/locale/fr/LC_MESSAGES/*.po

# Step 4: Translate ALL fuzzy/empty msgstr in touched files
# (Edit .po files directly — no babel needed since charset fix was done in Phase 26.1)
# Fuzzy entries: marked with "# , fuzzy" — translate the msgstr, remove the fuzzy flag
# New empty entries: msgstr "" — fill in French translation

# Step 5: Compile .mo files
cd /home/loc/workspace/ketu/docs && make build-mo

# Step 6: Build both and verify ≤1 warning each
cd /home/loc/workspace/ketu/docs && make html 2>&1 | grep -c "WARNING"  # must be 1
cd /home/loc/workspace/ketu/docs && make html-fr 2>&1 | grep -c "WARNING"  # must be 1
```

---

## 2. The 1-Warning Baseline

**Confirmed via live build on 2026-06-03:**

```
WARNING: l'option 'display_version' n'est pas supportée pour ce thème
La compilation a réussi, 1 avertissement.
```

Both English (`make html`) and French (`make html-fr`) builds produce **exactly 1 warning** — the `display_version` RTD theme option warning. This is the baseline. The verification step must assert `grep -c "WARNING"` returns `1` for both builds.

**Source:** `docs/source/conf.py:63` — `"display_version": True` in `html_theme_options`. This is a harmless pre-existing option that the current RTD theme version ignores. Do NOT remove it (it would change RTD behavior); just accept it as the baseline.

---

## 3. concepts.md Current State (DOC-14)

### What must change (surgical view)

**Problem 1: The Summary Table includes H5/H9/H10 (EXTENDED harmonics)**

Current table at `concepts.md:116-124`:

```
Harmonic | Division | Aspects
---------|----------|------------------
1        | 180°/1   | Conjunction (0°), Opposition (180°)
2        | 180°/2   | Square (90°)
3        | 180°/3   | Sextile (60°), Trine (120°)
5        | 360°/5   | Quintile (72°), Biquintile (144°)   ← REMOVE from table
6        | 180°/6   | Semi-sextile (30°), Quincunx (150°)
9        | 360°/9   | Novile (40°), Binovile (80°), Quadrinovile (160°)  ← REMOVE
10       | 360°/10  | Decile (36°), Tredecile (108°)    ← REMOVE
```

DOC-14 requires: keep only H1, H2, H3, H6 in the table (CLASSICAL 5 + TRADITIONAL 7 = 7 aspects from half-circle harmonics). EXTENDED (H5/H9/H10) must be moved out of the table to a prose note "available in code".

**Problem 2: The harmonic subsections H5/H9/H10 appear as full sections**

`concepts.md:98-112` contains full `####` subsections for Harmonic 5, Harmonic 9, Harmonic 10. These should be collapsed into a prose note below the table, not kept as equal-level subsections alongside H1/H2/H3/H6.

**Problem 3: The 14-row "Aspect Types and Harmonic Coefficients" table at lines 206-221**

This table lists all 14 aspects (including Decile, Novile, Quintile, Binovile, Tredecile, Biquintile, Quadrinovile). DOC-14 says the tables show only CLASSICAL(5) and TRADITIONAL(7). This table needs to be restructured — or the 7 EXTENDED aspects moved to a note/collapsed section.

**What is already CORRECT and must NOT change:**

- `concepts.md:128-132`: "Default aspect set (v1.3+): TRADITIONAL (7 half-circle aspects)" — ALREADY CORRECT
- `concepts.md:133-153`: "Configurable Aspect Sets" section listing TRADITIONAL/CLASSICAL/EXTENDED with code example — ALREADY CORRECT; EXTENDED mention here is fine (it's in code context, not in a table)
- `concepts.md:199`: "Pluto, Chiron | 4°" in Default Orbs table — ALREADY CORRECT (4° is already there from Phase 29)
- The `aspects_for_harmonics` section (lines 156-178) — ALREADY CORRECT

**New addition needed:** A section or paragraph documenting `generate_harmonic_aspects(h)` with an example and the "~2× smaller full-circle orbs" note.

**Chiron range update needed:** `concepts.md:66` says "valid range 1950–2050" — must become "valid range 1900–2100 (New in v1.4)".

---

## 4. Stale Default Claims — Complete Hit List (DOC-15)

### migration.md

**Line 58** (`docs/source/migration.md`):
```
Valid date range: 1950–2050. Attempting to compute Chiron outside this range raises a `ValueError`.
```
Must become: "Valid date range: 1900–2100 (expanded in v1.4). Out-of-range input is clamped to the nearest segment boundary — no `ValueError` is raised."

Note: The runtime behavior changed (Phase 30 switched from raising to clamping). The doc must reflect this.

**Line 131** (`docs/source/migration.md`):
```
`calculate_aspects` now accepts an optional `aspects` parameter. Without it, behavior is unchanged (EXTENDED = all 14 aspects).
```
This is in the "Upgrading from v1.0 to v1.1" section. Must become: "Without it, the v1.1 default was EXTENDED (all 14 aspects). As of v1.3, the default is TRADITIONAL (7 half-circle aspects); see [Aspects](concepts.md) for the preset table."

Also at **line 136**: `# v1.0 behavior (unchanged default)` — comment must be updated to clarify it was the v1.1 behavior (EXTENDED), not the current default.

### relational_charts.md

**Line 18** (`docs/source/relational_charts.md`):
```
- `aspects` — aspect set spec (`None` uses the default classical set)
```
Must become: "`None` uses the library default — TRADITIONAL (7 half-circle aspects, v1.3+)"

**Line 75** (`docs/source/relational_charts.md`):
```
calculate_synastry(chart_a, chart_b, aspects="classical", orbs="synastry", mode="filtered")
```
The `aspects="classical"` shown as the default in the function signature is wrong (the actual default is `"classical"` per source code `ketu/synastry/api.py`, but the DESC at line 81 says `"classical" (default)` which is also wrong for the library default). Must distinguish: "the synastry function's own default is `"classical"` (for backward-compat byte stability); the library default for `calculate_aspects` is TRADITIONAL."

**Line 81** (`docs/source/relational_charts.md`):
```
- `aspects` — aspect set: `"classical"` (default), `"traditional"`, `"extended"`, or a list/mask
```
Must note that `"classical"` is the `calculate_synastry` default (backward-compat pinned), not the library-wide default. Add a note pointing to `calculate_aspects` for the library default.

### api.md

**Line 183** (`docs/source/api.md`):
```
| `EXTENDED` | All 14 aspects | Includes full-circle minors (H5/H9/H10) |
```
The table at lines 181-183 has `| CLASSICAL | … | v1.2 and earlier default |` and `| EXTENDED | … |` with no "default" annotation. This is actually OK as written — but must add a `generate_harmonic_aspects` entry to the Aspects section (DOC-16).

**Lines 725-726** (`docs/source/api.md`):
```
- Valid date range: 1950–2050 (Chebyshev polynomial coefficients embedded in `ketu/data/chiron_coeffs.npz`)
- Accuracy: max error 0.005695° (sub-arcminute) over the 1950–2050 range
```
Must become: "Valid date range: 1900–2100 (expanded in v1.4, 2283 segments). Accuracy: max error 0.001214° over the 1900–2100 range."

### changelog.md

**Line 12** (`docs/source/changelog.md`):
```
valid range 1950–2050, max error 0.005695° (sub-arcminute)
```
Historical entry for v1.3.0. This describes what was true AT v1.3 release — keep as historical. The v1.4 changelog section (to be added) documents the range expansion.

**Line 13** (`docs/source/changelog.md`):
```
**`ketu/data/chiron_coeffs.npz`**: Embedded coefficient file (1142 segments, …)
```
Same — keep as historical v1.3 record. The v1.4 section will say "2283 segments, 1900–2100".

**Line 41** (`docs/source/changelog.md`) — under `[1.1.0]`:
```
`EXTENDED` (14 — default). … `calculate_aspects(jdate, l_bodies, aspects=None)` now accepts an aspect-set spec.
```
This is STALE. The entry accurately records what was true in v1.1 (EXTENDED WAS the default at v1.1 introduction). The stale nature is that it was later CHANGED to TRADITIONAL in v1.3. Two options: (a) add a footnote "(changed to TRADITIONAL in v1.3)"; (b) update the entry in-place. Option (a) is safer — the changelog should record history accurately.

### chiron.md

**Line 10** (`docs/source/chiron.md`):
```
| Valid date range | 1950-01-01 to 2050-12-31 (Julian Days ~2433282 to ~2469807) |
```
Must become: "1900-01-01 to 2100-12-31 (Julian Days 2415020.5 to 2488069.5) — expanded in v1.4"

**Lines 64-73** (`docs/source/chiron.md`) — the "Date Range and Error Behaviour" section:
```
Requesting Chiron outside 1950-2050 raises a `ValueError`:
```
Must become: "Input outside 1900–2100 is silently **clamped** to the nearest segment boundary — no `ValueError` is raised." The code example showing `ValueError` must be removed or replaced with a clamping example.

**Line 73** (`docs/source/chiron.md`):
```
the positional error is guaranteed to be at most 0.005695° … Phase 23
```
Must become: "max error 0.001214° over the 1900–2100 range"

---

## 5. New API to Document (DOC-16)

### generate_harmonic_aspects — function signature (verified)

Location: `ketu/aspects/harmonics.py:118`
Export: `ketu.aspects.generate_harmonic_aspects` (in `__init__.py:70`)

```python
def generate_harmonic_aspects(h: int) -> npt.NDArray[np.void]:
    """
    Generate aspect specs for integer harmonic h.
    Returns structured array with HARMONIC_DTYPE (identical to core.aspects.dtype).
    Shape: (h // 2,)
    h must be int, 2 <= h <= 64.
    """
```

**Where to document:** The `api.md` Aspects section already documents `aspects_for_harmonics` in detail (lines 189-219). `generate_harmonic_aspects` must be added as a new subsection in `api.md` between `aspects_for_harmonics` and `core.aspects columns`. Also add a brief mention in `concepts.md` "Configurable Aspect Sets" section.

**Key facts for the doc:**

- Output dtype: `HARMONIC_DTYPE` = `[("name", "S16"), ("angle", "f4"), ("coef", "f4"), ("harmonic", "i4"), ("symbol", "U4")]` — drop-in for `core.aspects`
- Angle convention: `fold_to_0_180(k · 360 / h)` for `k = 1 … h // 2` — full-circle 360° convention, folded to 0–180°
- Coef: `k / h` — used as the orb-scaling factor
- The resulting dynamic orbs are **~2× smaller** than table (half-circle) orbs because `coef = k/h` for full-circle harmonics is smaller than the equivalent half-circle coef. **This is accepted behavior — not a bug** (see Phase 28 locked decision)
- Accepts harmonics outside `{1,2,3,5,6,9,10}` — e.g. `h=7`, `h=11`, `h=17` all work
- `h=1` is excluded (produces 0 rows); `h > 64` is excluded (impractical orbs)
- Returns are passed as `dynamic_specs=` parameter to `calculate_aspects`, `find_aspects_between_dates`, and `calculate_synastry`

**Runnable example for doc:**

```python
from ketu.aspects import generate_harmonic_aspects

# Harmonic 7: 3 unique folded angles (septile family)
specs = generate_harmonic_aspects(7)
print(len(specs))          # 3
print(specs['name'])       # [b'H7-1', b'H7-2', b'H7-3']
print(specs['angle'])      # [51.43, 102.86, 154.29]
print(specs['coef'])       # [0.1429, 0.2857, 0.4286]

# Pass to calculate_aspects:
from ketu.aspects import calculate_aspects
result = calculate_aspects(jd, dynamic_specs=generate_harmonic_aspects(7))
```

**Orb note (mandatory per DOC-16):**

> **Note on orbs:** Dynamic harmonic orbs use `coef = k/h` (full-circle convention). For high harmonics this yields orbs roughly half the size of the equivalent half-circle aspect. This is accepted behaviour — the two conventions coexist without unification (see v1.4 release notes).

### Kala references in docs — NONE FOUND

Grep of all `.md` and `.rst` docs returned **zero hits** for "Kala" or "kala". DOC-16 requirement (no Kala reference) is already satisfied for the docs. Source code (`ketu/synastry/core.py`, `ketu/charts/core.py`, `ketu/aspects/calculator.py`) contains "Kala" in docstrings/comments but those are not rendered in user-facing Sphinx docs (autodoc is not used for these internal modules). No action needed for the Kala-grep requirement.

---

## 6. French Gettext Catalogs (DOC-17)

### Current State (verified via babel, 2026-06-03)

All 17 `.po` files have **0 empty msgstr, 0 fuzzy entries** — Phase 26.1 result is clean.

```
concepts.po:         300 messages, 0 empty, 0 fuzzy
migration.po:         89 messages, 0 empty, 0 fuzzy
relational_charts.po: 88 messages, 0 empty, 0 fuzzy
api.po:              188 messages, 0 empty, 0 fuzzy
chiron.po:            31 messages, 0 empty, 0 fuzzy
changelog.po:        117 messages, 0 empty, 0 fuzzy
```

### Files that will accumulate fuzzies/empties after Phase 31 Wave 1 edits

| English file to edit | Corresponding .po |
|---------------------|-------------------|
| `docs/source/concepts.md` | `docs/locale/fr/LC_MESSAGES/concepts.po` |
| `docs/source/migration.md` | `docs/locale/fr/LC_MESSAGES/migration.po` |
| `docs/source/relational_charts.md` | `docs/locale/fr/LC_MESSAGES/relational_charts.po` |
| `docs/source/api.md` | `docs/locale/fr/LC_MESSAGES/api.po` |
| `docs/source/chiron.md` | `docs/locale/fr/LC_MESSAGES/chiron.po` |
| `docs/source/changelog.md` | `docs/locale/fr/LC_MESSAGES/changelog.po` |

The `.po` files for other pages (quickstart, architecture, etc.) will NOT need re-translation unless their `.md` source is edited.

### Update-Po Behaviour After Edits

When `make update-po` runs after source edits:

- **Changed strings** → existing `msgstr` is marked `#, fuzzy` (kept as hint, must be re-translated and fuzzy flag removed)
- **New strings** (added content) → new entries with empty `msgstr ""`
- **Removed strings** → marked `#~` (obsolete, not rendered, can ignore)

The planner must include a translate-the-fuzzies step for each affected `.po` file.

### Charset Headers — Already Fixed

Phase 26.1 Plan 01 fixed the missing charset headers in all 5 problematic files. The fix survives `update-po` (verified in Phase 26.1 research). No charset fix needed in Phase 31.

### Marker-Preservation Rules (from Phase 26.1 — carry forward)

- Never add `#`/`##`/`###` heading markers in `msgstr` if they are absent from `msgid`
- Preserve `{ref}\`...\``, `{doc}\`...\``, and all `{role}\`...\`` verbatim
- Code-only msgid (entirely backtick-wrapped) → copy verbatim as `msgstr`
- Keep `**bold**` markers; translate text; add FR space before `:` (e.g., `Paramètres :`)

---

## 7. Verification Commands

### DOC-14: No EXTENDED aspects in table AND no example referencing removed aspects

```bash
# Verify H5/H9/H10 rows removed from concepts.md summary table
# This must return 0 matches:
grep -n "360°/5\|360°/9\|360°/10\|Quintile.*table\|Novile.*table\|Decile.*table" \
  /home/loc/workspace/ketu/docs/source/concepts.md
```

### DOC-15: No stale default claims

```bash
# Must return 0 hits:
grep -rn "unchanged (EXTENDED\|EXTENDED = all 14 aspects\|default classical set\|classical.*default\|aspects.*=.*\"classical\".*default" \
  /home/loc/workspace/ketu/docs/source/ -i

# Check relational_charts for the stale aspects parameter description
grep -n "classical.*default\|default.*classical" \
  /home/loc/workspace/ketu/docs/source/relational_charts.md
```

### DOC-16: generate_harmonic_aspects documented, Chiron range/orb updated, no Kala

```bash
# generate_harmonic_aspects must appear in api.md:
grep -n "generate_harmonic_aspects" /home/loc/workspace/ketu/docs/source/api.md
# Must return ≥1 hit

# Chiron range must say 1900-2100 (not 1950-2050):
grep -rn "1950\|2050" /home/loc/workspace/ketu/docs/source/
# Must return 0 hits (all stale range references removed)

# No Kala in any doc file:
grep -rn "Kala\|kala" /home/loc/workspace/ketu/docs/source/ --include="*.md"
# Must return 0 hits (already 0 — verify stays 0)
```

### DOC-17: Zero empty msgstr, builds at 1-warning baseline

```bash
# Check zero empty/fuzzy in all 6 touched .po files:
/home/loc/workspace/ketu/venv/bin/python3 -c "
from babel.messages import pofile
import os

files = [
    'docs/locale/fr/LC_MESSAGES/concepts.po',
    'docs/locale/fr/LC_MESSAGES/migration.po',
    'docs/locale/fr/LC_MESSAGES/relational_charts.po',
    'docs/locale/fr/LC_MESSAGES/api.po',
    'docs/locale/fr/LC_MESSAGES/chiron.po',
    'docs/locale/fr/LC_MESSAGES/changelog.po',
]

all_ok = True
for fpath in files:
    with open('/home/loc/workspace/ketu/' + fpath, 'rb') as f:
        cat = pofile.read_po(f)
    empty = [m for m in cat if m.id and not m.string]
    fuzzy = [m for m in cat if m.id and m.fuzzy]
    ok = len(empty) == 0 and len(fuzzy) == 0
    print(f'{os.path.basename(fpath)}: {\"OK\" if ok else \"FAIL\"} ({len(empty)} empty, {len(fuzzy)} fuzzy)')
    if not ok:
        all_ok = False

print('PASS' if all_ok else 'FAIL')
"

# Build warning counts (must be 1 each):
/home/loc/workspace/ketu/venv/bin/python -m sphinx \
  -b html docs/source docs/build/html 2>&1 | grep -c "WARNING"  # expect: 1

/home/loc/workspace/ketu/venv/bin/python -m sphinx \
  -b html -D language=fr docs/source docs/build/html-fr 2>&1 | grep -c "WARNING"  # expect: 1
```

---

## 8. Sequencing and Wave Structure

### Natural Plan Boundaries

**Wave 1 — English doc edits (all independent, can run in parallel):**

- **Plan A: concepts.md** — biggest change; restructures the harmonic section (removes H5/H9/H10 from tables, collapses their subsections, adds generate_harmonic_aspects section, updates Chiron range note). DOC-14 + part of DOC-16.
- **Plan B: migration.md** — 2 targeted fixes: (1) "EXTENDED unchanged default" stale claim in v1.0→v1.1 section; (2) Chiron date range + behavior change (ValueError → clamped). DOC-15.
- **Plan C: relational_charts.md** — 2-line fix: lines 18 and 81, stale "classical" default for aspects parameter. DOC-15.
- **Plan D: api.md** — 2 concerns: (1) add generate_harmonic_aspects subsection to Aspects section; (2) update Chiron section (lines 725-726, range + accuracy). DOC-15 + DOC-16.
- **Plan E: chiron.md** — update implementation table row (range), Date Range section (clamped vs ValueError), accuracy number. DOC-16.
- **Plan F: changelog.md** — (1) add `## [1.4.0]` section covering generate_harmonic_aspects, Chiron 1900-2100, Chiron orb 4°; (2) annotate the stale `EXTENDED (14 — default)` in v1.1 entry with "(changed to TRADITIONAL in v1.3)"; (3) update v1.3 Chiron entry. Also bump `conf.py` version to `1.4.0`.

**Wave 2 — French gettext cycle (MUST follow Wave 1 fully):**

- **Plan G:** Run `make gettext && make update-po`. Then translate all fuzzies/new-empties in `concepts.po`, `migration.po`, `relational_charts.po`, `api.po`, `chiron.po`, `changelog.po`. Compile `make build-mo`. Build both en+fr and assert ≤1 warning each.

### Ordering Constraints

```
Plans A, B, C, D, E, F (Wave 1) → all parallel (no inter-dependencies)
Plan G (Wave 2) → must wait for ALL of Wave 1 (gettext reads modified source)
```

Note: Plans D and F both touch api.md-related content but are separate files — truly independent.

---

## 9. Key Technical Details for Planner

### The "~2× smaller orbs" note — exactly what to write

Per Phase 28 locked decision (ACCEPTED, not a bug): when `generate_harmonic_aspects(h)` is used with `calculate_aspects`, the resulting orbs are approximately half those of the equivalent half-circle aspect. Example: a Septile (H7-1, angle=51.43°, coef=1/7≈0.143) with Sun-Moon would give orb `(12+12)/2 × 0.143 ≈ 1.7°` vs a Sextile (angle=60°, coef=1/3≈0.333) giving `(12+12)/2 × 0.333 ≈ 4°`. The two conventions coexist — no unification planned for v1.4.

### What EXTENDED is NOT losing — critical planner guard

EXTENDED (`ketu.aspects.EXTENDED`) still exists as a valid constant. It is ONLY being removed from **doc tables**. The docs will continue to say EXTENDED is "available in code" but won't show it in the summary table alongside CLASSICAL and TRADITIONAL. The code example in concepts.md that imports EXTENDED and calls `calculate_aspects(jd, aspects=EXTENDED)` must remain.

### Chiron clamping vs ValueError change

Phase 30 changed out-of-range Chiron input from raising `ValueError` to silent clamping. This affects:
- `chiron.md:64`: "raises a `ValueError`" → must become "is silently clamped"
- `migration.md:58`: "raises a `ValueError`" → same fix
- The code example in `chiron.md:64-70` showing the ValueError must be removed or rewritten as a clamping note

### conf.py version bump

`docs/source/conf.py:14-15` has `release = "1.3.0"` and `version = "1.3.0"`. This should be bumped to `"1.4.0"` in Plan F or as a separate sub-task.

### SYNASTRY default `aspects="classical"` (not a library default — carefully document)

The actual `calculate_synastry` function signature uses `aspects="classical"` as its default (for backward-compat byte stability — per prior decision). This is intentional and correct. The doc fix in `relational_charts.md` must NOT say "the default is TRADITIONAL" — it must clarify that `calculate_synastry`'s own default is `"classical"` (pinned for compatibility), while the library-wide `calculate_aspects` default is TRADITIONAL. These are different functions with intentionally different defaults.

---

## Common Pitfalls

### Pitfall 1: Removing EXTENDED from doc tables = removing from code
**What goes wrong:** Planner misreads DOC-14 as "delete EXTENDED from code"
**Prevention:** The locked constraint from Prior Decisions is clear: frozen 14-row `core.aspects` table unchanged. Only doc tables change.

### Pitfall 2: Breaking MyST role in translation
**What goes wrong:** Translating a `{ref}\`...\`` or `{doc}\`...\`` Sphinx role in a `.po` msgstr breaks xref resolution
**Prevention:** All MyST roles must be reproduced verbatim in msgstr (Phase 26.1 rule, carry forward)

### Pitfall 3: Missing fuzzy entries after update-po
**What goes wrong:** Only translating new empty entries but missing fuzzy entries (changed strings)
**Prevention:** Grep `.po` for both `^#, fuzzy` and empty `msgstr` after running update-po

### Pitfall 4: Forgetting conf.py version bump
**What goes wrong:** Build shows v1.3.0 but release is v1.4.0
**Prevention:** Include conf.py version bump explicitly in Plan F

### Pitfall 5: gettext run before all English edits done
**What goes wrong:** Wave 2 extraction misses some new strings (only reads current source state)
**Prevention:** Hard ordering constraint: all Wave 1 plans MUST complete before `make gettext` runs

---

## Open Questions

1. **changelog.md stale v1.1 entry** — The `EXTENDED (14 — default)` claim at changelog.md:41 records historical truth (v1.1 IS when EXTENDED was the default). Should we (a) annotate with "(changed to TRADITIONAL in v1.3)" or (b) rewrite to say "EXTENDED (14) was the initial default, changed to TRADITIONAL in v1.3"? Option (b) is cleaner but rewrites changelog history more aggressively. RECOMMENDATION: option (a) — append "(changed to TRADITIONAL in v1.3)" inline.

2. **New concepts.md section for generate_harmonic_aspects** — Where exactly should it go? RECOMMENDATION: As a new `### Dynamic Harmonic Generator (generate_harmonic_aspects)` subsection immediately after the `### Configurable Aspect Sets` subsection, before the `## Orbs` section. This keeps the aspects topic cohesive.

3. **chiron.md "New in v1.4" badges** — Should changed values be marked `(New in v1.4)`? RECOMMENDATION: yes, mirror the `(New in v1.3)` pattern already in the file.

---

## Sources

### Primary (HIGH confidence — direct file reads)

- `docs/source/concepts.md` — full read, lines 1-392
- `docs/source/migration.md` — full read, lines 1-292
- `docs/source/relational_charts.md` — full read, lines 1-173
- `docs/source/api.md` — full read, lines 1-750
- `docs/source/chiron.md` — full read, lines 1-85
- `docs/source/changelog.md` — lines 1-80
- `docs/source/conf.py` — full read
- `docs/Makefile` — full read
- `ketu/aspects/harmonics.py` — full read (generate_harmonic_aspects signature + docs)
- `ketu/aspects/presets.py` — partial read (TRADITIONAL default confirmation)
- `ketu/core.py:84` — Chiron orb=4 literal confirmed
- `ketu/ephemeris/chiron.py` — clamping behavior confirmed (no ValueError)
- `.planning/phases/26.1-french-documentation-translation/26.1-RESEARCH.md` — i18n workflow
- `.planning/phases/26.1-french-documentation-translation/26.1-VERIFICATION.md` — Phase 26.1 final state
- `.planning/phases/28-dynamic-harmonic-generator/28-01-SUMMARY.md` — Phase 28 decisions

### Build verification (HIGH confidence — live runs 2026-06-03)

- English build: `python -m sphinx -b html docs/source docs/build/html` → 1 warning (display_version)
- French build: `python -m sphinx -b html -D language=fr docs/source docs/build/html-fr` → 1 warning (display_version)
- babel `.po` check: 0 empty, 0 fuzzy across all 6 key catalogs

---

## Metadata

**Confidence breakdown:**
- Stale string locations: HIGH — exact file:line verified
- Toolchain commands: HIGH — run live, Makefile verified
- 1-warning baseline: HIGH — reproduced in live build
- generate_harmonic_aspects API: HIGH — read actual source
- Wave structure: HIGH — dependencies are clear
- French .po state: HIGH — verified via babel

**Research date:** 2026-06-03
**Valid until:** 2026-06-17 (stable toolchain; 14-day window)
