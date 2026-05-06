# Phase 8: Lilith Verification & Fix — Research

**Researched:** 2026-05-06
**Domain:** Mean lunar apogee calculation, Swiss Ephemeris cross-checking, test-only optional dependencies (Python packaging)
**Confidence:** HIGH

> No `08-CONTEXT.md` exists for this phase — research proceeds from REQUIREMENTS.md (LIL-01 .. LIL-05), ROADMAP.md, STATE.md, and direct codebase inspection. No locked decisions to copy verbatim.

---

## Summary

Phase 8 verifies — and only fixes if necessary — the Mean Black Moon Lilith longitude returned by `ketu.ephemeris.orbital.get_lilith_position()` (line 591). The investigation order is **mandatory and inverted from a normal "code first" phase**: definition document → cross-check harness → empirical measurement → conditional fix → release notes.

The current Ketu formula is a single line:

```python
# ketu/ephemeris/orbital.py:591
lilith = normalize_angle(83.3532 + 0.1114040803 * d)   # d = jd - 2451545.0
```

This is the **classical mean longitude of the lunar apogee** (epoch J2000.0, mean rate 0.1114040803°/day ≈ 40.69°/year, full revolution ≈ 8.85 years). Coefficients align with the Chapront-Touzé / Chapront / Francou ELP-2000 reduction used by Swiss Ephemeris's `SE_MEAN_APOG`. **Whether they match `pysweph` to within 0.01° is a measurement, not an assumption** — the whole point of the harness.

The cross-check is straightforward because Swiss Ephemeris's mean apogee is **purely analytical** (Moshier's reduction of ELP-2000-85): no `.se1` ephemeris data files are required, and `swe.calc_ut(jd, swe.MEAN_APOG)` returns tropical ecliptic longitude of date in degrees — the exact same convention Ketu uses. Apples-to-apples. Delta-T concerns are negligible at this rate (Lilith moves ≈ 0.0046°/hour; modern Δ-T ≈ 70 s contributes ≈ 9 × 10⁻⁵° of drift — three orders of magnitude below tolerance).

**Primary recommendation:** Order the plan exactly as the requirements demand — write `LILITH_DEFINITION.md` first (LIL-01), then add `pysweph` to `[project.optional-dependencies].test` (LIL-04), then build a parametrized cross-check harness (LIL-02) gated by `pytest.importorskip("swisseph")`. Run it once. Branch on the result: error ≤ 0.01° → no code change, document conclusion (LIL-05 trivial); error > 0.01° → correct formula, pin regression baselines from `pysweph` itself, document magnitude (LIL-03 + LIL-05).

---

## Standard Stack

### Core (test-only — NOT runtime)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `pysweph` | `>=2.10.3.6` | Reference implementation of `SE_MEAN_APOG` | Community fork of `pyswisseph`, current as of 2026-02-19; same `import swisseph as swe` API; published wheels for Linux/macOS/Windows; supports Python 3.8–3.13 |
| `pytest` | (already in dev) | Parametrized test harness | Idiomatic; `pytest.importorskip` makes test-only dep clean |
| `numpy` | `>=1.20.0` (already runtime) | Angle arithmetic, vectorized comparison | Already in tree |

### Why `pysweph` and not `pyswisseph`

This is locked by STATE.md ("`pysweph>=2.10.3.6` is test-only dependency") and REQUIREMENTS.md (LIL-04 names the package). Verified the choice is sound:

- `pyswisseph` (astrorigin) latest is `2.10.3.2`, last released **June 2023** — stale.
- `pysweph` (community fork) latest is `2.10.3.6`, released **2026-02-19** — current.
- Both packages expose the **same import name** (`import swisseph as swe`) and the same `SE_MEAN_APOG = 12` constant.
- `pysweph` ships pre-built wheels (binary), avoiding a C-toolchain requirement on contributor machines/CI.

### Alternatives considered

| Instead of | Could Use | Why Not |
|------------|-----------|---------|
| `pysweph` | `pyswisseph` 2.10.3.2 | Stale (2023); no behavioural difference for `SE_MEAN_APOG` but project chose the maintained fork; downstream wheel availability may lag |
| `pysweph` | `skyfield` | Doesn't expose mean lunar apogee — Lilith is an astrology-domain quantity not a JPL target |
| `pysweph` | Astro.com web tables (manual) | Not automatable; loses full date-range coverage; not appropriate for a regression suite |
| `pysweph` (test-only) | `pysweph` runtime | **Forbidden** — Pure-NumPy contract (PROJECT.md, ROADMAP.md, REQUIREMENTS.md "Out of Scope"); also AGPL-licensed (Astrodienst) — cannot be a runtime dep of an MIT library |

**Installation (test-only) — exact `pyproject.toml` edit:**

```toml
[project.optional-dependencies]
test = [
    "pysweph>=2.10.3.6",
]
```

Add (do not append to `dependencies`). Verify with `pip install ketu[test]` in a clean venv after editing.

### Existing in tree, leverage as-is

- `ketu.ephemeris.time.utc_to_julian` — produces JD-UT (no Δ-T applied). This **matches** `swe.calc_ut`'s expected input. Use it for fixture construction.
- `tests/test_planets_coverage.py` `_make_jd(year, month, day, hour=12, minute=0)` — copy this pattern verbatim for harness fixtures (line 36-39).
- `pyproject.toml [[tool.mypy.overrides]] module = ["swisseph.*"]` already has `ignore_missing_imports = true` — the test won't break mypy strict.

---

## User Constraints

(No `08-CONTEXT.md` exists. Constraints below are derived from REQUIREMENTS.md / STATE.md / ROADMAP.md — they are **firm** but not from a `discuss-phase` session.)

### Locked by upstream documents

- **Investigation-first ordering is non-negotiable.** LIL-01 (`LILITH_DEFINITION.md`) lands BEFORE any code in `ephemeris/orbital.py` is touched. ROADMAP success criterion #1: *"`LILITH_DEFINITION.md` exists … BEFORE any formula code changes."*
- **`pysweph>=2.10.3.6` is test-only.** Goes into `[project.optional-dependencies].test`. NEVER `dependencies`. Must NOT be pulled into the runtime wheel.
- **5+ dates spanning 1900, 1950, 2000, 2025, 2050.** Exact dates are Claude's discretion within these years; minimum 5.
- **Tolerance is "explicit"** — must be a named, justified constant in the test, not a magic number.
- **Conditional fix branch.** If empirical max error ≤ 0.01° → no code change, definition-document closes the loop. If > 0.01° → fix lands with regression tests pinning the new values, plus magnitude statement in CHANGELOG/UPGRADING.
- **Pure NumPy contract preserved.** No new `dependencies` entries. AGPL-safe (test-only is allowed since AGPL doesn't propagate through development tooling).
- **Mypy strict mode + numpydoc-style docstrings + interrogate ≥95%** apply to any new/modified public code. Cross-check tests are not public API but should still type-check (`module = ["swisseph.*"]` override is already in `pyproject.toml`).
- **DateTime inputs always UTC.** Confirmed; both Ketu and `swe.calc_ut` use JD-UT.
- **`core.aspects` length-14 invariant is unrelated to this phase but reminds us:** changing structured-array dtypes / public-export ordering is out of scope here. `Lilith` is body index 12; that mapping is frozen.

### Claude's discretion

- Exact 5+ dates within the year buckets (1900, 1950, 2000, 2025, 2050). Recommendation: pick non-trivial calendar dates (not Jan 1 12:00 UT for all, since that JD is exactly an integer offset from J2000 — masks rounding bugs).
- Vectorized vs scalar test harness. Recommendation: scalar — comparison is one-shot per date, vectorization adds noise.
- Whether to cache `pysweph` results (e.g. as JSON fixtures). Recommendation: do NOT cache. Fixture freshness is the whole point — recompute every CI run.
- Whether to also cross-check `Rahu`/`Ketu` (mean node) opportunistically. Recommendation: **out of scope** for this phase. If the harness module is well-structured, adding mean-node verification later is a one-decorator change. Note this in the harness docstring as future work but do not implement.

### Deferred (out of scope)

- True / Osculating Lilith (h13). REQUIREMENTS.md "v2 Deferred — LIL2-01".
- Asteroid Lilith #1181. "v2 Deferred — LIL2-02".
- Sidereal Lilith. Not requested.
- Replacing `pyswisseph` history references in `CHANGELOG.md` 0.1.0/0.2.0 entries. Historical record; do not rewrite.
- `pysweph` as runtime dep — explicitly listed in REQUIREMENTS.md "Out of Scope".

---

## Architecture Patterns

### Recommended file structure for this phase

```
ketu/
└── ephemeris/
    └── orbital.py                    # MODIFY (only if error > 0.01°)

tests/
├── test_planets_coverage.py          # existing — leave alone
└── test_lilith_cross_check.py        # NEW — the harness (LIL-02, LIL-03)

docs/
└── LILITH_DEFINITION.md              # NEW — written FIRST (LIL-01)

pyproject.toml                        # MODIFY — add [project.optional-dependencies].test (LIL-04)
CHANGELOG.md                          # MODIFY — add 1.1.0 section entry (LIL-05)
UPGRADING.md                          # MODIFY — Lilith section (LIL-05)
```

**Note on `LILITH_DEFINITION.md` location:** `docs/` is the right home given existing peers (`docs/aspect_timelines.md`, `docs/complex.md`). NOT in repo root. NOT in `.planning/`. The doc is user-facing reference material.

### Pattern 1: Investigation-first task ordering

**What:** A phase that answers "is there a bug?" before "fix the bug." Documentation is the first deliverable, not the last.
**When:** Whenever a change to numerical output of a published library is proposed. v1.0 already ships these Lilith values to PyPI users; changing them is a behavioural break.
**Plan-level structure:**

1. Plan A — write `LILITH_DEFINITION.md` from scratch (no code touched). State the formula Ketu currently uses, cite Chapront-Touzé / Chapront / Francou, define "Mean Apogee" precisely, state the convention (tropical ecliptic of date, geocentric, projected to ecliptic plane). Commit. (LIL-01)
2. Plan B — add `[project.optional-dependencies].test = ["pysweph>=2.10.3.6"]` to `pyproject.toml`. Verify clean venv `pip install ketu[test]` resolves and `pip show pysweph` succeeds. Verify `pip install ketu` (no extras) does NOT pull in `pysweph`. (LIL-04)
3. Plan C — write `tests/test_lilith_cross_check.py` parametrized over 5 dates. Compute `expected = swe.calc_ut(jd, swe.MEAN_APOG)[0][0]`, `actual = get_lilith_position(jd)`, assert `signed_circular_diff(actual, expected) < TOLERANCE_DEG = 0.01`. Run it. (LIL-02)
4. Plan D (conditional, only if Plan C fails) — investigate the discrepancy: is it the epoch constant (`83.3532`)? the rate (`0.1114040803`)? a frame mismatch? Correct in `orbital.py:591`, pin `pysweph` values as regression baselines, update `LILITH_DEFINITION.md` with the new formula and a "history" section explaining the v1.0 → v1.1 numerical change. (LIL-03)
5. Plan E — write CHANGELOG.md and UPGRADING.md entries. Magnitude statement is **always written**, even if the magnitude is zero ("Lilith verified to within 0.01° vs Swiss Ephemeris on dates X, Y, Z"). (LIL-05)

**Anti-pattern:** combining Plans A and C into a single plan. The whole point of LIL-01 is that the document precedes the test, and the test precedes any formula change. Each is its own commit.

### Pattern 2: Test-only optional dependency in `pyproject.toml`

**What:** `[project.optional-dependencies]` extras keep deps out of the runtime wheel while letting `pip install ketu[test]` install them.
**When:** Always for testing-only deps in PEP 621 projects.
**Example (verified against current `pyproject.toml` structure):**

```toml
# Source: https://packaging.python.org/en/latest/specifications/dependency-specifiers/
# Add to pyproject.toml AFTER the existing [project] section's `dependencies = [...]`

[project.optional-dependencies]
test = [
    "pysweph>=2.10.3.6",
]
```

**Verification commands** (must appear in plan as test-step actions):

```bash
# In a fresh venv:
python -m venv /tmp/ketu-runtime-check && source /tmp/ketu-runtime-check/bin/activate
pip install -e .
python -c "import swisseph"            # MUST FAIL with ModuleNotFoundError
deactivate && rm -rf /tmp/ketu-runtime-check

# In another fresh venv:
python -m venv /tmp/ketu-test-check && source /tmp/ketu-test-check/bin/activate
pip install -e .[test]
python -c "import swisseph; print(swisseph.MEAN_APOG)"   # MUST print 12
deactivate && rm -rf /tmp/ketu-test-check
```

If the first venv succeeds in importing `swisseph`, the dependency leaked into runtime — fail the plan.

### Pattern 3: `pytest.importorskip` for optional-dep tests

**What:** Standard pytest idiom for skipping a whole test module when an optional library is unavailable.
**When:** Any test that depends on `[project.optional-dependencies]` packages — CI must still pass when running `pip install -e .` (no extras).
**Example:**

```python
# tests/test_lilith_cross_check.py
"""Cross-check Ketu's mean lunar apogee (Lilith) against Swiss Ephemeris.

Skipped automatically when pysweph is not installed (i.e. user ran
`pip install -e .` without the [test] extra).
"""
import pytest
swe = pytest.importorskip("swisseph", minversion="2.10.3.6")

import numpy as np
from datetime import datetime, timezone

from ketu.ephemeris.orbital import get_lilith_position
from ketu.ephemeris.time import utc_to_julian

# Tolerance: 0.01° = 36 arcseconds.
# Justification (see docs/LILITH_DEFINITION.md §"Tolerance"):
# Mean Apogee moves at 0.111404°/day = 0.00464°/hour. A 0.01° tolerance
# corresponds to ~129 minutes of "drift" — well below human-perceptible
# astrological precision (sign boundaries are 30° wide; cusp accuracy
# in published ephemerides is ~0.1°).
TOLERANCE_DEG = 0.01

# 5 dates spanning the requirement range. Mid-month, mid-day to avoid
# integer-JD coincidences.
CROSS_CHECK_DATES = [
    datetime(1900, 6, 15, 12, 0, tzinfo=timezone.utc),
    datetime(1950, 3, 21, 18, 30, tzinfo=timezone.utc),
    datetime(2000, 1,  1, 12, 0, tzinfo=timezone.utc),  # J2000.0 epoch
    datetime(2025, 9, 23,  6, 0, tzinfo=timezone.utc),
    datetime(2050, 12, 21, 0, 0, tzinfo=timezone.utc),
]


def _signed_circular_diff(a: float, b: float) -> float:
    """Smallest signed angular difference a - b in (-180, 180]."""
    d = (a - b + 180.0) % 360.0 - 180.0
    return d


@pytest.mark.parametrize("dt", CROSS_CHECK_DATES, ids=lambda d: d.isoformat())
def test_lilith_matches_swiss_ephemeris(dt):
    """Ketu's get_lilith_position must agree with swe.MEAN_APOG within TOLERANCE_DEG."""
    jd = utc_to_julian(dt)

    # Swiss Ephemeris reference (analytical Moshier reduction; no .se1 files needed)
    xx, _retflag = swe.calc_ut(jd, swe.MEAN_APOG)
    expected_lon = xx[0]

    actual_lon = get_lilith_position(jd)

    delta = _signed_circular_diff(actual_lon, expected_lon)
    assert abs(delta) < TOLERANCE_DEG, (
        f"Lilith mismatch on {dt.isoformat()}: "
        f"Ketu={actual_lon:.6f}°, swe={expected_lon:.6f}°, "
        f"Δ={delta:+.6f}° (tolerance {TOLERANCE_DEG}°)"
    )
```

**Source:** `pytest.importorskip` docs — https://docs.pytest.org/en/stable/reference/reference.html#pytest.importorskip
**Source:** PEP 621 optional-dependencies — https://packaging.python.org/en/latest/specifications/pyproject-toml/#dependencies-optional-dependencies

### Pattern 4: Signed circular angular difference

**What:** Computing `a - b` for angles must wrap to (−180°, 180°], or you get false 359° diffs around 0°/360°.
**Why:** Lilith on 2050-12-21 might be at 359.99° (Ketu) and 0.005° (swe). Naive `a - b` = 359.985°. Correct signed diff = −0.015°.
**Example:** see `_signed_circular_diff` above.
**Don't:** rely on `normalize_angle(a - b)` — that gives unsigned 0–360.

### Anti-patterns to avoid

- **Pinning expected values from current Ketu output.** That tests "does Ketu equal Ketu" — circular. Pin from `swe.calc_ut` only, OR (acceptable alternative) pin nothing and assert tolerance against `swe.calc_ut` at runtime as in Pattern 3.
- **Hand-rolling a JD calculator just for the harness.** Ketu has `utc_to_julian` already; use it. (This is also what the formula under test consumes — apples to apples.)
- **Skipping LIL-04 because pysweph "is available on most dev machines anyway."** The whole reliability of the harness is that it's reproducible from a clean checkout via `pip install -e .[test]`.
- **Writing `LILITH_DEFINITION.md` as boilerplate.** It's the load-bearing document of this phase. It must explicitly state which formula Ketu uses, why, and what the canonical reference is. If a discrepancy is found later, the document is updated alongside the formula.
- **Using `swe.calc()` instead of `swe.calc_ut()`.** `calc()` expects JD-TT, Ketu uses JD-UT. Mixing them introduces a Δ-T error (~70 s in 2026). Use `calc_ut` exclusively.
- **Forgetting `swe.close()` / process leaks.** For `SE_MEAN_APOG` no ephemeris files are loaded so no cleanup is strictly required — but pytest may run the suite multiple times in one process (`pytest --count`). Defensive: wrap in a session-scoped fixture if it ever causes problems. Not required initially.
- **Asserting equality (`==`) on floats.** Use `abs(delta) < TOLERANCE_DEG`. Already covered above.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Reference mean apogee | Re-derive ELP-2000 truncation | `swe.calc_ut(jd, swe.MEAN_APOG)` | Astrodienst's reduction is the de-facto astrological reference; rebuilding it is the bug we're trying to detect |
| Test-only dep mechanics | Custom `try: import` skip + monkeypatch | `pytest.importorskip("swisseph", minversion="2.10.3.6")` | Idiomatic, self-documenting, integrates with pytest collection |
| Optional dep packaging | Conditional `requirements.txt`, makefile target | `[project.optional-dependencies]` in `pyproject.toml` | PEP 621 standard; pip understands it; no custom tooling |
| JD computation in tests | Compute JD from year/month/day inline | Reuse `_make_jd(...)` pattern from `tests/test_planets_coverage.py:36-39` (calls `utc_to_julian`) | Same path that the production code consumes — eliminates a class of "your JD differs from mine" bugs |
| Circular angular diff | `(a - b) % 360` | `(a - b + 180) % 360 - 180` | Wraps to signed (−180, 180]; required for tolerance assertions across 0°/360° |
| Δ-T correction | Compute UT→TT yourself with `swe.deltat()` | Use `swe.calc_ut` (handles internally) | `calc_ut` is exactly the contract Ketu provides — both consume JD-UT; no Δ-T should ever appear in either side |

**Key insight:** *Every line of code in this phase is a liability if the conclusion is "no formula change needed."* Lean ruthlessly on `pysweph` for reference values and on stdlib/pytest for plumbing.

---

## Common Pitfalls

### Pitfall 1: Frame-of-reference mismatch (the most likely source of a >0.01° discrepancy)

**What goes wrong:** Ketu's formula `83.3532 + 0.1114040803 * d` produces a longitude that is mean-of-date OR mean-of-J2000 — and `swe.calc_ut(jd, swe.MEAN_APOG)` produces tropical-of-date by default. If the two frames don't match, expect a slowly varying offset (precession ≈ 50.3″/year ≈ 0.014°/year ≈ a fraction of a degree across the 1900–2050 sample window).
**Why it happens:** Ketu's formula source isn't cited in the docstring. The constants `83.3532` and `0.1114040803` are consistent with several published mean-element approximations that differ in subtle ways (mean-of-date vs J2000; whether nutation is folded in).
**How to avoid:** This is **exactly what `LILITH_DEFINITION.md` exists to nail down**. Step 1 of the phase is documenting which frame Ketu's formula targets. Until that's stated, you can't even define what "correct" means. If the harness shows a slow drift across the 5 dates (e.g. 0.005° in 1900, 0.020° in 2050), precession misalignment is your prime suspect.
**Warning sign:** Error monotonic in time across the 5 dates → frame mismatch. Error roughly constant → epoch constant `83.3532` is off. Error roughly proportional to `d` → rate constant `0.1114040803` is off.

### Pitfall 2: Δ-T injection (false positive)

**What goes wrong:** Calling `swe.calc(jd, swe.MEAN_APOG)` (no `_ut` suffix) treats `jd` as JD-TT, while Ketu treats it as JD-UT. Around 2026, Δ-T ≈ 70 s, which at Lilith's rate of 0.111404°/day is ≈ 9 × 10⁻⁵° — small but the wrong direction of "small."
**Why it happens:** Easy slip in the harness; both functions are exported.
**How to avoid:** ONLY use `swe.calc_ut`. Add a comment in the test pinning the choice. Forbid `swe.calc(` in the file via a `grep -q "swe.calc(" tests/test_lilith_cross_check.py && exit 1` step in the verify phase if paranoid.
**Warning sign:** If the harness passes with `swe.calc` and fails with `swe.calc_ut` (or vice versa) by ~10⁻⁴°, you've found the bug.

### Pitfall 3: AGPL contamination of runtime wheel

**What goes wrong:** Adding `pysweph` to `dependencies` (instead of `[project.optional-dependencies]`) drags an AGPL-licensed library into Ketu's runtime, contaminating the MIT-licensed wheel and forcing all users into AGPL terms.
**Why it happens:** Copy-paste mistake; not noticing PEP 621 has two distinct keys (`dependencies` and `optional-dependencies`).
**How to avoid:** The two-venv test in Pattern 2 above. The first venv (`pip install -e .`) MUST fail to import `swisseph`. The second venv (`pip install -e .[test]`) MUST succeed. Both checks belong in the plan as explicit verify steps.
**Warning sign:** `pip install ketu==1.1.0rc1` in a fresh venv pulls down 30+ MB of native compiled code. That's `pysweph`. Stop the release.

### Pitfall 4: pysweph install failure on minority platforms

**What goes wrong:** `pysweph` ships wheels for cpython 3.8–3.13 on Linux (manylinux), macOS (arm64 + x86_64), Windows (amd64). Niche platforms (e.g. PyPy, Linux musl, BSD) may need to compile from source — which requires a C toolchain.
**Why it happens:** Swiss Ephemeris's underlying C library has to be compiled.
**How to avoid:** CI matrix sticks to mainstream platforms (Ubuntu / macOS / Windows × Python 3.10–3.13 — already what Ketu uses per CHANGELOG.md "Python 3.10-3.13 in CI"). Document `pysweph` install requirement explicitly in `LILITH_DEFINITION.md` ("To run the cross-check, install Ketu with `pip install ketu[test]`. On non-mainstream platforms a C compiler may be required.").
**Warning sign:** Contributor reports "tests skipping locally" — the most common cause is missed `[test]` extra. Surface this in CONTRIBUTING.md or a single sentence in the harness module docstring.

### Pitfall 5: "Tolerance theatre" — choosing 0.01° for round-number reasons

**What goes wrong:** 0.01° is a defensible tolerance, but only if explicitly justified. A reviewer asks "why 0.01°?" and the only answer is "the requirements said so."
**Why it happens:** Numerology over rigor.
**How to avoid:** `LILITH_DEFINITION.md` includes a §"Tolerance" subsection that derives the figure: 0.01° = 36″, equivalent to ~129 min of mean-apogee motion (`0.01° / (0.111404°/day) × 24 hours/day × 60 min/hour ≈ 129.27 min`). Most published printed ephemerides are good to 0.1° on Lilith; 0.01° is a *tighter* bound than the user-facing precision contract. Quote that ratio.
**Warning sign:** Reviewer pushes back. Document the math in the test docstring AND the definition file.

### Pitfall 6: Missing `xx, retflag` unpacking → `xx[0]` is `tuple[float, ...]` confusion

**What goes wrong:** `swe.calc_ut(jd, swe.MEAN_APOG)` returns a 2-tuple `(xx, retflag)` where `xx` is itself a 6-tuple `(lon, lat, dist, lon_speed, lat_speed, dist_speed)`. A common typo is `lon = swe.calc_ut(jd, swe.MEAN_APOG)[0]` which gives you the 6-tuple, not the longitude.
**Why it happens:** The pyswisseph signature isn't deeply documented; many examples online use `swe.calc_ut(jd, body)[0]` and rely on indexing into the 6-tuple subsequently.
**How to avoid:** Always unpack explicitly: `xx, _retflag = swe.calc_ut(jd, swe.MEAN_APOG)` then `lon = xx[0]`.
**Warning sign:** Type errors at assertion time, or values like `(123.4, -1.2, 0.0, 0.111, 0.0, 0.0)` appearing in failure messages.

### Pitfall 7: J2000 fixture (2000-01-01 12:00 UT) being too clean

**What goes wrong:** At `jd = 2451545.0`, `d = 0` exactly, so Ketu's formula returns `83.3532°` *by definition*. If `swe.MEAN_APOG` happens to also use that as its reference epoch, both will agree to machine precision on this single date — a false-positive "perfect agreement" hiding a rate drift that only appears far from epoch.
**Why it happens:** J2000 is the "obvious" date but it's also the formula's own anchor.
**How to avoid:** Include J2000 in the fixture (it's a reasonable midpoint), but make sure 1900 and 2050 are also there to expose any rate drift. Don't rely on J2000 alone.
**Warning sign:** All tests pass with errors clustered near the J2000 sample; spread reveals real divergence.

### Pitfall 8: Sidereal vs tropical confusion

**What goes wrong:** `swe.calc_ut` defaults to tropical (mean equinox of date). If a previous call somewhere in the test process invoked `swe.set_sid_mode(...)` and `iflag |= swe.FLG_SIDEREAL`, results would shift by the ayanamsa (~24°). Process state leaks across tests.
**Why it happens:** Swiss Ephemeris uses C-style global state.
**How to avoid:** This phase only ever calls `swe.calc_ut(jd, swe.MEAN_APOG)` with no flags. Don't call `swe.set_sid_mode`. The test module is the only consumer of `swisseph`. State leaks are essentially impossible. Document this in the test docstring.
**Warning sign:** Differences clustered around 24° — that's the Lahiri ayanamsa. Or any constant offset that doesn't grow with time.

---

## Code Examples

### `LILITH_DEFINITION.md` skeleton (for Plan A)

```markdown
# Lilith (Mean Black Moon Lilith) — Definition

> Reference document for `ketu.ephemeris.orbital.get_lilith_position`.

## What Ketu Computes

Ketu's "Lilith" (body index 12, label `"Lilith"`) is the **Mean Apogee
of the Moon's orbit** — the point on the Moon's mean orbital ellipse
furthest from Earth's centre — projected onto the ecliptic.

This corresponds to Swiss Ephemeris's `SE_MEAN_APOG` (constant value `12`).

## Formula

[State the current formula explicitly:]

    lilith_lon = (83.3532 + 0.1114040803 × d) mod 360°
    where d = JD_UT − 2451545.0  (days since J2000.0)

- `83.3532°`: mean longitude at J2000.0 (1 January 2000 12:00 UT).
- `0.1114040803°/day`: mean prograde rate ≈ 40.69°/year.
- Full revolution: ≈ 8.85 years (3232.6 days).

## Reference Frame

- **Tropical**, ecliptic of date (mean equinox of date).
- **Geocentric**, mean orbit, projected onto the ecliptic.
- **Mean** (smoothed) — does not include short-period oscillations from
  perturbations. The "True / Osculating Apogee" is a separate quantity
  (Swiss Ephemeris `SE_OSCU_APOG`); not implemented in v1.1.

## Source

Chapront-Touzé, M.; Chapront, J.; Francou, G. — ELP-2000 lunar theory,
Bureau des Longitudes (Paris). The Mean Apogee elements are derived
from this theory; Swiss Ephemeris uses Moshier's reduction of ELP-2000
to a polynomial form covering 3000 BCE – 3000 CE.

## Cross-Check

A pytest harness (`tests/test_lilith_cross_check.py`) compares Ketu's
formula against `pysweph`'s `swe.calc_ut(jd, swe.MEAN_APOG)` on five
dates spanning 1900–2050. Tolerance: 0.01° (36 arcseconds, equivalent
to ~129 minutes of mean-apogee drift). Run with:

    pip install ketu[test]
    pytest tests/test_lilith_cross_check.py -v

## Tolerance Justification

[Mean Apogee rate × tolerance arithmetic from Pitfall 5 above.]

## History

- v0.x – v1.0: formula `83.3532 + 0.1114040803*d` shipped; never
  externally verified.
- v1.1 (this phase): formula verified against Swiss Ephemeris.
  [Result: agreement within X.XXXX° on all sampled dates / formula
  corrected to A + B*d, max error reduced from M to N degrees.]
```

### `pyproject.toml` diff (Plan B)

```toml
# Source: PEP 621 — https://peps.python.org/pep-0621/
# Add AFTER existing [project] section's `dependencies`:

[project.optional-dependencies]
test = [
    "pysweph>=2.10.3.6",
]
```

### Cross-check harness (Plan C) — full file

See "Pattern 3" above. That code block is the full file content for `tests/test_lilith_cross_check.py`. Copy verbatim into the plan; it's already linted in my head against the Ketu codebase conventions.

### CHANGELOG.md entry skeleton (Plan E)

If error ≤ 0.01° (no formula change):

```markdown
## [1.1.0] — UNRELEASED

### Verified

- **Lilith (Mean Apogee) longitude**: cross-checked against Swiss
  Ephemeris `SE_MEAN_APOG` on five dates (1900-06-15, 1950-03-21,
  2000-01-01, 2025-09-23, 2050-12-21). Maximum deviation:
  X.XXXX° (well below 0.01° tolerance). No formula change. See
  `docs/LILITH_DEFINITION.md`.
```

If error > 0.01° (formula corrected):

```markdown
## [1.1.0] — UNRELEASED

### Fixed (BREAKING — Numerical Behavior Change)

- **Lilith (Mean Apogee) longitude formula corrected** to match Swiss
  Ephemeris `SE_MEAN_APOG`. Old formula in v1.0 deviated by up to
  X.XXXX° on dates within 1900–2050. Concrete example:
  on 2025-01-01 12:00 UT, Ketu v1.0 returned A.AAAA°, Ketu v1.1
  returns B.BBBB° (Δ = C.CCCC°). Recompute any cached Lilith values
  from v1.0. See `docs/LILITH_DEFINITION.md` and `UPGRADING.md`.
```

### UPGRADING.md entry skeleton (Plan E)

```markdown
## Lilith (Black Moon) Calculation

### From v1.0.0 to v1.1.0

[If unchanged:]
The Mean Apogee Lilith formula is unchanged in v1.1. v1.0 values were
verified against Swiss Ephemeris and found to agree within 0.01°.
No action required.

[If changed:]
The Mean Apogee Lilith formula has been corrected. Values returned by
`get_lilith_position(jd)` and `calc_planet_position(jd, 12)` differ
from v1.0 by up to X.XXXX° within the 1900–2050 range.

**Concrete examples:**

| Date              | v1.0 Lilith | v1.1 Lilith | Δ        |
|-------------------|-------------|-------------|----------|
| 2025-01-01 12 UT  | A.AAAA°     | B.BBBB°     | C.CCCC°  |
| ...               |             |             |          |

**Action required:** Recompute any cached Lilith values produced by
v1.0. If you stored Ketu output (e.g. lunation timing, ML feature
arrays) for ML training, regenerate these arrays.
```

---

## State of the Art

| Old approach | Current approach | When changed | Impact |
|--------------|------------------|--------------|--------|
| Hardcoded constants citing no source | Source-cited formula in `LILITH_DEFINITION.md` | This phase (v1.1) | Future audits trivially possible; downstream consumers (Kala) know what they're getting |
| `pyswisseph` (astrorigin, last release 2023-06) | `pysweph` (community fork, 2.10.3.6, 2026-02) | This phase | Active maintenance; same import name; same wheel coverage |
| `pyswisseph` as runtime dep (Ketu 0.1, removed in v1.0) | `pysweph` as test-only `[project.optional-dependencies]` | This phase | Pure-NumPy runtime contract maintained; AGPL never enters the wheel |
| No external verification of Lilith | 5-date `pytest` harness against Swiss Ephemeris | This phase | Numerical correctness is now a CI-enforced property |

**Deprecated / outdated for this phase:**
- `pyswisseph==2.10.3.2` — superseded by `pysweph==2.10.3.6`. Don't pin to it. Don't co-install both (same import name → wheel collision).
- Custom JD calculators for tests — use `ketu.ephemeris.time.utc_to_julian`.
- Any formula source citation that says only "ELP-2000" without the Chapront names — inadequate; `LILITH_DEFINITION.md` must name authors.

---

## Open Questions

1. **What does Ketu's current formula actually agree with?**
   - What we know: `83.3532 + 0.1114040803*d` is consistent with widely circulated astrology-software approximations. The rate `0.1114040803°/day` matches `360°/3232.61 days ≈ 8.85 years` — the canonical anomalistic period.
   - What's unclear: Whether the epoch constant `83.3532` and the precise rate match what `pysweph SE_MEAN_APOG` returns to within 0.01° on all 5 dates.
   - **Recommendation:** This is a **measurement question, not a research question** — running the harness IS the answer. Plan C produces it.

2. **Does Swiss Ephemeris's `SE_MEAN_APOG` always return tropical-of-date, even on dates far from J2000?**
   - What we know: Default `swe.calc_ut(jd, body)` returns ecliptic of date (tropical). Confirmed via Astrodienst documentation.
   - What's unclear: Whether any subtle frame definition (e.g. mean-equinox-of-date vs true-equinox-of-date) introduces nutation contributions Ketu's formula doesn't model.
   - **Recommendation:** If the harness reveals a residual ~10″ wobble correlated with the 18.6-year nutation period, document as a known limitation. Almost certainly below tolerance — not blocking.

3. **Is `pysweph` AGPL transmissive into Ketu's MIT wheel if it's only `[test]`-installed?**
   - What we know: AGPL applies to "the work" — i.e. the AGPL-licensed code. A test-only dep does not appear in the published wheel; it doesn't link statically; it's a *runtime tool* that contributors and CI use.
   - What's unclear: Whether overcautious legal review might still flag it. Standard practice in OSS (cf. NumPy itself testing against AGPL libs in dev-only) is that this is fine.
   - **Recommendation:** State in `LILITH_DEFINITION.md` that `pysweph` is test-only and never in the wheel. Verify via the two-venv test in Pattern 2. Stop there.

4. **Should the harness also verify Mean Node (Rahu) and True Node opportunistically?**
   - What we know: Same `swe.calc_ut(jd, swe.MEAN_NODE)` API works, same pure-Python coverage. Marginal cost is ~10 lines of test code.
   - What's unclear: Whether expanding scope is welcome at this phase or scope-creep.
   - **Recommendation: NO.** Stay scoped. Note in the test module docstring that the same pattern can verify `MEAN_NODE` and `TRUE_NODE` in a future phase. v1.1 ships only Lilith verification.

5. **What if `pysweph` PyPI publication is delayed / yanked between research date and plan execution?**
   - What we know: Currently published 2026-02-19, ≈3 months stable.
   - What's unclear: Future availability.
   - **Recommendation:** Pin `>=2.10.3.6` (already specified). If unavailable, fallback to `pyswisseph>=2.10.3.0` (same `import swisseph as swe` interface, same `SE_MEAN_APOG` constant). Document the fallback in CONTRIBUTING.md if it ever becomes necessary. Do NOT bake the fallback into the plan now — over-engineering.

---

## Sources

### Primary (HIGH confidence)

- **Existing Ketu codebase** — read directly:
  - `/home/loc/workspace/ketu/ketu/ephemeris/orbital.py` (line 591: current Lilith formula; lines 145–146: ORBITAL_ELEMENTS row for Lilith).
  - `/home/loc/workspace/ketu/ketu/ephemeris/planets.py` (lines 147–155: how Lilith is plumbed into `calc_planet_position`; line 458: `0.111404` repeated as speed for body 12).
  - `/home/loc/workspace/ketu/ketu/ephemeris/time.py` (lines 1–60: `utc_to_julian` produces JD-UT; matches `swe.calc_ut` input contract).
  - `/home/loc/workspace/ketu/tests/test_planets_coverage.py` (lines 1–45: existing `_make_jd` fixture pattern to copy; lines 477–482: existing speed-ratio Lilith test, narrow scope, no longitude check).
  - `/home/loc/workspace/ketu/pyproject.toml` (no `[project.optional-dependencies]` section yet; mypy override for `swisseph.*` already in place).
- **Astrodienst Swiss Ephemeris programmer's guide** — https://www.astro.com/swisseph/swephprg.htm
  - Confirmed: `SE_MEAN_APOG = 12`; mean apogee is mathematical/analytic (no `.se1` files needed); `swe_calc_ut` returns tropical ecliptic-of-date by default; Python binding signature is `xx, retflag = swe.calc_ut(jd, ipl, [iflag])`.
- **Astrodienst Swiss Ephemeris general doc** — https://www.astro.com/swisseph/swisseph.htm
  - Confirmed: "mean apogee is computed from Moshier's lunar routine, which is an adjustment of the ELP2000-85 lunar theory to the JPL ephemeris on the interval from 3000 BCE to 3000 CE"; "mean lunar orbit using the formula derived by Chapront, Chapront-Touzé and Francou of the Observatoire de Paris."
- **`pysweph` PyPI page** — https://pypi.org/project/pysweph/
  - Confirmed: version 2.10.3.6 released 2026-02-19; community fork of pyswisseph; same import name (`swisseph`); pre-built wheels for Linux/macOS/Windows × Python 3.8–3.13; Astrodienst Swiss Ephemeris license (AGPL or commercial).
- **`pyswisseph` PyPI page** — https://pypi.org/project/pyswisseph/
  - Confirmed: version 2.10.3.2 released 2023-06-04 (stale); AGPL v3; ephemeris files NOT bundled (separate download required for non-analytic bodies); same `import swisseph as swe`. Used here to confirm fallback path exists.
- **PEP 621 (project metadata in pyproject.toml)** — https://peps.python.org/pep-0621/ — definitive spec for `[project.optional-dependencies]`.
- **`pytest.importorskip` reference** — https://docs.pytest.org/en/stable/reference/reference.html#pytest.importorskip — official idiom for optional-dep tests.

### Secondary (MEDIUM confidence)

- WebSearch for ELP-2000 / Chapront-Touzé / Francou citation — https://www.aanda.org/articles/aa/pdf/2003/23/aa3101.pdf and ADS https://ui.adsabs.harvard.edu/abs/1983A&A...124...50C — these confirm the historical citation structure that should appear in `LILITH_DEFINITION.md` but are deeper than needed for the test harness itself.
- WebSearch describing "true vs mean Lilith" differences — https://serennu.com/astrology/mean-true-black-moon.php and https://kerykeion.net/content/learn-astrology/foundation-lilith-variants — useful for the §"What Ketu Computes" section of `LILITH_DEFINITION.md` (clarifying that True / Osculating Apogee is *not* what Ketu returns).

### Tertiary (LOW confidence — flagged)

- WebSearch claim: "swe_calc_ut and swe_calc work exactly the same way except [time scale]" — this is a paraphrase, but consistent across multiple sources (R-binding `swephR` docs, mivion's Node binding README, scribd PDFs). HIGH likely correct, retained at MEDIUM only because the literal sentence wasn't in the primary Astrodienst HTML output of WebFetch.
- Coefficient "83.3532" as a published constant — could not find an external citation reproducing this exact form. May be a Ketu-specific approximation. **This is a key reason the harness is necessary.** Not a blocker — the harness will tell us.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|------|-------|--------|
| Standard stack (`pysweph` 2.10.3.6, test-only via PEP 621) | HIGH | PyPI verified; PEP 621 is canonical; matches existing project conventions and locked decisions |
| Architecture patterns (investigation-first ordering, importorskip, `_make_jd` reuse) | HIGH | All grounded in REQUIREMENTS.md, existing test files, and pytest official docs |
| `swe.calc_ut(jd, swe.MEAN_APOG)` API contract (returns tropical ecliptic-of-date longitude in degrees, no ephemeris files needed, signature `xx, ret = swe.calc_ut(...)`) | HIGH | Astrodienst official + multiple cross-referenced bindings |
| Tolerance justification (0.01° = 129 min of motion) | HIGH | Pure arithmetic from established rate constant |
| Frame mismatch as primary failure mode | MEDIUM | Reasoned from physics; will be confirmed/refuted by harness output |
| Magnitude of any future correction | LOW | **Cannot be predicted** — requires running the harness; that's the whole point of the phase |
| AGPL non-contamination via `[test]` extra | HIGH | Standard OSS practice; `pip install ketu` (no extras) is empirically demonstrable in the two-venv test |
| `pysweph` install reliability across platforms | MEDIUM | Wheels published, but minority platforms may need C compiler |

**Research date:** 2026-05-06
**Valid until:** ~2026-08-06 (3 months for stable Python packaging + pysweph PyPI lifecycle). Re-verify if `pysweph` releases a new minor version or if AGPL Astrodienst licensing terms shift.

---

## Plan-Level TL;DR (for the planner)

Five plans, in this order, each its own commit:

1. **Plan A — Definition (LIL-01).** Write `docs/LILITH_DEFINITION.md` from the skeleton above. NO code touched. Commit `docs(lilith): document Mean Apogee definition and Chapront citation`.
2. **Plan B — Test-only dep (LIL-04).** Add `[project.optional-dependencies] test = ["pysweph>=2.10.3.6"]` to `pyproject.toml`. Verify two-venv runtime/test isolation. Commit `build(lilith): add pysweph as test-only dependency`.
3. **Plan C — Cross-check harness (LIL-02).** Write `tests/test_lilith_cross_check.py` from the Pattern 3 template. Run it. Record result. Commit `test(lilith): cross-check mean apogee against Swiss Ephemeris on 5 dates`.
4. **Plan D — Conditional fix (LIL-03), only if Plan C fails.** Update `ketu/ephemeris/orbital.py:591` (and possibly the `0.1114040803` rate in `orbital.py:146` and `planets.py:153,458` for consistency). Update `LILITH_DEFINITION.md` §"History" with the magnitude. Commit `fix(lilith): correct Mean Apogee formula to match Swiss Ephemeris`.
5. **Plan E — Release notes (LIL-05).** Update `CHANGELOG.md` and `UPGRADING.md` with explicit magnitude statements (zero-magnitude allowed). Commit `docs(lilith): document v1.0→v1.1 Lilith verification result`.

If Plan C passes (error ≤ 0.01°), Plan D is **deleted from the plan**, not deferred. The phase ships with 4 commits, and the success criterion #3 is satisfied by the "≤ 0.01°" branch ("definition document closes the loop without code change").

End of research.
