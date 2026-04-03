"""ramlpy - A modern Python library for parsing and validating RAML files."""

try:
    from importlib.metadata import version as _distribution_version
except ImportError:  # Python < 3.8
    _distribution_version = None

from ramlpy.api import parse, parse_string
from ramlpy.exceptions import (
    RamlError,
    RamlParseError,
    RamlValidationError,
    RamlVersionError,
)

if _distribution_version is not None:
    try:
        __version__ = _distribution_version("ramlpy-ng")
    except Exception:
        __version__ = "0.1.2"
else:
    __version__ = "0.1.2"
__all__ = [
    "__version__",
    "parse",
    "parse_string",
    "RamlError",
    "RamlParseError",
    "RamlValidationError",
    "RamlVersionError",
]
