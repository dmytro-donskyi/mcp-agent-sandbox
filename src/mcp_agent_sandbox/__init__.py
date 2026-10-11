"""MCP Agent Sandbox — Model Context Protocol tool registry & directory containment."""

from .protocol import MCPToolDefinition, MCPCallResult
from .registry import MCPToolRegistry
from .sandbox import DirectorySandbox, PathTraversalError

__version__ = "0.1.0"
__all__ = [
    "MCPToolDefinition",
    "MCPCallResult",
    "MCPToolRegistry",
    "DirectorySandbox",
    "PathTraversalError",
]
