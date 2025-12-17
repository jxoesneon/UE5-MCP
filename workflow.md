# MCP Workflow

## Overview
This document specifies the **end-to-end, editor-time workflow** for MCP across Blender and Unreal Engine 5 (UE5). It is written as an implementable contract: what happens at each stage, which artifacts are produced, and what “correctness” means (determinism, safety, and debuggability).

This workflow assumes MCP is invoked via CLI or an agent, and executed against one or more explicit **targets** (a Blender session, a UE5 Editor instance/project).

## Key Invariants
- **Explicit targeting**: tool calls MUST target a specific Blender session and/or UE5 project context.
- **Artifact-first**: cross-runtime handoff MUST occur via artifacts (exports + manifests), not implicit state.
- **Deterministic-by-default**: generators SHOULD support seeding and stable outputs when given the same inputs.
- **Safe-by-default**: destructive operations MUST be opt-in and auditable.

## Execution Modes
All commands SHOULD support the following modes (as applicable):

- `--dry-run`: validate inputs, produce a plan and/or diff, but do not mutate targets.
- `--apply`: execute with side effects.
- `--json`: emit machine-readable outputs (recommended default for agent integration).

Long-running operations SHOULD support:

- progress events
- cancellation
- resumability when feasible (checkpoint artifacts)

## Core Artifacts
Artifacts are stored under an artifact root (implementation-defined). Every artifact MUST have a manifest.

### 1) Run Manifest
A per-run manifest that records:

- `run_id`, `request_id`
- tool versions
- configuration snapshot hash
- inputs (redacted for secrets)
- outputs (structured)
- timestamps and durations

### 2) Asset Export Manifest
Each exported asset MUST include metadata sufficient for reliable import:

- format (`fbx`, `gltf`, `obj`)
- coordinate system, scale, units
- material slots + texture references
- collision/LOD intent where available
- deterministic seed and generation provenance where applicable

### 3) Reports
Profiling produces a report artifact:

- scene/level identifier
- metrics and hotspots
- suggested remediations
- reproducibility data (engine version, map name, settings)

## End-to-End Pipeline

### Stage 0: Preflight (Always)
1. Load configuration (see `configurations.md`).
2. Resolve targets (Blender session / UE5 project).
3. Validate tool inputs against schemas.
4. Policy checks:
   - allowed tools
   - allowed file paths
   - destructive operation gates

Outputs:

- validated input envelope
- a plan (if invoked via natural language or high-level intent)

### Stage 1: Blender Authoring (Scene + Assets)
Primary tools:

- `mcp.generate_scene`
- `mcp.add_object`
- `mcp.generate_texture`

Contract:

- Scene changes MUST be attributable to a tool call.
- Texture/material generation MUST declare external dependencies (AI provider, model, prompts) in run logs.
- If randomness is used, the seed MUST be recorded.

Failure modes:

- missing add-ons or Blender permissions
- non-deterministic geometry due to non-seeded generators

### Stage 2: Export from Blender (Handoff Boundary)
Primary tool:

- `mcp.export_asset`

Contract:

- Export MUST produce an Asset Export Manifest alongside the file.
- Export MUST preserve transforms/material slots and include texture references or embed textures when requested.
- Export SHOULD be repeatable given identical inputs (within the limits of the chosen format).

Failure modes:

- missing textures
- incompatible format settings for UE import

### Stage 3: Import into UE5 (Ingestion)
This stage is conceptually required even if the initial command surface does not yet expose `mcp.import_asset`.

Contract:

- UE import MUST read the Asset Export Manifest.
- Materials SHOULD be mapped deterministically (by slot name + texture hashes).
- UE-side outputs (created assets) MUST be reported as artifact references.

Failure modes:

- wrong scale/axes
- missing dependencies (textures, plugin requirements)

### Stage 4: Procedural Level Design in UE5
Primary tools:

- `mcp.generate_terrain`
- `mcp.populate_level`

Contract:

- Terrain generation MUST declare resolution/detail settings and seed.
- Population MUST support deterministic placement (seed + stable ordering).
- Placement SHOULD be constrained by performance budgets (instance count, LOD policy).

Failure modes:

- overpopulation causing performance regressions
- invalid asset references

### Stage 5: Blueprint Automation
Primary tool:

- `mcp.generate_blueprint`

Contract:

- Generated Blueprint edits MUST be validated for compile errors.
- The tool MUST produce:
  - a list of created/modified Blueprints
  - a summary of nodes/graphs changed

Failure modes:

- missing node connections
- incompatible engine version APIs

### Stage 6: Profiling & Optimization
Primary tool:

- `mcp.profile_performance`

Contract:

- Profiling MUST produce a report artifact.
- Suggested optimizations MUST be categorized by risk and expected impact.

## Rollback & Recovery
Rollback strategies vary by target:

- Blender: use file saves/checkpoints; MCP SHOULD support “checkpoint before apply”.
- UE5: use source control integration; MCP SHOULD support “create changelist/commit message” style outputs.

If an operation fails mid-run:

- MCP MUST return a structured error with `run_id` and partial artifacts.
- MCP SHOULD support replaying from the last completed stage where safe.

## Best Practices
- Use `--dry-run` for new automation flows and CI validation.
- Treat AI suggestions as untrusted; enforce schema validation and policy gates.
- Keep a consistent asset naming convention and deterministic seeding for reproducible builds.

For configuration details, see `configurations.md`.
