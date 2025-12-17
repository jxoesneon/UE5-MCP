# MCP Automation

## Overview
This document defines MCP automation semantics: how tools execute, how work is batched, and how side effects are controlled.

It complements:

- `workflow.md` (end-to-end pipeline)
- `architecture.md` (components and execution model)
- `commands.md` / `api_reference.md` (tool surface and schemas)

## Automation Contracts

### Determinism
- Tools that involve randomness SHOULD accept a `seed`.
- The seed and tool version MUST be recorded in the run manifest.

### Idempotency
- Tools SHOULD be idempotent when feasible.
- If a tool is not idempotent, it MUST:
  - declare side effects
  - support `dry_run` where meaningful
  - emit sufficient provenance to understand what changed

### Safety Gates
- Destructive behavior (overwrite/delete/import that replaces assets) MUST be explicit.
- Policy MUST be enforced (tool allowlist and path allowlist).

### Artifact & Provenance Requirements
Every run MUST generate:

- a run manifest with `run_id`
- tool outputs in structured form
- artifact manifests for any exported/generated files

AI-assisted steps MUST also record:

- provider + model identifier
- prompt template hash
- budget usage summary

## Batching and Concurrency

### Batching
Tools MAY batch operations to reduce overhead:

- batch object placement
- batch material generation
- batch exports

Batching MUST preserve debuggability:

- per-item success/failure reporting
- stable ordering

### Concurrency
Concurrency is constrained by target runtimes:

- Blender and UE5 editor state are shared mutable resources.
- Mutating operations SHOULD be serialized per target.
- Read-only operations MAY be concurrent.

## Blender Automation

### Scene Generation (`mcp.generate_scene`)
Automation goals:

- produce a coherent object graph
- keep modifications attributable to a tool call
- support `dry_run` plans prior to applying

Recommended invariants:

- object naming conventions
- deterministic seed usage

### Texture/Material Automation (`mcp.generate_texture`)
Automation goals:

- deterministic mapping of textures/material slots
- explicit reporting of created materials and dependencies

### Export Automation (`mcp.export_asset`)
Automation goals:

- produce both the exported file and an export manifest
- preserve transform/material metadata
- support explicit overwrite controls

## UE5 Automation

### Terrain Automation (`mcp.generate_terrain`)
Automation goals:

- deterministic terrain creation via seed
- explicit parameters (size, detail)
- integration with PCG where applicable

### Population Automation (`mcp.populate_level`)
Automation goals:

- deterministic placement and stable ordering
- performance budgeting (max instances, density caps)

### Blueprint Automation (`mcp.generate_blueprint`)
Automation goals:

- blueprint edits that compile
- structured change summary (what assets, what graphs)

## Rollback & Recovery

### Checkpointing
High-impact operations SHOULD support checkpointing:

- Blender: save file snapshot prior to apply
- UE5: integrate with version control or changelist workflows

### Partial Failure
If a batch operation fails:

- MCP MUST return a structured error with partial results
- MCP SHOULD produce artifacts for successful sub-operations

## Performance Budgets
Tools SHOULD support explicit budgets:

- max instances
- max polycount
- timeouts

Tools MUST warn when budgets are exceeded and SHOULD refuse to apply changes if policy requires it.

For configuration options, refer to `configurations.md`.
