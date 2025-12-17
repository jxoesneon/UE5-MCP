# Blender-MCP

## Overview

Blender-MCP defines how MCP automates Blender for:

- scene generation and editing
- material/texture workflows
- export packaging for downstream ingestion (UE5)

This document is an integration specification: execution boundaries, transport, safety constraints, and artifact contracts.

## Scope

Blender-MCP targets **editor-time automation** inside Blender, not runtime use.

Primary tools:

- `mcp.generate_scene`
- `mcp.add_object`
- `mcp.generate_texture`
- `mcp.export_asset`

## Integration Architecture

### Add-on shape

Blender-MCP is implemented as a Blender add-on that:

- registers a small MCP endpoint (transport-specific)
- exposes tool handlers that call Blender’s Python API
- reports structured results and artifacts

The add-on SHOULD run with least privilege and restrict file system operations to allowlisted paths.

### Transport

The transport mechanism is implementation-defined. Recommended options:

- **Local stdio**: safest for agent-run “Blender as a subprocess”.
- **Local HTTP/WebSocket**: suitable when Blender stays open and MCP connects to a running session.

Security constraints:

- default bind: `localhost` only
- explicit opt-in for remote access

## Execution Semantics

### Target selection

Every tool call MUST target a specific Blender session/context.

### Determinism

- Tools SHOULD accept `seed` for any non-deterministic generation.
- Tool versions and seed MUST be recorded in the run manifest.

### Dry-run

Where feasible, tools SHOULD support `dry_run`:

- validate parameters
- report intended changes
- avoid mutating Blender state

## Safety & Permissions

### File system

Tools that write to disk (e.g., `mcp.export_asset`) MUST:

- respect an allowlist of output directories
- refuse overwrite unless explicitly enabled
- emit an artifact manifest

### Script execution

Model-generated code MUST NOT be executed directly.

If any dynamic scripting is supported, it MUST be behind strict policy gates and sandboxing.

## Asset Pipeline Contract

### Export formats

Blender-MCP SHOULD support exporting to:

- `fbx`
- `gltf`
- `obj`

### Export manifest

Every export MUST produce a companion manifest (see `workflow.md`). Minimum recommended fields:

- export path
- format
- unit scale and axis conventions
- object name/id
- material slots and texture references
- seed/provenance where applicable

### Material/texture portability

Exports SHOULD avoid fragile absolute paths.

- prefer embedding textures when requested
- otherwise emit stable relative references and include a copy strategy

## Limitations (Expected)

- Blender Python API operations can be slow for very large scenes.
- Determinism depends on using stable seeds and avoiding time-based randomness.
- Export fidelity varies by format; manifests are required to keep imports consistent.

## Testing Strategy

- schema validation tests for tool inputs
- golden tests for manifests
- deterministic tests for seeded generation (within tolerance)

For more details on automation semantics, refer to `automation.md`.
