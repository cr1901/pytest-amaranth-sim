"""Minimal conftest file to bring in pytester plugin."""

import pytest
pytest_plugins = "pytester"


@pytest.fixture
def file_exists(pytester):
    def inner(glob):
        return next(pytester.path.glob(glob), None) is not None

    return inner
