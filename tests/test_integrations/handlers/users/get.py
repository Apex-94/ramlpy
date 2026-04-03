"""Handler for GET /users."""
from flask import jsonify


def handle(validated_data):
    """Handle GET /users request."""
    return jsonify({"users": [{"id": 1, "name": "Alice"}]})
