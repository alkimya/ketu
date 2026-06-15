# Phase 38: Fictitious-Point Orbs Engine - Context

**Gathered:** 2026-06-15
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase makes the three fictitious points — **Rahu (id 10), Ketu (id 11), Lilith (id 12)** — participate in
aspect detection by giving them a **2° orb** (was `0°`), and suppresses the one tautological artefact that a
non-zero node orb creates: the **intra-chart Rahu↔Ketu Opposition** (the nodes are 180° apart by construction).
The full test suite — including the synastry orb oracles and the ~40 files that reference the three points — must
be green against deliberately rewritten oracles, with 100% coverage and `mypy --strict` clean.

**Locked WHAT (from REQUIREMENTS.md ORB-01/02/03 — do not re-litigate):**
- Single-source edit: `core.bodies` rows 10/11/12 `orb` field `0 → 2`. All consumers inherit data-driven
  (`get_orb`, `synastry_orb_limit`, cycles, composite, CLI) — no per-consumer orb edits.
- Filter targets BOTH conditions simultaneously: `(body1, body2) == (Rahu, Ketu)` AND `aspect == Opposition`.
  Rahu and Ketu stay FULLY active for every other aspect and every other pair.
- Synastry is IN SCOPE: orb-limit oracles rewritten, full ~40-file regression sweep, every changed detection
  deliberately pinned (no silent oracle update).

**Out of scope (REQUIREMENTS.md):** configurable per-call point orb override; filtering any other pair; changing
planet orbs (Sun..Chiron stay frozen); Rahu UI work; new bodies; a patch release (must be MINOR 1.7.0). Docs +
release belong to **Phase 39**, not here.

</domain>

<decisions>
## Implementation Decisions

### ORB-02 filter placement
- **D-01:** The suppression rule lives in **one shared pure helper** (e.g.
  `_is_tautological_node_opposition(b1, b2, i_asp) -> bool`), defined once and CALLED from every path that must
  filter. Single source of truth for the rule — no inlined duplication of the `(10,11) AND Opposition` condition,
  no drift risk. The helper gets a dedicated unit test; each path gets an integration test. (Rejected: inline guard
  per path — duplicates the rule; post-detection result-array scrub — emit-then-remove, and every API must remember
  to call it.)
- **D-02:** In the natal vectorized engine, the helper attaches inside the shared core `_detect_aspects_for_date`
  ([ketu/aspects/calculator.py](../../../ketu/aspects/calculator.py)) — the natural chokepoint used by BOTH
  `calculate_aspects_vectorized` and `calculate_aspects_batch`. Both emit sites (static loop + dynamic loop) must
  honour the helper so the artefact never reaches results via either path. Canonical body IDs are `Rahu=10, Ketu=11`
  and canonical `Opposition` index is **13** (last row of `core.aspects`) — the helper keys on the canonical i_asp,
  not on the selected-subset position `k`.

### Scalar get_aspect coverage
- **D-03:** The scalar `get_aspect(jdate, body1, body2)` ([ketu/aspects/calculator.py](../../../ketu/aspects/calculator.py))
  **also filters** — it calls the same shared helper and returns `None` for `(Rahu, Ketu)` + Opposition. Goes one
  step beyond REQUIREMENTS' named surface (vectorized + synastry) for **consistency**: no public Ketu path ever emits
  the tautological artefact, so the same pair never disagrees between the scalar and vectorized paths. Cost is near
  zero (helper already written) plus one dedicated scalar test. `get_aspect` normalizes `body1 > body2` by swapping,
  so the helper must be order-insensitive (or be called after the swap with the canonical `(10, 11)` order).

### ORB-02 filter scope — natal only, NOT synastry
- **D-04:** The filter is **natal-engine only**. It targets the INTRA-chart tautology: within one chart Rahu and
  Ketu are 180° apart by construction. In **synastry** the two points come from two independent charts
  (Rahu_A vs Ketu_B at independent longitudes) — that opposition is **real relational data**, NOT tautological, and
  is KEPT. The synastry engine ([ketu/synastry/api.py](../../../ketu/synastry/api.py)) has its OWN detection loop
  (it does not call `_detect_aspects_for_date`); that loop **does not call the suppression helper**.
- **D-05:** Consequence for ORB-03: the synastry oracle rewrite is purely about the **new 2° orb math**
  (orb-limit values flipping from `0.0` to non-zero), NOT about adding any Rahu↔Ketu suppression. Self-synastry
  (A vs A, the idempotent case) is also NOT filtered — keeping it simple and matching D-04 (no chart-identity-dependent
  branching).

### Idempotent self-pair oracle (test_modes_idempotent.py)
- **D-06:** The rewritten `tests/synastry/test_modes_idempotent.py` **keeps its existing diagonal invariants
  unchanged**: 16 self-pair rows, all conjunctions (`aspect_type == 0`), emitted `|orb| < 1e-6`. These invariants
  genuinely do NOT change at orb 2° — on a self-pair `dist == 0`, so the emitted orb (delta `= -dist`) stays `0`,
  and the now-non-zero orb_limit only makes Rahu/Ketu/Lilith self-pairs MORE reliably detectable (reinforces the
  "always conjunction" invariant). No new assertion needed in THIS file.
- **D-07:** The orb-limit behaviour change (Rahu/Ketu/Lilith self-pair `synastry_orb_limit` flipping `0.0 → 1.0`,
  i.e. `(2+2)/2 × 1 × 0.5`) is pinned deliberately in `tests/synastry/test_orbs.py` — the dedicated home for
  orb-limit values — NOT in the idempotent test. This satisfies ORB-03's "no silent change" mandate without
  conflating the two test files' responsibilities. Concretely: `test_orbs.py` oracles that today assert
  `synastry_orb_limit(10,10,0) == 0.0` / `(11,11,0) == 0.0` / `(12,12,0) == 0.0` must be rewritten to `== 1.0`,
  and any point↔planet / point↔point synastry oracle recomputed at the new orb.

### Claude's Discretion
- The exact regression-sweep strategy for the ~40 files referencing Rahu/Ketu/Lilith (which files, ordering,
  whether to split into sub-plans) is the planner's call — the locked constraint is only that EVERY changed
  detection is deliberately pinned, never silently accepted, and the final `pytest tests/` is 0 failures /
  100% coverage / `mypy --strict` clean.
- Helper naming, signature, and module location (calculator.py vs a small shared module) are discretionary so long
  as D-01's single-source-of-truth property holds and it is unit-tested in isolation.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — ORB-01 / ORB-02 / ORB-03 definitions, the orb-formula background, the Out-of-Scope
  table (no per-call override, no other-pair filtering, planet orbs frozen).
- `.planning/ROADMAP.md` §"Phase 38: Fictitious-Point Orbs Engine" — goal + the four Success Criteria the verifier
  will check against.

### Source of truth — orb value (ORB-01)
- `ketu/core.py` (`bodies` table, rows `Rahu`/`Ketu`/`Lilith` ~lines 81-83) — the SINGLE edit site: `orb` field
  `0 → 2`. Dtype is `("orb", "f4")`. This is the only place orbs are defined; everything else reads it.

### Source of truth — orb formula & natal detection (ORB-02, scalar)
- `ketu/aspects/calculator.py` — `get_orb` (formula `(orbs[b1]+orbs[b2])/2 * coef[asp]`), the shared core
  `_detect_aspects_for_date` (two emit sites: static + dynamic loops; the natal vectorized chokepoint), and the
  scalar `get_aspect` (must also filter per D-03). Canonical `Opposition` = i_asp 13.

### Synastry (ORB-03 oracle rewrite, D-04/D-05)
- `ketu/synastry/orbs.py` — `synastry_orb_limit` reuses the natal formula × `SYNASTRY_FACTOR (0.5)`; `_BODY_ORBS_16`
  mirrors `core.bodies["orb"]` at indices 0..13, so the 2° edit propagates automatically (no edit here).
- `ketu/synastry/api.py` — `calculate_synastry`'s OWN detection loop (independent of `_detect_aspects_for_date`);
  per D-04 it does NOT call the suppression helper.
- `tests/synastry/test_orbs.py` — oracles `synastry_orb_limit(10,10,0)`/`(11,11,0)`/`(12,12,0)` rewritten `0.0 → 1.0`
  (D-07); recompute any point-involving orb-limit oracle at the new value.
- `tests/synastry/test_modes_idempotent.py` — diagonal invariants kept unchanged (D-06); 16 self-pairs, all
  conjunctions, `|orb| < 1e-6`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Single-source `core.bodies` table:** ORB-01 is genuinely a one-field edit on three rows; `get_orb`,
  `synastry_orb_limit`/`_BODY_ORBS_16`, cycles, composite, and CLI all read this table data-driven.
- **Shared natal detection core `_detect_aspects_for_date`:** one function serves both `calculate_aspects_vectorized`
  and `calculate_aspects_batch`, so the D-02 helper-call there covers the whole natal vectorized surface at once.
- **`synastry_orb_limit` is a multiplicative transform of the natal formula**, NOT a parallel orb table — so the 2°
  change flows into synastry orb limits automatically (only the test ORACLES change, not the synastry orb code).

### Established Patterns
- **No filter exists anywhere yet** (grep confirms): ORB-02 is brand-new logic. This makes the shared-helper design
  (D-01) cheap to introduce cleanly rather than retrofitting.
- **Canonical i_asp contract:** the engine always emits the canonical 0-13 index into `core.aspects` regardless of
  the selected subset (Kala contract). The helper must key on canonical i_asp (Opposition = 13), not the loop
  position `k`.
- **Two independent detection loops:** natal (`calculator.py`) and synastry (`api.py`) are separate by design;
  D-04 deliberately keeps them divergent on the filter (natal filters, synastry does not).
- **100% coverage + mypy --strict gates** are hard CI gates (v1.6 baseline: 1654 tests green). New helper + filter
  code must be fully covered, including the negative branches (e.g. Rahu↔Ketu conjunction still detected,
  Rahu↔Sun opposition still detected).

### Integration Points
- `core.bodies["orb"]` edit → propagates to `get_orb`, `synastry._BODY_ORBS_16`, cycles, composite, CLI.
- Shared helper → called from `_detect_aspects_for_date` (both emit sites) AND `get_aspect`; NOT called from
  `synastry/api.py`.
- Regression surface: ~40 test files reference Rahu/Ketu/Lilith; the previously-zero-orb assumption is now false
  in several of them (notably `tests/synastry/test_orbs.py`).

</code_context>

<specifics>
## Specific Ideas

- The Rahu↔Ketu Opposition is suppressed because Ketu (South Node) is the exact 180° opposite of Rahu (North Node)
  **by construction within a single chart** — a permanent, information-free fixed angle once the orb is non-zero.
  This framing (not "the nodes are noisy" but "this specific intra-chart pair is tautological") is the rationale the
  Phase 39 docs must carry, and it is precisely WHY synastry cross-pairs are NOT filtered (D-04).
- MINOR-not-patch reasoning (for Phase 39, noted here so it isn't lost): aspect RESULTS change for consumers (Kala),
  new aspects appear, so `pip install -U` is not behaviourally neutral — `orb = 0` was an intentional Abu Ma'shar /
  Al-Biruni modelling choice, not a bug, so this is not a patch fix.

</specifics>

<deferred>
## Deferred Ideas

- **Configurable per-call point orb override** (runtime override of `core.bodies`) — explicitly out of v1.7 scope
  (larger config-surface decision, no current demand). REQUIREMENTS.md Out-of-Scope table.
- **Filtering other degenerate pairs** — only Rahu↔Ketu Opposition is tautological by construction; no other point
  pair has a permanent fixed angle. Out of scope.
- **Docs (en+fr) + release v1.7.0** — ORB-04 / REL-01 belong to **Phase 39**, not this phase.

None of the four discussed areas drifted outside the phase scope — all clarified HOW to implement the locked WHAT.

</deferred>

---

*Phase: 38-fictitious-point-orbs-engine*
*Context gathered: 2026-06-15*
