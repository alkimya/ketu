---
phase: 34-harmonics-debt
plan: 02
type: execute
wave: 2
depends_on: ["34-01"]
files_modified:
  - ketu/aspects/calculator.py
  - tests/test_find_aspect_timing_f3.py
  - docs/source/api.md
  - docs/locale/fr/LC_MESSAGES/api.po
  - docs/locale/fr/LC_MESSAGES/api.mo
autonomous: true

must_haves:
  truths:
    - "find_aspect_timing accepts dyn_coef: Optional[float] = None and derives orb = (bodies['orb'][b1]+bodies['orb'][b2])/2 * dyn_coef"
    - "The static path (orb=None, dyn_coef=None) returns byte-identical timing to before — backward compatible"
    - "The explicit orb=<float> escape hatch is unchanged and byte-identical"
    - "When BOTH orb and dyn_coef are given, explicit orb WINS SILENTLY (no ValueError)"
    - "An off-table angle with neither orb nor dyn_coef still raises ValueError"
  artifacts:
    - path: ketu/aspects/calculator.py
      provides: "find_aspect_timing with dyn_coef param + 3-branch orb resolution (explicit-orb-first)"
      contains: "dyn_coef"
    - path: tests/test_find_aspect_timing_f3.py
      provides: "TestFindAspectTimingF3: derives-orb, matches-calculate_aspects-formula, static-unchanged, explicit-orb-wins, off-table-raises"
      contains: "class TestFindAspectTimingF3"
    - path: docs/source/api.md
      provides: "find_aspect_timing dyn_coef parameter documented; precedence (explicit orb wins) stated"
      contains: "dyn_coef"
    - path: docs/locale/fr/LC_MESSAGES/api.mo
      provides: "Compiled French translation of the dyn_coef paragraph"
  key_links:
    - from: tests/test_find_aspect_timing_f3.py
      to: ketu.aspects.calculator.find_aspect_timing
      via: "import + call with dyn_coef= and orb=+dyn_coef= asserting precedence"
      pattern: "find_aspect_timing"
    - from: ketu.aspects.calculator.find_aspect_timing
      to: ketu.core.bodies
      via: "orb derivation mirrors calculate_aspects:215-216 ((orb_b1+orb_b2)/2*dyn_coef)"
      pattern: "bodies\\[.orb.\\]"
---

<objective>
Pay down debt **F3 (ASP-F3, HARM-04..05)**: let `find_aspect_timing` derive its
own dynamic orb from a coefficient instead of forcing the caller to pre-compute
and pass it as `orb=<float>`.

Purpose: A surgical, backward-compatible one-parameter addition. F3's logic is
INDEPENDENT of F2 and F1 (it touches `calculator.py`'s `find_aspect_timing`, not
the naming contract or the CLI). It is sequenced as **Wave 2, depends_on 34-01**
for ONE reason only: both plans edit the shared docs files (`docs/source/api.md`
and the fr `api.po`/`api.mo`), so they cannot run in parallel without a
file-ownership conflict. Serializing F3 after F2 also keeps the locked
F2 → F3 → F1 order explicit. F3 otherwise owns the `find_aspect_timing` region
of `calculator.py` + a NEW dedicated test file (avoiding the
`tests/test_dynamic_harmonics.py` shared by Plan 01).

Output:
- `find_aspect_timing(jdate, body1, body2, aspect_value, orb=None, dyn_coef=None)`
  with a 3-branch orb-resolution block (explicit `orb` checked FIRST).
- `tests/test_find_aspect_timing_f3.py` with `TestFindAspectTimingF3`.
- `find_aspect_timing` API docs updated (en + fr) — `dyn_coef` parameter +
  precedence rule.
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

@ketu/aspects/calculator.py
@docs/source/api.md

**Hard gates (bake into verification):**
- `fail_under=100` coverage, zero pragma — the new `dyn_coef is not None` branch
  MUST be covered by a test.
- mypy `--strict` clean on `ketu/aspects/calculator.py` (`Optional[float]` is
  trivially clean; no `np.void` single-row typing).
- numpydoc + interrogate gates pass for `find_aspect_timing` after the docstring
  edit.
- Pure-NumPy runtime (no new imports of pyswisseph).
- core.aspects V1/V13 sha256 fingerprints byte-identical (no core.py change).
- Docs are en + fr — translate the `dyn_coef` paragraph in `api.po`, recompile `.mo`.

**Locked decisions (do NOT reopen):**
- Signature gets `dyn_coef: Optional[float] = None` (Option (a)).
- Explicit `orb` is checked FIRST and short-circuits.
- **Precedence when BOTH `orb` and `dyn_coef` are given: explicit `orb` WINS
  SILENTLY (do NOT raise).** This overrides the brief's §4-C "raise"
  recommendation. Test the silent-wins behaviour, NOT a ValueError.
- Orb formula MUST equal `(bodies['orb'][body1] + bodies['orb'][body2]) / 2 * dyn_coef`,
  identical to `calculate_aspects` at `calculator.py:215-216`.
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add dyn_coef to find_aspect_timing (explicit-orb-first, 3-branch)</name>
  <files>ketu/aspects/calculator.py</files>
  <action>
Edit `find_aspect_timing` (def at `calculator.py:568`).

1. Signature — add `dyn_coef: Optional[float] = None` after `orb`:
   `def find_aspect_timing(jdate, body1, body2, aspect_value, orb=None, dyn_coef=None) -> Tuple[float, float, float]:`
   (`Optional`/`Tuple` are already imported in this module.)

2. Replace the current orb-resolution block (lines ~611-617, the
   `if orb is None:` block) with a 3-branch block whose ORDER encodes the locked
   precedence (explicit orb FIRST):

   ```python
   if orb is not None:
       # Explicit orb wins silently — escape hatch short-circuits, even when
       # dyn_coef is also provided (HARM-05 locked precedence: explicit orb
       # wins, NOT raise).
       pass
   elif dyn_coef is not None:
       # Dynamic path — derive orb from the coefficient. Mirrors the formula
       # in calculate_aspects (calculator.py:215-216):
       #   (orb_b1 + orb_b2) / 2 * dyn_coef
       orb = (
           float(bodies["orb"][body1]) + float(bodies["orb"][body2])
       ) / 2 * dyn_coef
   else:
       # Static path — frozen-table lookup (UNCHANGED behaviour).
       asp_idx = np.where(_CORE_ASPECTS["angle"] == aspect_value)[0]
       if len(asp_idx) == 0:
           raise ValueError(f"unknown aspect value: {aspect_value}")
       orb = get_orb(body1, body2, int(asp_idx[0]))
   ```

   `bodies` is the module-global default bodies array; `body1`/`body2` are body
   IDs used directly as positional indices (the default `bodies['id']` is
   `[0..13]`, so the positional index equals the body ID — same indexing the
   existing static path uses via `get_orb`). Confirm `bodies` is already
   imported at module top (it is used by `get_orb`); if not, import it from
   `ketu.core`.

3. Update the docstring (numpydoc): add the `dyn_coef : float, optional`
   parameter block describing the derived-orb formula and the precedence rule
   ("explicit `orb` wins silently when both are given"). Replace the stale
   "Pass the orb derived from your dynamic_specs row" instruction (lines
   ~590-593) with a pointer to `dyn_coef`. Keep the `Raises` note that an
   off-table angle with neither `orb` nor `dyn_coef` raises ValueError.

Do NOT change the backward/forward search loops or `find_exact_aspect` call —
only the orb-resolution block + signature + docstring.
  </action>
  <verify>
`venv/bin/python -c "import inspect; from ketu.aspects.calculator import find_aspect_timing; print(inspect.signature(find_aspect_timing))"`
→ shows `dyn_coef=None`. `venv/bin/mypy --strict ketu/aspects/calculator.py` →
clean. `venv/bin/python -m numpydoc validate ketu.aspects.calculator.find_aspect_timing`
(or `make numpydoc`) → passes. `git diff --stat ketu/core.py` → no change.
  </verify>
  <done>
Signature has `dyn_coef=None`; orb resolution is 3-branch explicit-orb-first;
formula matches calculate_aspects:215-216; docstring updated; mypy/numpydoc green.
  </done>
</task>

<task type="auto">
  <name>Task 2: TestFindAspectTimingF3 — derive, match-formula, static-unchanged, precedence, raise</name>
  <files>tests/test_find_aspect_timing_f3.py</files>
  <action>
Create a NEW test file `tests/test_find_aspect_timing_f3.py` (dedicated file so
it does not collide with Plan 01's edits to `tests/test_dynamic_harmonics.py`).
Add `class TestFindAspectTimingF3` with `JD = 2451545.0` and these tests
(import `find_aspect_timing` from `ketu.aspects.calculator`, `bodies` from
`ketu.core`, `pytest`):

  - `test_dyn_coef_derives_orb_internally` — call
    `find_aspect_timing(JD, 0, 1, 51.4286, dyn_coef=1/7)`; assert it returns a
    3-tuple of floats (no ValueError). This covers the NEW `dyn_coef` branch
    (HARM-04).
  - `test_dyn_coef_orb_matches_calculate_aspects_formula` — compute
    `expected_orb = (float(bodies['orb'][0]) + float(bodies['orb'][1])) / 2 * (1/7)`;
    assert `find_aspect_timing(JD, 0, 1, 51.4286, dyn_coef=1/7)
    == find_aspect_timing(JD, 0, 1, 51.4286, orb=expected_orb)`. Proves the
    derived orb equals the explicit one (HARM-04 cross-check).
  - `test_static_path_unchanged` — assert
    `find_aspect_timing(JD, 0, 1, 120.0) == find_aspect_timing(JD, 0, 1, 120.0, dyn_coef=None)`.
    Proves backward compatibility / byte-identical static path (HARM-05).
  - `test_explicit_orb_wins_over_dyn_coef` — with `explicit_orb=3.0` and
    `coef=1/7` (which would derive ~1.71°, different from 3.0), assert
    `find_aspect_timing(JD, 0, 1, 51.4286, orb=explicit_orb)
    == find_aspect_timing(JD, 0, 1, 51.4286, orb=explicit_orb, dyn_coef=coef)`.
    Proves explicit orb WINS SILENTLY (HARM-05 precedence — locked: NOT raise).
  - `test_off_table_no_orb_no_dyn_coef_raises` — `pytest.raises(ValueError)`
    around `find_aspect_timing(JD, 0, 1, 51.4286)` (off-table angle, neither
    orb nor dyn_coef). Proves the static-path ValueError is preserved (HARM-05).

Use research §"Debt F3 → Test specs" bodies as the authoritative reference.
  </action>
  <verify>
`venv/bin/pytest tests/test_find_aspect_timing_f3.py -v` → all 5 pass. Then
`venv/bin/pytest tests/test_dynamic_harmonics.py -k FindAspectTiming -q` → the
existing `TestFindAspectTimingGuards` (backward-compat paths) still pass
unchanged. Coverage: the new `dyn_coef` branch is exercised (confirm via
`venv/bin/pytest tests/ --cov=ketu/aspects/calculator --cov-report=term-missing -q`
showing no missing lines in the new block).
  </verify>
  <done>
TestFindAspectTimingF3 (5 tests) passes; existing TestFindAspectTimingGuards
unchanged-and-green; the dyn_coef branch is covered (no missing-lines).
  </done>
</task>

<task type="auto">
  <name>Task 3: Document find_aspect_timing dyn_coef (en + fr)</name>
  <files>docs/source/api.md, docs/locale/fr/LC_MESSAGES/api.po, docs/locale/fr/LC_MESSAGES/api.mo</files>
  <action>
**English:** In `docs/source/api.md`, update the `find_aspect_timing` entry (or
add it if only briefly present): document the new `dyn_coef` parameter — derives
the dynamic orb as `(bodies['orb'][b1] + bodies['orb'][b2]) / 2 * dyn_coef`,
removing the need for callers to pre-compute the orb for off-table harmonic
angles. State the precedence explicitly: when both `orb` and `dyn_coef` are
given, **explicit `orb` wins silently**. Note the static path (neither given,
table angle) and the off-table-raises behaviour are unchanged. Add a tiny code
example: `find_aspect_timing(jd, 0, 1, 51.4286, dyn_coef=1/7)` for the H7-1
Sun-Moon timing.

**French:** Run `make -C docs gettext && make -C docs update-po` (venv) to
extract new strings into `api.po`; translate the `dyn_coef` paragraph + example
caption to French in `docs/locale/fr/LC_MESSAGES/api.po`; recompile with
`make -C docs build-mo`. Confirm no fuzzy/empty new entries; `.mo` newer than `.po`.
  </action>
  <verify>
`grep -n "dyn_coef" docs/source/api.md` → present with precedence note.
`msgfmt -c docs/locale/fr/LC_MESSAGES/api.po` → no errors; the new dyn_coef
msgid is translated (non-empty). `make -C docs html-fr` builds without
untranslated-string warnings for the new entries.
  </verify>
  <done>
api.md documents dyn_coef + the "explicit orb wins" precedence; fr `.po`
translated and `.mo` recompiled.
  </done>
</task>

</tasks>

<verification>
- `venv/bin/pytest tests/test_find_aspect_timing_f3.py -v` → green.
- `venv/bin/pytest tests/ -q` → full suite green; `fail_under=100` satisfied;
  zero pragma added; the new `dyn_coef` branch covered.
- `venv/bin/mypy --strict ketu/aspects/calculator.py` → clean.
- numpydoc + interrogate pass for `find_aspect_timing`.
- V1/V13 sha256 fingerprint tests green (no core.aspects drift).
- fr `api.po`/`api.mo` updated and compile clean.
</verification>

<success_criteria>
- HARM-04: `find_aspect_timing` derives orb from `dyn_coef` via the
  `(orb_b1+orb_b2)/2*dyn_coef` formula (matches calculate_aspects).
- HARM-05: static path + explicit-orb escape hatch backward-compatible and
  byte-identical; precedence (explicit orb wins silently when both given)
  defined and tested; off-table-no-args still raises ValueError.
- mypy --strict + numpydoc + interrogate + 100% coverage green; en + fr docs synced.
</success_criteria>

<output>
After completion, create `.planning/phases/34-harmonics-debt/34-02-SUMMARY.md`.
</output>
