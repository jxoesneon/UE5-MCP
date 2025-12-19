# UE5-MCP Quickstart Guide

Get up and running with UE5-MCP in 10 minutes.

## Overview

UE5-MCP enables AI-assisted automation across Blender and Unreal Engine 5. This guide covers the minimal setup to start using MCP.

## Prerequisites

| Component     | Minimum Version | Download                                      |
|---------------|-----------------|-----------------------------------------------|
| Python        | 3.11+           | [python.org](https://python.org)              |
| Blender       | 3.0+            | [blender.org](https://blender.org)            |
| Unreal Engine | 5.1+            | [unrealengine.com](https://unrealengine.com)  |

## Installation

### Step 1: Install UE5-MCP

```bash
# Clone the repository
git clone https://github.com/jxoesneon/UE5-MCP.git
cd UE5-MCP

# Install with uv (recommended)
uv sync
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\activate  # Windows

# Verify installation
mcp --version
# or: python -m mcp --version
```

### Step 2: Create Configuration

Create the config directory and file:

```bash
mkdir -p ~/.mcp
```

Create config files in `~/.mcp/`:

```json
{
  "blender": {
    "executable_path": "blender"
  },
  "ue5": {
    "host": "localhost",
    "port": 8080
  },
  "ai": {
    "provider": "openai",
    "enabled": true
  }
}
```

### Step 3: Set Up API Keys (Optional)

For AI-powered features, set your OpenAI API key:

```bash
# Linux/macOS
export OPENAI_API_KEY="your-api-key-here"

# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"
```

## Quick Tests

### Test Blender Connection

**No addon installation needed** - MCP automatically manages Blender:

```bash
# Dry-run (doesn't need Blender running)
mcp blender generate-scene "A red cube" --dry-run

# Real execution (MCP spawns Blender automatically)
mcp blender generate-scene "A red cube"
```

### Test UE5 Connection

First, set up the UE5 server:

1. Open your UE5 project
2. Enable **Python Editor Script Plugin** (Edit → Plugins)
3. Copy `modules/mcp_target_ue5/plugin/ue5_mcp_server.py` to your project's `Content/Python/` folder
4. Run `py ue5_mcp_server` in the Output Log

Then test:

```bash
# Check connection
curl http://localhost:8080/health

# Dry-run command
mcp ue5 generate-terrain 1000 1000 --dry-run
```

## Example Workflow

### Create and Export Asset from Blender

```bash
# Generate a medieval house
mcp blender generate-scene "A medieval stone house with a wooden door"

# Export to FBX
mcp blender export-asset "medieval_house" --format fbx --output ./exports/
```

### Import Asset into UE5

```bash
# Import the exported asset
mcp ue5 import-asset ./exports/medieval_house_manifest.json
```

### Generate UE5 Content

```bash
# Generate terrain
mcp ue5 generate-terrain 2000 2000 --detail high

# Populate with trees
mcp ue5 populate-level --asset "Tree_01" --density 100

# Create interactive Blueprint
mcp ue5 generate-blueprint "A treasure chest that opens when clicked"
```

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                        MCP CLI                               │
│                    (mcp command)                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           ▼                               ▼
┌──────────────────────┐       ┌──────────────────────┐
│   Blender Target     │       │    UE5 Target        │
│                      │       │                      │
│  Transport: Stdio    │       │  Transport: HTTP     │
│  (subprocess)        │       │  (localhost:8080)    │
└──────────┬───────────┘       └──────────┬───────────┘
           │                              │
           ▼                              ▼
┌──────────────────────┐       ┌──────────────────────┐
│      Blender         │       │    UE5 Editor        │
│  blender_server.py   │       │  ue5_mcp_server.py   │
│  (bpy API)           │       │  (unreal API)        │
└──────────────────────┘       └──────────────────────┘
```

## What's Next?

- **Blender Setup Guide** (`docs/setup/blender_setup.md`) - Detailed Blender configuration
- **UE5 Setup Guide** (`docs/setup/ue5_setup.md`) - Detailed UE5 configuration
- **Commands Reference** (`commands.md`) - All available commands
- **Workflow Guide** (`workflow.md`) - End-to-end pipelines
- **AI Integration** (`ai_integration.md`) - AI-powered features

## Troubleshooting

### Common Issues

| Issue                      | Solution                                      |
|----------------------------|-----------------------------------------------|
| `mcp: command not found`   | Use `python -m mcp` instead, or check PATH    |
| `Blender not found`        | Set `executable_path` in config               |
| `Connection refused (UE5)` | Start the server: `py ue5_mcp_server`         |
| `OPENAI_API_KEY not set`   | Export the environment variable               |

### Getting Help

- Check `troubleshooting.md`
- Open an issue on [GitHub](https://github.com/jxoesneon/UE5-MCP/issues)
- See detailed logs with `--verbose` flag
