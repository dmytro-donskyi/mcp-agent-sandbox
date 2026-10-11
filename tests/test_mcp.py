"""Tests for mcp-agent-sandbox (Tool registry, Tenancy check, Path containment)."""
from pathlib import Path
import pytest

from mcp_agent_sandbox.sandbox import DirectorySandbox, PathTraversalError
from mcp_agent_sandbox.registry import MCPToolRegistry


def test_sandbox_path_traversal_blocked(tmp_path: Path):
    sb = DirectorySandbox(tmp_path)

    # Allowed local file
    safe_p = sb.resolve_safe_path("docs/plan.md")
    assert safe_p == (tmp_path / "docs" / "plan.md").resolve()

    # Path traversal attack attempting to reach root or parent directory
    with pytest.raises(PathTraversalError):
        sb.resolve_safe_path("../../etc/passwd")

    with pytest.raises(PathTraversalError):
        sb.resolve_safe_path("../secret.env")


def test_sandbox_safe_read_write(tmp_path: Path):
    sb = DirectorySandbox(tmp_path)
    sb.safe_write_text("sub/hello.txt", "world")
    assert sb.safe_read_text("sub/hello.txt") == "world"


@pytest.mark.asyncio
async def test_tool_registry_tenancy_guard():
    reg = MCPToolRegistry()

    def get_estimate(project_id: str, item_id: str):
        return {"project": project_id, "cost": 45000}

    reg.register_tool(
        name="get_estimate",
        description="Retrieve estimating item",
        input_schema={"type": "object", "properties": {"project_id": {"type": "string"}}},
        handler=get_estimate,
        requires_auth=True
    )

    # Authorized call
    res_auth = await reg.execute_tool(
        tool_name="get_estimate",
        arguments={"project_id": "proj_A", "item_id": "item_1"},
        session_project_id="proj_A"
    )
    assert not res_auth.is_error
    assert res_auth.content["cost"] == 45000

    # Cross-project leakage attack: Agent in proj_B attempts to access proj_A
    res_leak = await reg.execute_tool(
        tool_name="get_estimate",
        arguments={"project_id": "proj_A", "item_id": "item_1"},
        session_project_id="proj_B"
    )
    assert res_leak.is_error
    assert "Access Denied" in res_leak.error_message
