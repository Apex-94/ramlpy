"""Tests for ValidationResult helpers and ApiSpec routing helpers."""

import pytest

from ramlpy.exceptions import RamlValidationError
from ramlpy.model.api import ApiSpec
from ramlpy.model.method import MethodSpec
from ramlpy.model.parameters import ParameterSpec
from ramlpy.model.resource import ResourceSpec
from ramlpy.validator.engine import resolve_route
from ramlpy.validator.errors import ValidationResult


def test_validation_result_raise_unless_ok():
    ok = ValidationResult(True, data={}, errors=[])
    ok.raise_unless_ok()

    bad = ValidationResult(False, data={}, errors=[{"code": "x"}])
    with pytest.raises(RamlValidationError) as exc:
        bad.raise_unless_ok()
    assert exc.value.errors == [{"code": "x"}]


def test_resolve_route_public():
    resource = ResourceSpec(
        full_path="/a/{id}",
        uri_parameters={"id": ParameterSpec(name="id", location="path", type_ref="string")},
        methods={"get": MethodSpec(method="get")},
    )
    api = ApiSpec(resources=[resource])
    r, m, extracted = resolve_route(api, "/a/1", "get")
    assert r is resource
    assert m.method == "get"
    assert extracted == {"id": "1"}


def test_api_spec_match_route():
    resource = ResourceSpec(
        full_path="/x",
        uri_parameters={},
        methods={"get": MethodSpec(method="get")},
    )
    api = ApiSpec(resources=[resource])
    r, m, ext = api.match_route("/x", "get")
    assert r is resource
    assert m.method == "get"
    assert ext == {}

    assert api.match_route("/missing", "get")[0] is None
