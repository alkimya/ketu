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
- **North Node**: True North Node
- **Lilith** ⚸: Black Moon (Mean Apogee)

## Aspects

### Harmonic Theory

Aspects are based on the division of the **semi-circle** (180°) by whole numbers, creating **harmonics**. Since an aspect never exceeds 180° (beyond that we measure from the other side), we work on a division of the semi-circle by 6.

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

## Orbs

### Orb Principle

In the Arabic tradition, each **planet has an orb** (zone of influence) that is specific to it. The orb of an aspect between two planets is calculated as the **half-sum of the orbs of the two planets**, multiplied by the **harmonic coefficient**.

```python
# Orb calculation in Ketu
orb = (orb_planet1 + orb_planet2) / 2 * harmonic_coefficient
```

### Harmonic Coefficients

Aspect       | Angle | Harmonic | Coefficient
-------------|-------|----------|------------
Conjunction  | 0°    | 1        | 1
Opposition   | 180°  | 1        | 1
Square       | 90°   | 2        | 1/2
Sextile      | 60°   | 3        | 1/3
Trine        | 120°  | 3        | 2/3
Semi-sextile | 30°   | 6        | 1/6
Quincunx     | 150°  | 6        | 5/6

### Calculation Examples

#### Sun-Moon Aspect (Conjunction)

- Sun Orb: 12°
- Moon Orb: 12°
- Coefficient: 1 (conjunction)
- Final Orb: (12 + 12) / 2 × 1 = **12°**

#### Mercury-Mars Aspect (Square)

- Mercury Orb: 8°
- Mars Orb: 10°
- Coefficient: 1/2 (square)
- Final Orb: (8 + 10) / 2 × 0.5 = **4.5°**

#### Venus-Jupiter Aspect (Sextile)

- Venus Orb: 8°
- Jupiter Orb: 10°
- Coefficient: 1/3 (sextile)
- Final Orb: (8 + 10) / 2 × 0.333 = **3°**

### Default Orbs (inspired by Abu Ma'shar)

Body                    | Orb
------------------------|--------
Sun, Moon               | 12°
Mercury, Venus          | 8°
Mars, Jupiter, Saturn   | 10°
Uranus, Neptune         | 6°
Pluto                   | 4°
Rahu, Lilith            | 0°

**Note**: Orbs can be customized as needed. See [example 05](../../examples/05_custom_orbs.py).

## Aspect Types

Ketu calculates 7 major aspects based on harmonics 1, 2, 3, and 6:

Aspect       | Angle | Symbol
-------------|-------|--------
Conjunction  | 0°    | ☌
Semi-sextile | 30°   | ⚺
Sextile      | 60°   | ⚹
Square       | 90°   | □
Trine        | 120°  | △
Quincunx     | 150°  | ⚻
Opposition   | 180°  | ☍

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

Ketu recognizes the 12 tropical zodiac signs:

### Sign List

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

## Swiss Ephemeris

Ketu uses **pyswisseph**, the Python interface to Swiss Ephemeris, for high-precision calculations:

- Precision: ±0.001" arc
- Period covered: 13000 BCE to 17000 CE
- Data: JPL DE431/DE441
- Model: Jet Propulsion Laboratory (NASA) planetary ephemerides

## Resources

### Websites

- [Swiss Ephemeris](https://www.astro.com/swisseph/) - Ephemeris documentation
- [Astrodienst](https://www.astro.com/) - Online astrological calculations
- [NASA JPL Horizons](https://ssd.jpl.nasa.gov/horizons/) - Astronomical ephemerides

### Technical Documentation

- [pyswisseph Documentation](https://astrorigin.com/pyswisseph/) - Python interface
- [JPL Ephemerides](https://ssd.jpl.nasa.gov/planets/eph_export.html) - Source data

## Next Steps

- Explore [Examples](examples.md) to see these concepts in action
- See the [API Reference](api.md) for technical implementation
- Read the [Quick Start Guide](quickstart.md) to begin coding
