import json
from typing import Any

from sqlalchemy.orm import Session

from ..models import HobbyType
from ..schemas import EntryPropBase
from .schema_validation import validate_props


def validate_entry_props(
    session: Session,
    type_key: str,
    props: list[EntryPropBase]
) -> dict[str, Any]:
    """
    Validate entry properties against the hobby type's JSON schema.
    Returns validation result with errors if any.
    """
    # Get the hobby type schema
    hobby_type = session.query(HobbyType).filter(HobbyType.key == type_key).first()
    if not hobby_type:
        return {
            "valid": False,
            "errors": [f"Hobby type '{type_key}' not found"]
        }

    try:
        schema = json.loads(hobby_type.schema_json)
    except json.JSONDecodeError:
        return {
            "valid": False,
            "errors": ["Invalid JSON schema for hobby type"]
        }

    # Convert props to a dictionary for validation
    props_dict = {}
    for prop in props:
        if prop.value_text is not None:
            try:
                # Try to parse as JSON first (for numbers, booleans, etc.)
                props_dict[prop.key] = json.loads(prop.value_text)
            except json.JSONDecodeError:
                # If not JSON, treat as string
                props_dict[prop.key] = prop.value_text

    # Validate against schema using Draft 2020-12
    try:
        validate_props(hobby_type.schema_json, props_dict)
        return {"valid": True, "errors": []}
    except Exception as e:
        return {
            "valid": False,
            "errors": [str(e)]
        }
