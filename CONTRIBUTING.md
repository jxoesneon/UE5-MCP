# Contributing to MCP

This repository is a **specification-first** project for an MCP-driven automation system spanning Unreal Engine 5 and Blender.

Contributions are welcome, but we use a strict “contract-first” workflow:

- Changes to docs and schemas define the contract.
- Implementations (when present) must conform to the contract.
- Automation is expected to be deterministic, idempotent, and safe-by-default.

## Project Status and Scope

- **Current status**: documentation/specs are authoritative; implementation may be partial or absent.
- **Primary scope**: editor-time automation for UE5 and Blender via MCP-style tools/commands.
- **Non-goals**: shipping runtime gameplay code inside UE projects; unsandboxed destructive operations.

## Ways to Contribute

- **Documentation/spec improvements**: clarity, rigor, schema definitions, examples, threat model, test vectors.
- **Protocol work**: JSON schema/versioning, error model, idempotency semantics, tool descriptors.
- **Reference implementation**: minimal CLI + registry + adapters with contract tests.
- **Target adapters**: UE5 Remote Control / Python Editor Scripting, Blender add-on boundaries.
- **Tooling**: CI, lint/type gates, release automation, reproducible dependency management.

## Communication and Coordination

- **Issues**: use GitHub Issues for bugs, requests, and proposals.
- **Design discussions**: use Issues (or Discussions, if enabled) for RFC-level topics.
- **Security**: see “Security Reporting” below.

## Reporting Issues

When filing an issue, include:

- **What you expected to happen**
- **What happened instead**
- **Reproduction steps** (minimal)
- **Environment**
  - OS
  - Python version
  - UE / Blender versions (if applicable)
  - Transport mode (stdio / HTTP / TCP)
- **Artifacts** (if available)
  - run manifest
  - logs
  - exported scene/asset manifests

## Proposing Changes (RFC-lite)

If a change impacts external contracts (command names, tool schemas, request/response envelopes, error codes, config keys):

- **Open an issue first** describing motivation, alternatives considered, and compatibility impact.
- Prefer **additive** changes.
- If a breaking change is unavoidable, propose a **versioned protocol bump** and a migration plan.

## Development Environment (Recommended)

This repo is Python-first.

- **Python**: 3.11+.
- **Virtual environment**: use `venv` or a modern toolchain (e.g., uv).
- **Node**: optional (only if/when frontend or tooling requires it).

If you are contributing UE5/Blender adapter work:

- **UE5**: 5.x with Editor Scripting utilities and/or Remote Control API plugin enabled.
- **Blender**: 3.x+ and ability to install a development add-on.

## Quality Gates (What CI Should Enforce)

Pull requests are expected to meet these standards:

- **Formatting**: consistent formatting across Python and Markdown.
- **Linting**: no new lint violations.
- **Type checking**: no new type errors (when type checks exist).
- **Tests**:
  - Contract tests for schema compliance.
  - Unit tests for deterministic logic.
  - Integration tests for adapters (prefer fakes unless running real targets).
- **Docs**: examples and references are accurate; links are not obviously broken.

## Pre-PR Checklist (Local)

Before opening a PR, run the repository verification script:

```bash
bash scripts/verify.sh
```

Recommended (optional) local hooks:

```bash
python3 -m pip install pre-commit
pre-commit install
```

## Pull Request Process

- **Branching**: create a topic branch off the default branch.
- **Commits**: keep commits focused; avoid drive-by unrelated formatting.
- **PR description**: include:
  - Summary of changes
  - Motivation/context
  - User-visible impact
  - Compatibility notes (breaking/additive)
  - Test plan (what you ran, what you didn’t)

Reviewers will focus on:

- Contract stability (commands, schemas, errors)
- Safety and policy boundaries
- Determinism/idempotency semantics
- Observability and auditability (run manifests, structured errors)

## Post-PR Checklist (CI + Review)

After opening a PR:

- Ensure GitHub Actions checks are green.
- If you are a reviewer (not the PR author), you can wait for checks and approve/merge via:

```bash
bash scripts/pr_wait_and_merge.sh <pr-number-or-url>
```

Note: GitHub does not allow approving your own PR; the script will attempt approval best-effort.

## Security Reporting

This project may eventually control powerful editor automation workflows. Treat it as security-sensitive.

- **Do not** open public issues for vulnerabilities that enable remote code execution, credential exposure, or destructive automation without adequate safeguards.
- Prefer private disclosure (via repository Security advisories, if enabled).
- Include:
  - Impact assessment
  - Reproduction steps
  - Suggested mitigations

## Licensing and DCO/CLA

Unless otherwise specified:

- Contributions are accepted under the repository license.
- If a DCO/CLA is introduced later, contributors may be asked to sign off accordingly.
