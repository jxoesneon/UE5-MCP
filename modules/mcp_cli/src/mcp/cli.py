import argparse
import json
import sys

from mcp_core import __version__ as core_version
from mcp_core import register_system_tools
from mcp_core.execution import executor
from mcp_core.observability import configure_logging
from mcp_protocol import (
    ConfigGetInput,
    HelpInput,
    ListCommandsInput,
    ToolError,
    ToolResult,
)


def _print_result(result: ToolResult | ToolError):
    # Determine output format (JSON for now, pretty printing later)
    # For now, just dump the model to stdout
    print(json.dumps(result.model_dump(), indent=2))

def _handle_list_commands(args: argparse.Namespace):
    # Input is empty
    inp = ListCommandsInput()
    result = executor.execute("mcp.list_commands", inp)
    _print_result(result)

def _handle_help(args: argparse.Namespace):
    inp = HelpInput(command_name=args.command)
    result = executor.execute("mcp.help", inp)
    _print_result(result)

def _handle_config_get(args: argparse.Namespace):
    inp = ConfigGetInput(key=args.key)
    result = executor.execute("mcp.config_get", inp)
    _print_result(result)

def main(argv: list[str] | None = None) -> int:
    # Configure logging
    configure_logging()

    # Ensure system tools are registered
    register_system_tools()

    parser = argparse.ArgumentParser(prog="mcp", description="UE5-MCP Command Line Interface")
    parser.add_argument("--version", action="store_true", help="Show version")

    subparsers = parser.add_subparsers(dest="subcommand", help="Available commands")

    # list-commands
    parser_list = subparsers.add_parser("list-commands", help="List available tools")
    parser_list.set_defaults(func=_handle_list_commands)

    # help
    parser_help = subparsers.add_parser("help", help="Get help for a specific tool")
    parser_help.add_argument("command", help="Name of the tool to get help for")
    parser_help.set_defaults(func=_handle_help)

    # config
    parser_config = subparsers.add_parser("config", help="Manage configuration")
    config_subparsers = parser_config.add_subparsers(dest="config_op", required=True)

    # config get
    parser_config_get = config_subparsers.add_parser("get", help="Get a config value")
    parser_config_get.add_argument("key", help="Configuration key (e.g. logging.level)")
    parser_config_get.set_defaults(func=_handle_config_get)

    args = parser.parse_args(argv)

    if args.version:
        # We use the core version as the system version for now
        print(core_version)
        return 0

    if hasattr(args, "func"):
        args.func(args)
        return 0

    parser.print_help()
    return 0

if __name__ == "__main__":
    sys.exit(main())
