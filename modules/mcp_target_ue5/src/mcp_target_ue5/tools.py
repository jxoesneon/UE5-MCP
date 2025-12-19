import asyncio
import json
from typing import Any

from mcp_core.ai import create_ai_client
from mcp_core.ai.prompts import PromptTemplate
from mcp_core.config.settings import settings
from mcp_core.observability.context import get_current_context
from mcp_protocol.models import (
    DebugBlueprintInput,
    GenerateBlueprintInput,
    GenerateTerrainInput,
    ImportAssetInput,
    OptimizeLevelInput,
    PopulateLevelInput,
    ProfilePerformanceInput,
    ToolError,
    ToolErrorDetail,
    ToolResult,
)

from .transport import HttpTransport

# AI prompt for Blueprint generation
BLUEPRINT_GENERATION_PROMPT = PromptTemplate(
    name="blueprint_generation",
    version=1,
    template="""You are an Unreal Engine 5 Blueprint architect. Given a description of desired behavior, output a JSON structure describing the Blueprint nodes and connections needed.

Description: {description}

Output a JSON object with the following structure:
{{
  "blueprint_name": "BP_<descriptive_name>",
  "parent_class": "Actor",
  "events": [
    {{
      "event_type": "BeginPlay|Tick|OnOverlap|OnInteract|Custom",
      "event_name": "string"
    }}
  ],
  "variables": [
    {{
      "name": "string",
      "type": "bool|int|float|string|vector|actor",
      "default_value": "any"
    }}
  ],
  "functions": [
    {{
      "name": "string",
      "description": "string",
      "nodes": ["node descriptions"]
    }}
  ],
  "components": [
    {{
      "type": "StaticMesh|BoxCollision|SphereCollision|Audio|Light",
      "name": "string"
    }}
  ]
}}

Only output the JSON, no additional text.""",
    input_variables=["description"]
)

# Global transport instance
_transport: HttpTransport | None = None

def get_transport() -> HttpTransport:
    global _transport
    if _transport is None:
        # TODO: Get host/port from config
        _transport = HttpTransport()
    return _transport


def _execute_ue5_command(command: str, params: dict[str, Any]) -> dict[str, Any]:
    transport = get_transport()
    # Ensure connected (lightweight check usually)
    # transport.connect()
    response = transport.send_command(command, params)
    result: dict[str, Any] = response.get("data", {})
    return result


def import_asset(input: ImportAssetInput) -> ToolResult | ToolError:
    """
    Import an asset from an export manifest into UE5.
    """
    ctx = get_current_context()

    if not input.dry_run:
        try:
            data = _execute_ue5_command("import_asset", input.model_dump())
            result_data = data
        except Exception as e:
            return ToolError(
                tool="import_asset",
                request_id=ctx.request_id or "",
                run_id=ctx.run_id or "",
                error=ToolErrorDetail(code="EXECUTION_ERROR", message=str(e))
            )
    else:
        result_data = {
            "message": f"Imported asset from '{input.manifest_path}'",
            "assets": ["/Game/Imported/Asset1"]
        }

    return ToolResult(
        tool="import_asset",
        request_id=ctx.request_id or "",
        run_id=ctx.run_id or "",
        result=result_data
    )


def generate_terrain(input: GenerateTerrainInput) -> ToolResult | ToolError:
    """
    Generate procedural terrain in UE5.
    """
    ctx = get_current_context()

    if not input.dry_run:
        try:
            data = _execute_ue5_command("generate_terrain", input.model_dump())
            result_data = data
        except Exception as e:
            return ToolError(
                tool="generate_terrain",
                request_id=ctx.request_id or "",
                run_id=ctx.run_id or "",
                error=ToolErrorDetail(code="EXECUTION_ERROR", message=str(e))
            )
    else:
        result_data = {
            "message": f"Generated {input.width}x{input.height} terrain ({input.detail_level})",
            "terrain_path": "/Game/Maps/GeneratedTerrain"
        }

    return ToolResult(
        tool="generate_terrain",
        request_id=ctx.request_id or "",
        run_id=ctx.run_id or "",
        result=result_data
    )


def populate_level(input: PopulateLevelInput) -> ToolResult | ToolError:
    """
    Populate a level with assets.
    """
    ctx = get_current_context()

    if not input.dry_run:
        try:
            data = _execute_ue5_command("populate_level", input.model_dump())
            result_data = data
        except Exception as e:
            return ToolError(
                tool="populate_level",
                request_id=ctx.request_id or "",
                run_id=ctx.run_id or "",
                error=ToolErrorDetail(code="EXECUTION_ERROR", message=str(e))
            )
    else:
        result_data = {
            "message": f"Populated level with {input.density} instances of '{input.asset_type}'",
            "count": input.density
        }

    return ToolResult(
        tool="populate_level",
        request_id=ctx.request_id or "",
        run_id=ctx.run_id or "",
        result=result_data
    )


def generate_blueprint(input: GenerateBlueprintInput) -> ToolResult | ToolError:
    """
    Generate or modify Blueprint logic using AI to interpret the description.
    """
    ctx = get_current_context()

    if not input.dry_run:
        try:
            # Use AI to interpret the logic description into Blueprint structure
            blueprint_spec = None
            if settings.ai.enabled:
                try:
                    ai_client = create_ai_client()
                    ai_client.prompt_registry.register(BLUEPRINT_GENERATION_PROMPT)
                    ai_response = asyncio.run(ai_client.generate(
                        prompt_name="blueprint_generation",
                        variables={"description": input.logic_description}
                    ))
                    # Parse the AI response
                    content = ai_response.content.strip()
                    if content.startswith("```json"):
                        content = content[7:-3]
                    elif content.startswith("```"):
                        content = content[3:-3]
                    blueprint_spec = json.loads(content)
                except Exception as e:
                    print(f"AI Blueprint generation failed: {e}")

            # Prepare payload with AI-generated spec if available
            payload = input.model_dump()
            if blueprint_spec:
                payload["blueprint_spec"] = blueprint_spec

            data = _execute_ue5_command("generate_blueprint", payload)
            result_data = data

            # Add AI-generated spec to result for transparency
            if blueprint_spec:
                result_data["ai_generated_spec"] = blueprint_spec

        except Exception as e:
            return ToolError(
                tool="generate_blueprint",
                request_id=ctx.request_id or "",
                run_id=ctx.run_id or "",
                error=ToolErrorDetail(code="EXECUTION_ERROR", message=str(e))
            )
    else:
        result_data = {
            "message": "Blueprint generated from description",
            "blueprint_path": "/Game/Blueprints/GeneratedBP",
            "status": "compiled",
            "description": input.logic_description
        }

    return ToolResult(
        tool="generate_blueprint",
        request_id=ctx.request_id or "",
        run_id=ctx.run_id or "",
        result=result_data
    )


def profile_performance(input: ProfilePerformanceInput) -> ToolResult | ToolError:
    """
    Profile performance of a level.
    """
    ctx = get_current_context()

    if not input.dry_run:
        try:
            data = _execute_ue5_command("profile_performance", input.model_dump())
            result_data = data
        except Exception as e:
            return ToolError(
                tool="profile_performance",
                request_id=ctx.request_id or "",
                run_id=ctx.run_id or "",
                error=ToolErrorDetail(code="EXECUTION_ERROR", message=str(e))
            )
    else:
        result_data = {
            "message": f"Profiled level '{input.level_name}'",
            "fps_avg": 60.0,
            "frame_time_ms": 16.67
        }

    return ToolResult(
        tool="profile_performance",
        request_id=ctx.request_id or "",
        run_id=ctx.run_id or "",
        result=result_data
    )


def optimize_level(input: OptimizeLevelInput) -> ToolResult | ToolError:
    """
    Optimize level content based on budgets.
    """
    ctx = get_current_context()

    if not input.dry_run:
        try:
            data = _execute_ue5_command("optimize_level", input.model_dump())
            result_data = data
        except Exception as e:
            return ToolError(
                tool="optimize_level",
                request_id=ctx.request_id or "",
                run_id=ctx.run_id or "",
                error=ToolErrorDetail(code="EXECUTION_ERROR", message=str(e))
            )
    else:
        result_data = {
            "message": "Optimization pass complete",
            "optimized_count": 5
        }

    return ToolResult(
        tool="optimize_level",
        request_id=ctx.request_id or "",
        run_id=ctx.run_id or "",
        result=result_data
    )


def debug_blueprint(input: DebugBlueprintInput) -> ToolResult | ToolError:
    """
    Debug a blueprint.
    """
    ctx = get_current_context()

    if not input.dry_run:
        try:
            data = _execute_ue5_command("debug_blueprint", input.model_dump())
            result_data = data
        except Exception as e:
            return ToolError(
                tool="debug_blueprint",
                request_id=ctx.request_id or "",
                run_id=ctx.run_id or "",
                error=ToolErrorDetail(code="EXECUTION_ERROR", message=str(e))
            )
    else:
        result_data = {
            "message": f"Debugged blueprint '{input.blueprint_name}'"
        }

    return ToolResult(
        tool="debug_blueprint",
        request_id=ctx.request_id or "",
        run_id=ctx.run_id or "",
        result=result_data
    )
