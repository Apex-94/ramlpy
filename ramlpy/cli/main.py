"""CLI entry point for RAML validation."""

import sys
import argparse
import json

from ramlpy.api import parse
from ramlpy.exceptions import RamlError


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='ramlpy',
        description='RAML parser and validator',
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse a RAML file')
    parse_parser.add_argument('file', help='RAML file to parse')
    parse_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a RAML file')
    validate_parser.add_argument('file', help='RAML file to validate')
    
    args = parser.parse_args()
    
    if args.command == 'parse':
        cmd_parse(args)
    elif args.command == 'validate':
        cmd_validate(args)
    else:
        parser.print_help()
        sys.exit(1)


def cmd_parse(args):
    """Handle parse command."""
    try:
        api = parse(args.file)
        if getattr(args, 'json', False):
            output = {
                'title': api.title,
                'version': api.version,
                'base_uri': api.base_uri,
                'resources': [r.full_path for r in api.resources],
            }
            print(json.dumps(output, indent=2))
        else:
            print("Title: %s" % api.title)
            print("Version: %s" % api.version)
            print("Base URI: %s" % api.base_uri)
            print("Resources:")
            for resource in api.resources:
                print("  %s" % resource.full_path)
                for method_name in resource.methods:
                    print("    - %s" % method_name.upper())
    except RamlError as e:
        print("Error: %s" % e, file=sys.stderr)
        sys.exit(1)


def cmd_validate(args):
    """Handle validate command."""
    try:
        api = parse(args.file)
        print("RAML file is valid.")
        print("Title: %s" % api.title)
        print("Version: %s" % api.version)
        print("Resources: %d" % len(api.resources))
    except RamlError as e:
        print("Validation failed: %s" % e, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
