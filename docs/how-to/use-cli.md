# How to use the CLI

This guide shows you how to use the ramlpy-ng command-line interface.

## Basic Usage

The `ramlpy-ng` CLI provides three main commands: `parse`, `validate`, and `info`.

### Parse a RAML File

To parse a RAML file and display its structure:

```bash
ramlpy-ng parse api.raml
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
ramlpy-ng parse api.raml --json
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
ramlpy-ng validate api.raml
```

Output:
```
RAML file is valid.
Title: User Management API
Version: v1
Resources: 2
```

### Show API Information

To display detailed information about the API:

```bash
ramlpy-ng info api.raml
```

Output:
```
Title: User Management API
Version: v1
Base URI: https://api.example.com/{version}
Media Type: application/json
Resources: 2
  /users
    - GET
    - POST
  /users/{userId}
    - GET
Types: User, NewUser
```

As JSON:
```bash
ramlpy-ng info api.raml --json
```

## Error Messages

If the RAML file has errors, the CLI will display them:

```bash
ramlpy-ng validate invalid.raml
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

ramlpy-ng validate "$1"
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
ramlpy-ng --help
```

Output:
```
usage: ramlpy [-h] {parse,validate,info} ...

RAML parser and validator

positional arguments:
  {parse,validate,info}
                        Command to run
    parse               Parse a RAML file
    validate            Validate a RAML file
    info                Show API information

optional arguments:
  -h, --help            show this help message and exit
```
