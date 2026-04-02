"""Flask integration for RAML validation."""

from functools import wraps

try:
    from flask import request, jsonify, g
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


def validate_with_raml(api, path=None, method=None):
    """Flask decorator to validate requests against RAML spec.
    
    Args:
        api: ApiSpec to validate against
        path: RAML path pattern (e.g., /users/{id})
        method: HTTP method (e.g., get, post)
    
    Returns:
        Decorator function
    """
    if not HAS_FLASK:
        raise ImportError("Flask is required for this integration")
    
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
                return jsonify({"errors": result.errors}), 400
            g.raml_validated = result.data
            request.raml = type("RamlContext", (), {"validated": result.data})()
            return fn(*args, **kwargs)
        return wrapper
    return decorator


class RamlApi(object):
    """Flask extension for RAML validation."""
    
    def __init__(self, app=None, api_spec=None):
        self.api_spec = api_spec
        if app is not None:
            self.init_app(app, api_spec)
    
    def init_app(self, app, api_spec=None):
        """Initialize the extension with a Flask app."""
        if api_spec:
            self.api_spec = api_spec
        app.extensions['ramlpy'] = self
    
    def validate(self, path=None, method=None):
        """Decorator to validate requests."""
        return validate_with_raml(self.api_spec, path=path, method=method)
