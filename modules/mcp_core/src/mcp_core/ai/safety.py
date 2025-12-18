import re

from pydantic import BaseModel


class SafetyPolicy(BaseModel):
    """Configuration for safety checks."""
    block_injection_patterns: bool = True
    allowed_tools: list[str] | None = None # None means all allowed (or defer to global policy)
    deny_tools: list[str] = ["os.system", "subprocess.call", "eval", "exec"] # Defaults


class SafetyValidator:
    """
    Validates AI outputs for safety and policy compliance.
    """
    def __init__(self, policy: SafetyPolicy = SafetyPolicy()):
        self.policy = policy
        
        # Simple heuristic patterns for prompt injection or dangerous code
        self._injection_patterns = [
            r"ignore previous instructions",
            r"system prompt",
            r"you are not a helper",
        ]

    def validate_content(self, content: str) -> bool:
        """
        Check text content for safety violations.
        Returns True if safe, False otherwise.
        """
        if self.policy.block_injection_patterns:
            for pattern in self._injection_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # Logging would happen here
                    return False
        return True

    def validate_tool_call(self, tool_name: str) -> bool:
        """
        Check if a proposed tool call is allowed.
        """
        if tool_name in self.policy.deny_tools:
            return False
            
        if self.policy.allowed_tools is not None:
            if tool_name not in self.policy.allowed_tools:
                return False
                
        return True
