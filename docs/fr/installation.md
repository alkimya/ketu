# Installation

## Prérequis

Ketu nécessite :

- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)

## Installation stable depuis PyPI

La méthode la plus simple pour installer Ketu :

```bash
pip install ketu
```

## Installation depuis les sources

### Cloner le dépôt

```bash
git clone https://github.com/alkimya/ketu.git
cd ketu
```

### Installation en mode développement

```bash
pip install -e .
```

Cette méthode permet de modifier le code source et de voir immédiatement les changements.

## Installation dans un environnement virtuel (recommandé)

### Avec venv

```bash
# Créer l'environnement
python -m venv venv

# Installer Ketu
pip install ketu
```

## Vérification de l'installation

### En ligne de commande

```bash
# Lancer l'interface interactive
ketu
```

### En Python

```python
import ketu
print(ketu.__version__)
# Output: 0.2.0
```

## Dépendances

Ketu utilise les bibliothèques suivantes :

Bibliothèque    |   Version |   Description
----------------|-----------|--------------
numpy           |   ≥1.20.0 |   Calculs numériques et arrays
pyswisseph      |   ≥2.10.0 |   Éphémérides planétaires

## Désinstallation

```bash
pip uninstall ketu
```

## Prochaines étapes

Une fois installé, consultez le [Guide de démarrage rapide](quickstart.md) pour commencer à utiliser Ketu.
