---
phase: 37-documentation-release-v1-6-0
plan: 02
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
    - "ketu.__version__ == importlib.metadata.version('ketu') == '1.6.0' (pytest tests/test_version.py green after pip install -e .)"
    - "ALL THREE version files read '1.6.0': pyproject.toml line 7 (was 1.5.0), ketu/__init__.py line 57 (was 1.5.0), docs/source/conf.py lines 14-15 release AND version (were 1.5.0) — conf.py was NOT pre-bumped by Phase 36, so it MUST be bumped here; no '1.5.0' remains in conf.py"
    - "CHANGELOG.md gains a NEW '## [1.6.0] - <today UTC date>' section as the FIRST version section (above '## [1.5.0] - 2026-06-04'), AUTHORED FROM SCRATCH (Phase 36 did NOT pre-author a [1.6.0] stub — verified live, no Unreleased stub exists), with ### Added (declination aspects subpackage: find_declination_aspects + declination_aspect_masks + DeclinationAspectMasks + DECLA_ASPECT_DTYPE + DECLA_COEF + MIN_DECL_ORB) and ### Notes (CHART_DTYPE unchanged / additive subpackage / core.aspects byte-identical)"
    - "CHANGELOG.md has NO '## [1.6.0] - Unreleased' and NO '## [Unreleased]' section"
    - "docs/source/changelog.md gains a BYTE-IDENTICAL-CONTENT '## [1.6.0] - <same date>' section above '## [1.5.0] - 2026-06-04' (RTD docs copy — same Added/Notes content as the root CHANGELOG, adapted only to the docs file's `### Added 1.6.0` heading idiom)"
    - "fr/CHANGELOG.md gains a fresh dated French '## [1.6.0] - <date>' section above '## [1.5.0] - 2026-06-04', translating the Added + Notes bullets (### Ajouts, ### Notes)"
    - "UPGRADING.md gains a '## v1.5 -> v1.6' section as the NEW FIRST section (above '## v1.4 -> v1.5' at line 6), documenting that v1.6 is purely additive: new ketu.declination subpackage, CHART_DTYPE UNCHANGED (no ratchet break), core.aspects byte-identical, no migration needed"
    - "README.md '## Roadmap' checklist gains a v1.6 entry (declination aspects / parallels & contra-parallels via ketu.declination) after the existing '- [x] Dynamic harmonic CLI' line (line ~330)"
    - "Full suite still green: pytest tests/ -q (expect ~1654 passed, 2 skipped); mypy --strict already clean (no fix task needed — docs/metadata only)"
  artifacts:
    - path: "pyproject.toml"
      provides: "Build-system version source of truth"
      contains: "version = \"1.6.0\""
    - path: "ketu/__init__.py"
      provides: "Runtime version source of truth"
      contains: "__version__ = \"1.6.0\""
    - path: "docs/source/conf.py"
      provides: "RTD version/release source of truth (MUST be bumped — not pre-bumped)"
      contains: "release = \"1.6.0\""
    - path: "CHANGELOG.md"
      provides: "Authored-from-scratch dated [1.6.0] entry (declination aspects)"
      contains: "## [1.6.0] - 20"
    - path: "docs/source/changelog.md"
      provides: "RTD changelog with byte-identical-content dated [1.6.0]"
      contains: "## [1.6.0] - 20"
    - path: "fr/CHANGELOG.md"
      provides: "French [1.6.0] changelog section"
      contains: "## [1.6.0] - 20"
    - path: "UPGRADING.md"
      provides: "v1.5 -> v1.6 migration (purely additive: ketu.declination, CHART_DTYPE unchanged)"
      contains: "## v1.5 -> v1.6"
    - path: "README.md"
      provides: "Roadmap checklist entry for v1.6 declination aspects"
      contains: "ketu.declination\|Declination aspects\|parallels"
  key_links:
    - from: "pyproject.toml version"
      to: "ketu/__init__.py __version__"
      via: "test_version_matches_metadata (importlib.metadata == __version__)"
      pattern: "1\\.6\\.0"
    - from: "docs/source/conf.py release/version"
      to: "ReadTheDocs v1.6 docs branding"
      via: "Sphinx reads conf.py release/version (MUST be 1.6.0 or RTD shows stale 1.5.0)"
      pattern: "release = \"1\\.6\\.0\""
    - from: "CHANGELOG.md [1.6.0] content"
      to: "docs/source/changelog.md [1.6.0] content"
      via: "byte-identical content requirement (root EN ↔ RTD docs copy)"
      pattern: "find_declination_aspects"
---

<objective>
Make the v1.6.0 release candidate publication-ready by editing version metadata
and changelogs ONLY — NO source-code change, NO quality-gate fix (mypy --strict is
already clean; this is a docs+metadata-only release like v1.5). Bump the version
to 1.6.0 in THREE source-of-truth files (pyproject.toml + ketu/__init__.py +
docs/source/conf.py — conf.py is at 1.5.0 and MUST be bumped or RTD renders stale
1.5.0). AUTHOR a fresh `[1.6.0]` changelog FROM SCRATCH in the root CHANGELOG.md
(Phase 36 did NOT pre-author a stub — verified live, unlike v1.5 which only
date-stamped). Mirror that content byte-identically into docs/source/changelog.md
(RTD copy). Author a fresh French `[1.6.0]` section in fr/CHANGELOG.md. Add a
`## v1.5 -> v1.6` section to UPGRADING.md (purely additive). Update the README
Roadmap checklist.

Purpose: v1.6.0 is an ADDITIVE minor — the new `ketu.declination` subpackage is
additive-only, `CHART_DTYPE` is byte-identical to v1.5 (no ratchet break), and the
frozen `core.aspects` table is byte-identical. The release must ship with accurate
version metadata across all three source-of-truth files and complete, dated
release notes documenting the declination-aspects detector surface
(find_declination_aspects / declination_aspect_masks / DeclinationAspectMasks /
DECLA_ASPECT_DTYPE / DECLA_COEF / MIN_DECL_ORB). This plan tags-ready a commit
whose version and changelogs are release-correct. Runs in parallel with 37-01
(feature docs) — NO file overlap (37-01 touches concepts.md/api.md/.po; this plan
touches changelog.md/conf.py and the metadata files).
Output: version 1.6.0 synced in all three files; a single dated [1.6.0] CHANGELOG
(EN root + RTD docs, content matched); a fresh dated French [1.6.0] section; a
complete UPGRADING v1.5 -> v1.6 section; a README Roadmap update. No ketu/ logic
changed.
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
@pyproject.toml
@ketu/__init__.py
@docs/source/conf.py
@CHANGELOG.md
@docs/source/changelog.md
@fr/CHANGELOG.md
@UPGRADING.md
@README.md
@ketu/declination/__init__.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Bump version to 1.6.0 in THREE files (incl. conf.py) and confirm the sync gate</name>
  <files>pyproject.toml, ketu/__init__.py, docs/source/conf.py</files>
  <action>
    Bump the version to 1.6.0 in THREE source-of-truth files. conf.py was NOT
    pre-bumped by Phase 36, so it is still at "1.5.0" and MUST be bumped here —
    skipping it leaves RTD showing 1.5.0 after the release.

    Change EXACTLY these strings (verified against live files 2026-06-04):
      a. `pyproject.toml` line 7: `version = "1.5.0"` -> `version = "1.6.0"`.
      b. `ketu/__init__.py` line 57: `__version__ = "1.5.0"` ->
         `__version__ = "1.6.0"`.
      c. `docs/source/conf.py` line 14: `release = "1.5.0"` ->
         `release = "1.6.0"`.
      d. `docs/source/conf.py` line 15: `version = "1.5.0"` ->
         `version = "1.6.0"`.
    All four edits MUST be made together — bumping a subset fails the sync gate or
    freezes RTD branding.

    Then re-install the editable package so importlib.metadata picks up the new
    version, and run the sync gate:
      `pip install -e . -q && pytest tests/test_version.py -v`
    Both version tests MUST pass. (test_version.py checks pyproject.toml +
    ketu/__init__.py vs importlib.metadata — it does NOT check conf.py, which is
    why the explicit conf.py grep below is the guard for that file.)
  </action>
  <verify>
    `grep -n 'version = "1.6.0"' pyproject.toml` matches at line 7;
    `grep -n '__version__ = "1.6.0"' ketu/__init__.py` matches at line 57;
    `grep -q 'release = "1.6.0"' docs/source/conf.py` matches;
    `grep -q 'version = "1.6.0"' docs/source/conf.py` matches;
    `! grep -q '1.5.0' docs/source/conf.py` (no stale 1.5.0 left in conf.py);
    `pytest tests/test_version.py -v` is GREEN.
  </verify>
  <done>
    pyproject.toml, ketu/__init__.py, and docs/source/conf.py (both release and
    version) all read "1.6.0"; ketu.__version__ ==
    importlib.metadata.version("ketu") == "1.6.0"; test_version.py passes; no
    "1.5.0" remains in conf.py.
  </done>
</task>

<task type="auto">
  <name>Task 2: Author the [1.6.0] changelog FROM SCRATCH (root + docs RTD copy) and the French section</name>
  <files>CHANGELOG.md, docs/source/changelog.md, fr/CHANGELOG.md</files>
  <action>
    Unlike v1.5 (which only date-stamped pre-authored stubs), Phase 36 did NOT
    pre-author a `[1.6.0]` section — verified live: the newest section in both
    CHANGELOG.md (line 10) and docs/source/changelog.md (line 8) is
    `## [1.5.0] - 2026-06-04`. So this plan AUTHORS the [1.6.0] content from
    scratch in all three changelogs.

    Determine the release date: TODAY's UTC date in `YYYY-MM-DD` form via
    `date -u +%F`. Use the SAME date in all three changelog headers.

    1. CHANGELOG.md — INSERT a new `## [1.6.0] - <date>` section as the FIRST
       version section, immediately ABOVE `## [1.5.0] - 2026-06-04` (line 10). Use
       the root file's heading idiom (`### Added`, `### Notes` — NO version suffix;
       see the [1.5.0] root section style). Content (authoritative API source:
       `ketu/declination/__init__.py` __all__ + the live dtype):

       ### Added
       - **`ketu.declination` subpackage — declination aspects (parallels &
         contra-parallels)**: a NEW additive subpackage detecting parallel (`P`)
         and contra-parallel (`CP`) aspects on the equatorial declination axis (δ),
         independent of ecliptic longitude. (Phase 36)
       - **`find_declination_aspects(body_decl)`**: scalar/single-chart detector.
         Takes the `(14,)` signed-δ `chart["body_decl"]` array; returns a
         `DECLA_ASPECT_DTYPE` structured array (upper-triangle pairs, sorted,
         deduplicated); `np.empty(0, …)` when none detected (never `None`).
       - **`declination_aspect_masks(body_decl)`**: vectorized batch path. Accepts
         `(S, 14)` or `(14,)` (promoted via `np.atleast_2d`); returns a
         `DeclinationAspectMasks` NamedTuple of `(S, 91)` masks + `(91,)`
         index/orb vectors. Pure broadcasting, no Python body loop.
       - **`DeclinationAspectMasks` NamedTuple** (6 fields: `parallel`, `contra`,
         `gap`, `idx_i`, `idx_j`, `orb_pairs`).
       - **`DECLA_ASPECT_DTYPE`** (5 fields: `body1`, `body2`, `kind` ∈ {"P","CP"},
         `gap`, `orb`).
       - **`DECLA_COEF = 1/12` and `MIN_DECL_ORB = 0.5°`**: the body-derived orb
         formula `max((orb_b1 + orb_b2)/2 × DECLA_COEF, MIN_DECL_ORB)` → Sun/Moon
         = 1.0°, zero-orb bodies (Rahu/Ketu/Lilith) floored to 0.5°.

       ### Notes
       - **`CHART_DTYPE` unchanged — additive subpackage**: `ketu.declination` is a
         purely additive companion to the v1.5 declination δ infrastructure. The
         `body_decl` field (shape `(14,)`) shipped in v1.5 is the sole input;
         `CHART_DTYPE` is byte-identical to v1.5 (no ratchet break). The new names
         are reachable via `ketu.declination.*` only — `ketu.__all__` is unchanged.
       - **Parallel ≠ longitude conjunction**: declination aspects are independent
         of ecliptic-longitude aspects. The frozen 14-row `core.aspects` table is
         byte-identical to v1.5.

       Leave `## [1.5.0] - 2026-06-04` and everything below untouched.

    2. docs/source/changelog.md — INSERT the SAME [1.6.0] content above
       `## [1.5.0] - 2026-06-04` (line 8), adapted to the docs file's heading idiom
       which suffixes the version (`### Added 1.6.0`, `### Notes 1.6.0` — see the
       existing `### Added 1.5.0` style in that file). The BULLET CONTENT must be
       byte-identical to the root CHANGELOG.md [1.6.0] bullets (success criterion:
       EN root and RTD docs carry the same content). Do NOT touch any other version
       header.

    3. fr/CHANGELOG.md — author a NEW French `## [1.6.0] - <date>` section INSERTED
       ABOVE the existing `## [1.5.0] - 2026-06-04` (line 13), after the header/
       note block. Match the file's existing style (`### Ajouts`, `### Notes` — see
       the [1.5.0] French section). Translate the Added + Notes bullets faithfully;
       keep identifiers (`find_declination_aspects`, `DECLA_ASPECT_DTYPE`,
       `body_decl`, `ketu.declination`, `DECLA_COEF`, `MIN_DECL_ORB`,
       `np.atleast_2d`) verbatim. Key terms: parallel → parallèle, contra-parallel
       → contre-parallèle, declination axis → axe de déclinaison, additive →
       additif, unchanged → inchangé. Leave the existing `## [1.5.0]` French
       section and below untouched.
  </action>
  <verify>
    `grep -c '^## \[1.6.0\] - 20' CHANGELOG.md` returns 1;
    `! grep -q '^## \[1.6.0\] - Unreleased' CHANGELOG.md`;
    `! grep -q '^## \[Unreleased\]' CHANGELOG.md`;
    `grep -q 'find_declination_aspects' CHANGELOG.md` and `grep -q 'ketu.declination' CHANGELOG.md` and `grep -q 'CHART_DTYPE' CHANGELOG.md` (content present);
    `grep -c '^## \[1.6.0\] - 20' docs/source/changelog.md` returns 1 and
    `grep -q 'find_declination_aspects' docs/source/changelog.md`;
    `grep -c '^## \[1.6.0\] - 20' fr/CHANGELOG.md` returns 1 and
    `grep -q 'contre-parallèle\|déclinaison' fr/CHANGELOG.md` matches and
    `grep -q 'find_declination_aspects' fr/CHANGELOG.md` matches;
    `grep -c '^## \[1.5.0\] - 2026-06-04' CHANGELOG.md` returns 1 (existing section intact).
  </verify>
  <done>
    CHANGELOG.md has a new dated `[1.6.0]` section authored from scratch (declination
    aspects subpackage + Notes), no Unreleased anywhere; docs/source/changelog.md
    has the byte-identical-content `[1.6.0]` section (docs heading idiom);
    fr/CHANGELOG.md has a matching dated French `[1.6.0]` section above `[1.5.0]`;
    the [1.5.0] sections are untouched.
  </done>
</task>

<task type="auto">
  <name>Task 3: Add UPGRADING v1.5 -> v1.6 section and update the README Roadmap checklist</name>
  <files>UPGRADING.md, README.md</files>
  <action>
    v1.6 is fully additive (no breaking changes), but a migration note documents
    the additive surface for downstream consumers (Kala) and MUST NOT be omitted.

    1. UPGRADING.md — add a `## v1.5 -> v1.6` section as the NEW FIRST section,
       inserted BEFORE the existing `## v1.4 -> v1.5` (currently at line 6),
       keeping newest-first ordering. Content:
         `## v1.5 -> v1.6`
         Intro: v1.6 is **purely additive** — no field is removed or reordered, no
         existing API changes behavior.
         `### New `ketu.declination` subpackage — additive, no migration needed`:
            - new subpackage detecting parallels (`P`) / contra-parallels (`CP`) on
              the declination axis; entry points `from ketu.declination import
              find_declination_aspects, declination_aspect_masks,
              DeclinationAspectMasks, DECLA_ASPECT_DTYPE, DECLA_COEF, MIN_DECL_ORB`.
            - These names are reachable via `ketu.declination.*` ONLY — `ketu.__all__`
              is unchanged.
         `### CHART_DTYPE is UNCHANGED — no ratchet break`:
            - the detector consumes the v1.5 `body_decl` field (shape `(14,)`);
              `CHART_DTYPE` is byte-identical to v1.5. Any code or ratchet test
              pinning the CHART_DTYPE sha256 fingerprint needs NO change for v1.6
              (contrast v1.4 → v1.5, which DID change the dtype). The frozen 14-row
              `core.aspects` table is byte-identical.
         `### Kala guidance`:
            - no migration required; the new detector is opt-in. Compose
              `is_out_of_bounds` (v1.5) with the aspect output if "both OOB"
              annotation is desired (interpretive, not a detection flag).
       Do NOT modify the existing `## v1.4 -> v1.5` content.

    2. README.md — update the `## Roadmap` checklist (line ~312). Add ONE entry
       IMMEDIATELY AFTER the existing
       `- [x] Dynamic harmonic CLI (`--harmonics h7`) + `H{h}-{k}` naming contract +`
       / `find_aspect_timing(dyn_coef=)` block (the two-line entry ending around
       line 331). Add:
         - [x] Declination aspects — parallels & contra-parallels on the δ axis
           (`ketu.declination`: `find_declination_aspects`,
           `declination_aspect_masks`)
       Do NOT add a `## What's New in v1.6.0` section (no prior-version equivalent
       exists — adding one would create an inconsistency). Do NOT modify any other
       README section.
  </action>
  <verify>
    `grep -q '^## v1.5 -> v1.6' UPGRADING.md`;
    `grep -q 'ketu.declination' UPGRADING.md`;
    `grep -q 'CHART_DTYPE is UNCHANGED\|byte-identical\|no ratchet' UPGRADING.md`;
    `grep -q 'find_declination_aspects' UPGRADING.md`;
    `grep -c '^## v1.4 -> v1.5' UPGRADING.md` returns 1 (existing section intact);
    `grep -q 'ketu.declination' README.md` and `grep -qi 'parallel\|contra-parallel\|declination aspect' README.md` both match under the Roadmap;
    `! grep -q "What.s New in v1.6.0" README.md` (no inconsistent section added).
  </verify>
  <done>
    UPGRADING.md `## v1.5 -> v1.6` is the new first section (new ketu.declination
    subpackage + CHART_DTYPE unchanged/no-ratchet + Kala guidance), with
    `## v1.4 -> v1.5` intact; README `## Roadmap` checklist has the v1.6 declination
    aspects entry after the dynamic harmonic CLI entry; no "What's New" section added.
  </done>
</task>

</tasks>

<verification>
- `pytest tests/test_version.py -v` GREEN; pyproject.toml + ketu/__init__.py + docs/source/conf.py (release AND version) all read "1.6.0"; no "1.5.0" remains in conf.py.
- CHANGELOG.md: exactly one `## [1.6.0] - <date>` section authored from scratch (declination aspects + Notes), no Unreleased anywhere; `## [1.5.0] - 2026-06-04` and below unchanged.
- docs/source/changelog.md: `## [1.6.0]` section with content matching the root CHANGELOG bullets (docs heading idiom).
- fr/CHANGELOG.md: dated `## [1.6.0]` French section above `[1.5.0]`, translating the Added + Notes bullets.
- UPGRADING.md: `## v1.5 -> v1.6` first section (additive: ketu.declination, CHART_DTYPE unchanged/no-ratchet, Kala guidance), `## v1.4 -> v1.5` intact.
- README.md: `## Roadmap` checklist has the v1.6 declination-aspects entry; no `## What's New in v1.6.0` section.
- Full suite still green: `pytest tests/ -q` (expect ~1654 passed, 2 skipped). mypy --strict already clean — no fix needed.
</verification>

<success_criteria>
Version bumped to 1.6.0 in ALL THREE source-of-truth files (pyproject.toml +
ketu/__init__.py + docs/source/conf.py — the conf.py bump prevents stale 1.5.0 RTD
branding); the root CHANGELOG and docs RTD changelog `[1.6.0]` sections are
authored from scratch with matching content (declination aspects subpackage +
additive Notes); fr/CHANGELOG has a fresh dated French `[1.6.0]` section; UPGRADING
documents the v1.5 -> v1.6 purely-additive migration (ketu.declination,
CHART_DTYPE unchanged); README Roadmap lists the v1.6 declination aspects. mypy
--strict already clean (no fix task needed). No `ketu/` calculation logic changed.
</success_criteria>

<output>
After completion, create
`.planning/phases/37-documentation-release-v1-6-0/37-02-SUMMARY.md`
</output>
</content>
</invoke>
