from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

ERROR_CODES_ALLOWED = {
    "VALIDATION_ERROR",
    "POLICY_DENIED",
    "TARGET_UNAVAILABLE",
    "TIMEOUT",
    "DEPENDENCY_MISSING",
    "IO_ERROR",
    "INTERNAL_ERROR",
}

MCP_PATHS_ALLOWED = {
    "~/.mcp/blender_mcp_config.json",
    "~/.mcp/ue5_mcp_config.json",
    "~/.mcp/artifacts",
    "~/.mcp/artifacts/<run_id>/run_manifest.json",
}


def _iter_markdown_files() -> list[Path]:
    md_files: list[Path] = []
    for path in REPO_ROOT.rglob("*.md"):
        if any(part in {".git", "venv", ".venv", "node_modules"} for part in path.parts):
            continue
        md_files.append(path)
    return sorted(md_files)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_declared_tools_from_commands_md(commands_md: str) -> set[str]:
    tools: set[str] = set()
    for line in commands_md.splitlines():
        m = re.match(r"^### `(?P<tool>mcp\.[a-z0-9_]+)", line.strip())
        if m:
            tools.add(m.group("tool"))
    return tools


def _extract_declared_tools_from_api_reference_md(api_reference_md: str) -> set[str]:
    tools: set[str] = set()
    for line in api_reference_md.splitlines():
        m = re.match(r"^### `(?P<tool>mcp\.[a-z0-9_]+)`\s*$", line.strip())
        if m:
            tools.add(m.group("tool"))
    return tools


def _extract_referenced_tools(text: str) -> set[str]:
    sanitized = text
    sanitized = re.sub(r"https?://\S+", "", sanitized)
    sanitized = re.sub(r"\]\([^)]+\)", "]()", sanitized)
    return set(re.findall(r"\bmcp\.[a-z0-9_]+\b", sanitized))


def _extract_backticked_error_codes(text: str) -> set[str]:
    candidates = set(re.findall(r"`([A-Z][A-Z0-9_]{2,})`", text))
    return {
        c
        for c in candidates
        if "_" in c
        and not c.startswith("MCP_")
    }


def _extract_mcp_paths(text: str) -> set[str]:
    return set(re.findall(r"~\/\.mcp\/[^\s)\]`\"']+", text))


def _extract_local_md_links(text: str) -> set[str]:
    links: set[str] = set()
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if "://" in target or target.startswith("mailto:"):
            continue
        if target.startswith("#"):
            continue

        target_no_anchor = target.split("#", 1)[0]
        if target_no_anchor.endswith(".md"):
            links.add(target_no_anchor)
    return links


def _check_links(md_files: list[Path]) -> list[str]:
    errors: list[str] = []
    for md in md_files:
        text = _read_text(md)
        for link in _extract_local_md_links(text):
            normalized = link
            if normalized.startswith("./"):
                normalized = normalized[2:]

            if ".." in Path(normalized).parts:
                errors.append(f"{md}: path traversal in markdown link not allowed: {link}")
                continue

            if normalized.startswith("/"):
                errors.append(f"{md}: absolute markdown link not allowed: {link}")
                continue

            target_path = (REPO_ROOT / normalized).resolve()
            if REPO_ROOT not in target_path.parents and target_path != REPO_ROOT:
                errors.append(f"{md}: markdown link resolves outside repo: {link}")
                continue
            if not target_path.exists():
                errors.append(f"{md}: broken link target: {link}")
                continue

            if target_path.suffix.lower() != ".md":
                errors.append(f"{md}: non-md link target where .md expected: {link}")

    return errors


def main() -> int:
    md_files = _iter_markdown_files()

    commands_path = REPO_ROOT / "commands.md"
    api_reference_path = REPO_ROOT / "api_reference.md"

    if not commands_path.exists():
        print("Missing commands.md", file=sys.stderr)
        return 2

    if not api_reference_path.exists():
        print("Missing api_reference.md", file=sys.stderr)
        return 2

    commands_text = _read_text(commands_path)
    api_reference_text = _read_text(api_reference_path)

    declared_tools = (
        _extract_declared_tools_from_commands_md(commands_text)
        | _extract_declared_tools_from_api_reference_md(api_reference_text)
    )

    issues: list[str] = []

    referenced_tools: set[str] = set()
    referenced_error_codes: set[str] = set()
    referenced_mcp_paths: set[str] = set()

    for md in md_files:
        text = _read_text(md)
        referenced_tools |= _extract_referenced_tools(text)
        referenced_error_codes |= _extract_backticked_error_codes(text)
        referenced_mcp_paths |= _extract_mcp_paths(text)

    unknown_tools = sorted(t for t in referenced_tools if t not in declared_tools)
    if unknown_tools:
        issues.append(
            "Unknown tool references (not declared in commands.md/api_reference.md):\n"
            + "\n".join(f"- {t}" for t in unknown_tools)
        )

    unknown_error_codes = sorted(code for code in referenced_error_codes if code not in ERROR_CODES_ALLOWED)
    for code in unknown_error_codes:
        issues.append(f"Unknown error code reference: {code}")

    unknown_paths = sorted(p for p in referenced_mcp_paths if p not in MCP_PATHS_ALLOWED)
    if unknown_paths:
        issues.append(
            "Unknown ~/.mcp/* path references:\n" + "\n".join(f"- {p}" for p in unknown_paths)
        )

    issues.extend(_check_links(md_files))

    if issues:
        print("Docs contract check failed:\n", file=sys.stderr)
        print("\n".join(issues), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
