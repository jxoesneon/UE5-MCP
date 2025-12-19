from mcp_core.registry import ToolRegistry
from mcp_protocol.models import (
    AddObjectInput,
    ExportAssetInput,
    GenerateSceneInput,
    GenerateTextureInput,
)

from .tools import (
    add_object,
    export_asset,
    generate_scene,
    generate_texture,
)

__all__ = ["__version__", "register_blender_tools"]

__version__ = "1.0.0"


def register_blender_tools(registry: ToolRegistry) -> None:
    """Register Blender-related tools with the registry."""
    # Check if already registered to make this function idempotent
    if registry.get_tool("mcp.generate_scene"):
        return

    registry.register(
        name="mcp.generate_scene",
        description="Generate a Blender scene based on a description.",
        input_model=GenerateSceneInput,
        handler=generate_scene,
    )
    registry.register(
        name="mcp.add_object",
        description="Add an object to the current Blender scene.",
        input_model=AddObjectInput,
        handler=add_object,
    )
    registry.register(
        name="mcp.generate_texture",
        description="Generate a texture for an object.",
        input_model=GenerateTextureInput,
        handler=generate_texture,
    )
    registry.register(
        name="mcp.export_asset",
        description="Export an asset from Blender.",
        input_model=ExportAssetInput,
        handler=export_asset,
    )
