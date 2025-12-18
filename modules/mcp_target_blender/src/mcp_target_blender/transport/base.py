from abc import ABC, abstractmethod
from typing import Any

class BlenderTransport(ABC):
    """Abstract base class for Blender transport mechanisms."""
    
    @abstractmethod
    def send_command(self, command: str, params: dict[str, Any]) -> dict[str, Any]:
        """Send a command to Blender and return the result."""
        pass
        
    @abstractmethod
    def connect(self) -> None:
        """Establish connection to Blender."""
        pass
        
    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to Blender."""
        pass
