# Unreal Engine 5 Setup Guide

This guide explains how to set up MCP to work with Unreal Engine 5.

## Prerequisites

- **Unreal Engine 5.1+** installed
- **Python 3.11+** installed
- **UE5-MCP** installed (see main README.md)

## How It Works

MCP communicates with UE5 using an **HTTP transport**:

1. A Python HTTP server runs inside the UE5 Editor
2. MCP sends commands via HTTP POST to `localhost:8080`
3. The server executes commands using UE5's Python API
4. Results are returned as JSON responses

```text
MCP CLI  <-- HTTP/JSON (localhost:8080) -->  UE5 Editor (ue5_mcp_server.py)
```

## Setup Steps

### Step 1: Enable Required UE5 Plugins

Open your UE5 project and enable these plugins:

1. **Edit → Plugins**
2. Search and enable:
   - ✅ **Python Editor Script Plugin** (required)
   - ✅ **Procedural Content Generation Framework** (for terrain/population)
   - ✅ **Editor Scripting Utilities** (recommended)

3. **Restart the Editor** when prompted

### Step 2: Install the MCP Server Script

Copy the server script to your UE5 project:

```bash
# From the UE5-MCP repository
cp modules/mcp_target_ue5/plugin/ue5_mcp_server.py /path/to/YourProject/Content/Python/
```

**Or manually:**

1. Navigate to `modules/mcp_target_ue5/plugin/`
2. Copy `ue5_mcp_server.py`
3. Paste into your UE5 project's `Content/Python/` folder
   - Create the `Python` folder if it doesn't exist

### Step 3: Start the MCP Server in UE5

#### Option A: Run manually (recommended for first-time setup)

1. Open UE5 Editor
2. Open **Window → Developer Tools → Output Log**
3. In the command bar at the bottom, type:

```text
py ue5_mcp_server
```

1. You should see: `[MCP] MCP Server started on http://localhost:8080`

#### Option B: Auto-start on editor launch

Create a startup script:

1. Create file: `Content/Python/init_unreal.py`
2. Add this content:

```python
import ue5_mcp_server
ue5_mcp_server.start_server_async()
```

1. The server will now start automatically when UE5 opens.

### Step 4: Configure MCP

Create or update your MCP configuration file:

**Location:** `~/.mcp/ue5_mcp_config.json`

```json
{
  "ue5": {
    "host": "localhost",
    "port": 8080,
    "timeout": 30
  }
}
```

**Configuration Options:**

| Option    | Default       | Description                 |
|-----------|---------------|-----------------------------|
| `host`    | `"localhost"` | UE5 server host             |
| `port`    | `8080`        | UE5 server port             |
| `timeout` | `30`          | Command timeout in seconds  |

### Step 5: Test the Connection

```bash
# Check if the server is running
curl http://localhost:8080/health

# Expected response:
# {"status": "ok", "engine_version": "5.3.0"}

# Test with MCP CLI (dry-run)
mcp ue5 generate-terrain 1000 1000 --dry-run

# Test with MCP CLI (real)
mcp ue5 generate-terrain 1000 1000 --detail high
```

## Troubleshooting

### "Connection refused"

**Cause:** The MCP server is not running in UE5.

**Solution:**

1. Open UE5 Editor
2. Run in the Output Log:

```text
py ue5_mcp_server
```

1. Check for any error messages

### "Python Editor Script Plugin not found"

**Cause:** The plugin is not enabled.

**Solution:**

1. Edit → Plugins
2. Search for "Python"
3. Enable "Python Editor Script Plugin"
4. Restart the editor

### "Module 'unreal' not found"

**Cause:** Running the script outside of UE5.

**Solution:**
The script must run inside UE5's Python environment. Run it via:

- Output Log: `py ue5_mcp_server`
- Or place in `Content/Python/` and import

### "Port 8080 already in use"

**Cause:** Another application is using the port.

**Solution:**
Change the port in both places:

1. In UE5 (environment variable):

```python
import os
os.environ["MCP_SERVER_PORT"] = "8081"
import ue5_mcp_server
ue5_mcp_server.start_server_async()
```

1. In MCP config (`~/.mcp/ue5_mcp_config.json`):

```json
{
  "ue5": {
    "port": 8081
  }
}
```

### Commands timeout or fail

**Cause:** Complex operations taking too long, or level not loaded.

**Solution:**
1. Ensure a level/map is open in the editor
2. Increase timeout in config
3. Check Output Log for errors

## Supported Commands

| Command               | Description                          |
|-----------------------|--------------------------------------|
| `import-asset`        | Import asset from Blender export     |
| `generate-terrain`    | Generate terrain with PCG            |
| `populate-level`      | Populate level with assets           |
| `generate-blueprint`  | Generate Blueprint from description  |
| `profile-performance` | Profile level performance            |
| `optimize-level`      | Run optimization pass                |
| `debug-blueprint`     | Debug a Blueprint                    |

## Example Workflow

```bash
# 1. Generate terrain
mcp ue5 generate-terrain 2000 2000 --detail high --seed 12345

# 2. Populate with trees
mcp ue5 populate-level --asset "Tree_01" --density 500 --seed 12345

# 3. Import asset from Blender
mcp ue5 import-asset ./exports/bridge_manifest.json

# 4. Generate a door Blueprint
mcp ue5 generate-blueprint "A door that opens when the player approaches"

# 5. Profile performance
mcp ue5 profile-performance "MainLevel"
```

## Security Notes

By default, the MCP server only accepts connections from `localhost`. This is intentional for security.

**Do NOT enable remote access** unless you:
1. Are on a trusted network
2. Have implemented authentication
3. Understand the risks

To enable remote access (not recommended):

```python
import os
os.environ["MCP_ENABLE_REMOTE"] = "true"
```

## Advanced: C++ Plugin Alternative

For production use, consider the C++ plugin variant which offers:
- Better performance
- Tighter UE5 integration
- No Python dependency at runtime

See `modules/mcp_target_ue5/plugin/README.md` for details.

## Next Steps

- See `docs/setup/blender_setup.md` for asset creation
- See `workflow.md` for end-to-end pipelines
- See `commands.md` for all available commands
