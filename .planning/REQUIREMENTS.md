# Requirements: Ketu — v1.7 Fictitious-Point Orbs

**Defined:** 2026-06-15
**Core Value:** Cycle calculations must be correct, tested, and performant. If the math is wrong, nothing downstream matters.

## Milestone v1.7 Requirements

Requirements for the v1.7 minor release. Each maps to exactly one roadmap phase.

**Background:** Rahu (10), Ketu (11), and Lilith (12) ship with `orb = 0` in `core.bodies`
(a deliberate Abu Ma'shar / Al-Biruni modelling choice for fictitious points). Because the
aspect-orb formula is `(orbs[body1] + orbs[body2]) / 2 * coef[asp]`
([calculator.py:167](../../ketu/aspects/calculator.py)), two zero-orb points can NEVER form an
aspect (0 + 0 → 0 → only an exact-separation match), and Lilith can never aspect the nodes. The
Rahu (frontend) project surfaced this: with `orb = 0` the node/Lilith aspect grid renders empty.
v1.7 gives the three points a 2° orb so they enter aspect, and filters out the one tautological
artefact that a non-zero orb creates (Rahu↔Ketu Opposition).

### Orbs

- [x] **ORB-01**: Rahu, Ketu, and Lilith carry orb `2°` (was `0°`) in the single-source `core.bodies` table; all consumers (`get_orb`, `synastry_orb_limit`, cycles, composite, CLI) inherit the new value data-driven with no per-consumer edits. Point↔point conjunction orb = 2°; point↔planet orb = mean of the two (e.g. Rahu↔Sun = (2+12)/2 = 7°).
- [x] **ORB-02**: The aspect engine suppresses ONLY the simultaneous `(body1, body2) == (Rahu, Ketu)` AND `aspect == Opposition` detection (both conditions together) — the permanent, tautological 180° artefact (Ketu = South Node, exact opposite of Rahu by construction). Rahu and Ketu remain FULLY active for every other aspect and every other pair (Rahu↔Sun, Ketu↔Lilith, Rahu/Ketu conjunctions, etc.); the filter targets the noise pair only, not the bodies.
- [x] **ORB-03**: Synastry inherits the new point orb everywhere; the `orb = 0` oracles are rewritten to the new expected values (at least `synastry_orb_limit` cases in `tests/synastry/test_orbs.py` and the idempotent-modes oracle in `tests/synastry/test_modes_idempotent.py`), and a full regression sweep over every test that references Rahu/Ketu/Lilith (~40 files) is green. New/changed aspect detections are pinned, not silently accepted.

### Documentation

- [x] **ORB-04**: Documentation (en + fr) updated for the 2° fictitious-point orb, the Rahu↔Ketu Opposition filter and its rationale, and the MINOR-not-patch reasoning (aspect results change → Kala must opt in via a deliberate upgrade, not assume `pip install -U` is neutral). FR `.po` translated and `.mo` recompiled (no English fallback).

### Release

- [x] **REL-01**: `ketu == 1.7.0` shipped to PyPI via OIDC trusted publishing — version bumped in all source-of-truth files, dated `[1.7.0]` changelog (EN + FR) + UPGRADING v1.6→v1.7 documenting the point-orb behaviour change, both `origin/main` and the `v1.7.0` tag pushed, a human go/no-go relecture-validation honoured before any irreversible action, and a post-publish fresh-venv smoke FROM PyPI confirming the new point orb produces ≥1 node/Lilith aspect and the Rahu↔Ketu Opposition is absent (and no `pyswisseph` at runtime).

## Future Requirements

Deferred to a future release. Tracked but not in this roadmap.

### Harmonics CLI

- **HARMF-01**: Rich `--harmonics` CLI grammar — multi-harmonic (`h7,h11`) and preset+harmonic mixing (`traditional,h7`). v1.5 shipped only the Tight single-token form; carried forward.

### Declination follow-ups

- **DECLA-F1**: Declination synastry / applying-timing / dedicated CLI surface for declination aspects (v1.6 shipped in-orb detection only). Natural follow-ups if demand surfaces.

## Out of Scope

Explicitly excluded for v1.7. Documented to prevent scope creep.

| Feature | Reason |
| ------- | ------ |
| Configurable per-call point orb (override `core.bodies`) | v1.7 sets one global value (2°); a runtime override is a separate, larger config-surface decision with no current demand |
| Filtering other tautological/degenerate pairs | Only Rahu↔Ketu Opposition is tautological by construction; no other point pair has a permanent fixed angle |
| Changing planet orbs (Sun..Chiron) | v1.7 touches the three fictitious points only; the Abu Ma'shar / Al-Biruni planet orbs stay frozen |
| Rahu UI work (FastAPI / SvelteKit / D3) | Separate repo `~/workspace/rahu`, consumes `ketu` from PyPI; v1.7 only unblocks it from the engine side |
| True/Osculating Lilith, asteroids, extra bodies | No new bodies; v1.7 is an orb change on existing points |
| Patch release (1.6.1) | Aspect results change for consumers — a minor bump is required so Kala treats the upgrade as deliberate |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
| ----------- | ----- | ------ |
| ORB-01 | Phase 38 | Complete |
| ORB-02 | Phase 38 | Complete |
| ORB-03 | Phase 38 | Complete |
| ORB-04 | Phase 39 | Complete |
| REL-01 | Phase 39 | Complete |

**Coverage:**

- v1.7 requirements: 5 total
- Mapped to phases: 5 (Phase 38: ORB-01/02/03; Phase 39: ORB-04/REL-01)
- Unmapped: 0 ✓

---
*Requirements defined: 2026-06-15*
*Last updated: 2026-06-15 — traceability filled by roadmapper (phases 38-39)*
