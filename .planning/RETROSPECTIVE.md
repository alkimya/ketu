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

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.6 | 1 | 2 | First milestone where the release pre-flight caught prior-phase CI-gate debt; human go/no-go checkpoint exercised end-to-end |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1.5 | 1627 | 100% | declination δ functions + body_decl field |
| v1.6 | 1654 | 100% | ketu.declination subpackage (parallels/contra-parallels) |

### Top Lessons (Verified Across Milestones)

1. **The user go/no-go relecture-validation gate before any irreversible PyPI publish is non-negotiable** — held in v1.5 and again in v1.6.
2. **Additive-only minors keep the frozen contracts intact** (`CHART_DTYPE`, `core.aspects` fingerprints) — verified across v1.4, v1.5, v1.6.
3. **Push BOTH the tag AND origin/main on release** — RTD follows main, PyPI follows the tag (v1.5 lesson, re-applied in v1.6).
