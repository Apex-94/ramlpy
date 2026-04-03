"""Handler for GET /users/{userId}."""
from flask import jsonify


def handle(validated_data):
    """Handle GET /users/{userId} request."""
    user_id = validated_data["path_params"]["userId"]
    return jsonify({"user": {"id": user_id, "name": "Alice"}})
