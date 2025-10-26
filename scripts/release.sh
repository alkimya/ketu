#!/bin/bash
# Script de release automatique pour Ketu
# Usage: ./scripts/release.sh [version] [--dry-run]
# Exemple: ./scripts/release.sh 0.3.0
#          ./scripts/release.sh 0.3.0 --dry-run

set -e  # Arrête le script en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Mode dry-run
DRY_RUN=false
if [[ "$*" == *"--dry-run"* ]]; then
    DRY_RUN=true
    warning "MODE DRY-RUN : aucune modification ne sera effectuée"
fi

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

# Vérifier que gh (GitHub CLI) est installé
if ! command -v gh &> /dev/null; then
    error "GitHub CLI (gh) n'est pas installé. Installe-le avec : brew install gh (ou apt install gh)"
fi

# Vérifier qu'on est authentifié avec gh
if ! gh auth status &> /dev/null; then
    error "Tu n'es pas authentifié avec GitHub CLI. Lance : gh auth login"
fi

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
VERSION=""
for arg in "$@"; do
    if [[ ! "$arg" =~ ^-- ]]; then
        VERSION="$arg"
        break
    fi
done

if [ -z "$VERSION" ]; then
    # Lire la version depuis pyproject.toml
    CURRENT_VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
    info "Version actuelle: $CURRENT_VERSION"
    echo -n "Nouvelle version (format: X.Y.Z): "
    read VERSION
fi

# Valider le format de version
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-rc[0-9]+|-beta[0-9]+)?$ ]]; then
    error "Format de version invalide. Utilise X.Y.Z ou X.Y.Z-rc1 ou X.Y.Z-beta1"
fi

info "Création de la release v$VERSION..."

# Créer une copie de backup en dry-run
if [ "$DRY_RUN" = true ]; then
    cp pyproject.toml pyproject.toml.backup
    cp ketu/__init__.py ketu/__init__.py.backup
    cp CHANGELOG.md CHANGELOG.md.backup
fi

# Mettre à jour la version dans pyproject.toml
info "Mise à jour de pyproject.toml..."
if [ "$(uname)" = "Darwin" ]; then
    # macOS
    sed -i '' "s/^version = .*/version = \"$VERSION\"/" pyproject.toml
else
    # Linux
    sed -i "s/^version = .*/version = \"$VERSION\"/" pyproject.toml
fi

# Mettre à jour la version dans ketu/__init__.py
info "Mise à jour de ketu/__init__.py..."
if [ "$(uname)" = "Darwin" ]; then
    sed -i '' "s/^__version__ = .*/__version__ = \"$VERSION\"/" ketu/__init__.py
else
    sed -i "s/^__version__ = .*/__version__ = \"$VERSION\"/" ketu/__init__.py
fi

# Mettre à jour CHANGELOG.md
info "Mise à jour de CHANGELOG.md..."
TODAY=$(date +%Y-%m-%d)
if [ "$(uname)" = "Darwin" ]; then
    sed -i '' "s/## \[Unreleased\]/## [Unreleased]\n\n## [$VERSION] - $TODAY/" CHANGELOG.md
else
    sed -i "s/## \[Unreleased\]/## [Unreleased]\n\n## [$VERSION] - $TODAY/" CHANGELOG.md
fi

# Afficher les changements
info "Changements effectués:"
git diff pyproject.toml ketu/__init__.py CHANGELOG.md

# En mode dry-run, restaurer les fichiers
if [ "$DRY_RUN" = true ]; then
    warning "Mode dry-run : restauration des fichiers..."
    mv pyproject.toml.backup pyproject.toml
    mv ketu/__init__.py.backup ketu/__init__.py
    mv CHANGELOG.md.backup CHANGELOG.md
    success "Dry-run terminé ! Aucune modification effectuée."
    info "Pour faire la release réellement, relance sans --dry-run"
    exit 0
fi

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

# Extraire les notes de version du CHANGELOG
info "Extraction des notes de version depuis CHANGELOG.md..."
RELEASE_NOTES=$(awk "/## \[$VERSION\]/,/## \[/" CHANGELOG.md | sed '1d;$d' | sed '/^$/d')

# Si pas de notes trouvées, utiliser un message par défaut
if [ -z "$RELEASE_NOTES" ]; then
    RELEASE_NOTES="Version $VERSION

Voir [CHANGELOG.md](https://github.com/alkimya/ketu/blob/main/CHANGELOG.md) pour les détails."
fi

# Créer la release GitHub
info "Création de la release GitHub..."
if [[ "$VERSION" =~ (rc|beta) ]]; then
    # Release candidate ou beta = pre-release
    gh release create "v$VERSION" \
        --title "v$VERSION" \
        --notes "$RELEASE_NOTES" \
        --prerelease
    success "Pre-release GitHub créée (rc/beta)"
else
    # Release stable
    gh release create "v$VERSION" \
        --title "v$VERSION" \
        --notes "$RELEASE_NOTES"
    success "Release GitHub créée"
fi

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
echo "  3. Vérifie les URLs:"
echo "     - Release : ${BLUE}https://github.com/alkimya/ketu/releases/tag/v$VERSION${NC}"
echo "     - Actions : ${BLUE}https://github.com/alkimya/ketu/actions${NC}"
if [[ "$VERSION" =~ (rc|beta) ]]; then
    echo "     - TestPyPI : ${BLUE}https://test.pypi.org/project/ketu/$VERSION/${NC}"
else
    echo "     - PyPI : ${BLUE}https://pypi.org/project/ketu/$VERSION/${NC}"
fi
echo "     - Docs : ${BLUE}https://ketu.readthedocs.io/en/v$VERSION/${NC}"
echo ""
info "Pour annuler cette release (avant de push):"
echo "     git reset --hard HEAD~1"
echo "     git tag -d v$VERSION"
echo "     gh release delete v$VERSION"
