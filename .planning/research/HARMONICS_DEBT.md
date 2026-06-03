# Dynamic-Harmonics Debt — Design Research (ASP-F1/F2/F3)

**Domain:** Internal API/CLI consistency for `ketu` v1.5
**Researched:** 2026-06-03
**Overall confidence:** HIGH (recommendations grounded in verified existing code; ecosystem check is MEDIUM and only informs naming)

This is an internal design task. v1.4 already shipped the engine
(`generate_harmonic_aspects(h)` + the `dynamic_specs=` path threaded through
`calculate_aspects` / `find_aspects_between_dates`). Three debts remain. Every
recommendation below is shaped to drop into the EXISTING code with minimal
surface and to satisfy the hard gates (frozen `core.aspects` byte-identical,
pure NumPy runtime, mypy --strict, `fail_under=100`, numpydoc/interrogate,
CLI sha256 byte-stability fixtures).

---

## 1. ASP-F1 — CLI grammar for arbitrary harmonics (`--harmonics h7`)

### 1.1 The disambiguation problem

`parse_harmonics_spec` (`ketu/cli/harmonics_spec.py:43`) today routes on shape:

| Input shape | Branch | Result |
|---|---|---|
| preset name (`classical`/`traditional`/`extended`/`all`) | line 75 | length-14 bool mask |
| contains `,` | line 84 | indices → length-14 bool mask |
| bare integer (`"12"`) | line 104 | **REJECTED** — ambiguous (ArgumentTypeError, lines 110-114) |
| empty / anything else | line 117 | REJECTED |

The bare-int rejection is deliberate and tested (`tests/cli/test_harmonics_spec.py`).
A new arbitrary-harmonic token must be unambiguous against ALL four branches.

### 1.2 Syntax recommendation: `h<N>` (lowercase `h` prefix) — RECOMMENDED

**Use `h7`, `h11`, `h17`.** Rationale, validated against each existing branch:

- **vs bare-int rejection** — `h7` is not parseable by `int()`, so it never
  reaches the line 104 bare-int trap. The ambiguity that justified rejecting
  `"7"` ("single index? harmonic? subset?") is resolved precisely by the `h`
  tag: `h` means *harmonic*. Clean separation.
- **vs preset names** — `_PRESET_NAMES` (line 38) is a closed frozenset; none
  start with `h` (`classical/traditional/extended/all`). After `.lower()`
  (line 68), `h7` cannot collide. No future preset should be named `h*`.
- **vs index list** — no comma, so it never enters the line 84 list branch.
- **Ecosystem fit** — the astrology convention writes the *n*-th harmonic as
  "H*n*" (H5 quintile, H7 septile, H9 novile — see §1.6 / Sources). `h7` is the
  lowercase mirror of that idiom; users reading harmonic-chart literature will
  recognise it immediately.

**Case handling:** because line 68 already lowercases the whole spec, accept
`h7`, `H7`, `h 7` (after strip of internal space? — no, keep it strict: a single
token `h<digits>`). Recommend the canonical surface be lowercase `h7`; `H7`
maps to the same thing for free via the existing `.lower()`. Document `h7` as
canonical.

**Grammar (regex, applied AFTER preset + comma branches, BEFORE the bare-int
trap):** `^h(\d+)$` on the already-lowercased `s`. The captured group is parsed
with `int()` and handed to `generate_harmonic_aspects()`, which owns range
validation (`2 <= h <= 64`, `harmonics.py:196`). Do NOT duplicate the range
check in the CLI — let the generator's `ValueError` propagate (wrap as
`ArgumentTypeError` per the module's argparse convention, lines 23-26).

### 1.3 Rejected alternatives

| Alternative | Why not |
|---|---|
| bare `7` | The whole point of the existing rejection (line 104) is that bare ints are ambiguous. Un-rejecting it would break `test_*` and re-introduce the ambiguity. |
| `harmonic:7` / `harmonic=7` | Verbose; introduces a `:`/`=` sublexer with no other use; argparse already splits on `=` for `--flag=value`, inviting confusion. |
| `7th` | Ordinal suffix parsing is locale-flavoured and ugly; collides with nothing but reads worse than `h7`. |
| `H7` as the ONLY accepted form | Fine, but since line 68 lowercases everything, `h7` is the natural canonical. Accept both, canonicalise to `h7` in docs. |

`h<N>` is the recommendation; `H<N>` is accepted as a free alias.

### 1.4 Semantics — CONFIRMED

`h7` means **"harmonic 7"** → call `generate_harmonic_aspects(7)`
(`harmonics.py:118`) → a structured array of shape `(7//2,) = (3,)` with names
`b'H7-1', b'H7-2', b'H7-3'` at angles `51.43, 102.86, 154.29`. That array is
fed to the command layer as `dynamic_specs=` (the parameter already accepted by
`calculate_aspects` / `find_aspects_between_dates`, see
`calculator.py:119,660`). Verified output:

```
h=2  -> ['H2-1']  (180.0)
h=7  -> ['H7-1','H7-2','H7-3']  (51.43, 102.86, 154.29)
h=12 -> ['H12-1'..'H12-6']  (30,60,90,120,150,180)
```

So `--harmonics h7` produces aspects at the three septile-family angles, named
`H7-1/2/3`. This is the correct and expected semantics.

### 1.5 Combination grammar — minimal coherent set

The existing surface has TWO disjoint output channels:

- **static channel:** a length-14 bool mask into `core.aspects` (presets + index lists)
- **dynamic channel:** a `dynamic_specs` structured array (harmonics)

A clean v1.5 grammar should let a single `--harmonics` value populate both
channels. Recommended grammar (comma-separated token list, each token typed):

```
spec      := preset | token-list
token-list := token ("," token)*
token      := index | harmonic        # index = digits; harmonic = h<digits>
preset    := classical|traditional|extended|all
```

Concretely, RECOMMEND supporting:

| Input | static mask | dynamic_specs | Notes |
|---|---|---|---|
| `h7` | (none → default/empty) | `g(7)` | single harmonic |
| `h7,h11` | (none) | `[g(7), g(11)]` | multiple harmonics (list — `_normalize_dynamic_specs` concatenates, `calculator.py:56-59`) |
| `traditional,h7` | traditional mask | `g(7)` | preset + harmonic mix |
| `0,4,h7` | indices {0,4} | `g(7)` | index list + harmonic mix |
| `classical` | classical mask | None | unchanged |
| `0,4,7,9,13` | indices | None | unchanged |

**Decision points (flagged as open in §4):**
- Whether `h7` ALONE leaves the static mask empty vs. defaults to the current
  CLI "classical" fallback. RECOMMEND: when ANY token is present, the static
  mask is exactly the union of the index/preset tokens given (empty if none) —
  do NOT silently inject classical. `--harmonics h7` should mean "only the H7
  family", not "classical + H7". This is the least-surprising rule and keeps the
  two channels independent.
- Whether a *bare* preset name may appear inside a comma list (`traditional,h7`).
  RECOMMEND yes, but ONLY as the first token and only one preset, to avoid
  defining preset-union semantics. Simpler still: forbid preset-in-list and
  require either a single preset OR a token-list of indices+harmonics. Pick the
  simpler one for v1.5 (see §4-A).

**Minimal coherent grammar for v1.5 (the tight option):** keep presets as
standalone-only; extend the comma-list branch so each comma token is EITHER an
index (`\d+`) OR a harmonic (`h\d+`). This reuses the existing line 84 split,
adds one regex test per token, and yields `(mask, dynamic_specs)`. `traditional,h7`
is then NOT supported (use `extended` semantics via indices if you need table
aspects + a harmonic: `0,1,4,7,9,11,13,h7`). This is the cleanest minimal step;
the preset+harmonic mix can be a later enhancement.

### 1.6 `parse_harmonics_spec` return-shape change (the typing crux)

Today: `parse_harmonics_spec(value) -> npt.NDArray[np.bool_]` (a mask only). The
command layer (`aspects_cmd.py:90-95`) reads `args.harmonics` as "mask or None".

The dynamic channel needs a SECOND output. Under mypy --strict, return a typed
2-tuple (a `NamedTuple` is cleanest for self-documenting field access and clean
stubs):

```python
class HarmonicsSelection(NamedTuple):
    mask: npt.NDArray[np.bool_]                 # length-14, always present
    dynamic_specs: DynamicAspectSpec            # None or array/list of arrays
```

- `DynamicAspectSpec` already exists and is exactly the right type
  (`harmonics.py:67`: `Optional[Union[NDArray[np.void], List[NDArray[np.void]]]]`).
  Reuse it — do NOT invent a new alias.
- Signature becomes `parse_harmonics_spec(value: str) -> HarmonicsSelection`.
- For ALL existing inputs (presets, index lists), return
  `HarmonicsSelection(mask=<existing mask>, dynamic_specs=None)` — behaviour
  unchanged, only the wrapper is new.
- For harmonic tokens, `mask` is the union of any index/preset tokens (or an
  all-False length-14 mask if none), and `dynamic_specs` carries the
  `generate_harmonic_aspects(h)` array(s).

**Why a NamedTuple over a tagged union / `dict` / two functions:**
- mypy --strict resolves `.mask` / `.dynamic_specs` with exact types; no
  `cast`, no `# type: ignore`.
- argparse's `type=` callback must return ONE object; a NamedTuple is one
  object that the command layer destructures. (A bare `tuple[mask, specs]` also
  works but the named fields document the contract and survive refactors.)
- It is additive: `args.harmonics` becomes a `HarmonicsSelection | None`
  instead of `mask | None`. The command layer change is localised to
  `aspects_cmd.py` (and any other consumer of `args.harmonics`).

**Command-layer wiring (`aspects_cmd.py`):**
```python
if args.harmonics is None:
    mask = resolve_aspect_set("classical"); dyn = None; label = "classical"
else:
    mask = args.harmonics.mask
    dyn  = args.harmonics.dynamic_specs
    label = _preset_label_for_mask(mask)   # extend to report harmonics
# then thread dyn into print_aspects / calculate_aspects via dynamic_specs=dyn
```
`print_aspects` / `calculate_aspects` already accept `dynamic_specs=`
(`calculator.py:119`), so the plumbing exists end-to-end; only the CLI layer
needs the new field.

### 1.7 CLI byte-stability — FLAGGED (the ketu ritual)

Two distinct concerns:

1. **No regression for existing invocations.** Because presets/index-lists keep
   returning the same mask (now wrapped), and `--harmonics all` still resolves
   to `extended`, the pinned fixture
   `tests/cli/fixtures/v1_1_reference_output.txt`
   (`test_v1_1_reference_byte_stable.py`) must remain byte-identical. The
   wrapper change is internal; verify the existing fixture still passes
   UNCHANGED. If it changes, something leaked — investigate before re-pinning.

2. **New `--harmonics h7` output is NEW bytes.** Any test that captures
   `--harmonics h7 aspects --date ...` stdout produces NEW aspect lines (e.g.
   `Sun H7-1 Moon ...`). Per the documented ketu ritual, the regression fixture
   for the new invocation must be **generated and then manually audited** before
   pinning (confirm angles, synthetic names `H7-k`, header label, the always-on
   "Aspect Timing Example" block which stays classical-pinned per
   `aspects_cmd.py:109-125`). Add a new pinned fixture + sha256/byte-diff test
   alongside the existing one; do NOT modify the v1.1 fixture to absorb new
   lines.

   Also note the resolved-config header (`emit_resolved_config`,
   `aspects_cmd.py:98`) currently labels via `_preset_label_for_mask` which only
   knows preset masks → will say `custom`. For a harmonic invocation the header
   should report the harmonic(s) (e.g. `# Aspect set: h7`). Extend
   `_preset_label_for_mask` (or pass the harmonic label through) and pin THAT in
   the new fixture. This is a header-on-stderr change; stdout stays clean.

---

## 2. ASP-F2 — formalize the synthetic naming contract `H{h}-{k}`

### 2.1 Current scheme (verified)

`generate_harmonic_aspects(h)` (`harmonics.py:204-208`) emits, for
`k = 1 … h//2`:
- `name  = f"H{h}-{k}".encode()` → **bytes**, dtype field `name S16`
- `angle = fold_to_0_180(k·360/h)` in `(0°, 180°]`
- `coef  = k/h`
- `harmonic = h`
- `symbol = ""` (blank, U4 — same as the 7 minor table aspects)

Verified boundary output:
```
h=2  -> H2-1 @180
h=3  -> H3-1 @120
h=4  -> H4-1@90, H4-2@180
h=5  -> H5-1@72, H5-2@144
h=6  -> H6-1@60, H6-2@120, H6-3@180
h=7  -> H7-1@51.43, H7-2@102.86, H7-3@154.29
h=9  -> H9-1@40, H9-2@80, H9-3@120, H9-4@160
h=12 -> H12-1@30 ... H12-6@180
```

### 2.2 Is `H{h}-{k}` a good, stable, documentable contract? YES — keep it.

It is uniform, parseable, collision-free WITHIN the dynamic channel, and matches
the ecosystem idiom (harmonic *n* ≈ "H*n*"). Two properties make it superior to
the traditional-name approach:

- **Uniformity > traditional names.** Astrology has traditional names for SOME
  low harmonics only: H5=quintile (72°), H7=septile (51.4°), H9=novile (40°),
  and the H5/H9 multiples (biquintile 144°, binovile 80°, quadnovile 160°). But
  there is no consistent traditional name for H11, H13, H17, nor for every
  `k`-multiple. Mixing "septile" for H7-1 but "H11-2" for H11-2 produces an
  inconsistent, harder-to-machine-parse contract. **RECOMMEND: always use
  `H{h}-{k}` for uniformity; never substitute traditional names in the
  generator output.** (Traditional names can live in DOCS as a reference table
  mapping `H5-1 ≡ quintile`, etc., for human readers — but the emitted `name`
  bytes stay `H{h}-{k}`.)

- **`k` carries the multiple unambiguously.** `H7-1/2/3` map to
  septile/biseptile/triseptile. A consumer that wants the traditional label can
  derive it from `(h, k)`; the reverse (parsing "biseptile" back to a coef) is
  lossy and locale-flavoured.

This is a RECOMMENDATION with one OPEN choice for the user: whether to also
ship a docs-only `(h,k) → traditional name` lookup table (see §4-B).

### 2.3 Precise contract specification (what v1.5 guarantees)

State this verbatim in the API docs and pin it with a test:

> **Synthetic aspect name contract (v1.5+).** For an integer harmonic
> `h` with `2 ≤ h ≤ 64`, `generate_harmonic_aspects(h)` returns a structured
> array of dtype `HARMONIC_DTYPE` (identical to `ketu.core.aspects.dtype`) and
> shape `(h // 2,)`. Row `j` (0-indexed) corresponds to `k = j + 1` and has:
>
> - **`name`**: the **byte string** `b"H{h}-{k}"` (ASCII, no padding shown),
>   stored in an `S16` field. Format: literal `H`, decimal `h`, literal `-`,
>   decimal `k`, `k ∈ [1, h//2]`. Encoding is **bytes**, not str (it is the
>   `.encode()` of the f-string, `harmonics.py:207`).
> - **`angle`**: `fold_to_0_180(k·360/h)`, an `f4`, in the half-open-to-closed
>   range `(0°, 180°]`.
> - **`coef`**: `k/h` as `f4`.
> - **`harmonic`**: `h` as `i4`.
> - **`symbol`**: empty `str` `""` in a `U4` field.
>
> **Ordering:** strictly ascending `k` (= ascending row index). Deterministic.
>
> **Stability:** the `(h, k) → name/angle/coef` mapping is FROZEN across v1.5+
> minor/patch releases. Adding new `h` support never changes existing rows.

Decode rule for consumers (already used at `calculator.py:754-759`): names come
back as `bytes`; decode with `.decode()` to get `"H7-1"`. Document that the
public-facing string form is the ASCII decode of the bytes.

### 2.4 Pinning test (shape)

Add to `tests/test_dynamic_harmonics.py` (or a dedicated
`test_harmonic_naming_contract.py`):

```python
def test_naming_contract_h7_exact():
    specs = generate_harmonic_aspects(7)
    # bytes, not str — pins the encoding half of the contract
    assert specs["name"].tolist() == [b"H7-1", b"H7-2", b"H7-3"]
    assert specs["name"].dtype == np.dtype("S16")
    assert [round(float(a), 2) for a in specs["angle"]] == [51.43, 102.86, 154.29]
    assert [round(float(c), 4) for c in specs["coef"]] == [0.1429, 0.2857, 0.4286]
    assert specs["symbol"].tolist() == ["", "", ""]
    assert specs["harmonic"].tolist() == [7, 7, 7]

def test_naming_contract_boundaries():
    assert generate_harmonic_aspects(2)["name"].tolist() == [b"H2-1"]   # opposition-only
    assert generate_harmonic_aspects(2)["angle"].tolist() == [180.0]
    # even h: last row folds to exactly 180°, still h//2 rows (no degenerate dedup)
    assert generate_harmonic_aspects(6)["name"].tolist() == [b"H6-1", b"H6-2", b"H6-3"]
    assert [round(float(a),1) for a in generate_harmonic_aspects(6)["angle"]] == [60.0, 120.0, 180.0]
    for h in range(2, 65):
        assert len(generate_harmonic_aspects(h)) == h // 2   # exact count, all h
```

The existing doctests at `harmonics.py:171-181` already pin h=7; promote that to
a first-class contract test so it cannot silently change.

### 2.5 Edge cases — CONFIRMED CORRECT

- **h=2 (opposition only):** 1 row, `H2-1 @180°`. Correct — the only folded
  angle of the 2nd harmonic is the opposition pole.
- **h even (e.g. 6, 12):** the last `k = h//2` gives `k·360/h = 180°`, which
  folds to exactly `180.0` and IS emitted. There are exactly `h//2` rows; no
  fewer (the fold never collapses two distinct `k ≤ h//2` to the same value for
  `k` in range). Verified for h=6 (3 rows) and h=12 (6 rows).
- **Cross-channel angle collisions are expected and harmless.** Several
  synthetic angles equal frozen-table angles: `H2-1=180°`, `H3-1=120°`,
  `H4-1=90°`, `H6-2=120°`, `H6-3=180°`, `H9-3=120°`, `H12-3=90°`, etc. The
  detection chain handles this correctly: the static path matches table angles
  FIRST and the dynamic path only fires when the static loop did NOT match
  (`calculator.py:209-210` "only when the static loop did NOT match"; the
  vectorized/between-dates paths use `matched_pairs` / `static_idx`-first
  name resolution, `calculator.py:736-746`). So a 120° hit is reported under its
  table name (trine), not `H3-1`, when the trine is in the active set. **Contract
  note to document:** `H{h}-{k}` is the name a dynamic angle receives ONLY when
  that exact angle is not already a selected static aspect; the naming contract
  is about what the GENERATOR emits, while the DETECTION layer prefers the
  canonical table name on collision. Keep these two statements distinct in docs.

---

## 3. ASP-F3 — `find_aspect_timing` orb derivation

### 3.1 The debt

`find_aspect_timing(jdate, body1, body2, aspect_value, orb=None)`
(`calculator.py:568`) has two paths:
- `orb is None` → static: look up `aspect_value` in `_CORE_ASPECTS`, then
  `orb = get_orb(body1, body2, asp_idx)` (`calculator.py:611-617`).
- `orb=<float>` → dynamic escape hatch: caller passes a pre-computed orb. The
  docstring (`calculator.py:588-593`) tells the caller to compute
  `(bodies['orb'][b1]+bodies['orb'][b2])/2 * dyn_coef` THEMSELVES.

That delegation is the debt: the orb-derivation formula lives in TWO places
(here, in the caller's head; and authoritatively in `get_orb`,
`calculator.py:81-82`, and in the dynamic branches of `calculate_aspects`,
`calculator.py:216` / vectorized `:360` / batch `:503`). The function should be
able to derive the dynamic orb itself from a spec, exactly like
`calculate_aspects` does.

### 3.2 Options

| Option | Signature addition | Pros | Cons |
|---|---|---|---|
| **(a) `dyn_coef`** | `dyn_coef: Optional[float] = None` | Tiny; mirrors the exact quantity used at `calculator.py:215-216`; trivially typed under --strict | Caller still extracts `coef` from the spec row; one indirection remains, but it's a `float`, not a formula |
| **(b) dynamic_spec row** | `dyn_spec: Optional[NDArray[np.void]] = None` (one row) | Function reads `coef` itself; symmetrical with how the row carries angle too | A "single row" of a structured array is awkward to type (`np.void`); caller must slice `specs[k]`; `aspect_value` would then be redundant with `dyn_spec["angle"]` (two sources of truth for the angle) |
| **(c) harmonic h** | `harmonic: Optional[int] = None` (+ recompute) | Most "self-contained" | Re-derives `coef=k/h` → needs `k` too, so really needs `(h,k)`; re-implements the generator's math inside the timing function — duplicates `harmonics.py` logic. Worst for single-source-of-truth. |

### 3.3 Recommendation: **Option (a) — add `dyn_coef: Optional[float] = None`**

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

Orb-resolution logic (replaces lines 611-617):

```python
if orb is None:
    if dyn_coef is not None:
        # Dynamic path — derive orb from the coef, mirroring calculate_aspects
        # (calculator.py:215-216) and get_orb's formula (calculator.py:81-82).
        orb = (
            float(bodies["orb"][body1]) + float(bodies["orb"][body2])
        ) / 2 * dyn_coef
    else:
        # Static path — frozen-table lookup (UNCHANGED).
        asp_idx = np.where(_CORE_ASPECTS["angle"] == aspect_value)[0]
        if len(asp_idx) == 0:
            raise ValueError(f"unknown aspect value: {aspect_value}")
        orb = get_orb(body1, body2, int(asp_idx[0]))
# else: explicit orb=<float> escape hatch — UNCHANGED, used as-is.
```

**Why (a):**
- It is the SAME scalar `calculate_aspects` already computes
  (`dyn_coef = float(dyn_row["coef"])` then
  `(orb_b1+orb_b2)/2 * dyn_coef`, `calculator.py:215-216`). The orb formula now
  lives behind one parameter shape across the whole module — no formula in any
  caller's head.
- `Optional[float]` is trivially clean under mypy --strict — no `np.void`
  single-row typing gymnastics (which option (b) drags in).
- `aspect_value` stays the single source for the angle; `dyn_coef` supplies only
  the orb scale. No redundant/contradictory angle source (the trap in option b).
- The caller does `dyn_coef=float(spec_row["coef"])` — one field read, matching
  the idiom already used three times in `calculate_aspects*`
  (`:215, :359, :462`).

**Optional convenience (only if the user wants it, §4-C):** ALSO accept a
single-row spec via a thin helper rather than overloading this signature — e.g.
a module-level `dyn_coef_from_row(row) -> float` returning `float(row["coef"])`.
Keeps the timing signature scalar-only (best for --strict) while removing the
caller's field-read boilerplate. RECOMMEND shipping the helper, keeping the
param as `dyn_coef: float`.

### 3.4 Backward-compatibility proof

The three reachable states after the change:

| Call | Before | After | Identical? |
|---|---|---|---|
| `find_aspect_timing(jd, b1, b2, 120.0)` | `orb=None` → table lookup → `get_orb` | `orb=None` AND `dyn_coef=None` → SAME table-lookup branch | YES — both new params default `None`; the `else` branch is the verbatim old code |
| `find_aspect_timing(jd, b1, b2, 51.4286, orb=2.5)` | uses `orb=2.5` directly | `orb is not None` → skips the whole if-block → uses `2.5` directly | YES — the explicit-orb escape hatch is untouched |
| `find_aspect_timing(jd, b1, b2, 51.4286, dyn_coef=0.1429)` | N/A (caller computed orb) | NEW: derives orb internally | NEW behaviour, additive only |

- The static path (`orb=None, dyn_coef=None`) executes byte-identical code → no
  test churn, no coverage gap on the existing branch.
- The `orb=<float>` escape hatch is checked FIRST (`if orb is None:`), so passing
  an explicit orb still short-circuits regardless of `dyn_coef`. (Define
  precedence: explicit `orb` wins over `dyn_coef`; document it. Optionally raise
  if BOTH `orb` and `dyn_coef` are given — see §4-C.)
- 100% coverage: the new `if dyn_coef is not None` branch needs a test that
  passes a `dyn_coef` and asserts the derived orb equals
  `(bodies['orb'][b1]+bodies['orb'][b2])/2 * dyn_coef` (and equals what
  `calculate_aspects` uses for the same row — cross-check). The `both-given`
  guard (if added) needs its own test.

### 3.5 Docstring update

Replace the "compute it yourself" instruction (`calculator.py:592-593`) with the
new `dyn_coef` parameter doc, cross-referencing `generate_harmonic_aspects` and
noting `coef = k/h`. Keep numpydoc-clean (interrogate/numpydoc gates are
blocking).

---

## 4. Open design choices for the user

Each is a real fork; recommendation given, but the user decides.

**A. Combination grammar scope (ASP-F1).**
- *Tight (recommended for v1.5):* presets stay standalone; the comma-list branch
  accepts index tokens AND `h<N>` tokens (`0,4,h7`, `h7,h11`). No preset-in-list.
  Smallest diff, reuses the line-84 split, one new per-token regex.
- *Rich:* also allow `traditional,h7` (preset + harmonics). Needs preset-union
  rules; more surface, more fixtures.
- **Recommendation:** ship Tight in v1.5; defer preset-mix.

**B. Traditional-name docs table (ASP-F2).**
- Ship a docs-only reference mapping `H5-1≡quintile`, `H5-2≡biquintile`,
  `H7-1≡septile`, `H9-1≡novile`, `H9-2≡binovile`, `H9-4≡quadnovile`, etc.?
- **Recommendation:** YES as DOCS ONLY (human aid). The emitted `name` bytes stay
  `H{h}-{k}`. Do not put traditional names in the structured array.

**C. `find_aspect_timing` ergonomics + precedence (ASP-F3).**
- Add the `dyn_coef_from_row` helper? **Recommend YES.**
- If both `orb` and `dyn_coef` are passed: silently let `orb` win, OR raise
  `ValueError("pass orb or dyn_coef, not both")`? **Recommend RAISE** — it is a
  caller bug, and a clear error beats silent precedence. (Costs one tested
  branch; cheap under the 100% gate.)

**D. Header label for harmonic invocations (ASP-F1 / byte-stability).**
- `_preset_label_for_mask` returns `custom` for any non-preset mask. For
  `--harmonics h7` the resolved-config header should say something like
  `# Aspect set: h7` (or `h7,h11`). **Recommendation:** thread the original
  harmonic token(s) into the header label rather than relying on the mask
  (the mask cannot encode the dynamic channel). Pin the new header text in the
  new fixture.

---

## 5. Sources / ecosystem references

Ecosystem check was used ONLY to validate the `h<N>` syntax idiom and the
traditional-name question (ASP-F2 §2.2). Confidence MEDIUM (community/astrology
sources, multiple agree); it does not drive the internal-API recommendations
(those are HIGH, grounded in the verified code).

- Harmonic-number → aspect-name convention (H5=quintile 72°, H7=septile 51.4°,
  H9=novile 40°): The Mountain Astrologer, Astrodienst, Augurine (multiple
  sources agree). Confirms "H*n*" is the recognised idiom, supporting lowercase
  `h7` as the CLI token and `H{h}-{k}` as the generator naming scheme.
  - https://mountainastrologer.com/harmonic-charts/
  - https://www.astro.com/astrology/in_harmon_e.htm
  - https://www.augurine.com/learn/harmonic-charts

Internal code (HIGH — verified this session):
- `ketu/aspects/harmonics.py:118,196,204-208` (generator, range, naming)
- `ketu/cli/harmonics_spec.py:43,75,84,104-114` (parse branches + bare-int rejection)
- `ketu/aspects/calculator.py:56-59,81-82,119,180-226,568-651,654-768`
  (`_normalize_dynamic_specs`, `get_orb`, `calculate_aspects` dynamic orb,
  `find_aspect_timing`, `find_aspects_between_dates` synthetic-name recovery)
- `ketu/cli/aspects_cmd.py:40-127` and `ketu/cli/parser.py:85-97`
  (command-layer mask consumption, `--harmonics` wiring)
- `tests/cli/test_v1_1_reference_byte_stable.py`,
  `tests/cli/test_harmonics_spec.py` (byte-stability + parse tests)
- Boundary behaviour verified live: `generate_harmonic_aspects(h)` for
  h ∈ {2,3,4,5,6,7,9,12} → exactly `h//2` rows, even-h last row folds to 180°.
