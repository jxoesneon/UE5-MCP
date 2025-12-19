# Blender Setup Guide

This guide explains how to set up MCP to work with Blender.

## Prerequisites

- **Blender 3.0+** installed
- **Python 3.11+** installed
- **UE5-MCP** installed (see main README.md)

## How It Works

MCP communicates with Blender using a **stdio transport**:

1. MCP spawns Blender as a subprocess in background mode
2. A Python server script (`blender_server.py`) runs inside Blender
3. Commands are sent via stdin/stdout using JSON messages
4. The server script has full access to Blender's `bpy` API

```text
┌─────────────┐     stdin/stdout      ┌─────────────────────┐
│   MCP CLI   │ ◄──── JSON ────────► │  Blender (bpy)      │
│             │                       │  blender_server.py  │
└─────────────┘                       └─────────────────────┘
```

## Setup Steps

### Step 1: Verify Blender Installation

Ensure Blender is accessible from the command line:

```bash
# Check if Blender is in PATH
blender --version

# If not found, add Blender to your PATH or note the full path
# macOS example: /Applications/Blender.app/Contents/MacOS/Blender
# Windows example: C:\Program Files\Blender Foundation\Blender 3.6\blender.exe
# Linux example: /usr/bin/blender
```

### Step 2: Configure MCP

Create or update your MCP configuration file:

**Location:** `~/.mcp/blender_mcp_config.json`

```json
{
  "blender": {
    "executable_path": "blender",
    "startup_timeout": 30,
    "command_timeout": 60
  }
}
```

**Configuration Options:**

| Option             | Default       | Description                            |
|--------------------|---------------|----------------------------------------|
| `executable_path`  | `"blender"`   | Path to Blender executable             |
| `startup_timeout`  | `30`          | Seconds to wait for Blender to start   |
| `command_timeout`  | `60`          | Seconds to wait for command completion |

**Example for macOS (if Blender not in PATH):**

```json
{
  "blender": {
    "executable_path": "/Applications/Blender.app/Contents/MacOS/Blender"
  }
}
```

**Example for Windows:**

```json
{
  "blender": {
    "executable_path": "C:\\Program Files\\Blender Foundation\\Blender 3.6\\blender.exe"
  }
}
```

### Step 3: Test the Connection

Run a simple test command:

```bash
# Dry-run mode (doesn't require Blender to be running)
mcp blender generate-scene "A simple cube" --dry-run

# Full mode (will spawn Blender)
mcp blender generate-scene "A simple cube"
```

## Troubleshooting

### "Blender executable not found"

**Cause:** Blender is not in your system PATH.

**Solution:**
1. Add Blender to your PATH, or
2. Specify the full path in the config file

```bash
# Find Blender location
# macOS
mdfind -name "Blender.app"

# Linux
which blender
locate blender

# Windows (PowerShell)
Get-Command blender
```

### "Blender process closed connection unexpectedly"

**Cause:** Blender crashed or the server script failed to load.

**Solution:**

1. Check Blender can run in background mode:

```bash
blender --background --python -c "import bpy; print('OK')"
```

1. Check for Python errors in Blender's console output
1. Ensure no other MCP instance is running

### "Command timed out"

**Cause:** Complex operations taking longer than the timeout.

**Solution:**
Increase the timeout in your config:

```json
{
  "blender": {
    "command_timeout": 300
  }
}
```

### Blender opens a window instead of running in background

**Cause:** Some Blender operations require a display.

**Solution:**
On Linux, use a virtual framebuffer:

```bash
xvfb-run blender --background ...
```

Or set the environment variable:

```bash
export BLENDER_HEADLESS=1
```

## Supported Commands

| Command            | Description                       |
|--------------------|-----------------------------------|
| `generate-scene`   | Generate a scene from description |
| `add-object`       | Add an object to the scene        |
| `generate-texture` | Generate texture for an object    |
| `export-asset`     | Export scene/object to file       |

## Example Workflow

```bash
# 1. Generate a scene
mcp blender generate-scene "A medieval village with houses and a well"

# 2. Add more objects
mcp blender add-object --type cube --name "Tower" --location 10,0,0

# 3. Generate textures
mcp blender generate-texture "Tower" --type "stone wall"

# 4. Export for UE5
mcp blender export-asset "medieval_village" --format fbx --output ./exports/
```

## Advanced: Manual Server Mode

For development or debugging, you can run the Blender server manually:

```bash
# Start Blender with the server script
blender --background --python /path/to/blender_server.py

# In another terminal, send commands manually
echo '{"command": "ping", "params": {}, "id": 1}' | nc localhost 5000
```

## Next Steps

- See `docs/setup/ue5_setup.md` for importing assets into Unreal
- See `workflow.md` for end-to-end pipelines
- See `commands.md` for all available commands
