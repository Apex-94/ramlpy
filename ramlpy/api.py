"""Public API for parsing RAML files."""

from ramlpy.loader.version import detect_raml_version
from ramlpy.loader.include_resolver import IncludeResolver
from ramlpy.parser.parser08 import Raml08Parser
from ramlpy.parser.parser10 import Raml10Parser
from ramlpy.compiler.normalize08 import normalize_raml08
from ramlpy.compiler.normalize10 import normalize_raml10
from ramlpy.exceptions import RamlVersionError


def parse(path):
    """Parse a RAML file and return an ApiSpec.
    
    Args:
        path: Path to RAML file
    
    Returns:
        ApiSpec: Normalized API specification
    
    Raises:
        RamlVersionError: If RAML version is unsupported
        RamlParseError: If file cannot be parsed
    """
    resolver = IncludeResolver(base_path=None)
    content, source = resolver.resolve(path)
    version = detect_raml_version(source.content)
    
    if version == "0.8":
        ast = Raml08Parser(base_path=source.base_path).parse(source.content)
        return normalize_raml08(ast)
    elif version == "1.0":
        ast = Raml10Parser(base_path=source.base_path).parse(source.content)
        return normalize_raml10(ast)
    else:
        raise RamlVersionError("Unsupported RAML version: %s" % version)


def parse_string(text, base_path=None):
    """Parse RAML text and return an ApiSpec.
    
    Args:
        text: RAML content as string
        base_path: Base path for resolving includes
    
    Returns:
        ApiSpec: Normalized API specification
    
    Raises:
        RamlVersionError: If RAML version is unsupported
        RamlParseError: If text cannot be parsed
    """
    version = detect_raml_version(text)
    if version == "0.8":
        ast = Raml08Parser(base_path=base_path).parse(text)
        return normalize_raml08(ast)
    elif version == "1.0":
        ast = Raml10Parser(base_path=base_path).parse(text)
        return normalize_raml10(ast)
    raise RamlVersionError("Unsupported RAML version: %s" % version)
