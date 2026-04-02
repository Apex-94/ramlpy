"""Test Flask auto-routes."""
import pytest
from flask import Flask, jsonify

from ramlpy import parse
from ramlpy.integrations.flask import RamlAutoApi


@pytest.fixture
def api_spec():
    return parse("tests/fixtures/raml_examples/simple-08/api.raml")


@pytest.fixture
def app(api_spec):
    flask_app = Flask(__name__)
    flask_app.config["TESTING"] = True
    auto_api = RamlAutoApi(flask_app, api_spec)

    @auto_api.route("/users", "GET")
    def get_users(validated_data):
        return jsonify({"users": [{"id": 1, "name": "Alice"}]})

    @auto_api.route("/users", "POST")
    def create_user(validated_data):
        return jsonify({"created": validated_data.get("body", {})}), 201

    @auto_api.route("/users/{userId}", "GET")
    def get_user(validated_data):
        return jsonify({"user": {"id": validated_data["path_params"]["userId"], "name": "Alice"}})

    auto_api.register_routes(flask_app)
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_users(client):
    resp = client.get("/users")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "users" in data


def test_get_user(client):
    resp = client.get("/users/42")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["user"]["id"] == 42


def test_create_user(client):
    resp = client.post("/users", json={"name": "Bob", "email": "bob@example.com"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert "created" in data


def test_route_not_defined(client):
    resp = client.delete("/users")
    assert resp.status_code == 405
