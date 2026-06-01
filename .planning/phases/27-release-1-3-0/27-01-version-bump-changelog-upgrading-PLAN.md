---
phase: 27-release-1-3-0
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - pyproject.toml
  - ketu/__init__.py
  - CHANGELOG.md
  - UPGRADING.md
  - fr/CHANGELOG.md
autonomous: true

must_haves:
  truths:
    - "ketu.__version__ == importlib.metadata.version('ketu') == '1.3.0' (pytest tests/test_version.py green)"
    - "CHANGELOG.md has a single dated '## [1.3.0] - <date>' section that contains the aspect-engine items, the cycle-direction BREAKING + datetime64 fix, AND the Chiron 14th-body Added + BREAKING-contract notes"
    - "CHANGELOG.md no longer contains a '## [Unreleased]' section nor '## [1.3.0] - Unreleased'"
    - "UPGRADING.md '## v1.2 -> v1.3' documents the Chiron 13->14 positional-array contract change (CHART_DTYPE shape table) in addition to the existing aspect-engine section"
    - "fr/CHANGELOG.md has a '## [1.3.0] - <date>' section translating the same bullets"
  artifacts:
    - path: "pyproject.toml"
      provides: "Build-system version source of truth"
      contains: "version = \"1.3.0\""
    - path: "ketu/__init__.py"
      provides: "Runtime version source of truth"
      contains: "__version__ = \"1.3.0\""
    - path: "CHANGELOG.md"
      provides: "Dated [1.3.0] entry with all v1.3 items incl. Chiron"
      contains: "## [1.3.0] -"
    - path: "UPGRADING.md"
      provides: "v1.2 -> v1.3 migration incl. Chiron positional contract"
      contains: "Chiron"
    - path: "fr/CHANGELOG.md"
      provides: "French [1.3.0] changelog section"
      contains: "## [1.3.0] -"
  key_links:
    - from: "pyproject.toml version"
      to: "ketu/__init__.py __version__"
      via: "test_version_matches_metadata (importlib.metadata == __version__)"
      pattern: "1\\.3\\.0"
    - from: "CHANGELOG.md [1.3.0] Chiron BREAKING note"
      to: "UPGRADING.md v1.2 -> v1.3 Chiron section"
      via: "cross-reference for the 13->14 migration recipe"
      pattern: "CHART_DTYPE|13.*14|14.*body"
---

<objective>
Bump Ketu to 1.3.0 and finalize all release documentation: merge the two
unversioned CHANGELOG sections into one dated `[1.3.0]`, ADD the missing
Chiron 14th-body entries, ADD the missing Chiron positional-contract section
to UPGRADING, add the French `[1.3.0]` changelog section, and verify the
already-written README "What's New in v1.3.0" is complete.

Purpose: REL-10. v1.3.0 must ship with accurate, complete release notes that
document BOTH breaking changes (the Chiron 13->14 body-axis expansion for
Kala/downstream, and the aspect-engine default/coefficient/preset surface) so
the release ceremony in 27-02 tags a commit whose docs are publication-ready.
Output: version bumped in the two source-of-truth files, a single dated
`[1.3.0]` CHANGELOG (EN + FR), and a complete UPGRADING `v1.2 -> v1.3` section.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/27-release-1-3-0/27-RESEARCH.md
@pyproject.toml
@ketu/__init__.py
@CHANGELOG.md
@UPGRADING.md
@fr/CHANGELOG.md
@README.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Bump version to 1.3.0 in the two source-of-truth files and verify the sync gate</name>
  <files>pyproject.toml, ketu/__init__.py</files>
  <action>
    Change EXACTLY two strings. Do NOT touch docs/source/conf.py — it is
    already at "1.3.0" (pre-bumped in Phase 25); editing it creates a
    spurious no-op diff (RESEARCH Pitfall 8).

    1. `pyproject.toml` line 7: `version = "1.2.0"` -> `version = "1.3.0"`.
    2. `ketu/__init__.py` line 57: `__version__ = "1.2.0"` -> `__version__ = "1.3.0"`.

    Both MUST be bumped in the same change — bumping only one fails the sync
    gate (RESEARCH Pitfall 6).

    Then re-install the editable package so importlib.metadata picks up the
    new version, and run the gate:
      `pip install -e . -q && pytest tests/test_version.py -v`

    Both `test_version_matches_metadata` and `test_version_format` MUST pass.
  </action>
  <verify>
    `grep -n 'version = "1.3.0"' pyproject.toml` and
    `grep -n '__version__ = "1.3.0"' ketu/__init__.py` both match;
    `pytest tests/test_version.py -v` is GREEN (2 passed). Confirm
    `docs/source/conf.py` was NOT modified (`git diff --stat docs/source/conf.py`
    shows nothing).
  </verify>
  <done>
    pyproject.toml and ketu/__init__.py both read "1.3.0";
    ketu.__version__ == importlib.metadata.version("ketu") == "1.3.0";
    test_version.py passes; conf.py untouched.
  </done>
</task>

<task type="auto">
  <name>Task 2: Merge CHANGELOG into one dated [1.3.0] and ADD the Chiron 14th-body entries</name>
  <files>CHANGELOG.md, fr/CHANGELOG.md</files>
  <action>
    The English CHANGELOG currently has TWO unversioned sections that must
    become ONE dated section (RESEARCH "CHANGELOG.md Current State", Pitfalls
    1, 2, 7). Read the current file first to preserve exact existing wording —
    MERGE/ADD, do not rewrite the aspect content (Phase 26 already wrote it).

    Determine the release date: use today's UTC date in `YYYY-MM-DD` form
    (it is 2026-06-01 unless this plan runs on a later day — use the actual
    current date). Use the SAME date in both EN and FR.

    In CHANGELOG.md:
    1. RENAME the header `## [1.3.0] - Unreleased` to `## [1.3.0] - <date>`.
    2. MOVE the two items currently under `## [Unreleased]` (lines ~10-33)
       INTO the `[1.3.0]` section:
         - the `### Changed` BREAKING `CYCLE_DTYPE.angular_separation`
           direction-fix bullet (body1 -> body2, Kala adjusts `360 - old`),
         - the `### Fixed` `generate_cycle_series` datetime64-cache bullet.
       Place the angular_separation BREAKING bullet under the existing
       `[1.3.0]` `### Changed` heading (with the aspect-default BREAKING
       bullet); place the datetime64 bullet under a `### Fixed` heading.
    3. DELETE the now-empty `## [Unreleased]` section header entirely.
    4. ADD under `[1.3.0]` `### Added` a Chiron bullet (currently MISSING —
       RESEARCH Pitfall 2). Use the text from RESEARCH "What is MISSING from
       [1.3.0]" — Chiron as the 14th body (body_id=13), embedded Chebyshev
       evaluator (pure NumPy, zero pyswisseph at runtime),
       `calc_planet_position(jd, 13)` / `calc_planet_position_batch(jds, 13)`
       from `ketu/data/chiron_coeffs.npz` (289.7 KB, seg=32d/deg=10), max
       |Δλ| = 0.005695° over 1950-2050, available through all standard
       calculation paths; CHART_DTYPE body axis expanded 13 -> 14 bodies.
    5. ADD under `[1.3.0]` `### Changed` a BREAKING contract note for Kala
       (RESEARCH "Under ### Changed — BREAKING contract note"): CHART_DTYPE
       body arrays (13,) -> (14,) and aspects (13,13) -> (14,14); index 13 is
       Chiron; code that hardcoded 13 bodies or fixed numeric index > 12 must
       update; cycles default pairs + synastry axis (15 -> 16 incl. ASC/MC)
       updated; reference UPGRADING.md "v1.2 -> v1.3".

    Result: a SINGLE `## [1.3.0] - <date>` section containing — Added:
    aspects_for_harmonics + harmonic/symbol columns + Chiron; Changed:
    aspect-default BREAKING + angular_separation BREAKING + Chiron-axis
    BREAKING; Fixed: datetime64 cache. `## [1.2.0] - 2026-05-28` and below
    are untouched.

    In fr/CHANGELOG.md (RESEARCH "fr/CHANGELOG.md Required Delta"):
    Add a `## [1.3.0] - <date>` section ABOVE the existing `## [1.2.0]`,
    matching the existing French style (sections `### Ajouts`, `### Modifié`,
    `### Corrigé`). It is a synthesized translation (the EN file is
    authoritative — per the file's own header note), NOT double-maintained.
    Cover: Chiron 14e corps (`calc_planet_position(jd, 13)`, .npz Chebyshev
    embarqué, pur NumPy); BREAKING CHART_DTYPE 13->14 corps (note Kala);
    `aspects_for_harmonics(harmonics)` masque numpy.bool_ figé longueur 14;
    BREAKING défaut Python API CLASSICAL(5) -> TRADITIONAL(7); correction
    cycle direction `angular_separation` body1->body2 + `datetime64` cache;
    renvoi vers `UPGRADING.md -> v1.2 -> v1.3`.
  </action>
  <verify>
    `grep -c '^## \[1.3.0\] - 20' CHANGELOG.md` returns 1 (dated, not
    Unreleased); `grep -c '^## \[Unreleased\]' CHANGELOG.md` returns 0;
    `grep -c '^## \[1.3.0\] - Unreleased' CHANGELOG.md` returns 0;
    `grep -i 'Chiron' CHANGELOG.md` matches both the Added bullet and the
    BREAKING contract note; `grep 'angular_separation' CHANGELOG.md` and
    `grep 'datetime64' CHANGELOG.md` both match under [1.3.0];
    `grep -c '^## \[1.3.0\] - 20' fr/CHANGELOG.md` returns 1 and
    `grep -i 'Chiron' fr/CHANGELOG.md` matches.
  </verify>
  <done>
    CHANGELOG.md has exactly one dated `[1.3.0]` section carrying all five
    item-groups (aspects + Chiron + angular_separation + datetime64), no
    `[Unreleased]` or `[1.3.0] - Unreleased` headers remain, and the
    `[1.2.0]` section is unchanged; fr/CHANGELOG.md has a matching dated
    `[1.3.0]` section translating the same bullets.
  </done>
</task>

<task type="auto">
  <name>Task 3: ADD the Chiron section to UPGRADING and verify README is complete</name>
  <files>UPGRADING.md, README.md</files>
  <action>
    The `## v1.2 -> v1.3` section in UPGRADING.md currently documents ONLY the
    aspect-engine change (lines ~1-105). The Chiron 13->14 positional-contract
    section is MISSING (RESEARCH Pitfall 3) — ADD it. Do NOT rewrite the
    existing aspect-engine content (Phase 26 wrote it).

    1. UPGRADING.md — add a Chiron sub-section inside `## v1.2 -> v1.3`,
       placed BEFORE the existing "### Aspect engine changes (1.3.0)"
       sub-section (Chiron first is more prominent). Use the markdown from
       RESEARCH "UPGRADING.md Required Delta": a `### Chiron added as
       body_id=13 (14th body)` heading covering —
         - the CHART_DTYPE shape-expansion table
           (body_lons (13,)->(14,), body_speeds (13,)->(14,),
            aspects (13,13)->(14,14)),
         - Kala / downstream guidance: hardcoded body count 13 or fixed
           numeric index > 12 must update; cached v1.2 CHART_DTYPE arrays are
           incompatible — recompute with v1.3,
         - the new pure-NumPy import example
           (`from ketu.ephemeris.planets import calc_planet_position`;
            `calc_planet_position(2451545.0, 13)` -> finite longitude;
            no pyswisseph required at runtime),
         - Kala synastry body axis 15 -> 16 (Sun..Chiron + ASC + MC).

    2. README.md — READ the full `## What's New in v1.3.0` section (it was
       pre-written, likely Phase 25). It currently covers Chiron, the
       data-driven aspect engine, the new breaking default aspect set, and
       full French docs. VERIFY it is complete and accurate against the
       shipped surface. If it is already complete (it appears to be), make NO
       change to README.md and note "README verified complete, no change" in
       the summary. Only amend if a genuine inaccuracy or omission is found.
  </action>
  <verify>
    `grep -i 'Chiron' UPGRADING.md` matches inside the `## v1.2 -> v1.3`
    block; `grep -E 'body_lons|CHART_DTYPE|\(13,\)|\(14,\)' UPGRADING.md`
    matches the shape table; `grep 'calc_planet_position' UPGRADING.md`
    matches the import example. README `## What's New in v1.3.0` confirmed to
    cover Chiron + aspect engine + breaking default + French docs (either
    unchanged-because-complete or amended).
  </verify>
  <done>
    UPGRADING.md `## v1.2 -> v1.3` now has a Chiron positional-contract
    sub-section with the 13->14 shape table, recompute-caches guidance, the
    pure-NumPy import example, and the synastry 15->16 note; README
    `## What's New in v1.3.0` is confirmed complete and accurate.
  </done>
</task>

</tasks>

<verification>
- `pytest tests/test_version.py -v` GREEN; pyproject.toml + ketu/__init__.py both "1.3.0"; conf.py untouched.
- CHANGELOG.md: exactly one `## [1.3.0] - <date>` section; no `[Unreleased]` and no `[1.3.0] - Unreleased`; contains aspect items + Chiron Added bullet + Chiron BREAKING note + angular_separation BREAKING + datetime64 Fixed.
- fr/CHANGELOG.md: dated `## [1.3.0]` section translating the same bullets.
- UPGRADING.md `## v1.2 -> v1.3`: Chiron shape-table section present alongside the existing aspect-engine section.
- README `## What's New in v1.3.0`: verified complete (covers Chiron + aspects + breaking default + French docs).
- Run the full suite once to confirm no doc/version change broke anything: `pytest tests/ -q` all pass.
</verification>

<success_criteria>
REL-10 satisfied: version bumped to 1.3.0 (both source-of-truth files,
sync gate green); CHANGELOG has a single dated `[1.3.0]` entry listing the
additive features plus BOTH breaking notes (Chiron 13->14 positional contract
for Kala AND the aspect-engine default/coefficient/preset changes);
UPGRADING.md documents the 13->14 positional-array change and the aspect
changes; fr/CHANGELOG has a matching `[1.3.0]` section. No `ketu/` source
logic changed — only the two version strings.
</success_criteria>

<output>
After completion, create
`.planning/phases/27-release-1-3-0/27-01-SUMMARY.md`
</output>
