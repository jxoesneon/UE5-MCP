# MCP Commands

## Overview
This document specifies the **stable command surface** for MCP. These commands are treated as a contract: inputs are validated, outputs are structured, and side effects are auditable.

This file defines the CLI layer. For programmatic interfaces, see `api_reference.md`.

## Conventions

### Naming
- Command names are namespaced as `mcp.<tool_name>`.
- Tool names MUST be stable; behavior changes MUST be versioned and documented.

### Targets
Commands that execute inside Blender/UE5 MUST support explicit targeting (exact flags are implementation-defined):

- Blender target: an existing Blender session or a launchable Blender project context.
- UE target: a specific UE5 project and editor instance.

### Execution Modes
Commands that mutate state SHOULD support:

- `--dry-run` (no side effects; validate + produce plan/diff when possible)
- `--apply` (perform side effects)

### Output Format
By default, commands SHOULD emit a machine-readable JSON envelope.

Minimum output envelope:

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

### Error Model
Errors MUST be structured and include a stable `code`.

```json
{
  "protocol_version": "1.0",
  "tool": "mcp.export_asset",
  "request_id": "...",
  "run_id": "...",
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "...",
    "retriable": false,
    "details": {}
  }
}
```

## 1. General MCP Commands

### `mcp.list_commands`
- **Purpose**: Return the canonical list of tools, their versions, and short descriptions.
- **Side effects**: None.

Example:

```bash
mcp.list_commands
```

### `mcp.help "command_name"`
- **Purpose**: Provide detailed usage, schema, and examples for a specific tool.
- **Side effects**: None.

Example:

```bash
mcp.help "mcp.generate_blueprint"
```

### `mcp.config get key`
- **Purpose**: Read an effective configuration value.
- **Side effects**: None.

### `mcp.config set key value`
- **Purpose**: Update configuration (implementation-defined scope).
- **Side effects**: Writes config.
- **Safety**: MUST refuse to write secrets unless explicitly allowed.

### `mcp.reset_config`
- **Purpose**: Restore configuration to defaults.
- **Side effects**: Destructive write.
- **Safety**: MUST require explicit confirmation.

## 2. Blender-MCP Commands

### `mcp.generate_scene "description"`
- **Purpose**: Generate a scene scaffold from a natural language description.
- **Inputs**:
  - `description` (string)
- **Optional flags (recommended)**:
  - `--seed <int>`
  - `--style <string>`
  - `--dry-run | --apply`
- **Outputs**:
  - scene summary (created collections/objects)
  - provenance (seed, generator version)
- **Side effects**:
  - mutates Blender scene when executed with `--apply`

Example:

```bash
mcp.generate_scene "A futuristic city with neon lights and flying cars."
```

### `mcp.add_object "object_type" x y z`
- **Purpose**: Add an object to the active scene at a location.
- **Inputs**:
  - `object_type` (string)
  - `x`, `y`, `z` (float)
- **Outputs**:
  - object identifier/name
- **Side effects**:
  - mutates Blender scene when executed with `--apply`

Example:

```bash
mcp.add_object "tree" 5.0 2.5 0.0
```

### `mcp.generate_texture "object_name" "texture_type"`
- **Purpose**: Generate/apply a material or texture to an object.
- **Inputs**:
  - `object_name` (string)
  - `texture_type` (string)
- **Outputs**:
  - material/texture references and a mapping summary

Example:

```bash
mcp.generate_texture "rock_model" "mossy stone"
```

### `mcp.export_asset "object_name" "format" "filepath"`
- **Purpose**: Export an asset and produce an export manifest.
- **Inputs**:
  - `object_name` (string)
  - `format` (enum: `fbx`, `obj`, `gltf`)
  - `filepath` (string)
- **Optional flags (recommended)**:
  - `--include-textures`
  - `--overwrite` (MUST be explicit)
- **Outputs**:
  - exported file path
  - manifest path
- **Side effects**:
  - writes files to disk

Example:

```bash
mcp.export_asset "car_model" "fbx" "./exports/car_model.fbx"
```

## 3. Unreal Engine 5-MCP Commands

### `mcp.generate_terrain width height detail_level`
- **Purpose**: Generate procedural terrain in UE5.
- **Inputs**:
  - `width`, `height` (int)
  - `detail_level` (enum: `low`, `medium`, `high`)
- **Optional flags (recommended)**:
  - `--seed <int>`
  - `--dry-run | --apply`
- **Outputs**:
  - created terrain identifiers and parameters

Example:

```bash
mcp.generate_terrain 1000 1000 "high"
```

### `mcp.populate_level "asset_type" density`
- **Purpose**: Populate a level with assets.
- **Inputs**:
  - `asset_type` (string)
  - `density` (int)
- **Optional flags (recommended)**:
  - `--seed <int>`
  - `--budget-max-instances <int>`
- **Outputs**:
  - placement summary and performance warnings

Example:

```bash
mcp.populate_level "trees" 500
```

### `mcp.generate_blueprint "logic_description"`
- **Purpose**: Generate or modify Blueprint logic based on a behavioral spec.
- **Inputs**:
  - `logic_description` (string)
- **Outputs**:
  - created/modified Blueprint references
  - compile/validation status

Example:

```bash
mcp.generate_blueprint "A door that opens when the player interacts."
```

### `mcp.profile_performance "level_name"`
- **Purpose**: Produce a performance report artifact for a level.
- **Inputs**:
  - `level_name` (string)
- **Outputs**:
  - report artifact reference

Example:

```bash
mcp.profile_performance "desert_map"
```

### `mcp.debug_blueprint "blueprint_name"`
- **Purpose**: Diagnose common Blueprint issues (validation, missing connections).
- **Side effects**: None by default.

### `mcp.optimize_level`
- **Purpose**: Apply safe optimizations guided by explicit budgets.
- **Side effects**: Mutates project when executed with `--apply`.

For additional details on API functions, refer to `api_reference.md`.
