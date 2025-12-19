from typing import Any

from mcp_protocol import (
    ConfigGetInput,
    ConfigSetInput,
    HelpInput,
    ListCommandsInput,
    ResetConfigInput,
    ToolError,
    ToolErrorDetail,
    ToolResult,
)

from .config.settings import settings
from .observability.context import get_current_context
from .registry import ToolRegistry, registry


def list_commands_handler(input: ListCommandsInput) -> ToolResult | ToolError:
    ctx = get_current_context()
    tools = registry.list_tools()
    result = {
        "tools": [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_model.model_json_schema(),
            }
            for t in tools
        ]
    }
    return ToolResult(
        tool="mcp.list_commands",
        request_id=ctx.request_id or "",
        run_id=ctx.run_id or "",
        result=result
    )

def help_handler(input: HelpInput) -> ToolResult | ToolError:
    ctx = get_current_context()
    tool = registry.get_tool(input.command_name)
    if not tool:
        return ToolError(
            tool="mcp.help",
            request_id=ctx.request_id or "",
            run_id=ctx.run_id or "",
            error=ToolErrorDetail(
                code="TOOL_NOT_FOUND",
                message=f"Tool '{input.command_name}' not found."
            )
        )

    result = {
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.input_model.model_json_schema(),
    }
    return ToolResult(
        tool="mcp.help",
        request_id=ctx.request_id or "",
        run_id=ctx.run_id or "",
        result=result
    )

def config_get_handler(input: ConfigGetInput) -> ToolResult | ToolError:
    ctx = get_current_context()
    # Basic dot-notation access
    keys = input.key.split(".")
    value: Any = settings
    try:
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            elif isinstance(value, dict) and k in value:
                value = value[k]
            else:
                raise KeyError(k)
    except (KeyError, AttributeError):
        return ToolError(
            tool="mcp.config_get",
            request_id=ctx.request_id or "",
            run_id=ctx.run_id or "",
            error=ToolErrorDetail(
                code="CONFIG_KEY_NOT_FOUND",
                message=f"Key '{input.key}' not found in configuration."
            )
        )

    # Redact secrets if necessary (rudimentary check)
    if "key" in input.key.lower() or "secret" in input.key.lower():
        value = "***REDACTED***"

    return ToolResult(
        tool="mcp.config_get",
        request_id=ctx.request_id or "",
        run_id=ctx.run_id or "",
        result={"key": input.key, "value": value}
    )

# Note: Config Set/Reset are placeholders as BaseSettings is immutable by default
# and typical usage is env vars or files. Runtime modification would require a mutable backing store.
def config_set_handler(input: ConfigSetInput) -> ToolResult | ToolError:
    ctx = get_current_context()
    return ToolError(
        tool="mcp.config_set",
        request_id=ctx.request_id or "",
        run_id=ctx.run_id or "",
        error=ToolErrorDetail(
            code="NOT_IMPLEMENTED",
            message="Runtime configuration modification is not yet supported. Use environment variables or config files."
        )
    )

def reset_config_handler(input: ResetConfigInput) -> ToolResult | ToolError:
    ctx = get_current_context()
    if not input.confirm:
        return ToolError(
            tool="mcp.reset_config",
            request_id=ctx.request_id or "",
            run_id=ctx.run_id or "",
            error=ToolErrorDetail(
                code="CONFIRMATION_REQUIRED",
                message="Use --confirm to reset configuration."
            )
        )
    return ToolError(
        tool="mcp.reset_config",
        request_id=ctx.request_id or "",
        run_id=ctx.run_id or "",
        error=ToolErrorDetail(
            code="NOT_IMPLEMENTED",
            message="Runtime configuration reset is not yet supported."
        )
    )

def register_system_tools(registry: ToolRegistry = registry):
    # Check if already registered to make this function idempotent
    if registry.get_tool("mcp.list_commands"):
        return

    registry.register(
        name="mcp.list_commands",
        description="List all available tools and their schemas.",
        input_model=ListCommandsInput,
        handler=list_commands_handler,
    )
    registry.register(
        name="mcp.help",
        description="Get detailed help for a specific tool.",
        input_model=HelpInput,
        handler=help_handler,
    )
    registry.register(
        name="mcp.config_get",
        description="Get a configuration value.",
        input_model=ConfigGetInput,
        handler=config_get_handler,
    )
    registry.register(
        name="mcp.config_set",
        description="Set a configuration value (not implemented).",
        input_model=ConfigSetInput,
        handler=config_set_handler,
    )
    registry.register(
        name="mcp.reset_config",
        description="Reset configuration to defaults (not implemented).",
        input_model=ResetConfigInput,
        handler=reset_config_handler,
    )
