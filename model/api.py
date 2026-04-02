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
    
    def resource(self, path):
        """Get a resource by its full path.
        
        Args:
            path: The full path of the resource
        
        Returns:
            ResourceSpec: The resource at the given path
        
        Raises:
            KeyError: If no resource exists at the given path
        """
        for resource in self.resources:
            if resource.full_path == path:
                return resource
        raise KeyError("Resource not found: %s" % path)
    
    def validate_request(self, path, method, path_params=None,
                         query_params=None, headers=None, body=None,
                         content_type=None):
        """Validate an incoming request against this API spec.
        
        Args:
            path: Request path
            method: HTTP method
            path_params: Path parameters dict
            query_params: Query parameters dict
            headers: Request headers dict
            body: Request body
            content_type: Content-Type header value
        
        Returns:
            ValidationResult: The validation result
        """
        from ramlpy.validator.engine import validate_request
        return validate_request(
            self,
            path=path,
            method=method,
            path_params=path_params or {},
            query_params=query_params or {},
            headers=headers or {},
            body=body,
            content_type=content_type,
        )
    
    def __repr__(self):
        return "ApiSpec(title=%r, version=%r, base_uri=%r)" % (
            self.title, self.version, self.base_uri
        )
