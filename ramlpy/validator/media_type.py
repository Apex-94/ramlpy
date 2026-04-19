"""HTTP Content-Type handling for request validation."""


def normalize_media_type(content_type):
    """Return the media type in lowercase without parameters (e.g. charset).

    ``application/json; charset=utf-8`` → ``application/json``
    """
    if not content_type or not isinstance(content_type, str):
        return None
    stripped = content_type.strip()
    if not stripped:
        return None
    main = stripped.split(";", 1)[0].strip()
    return main.lower() if main else None


def resolve_body_spec(bodies, content_type):
    """Pick the :class:`~ramlpy.model.bodies.BodySpec` for this Content-Type.

    Matches case-insensitively and ignores parameters such as ``charset``, so RAML
    keys like ``application/json`` work when the client sends
    ``application/json; charset=utf-8``.

    Args:
        bodies: ``dict`` mapping media type string -> BodySpec
        content_type: Raw ``Content-Type`` header value, or None

    Returns:
        BodySpec or None if *bodies* is empty.
    """
    if not bodies:
        return None
    if not content_type:
        for spec in bodies.values():
            return spec
        return None

    normalized = normalize_media_type(content_type)
    if normalized and normalized in bodies:
        return bodies[normalized]
    if content_type in bodies:
        return bodies[content_type]
    if normalized:
        for key, spec in bodies.items():
            if normalize_media_type(key) == normalized:
                return spec
    for spec in bodies.values():
        return spec
    return None
