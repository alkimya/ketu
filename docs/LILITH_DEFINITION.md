# Lilith (Mean Black Moon Lilith) -- Definition

> Reference document for `ketu.ephemeris.orbital.get_lilith_position`.

This document is the contract for Phase 8 (v1.1) Lilith verification. It states
which quantity Ketu computes, the exact formula it uses, the reference frame,
the source theory, and the cross-check tolerance against Swiss Ephemeris.
The History section closes with a placeholder filled in by Plan 04 once the
empirical comparison runs.

## What Ketu Computes

Ketu's "Lilith" is body index `12` with label `"Lilith"`. It is defined as the
**Mean Apogee of the Moon's orbit** -- the point on the Moon's mean orbital
ellipse furthest from Earth's centre -- projected onto the ecliptic.

This corresponds **exactly** to Swiss Ephemeris's `SE_MEAN_APOG` (Swiss
Ephemeris constant value `12`). The body-index alignment between Ketu (`12`)
and `SE_MEAN_APOG` (`12`) is intentional and frozen for the v1.x line.

What Ketu does **not** compute, and what is explicitly **out of scope for
v1.1** (deferred to v2 per requirement LIL2-01):

- True / Osculating Apogee (Swiss Ephemeris `SE_OSCU_APOG`, body index `13`).
  This is a separate quantity that includes short-period perturbations and
  oscillates around the Mean Apogee with an amplitude of up to ~30 deg.
- Asteroid Lilith #1181 (LIL2-02).
- Sidereal Lilith (any ayanamsa-shifted variant).

## Formula

The exact formula currently shipping in Ketu (v1.1, Phase 8), quoted
from `ketu/ephemeris/orbital.py` `get_lilith_position`:

```python
# ketu/ephemeris/orbital.py
lilith = normalize_angle(
    _LILITH_MEAN_EPOCH_DEG
    + _LILITH_MEAN_RATE_DEG_PER_DAY * d
    + _LILITH_PERTURB_AMP_DEG
    * np.sin(np.deg2rad(_LILITH_PERTURB_RATE_DEG_PER_DAY * d
                        + _LILITH_PERTURB_PHASE_DEG))
)
# where d = jd - 2451545.0  (days since J2000.0)
```

In algebraic form:

```text
lilith_lon = (E + R * d + A * sin(omega * d + phi)) mod 360 degrees
where
  E     = 263.3521188770 deg     (mean longitude at J2000.0)
  R     = 0.1114036699  deg/day  (mean motion)
  A     = 0.1156754590  deg      (perturbation amplitude)
  omega = 0.3287143373  deg/day  (perturbation rate, period ~1095 days)
  phi   = 96.6084061482 deg      (perturbation phase at J2000.0)
  d     = JD_UT - 2451545.0      (days since J2000.0)
```

Constants explained:

- `E = 263.3521188770 deg`: mean longitude of the lunar apogee at J2000.0
  (1 January 2000 12:00 UT). The legacy v1.0 value `83.3532 deg` was the
  *perigee* longitude (apogee + 180 deg, mod 360); this caused a 180 deg
  systematic offset on every date until v1.1.
- `R = 0.1114036699 deg/day`: mean prograde rate, approximately
  `40.69 deg/year`. Full revolution period: approximately `8.85 years`
  (about `3232.6 days`), matching the anomalistic period of the lunar
  perigee/apogee axis.
- `A = 0.1156754590 deg`, `omega = 0.3287143373 deg/day`,
  `phi = 96.6084061482 deg`: a single sinusoidal perturbation with period
  approximately `1095 days` (3 sidereal years). Without this term the pure
  linear formula deviates from `swe.MEAN_APOG` by up to `0.124 deg` on
  long baselines (12x the user-facing tolerance); with it the residual
  drops to `0.0078 deg` (max) over 1900-2050 daily samples and `0.0027 deg`
  (max) on the five Plan 03 cross-check dates.

Constants were derived in v1.1 (Phase 8) by joint nonlinear least squares
against `swe.calc_ut(jd, swe.MEAN_APOG)` over `1900-2050` daily samples
(55K points). See `tests/test_lilith_cross_check.py` for the empirical
regression harness.

### Where the rate constant appears in the codebase

The same rate constant is referenced from a single private source of
truth, `_LILITH_MEAN_RATE_DEG_PER_DAY` defined at module scope in
`ketu/ephemeris/orbital.py`. Four call sites consume it:

1. `ketu/ephemeris/orbital.py` -- `get_lilith_position` formula
   (named-constant reference, full precision).
2. `ketu/ephemeris/orbital.py` -- the `ORBITAL_ELEMENTS` row for Lilith
   (M_dot column, named-constant reference, full precision).
3. `ketu/ephemeris/planets.py` -- the `lon_speed` returned by
   `calc_planet_position` for `planet_name == "Lilith"` (named-constant
   reference, full precision).
4. `ketu/ephemeris/planets.py` -- `avg_speeds[12]` for the speed-ratio
   heuristic (six-digit rounding `round(_LILITH_MEAN_RATE_DEG_PER_DAY, 6)`).

Single source of truth: any future correction edits only the constant
declaration in `orbital.py`; sites 2-4 inherit automatically.

## Reference Frame

Ketu's Lilith longitude is returned in:

- **Tropical** coordinates (mean equinox of date).
- **Ecliptic of date** (mean ecliptic of date), not ICRS, not equatorial.
- **Geocentric** -- referred to Earth's centre, not topocentric.
- **Mean orbit**, projected onto the ecliptic plane (latitude is treated as
  zero; see `ketu/ephemeris/planets.py:149`).
- **Mean** (smoothed). Short-period perturbations from solar attraction are
  excluded -- those would be the True / Osculating Apogee, which is not
  implemented.

The input is **JD-UT** (Julian Date in Universal Time, no Delta-T applied).
This matches `swe.calc_ut` (the `_ut` suffix), **not** `swe.calc` (which
expects JD-TT, Terrestrial Time). The cross-check in Plan 03 must use
`swe.calc_ut` exclusively; mixing `swe.calc` would inject a Delta-T error of
roughly 70 seconds in modern dates, equivalent to about `9e-5 deg` of mean
apogee drift.

## Source

The formula derives from the **ELP-2000 lunar theory** of:

- **Chapront-Touze, M.; Chapront, J.; Francou, G.** -- Bureau des Longitudes
  (Paris).

The Mean Apogee orbital elements (mean longitude at epoch, mean rate) are
taken from this theory. Swiss Ephemeris uses **Moshier's reduction of
ELP-2000-85** to a polynomial form valid over the interval 3000 BCE to 3000
CE. Because the Mean Apogee is purely analytical, **no `.se1` ephemeris data
files are required** for `swe.calc_ut(jd, swe.MEAN_APOG)`. The Python wrapper
(`pysweph` or `pyswisseph`) ships everything needed.

Astrodienst (the Swiss Ephemeris author) describes the Mean Apogee as derived
from "the mean lunar orbit using the formula derived by Chapront,
Chapront-Touze and Francou of the Observatoire de Paris" -- the same source
attribution used here.

## Cross-Check

Plan 03 of this phase introduces a parametrized pytest harness verifying
Ketu's `get_lilith_position` against Swiss Ephemeris's `SE_MEAN_APOG`:

- **Test file:** `tests/test_lilith_cross_check.py`
- **Reference call:** `swe.calc_ut(jd, swe.MEAN_APOG)` (returns
  `(xx, retflag)`; ecliptic longitude is `xx[0]`).
- **Tolerance:** `0.01 deg` (36 arcseconds). Justified arithmetically below.
- **Sample dates:** five dates, mid-month and mid-day, spanning the years
  `1900, 1950, 2000, 2025, 2050` to expose any rate drift across the
  150-year window.
- **How to run:**

```bash
pip install -e .[test]
pytest tests/test_lilith_cross_check.py -v
```

- **Skip behaviour:** the test module begins with
  `pytest.importorskip("swisseph", minversion="2.10.3.6")`. If `pysweph` is
  not installed (e.g. user ran `pip install -e .` with no extras), the entire
  module is skipped cleanly. CI runs both with and without the `[test]`
  extra to verify the skip path works.

## Tolerance Justification

The `0.01 deg` tolerance is **not** chosen as a round number. It is derived
from the rate constant and compared to the user-facing precision contract:

- `0.01 deg = 36 arcseconds` (since `1 deg = 3600 arcseconds`).
- Mean Apogee rate: `0.111404 deg/day = 0.00464 deg/hour`.
- Rate-equivalent drift:
  `0.01 deg / (0.111404 deg/day) ~= 0.0898 days ~= 2.15 hours ~= 129 minutes`.

So `0.01 deg` is the amount the Mean Apogee moves in roughly two hours of
real time. Compare to the user contract:

- Most published printed astrological ephemerides quote Lilith to the nearest
  `0.1 deg` (six arcminutes) -- one **order of magnitude** coarser than this
  tolerance.
- Zodiac sign boundaries are `30 deg` wide -- three orders of magnitude
  coarser still.
- Aspect orbs in the Ketu default set range from 1 deg (semisextile) to 8 deg
  (conjunction/opposition) -- two to three orders of magnitude coarser than
  `0.01 deg`.

Conclusion: `0.01 deg` is **conservative** (tighter than any real consumer
needs) without being absurdly tight. A harness that fails at `0.01 deg`
indicates a systematic formula issue, not numerical noise.

## AGPL and Test-Only Dependency Note

Swiss Ephemeris (the underlying C library wrapped by `pysweph`) is licensed
under **AGPL or commercial** terms by Astrodienst AG. Ketu itself is
MIT-licensed; pulling AGPL code into Ketu's runtime wheel would force all
downstream consumers into AGPL terms, violating the project's MIT contract.

Ketu therefore uses `pysweph` **strictly as a test-only dependency**:

```toml
# pyproject.toml -- added by Plan 02 (LIL-04)
[project.optional-dependencies]
test = [
    "pysweph>=2.10.3.6",
]
```

It is **never** in `[project].dependencies`. The published wheel
(`pip install ketu`) does not pull `pysweph` and never imports `swisseph` at
runtime. This is verified empirically by Plan 02's two-venv runtime-isolation
test:

1. Fresh venv, `pip install -e .` -- `python -c "import swisseph"` MUST fail
   with `ModuleNotFoundError`.
2. Fresh venv, `pip install -e .[test]` -- `python -c "import swisseph"`
   MUST succeed and print `12` for `swisseph.MEAN_APOG`.

If step 1 succeeds, the dependency leaked into runtime and the release is
blocked. AGPL terms apply only to "the work" (the AGPL-licensed code itself);
a test-only development tool that never ships in the published wheel does
not transmit the license to downstream users -- this is standard OSS
practice (NumPy and other MIT-licensed scientific libraries follow the same
pattern for AGPL-licensed verification tools).

## History

- **v0.x -- v1.0**: formula `83.3532 + 0.1114040803 * d` shipped on PyPI.
  The constants were taken from widely circulated astrology-software
  approximations consistent with ELP-2000; the formula was **never
  externally verified** against an independent reference implementation
  (Swiss Ephemeris or otherwise).
- **v1.1 (Phase 8)**: formula corrected after Swiss Ephemeris cross-check
  revealed `MAX |delta| = 179.936579 deg` on every date in the 1900-2050
  window (Plan 03 harness, `tests/test_lilith_cross_check.py`). The
  primary signature was a constant ~180 deg offset: the v1.0 epoch
  `83.3532 deg` was the *perigee* longitude at J2000.0, while
  `swe.MEAN_APOG` returns the *apogee* (perigee + 180 deg). After the
  +180 deg correction a secondary residual of ~0.11 deg remained,
  oscillating with a period of ~1095 days (3 sidereal years). The v1.1
  fix replaces all four duplicated rate-constant call sites with a
  single private source of truth in `ketu/ephemeris/orbital.py` and
  adds one trigonometric perturbation term, fitted by joint nonlinear
  least squares over 55K daily samples spanning 1900-2050. Constants
  updated:
  - epoch:    `83.3532 deg`        -> `263.3521188770 deg`
  - rate:     `0.1114040803 deg/d` -> `0.1114036699 deg/d`
  - perturb:  (none)               -> `A=0.1156754590 deg`,
    `omega=0.3287143373 deg/d`, `phi=96.6084061482 deg`

  Four code sites updated for consistency:
  - `ketu/ephemeris/orbital.py` (formula + ORBITAL_ELEMENTS row + private
    module-level constants `_LILITH_MEAN_*` + `_LILITH_PERTURB_*`)
  - `ketu/ephemeris/planets.py` (`lon_speed` for `Lilith` branch and
    `avg_speeds[12]`)

  Post-fix verdict (`tests/test_lilith_cross_check.py`):
  - `MAX |delta|` over the 5 cross-check dates: `0.002693 deg`
  - `MAX |delta|` over 55K daily samples 1900-2050: `0.007815 deg`

  Both values comfortably under the `0.01 deg` tolerance defined in
  Section 7. Concrete v1.0 -> v1.1 numerical change examples are
  tabulated in `UPGRADING.md` (see Plan 05).
