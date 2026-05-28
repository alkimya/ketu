---
phase: 20-release-preparation-v1-2-0
plan: 03
type: execute
wave: 2
depends_on: ["20-01", "20-02"]
files_modified:
  - pyproject.toml
  - ketu/__init__.py
  - CHANGELOG.md
  - fr/CHANGELOG.md
  - UPGRADING.md
  - README.md
  - .planning/REQUIREMENTS.md
  - .planning/STATE.md
autonomous: true

must_haves:
  truths:
    - "ketu.__version__ == importlib.metadata.version('ketu') == '1.2.0'"
    - "CHANGELOG.md has a dated [1.2.0] section covering SYN/COMP/RET/PARTS/CHART, three new house systems (whole_sign/equal/regiomontanus), doc gates, and workflow refresh, with NO BREAKING heading"
    - "fr/CHANGELOG.md exists, is generated/translated (header note says so, not hand-maintained), and ships via MANIFEST.in recursive-include"
    - "UPGRADING.md has a v1.1 -> v1.2 section that is additive-only (no breaking-change recipes)"
    - "README 'What's New' section reflects v1.2.0"
    - "REQUIREMENTS.md no longer shows PARTS-01..08 / OPS-* as falsely Pending where complete"
  artifacts:
    - path: "fr/CHANGELOG.md"
      provides: "Generated French changelog synthesized from English"
      contains: "[1.2.0]"
    - path: "CHANGELOG.md"
      provides: "Dated [1.2.0] release entry, additive-only"
      contains: "## [1.2.0]"
    - path: "UPGRADING.md"
      provides: "v1.1 -> v1.2 additive migration section"
      contains: "v1.1 -> v1.2"
  key_links:
    - from: "pyproject.toml version"
      to: "ketu/__init__.py __version__"
      via: "must be identical strings"
      pattern: "1\\.2\\.0"
    - from: "CHANGELOG.md:3 blockquote"
      to: "fr/CHANGELOG.md"
      via: "the French-version reference is now accurate (file exists)"
      pattern: "fr/CHANGELOG\\.md"
---

<objective>
Bump the version to 1.2.0 in both source-of-truth locations, write the
dated `[1.2.0]` CHANGELOG entry (additive-only, including the Arabic
Parts and three-new-house-systems entries that were never logged), CREATE
the generated `fr/CHANGELOG.md` (OPS-04 LOCKED DECISION), add the
additive `v1.1 -> v1.2` UPGRADING section, refresh the README "What's New"
block, and clean the REQUIREMENTS.md/STATE.md status drift. All
doc/config — zero `ketu/` logic change beyond the version string.

Purpose: a release is its release notes plus a correct version. This plan
produces every human-facing artifact the v1.2.0 tag will reference.
Depends on 20-01 (workflow refresh, so the CHANGELOG can claim it
truthfully) and 20-02 (gate flip, so the CHANGELOG can say "numpydoc now
blocking").
Output: version-synced repo with complete, accurate, bilingual release
documentation.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/20-release-preparation-v1-2-0/20-RESEARCH.md
@.planning/REQUIREMENTS.md
@CHANGELOG.md
@UPGRADING.md
@README.md
@MANIFEST.in
@pyproject.toml
@ketu/__init__.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Version bump to 1.2.0 + promote [Unreleased] to dated [1.2.0] (additive-only, filling Phase 15/19 gaps)</name>
  <files>pyproject.toml, ketu/__init__.py, CHANGELOG.md</files>
  <action>
    1. `pyproject.toml:7` — `version = "1.1.0"` -> `version = "1.2.0"`.
    2. `ketu/__init__.py:57` — `__version__ = "1.1.0"` -> `__version__ = "1.2.0"`.
       (Version is STATIC in pyproject.toml; importlib.metadata reads it
       after a reinstall. The version-sync test compares the two literals.)
    3. `CHANGELOG.md`:
       - Rename the `## [Unreleased]` header to
         `## [1.2.0] - 2026-05-28` (use today's date; if the release day
         differs, plan 20-04 will re-stamp it — but write a real date, NEVER
         "UNRELEASED").
       - Keep the existing `### Added` / `### Changed` content (SYN/COMP/RET
         + the HOUSES_DTYPE U10->U16 change) intact under the new header.
       - ADD the MISSING entries the research flagged:
         * Phase 19 Arabic Parts (`### Added`): `ketu.parts` subpackage —
           extensible `PARTS` registry + `PartSpec` (analogue of houses
           `SYSTEMS`); `calculate_part(part_name, chart)` sect-aware
           dispatch via `is_day_chart`; `calculate_all_parts(chart,
           parts=None)` dict output; three built-in parts — Fortune
           (sect-aware), Spirit (sect-aware mirror), Marriage
           (sect-invariant, `ASC + Descendant - Venus`); `ketu --list-parts`
           CLI flag; `make parts-coverage` gate (100% on ketu/parts/);
           `parts_coverage_gate` pytest marker. (PARTS-01..08)
         * Phase 15 three new house systems (`### Added`): Whole Sign
           (`"whole_sign"`), Equal (`"equal"`), Regiomontanus
           (`"regiomontanus"`) registered in `ketu.houses.SYSTEMS` via the
           `@register` decorator; available through `calculate_houses(...,
           system=...)`, the `ketu houses --system` CLI, and
           `ketu --list-house-systems`. (HOU2-01..05) — VERIFIED present in
           ketu/houses/ ({whole_sign,equal,regiomontanus}.py all
           @register).
         * (If not already covered) CHART abstraction (`ketu.charts`,
           CHART_DTYPE) if it has a public surface worth noting — check
           ketu/charts/ and add a one-line bullet only if user-facing.
       - Add an `### Infrastructure` (or fold into `### Changed`) note for
         the workflow refresh (Node 24: checkout@v5, setup-python@v6,
         upload-artifact@v5) and the numpydoc gate now blocking + interrogate
         >=95% gate. (OPS-01, OPS-02, OPS-03)
       - DO NOT add a BREAKING / Removed (BREAKING) / Changed (BREAKING)
         heading anywhere in the [1.2.0] section. This is a non-breaking
         minor (phase success criterion #4). The HOUSES_DTYPE width change
         is explicitly Non-breaking — keep that wording.
       - Leave the `> Consultez la version française dans fr/CHANGELOG.md.`
         blockquote at line 3 in place (it becomes accurate once Task 2
         creates the file).
  </action>
  <verify>
    `grep -n 'version = "1.2.0"' pyproject.toml` and
    `grep -n '__version__ = "1.2.0"' ketu/__init__.py` both match.
    `pip install -e . -q && pytest tests/test_version.py -v` passes
    (test_version_matches_metadata + test_version_format).
    `grep -n "## \[1.2.0\] - 2026" CHANGELOG.md` matches and
    `grep -n "## \[Unreleased\]" CHANGELOG.md` returns nothing.
    `grep -niE "BREAKING" CHANGELOG.md | sed -n '1,3p'` — confirm no
    BREAKING heading falls inside the [1.2.0] block (the v1.0/v1.1 BREAKING
    headings below are fine).
    `grep -n "ketu.parts\|whole_sign\|regiomontanus\|equal" CHANGELOG.md`
    shows the newly added Phase 15/19 bullets.
  </verify>
  <done>
    Both version literals are "1.2.0"; test_version passes; CHANGELOG has a
    dated, additive-only [1.2.0] entry that includes Arabic Parts and the
    three new house systems and the workflow/gate refresh, with no BREAKING
    heading.
  </done>
</task>

<task type="auto">
  <name>Task 2: CREATE fr/CHANGELOG.md (generated) + UPGRADING v1.1->v1.2 + README What's New</name>
  <files>fr/CHANGELOG.md, UPGRADING.md, README.md</files>
  <action>
    OPS-04 LOCKED DECISION: CREATE fr/CHANGELOG.md (do NOT remove the
    reference). The `fr/` directory does not yet exist — create it. The
    file is a GENERATED/TRANSLATED artifact synthesized from the English
    CHANGELOG, NEVER hand-maintained in parallel.

    1. Create `fr/CHANGELOG.md`:
       - Open with a header note (in French) stating the file is a
         synthesized translation of `../CHANGELOG.md`, not maintained in
         parallel, updated at each release alongside the English version,
         and that the English `CHANGELOG.md` is authoritative ("fait foi").
       - Add a French `## [1.2.0] - 2026-05-28` section translating the key
         bullets of the English [1.2.0] entry: `ketu.synastry`,
         `ketu.composite`, `ketu.returns`, `ketu.parts` (Parts Arabes —
         Fortune/Esprit sect-aware, Mariage sect-invariant, CLI
         `--list-parts`), les trois systèmes de maisons supplémentaires
         (Maisons Entières/Whole Sign, Maisons Égales, Régiomontanus),
         gates de doc CI (interrogate >=95% + numpydoc bloquant), refresh
         des workflows (Node.js 24). NO BREAKING / "Cassant" heading.
       - For [1.1.0] and [1.0.0], do NOT re-translate the full body — add a
         short stub line per version pointing to the English CHANGELOG
         anchor (e.g. `Voir [CHANGELOG.md](../CHANGELOG.md#110---2026-05-08)`).
       - Match the bullets you actually wrote in Task 1 — do not invent
         features. Keep the persona's French register (Sophie Chen).
       MANIFEST.in already has `recursive-include fr *.md`, so this file
       ships in the sdist automatically — do NOT edit MANIFEST.in.

    2. `UPGRADING.md` — insert a NEW `## v1.1 -> v1.2` section ABOVE the
       existing `## v1.0 -> v1.1` (file is newest-first). It MUST be
       additive-only:
       - One-line intro: v1.2 is a fully backward-compatible feature
         release; all v1.1 code continues to work unchanged; no breaking
         changes.
       - "New APIs" subsection with import-path recipes:
         * `from ketu.synastry import calculate_synastry`
         * `from ketu.composite import calculate_composite, circular_midpoint`
         * `from ketu.returns import solar_return, lunar_return` — include
           the API ASYMMETRY note: `solar_return(..., target_year=<int>)`
           takes an integer year; `lunar_return(..., target_jd=<float>)`
           takes a Julian Date. Note relocation via `return_lat/return_lon`.
         * `from ketu.parts import calculate_part, calculate_all_parts` —
           sect-aware dispatch (Fortune/Spirit), fixed Marriage; CLI
           `ketu --list-parts`.
         * Three new house systems via `calculate_houses(jd, lat, lon,
           system="whole_sign"|"equal"|"regiomontanus")`; CLI
           `ketu houses --system whole_sign`. (Note: the v1.0->v1.1 section
           said `equal` and `whole_sign` were "not yet registered" — they
           are now; this section supersedes that.)
       - Closing note: nothing to change for existing code; this section is
         informational/opt-in only.
       Do NOT add any "Action required" / recompute-your-cache style
       recipe — there are no breaking numerical changes in v1.2.

    3. `README.md` — replace the `## What's New in v1.1.0` section
       (~lines 13-41) with `## What's New in v1.2.0`:
       - One-line framing: non-breaking feature release; all v1.1 code
         works unchanged.
       - Bullets: synastry, composite, returns, Arabic parts (Fortune/
         Spirit/Marriage + `ketu --list-parts`), three new house systems
         (Whole Sign / Equal / Regiomontanus), CI doc gates (interrogate +
         numpydoc now blocking), Node-24 workflow refresh.
       - Keep the trailing "For the full list of changes see
         [CHANGELOG.md]" line.
  </action>
  <verify>
    `test -f fr/CHANGELOG.md && grep -n "\[1.2.0\]" fr/CHANGELOG.md` —
    file exists with the 1.2.0 section.
    `grep -niE "traduction|synthétis|fait foi" fr/CHANGELOG.md` — header
    note present.
    `grep -n "v1.1 -> v1.2\|v1.1 → v1.2" UPGRADING.md` — section present;
    `grep -n "target_year\|target_jd" UPGRADING.md` — asymmetry note present.
    `grep -n "What's New in v1.2.0" README.md` — present;
    `grep -n "What's New in v1.1.0" README.md` — returns nothing.
    `python -m build --sdist -q 2>/dev/null && tar -tzf dist/ketu-1.2.0.tar.gz | grep "fr/CHANGELOG.md"` — confirms fr/ ships in the sdist (then `rm -rf dist build *.egg-info` to clean up).
  </verify>
  <done>
    fr/CHANGELOG.md created as a generated translation (with the
    not-hand-maintained header) and ships in the sdist; UPGRADING.md has an
    additive-only v1.1->v1.2 section; README "What's New" reflects v1.2.0.
  </done>
</task>

<task type="auto">
  <name>Task 3: Reconcile REQUIREMENTS.md / STATE.md status drift</name>
  <files>.planning/REQUIREMENTS.md, .planning/STATE.md</files>
  <action>
    Research found pre-existing status drift: REQUIREMENTS.md status table
    shows PARTS-01..08 as `Pending` though Phase 19 is complete and
    verified, and OPS-03/04/05 will be satisfied by this phase.
    - In `.planning/REQUIREMENTS.md` status table (~lines 149-161): flip
      PARTS-01..08 from `Pending` to `Done` (Phase 19 is closed per
      MEMORY/ROADMAP). Leave OPS-03/04/05 as Pending for now (they flip on
      release in 20-04) UNLESS the verifier convention is to mark them Done
      when the implementing plan lands — match whatever convention the rest
      of the table uses (check how other completed-phase requirements are
      marked). Also un-check the `- [ ] **PARTS-0X**` checklist items at
      lines ~62-69 to `- [x]` if that mirrors the table.
    - In `.planning/STATE.md`: update the "Current Position" / focus prose
      so it reflects Phase 20 as the active phase (not Phase 19 complete),
      and update the progress counters if STATE tracks per-phase status.
      Keep edits minimal and factual; do not invent state.
    Scope guard: do NOT touch ROADMAP.md here — the planner orchestrator
    owns ROADMAP plan-list updates. This task is REQUIREMENTS.md + STATE.md
    drift cleanup only.
  </action>
  <verify>
    `grep -nE "PARTS-0[1-8]" .planning/REQUIREMENTS.md | grep -i pending` —
    returns nothing (no PARTS row still says Pending).
    `grep -ni "phase 20" .planning/STATE.md` — STATE references Phase 20 as
    current/active.
  </verify>
  <done>
    REQUIREMENTS.md no longer falsely marks completed PARTS requirements as
    Pending; STATE.md reflects Phase 20 as the active phase.
  </done>
</task>

</tasks>

<verification>
- `python -c "import ketu; print(ketu.__version__)"` prints `1.2.0`
  (after `pip install -e .`), and `pytest tests/test_version.py -v` passes.
- CHANGELOG [1.2.0] dated, additive-only, includes Arabic Parts + 3 house
  systems + workflow/gate refresh; no BREAKING heading in that block.
- fr/CHANGELOG.md exists, generated-header present, ships in sdist.
- UPGRADING.md v1.1->v1.2 is additive-only with the solar/lunar asymmetry
  note.
- README "What's New in v1.2.0" present; v1.1.0 block gone.
- No PARTS requirement still marked Pending in REQUIREMENTS.md.
- Full suite still green: `pytest tests/ -q`.
</verification>

<success_criteria>
- Version 1.2.0 synced across pyproject.toml + __init__.py; version test
  passes (phase success criterion #3).
- Complete additive [1.2.0] CHANGELOG + bilingual fr/CHANGELOG.md (OPS-04
  locked decision) + additive UPGRADING + README (criteria #2 and #4).
- Status drift reconciled in planning docs.
</success_criteria>

<output>
After completion, create
`.planning/phases/20-release-preparation-v1-2-0/20-03-SUMMARY.md`
</output>
