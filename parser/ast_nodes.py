"""AST node classes for RAML parsing."""


class AstNode(object):
    """Base AST node."""
    pass


class DocumentNode(AstNode):
    """Root document node."""
    def __init__(self, version, data):
        self.version = version
        self.data = data


class ResourceNode(AstNode):
    """Resource node."""
    def __init__(self, path, methods=None, nested_resources=None,
                 uri_parameters=None, traits=None):
        self.path = path
        self.methods = methods or []
        self.nested_resources = nested_resources or []
        self.uri_parameters = uri_parameters or {}
        self.traits = traits or []


class MethodNode(AstNode):
    """HTTP method node."""
    def __init__(self, method, headers=None, query_parameters=None,
                 body=None, responses=None, secured_by=None,
                 description=None, traits=None):
        self.method = method
        self.headers = headers or {}
        self.query_parameters = query_parameters or {}
        self.body = body
        self.responses = responses or {}
        self.secured_by = secured_by or []
        self.description = description
        self.traits = traits or []


class ParameterNode(AstNode):
    """Parameter node."""
    def __init__(self, name, type_name=None, required=None, default=None,
                 enum=None, pattern=None, minimum=None, maximum=None,
                 min_length=None, max_length=None, repeat=None, **kwargs):
        self.name = name
        self.type_name = type_name
        self.required = required
        self.default = default
        self.enum = enum
        self.pattern = pattern
        self.minimum = minimum
        self.maximum = maximum
        self.min_length = min_length
        self.max_length = max_length
        self.repeat = repeat
        self.extra = kwargs


class BodyNode(AstNode):
    """Body specification node."""
    def __init__(self, media_type, schema=None, example=None,
                 examples=None, type_ref=None):
        self.media_type = media_type
        self.schema = schema
        self.example = example
        self.examples = examples or {}
        self.type_ref = type_ref
