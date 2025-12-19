# MCP API Reference

## Overview
This document defines the **programmatic contract** for MCP tools. It is designed to be usable from:

- a CLI (`commands.md`)
- an agent/tool runtime
- a Python API surface (implementation-defined)

The authoritative contract is the **tool schema + result envelope**. Language-specific APIs are convenience layers over the same tool definitions.

## Versioning
- **Protocol version**: semantic versioning (e.g., `1.0`).
- **Tool schema version**: tools may evolve; breaking changes require a major bump.

## Common Types

### Tool Result Envelope
All tools MUST return a structured envelope.

```json
{
  "protocol_version": "1.0",
  "tool": "mcp.generate_scene",
  "request_id": "...",
  "run_id": "...",
  "status": "ok",
  "result": {},
  "artifacts": [],
  "warnings": []
}
```

### Error Envelope

```json
{
  "protocol_version": "1.0",
  "tool": "mcp.generate_terrain",
  "request_id": "...",
  "run_id": "...",
  "status": "error",
  "error": {
    "code": "TARGET_UNAVAILABLE",
    "message": "UE5 editor is not reachable",
    "retriable": true,
    "details": {}
  }
}
```

Recommended error codes:

- `VALIDATION_ERROR`
- `POLICY_DENIED`
- `TARGET_UNAVAILABLE`
- `TIMEOUT`
- `DEPENDENCY_MISSING`
- `IO_ERROR`
- `INTERNAL_ERROR`
- `EXECUTION_ERROR`
- `NOT_IMPLEMENTED`
- `CONFIRMATION_REQUIRED`
- `CONFIG_KEY_NOT_FOUND`
- `TOOL_NOT_FOUND`

## Execution Semantics
- Tools MUST declare whether they are **read-only** or have **side effects**.
- Tools SHOULD support `dry_run` where meaningful.
- Tools SHOULD support deterministic outputs via `seed` when randomness is involved.

## 1. Blender-MCP Tools

### `mcp.generate_scene`
- **Purpose**: Generate a scene scaffold in Blender.
- **Inputs**:
  - `description` (string)
  - `seed` (integer, optional)
  - `style` (string, optional)
  - `dry_run` (boolean, optional)
- **Side effects**: Mutates Blender state when `dry_run=false`.
- **Determinism**: SHOULD be deterministic for a fixed `seed` and tool version.
- **Result** (conceptual):
  - `scene_id`
  - `objects_created[]`
  - `collections_created[]`

### `mcp.add_object`
- **Purpose**: Add an object instance to the active scene.
- **Inputs**:
  - `object_type` (string)
  - `location` (object: `{ "x": number, "y": number, "z": number }`)
  - `dry_run` (boolean, optional)
- **Side effects**: Mutates Blender state when `dry_run=false`.
- **Result** (conceptual):
  - `object_name`
  - `object_id`

### `mcp.generate_texture`
- **Purpose**: Generate/apply a material/texture.
- **Inputs**:
  - `object_name` (string)
  - `texture_type` (string)
  - `dry_run` (boolean, optional)
- **Side effects**: Mutates Blender material graph when `dry_run=false`.
- **AI**: If AI is used, tool MUST emit provenance (provider/model/prompt hash).
- **Result** (conceptual):
  - `material_name`
  - `texture_assets[]`

### `mcp.export_asset`
- **Purpose**: Export an object and produce an export manifest.
- **Inputs**:
  - `object_name` (string)
  - `format` (enum: `fbx`, `obj`, `gltf`)
  - `filepath` (string)
  - `include_textures` (boolean, optional)
  - `overwrite` (boolean, optional)
- **Side effects**: Writes files to disk.
- **Result** (conceptual):
  - `export_path`
  - `manifest_path`

## 2. UE5-MCP Tools

### `mcp.import_asset`
- **Purpose**: Import assets into UE5 by consuming an export manifest produced by `mcp.export_asset`.
- **Inputs**:
  - `manifest_path` (string)
  - `dry_run` (boolean, optional)
  - `overwrite` (boolean, optional)
- **Side effects**: Writes assets into the UE project when `dry_run=false`.
- **Result** (conceptual):
  - `imported_assets[]`
  - `import_summary`
  - `warnings[]`

### `mcp.generate_terrain`
- **Purpose**: Generate terrain using UE5 Editor scripting/PCG.
- **Inputs**:
  - `width` (integer)
  - `height` (integer)
  - `detail_level` (enum: `low`, `medium`, `high`)
  - `seed` (integer, optional)
  - `dry_run` (boolean, optional)
- **Side effects**: Mutates UE5 project when `dry_run=false`.
- **Result** (conceptual):
  - `terrain_asset_path`
  - `parameters`

### `mcp.populate_level`
- **Purpose**: Populate a level with instanced assets.
- **Inputs**:
  - `asset_type` (string)
  - `density` (integer)
  - `seed` (integer, optional)
  - `budget_max_instances` (integer, optional)
  - `dry_run` (boolean, optional)
- **Side effects**: Mutates UE5 level when `dry_run=false`.
- **Result** (conceptual):
  - `placements_created`
  - `warnings[]`

### `mcp.generate_blueprint`
- **Purpose**: Create or modify Blueprint logic.
- **Inputs**:
  - `logic_description` (string)
  - `dry_run` (boolean, optional)
- **Side effects**: Mutates Blueprint assets when `dry_run=false`.
- **Result** (conceptual):
  - `blueprints_modified[]`
  - `compile_status`

### `mcp.profile_performance`
- **Purpose**: Generate a performance report artifact.
- **Inputs**:
  - `level_name` (string)
- **Side effects**: None expected (reads project state).
- **Result** (conceptual):
  - `report_artifact`

### `mcp.optimize_level`
- **Purpose**: Apply safe optimizations guided by explicit budgets.
- **Inputs**:
  - `dry_run` (boolean, optional)
  - `budgets` (object, optional)
- **Side effects**: Mutates UE5 project state when `dry_run=false`.
- **Result** (conceptual):
  - `changes_applied[]`
  - `warnings[]`

### `mcp.debug_blueprint`
- **Purpose**: Diagnose common Blueprint failures.
- **Inputs**:
  - `blueprint_name` (string)
- **Side effects**: None by default.

## 3. System Tools

### `mcp.list_commands`
- **Purpose**: List all available tools and their schemas.
- **Inputs**: None
- **Side effects**: None
- **Result**: Array of tool definitions with names, descriptions, and input schemas.

### `mcp.help`
- **Purpose**: Get detailed help for a specific tool.
- **Inputs**:
  - `command_name` (string)
- **Side effects**: None
- **Result**: Tool name, description, and full input schema.

### `mcp.config_get`
- **Purpose**: Read an effective configuration value.
- **Inputs**:
  - `key` (string) - Dot-notation path (e.g., `logging.level`)
- **Side effects**: None
- **Result**: Key-value pair. Secrets are redacted.

### `mcp.config_set`
- **Purpose**: Set a configuration value at runtime.
- **Inputs**:
  - `key` (string)
  - `value` (any)
- **Side effects**: Modifies runtime configuration.
- **Status**: Not yet implemented. Use environment variables or config files.

### `mcp.reset_config`
- **Purpose**: Reset configuration to defaults.
- **Inputs**:
  - `confirm` (boolean) - Must be true to proceed.
- **Side effects**: Destructive write.
- **Status**: Not yet implemented.

## Transport Layer

### Blender Transport (Stdio)

MCP communicates with Blender via subprocess stdin/stdout:

```python
from mcp_target_blender.transport import StdioTransport

transport = StdioTransport(blender_path="/path/to/blender")
transport.connect()  # Launches Blender subprocess
response = transport.send_command("generate_scene", {"description": "..."})
transport.disconnect()  # Terminates subprocess
```

### UE5 Transport (HTTP)

MCP communicates with UE5 via HTTP to a plugin server:

```python
from mcp_target_ue5.transport import HttpTransport

transport = HttpTransport(host="localhost", port=8080)
transport.connect()  # Health check
response = transport.send_command("generate_terrain", {"width": 1000, ...})
```

**Error Types:**
- `ConnectionError` - Target unavailable (code: `TARGET_UNAVAILABLE`)
- `TimeoutError` - Command timed out (code: `TIMEOUT`)
- `CommandError` - Execution failed (code: `EXECUTION_ERROR`)

## AI Integration

### Provider Abstraction

```python
from mcp_core.ai import create_ai_client

client = create_ai_client()  # Uses OpenAI by default
response = await client.generate(
    prompt_name="scene_generation",
    variables={"description": "A medieval village"}
)
```

### Budget Enforcement

AI usage is tracked and limited per configuration:

```json
{
  "ai": {
    "budget": {
      "max_requests_per_run": 20,
      "max_total_tokens": 20000,
      "max_total_cost_usd": 5.0
    }
  }
}
```

### Safety Controls

- Input/output validation against injection patterns
- Tool allowlist/denylist
- No direct execution of model-generated code

## Authentication & Configuration
- Tool execution is configured via the files described in `configurations.md`.
- AI providers require credentials; credentials MUST be supplied via configuration or environment variables and MUST NOT be written to logs.

For CLI usage, refer to `commands.md`.
For setup instructions, refer to `docs/setup/quickstart.md`.
