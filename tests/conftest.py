"""Test configuration."""

import os
import pytest

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture
def raml08_fixture():
    """Load a RAML 0.8 fixture."""
    path = os.path.join(FIXTURES_DIR, "raml08", "simple_api.raml")
    with open(path, "r") as f:
        return f.read()


@pytest.fixture
def raml10_fixture():
    """Load a RAML 1.0 fixture."""
    path = os.path.join(FIXTURES_DIR, "raml10", "simple_api.raml")
    with open(path, "r") as f:
        return f.read()


@pytest.fixture
def raml08_fixture_path():
    """Get path to RAML 0.8 fixture."""
    return os.path.join(FIXTURES_DIR, "raml08", "simple_api.raml")


@pytest.fixture
def raml10_fixture_path():
    """Get path to RAML 1.0 fixture."""
    return os.path.join(FIXTURES_DIR, "raml10", "simple_api.raml")
