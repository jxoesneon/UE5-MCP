# MCP Troubleshooting Guide

## Overview

This document provides diagnostic playbooks for common MCP failures across:

- CLI/runtime
- Blender target integration
- UE5 target integration
- AI provider integration

It assumes MCP returns structured errors as defined in `api_reference.md`.

## Before You Debug

### Capture a Reproducible Run

For any report, collect:

- exact command invoked
- whether you used `--dry-run` or `--apply`
- the returned `run_id` and `request_id`
- the active config files:
  - `~/.mcp/blender_mcp_config.json`
  - `~/.mcp/ue5_mcp_config.json`
- the artifact root and any generated manifests (see below)

### Logs and Artifacts

The exact locations are implementation-defined, but the recommended defaults are:

- Logs: JSON logs to stdout (and optionally a log file if configured)
- Artifacts: `~/.mcp/artifacts`
- Run manifests: `~/.mcp/artifacts/<run_id>/run_manifest.json`

If you enabled file logging, include the log file path.

## Error Code Triage

Use the `error.code` to choose the correct playbook.

### `VALIDATION_ERROR`

- **Meaning**: Inputs do not match the tool schema.
- **Fix**:
  - re-check argument order and types
  - run `mcp.help "<tool>"` to confirm schema

### `DEPENDENCY_MISSING`

- **Meaning**: Required runtime/plugin/add-on is missing.
- **Fix**:
  - confirm Blender/UE plugins and Python dependencies as per `dependencies.md`
  - verify the target environment is the expected version

### `TARGET_UNAVAILABLE`

- **Meaning**: Blender/UE target is not reachable.
- **Fix**:
  - verify the target is running
  - verify transport settings (port/path/stdio)
  - ensure local firewall rules allow local connections

### `POLICY_DENIED`

- **Meaning**: Safety/policy layer rejected the action.
- **Fix**:
  - inspect policy configuration (`configurations.md`)
  - confirm whether the tool is allowlisted
  - confirm whether the path is allowlisted
  - confirm destructive actions are enabled only when intended

### `TIMEOUT`

- **Meaning**: Tool did not complete within the configured timeout.
- **Fix**:
  - re-run with a higher timeout budget
  - reduce workload (e.g., lower density, smaller terrain)
  - check whether the target is stalled (UE5 editor busy)

### `IO_ERROR`

- **Meaning**: Filesystem operations failed.
- **Fix**:
  - confirm the destination path exists
  - confirm write permissions
  - avoid overwrites unless explicitly enabled

### `INTERNAL_ERROR`

- **Meaning**: Unexpected failure.
- **Fix**:
  - include logs + artifacts + config snapshot hash in the report
  - attempt a minimal reproduction with `--dry-run`

## General Issues

### MCP Not Running / CLI Not Found

Symptoms:

- `command not found: mcp`
- module import errors

Resolution:

- confirm your Python version meets `dependencies.md`
- confirm MCP is installed in the active environment
- confirm `PATH` includes the installed entrypoint
- try running via the module directly: `python -m mcp`

### Config Parse Errors

Symptoms:

- JSON parse failures
- `VALIDATION_ERROR` during startup

Resolution:

- validate JSON syntax
- remove unknown keys (unknown keys should be rejected or warned)
- reset to defaults and re-apply changes incrementally

## Blender Target Playbooks

### Scene Not Generating

Common causes:

- Blender is not running or MCP add-on is not enabled
- the tool attempted side effects without `--apply`
- insufficient permissions for scripting

Resolution:

- confirm Blender is running
- confirm the MCP integration is enabled
- run the tool in `--dry-run` first to validate inputs

### Exported Assets Missing Textures

Common causes:

- textures are not embedded or not referenced correctly
- relative texture paths are not portable

Resolution:

- export with textures explicitly included (if supported)
- verify the export manifest lists texture references

## UE5 Target Playbooks

### UE5 Not Reachable

Common causes:

- UE5 editor not running
- required plugins not enabled
- remote control/transport not configured

Resolution:

- enable:
  - `Python Editor Script Plugin`
  - `Procedural Content Generation (PCG) Framework`
- restart UE5 after enabling plugins

### Terrain/Population Causes Severe Slowdown

Common causes:

- high density instancing
- expensive materials
- lack of budget constraints

Resolution:

- re-run with lower density and explicit budgets
- profile with `mcp.profile_performance` and review the report artifact

### Generated Blueprints Don’t Compile

Common causes:

- incomplete node wiring
- engine API differences

Resolution:

- run `mcp.debug_blueprint "<name>"`
- treat generated output as a proposal; apply changes in a controlled branch/changelist

## AI Integration Playbooks

### AI Features Not Working

Common causes:

- `ai.enabled=false`
- missing API key
- provider outage or network restrictions

Resolution:

- confirm config and environment variables as per `configurations.md`
- confirm budget limits are not exceeded

## Resetting to a Known-Good State

If problems persist:

- reset configuration:

```bash
mcp.reset_config
```

- delete only the artifact cache if safe (implementation-defined)

For additional help, refer to `configurations.md`.
