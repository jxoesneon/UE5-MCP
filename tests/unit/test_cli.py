from __future__ import annotations

import sys
from pathlib import Path


def _add_module_paths() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo_root / "modules" / "mcp_cli" / "src"))


def test_cli_version_flag(capsys) -> None:
    _add_module_paths()

    from mcp.cli import main

    rc = main(["--version"])
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.out.strip() == "0.6.0"
