from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class LoggingConfig(BaseSettings):
    level: str = "INFO"
    format: Literal["json", "text"] = "json"
    output: str = "stdout"

class ArtifactsConfig(BaseSettings):
    root: Path = Path("~/.mcp/artifacts").expanduser()
    write_manifests: bool = True

class PolicyConfig(BaseSettings):
    allow_destructive: bool = False
    allowed_paths: list[str] = Field(default_factory=list)
    tool_allowlist: list[str] = Field(default_factory=list)

class AIBudgetConfig(BaseSettings):
    max_requests_per_run: int = 20
    max_total_tokens: int = 20000
    max_total_cost_usd: float = 5.0
    timeout_seconds: int = 60

class AIConfig(BaseSettings):
    enabled: bool = True
    provider: str = "openai"
    budget: AIBudgetConfig = Field(default_factory=AIBudgetConfig)

class SafetyConfig(BaseSettings):
    block_injection_patterns: bool = True
    allowed_tools: list[str] | None = None
    deny_tools: list[str] = ["os.system", "subprocess.call", "eval", "exec"]

class BlenderSceneGenerationConfig(BaseSettings):
    default_style: str = "realistic"
    object_variation: bool = True
    default_seed: int = 0

class BlenderAssetProcessingConfig(BaseSettings):
    texture_resolution: str = "4K"
    lod_levels: int = 3
    batch_processing: bool = True

class BlenderExportConfig(BaseSettings):
    default_format: str = "fbx"
    include_textures_by_default: bool = False
    axis: str = "-Z+Y"
    scale: float = 1.0

class BlenderTransportConfig(BaseSettings):
    executable_path: str = "blender"

class BlenderConfig(BaseSettings):
    transport: BlenderTransportConfig = Field(default_factory=BlenderTransportConfig)
    scene_generation: BlenderSceneGenerationConfig = Field(default_factory=BlenderSceneGenerationConfig)
    asset_processing: BlenderAssetProcessingConfig = Field(default_factory=BlenderAssetProcessingConfig)
    export: BlenderExportConfig = Field(default_factory=BlenderExportConfig)

class UE5LevelDesignConfig(BaseSettings):
    default_terrain_size: tuple[int, int] = (1000, 1000)
    auto_populate: bool = False
    default_seed: int = 0

class UE5PerformanceBudgetsConfig(BaseSettings):
    max_instances: int = 200000
    max_draw_calls: int = 5000

class UE5PerformanceConfig(BaseSettings):
    dynamic_lighting: bool = False
    max_polycount: int = 500000
    physics_enabled: bool = True
    budgets: UE5PerformanceBudgetsConfig = Field(default_factory=UE5PerformanceBudgetsConfig)

class UE5TransportConfig(BaseSettings):
    host: str = "localhost"
    port: int = 8080

class UE5Config(BaseSettings):
    transport: UE5TransportConfig = Field(default_factory=UE5TransportConfig)
    level_design: UE5LevelDesignConfig = Field(default_factory=UE5LevelDesignConfig)
    performance: UE5PerformanceConfig = Field(default_factory=UE5PerformanceConfig)

class McpSettings(BaseSettings):
    protocol_version: str = "1.0"
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    artifacts: ArtifactsConfig = Field(default_factory=ArtifactsConfig)
    policy: PolicyConfig = Field(default_factory=PolicyConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    blender: BlenderConfig = Field(default_factory=BlenderConfig)
    ue5: UE5Config = Field(default_factory=UE5Config)

    model_config = SettingsConfigDict(
        env_prefix="MCP_",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            JsonConfigSettingsSource(
                settings_cls,
                json_file=Path("~/.mcp/blender_mcp_config.json").expanduser()
            ),
            JsonConfigSettingsSource(
                settings_cls,
                json_file=Path("~/.mcp/ue5_mcp_config.json").expanduser()
            ),
            file_secret_settings,
        )

# Global settings instance loaded with defaults, config files, and environment variables
settings = McpSettings()
