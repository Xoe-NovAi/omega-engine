"""JSON parsing + JSON Schema conformance scoring."""

from __future__ import annotations

import json
from typing import Any

import jsonschema


def parse_json(raw: str) -> tuple[Any | None, bool]:
    try:
        return json.loads(raw), True
    except (json.JSONDecodeError, TypeError):
        return None, False


def validate_schema(obj: Any, schema: dict) -> tuple[bool, list[str]]:
    try:
        jsonschema.validate(instance=obj, schema=schema)
        return True, []
    except jsonschema.ValidationError as exc:
        return False, [exc.message[:200]]
    except jsonschema.SchemaError as exc:
        return False, [f"schema error: {exc.message[:200]}"]
