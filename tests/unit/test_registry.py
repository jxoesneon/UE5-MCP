import pytest
from mcp_core.registry import ToolRegistry
from pydantic import BaseModel


class MockInput(BaseModel):
    x: int

def mock_handler(input: MockInput):
    return input.x * 2

def test_register_and_get_tool():
    registry = ToolRegistry()
    registry.register("mock.tool", "A mock tool", MockInput, mock_handler)

    tool = registry.get_tool("mock.tool")
    assert tool is not None
    assert tool.name == "mock.tool"
    assert tool.description == "A mock tool"
    assert tool.input_model is MockInput
    assert tool.handler is mock_handler

def test_register_duplicate_tool():
    registry = ToolRegistry()
    registry.register("mock.tool", "A mock tool", MockInput, mock_handler)

    with pytest.raises(ValueError, match="already registered"):
        registry.register("mock.tool", "Another mock tool", MockInput, mock_handler)

def test_list_tools():
    registry = ToolRegistry()
    registry.register("b.tool", "Tool B", MockInput, mock_handler)
    registry.register("a.tool", "Tool A", MockInput, mock_handler)

    tools = registry.list_tools()
    assert len(tools) == 2
    assert tools[0].name == "a.tool"
    assert tools[1].name == "b.tool"

def test_get_nonexistent_tool():
    registry = ToolRegistry()
    assert registry.get_tool("nonexistent") is None
