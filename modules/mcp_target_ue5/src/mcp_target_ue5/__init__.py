from mcp_core.registry import ToolRegistry
from mcp_protocol.models import (
    DebugBlueprintInput,
    GenerateBlueprintInput,
    GenerateTerrainInput,
    ImportAssetInput,
    OptimizeLevelInput,
    PopulateLevelInput,
    ProfilePerformanceInput,
)

from .tools import (
    debug_blueprint,
    generate_blueprint,
    generate_terrain,
    import_asset,
    optimize_level,
    populate_level,
    profile_performance,
)

__all__ = ["__version__", "register_ue5_tools"]

__version__ = "0.6.0"


def register_ue5_tools(registry: ToolRegistry) -> None:
    """Register UE5-related tools with the registry."""
    registry.register(
        name="mcp.import_asset",
        description="Import an asset from an export manifest into UE5.",
        input_model=ImportAssetInput,
        handler=import_asset,
    )
    registry.register(
        name="mcp.generate_terrain",
        description="Generate procedural terrain in UE5.",
        input_model=GenerateTerrainInput,
        handler=generate_terrain,
    )
    registry.register(
        name="mcp.populate_level",
        description="Populate a level with assets.",
        input_model=PopulateLevelInput,
        handler=populate_level,
    )
    registry.register(
        name="mcp.generate_blueprint",
        description="Generate or modify Blueprint logic.",
        input_model=GenerateBlueprintInput,
        handler=generate_blueprint,
    )
    registry.register(
        name="mcp.profile_performance",
        description="Profile performance of a level.",
        input_model=ProfilePerformanceInput,
        handler=profile_performance,
    )
    registry.register(
        name="mcp.optimize_level",
        description="Optimize level content based on budgets.",
        input_model=OptimizeLevelInput,
        handler=optimize_level,
    )
    registry.register(
        name="mcp.debug_blueprint",
        description="Debug a blueprint.",
        input_model=DebugBlueprintInput,
        handler=debug_blueprint,
    )
