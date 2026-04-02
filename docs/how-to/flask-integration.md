# How to integrate with Flask

This guide shows you how to integrate ramlpy with your Flask application.

## Installation

First, install ramlpy with Flask support:

```bash
pip install ramlpy[flask]
```

## Approach 1: Decorator

The simplest approach is to use the `@validate_with_raml` decorator:

```python
from flask import Flask, request, jsonify
from ramlpy import parse
from ramlpy.integrations.flask import validate_with_raml

app = Flask(__name__)
api = parse("api.raml")

@app.route("/users/<int:user_id>", methods=["GET"])
@validate_with_raml(api, path="/users/{userId}", method="get")
def get_user(user_id):
    validated = request.raml.validated
    user_id = validated["path_params"]["userId"]
    return jsonify({"id": user_id})
```

## Approach 2: Extension

For larger applications, use the `RamlApi` extension:

```python
from flask import Flask
from ramlpy import parse
from ramlpy.integrations.flask import RamlApi

app = Flask(__name__)
api = parse("api.raml")

# Initialize the extension
raml = RamlApi(app, api_spec=api)

@app.route("/users/<int:user_id>", methods=["GET"])
@raml.validate(path="/users/{userId}", method="get")
def get_user(user_id):
    validated = request.raml.validated
    return jsonify({"id": validated["path_params"]["userId"]})
```

## Application Factory Pattern

If you use the application factory pattern:

```python
from flask import Flask
from ramlpy import parse
from ramlpy.integrations.flask import RamlApi

raml = RamlApi()

def create_app():
    app = Flask(__name__)
    api = parse("api.raml")
    raml.init_app(app, api_spec=api)
    
    from .views import register_views
    register_views(app)
    
    return app
```

**views.py:**
```python
from flask import request, jsonify
from . import raml

def register_views(app):
    @app.route("/users", methods=["GET"])
    @raml.validate(path="/users", method="get")
    def list_users():
        validated = request.raml.validated
        return jsonify({"users": []})
```

## Accessing Validated Data

After validation, the validated data is available in several places:

```python
@raml.validate(path="/users/{userId}", method="get")
def get_user(user_id):
    # Via request object
    validated = request.raml.validated
    
    # Via Flask's g object
    validated = g.raml_validated
    
    # Structure:
    # {
    #     "path_params": {"userId": 123},
    #     "query_params": {"limit": 10},
    #     "headers": {"Accept": "application/json"},
    #     "body": {...}
    # }
```

## Custom Error Responses

By default, validation errors return a 400 response with JSON errors. To customize:

```python
from flask import Flask, request, jsonify
from ramlpy.integrations.flask import validate_with_raml

def custom_validate(api, path, method):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            result = api.validate_request(
                path=path or request.path,
                method=method or request.method,
                path_params=kwargs,
                query_params=request.args.to_dict(flat=True),
                headers=dict(request.headers),
                body=request.get_json(silent=True),
                content_type=request.content_type,
            )
            if not result.ok:
                # Custom error format
                return jsonify({
                    "status": "error",
                    "details": result.errors
                }), 400
            request.raml = type("RamlContext", (), {"validated": result.data})()
            return fn(*args, **kwargs)
        return wrapper
    return decorator
```

## Blueprint Integration

Works seamlessly with Flask Blueprints:

```python
from flask import Blueprint, request, jsonify
from ramlpy.integrations.flask import validate_with_raml

users_bp = Blueprint('users', __name__)

@users_bp.route("/users", methods=["GET"])
@validate_with_raml(api, path="/users", method="get")
def list_users():
    return jsonify({"users": []})
```
