# Tutorial: Building a Validated API

In this tutorial, we'll build a complete Flask API with RAML-based request validation. By the end, you'll understand how to:

- Define a RAML API specification
- Parse the specification with ramlpy
- Validate incoming requests against the spec
- Return structured error responses

## Prerequisites

- Python 3.6 or later
- Basic familiarity with Flask
- Basic understanding of RAML

## Step 1: Define the API

First, let's create a RAML file that describes our API. Create a file called `api.raml`:

```raml
#%RAML 1.0
title: User Management API
version: v1
baseUri: https://api.example.com/{version}
mediaType: application/json

types:
  User:
    type: object
    properties:
      id: integer
      name: string
      email: string
      role:
        type: string
        enum: [admin, user, guest]

  UserCreateRequest:
    type: object
    properties:
      name: string
      email: string
      role?:
        type: string
        enum: [admin, user, guest]

  ErrorResponse:
    type: object
    properties:
      errors:
        type: array
        items:
          type: object
          properties:
            code: string
            message: string
            pointer: string

/users:
  get:
    description: List all users
    queryParameters:
      limit?:
        type: integer
        default: 20
        minimum: 1
        maximum: 100
      offset?:
        type: integer
        default: 0
        minimum: 0
      role?:
        type: string
        enum: [admin, user, guest]
    responses:
      200:
        body:
          application/json:
            type: User[]

  post:
    description: Create a new user
    body:
      application/json:
        type: UserCreateRequest
    responses:
      201:
        body:
          application/json:
            type: User

/users/{userId}:
  uriParameters:
    userId:
      type: integer
      minimum: 1
  get:
    description: Get a user by ID
    responses:
      200:
        body:
          application/json:
            type: User
      404:
        body:
          application/json:
            type: ErrorResponse
```

## Step 2: Set Up the Flask App

Create a new file called `app.py`:

```python
from flask import Flask, request, jsonify
from ramlpy import parse
from ramlpy.integrations.flask import validate_with_raml

app = Flask(__name__)

# Parse the RAML specification
api = parse("api.raml")

# In-memory user store for demonstration
USERS = [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
    {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
]

@app.route("/users", methods=["GET"])
@validate_with_raml(api, path="/users", method="get")
def list_users():
    """List all users with optional filtering."""
    validated = request.raml.validated
    query_params = validated["query_params"]
    
    # Apply filters
    users = USERS[:]
    if "role" in query_params:
        users = [u for u in users if u["role"] == query_params["role"]]
    
    # Apply pagination
    offset = query_params.get("offset", 0)
    limit = query_params.get("limit", 20)
    users = users[offset:offset + limit]
    
    return jsonify(users)

@app.route("/users", methods=["POST"])
@validate_with_raml(api, path="/users", method="post")
def create_user():
    """Create a new user."""
    validated = request.raml.validated
    body = validated["body"]
    
    # Create new user
    new_id = max(u["id"] for u in USERS) + 1 if USERS else 1
    new_user = {
        "id": new_id,
        "name": body["name"],
        "email": body["email"],
        "role": body.get("role", "user"),
    }
    USERS.append(new_user)
    
    return jsonify(new_user), 201

@app.route("/users/<int:user_id>", methods=["GET"])
@validate_with_raml(api, path="/users/{userId}", method="get")
def get_user(user_id):
    """Get a user by ID."""
    validated = request.raml.validated
    user_id = validated["path_params"]["userId"]
    
    user = next((u for u in USERS if u["id"] == user_id), None)
    if user is None:
        return jsonify({"errors": [{"code": "not_found", "message": "User not found"}]}), 404
    
    return jsonify(user)

if __name__ == "__main__":
    app.run(debug=True)
```

## Step 3: Run the App

```bash
pip install flask ramlpy
python app.py
```

## Step 4: Test the API

### Valid Request

```bash
# List users with pagination
curl "http://localhost:5000/users?limit=10&offset=0"

# Create a new user
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Charlie", "email": "charlie@example.com"}'

# Get a user by ID
curl http://localhost:5000/users/1
```

### Invalid Request

```bash
# Invalid limit (not a number)
curl "http://localhost:5000/users?limit=abc"
# Returns: {"errors": [{"code": "invalid_type", "message": "Parameter 'limit' is not a valid integer", ...}]}

# Invalid role (not in enum)
curl "http://localhost:5000/users?role=superadmin"
# Returns: {"errors": [{"code": "invalid_enum", "message": "Parameter 'role' must be one of ['admin', 'user', 'guest']", ...}]}

# Missing required body field
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Charlie"}'
# Returns: {"errors": [{"code": "missing_required_property", ...}]}
```

## Step 5: Understanding the Validation Flow

Here's what happens when a request comes in:

1. Flask receives the request and routes it to the appropriate view function
2. The `@validate_with_raml` decorator intercepts the request
3. ramlpy validates the request against the RAML specification:
   - Path parameters are validated and coerced (e.g., `userId` to integer)
   - Query parameters are validated and coerced (e.g., `limit` to integer)
   - Headers are validated (e.g., `Content-Type`)
   - Request body is validated against the schema
4. If validation fails, a 400 response is returned with error details
5. If validation passes, the validated data is attached to `request.raml.validated`

## Next Steps

- Learn how to [handle validation errors](../how-to/handle-errors.md)
- Explore [RAML includes](../how-to/use-includes.md) for larger APIs
- See the [Flask integration guide](../how-to/flask-integration.md) for more options