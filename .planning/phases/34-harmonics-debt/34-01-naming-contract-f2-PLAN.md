---
phase: 34-harmonics-debt
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - ketu/aspects/harmonics.py
  - tests/test_dynamic_harmonics.py
  - docs/source/concepts.md
  - docs/source/api.md
  - docs/locale/fr/LC_MESSAGES/concepts.po
  - docs/locale/fr/LC_MESSAGES/concepts.mo
  - docs/locale/fr/LC_MESSAGES/api.po
  - docs/locale/fr/LC_MESSAGES/api.mo
autonomous: true

must_haves:
  truths:
    - "generate_harmonic_aspects(h)['name'] is pinned exactly for h=2, h=7, even-h folding, and all h in [2..64]"
    - "The H{h}-{k} naming scheme (bytes S16, ascending k=1..h//2, no traditional-name substitution) is documented as a public API contract"
    - "Docs distinguish the GENERATOR channel (always emits H{h}-{k}) from the DETECTION channel (prefers canonical table name on angle collision, e.g. 120° -> Trine not H3-1)"
    - "core.aspects V1/V13 sha256 fingerprints stay byte-identical (no core.py change)"
  artifacts:
    - path: tests/test_dynamic_harmonics.py
      provides: "TestNamingContractF2 pinning class (h7 exact, h2 boundary, even-h last row, all-h format, collision-prefers-table)"
      contains: "class TestNamingContractF2"
    - path: ketu/aspects/harmonics.py
      provides: "generate_harmonic_aspects docstring promoted to public API contract statement (Notes section already present)"
      contains: "H{h}-{k}"
    - path: docs/source/concepts.md
      provides: "Two-channel distinction + traditional-name reference table"
      contains: "H{h}-{k}"
    - path: docs/locale/fr/LC_MESSAGES/concepts.mo
      provides: "Compiled French translation of the new contract paragraphs"
  key_links:
    - from: tests/test_dynamic_harmonics.py
      to: ketu.aspects.harmonics.generate_harmonic_aspects
      via: "import + direct call asserting ['name'].tolist()"
      pattern: "generate_harmonic_aspects"
    - from: tests/test_dynamic_harmonics.py
      to: ketu.aspects.calculator.calculate_aspects
      via: "collision test (H3-1 at 120° must surface as Trine i_asp=9, not i_asp=-2)"
      pattern: "calculate_aspects"
---

<objective>
Pay down debt **F2 (ASP-F2, HARM-01..03)**: turn the already-correct `H{h}-{k}`
synthetic-aspect naming behaviour into a **documented, pinned public API
contract**.

Purpose: The CLI surface (F1, Plan 03) depends on the naming contract being
stable. F2 is FIRST in the locked F2 → F3 → F1 order. Per research, the
generator code in `harmonics.py` is ALREADY correct — this plan adds ZERO
behavioural code changes; it is a pure **test + docstring + docs** addition.

Output:
- A `TestNamingContractF2` pinning class in `tests/test_dynamic_harmonics.py`.
- A public-API-contract statement promoted into the `generate_harmonic_aspects`
  docstring (numpydoc-clean).
- The two-channel distinction (GENERATOR vs DETECTION) + a traditional-name
  reference table in `docs/source/concepts.md` and `api.md`.
- French translations of the new doc paragraphs (`.po` edited + `.mo` recompiled).
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

@ketu/aspects/harmonics.py
@docs/source/concepts.md
@docs/source/api.md

**Hard gates (bake into verification):**
- `core.aspects` V1/V13 sha256 fingerprints byte-identical — NO change to
  `ketu/core.py`. (V1=`c5bd177316ce98d428bee011a5b0f17ae247d1dee1e478c2389af51d39afb359`,
  V13=`3258530818272989c27eb6de6a717947df1a2fccda10d9562aa15ef67b8f27d8`)
- `fail_under=100` coverage, zero pragma. (Generator is unchanged → no new
  branches; the new tests must still all pass and add no uncovered code.)
- numpydoc + interrogate gates pass for `harmonics.py` after the docstring edit.
- mypy `--strict` clean on `harmonics.py` (no signature change — trivially clean).
- Docs are en + fr — translate new paragraphs in the `.po` and recompile `.mo`.

**Locked decision (do NOT reopen):** Generator naming is ALWAYS `H{h}-{k}`; NO
traditional-name substitution in generator output. Traditional names
(quintile/septile/novile…) appear in DOCS ONLY as a human reference table. The
emitted `name` bytes stay `H{h}-{k}`. Do NOT add traditional names to the
structured array.
</context>

<tasks>

<task type="auto">
  <name>Task 1: Pin the H{h}-{k} naming contract with TestNamingContractF2</name>
  <files>tests/test_dynamic_harmonics.py</files>
  <action>
Add a new test class `TestNamingContractF2` to `tests/test_dynamic_harmonics.py`
(append near the existing `TestGenerateH7Values` / `TestEvenHEmits180NeverO360`
classes; reuse the file's existing imports — `numpy as np`, `pytest`,
`generate_harmonic_aspects`). The class pins the contract for representative
harmonics and boundaries (HARM-01, HARM-02, HARM-03):

  - `test_naming_contract_h7_exact` — assert
    `specs['name'].tolist() == [b'H7-1', b'H7-2', b'H7-3']`;
    `specs['name'].dtype == np.dtype('S16')`;
    angles `[51.43, 102.86, 154.29]` (round 2);
    coefs `[0.1429, 0.2857, 0.4286]` (round 4);
    `specs['symbol'].tolist() == ['', '', '']` (U4 unicode empty string, NOT
    `b''` — see research pitfall); `specs['harmonic'].tolist() == [7, 7, 7]`.
  - `test_naming_contract_h2_opposition_only` — `generate_harmonic_aspects(2)`
    yields exactly 1 row, `name == [b'H2-1']`, `angle[0] == 180.0`.
  - `test_naming_contract_even_h_last_row` — for `h in [2, 4, 6, 8, 12]`:
    `len(specs) == h // 2` and `float(specs['angle'][-1]) == pytest.approx(180.0, abs=1e-4)`.
  - `test_naming_contract_all_h` — for ALL `h in range(2, 65)`: `len(specs) == h // 2`,
    and every row name matches regex `rb'^H(\d+)-(\d+)$'` with group(1)==h and
    group(2)==k where k is 1-indexed (`j + 1`). This locks the full
    contract across h=2..64 (HARM-02 "h up to 64").
  - `test_naming_collision_detection_prefers_table_name` — import
    `from ketu.aspects.calculator import calculate_aspects`; build
    `specs = generate_harmonic_aspects(3)` (H3-1 at 120° collides with Trine);
    call `calculate_aspects(2451545.0, dynamic_specs=specs)`; assert at least one
    row has `i_asp == 9` (Trine), demonstrating the DETECTION layer's static-first
    priority — the 120° hit is tagged Trine, NOT `i_asp=-2`/H3-1. This pins the
    HARM-03 collision semantics. (Use the exact-array indexing the result returns:
    `result['i_asp']` for the structured array.)

Use the test bodies sketched in research §"Debt F2 → Test specs" as the
authoritative reference, but ground field access in the actual structured-array
shape returned by `calculate_aspects` (fields `body1,body2,i_asp,orb`).
Do NOT modify any existing test in the file.
  </action>
  <verify>
`venv/bin/pytest tests/test_dynamic_harmonics.py::TestNamingContractF2 -v` →
all 5 tests pass. Then full guard:
`venv/bin/pytest tests/test_dynamic_harmonics.py -q` → green (no regressions).
  </verify>
  <done>
TestNamingContractF2 exists with the 5 pinning tests; all pass; no existing
test modified; the all-h test covers h=2..64; the collision test confirms
static-first (Trine, not H3-1) detection.
  </done>
</task>

<task type="auto">
  <name>Task 2: Promote the naming contract to the generator docstring (numpydoc-clean)</name>
  <files>ketu/aspects/harmonics.py</files>
  <action>
The naming behaviour is already correct and already partly documented in the
`Notes` section of `generate_harmonic_aspects` (lines ~149-167) and the module
docstring. Make NO change to any executable code (the generator stays
byte-identical; the V1/V13 fingerprints depend on `core.py`, not this file, but
keep this file's runtime behaviour unchanged regardless).

Edit ONLY docstrings to make the public-API-contract guarantee explicit:
  - In the `generate_harmonic_aspects` `Notes` section, add a short "Public API
    contract" paragraph stating: the emitted `name` field is ALWAYS the byte
    string `b'H{h}-{k}'` (S16) for `k = 1..h//2` in ascending `k` order; this
    `(h, k) → (name, angle, coef)` mapping is FROZEN across v1.5+ minor/patch
    releases; NO traditional-name substitution is ever performed by the
    generator (traditional names like quintile/septile/novile are documentation
    references only); adding support for new `h` never alters existing rows.
  - Keep the existing numpydoc structure intact (Parameters / Returns / Raises /
    Notes / Examples). Do not break any existing doctest (the `Examples` block
    must still pass `make doctest`).

This is docstring-only; `__all__` and signatures are unchanged.
  </action>
  <verify>
`venv/bin/python -m numpydoc validate ketu.aspects.harmonics.generate_harmonic_aspects`
(or the project's numpydoc gate, e.g. `make numpydoc` / the pyproject-configured
invocation) → passes. `venv/bin/interrogate ketu/aspects/harmonics.py` → 100%.
`venv/bin/python -m pytest --doctest-modules ketu/aspects/harmonics.py -q` (or
`make doctest`) → existing doctests still pass. `git diff --stat ketu/core.py` →
no change to core.py.
  </verify>
  <done>
The contract paragraph is in the docstring; numpydoc + interrogate green;
doctests unchanged-and-passing; no executable-code change in harmonics.py;
core.py untouched.
  </done>
</task>

<task type="auto">
  <name>Task 3: Document the two-channel distinction + traditional-name table (en + fr)</name>
  <files>docs/source/concepts.md, docs/source/api.md, docs/locale/fr/LC_MESSAGES/concepts.po, docs/locale/fr/LC_MESSAGES/concepts.mo, docs/locale/fr/LC_MESSAGES/api.po, docs/locale/fr/LC_MESSAGES/api.mo</files>
  <action>
**English docs:**
  - `docs/source/concepts.md` (near the existing "Harmonic Theory" section,
    ~line 70, and the `generate_harmonic_aspects` discussion): add a subsection
    "Synthetic harmonic naming (H{h}-{k})" that states the two-channel rule:
      1. GENERATOR channel: `generate_harmonic_aspects(h)` ALWAYS emits
         `H{h}-{k}` names (k = 1..h//2), uniform, no traditional substitution.
      2. DETECTION channel: when `calculate_aspects`/`find_aspects_between_dates`
         detect an angle that collides with a canonical table aspect, they
         report the canonical table name (e.g. a 120° hit is `Trine`, NOT
         `H3-1`) — static-first priority. H{h}-{k} names appear only for
         genuinely off-table angles (i_asp=-2 rows).
    Then add the human-only traditional-name reference table:
    `H5-1 ≡ quintile`, `H5-2 ≡ biquintile`, `H7-1 ≡ septile`,
    `H9-1 ≡ novile`, `H9-2 ≡ binovile`, `H9-4 ≡ quadnovile`. Make explicit:
    these traditional names are docs-only and never appear in emitted bytes.
  - `docs/source/api.md` (the existing `generate_harmonic_aspects(h)` section,
    ~line 221): add a "Naming contract" note: emitted `name` bytes are always
    `b'H{h}-{k}'` (S16), ascending k, frozen across v1.5+; cross-reference the
    concepts two-channel distinction. Do NOT duplicate the full table; link it.

**French translation (required — docs are en + fr):**
  - Run `make -C docs gettext` then `make -C docs update-po` (via venv) to
    extract the new strings into `concepts.po` / `api.po`.
  - Translate the new paragraphs + table into French in
    `docs/locale/fr/LC_MESSAGES/concepts.po` and `api.po` (rigorous, no
    English-fallback for the new msgids).
  - Recompile: `make -C docs build-mo` (or `sphinx-intl ...`) to regenerate
    `concepts.mo` and `api.mo`. Confirm no `fuzzy` flags remain on the new
    entries and the `.mo` timestamps are newer than the `.po`.
  </action>
  <verify>
`grep -n "H{h}-{k}" docs/source/concepts.md` and `grep -n "Trine" docs/source/concepts.md`
→ the two-channel paragraph is present. `grep -ni "septile" docs/source/concepts.md`
→ traditional-name table present. `grep -n "H{h}-{k}\|naming contract\|Naming contract" docs/source/api.md`
→ api note present. `msgfmt -c docs/locale/fr/LC_MESSAGES/concepts.po` and
`msgfmt -c docs/locale/fr/LC_MESSAGES/api.po` → no errors; the new msgids are
translated (not empty). `make -C docs html-fr` (or `html-all`) builds without
warnings about untranslated new strings.
  </verify>
  <done>
concepts.md + api.md carry the two-channel distinction and (concepts) the
traditional-name reference table; the new strings are translated in fr `.po`
and the `.mo` files are recompiled; no fuzzy/empty new entries.
  </done>
</task>

</tasks>

<verification>
- `venv/bin/pytest tests/test_dynamic_harmonics.py -q` → green (new
  TestNamingContractF2 + existing all pass).
- `venv/bin/pytest tests/test_ketu.py -k fingerprint -q` and the V1/V13
  fingerprint tests in `tests/test_dynamic_harmonics.py` → green (byte-identical;
  proves no core.aspects drift).
- `venv/bin/pytest tests/ -q` → full suite green, coverage `fail_under=100`
  satisfied, zero pragma added.
- mypy `--strict` clean on `ketu/aspects/harmonics.py`.
- numpydoc + interrogate gates pass for `harmonics.py`.
- French `.po`/`.mo` updated and compile clean (`msgfmt -c`).
</verification>

<success_criteria>
- HARM-01: `H{h}-{k}` is a documented public API contract (docstring + concepts/api docs).
- HARM-02: pinning test asserts `generate_harmonic_aspects(h)['name']` exactly for
  h=2 (opposition-only), even-h last-row-180°, and all h in [2..64].
- HARM-03: docs distinguish GENERATOR (always H{h}-{k}) from DETECTION (canonical
  name on collision, 120° → Trine), and a test confirms static-first detection.
- core.aspects V1/V13 sha256 fingerprints byte-identical (no core.py change).
- en + fr docs in sync; gates green.
</success_criteria>

<output>
After completion, create `.planning/phases/34-harmonics-debt/34-01-SUMMARY.md`.
</output>
