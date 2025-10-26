# Guide de Release

Ce document explique comment publier une nouvelle version de Ketu sur PyPI et mettre à jour la documentation.

## Configuration initiale

### 1. Configuration PyPI

#### Créer un compte PyPI
1. Va sur https://pypi.org et crée un compte
2. Active l'authentification à deux facteurs (2FA)
3. Va dans Account settings > API tokens
4. Crée un token API avec le scope "Entire account" ou limité au projet "ketu"

#### Créer un compte Test PyPI (optionnel mais recommandé)
1. Va sur https://test.pypi.org et crée un compte
2. Répète les étapes pour créer un token API

#### Configurer les secrets GitHub
1. Va sur ton repo GitHub : https://github.com/alkimya/ketu
2. Settings > Secrets and variables > Actions
3. Ajoute ces secrets :
   - `PYPI_API_TOKEN` : ton token PyPI de production
   - `TEST_PYPI_API_TOKEN` : ton token Test PyPI (optionnel)

### 2. Configuration ReadTheDocs

1. Va sur https://readthedocs.org et connecte-toi avec ton compte GitHub
2. Importe ton projet : https://readthedocs.org/dashboard/import/
3. Sélectionne le repo `ketu`
4. ReadTheDocs détectera automatiquement `.readthedocs.yaml`
5. Active "Build pull requests" dans les paramètres avancés (optionnel)

La documentation sera disponible sur : https://ketu.readthedocs.io

## ⚠️ Important : Tag = Publication !

**Règle d'or** : Ne crée un tag que quand tu veux publier une version !

### Développement normal (PAS de publication)

```bash
# Travaille normalement sur main
git add .
git commit -m "Add new feature"
git push origin main

# ✅ Code poussé sur GitHub
# ✅ Tests CI s'exécutent
# ❌ RIEN n'est publié sur PyPI
# ❌ Pas de release
```

**Tant que tu ne crées pas de tag, rien n'est publié !**

### Publication (avec tag)

```bash
# Seulement quand tu es prêt à publier
./scripts/release.sh 0.3.0
git push origin main --tags

# ✅ Tag créé → déclenche publication PyPI
# ✅ Release GitHub créée
# ✅ Documentation mise à jour
```

---

## Faire une release

### Méthode 1 : Script automatique (recommandé)

```bash
# Test d'abord avec --dry-run (aucune modification)
./scripts/release.sh 0.3.0 --dry-run

# Release stable (va sur PyPI + crée Release GitHub)
./scripts/release.sh 0.3.0

# Release candidate (va sur Test PyPI + Pre-release GitHub)
./scripts/release.sh 0.3.0-rc1

# Release beta (va sur Test PyPI + Pre-release GitHub)
./scripts/release.sh 0.3.0-beta1
```

Le script va :
1. Vérifier que `gh` (GitHub CLI) est installé et authentifié
2. Mettre à jour les versions dans `pyproject.toml` et `ketu/__init__.py`
3. Mettre à jour `CHANGELOG.md` avec la date
4. Créer un commit de release
5. Créer un tag git `vX.Y.Z`
6. **Créer automatiquement une Release GitHub** avec les notes du CHANGELOG
7. Te demander confirmation

Ensuite, pousse les changements :
```bash
git push origin main
git push origin v0.3.0
```

**Note :** Le script crée automatiquement la **Release GitHub** ! Plus besoin de le faire manuellement.

### Méthode 2 : Manuelle

```bash
# 1. Mettre à jour la version
vim pyproject.toml  # Modifier version = "0.3.0"
vim ketu/__init__.py  # Modifier __version__ = "0.3.0"
vim CHANGELOG.md  # Ajouter la section de release

# 2. Commiter
git add pyproject.toml ketu/__init__.py CHANGELOG.md
git commit -m "Release v0.3.0"

# 3. Créer le tag
git tag -a v0.3.0 -m "Release v0.3.0"

# 4. Pousser
git push origin main
git push origin v0.3.0
```

## Ce qui se passe automatiquement

### 1. GitHub Actions (Publication PyPI)

Dès que tu pousses un tag `v*.*.*`, le workflow `.github/workflows/publish.yml` :

1. ✅ Lance les tests sur Python 3.9-3.13
2. 📦 Build le package (wheel + source distribution)
3. 🔍 Vérifie le package avec `twine check`
4. 📤 Publie sur :
   - **Test PyPI** si le tag contient `rc` ou `beta`
   - **PyPI** pour les versions stables

Tu peux suivre le workflow sur : https://github.com/alkimya/ketu/actions

### 2. ReadTheDocs (Documentation)

ReadTheDocs détecte automatiquement :
- Les nouveaux tags et crée une version de doc pour chaque tag
- Les commits sur `main` et met à jour la version `latest`

La documentation versionnée sera sur :
- https://ketu.readthedocs.io/en/latest/ (dernière version main)
- https://ketu.readthedocs.io/en/stable/ (dernière release stable)
- https://ketu.readthedocs.io/en/v0.3.0/ (version spécifique)

## Types de versions

### Version stable : `X.Y.Z`
```bash
./scripts/release.sh 0.3.0
```
- Va directement sur PyPI
- Installable avec `pip install ketu`
- Documentation sur `/en/stable/`

### Release Candidate : `X.Y.Z-rcN`
```bash
./scripts/release.sh 0.3.0-rc1
```
- Va sur Test PyPI
- Installable avec `pip install -i https://test.pypi.org/simple/ ketu`
- Permet de tester avant la version finale

### Beta : `X.Y.Z-betaN`
```bash
./scripts/release.sh 0.3.0-beta1
```
- Va sur Test PyPI
- Pour les testeurs early adopters

## Rollback / Annulation

### Avant de pousser
```bash
# Annuler le commit et le tag
git reset --hard HEAD~1
git tag -d v0.3.0
```

### Après avoir poussé
⚠️ **ATTENTION** : On ne peut PAS supprimer une version sur PyPI une fois publiée !

Tu peux seulement :
1. Publier une nouvelle version corrective (ex: 0.3.1)
2. Yank la version problématique sur PyPI (elle reste visible mais pip ne l'installera plus par défaut)

Pour yank une version :
```bash
# Via twine
twine upload --repository pypi --skip-existing dist/*
# Puis sur https://pypi.org/project/ketu/ > Manage > Options > Yank

# Ou via pip
pip install --upgrade pip
```

## Vérification post-release

### 1. Vérifier PyPI
- Package visible : https://pypi.org/project/ketu/
- Installation fonctionne : `pip install ketu==[version]`

### 2. Vérifier ReadTheDocs
- Doc visible : https://ketu.readthedocs.io
- Version listée dans le sélecteur de versions

### 3. Vérifier GitHub
- Tag créé : https://github.com/alkimya/ketu/tags
- Workflow réussi : https://github.com/alkimya/ketu/actions

## Checklist de release

- [ ] Tous les tests passent localement
- [ ] CHANGELOG.md est à jour
- [ ] Version bump dans pyproject.toml et __init__.py
- [ ] Commit et tag créés
- [ ] Push sur GitHub
- [ ] Workflow GitHub Actions réussi
- [ ] Package visible sur PyPI
- [ ] Documentation mise à jour sur ReadTheDocs
- [ ] Installation pip fonctionne
- [ ] Annonce sur GitHub Releases (optionnel)

## Dépannage

### Le workflow échoue avec "Invalid credentials"
→ Vérifie que `PYPI_API_TOKEN` est bien configuré dans GitHub Secrets

### ReadTheDocs ne build pas
→ Vérifie `.readthedocs.yaml` et les logs sur https://readthedocs.org/projects/ketu/builds/

### Le package ne s'installe pas
→ Vérifie que `pyproject.toml` est correct avec : `python -m build && twine check dist/*`

## Ressources

- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [ReadTheDocs Documentation](https://docs.readthedocs.io/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
