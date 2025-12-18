from mcp_protocol.models import (
    AddObjectInput,
    GenerateSceneInput,
    ToolError,
    ToolErrorDetail,
    ToolResult,
    Vec3,
)


def test_vec3_model():
    v = Vec3(x=1.0, y=2.0, z=3.0)
    assert v.x == 1.0
    assert v.y == 2.0
    assert v.z == 3.0

def test_generate_scene_input_defaults():
    inp = GenerateSceneInput(description="A test scene")
    assert inp.description == "A test scene"
    assert inp.dry_run is False
    assert inp.seed is None

def test_add_object_input_nested():
    inp = AddObjectInput(
        object_type="Cube",
        location=Vec3(x=0, y=0, z=0)
    )
    assert inp.location.x == 0

def test_tool_result_serialization():
    res = ToolResult(
        tool="mcp.test",
        request_id="req-1",
        run_id="run-1",
        result={"foo": "bar"}
    )
    data = res.model_dump()
    assert data["status"] == "ok"
    assert data["protocol_version"] == "1.0"
    assert data["result"]["foo"] == "bar"

def test_tool_error_serialization():
    err = ToolError(
        tool="mcp.test",
        request_id="req-1",
        run_id="run-1",
        error=ToolErrorDetail(
            code="TEST_ERROR",
            message="Something went wrong"
        )
    )
    data = err.model_dump()
    assert data["status"] == "error"
    assert data["error"]["code"] == "TEST_ERROR"
