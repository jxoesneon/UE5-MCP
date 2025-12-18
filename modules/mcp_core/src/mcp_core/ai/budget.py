from pydantic import BaseModel


class AIRequestCost(BaseModel):
    """Cost details for a single request."""
    total_cost_usd: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0


class AIBudgetConfig(BaseModel):
    """Configuration for AI budgets."""
    max_total_cost_usd: float | None = None
    max_total_tokens: int | None = None
    max_requests_per_run: int | None = None

    # Optional: enforcing limits over a time window (e.g. daily) is out of scope for now
    # as this is mostly per-run context.


class BudgetTracker:
    """
    Tracks AI usage and enforces budget limits for a session/run.
    """
    def __init__(self, config: AIBudgetConfig):
        self.config = config
        self.current_cost_usd: float = 0.0
        self.current_tokens: int = 0
        self.request_count: int = 0

    def check_budget(self, estimated_cost: float = 0.0, estimated_tokens: int = 0) -> None:
        """
        Check if the operation would exceed the budget.
        Raises ValueError (or specific BudgetExceededError) if limit reached.
        """
        # Check request count
        if self.config.max_requests_per_run is not None:
            if self.request_count >= self.config.max_requests_per_run:
                raise ValueError(f"Budget exceeded: Max requests ({self.config.max_requests_per_run}) reached.")

        # Check cost
        if self.config.max_total_cost_usd is not None:
            if self.current_cost_usd + estimated_cost > self.config.max_total_cost_usd:
                raise ValueError(f"Budget exceeded: Max cost (${self.config.max_total_cost_usd:.4f}) reached.")

        # Check tokens
        if self.config.max_total_tokens is not None:
            if self.current_tokens + estimated_tokens > self.config.max_total_tokens:
                raise ValueError(f"Budget exceeded: Max tokens ({self.config.max_total_tokens}) reached.")

    def track_usage(self, cost: AIRequestCost) -> None:
        """
        Record usage after a request completes.
        """
        self.current_cost_usd += cost.total_cost_usd
        self.current_tokens += (cost.prompt_tokens + cost.completion_tokens)
        self.request_count += 1
