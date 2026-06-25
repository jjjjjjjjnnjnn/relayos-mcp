"""MCP server — exposes RelayOS agents as MCP tools for Claude Code."""

from __future__ import annotations

import json
import logging
import sys
from typing import Any

logger = logging.getLogger(__name__)

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import CallToolRequest, ListToolsRequest, Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from relayos_mcp.executor import TaskExecutor
from relayos_mcp.schema import TASK_SCHEMA


class MCPServer:
    """MCP server that exposes RelayOS agents as tools."""

    def __init__(self):
        self.executor = TaskExecutor()

    def run(self):
        """Start the MCP server (stdio transport for Claude Code)."""
        if not MCP_AVAILABLE:
            print("MCP SDK not installed. Install: pip install mcp")
            sys.exit(1)

        app = Server("relayos-mcp")

        @app.list_tools()
        async def list_tools() -> list[Tool]:
            agents = self.executor.detect_agents()
            return [
                Tool(
                    name="relay_execute",
                    description="Execute a command via a RelayOS agent",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent": {
                                "type": "string",
                                "enum": [a["name"] for a in agents],
                                "description": "Agent to run the command",
                            },
                            "command": {"type": "string", "description": "Command to execute"},
                            "timeout": {"type": "integer", "default": 120},
                        },
                        "required": ["agent", "command"],
                    },
                ),
                Tool(
                    name="relay_run_task",
                    description="Execute a multi-step task with multiple agents",
                    inputSchema=TASK_SCHEMA,
                ),
                Tool(
                    name="relay_list_agents",
                    description="List available RelayOS agents",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
            ]

        @app.call_tool()
        async def call_tool(req: CallToolRequest) -> list[TextContent]:
            name = req.params.name
            args = req.params.arguments or {}

            if name == "relay_list_agents":
                agents = self.executor.detect_agents()
                return [TextContent(type="text", text=json.dumps(agents, indent=2))]

            if name == "relay_execute":
                result = self.executor.execute({
                    "actions": [{
                        "agent": args.get("agent", "local"),
                        "command": args.get("command", ""),
                        "timeout": args.get("timeout", 120),
                    }],
                })
                r = result[0]
                return [TextContent(type="text", text=r.output or r.error)]

            if name == "relay_run_task":
                # args IS the task definition
                if isinstance(args, dict) and "actions" in args:
                    results = self.executor.execute(args)
                    lines = [f"Task completed: {len(results)} actions"]
                    for r in results:
                        status = "✅" if r.success else "❌"
                        lines.append(f"  {status} [{r.agent}] {r.duration_ms}ms: {r.output[:100] or r.error[:100]}")
                    return [TextContent(type="text", text="\n".join(lines))]
                return [TextContent(type="text", text="Invalid task: missing 'actions'")]

            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        import asyncio
        asyncio.run(stdio_server(app))


def main():
    """Entry point: run as `relayos-mcp`."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    server = MCPServer()
    server.run()


if __name__ == "__main__":
    main()
