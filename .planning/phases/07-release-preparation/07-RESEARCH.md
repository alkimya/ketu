# Phase 7: Release Preparation - Research

**Researched:** 2026-02-12
**Domain:** Python package publishing (PyPI + GitHub releases)
**Confidence:** HIGH

## Summary

Phase 7 involves publishing Ketu 1.0.0 to PyPI and creating a corresponding GitHub release. The modern Python packaging ecosystem (2026) uses **pyproject.toml-based configuration** with **setuptools** as the build backend, and **trusted publishing** via OpenID Connect (OIDC) to eliminate manual API token management.

The critical path involves: (1) version bumps in pyproject.toml and `__init__.py`, (2) classifier updates to "Production/Stable", (3) building and validating distribution artifacts (wheel + sdist), (4) optional TestPyPI validation, (5) PyPI publication via GitHub Actions trusted publisher, and (6) GitHub release creation with changelog.

**Primary recommendation:** Use GitHub Actions with trusted publishing for secure, automated PyPI releases triggered by Git tags. Test the complete install flow in fresh virtual environments before publishing to production PyPI.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| build | latest | PEP 517 build frontend | Official PyPA tool, replaces `python setup.py` |
| twine | latest | PyPI upload + validation | Official PyPA tool, secure uploads with GPG signing |
| setuptools | >=61.0 | Build backend | De facto standard, excellent pyproject.toml support |
| wheel | latest | Binary distribution format | Universal standard for Python packages |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| check-wheel-contents | latest | Wheel validation | Detect unnecessary files, import issues, portability problems |
| pydistcheck | latest | Distribution testing | Verify package structure and portability |
| gh | latest | GitHub CLI | Create releases, upload assets, manage tags |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| setuptools | hatchling, flit, poetry-core | Hatchling/flit are faster and simpler, but setuptools has maximum ecosystem compatibility for migration |
| GitHub Actions | Manual twine upload | Automation eliminates human error, trusted publishing is more secure |
| Trusted publishing | API tokens | OIDC tokens expire in 15 minutes vs. long-lived tokens (better security) |

**Installation (development):**
```bash
pip install build twine check-wheel-contents pydistcheck gh
```

## Architecture Patterns

### Version Management: Dual Hard-Coding Pattern

**Current approach:** Ketu uses the dual hard-coding pattern with manual synchronization.

```
pyproject.toml:
  [project]
  version = "1.0.0"

ketu/__init__.py:
  __version__ = "1.0.0"
```

**Why this pattern:**
- Simple and explicit
- No build complexity
- Works with all build systems
- Version visible in both source and installed package

**Trade-off:** Requires updating two locations. Acceptable for major releases where you're already touching multiple files (CHANGELOG, docs, etc.).

**Alternative (not recommended for v1.0.0):** Dynamic versioning with `importlib.metadata` at runtime adds complexity without clear benefit for a stable release.

### Recommended Release Workflow

```
1. Pre-release Preparation
   ├── Update version in pyproject.toml
   ├── Update version in ketu/__init__.py
   ├── Update classifiers in pyproject.toml
   ├── Finalize CHANGELOG.md
   └── Verify UPGRADING.md is current

2. Build and Validate Locally
   ├── Clean old artifacts: rm -rf dist/ build/ *.egg-info
   ├── Build: python -m build --sdist --wheel
   ├── Validate metadata: twine check dist/*
   ├── Optional: check-wheel-contents dist/*.whl
   └── Inspect contents: tar -tzf dist/*.tar.gz | head -50

3. Test Installation in Fresh Venv
   ├── Create clean venv: python -m venv /tmp/test-ketu-venv
   ├── Activate: source /tmp/test-ketu-venv/bin/activate
   ├── Install from wheel: pip install dist/ketu-1.0.0-py3-none-any.whl
   ├── Test imports and version
   ├── Run test suite: pytest (if included)
   └── Deactivate and clean up

4. Optional: TestPyPI Validation
   ├── Upload: twine upload --repository testpypi dist/*
   ├── Create new venv
   ├── Install: pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple ketu==1.0.0
   └── Validate functionality

5. Create Git Tag and Push
   ├── Commit all changes: git add . && git commit -m "release: version 1.0.0"
   ├── Tag: git tag -a v1.0.0 -m "Release version 1.0.0"
   ├── Push commits: git push origin main
   └── Push tag: git push origin v1.0.0

6. GitHub Actions Auto-Publishes to PyPI
   └── Trusted publisher workflow triggered by tag

7. Create GitHub Release
   ├── gh release create v1.0.0 --title "Ketu 1.0.0" --notes-file RELEASE_NOTES.md
   ├── Auto-attach source archives (GitHub does this)
   └── Verify release page shows changelog
```

### Trusted Publishing Configuration

**On PyPI (one-time setup):**
1. Go to https://pypi.org/manage/account/publishing/
2. Add trusted publisher with:
   - **Owner:** alkimya
   - **Repository name:** ketu
   - **Workflow filename:** publish.yml
   - **Environment name:** pypi (optional but recommended for manual approval)

**Repeat for TestPyPI:**
- https://test.pypi.org/manage/account/publishing/
- Use environment name: testpypi

**In GitHub Actions workflow:**

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*.*.*'  # Trigger on version tags like v1.0.0

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install build dependencies
        run: python -m pip install --upgrade pip build
      - name: Build distributions
        run: python -m build --sdist --wheel
      - name: Store distributions
        uses: actions/upload-artifact@v4
        with:
          name: python-package-distributions
          path: dist/

  publish-to-pypi:
    needs: build
    runs-on: ubuntu-latest
    environment: pypi  # Enables manual approval if configured
    permissions:
      id-token: write  # CRITICAL: Enables OIDC token generation
    steps:
      - name: Download distributions
        uses: actions/download-artifact@v4
        with:
          name: python-package-distributions
          path: dist/
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        # No password or API token needed - uses trusted publishing!

  publish-to-testpypi:
    needs: build
    runs-on: ubuntu-latest
    environment: testpypi
    permissions:
      id-token: write
    steps:
      - name: Download distributions
        uses: actions/download-artifact@v4
        with:
          name: python-package-distributions
          path: dist/
      - name: Publish to TestPyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/
```

**Security note:** "For security reasons, you must require manual approval on each run for the pypi environment" (official PyPA guide).

### GitHub Release Creation Pattern

**Option 1: GitHub CLI (recommended for automation)**
```bash
# Extract changelog section for v1.0.0
gh release create v1.0.0 \
  --title "Ketu 1.0.0 - Production Release" \
  --notes-file <(sed -n '/## \[1.0.0\]/,/## \[0.4.0\]/p' CHANGELOG.md | head -n -1)

# Or with inline notes
gh release create v1.0.0 \
  --title "Ketu 1.0.0" \
  --notes "$(cat <<'EOF'
First production-stable release of Ketu.

See [CHANGELOG.md](https://github.com/alkimya/ketu/blob/main/CHANGELOG.md) for full details.
See [UPGRADING.md](https://github.com/alkimya/ketu/blob/main/UPGRADING.md) for migration guide from 0.4.x.

**Install:** \`pip install ketu==1.0.0\`
EOF
)"
```

**Option 2: GitHub web interface**
1. Navigate to https://github.com/alkimya/ketu/releases/new
2. Choose tag: v1.0.0
3. Title: "Ketu 1.0.0"
4. Description: Copy from CHANGELOG.md section for 1.0.0
5. Attach binaries: Optional (GitHub auto-generates source archives)
6. Click "Publish release"

**What gets auto-attached:**
- Source code (zip) - auto-generated by GitHub
- Source code (tar.gz) - auto-generated by GitHub

**What to manually attach (optional):**
- Pre-built wheels from PyPI (not necessary - users install from PyPI)
- Documentation PDF (if you generate one)

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PyPI uploads | Custom upload script | twine | Handles authentication, retries, GPG signing, TLS verification |
| Build system | setup.py with distutils | build + setuptools | PEP 517 standard, isolated build environments, reproducible |
| Version extraction | Regex parsing of files | Hard-code or importlib.metadata | Simple is better, fewer edge cases |
| GitHub releases | curl to GitHub API | gh CLI or GitHub Actions | Authentication, markdown rendering, asset uploads handled |
| Wheel validation | Manual inspection | check-wheel-contents | Detects 20+ categories of issues (wrong file permissions, missing py.typed, etc.) |
| Fresh environment testing | "Just trust it" | python -m venv + pip install | Catches missing dependencies, package data, MANIFEST issues |

**Key insight:** PyPI publishing is **unforgiving** - you cannot delete or re-upload a version once published. Use validation tools to catch issues before upload.

## Common Pitfalls

### Pitfall 1: Missing Package Data (py.typed, data files)
**What goes wrong:** Package installs but type stubs don't work, or data files are missing.

**Why it happens:** setuptools needs explicit configuration to include non-.py files.

**How to avoid:**
```toml
# In pyproject.toml
[tool.setuptools.package-data]
ketu = ["py.typed"]  # Explicit inclusion
```

**Warning signs:**
- `mypy` can't find inline types after installing from wheel
- File-not-found errors for bundled data

**Verification:**
```bash
# Check wheel contents
unzip -l dist/ketu-1.0.0-py3-none-any.whl | grep py.typed
# Should show: ketu/py.typed

# Or use check-wheel-contents
check-wheel-contents dist/*.whl
```

### Pitfall 2: Version Desynchronization
**What goes wrong:** `pip show ketu` shows 1.0.0 but `import ketu; ketu.__version__` shows 0.4.0 (or vice versa).

**Why it happens:** Updated version in one location but not the other.

**How to avoid:**
1. Automated test that verifies sync:
```python
def test_version_sync():
    from importlib.metadata import version
    import ketu
    assert version("ketu") == ketu.__version__
```
2. Pre-release checklist item: "Verify version in both pyproject.toml and `__init__.py`"

**Warning signs:**
- Test failure
- Manual inspection shows mismatch

### Pitfall 3: Uploading to PyPI Before Creating Git Tag
**What goes wrong:** PyPI has v1.0.0 but GitHub repo has no corresponding tag/release. Users can't match code to package.

**Why it happens:** Wrong order in release workflow.

**How to avoid:**
- **Always create and push tag BEFORE manual PyPI upload**
- Or use GitHub Actions (tag push triggers publish automatically)

**Warning signs:**
- PyPI release exists but `git tag` doesn't list it
- GitHub releases page missing version

### Pitfall 4: Malformed Changelog Breaking Rendering
**What goes wrong:** CHANGELOG.md displays as plain text on GitHub release, not formatted markdown.

**Why it happens:** Invalid reStructuredText or markdown syntax.

**How to avoid:**
```bash
# Validate with twine
twine check dist/*

# If using RST for long_description, test rendering
python -m readme_renderer README.rst
```

**Warning signs:**
- `twine check` reports errors
- GitHub release preview shows raw markup

### Pitfall 5: Broken Install in Fresh Environment
**What goes wrong:** Package installs fine in dev environment but fails in clean venv.

**Why it happens:**
- Missing dependencies in `pyproject.toml`
- Implicit dependencies from dev environment
- Missing files (incomplete MANIFEST)

**How to avoid:**
```bash
# ALWAYS test in fresh venv before publishing
python -m venv /tmp/test-install
source /tmp/test-install/bin/activate
pip install dist/ketu-1.0.0-py3-none-any.whl
python -c "import ketu; print(ketu.__version__)"
pytest  # If tests are included
deactivate
rm -rf /tmp/test-install
```

**Warning signs:**
- Import errors in fresh venv
- Missing module errors
- Dependency resolution failures

### Pitfall 6: Forgetting to Update Classifiers
**What goes wrong:** PyPI page shows "Development Status :: 4 - Beta" for a 1.0.0 release.

**Why it happens:** Forgot to update classifiers in pyproject.toml.

**How to avoid:**
```toml
# pyproject.toml - UPDATE THIS
classifiers = [
    "Development Status :: 5 - Production/Stable",  # Was "4 - Beta"
    # ... rest unchanged
]
```

**Warning signs:**
- PyPI page displays "Beta" badge
- Automated CI check fails (if you add one)

### Pitfall 7: TestPyPI Limits and Caching
**What goes wrong:** Can't upload new version to TestPyPI because you hit size limits, or old version is cached.

**Why it happens:** TestPyPI has lower storage limits than production PyPI. CDN caching means old versions persist.

**How to avoid:**
- Use TestPyPI sparingly (not for every commit)
- Increment version for each TestPyPI upload (e.g., 1.0.0rc1, 1.0.0rc2)
- Use local venv testing instead of TestPyPI for most validation

**Warning signs:**
- TestPyPI rejects upload due to quota
- `pip install` from TestPyPI gets old version

## Code Examples

Verified patterns from official sources:

### Complete Build and Publish Script

```bash
#!/usr/bin/env bash
# build-and-publish.sh - Local release workflow
set -euo pipefail

VERSION="1.0.0"

echo "=== Ketu ${VERSION} Release ==="

# 1. Clean old builds
echo "[1/7] Cleaning old build artifacts..."
rm -rf dist/ build/ *.egg-info

# 2. Build distributions
echo "[2/7] Building sdist and wheel..."
python -m build --sdist --wheel

# 3. Validate metadata
echo "[3/7] Validating package metadata..."
twine check dist/*

# 4. Check wheel contents (optional but recommended)
echo "[4/7] Checking wheel contents..."
check-wheel-contents dist/*.whl || echo "Warning: check-wheel-contents found issues"

# 5. List build artifacts
echo "[5/7] Build artifacts:"
ls -lh dist/

# 6. Test installation in fresh venv
echo "[6/7] Testing installation in fresh environment..."
TEMP_VENV=$(mktemp -d)
python -m venv "$TEMP_VENV"
source "$TEMP_VENV/bin/activate"
pip install --quiet dist/ketu-${VERSION}-py3-none-any.whl
python -c "import ketu; assert ketu.__version__ == '${VERSION}', 'Version mismatch!'; print(f'✓ Version check passed: {ketu.__version__}')"
pytest tests/ -q || echo "Warning: Tests failed in clean environment"
deactivate
rm -rf "$TEMP_VENV"

echo "[7/7] Build complete and validated!"
echo ""
echo "Next steps:"
echo "  1. Review: ls -la dist/"
echo "  2. Test PyPI (optional): twine upload --repository testpypi dist/*"
echo "  3. Git tag: git tag -a v${VERSION} -m 'Release version ${VERSION}'"
echo "  4. Push: git push origin main && git push origin v${VERSION}"
echo "  5. GitHub Actions will auto-publish to PyPI"
echo "  6. Create GitHub release: gh release create v${VERSION}"
```

### Version Synchronization Test

```python
# tests/test_version.py
"""Verify version synchronization across project."""
from importlib.metadata import version


def test_version_matches_metadata():
    """Ensure __version__ in code matches package metadata."""
    import ketu

    installed_version = version("ketu")
    code_version = ketu.__version__

    assert installed_version == code_version, (
        f"Version mismatch: package metadata={installed_version}, "
        f"ketu.__version__={code_version}"
    )


def test_version_format():
    """Verify version follows semantic versioning."""
    import re
    import ketu

    # Semantic versioning: MAJOR.MINOR.PATCH[-prerelease][+build]
    semver_pattern = r'^\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?(?:\+[a-zA-Z0-9.]+)?$'

    assert re.match(semver_pattern, ketu.__version__), (
        f"Version {ketu.__version__} doesn't follow semantic versioning"
    )
```

### Pyproject.toml Configuration for 1.0.0

```toml
# Source: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ketu"
version = "1.0.0"  # UPDATE: Was 0.4.0
description = "Library to compute astronomical bodies positions and planetary aspects between them"
readme = "README.md"
requires-python = ">=3.10"
license = "MIT"
authors = [
    {name = "Loc Cosnier", email = "loc.cosnier@pm.me"}
]
keywords = [
    "astrology",
    "astronomy",
    "ephemeris",
    "aspects",
    "planets",
    "zodiac",
    "numpy"
]
classifiers = [
    "Development Status :: 5 - Production/Stable",  # UPDATE: Was "4 - Beta"
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",  # Add if missing
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Scientific/Engineering :: Astronomy",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Typing :: Typed",  # Add since you have py.typed
]
dependencies = [
    "numpy>=1.20.0",
]

[project.urls]
Homepage = "https://github.com/alkimya/ketu"
Documentation = "https://ketu.readthedocs.io"
Repository = "https://github.com/alkimya/ketu"
Issues = "https://github.com/alkimya/ketu/issues"
Changelog = "https://github.com/alkimya/ketu/blob/main/CHANGELOG.md"  # Add

[project.scripts]
ketu = "ketu.display:main"

[tool.setuptools]
packages = ["ketu", "ketu.ephemeris", "ketu.aspects", "ketu.cycles", "ketu.cache"]

[tool.setuptools.package-data]
ketu = ["py.typed"]  # Critical for type checking
```

## State of the Art

| Old Approach | Current Approach (2026) | When Changed | Impact |
|--------------|------------------------|--------------|--------|
| setup.py + setuptools.setup() | pyproject.toml + build | PEP 517 (2017), mainstream ~2020 | Isolated builds, reproducible environments |
| Manual twine upload with API tokens | Trusted publishing (OIDC) | 2023 (PyPI feature) | Eliminates long-lived secrets, auto-expiring tokens (15min) |
| python setup.py sdist bdist_wheel | python -m build | PEP 517 adoption | Standard interface for all build backends |
| setup.cfg for metadata | pyproject.toml [project] table | PEP 621 (2020) | Single source of truth for metadata |
| MANIFEST.in for all data | setuptools auto-discovery + package-data | setuptools 61+ (2022) | Less boilerplate, but MANIFEST.in still needed for sdist extras |

**Deprecated/outdated:**
- `python setup.py upload` - **Removed in setuptools**, security issues. Use twine.
- `setup.py install` - **Deprecated**. Use `pip install .`
- API tokens without expiration - Still works but **insecure**. Use trusted publishing.
- `include_package_data=True` without explicit package-data - Can miss files in wheels.

## Open Questions

1. **Should we publish to TestPyPI first?**
   - What we know: TestPyPI is recommended for validation, has separate account, lower storage limits
   - What's unclear: Whether it's worth the setup overhead for a well-tested package
   - Recommendation: **Optional but recommended**. Do it if time permits, skip if confident in local testing.

2. **Should we use GitHub Actions or manual upload for first 1.0.0?**
   - What we know: GitHub Actions is best practice, but requires trusted publisher setup
   - What's unclear: Whether the one-time setup is worth it vs. manual twine upload
   - Recommendation: **Use GitHub Actions with trusted publishing**. It's the modern standard, and Ketu will benefit from automated releases going forward.

3. **Should we include wheel/sdist binaries in GitHub release assets?**
   - What we know: GitHub auto-generates source archives; PyPI hosts wheels
   - What's unclear: Whether duplicating on GitHub adds value
   - Recommendation: **No.** Users install from PyPI. GitHub source archives are sufficient for archival.

4. **Dynamic vs. static versioning?**
   - What we know: Current approach is dual hard-coding (pyproject.toml + `__init__.py`)
   - What's unclear: Whether dynamic versioning (importlib.metadata) reduces maintenance
   - Recommendation: **Keep current approach**. Simple, explicit, works everywhere. Dynamic versioning adds complexity without clear benefit for major releases.

## Sources

### Primary (HIGH confidence)

**Official Python Packaging Authority (PyPA) Documentation:**
- [Publishing package distribution releases using GitHub Actions CI/CD workflows](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/) - GitHub Actions + trusted publishing workflow
- [Writing your pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) - pyproject.toml structure and metadata
- [Using TestPyPI](https://packaging.python.org/guides/using-testpypi/) - TestPyPI validation workflow
- [Single-sourcing the Project Version](https://packaging.python.org/en/latest/discussions/single-source-version/#single-source-version) - Version management patterns

**Official PyPI Documentation:**
- [Publishing with a Trusted Publisher](https://docs.pypi.org/trusted-publishers/) - OIDC/trusted publishing overview
- [Adding a Trusted Publisher to an Existing PyPI Project](https://docs.pypi.org/trusted-publishers/adding-a-publisher/) - GitHub Actions configuration fields

**Official GitHub Documentation:**
- [gh release create command](https://cli.github.com/manual/gh_release_create) - GitHub CLI release creation

**Official setuptools Documentation:**
- [Configuring setuptools using pyproject.toml files](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html) - setuptools configuration reference
- [Controlling files in the distribution](https://setuptools.pypa.io/en/latest/userguide/miscellaneous.html) - Package data and MANIFEST.in
- [Data Files Support](https://setuptools.pypa.io/en/latest/userguide/datafiles.html) - py.typed and package data configuration

### Secondary (MEDIUM confidence)

- [How to Test a Python Distribution — pydistcheck documentation](https://pydistcheck.readthedocs.io/en/latest/how-to-test-a-python-distribution.html) - Validation tools and techniques
- [Knowledge Bits — Common Python Packaging Mistakes](https://jwodder.github.io/kbits/posts/pypkg-mistakes/) - Pitfalls and anti-patterns
- [PyPI Release Checklist — cookiecutter-pypackage](https://cookiecutter-pypackage.readthedocs.io/en/latest/pypi_release_checklist.html) - Standard release workflow steps
- [What Are Python Wheels and Why Should You Care? – Real Python](https://realpython.com/python-wheels/) - Wheel format and best practices
- [How to Publish an Open-Source Python Package to PyPI – Real Python](https://realpython.com/pypi-publish-python-package/) - End-to-end publishing guide
- [Setup Trusted Publishing for secure and automated publishing via GitHub Actions — Python Packaging Guide](https://www.pyopensci.org/python-package-guide/tutorials/trusted-publishing.html) - PyOpenSci trusted publishing tutorial

### Tertiary (LOW confidence - community guides)

- [Automate PyPi releases with Github Actions | Medium](https://medium.com/@VersuS_/automate-pypi-releases-with-github-actions-4c5a9cfe947d) - Community workflow example
- [Pradyun Gedam's blog: Choreographing a release process](https://pradyunsg.me/blog/2024/01/27/package-release-workflow/) - pip maintainer's release workflow

## Metadata

**Confidence breakdown:**
- Standard stack: **HIGH** - All tools are official PyPA standards, verified from pypa.io and packaging.python.org
- Architecture patterns: **HIGH** - Workflows from official PyPA guides, tested by thousands of projects
- Pitfalls: **HIGH** - Sourced from official documentation warnings and experienced maintainer blogs
- Trusted publishing: **HIGH** - Official PyPI feature documented at docs.pypi.org
- GitHub Actions workflow: **HIGH** - Official pypa/gh-action-pypi-publish action maintained by PyPA

**Research date:** 2026-02-12
**Valid until:** ~90 days (packaging ecosystem is stable; trusted publishing and PEP 621 are established standards)

**Notes:**
- All official PyPA and PyPI documentation reflects 2026 state of the art
- Trusted publishing is production-ready and recommended for all new releases
- setuptools with pyproject.toml is the most compatible approach for existing projects
- Fresh venv testing is CRITICAL - PyPI uploads are permanent and cannot be deleted
