# UE5-MCP Monorepo Structure

```text
UE5-MCP/
│
├── modules/                       # Core functional modules
│
│   ├── mcp_protocol/               # Contracts + schemas (source of truth)
│   │   ├── schemas/                # JSON Schema for requests/results/errors
│   │   ├── versions/               # Versioned protocol artifacts (e.g., v1, v1.1)
│   │   └── python/                 # Pydantic/dataclass models generated from schemas
│   │
│   ├── mcp_core/                   # Control-plane runtime (planner/executor/policy)
│   │   ├── registry/               # Command registry + tool descriptors
│   │   ├── planning/               # Planner interface + plan IR
│   │   ├── execution/              # Executor + idempotency + rollback
│   │   ├── policy/                 # Policy engine + allow/deny rules
│   │   ├── storage/                # Artifacts + run manifests
│   │   └── observability/          # Structured logging + traces + metrics
│   │
│   ├── mcp_cli/                    # CLI entrypoint (thin wrapper over mcp_core)
│   │   └── mcp/                    # `python -m mcp` / console_scripts
│   │
│   ├── mcp_target_blender/         # Blender adapter boundary (editor-time automation)
│   │   ├── transport/              # stdio/IPC/HTTP adapters
│   │   ├── addon/                  # Blender add-on shape (packaged separately)
│   │   └── scripts/                # Blender Python scripts invoked by adapter
│   │
│   └── mcp_target_ue5/             # UE5 adapter boundary (editor-time automation)
│       ├── transport/              # Remote Control API / TCP / stdio bridges
│       ├── plugin/                # UE plugin shape (packaged separately)
│       └── scripts/                # UE Python scripts + templates
│
├── docs/                           # Long-form specs (eventually migrate root *.md here)
├── tests/                          # Cross-package tests (contract + integration)
│   ├── contract/                   # Schema and API conformance tests
│   ├── integration/                # Adapter tests using fakes/simulators
│   └── e2e/                        # Optional end-to-end tests (require Blender/UE)
│
├── tools/                          # Dev tooling (linters, generators, release helpers)
├── scripts/                        # Repo scripts (bootstrap, smoke, release)
├── .github/                        # CI, issue/PR templates, security metadata
│
├── pyproject.toml                  # Root workspace config (tooling + shared settings)
├── uv.lock                         # Reproducible dependency lock (preferred)
└── README.md
```

## Purpose

This document defines the *recommended* repository layout for a 2025 Python-first implementation of the UE5-MCP specification.

- **Specification-first**: The docs in this repository are the contract; code must conform.
- **Control-plane vs data-plane**: `mcp_core` orchestrates; targets (Blender/UE5) execute editor-time actions.
- **Packaging-ready**: Each module is a real Python package with independent tests and clear boundaries.

## Design Principles

- **Stable contracts**: JSON schema + versioned protocol artifacts live in `modules/mcp_protocol/`.
- **Thin adapters**: Blender/UE5 packages should focus on transport + target-specific execution, not orchestration.
- **Determinism and auditability**: Runs produce manifests and artifacts (see `architecture.md`, `automation.md`).
- **Replaceable AI**: AI provider integrations must remain optional and isolated behind interfaces.

## Build and Dependency Management (2025 baseline)

- **Python**: 3.11+.
- **Reproducibility**: prefer `uv.lock` (or an equivalent lock) committed to the repo.
- **Optional extras**: target-specific dependencies are installed via extras (e.g., `.[blender]`, `.[ue5]`, `.[dev]`).

## Testing and Quality Gates

- **Unit tests**: colocated per module (fast, hermetic).
- **Contract tests**: validate that CLI/SDK outputs conform to JSON schemas.
- **Integration tests**: run adapters against fakes/stubs; real Blender/UE tests are opt-in.
- **CI gates** (recommended): formatting + linting, type checking, tests, schema validation, docs link checks.

## Release and Versioning

- **SemVer**: version the protocol and the implementation separately.
- **Protocol**: changes tracked under `modules/mcp_protocol/versions/` and tested via contract suite.
- **Implementation**: tagged releases; changelog entries must link to protocol version compatibility.

## Mapping Features to Packages

- **Command surface**: `modules/mcp_cli/` (user-facing) calling into `modules/mcp_core/`.
- **Planning/execution**: `modules/mcp_core/planning` and `modules/mcp_core/execution`.
- **UE5 automation**: `modules/mcp_target_ue5/` (Remote Control API, Python Editor Scripting, etc.).
- **Blender automation**: `modules/mcp_target_blender/` (addon + scripts + IPC).

## Additional Enhancements to Consider

Dedicated AI Scripting Layer

Add a `modules/mcp_ai/` package if/when AI becomes a first-class runtime component (providers, evals, budgeting).
Integration with AI Services

Ensure adapters can call provider-agnostic interfaces from `mcp_core` rather than embedding provider logic.
Cloud vs. Local Compute

 Support both on-premise and cloud AI inference for asset generation and debugging.
