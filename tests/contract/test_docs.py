import json
from pathlib import Path

import pytest
from jsonschema import validate

REPO_ROOT = Path(__file__).parents[2]
SCHEMAS_DIR = REPO_ROOT / "modules/mcp_protocol/schemas"
CORE_SCHEMA_PATH = SCHEMAS_DIR / "core.json"

def load_schema(path: Path):
    with open(path) as f:
        return json.load(f)

CORE_SCHEMA = load_schema(CORE_SCHEMA_PATH)

def get_definition_schema(definition_name: str):
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$ref": f"#/definitions/{definition_name}",
        "definitions": CORE_SCHEMA["definitions"]
    }

DOC_MAPPINGS = [
    {
        "file": "api_reference.md",
        "header": "### Tool Result Envelope",
        "definition": "ToolResult"
    },
    {
        "file": "api_reference.md",
        "header": "### Error Envelope",
        "definition": "ToolError"
    },
    {
        "file": "commands.md",
        "header": "### Output Format",
        "definition": "ToolResult"
    },
    {
        "file": "commands.md",
        "header": "### Error Model",
        "definition": "ToolError"
    }
]

def extract_json_blocks(file_path: Path, target_header: str) -> list[dict]:
    lines = file_path.read_text(encoding="utf-8").splitlines()
    blocks = []
    
    state = "SEARCHING_HEADER"
    current_json = []
    header_level = len(target_header.split()[0])
    
    for line in lines:
        if state == "SEARCHING_HEADER":
            if line.strip().startswith(target_header):
                state = "SEARCHING_BLOCK"
        
        elif state == "SEARCHING_BLOCK":
            if line.strip().startswith("```json"):
                state = "READING_BLOCK"
            elif line.startswith("#"):
                # Check header level
                curr_level = len(line.split()[0])
                if curr_level <= header_level:
                    # Found a header of same or higher importance, stop searching for this section
                    state = "SEARCHING_HEADER"
        
        elif state == "READING_BLOCK":
            if line.strip().startswith("```"):
                # End of block
                json_str = "\n".join(current_json)
                try:
                    blocks.append(json.loads(json_str))
                except json.JSONDecodeError as e:
                    pytest.fail(f"Invalid JSON in {file_path} section {target_header}: {e}")
                
                current_json = []
                state = "SEARCHING_BLOCK"
            else:
                current_json.append(line)
                
    return blocks

@pytest.mark.parametrize("mapping", DOC_MAPPINGS)
def test_doc_json_validity(mapping):
    file_path = REPO_ROOT / mapping["file"]
    if not file_path.exists():
        pytest.skip(f"{mapping['file']} not found")
        
    schema = get_definition_schema(mapping["definition"])
    
    blocks = extract_json_blocks(file_path, mapping["header"])
    
    if not blocks:
        pytest.fail(f"No JSON blocks found for '{mapping['header']}' in {mapping['file']}")
        
    for block in blocks:
        validate(instance=block, schema=schema)
