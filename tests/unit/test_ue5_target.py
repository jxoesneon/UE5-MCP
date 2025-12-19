from unittest.mock import MagicMock, patch

import pytest
from mcp_core.observability.context import set_context
from mcp_protocol.models import (
    DebugBlueprintInput,
    GenerateBlueprintInput,
    GenerateTerrainInput,
    ImportAssetInput,
    OptimizeLevelInput,
    PopulateLevelInput,
    ProfilePerformanceInput,
)
from mcp_target_ue5.tools import (
    debug_blueprint,
    generate_blueprint,
    generate_terrain,
    import_asset,
    optimize_level,
    populate_level,
    profile_performance,
)
from mcp_target_ue5.transport import HttpTransport


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


def test_import_asset(context_setup) -> None:
    input_data = ImportAssetInput(
        manifest_path="./test_manifest.json",
        dry_run=True,
        overwrite=False
    )
    result = import_asset(input_data)
    assert result.status == "ok"
    assert result.result["message"] == "Imported asset from './test_manifest.json'"
    assert result.request_id == "req-123"
    assert result.run_id == "run-456"


def test_generate_terrain(context_setup) -> None:
    input_data = GenerateTerrainInput(
        width=1000,
        height=1000,
        detail_level="high",
        seed=12345,
        dry_run=True
    )
    result = generate_terrain(input_data)
    assert result.status == "ok"
    assert result.result["message"] == "Generated 1000x1000 terrain (high)"
    assert result.result["terrain_path"] == "/Game/Maps/GeneratedTerrain"


def test_populate_level(context_setup) -> None:
    input_data = PopulateLevelInput(
        asset_type="Tree_01",
        density=100,
        seed=12345,
        dry_run=True
    )
    result = populate_level(input_data)
    assert result.status == "ok"
    assert result.result["message"] == "Populated level with 100 instances of 'Tree_01'"
    assert result.result["count"] == 100


def test_generate_blueprint(context_setup) -> None:
    input_data = GenerateBlueprintInput(
        logic_description="A simple door",
        dry_run=True
    )
    result = generate_blueprint(input_data)
    assert result.status == "ok"
    assert result.result["message"] == "Blueprint generated from description"
    assert result.result["status"] == "compiled"


def test_profile_performance(context_setup) -> None:
    input_data = ProfilePerformanceInput(
        level_name="TestLevel",
        dry_run=True
    )
    result = profile_performance(input_data)
    assert result.status == "ok"
    assert result.result["message"] == "Profiled level 'TestLevel'"
    assert "fps_avg" in result.result


def test_optimize_level(context_setup) -> None:
    input_data = OptimizeLevelInput(
        dry_run=True
    )
    result = optimize_level(input_data)
    assert result.status == "ok"
    assert result.result["message"] == "Optimization pass complete"


def test_debug_blueprint(context_setup) -> None:
    input_data = DebugBlueprintInput(
        blueprint_name="BP_Door",
        dry_run=True
    )
    result = debug_blueprint(input_data)
    assert result.status == "ok"
    assert result.result["message"] == "Debugged blueprint 'BP_Door'"


def test_transport_instantiation() -> None:
    transport = HttpTransport(host="localhost", port=8080)
    assert transport.base_url == "http://localhost:8080"

    # Test with mocked HTTP calls
    with patch("httpx.get") as mock_get, patch("httpx.post") as mock_post:
        # Mock health check
        mock_get.return_value = MagicMock(status_code=200)
        mock_get.return_value.raise_for_status = MagicMock()

        # Mock command response
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()
        mock_post.return_value.json.return_value = {"status": "ok", "data": {}}

        transport.connect()
        resp = transport.send_command("ping", {})
        assert resp["status"] == "ok"
        transport.disconnect()
