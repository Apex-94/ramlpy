# How to use the CLI

This guide shows you how to use the ramlpy command-line interface.

## Basic Usage

The `ramlpy` CLI provides two main commands: `parse` and `validate`.

### Parse a RAML File

To parse a RAML file and display its structure:

```bash
ramlpy parse api.raml
```

Output:
```
Title: User Management API
Version: v1
Base URI: https://api.example.com/{version}
Resources:
  /users
    - GET
    - POST
  /users/{userId}
    - GET
```

### Parse as JSON

To output the parsed result as JSON:

```bash
ramlpy parse api.raml --json
```

Output:
```json
{
  "title": "User Management API",
  "version": "v1",
  "base_uri": "https://api.example.com/{version}",
  "resources": ["/users", "/users/{userId}"]
}
```

### Validate a RAML File

To check if a RAML file is valid:

```bash
ramlpy validate api.raml
```

Output:
```
RAML file is valid.
Title: User Management API
Version: v1
Resources: 2
```

## Error Messages

If the RAML file has errors, the CLI will display them:

```bash
ramlpy validate invalid.raml
```

Output:
```
Validation failed: Missing or invalid RAML header
```

## Using in Scripts

The CLI can be used in shell scripts for CI/CD validation:

```bash
#!/bin/bash
# validate-raml.sh

ramlpy validate "$1"
if [ $? -eq 0 ]; then
    echo "RAML validation passed!"
    exit 0
else
    echo "RAML validation failed!"
    exit 1
fi
```

Usage:
```bash
./validate-raml.sh api.raml
```

## Help

To see available commands and options:

```bash
ramlpy --help
```

Output:
```
usage: ramlpy [-h] {parse,validate} ...

RAML parser and validator

positional arguments:
  {parse,validate}  Command to run
    parse           Parse a RAML file
    validate        Validate a RAML file

optional arguments:
  -h, --help        show this help message and exit
```
