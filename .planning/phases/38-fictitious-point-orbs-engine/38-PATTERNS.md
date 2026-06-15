# Phase 38: Fictitious-Point Orbs Engine - Pattern Map

**Mapped:** 2026-06-15
**Files analyzed:** 6 source/test targets (+ ~40-file regression sweep, planner-scoped)
**Analogs found:** 6 / 6 (all patterns exist in-repo)

This phase has **no new module**. The single new code artefact is a pure helper
`_is_tautological_node_opposition` added inside an existing module
(`ketu/aspects/calculator.py`). Everything else is a data edit, helper-call
insertions at known chokepoints, and oracle rewrites. Pure NumPy, type hints
everywhere, 100% coverage + `mypy --strict` are hard gates.

## File Classification

| File | Role | Data Flow | Change Kind | Closest Analog | Match Quality |
|------|------|-----------|-------------|----------------|---------------|
| `ketu/core.py` | model (data table) | transform (source-of-truth) | ORB-01 single-field edit (3 rows) | self (sibling rows) | exact |
| `ketu/aspects/calculator.py` | service (detection engine) | transform/CRUD-of-rows | NEW pure helper (D-01) + 3 call sites (D-02 ×2, D-03 ×1) | `get_orb` (sibling pure helper) | exact |
| `ketu/synastry/orbs.py` | service (orb formula) | transform | NO edit (data-driven inherit) | n/a | n/a |
| `ketu/synastry/api.py` | service (synastry engine) | transform | NO edit (D-04 — does NOT call helper) | n/a | n/a |
| `tests/synastry/test_orbs.py` | test | data assertions | oracle rewrite 0.0→1.0 (D-07) | self (existing oracle rows) | exact |
| `tests/synastry/test_modes_idempotent.py` | test | property/parametrized | UNCHANGED invariants (D-06) | self | exact |
| NEW unit + integration tests | test | parametrized | new helper + 3 path tests | `tests/test_aspects_vectorization.py`, `test_orbs.py` | role-match |
| ~40 regression files | test | mixed | deliberate re-pin (planner-scoped) | n/a | n/a |

## Pattern Assignments

### `ketu/core.py` (model, ORB-01 edit site)

**Analog:** the sibling rows in the same `bodies` array (no external analog needed).

**Exact edit site** — `bodies` array, rows id 10/11/12, the `orb` field is the
**3rd tuple position** (dtype `("orb", "f4")`). Lines 81-83:

```python
        ("Rahu", 10, 0, -0.052954),  # Mean North Node (regression ~360°/18.6yr)
        ("Ketu", 11, 0, -0.052954),  # Mean South Node (opposite of Rahu)
        ("Lilith", 12, 0, 0.113),  # Mean Apogee (Black Moon)
```

Change the `0` → `2` in each of these three rows. **Do not touch** Chiron (id 13,
orb 4, line 84) or any planet row. dtype declared at line 86:
`dtype=[("name", "S12"), ("id", "i4"), ("orb", "f4"), ("speed", "f4")]`.

This is the single source of truth — `get_orb`, `synastry._BODY_ORBS_16`, cycles,
composite, CLI all read `bodies["orb"]` data-driven, so no other source edit.

---

### `ketu/aspects/calculator.py` (service — NEW helper + 3 call sites)

**Analog for the helper shape:** `get_orb` (lines 148-167) — a small module-level
pure function, full type hints, numpydoc docstring (mandatory for the numpydoc
gate). Copy that structure exactly:

```python
def get_orb(body1: int, body2: int, asp: int) -> float:
    """
    Calculate the orb tolerance for two bodies and an aspect.
    ...numpydoc Parameters / Returns...
    """
    orbs, coef = bodies["orb"], _CORE_ASPECTS["coef"]
    return (orbs[body1] + orbs[body2]) / 2 * coef[asp]
```

**New helper signature (D-01, D-02, D-03).** Must be **order-insensitive** because
`get_aspect` swaps `body1 > body2` (so it may pass either order), while
`_detect_aspects_for_date` always emits canonical ascending `(b1, b2)` from
`np.triu_indices`. Canonical IDs: `Rahu=10, Ketu=11`; canonical `Opposition`
i_asp = **13** (last row of `core.aspects`). Define module-level constants for
these (no magic numbers — keeps coverage/intent clear):

```python
_RAHU_ID = 10
_KETU_ID = 11
_OPPOSITION_IASP = 13  # canonical index into core.aspects (last row)


def _is_tautological_node_opposition(body1: int, body2: int, i_asp: int) -> bool:
    """
    True iff this is the intra-chart Rahu↔Ketu Opposition (tautological).
    ...numpydoc...
    """
    if i_asp != _OPPOSITION_IASP:
        return False
    pair = (int(body1), int(body2))
    return pair == (_RAHU_ID, _KETU_ID) or pair == (_KETU_ID, _RAHU_ID)
```

**Call site 1 — `_detect_aspects_for_date` static emit loop** (D-02). Existing emit
block, lines 126-132:

```python
        if np.any(in_orb):
            for i, idx in enumerate(np.where(in_orb)[0]):
                pair = (body1_ids[idx], body2_ids[idx])
                if pair not in matched_pairs:
                    # Emit canonical i_asp (NOT k) to preserve Kala contract.
                    results.append((body1_ids[idx], body2_ids[idx], i_asp, orb_values[i]))
                    matched_pairs.add(pair)
```

Guard the `results.append` with the helper keyed on the **canonical `i_asp`** (not
the loop position `k`). Note the suppressed pair must STILL be added to
`matched_pairs` so a later aspect cannot re-emit for it — verify the chosen
placement against the first-match-wins contract (suppress emission, but the pair
is already opposition-matched). The planner must decide whether suppression also
blocks the slot or lets a lower-priority aspect fill it; the locked WHAT only
removes the tautological Opposition, and Opposition is i_asp 13 (last static row),
so in practice no other static aspect competes.

**Call site 2 — dynamic emit loop** (D-02). Lines 138-143 — dynamic rows carry
`i_asp = -2`, never 13, so the helper returns `False` there; the guard is harmless
but should be present for uniformity per D-01 single-source. (Document that dynamic
rows are structurally exempt.)

**Call site 3 — scalar `get_aspect`** (D-03). Lines 188-197. `body1 > body2` swap
happens at line 188-189, so call the helper AFTER the swap (canonical order) or
rely on its order-insensitivity:

```python
    if body1 > body2:
        body1, body2 = body2, body1
    dist = distance(long(jdate, body1), long(jdate, body2))
    for i_asp, aspect in enumerate(_CORE_ASPECTS["angle"]):
        orb = get_orb(body1, body2, i_asp)
        if i_asp == 0 and dist <= orb:
            return body1, body2, i_asp, dist
        elif aspect - orb <= dist <= aspect + orb:
            # NEW: suppress the tautological intra-chart Rahu↔Ketu Opposition
            if _is_tautological_node_opposition(body1, body2, i_asp):
                return None
            return body1, body2, i_asp, aspect - dist
    return None
```

Add the helper to `__all__`? **No** — it is private (`_`-prefixed), so leave
`__all__` (lines 812-820) unchanged.

**Note for `calculate_aspects` (lines 200-311):** the slow scalar-loop public API
does NOT route through `_detect_aspects_for_date`. The locked surface (D-02/D-03)
is vectorized + batch + scalar `get_aspect`. The planner must decide whether
`calculate_aspects` (the non-vectorized public path) also needs the guard for
cross-path consistency — D-03's consistency rationale ("no public Ketu path emits
the artefact") argues YES; flag this explicitly so it is a deliberate decision, not
an omission. If guarded, the insertion point is the static `aspects_data.append`
at lines 286 and 290.

---

### `tests/synastry/test_orbs.py` (test — oracle rewrite, D-07)

**Analog:** the existing oracle rows in this same file. Three assertions flip
`0.0 → 1.0`. Lines 90-106:

```python
def test_synastry_orb_limit_rahu_rahu_zero_orb() -> None:
    """Rahu-Rahu conjunction == 0.0 deg ..."""
    assert synastry_orb_limit(10, 10, 0) == 0.0     # -> rewrite to 1.0

def test_synastry_orb_limit_ketu_ketu_zero_orb() -> None:
    assert synastry_orb_limit(11, 11, 0) == 0.0     # -> rewrite to 1.0

def test_synastry_orb_limit_lilith_lilith_zero_orb() -> None:
    assert synastry_orb_limit(12, 12, 0) == 0.0     # -> rewrite to 1.0
```

New value math (D-07): `(2 + 2) / 2 × coef_conj(1) × factor(0.5) = 1.0`. Rename
the tests away from `_zero_orb` (now misleading) and rewrite docstrings — they
currently assert "zero natal orb" as the rationale (lines 91-96), which is now
false. Also recompute any **point↔planet** / **point↔point** orb-limit oracle
elsewhere in the suite at the new 2° orb (e.g. a Rahu-Sun conjunction limit
becomes `(2+12)/2 × 1 × 0.5 = 3.5`). The docstring at the top of the file
(lines 1-7) cites "Rahu-Rahu = 0 deg" as a pinned ratchet — update it.

The `_BODY_ORBS_16` canonical-mirror test (lines 51-54) needs no edit: it asserts
`_BODY_ORBS_16[:14] == _BODIES["orb"]` structurally, so it tracks the new 2°
automatically (good — proves data-driven propagation).

---

### `tests/synastry/test_modes_idempotent.py` (test — UNCHANGED, D-06)

**Do NOT edit.** Diagonal invariants stay valid at orb 2°. The pinned block
(lines 107-131) asserts: 16 self-pair rows, all `aspect_type == 0` (conjunction),
`|orb| < 1e-6`. On a self-pair `dist == 0`, so emitted orb (`delta = -dist`) stays
0 regardless of orb_limit; a now-non-zero limit only reinforces detectability. The
docstring at lines 112-118 references "Rahu/Ketu/Lilith have zero natal orbs" as
the rationale — this is now stale; the planner may refresh the comment but MUST NOT
weaken the assertions. D-07 owns the orb-limit value change, not this file.

---

### NEW tests (helper unit + per-path integration)

**Analogs:**
- **Helper unit test** — pure data assertions, see `tests/synastry/test_orbs.py`
  style (one assertion per behaviour, numpydoc one-liner docstring). Cover all
  branches for 100%: `(10,11,13)→True`, `(11,10,13)→True` (order-insensitivity),
  `(10,11,0)→False` (Rahu↔Ketu conjunction still emits), `(10,0,13)→False`
  (Rahu↔Sun opposition still emits), `(10,11,-2)→False` (dynamic exempt).
- **Integration tests** — `tests/test_aspects_vectorization.py` shows the
  detection-result assertion idiom (sort by `body1, body2, i_asp`, then assert on
  fields; lines 39-43, 67-76). Pin: vectorized + batch + scalar `get_aspect` each
  drop the `(10, 11, 13)` row but keep `(10, 11, 0)` conjunction and
  `(10, 0, 13)` Rahu-Sun opposition when in orb. Use a date where the negative
  branches actually fire (a real Rahu↔Sun opposition) so the keep-branches are
  covered, not just the suppress-branch.

## Shared Patterns

### Single-source-of-truth rule (D-01)
**Source:** `get_orb` (calculator.py:148-167) — the rule lives in ONE pure
function, every consumer calls it; mirrors how `synastry_orb_limit`
(orbs.py:148-152) is "a multiplicative transform OF" `get_orb` rather than a
parallel table. Apply the same discipline to `_is_tautological_node_opposition`:
defined once, called from all natal emit paths, never inlined.

### Canonical i_asp contract (Kala)
**Source:** `_detect_aspects_for_date` comment (calculator.py:131) — "Emit
canonical i_asp (NOT k) to preserve Kala contract." The helper MUST key on
canonical `i_asp == 13`, never the selected-subset loop position `k`.
Apply to: both `_detect_aspects_for_date` call sites.

### numpydoc + type hints (hard CI gate)
**Source:** every function in calculator.py / orbs.py. Apply to: the new helper
and all new tests — full type annotations (`-> bool`, `-> None`), numpydoc
`Parameters`/`Returns`. `mypy --strict` must stay clean; cast NumPy scalars to
`int()` at the helper boundary (the `body1_ids[idx]` values are `np.int32`).

### Data-driven propagation (no per-consumer edit)
**Source:** `_BODY_ORBS_16 = _build_body_orbs_16()` (orbs.py:59-86) mirrors
`bodies["orb"]`; `get_orb` reads `bodies["orb"]` live. The ORB-01 edit flows to
synastry, cycles, composite, CLI with zero extra edits — confirm via the
regression sweep, do not add orb edits anywhere else.

## No Synastry Helper Call (D-04 / D-05)

`ketu/synastry/api.py` has its **own** detection loop (`calculate_synastry`,
the `for i_asp in selected_indices` block around lines 308-329 with its own
`in_orb`/`delta`/`matched` logic). It is intentionally independent of
`_detect_aspects_for_date` and **must NOT call** `_is_tautological_node_opposition`
— synastry Rahu_A↔Ketu_B is real relational data. Self-synastry (A vs A) is also
NOT filtered (D-05). No code edit to `api.py` or `orbs.py`.

## Regression Sweep (planner-scoped)

~31 test files (grep) reference Rahu/Ketu/Lilith or ids 10/11/12. The previously-
zero-orb assumption is now false in several. Locked constraint: EVERY changed
detection deliberately re-pinned (no silent oracle update), final
`pytest tests/` = 0 failures / 100% coverage / `mypy --strict` clean. Likely-
affected oracle/fixture families to audit first: `tests/synastry/fixtures/*.json`
+ `test_oracle.py`, `tests/composite/test_oracle.py`, `tests/declination/
test_find_aspects.py`, `tests/test_cycles_calculator.py`, `tests/charts/
test_aspect_matrix.py`, `tests/cli/fixtures/*reference_output.txt` (byte-stable
CLI snapshots will shift — new node aspects appear). Splitting the sweep into
sub-plans is the planner's call.

## Metadata

**Analog search scope:** `ketu/aspects/`, `ketu/synastry/`, `ketu/core.py`,
`tests/synastry/`, `tests/` aspect-detection tests.
**Files scanned:** core.py, calculator.py, orbs.py, api.py (partial),
test_orbs.py, test_modes_idempotent.py, test_aspects_vectorization.py.
**Pattern extraction date:** 2026-06-15
