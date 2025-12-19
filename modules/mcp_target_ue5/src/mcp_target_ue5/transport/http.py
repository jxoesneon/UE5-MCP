from typing import Any

import httpx

from .base import UE5Transport


class TransportError(Exception):
    """Base error for transport failures."""
    def __init__(self, message: str, code: str = "TRANSPORT_ERROR"):
        super().__init__(message)
        self.code = code


class ConnectionError(TransportError):
    """Failed to connect to UE5."""
    def __init__(self, message: str):
        super().__init__(message, "TARGET_UNAVAILABLE")


class TimeoutError(TransportError):
    """Command timed out."""
    def __init__(self, message: str):
        super().__init__(message, "TIMEOUT")


class CommandError(TransportError):
    """UE5 returned an error."""
    def __init__(self, message: str):
        super().__init__(message, "EXECUTION_ERROR")


class HttpTransport(UE5Transport):
    """
    Transport implementation using HTTP to talk to a UE5 plugin server.
    """
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.timeout = 30.0

    def connect(self) -> None:
        """
        Check connectivity to the UE5 server.
        """
        try:
            response = httpx.get(f"{self.base_url}/health", timeout=5.0)
            response.raise_for_status()
        except httpx.RequestError as e:
            raise ConnectionError(f"Failed to connect to UE5 at {self.base_url}: {e}")
        except httpx.HTTPStatusError as e:
            raise ConnectionError(f"UE5 server returned error: {e}")

    def disconnect(self) -> None:
        """
        Close connection (no-op for HTTP).
        """
        pass

    def send_command(self, command: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Send a JSON command to UE5 via HTTP POST.
        """
        try:
            payload = {
                "command": command,
                "params": params
            }

            response = httpx.post(
                f"{self.base_url}/command",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            result: dict[str, Any] = response.json()

            if result.get("status") == "error":
                raise RuntimeError(f"UE5 Error: {result.get('error', 'Unknown error')}")

            return result

        except httpx.TimeoutException:
            raise TimeoutError(f"UE5 command '{command}' timed out after {self.timeout}s")
        except httpx.RequestError as e:
            raise ConnectionError(f"Network error communicating with UE5: {e}")
        except httpx.HTTPStatusError as e:
            raise CommandError(f"UE5 server returned HTTP error: {e}")
