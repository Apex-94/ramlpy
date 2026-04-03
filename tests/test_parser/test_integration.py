"""Integration tests for parsing RAML files."""

import os
import pytest
from ramlpy.api import parse, parse_string
from ramlpy.loader.version import detect_raml_version


def test_parse_raml08(raml08_fixture_path):
    """Test parsing a RAML 0.8 file."""
    api = parse(raml08_fixture_path)
    assert api.title == "Simple API"
    assert api.version == "v1"
    assert len(api.resources) > 0


def test_parse_raml10(raml10_fixture_path):
    """Test parsing a RAML 1.0 file."""
    api = parse(raml10_fixture_path)
    assert api.title == "Simple API"
    assert api.version == "v1"
    assert len(api.resources) > 0
    assert "User" in api.types


def test_parse_accepts_pathlib_path(raml10_fixture_path):
    """parse() should accept os.PathLike paths."""
    from pathlib import Path

    api = parse(Path(raml10_fixture_path))
    assert api.title == "Simple API"


def test_parse_string_raml08(raml08_fixture):
    """Test parsing RAML 0.8 from string."""
    api = parse_string(raml08_fixture)
    assert api.title == "Simple API"
    assert api.version == "v1"


def test_parse_string_raml10(raml10_fixture):
    """Test parsing RAML 1.0 from string."""
    api = parse_string(raml10_fixture)
    assert api.title == "Simple API"
    assert api.version == "v1"
    assert "User" in api.types


def test_resource_access(raml08_fixture_path):
    """Test accessing resources from parsed API."""
    api = parse(raml08_fixture_path)
    users_resource = api.resource("/users")
    assert users_resource is not None
    assert "get" in users_resource.methods


def test_validation_result(raml08_fixture_path):
    """Test validation result structure."""
    api = parse(raml08_fixture_path)
    result = api.validate_request(
        path="/users",
        method="get",
        path_params={},
        query_params={"limit": "10"},
        headers={},
        body=None,
        content_type=None,
    )
    assert result.ok
    assert result.data["query_params"]["limit"] == 10
