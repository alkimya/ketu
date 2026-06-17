---
phase: 40-declination-speed-field-chart-api
reviewed: 2026-06-17T00:00:00Z
depth: standard
files_reviewed: 12
files_reviewed_list:
  - ketu/calculations.py
  - ketu/charts/__init__.py
  - ketu/charts/api.py
  - ketu/charts/core.py
  - ketu/composite/api.py
  - tests/charts/test_chart_helpers.py
  - tests/charts/test_compute_chart.py
  - tests/charts/test_dtype.py
  - tests/composite/test_calculate_composite.py
  - tests/returns/test_solar_return.py
  - tests/synastry/test_calculate_synastry.py
  - tests/test_declination.py
findings:
  critical: 0
  warning: 4
  info: 5
  total: 9
status: issues_found
---

# Phase 40: Code Review Report

**Reviewed:** 2026-06-17
**Depth:** standard
**Files Reviewed:** 12
**Status:** issues_found

## Summary

Phase 40 adds the `body_decl_speed` (dδ/dt, deg/day) field to `CHART_DTYPE` at
index 8 (15→16 fields), a public `DECL_STANDSTILL_EPS = 0.001` constant, a
vectorised forward-FD population in `compute_chart` (Δt=0.01), a chart-level
`is_ascending_declination_chart` classifier, and composite-path derivation via
finite difference on the composite's own frozen (λ, β). The numerical core is
sound: the FD slope reuses δ₀ correctly, the obliquity broadcast handles both
scalar (S=()) and vectorised (S=(N,)) inputs, the int8 {-1,0,+1} classification
is correct, and the composite anti-averaging discipline is genuinely enforced
(FD on frozen λ,β advanced by midpoint velocities, NOT a midpoint of parent
speeds — pinned by `test_body_decl_speed_not_parent_midpoint`). The full suite
is green (1691 passed, 100% coverage).

No blockers. The findings are robustness and maintainability concerns: a
hard-coded FD step replicated across three call sites with a load-bearing
exact-match contract, silent NaN→neutral misclassification in the helper, an
inconsistency between the composite's inline aspect loop and the vectorised
calculator's Rahu↔Ketu suppression (pre-existing but in a file under review and
now relevant because the composite path was edited in this phase), and a cluster
of stale `(13,)` docstring references that contradict the actual `(14,)` axis.

## Warnings

### WR-01: FD step `0.01` is a magic number replicated across three sites with an exact-equality contract

**File:** `ketu/charts/api.py:402,411`; `ketu/calculations.py:541`; `ketu/composite/api.py:293,308`
**Issue:** The finite-difference step `0.01` day is hard-coded independently in
(a) the scalar `declination_velocity` (`calculations.py:541`), (b) the vectorised
`compute_chart` FD block (`api.py:402` and `api.py:411`), and (c) the composite
derivation (`composite/api.py:293`). The DSPD-02 contract requires the chart
value to equal the scalar value **exactly** (`test_body_decl_speed_matches_scalar_declination_velocity_exactly`
asserts `delta == 0.0`). That exact-equality contract silently depends on three
separate literals staying byte-identical. If a future edit tunes the step in one
site (e.g. to `0.005` in `declination_velocity` for accuracy) and misses the
others, the exact-match test breaks far from the edit, and worse, `body_decl`
(δ₀) and the FD step could drift out of sync. The composite comment even
documents the coupling manually: `# verbatim from declination_velocity
(calculations.py:495-524)`.
**Fix:** Promote the step to a single shared module constant next to
`DECL_STANDSTILL_EPS` and reference it everywhere:
```python
# ketu/calculations.py
DECL_FD_STEP: float = 0.01  # forward-FD step (day) for dδ/dt; load-bearing across chart/composite
...
def declination_velocity(jdate, body):
    return (declination(jdate + DECL_FD_STEP, body) - declination(jdate, body)) / DECL_FD_STEP
```
Then import `DECL_FD_STEP` in `charts/api.py` and `composite/api.py` instead of
the literal `0.01` / `_Dt = 0.01`.

### WR-02: `is_ascending_declination_chart` silently misclassifies NaN as neutral (0)

**File:** `ketu/charts/api.py:615-619`
**Issue:** The classifier uses
`np.where(speeds > EPS, 1, np.where(speeds < -EPS, -1, 0))`. For any
`body_decl_speed == NaN`, both comparisons are `False`, so a NaN body is
classified `0` (standstill / neutral) with no warning. `compute_chart` currently
guarantees finite speeds, but the helper accepts an arbitrary `CHART_DTYPE`
array (the test suite itself constructs synthetic charts via `np.zeros`), so a
caller that hand-builds or mutates a chart and leaves a NaN will get a silently
plausible-but-wrong "neutral" answer instead of a detectable signal. Neutral and
"unknown/NaN" are physically distinct states.
**Fix:** Either propagate NaN explicitly or assert finiteness. Minimal,
behaviour-preserving for finite input:
```python
speeds = np.asarray(chart["body_decl_speed"], dtype=np.float64)
result = np.where(
    speeds > DECL_STANDSTILL_EPS, np.int8(1),
    np.where(speeds < -DECL_STANDSTILL_EPS, np.int8(-1), np.int8(0)),
).astype(np.int8)
# NaN must not masquerade as a standstill; surface it distinctly.
if np.any(~np.isfinite(speeds)):
    raise ValueError("body_decl_speed contains non-finite values; chart is malformed")
return result
```
At minimum, document in the docstring that NaN is treated as neutral so callers
are not surprised.

### WR-03: Composite inline aspect loop does NOT suppress the tautological Rahu↔Ketu opposition

**File:** `ketu/composite/api.py:383-412`
**Issue:** The vectorised aspect engine used by `compute_chart`
(`calculate_aspects_vectorized`) suppresses the always-present ~180° Rahu↔Ketu
opposition via `_is_tautological_node_opposition` (calculator.py:169/190/247/342/350,
a v1.7 behaviour). The composite's hand-inlined aspect loop reproduces the
calculator's `triu` matching algebra but omits this suppression entirely. A
composite chart will therefore record a spurious Rahu(10)↔Ketu(11) opposition in
`aspect_matrix[10,11]` / `aspect_orbs[10,11]`, whereas the natal charts produced
by `compute_chart` will not. This is an observable inconsistency between two
"intra-chart aspect" surfaces of the same package, and it diverges from the
package-wide v1.7 decision. The defect is pre-existing (the inline loop predates
v1.7), but the composite file was edited in this phase and the inline loop is the
documented divergence point ("inline loop semantically identical to the engine's
triu loop").
**Fix:** Mirror the calculator's guard in the inline loop before writing a match:
```python
from ketu.aspects.calculator import _is_tautological_node_opposition
...
if i_asp == 0:
    if dist <= pair_orb:
        ...
else:
    if aspect_angle - pair_orb <= dist <= aspect_angle + pair_orb:
        if _is_tautological_node_opposition(i, j, int(i_asp)):
            break  # suppress tautological Rahu<->Ketu opposition (v1.7 parity)
        signed_orb = aspect_angle - dist
        ...
```
(If `_is_tautological_node_opposition` is considered private, lift it to a shared
helper rather than re-implementing the index check.)

### WR-04: Stale `(13,)` axis references in docstrings/comments contradict the live `(14,)` dtype

**File:** `ketu/charts/core.py:22`; `ketu/charts/api.py:319`; `ketu/composite/api.py:33,168,239`
**Issue:** Multiple narrative/docstring sites still describe a 13-body axis,
which is wrong (the axis is `(14,)` since the v1.3 Chiron ratchet, and this very
phase relies on the 14-axis everywhere):
- `charts/core.py:22` — "the canonical 13-body axis"
- `charts/api.py:319` — "The body axis ``(13,)`` is frozen per D-08"
- `composite/api.py:33` — "``body_speeds`` ``f8`` / ``(13,)`` contract"
- `composite/api.py:168` — "``body_speeds`` must be ``f8`` shape ``(13,)``"
- `composite/api.py:239` — "vectorised over the frozen (13,) axis"

These mislead any reader/consumer about the contract (Kala indexes positionally
off these descriptions). The phase added a new field to a 14-axis dtype, so the
adjacent prose should be correct. This is doc-only but actively contradictory.
**Fix:** Replace every `(13,)` / "13-body" reference in these files with `(14,)`
/ "14-body". `composite/api.py:375` already has a stale `# shape (13,)` comment on
`_BODIES["orb"]` (the array is length 14) — fix it in the same pass (see IN-02).

## Info

### IN-01: `.astype(np.int8)` on the `np.where` result is redundant

**File:** `ketu/charts/api.py:619`
**Issue:** The nested `np.where` already returns an `int8` array because every
branch value is an `np.int8` scalar. The trailing `.astype(np.int8)` is a no-op
copy. Harmless, but it implies the dtype is otherwise uncertain.
**Fix:** Drop `.astype(np.int8)` (the test `test_dtype_is_int8` will still pass),
or keep it with a one-line comment noting it is a defensive guarantee.

### IN-02: Wrong inline shape comment on `_BODIES["orb"]`

**File:** `ketu/composite/api.py:375`
**Issue:** `body_orbs = _BODIES["orb"]  # shape (13,)` — `_BODIES` has 14 entries
(Sun..Chiron), so the array is shape `(14,)`. The loop iterates `range(_BODY_COUNT)`
= 14, so the code is correct; only the comment is wrong.
**Fix:** Change the comment to `# shape (14,)`.

### IN-03: Composite re-fetches β-rate from the ephemeris while λ-rate comes from the stored chart — undocumented asymmetry

**File:** `ketu/composite/api.py:283-297`
**Issue:** The composite advances λ by `out["body_speeds"]` (the stored,
already-averaged composite longitude speed) but advances β by `_body_lat_speeds`,
which is **re-fetched** from `calc_planet_position_batch(...)[:,4]` at each
parent's jd and then averaged locally. Both are midpoint rates, so the result is
self-consistent, but the two rates are sourced from different places (one stored,
one recomputed). A future edit that changes how `body_speeds` is populated
upstream would silently desynchronise the λ and β advancement bases. The comment
explains *why* β is re-fetched (lat_speed isn't stored) but not that λ
deliberately uses the stored field.
**Fix:** Add a one-line comment at line 294 noting λ-rate is read from the stored
`body_speeds` (midpoint) while β-rate is re-derived because `lat_speed` is not a
`CHART_DTYPE` field — making the asymmetry intentional and documented.

### IN-04: DSPD-02 exact-equality contract depends on an undocumented scalar/vectorised ephemeris invariant

**File:** `ketu/charts/api.py:396-411`; `tests/charts/test_compute_chart.py:337-357`
**Issue:** `test_body_decl_speed_matches_scalar_declination_velocity_exactly`
asserts `delta == 0.0` between the chart FD (which uses
`calc_planet_position_batch` / the `.vectorized()` strategy) and the scalar
`declination_velocity` (which uses `calc_planet_position` / the scalar strategy).
This exact equality only holds if the scalar and vectorised ephemeris strategies
produce bit-identical λ/β for a single date. That invariant is real today (the
suite is green) but is not stated anywhere near the FD code, so a legitimate
future optimisation of either strategy could break a test whose failure mode
points at the FD rather than at the ephemeris.
**Fix:** Add a code comment at `api.py:411` noting the exact-equality contract
relies on scalar/vectorised strategy bit-parity, and reference that invariant
from the test, so a strategy-level change is traced back correctly.

### IN-05: `compute_chart` body-position FD doubles the ephemeris evaluation

**File:** `ketu/charts/api.py:403`
**Issue:** `_vectorised_body_properties(_jd_b1)` recomputes all 14 bodies at
`jd + 0.01`, doubling the per-chart body-position cost. This is correct (the FD
needs real positions at jd+Δt, matching the scalar) and performance is explicitly
out of v1 review scope; flagged only so the cost is a known, deliberate trade-off
rather than an accident.
**Fix:** None required for correctness. If batch sizes grow, consider a single
fused 2-point evaluation; not actionable now.

---

_Reviewed: 2026-06-17_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
