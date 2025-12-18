from mcp_core.config.settings import McpSettings


def test_defaults():
    settings = McpSettings()
    assert settings.logging.level == "INFO"
    assert settings.ai.enabled is True
    assert settings.blender.scene_generation.default_style == "realistic"

def test_env_override(monkeypatch):
    monkeypatch.setenv("MCP_LOGGING__LEVEL", "DEBUG")
    monkeypatch.setenv("MCP_AI__ENABLED", "false")
    monkeypatch.setenv("MCP_UE5__PERFORMANCE__MAX_POLYCOUNT", "100")

    settings = McpSettings()
    assert settings.logging.level == "DEBUG"
    assert settings.ai.enabled is False
    assert settings.ue5.performance.max_polycount == 100

def test_artifacts_path_expansion():
    # pydantic-settings expands user path if it starts with ~
    # We can't easily test exact path since it depends on the user,
    # but we can check it's absolute
    settings = McpSettings()
    assert settings.artifacts.root.is_absolute()
