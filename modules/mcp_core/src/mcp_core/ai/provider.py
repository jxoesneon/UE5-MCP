from abc import ABC, abstractmethod

from .models import (
    AICompletionRequest,
    AICompletionResponse,
    ImageGenerationRequest,
    ImageGenerationResponse,
)


class AIProvider(ABC):
    """
    Abstract base class for AI providers (e.g., OpenAI, Anthropic, Local).
    Encapsulates connection logic, authentication, and format adaptation.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the provider (e.g., 'openai', 'anthropic')."""
        ...

    @abstractmethod
    async def generate_text(self, request: AICompletionRequest) -> AICompletionResponse:
        """
        Generate text based on the request.
        Must handle retries and timeouts internally or via decoration.
        """
        ...

    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """
        Generate images based on the request.
        Providers that don't support images should raise NotImplementedError.
        """
        raise NotImplementedError(f"Provider {self.name} does not support image generation.")

    @abstractmethod
    async def check_health(self) -> bool:
        """
        Check if the provider is reachable and authenticated.
        """
        ...
