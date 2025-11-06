#!/usr/bin/env python3
"""
Exemple 4 : Séries temporelles

Montre comment :
- Calculer les positions sur plusieurs jours
- Détecter les changements de signe
- Détecter les rétrogradations
- Tracer l'évolution des positions
"""

import ketu
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import numpy as np


def detect_sign_changes(start_date, num_days, body_id, timezone_str="UTC"):
    """Détecter les changements de signe pour un corps"""

    tz = ZoneInfo(timezone_str)
    print(f"\nChangements de signe pour {ketu.body_name(body_id)}")
    print("-" * 60)

    current_sign = None

    for day in range(num_days):
        dt = start_date + timedelta(days=day)
        jday = ketu.utc_to_julian(dt)

        longitude = ketu.long(jday, body_id)
        sign_data = ketu.body_sign(longitude)
        sign_index = sign_data[0]
        sign_name = ketu.signs[sign_index]

        # Détecter changement
        if current_sign is None:
            current_sign = sign_index
            print(f"{dt.strftime('%d/%m/%Y')} : Entrée en {sign_name}")
        elif sign_index != current_sign:
            print(f"{dt.strftime('%d/%m/%Y')} : Entrée en {sign_name}")
            current_sign = sign_index


def detect_retrogrades(start_date, num_days, body_id, timezone_str="UTC"):
    """Détecter les périodes de rétrogradation"""

    tz = ZoneInfo(timezone_str)
    print(f"\nPériodes de rétrogradation pour {ketu.body_name(body_id)}")
    print("-" * 60)

    was_retrograde = None
    retrograde_start = None

    for day in range(num_days):
        dt = start_date + timedelta(days=day)
        jday = ketu.utc_to_julian(dt)

        is_retro = ketu.is_retrograde(jday, body_id)

        if was_retrograde is None:
            was_retrograde = is_retro
            if is_retro:
                retrograde_start = dt
                print(f"{dt.strftime('%d/%m/%Y')} : ⬅ Début rétrogradation")

        elif is_retro and not was_retrograde:
            # Commence à rétrograder
            retrograde_start = dt
            print(f"{dt.strftime('%d/%m/%Y')} : ⬅ Début rétrogradation")
            was_retrograde = True

        elif not is_retro and was_retrograde:
            # Fin de rétrogradation
            duration = (dt - retrograde_start).days
            print(f"{dt.strftime('%d/%m/%Y')} : ➡ Fin rétrogradation (durée: {duration} jours)")
            was_retrograde = False


def track_positions(start_date, num_days, body_id):
    """Suivre l'évolution de la position"""

    print(f"\nÉvolution de la position de {ketu.body_name(body_id)}")
    print("-" * 60)

    positions = []
    dates = []

    for day in range(0, num_days, 7):  # Toutes les semaines
        dt = start_date + timedelta(days=day)
        jday = ketu.utc_to_julian(dt)
        longitude = ketu.long(jday, body_id)

        positions.append(longitude)
        dates.append(dt)

        sign_data = ketu.body_sign(longitude)
        sign_name = ketu.signs[sign_data[0]]
        retro = "℞" if ketu.is_retrograde(jday, body_id) else " "

        print(f"{dt.strftime('%d/%m/%Y')} : {longitude:7.2f}° ({sign_name:12}) {retro}")

    # Statistiques
    positions = np.array(positions)
    print(f"\nStatistiques sur {num_days} jours:")
    print(f"  Position min  : {positions.min():.2f}°")
    print(f"  Position max  : {positions.max():.2f}°")
    print(f"  Déplacement   : {positions.max() - positions.min():.2f}°")
    print(f"  Vitesse moy.  : {(positions[-1] - positions[0]) / num_days:.4f}°/jour")


def main():
    print("=" * 60)
    print("EXEMPLE 4 : SÉRIES TEMPORELLES")
    print("=" * 60)

    # Date de départ
    start = datetime(2024, 1, 1, 0, 0, tzinfo=ZoneInfo("UTC"))

    # Changements de signe du Soleil sur 1 an
    detect_sign_changes(start, 365, 0, "UTC")  # Soleil

    # Rétrogradations de Mercure sur 1 an
    detect_retrogrades(start, 365, 2, "UTC")  # Mercure

    # Évolution de Mars sur 90 jours
    track_positions(start, 90, 4)  # Mars

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
