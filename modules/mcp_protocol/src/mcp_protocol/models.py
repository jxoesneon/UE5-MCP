from typing import Any, Literal

from pydantic import BaseModel, Field


class Artifact(BaseModel):
    type: str
    uri: str | None = None
    content: str | None = None
    metadata: dict[str, Any] | None = None

class ToolResult(BaseModel):
    protocol_version: Literal["1.0"] = "1.0"
    tool: str
    request_id: str
    run_id: str
    status: Literal["ok"] = "ok"
    result: dict[str, Any]
    artifacts: list[Artifact] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

class ToolErrorDetail(BaseModel):
    code: str
    message: str
    retriable: bool = False
    details: dict[str, Any] = Field(default_factory=dict)

class ToolError(BaseModel):
    protocol_version: Literal["1.0"] = "1.0"
    tool: str
    request_id: str
    run_id: str
    status: Literal["error"] = "error"
    error: ToolErrorDetail

class RunManifest(BaseModel):
    run_id: str
    request_id: str
    tool_name: str
    status: str
    start_time: str
    end_time: str
    duration_seconds: float
    inputs: dict[str, Any]
    outputs: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
    artifacts: list[Artifact] = Field(default_factory=list)
    config_hash: str | None = None
    tool_version: str | None = None

# --- Blender Tool Inputs ---

class Vec3(BaseModel):
    x: float
    y: float
    z: float

class GenerateSceneInput(BaseModel):
    description: str
    seed: int | None = None
    style: str | None = None
    dry_run: bool = False

class AddObjectInput(BaseModel):
    object_type: str
    location: Vec3
    dry_run: bool = False

class GenerateTextureInput(BaseModel):
    object_name: str
    texture_type: str
    dry_run: bool = False

class ExportAssetInput(BaseModel):
    object_name: str
    format: Literal["fbx", "obj", "gltf"]
    filepath: str
    include_textures: bool = True
    overwrite: bool = False

# --- UE5 Tool Inputs ---

class ImportAssetInput(BaseModel):
    manifest_path: str
    dry_run: bool = False
    overwrite: bool = False

class GenerateTerrainInput(BaseModel):
    width: int
    height: int
    detail_level: Literal["low", "medium", "high"]
    seed: int | None = None
    dry_run: bool = False

class PopulateLevelInput(BaseModel):
    asset_type: str
    density: int
    seed: int | None = None
    budget_max_instances: int | None = None
    dry_run: bool = False

class GenerateBlueprintInput(BaseModel):
    logic_description: str
    dry_run: bool = False

class ProfilePerformanceInput(BaseModel):
    level_name: str

class OptimizeLevelInput(BaseModel):
    dry_run: bool = False
    budgets: dict[str, Any] | None = None

class DebugBlueprintInput(BaseModel):
    blueprint_name: str

# --- System Tool Inputs ---

class ListCommandsInput(BaseModel):
    pass

class HelpInput(BaseModel):
    command_name: str

class ConfigGetInput(BaseModel):
    key: str

class ConfigSetInput(BaseModel):
    key: str
    value: Any

class ResetConfigInput(BaseModel):
    confirm: bool = False
