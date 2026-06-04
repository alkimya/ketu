# Phase 36: Declination Aspects Core - Context

**Gathered:** 2026-06-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Add `find_declination_aspects` as a pure-NumPy companion function that detects
**parallels** (δ₁≈δ₂, same non-zero hemisphere) and **contra-parallels**
(δ₁≈−δ₂, opposite non-zero hemispheres) between all 14 bodies of a natal chart,
consuming `CHART_DTYPE["body_decl"]` (shipped in v1.5).

**Fixed by scope + research brief (do NOT re-decide):**
- Signed-δ definitions: parallel `sign(δ₁)==sign(δ₂)≠0 ∧ |δ₁−δ₂| ≤ orb`;
  contra `sign(δ₁)≠sign(δ₂) ∧ both≠0 ∧ |δ₁+δ₂| ≤ orb`.
- Orb formula `max((orb_b1+orb_b2)/2 × DECLA_COEF, MIN_DECL_ORB)` with
  `DECLA_COEF=1/12`, `MIN_DECL_ORB=0.5°` (Sun/Moon → 1.0°, Rahu/Lilith → 0.5°).
- Detection is in-orb boolean ONLY (no applying/separating, no timing, no synastry,
  no CLI surface — all deferred DECLA-F1..F4).
- The four research pitfalls are REQUIRED test cases (sign conflation, orb inflation,
  zero-sign trap, MIN_DECL_ORB floor).
- `CHART_DTYPE` stays byte-identical (companion function, no dtype field, no ratchet
  break, no Kala impact); frozen 14-row `core.aspects` table + V1/V13 sha256
  fingerprints unchanged; 100% coverage + mypy `--strict` clean maintained.

This phase clarifies the **API shape** only. Algorithm, formula, pitfalls and
symbol conventions are already locked (see `.planning/research/DECLINATION_ASPECTS.md`).

</domain>

<decisions>
## Implementation Decisions

### Scalar return shape (`find_declination_aspects`)
- Returns a **single unified structured array** of `DECLA_ASPECT_DTYPE` — one row
  per detected aspect, P and CP mixed and distinguished by the `kind` field
  (matches ROADMAP success criterion #1 and the `SYNASTRY_DTYPE` precedent).
  NOT a `(parallels, contras)` tuple — the §3.1 brief sketch is superseded.
- **Row ordering:** by `(body1, body2)` ascending (upper-triangle natural order,
  `np.triu_indices`). Deterministic and reproducible — easy to test, stable for
  equal gaps.
- **Empty result:** `np.empty(0, dtype=DECLA_ASPECT_DTYPE)` (never `None`) — uniform
  return type, iterable without a guard, ML/Kala-friendly.
- `body1 < body2` always (upper triangle, no duplicate pairs, no self-pairs).

### `DECLA_ASPECT_DTYPE` (5 fields)
```python
DECLA_ASPECT_DTYPE = np.dtype([
    ("body1", "i1"),   # index into core.bodies (0-13), body1 < body2
    ("body2", "i1"),
    ("kind",  "U2"),   # "P" (parallel) or "CP" (contra-parallel)
    ("gap",   "f8"),   # |δ₁−δ₂| for P, |δ₁+δ₂| for CP, degrees
    ("orb",   "f8"),   # derived orb limit used for this pair, degrees
])
```
- `body1`/`body2` are **`i1`** — consistent with `synastry`'s `body_a`/`body_b`
  (indices 0-13 fit), NOT the `i4` from the brief §4.1 sketch.
- `kind` stores **text `"P"` / `"CP"`** (`U2`), per Solar Fire / Astrodienst
  convention (brief §6.2) — readable in raw array dumps, no lookup table needed.
- Keep **both `gap` and `orb`** (5 fields) — self-describing result; the caller can
  read the margin (`orb − gap`) without recomputing the formula.
- **No symbol field.** The `//` / `#` glyphs are a doc/display convention (DECLA-05),
  not engine data — kept out of the dtype to avoid a double source of truth. A
  consumer maps `kind → symbol` at display time.

### Batch path (vectorized `(S,14) → (S,91)`)
- A **separate dedicated function** for the batch path — `find_declination_aspects`
  stays scalar (returns the structured array). The batch function returns boolean
  masks, not per-chart structured arrays. Two clean contracts, no return-type
  polymorphism (avoids the mypy/typing trap of one function returning different
  shapes by input ndim).
- Batch returns **boolean masks of shape `(S, 91)`** for parallel and contra over
  the fixed upper-triangle 91 pairs, plus the pair indices `idx_i`/`idx_j` `(91,)`,
  the per-pair `orb_pairs` `(91,)`, and the `gap` `(S, 91)`. Pure NumPy broadcasting
  via the precomputed 14×14 orb matrix — **no Python loop over bodies in the hot
  path** (ROADMAP success criterion #4). NOT a list of per-chart structured arrays
  (that would reintroduce the S-loop the criterion forbids).
- **Container = a typed `NamedTuple`** (Claude's discretion confirmed) — named,
  immutable, mypy-`--strict`-friendly, self-documenting, pure-stdlib. Cleaner than
  the ad-hoc `dict` of the brief §3.2.

### Location & exposure
- New dedicated sub-package **`ketu/declination/`** following the `synastry` /
  `composite` / `returns` / `parts` precedent:
  - `core.py` — `DECLA_ASPECT_DTYPE`, `DECLA_COEF`, `MIN_DECL_ORB`, the 14×14 orb
    matrix.
  - `api.py` — `find_declination_aspects` (scalar) + the batch function.
  - `__init__.py` — re-exports the public names of the sub-package.
- Scalar function name = **`find_declination_aspects`** (verbatim from scope, brief,
  and ROADMAP success criteria — consistent with `find_aspect_timing` /
  `calculate_synastry`).
- **Sub-module exposure only**: `ketu.declination.find_declination_aspects`. The
  top-level `ketu/__init__.py` `__all__` stays minimal (as it is today — synastry,
  parts, returns are all NOT re-exported at top level). No new top-level export.
- NOT placed inside `ketu/aspects/` — that sub-package carries the frozen longitude
  table + harmonics; keeping the δ-axis isolated protects the `core.aspects`
  byte-identical contract.

### Claude's Discretion
- The exact `NamedTuple` field names/order for the batch return (follow the brief's
  intent: parallel/contra masks, gap, idx_i, idx_j, orb_pairs).
- The exact name of the batch function (e.g. `declination_aspect_masks` or similar),
  as long as it is clearly distinct from the scalar `find_declination_aspects`.
- Whether the 14×14 orb matrix is a module-level constant vs lazily built (it is O(1)
  either way).
- Internal helper structure (`_decl_orb`, sign handling) — algorithm is fixed, layout
  is Claude's.

</decisions>

<specifics>
## Specific Ideas

- The closest existing analog is `ketu/synastry/` — a companion that detects aspects
  between bodies and emits a structured array (`SYNASTRY_DTYPE`). Mirror its layout:
  `core.py` (dtype + body-count constant) + `api.py` (the detection function) +
  `__init__.py` (re-export). Reuse `i1` for body indices to stay consistent with it.
- Regression fixtures should be derived from real astronomical events the way v1.4
  built Chebyshev oracles — e.g. a summer-solstice Sun/inner-planet parallel near
  2000-06-21, and a Moon-OOB parallel/contra found by scanning the v1.5 declination
  oracle infrastructure (brief §7 "Known Test-Case Seeds").

</specifics>

<deferred>
## Deferred Ideas

- **Applying/separating detection** on the δ axis (DECLA-F1) — computable via v1.5
  `declination_velocity`, but no mainstream source reports it; out of v1.6.
- **Exact-crossing timing** for declination aspects (DECLA-F2) — achievable with the
  `aspect_windows.py` bisection pattern; not expected by Kala at this milestone.
- **δ synastry** (inter-chart parallels/contras, DECLA-F3) — out of scope.
- **Dedicated CLI surface** for declination aspects (DECLA-F4) — out of scope.
- **`HARMF-01`** (rich `--harmonics h7,h11 / traditional,h7` grammar) — explicitly
  deferred out of v1.6; v1.6 ≠ "DECLA + HARMF-01".
- **Codeclination** (Boehrer's 23°27′ mirror) — a separate interpretive technique,
  not a detection aspect; do NOT implement.
- **"Both OOB" annotation** on parallels — interpretive delineation, not a detection
  flag; the caller can compose `is_out_of_bounds` with the aspect output if wanted.

</deferred>

---

*Phase: 36-declination-aspects-core*
*Context gathered: 2026-06-04*
