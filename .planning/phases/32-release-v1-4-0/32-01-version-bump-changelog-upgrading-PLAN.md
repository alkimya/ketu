---
phase: 32-release-v1-4-0
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - ketu/synastry/api.py
  - pyproject.toml
  - ketu/__init__.py
  - CHANGELOG.md
  - fr/CHANGELOG.md
  - docs/source/changelog.md
  - UPGRADING.md
  - README.md
autonomous: true

must_haves:
  truths:
    - "python -m mypy --strict ketu/ reports ZERO errors (the pre-existing ketu/synastry/api.py:392 no-any-return is fixed)"
    - "ketu.__version__ == importlib.metadata.version('ketu') == '1.4.0' (pytest tests/test_version.py green)"
    - "CHANGELOG.md has a single dated '## [1.4.0] - <date>' section authored fresh above '## [1.3.0] - 2026-06-01', with Added (generate_harmonic_aspects + Chiron 1900-2100 range) and Changed (Chiron orb 0->4, Chiron out-of-range clamp, docs recentring)"
    - "CHANGELOG.md contains no '## [Unreleased]' section and no '2026-06-XX' placeholder in the [1.4.0] header"
    - "fr/CHANGELOG.md has a matching '## [1.4.0] - <date>' section above '## [1.3.0] - 2026-06-01' translating the same bullets"
    - "docs/source/changelog.md '## [1.4.0] - 2026-06-XX' placeholder is replaced with the real release date; the '## [1.3.0] - 2026-06-XX' placeholder is replaced with 2026-06-01"
    - "UPGRADING.md has a '## v1.3 -> v1.4' section (new first section) covering the Chiron orb 0->4 behavioural break, Chiron out-of-range clamp, range expansion, and the additive dynamic generator"
    - "README.md has a '## What's New in v1.4.0' section above the existing '## What's New in v1.3.0'"
    - "docs/source/conf.py is NOT modified (already at 1.4.0 from Phase 31)"
  artifacts:
    - path: "ketu/synastry/api.py"
      provides: "calculate_synastry with a typed (non-Any) filtered return"
      contains: "cast(np.ndarray"
    - path: "pyproject.toml"
      provides: "Build-system version source of truth"
      contains: "version = \"1.4.0\""
    - path: "ketu/__init__.py"
      provides: "Runtime version source of truth"
      contains: "__version__ = \"1.4.0\""
    - path: "CHANGELOG.md"
      provides: "Dated [1.4.0] entry with all v1.4 items"
      contains: "## [1.4.0] -"
    - path: "fr/CHANGELOG.md"
      provides: "French [1.4.0] changelog section"
      contains: "## [1.4.0] -"
    - path: "docs/source/changelog.md"
      provides: "RTD changelog with date-stamped [1.4.0] (and [1.3.0])"
      contains: "## [1.4.0] -"
    - path: "UPGRADING.md"
      provides: "v1.3 -> v1.4 migration (Chiron orb break + clamp + range + additive generator)"
      contains: "## v1.3 -> v1.4"
    - path: "README.md"
      provides: "What's New in v1.4.0 section"
      contains: "## What's New in v1.4.0"
  key_links:
    - from: "pyproject.toml version"
      to: "ketu/__init__.py __version__"
      via: "test_version_matches_metadata (importlib.metadata == __version__)"
      pattern: "1\\.4\\.0"
    - from: "CHANGELOG.md [1.4.0] Chiron orb BREAKING note"
      to: "UPGRADING.md v1.3 -> v1.4 Chiron orb section"
      via: "cross-reference for the 0->4 orb migration recipe"
      pattern: "orb.*0.*4|0.*4.*orb"
    - from: "ketu/synastry/api.py:392 filtered return"
      to: "mypy --strict gate"
      via: "cast(np.ndarray, ...) removes the no-any-return error"
      pattern: "cast\\(np\\.ndarray"
---

<objective>
Make the v1.4.0 release candidate publication-ready: fix the one
pre-existing `mypy --strict` error that blocks the release gate, bump the
version to 1.4.0 in the two source-of-truth files, author the root
`CHANGELOG.md` `[1.4.0]` section FRESH (there is no `[Unreleased]` to merge),
sync a French `[1.4.0]` section in `fr/CHANGELOG.md`, date-stamp the
`docs/source/changelog.md` `[1.4.0]` (and the leftover `[1.3.0]`) placeholder,
add a `## v1.3 -> v1.4` section to `UPGRADING.md`, and add a
`## What's New in v1.4.0` section to `README.md`.

Purpose: REL-12. v1.4.0 must ship with accurate, complete release notes that
document the two behavioural changes (Chiron orb 0°→4° — Chiron now forms
scored aspects; Chiron out-of-range now silently clamps instead of raising
`ValueError`) and the additive dynamic harmonic generator. The mypy fix is a
hard pre-flight gate (32-02 STOPS on it) and was introduced by Phase 28 — it
MUST be clean before tagging. This plan tags a commit whose docs and types are
release-ready.
Output: mypy --strict clean; version bumped in the two source-of-truth files
(sync gate green); a single dated `[1.4.0]` CHANGELOG (EN + FR); date-stamped
RTD changelog; a complete UPGRADING `v1.3 -> v1.4` section; a README What's New
section. No `ketu/` calculation logic changed beyond the typed-return fix.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/32-release-v1-4-0/32-RESEARCH.md
@ketu/synastry/api.py
@pyproject.toml
@ketu/__init__.py
@CHANGELOG.md
@fr/CHANGELOG.md
@docs/source/changelog.md
@UPGRADING.md
@README.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Fix the mypy --strict no-any-return error and bump version to 1.4.0</name>
  <files>ketu/synastry/api.py, pyproject.toml, ketu/__init__.py</files>
  <action>
    This task does the two SOURCE changes that gate the release: the mypy fix
    (RESEARCH Pitfall 4) and the version bump (RESEARCH "Version Bump
    Locations"). Both go in this plan's single atomic commit.

    1. MYPY FIX — `ketu/synastry/api.py` line 392.
       The pre-existing error (introduced by Phase 28's dynamic_specs work, NOT
       present at v1.3) is:
         `ketu/synastry/api.py:392: error: Returning Any from function declared
          to return "ndarray[...]"  [no-any-return]`
       on the line `return out[out["aspect_type"] != -1]` inside the
       `mode == "filtered"` branch of `calculate_synastry` (declared
       `-> np.ndarray`).
       Fix by wrapping the boolean-mask index in an explicit cast:
         a. Add `cast` to the typing import. Current line 51 reads
            `from typing import Literal, Tuple` — change it to
            `from typing import Literal, Tuple, cast`.
         b. Change line 392 from
              `return out[out["aspect_type"] != -1]`
            to
              `return cast(np.ndarray, out[out["aspect_type"] != -1])`
       Do NOT change any runtime behaviour — `cast` is a typing-only no-op.
       Then run `python -m mypy --strict ketu/` and confirm ZERO errors
       ("Success: no issues found in 69 source files" or equivalent — the
       previous run reported exactly 1 error in 1 file).

    2. VERSION BUMP — change EXACTLY two strings. Do NOT touch
       `docs/source/conf.py` — it is already at "1.4.0" (pre-bumped in Phase
       31); editing it creates a spurious no-op diff (RESEARCH Pitfall 5).
         a. `pyproject.toml` line 7: `version = "1.3.0"` -> `version = "1.4.0"`.
         b. `ketu/__init__.py` line 57: `__version__ = "1.3.0"` ->
            `__version__ = "1.4.0"`.
       Both MUST be bumped together — bumping only one fails the sync gate
       (RESEARCH Pitfall 10).

    3. Re-install the editable package so importlib.metadata picks up the new
       version, then run the sync gate:
         `pip install -e . -q && pytest tests/test_version.py -v`
       Both version tests MUST pass.
  </action>
  <verify>
    `python -m mypy --strict ketu/` reports ZERO errors;
    `grep -n 'cast(np.ndarray' ketu/synastry/api.py` matches at the filtered
    return; `grep -n 'version = "1.4.0"' pyproject.toml` and
    `grep -n '__version__ = "1.4.0"' ketu/__init__.py` both match;
    `pytest tests/test_version.py -v` is GREEN; `git diff --stat
    docs/source/conf.py` shows NOTHING (conf.py untouched).
  </verify>
  <done>
    mypy --strict is clean; pyproject.toml and ketu/__init__.py both read
    "1.4.0"; ketu.__version__ == importlib.metadata.version("ketu") == "1.4.0";
    test_version.py passes; conf.py untouched.
  </done>
</task>

<task type="auto">
  <name>Task 2: Author root CHANGELOG [1.4.0] fresh, sync fr/CHANGELOG, and date-stamp docs/source/changelog.md</name>
  <files>CHANGELOG.md, fr/CHANGELOG.md, docs/source/changelog.md</files>
  <action>
    Unlike v1.3 (which MERGED an existing [Unreleased] section), the root
    CHANGELOG has NO [Unreleased] and NO [1.4.0] — the [1.4.0] block must be
    AUTHORED FRESH (RESEARCH Pitfall 1). Read CHANGELOG.md first to confirm
    `## [1.3.0] - 2026-06-01` is the current top section (line 10).

    Determine the release date: use TODAY's UTC date in `YYYY-MM-DD` form
    (`date -u +%F`). Use the SAME date in CHANGELOG.md, fr/CHANGELOG.md, and the
    docs/source/changelog.md [1.4.0] header.

    1. CHANGELOG.md — insert a fresh `## [1.4.0] - <date>` block IMMEDIATELY
       above `## [1.4.0]`'s eventual position, i.e. above the current
       `## [1.3.0] - 2026-06-01` header (after line 9, the blank line). Use the
       Keep-a-Changelog root format (`### Added` / `### Changed`, NOT the docs
       `### Added 1.4.0` format). Use the exact bullets from RESEARCH "Root
       CHANGELOG.md [1.4.0] section to author":
         ### Added
         - generate_harmonic_aspects(h) dynamic harmonic generator (2 <= h <= 64,
           coef=k/h full-circle 360° folded to 0-180°; structured array
           compatible with core.aspects; dynamic_specs= arg to calculate_aspects,
           find_aspects_between_dates, calculate_synastry; frozen 14-row
           core.aspects + preset fingerprints byte-identical; available at
           ketu.aspects.generate_harmonic_aspects and
           ketu.aspects.harmonics.generate_harmonic_aspects). (Phase 28)
         - Chiron range expanded to 1900-2100 (ketu/data/chiron_coeffs.npz
           regenerated, 2283 Chebyshev segments, jd_start=2415020.5 /
           jd_end=2488069.5, seg=32 days, degree=10; max |Δλ| = 0.001214°;
           pure-NumPy runtime; .npz ~578 KB, was 289.7 KB;
           calc_planet_position(jd, 13) resolves any JD in the new range incl.
           1900-1949 and 2051-2100). (Phase 30)
         ### Changed
         - Chiron orb 0° -> 4° (Pluto parity): core.bodies['orb'] for Chiron is
           now 4°; Chiron now forms scored aspects in calculate_aspects,
           compute_chart, calculate_synastry, find_aspects_between_dates;
           downstream code that expected zero Chiron aspects must adapt; see
           UPGRADING.md -> "v1.3 -> v1.4". (Phase 29)
         - Chiron out-of-range clamping: JD outside 1900-2100 is now silently
           clamped to the nearest segment boundary; previously raised
           ValueError. (Phase 30)
         - Documentation recentred on the 180°-division default: concepts.md
           aspect tables show CLASSICAL (5) and TRADITIONAL (7) only; full-circle
           minor harmonics (H5/H9/H10 / EXTENDED) remain in code but are removed
           from the summary tables. (Phase 31)
       Leave `## [1.3.0] - 2026-06-01` and everything below untouched.

    2. fr/CHANGELOG.md — insert a matching `## [1.4.0] - <date>` section ABOVE
       the existing `## [1.3.0] - 2026-06-01`, in French, matching the file's
       existing style (`### Ajouts` / `### Modifié`). Use the bullets from
       RESEARCH "fr/CHANGELOG.md Required Delta" (générateur d'harmoniques
       dynamiques, plage Chiron 1900-2100, orbe Chiron 0°->4°, comportement
       hors-plage bridé, documentation recentrée 180°). The EN file is
       authoritative (per the fr header note) — this is a synthesized
       translation, not double-maintained.

    3. docs/source/changelog.md — date-stamp the placeholders (RESEARCH
       Pitfalls 2 & 3):
         a. Line 8: `## [1.4.0] - 2026-06-XX` -> `## [1.4.0] - <date>` (today's
            real UTC date, same as above).
         b. Line 21: `## [1.3.0] - 2026-06-XX` -> `## [1.3.0] - 2026-06-01`
            (the actual v1.3.0 release date from root CHANGELOG.md).
       Do NOT change the docs body content (Phase 31 wrote it) — only the dates.
       (Note: line 36 `## [1.2.0] - 2026-04-XX` is out of scope; leave it.)
  </action>
  <verify>
    `grep -c '^## \[1.4.0\] - 20' CHANGELOG.md` returns 1;
    `! grep -q '^## \[1.4.0\] - 2026-06-XX' CHANGELOG.md` (no XX placeholder);
    `! grep -q '^## \[Unreleased\]' CHANGELOG.md` (no Unreleased);
    `grep -q 'generate_harmonic_aspects' CHANGELOG.md` and
    `grep -q 'Chiron' CHANGELOG.md` both match under [1.4.0];
    `grep -c '^## \[1.4.0\] - 20' fr/CHANGELOG.md` returns 1 and
    `grep -q 'générateur' fr/CHANGELOG.md` matches;
    `! grep -q '\[1.4.0\] - 2026-06-XX' docs/source/changelog.md` and
    `! grep -q '\[1.3.0\] - 2026-06-XX' docs/source/changelog.md` (both
    placeholders resolved).
  </verify>
  <done>
    CHANGELOG.md has exactly one dated `[1.4.0]` section (authored fresh, no
    Unreleased, no XX) carrying Added (generator + Chiron range) and Changed
    (orb 0->4 + clamp + docs recentring), with [1.3.0] and below untouched;
    fr/CHANGELOG.md has a matching dated French `[1.4.0]` section;
    docs/source/changelog.md [1.4.0] and [1.3.0] dates are resolved.
  </done>
</task>

<task type="auto">
  <name>Task 3: Add UPGRADING v1.3 -> v1.4 section and README What's New in v1.4.0</name>
  <files>UPGRADING.md, README.md</files>
  <action>
    Both files need a NEW newest-first section (RESEARCH Pitfall 13 — the
    Chiron orb change IS a behavioural break and MUST be documented).

    1. UPGRADING.md — add a `## v1.3 -> v1.4` section as the NEW FIRST section,
       inserted before the existing `## v1.2 -> v1.3` (currently at line 6).
       Use the markdown from RESEARCH "UPGRADING.md Required Delta", covering
       four sub-sections:
         a. `### Chiron orb changed from 0° to 4° — Chiron now forms aspects`:
            core.bodies['orb'] for Chiron is now 4° (was 0°); calculate_aspects,
            compute_chart, calculate_synastry, find_aspects_between_dates now
            detect+score Chiron aspects; downstream code assuming zero Chiron
            aspects must update; CHART_DTYPE body axis UNCHANGED from v1.3 (still
            14 bodies / indices 0-13) — only the orb scalar changes; Kala /
            downstream guidance: body_id=13 (Chiron) aspect tallies are now
            non-empty, recompute after upgrade.
         b. `### Chiron out-of-range behaviour: ValueError -> silent clamp`:
            JD outside 1900-2100 to calc_planet_position(jd, 13) /
            calc_planet_position_batch(jds, 13) is now silently clamped to the
            nearest segment boundary; previously raised ValueError; code relying
            on the ValueError for bounds checking must add explicit range
            validation.
         c. `### Chiron range expanded: 1950-2050 -> 1900-2100`: now resolves
            any JD in 1900-2100; embedded .npz regenerated, no code changes
            needed; include the runnable verify snippet from RESEARCH (JD
            2422324.5 ≈ 1920-01-01, assert math.isfinite(lon) and 0 <= lon <
            360).
         d. `### Dynamic harmonic generator — additive, no migration needed`:
            ketu.aspects.generate_harmonic_aspects(h) is new + pure-additive; no
            existing imports/callers change; opt in by passing
            dynamic_specs=generate_harmonic_aspects(h) to calculate_aspects,
            find_aspects_between_dates, or calculate_synastry.
       Do NOT modify the existing `## v1.2 -> v1.3` content.

    2. README.md — add a `## What's New in v1.4.0` section inserted BEFORE the
       current `## What's New in v1.3.0` (line 13), keeping newest-first. Use
       the markdown from RESEARCH "README.md Required Delta": a short intro
       paragraph (dynamic harmonic generator + Chiron range 1900-2100; the two
       behavioural changes are Chiron orb 0->4 and silenced out-of-range clamp;
       links to UPGRADING.md and CHANGELOG.md) followed by three bullets
       (Dynamic harmonic generator; Chiron range 1900-2100 with 2283 segments /
       max error 0.001214°; Chiron orb 4°), and a trailing `---` separator so
       the existing v1.3 section remains visually delimited. Do NOT modify the
       existing v1.3.0 / v1.2.0 README sections.
  </action>
  <verify>
    `grep -q '^## v1.3 -> v1.4' UPGRADING.md`;
    `grep -iq 'silent clamp\|silently clamped' UPGRADING.md`;
    `grep -q 'generate_harmonic_aspects' UPGRADING.md`;
    `grep -q '2422324.5' UPGRADING.md` (the 1920 verify snippet);
    `grep -q '^## What.s New in v1.4.0' README.md`;
    `grep -q '^## What.s New in v1.3.0' README.md` (v1.3 section preserved);
    `grep -c '^## v1.2 -> v1.3' UPGRADING.md` returns 1 (existing section intact).
  </verify>
  <done>
    UPGRADING.md `## v1.3 -> v1.4` is the new first section with the four
    sub-sections (orb break, clamp, range, additive generator) and the runnable
    1920 verify snippet; README has `## What's New in v1.4.0` above the existing
    v1.3.0 section; both existing v1.2->v1.3 / v1.3.0 sections are unchanged.
  </done>
</task>

</tasks>

<verification>
- `python -m mypy --strict ketu/` reports ZERO errors (synastry/api.py:392 fixed via cast).
- `pytest tests/test_version.py -v` GREEN; pyproject.toml + ketu/__init__.py both "1.4.0"; conf.py untouched (`git diff --stat docs/source/conf.py` empty).
- CHANGELOG.md: exactly one `## [1.4.0] - <date>` section (fresh, no Unreleased, no XX); Added has generate_harmonic_aspects + Chiron range; Changed has orb 0->4 + clamp + docs recentring; [1.3.0] and below unchanged.
- fr/CHANGELOG.md: dated `## [1.4.0]` section translating the same bullets.
- docs/source/changelog.md: [1.4.0] and [1.3.0] date placeholders resolved (no `2026-06-XX` in either header).
- UPGRADING.md: `## v1.3 -> v1.4` first section with orb break + clamp + range + additive generator.
- README.md: `## What's New in v1.4.0` above the existing v1.3.0 section.
- Full suite still green: `pytest tests/ -q` (expect 1537 passed, 2 skipped).
</verification>

<success_criteria>
REL-12 satisfied: the pre-existing mypy --strict error is fixed (release gate
unblocked); version bumped to 1.4.0 in both source-of-truth files (sync gate
green); CHANGELOG has a single dated `[1.4.0]` entry listing Added (dynamic
harmonics generator, Chiron 1900-2100 range) and Changed (Chiron orb 0°->4°,
out-of-range clamp, documentation recentring); fr/CHANGELOG synced; UPGRADING
documents the v1.3 -> v1.4 behavioural breaks; README has a What's New section;
docs/source/changelog.md is date-stamped. No `ketu/` calculation logic changed
beyond the typing-only `cast` at synastry/api.py:392.
</success_criteria>

<output>
After completion, create
`.planning/phases/32-release-v1-4-0/32-01-SUMMARY.md`
</output>
