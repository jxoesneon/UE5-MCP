from datetime import datetime

from mcp_core.observability.context import get_current_context
from mcp_protocol.models import (
    AddObjectInput,
    Artifact,
    ExportAssetInput,
    ExportManifest,
    GenerateSceneInput,
    GenerateTextureInput,
    ToolError,
    ToolErrorDetail,
    ToolResult,
)

from .transport import StdioTransport

# Global transport instance
_transport: StdioTransport | None = None

def get_transport() -> StdioTransport:
    global _transport
    if _transport is None:
        # TODO: Get blender path from config
        _transport = StdioTransport()
    return _transport


def generate_scene(input: GenerateSceneInput) -> ToolResult | ToolError:
    """
    Generate a Blender scene based on a description.
    """
    ctx = get_current_context()

    if not input.dry_run:
        try:
            transport = get_transport()
            response = transport.send_command("generate_scene", input.model_dump())
            result_data = response.get("data", {})
        except Exception as e:
            return ToolError(
                tool="generate_scene",
                request_id=ctx.request_id or "",
                run_id=ctx.run_id or "",
                error=ToolErrorDetail(code="EXECUTION_ERROR", message=str(e))
            )
    else:
        result_data = {
            "message": f"Scene generated: {input.description}",
            "style": input.style,
            "seed": input.seed
        }

    return ToolResult(
        tool="generate_scene",
        request_id=ctx.request_id or "",
        run_id=ctx.run_id or "",
        result=result_data
    )

def add_object(input: AddObjectInput) -> ToolResult | ToolError:
    """
    Add an object to the current Blender scene.
    """
    ctx = get_current_context()

    if not input.dry_run:
        try:
            transport = get_transport()
            response = transport.send_command("add_object", input.model_dump())
            result_data = response.get("data", {})
        except Exception as e:
            return ToolError(
                tool="add_object",
                request_id=ctx.request_id or "",
                run_id=ctx.run_id or "",
                error=ToolErrorDetail(code="EXECUTION_ERROR", message=str(e))
            )
    else:
        result_data = {
            "message": f"Added object: {input.object_type}",
            "location": input.location.model_dump()
        }

    return ToolResult(
        tool="add_object",
        request_id=ctx.request_id or "",
        run_id=ctx.run_id or "",
        result=result_data
    )

def generate_texture(input: GenerateTextureInput) -> ToolResult | ToolError:
    """
    Generate a texture for an object.
    """
    ctx = get_current_context()

    if not input.dry_run:
        try:
            transport = get_transport()
            response = transport.send_command("generate_texture", input.model_dump())
            result_data = response.get("data", {})
        except Exception as e:
            return ToolError(
                tool="generate_texture",
                request_id=ctx.request_id or "",
                run_id=ctx.run_id or "",
                error=ToolErrorDetail(code="EXECUTION_ERROR", message=str(e))
            )
    else:
        result_data = {
            "message": f"Generated texture '{input.texture_type}' for '{input.object_name}'"
        }

    return ToolResult(
        tool="generate_texture",
        request_id=ctx.request_id or "",
        run_id=ctx.run_id or "",
        result=result_data
    )

def export_asset(input: ExportAssetInput) -> ToolResult | ToolError:
    """
    Export an asset from Blender.
    """
    ctx = get_current_context()

    if not input.dry_run:
        try:
            transport = get_transport()
            response = transport.send_command("export_asset", input.model_dump())
            result_data = response.get("data", {})
        except Exception as e:
            return ToolError(
                tool="export_asset",
                request_id=ctx.request_id or "",
                run_id=ctx.run_id or "",
                error=ToolErrorDetail(code="EXECUTION_ERROR", message=str(e))
            )
    else:
        result_data = {
            "message": f"Exported '{input.object_name}' to '{input.filepath}'",
            "format": input.format
        }

    # Create export manifest
    manifest = ExportManifest(
        export_path=input.filepath,
        format=input.format,
        object_name=input.object_name,
        provenance={
            "tool": "mcp.export_asset",
            "run_id": ctx.run_id or "",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

    # Create artifact for the manifest
    artifact = Artifact(
        type="application/json",
        uri=f"file://{input.filepath}.manifest.json",
        content=manifest.model_dump_json(indent=2),
        metadata={"type": "export_manifest"}
    )

    return ToolResult(
        tool="export_asset",
        request_id=ctx.request_id or "",
        run_id=ctx.run_id or "",
        result=result_data,
        artifacts=[artifact]
    )
