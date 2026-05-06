# Stack Research — Ketu v1.1

**Domain:** Astronomical-astrological Python library (extension of validated v1.0)
**Researched:** 2026-05-06
**Confidence:** HIGH for runtime stack decisions, HIGH for test-only validation strategy, MEDIUM on Lilith formula choice (multiple competing conventions)

## TL;DR

**No new runtime dependencies.** v1.1 stays pure-NumPy.
**One new test/dev dependency:** `pysweph>=2.10.3.6` (community fork of pyswisseph, supports Python 3.10–3.13). Used as ground-truth oracle for validating houses + Lilith.
**No new modules, just extend existing ones:**
- `ketu/houses/` (new sub-package, NumPy-only) — Placidus + Koch + Whole Sign + Equal
- `ketu/aspects/config.py` (new) — `AspectSet`/`HarmonicSet` dataclasses for runtime aspect configuration
- `ketu/ephemeris/orbital.py` (existing) — fix Lilith epoch constant + add osculating apogee variant
- `ketu/display.py` (existing) — replace `input()` CLI with `argparse` (subcommand pattern)
**Algorithms:** documented in plain spherical trig + a small `numpy`-vectorized fixed-point loop (no `scipy`).

---

## Recommended Stack

### Runtime Dependencies (UNCHANGED)

| Technology         | Version    | Purpose                              | Why Recommended                                                                                           |
|--------------------|------------|--------------------------------------|-----------------------------------------------------------------------------------------------------------|
| `numpy`            | `>=1.20.0` | Vectorized math, structured arrays   | Already the entire runtime contract for Ketu 1.0. Houses/aspects are vectorizable in pure NumPy.          |
| Python stdlib only | 3.10–3.13  | `argparse`, `dataclasses`, `zoneinfo`| `argparse` covers the CLI flag-parsing needs (no `click`/`typer` needed). `dataclasses` for `AspectSet`. |

**Hard rule preserved:** `pyproject.toml` `[project] dependencies` stays at `["numpy>=1.20.0"]`. v1.1 must not regress this.

### Test / Dev Dependencies (NEW)

| Library     | Version       | Purpose                                                       | When Used                                                                                                                                                                                       |
|-------------|---------------|---------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `pysweph`   | `>=2.10.3.6`  | Ground-truth oracle for houses + Lilith                       | Test-only. Compare Ketu's pure-NumPy houses against `swe.houses(...)` and Ketu's Lilith against `swe.calc_ut(jd, swe.MEAN_APOG)`. Tests skip gracefully if not installed (`pytest.importorskip`). |
| `pytest`    | already used  | Test runner                                                   | Ongoing                                                                                                                                                                                          |
| `mypy`      | already used  | Strict type checking                                          | Ongoing — already has `[[tool.mypy.overrides]] module = ["swisseph.*"]` (compatible with `pysweph` since it imports as `swisseph`)                                                                |

**Why `pysweph`, not `pyswisseph`?** The original `pyswisseph` last released v2.10.3.2 in June 2023, has no wheels for Python 3.12 or 3.13, and its maintainer became unresponsive in 2025. The `pysweph` fork by sailorfe released v2.10.3.6 on **2026-02-19**, ships wheels for cp38–cp313 (manylinux + macOS), and tracks the same Swiss Ephemeris C library version 2.10.03. It imports as `import swisseph` so existing mypy override and any test code is identical.

**License safety for a test-only dep:** Swiss Ephemeris is dual-licensed AGPL-3.0-or-later / commercial. Using it as a *test-only* validation oracle does **not** infect Ketu's MIT runtime: AGPL obligations attach to *distribution* of derivative works. Test code is not distributed in the wheel (`tests/` is excluded from `[tool.setuptools] packages`), and CI installation of an AGPL package to run tests is the standard pattern (analogous to using GPL `gdb` to debug an MIT project). Document this clearly in `CONTRIBUTING.md` and put it in `[project.optional-dependencies] test`, not `dependencies`.

### Algorithmic Building Blocks (NumPy-only, in-house)

| Component                        | Technique                                                              | Where it lives                              |
|----------------------------------|------------------------------------------------------------------------|---------------------------------------------|
| Placidus cusps                   | Fixed-point iteration on `RA = target + arcsin(tan(φ)·tan(δ))`         | `ketu/houses/placidus.py`                   |
| Koch cusps                       | Fixed-point iteration on Oblique Ascension trisection                  | `ketu/houses/koch.py`                       |
| Whole Sign / Equal               | Pure trig, no iteration                                                | `ketu/houses/simple.py`                     |
| Polar fallback                   | Detect `\|φ\| + ε > 90°`, raise `PolarLatitudeError` or fall back to Porphyry | `ketu/houses/__init__.py`                   |
| Vectorized convergence           | `np.where`-masked fixed-point loop, max ~20 iters, tol `1e-9 rad`      | `ketu/houses/_solve.py`                     |
| Aspect set / harmonic config     | `@dataclass(frozen=True)` + factory functions                          | `ketu/aspects/config.py`                    |
| Lilith fix                       | Recompute epoch constant against Meeus eq. 45.7 + add `LilithTrue` body| `ketu/ephemeris/orbital.py` (existing file) |

### Development Tools (UNCHANGED)

| Tool        | Purpose                                  | Notes                                                                                              |
|-------------|------------------------------------------|----------------------------------------------------------------------------------------------------|
| `pytest`    | Test runner                              | Already at 250 tests / 91% cov. Add `tests/test_houses.py`, `tests/test_lilith_validation.py`.     |
| `pytest-cov`| Coverage                                 | Already configured (`fail_under = 70`).                                                            |
| `mypy`      | Strict typing                            | Add `ketu.houses.*` to per-module overrides if needed (prefer keeping it strict-clean from day 1).|
| `numpydoc`  | Docstring style                          | Already the convention. Apply to all new public functions.                                         |

---

## Algorithm Details

### Placidus (house system code `'P'`)

**Concept:** Trisect the semi-diurnal arc (SA) and semi-nocturnal arc (SN) in time.

**Inputs:** Julian Date (UT), geographic latitude φ, geographic longitude λ, obliquity ε(jd).

**Step 1 — Angles:**
```
ARMC = local sidereal time in degrees   (already in ketu.ephemeris.time.sidereal_time)
MC   : tan(λ_MC) = tan(ARMC) / cos(ε)
ASC  : standard ASC formula from ARMC, ε, φ
```

**Step 2 — Intermediate cusps (11, 12, 2, 3) — fixed-point iteration:**

For house `H` (with fraction `F = 1/3` for cusps 11 & 3, `F = 2/3` for cusps 12 & 2):

```
target_RA = ARMC + F·90°       (or with appropriate sign per cusp)
RA ← target_RA                  # initial guess
repeat:
    δ  = arcsin(sin(RA) · sin(ε))
    AD = arcsin(tan(φ) · tan(δ))
    RA_new = target_RA + F · AD       # for upper cusps; sign flips for lower
    if |RA_new - RA| < tol: break
    RA = RA_new
λ = atan2(sin(RA)·cos(ε) + tan(δ)·sin(ε), cos(RA))
```

**Vectorization:** when given an array of `(jd, lat)` pairs, broadcast δ, AD, RA across the array and use `np.where` to mask elements that have already converged. Typical convergence: 5–8 iterations to `1e-9` rad.

**Failure mode:** When `|tan(φ)·tan(δ)| > 1` the formula is undefined. This happens whenever `|φ| + ε > 90°` (polar regions). v1.1 should:
1. Pre-check `|lat| > 66.5°` and emit a warning,
2. Detect non-convergence/NaN inside the iteration,
3. Either raise `PolarLatitudeError` or fall back to Porphyry (configurable via parameter).

### Koch (house system code `'K'`)

**Concept:** Trisect the Oblique Ascension (OA) interval between MC and ASC.

```
OA(λ) = RA(λ) - AD(λ)
target_OA_11 = OA_MC + (OA_Asc - OA_MC) / 3
target_OA_12 = OA_MC + 2·(OA_Asc - OA_MC) / 3
```

Then the same fixed-point loop as Placidus, with `target = target_OA` and `RA_new = target + AD`.

**Same polar failure mode as Placidus.**

### Whole Sign (`'W'`) and Equal (`'E'`)

Trivial; no iteration.
- **Whole Sign:** cusp[i] = floor(ASC / 30) · 30 + i · 30
- **Equal:** cusp[i] = ASC + i · 30

These should ship in v1.1 alongside Placidus/Koch — they're essentially free and answer the "which house system?" debate by giving the user three good options.

### Lilith Fix

Current code (`ketu/ephemeris/orbital.py:591`):
```python
lilith = normalize_angle(83.3532 + 0.1114040803 * d)
```

Issues to investigate (handed to roadmapper as test items, not solutions):
1. **Epoch constant 83.3532°.** Meeus AA eq. 45.7 gives the lunar perigee polynomial; mean apogee is perigee + 180°. The constant should be derived from Meeus's `M' = 134.9633964 + ...` (perigee) → apogee `= 314.9633964°` mod 360, **not** 83.3532. The 83.3532 figure looks like a different convention — needs cross-check against `swe.calc_ut(jd, swe.MEAN_APOG)` at multiple JDs to determine actual offset and direction.
2. **Linear-only model.** Meeus uses `M' = M'_0 + n·T + a·T² + b·T³ + ...` (T in Julian centuries). Ketu uses linear (`d` in days). Linear is fine for ~±1 century from J2000 with arc-minute accuracy, but for ML/trading 100-year backtests the higher-order terms become relevant. Decision should be made empirically: compare against pysweph oracle over 1900–2100 and accept linear if max error < 0.5° (else add T² term).
3. **Missing osculating apogee (True Lilith / SE_OSCU_APOG = 13).** Many users expect both. Add as separate body code 13 with its own calculation (numerical solution of two-body apogee from Moon's ECI position — non-trivial; defer to v1.2 if scope-pressed).

**Validation harness recipe:**
```python
# tests/test_lilith_validation.py
import pytest
swe = pytest.importorskip("swisseph")  # works for both pyswisseph and pysweph

@pytest.mark.parametrize("jd", [2451545.0, 2415020.0, 2488069.0, ...])
def test_lilith_matches_swe_mean_apog(jd):
    ketu_lon = ketu.ephemeris.get_lilith_position(jd)
    swe_lon, _ = swe.calc_ut(jd, swe.MEAN_APOG)
    assert abs(((ketu_lon - swe_lon[0]) + 180) % 360 - 180) < 0.5  # within 0.5°
```

### CLI Flag Parsing — Recommended Pattern

Current state: `ketu/display.py:main()` uses `input()` prompts. v1.1 should switch to `argparse` (stdlib, zero new deps).

**Recommended structure — subcommand dispatch:**
```python
def main() -> None:
    parser = argparse.ArgumentParser(prog="ketu", description="...")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # ketu chart 2024-11-05T18:00 --lat 41.9 --lon 12.5 --houses placidus
    p_chart = sub.add_parser("chart", help="Compute a natal/transit chart")
    p_chart.add_argument("datetime", type=parse_iso)
    p_chart.add_argument("--lat", type=float, required=True)
    p_chart.add_argument("--lon", type=float, required=True)
    p_chart.add_argument("--houses", choices=["placidus", "koch", "whole", "equal"],
                         default="placidus")
    p_chart.add_argument("--harmonics", type=parse_harmonics,
                         default=[1, 2, 3, 4, 6, 8, 12],
                         help="Comma-separated harmonics, e.g. --harmonics 1,2,3,5,7")
    p_chart.add_argument("--orb", type=float, default=8.0)
    p_chart.set_defaults(func=cmd_chart)

    # ketu cycles ...
    p_cyc = sub.add_parser("cycles", help="Generate cycle time series")
    ...
    p_cyc.set_defaults(func=cmd_cycles)

    args = parser.parse_args()
    args.func(args)


def parse_harmonics(s: str) -> list[int]:
    """argparse type: '1,2,3,5' -> [1,2,3,5]. Validates each is positive int."""
    try:
        vals = [int(x.strip()) for x in s.split(",") if x.strip()]
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid harmonics: {s!r}")
    if not vals or any(v < 1 for v in vals):
        raise argparse.ArgumentTypeError("Harmonics must be positive integers")
    return vals
```

**Why this pattern:**
- **`type=` callable, not custom `Action` class** — simpler, integrates cleanly with argparse's error reporting (`ArgumentTypeError`), and enables `default=[1,2,3,4,6,8,12]` as a real list (custom Actions break defaults).
- **`choices=`** for the closed set of house systems — argparse generates the help text and "invalid choice" error automatically.
- **Subparsers + `set_defaults(func=...)`** — the canonical 2025-best-practice argparse layout. Keeps each subcommand's logic in its own function, and `main()` is just dispatch.
- **`parse_iso`** uses `datetime.fromisoformat` (Py3.11+ accepts `Z`; for 3.10 wrap with `replace("Z", "+00:00")`).

**Don't add `click` or `typer`.** Both are excellent but are runtime deps (`click` pulls in nothing else, but it's still a new line in `dependencies`). Ketu's selling point is "NumPy only"; that brand promise is worth preserving for a CLI that just needs ~8 flags.

---

## Installation

No changes to user-facing install:
```bash
pip install ketu              # unchanged for end users
```

For contributors running validation tests:
```bash
pip install -e ".[test]"      # NEW optional extra: pulls in pysweph
# Or directly:
pip install pysweph>=2.10.3.6
```

`pyproject.toml` addition:
```toml
[project.optional-dependencies]
test = [
    "pytest>=7",
    "pytest-cov",
    "pysweph>=2.10.3.6 ; python_version >= '3.10'",
]
```

---

## Alternatives Considered

| Recommended                      | Alternative                          | When Alternative Would Win                                                                                  |
|----------------------------------|--------------------------------------|-------------------------------------------------------------------------------------------------------------|
| `pysweph` (test-only oracle)     | `pyswisseph` (original)              | If we needed to support only Python 3.10–3.11 *and* wanted upstream-blessed source. Not our case.            |
| `pysweph` (test-only oracle)     | `skyfield`                           | If we wanted a pure-Python oracle (no C ext). But Skyfield doesn't compute astrological houses or Lilith natively — wrong tool. |
| `pysweph` (test-only oracle)     | `kerykeion` / `immanuel`             | If we wanted a high-level chart API for tests. But both depend on `pyswisseph` themselves and add ~3 layers of indirection. Just call the oracle directly. |
| `argparse` (stdlib)              | `click`                              | Decorator-based API, nicer for very large CLIs (>20 commands). Ketu has ~3 subcommands; not worth a runtime dep. |
| `argparse` (stdlib)              | `typer`                              | Type-hint-driven CLI, beautiful. But pulls in `click` + `rich`, breaks NumPy-only contract.                  |
| In-house NumPy fixed-point       | `scipy.optimize.fixed_point` / `newton` | If we already had SciPy as a dep. We don't, and adding SciPy (~30 MB) for one 8-line iteration is absurd.    |
| In-house NumPy fixed-point       | `scipy.optimize.brentq`              | Brentq is more robust, but is not natively vectorized over arrays of problems and would force a Python loop. |
| Trisection-based Placidus        | Otto Ludwig's pole rotation method   | Mathematically equivalent for Placidus; trisection is more widely documented and easier to verify against `swe.houses`. |

## What NOT to Use

| Avoid                                     | Why                                                                                                                                                                                  | Use Instead                                                                                                          |
|-------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| `pyswisseph` 2.10.3.2 (original)          | No Python 3.13 wheel; maintainer unresponsive since mid-2025; would force CI to build from C source                                                                                  | `pysweph>=2.10.3.6` (drop-in API-compatible fork)                                                                   |
| `pyswisseph` or `pysweph` as **runtime** dep | (a) Breaks NumPy-only brand, (b) AGPL-or-commercial license would force Ketu's MIT users to choose AGPL or buy commercial license, (c) C extension complicates wheels                | Pure-NumPy in-house implementations of Placidus/Koch; `pysweph` only in `[test]` extra                              |
| `flatlib`                                 | Built on the `pyswisseph` C lib (same license issue as a runtime dep), last meaningful release 2018, abandoned                                                                       | In-house NumPy implementation                                                                                        |
| `kerykeion` / `immanuel`                  | High-level chart libraries, depend on `pyswisseph`; not validation oracles, they ARE the thing we're competing with on the "houses" feature                                          | `pysweph` directly for ground truth; build our own high-level API                                                   |
| `scipy` as runtime dep                    | 30+ MB for a single fixed-point loop we can write in 10 lines of NumPy                                                                                                              | Hand-coded vectorized fixed-point in `ketu/houses/_solve.py`                                                        |
| `click` / `typer` for the CLI             | New runtime deps, breaks NumPy-only contract                                                                                                                                         | `argparse` (stdlib)                                                                                                  |
| Storing aspect/harmonic config as a dict  | Type-unsafe, no IDE completion, hard to diff in tests                                                                                                                                | `@dataclass(frozen=True)` `AspectSet` and `HarmonicSet` with validation in `__post_init__`                            |
| Recomputing the existing aspects array    | The 14-aspect harmonic table in `ketu.core.aspects` is validated and cycled in 250 tests. Don't touch it.                                                                            | New `AspectSet` is a *configuration* layer that *selects* from the existing table; legacy callers see no change.    |
| Eager imports of `swisseph` in test files | Hard fails CI on systems where pysweph isn't installed; breaks the optional-extra story                                                                                             | `swe = pytest.importorskip("swisseph")` at the top of validation test files                                          |

---

## Stack Patterns by Variant

**If user installs `ketu` (default, end user):**
- Pure NumPy. No C extension. Houses, aspects, Lilith all computed in-process.
- ~5 MB install, works on every platform NumPy works on.

**If contributor installs `ketu[test]`:**
- Adds `pysweph` (~3 MB compiled C ext + ~10 MB Swiss Ephemeris data files if user downloads them).
- Validation tests run; without `[test]` extra, those test files are skipped via `importorskip`.
- CI installs the `[test]` extra. Production wheel builds do not.

**If user is in polar latitudes (|lat| > 66.5°):**
- Placidus/Koch raise `PolarLatitudeError` by default.
- User passes `polar_fallback="porphyry"` (or `"whole_sign"`) to silently fall back.
- Whole Sign and Equal always work everywhere — recommend these in the docs for circumpolar use cases.

---

## Version Compatibility

| Package A                  | Compatible With           | Notes                                                                                                              |
|----------------------------|---------------------------|--------------------------------------------------------------------------------------------------------------------|
| `numpy>=1.20.0`            | Python 3.10–3.13          | Already validated in v1.0; structured-array dtype API stable for >5 years                                          |
| `pysweph==2.10.3.6`        | Python 3.8–3.13           | Wheels for cp310, cp311, cp312, cp313 (manylinux2014, macOS universal2). Imports as `import swisseph`.            |
| `pysweph` ↔ `pyswisseph`   | Drop-in API compatible    | Same C library version (2.10.03), same Python module name `swisseph`. Existing mypy override works for both.      |
| `argparse`                 | All Python versions       | Stdlib. `BooleanOptionalAction` requires 3.9+; Ketu requires 3.10+, so safe.                                       |
| `datetime.fromisoformat`   | Python 3.10 (limited), 3.11+ (full ISO 8601) | For Python 3.10 compat with `Z` suffix, manually replace `"Z"` → `"+00:00"` before parsing.                          |
| `dataclasses`              | Python 3.7+               | Stdlib; `frozen=True` and `slots=True` (3.10+) both safe                                                            |

---

## Integration Points with Existing Ketu Architecture

| New piece                       | Touches                                       | Risk                                                                                                                 |
|---------------------------------|-----------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| `ketu/houses/`                  | New top-level sub-package; imported by `ketu/__init__.py` and `display.py` | LOW. Self-contained; uses `ketu.ephemeris.time.sidereal_time` (existing) and `ketu.ephemeris.coordinates` (existing). |
| Replaces `calculate_house_cusps` stub in `ketu/ephemeris/planets.py:270` | The current stub returns equal-house with a placeholder MC. Replace its body with a delegation to `ketu.houses.calculate(...)`. Keep signature for back-compat. | LOW. Stub is a placeholder; no caller depends on its current incorrect output (verified: only docstring references). |
| `ketu/aspects/config.py`        | New module; imported by `calculate_aspects` for optional `aspect_set` kwarg | MEDIUM. Existing 14-aspect default must remain the default when no `aspect_set` is passed (back-compat).             |
| Lilith fix in `orbital.py:591`  | Changes returned values for Lilith            | HIGH. Any downstream test asserting specific Lilith longitudes will break. Audit `tests/` for Lilith assertions before merging; bump to v1.1.0 (minor) since output values change for an existing body. Strictly speaking this is a breaking semantic change masked by a "fix" framing — document loudly in CHANGELOG. |
| `argparse` CLI in `display.py`  | Replaces `main()` body                        | MEDIUM. The `ketu` console-script entry point currently triggers interactive prompts. v1.1 changes that to flag-driven. Keep `ketu interactive` (or running with no args) as a fallback that calls the old `input()` flow, OR document the breaking change. |
| `pyproject.toml` `[project.optional-dependencies]` | New `test` extra | LOW. Additive only.                                                                                                  |

---

## Sources

- [pysweph on PyPI](https://pypi.org/project/pysweph/) — verified v2.10.3.6 (2026-02-19), Python 3.8–3.13 wheels, fork status — **HIGH confidence**
- [pyswisseph on PyPI](https://pypi.org/project/pyswisseph/) — verified v2.10.3.2 (2023-06-04), no 3.12/3.13 wheels — **HIGH confidence**
- [pyswisseph 2.10.3.2 file list](https://pypi.org/project/pyswisseph/2.10.3.2/) — confirmed wheel matrix cp36–cp311 — **HIGH confidence**
- [pyswisseph license dual AGPL/commercial issue #92](https://github.com/astrorigin/pyswisseph/issues/92) — verified dual licensing concerns — **HIGH confidence**
- [Swiss Ephemeris programmer's manual](https://www.astro.com/swisseph/swephprg.htm) — verified `SE_MEAN_APOG = 12`, `SE_OSCU_APOG = 13`, distinction from asteroid 1181 Lilith — **HIGH confidence**
- [libephemeris house-systems algorithm reference](https://github.com/g-battaglia/libephemeris/blob/main/docs/reference/house-systems.md) — verified Placidus and Koch formulas, polar failure condition `|φ| + ε > 90°`, fixed-point convergence pattern — **HIGH confidence**
- [Meeus Astronomical Algorithms eq. 45.7 reference (multiple secondary sources)](https://serennu.com/astrology/mean-true-black-moon.php) — confirmed Mean Lilith = lunar perigee polynomial + 180°. Primary source (Meeus 2nd ed., p. 308) not directly fetched — **MEDIUM confidence**, validation against pysweph oracle will resolve definitively
- [Python argparse docs (3.14)](https://docs.python.org/3/library/argparse.html) — verified `type=` callable + `set_defaults(func=...)` subparser pattern — **HIGH confidence**
- [SciPy `fixed_point` docs](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.fixed_point.html) — confirmed Steffensen/Aitken acceleration availability (we don't use it, but verified plain iteration is sufficient at typical convergence rates) — **HIGH confidence**
- Ketu codebase audit — `ketu/ephemeris/planets.py:270` (stub `calculate_house_cusps`), `ketu/ephemeris/orbital.py:574` (`get_lilith_position` linear formula, epoch 83.3532°), `ketu/display.py:60` (`input()` CLI), `pyproject.toml:92` (existing `swisseph.*` mypy override) — **HIGH confidence** (direct file reads)

---
*Stack research for: Ketu v1.1 (configurable aspects + Placidus/Koch houses + Lilith fix)*
*Researched: 2026-05-06*
