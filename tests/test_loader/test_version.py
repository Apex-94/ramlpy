"""Test version detection."""

import pytest
from ramlpy.loader.version import detect_raml_version
from ramlpy.exceptions import RamlVersionError


def test_detect_raml_08():
    text = "#%RAML 0.8\ntitle: Test"
    assert detect_raml_version(text) == "0.8"


def test_detect_raml_10():
    text = "#%RAML 1.0\ntitle: Test"
    assert detect_raml_version(text) == "1.0"


def test_detect_raml_10_library():
    text = "#%RAML 1.0 Library\ntitle: Test"
    assert detect_raml_version(text) == "1.0"


def test_detect_raml_10_resource_type():
    text = "#%RAML 1.0 ResourceType\ndisplayName: Test"
    assert detect_raml_version(text) == "1.0"


def test_missing_header():
    with pytest.raises(RamlVersionError):
        detect_raml_version("title: Test")


def test_empty_string():
    with pytest.raises(RamlVersionError):
        detect_raml_version("")
