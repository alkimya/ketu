# Examples

## Moon Phases with Pattern Matching

```python
import ketu
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def lunar_phase(jday):
    """Determine the lunar phase with pattern matching"""
    
    # Calculate the Sun-Moon angle
    sun_long = ketu.long(jday, 0)
    moon_long = ketu.long(jday, 1)
    
    # Elongation of the Moon relative to the Sun
    elongation = (moon_long - sun_long) % 360
    
    # Pattern matching on elongation
    match elongation:
        case e if 0 <= e < 22.5:
            return “🌑 New Moon”, e, “Conjunction”
        case e if 22.5 <= e < 67.5:
            return “🌒 First Quarter”, e, “Waxing”
        case e if 67.5 <= e < 112.5:
            return “🌓 First Quarter”, e, “Waxing Quarter”
        case e if 112.5 <= e < 157.5:
            return “🌔 Waxing Gibbous”, e, “Gibbous”
        case e if 157.5 <= e < 202.5:
            return “🌕 Full Moon”, e, “Opposition”
        case e if 202.5 <= e < 247.5:
            return “🌖 Waning Gibbous Moon”, e, “Gibbous”
        case e if 247.5 <= e < 292.5:
            return “🌗 Last Quarter”, e, “Waning Square”
        case e if 292.5 <= e < 337.5:
            return “🌘 Last Crescent”, e, “Balsamic”
        case _:
            return “🌑 New Moon”, e, “Conjunction”

def lunar_calendar(year, month):
    """Generate a lunar phase calendar for a month"""
    
    print(f“\n{‘=’*50}”)
    print(f“LUNAR CALENDAR - {month:02d}/{year}”)
    print(f“{‘=’*50}\n”)
    
    tz = ZoneInfo(“UTC”)
    
    # For each day of the month
    for day in range(1, 32):
        try:
            dt = datetime(year, month, day, 12, 0, tzinfo=tz)
            jday = ketu.utc_to_julian(dt)
            
            phase, elongation, description = lunar_phase(jday)
            
            # Display the main phases
            if any(key in phase for key in [“New”, “First Quarter”, 
                                            “Full”, “Last Quarter”]):
                print(f“{day:02d}/{month:02d}: {phase} ({elongation:.1f}°)”)
                
        except ValueError:
            break  # End of month

# Example of use
lunar_calendar(2024, 1)
```

## Planetary Transits

```python
import ketu
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Tuple
from zoneinfo import ZoneInfo


@dataclass
class Transit:
    """Represents a planetary transit"""
    planet: str
    aspect: str
    natal_planet: str
    date: datetime
    orb: float
    exact: bool = False

def search_transits(natal_date, transit_date, planets_to_follow=None):
    """Search for today's transits on a natal chart"""
    
    if planets_to_follow is None:
        planets_to_follow = [0, 1, 2, 3, 4, 5, 6]  # Sun to Saturn
    
    # Natal positions
    natal_jday = ketu.utc_to_julian(natal_date)
    natal_positions = {}
    for i in planets_to_follow:
        natal_positions[i] = ketu.long(natal_jday, i)
    
    # Transit positions
    transit_jday = ketu.utc_to_julian(transit_date)
    transits = []
    
    for i_transit in planets_to_follow:
        transit_pos = ketu.long(transit_jday, transit_i)
        
        for natal_i, natal_pos in natal_positions.items():
            # Calculate the aspect
            diff = abs(transit_pos - natal_pos) % 360
            if diff > 180:
                diff = 360 - diff
            
            # Check each aspect type
            for j, angle in enumerate(ketu.aspects[“value”]):
                max_orb = ketu.get_orb(i_transit, i_natal, j)
                orb = abs(diff - angle)
                
                if orb <= max_orb:
                    transit = Transit(
                        planet=ketu.body_name(i_transit),
                        aspect=ketu.aspects[“name”][j].decode(),
                        natal_planet=ketu.body_name(i_natal),
                        date=date_transit,
                        orb=orb,
                        exact=(orb < 1.0)
                    )
                    transits.append(transit)
    
    return transits

# Example
natal = datetime(1990, 5, 15, 14, 30, tzinfo=ZoneInfo(“Europe/Paris”))
transit = datetime.now(ZoneInfo(“Europe/Paris”))

transits = search_transits(natal, transit)
for t in transits:
    exact = “ EXACT!” if t.exact else ‘’
    print(f“{t.planet} {t.aspect} {t.natal_planet} natal ”
          f“(orb: {t.orb:.2f}°){exact}”)
```

## Period Analysis

```python
def analyze_period(start_date, end_date, step_days=1):
    """Analyze aspects over a period"""
    
    results = {
        “exact_aspects”: [],
        “sign_changes”: [],
        “retrogrades”: [],
        “statistics”: {}
    }
    
    # Scan the period
    current = start_date
    prev_signs = None
    prev_retros = None
    
    while current <= end_date:
        jday = ketu.utc_to_julian(current)
        
        # Current signs
        signs = [ketu.body_sign(ketu.long(jday, i))[0] 
                 for i in range(10)]
        
        # Retrogrades
        retros = [ketu.is_retrograde(jday, i) 
                  for i in range(10)]
        
        # Detect changes
        if prev_signs is not None:
            for i, (s1, s2) in enumerate(zip(prev_signs, signs)):
                if s1 != s2:
                    results[“sign_changes”].append({
                        “date”: current,
                        “planet”: ketu.body_name(i),
                        “old_sign”: ketu.signs[s1],
                        “new_sign”: ketu.signs[s2]
                    })
        
        if prev_retros is not None:
            for i, (r1, r2) in enumerate(zip(prev_retros, retros)):
                if r1 != r2:
                    results[“retrogradations”].append({
                        “date”: current,
                        “planet”: ketu.body_name(i),
                        “status”: ‘Retrograde’ if r2 else “Direct”
                    })
        
        # Exact aspects (orb < 0.5°)
        aspects = ketu.calculate_aspects(jday)
        for asp in aspects:
            if abs(asp[3]) < 0.5:
                results[“exact_aspects”].append({
                    “date”: current,
                    “aspect”: ketu.aspects[“name”][asp[2]].decode(),
                    “planet1”: ketu.body_name(asp[0]),
                    “planet2”: ketu.body_name(asp[1]),
                    “orb”: asp[3]
                })
        
        prev_signs = signs
        prev_retros = retros
        current += timedelta(days=days_per_month)
    
    return results

# Analyze the current month
start = datetime.now().replace(day=1, hour=0, minute=0)
end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

analysis = analyze_period(start, end)
print(f“Sign changes: {len(analysis[‘sign_changes’])}”)
print(f“Direction changes: {len(analysis[‘retrogradations’])}”)
print(f“Exact aspects: {len(analysis[‘exact_aspects’])}”)
```

## Advanced pattern matching for configurations

```python
from typing import Optional

def detect_configuration(jday) -> Optional[str]:
    """Detect special planetary configurations with pattern matching"""
    
    # Get all aspects
    aspects = ketu.calculate_aspects(jday)
    
    # Create an aspect graph
    connections = {}
    for asp in aspects:
        b1, b2, type_asp, orb = asp
        if abs(orb) < 5:  # Maximum orb 5°
            if b1 not in connections:
                connections[b1] = []
            if b2 not in connections:
                connections[b2] = []
            connections[b1].append((b2, type_asp))
            connections[b2].append((b1, type_asp))
    
    # Pattern matching on configurations
    match len(connections):
        case n if n >= 3:
            # Search for a Grand Trine
            for p1 in connections:
                for p2, asp1 in connections[p1]:
                    if asp1 == 4:  # Trine
                        for p3, asp2 in connections[p2]:
                            if asp2 == 4 and p3 != p1:
                                # Check the 3rd trine
                                for p, asp3 in connections[p3]:
                                    if p == p1 and asp3 == 4:
                                        return f“Grand Trine: {ketu.body_name(p1)}-{ketu.body_name(p2)}-{ketu.body_name(p3)}”
            
            # Look for a T-Square
            for p1 in connections:
                oppositions = [p for p, a in connections[p1] if a == 6]
                squares = [p for p, a in connections[p1] if a == 3]
                
                if oppositions and len(squares) >= 2:
                    return f“T-Square with apex {ketu.body_name(p1)}”
            
            # Search for a Yod
            for apex in connections:
                quinconces = [p for p, a in connections[apex] if a == 5]
                if len(quinconces) >= 2:
                    # Check the sextile at the base
                    p1, p2 = quinconces[0], quinconces[1]
                    for p, a in connections[p1]:
                        if p == p2 and a == 2:  # Sextile
                            return f“Yod with apex {ketu.body_name(apex)}”
        
        case _:
    return None

return None

# Test
jday = ketu.utc_to_julian(datetime.now())
config = detect_configuration(jday)
if config:
    print(f“Configuration detected: {config}”)
```

## Next steps

- Check out the [Concepts](concepts.md) to understand the theory
- Refer to the [API](api.md) for technical details
- Contribute to the project on [GitHub](https://github.com/alkimya/ketu)
