---
phase: 16-synastry
plan: 04
subsystem: cli
tags: [argparse, cli, synastry, introspection, json-output, ascii-table, m1-ratchet, first-wins]

# Dependency graph
requires:
  - phase: 16-synastry
    plan: 02
    provides: calculate_synastry, SYNASTRY_DTYPE, SYNASTRY_FACTOR, ASC_MC_NATAL_ORB_DEG, _PRESET_BY_NAME
  - phase: 14-chart-abstraction-foundation
    provides: compute_chart (consumed twice per invocation, one chart per side)
  - phase: 15-additional-house-systems
    provides: SYSTEMS registry (6 systems: equal/koch/placidus/porphyry/regiomontanus/whole_sign)
  - phase: 11-cli-refactor-and-integration
    provides: CLI-06 resolved-config STDERR header pattern (emit_resolved_config), subparser dispatch convention (set_defaults(func=...)), introspection short-circuit ladder in main()
provides:
  - "`ketu synastry` CLI sub-command (9 arguments: --date-a/--lat-a/--lon-a/--date-b/--lat-b/--lon-b/--mode/--system/--polar-fallback/--json)"
  - "`ketu --list-orbs` top-level introspection flag (sibling of --list-aspect-sets and --list-house-systems)"
  - "Aligned ASCII table renderer (default) with Body A / Body B / Aspect / Orb / Limit / Apply columns"
  - "JSON list-of-dicts serialisation of SYNASTRY_DTYPE (11 keys per dict: 8 dtype fields + 3 label fields: body_a_name, body_b_name, aspect_name)"
  - "First-wins early-return ladder ratchet test (M-1 Pitfall 8 contract pinned)"
  - "_PRESET_BY_NAME (singular) import convention reinforced in introspection.py (M-5 ratchet)"
affects: [16-05-close-out, 17-composite (CLI patterns to mirror), 18-solar-return (CLI patterns to mirror)]

# Tech tracking
tech-stack:
  added: []  # No new runtime deps; pure argparse + json stdlib + existing numpy / ketu.* surface
  patterns:
    - "Suffixed --date-a/--lat-a/--lon-a + --date-b/--lat-b/--lon-b argparse grouping (chart-pair convention, locked by CONTEXT.md decision; lookup-pattern for Plans 17/18)"
    - "Aligned ASCII table f-string formatting mirrors houses_cmd._format_cusp (10-char body labels, 14-char aspect names, 9-char signed orb, 7-char limit, 6-char Y/N apply)"
    - "JSON sentinel handling: aspect_type=-1 -> aspect_name=None; orb=NaN/orb_limit=NaN -> JSON null (per-field np.isnan check at write time)"
    - "STDERR diagnostics layered on top of emit_resolved_config: '# Synastry mode: X' + '# Orbs: synastry (factor 0.5 — astro.com convention)' lines"
    - "Data-driven preset enumeration in cmd_list_orbs: iterates sorted(_PRESET_BY_NAME.keys()), so v1.3 in-place dict extension surfaces in CLI without code edits here"
    - "First-wins early-return ladder in main(): args.list_aspect_sets -> args.list_house_systems -> args.list_orbs, intentionally NOT alphabetical (production order locked by code comment + M-1 test)"

key-files:
  created:
    - ketu/cli/synastry_cmd.py
    - tests/cli/test_synastry_cmd.py
  modified:
    - ketu/cli/parser.py  # synastry subparser + --list-orbs flag + ladder branch in main()
    - ketu/cli/introspection.py  # cmd_list_orbs + _ORB_PRESET_DESCRIPTIONS
    - tests/cli/test_introspection.py  # +1 short-circuit + 5 cmd_list_orbs tests
    - tests/cli/test_parser.py  # +6 tests (3 synastry subparser + 3 list-orbs incl. M-1 collision ratchet)

key-decisions:
  - "Suffixed argument grouping locked: chart-A bundle (--date-a/--lat-a/--lon-a) → chart-B bundle (--date-b/--lat-b/--lon-b) → mode → system → polar-fallback → json. Order pinned in plan; provides scanning-order parity with how a human reads the resulting help."
  - "STDERR header carries TWO synastry-specific diagnostic lines AFTER emit_resolved_config: '# Synastry mode: <mode>' and '# Orbs: synastry (factor 0.5 — astro.com convention)'. Pins the orbs preset citation (ROADMAP success criterion #3) into every CLI invocation."
  - "JSON output adds three label fields ON TOP of the 8 SYNASTRY_DTYPE fields: body_a_name, body_b_name (via _BODY_LABELS_15 = core.bodies['name'] + ['ASC', 'MC']), and aspect_name (via core.aspects['name'], None for sentinel rows). Consumers get human-readable rows without re-joining the core dtype tables."
  - "Aligned ASCII table is for FILTERED rows only — when --mode dense is requested, the table view STILL filters to aspect_type >= 0 before rendering (sentinel rows would explode the table to 225 lines with NaN noise). Dense output makes sense via --json only; the table consistently shows only meaningful aspects."
  - "First-wins early-return ladder is INTENTIONAL (research §Pitfall 8). Ladder order = args.list_aspect_sets → args.list_house_systems → args.list_orbs. Comment in parser.main() + test_list_flags_collision_first_wins XOR assertion pin the contract."
  - "M-5 ratchet honoured: cmd_list_orbs imports _PRESET_BY_NAME (singular), matching the convention from ketu/aspects/presets.py:91. Verified by the import succeeding (no parallel _PRESETS_BY_NAME alias exists in ketu.synastry.orbs)."

patterns-established:
  - "CLI sub-command for two-chart operations (synastry, future composite, future bi-wheel): suffixed arg bundling per chart side, mode selector exposed via --mode, JSON opt-in via --json. Plans 17/18 should mirror this exactly."
  - "Introspection flag ladder in main(): every new --list-* flag adds one early-return branch; collision is first-wins by design; M-1 test ratchets the XOR contract."
  - "Data-driven preset description tables (_ORB_PRESET_DESCRIPTIONS keyed by _PRESET_BY_NAME entries): future v1.3 preset addition only requires extending _PRESET_BY_NAME + _ORB_PRESET_DESCRIPTIONS; the CLI output and tests adapt automatically."

# Metrics
duration: ~30min
completed: 2026-05-11
---

# Phase 16 Plan 04: Synastry CLI Sub-command Summary

**`ketu synastry --date-a ... --date-b ...` CLI sub-command with aligned ASCII table (default) + JSON opt-in, `--mode dense|filtered` selector, 6-system `--system` choice, `--polar-fallback raise|porphyry` pass-through, plus the `ketu --list-orbs` introspection flag — 32 new CLI tests, 100% synastry-module coverage preserved, M-1 collision ratchet pinned.**

## Performance

- **Duration:** ~30 min (spread across two sessions — Tasks 1 + 2 scaffolded in a prior interrupted run; this session closes Task 3 + verification)
- **Started:** 2026-05-11T08:45:36Z (this session)
- **Completed:** 2026-05-11T09:10:53Z (approx.)
- **Tasks:** 3 / 3
- **Files modified:** 5 (1 new dispatcher + 1 new test file + 3 modified)

## Accomplishments

- **CLI sub-command shipped.** `ketu synastry` parses all 6 required args (chart pair) + 4 optional args (mode/system/polar-fallback/json), dispatches via `set_defaults(func=cmd_synastry)`, and produces both an aligned ASCII table (default) and a JSON list-of-dicts (`--json` opt-in).
- **`ketu --list-orbs` introspection.** Sibling of `--list-aspect-sets` and `--list-house-systems`. Prints the synastry orb preset table (factor 0.50 vs factor 1.00), the canonical formula derivation `(orb[b1] + orb[b2]) / 2 * coef[asp] * factor`, the ASC/MC 8.0° natal-orb annotation, three worked examples, and a Rahu/Ketu/Lilith zero-orb edge-case note.
- **6-system house-system selector wired.** Reuses `_HOUSE_SYSTEMS = ketu.houses.SYSTEMS` (already imported in parser.py from Phase 15); same `sorted()` enumeration as `ketu houses --system`.
- **First-wins collision ratchet pinned.** `test_list_flags_collision_first_wins` asserts XOR between the orbs and house-systems output branches when both flags are passed — pins Pitfall 8 from 16-RESEARCH.md against any future "run-all" regression.
- **`_PRESET_BY_NAME` (singular) reinforced.** Import in `introspection.py` uses the project-wide singular convention (mirrors `ketu/aspects/presets.py:91`); M-5 ratchet satisfied without code change to `ketu/synastry/orbs.py` (Plan 16-01 already locked it).
- **32 new CLI tests** across three files (21 synastry-cmd + 5 introspection + 6 parser, with the M-1 collision ratchet being the headline new contract), bringing the full project suite to **1064 PASSED**. Coverage on `ketu/cli/synastry_cmd.py` = **98%** (1 defensive-branch line uncovered). Synastry module coverage = **100%** (no regression).

## Task Commits

Each task was committed atomically across the two sessions (Tasks 1+2 from the prior interrupted session, Task 3 split into two commits this session):

1. **Task 1: cmd_synastry dispatcher + cmd_list_orbs** — `9c81a86` (feat) — prior session
2. **Task 2: synastry subparser + --list-orbs flag wired into parser** — `b788da3` (feat) — prior session
3. **Task 3a: test_synastry_cmd.py (21 tests) + test_introspection.py (5 list_orbs tests + 1 short-circuit)** — `dab57c6` (test) — this session
4. **Task 3b: test_parser.py (+6 synastry subparser / list-orbs / M-1 collision ratchet tests)** — `39e8dac` (test) — this session

**Plan metadata commit:** pending (this SUMMARY + STATE.md update).

## Files Created/Modified

### Created

- `ketu/cli/synastry_cmd.py` (~184 LoC) — Module docstring, `_BODY_LABELS_15` constant (`core.bodies['name']` + `['ASC', 'MC']`), `_body_label` helper (15-body index → human label), `_row_to_jsonable` helper (SYNASTRY_DTYPE row → 11-key dict with sentinel-aware None handling), `cmd_synastry` dispatcher (resolved-config STDERR, parse_iso_utc both dates, compute_chart both charts, calculate_synastry, render table or JSON). Mirrors `ketu/cli/houses_cmd.py:1-85` structure exactly.
- `tests/cli/test_synastry_cmd.py` (~375 LoC, 21 tests across 8 classes) — `TestSynastryParserRequirements` (5 argparse-error tests), `TestSynastryModeSelector` (3 mode-selector tests), `TestSynastryJsonOutput` (4 JSON-output tests including the SYNASTRY_DTYPE-keys + name-fields shape), `TestSynastrySystemSelector` (3 house-system selector tests covering placidus default + whole_sign + invalid name), `TestSynastryPolarFallback` (2 polar-fallback tests at lat=80°), `TestSynastryAsciiTable` (2 table-shape tests including the empty-result mocked branch), `TestSynastryStderrDiagnostics` (1 STDERR-header test), `TestSynastryJsonMatchesPythonAPI` (1 round-trip consistency test).

### Modified

- `ketu/cli/parser.py` — Added `from .introspection import cmd_list_orbs`, `from .synastry_cmd import cmd_synastry`, the `--list-orbs` top-level flag, the synastry subparser (9 arguments: `--date-a`, `--lat-a`, `--lon-a`, `--date-b`, `--lat-b`, `--lon-b`, `--mode`, `--system`, `--polar-fallback`, `--json` — argparse `set_defaults(func=cmd_synastry)`), updated `subparsers.metavar` to `"{aspects,houses,synastry}"`, and the `if args.list_orbs: cmd_list_orbs(); return 0` early-return branch in `main()` with a code comment pinning the first-wins ladder contract.
- `ketu/cli/introspection.py` — Added imports of `_PRESET_BY_NAME`, `SYNASTRY_FACTOR`, `ASC_MC_NATAL_ORB_DEG` (singular `_PRESET_BY_NAME` — M-5 ratchet), `_ORB_PRESET_DESCRIPTIONS` table, and `cmd_list_orbs()` function (data-driven preset enumeration + formula derivation + ASC/MC annotation + 3 examples + Rahu/Ketu/Lilith zero-orb note).
- `tests/cli/test_introspection.py` — Extended `TestIntrospectionShortCircuits` with `test_list_orbs_no_subcommand`; added new `TestListOrbs` class with 5 tests (`test_cmd_list_orbs_runs_without_error`, `..._lists_both_presets`, `..._includes_formula_derivation`, `..._cites_asc_mc_default`, `..._examples_block`).
- `tests/cli/test_parser.py` — Added `TestSynastrySubparser` class (3 tests: `test_parser_has_synastry_subparser`, `..._default_mode_filtered`, `..._default_system_placidus`) and `TestListOrbsFlag` class (3 tests: `test_parser_list_orbs_flag_recognized`, `test_main_dispatches_list_orbs`, `test_list_flags_collision_first_wins` — the M-1 ratchet).

## Public CLI Surface Exposed

| Surface | Type | Notes |
| --- | --- | --- |
| `ketu synastry --date-a … --date-b …` | subcommand | 9 args; default output: aligned ASCII table; `--json` opt-in |
| `ketu --list-orbs` | top-level flag | sibling of `--list-aspect-sets`, `--list-house-systems` |
| `cmd_synastry` | dispatcher function | importable from `ketu.cli.synastry_cmd`; `(args: argparse.Namespace) -> int` |
| `cmd_list_orbs` | introspection function | importable from `ketu.cli.introspection`; `() -> None` |
| `_body_label`, `_row_to_jsonable` | private helpers | exported from `ketu.cli.synastry_cmd` for unit-test access |

## Coverage & Doc-Gate Status

| Gate | Result |
| --- | --- |
| `interrogate ketu/cli/{synastry_cmd,introspection,parser}.py -f 95` | **100%** (11/11 docstrings) |
| `numpydoc lint ketu/cli/{synastry_cmd,introspection,parser}.py` | **0 issues** |
| `mypy --strict ketu/cli/` | **0 issues** (9 source files) |
| Coverage on `ketu/cli/synastry_cmd.py` | **98%** (44/45 stmts; 1 defensive `_body_label` `raise ValueError` branch) |
| Coverage on `ketu/synastry/` | **100%** (98/98 stmts) — no regression from CLI integration |
| `pytest tests/cli/` (full CLI suite) | **136/136** PASS |
| `pytest tests/synastry/` (synastry domain) | All PASS (preserved from Plans 16-01..03) |
| `pytest tests/` (full regression) | **1064/1064** PASS |

## Decisions Made

All locked decisions tracked in frontmatter `key-decisions`. Highlights:

- **Suffixed arg-group order is the locked convention.** Chart-A bundle first, then chart-B bundle, then mode/system/polar/json — pins the scanning order in `--help` and prevents future drift toward positional / alternating layouts.
- **STDERR diagnostics are a layered contract.** `emit_resolved_config` provides `# Ketu vX` + `# House system: <name>`; the synastry dispatcher adds `# Synastry mode: <mode>` and `# Orbs: synastry (factor 0.5 — astro.com convention)`. The orbs citation per-invocation is non-negotiable (ROADMAP success criterion #3).
- **Dense-mode ASCII output is silently filtered to aspect_type >= 0.** Rendering 225 lines with NaN noise would be hostile UX; the `--mode dense` flag is meaningful only via `--json` for ML / programmatic consumers. Decision pinned in code: `aspected = result[result["aspect_type"] >= 0] if args.mode == "dense" else result`.
- **First-wins ladder, not alphabetical.** Production ladder is `list_aspect_sets → list_house_systems → list_orbs` (declaration order in the source). M-1 test enforces XOR between the orbs branch and the house-systems branch when both flags are passed simultaneously — the test does NOT over-specify which branch wins, only that exactly one fires.

## Deviations from Plan

### Auto-fixed Issues

None during this session.

The prior session (Tasks 1 + 2) finished without recorded deviations — `synastry_cmd.py` and the parser additions match the plan's reference implementation exactly (mod stylistic adaptations: explicit `typing.Any` import for `_row_to_jsonable` return type; multiline arg `help` strings split for line-length comfort; `set_defaults(func=cmd_synastry)` on the subparser; `metavar="{aspects,houses,synastry}"` update).

This session (Task 3) executed exactly as specified: 21 tests for `test_synastry_cmd.py` (one per plan test-bullet), 5 + 1 short-circuit for `test_introspection.py`, 6 for `test_parser.py` including the M-1 collision-ratchet. No fixes needed; all tests passed on first run.

---

**Total deviations:** 0 auto-fixed.
**Impact on plan:** Plan executed exactly as written — single-source plan validity confirmed.

## Issues Encountered

- **GPG signing**: continued environmental issue (consistent across Plans 16-01 and 16-02); both task commits in this session used `-c commit.gpgsign=false`. Not a regression.
- **Hardcoded `venv/bin/pytest` shebang**: the on-disk `venv/bin/pytest` script has shebang `#!/home/loc/workspace/solaris/ketu/venv/bin/python3` (path does not exist on this machine). Workaround: invoke pytest as `venv/bin/python3 -m pytest …`. Documented in STATE.md as a v1.2 ops-debt item, not in 16-04 scope.
- **`venv/bin/python3 -m coverage run --source=ketu`** silently produced an empty dataset when the `--source` was set on the command-line (overriding `pyproject.toml [tool.coverage.run] source`). Workaround: drop `--source` (pyproject already specifies it). One-time confusion; commands captured for future sessions.

## User Setup Required

None — no external service configuration required. The CLI sub-command works on any UTC date + lat/lon pair using existing Ketu primitives.

## Ratchet Confirmations

- **M-1 Pitfall 8 (first-wins ladder).** `test_list_flags_collision_first_wins` in `tests/cli/test_parser.py` asserts XOR between the orbs and house-systems output branches when `main(['--list-orbs', '--list-house-systems'])` is invoked. **PASSES.** Production code comment in `parser.main()` documents the intentional first-wins semantics.
- **M-5 `_PRESET_BY_NAME` (singular).** `ketu/cli/introspection.py:13-17` imports `_PRESET_BY_NAME` (singular) from `ketu.synastry.orbs`. **VERIFIED** by successful import (no module-level NameError); reinforced by the data-driven CLI output that iterates `sorted(_ORB_PRESETS.keys())`. Singular convention matches `ketu/aspects/presets.py:91` (cross-module).
- **CLI-06 resolved-config header.** `emit_resolved_config(mask=None, preset_name=None, house_system=args.system)` plus the two synastry-specific STDERR lines emit on every `cmd_synastry` call. **VERIFIED** by `test_synastry_stderr_includes_resolved_config` and `test_synastry_system_placidus_default` / `test_synastry_system_whole_sign`.

## Hand-off Note for Plan 16-05 (Phase Close-out)

All Phase 16 features are now shipped (Plans 16-01..04 complete):

- **API surface.** `ketu.synastry.calculate_synastry`, `SYNASTRY_DTYPE`, `SYNASTRY_FACTOR`, `ASC_MC_NATAL_ORB_DEG`, `_PRESET_BY_NAME`, `OrbSetSpec`, `resolve_orb_set`, `synastry_orb_limit` — all exported.
- **CLI surface.** `ketu synastry` sub-command + `ketu --list-orbs` flag — both wired, doc-gates green, mypy strict clean.
- **Tests.** 1064 / 1064 PASS project-wide; 100% coverage on `ketu/synastry/`; 98% on `ketu/cli/synastry_cmd.py`; oracle tests live in `tests/synastry/test_oracle.py` (Plan 16-03).

Plan 16-05 (close-out) tasks expected:
1. Phase 16 doc-gate ratchets (interrogate ≥95% project-wide on `ketu/`, numpydoc full clean, mypy --strict on the synastry + cli subpackages — all already green per the verification above).
2. `Makefile` target for the synastry coverage gate (mirror `make houses-coverage` / `make charts-coverage`).
3. Cross-references (CHANGELOG entry, ROADMAP success-criterion check-off SYN-01..SYN-05, downstream Kala adapter handshake docs if applicable).
4. Phase close: STATE.md `completed_phases` count bump from 3 → 4 (when Plan 16-05 commits); roadmap progress arrow advances from Phase 16 to Phase 17 (composite-chart).

No code or behavior changes required from Plan 16-04 — handoff is doc + ops only.

## Self-Check: PASSED

Verified post-write:

- `ketu/cli/synastry_cmd.py` exists (FOUND)
- `ketu/cli/parser.py` modified (FOUND in commit b788da3)
- `ketu/cli/introspection.py` modified (FOUND in commit 9c81a86)
- `tests/cli/test_synastry_cmd.py` exists (FOUND in commit dab57c6)
- `tests/cli/test_introspection.py` modified (FOUND in commit dab57c6)
- `tests/cli/test_parser.py` modified (FOUND in commit 39e8dac)
- Commit `9c81a86` exists (FOUND — feat task 1)
- Commit `b788da3` exists (FOUND — feat task 2)
- Commit `dab57c6` exists (FOUND — test task 3a)
- Commit `39e8dac` exists (FOUND — test task 3b)
- `pytest tests/cli/` green (136/136)
- `pytest tests/` full regression green (1064/1064)
- `interrogate ketu/cli/{synastry_cmd,introspection,parser}.py -f 95` ≥ 95% (100%)
- `numpydoc lint` clean (0 issues)
- `mypy --strict ketu/cli/` clean (0 issues, 9 files)
- Coverage on `ketu/cli/synastry_cmd.py` (98%)
- Coverage on `ketu/synastry/` (100%, no regression)
- `python -m ketu synastry --help` smoke (FOUND — all 9 args documented)
- `python -m ketu --list-orbs` smoke (FOUND — both presets, formula, examples, Rahu/Ketu/Lilith note)
- `python -m ketu synastry --date-a 1961-07-01T18:45:00Z --lat-a 52.83 --lon-a 0.50 --date-b 1948-11-14T21:14:00Z --lat-b 51.50 --lon-b -0.17` smoke (FOUND — Diana × Charles synastry table, 22 aspects)

---

*Phase: 16-synastry*
*Completed: 2026-05-11*
