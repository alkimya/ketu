# Makefile for Sphinx documentation with internationalization
# Default language is English

# You can set these variables from the command line.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SPHINXINTL    ?= sphinx-intl
SOURCEDIR     = source
BUILDDIR      = build
LOCALEDIR     = locale

.PHONY: all
all: html

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Custom targets
.PHONY: clean livehtml install

clean:
	rm -rf $(BUILDDIR)

# Install documentation dependencies
install:
	pip install -r requirements-docs.txt

# Live HTML with auto-reload (English only)
livehtml:
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" \
		--port 8000 \
		--open-browser \
		--watch ../ketu

# Internationalization targets
.PHONY: gettext update-pot update-po build-mo html-fr html-all

# Extract translatable strings to POT files
gettext:
	@echo "Extracting translatable strings to POT files..."
	@$(SPHINXBUILD) -b gettext "$(SOURCEDIR)" "$(BUILDDIR)/gettext"
	@echo "POT files created in $(BUILDDIR)/gettext/"

# Update POT files (alias for gettext)
update-pot: gettext

# Update PO files for all languages
update-po: gettext
	@echo "Updating PO files for all languages..."
	@$(SPHINXINTL) update -p "$(BUILDDIR)/gettext" -l fr
	@echo "PO files updated in $(LOCALEDIR)/"

# Initialize PO files for a new language
# Usage: make init-po LANG=es
init-po: gettext
	@if [ -z "$(LANG)" ]; then \
		echo "Error: LANG variable not set. Usage: make init-po LANG=es"; \
		exit 1; \
	fi
	@echo "Initializing PO files for language: $(LANG)"
	@$(SPHINXINTL) update -p "$(BUILDDIR)/gettext" -l $(LANG)
	@echo "PO files created in $(LOCALEDIR)/$(LANG)/"

# Build translated documentation for French
html-fr: build-mo
	@echo "Building French documentation..."
	@$(SPHINXBUILD) -b html -D language=fr "$(SOURCEDIR)" "$(BUILDDIR)/html-fr" $(SPHINXOPTS)
	@echo "French documentation built in $(BUILDDIR)/html-fr/"

# Build all language versions
html-all: html html-fr
	@echo "All language versions built successfully!"

# Build MO files from PO files (internal target)
build-mo:
	@if [ -d "$(LOCALEDIR)" ]; then \
		echo "Building MO files from PO files..."; \
		$(SPHINXINTL) build -d "$(LOCALEDIR)"; \
	fi

# Build HTML with translation support
html: build-mo
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)

# Translation workflow helper
.PHONY: i18n-help
i18n-help:
	@echo "Translation Workflow Commands:"
	@echo ""
	@echo "  make gettext        - Extract translatable strings to POT files"
	@echo "  make update-po      - Update PO files for all languages"
	@echo "  make init-po LANG=xx - Initialize PO files for a new language (e.g., LANG=es)"
	@echo ""
	@echo "  make html           - Build English documentation"
	@echo "  make html-fr        - Build French documentation"
	@echo "  make html-all       - Build all language versions"
	@echo ""
	@echo "  make livehtml       - Live preview with auto-reload (English)"
	@echo ""
	@echo "Translation Files:"
	@echo "  POT files (templates): $(BUILDDIR)/gettext/"
	@echo "  PO files (translations): $(LOCALEDIR)/[lang]/LC_MESSAGES/"
	@echo "  MO files (compiled): $(LOCALEDIR)/[lang]/LC_MESSAGES/ (auto-generated)"
	@echo ""
	@echo "Example Workflow:"
	@echo "  1. Edit source/*.md files (English)"
	@echo "  2. make gettext          # Extract new strings"
	@echo "  3. make update-po        # Update PO files"
	@echo "  4. Edit locale/fr/LC_MESSAGES/*.po files"
	@echo "  5. make html-all         # Build all versions"
	@echo ""
