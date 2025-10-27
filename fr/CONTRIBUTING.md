# Guide de contribution

> Looking for the English guide? [Read CONTRIBUTING.md](../CONTRIBUTING.md)

Merci de ton intérêt pour contribuer à Ketu ! Voici comment tu peux aider.

## Démarrage rapide

### Configurer l'environnement de développement

1. Clone le repository :

```bash
git clone https://github.com/alkimya/ketu.git
cd ketu
```

2. Crée un environnement virtuel :

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Installe les dépendances en mode développement :

```bash
pip install -e .
pip install pytest pytest-cov
```

## Lancer les tests

Avant de soumettre une contribution, assure-toi que tous les tests passent :

```bash
pytest tests/ -v --cov=ketu
```

Pour lancer un fichier de test spécifique :

```bash
pytest tests/test_ketu.py -v
```

## Standards de code

- **Style** : Utilise PEP 8 pour le style Python
- **Docstrings** : Documente toutes les fonctions publiques
- **Type hints** : Ajoute des annotations de type quand possible
- **Tests** : Ajoute des tests pour toute nouvelle fonctionnalité

### Exemple de docstring

```python
def calculate_aspect(jdate, body1, body2):
    """Calculate the aspect between two celestial bodies.

    Args:
        jdate (float): Julian day number
        body1 (int): ID of the first body
        body2 (int): ID of the second body

    Returns:
        tuple: (body1, body2, aspect_index, orb) or None if no aspect
    """
    pass
```

## Workflow de contribution

1. **Fork** le projet
2. **Crée une branche** pour ta fonctionnalité (`git checkout -b feature/ma-feature`)
3. **Commit** tes changements (`git commit -m 'feat: implementation pure numpy`)
4. **Push** vers la branche (`git push origin feature/ma-feature`)
5. **Ouvre une Pull Request**

### Messages de commit

Utilise des messages clairs et descriptifs :

- `feat` : nouvelle fonctionnalité
- `fix` : correction d'un bug
- `docs` : mise à jour de la documentation
- `test` : tests uniquement
- `refactor` : modifications du code qui ne corrigent ni n'ajoutent de fonctionnalité
- `chore` : maintenance, outillage, code hors production

## Signaler un bug

Ouvre une issue sur GitHub avec :

- Une description claire du problème
- Les étapes pour reproduire le bug
- Le comportement attendu vs observé
- Ta version de Python et de Ketu
- Un exemple de code minimal si possible

## Proposer une fonctionnalité

Avant de travailler sur une grosse fonctionnalité :

1. Ouvre une issue pour en discuter
2. Attends les retours de la communauté
3. Une fois validée, commence le développement

## Documentation

Si tu ajoutes ou modifies des fonctionnalités :

1. Mets à jour la documentation dans `/docs/source/`
2. Ajoute des exemples d'utilisation
3. Mets à jour le [CHANGELOG.md](../CHANGELOG.md)

Pour générer la documentation localement :

```bash
cd docs
make livehtml  # Lance un serveur de documentation en live reload
```

## Checklist avant PR

- [ ] Les tests passent (`pytest tests/`)
- [ ] La couverture de code est maintenue ou améliorée
- [ ] Le code suit PEP 8
- [ ] Les docstrings sont à jour
- [ ] Le [CHANGELOG.md](../CHANGELOG.md) est à jour
- [ ] La documentation est mise à jour si nécessaire

## Ressources

- [Documentation du projet (Read the Docs)](https://ketu.readthedocs.io/)
- [Issues](https://github.com/alkimya/ketu/issues)
- [Discussions](https://github.com/alkimya/ketu/discussions)
- Contact : [loc.cosnier@pm.me](mailto:loc.cosnier@pm.me)

## Licence

En contribuant, vous acceptez que votre code soit publié sous licence MIT.
