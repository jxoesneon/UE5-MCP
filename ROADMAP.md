# UE5-MCP Implementation Roadmap (End-to-End)

## Purpose

This roadmap is an **end-to-end implementation plan** for building the UE5-MCP system described by this repository’s specifications.

It is written for a spec-first repo:

- The docs in this repository define the **contract** (tools, schemas, error model, execution semantics).
- The roadmap defines **how to implement** those contracts in an incremental, verifiable way.

## How to Use This Roadmap

- Implement in **phases**; each phase ends with a measurable “Definition of Done”.
- Prefer **additive** changes to the contract surface.
- Every phase must include:
  - contract/schema validation
  - structured errors
  - artifacts and provenance
  - a minimal test plan (unit/contract/integration)

## Global Success Criteria

An implementation can be considered “end-to-end viable” when all of the following are true:

- A user can run the documented tools via CLI with `--dry-run` and receive a valid JSON envelope.
- A user can run at least one safe `--apply` flow against a target with policy gates enabled.
- Every run emits a `run_id` and produces a run manifest and relevant artifact manifests.
- Failures always return structured errors (`error.code`) consistent with `api_reference.md`.

## Version / Release Milestones

This repo follows SemVer with a pragmatic approach for a spec-first project:

- `0.y.z` releases are pre-stable and may include breaking changes as the implementation is established.
- `1.0.0` is the first “stable implementation” milestone.

Expected milestones:

- `v0.0.0`: Spec + workflow baseline (docs contract, CI quality gates, contribution workflow).
- `v0.1.0`: Phase 0 complete (repo + tooling baseline; package skeleton exists).
- `v0.2.0`: Phase 1 complete (contracts as code: schemas + models + contract tests).
- `v0.3.0`: Phase 2 complete (core runtime MVP: envelopes, policy, config).
- `v0.4.0`: Phase 3 complete (artifacts, manifests, observability).
- `v0.5.0`: Phase 4 complete (Blender adapter skeleton).
- `v0.6.0`: Phase 5 complete (UE5 adapter skeleton).
- `v0.7.0`: Phase 6 complete (end-to-end pipeline).
- `v0.8.0`: Phase 7 complete (AI provider layer).
- `v0.9.0`: Phase 8 complete (evals + regression harness).
- `v1.0.0`: Phase 9 complete (packaging, releases, hardening).

## Phase 0 — Repository + Tooling Baseline (Week 0–1)

**Goal**: make the repo implementation-ready without committing to a full runtime.

Deliverables:

- `pyproject.toml` workspace scaffold (tooling only)
- lockfile strategy (`uv.lock` preferred)
- CI quality gates beyond Markdown lint (type check, unit tests placeholder, contract tests placeholder)
- documentation consistency checks in CI (optional)

Definition of Done:

- CI runs on PRs and merges.
- A minimal Python package skeleton exists (even if tools are stubs).

Maps to:

- `dependencies.md`
- `monorepo_structure.md`
- `CONTRIBUTING.md`

## Phase 1 — Protocol + Contracts as Code (Week 1–2)

**Goal**: turn the written contract into machine-checkable schemas and types.

Deliverables:

- JSON Schemas for:
  - tool inputs
  - result envelope
  - error envelope
  - artifact descriptors
- Versioned schema directory and compatibility policy
- Generated/handwritten Python models that mirror the schemas

Definition of Done:

- Contract tests validate:
  - every schema is valid JSON Schema
  - example payloads in docs validate against schemas

Maps to:

- `api_reference.md`
- `commands.md`
- `architecture.md`

## Phase 2 — Core Runtime MVP (Week 2–4)

**Goal**: implement the control-plane primitives independent of Blender/UE.

Deliverables:

- Command registry:
  - `mcp.list_commands`
  - `mcp.help`
- Execution envelope:
  - always emits `protocol_version`, `request_id`, `run_id`, `status`
  - structured `error` with stable codes
- Config system:
  - read target configs (`~/.mcp/blender_mcp_config.json`, `~/.mcp/ue5_mcp_config.json`)
  - env overrides
  - `mcp.config get/set/reset_config` (with secret redaction)
- Policy system:
  - tool allowlist
  - path allowlist
  - destructive gate

Definition of Done:

- `--dry-run` works for at least one tool and returns a valid envelope.
- Policy gates deny destructive operations by default.

Maps to:

- `configurations.md`
- `commands.md`
- `automation.md`

## Phase 3 — Artifacts, Manifests, and Observability (Week 3–5)

**Goal**: make every run auditable and debuggable.

Deliverables:

- Artifact root management (`~/.mcp/artifacts` by default)
- Run manifest writing (`~/.mcp/artifacts/<run_id>/run_manifest.json`)
- Structured JSON logging
- Trace identifiers (`trace_id`/`span_id`) as optional fields

Definition of Done:

- For any tool invocation (even stubbed), a run manifest is written.
- Errors include sufficient context for troubleshooting without exposing secrets.

Maps to:

- `workflow.md`
- `troubleshooting.md`
- `architecture.md`

## Phase 4 — Blender Adapter Skeleton (Week 4–6)

**Goal**: implement the Blender target boundary with deterministic execution semantics.

Deliverables:

- Transport boundary (local-first):
  - stdio or local IPC
- Tool stubs that validate schemas and produce artifacts:
  - `mcp.generate_scene`
  - `mcp.add_object`
  - `mcp.generate_texture` (AI optional)
  - `mcp.export_asset`
- Export manifest format and validation

Definition of Done:

- A Blender integration test can run `--dry-run` for `mcp.export_asset` and produce a manifest.
- A minimal `--apply` flow can export a known object (with `--overwrite` gated).

Maps to:

- `blender_mcp.md`
- `workflow.md` (Stages 1–2)

## Phase 5 — UE5 Adapter Skeleton (Week 5–8)

**Goal**: implement UE5 target connectivity and safe read/write primitives.

Deliverables:

- Transport selection:
  - Remote Control API (HTTP/WebSocket) and/or
  - UE Python Editor Scripting bridge and/or
  - UE plugin TCP server (local-only default)
- Tools:
  - `mcp.import_asset` (ingestion from export manifest)
  - `mcp.generate_terrain`
  - `mcp.populate_level`
  - `mcp.generate_blueprint` (initially constrained; safe-by-default)
  - `mcp.profile_performance`

Definition of Done:

- UE5 target can be reached and queried (basic handshake).
- `mcp.generate_terrain --dry-run` returns a plan/diff-like response.
- `mcp.generate_terrain --apply` mutates a dedicated sandbox level when policy allows.

Maps to:

- `ue5_mcp.md`
- `workflow.md` (Stages 3–6)

## Phase 6 — End-to-End Pipeline (Week 8–10)

**Goal**: connect Blender export → UE import → level automation with artifacts as the boundary.

Deliverables:

- End-to-end “happy path” scenario:
  - generate scene (optional)
  - export asset + manifest
  - import asset from manifest
  - generate terrain
  - populate level
  - generate blueprint
  - profile performance
- Unified run manifests across multi-stage flows

Definition of Done:

- One scripted e2e run completes in a sandbox project and produces:
  - run manifest
  - export manifest
  - import outputs
  - profiling report artifact

Maps to:

- `workflow.md` (entire doc)
- `automation.md`

## Phase 7 — AI Provider Layer (Week 9–12)

**Goal**: add AI as an optional, bounded planning/generation component.

Deliverables:

- Provider abstraction
- Prompt template versioning + hashing
- Budget enforcement (`ai.budget.*`)
- Safety controls (no direct execution of model-generated code)

Definition of Done:

- AI can propose tool calls that validate against schemas.
- Budget failures return structured errors and partial artifacts.

Maps to:

- `ai_integration.md`
- `configurations.md`

## Phase 8 — Evals + Regression Harness (Week 10–13)

**Goal**: make quality measurable and prevent regressions.

Deliverables:

- Golden tests for:
  - envelopes
  - error codes
  - manifests
- Determinism tests for seeded tools
- Safety tests ensuring forbidden tools/paths are blocked

Definition of Done:

- CI runs contract + unit tests on every PR.
- Regressions in schema conformance fail CI.

Maps to:

- `ai_integration.md` (Evals)
- `automation.md`

## Phase 9 — Hardening, Packaging, and Releases (Week 12+)

**Goal**: make the system installable and operable by others.

Deliverables:

- Packaging (console entrypoint `mcp`)
- Versioned releases
- Upgrade/migration notes for protocol bumps
- Operational docs for local/team modes

Definition of Done:

- A tagged release can be installed in a clean environment.
- Documentation matches reality (no “spec drift”).

## Risk Register (High-Level)

- **UE5 API instability**: mitigate via version gating + compatibility matrix.
- **Blueprint editing brittleness**: start with constrained templates + dry-run diffs.
- **Security exposure**: local-only defaults; strong auth/policy before remote exposure.
- **Non-determinism**: enforce seeds, record tool versions, store artifact hashes.
- **Cost overruns**: enforce budgets and require explicit opt-in for AI.

## Traceability Matrix (Docs → Implementation Artifacts)

- `commands.md` → CLI commands, flags, JSON envelope output
- `api_reference.md` → schemas, models, stable tool signatures
- `configurations.md` → config loader + precedence + redaction
- `workflow.md` → integration tests + e2e pipeline
- `automation.md` → executor semantics, idempotency, batching
- `troubleshooting.md` → error codes + artifact locations + diagnostics
