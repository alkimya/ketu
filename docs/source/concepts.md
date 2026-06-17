# Astrological Concepts

## Coordinate System

### Ecliptic Longitude

**Ecliptic longitude** is the position of a celestial body measured along the ecliptic (the Earth's orbital plane around the Sun), expressed in degrees from 0° to 360°.

- 0° = Vernal point (0° Aries)
- 90° = Summer solstice (0° Cancer)
- 180° = Autumn equinox (0° Libra)
- 270° = Winter solstice (0° Capricorn)

### Ecliptic Latitude

**Ecliptic latitude** measures the angular distance of a body above (+) or below (-) the ecliptic plane.

### Distance in AU

The **Astronomical Unit** (AU) is the average Earth-Sun distance, approximately 149.6 million km.

## Astronomical Time

### Coordinated Universal Time (UTC)

**UTC** is the reference time standard, based on international atomic time.

### Julian Day

The **Julian Day** (JD) is a continuous dating system used in astronomy. JD begins at noon UTC on January 1, 4713 BCE in the proleptic Julian calendar.

```python
# Conversion in Ketu
from ketu.ephemeris.time import utc_to_julian
jday = utc_to_julian(datetime_utc)
```

## Celestial Bodies

Ketu calculates the positions of 14 celestial bodies (body IDs 0–13):

### Classical Planets

- **Sun** ☉ (body_id=0)
- **Moon** ☽ (body_id=1)
- **Mercury** ☿ (body_id=2)
- **Venus** ♀ (body_id=3)
- **Mars** ♂ (body_id=4)
- **Jupiter** ♃ (body_id=5)
- **Saturn** ♄ (body_id=6)

### Modern Planets

- **Uranus** ♅ (body_id=7)
- **Neptune** ♆ (body_id=8)
- **Pluto** ♇ (body_id=9)

### Fictitious Points

- **Rahu** ☊ (body_id=10): Mean North Node
- **Ketu** ☋ (body_id=11): Mean South Node
- **Lilith** ⚸ (body_id=12): Black Moon (Mean Apogee)

### Centaur Body (New in v1.3)

- **Chiron** ⚷ (body_id=13): Centaur body between Saturn and Uranus. Computed via embedded Chebyshev polynomial coefficients; valid range **1900–2100** (expanded in v1.4). Out-of-range input is silently clamped to the nearest segment boundary. See [Chiron](chiron.md) for details.

## Aspects

### Harmonic Theory

Aspects lean on the geometry of the zodiac circle. A **harmonic** divides a base angle into *n* equal parts, and the resulting fractions act as landmarks for the main kinds of planetary encounters.

The default framing uses the **half-circle base** (180°, the distance between conjunction and opposition): harmonics **1, 2, 3, 6** yield the 7 classical-to-Ptolemaic aspects (Conjunction, Semi-sextile, Sextile, Square, Trine, Quincunx, Opposition). This is the TRADITIONAL preset, the library default.

**Full-circle harmonics** (5, 9, 10 — quintiles, noviles, deciles) use a 360° base and are available as opt-in presets; they are not part of the default set.

#### Harmonic 1 (180°/1 = 180°)

- Conjunction (0°): same point
- Opposition (180°): opposite point

#### Harmonic 2 (180°/2 = 90°)

- Square (90°): quarter circle

#### Harmonic 3 (180°/3 = 60°)

- Sextile (60°): 1/3 of semi-circle
- Trine (120°): 2/3 of semi-circle

#### Harmonic 6 (180°/6 = 30°)

- Semi-sextile (30°): 1/6 of semi-circle
- Quincunx (150°): 5/6 of semi-circle

The full-circle minor harmonics — **H5** (quintiles), **H9** (noviles), **H10** (deciles) — are **available in code** but are not part of the default framing. They are opt-in via the `EXTENDED` preset or `aspects_for_harmonics([5, 9, 10])` (see [Configurable Aspect Sets](#configurable-aspect-sets-new-in-v1-1-updated-in-v1-3) below).

### Summary Table

Harmonic | Division | Aspects
---------|----------|------------------
1        | 180°/1   | Conjunction (0°), Opposition (180°)
2        | 180°/2   | Square (90°)
3        | 180°/3   | Sextile (60°), Trine (120°)
6        | 180°/6   | Semi-sextile (30°), Quincunx (150°)

The table above lists the 7 default half-circle aspects (the TRADITIONAL preset). The full-circle minor aspects (H5/H9/H10) are available in code; see the note above and [Configurable Aspect Sets](#configurable-aspect-sets-new-in-v1-1-updated-in-v1-3).

**Default aspect set (v1.3+):** the library default is the **7 half-circle aspects**
(harmonics 1, 2, 3, 6 — TRADITIONAL preset): Conjunction, Semi-sextile, Sextile, Square,
Trine, Quincunx, Opposition. The full-circle minor harmonics (H5/H9/H10) are **opt-in**
and not included in the default.

(configurable-aspect-sets-new-in-v1-1-updated-in-v1-3)=
### Configurable Aspect Sets (New in v1.1, updated in v1.3)

Rather than always computing all 14 aspects, you can select a preset or pass a custom mask:

- **TRADITIONAL** *(library default)*: the 7 half-circle aspects — Conjunction, Semi-sextile,
  Sextile, Square, Trine, Quincunx, Opposition (harmonics 1, 2, 3, 6)
- **CLASSICAL**: Conjunction, Sextile, Square, Trine, Opposition (5 major aspects; the old
  v1.2 default — still available as the opt-in "5 majors" preset)
- **EXTENDED**: all 14 aspects

```python
from ketu.aspects import calculate_aspects, CLASSICAL, TRADITIONAL, EXTENDED

# New library default (7 half-circle aspects):
aspects = calculate_aspects(jday)                        # uses TRADITIONAL

# Old 5-major default (restore v1.2 behavior):
aspects = calculate_aspects(jday, aspects=CLASSICAL)     # 5 aspects

# All 14 aspects:
aspects = calculate_aspects(jday, aspects=EXTENDED)      # 14 aspects
```

**Harmonic composition with `aspects_for_harmonics`** (New in v1.3): build a custom
aspect set from any combination of the supported harmonics. This is the harmonic-selection
sister function to the named presets:

```python
from ketu.aspects import aspects_for_harmonics

# Compose the library default explicitly (7 half-circle):
mask = aspects_for_harmonics([1, 2, 3, 6])

# Opt into the full-circle minor aspects:
minors = aspects_for_harmonics([5, 9, 10])

# Just the Sextile and Trine (harmonic 3):
h3_only = aspects_for_harmonics([3])

# All 14:
all14 = aspects_for_harmonics([1, 2, 3, 5, 6, 9, 10])
```

`aspects_for_harmonics` returns a frozen `numpy.bool_` mask of length 14, which can be
passed directly as the `aspects=` argument to any Ketu function. Valid harmonics:
`{1, 2, 3, 5, 6, 9, 10}`.

### Dynamic Harmonic Generator (generate_harmonic_aspects)

`generate_harmonic_aspects(h)` builds aspect specs on the fly for **any** integer harmonic
`h` (2 ≤ h ≤ 64), not just the named-preset harmonics. It uses the full-circle 360°
convention folded to 0–180°, and the returned array has the same dtype as `core.aspects`,
making it a drop-in for every consumer.

```python
from ketu.aspects import generate_harmonic_aspects

# Harmonic 7: 3 unique folded angles (septile family)
specs = generate_harmonic_aspects(7)
print(len(specs))          # 3
print(specs['name'])       # [b'H7-1', b'H7-2', b'H7-3']
print(specs['angle'])      # [51.43, 102.86, 154.29]
print(specs['coef'])       # [0.1429, 0.2857, 0.4286]

# Pass to calculate_aspects via dynamic_specs:
from ketu.aspects import calculate_aspects
jd = 2451545.0  # J2000
result = calculate_aspects(jd, dynamic_specs=generate_harmonic_aspects(7))
```

The returned array is a drop-in for `core.aspects` (same dtype) and is passed as the
`dynamic_specs=` argument to `calculate_aspects`, `find_aspects_between_dates`, and
`calculate_synastry`.

> **Note on orbs:** Dynamic harmonic orbs use `coef = k / h` (full-circle convention). For
> high harmonics this yields orbs roughly half the size of the equivalent half-circle aspect
> — e.g. a septile (H7-1, coef ≈ 0.143) gives a smaller orb than a sextile (coef ≈ 0.333)
> for the same body pair. This is **accepted behaviour**: the two conventions coexist without
> unification (see the v1.4 release notes).

(synthetic-harmonic-naming)=
### Synthetic harmonic naming (H{h}-{k})

Ketu uses two distinct channels for harmonic aspects, and they follow different naming rules.

**GENERATOR channel** — `generate_harmonic_aspects(h)` always emits `H{h}-{k}` names
(k = 1..h//2), uniform and mechanical, with no traditional-name substitution.
The emitted `name` bytes are always `b'H{h}-{k}'` (S16 dtype), frozen across v1.5+
minor and patch releases.

**DETECTION channel** — when `calculate_aspects` or `find_aspects_between_dates` detects
an angle that collides with a canonical table aspect, they report the canonical table name
with static-first priority.  For example, a 120° hit is reported as `Trine` (i_asp=9),
not `H3-1` (i_asp=-2).  The `H{h}-{k}` label only appears in result rows for
genuinely off-table angles (i_asp=-2 sentinel).

**Traditional-name reference table** (documentation only — never emitted by the generator):

Synthetic name | Traditional name
---------------|------------------
H5-1           | Quintile
H5-2           | Biquintile
H7-1           | Septile
H9-1           | Novile
H9-2           | Binovile
H9-4           | Quadnovile

These traditional names are provided here as a human reference only.  They never appear
in the structured-array `name` bytes emitted by `generate_harmonic_aspects`.

(harmonics-h7-cli-new-in-v1-5)=
### `--harmonics h7` — arbitrary harmonics on the CLI (New in v1.5)

The CLI accepts the `h<N>` token form for `--harmonics` to select an arbitrary harmonic
family on the command line, without writing any Python code.

**Syntax:** `--harmonics h<N>` (h-prefix, case-insensitive; e.g. `h7`, `H7`). `N` must be
an integer in `[2, 64]`. The token selects only the chosen harmonic family via the
`dynamic_specs=` channel (see {ref}`synthetic-harmonic-naming` for the two-channel
explanation). The static aspect table mask is empty — only `H{N}-{k}` dynamic aspects
are detected.

**Semantics:** the resolved-config header on stderr reads `# Aspect set: h7 (...)`.
The stdout positions block and "Aspect Timing Example" trailing block are always emitted
unchanged (the timing example uses the classical Sun-Moon aspects regardless of the
`--harmonics` selection).

**Tight-grammar boundary — what is supported vs. deferred:**

| Form | Status | Example |
|---|---|---|
| `h<N>` alone | Supported (v1.5+) | `--harmonics h7` |
| Comma-separated index list | Supported (pre-existing) | `--harmonics 0,4,9` |
| Named preset | Supported (pre-existing) | `--harmonics classical` |
| Multi-harmonic mixing (`h7,h11`) | NOT YET SUPPORTED (HARMF-01) | rejected with error |
| Mixed preset+harmonic (`traditional,h7`) | NOT YET SUPPORTED (HARMF-01) | rejected with error |

Mixing forms (`h7,h11`, `traditional,h7`) are **deferred** to HARMF-01 and currently
rejected with an `argparse` error. Do not attempt them in v1.5.

**Worked example (J2000, septile family):**

```bash
python -m ketu --harmonics h7 aspects --date 2000-01-01T12:00:00Z
```

This emits septile-family aspects (`H7-1` ≈51.43°, `H7-2` ≈102.86°, `H7-3` ≈154.29°)
for all body pairs in orb at J2000, followed by the classical "Aspect Timing Example" block.
The stderr header confirms the resolved selection: `# Aspect set: h7 (3 aspects: H7-1 51°, H7-2 103°, H7-3 154°)`.

## Orbs

### Orb Principle

In the Arabic tradition, each **planet has an orb** (zone of influence) that is specific to it. The orb of an aspect between two planets is calculated as the **half-sum of the orbs of the two planets**, multiplied by the **harmonic coefficient**.

```python
# Orb calculation in Ketu
orb = [(orb_planet1 + orb_planet2) / 2] * harmonic_coefficient
```

### Default Orbs of Planets

Body                        | Orb
----------------------------|--------
Sun, Moon                   | 12°
Venus, Jupiter, Saturn      | 10°
Mercury, Mars               | 8°
Uranus, Neptune             | 6°
Pluto, Chiron               | 4°
Rahu, Ketu, Lilith          | 2° (since v1.7; previously 0°)

### Fictitious Points: Rahu, Ketu, Lilith (new in v1.7)

Prior to v1.7, Rahu (Mean Node, id 10), Ketu (Mean South Node, id 11), and Lilith
(Black Moon, id 12) carried a 0° orb — an Abu Ma'shar / Al-Biruni modelling choice
for fictitious (non-physical) points. Because the aspect-orb formula is
`(orb_b1 + orb_b2) / 2 × coef`, two zero-orb points yield a 0° joint orb,
meaning they can only form an aspect at exact separation — in practice never
detected. **v1.7 gives the three points a 2° longitude orb** so they enter
ecliptic aspects normally.

Orb examples with the new 2° point orb:

- Point↔point conjunction: **(2 + 2) / 2 × 1 = 2°**
- Rahu↔Sun opposition: **(2 + 12) / 2 × 1 = 7°**
- Ketu↔Moon trine: **(2 + 12) / 2 × 2/3 ≈ 4.67°**

**Rahu↔Ketu Opposition filter:** Ketu (Mean South Node) is the exact 180°
opposite of Rahu by construction — the two mean nodes are always separated by
180° in the geocentric ecliptic. With a non-zero orb, the aspect engine would
permanently detect this pair as an Opposition on every date, producing a
tautological artefact. The engine therefore suppresses **only** the simultaneous
condition `(body1, body2) == (Rahu, Ketu)` AND `aspect == Opposition`.
Every other Rahu or Ketu aspect is detected normally (Rahu↔Sun oppositions,
Rahu↔Ketu conjunctions, Ketu↔Lilith sextiles, etc.).

> **v1.7 — fictitious-point orbs (MINOR, not patch)**
>
> The 2° longitude orb causes aspect RESULTS to change: new node/Lilith aspects
> now appear in the output where none existed before, and the Rahu↔Ketu
> tautological Opposition no longer appears. Downstream consumers must treat
> the upgrade from 1.6.x to 1.7.0 as a **deliberate, reviewed upgrade** — NOT a
> neutral `pip install -U`. This is why the release carries version MINOR 1.7.0
> (semver: behaviour changes) rather than a patch increment.

### Aspect Types and Harmonic Coefficients

The 7 default half-circle aspects (TRADITIONAL preset, harmonics 1, 2, 3, 6):

Aspect         | Angle | Symbol | Harmonic | Coefficient
---------------|-------|--------|----------|------------
Conjunction    | 0°    | ☌      | 1        | 1
Semi-sextile   | 30°   | ⚺      | 6        | 1/6
Sextile        | 60°   | ⚹      | 3        | 1/3
Square         | 90°   | □      | 2        | 1/2
Trine          | 120°  | △      | 3        | 2/3
Quincunx       | 150°  | ⚻      | 6        | 5/6
Opposition     | 180°  | ☍      | 1        | 1

The 7 full-circle minor aspects (H5/H9/H10) remain available via `EXTENDED` / `aspects_for_harmonics([5, 9, 10])` and are listed in the full 14-aspect table in the [API reference](api.md).

### Calculation Examples

#### Sun-Moon Aspect (Conjunction)

- Sun Orb: 12°
- Moon Orb: 12°
- Coefficient: 1 (conjunction)
- Final Orb: (12 + 12) / 2 × 1 = **12°**

#### Mercury-Mars Aspect (Square)

- Mercury Orb: 8°
- Mars Orb: 8°
- Coefficient: 1/2 (square)
- Final Orb: (8 + 8) / 2 × 0.5 = **4°**

#### Venus-Jupiter Aspect (Sextile)

- Venus Orb: 10°
- Jupiter Orb: 10°
- Coefficient: 1/3 (sextile)
- Final Orb: (10 + 10) / 2 × 0.333 = **3.33°**

## House Systems

### What Are Houses?

The **astrological houses** divide the local sky into twelve sectors based on the observer's geographic location and the time of birth. Unlike the zodiac signs (which are fixed along the ecliptic), houses rotate with the Earth's daily rotation and depend on the local horizon and meridian.

Ketu supports six house systems (New in v1.1/v1.2):

- **Placidus** (`"placidus"`): The most widely used system in Western astrology. Divides each quadrant by time rather than space.
- **Koch** (`"koch"`): Similar to Placidus but using a different time-division formula; sensitive to high latitudes.
- **Porphyry** (`"porphyry"`): Divides each quadrant into three equal parts by longitude. Simpler and works at all latitudes.
- **Whole Sign** (`"whole_sign"`): Each house corresponds to an entire zodiac sign, starting from the rising sign.
- **Equal** (`"equal"`): Houses are 30° each, starting from the Ascendant degree.
- **Regiomontanus** (`"regiomontanus"`): Divides the celestial equator into equal parts; popular in medieval astrology.

### High Latitude Behavior

Placidus and Koch may fail to compute cusps at very high latitudes (above approximately 66°). Use `polar_fallback="porphyry"` to fall back gracefully, or `polar_fallback="raise"` (default) to receive a `HighLatitudeError`.

```python
from ketu.houses import calculate_houses, HighLatitudeError

jd = 2451545.0  # J2000
try:
    h = calculate_houses(jd, lat=70.0, lon=25.0, system="placidus")
except HighLatitudeError:
    h = calculate_houses(jd, lat=70.0, lon=25.0, system="porphyry")
```

See [Houses](houses.md) for the full API reference and examples.

## Sect (Day vs. Night Chart)

### What Is Sect?

**Sect** is a classical doctrine distinguishing *day charts* (Sun above the horizon at birth) from *night charts* (Sun below the horizon). This distinction affects the calculation of certain Arabic Parts such as the Part of Fortune and the Part of Spirit, which invert their formulas between day and night charts.

In Ketu, `is_day_chart(jd, lat, lon)` returns `True` when the Sun is above the horizon at the given time and location. This helper is used internally by `calculate_part` for sect-sensitive lots.

```python
from ketu.charts import is_day_chart

jd = 2451545.0       # J2000
lat, lon = 48.8566, 2.3522  # Paris
print(is_day_chart(jd, lat, lon))
```

See [Arabic Parts](arabic_parts.md) for how sect influences Fortune and Spirit formulas.

(equatorial-declination-new-in-v1-5)=
## Equatorial Declination — New in v1.5

### Declination δ vs. Ecliptic Latitude β

Ketu tracks two distinct north/south quantities for each body:

- **Ecliptic latitude β** — angular distance above/below the ecliptic plane. Returned by `lat(jd, body)`. The function `is_ascending` tracks whether β is rising.
- **Equatorial declination δ** — angular distance north/south of the celestial equator. Returned by `declination(jd, body)`. The function `is_ascending_declination` tracks whether δ is rising (montante/descendante).

**These are different quantities and disagree on different days.** "Ascending Moon" is ambiguous without specifying which coordinate system:

| Function | Tracks | Concept |
|---|---|---|
| `is_ascending(jd, 1)` | β rising (ecliptic latitude) | Traditional latitude motion |
| `is_ascending_declination(jd, 1)` | δ rising (declination) | Biodynamic montant/descendant |

**Proof of β-vs-δ independence:** at 2025-03-07 (JD=2460742.0), Moon near a major standstill peak (δ≈+28.66°), `is_ascending_declination=True` (dδ/dt=+0.30°/day) while `is_ascending=False` (β descending). They flip on different days.

### Montant / Descendant (Biodynamic Framing)

In biodynamics, the **montant/descendant** cycle refers to the trajectory of the Moon's own equatorial declination δ — not to zodiacal sign conventions or ecliptic latitude.

- **Montante** (ascending in δ): dδ/dt > 0, Moon moving northward. `is_ascending_declination` returns `True`.
- **Descendante** (descending in δ): dδ/dt < 0, Moon moving southward. `is_ascending_declination` returns `False`.

The Moon's δ cycle period is approximately **27.21 days** (draconic/nodal month) — the time between two successive northward crossings of the celestial equator. This is close to, but distinct from, the 27.32-day tropical month.

```python
from ketu.calculations import (
    declination,
    declination_velocity,
    is_ascending_declination,
)

jd = 2451545.0  # J2000

delta = declination(jd, 1)
vel   = declination_velocity(jd, 1)

print(f"Moon δ: {delta:.4f}°")
print(f"Moon dδ/dt: {vel:.4f}°/day")
print("Montante" if is_ascending_declination(jd, 1) else "Descendante")
```

### Out-of-Bounds (OOB)

A body is **out-of-bounds** (hors limites) when its declination exceeds the instantaneous obliquity of the ecliptic: |δ| > ε(jd).

Under normal conditions no planet can exceed the obliquity — the Sun's declination defines the obliquity bounds (±ε ≈ ±23.4°). The Moon is the exception: because the lunar orbital plane is tilted ~5° relative to the ecliptic, the Moon can exceed the Sun's extreme declinations during the **major lunar standstill** (~18.6-year nodal cycle). During 2024–2025, the Moon reaches |δ| ≈ 28.7°.

The OOB threshold uses the **instantaneous true obliquity** ε(jd) — not mean obliquity — because nutation shifts ε by up to ±17 arcseconds.

```python
from ketu.calculations import is_out_of_bounds

jd_standstill = 2460742.0   # 2025-03-07, near major standstill peak

print(f"Moon OOB: {is_out_of_bounds(jd_standstill, 1)}")   # True
```

### CHART_DTYPE — body_decl field (New in v1.5)

`CHART_DTYPE` gains an additive field `body_decl` (`float64[14]`) holding the equatorial declination δ for each of the 14 bodies. This is an **additive dtype change**: the body count (14) is unchanged, but downstream code using positional access or `.view()` on `CHART_DTYPE` must adapt (downstream impact documented, not auto-migrated).

```python
from ketu.charts import compute_chart

chart = compute_chart(jd, 48.8566, 2.3522)
moon_decl = chart["body_decl"][1]   # Moon δ in degrees
```

### CHART_DTYPE — body_decl_speed field (New in v1.8)

`CHART_DTYPE` gains an additive field `body_decl_speed` (`float64[14]`)
holding the equatorial declination velocity dδ/dt (degrees/day) for each of
the 14 bodies. The field sits at dtype index 8, after `body_decl`.

**What the sign means:** positive = northward (montante in biodynamics),
negative = southward (descendante). This mirrors `body_speeds` for ecliptic
longitude: the sign is the direction of motion, the magnitude is the rate.

**Why finite difference at Δt = 0.01 day:** Ketu computes all position
derivatives by forward finite difference at a 0.01-day step — the same idiom
used by `lat_velocity`, `dist_velocity_au`, and the scalar
`declination_velocity`. The step is a package-wide constant, not configurable,
and introduces no new API surface. The difference between two declination
values 0.01 day apart divided by 0.01 gives dδ/dt in °/day.

**Standstill contract and `DECL_STANDSTILL_EPS`:** When |dδ/dt| is very
small, the body is at a **declination standstill** — neither clearly montante
nor descendante. Ketu defines the threshold as
`DECL_STANDSTILL_EPS = 0.001` °/day and exports it as a public constant.
The chart-level helper `is_ascending_declination_chart(chart)` applies this
threshold and returns `int8` values: `+1` (ascending), `-1` (descending),
`0` (standstill — |dδ/dt| ≤ EPS).

**Library design principle:** Ketu computes all the astronomy — the finite
difference, the declination velocity, and the standstill threshold — and
exposes them as plain array fields and a named constant. Downstream consumers
read `chart["body_decl_speed"]`, compare against `DECL_STANDSTILL_EPS`, or
call `is_ascending_declination_chart`; they compute no astronomy of their own.

**Additive dtype change:** the body count (14) is unchanged. Code using named
field access (`chart["body_decl_speed"]`) needs no migration. Positional /
`.view()` consumers must adapt (see `UPGRADING.md` at the repository root →
"v1.7 -> v1.8").

```python
from ketu.charts import compute_chart, is_ascending_declination_chart
from ketu.calculations import DECL_STANDSTILL_EPS
from ketu.calculations import utc_to_julian
from datetime import datetime, timezone

jd = utc_to_julian(datetime(2026, 6, 17, 12, 0, tzinfo=timezone.utc))
chart = compute_chart(jd, lat=48.8566, lon=2.3522)

# Per-body dδ/dt in °/day (positive = northward)
speeds = chart["body_decl_speed"]
moon_speed = float(speeds[1])   # Moon dδ/dt

# Chart-level montant/descendant/standstill
directions = is_ascending_declination_chart(chart)
# +1 = montante, -1 = descendante, 0 = standstill (|dδ/dt| ≤ DECL_STANDSTILL_EPS)
moon_dir = int(directions[1])

print(f"Moon dδ/dt: {moon_speed:.4f} °/day")
print(f"Standstill threshold: {DECL_STANDSTILL_EPS} °/day")
if moon_dir == 1:
    print("Moon montante (northward)")
elif moon_dir == -1:
    print("Moon descendante (southward)")
else:
    print("Moon at declination standstill")
```

(declination-aspects-new-in-v1-6)=
## Declination Aspects — New in v1.6

Declination aspects compare two bodies on the **equatorial declination axis** (δ),
independent of ecliptic longitude. The detector lives in the additive
`ketu.declination` subpackage — `CHART_DTYPE` is unchanged. It consumes
`chart["body_decl"]` (the `(14,)` field shipped in v1.5).

### Parallel and Contra-Parallel

- **Parallel** (`P`): two bodies share the same declination δ **AND** are on the
  **same side** of the celestial equator (both north OR both south).
  Signed-δ rule: `sign(δ₁) == sign(δ₂) ≠ 0  AND  |δ₁ − δ₂| ≤ orb`.
  The same-hemisphere rule is **strict** — the dominant convention across Sepharial,
  Carter, Cafe Astrology, Lunarium, McAfee, Kerykeion, and astro.com.

- **Contra-parallel** (`CP`): equal magnitude of δ but on **opposite sides** of the
  celestial equator. Signed-δ rule:
  `sign(δ₁) ≠ sign(δ₂)  AND  both ≠ 0  AND  |δ₁ + δ₂| ≤ orb`.

- **Zero-sign trap:** a body exactly on the celestial equator (δ = 0, `np.sign` → 0)
  forms **neither** a parallel nor a contra-parallel. Two bodies exactly at δ = 0
  have 0° separation but are **not** flagged.

```python
import numpy as np
from ketu.declination import find_declination_aspects

decl = np.zeros(14)
decl[0] = 20.0   # Sun  δ = +20.0°
decl[1] = 20.5   # Moon δ = +20.5°  → same hemisphere, gap 0.5° ≤ 1.0° orb

aspects = find_declination_aspects(decl)
print(aspects)   # [(0, 1, 'P', 0.5, 1.0)] — Sun/Moon parallel
```

### The Orb Formula (Body-Derived)

The per-pair orb on the declination axis is:

```text
δ_orb(b1, b2) = max((bodies['orb'][b1] + bodies['orb'][b2]) / 2 × DECLA_COEF, MIN_DECL_ORB)
```

with `DECLA_COEF = 1/12 ≈ 0.0833` and `MIN_DECL_ORB = 0.5°`.

**Worked Sun/Moon example:** Sun orb 12° + Moon orb 12° → mean 12° → × 1/12 →
exactly **1.0°**. The coefficient `1/12` is the reciprocal of the maximum body orb
(Sun/Moon both at 12°) — a justified exact fraction, not a magic number — chosen so
Sun/Moon lands on the published 1° natal consensus (Carter, Cafe Astrology,
astro.com).

**Floor example (v1.6 and earlier):** When Rahu, Ketu, and Lilith had a 0° longitude
orb, the declination formula yielded 0° and the floor kicked in, giving **0.5°**
so they remained detectable on the δ axis.

**v1.7 note:** As of v1.7 the **longitude** orb of Rahu, Ketu, and Lilith is 2°
(see the Fictitious Points subsection above). The two axes are **independent**: the
longitude change does NOT affect the declination formula. On the δ axis the formula
still yields `(2+2)/2 × 1/12 ≈ 0.167°` for a point↔point pair, which is below the
0.5° floor — so the δ orb for Rahu/Lilith/Ketu pairs remains **0.5°** (floor),
unchanged from v1.6.

Pair                 | δ orb
---------------------|----------------------------------
Sun / Moon           | 1.0°
Sun / Mars           | 0.833°
Jupiter / Saturn     | 0.833°
Uranus / Neptune     | 0.5°
Rahu / Lilith        | 0.5° (floor, unchanged from v1.6)

### Biodynamic Framing

Parallel ≈ **conjunction by declination**; contra-parallel ≈ **opposition by
declination** (Sepharial: "they act as if in conjunction"; Carter couples parallel with
conjunction). These are ANGLES/relationships between bodies on the δ axis — the same
aspect-centric biodynamic framing as the rest of Ketu, not zodiacal-sign conventions.

### Parallel ≠ Longitude Conjunction (the Key Distinction)

Two bodies can be **parallel in declination without being conjunct in ecliptic
longitude**, and vice-versa. Declination δ (equatorial) and longitude (ecliptic) are
**independent measurements**. A "double whammy" (both conjunct AND parallel) is
notably stronger, but the detection paths are entirely separate —
`find_declination_aspects` consumes **only** `body_decl`, never longitudes.

### Symbols and Abbreviations

| Aspect | Symbol | Text abbrev | Notes |
|--------|--------|-------------|-------|
| Parallel | `//` (proposed U+2BDD) | `P` | `‖` / `⫽` as text fallbacks |
| Contra-parallel | `#` (proposed U+2BDE) | `CP` | Dominant in printed tables |

The `//` and `#` glyphs are proposals from David Faulks (Unicode L2/16-174, 2016) —
not yet in the Unicode standard. Text abbreviations `P` / `CP` match Solar Fire and
Astrodienst conventions and are used as the `kind` field values in `DECLA_ASPECT_DTYPE`.

### Out-of-Bounds Interaction

OOB bodies (|δ| > ε, tracked via `is_out_of_bounds` from v1.5) participate in P/CP
detection **mechanically identically** — the formula does not change. "Both OOB" is
an **interpretive annotation** the caller composes (e.g. by combining
`is_out_of_bounds` results with the aspect output), **not** a detection flag. Some
authors (Boehrer, McAfee) consider two-OOB parallels especially intense — a
delineation note only.

## Planetary Movements

### Retrogradation

**Retrogradation** is the apparent movement of a planet that seems to move backward in the zodiac. It's an optical illusion due to differences in orbital speed between Earth and the observed planet.

```python
from ketu.calculations import is_retrograde

if is_retrograde(jday, planet_id):
    print("Planet retrograde")
```

### Average Speeds

Planet  | Average Speed | Complete Cycle
--------|---------------|-------------------
Moon    | 13.18°/day    | 27.3 days
Mercury | 1.38°/day     | 88 days
Venus   | 1.20°/day     | 225 days
Sun     | 0.99°/day     | 365.25 days
Mars    | 0.52°/day     | 687 days
Jupiter | 0.08°/day     | 11.9 years
Saturn  | 0.03°/day     | 29.5 years
Uranus  | 0.01°/day     | 84 years
Neptune | 0.01°/day     | 165 years
Pluto   | 0.00°/day     | 248 years

## Zodiac Signs

No | Sign        | Symbol | Start Degree | End Degree
---|-------------|--------|--------------|----------
1  | Aries       | ♈      | 0°           | 30°
2  | Taurus      | ♉      | 30°          | 60°
3  | Gemini      | ♊      | 60°          | 90°
4  | Cancer      | ♋      | 90°          | 120°
5  | Leo         | ♌      | 120°         | 150°
6  | Virgo       | ♍      | 150°         | 180°
7  | Libra       | ♎      | 180°         | 210°
8  | Scorpio     | ♏      | 210°         | 240°
9  | Sagittarius | ♐      | 240°         | 270°
10 | Capricorn   | ♑      | 270°         | 300°
11 | Aquarius    | ♒      | 300°         | 330°
12 | Pisces      | ♓      | 330°         | 360°

```python
from ketu.calculations import body_sign
import ketu

# Get a planet's sign
sign_data = body_sign(longitude)
sign_index = sign_data[0]  # 0-11
degrees = sign_data[1]      # 0-29
minutes = sign_data[2]      # 0-59
seconds = sign_data[3]      # 0-59

sign_name = ketu.signs[sign_index]
```

## Planetary Configurations

### Grand Trine

Three planets forming trines with each other (equilateral triangle of 120°).

### T-Square

Two planets in opposition (180°), both square (90°) to a third planet (apex).

### Yod (Finger of God)

Two planets in sextile (60°), both quincunx (150°) to a third planet (apex).

### Grand Square

Four planets forming four squares (90°) and two oppositions (180°), creating a square in the chart.

## Cycles and Returns

### Planetary Returns

A **planetary return** occurs when a planet returns to its natal position (same ecliptic longitude).

**Main returns:**

- **Solar return**: Astrological birthday (365.25 days)
- **Lunar return**: Approximately every 27.3 days
- **Jupiter return**: Approximately every 12 years
- **Saturn return**: Approximately at 29-30 years and 58-60 years

Ketu provides dedicated functions for solar and lunar returns in `ketu.returns`. See [Predictive Charts](predictive_charts.md) for details.

## Next Steps

- Explore [Examples](examples.md) to see these concepts in action
- See the [API Reference](api.md) for technical implementation
- Read the [Quick Start Guide](quickstart.md) to begin coding
- Discover [House Systems](houses.md) for chart calculation
