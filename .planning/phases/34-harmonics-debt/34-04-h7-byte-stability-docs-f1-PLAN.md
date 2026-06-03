---
phase: 34-harmonics-debt
plan: 04
type: execute
wave: 3
depends_on: ["34-01", "34-02", "34-03"]
files_modified:
  - tests/cli/fixtures/harmonics_h7_reference_output.txt
  - tests/cli/test_v1_1_reference_byte_stable.py
  - docs/source/concepts.md
  - docs/source/api.md
  - docs/locale/fr/LC_MESSAGES/concepts.po
  - docs/locale/fr/LC_MESSAGES/concepts.mo
  - docs/locale/fr/LC_MESSAGES/api.po
  - docs/locale/fr/LC_MESSAGES/api.mo
autonomous: true

must_haves:
  truths:
    - "A NEW byte-stability fixture tests/cli/fixtures/harmonics_h7_reference_output.txt exists, freshly generated and manually audited"
    - "The fixture shows synthetic H7-1/H7-2/H7-3 names (NOT Quadrinovile), septile angles (~51.43/102.86/154.29°), and the unchanged classical-pinned 'Aspect Timing Example' block"
    - "The stderr resolved-config header for the h7 run reads '# Aspect set: h7 (...)'"
    - "A NEW sibling test class TestHarmonicsH7ByteStable pins the fixture; the existing TestV1_1ReferenceByteStable is UNCHANGED"
    - "The --harmonics h7 CLI surface (syntax, semantics, Tight-grammar boundary, what is deferred) is documented en + fr"
  artifacts:
    - path: tests/cli/fixtures/harmonics_h7_reference_output.txt
      provides: "Pinned stdout of 'python -m ketu --harmonics h7 aspects --date 2000-01-01T12:00:00Z'"
      contains: "H7-"
    - path: tests/cli/test_v1_1_reference_byte_stable.py
      provides: "TestHarmonicsH7ByteStable sibling class (existing class untouched)"
      contains: "class TestHarmonicsH7ByteStable"
    - path: docs/source/concepts.md
      provides: "--harmonics h7 CLI section (syntax/semantics/Tight-grammar boundary)"
      contains: "--harmonics h7"
    - path: docs/locale/fr/LC_MESSAGES/concepts.mo
      provides: "Compiled French translation of the h7 CLI section"
  key_links:
    - from: tests/cli/test_v1_1_reference_byte_stable.py
      to: tests/cli/fixtures/harmonics_h7_reference_output.txt
      via: "subprocess run of --harmonics h7 compared byte-for-byte against the fixture"
      pattern: "harmonics_h7_reference_output"
    - from: tests/cli/test_v1_1_reference_byte_stable.py
      to: "python -m ketu --harmonics h7"
      via: "REFERENCE_ARGV_H7 subprocess"
      pattern: "--harmonics.*h7"
---

<objective>
Complete debt **F1 (ASP-F1) — byte-stability + docs (HARM-08, HARM-09)**: pin
the `--harmonics h7` CLI output with a freshly generated, manually audited
byte-stability fixture (the ketu ritual), and document the new CLI surface
en + fr.

Purpose: This is the final F1 plan. It DEPENDS on Plan 03 — the `--harmonics h7`
CLI must already produce correct output before its bytes can be pinned. The
existing v1.1 fixture stays UNCHANGED (verified, not re-pinned); a NEW sibling
fixture/test is added for `h7`.

Output:
- `tests/cli/fixtures/harmonics_h7_reference_output.txt` (generated + audited + pinned).
- `TestHarmonicsH7ByteStable` sibling class in `test_v1_1_reference_byte_stable.py`.
- `--harmonics h7` CLI section in `concepts.md` + `api.md`, translated to fr.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/REQUIREMENTS.md
@.planning/phases/34-harmonics-debt/34-RESEARCH.md

@tests/cli/test_v1_1_reference_byte_stable.py
@ketu/cli/aspects_cmd.py
@docs/source/concepts.md
@docs/source/api.md

**Hard gates (bake into verification):**
- Existing v1.1 CLI byte-stability fixture
  (`tests/cli/fixtures/v1_1_reference_output.txt`) and
  `TestV1_1ReferenceByteStable` stay UNCHANGED — verified, NOT re-pinned. Do NOT
  modify either. Only ADD a sibling fixture/test.
- The NEW `--harmonics h7` fixture is freshly generated and MANUALLY AUDITED
  before pinning (the ketu ritual — an agent audit step against documented
  expectations, NOT a blind regenerate).
- `fail_under=100` coverage, zero pragma.
- numpydoc + interrogate gates pass for any touched public surface (this plan
  adds tests + docs; no production code change expected).
- Docs are en + fr — translate the new paragraphs in `concepts.po`/`api.po`,
  recompile `.mo`.
- core.aspects V1/V13 sha256 fingerprints byte-identical (no core.py change).

**Locked decisions (do NOT reopen):**
- Header label `# Aspect set: h7` (threaded by Plan 03) is pinned in this fixture.
- Tight grammar is the documented surface; `h7,h11` and `traditional,h7` are
  DEFERRED (HARMF-01) — document them as "not yet supported", do NOT implement.
- The always-on "Aspect Timing Example" block stays classical-pinned and appears
  unchanged in the new fixture.
</context>

<tasks>

<task type="auto">
  <name>Task 1: Generate + MANUALLY AUDIT the h7 byte-stability fixture (ketu ritual)</name>
  <files>tests/cli/fixtures/harmonics_h7_reference_output.txt</files>
  <action>
This is the ketu ritual — generate, then AUDIT against documented expectations
BEFORE committing (NOT a blind regenerate).

1. Generate the fixture (stdout only) using the SAME reference date as the v1.1
   fixture so the position block is comparable:
   ```bash
   venv/bin/python -m ketu --harmonics h7 aspects --date 2000-01-01T12:00:00Z \
     > tests/cli/fixtures/harmonics_h7_reference_output.txt
   ```

2. AUDIT the generated file (read it, verify EACH expectation explicitly; if any
   fails, STOP — it means Plan 03 is wrong, do not pin a bad fixture):
   - The "Bodies Aspects" section shows DYNAMIC aspect rows named `H7-1`,
     `H7-2`, and/or `H7-3` (whichever pairs are in orb on that date) — and NEVER
     the string `Quadrinovile` (the pre-fix bug). `grep -c Quadrinovile` MUST be 0.
   - Any H7 aspect angle is from the septile family (~51.43°, ~102.86°,
     ~154.29°) — sanity-check that the orb columns are consistent with those
     base angles (the printed value is the orb/offset, not the base angle, so
     verify by re-deriving: the detected pairs should be near a septile angle).
   - The trailing "------------- Aspect Timing Example -------------" Sun-Moon
     block is PRESENT and identical in form to the v1.1 fixture's block (it is
     classical-pinned, always emitted). Diff it against the same block in
     `tests/cli/fixtures/v1_1_reference_output.txt` to confirm it is unchanged.
   - The degree symbol is U+00BA `º` (0xc2 0xba), NOT U+00B0 (consistent with the
     v1.1 convention).
   - Confirm the header `# Aspect set: h7` lands on STDERR, NOT in this stdout
     fixture (regenerate-check: `... 2>/tmp/h7.err` and `grep '# Aspect set: h7' /tmp/h7.err`).

3. Only after the audit passes, keep the fixture file as the pinned reference.
   Record the audit findings (the H7-k names seen, the date, the
   timing-block-unchanged confirmation) in the plan SUMMARY.
  </action>
  <verify>
`test -s tests/cli/fixtures/harmonics_h7_reference_output.txt` → non-empty.
`grep -c "H7-" tests/cli/fixtures/harmonics_h7_reference_output.txt` → ≥1.
`grep -c "Quadrinovile" tests/cli/fixtures/harmonics_h7_reference_output.txt` → 0.
`grep -c "Aspect Timing Example" tests/cli/fixtures/harmonics_h7_reference_output.txt` → 1.
`python3 -c "import pathlib; d=pathlib.Path('tests/cli/fixtures/harmonics_h7_reference_output.txt').read_bytes(); assert d.count(b'\xc2\xb0')==0; print('degree-symbol OK')"`
→ OK. Diff the trailing timing block vs v1_1 fixture → identical block.
  </verify>
  <done>
The h7 fixture is generated, audited (H7-k names not Quadrinovile, septile
angles, timing block unchanged, U+00BA degree symbol), and pinned; audit
findings recorded in the SUMMARY.
  </done>
</task>

<task type="auto">
  <name>Task 2: Add TestHarmonicsH7ByteStable sibling class (existing class untouched)</name>
  <files>tests/cli/test_v1_1_reference_byte_stable.py</files>
  <action>
Add a NEW class `TestHarmonicsH7ByteStable` to
`tests/cli/test_v1_1_reference_byte_stable.py`. Do NOT modify the existing
`TestV1_1ReferenceByteStable` class or its `FIXTURE`/`REFERENCE_ARGV` constants.

  - Add module-level constants:
    ```python
    FIXTURE_H7 = Path(__file__).parent / "fixtures" / "harmonics_h7_reference_output.txt"
    REFERENCE_ARGV_H7 = [sys.executable, "-m", "ketu",
                         "--harmonics", "h7", "aspects", "--date", REFERENCE_DATE]
    ```
    (reuse the existing `REFERENCE_DATE = "2000-01-01T12:00:00Z"`).
  - `class TestHarmonicsH7ByteStable` with subprocess-based tests (mirror the
    existing class's structure — subprocess, not in-process):
    - `test_fixture_exists_and_nonempty` — fixture committed and non-empty.
    - `test_h7_byte_identical_to_fixture` — run `REFERENCE_ARGV_H7`, assert
      rc==0 and `result.stdout == FIXTURE_H7.read_bytes()` (byte-for-byte);
      on mismatch emit a unified diff like the existing test.
    - `test_h7_stderr_contains_h7_header` — assert
      `"# Aspect set: h7" in result.stderr.decode()`.
    - `test_h7_stderr_structurally_clean` — every non-empty stderr line starts
      with `#` (no leak to stderr).
    - `test_h7_shows_synthetic_names_not_quadrinovile` — `b"H7-"` in stdout and
      `b"Quadrinovile"` NOT in stdout.
    - `test_h7_timing_example_block_present` — `b"Aspect Timing Example"` in stdout.
  </action>
  <verify>
`venv/bin/pytest tests/cli/test_v1_1_reference_byte_stable.py -v` → BOTH classes
pass (existing TestV1_1ReferenceByteStable UNCHANGED + new TestHarmonicsH7ByteStable).
`git diff tests/cli/fixtures/v1_1_reference_output.txt` → no change (existing
fixture untouched). `git diff tests/cli/test_v1_1_reference_byte_stable.py` →
only additive (new constants + new class; existing class body unchanged).
  </verify>
  <done>
TestHarmonicsH7ByteStable pins the h7 fixture and passes; the existing v1.1
class + fixture are byte-identical (additive-only diff).
  </done>
</task>

<task type="auto">
  <name>Task 3: Document the --harmonics h7 CLI surface (en + fr)</name>
  <files>docs/source/concepts.md, docs/source/api.md, docs/locale/fr/LC_MESSAGES/concepts.po, docs/locale/fr/LC_MESSAGES/concepts.mo, docs/locale/fr/LC_MESSAGES/api.po, docs/locale/fr/LC_MESSAGES/api.mo</files>
  <action>
**English:**
  - `docs/source/concepts.md` (near the existing `--harmonics` / Configurable
    Aspect Sets discussion): add a "`--harmonics h7` — arbitrary harmonics on the
    CLI" subsection covering:
      - Syntax: `--harmonics h<N>` (h-prefixed, case-insensitive; e.g. `h7`,
        `H7`). Produces the harmonic's `h//2` dynamic aspects via the
        `dynamic_specs=` channel (the `H{h}-{k}` synthetic names — link the F2
        two-channel section).
      - Semantics: selects ONLY that harmonic family (the table mask is empty);
        the resolved-config stderr header reads `# Aspect set: h7 (...)`.
      - Tight-grammar boundary (what is DEFERRED): `h7` alone OR the existing
        comma index list. Mixing (`traditional,h7`) and multi-harmonic
        (`h7,h11`) are NOT yet supported (tracked as HARMF-01) and are rejected
        with an error.
      - A short worked example (the `2000-01-01T12:00:00Z` invocation).
  - `docs/source/api.md` (the `--harmonics` / `parse_harmonics_spec` entry):
    update to reflect the `HarmonicsSelection` return type `(mask,
    dynamic_specs)` and the `h<N>` form; note preset/index inputs yield
    `dynamic_specs=None`.

**French:**
  - `make -C docs gettext && make -C docs update-po` (venv) → extract new strings
    into `concepts.po`/`api.po`.
  - Translate the h7 CLI section + the `HarmonicsSelection`/`h<N>` api note into
    French (`concepts.po`, `api.po`); no English-fallback for the new msgids.
  - `make -C docs build-mo` → recompile `concepts.mo`/`api.mo`. Confirm no
    fuzzy/empty new entries; `.mo` newer than `.po`.
  </action>
  <verify>
`grep -n "\-\-harmonics h7\|h<N>" docs/source/concepts.md` → section present with
the Tight-grammar/deferred note. `grep -n "HarmonicsSelection\|h<N>\|dynamic_specs" docs/source/api.md`
→ api note present. `msgfmt -c docs/locale/fr/LC_MESSAGES/concepts.po` and
`msgfmt -c docs/locale/fr/LC_MESSAGES/api.po` → no errors; new msgids translated.
`make -C docs html-fr` → builds without untranslated-new-string warnings.
  </verify>
  <done>
concepts.md + api.md document the `--harmonics h7` surface (syntax, semantics,
Tight-grammar boundary, deferred mixing); fr `.po` translated and `.mo`
recompiled.
  </done>
</task>

</tasks>

<verification>
- `venv/bin/pytest tests/cli/test_v1_1_reference_byte_stable.py -v` → both
  classes green; existing v1.1 fixture/class byte-identical (additive-only).
- `venv/bin/pytest tests/ -q` → full suite green; `fail_under=100`; zero pragma.
- The h7 fixture audit passed (H7-k names not Quadrinovile, septile angles,
  timing block unchanged, U+00BA degree symbol, `# Aspect set: h7` on stderr).
- fr `concepts.po/.mo` + `api.po/.mo` updated, compile clean.
- V1/V13 sha256 fingerprint tests green.
</verification>

<success_criteria>
- HARM-08: existing v1.1 fixture UNCHANGED (not re-pinned); NEW h7 byte-stability
  fixture freshly generated + manually audited + pinned; resolved-config stderr
  header labels the arbitrary-harmonic selection (`# Aspect set: h7`).
- HARM-09: `--harmonics h7` CLI surface documented en + fr (syntax, semantics,
  Tight-grammar boundary / deferred mixing).
</success_criteria>

<output>
After completion, create `.planning/phases/34-harmonics-debt/34-04-SUMMARY.md`.
</output>
