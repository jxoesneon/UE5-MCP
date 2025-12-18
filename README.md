# UE5-MCP (Model Context Protocol)

## Project Status

This repository currently provides a **specification-first documentation set** for UE5 + Blender automation via MCP.

Implementation is being built to match these docs. Until the code lands, treat:

- **Docs as the contract** (what tools/commands/configs will do).
- **Anything not explicitly specified** as undefined behavior.

## Overview

UE5-MCP (Model Context Protocol) is a tool-and-protocol layer that enables **AI-assisted automation** across:

- **Blender**: scene generation, asset creation, texturing/material workflows, export.
- **Unreal Engine 5**: level assembly, terrain/PCG automation, Blueprint generation, profiling/optimization.

The goal is to let you express intent in natural language (or structured tool calls) and have MCP produce deterministic, inspectable actions in Blender/UE5.

## What This Is / Isn’t

### This is

- A **workflow automation system** that exposes well-defined tools (commands/APIs) for Blender and UE5.
- A **provider-agnostic AI orchestration layer** (OpenAI/Claude/SD, etc.) with safety controls.
- A **bridge** between DCC output (Blender) and engine ingestion (UE5), preserving materials, transforms, and metadata.

### This isn’t

- A replacement for Blender or UE5 authoring.
- A guarantee of “one prompt builds an entire shippable game.”
- A runtime plugin intended for packaged games; the initial target is **editor-time automation**.

## Key Capabilities (Contract)

- **Scene Generation (Blender)**: `mcp.generate_scene` + object placement + procedural textures.
- **Asset Export/Transfer**: export to `.fbx`, `.obj`, `.gltf` with metadata conventions.
- **Level Design Automation (UE5)**: terrain generation and asset population.
- **Blueprint Automation (UE5)**: generate/edit Blueprints from behavioral specifications.
- **Profiling & Optimization (UE5)**: produce reports and suggested remediations.

See:

- `workflow.md` for the end-to-end pipeline
- `commands.md` for the command surface
- `api_reference.md` for programmatic APIs

## Quickstart (Spec-Driven)

Until the implementation is available, you can still use the docs to plan integrations and project structure.

1. **Install prerequisites**
   - Blender 3.x+
   - UE 5.1+
   - Python 3.11+

2. **Enable UE plugins**
   - `Python Editor Script Plugin`
   - `Procedural Content Generation (PCG) Framework`
   - `UnrealCV Plugin` (if using UnrealCV-based transport)

3. **Create configs**
   - Blender: `~/.mcp/blender_mcp_config.json`
   - UE5: `~/.mcp/ue5_mcp_config.json`

4. **Run commands (examples)**
   - `mcp.generate_scene "A medieval village with a river"`
   - `mcp.export_asset "bridge_model" "fbx" "./exports/bridge.fbx"`
   - `mcp.generate_terrain 2000 2000 "high"`
   - `mcp.generate_blueprint "A door opens when the player interacts."`

## Security, Safety, and Governance (2025 Baseline)

- **Secrets**: API keys must be supplied via config or environment variables; never commit them.
- **Least privilege**: default behavior should avoid destructive operations (delete/overwrite) unless explicitly enabled.
- **Auditability**: every tool execution should emit structured logs (inputs, outputs, side effects, timings).
- **Reproducibility**: generated assets/scripts should be traceable to prompts + tool parameters + versioned templates.

See `configurations.md` and `ai_integration.md`.

## Documentation Map

- `architecture.md`: component boundaries, data flows, and security posture
- `workflow.md`: end-to-end asset → engine pipeline
- `commands.md`: CLI/tool surface and semantics
- `api_reference.md`: programmatic APIs and contracts
- `configurations.md`: config schema, precedence, secrets
- `dependencies.md`: reproducible dependencies and toolchain requirements
- `troubleshooting.md`: diagnostic playbooks
- `ROADMAP.md`: end-to-end implementation roadmap (phases, acceptance criteria, risks)

## Roadmap (Implementation)

See `ROADMAP.md` for a phased, end-to-end implementation plan with acceptance criteria, risks, and spec mappings.

## Contributing

See `CONTRIBUTING.md`.

## License

See `LICENSE.md`.
