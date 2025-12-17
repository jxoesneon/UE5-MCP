# MCP Dependencies

## Overview
This document defines the **toolchain and dependency expectations** for building and running MCP across Blender and Unreal Engine 5.

The repository is intended to be reproducible in 2025 terms: pinned versions, lockfiles, and explicit platform requirements.

## Supported Platforms
- macOS (developer workstation)
- Windows (common UE5 workstation)
- Linux (CI and some content pipelines)

## 1. Language Runtime

### Python
- Minimum: Python 3.11
- Recommended: Python 3.12+

Rationale:

- Python 3.11+ performance and typing improvements
- Compatibility with modern packaging and tooling

## 2. Python Dependency Management (Reproducible)

MCP SHOULD be packaged using a modern Python packaging workflow.

Recommended approach:

- Use `pyproject.toml` for metadata and dependency declaration.
- Use a lockfile for reproducible installs.

Policy:

- Do not commit `venv/` directories.
- Pin and lock dependencies for CI and releases.

## 3. Python Packages (Conceptual Groups)

The concrete dependency list is implementation-defined, but the system typically requires:

### Core runtime
- Schema validation (JSON Schema)
- CLI framework
- HTTP/WebSocket/stdio transport utilities
- Structured logging

### Procedural / asset tooling
- Numeric + geometry helpers (`numpy`, optional)
- Image/texture processing (`pillow`, optional)

### AI providers (optional)
- Provider SDKs (e.g., OpenAI-compatible SDK)

### UE/Blender connectivity (optional)
- UnrealCV (only if using UnrealCV transport)

## 4. Blender Requirements

### Blender Version
- Minimum: Blender 3.x
- Recommended: Blender 4.x

### Add-ons
- `Node Wrangler` (recommended for material workflows)

### Blender execution model
MCP can integrate via:

- a Blender add-on that exposes an RPC interface
- a controlled “run script in Blender” automation path

## 5. Unreal Engine Requirements

### UE5 Version
- Minimum: Unreal Engine 5.1
- Recommended: Unreal Engine 5.3+

### Required Plugins
- `Python Editor Script Plugin`
- `Procedural Content Generation (PCG) Framework`

### Optional Plugins
- `UnrealCV Plugin` (only if UnrealCV-based transport is selected)

## 6. AI & Model Runtime Requirements

AI features are optional and must be gated by policy/config.

- Cloud providers require an API key (see `configurations.md`).
- Local diffusion models require sufficient GPU resources and are best run as a separate service.

## 7. Hardware Guidance (Workstations)
- **Blender + UE5**: 32GB RAM recommended.
- **GPU**: 8–16GB VRAM recommended for UE5 editor workflows; more for local image generation.

## 8. CI/CD Expectations
- CI MUST run in a fully reproducible environment (locked dependencies).
- CI SHOULD validate:
  - schema/tool definitions
  - formatting/lint
  - unit tests

For configuration details, refer to `configurations.md`.
