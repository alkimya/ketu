"""Configuration file for the Sphinx documentation builder."""

import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath("../.."))

# Project information
project = "Ketu"
copyright = f"{datetime.now().year}, Loc Cosnier"
author = "Loc Cosnier"
release = "1.5.0"
version = "1.5.0"

# Language and internationalization
language = "en"
locale_dirs = ["../locale/"]
gettext_compact = False
gettext_uuid = False

# General configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
    "sphinx_copybutton",
    "myst_parser",
]

# MyST configuration
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

# Templates path
templates_path = ["_templates"]

# Exclude patterns
exclude_patterns = []

# HTML output options
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_logo = None
html_favicon = None

# Theme options
html_theme_options = {
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

# Context for templates (language badges)
# Language will be dynamically set by sphinx-intl
on_rtd = os.environ.get("READTHEDOCS") == "True"
rtd_version = os.environ.get("READTHEDOCS_VERSION", "latest")

# Get current language from environment or default to 'en'
current_language = language if language else "en"

# Define available languages
available_languages = [
    {"code": "en", "label": "EN"},
    {"code": "fr", "label": "FR"},
]

# Build language links
language_links = []
for lang in available_languages:
    is_current = lang["code"] == current_language

    if on_rtd:
        url = f"/{lang['code']}/{rtd_version}/"
    else:
        if lang["code"] == "en":
            url = "../html/index.html"
        else:
            url = f"../html-{lang['code']}/index.html"

    language_links.append({
        "code": lang["code"],
        "label": lang["label"],
        "url": url,
        "current": is_current
    })

html_context = {
    "languages": language_links,
}

# Autodoc configuration
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "show-inheritance": True,
}

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}

# Source suffix
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
