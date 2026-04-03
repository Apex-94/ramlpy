"""Flask auto-router that maps RAML routes to handler files."""

import os
import re
import importlib
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


def _path_to_module_name(path):
    """Convert a RAML path to a Python module name.
    
    /users/{userId}/orders/{orderId}/GET -> users.user_id.orders.order_id.get
    """
    parts = path.strip("/").split("/")
    cleaned = []
    for part in parts:
        # Remove { } from path params and convert to snake_case
        part = part.strip("{}")
        part = re.sub(r'([A-Z])', r'_\1', part).lower().lstrip("_")
        cleaned.append(part)
    return ".".join(cleaned)


def _load_module_from_file(filepath):
    """Load a Python module from a file path."""
    spec = importlib.util.spec_from_file_location("handler_" + os.path.basename(filepath), filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RamlRouter(object):
    """Auto-register Flask routes from RAML spec by scanning handler files.
    
    Convention: Handler files are placed in a handlers directory with structure:
        handlers/
            users/
                get.py          # handles GET /users
                post.py         # handles POST /users
                {userId}/
                    get.py      # handles GET /users/{userId}
                    put.py      # handles PUT /users/{userId}
    
    Each handler file must export a function named `handle` that receives
    validated_data and returns a Flask response.
    
    Usage:
        from ramlpy import parse
        from ramlpy.integrations.flask_router import RamlRouter
        
        app = Flask(__name__)
        router = RamlRouter(app, parse("api.raml"), handlers_dir="handlers")
        router.register_routes()
    """
    
    def __init__(self, app=None, api_spec=None, handlers_dir=None):
        self.api_spec = api_spec
        self.handlers_dir = handlers_dir
        self._handlers = {}
        if app is not None:
            self.init_app(app, api_spec, handlers_dir)
    
    def init_app(self, app, api_spec=None, handlers_dir=None):
        """Initialize with Flask app, API spec, and handlers directory."""
        if api_spec:
            self.api_spec = api_spec
        if handlers_dir:
            self.handlers_dir = handlers_dir
        app.extensions['ramlpy_router'] = self
    
    def _find_handler_file(self, raml_path, method):
        """Find the handler file for a given RAML path and method.
        
        Looks in handlers_dir for:
        1. handlers/<path>/<method>.py
        2. handlers/<path>/handler.py (with handle_<method> function)
        """
        if not self.handlers_dir:
            return None
        
        # Build path: /users/{userId} -> users/{userId}
        path_parts = raml_path.strip("/").split("/")
        handler_dir = os.path.join(self.handlers_dir, *path_parts)
        
        # Try: <method>.py
        method_file = os.path.join(handler_dir, method.lower() + ".py")
        if os.path.isfile(method_file):
            return method_file
        
        # Try: handler.py (with handle_<method> function)
        handler_file = os.path.join(handler_dir, "handler.py")
        if os.path.isfile(handler_file):
            return handler_file
        
        return None
    
    def _load_handler(self, filepath, method):
        """Load a handler function from a file.
        
        For <method>.py files: expects a `handle(validated_data)` function.
        For handler.py files: expects a `handle_<method>(validated_data)` function.
        """
        module = _load_module_from_file(filepath)
        
        # Check if it's a method-specific file
        basename = os.path.basename(filepath)
        if basename.startswith(method.lower()) or basename == method.lower() + ".py":
            func = getattr(module, "handle", None)
            if func is None:
                # Try any callable that's not a dunder
                for name in dir(module):
                    if not name.startswith("_") and name != "handle":
                        obj = getattr(module, name)
                        if callable(obj):
                            func = obj
                            break
            return func
        else:
            # handler.py - look for handle_<method>
            func_name = "handle_" + method.lower()
            func = getattr(module, func_name, None)
            if func is None:
                # Fallback: try `handle`
                func = getattr(module, "handle", None)
            return func
    
    def register_routes(self, app=None):
        """Register all Flask routes by scanning handler files.
        
        Returns:
            list: List of registered route info dicts with path, method, handler_file
        """
        if app is None:
            app = current_app
        
        if self.api_spec is None:
            raise RuntimeError("api_spec must be set before calling register_routes()")
        
        registered = []
        
        for resource in self.api_spec.resources:
            raml_path = resource.full_path
            flask_path = _raml_path_to_flask(raml_path)
            
            for http_method in resource.methods:
                method_upper = http_method.upper()
                method_lower = http_method.lower()
                
                # Find handler file
                handler_file = self._find_handler_file(raml_path, method_lower)
                if handler_file is None:
                    continue
                
                # Load handler function
                handler_func = self._load_handler(handler_file, method_lower)
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
                    "handler_file": handler_file,
                    "flask_path": flask_path,
                })
        
        return registered
    
    def list_routes(self):
        """List all routes and their handler file status.
        
        Returns:
            list: List of dicts with path, method, handler_file, found status
        """
        if self.api_spec is None:
            return []
        
        routes = []
        for resource in self.api_spec.resources:
            raml_path = resource.full_path
            for http_method in resource.methods:
                handler_file = self._find_handler_file(raml_path, http_method)
                routes.append({
                    "path": raml_path,
                    "method": http_method.upper(),
                    "handler_file": handler_file,
                    "found": handler_file is not None,
                })
        return routes
