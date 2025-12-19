# UE5-MCP Plugin

This folder contains the Unreal Engine 5 plugin components that enable MCP communication.

## Overview

The UE5-MCP plugin runs an HTTP server inside the Unreal Editor that listens for commands from the MCP CLI. This allows external tools to automate UE5 workflows.

## Installation Options

### Option 1: Python Editor Script (Recommended for Quick Setup)

Use the Python-based HTTP server script that runs inside UE5's Python environment.

**Requirements:**
- UE5 with `Python Editor Script Plugin` enabled

**Setup:**
1. Copy `ue5_mcp_server.py` to your UE5 project's `Content/Python/` folder
2. Enable the Python Editor Script Plugin in UE5
3. Run the script from the Output Log or set it to auto-run

### Option 2: C++ Plugin (Recommended for Production)

Use the full C++ plugin for better performance and tighter integration.

**Setup:**
1. Copy the `UE5MCP/` folder to your project's `Plugins/` directory
2. Regenerate project files
3. Build and enable the plugin

## HTTP API Endpoints

The server listens on `http://localhost:8080` by default.

### `GET /health`

Health check endpoint.

**Response:**

```json
{
  "status": "ok",
  "engine_version": "5.3.0"
}
```

### `POST /command`

Execute an MCP command.

**Request:**

```json
{
  "command": "generate_terrain",
  "params": {
    "width": 1000,
    "height": 1000,
    "detail_level": "high",
    "seed": 12345
  }
}
```

**Response:**

```json
{
  "status": "ok",
  "data": {
    "message": "Generated 1000x1000 terrain (high)",
    "terrain_path": "/Game/Maps/GeneratedTerrain"
  }
}
```

## Supported Commands

| Command              | Description                         |
|----------------------|-------------------------------------|
| `import_asset`       | Import asset from export manifest   |
| `generate_terrain`   | Generate terrain with PCG           |
| `populate_level`     | Populate level with assets          |
| `generate_blueprint` | Generate Blueprint from description |
| `profile_performance`| Profile level performance           |
| `optimize_level`     | Run optimization pass               |
| `debug_blueprint`    | Debug a Blueprint                   |

## Configuration

The server can be configured via environment variables or UE5 project settings:

| Variable            | Default     | Description                      |
|---------------------|-------------|----------------------------------|
| `MCP_SERVER_HOST`   | `localhost` | Bind address                     |
| `MCP_SERVER_PORT`   | `8080`      | Server port                      |
| `MCP_ENABLE_REMOTE` | `false`     | Allow non-localhost connections  |

## Security

By default, the server only accepts connections from `localhost`. This is intentional to prevent unauthorized access to your UE5 Editor.

To enable remote access (not recommended):
1. Set `MCP_ENABLE_REMOTE=true`
2. Implement authentication (see `ue5_mcp_server.py` for hooks)

## Troubleshooting

### Server not starting
- Ensure Python Editor Script Plugin is enabled
- Check Output Log for errors
- Verify port 8080 is not in use

### Connection refused
- Ensure the server is running (check Output Log)
- Verify firewall settings
- Check the correct port is configured

### Commands failing
- Check that required plugins are enabled (PCG Framework, etc.)
- Verify the target level/map is loaded
- Check Output Log for detailed errors
