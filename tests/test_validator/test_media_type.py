"""Tests for Content-Type normalization and body spec resolution."""

from ramlpy.model.api import ApiSpec
from ramlpy.model.bodies import BodySpec
from ramlpy.model.method import MethodSpec
from ramlpy.model.resource import ResourceSpec
from ramlpy.model.types import TypeSpec
from ramlpy.validator.engine import validate_request
from ramlpy.validator.media_type import normalize_media_type, resolve_body_spec


def test_normalize_media_type_strips_charset():
    assert normalize_media_type('application/json; charset=utf-8') == "application/json"
    assert normalize_media_type("  TEXT/PLAIN ; Charset=US-ASCII ") == "text/plain"


def test_resolve_body_spec_matches_charset_suffix():
    bodies = {
        "application/json": BodySpec(media_type="application/json"),
    }
    assert resolve_body_spec(bodies, "application/json; charset=utf-8") is bodies["application/json"]


def test_validate_request_body_with_charset_in_content_type():
    schema = {
        "type": "object",
        "required": ["name"],
        "properties": {"name": {"type": "string"}},
    }
    api = ApiSpec(
        title="t",
        version="v1",
        resources=[
            ResourceSpec(
                full_path="/items",
                uri_parameters={},
                methods={
                    "post": MethodSpec(
                        method="post",
                        bodies={
                            "application/json": BodySpec(
                                media_type="application/json",
                                type_ref="Payload",
                            ),
                        },
                    ),
                },
            ),
        ],
        types={
            "Payload": TypeSpec(name="Payload", schema_source=schema),
        },
    )
    result = validate_request(
        api,
        path="/items",
        method="post",
        path_params={},
        query_params={},
        headers={},
        body={"name": "ok"},
        content_type="application/json; charset=utf-8",
    )
    assert result.ok
