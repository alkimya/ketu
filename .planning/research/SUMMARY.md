# Research Summary: Ketu v1.1 — Flexibility & Houses

**Synthesized from:** STACK.md, FEATURES.md, ARCHITECTURE.md, PITFALLS.md
**Date:** 2026-05-06
**Overall Confidence:** HIGH

---

## Executive Summary

Ketu v1.1 extends a well-validated, zero-dependency library (1.0.0, 250 tests, 91% coverage) with three orthogonal features:

1. **Configurable aspect sets** (5 Ptolemaic majors as new default; harmonics 9/10/11/12 opt-in)
2. **Astrological house calculation** (Placidus + Koch, extensible registry pattern)
3. **Lilith definition + verification** (formula audit against Swiss Ephemeris)

All four researchers converge on the same judgment: the work is **additive**, not transformative. No new runtime dependencies are needed — the pure-NumPy, pure-stdlib contract is preserved. The one new dependency (`pysweph>=2.10.3.6`) is test-only and AGPL-safe (test code isn't distributed in the wheel).

The dominant risk is the intersection of backward compatibility and correctness: `core.aspects` is a public positionally-indexed constant that must remain 14-row append-only; Placidus is undefined above 66.56° latitude and must fail explicitly; Lilith must be defined in writing (Mean vs True vs Asteroid 1181) before code changes. These are non-negotiable design gates.

---

## Stack Additions (v1.1)

- **No new runtime dependencies.** Pure-NumPy contract preserved.
- **Test-only dependency:** `pysweph>=2.10.3.6` (NOT `pyswisseph`). The original `pyswisseph` is unmaintained since 2025; `pysweph` fork by sailorfe shipped 2026-02-19 with cp38–cp313 wheels. Imports as `import swisseph` (existing `[[tool.mypy.overrides]] module = ["swisseph.*"]` works as-is). Goes in `[project.optional-dependencies] test`.
- **CLI:** stdlib `argparse` with subparsers + `set_defaults(func=...)` dispatch. Use `type=callable` (not custom `Action`) for `--harmonics` parsing. **Don't add `click` or `typer`** (runtime deps; breaks NumPy-only contract).
- **Algorithms** are simple enough to vectorize in NumPy without SciPy.

## Feature Categories

### Table Stakes (must-have for v1.1)

- **5 Ptolemaic majors as default** (conjunction, opposition, trine, square, sextile) — universal in astrological libraries
- **Named aspect presets:** `classical` (5), `traditional` (7 = harmonic 12), `extended` (14 = legacy/v1.0)
- **CLI escape hatch:** `--harmonics all` returns v1.0 14-aspect output for backward compat
- **House cusps:** 12 ecliptic longitudes (NumPy array, 0-indexed)
- **Angles output:** ASC, MC (and optionally ARMC, Vertex)
- **Two house systems:** Placidus + Koch
- **Polar fallback:** `HighLatitudeError` or `polar_fallback` parameter (`raise` / `porphyry` / `whole_sign`)
- **Lilith definition document** before code: Mean Apogee, tropical longitude, Chapront-Touz/Francou source
- **Lilith reference tests:** 5+ dates spanning 1900-2050 against Swiss Ephemeris `SE_MEAN_APOG`

### Differentiators (Ketu-distinctive)

- **Vectorized over date arrays** for body-position-driven calculations (aspects, transits)
- **Explicit `harmonic` + `category` fields** added to `core.aspects` structured array (non-breaking, append-only)
- **Pure NumPy** house implementation (no SciPy dependency)
- **CLI echoes resolved config** in output (`# Aspect set: classical [0°, 60°, 90°, 120°, 180°]`)

### Anti-features (explicit NO)

- Asteroid Lilith #1181 — defer to future milestone
- True/Osculating Lilith — out of scope for v1.1 (could be added in v1.2 if requested)
- Additional house systems (Whole Sign, Equal, Porphyry, Regiomontanus...) — architecture supports them, defer concrete impl
- Timezone handling — UTC remains required
- Bare `--harmonics 12` integers — too ambiguous (force named presets or explicit angle list)

## Architecture Integration

### New Modules

```
ketu/
├── aspects/
│   └── presets.py          # NEW: classical/traditional/extended preset views
├── houses/                  # NEW subpackage
│   ├── __init__.py          # Public API: calculate_houses(), HOUSES_DTYPE
│   ├── _angles.py           # Shared LST/obliquity primitives
│   ├── placidus.py          # Placidus iterative algorithm
│   ├── koch.py              # Koch closed-form algorithm
│   └── registry.py          # System dispatcher (extensibility hook)
└── (existing modules)
```

### Modified Modules

- `ketu/core.py` — keep `aspects` array length 14 + add `harmonic` + `category` fields (non-breaking; existing column types preserved)
- `ketu/aspects/calculator.py`, `aspect_windows.py`, `transits.py`, `aspects/timelines.py` — accept `aspect_set` / `selected_indices` parameter, defaulting to legacy 14
- `ketu/ephemeris/planets.py` — fix Lilith formula; delete broken `calculate_house_cusps` stub (line 270)
- `ketu/ephemeris/orbital.py` — fix Lilith epoch constant if needed (currently `83.3532°` at line 591 — verify)
- `ketu/ephemeris/time.py` — audit GMST/LST precision for houses (may need tightening from ~0.01° to ~0.001°)
- `ketu/display.py` (or new `ketu/__main__.py`) — argparse subcommands, `--harmonics SPEC`, `houses` subcommand, `--list-aspect-sets`, `--list-house-systems`
- `ketu/__init__.py` — add new public exports to `__all__`

### Decoupling Discovery

- **`cycles/` is decoupled** from `core.aspects` — defines its own `MAJOR_ASPECTS` array. Aspect refactor does NOT ripple into cycles or complex.py. Significantly narrows blast radius.
- `generate_aspect_timeline()` already defaults to 5 majors. The "default 14" problem only lives in `calculate_aspects()`, `calculate_aspects_vectorized()`, `calculate_aspects_batch()`.

## Critical Pitfalls (and prevention)

| Pitfall | Prevention |
|---------|------------|
| Silent breaking change to `core.aspects` shape (Kala uses positional indexing) | Append-only invariant test; document order as public contract |
| Cache returning stale results after config change | Include config hash in cache keys |
| Wrong Lilith picked (Mean vs True vs Asteroid #1181) | LILITH_DEFINITION.md FIRST; cross-validate 2 sources |
| Lilith fix breaks downstream stored values | CHANGELOG numerical-behavior section; quantify magnitude; notify Kala/Surya |
| Placidus undefined at lat > 66.56° → silent NaN | Polar fallback (Porphyry) or explicit error; tests at 70°/80° |
| LST precision insufficient for houses | Audit `ephemeris/time.py` BEFORE Phase 3; verify Ascendant within 1 arcmin of Astro.com |
| Placidus iterative non-convergence | Iteration cap (~50); NaN-recovery; scalar loop is fine (don't over-vectorize) |
| Inconsistent aspect filtering across modules | Single `KetuConfig` threaded everywhere; integration test |
| `--harmonics 12` ambiguity | Force named presets; reject bare ints |
| CLI default change breaks scripts | `--harmonics all` legacy escape hatch; CHANGELOG breaking banner |
| Performance regression (filter in inner loop) | Resolve filter mask once at API entry; benchmark gate |
| Coverage drop adding houses | CI gate at 90% project / 85% module; target 95% for new code |
| numpydoc/mypy drift on new modules | mypy strict + sphinx -W + interrogate ≥95% in CI |
| Missing top-level exports | `tests/test_public_api.py` smoke test |

## Suggested Phase Structure

**5 phases** (4 delivery + 1 release):

| # | Phase | Goal | Depends on | Parallelizable with |
|---|-------|------|-----------|---------------------|
| 8 | Lilith Verification & Fix | Establish pysweph oracle; verify/fix Lilith formula | — | 9, 10 |
| 9 | Configurable Aspects | Default 5 majors; preset views; legacy `all` flag | — | 8, 10 |
| 10 | Houses Module | Placidus + Koch with polar fallback; LST audit | — | 8, 9 |
| 11 | CLI Integration | argparse subcommands; `--harmonics`; `houses`; introspection | 9 AND 10 | — |
| 12 | Release Preparation | v1.1.0 bump; CHANGELOG; UPGRADING.md; PyPI publish | 8, 9, 10, 11 | — |

Phase numbering continues from v1.0 (last was Phase 7).

**Parallelization note:** Phases 8, 9, 10 are mutually independent (disjoint modules). Phase 11 hard-blocks on both 9 and 10. Phase 12 is last.

## Open Questions for Phase Planning

- **Lilith formula accuracy:** `83.3532°` constant at `ephemeris/orbital.py:591` needs empirical pysweph comparison — Phase 8 first task resolves this. If correction >0.5°, quantify Kala/Surya impact before release.
- **LST/obliquity precision:** Existing `ephemeris/time.py` tuned for body positions (~0.01°); houses need ~0.001°. Phase 10 must include precision audit + Ascendant reference test before implementation.
- **Kala aspect-count dependency:** Whether `KetuAdapter` hardcodes 14 aspect rows from `calculate_aspects_batch()` is unverified. Needs check with Kala maintainer before Phase 9 merge.
- **`calculate_house_cusps` deprecation cycle:** Keep stub for one minor with `DeprecationWarning`, or remove immediately? (Currently returns wrong equal-house results — recommend immediate removal in Phase 10.)
- **CLI no-arg behavior:** Old interactive `input()` prompt or print help? UX call.

## Stack Additions Summary

**Stack additions:** Test-only `pysweph>=2.10.3.6` (Swiss Ephemeris fork, AGPL, replaces unmaintained pyswisseph). No runtime deps.

**Feature table stakes:** 5 Ptolemaic majors default + named presets; CLI escape hatch `--harmonics all`; Placidus+Koch with polar fallback; Lilith DEFINITION.md + 5+ reference dates; vectorization over date arrays.

**Watch Out For:**

1. `core.aspects` must stay append-only (Kala uses positional indexing)
2. Placidus polar undefined above 66.56° — explicit fallback required
3. Lilith definition (Mean vs True vs #1181) must be written before code
4. LST precision audit before house implementation
5. `--harmonics 12` ambiguity — force named presets
6. Cache keys must include config (aspect set, house system)

---

*Synthesized: 2026-05-06*
