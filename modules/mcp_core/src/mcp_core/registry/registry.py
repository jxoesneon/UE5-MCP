from collections.abc import Callable
from typing import Any, NamedTuple

from pydantic import BaseModel


class ToolEntry(NamedTuple):
    name: str
    description: str
    input_model: type[BaseModel]
    handler: Callable[[Any], Any]

class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolEntry] = {}

    def register(
        self,
        name: str,
        description: str,
        input_model: type[BaseModel],
        handler: Callable[[Any], Any],
    ) -> None:
        if name in self._tools:
            raise ValueError(f"Tool '{name}' is already registered.")
        
        self._tools[name] = ToolEntry(
            name=name,
            description=description,
            input_model=input_model,
            handler=handler,
        )

    def get_tool(self, name: str) -> ToolEntry | None:
        return self._tools.get(name)

    def list_tools(self) -> list[ToolEntry]:
        return sorted(self._tools.values(), key=lambda t: t.name)

    def clear(self) -> None:
        """Clear all registered tools. Useful for testing."""
        self._tools.clear()

# Global registry instance
registry = ToolRegistry()
