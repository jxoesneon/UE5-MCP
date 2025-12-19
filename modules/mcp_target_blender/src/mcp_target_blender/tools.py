import asyncio
import json
from datetime import datetime

import httpx
from mcp_core.ai import PromptTemplate, create_ai_client
from mcp_core.ai.models import ImageGenerationRequest
from mcp_core.config.settings import settings
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


SCENE_GENERATION_PROMPT = PromptTemplate(
    name="scene_generation",
    version=1,
    template="""
    You are a 3D scene layout assistant.
    Analyze the following scene description and generate a JSON list of objects to populate the scene.
    Each object should have:
    - object_type: one of [cube, sphere, plane, cylinder, cone, monkey]
    - location: {x: float, y: float, z: float}
    - name: optional string

    Description: {description}
    Style: {style}

    Output ONLY valid JSON:
    [
        {{"object_type": "cube", "location": {{"x": 0, "y": 0, "z": 0}}, "name": "CenterCube"}}
    ]
    """,
    input_variables=["description", "style"]
)

def generate_scene(input: GenerateSceneInput) -> ToolResult | ToolError:
    """
    Generate a Blender scene based on a description.
    """
    ctx = get_current_context()

    if not input.dry_run:
        try:
            # AI Interpretation step
            objects_to_create = []
            if settings.ai.enabled:
                try:
                    ai_client = create_ai_client()
                    ai_client.prompt_registry.register(SCENE_GENERATION_PROMPT)

                    ai_response = asyncio.run(ai_client.generate(
                        prompt_name="scene_generation",
                        variables={"description": input.description, "style": input.style or "default"}
                    ))

                    # Parse JSON from AI response
                    # Robust parsing needed for real world, assuming clean JSON for now or stripping markdown code blocks
                    content = ai_response.content.strip()
                    if content.startswith("```json"):
                        content = content[7:-3]
                    elif content.startswith("```"):
                        content = content[3:-3]

                    objects_to_create = json.loads(content)
                except Exception as e:
                    # Fallback or partial failure
                    print(f"AI generation failed: {e}")
                    # We continue with empty list or basic setup

            # Prepare payload for Blender
            payload = input.model_dump()
            if objects_to_create:
                payload["objects"] = objects_to_create

            transport = get_transport()
            transport_response = transport.send_command("generate_scene", payload)
            result_data = transport_response.get("data", {})

            # Augment result with AI trace if available
            if objects_to_create:
                result_data["ai_generated_objects"] = len(objects_to_create)

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
            texture_path = None
            generated_artifacts = []

            if settings.ai.enabled:
                try:
                    ai_client = create_ai_client()

                    req = ImageGenerationRequest(
                        prompt=input.texture_type,
                        n=1,
                        size="1024x1024"
                    )

                    # Need to wrap in asyncio.run since we are in sync context
                    response = asyncio.run(ai_client.provider.generate_image(req))

                    if response.urls:
                        image_url = response.urls[0]

                        # Download the image
                        async def download_image():
                            async with httpx.AsyncClient() as client:
                                resp = await client.get(image_url)
                                resp.raise_for_status()
                                return resp.content

                        image_data = asyncio.run(download_image())

                        # Save to artifacts
                        filename = f"texture_{ctx.run_id}_{datetime.now().strftime('%H%M%S')}.png"

                        # Ensure artifacts dir exists
                        artifacts_dir = settings.artifacts.root
                        artifacts_dir.mkdir(parents=True, exist_ok=True)

                        texture_path = str(artifacts_dir / filename)
                        with open(texture_path, "wb") as f:
                            f.write(image_data)

                        # Create artifact object
                        generated_artifacts.append(Artifact(
                            type="image/png",
                            uri=f"file://{texture_path}",
                            content="",
                            metadata={"source": "ai_generation", "prompt": input.texture_type}
                        ))

                except Exception as e:
                     print(f"AI texture generation failed: {e}")

            # Prepare payload
            payload = input.model_dump()
            if texture_path:
                payload["texture_path"] = texture_path

            transport = get_transport()
            transport_response = transport.send_command("generate_texture", payload)
            result_data = transport_response.get("data", {})

            if texture_path:
                result_data["texture_path"] = texture_path

            return ToolResult(
                tool="generate_texture",
                request_id=ctx.request_id or "",
                run_id=ctx.run_id or "",
                result=result_data,
                artifacts=generated_artifacts
            )

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
