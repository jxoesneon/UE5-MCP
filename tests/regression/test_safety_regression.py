from unittest.mock import patch

import pytest
from mcp_core.config.settings import PolicyConfig
from mcp_core.policy.engine import PolicyEngine


def test_policy_allow_destructive_default():
    """Verify destructive tools are blocked by default."""
    # Default PolicyConfig has allow_destructive=False
    with patch("mcp_core.config.settings.settings.policy", PolicyConfig()):
        engine = PolicyEngine()
        with pytest.raises(PermissionError, match="is destructive"):
            engine.check_destructive_allowed("delete_world", is_destructive=True)

def test_policy_allow_destructive_enabled():
    """Verify destructive tools are allowed when configured."""
    config = PolicyConfig(allow_destructive=True)
    with patch("mcp_core.config.settings.settings.policy", config):
        engine = PolicyEngine()
        # Should not raise
        engine.check_destructive_allowed("delete_world", is_destructive=True)

def test_policy_tool_allowlist():
    """Verify tool allowlist enforcement."""
    config = PolicyConfig(tool_allowlist=["allowed_tool"])
    with patch("mcp_core.config.settings.settings.policy", config):
        engine = PolicyEngine()
        
        # Allowed
        engine.check_tool_allowed("allowed_tool")
        
        # Blocked
        with pytest.raises(PermissionError, match="not in the allowlist"):
            engine.check_tool_allowed("forbidden_tool")

def test_policy_path_enforcement(tmp_path):
    """Verify allowed_paths enforcement using a real temp dir."""
    safe_dir = tmp_path / "safe"
    safe_dir.mkdir()
    
    unsafe_dir = tmp_path / "unsafe"
    unsafe_dir.mkdir()
    
    config = PolicyConfig(allowed_paths=[str(safe_dir)])
    
    with patch("mcp_core.config.settings.settings.policy", config):
        engine = PolicyEngine()
        
        # Allowed file
        safe_file = safe_dir / "file.txt"
        engine.check_path_allowed(str(safe_file))
        
        # Unsafe file
        unsafe_file = unsafe_dir / "file.txt"
        with pytest.raises(PermissionError, match="not in the allowed_paths"):
            engine.check_path_allowed(str(unsafe_file))

        # Traversal attempt (if resolved)
        # ../unsafe/file.txt from inside safe? 
        # PolicyEngine resolves path first.
        traversal = safe_dir / ".." / "unsafe" / "file.txt"
        with pytest.raises(PermissionError, match="not in the allowed_paths"):
            engine.check_path_allowed(str(traversal))
