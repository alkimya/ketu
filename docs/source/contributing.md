# Contribuer à Ketu

Nous accueillons avec plaisir les contributions ! 🌟

## Comment contribuer

### 1. Forker le projet

```bash
# Forker sur GitHub puis cloner
git clone https://github.com/VOTRE-USERNAME/ketu.git
cd ketu
```

### 2. Créer un environnement de développement

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer en mode développement
pip install -e ".[dev]"
```

### 3. Créer une branche

```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
```

### 4. Développer et tester

```bash
# Lancer les tests
pytest tests/

# Vérifier le style
flake8 ketu/

# Formatter le code
black ketu/
```

### 5. Commiter avec un message clair

```bash
git add .
git commit -m "feat: ajout du calcul des maisons astrologiques"
```

Format des messages de commit :

- `feat:` Nouvelle fonctionnalité
- `fix:` Correction de bug
- `docs:` Documentation
- `style:` Formatage, style
- `refactor:` Refactoring
- `test:` Ajout de tests
- `chore:` Maintenance

### 6. Pusher et créer une Pull Request

```bash
git push origin feature/ma-nouvelle-fonctionnalite
```

Puis créer une PR sur GitHub.

## Directives de développement

### Style de code

- PEP 8 pour le style Python
- Docstrings Google style
- Type hints quand pertinent
- Maximum 88 caractères par ligne (Black)

### Tests

- Couverture minimale : 80%
- Tests unitaires avec pytest
- Mocks pour les appels Swiss Ephemeris

### Documentation

- Toute nouvelle fonction doit être documentée
- Exemples dans les docstrings
- Mise à jour de la doc Sphinx si nécessaire

## Domaines de contribution

### 🎯 Priorités actuelles

1. **Migration pure numpy** : Remplacer pyswisseph
2. **Calculs d'aspects exacts** : Trouver les moments précis
3. **API étendue** : Maisons, parts arabes, etc.
4. **Interface graphique** : GUI avec Tkinter ou web

### 💡 Idées bienvenues

- Optimisations de performance
- Nouveaux types d'aspects
- Systèmes de maisons
- Exports (PDF, images)
- Intégrations (API REST, Discord bot)

## Architecture du projet

```
ketu/
├── ketu/
│   ├── __init__.py      # Exports publics
│   ├── ketu.py          # Module principal
│   ├── ephemeris.py     # (futur) Calculs pure numpy
│   ├── aspects.py       # (futur) Module aspects
│   └── utils.py         # (futur) Utilitaires
├── tests/
│   ├── test_ketu.py
│   ├── test_ephemeris.py
│   └── fixtures/
├── docs/
│   └── source/
└── examples/
```

## Processus de review

- Tests : Tous les tests doivent passer
- Coverage : Ne pas diminuer la couverture
- Documentation : À jour et claire
- Style : Respect des conventions
- Performance : Pas de régression

## Ressources

### Documentation technique

- [Swiss Ephemeris](https://www.astro.com/swisseph/)
- [VSOP87](https://en.wikipedia.org/wiki/VSOP_model)
- [JPL Horizons](https://ssd.jpl.nasa.gov/horizons/)

### Livres de référence

- *Astronomical Algorithms* - Jean Meeus
- *Fundamentals of Astrodynamics* - Bate, Mueller, White

### Communauté

- [Discussions GitHub](https://github.com/alkimya/ketu/discussions)
- [Issues](https://github.com/alkimya/ketu/issues)
- Email : [loc.cosnier@pm.me](mailto:loc.cosnier@pm.me)

## Licence

En contribuant, vous acceptez que vos contributions soient sous licence MIT.

## Code de conduite

- Bienveillance et respect
- Critiques constructives
- Focus sur les solutions
- Ouverture à l'apprentissage

Merci de contribuer à Ketu ! 🙏
