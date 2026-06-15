# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.6 — Declination Aspects

**Shipped:** 2026-06-04
**Phases:** 2 | **Plans:** 5 | **Sessions:** 1

### What Was Built
- Additive `ketu.declination` subpackage: `find_declination_aspects` (scalar) + `declination_aspect_masks` (vectorized batch, no Python body loop) + `DeclinationAspectMasks` NamedTuple + `DECLA_ASPECT_DTYPE` + `DECLA_COEF=1/12` + `MIN_DECL_ORB=0.5°` — parallels & contra-parallels on the δ axis (DECLA-01..04).
- Feature documentation en + fr (concepts prose + API reference + verified FR `.mo` recompile, no English fallback) (DECLA-05).
- `ketu==1.6.0` shipped to PyPI via OIDC after a 14-gate local pre-flight and an explicit human go/no-go; tag + origin/main pushed, GitHub release, post-publish smoke from PyPI green.

### What Worked
- **Wave-based parallel execution** of the docs (37-01) and version-bump (37-02) plans — no file overlap, both landed cleanly; only the merge/cleanup was sequential.
- **The 14-gate release pre-flight caught two real CI-gate failures** (numpydoc GL01/GL06/GL07 + a NumPy-2.x `np.str_` doctest mismatch) in the already-merged Phase 36 code *before* the irreversible publish — exactly what a pre-flight is for.
- **The human go/no-go checkpoint held** — the orchestrator paused, surfaced all three deviations, and waited for explicit approval before tagging. The locked relecture-validation constraint worked as designed.
- **Additive-by-construction discipline**: `CHART_DTYPE` stayed byte-identical (companion function, not a field), so there was no ratchet break and Kala is unaffected.

### What Was Inefficient
- **The worktree executor for 37-01 was blocked on a denied Bash permission** and produced 0 commits — ~30% of the work was recovered inline by the orchestrator. A parallel docs executor that can't run `git`/`make` is dead weight; sequential-inline would have been faster for that plan.
- **sphinx-intl fuzzy auto-fills were dangerously wrong** (the v1.6 heading seeded with the v1.5 string, `1.0°`→`10°`, `DECLA_ASPECT_DTYPE`→`CHART_DTYPE`). Every new msgstr had to be hand-audited; trusting `update-po` output blindly would have shipped mistranslations.
- **The plan's premise that the repo commits zero `.mo` was simply wrong** — discovered only at the `make clean` gate. Cost a detour to confirm the convention via git history before committing the `.mo`.
- **`python -m venv` is unusable in this sandbox** (no ensurepip); both fresh-venv smokes had to fall back to `uv venv`, and the first PyPI smoke needed `--refresh` to bypass uv's stale index cache.

### Patterns Established
- **Pre-flight = 14 hard gates, STOP on first red, then a blocking human checkpoint, then publish.** Reusable shape for every release phase.
- **MyST cross-doc links use the explicit-label `[text](#label)` form** (bare hash), not `file.md#anchor` — the latter emits `xref_missing` in both EN and FR builds even though the href resolves.
- **Commit recompiled `.mo` alongside `.po`** — repo convention; `.po`-without-`.mo` ships stale French docs.
- **Fresh-venv wheel smokes must run from a non-repo cwd** (e.g. `/tmp`) so the local `ketu/` source tree doesn't shadow the installed wheel.

### Key Lessons
1. **A pre-flight on a release phase will catch quality-gate debt that earlier phases' verification missed.** Phase 36's VERIFICATION marked its code SATISFIED, but its docstrings failed the CI numpydoc/doctest gates — only the release pre-flight ran those gates against that code. Run the full CI gate set in every phase, not just at release.
2. **Don't trust i18n tooling's fuzzy matches.** `sphinx-intl update-po` will happily seed a new string with an unrelated existing translation. Audit every new `msgstr` and clear every `#, fuzzy` flag.
3. **A parallel executor without the permissions to do its job is worse than sequential** — it consumes a worktree and returns nothing committable. Match the execution mode to the plan's tool needs.
4. **Verify the plan's environmental assumptions against the live repo** (does it really commit zero `.mo`? does `python -m venv` work here?) before treating them as gates.

### Cost Observations
- Model mix: orchestration on Opus 4.8; executors + verifier + integration-checker on Sonnet.
- Sessions: 1 (same-day execute → audit → close, ~10h elapsed).
- Notable: the blocked worktree executor wasted ~80k subagent tokens for 0 commits; the inline recovery was cheaper than a re-spawn would have been.

---

## Milestone: v1.7 — Fictitious-Point Orbs

**Shipped:** 2026-06-15
**Phases:** 2 | **Plans:** 5 | **Sessions:** 1

### What Was Built
- Orb `0°→2°` on Rahu/Ketu/Lilith in the single-source `core.bodies` table; all consumers (`get_orb`, `synastry_orb_limit`, cycles, composite, CLI) inherit data-driven (ORB-01).
- Shared `_is_tautological_node_opposition` helper wired into all four public natal/scalar emit paths; suppresses ONLY the permanent `(Rahu, Ketu)` + `Opposition` artefact, never the bodies (ORB-02).
- Synastry `orb=0` oracles rewritten (0.0→1.0 for point self-pairs) + full ~40-file regression sweep; two new CLI Rahu detections (Sun-Rahu Quincunx, Venus-Rahu Trine) deliberately pinned (ORB-03).
- Docs en + fr (2° orb, Rahu↔Ketu filter rationale, MINOR-not-patch Kala note); FR `.po` translated + `.mo` recompiled (ORB-04).
- `ketu==1.7.0` shipped to PyPI via OIDC after local pre-flight + explicit human go/no-go; tag + origin/main pushed, post-publish smoke from PyPI green (REL-01).

### What Worked
- **Single-source orb edit propagated cleanly** — flipping one value in `core.bodies` changed every consumer with no per-consumer edit, exactly as the Chiron-orb pattern (v1.4) predicted. The data-driven design paid off again.
- **The surgical filter stayed surgical** — `_is_tautological_node_opposition` targets the one pair+aspect; the regression sweep confirmed Rahu/Ketu remain fully active for every other aspect and pair.
- **The release pre-flight caught two stale ORB-04 defects before publish** — leftover `orb=0` docstrings and a broken `concepts.md#orbs` Sphinx xref in `api.md` (EN+FR). Same pattern as v1.6: the pre-flight runs gates against code earlier phases didn't.
- **The human go/no-go checkpoint held again** — paused, surfaced the deviations, waited for explicit approval before the irreversible tag/push/publish.
- **No silent oracle updates** — every changed detection (synastry self-pairs, two new CLI Rahu aspects) was deliberately pinned, so the diff is auditable.

### What Was Inefficient
- **The 39-01 worktree executor was Bash-blocked** (same failure mode as v1.6's 37-01) and the docs plan finished inline. The lesson from v1.6 — a parallel docs executor without `git`/`make` permissions is dead weight — recurred; the execution mode wasn't adjusted preemptively.
- **Stale `orb=0` artefacts lived in docstrings and a doc xref** that earlier phases' verification didn't flag — only the release pre-flight surfaced them. A grep for `orb=0` / `0°` in docs during Phase 38 would have caught them earlier.

### Patterns Established
- **A single-source data table (`core.bodies`) makes a behaviour change a one-line edit** — orb changes (Chiron v1.4, fictitious points v1.7) propagate to all consumers for free. Keep new tunables in the table, not in consumers.
- **Suppress the artefact, not the body** — when a non-zero orb creates a tautological detection (fixed-angle pair), filter the exact `(pair, aspect)` tuple in the emit path; never disable the body.
- **MINOR-not-patch when results change** — even a "small" orb tweak that alters aspect detections is a minor bump with an UPGRADING note, not a patch. Consumers must opt in deliberately.

### Key Lessons
1. **A behaviour change that alters downstream RESULTS is a MINOR, regardless of code size.** One value flipped, but every consumer's aspect grid changed — semver tracks observable behaviour, not diff size.
2. **The release pre-flight is the de-facto final doc audit.** Stale `orb=0` docstrings/xrefs survived phase verification and were only caught at pre-flight (third milestone running: v1.6 numpydoc/doctest, v1.7 docstring/xref). Run a docs grep for changed constants during the engine phase, not just at release.
3. **Match the execution mode to the plan's tool needs up front.** The Bash-blocked worktree docs executor recurred from v1.6; for docs/release plans that need `git`/`make`, go inline by default.

### Cost Observations
- Model mix: orchestration on Opus 4.8; executors + verifier on Sonnet.
- Sessions: 1 (same-day plan → execute → ship, ~3h elapsed: `ce48b17` 20:45 → `fae8eea` 23:58).
- Notable: a tight 2-phase / 5-plan milestone; the surgical scope kept the regression surface bounded to point-referencing tests.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.6 | 1 | 2 | First milestone where the release pre-flight caught prior-phase CI-gate debt; human go/no-go checkpoint exercised end-to-end |
| v1.7 | 1 | 2 | First behaviour-changing (non-additive) minor since v1.3; surgical artefact filter + single-source orb edit; pre-flight again caught stale docs (xref + docstrings) |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1.5 | 1627 | 100% | declination δ functions + body_decl field |
| v1.6 | 1654 | 100% | ketu.declination subpackage (parallels/contra-parallels) |
| v1.7 | 1668 | 100% | fictitious-point 2° orbs (behaviour change, not zero-dep additions) |

### Top Lessons (Verified Across Milestones)

1. **The user go/no-go relecture-validation gate before any irreversible PyPI publish is non-negotiable** — held in v1.5 and again in v1.6.
2. **Additive-only minors keep the frozen contracts intact** (`CHART_DTYPE`, `core.aspects` fingerprints) — verified across v1.4, v1.5, v1.6.
3. **Push BOTH the tag AND origin/main on release** — RTD follows main, PyPI follows the tag (v1.5 lesson, re-applied in v1.6 and v1.7).
4. **The release pre-flight is the de-facto final doc audit** — caught CI-gate debt in v1.6 (numpydoc/doctest) and stale-constant docs in v1.7 (`orb=0` docstrings + broken xref). Phase verification alone doesn't run those gates against earlier code.
5. **MINOR-not-patch when downstream results change** — even a one-value orb tweak is a minor with an UPGRADING note (v1.7), so consumers opt in deliberately rather than assuming `pip install -U` is neutral.
