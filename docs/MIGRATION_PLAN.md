# Documentation Restructuring Plan

## Objective

Migrate from parallel EN/FR documentation to a single-source structure using sphinx-intl with PO file translations.

## Current Structure

```text
docs/
├── en/           # English docs (11 .md files + conf.py)
├── fr/           # French docs (11 .md files + conf.py)
├── Makefile      # Build system (default: FR)
└── requirements-docs.txt
```

## Target Structure

```text
docs/
├── source/       # Single source of truth (English)
│   ├── conf.py
│   ├── index.md
│   └── *.md      # All English content
├── locale/       # Translations
│   ├── fr/
│   │   └── LC_MESSAGES/
│   │       └── *.po
│   └── [future languages]/
├── build/        # Built documentation
│   ├── html/     # English (default)
│   └── html-fr/  # French translation
├── Makefile      # Updated build system
└── requirements-docs.txt  # Add sphinx-intl
```

## Migration Steps

### 1. Install sphinx-intl

Add to requirements-docs.txt:

- sphinx-intl>=2.1.0

### 2. Create new structure

- Move docs/en/ → docs/source/
- Update conf.py for i18n support
- Add gettext builder configuration

### 3. Extract translations

```bash
# Extract translatable strings to POT files
make gettext

# Initialize French locale
sphinx-intl update -p build/gettext -l fr
```

### 4. Migrate French translations

- Extract text from docs/fr/*.md
- Populate docs/locale/fr/LC_MESSAGES/*.po files
- Use automated tools where possible

### 5. Update build system

- Modify Makefile for multi-language builds
- Set English as default
- Add targets: html-fr, html-all

### 6. Test and validate

- Build English docs: `make html`
- Build French docs: `make html-fr`
- Test responsive design on mobile
- Verify all links work

### 7. Cleanup

- Archive docs/en/ and docs/fr/
- Update CI/CD if applicable
- Document translation workflow

## Benefits

✅ Single source of truth (English)
✅ Professional translation workflow (PO files)
✅ Easy to add more languages
✅ Better maintainability
✅ Industry-standard approach
✅ Responsive design already implemented

## Timeline

- Phase 1: Setup infrastructure (30 min)
- Phase 2: Extract and migrate translations (1-2 hours)
- Phase 3: Test and validate (30 min)
- Total: ~2-3 hours

## Responsive Design Status

✅ Already excellent! Current custom.css has:

- Mobile breakpoints (@media max-width: 768px)
- Portrait mode fixes (@media max-width: 480px + orientation: portrait)
- Proper sidebar behavior on mobile
- Responsive tables and typography
- No changes needed!
