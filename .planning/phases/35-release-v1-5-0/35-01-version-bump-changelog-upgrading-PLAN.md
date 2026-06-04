---
phase: 35-release-v1-5-0
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - pyproject.toml
  - ketu/__init__.py
  - docs/source/conf.py
  - CHANGELOG.md
  - docs/source/changelog.md
  - fr/CHANGELOG.md
  - UPGRADING.md
  - README.md
autonomous: true

must_haves:
  truths:
    - "ketu.__version__ == importlib.metadata.version('ketu') == '1.5.0' (pytest tests/test_version.py green)"
    - "ALL THREE version files read '1.5.0': pyproject.toml line 7, ketu/__init__.py line 57, docs/source/conf.py lines 14-15 (release AND version) — conf.py was NOT pre-bumped by Phases 33/34, unlike Phase 32"
    - "CHANGELOG.md '## [1.5.0]' is DATE-STAMPED (Unreleased replaced with today's real UTC date); the complete pre-authored content (6 Added, 2 Changed, 2 Fixed, 2 Notes) is left BYTE-IDENTICAL — only the header date changes"
    - "CHANGELOG.md contains no '## [1.5.0] - Unreleased' and no '## [Unreleased]' section"
    - "docs/source/changelog.md '## [1.5.0]' header is date-stamped to the same UTC date; the docs body content is left untouched"
    - "fr/CHANGELOG.md has a NEW dated '## [1.5.0] - <date>' French section above '## [1.4.0] - 2026-06-03', translating the 6 Added + 2 Changed + 2 Fixed + 2 Notes bullets"
    - "UPGRADING.md has a '## v1.4 -> v1.5' section as the NEW FIRST section, above '## v1.3 -> v1.4', covering body_decl additive dtype + node-speed correction + additive API"
    - "README.md '## Roadmap' checklist gains two v1.5 entries (declination helpers + dynamic harmonic CLI) after the existing data-driven aspect engine entry"
    - "Full suite still green: pytest tests/ -q (expect ~1626 passed, 2 skipped); mypy --strict already clean (no fix task needed, unlike Phase 32)"
  artifacts:
    - path: "pyproject.toml"
      provides: "Build-system version source of truth"
      contains: "version = \"1.5.0\""
    - path: "ketu/__init__.py"
      provides: "Runtime version source of truth"
      contains: "__version__ = \"1.5.0\""
    - path: "docs/source/conf.py"
      provides: "RTD version/release source of truth (MUST be bumped — not pre-bumped)"
      contains: "release = \"1.5.0\""
    - path: "CHANGELOG.md"
      provides: "Date-stamped [1.5.0] entry (content pre-authored, untouched)"
      contains: "## [1.5.0] - 20"
    - path: "docs/source/changelog.md"
      provides: "RTD changelog with date-stamped [1.5.0]"
      contains: "## [1.5.0] - 20"
    - path: "fr/CHANGELOG.md"
      provides: "French [1.5.0] changelog section"
      contains: "## [1.5.0] - 20"
    - path: "UPGRADING.md"
      provides: "v1.4 -> v1.5 migration (body_decl additive dtype + node-speed correction + additive API)"
      contains: "## v1.4 -> v1.5"
    - path: "README.md"
      provides: "Roadmap checklist entries for v1.5 declination + dynamic harmonics"
      contains: "is_ascending_declination"
  key_links:
    - from: "pyproject.toml version"
      to: "ketu/__init__.py __version__"
      via: "test_version_matches_metadata (importlib.metadata == __version__)"
      pattern: "1\\.5\\.0"
    - from: "docs/source/conf.py release/version"
      to: "ReadTheDocs v1.5 docs branding"
      via: "Sphinx reads conf.py release/version (MUST be 1.5.0 or RTD shows stale 1.4.0)"
      pattern: "release = \"1\\.5\\.0\""
    - from: "CHANGELOG.md [1.5.0] body_decl + node-speed entries"
      to: "UPGRADING.md v1.4 -> v1.5 migration notes"
      via: "cross-reference for the additive-dtype + node-speed migration recipe"
      pattern: "body_decl"
---

<objective>
Make the v1.5.0 release candidate publication-ready by editing docs and version
metadata ONLY — there is NO source-code change and NO quality-gate fix needed
(mypy --strict is already clean, unlike Phase 32). Bump the version to 1.5.0 in
THREE source-of-truth files (pyproject.toml + ketu/__init__.py + docs/source/conf.py),
DATE-STAMP the two already-authored `[1.5.0]` changelog stubs (root CHANGELOG.md
+ docs/source/changelog.md — replace `Unreleased` with the real UTC date, do NOT
re-author the content), AUTHOR a fresh French `[1.5.0]` section in fr/CHANGELOG.md,
ADD a `## v1.4 -> v1.5` section to UPGRADING.md, and UPDATE the README Roadmap
checklist with the v1.5 additions.

Purpose: REL-01 + REL-02. v1.5.0 is an ADDITIVE minor — no breaking changes,
`is_ascending` (β) and the frozen `core.aspects` table stay byte-identical. The
release must ship with accurate version metadata across all three source-of-truth
files (so RTD renders 1.5.0, not stale 1.4.0) and complete, dated release notes
documenting the additive declination δ surface (declination / declination_velocity /
is_ascending_declination / is_out_of_bounds / body_decl) and the arbitrary-harmonic
CLI surface (--harmonics h7 / H{h}-{k} naming contract / find_aspect_timing dyn_coef).
This plan tags-ready a commit whose docs and version are release-correct.
Output: version 1.5.0 synced in all three files (sync gate green); a single dated
[1.5.0] CHANGELOG (EN root + RTD docs) with content untouched; a fresh dated French
[1.5.0] section; a complete UPGRADING v1.4 -> v1.5 section; a README Roadmap update.
No ketu/ calculation logic changed.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/35-release-v1-5-0/35-RESEARCH.md
@pyproject.toml
@ketu/__init__.py
@docs/source/conf.py
@CHANGELOG.md
@docs/source/changelog.md
@fr/CHANGELOG.md
@UPGRADING.md
@README.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Bump version to 1.5.0 in THREE files (incl. conf.py) and confirm the sync gate</name>
  <files>pyproject.toml, ketu/__init__.py, docs/source/conf.py</files>
  <action>
    Bump the version to 1.5.0 in THREE source-of-truth files. This is the
    SINGLE most important delta from Phase 32: Phase 32 bumped only TWO files
    because conf.py was pre-bumped by Phase 31. For v1.5 the OPPOSITE is true —
    Phases 33/34 did NOT pre-bump conf.py, so it is still at "1.4.0" and MUST be
    bumped here (RESEARCH Pitfall 2 + Pitfall 7). Skipping conf.py leaves RTD
    showing 1.4.0 after the release.

    Change EXACTLY these strings (verified against live files 2026-06-04):
      a. `pyproject.toml` line 7: `version = "1.4.0"` -> `version = "1.5.0"`.
      b. `ketu/__init__.py` line 57: `__version__ = "1.4.0"` ->
         `__version__ = "1.5.0"`.
      c. `docs/source/conf.py` line 14: `release = "1.4.0"` ->
         `release = "1.5.0"`.
      d. `docs/source/conf.py` line 15: `version = "1.4.0"` ->
         `version = "1.5.0"`.
    All four edits across the three files MUST be made together — bumping a
    subset fails the sync gate or freezes RTD branding.

    Then re-install the editable package so importlib.metadata picks up the new
    version, and run the sync gate:
      `pip install -e . -q && pytest tests/test_version.py -v`
    Both version tests MUST pass. (test_version.py checks pyproject.toml +
    ketu/__init__.py vs importlib.metadata — it does NOT check conf.py, which is
    why the explicit conf.py grep below is the guard for that file.)
  </action>
  <verify>
    `grep -n 'version = "1.5.0"' pyproject.toml` matches at line 7;
    `grep -n '__version__ = "1.5.0"' ketu/__init__.py` matches at line 57;
    `grep -q 'release = "1.5.0"' docs/source/conf.py` matches;
    `grep -q 'version = "1.5.0"' docs/source/conf.py` matches;
    `! grep -q '1.4.0' docs/source/conf.py` (no stale 1.4.0 left in conf.py);
    `pytest tests/test_version.py -v` is GREEN.
  </verify>
  <done>
    pyproject.toml, ketu/__init__.py, and docs/source/conf.py (both release and
    version) all read "1.5.0"; ketu.__version__ ==
    importlib.metadata.version("ketu") == "1.5.0"; test_version.py passes; no
    "1.4.0" remains in conf.py.
  </done>
</task>

<task type="auto">
  <name>Task 2: Date-stamp both changelogs (content untouched) and author the French [1.5.0] section</name>
  <files>CHANGELOG.md, docs/source/changelog.md, fr/CHANGELOG.md</files>
  <action>
    The root CHANGELOG.md and docs/source/changelog.md ALREADY have complete,
    correctly-formatted `[1.5.0]` sections authored during Phases 33/34. Unlike
    Phase 32 (which authored fresh content), this plan only DATE-STAMPS them —
    do NOT re-author or re-order any bullet (RESEARCH Pitfall 1). The fr/CHANGELOG
    is the only changelog that needs new authoring (RESEARCH Pitfall 8).

    Determine the release date: TODAY's UTC date in `YYYY-MM-DD` form via
    `date -u +%F`. Use the SAME date in all three changelog headers.

    1. CHANGELOG.md — line 10 currently reads `## [1.5.0] - Unreleased`. Replace
       ONLY `Unreleased` with the real UTC date, so it reads
       `## [1.5.0] - <date>`. Read the file first to confirm the section below it
       (6 `### Added`, 2 `### Changed`, 2 `### Fixed`, 2 `### Notes` bullets) is
       complete; leave every bullet BYTE-IDENTICAL. Leave
       `## [1.4.0] - 2026-06-03` (line ~70) and everything below untouched.

    2. docs/source/changelog.md — line 8 currently reads `## [1.5.0] - Unreleased`.
       Replace ONLY `Unreleased` with the same UTC date (RESEARCH Pitfall 3).
       Do NOT touch the docs body content (Phases 33/34 wrote it) or any other
       version header — the `## [1.2.0] - 2026-04-XX` placeholder (further down)
       is OUT OF SCOPE per established practice; the `[1.3.0]` / `[1.4.0]`
       headers are already dated.

    3. fr/CHANGELOG.md — author a NEW French `## [1.5.0] - <date>` section
       INSERTED ABOVE the existing `## [1.4.0] - 2026-06-03` (after the `---`
       separator / header block). Match the file's existing style: `### Ajouts`,
       `### Modifié`, `### Corrigé`, `### Notes` headers (see the existing
       `[1.4.0]` French section for the exact heading/bullet idiom). The EN root
       CHANGELOG.md `[1.5.0]` section is authoritative — read it and translate
       its bullets faithfully:
         ### Ajouts (6 bullets):
           - `declination(jdate, body)` — déclinaison équatoriale δ (Phase 33)
           - `declination_velocity(jdate, body)` — dδ/dt (Phase 33)
           - `is_ascending_declination(jdate, body)` — Lune montante/descendante;
             distinct de `is_ascending` (trajectoire β, inchangé) (Phase 33)
           - `is_out_of_bounds(jdate, body)` — OOB via obliquité instantanée
             ε(jd) (Phase 33)
           - `CHART_DTYPE` gagne le champ `body_decl` (additif, float64[14])
             (Phase 33)
           - surface CLI `--harmonics h<N>` (ex. `ketu --harmonics h7 …`)
             (Phase 34)
         ### Modifié (2 bullets):
           - nommage `H{h}-{k}` promu en contrat d'API public (Phase 34)
           - `find_aspect_timing` gagne le paramètre `dyn_coef=` (Phase 34)
         ### Corrigé (2 bullets):
           - vitesse moyenne des nœuds lunaires corrigée (Phase 33)
           - `calculate_aspects_batch` : lignes de paires en double éliminées
             (Phase 33)
         ### Notes (2 bullets):
           - `is_ascending` (trajectoire β) inchangé
           - impact Kala : changement de dtype additif (`body_decl`) — accès par
             nom inchangé, accès positionnel/`.view()` à adapter
       Match the EN root CHANGELOG.md bullet content where it is more specific;
       the EN file is the reference (per the fr/ header note). Leave the existing
       `## [1.4.0] - 2026-06-03` French section and below untouched.
  </action>
  <verify>
    `grep -c '^## \[1.5.0\] - 20' CHANGELOG.md` returns 1;
    `! grep -q '^## \[1.5.0\] - Unreleased' CHANGELOG.md`;
    `! grep -q '^## \[Unreleased\]' CHANGELOG.md`;
    `grep -q 'declination' CHANGELOG.md` and `grep -q 'body_decl' CHANGELOG.md`
    both match (content preserved);
    `grep -c '^## \[1.5.0\] - 20' docs/source/changelog.md` returns 1 and
    `! grep -q '^## \[1.5.0\] - Unreleased' docs/source/changelog.md`;
    `grep -c '^## \[1.5.0\] - 20' fr/CHANGELOG.md` returns 1 and
    `grep -q 'déclinaison' fr/CHANGELOG.md` matches and
    `grep -q 'body_decl' fr/CHANGELOG.md` matches.
  </verify>
  <done>
    CHANGELOG.md has exactly one dated `[1.5.0]` section (Unreleased replaced,
    pre-authored content byte-identical, no Unreleased anywhere);
    docs/source/changelog.md `[1.5.0]` is date-stamped (no Unreleased);
    fr/CHANGELOG.md has a matching dated French `[1.5.0]` section above `[1.4.0]`
    translating all 6+2+2+2 bullets.
  </done>
</task>

<task type="auto">
  <name>Task 3: Add UPGRADING v1.4 -> v1.5 section and update the README Roadmap checklist</name>
  <files>UPGRADING.md, README.md</files>
  <action>
    v1.5 is fully additive (no breaking changes), but two items warrant
    migration notes for downstream consumers — primarily Kala — and MUST NOT be
    omitted just because nothing breaks (RESEARCH Pitfall 10).

    1. UPGRADING.md — add a `## v1.4 -> v1.5` section as the NEW FIRST section,
       inserted BEFORE the existing `## v1.3 -> v1.4` (currently at line 6),
       keeping newest-first ordering. Use the exact markdown from RESEARCH
       "UPGRADING.md Required Delta -> `## v1.4 -> v1.5` content to add",
       covering three sub-sections:
         a. `### CHART_DTYPE gains body_decl — additive dtype change`:
            new `body_decl` field (`float64[14]`), purely additive, no field
            removed/reordered; NAMED field access (`chart["body_lons"]`,
            `chart["body_decl"]`) is UNAFFECTED; POSITIONAL access (`chart[..., N]`)
            or `.view()` on the raw dtype MUST adapt (byte layout changed, new
            field appended at the end); `compute_chart` and `calculate_composite`
            both populate `body_decl` automatically; Kala guidance: update
            CHART_DTYPE definitions to include body_decl, named access needs no
            change, a ratchet test pins the dtype sha256 fingerprint.
         b. `### Lunar node mean speed corrected in core.bodies`:
            `core.bodies['speed']` for Rahu (index 10) and Ketu (index 11)
            corrected from ~−0.013°/day to −0.052954°/day (true nodal regression
            rate, 360° over ~18.6 years); code reading those indices sees the
            corrected value; recompute any cached speed-ratios / adaptive step
            sizes involving the nodes; `calculate_speed_ratio` now sources
            average speeds from `core.bodies['speed']` (single source of truth).
         c. `### New API surface — additive, no migration needed`:
            list all additive entry points with their import paths —
            `from ketu.calculations import declination` (δ scalar + vectorized),
            `declination_velocity` (dδ/dt °/day), `is_ascending_declination`
            (True when dδ/dt > 0, Moon montante; DISTINCT from `is_ascending`
            β-trajectory), `is_out_of_bounds` (|δ| > instantaneous ε(jd)); the
            `--harmonics h<N>` CLI top-level flag (e.g.
            `ketu --harmonics h7 aspects --date …`); `H{h}-{k}` naming as a
            public API contract; `find_aspect_timing(..., dyn_coef=None)` optional
            backwards-compatible parameter.
       Do NOT modify the existing `## v1.3 -> v1.4` content.

    2. README.md — update the `## Roadmap` checklist (line 312). Add the
       following two entries IMMEDIATELY AFTER the existing
       `- [x] Data-driven aspect engine with harmonic-based selection` line
       (RESEARCH "README.md Required Delta", recommended Option (a) — Roadmap
       checklist update, NOT a new "What's New" section since the README has no
       v1.4 "What's New" section to be consistent with):
         - [x] Equatorial declination δ, montant/descendant, OOB helpers (`declination`,
           `is_ascending_declination`, `is_out_of_bounds`)
         - [x] Dynamic harmonic CLI (`--harmonics h7`) + `H{h}-{k}` naming contract +
           `find_aspect_timing(dyn_coef=)`
       Do NOT add a `## What's New in v1.5.0` section (no v1.4 equivalent exists
       — adding one would create an inconsistency). Do NOT modify any other
       README section.
  </action>
  <verify>
    `grep -q '^## v1.4 -> v1.5' UPGRADING.md`;
    `grep -q 'body_decl' UPGRADING.md`;
    `grep -q '0.052954\|−0.052954\|-0.052954' UPGRADING.md` (node-speed note);
    `grep -q 'is_ascending_declination' UPGRADING.md`;
    `grep -c '^## v1.3 -> v1.4' UPGRADING.md` returns 1 (existing section intact);
    `grep -q 'is_ascending_declination' README.md` and
    `grep -q -- '--harmonics h7' README.md` both match under the Roadmap;
    `! grep -q "What.s New in v1.5.0" README.md` (no inconsistent section added).
  </verify>
  <done>
    UPGRADING.md `## v1.4 -> v1.5` is the new first section with the three
    sub-sections (body_decl additive dtype + positional-access caveat,
    node-speed correction, additive API surface), with `## v1.3 -> v1.4` intact;
    README `## Roadmap` checklist has the two v1.5 entries (declination helpers +
    dynamic harmonic CLI) after the data-driven aspect engine entry; no
    "What's New" section was added.
  </done>
</task>

</tasks>

<verification>
- `pytest tests/test_version.py -v` GREEN; pyproject.toml + ketu/__init__.py + docs/source/conf.py (release AND version) all read "1.5.0"; no "1.4.0" remains in conf.py.
- CHANGELOG.md: exactly one `## [1.5.0] - <date>` section (Unreleased replaced, pre-authored content untouched, no Unreleased anywhere); `## [1.4.0] - 2026-06-03` and below unchanged.
- docs/source/changelog.md: `## [1.5.0]` date-stamped (no Unreleased).
- fr/CHANGELOG.md: dated `## [1.5.0]` French section above `[1.4.0]`, translating the 6 Added + 2 Changed + 2 Fixed + 2 Notes bullets.
- UPGRADING.md: `## v1.4 -> v1.5` first section (body_decl additive dtype, node-speed correction, additive API), `## v1.3 -> v1.4` intact.
- README.md: `## Roadmap` checklist has two v1.5 entries; no `## What's New in v1.5.0` section.
- Full suite still green: `pytest tests/ -q` (expect ~1626 passed, 2 skipped). mypy --strict already clean — no fix needed.
</verification>

<success_criteria>
REL-01 + REL-02 satisfied: version bumped to 1.5.0 in ALL THREE source-of-truth
files (pyproject.toml + ketu/__init__.py + docs/source/conf.py — the conf.py bump
is the critical Phase-32-inverted step so RTD renders 1.5.0); the root CHANGELOG
and docs RTD changelog `[1.5.0]` sections are date-stamped (content left
byte-identical — only the header date changed); fr/CHANGELOG has a fresh dated
French `[1.5.0]` section; UPGRADING documents the v1.4 -> v1.5 additive migration
(body_decl dtype + node-speed correction + additive API); README Roadmap lists the
v1.5 additions. mypy --strict is already clean (no fix task needed, unlike Phase
32). No `ketu/` calculation logic changed.
</success_criteria>

<output>
After completion, create
`.planning/phases/35-release-v1-5-0/35-01-SUMMARY.md`
</output>
