# AI Integration in MCP

## Overview

MCP supports **optional AI assistance** for planning and content generation. This document defines the 2025 contract for how AI is integrated, governed, and evaluated.

AI is a productivity feature, not a trusted execution authority. In MCP:

- AI may propose plans and content.
- MCP validates, policy-checks, and executes through deterministic adapters.

For the command/tool surface, see `commands.md` and `api_reference.md`.

## Design Principles

- **Human intent, machine check**: AI outputs are suggestions until validated.
- **Bounded compute**: enforce cost/latency budgets.
- **Data minimization**: never send secrets or unnecessary project data to providers.
- **Reproducibility**: persist provenance (provider, model, prompt hash, seed where applicable).

## AI Roles in MCP

### 1) Planner

Converts underspecified intent into a tool plan.

- Input: natural language + minimal context
- Output: structured tool calls validated by schemas

### 2) Generator

Produces assets or specifications (textures/material text prompts, blueprint descriptions).

- Output MUST be bounded and structured.

### 3) Critic (Optional)

Evaluates outputs for policy/quality issues and suggests remediations.

## Provider Abstraction

MCP MUST isolate provider-specific behavior behind an adapter.

Minimum capabilities:

- **Text (LLM)**: planning, summarization, structured outputs
- **Image/texture** (optional): texture/material generation

Provider categories:

- **Cloud providers** (API-based)
- **Local providers** (self-hosted OpenAI-compatible endpoints)

The provider adapter MUST support:

- timeouts
- retries for transient failures
- streaming (optional)
- request/response logging with redaction

## Configuration

AI settings are configured via `configurations.md`.

Recommended config keys:

- `ai.enabled`
- `ai.provider`
- `ai.budget.*`

Secrets MUST be provided via environment variables (recommended):

- `MCP_AI_API_KEY`

## Budgeting (Cost / Latency / Safety)

Every run MUST be constrained by budgets.

Recommended budgets:

- `max_requests_per_run`
- `max_total_tokens`
- `max_total_cost_usd`
- `timeout_seconds`

When a budget is exceeded:

- MCP MUST return a structured error (recommended `POLICY_DENIED` or `TIMEOUT` depending on cause)
- MCP SHOULD include partial artifacts and the `run_id`

## Prompt Hygiene & Template Versioning

MCP MUST treat prompts as versioned templates.

Guidelines:

- Separate **instructions** (system prompt) from **untrusted context** (project data).
- Avoid sending raw file trees, secrets, or large binary-derived text.
- Prefer schema-driven outputs (structured JSON), validated before execution.
- Record a **prompt template hash** and provider model identifier in the run manifest.

## Safety Controls

### Prompt Injection Resistance

MCP MUST assume that any external text (assets metadata, imported docs, web content) may contain adversarial instructions.

Mitigations:

- never execute model-generated code directly
- validate all tool calls against schemas
- enforce tool allowlists and path allowlists

### Destructive Actions

AI-driven plans MUST NOT enable destructive operations implicitly.

- destructive tools require explicit opt-in via policy config
- prefer `--dry-run` and user review for high-impact changes

### Privacy & IP

- minimize what is sent to providers
- consider an allowlist of what project data is permitted to leave the machine

## Evaluation (Evals) and Quality Gates

AI behavior MUST be continuously evaluated.

Recommended eval types:

- **Schema conformance**: tool calls always validate.
- **Determinism**: seeded operations are stable.
- **Blueprint correctness**: generated Blueprints compile and pass basic checks.
- **Safety**: no forbidden tools/paths used.

Recommended harness:

- golden test prompts
- snapshot tests on the produced tool plans
- regression suite executed in CI using `--dry-run`

## Example Workflows

### Scene Generation

```bash
mcp.generate_scene "A cyberpunk city with neon lights" --dry-run
```

### Blueprint Automation

```bash
mcp.generate_blueprint "A door opens when the player interacts" --dry-run
```

For additional configuration, see `configurations.md`.
