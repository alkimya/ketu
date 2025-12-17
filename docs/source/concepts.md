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
jday = ketu.utc_to_julian(datetime_utc)
```

## Celestial Bodies

Ketu calculates the positions of 13 celestial bodies:

### Classical Planets

- **Sun** ☉
- **Moon** ☽
- **Mercury** ☿
- **Venus** ♀
- **Mars** ♂
- **Jupiter** ♃
- **Saturn** ♄

### Modern Planets

- **Uranus** ♅
- **Neptune** ♆
- **Pluto** ♇

### Fictitious Points

- **Rahu** ☊: Mean North Node
- **Ketu** ☋: Mean South Node
- **Lilith** ⚸: Black Moon (Mean Apogee)

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

### Summary Table

Harmonic | Division | Aspects
---------|----------|------------------
1        | 180°/1   | Conjunction (0°), Opposition (180°)
2        | 180°/2   | Square (90°)
3        | 180°/3   | Sextile (60°), Trine (120°)
6        | 180°/6   | Semi-sextile (30°), Quincunx (150°)

In practice, we use mainly harmonics 1, 2 and 3.

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
Pluto                   | 4°
Rahu, Lilith            | 0°

### Aspect Types and Harmonic Coefficients

Ketu calculates 7 major aspects based on harmonics 1, 2, 3, and 6:

Aspect       | Angle | Symbol | Harmonic | Coefficient
-------------|-------|--------|----------|------------
Conjunction  | 0°    | ☌      | 1        | 1
Semi-sextile | 30°   | ⚺      | 6        | 1/6
Sextile      | 60°   | ⚹      | 3        | 1/3
Square       | 90°   | □      | 2        | 1/2
Trine        | 120°  | △      | 3        | 2/3
Quincunx     | 150°  | ⚻      | 6        | 5/6
Opposition   | 180°  | ☍      | 1        | 1

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

## Planetary Movements

### Retrogradation

**Retrogradation** is the apparent movement of a planet that seems to move backward in the zodiac. It's an optical illusion due to differences in orbital speed between Earth and the observed planet.

```python
# Check retrogradation
if ketu.is_retrograde(jday, planet_id):
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
# Get a planet's sign
sign_data = ketu.body_sign(longitude)
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

```python
# Calculate a return
natal_position = ketu.long(natal_jday, planet_id)
current_position = ketu.long(current_jday, planet_id)

# The return occurs when the difference < orb
if abs(current_position - natal_position) < 1.0:
    print("Planetary return!")
```

## Next Steps

- Explore [Examples](examples.md) to see these concepts in action
- See the [API Reference](api.md) for technical implementation
- Read the [Quick Start Guide](quickstart.md) to begin coding
