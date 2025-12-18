import json
import os
import subprocess
import sys
from typing import Any, cast

from .base import BlenderTransport


class StdioTransport(BlenderTransport):
    """
    Transport implementation using standard I/O (subprocess).
    Launches Blender in background mode and communicates via stdin/stdout.
    """
    def __init__(self, blender_path: str = "blender"):
        self.blender_path = blender_path
        self._process: subprocess.Popen | None = None

    def connect(self) -> None:
        """
        Launch Blender in background with the listener script.
        """
        if self._process is not None:
            return

        # Locate the server script
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "scripts",
            "blender_server.py"
        )

        if not os.path.exists(script_path):
            # Fallback for dev environment or differing install layout
            # Try to find it relative to module root if not found in package
            # This logic might need adjustment based on install method
            pass

        cmd = [
            self.blender_path,
            "--background",
            "--python",
            script_path
        ]

        try:
            self._process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=sys.stderr, # Forward stderr for logging
                text=True,
                bufsize=1
            )
        except FileNotFoundError:
            raise RuntimeError(f"Blender executable not found at '{self.blender_path}'. Please ensure Blender is installed and in PATH, or configure the path.")

    def disconnect(self) -> None:
        """
        Terminate the Blender process.
        """
        if self._process:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None

    def send_command(self, command: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Send a JSON command to Blender's stdin and read response from stdout.
        """
        if not self._process:
            self.connect()

        if not self._process or not self._process.stdin or not self._process.stdout:
             raise RuntimeError("Blender process not connected")

        request = {
            "command": command,
            "params": params,
            "id": 1 # Simple ID for now
        }

        try:
            self._process.stdin.write(json.dumps(request) + "\n")
            self._process.stdin.flush()

            response_line = self._process.stdout.readline()
            if not response_line:
                raise RuntimeError("Blender process closed connection unexpectedly")

            response = json.loads(response_line)

            if response.get("status") == "error":
                raise RuntimeError(f"Blender error: {response.get('error')}")

            return cast(dict[str, Any], response)

        except BrokenPipeError:
            self._process = None
            raise RuntimeError("Blender process pipe broken")
