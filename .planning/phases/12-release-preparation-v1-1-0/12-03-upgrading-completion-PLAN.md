---
phase: 12-release-preparation-v1-1-0
plan: 03
type: execute
wave: 1
depends_on: []
files_modified:
  - UPGRADING.md

autonomous: true

must_haves:
  truths:
    - "UPGRADING.md no longer claims that 'configurable aspects, houses module, CLI refactor is backward-compatible' — that statement is removed or replaced (it is misleading per RESEARCH §Pitfall 4)"
    - "UPGRADING.md has a 'CLI Default Aspect Set' subsection with explicit migration recipes for CLI users AND Python API users"
    - "UPGRADING.md has a 'Kala / Downstream Adapter Migration' subsection with a concrete API-level recipe (text only — Kala is a sibling repo; do NOT modify it from here)"
    - "UPGRADING.md has a 'Houses Module' subsection pointing to ketu.calculate_houses + ketu houses CLI subcommand and explicitly noting that ketu.ephemeris.calculate_house_cusps is REMOVED"
    - "UPGRADING.md has a 'Resolved-Config stderr Header' subsection (one short paragraph) noting the new # Aspect set: line on stderr"
    - "Existing 'Lilith (Black Moon) Calculation' subsection content is byte-identical to pre-edit state (this plan does NOT touch the well-written Lilith content)"
  artifacts:
    - path: "UPGRADING.md"
      provides: "v1.0 -> v1.1 migration recipes for all three breaking surfaces (Lilith, CLI default, houses) plus downstream adapter guidance"
      contains: "CLI Default Aspect Set"
  key_links:
    - from: "UPGRADING.md CLI Default Aspect Set recipe"
      to: "Phase 11 CLI flag --harmonics extended"
      via: "Concrete shell command shown in the recipe"
      pattern: "ketu --harmonics extended"
    - from: "UPGRADING.md Kala adapter recipe"
      to: "ketu.aspects API parameter aspects=EXTENDED"
      via: "Concrete Python snippet shown in the recipe"
      pattern: "aspects=EXTENDED|aspects=preset"
    - from: "UPGRADING.md Houses Module section"
      to: "ketu.calculate_houses + ketu houses CLI subcommand"
      via: "Code snippets demonstrating both API and CLI invocations"
      pattern: "calculate_houses|ketu houses"
---

<objective>
Close the three UPGRADING.md migration-recipe gaps RESEARCH identified.
The current UPGRADING.md `## v1.0 -> v1.1` section is excellent on Lilith
(detailed shift table, root cause, fix formula, post-fix accuracy, action
required, downstream-consumer note) but contains exactly one misleading
sentence and three missing recipes:

1. The single sentence at the bottom of the v1.1 block claims:
   > "Other v1.1 work (configurable aspects, houses module, CLI refactor)
   > is backward-compatible."

   This is **wrong** — the Phase 9 CLI default change was a deliberate
   breaking shift from EXTENDED (14 aspects) to CLASSICAL (5 aspects).
   Scripts that scrape v1.0 CLI stdout will see ~64% fewer aspect rows
   per body pair in v1.1.
2. There is no Kala / downstream-adapter recipe (REL-03 explicit).
3. There is no Houses Module migration recipe (HOU-10 removed
   `ketu.ephemeris.calculate_house_cusps` — discoverability of the
   replacement matters).

Plus a small fourth note: the new `# Aspect set:` stderr header is
mildly breaking for users who pipe stderr.

Purpose: Closes REL-03. Without this plan, Kala (sibling repo) and any
script-based v1.0 user will silently lose 9 aspect rows per body pair
on upgrade, and house-using v1.0 code will fail with `ImportError`
without an obvious fix path.

Output: Surgical UPGRADING.md edit replacing the misleading sentence
with four substantive subsections. Lilith content is left byte-identical
(the Lilith section is well-written and correct; do not touch it).
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/12-release-preparation-v1-1-0/12-RESEARCH.md

@UPGRADING.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Replace the misleading "backward-compatible" sentence with four substantive subsections</name>
  <files>UPGRADING.md</files>
  <action>
The misleading sentence is at the END of the v1.1 block, in a small
subsection titled `### Other v1.0 -> v1.1 Changes`. The exact text in
the repo right now:

```markdown
### Other v1.0 -> v1.1 Changes

Other v1.1 work (configurable aspects, houses module, CLI refactor)
is backward-compatible. See per-feature documentation and the
`CHANGELOG.md` v1.1.0 entry for non-Lilith additions.
```

This entire `### Other v1.0 -> v1.1 Changes` subsection (heading +
two-paragraph body) is to be REPLACED with four new subsections, in
this order:

1. CLI Default Aspect Set (Phase 9)
2. Kala / Downstream Adapter Migration (Phase 9)
3. Houses Module (Phase 10)
4. Resolved-Config stderr Header (Phase 9)

Use the Edit tool with old_string = the literal three-line subsection
above (heading + the misleading sentence + closing). Read UPGRADING.md
to lock the exact whitespace before authoring old_string — single
trailing newline matters for the boundary with the `---` horizontal
rule that separates the v1.1 block from the v0.4 block below.

new_string is the following four subsections (verbatim — these
recipes are based on the actual surface area of the shipped Phase 11
CLI; verify each command/import in a `grep` pass before writing if
unsure):

```markdown
### CLI Default Aspect Set (Phase 9 / ASP-04)

In v1.0, the `ketu` CLI emitted **14 aspects per body pair** by
default (the EXTENDED preset: conjunction, opposition, trine, square,
sextile, quincunx, semisextile, semisquare, sesquisquare, quintile,
biquintile, novile, septile, decile).

In v1.1, the CLI default is **CLASSICAL: the 5 major aspects only**
(conjunction, opposition, trine, square, sextile). Scripts that
parsed v1.0 CLI output will receive approximately 64% fewer aspect
rows per body pair.

The `core.aspects` array is **unchanged** (length-14, append-only —
verified by the Phase 9 invariant test in
`tests/test_aspects_invariants.py`). Positional indexing into the
array still works. Only the *default selection* the CLI applies on
top of the array changed.

**Migration recipe (CLI users)**

```bash
# Restore v1.0 default behavior (14 aspects):
ketu --harmonics extended aspects --date 2026-05-07T12:00:00Z

# Discover available presets:
ketu --list-aspect-sets

# Pin to v1.0 instead of migrating:
pip install 'ketu<1.1'
```

**Migration recipe (Python API users)**

```python
# v1.0 implicit: calculate_aspects emitted all 14 harmonics
from ketu.aspects import calculate_aspects
result = calculate_aspects(jd, bodies)  # got 14 aspects

# v1.1 default: 5 majors only. Restore v1.0 behavior explicitly:
from ketu.aspects import calculate_aspects
from ketu.aspects.presets import EXTENDED
result = calculate_aspects(jd, bodies, aspects=EXTENDED)  # 14 aspects
```

### Kala / Downstream Adapter Migration (Phase 9 / ASP-04)

If you maintain a downstream adapter that consumes Ketu's aspect
output (Kala's `KetuDataAdapter`, custom scripts, ML feature
pipelines), check whether your code depends on the **count** of
aspect rows or on a specific *named* aspect (quincunx, semisextile,
etc.) that only EXTENDED includes.

In v1.0, downstream consumers received EXTENDED implicitly. In v1.1,
they receive CLASSICAL by default — silently losing 9 rows per body
pair without any error.

**Recipe** — request EXTENDED explicitly at the API boundary:

```python
# In your adapter's Ketu call site:
from ketu.aspects.presets import EXTENDED
from ketu.aspects import calculate_aspects_batch

aspects = calculate_aspects_batch(jds, bodies, aspects=EXTENDED)
```

The `core.aspects` array remains length-14 and append-only (Kala
positional indexing unaffected). Cache keys include the aspect-set
configuration hash, so explicit `aspects=EXTENDED` produces a fresh
cache entry rather than serving stale CLASSICAL data.

> **Note:** This guidance is for *downstream maintainers* of adapters
> that depend on Ketu's CLI or Python API. It does not require any
> change inside `ketu` itself. Sibling project Kala (separate
> repository) handles its own upgrade independently.

### Houses Module (Phase 10 / HOU-10)

The v1.0 placeholder `ketu.ephemeris.calculate_house_cusps` was
**removed** because it was broken: it returned an Equal House
fallback regardless of the requested `house_system` argument and
exposed an inconsistent return shape. The replacement is the new
`ketu.houses` module.

**Migration recipe (Python API)**

```python
# v1.0 (BROKEN, now removed - ImportError in v1.1):
from ketu.ephemeris import calculate_house_cusps  # ImportError

# v1.1:
from ketu import calculate_houses, house_of, HOUSES_DTYPE
houses = calculate_houses(jd, lat, lon, system='placidus')
# houses is a HOUSES_DTYPE structured array with 12 cusps + ASC/MC/ARMC/Vertex,
# vectorised over the broadcast of (jd, lat, lon).
ascendant = houses['cusps'][..., 0]      # cusp 1 = ASC
midheaven = houses['cusps'][..., 9]      # cusp 10 = MC
which_house = house_of(planet_lon=200.0, cusps=houses['cusps'][0])  # 1..12
```

**Migration recipe (CLI)**

```bash
# Single-chart house cusps:
ketu houses --jd 2451545.0 --lat 48.85 --lon 2.35 --system placidus

# Discover available house systems and polar-fallback hints:
ketu --list-house-systems
```

Available systems: `placidus`, `koch`, `porphyry`, `equal`,
`whole_sign`. High-latitude charts (|lat| > polar_circle(jd)) raise
`HighLatitudeError` by default; pass `--polar-fallback porphyry` (CLI)
or `polar_fallback="porphyry"` (Python API) to fall back to Porphyry
houses instead.

### Resolved-Config stderr Header (Phase 11 / CLI-06)

The v1.1 CLI prints a resolved-config header to **stderr** (not
stdout) on every invocation. Example:

```text
# Ketu v1.1.0
# Aspect set: classical (5 aspects: 0, 60, 90, 120, 180)
```

Pipelines that read stdout only (`ketu ... | parser`) are
**unaffected**. Pipelines that mix stdout and stderr (`ketu ... 2>&1`)
will see two extra leading lines and may need to filter on `^# `.
Suppress entirely with `2>/dev/null` if your pipeline cannot tolerate
stderr output.

For the houses subcommand, the second line is `# House system: <name>`
instead of `# Aspect set: ...`.
```

**Verification BEFORE writing**

Confirm the misleading sentence still exists at the expected location:
```bash
grep -n "is backward-compatible" UPGRADING.md
# Expect exactly one match in the v1.0 -> v1.1 block.
```

Confirm Phase 11's actual flag is `--harmonics` (not `--aspect-set`):
```bash
grep -nE "add_argument.*--harmonics|add_argument.*--aspect-set" \
  ketu/cli/parser.py
```
Use whichever flag the parser actually exposes. As of Phase 11 SUMMARYs,
the flag is `--harmonics` accepting preset names like `classical`,
`traditional`, `extended`, `all`, plus comma lists. If both flags are
defined as aliases, prefer the canonical one used by
`tests/cli/test_aspects_cmd.py`.

**DO NOT** in this task:
- Edit the `### Lilith (Black Moon) Calculation` subsection or any of
  its sub-content (the per-date table, formula constants, post-fix
  accuracy bullets, action-required paragraph). Those stay byte-identical.
- Edit the `## v0.4.x -> v1.0.0` block or anything below the
  horizontal rule (`---`).
- Add a date stamp.
  </action>
  <verify>
```bash
# Misleading sentence is gone
! grep -q "is backward-compatible" UPGRADING.md

# All four new subsections present
grep -q "^### CLI Default Aspect Set " UPGRADING.md
grep -q "^### Kala / Downstream Adapter Migration " UPGRADING.md
grep -q "^### Houses Module " UPGRADING.md
grep -q "^### Resolved-Config stderr Header " UPGRADING.md

# Concrete CLI recipe present
grep -q "ketu --harmonics extended" UPGRADING.md
grep -q "ketu --list-aspect-sets" UPGRADING.md
grep -q "ketu --list-house-systems" UPGRADING.md

# Concrete Python API recipe present
grep -q "from ketu.aspects.presets import EXTENDED" UPGRADING.md
grep -q "calculate_aspects_batch" UPGRADING.md
grep -q "from ketu import calculate_houses" UPGRADING.md
grep -q "house_of" UPGRADING.md

# stderr header note present
grep -q "# Aspect set: classical" UPGRADING.md

# Lilith content is unchanged (a few sentinel strings from the
# existing well-written content)
grep -q "MAX |delta| = 179.936579 deg" UPGRADING.md
grep -q "Recompute any cached Lilith values" UPGRADING.md
grep -q "0.002693 deg" UPGRADING.md

# v0.4.x section untouched (sanity)
grep -q "^## v0.4.x -> v1.0.0$" UPGRADING.md
```

All `grep -q` checks must succeed (and the negative `! grep -q
"is backward-compatible"` must succeed too — i.e., grep must NOT
find that phrase).

If any verify fails, re-Edit and re-run verify.
  </verify>
  <done>
UPGRADING.md `## v1.0 -> v1.1` block now ends with four substantive
migration subsections (CLI default, Kala adapter, Houses Module,
stderr header) instead of a single misleading "backward-compatible"
sentence. All three RESEARCH-identified missing recipes are added.
The Lilith section is byte-identical to pre-edit state.
  </done>
</task>

<task type="auto">
  <name>Task 2: Diff-review and commit</name>
  <files>(no source edits; verification + git only)</files>
  <action>
1. Diff review. Confirm only one file changed:
```bash
git status --porcelain
# Expect: M  UPGRADING.md  (and nothing else)

git diff --stat UPGRADING.md
# Expect: ~110-130 insertions, ~5-7 deletions
```

The deletions correspond to the three lines of the deleted misleading
subsection. The insertions correspond to the four new subsections.

2. Sanity render. UPGRADING.md is referenced from CHANGELOG.md and
README.md but is not the PyPI long_description (README.md is). Still,
do a quick markdown lint to catch obvious breakage:
```bash
source venv/bin/activate
python -c "
import re
with open('UPGRADING.md') as f:
    text = f.read()
# Heading hierarchy sanity: every #### is preceded somewhere by a ###
# (we're not adding ## headings here).
h2 = re.findall(r'^## ', text, re.MULTILINE)
h3 = re.findall(r'^### ', text, re.MULTILINE)
h4 = re.findall(r'^#### ', text, re.MULTILINE)
assert len(h2) >= 2, f'expected at least 2 h2 sections, got {len(h2)}'
assert len(h3) >= 5, f'expected at least 5 h3 sections in v1.1 block, got {len(h3)}'
print(f'OK headings: h2={len(h2)} h3={len(h3)} h4={len(h4)}')
# Code-fence balance check
fences = re.findall(r'^```', text, re.MULTILINE)
assert len(fences) % 2 == 0, f'unbalanced ```` fences: {len(fences)}'
print(f'OK fences: {len(fences)} (balanced)')
"
```

3. Commit:
```bash
node ./.claude/get-shit-done/bin/gsd-tools.js commit \
  "docs(12-03): add CLI / Kala / houses / stderr migration recipes to UPGRADING.md" \
  --files UPGRADING.md
```
GPG signing fallback per Plan 11-01 environmental note if needed.

4. Verify the commit:
```bash
git log -1 --oneline
git show --stat HEAD
```
  </action>
  <verify>
- `git log -1 --pretty=format:'%s'` shows
  `docs(12-03): add CLI / Kala / houses / stderr migration recipes to UPGRADING.md`
  (or close).
- `git show --stat HEAD` lists exactly one file: `UPGRADING.md`.
- `git status --porcelain` is empty.
- All `grep -q` checks from Task 1 still pass against the committed
  file.
- Heading and code-fence balance check from sub-step 2 prints OK.
  </verify>
  <done>
UPGRADING.md is updated and committed atomically on
`gsd/v1.1-milestone`. The four RESEARCH-identified migration recipes
are in place, the misleading sentence is gone, the Lilith content is
preserved verbatim. REL-03 is closed.
  </done>
</task>

</tasks>

<verification>
Phase-level verification of REL-03 after Plan 12-03:

```bash
# Misleading sentence removed
! grep -q "is backward-compatible" UPGRADING.md

# Three explicit migration recipes named by REL-03 success criterion 3
grep -q "^### CLI Default Aspect Set " UPGRADING.md           # script users (CLI)
grep -q "^### Kala / Downstream Adapter Migration " UPGRADING.md  # Kala adapter
grep -q "Recompute any cached Lilith values" UPGRADING.md     # Lilith consumers (existing)

# Houses migration recipe (HOU-10 fallout) plus stderr note
grep -q "^### Houses Module " UPGRADING.md
grep -q "^### Resolved-Config stderr Header " UPGRADING.md

# Concrete API/CLI invocations present (not just prose)
grep -qE "ketu --harmonics extended|aspects=EXTENDED" UPGRADING.md
grep -qE "ketu houses |calculate_houses\(" UPGRADING.md

# Lilith section preserved
grep -q "MAX |delta| = 179.936579 deg" UPGRADING.md

# Single-file commit landed
git show --stat HEAD | grep "UPGRADING\.md"
```
</verification>

<success_criteria>
- UPGRADING.md `## v1.0 -> v1.1` block has four new substantive
  subsections.
- Misleading "backward-compatible" sentence is removed.
- All three REL-03 migration audiences (script CLI users, Kala
  adapter, Lilith consumers) have an explicit recipe.
- Bonus: stderr header note is in place.
- Lilith section content is byte-identical to pre-edit state.
- Single commit on `gsd/v1.1-milestone` touching exactly one file.
- REL-03 closed.
</success_criteria>

<output>
After completion, create `.planning/phases/12-release-preparation-v1-1-0/12-03-SUMMARY.md`
including:
- Confirmation that the misleading sentence was successfully located
  and removed (record line number).
- Whether the actual Phase 11 CLI flag was `--harmonics` (as expected)
  or `--aspect-set` (alternate); if alternate, list the recipes that
  were updated to match.
- Commit hash.
- Any deviations (e.g., a Python API symbol named differently from
  what RESEARCH.md sketched and warranted a recipe tweak).
</output>
