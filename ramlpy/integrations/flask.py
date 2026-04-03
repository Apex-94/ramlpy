"""Flask integration for RAML validation."""

import re
from functools import wraps

try:
    from flask import request, jsonify, g, Flask, current_app
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


def _raml_path_to_flask(path):
    """Convert a RAML path like /users/{userId} to Flask route /users/<userId>."""
    return re.sub(r'\{(\w+)\}', r'<\1>', path)


def _match_raml_path(raml_path, request_path):
    """Check if a request path matches a RAML path pattern.
    
    Returns (matched, path_params) tuple.
    """
    pattern = re.sub(r'\{(\w+)\}', r'(?P<\1>[^/]+)', raml_path)
    pattern = '^' + pattern + '$'
    m = re.match(pattern, request_path)
    if m:
        return True, m.groupdict()
    return False, {}


class RamlApi(object):
    """Flask extension for RAML validation with auto-routing."""
    
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
    
    def auto_routes(self, handler, methods=None, exclude=None):
        """Dynamically register Flask routes for all RAML resources/methods.
        
        For each resource+method combination in the RAML spec, registers a Flask
        route that validates the request and then calls the provided handler.
        
        Args:
            handler: A callable that receives (resource_path, http_method, validated_data)
                     and returns a Flask response.
                     Signature: handler(resource_path, method, validated_data) -> response
            methods: Optional list of HTTP methods to include. If None, all methods
                     defined in the RAML are used.
            exclude: Optional set of (path, method) tuples to exclude.
        
        Returns:
            list: List of registered Flask rule objects
        """
        if self.api_spec is None:
            raise RuntimeError("api_spec must be set before calling auto_routes()")
        
        exclude = exclude or set()
        methods = set(m.upper() for m in (methods or [])) if methods else None
        rules = []
        
        for resource in self.api_spec.resources:
            raml_path = resource.full_path
            flask_path = _raml_path_to_flask(raml_path)
            
            for http_method in resource.methods:
                method_upper = http_method.upper()
                
                # Skip if methods filter is set and this method isn't included
                if methods and method_upper not in methods:
                    continue
                
                # Skip if excluded
                if (raml_path, http_method) in exclude or (raml_path, method_upper) in exclude:
                    continue
                
                endpoint = "%s_%s" % (http_method, raml_path.strip("/").replace("/", "_"))
                
                def make_view(raml_p, method_m):
                    def view(**path_params):
                        result = self.api_spec.validate_request(
                            path=raml_p,
                            method=method_m,
                            path_params=path_params,
                            query_params=request.args.to_dict(flat=True),
                            headers=dict(request.headers),
                            body=request.get_json(silent=True),
                            content_type=request.content_type,
                        )
                        if not result.ok:
                            return jsonify({"errors": result.errors}), 400
                        g.raml_validated = result.data
                        request.raml = type("RamlContext", (), {"validated": result.data})()
                        return handler(raml_p, method_m, result.data)
                    return view
                
                rule = current_app.add_url_rule(
                    flask_path,
                    endpoint=endpoint,
                    view_func=make_view(raml_path, http_method),
                    methods=[method_upper],
                )
                rules.append(rule)
        
        return rules


class RamlAutoApi(object):
    """Auto-register Flask routes from RAML spec with per-route handlers.
    
    Usage:
        api = RamlAutoApi(app, parse("api.raml"))
        
        @api.route("/users", "GET")
        def get_users(validated_data):
            return jsonify({"users": []})
        
        @api.route("/users/{userId}", "GET")
        def get_user(validated_data):
            return jsonify({"user": {...}})
        
        api.register_routes()
    """
    
    def __init__(self, app=None, api_spec=None):
        self.api_spec = api_spec
        self._handlers = {}
        if app is not None:
            self.init_app(app, api_spec)
    
    def init_app(self, app, api_spec=None):
        """Initialize the extension with a Flask app."""
        if api_spec:
            self.api_spec = api_spec
        app.extensions['ramlpy_auto'] = self
    
    def route(self, path, method):
        """Decorator to register a handler for a specific RAML path+method."""
        key = (path, method.lower())
        def decorator(fn):
            self._handlers[key] = fn
            return fn
        return decorator
    
    def register_routes(self, app=None):
        """Register all Flask routes for handlers that have been defined.
        
        Only registers routes for which a handler has been decorated.
        """
        if app is None:
            from flask import current_app
            app = current_app
        
        rules = []
        for (raml_path, http_method), handler in self._handlers.items():
            flask_path = _raml_path_to_flask(raml_path)
            method_upper = http_method.upper()
            endpoint = "%s_%s" % (http_method, raml_path.strip("/").replace("/", "_"))
            
            def make_view(raml_p, method_m, handler_fn):
                def view(**path_params):
                    result = self.api_spec.validate_request(
                        path=raml_p,
                        method=method_m,
                        path_params=path_params,
                        query_params=request.args.to_dict(flat=True),
                        headers=dict(request.headers),
                        body=request.get_json(silent=True),
                        content_type=request.content_type,
                    )
                    if not result.ok:
                        return jsonify({"errors": result.errors}), 400
                    g.raml_validated = result.data
                    request.raml = type("RamlContext", (), {"validated": result.data})()
                    return handler_fn(result.data)
                return view
            
            app.add_url_rule(
                flask_path,
                endpoint=endpoint,
                view_func=make_view(raml_path, http_method, handler),
                methods=[method_upper],
            )
        
        return rules
