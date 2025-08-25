import json
from typing import Any

from jsonschema import Draft202012Validator, validate


def validate_props(type_schema_json: str, props: dict[str, Any]) -> None:
    """
    Validate entry props against HobbyType schema_json using JSON Schema Draft 2020-12.
    
    Args:
        type_schema_json: JSON Schema string from HobbyType.schema_json
        props: Dictionary of property key-value pairs to validate
        
    Raises:
        ValidationError: If props don't match the schema
        ValueError: If schema_json is invalid JSON
    """
    try:
        schema = json.loads(type_schema_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON Schema: {e}")

    # Use Draft 2020-12 validator
    validator = Draft202012Validator(schema)

    # Validate the schema itself first
    Draft202012Validator.check_schema(schema)

    # Validate props against schema
    validate(instance=props, schema=schema, cls=Draft202012Validator)


def is_valid_json_schema(schema_json: str) -> bool:
    """
    Check if a string is valid JSON Schema.
    
    Args:
        schema_json: JSON Schema string to validate
        
    Returns:
        bool: True if valid JSON Schema, False otherwise
    """
    try:
        schema = json.loads(schema_json)
        Draft202012Validator.check_schema(schema)
        return True
    except (json.JSONDecodeError, Exception):
        return False
