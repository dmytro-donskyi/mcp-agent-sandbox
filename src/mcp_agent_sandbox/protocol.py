"""Model Context Protocol (MCP) data structures and JSON Schema specifications."""
from __future__ import annotations

import dataclasses
from typing import Any, Callable, Dict, Optional


@dataclasses.dataclass
class MCPToolDefinition:
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable[..., Any]
    requires_auth: bool = True


@dataclasses.dataclass
class MCPCallResult:
    tool_name: str
    is_error: bool
    content: Any
    error_message: Optional[str] = None

    def to_mcp_response(self) -> Dict[str, Any]:
        if self.is_error:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Error: {self.error_message}"}]
            }
        return {
            "isError": False,
            "content": [{"type": "text", "text": str(self.content)}]
        }
