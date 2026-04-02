"""Normalize RAML 1.0 AST to shared model."""

from ramlpy.model.api import ApiSpec
from ramlpy.model.resource import ResourceSpec
from ramlpy.model.method import MethodSpec
from ramlpy.model.parameters import ParameterSpec
from ramlpy.model.bodies import BodySpec
from ramlpy.model.types import TypeSpec


def normalize_raml10(ast):
    """Convert RAML 1.0 AST to normalized ApiSpec.
    
    Args:
        ast: DocumentNode from Raml10Parser
    
    Returns:
        ApiSpec: Normalized API specification
    """
    data = ast.data
    
    resources = []
    for resource_node in data.get('resources', []):
        resources.append(_normalize_resource(resource_node))
    
    types = _normalize_types_10(data.get('types', {}))
    traits = data.get('traits', {}) or {}
    resource_types = data.get('resourceTypes', {}) or {}
    security_schemes = data.get('securitySchemes', {}) or {}
    
    return ApiSpec(
        title=data.get('title'),
        version=data.get('version'),
        base_uri=data.get('baseUri'),
        media_type=data.get('mediaType'),
        resources=resources,
        types=types,
        traits=traits,
        resource_types=resource_types,
        security_schemes=security_schemes,
    )


def _normalize_resource(node):
    """Normalize a ResourceNode to ResourceSpec."""
    methods = {}
    for method_node in node.methods:
        spec = _normalize_method(method_node)
        methods[spec.method] = spec
    
    nested = []
    for nested_node in node.nested_resources:
        nested.append(_normalize_resource(nested_node))
    
    uri_params = {}
    for param_node in node.uri_parameters:
        spec = _normalize_parameter(param_node, location='path')
        uri_params[spec.name] = spec
    
    return ResourceSpec(
        full_path=node.path,
        uri_parameters=uri_params,
        methods=methods,
        nested_resources=nested,
    )


def _normalize_method(node):
    """Normalize a MethodNode to MethodSpec."""
    headers = {}
    for param_node in node.headers:
        spec = _normalize_parameter(param_node, location='header')
        headers[spec.name] = spec
    
    query_params = {}
    for param_node in node.query_parameters:
        spec = _normalize_parameter(param_node, location='query')
        query_params[spec.name] = spec
    
    bodies = {}
    if node.body:
        body_list = node.body if isinstance(node.body, list) else [node.body]
        for body_node in body_list:
            spec = BodySpec(
                media_type=body_node.media_type,
                type_ref=body_node.type_ref,
                schema_ref=body_node.schema,
                example=body_node.example,
                examples=body_node.examples,
            )
            bodies[spec.media_type] = spec
    
    return MethodSpec(
        method=node.method,
        headers=headers,
        query_parameters=query_params,
        bodies=bodies,
        responses=node.responses,
        secured_by=node.secured_by,
        description=node.description,
    )


def _normalize_parameter(node, location='query'):
    """Normalize a ParameterNode to ParameterSpec."""
    # Clean up parameter name (remove trailing ?)
    name = node.name.rstrip('?')
    return ParameterSpec(
        name=name,
        location=location,
        required=node.required if node.required is not None else False,
        type_ref=node.type_name or 'string',
        enum=node.enum,
        default=node.default,
        repeat=node.repeat if node.repeat is not None else False,
        pattern=node.pattern,
        minimum=node.minimum,
        maximum=node.maximum,
        min_length=node.min_length,
        max_length=node.max_length,
    )


def _normalize_types_10(types_data):
    """Normalize RAML 1.0 types to TypeSpec dict."""
    types = {}
    if not types_data:
        return types
    for name, type_def in types_data.items():
        if isinstance(type_def, dict):
            types[name] = TypeSpec(
                name=name,
                base_type=type_def.get('type'),
                properties=type_def.get('properties', {}),
                enum=type_def.get('enum', []),
                inline_definition=type_def,
            )
        else:
            types[name] = TypeSpec(
                name=name,
                base_type=type_def,
            )
    return types
