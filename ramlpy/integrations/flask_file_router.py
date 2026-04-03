"""Flask auto-router that dispatches RAML routes to handler functions in a single file."""

import os
import re
import importlib.util
from functools import wraps

try:
    from flask import request, jsonify, g, current_app
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


def _raml_path_to_flask(path):
    """Convert a RAML path like /users/{userId} to Flask route /users/<userId>."""
    return re.sub(r'\{(\w+)\}', r'<\1>', path)


def _path_to_func_name(path, method):
    """Convert a RAML path+method to a handler function name.
    
    /users + GET -> users_get
    /users/{userId} + GET -> users_userId_get
    /users/{userId}/orders/{orderId} + POST -> users_userId_orders_orderId_post
    """
    parts = path.strip("/").split("/")
    cleaned = []
    for part in parts:
        # Remove { } from path params
        part = part.strip("{}")
        cleaned.append(part)
    cleaned.append(method.lower())
    return "_".join(cleaned)


class RamlFileRouter(object):
    """Auto-register Flask routes from RAML spec, dispatching to functions in a handlers file.
    
    Convention: A single handlers.py file defines functions named by path+method:
        def users_get(validated_data): ...
        def users_userId_get(validated_data): ...
        def users_post(validated_data): ...
    
    Usage:
        from ramlpy import parse
        from ramlpy.integrations.flask_file_router import RamlFileRouter
        
        app = Flask(__name__)
        router = RamlFileRouter(app, parse("api.raml"), handlers_file="handlers.py")
        router.register_routes()
    """
    
    def __init__(self, app=None, api_spec=None, handlers_file=None):
        self.api_spec = api_spec
        self.handlers_file = handlers_file
        self._handlers_module = None
        if app is not None:
            self.init_app(app, api_spec, handlers_file)
    
    def init_app(self, app, api_spec=None, handlers_file=None):
        """Initialize with Flask app, API spec, and handlers file path."""
        if api_spec:
            self.api_spec = api_spec
        if handlers_file:
            self.handlers_file = handlers_file
        app.extensions['ramlpy_file_router'] = self
    
    def _load_handlers(self):
        """Load the handlers module from file."""
        if self._handlers_module is not None:
            return self._handlers_module
        
        if not self.handlers_file:
            raise RuntimeError("handlers_file must be set before calling register_routes()")
        
        if not os.path.isfile(self.handlers_file):
            raise FileNotFoundError("Handlers file not found: %s" % self.handlers_file)
        
        spec = importlib.util.spec_from_file_location("raml_handlers", self.handlers_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self._handlers_module = module
        return module
    
    def _find_handler(self, path, method):
        """Find the handler function for a given path and method.
        
        Tries:
        1. <path_segments>_<method>  (e.g., users_userId_get)
        2. <method>_<path_segments>  (e.g., get_users_userId)
        3. handle_<path_segments>_<method>
        """
        module = self._load_handlers()
        
        # Build function name candidates
        parts = path.strip("/").split("/")
        path_key = "_".join(p.strip("{}") for p in parts)
        
        candidates = [
            path_key + "_" + method.lower(),       # users_userId_get
            method.lower() + "_" + path_key,       # get_users_userId
            "handle_" + path_key + "_" + method.lower(),  # handle_users_userId_get
        ]
        
        for name in candidates:
            func = getattr(module, name, None)
            if func is not None and callable(func):
                return func
        
        return None
    
    def register_routes(self, app=None):
        """Register all Flask routes by dispatching to handler functions.
        
        Returns:
            list: List of registered route info dicts
        """
        if app is None:
            app = current_app
        
        if self.api_spec is None:
            raise RuntimeError("api_spec must be set before calling register_routes()")
        
        # Load handlers to validate
        self._load_handlers()
        
        registered = []
        
        for resource in self.api_spec.resources:
            raml_path = resource.full_path
            flask_path = _raml_path_to_flask(raml_path)
            
            for http_method in resource.methods:
                method_lower = http_method.lower()
                method_upper = http_method.upper()
                
                # Find handler function
                handler_func = self._find_handler(raml_path, method_lower)
                if handler_func is None:
                    continue
                
                endpoint = "%s_%s" % (method_lower, raml_path.strip("/").replace("/", "_"))
                
                def make_view(raml_p, method_m, handler_fn):
                    @wraps(handler_fn)
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
                    view_func=make_view(raml_path, method_lower, handler_func),
                    methods=[method_upper],
                )
                
                registered.append({
                    "path": raml_path,
                    "method": method_upper,
                    "handler": handler_func.__name__,
                    "flask_path": flask_path,
                })
        
        return registered
    
    def list_routes(self):
        """List all routes and their handler function status."""
        if self.api_spec is None:
            return []
        
        routes = []
        for resource in self.api_spec.resources:
            raml_path = resource.full_path
            for http_method in resource.methods:
                handler = self._find_handler(raml_path, http_method.lower())
                routes.append({
                    "path": raml_path,
                    "method": http_method.upper(),
                    "handler": handler.__name__ if handler else None,
                    "found": handler is not None,
                })
        return routes
