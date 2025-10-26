#!/bin/bash
# Script de release automatique pour Ketu
# Usage: ./scripts/release.sh [version]
# Exemple: ./scripts/release.sh 0.3.0

set -e  # Arrête le script en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher un message coloré
info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

# Vérifier qu'on est sur la branche main
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    error "Tu dois être sur la branche 'main' pour faire une release (branche actuelle: $CURRENT_BRANCH)"
fi

# Vérifier qu'il n'y a pas de modifications non commitées
if ! git diff-index --quiet HEAD --; then
    error "Il y a des modifications non commitées. Commite ou stash tes changements d'abord."
fi

# Récupérer la version
if [ -z "$1" ]; then
    # Lire la version depuis pyproject.toml
    CURRENT_VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
    info "Version actuelle: $CURRENT_VERSION"
    echo -n "Nouvelle version (format: X.Y.Z): "
    read VERSION
else
    VERSION=$1
fi

# Valider le format de version
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-rc[0-9]+|-beta[0-9]+)?$ ]]; then
    error "Format de version invalide. Utilise X.Y.Z ou X.Y.Z-rc1 ou X.Y.Z-beta1"
fi

info "Création de la release v$VERSION..."

# Mettre à jour la version dans pyproject.toml
info "Mise à jour de pyproject.toml..."
sed -i "s/^version = .*/version = \"$VERSION\"/" pyproject.toml

# Mettre à jour la version dans ketu/__init__.py
info "Mise à jour de ketu/__init__.py..."
sed -i "s/^__version__ = .*/__version__ = \"$VERSION\"/" ketu/__init__.py

# Mettre à jour CHANGELOG.md
info "Mise à jour de CHANGELOG.md..."
TODAY=$(date +%Y-%m-%d)
sed -i "s/## \[Unreleased\]/## [Unreleased]\n\n## [$VERSION] - $TODAY/" CHANGELOG.md

# Afficher les changements
info "Changements effectués:"
git diff pyproject.toml ketu/__init__.py CHANGELOG.md

echo ""
warning "Vérifie les changements ci-dessus. Continuer ? (y/N)"
read -r CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    error "Release annulée."
fi

# Commiter les changements
info "Création du commit de release..."
git add pyproject.toml ketu/__init__.py CHANGELOG.md
git commit -m "Release v$VERSION

🚀 Version $VERSION

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

success "Commit créé"

# Créer le tag
info "Création du tag v$VERSION..."
git tag -a "v$VERSION" -m "Release v$VERSION"
success "Tag créé"

# Afficher les instructions finales
echo ""
success "Release v$VERSION prête !"
echo ""
info "Prochaines étapes:"
echo "  1. Pousse les changements:"
echo "     ${GREEN}git push origin main${NC}"
echo "     ${GREEN}git push origin v$VERSION${NC}"
echo ""
echo "  2. Le workflow GitHub Actions va automatiquement:"
if [[ "$VERSION" =~ (rc|beta) ]]; then
    echo "     - Publier sur ${YELLOW}TestPyPI${NC} (version $VERSION contient rc/beta)"
else
    echo "     - Publier sur ${GREEN}PyPI${NC} (version stable)"
fi
echo "     - ReadTheDocs va se mettre à jour automatiquement"
echo ""
info "Pour annuler cette release (avant de push):"
echo "     git reset --hard HEAD~1"
echo "     git tag -d v$VERSION"
