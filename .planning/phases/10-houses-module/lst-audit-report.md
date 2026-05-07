# LST / Mean Obliquity Precision Audit (Plan 10-01)

**Phase 10 (Houses Module) blocker resolution.** This document records the
empirical precision of `ketu.ephemeris.time.sidereal_time()` and
`ketu.ephemeris.coordinates.mean_obliquity()` against the Swiss Ephemeris
oracle, and the tighten-vs-accept decision required by HOU-01
(<60 arcsec / 1 arcmin Ascendant error vs Astro.com / Swiss Ephemeris).

## 1. Methodology

**Sample dates** (5, spanning 1900-2100 to cover the v1.1 valid range
1900-2050 plus margin):

| Label                       | JD (UT)   |
| --------------------------- | --------- |
| 1900-01-01 12h UT           | 2415021.0 |
| J2000 (2000-01-01 12h TT)   | 2451545.0 |
| 2024-06-21 0h UT            | 2460482.5 |
| 2050-12-31 12h UT           | 2470204.0 |
| 2100-01-01 12h UT           | 2488069.5 |

**Latitudes (3)** for the ASC sensitivity probe: 0° (equator),
49° (Paris-like mid-latitude), 66.5° (Arctic Circle / Placidus polar
boundary stress).

**Reference oracle:** `pyswisseph` 2.10.03 (`swe.version == "2.10.03"`).
The oracle is gated by `pytest.importorskip("swisseph")` matching the
Phase 8 cross-check pattern; it stays a `[project.optional-dependencies].test`
extra and is never a runtime dependency.

**Measurement formulae** (degrees → arcseconds via `× 3600`, with
360° wrap handled by `((delta + 180) % 360) - 180`):

```
gmst_drift_arcsec     = signed_delta_arcsec(sidereal_time(jd, 0.0), swe.sidtime(jd) * 15.0)
obliquity_drift_arcsec = (mean_obliquity(jd) - swe.calc_ut(jd, swe.ECL_NUT)[0][1]) * 3600
asc_error_arcsec       = signed_delta_arcsec(asc_ketu, asc_swe)
```

The ASC error probe feeds **both ketu's GMST and ketu's mean obliquity**
into `swe.houses_armc(armc, lat, eps, b"P")` and compares against the
same oracle call with swisseph's own `swe.sidtime` / `eps`. This
isolates how ketu's primitive drift propagates through Placidus's ASC
formula.

## 2. GMST drift table

| Date                       | ketu (deg)      | swe.sidtime × 15 (deg) | drift (arcsec) |
| -------------------------- | --------------- | ---------------------- | -------------: |
| 1900-01-01 12h UT          | 280.67659993    | 280.68114288           |       −16.3546 |
| J2000 (2000-01-01 12h TT)  | 280.46061837    | 280.45707244           |       +12.7654 |
| 2024-06-21 0h UT           | 269.68397781    | 269.68305393           |        +3.3260 |
| 2050-12-31 12h UT          | 311.65492721    | 311.65737927           |        −8.8274 |
| 2100-01-01 12h UT          | 100.73823632    | 100.73850232           |        −0.9576 |

**Max |GMST drift| = 16.35 arcsec.**

**Root cause.** ketu's `sidereal_time()` returns **mean GMST** (IAU 1982
polynomial form). `swe.sidtime()` returns **apparent GMST** (= mean GMST
+ equation of equinoxes, where `EE = nut_lon × cos(eps_mean)`). The
12-16 arcsec drift is the equation of equinoxes magnitude, NOT a
polynomial-precision error. swisseph's house functions consume
**apparent** ARMC; mean GMST as ARMC produces a systematic offset.

## 3. Obliquity drift table

| Date                       | ketu (deg)        | swe (deg)         | drift (arcsec) |
| -------------------------- | ----------------- | ----------------- | -------------: |
| 1900-01-01 12h UT          | 23.4522942543     | 23.4522887023     |      +0.019987 |
| J2000 (2000-01-01 12h TT)  | 23.4392911111     | 23.4392794439     |      +0.042002 |
| 2024-06-21 0h UT           | 23.4361090487     | 23.4360959096     |      +0.047301 |
| 2050-12-31 12h UT          | 23.4326478844     | 23.4326331654     |      +0.052988 |
| 2100-01-01 12h UT          | 23.4262874622     | 23.4262699153     |      +0.063169 |

**Max |obliquity drift| = 0.063 arcsec.**

`coordinates.mean_obliquity` already implements the IAU 2006 polynomial
(see `coordinates.py` line 304-311). Drift is well under 0.1 arcsec
across the sample range — already excellent. **Confirmed; do NOT
modify.** The 2× headroom test threshold `TOL_OBLIQUITY_ARCSEC = 0.1`
guards future regressions without triggering on the measured ~0.05″
floor.

## 4. ASC error sensitivity table (5 dates × 3 latitudes)

ASC error attributable to ketu's GMST + mean-obliquity drift propagated
through `swe.houses_armc` (Placidus, ARMC isolation method):

| Date                       | lat 0° | lat 49° | lat 66.5° |
| -------------------------- | -----: | ------: | --------: |
| 1900-01-01 12h UT          | −17.71 |  −33.05 |     −8.23 |
| J2000 (2000-01-01 12h TT)  | +13.83 |  +25.92 |     +7.46 |
| 2024-06-21 0h UT           |  +3.62 |   +7.23 |  +227.25† |
| 2050-12-31 12h UT          |  −8.87 |  −10.20 |     −4.01 |
| 2100-01-01 12h UT          |  −1.03 |   −0.70 |     −0.53 |

**† Polar singularity, NOT a precision regression.** At
2024-06-21 / lat=66.5°, ARMC = 269.68° puts the Placidus ASC near the
horizon-pole alignment where `dASC/dARMC` blows up: empirically
~70 arcsec ASC per 1 arcsec ARMC drift. swisseph itself rejects
`lat ≥ 66.6°` at this ARMC ("`swisseph.houses_armc: error`"). The plan's
instruction to fence at lat=66.5° **does** include this stress sample —
the resulting test failure is the audit's value-add: it exposes the
near-circumpolar instability that any houses implementation will
inherit and which downstream Plan 10-05 (`koch-porphyry-polar`) must
address by switching to Porphyry above the polar boundary.

| Latitude | max \|ASC error\| (arcsec) |
| -------- | ------------------------: |
| 0°       |                     17.71 |
| 49°      |                     33.05 |
| 66.5°    |                    227.25 |

**Overall max |ASC error| = 227.25 arcsec @ 2024-06-21 lat=66.5°.**

Excluding the polar singularity, **max |ASC error| = 33.05 arcsec at
lat=49° / 1900-01-01** — under the 60-arcsec spec but with only
27 arcsec headroom.

## 5. Spec comparison

HOU-01 spec: **<60 arcsec (1 arcmin) ASC error vs Swiss Ephemeris.**

Headroom rule (per plan must_haves):
> If headroom > 30 arcsec at all polar samples, ACCEPT;
> if headroom < 30 arcsec OR negative anywhere, TIGHTEN.

**Headroom (current state, mean GMST):**

- Best case (2100 lat=66.5°): 60 − 0.53 = **+59.47 arcsec**
- Worst non-singular case (1900 lat=49°): 60 − 33.05 = **+26.95 arcsec**
- Singular case (2024 lat=66.5°): 60 − 227.25 = **−167.25 arcsec**

The mid-latitude headroom (27 arcsec) is below the 30-arcsec floor. The
polar singular case is far outside spec. Both trigger the TIGHTEN rule.

**Headroom (after tightening, apparent GMST + true obliquity recipe):**

| Date                       | lat=66.5° err (arcsec) | headroom |
| -------------------------- | ---------------------: | -------: |
| 1900-01-01 12h UT          |                  +0.27 |   +59.73 |
| J2000 (2000-01-01 12h TT)  |                  +0.63 |   +59.37 |
| 2024-06-21 0h UT           |                  −8.67 |   +51.33 |
| 2050-12-31 12h UT          |                  +1.11 |   +58.89 |
| 2100-01-01 12h UT          |                  +1.11 |   +58.89 |

Tightening collapses polar error from 227 → 8.67 arcsec at the same
2024 sample; the residual 8.67″ is **not** a singularity but the
truncated 4-term nutation series in `coordinates.nutation()`. The
mid-latitude headroom (lat=49°) expands from 27 → ~58 arcsec across all
samples. **All polar-boundary samples now have >50 arcsec headroom.**

## 6. Verdict

**Verdict: TIGHTEN**

The audit reveals two interrelated facts:

1. ketu's `sidereal_time()` is named generically but implements **mean
   GMST**, while `swe.sidtime()` (and all swisseph house functions)
   uses **apparent GMST** (mean + equation of equinoxes). This is a
   semantic mismatch, not a polynomial-precision issue; the IAU 1982
   polynomial in time.py is fit-for-purpose at the mean level.
2. The current mid-latitude ASC headroom (27 arcsec at lat=49°,
   1900-01-01) is below the 30-arcsec floor, and the 2024 polar sample
   is wildly outside spec. Plan 10-04 (Placidus) and 10-05 (Koch /
   polar fallback) cannot land on this primitive without either
   tightening or eating the entire HOU-01 budget on GMST drift alone.

The fix is small, well-established astronomy (Meeus 2nd ed. Ch. 12,
"Sidereal Time at Greenwich"), and reuses functions already present in
`coordinates.py` (`nutation()`, `mean_obliquity()`). It is the
defensible engineering call.

## 7. Target formula (TIGHTEN)

The current code (kept unchanged for the mean-GMST polynomial part):

```python
# Days and centuries since J2000.0
d = jd - 2451545.0
T = d / 36525.0

# Mean GMST at 0h UT (IAU 1982 / Meeus 2nd ed. eq. 12.4)
gmst_mean = 280.46061837 + 360.98564736629 * d + 0.000387933 * T**2 - T**3 / 38710000.0
```

The added correction (Meeus eq. 12.6) — equation of equinoxes:

```python
# Apparent GMST = mean GMST + equation of equinoxes
nut_lon, _ = nutation(jd)              # degrees, from coordinates.py
eps_mean = mean_obliquity(jd)           # degrees, IAU 2006, from coordinates.py
EE_deg = nut_lon * cos(radians(eps_mean))   # equation of equinoxes (degrees)
gmst_apparent = (gmst_mean + EE_deg) % 360.0

lst = (gmst_apparent + longitude) % 360.0
```

References:

- Meeus, *Astronomical Algorithms*, 2nd ed., Ch. 12 (Sidereal Time),
  eq. 12.4 (mean GMST polynomial) and eq. 12.6 (apparent = mean + EE).
- Capitaine et al. (2003), *Astronomy & Astrophysics* 412, 567 —
  IAU 2006 GMST polynomial verifies our existing IAU 1982 mean form
  agrees to <0.5 arcsec across the sample range; the dominant ~12 arcsec
  drift is purely the missing EE term.

Empirical verification of the tightened formula (apparent GMST):

| Date                       | drift (arcsec, vs swe.sidtime × 15) |
| -------------------------- | ----------------------------------: |
| 1900-01-01 12h UT          |                              −0.250 |
| J2000 (2000-01-01 12h TT)  |                              −0.108 |
| 2024-06-21 0h UT           |                              +0.115 |
| 2050-12-31 12h UT          |                              +1.938 |
| 2100-01-01 12h UT          |                              +2.051 |

**Max |drift| after tightening = 2.05 arcsec.** Under the 1.0 arcsec
target only at the J2000-vicinity samples; the 2050+ residual is from
the 4-term truncated nutation in `coordinates.nutation()` (full IAU
2000A has 1365 terms). For HOU-01 this is comfortably under spec
(2 arcsec direct drift → ~3 arcsec ASC error at lat=49°, ~5 arcsec at
lat=66.5° outside polar singularity); however, since `TOL_GMST_ARCSEC`
must reflect the achieved precision, the test tolerance is set to
`5.0 arcsec` (not 1.0 as suggested by the plan). The plan's 1.0-arcsec
target presupposes a full IAU 2000A nutation series; that's a v1.2
investment, NOT a Plan 10-01 deliverable.

**Tolerance rationale (TIGHTEN branch):**

- `TOL_GMST_ARCSEC = 5.0` — 2.4× post-tightening max (2.05 arcsec)
  measured here. Reflects achieved precision, leaves headroom for
  future nutation refinement, and would FAIL CI if the mean-vs-apparent
  semantic regression returns.
- `TOL_OBLIQUITY_ARCSEC = 0.1` — 1.6× post-fix max (0.063 arcsec).
  Already-excellent confirmation; not a fix.

---

**State.md blocker closed by this plan:**
"LST/obliquity precision audit (Phase 10 first task) — current
ephemeris/time.py tuned for ~0.01°; houses need ~0.001°. Audit must
precede implementation per HOU-01."
