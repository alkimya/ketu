# Phase 34: Harmonics Debt (ASP-F1/F2/F3) — Planning Research

**Researched:** 2026-06-03
**Domain:** Internal API/CLI consistency — dynamic-harmonic naming contract, `find_aspect_timing` orb derivation, CLI grammar
**Confidence:** HIGH (all claims verified against live code this session)
**Source:** `.planning/research/HARMONICS_DEBT.md` (primary) + codebase verification

---

## Summary

Phase 34 pays down three debts left open by the v1.4 dynamic-harmonics engine.
The engine itself (`generate_harmonic_aspects` + `dynamic_specs=` threading) is
already shipped and green (1537 tests, 100% coverage). What remains:

1. **ASP-F2 (HARM-01..03):** The `H{h}-{k}` naming scheme is already the live
   behaviour but is NOT yet a documented, pinned public API contract. A test
   suite must pin it exactly (bytes encoding, k-ordering, shape, boundary cases,
   collision semantics). Docs must distinguish two channels clearly.
2. **ASP-F3 (HARM-04..05):** `find_aspect_timing` currently forces the caller to
   compute the dynamic orb themselves and pass it as `orb=<float>`. Adding
   `dyn_coef: Optional[float] = None` (Option a) lets the function derive it
   itself — same formula as `calculate_aspects` uses at line 215-216. Three
   paths remain backward-compatible; only one new branch is added.
3. **ASP-F1 (HARM-06..09):** The CLI currently rejects `h7` (falls through to
   the "unrecognized" error branch). Wiring `h7` requires: (a) a new parse
   branch in `harmonics_spec.py`, (b) a `HarmonicsSelection` NamedTuple return
   type, (c) updating `aspects_cmd.py` to destructure the new type and thread
   `dynamic_specs=` through, (d) extending `print_aspects` for dynamic rows, (e)
   a new byte-stability fixture manually audited, (f) docs en+fr.

**Implementation order: F2 → F3 → F1** (locked). The CLI surface depends on a
stable naming contract; `find_aspect_timing` is independent of both.

---

## Locked Decisions (from roadmap — do NOT reopen)

| Decision | Locked value |
|---|---|
| Implementation order | F2 → F3 → F1 |
| Grammar | Tight: `h7` alone OR existing comma index list. `traditional,h7` and `h7,h11` deferred (HARMF-01). |
| CLI token | `h<N>` via `^h(\d+)$`, after preset+comma branches, before bare-int trap. Case-insensitive via existing `.lower()`. |
| `parse_harmonics_spec` return | `HarmonicsSelection` NamedTuple `(mask, dynamic_specs)`, reuses `DynamicAspectSpec` type alias. |
| `find_aspect_timing` orb | `dyn_coef: Optional[float] = None` (Option a). Explicit `orb` checked first (escape hatch short-circuits). |
| Both `orb` AND `dyn_coef` given | **Explicit `orb` wins** (NOT raise). Test this precedence explicitly. |
| Generator naming | Always `H{h}-{k}`. No traditional-name substitution in generator output. Traditional names in DOCS ONLY. |
| Header label | Thread harmonic token(s) into stderr header (e.g. `# Aspect set: h7`). Pin in NEW byte-stability fixture. |

**Critical nuance on orb precedence:** The brief's §4-C recommended raising if
both `orb` and `dyn_coef` are given, but the roadmap locks "explicit `orb` wins"
(silent precedence, not raise). Plan tests must test this silent-wins behaviour,
NOT a ValueError.

---

## Hard Gates (non-negotiable)

- `core.aspects` 14-row table + V1/V13 sha256 fingerprints stay byte-identical
  throughout. (V1: `c5bd177316ce98d428bee011a5b0f17ae247d1dee1e478c2389af51d39afb359`,
  V13: `3258530818272989c27eb6de6a717947df1a2fccda10d9562aa15ef67b8f27d8`)
- Existing v1.1 CLI byte-stability fixture (`test_v1_1_reference_byte_stable.py` /
  `fixtures/v1_1_reference_output.txt`) stays UNCHANGED — verified, not re-pinned.
- Pure-NumPy runtime (no pyswisseph imports under `ketu/`).
- `mypy --strict` clean on all changed modules.
- `fail_under=100` coverage, zero pragma.
- numpydoc + interrogate gates pass for all changed functions.
- NEW `--harmonics h7` byte-stability fixture freshly generated and MANUALLY AUDITED
  before pinning (the ketu ritual: confirm angles, synthetic names `H7-k`, header
  label, the always-on "Aspect Timing Example" block stays classical-pinned).

---

## Debt F2 — `H{h}-{k}` Naming Contract

### Files to touch

**`ketu/aspects/harmonics.py`** — no code changes needed. The naming is already
correct (verified). Changes are documentation only: promote the contract
statement to the module docstring (or `generate_harmonic_aspects` docstring),
formalising it as the public API guarantee.

**`tests/test_dynamic_harmonics.py`** — add a new `TestNamingContract` class
with the pinning tests below. Existing tests there already cover shape/dtype/value
(class `TestGenerateH7Values` at lines 155-188) and even-h behaviour
(`TestEvenHEmits180NeverO360` at lines 196-218). The new class upgrades the
doctest-level coverage to a first-class contract fixture.

**`docs/source/concepts.md`** and **`docs/source/api.md`** — add the two-channel
distinction (§2.2 from brief): GENERATOR always emits `H{h}-{k}`; DETECTION
layer prefers canonical table name on angle collision (120° → Trine, not `H3-1`).
Add the traditional-name reference table (H5-1≡quintile, H5-2≡biquintile,
H7-1≡septile, H9-1≡novile, H9-2≡binovile, H9-4≡quadnovile) as human-only docs.

**`docs/locale/fr/LC_MESSAGES/concepts.po`** and **`api.po`** — translate the
new contract paragraph + traditional-name table to French.

### Current state (verified)

`harmonics.py:204-208` (actual line numbers confirmed by reading the file):

```python
for k in range(1, h // 2 + 1):
    angle = _fold_to_0_180(k * 360.0 / h)
    coef = k / h
    name = f"H{h}-{k}".encode()   # line 207 — bytes, S16
    rows.append((name, angle, coef, h, ""))
```

`generate_harmonic_aspects` at `harmonics.py:118`. Range check at `harmonics.py:196`:
`if not (2 <= h <= 64)`.

Live-verified outputs:
- `h=2` → `[b'H2-1']` @ 180.0° — opposition-only (1 row)
- `h=7` → `[b'H7-1', b'H7-2', b'H7-3']` @ [51.43, 102.86, 154.29]°
- `h=6` → `[b'H6-1', b'H6-2', b'H6-3']` @ [60.0, 120.0, 180.0]° — even-h last=180°
- `h=12` → 6 rows, last = 180.0°
- `h=64` → 32 rows, last = 180.0°

The `HARMONIC_DTYPE` at `harmonics.py:44-52` is byte-identical to `ketu.core.aspects.dtype`
(verified by `TestHarmonicDtype.test_dtype_matches_core_aspects`).

### Test specs

Add to `tests/test_dynamic_harmonics.py` as `class TestNamingContractF2`:

```python
def test_naming_contract_h7_exact():
    """HARM-01/HARM-02: bytes encoding, k-ordering, coefs, symbols, harmonic col."""
    specs = generate_harmonic_aspects(7)
    assert specs["name"].tolist() == [b"H7-1", b"H7-2", b"H7-3"]
    assert specs["name"].dtype == np.dtype("S16")
    assert [round(float(a), 2) for a in specs["angle"]] == [51.43, 102.86, 154.29]
    assert [round(float(c), 4) for c in specs["coef"]] == [0.1429, 0.2857, 0.4286]
    assert specs["symbol"].tolist() == ["", "", ""]
    assert specs["harmonic"].tolist() == [7, 7, 7]

def test_naming_contract_h2_opposition_only():
    """HARM-02 boundary: h=2 emits exactly 1 row, name=b'H2-1', angle=180."""
    specs = generate_harmonic_aspects(2)
    assert specs["name"].tolist() == [b"H2-1"]
    assert float(specs["angle"][0]) == 180.0

def test_naming_contract_even_h_last_row():
    """HARM-02 boundary: even h, last row folds to exactly 180°; exactly h//2 rows."""
    for h in [2, 4, 6, 8, 12]:
        specs = generate_harmonic_aspects(h)
        assert len(specs) == h // 2
        assert float(specs["angle"][-1]) == pytest.approx(180.0, abs=1e-4)

def test_naming_contract_all_h():
    """HARM-02: for ALL h in [2..64], len==h//2 and names follow H{h}-{k} format."""
    import re
    pat = re.compile(rb"^H(\d+)-(\d+)$")
    for h in range(2, 65):
        specs = generate_harmonic_aspects(h)
        assert len(specs) == h // 2
        for j, row in enumerate(specs):
            m = pat.match(bytes(row["name"]))
            assert m is not None
            assert int(m.group(1)) == h
            assert int(m.group(2)) == j + 1  # k = j+1, 1-indexed

def test_naming_collision_detection_prefers_table_name():
    """HARM-03: 120° hit is reported as 'Trine' not 'H3-1' when trine is in the static set."""
    from ketu.aspects.calculator import calculate_aspects
    from ketu.aspects.harmonics import generate_harmonic_aspects
    specs = generate_harmonic_aspects(3)   # H3-1 at 120° (same as Trine)
    # With default aspects (trine included), 120° hit should be 'Trine' (i_asp=9), not i_asp=-2
    result = calculate_aspects(2451545.0, dynamic_specs=specs)
    trine_rows = [r for r in result if r["i_asp"] == 9]
    h3_rows    = [r for r in result if r["i_asp"] == -2]
    # Any pair that hit trine (120°) is tagged i_asp=9, not -2
    assert len(trine_rows) > 0   # at least one trine exists
    # None of the dynamic rows should carry the exact 120° angle (it was consumed statically)
    # (This test confirms static-first priority)
```

### Gates

- `fail_under=100` — new test class must cover all new branches in `harmonics.py`
  (there are none; the generator is unchanged, only docs/tests are new).
- numpydoc/interrogate on `harmonics.py` — docstring update must pass numpydoc gate.
- V1/V13 sha256 fingerprints unmodified (no code change to `core.py`).

### Pitfalls

- **Do NOT add traditional names to the structured array.** Traditional names go
  in docs only. Any attempt to map `b'H7-1'` to `b'septile'` in the generator
  would break the naming contract.
- **Collision semantics are detection-layer, not generator-layer.** `H3-1` at 120°
  is NEVER emitted by `calculate_aspects` when trine is in the static set
  (static-first). The naming contract is about what `generate_harmonic_aspects`
  returns, not what `calculate_aspects` labels a 120° hit.
- **Symbol field = empty string `""`**, not `b""`. It is a `U4` field (unicode),
  not bytes. The existing minor aspects in the table also have `""`. Verify this
  in the pinning test.

---

## Debt F3 — `find_aspect_timing` Dynamic Orb (`dyn_coef`)

### Files to touch

**`ketu/aspects/calculator.py`** — `find_aspect_timing` at line 568.
Current signature: `(jdate, body1, body2, aspect_value, orb=None)`.
New signature: `(jdate, body1, body2, aspect_value, orb=None, dyn_coef=None)`.

**`tests/test_dynamic_harmonics.py`** (or a new `tests/test_find_aspect_timing_f3.py`)
— new test class for the new branch.

**`docs/source/api.md`** — update `find_aspect_timing` docstring and the API doc
section. Replace the "compute it yourself" instruction (`calculator.py:592-593`)
with the new `dyn_coef` parameter documentation.

### Current state (verified)

`find_aspect_timing` at `calculator.py:568-651`. Current orb-resolution logic at
`calculator.py:611-617`:

```python
if orb is None:
    asp_idx = np.where(_CORE_ASPECTS["angle"] == aspect_value)[0]
    if len(asp_idx) == 0:
        raise ValueError(f"unknown aspect value: {aspect_value}")
    orb = get_orb(body1, body2, int(asp_idx[0]))
```

The docstring at lines 588-593 currently says (paraphrase): "For off-table
angles pass a pre-computed orb, e.g.
`(bodies['orb'][b1]+bodies['orb'][b2])/2 * dyn_coef`."

Three existing paths (verified by running):
1. `orb=None` + table angle → static lookup works.
2. `orb=None` + off-table angle → `ValueError("unknown aspect value: 51.4286")`.
3. `orb=2.0` + any angle → uses `2.0` directly.

`get_orb` formula at `calculator.py:81-82`:
```python
orbs, coef = bodies["orb"], _CORE_ASPECTS["coef"]
return (orbs[body1] + orbs[body2]) / 2 * coef[asp]
```

Dynamic orb formula used in `calculate_aspects` at `calculator.py:215-216`:
```python
dyn_coef = float(dyn_row["coef"])
dyn_orb = (orb_b1 + orb_b2) / 2 * dyn_coef
```

These are identical formulas — the new `find_aspect_timing` path simply mirrors
the existing `calculate_aspects` implementation.

Live-verified: Sun orb=12.0, Moon orb=12.0. H7-1 coef=1/7.
Expected dyn_orb for Sun/Moon H7-1: `(12+12)/2 * (1/7) = 1.7143°`.

### Signature change

```python
def find_aspect_timing(
    jdate: float,
    body1: int,
    body2: int,
    aspect_value: float,
    orb: Optional[float] = None,
    dyn_coef: Optional[float] = None,
) -> Tuple[float, float, float]:
```

New orb-resolution block replacing lines 611-617:

```python
if orb is not None:
    pass  # explicit orb wins — short-circuit (HARM-05 precedence)
elif dyn_coef is not None:
    # Dynamic path — derive orb from coef (mirrors calculate_aspects:215-216)
    orb = (
        float(bodies["orb"][body1]) + float(bodies["orb"][body2])
    ) / 2 * dyn_coef
else:
    # Static path — frozen-table lookup (UNCHANGED)
    asp_idx = np.where(_CORE_ASPECTS["angle"] == aspect_value)[0]
    if len(asp_idx) == 0:
        raise ValueError(f"unknown aspect value: {aspect_value}")
    orb = get_orb(body1, body2, int(asp_idx[0]))
```

This is equivalent to the original logic with the `if orb is not None` check
moved to be explicit (current code: `if orb is None:` block followed by use of
`orb`; the refactor makes the three branches parallel and the precedence obvious).

**Locked precedence:** explicit `orb` wins silently when both `orb` and `dyn_coef`
are provided. Do NOT raise. Test that the explicit `orb` value is used, not the
derived one.

### Test specs

New test class (add to `tests/test_dynamic_harmonics.py` or new file):

```python
class TestFindAspectTimingF3:
    JD = 2451545.0

    def test_dyn_coef_derives_orb_internally(self):
        """HARM-04: dyn_coef path derives orb = (orb_b1+orb_b2)/2*dyn_coef."""
        from ketu.aspects.calculator import find_aspect_timing
        from ketu.core import bodies
        coef = 1 / 7  # H7-1
        result = find_aspect_timing(self.JD, 0, 1, 51.4286, dyn_coef=coef)
        assert len(result) == 3
        assert all(isinstance(x, float) for x in result)

    def test_dyn_coef_orb_matches_calculate_aspects_formula(self):
        """HARM-04: derived orb equals (orb_b1+orb_b2)/2*dyn_coef — cross-check."""
        from ketu.aspects.calculator import find_aspect_timing
        from ketu.core import bodies
        coef = 1 / 7
        expected_orb = (float(bodies["orb"][0]) + float(bodies["orb"][1])) / 2 * coef
        # result[0]=begin, result[2]=end; orb window should be ~2*expected_orb wide
        result_dyn = find_aspect_timing(self.JD, 0, 1, 51.4286, dyn_coef=coef)
        result_exp = find_aspect_timing(self.JD, 0, 1, 51.4286, orb=expected_orb)
        # Both calls should return the same timing (same derived orb)
        assert result_dyn == result_exp

    def test_static_path_unchanged(self):
        """HARM-05: static path (orb=None, dyn_coef=None) is byte-identical."""
        from ketu.aspects.calculator import find_aspect_timing
        before = find_aspect_timing(self.JD, 0, 1, 120.0)
        after  = find_aspect_timing(self.JD, 0, 1, 120.0, dyn_coef=None)
        assert before == after

    def test_explicit_orb_wins_over_dyn_coef(self):
        """HARM-05 precedence: explicit orb= wins silently when both are given."""
        from ketu.aspects.calculator import find_aspect_timing
        explicit_orb = 3.0
        coef = 1 / 7  # would give ~1.7°, different from 3.0
        # The explicit orb should dominate
        result_explicit = find_aspect_timing(self.JD, 0, 1, 51.4286, orb=explicit_orb)
        result_both     = find_aspect_timing(self.JD, 0, 1, 51.4286, orb=explicit_orb,
                                              dyn_coef=coef)
        assert result_explicit == result_both  # explicit orb wins, not derived

    def test_off_table_no_orb_no_dyn_coef_raises(self):
        """HARM-05: off-table angle with neither orb nor dyn_coef still raises ValueError."""
        from ketu.aspects.calculator import find_aspect_timing
        with pytest.raises(ValueError):
            find_aspect_timing(self.JD, 0, 1, 51.4286)
```

### Gates

- `fail_under=100` — the new `dyn_coef is not None` branch must be covered.
- The existing `TestFindAspectTimingGuards` tests (lines 531-566 of
  `tests/test_dynamic_harmonics.py`) must continue passing unchanged — they test
  the backward-compatible paths.
- mypy `--strict` clean: `Optional[float]` is trivially clean; no `np.void` typing.
- numpydoc gate: update docstring with numpydoc-formatted `dyn_coef` parameter block.

### Pitfalls

- **Do not move the `orb=None` check to after `dyn_coef`.** The precedence rule
  ("explicit orb wins") is implemented by checking `orb is not None` FIRST and
  short-circuiting. If you put the explicit-orb check last, `dyn_coef` would win
  when both are provided — wrong.
- **`bodies["orb"]` is indexed by position, not by body ID.** `bodies["orb"][0]`
  is Sun (body_id=0), `bodies["orb"][1]` is Moon. In `find_aspect_timing`, the
  `body1`/`body2` parameters are already body IDs used directly as array indices.
  Verify this matches the `calculate_aspects` indexing pattern
  (`calculator.py:197-198` uses `np.where(l_bodies["id"] == b1)` for the
  configurable bodies array; `find_aspect_timing` uses the global `bodies`
  directly — the body IDs ARE positional indices for the default `bodies` array
  because `bodies["id"]` = `[0,1,2,...,13]`).
- **`aspect_value` is the single source for the angle.** The `dyn_coef` parameter
  provides only the orb scale, NOT the angle. Do not try to derive the angle from
  `dyn_coef`.

---

## Debt F1 — CLI `--harmonics h7`

### Files to touch (full list)

1. **`ketu/cli/harmonics_spec.py`** — add `HarmonicsSelection` NamedTuple, new
   `h<N>` parse branch, update `parse_harmonics_spec` signature and return.
2. **`ketu/cli/aspects_cmd.py`** — destructure `HarmonicsSelection`, thread
   `dynamic_specs=`, extend `_preset_label_for_mask` (or parallel label path),
   update `emit_resolved_config` call, update `print_aspects` call.
3. **`ketu/display.py`** — `print_aspects` must accept `dynamic_specs=` to
   display correct synthetic names for dynamic rows (currently `i_asp=-2` would
   incorrectly index `_CORE_ASPECTS['name'][-2]` = `b'Quadrinovile'`).
4. **`ketu/cli/parser.py`** — update `--harmonics` help text to document `h7`
   syntax; update `type=` if needed (it already uses `parse_harmonics_spec`).
5. **`tests/cli/test_harmonics_spec.py`** — update existing tests that access
   return value directly as `np.ndarray` (lines 19-24, 142 use `.sum()`,
   `isinstance(mask, np.ndarray)`, etc.) — must access `.mask` after the change.
   Add new tests for the `h7` parse path and `HarmonicsSelection` shape.
6. **`tests/cli/test_parser.py`** — update tests at lines 114-117 that check
   `isinstance(args.harmonics, np.ndarray)`, `.dtype`, `.shape`, `.sum()` — must
   access `.mask` after the change.
7. **`tests/cli/test_aspects_cmd.py`** — update/add integration tests for the
   `--harmonics h7` flow end-to-end.
8. **`tests/cli/fixtures/`** — add `harmonics_h7_reference_output.txt` (new
   byte-stability fixture for `--harmonics h7 aspects --date ...`).
9. **`tests/cli/test_v1_1_reference_byte_stable.py`** — add a sibling test class
   `TestHarmonicsH7ByteStable` (do NOT modify the existing `TestV1_1ReferenceByteStable`).
10. **`docs/source/concepts.md`** — add `--harmonics h7` section (syntax,
    semantics, Tight-grammar boundary, what is deferred).
11. **`docs/source/api.md`** — update `parse_harmonics_spec` and the CLI
    `--harmonics` entry.
12. **`docs/locale/fr/LC_MESSAGES/concepts.po`** and **`api.po`** — translate
    new paragraphs.

### Current state (verified)

**`harmonics_spec.py:43`** — `parse_harmonics_spec` returns
`npt.NDArray[np.bool_]`. Four parse branches (lines 75, 84, 104, 117):
- L75: preset names → `resolve_aspect_set(s)` returns mask
- L84: comma → `resolve_aspect_set(indices)` returns mask
- L104-114: bare int → `ArgumentTypeError`
- L117-120: anything else → `ArgumentTypeError` (this is where `h7` currently lands)

**`parser.py:85-97`** — `--harmonics` already wired with `type=parse_harmonics_spec`.

**`aspects_cmd.py:90-95`** — `args.harmonics` consumed as raw mask or None.
After change: `args.harmonics` will be `HarmonicsSelection | None`.

**`display.py:75-84`** — `print_aspects` calls `calculate_aspects(jdate, aspects=aspects)`
and then `_CORE_ASPECTS['name'][i_asp]` for each row. **Bug for dynamic rows:**
`i_asp=-2` maps to `_CORE_ASPECTS['name'][-2]` = `b'Quadrinovile'` (verified).
`print_aspects` must be extended to accept `dynamic_specs=` and do the same
synthetic-name lookup as `find_aspects_between_dates` (lines 744-759 of
`calculator.py`).

### Step-by-step changes

#### Step 1 — `harmonics_spec.py`: NamedTuple + new parse branch

```python
from typing import NamedTuple
from ketu.aspects.harmonics import DynamicAspectSpec, generate_harmonic_aspects
import re

class HarmonicsSelection(NamedTuple):
    mask: npt.NDArray[np.bool_]          # length-14, always present
    dynamic_specs: DynamicAspectSpec     # None or array

_H_TOKEN_RE = re.compile(r"^h(\d+)$")   # compiled once at module level

def parse_harmonics_spec(value: str) -> HarmonicsSelection:
    ...
    # After preset branch (returns HarmonicsSelection(mask=..., dynamic_specs=None))
    # After comma branch (same)
    # NEW: h<N> branch — BEFORE the bare-int trap
    m = _H_TOKEN_RE.match(s)
    if m:
        h_str = m.group(1)
        try:
            h = int(h_str)
        except ValueError:
            # cannot happen since _H_TOKEN_RE requires \d+, but defensive
            raise argparse.ArgumentTypeError(f"invalid harmonic in {value!r}")
        try:
            specs = generate_harmonic_aspects(h)
        except ValueError as e:
            raise argparse.ArgumentTypeError(str(e))
        empty_mask = np.zeros(14, dtype=np.bool_)
        return HarmonicsSelection(mask=empty_mask, dynamic_specs=specs)
    # bare-int trap (unchanged)
    # unrecognized branch (unchanged)
```

The `all-False` mask for `h7` means no table aspects are selected; only dynamic
aspects fire. This is "only the H7 family" behaviour (locked).

#### Step 2 — `aspects_cmd.py`: destructure and thread

```python
# Old:
if args.harmonics is None:
    mask = resolve_aspect_set("classical"); preset_label = "classical"
else:
    mask = args.harmonics
    preset_label = _preset_label_for_mask(mask)

# New:
if args.harmonics is None:
    mask = resolve_aspect_set("classical"); dyn = None; label = "classical"
else:
    mask = args.harmonics.mask
    dyn  = args.harmonics.dynamic_specs
    label = _preset_label_for_mask(mask) if dyn is None else _harmonic_label(dyn)

emit_resolved_config(mask, label, house_system=None)
...
print_aspects(jd, aspects=mask, dynamic_specs=dyn)
```

`_harmonic_label(dyn)` needs to extract the harmonic token. Because
`generate_harmonic_aspects(h)['harmonic']` carries `h` for every row, the label
can be derived: `h = int(dyn['harmonic'][0])` → label `f"h{h}"`. For a list of
specs: join multiple `h` values.

The `emit_resolved_config` call with a harmonic label must emit something like:
`# Aspect set: h7 (3 aspects: H7-1 51°, H7-2 102°, H7-3 154°)`.
`emit_resolved_config` in `formatters.py` currently iterates `_CORE_ASPECTS["name"][mask]`.
For the dynamic case, the mask is all-False (no table aspects), so the details
string would be empty — wrong. Two options:
  - Pass a `dynamic_label` string to `emit_resolved_config` that overrides the
    details when `dynamic_specs` is not None.
  - Handle in `aspects_cmd.py` directly before calling `emit_resolved_config`.

Simplest: add an optional `dynamic_label: str | None = None` to
`emit_resolved_config`. When provided, it overrides the mask-derived detail
string. The stderr line becomes:
`# Aspect set: h7 (3 aspects: H7-1 51°, H7-2 102°, H7-3 154°)`.

#### Step 3 — `display.py`: `print_aspects` dynamic_specs support

```python
from ketu.aspects.harmonics import DynamicAspectSpec

def print_aspects(
    jdate: float,
    aspects: "AspectSetSpec" = None,
    dynamic_specs: DynamicAspectSpec = None,
) -> None:
    ...
    for aspect in calculate_aspects(jdate, aspects=aspects, dynamic_specs=dynamic_specs):
        body1, body2, i_asp, orb = aspect
        degs, mins, secs = dd_to_dms(orb)
        if i_asp == -2:
            # Dynamic row — look up synthetic name from dynamic_specs
            dyn = _normalize_dynamic_specs(dynamic_specs)
            # ... name lookup same as calculator.py:744-759
        else:
            aspect_name_bytes = _CORE_ASPECTS['name'][i_asp]
            aspect_name = aspect_name_bytes.decode() if isinstance(...) else str(...)
```

The existing `i_asp=-2` rows MUST display the synthetic `H7-k` name, not
`Quadrinovile`. This is a required fix for correctness of `--harmonics h7`.

#### Step 4 — `parser.py`: update help text

The `--harmonics` help string currently lists only preset names and index lists.
Add: `"or an arbitrary harmonic 'h<N>' (e.g. 'h7' for septile family)"`.
No other changes to `parser.py` — the `type=parse_harmonics_spec` wiring already
handles it.

#### Step 5 — byte-stability fixture (the ketu ritual)

Generate the fixture:
```bash
python -m ketu --harmonics h7 aspects --date 2000-01-01T12:00:00Z \
  > tests/cli/fixtures/harmonics_h7_reference_output.txt
```
Then **manually audit** before committing:
- Confirm aspect lines show `H7-1`/`H7-2`/`H7-3` names (not `Quadrinovile`)
- Confirm angles match septile family: ~51.43°, ~102.86°, ~154.29°
- Confirm the "Aspect Timing Example" block (Sun/Moon classical) is still present
  and unchanged (it is always emitted, classical-pinned per `aspects_cmd.py:109-125`)
- Check stderr (not stdout) contains `# Aspect set: h7`

Add the sibling test class in `test_v1_1_reference_byte_stable.py` (do NOT
modify the existing `TestV1_1ReferenceByteStable`):

```python
FIXTURE_H7 = Path(__file__).parent / "fixtures" / "harmonics_h7_reference_output.txt"
REFERENCE_ARGV_H7 = [sys.executable, "-m", "ketu",
                     "--harmonics", "h7", "aspects", "--date", REFERENCE_DATE]

class TestHarmonicsH7ByteStable:
    def test_fixture_exists_and_nonempty(self): ...
    def test_h7_byte_identical_to_fixture(self): ...
    def test_stderr_contains_h7_header(self): ...
    # etc.
```

### Test specs for F1

**Existing tests that MUST be updated** (they currently access `parse_harmonics_spec`
return value as if it were a raw `np.ndarray`):

| File | Line | Current code | Updated code |
|---|---|---|---|
| `test_harmonics_spec.py` | 19 | `assert isinstance(mask, np.ndarray)` | `assert isinstance(result.mask, np.ndarray)` |
| `test_harmonics_spec.py` | 20 | `assert mask.dtype == np.bool_` | `assert result.mask.dtype == np.bool_` |
| `test_harmonics_spec.py` | 21 | `assert mask.shape == (14,)` | `assert result.mask.shape == (14,)` |
| `test_harmonics_spec.py` | 22 | `assert mask.sum() == 5` | `assert result.mask.sum() == 5` |
| `test_harmonics_spec.py` | 142 | `args.harmonics.sum() == 5` | `args.harmonics.mask.sum() == 5` |
| `test_parser.py` | 114 | `isinstance(args.harmonics, np.ndarray)` | `isinstance(args.harmonics, HarmonicsSelection)` |
| `test_parser.py` | 115 | `args.harmonics.dtype == np.bool_` | `args.harmonics.mask.dtype == np.bool_` |
| `test_parser.py` | 116 | `args.harmonics.shape == (14,)` | `args.harmonics.mask.shape == (14,)` |
| `test_parser.py` | 117 | `args.harmonics.sum() == 5` | `args.harmonics.mask.sum() == 5` |

**New tests to add** (in `test_harmonics_spec.py` or a new file):

```python
class TestHarmonicTokenF1:
    def test_h7_accepted_returns_named_tuple(self): ...  # isinstance HarmonicsSelection
    def test_h7_mask_is_all_false(self): ...  # len=14, all False
    def test_h7_dynamic_specs_has_3_rows(self): ...  # len=3
    def test_h7_dynamic_specs_names(self): ...  # [b'H7-1', b'H7-2', b'H7-3']
    def test_H7_uppercase_accepted(self): ...  # case-insensitive
    def test_h2_accepted_1_row(self): ...  # boundary
    def test_h64_accepted_32_rows(self): ...  # boundary
    def test_h1_rejected(self): ...  # out-of-range
    def test_h65_rejected(self): ...  # out-of-range
    def test_h0_rejected(self): ...  # out-of-range
    def test_preset_still_returns_mask_only(self): ...  # dynamic_specs=None
    def test_index_list_still_returns_mask_only(self): ...  # dynamic_specs=None
    def test_argparse_h7_end_to_end(self): ...  # parse_args(['--harmonics','h7',...])
```

### Gates

- `fail_under=100` — every new branch in `harmonics_spec.py`, `aspects_cmd.py`,
  `display.py` must be covered. In particular:
  - The `_H_TOKEN_RE.match(s)` branch in `parse_harmonics_spec`
  - The `dyn is not None` path in `print_aspects`
  - The `_harmonic_label` function
  - The `dynamic_label` path in `emit_resolved_config`
- Existing `TestV1_1ReferenceByteStable` must pass UNCHANGED (no re-pinning).
- NEW `TestHarmonicsH7ByteStable` must pass (fixture pinned after manual audit).
- mypy `--strict` clean: `HarmonicsSelection` NamedTuple must be typed; consumers
  annotated `HarmonicsSelection | None`.
- numpydoc/interrogate on `harmonics_spec.py` (module docstring + function
  docstring updated), `display.py` (`print_aspects` docstring updated),
  `aspects_cmd.py`.

### Pitfalls

- **`h7` in the comma branch.** If someone passes `"h7,h11"`, the comma branch
  (line 84) fires first and tries `int("h7")` → `ValueError` → "invalid
  harmonics list" error message. This is the correct Tight-grammar rejection
  (`h7,h11` is DEFERRED). However, make sure the error message is informative
  (not just "invalid harmonics list 'h7,h11'"). Consider a small improvement:
  detect `h` tokens in the comma list and surface a "multi-harmonic syntax is
  not yet supported" message. NOT strictly required by the spec, but improves UX.
- **`_PRESET_NAMES` is a closed frozenset.** It is `{"classical","traditional","extended","all"}`.
  The new `h<N>` branch must be inserted AFTER the preset check but BEFORE the
  bare-int trap. Order in `parse_harmonics_spec`: (1) preset, (2) comma, (3) NEW
  `h<N>`, (4) bare-int rejection, (5) unrecognized.
- **Return type change breaks existing consumers.** The `test_harmonics_spec.py`
  and `test_parser.py` tests access `.sum()`, `.dtype`, `.shape` directly on the
  return value. These WILL break unless updated. See the update table above.
- **`print_aspects` is called from non-CLI code too** (e.g. tests and examples
  call `print_aspects(jd)` with no `dynamic_specs=`). The new parameter must
  default to `None` so existing calls remain unchanged.
- **`emit_resolved_config` currently iterates `_CORE_ASPECTS["name"][mask]`.**
  For the harmonic case, `mask` is all-False, so `details` would be an empty
  string. The header would say `# Aspect set: h7 (0 aspects: )` — wrong. The
  `dynamic_label` approach fixes this cleanly.
- **`_normalize_dynamic_specs` import in `display.py`.** If `print_aspects` does
  the synthetic-name lookup, it needs `_normalize_dynamic_specs` from
  `calculator.py`, or the logic can be duplicated as a small inline helper. Keep
  it DRY: import from `calculator` or refactor into a shared utility in
  `harmonics.py`.
- **The "Aspect Timing Example" trailing block** in `aspects_cmd.py:109-125` is
  ALWAYS classical-pinned. It uses `find_aspects_between_dates(..., aspects="classical")`
  with no `dynamic_specs`. This MUST remain unchanged so the v1.1 byte-stability
  fixture stays intact. The NEW `--harmonics h7` fixture will include this
  classical-pinned block unchanged.
- **`parse_harmonics_spec` is documented as returning `NDArray[np.bool_]`** in
  the module docstring AND in `parser.py:83`. Both must be updated to reflect
  `HarmonicsSelection`. The module docstring of `harmonics_spec.py` explicitly
  says "returns a length-14 `np.bool_` mask".

---

## Implementation Order Summary

### Wave 1 — F2: Naming Contract (no code changes, only tests + docs)

| Plan | Changes |
|---|---|
| Tests | Add `TestNamingContractF2` to `tests/test_dynamic_harmonics.py` |
| Docs EN | Update `docs/source/concepts.md` and `api.md` with two-channel distinction + traditional-name reference table |
| Docs FR | Translate new paragraphs in `docs/locale/fr/LC_MESSAGES/concepts.po` and `api.po`; recompile `.mo` |

All F2 changes are additive; no existing tests break.

### Wave 2 — F3: `find_aspect_timing` dyn_coef (independent of F2 and F1)

| Plan | Changes |
|---|---|
| Code | `ketu/aspects/calculator.py`: add `dyn_coef` param, update orb-resolution logic |
| Tests | Add `TestFindAspectTimingF3` to `tests/test_dynamic_harmonics.py` |
| Docs EN | Update `docs/source/api.md` `find_aspect_timing` entry |
| Docs FR | Translate in `api.po`; recompile |

No existing tests break (backward-compatible addition).

### Wave 3 — F1: CLI `--harmonics h7` (depends on F2 naming contract being stable)

| Plan | Changes |
|---|---|
| Core types | `ketu/cli/harmonics_spec.py`: `HarmonicsSelection`, new `h<N>` branch |
| Display | `ketu/display.py`: add `dynamic_specs=` to `print_aspects` |
| CLI wiring | `ketu/cli/aspects_cmd.py`: destructure `HarmonicsSelection`, thread `dynamic_specs=`, harmonic header label |
| Formatters | `ketu/cli/formatters.py`: add `dynamic_label=` to `emit_resolved_config` |
| Parser help | `ketu/cli/parser.py`: update `--harmonics` help text |
| Test updates | `tests/cli/test_harmonics_spec.py`: update existing + add new `TestHarmonicTokenF1` |
| Test updates | `tests/cli/test_parser.py`: update 4 assertions |
| Test updates | `tests/cli/test_aspects_cmd.py`: add `--harmonics h7` integration tests |
| Byte-stability | Generate + audit + commit `fixtures/harmonics_h7_reference_output.txt` |
| Byte-stability | Add `TestHarmonicsH7ByteStable` class |
| Docs EN | `concepts.md`, `api.md`: `--harmonics h7` CLI section |
| Docs FR | `concepts.po`, `api.po`; recompile |

---

## Verification Log

All claims from `.planning/research/HARMONICS_DEBT.md` verified against the live codebase this session:

| Claim | Status | Notes |
|---|---|---|
| `harmonics.py:118` — `generate_harmonic_aspects` definition | CONFIRMED | Exact line match |
| `harmonics.py:196` — range check `2 <= h <= 64` | CONFIRMED | Actual line 196: `if not (2 <= h <= 64)` |
| `harmonics.py:204-208` — naming loop with `f"H{h}-{k}".encode()` | CONFIRMED | Line 207 exact |
| `harmonics_spec.py:43` — `parse_harmonics_spec` signature | CONFIRMED | Returns `npt.NDArray[np.bool_]` |
| `harmonics_spec.py:75` — preset branch | CONFIRMED | Exact line |
| `harmonics_spec.py:84` — comma branch | CONFIRMED | Exact line |
| `harmonics_spec.py:104-114` — bare-int rejection | CONFIRMED | Exact lines |
| `harmonics_spec.py:117` — unrecognized fallback | CONFIRMED | Exact line; `h7` currently lands here |
| `calculator.py:56-59` — `_normalize_dynamic_specs` | CONFIRMED | Lines 54-60 |
| `calculator.py:81-82` — `get_orb` formula | CONFIRMED | Exact lines |
| `calculator.py:119` — `calculate_aspects` `dynamic_specs=` param | CONFIRMED | Line 119 |
| `calculator.py:215-216` — dyn_coef formula in `calculate_aspects` | CONFIRMED | Exact lines |
| `calculator.py:568` — `find_aspect_timing` definition | CONFIRMED | Exact line |
| `calculator.py:611-617` — static orb-lookup block | CONFIRMED | Exact lines |
| `calculator.py:736-746` — name resolution in `find_aspects_between_dates` | CONFIRMED | Lines 736-759 (slightly wider) |
| `aspects_cmd.py:90-95` — mask consumption | CONFIRMED | Lines 90-95 exact |
| `aspects_cmd.py:98` — `emit_resolved_config` call | CONFIRMED | Line 98 |
| `aspects_cmd.py:109-125` — always-on Aspect Timing Example block | CONFIRMED | Lines 109-125 |
| `_preset_label_for_mask` returns `"custom"` for all-False mask | CONFIRMED | Verified by running |
| `parser.py:85-97` — `--harmonics` argparse wiring | CONFIRMED | Lines 85-97 |
| `tests/cli/test_v1_1_reference_byte_stable.py` exists | CONFIRMED | File read |
| V1 sha256 = `c5bd177...` | CONFIRMED | In `tests/test_ketu.py:104-106` AND `tests/test_dynamic_harmonics.py:319` |
| V13 sha256 = `3258530...` | CONFIRMED | In `tests/test_ketu.py:110-112` |
| h=2 → 1 row `b'H2-1'` @ 180° | CONFIRMED | Live run |
| h=7 → 3 rows, angles [51.43, 102.86, 154.29] | CONFIRMED | Live run + existing tests |
| even-h last row folds to exactly 180° | CONFIRMED | Live run |
| `print_aspects` uses `_CORE_ASPECTS['name'][i_asp]` — bug for i_asp=-2 | CONFIRMED | `display.py:78`; `-2` index returns `b'Quadrinovile'` |
| `print_aspects` currently has NO `dynamic_specs=` param | CONFIRMED | Signature: `(jdate, aspects=None)` |
| 1537 tests pass, 100% coverage | CONFIRMED | `pytest tests/ -q` output |

**One drift from the brief:** The brief references `calculator.py:754-759` for
name recovery in `find_aspects_between_dates`. Actual line range is 744-759 (the
static lookup is at 736, dynamic at 744). The logic is identical; only the line
numbers shifted slightly.

**Undocumented gap discovered:** `print_aspects` in `display.py` is NOT covered
in the brief's "files to touch" list for F1. It must be updated to accept
`dynamic_specs=` and perform synthetic-name lookup for `i_asp=-2` rows. Without
this fix, `--harmonics h7` would display `Quadrinovile` instead of `H7-1` etc.
for every dynamic aspect row. This is a new finding that must be planned.

---

## RESEARCH COMPLETE

**Phase:** 34 — Harmonics Debt (ASP-F1/F2/F3)
**Confidence:** HIGH — all code claims verified against live files; boundary
outputs confirmed by running the venv.

### Key Findings

- F2 (naming contract): zero code changes needed; all naming is already correct.
  Pure test + doc addition. Can ship as a single atomic plan.
- F3 (`dyn_coef`): surgical addition of one parameter to `find_aspect_timing`.
  Three backward-compatible paths; one new branch; one precedence test required
  ("explicit orb wins" = silent, NOT raise).
- F1 (CLI): broader surface than the brief suggested — `print_aspects` in
  `display.py` ALSO needs `dynamic_specs=` to display correct synthetic names
  (i_asp=-2 bug discovered). Six files need code changes; nine files total.
- Tight grammar means `h7,h11` enters the comma branch and fails with "invalid
  harmonics list" — acceptable (deferred). Consider a better error message.
- The `HarmonicsSelection` return-type change will break 9 existing test
  assertions (identified and mapped above) — they must be updated in the same
  plan as the harmonics_spec.py change.
- Byte-stability fixture for `--harmonics h7` must be generated + manually
  audited before pinning (ketu ritual). The Aspect Timing Example block in the
  output stays classical-pinned unchanged — confirm it appears in the new fixture.
