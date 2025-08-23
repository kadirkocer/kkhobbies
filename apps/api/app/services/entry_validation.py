import json
from typing import Dict, Any, List
import jsonschema
from sqlalchemy.orm import Session
from ..models import HobbyType
from ..schemas import EntryPropBase


def validate_entry_props(
    session: Session,
    type_key: str,
    props: List[EntryPropBase]
) -> Dict[str, Any]:
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
    
    # Validate against schema
    try:
        jsonschema.validate(props_dict, schema)
        return {"valid": True, "errors": []}
    except jsonschema.ValidationError as e:
        return {
            "valid": False,
            "errors": [str(e)]
        }
    except jsonschema.SchemaError as e:
        return {
            "valid": False,
            "errors": [f"Invalid schema: {str(e)}"]
        }