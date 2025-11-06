#!/usr/bin/env python3
"""
Exemple 1 : Calculs de positions planétaires de base

Montre comment :
- Convertir une date en jour julien
- Obtenir les positions des planètes (longitude, latitude, distance)
- Déterminer le signe zodiacal
"""

import ketu
from datetime import datetime
from zoneinfo import ZoneInfo


def main():
    print("=" * 60)
    print("EXEMPLE 1 : POSITIONS PLANÉTAIRES DE BASE")
    print("=" * 60)

    # Date et heure
    paris = ZoneInfo("Europe/Paris")
    dt = datetime(2020, 12, 21, 19, 20, tzinfo=paris)
    print(f"\nDate : {dt.strftime('%d/%m/%Y %H:%M %Z')}")

    # Convertir en jour julien
    jday = ketu.utc_to_julian(dt)
    print(f"Jour julien : {jday:.2f}")

    # Position du Soleil
    print("\n--- SOLEIL ---")
    sun_longitude = ketu.long(jday, 0)
    sun_latitude = ketu.lat(jday, 0)
    sun_distance = ketu.dist_au(jday, 0)

    print(f"Longitude : {sun_longitude:.4f}°")
    print(f"Latitude  : {sun_latitude:.4f}°")
    print(f"Distance  : {sun_distance:.6f} AU")

    # Déterminer le signe zodiacal
    sign_data = ketu.body_sign(sun_longitude)
    sign_index = sign_data[0]
    degrees = sign_data[1]
    minutes = sign_data[2]
    seconds = sign_data[3]

    print(f"Signe     : {ketu.signs[sign_index]} {degrees}°{minutes}'{seconds}\"")

    # Position de la Lune
    print("\n--- LUNE ---")
    moon_long = ketu.long(jday, 1)
    moon_sign = ketu.body_sign(moon_long)

    print(f"Longitude : {moon_long:.4f}°")
    print(f"Signe     : {ketu.signs[moon_sign[0]]} {moon_sign[1]}°{moon_sign[2]}'")

    # Vérifier la rétrogradation de Mercure
    print("\n--- MERCURE ---")
    mercury_long = ketu.long(jday, 2)
    mercury_sign = ketu.body_sign(mercury_long)

    if ketu.is_retrograde(jday, 2):
        print(f"Mercure est RÉTROGRADE en {ketu.signs[mercury_sign[0]]}")
    else:
        print(f"Mercure est DIRECT en {ketu.signs[mercury_sign[0]]}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
