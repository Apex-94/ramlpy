# RAML Example Pack

This pack contains simple and complex RAML samples for both RAML 0.8 and RAML 1.0.

## Included examples

1. `simple-08/api.raml`
   - Basic RAML 0.8 API
   - URI params, query params, JSON schema body, responses

2. `simple-08-with-types/api.raml`
   - RAML 0.8 API using an external shared `types.raml` file under the root `schemas` node
   - Mirrors the 0.8 spec pattern where reusable schemas are externalized and included with `!include`

3. `complex-08-with-types/api.raml`
   - RAML 0.8 API with external shared `types.raml`, plus external `resourceTypes` and `traits`
   - Useful for parser tests around includes, schema references, and parameterized resource types

4. `simple-10-inline/api.raml`
   - Basic RAML 1.0 API
   - Inline `types`, request/response bodies, enums, examples

5. `simple-10-with-types/api.raml`
   - RAML 1.0 API that imports reusable types from `types.raml`

6. `complex-10-with-types/api.raml`
   - More advanced RAML 1.0 API
   - `uses`, traits, resource types, security schemes, nested resources, reusable types in `types.raml`

7. `modular-10-library/api.raml`
   - RAML 1.0 API using `uses` with a standalone library fragment
   - Demonstrates library namespaces and cross-file type references

## Notes

- RAML 0.8 does **not** have RAML 1.0-style root `types`; it uses `schemas` and `!include` instead.
- RAML 1.0 supports both reusable `types` and modular `Library` fragments via `uses`.
