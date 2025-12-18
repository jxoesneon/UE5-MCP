import pytest
from mcp_core.observability.context import set_context
from mcp_protocol.models import (
    AddObjectInput,
    ExportAssetInput,
    GenerateSceneInput,
    GenerateTextureInput,
    Vec3,
)
from mcp_target_blender.tools import (
    add_object,
    export_asset,
    generate_scene,
    generate_texture,
)
from mcp_target_blender.transport import StdioTransport


@pytest.fixture
def context_setup():
    """Setup execution context for tests."""
    token = set_context(
        request_id="req-123",
        run_id="run-456",
        trace_id="trace-789",
        tool_name="test_tool"
    )
    yield
    token.reset()


def test_generate_scene(context_setup) -> None:
    input_data = GenerateSceneInput(
        description="A test scene",
        style="low_poly",
        seed=42
    )
    result = generate_scene(input_data)
    assert result.status == "ok"
    assert result.result["message"] == "Scene generated: A test scene"
    assert result.result["style"] == "low_poly"
    assert result.result["seed"] == 42
    assert result.request_id == "req-123"
    assert result.run_id == "run-456"


def test_add_object(context_setup) -> None:
    input_data = AddObjectInput(
        object_type="Cube",
        location=Vec3(x=1.0, y=2.0, z=3.0)
    )
    result = add_object(input_data)
    assert result.status == "ok"
    assert result.result["message"] == "Added object: Cube"
    assert result.result["location"] == {"x": 1.0, "y": 2.0, "z": 3.0}


def test_generate_texture(context_setup) -> None:
    input_data = GenerateTextureInput(
        object_name="Cube",
        texture_type="wood"
    )
    result = generate_texture(input_data)
    assert result.status == "ok"
    assert result.result["message"] == "Generated texture 'wood' for 'Cube'"


def test_export_asset_dry_run(context_setup) -> None:
    input_data = ExportAssetInput(
        object_name="Cube",
        format="fbx",
        filepath="/tmp/cube.fbx",
        dry_run=True
    )
    result = export_asset(input_data)
    assert result.status == "ok"
    assert result.result["message"] == "Exported 'Cube' to '/tmp/cube.fbx'"
    
    # Check artifacts
    assert len(result.artifacts) == 1
    artifact = result.artifacts[0]
    assert artifact.type == "application/json"
    assert artifact.metadata["type"] == "export_manifest"
    
    # Verify manifest content
    import json
    manifest = json.loads(artifact.content)
    assert manifest["object_name"] == "Cube"
    assert manifest["format"] == "fbx"
    assert manifest["export_path"] == "/tmp/cube.fbx"
    assert manifest["provenance"]["tool"] == "mcp.export_asset"
    assert manifest["provenance"]["run_id"] == "run-456"


def test_transport_instantiation() -> None:
    transport = StdioTransport()
    assert transport.blender_path == "blender"
    
    # Test stub methods
    transport.connect()
    resp = transport.send_command("ping", {})
    assert resp["status"] == "ok"
    transport.disconnect()
