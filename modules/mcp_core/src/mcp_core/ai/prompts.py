import hashlib
from typing import Any

from pydantic import BaseModel, Field


class PromptTemplate(BaseModel):
    """
    Represents a versioned prompt template.
    """
    name: str
    version: int
    template: str
    description: str | None = None
    input_variables: list[str] = Field(default_factory=list)

    @property
    def content_hash(self) -> str:
        """
        Returns a SHA-256 hash of the template content and version.
        Used for provenance tracking.
        """
        content = f"{self.name}:{self.version}:{self.template}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def format(self, **kwargs: Any) -> str:
        """
        Formats the template with the provided variables.
        Raises ValueError if required variables are missing.
        """
        missing = [var for var in self.input_variables if var not in kwargs]
        if missing:
            raise ValueError(f"Missing required variables for prompt '{self.name}': {', '.join(missing)}")
        
        # Simple f-string style formatting, but safer to use string.Template or jinja2 if complex.
        # For now, we assume simple {var} substitution using str.format map.
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            # This catches cases where the template has {var} but it wasn't in input_variables checks
            # or extra braces.
            raise ValueError(f"Error formatting prompt '{self.name}': {e}")


class PromptRegistry:
    """
    Registry for managing prompt templates.
    """
    def __init__(self):
        self._templates: dict[str, dict[int, PromptTemplate]] = {}

    def register(self, template: PromptTemplate) -> None:
        """Register a new prompt template."""
        if template.name not in self._templates:
            self._templates[template.name] = {}
        
        if template.version in self._templates[template.name]:
            raise ValueError(f"Prompt '{template.name}' version {template.version} already registered.")
            
        self._templates[template.name][template.version] = template

    def get(self, name: str, version: int | None = None) -> PromptTemplate:
        """
        Retrieve a prompt template by name and optional version.
        If version is None, returns the latest version.
        """
        if name not in self._templates:
            raise ValueError(f"Prompt '{name}' not found.")
            
        versions = self._templates[name]
        
        if version is not None:
            if version not in versions:
                raise ValueError(f"Prompt '{name}' version {version} not found.")
            return versions[version]
            
        # Get latest version
        latest_version = max(versions.keys())
        return versions[latest_version]

    def list_prompts(self) -> list[dict[str, Any]]:
        """List all registered prompts."""
        result = []
        for name, versions in self._templates.items():
            for version, tmpl in versions.items():
                result.append({
                    "name": name,
                    "version": version,
                    "description": tmpl.description,
                    "hash": tmpl.content_hash
                })
        return result
