"""MethodSpec - A RAML HTTP method (GET, POST, etc.) on a resource."""


class MethodSpec(object):
    """A RAML HTTP method (GET, POST, etc.) on a resource."""
    
    def __init__(self, method, headers=None, query_parameters=None,
                 bodies=None, responses=None, secured_by=None,
                 description=None):
        self.method = method.lower()
        self.headers = headers or {}
        self.query_parameters = query_parameters or {}
        self.bodies = bodies or {}
        self.responses = responses or {}
        self.secured_by = secured_by or []
        self.description = description
    
    def __repr__(self):
        return "MethodSpec(method=%r)" % self.method
