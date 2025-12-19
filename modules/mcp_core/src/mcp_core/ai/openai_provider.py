import os
from typing import cast

from openai import AsyncOpenAI, OpenAIError
from openai.types.chat import ChatCompletion

from .models import (
    AICompletionRequest,
    AICompletionResponse,
    AIModelUsage,
    ImageGenerationRequest,
    ImageGenerationResponse,
)
from .provider import AIProvider


class OpenAIProvider(AIProvider):
    """
    Concrete implementation of AIProvider for OpenAI's API.
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.client = AsyncOpenAI(
            api_key=api_key or os.environ.get("OPENAI_API_KEY"),
            base_url=base_url
        )

    @property
    def name(self) -> str:
        return "openai"

    async def generate_text(self, request: AICompletionRequest) -> AICompletionResponse:
        try:
            # Default to gpt-4o-mini if not specified, assuming it's a cost-effective default
            model = request.model or "gpt-4o-mini"

            messages: list[dict[str, str]] = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})

            messages.append({"role": "user", "content": request.prompt})

            response = cast(ChatCompletion, await self.client.chat.completions.create(
                model=model,
                messages=messages, # type: ignore
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stop=request.stop_sequences,
                stream=False  # maximizing compatibility for now
            ))

            choice = response.choices[0]
            content = choice.message.content or ""
            stop_reason = choice.finish_reason

            usage = None
            if response.usage:
                # Calculate cost estimation (rough approximation, ideally should be config driven)
                # These rates are illustrative; for real usage, maintain a pricing table.
                cost = 0.0
                # Very rough placeholder pricing
                input_cost_per_1k = 0.00015
                output_cost_per_1k = 0.0006

                cost = (response.usage.prompt_tokens / 1000 * input_cost_per_1k) + \
                       (response.usage.completion_tokens / 1000 * output_cost_per_1k)

                usage = AIModelUsage(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                    cost_usd=cost
                )

            return AICompletionResponse(
                content=content,
                model=response.model,
                usage=usage,
                stop_reason=stop_reason,
                provider_metadata=response.model_dump(exclude={"choices", "usage"})
            )

        except OpenAIError as e:
            # Wrap or re-raise as a provider-agnostic error if needed,
            # but for now letting it bubble up or catching in client is fine.
            raise RuntimeError(f"OpenAI API error: {str(e)}") from e

    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        try:
            model = request.model or "dall-e-3"

            response = await self.client.images.generate(
                model=model,
                prompt=request.prompt,
                n=request.n,
                size=request.size, # type: ignore
                response_format="url"
            )

            urls = [item.url for item in response.data if item.url]

            # DALL-E 3 standard cost
            cost = 0.04 * request.n # $0.04 per image standard

            return ImageGenerationResponse(
                urls=urls,
                usage=AIModelUsage(
                    total_tokens=0,
                    cost_usd=cost
                )
            )

        except OpenAIError as e:
            raise RuntimeError(f"OpenAI Image API error: {str(e)}") from e

    async def check_health(self) -> bool:
        try:
            # Simple models list call to verify auth and reachability
            await self.client.models.list()
            return True
        except Exception:
            return False
