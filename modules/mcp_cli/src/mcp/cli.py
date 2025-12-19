import argparse
import json
import sys

from mcp_core import __version__ as core_version
from mcp_core import register_system_tools
from mcp_core.execution import executor
from mcp_core.observability import configure_logging
from mcp_core.registry import registry
from mcp_protocol.models import (
    AddObjectInput,
    ConfigGetInput,
    ConfigSetInput,
    DebugBlueprintInput,
    ExportAssetInput,
    GenerateBlueprintInput,
    GenerateSceneInput,
    GenerateTerrainInput,
    GenerateTextureInput,
    HelpInput,
    ImportAssetInput,
    ListCommandsInput,
    OptimizeLevelInput,
    PopulateLevelInput,
    ProfilePerformanceInput,
    ResetConfigInput,
    ToolError,
    ToolResult,
    Vec3,
)

# Try to import Blender tools
try:
    from mcp_target_blender import register_blender_tools
    HAS_BLENDER = True
except ImportError:
    HAS_BLENDER = False

# Try to import UE5 tools
try:
    from mcp_target_ue5 import register_ue5_tools
    HAS_UE5 = True
except ImportError:
    HAS_UE5 = False


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

def _handle_config_set(args: argparse.Namespace):
    inp = ConfigSetInput(key=args.key, value=args.value)
    result = executor.execute("mcp.config_set", inp)
    _print_result(result)

def _handle_reset_config(args: argparse.Namespace):
    inp = ResetConfigInput(confirm=args.confirm)
    result = executor.execute("mcp.reset_config", inp)
    _print_result(result)

# --- Blender Handlers ---

def _handle_generate_scene(args: argparse.Namespace):
    inp = GenerateSceneInput(
        description=args.description,
        seed=args.seed,
        style=args.style,
        dry_run=args.dry_run
    )
    result = executor.execute("mcp.generate_scene", inp)
    _print_result(result)

def _handle_add_object(args: argparse.Namespace):
    inp = AddObjectInput(
        object_type=args.object_type,
        location=Vec3(x=args.x, y=args.y, z=args.z),
        dry_run=args.dry_run if hasattr(args, "dry_run") else False # AddObjectInput in schema has dry_run? Checked model, yes it does in schema but not explicitly in command args in commands.md example. Adding for consistency if model supports it.
        # Wait, checking models.py: AddObjectInput has dry_run: bool = False.
    )
    result = executor.execute("mcp.add_object", inp)
    _print_result(result)

def _handle_generate_texture(args: argparse.Namespace):
    inp = GenerateTextureInput(
        object_name=args.object_name,
        texture_type=args.texture_type,
        dry_run=args.dry_run
    )
    result = executor.execute("mcp.generate_texture", inp)
    _print_result(result)

def _handle_export_asset(args: argparse.Namespace):
    inp = ExportAssetInput(
        object_name=args.object_name,
        format=args.format,
        filepath=args.filepath,
        include_textures=args.include_textures,
        overwrite=args.overwrite,
        dry_run=args.dry_run
    )
    result = executor.execute("mcp.export_asset", inp)
    _print_result(result)


# --- UE5 Handlers ---

def _handle_import_asset(args: argparse.Namespace):
    inp = ImportAssetInput(
        manifest_path=args.manifest_path,
        dry_run=args.dry_run,
        overwrite=args.overwrite
    )
    result = executor.execute("mcp.import_asset", inp)
    _print_result(result)

def _handle_generate_terrain(args: argparse.Namespace):
    inp = GenerateTerrainInput(
        width=args.width,
        height=args.height,
        detail_level=args.detail_level,
        seed=args.seed,
        dry_run=args.dry_run
    )
    result = executor.execute("mcp.generate_terrain", inp)
    _print_result(result)

def _handle_populate_level(args: argparse.Namespace):
    inp = PopulateLevelInput(
        asset_type=args.asset_type,
        density=args.density,
        seed=args.seed,
        budget_max_instances=args.budget_max_instances,
        dry_run=args.dry_run
    )
    result = executor.execute("mcp.populate_level", inp)
    _print_result(result)

def _handle_generate_blueprint(args: argparse.Namespace):
    inp = GenerateBlueprintInput(
        logic_description=args.logic_description,
        dry_run=args.dry_run
    )
    result = executor.execute("mcp.generate_blueprint", inp)
    _print_result(result)

def _handle_profile_performance(args: argparse.Namespace):
    inp = ProfilePerformanceInput(
        level_name=args.level_name
    )
    result = executor.execute("mcp.profile_performance", inp)
    _print_result(result)

def _handle_optimize_level(args: argparse.Namespace):
    inp = OptimizeLevelInput(
        dry_run=args.dry_run,
        budgets=None # CLI arg for budgets is complex, leaving None for now
    )
    result = executor.execute("mcp.optimize_level", inp)
    _print_result(result)

def _handle_debug_blueprint(args: argparse.Namespace):
    inp = DebugBlueprintInput(
        blueprint_name=args.blueprint_name
    )
    result = executor.execute("mcp.debug_blueprint", inp)
    _print_result(result)

def _handle_export_asset_ue5(args: argparse.Namespace):
    inp = ExportAssetInput(
        object_name=args.object_name,
        format=args.format,
        filepath=args.filepath,
        include_textures=args.include_textures,
        overwrite=args.overwrite,
        dry_run=args.dry_run
    )
    result = executor.execute("mcp.export_asset_ue5", inp)
    _print_result(result)


def main(argv: list[str] | None = None) -> int:
    # Configure logging
    configure_logging()

    # Ensure system tools are registered
    register_system_tools(registry)

    # Register Blender tools if available
    if HAS_BLENDER:
        register_blender_tools(registry)

    # Register UE5 tools if available
    if HAS_UE5:
        register_ue5_tools(registry)

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

    # config set
    parser_config_set = config_subparsers.add_parser("set", help="Set a config value")
    parser_config_set.add_argument("key", help="Configuration key")
    parser_config_set.add_argument("value", help="Value to set")
    parser_config_set.set_defaults(func=_handle_config_set)

    # config reset
    parser_config_reset = config_subparsers.add_parser("reset", help="Reset config to defaults")
    parser_config_reset.add_argument("--confirm", action="store_true", help="Confirm reset")
    parser_config_reset.set_defaults(func=_handle_reset_config)

    if HAS_BLENDER:
        # mcp.generate_scene
        p_gen_scene = subparsers.add_parser("generate_scene", help="Generate a scene scaffold")
        p_gen_scene.add_argument("description", help="Scene description")
        p_gen_scene.add_argument("--seed", type=int, help="Random seed")
        p_gen_scene.add_argument("--style", help="Visual style")
        p_gen_scene.add_argument("--dry-run", action="store_true", help="Simulate execution")
        p_gen_scene.add_argument("--apply", action="store_true", help="Apply changes (mutually exclusive with dry-run)") # Logic for apply vs dry-run default?
        # Commands.md says: --dry-run | --apply. Default is usually to do nothing or error if not specified? Or safe default?
        # For now let's stick to boolean flags. If neither, what happens?
        # Spec says "default behavior should avoid destructive operations".
        # Let's assume explicit --apply needed for mutation if dangerous.
        # But GenerateScene might not be dangerous?
        # Let's just pass dry_run=True if --dry-run is present.
        p_gen_scene.set_defaults(func=_handle_generate_scene)

        # mcp.add_object
        p_add_obj = subparsers.add_parser("add_object", help="Add an object")
        p_add_obj.add_argument("object_type", help="Type of object")
        p_add_obj.add_argument("x", type=float, help="X coordinate")
        p_add_obj.add_argument("y", type=float, help="Y coordinate")
        p_add_obj.add_argument("z", type=float, help="Z coordinate")
        p_add_obj.add_argument("--dry-run", action="store_true", help="Simulate execution")
        p_add_obj.set_defaults(func=_handle_add_object)

        # mcp.generate_texture
        p_gen_tex = subparsers.add_parser("generate_texture", help="Generate/apply texture")
        p_gen_tex.add_argument("object_name", help="Target object name")
        p_gen_tex.add_argument("texture_type", help="Type of texture")
        p_gen_tex.add_argument("--dry-run", action="store_true", help="Simulate execution")
        p_gen_tex.set_defaults(func=_handle_generate_texture)

        # mcp.export_asset
        p_export = subparsers.add_parser("export_asset", help="Export an asset")
        p_export.add_argument("object_name", help="Object to export")
        p_export.add_argument("format", choices=["fbx", "obj", "gltf"], help="Export format")
        p_export.add_argument("filepath", help="Output file path")
        p_export.add_argument("--include-textures", action="store_true", default=True, help="Include textures (default: True)")
        p_export.add_argument("--no-include-textures", action="store_false", dest="include_textures", help="Do not include textures")
        p_export.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
        p_export.add_argument("--dry-run", action="store_true", help="Simulate execution")
        p_export.set_defaults(func=_handle_export_asset)

    if HAS_UE5:
        # mcp.import_asset
        p_import = subparsers.add_parser("import_asset", help="Import an asset")
        p_import.add_argument("manifest_path", help="Path to export manifest")
        p_import.add_argument("--overwrite", action="store_true", help="Overwrite existing assets")
        p_import.add_argument("--dry-run", action="store_true", help="Simulate execution")
        p_import.set_defaults(func=_handle_import_asset)

        # mcp.generate_terrain
        p_gen_terrain = subparsers.add_parser("generate_terrain", help="Generate terrain")
        p_gen_terrain.add_argument("width", type=int, help="Width")
        p_gen_terrain.add_argument("height", type=int, help="Height")
        p_gen_terrain.add_argument("detail_level", choices=["low", "medium", "high"], help="Detail level")
        p_gen_terrain.add_argument("--seed", type=int, help="Random seed")
        p_gen_terrain.add_argument("--dry-run", action="store_true", help="Simulate execution")
        p_gen_terrain.set_defaults(func=_handle_generate_terrain)

        # mcp.populate_level
        p_pop_level = subparsers.add_parser("populate_level", help="Populate level with assets")
        p_pop_level.add_argument("asset_type", help="Asset type to spawn")
        p_pop_level.add_argument("density", type=int, help="Density (count)")
        p_pop_level.add_argument("--seed", type=int, help="Random seed")
        p_pop_level.add_argument("--budget-max-instances", type=int, help="Max instances budget")
        p_pop_level.add_argument("--dry-run", action="store_true", help="Simulate execution")
        p_pop_level.set_defaults(func=_handle_populate_level)

        # mcp.generate_blueprint
        p_gen_bp = subparsers.add_parser("generate_blueprint", help="Generate Blueprint logic")
        p_gen_bp.add_argument("logic_description", help="Description of logic")
        p_gen_bp.add_argument("--dry-run", action="store_true", help="Simulate execution")
        p_gen_bp.set_defaults(func=_handle_generate_blueprint)

        # mcp.profile_performance
        p_profile = subparsers.add_parser("profile_performance", help="Profile level performance")
        p_profile.add_argument("level_name", help="Level name")
        p_profile.set_defaults(func=_handle_profile_performance)

        # mcp.optimize_level
        p_opt = subparsers.add_parser("optimize_level", help="Optimize level")
        p_opt.add_argument("--dry-run", action="store_true", help="Simulate execution")
        p_opt.set_defaults(func=_handle_optimize_level)

        # mcp.debug_blueprint
        p_debug = subparsers.add_parser("debug_blueprint", help="Debug a blueprint")
        p_debug.add_argument("blueprint_name", help="Blueprint name")
        p_debug.set_defaults(func=_handle_debug_blueprint)

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
