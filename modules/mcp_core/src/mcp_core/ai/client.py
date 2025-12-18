from typing import Any

from mcp_core.config.settings import AIConfig, SafetyConfig

from .budget import AIBudgetConfig, AIRequestCost, BudgetTracker
from .models import AICompletionRequest, AICompletionResponse
from .prompts import PromptRegistry
from .provider import AIProvider
from .safety import SafetyPolicy, SafetyValidator


class AIClient:
    """
    High-level client for AI operations, orchestrating:
    - Provider communication
    - Prompt management
    - Budget enforcement
    - Safety checks
    """
    def __init__(
        self,
        provider: AIProvider,
        config: AIConfig,
        safety_config: SafetyConfig,
        prompt_registry: PromptRegistry | None = None
    ):
        self.provider = provider
        self.config = config
        
        # Convert settings to domain models
        budget_config = AIBudgetConfig(
            max_requests_per_run=config.budget.max_requests_per_run,
            max_total_tokens=config.budget.max_total_tokens,
            max_total_cost_usd=config.budget.max_total_cost_usd,
        )
        self.budget_tracker = BudgetTracker(budget_config)
        
        safety_policy = SafetyPolicy(
            block_injection_patterns=safety_config.block_injection_patterns,
            allowed_tools=safety_config.allowed_tools,
            deny_tools=safety_config.deny_tools,
        )
        self.safety_validator = SafetyValidator(safety_policy)
        
        self.prompt_registry = prompt_registry or PromptRegistry()

    async def generate(
        self,
        prompt_name: str,
        variables: dict[str, Any],
        system_prompt: str | None = None,
        model: str | None = None,
        **kwargs: Any
    ) -> AICompletionResponse:
        """
        Generate content using a registered prompt template.
        """
        # 1. Budget Check
        self.budget_tracker.check_budget()

        # 2. Prepare Prompt
        try:
            template = self.prompt_registry.get(prompt_name)
            prompt_text = template.format(**variables)
        except ValueError:
            # Re-raise to let caller handle missing prompts
            raise ValueError(f"Prompt template '{prompt_name}' not found or invalid.")

        # 3. Safety Check (Input)
        if not self.safety_validator.validate_content(prompt_text):
            raise ValueError("Input prompt violates safety policy.")

        # 4. Execute
        request = AICompletionRequest(
            prompt=prompt_text,
            system_prompt=system_prompt,
            model=model,
            **kwargs
        )
        
        response = await self.provider.generate_text(request)

        # 5. Safety Check (Output)
        if not self.safety_validator.validate_content(response.content):
            raise ValueError("AI response violates safety policy.")

        # 6. Track Usage
        if response.usage:
            cost = AIRequestCost(
                total_cost_usd=response.usage.cost_usd or 0.0,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens
            )
            self.budget_tracker.track_usage(cost)

        return response
