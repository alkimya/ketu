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

- **Chiron** ⚷ (body_id=13): Centaur body between Saturn and Uranus. Computed via embedded Chebyshev polynomial coefficients; valid range 1950–2050. See [Chiron](chiron.md) for details.

## Aspects

### Harmonic Theory

Aspects lean on the geometry of the zodiac circle: we often slice it into twelve 30° segments, but when comparing two planets we bring the angle back to the **half-circle** (180°) to keep the shortest distance. The **harmonics** are simply the integer fractions of those 180° by 30º, and they act as landmarks for the main kinds of planetary encounters.

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

#### Harmonic 5 (360°/5 = 72°)

- Quintile (72°): 1/5 of circle
- Biquintile (144°): 2/5 of circle

#### Harmonic 9 (360°/9 = 40°)

- Novile (40°): 1/9 of circle
- Binovile (80°): 2/9 of circle
- Quadrinovile (160°): 4/9 of circle

#### Harmonic 10 (360°/10 = 36°)

- Decile (36°): 1/10 of circle (semi-quintile)
- Tredecile (108°): 3/10 of circle (tri-decile)

### Summary Table

Harmonic | Division | Aspects
---------|----------|------------------
1        | 180°/1   | Conjunction (0°), Opposition (180°)
2        | 180°/2   | Square (90°)
3        | 180°/3   | Sextile (60°), Trine (120°)
5        | 360°/5   | Quintile (72°), Biquintile (144°)
6        | 180°/6   | Semi-sextile (30°), Quincunx (150°)
9        | 360°/9   | Novile (40°), Binovile (80°), Quadrinovile (160°)
10       | 360°/10  | Decile (36°), Tredecile (108°)

Ketu supports all 14 aspects across harmonics 1, 2, 3, 5, 6, 9, and 10.

### Configurable Aspect Sets (New in v1.1)

Rather than always computing all 14 aspects, you can select a preset or pass a custom mask:

- **CLASSICAL**: Conjunction, Sextile, Square, Trine, Opposition (5 aspects)
- **TRADITIONAL**: CLASSICAL + Semi-sextile and Quincunx (7 aspects)
- **EXTENDED**: all 14 aspects

```python
from ketu.aspects import calculate_aspects, CLASSICAL, TRADITIONAL, EXTENDED

aspects = calculate_aspects(jday, aspects=CLASSICAL)
```

## Orbs

### Orb Principle

In the Arabic tradition, each **planet has an orb** (zone of influence) that is specific to it. The orb of an aspect between two planets is calculated as the **half-sum of the orbs of the two planets**, multiplied by the **harmonic coefficient**.

```python
# Orb calculation in Ketu
orb = [(orb_planet1 + orb_planet2) / 2] * harmonic_coefficient
```

### Default Orbs of Planets

Body                    | Orb
------------------------|--------
Sun, Moon               | 12°
Venus, Jupiter, Saturn  | 10°
Mercury, Mars           | 8°
Uranus, Neptune         | 6°
Pluto, Chiron           | 4°
Rahu, Lilith            | 0°

### Aspect Types and Harmonic Coefficients

Ketu calculates 14 aspects across harmonics 1, 2, 3, 5, 6, 9, and 10:

Aspect         | Angle | Symbol | Harmonic | Coefficient
---------------|-------|--------|----------|------------
Conjunction    | 0°    | ☌      | 1        | 1
Semi-sextile   | 30°   | ⚺      | 6        | 1/6
Decile         | 36°   |        | 10       | 1/10
Novile         | 40°   |        | 9        | 1/9
Sextile        | 60°   | ⚹      | 3        | 1/3
Quintile       | 72°   |        | 5        | 1/5
Binovile       | 80°   |        | 9        | 2/9
Square         | 90°   | □      | 2        | 1/2
Tredecile      | 108°  |        | 10       | 3/10
Trine          | 120°  | △      | 3        | 2/3
Biquintile     | 144°  |        | 5        | 2/5
Quincunx       | 150°  | ⚻      | 6        | 5/6
Quadrinovile   | 160°  |        | 9        | 4/9
Opposition     | 180°  | ☍      | 1        | 1

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
