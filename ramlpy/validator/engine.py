"""Main validation engine."""

from ramlpy.validator.errors import ValidationIssue, ValidationResult
from ramlpy.validator.scalars import coerce_scalar


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


def validate_request(api_spec, path, method, path_params,
                     query_params, headers, body, content_type):
    """Validate an incoming request against the API spec.
    
    Args:
        api_spec: ApiSpec to validate against
        path: Request path
        method: HTTP method
        path_params: Path parameters dict
        query_params: Query parameters dict
        headers: Request headers dict
        body: Request body
        content_type: Content-Type header value
    
    Returns:
        ValidationResult
    """
    method = method.lower()
    target_resource = None
    target_method = None
    
    for resource in api_spec.resources:
        if resource.full_path == path:
            target_resource = resource
            if method in resource.methods:
                target_method = resource.methods[method]
            break
    
    if target_resource is None or target_method is None:
        return ValidationResult(
            ok=False,
            errors=[ValidationIssue(
                code="route_not_found",
                message="No RAML route found for %s %s" % (method.upper(), path),
                pointer="request",
            ).as_dict()]
        )
    
    errors = []
    validated = {
        "path_params": {},
        "query_params": {},
        "headers": {},
        "body": body,
    }
    
    # Validate path parameters
    for name, spec in target_resource.uri_parameters.items():
        value, error = validate_parameter(spec, path_params.get(name), "path.%s" % name)
        if error:
            errors.append(error.as_dict())
        else:
            validated["path_params"][name] = value
    
    # Validate query parameters
    for name, spec in target_method.query_parameters.items():
        value, error = validate_parameter(spec, query_params.get(name), "query.%s" % name)
        if error:
            errors.append(error.as_dict())
        else:
            validated["query_params"][name] = value
    
    # Validate headers
    for name, spec in target_method.headers.items():
        value, error = validate_parameter(spec, headers.get(name), "headers.%s" % name)
        if error:
            errors.append(error.as_dict())
        else:
            validated["headers"][name] = value
    
    return ValidationResult(ok=(len(errors) == 0), data=validated, errors=errors)
