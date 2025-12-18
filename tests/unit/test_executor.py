from unittest.mock import MagicMock

import pytest
from mcp_core.execution.tool_executor import ToolExecutor
from mcp_core.registry import registry
from mcp_protocol import Artifact, ToolError, ToolResult
from pydantic import BaseModel


class MockInput(BaseModel):
    value: str

def mock_handler(input: MockInput) -> ToolResult:
    return ToolResult(
        tool="mock.tool",
        request_id="req-1",
        run_id="run-1",
        result={"echo": input.value},
        artifacts=[Artifact(type="text/plain", content="art")]
    )

def mock_handler_error(input: MockInput) -> ToolError:
    from mcp_protocol import ToolErrorDetail
    return ToolError(
        tool="mock.tool",
        request_id="req-1",
        run_id="run-1",
        error=ToolErrorDetail(code="TEST_ERROR", message="Something went wrong")
    )

@pytest.fixture(autouse=True)
def setup_registry():
    registry.clear()
    registry.register("mock.tool", "Mock Tool", MockInput, mock_handler)
    registry.register("mock.error", "Mock Error Tool", MockInput, mock_handler_error)
    yield
    registry.clear()

@pytest.fixture
def mock_storage(monkeypatch):
    mock_am = MagicMock()
    # Return artifact as is (or modified)
    mock_am.store_artifact.side_effect = lambda rid, art: art.model_copy(update={"uri": "/tmp/art"})
    monkeypatch.setattr("mcp_core.execution.tool_executor.artifact_manager", mock_am)
    return mock_am

@pytest.fixture
def mock_policy(monkeypatch):
    mock_pe = MagicMock()
    monkeypatch.setattr("mcp_core.execution.tool_executor.policy_engine", mock_pe)
    return mock_pe

def test_execute_success(mock_storage, mock_policy):
    executor = ToolExecutor()
    input_data = MockInput(value="hello")
    
    result = executor.execute("mock.tool", input_data)
    
    assert isinstance(result, ToolResult)
    assert result.status == "ok"
    assert result.result["echo"] == "hello"
    
    # Check artifacts stored
    assert len(result.artifacts) == 1
    assert result.artifacts[0].uri == "/tmp/art"
    mock_storage.store_artifact.assert_called_once()
    
    # Check manifest written
    mock_storage.write_run_manifest.assert_called_once()
    manifest = mock_storage.write_run_manifest.call_args[0][0]
    assert manifest.tool_name == "mock.tool"
    assert manifest.status == "success"
    assert manifest.inputs["value"] == "hello"

def test_execute_tool_not_found(mock_storage):
    executor = ToolExecutor()
    result = executor.execute("nonexistent", {"value": "foo"})
    
    assert isinstance(result, ToolError)
    assert result.error.code == "INTERNAL_ERROR" # Currently ValueError -> Internal Error
    assert "not found" in result.error.message
    
    # Manifest should record error
    mock_storage.write_run_manifest.assert_called_once()
    manifest = mock_storage.write_run_manifest.call_args[0][0]
    assert manifest.status == "error"

def test_execute_validation_error(mock_storage):
    executor = ToolExecutor()
    # Missing required field 'value'
    result = executor.execute("mock.tool", {})
    
    assert isinstance(result, ToolError)
    assert result.error.code == "VALIDATION_ERROR"
    
    mock_storage.write_run_manifest.assert_called_once()
    manifest = mock_storage.write_run_manifest.call_args[0][0]
    assert manifest.status == "error"

def test_execute_tool_error(mock_storage, mock_policy):
    executor = ToolExecutor()
    result = executor.execute("mock.error", {"value": "fail"})
    
    assert isinstance(result, ToolError)
    assert result.error.code == "TEST_ERROR"
    
    mock_storage.write_run_manifest.assert_called_once()
    manifest = mock_storage.write_run_manifest.call_args[0][0]
    assert manifest.status == "error"
    assert manifest.error["code"] == "TEST_ERROR"

def test_execute_policy_denied(mock_storage, mock_policy):
    mock_policy.check_tool_allowed.side_effect = PermissionError("Not allowed")
    
    executor = ToolExecutor()
    result = executor.execute("mock.tool", {"value": "denied"})
    
    assert isinstance(result, ToolError)
    assert result.error.code == "INTERNAL_ERROR" # PermissionError -> Internal Error in current catch-all
    # Ideally should be POLICY_DENIED, but currently executor catches all Exception.
    # We might want to improve executor error handling later.
    assert "Not allowed" in result.error.message
    
    mock_storage.write_run_manifest.assert_called_once()
