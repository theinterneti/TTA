"""
Serialization utilities for player experience data models.
"""

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, TypeVar

T = TypeVar("T")


class PlayerExperienceEncoder(json.JSONEncoder):
    """Custom JSON encoder for player experience data models."""

    def default(self, o: Any) -> Any:
        """Convert objects to JSON-serializable format."""
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, timedelta):
            return o.total_seconds()

        if isinstance(o, Enum):
            return o.value

        if is_dataclass(o) and not isinstance(o, type):
            return asdict(o)  # type: ignore[arg-type]

        return super().default(o)


def serialize_model(model: Any) -> str:
    """
    Serialize a data model to JSON string.

    Args:
        model: The data model to serialize

    Returns:
        JSON string representation
    """
    return json.dumps(model, cls=PlayerExperienceEncoder, indent=2)


def serialize_model_to_dict(model: Any) -> dict[str, Any] | Any:
    """
    Serialize a data model to dictionary.

    Args:
        model: The data model to serialize

    Returns:
        Dictionary representation or the model itself if not a dataclass
    """
    if is_dataclass(model) and not isinstance(model, type):
        result = asdict(model)  # type: ignore[arg-type]
        return _convert_special_types(result)

    return model


def _convert_special_types(obj: Any) -> Any:
    """Convert special types in nested dictionaries."""
    if isinstance(obj, dict):
        return {key: _convert_special_types(value) for key, value in obj.items()}

    if isinstance(obj, list):
        return [_convert_special_types(item) for item in obj]

    if isinstance(obj, datetime):
        return obj.isoformat()

    if isinstance(obj, timedelta):
        return obj.total_seconds()

    if isinstance(obj, Enum):
        return obj.value

    return obj


def deserialize_model[T](data: str, model_class: type[T]) -> T:
    """
    Deserialize JSON string to data model.

    Args:
        data: JSON string to deserialize
        model_class: The target data model class

    Returns:
        Instance of the data model
    """
    parsed_data = json.loads(data)
    return deserialize_dict_to_model(parsed_data, model_class)


def deserialize_dict_to_model[T](data: dict[str, Any], model_class: type[T]) -> T:
    """
    Deserialize dictionary to data model.

    Args:
        data: Dictionary to deserialize
        model_class: The target data model class

    Returns:
        Instance of the data model
    """
    # Convert datetime strings back to datetime objects
    converted_data = _convert_from_serialized(data, model_class)

    try:
        return model_class(**converted_data)
    except TypeError as e:
        raise ValueError(
            f"Failed to deserialize to {model_class.__name__}: {str(e)}"
        ) from e


def _convert_from_serialized(data: dict[str, Any], model_class: type) -> dict[str, Any]:
    """Convert serialized data back to appropriate types."""
    if not is_dataclass(model_class):
        return data

    # Get field type hints from the model class
    import typing

    type_hints = typing.get_type_hints(model_class)

    converted = {}
    for key, value in data.items():
        if key in type_hints:
            field_type = type_hints[key]
            converted[key] = _convert_field_value(value, field_type)
        else:
            converted[key] = value

    return converted


def _convert_field_value(value: Any, field_type: type) -> Any:
    """Convert a field value to the appropriate type."""
    if value is None:
        return None

    # Handle datetime fields
    if field_type == datetime and isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return value

    # Handle timedelta fields
    if field_type == timedelta and isinstance(value, (int, float)):
        return timedelta(seconds=value)

    # Handle enum fields
    if hasattr(field_type, "__bases__") and Enum in field_type.__bases__:
        if isinstance(value, str):
            try:
                return field_type(value)
            except ValueError:
                return value

    # Handle list fields
    if hasattr(field_type, "__origin__") and field_type.__origin__ is list:
        if isinstance(value, list):
            # Get the list item type
            item_type = field_type.__args__[0] if field_type.__args__ else None
            if item_type:
                return [_convert_field_value(item, item_type) for item in value]

    # Handle dict fields
    if hasattr(field_type, "__origin__") and field_type.__origin__ is dict:
        if isinstance(value, dict):
            return value

    # Handle dataclass fields
    if is_dataclass(field_type) and isinstance(value, dict):
        return deserialize_dict_to_model(value, field_type)

    return value


def create_model_schema(model_class: type) -> dict[str, Any]:
    """
    Create a JSON schema for a data model.

    Args:
        model_class: The data model class

    Returns:
        JSON schema dictionary
    """
    if not is_dataclass(model_class):
        raise ValueError("Model class must be a dataclass")

    import typing

    type_hints = typing.get_type_hints(model_class)

    schema = {"type": "object", "properties": {}, "required": []}

    for field_name, field_type in type_hints.items():
        schema["properties"][field_name] = _get_field_schema(field_type)

        # Check if field has a default value
        if hasattr(model_class, "__dataclass_fields__"):
            field_info = model_class.__dataclass_fields__.get(field_name)
            if field_info and field_info.default == field_info.default_factory is None:
                schema["required"].append(field_name)

    return schema


def _get_field_schema(field_type: type) -> dict[str, Any]:
    """Get JSON schema for a field type."""
    if field_type == str:
        return {"type": "string"}

    if field_type == int:
        return {"type": "integer"}

    if field_type == float:
        return {"type": "number"}

    if field_type == bool:
        return {"type": "boolean"}

    if field_type == datetime:
        return {"type": "string", "format": "date-time"}

    if hasattr(field_type, "__origin__"):
        if field_type.__origin__ is list:
            item_type = field_type.__args__[0] if field_type.__args__ else None
            return {
                "type": "array",
                "items": _get_field_schema(item_type) if item_type else {},
            }

        if field_type.__origin__ is dict:
            return {"type": "object"}

    if (
        hasattr(field_type, "__bases__")
        and isinstance(field_type, type)
        and issubclass(field_type, Enum)
    ):
        return {"type": "string", "enum": [item.value for item in field_type]}

    if is_dataclass(field_type):
        return create_model_schema(field_type)

    return {"type": "object"}  # Default fallback
