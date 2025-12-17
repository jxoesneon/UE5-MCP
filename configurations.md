# MCP Configurations

## Overview
This document defines MCP’s configuration model: file locations, schema, precedence, secrets handling, and operational guidance.

Configuration is split by **target runtime**:

- Blender: `~/.mcp/blender_mcp_config.json`
- UE5: `~/.mcp/ue5_mcp_config.json`

Implementations SHOULD support a single “effective config” view that merges defaults, config files, environment overrides, and CLI overrides.

## Goals
- **Reproducibility**: runs must be traceable to an immutable config snapshot hash.
- **Safety**: secrets are never logged; destructive settings default to off.
- **Portability**: configs are explicit and can be checked into a project repo (without secrets).
- **Clarity**: every key has a documented type, default, and scope.

## Configuration Precedence
Highest priority wins:

1. CLI flags (implementation-defined)
2. Environment variables
3. Target config file (Blender/UE5)
4. Built-in defaults

## Secrets Handling
- Secrets MUST be supplied via environment variables or a separate secrets store.
- Config files MUST NOT require embedding secrets.
- Implementations MUST redact secrets in logs and in `mcp.config get` output by default.

Recommended convention:

- `MCP_AI_API_KEY` (or provider-specific equivalents)

## Schema (Conceptual)
The following is a conceptual schema. Implementations SHOULD also publish a JSON Schema for validation.

### 1) Common Keys
```json
{
  "protocol_version": "1.0",
  "logging": {
    "level": "INFO",
    "format": "json",
    "output": "stdout"
  },
  "artifacts": {
    "root": "~/.mcp/artifacts",
    "write_manifests": true
  },
  "policy": {
    "allow_destructive": false,
    "allowed_paths": [],
    "tool_allowlist": []
  },
  "ai": {
    "enabled": true,
    "provider": "openai",
    "budget": {
      "max_requests_per_run": 20,
      "max_total_tokens": 20000,
      "max_total_cost_usd": 5.0,
      "timeout_seconds": 60
    }
  }
}
```

### 2) Blender Target Keys
```json
{
  "blender": {
    "scene_generation": {
      "default_style": "realistic",
      "object_variation": true,
      "default_seed": 0
    },
    "asset_processing": {
      "texture_resolution": "4K",
      "lod_levels": 3,
      "batch_processing": true
    },
    "export": {
      "default_format": "fbx",
      "include_textures_by_default": false,
      "axis": "-Z+Y",
      "scale": 1.0
    }
  }
}
```

### 3) UE5 Target Keys
```json
{
  "ue5": {
    "level_design": {
      "default_terrain_size": [1000, 1000],
      "auto_populate": false,
      "default_seed": 0
    },
    "performance": {
      "dynamic_lighting": false,
      "max_polycount": 500000,
      "physics_enabled": true,
      "budgets": {
        "max_instances": 200000,
        "max_draw_calls": 5000
      }
    }
  }
}
```

## Environment Variables
Implementations SHOULD support overrides using environment variables.

Recommended patterns:

- `MCP_LOG_LEVEL`
- `MCP_ARTIFACTS_ROOT`
- `MCP_AI_ENABLED`
- `MCP_AI_PROVIDER`
- `MCP_AI_API_KEY`

## Validation
- Config MUST be validated on startup.
- Unknown keys SHOULD be rejected (or surfaced as warnings) to prevent silent misconfiguration.

## Operational Guidance

### Local Development
- Use JSON logs to simplify debugging.
- Keep artifact manifests enabled.

### CI
- Force `ai.enabled=false` unless explicitly testing AI.
- Use `--dry-run` flows to validate schemas and manifests.

### Shared Team Environments
- Enforce tool allowlists and path allowlists.
- Keep secrets in environment variables managed by the CI/CD system.

## Updating Configurations
Implementations MAY provide:

- `mcp.config get <key>`
- `mcp.config set <key> <value>`
- `mcp.reset_config`

For troubleshooting issues, see `troubleshooting.md`.
