# Guide de contribution

Merci de ton intérêt pour contribuer à Ketu ! Voici comment tu peux aider.

## 🚀 Démarrage rapide

### Configurer l'environnement de développement

1. Clone le repository :

```bash
git clone https://github.com/alkimya/ketu.git
cd ketu
```

2. Crée un environnement virtuel :

```bash
python3 -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
```

3. Installe les dépendances en mode développement :

```bash
pip install -e .
pip install pytest pytest-cov
```

## 🧪 Lancer les tests

Avant de soumettre une contribution, assure-toi que tous les tests passent :

```bash
pytest tests/ -v --cov=ketu
```

Pour lancer un fichier de test spécifique :

```bash
pytest tests/test_ketu.py -v
```

## 📝 Standards de code

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

## 🔄 Workflow de contribution

1. **Fork** le projet
2. **Crée une branche** pour ta fonctionnalité (`git checkout -b feature/ma-feature`)
3. **Commit** tes changements (`git commit -m 'Ajoute une super fonctionnalité'`)
4. **Push** vers la branche (`git push origin feature/ma-feature`)
5. **Ouvre une Pull Request**

### Messages de commit

Utilise des messages clairs et descriptifs :

- ✅ `Ajoute calcul des aspects mineurs`
- ✅ `Corrige bug dans le calcul de rétrogradation`
- ✅ `Améliore performance du cache LRU`
- ❌ `update`
- ❌ `fix bug`

## 🐛 Signaler un bug

Ouvre une issue sur GitHub avec :

- Une description claire du problème
- Les étapes pour reproduire le bug
- Le comportement attendu vs observé
- Ta version de Python et de Ketu
- Un exemple de code minimal si possible

## 💡 Proposer une fonctionnalité

Avant de travailler sur une grosse fonctionnalité :

1. Ouvre une issue pour en discuter
2. Attends les retours de la communauté
3. Une fois validée, commence le développement

## 📚 Documentation

Si tu ajoutes ou modifies des fonctionnalités :

1. Mets à jour la documentation dans `/docs/source/`
2. Ajoute des exemples d'utilisation
3. Mets à jour le CHANGELOG.md

Pour générer la documentation localement :

```bash
cd docs
make livehtml  # Lance un serveur de documentation en live reload
```

## ✅ Checklist avant PR

- [ ] Les tests passent (`pytest tests/`)
- [ ] La couverture de code est maintenue ou améliorée
- [ ] Le code suit PEP 8
- [ ] Les docstrings sont à jour
- [ ] Le CHANGELOG.md est mis à jour
- [ ] La documentation est mise à jour si nécessaire

## 🙏 Merci !

Toute contribution, grande ou petite, est appréciée. Que ce soit :

- Corriger une faute de frappe dans la doc
- Ajouter des tests
- Améliorer les performances
- Proposer de nouvelles fonctionnalités

Merci de faire partie de la communauté Ketu !
