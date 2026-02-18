"""Minimal conftest file to bring in pytester plugin."""

import pytest
# FIXME: Is this supposed to error? https://docs.pytest.org/en/stable/deprecations.html#pytest-plugins-in-non-top-level-conftest-files
# A subdir that defines pytest_plugins _will_ error with
# "Failed: Defining 'pytest_plugins' in a non-top-level conftest is no longer supported".  # noqa: E501
# Now that Sybil is used for doctests however, we have a conftest.py at project
# root (which does _not_ define pytest_plugins). But no error occurs...
pytest_plugins = "pytester"


@pytest.fixture
def file_exists(pytester):
    def inner(glob):
        return next(pytester.path.glob(glob), None) is not None

    return inner
