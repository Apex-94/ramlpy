"""Loader module for RAML files."""

from ramlpy.loader.version import detect_raml_version
from ramlpy.loader.yaml_loader import load_yaml
from ramlpy.loader.include_resolver import IncludeResolver
from ramlpy.loader.source import Source


def load_and_resolve(path):
    """Load a RAML file and resolve all includes.
    
    Args:
        path: Path to RAML file
    
    Returns:
        tuple: (resolved_content_dict, Source object)
    """
    resolver = IncludeResolver(base_path=None)
    content, source = resolver.resolve(path)
    return content, source


__all__ = [
    "detect_raml_version",
    "load_yaml",
    "IncludeResolver",
    "Source",
    "load_and_resolve",
]
