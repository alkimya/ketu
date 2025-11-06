# Exemples avancés

## Phases de la Lune avec Pattern Matching

```python
import ketu
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def phase_lunaire(jday):
    """Déterminer la phase lunaire avec pattern matching (Python 3.10+)"""
    
    # Calculer l'angle Soleil-Lune
    sun_long = ketu.long(jday, 0)
    moon_long = ketu.long(jday, 1)
    
    # Élongation de la Lune par rapport au Soleil
    elongation = (moon_long - sun_long) % 360
    
    # Pattern matching sur l'élongation
    match elongation:
        case e if 0 <= e < 22.5:
            return "🌑 Nouvelle Lune", e, "Conjonction"
        case e if 22.5 <= e < 67.5:
            return "🌒 Premier Croissant", e, "Croissante"
        case e if 67.5 <= e < 112.5:
            return "🌓 Premier Quartier", e, "Carré croissant"
        case e if 112.5 <= e < 157.5:
            return "🌔 Lune Gibbeuse Croissante", e, "Gibbeuse"
        case e if 157.5 <= e < 202.5:
            return "🌕 Pleine Lune", e, "Opposition"
        case e if 202.5 <= e < 247.5:
            return "🌖 Lune Gibbeuse Décroissante", e, "Gibbeuse"
        case e if 247.5 <= e < 292.5:
            return "🌗 Dernier Quartier", e, "Carré décroissant"
        case e if 292.5 <= e < 337.5:
            return "🌘 Dernier Croissant", e, "Balsamique"
        case _:
            return "🌑 Nouvelle Lune", e, "Conjonction"

def calendrier_lunaire(annee, mois):
    """Générer un calendrier des phases lunaires pour un mois"""
    
    print(f"\n{'='*50}")
    print(f"CALENDRIER LUNAIRE - {mois:02d}/{annee}")
    print(f"{'='*50}\n")
    
    tz = ZoneInfo("UTC")
    
    # Pour chaque jour du mois
    for jour in range(1, 32):
        try:
            dt = datetime(annee, mois, jour, 12, 0, tzinfo=tz)
            jday = ketu.utc_to_julian(dt)
            
            phase, elongation, description = phase_lunaire(jday)
            
            # Afficher les phases principales
            if any(key in phase for key in ["Nouvelle", "Premier Quartier", 
                                            "Pleine", "Dernier Quartier"]):
                print(f"{jour:02d}/{mois:02d}: {phase} ({elongation:.1f}°)")
                
        except ValueError:
            break  # Fin du mois

# Exemple d'utilisation
calendrier_lunaire(2024, 1)
```

## Transits planétaires

```python
import ketu
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Tuple
from zoneinfo import ZoneInfo


@dataclass
class Transit:
    """Représente un transit planétaire"""
    planete: str
    aspect: str
    planete_natale: str
    date: datetime
    orbe: float
    exact: bool = False

def chercher_transits(date_natale, date_transit, planetes_a_suivre=None):
    """Chercher les transits du jour sur un thème natal"""
    
    if planetes_a_suivre is None:
        planetes_a_suivre = [0, 1, 2, 3, 4, 5, 6]  # Soleil à Saturne
    
    # Positions natales
    jday_natal = ketu.utc_to_julian(date_natale)
    positions_natales = {}
    for i in planetes_a_suivre:
        positions_natales[i] = ketu.long(jday_natal, i)
    
    # Positions en transit
    jday_transit = ketu.utc_to_julian(date_transit)
    transits = []
    
    for i_transit in planetes_a_suivre:
        pos_transit = ketu.long(jday_transit, i_transit)
        
        for i_natal, pos_natal in positions_natales.items():
            # Calculer l'aspect
            diff = abs(pos_transit - pos_natal) % 360
            if diff > 180:
                diff = 360 - diff
            
            # Vérifier chaque type d'aspect
            for j, angle in enumerate(ketu.aspects["value"]):
                orbe_max = ketu.get_orb(i_transit, i_natal, j)
                orbe = abs(diff - angle)
                
                if orbe <= orbe_max:
                    transit = Transit(
                        planete=ketu.body_name(i_transit),
                        aspect=ketu.aspects["name"][j].decode(),
                        planete_natale=ketu.body_name(i_natal),
                        date=date_transit,
                        orbe=orbe,
                        exact=(orbe < 1.0)
                    )
                    transits.append(transit)
    
    return transits

# Exemple
natal = datetime(1990, 5, 15, 14, 30, tzinfo=ZoneInfo("Europe/Paris"))
transit = datetime.now(ZoneInfo("Europe/Paris"))

transits = chercher_transits(natal, transit)
for t in transits:
    exact = " EXACT!" if t.exact else ""
    print(f"{t.planete} {t.aspect} {t.planete_natale} natal "
          f"(orbe: {t.orbe:.2f}°){exact}")
```

## Analyse de période

```python
def analyser_periode(date_debut, date_fin, pas_jours=1):
    """Analyser les aspects sur une période"""
    
    resultats = {
        "aspects_exacts": [],
        "changements_signe": [],
        "retrogradations": [],
        "statistiques": {}
    }
    
    # Parcourir la période
    current = date_debut
    prev_signs = None
    prev_retros = None
    
    while current <= date_fin:
        jday = ketu.utc_to_julian(current)
        
        # Signes actuels
        signs = [ketu.body_sign(ketu.long(jday, i))[0] 
                 for i in range(10)]
        
        # Rétrogradations
        retros = [ketu.is_retrograde(jday, i) 
                  for i in range(10)]
        
        # Détecter les changements
        if prev_signs is not None:
            for i, (s1, s2) in enumerate(zip(prev_signs, signs)):
                if s1 != s2:
                    resultats["changements_signe"].append({
                        "date": current,
                        "planete": ketu.body_name(i),
                        "ancien_signe": ketu.signs[s1],
                        "nouveau_signe": ketu.signs[s2]
                    })
        
        if prev_retros is not None:
            for i, (r1, r2) in enumerate(zip(prev_retros, retros)):
                if r1 != r2:
                    resultats["retrogradations"].append({
                        "date": current,
                        "planete": ketu.body_name(i),
                        "statut": "Rétrograde" if r2 else "Direct"
                    })
        
        # Aspects exacts (orbe < 0.5°)
        aspects = ketu.calculate_aspects(jday)
        for asp in aspects:
            if abs(asp[3]) < 0.5:
                resultats["aspects_exacts"].append({
                    "date": current,
                    "aspect": ketu.aspects["name"][asp[2]].decode(),
                    "planete1": ketu.body_name(asp[0]),
                    "planete2": ketu.body_name(asp[1]),
                    "orbe": asp[3]
                })
        
        prev_signs = signs
        prev_retros = retros
        current += timedelta(days=pas_jours)
    
    return resultats

# Analyser le mois en cours
debut = datetime.now().replace(day=1, hour=0, minute=0)
fin = (debut + timedelta(days=32)).replace(day=1) - timedelta(days=1)

analyse = analyser_periode(debut, fin)
print(f"Changements de signe: {len(analyse['changements_signe'])}")
print(f"Changements de direction: {len(analyse['retrogradations'])}")
print(f"Aspects exacts: {len(analyse['aspects_exacts'])}")
```

## Pattern matching avancé pour les configurations

```python
from typing import Optional

def detecter_configuration(jday) -> Optional[str]:
    """Détecter les configurations planétaires spéciales avec pattern matching"""
    
    # Obtenir tous les aspects
    aspects = ketu.calculate_aspects(jday)
    
    # Créer un graphe des aspects
    connexions = {}
    for asp in aspects:
        b1, b2, type_asp, orbe = asp
        if abs(orbe) < 5:  # Orbe maximum 5°
            if b1 not in connexions:
                connexions[b1] = []
            if b2 not in connexions:
                connexions[b2] = []
            connexions[b1].append((b2, type_asp))
            connexions[b2].append((b1, type_asp))
    
    # Pattern matching sur les configurations
    match len(connexions):
        case n if n >= 3:
            # Chercher un Grand Trigone
            for p1 in connexions:
                for p2, asp1 in connexions[p1]:
                    if asp1 == 4:  # Trigone
                        for p3, asp2 in connexions[p2]:
                            if asp2 == 4 and p3 != p1:
                                # Vérifier le 3e trigone
                                for p, asp3 in connexions[p3]:
                                    if p == p1 and asp3 == 4:
                                        return f"Grand Trigone: {ketu.body_name(p1)}-{ketu.body_name(p2)}-{ketu.body_name(p3)}"
            
            # Chercher un T-Carré
            for p1 in connexions:
                oppositions = [p for p, a in connexions[p1] if a == 6]
                carres = [p for p, a in connexions[p1] if a == 3]
                
                if oppositions and len(carres) >= 2:
                    return f"T-Carré avec apex {ketu.body_name(p1)}"
            
            # Chercher un Yod
            for apex in connexions:
                quinconces = [p for p, a in connexions[apex] if a == 5]
                if len(quinconces) >= 2:
                    # Vérifier le sextile à la base
                    p1, p2 = quinconces[0], quinconces[1]
                    for p, a in connexions[p1]:
                        if p == p2 and a == 2:  # Sextile
                            return f"Yod avec apex {ketu.body_name(apex)}"
        
        case _:
            return None
    
    return None

# Test
jday = ketu.utc_to_julian(datetime.now())
config = detecter_configuration(jday)
if config:
    print(f"Configuration détectée: {config}")
```

## Prochaines étapes

- Consultez les [Concepts](concepts.md) pour comprendre la théorie
- Référez-vous à l'[API](api.md) pour les détails techniques
- Contribuez au projet sur [GitHub](https://github.com/alkimya/ketu)
