"""Match request URL paths against RAML resource templates (e.g. /users/{id})."""

import re


def match_raml_path(raml_path, request_path):
    """Return whether *request_path* matches the RAML template *raml_path*.

    Args:
        raml_path: RAML resource path with ``{param}`` segments.
        request_path: Concrete path from the HTTP request.

    Returns:
        tuple: (matched: bool, path_params: dict of string values from the path)
    """
    pattern = re.sub(r"\{(\w+)\}", r"(?P<\1>[^/]+)", raml_path)
    pattern = "^" + pattern + "$"
    match = re.match(pattern, request_path)
    if match:
        return True, match.groupdict()
    return False, {}
