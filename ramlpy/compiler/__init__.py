"""Compiler module for normalizing AST to shared model."""

from ramlpy.compiler.normalize08 import normalize_raml08
from ramlpy.compiler.normalize10 import normalize_raml10

__all__ = ["normalize_raml08", "normalize_raml10"]
