"""Framework-agnostic RAML validation engine."""

from ramlpy.exceptions import RamlValidationError
from ramlpy.path_match import match_raml_path
from ramlpy.validator.errors import ValidationIssue, ValidationResult
from ramlpy.validator.jsonschema_support import validate_with_jsonschema
from ramlpy.validator.media_type import resolve_body_spec
from ramlpy.validator.scalars import coerce_scalar


def _header_raw_value(headers, name):
    """Return header value matching *name* (HTTP headers are case-insensitive)."""
    if not headers:
        return None
    if name in headers:
        return headers[name]
    want = name.lower()
    for key, value in headers.items():
        if key.lower() == want:
            return value
    return None


def resolve_route(api_spec, path, method):
    """Find resource and method for *path*; resolve template match to path param strings.

    Accepts either a RAML template path (e.g. ``/users/{id}``) or a concrete request path
    (e.g. ``/users/5``).

    Returns:
        tuple: (ResourceSpec or None, MethodSpec or None, extracted path params dict)
    """
    method_l = method.lower()
    for resource in api_spec.iter_resources():
        if method_l not in resource.methods:
            continue
        if resource.full_path == path:
            return resource, resource.methods[method_l], {}
    candidates = []
    for resource in api_spec.iter_resources():
        if method_l not in resource.methods:
            continue
        matched, extracted = match_raml_path(resource.full_path, path)
        if matched:
            candidates.append((len(resource.full_path), resource, extracted))
    if not candidates:
        return None, None, {}
    candidates.sort(key=lambda x: -x[0])
    _, resource, extracted = candidates[0]
    return resource, resource.methods[method_l], extracted


def _resolve_type_spec(api_spec, type_ref):
    """Resolve a type reference to its TypeSpec.
    
    Args:
        api_spec: The ApiSpec containing the types registry
        type_ref: TypeRef or string type name
    
    Returns:
        TypeSpec or None
    """
    if type_ref is None or isinstance(type_ref, dict):
        return None
    
    name = type_ref.name if hasattr(type_ref, 'name') else type_ref
    return api_spec.types.get(name)


def _parse_complex_type_string(api_spec, t_str, visited):
    """Helper to parse complex RAML generic strings like 'Employee[]' or 'A | B' into JSON Schema."""
    if '|' in t_str:
        types = [t.strip() for t in t_str.split('|')]
        return {"anyOf": [_parse_complex_type_string(api_spec, t, visited.copy()) for t in types]}
    elif t_str.endswith('[]'):
        base_t = t_str[:-2]
        return {"type": "array", "items": _parse_complex_type_string(api_spec, base_t, visited.copy())}
    elif t_str in api_spec.types:
        type_spec = api_spec.types[t_str]
        if type_spec.name not in visited:
            visited.add(type_spec.name)
            return _build_json_schema_from_type(api_spec, type_spec, visited.copy())
        else:
            return {}
    else:
        return {"type": _raml_type_to_json_type(t_str)}


def _build_json_schema_from_type(api_spec, type_spec, visited=None):
    """Build a JSON Schema from a TypeSpec for validation.
    
    Args:
        api_spec: The ApiSpec for resolving type references
        type_spec: The TypeSpec to convert
        visited: Set of already-visited type names (for circular ref detection)
    
    Returns:
        dict: JSON Schema dict
    """
    if type_spec is None:
        return {}
    
    if visited is None:
        visited = set()
    
    # If there's a schema_source (from RAML 0.8 JSON schema), use it directly
    if type_spec.schema_source:
        return type_spec.schema_source
    
    # If there's an inline_definition (from RAML 1.0 inline types), convert it
    if type_spec.inline_definition:
        return _convert_inline_definition(api_spec, type_spec.inline_definition, visited)
    
    # Build schema from type properties (fallback for manually constructed TypeSpec)
    base_t = type_spec.base_type or "object"
    schema = _parse_complex_type_string(api_spec, base_t, visited)
    
    if type_spec.enum:
        schema["enum"] = type_spec.enum
    
    if type_spec.base_type == "object" and type_spec.properties:
        schema["properties"] = {}
        required = []
        
        for prop_name, prop_def in type_spec.properties.items():
            if isinstance(prop_def, dict):
                if prop_def.get("required"):
                    required.append(prop_name)
                prop_schema = _convert_property_dict(api_spec, prop_def, visited.copy())
            else:
                prop_schema = _scalar_type_to_schema(prop_def)
            schema["properties"][prop_name] = prop_schema
        
        if required:
            schema["required"] = required
    
    elif type_spec.base_type == "array" and type_spec.items:
        items_type_spec = _resolve_type_spec(api_spec, type_spec.items)
        if items_type_spec:
            schema["items"] = _build_json_schema_from_type(api_spec, items_type_spec, visited.copy())
        elif isinstance(type_spec.items, str):
            items_type_spec = _resolve_type_spec(api_spec, type_spec.items)
            if items_type_spec:
                schema["items"] = _build_json_schema_from_type(api_spec, items_type_spec, visited.copy())
            else:
                schema["items"] = _scalar_type_to_schema(type_spec.items)
        else:
            schema["items"] = _scalar_type_to_schema(type_spec.items)
    
    # Add facets from the type itself
    schema = _add_facets_to_schema(schema, type_spec)
    
    return schema


def _convert_inline_definition(api_spec, definition, visited):
    """Convert an inline definition dict to JSON Schema."""
    if not isinstance(definition, dict):
        return _scalar_type_to_schema(definition)
    
    # Check if it has a 'type' key that references a named type
    type_val = definition.get("type")
    if isinstance(type_val, str) and type_val in api_spec.types:
        type_spec = api_spec.types[type_val]
        if type_spec.name not in visited:
            visited.add(type_spec.name)
            return _build_json_schema_from_type(api_spec, type_spec, visited.copy())
        else:
            return {}  # Circular reference, skip
    
    # It's an object definition with properties
    schema = {}
    
    if "type" in definition:
        type_val = definition["type"]
        
        if isinstance(type_val, str):
            parsed_schema = _parse_complex_type_string(api_spec, type_val, visited)
            if "anyOf" in parsed_schema:
                schema.update(parsed_schema)
            elif "type" in parsed_schema and parsed_schema["type"] == "array":
                schema.update(parsed_schema)
            else:
                schema.update(parsed_schema)
        else:
            schema["type"] = type_val
    
    if "properties" in definition:
        schema["properties"] = {}
        required = []
        for prop_name, prop_def in definition["properties"].items():
            if isinstance(prop_def, dict) and prop_def.get("required"):
                required.append(prop_name)
            schema["properties"][prop_name] = _convert_property_dict(api_spec, prop_def, visited.copy())
        if required:
            schema["required"] = required
    
    if "items" in definition:
        items_val = definition["items"]
        if isinstance(items_val, str) and items_val in api_spec.types:
            items_type_spec = api_spec.types[items_val]
            if items_type_spec.name not in visited:
                visited.add(items_type_spec.name)
                schema["items"] = _build_json_schema_from_type(api_spec, items_type_spec, visited.copy())
            else:
                schema["items"] = {}
        elif isinstance(items_val, dict):
            schema["items"] = _convert_property_dict(api_spec, items_val, visited.copy())
        else:
            schema["items"] = _scalar_type_to_schema(items_val)
    
    # Copy over facet constraints
    for facet in ["minimum", "maximum", "minLength", "maxLength", "pattern", 
                  "enum", "minItems", "maxItems", "default"]:
        if facet in definition:
            schema[facet] = definition[facet]
    
    return schema


def _convert_property_dict(api_spec, prop_def, visited):
    """Convert a property definition dict to JSON Schema."""
    if isinstance(prop_def, str):
        return _parse_complex_type_string(api_spec, prop_def, visited)
    
    if not isinstance(prop_def, dict):
        return _scalar_type_to_schema(prop_def)
    
    type_val = prop_def.get("type")
    
    if isinstance(type_val, str) and type_val in api_spec.types:
        type_spec = api_spec.types[type_val]
        if type_spec.name not in visited:
            visited.add(type_spec.name)
            return _build_json_schema_from_type(api_spec, type_spec, visited.copy())
        else:
            return {}
    
    schema = {}
    if isinstance(type_val, str):
        parsed_schema = _parse_complex_type_string(api_spec, type_val, visited)
        schema.update(parsed_schema)
    elif type_val is not None:
        schema["type"] = type_val
    
    # Handle nested items for arrays
    if "items" in prop_def:
        items_val = prop_def["items"]
        if isinstance(items_val, str) and items_val in api_spec.types:
            items_type_spec = api_spec.types[items_val]
            if items_type_spec.name not in visited:
                visited.add(items_type_spec.name)
                schema["items"] = _build_json_schema_from_type(api_spec, items_type_spec, visited.copy())
            else:
                schema["items"] = {}
        elif isinstance(items_val, dict):
            schema["items"] = _convert_property_dict(api_spec, items_val, visited.copy())
        else:
            schema["items"] = _scalar_type_to_schema(items_val)
    
    # Handle nested properties for objects
    if "properties" in prop_def:
        schema["properties"] = {}
        required = []
        for pname, pdef in prop_def["properties"].items():
            if isinstance(pdef, dict):
                if pdef.get("required"):
                    required.append(pname)
                schema["properties"][pname] = _convert_property_dict(api_spec, pdef, visited.copy())
            else:
                schema["properties"][pname] = _scalar_type_to_schema(pdef)
        if required:
            schema["required"] = required
    
    # Copy facets
    for facet in ["minimum", "maximum", "minLength", "maxLength", "pattern",
                  "enum", "minItems", "maxItems", "default"]:
        if facet in prop_def:
            schema[facet] = prop_def[facet]
    
    return schema


def _raml_type_to_json_type(raml_type):
    """Convert a RAML type name to a JSON Schema type."""
    type_map = {
        "string": "string",
        "integer": "integer",
        "int": "integer",
        "number": "number",
        "float": "number",
        "double": "number",
        "boolean": "boolean",
        "bool": "boolean",
        "date": "string",
        "datetime": "string",
        "time": "string",
        "file": "string",
        "any": None,
        "nil": "null",
        "null": "null",
        "object": "object",
        "array": "array",
    }
    return type_map.get(raml_type.lower(), raml_type)


def _scalar_type_to_schema(type_ref):
    """Convert a scalar type reference to a JSON Schema type."""
    type_map = {
        "string": {"type": "string"},
        "integer": {"type": "integer"},
        "int": {"type": "integer"},
        "number": {"type": "number"},
        "float": {"type": "number"},
        "double": {"type": "number"},
        "boolean": {"type": "boolean"},
        "bool": {"type": "boolean"},
        "date": {"type": "string", "format": "date"},
        "datetime": {"type": "string", "format": "date-time"},
        "time": {"type": "string", "format": "time"},
        "file": {"type": "string"},
        "any": {},
        "nil": {"type": "null"},
        "null": {"type": "null"},
    }
    name = type_ref.name if hasattr(type_ref, 'name') else type_ref
    return type_map.get(name.lower(), {})


def _add_facets_to_schema(schema, spec):
    """Add validation facets from a spec to the JSON Schema."""
    if spec is None:
        return schema
    
    facets = getattr(spec, 'facets', {}) or {}
    
    # Direct attributes on ParameterSpec/TypeSpec
    for attr in ['minimum', 'maximum', 'minLength', 'maxLength', 
                 'min_length', 'max_length', 'pattern', 'enum',
                 'minItems', 'maxItems', 'min_items', 'max_items']:
        val = getattr(spec, attr, None)
        if val is not None and val != [] and val != "":
            json_attr = attr.replace('_', '')
            if json_attr == 'minlength':
                json_attr = 'minLength'
            elif json_attr == 'maxlength':
                json_attr = 'maxLength'
            elif json_attr == 'minitems':
                json_attr = 'minItems'
            elif json_attr == 'maxitems':
                json_attr = 'maxItems'
            schema[json_attr] = val
    
    # Facets dict
    if facets:
        facet_map = {
            'minimum': 'minimum',
            'maximum': 'maximum',
            'minLength': 'minLength',
            'maxLength': 'maxLength',
            'min_length': 'minLength',
            'max_length': 'maxLength',
            'pattern': 'pattern',
            'enum': 'enum',
            'minItems': 'minItems',
            'maxItems': 'maxItems',
            'min_items': 'minItems',
            'max_items': 'maxItems',
        }
        for facet_key, json_key in facet_map.items():
            if facet_key in facets:
                schema[json_key] = facets[facet_key]
    
    return schema


def _validate_body(api_spec, method_spec, body, content_type):
    """Validate request body against the method's body schema.
    
    Args:
        api_spec: The ApiSpec containing types registry
        method_spec: The MethodSpec for the request
        body: The request body to validate
        content_type: The Content-Type of the request
    
    Returns:
        list: List of ValidationIssue dicts
    """
    if body is None:
        return []

    body_spec = resolve_body_spec(method_spec.bodies, content_type)

    if body_spec is None:
        return []
    
    # Get the type reference from the body spec
    type_ref = body_spec.type_ref
    
    if isinstance(type_ref, dict):
        schema = _convert_inline_definition(api_spec, type_ref, set())
        if not schema:
            return []
        return [issue.as_dict() for issue in validate_with_jsonschema(schema, body, "#/body")]
    
    # Resolve the type
    type_spec = _resolve_type_spec(api_spec, type_ref)
    
    # If no exact named type is found, it might be an inline composite (e.g., A | B)
    if type_spec is None:
        if isinstance(type_ref, str) and ('|' in type_ref or type_ref.endswith('[]')):
            schema = _convert_inline_definition(api_spec, {"type": type_ref}, set())
        else:
            return []
    else:
        # Build JSON Schema and validate
        schema = _build_json_schema_from_type(api_spec, type_spec)
        
    if not schema:
        return []
    
    return [issue.as_dict() for issue in validate_with_jsonschema(schema, body, "#/body")]


def validate_parameter(param_spec, raw_value, pointer):
    """Validate and coerce a single parameter.
    
    Args:
        param_spec: ParameterSpec to validate against
        raw_value: Raw value from request
        pointer: JSON pointer for error messages
    
    Returns:
        tuple: (coerced_value, ValidationIssue or None)
    """
    if raw_value is None:
        if param_spec.required and param_spec.default is None:
            return None, ValidationIssue(
                code="missing_required",
                message="Missing required parameter '%s'" % param_spec.name,
                pointer=pointer,
                expected=param_spec.type_ref,
                actual=None,
            )
        return param_spec.default, None
    
    try:
        value = coerce_scalar(param_spec.type_ref, raw_value)
    except Exception:
        return None, ValidationIssue(
            code="invalid_type",
            message="Parameter '%s' is not a valid %s" % (
                param_spec.name, param_spec.type_ref
            ),
            pointer=pointer,
            expected=param_spec.type_ref,
            actual=raw_value,
        )
    
    if param_spec.enum and value not in param_spec.enum:
        return None, ValidationIssue(
            code="invalid_enum",
            message="Parameter '%s' must be one of %s" % (
                param_spec.name, param_spec.enum
            ),
            pointer=pointer,
            expected=param_spec.enum,
            actual=value,
        )
    
    return value, None


def _validate_route_inputs(api_spec, resource_spec, method_spec, path_params,
                           query_params, headers, body, content_type):
    """Validate parsed handler inputs for a resolved route."""
    path_params = path_params or {}
    query_params = query_params or {}
    headers = headers or {}

    errors = []
    validated = {
        "path_params": {},
        "query_params": {},
        "headers": {},
        "body": body,
    }

    for name, spec in resource_spec.uri_parameters.items():
        value, error = validate_parameter(
            spec, path_params.get(name), "path.%s" % name
        )
        if error:
            errors.append(error.as_dict())
        else:
            validated["path_params"][name] = value

    for name, spec in method_spec.query_parameters.items():
        value, error = validate_parameter(
            spec, query_params.get(name), "query.%s" % name
        )
        if error:
            errors.append(error.as_dict())
        else:
            validated["query_params"][name] = value

    for name, spec in method_spec.headers.items():
        value, error = validate_parameter(
            spec, _header_raw_value(headers, name), "headers.%s" % name
        )
        if error:
            errors.append(error.as_dict())
        else:
            validated["headers"][name] = value

    errors.extend(_validate_body(api_spec, method_spec, body, content_type))
    return ValidationResult(ok=(len(errors) == 0), data=validated, errors=errors)


class RouteValidator(object):
    """Reusable validator bound to a specific RAML route and method."""

    def __init__(self, api_spec, resource_spec, method_spec):
        self.api_spec = api_spec
        self.resource_spec = resource_spec
        self.method_spec = method_spec
        self.path = resource_spec.full_path
        self.method = method_spec.method

    def validate(self, path_params=None, query_params=None, headers=None,
                 body=None, content_type=None):
        """Validate parsed request values and return a ValidationResult."""
        return _validate_route_inputs(
            self.api_spec,
            self.resource_spec,
            self.method_spec,
            path_params=path_params,
            query_params=query_params,
            headers=headers,
            body=body,
            content_type=content_type,
        )

    def validate_or_raise(self, path_params=None, query_params=None, headers=None,
                          body=None, content_type=None):
        """Validate parsed request values and raise on failure."""
        result = self.validate(
            path_params=path_params,
            query_params=query_params,
            headers=headers,
            body=body,
            content_type=content_type,
        )
        if not result.ok:
            raise RamlValidationError(
                "RAML validation failed for %s %s" % (
                    self.method.upper(), self.path
                ),
                errors=result.errors,
            )
        return result.data

    def validate_body(self, body, content_type=None):
        """Validate only the request body for this route."""
        return self.validate(body=body, content_type=content_type)

    def validate_body_or_raise(self, body, content_type=None):
        """Validate only the request body and return the validated payload."""
        return self.validate_or_raise(body=body, content_type=content_type)["body"]

    def __repr__(self):
        return "RouteValidator(path=%r, method=%r)" % (self.path, self.method)
