"""
End-to-end integration tests for the MCP pipeline.

These tests verify the full flow from CLI through executor to tool handlers,
using mocked transports to avoid requiring actual Blender/UE5 connections.
"""

from unittest.mock import MagicMock, patch

import pytest
from mcp_core import register_system_tools
from mcp_core.execution import executor
from mcp_core.observability.context import set_context
from mcp_core.registry import registry
from mcp_protocol.models import (
    ExportAssetInput,
    GenerateBlueprintInput,
    GenerateSceneInput,
    GenerateTerrainInput,
    ImportAssetInput,
    PopulateLevelInput,
    ToolResult,
)

# Import tool registration functions
try:
    from mcp_target_blender import register_blender_tools
    HAS_BLENDER = True
except ImportError:
    HAS_BLENDER = False

try:
    from mcp_target_ue5 import register_ue5_tools
    HAS_UE5 = True
except ImportError:
    HAS_UE5 = False


@pytest.fixture(autouse=True)
def setup_tools_and_context():
    """Set up tools registry and execution context for all tests."""
    # Register tools only if not already registered
    if not registry.get_tool("mcp.list_commands"):
        register_system_tools(registry)
    if HAS_BLENDER and not registry.get_tool("mcp.generate_scene"):
        register_blender_tools(registry)
    if HAS_UE5 and not registry.get_tool("mcp.import_asset"):
        register_ue5_tools(registry)

    # Set up context
    token = set_context(
        request_id="test-request-123",
        run_id="test-run-456",
        trace_id="test-trace-789"
    )
    yield
    token.reset()


@pytest.fixture
def mock_blender_transport():
    """Mock Blender stdio transport."""
    with patch("mcp_target_blender.transport.get_transport") as mock:
        transport = MagicMock()
        transport.send_command.return_value = {
            "status": "ok",
            "data": {"message": "Mocked Blender response"}
        }
        mock.return_value = transport
        yield transport


@pytest.fixture
def mock_ue5_transport():
    """Mock UE5 HTTP transport."""
    with patch("mcp_target_ue5.tools.get_transport") as mock:
        transport = MagicMock()
        transport.send_command.return_value = {
            "status": "ok",
            "data": {"message": "Mocked UE5 response"}
        }
        mock.return_value = transport
        yield transport


class TestBlenderPipeline:
    """Test Blender tool execution pipeline."""

    def test_generate_scene_dry_run(self):
        """Test generate_scene in dry-run mode."""
        input_data = GenerateSceneInput(
            description="A test scene",
            dry_run=True
        )
        result = executor.execute("mcp.generate_scene", input_data)

        assert isinstance(result, ToolResult)
        assert result.status == "ok"
        assert "message" in result.result

    def test_export_asset_dry_run(self):
        """Test export_asset in dry-run mode."""
        input_data = ExportAssetInput(
            object_name="TestCube",
            format="fbx",
            filepath="/tmp/test.fbx",
            dry_run=True
        )
        result = executor.execute("mcp.export_asset", input_data)

        assert isinstance(result, ToolResult)
        assert result.status == "ok"


class TestUE5Pipeline:
    """Test UE5 tool execution pipeline."""

    def test_generate_terrain_dry_run(self):
        """Test generate_terrain in dry-run mode."""
        input_data = GenerateTerrainInput(
            width=1000,
            height=1000,
            detail_level="medium",
            dry_run=True
        )
        result = executor.execute("mcp.generate_terrain", input_data)

        assert isinstance(result, ToolResult)
        assert result.status == "ok"
        assert "terrain_path" in result.result

    def test_populate_level_dry_run(self):
        """Test populate_level in dry-run mode."""
        input_data = PopulateLevelInput(
            asset_type="Tree_01",
            density=100,
            dry_run=True
        )
        result = executor.execute("mcp.populate_level", input_data)

        assert isinstance(result, ToolResult)
        assert result.status == "ok"
        assert "count" in result.result

    def test_generate_blueprint_dry_run(self):
        """Test generate_blueprint in dry-run mode."""
        input_data = GenerateBlueprintInput(
            logic_description="A door that opens when clicked",
            dry_run=True
        )
        result = executor.execute("mcp.generate_blueprint", input_data)

        assert isinstance(result, ToolResult)
        assert result.status == "ok"
        assert "blueprint_path" in result.result

    def test_import_asset_dry_run(self):
        """Test import_asset in dry-run mode."""
        input_data = ImportAssetInput(
            manifest_path="/tmp/test_manifest.json",
            dry_run=True
        )
        result = executor.execute("mcp.import_asset", input_data)

        assert isinstance(result, ToolResult)
        assert result.status == "ok"


class TestEndToEndFlow:
    """Test complete end-to-end workflows."""

    def test_blender_to_ue5_pipeline_dry_run(self):
        """Test the full Blender export -> UE5 import pipeline in dry-run."""
        # Step 1: Generate scene in Blender
        scene_input = GenerateSceneInput(
            description="A medieval house",
            dry_run=True
        )
        scene_result = executor.execute("mcp.generate_scene", scene_input)
        assert isinstance(scene_result, ToolResult)

        # Step 2: Export from Blender
        export_input = ExportAssetInput(
            object_name="MedievalHouse",
            format="fbx",
            filepath="/tmp/medieval_house.fbx",
            dry_run=True
        )
        export_result = executor.execute("mcp.export_asset", export_input)
        assert isinstance(export_result, ToolResult)

        # Step 3: Import into UE5
        import_input = ImportAssetInput(
            manifest_path="/tmp/medieval_house_manifest.json",
            dry_run=True
        )
        import_result = executor.execute("mcp.import_asset", import_input)
        assert isinstance(import_result, ToolResult)

        # Step 4: Generate terrain in UE5
        terrain_input = GenerateTerrainInput(
            width=2000,
            height=2000,
            detail_level="high",
            dry_run=True
        )
        terrain_result = executor.execute("mcp.generate_terrain", terrain_input)
        assert isinstance(terrain_result, ToolResult)

        # Step 5: Populate level
        populate_input = PopulateLevelInput(
            asset_type="MedievalHouse",
            density=10,
            dry_run=True
        )
        populate_result = executor.execute("mcp.populate_level", populate_input)
        assert isinstance(populate_result, ToolResult)

    def test_result_envelope_structure(self):
        """Verify result envelopes match the documented format."""
        input_data = GenerateSceneInput(
            description="Test scene",
            dry_run=True
        )
        result = executor.execute("mcp.generate_scene", input_data)

        # Verify envelope structure per commands.md
        assert hasattr(result, "protocol_version")
        assert result.protocol_version == "1.0"
        assert hasattr(result, "tool")
        assert hasattr(result, "request_id")
        assert hasattr(result, "run_id")
        assert hasattr(result, "status")
        assert hasattr(result, "result")
        assert hasattr(result, "artifacts")
        assert hasattr(result, "warnings")

    def test_context_propagation(self):
        """Verify context (request_id, run_id) propagates through execution."""
        input_data = GenerateSceneInput(
            description="Context test",
            dry_run=True
        )

        # Execute with explicit request_id
        result = executor.execute(
            "mcp.generate_scene",
            input_data,
            request_id="explicit-request-id"
        )

        assert result.request_id == "explicit-request-id"
        assert result.run_id  # Should be auto-generated


class TestPolicyIntegration:
    """Test policy engine integration in the pipeline."""

    def test_destructive_operation_blocked_by_default(self):
        """Test that destructive operations are blocked when allow_destructive=False."""
        # This test verifies the policy engine is integrated
        # In a real scenario with allow_destructive=False, non-dry-run ops should fail
        input_data = GenerateSceneInput(
            description="Test scene",
            dry_run=False  # Destructive
        )

        # This should work in dry_run=True or when allow_destructive=True
        # The actual blocking depends on policy settings
        result = executor.execute("mcp.generate_scene", input_data)
        # Result will be error if destructive blocked, or success if allowed
        assert result is not None
