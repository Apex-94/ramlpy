"""Test validation engine."""

from ramlpy.model.api import ApiSpec
from ramlpy.model.resource import ResourceSpec
from ramlpy.model.method import MethodSpec
from ramlpy.model.parameters import ParameterSpec
from ramlpy.validator.engine import validate_request, validate_parameter


def test_validate_parameter_required_missing():
    param = ParameterSpec(name="id", location="path", required=True, type_ref="integer")
    value, error = validate_parameter(param, None, "path.id")
    assert value is None
    assert error is not None
    assert error.code == "missing_required"


def test_validate_parameter_required_with_default():
    param = ParameterSpec(name="limit", location="query", required=False, type_ref="integer", default=10)
    value, error = validate_parameter(param, None, "query.limit")
    assert value == 10
    assert error is None


def test_validate_parameter_integer_valid():
    param = ParameterSpec(name="id", location="path", required=True, type_ref="integer")
    value, error = validate_parameter(param, "123", "path.id")
    assert value == 123
    assert error is None


def test_validate_parameter_integer_invalid():
    param = ParameterSpec(name="id", location="path", required=True, type_ref="integer")
    value, error = validate_parameter(param, "abc", "path.id")
    assert value is None
    assert error is not None
    assert error.code == "invalid_type"


def test_validate_parameter_enum_valid():
    param = ParameterSpec(name="sort", location="query", required=False, type_ref="string", enum=["asc", "desc"])
    value, error = validate_parameter(param, "asc", "query.sort")
    assert value == "asc"
    assert error is None


def test_validate_parameter_enum_invalid():
    param = ParameterSpec(name="sort", location="query", required=False, type_ref="string", enum=["asc", "desc"])
    value, error = validate_parameter(param, "random", "query.sort")
    assert value is None
    assert error is not None
    assert error.code == "invalid_enum"


def test_validate_request_route_not_found():
    api = ApiSpec(title="Test", version="v1", resources=[])
    result = validate_request(
        api,
        path="/users",
        method="get",
        path_params={},
        query_params={},
        headers={},
        body=None,
        content_type=None,
    )
    assert not result.ok
    assert len(result.errors) == 1
    assert result.errors[0]["code"] == "route_not_found"


def test_validate_request_valid():
    param = ParameterSpec(name="id", location="path", required=True, type_ref="integer")
    resource = ResourceSpec(
        full_path="/users/{id}",
        uri_parameters={"id": param},
        methods={"get": MethodSpec(method="get")},
    )
    api = ApiSpec(title="Test", version="v1", resources=[resource])
    
    result = validate_request(
        api,
        path="/users/{id}",
        method="get",
        path_params={"id": "123"},
        query_params={},
        headers={},
        body=None,
        content_type=None,
    )
    assert result.ok
    assert result.data["path_params"]["id"] == 123


def test_validate_request_concrete_path_extracts_params():
    param = ParameterSpec(name="id", location="path", required=True, type_ref="integer")
    resource = ResourceSpec(
        full_path="/users/{id}",
        uri_parameters={"id": param},
        methods={"get": MethodSpec(method="get")},
    )
    api = ApiSpec(title="Test", version="v1", resources=[resource])
    result = validate_request(
        api,
        path="/users/99",
        method="get",
        path_params={},
        query_params={},
        headers={},
        body=None,
        content_type=None,
    )
    assert result.ok
    assert result.data["path_params"]["id"] == 99


def test_validate_request_headers_case_insensitive():
    resource = ResourceSpec(
        full_path="/ping",
        uri_parameters={},
        methods={
            "get": MethodSpec(
                method="get",
                headers={
                    "X-Request-Id": ParameterSpec(
                        name="X-Request-Id",
                        location="header",
                        required=True,
                        type_ref="string",
                    ),
                },
            ),
        },
    )
    api = ApiSpec(title="Test", version="v1", resources=[resource])
    result = validate_request(
        api,
        path="/ping",
        method="get",
        path_params={},
        query_params={},
        headers={"x-request-id": "abc"},
        body=None,
        content_type=None,
    )
    assert result.ok
    assert result.data["headers"]["X-Request-Id"] == "abc"


def test_api_spec_nested_resource_lookup():
    inner = ResourceSpec(full_path="/parent/child", uri_parameters={}, methods={})
    parent = ResourceSpec(
        full_path="/parent",
        uri_parameters={},
        methods={},
        nested_resources=[inner],
    )
    api = ApiSpec(title="Test", version="v1", resources=[parent])
    assert api.resource("/parent/child") is inner
