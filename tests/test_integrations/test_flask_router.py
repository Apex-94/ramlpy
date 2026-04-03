"""Test RamlRouter - auto-discovery of handler files from directory."""
import os
import pytest
from flask import Flask

from ramlpy import parse
from ramlpy.integrations.flask_router import RamlRouter


@pytest.fixture
def api_spec():
    return parse("tests/fixtures/raml_examples/simple-08/api.raml")


@pytest.fixture
def handlers_dir():
    return os.path.join(os.path.dirname(__file__), "handlers")


@pytest.fixture
def app(api_spec, handlers_dir):
    flask_app = Flask(__name__)
    flask_app.config["TESTING"] = True

    router = RamlRouter(flask_app, api_spec, handlers_dir=handlers_dir)
    with flask_app.app_context():
        router.register_routes()

    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_users(client):
    resp = client.get("/users")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "users" in data


def test_post_users(client):
    resp = client.post("/users", json={"name": "Bob", "email": "bob@example.com"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["created"]["name"] == "Bob"


def test_get_user_by_id(client):
    resp = client.get("/users/42")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["user"]["id"] == 42


def test_list_routes(api_spec, handlers_dir):
    router = RamlRouter(api_spec=api_spec, handlers_dir=handlers_dir)
    routes = router.list_routes()
    assert len(routes) > 0
    # Check that handler files are found
    found = [r for r in routes if r["found"]]
    assert len(found) >= 3  # GET /users, POST /users, GET /users/{userId}
