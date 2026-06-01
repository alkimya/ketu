# Phase 26: Aspects Data-Driven + Dynamic Harmonics - Research

**Researched:** 2026-06-01
**Domain:** NumPy structured-array refactor of an existing aspect engine (data-driven table + harmonic-selection API + breaking default-set change)
**Confidence:** HIGH (the entire change surface is in-repo and was read line-by-line; the one MEDIUM item is exact minor-aspect glyph codepoints)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Aspect table shape**
- Extend the existing structured array in `ketu/core.py` (`core.aspects`) — do NOT switch to NamedTuple/dataclass. Stay NumPy-first. The table grows two new dtype fields; it does not change kind.
- Exactly the 5 roadmap fields: `name`, `angle`, `harmonic`, `coefficient`, `symbol`. `coefficient` == the current `coef` field (orb weight). No absolute orb field — effective orb stays derived (body orb × coefficient).
- New fields to add to the dtype: `harmonic` (`i4`) and `symbol` (a Unicode-capable string field, e.g. `U2`/`U4`).
- Table stays in `ketu/core.py` — enrich in place; zero import-chain rewiring. The iteration/detection logic may live in `ketu/aspects/`.

**Aspect symbols**
- Use standard astrological Unicode glyphs (☌ conjunction, ⚹ sextile, □ square, △ trine, ☍ opposition, plus minor-aspect glyphs).
- At planning: confirm the canonical glyph per aspect and check what `display.py` / `ketu/cli/formatters.py` already render.

**Harmonic-selection API**
- `aspects_for_harmonics([...])` returns a boolean mask — the same length-N `np.bool_` mask shape that `resolve_aspect_set` and the presets produce. Drop-in into the existing pipeline.
- Presets are redefined ON TOP of the harmonic table — single source of truth. Default = `aspects_for_harmonics([1, 2, 3, 6])`. `EXTENDED` keeps all aspects.
- Strict validation: only harmonics actually present in the table (1, 2, 3, 5, 6, 9, 10) are valid. `aspects_for_harmonics([7])` raises `ValueError`.
- Public surface: `aspects_for_harmonics` is a sister function to `resolve_aspect_set`, exported from `ketu/aspects/presets.py` (or package `__init__`), added to `__all__`.

**Default aspect set & coefficients**
- New default = the 7 half-circle aspects (H1/2/3/6): Conjunction (0°,H1), Semi-sextile (30°), Sextile (60°), Square (90°), Trine (120°), Quincunx (150°), Opposition (180°). These are exactly the existing `TRADITIONAL` preset's 7 rows.
- TWO-part default shift for UPGRADING: the *current* `resolve_aspect_set` default is `CLASSICAL` (5 aspects), not 7. So 1.3.0 both (a) adds Semi-sextile + Quincunx to the implicit default and (b) keeps H5/H9/H10 out. A caller with no `aspects=` now gets 7 instead of 5.
- Coefficients kept bit-for-bit identical for retained aspects — only structure, default set, and new columns change. No numeric recalibration.
- Opt-in path for minors: `EXTENDED` stays all-14, and `aspects_for_harmonics([5,9,10])` composes them. No new preset.

**Migration & public breaking change**
- Hard break, documented — no deprecation alias. UPGRADING shows restore recipe: `aspects='classical'` for old 5, `aspects='extended'` for all 14.
- Kala: generic UPGRADING note; adapts post-release (NOT a blocker).
- CHANGELOG + UPGRADING: dedicated "Aspect engine changes (1.3.0)" section with before/after of default (5→7), restore recipe, new API, minors-opt-in note, code examples. CHANGELOG BREAKING entry under [1.3.0].
- concepts.md (Harmonic Theory): full pedagogical explanation. Calibrate against existing concepts.md to avoid duplication.
- api.md updated for new function + table fields; fr gettext regenerated (msgstr may stay English-fallback).

### Claude's Discretion
- CLI naming-collision: `--harmonics` flag already exists, means "aspect *set* spec". Decision: API-only this phase; do NOT wire a harmonic-number CLI surface. Capture CLI as deferred.
- Exact `symbol` dtype width, precise glyph per aspect, where the iteration/detection loop physically lives in `ketu/aspects/`.
- Whether `TRADITIONAL` is reused as the default constant or a freshly-named harmonic-derived constant.

### Deferred Ideas (OUT OF SCOPE)
- CLI wiring of a harmonic-number surface (the `--harmonics` flag collision).
- An absolute-orb field on the aspect table.
- Coefficient recalibration.
</user_constraints>

---

## Summary

This is a low-risk, high-precision refactor. The current aspect engine is **already substantially data-driven**: every consumer reads `core.aspects` by **field name** (`["angle"]`, `["coef"]`, `["name"]`), never by positional tuple-unpacking, and the detection loops in `ketu/aspects/calculator.py` already `enumerate`/iterate the table rather than hardcoding per-aspect branches. The one genuinely hardcoded special-case is the conjunction branch (`if i_asp == 0`) which uses raw distance instead of `angle ± orb` — that is a legitimate geometric special-case (0° has no negative side), not per-aspect scatter, and it appears in four places (calculator ×2, composite, synastry).

The harmonic-mapping "tension" the CONTEXT flags is **already resolved in the codebase**: `docs/source/concepts.md:70-126` documents the exact convention — **half-circle harmonics divide 180°** (`180°/n`) and **full-circle harmonics divide 360°** (`360°/n`). Under that rule the asserted mapping H1={0,180}, H2={90}, H3={60,120}, H6={30,150}, H5/H9/H10={minors} falls out cleanly, and `[1,2,3,6]` yields exactly the 7 half-circle aspects. The existing `concepts.md` summary table (lines 116-124) and the coefficient table (lines 168-183) **already encode this mapping with the harmonic numbers** — the new `harmonic` column simply transcribes them. (Note one transcription nuance below: concepts.md assigns sextile 60° to **H3**, not H6; the CONTEXT body text says H6 for 60° in one place but its own "intended mapping" line lists 60°∈H6 — this is the single thing to freeze. See the Harmonic Mapping section: **the codebase convention puts 60° and 120° in H3**, which is the mapping that makes `[1,2,3,6]→7` correct.)

**Primary recommendation:** Add two columns (`harmonic` i4, `symbol` U4) to `core.aspects` in place, transcribing the harmonic numbers and glyphs already documented in `concepts.md`. Add `aspects_for_harmonics(list[int]) -> np.bool_[14]` to `ketu/aspects/presets.py` mirroring `resolve_aspect_set`'s validation contract. Redefine `CLASSICAL`/`TRADITIONAL`/`EXTENDED` and the resolver default on top of the harmonic table. Flip the resolver default from `CLASSICAL` (5) to the 7 half-circle set. Update the ~6 contract tests that pin dtype names / default=5 / fingerprint, document the breaking change, and regenerate gettext.

---

## Current State Ground-Truth

### The `core.aspects` table — VERBATIM (`ketu/core.py:87-108`)

```python
# Structured array of major aspects (harmonics 1, 2, 3, 6, 9, and 10)
# Fields: name, angle (degrees), coefficient for orb calculation
aspects = np.array(
    [
        # Classical aspects (Harmonics 1, 2, 3, 6)
        ("Conjunction", 0, 1),
        ("Semi-sextile", 30, 1 / 6),
        ("Decile", 36, 1 / 10),  # H10 - Semi-quintile
        ("Novile", 40, 1 / 9),  # H9 - Nonagone
        ("Sextile", 60, 1 / 3),
        ("Quintile", 72, 1 / 5),  # H5 (sub-harmonic of H10)
        ("Binovile", 80, 2 / 9),  # H9
        ("Square", 90, 1 / 2),
        ("Tredecile", 108, 3 / 10),  # H10 - Tri-decile
        ("Trine", 120, 2 / 3),
        ("Biquintile", 144, 2 / 5),  # H5 (sub-harmonic of H10)
        ("Quincunx", 150, 5 / 6),
        ("Quadrinovile", 160, 4 / 9),  # H9
        ("Opposition", 180, 1),
    ],
    dtype=[("name", "S16"), ("angle", "f4"), ("coef", "f4")],
)
```

**Field name is `coef` (NOT `coefficient`).** CONTEXT's "coefficient == the current coef field" is correct; the locked decision says the *logical* field is `coefficient` but the *implementation* keeps `coef`. **DECISION FOR PLANNER:** do NOT rename `coef` → `coefficient`. A rename would break `synastry/orbs.py:150`, `synastry/api.py:289`, `composite/api.py:314`, `calculator.py:51`, and the dtype-names contract test, for zero functional gain. The roadmap's 5-field tuple `(name, angle, harmonic, coefficient, symbol)` is a *conceptual* contract satisfied by `(name, angle, coef, harmonic, symbol)`. (Confirm framing with user if they want the literal rename — but the CONTEXT "no import-chain rewiring" decision argues against it.)

**Total: 14 rows** (`len(aspects) == 14`, asserted in 3 tests + the `presets.py:44` module-load assert). Row order is canonical and append-only.

### Per-row table (the planner's enrichment target)

| idx | name | angle | coef | **harmonic (to add)** | **symbol (to add)** |
|-----|------|-------|------|----------------------|---------------------|
| 0 | Conjunction | 0 | 1 | **1** | ☌ U+260C |
| 1 | Semi-sextile | 30 | 1/6 | **6** | ⚺ U+26BA |
| 2 | Decile | 36 | 1/10 | **10** | ⚺/blank (see Glyph Table) |
| 3 | Novile | 40 | 1/9 | **9** | blank (see Glyph Table) |
| 4 | Sextile | 60 | 1/3 | **3** | ⚹ U+26B9 |
| 5 | Quintile | 72 | 1/5 | **5** | Q / ⚼ U+26BC |
| 6 | Binovile | 80 | 2/9 | **9** | blank |
| 7 | Square | 90 | 1/2 | **2** | □ U+25A1 |
| 8 | Tredecile | 108 | 3/10 | **10** | blank |
| 9 | Trine | 120 | 2/3 | **3** | △ U+25B3 |
| 10 | Biquintile | 144 | 2/5 | **5** | bQ / blank |
| 11 | Quincunx | 150 | 5/6 | **6** | ⚻ U+26BB |
| 12 | Quadrinovile | 160 | 4/9 | **9** | blank |
| 13 | Opposition | 180 | 1 | **1** | ☍ U+260D |

Coefficients confirmed identical to `tests/test_ketu.py:60-75` `EXPECTED_ASPECT_COEFS`. **These must NOT change** (byte-fingerprint test + per-row test pin them).

### Consumer map — every site that reads `core.aspects` (with file:line)

All access is **by field name**, so adding two columns is binary-safe at every site. No positional tuple-unpacking of an aspect *row* exists anywhere.

| File:line | What it reads | Pattern | Breaks on +2 cols? |
|-----------|---------------|---------|--------------------|
| `ketu/core.py:107` | dtype def | source of truth | This is the edit site |
| `ketu/aspects/calculator.py:20` | import `aspects as _CORE_ASPECTS` | named import | No |
| `ketu/aspects/calculator.py:51` | `_CORE_ASPECTS["coef"]` | field | No |
| `ketu/aspects/calculator.py:76` | `enumerate(_CORE_ASPECTS["angle"])` | field iterate | No |
| `ketu/aspects/calculator.py:181-182` | `["angle"][mask]`, `["coef"][mask]` | field+mask | No |
| `ketu/aspects/calculator.py:302-303` | `["angle"][mask]`, `["coef"][mask]` | field+mask | No |
| `ketu/aspects/calculator.py:410,416,490,517` | `["angle"]`, `["name"]` | field | No |
| `ketu/aspects/core.py:17,58,60,66,68` | `aspects["name"]`, `aspects["angle"]` | field | No |
| `ketu/aspects/windows.py:20,49,298,299` | `["name"]`, `["angle"]` | field | No |
| `ketu/aspects/transits.py:29,60,350,351,578,579` | `["name"]`, `["angle"]` | field | No |
| `ketu/aspects/timelines.py:26,36,476,480,485,487,513,514` | `["name"]`, `["angle"]` | field | No |
| `ketu/aspects/presets.py:40,44-47` | import + `len(_ASPECTS)==14` assert + `_ASPECTS["name"]` | named + len | **len assert + index arrays** (see below) |
| `ketu/calculations.py:14` | `from .core import ... aspects ...` | named import | No |
| `ketu/display.py:17,78,82` | `["name"][i_asp]` (renders aspect NAME, not glyph) | field | No |
| `ketu/composite/api.py:75,314` | `["coef"]`, `["angle"]` | field | No |
| `ketu/synastry/api.py:57,288,289,296` | `["angle"]`, `["coef"]` | field | No |
| `ketu/synastry/orbs.py:35,150` | `["coef"][asp]` | field | No |
| `ketu/cli/formatters.py:15,49,50` | `["name"][mask]`, `["angle"][mask]` (renders NAME + angle°, NO glyph) | field+mask | No |
| `ketu/cli/introspection.py:12,49,50` | `["name"][mask]`, `["angle"][mask]` (renders NAME + angle°, NO glyph) | field+mask | No |
| `ketu/cli/harmonics_spec.py:36` | imports `resolve_aspect_set` only | indirect | No |
| `ketu/__init__.py:61` | `from ketu.core import ... aspects ...` | named re-export | No |

**The only structural couplings to length-14 / index arrays:**
- `ketu/aspects/presets.py:44-47` — `assert len(_ASPECTS) == 14`. Stays valid (we add columns, not rows).
- `ketu/aspects/presets.py:54-60` — `_CLASSICAL_INDICES`, `_TRADITIONAL_INDICES`, `_EXTENDED_INDICES` hardcode row indices. **These are the redefine-on-top-of-harmonic-table target** (see Locked Decisions → Targets).

### The preset system (`ketu/aspects/presets.py`)

- **Constants** (lines 87-91): `CLASSICAL`, `TRADITIONAL`, `EXTENDED` are **frozen length-14 `np.bool_` masks** (built by `_indices_to_mask`, `writeable=False`).
  - `CLASSICAL` = indices `[0,4,7,9,13]` (5 majors).
  - `TRADITIONAL` = indices `[0,1,4,7,9,11,13]` (7 — CLASSICAL + Semi-sextile + Quincunx).
  - `EXTENDED` = `np.arange(14)` (all 14).
- **Resolver** (lines 104-224): `resolve_aspect_set(spec, default=CLASSICAL) -> np.bool_[14]`.
  - Accepts: `None`→default; `str` preset name (case-insensitive, keys `classical/traditional/extended`); `Sequence[str]` aspect names (exact bytes); `Sequence[int]` indices `[0,14)`; `np.ndarray[bool]` shape `(14,)` passthrough; `np.ndarray[int]` indices.
  - **CURRENT DEFAULT = `CLASSICAL` (5)** — CONFIRMED at line 106 `default: ... = CLASSICAL`, and pinned by `tests/test_aspect_presets.py:130-133` and `:489-503`. This is what flips to 7.
  - **ValueError contract** (the template `aspects_for_harmonics` should mirror): unknown preset name (lists valid presets), unknown aspect name (lists all 14 decoded names), out-of-range index (`out of range`), wrong-length bool mask (`shape`), invalid item type (`invalid aspect spec item`), bool-in-sequence rejected.
  - `__all__` (line 227): `CLASSICAL, TRADITIONAL, EXTENDED, AspectSetSpec, resolve_aspect_set`. **`aspects_for_harmonics` gets appended here AND in `ketu/aspects/__init__.py:59-65,97-103`.**

### Detection / orb logic (`ketu/aspects/calculator.py`)

- `get_orb(b1,b2,asp)` (lines 33-52): `(orbs[b1]+orbs[b2])/2 * coef[asp]`. Reads `bodies["orb"]` and `_CORE_ASPECTS["coef"]` by field. **Effective orb is derived (body orb × coef)** — matches the locked "no absolute orb field" decision.
- `get_aspect` (lines 55-82): single-pair scanner, `for i_asp, aspect in enumerate(_CORE_ASPECTS["angle"])` — **already iterates the table**. Conjunction special-case `if i_asp == 0 and dist <= orb` (raw distance, no negative side). Out of ASP-07 scope (no `aspects=` param), filtered post-hoc.
- `calculate_aspects` / `_vectorized` / `_batch` (lines 85-386): all call `resolve_aspect_set(aspects)` ONCE, then iterate `selected_indices` with parallel `selected_angles`/`selected_coefs` slices. **Already fully data-driven over the table.** The conjunction `if i_asp == 0` branch (lines 225, 363) is the only per-aspect special-case — geometric, not scatter.
- `find_aspects_between_dates` (lines 453-522): resolves mask, passes `selected_angles` to `find_all_aspects`, maps angle→canonical index via `np.where(_CORE_ASPECTS["angle"] == ...)`.

**Assessment:** The "no per-aspect hardcoding scattered across modules" success criterion is **~90% already met**. The genuine remaining "scatter" is the **conjunction special-case duplicated in 4 sites** (calculator.py:225 & :363, composite/api.py:~330, synastry/api.py:~300). The planner may optionally consolidate, but per the locked "structure + default + new columns only; retained numeric output byte-stable" decision, **leave the conjunction branches alone** unless the planner adds a `harmonic`/`symbol`-driven helper that provably preserves output. The data-driven win this phase delivers is: the *table itself* now carries `harmonic` (enabling `aspects_for_harmonics`) and `symbol` (enabling glyph rendering), and presets/default derive from the table rather than hardcoded index literals.

---

## Locked Decisions → Concrete Targets

| Decision | Concrete change | File:line |
|----------|-----------------|-----------|
| Add `harmonic` (i4) + `symbol` (U4) columns | Edit the `np.array(...)` literal: append `harmonic, symbol` to each of the 14 rows; extend dtype to `[("name","S16"),("angle","f4"),("coef","f4"),("harmonic","i4"),("symbol","U4")]` | `ketu/core.py:89-108` |
| Keep table in core.py; no import rewiring | All consumers already import `from ketu.core import aspects` by name — no edits needed | n/a (verified above) |
| `coefficient` == existing `coef` | Do NOT rename `coef`. Document the conceptual mapping in CHANGELOG/api.md | n/a |
| Update core.py module docstring | The `aspects` docstring block (lines 28-38) lists only name/angle/coef — add harmonic + symbol field descriptions | `ketu/core.py:28-38` |
| `aspects_for_harmonics([...]) -> np.bool_[14]` | New function mirroring `resolve_aspect_set` validation; builds mask via `np.isin(_ASPECTS["harmonic"], valid_list)` | `ketu/aspects/presets.py` (new fn ~after line 224) |
| Strict validation: valid harmonics = {1,2,3,5,6,9,10} | Compute `_VALID_HARMONICS = set(int(h) for h in _ASPECTS["harmonic"])` from the table (data-driven). Raise `ValueError` for any input harmonic not in set (e.g. `[7]`) | `presets.py` |
| Presets redefined on top of harmonic table | Replace hardcoded `_CLASSICAL_INDICES`/`_TRADITIONAL_INDICES` literals with harmonic-derived masks where clean. `TRADITIONAL = aspects_for_harmonics([1,2,3,6])` (the 7 half-circle). `EXTENDED = aspects_for_harmonics([1,2,3,5,6,9,10])` (all 14) or keep `np.arange(14)`. **`CLASSICAL` (5 majors) is NOT a clean harmonic set** — it drops Semi-sextile (H6) and Quincunx (H6) but keeps Sextile (H3). Keep `CLASSICAL` as an explicit index/name list (it is a curated Ptolemaic-majors subset, not a pure harmonic selection). | `presets.py:54-91` |
| Default shift 5→7 (half-circle) | Change `resolve_aspect_set` signature default from `CLASSICAL` to the 7 half-circle constant (the redefined `TRADITIONAL`, or a new `DEFAULT`/`HALF_CIRCLE` constant — Discretion). | `presets.py:106` |
| `TRADITIONAL` reuse vs new constant (Discretion) | **Recommend:** reuse `TRADITIONAL` as the default value but ALSO export a semantically-named alias `aspects_for_harmonics([1,2,3,6])` result. TRADITIONAL already == the 7 half-circle set (indices `[0,1,4,7,9,11,13]`), so it is exactly correct. Reusing it avoids inventing a 4th preset name. | `presets.py` |
| Coefficients byte-stable | Do not touch any coef value; byte-fingerprint test guards this | `core.py` |
| Minors opt-in | `aspects_for_harmonics([5,9,10])` composes the 7 minors; `EXTENDED` keeps all 14. No new preset. | `presets.py` |
| Export new fn | Append `"aspects_for_harmonics"` to `presets.py:__all__` AND `ketu/aspects/__init__.py` import block + `__all__` | `presets.py:227`, `aspects/__init__.py:59-65,97-103` |
| Glyph rendering hookup (optional this phase) | display.py / formatters.py / introspection.py currently render NAME only. The `symbol` column is added to the table but **CONTEXT does not require wiring glyph output** — the decision says "check what they render" and the table must "match them". Since nothing renders glyphs today, the table is the new source of truth; rendering glyphs is NOT required by the success criteria. **Recommend: add the column, do NOT change rendering this phase** (CLI surface is deferred). | n/a (table only) |

---

## Harmonic Mapping (THEORY — verify & freeze)

### The rule the table must encode

**The codebase already commits to this convention** (`docs/source/concepts.md:70-126`, HIGH confidence — it is the project's own documented theory):

> A **harmonic** divides a *base angle* into *n* equal parts. Ketu uses **two** base angles:
> - **Half-circle harmonics** divide **180°** (`180°/n`): harmonics **1, 2, 3, 6**.
> - **Full-circle harmonics** divide the whole **360°** (`360°/n`): harmonics **5, 9, 10**.

This dual-base rule is what resolves the "tension" the CONTEXT flagged. The naive `360/angle` framing fails (gives 90°→H4, 150°→H2.4); the **half-circle base** framing is the project's chosen convention and is internally consistent.

### Per-aspect harmonic (FROZEN — transcribe these into the `harmonic` column)

| idx | aspect | angle | division | harmonic | half/full | in `[1,2,3,6]`? |
|-----|--------|-------|----------|----------|-----------|-----------------|
| 0 | Conjunction | 0° | 180°·0/1 | **1** | half | ✅ |
| 13 | Opposition | 180° | 180°/1 | **1** | half | ✅ |
| 7 | Square | 90° | 180°/2 | **2** | half | ✅ |
| 4 | Sextile | 60° | 180°/3 (= 1/3 of semicircle) | **3** | half | ✅ |
| 9 | Trine | 120° | 2·180°/3 | **3** | half | ✅ |
| 1 | Semi-sextile | 30° | 180°/6 | **6** | half | ✅ |
| 11 | Quincunx | 150° | 5·180°/6 | **6** | half | ✅ |
| 5 | Quintile | 72° | 360°/5 | **5** | full | ❌ |
| 10 | Biquintile | 144° | 2·360°/5 | **5** | full | ❌ |
| 3 | Novile | 40° | 360°/9 | **9** | full | ❌ |
| 6 | Binovile | 80° | 2·360°/9 | **9** | full | ❌ |
| 12 | Quadrinovile | 160° | 4·360°/9 | **9** | full | ❌ |
| 2 | Decile | 36° | 360°/10 | **10** | full | ❌ |
| 8 | Tredecile | 108° | 3·360°/10 | **10** | full | ❌ |

**Selecting `[1,2,3,6]` yields exactly indices `{0,1,4,7,9,11,13}` = the 7 half-circle aspects.** This is bit-identical to the current `_TRADITIONAL_INDICES = [0,1,4,7,9,11,13]` (`presets.py:57-59`). The default-shift is therefore mechanically: `default = TRADITIONAL`.

### CRITICAL DISCREPANCY TO RESOLVE — sextile/trine harmonic

⚠️ **The CONTEXT body text is internally inconsistent on 60°/120°.** The "Specific Ideas" block says two contradictory things:
- "The intended mapping is H1={0°,180°}, H2={90°}, H3={120°}, H6={30°,60°,150°}" — this puts **60° (sextile) in H6** and **120° (trine) in H3**.
- But it also asks to "CONFIRM the H3/H6 attribution".

**The codebase convention (concepts.md:88-96, 120) puts BOTH 60° and 120° in H3** (`Harmonic 3 (180°/3 = 60°): Sextile (60°), Trine (120°)`), and **only 30° and 150° in H6** (`Harmonic 6: Semi-sextile (30°), Quincunx (150°)`).

**Both mappings produce the same `[1,2,3,6]→7` result** (because both H3 and H6 are selected). So the default set is robust either way. **BUT the `harmonic` column is now public** (it drives `aspects_for_harmonics`), so the value matters: with the **codebase mapping**, `aspects_for_harmonics([3])` returns `{Sextile, Trine}` and `aspects_for_harmonics([6])` returns `{Semi-sextile, Quincunx}`; with the **CONTEXT-body mapping**, `[3]`→`{Trine}` and `[6]`→`{Sextile, Semi-sextile, Quincunx}`.

**RECOMMENDATION (HIGH confidence): adopt the codebase mapping — Sextile=H3, Trine=H3, Semi-sextile=H6, Quincunx=H6.** Rationale: (1) it is already documented and shipped in `concepts.md`; (2) it is the standard harmonic-astrology convention (John Addey / harmonic theory: the trine and sextile are both expressions of the **3rd harmonic** — sextile = 60° = 360/6 only by full-circle, but as a *half-circle* division 60° = 180/3; the 3rd harmonic governs the "triplicity/grand-trine" family which includes the sextile); (3) it makes `aspects_for_harmonics([3])` return the harmonically-coherent trine+sextile pair, which is the pedagogically correct grouping. The CONTEXT's parenthetical "60° (sextile): theoretically H6 (360/6)" is the naive full-circle reading the project explicitly rejected in favor of the half-circle base.

**ACTION FOR PLANNER:** Freeze the column to the codebase mapping (the table above). Surface this discrepancy to the user in the plan's decision log so they can veto if they truly want sextile=H6. The 7-aspect default is unaffected either way.

**Source for harmonic convention:** Project's own `docs/source/concepts.md:70-126` (HIGH — authoritative for *this* project). Cross-checked against standard harmonic astrology (Addey, *Harmonics in Astrology*): the half-circle/whole-circle dual-base and trine+sextile both being 3rd-harmonic expressions is consistent with mainstream harmonic theory (MEDIUM — general-knowledge, not freshly web-verified; the project doc is the binding source).

---

## Glyph Table

### What renders glyphs today: NOTHING

- `ketu/display.py:78-82` renders `aspect_name` (the decoded string), padded `{aspect_name:12}`. **No glyph.**
- `ketu/cli/formatters.py:49-51` renders `"{name} {angle}°"`. **No glyph.**
- `ketu/cli/introspection.py:49-54` renders `"{name} {angle}°"`. **No glyph.**
- Repo-wide grep for `glyph`/`symbol` in `ketu/**.py` finds only unrelated mentions (`houses/_ecliptic.py:146` "symbol" = Python symbol; `synastry/core.py:48` mentions "aspect glyph at the correct degree" in a docstring describing a downstream consumer's use, not Ketu rendering).

**Implication:** There is **no existing name→glyph map to match**. The `symbol` column becomes the canonical source of truth. The only place glyphs currently appear is the **documentation** (`concepts.md:168-183` table), which the new column should match.

### Glyphs already in `concepts.md:168-183` (codepoints verified via `ord()`)

| aspect | glyph | codepoint | len |
|--------|-------|-----------|-----|
| Conjunction | ☌ | U+260C | 1 |
| Semi-sextile | ⚺ | U+26BA | 1 |
| Sextile | ⚹ | U+26B9 | 1 |
| Square | □ | U+25A1 | 1 |
| Trine | △ | U+25B3 | 1 |
| Quincunx | ⚻ | U+26BB | 1 |
| Opposition | ☍ | U+260D | 1 |
| Decile, Novile, Quintile, Binovile, Tredecile, Biquintile, Quadrinovile | *(blank in doc)* | — | 0 |

### Proposed canonical glyph per aspect (all 14)

The 7 major/half-circle glyphs are settled (match concepts.md). For the 7 minors, concepts.md leaves them blank. Options:
1. **Leave minors blank** (`""`) — matches concepts.md exactly; zero ambiguity; the column is honest about "no standard single glyph in our doc".
2. **Fill from Unicode astrology block** — Quintile ⚼ U+26BC exists; biquintile/noviles/deciles lack clean single-codepoint glyphs (the Unicode L2/16-174 proposal added many but font support is poor).

**RECOMMENDATION (MEDIUM confidence on minors):** Fill the 7 majors with the concepts.md glyphs (settled). For minors, **use a short ASCII label or leave blank** — recommend **blank `""`** for the 5 truly-unsupported ones (Decile, Novile, Binovile, Tredecile, Quadrinovile) and `⚼` U+26BC for Quintile (the one with stable Unicode/font support). Biquintile has no widely-supported single glyph → blank. This keeps the column faithful to what concepts.md already commits to and avoids shipping glyphs that render as tofu. **Confirm minor glyphs with the user at planning** — they may prefer all-blank-minors for consistency.

### `symbol` dtype width

- All 7 major glyphs are **single BMP codepoints** (verified: `len(g) == 1` for each).
- A NumPy `U2` field would hold any single glyph fine, but `U4` gives headroom for (a) a future 2-char ASCII label like `"Q"`/`"bQ"` if the user chooses labels over Unicode, (b) variation selectors (e.g. `U+FE0E`), (c) any multi-codepoint minor glyph.
- **NumPy silently truncates** strings longer than the width — a `U2` column assigned a 3-char value drops chars with no error. This is the documented pitfall.
- **RECOMMENDATION: `U4`.** Costs 14×4×4 = 224 bytes total; eliminates truncation risk; matches the CONTEXT's "e.g. U2/U4" with the safer choice.

---

## Test & Gate Impact

### Tests that pin the CURRENT contract and MUST be updated

| File:line | What it asserts | Required change |
|-----------|-----------------|-----------------|
| `tests/test_ketu.py:124-129` `test_aspects_dtype_names` | `dtype.names == ("name","angle","coef")` | **Update to** `("name","angle","coef","harmonic","symbol")` |
| `tests/test_ketu.py:150-160` `test_aspects_byte_fingerprint` | sha256 of `name+angle+coef` tobytes == `c5bd...b359` | **Likely UNCHANGED** — it hashes only the 3 *existing* columns (lines 153-155), which are byte-stable. Verify it does not iterate `dtype.names`. If it stays scoped to the 3 columns, the fingerprint is preserved (this is the design intent of the append-only invariant). **Recommend extending** it to also hash `harmonic`+`symbol` and pinning a new fingerprint for full coverage. |
| `tests/test_ketu.py:25-75` `EXPECTED_ASPECT_*` + `test_aspects_structure` | per-row name/angle/coef | **UNCHANGED** (name/angle/coef byte-stable). Optionally add `EXPECTED_ASPECT_HARMONICS` + `EXPECTED_ASPECT_SYMBOLS` and per-row checks. |
| `tests/test_ketu.py:117-122` `test_aspects_length` | `len == 14` | **UNCHANGED** (still 14 rows) |
| `tests/test_aspect_presets.py:58-69` `test_classical_mask_shape_and_sum` | CLASSICAL sum==5, indices `[0,4,7,9,13]` | **UNCHANGED** (CLASSICAL stays 5 majors) |
| `tests/test_aspect_presets.py:72-82` `test_traditional_mask_shape_and_sum` | TRADITIONAL sum==7, indices `[0,1,4,7,9,11,13]` | **UNCHANGED** (still the 7 half-circle) — but verify the redefinition (harmonic-derived) produces the identical mask |
| `tests/test_aspect_presets.py:130-133` `test_resolve_none_returns_classical` | `resolve_aspect_set(None) == CLASSICAL` | **FLIP** → default now returns the 7 half-circle (TRADITIONAL). Rename test to `test_resolve_none_returns_default_half_circle` and assert `== TRADITIONAL` (or new DEFAULT constant). |
| `tests/test_aspect_presets.py:489-503` `test_default_equals_classical` | `calculate_aspects(jd)` == `aspects=CLASSICAL` | **FLIP** → default now equals `aspects=TRADITIONAL` (7). Rename + reassert. |
| `tests/test_aspect_presets.py:442-457` `test_find_aspects_between_dates_default_equals_classical` | default == `aspects=CLASSICAL` | **FLIP** → default == TRADITIONAL |
| `ketu/aspects/calculator.py:100-105,156-162,275-280,474-478` docstrings | "`None` resolves to `CLASSICAL` (5 majors)" | **Update docstrings** to "resolves to the 7 half-circle default" (×4 functions). numpydoc gate will not catch wrong prose, but accuracy matters. |
| `ketu/charts/api.py:131-135,364` docstrings | "`None` resolves to CLASSICAL" / "default: EXTENDED" | **Update** — note charts/api.py:364 says default EXTENDED which is ALREADY stale (it resolves via calculator → CLASSICAL today); fix to the new default. Verify whether charts override the default. |

### Tests asserting the *result* dtype (UNAFFECTED — different array)

- `tests/test_aspects_vectorization.py:67` and `tests/test_ketu.py:339`: assert `(body1, body2, i_asp, orb)` — this is the **output** structured array, not `core.aspects`. No change.

### CLI tests pinning default=5 (likely UNAFFECTED — CLI has its own default)

- `tests/cli/test_parser.py:117` `args.harmonics.sum() == 5`, `tests/cli/test_harmonics_spec.py:20,44,48,67,142` sum==5, `tests/cli/test_resolved_header.py:35-36` "5 aspects": these test the **CLI `--harmonics` default**, which is independent of the library default and is **explicitly deferred** (CONTEXT: "API-only this phase; do NOT wire a harmonic-number CLI surface"). **VERIFY** whether the CLI default flows from `resolve_aspect_set(None)` (would shift to 7) or is pinned to a literal `"classical"` in the parser. If the CLI bare default flows from the library default, the planner must decide: either (a) pin the CLI to `"classical"` explicitly to keep CLI byte-stable, or (b) let the CLI default shift to 7 too (then update these CLI tests). **This is a decision point to surface — the CLI byte-stable escape hatch (`test_v1_1_reference_byte_stable.py`) may be affected.** Check `ketu/cli/parser.py` default for `--harmonics`.

### Coverage / quality gates (BLOCKING — all must stay green)

- **`fail_under = 100`** (`pyproject.toml:101`), zero pragma. Every new branch in `aspects_for_harmonics` (each `ValueError` path, the happy path) MUST be tested. The validation has ≥4 branches: empty list, valid harmonic, invalid harmonic (e.g. 7), non-int item. Mirror the `test_aspect_presets.py` error-path test density.
- **interrogate ≥95%** (`pyproject.toml:123-124`): `aspects_for_harmonics` needs a numpydoc docstring (Parameters/Returns/Raises/Examples).
- **numpydoc validate** (`pyproject.toml:139-148`): `checks = ["all", -EX01, -SA01, -ES01]`. The new function needs a full numpydoc block (Summary, Parameters, Returns, Raises). Note `override_SS05` already whitelists `^Aspect$` — if the planner names anything `Aspect*`, SS05 (summary-starts-with-infinitive) is pre-excused.
- **make doctest** (56 doctests, ELLIPSIS+NORMALIZE_WHITESPACE): if `aspects_for_harmonics` has a doctest, it counts. **Watch:** any doctest that prints `core.aspects` (e.g. `core.py:47-58` docstring examples) — adding columns changes the repr. The current doctests access `aspects['angle'][...]` by field (line 53-55) so they are **safe**; verify none print the whole array.
- **mypy --strict** (`pyproject.toml`): `aspects_for_harmonics` needs full type hints (`Sequence[int] -> npt.NDArray[np.bool_]`).

### Net test count

Currently **1373 tests / 100% coverage** (STATE.md:57). Expect +~8-12 new tests (aspects_for_harmonics happy + error paths, harmonic-column per-row, symbol-column per-row) minus 0 (the flipped tests are renamed/reasserted, not removed).

---

## Docs / i18n Steps

### Files to edit (English source)

| File | Section | Change |
|------|---------|--------|
| `docs/source/concepts.md:70-126` | Harmonic Theory | Already correct. Add a short note that the **default set is now the 7 half-circle aspects** and minors are opt-in. The dual-base rule (lines 72-77) is the pedagogical anchor — reuse, don't duplicate. |
| `docs/source/concepts.md:128-140` | Configurable Aspect Sets (v1.1) | Update: default changed to half-circle/TRADITIONAL; add `aspects_for_harmonics` example; note CLASSICAL=5 is now opt-in for "old default". |
| `docs/source/concepts.md:168-183` | Aspect Types table | Already has Symbol + Harmonic columns matching the new `core.aspects` columns. Verify the 7-major glyphs match the `symbol` column exactly; fill/blank minors consistently. |
| `docs/source/api.md:160-227` | Aspects section | Fix **stale** `None → EXTENDED` (line 211) and `EXTENDED (default)` (line 183) — these are ALREADY wrong (current default is CLASSICAL); set to new 7 half-circle default. Document `aspects_for_harmonics`. Update preset table to note default. |
| `docs/source/api.md:356-364` | compute_chart | Fix stale "default: EXTENDED" (line 364). |
| `CHANGELOG.md:10` | `[Unreleased]` → cut a `[1.3.0]` | Add **BREAKING** entry: default aspect set 5→7 (half-circle); new `aspects_for_harmonics`; `harmonic`+`symbol` columns; minors opt-in. Before/after + restore recipe. |
| `UPGRADING.md:5` (newest-first) | New `## v1.2 -> v1.3` section | Restore recipe (`aspects='classical'`→old 5, `aspects='extended'`→all 14); new API; minors-opt-in; generic Kala note (Kala adapts post-release, not a blocker). |

### gettext regeneration commands (EXACT — from `docs/Makefile`)

The Makefile points `VENVBIN ?= ../venv/bin` so `make` works without activation, but **the CONTEXT/state log flags broken venv shebangs**. Use the `python3 -m` invocation workaround when the shebang is stale:

```bash
cd /home/loc/workspace/ketu/docs
# 1. Extract translatable strings → build/gettext/*.pot
make gettext          # = sphinx-build -b gettext source build/gettext
# 2. Merge into French PO files (locale/fr/LC_MESSAGES/*.po)
make update-po        # = sphinx-intl update -p build/gettext -l fr
# 3. (optional) compile + build FR HTML to verify
make html-fr          # = build-mo (sphinx-intl build) + sphinx-build -b html -D language=fr
```

**If the venv shebangs are broken** (Phase 25 workaround), bypass the Makefile's `$(VENVBIN)/sphinx-build` by overriding the binaries to module form:

```bash
cd /home/loc/workspace/ketu/docs
make gettext   SPHINXBUILD="python3 -m sphinx"
make update-po SPHINXBUILD="python3 -m sphinx" SPHINXINTL="python3 -m sphinx_intl"
```

(`sphinx-intl`'s module entry is `sphinx_intl` — verify with `python3 -m sphinx_intl --help` first.) The PO file to expect changes in is `docs/locale/fr/LC_MESSAGES/concepts.po` (296 msgids today) and `api.po`/`changelog.po`. **CONTEXT permits msgstr to stay English-fallback** — new msgids may remain untranslated (matches the MEMORY note "doc fr in English-fallback after Phase 25; translate before 1.3.0 release"). Do NOT run `migrate_translations.py` — it's a one-time legacy migration tool (`docs/fr/` → PO) and expects `cwd=docs`, not the per-phase update path.

---

## Risks & Pitfalls

### Pitfall 1: NumPy silently truncates U-string columns (HIGH stakes)
**What:** Assigning a string longer than the `symbol` field width drops characters with no error. **Avoid:** use `U4` (recommended); add a test that round-trips each glyph and asserts `len(core.aspects["symbol"][i]) == len(expected_glyph)`. **Warning sign:** a glyph rendering as a partial/wrong char.

### Pitfall 2: Default-shift ripples to the CLI byte-stable escape hatch (HIGH stakes)
**What:** If the CLI `--harmonics` default flows from `resolve_aspect_set(None)`, flipping the library default 5→7 silently changes CLI output, breaking `tests/cli/test_v1_1_reference_byte_stable.py` (the locked v1.0/v1.1 byte-identical contract). **Avoid:** read `ketu/cli/parser.py` `--harmonics` default FIRST; if it inherits the library default, pin it explicitly to `"classical"` (or accept the shift and update the byte-stable reference — a decision to surface). **Warning sign:** `test_resolved_header.py` "5 aspects" failing unexpectedly.

### Pitfall 3: The harmonic mapping for 60°/120° (HIGHEST correctness stakes — see Theory section)
**What:** The CONTEXT body text contradicts the codebase on whether sextile is H3 or H6. Freezing the wrong value makes `aspects_for_harmonics([3])` / `([6])` return surprising sets. **Avoid:** adopt the codebase/concepts.md mapping (Sextile=H3, Trine=H3, Semi-sextile=H6, Quincunx=H6); surface the discrepancy in the plan decision log. The `[1,2,3,6]→7` default is robust either way, so the *default* is safe; only the *per-harmonic introspection* differs.

### Pitfall 4: byte-fingerprint test false sense of safety
**What:** `test_aspects_byte_fingerprint` only hashes name+angle+coef, so it will NOT detect a wrong harmonic/symbol value. **Avoid:** add explicit per-row `EXPECTED_ASPECT_HARMONICS`/`EXPECTED_ASPECT_SYMBOLS` assertions (mirrors the existing per-row name/angle/coef tests at `test_ketu.py:131-148`) to reach 100% coverage and pin the new columns.

### Pitfall 5: `coef` vs `coefficient` rename temptation
**What:** The roadmap's 5-field tuple lists `coefficient`; a literal rename breaks 5 consumer sites + the dtype-names contract test for zero benefit and violates "no import-chain rewiring". **Avoid:** keep `coef`; document the conceptual==logical mapping in api.md/CHANGELOG.

### Pitfall 6: Doctest repr drift
**What:** Any doctest that prints the whole `core.aspects` array (vs a field slice) will fail when columns are added. **Avoid:** grep doctests for full-array prints; the current `core.py:47-58` doctests use field access (`aspects['angle'][...]`) and are safe — confirm no other module prints the array. The `make doctest` gate (56 doctests) is blocking.

### Pitfall 7: CLASSICAL is not a pure harmonic set
**What:** Trying to define `CLASSICAL = aspects_for_harmonics([...])` is impossible — CLASSICAL (Ptolemaic 5) keeps Sextile (H3) but drops Semi-sextile (H6) and Quincunx (H6) while TRADITIONAL adds them; no harmonic list selects exactly `{0,4,7,9,13}`. **Avoid:** keep CLASSICAL as a curated index/name list; only TRADITIONAL (`[1,2,3,6]`) and EXTENDED (`[1,2,3,5,6,9,10]`) are pure-harmonic. This is correct and expected — document CLASSICAL as "Ptolemaic majors, a curated subset".

### Pitfall 8: Frozen-mask contract on the new function
**What:** `resolve_aspect_set` and presets return `writeable=False` masks (`_indices_to_mask`); tests assert mutation raises ValueError. **Avoid:** `aspects_for_harmonics` must also return a frozen mask via the same `_indices_to_mask` helper (or set `flags.writeable=False`) for consistency, and add a frozen-mutation test.

---

## CONTEXT Claims Verified

| # | CONTEXT claim | Verdict | Evidence |
|---|---------------|---------|----------|
| 1 | `core.aspects` is a structured array in `ketu/core.py` | **TRUE** | `core.py:89-108` |
| 2 | The orb-weight field is `coef` (CONTEXT: "coefficient == current coef field") | **TRUE** | `core.py:107` `("coef","f4")`; CONTEXT correctly maps `coefficient`→`coef` |
| 3 | Table has 14 aspects; TRADITIONAL=7, CLASSICAL=5 | **TRUE** | 14 rows `core.py:90-105`; `_CLASSICAL_INDICES`=5 `presets.py:54-56`; `_TRADITIONAL_INDICES`=7 `presets.py:57-59` |
| 4 | Current `resolve_aspect_set` default is CLASSICAL (5), not 7 | **TRUE** | `presets.py:106` `default: ... = CLASSICAL`; pinned by `test_aspect_presets.py:130-133, 489-503` |
| 5 | TRADITIONAL = exactly the 7 half-circle aspects (0/30/60/90/120/150/180) | **TRUE** | `_TRADITIONAL_INDICES=[0,1,4,7,9,11,13]` = those 7 angles |
| 6 | `EXTENDED` = all 14 | **TRUE** | `_EXTENDED_INDICES = np.arange(14)` `presets.py:60` |
| 7 | Presets are length-14 frozen `np.bool_` masks | **TRUE** | `_indices_to_mask` sets `writeable=False` `presets.py:79-82`; tests `test_aspect_presets.py:93-108` |
| 8 | `resolve_aspect_set` returns a length-14 mask; strict ValueError validation | **TRUE** | `presets.py:104-224`; error tests `test_aspect_presets.py:243-318` |
| 9 | `--harmonics` CLI flag exists, means "aspect set spec", rejects bare integers as ambiguous | **TRUE** | `harmonics_spec.py:103-114` rejects bare int with "ambiguous" message; `:74-101` accepts preset/comma-list |
| 10 | `display.py` / `formatters.py` render glyphs | **FALSE** | `display.py:78-82` renders aspect **name** string; `formatters.py:49-51` and `introspection.py:49-54` render **name + angle°**. **No glyph rendering anywhere in the codebase.** The `symbol` column will be a new source of truth, not a match to existing rendering. |
| 11 | Detection logic iterates the table (vs hardcodes per-aspect) | **TRUE (mostly)** | `get_aspect` `calculator.py:76` enumerates; `calculate_aspects*` iterate `selected_indices`. Only per-aspect special-case is the conjunction `if i_asp==0` branch (geometric, in 4 sites). ~90% data-driven already. |
| 12 | Effective orb = body orb × coef (no absolute orb field) | **TRUE** | `get_orb` `calculator.py:51-52`; matches "no absolute orb field" decision |
| 13 | Intended harmonic mapping H1={0,180}, H2={90}, H3={120}, H6={30,60,150} | **NUANCED / partially FALSE** | The codebase (`concepts.md:88-96,120`) puts **60° (sextile) in H3**, not H6, and **only 30°+150° in H6**. CONTEXT's "H3={120}" omits the sextile and its "H6={...,60,...}" is the naive full-circle reading the project rejected. **Both produce `[1,2,3,6]→7` identically**, so the default is safe; but the per-harmonic column must follow the codebase convention. See Theory section. |
| 14 | Naive 360/angle gives 90°→H4, 150°→H2.4 (non-integer) — tension exists | **TRUE** | Arithmetic confirms; resolved by the half-circle dual-base convention documented in `concepts.md:70-77` |
| 15 | Minor angles: quintile 72, biquintile 144, novile 40, binovile 80, quadrinovile 160, decile 36, tredecile 108 | **TRUE** | All match `core.py:90-105` exactly |
| 16 | concepts.md Harmonic Theory section exists | **TRUE** | `concepts.md:70-126`; already documents the dual-base rule + full per-harmonic table |
| 17 | api.md aspect/preset section exists | **TRUE** | `api.md:160-227`; BUT contains **stale** `None → EXTENDED` (line 211) and `EXTENDED (default)` (lines 183, 364) — already wrong today (real default is CLASSICAL). Must be fixed. |
| 18 | gettext pipeline: docs/locale/, docs/Makefile, docs/migrate_translations.py | **TRUE** | All present; commands `make gettext` / `make update-po` / `make html-fr` (`Makefile:48-91`); `python3 -m` override needed if venv shebangs broken |
| 19 | Cache .npz / CHART_DTYPE serializes core.aspects (dtype-widening risk) | **FALSE (no coupling)** | grep `ketu/cache/` finds no `aspects` reference; no dtype embeds `core.aspects.dtype`. Adding columns cannot break the cache or any chart dtype. **Risk does not apply.** |
| 20 | Full suite 1373 tests / 100% coverage | **TRUE** | `STATE.md:57` |
| 21 | 100% coverage (fail_under=100, zero pragma), interrogate≥95%, numpydoc validate, make doctest (56), mypy --strict — all BLOCKING | **TRUE** | `pyproject.toml:101,123,139`; doctest count `STATE.md:57` |
| 22 | Tests assert aspect count / dtype / default-set size / preset contents that need updating | **TRUE** | `test_ketu.py:117-160`, `test_aspect_presets.py:58-89,130-133,489-503` — enumerated in Test & Gate Impact |
| 23 | A body-count-freeze ratchet pattern exists (`test_body_count_frozen_at_*`) | **TRUE (analogous, for bodies not aspects)** | `tests/charts/test_dtype.py:228` `_BODY_COUNT==14`; the aspect equivalent is the `len==14` + dtype-names + fingerprint trio in `test_ketu.py`. No separate `test_aspect_count_frozen` file — the freeze lives in `test_ketu.py:117-160`. |
| 24 | No positional tuple-unpacking of aspect rows that would break on +2 fields | **TRUE** | Every consumer uses field access (`["name"]`/`["angle"]`/`["coef"]`); no `name, angle, coef = row` anywhere. Verified across all 21 consumer sites. |

---

## Open Questions

1. **CLI default flow (Pitfall 2)** — Does `ketu/cli/parser.py`'s `--harmonics` default inherit `resolve_aspect_set(None)` or pin `"classical"` literally?
   - What we know: CLI tests pin sum==5 (`test_parser.py:117`, `test_harmonics_spec.py`). The library default flips to 7.
   - What's unclear: whether the CLI bare default is wired to the library default.
   - Recommendation: planner reads `parser.py` default in task 1; decide pin-to-classical (preserve CLI byte-stability) vs shift-CLI-too (update CLI tests + byte-stable reference). The CONTEXT defers CLI *harmonic-number* surface but is silent on the CLI *default-set* shift — surface to user.

2. **Sextile harmonic value (Pitfall 3 / Theory discrepancy)** — H3 (codebase) vs H6 (CONTEXT body text).
   - What we know: both yield `[1,2,3,6]→7`; codebase + standard harmonic theory favor H3.
   - Recommendation: freeze H3 per concepts.md; surface in plan decision log for user veto.

3. **Minor-aspect glyphs (MEDIUM confidence)** — fill with Unicode (poor font support) vs leave blank vs ASCII labels.
   - Recommendation: 7 majors = concepts.md glyphs (settled); minors blank (faithful to concepts.md) except optionally Quintile ⚼ U+26BC. Confirm with user.

4. **`coef`→`coefficient` literal rename** — roadmap tuple says `coefficient`; codebase says `coef`.
   - Recommendation: keep `coef` (CONTEXT "no import-chain rewiring" + 5 consumer sites). Confirm the conceptual mapping satisfies the roadmap.

---

## Sources

### Primary (HIGH confidence)
- `ketu/core.py:87-108` — verbatim `core.aspects` dtype + 14 rows + coef values
- `ketu/aspects/presets.py:54-224` — preset constants, `resolve_aspect_set` signature/validation, current default=CLASSICAL
- `ketu/aspects/calculator.py:33-522` — `get_orb`, `get_aspect`, the 4 multi-aspect APIs and their table iteration
- `docs/source/concepts.md:70-183` — the project's authoritative harmonic-theory convention (dual-base 180°/360°) + per-aspect harmonic + glyph table
- `tests/test_ketu.py:25-160`, `tests/test_aspect_presets.py:58-503` — the contract tests pinning dtype/length/default/presets
- `docs/Makefile:48-95` — exact gettext/update-po/html-fr targets
- `pyproject.toml:92-148` — coverage (fail_under=100), interrogate, numpydoc, mypy gates
- Repo-wide grep of all 21 `core.aspects` consumer sites — confirmed all field-access, no positional unpacking, no cache/dtype coupling

### Secondary (MEDIUM confidence)
- [Unicode L2/16-174 Extra Aspect Symbols for Astrology (David Faulks)](https://www.unicode.org/L2/L2016/16174r-astrology-aspects.pdf) — codepoints for aspect glyphs (verified the 7 major glyphs in concepts.md are single BMP codepoints via `ord()`)
- [U+26B9 SEXTILE – Unicode/codepoints.net](https://codepoints.net/U+26B9) — confirms ⚹ U+26B9
- [Astronomical symbols — Wikipedia](https://en.wikipedia.org/wiki/Astronomical_symbols) — aspect glyph cross-reference

### Knowledge (project-internal, binding)
- Standard harmonic astrology (Addey, *Harmonics in Astrology*): trine+sextile as 3rd-harmonic expressions, half-circle vs whole-circle base — consistent with `concepts.md` (the project doc is the authoritative source; general harmonic theory is corroborating, MEDIUM).

## Metadata

**Confidence breakdown:**
- Current-state ground-truth (dtype, rows, consumers, presets, detection): **HIGH** — every line read in-repo
- Harmonic mapping: **HIGH** for the rule and the `[1,2,3,6]→7` result; the sextile-H3-vs-H6 discrepancy is flagged and resolved against the codebase
- Glyphs (7 majors): **HIGH** (codepoint-verified, match concepts.md). Minors: **MEDIUM** (no standard single glyph; recommend blank)
- Test/gate impact: **HIGH** — enumerated file:line for every affected test and gate
- Docs/i18n commands: **HIGH** (read from Makefile); venv-shebang workaround **MEDIUM** (per CONTEXT/state-log, not re-verified this session)

**Research date:** 2026-06-01
**Valid until:** 30 days (stable in-repo surface; the only external dependency is Unicode glyph conventions, which are immutable)

---

## RESEARCH COMPLETE

**Phase:** 26 - Aspects Data-Driven + Dynamic Harmonics
**Confidence:** HIGH

### Key Findings
- The engine is **already ~90% data-driven**: all 21 consumers read `core.aspects` by field name, none by positional unpacking, and detection loops already iterate the table. Adding `harmonic`+`symbol` columns is binary-safe everywhere; the cache/CHART dtype have **zero coupling** to the aspect dtype (CONTEXT's dtype-widening risk does not apply).
- The harmonic-mapping "tension" is **already resolved in `concepts.md:70-126`**: half-circle harmonics divide 180° (H1,2,3,6), full-circle divide 360° (H5,9,10). `[1,2,3,6]` → exactly the 7 half-circle aspects = the existing `TRADITIONAL` mask `{0,1,4,7,9,11,13}`. The default-shift is mechanically `default = TRADITIONAL`.
- **Discrepancy flagged:** CONTEXT body text says sextile 60°∈H6, but the codebase + standard theory put it in **H3** (trine+sextile both 3rd-harmonic). Both give the same 7-aspect default; freeze H3 per concepts.md and surface for user veto.
- **CONTEXT claim #10 is FALSE:** nothing renders glyphs today (display/formatters/introspection render aspect *names*). The `symbol` column becomes a new source of truth, not a match — so glyph *rendering* is NOT required by the success criteria (table-only this phase). Field is `coef`, not `coefficient` — recommend NOT renaming.
- **Two stale docs already wrong today:** `api.md:183,211,364` claim default=EXTENDED (real default is CLASSICAL). Fix as part of the doc update.

### File Created
`/home/loc/workspace/ketu/.planning/phases/26-aspects-data-driven/26-RESEARCH.md`

### Confidence Assessment
| Area | Level | Reason |
|------|-------|--------|
| Current state ground-truth | HIGH | Read line-by-line; all 21 consumers mapped with file:line |
| Harmonic mapping | HIGH | Codebase convention documented + `[1,2,3,6]→7` proven; sextile discrepancy flagged/resolved |
| Glyphs (majors) | HIGH | Codepoint-verified; minors MEDIUM (recommend blank) |
| Test/gate impact | HIGH | Every affected test enumerated file:line |
| Pitfalls | HIGH | Each tied to concrete code evidence |

### Open Questions
1. CLI `--harmonics` default flow (inherits library default? → byte-stable escape-hatch risk) — planner reads `parser.py` first.
2. Sextile harmonic = H3 (codebase) vs H6 (CONTEXT text) — freeze H3, surface for veto.
3. Minor-aspect glyphs: blank vs Unicode — recommend blank.
4. `coef`→`coefficient` literal rename — recommend keep `coef`.

### Ready for Planning
Research complete. Planner can write byte-accurate, file-specific PLAN.md files.
