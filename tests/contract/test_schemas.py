import json
from pathlib import Path

import pytest
from jsonschema import ValidationError, validate

# Paths to schemas
SCHEMA_DIR = Path("modules/mcp_protocol/schemas")
CORE_SCHEMA = SCHEMA_DIR / "core.json"
BLENDER_SCHEMA = SCHEMA_DIR / "blender.json"
UE5_SCHEMA = SCHEMA_DIR / "ue5.json"

def load_schema(path: Path):
    with open(path) as f:
        return json.load(f)

def test_core_schema_validity():
    schema = load_schema(CORE_SCHEMA)
    # Simple check: validate a valid ToolResult against the definition
    valid_result = {
        "protocol_version": "1.0",
        "tool": "mcp.test",
        "request_id": "req-1",
        "run_id": "run-1",
        "status": "ok",
        "result": {"foo": "bar"}
    }
    # We need to resolve local refs. For this test, we can just extract the definition
    # or use a resolver. Since definitions are local to the file, we can test against the definition schema directly if we wrap it?
    # Actually, simpler: jsonschema handles #/definitions/ automatically if we validate against the root schema
    # BUT the root schema in core.json doesn't define the structure of the *document* itself to be a ToolResult,
    # it defines definitions.

    # So we construct a schema that expects a ToolResult
    test_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$ref": "#/definitions/ToolResult",
        "definitions": schema["definitions"]
    }

    validate(instance=valid_result, schema=test_schema)

    # Test invalid result (missing tool)
    invalid_result = {
        "protocol_version": "1.0",
        "request_id": "req-1",
        "run_id": "run-1",
        "status": "ok",
        "result": {}
    }
    with pytest.raises(ValidationError):
        validate(instance=invalid_result, schema=test_schema)

def test_blender_schema_validity():
    schema = load_schema(BLENDER_SCHEMA)

    # Test GenerateSceneInput
    test_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$ref": "#/definitions/GenerateSceneInput",
        "definitions": schema["definitions"]
    }

    valid_input = {
        "description": "A test scene",
        "dry_run": True
    }
    validate(instance=valid_input, schema=test_schema)

    invalid_input = {
        "dry_run": True
        # missing description
    }
    with pytest.raises(ValidationError):
        validate(instance=invalid_input, schema=test_schema)

def test_ue5_schema_validity():
    schema = load_schema(UE5_SCHEMA)

    # Test GenerateTerrainInput
    test_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$ref": "#/definitions/GenerateTerrainInput",
        "definitions": schema["definitions"]
    }

    valid_input = {
        "width": 100,
        "height": 100,
        "detail_level": "medium"
    }
    validate(instance=valid_input, schema=test_schema)

    invalid_input = {
        "width": 100,
        "height": 100,
        "detail_level": "ultra" # invalid enum
    }
    with pytest.raises(ValidationError):
        validate(instance=invalid_input, schema=test_schema)
