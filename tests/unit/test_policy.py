
import pytest
from mcp_core.config.settings import McpSettings
from mcp_core.policy.engine import PolicyEngine


@pytest.fixture
def policy_engine():
    return PolicyEngine()

def test_check_tool_allowed_no_allowlist(policy_engine, monkeypatch):
    # Empty allowlist means all tools are allowed (unless we interpret empty as "allow none"? 
    # Based on implementation: if allowlist and tool_name not in allowlist -> raise.
    # So if allowlist is empty, loop doesn't run or condition is false?
    # Actually current impl: if allowlist and ...
    # So empty allowlist = everything allowed.
    
    # Let's mock settings
    settings = McpSettings()
    settings.policy.tool_allowlist = []
    monkeypatch.setattr("mcp_core.policy.engine.settings", settings)
    
    policy_engine.check_tool_allowed("any.tool")

def test_check_tool_allowed_with_allowlist(policy_engine, monkeypatch):
    settings = McpSettings()
    settings.policy.tool_allowlist = ["allowed.tool"]
    monkeypatch.setattr("mcp_core.policy.engine.settings", settings)
    
    policy_engine.check_tool_allowed("allowed.tool")
    
    with pytest.raises(PermissionError):
        policy_engine.check_tool_allowed("forbidden.tool")

def test_check_destructive_allowed(policy_engine, monkeypatch):
    settings = McpSettings()
    settings.policy.allow_destructive = False
    monkeypatch.setattr("mcp_core.policy.engine.settings", settings)
    
    # Non-destructive always allowed
    policy_engine.check_destructive_allowed("safe.tool", is_destructive=False)
    
    # Destructive disallowed
    with pytest.raises(PermissionError):
        policy_engine.check_destructive_allowed("unsafe.tool", is_destructive=True)
        
    # Enable destructive
    settings.policy.allow_destructive = True
    policy_engine.check_destructive_allowed("unsafe.tool", is_destructive=True)

def test_check_path_allowed(policy_engine, monkeypatch, tmp_path):
    safe_dir = tmp_path / "safe"
    safe_dir.mkdir()
    
    settings = McpSettings()
    settings.policy.allowed_paths = [str(safe_dir)]
    monkeypatch.setattr("mcp_core.policy.engine.settings", settings)
    
    # Allowed path
    policy_engine.check_path_allowed(safe_dir / "file.txt")
    
    # Disallowed path
    with pytest.raises(PermissionError):
        policy_engine.check_path_allowed(tmp_path / "unsafe.txt")

def test_check_path_allowed_no_restrictions(policy_engine, monkeypatch, tmp_path):
    settings = McpSettings()
    settings.policy.allowed_paths = [] # Empty list = no path restrictions? 
    # Current impl: if not allowed_paths: return. So yes, unrestricted.
    monkeypatch.setattr("mcp_core.policy.engine.settings", settings)
    
    policy_engine.check_path_allowed(tmp_path / "anywhere.txt")
