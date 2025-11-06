# Minimal makefile for Sphinx documentation
# Default build is French documentation

# You can set these variables from the command line.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = fr
BUILDDIR      = build

.PHONY: all
all: html en

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
	rm -rf build

livehtml:
	$(SPHINXBUILD) -b html en $(BUILDDIR)/html/en
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" \
		--port 8000 \
		--open-browser \
		--watch ../ketu \
		--watch en \
		--pre-build "$(SPHINXBUILD) -b html en $(BUILDDIR)/html/en"

# Build English documentation
.PHONY: en
en:
	$(SPHINXBUILD) -b html en $(BUILDDIR)/html/en $(SPHINXOPTS)

install:
	pip install -r requirements-docs.txt
