"""Single handlers file for all routes."""
from flask import jsonify


def users_get(validated_data):
    """Handle GET /users."""
    return jsonify({"users": [{"id": 1, "name": "Alice"}]})


def users_post(validated_data):
    """Handle POST /users."""
    body = validated_data.get("body", {})
    return jsonify({"created": body}), 201


def users_userId_get(validated_data):
    """Handle GET /users/{userId}."""
    user_id = validated_data["path_params"]["userId"]
    return jsonify({"user": {"id": user_id, "name": "Alice"}})
