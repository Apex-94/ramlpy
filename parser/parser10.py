"""RAML 1.0 parser."""

from ramlpy.parser.base import BaseParser
from ramlpy.parser.ast_nodes import (
    DocumentNode, ResourceNode, MethodNode,
    ParameterNode, BodyNode
)
from ramlpy.loader.yaml_loader import load_yaml


class Raml10Parser(BaseParser):
    """Parser for RAML 1.0 files."""
    
    def parse(self, text):
        """Parse RAML 1.0 text into AST."""
        data = load_yaml(text)
        return self._parse_document(data)
    
    def _parse_document(self, data):
        """Parse the root document."""
        if data is None:
            data = {}
        resources = []
        for key, value in data.items():
            if key.startswith('/'):
                resources.append(self._parse_resource(key, value))
        
        return DocumentNode(version='1.0', data={
            'title': data.get('title'),
            'version': data.get('version'),
            'baseUri': data.get('baseUri'),
            'mediaType': data.get('mediaType'),
            'protocols': data.get('protocols', []),
            'types': data.get('types', {}),
            'resources': resources,
            'traits': data.get('traits', {}),
            'resourceTypes': data.get('resourceTypes', {}),
            'securitySchemes': data.get('securitySchemes', {}),
            'uses': data.get('uses', {}),
            'annotationTypes': data.get('annotationTypes', {}),
        })
    
    def _parse_resource(self, path, data):
        """Parse a resource."""
        if data is None:
            data = {}
        methods = []
        nested = []
        uri_params = data.get('uriParameters', {})
        
        for key, value in (data or {}).items():
            if key.startswith('/'):
                nested.append(self._parse_resource(key, value))
            elif key.startswith('/') is False and key not in (
                'uriParameters', 'displayName', 'description', 'is', 'type',
                'annotations'
            ):
                methods.append(self._parse_method(key, value))
        
        return ResourceNode(
            path=path,
            methods=methods,
            nested_resources=nested,
            uri_parameters=self._parse_parameters(uri_params),
            traits=data.get('is', []),
        )
    
    def _parse_method(self, method, data):
        """Parse an HTTP method."""
        if data is None:
            data = {}
        
        headers = data.get('headers', {})
        query_params = data.get('queryParameters', {})
        body = data.get('body', {})
        responses = data.get('responses', {})
        
        return MethodNode(
            method=method,
            headers=self._parse_parameters(headers),
            query_parameters=self._parse_parameters(query_params),
            body=self._parse_body(body) if body else None,
            responses=responses,
            secured_by=data.get('securedBy', []),
            description=data.get('description'),
        )
    
    def _parse_parameters(self, params):
        """Parse parameter definitions."""
        result = []
        if not params:
            return result
        for name, spec in params.items():
            # Handle RAML 1.0 shorthand: paramName?: type
            # where name includes '?' to indicate optional
            if spec is None:
                spec = {}
            elif isinstance(spec, str):
                # Shorthand syntax: just a type name
                # Extract required from name (trailing ?)
                is_required = not name.endswith('?')
                clean_name = name.rstrip('?')
                type_name = spec
                result.append(ParameterNode(
                    name=clean_name,
                    type_name=type_name,
                    required=is_required,
                ))
                continue
            
            # Map 'type' key to 'type_name' for ParameterNode
            type_name = spec.pop('type', None)
            result.append(ParameterNode(name=name, type_name=type_name, **spec))
        return result
    
    def _parse_body(self, body):
        """Parse body specification (1.0 style)."""
        if isinstance(body, dict):
            media_types = []
            for mt, spec in body.items():
                if spec is None:
                    spec = {}
                media_types.append(BodyNode(
                    media_type=mt,
                    type_ref=spec.get('type'),
                    schema=spec.get('schema'),
                    example=spec.get('example'),
                    examples=spec.get('examples', {}),
                ))
            return media_types
        return None
