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

## Milestone: v1.8 — Declination Speed

**Shipped:** 2026-06-19
**Phases:** 2 | **Plans:** 6 | **Sessions:** 1 (execute) + 1 (audit/close)

### What Was Built
- `body_decl_speed` (dδ/dt, deg/day) appended to `CHART_DTYPE` at index 8 (15→16 fields), populated by `compute_chart` via vectorised forward FD at Δt=0.01 d (exact Δ=0 vs the v1.5 scalar `declination_velocity`) (DSPD-01, DSPD-02).
- `body_decl_speed` inherited by synastry/composite/returns; composite derived from its own frozen (λ,β), never the parent midpoint (anti-averaging ratchet); dtype ratchet re-pinned at 16 fields, body count frozen at 14 (DSPD-03, DSPD-04).
- Public `DECL_STANDSTILL_EPS = 0.001` constant in `ketu.calculations.__all__` + chart-level `is_ascending_declination_chart(chart)→int8 {+1,0,−1}` helper, distinct from (and consistent with) the v1.5 scalar (DSPD-05, DSPD-06).
- Docs en+fr for the field, Δt step, threshold, helper, and the Ketu/Rahu boundary; FR `.po`/`.mo` recompiled (no English fallback); full private-name sweep (DSPD-07).
- `ketu==1.8.0` shipped to PyPI via OIDC after human go/no-go; tag + origin/main pushed, post-publish fresh-venv smoke from PyPI green (REL-01).

### What Worked
- **The v1.5 `body_decl` precedent was a near-exact template.** Index-8 additive field, ratchet re-pin, composite-from-own-chart (not parent midpoint), Kala re-pin note — the v1.5 milestone had already solved every structural question, so Phase 40 was mostly mechanical replay. Reusing a known-good pattern collapsed the design risk.
- **"Expose, don't reinvent" kept the scope tiny and correct.** The calculation existed since v1.5; the whole milestone was wiring an existing scalar into the structured chart. Naming that framing up front (in REQUIREMENTS Intent) stopped any temptation to re-derive the FD and gave the exact Δ=0 agreement test for free.
- **The composite anti-averaging ratchet caught the exact v1.5 trap by design.** Pinning `comp ≠ naïve parent-midpoint` (Moon −5.58 vs −3.23) means a future refactor that accidentally midpoints the parents' δ-speed fails loudly.
- **Verifier ran the FR-rendering human item to ground.** Phase 41 left one human-verification item (does the FR HTML actually render French, not fall back to EN); the orchestrator rebuilt the FR docs and inspected `concepts.html` directly rather than trusting the `.mo` mtime — confirmed, then user-confirmed.
- **The milestone audit was a clean pass with zero surprises.** 3-source cross-reference (VERIFICATION + SUMMARY + traceability) + an integration-checker E2E "Rahu consumer" run all agreed 8/8; the only finding was a transient measurement artifact the checker self-corrected (DSPD-02 is Δ=0 exact).

### What Was Inefficient
- **No milestone audit existed at close time.** Unlike v1.6 (which archived a `v1.6-MILESTONE-AUDIT.md`), v1.8 reached `/gsd-complete-milestone` with no audit file — it had to be run inline first. The audit should be a standing pre-close step, not an ad-hoc catch.
- **The CLI auto-extracted noisy "accomplishments" into MILESTONES.md** (`CHANGELOG.md` as a bullet, a raw `make gettext` command line) because it grabs the first non-frontmatter lines of each SUMMARY. Had to hand-rewrite the entry. SUMMARY one-liners aren't reliably the first prose line.
- **REQUIREMENTS.md traceability went stale post-execution** — it still showed DSPD-07 as "Pending"/`[ ]` while the code was fully shipped (the 41 verifier flagged this explicitly). The traceability table isn't updated when a phase completes, so the audit's 3-source cross-check is what actually catches the truth.

### Patterns Established
- **"Expose an existing scalar as a structured-chart field" is now a repeatable shape** (v1.5 `body_decl`, v1.8 `body_decl_speed`): additive field at an adjacent index, re-pin the ratchet, derive composite from the composite's own chart, document the MINOR-not-patch re-pin for Kala. Future field additions follow this without re-deciding.
- **Define the downstream contract IN the engine** (`DECL_STANDSTILL_EPS`), so the consumer (Rahu) invents no astronomy — even a threshold is an astronomy decision and belongs in Ketu.
- **Run `/gsd-audit-milestone` before `/gsd-complete-milestone`, always.** The 3-source cross-reference + integration E2E is the real gate; phase-level verification alone leaves the traceability table stale.

### Key Lessons
1. **A milestone that "exposes" rather than "computes" is the cheapest kind — name that framing in the requirements Intent and the scope polices itself.** The exact Δ=0 agreement test falls out of reusing the FD verbatim.
2. **The requirements traceability table is not self-updating; trust the 3-source cross-reference at audit, not the checkboxes.** DSPD-07 read "Pending" in REQUIREMENTS.md while shipped and live on PyPI.
3. **Don't trust auto-extracted SUMMARY one-liners for the milestone record** — they grab the first prose line, which is often a table header or a raw command. Curate the MILESTONES.md accomplishments by hand.
4. **A human-verification item left by a phase verifier should be resolved by inspecting the actual artifact** (rebuilt FR HTML), not by re-asserting the proxy (`.mo` mtime) — the orchestrator did this and it was the right call.

### Cost Observations
- Model mix: orchestration on Opus 4.8; executors + verifier + integration-checker on Sonnet.
- Sessions: execute same-day 2026-06-17 (engine + EN docs + FR), release + close 2026-06-19.
- Notable: smallest code delta of any recent feature milestone (17 code files, +711/−58) for a fully additive chart field; the doc/translation surface (66 files incl. docs) dwarfed the engine change.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.6 | 1 | 2 | First milestone where the release pre-flight caught prior-phase CI-gate debt; human go/no-go checkpoint exercised end-to-end |
| v1.7 | 1 | 2 | First behaviour-changing (non-additive) minor since v1.3; surgical artefact filter + single-source orb edit; pre-flight again caught stale docs (xref + docstrings) |
| v1.8 | 2 | 2 | "Expose existing scalar as chart field" replay of the v1.5 `body_decl` pattern; milestone audit run inline at close (no pre-existing audit file); 3-source cross-reference caught stale traceability |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1.5 | 1627 | 100% | declination δ functions + body_decl field |
| v1.6 | 1654 | 100% | ketu.declination subpackage (parallels/contra-parallels) |
| v1.7 | 1668 | 100% | fictitious-point 2° orbs (behaviour change, not zero-dep additions) |
| v1.8 | 1691 | 100% | body_decl_speed field + DECL_STANDSTILL_EPS + is_ascending_declination_chart helper |

### Top Lessons (Verified Across Milestones)

1. **The user go/no-go relecture-validation gate before any irreversible PyPI publish is non-negotiable** — held in v1.5, v1.6, v1.7, and v1.8.
2. **Additive-only minors keep the frozen contracts intact** (`CHART_DTYPE` named access, `core.aspects` fingerprints) — verified across v1.4, v1.5, v1.6, v1.8 (v1.8 grows the dtype but only positional/`.view()` consumers must adapt; named access stays safe).
3. **Push BOTH the tag AND origin/main on release** — RTD follows main, PyPI follows the tag (v1.5 lesson, re-applied in v1.6, v1.7, v1.8).
4. **The release pre-flight is the de-facto final doc audit** — caught CI-gate debt in v1.6 (numpydoc/doctest) and stale-constant docs in v1.7 (`orb=0` docstrings + broken xref). Phase verification alone doesn't run those gates against earlier code.
5. **MINOR-not-patch when downstream results OR layout change** — a one-value orb tweak (v1.7, results change) and a grown dtype layout (v1.8, positional layout change) are both minors with UPGRADING notes, so consumers opt in deliberately rather than assuming `pip install -U` is neutral.
6. **Run `/gsd-audit-milestone` before close; the 3-source cross-reference is the real gate** — v1.8 reached close with stale traceability (`DSPD-07` "Pending" while shipped) and no audit file; the inline audit's VERIFICATION+SUMMARY+traceability cross-check + integration E2E is what confirmed truth.
