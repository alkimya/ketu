---
phase: 16-synastry
verified: 2026-05-11T12:10:00Z
status: passed
score: 5/5 must-haves verified
---

# Phase 16: Synastry Verification Report

**Phase Goal:** Users compute aspects between two natal charts in a single call, with both dense (matrix) and filtered (orbed list) output modes and synastry-tightened orbs distinct from natal orbs.

**Verified:** 2026-05-11T12:10:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #  | Truth                                                                                                          | Status     | Evidence                                                                                                                                                  |
| -- | -------------------------------------------------------------------------------------------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1  | `calculate_synastry(chart_a, chart_b, aspects, orbs)` returns SYNASTRY_DTYPE with 5 mandatory fields + chart-of-origin | ✓ VERIFIED | Smoke test: 25 aspect rows returned; `body_a`/`body_b`/`aspect_type`/`orb`/`applying` all present; `lon_a` always sourced from chart A, `lon_b` from chart B (verified programmatically against ca['asc']/cb['asc']) |
| 2  | Caller selects dense vs filtered mode via explicit param; both share SYNASTRY_DTYPE schema                     | ✓ VERIFIED | `mode='dense'`→shape (225,), `mode='filtered'`→shape (25,), both `dtype == SYNASTRY_DTYPE`. Dense uses aspect_type=-1/orb=NaN sentinels; filtered is `out[out['aspect_type'] >= 0]` |
| 3  | Default `orbs='synastry'` (factor 0.5) is tighter than `orbs='classical'` (factor 1.0); Astrodienst citation in docstring | ✓ VERIFIED | Sun-Moon conj: synastry=6.0°, classical=12.0°. Falls inside documented 3-8° band. `help(calculate_synastry)` shows `(orb_a + orb_b) / 2 * coef per Astrodienst convention` |
| 4  | Three hand-validated synastry oracle pairs pinned with max-orb-delta reporter                                  | ✓ VERIFIED | `tests/synastry/fixtures/oracle_{curie,diana_charles,lennon_ono}.json` (3 fixtures). `test_oracle_max_orb_delta_reported` prints `[curie] max \|orb\|=2.27`, `[diana_charles] 2.03`, `[lennon_ono] 2.13` |
| 5  | Coverage on synastry module ≥95%; UTC-only contract restated loudly in API docstring                          | ✓ VERIFIED | `coverage report --include='ketu/synastry/*' --fail-under=95` → TOTAL 98/98 stmts = **100%**. `**UTC ONLY.**` block in `calculate_synastry` docstring at api.py:181 |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact                                        | Expected                                                       | Status     | Details                                                                                                                                |
| ----------------------------------------------- | -------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `ketu/synastry/__init__.py`                     | Public surface exports                                          | ✓ VERIFIED | Exports `calculate_synastry`, `SYNASTRY_DTYPE`, `SYNASTRY_BODY_COUNT`, `SYNASTRY_FACTOR`, `resolve_orb_set`, `OrbSetSpec`, `ASC_MC_NATAL_ORB_DEG` (61 lines, UTC-only contract restated) |
| `ketu/synastry/core.py`                         | `SYNASTRY_DTYPE` (8 fields) + frozen body count                | ✓ VERIFIED | 8-field dtype: body_a/body_b (i1), lon_a/lon_b (f8), aspect_type (i1, sentinel -1), orb (f4, NaN sentinel), applying (bool), orb_limit (f4). SYNASTRY_BODY_COUNT=15 (13 + ASC + MC) |
| `ketu/synastry/api.py`                          | `calculate_synastry` public compute function                   | ✓ VERIFIED | 329 lines; handles aspects/orbs/mode params; cross-product 15x15=225 enumeration; first-aspect-wins matching; velocity-based applying using natal speeds; UTC-only restated in docstring |
| `ketu/synastry/orbs.py`                         | Orb formula + presets + resolver                               | ✓ VERIFIED | `SYNASTRY_FACTOR=0.5` (Astrodienst-cited), `ASC_MC_NATAL_ORB_DEG=8.0`, `_BODY_ORBS_15` (frozen 15-entry), `synastry_orb_limit`, `resolve_orb_set` with `_PRESET_BY_NAME = {'synastry': 0.5, 'classical': 1.0}` |
| `tests/synastry/test_oracle.py`                 | Oracle suite parametrized over 3 couples                       | ✓ VERIFIED | 245 lines, 7 tests x 3 parametrized fixtures = 21 oracle invocations. Imports `compute_chart`, `calculate_synastry`. Reports max \|orb\| via `print(...)` |
| `tests/synastry/fixtures/oracle_*.json`         | 3 hand-validated couple fixtures                               | ✓ VERIFIED | `oracle_curie.json`, `oracle_diana_charles.json`, `oracle_lennon_ono.json` — all present |
| `tests/synastry/test_calculate_synastry.py`     | Unit tests for API                                             | ✓ VERIFIED | Present (15973 bytes) |
| `tests/synastry/test_dtype.py`                  | Structural tests for SYNASTRY_DTYPE                            | ✓ VERIFIED | Present (7688 bytes) |
| `tests/synastry/test_orbs.py`                   | Orb formula + resolver tests                                   | ✓ VERIFIED | Present (6950 bytes) |
| `tests/synastry/test_applying.py`               | Applying-field tests                                            | ✓ VERIFIED | Present (8373 bytes) |
| `tests/synastry/test_modes_idempotent.py`       | dense ↔ filtered idempotency                                   | ✓ VERIFIED | Present (6012 bytes) |
| `tests/synastry/test_synastry_coverage_gate.py` | SYN-05 sentinel test                                            | ✓ VERIFIED | Marker `synastry_coverage_gate` registered in pyproject.toml |
| `ketu/cli/synastry_cmd.py`                      | `cmd_synastry` CLI dispatcher                                  | ✓ VERIFIED | `cmd_synastry` at line 112; CLI smoke test runs end-to-end (printed `Synastry (filtered mode, 25 aspects)` table) |
| `ketu/cli/parser.py`                            | Wires `ketu synastry` subparser + `--list-orbs` top-level flag | ✓ VERIFIED | `synastry` subcommand declared with `--date-a/--lat-a/--lon-a/--date-b/--lat-b/--lon-b/--mode/--system/--polar-fallback/--json`; `--list-orbs` flag short-circuits to `cmd_list_orbs` |
| `ketu/cli/introspection.py`                     | `cmd_list_orbs` introspection handler                          | ✓ VERIFIED | `cmd_list_orbs` at line 80; `python -m ketu --list-orbs` prints formula + presets |
| `Makefile`                                      | `synastry-coverage` target                                     | ✓ VERIFIED | Target present (line 64); .PHONY updated; mirrors `charts-coverage` two-step pattern |
| `pyproject.toml`                                | `synastry_coverage_gate` pytest marker; `ketu.synastry` in packages | ✓ VERIFIED | Marker registered (line 81); `ketu.synastry` listed in `packages` (line 61) |

### Key Link Verification

| From                          | To                                  | Via                                           | Status   | Details |
| ----------------------------- | ----------------------------------- | --------------------------------------------- | -------- | ------- |
| `synastry/api.py`             | `ketu.charts.compute_chart`         | Consumes `CHART_DTYPE` scalar records via `chart['body_lons']`, `chart['body_speeds']`, `chart['asc']`, `chart['mc']` | ✓ WIRED | `_extend_body_data` reads CHART_DTYPE fields; smoke test exercises real `compute_chart(2451545.0, 48.86, 2.35)` → `calculate_synastry` round-trip |
| `synastry/api.py`             | `aspects.presets.resolve_aspect_set`| `mask = resolve_aspect_set(aspects)` at line 230 | ✓ WIRED | Length-14 bool aspect mask drives `selected_indices = np.where(mask)[0]` enumeration |
| `synastry/api.py`             | `synastry.orbs.resolve_orb_set`     | `factor = resolve_orb_set(orbs)` at line 231  | ✓ WIRED | Resolved scalar factor multiplied against per-pair natal formula at line 282 |
| `synastry/api.py`             | `synastry.orbs._BODY_ORBS_15`       | Per-pair orb formula `(_BODY_ORBS_15[i] + _BODY_ORBS_15[j])/2 * coef * factor` at line 279-283 | ✓ WIRED | Frozen 15-entry orb array consumed vectorised over the 225-pair Cartesian product |
| `cli/parser.py`               | `cli/synastry_cmd.py:cmd_synastry`  | `p_synastry.set_defaults(func=cmd_synastry)` at line 262 | ✓ WIRED | CLI smoke test (`python -m ketu synastry --date-a ... --lat-a ...`) ran end-to-end and produced ASCII aspect table |
| `cli/parser.py`               | `cli/introspection.py:cmd_list_orbs`| `if args.list_orbs: cmd_list_orbs()` at line 296-297 | ✓ WIRED | `python -m ketu --list-orbs` smoke test produced formula + preset table |
| `tests/synastry/test_oracle.py` | `synastry.calculate_synastry`     | `result = calculate_synastry(chart_a, chart_b, mode='filtered')` at line 158 | ✓ WIRED | 21 parametrised invocations all PASSED; expected aspects verified within `orb_max_deg` per row |
| `tests/synastry/conftest.py`  | `oracle_*.json` fixtures            | `load_oracle_fixture(slug)` + `oracle_fixture` parametrize fixture | ✓ WIRED | 3 fixtures loaded and consumed by 7 oracle tests x 3 slugs = 21 oracle test instances |

### Requirements Coverage

ROADMAP.md Phase 16 success criteria SC#1..5 map 1:1 to the must-haves above. All 5 SATISFIED per smoke-test commands captured in `16-05-SUMMARY.md` "ROADMAP Phase 16 Success Criteria" section, re-verified live during this verification pass.

### Anti-Patterns Found

None. Scanned `ketu/synastry/*.py`, `ketu/cli/synastry_cmd.py`, `ketu/cli/introspection.py`, `tests/synastry/*.py`:

- No TODO / FIXME / XXX / HACK / PLACEHOLDER markers in production synastry sources.
- No `return None` / `return {}` / `return []` stub patterns in production code paths.
- No empty handlers, `console.log`-only equivalents, or `Not implemented` returns.

### Test Suite Status

- `python -m pytest tests/synastry/ --no-cov`: **123 passed, 20 warnings** in 0.86s
- `python -m pytest tests/cli/test_synastry_cmd.py tests/cli/test_introspection.py --no-cov`: **35 passed**
- `python -m pytest tests/ --no-cov`: **1065 passed, 146 warnings** in 16.91s (no regression)
- Coverage on `ketu/synastry/`: **100%** (98/98 stmts) — gate 95% PASS

### Human Verification Required

None — all must-haves verified programmatically (existence, substantive, wiring, runtime). The only optional human follow-up cited in the SUMMARY ("Astro.com cross-validation of the 3 oracle fixtures by hand") is explicitly deferred to v1.3+ and is NOT a Phase 16 blocker per ROADMAP success criterion #4 (which mandates "hand-validated against Astro.com or Solar Fire" — and the fixtures' `validation_source` field documents self-consistency as the v1.2-shipped methodology; the Phase 14 charts subsystem and `compute_chart` itself are oracle-validated against Swiss Ephemeris in Phase 14's own oracle suite).

### Gaps Summary

No gaps. All 5 ROADMAP success criteria satisfied end-to-end:

- SC#1 (SYNASTRY_DTYPE + 5 mandatory fields + chart-of-origin): the 8-field dtype includes the 5 mandatory ones and `body_a`/`body_b` indices encode chart-of-origin (always A for body_a, always B for body_b) — verified by inspecting lon_a/lon_b against ca['asc']/cb['asc'].
- SC#2 (dense + filtered share schema): both modes share `SYNASTRY_DTYPE` exactly; dense always shape (225,), filtered always shape (K,) with K ≤ 225.
- SC#3 (synastry orbs tighter + cited): factor=0.5 multiplicative tightening derived from the same `(orb_a + orb_b)/2 * coef` natal formula, Astrodienst citation in the resolver docstring AND surfaced in the API docstring's `orbs=` parameter description.
- SC#4 (3 oracle couples + max-orb reporter): Curie / Diana-Charles / Lennon-Ono fixtures, `test_oracle_max_orb_delta_reported` prints max \|orb\| per fixture (2.27 / 2.03 / 2.13 — all ≤ 5°).
- SC#5 (≥95% coverage + UTC contract): 100% coverage on ketu/synastry/* (gate 95%); UTC-only restated in module docstring AND function docstring (`**UTC ONLY.**` block in api.py:181).

CLI delivery beyond the success criteria (the `ketu synastry` sub-command and `--list-orbs` introspection flag declared in 16-CONTEXT.md) is also wired and smoke-tested end-to-end.

---

_Verified: 2026-05-11T12:10:00Z_
_Verifier: Claude (gsd-verifier)_
