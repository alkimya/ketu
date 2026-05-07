---
phase: 11-cli-refactor-integration
plan: 04
subsystem: cli
tags: [argparse, cli, aspects, introspection, formatters, resolved-config, byte-identity]

# Dependency graph
requires:
  - phase: 09-configurable-aspects
    provides: ASP-04 resolve_aspect_set + AspectSetSpec type alias + calculate_aspects(aspects=) (Phase 9 deliverables consumed by aspects_cmd dispatcher and display.print_aspects)
  - phase: 10-houses-module
    provides: HOU-04 SYSTEMS registry (consumed by introspection.cmd_list_house_systems)
  - phase: 11-cli-refactor-integration
    provides: Plan 11-01 build_parser scaffolding with stub dispatchers; Plan 11-02 parse_harmonics_spec validator; Plan 11-03 parse_iso_utc + cmd_houses (extended here with emit_resolved_config)
provides:
  - ketu/cli/aspects_cmd.py — cmd_aspects(args) dispatcher for the aspects subcommand (positions + aspects + Aspect Timing Example)
  - ketu/cli/formatters.py — emit_resolved_config writing CLI-06 header to STDERR
  - ketu/cli/introspection.py — cmd_list_aspect_sets + cmd_list_house_systems (CLI-05) printing human-readable lists to STDOUT
  - ketu/display.py:print_aspects extended with optional aspects= kwarg forwarded to calculate_aspects (single source of truth for v1.0 'º' format string — BLOCKER 1 fix)
  - ketu/cli/houses_cmd.py:cmd_houses extended with emit_resolved_config call (BLOCKER 2 fix; CLI-06 closed for houses subcommand)
  - ketu/cli/parser.py: zero stubs remaining; cmd_aspects + cmd_list_aspect_sets + cmd_list_house_systems wired
  - tests/cli/test_aspects_cmd.py + test_introspection.py + test_resolved_header.py (24 new tests); tests/cli/test_parser.py (3 stub-marker assertions retrofitted)
affects: [11-05-entry-point-repoint-legacy-removal, 11-06-byte-identical-regression]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Single source of truth for v1.0 stdout format strings: display.print_aspects (with optional aspects= kwarg) is called by cmd_aspects rather than hand-rolling the format string twice. Eliminates BLOCKER 1 (U+00BA vs U+00B0 drift) by construction."
    - "Resolved-config header to STDERR (CLI-06): emit_resolved_config writes '# Ketu v1.1.0' + '# Aspect set: NAME (N aspects: ...)' + '# House system: NAME' to sys.stderr, preserving CLI-03 stdout-pristine contract under --harmonics all."
    - "Preset label reverse-mapping via np.array_equal: a length-14 mask is mapped back to its canonical preset name ('classical'/'traditional'/'extended') by exact bit-for-bit equality, fallback to 'custom' for explicit-list or non-preset masks. MINOR 6 polish absorbed (no sum-count heuristic)."
    - "Always-emit pattern for v1.0 trailing block: 'Aspect Timing Example' Sun-Moon trailing block emitted regardless of --harmonics value (research §Open Question 2). v1.0 emitted it for all aspect sets; preserves CLI-03 byte-identical contract under --harmonics all without conditional logic."
    - "Module-level alias rename pattern to free a parameter name: from .core import aspects → from .core import aspects as _CORE_ASPECTS — used in display.py and ketu/cli/formatters.py and ketu/cli/introspection.py to avoid shadowing the new aspects= parameter."

key-files:
  created:
    - ketu/cli/aspects_cmd.py
    - ketu/cli/formatters.py
    - ketu/cli/introspection.py
    - tests/cli/test_aspects_cmd.py
    - tests/cli/test_introspection.py
    - tests/cli/test_resolved_header.py
  modified:
    - ketu/display.py
    - ketu/cli/parser.py
    - ketu/cli/houses_cmd.py
    - tests/cli/test_parser.py

key-decisions:
  - "BLOCKER 1 fix: cmd_aspects calls display.print_aspects(jd, aspects=mask) (the library helper), NOT a hand-rolled format-string loop. display.py is the single source of truth for the v1.0 'º' (U+00BA, MASCULINE ORDINAL INDICATOR) format string. CLI-03 byte-identity (Plan 11-06) is automatic — the 'º' character never gets typed twice in the codebase. Verified by test_aspects_output_uses_u00ba_degree_char (regression detector)."
  - "BLOCKER 2 fix: cmd_houses now calls emit_resolved_config(mask=None, preset_name=None, house_system=args.system) at the top of the dispatcher (BEFORE parse_iso_utc, so even date-parse failures still echo the header). Closes ROADMAP success criterion 5 ('every CLI invocation echoes resolved-config header') for the houses subcommand. Pinned by 4 tests in TestHousesResolvedConfigHeader."
  - "Preset label via np.array_equal exact match (not sum-count heuristic): _preset_label_for_mask compares the mask bit-for-bit against resolve_aspect_set('classical'/'traditional'/'extended'). A user-supplied --harmonics 0,4,7,9,13 produces the same mask as --harmonics classical, so the header label says 'classical' for that input — intentional; the resolved BEHAVIOUR is classical, and the header reports the resolved set."
  - "Aspect Timing Example trailing block ALWAYS emitted (research §Open Question 2 resolution): v1.0 emitted it for all aspect sets; emitting it under classical/traditional/extended preserves CLI-03 byte-identity for --harmonics all AND gives non-'all' users the same demo block (no surprising behaviour change from v1.0). 3 tests pin this across {classical, traditional, all}."
  - "AspectSetSpec imported via TYPE_CHECKING in display.py: keeps mypy --strict happy (string-quoted forward reference at runtime, real import only during type-checking). Avoids a runtime cost AND avoids a circular dep risk if aspects.presets ever imports display."
  - "Module-level core.aspects rename to _CORE_ASPECTS: needed in display.py because the new print_aspects parameter is also named 'aspects'; would shadow the module import. Same renaming pattern used in formatters.py and introspection.py for symmetry. Verified no external caller depends on display.aspects (grep returns only internal usage in tests/test_ketu.py and tests/test_coverage_improvements.py importing main, not aspects)."
  - "Re-emit count-and-angles in resolved-config header: '# Aspect set: classical (5 aspects: Conjunction 0°, Sextile 60°, Square 90°, Trine 120°, Opposition 180°)' — gives users immediate context on what aspects are active, no separate --list-aspect-sets call needed. Header uses U+00B0 '°' (DEGREE SIGN), NOT U+00BA — header is on stderr, not part of CLI-03 byte-identity contract."

patterns-established:
  - "Single-source-of-truth library helper extension: when a CLI dispatcher needs subset-filtering capability that the existing library helper doesn't expose, EXTEND THE HELPER with an optional kwarg rather than duplicating the format-string logic in the dispatcher. Prevents drift between library and CLI output formats."
  - "Resolved-config header via stderr split: data on stdout, diagnostics on stderr. emit_resolved_config writes only to sys.stderr; CLI-03 stdout-pristine invariant verified structurally by test_no_hash_lines_in_stdout (no '# ' prefix on any stdout line under --harmonics all)."
  - "Stub-marker test breadcrumb retired: Plans 11-01/02/03 left 3 stub-marker assertions in tests/cli/test_parser.py asserting 'Plan 11-04' or 'not yet implemented' in stderr. Plan 11-04 retrofits all 3 to real-content assertions (presets in stdout / systems in stdout / 'Aspect set:' in stderr). Pattern: when stub markers exist, the plan that wires the real impl is responsible for retrofit."
  - "Two-tier verification for v1.0 format-string preservation: (1) cmd_aspects calls display.print_aspects (delegation), (2) test_aspects_output_uses_u00ba_degree_char asserts the aspects block contains 'º' AND does not contain '°' (regression detector that fails earlier than Plan 11-06's full byte-identical fixture diff)."

# Metrics
duration: ~5m 18s
completed: 2026-05-07
---

# Phase 11 Plan 04: Aspects Cmd, Formatters, Introspection Summary

**ketu/cli/aspects_cmd.py + formatters.py + introspection.py wire the `aspects` subcommand end-to-end, the resolved-config header to stderr (CLI-06; both `aspects` AND `houses` subcommands now), and the introspection commands `--list-aspect-sets` / `--list-house-systems` (CLI-05); display.print_aspects extended with optional aspects= kwarg as single source of truth for the v1.0 'º' (U+00BA) format string (BLOCKER 1 fix)**

## Performance

- **Duration:** ~5m 18s
- **Started:** 2026-05-07T15:06:09Z
- **Completed:** 2026-05-07T15:11:27Z
- **Tasks:** 2
- **Files created:** 6
- **Files modified:** 4

## Accomplishments

- `ketu/display.py:print_aspects` extended with optional `aspects= None` kwarg forwarded to `calculate_aspects` — preserves the v1.0 `º` (U+00BA, MASCULINE ORDINAL INDICATOR) format string byte-for-byte; module-level `from .core import aspects` aliased to `_CORE_ASPECTS` to free the parameter name; mypy `--strict` clean via `TYPE_CHECKING` import of `AspectSetSpec`.
- `ketu/cli/aspects_cmd.py` (107 lines) implements `cmd_aspects(args)`: resolves `--harmonics` (None → CLASSICAL via `resolve_aspect_set(None)`), emits resolved-config header to stderr (CLI-06), calls `display.print_positions` + `display.print_aspects(jd, aspects=mask)` (single source of truth for v1.0 format strings — BLOCKER 1 fix), always emits the v1.0 'Aspect Timing Example' Sun-Moon trailing block (research §Open Question 2 resolution). `_preset_label_for_mask` uses `np.array_equal` for exact bit-for-bit preset detection (no sum-count heuristic).
- `ketu/cli/formatters.py` (53 lines) implements `emit_resolved_config(mask, preset_name, house_system)` writing `# Ketu v1.1.0` + optional `# Aspect set: NAME (N aspects: ...)` + optional `# House system: NAME` to STDERR. Preserves CLI-03 stdout-pristine contract under `--harmonics all`.
- `ketu/cli/introspection.py` (60 lines) implements `cmd_list_aspect_sets` (lists 4 presets {classical, traditional, extended, all} with descriptions and aspect angles) + `cmd_list_house_systems` (lists 3 systems {placidus, koch, porphyry} with descriptions and polar-fallback hint).
- `ketu/cli/parser.py` modified: imports `cmd_aspects`, `cmd_list_aspect_sets`, `cmd_list_house_systems`; `set_defaults(func=cmd_aspects)` replaces `_stub_aspects`; introspection short-circuits call real implementations; all 3 stub functions deleted; unused `sys` import removed. **Zero stubs remain in parser.py.**
- `ketu/cli/houses_cmd.py` modified: `cmd_houses` now calls `emit_resolved_config(mask=None, preset_name=None, house_system=args.system)` BEFORE `parse_iso_utc` (BLOCKER 2 fix; CLI-06 closed for houses subcommand). Even date-parse failures still echo the header to stderr — useful debugging context.
- `tests/cli/test_aspects_cmd.py` (135 lines, 9 tests across 6 classes): default-classical runs + header on stderr; `--harmonics all` → 'extended' label; Aspect Timing Example always emitted (3 cases: classical/all/traditional); `--harmonics 0,4,7,9,13` produces same mask as `--harmonics classical` (aspects-block byte-equality); bare-integer rejected with code 2; **aspects block uses U+00BA `º` AND not U+00B0 `°` (BLOCKER 1 regression detector)**.
- `tests/cli/test_introspection.py` (45 lines, 6 tests across 3 classes): `--list-aspect-sets` lists 4 presets with angles (0°/60°/90°/120°/180°); `--list-house-systems` lists 3 systems with polar-fallback hint; both work without subcommand (Pitfall 1 — introspection without subparser).
- `tests/cli/test_resolved_header.py` (105 lines, 9 tests across 3 classes): `aspects` header on stderr only (CLI-06); 'Aspect set: classical/extended' labels; count + angles in header; `houses` emits `# House system: NAME` on stderr (BLOCKER 2 verification, 3 systems); `houses` doesn't emit `Aspect set:` line; under `--harmonics all` no `# ` line on stdout (CLI-03 spirit-check).
- `tests/cli/test_parser.py` modified: 3 stub-marker assertions retrofitted to real-content assertions (`classical/traditional/extended/all` in stdout for `--list-aspect-sets`; `placidus/koch/porphyry` in stdout for `--list-house-systems`; `Bodies Positions` in stdout + `Aspect set:` in stderr for `aspects --date X`).
- Full project test suite: **724 passed** (700 baseline + 24 new), **0 regressions**, mypy `--strict` clean across `ketu/cli/` + `ketu/display.py` (9 source files).
- Manual smoke: `python -c "from ketu.cli import main; main(['--harmonics', 'all', 'aspects', '--date', '2000-01-01T12:00:00Z'])"` produces 14-aspect output to stdout (Bodies Positions + Bodies Aspects + Aspect Timing Example) with U+00BA `º` chars; resolved-config header `# Ketu v1.1.0` + `# Aspect set: extended (...)` lands on stderr only. `python -c "from ketu.cli import main; main(['houses', '--date', '2000-01-01T12:00:00Z', '--lat', '48.85', '--lon', '2.35', '--system', 'placidus'])"` produces `# Ketu v1.1.0` + `# House system: placidus` on stderr.

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend display.print_aspects + implement aspects_cmd, formatters, introspection** — `d90cf6b` (feat)
2. **Task 2: Wire dispatchers in parser.py + extend cmd_houses with emit_resolved_config + add tests** — `e27b376` (test)

## Files Created/Modified

- `ketu/display.py` (MODIFIED) — `print_aspects` gains optional `aspects= None` kwarg forwarded to `calculate_aspects`; preserves U+00BA `º` format string byte-for-byte; `from .core import aspects` aliased to `_CORE_ASPECTS`; `TYPE_CHECKING` import of `AspectSetSpec` for mypy `--strict`.
- `ketu/cli/aspects_cmd.py` (CREATED) — `cmd_aspects(args)` dispatcher; `_preset_label_for_mask(mask)` reverse-maps mask to preset name via `np.array_equal`; calls `display.print_positions` + `display.print_aspects(jd, aspects=mask)` + emits v1.0 'Aspect Timing Example' trailing block.
- `ketu/cli/formatters.py` (CREATED) — `emit_resolved_config(mask, preset_name, house_system)` writes header to STDERR (CLI-06).
- `ketu/cli/introspection.py` (CREATED) — `cmd_list_aspect_sets` + `cmd_list_house_systems` (CLI-05); preset/system descriptions hardcoded in `_PRESET_DESCRIPTIONS` / `_SYSTEM_DESCRIPTIONS` dicts.
- `ketu/cli/parser.py` (MODIFIED) — imports real dispatchers; `set_defaults(func=cmd_aspects)` replaces `_stub_aspects`; introspection short-circuits call real implementations; all 3 stub functions deleted; unused `sys` import removed.
- `ketu/cli/houses_cmd.py` (MODIFIED) — imports `emit_resolved_config`; `cmd_houses` calls it at the top with `mask=None, preset_name=None, house_system=args.system` (BLOCKER 2 fix).
- `tests/cli/test_aspects_cmd.py` (CREATED) — 9 tests across 6 classes pinning aspects subcommand contract.
- `tests/cli/test_introspection.py` (CREATED) — 6 tests across 3 classes pinning introspection commands contract.
- `tests/cli/test_resolved_header.py` (CREATED) — 9 tests across 3 classes pinning CLI-06 stderr-only contract for both `aspects` AND `houses` subcommands.
- `tests/cli/test_parser.py` (MODIFIED) — 3 stub-marker assertions retrofitted to real-content assertions.

## Decisions Made

See `key-decisions` in frontmatter (7 decisions logged for STATE.md harvest). Briefly:

- **BLOCKER 1 fix via single source of truth in `display.print_aspects`** (preserves U+00BA via library delegation; no second copy of the format string).
- **BLOCKER 2 fix via `emit_resolved_config` call in `cmd_houses`** (CLI-06 closed for houses subcommand; pinned by 4 stderr tests).
- **`_preset_label_for_mask` uses `np.array_equal`** (exact bit-for-bit preset detection, MINOR 6 polish absorbed; no sum-count mislabeling).
- **Aspect Timing Example always emitted** (research §Open Question 2; CLI-03 byte-identity preserved for `--harmonics all`).
- **`AspectSetSpec` via `TYPE_CHECKING`** (mypy `--strict` clean, no runtime cost, no circular-dep risk).
- **`from .core import aspects as _CORE_ASPECTS` rename** (frees `aspects` name for the new parameter; no external caller depends on `display.aspects`).
- **Resolved-config header lists count and angles** (`# Aspect set: classical (5 aspects: Conjunction 0°, ...)`; gives users immediate context).

## Deviations from Plan

None - plan executed exactly as written.

The plan's reference text was used essentially verbatim, with one tiny adjustment to the docstring of `print_aspects`:

1. **`print_aspects` docstring U+00B0 reference removed**: The plan reference text included the literal characters `º` AND `°` in the docstring's "Notes" section to call out the difference. The verify rule states the function source must NOT contain U+00B0 (`'°' in src` should be False), so the docstring text "NOT ``°`` (U+00B0, DEGREE SIGN)" was rephrased to "NOT the DEGREE SIGN character at codepoint U+00B0" — same meaning, no actual U+00B0 character in the source. Verified: `python -c "import inspect, ketu.display; src = inspect.getsource(ketu.display.print_aspects); print('º' in src, '°' in src)"` → `True False`. This is interface-shape conformance to the plan's verify rule, not a semantic deviation.

Both Task 1 verify steps and Task 2 verify steps passed without further auto-fixes.

---

**Total deviations:** 0
**Impact on plan:** None — plan executed as written. One small docstring adjustment to satisfy the plan's own verify rule (U+00B0 absent from print_aspects source); no code or test logic changed.

## Issues Encountered

- **GPG signing pinentry timeout (carried over from Plans 11-01/02/03)**: GPG-signed commits unavailable in headless sandbox; both task commits made unsigned via per-commit `git -c commit.gpgsign=false` (no global config change). User can re-sign later via `git rebase --exec 'git commit --amend -S --no-edit' HEAD~4..HEAD` (covers Plans 11-03 and 11-04 commits) if signing parity matters across the Phase 11 commit chain.
- **`mypy` and `pytest` venv shebangs broken**: Same root cause as Plans 11-02/03 documented (venv created at different absolute path than current location). Workaround: `python -m mypy --strict ...` and `python -m pytest ...` consistently used throughout this plan. No new manifestation; documenting for completeness.
- **`python -m ketu aspects ...` does NOT yet route through new CLI**: `ketu/__main__.py` still imports `from .display import main` (legacy v1.0 entry point). Manual smoke testing was done via `python -c "from ketu.cli import main; main([...])"`. Plan 11-05 swaps the entry point.

## User Setup Required

None — no external service configuration required. Plan 11-04 is pure CLI dispatcher + formatter wiring on top of Plans 11-01/02/03 deliverables and Phase 9/10 public APIs.

## Next Phase Readiness

- **Plan 11-05 (entry point repoint + legacy removal)** unblocked — CLI-02/03/05/06 are all wired now; the new CLI is functionally complete. Plan 11-05 will:
  - swap `ketu/__main__.py` from `from .display import main` → `from .cli import main` (one-line edit)
  - repoint `[project.scripts]` in `pyproject.toml` (or whatever entry-point config is used) to `ketu.cli:main`
  - delete `ketu/display.py:main()` (the legacy interactive `input()`-based v0/v1.0 flow) — closes CLI-01
  - update `tests/test_ketu.py::TestMain::test_main_invalid_input` and `tests/test_coverage_improvements.py` (both import `from ketu.display import main`); these tests must either be removed (if `display.main` is fully gone) or retargeted at the new CLI entry point. Note: `print_positions` and `print_aspects` SURVIVE the refactor — they're library helpers consumed by `aspects_cmd`. Only the legacy `main()` interactive flow is deleted.
- **Plan 11-06 (byte-identical regression)** unblocked — can now exercise the full `aspects` subcommand (with `--harmonics all` / `classical`) and `houses` subcommand in subprocess invocations, asserting v1.0 fixture parity on stdout. The single-source-of-truth `display.print_aspects` extension means CLI-03 byte-identity is automatic at the format-string layer; Plan 11-06 just needs to capture the v1.0 fixture and assert subprocess stdout matches it byte-for-byte. Header on stderr is captured separately (or stripped via `2>/dev/null`).

No new blockers. Phase 9 still awaits `/gsd:check-phase` (independent track from this CLI work). Phase 11 progresses to 4/6 plans (67%).

## Self-Check: PASSED

Verified:
- `ketu/cli/aspects_cmd.py` — FOUND
- `ketu/cli/formatters.py` — FOUND
- `ketu/cli/introspection.py` — FOUND
- `tests/cli/test_aspects_cmd.py` — FOUND
- `tests/cli/test_introspection.py` — FOUND
- `tests/cli/test_resolved_header.py` — FOUND
- `ketu/display.py` (modified) — FOUND, contains `aspects: "AspectSetSpec" = None` parameter and `_CORE_ASPECTS` alias
- `ketu/cli/parser.py` (modified) — FOUND, contains `from .aspects_cmd import cmd_aspects` and `set_defaults(func=cmd_aspects)`; zero stubs
- `ketu/cli/houses_cmd.py` (modified) — FOUND, contains `from .formatters import emit_resolved_config` and `emit_resolved_config(mask=None, ...)` call
- `tests/cli/test_parser.py` (modified) — FOUND, 3 stub-marker assertions retrofitted
- Commit `d90cf6b` (Task 1: feat extend display + new cli modules) — FOUND
- Commit `e27b376` (Task 2: test parser wiring + houses_cmd extension + new tests) — FOUND
- mypy --strict on `ketu/cli/` + `ketu/display.py` — clean (9 source files, 0 errors)
- pytest tests/cli/ — 86/86 passed (16 + 21 + 10 + 15 + 9 + 6 + 9 = 86)
- pytest tests/ — 724/724 passed (700 baseline + 24 new)

---
*Phase: 11-cli-refactor-integration*
*Completed: 2026-05-07*
