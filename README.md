# 🤖 MCP Agent Sandbox

[![CI](https://github.com/dmitriy-donskoy/mcp-agent-sandbox/actions/workflows/ci.yml/badge.svg)](https://github.com/dmitriy-donskoy/mcp-agent-sandbox/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Protocol: Model Context Protocol](https://img.shields.io/badge/protocol-MCP-green.svg)](https://modelcontextprotocol.io/)
[![Tests: 100% Green](https://img.shields.io/badge/tests-100%25%20passed-brightgreen.svg)]()

> **Production-grade Model Context Protocol (MCP) server, tool registry, and multi-tenant project boundary containment for AI Agents (Claude & OpenAI).**  
> Enforces strict tenancy boundaries, blocks path traversal attacks (CWE-22), and formats tool schemas natively for LLM execution.

---

## 🚀 Key Highlights

* **Model Context Protocol (MCP) Compatible:** Formats tool lists and results according to open MCP standards for Claude Desktop, Claude Code, and OpenAI Agents SDK.
* **Cryptographic Project Isolation:** Tools requiring authorization verify `session_project_id` matching before execution, preventing cross-tenant information disclosure.
* **Directory Sandbox Lockdown:** Resolves target paths relative to an authorized project root, blocking directory escape attacks (`../../etc/passwd`).
* **Fail-Closed Execution:** Uncaught tool exceptions are trapped and returned as structured MCP error payloads without crashing the server process.

---

## 📦 Quickstart

```python
import asyncio
from mcp_agent_sandbox import MCPToolRegistry, DirectorySandbox

async def main():
    registry = MCPToolRegistry()

    # Define a tool with tenancy guard
    def fetch_project_file(project_id: str, file_path: str):
        return {"status": "SUCCESS", "project": project_id, "file": file_path}

    registry.register_tool(
        name="fetch_project_file",
        description="Reads authorized project documents",
        input_schema={
            "type": "object",
            "properties": {
                "project_id": {"type": "string"},
                "file_path": {"type": "string"}
            },
            "required": ["project_id", "file_path"]
        },
        handler=fetch_project_file,
        requires_auth=True
    )

    # Agent calls tool with matching session context
    result = await registry.execute_tool(
        tool_name="fetch_project_file",
        arguments={"project_id": "client_alpha", "file_path": "specs/v1.md"},
        session_project_id="client_alpha"
    )

    print(result.to_mcp_response())

asyncio.run(main())
```

---

## 🧪 Testing

```bash
pytest tests -v
```

---

## 📄 License

MIT License. Authored by **Dmitriy Donskoy**.
