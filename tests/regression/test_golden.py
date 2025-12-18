import json
from pathlib import Path
from typing import Any

from mcp_protocol.models import (
    Artifact,
    RunManifest,
    ToolError,
    ToolErrorDetail,
    ToolResult,
)

GOLDEN_DIR = Path(__file__).parent / "data"
GOLDEN_DIR.mkdir(exist_ok=True)

def assert_golden(name: str, actual_data: dict[str, Any]):
    """
    Compare actual data against a golden file.
    If the golden file does not exist, it is created.
    """
    golden_path = GOLDEN_DIR / f"{name}.json"
    
    # Sort keys for deterministic JSON serialization
    actual_json = json.dumps(actual_data, indent=2, sort_keys=True)
    
    if not golden_path.exists():
        golden_path.write_text(actual_json)
        # We don't fail on first run, but we warn or just pass. 
        # In a real CI env, we might want to fail if goldens are missing.
        # For this dev phase, bootstrapping is fine.
        return

    expected_json = golden_path.read_text()
    
    # Compare parsed objects to ignore whitespace diffs if any, 
    # but we also want to ensure the serialization format is stable.
    # Comparing strings is stricter.
    assert actual_json == expected_json, f"Golden mismatch for {name}"

def test_golden_tool_result_success():
    """Verify ToolResult serialization against golden record."""
    result = ToolResult(
        tool="mcp.test",
        request_id="req-123",
        run_id="run-456",
        status="ok",
        result={"value": 42},
        artifacts=[
            Artifact(type="text", uri="file:///tmp/test.txt", content="Hello")
        ]
    )
    assert_golden("tool_result_success", result.model_dump(mode="json"))

def test_golden_tool_error():
    """Verify ToolError serialization against golden record."""
    error = ToolError(
        tool="mcp.test",
        request_id="req-123",
        run_id="run-456",
        error=ToolErrorDetail(
            code="INVALID_INPUT",
            message="Something went wrong",
            retriable=True,
            details={"field": "username"}
        )
    )
    assert_golden("tool_error", error.model_dump(mode="json"))

def test_golden_run_manifest():
    """Verify RunManifest serialization against golden record."""
    manifest = RunManifest(
        run_id="run-456",
        request_id="req-123",
        tool_name="mcp.test",
        status="success",
        start_time="2023-01-01T12:00:00Z",
        end_time="2023-01-01T12:00:01Z",
        duration_seconds=1.0,
        inputs={"param": "value"},
        outputs={"result": "ok"},
        config_hash="abc123hash",
        tool_version="1.0.0"
    )
    assert_golden("run_manifest", manifest.model_dump(mode="json"))
