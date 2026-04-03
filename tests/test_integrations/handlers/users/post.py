"""Handler for POST /users."""
from flask import jsonify


def handle(validated_data):
    """Handle POST /users request."""
    body = validated_data.get("body", {})
    return jsonify({"created": body}), 201
