# Unreal Engine 5-MCP

## Overview
UE5-MCP defines how MCP automates Unreal Engine 5 for:

- terrain and PCG-driven level generation
- asset ingestion and placement
- Blueprint creation/modification
- profiling and optimization reporting

This document is an integration specification: where MCP connects, what the contracts are, and how safety/determinism are enforced.

## Scope and Boundary
UE5-MCP targets **editor-time automation**. The initial assumption is that MCP operates against a running UE5 Editor instance.

Non-goals:

- packaged game runtime control (initially)
- giving an AI agent unrestricted access to modify arbitrary project files

Primary tools:

- `mcp.import_asset`
- `mcp.generate_terrain`
- `mcp.populate_level`
- `mcp.generate_blueprint`
- `mcp.profile_performance`

## Integration Architecture

### Execution backends
UE5-MCP can execute through one or more backends:

- **UE Python Editor Scripting** (preferred): direct editor automation
- **Remote Control API (HTTP/WebSocket)** (optional): remote property/function invocation
- **UnrealCV** (optional): legacy/third-party transport for certain workflows

Backends MUST normalize results into the MCP result envelope (see `api_reference.md`).

### Transport
MCP connects to UE5 via an implementation-defined transport.

Recommended constraints:

- local-only by default
- explicit opt-in for remote access
- authenticated endpoints for non-local usage

## Required UE5 Plugins
- `Python Editor Script Plugin`
- `Procedural Content Generation (PCG) Framework`

Optional plugins:

- `Remote Control` (if using Remote Control API)
- `UnrealCV` (if using UnrealCV)

## Execution Semantics

### Target selection
Tool calls MUST target a specific UE5 project/editor context.

Recommended targeting fields (conceptual):

- project path
- map/level name
- optional world partition or sub-level selection

### Determinism
- Terrain/population tools SHOULD accept a `seed`.
- Placement MUST be stable given identical inputs (seed + tool version + asset set).

### Dry-run
Tools SHOULD support `dry_run`:

- validate parameters
- compute an execution plan (e.g., instance counts, asset sets)
- avoid mutating the project

## Tool Contracts

### Terrain Generation (`mcp.generate_terrain`)
Contract:

- declares size/detail settings
- integrates with PCG where applicable
- records seed and parameters

Expected outputs:

- created terrain asset references
- parameters used

### Population (`mcp.populate_level`)
Contract:

- deterministic placement ordering
- budgeting support (max instances)
- emits warnings when budgets are exceeded

Expected outputs:

- placements created
- summary statistics (counts, bounds)

### Blueprint Automation (`mcp.generate_blueprint`)
Contract:

- outputs MUST compile (or return explicit compile errors)
- changes MUST be summarized (assets/graphs affected)
- high-impact changes SHOULD be gated behind review workflows

### Profiling (`mcp.profile_performance`)
Contract:

- produces a report artifact
- categorizes recommendations by risk/impact

## Asset Ingestion from Blender
UE5-MCP SHOULD support ingestion of Blender exports by consuming export manifests.

`mcp.import_asset` is the recommended ingestion entry point. Early implementations MAY support it in `dry_run`-only mode first, but the import process MUST be standardized:

- read export manifest
- enforce scale/axis conventions
- map materials deterministically

## Safety & Project Hygiene
- Prefer operating in a dedicated sandbox map until changes are validated.
- Integrate with source control workflows for rollback.
- Never overwrite assets unless explicitly configured and confirmed.

## Limitations (Expected)
- Blueprint graph editing APIs vary by engine version.
- Some automation requires editor focus and can be disrupted by modal dialogs.
- Profiling results depend on project settings and hardware; reports must include metadata.

For more details, refer to `automation.md` and `workflow.md`.
