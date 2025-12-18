from typing import Any

from pydantic import BaseModel, Field


class AIModelUsage(BaseModel):
    """Token usage statistics."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float | None = None


class AICompletionRequest(BaseModel):
    """Request to an AI provider for text generation."""
    prompt: str
    system_prompt: str | None = None
    model: str | None = None  # Provider-specific model identifier
    temperature: float = 0.7
    max_tokens: int | None = None
    stop_sequences: list[str] | None = None
    stream: bool = False
    
    # Metadata for logging/budgeting
    request_id: str | None = None
    user_id: str | None = None


class AICompletionResponse(BaseModel):
    """Response from an AI provider."""
    content: str
    model: str
    usage: AIModelUsage | None = None
    stop_reason: str | None = None
    provider_metadata: dict[str, Any] = Field(default_factory=dict)


class ImageGenerationRequest(BaseModel):
    """Request for image generation."""
    prompt: str
    n: int = 1
    size: str = "1024x1024"
    model: str | None = None


class ImageGenerationResponse(BaseModel):
    """Response for image generation."""
    urls: list[str]
    usage: AIModelUsage | None = None
