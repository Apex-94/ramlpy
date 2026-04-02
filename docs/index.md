# ramlpy Documentation

Welcome to the ramlpy documentation! ramlpy is a modern Python library for parsing and validating RAML 0.8 and 1.0 files, designed for Flask-based REST API integrations.

## Getting Help

- **Quick start**: New to ramlpy? Start with the [Getting Started Guide](getting-started/index.md)
- **Tutorials**: Follow our step-by-step [Tutorial](getting-started/tutorial.md) to build your first validated API
- **How-to guides**: Need to accomplish a specific task? Check our [How-to guides](how-to/index.md)
- **Reference**: Looking for API details? See the [Reference](reference/index.md)
- **Examples**: Want to see real-world usage? Browse our [Examples](examples/index.md)

## Documentation Structure

This documentation is organized into four main sections, following the [Diataxis framework](https://diataxis.fr/):

### [Getting Started](getting-started/index.md)
Tutorials that guide you through learning ramlpy by doing. These are designed for newcomers who want to learn by building.

- [Installation](getting-started/installation.md)
- [Quick Start](getting-started/quickstart.md)
- [Tutorial: Building a Validated API](getting-started/tutorial.md)

### [How-to Guides](how-to/index.md)
Practical guides that show you how to solve specific problems.

- [How to validate request parameters](how-to/validate-parameters.md)
- [How to validate request bodies](how-to/validate-bodies.md)
- [How to use RAML includes](how-to/use-includes.md)
- [How to integrate with Flask](how-to/flask-integration.md)
- [How to handle validation errors](how-to/handle-errors.md)
- [How to use the CLI](how-to/use-cli.md)

### [Reference](reference/index.md)
Technical descriptions of the library's components.

- [API Reference](reference/api.md)
- [Model Classes](reference/models.md)
- [Validation Engine](reference/validation.md)
- [Include Resolution](reference/includes.md)
- [Exceptions](reference/exceptions.md)

### [Topics](topics/index.md)
In-depth explanations of key concepts and design decisions.

- [Architecture Overview](topics/architecture.md)
- [RAML 0.8 vs 1.0](topics/raml-versions.md)
- [Type Coercion](topics/type-coercion.md)
- [Python Version Compatibility](topics/python-compatibility.md)

### [Examples](examples/index.md)
Real-world examples and use cases.

- [Simple User API (RAML 0.8)](examples/simple-08.md)
- [Product API with Types (RAML 1.0)](examples/simple-10.md)
- [Complex Orders API](examples/complex-08.md)
- [Modular Library Pattern](examples/modular-10.md)

## Test Coverage

All 77 tests pass successfully:

```
======================== 77 passed, 0 skipped in 1.68s =========================
```

This includes tests for:
- Version detection (6 tests)
- Parser integration (18 tests)
- RAML examples fixtures (35 tests)
- Validation engine (12 tests)
- Scalar coercion (6 tests)

## Version Information

- **Current version**: 0.1.0
- **Python support**: 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14
- **RAML support**: 0.8, 1.0
