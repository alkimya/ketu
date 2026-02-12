"""Verify version synchronization across project."""

import re

from importlib.metadata import version


def test_version_matches_metadata() -> None:
    """Ensure __version__ matches installed package metadata."""
    import ketu

    installed_version = version("ketu")
    code_version = ketu.__version__

    assert installed_version == code_version, (
        f"Version mismatch: package metadata={installed_version}, "
        f"ketu.__version__={code_version}"
    )


def test_version_format() -> None:
    """Verify version follows semantic versioning."""
    import ketu

    semver_pattern = r"^\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?(?:\+[a-zA-Z0-9.]+)?$"

    assert re.match(semver_pattern, ketu.__version__), (
        f"Version {ketu.__version__} does not follow semantic versioning"
    )
