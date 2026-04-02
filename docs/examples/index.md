# Examples

Real-world examples and use cases for ramlpy.

## Available Examples

- [Simple User API (RAML 0.8)](simple-08.md) - Basic RAML 0.8 API with schemas
- [Product API with Types (RAML 1.0)](simple-10.md) - RAML 1.0 with inline types
- [Complex Orders API](complex-08.md) - RAML 0.8 with includes and resource types
- [Modular Library Pattern](modular-10.md) - RAML 1.0 with library namespaces

## Test Fixtures

All examples are tested and verified. The test fixtures are located in:

```
tests/fixtures/raml_examples/
├── simple-08/
├── simple-08-with-types/
├── simple-10-inline/
├── simple-10-with-types/
├── complex-08-with-types/
├── complex-10-with-types/
└── modular-10-library/
```

## Running Example Tests

To run all example tests:

```bash
pytest tests/test_parser/test_raml_examples.py -v
```

All 35 example tests pass successfully.
