# Pitfalls Research — v1.4 Features on the Existing Ketu Codebase

**Domain:** Adding dynamic harmonics, Chiron orb change, Chiron range extension, doc
recentring to an unusually well-pinned pure-NumPy library (ketu==1.3.0).
**Researched:** 2026-06-02
**Confidence:** HIGH — every pitfall is grounded in actual source code and test
invariants read from the repository.

---

## Area 1 — Frozen Table / Fingerprint Preservation

### Pitfall 1-A: Dynamic path accidentally guarded by `_VALID_HARMONICS`

**What goes wrong:**
`_VALID_HARMONICS` in `ketu/aspects/presets.py:72` is a `frozenset` derived
data-driven from the frozen `core.aspects["harmonic"]` column —
`{1, 2, 3, 5, 6, 9, 10}`. The existing `aspects_for_harmonics()` raises
`ValueError` for any harmonic not in that set. If the dynamic path reuses
`aspects_for_harmonics(harmonics=[h])` as its entry point for arbitrary h
(e.g. h=7), it will raise instead of generating the aspect. The whole point
of the dynamic generator is to bypass the table entirely.

**Warning sign:**
`ValueError: unknown harmonic: 7. Valid harmonics: 1, 2, 3, 5, 6, 9, 10`
raised by the generator rather than producing a result.

**Prevention:**
The dynamic generator must be a **separate code path** that does NOT call
`aspects_for_harmonics` at all. It takes `(h, orb_override=None)`, computes
`k·360/h` for `k=1…floor(h/2)` in the unified-360° convention, folds > 180°
via `360 - angle`, deduplicates, and returns angle + computed orb directly
— never touching `core.aspects` rows or `_VALID_HARMONICS`.

**Phase to address:** Dynamic harmonic generator phase (the parallel-path
feature phase).

---

### Pitfall 1-B: Accidental mutation of `core.aspects` via the dynamic path

**What goes wrong:**
`core.aspects` is a `numpy` structured array. It is not frozen at the NumPy
level (`flags.writeable` is not set to False on the array itself in
`ketu/core.py`). If the dynamic generator constructs a new aspects array and
accidentally assigns it to `ketu.core.aspects` (e.g. via `import ketu.core as
_core; _core.aspects = new_arr`), the V1 and V13 sha256 fingerprint tests in
`tests/test_ketu.py:189-213` will fail immediately. However, the mutation
could also happen more subtly if a result array is created by concatenating
the table with dynamic rows and that concatenated array is inadvertently
stored back.

**Warning sign:**
`test_aspects_byte_fingerprint` fails with a new sha256 hash, OR
`test_aspects_length` fails with length > 14.

**Prevention:**
The dynamic path must operate on **transient in-function arrays only**. It
must not write to `ketu.core.aspects` or any module-level attribute derived
from it. The phase plan should include an explicit "no mutation of
`ketu.core`" constraint check. Consider adding a module-level
`aspects.flags.writeable = False` to `core.py` as belt-and-suspenders.

**Phase to address:** Dynamic harmonic generator phase.

---

### Pitfall 1-C: Cache keys based on `i_asp` (table index) break for dynamic aspects

**What goes wrong:**
The ASP-06 forward-looking rule in `ketu/aspects/presets.py:46-51` already
documents this: "a future cache that memoizes a function whose return value
depends on `aspects=` … MUST include `mask.tobytes()`." Dynamic aspects have
no row in the 14-row table, so `i_asp` is meaningless for them. If any new
cache (e.g. an LRU on a batch calculator) keys on `(jd, body1, body2,
i_asp)`, it will either crash (index out of range) or silently serve a stale
entry from a different aspect set.

The existing caches (`body_properties` LRU, `_cached_planet_position_batch`
in `ketu/aspects/core.py:75`) key on `(jd, planet_id)` — they are not
affected. But adding a results-level cache is a common optimization impulse
when building a hot generator loop.

**Warning sign:**
Correct result returned the first call, wrong result returned the second
call with different `h` but same `(jd, body1, body2)` — classic stale-cache
symptom. Or `IndexError: index 14 is out of bounds for axis 0 with size 14`.

**Prevention:**
Any new cache on aspect-detection output must key on the **full description
of the aspect being tested**: for table aspects, `i_asp` suffices; for dynamic
aspects, use `(angle_deg, orb_deg)` or a float-rounded tuple. Never mix the
two key schemas in the same cache dict.

**Phase to address:** Dynamic harmonic generator phase; verify during code
review that no new LRU cache is added without an explicit key-schema comment.

---

## Area 2 — Harmonic Math Edge Cases

### Pitfall 2-A: Emitting k=0 (0°) and duplicate mirror angles

**What goes wrong:**
For harmonic h, the full-circle positions are `k·360/h` for `k = 0, 1, …,
h-1`. The fold into [0°, 180°] maps any angle > 180° to `360 - angle`.
This produces duplicates:
- `k=0` → 0° (same as Conjunction; should be excluded if the dynamic path
  generates "other-than-conjunction" harmonics)
- For even h, `k = h/2` → 180° (Opposition), and `k = h - k' → 360 -
  (k'·360/h) = same angle` as `k = k'` when folded. So for h=4:
  k=0→0°, k=1→90°, k=2→180°, k=3→90°. After folding: {0°, 90°, 180°, 90°}
  → duplicates at 90°.
- For odd h (e.g. h=7), there is no exact 180° position. Folding k=4 gives
  `360 - 4·360/7 = 154.3°`, k=3 gives `3·360/7 = 154.3°` — same angle.
  All `k > h/2` mirror `k < h/2` after folding.

The correct iteration is `k = 1 … floor(h/2)`, yielding `floor(h/2)` unique
angles. `k=0` (0°/Conjunction) and the duplicates are excluded by construction.

**Warning sign:**
For h=4, generator emits [0°, 90°, 180°, 90°] — duplicates visible in output,
or unexpected 0° Conjunction-like aspects firing from the dynamic path when
body separation is near 0°.

**Prevention:**
Use `angles = [k * 360.0 / h for k in range(1, h // 2 + 1)]` as the canonical
loop. Do NOT use `range(1, h)` with a post-hoc `set()` deduplification — that
changes the order and does not handle floating-point near-duplicates reliably.
For the 180° boundary when h is even, `k = h//2` is a valid aspect (like
Opposition at h=1) — include it. Unit test: for h=4, result must be exactly
[90°, 180°]; for h=6, [60°, 120°, 180°]; for h=7, [51.4°, 102.9°, 154.3°].

**Phase to address:** Dynamic harmonic generator phase.

---

### Pitfall 2-B: Floating-point equality matching separation to generated angle

**What goes wrong:**
The generated angles are `k * 360.0 / h` in Python floats. For h=7 and k=1,
this is `51.42857142857143°`. If the matcher checks `abs(separation -
angle) < orb` using the un-rounded float as `angle`, results are correct. But
if the angle is stored as `float32` (as `core.aspects["angle"]` uses
`dtype="f4"`), the float32 representation of `51.42857142857143` is
`51.428570...` with truncation error. A dynamic angle must stay `float64`
throughout the match.

**Warning sign:**
Near-exact aspects (separation within 0.0001° of the theoretical angle) are
sometimes detected and sometimes missed — intermittent failure that appears
only at very tight orbs or when the body happens to be exactly at the aspect
angle.

**Prevention:**
Do not cast dynamic aspect angles to `float32`. Keep them as `float64` for
the entire lifetime of the match computation. Only round/truncate when
serializing to the output structured array's `angle` field (which can be `f4`
for display purposes if needed, but the match should use `f8`).

**Phase to address:** Dynamic harmonic generator phase.

---

### Pitfall 2-C: Tiny orbs for high harmonics silently producing no aspects

**What goes wrong:**
The coef-based orb for a dynamic aspect is `(orb_a + orb_b) / 2 * (k/h)`.
For h=18, k=1, Sun-Moon: `(12+12)/2 * (1/18) = 0.667°`. For h=36: `0.333°`.
At h=72: `0.167°`. These are valid aspects mathematically but will essentially
never appear in real chart data because planetary separations rarely land in
a 0.167° window. The dynamic generator must document this behavior rather than
treating it as a bug.

**Warning sign:**
User reports "H18 aspects always return empty result." The cause is not a bug
— it is expected behavior from the orb formula. Without documentation, this
looks like a defect.

**Prevention:**
Add a docstring note: "For harmonics above H12, the computed orb is typically
< 1°; aspects rarely appear in practice. This is expected behavior, not a
bug." Consider an optional `orb_override` parameter that bypasses the coef
formula for callers who want fixed-width orbs for research purposes.

**Phase to address:** Dynamic harmonic generator phase.

---

## Area 3 — Chiron Orb Change (0° → 4°)

### Pitfall 3-A: Synastry group-assert split in `test_orbs.py`

**What goes wrong:**
`tests/synastry/test_orbs.py` has three independent zero-orb tests:
- `test_synastry_orb_limit_rahu_rahu_zero_orb` (body 10, asserts `== 0.0`)
- `test_synastry_orb_limit_ketu_ketu_zero_orb` (body 11, asserts `== 0.0`)
- `test_synastry_orb_limit_lilith_lilith_zero_orb` (body 12, asserts `== 0.0`)

There is **no** `test_synastry_orb_limit_chiron_chiron_zero_orb` function in
the file — Chiron (body 13) is mentioned in test docstrings as a "zero-orb
body" but is not individually asserted. Therefore changing `bodies["orb"][13]`
from 0 to 4 in `core.py` does **not** break any existing `synastry/test_orbs.py`
test by assertion.

However, `test_body_orbs_15_canonical_entries_match_bodies` asserts
`_BODY_ORBS_16[:14] == _BODIES["orb"].astype(np.float32)` — this is a
derived-from-source test that passes automatically once `core.bodies` is
updated. The risk is in the docstring of
`test_self_synastry_dense_diagonal_is_conjunction` (lines 112-118), which
says "Rahu / Ketu / Lilith / Chiron have zero natal orbs." That docstring
becomes factually wrong after the change. A stale docstring is not a test
failure, but it becomes misleading for future maintainers.

**Warning sign:**
All tests pass but `test_modes_idempotent.py:test_self_synastry_dense_diagonal_is_conjunction`
docstring still says "Chiron" in the zero-orb list. Grep `zero natal orb` to
find all stale mentions.

**Prevention:**
After changing `core.bodies["orb"][13]` from 0 to 4:
1. Update `test_self_synastry_dense_diagonal_is_conjunction` docstring to
   read "Rahu / Ketu / Lilith have zero natal orbs (Chiron now 4°)."
2. Add a new explicit test: `test_synastry_orb_limit_chiron_nonzero_orb` that
   asserts `synastry_orb_limit(13, 13, 0) == pytest.approx(2.0, abs=1e-5)`
   (= (4+4)/2 * 1 * 0.5 = 2.0).
3. Grep `zero.*orb.*Chiron` and `Chiron.*zero.*orb` across the whole test
   tree to catch all stale references.

**Phase to address:** Chiron orb change phase.

---

### Pitfall 3-B: CLI byte-stable fixture shows NEW Chiron aspects at 4° orb

**What goes wrong:**
At the reference date `2000-01-01T12:00:00Z`, the fixture
`tests/cli/fixtures/v1_1_reference_output.txt` currently shows two Chiron
aspects:
- `Saturn  - Chiron : Quincunx  1º11' 2"` (orb 1.18° — within 4° at 0°
  natal, and still within 4° at 4° natal since the aspect fires by
  coef × half-sum = 5/6 × 5° = 4.17° > 1.18°. So this one was already
  detectable but only happened to fire because it was within the coef-reduced
  orb even at 0° natal Chiron.)
- `Pluto   - Chiron : Conjunction  0º 9'48"` (orb 0.16° — always fires)

Wait — re-examining: with `bodies["orb"][13] = 0`, the half-sum for any
Chiron pair is `(orb_other + 0) / 2 = orb_other / 2`. For Saturn(10°)-
Chiron(0°): half-sum = 5°. Quincunx coef = 5/6. Final orb = 5 × 5/6 ≈ 4.17°.
The current fixture shows the Quincunx at orb 1.18° — it fires because the
**Saturn** orb (10°) drives the half-sum even when Chiron=0°.

After changing Chiron to 4°, the Saturn-Chiron half-sum becomes `(10+4)/2 =
7°`. Quincunx orb = 7 × 5/6 ≈ 5.83°. So the same aspect still fires. **But
other pairs involving Chiron will newly start firing** — previously, for any
body pair (X, Chiron), the orb was `orb_X / 2 × coef`; now it is `(orb_X +
4) / 2 × coef`. For Pluto(4°)-Chiron: old = 2° × coef, new = 4° × coef — new
aspects involving Pluto-Chiron at looser separations will appear. For
Mercury(8°)-Chiron: old half-sum = 4°, new = 6°.

**Warning sign:**
`test_harmonics_all_byte_identical_to_v1_1_reference` FAILS with a diff
showing new Chiron aspect lines in the output. This is expected — the fixture
MUST be regenerated.

**Prevention:**
Regenerate the fixture using the command documented in the test file:
```
python -m ketu --harmonics all aspects --date 2000-01-01T12:00:00Z \
    > tests/cli/fixtures/v1_1_reference_output.txt
```
Then **manually audit** every new Chiron line added vs. the old fixture to
confirm each new aspect is astronomically plausible (separation < new orb
limit). Do not blindly accept the regenerated file — run `git diff` on the
fixture and check each new/changed line.

**Phase to address:** Chiron orb change phase.

---

### Pitfall 3-C: Other byte-stable or pinned-value tests that implicitly depend on Chiron's 0° orb

**What goes wrong:**
The `--harmonics all` fixture is the obvious one, but search must cover:
- Any test that uses a real julian date and asserts a specific aspect list
  (oracle tests in `tests/synastry/fixtures/*.json` use `orb_max_deg=5.0`
  for assertions, not the natal orb — these are safe).
- `tests/charts/test_aspect_matrix.py` — may assert specific aspect counts
  for reference dates; if a date was chosen where Chiron is near an aspect
  with another body within [old_limit, new_limit], counts change.
- `tests/test_ketu.py:test_calculate_aspects` — only asserts structural
  dtype and bounds, not specific aspect counts — safe.

**Warning sign:**
Any test that asserts a specific aspect count (e.g. `assert len(aspects) == 27`)
or a specific set of body pairs breaks.

**Prevention:**
Run `pytest -x` after changing `core.bodies["orb"][13]` and before
regenerating the CLI fixture. Every failing test that is not `test_harmonics_all_byte_identical`
must be diagnosed individually — it may be a legitimate change (new aspects
now fire) or a logic bug.

**Phase to address:** Chiron orb change phase.

---

## Area 4 — Chiron Ephemeris Range Regeneration (1950-2050 → 1900-2100)

### Pitfall 4-A: New first segment is partial-length and triggers the same bug as Phase 24's last-segment bug

**What goes wrong:**
Phase 24 hit a 0.905° error in the last segment because the evaluator
(`_eval_chiron_qty`) was using `seg_len=32` to compute `t`, but the last
segment was shorter than 32 days. The fix was `actual_len = min(seg_starts[si]
+ seg_len, jd_end) - seg_starts[si]`. This fix lives in the evaluator (line
113 of `ketu/ephemeris/chiron.py`) and uses `jd_end` from the loaded `.npz`.

Extending to 1900-2100 changes `jd_start` to the 1900-01-01 JD (~2415021.5)
and `jd_end` to the 2100-01-01 JD (~2488069.5). The total range is now
~73048 days. `ceil(73048 / 32) = 2284` segments. The first segment starts at
`jd_start` and runs a full 32 days (no truncation at the start — segments are
built from `jd_s = jd0 + si * 32`). The **last** segment is again the one at
risk: `2100-01-01` minus the last segment start may be less than 32 days.

The generator `fit_segment` already uses `jd_e = min(jd_s + seg_len, jd1)`,
so the generator side is safe. The evaluator uses `actual_len = min(seg_starts[si]
+ seg_len, jd_end) - seg_starts[si]` — `jd_end` is read from the `.npz`'s
`jd_end` key. **This is correct as long as the `.npz` stores the new `jd_end`
(2100 JD).** The risk is if someone resets `jd_end` in the write call to the
old 2050 value by copy-paste.

**Warning sign:**
`test_chiron_longitude_within_tolerance` for dates near 2100-01-01 fails with
a large error (> 0.01°). Or the generator's own validation gate prints
`max|Δλ| >= 0.01°` at the last segment.

**Prevention:**
In `gen_chiron_coeffs.py`, update the `jd0` and `jd1` computation from
`swe.julday(1950, 1, 1, 0.0)` to `swe.julday(1900, 1, 1, 0.0)` and
`swe.julday(2100, 1, 1, 0.0)`. The `write_npz` call passes `jd0` and `jd1`
explicitly — as long as these are updated, `jd_end` in the `.npz` is correct.
Do NOT hardcode the JD constants; derive them from `swe.julday`.

**Phase to address:** Chiron range extension phase.

---

### Pitfall 4-B: 1895-1896 perihelion region near the new lower bound

**What goes wrong:**
Chiron's perihelion was ~1895-1896. The 1900-1950 extension places the
perihelion region within the new data range. Near perihelion, Chiron moves
fastest and the ecliptic longitude changes most rapidly, making Chebyshev
approximation hardest. The Phase 24 spike validated `max|Δλ| = 0.000861°`
for 1950-2050 — the perihelion region was just outside that window. The 1900
extension may degrade accuracy near the first few segments.

The Phase 23 decision log locked `seg_len=32d, degree=10` for 1950-2050.
These parameters may not achieve < 0.01° near the 1895-1896 perihelion. The
generator's built-in validation gate will catch this — `max|Δλ| >= 0.01°` →
`sys.exit(1)`. But if the phase plan assumes the same parameters will work,
the generator will block the build and require parameter adjustment (shorter
`seg_len` or higher `degree` for the near-perihelion segments).

**Warning sign:**
Generator exits with `VALIDATION ÉCHOUÉE : max|Δλ|=0.xxxx° >= 0.01°` and
reports `pire JD : ~2414xxx.x` (in the 1895-1910 range).

**Prevention:**
Before committing to 1900-2100 as the target range, run a quick validation
spike using the existing generator with `jd0 = swe.julday(1900, 1, 1)` and
check if the < 0.01° gate passes. If it fails near 1895-1910, consider either
(a) a tighter first-segment range of ~1905-2100 to stay clear of the
perihelion, or (b) increasing `degree` to 12 for the first N segments. The
23-DECISION.md parameters are locked for 1950-2050 — a new decision log entry
is needed if parameters must change for the extended range.

**Phase to address:** Chiron range extension phase; may require a spike
sub-task before the main plan.

---

### Pitfall 4-C: Wheel size doubles, regression refs must be re-pinned, stale user caches

**What goes wrong:**
The current `ketu/data/chiron_coeffs.npz` is 290KB (confirmed by `ls -lh`).
For 200 years at `seg_len=32d`, `n_segs ≈ 2284` vs. current 1142 — roughly
2× the segments. `np.savez_compressed` will produce ~580KB. This is included
in the wheel (`ketu/data/*.npz` is in `package-data`). A 600KB data file in a
pure-NumPy library wheel is acceptable but should be documented in the release
notes.

The 7 pinned regression refs in `tests/ephemeris/test_chiron_regression.py`
span 1950-2050. With the extended range, new refs spanning 1900-2100 must be
added — covering at least one date in 1900-1950 and one in 2050-2100. The
existing 7 refs must still pass (backward compatibility of the evaluator for
dates already in the old range).

For users with stale `~/.ketu` cache files from ketu==1.3.0: the ephemeris
cache in `ketu/cache/ephemeris_cache.py` checks `data.shape[1] != BODY_COUNT`
(line 156) on load — it detects and recomputes if body count changes, but a
body count change did NOT occur here (still 14 bodies). The Chiron position
itself is recomputed from the in-package `.npz` on every `_load_chiron_data()`
call (with `lru_cache(maxsize=1)`, which resets on interpreter restart). There
is no disk persistence of Chiron's Chebyshev evaluation result. Stale caches
are therefore not a risk for Chiron-position accuracy, but they do contain
body positions that include Chiron computed from the old `.npz`. On ketu
upgrade, the new `.npz` is in the new wheel and `_load_chiron_data()` reads
it — the LRU cache is per-process and the new `.npz` is loaded on the first
call after the upgrade. No manual cache clearing needed.

**Warning sign:**
Re-pinned regression test file shows only 1950-2050 dates — missing coverage
of the newly valid 1900-1950 and 2050-2100 range.

**Prevention:**
Add at minimum 2 new ref entries to `test_chiron_regression.py`: one at
~1905-01-01 and one at ~2095-01-01. Run `python tools/gen_chiron_coeffs.py
--dump-refs` after extending the ref-JD list in the tool. Confirm wheel size
< 1MB in the release checklist.

**Phase to address:** Chiron range extension phase.

---

## Area 5 — Documentation / Gettext Pitfalls

### Pitfall 5-A: Changing English source strings orphans fr `.po` entries (fuzzy/obsolete)

**What goes wrong:**
The gettext flow uses `sphinx-intl`. The `docs/Makefile` provides `make
update-po` which runs `sphinx-build -b gettext` to regenerate POT files,
then `sphinx-intl update -p build/gettext -l fr` to merge. When an English
source string changes (e.g., the Orb table in `concepts.md` line 199 changes
"Pluto, Chiron | 4°" → "Pluto | 4°; Chiron | 4°"), sphinx-intl marks the
corresponding `.po` entry as fuzzy or obsolete. A fuzzy entry is NOT compiled
into the `.mo` file unless the translator explicitly removes the `#, fuzzy` flag
and confirms the translation. If the `.mo` files are compiled from stale or
fuzzy-flagged `.po` files, the French docs will show untranslated strings for
the changed sections.

**Warning sign:**
After `make update-po`, running `grep -r "#, fuzzy"
docs/locale/fr/LC_MESSAGES/` returns hits in `concepts.po`, `migration.po`, or
`relational_charts.po`. The French build (`make html-fr`) succeeds but affected
paragraphs fall back to English silently.

**Prevention:**
The gettext flow for this milestone must be:
1. `cd docs && make update-po` — regenerates POT, merges into `.po` files.
2. `grep -r "#, fuzzy" locale/fr/LC_MESSAGES/` — find all fuzzy entries.
3. Translate each fuzzy string, remove the `#, fuzzy` flag.
4. `make build-mo` — compile `.mo` files.
5. `make html-fr` — build and visually spot-check the changed sections.
This is the same flow executed for Phase 26.1 (Phase 26 note in project
memory: "17 .po/1405 msgs, DOC-13").

**Phase to address:** Documentation recentring phase (v1.4 doc phase).

---

### Pitfall 5-B: Removing EXTENDED from concepts.md tables while EXTENDED stays in code — doctest/numpydoc drift

**What goes wrong:**
`ketu/aspects/presets.py` has doctests in `aspects_for_harmonics` (lines
154-158). The module docstring references `EXTENDED` extensively. The public
`EXTENDED` constant is exported in `ketu/aspects/__init__.py`. If the doc
recentring removes EXTENDED from `concepts.md` tables but some `make doctest`
docstring example still says `EXTENDED` or implies "all 14 aspects are the
default," the CI `make doctest` gate (`56 doctests` per project memory) will
not break — but the narrative will contradict the code's own docstring.

More concretely: `ketu/aspects/presets.py:194` defines `EXTENDED` and its
docstring module says "Legacy v1.0 behaviour; all aspects including full-circle
minors." If `concepts.md` is rewritten to say "EXTENDED has been removed," a
user who imports `from ketu.aspects import EXTENDED` and it works will be
confused.

The task is "remove from concepts.md **tables**" — not remove from the API.
So the risk is a table removal that contradicts a reference in the very next
paragraph of concepts.md that still mentions `EXTENDED` in a code block.

**Warning sign:**
`grep -n "EXTENDED" docs/source/concepts.md` returns results after the table
removal — the code block at line 143-154 still shows `EXTENDED`. That block
must also be updated to mention it as "opt-in, not in default tables."

**Prevention:**
Do not surgically remove only the table rows. Audit every paragraph in
`concepts.md` that references H5/H9/H10 or `EXTENDED` and update the
narrative consistently: "EXTENDED (all 14 aspects including full-circle
harmonics H5/H9/H10) remains available in code but is no longer shown in the
default summary tables." The recentring goal is concepts.md leading with the
7-aspect TRADITIONAL default — make sure no paragraph below the tables
contradicts that framing.

**Phase to address:** Documentation recentring phase.

---

### Pitfall 5-C: numpydoc/interrogate BLOCKING gates on the new generator function

**What goes wrong:**
`pyproject.toml` has `[tool.interrogate] fail-under = 95` and
`[tool.numpydoc_validation] checks = ["all", ...]`. Any new public function
in `ketu/` with a missing or malformed numpydoc docstring will:
- Cause `interrogate` to fail if the function is undocumented (drops coverage
  below 95%).
- Cause `numpydoc validate` to report "PR01: Missing parameter description"
  or similar, which is a BLOCKING gate in CI per Phase 21.

The dynamic harmonic generator function (and any accompanying public API
like `generate_harmonic_aspects(h, jd, ...)`) must have full numpydoc
docstrings including `Parameters`, `Returns`, `Raises`, and `Examples` sections.

**Warning sign:**
CI fails at the numpydoc validation step with `SS05 / PR01 / RT01` errors
against the new generator function, or `interrogate` drops below 95%.

**Prevention:**
Write the numpydoc docstring **before** the function body (test-driven
documentation). Follow the pattern in `aspects_for_harmonics` in `presets.py`
(lines 113-183) as a template: full Parameters/Returns/Raises/Examples with
`>>>` doctests that exercise the boundary cases (h=1, h=even, h=odd, k/h
convention).

**Phase to address:** Dynamic harmonic generator phase.

---

### Pitfall 5-D: Migration and relational_charts.md default-aspect fixes may contradict concepts.md

**What goes wrong:**
`docs/source/migration.md:131` says "Without it [the `aspects` parameter],
behavior is unchanged (EXTENDED = all 14 aspects)." That is the v1.1-era
description — it was not updated to reflect the v1.3 default change to
TRADITIONAL. `docs/source/relational_charts.md:18` says
`aspects — aspect set spec (None uses the default classical set)` — also
stale (default is TRADITIONAL, not classical).

The v1.4 doc recentring must update these files. If only `concepts.md` is
edited, the cross-document inconsistency remains. A user reading
`migration.md` to understand what changed between versions will see conflicting
default descriptions.

**Warning sign:**
`grep -rn "default classical\|EXTENDED = all\|default.*14 aspects"
docs/source/` returns hits in migration.md or relational_charts.md after the
concepts.md update.

**Prevention:**
Run `grep -rn "EXTENDED\|classical.*default\|default.*classical" docs/source/`
as a mandatory pre-commit check when the doc phase is executed. Update ALL
occurrences to reflect TRADITIONAL (7 aspects) as the current default, with
a note that EXTENDED remains available.

**Phase to address:** Documentation recentring phase.

---

## Area 6 — Versioning / Release Pitfalls

### Pitfall 6-A: Push origin main AND the tag — not just the tag

**What goes wrong:**
ReadTheDocs follows `origin/main` for the `latest` docs build. PyPI's OIDC
workflow triggers on the Git tag. If only the tag is pushed (e.g. `git tag
v1.4.0 && git push origin v1.4.0`), PyPI publishes the new wheel but RTD's
`latest` docs remain frozen at the last `main` push — the updated
`concepts.md`, `migration.md`, `relational_charts.md` are invisible to
documentation users.

This exact mistake was recorded in project memory: "Pousser main, pas juste le
tag, à la release — PyPI suit le tag mais RTD suit origin/main."

**Warning sign:**
After the release, `ketu.readthedocs.io/en/latest/` still shows the v1.3 doc
content (e.g., the old Chiron orb in the Default Orbs table, or the old
migration defaults).

**Prevention:**
Release checklist must include:
1. `git push origin main` — before or after the tag, but required.
2. `git push origin v1.4.0` — triggers PyPI OIDC.
3. Check RTD build status at `readthedocs.org/projects/ketu/builds/` to
   confirm the `latest` build completed with the new SHA.

**Phase to address:** Release phase.

---

### Pitfall 6-B: Chiron orb change does NOT break the bodies positional contract with Kala

**What goes wrong (or rather, what does NOT go wrong, stated to prevent false alarm):**
Kala uses Ketu via a `KetuAdapter`. Project memory records that the 13→14
body axis change (Phase 24) was a breaking change that Kala needed to adapt.
Someone might worry that changing Chiron's orb also breaks Kala.

It does not. The `bodies` array shape and dtype are unchanged — `orb` is just
a `float32` field. The body axis is still 14 entries. Kala adapts to Chiron
position, not to its natal orb (which is only used internally by
`ketu.aspects`). However, Kala may pin aspect-detection results for specific
dates — if those results included or excluded Chiron aspects based on Chiron's
0° orb, Kala's pinned outputs would change.

**Warning sign:**
Kala regression tests fail because Chiron now participates in aspects it
previously did not, and Kala had pinned result counts or specific aspect lists.
This is a downstream breakage, not a ketu bug.

**Prevention:**
Document in the v1.4.0 changelog: "Chiron natal orb changed from 0° to 4°.
This affects aspect detection: Chiron now participates in aspects at distances
up to the coef-scaled orb. Downstream consumers that pin aspect-detection
results including Chiron pairs must be updated." Add a `CHANGELOG.md` entry
under a "Migration Notes" sub-section.

**Phase to address:** Release phase.

---

## Pitfall-to-Phase Mapping

| Pitfall | Area | Prevention Phase | Verification |
|---------|------|-----------------|--------------|
| 1-A: Dynamic path gated by `_VALID_HARMONICS` | Fingerprint | Dynamic harmonic generator | `test_aspects_byte_fingerprint` still passes; dynamic H7 returns result, not ValueError |
| 1-B: Accidental table mutation | Fingerprint | Dynamic harmonic generator | Both sha256 fingerprints still match constants in `test_ketu.py` |
| 1-C: Index-based cache key for dynamic aspects | Cache key | Dynamic harmonic generator | Code review: no new LRU keyed on `i_asp` without key-schema comment |
| 2-A: k=0 and mirror-angle duplicates | Harmonic math | Dynamic harmonic generator | Unit test: H4→[90°,180°], H6→[60°,120°,180°], H7→3 angles |
| 2-B: float32 vs float64 in angle match | Harmonic math | Dynamic harmonic generator | Unit test: separation exactly at computed angle is detected at orb=0.01° |
| 2-C: High-harmonic tiny orbs | Harmonic math | Dynamic harmonic generator | Docstring note + optional `orb_override`; no functional test needed |
| 3-A: Synastry group-assert docstring / missing Chiron-specific test | Chiron orb | Chiron orb change | New `test_synastry_orb_limit_chiron_nonzero_orb`; grep for stale docstrings |
| 3-B: CLI fixture regeneration | Chiron orb | Chiron orb change | Regenerate fixture; manual audit of each new Chiron aspect line |
| 3-C: Other pinned-count tests break | Chiron orb | Chiron orb change | `pytest -x` before fixture regeneration; diagnose each new failure |
| 4-A: Last-segment partial-length for new range | Range regen | Chiron range extension | Generator validation gate < 0.01°; check `pire JD` is not near 2100 boundary |
| 4-B: 1895-1896 perihelion near new lower bound | Range regen | Chiron range extension spike | Run generator; confirm gate passes for 1900-2100; spike sub-task if not |
| 4-C: Wheel size, re-pinned refs, stale caches | Range regen | Chiron range extension | Add 1900/2050-era refs to `test_chiron_regression.py`; wheel size < 1MB |
| 5-A: Fuzzy/obsolete fr `.po` entries | Doc/gettext | Doc recentring phase | `grep -r "#, fuzzy" docs/locale/fr/` returns 0 after `make update-po` + translate |
| 5-B: EXTENDED in code vs. doc table removal | Doc | Doc recentring phase | `grep -n "EXTENDED" docs/source/concepts.md` shows only "opt-in" narrative, no removed table |
| 5-C: numpydoc/interrogate gate on new function | Doc gates | Dynamic harmonic generator | CI `make doctest` and interrogate pass; numpydoc validate returns 0 errors |
| 5-D: migration.md / relational_charts.md stale defaults | Doc | Doc recentring phase | `grep -rn "EXTENDED\|classical.*default" docs/source/` returns 0 stale hits |
| 6-A: Push main not just tag | Release | Release phase | RTD `latest` build SHA matches release commit; docs show updated Chiron orb table |
| 6-B: Chiron orb breaks Kala aspect pins | Release | Release phase | CHANGELOG migration note; Kala adapter tests run post-release |

---

## "Looks Done But Isn't" Checklist

- [ ] **Dynamic generator:** `aspects_for_harmonics` is NOT called from the dynamic path — verified by code grep.
- [ ] **Dynamic generator:** Both sha256 fingerprint constants in `test_ketu.py` unchanged after the phase.
- [ ] **Chiron orb change:** `test_synastry_orb_limit_rahu_rahu_zero_orb`, `_ketu_ketu_`, `_lilith_lilith_` all still pass (these must stay 0.0).
- [ ] **Chiron orb change:** New `test_synastry_orb_limit_chiron_nonzero_orb` added and passes (expects 2.0).
- [ ] **CLI fixture:** `v1_1_reference_output.txt` regenerated; `test_degree_symbol_is_masculine_ordinal` still passes on the new fixture.
- [ ] **Chiron range:** `_CHIRON_REFS` in `test_chiron_regression.py` includes at least one date pre-1950 and one post-2050.
- [ ] **Chiron range:** Generator validation gate printed `max|Δλ| < 0.01°` for the full 1900-2100 range.
- [ ] **Gettext:** `grep -r "#, fuzzy" docs/locale/fr/LC_MESSAGES/` returns empty after translation and `make build-mo`.
- [ ] **Release:** `git log --oneline origin/main` shows the release commit; RTD `latest` reflects it.

---

*Pitfalls research for: ketu v1.4.0 feature set (dynamic harmonics, Chiron orb 0→4°, range 1900-2100, doc recentring)*
*Researched: 2026-06-02*
