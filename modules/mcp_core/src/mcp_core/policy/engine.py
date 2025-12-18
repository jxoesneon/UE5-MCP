from pathlib import Path

from ..config.settings import settings


class PolicyEngine:
    def check_tool_allowed(self, tool_name: str) -> None:
        """
        Check if a tool is allowed to run.
        If tool_allowlist is set, the tool must be in it.
        """
        allowlist = settings.policy.tool_allowlist
        if allowlist and tool_name not in allowlist:
            raise PermissionError(f"Tool '{tool_name}' is not in the allowlist.")

    def check_destructive_allowed(self, tool_name: str, is_destructive: bool) -> None:
        """
        Check if a destructive tool is allowed to run.
        """
        if is_destructive and not settings.policy.allow_destructive:
            raise PermissionError(
                f"Tool '{tool_name}' is destructive and allow_destructive is False."
            )

    def check_path_allowed(self, path: str | Path) -> None:
        """
        Check if a file path is allowed to be accessed.
        If allowed_paths is set, the path must be within one of them.
        """
        allowed_paths = settings.policy.allowed_paths
        if not allowed_paths:
            return

        # Resolve path to be absolute
        target_path = Path(path).expanduser().resolve()
        
        is_allowed = False
        for allowed in allowed_paths:
            allowed_path = Path(allowed).expanduser().resolve()
            # Check if target_path is relative to allowed_path
            try:
                target_path.relative_to(allowed_path)
                is_allowed = True
                break
            except ValueError:
                continue
        
        if not is_allowed:
            raise PermissionError(
                f"Path '{path}' is not in the allowed_paths list."
            )

policy_engine = PolicyEngine()
