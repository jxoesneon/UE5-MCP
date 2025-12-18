import json
from unittest.mock import MagicMock, patch

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
    get_transport,
)
from mcp_target_blender.transport import StdioTransport


@pytest.fixture
def context_setup():
    """Setup execution context for tests."""
    # Reset global transport
    import mcp_target_blender.tools
    mcp_target_blender.tools._transport = None
    
    token = set_context(
        request_id="req-123",
        run_id="run-456",
        trace_id="trace-789",
        tool_name="test_tool"
    )
    yield
    token.reset()
    mcp_target_blender.tools._transport = None


@pytest.fixture
def mock_subprocess():
    with patch("subprocess.Popen") as mock_popen:
        process_mock = MagicMock()
        mock_popen.return_value = process_mock
        
        # Setup stdin/stdout mocks
        process_mock.stdin = MagicMock()
        process_mock.stdout = MagicMock()
        process_mock.terminate = MagicMock()
        process_mock.wait = MagicMock()
        process_mock.kill = MagicMock()
        
        yield process_mock


def test_generate_scene_dry_run(context_setup) -> None:
    input_data = GenerateSceneInput(
        description="A test scene",
        style="low_poly",
        seed=42,
        dry_run=True
    )
    result = generate_scene(input_data)
    assert result.status == "ok"
    assert result.result["message"] == "Scene generated: A test scene"
    assert result.result["style"] == "low_poly"
    assert result.result["seed"] == 42
    assert result.request_id == "req-123"
    assert result.run_id == "run-456"


def test_generate_scene_live(context_setup, mock_subprocess) -> None:
    # Setup mock response from Blender
    response = {
        "id": 1,
        "status": "ok",
        "data": {
            "message": "Scene generated: Live run",
            "objects_count": 5
        }
    }
    mock_subprocess.stdout.readline.return_value = json.dumps(response)
    
    input_data = GenerateSceneInput(
        description="Live run",
        dry_run=False
    )
    
    result = generate_scene(input_data)
    
    assert result.status == "ok"
    assert result.result["message"] == "Scene generated: Live run"
    assert result.result["objects_count"] == 5
    
    # Verify command sent to Blender
    args, _ = mock_subprocess.stdin.write.call_args
    sent_request = json.loads(args[0])
    assert sent_request["command"] == "generate_scene"
    assert sent_request["params"]["description"] == "Live run"


def test_add_object_dry_run(context_setup) -> None:
    input_data = AddObjectInput(
        object_type="Cube",
        location=Vec3(x=1.0, y=2.0, z=3.0),
        dry_run=True
    )
    result = add_object(input_data)
    assert result.status == "ok"
    assert result.result["message"] == "Added object: Cube"
    assert result.result["location"] == {"x": 1.0, "y": 2.0, "z": 3.0}


def test_add_object_live(context_setup, mock_subprocess) -> None:
    # Setup mock response from Blender
    response = {
        "id": 1,
        "status": "ok",
        "data": {
            "message": "Added object: Sphere",
            "name": "Sphere",
            "location": {"x": 1.0, "y": 2.0, "z": 3.0}
        }
    }
    mock_subprocess.stdout.readline.return_value = json.dumps(response)
    
    input_data = AddObjectInput(
        object_type="Sphere",
        location=Vec3(x=1.0, y=2.0, z=3.0),
        dry_run=False
    )
    
    result = add_object(input_data)
    
    assert result.status == "ok"
    assert result.result["message"] == "Added object: Sphere"
    assert result.result["name"] == "Sphere"
    
    # Verify command sent to Blender
    args, _ = mock_subprocess.stdin.write.call_args
    sent_request = json.loads(args[0])
    assert sent_request["command"] == "add_object"
    assert sent_request["params"]["object_type"] == "Sphere"
    assert sent_request["params"]["location"] == {"x": 1.0, "y": 2.0, "z": 3.0}


def test_generate_texture_dry_run(context_setup) -> None:
    input_data = GenerateTextureInput(
        object_name="Cube",
        texture_type="wood",
        dry_run=True
    )
    result = generate_texture(input_data)
    assert result.status == "ok"
    assert result.result["message"] == "Generated texture 'wood' for 'Cube'"


def test_generate_texture_live(context_setup, mock_subprocess) -> None:
    # Setup mock response from Blender
    response = {
        "id": 1,
        "status": "ok",
        "data": {
            "message": "Generated texture 'marble' for 'Sphere'",
            "texture_path": "/tmp/marble.png"
        }
    }
    mock_subprocess.stdout.readline.return_value = json.dumps(response)
    
    input_data = GenerateTextureInput(
        object_name="Sphere",
        texture_type="marble",
        dry_run=False
    )
    
    result = generate_texture(input_data)
    
    assert result.status == "ok"
    assert result.result["message"] == "Generated texture 'marble' for 'Sphere'"
    assert result.result["texture_path"] == "/tmp/marble.png"
    
    # Verify command sent to Blender
    args, _ = mock_subprocess.stdin.write.call_args
    sent_request = json.loads(args[0])
    assert sent_request["command"] == "generate_texture"
    assert sent_request["params"]["object_name"] == "Sphere"
    assert sent_request["params"]["texture_type"] == "marble"


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


def test_export_asset_live(context_setup, mock_subprocess) -> None:
    # Setup mock response from Blender
    response = {
        "id": 1,
        "status": "ok",
        "data": {
            "message": "Exported 'Sphere' to '/tmp/sphere.obj'",
            "file_size": 1024
        }
    }
    mock_subprocess.stdout.readline.return_value = json.dumps(response)
    
    input_data = ExportAssetInput(
        object_name="Sphere",
        format="obj",
        filepath="/tmp/sphere.obj",
        dry_run=False
    )
    
    result = export_asset(input_data)
    
    assert result.status == "ok"
    assert result.result["message"] == "Exported 'Sphere' to '/tmp/sphere.obj'"
    
    # Verify command sent to Blender
    args, _ = mock_subprocess.stdin.write.call_args
    sent_request = json.loads(args[0])
    assert sent_request["command"] == "export_asset"
    assert sent_request["params"]["object_name"] == "Sphere"
    assert sent_request["params"]["filepath"] == "/tmp/sphere.obj"
    
    # Check artifacts are still created in live run (if expected)
    # The current implementation creates artifacts in live run too (see tools.py)
    assert len(result.artifacts) == 1
    artifact = result.artifacts[0]
    assert artifact.type == "application/json"
    assert artifact.metadata["type"] == "export_manifest"


def test_transport_connection(mock_subprocess) -> None:
    transport = StdioTransport(blender_path="blender_mock")
    
    # Test connect
    transport.connect()
    assert mock_subprocess.stdin is not None
    
    # Test send_command
    response_data = {"status": "ok", "data": "pong"}
    mock_subprocess.stdout.readline.return_value = json.dumps(response_data)
    
    resp = transport.send_command("ping", {})
    assert resp["status"] == "ok"
    assert resp["data"] == "pong"
    
    # Verify write
    mock_subprocess.stdin.write.assert_called()
    
    # Test disconnect
    transport.disconnect()
    mock_subprocess.terminate.assert_called()
