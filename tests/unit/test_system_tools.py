import pytest
from mcp_core.config.settings import McpSettings
from mcp_core.registry import registry
from mcp_core.system_tools import (
    config_get_handler,
    config_set_handler,
    help_handler,
    list_commands_handler,
    register_system_tools,
    reset_config_handler,
)
from mcp_protocol import (
    ConfigGetInput,
    ConfigSetInput,
    HelpInput,
    ListCommandsInput,
    ResetConfigInput,
)


@pytest.fixture(autouse=True)
def clean_registry():
    registry.clear()
    yield
    registry.clear()

def test_list_commands_handler():
    # Ensure system tools are registered for this test
    register_system_tools()
    
    inp = ListCommandsInput()
    result = list_commands_handler(inp)
    
    assert result.status == "ok"
    assert result.tool == "mcp.list_commands"
    
    tools = result.result["tools"]
    tool_names = [t["name"] for t in tools]
    assert "mcp.list_commands" in tool_names
    assert "mcp.help" in tool_names

def test_help_handler():
    register_system_tools()
    
    inp = HelpInput(command_name="mcp.list_commands")
    result = help_handler(inp)
    
    assert result.status == "ok"
    assert result.result["name"] == "mcp.list_commands"
    assert "input_schema" in result.result

def test_help_handler_not_found():
    inp = HelpInput(command_name="nonexistent.tool")
    result = help_handler(inp)
    
    assert result.status == "error"
    assert result.error.code == "TOOL_NOT_FOUND"

def test_config_get_handler(monkeypatch):
    # Mock settings
    settings = McpSettings()
    # We can rely on defaults: logging.level is INFO
    monkeypatch.setattr("mcp_core.system_tools.settings", settings)
    
    inp = ConfigGetInput(key="logging.level")
    result = config_get_handler(inp)
    
    assert result.status == "ok"
    assert result.result["value"] == "INFO"

def test_config_get_handler_nested(monkeypatch):
    settings = McpSettings()
    monkeypatch.setattr("mcp_core.system_tools.settings", settings)
    
    inp = ConfigGetInput(key="blender.scene_generation.default_style")
    result = config_get_handler(inp)
    
    assert result.status == "ok"
    assert result.result["value"] == "realistic"

def test_config_get_handler_not_found(monkeypatch):
    settings = McpSettings()
    monkeypatch.setattr("mcp_core.system_tools.settings", settings)
    
    inp = ConfigGetInput(key="nonexistent.key")
    result = config_get_handler(inp)
    
    assert result.status == "error"
    assert result.error.code == "CONFIG_KEY_NOT_FOUND"

def test_config_set_not_implemented():
    inp = ConfigSetInput(key="foo", value="bar")
    result = config_set_handler(inp)
    
    assert result.status == "error"
    assert result.error.code == "NOT_IMPLEMENTED"

def test_reset_config_not_implemented():
    inp = ResetConfigInput()
    result = reset_config_handler(inp)
    
    assert result.status == "error"
    assert result.error.code == "NOT_IMPLEMENTED"
