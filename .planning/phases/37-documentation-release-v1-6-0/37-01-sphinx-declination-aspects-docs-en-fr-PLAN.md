---
phase: 37-documentation-release-v1-6-0
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - docs/source/concepts.md
  - docs/source/api.md
  - docs/locale/fr/LC_MESSAGES/concepts.po
  - docs/locale/fr/LC_MESSAGES/api.po
autonomous: true

must_haves:
  truths:
    - "docs/source/concepts.md has a NEW '## Declination Aspects — New in v1.6' section (after the v1.5 'CHART_DTYPE — body_decl field' subsection, before '## Aspect Configurations') covering ALL FIVE DECLA-05 items: signed-δ parallel/contra-parallel definitions with the STRICT same-hemisphere rule; the body-derived orb formula with the worked Sun/Moon = 1.0° example; the biodynamic framing (parallel ≈ conjunction / contra-parallel ≈ opposition on the δ axis); the explicit 'parallel ≠ longitude conjunction' distinction; and the // / # symbol conventions with P / CP text abbreviations"
    - "docs/source/api.md has a NEW '## Declination Aspects (`ketu.declination`) — New in v1.6' section (after '## Equatorial Declination (`ketu.calculations`) — New in v1.5' at line ~920, before '## Chiron (body_id=13) — New in v1.3' at line ~966) documenting find_declination_aspects, declination_aspect_masks, DeclinationAspectMasks, DECLA_ASPECT_DTYPE (5 fields body1/body2/kind/gap/orb), DECLA_COEF (1/12), MIN_DECL_ORB (0.5) — with the correct import path `from ketu.declination import ...` and the live dtype (body1/body2 are i1)"
    - "The docs explicitly state the zero-sign trap (δ=0 forms NEITHER aspect) and the OOB-interaction note (OOB bodies participate in detection mechanically identically; 'both OOB' is an interpretive annotation the caller composes via is_out_of_bounds, NOT a detection flag)"
    - "Every NEW English msgid introduced by the two doc edits has a French msgstr in docs/locale/fr/LC_MESSAGES/concepts.po and api.po — verified by `make -C docs gettext && make -C docs update-po` leaving ZERO empty `msgstr \"\"` for the new declination-aspects strings (msgfmt --statistics reports 0 untranslated for the new entries)"
    - "make -C docs html-fr builds with NO 'inconsistent' / fuzzy warnings on the new strings, and the rendered FR concepts page contains 'parallèle' and 'contre-parallèle' (the .mo compile path works end-to-end)"
    - "Full suite still green and version metadata UNCHANGED here (still 1.5.0): this plan is docs-only, touches NO ketu/ source, NO version files, NO changelog — `git diff --name-only` shows only the 4 files_modified"
  artifacts:
    - path: "docs/source/concepts.md"
      provides: "EN prose: parallel/contra definitions + orb formula + biodynamic framing + parallel≠conjunction + symbols (DECLA-05)"
      contains: "Declination Aspects"
    - path: "docs/source/api.md"
      provides: "EN API reference for ketu.declination (find_declination_aspects, declination_aspect_masks, DECLA_ASPECT_DTYPE, DECLA_COEF, MIN_DECL_ORB)"
      contains: "find_declination_aspects"
    - path: "docs/locale/fr/LC_MESSAGES/concepts.po"
      provides: "French translation of the new concepts declination-aspects strings"
      contains: "contre-parallèle"
    - path: "docs/locale/fr/LC_MESSAGES/api.po"
      provides: "French translation of the new api declination-aspects strings"
      contains: "find_declination_aspects"
  key_links:
    - from: "docs/source/concepts.md new section"
      to: "ketu.declination.find_declination_aspects behavior"
      via: "prose describes sign(δ₁)==sign(δ₂)≠0 ∧ |δ₁−δ₂|≤orb (parallel) and the 1/12 orb coefficient → Sun/Moon 1.0°"
      pattern: "1/12|0\\.0833|same.hemisphere|same side"
    - from: "docs/source/api.md new section"
      to: "DECLA_ASPECT_DTYPE live definition"
      via: "documents the 5 fields body1/body2/kind/gap/orb with kind ∈ {P, CP}"
      pattern: "DECLA_ASPECT_DTYPE"
    - from: "docs/locale/fr/LC_MESSAGES/*.po new msgstr"
      to: "make html-fr rendered French pages"
      via: "sphinx-intl build (.mo recompile) — empty msgstr falls back to English"
      pattern: "msgstr \"[^\"]"
---

<objective>
Author the v1.6 declination-aspects FEATURE DOCUMENTATION (DECLA-05) in English
and French. This is the new chantier that v1.5 did NOT have — v1.5 only
date-stamped changelogs; Phase 37 adds a genuine feature-doc surface for the
parallel/contra-parallel detector shipped in Phase 36.

Add a prose section to `docs/source/concepts.md` and an API-reference section to
`docs/source/api.md`, both placed immediately after their existing v1.5
equatorial-declination sections (IA consistency: declination δ lives in concepts
+ api, so declination ASPECTS live next to it — NOT in a new standalone page).
Then regenerate the gettext templates, update the French `.po` catalogs, translate
the new strings, and confirm `make html-fr` compiles the `.mo` end-to-end so the
French docs do NOT fall back to English (LOCKED reminder
project_fr_translations_before_release).

Purpose: DECLA-05 — readers get the full parallel/contra-parallel documentation in
both English and French BEFORE the release. The five mandatory items are: (1)
signed-δ definitions with the strict same-hemisphere rule, (2) the body-derived
orb formula with the worked Sun/Moon = 1.0° example, (3) the biodynamic framing
(parallel ≈ conjunction / contra-parallel ≈ opposition on the δ axis), (4) the
explicit "parallel ≠ longitude conjunction" distinction, and (5) the // / #
symbol conventions with P / CP text abbreviations.
Output: a new concepts section + a new api section (EN) and their faithful French
translations in concepts.po / api.po, with the `.mo` build verified. NO source
code, version, or changelog changes — those are 37-02's job (parallel-safe, no
file overlap).
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/research/DECLINATION_ASPECTS.md
@docs/source/concepts.md
@docs/source/api.md
@docs/Makefile
@ketu/declination/__init__.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Author the EN concepts.md "Declination Aspects" section (the 5 DECLA-05 items)</name>
  <files>docs/source/concepts.md</files>
  <action>
    Insert a NEW top-level section into `docs/source/concepts.md`. PLACEMENT:
    immediately AFTER the existing v1.5 declination block — i.e. after the
    `### CHART_DTYPE — body_decl field (New in v1.5)` subsection's code block ends
    (around line ~445) and BEFORE the next top-level heading. Read the file first
    to find the exact line where the `## Equatorial Declination — New in v1.5`
    section ends so the new `## Declination Aspects — New in v1.6` is a sibling
    top-level `##` heading inserted right after it. Do NOT renumber or alter the
    existing v1.5 section.

    The new section MUST cover ALL FIVE DECLA-05 items (authoritative source:
    `.planning/research/DECLINATION_ASPECTS.md` §1, §2, §5, §6). Write it as:

    `## Declination Aspects — New in v1.6`

    Intro line: declination aspects compare two bodies on the EQUATORIAL
    declination axis (δ), independent of ecliptic longitude. The detector lives in
    the additive `ketu.declination` subpackage (CHART_DTYPE unchanged).

    `### Parallel and Contra-Parallel`
    - **Parallel** (`P`): two bodies share the same declination δ AND are on the
      SAME side of the celestial equator (both north OR both south). Signed-δ rule:
      `sign(δ₁) == sign(δ₂) ≠ 0  AND  |δ₁ − δ₂| ≤ orb`. State that the
      same-hemisphere rule is STRICT (dominant convention across Sepharial, Carter,
      Cafe Astrology, Lunarium, McAfee, Kerykeion, astro.com).
    - **Contra-parallel** (`CP`): equal magnitude of δ but OPPOSITE sides. Signed-δ
      rule: `sign(δ₁) ≠ sign(δ₂)  AND  both ≠ 0  AND  |δ₁ + δ₂| ≤ orb`.
    - **Zero-sign trap (MUST state):** a body exactly on the equator (δ = 0,
      `np.sign` → 0) forms NEITHER a parallel NOR a contra-parallel. Two bodies on
      the equator have 0° separation but are NOT flagged.

    `### The orb formula (body-derived)`
    - Give the formula verbatim:
      `δ_orb(b1, b2) = max((bodies['orb'][b1] + bodies['orb'][b2]) / 2 × DECLA_COEF, MIN_DECL_ORB)`
      with `DECLA_COEF = 1/12 ≈ 0.0833` and `MIN_DECL_ORB = 0.5°`.
    - WORKED Sun/Moon example (DECLA-05 mandatory): Sun orb 12° + Moon orb 12° →
      mean 12° → ×1/12 → exactly **1.0°**. Explain `1/12` is the reciprocal of the
      maximum body orb (Sun/Moon at 12°) — a justified exact fraction, not a magic
      number — chosen so Sun/Moon lands on the published 1° natal consensus.
    - Floor example: zero-orb bodies (Rahu, Ketu, Lilith — orb 0) → formula yields
      0° → floored to **0.5°** so they remain detectable.
    - Include a SMALL worked table (Sun/Moon → 1.0°, Sun/Mars → 0.833°,
      Jupiter/Saturn → 0.833°, Uranus/Neptune → 0.5°, Rahu/Lilith → 0.5° floor).

    `### Biodynamic framing`
    - Parallel ≈ conjunction by declination; contra-parallel ≈ opposition by
      declination (Sepharial: "they act as if in conjunction"; Carter couples
      parallel with conjunction). Tie to Ketu's aspect-centric biodynamics: these
      are ANGLES/relationships between bodies on the δ axis, NOT zodiacal-sign
      conventions.

    `### Parallel ≠ longitude conjunction (the key distinction)`
    - The single most important clarification (DECLA-05 mandatory): two bodies can
      be parallel in declination WITHOUT being conjunct in ecliptic longitude, and
      vice-versa. δ (equatorial) and longitude (ecliptic) are INDEPENDENT
      measurements. A "double whammy" (both conjunct AND parallel) is notably
      stronger, but the detection paths are separate —
      `find_declination_aspects` consumes ONLY `body_decl`, never longitudes.

    `### Symbols and abbreviations`
    - Glyphs: `//` (parallel, intended Unicode U+2BDD; `‖`/`⫽` text fallbacks) and
      `#` (contra-parallel, intended Unicode U+2BDE) — proposals not yet in the
      Unicode standard (David Faulks L2/16-174). Text abbreviations used as the
      `kind` field values: `P` (parallel), `CP` (contra-parallel) — matches Solar
      Fire / Astrodienst.

    `### Out-of-bounds interaction`
    - OOB bodies (|δ| > ε, via `is_out_of_bounds` from v1.5) participate in P/CP
      detection MECHANICALLY IDENTICALLY — the formula does not change. "Both OOB"
      is an INTERPRETIVE annotation the CALLER composes (e.g. by combining
      `is_out_of_bounds` with the aspect output), NOT a detection flag. Some authors
      (Boehrer, McAfee) consider two-OOB parallels especially intense — a
      delineation note only.

    Add ONE runnable Python example (fenced ```python) consistent with the file's
    style, e.g.:
      ```python
      import numpy as np
      from ketu.declination import find_declination_aspects

      decl = np.zeros(14)
      decl[0] = 20.0   # Sun  δ = +20.0°
      decl[1] = 20.5   # Moon δ = +20.5°  → same hemisphere, gap 0.5° ≤ 1.0° orb

      aspects = find_declination_aspects(decl)
      print(aspects)   # [(0, 1, 'P', 0.5, 1.0)] — Sun/Moon parallel
      ```
    Keep prose tight and consistent with the existing concepts.md voice (it uses
    `###` subsections, bold term intros, and short ```python blocks). Do NOT touch
    any other section.
  </action>
  <verify>
    `grep -q '^## Declination Aspects — New in v1.6' docs/source/concepts.md`;
    `grep -q 'same.hemisphere\|same side' docs/source/concepts.md`;
    `grep -q '1/12\|0.0833' docs/source/concepts.md` and `grep -q '1.0°\|1.000°\|exactly 1' docs/source/concepts.md` (worked Sun/Moon);
    `grep -q 'contra-parallel\|contra parallel' docs/source/concepts.md`;
    `grep -qi 'conjunction by declination\|opposition by declination' docs/source/concepts.md` (biodynamic framing);
    `grep -qi 'without being conjunct\|independent measurement\|≠ longitude\|not.*longitude conjunction' docs/source/concepts.md` (parallel≠conjunction);
    `grep -q 'find_declination_aspects' docs/source/concepts.md`;
    `grep -q 'is_out_of_bounds' docs/source/concepts.md` (OOB-interaction note);
    `grep -c '^## Equatorial Declination — New in v1.5' docs/source/concepts.md` returns 1 (existing v1.5 section intact).
  </verify>
  <done>
    concepts.md has the new `## Declination Aspects — New in v1.6` section covering
    all five DECLA-05 items (definitions + same-hemisphere rule, orb formula with
    Sun/Moon=1.0°, biodynamic framing, parallel≠conjunction, symbols P/CP and
    //#), plus the zero-sign trap and OOB-interaction note, with a runnable
    example; the v1.5 section and the rest of the file are untouched.
  </done>
</task>

<task type="auto">
  <name>Task 2: Author the EN api.md "Declination Aspects (ketu.declination)" reference section</name>
  <files>docs/source/api.md</files>
  <action>
    Insert a NEW section into `docs/source/api.md`. PLACEMENT: immediately AFTER
    the existing `## Equatorial Declination (`ketu.calculations`) — New in v1.5`
    section (starts at line ~920) and BEFORE `## Chiron (body_id=13) — New in v1.3`
    (line ~966). Read the file first to confirm the exact line where the v1.5
    declination section ends. The new heading is a sibling top-level `##`.

    Verify the public names against the LIVE subpackage before writing (do NOT
    trust prose — read `ketu/declination/__init__.py` __all__ and the live dtype).
    Confirmed live facts to document:
      - Import path: `from ketu.declination import find_declination_aspects,
        declination_aspect_masks, DeclinationAspectMasks, DECLA_ASPECT_DTYPE,
        DECLA_COEF, MIN_DECL_ORB`. These are NOT re-exported from top-level `ketu`
        (ketu.__all__ unchanged — additive-only).
      - `DECLA_ASPECT_DTYPE` live layout (5 fields): `body1` (i1), `body2` (i1),
        `kind` (U2 ∈ {"P","CP"}), `gap` (f8), `orb` (f8). NOTE: body1/body2 are
        `i1` in the LIVE dtype — document i1, not i4.
      - `DECLA_COEF = 1/12`, `MIN_DECL_ORB = 0.5`.

    Write:

    `## Declination Aspects (`ketu.declination`) — New in v1.6`

    Intro: additive subpackage detecting parallels/contra-parallels on the
    declination axis; consumes `chart["body_decl"]` (the v1.5 `(14,)` field);
    `CHART_DTYPE` is unchanged; names are reachable only via `ketu.declination.*`,
    NOT `ketu.*`.

    `### `find_declination_aspects(body_decl)``
    - Scalar/single-chart detector. Takes a `(14,)` signed-degree array
      (`chart["body_decl"]`), returns a structured array of `DECLA_ASPECT_DTYPE`
      rows: upper-triangle pairs (body1 < body2), no duplicates, sorted by
      (body1, body2). Returns `np.empty(0, dtype=DECLA_ASPECT_DTYPE)` when nothing
      is detected — NEVER `None`, never a tuple.
    - Parameters: `body_decl` (`ndarray`, shape `(14,)`, signed δ in degrees).
    - Returns: `ndarray[DECLA_ASPECT_DTYPE]`.
    - A short ```python example mirroring the concepts.md Sun/Moon parallel
      (decl[0]=20.0, decl[1]=20.5 → one `('P')` row).

    `### `declination_aspect_masks(body_decl)``
    - Vectorized batch path. Accepts `(S, 14)` or `(14,)` (promoted via
      `np.atleast_2d`), returns a `DeclinationAspectMasks` NamedTuple. Pure NumPy
      broadcasting, no Python body loop.

    `### `DeclinationAspectMasks``
    - NamedTuple with SIX fields in order: `parallel`, `contra`, `gap` (each
      `(S, 91)`), then `idx_i`, `idx_j`, `orb_pairs` (each `(91,)`). 91 =
      upper-triangle pair count for 14 bodies.

    `### `DECLA_ASPECT_DTYPE``
    - The 5-field frozen contract: `body1` (i1), `body2` (i1), `kind` (U2 ∈
      {"P","CP"}), `gap` (f8 — `|δ₁−δ₂|` for P, `|δ₁+δ₂|` for CP), `orb` (f8 — the
      orb limit used for that pair).

    `### `DECLA_COEF` and `MIN_DECL_ORB``
    - `DECLA_COEF = 1/12` (orb scaling on the declination axis);
      `MIN_DECL_ORB = 0.5°` (floor so zero-orb bodies stay detectable). One line on
      the formula `max((orb_b1+orb_b2)/2 × DECLA_COEF, MIN_DECL_ORB)` → Sun/Moon
      1.0°, Rahu/Lilith 0.5°. Cross-reference the concepts page for the full
      derivation: `[Declination Aspects](concepts.md#declination-aspects-new-in-v1-6)`
      (confirm the actual MyST anchor slug after writing concepts.md; MyST
      lowercases, replaces spaces with `-`, and drops the em-dash — verify with the
      built page or adjust the link to the real auto-slug).

    Match the api.md house style (each function as `### `name(args)`` with
    Parameters/Returns bullet lists and a fenced ```python block). Do NOT touch any
    other section.
  </action>
  <verify>
    `grep -q '^## Declination Aspects' docs/source/api.md`;
    `grep -q 'find_declination_aspects' docs/source/api.md`;
    `grep -q 'declination_aspect_masks' docs/source/api.md`;
    `grep -q 'DeclinationAspectMasks' docs/source/api.md`;
    `grep -q 'DECLA_ASPECT_DTYPE' docs/source/api.md`;
    `grep -q 'DECLA_COEF' docs/source/api.md` and `grep -q 'MIN_DECL_ORB' docs/source/api.md`;
    `grep -q 'from ketu.declination import' docs/source/api.md`;
    `grep -q 'np.empty(0' docs/source/api.md` (empty-result contract documented);
    `grep -c '^## Equatorial Declination' docs/source/api.md` returns 1 and `grep -c '^## Chiron' docs/source/api.md` returns 1 (neighbouring sections intact).
  </verify>
  <done>
    api.md has a new `## Declination Aspects (ketu.declination) — New in v1.6`
    section documenting find_declination_aspects, declination_aspect_masks,
    DeclinationAspectMasks (6 fields), DECLA_ASPECT_DTYPE (5 fields, body1/body2
    = i1), DECLA_COEF (1/12), MIN_DECL_ORB (0.5), the empty-result contract, and
    the correct `from ketu.declination import` path; neighbouring sections intact.
  </done>
</task>

<task type="auto">
  <name>Task 3: Regenerate gettext, update FR .po, translate the new strings, verify the .mo build</name>
  <files>docs/locale/fr/LC_MESSAGES/concepts.po, docs/locale/fr/LC_MESSAGES/api.po</files>
  <action>
    The new English strings in concepts.md + api.md must be translated to French
    or the FR docs fall back to English for the new section (LOCKED reminder
    project_fr_translations_before_release). Use the project's established i18n
    workflow (docs/Makefile targets), running from the repo with the venv active.

    1. Regenerate POT + update the FR PO catalogs:
       `source venv/bin/activate` then
       `make -C docs gettext` (extracts msgids from the edited .md to
       build/gettext/) and
       `make -C docs update-po` (runs `sphinx-intl update -p build/gettext -l fr`,
       appending the NEW msgids as empty-msgstr entries into
       docs/locale/fr/LC_MESSAGES/concepts.po and api.po). Only concepts.po and
       api.po should change (those are the only two source files edited) — if
       update-po touches other .po files due to line-number reference shifts, that
       is acceptable but the TRANSLATION work below is limited to the new
       declination-aspects msgids.

    2. Translate EVERY new (empty-msgstr) entry in concepts.po and api.po into
       French. Follow the existing translation idiom already in concepts.po (it
       uses « parallèle », « contre-parallèle », « déclinaison », « montante/
       descendante »; technical identifiers like `find_declination_aspects`,
       `DECLA_ASPECT_DTYPE`, `body_decl`, code fences and the worked numbers stay
       verbatim — only translate prose). Key terms:
         - parallel → parallèle ; contra-parallel → contre-parallèle
         - same hemisphere / same side → même hémisphère / même côté
         - celestial equator → équateur céleste
         - orb → orbe ; floor → plancher
         - out-of-bounds → hors limites
         - "parallel ≠ longitude conjunction" → « parallèle ≠ conjonction en
           longitude » ; independent measurements → mesures indépendantes
       Do NOT leave any new declination-aspects entry with `msgstr ""`. Do NOT
       mark them fuzzy. Update the PO-Revision-Date header line is optional.

    3. Build the French docs to compile the .mo and prove no fallback:
       `make -C docs html-fr` (this runs `build-mo` = `sphinx-intl build -d locale`
       → recompiles .mo, then `sphinx-build -D language=fr`). It MUST complete
       without errors. Then confirm the new strings rendered in French and are not
       untranslated:
         - `grep -rq 'contre-parallèle' docs/build/html-fr/concepts.html` (FR
           rendering present);
         - `msgfmt --statistics docs/locale/fr/LC_MESSAGES/concepts.po` and
           `... api.po` report 0 untranslated messages for the new entries (i.e.
           the catalogs have no empty msgstr left for the declination-aspects
           msgids — confirm with
           `! grep -A1 'declination\|parallèle\|find_declination' docs/locale/fr/LC_MESSAGES/concepts.po | grep -q 'msgstr ""'` style check, or simply scan that the new entries are filled).

    4. Clean the docs build artifacts so they are not committed:
       `make -C docs clean` (removes docs/build/). The .mo files are build
       artifacts (the repo currently commits ZERO .mo — 0 found) and MUST NOT be
       committed; only the .po source files are committed.

    Report: which .po files changed, the count of new translated entries, and the
    html-fr build result.
  </action>
  <verify>
    `make -C docs gettext` and `make -C docs update-po` complete without error;
    `git diff --name-only docs/locale/` lists concepts.po and api.po;
    no NEW declination-aspects msgid in concepts.po/api.po has an empty `msgstr ""`
    (every parallel/contra/orb/symbol string is translated to French);
    `grep -q 'contre-parallèle' docs/locale/fr/LC_MESSAGES/concepts.po`;
    `grep -q 'find_declination_aspects' docs/locale/fr/LC_MESSAGES/api.po`;
    `make -C docs html-fr` builds successfully and
    `grep -rq 'contre-parallèle' docs/build/html-fr/` matches (then build cleaned);
    `git status --porcelain docs/build` is empty (no .mo / build artifacts staged).
  </verify>
  <done>
    The new EN declination-aspects strings are extracted, the FR concepts.po and
    api.po carry complete French translations (no empty msgstr for the new
    entries, not fuzzy), `make html-fr` compiles the .mo and renders the French
    declination-aspects section (no English fallback), and no build artifacts are
    left for commit.
  </done>
</task>

</tasks>

<verification>
- concepts.md: new `## Declination Aspects — New in v1.6` section covers all 5 DECLA-05 items (signed-δ definitions + strict same-hemisphere rule, orb formula with worked Sun/Moon = 1.0°, biodynamic framing, parallel≠longitude-conjunction, // / # symbols + P/CP), plus zero-sign trap + OOB-interaction note; v1.5 section intact.
- api.md: new `## Declination Aspects (ketu.declination) — New in v1.6` section documents find_declination_aspects (empty-result contract), declination_aspect_masks, DeclinationAspectMasks (6 fields), DECLA_ASPECT_DTYPE (5 fields, body1/body2 = i1), DECLA_COEF (1/12), MIN_DECL_ORB (0.5), `from ketu.declination import` path; neighbouring sections intact.
- FR: concepts.po + api.po updated via `make gettext` + `make update-po`; every new declination-aspects msgid translated (no empty msgstr, not fuzzy); `make html-fr` builds and the rendered French page contains « contre-parallèle » (.mo compile verified end-to-end); build artifacts cleaned.
- Docs-only: `git diff --name-only` shows ONLY the 4 files_modified; no ketu/ source, version, or changelog change; full suite still green (`pytest tests/ -q` ~1654 passed, 2 skipped — unchanged, this plan does not touch tests).
</verification>

<success_criteria>
DECLA-05 satisfied for the documentation: English readers (concepts.md + api.md)
and French readers (translated .po, .mo verified) get the complete
parallel/contra-parallel documentation — signed-δ definitions with the strict
same-hemisphere rule, the body-derived orb formula with the worked Sun/Moon = 1.0°
example, the biodynamic framing (parallel ≈ conjunction / contra-parallel ≈
opposition on the δ axis), the explicit "parallel ≠ longitude conjunction"
distinction, the // / # symbols with P / CP abbreviations, plus the zero-sign trap
and the OOB-interaction note. The French .mo recompile path is verified so the FR
docs do NOT fall back to English. No source, version, or changelog change here.
</success_criteria>

<output>
After completion, create
`.planning/phases/37-documentation-release-v1-6-0/37-01-SUMMARY.md`
</output>
</content>
</invoke>
