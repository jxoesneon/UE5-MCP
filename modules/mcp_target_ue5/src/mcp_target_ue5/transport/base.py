from abc import ABC, abstractmethod
from typing import Any


class UE5Transport(ABC):
    """Abstract base class for UE5 transport mechanisms."""
    
    @abstractmethod
    def send_command(self, command: str, params: dict[str, Any]) -> dict[str, Any]:
        """Send a command to UE5 and return the result."""
        pass
        
    @abstractmethod
    def connect(self) -> None:
        """Establish connection to UE5."""
        pass
        
    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to UE5."""
        pass
