from __future__ import annotations

import sys
from pathlib import Path


def _add_module_paths() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    module_paths = [
        repo_root / "modules" / "mcp_protocol" / "src",
        repo_root / "modules" / "mcp_core" / "src",
        repo_root / "modules" / "mcp_cli" / "src",
        repo_root / "modules" / "mcp_target_blender" / "src",
        repo_root / "modules" / "mcp_target_ue5" / "src",
    ]
    for p in module_paths:
        sys.path.insert(0, str(p))


def test_imports() -> None:
    _add_module_paths()

    import mcp  # noqa: F401
    import mcp_core  # noqa: F401
    import mcp_protocol  # noqa: F401
    import mcp_target_blender  # noqa: F401
    import mcp_target_ue5  # noqa: F401
