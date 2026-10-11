"""Tool registry with tenancy scoping, authorization, and execution dispatch."""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional
from .protocol import MCPCallResult, MCPToolDefinition


class UnauthorizedProjectAccessError(Exception):
    """Raised when an agent tries to call a tool without matching project context."""


class MCPToolRegistry:
    """Registry maintaining active MCP tools with project-level tenancy enforcement."""

    def __init__(self) -> None:
        self._tools: Dict[str, MCPToolDefinition] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler,
        requires_auth: bool = True
    ) -> None:
        self._tools[name] = MCPToolDefinition(
            name=name,
            description=description,
            input_schema=input_schema,
            handler=handler,
            requires_auth=requires_auth
        )

    def list_tools(self) -> List[Dict[str, Any]]:
        """Returns standard MCP tools list format."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "inputSchema": t.input_schema
            }
            for t in self._tools.values()
        ]

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        session_project_id: Optional[str] = None
    ) -> MCPCallResult:
        """Executes tool with tenancy boundary check and fail-closed error handling."""
        tool = self._tools.get(tool_name)
        if tool is None:
            return MCPCallResult(
                tool_name=tool_name,
                is_error=True,
                content=None,
                error_message=f"Tool '{tool_name}' not found."
            )

        if tool.requires_auth:
            target_project = arguments.get("project_id")
            if not target_project or target_project != session_project_id:
                return MCPCallResult(
                    tool_name=tool_name,
                    is_error=True,
                    content=None,
                    error_message=f"Access Denied: Session project '{session_project_id}' cannot access target project '{target_project}'."
                )

        try:
            if asyncio.iscoroutinefunction(tool.handler):
                result = await tool.handler(**arguments)
            else:
                result = tool.handler(**arguments)
            return MCPCallResult(tool_name=tool_name, is_error=False, content=result)
        except Exception as exc:
            return MCPCallResult(
                tool_name=tool_name,
                is_error=True,
                content=None,
                error_message=f"Execution failure: {str(exc)}"
            )
