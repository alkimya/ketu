"""Example: Export astronomical events to iCalendar format.

This example demonstrates how to export lunations, transits, and aspects
to .ics files that can be imported into calendar applications like:
- Google Calendar
- Apple Calendar
- Outlook
- Thunderbird
- etc.

Requirements: pip install icalendar
"""

import os
from ketu.icalendar_export import (
    export_lunations_to_ical,
    export_transits_to_ical,
    export_aspects_to_ical,
)


def example_1_lunar_calendar():
    """Example 1: Export complete lunar calendar for a year."""
    print("=" * 70)
    print("Example 1: Calendrier Lunaire 2024")
    print("=" * 70)

    filename = "calendrier_lunaire_2024.ics"

    export_lunations_to_ical(
        year=2024,
        filename=filename,
        include_new_moon=True,
        include_full_moon=True,
        include_quarters=False,  # Skip quarters for cleaner calendar
        event_duration_mode="exact",  # Point events at exact moment
        alert_before_minutes=60,  # Alert 1 hour before
    )

    print(f"\n✓ Fichier créé: {filename}")
    print("  Importez ce fichier dans votre application de calendrier")
    print()


def example_2_lunar_calendar_with_orbs():
    """Example 2: Lunar calendar with orb durations."""
    print("=" * 70)
    print("Example 2: Calendrier Lunaire avec Durées d'Orbe")
    print("=" * 70)

    filename = "calendrier_lunaire_2024_orbes.ics"

    export_lunations_to_ical(
        year=2024,
        filename=filename,
        include_new_moon=True,
        include_full_moon=True,
        include_quarters=True,  # Include all lunar phases
        event_duration_mode="orb",  # Events span entire orb duration
        alert_before_minutes=None,  # No alerts
    )

    print(f"\n✓ Fichier créé: {filename}")
    print("  Les événements durent toute la période d'orbe")
    print()


def example_3_personal_transits():
    """Example 3: Personal transits calendar."""
    print("=" * 70)
    print("Example 3: Transits Personnels 2024")
    print("=" * 70)

    filename = "mes_transits_2024.ics"

    # Example natal date (replace with your own!)
    natal_date = "1990-05-15 14:30"

    export_transits_to_ical(
        natal_date=natal_date,
        start_date="2024-01-01",
        end_date="2024-12-31",
        filename=filename,
        transiting_bodies=["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"],
        natal_bodies=["Sun", "Moon", "Mercury", "Venus", "Mars"],
        aspects_list=["Conjunction", "Square", "Trine", "Opposition"],
        event_duration_mode="exact",
        alert_before_minutes=1440,  # Alert 24 hours before
    )

    print(f"\n✓ Fichier créé: {filename}")
    print(f"  Transits des planètes lentes pour thème du {natal_date}")
    print()


def example_4_jupiter_saturn_aspects():
    """Example 4: Jupiter-Saturn aspects (social cycle)."""
    print("=" * 70)
    print("Example 4: Aspects Jupiter-Saturne (Cycle Social)")
    print("=" * 70)

    filename = "jupiter_saturn_2020_2030.ics"

    export_aspects_to_ical(
        body1="Jupiter",
        body2="Saturn",
        start_date="2020-01-01",
        end_date="2030-12-31",
        filename=filename,
        aspects_list=["Conjunction", "Sextile", "Square", "Trine", "Opposition"],
        event_duration_mode="orb",  # Long duration for slow planets
        alert_before_minutes=None,
    )

    print(f"\n✓ Fichier créé: {filename}")
    print("  Cycle complet Jupiter-Saturne sur 10 ans")
    print()


def example_5_venus_mars_aspects():
    """Example 5: Venus-Mars aspects (love cycle)."""
    print("=" * 70)
    print("Example 5: Aspects Vénus-Mars 2024 (Cycle Amoureux)")
    print("=" * 70)

    filename = "venus_mars_2024.ics"

    export_aspects_to_ical(
        body1="Venus",
        body2="Mars",
        start_date="2024-01-01",
        end_date="2024-12-31",
        filename=filename,
        aspects_list=["Conjunction", "Square", "Trine", "Opposition"],
        event_duration_mode="exact",
        alert_before_minutes=60,  # Alert 1 hour before
    )

    print(f"\n✓ Fichier créé: {filename}")
    print("  Aspects Vénus-Mars pour l'année")
    print()


def example_6_multiple_years_transits():
    """Example 6: Multi-year transits for long-term planning."""
    print("=" * 70)
    print("Example 6: Transits sur Plusieurs Années (2024-2030)")
    print("=" * 70)

    filename = "transits_longterme_2024_2030.ics"

    natal_date = "1990-05-15 14:30"

    export_transits_to_ical(
        natal_date=natal_date,
        start_date="2024-01-01",
        end_date="2030-12-31",
        filename=filename,
        transiting_bodies=["Saturn", "Uranus", "Neptune", "Pluto"],  # Very slow
        natal_bodies=["Sun", "Moon"],  # Just main points
        aspects_list=["Conjunction", "Square", "Opposition"],  # Major only
        event_duration_mode="orb",
        alert_before_minutes=10080,  # Alert 1 week before (7 days)
    )

    print(f"\n✓ Fichier créé: {filename}")
    print("  Transits majeurs des planètes très lentes sur 6 ans")
    print()


def show_import_instructions():
    """Show instructions for importing into calendar apps."""
    print("\n" + "=" * 70)
    print("INSTRUCTIONS D'IMPORTATION")
    print("=" * 70)
    print()
    print("📱 Google Calendar:")
    print("  1. Ouvrez Google Calendar")
    print("  2. Cliquez sur '⚙️ Paramètres' → 'Importer et exporter'")
    print("  3. Cliquez 'Sélectionner un fichier' et choisissez le .ics")
    print("  4. Sélectionnez le calendrier de destination")
    print("  5. Cliquez 'Importer'")
    print()
    print("🍎 Apple Calendar (macOS/iOS):")
    print("  1. Double-cliquez sur le fichier .ics")
    print("  2. Ou ouvrez Calendar → Fichier → Importer")
    print("  3. Choisissez le calendrier de destination")
    print()
    print("📧 Outlook:")
    print("  1. Ouvrez Outlook")
    print("  2. Fichier → Ouvrir et exporter → Importer/Exporter")
    print("  3. Sélectionnez 'Importer un fichier iCalendar (.ics)'")
    print("  4. Choisissez le fichier")
    print()
    print("🦊 Thunderbird:")
    print("  1. Ouvrez l'onglet Calendrier")
    print("  2. Fichier → Importer")
    print("  3. Sélectionnez le fichier .ics")
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "iCALENDAR EXPORT EXAMPLES" + " " * 28 + "║")
    print("╚" + "═" * 68 + "╝")

    # Run all examples
    example_1_lunar_calendar()
    example_2_lunar_calendar_with_orbs()
    example_3_personal_transits()
    example_4_jupiter_saturn_aspects()
    example_5_venus_mars_aspects()
    example_6_multiple_years_transits()

    # Show import instructions
    show_import_instructions()

    print("=" * 70)
    print("Examples completed successfully!")
    print("=" * 70)
    print()
    print("Les fichiers .ics ont été créés dans le répertoire courant.")
    print("Vous pouvez maintenant les importer dans votre calendrier préféré.")
    print()
