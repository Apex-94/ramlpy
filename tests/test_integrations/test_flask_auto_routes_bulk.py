"""Test Flask auto-routes bulk approach (Approach 2: RamlApi.auto_routes)."""
import pytest
from flask import Flask, jsonify

from ramlpy import parse
from ramlpy.integrations.flask import RamlApi


@pytest.fixture
def api_spec():
    return parse("tests/fixtures/raml_examples/simple-08/api.raml")


@pytest.fixture
def app(api_spec):
    flask_app = Flask(__name__)
    flask_app.config["TESTING"] = True

    raml_api = RamlApi(flask_app, api_spec)

    # Single handler for all routes
    def handler(resource_path, method, validated_data):
        return jsonify({
            "resource": resource_path,
            "method": method,
            "data": validated_data,
        })

    with flask_app.app_context():
        raml_api.auto_routes(handler)

    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_users(client):
    resp = client.get("/users")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["resource"] == "/users"
    assert data["method"] == "get"


def test_post_users(client):
    resp = client.post("/users", json={"name": "Bob"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["resource"] == "/users"
    assert data["method"] == "post"
    assert data["data"]["body"]["name"] == "Bob"


def test_get_user_by_id(client):
    resp = client.get("/users/42")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["resource"] == "/users/{userId}"
    assert data["method"] == "get"
    assert data["data"]["path_params"]["userId"] == 42


def test_route_not_defined(client):
    resp = client.delete("/users")
    assert resp.status_code == 405
