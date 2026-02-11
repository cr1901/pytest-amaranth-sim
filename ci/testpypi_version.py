"""Remove local info from version string for testPyPI builds.

This is required to avoid a "The use of local versions in... is not allowed."
error when publishing to (Test) PyPI. However, I prefer PDM to handle version
strings otherwise.
"""

import os
from pdm.backend.hooks.version import SCMVersion, default_version_formatter  # pyright: ignore[reportMissingImports]


def format_version(version: SCMVersion) -> str:  # noqa: D103
    ver = default_version_formatter(version)

    if os.environ.get("GITHUB_JOB", "") in ("build",):
        # If doing the publish to (Test) PyPI, drop local version identifier,
        # as specified by: https://packaging.python.org/en/latest/specifications/version-specifiers/#local-version-identifiers
        return ver.split("+")[0]
    else:
        return ver
