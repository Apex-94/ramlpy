"""ApiSpec - Top-level normalized RAML API specification."""


class ApiSpec(object):
    """Top-level normalized RAML API specification."""
    
    def __init__(self, title=None, version=None, base_uri=None,
                 media_type=None, resources=None, types=None,
                 traits=None, resource_types=None, security_schemes=None,
                 metadata=None):
        self.title = title
        self.version = version
        self.base_uri = base_uri
        self.media_type = media_type
        self.resources = resources or []
        self.types = types or {}
        self.traits = traits or {}
        self.resource_types = resource_types or {}
        self.security_schemes = security_schemes or {}
        self.metadata = metadata or {}
    
    def iter_resources(self):
        """Yield every resource in document order, including nested resources."""
        for resource in self.resources:
            yield resource
            for nested in self._iter_nested_resources(resource):
                yield nested
    
    @staticmethod
    def _iter_nested_resources(resource):
        for child in resource.nested_resources:
            yield child
            for nested in ApiSpec._iter_nested_resources(child):
                yield nested
    
    def resource(self, path):
        """Get a resource by its full path.
        
        Args:
            path: The full path of the resource
        
        Returns:
            ResourceSpec: The resource at the given path
        
        Raises:
            KeyError: If no resource exists at the given path
        """
        for resource in self.iter_resources():
            if resource.full_path == path:
                return resource
        raise KeyError("Resource not found: %s" % path)

    def validator_for(self, path, method):
        """Create a reusable validator for a specific RAML route and method.

        Args:
            path: RAML resource path template, e.g. ``/users/{id}``
            method: HTTP method

        Returns:
            RouteValidator

        Raises:
            KeyError: If the route or method is not present in the API spec
        """
        resource = self.resource(path)
        method_spec = resource.methods.get(method.lower())
        if method_spec is None:
            raise KeyError("Method not found for route %s: %s" % (path, method))
        from ramlpy.validator.engine import RouteValidator
        return RouteValidator(self, resource, method_spec)
    
    def match_route(self, path, method):
        """Resolve RAML resource and method for a path (template or concrete URL).
        
        Returns:
            tuple: (ResourceSpec, MethodSpec, extracted path param strings) if a route
            matches, or ``(None, None, {})`` if none match.
        """
        from ramlpy.validator.engine import resolve_route
        return resolve_route(self, path, method)
    
    def __repr__(self):
        return "ApiSpec(title=%r, version=%r, base_uri=%r)" % (
            self.title, self.version, self.base_uri
        )
