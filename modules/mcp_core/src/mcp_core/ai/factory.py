from mcp_core.config.settings import settings

from .client import AIClient
from .openai_provider import OpenAIProvider
from .provider import AIProvider


def create_ai_client() -> AIClient:
    """
    Factory function to create an AIClient instance based on global settings.
    """
    if not settings.ai.enabled:
        # If AI is disabled, we might still return a client but with a dummy provider
        # or handle it upstream. For now, we assume enabled check happens before usage
        # or we could return a specific 'NoOpProvider' if needed.
        # But let's respect the config and default to OpenAI if enabled.
        pass

    provider: AIProvider
    
    # Simple registry dispatch
    provider_name = settings.ai.provider.lower()
    
    if provider_name == "openai":
        provider = OpenAIProvider()
    else:
        # Fallback or error
        raise ValueError(f"Unsupported AI provider: {provider_name}")

    return AIClient(
        provider=provider,
        config=settings.ai,
        safety_config=settings.safety
    )
