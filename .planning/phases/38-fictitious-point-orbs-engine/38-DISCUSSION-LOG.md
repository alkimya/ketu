# Phase 38: Fictitious-Point Orbs Engine - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-15
**Phase:** 38-fictitious-point-orbs-engine
**Areas discussed:** ORB-02 filter placement, Scalar get_aspect coverage, Filter scope in synastry, Idempotent self-pair oracle

---

## ORB-02 filter placement

| Option | Description | Selected |
|--------|-------------|----------|
| Helper partagé réutilisé | One pure function defined once, called from every path that must filter (vectorized, scalar, synastry). Single source of truth; dedicated helper test + per-path integration tests. | ✓ |
| Garde inline par chemin | Inline `(b1,b2)==(10,11) and asp==Opposition` in each loop, no helper. Simpler/local but duplicates the rule in 2-3 places; drift risk. | |
| Filtre post-détection | Detect normally then scrub the Rahu↔Ketu Opposition row(s) from the final result array. Centralized but emit-then-remove; each API must remember to call it. | |

**User's choice:** Helper partagé réutilisé
**Notes:** One source of truth for the rule; cascades into the other three areas (each filtering path calls the same helper).

---

## Scalar get_aspect coverage

| Option | Description | Selected |
|--------|-------------|----------|
| Oui, get_aspect filtre aussi | Scalar `get_aspect` calls the shared helper and returns `None` for (Rahu,Ketu)+Opposition. Full consistency: no public Ketu path emits the artefact. Near-zero cost + one scalar test. | ✓ |
| Non, scalaire non filtré | `get_aspect` left as-is, may return the Rahu↔Ketu Opposition. Strictly matches REQUIREMENTS' named surface (vectorized+synastry only) but creates a scalar-vs-vectorized inconsistency for the same pair. | |

**User's choice:** Oui, get_aspect filtre aussi
**Notes:** Consistency across all public paths; helper already written so the extension is one call.

---

## Filter scope in synastry

| Option | Description | Selected |
|--------|-------------|----------|
| Filtre natal seulement (pas en synastrie) | Filter targets the intra-chart tautology only. In cross-synastry Rahu_A↔Ketu_B comes from independent charts → real relational data, kept. Synastry loop does NOT call the suppression helper. | ✓ |
| Filtre aussi en synastrie | Suppress Rahu↔Ketu Opposition in synastry results too, by symmetry — but this discards real relational data (the two points are not opposed by construction across two people). | |
| Filtrer seulement la self-synastrie | Filter only A-vs-A self-synastry where Rahu_A↔Ketu_A is again tautological; keep A-vs-B active. More precise but adds chart-identity-dependent branching. | |

**User's choice:** Filtre natal seulement (pas en synastrie)
**Notes:** Astronomically correct — the tautology is intra-chart only. Means the synastry oracle rewrite is purely about the new 2° orb math, not about adding suppression.

---

## Idempotent self-pair oracle

| Option | Description | Selected |
|--------|-------------|----------|
| Garder invariants, le delta reste 0 | Keep the existing diagonal invariants (16 rows, all conjunctions, \|orb\|<1e-6) — they genuinely don't change at orb 2° (dist=0 on self-pair → delta=0). Non-zero orb_limit only reinforces "always conjunction". | ✓ |
| Épingler aussi le nouvel orb_limit | Additionally assert point self-pair orb_limit = 1.0 (was 0.0) in this file, to pin the behaviour change deliberately. | |

**User's choice:** Garder invariants, le delta reste 0
**Notes:** The orb_limit change (0.0 → 1.0 for point self-pairs) is pinned in `tests/synastry/test_orbs.py` instead — the dedicated home for orb-limit values — so ORB-03's "no silent change" mandate is satisfied without conflating the two test files.

---

## Claude's Discretion

- Regression-sweep strategy for the ~40 files referencing Rahu/Ketu/Lilith (which files, ordering, sub-plan split) — planner's call; only constraint is deliberate pinning of every changed detection + final green/100%/mypy-strict.
- Shared-helper naming, signature, and module location — discretionary as long as it stays single-source-of-truth and unit-tested in isolation.

## Deferred Ideas

- Configurable per-call point orb override — out of v1.7 scope (REQUIREMENTS.md).
- Filtering other degenerate pairs — none other is tautological by construction; out of scope.
- Docs (en+fr) + release v1.7.0 — ORB-04 / REL-01, belong to Phase 39.
