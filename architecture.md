# MCP Architecture

## Overview
MCP (Model Context Protocol) is an **editor-time automation system** that turns user intent into deterministic, inspectable operations across Blender and Unreal Engine 5 (UE5). It provides:

- A **stable tool surface** (commands + APIs) for scene generation, asset transfer, and in-editor automation.
- A **protocol** for representing tool invocations, plans, and execution results.
- A set of **adapters** that implement those tool invocations against Blender, UE5, and optional AI providers.

This document defines the architecture as an implementable contract: component boundaries, data flow, security posture, and operational behavior.

## Goals
- **Determinism by default**: executions are reproducible, inspectable, and diffable.
- **Safety-first automation**: destructive actions require explicit opt-in.
- **Provider-agnostic AI**: AI usage is optional, bounded, and replaceable.
- **Editor-time focus**: the primary target is authoring workflows, not runtime gameplay.
- **Extensibility**: new tools/backends can be added without reworking core infrastructure.

## Non-Goals
- Shipping a one-shot “prompt builds an entire game” solution.
- Shipping a runtime dependency for packaged UE games (initially).
- Hard-coding a specific AI provider or model.

## Architectural Boundary
MCP is a control-plane system. It orchestrates tools that execute inside external runtimes:

- **Blender runtime** (Python API, add-on context)
- **UE5 Editor runtime** (Python Editor Script Plugin, PCG, optional UnrealCV)
- **AI providers** (LLM + image/texture generation) used as planning/assistive components

MCP does not replace Blender/UE5; it produces operations that those environments execute.

## Core Concepts
- **Tool**: a named capability with a validated input schema and a structured output.
- **Command**: user-facing alias for a tool (CLI/agent-facing entry point).
- **Plan**: an ordered set of tool calls produced from intent (may be human-reviewed).
- **Run**: a single execution instance with an immutable `run_id`, logs, and artifacts.
- **Artifact**: generated output (files, reports, exported assets) with metadata and provenance.
- **Target**: the execution environment (Blender session, UE5 project/editor instance).

## High-Level Components

### 1) MCP Gateway (Transport Layer)
Responsibilities:

- Accept requests from a CLI, IDE agent, or remote client.
- Perform request framing, streaming, and cancellation.
- Attach trace context (`trace_id`, `run_id`) and enforce timeouts.

Transport options (implementation-dependent):

- **stdio** for local agent/server integration.
- **HTTP/WebSocket** for remote clients and streaming events.
- **TCP** only as a legacy/compat option; prefer authenticated, structured transports.

### 2) Command Registry (Tool Surface)
Responsibilities:

- Provide canonical tool definitions (name, description, JSON schema, examples).
- Provide `mcp.list_commands` and `mcp.help` views.
- Enforce stable naming, versioning, and deprecation policies.

### 3) Policy & Security Layer
Responsibilities:

- Authentication for remote transports (tokens/keys) where applicable.
- Authorization policies (allowlist tools, file paths, project roots).
- Safety gates for destructive operations (delete/overwrite/import side-effects).
- Secret handling (config/env only; never logs).

### 4) Planner (Optional AI + Heuristics)
Responsibilities:

- Convert ambiguous intent into a structured plan (tool calls).
- Ask clarifying questions when inputs are underspecified.
- Produce bounded outputs (token/cost/time budgets).

Planner outputs are treated as **untrusted suggestions** until validated and policy-checked.

### 5) Executor (Deterministic Runtime)
Responsibilities:

- Validate inputs against schemas.
- Execute tool calls against adapters.
- Manage retries for transient failures (network/IO) with backoff.
- Emit events, logs, and artifacts.

Execution model:

- **Preflight**: validate + compute a diff/plan where supported.
- **Apply**: execute with locking on per-target resources.
- **Post-validate**: sanity checks and artifact registration.

### 6) Adapters (Blender / UE5 / AI)
Responsibilities:

- Provide the concrete implementation of tools.
- Translate tool inputs into runtime-specific API calls.
- Normalize outputs/errors into MCP’s structured result model.

Adapter categories:

- **Blender adapter**: scene operations, object placement, export.
- **UE5 adapter**: terrain/PCG ops, import, Blueprint edits, profiling.
- **AI adapter**: text planning, texture generation, summarization, critique.

### 7) Storage & Artifacts
Responsibilities:

- Store execution logs and structured results.
- Store exported/generated artifacts and their provenance.
- Support cache keys for deterministic re-runs (where safe).

At minimum: local filesystem artifact root with manifest files. Advanced: object storage + DB.

### 8) Observability
Responsibilities:

- **Structured logs** per tool call and per run.
- **Metrics** (latency, error rates, tool usage, budget usage).
- **Tracing** across planner → executor → adapters.

Implementation guidance: OpenTelemetry-compatible tracing and JSON logs.

## Protocol & Versioning
MCP requests/responses MUST be versioned.

- **Protocol version**: semantic versioning (`MAJOR.MINOR.PATCH`).
- **Tool schema versioning**: tool definitions are versioned and can be deprecated.

Minimum envelope fields (conceptual):

- `protocol_version`
- `request_id` (idempotency key)
- `run_id` (execution instance)
- `tool_name`
- `params` (validated against tool schema)
- `trace_id` / `span_id`

### Idempotency & Reproducibility
- Tools SHOULD be idempotent when feasible.
- Non-idempotent tools MUST declare side effects and support `dry_run` where possible.
- All runs MUST record: tool inputs, tool versions, config snapshot hash, and artifact hashes.

### Streaming & Cancellation
Long-running tools (terrain generation, imports, AI calls) SHOULD emit progress events and accept cancellation signals.

## Security Model
Security is enforced at **multiple layers**:

- **Secrets**: provided via config/env; redacted from logs.
- **Authorization**: tool allowlist, path allowlist, and project-root constraints.
- **Sandboxing**: adapters must avoid executing arbitrary code paths from model output.
- **Prompt injection resistance**: treat external content as data; separate instructions from context.
- **Auditability**: immutable audit logs per run with timestamps and actor identity (where applicable).

## Concurrency & Target Isolation
MCP must assume Blender and UE5 sessions have shared mutable state.

- Use per-target locks (e.g., one executor per Blender session / UE project).
- Queue tool calls that mutate the same scene/project.
- Prefer explicit “open project / select level” targeting instead of implicit globals.

## Reference Execution Flows

### Blender Asset Pipeline
1. `generate_scene` produces a plan or direct scene operations.
2. `add_object` mutates scene state.
3. `generate_texture` produces textures/material bindings.
4. `export_asset` emits an artifact with a manifest (format, scale, axes, materials).

### UE5 Level Pipeline
1. `import_asset` ingests exported artifacts.
2. `generate_terrain` produces terrain/heightmap/PCG graphs.
3. `populate_level` instantiates assets with deterministic seeding.
4. `generate_blueprint` produces Blueprint edits with validation.
5. `profile_performance` produces a report artifact.

## Extensibility
To add a tool:

- Define a schema + examples.
- Implement an adapter method.
- Add policy defaults (is it destructive? does it touch the filesystem?).
- Add tests (schema validation + golden outputs for deterministic mode).

## Operational Profiles
- **Local single-user**: stdio transport, local artifacts, minimal auth.
- **Team shared**: HTTP/WebSocket gateway, central artifact store, role-based policies.
- **CI validation**: run tool plans in `dry_run` and validate schemas, manifests, and deterministic outputs.
